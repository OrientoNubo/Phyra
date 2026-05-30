"""Archive-to-phyra-archbase: name suggestion, copy + index regen, and
the route that ties a finished job to the sibling collection."""

import pytest
from fastapi.testclient import TestClient

from phyra_dualtrans.web import archive as arch
from phyra_dualtrans.web.app import app
from phyra_dualtrans.web.archive import (
    ArchiveError,
    archive_files,
    suggest_name,
)


def test_suggest_name_splits_arxiv_stem_and_detokenizes():
    # arXiv stems are already <YYMM>_<title>; the ': ' acronym separator
    # round-trips from '__'
    s = suggest_name("2402_Genie__Generative_Interactive_Environments")
    assert s["yymm"] == "2402"
    assert s["title"] == "Genie: Generative Interactive Environments"


def test_suggest_name_upload_stem_has_no_yymm():
    s = suggest_name("my_paper_draft")
    assert s["yymm"] == ""
    assert s["title"] == "my paper draft"


def _fake_generate_script(tmp_path):
    """A stand-in generate_index.py that just touches a marker so we can
    assert the regen ran (and exits 0)."""
    script = tmp_path / "script" / "generate_index.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    marker = tmp_path / "index.html"
    script.write_text(
        "from pathlib import Path\n"
        f"Path(r'{marker}').write_text('regenerated')\n"
    )
    return script, marker


def test_archive_files_copies_with_convention_and_regens(tmp_path):
    original = tmp_path / "src.pdf"
    dual = tmp_path / "src.dual.pdf"
    original.write_bytes(b"%PDF-1.4 orig")
    dual.write_bytes(b"%PDF-1.4 dual")
    collection = tmp_path / "collection"
    script, marker = _fake_generate_script(tmp_path)

    res = archive_files(
        original=original, dual=dual,
        yymm="2402", title="Genie: Generative Interactive Environments",
        lang_out="zh-TW", collection_dir=collection, generate_script=script,
    )

    stem = "2402_Genie_Generative_Interactive_Environments"
    assert res["stem"] == stem
    assert (collection / f"{stem}.pdf").read_bytes() == b"%PDF-1.4 orig"
    assert (collection / f"{stem}_bilingual.zh-TW.dual.pdf").exists()
    assert res["index_ok"] is True
    assert marker.read_text() == "regenerated"


def test_archive_files_rejects_bad_yymm_and_missing_source(tmp_path):
    original = tmp_path / "o.pdf"
    dual = tmp_path / "d.pdf"
    original.write_bytes(b"x")
    dual.write_bytes(b"x")
    coll = tmp_path / "c"
    script, _ = _fake_generate_script(tmp_path)

    with pytest.raises(ArchiveError) as ei:
        archive_files(original=original, dual=dual, yymm="24",
                      title="t", lang_out="zh-TW",
                      collection_dir=coll, generate_script=script)
    assert ei.value.status == 400

    with pytest.raises(ArchiveError) as ei2:
        archive_files(original=tmp_path / "nope.pdf", dual=dual,
                      yymm="2402", title="t", lang_out="zh-TW",
                      collection_dir=coll, generate_script=script)
    assert ei2.value.status == 409


def test_archbase_info_endpoint_shape():
    with TestClient(app) as c:
        r = c.get("/api/archbase").json()
        assert set(r) == {"enabled", "port"}
        assert isinstance(r["enabled"], bool)
        assert isinstance(r["port"], int)


def test_archive_route_end_to_end(tmp_path, monkeypatch):
    """POST /api/jobs/{id}/archive copies the job's PDFs into a configured
    archbase collection and reports success."""
    from phyra_dualtrans.models import TranslateParams
    from phyra_dualtrans.web import routes_jobs
    from phyra_dualtrans.web.jobs import Job

    collection = tmp_path / "collection"
    script, marker = _fake_generate_script(tmp_path)
    monkeypatch.setattr(routes_jobs, "archbase_paths",
                        lambda *a, **k: (collection, script))

    with TestClient(app) as c:
        mgr = app.state.manager
        wd = tmp_path / "job"
        wd.mkdir()
        orig = wd / "2402_NetLLM.pdf"
        dual = wd / "2402_NetLLM_bilingual.zh-TW.dual.pdf"
        orig.write_bytes(b"%PDF orig")
        dual.write_bytes(b"%PDF dual")
        job = Job(id="arch01", params=TranslateParams(lang_out="zh-TW"),
                  backend_redacted={}, cfg_json="", workdir=wd,
                  source_kind="arxiv", stem="2402_NetLLM")
        job.status = "succeeded"
        job.outputs = {"dual": str(dual), "original": str(orig)}
        mgr.jobs[job.id] = job

        # suggest endpoint splits the stem
        sug = c.get("/api/jobs/arch01/archive/suggest").json()
        assert sug["yymm"] == "2402" and sug["title"] == "NetLLM"

        r = c.post("/api/jobs/arch01/archive",
                   data={"yymm": "2402", "title": "NetLLM"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True and body["stem"] == "2402_NetLLM"
        assert (collection / "2402_NetLLM.pdf").exists()
        assert (collection / "2402_NetLLM_bilingual.zh-TW.dual.pdf").exists()
        assert marker.exists()

        mgr.jobs.pop("arch01", None)
