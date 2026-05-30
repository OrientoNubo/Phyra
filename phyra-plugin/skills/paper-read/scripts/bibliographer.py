"""
paper-bibliographer helper (v0.7.0 Agent A).

Extract a paper's bibliographic profile into BIBLIO.json. Optionally
WebSearch-verify author affiliations + homepages.

Inputs:
  - source PDF (PyMuPDF first-page text + figure captions for the prompt)

Output:
  - BIBLIO.json (schema documented in agents/paper-bibliographer.md)

Usage:
  uv run --with pymupdf python bibliographer.py \\
      <source.pdf> <out_BIBLIO.json> [<lang_out>]
"""

import json
import logging
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF

# Local retry harness — sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _retry import RateLimitError, is_rate_limit_response, retry_call  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bibliographer")

CALL_TIMEOUT_SEC = 600
SCHEMA_VERSION = 1
MAX_CONTEXT_CHARS = 30_000  # only first few pages + figure captions needed


SYSTEM_PROMPT = (
    "You are Phyra's paper-bibliographer agent. Produce ONE JSON object "
    "describing the paper's identification (basic_info), authors (with "
    "affiliations and verified homepages when possible), venue, related "
    "lineage (3-7 directly cited prior works), conceptual frame "
    "(keywords/topic/domain), and the page+label of the main pipeline figure.\n\n"
    "You have WebSearch and WebFetch tools. Use them to verify the affiliation "
    "and find the homepage of the FIRST author and corresponding author. "
    "If WebSearch fails or returns nothing relevant, leave `verified_url` as "
    "null and proceed — do not retry indefinitely.\n\n"
    "Hard rules:\n"
    "  1. Output ONLY the JSON object — no preamble, no markdown fences.\n"
    "  2. Use `null` for unknown / unverifiable fields. NEVER invent.\n"
    "  3. `main_pipeline_figure` MUST point to the END-TO-END model architecture "
    "figure (usually first figure in §3 Method, captioned 'Overview' / "
    "'Pipeline' / 'Architecture' / 'Framework'). Sub-module figures and "
    "result figures DO NOT qualify. If the paper truly lacks one, emit `null`.\n"
    "  4. `related_lineage` = 3-7 specific prior works the paper compares "
    "against or builds on. NOT a literature review.\n"
    "  5. Prose fields (research_topic) in the requested target language."
)


USER_PROMPT_TMPL = """Produce BIBLIO.json for this paper.

# Output schema

```jsonc
{{
  "schema_version": 1,
  "lang_out": "{lang_out}",
  "basic_info": {{
    "short_name": "...",
    "full_title": "...",
    "arxiv_id": "...",
    "version_tag": "v1",
    "release_date": "YYYY-MM-DD",
    "venue": "...",
    "authors_brief": "...",
    "links": {{"abs": "...", "pdf": "...", "code": null, "project": null}},
    "pdf_local_path": "{pdf_path}"
  }},
  "authors": [
    {{"name": "...", "affiliation": "...", "homepage": null,
      "verified_url": null, "role": "..."}}
  ],
  "venue_detail": {{
    "type": "arXiv preprint | conference | journal | workshop",
    "name": "...",
    "decision_status": null
  }},
  "related_lineage": [
    {{"key": "...", "relation": "baseline | predecessor | concurrent | influence | base model",
      "brief": "<=120 chars"}}
  ],
  "keywords": ["..."],
  "research_topic": "<=200-word paragraph in {bullet_lang}; complete, never truncated",
  "core_argument": "<=400-word paragraph in {bullet_lang}; explain the root cause the authors identify and why their solution is logically necessary; complete, never truncated",
  "domain": ["..."],
  "main_pipeline_figure": {{
    "page": 3,
    "fig_label": "Figure 2",
    "caption_excerpt": "<=200 chars"
  }}
}}
```

# Source PDF — first 6 pages + figure caption list

{first_pages_text}

# Figure captions detected in the paper

{figures_block}

Use WebSearch / WebFetch to verify affiliations and find homepages of the
first author and corresponding author. Leave `verified_url` as null if you
cannot verify within a few searches.

# Output format (strict)

Begin your response with `{{` and end with `}}`. Emit ONLY the JSON object —
no prose before or after, no markdown code fences, no explanations. The
first character of your response MUST be `{{` and the last MUST be `}}`.
"""


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)


