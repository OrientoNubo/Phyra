"""build_dual figure overlay: the translated side's figures are repaired
from the ORIGINAL page (rasterized) so BabelDOC's IL-rebuild can't break
them, while body text / captions (outside figure clusters) stay
translated. Verified end-to-end on IM-CMDet (vector diagram) and
CubeDiff (raster panoramas); these are the fast unit guards."""

from __future__ import annotations

import fitz

from phyra_dualtrans.pipeline.build_dual import (
    _cluster_rects,
    _overlay_original_figures,
)


def test_cluster_rects_merges_touching_splits_distant():
    a = fitz.Rect(10, 10, 50, 50)
    b = fitz.Rect(52, 12, 90, 48)          # ~touching a (within gap)
    far = fitz.Rect(400, 400, 480, 480)    # separate figure
    out = _cluster_rects([a, b, far])
    assert len(out) == 2
    merged = next(r for r in out if r.x0 <= 10)
    assert merged.x1 >= 90 and merged.y1 >= 48      # a∪b merged
    assert any(abs(r.x0 - 400) < 1 for r in out)    # far kept separate


def _twoup_dst(w, h):
    d = fitz.open()
    p = d.new_page(width=w * 2, height=h)  # side-by-side dst page
    return d, p


def test_overlay_stamps_vector_figure_region():
    # original page: a big vector rectangle (a "figure") top-left,
    # prose lower down.
    src = fitz.open()
    sp = src.new_page(width=300, height=400)
    sp.draw_rect(fitz.Rect(30, 30, 270, 200), color=(0, 0, 0),
                 fill=(0.2, 0.4, 0.8))
    sp.insert_text((30, 320), "body text that stays translated")

    dst_doc, dp = _twoup_dst(300, 400)
    before = len(dp.get_images())
    n = _overlay_original_figures(dp, src, 0, x_offset=300.0)
    assert n >= 1                                  # a figure was overlaid
    assert len(dp.get_images()) > before           # raster stamped
    # stamped on the RIGHT half only
    info = dp.get_image_info()
    assert info and all(fitz.Rect(i["bbox"]).x0 >= 290 for i in info)
    src.close(); dst_doc.close()


def test_overlay_noop_on_text_only_page():
    src = fitz.open()
    sp = src.new_page(width=300, height=400)
    sp.insert_text((40, 60), "Only prose here. No figures at all.")
    dst_doc, dp = _twoup_dst(300, 400)
    assert _overlay_original_figures(dp, src, 0, x_offset=300.0) == 0
    assert len(dp.get_images()) == 0
    src.close(); dst_doc.close()


def test_overlay_skips_page_spanning_cluster():
    """A near-full-page drawing must NOT be rasterized over (would hide
    translated prose)."""
    src = fitz.open()
    sp = src.new_page(width=300, height=400)
    sp.draw_rect(fitz.Rect(2, 2, 298, 398))        # ~whole page
    dst_doc, dp = _twoup_dst(300, 400)
    assert _overlay_original_figures(dp, src, 0, x_offset=300.0) == 0
    src.close(); dst_doc.close()


def test_overlay_does_not_cover_caption():
    """The figure raster must stop ABOVE the caption so the (translated)
    caption stays visible — the user wants captions translated."""
    src = fitz.open()
    sp = src.new_page(width=300, height=400)
    sp.draw_rect(fitz.Rect(30, 30, 270, 220), fill=(0.2, 0.4, 0.8))
    sp.insert_text((40, 245), "Figure 1: a caption that must be translated")
    dst_doc, dp = _twoup_dst(300, 400)
    n = _overlay_original_figures(dp, src, 0, x_offset=300.0)
    assert n == 1
    stamped = fitz.Rect(dp.get_image_info()[0]["bbox"])
    # caption baseline ≈ y=245; stamped figure must end above it
    assert stamped.y1 <= 244, stamped
    src.close(); dst_doc.close()


def test_many_small_rects_still_cluster_not_one_union():
    """NetLLM p7 regression: a normal 2-column page whose vector diagrams
    decompose into HUNDREDS of small rects (here >200, the OLD mosaic
    threshold) must still cluster into per-figure regions — NOT collapse
    into one page-spanning union that stamps the original text column over
    the translated prose. Two separated figure blocks with a prose band
    between them ⇒ two stamps, and neither covers the prose."""
    src = fitz.open()
    sp = src.new_page(width=600, height=400)
    # figure A (top) and figure B (bottom), each a dense block of small
    # rects — together ~360 rects, above the old 200 cutoff, below 1200.
    for x in range(20, 280, 12):
        for y in range(20, 150, 12):
            sp.draw_rect(fitz.Rect(x, y, x + 8, y + 8), fill=(0.2, 0.4, 0.8))
        for y in range(260, 380, 12):
            sp.draw_rect(fitz.Rect(x, y, x + 8, y + 8), fill=(0.8, 0.3, 0.2))
    # prose band BETWEEN the two figures — must stay translated (untouched)
    prose = fitz.Rect(20, 175, 280, 245)
    sp.insert_textbox(prose, "body text that must stay translated " * 6,
                      fontsize=9, lineheight=1.0)

    dst_doc, dp = _twoup_dst(600, 400)
    n = _overlay_original_figures(dp, src, 0, x_offset=600.0)
    assert n == 2, f"expected 2 per-figure stamps, got {n} (mosaic union?)"
    # no stamp may cover the prose band (mapped onto the right half)
    pr = fitz.Rect(600 + prose.x0, prose.y0, 600 + prose.x1, prose.y1)
    for info in dp.get_image_info():
        ov = fitz.Rect(info["bbox"]) & pr
        assert ov.get_area() < 0.30 * pr.get_area(), "stamp covers prose"
    src.close(); dst_doc.close()


def test_overlay_env_kill_switch(monkeypatch):
    import phyra_dualtrans.pipeline.build_dual as bd
    monkeypatch.setattr(bd, "_NO_FIG_OVERLAY", True)
    src = fitz.open()
    sp = src.new_page(width=300, height=400)
    sp.draw_rect(fitz.Rect(30, 30, 270, 200), fill=(0, 0, 0))
    dst_doc, dp = _twoup_dst(300, 400)
    assert bd._overlay_original_figures(dp, src, 0, x_offset=300.0) == 0
    src.close(); dst_doc.close()
