"""
Configuration & secrets.

The service has NO auth and may be LAN-exposed, so there is deliberately
no shared, server-side, API-writable settings file. Two scopes only:

- AppSettings  : operator config + secrets, from env / .env ONLY
                 (api_key, base_url defaults, concurrency, gates...).
- BUILTIN_DEFAULTS : static, non-secret form defaults served read-only
                 by GET /api/settings for first paint. Per-user UI
                 preferences live in the BROWSER (localStorage), never
                 on the server — a shared file would leak one visitor's
                 prefs to the next and let a saved key be redirected.

Per-request backend precedence (in `resolve_backend`):
    explicit request value  >  env / .env  >  built-in default
The env api_key is paired ONLY with the env base_url: a request that
supplies its own base_url MUST supply its own key, so the operator's
key can never be redirected to an attacker endpoint.
"""

from __future__ import annotations

import hmac
import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from phyra_model_service.backends.base import BackendConfig
from phyra_model_service.settings import ModelSettings

# The shared model layer owns all Ollama config + defaults; dualtrans no
# longer declares its own ollama_* settings. `model_settings()` reads a
# fresh ModelSettings (cheap; env-only) so monkeypatched env / .env is
# always reflected. The legacy PHYRA_DUALTRANS_OLLAMA_* env names still
# work (ModelSettings accepts them as aliases).
def model_settings() -> ModelSettings:
    return ModelSettings()


def _xdg(base_env: str, fallback: str) -> Path:
    return Path(os.environ.get(base_env, str(Path.home() / fallback)))


def _default_jobs_dir() -> Path:
    return _xdg("XDG_DATA_HOME", ".local/share") / "phyra-dualtrans/jobs"


