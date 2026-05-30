---
name: academic-reading
description: "Use this skill when reading, analyzing, or critically evaluating academic papers. Triggers on: paper reading, understanding contributions, evaluating methodology, performing TP-V three-pass reading, identifying red flags in research."
---

# academic-reading

**Purpose:** A framework for systematic paper reading, guiding the agent on how to deconstruct structure, identify core contributions, and critically evaluate methodology.

This skill defines two intertwined analytical threads:

- **Explicit thread** -- Reading order: determines what you read first and what you read later
- **Implicit thread** -- Dialectical thinking: determines what questions you ask at each step

Both threads are used together with the TP-V three-pass reading framework. Each pass follows the reading order while continuously running dialectical questioning.

---

## Reading Order (Explicit Thread) (Non-linear) (Used with TP-V Framework)

Do not read linearly from beginning to end. Read in the following order:

1. **Abstract**: Obtain the problem statement and claimed contributions
2. **Conclusion**: Understand what the authors believe they have proven
3. **Introduction**: Understand the narrative logic of the problem background and the gap
4. **Method**: Evaluate whether the method truly addresses the problem raised in the Introduction
5. **Experiment**: Verify whether experiments support the claims made in the Method section
6. **Related Work**: Understand how the authors position their own work

The logic of this order: know the conclusion first, then go back to examine the process. Build expectations first, then verify them.

---

## Dialectical Thinking (Implicit Thread) (Continuous Questioning Throughout Each TP-V Pass)

At every stage of reading, continuously question along these six dimensions:

1. **Importance:** The importance of the task being addressed -- is this truly a task that needs to be solved?
2. **Necessity:** The necessity of the identified problem -- is this truly a necessary and meaningful problem?
3. **Legitimacy:** The legitimacy of experiments and data -- is this a fair experimental setup? Is the data reliable?
4. **Correctness:** The correctness of claimed contributions -- do the experiments and data truly support those claims?
5. **Cost:** Does the importance of the problem match the cost of the proposed solution?
6. **Coherence:** Is the paper a unified whole? Does it tell a complete, consistent story from beginning to end?

> Reading is interrogation, not absorption. A paper is an argument, not a set of facts. Your task is to find where the argument holds and where it begins to unravel.

---

## Structural Elements That Must Be Identified

During reading, the following elements must be explicitly identified and recorded:

- The problem the paper actually solves vs. the problem the paper claims to solve (these are often inconsistent)
- Core assumptions (stated and unstated)
- Key design choices in the method and the reasoning behind them
- Controlled variables and free variables in the experimental design

If any of the above cannot be identified, explicitly mark it as "unidentified" rather than skipping it.

---

## Signals That Must Be Flagged (Red Flags)

When the following situations are encountered, they must be explicitly flagged as red flags in the output:

- The strength of conclusions exceeds the degree of experimental support
- Key terms are not defined when first used
- Baseline selection lacks justification
- Ablation studies are missing or insufficient
- Testing only on specific datasets while claiming generalizability

Each red flag should include a specific paragraph or table reference indicating where the issue occurs.

---

## Prohibited Reading Behaviors

The following behaviors are strictly prohibited:

- Do not infer method details directly from the abstract
- Do not increase trust because the authors' institution is well-known
- Do not skip numerical details and analysis in the experiment section

Violating these prohibitions leads to incorrect paper evaluation. Always base judgments on the evidence within the paper itself.

---

## Paper Reading Framework (TP-V): Three-Pass Method Variant

TP-V (Three-Pass Variant) divides paper reading into three passes, each with different depth and objectives.
This is not simple repeated reading, but progressively deepening understanding.

In each pass, both should run simultaneously:
- "Reading Order (Explicit Thread)" -- determines the reading path
- "Dialectical Thinking (Implicit Thread)" -- determines the questioning direction

The relationship between the three passes: Bird's eye view establishes the framework, grasping content fills in the details, re-implementation verifies the logic.

### First Pass: Bird's Eye View

- **Objective:** Quick assessment, establish the overall outline
- **Method:** Carefully read the title, abstract, introduction; read section headings (skip body text); skim the conclusion
- **Time expectation:** This is the fastest pass; its purpose is to decide whether the paper is worth continuing to read
- **After reading, you should be able to answer:**
  - **Category** -- Paper type
  - **Context** -- Related fields and theoretical foundations
  - **Correctness** -- Whether assumptions are reasonable
  - **Contributions** -- Main contributions
  - **Clarity** -- Writing quality of the paper
- **Dialectical focus:** Importance, Necessity -- Is this problem worth studying?

### Second Pass: Grasping the Content

- **Objective:** Understand the main arguments and evidence without delving into details
- **Method:** Carefully read the body text and take notes on key points; pay special attention to figures, tables, and data
- **Note:** Mark parts you do not understand, but do not stop to investigate deeply at this stage
- **Output:** A summary of the paper's main content and evidence
- **Dialectical focus:** Legitimacy, Correctness -- Is the experimental design fair? Does the evidence support the conclusions?

### Third Pass: Deep Re-implementation (Virtual Re-implementation)

- **Objective:** Critically evaluate every detail
- **Method:** Attempt to mentally retrace the authors' research path
- **Requirement:** Challenge every assumption, inference, and experimental design decision
- **Core question:** If I were to reproduce this paper's work, where would I encounter difficulties? Which details are ambiguous?
- **Output:** A complete assessment of the paper's strengths, weaknesses, and potential directions for improvement
- **Dialectical focus:** Cost, Coherence -- Is the cost of the method reasonable? Is the paper internally consistent?

---

## Usage Guidelines

**When to trigger this skill:**

- The user asks to read, analyze, or evaluate an academic paper
- The user asks to understand a paper's contributions or methodology
- The user asks to identify problems or red flags in a paper
- The user mentions TP-V, three-pass reading, or three-pass method

**Execution principles:**

- After completing the first pass, decide whether to proceed to the second pass based on results. Not all papers warrant three-pass reading.
- Output from each pass should be presented independently, allowing the user to choose their desired reading depth.
- Red flags should be flagged immediately upon discovery; do not wait until the end to summarize.
- Structural element identification runs across all three passes, progressively refined as understanding deepens.
- Always distinguish between "what the paper says" and "what the paper proves."
- All evaluations must be based on the paper's own content; do not introduce external bias.
