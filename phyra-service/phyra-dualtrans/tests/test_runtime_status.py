from fastapi.testclient import TestClient

from phyra_dualtrans import runtime_status as rs
from phyra_dualtrans.web.app import app


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
    """A dead Ollama host must never raise — it becomes a field. The
    verdict still reflects GPU availability (which varies by host), so we
    only assert the shape and that ollama is reported unreachable."""
    out = rs.collect("http://127.0.0.1:1")
    assert set(out) >= {"level", "summary", "detail", "gpu", "ollama"}
    assert out["level"] in {"ok", "warn", "error"}
    assert out["ollama"]["reachable"] is False


def test_runtime_route_shape():
    with TestClient(app) as c:
        r = c.get("/api/runtime", params={"host": "http://127.0.0.1:1"})
        assert r.status_code == 200
        body = r.json()
        assert body["ollama"]["reachable"] is False
        assert isinstance(body["summary"], str) and body["summary"]
