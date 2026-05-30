"""A PDF with inline images MuPDF rejects ("BI operator can only show
ImageMask, Gray, RGB, or CMYK images") made `out.save(clean=True)` throw
and killed an otherwise-successful translation (no output at all). The
real reported failure: job 8f020b7012f0, IM-CMDet UAV visible-infrared
paper. _safe_save must degrade to a non-clean (valid) save instead."""

from __future__ import annotations

import pytest

from phyra_dualtrans.pipeline.build_dual import _safe_save

_FZ_BI = "code=4: BI operator can only show ImageMask, Gray, RGB, or CMYK"


class FakeDoc:
    def __init__(self, fail_when):
        self.fail_when = fail_when
        self.calls: list[dict] = []

    def save(self, path, **kw):
        self.calls.append(kw)
        if self.fail_when(kw):
            raise RuntimeError(_FZ_BI)
        with open(path, "wb") as fh:
            fh.write(b"%PDF-1.4\n%%EOF\n")


def test_clean_save_failure_falls_back_to_noclean(tmp_path):
    out = tmp_path / "dual.pdf"
    # fails whenever clean=True (the real MuPDF sanitizer path)
    doc = FakeDoc(lambda kw: kw.get("clean") is True)
    _safe_save(doc, out, label="dual")            # must NOT raise

    assert out.exists() and out.read_bytes().startswith(b"%PDF")
    assert doc.calls[0].get("clean") is True       # tried the optimal first
    assert doc.calls[-1].get("clean") is not True  # then a non-clean save
    assert len(doc.calls) >= 2


def test_normal_path_uses_first_strategy_only(tmp_path):
    out = tmp_path / "ok.pdf"
    doc = FakeDoc(lambda kw: False)                # nothing fails
    _safe_save(doc, out, label="dual")
    assert out.exists()
    assert len(doc.calls) == 1                      # no needless re-saves
    assert doc.calls[0]["clean"] is True


def test_all_strategies_failing_raises_with_label(tmp_path):
    doc = FakeDoc(lambda kw: True)                  # every attempt fails
    with pytest.raises(RuntimeError, match="mono: every save strategy"):
        _safe_save(doc, tmp_path / "x.pdf", label="mono")
    assert len(doc.calls) == 4                       # tried all fallbacks


def test_only_objstms_problem_still_recovers(tmp_path):
    out = tmp_path / "d.pdf"
    # e.g. a build where clean is fine but use_objstms path errors
    doc = FakeDoc(lambda kw: kw.get("use_objstms") is True)
    _safe_save(doc, out, label="dual")
    assert out.exists()
    assert doc.calls[-1].get("use_objstms") is not True
