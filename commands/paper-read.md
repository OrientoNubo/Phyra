---
description: "Read and analyze an academic paper, generating HTML slide report and MD reading notes"
argument-hint: "<paper-file-path> [--at]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "Agent", "SendMessage"]
---

# /phyra:paper-read

> Paper reading workflow: parse, deep analysis, produce HTML slide report and MD reading notes. Supports NT (sequential) and AT (parallel) execution modes.

## Step 0 — Parse arguments and load soul

Parse `$ARGUMENTS` to extract:

- **paper-file-path**: the path to the academic paper (required). If missing, abort
  with a clear error message listing usage: `/phyra:paper-read <paper-file-path> [--at]`.
- **--at flag**: if present, execute in AT (Agent Teams) mode. Otherwise default to
  NT (sequential) mode.

Store the resolved absolute path as `$PAPER_PATH` and the mode as `$MODE`.

**Before any other work, load the `soul` skill.** This establishes Phyra's soul
core and must be active for the entire workflow. All subagents inherit this foundation.

---

## NT Mode (default — sequential subagent execution)

Execute the following steps strictly in order. Each step must finish before the next
begins. Pass results forward through the conversation context.

### Step 1 — paper-parser

Invoke the `paper-parser` agent.

- **Input**: `$PAPER_PATH`
- **Output**: structured extraction document (title, authors, sections, figures,
  tables, references, detected-issues). No evaluative content.
- Store the extraction as `$PARSED_PAPER`.

### Step 2 — content-analyst

Invoke the `content-analyst` agent.

- **Input**: `$PARSED_PAPER` and `$PAPER_PATH` (for cross-referencing original text)
- **Output**: deep analysis report including claim map, methodology assessment,
  contribution summary, and key findings. Store as `$ANALYSIS_REPORT`.

### Step 3 — html-reporter

Invoke the `html-reporter` agent.

- **Input**: `$ANALYSIS_REPORT` and `$PARSED_PAPER`
- **Output**: a self-contained HTML slide report designed for visual presentation.
  The report should include key figures, contribution highlights, methodology
  overview, and results summary in a navigable slide format.
- Writes output to `.phyra/reports/<paper-slug>-slides.html`.

### Step 4 — md-reporter

Invoke the `md-reporter` agent.

- **Input**: `$ANALYSIS_REPORT` and `$PARSED_PAPER`
- **Output**: comprehensive Markdown reading notes structured for reference and
  annotation. Includes section-by-section summaries, critical observations,
  key equations and definitions, and open questions.
- Writes output to `.phyra/reports/<paper-slug>-reading-notes.md`.

---

## AT Mode (Agent Teams — parallel execution)

When `--at` is detected, use Agent Teams for parallelizable steps. Synchronous
barriers are enforced where downstream agents depend on upstream output.

### Step 1 — paper-parser (sync barrier)

Spawn `paper-parser` and **wait for completion** before proceeding.

- **Input**: `$PAPER_PATH`
- **Output**: `$PARSED_PAPER` (structured extraction)

### Step 2 — content-analyst (sync barrier)

Spawn `content-analyst` and **wait for completion** before proceeding.

- **Input**: `$PARSED_PAPER`, `$PAPER_PATH`
- **Output**: `$ANALYSIS_REPORT` (deep analysis report)

### Step 3 — [html-reporter || md-reporter] (parallel)

Spawn both reporter agents **in parallel** using Agent Teams:

- **html-reporter**:
  - Input: `$ANALYSIS_REPORT`, `$PARSED_PAPER`
  - Output: writes `.phyra/reports/<paper-slug>-slides.html`

- **md-reporter**:
  - Input: `$ANALYSIS_REPORT`, `$PARSED_PAPER`
  - Output: writes `.phyra/reports/<paper-slug>-reading-notes.md`

Wait for **both** to complete before proceeding.

---

## Post-workflow

After the workflow completes (in either mode), report to the user:

1. Confirm which mode was used (NT or AT).
2. List the files produced and their locations.
3. Provide a brief summary of the paper's key contributions from the analysis report.
