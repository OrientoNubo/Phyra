"""
LLM backend abstraction.

The only thing that varies per provider is the actual model call. That
seam is `LLMClient.complete(system, prompt) -> str`.

`complete()` is intentionally SYNCHRONOUS — it is invoked from a thread
pool inside the caller's translation subprocess. Clients must not start
their own event loop.

Contract:
  - return the translated text on success
  - raise RateLimitSignal(matched)  when the response looks rate-limited
    (the caller's retry loop sleeps + retries on this)
  - raise HardCallError(...)        on any other non-retryable failure
    (the caller falls back to the source text on this)
"""

from __future__ import annotations

import json
from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from ..settings import DEFAULT_KEEP_ALIVE, DEFAULT_OLLAMA_HOST


class BackendError(RuntimeError):
    """Base class for all backend problems."""


class BackendUnavailable(BackendError):
    """Backend cannot be used (missing binary / unreachable / no key).

    Surfaced by preflight; must never crash the server."""


class RateLimitSignal(BackendError):
    """The provider rate-limited us. Caller retries after a sleep."""

    def __init__(self, matched: str):
        super().__init__(f"rate-limited: {matched}")
        self.matched = matched


class HardCallError(BackendError):
    """Non-retryable call failure. Caller falls back to source text."""


# 180s matches the upstream paper-translate CALL_TIMEOUT_SEC.
DEFAULT_TIMEOUT_SEC = 180


class BackendConfig(BaseModel):
    """Per-job backend selection + credentials.

    Built by the web layer and handed to the translation subprocess over
    stdin (never argv) so the api_key never appears in `ps`.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["openai", "ollama", "claude_cli"]
    model: str = ""
    base_url: str | None = None
    api_key: SecretStr | None = None
    timeout_sec: int = DEFAULT_TIMEOUT_SEC
    extra_headers: dict[str, str] = Field(default_factory=dict)
    # Ollama only: let the model "think" (hybrid reasoning). Default off
    # — for translation it ~9× the tokens / latency with no quality gain.
    # Exposed so the user can opt back in per job.
    think: bool = False
    # Ollama only: how long the model stays resident in VRAM after the
    # LAST request. Sent as `keep_alive` on every /api/chat call, so the
    # timer resets while a job streams blocks and only fires once the job
    # goes idle — at which point Ollama unloads and frees the VRAM.
    # Accepts an Ollama duration ("10s", "5m"), 0 (unload immediately),
    # or -1 (keep forever). Default DEFAULT_KEEP_ALIVE.
    keep_alive: str = DEFAULT_KEEP_ALIVE

    @model_validator(mode="after")
    def _fill_defaults(self) -> "BackendConfig":
        if self.kind == "claude_cli" and not self.model:
            self.model = "sonnet"
        if self.kind == "ollama" and not self.base_url:
            self.base_url = DEFAULT_OLLAMA_HOST
        if self.kind == "openai" and not self.base_url:
            self.base_url = "https://api.openai.com/v1"
        return self

    def redacted(self) -> dict:
        """Dict form with the api_key masked — safe to log / echo back."""
        d = self.model_dump(mode="json")
        if self.api_key is not None:
            d["api_key"] = "***"
        return d

    def child_json(self) -> str:
        """JSON for the translation child's stdin — includes the REAL
        api_key (pydantic would otherwise serialize SecretStr as ****)."""
        d = self.model_dump(mode="json")
        d["api_key"] = (
            self.api_key.get_secret_value() if self.api_key else None
        )
        return json.dumps(d)


@runtime_checkable
class LLMClient(Protocol):
    name: str

    def complete(self, system: str, prompt: str) -> str: ...
