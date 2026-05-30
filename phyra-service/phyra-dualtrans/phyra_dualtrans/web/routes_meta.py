"""Backends, settings, preflight, health."""

from __future__ import annotations

from fastapi import APIRouter, Request

from .. import __version__
from ..backends import BACKEND_INFO, list_ollama_models
from ..config import (
    archbase_enabled,
    backend_gated,
    builtin_defaults,
    get_settings,
    managed_ollama_host,
    resolve_backend,
)
from ..pipeline.preflight import run_preflight
from ..runtime_status import collect as collect_runtime

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "version": __version__}


@router.get("/api/backends")
def backends() -> list[dict]:
    # Surface whether each backend is password-gated so the UI shows the
    # field. Copy each entry; never mutate the module-level BACKEND_INFO.
    out: list[dict] = []
    for b in BACKEND_INFO:
        b = dict(b)
        b["needs_password"] = backend_gated(b["kind"])
        out.append(b)
    return out


@router.get("/api/backends/ollama/models")
def ollama_models(host: str | None = None) -> dict:
    return list_ollama_models(host)


@router.get("/api/ollama")
def ollama_status(request: Request) -> dict:
    """Managed-Ollama status for the UI: whether it is managed, its host,
    and the tuned model's provisioning state (pending/preparing/ready/
    error) so a first-run model pull can be surfaced instead of looking
    like a hang."""
    svc = getattr(request.app.state, "ollama", None)
    if svc is None:
        return {"managed": False, "host": managed_ollama_host()}
    return {"managed": True, **svc.status()}


@router.get("/api/runtime")
def runtime_status(host: str | None = None) -> dict:
    """Hardware/runtime status for the Settings panel: is an NVIDIA GPU +
    working driver visible (nvidia-smi), and is the Ollama model resident
    in VRAM or has it fallen back to CPU. Surfaces the common slow-down
    where a crashed GPU driver silently pushes Ollama onto the CPU. `host`
    lets the UI point the Ollama probe at the active backend's Base URL;
    when omitted it falls back to the managed Ollama (loopback)."""
    return collect_runtime(host or managed_ollama_host())


@router.get("/api/archbase")
def archbase_info() -> dict:
    """Whether the sibling phyra-archbase is reachable (enables the
    "save to archive" button) and its port (the UI builds the cross-link
    from the browser's own hostname + this port, so it works over LAN)."""
    return {
        "enabled": archbase_enabled(),
        "port": get_settings().archbase_port,
    }


@router.get("/api/center")
def center_info() -> dict:
    """Port of the Phyra Center landing page (the parent hub). The UI
    builds a "🜂 返回 Phyra Center" banner from the browser's hostname +
    this port so it works over the LAN. The banner stays hidden when
    Center is not reachable — the WebUI works standalone."""
    return {"port": get_settings().center_port}


@router.get("/api/settings")
def get_settings_route() -> dict:
    """Read-only, non-secret built-in defaults for first paint. Per-user
    preferences are stored in the browser (localStorage); there is NO
    server-side, API-writable settings file (the service has no auth and
    may be LAN-exposed — a shared file would leak prefs and let a saved
    key be redirected). Hence no PUT."""
    return builtin_defaults()


@router.get("/api/preflight")
def preflight(
    backend: str = "claude_cli",
    lang_out: str = "zh-TW",
    compress: str = "lossy",
    base_url: str | None = None,
) -> dict:
    # Must honor the user's Base URL — otherwise the ollama reachability
    # probe always hits the default :11434 and "fails" even when the
    # user correctly pointed at a custom port. (No api_key here: never
    # put a secret in a GET query / access log.)
    cfg = resolve_backend(kind=backend, base_url=base_url)
    return run_preflight(
        backend=backend,
        lang_out=lang_out,
        compress=compress,
        base_url=cfg.base_url,
        has_api_key=cfg.api_key is not None,
    )
