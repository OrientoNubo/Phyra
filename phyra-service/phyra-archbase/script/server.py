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
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
COLLECTION = ROOT / "collection"
TAGS_PATH = COLLECTION / "tags.json"
GENERATE = SCRIPT_DIR / "generate_index.py"

ADMIN_PW = os.environ.get("PHYRA_ARCHBASE_ADMIN_PASSWORD", "")

# Sibling phyra-dualtrans (same host). Used to auto-generate a bilingual PDF
# for a paper that has none: archbase uploads the original to dualtrans, polls
# the job, then asks dualtrans to archive the result straight back into THIS
# collection (its archive target auto-detects ../phyra-archbase). Port matches
# phyra-center/script/start.sh DT_PORT (overridable for standalone runs).
DUALTRANS_PORT = int(os.environ.get("PHYRA_DUALTRANS_PORT", "8039"))
DUALTRANS_HOST = os.environ.get("PHYRA_DUALTRANS_HOST", "127.0.0.1")

# arXiv: ids are downloaded directly from arxiv.org/pdf/<id>; a single id
# metadata lookup (fast, reliable — unlike full-text search) best-effort
# prefills the title. arXiv asks for a descriptive User-Agent.
_ARXIV_API = "https://export.arxiv.org/api/query"
_ARXIV_UA = ("phyra-archbase/0.1 "
             "(https://github.com/OrientoNubo/Phyra; mailto:d11922023@csie.ntu.edu.tw)")

# Stem construction, kept byte-for-byte in sync with phyra-dualtrans'
# vendor.resolve_input.build_stem so a paper imported here and the same paper
# translated through dualtrans land on the IDENTICAL stem (the bilingual PDF
# then attaches to the imported original).
_RX_UNSAFE_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_STEM_MAX_LEN = 180
_ARXIV_ID_RE = re.compile(
    r"^\d{4}\.\d{4,5}(v\d+)?$|^[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(v\d+)?$", re.I
)

# In-memory DualTrans job tracker, keyed by paper stem. A best-effort,
# process-local view the browse page polls; it is not persisted (a server
# restart simply forgets in-flight auto-translations, which dualtrans still
# finishes and archives on its own).
_DT_JOBS: dict[str, dict] = {}
_DT_LOCK = threading.Lock()

# artifact suffixes one paper stem can own (kept in sync with generate_index.py)
SUFFIXES = [
    "_analysis.zh-TW.html",
    "_analysis.zh-TW.md",
    "_bilingual.zh-TW.dual.pdf",
    "_draftslide.html",
    ".pdf",
]

# Per-artifact groups for granular delete (a "kind" → the suffix(es) it owns).
# Deleting a paper's bilingual / analysis / slide leaves the rest intact; the
# original PDF is intentionally NOT a granular kind (drop the whole paper via
# /api/delete instead). Analysis is a pair (viewer .html + source .md).
ARTIFACT_GROUPS = {
    "bilingual": ["_bilingual.zh-TW.dual.pdf"],
    "analysis":  ["_analysis.zh-TW.html", "_analysis.zh-TW.md"],
    "slide":     ["_draftslide.html"],
}

# Uploadable artifact kinds: extension → destination suffix. The analysis
# viewer is .html (drives the 📖 Analysis chip); .md is the source the index
# reads title/short-name from. Slides are a single .html.
UPLOAD_KINDS = {
    "analysis": {".html": "_analysis.zh-TW.html", ".md": "_analysis.zh-TW.md"},
    "slide":    {".html": "_draftslide.html"},
}

# Upload payloads are JSON-with-text (html/md are UTF-8 text; an analysis page
# may embed base64 figures, so allow comfortably more than the 1 MB tag cap).
MAX_UPLOAD_BYTES = 64 * 1024 * 1024
# Raw PDF upload (binary body, not JSON) — a generous ceiling for big papers.
MAX_PDF_BYTES = 96 * 1024 * 1024

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


