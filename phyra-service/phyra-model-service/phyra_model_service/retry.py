"""
Rate-limit detection for backend responses.

`is_rate_limit_response()` is a small heuristic the backends use to map a
provider response onto the translator's retry/fallback contract: a truthy
return means "this looks rate-limited — sleep + retry", None means "treat
as a hard failure / normal output".

This is the generic detector extracted from phyra-dualtrans's vendored
`_retry.py`; the full 30-minute retry harness (retry_call / decorator)
stays vendored in the plugin where it belongs.
"""

from __future__ import annotations

import re

# Heuristic detector. claude -p / OpenAI-compatible servers emit messages
# like:
#   "Claude AI usage limit reached|<unix-ts>"
#   "rate_limit_error: ..."
#   "anthropic-rate-limit-error"
RATE_LIMIT_PATTERNS = [
    re.compile(r"usage\s*limit\s*(reached|hit|exceeded)", re.IGNORECASE),
    re.compile(r"rate[\-_ ]limit", re.IGNORECASE),
    re.compile(r"anthropic[\-_ ]rate[\-_ ]limit", re.IGNORECASE),
    re.compile(r"\b429\b"),
]


def is_rate_limit_response(text: str) -> str | None:
    """Return the matched substring if `text` looks like a rate-limit
    response, else None. Caller should treat a truthy return as 'must
    retry'."""
    if not text:
        return None
    for rx in RATE_LIMIT_PATTERNS:
        m = rx.search(text)
        if m:
            return m.group(0)
    return None
