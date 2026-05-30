"""phyra-dualtrans backends return PLAIN translated text. BabelDOC's
`ILTranslatorLLMOnly` engine instead needs a JSON-batch I/O contract
(`request_json_mode`, json.loads of `[{"id","output"}]`). Advertising
do_llm_translate made BabelDOC pick that engine, every batch failed
json.loads, and ~17% of paragraphs fell back untranslated (the reported
"very bad" IM-CMDet output). So do_llm_translate must raise
NotImplementedError → BabelDOC uses the simple per-paragraph
`ILTranslator` path → our do_translate() (the proven-good path).
"""

from __future__ import annotations

import pytest

from phyra_dualtrans.backends.base import HardCallError, RateLimitSignal
from phyra_dualtrans.pipeline.babeldoc_translator import (
    BabelDocTranslator,
    translation_effectively_failed,
)


class CapLLM:
    name = "cap"

    def __init__(self, reply="譯文", exc=None):
        self.reply, self.exc = reply, exc
        self.calls: list[tuple[str, str]] = []

    def complete(self, system, prompt):
        self.calls.append((system, prompt))
        if self.exc:
            raise self.exc
        return self.reply


def _t(llm=None, **kw):
    return BabelDocTranslator("en", "zh-TW", llm or CapLLM(), **kw)


def test_do_translate_wraps_raw_segment():
    llm = CapLLM()
    out = _t(llm).do_translate("hello world")
    assert out == "譯文"
    sys, user = llm.calls[0]
    assert sys == _t(llm)._sys and sys                 # our sci sys prompt
    assert "Translate to zh-TW" in user and "INPUT:\nhello world" in user


def test_do_llm_translate_probe_raises_notimplemented():
    """BabelDOC probes do_llm_translate(None); NotImplementedError makes
    translator_supports_llm() / support_llm_translate False → the simple
    ILTranslator path (not the JSON-batch ILTranslatorLLMOnly)."""
    with pytest.raises(NotImplementedError):
        _t().do_llm_translate(None)
    with pytest.raises(NotImplementedError):
        _t().do_llm_translate("any text")


def test_plain_fallback_is_source_text():
    t = _t(CapLLM(exc=HardCallError("boom")), wait_seconds=0, max_attempts=1)
    assert t.do_translate("para text") == "para text"      # source fallback


def test_rate_limit_exhaustion_falls_back_to_source():
    t = _t(CapLLM(exc=RateLimitSignal("429")), wait_seconds=0,
           max_attempts=2)
    assert t.do_translate("keep me") == "keep me"


def test_stats_count_calls_and_fallbacks():
    ok = _t(CapLLM())
    ok.do_translate("a")
    assert ok.stats == (1, 0)                               # 1 call, 0 fail

    bad = _t(CapLLM(exc=HardCallError("down")), wait_seconds=0,
             max_attempts=1)
    for _ in range(6):
        bad.do_translate("x")
    assert bad.stats == (6, 6)                              # all fell back


def test_translation_effectively_failed_thresholds():
    # the reported bug: wrong Base URL → every segment fell back
    assert translation_effectively_failed(30, 30) is True
    assert translation_effectively_failed(100, 96) is True   # ≥95%
    # healthy / mixed translations must NOT be flagged
    assert translation_effectively_failed(100, 4) is False
    assert translation_effectively_failed(179, 30) is False  # IM-CMDet-ish
    # tiny docs: don't wrongly fail a 1-formula-paragraph file
    assert translation_effectively_failed(3, 3) is False
    assert translation_effectively_failed(0, 0) is False


def test_ignore_cache_prevents_fallback_poisoning():
    """The 'all-English' bug: BabelDOC's BaseTranslator persistently
    caches WHATEVER do_translate() returns — including our source-text
    fallback on a failed call. One failed run then poisons the cache so
    every later run returns the English source without ever calling the
    backend. The runner now constructs the translator with
    ignore_cache=True; verify a failed (fallback) result is NOT served
    from cache — the backend is retried on the very next call."""
    llm = CapLLM(exc=HardCallError("backend down"))
    t = _t(llm, wait_seconds=0, max_attempts=1, ignore_cache=True)
    assert t.ignore_cache is True
    # BaseTranslator.translate() is what BabelDOC actually calls; it owns
    # the cache get/set around do_translate().
    assert t.translate("hello world") == "hello world"   # fallback→source
    assert t.translate("hello world") == "hello world"
    assert len(llm.calls) == 2          # backend hit BOTH times: no cache
    assert t.stats == (2, 2)            # stats stay accurate (guard works)


def test_distillation_guide_still_in_system_for_do_translate():
    llm = CapLLM()
    t = BabelDocTranslator("en", "zh-TW", llm,
                           guide="GLOSSARY: tensor => 張量")
    t.do_translate("the tensor")
    sys, _ = llm.calls[0]
    assert "TRANSLATION GUIDE" in sys and "張量" in sys
