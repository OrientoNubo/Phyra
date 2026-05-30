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
import os
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build-dual")

# Papers with pathological inline images (e.g. IM-CMDet: ~1.5–4k tiled
# images/page) make MuPDF emit a flood of "syntax error" warnings; its
# Python error callback then crashes on surrogate bytes in those
# messages (UnicodeEncodeError). The renderer itself RECOVERS — only the
# logging callback is buggy — so silence it. We already degrade saves
# gracefully and report failures ourselves.
try:  # pragma: no cover - depends on the PyMuPDF build
    fitz.TOOLS.mupdf_display_errors(False)
except Exception:  # noqa: BLE001
    pass

# Stamp the ORIGINAL page's image regions over the translated side.
# BabelDOC rebuilds the translated page from its IL and re-emits inline
# images via BI/ID/EI; a malformed source inline image then corrupts the
# figure ONLY on the translated (right) side (the left/original side is a
# verbatim show_pdf_page copy and stays fine). The user prefers the
# figure untouched over broken, so we paint the pixel-identical original
# image on top — body text + captions (outside the image bbox) stay
# translated. Disable with PHYRA_DUALTRANS_NO_FIGURE_OVERLAY=1.
_NO_FIG_OVERLAY = os.environ.get(
    "PHYRA_DUALTRANS_NO_FIGURE_OVERLAY", "0"
) == "1"
# DPI for the rasterized snapshot used to repair INLINE-image figures.
# 200 is crisp on screen; the user explicitly prefers a faithful (if
# raster) figure over a corrupted one.
_FIG_RASTER_DPI = int(os.environ.get("PHYRA_DUALTRANS_FIGURE_DPI", "200"))

# A caption line in the ENGLISH original (Figure 6: / Fig. 3 / Table 1 /
# Table I / Algorithm 2). Used to keep the figure raster off the caption
# so it stays translated.
_CAPTION_RX = re.compile(
    r"^(figure|fig\.?|table|tab\.?|algorithm|scheme)\s*"
    r"(?:\d|[ivxlc]{1,6}\b)",
    re.IGNORECASE,
)


# A figure region must never be DEFINED by (or bridged through) a long
# thin sliver — a rule, an arrow shaft, a column divider, a bracket. One
# such 16x524 vertical line on NetLLM p5 chained the top-left diagram all
# the way down the column, so the whole left text column clustered into a
# "figure" and the ORIGINAL English raster got stamped over the translated
# Chinese (the reported "English paragraph with Chinese underneath" bug).
# A real figure body is never this elongated.
_SLIVER_ASPECT = 12.0   # long side : short side
_SLIVER_SHORT_MAX = 25.0  # px; below this a high-aspect rect is a line
# Never rasterize a region that is mostly TEXT — even if clustering still
# produces one, this is the backstop that keeps original text off the
# translated prose. Real figures here cover 27-47% text; a prose column 82%.
_MAX_TEXT_COVERAGE = 0.70
# Only collapse the whole page into ONE region (the "mosaic" path) when
# there are this many rects — a genuine tiled-image figure (IM-CMDet:
# 1.5–4k tiles). The old threshold (200) misfired on ordinary pages whose
# vector diagrams decompose into many small pieces: NetLLM p7 has 594
# image+drawing rects across a 2-column layout, so the union spanned the
# right-hand prose (28.6% of the page, only 35% text → it slipped past the
# text backstop) and the original English column got stamped over the
# translated Chinese. Below this count we always cluster into per-figure
# regions (594 rects cluster in ~0.01s; even a real contiguous mosaic of
# 4k tiles clusters to one region in ~0.03s — the union is purely a guard
# against the pathological many-scattered-rects case).
_MOSAIC_MIN_RECTS = 1200


def _is_bridging_sliver(b: fitz.Rect) -> bool:
    """A long thin line/arrow/divider — must not seed or bridge a figure
    cluster (a real figure body is never this elongated)."""
    lo, hi = min(b.width, b.height), max(b.width, b.height)
    return lo <= _SLIVER_SHORT_MAX and hi >= _SLIVER_ASPECT * max(lo, 1.0)


def _text_coverage(src_page: fitz.Page, region: fitz.Rect) -> float:
    """Fraction of `region` covered by the page's text blocks. High → the
    region is a body-text column, not a figure → must not be rasterized."""
    area = region.get_area()
    if area <= 0:
        return 0.0
    covered = 0.0
    try:
        for b in src_page.get_text("blocks"):
            r = fitz.Rect(b[:4]) & region
            if not r.is_empty:
                covered += r.get_area()
    except Exception:  # noqa: BLE001 — guard must never break a job
        return 0.0
    return min(covered / area, 1.0)


