# Changelog

## v0.9.6 (2026-05-16) — paper-read HTML: light/dark/system appearance

Both paper-read HTML outputs (analysis viewer + slide deck) now ship a
light/dark/system appearance toggle. Layout, spacing, and DOM structure
are untouched — the kit is purely additive and the palette only restyles
via the CSS variable names the generators already use.

Palette adapted from `paper-base/script/generate_index.py` (the #c96c49
warm-grey scheme): `:root` carries the light values, `[data-theme="dark"]`
the dark ones, plus a few dark "patch" rules for the handful of
non-variable colours baked into the base CSS (code/pre/table-hover
backgrounds, slide bottom-bar).

The kit is a single shared module so already-generated HTML files can be
retrofitted later by the *same* call — `inject()` is idempotent (returns
unchanged if a `.theme-toggle` is already present), so re-running a
generator or re-retrofitting a file never double-injects.

### Added

- `skills/paper-read/scripts/theme_kit.py` (new) — `THEME_CSS`,
  `THEME_HEAD_SCRIPT` (no-FOUC), `THEME_TOGGLE_HTML` (fixed-position
  segmented control), `THEME_TOGGLE_SCRIPT` (localStorage key
  `phyra-theme`), and an idempotent `inject(html)` that splices them in
  before `</head>`, after `<body>`, and before `</body>`.
- `skills/paper-read/scripts/retrofit_theme.py` (new) — CLI that applies
  `theme_kit.inject()` in place to HTML generated before this change.
  Takes directories (default globs `**/*_analysis.*.html` +
  `**/*_draftslide.html`) or explicit globs; `--dry-run` reports without
  writing. Idempotent, so re-runs are safe.

### Changed

- `skills/paper-read/scripts/build_analysis_html.py` — `render_page()`
  returns `inject_theme(page)` (one import + one wrap; no CSS rewritten).
- `skills/paper-read/scripts/build_slide.py` — `render_html()` returns
  `inject_theme(page)` (one import + one wrap; no CSS rewritten).

## v0.9.5 (2026-05-16) — paper-slide: stop "Paper Structure" duplicating §3

The slide deck's "Paper Structure" slide rendered the *entire* §3
Section Walkthrough via `md_to_html(s3)`. But §3.2 / §3.3 / §3.6 are
also carried by their own dedicated Introduction / Related Work /
Conclusion slides, so that prose appeared **twice** in every deck, and
"Paper Structure" became an over-long wall of text instead of a map.
(The analysis MD/HTML was never affected — `build_analysis_html.py`
renders the MD 1:1.)

"Paper Structure" is now a pure roadmap: the ordered list of §3's
`### 3.x <title>` headings only, no body text. On 2605_X2SAM this drops
the deck from ~84KB to ~69KB with the same slide count (19), and the
three previously-duplicated passages now appear exactly once.

### Fixed

- `skills/paper-read/scripts/build_slide.py`
  - New `extract_section3_outline(s3)` — extracts only the `### 3.x`
    headings from §3 and renders them as a `<ul class="toc">` card.
  - "Paper Structure" slide now uses that outline instead of
    `md_to_html(s3)`.
  - New `.toc` CSS rule (borderless list with an accent left-border per
    item) so the roadmap reads as a map, not a bullet dump.

## v0.9.4 (2026-05-15) — paper-analyzer: downscale figure attachments

`paper_analyzer.py` now downscales image attachments before embedding
them in the `claude -p` stdin prompt.

The `--output-format json` claude CLI tokenizes the entire
`data:image/png;base64,...` URL as text, so a full-page raster figure
(~756KB PNG → ~1M base64 chars) consumes ~1M context tokens by itself
and trips `api_error_status=400 "Prompt is too long"`. The A4 METHOD
call attaches the paper's main pipeline figure and was failing in
~1.7 seconds on every paper with a full-bleed pipeline diagram.

The fix uses PyMuPDF's `Pixmap.shrink` (already a dependency) to halve
dimensions until the longest edge is ≤ 1280px, re-encodes as JPEG q82,
and base64s that instead. On the MEt3R figure this brings the encoded
size from ~1MB to ~260KB (~260K tokens), comfortably under the 1M
context budget. The pipeline figure remains legible at 850×1100 — well
above what's needed for method-overview comprehension.

Also widens the failure log to print full stderr and stdout (truncated
to 2KB each) when claude -p exits non-zero, so future "rc=1 stderr=''"
mysteries surface the JSON envelope's `result` / `terminal_reason`
fields immediately.

### Changed

- `skills/paper-read/scripts/paper_analyzer.py`
  - New `_encode_image_attachment(path)` helper (fitz Pixmap shrink +
    JPEG q82 + base64).
  - `_call_claude_once` now calls the helper instead of base64'ing raw
    PNG bytes.
  - `_call_claude_once` non-zero-exit branch logs `rc`, `stderr[:2000]`,
    and `stdout[:2000]` instead of just truncated stderr.

## v0.9.3 (2026-05-15) — paper-translate: skip BabelDOC's stuck teardown

`translate_with_claude.py` now force-exits the moment the FINISH (or
ERROR) event arrives from BabelDOC's `async_translate`.

BabelDOC 0.5.24 leaves non-daemon executor threads alive after emitting
FINISH; `asyncio.run()` then stalls for ~20 minutes waiting for those
threads, even though the dual.pdf is already on disk. We saw this on a
14-page paper: BabelDOC finished at minute 4, but the Python process
hung until killed at minute 25. The patched script flushes stdio and
calls `os._exit(0)` from inside the event loop the instant FINISH
arrives, since nothing downstream of FINISH is needed by paper-translate
— `build_dual.py` reads the cached `.no_refs.no_watermark.<lang>.dual.pdf`
directly.

### Changed

- `skills/paper-translate/scripts/translate_with_claude.py`
  - New `_force_exit(code)` helper (flush + `os._exit`).
  - `finish` handler now calls `_force_exit(0)` after logging.
  - `error` handler now calls `_force_exit(1)` after logging.

## v0.9.2 (2026-05-14) — arXiv stems include full paper title

The arXiv-download stem changes from `<YYMM>_<short>` to
`<YYMM>_<sanitized-title>`, e.g.

```
old: .phyra/papers/2402_Genie.pdf
new: .phyra/papers/2402_Genie_Generative_Interactive_Environments.pdf
```

The full sanitized title is far more recognisable in a file listing
than a 4–6 char acronym, which matters when a researcher accumulates
dozens of papers in `.phyra/papers/` over time.

### Changed

