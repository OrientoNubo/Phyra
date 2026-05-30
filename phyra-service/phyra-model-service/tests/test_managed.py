"""ManagedOllama lifecycle + unified-settings defaults. No real Ollama is
spawned: the subprocess / HTTP seams are mocked. The real
spawn→ready→stop path is exercised at runtime, not in unit tests.

These moved out of phyra-dualtrans because they monkeypatch the module's
own internals (`_is_ollama`, `shutil`), which only works when imported
from the module that actually defines them."""

from __future__ import annotations

import phyra_model_service.managed as osvc
from phyra_model_service.managed import ManagedOllama
from phyra_model_service.settings import (
    DEFAULT_KEEP_ALIVE,
    DEFAULT_MANAGED_PORT,
    DEFAULT_MODEL,
    ModelSettings,
)


def _mk(**kw):
    return ManagedOllama(
        port=kw.get("port", 11599), model=kw.get("model", "phyra-trans"),
        base_model=kw.get("base", "qwen3:14b"),
        num_parallel=kw.get("np", 2),
    )


def test_default_keep_alive_is_the_shared_constant():
    svc = _mk()
    assert svc.keep_alive == DEFAULT_KEEP_ALIVE      # single source of truth


def test_from_settings_uses_unified_defaults(monkeypatch):
    # no env → canonical defaults from ModelSettings
    for k in ("PHYRA_MODEL_OLLAMA_PORT", "PHYRA_DUALTRANS_OLLAMA_PORT",
              "PHYRA_MODEL_OLLAMA_MODEL", "PHYRA_DUALTRANS_OLLAMA_MODEL",
              "PHYRA_MODEL_OLLAMA_KEEP_ALIVE",
              "PHYRA_DUALTRANS_OLLAMA_KEEP_ALIVE"):
        monkeypatch.delenv(k, raising=False)
    svc = ManagedOllama.from_settings(ModelSettings())
    assert svc.port == DEFAULT_MANAGED_PORT
    assert svc.model == DEFAULT_MODEL
    assert svc.keep_alive == DEFAULT_KEEP_ALIVE


def test_legacy_env_alias_still_honored(monkeypatch):
    monkeypatch.setenv("PHYRA_DUALTRANS_OLLAMA_KEEP_ALIVE", "30s")
    monkeypatch.setenv("PHYRA_DUALTRANS_OLLAMA_PORT", "11577")
    svc = ManagedOllama.from_settings(ModelSettings())
    assert svc.keep_alive == "30s"
    assert svc.port == 11577


def test_has_matches_tag_variants():
    h = ManagedOllama._has
    names = ["qwen3:14b", "phyra-trans:latest"]
    assert h(names, "phyra-trans") is True
    assert h(names, "qwen3:14b") is True
    assert h(names, "qwen3") is True                   # family match
    assert h(names, "llama3") is False


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
    monkeypatch.setattr(svc, "_spawn", lambda: spawned.append(True))
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
    monkeypatch.setattr(svc, "_tags", lambda: [])
    seen = []

    def fake_ollama(*args, timeout):
        seen.append(args[0])
        return True
    monkeypatch.setattr(svc, "_ollama", fake_ollama)
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
