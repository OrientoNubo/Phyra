# Step 6: Improvement Analysis Report

**Source:** `sample-draft.md` (original) vs. `05-sample-draft-phyra-20260405.md` (revised)
**Reporter agent:** Phyra MD Reporter (NT has-draft mode)
**Date:** 2026-04-05

## Executive Summary

The original draft was an early skeleton (approximately 15-20% complete) with an intact but underdeveloped storyline. The revised draft addresses all structural gaps and fills all five TODO placeholders, bringing the manuscript to a structurally complete state (approximately 75-80% complete). The remaining gap to submission-readiness is entirely empirical: all quantitative results are placeholders awaiting actual experiments.

## Change Inventory

| Change | Type | Section(s) affected |
|--------|------|-------------------|
| Abstract restructured to five-paragraph format | Revision | Abstract |
| Introduction completed (was truncated mid-sentence) | Completion | Section 1 |
| Differentiation from RegionCLIP added | Addition | Section 1 |
| Explicit contribution list added (3 falsifiable items) | Addition | Section 1 |
| Related Work section written from scratch | Addition | Section 2 (new) |
| Projection network architecture specified | TODO filled | Section 3.2 |
| Contrastive learning objective defined with equations | TODO filled | Section 3.2 |
| Hard negative mining strategy described | TODO filled | Section 3.2 |
| Seen/unseen category split protocol specified | TODO filled | Section 3.3 |
| Training losses formalized with equation | TODO filled | Section 3.3 |
| Experiments section written with 6 sub-experiments | Addition | Section 4 (new) |
| Conclusion with limitations and future work | Addition | Section 5 (new) |
| Reference list added (11 entries) | Addition | References (new) |
| Inline Phyra comments added for all major changes | Annotation | Throughout |

## Quantitative Comparison

| Metric | Original | Revised |
|--------|----------|---------|
| Word count (approximate) | ~350 | ~3,200 |
| Sections present | 3 of 6 | 6 of 6 |
| TODO placeholders | 5 | 0 |
| Equations | 0 | 3 |
| Tables | 0 | 6 |
| Formal references | 0 | 11 |
| Contribution claims | 0 | 3 |
| Inline annotations for changes | 0 | 12 |

## Phyra Compliance Check

### phyra-soul constraints

| Constraint | Status |
|-----------|--------|
| No `------` (Chinese em-dash) as connector | Pass |
| No `---` as paragraph separator | Pass |
| No triple-nested bullet points | Pass |
| Bold only for genuine emphasis | Pass |
| Degree words ("significantly", etc.) backed by data or marked as placeholder | Pass (all claims reference placeholder values) |
| Contribution claims are falsifiable | Pass (each can be negated by experiment) |
| Active voice preferred | Pass |

### phyra-paper-writing constraints

| Constraint | Status |
|-----------|--------|
| Three-sentence test passes | Pass |
| Gap cites specific prior work with specific limitation | Pass (RegionCLIP pseudo-label noise) |
| Contributions: 3-4 items | Pass (3 items) |
| No "We propose..." in contributions | Pass |
| No "first to..." claims | Pass |
| Abstract follows five-paragraph structure | Pass |
| Abstract within 150-250 words | Pass (~180 words) |
| No "In recent years..." opening | Pass |
| No self-aggrandizing adjectives in contributions | Pass |
| Related Work includes comparative analysis, not just listing | Pass |

### phyra-experiment-design constraints

| Constraint | Status |
|-----------|--------|
| Three baseline types covered | Pass (SOTA: 4 methods; Classic: 3 methods; Ablated: 5 variants) |
| Ablation hypotheses stated before results | Pass |
| Primary metric identified with rationale | Pass (AP50_novel for COCO, AP_rare for LVIS) |
| No cherry-picking (all metrics reported) | Pass (table includes all standard metrics) |
| Statistical rigor noted | Partial (multi-seed requirement stated in experiment plan; not yet reflected in results tables since results are placeholders) |

## Remaining Work to Submission

### Must-do (blocking submission)

1. **Run all experiments and fill placeholder values.** Every `[X.X]` in the revised draft must be replaced with actual numbers. This includes Tables in Sections 4.2-4.6 and claims in Abstract and Contributions.
2. **Verify baseline numbers.** The reference baseline numbers in the comparison tables are approximate. Must confirm against published papers or re-run with identical settings.
3. **Add figures.** The paper needs at minimum: (a) Architecture diagram (Section 3.1), (b) t-SNE embedding visualization (Section 4, per experiment plan), (c) Qualitative detection results, (d) Sensitivity curve plot.
4. **Finalize author and affiliation information.**
5. **Resolve naming concern.** Decide whether to keep "RegionCLIP-Det" or rename to avoid confusion with RegionCLIP (see Risk 3 in storyline evaluation).

### Should-do (strengthening)

1. **Add cross-dataset evaluation** (Objects365 or OpenImages) to pre-empt generalization concerns.
2. **Add computational cost comparison** (FLOPs, inference speed) against baselines.
3. **Expand limitations discussion** with specific failure case analysis once experimental results are available.
4. **Proofread all reference entries** against actual publication records.

### Nice-to-have

1. Add an appendix with additional qualitative results and hyperparameter sensitivity analysis.
2. Include pseudo-code for the hard negative mining procedure.

## Risk Assessment Post-Revision

| Risk | Pre-revision severity | Post-revision severity | Notes |
|------|----------------------|----------------------|-------|
| Novelty perception | High | Medium | Differentiation from RegionCLIP now explicit; ablation plan validates each component. Final severity depends on experimental margins. |
| Experimental sufficiency | High | Medium-Low | Full experiment plan in place; only execution remains. |
| Naming confusion | Medium | Medium | Unchanged; requires author decision. |
| Storyline coherence | High | Low | Three-sentence test passes; full arc from problem to evidence now present. |
| Structural completeness | High | Low | All sections present with substantive content. |

## Workflow Trace

| Step | Agent | Input | Output | Status |
|------|-------|-------|--------|--------|
| 1 | Paper Parser | sample-draft.md | 01-parser-output.md | Complete |
| 2 | Content Analyst | Parser output + draft | 02-diagnosis.md | Complete |
| 3 | Story Architect | Diagnosis | 03-storyline-eval.md | Complete |
| 4 | Experiment Planner | Diagnosis + storyline eval | 04-experiment-plan.md | Complete |
| 5 | Paper Writer | All prior outputs | 05-sample-draft-phyra-20260405.md | Complete |
| 6 | MD Reporter | Original vs. revised | 06-improvement-report.md | Complete |
