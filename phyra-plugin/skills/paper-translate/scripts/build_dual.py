"""
build_dual.py (v0.9.0) — assemble the final bilingual side-by-side PDF.

The translator runs BabelDOC on a sliced (refs-removed) PDF to save cost.
This script stitches the result back into a PDF with the SAME page count as
the original by:

  1. Opening BabelDOC's `<slug>.no_refs.no_watermark.<lang>.dual.pdf` (which
     has 2*N pages — left=original, right=translation, interleaved).
  2. Inserting placeholder ref pages from the original PDF where references
     were sliced off (so the dual layout still shows the original ref pages
     on the left, with a "[reference page — translation skipped]" block on
     the right side).

Output:
  - bilingual.<lang>.dual.pdf — final dual side-by-side, full page count
  - (optional) bilingual.<lang>.mono.pdf — translation-only PDF
    extracted from the dual (right-hand pages of non-ref content + grey
    placeholder for refs)

Usage:
  uv run --with pymupdf python build_dual.py \\
      <original.pdf> <babeldoc_dual.pdf> <slice_meta.json> <out_dual.pdf> \\
      [--lang-out zh-TW] [--also-mono <out_mono.pdf>]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build-dual")

PLACEHOLDER_TEXT = {
    "zh-TW": "（此頁為參考文獻，翻譯已略過）",
    "zh-HK": "（此頁為參考文獻，翻譯已略過）",
    "zh-CN": "（此页为参考文献，翻译已略过）",
    "ja":    "(参考文献ページ — 翻訳をスキップ)",
    "ko":    "(참고 문헌 페이지 — 번역 생략)",
    "en":    "[reference page — translation skipped]",
}

CJK_FONT_MAP = {
    "zh-TW": ("SourceHanSerifTW-Regular.ttf", "shs-tw"),
    "zh-HK": ("SourceHanSerifHK-Regular.ttf", "shs-hk"),
    "zh-CN": ("SourceHanSerifCN-Regular.ttf", "shs-cn"),
    "ja":    ("SourceHanSerifJP-Regular.ttf", "shs-jp"),
    "ko":    ("SourceHanSerifKR-Regular.ttf", "shs-kr"),
    "en":    None,  # ASCII placeholder uses default Helvetica
}


def _font_for(lang_out: str) -> tuple[str | None, str]:
    """Return (font_file_path, fontname_alias) for a CJK language. Falls
    back to default Helvetica when the SourceHan font is missing."""
    entry = CJK_FONT_MAP.get(lang_out)
    if not entry:
        return None, "helv"
    fname, alias = entry
    fpath = Path.home() / ".cache/babeldoc/fonts" / fname
    if not fpath.exists():
        log.warning("CJK font missing for %s at %s; falling back to helv "
                    "(placeholder will render as '?' glyphs)",
                    lang_out, fpath)
        return None, "helv"
    return str(fpath), alias


def insert_placeholder_page(out: fitz.Document, src_page: fitz.Page,
                            lang_out: str,
                            font_path: str | None,
                            font_alias: str) -> None:
    """Insert a 2-up dual-layout page where left = original ref page,
    right = grey placeholder text."""
    src_w = src_page.rect.width
    src_h = src_page.rect.height
    page = out.new_page(width=src_w * 2, height=src_h)

    # Left: original ref page
    page.show_pdf_page(
        fitz.Rect(0, 0, src_w, src_h),
        src_page.parent, src_page.number,
    )
    # Right: grey placeholder
    rect_r = fitz.Rect(src_w, 0, src_w * 2, src_h)
    page.draw_rect(rect_r, color=None, fill=(0.97, 0.97, 0.97), overlay=False)
    msg = PLACEHOLDER_TEXT.get(lang_out, PLACEHOLDER_TEXT["en"])
    if font_path:
        page.insert_font(fontname=font_alias, fontfile=font_path)
        fontname = font_alias
    else:
        fontname = "helv"
    page.insert_textbox(
        fitz.Rect(src_w + 24, src_h / 2 - 24, src_w * 2 - 24, src_h / 2 + 24),
        msg, fontsize=14, fontname=fontname,
        color=(0.5, 0.5, 0.5), align=1,
    )


def build(*, original_pdf: Path, babeldoc_dual_pdf: Path, slice_meta_path: Path,
          out_pdf: Path, lang_out: str,
          also_mono: Path | None = None) -> None:
    meta = json.loads(slice_meta_path.read_text(encoding="utf-8"))
    total_pages = int(meta["total_pages"])
    ref_pages = set(meta.get("ref_pages") or [])
    kept_pages = list(meta.get("kept_pages") or [])

    log.info("total_pages=%d kept=%d ref=%d",
             total_pages, len(kept_pages), len(ref_pages))

    src = fitz.open(original_pdf)
    bd = fitz.open(babeldoc_dual_pdf)
    out = fitz.open()
    font_path, font_alias = _font_for(lang_out)

    # BabelDOC dual.pdf is one page per source page (already side-by-side).
    if bd.page_count != len(kept_pages):
        log.warning(
            "babeldoc dual.pdf page_count=%d != kept_pages count=%d; "
            "alignment may drift", bd.page_count, len(kept_pages),
        )

    bd_idx = 0
    for pn in range(1, total_pages + 1):
        if pn in ref_pages:
            insert_placeholder_page(out, src[pn - 1], lang_out,
                                    font_path, font_alias)
        else:
            if bd_idx >= bd.page_count:
                log.warning("ran out of babeldoc pages at pn=%d; "
                            "appending original page only", pn)
                src_page = src[pn - 1]
                page = out.new_page(width=src_page.rect.width * 2,
                                    height=src_page.rect.height)
                page.show_pdf_page(
                    fitz.Rect(0, 0, src_page.rect.width, src_page.rect.height),
                    src, pn - 1,
                )
                continue
            out.insert_pdf(bd, from_page=bd_idx, to_page=bd_idx)
            bd_idx += 1

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    # PyMuPDF's standalone subset_fonts() pass dedupes the SourceHan font
    # across the 20-ish ref pages that each registered it independently;
    # without this the file bloats to ~10MB. The save kwargs alone do not
    # subset.
    try:
        out.subset_fonts()
    except Exception as e:  # PyMuPDF < 1.18 lacks this; not worth crashing
        log.debug("subset_fonts() unavailable: %s", e)
    out.save(str(out_pdf), garbage=4, deflate=True, deflate_fonts=True,
             clean=True, use_objstms=True)
    log.info("wrote %s (%d pages, %.1f MB)",
             out_pdf, out.page_count, out_pdf.stat().st_size / 1e6)

    if also_mono:
        # Crop right halves of non-ref pages, render placeholder for refs.
        mono = fitz.open()
        bd_idx = 0
        for pn in range(1, total_pages + 1):
            if pn in ref_pages:
                src_page = src[pn - 1]
                mono_page = mono.new_page(width=src_page.rect.width,
                                          height=src_page.rect.height)
                mono_page.draw_rect(mono_page.rect, color=None,
                                    fill=(0.97, 0.97, 0.97), overlay=False)
                if font_path:
                    mono_page.insert_font(fontname=font_alias, fontfile=font_path)
                    fontname = font_alias
                else:
                    fontname = "helv"
                mono_page.insert_textbox(
                    fitz.Rect(24, src_page.rect.height / 2 - 24,
                              src_page.rect.width - 24, src_page.rect.height / 2 + 24),
                    PLACEHOLDER_TEXT.get(lang_out, PLACEHOLDER_TEXT["en"]),
                    fontsize=14, fontname=fontname,
                    color=(0.5, 0.5, 0.5), align=1,
                )
            else:
                if bd_idx >= bd.page_count:
                    bd_idx += 1
                    continue
                bp = bd[bd_idx]
                full_w = bp.rect.width
                half_w = full_w / 2
                # Right half = translation
                mono_page = mono.new_page(width=half_w,
                                          height=bp.rect.height)
                mono_page.show_pdf_page(
                    mono_page.rect, bd, bd_idx,
                    clip=fitz.Rect(half_w, 0, full_w, bp.rect.height),
                )
                bd_idx += 1
        mono.save(str(also_mono), garbage=4, deflate=True, clean=True)
        log.info("wrote %s (%d pages, %.1f MB)",
                 also_mono, mono.page_count, also_mono.stat().st_size / 1e6)
        mono.close()

    out.close()
    bd.close()
    src.close()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_pdf")
    p.add_argument("babeldoc_dual_pdf")
    p.add_argument("slice_meta_json")
    p.add_argument("out_dual_pdf")
    p.add_argument("--lang-out", default="zh-TW")
    p.add_argument("--also-mono", default=None,
                   help="If set, also write a translation-only PDF here")
    args = p.parse_args()

    build(
        original_pdf=Path(args.original_pdf).resolve(),
        babeldoc_dual_pdf=Path(args.babeldoc_dual_pdf).resolve(),
        slice_meta_path=Path(args.slice_meta_json).resolve(),
        out_pdf=Path(args.out_dual_pdf).resolve(),
        lang_out=args.lang_out,
        also_mono=(Path(args.also_mono).resolve() if args.also_mono else None),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
