"""dualtrans config → shared model layer wiring. The ManagedOllama
lifecycle unit tests moved to phyra-model-service (they monkeypatch that
module's own internals); what remains here is the dualtrans-specific
bridge: resolve_backend / managed_ollama_host / builtin_defaults reading
the unified ModelSettings (still via the legacy PHYRA_DUALTRANS_OLLAMA_*
env names)."""

from __future__ import annotations

from phyra_dualtrans.config import (
    builtin_defaults,
    get_settings,
    managed_ollama_host,
    resolve_backend,
)


def _reload_settings(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()      # AppSettings is cached; ModelSettings is fresh


def test_resolve_backend_uses_managed_host_when_enabled(monkeypatch):
    _reload_settings(monkeypatch,
                     PHYRA_DUALTRANS_MANAGE_OLLAMA="1",
                     PHYRA_DUALTRANS_OLLAMA_PORT="11500")
    cfg = resolve_backend(kind="ollama")
    assert cfg.base_url == "http://127.0.0.1:11500"
    assert managed_ollama_host() == "http://127.0.0.1:11500"
    # the UI first-paint model becomes the tuned managed model
    assert builtin_defaults()["model"] == "phyra-trans"
    # an explicit per-request Base URL still wins
    cfg2 = resolve_backend(kind="ollama", base_url="http://x:9/v1")
    assert cfg2.base_url == "http://x:9/v1"


def test_resolve_backend_falls_back_when_unmanaged(monkeypatch):
    _reload_settings(monkeypatch,
                     PHYRA_DUALTRANS_MANAGE_OLLAMA="0",
                     OLLAMA_HOST="http://localhost:11434")
    assert managed_ollama_host() is None
    assert resolve_backend(kind="ollama").base_url == \
        "http://localhost:11434"
    assert "base_url" not in builtin_defaults()        # never echoed
