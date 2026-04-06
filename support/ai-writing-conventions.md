# AI Writing Conventions -- Domain Writing Style Reference

> This document serves as a domain-specific writing conventions reference for Phyra's academic writing plugin, referenced by the `paper-writing` skill.
> It covers four major domains -- CV, NLP, ML, and Multimodal -- as well as cross-domain general conventions.

---

## 1. Computer Vision (CV) -- CVPR / ICCV / ECCV Style

### 1.1 Section Ordering

Typical structure (most common arrangement):

```
1. Introduction
2. Related Work          <- Some authors place this after Method
3. Method / Approach
4. Experiments
5. Conclusion
```

- Recent CVPR trend: placing Related Work after Method so readers understand the proposed method before seeing how it is positioned.
- ECCV leans toward the traditional order (Related Work immediately after Introduction).

### 1.2 Citation Density

- Generally expect **30-60 references**.
- Too few (<20) raises concerns about insufficient survey; too many (>80) may appear padded.
- Each paragraph in Related Work should focus on one sub-topic, citing 3-8 works per paragraph.

### 1.3 Figure Conventions

| Position | Purpose | Notes |
|----------|---------|-------|
| Figure 1 | **Teaser figure** | The single most important figure in the paper; must convey the core idea at a glance |
| Figure 2-3 | Architecture / pipeline diagram | Main method figure, typically containing module names and data flow arrows |
| Later figures | Qualitative comparisons | Visual comparisons against baselines; method names must be labeled |

- Image resolution should be at least 300 dpi; vector graphics (PDF/SVG) preferred.
- In qualitative comparisons, use red boxes or arrows to highlight regions of difference.

### 1.4 Table Conventions

- **Bold** marks the best result; **underline** marks the second-best.
- Table captions go above the table.
- Column alignment: numbers right-aligned or centered; method names left-aligned.
- If result differences fall within the margin of statistical error, standard deviations should be annotated.

### 1.5 Abstract Length

- Target **150-250 words**. CVPR/ICCV templates have no hard limit, but exceeding 250 words feels verbose.
- Structure: problem -> insight -> method overview -> key result numbers.

### 1.6 Common Phrasing to Avoid

- "In recent years, X has attracted increasing attention..." (cliche)
- "To the best of our knowledge, this is the first..." (only if genuinely verifiable)
- "We propose a novel..." as the opening sentence of the abstract (reviewers find this tiresome)
- Instead, state the problem and solution directly without unnecessary modifiers.

---

## 2. NLP -- ACL / EMNLP / NAACL Style

### 2.1 Section Ordering

```
1. Introduction
2. Related Work          <- The NLP community strongly prefers this after Intro
3. Background / Preliminaries (as needed)
4. Method
5. Experimental Setup
6. Results and Analysis
7. Limitations           <- Required since ACL 2023
8. Ethics Statement      <- Required at ACL venues
9. Conclusion
```

### 2.2 Ethics Statement

- ACL, EMNLP, and NAACL all require an Ethics Statement.
- Content covers: legality of data sources, annotator compensation, potential societal impact, bias risks.
- Typically 0.5-1 page; does not count toward the main text page limit.

### 2.3 Reproducibility Checklist

- ACL-family conferences require a reproducibility checklist (submitted alongside the paper).
- The paper should explicitly list: hyperparameters, training time, hardware specs, number of random seeds.
- A complete experimental setup table in the Appendix is recommended.

### 2.4 Citation Density

- NLP papers tend to have higher citation counts: **40-80 references**.
- Reason: NLP has many sub-fields (parsing, generation, QA, summarization...), requiring broad positioning.
- Pre-trained model papers (BERT, GPT series, etc.) are almost always cited.

### 2.5 Limitations Section

- **Mandatory since ACL 2023**; missing this section may result in desk rejection.
- Honestly discuss: scope of applicability, dataset limitations, shortcomings of evaluation metrics.
- Do not write this as self-justification; reviewers expect genuine reflection.

---

## 3. Machine Learning -- NeurIPS / ICML / ICLR Style

### 3.1 Theoretical vs. Empirical Paper Conventions

**Theory papers:**
- The main theorem should be fully stated in the main text; proofs may go in the Appendix.
- A proof sketch should be included in the main text so reviewers can quickly grasp the proof strategy.
- Assumptions should be numbered and collected in one place for easy reference.

**Empirical papers:**
- Must validate on multiple datasets / benchmarks.
- Ablation study is a basic requirement (see section 5.3).
- Computational cost analysis (FLOPs, GPU hours) is increasingly valued.