def _cluster_rects(rects: list[fitz.Rect], gap: float = 6.0
                   ) -> list[fitz.Rect]:
    """Merge rects that touch / overlap (within `gap`) into figure
    clusters, so a page with two separate figures (text between them)
    yields two regions — we never rasterize over the prose in the gap."""
    boxes = [fitz.Rect(r) for r in rects if not fitz.Rect(r).is_empty]
    merged = True
    while merged:
        merged = False
        out: list[fitz.Rect] = []
        for b in boxes:
            placed = False
            for i, o in enumerate(out):
                e = fitz.Rect(o) + (-gap, -gap, gap, gap)
                if e.intersects(b):
                    # NB: PyMuPDF Rect has no __ior__ — must reassign
                    # the list element, not `o |= b` (which would just
                    # rebind the local and silently drop `b`).
                    u = fitz.Rect(o)
                    u.include_rect(b)
                    out[i] = u
                    placed = True
                    merged = True
                    break
            if not placed:
                out.append(fitz.Rect(b))
        boxes = out
    return boxes


def _overlay_original_figures(
    dst_page: fitz.Page,
    src_doc: fitz.Document,
    src_pageno: int,
    *,
    x_offset: float,
) -> int:
    """Repair the translated side's figures from the ORIGINAL page.

    BabelDOC rebuilds the translated page from its IL and re-serializes
    images; malformed inline images then corrupt the figure ONLY on the
    translated side (MuPDF: "BI operator can only show ..."), and
    re-placing the original via show_pdf_page degrades them again at
    save time. The robust, type-agnostic fix the user asked for ("rather
    the figure untouched than broken"): cluster the original page's
    image regions, RASTERIZE each cluster with MuPDF's tolerant renderer
    (the same one that draws the correct original/left side) and stamp it
    as one flat image — a flat image cannot be re-encode-corrupted.
    Captions/body sit OUTSIDE image bboxes and stay translated.

    Skipped: hairline/rule images, and any cluster spanning most of the
    page (never paste a raster snapshot over a page of translated prose).
    Best-effort: any failure is logged and skipped. Returns # stamped."""
    if _NO_FIG_OVERLAY:
        return 0
    try:
        src_page = src_doc[src_pageno]
        sw, sh = src_page.rect.width, src_page.rect.height
        if sw <= 0 or sh <= 0:
            return 0
        dst_w = dst_page.rect.width - x_offset
        sx, sy = dst_w / sw, dst_page.rect.height / sh
        page_area = sw * sh
        rects = []
        for info in src_page.get_image_info():
            b = fitz.Rect(info["bbox"]) & src_page.rect
            if b.is_empty or b.width < 2 or b.height < 2:
                continue            # only drop degenerate slivers
            if _is_bridging_sliver(b):
                continue            # a thin rule/bar — never a figure body
            rects.append(b)
        # Figures are often VECTOR art (IM-CMDet: a 385-path diagram with
        # NO images) — BabelDOC's IL rebuild guts those too. Include
        # drawing rects so vector figures/tables are repaired as well.
        # Hairlines/rules (h or w < 3) are dropped so they don't bridge
        # a figure cluster into adjacent prose; longer thin slivers
        # (arrows / dividers / brackets) are dropped by _is_bridging_sliver
        # for the same reason.
        for g in src_page.get_drawings():
            b = fitz.Rect(g["rect"]) & src_page.rect
            if b.is_empty or b.width < 3 or b.height < 3:
                continue
            if _is_bridging_sliver(b):
                continue
            rects.append(b)
    except Exception as e:  # noqa: BLE001
        log.debug("figure overlay skipped on src p%d: %s",
                  src_pageno + 1, e)
        return 0
    if not rects:
        return 0

    # A page packed with THOUSANDS of image tiles IS one mosaic figure
    # (IM-CMDet: 1.5–4k tiles). Treat it as a single region — also avoids
    # O(n^2) clustering on pathological inputs. Otherwise cluster into
    # per-figure groups so a normal page (figures/diagrams + prose between
    # or beside them) keeps the prose translated. See _MOSAIC_MIN_RECTS.
    if len(rects) > _MOSAIC_MIN_RECTS:
        u = fitz.Rect(rects[0])
        for r in rects[1:]:
            u |= r
        regions = [u]
    else:
        regions = _cluster_rects(rects)

    # Caption blocks (read from the ENGLISH original): the user wants
    # CAPTIONS translated, so a figure region must not be rasterized over
    # its caption. Trim each region vertically to exclude any caption
    # text block it overlaps (caption sits just above tables / below
    # figures). Figure-internal labels are NOT captions (no "Figure N").
    try:
        caps = [
            fitz.Rect(b[:4]) & src_page.rect
            for b in src_page.get_text("blocks")
            if _CAPTION_RX.match((b[4] or "").strip())
        ]
    except Exception:  # noqa: BLE001
        caps = []

    def _trim_caption(r: fitz.Rect) -> fitz.Rect:
        r = fitz.Rect(r)
        midy = (r.y0 + r.y1) / 2
        for c in caps:
            if c.is_empty or not r.intersects(c):
                continue
            if c.y0 >= midy:                 # caption below the figure
                r.y1 = min(r.y1, c.y0 - 2)
            elif c.y1 <= midy:               # caption above (tables)
                r.y0 = max(r.y0, c.y1 + 2)
        return r

    mat = fitz.Matrix(_FIG_RASTER_DPI / 72, _FIG_RASTER_DPI / 72)
    n = 0
    for region in regions:
        if region.get_area() < 0.012 * page_area:
            continue                # too small to be a figure → skip

        # never blanket a near-full page (would hide translated prose)
        if region.get_area() > 0.85 * page_area:
            log.debug("p%d: skip page-spanning image cluster",
                      src_pageno + 1)
            continue
        region = _trim_caption(region)
        if (region.is_empty or region.height < 8 or region.width < 8
                or region.get_area() < 0.012 * page_area):
            continue                # collapsed after caption trim → skip
        # Backstop: never paint the original (English) raster over a region
        # that is mostly TEXT on the translated side — that would bury the
        # translation. A real figure is sparse text; a prose column is not.
        if _text_coverage(src_page, region) > _MAX_TEXT_COVERAGE:
            log.debug("p%d: skip text-heavy region (cov>%.0f%%) — not a "
                      "figure", src_pageno + 1, _MAX_TEXT_COVERAGE * 100)
            continue
        try:
            pix = src_page.get_pixmap(matrix=mat, clip=region,
                                      alpha=False)
            dest = fitz.Rect(x_offset + region.x0 * sx, region.y0 * sy,
                             x_offset + region.x1 * sx, region.y1 * sy)
            dst_page.insert_image(dest, pixmap=pix, overlay=True)
            n += 1
        except Exception as e:  # noqa: BLE001 — keep the rest of the page
            log.debug("figure raster overlay failed src p%d: %s",
                      src_pageno + 1, e)
    return n

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


