"""The claude_cli backend is gated by an optional shared password.

Rationale: claude_cli spends THIS host's Claude Code auth (no API key,
billed to the operator). The service has no auth and binds 0.0.0.0, so on
a shared / public network anyone reachable could otherwise burn that quota.
The password is env-only — there is no server-side, API-writable
settings file at all (per-user prefs are browser-local).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from phyra_dualtrans.config import get_settings
from phyra_dualtrans.web.app import app

CLAUDE = '{"kind":"claude_cli","model":"sonnet"}'
OPENAI = '{"kind":"openai","model":"gpt-4o"}'


@pytest.fixture
def gated(monkeypatch):
    monkeypatch.setenv("PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD", "s3cret")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_claude_cli_wrong_password_is_401(gated):
    with TestClient(app) as c:
        r = c.post("/api/translate", data={
            "backend": CLAUDE, "admin_password": "nope",
        })
        assert r.status_code == 401
        r2 = c.post("/api/translate", data={"backend": CLAUDE})  # missing
        assert r2.status_code == 401


def test_claude_cli_correct_password_passes_gate(gated):
    # Correct password → gate passes; with no file/arxiv it then fails the
    # INPUT check (400), proving auth succeeded without spawning a job.
    with TestClient(app) as c:
        r = c.post("/api/translate", data={
            "backend": CLAUDE, "admin_password": "s3cret",
        })
        assert r.status_code == 400
        assert "401" not in str(r.status_code)


def test_other_backends_not_gated(gated):
    # openai supplies its own key; the claude_cli password must not apply.
    with TestClient(app) as c:
        r = c.post("/api/translate", data={"backend": OPENAI})
        assert r.status_code != 401
        assert r.status_code == 400  # only missing input


def test_no_gate_when_unconfigured():
    # No password env → backward compatible: claude_cli reaches the input
    # check (400), never 401.
    get_settings.cache_clear()
    with TestClient(app) as c:
        r = c.post("/api/translate", data={"backend": CLAUDE})
        assert r.status_code == 400


def test_backends_endpoint_advertises_gate(gated):
    with TestClient(app) as c:
        info = {b["kind"]: b for b in c.get("/api/backends").json()}
        assert info["claude_cli"]["needs_password"] is True
        assert info["openai"]["needs_password"] is False   # caller pays
        assert info["ollama"]["needs_password"] is False    # never gated


OLLAMA = '{"kind":"ollama","model":"qwen3-32b-trans"}'


def test_ollama_is_never_gated(gated):
    """Even with the claude_cli password set, ollama (local GPU) is not
    gated — by design / per user request."""
    with TestClient(app) as c:
        # no admin_password, claude_cli password configured → still not 401
        r = c.post("/api/translate", data={"backend": OLLAMA})
        assert r.status_code == 400   # only missing input, never 401


def test_arxiv_field_rejects_local_path_lfi():
    """The arxiv field must be a real arXiv id/URL — a filesystem path
    would be read by resolve_input() (arbitrary-file read)."""
    with TestClient(app) as c:
        for evil in ("/etc/passwd", "/home/nubo/.ssh/id_rsa",
                     "../../etc/hosts", "file:///etc/passwd",
                     "~/secret.pdf"):
            r = c.post("/api/translate", data={
                "backend": OPENAI, "arxiv": evil})
            assert r.status_code == 400, f"{evil!r} not rejected"
            assert "arxiv" in r.text.lower() or "arXiv" in r.text


def test_backends_endpoint_no_gate_when_unconfigured():
    get_settings.cache_clear()
    with TestClient(app) as c:
        info = {b["kind"]: b for b in c.get("/api/backends").json()}
        assert info["claude_cli"]["needs_password"] is False
