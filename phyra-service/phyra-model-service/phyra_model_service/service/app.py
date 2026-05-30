"""
phyra-model-service control plane (FastAPI).

A thin, long-lived HTTP service whose whole job is to OWN one shared,
correctly-configured managed Ollama for the Phyra suite and answer status
queries about it. It does NOT proxy chat/translation calls — sibling
services talk to Ollama directly on the hot path (no extra hop); this
service just keeps Ollama up with one set of defaults (one idle-unload
window so VRAM frees consistently) and surfaces GPU/VRAM health.

Endpoints:
  GET /healthz        -> {"ok": true, "version": "..."}
  GET /api/ollama     -> managed-Ollama status (host, model, model_status)
  GET /api/models     -> installed Ollama models (?host overrides)
  GET /api/runtime    -> GPU + VRAM-placement snapshot (?host overrides)

Best-effort: a failed Ollama spawn never crashes the service — it reports
the failure via /api/ollama instead. Disable management with
PHYRA_MODEL_MANAGE_OLLAMA=0 to point at your own Ollama.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from .. import __version__
from ..backends.ollama import list_models
from ..managed import ManagedOllama
from ..runtime import collect as collect_runtime
from ..settings import ModelSettings


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    import logging

    settings = ModelSettings()
    app.state.settings = settings

    ollama = None
    if settings.manage:
        ollama = ManagedOllama.from_settings(settings)
        await asyncio.to_thread(ollama.start)
    else:
        logging.getLogger("phyra-model-service").info(
            "management off (PHYRA_MODEL_MANAGE_OLLAMA=0); using %s",
            settings.ollama_host,
        )
    app.state.ollama = ollama
    try:
        yield
    finally:
        if ollama is not None:
            await asyncio.to_thread(ollama.stop)


def _probe_host(app: FastAPI) -> str:
    """The host the status probes should target by default: the managed
    Ollama when managed, else the configured fallback host."""
    settings: ModelSettings = app.state.settings
    return settings.managed_host() or settings.ollama_host


def create_app() -> FastAPI:
    app = FastAPI(
        title="phyra-model-service", version=__version__, lifespan=lifespan
    )

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True, "version": __version__}

    @app.get("/api/ollama")
    def ollama_status(request: Request) -> dict:
        svc = getattr(request.app.state, "ollama", None)
        if svc is None:
            return {"managed": False, "host": _probe_host(request.app)}
        return {"managed": True, **svc.status()}

    @app.get("/api/models")
    def models(request: Request, host: str | None = None) -> dict:
        return list_models(host or _probe_host(request.app))

    @app.get("/api/runtime")
    def runtime(request: Request, host: str | None = None) -> dict:
        return collect_runtime(host or _probe_host(request.app))

    return app


app = create_app()


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "") or ModelSettings().service_port)
    uvicorn.run(
        "phyra_model_service.service.app:app",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
