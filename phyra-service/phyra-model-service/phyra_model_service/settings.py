"""
Unified Ollama / model settings — the single source of truth for the
managed-Ollama defaults shared across the whole Phyra service suite.

Every default the model layer needs (port, model, idle-unload window, …)
is defined ONCE here as a module constant, so phyra-dualtrans (and any
future plugin) gets identical behaviour without re-declaring it.

`ModelSettings` reads the environment with BOTH the new canonical
``PHYRA_MODEL_*`` names AND the legacy ``PHYRA_DUALTRANS_OLLAMA_*`` /
``OLLAMA_HOST`` names (via AliasChoices), so existing .env files keep
working unchanged while new services can use the unified prefix.
"""

from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── canonical defaults (the ONE place these live) ────────────────────
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
# Dedicated managed-Ollama loopback port — never collides with a system
# Ollama (:11434) or the user's own manual instance.
DEFAULT_MANAGED_PORT = 11500
# Tuned translation model created from the base on first run.
DEFAULT_MODEL = "phyra-trans"
DEFAULT_BASE_MODEL = "qwen3:14b"
DEFAULT_NUM_PARALLEL = 2
# How long Ollama keeps the model resident in VRAM after the LAST request.
# Sent as keep_alive on every chat call (the timer resets while a job
# streams), so VRAM frees ~this long after translation goes idle. "10s" /
# "5m" / 0 (unload now) / -1 (keep forever).
DEFAULT_KEEP_ALIVE = "10s"


class ModelSettings(BaseSettings):
    """Operator config for the shared model layer, from env / .env only."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Manage a dedicated Ollama (start it with the service, stop it on
    # shutdown). Off → use your own server at `ollama_host`.
    manage: bool = Field(
        True,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_MANAGE_OLLAMA", "PHYRA_DUALTRANS_MANAGE_OLLAMA"
        ),
    )
    ollama_port: int = Field(
        DEFAULT_MANAGED_PORT,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_PORT", "PHYRA_DUALTRANS_OLLAMA_PORT"
        ),
    )
    # The non-managed fallback host (env OLLAMA_HOST, or a per-request URL).
    ollama_host: str = Field(
        DEFAULT_OLLAMA_HOST,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_HOST", "OLLAMA_HOST"
        ),
    )
    model: str = Field(
        DEFAULT_MODEL,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_MODEL", "PHYRA_DUALTRANS_OLLAMA_MODEL"
        ),
    )
    base_model: str = Field(
        DEFAULT_BASE_MODEL,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_BASE_MODEL",
            "PHYRA_DUALTRANS_OLLAMA_BASE_MODEL",
        ),
    )
    num_parallel: int = Field(
        DEFAULT_NUM_PARALLEL,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_NUM_PARALLEL",
            "PHYRA_DUALTRANS_OLLAMA_NUM_PARALLEL",
        ),
    )
    keep_alive: str = Field(
        DEFAULT_KEEP_ALIVE,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_KEEP_ALIVE",
            "PHYRA_DUALTRANS_OLLAMA_KEEP_ALIVE",
        ),
    )
    models_dir: str | None = Field(
        None,
        validation_alias=AliasChoices(
            "PHYRA_MODEL_OLLAMA_MODELS_DIR",
            "PHYRA_DUALTRANS_OLLAMA_MODELS_DIR",
        ),
    )
    # The control-plane HTTP port for the standalone model-service app.
    service_port: int = Field(
        8041, validation_alias=AliasChoices("PHYRA_MODEL_SERVICE_PORT")
    )

    def managed_host(self) -> str | None:
        """The dedicated managed-Ollama host, or None when management is
        off (then `ollama_host` / a per-request Base URL is used)."""
        if not self.manage:
            return None
        return f"http://127.0.0.1:{self.ollama_port}"
