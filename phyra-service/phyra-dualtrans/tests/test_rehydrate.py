"""Restart rehydration: a finished job's workdir/job.json (or, lacking
that, a final dual on disk) is restored into the registry on startup so
the UI still lists and can download it after a server restart."""

from __future__ import annotations

import json

from phyra_dualtrans.config import get_settings
from phyra_dualtrans.models import TranslateParams
from phyra_dualtrans.web.jobs import Job, JobManager


def _jobsdir():
    jd = get_settings().jobs_dir
    jd.mkdir(parents=True, exist_ok=True)
    return jd


def _mk(d, *, meta=None, dual=None, mono=None, extra=None):
    d.mkdir(parents=True, exist_ok=True)
    if dual:
        (d / dual).write_bytes(b"%PDF-1.4 dual")
    if mono:
        (d / mono).write_bytes(b"%PDF-1.4 mono")
    for f in extra or []:
        (d / f).write_bytes(b"x")
    if meta is not None:
        (d / "job.json").write_text(json.dumps(meta), "utf-8")


def test_persist_then_rehydrate_roundtrip():
    jd = _jobsdir()
    wd = jd / "abc123"
    wd.mkdir(parents=True)
    (wd / "p_bilingual.zh-TW.dual.pdf").write_bytes(b"%PDF dual")
    (wd / "p_bilingual.zh-TW.mono.pdf").write_bytes(b"%PDF mono")

    job = Job(id="abc123", params=TranslateParams(distill=True),
              backend_redacted={"kind": "ollama"}, cfg_json="{}",
              workdir=wd, source_kind="upload", stem="p")
    job.status = "succeeded"
    job.outputs = {"dual": str(wd / "p_bilingual.zh-TW.dual.pdf"),
                   "mono": str(wd / "p_bilingual.zh-TW.mono.pdf")}
    JobManager()._persist(job)
    assert (wd / "job.json").is_file()

    m = JobManager()
    assert m.rehydrate() == 1
    r = m.get("abc123")
    assert r is not None and r.status == "succeeded" and r.stem == "p"
    assert r.params.distill is True
    assert r.backend_redacted == {"kind": "ollama"}
    assert r.outputs["dual"].endswith("p_bilingual.zh-TW.dual.pdf")
    assert r.outputs["mono"].endswith("p_bilingual.zh-TW.mono.pdf")


def test_running_status_becomes_failed_after_restart():
    jd = _jobsdir()
    _mk(jd / "j1",
        meta={"id": "j1", "stem": "s", "status": "running",
              "params": {}, "outputs": {}},
        dual=None)
    m = JobManager()
    m.rehydrate()
    j = m.get("j1")
    assert j is not None and j.status == "failed"
    assert "restart" in (j.error or "")


def test_no_meta_but_dual_present_is_synthesized():
    jd = _jobsdir()
    _mk(jd / "j2", dual="MyPaper_bilingual.zh-TW.dual.pdf",
        mono="MyPaper_bilingual.zh-TW.mono.pdf")
    m = JobManager()
    m.rehydrate()
    j = m.get("j2")
    assert j is not None and j.status == "succeeded"
    assert j.stem == "MyPaper"
    assert "dual" in j.outputs and "mono" in j.outputs


def test_dir_without_outputs_is_skipped():
    jd = _jobsdir()
    _mk(jd / "j3", extra=["x.no_refs.pdf", "child.log"])  # only junk
    m = JobManager()
    m.rehydrate()
    assert m.get("j3") is None


def test_rehydrate_does_not_clobber_live_jobs():
    jd = _jobsdir()
    _mk(jd / "live", meta={"id": "live", "status": "succeeded",
                           "params": {}, "outputs": {}})
    m = JobManager()
    sentinel = Job(id="live", params=TranslateParams(), backend_redacted={},
                   cfg_json="", workdir=jd / "live", source_kind="upload")
    sentinel.status = "running"
    m.jobs["live"] = sentinel
    m.rehydrate()
    assert m.get("live") is sentinel  # existing entry untouched


def test_cleanup_keeps_job_json():
    jd = _jobsdir()
    wd = jd / "c1"
    wd.mkdir(parents=True)
    for f in ("d_bilingual.zh-TW.dual.pdf", "d.no_refs.pdf",
              "child.log", "job.json", "slice_meta.json"):
        (wd / f).write_bytes(b"x")
    job = Job(id="c1", params=TranslateParams(), backend_redacted={},
              cfg_json="", workdir=wd, source_kind="upload", stem="d")
    job.outputs = {"dual": str(wd / "d_bilingual.zh-TW.dual.pdf")}
    JobManager()._cleanup_workdir(job)
    assert (wd / "job.json").exists()          # never dropped
    assert (wd / "slice_meta.json").exists()
    assert not (wd / "d.no_refs.pdf").exists()
    assert not (wd / "child.log").exists()
