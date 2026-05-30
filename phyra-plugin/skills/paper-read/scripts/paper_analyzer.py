"""
paper-analyzer (v0.8.0) — produce a structured Markdown analysis of an
academic paper. Replaces the v0.7 phyra_analyzer.py JSON-driven path.

5-call split (run in parallel by default; --nt forces serial):
  A1 OVERVIEW    — §1 Basic Information, §2 Research Overview
  A2 SECTIONS    — §3 Section Walkthrough
  A3 CRITIC      — §4 Critical Profile, §7 Phyra's Judgment, §8 Open Questions
  A4 METHOD      — §5 Methodology Deep Dive (multimodal: main_pipeline_figure)
  A5 EXPERIMENTS — §6 Experiments

Inputs:
  - source PDF
  - PARSED_PAPER.md (from paper-parser)
  - BIBLIO.json (from paper-bibliographer)
  - figures/ dir (from extract_figures.py) — optional
  - lang_out

Output:
  - .phyra/reports/<slug>/analysis.<lang>.md (final, merged)
  - .phyra/.cache/<slug>/sections/{A1..A5}.md (partial, kept for debug)
  - .phyra/.cache/<slug>/_token_usage.jsonl (per-call usage records)

Usage:
  uv run --with pymupdf python paper_analyzer.py \\
      <source.pdf> <PARSED_PAPER.md> <BIBLIO.json> \\
      <out_analysis.md> <lang_out> [--nt]
"""

import argparse
import base64
import datetime as _dt
import json
import logging
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import fitz  # PyMuPDF

# Local retry harness — sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _retry import RateLimitError, is_rate_limit_response, retry_call  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("paper-analyzer")

CALL_TIMEOUT_SEC = 1500           # 25 min per call (dense math papers)
MAX_PDF_TEXT_PER_CALL = 90_000    # ~90KB context, fits comfortably under 200K tokens

SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------
#
# Prompt templates live alongside this file in prompts/*.md so they can be
# audited and version-controlled independently of the orchestration logic.
# Each constant below loads its file exactly once at import time (read_text
# is called during module load), so callers see the same module-level cache
# they did before externalisation.

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------

_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _sanitize(s: str) -> str:
    return _CTRL_RE.sub("", s)


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def claude_bin() -> str:
    p = shutil.which("claude")
    if not p:
        raise RuntimeError("`claude` not found in PATH. Run preflight.py first.")
    return p


# Claude CLI embeds attachments as `data:image/...;base64,...` text in the
# stdin prompt, and the full base64 string is tokenized as ordinary text.
# A 756KB PNG → ~1M base64 chars → ~1M context tokens, which by itself
# exhausts the 1M-context Sonnet window and trips a `prompt_too_long`
# 400. We rescale every image attachment to a bounded edge length before
# encoding so the base64 footprint stays well below 200K tokens.
_ATTACH_MAX_EDGE_PX = 1280
_ATTACH_JPEG_QUALITY = 82


def _encode_image_attachment(path: Path) -> tuple[str, str]:
    """Return (mime, base64) for a figure attachment, downscaled with fitz.

    fitz.Pixmap.shrink halves dimensions per call, so the smallest size we
    can land on is somewhere in [target, 2·target). Halving while the
    longest edge still exceeds target gives the closest fit.
    """
    pm = fitz.Pixmap(str(path))
    while max(pm.width, pm.height) > _ATTACH_MAX_EDGE_PX:
        pm.shrink(1)
    if pm.alpha:
        pm = fitz.Pixmap(fitz.csRGB, pm)
    jpg = pm.tobytes(output="jpg", jpg_quality=_ATTACH_JPEG_QUALITY)
    return ("image/jpeg", base64.b64encode(jpg).decode("ascii"))


def _record_usage(out_path: Path, label: str, usage: dict, cost_usd: float | None) -> None:
    try:
        log_path = out_path.parent / "_token_usage.jsonl"
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "label": label,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            "cost_usd": cost_usd,
        }
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:  # never let usage tracking break the pipeline
        log.debug("usage log skipped: %s", e)


