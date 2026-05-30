from fastapi.testclient import TestClient

from phyra_dualtrans.web.app import app


def test_healthz_and_backends():
    with TestClient(app) as c:
        h = c.get("/healthz").json()
        assert h["ok"] is True and "version" in h
        kinds = {b["kind"] for b in c.get("/api/backends").json()}
        assert kinds == {"openai", "ollama", "claude_cli"}


def test_settings_is_readonly_builtin_no_secrets():
    with TestClient(app) as c:
        s = c.get("/api/settings").json()
        assert s["backend"] == "ollama"
        assert s["model"] == "qwen3-32b-trans"
        assert "api_key" not in s             # secrets never echoed
        assert "base_url" not in s            # operator/env only
        # no server-side, API-writable settings file exists anymore
        assert c.put("/api/settings", json={"backend": "openai"}
                     ).status_code in (404, 405)


def test_ollama_models_endpoint_graceful():
    with TestClient(app) as c:
        r = c.get("/api/backends/ollama/models?host=http://127.0.0.1:1").json()
        assert r["available"] is False


def test_preflight_shape():
    with TestClient(app) as c:
        r = c.get("/api/preflight?backend=claude_cli&lang_out=zh-TW&compress=off").json()
        assert "ok" in r and isinstance(r["checks"], list)
        assert any(ck["name"] == "babeldoc" for ck in r["checks"])


def test_preflight_uses_supplied_ollama_base_url():
    """Regression: preflight must probe the USER's Base URL, not the
    default :11434 (the reported 'ollama not reachable at
    localhost:11434' while the form said :18763)."""
    with TestClient(app) as c:
        ck = {x["name"]: x for x in c.get(
            "/api/preflight?backend=ollama&base_url=http://127.0.0.1:18763/v1"
        ).json()["checks"]}
        d = ck["ollama:reachable"]["detail"]
        assert "18763" in d and "11434" not in d        # honored the input

        # no base_url → falls back to the default host (unchanged)
        ck2 = {x["name"]: x for x in c.get(
            "/api/preflight?backend=ollama").json()["checks"]}
        assert "11434" in ck2["ollama:reachable"]["detail"]


def test_translate_requires_input():
    with TestClient(app) as c:
        r = c.post("/api/translate", data={
            "backend": '{"kind":"claude_cli","model":"sonnet"}',
        })
        assert r.status_code == 400


def test_unknown_job_404():
    with TestClient(app) as c:
        assert c.get("/api/jobs/deadbeef").status_code == 404


def test_download_original_kind_and_inline_disposition(tmp_path):
    """The Jobs UI must serve the ORIGINAL pdf and be able to open any
    output INLINE (view in the browser) instead of forcing a download."""
    from phyra_dualtrans.models import TranslateParams
    from phyra_dualtrans.web.jobs import Job

    with TestClient(app) as c:
        mgr = app.state.manager
        wd = tmp_path
        orig = wd / "paper.pdf"
        dual = wd / "paper_bilingual.zh-TW.dual.pdf"
        orig.write_bytes(b"%PDF-1.4 original")
        dual.write_bytes(b"%PDF-1.4 dual")
        job = Job(id="abc123", params=TranslateParams(), backend_redacted={},
                  cfg_json="", workdir=wd, source_kind="upload", stem="paper")
        job.status = "succeeded"
        job.outputs = {"dual": str(dual), "original": str(orig)}
        mgr.jobs[job.id] = job

        # original is downloadable and defaults to attachment
        r = c.get("/api/jobs/abc123/download?kind=original")
        assert r.status_code == 200
        assert r.headers["content-disposition"].startswith("attachment")

        # inline=1 → served for in-browser viewing
        r2 = c.get("/api/jobs/abc123/download?kind=dual&inline=1")
        assert r2.status_code == 200
        assert r2.headers["content-disposition"].startswith("inline")

        # unknown kind is rejected by the route pattern
        assert c.get("/api/jobs/abc123/download?kind=bogus").status_code == 422
        mgr.jobs.pop("abc123", None)