def _safe_save(doc: fitz.Document, path: Path, *, label: str) -> None:
    """Save with progressively simpler options. `clean=True` invokes
    MuPDF's content-stream sanitizer, which raises on PDFs with inline
    images in colorspaces it rejects ("BI operator can only show ...").
    A single such page must NOT throw away an otherwise-good translated
    document — degrade to a non-clean (less optimized but valid) save."""
    attempts = [
        dict(garbage=4, deflate=True, deflate_fonts=True, clean=True,
             use_objstms=True),
        dict(garbage=4, deflate=True, deflate_fonts=True, clean=False,
             use_objstms=True),
        dict(garbage=3, deflate=True, clean=False),
        dict(),
    ]
    last: Exception | None = None
    for i, kw in enumerate(attempts):
        try:
            doc.save(str(path), **kw)
            if i:
                log.warning("%s: saved with reduced options (attempt "
                            "%d/%d) after: %s", label, i + 1,
                            len(attempts), last)
            return
        except Exception as e:  # noqa: BLE001 — try the next strategy
            last = e
            log.warning("%s: save attempt %d/%d failed: %s",
                        label, i + 1, len(attempts), e)
    raise RuntimeError(f"{label}: every save strategy failed: {last}")


def insert_placeholder_page(out: fitz.Document, src_page: fitz.Page,
                            lang_out: str,
                            font_path: str | None,
                            font_alias: str) -> None:
    """Insert a 2-up dual-layout page where left = original ref page,
    right = grey placeholder text."""
    src_w = src_page.rect.width
    src_h = src_page.rect.height
    page = out.new_page(width=src_w * 2, height=src_h)

    # Left: original ref page. Some PDFs have inline images MuPDF won't
    # render ("BI operator ..."); a bad ref page must not abort the job
    # — emit the placeholder without the original render.
    try:
        page.show_pdf_page(
            fitz.Rect(0, 0, src_w, src_h),
            src_page.parent, src_page.number,
        )
    except Exception as e:  # noqa: BLE001
        log.warning("ref page %d render failed (%s); placeholder only",
                    src_page.number + 1, e)
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
                try:
                    page.show_pdf_page(
                        fitz.Rect(0, 0, src_page.rect.width,
                                  src_page.rect.height),
                        src, pn - 1,
                    )
                except Exception as e:  # noqa: BLE001 — keep page count
                    log.warning("page %d render failed (%s); blank kept",
                                pn, e)
                continue
            out.insert_pdf(bd, from_page=bd_idx, to_page=bd_idx)
            np = out[out.page_count - 1]
            n = _overlay_original_figures(
                np, src, pn - 1, x_offset=np.rect.width / 2
            )
            if n:
                log.debug("p%d: overlaid %d original image(s) on the "
                          "translated side", pn, n)
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
    _safe_save(out, out_pdf, label="dual")
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
                # mono page == original size, no side offset
                _overlay_original_figures(
                    mono_page, src, pn - 1, x_offset=0.0
                )
                bd_idx += 1
        _safe_save(mono, also_mono, label="mono")
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
