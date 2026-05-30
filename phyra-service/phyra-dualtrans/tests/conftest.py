"""Shared fixtures: temp config/jobs env + tiny synthetic PDFs."""

from __future__ import annotations

import os
from pathlib import Path

import fitz  # PyMuPDF
import pytest


@pytest.fixture(autouse=True)
def _isolated_env(tmp_path_factory, monkeypatch):
    """Point config + jobs dir at a throwaway location so tests never
    touch the real ~/.config / ~/.local."""
    base = tmp_path_factory.mktemp("pdt")
    monkeypatch.setenv("PHYRA_DUALTRANS_CONFIG", str(base / "config.json"))
    monkeypatch.setenv("PHYRA_DUALTRANS_JOBS_DIR", str(base / "jobs"))
    # never spawn a real Ollama from the app lifespan during tests
    monkeypatch.setenv("PHYRA_DUALTRANS_MANAGE_OLLAMA", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from phyra_dualtrans.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _make_pdf(path: Path, page_texts: list[str]) -> Path:
    doc = fitz.open()
    for txt in page_texts:
        page = doc.new_page(width=400, height=600)
        page.insert_text((60, 80), txt, fontsize=14)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture
def plain_pdf(tmp_path) -> Path:
    """3 pages, no References section."""
    return _make_pdf(
        tmp_path / "plain.pdf",
        ["Introduction body", "Method body", "Results body"],
    )


_PURE_REFS = (
    "[1] A. Author. A great title. In Proc CVPR, 2020.\n"
    "[2] B. Writer. Another paper. NeurIPS, 2021.\n"
    "[3] C. Coder. Yet another work. arXiv:2101.00001, 2021.\n"
    "[4] D. Dev. Deep things here. ICLR, 2022.\n"
    "[5] E. Eng. Even more references. CVPR, 2023.\n"
    "[6] F. Fox. The final entry. ICCV, 2019.\n"
    "[7] G. Gray. Trailing one. ECCV, 2018."
)
# A realistic References-HEADER page: body prose, then the heading, then
# the first couple of entries — i.e. NOT pure → must stay translated.
_REF_HEADER_PAGE = (
    "We conclude with a discussion of limitations and directions for\n"
    "future work in real-world robotic perception and mapping.\n"
    "Acknowledgements. We thank everyone involved in this project.\n"
    "References\n"
    "[1] A. Author. A great title. In Proc CVPR, 2020."
)


@pytest.fixture
def ref_pdf(tmp_path) -> Path:
    """5 pages: 1-3 body, page 4 = the 'References' HEADER page (body
    prose + heading + first entry → NOT pure → translated), page 5 = a
    pure-bibliography continuation page (skipped)."""
    return _make_pdf(
        tmp_path / "withref.pdf",
        ["Introduction body text here, several words.",
         "Method body text describing the approach in detail.",
         "Results body text with numbers and discussion.",
         _REF_HEADER_PAGE, _PURE_REFS],
    )


def make_fake_babeldoc_dual(path: Path, n_pages: int) -> Path:
    """Side-by-side dual: each page is double-width (left|right)."""
    doc = fitz.open()
    for i in range(n_pages):
        page = doc.new_page(width=800, height=600)
        page.insert_text((40, 80), f"orig {i}", fontsize=12)
        page.insert_text((440, 80), f"trans {i}", fontsize=12)
    doc.save(str(path))
    doc.close()
    return path
