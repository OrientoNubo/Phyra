"""
slice_pdf.py — pass-through (references are no longer page-sliced).

History: this module used to strip whole "References" pages before
BabelDOC to save cost, re-injecting grey "[reference page — translation
skipped]" placeholders in build_dual. That page-granular heuristic was
unreliable in BOTH directions — it skipped nothing on 2501_CubeDiff (all
references got translated) yet could drop a body/appendix page elsewhere
— and a grey placeholder is not 「原樣」: the user wants the original
references to stay VISIBLE, just untranslated.

References (and figure/table content) are now handled at PARAGRAPH
granularity inside the translation child by `il_filter` (a subclass of
BabelDOC's ILTranslator). That is robust to mixed pages and keeps the
original text in place. So slicing is a no-op: the whole PDF is passed
through and `build_dual` produces a straight full-length side-by-side
(``ref_pages == []`` — a path it already supports).

The function signature and `meta` schema are unchanged so jobs.py and
build_dual need no changes (full removal of this stage is deferred).

Usage:
  python slice_pdf.py <source.pdf> <PARSED_PAPER.md|-> <out.pdf> <meta.json>
"""

import json
import logging
import sys
from pathlib import Path

import fitz  # PyMuPDF

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("slice_pdf")


def slice_pdf(
    src_pdf: Path,
    parsed_paper_md: Path | None,  # accepted for signature compat; unused
    out_sliced: Path,
    out_meta: Path,
) -> dict:
    """Pass the whole PDF through. References are kept (handled, and left
    as original, by il_filter at paragraph level). Returns the meta dict."""
    with fitz.open(src_pdf) as doc:
        total_pages = len(doc)

    out_sliced.parent.mkdir(parents=True, exist_ok=True)
    out_sliced.write_bytes(src_pdf.read_bytes())

    meta = {
        "schema_version": 1,
        "total_pages": total_pages,
        "ref_start_page": None,
        "ref_pages": [],
        "kept_pages": list(range(1, total_pages + 1)),
    }
    out_meta.parent.mkdir(parents=True, exist_ok=True)
    out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log.info(
        "pass-through: %d pages kept (references handled per-paragraph "
        "by il_filter, kept as original)", total_pages,
    )
    return meta


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(2)
    slice_pdf(
        Path(sys.argv[1]).resolve(),
        None,
        Path(sys.argv[3]).resolve(),
        Path(sys.argv[4]).resolve(),
    )