def _call_claude_once(prompt: str, system_prompt: str, *,
                      label: str,
                      usage_log_path: Path,
                      attachments: list[Path] | None,
                      timeout_sec: int) -> str:
    """One attempt at claude -p. Raises RateLimitError on rate-limit response,
    other RuntimeError on non-zero exit."""
    user_prompt = prompt
    if attachments:
        for att in attachments:
            if not att.exists():
                log.warning("[%s] attachment missing: %s — skipping", label, att)
                continue
            mime, data = _encode_image_attachment(att)
            user_prompt += (
                f"\n\n![{att.name}](data:{mime};base64,{data})\n"
            )

    cmd = [
        claude_bin(), "-p",
        "--append-system-prompt", _sanitize(system_prompt),
        "--output-format", "json",
    ]
    # User prompt goes via stdin to avoid the OS argv limit (~128KB).
    # Multimodal attachments embedded as base64 routinely exceed that.
    t0 = time.monotonic()
    try:
        res = subprocess.run(
            cmd, input=_sanitize(user_prompt),
            capture_output=True, text=True, timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"[{label}] claude -p timed out after {timeout_sec}s")
    dt = time.monotonic() - t0
    if res.returncode != 0:
        # Inspect stderr for rate-limit signal — claude -p sometimes exits
        # non-zero on rate limit.
        sig = is_rate_limit_response((res.stderr or "") + (res.stdout or ""))
        if sig:
            raise RateLimitError(sig)
        log.error("[%s] claude rc=%d stderr=%r stdout=%r",
                  label, res.returncode,
                  (res.stderr or "")[:2000], (res.stdout or "")[:2000])
        raise RuntimeError(f"[{label}] claude -p failed: rc={res.returncode}")
    try:
        envelope = json.loads(res.stdout)
    except json.JSONDecodeError:
        log.warning("[%s] claude --output-format json returned non-json", label)
        sig = is_rate_limit_response(res.stdout)
        if sig:
            raise RateLimitError(sig)
        return _strip_ansi(res.stdout).strip()
    text = envelope.get("result", "")
    # Even with rc=0, the result body can carry a rate-limit message.
    sig = is_rate_limit_response(text)
    if sig:
        raise RateLimitError(sig)
    usage = envelope.get("usage", {}) or {}
    cost = envelope.get("total_cost_usd")
    in_tok = usage.get("input_tokens", 0)
    out_tok = usage.get("output_tokens", 0)
    cache_r = usage.get("cache_read_input_tokens", 0)
    cache_c = usage.get("cache_creation_input_tokens", 0)
    log.info(
        "[%s] claude returned in %.1fs (%d chars; "
        "tokens in=%d out=%d cache_r=%d cache_c=%d; $%.4f)",
        label, dt, len(text),
        in_tok, out_tok, cache_r, cache_c, cost or 0.0,
    )
    _record_usage(usage_log_path, label, usage, cost)
    return _strip_ansi(text).strip()


def call_claude(prompt: str, system_prompt: str, *,
                label: str,
                usage_log_path: Path,
                attachments: list[Path] | None = None,
                timeout_sec: int = CALL_TIMEOUT_SEC) -> str:
    """Call claude with rate-limit retry. Wraps _call_claude_once with the
    shared 30 min × 50 retry harness from `_retry.py`.
    """
    return retry_call(
        lambda: _call_claude_once(
            prompt, system_prompt,
            label=label,
            usage_log_path=usage_log_path,
            attachments=attachments,
            timeout_sec=timeout_sec,
        ),
        label=label,
        log_dir=usage_log_path.parent,
    )


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------