- `skills/paper-read/scripts/resolve_input.py`
  - New `sanitize_title_for_stem` + `build_stem` helpers. Sanitization
    rules: `": "` → `"_"`, then any remaining `:` → `_`; Windows
    reserved chars (`<>"/\|?*` and control bytes) → `_`; every
    whitespace char → `_`; underscore runs collapsed; stem capped at
    180 chars. **Stems never contain spaces**, so shell drivers do not
    need to quote `$STEM`.
  - The old acronym-derivation pipeline (`derive_short_name` +
    `_good_acronym` + abstract regex patterns + `fetch_arxiv_meta`'s
    abstract scrape) is removed. The stem now depends on the title
    alone — a single pure function, easier to reason about.
  - Fallback when arXiv title fetch fails: `<YYMM>_<arxiv-suffix>`,
    e.g. `2402_15391` from `2402.15391`. Always unique without needing
    abstract parsing.
- `skills/paper-read/SKILL.md` and `skills/paper-translate/SKILL.md`
  - Step-0 examples updated to the new underscore naming.
  - Defensive quoting around `"$OUT_DIR/..."` and `".phyra/.cache/$STEM/..."`
    kept in place so paths still survive a user-supplied cwd or
    OUT_DIR that happens to contain spaces.

### Migration

No action required for new runs. Previously-downloaded PDFs under the
old name (`2402_Genie.pdf`) still resolve via the local-PDF branch of
`resolve_input.py` (which never renames a local file). If you want the
new naming for a paper you already analysed, delete the old PDF +
cache dir and rerun `/phyra:paper-read <arxiv-id>` — the bibliographer
result is cheap to regenerate.

## v0.9.1 (2026-05-05) — `paper-translate` defaults to Sonnet

Translation is a many-call workload (one `claude -p` per BabelDOC chunk;
typically hundreds of calls per paper) so the speed and cost profile of
Sonnet matters more than the deeper reasoning of Opus. Previously the
per-chunk call did not pin a model and inherited the user's default —
which meant Opus when the parent CC session was on Opus, leading to
unnecessarily slow + expensive translations.

### Changed

- `skills/paper-translate/scripts/translate_with_claude.py`
  - New `--model <alias-or-id>` flag, default `sonnet`. The value is
    passed through to each per-chunk `claude --model <name>`
    subprocess invocation.
  - `ClaudeHeadlessTranslator.__init__` takes a new `cli_model`
    parameter; `self.model` (BabelDOC's logical identifier used in
    cache/log lines) is now `claude-headless-<cli_model>` so cache
    entries from different model runs do not collide.
  - The progress log line at startup now prints the resolved model.
- `skills/paper-translate/SKILL.md` and `commands/paper-translate.md`
  expose the new `--model` flag in `argument-hint` and the Step 0
  argument-parsing list. The wired Step 3.2 invocation passes
  `--model $MODEL`.

### Migration

No action required. If you want the previous behavior (inherit the
parent CC session's model), pass `--model opus` (or whichever model
your session uses) explicitly.

## v0.9.0 (2026-05-04) — `paper-translate` extracted as its own command

**BREAKING.** Translation is no longer a flag on `/phyra:paper-read` — it
lives in a new top-level command, `/phyra:paper-translate`. `paper-read`
keeps analysis (Markdown + viewer HTML) and the optional slide deck.

### Why

v0.8.1 already decoupled the *internal* subagents (analyzer / translator
/ slide-maker), but kept them behind a single user-facing command.
Translation has fundamentally different cost shape (BabelDOC + per-chunk
Claude calls = long, expensive, heavy external deps) and dependency
profile (babeldoc + CJK font + optional Ghostscript) than analysis. The
unified command meant:

- `paper-read` preflight had to conditionally check babeldoc/font/gs.
- Users wanting *only* a translated PDF had to run an analyzer pass too.
- Cost asymmetry confused new users — "why does paper-read sometimes
  take 30 seconds and sometimes 30 minutes?"

Splitting the surface API matches the existing internal split.

### Added

- **New command `/phyra:paper-translate`.**
  - Single deliverable: bilingual side-by-side PDF (and optional mono via
    `--mono`).
  - Args: `<paper-pdf-or-arxiv> [--lang-out zh-TW] [--lang-in en] [--mono]
    [--qps 2] [--compress lossy|lossless|off]`. No interactive prompts.
- `commands/paper-translate.md` — slash-command file.
- `skills/paper-translate/SKILL.md` — workflow definition.
- `skills/paper-translate/scripts/preflight.py` — translate-only deps
  check (babeldoc + font + claude + uv + optional gs).

### Moved

- `skills/paper-read/scripts/slice_pdf.py` → `skills/paper-translate/scripts/`
- `skills/paper-read/scripts/translate_with_claude.py` → `skills/paper-translate/scripts/`
- `skills/paper-read/scripts/build_dual.py` → `skills/paper-translate/scripts/`

`translate_with_claude.py` now imports `_retry.py` from the sibling
`skills/paper-read/scripts/` (single source of truth for retry semantics
across all paper-* commands). The path is resolved via
`${CLAUDE_PLUGIN_ROOT}` at runtime, with a `parents[2]` fallback for
standalone runs. `slice_pdf.py` accepts `-` as the PARSED_PAPER argument
to skip parsed lookup and use the PDF heuristic only.

### Changed

- `commands/paper-read.md` — removed `--translate / --no-translate /
  --mono` from `argument-hint` and description; added pointer to
  `/phyra:paper-translate`. Bumped to v0.9.0.
- `skills/paper-read/SKILL.md` — removed Step 5b (translator); renumbered
  Step 5 (analyzer) and Step 6 (slide); removed `bilingual` row from the
  output table; removed `paper-translator` from the subagent table;
  added "See also" section pointing to `/phyra:paper-translate`. Bumped
  to v0.9.0.
- `skills/paper-read/scripts/preflight.py` — removed `--need-translate`,
  `--need-slide`, `--compress`, `LANG_FONT_MAP`, `check_font()`, babeldoc
  check, gs check. Now only checks `${CLAUDE_PLUGIN_ROOT}` + `uv` +
  `claude`. Bumped to v0.9.0.
- `agents/paper-translator.md` — `Inputs` / `Output` sections rewritten
  to come from the `/phyra:paper-translate` orchestrator; output paths
  use `$OUT_DIR` convention (matches paper-read) instead of the old
  `.phyra/reports/<slug>/`. Bumped to v0.9.0.
- `.claude-plugin/plugin.json` + `marketplace.json` — version 0.8.1 →
  0.9.0; description / keywords mention paper-translation.
