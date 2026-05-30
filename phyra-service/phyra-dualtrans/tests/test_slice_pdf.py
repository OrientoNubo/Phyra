"""slice_pdf is now a pass-through: references are handled at paragraph
granularity by il_filter (kept as the original, not page-sliced into
grey placeholders). These tests pin the pass-through contract."""

import json

import fitz

from phyra_dualtrans.pipeline.slice_pdf import slice_pdf

from .conftest import _PURE_REFS, _REF_HEADER_PAGE


def test_plain_pdf_passes_through(plain_pdf, tmp_path):
    out = tmp_path / "sliced.pdf"
    meta_p = tmp_path / "meta.json"
    meta = slice_pdf(plain_pdf, None, out, meta_p)

    n = fitz.open(plain_pdf).page_count
    assert meta["total_pages"] == n == 3
    assert meta["ref_pages"] == []
    assert meta["kept_pages"] == [1, 2, 3]
    assert fitz.open(out).page_count == 3
    assert json.loads(meta_p.read_text())["ref_pages"] == []


def test_refs_are_NOT_page_sliced(ref_pdf, tmp_path):
    """The old heuristic dropped pure-ref pages; now NOTHING is sliced —
    every page is kept and references stay visible (il_filter keeps them
    as the original text, just untranslated)."""
    out = tmp_path / "sliced.pdf"
    meta = slice_pdf(ref_pdf, None, out, tmp_path / "meta.json")

    assert meta["total_pages"] == 5
    assert meta["ref_pages"] == []                 # never page-slice refs
    assert meta["kept_pages"] == [1, 2, 3, 4, 5]   # all pages kept
    assert meta["ref_start_page"] is None
    assert fitz.open(out).page_count == 5          # full PDF passed through


def test_passthrough_independent_of_content(tmp_path):
    """Mixed body+refs / pure-ref pages, supplementary — all kept; the
    pass-through never inspects content (no fragile page heuristic)."""
    p = tmp_path / "mixed.pdf"
    d = fitz.open()
    for txt in ("Body one.", _REF_HEADER_PAGE, _PURE_REFS,
                "Supplementary Material\nMore real content here.",
                "Appendix results."):
        pg = d.new_page(width=480, height=700)
        pg.insert_text((60, 80), txt, fontsize=12)
    d.save(str(p)); d.close()

    meta = slice_pdf(p, None, tmp_path / "s.pdf", tmp_path / "m.json")
    assert meta["ref_pages"] == []
    assert meta["kept_pages"] == [1, 2, 3, 4, 5]
    assert fitz.open(tmp_path / "s.pdf").page_count == 5