def extract_pdf_text(pdf_path: Path, *,
                     pages: list[int] | None = None,
                     max_chars: int = MAX_PDF_TEXT_PER_CALL) -> str:
    parts: list[str] = []
    total = 0
    with fitz.open(pdf_path) as doc:
        page_iter = (
            [(i, doc[i - 1]) for i in pages if 1 <= i <= len(doc)]
            if pages else
            [(i + 1, doc[i]) for i in range(len(doc))]
        )
        for pn, page in page_iter:
            text = page.get_text("text")
            block = f"--- page {pn} ---\n{text}\n"
            if total + len(block) > max_chars:
                parts.append(f"--- (truncated; remaining pages omitted) ---")
                break
            parts.append(block)
            total += len(block)
    return "\n".join(parts)


def detect_section_pages(parsed_md_path: Path) -> dict[str, list[int]]:
    """Bucket pages by section using the headings extracted in PARSED_PAPER.

    Buckets:
      - intro:   abstract, introduction
      - related: related work, preliminaries, background
      - method:  method, approach, model, architecture, framework
      - exp:     experiments, results, evaluation
      - concl:   discussion, conclusion, limitation, future work
      - ref:     references, bibliography (excluded from analysis)

    Pages not matching any bucket fall into 'other'.
    """
    text = parsed_md_path.read_text(encoding="utf-8") if parsed_md_path.exists() else ""

    rx_sections = re.compile(
        r"^\s*-\s+(?:[A-Z]\.?\s*|\d+(?:\.\d+)*\.?\s+)([^()\[\]]{1,120})"
        r"\s*\(p(?:p\.|\.|p)?\s*(\d+)(?:\s*[–\-]\s*(\d+))?\)",
        re.MULTILINE,
    )

    bucket_keywords = {
        "intro":   re.compile(r"\b(introduction|abstract)\b", re.IGNORECASE),
        "related": re.compile(r"\b(related\s+work|preliminar(?:y|ies)|background)\b",
                              re.IGNORECASE),
        "method":  re.compile(r"\b(method(?:ology)?|approach|model|architecture|framework)\b",
                              re.IGNORECASE),
        "exp":     re.compile(r"\b(experiment|evaluation|result|implementation\s+details?)\b",
                              re.IGNORECASE),
        "concl":   re.compile(r"\b(discussion|conclusion|limitation|future\s+work)\b",
                              re.IGNORECASE),
        "ref":     re.compile(r"\b(reference|bibliograph)", re.IGNORECASE),
    }

    out: dict[str, list[int]] = {k: [] for k in list(bucket_keywords) + ["other"]}
    seen_starts: list[tuple[int, str]] = []
    for m in rx_sections.finditer(text):
        title = m.group(1).strip()
        try:
            start = int(m.group(2))
        except (TypeError, ValueError):
            continue
        end = int(m.group(3)) if m.group(3) else start
        bucket = "other"
        for k, rx in bucket_keywords.items():
            if rx.search(title):
                bucket = k
                break
        for p in range(start, end + 1):
            if p not in out[bucket]:
                out[bucket].append(p)
        seen_starts.append((start, title))

    for k in out:
        out[k] = sorted(set(out[k]))
    return out


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
#
# The system prompt and the per-call (A1..A5) prompts are loaded from
# prompts/*.md at module-import time. The .md files are the canonical
# source — edit them, not this file, when you want to change prompt
# wording.

SYSTEM_PROMPT_BASE = _load_prompt("system_base")

A1_PROMPT = _load_prompt("a1_overview")
A2_PROMPT = _load_prompt("a2_sections")
A3_PROMPT = _load_prompt("a3_critic")
A4_PROMPT = _load_prompt("a4_method")
A5_PROMPT = _load_prompt("a5_experiments")


# ---------------------------------------------------------------------------
# Per-call orchestration
# ---------------------------------------------------------------------------

def _format_authors_block(biblio: dict) -> str:
    rows = []
    for a in biblio.get("authors") or []:
        rows.append(a)
    return json.dumps(rows, ensure_ascii=False)


def _safe(s, default="—"):
    if s is None:
        return default
    s = str(s).strip()
    return s if s else default


