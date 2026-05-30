"""
Translation subprocess entrypoint — the os._exit isolation boundary.

The FastAPI server NEVER imports BabelDOC and never runs this in-process.
For every job it spawns:

    python -m phyra_dualtrans.pipeline.translate_runner \
        <input.pdf> <output_dir> --lang-in en --lang-out zh-TW --qps 2

The BackendConfig (incl. api_key) is fed as one JSON object on STDIN so it
never appears in argv / `ps`. Progress is written to STDOUT as
line-delimited JSON (NDJSON); all logging goes to STDERR.

BabelDOC 0.5.24 leaves non-daemon executor threads alive after it
finishes, stalling asyncio teardown ~20 min. Once the dual PDF is on disk
that is pointless, so this process force-exits with os._exit — which is
SAFE here because it only kills this child, never the server.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import threading
from pathlib import Path

# Logging → stderr only. STDOUT is reserved for NDJSON.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("phyra-dualtrans.runner")

_emit_lock = threading.Lock()


def emit(**payload) -> None:
    """Write one NDJSON event to stdout. Thread-safe (called from
    BabelDOC's worker threads and the asyncio loop)."""
    line = json.dumps(payload, ensure_ascii=False)
    with _emit_lock:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


def _force_exit(code: int) -> None:
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)


def _read_backend_config():
    from ..backends.base import BackendConfig

    raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("no BackendConfig JSON on stdin")
    return BackendConfig.model_validate_json(raw)


