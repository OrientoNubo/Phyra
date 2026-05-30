"""
OpenAI-compatible backend.

Covers OpenAI, DeepSeek, Together, Groq, OpenRouter, vLLM, LM Studio — any
endpoint speaking the OpenAI chat-completions API. Ollama reuses this class
(see ollama.py) pointed at its /v1 shim.

System prompt → `system` message, user prompt → `user` message,
temperature 0. Output is run through the same `clean()` as upstream.
"""

from __future__ import annotations

import logging

import openai
from openai import OpenAI

from ..retry import is_rate_limit_response
from ..text import clean
from .base import BackendConfig, HardCallError, RateLimitSignal

log = logging.getLogger("phyra-model-service.backend.openai")


class OpenAICompatibleClient:
    def __init__(self, cfg: BackendConfig):
        self.cfg = cfg
        self.name = f"openai-{cfg.model or 'unset'}"
        # OpenAI() requires a non-empty key string even for keyless local
        # servers; a real missing key is caught by preflight, not here.
        api_key = cfg.api_key.get_secret_value() if cfg.api_key else "EMPTY"
        self._client = OpenAI(
            base_url=cfg.base_url or "https://api.openai.com/v1",
            api_key=api_key,
            timeout=float(cfg.timeout_sec),
            max_retries=0,  # the translator owns the retry loop
            default_headers=cfg.extra_headers or None,
        )

    def complete(self, system: str, prompt: str) -> str:
        # Empty system → omit the system message entirely. BabelDOC's
        # llm_translate path hands us a complete, self-contained prompt
        # and (like BabelDOC's own client) must be sent with no system.
        messages = (
            [{"role": "system", "content": system}] if system else []
        ) + [{"role": "user", "content": prompt}]
        try:
            resp = self._client.chat.completions.create(
                model=self.cfg.model,
                messages=messages,
                temperature=0,
            )
        except openai.RateLimitError as e:
            raise RateLimitSignal(str(e)[:200]) from e
        except openai.APIStatusError as e:
            body = ""
            try:
                body = e.response.text or ""
            except Exception:
                pass
            matched = is_rate_limit_response(f"{e} {body}")
            if e.status_code == 429 or matched:
                raise RateLimitSignal(matched or "http 429") from e
            raise HardCallError(
                f"openai api error {e.status_code}: {str(e)[:200]}"
            ) from e
        except (openai.APITimeoutError, openai.APIConnectionError) as e:
            raise HardCallError(f"openai connection: {str(e)[:200]}") from e
        except openai.OpenAIError as e:
            matched = is_rate_limit_response(str(e))
            if matched:
                raise RateLimitSignal(matched) from e
            raise HardCallError(f"openai error: {str(e)[:200]}") from e
        except Exception as e:  # noqa: BLE001 — never leak an untyped error
            raise HardCallError(f"openai unexpected: {str(e)[:200]}") from e

        content = ""
        if resp.choices and resp.choices[0].message:
            content = resp.choices[0].message.content or ""
        out = clean(content)
        if not out:
            # Some OpenAI-compatible servers return HTTP 200 with a
            # rate-limit error in the body and no choices.
            try:
                raw = resp.model_dump_json()
            except Exception:
                raw = str(resp)
            matched = is_rate_limit_response(raw)
            if matched:
                raise RateLimitSignal(matched)
            raise HardCallError("openai returned empty completion")
        return out
