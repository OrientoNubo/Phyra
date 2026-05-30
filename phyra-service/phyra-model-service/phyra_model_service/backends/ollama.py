"""
Ollama backend — native /api/chat with thinking DISABLED.

Ollama exposes an OpenAI-compatible API at `<host>/v1`, but qwen3 (and
other hybrid reasoning models) keep *thinking* on there: a one-sentence
translation cost ~430 generated tokens / ~7 s of hidden chain-of-thought
that the /v1 shim does not let you switch off (`/no_think`,
`chat_template_kwargs`, `think` are all ignored on /v1). The same call on
the NATIVE `/api/chat` endpoint with `"think": false` drops to ~48 tokens
/ <1 s — ~9× fewer tokens, several × faster — with no quality loss for a
translation task. So this client talks native /api/chat directly instead
of reusing the OpenAI SDK path. Thinking is **off by default** but the
user can opt back in per job (`BackendConfig.think`) — model choice and
this toggle are both left to the user.

`list_models()` queries `<host>/api/tags` and degrades gracefully
(returns `available: False`, never raises) when Ollama is not running.
"""

from __future__ import annotations

import logging

import httpx

from ..retry import is_rate_limit_response
from ..settings import DEFAULT_OLLAMA_HOST
from ..text import clean
from .base import BackendConfig, HardCallError, RateLimitSignal
from .openai_compatible import OpenAICompatibleClient

log = logging.getLogger("phyra-model-service.backend.ollama")


def normalize_host(base_url: str | None) -> str:
    """Accept either `http://h:11434` or `http://h:11434/v1`; return the
    bare host root (no trailing slash, no /v1)."""
    h = (base_url or DEFAULT_OLLAMA_HOST).strip().rstrip("/")
    if h.endswith("/v1"):
        h = h[:-3]
    return h.rstrip("/")


class OllamaClient(OpenAICompatibleClient):
    """Native-API client. Subclasses OpenAICompatibleClient only so the
    registry / isinstance checks keep working; `complete()` is fully
    overridden to hit `/api/chat` with `think: false`."""

    def __init__(self, cfg: BackendConfig):
        # Build the parent (OpenAI /v1) client too — harmless, and keeps
        # the type contract — but our complete() never uses it.
        host = normalize_host(cfg.base_url)
        super().__init__(
            cfg.model_copy(update={"base_url": host + "/v1"})
        )
        self.name = f"ollama-{cfg.model or 'unset'}"
        self._host = host
        self._model = cfg.model
        self._timeout = float(cfg.timeout_sec)
        self._headers = dict(cfg.extra_headers or {})
        self._think = bool(cfg.think)  # user choice; default False
        self._keep_alive = cfg.keep_alive  # unload after this idle window

    def complete(self, system: str, prompt: str) -> str:
        # Empty system → no system message (BabelDOC's llm_translate
        # path supplies a complete, self-contained prompt).
        messages = (
            [{"role": "system", "content": system}] if system else []
        ) + [{"role": "user", "content": prompt}]
        payload = {
            "model": self._model,
            "stream": False,
            "think": self._think,  # user choice; default False (fast)
            "keep_alive": self._keep_alive,  # idle-unload to free VRAM
            "options": {"temperature": 0},
            "messages": messages,
        }
        try:
            r = httpx.post(
                self._host + "/api/chat",
                json=payload,
                timeout=self._timeout,
                headers=self._headers or None,
            )
        except httpx.TimeoutException as e:
            raise HardCallError(f"ollama timeout: {str(e)[:200]}") from e
        except httpx.HTTPError as e:
            raise HardCallError(
                f"ollama connection: {str(e)[:200]}"
            ) from e

        if r.status_code != 200:
            body = (r.text or "")[:500]
            matched = is_rate_limit_response(f"{r.status_code} {body}")
            if r.status_code == 429 or matched:
                raise RateLimitSignal(matched or "http 429")
            raise HardCallError(
                f"ollama api error {r.status_code}: {body[:200]}"
            )

        try:
            data = r.json()
        except Exception as e:  # noqa: BLE001
            raise HardCallError(
                f"ollama bad JSON: {str(e)[:160]}"
            ) from e

        content = ((data.get("message") or {}).get("content")) or ""
        out = clean(content)
        if not out:
            matched = is_rate_limit_response(r.text or "")
            if matched:
                raise RateLimitSignal(matched)
            raise HardCallError("ollama returned empty completion")
        return out


def list_models(host: str | None = None) -> dict:
    """List locally installed Ollama models. Never raises."""
    base = normalize_host(host)
    try:
        r = httpx.get(base + "/api/tags", timeout=3.0)
        r.raise_for_status()
        data = r.json()
        models = sorted(
            m.get("name", "") for m in data.get("models", []) if m.get("name")
        )
        return {"available": True, "models": models, "host": base}
    except Exception as e:  # noqa: BLE001 — graceful degrade is the contract
        return {
            "available": False,
            "models": [],
            "host": base,
            "reason": f"Ollama not reachable at {base} ({e.__class__.__name__})",
        }
