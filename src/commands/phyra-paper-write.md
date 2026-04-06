---
description: "Plan and write academic papers, from storyline design to experiment planning to draft writing"
argument-hint: "[paper-file-path] [--at] [--from-scratch]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "SendMessage"]
---

# /phyra-paper-write

> 從故事線設計到實驗規劃到草稿撰寫的完整論文寫作流程。四種模式：NT/AT x 從零開始/有草稿。

## Step 0 — Parse arguments and load soul

Parse `$ARGUMENTS` to extract:

- **paper-file-path**: optional path to an existing draft. Store as `$PAPER_PATH`.
- **--from-scratch**: explicitly request from-scratch mode.
- **--at**: use AT (Agent Teams) parallel mode instead of NT (sequential).

**Mode detection:**

1. `--from-scratch` present OR no file path → `$DRAFT_MODE = from-scratch`
2. File path provided (without `--from-scratch`) → `$DRAFT_MODE = has-draft`
3. `--at` present → `$EXEC_MODE = AT`, otherwise → `$EXEC_MODE = NT`

**Before any other work, load the `phyra-soul` skill.** This establishes Phyra's soul
core and must be active for the entire workflow. All subagents inherit this foundation.

---

## Mode 1 — NT from-scratch

Conditions: `$EXEC_MODE = NT`, `$DRAFT_MODE = from-scratch`. Execute strictly in order.

### Step 1 — phyra-story-architect
Design the paper's storyline from scratch. Output: three-sentence version, contribution
claims draft, risk conditions. Store as `$STORYLINE`.

### Step 2 — phyra-experiment-planner
Input: `$STORYLINE`. Design experiment list with hypotheses and priority ranking.
Store as `$EXPERIMENT_PLAN`.

### Step 3 — phyra-paper-writer
Input: `$STORYLINE`, `$EXPERIMENT_PLAN`. Integrate storyline and experiment plan,
write paper framework or complete draft. Store path as `$DRAFT_OUTPUT`.

### Step 4 — phyra-md-reporter
Input: all prior outputs. Template: `paper-write-plan`. Output: planning analysis report MD.

---

## Mode 2 — NT has-draft

Conditions: `$EXEC_MODE = NT`, `$DRAFT_MODE = has-draft`. Execute strictly in order.

### Step 1 — phyra-paper-parser
Input: `$PAPER_PATH`. Parse existing materials into structured extraction. Store as `$PARSED_DRAFT`.

### Step 2 — phyra-content-analyst
Input: `$PARSED_DRAFT`, `$PAPER_PATH`. Diagnose: is storyline clear? Method logic
consistent? Experiments sufficient? Store as `$DIAGNOSIS`.

### Step 3 — phyra-story-architect
Input: `$PARSED_DRAFT`, `$DIAGNOSIS`. Evaluate existing storyline, propose optimization
directions. Store as `$STORYLINE_OPT`.

### Step 4 — phyra-experiment-planner
Input: `$PARSED_DRAFT`, `$DIAGNOSIS`, `$STORYLINE_OPT`. Plan experiments to add or
modify. Store as `$EXPERIMENT_REVISION`.

### Step 5 — phyra-paper-writer
Input: `$PAPER_PATH`, `$DIAGNOSIS`, `$STORYLINE_OPT`, `$EXPERIMENT_REVISION`. Execute
modifications, create copy (do not overwrite original), annotate major changes with
inline comments. Store path as `$REVISED_DRAFT`.

### Step 6 — phyra-md-reporter
Input: all prior outputs. Output: improvement analysis report MD.

---

## Mode 3 — AT from-scratch

Conditions: `$EXEC_MODE = AT`, `$DRAFT_MODE = from-scratch`. Use Agent Teams for
parallel steps with sync barriers where needed.

### Step 1 — [phyra-story-architect-A || phyra-story-architect-B || phyra-story-architect-C] (parallel)

Spawn three `phyra-story-architect` instances **in parallel**, each with a distinct stance:

- **A (conservative)**: incremental contributions, established methods, low-risk narrative.
- **B (aggressive)**: ambitious claims, novel framings, high-impact positioning.
- **C (adversarial)**: challenges assumptions, seeks failure modes, stress-tests premise.

Each outputs a complete storyline proposal + risk analysis. Wait for **all three**.
Store as `$PROPOSAL_A`, `$PROPOSAL_B`, `$PROPOSAL_C`.

### Step 2 — phyra-experiment-planner
Input: `$PROPOSAL_A`, `$PROPOSAL_B`, `$PROPOSAL_C`. Read all three proposals, design
experiments that support multiple directions and maximally differentiate between them.
Store as `$EXPERIMENT_PLAN`.

### Step 3 — phyra-paper-writer
Input: all proposals + `$EXPERIMENT_PLAN`. Output decision explanation (which elements
adopted/rejected from each proposal) → integrate three proposals → write paper.
Store path as `$DRAFT_OUTPUT`.

### Step 4 — phyra-md-reporter
Input: all prior outputs. Output: decision analysis and planning report MD.

---

## Mode 4 — AT has-draft

Conditions: `$EXEC_MODE = AT`, `$DRAFT_MODE = has-draft`.

### Step 1 — phyra-paper-parser (sync barrier)
Spawn and **wait for completion**. Input: `$PAPER_PATH`. Output: `$PARSED_DRAFT`.

### Step 2 — [phyra-content-analyst || phyra-story-architect || phyra-experiment-planner] (parallel)

Spawn all three **in parallel**. Each diagnoses the draft from its own perspective.
**No inter-communication** — viewpoint independence is critical.

- **phyra-content-analyst**: Input: `$PARSED_DRAFT`, `$PAPER_PATH`. Output: content
  diagnosis (storyline clarity, logic consistency, evidence gaps). Store as `$DIAG_CONTENT`.
- **phyra-story-architect**: Input: `$PARSED_DRAFT`, `$PAPER_PATH`. Output: storyline
  diagnosis (narrative strength, contribution framing, risk). Store as `$DIAG_STORY`.
- **phyra-experiment-planner**: Input: `$PARSED_DRAFT`, `$PAPER_PATH`. Output: experiment
  diagnosis (coverage gaps, hypothesis validity, priorities). Store as `$DIAG_EXPERIMENT`.

Wait for **all three** to complete.

### Step 3 — phyra-paper-writer
Input: `$PAPER_PATH`, `$PARSED_DRAFT`, `$DIAG_CONTENT`, `$DIAG_STORY`, `$DIAG_EXPERIMENT`.
Read all three diagnoses → output decision explanation reconciling perspectives →
execute modifications, create copy (do not overwrite). Store path as `$REVISED_DRAFT`.

### Step 4 — phyra-md-reporter
Input: all diagnoses + `$REVISED_DRAFT`. Output: improvement analysis report MD.

---

## Post-workflow

After the workflow completes (in any mode), report to the user:

1. Confirm which mode was used (NT/AT and from-scratch/has-draft).
2. List all files produced and their locations.
3. Brief summary of key storyline decisions and next steps from the reporter output.
