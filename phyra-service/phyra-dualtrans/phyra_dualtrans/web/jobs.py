"""
JobManager — registry + asyncio supervisor + per-job subprocess + SSE fan-out.

Each job's pipeline:
  A0 resolve input (arXiv download, if any)        [thread]
  A  slice_pdf — strip reference pages             [thread]
  B  translate_runner CHILD PROCESS                [subprocess; NDJSON]
  C  build_dual — stitch full-page-count dual+mono [thread]
  D  compress_pdf — Ghostscript / noop             [thread]
  E  cleanup — drop *.no_refs* + child.log         [thread; success only]

Stage B is the critical isolation boundary: the server never imports
BabelDOC; the child is the only thing allowed to os._exit (it kills only
itself). Cancel = proc.kill(), which is clean thanks to that isolation.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import shutil
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from ..config import get_settings
from ..models import JobView, TranslateParams
from ..pipeline.build_dual import build as build_dual
from ..pipeline.compress import compress_pdf
from ..pipeline.slice_pdf import slice_pdf
from ..vendor.resolve_input import detect_arxiv_id
from ..vendor.resolve_input import resolve as resolve_input
from ..vendor.resolve_input import sanitize_title_for_stem

SENTINEL = None  # closes an SSE subscriber queue
_TERMINAL = {"succeeded", "failed", "canceled"}


@dataclass
class Job:
    id: str
    params: TranslateParams
    backend_redacted: dict
    cfg_json: str  # BackendConfig JSON fed to the child via stdin (never in views)
    workdir: Path
    source_kind: str  # "upload" | "arxiv"
    arxiv: str | None = None
    original_pdf: Path | None = None
    stem: str = ""
    status: str = "queued"
    progress: dict = field(
        default_factory=lambda: {"stage": None, "stage_pct": 0.0,
                                 "overall_pct": 0.0}
    )
    outputs: dict = field(default_factory=dict)
    error: str | None = None
    compress_stats: dict | None = None
    # set once the job's PDFs have been copied into phyra-archbase; persisted
    # to job.json so the "already archived" mark survives a server restart.
    archived: bool = False
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    _subs: list[asyncio.Queue] = field(default_factory=list)
    _task: asyncio.Task | None = None
    _proc: asyncio.subprocess.Process | None = None
    # Batch ordering: a job set to run after another waits on the
    # predecessor's _done_evt before acquiring the concurrency semaphore,
    # so a batch runs strictly in submission order regardless of
    # asyncio.Semaphore fairness.
    _done_evt: asyncio.Event = field(default_factory=asyncio.Event)
    _after: asyncio.Event | None = None

    def view(self) -> JobView:
        return JobView(
            id=self.id,
            status=self.status,  # type: ignore[arg-type]
            stem=self.stem,
            params=self.params.model_dump(),
            backend=self.backend_redacted,
            progress=self.progress,
            outputs=self.outputs,
            error=self.error,
            compress_stats=self.compress_stats,
            archived=self.archived,
            created_at=self.created_at,
            started_at=self.started_at,
            finished_at=self.finished_at,
        )

    def snapshot_event(self) -> dict:
        return {
            "type": "snapshot",
            "status": self.status,
            "stem": self.stem,
            "progress": self.progress,
            "outputs": self.outputs,
            "error": self.error,
        }


class JobManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.jobs: dict[str, Job] = {}
        self._sem: asyncio.Semaphore | None = None

    @property
    def sem(self) -> asyncio.Semaphore:
        if self._sem is None:
            self._sem = asyncio.Semaphore(
                max(1, self.settings.max_concurrent_jobs)
            )
        return self._sem

    # ---- creation -------------------------------------------------------

    def create(
        self,
        *,
        params: TranslateParams,
        cfg_json: str,
        backend_redacted: dict,
        source_kind: str,
        upload_bytes: bytes | None = None,
        upload_name: str | None = None,
        arxiv: str | None = None,
        after: Job | None = None,
    ) -> Job:
        jid = uuid.uuid4().hex[:12]
        workdir = self.settings.jobs_dir / jid
        workdir.mkdir(parents=True, exist_ok=True)

        job = Job(
            id=jid,
            params=params,
            backend_redacted=backend_redacted,
            cfg_json=cfg_json,
            workdir=workdir,
            source_kind=source_kind,
            arxiv=arxiv,
        )
        if after is not None:
            job._after = after._done_evt

        if source_kind == "upload":
            stem = sanitize_title_for_stem(Path(upload_name or "paper").stem) \
                or "paper"
            src = workdir / f"{stem}.pdf"
            src.write_bytes(upload_bytes or b"")
            job.original_pdf = src
            job.stem = stem

        self.jobs[jid] = job
        job._task = asyncio.create_task(self._run(job))
        return job

    # ---- supervisor -----------------------------------------------------

    async def _run(self, job: Job) -> None:
        try:
            # Batch ordering: don't even contend for the semaphore until
            # the previous job in the batch has terminated.
            if job._after is not None:
                await job._after.wait()
            async with self.sem:
                job.status = "running"
                job.started_at = time.time()
                self._broadcast(job, {"type": "status", "status": "running"})

                lo = job.params.lang_out

                # A0 — resolve input (arXiv download)
                if job.source_kind == "arxiv":
                    # Defense-in-depth: never let resolve_input treat a
                    # non-arXiv string as a local path (LFI).
                    if detect_arxiv_id(job.arxiv or "") is None:
                        raise ValueError("invalid arXiv input")
                    info = await asyncio.to_thread(
                        resolve_input, job.arxiv or "",
                        override_out_dir=job.workdir,
                    )
                    job.original_pdf = Path(info["pdf_path"])
                    job.stem = info["stem"]
                # Expose the ORIGINAL pdf as a job output so the UI can
                # view/download it. It already lives in the workdir (same
                # directory as the translated PDFs); listing it in outputs
                # also pins it through cleanup (the keep-set). Honors
                # drop_original: when the operator opts to discard inputs,
                # no original is offered.
                if job.original_pdf and not self.settings.drop_original:
                    job.outputs["original"] = str(job.original_pdf)
                self._broadcast(
                    job, {"type": "stage_end", "stage": "input",
                          "stem": job.stem, "outputs": job.outputs}
                )

                stem = job.stem
                sliced = job.workdir / f"{stem}.no_refs.pdf"
                meta = job.workdir / "slice_meta.json"

                # A — slice references
                await asyncio.to_thread(
                    slice_pdf, job.original_pdf, None, sliced, meta
                )
                self._broadcast(
                    job, {"type": "stage_end", "stage": "slice"}
                )

                # B — translation child process
                bd_dual = await self._run_child(job, sliced)

                # C — build full-page-count dual (+ mono)
                final_dual = job.workdir / f"{stem}_bilingual.{lo}.dual.pdf"
                mono = (
                    job.workdir / f"{stem}_bilingual.{lo}.mono.pdf"
                    if job.params.mono else None
                )
                await asyncio.to_thread(
                    build_dual,
                    original_pdf=job.original_pdf,
                    babeldoc_dual_pdf=bd_dual,
                    slice_meta_path=meta,
                    out_pdf=final_dual,
                    lang_out=lo,
                    also_mono=mono,
                )
                job.outputs["dual"] = str(final_dual)
                if mono and mono.exists():
                    job.outputs["mono"] = str(mono)
                self._broadcast(job, {"type": "stage_end", "stage": "build"})

                # D — compress
                cs = await asyncio.to_thread(
                    compress_pdf, final_dual, job.params.compress,
                    dpi=job.params.dpi, preset=job.params.preset,
                )
                if mono and mono.exists():
                    await asyncio.to_thread(
                        compress_pdf, mono, job.params.compress,
                        dpi=job.params.dpi, preset=job.params.preset,
                    )
                job.compress_stats = cs

                # E — drop throwaway intermediates (success path ONLY;
                # a failed job keeps them + child.log for debugging).
                if not self.settings.keep_intermediates:
                    await asyncio.to_thread(self._cleanup_workdir, job)
                    self._broadcast(
                        job, {"type": "stage_end", "stage": "cleanup"}
                    )

                job.status = "succeeded"
                self._broadcast(
                    job, {"type": "done", "outputs": job.outputs,
                          "compress": cs}
                )
        except asyncio.CancelledError:
            job.status = "canceled"
            self._kill_proc(job)
            self._broadcast(job, {"type": "canceled"})
        except Exception as e:  # noqa: BLE001
            job.status = "failed"
            job.error = f"{e.__class__.__name__}: {str(e)[:300]}"
            self._broadcast(job, {"type": "error", "error": job.error})
        finally:
            job.finished_at = time.time()
            self._persist(job)
            job._done_evt.set()  # unblock the next job in a batch
            self._close(job)

    async def _run_child(self, job: Job, sliced: Path) -> Path:
        env = {
            **_os_environ(),
            "PHYRA_DUALTRANS_RETRY_WAIT_SEC": str(self.settings.retry_wait_sec),
            "PHYRA_DUALTRANS_MAX_ATTEMPTS": str(self.settings.max_attempts),
        }
        argv = [
            sys.executable, "-m", "phyra_dualtrans.pipeline.translate_runner",
            str(sliced), str(job.workdir),
            "--lang-in", job.params.lang_in,
            "--lang-out", job.params.lang_out,
            "--qps", str(job.params.qps),
        ]
        if job.params.compat:
            argv.append("--compat")
        if job.params.distill:
            argv.append("--distill")

        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        job._proc = proc

        proc.stdin.write(job.cfg_json.encode("utf-8"))
        await proc.stdin.drain()
        proc.stdin.close()

        log_path = job.workdir / "child.log"
        log_f = log_path.open("wb")
        stderr_task = asyncio.create_task(self._drain(proc.stderr, log_f))

        dual: str | None = None
        try:
            async for raw in proc.stdout:
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    log_f.write(b"[non-json stdout] " + raw)
                    continue
                t = ev.get("type")
                if t == "progress":
                    job.progress = {
                        "stage": ev.get("stage"),
                        "stage_pct": ev.get("stage_pct", 0.0),
                        "overall_pct": ev.get("overall_pct", 0.0),
                    }
                    self._broadcast(job, {"type": "progress",
                                          **job.progress})
                elif t == "finish":
                    dual = ev.get("dual_pdf")
                    self._broadcast(job, {"type": "stage_end",
                                          "stage": "translate"})
                elif t == "error":
                    job.error = ev.get("error")
                    self._broadcast(job, {"type": "error",
                                          "error": job.error})
                else:
                    # rate_limit / chunk_fallback / stage_end / started / backend
                    self._broadcast(job, ev)
        finally:
            rc = await proc.wait()
            with contextlib.suppress(Exception):
                await stderr_task
            log_f.close()
            job._proc = None

        if dual is None or rc != 0:
            raise RuntimeError(
                job.error or f"translation child exited rc={rc} "
                f"(see {log_path})"
            )
        return Path(dual)

    @staticmethod
    async def _drain(stream: asyncio.StreamReader, fh) -> None:
        while True:
            chunk = await stream.read(4096)
            if not chunk:
                break
            fh.write(chunk)
            fh.flush()

    # ---- SSE fan-out ----------------------------------------------------

    def _broadcast(self, job: Job, ev: dict) -> None:
        for q in list(job._subs):
            with contextlib.suppress(Exception):
                q.put_nowait(ev)

    def _close(self, job: Job) -> None:
        for q in list(job._subs):
            with contextlib.suppress(Exception):
                q.put_nowait(SENTINEL)

    async def subscribe(self, job: Job):
        """Async generator of SSE events for a job (snapshot first)."""
        q: asyncio.Queue = asyncio.Queue()
        job._subs.append(q)
        try:
            yield job.snapshot_event()
            if job.status in _TERMINAL:
                yield {"type": job.status if job.status != "succeeded"
                       else "done", "outputs": job.outputs,
                       "error": job.error}
                return
            while True:
                ev = await q.get()
                if ev is SENTINEL:
                    break
                yield ev
                if ev.get("type") in ("done", "error", "canceled"):
                    break
        finally:
            with contextlib.suppress(ValueError):
                job._subs.remove(q)

    # ---- control --------------------------------------------------------

    def _cleanup_workdir(self, job: Job) -> None:
        """Delete throwaway intermediates after a SUCCESSFUL job:
        ``*.no_refs*`` (sliced input + BabelDOC dual) and ``child.log``;
        also the original pdf when ``drop_original``. Final dual/mono and
        ``slice_meta.json`` are always kept. Never raises — cleanup must
        not fail a translation that already produced its output."""
        wd = job.workdir
        keep = {Path(p).name for p in job.outputs.values()}
        keep.add("slice_meta.json")
        keep.add("job.json")  # restart-rehydration metadata — never drop
        orig = Path(job.original_pdf).name if job.original_pdf else None
        try:
            entries = list(wd.iterdir())
        except OSError:
            return
        for p in entries:
            if p.name in keep or not p.is_file():
                continue
            is_intermediate = ".no_refs" in p.name or p.name == "child.log"
            is_original = orig is not None and p.name == orig
            if is_intermediate or (
                is_original and self.settings.drop_original
            ):
                with contextlib.suppress(OSError):
                    p.unlink()

    @staticmethod
    def _kill_proc(job: Job) -> None:
        if job._proc is not None and job._proc.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                job._proc.kill()

    # ---- persistence / restart rehydration -----------------------------

    def _persist(self, job: Job) -> None:
        """Write workdir/job.json so a finished job survives a restart.
        Best-effort: never fail a job over persistence."""
        try:
            meta = {
                "id": job.id,
                "stem": job.stem,
                "status": job.status,
                "source_kind": job.source_kind,
                "params": job.params.model_dump(),
                "backend": job.backend_redacted,
                "outputs": {k: Path(v).name
                            for k, v in job.outputs.items()},
                "error": job.error,
                "compress_stats": job.compress_stats,
                "archived": job.archived,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "finished_at": job.finished_at,
            }
            (job.workdir / "job.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), "utf-8"
            )
        except Exception:  # noqa: BLE001 — persistence must never raise
            pass

    def rehydrate(self) -> int:
        """Rebuild the in-memory registry from jobs_dir on startup so the
        UI still lists (and can download) finished jobs after a restart.
        Returns how many were restored."""
        base = self.settings.jobs_dir
        if not base.is_dir():
            return 0
        n = 0
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name in self.jobs:
                continue
            job = None
            mf = d / "job.json"
            if mf.is_file():
                job = self._job_from_meta(d, mf)
            if job is None:
                job = self._job_from_disk(d)
            if job is not None:
                self.jobs[job.id] = job
                n += 1
        return n

    def _job_from_meta(self, d: Path, mf: Path) -> Job | None:
        try:
            m = json.loads(mf.read_text("utf-8"))
        except Exception:  # noqa: BLE001
            return None
        try:
            params = TranslateParams.model_validate(m.get("params") or {})
        except Exception:  # noqa: BLE001
            params = TranslateParams()
        job = Job(
            id=d.name,
            params=params,
            backend_redacted=m.get("backend") or {},
            cfg_json="",  # never re-run a rehydrated job
            workdir=d,
            source_kind=m.get("source_kind") or "upload",
            stem=m.get("stem") or d.name,
        )
        status = m.get("status") or "succeeded"
        if status not in _TERMINAL:
            status = "failed"
            job.error = "interrupted by a server restart"
        job.status = status
        job.error = m.get("error") or job.error
        job.compress_stats = m.get("compress_stats")
        job.archived = bool(m.get("archived"))
        job.created_at = m.get("created_at") or job.created_at
        job.started_at = m.get("started_at")
        job.finished_at = m.get("finished_at")
        for kind, name in (m.get("outputs") or {}).items():
            p = d / name
            if p.exists():
                job.outputs[kind] = str(p)
        return job

    @staticmethod
    def _job_from_disk(d: Path) -> Job | None:
        """No job.json (pre-feature / interrupted) — synthesize a
        succeeded entry iff a final dual PDF is present."""
        duals = sorted(d.glob("*_bilingual.*.dual.pdf"))
        if not duals:
            return None
        dual = duals[0]
        stem = dual.name.split("_bilingual.")[0]
        job = Job(
            id=d.name, params=TranslateParams(), backend_redacted={},
            cfg_json="", workdir=d, source_kind="upload", stem=stem,
        )
        job.status = "succeeded"
        job.outputs["dual"] = str(dual)
        monos = sorted(d.glob("*_bilingual.*.mono.pdf"))
        if monos:
            job.outputs["mono"] = str(monos[0])
        # the original is any pdf that is neither a final dual/mono nor a
        # throwaway intermediate (kept in the same workdir).
        origs = [p for p in sorted(d.glob("*.pdf"))
                 if "_bilingual." not in p.name and ".no_refs" not in p.name]
        if origs:
            job.outputs["original"] = str(origs[0])
        try:
            job.created_at = job.finished_at = dual.stat().st_mtime
        except OSError:
            pass
        return job

    def get(self, jid: str) -> Job | None:
        return self.jobs.get(jid)

    def list_views(self) -> list[dict]:
        return [
            {
                "id": j.id, "status": j.status, "stem": j.stem,
                "progress": j.progress, "created_at": j.created_at,
            }
            for j in sorted(self.jobs.values(),
                            key=lambda x: x.created_at, reverse=True)
        ]

    async def cancel(self, jid: str) -> bool:
        job = self.jobs.get(jid)
        if not job or job.status in _TERMINAL:
            return False
        self._kill_proc(job)
        if job._task is not None:
            job._task.cancel()
        return True

    def delete(self, jid: str) -> bool:
        job = self.jobs.pop(jid, None)
        if not job:
            return False
        self._kill_proc(job)
        shutil.rmtree(job.workdir, ignore_errors=True)
        return True


def _os_environ() -> dict:
    import os

    return dict(os.environ)