async def run(args: argparse.Namespace) -> None:
    # Imported here so import failures still get reported as an NDJSON error
    # rather than crashing before the protocol starts.
    from babeldoc.format.pdf.high_level import async_translate, init
    from babeldoc.format.pdf.translation_config import (
        TranslationConfig,
        WatermarkOutputMode,
    )

    from ..backends import get_backend
    from .babeldoc_translator import (
        BabelDocTranslator,
        translation_effectively_failed,
    )
    from .distill import DEFAULT_MAX_CHARS, distill_context
    from .il_filter import patch_high_level_il_translator

    cfg = _read_backend_config()
    emit(type="backend", kind=cfg.kind, model=cfg.model)

    llm = get_backend(cfg)

    wait_seconds = int(os.environ.get("PHYRA_DUALTRANS_RETRY_WAIT_SEC", 10))
    max_attempts = int(os.environ.get("PHYRA_DUALTRANS_MAX_ATTEMPTS", 5))

    # BabelDOC's BaseTranslator persistently caches WHATEVER do_translate()
    # returns — including the source-text fallback we emit when a backend
    # call fails — keyed (engine, params, text) with NO guard
    # (translator.py:136-138). One earlier failed run (e.g. a wrong Base
    # URL → every call times out → every segment falls back to source)
    # therefore poisons ~/.cache/babeldoc/cache.v1.db, and EVERY later run
    # of that paper gets cache HITS that return the English source:
    # do_translate() never runs, translator.stats stays (0,0), the
    # fail-loud guard is blind, and the job 'succeeds' with an all-English
    # PDF (the reported 2604_Geometric bug). A local backend re-running is
    # cheap; a silently-wrong PDF is not acceptable → cache OFF by default.
    # Opt back in with PHYRA_DUALTRANS_USE_CACHE=1 only when every backend
    # is known-good and cross-run reuse is wanted.
    use_cache = os.environ.get("PHYRA_DUALTRANS_USE_CACHE", "0") == "1"

    # Optional one-shot context distillation (pre-pass). Never fatal:
    # distill_context returns None on any failure and we translate as
    # before. Done BEFORE init() so its model call isn't tangled with
    # BabelDOC's executor.
    guide: str | None = None
    if args.distill:
        max_chars = int(os.environ.get(
            "PHYRA_DUALTRANS_DISTILL_MAX_CHARS", DEFAULT_MAX_CHARS))
        guide = distill_context(
            llm, Path(args.input_pdf).resolve(), args.lang_out,
            max_chars=max_chars, emit=emit,
        )

    init()

    # Apply the per-paragraph keep-source policy: only the References
    # section, figure/table CONTENT, formulas and running headers are
    # kept verbatim; captions and all body text are translated. This
    # replaces the unreliable page-level reference slicer (which both
    # over- and under-skipped, and produced grey placeholder pages
    # instead of leaving references 原樣). Set PHYRA_DUALTRANS_TRANSLATE_ALL=1
    # to disable the policy (translate every paragraph — old behaviour).
    translate_all = os.environ.get(
        "PHYRA_DUALTRANS_TRANSLATE_ALL", "0"
    ) == "1"
    if not translate_all:
        patch_high_level_il_translator(skip_references=True)
    emit(type="policy", keep_source=not translate_all)

    translator = BabelDocTranslator(
        lang_in=args.lang_in,
        lang_out=args.lang_out,
        llm=llm,
        emit=emit,
        wait_seconds=wait_seconds,
        max_attempts=max_attempts,
        guide=guide,
        ignore_cache=not use_cache,
    )
    emit(type="cache", enabled=use_cache)
    tcfg = TranslationConfig(
        translator=translator,
        input_file=str(Path(args.input_pdf).resolve()),
        lang_in=args.lang_in,
        lang_out=args.lang_out,
        doc_layout_model=None,
        output_dir=str(Path(args.output_dir).resolve()),
        no_dual=False,
        no_mono=True,  # dual only; mono is built later by build_dual
        watermark_output_mode=WatermarkOutputMode.NoWatermark,
        qps=args.qps,
        pool_max_workers=args.qps,
        skip_clean=False,
        auto_extract_glossary=False,
        enhance_compatibility=args.compat,
    )
    log.info(
        "translate %s → %s (lang_out=%s qps=%d compat=%s backend=%s/%s)",
        args.input_pdf, args.output_dir, args.lang_out, args.qps,
        args.compat, cfg.kind, cfg.model,
    )
    emit(type="started", lang_out=args.lang_out, qps=args.qps)

    async for ev in async_translate(tcfg):
        et = ev.get("type")
        if et == "progress_update":
            emit(
                type="progress",
                stage=ev.get("stage"),
                stage_pct=round(float(ev.get("stage_progress", 0)), 1),
                overall_pct=round(float(ev.get("overall_progress", 0)), 1),
            )
        elif et == "progress_end":
            emit(type="stage_end", stage=ev.get("stage"))
        elif et == "finish":
            r = ev["translate_result"]
            dual = r.no_watermark_dual_pdf_path or r.dual_pdf_path
            calls, fallbacks = translator.stats
            if translation_effectively_failed(calls, fallbacks):
                # Every (or ~all) segment fell back to source → the
                # backend is unreachable/broken (commonly a wrong Base
                # URL). Do NOT 'succeed' with an all-English PDF.
                emit(
                    type="error",
                    error=(
                        f"backend produced no translations: "
                        f"{fallbacks}/{calls} segments fell back to the "
                        f"source text. The model endpoint is unreachable "
                        f"or rejecting every request — check the backend "
                        f"Base URL / that the model is running."
                    ),
                )
                _force_exit(1)
            emit(
                type="finish",
                dual_pdf=str(dual),
                total_seconds=round(float(getattr(r, "total_seconds", 0)), 1),
            )
            # dual.pdf is on disk — force-exit (kills only this child).
            _force_exit(0)
        elif et == "error":
            emit(type="error", error=str(ev.get("error")))
            _force_exit(1)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="phyra-dualtrans translation child")
    p.add_argument("input_pdf")
    p.add_argument("output_dir")
    p.add_argument("--lang-in", default="en")
    p.add_argument("--lang-out", default="zh-TW")
    p.add_argument("--qps", type=int, default=2)
    p.add_argument("--compat", action="store_true")
    p.add_argument("--distill", action="store_true",
                   help="run the context-distillation pre-pass")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args))
        # async_translate normally force-exits on finish/error; reaching here
        # means it returned without either — treat as failure.
        emit(type="error", error="translation ended without a finish event")
        _force_exit(1)
    except BaseException as e:  # noqa: BLE001 — must surface as NDJSON
        emit(type="error", error=f"{e.__class__.__name__}: {str(e)[:300]}")
        _force_exit(1)


if __name__ == "__main__":
    main()