def run_a1(*, biblio: dict, pdf_path: Path, out_dir: Path,
           lang_out: str) -> str:
    bi = biblio.get("basic_info", {}) or {}
    links = bi.get("links", {}) or {}
    prompt = A1_PROMPT.format(
        biblio_json=json.dumps(biblio, ensure_ascii=False, indent=2),
        pdf_text=extract_pdf_text(pdf_path, max_chars=40_000),
        short_name=_safe(bi.get("short_name")),
        full_title=_safe(bi.get("full_title")),
        arxiv_id=_safe(bi.get("arxiv_id")),
        release_date=_safe(bi.get("release_date")),
        venue=_safe(bi.get("venue")),
        abs_link=_safe(links.get("abs")),
        pdf_link=_safe(links.get("pdf")),
        code_link=_safe(links.get("code")),
        project_link=_safe(links.get("project")),
    )
    sys_p = SYSTEM_PROMPT_BASE.format(lang_out=lang_out)
    return call_claude(prompt, sys_p, label="A1 OVERVIEW",
                       usage_log_path=out_dir / "_token_usage.jsonl")


def run_a2(*, parsed_md: str, pdf_path: Path, section_pages: dict,
           out_dir: Path, lang_out: str) -> str:
    sec_lines = []
    for line in parsed_md.splitlines():
        if re.match(r"^\s*-\s+(?:[A-Z]\.|\d+(?:\.\d+)*\.?)\s", line):
            sec_lines.append(line.strip())
    parsed_sections = "\n".join(sec_lines) or "(parsed section list unavailable)"

    relevant_pages = sorted(set(
        section_pages.get("intro", [])
        + section_pages.get("related", [])
        + section_pages.get("method", [])
        + section_pages.get("exp", [])
        + section_pages.get("concl", [])
    ))[:24]
    pdf_text = extract_pdf_text(pdf_path, pages=relevant_pages, max_chars=70_000) \
        if relevant_pages else extract_pdf_text(pdf_path, max_chars=70_000)

    prompt = A2_PROMPT.format(
        parsed_sections=parsed_sections,
        pdf_text=pdf_text,
    )
    sys_p = SYSTEM_PROMPT_BASE.format(lang_out=lang_out)
    return call_claude(prompt, sys_p, label="A2 SECTIONS",
                       usage_log_path=out_dir / "_token_usage.jsonl")


def run_a3(*, biblio: dict, pdf_path: Path, out_dir: Path,
           lang_out: str) -> str:
    prompt = A3_PROMPT.format(
        biblio_json=json.dumps(biblio, ensure_ascii=False, indent=2),
        pdf_text=extract_pdf_text(pdf_path, max_chars=80_000),
    )
    sys_p = SYSTEM_PROMPT_BASE.format(lang_out=lang_out)
    return call_claude(prompt, sys_p, label="A3 CRITIC",
                       usage_log_path=out_dir / "_token_usage.jsonl")


def run_a4(*, biblio: dict, pdf_path: Path, section_pages: dict,
           figures_dir: Path, out_dir: Path, lang_out: str) -> str:
    method_pages = section_pages.get("method") or list(range(1, 13))
    pdf_text = extract_pdf_text(pdf_path, pages=method_pages, max_chars=70_000)

    fig_info = biblio.get("main_pipeline_figure") or {}
    fig_page = fig_info.get("page")
    fig_label = fig_info.get("fig_label") or "(unknown)"
    attachments = []
    if fig_page:
        candidate = figures_dir / f"page_{fig_page:03d}.png"
        if candidate.exists():
            attachments.append(candidate)
        else:
            log.warning("[A4] main_pipeline_figure png missing: %s", candidate)

    prompt = A4_PROMPT.format(
        biblio_json=json.dumps(biblio, ensure_ascii=False, indent=2),
        pdf_text=pdf_text,
        fig_page=fig_page or "?",
        fig_label=fig_label,
    )
    sys_p = SYSTEM_PROMPT_BASE.format(lang_out=lang_out)
    return call_claude(prompt, sys_p, label="A4 METHOD",
                       usage_log_path=out_dir / "_token_usage.jsonl",
                       attachments=attachments)


