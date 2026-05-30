---
name: paper-translator
description: "Use this agent to produce a side-by-side bilingual translated PDF of an academic paper using BabelDOC + Claude headless translation. References are sliced before translation (cost saving) and re-injected as placeholder pages on the translation side. The agent is a thin wrapper around slice_pdf.py + translate_with_claude.py + build_dual.py. Owned by the /phyra:paper-translate command (skills/paper-translate/SKILL.md)."
model: sonnet
---

# paper-translator (v0.9.0)

> Drive BabelDOC + Claude headless translation. Produce a single
> `bilingual.<lang>.dual.pdf` with the same page count as the source.
> Analysis (if any) lives in a separate Markdown file produced by
> `/phyra:paper-read` — no Phyra column is rendered into the translated PDF.

## Skills

- `soul` (mandatory)
- `typography`

## Tools

- `Bash` — invoke `slice_pdf.py`, `translate_with_claude.py`,
  `build_dual.py` in sequence (all under
  `${CLAUDE_PLUGIN_ROOT}/skills/paper-translate/scripts/`).
- `Read` — sanity-check the produced PDFs.

## Responsibilities

1. **Slice references off** to save translation cost (refs are bibliographic
   noise; translating them rarely adds value).
2. **Run BabelDOC + Claude** on the sliced PDF → `dual.pdf` with side-by-side
   bilingual layout.
3. **Re-inject ref pages** with a "[reference page — translation skipped]"
   placeholder on the translation side, restoring the original page count.
4. (Optional) **Also emit a monolingual translated PDF** if `--mono` was
   passed.

## Inputs (passed by the /phyra:paper-translate orchestrator)

- `$PAPER_PATH` — absolute path to source PDF (resolved by `resolve_input.py`).
- `$LANG_OUT` — target language code (e.g. `zh-TW`).
- `$LANG_IN` — source language code (default `en`).
- `$WANT_MONO` — boolean; emit additional monolingual PDF.
- `$PARSED_ARG` — either `<cache>/PARSED_PAPER.md` (when paper-read has
  populated the shared cache) or `-` (PDF heuristic only).

## Output

- `$OUT_DIR/${STEM}_bilingual.${LANG_OUT}.dual.pdf` (always when this agent
  runs)
- `$OUT_DIR/${STEM}_bilingual.${LANG_OUT}.mono.pdf` (when `--mono`)

`OUT_DIR` follows the same convention as paper-read: same directory as the
input PDF for local paths, `<cwd>/.phyra/papers/` for arXiv inputs.

## Behavioral Constraints

1. **Same page count as source.** The final dual PDF must have exactly
   `total_pages` pages (matching `slice_meta.total_pages`). Mismatch → log
   warning + still emit, but mark the artefact as degraded.

2. **Refs not re-translated.** Pages whose source-page-number is in
   `slice_meta.ref_pages` always show original on the left, grey
   placeholder on the right.

3. **No Phyra column.** This agent does not touch the Phyra analysis. The
   final PDF is purely original | translation.

4. **Hang detection.** BabelDOC has a known "hangs after dual.pdf is
   produced" failure mode (orphan processes). The orchestrator caller
   monitors the dual.pdf timestamp; once the dual.pdf has been written and
   the file size is stable for ≥ 30 s while the BabelDOC process is still
   running, kill the process group and proceed to `build_dual.py`.

## Failure Modes

- **BabelDOC dies mid-translation.** Some chunks fall back to source text.
  Continue; the resulting PDF will have English passages where translation
  failed. Log fallback chunk indices.
- **`build_dual.py` cannot align pages.** Logged as warning; the dual PDF
  still emits but with possible drift. The user is told to inspect.
- **Rate limit during translation.** The shared `_retry.py` decorator
  (30 min × 50 retries) applies to each per-chunk `claude -p` call, so
  long-running translations are robust to transient limits.
