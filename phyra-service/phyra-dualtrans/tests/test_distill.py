"""Context-distillation pre-pass: extraction caps, graceful failure,
and guide injection into the translator system prompt + cache id."""

from __future__ import annotations

import fitz
import pytest

from phyra_dualtrans.pipeline.babeldoc_translator import BabelDocTranslator
from phyra_dualtrans.pipeline.distill import (
    distill_context,
    distill_system_prompt,
    distill_user_prompt,
    extract_pdf_text,
)

_PARA = ("We present a feed-forward transformer for 3D scene "
         "reconstruction with camera parameters, depth maps and point "
         "tracks, evaluated against strong baselines. ") * 6  # >200 chars


@pytest.fixture
def rich_pdf(tmp_path):
    p = tmp_path / "rich.pdf"
    d = fitz.open()
    for _ in range(3):
        pg = d.new_page(width=595, height=842)
        pg.insert_textbox(fitz.Rect(40, 40, 555, 800), _PARA, fontsize=11)
    d.save(str(p)); d.close()
    return p


class FakeLLM:
    name = "fake-1"

    def __init__(self, reply="DOMAIN: x\nGLOSSARY: a => 甲\nKEEP-IN-ENGLISH: VGGT\nSTYLE: TW"):
        self.reply = reply
        self.calls = 0

    def complete(self, system, prompt):
        self.calls += 1
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def test_extract_caps_length(rich_pdf):
    full = extract_pdf_text(rich_pdf, max_chars=10_000)
    assert full
    capped = extract_pdf_text(rich_pdf, max_chars=5)
    assert len(capped) <= 5


def test_prompts_mention_lang_and_sections():
    sysp = distill_system_prompt("zh-TW")
    usr = distill_user_prompt("some paper text", "zh-TW")
    assert "zh-TW" in sysp and "zh-TW" in usr
    for label in ("DOMAIN:", "GLOSSARY:", "KEEP-IN-ENGLISH:", "STYLE:"):
        assert label in usr


def test_distill_returns_guide_on_success(rich_pdf):
    llm = FakeLLM()
    g = distill_context(llm, rich_pdf, "zh-TW", max_chars=10_000)
    assert g and "GLOSSARY" in g and llm.calls == 1


def test_distill_none_when_text_too_short(tmp_path):
    import fitz
    p = tmp_path / "tiny.pdf"
    d = fitz.open(); d.new_page(width=200, height=200)
    d.save(str(p)); d.close()
    assert distill_context(FakeLLM(), p, "zh-TW") is None


def test_distill_never_raises_on_llm_failure(rich_pdf):
    llm = FakeLLM(reply=RuntimeError("model down"))
    assert distill_context(llm, rich_pdf, "zh-TW", max_chars=10_000) is None


def test_guide_injected_into_system_and_cache_id():
    g = "GLOSSARY: tensor => 張量"
    t = BabelDocTranslator("en", "zh-TW", FakeLLM(), guide=g)
    assert "TRANSLATION GUIDE" in t._sys and "張量" in t._sys
    assert t.model.startswith("phyra-fake-1-g")        # guide hash folded in

    t0 = BabelDocTranslator("en", "zh-TW", FakeLLM())
    assert t0.model == "phyra-fake-1"                  # unchanged w/o guide
    assert "TRANSLATION GUIDE" not in t0._sys