def run_a5(*, pdf_path: Path, section_pages: dict, out_dir: Path,
           lang_out: str) -> str:
    exp_pages = sorted(set(
        section_pages.get("exp", [])
        + section_pages.get("other", [])  # appendix usually lands in 'other'
    ))[:24]
    pdf_text = extract_pdf_text(pdf_path, pages=exp_pages, max_chars=80_000) \
        if exp_pages else extract_pdf_text(pdf_path, max_chars=80_000)

    prompt = A5_PROMPT.format(pdf_text=pdf_text)
    sys_p = SYSTEM_PROMPT_BASE.format(lang_out=lang_out)
    return call_claude(prompt, sys_p, label="A5 EXPERIMENTS",
                       usage_log_path=out_dir / "_token_usage.jsonl")


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def _strip_h1(s: str) -> str:
    """Remove an accidental leading H1 if a call wrote one."""
    s = s.strip()
    if s.startswith("# "):
        i = s.find("\n")
        if i != -1:
            s = s[i + 1:].lstrip()
    return s


def _ensure_section_present(md: str, expected_heading: str, label: str) -> None:
    if expected_heading not in md:
        raise ValueError(
            f"[{label}] output missing expected heading '{expected_heading}'\n"
            f"--- first 400 chars ---\n{md[:400]}"
        )


