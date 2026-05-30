"""
Per-language translation system prompts + output cleaner.

Ported VERBATIM from Phyra paper-translate's translate_with_claude.py
(SYSTEM_PROMPTS / system_prompt_for / _clean). Shared by every LLM
backend so translation behaviour is identical regardless of provider.
The default zh-TW prompt enforces Taiwan terminology.
"""

import re

SYSTEM_PROMPTS = {
    "zh-TW": (
        "You are a professional Taiwan-localized scientific translator. "
        "Translate the user's English input to Traditional Chinese using "
        "Taiwan terminology (軟體 not 软件, 演算法 not 算法, 函式 not 函数, "
        "程式 not 程序, 介面 not 接口, 預設 not 默认). "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "zh-HK": (
        "You are a professional Hong Kong-localized scientific translator. "
        "Translate to Traditional Chinese (Hong Kong conventions). "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "zh-CN": (
        "You are a professional scientific translator. "
        "Translate the user's English input to Simplified Chinese using "
        "mainland China terminology. "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "ja": (
        "You are a professional Japanese scientific translator. "
        "Translate the user's English input to natural Japanese, using "
        "established academic terminology where it exists. "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "ko": (
        "You are a professional Korean scientific translator. "
        "Translate the user's English input to natural Korean. "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
}


def system_prompt_for(lang_out: str) -> str:
    return SYSTEM_PROMPTS.get(
        lang_out,
        (
            "You are a professional scientific translator. "
            f"Translate the user's input to {lang_out}, output the translation only. "
            "Preserve every placeholder token verbatim, including {v0} {v1} ... "
            "and <style id='0'>...</style> tags. "
            "No preamble, no notes, no quotes."
        ),
    )


_THINK_RE = re.compile(r"<think\b[^>]*>.*?</think>", re.DOTALL | re.IGNORECASE)
_OPEN_THINK_RE = re.compile(r"<think\b[^>]*>.*\Z", re.DOTALL | re.IGNORECASE)
# qwen3's thinking SOFT-SWITCH control tokens. Ollama appends `/no_think`
# to the prompt when `think:false`; a fine-tuned model (e.g. qwen3-32b-trans)
# can echo the bare token back into its `content` as literal text, where it
# surfaces in the translated PDF ("...具體來說 /no_think"). These tokens are
# never legitimate translation output, so strip any that leak through. Match
# the standalone token (optionally flanked by whitespace), not substrings of
# real words.
# `\s*` eats any whitespace before the token; the trailing guard forbids an
# ASCII word char so "/thinking" is spared but "/no_think。" (CJK/punct after)
# is still stripped. no_think is listed first so the longer token wins.
_SOFT_SWITCH_RE = re.compile(
    r"\s*/(?:no_think|think)(?![A-Za-z0-9_])", re.IGNORECASE
)


def clean(s: str) -> str:
    """Strip ANSI escape sequences, reasoning-model ``<think>`` blocks,
    stray qwen ``/no_think`` `/` ``/think`` control tokens, and surrounding
    whitespace.

    The ANSI strip is ported VERBATIM from upstream. The ``<think>``
    removal is an intentional extension: hybrid reasoning models
    (qwen3, etc.) can leak a chain-of-thought block into ``content``;
    if it reached BabelDOC it would corrupt the translated PDF. The
    ``/no_think`` strip handles the same family of models echoing the
    thinking soft-switch token as literal text. Claude never emits any of
    these, so this is a no-op there."""
    s = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)  # strip ANSI
    s = _THINK_RE.sub("", s)                      # closed <think>…</think>
    s = _OPEN_THINK_RE.sub("", s)                 # unterminated <think>…
    s = _SOFT_SWITCH_RE.sub("", s)                # stray /no_think · /think
    return s.strip()
