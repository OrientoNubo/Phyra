# Step 3: Story Architect -- Storyline Evaluation

**Source:** `sample-draft.md` + `02-diagnosis.md`
**Architect agent:** Phyra Story Architect (NT has-draft mode)
**Date:** 2026-04-05

## Current Storyline Assessment

### Narrative Arc (as written)

The draft attempts the following arc:

1. Zero-shot object detection is important because annotation is expensive.
2. CLIP is good at zero-shot classification but not detection.
3. Prior work (OVR-CNN, ViLD, GLIP) tried to bridge this gap but two problems remain: (a) region features are not aligned with CLIP's embedding space, and (b) granularity mismatch causes background false positives.
4. RegionCLIP-Det addresses both through a region-text alignment module.

### Strengths of Current Storyline

- **Problem is real and well-scoped.** Zero-shot / open-vocabulary detection is an active and important research area. The framing connects to a genuine need.
- **Two-problem structure is clear.** Identifying two specific failure modes (embedding misalignment and granularity mismatch) gives the narrative concrete hooks rather than a vague "existing methods are insufficient" claim.
- **Method structure maps to problems.** The three-component architecture (RPN, alignment module, detection head) has a logical correspondence to the detection pipeline. The alignment module directly targets the stated problems.

### Weaknesses of Current Storyline

1. **The gap is not sufficiently differentiated from RegionCLIP (Zhong et al., CVPR 2022).** RegionCLIP already performs region-level alignment of CLIP features. The current draft does not explain what RegionCLIP fails to do that RegionCLIP-Det addresses. This is the most critical storyline weakness -- without clear differentiation from the closest prior work, the novelty claim collapses.

2. **Two problems but potentially only one solution.** The alignment module addresses problem (a) (embedding misalignment), but problem (b) (background false positives from granularity mismatch) requires a distinct mechanism (the negative mining strategy). The current narrative does not sufficiently distinguish how each problem maps to a specific technical contribution.

3. **No "why now" argument.** The draft does not explain what makes this problem newly tractable. What insight or technical capability enables RegionCLIP-Det that was not available when ViLD or GLIP were published?

4. **The Introduction never reaches contributions.** It cuts off before listing what the paper actually delivers. A reader has no explicit contract of what to expect from the rest of the paper.

5. **Abstract oversells.** "Competitive performance with significantly fewer training categories" is a strong claim with zero quantitative support. This sets up a credibility gap.

## Recommended Improvements

### Improvement 1: Sharpen the differentiation from RegionCLIP

**Current:** "We propose RegionCLIP-Det to address both issues..."
**Recommended:** Explicitly state what RegionCLIP's alignment approach misses. For example, if RegionCLIP uses pseudo-labels for pre-training but does not perform direct contrastive alignment at the proposal level during detection training, say so with precision. The gap must be against the closest prior work, not just against CLIP in general.

**Implementation:** Add 2-3 sentences in the Introduction after the discussion of prior work that specifically analyze RegionCLIP's limitation. Then frame RegionCLIP-Det's alignment module as addressing that specific limitation.

### Improvement 2: Map each problem to a distinct contribution

**Current:** Two problems are stated, one solution (alignment module) is described.
**Recommended:** Restructure to make the one-to-one mapping explicit:
- Problem (a): Embedding misalignment --> Contribution: Projection network with contrastive learning objective
- Problem (b): Background false positives --> Contribution: Hard negative mining strategy for background suppression
- Combined: Detection head that integrates both --> Contribution: Score fusion mechanism

This gives three falsifiable contributions, which aligns with Phyra's 3-4 contribution requirement.

### Improvement 3: Add a "why now" paragraph

**Recommended:** After stating the problems and before presenting the method, add a brief paragraph explaining the key insight. For example: "We observe that proposal-level features, when projected through a learned mapping, can achieve alignment quality comparable to CLIP's native image features, while retaining the spatial precision needed for localization. This observation motivates a simple yet effective architecture..."

This gives the reader a conceptual anchor before the technical details.

### Improvement 4: Complete the Introduction with explicit contributions

**Recommended:** End the Introduction with a numbered list of 3-4 contributions following Phyra's contribution format (no "We propose..." phrasing, each must be falsifiable):

1. A region-text alignment module that projects proposal features into CLIP's embedding space through a learned projection, achieving alignment scores within X% of native CLIP features on Y benchmark.
2. A hard negative mining strategy that reduces background false positive rates by Z% compared to naive region-text matching.
3. State-of-the-art results on COCO novel categories (AP = A) and LVIS rare categories (AP = B), using only N seen training categories.

### Improvement 5: Revise the Abstract to follow the five-paragraph structure

**Current:** The abstract is a single block mixing problem, method, and vague results.
**Recommended:** Restructure into the five required parts:
1. Problem statement (1-2 sentences)
2. Specific limitations of prior work (1-2 sentences)
3. Core method idea (1-2 sentences)
4. Key quantitative results (1-2 sentences, with actual numbers)
5. Broader significance (1 sentence)

Total: 150-250 words.

## Risk Analysis

### Risk 1: Novelty perception (HIGH)

**Risk:** Reviewers familiar with RegionCLIP, GLIP, and OWL-ViT may view region-text alignment as incremental. The open-vocabulary detection space is crowded (2022-2025 saw rapid progress).
**Mitigation:** The differentiation from RegionCLIP must be razor-sharp. Ablation experiments must demonstrate that the specific alignment approach (not just any alignment) is what drives performance. A direct comparison table showing what each method aligns, how, and at what granularity would strengthen the positioning.

### Risk 2: Experimental sufficiency (HIGH)

**Risk:** Without experiments, the paper cannot be submitted. The experiments must cover not only accuracy but also the specific claims about embedding alignment quality and background suppression.
**Mitigation:** Plan experiments before finishing the method writing, so that the method description naturally sets up the experimental questions. Include embedding space visualizations and false positive rate analysis as first-class results, not afterthoughts.

### Risk 3: Naming confusion (MEDIUM)

**Risk:** "RegionCLIP-Det" may be perceived as a direct extension of RegionCLIP rather than an independent contribution, potentially triggering reviewer bias.
**Mitigation:** Either (a) clearly acknowledge RegionCLIP and explain the fundamental differences in the Introduction, or (b) consider renaming to avoid confusion entirely. Option (b) is safer if the method's approach is substantially different.

### Risk 4: Scope creep in method (MEDIUM)

**Risk:** The five TODO items in the method span projection architecture, loss functions, and training strategy. If these are all novel, the paper risks being too dense. If they are standard choices, the contribution may be seen as thin.
**Mitigation:** Be honest about which components are novel and which are standard. Emphasize the novel components and briefly describe the standard ones with citations.

### Risk 5: Dataset choice (LOW)

**Risk:** COCO and LVIS are standard but may not be sufficient. Reviewers may request additional datasets (e.g., Objects365, OpenImages) or cross-dataset generalization.
**Mitigation:** Include at least one additional dataset or cross-dataset evaluation in the experiment plan.
