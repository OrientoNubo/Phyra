"""POST /api/translate/batch — ordered multi-input, strict chaining,
shared settings, password gate. create() is patched so no real
translation subprocess is spawned."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from phyra_dualtrans.config import get_settings
from phyra_dualtrans.models import TranslateParams
from phyra_dualtrans.web import jobs as jobs_mod
from phyra_dualtrans.web.app import app
from phyra_dualtrans.web.jobs import Job, JobManager

OPENAI = '{"kind":"openai","model":"gpt-4o","api_key":"k"}'
CLAUDE = '{"kind":"claude_cli","model":"sonnet"}'
PDF = b"%PDF-1.4 minimal"


@pytest.fixture
def recorder(monkeypatch):
    calls: list[dict] = []
    n = {"i": 0}

    def fake_create(self, **kw):
        n["i"] += 1

        class _J:
            id = f"job{n['i']}"
            stem = (kw.get("upload_name") or kw.get("arxiv") or "x")
        kw["_returned"] = _J
        calls.append(kw)
        return _J

    monkeypatch.setattr(jobs_mod.JobManager, "create", fake_create)
    return calls


def test_empty_batch_is_400(recorder):
    with TestClient(app) as c:
        r = c.post("/api/translate/batch", data={"backend": OPENAI})
        assert r.status_code == 400


def test_files_preserve_order_and_chain(recorder):
    with TestClient(app) as c:
        r = c.post(
            "/api/translate/batch",
            data={"backend": OPENAI, "lang_out": "zh-TW"},
            files=[
                ("file", ("a.pdf", PDF, "application/pdf")),
                ("file", ("b.pdf", PDF, "application/pdf")),
                ("file", ("c.pdf", PDF, "application/pdf")),
            ],
        )
        assert r.status_code == 201
        jobs = r.json()["jobs"]
        assert [j["stem"] for j in jobs] == ["a.pdf", "b.pdf", "c.pdf"]

    # first has no predecessor; each subsequent chained to the previous
    assert recorder[0]["after"] is None
    for i in range(1, len(recorder)):
        assert recorder[i]["after"] is recorder[i - 1]["_returned"]


def test_arxiv_textarea_expands_per_line(recorder):
    with TestClient(app) as c:
        r = c.post("/api/translate/batch", data={
            "backend": OPENAI,
            "arxiv": "2503.06132\n  \nhttps://arxiv.org/abs/2505.12345\n",
        })
        assert r.status_code == 201
    kinds = [k["source_kind"] for k in recorder]
    arx = [k["arxiv"] for k in recorder]
    assert kinds == ["arxiv", "arxiv"]                 # blank line skipped
    assert arx == ["2503.06132", "https://arxiv.org/abs/2505.12345"]


def test_shared_settings_applied(recorder):
    with TestClient(app) as c:
        c.post("/api/translate/batch", data={
            "backend": OPENAI, "lang_out": "ja", "distill": "true",
            "mono": "true", "qps": "5",
        }, files=[("file", ("p.pdf", PDF, "application/pdf"))])
    p: TranslateParams = recorder[0]["params"]
    assert p.lang_out == "ja" and p.distill is True
    assert p.mono is True and p.qps == 5


def test_claude_cli_batch_gated(monkeypatch, recorder):
    monkeypatch.setenv("PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD", "pw")
    get_settings.cache_clear()
    with TestClient(app) as c:
        r = c.post("/api/translate/batch", data={"backend": CLAUDE},
                   files=[("file", ("p.pdf", PDF, "application/pdf"))])
        assert r.status_code == 401
    assert recorder == []                              # gated before create


def test_done_event_gates_successor():
    """The ordering primitive: a job with _after blocks until the
    predecessor's _done_evt is set."""
    async def scenario():
        j1 = Job(id="1", params=TranslateParams(), backend_redacted={},
                 cfg_json="", workdir=None, source_kind="upload")
        j2 = Job(id="2", params=TranslateParams(), backend_redacted={},
                 cfg_json="", workdir=None, source_kind="upload")
        j2._after = j1._done_evt
        waiter = asyncio.create_task(j2._after.wait())
        await asyncio.sleep(0.02)
        assert not waiter.done()          # still blocked on predecessor
        j1._done_evt.set()                # predecessor terminal
        await asyncio.wait_for(waiter, timeout=1)
        assert waiter.done()

    asyncio.run(scenario())
