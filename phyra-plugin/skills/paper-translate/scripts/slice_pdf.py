"""
slice_pdf.py (v0.9.0) — strip References / Bibliography pages before BabelDOC.

Why: References pages are bibliographic noise — translating them wastes
~30% of BabelDOC time + cost. We slice them off, translate only non-ref
pages, and `build_dual.py` re-injects the original ref pages with a
"[reference page — translation skipped]" placeholder on the translation side.

PARSED_PAPER.md is optional. When present (e.g. paper-read previously ran
on the same PDF and populated `.phyra/.cache/<STEM>/`), we read the ref
start page from it; otherwise we fall back to a PDF-only heuristic.

Usage:
  uv run --with pymupdf python slice_pdf.py \\
      <source.pdf> <PARSED_PAPER.md|-> <out_sliced.pdf> <out_meta.json>

Pass `-` (a single hyphen) for PARSED_PAPER.md to skip the parsed lookup
and use the PDF heuristic only.
"""

import json
import logging
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("slice_pdf")


REF_HEADERS_RX = re.compile(
    r"^\s*(?:\d+\s+)?(References?|Bibliography|REFERENCES?|BIBLIOGRAPHY)\s*$",
    re.MULTILINE,
)


def find_ref_start_page_from_pdf(pdf_path: Path) -> int | None:
    """Return the 1-indexed page number where References starts, or None.

    Heuristic: scan from page ceil(N*0.3) onward for a line that's exactly
    "References" or "Bibliography" (with optional section number prefix).
    Take the LAST such match because some papers re-mention "References" in
    section sub-headings earlier in the body.
    """
    last_hit = None
    with fitz.open(pdf_path) as doc:
        n = len(doc)
        start = max(1, int(n * 0.3))
        for i in range(start, n + 1):
            t = doc[i - 1].get_text("text")
            if REF_HEADERS_RX.search(t):
                last_hit = i
    return last_hit


def find_ref_start_page_from_parsed(parsed_md: Path) -> int | None:
    """Try to extract ref start page from a PARSED_PAPER.md if it lists
    section page numbers in a parsable form (e.g. `- §References (p.17)`)."""
    try:
        text = parsed_md.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    # Look for section-list lines containing References + a page hint
    rx = re.compile(
        r"(?:References?|Bibliography)[^\n]{0,80}?p\.?\s*(\d+)",
        re.IGNORECASE,
    )
    matches = [int(m.group(1)) for m in rx.finditer(text)]
    return matches[-1] if matches else None


def slice_pdf(
    src_pdf: Path,
    parsed_paper_md: Path | None,
    out_sliced: Path,
    out_meta: Path,
) -> dict:
    """Slice off ref pages; emit out_sliced.pdf + out_meta.json.

    Returns the meta dict.
    """
    with fitz.open(src_pdf) as doc:
        total_pages = len(doc)

    # Two-source detection (parsed first, PDF scan as fallback)
    ref_start = None
    if parsed_paper_md and parsed_paper_md.exists():
        ref_start = find_ref_start_page_from_parsed(parsed_paper_md)
        if ref_start:
            log.info("ref start from PARSED_PAPER: page %d", ref_start)
    if not ref_start:
        ref_start = find_ref_start_page_from_pdf(src_pdf)
        if ref_start:
            log.info("ref start from PDF scan: page %d", ref_start)

    if not ref_start or ref_start <= 1:
        # No refs found, or refs start on page 1 (impossible) — copy whole PDF
        log.warning("no ref start detected; copying full PDF")
        out_sliced.write_bytes(src_pdf.read_bytes())
        meta = {
            "schema_version": 1,
            "total_pages": total_pages,
            "ref_start_page": None,
            "ref_pages": [],
            "kept_pages": list(range(1, total_pages + 1)),
        }
    else:
        # Keep pages 1..ref_start-1
        with fitz.open(src_pdf) as doc:
            sliced = fitz.open()
            sliced.insert_pdf(doc, from_page=0, to_page=ref_start - 2)
            out_sliced.parent.mkdir(parents=True, exist_ok=True)
            sliced.save(out_sliced)
            sliced.close()
        meta = {
            "schema_version": 1,
            "total_pages": total_pages,
            "ref_start_page": ref_start,
            "ref_pages": list(range(ref_start, total_pages + 1)),
            "kept_pages": list(range(1, ref_start)),
        }
        log.info("sliced %d pages → kept %d, dropped %d (refs)",
                 total_pages, len(meta["kept_pages"]), len(meta["ref_pages"]))

    out_meta.parent.mkdir(parents=True, exist_ok=True)
    out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(2)
    parsed_arg = sys.argv[2]
    if parsed_arg == "-":
        parsed = None
    else:
        parsed = Path(parsed_arg).resolve()
        if not parsed.exists():
            parsed = None
    slice_pdf(
        Path(sys.argv[1]).resolve(),
        parsed,
        Path(sys.argv[3]).resolve(),
        Path(sys.argv[4]).resolve(),
    )
