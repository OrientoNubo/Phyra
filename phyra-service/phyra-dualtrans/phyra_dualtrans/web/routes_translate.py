"""POST /api/translate (single) and /api/translate/batch (ordered many)."""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from ..config import check_backend_password, resolve_backend
from ..models import BackendInput, TranslateParams
from ..vendor.resolve_input import detect_arxiv_id
from .deps import get_manager
from .jobs import JobManager

router = APIRouter()


def _resolve(backend_json: str, admin_password: str, **params_kw):
    """Shared: parse backend, enforce the claude_cli password gate, build
    (TranslateParams, BackendConfig). Raises HTTPException on bad input."""
    try:
        bi = BackendInput.model_validate_json(backend_json)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"invalid backend JSON: {e}") from e

    # ollama / claude_cli spend the operator's own machine (local GPU /
    # Claude quota) → optional shared-password gate. openai is never
    # gated (the caller supplies the key). No-op when unconfigured.
    if not check_backend_password(bi.kind, admin_password):
        raise HTTPException(
            401, f"the {bi.kind} backend requires the admin password"
        )

    params = TranslateParams(**params_kw)
    cfg = resolve_backend(
        kind=bi.kind, model=bi.model, base_url=bi.base_url,
        api_key=bi.api_key, extra_headers=bi.extra_headers,
        think=bi.think,
    )
    return params, cfg


def _params_kw(form, *, default_compress="lossy"):
    """Pull the shared translate settings out of a form mapping."""
    def b(k, d=False):
        v = form.get(k)
        return str(v).lower() in ("1", "true", "on", "yes") if v is not None else d

    def i(k, d):
        try:
            return int(form.get(k, d))
        except (TypeError, ValueError):
            return d

    return dict(
        lang_in=form.get("lang_in", "en") or "en",
        lang_out=form.get("lang_out", "zh-TW") or "zh-TW",
        qps=i("qps", 2),
        compat=b("compat"),
        compress=form.get("compress", default_compress) or default_compress,
        dpi=i("dpi", 150),
        preset=form.get("preset", "ebook") or "ebook",
        mono=b("mono"),
        distill=b("distill"),
    )


@router.post("/api/translate", status_code=201)
async def translate(
    manager: JobManager = Depends(get_manager),
    file: UploadFile | None = File(None),
    arxiv: str | None = Form(None),
    lang_in: str = Form("en"),
    lang_out: str = Form("zh-TW"),
    qps: int = Form(2),
    compat: bool = Form(False),
    compress: str = Form("lossy"),
    dpi: int = Form(150),
    preset: str = Form("ebook"),
    mono: bool = Form(False),
    distill: bool = Form(False),
    backend: str = Form(...),
    admin_password: str = Form(""),
) -> dict:
    params, cfg = _resolve(
        backend, admin_password,
        lang_in=lang_in, lang_out=lang_out, qps=qps, compat=compat,
        compress=compress, dpi=dpi, preset=preset, mono=mono,
        distill=distill,
    )

    has_file = file is not None and bool((file.filename or "").strip())
    if has_file:
        data = await file.read()  # type: ignore[union-attr]
        if not data or b"%PDF-" not in data[:1024]:
            raise HTTPException(400, "uploaded file does not look like a PDF")
        job = manager.create(
            params=params, cfg_json=cfg.child_json(),
            backend_redacted=cfg.redacted(), source_kind="upload",
            upload_bytes=data, upload_name=file.filename,  # type: ignore[union-attr]
        )
    elif arxiv and arxiv.strip():
        # Must be a real arXiv id/URL. resolve_input() otherwise treats
        # an arbitrary string as a LOCAL filesystem path — on this
        # unauthenticated service that is an arbitrary-file read (LFI).
        if detect_arxiv_id(arxiv.strip()) is None:
            raise HTTPException(
                400, "not a valid arXiv id or arxiv.org URL"
            )
        job = manager.create(
            params=params, cfg_json=cfg.child_json(),
            backend_redacted=cfg.redacted(), source_kind="arxiv",
            arxiv=arxiv.strip(),
        )
    else:
        raise HTTPException(
            400, "provide either a PDF file or an arXiv URL / id"
        )

    return {"job_id": job.id, "stem": job.stem}


@router.post("/api/translate/batch", status_code=201)
async def translate_batch(
    request: Request,
    manager: JobManager = Depends(get_manager),
) -> dict:
    """Many inputs (PDF uploads and/or arXiv ids), processed strictly in
    submission order. Order is taken from the multipart field order
    (Starlette preserves it across keys); an `arxiv` textarea is expanded
    line by line at its position. Jobs are chained so job N starts only
    after job N-1 reaches a terminal state."""
    form = await request.form()
    backend = form.get("backend")
    if not backend:
        raise HTTPException(400, "missing backend")
    params, cfg = _resolve(
        str(backend), str(form.get("admin_password", "")),
        **_params_kw(form),
    )

    # Ordered (kind, value) list, honoring multipart field order.
    ordered: list[tuple[str, object]] = []
    for k, v in form.multi_items():
        if k == "file" and hasattr(v, "filename") and \
                (getattr(v, "filename", "") or "").strip():
            ordered.append(("upload", v))
        elif k == "arxiv" and isinstance(v, str):
            for line in v.splitlines():
                s = line.strip()
                if s:
                    ordered.append(("arxiv", s))

    if not ordered:
        raise HTTPException(
            400, "provide at least one PDF file or arXiv id"
        )

    created: list[dict] = []
    prev = None
    for kind, val in ordered:
        if kind == "upload":
            data = await val.read()  # type: ignore[union-attr]
            if not data or b"%PDF-" not in data[:1024]:
                continue  # skip a non-PDF; keep the rest of the batch
            job = manager.create(
                params=params, cfg_json=cfg.child_json(),
                backend_redacted=cfg.redacted(), source_kind="upload",
                upload_bytes=data,
                upload_name=getattr(val, "filename", "paper.pdf"),
                after=prev,
            )
        else:
            # LFI guard: a non-arXiv string would be read as a local
            # path by resolve_input(). Skip it (keep the rest).
            if detect_arxiv_id(str(val)) is None:
                continue
            job = manager.create(
                params=params, cfg_json=cfg.child_json(),
                backend_redacted=cfg.redacted(), source_kind="arxiv",
                arxiv=str(val), after=prev,
            )
        created.append({"job_id": job.id, "stem": job.stem})
        prev = job

    if not created:
        raise HTTPException(400, "no valid PDF / arXiv inputs in the batch")
    return {"jobs": created}
