"""
_retry.py (v0.8.0) — shared rate-limit retry harness for paper-read scripts.

User contract: when a `claude -p` subprocess returns a rate-limit /
usage-limit response, sleep 30 minutes and retry. Up to 50 attempts before
giving up. Every attempt is logged to `<cache_dir>/_retry.log` with timestamp,
PID, attempt number, and the matched signal text.

Usage:
  from _retry import retry_on_rate_limit, RateLimitError

  @retry_on_rate_limit(label="A1 OVERVIEW", log_dir=Path(".phyra/.cache/<slug>"))
  def call(prompt, system_prompt):
      ...   # if claude returns a rate-limit response, raise RateLimitError(text)
            # otherwise return the result string

Or imperatively:
  text = retry_call(
      lambda: call_once(...),
      label="A1 OVERVIEW",
      log_dir=Path(".phyra/.cache/<slug>"),
  )
"""

import functools
import logging
import os
import re
import time
from pathlib import Path

log = logging.getLogger("retry")

DEFAULT_WAIT_SECONDS = 30 * 60        # 30 minutes
DEFAULT_MAX_ATTEMPTS = 50

# Heuristic detector. claude -p emits messages like:
#   "Claude AI usage limit reached|<unix-ts>"
#   "rate_limit_error: ..."
#   "anthropic-rate-limit-error"
RATE_LIMIT_PATTERNS = [
    re.compile(r"usage\s*limit\s*(reached|hit|exceeded)", re.IGNORECASE),
    re.compile(r"rate[\-_ ]limit", re.IGNORECASE),
    re.compile(r"anthropic[\-_ ]rate[\-_ ]limit", re.IGNORECASE),
    re.compile(r"\b429\b"),
]


class RateLimitError(RuntimeError):
    """Raised by the inner call when a rate-limit response is detected."""
    pass


def is_rate_limit_response(text: str) -> str | None:
    """Return the matched substring if `text` looks like a rate-limit
    response, else None. Caller should treat truthy return as 'must retry'."""
    if not text:
        return None
    for rx in RATE_LIMIT_PATTERNS:
        m = rx.search(text)
        if m:
            return m.group(0)
    return None


def _append_log(log_dir: Path, line: str) -> None:
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "_retry.log").open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception as e:  # never let logging break the pipeline
        log.debug("retry-log write skipped: %s", e)


def retry_call(fn, *,
               label: str,
               log_dir: Path,
               wait_seconds: int = DEFAULT_WAIT_SECONDS,
               max_attempts: int = DEFAULT_MAX_ATTEMPTS):
    """Call `fn()`, retrying on RateLimitError. Returns fn's result.

    `fn` should:
      - raise RateLimitError(matched_text) when the LLM response looks like
        a rate-limit response, OR
      - raise any other exception (which we propagate without retry), OR
      - return a value (returned to the caller).
    """
    pid = os.getpid()
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = fn()
            if attempt > 1:
                _append_log(
                    log_dir,
                    f"{time.strftime('%Y-%m-%dT%H:%M:%S')} pid={pid} "
                    f"label={label!r} attempt={attempt} status=ok",
                )
            return result
        except RateLimitError as e:
            last_err = e
            line = (
                f"{time.strftime('%Y-%m-%dT%H:%M:%S')} pid={pid} "
                f"label={label!r} attempt={attempt}/{max_attempts} "
                f"signal={str(e)!r} sleeping={wait_seconds}s"
            )
            log.warning(line)
            _append_log(log_dir, line)
            if attempt >= max_attempts:
                break
            time.sleep(wait_seconds)
    raise RuntimeError(
        f"[{label}] rate-limit retry exhausted after {max_attempts} attempts; "
        f"last signal: {last_err!s}"
    )


def retry_on_rate_limit(*, label: str, log_dir: Path,
                        wait_seconds: int = DEFAULT_WAIT_SECONDS,
                        max_attempts: int = DEFAULT_MAX_ATTEMPTS):
    """Decorator form."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return retry_call(
                lambda: fn(*args, **kwargs),
                label=label, log_dir=log_dir,
                wait_seconds=wait_seconds, max_attempts=max_attempts,
            )
        return wrapper
    return decorator
