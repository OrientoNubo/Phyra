"""
Context distillation — a one-shot pre-pass before BabelDOC translation.

BabelDOC translates one paragraph per LLM call with NO document context,
so terminology drifts across the paper and each call cannot "see" the
rest. Feeding the whole document into every call is impossible on a
32 K-context local model.

Instead we do ONE pre-pass: read the (refs-stripped) PDF text, ask the
SAME model for a compact "translation guide" (domain, a recurring-term
glossary with preferred target translations, proper nouns to keep in
English, style notes), then inject that small fixed guide into every
segment's system prompt. Result: document-wide consistency at a small
fixed prompt cost, well within a small context window.

Distillation must NEVER fail the job: any error → return None and
translation proceeds exactly as before (just without the guide).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

log = logging.getLogger("phyra-dualtrans.distill")

DEFAULT_MAX_CHARS = 24_000  # ~8K tokens of source → safe inside 32K ctx


def extract_pdf_text(pdf_path: str | Path, max_chars: int) -> str:
    """Concatenated page text, capped to `max_chars` (head of the doc —
    title/abstract/intro/method carry the terminology that matters)."""
    import fitz  # PyMuPDF (already a dependency)

    doc = fitz.open(str(pdf_path))
    parts: list[str] = []
    total = 0
    try:
        for page in doc:
            t = page.get_text() or ""
            if not t:
                continue
            parts.append(t)
            total += len(t)
            if total >= max_chars:
                break
    finally:
        doc.close()
    return "".join(parts)[:max_chars].strip()


def distill_system_prompt(lang_out: str) -> str:
    return (
        "You build a CONCISE translation guide for a scientific paper. "
        f"It will be reused while translating the paper into {lang_out}. "
        "Be terse and high-signal: only what keeps terminology consistent "
        "and correct across the whole paper. No preamble, no markdown "
        "headers beyond the four labels requested, no commentary."
    )


def distill_user_prompt(text: str, lang_out: str) -> str:
    return (
        "From the paper text below, produce a guide with EXACTLY these "
        "four sections, compact, total under ~500 words:\n"
        "DOMAIN: one line — the paper's field and topic.\n"
        f"GLOSSARY: up to 40 lines `English term => {lang_out} term`, only "
        "recurring/important technical terms whose translation must stay "
        "consistent.\n"
        "KEEP-IN-ENGLISH: comma-separated proper nouns, method/model names, "
        "acronyms that must stay verbatim (not translated).\n"
        "STYLE: 1-3 lines of target-language conventions to apply "
        "(e.g. Taiwan terminology).\n\n"
        "PAPER TEXT:\n" + text
    )


def distill_context(
    llm,
    pdf_path: str | Path,
    lang_out: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    emit: Callable[..., None] | None = None,
) -> str | None:
    """Run the pre-pass. Returns the guide string, or None on any
    failure / empty input (caller then translates without a guide)."""
    _emit = emit or (lambda **kw: None)
    try:
        text = extract_pdf_text(pdf_path, max_chars)
    except Exception as e:  # noqa: BLE001
        log.warning("distill: text extract failed: %s", e)
        return None
    if len(text) < 200:  # nothing useful to distill from
        return None

    _emit(type="distill", stage="start", chars=len(text))
    try:
        guide = llm.complete(
            distill_system_prompt(lang_out),
            distill_user_prompt(text, lang_out),
        )
    except Exception as e:  # noqa: BLE001 — never fail the job
        log.warning("distill: model call failed (%s); continuing without",
                    e.__class__.__name__)
        _emit(type="distill", stage="skipped", reason=str(e)[:160])
        return None

    guide = (guide or "").strip()
    if not guide:
        _emit(type="distill", stage="skipped", reason="empty guide")
        return None
    _emit(type="distill", stage="done", guide_chars=len(guide))
    log.info("distill: guide ready (%d chars)", len(guide))
    return guide
