"""Managed-Ollama lifecycle + config wiring. No real Ollama is spawned:
the subprocess / HTTP seams are mocked. The real spawn→ready→stop path
is exercised by the operator at runtime, not in unit tests."""

from __future__ import annotations

import phyra_dualtrans.ollama_service as osvc
from phyra_dualtrans.config import (
    builtin_defaults,
    get_settings,
    managed_ollama_host,
    resolve_backend,
)
from phyra_dualtrans.ollama_service import ManagedOllama


def _reload_settings(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()
    return get_settings()


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


def test_has_matches_tag_variants():
    h = ManagedOllama._has
    names = ["qwen3:14b", "phyra-trans:latest"]
    assert h(names, "phyra-trans") is True
    assert h(names, "qwen3:14b") is True
    assert h(names, "qwen3") is True                   # family match
    assert h(names, "llama3") is False


def _mk(**kw):
    return ManagedOllama(
        port=kw.get("port", 11599), model=kw.get("model", "phyra-trans"),
        base_model=kw.get("base", "qwen3:14b"),
        num_parallel=kw.get("np", 2),
    )


def test_start_no_binary_is_safe(monkeypatch):
    monkeypatch.setattr(osvc.shutil, "which", lambda _: None)
    monkeypatch.setattr(osvc, "_is_ollama", lambda *a, **k: False)
    monkeypatch.setattr(osvc, "_port_open", lambda *a, **k: False)
    svc = _mk()
    svc._bin = None
    svc.start()                                        # must not raise
    assert svc.model_status == "error"
    assert svc._owned is False
    svc.stop()                                         # no-op, no raise


def test_start_reuses_existing_ollama(monkeypatch):
    monkeypatch.setattr(osvc, "_is_ollama", lambda *a, **k: True)
    spawned = []
    svc = _mk()
    monkeypatch.setattr(svc, "_spawn",
                        lambda: spawned.append(True))
    monkeypatch.setattr(svc, "_ensure_model_safe", lambda: None)
    svc.start()
    assert spawned == []                # reused, never spawned
    assert svc._owned is False
    assert svc._ready_evt.is_set()
    svc.stop()                          # must not kill someone else's


def test_ensure_model_present_is_ready(monkeypatch):
    svc = _mk()
    svc._bin = "/usr/bin/ollama"
    monkeypatch.setattr(svc, "_tags",
                        lambda: ["phyra-trans:latest", "qwen3:14b"])
    called = []
    monkeypatch.setattr(svc, "_ollama",
                        lambda *a, **k: called.append(a) or True)
    svc._ensure_model()
    assert svc.model_status == "ready"
    assert called == []                 # no pull/create needed


def test_ensure_model_pulls_then_creates(monkeypatch):
    svc = _mk()
    svc._bin = "/usr/bin/ollama"
    # base absent first; after "pull" the create succeeds
    monkeypatch.setattr(svc, "_tags", lambda: [])
    seen = []

    def fake_ollama(*args, timeout):
        seen.append(args[0])
        return True
    monkeypatch.setattr(svc, "_ollama", fake_ollama)
    # after create, _has(self._tags(), model) must be True
    monkeypatch.setattr(svc, "_tags",
                        lambda: ["phyra-trans:latest"]
                        if "create" in seen else [])
    svc._ensure_model()
    assert "pull" in seen and "create" in seen
    assert svc.model_status == "ready"


def test_modelfile_recipe():
    assert "FROM qwen3:14b" in osvc._MODELFILE.format(base="qwen3:14b")
    for p in ("num_ctx 8192", "temperature 0.3", "top_p 0.9",
              "repeat_penalty 1.05"):
        assert p in osvc._MODELFILE
