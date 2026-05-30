---
name: paper-translate
description: "Produce a side-by-side bilingual translated PDF of an academic paper using BabelDOC + Claude headless translation. References are sliced before translation (cost saving) then re-injected as placeholder pages so the final PDF has the same page count as the source. Optionally also emits a translation-only PDF (--mono). Independent of /phyra:paper-read. v0.9.0."
argument-hint: "<paper-pdf-path-or-arxiv-url-or-arxiv-id> [--lang-out zh-TW] [--lang-in en] [--mono] [--qps 2] [--compress lossy|lossless|off] [--model sonnet]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "Agent"]
---

# /phyra:paper-translate (v0.9.0)

> Single deliverable: a bilingual side-by-side translated PDF (and
> optionally a translation-only PDF). No analysis, no slide. For paper
> understanding use `/phyra:paper-read` instead.

## Step 0 — Parse arguments and load skills

Parse `$ARGUMENTS`:

- **paper-pdf-path-or-arxiv-url-or-arxiv-id** (required), one of:
  - a local PDF path (absolute or relative): outputs go in the **same
    directory** as the input PDF, with stem = the input file's stem.
  - an arXiv URL (`https://arxiv.org/abs/2503.06132` /
    `https://arxiv.org/pdf/2503.06132`).
  - a bare arXiv id (`2503.06132`).
  - For arXiv inputs: download to `<cwd>/.phyra/papers/`, rename to
    `<YYMM>_<sanitized-title>.pdf` (e.g.
    `2402_Genie_Generative_Interactive_Environments.pdf`), and outputs
    go alongside the downloaded PDF. The title is sanitized so the stem
    never contains spaces.
- `--lang-out <code>` (default `zh-TW`).
- `--lang-in <code>` (default `en`).
- `--mono`: also emit a translation-only PDF.
- `--qps <int>` (default `2`): per-second translation request budget.
- `--model <alias-or-id>` (default `sonnet`): Claude model passed to
  `claude --model` for each per-chunk translation call. Translation is
  many-call (one call per BabelDOC chunk; ~hundreds per paper), so we
  default to Sonnet for speed/cost. Override with `opus`, `haiku`, or a
  full id (e.g. `claude-sonnet-4-6`).
- `--compress <lossy|lossless|off>` (default `lossy`).

Resolve via `resolve_input.py` (lives in the sibling paper-read skill so
both commands derive identical STEM / OUT_DIR / cache dir from the same
input):

```
PARSED=$(uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/resolve_input.py \
    "$ARG")
PAPER_PATH=$(echo "$PARSED" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['pdf_path'])")
OUT_DIR=$(  echo "$PARSED" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['out_dir'])")
STEM=$(     echo "$PARSED" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['stem'])")
```

Output filenames (all go in `$OUT_DIR`):

| Output | Filename |
|--------|----------|
| Bilingual side-by-side PDF | `${STEM}_bilingual.${LANG_OUT}.dual.pdf` |
| Translation-only PDF (if `--mono`) | `${STEM}_bilingual.${LANG_OUT}.mono.pdf` |

Cache dir for intermediates: `<cwd>/.phyra/.cache/<STEM>/`. Shared with
`/phyra:paper-read` — if the user previously ran paper-read on the same
PDF, `PARSED_PAPER.md` will already be there and Step 3 will reuse it.

**Before any other work, load the `soul` and `typography` skills.**

## Step 1 — Preflight

```
${CLAUDE_PLUGIN_ROOT}/skills/paper-translate/scripts/preflight.py \
    --lang-out $LANG_OUT \
    --compress $COMPRESS
```

Checks: `${CLAUDE_PLUGIN_ROOT}`, `uv`, `claude`, `babeldoc`, the SourceHan
font for `$LANG_OUT`, and (if `--compress=lossy`) `gs`. Abort on non-zero.

## Step 2 — Determine ref pages (opportunistic cache reuse)

```
PARSED_PAPER=".phyra/.cache/$STEM/PARSED_PAPER.md"
if [ -f "$PARSED_PAPER" ]; then
    PARSED_ARG="$PARSED_PAPER"
else
    PARSED_ARG="-"   # tells slice_pdf.py to skip parsed lookup, use PDF heuristic
fi
```

## Step 3 — paper-translator subagent

Drives the three-step translation pipeline. The subagent definition lives
at `${CLAUDE_PLUGIN_ROOT}/agents/paper-translator.md`.

```
# 3.1 — slice off ref pages
uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-translate/scripts/slice_pdf.py \
    "$PAPER_PATH" \
    "$PARSED_ARG" \
    ".phyra/.cache/$STEM/${STEM}.no_refs.pdf" \
    ".phyra/.cache/$STEM/slice_meta.json"

# 3.2 — BabelDOC + Claude translate
uv run --python 3.12 --with babeldoc==0.5.24 --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-translate/scripts/translate_with_claude.py \
    ".phyra/.cache/$STEM/${STEM}.no_refs.pdf" \
    ".phyra/.cache/$STEM/" \
    --lang-in $LANG_IN \
    --lang-out $LANG_OUT \
    --qps $QPS \
    --model $MODEL    # default: sonnet

# 3.3 — stitch into final dual.pdf with refs placeholder
uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-translate/scripts/build_dual.py \
    "$PAPER_PATH" \
    ".phyra/.cache/$STEM/${STEM}.no_refs.no_watermark.${LANG_OUT}.dual.pdf" \
    ".phyra/.cache/$STEM/slice_meta.json" \
    "$OUT_DIR/${STEM}_bilingual.${LANG_OUT}.dual.pdf" \
    --lang-out $LANG_OUT \
    $( [ "$WANT_MONO" = "yes" ] && echo --also-mono \
         "$OUT_DIR/${STEM}_bilingual.${LANG_OUT}.mono.pdf" )
```

## Step 4 — Report

Print to the user:

1. Bilingual PDF: `$OUT_DIR/${STEM}_bilingual.${LANG_OUT}.dual.pdf`
2. Mono PDF (if `--mono`): `$OUT_DIR/${STEM}_bilingual.${LANG_OUT}.mono.pdf`
3. Total wall-clock (translation dominates)
4. BabelDOC chunk count + count of fallback chunks (if any)
5. Cache dir (kept for re-runs): `.phyra/.cache/$STEM/`

Do NOT delete the cache dir.

## Subagent / script ownership

| Subagent | Script | Output |
|----------|--------|--------|
| `paper-translator` | `slice_pdf.py` + `translate_with_claude.py` + `build_dual.py` | `bilingual.<lang>.dual.pdf` (+ optional mono) |

The agent definition in `${CLAUDE_PLUGIN_ROOT}/agents/paper-translator.md`
documents the contract. `slice_pdf.py` and `build_dual.py` are pure
PyMuPDF (no LLM). `translate_with_claude.py` is a `BaseTranslator`
subclass invoked by BabelDOC; per-chunk it spawns `claude -p` headless.

## Rate-limit handling

Per-chunk translation calls go through the same retry harness as
paper-read:`_retry.is_rate_limit_response()` (sourced from the sibling
`skills/paper-read/scripts/_retry.py`). On detection, the in-script
retry loop sleeps 30 minutes and retries up to 50 times. Failed chunks
fall back to source text (English passage shown verbatim on the
translation side); the run continues.

## See also

- `/phyra:paper-read` — analysis MD + viewer HTML (+ optional slide).
  Independent of this command; can be run before or after on the same
  PDF without conflict (cache dir `<cwd>/.phyra/.cache/<STEM>/` is
  shared).
