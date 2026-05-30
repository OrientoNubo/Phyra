<!-- type: paper-read-notes | generated: YYYY-MM-DD -->

# {Paper short name} — {Paper full title}

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | |
| Paper full title | |
| arXiv ID | |
| Release date | |
| Conference/Journal | |
| Paper link (abs) | |
| PDF link | |
| Code link | |
| Project page | |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| | | | |

### 1.2 Keywords

[5–8 core keywords, comma-separated.]

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| | predecessor / baseline / concurrent / influence / base model | |

## 2. Research Overview

### 2.1 Research Topic

[One paragraph in target language, ≤ 200 words. Describe what the paper studies and what it claims to achieve. **Must be complete, never truncated.**]

### 2.2 Domain Tags

[List 2–4 domain tags, e.g.: Long-context modeling / Test-time training / Video diffusion]

### 2.3 Core Architectures Used

[Bulleted list. For each architecture, a one-sentence description of its role in this paper.]

### 2.4 Core Argument

[One paragraph in target language, ≤ 400 words. Explain what the authors consider the root cause of the problem, and why the proposed solution is logically necessary. **Must be complete, never truncated.**]

## 3. Section Walkthrough

> Walk through the paper section by section. For each section, give: (a) approximate word count, (b) the story logic and what is claimed in this section, (c) what problem the authors raise here and how it connects to the next section. Each subsection ≈ 250–400 words.

### 3.1 Title and Abstract

[N words. Story logic of the abstract: what problem, what approach, what evidence, what claim. Identify the abstract's key sentences (the ones that, if removed, change the paper's claim).]

### 3.2 Introduction

[N words. Reconstruct the introduction's narrative arc: domain background → existing problems → entry point → contributions list. List the explicit pain points the authors target.]

### 3.3 Related Work / Preliminaries

[N words. Walk through key prior works the paper engages with. For each major group of related work, summarize what the paper cites and how it differentiates.]

### 3.4 Method (overview narrative)

[N words. The overall narrative of the method section, without per-module detail. The detailed structural analysis goes in §5.]

### 3.5 Experiments (overview narrative)

[N words. What the authors set out to test, what tasks they pick, what baselines they compare against. The detailed table-by-table analysis goes in §6.]

### 3.6 Conclusion / Limitations / Future Work

[N words. The conclusion's takeaways, any limitations the authors openly state, and the future work they hint at.]

## 4. Critical Profile

### 4.1 Highlights

[Ranked by importance. 7–10 specific one-sentence highlights — what the paper claims as its strengths, with concrete numbers/results when possible.]

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

[Limitations the authors explicitly admit in the paper. Cite the page/section.]

#### 4.2.2 Phyra-inferred

[Structural issues that the paper does not openly discuss but Phyra detects on a critical reading. One sentence each, ranked by severity. These are the harder-to-find problems and must be specific.]

### 4.3 Phyra's Judgment (summary)

[2–4 sentences. Summarize Phyra's overall stance: what is genuinely new, what is engineering-only, what core question remains unresolved. Detailed judgment goes in §7.]

## 5. Methodology Deep Dive

### 5.1 Method Overview

[2–3 paragraphs in technical voice. Describe the overall technical approach with enough detail that a reader who skipped §3.4 can still follow.]

### 5.2 Pipeline Diagram with Tensor Shapes

> Render the full forward path as a Markdown text diagram. Annotate every arrow with the tensor shape. Use the convention `[B, ..., d]` and explicitly indicate any shape change.

```
Input: tokens [B, L, d]
   ├→ split_chunks → [B, n_chunk, b, d]
   │     ├→ window_attention([B*n_chunk, b, d]) → [B, L, d]
   │     └→ large_chunk_TTT
   │            ├ K, V [B*nh, b, hd]
   │            ├ fast_weight W ∈ {[hd, hd*r], [hd*r, hd]}
   │            └ apply: o = fW(Q) → [B, L, d]
   ├→ feed_forward → [B, L, d]
   └→ task_head → output
```

### 5.3 Per-Module Breakdown

> Repeat the block below for every major module (typically 3–7).

#### 5.3.N {Module Name}

**Function:** [One sentence describing what this module does.]

**Input:**
- Name: [variable name]
- Shape: [tensor shape]
- Source: [from which module or data]

**Output:**
- Name: [variable name]
- Shape: [tensor shape]
- Consumer: [next module that consumes this]

**Processing:**

[Step-by-step transform, including dimension changes and key operations. Cite the equation number if the paper has one.]

**Key Formulas:**

$$
[LaTeX formula]
$$

**Implementation Details:**

[Activation, normalization, initialization, learning rate, etc. — only what the paper actually discloses.]

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---------|------|-------|------------------------|
| | | | |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|--------|-------------|---------|
| | | |

### 6.3 Training and Inference Settings

[Hardware, batch size, optimizer, learning rate schedule, training steps, inference settings. Cite the paper's appendix when relevant.]

### 6.4 Main Results

| Method | [Metric 1] | [Metric 2] | Notes |
|--------|-----------|-----------|-------|
| **This paper** | | | |
| Baseline A | | | |

### 6.5 Ablation Studies

[For each ablation: what was removed, what changed in the metric, and whether the ablation answers the right question. Flag ablations that look like sanity checks rather than diagnostic experiments.]

### 6.6 Phyra Experiment Assessment

[Check against `phyra:experiment-design`'s sufficiency list. For each item, mark covered / partial / missing, with one sentence of evidence.]

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

[For each contribution the authors claim: state whether the experiments actually support it, partially support it, or whether it is overclaimed. Cite the supporting figure / table.]

### 7.2 Fundamental Limitations of the Method

[Structural problems the method cannot overcome under its current design. Not "future work" — these are limits of the formulation itself. One short paragraph each.]

### 7.3 Citations Worth Tracking

[3–5 references the reader should chase. For each: why it is worth reading next.]

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] [Question one]
- [ ] [Question two]

### 8.2 Improvement Directions

[Ranked by feasibility. For each: the proposed change and the logical basis for why it should help.]
