"""
The single BabelDOC BaseTranslator, with a pluggable LLMClient.

Upstream paper-translate had ClaudeHeadlessTranslator mixing three
concerns: BabelDOC protocol glue, the rate-limit retry loop, and the
actual model call. Only the last varies per provider, so here the call is
injected as `LLMClient.complete()` and everything else is written once.

The retry loop + placeholder tuples are ported VERBATIM (timing,
fallback-to-source semantics, and the formula / rich-text placeholder
regexes must stay byte-identical or BabelDOC's reassembly corrupts).
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable

from babeldoc.translator.translator import BaseTranslator

from ..backends.base import HardCallError, LLMClient, RateLimitSignal
from .prompts import system_prompt_for

EmitFn = Callable[..., None]


class BabelDocTranslator(BaseTranslator):
    name = "phyra-dual"  # ≤20 chars (BabelDOC requirement)

    def __init__(
        self,
        lang_in: str,
        lang_out: str,
        llm: LLMClient,
        *,
        ignore_cache: bool = False,
        emit: EmitFn | None = None,
        wait_seconds: int = 60,
        max_attempts: int = 8,
        guide: str | None = None,
    ):
        super().__init__(lang_in, lang_out, ignore_cache)
        # BabelDOC's logical model id (used in its caches / logs). Fold a
        # short hash of the distillation guide in, so a different guide
        # never reuses cached segments translated under another guide.
        self.model = f"phyra-{llm.name}"
        if guide:
            h = hashlib.sha1(guide.encode("utf-8")).hexdigest()[:8]
            self.model = f"{self.model}-g{h}"
        self._llm = llm
        base_sys = system_prompt_for(lang_out)
        self._sys = (
            f"{base_sys}\n\n"
            "# TRANSLATION GUIDE (apply consistently across the whole "
            f"document)\n{guide.strip()}"
            if guide else base_sys
        )
        self._n = 0
        self._fallbacks = 0  # segments that returned source (call failed)
        self._emit: EmitFn = emit or (lambda **kw: None)
        self._wait = wait_seconds
        self._max = max_attempts

    @property
    def stats(self) -> tuple[int, int]:
        """(total segment calls, segments that fell back to source)."""
        return self._n, self._fallbacks

    def _run(self, system: str, user: str, *, fallback):
        """Call the model with the retry / rate-limit loop. On a
        non-retryable failure (or exhausted retries) return `fallback`."""
        self._n += 1
        i = self._n
        for attempt in range(1, self._max + 1):
            try:
                return self._llm.complete(system, user)
            except RateLimitSignal as e:
                self._emit(
                    type="rate_limit",
                    chunk=i,
                    attempt=attempt,
                    max_attempts=self._max,
                    wait_sec=self._wait,
                    signal=e.matched,
                )
                if attempt >= self._max:
                    self._emit(type="chunk_fallback", chunk=i,
                               reason="rate-limit retries exhausted")
                    self._fallbacks += 1
                    return fallback
                time.sleep(self._wait)
                continue
            except HardCallError as e:
                self._emit(type="chunk_fallback", chunk=i, reason=str(e))
                self._fallbacks += 1
                return fallback
        self._fallbacks += 1
        return fallback

    def do_translate(self, text, rate_limit_params=None):
        # BabelDOC hands us a RAW segment here — we build the prompt.
        user = (
            f"Translate to {self.lang_out}. Output the translation only.\n\n"
            f"INPUT:\n{text}"
        )
        return self._run(self._sys, user, fallback=text)

    def do_llm_translate(self, text, rate_limit_params=None):
        # NOT SUPPORTED — on purpose. BabelDOC routes translation to its
        # `ILTranslatorLLMOnly` engine iff this raises nothing on the
        # `do_llm_translate(None)` probe. That engine sends a JSON BATCH
        # prompt (`request_json_mode`) and `json.loads()` the reply,
        # expecting `[{"id":0,"output":"…"}]`. Our backends return PLAIN
        # translated text (claude_cli / ollama / generic OpenAI), so the
        # parse fails every batch → BabelDOC falls back per-paragraph and
        # ~17% of segments end up untranslated (the reported "very bad"
        # IM-CMDet output). Raising NotImplementedError makes BabelDOC
        # use the simple per-paragraph `ILTranslator` path → our
        # `do_translate()` with the prompt + placeholder tuples, which is
        # the proven-good path (and what upstream paper-translate used).
        raise NotImplementedError(
            "phyra-dualtrans backends return plain text; BabelDOC's "
            "JSON-batch llm-only mode is intentionally not advertised."
        )

    # Match OpenAITranslator's (string, regex) tuple shape — VERBATIM.
    def get_formular_placeholder(self, placeholder_id):
        return (
            "{v" + str(placeholder_id) + "}",
            r"\{\s*v\s*" + str(placeholder_id) + r"\s*\}",
        )

    def get_rich_text_left_placeholder(self, placeholder_id):
        return (
            f"<style id='{placeholder_id}'>",
            r"<\s*style\s*id\s*=\s*'\s*" + str(placeholder_id) + r"\s*'\s*>",
        )

    def get_rich_text_right_placeholder(self, placeholder_id):
        return ("</style>", r"<\s*/\s*style\s*>")


def translation_effectively_failed(calls: int, fallbacks: int) -> bool:
    """True when the backend produced essentially NO translation — every
    (or ≥95% over a meaningful number of) segment fell back to source.
    That is a broken/unreachable backend (e.g. wrong Base URL), not a
    content quirk; the job must fail loudly, not 'succeed' with an
    all-source 'bilingual' PDF."""
    return calls >= 5 and fallbacks / calls >= 0.95