- `README.md` — architecture diagram now shows 6 commands and the correct
  14-agent set (was still listing the v0.7.0 deprecated agents); added a
  `/phyra:paper-translate` command section; rewrote the `/phyra:paper-read`
  command section to reflect v0.9.0 outputs (analysis MD/HTML + optional
  slide); moved the BabelDOC setup notice from `paper-read` to
  `paper-translate`; updated the Requirements section accordingly.

### Migration notes

Replace `/phyra:paper-read … --translate` with two separate invocations:

```
# Before (v0.8.x)
/phyra:paper-read .phyra/papers/2505_LaCT.pdf --translate --no-slide

# After (v0.9.0)
/phyra:paper-read .phyra/papers/2505_LaCT.pdf --no-slide
/phyra:paper-translate .phyra/papers/2505_LaCT.pdf
```

The two commands share `<cwd>/.phyra/.cache/<STEM>/`, so running them on
the same PDF (in either order) reuses `PARSED_PAPER.md` for ref-page
detection.

### Trade-off acknowledged

`resolve_input.py` and `_retry.py` stay in `skills/paper-read/scripts/`
and `paper-translate` imports them via sibling-skill path lookup. This
isn't 100% decoupled, but avoids ~410 lines of duplicated code that would
need lock-step maintenance. If the two skills ever ship as separate
plugins, promote both helpers to a top-level `lib/`.

---

### Companion refactor (shipped in the same release)

Independent of the paper-translate split, the v0.9.0 release also
absorbs an accumulated refactor across agents, skills, and scripts.
These changes were already in flight when the paper-translate work
started; integrating them now keeps the agent / script ecosystem clean
heading into v0.9.x.

**peer-reviewer unification**

- New `agents/peer-reviewer.md` — a single stance-parameterised
  reviewer. Spawn with `stance: constructive` to write
  `drafts/review-positive.md` (repairability focus) or
  `stance: critical` to write `drafts/review-negative.md` (root-cause /
  boundary / novelty focus). Aborts if stance is missing.
- Removed `agents/peer-reviewer-positive.md` and
  `agents/peer-reviewer-negative.md` (both 80-90 lines of duplicated
  framework). The two stances now share the review framework and only
  diverge in reasoning sequence and stance-specific extra fields
  (`Possible fix direction` for constructive, `Defect type` + `Root
  cause` for critical).
- `commands/paper-review.md` — both NT and AT pipelines updated to spawn
  the unified `peer-reviewer` agent twice with distinct stance
  directives. `peer-reviewer-chair` is unchanged.

**`soul` skill: ethos extracted to references**

- `skills/soul/SKILL.md` slimmed down — the four foundational paragraphs
  (Philosophical / Aesthetic / Ethical / Behavioral) moved out to
  `skills/soul/references/philosophy.md`. The SKILL.md itself now only
  carries the runtime-enforceable global writing constraints, with a
  one-line pointer to the philosophy document for agent authors.
- Rationale: every agent loads `soul`, so paying ~600 tokens per agent
  load for prose that is informational (not enforcement) was wasteful.

**Analyzer prompts externalised**

- New directory `skills/paper-read/scripts/prompts/` with one Markdown
  file per call: `system_base.md`, `a1_overview.md`, `a2_sections.md`,
  `a3_critic.md`, `a4_method.md`, `a5_experiments.md`.
- `skills/paper-read/scripts/paper_analyzer.py` no longer carries the
  prompt strings inline; a small `_load_prompt()` helper reads each
  file at module import time. Edit the `.md` files (the canonical
  source) instead of the Python module when you want to tweak prompt
  wording.

**`md_utils.py` shared between renderers**

- New `skills/paper-read/scripts/md_utils.py` exporting `md_to_html()`
  and `normalize_md()`. Both `build_slide.py` and
  `build_analysis_html.py` previously carried independent copies of the
  same converter (~120 lines each); both now import from `md_utils`.
  `build_analysis_html.py` enables `include_anchor_ids=True` to get the
  TOC-ready heading anchors; `build_slide.py` leaves them off.
- Eliminates the silent-drift risk where the two renderers could
  disagree on what a given Markdown construct looks like.

**`bibliographer.py`: stricter JSON contract**

- The user prompt now ends with an explicit "begin with `{`, end with
  `}`, no preamble, no fences" rule.
- `parse_json_lenient()` simplified to brace-extract (find first `{` to
  last `}`), removing the older two-phase try-direct-then-extract
  pattern that occasionally produced confusing warnings.

**Agent description scope clarifications**

- `agents/content-analyst.md` — description now spells out it's the
  *lightweight diagnostic* counterpart to `paper-analyzer`. Used inside
  `/phyra:paper-review`, `/phyra:paper-graph`, `/phyra:paper-write`.
  Explicitly NOT for `/phyra:paper-read` (which uses `paper-analyzer`).
- `agents/paper-analyzer.md` — symmetric Scope callout: paper-read-only;
  for diagnostic use in the other commands, use `content-analyst`.

**`relationship-mapper` and downstream commands: enforce `citation-network` read**

