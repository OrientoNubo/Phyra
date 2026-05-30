import shutil

import pytest

from phyra_dualtrans.pipeline.build_dual import build
from phyra_dualtrans.pipeline.compress import compress_pdf
from phyra_dualtrans.pipeline.slice_pdf import slice_pdf

from .conftest import make_fake_babeldoc_dual


def _make_dual(plain_pdf, tmp_path):
    meta_p = tmp_path / "meta.json"
    meta = slice_pdf(plain_pdf, None, tmp_path / "s.pdf", meta_p)
    bd = make_fake_babeldoc_dual(tmp_path / "bd.pdf", len(meta["kept_pages"]))
    out = tmp_path / "out.dual.pdf"
    build(original_pdf=plain_pdf, babeldoc_dual_pdf=bd,
          slice_meta_path=meta_p, out_pdf=out, lang_out="zh-TW")
    return out


def test_off_is_byte_identical(plain_pdf, tmp_path):
    pdf = _make_dual(plain_pdf, tmp_path)
    before = pdf.read_bytes()
    stats = compress_pdf(pdf, "off")
    assert stats["applied"] is False
    assert pdf.read_bytes() == before


def test_lossless_is_noop(plain_pdf, tmp_path):
    pdf = _make_dual(plain_pdf, tmp_path)
    before = pdf.read_bytes()
    stats = compress_pdf(pdf, "lossless")
    assert stats["applied"] is False
    assert "Ghostscript" in stats["note"]
    assert pdf.read_bytes() == before


@pytest.mark.skipif(shutil.which("gs") is None, reason="Ghostscript absent")
def test_lossy_runs_ghostscript(plain_pdf, tmp_path):
    pdf = _make_dual(plain_pdf, tmp_path)
    stats = compress_pdf(pdf, "lossy", dpi=72, preset="screen")
    # gs ran; either it shrank (applied) or kept original (note) — never raises
    assert stats["mode"] == "lossy"
    assert "applied" in stats
