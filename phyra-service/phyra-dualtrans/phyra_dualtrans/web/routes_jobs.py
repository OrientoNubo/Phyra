"""Job status / SSE / download / cancel / delete / archive."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query
from fastapi.responses import FileResponse, Response

from ..config import archbase_paths
from .archive import ArchiveError, archive_files, suggest_name
from .deps import get_manager
from .jobs import JobManager
from .sse import sse_response

router = APIRouter()


@router.get("/api/jobs")
def list_jobs(m: JobManager = Depends(get_manager)) -> list[dict]:
    return m.list_views()


@router.get("/api/jobs/{jid}")
def get_job(jid: str, m: JobManager = Depends(get_manager)) -> dict:
    job = m.get(jid)
    if not job:
        raise HTTPException(404, "no such job")
    return job.view().model_dump()


@router.get("/api/jobs/{jid}/events")
async def job_events(jid: str, m: JobManager = Depends(get_manager)):
    job = m.get(jid)
    if not job:
        raise HTTPException(404, "no such job")
    return sse_response(m.subscribe(job))


@router.get("/api/jobs/{jid}/download")
def download(
    jid: str,
    kind: str = Query("dual", pattern="^(dual|mono|original)$"),
    inline: bool = Query(
        False,
        description="serve inline (view in browser) instead of forcing a "
                    "download",
    ),
    m: JobManager = Depends(get_manager),
):
    job = m.get(jid)
    if not job:
        raise HTTPException(404, "no such job")
    path = job.outputs.get(kind)
    if not path or not Path(path).exists():
        raise HTTPException(404, f"{kind} PDF not ready")
    return FileResponse(
        path, media_type="application/pdf", filename=Path(path).name,
        content_disposition_type="inline" if inline else "attachment",
    )


@router.post("/api/jobs/{jid}/cancel")
async def cancel(jid: str, m: JobManager = Depends(get_manager)) -> dict:
    if not await m.cancel(jid):
        raise HTTPException(409, "job is not running / not cancelable")
    return {"status": "canceled"}


@router.get("/api/jobs/{jid}/archive/suggest")
def archive_suggest(jid: str, m: JobManager = Depends(get_manager)) -> dict:
    """Best-guess {yymm, title} to prefill the archive dialog, plus
    whether the archive is reachable at all."""
    job = m.get(jid)
    if not job:
        raise HTTPException(404, "no such job")
    return {"enabled": archbase_paths() is not None, **suggest_name(job.stem)}


@router.post("/api/jobs/{jid}/archive")
def archive(
    jid: str,
    yymm: str = Form(...),
    title: str = Form(...),
    m: JobManager = Depends(get_manager),
) -> dict:
    """Copy this job's original + dual PDF into the sibling
    phyra-archbase collection (under its naming convention) and refresh
    its index."""
    job = m.get(jid)
    if not job:
        raise HTTPException(404, "no such job")
    if job.status != "succeeded":
        raise HTTPException(409, "only a succeeded job can be archived")

    paths = archbase_paths()
    if paths is None:
        raise HTTPException(
            503,
            "phyra-archbase is not configured "
            "(set PHYRA_DUALTRANS_ARCHBASE_DIR)",
        )
    collection_dir, generate_script = paths

    original = job.outputs.get("original")
    dual = job.outputs.get("dual")
    if not original:
        raise HTTPException(
            409, "no original PDF on this job (drop_original?)"
        )
    if not dual:
        raise HTTPException(409, "no dual PDF on this job")

    try:
        result = archive_files(
            original=Path(original),
            dual=Path(dual),
            yymm=yymm,
            title=title,
            lang_out=job.params.lang_out,
            collection_dir=collection_dir,
            generate_script=generate_script,
        )
    except ArchiveError as e:
        raise HTTPException(e.status, e.message) from e

    # mark as archived (re-archiving is a harmless overwrite, but the UI
    # shows it's already been saved); persist so the mark survives a restart
    job.archived = True
    m._persist(job)
    return {"ok": True, **result}


@router.delete("/api/jobs/{jid}", status_code=204)
def delete(jid: str, m: JobManager = Depends(get_manager)):
    if not m.delete(jid):
        raise HTTPException(404, "no such job")
    return Response(status_code=204)