### 3.2 Appendix Conventions

- NeurIPS allows unlimited Appendix length (but reviewers are not obligated to read it).
- Common Appendix content:
  - Full proofs
  - Additional experimental results
  - Hyperparameter search details
  - Detailed dataset information
- The main text should be self-contained; the Appendix serves only as supplementary material.

### 3.3 Anonymous Submission Formatting

- **Double-blind review:** Author names and affiliations must not appear.
- Self-citations use the third person: "Previous work [XX] showed..." not "Our previous work..."
- GitHub repo links: use anonymous repos (e.g., Anonymous GitHub) or note "will be released upon acceptance."
- Acknowledgements should be removed during the review period.

### 3.4 Broader Impact Statement

- NeurIPS has required a Broader Impact or Ethics statement since 2020.
- ICML / ICLR do not currently mandate this, but including one is viewed favorably.
- Should discuss: positive societal impact, potential negative impact, mitigation measures.

---

## 4. Multimodal -- Cross-Venue Conventions

### 4.1 Demo / Visualization Expectations

- Qualitative results are extremely important in multimodal papers; reviewers expect rich visualizations.
- Common presentation formats:
  - Attention map visualizations for image-text pairs
  - Grid comparisons of generated results (rows = different methods, columns = different samples)
  - Video-related work should include a supplementary video or provide a link

### 4.2 Multi-Dataset Evaluation Norms

- Evaluate on at least **3 or more** different datasets.
- Cover different data distributions and task complexities.
- Cross-modal retrieval papers commonly use: Flickr30k, COCO, CC3M, etc.
- If experimenting on only a single dataset, provide thorough justification (e.g., only one recognized benchmark exists for the task).

### 4.3 Supplementary Material

- Strongly recommended to provide supplementary material (PDF + video).
- The PDF supplement should contain additional qualitative results and failure cases.
- Failure case analysis is especially welcomed in multimodal papers.

---

## 5. Cross-Domain General Conventions

### 5.1 How to Write Related Work

**Correct positioning (not listing):**
- Each paragraph focuses on a sub-topic: first outline the development trajectory of that direction, then explain how the current paper differs.
- Structure: prior work did A -> but problem B exists -> this paper addresses it from angle C.
- Avoid enumerating papers one by one ("X did ..., Y did ..., Z did ...").

**Paragraph strategy:**
- Organize by technical topic, not chronological order.
- End each paragraph with a sentence clarifying the relationship or difference between the current paper and that research direction.

### 5.2 Contribution Statements

- Bulleted list is the most common format, typically 3-4 points.
- Do not use self-congratulatory adjectives: comprehensive, extensive, thorough, significant.
- Each point should be specific and verifiable, e.g., "achieves Y% improvement on benchmark X" rather than "greatly improves performance."

### 5.3 Ablation Study Presentation

- Purpose: verify the contribution of each design choice, not to show that many experiments were run.
- Standard format: fix all other components, remove/replace one component at a time.
- Tables should clearly mark the baseline (full model) and the differences in each variant.
- Present either **incrementally** (adding components step by step) or **by ablation** (removing components step by step); pick one approach.

### 5.4 Figure / Table Numbering and References

- Every figure and table must be referenced in the main text ("as shown in Figure 3").
- The first reference should appear before or on the same page as the figure/table.
- In LaTeX, use `\ref{}` rather than manual numbering to avoid numbering misalignment.
- Figure captions should be self-contained -- understandable without referring back to the main text.
- Table captions go **above** the table; figure captions go **below** the figure.

### 5.5 Notation Consistency

- Define all symbols at the beginning of the Method section or in Preliminaries.
- Vectors in bold lowercase (**x**), matrices in bold uppercase (**X**), scalars in italics (*x*).
- The same symbol must not change meaning throughout the paper.
- Subscript conventions should be consistent (e.g., $x_i$ for the $i$-th sample, $x^{(t)}$ for the $t$-th iteration).
- Mathematical symbols must be defined upon first appearance; do not assume the reader already knows them.

### 5.6 Writing Tone and Word Choice

- Prefer active voice: "We propose..." rather than "It is proposed that..."
- Avoid colloquial expressions: "a lot of" -> "numerous" / "a large number of"
- Avoid excessive hedging: "We believe that maybe..." -> "We hypothesize that..."
- Number formatting: spell out at the start of a sentence ("Three experiments..."); Arabic numerals are acceptable mid-sentence ("across 3 datasets").

---

> **Maintenance note:** This document is maintained by the Phyra team and updated in accordance with the latest conference policies.
> Last updated: 2026-04-04
