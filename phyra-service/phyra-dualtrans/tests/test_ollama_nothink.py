"""OllamaClient must hit native /api/chat with think=false (the ~9x
token/latency win), not the OpenAI /v1 shim where thinking can't be
disabled. clean() must also strip leaked <think> blocks."""

from __future__ import annotations

import json

import httpx
import pytest

from phyra_dualtrans.backends import get_backend
from phyra_dualtrans.backends.base import (
    BackendConfig,
    HardCallError,
    RateLimitSignal,
)
from phyra_dualtrans.pipeline.prompts import clean


class _Resp:
    def __init__(self, status, payload=None, text=""):
        self.status_code = status
        self._payload = payload
        self.text = text if text else json.dumps(payload or {})

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def _client(monkeypatch, captured, *, think=False):
    def fake_post(url, json=None, timeout=None, headers=None):
        captured["url"] = url
        captured["json"] = json
        return captured["resp"]

    monkeypatch.setattr(httpx, "post", fake_post)
    return get_backend(BackendConfig(
        kind="ollama", model="qwen3-32b-trans",
        base_url="http://localhost:11434/v1", think=think,
    ))


def test_uses_native_api_chat_with_think_false(monkeypatch):
    cap = {"resp": _Resp(200, {"message": {"content": "譯文"}})}
    c = _client(monkeypatch, cap)
    out = c.complete("sys", "translate this")

    assert out == "譯文"
    assert cap["url"] == "http://localhost:11434/api/chat"   # native, not /v1
    assert cap["json"]["think"] is False                     # thinking off
    assert cap["json"]["stream"] is False
    assert cap["json"]["options"]["temperature"] == 0
    assert cap["json"]["messages"][0]["role"] == "system"


def test_think_true_is_forwarded_when_user_opts_in(monkeypatch):
    cap = {"resp": _Resp(200, {"message": {"content": "x"}})}
    c = _client(monkeypatch, cap, think=True)
    c.complete("s", "p")
    assert cap["json"]["think"] is True            # user choice honored


def test_resolve_backend_defaults_think_off_and_forwards():
    from phyra_dualtrans.config import resolve_backend
    assert resolve_backend(kind="ollama", model="m").think is False
    assert resolve_backend(kind="ollama", model="m", think=True).think is True


def test_keep_alive_sent_on_every_chat_call(monkeypatch):
    # The idle-unload window must ride on the chat payload so Ollama frees
    # VRAM ~keep_alive after the last block; the timer resets per request.
    cap = {"resp": _Resp(200, {"message": {"content": "譯"}})}
    c = _client(monkeypatch, cap)
    c.complete("s", "p")
    assert cap["json"]["keep_alive"] == "10s"   # BackendConfig default


def test_resolve_backend_forwards_keep_alive_from_settings(monkeypatch):
    from phyra_dualtrans import config
    config.get_settings.cache_clear()
    monkeypatch.setenv("PHYRA_DUALTRANS_OLLAMA_KEEP_ALIVE", "30s")
    try:
        assert config.resolve_backend(kind="ollama", model="m").keep_alive \
            == "30s"
    finally:
        config.get_settings.cache_clear()


def test_empty_system_sends_no_system_message(monkeypatch):
    cap = {"resp": _Resp(200, {"message": {"content": "x"}})}
    c = _client(monkeypatch, cap)
    c.complete("", "just the user prompt")          # llm_translate path
    roles = [m["role"] for m in cap["json"]["messages"]]
    assert roles == ["user"]                        # no system message
    assert cap["json"]["messages"][0]["content"] == "just the user prompt"


def test_nonempty_system_still_sent(monkeypatch):
    cap = {"resp": _Resp(200, {"message": {"content": "x"}})}
    c = _client(monkeypatch, cap)
    c.complete("SYS", "USR")
    roles = [m["role"] for m in cap["json"]["messages"]]
    assert roles == ["system", "user"]


def test_leaked_think_block_is_stripped(monkeypatch):
    cap = {"resp": _Resp(200, {"message": {
        "content": "<think>reasoning we must not keep</think>最終譯文"}})}
    c = _client(monkeypatch, cap)
    assert c.complete("s", "p") == "最終譯文"


def test_http_429_is_rate_limit_signal(monkeypatch):
    cap = {"resp": _Resp(429, None, text="Too Many Requests")}
    c = _client(monkeypatch, cap)
    with pytest.raises(RateLimitSignal):
        c.complete("s", "p")


def test_empty_completion_is_hard_error(monkeypatch):
    cap = {"resp": _Resp(200, {"message": {"content": "   "}})}
    c = _client(monkeypatch, cap)
    with pytest.raises(HardCallError):
        c.complete("s", "p")


def test_connection_error_is_hard_error(monkeypatch):
    def boom(*a, **k):
        raise httpx.ConnectError("refused")

    monkeypatch.setattr(httpx, "post", boom)
    c = get_backend(BackendConfig(kind="ollama", model="m"))
    with pytest.raises(HardCallError):
        c.complete("s", "p")


def test_clean_strips_think_variants():
    assert clean("<think>a\nb</think>  hello ") == "hello"
    assert clean("<think foo='1'>x</think>譯") == "譯"
    assert clean("partial <think>never closed ...") == "partial"
    assert clean("no think here") == "no think here"


def test_clean_strips_stray_soft_switch_tokens():
    # the reported NetLLM bug: qwen3-32b-trans echoes the bare /no_think
    # control token into its translation output.
    assert clean("具體來說，當遺憾率 LLM 以達成目標 /no_think") \
        == "具體來說，當遺憾率 LLM 以達成目標"
    assert clean("/think 譯文內容") == "譯文內容"
    assert clean("譯文/no_think。") == "譯文。"        # CJK/punct around it
    assert clean("結果。 /no_think") == "結果。"
    # must NOT eat real words that merely contain the substring
    assert clean("rethinking the problem") == "rethinking the problem"
    assert clean("a path like models/thinking-v2") \
        == "a path like models/thinking-v2"