def bilingual_files(stem: str) -> list[Path]:
    """All bilingual dual PDFs for a stem, ANY target language
    (``{stem}_bilingual.<lang>.dual.pdf``). Matched by string (not glob) so a
    stem with glob metacharacters can't misbehave; confined to collection/."""
    coll = COLLECTION.resolve()
    pref, suf = f"{stem}_bilingual.", ".dual.pdf"
    out = []
    try:
        for p in COLLECTION.iterdir():
            if (p.is_file() and p.name.startswith(pref)
                    and p.name.endswith(suf) and p.resolve().parent == coll):
                out.append(p)
    except OSError:
        pass
    return out


def files_for_stem(stem: str) -> list[Path]:
    """Existing artifact files owned by this stem, confined to collection/."""
    coll = COLLECTION.resolve()
    out = []
    for suf in SUFFIXES:
        if "_bilingual." in suf:        # any-language bilingual handled below
            continue
        p = COLLECTION / f"{stem}{suf}"
        if p.is_file() and p.resolve().parent == coll:
            out.append(p)
    out += bilingual_files(stem)
    return out


def regenerate() -> bool:
    """Re-run generate_index.py so index.html reflects collection/ on disk."""
    try:
        subprocess.run([sys.executable, str(GENERATE)],
                       check=True, cwd=str(ROOT), env=os.environ.copy())
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


# ---- DualTrans auto-translation (archbase → dualtrans → back here) --------

def _dt_url(path: str) -> str:
    return f"http://{DUALTRANS_HOST}:{DUALTRANS_PORT}{path}"


def _suggest_name(stem: str) -> tuple[str, str]:
    """(yymm, title) from a stem, mirroring dualtrans' archive.suggest_name
    so the bilingual artifact lands back under this paper's own filename."""
    m = re.match(r"^(\d{4})_(.*)$", stem or "")
    yymm, rest = (m.group(1), m.group(2)) if m else ("", stem or "")
    return yymm, rest.replace("__", ": ").replace("_", " ").strip()


def _set_dt(stem: str, **fields) -> None:
    with _DT_LOCK:
        _DT_JOBS.setdefault(stem, {}).update(fields)


def _get_dt(stem: str) -> dict:
    with _DT_LOCK:
        return dict(_DT_JOBS.get(stem, {}))