def claude_bin() -> str:
    p = shutil.which("claude")
    if not p:
        raise RuntimeError("`claude` not found in PATH. Run preflight.py first.")
    return p


def extract_first_pages(pdf_path: Path, n_pages: int = 6, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    parts = []
    total = 0
    with fitz.open(pdf_path) as doc:
        cap = min(n_pages, len(doc))
        for i in range(cap):
            text = doc[i].get_text("text")
            block = f"--- page {i+1} ---\n{text}\n"
            if total + len(block) > max_chars:
                parts.append(f"--- (truncated; full source has {len(doc)} pages) ---")
                break
            parts.append(block)
            total += len(block)
    log.info("first %d-page text: %d chars", cap, total)
    return "\n".join(parts)


def extract_figure_captions(pdf_path: Path) -> str:
    """Heuristic: lines starting with 'Figure N' / 'Fig. N' across the PDF."""
    rx = re.compile(r"^\s*(Fig(?:ure)?\.?\s*\d+[:.\s].{0,300})", re.MULTILINE)
    out = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, 1):
            t = page.get_text("text")
            for m in rx.finditer(t):
                cap = m.group(1).strip().replace("\n", " ")[:300]
                out.append(f"page {i}: {cap}")
                if len(out) >= 40:
                    return "\n".join(out)
    return "\n".join(out)


def build_prompt(pdf_path: Path, lang_out: str) -> str:
    bullet_lang_map = {
        "zh-TW": "Traditional Chinese (Taiwan terms)",
        "zh-HK": "Traditional Chinese (Hong Kong terms)",
        "zh-CN": "Simplified Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "en": "English",
    }
    bullet_lang = bullet_lang_map.get(lang_out, lang_out)
    return USER_PROMPT_TMPL.format(
        lang_out=lang_out,
        bullet_lang=bullet_lang,
        pdf_path=str(pdf_path),
        first_pages_text=extract_first_pages(pdf_path).strip(),
        figures_block=extract_figure_captions(pdf_path).strip() or "(no Figure captions detected)",
    )


_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _sanitize_for_subprocess(s: str) -> str:
    """Strip control chars (including embedded null bytes) that subprocess
    cannot pass via argv. PDF text extraction occasionally yields ``\\x00``
    inside ligatures or stray metadata; without this, ``subprocess.run``
    raises ``ValueError: embedded null byte``."""
    return _CTRL_RE.sub("", s)


def _record_usage(out_path: Path, label: str, usage: dict, cost_usd: float | None) -> None:
    """Append one claude call's token usage to a JSONL alongside the artefact.

    Path: same directory as the artefact (e.g. BIBLIO.json's parent), file
    `_token_usage.jsonl`. Each line records label, timestamp, input/output/cache
    token counts, and reported total_cost_usd (when available). Best-effort —
    silently skipped on any error so usage tracking never breaks the pipeline.
    """
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


def _call_claude_once(prompt: str, *, usage_log_path: Path | None,
                      label: str) -> str:
    """One attempt at claude -p. Raises RateLimitError on rate-limit response,
    other RuntimeError on non-zero exit. v0.8.0: prompt goes via stdin to
    avoid argv limits."""
    cmd = [
        claude_bin(), "-p",
        "--append-system-prompt", _sanitize_for_subprocess(SYSTEM_PROMPT),
        "--output-format", "json",
    ]
    t0 = time.monotonic()
    res = subprocess.run(
        cmd, input=_sanitize_for_subprocess(prompt),
        capture_output=True, text=True, timeout=CALL_TIMEOUT_SEC,
    )
    dt = time.monotonic() - t0
    if res.returncode != 0:
        sig = is_rate_limit_response((res.stderr or "") + (res.stdout or ""))
        if sig:
            raise RateLimitError(sig)
        log.error("claude stderr: %s", res.stderr[:500])
        raise RuntimeError(f"claude -p failed: rc={res.returncode}")
    try:
        envelope = json.loads(res.stdout)
    except json.JSONDecodeError:
        log.warning("claude --output-format json returned non-json; using raw text")
        log.info("claude returned in %.1fs (rc=%d, %d chars)",
                 dt, res.returncode, len(res.stdout))
        sig = is_rate_limit_response(res.stdout)
        if sig:
            raise RateLimitError(sig)
        return _strip_ansi(res.stdout).strip()
    text = envelope.get("result", "")
    sig = is_rate_limit_response(text)
    if sig:
        raise RateLimitError(sig)
    usage = envelope.get("usage", {}) or {}
    cost = envelope.get("total_cost_usd")
    in_tok = usage.get("input_tokens", 0)
    out_tok = usage.get("output_tokens", 0)
    cache_r = usage.get("cache_read_input_tokens", 0)
    cache_c = usage.get("cache_creation_input_tokens", 0)
    log.info("[%s] claude returned in %.1fs (rc=%d, %d chars; "
             "tokens in=%d out=%d cache_r=%d cache_c=%d; $%.4f)",
             label, dt, res.returncode, len(text),
             in_tok, out_tok, cache_r, cache_c, cost or 0.0)
    if usage_log_path is not None:
        _record_usage(usage_log_path, label, usage, cost)
    return _strip_ansi(text).strip()