- `agents/relationship-mapper.md` — `citation-network` skill marked
  mandatory with explicit "you MUST `Read skills/citation-network/
  SKILL.md` before producing any relationship table" instruction.
- `commands/paper-graph.md` and `commands/paper-survey.md` echo the
  same requirement at the dispatch step.
- Reason: relationship tables produced without first reading the
  vocabulary / table-format definitions in citation-network were
  drifting in shape across runs.

**`research-scoring`: predecessor-count rule relaxed**

- The "must identify at least 3 direct predecessor works" requirement
  was overfitting to mature subfields and forced reviewers to invent
  ancestors when the paper genuinely opened a new line. Relaxed to
  "typically 2-4, depending on subfield maturity; fewer is acceptable
  for genuinely new lines, more is acceptable for dense lineages".
- The skill now also opens with an explicit relation note vs
  `peer-review-criteria` — when both are loaded by `peer-reviewer-chair`,
  `peer-review-criteria` wins on disagreement; `research-scoring`
  contributes only the numeric scoring rubric on top.

**Companion HTML asset**

- New `skills/html-color-system/references/palette-index.md` — flat
  lookup table of all 100 traditional Japanese colors used across the
  light (42) and dark (58) themes. Complements the existing
  `palette-light.md` and `palette-dark.md` CSS definitions.

**`agents/paper-bibliographer.md` cleanup**

- A stale Failure-Modes line still mentioned `phyra-analyzer skips
  multimodal entirely`. Updated to refer to the v0.9.0 path
  (`paper-analyzer`'s A4 METHOD call).

**README**

- Subagent table rewritten to reflect the actual 15-agent set
  (previously listed v0.6/v0.7 agents that have been deleted from
  disk: `phyra-analyzer`, `deep-extractor`, `page-annotator`, plus the
  pre-unification `peer-reviewer-positive` / `-negative`).
- `paper-review` pipeline strings updated to `peer-reviewer × 2
  (constructive + critical) -> peer-reviewer-chair` (was still showing
  the old split-agent names).
- Token Usage Reference table rewritten — the v0.7 stages
  (`build_3col`, `validate_layout`, `phyra-analyzer mega-call`) are
  gone; replaced with separate per-stage tables for `/phyra:paper-read`
  and `/phyra:paper-translate`.
- Subagent count corrected (architecture diagram + counts table).
- Skills count consistency: the architecture-diagram subgraph
  previously said "Skills (12)" while the counts table said
  "Skills | 14". The 12 figure counted only knowledge skills (loaded
  by agents); the 14 figure also counted the two workflow skills
  (`paper-read`, `paper-translate`, loaded by commands). Resolved by
  renaming the diagram subgraph to "Knowledge Skills (12)" and adding
  a separate "Workflow Skills (2)" subgraph; the counts-table
  description now spells out the split (12 knowledge + 2 workflow =
  14 total).

**Repo cleanup**

- Removed the empty `docs/` directory (left over from earlier
  redesign-paper-read.md cleanup in v0.8.0).

## v0.8.1 (2026-05-01) — Round-1 user fixes

Round-1 user feedback after v0.8.0 dogfood on LaCT (2505.23884) surfaced
seven concrete defects + three new requirements. Fixed:

### Markdown analysis fixes

- **Inline math abuse.** Analyzer prompt now states the inline / display
  math rule explicitly: `$f_W$` for variables / short symbols inside
  prose, `$$ ... $$` only for standalone equations. The previous prompt
  did not distinguish, and the LLM defaulted to `$$ ... $$` for every
  symbol, breaking reading flow.
- **`Local PDF path` row leaked into §1 Basic Information.** Removed
  from both the `paper-read-notes` template and the A1 OVERVIEW
  prompt — local paths belong on the user's machine, not in the
  artefact.
- **Word-count breakdowns** like `(約 1400 words；§2 約 800、§6 約 600)`.
  Analyzer prompt now mandates `(N words)` exactly, no semicolon, no
  co-section references. As a defensive fallback, slide / HTML renderers
  also strip the breakdown pattern at parse time.

### Slide deck fixes

- **No more whole-page PDF screenshots.** v0.8.0 embedded the
  main_pipeline_figure as a 200 DPI page rasterization, which looked
  like a PDF page glued in mid-deck. Removed entirely until proper
  figure-region cropping lands.
- **Inline math in slides** now renders inline (single-line `$$x$$` is
  rewritten to `$x$` before KaTeX gets to it).
- **Walkthrough slides** (Introduction, Related Work, Conclusion) used
  to be a single wall-of-text card. Now split into multiple cards on
  paragraph boundaries; if the LLM emitted one giant paragraph, the
  renderer soft-splits on Chinese sentence terminators (。 / ；) into
  3-sentence chunks.
- **Bottom bar** rebuilt: nav buttons + index on the left (fixed
  position, no flex jiggle), then the slide title (flex, ellipsis on
  overflow), then the progress bar.

### Architecture clarification

- **Three subagents, clear ownership.** SKILL.md rewritten with a
  responsibilities table: paper-bibliographer / paper-analyzer /
  paper-translator / paper-slide-maker each own exactly one helper
  script, no script crosses agent boundaries. Both paper-translator
  and paper-slide-maker now have explicit agent definitions in
  `agents/`.

### New deliverables

- **`<stem>_analysis.<lang>.html`** — the analysis MD rendered as a
  styled standalone HTML viewer (KaTeX math, sticky TOC, theme that
  matches the slide deck, print-friendly). Browser → print to PDF if
  the user wants a paper copy.

### Output naming + path conventions

- **Local PDF input** (e.g. `2503_USP.pdf`): all outputs land in the
  same directory as the input file, with stem reused:
  - `2503_USP_analysis.zh-TW.md`
  - `2503_USP_analysis.zh-TW.html`
  - `2503_USP_bilingual.zh-TW.dual.pdf`
  - `2503_USP_draftslide.html`
- **arXiv URL or bare ID** (e.g. `https://arxiv.org/abs/2503.06132` or
  `2503.06132`): downloads to `<cwd>/.phyra/papers/<YYMM>_<short>.pdf`,
  outputs land alongside. Short name is derived from the arXiv title's
  bracketed acronym (e.g. `USP: Unified ...` → `USP`), or the first
  CamelCase words. Implemented in
  `skills/paper-read/scripts/resolve_input.py`.

### Bumped

- Plugin → 0.8.1.

## v0.8.0 (2026-05-01) — Decouple analysis / translation / slide

Major refactor. After ~12 papers under v0.7.x, the 3-column trilingual PDF
revealed three structural problems: (1) cover panels truncated long
`research_topic` and `core_argument` paragraphs, (2) the per-page Phyra
column took ~27% of page width and proportionally shrank both the original
and translation columns, hurting readability, and (3) ASCII-only mono
blocks made `Method Anatomy` covers hard to follow. The fix is to **stop
forcing analysis, translation, and layout into the same artefact**.

### Architecture

`/phyra:paper-read` now produces three decoupled deliverables:

1. **`analysis.<lang>.md`** (always): a comprehensive Markdown analysis
   following the `paper-read-notes` template. No layout budgets; the
   long-form `research_topic` / `core_argument` are no longer truncated.
   New §3 "Section Walkthrough" walks the paper section by section. §5
   "Methodology Deep Dive" is centered on a Markdown tensor-shape pipeline
   diagram with per-module breakdown.
2. **`bilingual.<lang>.dual.pdf`** (opt-in): BabelDOC's dual side-by-side
   bilingual PDF, **without a Phyra column**. References are sliced before
   translation (cost saving) and re-injected as placeholder pages.
3. **`slide.html`** (opt-in): a fixed slide-deck HTML (left/right keyboard
   navigation, `slide-theme.md` styling), 12–22 slides covering cover →
   overview → paper structure → method → experiments → conclusion. Embeds
   the main pipeline figure and other key figures.

### New

- `agents/paper-analyzer.md` — replaces `phyra-analyzer`. Emits MD, not JSON.
- `agents/paper-slide-maker.md`, `agents/paper-translator.md` — thin
  agent definitions delegating to scripts.