def merge_sections(*, biblio: dict, a1: str, a2: str, a3: str, a4: str, a5: str,
                   lang_out: str) -> str:
    a1, a2, a3, a4, a5 = (_strip_h1(s) for s in (a1, a2, a3, a4, a5))
    _ensure_section_present(a1, "## 1. Basic Information", "A1")
    _ensure_section_present(a1, "## 2. Research Overview", "A1")
    _ensure_section_present(a2, "## 3. Section Walkthrough", "A2")
    _ensure_section_present(a3, "## 4. Critical Profile", "A3")
    _ensure_section_present(a3, "## 7. Phyra's Judgment", "A3")
    _ensure_section_present(a3, "## 8. Open Questions", "A3")
    _ensure_section_present(a4, "## 5. Methodology Deep Dive", "A4")
    _ensure_section_present(a5, "## 6. Experiments", "A5")

    bi = biblio.get("basic_info", {}) or {}
    short = _safe(bi.get("short_name"), "(unknown)")
    full = _safe(bi.get("full_title"), "(unknown)")
    today = _dt.date.today().isoformat()

    a3_split = re.search(
        r"^(## 4\..*?)(## 7\..*?)(## 8\..*)$",
        a3, re.DOTALL | re.MULTILINE,
    )
    if not a3_split:
        raise ValueError("A3 output does not contain §4 / §7 / §8 in order")
    sec4, sec7, sec8 = (s.strip() for s in a3_split.groups())

    parts = [
        f"<!-- type: paper-read-notes | generated: {today} | lang: {lang_out} -->",
        "",
        f"# {short} — {full}",
        "",
        a1,
        "",
        a2,
        "",
        sec4,
        "",
        a4,
        "",
        a5,
        "",
        sec7,
        "",
        sec8,
        "",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def analyze(*, pdf_path: Path, parsed_md_path: Path, biblio_path: Path,
            out_md_path: Path, figures_dir: Path | None,
            lang_out: str, at_mode: bool) -> None:
    log.info("paper-analyzer v0.8.0 (schema_version=%d, at_mode=%s)",
             SCHEMA_VERSION, at_mode)

    biblio = json.loads(biblio_path.read_text(encoding="utf-8"))
    parsed_md = parsed_md_path.read_text(encoding="utf-8") if parsed_md_path.exists() else ""
    section_pages = detect_section_pages(parsed_md_path)
    log.info("section buckets: %s", {k: v for k, v in section_pages.items() if v})

    cache_dir = biblio_path.parent
    sections_dir = cache_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = figures_dir or (cache_dir / "figures")

    tasks = [
        ("A1", run_a1, dict(biblio=biblio, pdf_path=pdf_path,
                            out_dir=cache_dir, lang_out=lang_out)),
        ("A2", run_a2, dict(parsed_md=parsed_md, pdf_path=pdf_path,
                            section_pages=section_pages,
                            out_dir=cache_dir, lang_out=lang_out)),
        ("A3", run_a3, dict(biblio=biblio, pdf_path=pdf_path,
                            out_dir=cache_dir, lang_out=lang_out)),
        ("A4", run_a4, dict(biblio=biblio, pdf_path=pdf_path,
                            section_pages=section_pages,
                            figures_dir=figures_dir,
                            out_dir=cache_dir, lang_out=lang_out)),
        ("A5", run_a5, dict(pdf_path=pdf_path,
                            section_pages=section_pages,
                            out_dir=cache_dir, lang_out=lang_out)),
    ]

    results: dict[str, str] = {}

    # Resume: if a section MD is already cached on disk, skip its task.
    pending_tasks = []
    for name, fn, kw in tasks:
        cached = sections_dir / f"{name}.md"
        if cached.exists() and cached.stat().st_size > 0:
            log.info("[%s] resume: loading cached section from %s", name, cached)
            results[name] = cached.read_text(encoding="utf-8")
        else:
            pending_tasks.append((name, fn, kw))

    failures: dict[str, Exception] = {}

    def _worker(name: str, fn, kw):
        text = fn(**kw)
        # Persist immediately inside the worker so a sibling failure
        # can never abandon a successful result.
        (sections_dir / f"{name}.md").write_text(text, encoding="utf-8")
        return text

    if at_mode:
        with ThreadPoolExecutor(max_workers=5) as ex:
            futs = {
                ex.submit(_worker, name, fn, kw): name
                for (name, fn, kw) in pending_tasks
            }
            for fut in as_completed(futs):
                name = futs[fut]
                try:
                    results[name] = fut.result()
                except Exception as e:
                    log.error("[%s] failed: %s", name, e)
                    failures[name] = e
    else:
        for name, fn, kw in pending_tasks:
            try:
                results[name] = _worker(name, fn, kw)
            except Exception as e:
                log.error("[%s] failed: %s", name, e)
                failures[name] = e

    if failures:
        names = ", ".join(sorted(failures))
        raise RuntimeError(
            f"paper-analyzer: {len(failures)} call(s) failed: {names}. "
            f"Successful sections persisted to {sections_dir}; rerun to resume."
        )

    final = merge_sections(
        biblio=biblio,
        a1=results["A1"], a2=results["A2"], a3=results["A3"],
        a4=results["A4"], a5=results["A5"],
        lang_out=lang_out,
    )

    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text(final, encoding="utf-8")
    word_count = len(final.split())
    log.info("wrote %s — %d chars, ~%d words",
             out_md_path, len(final), word_count)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf_path")
    p.add_argument("parsed_md")
    p.add_argument("biblio_json")
    p.add_argument("out_md")
    p.add_argument("lang_out", nargs="?", default="zh-TW")
    p.add_argument("--figures-dir", default=None,
                   help="dir holding extracted figure PNGs (default: cache/figures)")
    p.add_argument("--nt", action="store_true",
                   help="serial mode (default is AT/parallel)")
    args = p.parse_args()

    figures_dir = Path(args.figures_dir).resolve() if args.figures_dir else None

    analyze(
        pdf_path=Path(args.pdf_path).resolve(),
        parsed_md_path=Path(args.parsed_md).resolve(),
        biblio_path=Path(args.biblio_json).resolve(),
        out_md_path=Path(args.out_md).resolve(),
        figures_dir=figures_dir,
        lang_out=args.lang_out,
        at_mode=not args.nt,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