def call_claude(prompt: str, *, usage_log_path: Path | None = None,
                label: str = "bibliographer") -> str:
    """Call claude with rate-limit retry. Wraps _call_claude_once."""
    log_dir = usage_log_path.parent if usage_log_path else Path(".")
    return retry_call(
        lambda: _call_claude_once(prompt, usage_log_path=usage_log_path, label=label),
        label=label, log_dir=log_dir,
    )


def parse_json_lenient(raw: str) -> dict:
    """Parse Claude's text response into a JSON object.

    Even with a "JSON only" system prompt, models sometimes prepend a short
    preamble or wrap output in a ``` fence. We extract the outermost
    ``{ ... }`` block as the canonical JSON, falling back to a raw parse
    only if no braces are found at all.
    """
    raw = raw.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    first = raw.find("{")
    last = raw.rfind("}")
    if first != -1 and last > first:
        return json.loads(raw[first:last + 1])
    return json.loads(raw)


def fallback_biblio(pdf_path: Path, lang_out: str) -> dict:
    log.warning("emitting fallback BIBLIO (claude failed or invalid)")
    title = "(unknown)"
    authors_text = ""
    with fitz.open(pdf_path) as doc:
        first = doc[0].get_text("text").splitlines()
        if first:
            title = first[0].strip()[:200]
            authors_text = " ".join(first[1:5])[:300]
    return {
        "schema_version": SCHEMA_VERSION,
        "lang_out": lang_out,
        "basic_info": {
            "short_name": "(unknown)",
            "full_title": title,
            "arxiv_id": None, "version_tag": None, "release_date": None,
            "venue": None, "authors_brief": authors_text or None,
            "links": {"abs": None, "pdf": None, "code": None, "project": None},
            "pdf_local_path": str(pdf_path),
        },
        "authors": [],
        "venue_detail": {"type": None, "name": None, "decision_status": None},
        "related_lineage": [],
        "keywords": [],
        "research_topic": None,
        "core_argument": None,
        "domain": [],
        "main_pipeline_figure": None,
    }


def extract(pdf_path: Path, out_json: Path, lang_out: str = "zh-TW") -> None:
    log.info("paper-bibliographer v0.7.0 (schema_version=%d)", SCHEMA_VERSION)
    prompt = build_prompt(pdf_path, lang_out)
    log.info("prompt size: %d chars", len(prompt))

    try:
        raw = call_claude(prompt, usage_log_path=out_json, label="bibliographer")
        obj = parse_json_lenient(raw)
        assert obj.get("schema_version") == SCHEMA_VERSION, \
            f"schema_version must be {SCHEMA_VERSION}"
        for k in ("basic_info", "authors", "main_pipeline_figure"):
            assert k in obj, f"missing required field: {k}"
    except Exception as e:
        log.error("bibliographer failed: %s", e)
        obj = fallback_biblio(pdf_path, lang_out)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info("wrote %s", out_json)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    lang = sys.argv[3] if len(sys.argv) > 3 else "zh-TW"
    extract(
        Path(sys.argv[1]).resolve(),
        Path(sys.argv[2]).resolve(),
        lang_out=lang,
    )