def _default_archbase_dir() -> Path | None:
    """Auto-locate a sibling phyra-archbase checkout so the "save to
    archive" feature works out of the box when the two repos sit next to
    each other (``phyra-proj/{phyra-dualtrans,phyra-archbase}``). Returns
    None when no sibling is found — the feature then stays disabled until
    PHYRA_DUALTRANS_ARCHBASE_DIR is set."""
    # config.py → phyra_dualtrans/ → phyra-dualtrans/ → phyra-proj/
    cand = Path(__file__).resolve().parents[2] / "phyra-archbase"
    return cand if cand.is_dir() else None


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    jobs_dir: Path = Field(
        default_factory=_default_jobs_dir,
        validation_alias="PHYRA_DUALTRANS_JOBS_DIR",
    )
    max_concurrent_jobs: int = Field(
        1, validation_alias="PHYRA_DUALTRANS_MAX_CONCURRENT_JOBS"
    )
    job_ttl_hours: int = Field(
        0, validation_alias="PHYRA_DUALTRANS_JOB_TTL_HOURS"
    )
    # After a job SUCCEEDS, delete the throwaway intermediates
    # (`*.no_refs*.pdf` sliced/BabelDOC files + child.log) — they are
    # useless once the final dual/mono exist and dominate disk (~90 MB
    # vs ~2 MB for a typical paper). Set to keep them (old behavior /
    # debugging). Failed jobs are NEVER cleaned (intermediates + log
    # are what you debug with).
    keep_intermediates: bool = Field(
        False, validation_alias="PHYRA_DUALTRANS_KEEP_INTERMEDIATES"
    )
    # Also delete the uploaded/downloaded ORIGINAL pdf on success. Off by
    # default (it is user input, and the dual already embeds it on the
    # left); on → per-job footprint drops to just the final PDFs.
    drop_original: bool = Field(
        False, validation_alias="PHYRA_DUALTRANS_DROP_ORIGINAL"
    )

    # phyra-archbase integration: a sibling paper-archive WebUI. When set
    # (auto-detected as ../phyra-archbase, or via env), the Jobs UI offers
    # a "save to archive" button that copies the original + dual PDF into
    # archbase's collection/ and refreshes its index. archbase_port gates
    # the in-card "存入 archbase" button only (the top banner now points
    # at Phyra Center via center_port, not at archbase).
    archbase_dir: Path | None = Field(
        default_factory=_default_archbase_dir,
        validation_alias="PHYRA_DUALTRANS_ARCHBASE_DIR",
    )
    archbase_port: int = Field(
        8037, validation_alias="PHYRA_DUALTRANS_ARCHBASE_PORT"
    )
    # phyra-center integration: the parent hub that lists every sibling
    # service. The top banner ("🜂 返回 Phyra Center") is built from this
    # port + the browser's hostname (so LAN access works). When Center is
    # not reachable the banner stays hidden — the WebUI works standalone.
    center_port: int = Field(
        8035, validation_alias="PHYRA_DUALTRANS_CENTER_PORT"
    )
    # Backoff when a backend looks rate-limited. Tuned for LOCAL backends
    # (managed Ollama): a local model effectively never 429s, so a
    # *misclassified* hiccup must not freeze a paragraph for minutes.
    # 10s × 5 ⇒ ≤ ~50s worst case (was 60×8 ≈ 8 min — the reported
    # "等很久"). A HardCallError already falls back immediately (no
    # wait); only a real rate-limit signal sleeps. If you translate via
    # the Claude API and hit genuine usage-limit windows, raise these
    # (e.g. 1800 / 50) via env so it waits the reset out.
    retry_wait_sec: int = Field(
        10, validation_alias="PHYRA_DUALTRANS_RETRY_WAIT_SEC"
    )
    max_attempts: int = Field(
        5, validation_alias="PHYRA_DUALTRANS_MAX_ATTEMPTS"
    )

    openai_base_url: str = Field(
        "https://api.openai.com/v1",
        validation_alias="PHYRA_DUALTRANS_OPENAI_BASE_URL",
    )
    openai_api_key: SecretStr | None = Field(
        None, validation_alias="OPENAI_API_KEY"
    )
    # NOTE: all Ollama config (managed port, model, base_model,
    # num_parallel, keep_alive, models_dir, fallback host) now lives in the
    # shared phyra_model_service.settings.ModelSettings — accessed via
    # model_settings() above, not declared here. The legacy
    # PHYRA_DUALTRANS_OLLAMA_* / OLLAMA_HOST env names still work.

    # Optional password gating the `claude_cli` backend, which spends
    # THIS host's Claude Code auth (no key, billed to the operator).
    # `ollama` (local GPU) and `openai` (caller's key) are NOT gated.
    # env-ONLY by design (never config.json / the open API, or the gate
    # could be read/overwritten there). Unset → claude_cli is open.
    claude_cli_password: SecretStr | None = Field(
        None, validation_alias="PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD"
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


def _secret(v: SecretStr | None) -> str | None:
    s = v.get_secret_value() if v is not None else ""
    return s or None


def gate_password_for(kind: str) -> str | None:
    """The password required to use `kind`, or None if that backend is
    not gated. Only `claude_cli` is gateable (it spends the host's
    Claude auth); `ollama` (local GPU) and `openai` (caller's key) are
    never gated."""
    if kind == "claude_cli":
        return _secret(get_settings().claude_cli_password)
    return None


def backend_gated(kind: str) -> bool:
    return gate_password_for(kind) is not None


def check_backend_password(kind: str, supplied: str | None) -> bool:
    """Constant-time check. True when `kind` is not gated, or `supplied`
    matches that backend's configured password."""
    secret = gate_password_for(kind)
    if secret is None:
        return True
    return hmac.compare_digest(str(supplied or ""), secret)


# Back-compat thin wrappers (claude_cli-specific call sites / tests).
def claude_cli_gate_enabled() -> bool:
    return backend_gated("claude_cli")


def check_claude_cli_password(supplied: str | None) -> bool:
    return check_backend_password("claude_cli", supplied)


# Static, non-secret form defaults. Served read-only by GET
# /api/settings for first paint ONLY. Never contains a secret; per-user
# preferences are persisted client-side (localStorage), not here.
BUILTIN_DEFAULTS: dict = {
    "backend": "ollama",
    "model": "qwen3-32b-trans",
    "lang_in": "en",
    "lang_out": "zh-TW",
    "qps": 2,
    "compat": False,
    "compress": "lossy",
    "dpi": 150,
    "preset": "ebook",
    "mono": False,
    "distill": False,
    "think": False,
}


def managed_ollama_host(settings: ModelSettings | None = None) -> str | None:
    """The dedicated managed-Ollama host, or None when management is off
    (then the env OLLAMA_HOST / per-request Base URL is used instead).
    Not a secret — but still resolved server-side, never echoed in
    /api/settings, so the per-user-prefs / no-shared-base_url invariant
    holds. Delegates to the shared ModelSettings."""
    s = settings or model_settings()
    return s.managed_host()


def archbase_paths(
    settings: AppSettings | None = None,
) -> tuple[Path, Path] | None:
    """Resolve (collection_dir, generate_index_script) for the sibling
    phyra-archbase, or None when archive integration is unavailable
    (unset, or the dir/script are missing). Both must exist — a half
    checkout disables the feature rather than erroring at save time."""
    s = settings or get_settings()
    if not s.archbase_dir:
        return None
    base = Path(s.archbase_dir)
    coll = base / "collection"
    script = base / "script" / "generate_index.py"
    if not coll.is_dir() or not script.is_file():
        return None
    return coll, script


def archbase_enabled(settings: AppSettings | None = None) -> bool:
    return archbase_paths(settings) is not None


def builtin_defaults() -> dict:
    """Read-only, non-secret defaults for first paint. base_url / api_key
    are intentionally absent (operator/env-only, never echoed). When
    Ollama is managed, the model defaults to the tuned managed model so
    the user need not type a Base URL or model at all."""
    d = dict(BUILTIN_DEFAULTS)
    ms = model_settings()
    if ms.manage:
        d["model"] = ms.model
    return d


def resolve_backend(
    *,
    kind: str,
    model: str = "",
    base_url: str | None = None,
    api_key: str | None = None,
    extra_headers: dict[str, str] | None = None,
    think: bool = False,
) -> BackendConfig:
    """Resolve a per-request backend from the request + env ONLY (no
    shared server file).

    Security invariant: the env api_key is paired ONLY with the env
    base_url. If the request supplies its own base_url it must also
    supply its own key — otherwise the call gets no key. This makes it
    impossible to redirect the operator's key to an attacker endpoint
    by sending a custom base_url with a blank key.
    """
    settings = get_settings()
    ms = model_settings()

    eff_model = model or ("sonnet" if kind == "claude_cli" else "")

    caller_base = (base_url or "").strip() or None
    eff_base = caller_base
    if eff_base is None:
        if kind == "openai":
            eff_base = settings.openai_base_url
        elif kind == "ollama":
            # default to the managed Ollama when enabled, so the user
            # need not set a Base URL at all; else the env OLLAMA_HOST.
            eff_base = managed_ollama_host(ms) or ms.ollama_host

    eff_key: str | None = None
    if api_key and api_key != "***":
        eff_key = api_key                       # explicit per-request key
    elif (
        kind == "openai"
        and caller_base is None                 # ONLY with the env base
        and settings.openai_api_key is not None
    ):
        eff_key = settings.openai_api_key.get_secret_value()

    return BackendConfig(
        kind=kind,  # type: ignore[arg-type]
        model=eff_model,
        base_url=eff_base,
        api_key=SecretStr(eff_key) if eff_key else None,
        extra_headers=extra_headers or {},
        think=think,
        keep_alive=ms.keep_alive,  # Ollama idle-unload window (shared setting)
    )