- `skills/paper-read/scripts/paper_analyzer.py` — 5-call orchestrator
  (A1 OVERVIEW, A2 SECTIONS, A3 CRITIC, A4 METHOD, A5 EXPERIMENTS) with
  optional AT-mode parallelism.
- `skills/paper-read/scripts/extract_figures.py` — rasterizes figure pages
  from PARSED_PAPER and the BIBLIO main_pipeline_figure.
- `skills/paper-read/scripts/build_dual.py` — stitches BabelDOC's no-refs
  dual.pdf with the original PDF's ref pages (refs displayed as placeholder
  on the translation side). [G2 phase]
- `skills/paper-read/scripts/build_slide.py` — assembles the analysis MD +
  figures into a single self-contained HTML slide deck. [G3 phase]
- `skills/paper-read/scripts/_retry.py` — 30 min × 50 retries on rate-limit
  responses, applied to bibliographer / analyzer / translator subprocess
  calls. [G4 phase]
- `BIBLIO.json` schema gains `core_argument` (≤400-word paragraph).
- `paper-read-notes` template gains §3 Section Walkthrough; §5 expanded
  with explicit tensor-shape pipeline; §3.x Impact Rating dropped (folded
  into §7 Phyra's Judgment).

### Removed

- `agents/phyra-analyzer.md`, `agents/page-annotator.md`,
  `agents/deep-extractor.md`.
- `skills/paper-read/scripts/phyra_analyzer.py`,
  `skills/paper-read/scripts/build_3col.py`,
  `skills/paper-read/scripts/budget.py`,
  `skills/paper-read/scripts/validate_layout.py`,
  `skills/paper-read/scripts/page_annotator.py`,
  `skills/paper-read/scripts/deep_extractor.py`.
- The `--compress` flag (no PDF emitted from this command's analysis path
  anymore; BabelDOC dual.pdf is passed through unmodified).

### CLI

```
/phyra:paper-read <paper-file-path-or-arxiv-url>
    [--lang-out zh-TW]
    [--translate | --no-translate]   # default: ask
    [--slide     | --no-slide]       # default: ask
    [--mono]                         # also emit monolingual translated PDF
    [--at]                           # parallel mode for the analyzer 5-call split
```

## v0.7.3 (2026-04-28) — Round 1 self-debug

Round-1 of the multi-round /phyra:paper-read self-debug loop. Visual
inspection of the 3 baseline cover-3 PDFs surfaced two systemic bugs;
running the fixed pipeline on a 4th paper (ViT³ `2512.01643`) surfaced
a third pre-existing crash.

**Bug A — `module_spec` "Formulas" label overlapped Processing tail.**
Root cause: SourceHanSerifTW renders prose at ~FS*1.61 baseline-to-baseline
while `LH_BODY` predicted at FS*1.55. Over 21+ lines actual text crept
~17pt past the predicted rect bottom; PyMuPDF `insert_textbox` rendered
the overflow but returned a `rc` value smaller than actual rendered
height, so `cur_y` advanced too little and the next sub-field label
landed on top of the previous body.

**Fix:** bump `LH_BODY` 1.55 → 1.70 and `LH_MONO` 1.35 → 1.45 to bracket
the actual rendering. Pass a 2x-tall safety rect so `insert_textbox` never
has to overflow. Advance `cur_y` by *predicted* `box_h` rather than the
unreliable `used` returned by `_safe_insert_textbox`. Applied uniformly
to `render_summary`, `render_mono`, `render_module_spec`, `render_list`,
`render_judgment`, `render_callout`, `render_concern`, `render_crossref`.

**Bug B — `_wrap_lines` broke tensor shapes mid-token.**
Examples: `depth_m` → `dept` \n `h_m`; `[B, 3, H, W]` → `[B, 3` \n `, H, W]`;
`pose P_t` → `pos` \n `e P_t`. Root cause: pure character-count cut at
`max_chars` with no word/bracket awareness.

**Fix:** rewrote `_wrap_lines` as bracket-depth-aware. Tracks `[]/(){}`
nesting and only breaks at depth-0 whitespace or `, / ; |` punctuation
within `[max_chars*0.5, max_chars]`. Tensor shapes like `[B, 3, H, W]`
and function calls `f(x, y)` now stay intact.

**Bug C — `subprocess.run` `ValueError: embedded null byte`.**
Surfaced on ViT³: PyMuPDF occasionally emits `\x00` inside ligatures or
stray PDF metadata; subprocess args go through `exec()` which interprets
`\x00` as the C-string terminator, raising before claude is invoked.

**Fix:** `_sanitize_for_subprocess(s)` strips `\x00-\x08\x0b\x0c\x0e-\x1f\x7f`
from both prompt and system_prompt in `bibliographer.py` and
`phyra_analyzer.py`.

### Files touched

- `skills/paper-read/scripts/build_3col.py` — LH_BODY/LH_MONO bumps,
  `_wrap_lines` rewrite, all renderer cur_y advancement switched from
  `used` to predicted `box_h`.
- `skills/paper-read/scripts/bibliographer.py` — sanitize prompt/system.
- `skills/paper-read/scripts/phyra_analyzer.py` — sanitize prompt/system.

## v0.7.2 (2026-04-27)

### Cover pages: adaptive height + Cover 3 redesign + auto-thinned author table

Three cover-related polishes after v0.7.1 verification:

1. **Adaptive cover height** — covers no longer forced to A4 page height. `render_cover_page` now creates the page at 3× scratch height, tracks each panel's deepest cur_y, then crops with `set_mediabox` to `max(deepest_y) + bottom_pad`. A short cover (e.g. Critical Profile, halves layout with 5-7 highlights + 5-7 weaknesses + judgment footer) renders at ~43% A4 height instead of leaving the bottom 60% blank. A dense cover (Method & Experiments, thirds layout with framework + module specs) extends to ~110% A4 if needed instead of truncating. Each cover is its own page; PDF readers display variable-height pages cleanly.

2. **Cover 3 redesign** — dropped `info_table Datasets` and `info_table Main Results` (low information density vs space cost). New thirds layout:
   - Panel L: `module_spec` Framework (with explicit tensor shapes — unchanged)
   - Panel M: `module_spec` for top module(s)
   - Panel R: `list` Improvement Directions + `list` Ablation Highlights

3. **Auto-thinned Authors table** — phyra-analyzer system prompt rule 8: if MOST authors have null homepage, OMIT the Homepage column entirely (3-col Name | Affiliation | Role) instead of rendering empty cells across a 4-col table.

### Files touched

- `skills/paper-read/scripts/build_3col.py` — `render_cover_page` adaptive height (`set_mediabox` after measure-and-render)
- `skills/paper-read/scripts/phyra_analyzer.py` — GLOBAL_USER_TMPL Cover 3 spec rewrite, GLOBAL_SYSTEM_PROMPT rule 8 (Authors thinning)
- `.claude-plugin/plugin.json` + `marketplace.json` — 0.7.1 → 0.7.2

## v0.7.1 (2026-04-27)

### `phyra-analyzer` split into 4 calls — fixes mid-generation truncation on dense math papers

v0.7.0's mega-call asked claude headless for the entire `PHYRA_ANALYSIS.json` (~30 KB output) in a single `claude -p` invocation. For dense math papers (e.g. Scal3R `2604.08542`) the model exhausted its effective output token budget on internal reasoning before completing the JSON, returning ~300-1000 chars instead of the full structure and triggering the fallback path. v0.7.1 splits the work into four narrower calls:

- **C1 GLOBAL** — `covers[3]` + `highlights[]` + `ref_pages` + `total_pages`. ~10 KB output.
- **C2 INTRO/RW** — `pages[]` for Introduction / Related Work / Background pages.
- **C3 METHOD** — `pages[]` for Method / Approach / Architecture pages. The `main_pipeline_figure` PNG is embedded here only.
- **C4 EXP/CONCL** — `pages[]` for Experiments / Discussion / Conclusion / Appendix pages.

C1 must run first (its output decides `ref_pages`, which the section calls then exclude). C2/C3/C4 are independent and run in parallel by default (AT mode = on; `--nt` flag forces serial). Section bucketing is heuristic: `phyra_analyzer.py` scans each page for header text matching one of three regex sets (intro/method/exp) and assigns the page to the most recently seen bucket; ref pages are absorbed by `REF_RX` and excluded from all three section calls.

The merged JSON keeps schema_version 4 unchanged (this is purely a production strategy change). Per-page block cap, highlight density target, ASCII-only mono-block rule, and budget enforcement are unchanged.

### Files touched

- `skills/paper-read/scripts/phyra_analyzer.py` — rewrote orchestrator (`analyze_global` + `analyze_section` + `merge_results` + `detect_section_buckets`)
- `agents/phyra-analyzer.md` — describe 4-call flow
- `skills/paper-read/SKILL.md` — note `--nt` flag (AT default for analyzer)
- `.claude-plugin/plugin.json` + `marketplace.json` — 0.7.0 → 0.7.1

## v0.7.0 (2026-04-27)

### 4-agent architecture rewrite

Paper-read pipeline regrouped from 4 agents (paper-parser + content-analyst + deep-extractor + page-annotator) into a 4-role architecture:

- **Agent A** — `paper-bibliographer` (NEW): basic info, authors with WebSearch-verified affiliations + homepages, venue, related lineage, keywords, research topic, domain, and the page+label of the main pipeline figure. Output: `BIBLIO.json`.
- **Agent B** — `phyra-analyzer` (NEW): one mega-call that produces 3 fixed-grid cover pages, 25-40 categorized highlights, AND per-page bespoke phyra-column blocks all in one unified `PHYRA_ANALYSIS.json` (schema v4). Replaces v0.6.0's content-analyst + deep-extractor + page-annotator for paper-read. (Those agents remain in the repo for other commands and standalone use; marked `[DEPRECATED in v0.7.0]` for paper-read.)
- **Agent C** — translation (existing `translate_with_claude.py` / BabelDOC) — now operates on a sliced PDF with reference pages stripped.
- **"Agent D"** — `validate_layout.py` (NEW): pure Python dry-run that estimates per-cell line counts and warns on overflow.

`paper-parser` is retained (still needed for slice-pdf detection of References start page and for analyzer context).

### Cover pages: 3 fixed pages with grid layouts

Previous v0.6.0 had up to 4 single-column cover pages with no overflow protection (final cover often truncated). v0.7.0:

- **Cover 1** — `single` (full-width column flow): Basic Info + Authors + Research Topic + Core Argument + Related Lineage
- **Cover 2** — `halves` (1:1): Highlights | Weaknesses+Pain Points, with Phyra Judgment as full-width footer
- **Cover 3** — `thirds` (1:1:1): Framework (with explicit tensor shapes) | Modules + Improvement Directions | Datasets + Main Results + Ablations

`render_cover_page` now dispatches on `cover.layout` ∈ {single, halves, thirds}. Each panel has a fixed rect; on overflow a `… ⚠ truncated` marker is stamped (no silent content loss).

### Content budgeting (`budget.py`, `validate_layout.py`)

The phyra-analyzer prompt embeds a `BUDGETS.json` payload computed from page geometry:
- per-cover-panel `max_lines` and `max_chars_per_line` (CJK-aware: ~1.0× fontsize, ASCII ~0.55×)
- per-page phyra column: `max_lines=28`, `max_chars_cjk=30`, `target_fill_pct=60` (so non-ref pages aim to fill 60% of the column with real content, not echoes)

`validate_layout.py` runs the same math against the LLM output as a dry-run; logs overflow per panel/page.

### Highlights: 25-40 categorized sentences forming a "condensed paper"

Previous v0.6.0 produced 10-15 ungrouped highlights — too sparse to read coherently. v0.7.0 schema adds `category` ∈ {claim, method, result, conclusion, limitation} with target counts (claim 5-8, method 8-12, result 8-12, conclusion 3-5, limitation 0-3). Phyra-analyzer system prompt requires the highlight set to read as a coherent 3-5 paragraph condensed paper when extracted alone.

Side artefact: `<slug>.highlights.txt` is auto-exported next to the final PDF, listing every yellow sentence by category and page so readers can verify coherence without scrolling the PDF.

### `?` characters: three-line defense

Root causes from v0.6.0:
1. Box-drawing tree-prefix glyphs (`└─`, `├─`, `│`, `─`) — Courier (PyMuPDF built-in `cour`) doesn't have them.
2. CJK explanations placed inside `formula` / `diagram` / `table` body fields — Courier is Latin-only.
3. `render_formula`'s `" | "` separator was unreliable; LLMs split formula and CJK gloss with `\n` instead.

Defenses:
1. `_ascii_safe` / `GREEK_TO_ASCII` expanded to map all box-drawing chars to ASCII (`└` → `+--`, `├` → `|--`, `│` → `|`, `─` → `-`, etc.).
2. Phyra-analyzer system prompt (rule 5): mono blocks ASCII-ONLY; CJK explanations must go in a separate `summary` / `prose` / `concern` block.
3. `render_mono` now detects CJK in body after `_ascii_safe` and falls back to the proportional CJK font (alignment is lost but `?` chars are unacceptable).
4. `render_formula` auto-splits CJK gloss when no `" | "` is present (first CJK-bearing line and onward go to gloss).
5. `build_3col.py` end-of-build sanity check counts `?` chars across the final PDF and warns.

### Multimodal: from 5-12 pages → 1 page per paper

The v0.6.0 keyword heuristic (`needs_image`) over-fired on 5-12 pages per 22-page paper. v0.7.0 strategy:
- Agent A extracts `main_pipeline_figure: {page, fig_label, caption_excerpt}` — only the END-TO-END architecture figure.
- Agent B rasterizes only that page (plus any `--multimodal-pages 3,7` user override) at 150 DPI, embeds as `[image: path]` in the prompt.

### References: not translated, "skipped" placeholder rendered

`slice_pdf.py` detects the References / Bibliography start page (PARSED_PAPER first, PDF text scan fallback) and writes `<slug>.no_refs.pdf` + `slice_meta.json`. BabelDOC translates only the sliced PDF, saving ~30% wall-clock + cost. `build_3col.py` reconstructs the full page count using the original (un-sliced) PDF for the original column on ref pages, and renders a grey "[reference page — translation skipped]" placeholder in the translation column.

### `--compress` flag

`build_3col.py` adds a post-process compress step:
- `lossy` (default): Ghostscript `/ebook` — downsamples embedded images to 150 DPI, ~50-70% size reduction (e.g. 26-44 MB → ~10 MB). Preflight checks `gs --version`.
- `lossless`: PyMuPDF re-save with `garbage=4 + use_objstms=True + clean=True` — 5-10% reduction without quality loss.
- `off`: no-op.

### Schema v4 (breaking)

`page_notes.json` (v3) renamed `PHYRA_ANALYSIS.json` (v4). Hard cut: `build_3col.py` refuses schema ≠ 4. v0.6.0 caches must be regenerated (delete `.phyra/.cache/<slug>/page_notes.json`).

Schema additions: `ref_pages`, `main_pipeline_figure`, `covers[].layout`, `covers[].panels[].blocks`, `covers[].footer`, `highlights[].category`, plus a new `prose` block type (free-form paragraph, lower bar than `summary`).

### Files touched

- `agents/paper-bibliographer.md` (new)
- `agents/phyra-analyzer.md` (new)
- `agents/deep-extractor.md` (deprecated header)
- `agents/page-annotator.md` (deprecated header)
- `skills/paper-read/SKILL.md` (rewritten — 4-agent flow, A→parser→slice→[B|C]→D→build→compress)
- `skills/paper-read/scripts/bibliographer.py` (new)
- `skills/paper-read/scripts/phyra_analyzer.py` (new)
- `skills/paper-read/scripts/budget.py` (new)
- `skills/paper-read/scripts/slice_pdf.py` (new)
- `skills/paper-read/scripts/validate_layout.py` (new)
- `skills/paper-read/scripts/build_3col.py` (cover grid renderer, GREEK_TO_ASCII expansion, render_mono CJK fallback, render_formula auto-split, schema v4, ref-page handling, compress_pdf, highlights digest)
- `skills/paper-read/scripts/preflight.py` (gs check when --compress=lossy)
- `.claude-plugin/plugin.json` + `marketplace.json` (0.6.0 → 0.7.0)

## v0.6.0 (2026-04-27)

### Cover pages + structured extraction + highlight overlay

- New **deep-extractor** agent runs after content-analyst. Produces `DEEP_EXTRACT.json` with: basic_info, authors, related_lineage, keywords, research_topic, domain, core_argument, highlights, weaknesses, pain_points, method (overview, framework_diagram_text, modules with Function/Input/Output/Processing/Formulas), experiments (datasets, training_details, metrics, main_results, ablations), phyra_judgment (prose), improvement_directions, evidence_sentences.
- **N cover pages** (full-width single-column phyra-only) prepended before content pages. Cover 1 = paper card (Basic + Authors + Lineage + Topic + Argument), Cover 2 = critical profile (Highlights + Weaknesses + Phyra's Judgment + Improvements), Cover 3 = method anatomy (Overview + Framework + Module specs), Cover 4 = experiments anatomy (Datasets + Metrics + Training + Main Results + Ablations). Skipped automatically if a section is empty.
- **Yellow highlight overlay** on the original column. Uses content-analyst's evidence-cited sentences (verbatim PDF substrings via PyMuPDF `search_for`); semi-transparent (`opacity=0.4`) yellow rect drawn after `show_pdf_page`. Translation column not highlighted in v0.6.0 (alignment is harder; deferred to v0.6.x).

### 4 new block types

`info_table` (key-value or column table), `module_spec` (Function/Input/Output/Processing/Formulas), `list` (numbered items, cover-only), `judgment` (prose with bar, cover-only). Per-page bespoke pages can also use `info_table`/`module_spec` when anchored to a specific module/dataset page.

### Greek-symbol safety net

Monospace block bodies (`diagram` / `table` / `formula` / `module_spec` Input/Output/Formulas sub-fields) get a Python-side replacement of common Greek/math Unicode (`λ` → `lambda`, `∞` → `infty`, `∈` → `in`, `≤` → `<=`, etc.) because PyMuPDF's built-in Courier font lacks those glyphs. The page-annotator + deep-extractor prompts also instruct LLMs to use ASCII tokens directly.

### Schema bump

`page_notes.json` schema_version 2 → 3 (cover_pages + highlights + pages). Hard-cut. Stale v2 files cause `build_3col.py` to refuse and require regeneration.

### Files touched

- `agents/deep-extractor.md` (new)
- `agents/page-annotator.md` (new schema, new block types)
- `skills/paper-read/SKILL.md` (insert deep-extractor as Step 4)
- `skills/paper-read/scripts/deep_extractor.py` (new)
- `skills/paper-read/scripts/page_annotator.py` (cover composition + highlight passthrough)
- `skills/paper-read/scripts/build_3col.py` (cover renderer + 4 new block renderers + highlight overlay)

## v0.5.0 (2026-04-26)

### Phyra column v2 — content-adaptive bespoke annotations

Replaces the v0.4.0 fixed 4-section template (claims / method_notes / experiment_notes / questions). The Phyra column now produces per-page bespoke blocks chosen by the LLM from a closed enum of 7 types:

- `summary` — distillation of dense narrative pages
- `diagram` — ASCII pipeline / architecture / data flow with concrete tensor shapes (monospace)
- `table` — small comparison table (monospace grid)
- `formula` — equation + brief gloss (monospace + prose)
- `callout` — what this figure actually demonstrates (italic + bar)
- `concern` — red flag traced to ANALYSIS_REPORT (warning glyph + red bar)
- `crossref` — `→ p.X` pointer

Empty pages render only the breadcrumb header and a faint centered `·` glyph (no fake "no notes" label).

Cap of 3 blocks per page; truncation marker if more apply (`… see ANALYSIS_REPORT.md`).

### Layout: 0.5:1:1 → 0.75:1:1 + larger fonts

- Phyra column widened from `0.5 : 1 : 1` to **`0.75 : 1 : 1`** so monospace diagrams have room
- Body font 8.5pt → **10.5pt** (now matches the translation column body size)
- Header / title fonts also bumped (12pt / 11pt)
- Two grey vertical dividers preserved (between Phyra | Original and between Original | Translation)

### Selective multimodal page input

For pages classified as `method-pipeline` (by section name or figure caption keywords), `page_annotator.py` rasterizes the page to PNG at 150 dpi and includes the path in the prompt. Claude Code's headless mode reads the image internally via its Read tool — no API key, no special multimodal flag. Other page types stay text-only to keep the mega-call cheap.

### Schema v2 (breaking)

`page_notes.json` schema bumped 1 → 2. Hard cut: `build_3col.py` refuses to render schema-v1 files. Migration is automatic — `page_annotator.py` regenerates from the cached PARSED_PAPER + ANALYSIS_REPORT (~1 minute).

### Files touched

- `agents/page-annotator.md` — drop fixed-section language, describe 7 block types + classification
- `skills/paper-read/scripts/page_annotator.py` — new SYSTEM_PROMPT + 3 worked examples + selective multimodal + v2 validator
- `skills/paper-read/scripts/build_3col.py` — block dispatcher, geometry change, font bump, empty-page glyph
- `docs/redesign-paper-read.md` — §4 rewritten

## v0.4.0 (2026-04-26)

### `/phyra:paper-read` redesigned to a single trilingual PDF
- Output replaced: `<slug>-slides.html` + `<slug>-reading-notes.md` → `<slug>.<lang_out>.phyra3col.pdf`
- Three-column layout (analysis | original | translation), width ratio 0.5 : 1 : 1
- Translation uses BabelDOC + a custom `BaseTranslator` that subprocess-spawns `claude -p` headless — no API key required
- Target language is parameterizable via `--lang-out`; default `zh-TW`
- New `page-annotator` agent projects the global ANALYSIS_REPORT onto specific pages
- Other commands (paper-review, paper-survey, paper-graph, paper-write) keep using html-reporter / md-reporter unchanged

### Plugin packaging
- `commands/paper-read.md` removed; replaced by `skills/paper-read/SKILL.md` with helper scripts under `skills/paper-read/scripts/`
- `${CLAUDE_PLUGIN_ROOT}` adopted as the path-resolution convention for skill scripts (first usage in Phyra)
- BabelDOC is **not bundled**; users install via `uv tool install babeldoc==0.5.24` and run `babeldoc --warmup` once
- New `preflight.py` script gates the pipeline and prints copy-paste install hints on failure

### License
- Switched from CC-BY-NC-4.0 to **Apache-2.0**
- Reason: CC explicitly recommends against using CC licenses for software (no patent grant; "NonCommercial" is undefined for code). Apache-2.0 has an explicit patent grant, OSI-approved, and is compatible with downstream GPL/AGPL combinations
- BabelDOC's AGPL-3.0 does not propagate: Phyra calls BabelDOC via subprocess, which the FSF FAQ classifies as mere aggregation, not linking

### Subagents
- New: `page-annotator` (sonnet)
- Total: 13 (was 12)

## v0.3.0 (2026-04-06)

### Restructured as Official Claude Code Plugin
- Migrated to official Claude Code plugin format with `.claude-plugin/plugin.json` manifest
- Added marketplace support (`.claude-plugin/marketplace.json`)
- Removed `phyra-` prefix from all component names (plugin namespace `phyra:` handles namespacing)
- Translated all content from Chinese/English mixed to English-only (`main` branch)
- Chinese version preserved in `zh-hant` branch
- Removed custom install/uninstall scripts (replaced by plugin system)
- Removed `src/` wrapper directory (files now at plugin root)
- Removed `doc/` directory (content merged into README.md)
- Commands now invoked as `/phyra:paper-read`, `/phyra:paper-review`, etc.

## [0.2.1] - 2026-04-06

### Changed
- Background layers now use nipponcolors.com PNG assets (`texture.png`, `gloss.png`) instead of CSS-only fallbacks
- Theme switcher `<select>` text forced to black (`#1C1C1C`) on white background for readability
- Content width is now adjustable via a draggable handle on the right edge
- Graph containers now include a fullscreen toggle button

## [0.2.0] - 2026-04-05

### Added
- `phyra-typography` skill: independent typography constraints extracted from phyra-soul
- `phyra-html-color-system` skill: dedicated color system with 100 Japanese themes (42 light + 58 dark), 3-layer CSS background, dropdown theme switcher, and per-report-type color rules
- `phyra-ai-vocab-blacklist.md`: vocabulary blacklist for academic writing (6 categories, 61 entries)
- KaTeX LaTeX rendering support in HTML reports
- D3.js v7 graph interactivity (zoom, drag, gradient nodes)
- Unified footer format for all HTML reports

### Changed
- `phyra-peer-reviewer-chair` now loads `phyra-typography` and `phyra-soul` skills
- `phyra-html-slide-format` stripped of color content (moved to phyra-html-color-system)
- Theme switcher changed from Next/Random buttons to select dropdown + Random
- `phyra-paper-review` Step 5 explicitly instructs chair to read review-example.md
- `phyra-soul` typography rules replaced with reference to phyra-typography skill

### Removed
- `phyra-html-slide-format/references/` directory (4 files migrated to phyra-html-color-system)

## v0.1.0 (2026-04-04)

Initial release of Phyra.

- 10 Skills (academic reading, peer review, scoring, literature search, citation network, HTML/MD report formats, paper writing, experiment design, soul)
- 12 Subagents (paper parser, content analyst, dual reviewers + chair, literature searcher, relationship mapper, HTML/MD reporters, paper writer, experiment planner, story architect)
- 5 Commands (paper-review, paper-read, paper-survey, paper-graph, paper-write)
- 100-theme Japanese color system (nipponcolors.com)
- NT (sequential) and AT (Agent Teams parallel) execution modes
- Install scripts for macOS/Linux/Windows
