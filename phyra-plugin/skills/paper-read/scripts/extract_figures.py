"""
extract_figures.py (v0.8.0) — rasterize key pages from the source PDF for use
by paper-analyzer (multimodal A4 METHOD call) and paper-slide-maker.

Strategy:
  1. Read BIBLIO.main_pipeline_figure.page → always rasterize that page.
  2. Read PARSED_PAPER.md figure list → rasterize each page that contains a
     figure (deduped).
  3. Output PNGs at 200 DPI to `<out_dir>/page_{NNN}.png`. The naming uses
     the source PDF page number, zero-padded to 3 digits.

We rasterize whole pages rather than trying to crop figure regions. Cropping
is unreliable across journal layouts; the slide-maker can run a second pass
later if cropping is needed.

Usage:
  uv run --with pymupdf python extract_figures.py \\
      <source.pdf> <PARSED_PAPER.md> <BIBLIO.json> <out_dir>
"""

import json
import logging
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("extract-figures")

DPI = 200


def parse_figure_pages_from_md(parsed_md: str) -> list[int]:
    """Extract the set of page numbers mentioned by figure entries in
    PARSED_PAPER.md. The expected format (per paper-parser) is something
    like:
        - Figure 1: ... Location: p. 3
        - Figure 2: ... Location: pp. 4-5
    """
    pages: set[int] = set()
    rx = re.compile(
        r"^\s*-\s+Figure\s+\d+[:.].{0,500}?Location:\s*p+\.?\s*(\d+)(?:\s*[–\-]\s*(\d+))?",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    for m in rx.finditer(parsed_md):
        try:
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else start
            pages.update(range(start, end + 1))
        except (TypeError, ValueError):
            continue
    return sorted(pages)


def rasterize(pdf_path: Path, page_numbers: list[int], out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    with fitz.open(pdf_path) as doc:
        n = len(doc)
        for pn in page_numbers:
            if not (1 <= pn <= n):
                log.warning("page %d out of range (1..%d) — skipping", pn, n)
                continue
            target = out_dir / f"page_{pn:03d}.png"
            if target.exists():
                continue
            mat = fitz.Matrix(DPI / 72.0, DPI / 72.0)
            pix = doc[pn - 1].get_pixmap(matrix=mat)
            pix.save(str(target))
            written += 1
    return written


def main() -> int:
    if len(sys.argv) < 5:
        print(__doc__)
        return 2
    pdf_path = Path(sys.argv[1]).resolve()
    parsed_md_path = Path(sys.argv[2]).resolve()
    biblio_path = Path(sys.argv[3]).resolve()
    out_dir = Path(sys.argv[4]).resolve()

    parsed_md = parsed_md_path.read_text(encoding="utf-8") if parsed_md_path.exists() else ""
    biblio = json.loads(biblio_path.read_text(encoding="utf-8"))

    pages: set[int] = set(parse_figure_pages_from_md(parsed_md))
    main_fig = (biblio.get("main_pipeline_figure") or {}).get("page")
    if isinstance(main_fig, int):
        pages.add(main_fig)
    else:
        log.warning("BIBLIO.main_pipeline_figure.page missing/non-int")

    if not pages:
        log.warning("no figure pages identified — nothing to rasterize")
        out_dir.mkdir(parents=True, exist_ok=True)
        return 0

    log.info("rasterizing %d pages: %s", len(pages), sorted(pages))
    written = rasterize(pdf_path, sorted(pages), out_dir)
    log.info("wrote %d new PNGs to %s", written, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
