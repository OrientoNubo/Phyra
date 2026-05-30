#!/usr/bin/env python3
"""phyra-center — Phyra Center landing page (stdlib HTTP server).

Zero-dep on purpose — matches phyra-archbase's `server.py` style. Serves
the static landing page (`static/index.html`) plus three tiny endpoints:

  GET /healthz        -> {"ok": true, "version": "..."}
  GET /api/services   -> [{kind, name, port, url, reachable, latency_ms}, …]
  GET /api/center     -> {"port": <PORT>}   (used by sibling banners)

Service probes use stdlib `urllib`, with a short timeout, and degrade to
``reachable: false`` instead of raising — a dead sibling never breaks the
landing page. Ports come from env so the start script can override the
defaults (`PHYRA_ARCHBASE_PORT`, `PHYRA_DUALTRANS_PORT`).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

__version__ = "0.1.0"

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
STATIC = ROOT / "static"

PORT = int(os.environ.get("PORT", "8035"))
HOST = os.environ.get("HOST", "0.0.0.0")

# Sibling ports — start.sh exports these so the landing tiles + the
# "back to Center" banners agree on what host each service lives at.
ARCHBASE_PORT = int(os.environ.get("PHYRA_ARCHBASE_PORT", "8037"))
DUALTRANS_PORT = int(os.environ.get("PHYRA_DUALTRANS_PORT", "8039"))

# Service catalogue. `health_path` is the cheapest GET that returns 2xx
# when the service is alive; archbase has no /healthz so we probe "/"
# (its server.py always 200s on the index.html).
SERVICES: list[dict] = [
    {
        "kind": "library",
        "key": "phyra-archbase",
        "name": "phyra-archbase",
        "label": "📑 phyra-archbase",
        "tagline": "論文庫 · Archive & browse",
        "port": ARCHBASE_PORT,
        "health_path": "/",
    },
    {
        "kind": "library",
        "key": "phyra-dualtrans",
        "name": "phyra-dualtrans",
        "label": "📝 phyra-dualtrans",
        "tagline": "雙語翻譯 · BabelDOC + your model",
        "port": DUALTRANS_PORT,
        "health_path": "/healthz",
    },
]


def probe(host: str, port: int, path: str, timeout: float = 1.0) -> dict:
    """Best-effort HEAD/GET on a sibling. Never raises."""
    url = f"http://{host}:{port}{path}"
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            ok = 200 <= r.status < 400
            return {"reachable": ok, "status": r.status,
                    "latency_ms": int((time.monotonic() - t0) * 1000)}
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        return {"reachable": False, "status": None,
                "latency_ms": int((time.monotonic() - t0) * 1000),
                "error": str(e)[:120]}


def collect_services() -> list[dict]:
    """Per-service health. Probed against 127.0.0.1 (same host as Center)."""
    out = []
    for svc in SERVICES:
        info = dict(svc)
        info.pop("health_path", None)
        info["url_path"] = "/"
        info.update(probe("127.0.0.1", svc["port"], svc["health_path"]))
        out.append(info)
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def _json(self, code: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 — stdlib API
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            return self._json(HTTPStatus.OK,
                              {"ok": True, "version": __version__})
        if path == "/api/services":
            return self._json(HTTPStatus.OK, collect_services())
        if path == "/api/center":
            return self._json(HTTPStatus.OK, {"port": PORT})
        return super().do_GET()

    # Slightly quieter access log — matches archbase's style.
    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}", flush=True)


def main() -> None:
    if not (STATIC / "index.html").exists():
        raise SystemExit(f"missing landing page: {STATIC/'index.html'}")
    print(f"phyra-center serving {ROOT} on {HOST}:{PORT}", flush=True)
    print(f"  archbase  → :{ARCHBASE_PORT}", flush=True)
    print(f"  dualtrans → :{DUALTRANS_PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
