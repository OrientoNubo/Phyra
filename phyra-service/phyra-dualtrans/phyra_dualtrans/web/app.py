"""FastAPI application factory + entrypoint.

The server NEVER imports BabelDOC — translation runs in a child process
spawned by JobManager (see jobs.py). Binds 0.0.0.0 and has no auth: run on
a trusted LAN / localhost only.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope

from .. import __version__
from ..config import get_settings
from . import routes_jobs, routes_meta, routes_translate
from .jobs import JobManager

STATIC_DIR = Path(__file__).parent / "static"


class NoCacheStaticFiles(StaticFiles):
    """Serve static files with ``Cache-Control: no-cache``.

    Plain StaticFiles only sends ETag / Last-Modified, so browsers apply
    heuristic caching and may serve a stale index.html / app.js WITHOUT
    revalidating after the app is updated (this caused an updated UI not
    to appear). ``no-cache`` keeps the ETag (so 304s still work, no
    bandwidth wasted) but forces revalidation every load — the UI is
    always fresh, which is what a single-user local tool wants.
    """

    async def get_response(self, path: str, scope: Scope):
        resp = await super().get_response(path, scope)
        resp.headers["Cache-Control"] = "no-cache"
        return resp


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    import logging

    settings = get_settings()
    settings.jobs_dir.mkdir(parents=True, exist_ok=True)

    # Managed Ollama (shared model layer): start a dedicated,
    # correctly-configured Ollama with the WebUI and stop it on shutdown.
    # Best-effort (spawn is quick; readiness ≤40s; a first-time model pull
    # runs in a background thread so it never blocks the server). When the
    # phyra-model-service is already serving Ollama on the shared port, the
    # ManagedOllama reuse path detects it and never double-spawns. Disable
    # with PHYRA_MODEL_MANAGE_OLLAMA=0 (legacy PHYRA_DUALTRANS_MANAGE_OLLAMA
    # still honored).
    from phyra_model_service.managed import ManagedOllama
    from phyra_model_service.settings import ModelSettings

    ms = ModelSettings()
    ollama = None
    if ms.manage:
        ollama = ManagedOllama.from_settings(ms)
        await asyncio.to_thread(ollama.start)
    app.state.ollama = ollama

    mgr = JobManager()
    restored = mgr.rehydrate()
    if restored:
        logging.getLogger("phyra-dualtrans").info(
            "rehydrated %d job(s) from %s", restored, settings.jobs_dir
        )
    app.state.manager = mgr
    try:
        yield
    finally:
        if ollama is not None:
            await asyncio.to_thread(ollama.stop)


def create_app() -> FastAPI:
    app = FastAPI(
        title="phyra-dualtrans", version=__version__, lifespan=lifespan
    )
    # API routes first; the catch-all static mount must be registered last.
    app.include_router(routes_meta.router)
    app.include_router(routes_translate.router)
    app.include_router(routes_jobs.router)
    app.mount(
        "/", NoCacheStaticFiles(directory=STATIC_DIR, html=True),
        name="static",
    )
    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "phyra_dualtrans.web.app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
