"""Post-success workdir cleanup.

A finished job otherwise keeps ~90 MB of useless intermediates
(`*.no_refs*` sliced/BabelDOC files) forever. Stage E deletes them on
SUCCESS only; final dual/mono + slice_meta are always kept; the original
is kept unless PHYRA_DUALTRANS_DROP_ORIGINAL. The matching is substring-
based (not glob) so exotic stems like `2605_VGGT-$_Omega$` are safe.
"""

from __future__ import annotations

from pathlib import Path

from phyra_dualtrans.config import get_settings
from phyra_dualtrans.models import TranslateParams
from phyra_dualtrans.web.jobs import Job, JobManager

STEM = "2605_VGGT-$_Omega$"  # deliberately full of glob/regex metachars


def _populate(wd: Path) -> dict[str, Path]:
    files = {
        "original": wd / f"{STEM}.pdf",
        "sliced": wd / f"{STEM}.no_refs.pdf",
        "bd_dual": wd / f"{STEM}.no_refs.no_watermark.zh-TW.dual.pdf",
        "final_dual": wd / f"{STEM}_bilingual.zh-TW.dual.pdf",
        "final_mono": wd / f"{STEM}_bilingual.zh-TW.mono.pdf",
        "log": wd / "child.log",
        "meta": wd / "slice_meta.json",
    }
    for p in files.values():
        p.write_bytes(b"x")
    return files


def _job(wd: Path, files: dict[str, Path]) -> Job:
    job = Job(id="t", params=TranslateParams(), backend_redacted={},
              cfg_json="{}", workdir=wd, source_kind="upload")
    job.stem = STEM
    job.original_pdf = files["original"]
    job.outputs = {"dual": str(files["final_dual"]),
                   "mono": str(files["final_mono"])}
    return job


def test_cleanup_keeps_finals_drops_intermediates(tmp_path):
    files = _populate(tmp_path)
    JobManager()._cleanup_workdir(_job(tmp_path, files))

    assert not files["sliced"].exists()
    assert not files["bd_dual"].exists()
    assert not files["log"].exists()
    # kept
    assert files["final_dual"].exists()
    assert files["final_mono"].exists()
    assert files["meta"].exists()
    assert files["original"].exists()          # default: keep user input


def test_drop_original_also_removes_source(tmp_path, monkeypatch):
    monkeypatch.setenv("PHYRA_DUALTRANS_DROP_ORIGINAL", "1")
    get_settings.cache_clear()
    files = _populate(tmp_path)
    JobManager()._cleanup_workdir(_job(tmp_path, files))

    assert not files["original"].exists()      # opted in → gone
    assert files["final_dual"].exists()        # finals still safe
    assert files["final_mono"].exists()


def test_keep_intermediates_flag_parsed(monkeypatch):
    monkeypatch.setenv("PHYRA_DUALTRANS_KEEP_INTERMEDIATES", "1")
    get_settings.cache_clear()
    assert get_settings().keep_intermediates is True
    assert get_settings().drop_original is False    # independent default


def test_cleanup_never_raises_on_missing_workdir(tmp_path):
    files = _populate(tmp_path)
    job = _job(tmp_path, files)
    job.workdir = tmp_path / "gone"                  # does not exist
    JobManager()._cleanup_workdir(job)               # must not raise
