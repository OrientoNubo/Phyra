"""
resolve_input.py (v0.9.2) — resolve the user's argument into a local PDF
plus an output directory + filename stem.

The /phyra:paper-read user can pass:

  (a) an absolute or relative local PDF path:
        /home/nubo/papers/2402_Genie_Generative_Interactive_Environments.pdf
      → outputs go in `/home/nubo/papers/` with stem = file stem (unchanged).

  (b) an arXiv URL:
        https://arxiv.org/abs/2402.15391
        https://arxiv.org/pdf/2402.15391
      → download to `<cwd>/.phyra/papers/<YYMM>_<title>.pdf`,
        outputs go alongside (in `.phyra/papers/`).

  (c) a bare arXiv id:
        2402.15391
      → same as (b).

Stem construction for arXiv inputs (v0.9.2+):

  The stem is the full sanitized arXiv title prefixed with the YYMM
  month code. No acronym / short-name derivation: the full title is
  more recognisable in a file listing, and it stays a single function
  of the title alone (predictable, easy to debug).

  Example titles → stems:
    "Genie: Generative Interactive Environments"
      → "2402_Genie_Generative_Interactive_Environments"
    "USP: Unified Self-supervised Pretraining ..."
      → "2503_USP_Unified_Self-supervised_Pretraining_..."
    "Attention Is All You Need"
      → "1706_Attention_Is_All_You_Need"
    (title fetch failed)
      → "<YYMM>_<arxiv-suffix>"  e.g. "2402_15391"

  Sanitization rules for the title portion of the stem:
    - ": " (colon + space) collapses to a single "_".
    - Any remaining ":" becomes "_".
    - Other filesystem-unsafe characters (Windows reserved: <>"/\\|?*
      and control bytes) become "_".
    - Every remaining whitespace character becomes "_" (no spaces in
      stems — that keeps shell drivers in the paper-read / paper-translate
      SKILLs simple and quote-free).
    - Underscore runs are collapsed.
    - The full stem (incl. "<YYMM>_") is capped at ~180 chars.

Output: prints JSON to stdout with:
  {
    "pdf_path": "/abs/path/to/2402_Genie_Generative_Interactive_Environments.pdf",
    "out_dir": "/abs/path/to",
    "stem": "2402_Genie_Generative_Interactive_Environments",
    "kind": "local" | "arxiv-url" | "arxiv-id"
  }

Usage:
  uv run --with pymupdf python resolve_input.py <arg> [<override-out-dir>]
"""

import json
import logging
import re
import shutil
import subprocess
import sys
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
    """Fetch the arXiv abstract page; return the paper title or None.

    We do not fetch the abstract any more — the v0.9.2 stem rule depends
    only on the title.
    """
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Phyra/0.9.2"})
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
# downstream suffixes like ``_analysis.zh-TW.html`` (≈ 20 chars) and any
# wide-char encoding overhead.
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
    ``2402_15391`` for ``2402.15391``) — uniqueness is preserved without
    needing acronym derivation.
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
            ["curl", "-sL", "-A", "Phyra/0.8.1", "-o", str(dest), url],
            check=False,
        ).returncode
        if rc == 0 and dest.exists() and dest.stat().st_size > 1024:
            return
    req = urllib.request.Request(url, headers={"User-Agent": "Phyra/0.8.1"})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as fh:
        shutil.copyfileobj(resp, fh)


def resolve(arg: str, *, override_out_dir: Path | None = None) -> dict:
    arxiv_id = detect_arxiv_id(arg)

    if arxiv_id is not None:
        # arXiv URL or bare id
        title = fetch_arxiv_title(arxiv_id)
        yymm = yymm_from_arxiv_id(arxiv_id)
        stem = build_stem(yymm, title, arxiv_id)

        out_dir = override_out_dir or (Path.cwd() / ".phyra/papers")
        out_dir = out_dir.resolve()
        pdf_path = out_dir / f"{stem}.pdf"

        if not pdf_path.exists():
            download_arxiv_pdf(arxiv_id, pdf_path)
            log.info("title='%s' → %s", title, pdf_path)
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
    out_dir = override_out_dir or candidate.parent
    out_dir = out_dir.resolve()
    return {
        "pdf_path": str(candidate),
        "out_dir": str(out_dir),
        "stem": candidate.stem,
        "kind": "local",
        "arxiv_id": None,
        "title": None,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    arg = sys.argv[1]
    override_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    info = resolve(arg, override_out_dir=override_dir)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
