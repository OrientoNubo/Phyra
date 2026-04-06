---
description: "Comprehensive peer review of an academic paper with dual reviewers and an AC chair"
argument-hint: "<paper-file-path> [--at]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "WebSearch", "WebFetch", "Agent", "SendMessage"]
---

# /phyra-paper-review

> 雙審稿人 + AC chair 的完整同行審稿流程。支援 NT（順序）與 AT（平行）兩種執行模式。

## Step 0 — Parse arguments and load soul

Parse `$ARGUMENTS` to extract:

- **paper-file-path**: the path to the academic paper (required). If missing, abort
  with a clear error message listing usage: `/phyra-paper-review <paper-file-path> [--at]`.
- **--at flag**: if present, execute in AT (Agent Teams) mode. Otherwise default to
  NT (sequential) mode.

Store the resolved absolute path as `$PAPER_PATH` and the mode as `$MODE`.

**Before any other work, load the `phyra-soul` skill.** This establishes Phyra's soul
core and must be active for the entire workflow. All subagents inherit this foundation.

---

## NT Mode (default — sequential subagent execution)

Execute the following steps strictly in order. Each step must finish before the next
begins. Pass results forward through the conversation context.

### Step 1 — phyra-paper-parser

Invoke the `phyra-paper-parser` agent.

- **Input**: `$PAPER_PATH`
- **Output**: structured extraction document (title, authors, sections, figures,
  tables, references, detected-issues). No evaluative content.
- Store the extraction as `$PARSED_PAPER`.

### Step 2 — phyra-content-analyst

Invoke the `phyra-content-analyst` agent.

- **Input**: `$PARSED_PAPER` and `$PAPER_PATH` (for cross-referencing original text)
- **Output**: claim map (each claim linked to supporting evidence) and experiment
  sufficiency evaluation. Store as `$ANALYSIS_REPORT`.

### Step 3 — phyra-peer-reviewer-positive

Invoke the `phyra-peer-reviewer-positive` agent.

- **Input**: `$PAPER_PATH`, `$PARSED_PAPER`, and `$ANALYSIS_REPORT`
- **Output**: a positive-leaning review draft written to `.phyra/drafts/review-positive.md`.
  This reviewer highlights strengths, contributions, and potential while noting
  weaknesses constructively.

### Step 4 — phyra-peer-reviewer-negative

Invoke the `phyra-peer-reviewer-negative` agent.

- **Input**: `$PAPER_PATH`, `$PARSED_PAPER`, and `$ANALYSIS_REPORT`
- **Output**: a critical review draft written to `.phyra/drafts/review-negative.md`.
  This reviewer focuses on methodological gaps, unsupported claims, missing baselines,
  and reproducibility concerns.

### Step 5 — phyra-peer-reviewer-chair

Invoke the `phyra-peer-reviewer-chair` agent.

- **Input**: reads `.phyra/drafts/review-positive.md` and `.phyra/drafts/review-negative.md`.
  The chair also reads `~/.phyra/examples/review-example.md` as format reference.
  The chair does NOT receive the original paper or analysis report directly.
- **Process**: performs divergence analysis between the two reviews, identifies points
  of disagreement, and queries the respective reviewers (via follow-up in
  conversation) to resolve ambiguities.
- **Output**: writes two final documents:
  - `peer-review-report.md` — synthesized review with reconciled assessments
  - `review-scoring-report.md` — structured scoring across standard review dimensions

---

## AT Mode (Agent Teams — parallel execution)

When `--at` is detected, use Agent Teams for parallelizable steps. Synchronous
barriers are enforced where downstream agents depend on upstream output.

### Step 1 — phyra-paper-parser (sync barrier)

Spawn `phyra-paper-parser` and **wait for completion** before proceeding.

- **Input**: `$PAPER_PATH`
- **Output**: `$PARSED_PAPER` (structured extraction)

### Step 2 — phyra-content-analyst (sync barrier)

Spawn `phyra-content-analyst` and **wait for completion** before proceeding.

- **Input**: `$PARSED_PAPER`, `$PAPER_PATH`
- **Output**: `$ANALYSIS_REPORT` (claim map + experiment evaluation)

### Step 3 — [phyra-peer-reviewer-positive || phyra-peer-reviewer-negative] (parallel)

Spawn both reviewer agents **in parallel** using Agent Teams:

- **phyra-peer-reviewer-positive**:
  - Input: `$PAPER_PATH`, `$PARSED_PAPER`, `$ANALYSIS_REPORT`
  - Output: writes `.phyra/drafts/review-positive.md`

- **phyra-peer-reviewer-negative**:
  - Input: `$PAPER_PATH`, `$PARSED_PAPER`, `$ANALYSIS_REPORT`
  - Output: writes `.phyra/drafts/review-negative.md`

Wait for **both** to complete before proceeding.

### Step 4 — phyra-peer-reviewer-chair

Spawn `phyra-peer-reviewer-chair` after both reviewers have finished.

- **Input**: reads `.phyra/drafts/review-positive.md`, `.phyra/drafts/review-negative.md`,
  and `~/.phyra/examples/review-example.md` (format reference)
- **Process**: performs divergence analysis. In AT mode the chair agent can use
  `SendMessage` to directly query the still-active reviewer agents for clarification
  on specific points of disagreement.
- **Output**: writes `peer-review-report.md` and `review-scoring-report.md`

---

## Post-workflow

After the workflow completes (in either mode), report to the user:

1. Confirm which mode was used (NT or AT).
2. List the files produced and their locations.
3. Provide a brief summary of the chair's final verdict from `peer-review-report.md`.
