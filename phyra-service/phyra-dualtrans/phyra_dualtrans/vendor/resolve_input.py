"""
resolve_input.py — VENDORED from Phyra paper-read (v0.9.2), decoupled.

Resolves the user's argument into a local PDF plus an output directory +
filename stem. Upstream this had a CLI `main()` defaulting the out dir to
`<cwd>/.phyra/papers`; here `main()` is removed and callers MUST pass an
explicit `override_out_dir` (the per-job working dir). The arXiv
detection / title fetch / sanitize / download logic is kept byte-faithful
so stems stay identical to Phyra.

Accepted inputs:
  (a) a local PDF path           → out_dir defaults to override_out_dir
  (b) an arXiv URL               → download to override_out_dir/<stem>.pdf
        https://arxiv.org/abs/2402.15391
        https://arxiv.org/pdf/2402.15391
  (c) a bare arXiv id            → same as (b)
        2402.15391

`resolve(arg, *, override_out_dir=...)` returns:
  {
    "pdf_path": "/abs/path/to/2402_Genie_....pdf",
    "out_dir":  "/abs/path/to",
    "stem":     "2402_Genie_...",
    "kind":     "local" | "arxiv-url" | "arxiv-id",
    "arxiv_id": "2402.15391" | None,
    "title":    "Genie: ..." | None,
  }
"""

import logging
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("resolve-input")


_RX_ARXIV_URL = re.compile(
    r"https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?",
    re.IGNORECASE,
)
_RX_ARXIV_BARE = re.compile(r"^\s*(\d{4}\.\d{4,5})(?:v\d+)?\s*$")


def detect_arxiv_id(arg: str) -> str | None:
    m = _RX_ARXIV_URL.search(arg)
    if m:
        return m.group(1)
    m = _RX_ARXIV_BARE.match(arg)
    if m:
        return m.group(1)
    return None


def fetch_arxiv_title(arxiv_id: str) -> str | None:
    """Fetch the arXiv abstract page; return the paper title or None."""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "phyra-dualtrans/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_text = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        log.warning("arxiv title fetch failed for %s: %s", arxiv_id, e)
        return None

    m = re.search(
        r'<meta\s+name="citation_title"\s+content="([^"]+)"', html_text,
    )
    if m:
        return m.group(1).strip()
    m = re.search(r"<title>(.*?)</title>", html_text, re.DOTALL | re.IGNORECASE)
    if m:
        t = m.group(1).strip()
        # arXiv prepends "[2402.15391] " — strip it.
        t = re.sub(r"^\[[^\]]+\]\s*", "", t)
        return t
    return None


def yymm_from_arxiv_id(arxiv_id: str) -> str:
    return arxiv_id.split(".")[0]  # e.g. "2503"


# Filesystem-unsafe characters (Windows reserved set + control bytes).
# Forward slash is the POSIX path separator, so it must be replaced too.
_RX_UNSAFE_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Stem length cap. POSIX allows 255 bytes per name; we leave headroom for
# downstream suffixes like ``_bilingual.zh-TW.dual.pdf``.
_STEM_MAX_LEN = 180


def sanitize_title_for_stem(title: str) -> str:
    """Turn a paper title into a filesystem-safe stem fragment.

    Spaces are converted to underscores so shell drivers can use ``$STEM``
    unquoted without worrying about word-splitting.
    """
    s = (title or "").strip()
    if not s:
        return ""
    # ": " is the canonical acronym separator — collapse to a single "_"
    # so "Genie: Generative ..." becomes "Genie_Generative ..." rather
    # than "Genie__Generative ...".
    s = re.sub(r":\s+", "_", s)
    # Any other filesystem-unsafe char → "_".
    s = _RX_UNSAFE_FS.sub("_", s)
    # Every remaining whitespace run → single "_" (Plan B: no spaces).
    s = re.sub(r"\s+", "_", s)
    # Collapse underscore runs.
    s = re.sub(r"_+", "_", s)
    # Trim leading/trailing separators.
    s = s.strip("_")
    return s


def build_stem(yymm: str, title: str | None, arxiv_id: str | None = None) -> str:
    """Compose the final stem ``<YYMM>_<sanitized-title>``.

    When the title is unavailable, fall back to the arXiv suffix (e.g.
    ``2402_15391`` for ``2402.15391``).
    """
    sanitized = sanitize_title_for_stem(title or "")
    if not sanitized:
        if arxiv_id and "." in arxiv_id:
            sanitized = arxiv_id.split(".", 1)[1]
        else:
            sanitized = "paper"
    stem = f"{yymm}_{sanitized}"
    if len(stem) > _STEM_MAX_LEN:
        stem = stem[:_STEM_MAX_LEN].rstrip("_")
    return stem


def download_arxiv_pdf(arxiv_id: str, dest: Path) -> None:
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    log.info("downloading %s → %s", url, dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Prefer curl for resiliency; fall back to urllib.
    if shutil.which("curl"):
        rc = subprocess.run(
            ["curl", "-sL", "-A", "phyra-dualtrans/0.1", "-o", str(dest), url],
            check=False,
        ).returncode
        if rc == 0 and dest.exists() and dest.stat().st_size > 1024:
            return
    req = urllib.request.Request(url, headers={"User-Agent": "phyra-dualtrans/0.1"})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as fh:
        shutil.copyfileobj(resp, fh)


def resolve(arg: str, *, override_out_dir: Path) -> dict:
    """Resolve `arg` (local path | arXiv URL | arXiv id) to a PDF + stem.

    `override_out_dir` is required (no `.phyra/papers` fallback): for the
    web service this is always the per-job working directory.
    """
    out_dir = Path(override_out_dir).resolve()
    arxiv_id = detect_arxiv_id(arg)

    if arxiv_id is not None:
        title = fetch_arxiv_title(arxiv_id)
        yymm = yymm_from_arxiv_id(arxiv_id)
        stem = build_stem(yymm, title, arxiv_id)

        pdf_path = out_dir / f"{stem}.pdf"
        if not pdf_path.exists():
            download_arxiv_pdf(arxiv_id, pdf_path)
            log.info("title=%r → %s", title, pdf_path)
        else:
            log.info("already downloaded: %s", pdf_path)

        kind = "arxiv-url" if arg.lower().startswith("http") else "arxiv-id"
        return {
            "pdf_path": str(pdf_path),
            "out_dir": str(out_dir),
            "stem": stem,
            "kind": kind,
            "arxiv_id": arxiv_id,
            "title": title,
        }

    # Local PDF path
    candidate = Path(arg).expanduser().resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"local PDF not found: {candidate}")
    if candidate.suffix.lower() != ".pdf":
        log.warning("local file does not have .pdf extension: %s", candidate)
    return {
        "pdf_path": str(candidate),
        "out_dir": str(out_dir),
        "stem": candidate.stem,
        "kind": "local",
        "arxiv_id": None,
        "title": None,
    }
