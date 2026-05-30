import json

import fitz

from phyra_dualtrans.pipeline.build_dual import build
from phyra_dualtrans.pipeline.slice_pdf import slice_pdf

from .conftest import make_fake_babeldoc_dual


def test_dual_page_count_equals_original_no_refs(plain_pdf, tmp_path):
    meta_p = tmp_path / "meta.json"
    meta = slice_pdf(plain_pdf, None, tmp_path / "sliced.pdf", meta_p)
    bd = make_fake_babeldoc_dual(tmp_path / "bd.pdf", len(meta["kept_pages"]))

    out = tmp_path / "out.dual.pdf"
    build(
        original_pdf=plain_pdf, babeldoc_dual_pdf=bd,
        slice_meta_path=meta_p, out_pdf=out, lang_out="zh-TW",
    )
    assert fitz.open(out).page_count == fitz.open(plain_pdf).page_count == 3


def test_slice_passthrough_yields_full_side_by_side(ref_pdf, tmp_path):
    """Default pipeline: slice is pass-through → build emits a straight
    full-length side-by-side with NO placeholder. References stay
    VISIBLE in the original (il_filter keeps them untranslated) — this
    is the user's 「保持原樣」 requirement."""
    meta_p = tmp_path / "meta.json"
    meta = slice_pdf(ref_pdf, None, tmp_path / "sliced.pdf", meta_p)
    assert meta["ref_pages"] == [] and meta["kept_pages"] == [1, 2, 3, 4, 5]
    bd = make_fake_babeldoc_dual(tmp_path / "bd.pdf", 5)

    out = tmp_path / "out.dual.pdf"
    build(
        original_pdf=ref_pdf, babeldoc_dual_pdf=bd,
        slice_meta_path=meta_p, out_pdf=out, lang_out="zh-TW",
    )
    doc = fitz.open(out)
    assert doc.page_count == 5
    # fake BabelDOC stamps "trans <i>" on every translated page; with no
    # placeholder EVERY page must carry it.
    assert all("trans" in doc[p].get_text() for p in range(5))
    doc.close()


def test_build_dual_still_supports_ref_placeholder_meta(ref_pdf, tmp_path):
    """build_dual's placeholder path is still live code (legacy / direct
    meta with ref_pages): a ref page becomes a grey placeholder while the
    full original page count is preserved. Decoupled from slice_pdf
    (which no longer emits ref_pages)."""
    meta_p = tmp_path / "meta.json"
    meta_p.write_text(json.dumps({
        "schema_version": 1, "total_pages": 5,
        "ref_pages": [5], "kept_pages": [1, 2, 3, 4],
    }), encoding="utf-8")
    bd = make_fake_babeldoc_dual(tmp_path / "bd.pdf", 4)

    out = tmp_path / "out.dual.pdf"
    mono = tmp_path / "out.mono.pdf"
    build(
        original_pdf=ref_pdf, babeldoc_dual_pdf=bd,
        slice_meta_path=meta_p, out_pdf=out, lang_out="zh-TW",
        also_mono=mono,
    )
    assert fitz.open(out).page_count == 5   # 4 translated + 1 placeholder
    assert fitz.open(mono).page_count == 5


def test_is_bridging_sliver():
    from phyra_dualtrans.pipeline.build_dual import _is_bridging_sliver
    # the NetLLM p5 culprit: a 16.5 x 524 vertical line → sliver
    assert _is_bridging_sliver(fitz.Rect(184, 94, 200.5, 618.7)) is True
    # a thin horizontal rule / underline
    assert _is_bridging_sliver(fitz.Rect(60, 100, 540, 108)) is True
    # a real figure body is not a sliver
    assert _is_bridging_sliver(fitz.Rect(58, 67, 279, 170)) is False
    # a bar-chart region
    assert _is_bridging_sliver(fitz.Rect(331, 84, 543, 169)) is False
    # a square icon
    assert _is_bridging_sliver(fitz.Rect(66, 66, 84, 84)) is False


def test_text_coverage_skips_prose_column(tmp_path):
    """A region full of body text must read as high-coverage so the
    overlay backstop skips it (no English raster over translated prose)."""
    from phyra_dualtrans.pipeline.build_dual import (
        _MAX_TEXT_COVERAGE, _text_coverage,
    )
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    col = fitz.Rect(58, 80, 290, 620)
    rc = page.insert_textbox(
        col, ("The quick brown fox jumps over the lazy dog. " * 24),
        fontsize=10, fontname="helv", lineheight=1.0,
    )
    assert rc >= 0                                          # text was inserted
    # the region a clusterer would form around real prose is the text's
    # own bbox — overwhelmingly text → coverage well above the threshold.
    blocks = page.get_text("blocks")
    assert blocks
    region = fitz.Rect(blocks[0][:4])
    for b in blocks[1:]:
        region |= fitz.Rect(b[:4])
    assert _text_coverage(page, region) > _MAX_TEXT_COVERAGE   # prose → skip
    # an empty figure area has ~no text
    empty = fitz.Rect(330, 640, 540, 760)
    assert _text_coverage(page, empty) <= _MAX_TEXT_COVERAGE
    doc.close()
