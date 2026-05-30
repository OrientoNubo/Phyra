"""Runtime probes, standalone — placement classification + graceful
degrade when Ollama is unreachable (never raises)."""

from __future__ import annotations

from phyra_model_service import runtime as rs


def test_placement_classification():
    assert rs._placement(100, 0) == "cpu"        # fully on CPU
    assert rs._placement(100, 100) == "gpu"      # fully resident in VRAM
    assert rs._placement(100, 40) == "partial"   # split GPU/CPU
    assert rs._placement(0, 0) == "unknown"


def test_worst_placement_picks_least_gpu():
    assert rs._worst_placement([{"placement": "gpu"},
                                {"placement": "cpu"}]) == "cpu"
    assert rs._worst_placement([{"placement": "gpu"},
                                {"placement": "partial"}]) == "partial"
    assert rs._worst_placement([]) is None


def test_collect_degrades_when_ollama_unreachable():
    out = rs.collect("http://127.0.0.1:1")
    assert set(out) >= {"level", "summary", "detail", "gpu", "ollama"}
    assert out["level"] in {"ok", "warn", "error"}
    assert out["ollama"]["reachable"] is False
