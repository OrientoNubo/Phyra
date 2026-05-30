import json

from phyra_dualtrans.backends import get_backend, list_ollama_models
from phyra_dualtrans.backends.base import BackendConfig
from phyra_dualtrans.config import resolve_backend
from phyra_dualtrans.vendor._retry import is_rate_limit_response


def test_backend_config_defaults():
    c = BackendConfig(kind="claude_cli")
    assert c.model == "sonnet"          # claude_cli default
    c2 = BackendConfig(kind="ollama")
    assert c2.base_url == "http://localhost:11434"
    c3 = BackendConfig(kind="openai")
    assert c3.base_url == "https://api.openai.com/v1"


def test_child_json_carries_real_key_but_redacted_masks():
    c = BackendConfig(kind="openai", model="gpt-4o", api_key="sk-secret")
    payload = json.loads(c.child_json())
    assert payload["api_key"] == "sk-secret"      # child needs the real key
    assert c.redacted()["api_key"] == "***"       # API echo is masked


def test_rate_limit_detector():
    assert is_rate_limit_response("HTTP 429 Too Many Requests")
    assert is_rate_limit_response("Claude AI usage limit reached|1700")
    assert is_rate_limit_response("anthropic-rate-limit-error")
    assert is_rate_limit_response("a normal translation sentence") is None


def test_get_backend_constructs_clients():
    assert get_backend(BackendConfig(kind="openai", model="x", api_key="k"))
    assert get_backend(BackendConfig(kind="ollama", model="llama3"))


def test_ollama_unavailable_is_graceful():
    # nothing is listening on this port — must NOT raise
    info = list_ollama_models("http://127.0.0.1:1")
    assert info["available"] is False
    assert info["models"] == []
    assert "not reachable" in info["reason"]


def test_resolve_backend_env_key_only_with_env_base(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    from phyra_dualtrans.config import get_settings

    get_settings.cache_clear()
    # no caller base_url → env key paired with the env base
    cfg = resolve_backend(kind="openai", model="gpt-4o")
    assert cfg.api_key.get_secret_value() == "env-key"
    assert cfg.base_url == "https://api.openai.com/v1"

    # caller supplies ITS OWN base_url + no key → env key must NOT leak
    # there (this is the key-exfiltration vector being closed)
    cfg2 = resolve_backend(kind="openai", model="gpt-4o",
                           base_url="http://attacker.example/v1")
    assert cfg2.base_url == "http://attacker.example/v1"
    assert cfg2.api_key is None

    # explicit per-request key is always honored
    cfg3 = resolve_backend(kind="openai", model="gpt-4o",
                           base_url="http://x/v1", api_key="req-key")
    assert cfg3.api_key.get_secret_value() == "req-key"
