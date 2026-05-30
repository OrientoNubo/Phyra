---
name: paper-read
description: "Read an academic paper and produce two decoupled deliverables, each owned by its own subagent: (1) paper-analyzer → analysis Markdown + viewer HTML (mandatory), (2) paper-slide-maker → fixed slide-deck draft HTML (optional). For bilingual translated PDF use the separate /phyra:paper-translate command. v0.9.0."
argument-hint: "<paper-pdf-path-or-arxiv-url-or-arxiv-id> [--lang-out zh-TW] [--slide|--no-slide] [--at]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "Agent", "SendMessage", "AskUserQuestion"]
---

# /phyra:paper-read (v0.9.0 decoupled pipeline)

> **Two subagents — clear ownership.** The SKILL is the orchestrator;
> each deliverable is produced by exactly one subagent. Translation
> lives in its own command (`/phyra:paper-translate`).
>
> ```
>   paper-bibliographer (BIBLIO.json)
>       │
>       ├──→ paper-analyzer       (analysis.md + analysis.html)   [always]
>       └──→ paper-slide-maker    (draftslide.html)               [opt-in;
>                                                                  depends on
>                                                                  analyzer]
> ```

## Step 0 — Parse arguments and load `soul`

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
    go alongside the downloaded PDF. The title is taken verbatim from
    arXiv with `: ` collapsed to `_`, filesystem-unsafe characters
    (`<>"/\|?*`) replaced by `_`, and all whitespace converted to `_` —
    so stems never contain spaces.
- `--lang-out <code>` (default `zh-TW`).
- `--slide` / `--no-slide` (default: ask interactively).
- `--at`: parallel mode for analyzer's 5-call split (default ON).

Resolve via `resolve_input.py`:

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
| Analysis Markdown   | `${STEM}_analysis.${LANG_OUT}.md` |
| Analysis viewer HTML | `${STEM}_analysis.${LANG_OUT}.html` |
| Slide deck (draft)  | `${STEM}_draftslide.html` |

Cache dir for intermediates: `<cwd>/.phyra/.cache/<STEM>/`.

**Before any other work, load the `soul`, `typography`, and
`academic-reading` skills.**

## Step 1 — Preflight

```
${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/preflight.py \
    --lang-out $LANG_OUT
```

Checks `claude` and `uv`. No external binaries are needed for the
analyzer or slide steps. Abort on non-zero.

## Step 2 — `paper-bibliographer` subagent

Produces `BIBLIO.json` (basic info, authors, lineage, `research_topic`,
`core_argument`, main pipeline figure pointer). Mandatory; consumed by
both downstream subagents (analyzer and slide-maker).

```
uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/bibliographer.py \
    "$PAPER_PATH" \
    ".phyra/.cache/$STEM/BIBLIO.json" \
    $LANG_OUT
```

## Step 3 — `paper-parser` subagent

Produces `PARSED_PAPER.md` (section list with page numbers, figures, tables).

## Step 4 — Extract figures (deterministic helper, no LLM)

Used internally by the analyzer's A4 METHOD multimodal call.

```
uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/extract_figures.py \
    "$PAPER_PATH" \
    ".phyra/.cache/$STEM/PARSED_PAPER.md" \
    ".phyra/.cache/$STEM/BIBLIO.json" \
    ".phyra/.cache/$STEM/figures/"
```

## Step 5 — `paper-analyzer` subagent (always)

**Role:** read PDF + PARSED_PAPER + BIBLIO → comprehensive Markdown
analysis. No layout budget. Produces both an MD source and a viewer
HTML rendering of that MD.

```
# 5.1 — produce analysis MD (5-call internal split)
uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/paper_analyzer.py \
    "$PAPER_PATH" \
    ".phyra/.cache/$STEM/PARSED_PAPER.md" \
    ".phyra/.cache/$STEM/BIBLIO.json" \
    "$OUT_DIR/${STEM}_analysis.${LANG_OUT}.md" \
    $LANG_OUT \
    --figures-dir ".phyra/.cache/$STEM/figures/" \
    $( [ "$AT_MODE" = "no" ] && echo --nt )

# 5.2 — render the MD to a styled viewer HTML
uv run python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/build_analysis_html.py \
    "$OUT_DIR/${STEM}_analysis.${LANG_OUT}.md" \
    ".phyra/.cache/$STEM/BIBLIO.json" \
    "$OUT_DIR/${STEM}_analysis.${LANG_OUT}.html" \
    --lang-out $LANG_OUT
```

## Step 6 — `paper-slide-maker` subagent (only if `$WANT_SLIDE = yes`)

**Role:** turn the analysis MD into a fixed slide-deck HTML. Depends on
Step 5 having written the MD. No LLM calls — pure rendering.

```
uv run --with pymupdf python \
    ${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/build_slide.py \
    "$OUT_DIR/${STEM}_analysis.${LANG_OUT}.md" \
    ".phyra/.cache/$STEM/BIBLIO.json" \
    ".phyra/.cache/$STEM/figures/" \
    "$OUT_DIR/${STEM}_draftslide.html" \
    --lang-out $LANG_OUT
```

## Post-workflow

Report to the user:

1. Analysis MD: `$OUT_DIR/${STEM}_analysis.${LANG_OUT}.md`
2. Analysis HTML viewer: `$OUT_DIR/${STEM}_analysis.${LANG_OUT}.html`
3. Slide deck (if slide): `$OUT_DIR/${STEM}_draftslide.html`
4. Token usage summary from `.phyra/.cache/$STEM/_token_usage.jsonl`
5. Wall-clock total
6. Cache dir (kept for re-render and for `/phyra:paper-translate` reuse):
   `.phyra/.cache/$STEM/`

Do NOT delete the cache dir. Re-runs with different flags pick up cached
intermediates, and a subsequent `/phyra:paper-translate` on the same PDF
will reuse `PARSED_PAPER.md` for ref-page detection.

## Subagent responsibilities (single source of truth)

| Subagent | Inputs | Output | LLM calls |
|----------|--------|--------|-----------|
| `paper-bibliographer` | source PDF | `BIBLIO.json` | 1 (with WebSearch) |
| `paper-parser` | source PDF | `PARSED_PAPER.md` | 1 |
| `paper-analyzer` | PDF + PARSED + BIBLIO + figures | `analysis.<lang>.md` + `analysis.<lang>.html` | 5 (A1 OVERVIEW / A2 SECTIONS / A3 CRITIC / A4 METHOD / A5 EXPERIMENTS) |
| `paper-slide-maker` | analysis MD + BIBLIO | `draftslide.html` | 0 (pure renderer) |

For translation, see `/phyra:paper-translate` (owns the `paper-translator`
subagent and the BabelDOC + Claude headless pipeline).

The agent definitions in `${CLAUDE_PLUGIN_ROOT}/agents/paper-*.md` document
each subagent's contract. Each helper script in
`${CLAUDE_PLUGIN_ROOT}/skills/paper-read/scripts/` is the deterministic
shell for exactly one subagent — no script crosses agent boundaries.

## Rate-limit handling

All `claude -p` calls (bibliographer, paper-analyzer A1..A5) flow
through `_retry.py`: on detection of "usage limit" / "rate limit"
responses, sleep 30 minutes and retry, up to 50 attempts. Each retry
logs to `.phyra/.cache/$STEM/_retry.log`. The same `_retry.py` is also
imported by `/phyra:paper-translate` for its per-chunk translation
calls.

## See also

- `/phyra:paper-translate` — bilingual side-by-side PDF (BabelDOC +
  Claude headless). Independent command; can be run before or after
  paper-read on the same PDF without conflict (cache dir is shared).
