"""
Model-output cleaning.

`clean()` strips ANSI escapes, reasoning-model ``<think>`` blocks, and
stray qwen ``/no_think`` · ``/think`` soft-switch tokens from a model's
raw output. Shared by every backend so behaviour is identical regardless
of provider; Claude never emits any of these, so it is a no-op there.

Ported VERBATIM from phyra-dualtrans's pipeline/prompts.py (itself ported
from Phyra paper-translate). Lives in the shared model layer because the
``<think>`` / ``/no_think`` leakage is a property of how you talk to
hybrid reasoning models, not of any one service's pipeline.
"""

from __future__ import annotations

import re

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
    if it reached the consumer it would corrupt the output. The
    ``/no_think`` strip handles the same family of models echoing the
    thinking soft-switch token as literal text. Claude never emits any of
    these, so this is a no-op there."""
    s = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)  # strip ANSI
    s = _THINK_RE.sub("", s)                      # closed <think>…</think>
    s = _OPEN_THINK_RE.sub("", s)                 # unterminated <think>…
    s = _SOFT_SWITCH_RE.sub("", s)                # stray /no_think · /think
    return s.strip()
