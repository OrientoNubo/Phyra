import pytest

from phyra_dualtrans.vendor.resolve_input import (
    build_stem,
    detect_arxiv_id,
    resolve,
    sanitize_title_for_stem,
)


def test_detect_arxiv():
    assert detect_arxiv_id("2503.06132") == "2503.06132"
    assert detect_arxiv_id("https://arxiv.org/abs/2402.15391") == "2402.15391"
    assert detect_arxiv_id("https://arxiv.org/pdf/2402.15391v3") == "2402.15391"
    assert detect_arxiv_id("/some/local/file.pdf") is None


def test_sanitize_and_stem():
    assert sanitize_title_for_stem("Genie: Generative Interactive Environments") \
        == "Genie_Generative_Interactive_Environments"
    assert build_stem("2402", None, "2402.15391") == "2402_15391"
    assert build_stem("1706", "Attention Is All You Need") \
        == "1706_Attention_Is_All_You_Need"


def test_resolve_local(plain_pdf, tmp_path):
    info = resolve(str(plain_pdf), override_out_dir=tmp_path)
    assert info["kind"] == "local"
    assert info["pdf_path"] == str(plain_pdf)
    assert info["stem"] == "plain"
    assert info["out_dir"] == str(tmp_path)


def test_resolve_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve(str(tmp_path / "nope.pdf"), override_out_dir=tmp_path)
