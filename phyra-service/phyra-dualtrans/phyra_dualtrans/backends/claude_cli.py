"""
Claude CLI (headless) backend.

Ports the upstream paper-translate `_spawn_once` verbatim: spawn
`claude -p --model <m> --append-system-prompt <system>` and feed the user
prompt on stdin. Uses the host's existing Claude Code auth — no API key.
"""

from __future__ import annotations

import logging
import shutil
import subprocess

from ..pipeline.prompts import clean
from ..vendor._retry import is_rate_limit_response
from .base import BackendConfig, BackendUnavailable, HardCallError, RateLimitSignal

log = logging.getLogger("phyra-dualtrans.backend.claude")


def claude_bin() -> str:
    p = shutil.which("claude")
    if not p:
        raise BackendUnavailable(
            "`claude` not found in PATH (the claude_cli backend needs the "
            "Claude Code CLI installed and authenticated on the host)."
        )
    return p


class ClaudeCliClient:
    def __init__(self, cfg: BackendConfig):
        self.cfg = cfg
        self.name = f"claude-{cfg.model}"
        self._claude = claude_bin()

    def complete(self, system: str, prompt: str) -> str:
        argv = [self._claude, "-p", "--model", self.cfg.model]
        if system:  # empty → no system (BabelDOC llm_translate path)
            argv += ["--append-system-prompt", system]
        try:
            res = subprocess.run(
                argv,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.cfg.timeout_sec,
            )
        except subprocess.TimeoutExpired as e:
            raise HardCallError(
                f"claude timed out after {self.cfg.timeout_sec}s"
            ) from e
        out = clean(res.stdout)
        combined = (res.stderr or "") + (res.stdout or "")
        matched = is_rate_limit_response(combined)
        if matched:
            raise RateLimitSignal(matched)
        if res.returncode != 0 or not out:
            raise HardCallError(
                f"claude rc={res.returncode} out_empty={not out} "
                f"stderr={res.stderr.strip()[:200]!r}"
            )
        return out
