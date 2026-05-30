#!/usr/bin/env python3
"""phyra-archbase — static file server + a tiny mutation API.

Plain stdlib (no framework), matching generate_index.py's zero-dependency
style. Serves the generated site AND three endpoints the browse page needs:

  GET  /api/tags     -> collection/tags.json  ({} when absent)
  POST /api/tags     -> {"key": <stem>, "tags": [...]}     (no password)
  POST /api/delete   -> {"key": <stem>, "password": ...}   (admin only)

Tags are free to edit (low-risk, LAN-trusted). Deleting a paper removes
every artifact file for its stem, drops its tags, and regenerates
index.html — it requires the admin password from
$PHYRA_ARCHBASE_ADMIN_PASSWORD (unset = delete disabled, returns 403).
"""

import hmac
import json
import os
import re
import subprocess
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
COLLECTION = ROOT / "collection"
TAGS_PATH = COLLECTION / "tags.json"
GENERATE = SCRIPT_DIR / "generate_index.py"

ADMIN_PW = os.environ.get("PHYRA_ARCHBASE_ADMIN_PASSWORD", "")

# artifact suffixes one paper stem can own (kept in sync with generate_index.py)
SUFFIXES = [
    "_analysis.zh-TW.html",
    "_analysis.zh-TW.md",
    "_bilingual.zh-TW.dual.pdf",
    "_draftslide.html",
    ".pdf",
]

# a stem is a single path component — no separators, no traversal, no controls
STEM_RE = re.compile(r"[^/\\\x00-\x1f]+")


def load_tags() -> dict:
    try:
        data = json.loads(TAGS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_tags(tags: dict) -> None:
    COLLECTION.mkdir(parents=True, exist_ok=True)
    tmp = TAGS_PATH.with_name("tags.json.tmp")
    tmp.write_text(json.dumps(tags, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    tmp.replace(TAGS_PATH)


def valid_stem(key: str) -> bool:
    return bool(key) and STEM_RE.fullmatch(key) is not None and ".." not in key


def files_for_stem(stem: str) -> list[Path]:
    """Existing artifact files owned by this stem, confined to collection/."""
    coll = COLLECTION.resolve()
    out = []
    for suf in SUFFIXES:
        p = COLLECTION / f"{stem}{suf}"
        if p.is_file() and p.resolve().parent == coll:
            out.append(p)
    return out


def regenerate() -> bool:
    """Re-run generate_index.py so index.html reflects collection/ on disk."""
    try:
        subprocess.run([sys.executable, str(GENERATE)],
                       check=True, cwd=str(ROOT), env=os.environ.copy())
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    # --- response helpers ---
    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None
        if n <= 0 or n > 1_000_000:
            return None
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    # --- routing ---
    def do_GET(self):
        if self.path.split("?", 1)[0] == "/api/tags":
            return self._json(HTTPStatus.OK, load_tags())
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/tags":
            return self._post_tags()
        if path == "/api/delete":
            return self._post_delete()
        self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "unknown endpoint"})

    def _post_tags(self):
        data = self._read_json()
        if not isinstance(data, dict):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad json"})
        key = str(data.get("key", ""))
        raw = data.get("tags", [])
        if not valid_stem(key):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad key"})
        if not isinstance(raw, list):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad tags"})
        # normalize: trim, cap length, dedupe case-insensitively (keep first), cap count
        seen, tags = set(), []
        for t in raw:
            t = str(t).strip()[:40]
            if t and t.lower() not in seen:
                seen.add(t.lower())
                tags.append(t)
            if len(tags) >= 20:
                break
        store = load_tags()
        if tags:
            store[key] = tags
        else:
            store.pop(key, None)
        save_tags(store)
        return self._json(HTTPStatus.OK, {"ok": True, "tags": tags})

    def _post_delete(self):
        if not ADMIN_PW:
            return self._json(HTTPStatus.FORBIDDEN, {
                "ok": False,
                "error": "刪除未啟用：啟動時未設定 PHYRA_ARCHBASE_ADMIN_PASSWORD",
            })
        data = self._read_json()
        if not isinstance(data, dict):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad json"})
        if not hmac.compare_digest(str(data.get("password", "")), ADMIN_PW):
            return self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "管理員密碼錯誤"})
        key = str(data.get("key", ""))
        if not valid_stem(key):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad key"})
        files = files_for_stem(key)
        if not files:
            return self._json(HTTPStatus.NOT_FOUND,
                              {"ok": False, "error": "查無此論文的檔案"})
        removed = []
        for p in files:
            try:
                p.unlink()
                removed.append(p.name)
            except OSError:
                pass
        store = load_tags()
        if store.pop(key, None) is not None:
            save_tags(store)
        index_ok = regenerate()
        return self._json(HTTPStatus.OK,
                          {"ok": True, "removed": removed, "index_ok": index_ok})


def main():
    port = int(os.environ.get("PORT", "8037"))
    host = os.environ.get("HOST", "0.0.0.0")
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Serving {ROOT} on {host}:{port}")
    print("delete: " + ("enabled (admin password set)"
                         if ADMIN_PW else
                         "DISABLED — set PHYRA_ARCHBASE_ADMIN_PASSWORD to enable"))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