def _encode_multipart(fields: dict, files: list) -> tuple[bytes, str]:
    """Build a multipart/form-data body. `files` = [(name, filename, ctype,
    bytes), …]. Stdlib has no client multipart, so hand-roll it."""
    boundary = "----phyraArchbase" + uuid.uuid4().hex
    bb = boundary.encode()
    crlf = b"\r\n"
    buf = bytearray()
    for name, val in fields.items():
        buf += b"--" + bb + crlf
        buf += f'Content-Disposition: form-data; name="{name}"'.encode() + crlf + crlf
        buf += str(val).encode("utf-8") + crlf
    for name, filename, ctype, data in files:
        buf += b"--" + bb + crlf
        buf += (f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"').encode() + crlf
        buf += f"Content-Type: {ctype}".encode() + crlf + crlf
        buf += data + crlf
    buf += b"--" + bb + b"--" + crlf
    return bytes(buf), f"multipart/form-data; boundary={boundary}"


def _http_json(req: urllib.request.Request, timeout: float) -> dict:
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _dt_submit(pdf: bytes, filename: str, opts: dict | None = None) -> str:
    """Upload the original PDF to dualtrans for an ollama (local, ungated)
    translation. `opts` carries the common, model-agnostic settings
    (lang_out / compress / compat); the rest use dualtrans defaults. Returns
    the job id."""
    fields = {"backend": json.dumps({"kind": "ollama"})}
    if opts:
        fields["lang_out"] = opts.get("lang_out") or "zh-TW"
        fields["compress"] = opts.get("compress") or "lossy"
        fields["compat"] = "true" if opts.get("compat") else "false"
    body, ctype = _encode_multipart(
        fields,
        [("file", filename, "application/pdf", pdf)],
    )
    req = urllib.request.Request(
        _dt_url("/api/translate"), data=body,
        headers={"Content-Type": ctype}, method="POST",
    )
    return str(_http_json(req, timeout=60).get("job_id"))


def _dt_status(job_id: str) -> dict:
    req = urllib.request.Request(_dt_url(f"/api/jobs/{job_id}"), method="GET")
    return _http_json(req, timeout=30)


def _dt_archive(job_id: str, yymm: str, title: str) -> dict:
    data = urllib.parse.urlencode({"yymm": yymm, "title": title}).encode()
    req = urllib.request.Request(
        _dt_url(f"/api/jobs/{job_id}/archive"), data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    return _http_json(req, timeout=180)


def _dualtrans_worker(stem: str, opts: dict | None = None) -> None:
    """Run one paper's original PDF through dualtrans and archive the dual
    back here. Updates the per-stem tracker the browse page polls."""
    try:
        pdf = (COLLECTION / f"{stem}.pdf").read_bytes()
        yymm, title = _suggest_name(stem)
        _set_dt(stem, state="translating", pct=0, error=None)
        job_id = _dt_submit(pdf, f"{stem}.pdf", opts)
        _set_dt(stem, job_id=job_id)

        while True:
            time.sleep(2.0)
            v = _dt_status(job_id)
            st = v.get("status")
            prog = v.get("progress") or {}
            _set_dt(stem, pct=int(prog.get("overall_pct") or 0),
                    stage=prog.get("stage"))
            if st == "succeeded":
                break
            if st in ("failed", "canceled"):
                _set_dt(stem, state="error",
                        error=(v.get("error") or st))
                return

        _set_dt(stem, state="archiving")
        _dt_archive(job_id, yymm, title)   # writes the dual back into collection/
        regenerate()                        # belt-and-suspenders index refresh
        _set_dt(stem, state="done", pct=100)
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8")[:200]
        except Exception:  # noqa: BLE001
            pass
        _set_dt(stem, state="error",
                error=f"dualtrans HTTP {e.code}: {detail}")
    except (urllib.error.URLError, OSError) as e:
        _set_dt(stem, state="error",
                error=f"無法連線 dualtrans（:{DUALTRANS_PORT}）：{e}")
    except Exception as e:  # noqa: BLE001 — never let the worker thread die silently
        _set_dt(stem, state="error", error=str(e)[:300])


# ---- import a paper (arXiv link/id download, or PDF upload) ---------------

_ATOM = "{http://www.w3.org/2005/Atom}"
_NEW_ID = re.compile(r"\b(\d{4}\.\d{4,5})(v\d+)?\b")
_OLD_ID = re.compile(r"\b([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?\b", re.I)


def _detect_arxiv_id(text: str) -> str | None:
    """Pull an arXiv id from a bare id or an arxiv.org abs/pdf URL, else None."""
    s = (text or "").strip()
    if not s:
        return None
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([^\s?#]+)", s, re.I)
    if m:
        s = re.sub(r"\.pdf$", "", m.group(1), flags=re.I)
    m = _NEW_ID.search(s)
    if m:
        return m.group(1) + (m.group(2) or "")
    m = _OLD_ID.search(s)
    if m:
        return m.group(0)
    return None


def _yymm_from_arxiv(arxiv_id: str) -> str:
    m = re.match(r"^(\d{4})\.", arxiv_id)            # 2401.12345 → 2401
    if m:
        return m.group(1)
    m = re.search(r"/(\d{2})(\d{2})\d{3}", arxiv_id)  # hep-th/9901001 → 9901
    return (m.group(1) + m.group(2)) if m else ""


def _fetch_arxiv_meta(arxiv_id: str) -> dict:
    """Best-effort single-id metadata lookup (title/year/authors) to prefill
    the import dialog. Never raises — returns {} on any failure so import
    still works offline / when arXiv is rate-limiting."""
    base = re.sub(r"v\d+$", "", arxiv_id)
    qs = urllib.parse.urlencode({"id_list": base, "max_results": "1"})
    req = urllib.request.Request(
        f"{_ARXIV_API}?{qs}", headers={"User-Agent": _ARXIV_UA})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            root = ET.fromstring(r.read())
    except (urllib.error.URLError, OSError, ET.ParseError, ValueError):
        return {}
    entry = root.find(_ATOM + "entry")
    if entry is None:
        return {}

    def t(tag: str) -> str:
        el = entry.find(_ATOM + tag)
        return re.sub(r"\s+", " ", (el.text or "")).strip() if el is not None else ""

    title = t("title")
    if not title or title.lower() == "error":
        return {}
    authors = [
        (a.find(_ATOM + "name").text or "").strip()
        for a in entry.findall(_ATOM + "author")
        if a.find(_ATOM + "name") is not None
    ]
    return {"title": title, "year": t("published")[:4], "authors": authors}


def _sanitize_title(title: str) -> str:
    """Mirror dualtrans.sanitize_title_for_stem exactly."""
    s = (title or "").strip()
    if not s:
        return ""
    s = re.sub(r":\s+", "_", s)        # ": " acronym separator → single "_"
    s = _RX_UNSAFE_FS.sub("_", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def _build_stem(yymm: str, title: str, arxiv_id: str | None = None) -> str:
    sanitized = _sanitize_title(title)
    if not sanitized:
        sanitized = arxiv_id.split(".", 1)[1] if (arxiv_id and "." in arxiv_id) else "paper"
    stem = f"{yymm}_{sanitized}"
    if len(stem) > _STEM_MAX_LEN:
        stem = stem[:_STEM_MAX_LEN].rstrip("_")
    return stem


def _download_arxiv_pdf(arxiv_id: str, dest: Path) -> None:
    """Fetch https://arxiv.org/pdf/<id> to dest (atomic). Host is fixed to
    arxiv.org — the only input is the validated id, so there is no SSRF
    surface. Raises OSError/ValueError on failure."""
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    tmp = dest.with_name(dest.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "phyra-archbase/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, tmp.open("wb") as fh:
            shutil.copyfileobj(r, fh)
        data_head = tmp.open("rb").read(1024)
        if tmp.stat().st_size < 1024 or b"%PDF" not in data_head:
            raise ValueError("下載內容不是有效 PDF")
        tmp.replace(dest)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


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

    def _read_json(self, max_bytes=1_000_000):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None
        if n <= 0 or n > max_bytes:
            return None
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    # --- routing ---
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/tags":
            return self._json(HTTPStatus.OK, load_tags())
        if path == "/api/dualtrans/status":
            return self._get_dualtrans_status()
        if path == "/api/arxiv-meta":
            return self._get_arxiv_meta()
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/tags":
            return self._post_tags()
        if path == "/api/delete":
            return self._post_delete()
        if path == "/api/delete-artifact":
            return self._post_delete_artifact()
        if path == "/api/upload-artifact":
            return self._post_upload_artifact()
        if path == "/api/dualtrans":
            return self._post_dualtrans()
        if path == "/api/import-arxiv":
            return self._post_import_arxiv()
        if path == "/api/import-upload":
            return self._post_import_upload()
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

    def _post_delete_artifact(self):
        """Delete ONE artifact group (bilingual / analysis / slide) of a
        paper, leaving the rest of its files in place. Admin-gated, exactly
        like whole-paper delete — removing a file is destructive."""
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
        kind = str(data.get("kind", ""))
        if not valid_stem(key):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad key"})
        if kind not in ARTIFACT_GROUPS:
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad kind"})

        coll = COLLECTION.resolve()
        # bilingual: delete every language variant; others: fixed suffix(es)
        if kind == "bilingual":
            targets = bilingual_files(key)
        else:
            targets = [COLLECTION / f"{key}{suf}" for suf in ARTIFACT_GROUPS[kind]]
        removed = []
        for p in targets:
            if p.is_file() and p.resolve().parent == coll:
                try:
                    p.unlink()
                    removed.append(p.name)
                except OSError:
                    pass
        if not removed:
            return self._json(HTTPStatus.NOT_FOUND,
                              {"ok": False, "error": "查無此檔案"})
        index_ok = regenerate()
        return self._json(HTTPStatus.OK,
                          {"ok": True, "removed": removed, "index_ok": index_ok})

    def _post_upload_artifact(self):
        """Attach an analysis (.html/.md) or slide (.html) file to an EXISTING
        paper stem. No password (additive, non-destructive — mirrors free tag
        editing). The stem must already own at least one file so an upload
        can't fabricate an arbitrary new collection entry."""
        data = self._read_json(max_bytes=MAX_UPLOAD_BYTES)
        if not isinstance(data, dict):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad json"})
        key = str(data.get("key", ""))
        kind = str(data.get("kind", ""))
        filename = str(data.get("filename", ""))
        content = data.get("content", "")
        if not valid_stem(key):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad key"})
        ext_map = UPLOAD_KINDS.get(kind)
        if not ext_map:
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad kind"})
        if not isinstance(content, str) or not content:
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "empty content"})
        ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
        suffix = ext_map.get(ext)
        if not suffix:
            allowed = "／".join(ext_map)
            return self._json(HTTPStatus.BAD_REQUEST,
                              {"ok": False, "error": f"{kind} 僅接受 {allowed} 檔"})
        # the stem must already exist (an upload augments a known paper)
        if not files_for_stem(key):
            return self._json(HTTPStatus.NOT_FOUND,
                              {"ok": False, "error": "查無此論文"})

        coll = COLLECTION.resolve()
        dest = COLLECTION / f"{key}{suffix}"
        if dest.resolve().parent != coll:
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad path"})
        try:
            tmp = dest.with_name(dest.name + ".tmp")
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(dest)
        except OSError as e:
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR,
                              {"ok": False, "error": f"寫入失敗：{e}"})
        index_ok = regenerate()
        return self._json(HTTPStatus.OK,
                          {"ok": True, "file": dest.name, "index_ok": index_ok})

    def _post_dualtrans(self):
        """Kick off (or report) an auto-translation of a paper that has no
        bilingual PDF yet. No password — it only spends the local GPU via the
        ungated ollama backend and is additive (mirrors the upload path)."""
        data = self._read_json()
        if not isinstance(data, dict):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad json"})
        key = str(data.get("key", ""))
        if not valid_stem(key):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad key"})
        if not (COLLECTION / f"{key}.pdf").is_file():
            return self._json(HTTPStatus.NOT_FOUND,
                              {"ok": False, "error": "查無原文 PDF，無法翻譯"})
        if bilingual_files(key):
            _set_dt(key, state="done", pct=100)
            return self._json(HTTPStatus.OK, {"ok": True, "state": "done"})

        cur = _get_dt(key)
        if cur.get("state") in ("translating", "archiving"):
            return self._json(HTTPStatus.OK, {"ok": True, **cur})

        # common, model-agnostic translation settings (rest use dualtrans defaults)
        compress = str(data.get("compress", "") or "lossy")
        if compress not in ("off", "lossless", "lossy"):
            compress = "lossy"
        opts = {
            "lang_out": (str(data.get("lang_out", "") or "zh-TW").strip() or "zh-TW"),
            "compress": compress,
            "compat": bool(data.get("compat", False)),
        }
        _set_dt(key, state="translating", pct=0, error=None, job_id=None)
        threading.Thread(target=_dualtrans_worker, args=(key, opts),
                         daemon=True).start()
        return self._json(HTTPStatus.OK, {"ok": True, "state": "translating"})

    def _get_dualtrans_status(self):
        params = urllib.parse.parse_qs(self.path.split("?", 1)[1]
                                       if "?" in self.path else "")
        key = (params.get("key") or [""])[0]
        if not valid_stem(key):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad key"})
        st = _get_dt(key)
        if not st:
            # not tracked here (never started, or forgotten on restart) — fall
            # back to what's on disk so the UI can still settle correctly
            st = {"state": "done" if bilingual_files(key) else "idle"}
        return self._json(HTTPStatus.OK, {"ok": True, **st})

    def _resolve_import_target(self, yymm: str, title: str,
                               arxiv_id: str | None = None):
        """Validate (yymm, title), build the stem, and return (dest, stem) for
        a new paper. On any problem it writes the error response and returns
        None (the caller should just return)."""
        if not re.fullmatch(r"\d{4}", yymm or ""):
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "YYMM 需為 4 位數字"})
            return None
        if not (title or "").strip():
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "標題不可為空"})
            return None
        stem = _build_stem(yymm, title, arxiv_id)
        if not valid_stem(stem):
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad stem"})
            return None
        coll = COLLECTION.resolve()
        dest = COLLECTION / f"{stem}.pdf"
        if dest.resolve().parent != coll:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad path"})
            return None
        if dest.exists():
            self._json(HTTPStatus.CONFLICT,
                       {"ok": False, "error": "此論文已存在於庫中", "stem": stem})
            return None
        return dest, stem

    def _get_arxiv_meta(self):
        """Resolve an arXiv link/id → {arxiv_id, yymm, title?, year?} to
        prefill the import dialog. Title is best-effort (a single fast id
        lookup); the dialog still works if it comes back empty."""
        params = urllib.parse.parse_qs(self.path.split("?", 1)[1]
                                       if "?" in self.path else "")
        ref = (params.get("ref") or [""])[0]
        aid = _detect_arxiv_id(ref)
        if not aid:
            return self._json(HTTPStatus.BAD_REQUEST,
                              {"ok": False, "error": "無法辨識 arXiv 連結 / id"})
        base = re.sub(r"v\d+$", "", aid)
        return self._json(HTTPStatus.OK, {
            "ok": True, "arxiv_id": base, "yymm": _yymm_from_arxiv(base),
            **_fetch_arxiv_meta(aid),
        })

    def _post_import_arxiv(self):
        """Download an arXiv paper's PDF into collection/ as a new block. No
        password (additive). Host is fixed to arxiv.org and only a validated
        id is interpolated — no SSRF surface."""
        data = self._read_json()
        if not isinstance(data, dict):
            return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad json"})
        ref = str(data.get("ref", "") or data.get("arxiv_id", "")).strip()
        aid = _detect_arxiv_id(ref)
        if not aid or not _ARXIV_ID_RE.match(aid):
            return self._json(HTTPStatus.BAD_REQUEST,
                              {"ok": False, "error": "無法辨識 arXiv 連結 / id"})
        base = re.sub(r"v\d+$", "", aid)
        yymm = str(data.get("yymm", "")).strip() or _yymm_from_arxiv(base)
        title = str(data.get("title", "")).strip()
        target = self._resolve_import_target(yymm, title, base)
        if target is None:
            return
        dest, stem = target
        COLLECTION.mkdir(parents=True, exist_ok=True)
        try:
            _download_arxiv_pdf(aid, dest)
        except (urllib.error.URLError, OSError, ValueError) as e:
            return self._json(HTTPStatus.BAD_GATEWAY,
                              {"ok": False, "error": f"下載失敗：{e}"})
        index_ok = regenerate()
        return self._json(HTTPStatus.OK,
                          {"ok": True, "stem": stem, "file": dest.name,
                           "index_ok": index_ok})

    def _post_import_upload(self):
        """Create a new block from an uploaded PDF. The request body IS the
        raw PDF (Content-Type application/pdf); yymm + title ride in the query
        string — no multipart parsing needed. No password (additive)."""
        params = urllib.parse.parse_qs(self.path.split("?", 1)[1]
                                       if "?" in self.path else "")
        yymm = (params.get("yymm") or [""])[0].strip()
        title = (params.get("title") or [""])[0].strip()
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n <= 0 or n > MAX_PDF_BYTES:
            return self._json(HTTPStatus.BAD_REQUEST,
                              {"ok": False, "error": "檔案大小不正確或過大"})
        data = self.rfile.read(n)
        if b"%PDF-" not in data[:1024]:
            return self._json(HTTPStatus.BAD_REQUEST,
                              {"ok": False, "error": "上傳的檔案不是 PDF"})
        target = self._resolve_import_target(yymm, title)
        if target is None:
            return
        dest, stem = target
        COLLECTION.mkdir(parents=True, exist_ok=True)
        try:
            tmp = dest.with_name(dest.name + ".part")
            tmp.write_bytes(data)
            tmp.replace(dest)
        except OSError as e:
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR,
                              {"ok": False, "error": f"寫入失敗：{e}"})
        index_ok = regenerate()
        return self._json(HTTPStatus.OK,
                          {"ok": True, "stem": stem, "file": dest.name,
                           "index_ok": index_ok})


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
