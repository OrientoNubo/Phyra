# Step 1: Paper Parser Output

**Source:** `sample-draft.md`
**Parser agent:** Phyra Paper Parser (NT has-draft mode)
**Date:** 2026-04-05

## Extracted Document Metadata

| Field | Value |
|-------|-------|
| Title | Towards Robust Zero-Shot Object Detection via Vision-Language Alignment |
| Authors | [TBD] |
| Affiliation | [TBD] |
| Topic area | Zero-shot object detection, vision-language models |
| Target venue | Not specified (style suggests CVPR/ECCV/ICCV tier) |

## Extracted Section Structure

| # | Section | Present | Status |
|---|---------|---------|--------|
| 0 | Abstract | Yes | Exists, needs revision (missing quantitative results, broad significance claim) |
| 1 | Introduction | Yes | Incomplete, cuts off mid-sentence |
| 2 | Related Work | **No** | Missing entirely; section numbering jumps from 1 to 3 |
| 3 | Method | Partial | 3.1 Overview exists; 3.2 has three [TODO] blocks; 3.3 has two [TODO] blocks |
| 4 | Experiments | **No** | Missing entirely |
| 5 | Conclusion | **No** | Missing entirely |

## Identified [TODO] Items

1. **[TODO: describe the projection network architecture]** (Section 3.2, line 35)
   - Context: Needs to specify the neural network that maps RoIAlign features into CLIP embedding space.

2. **[TODO: describe the contrastive learning objective]** (Section 3.2, line 36)
   - Context: Needs the loss function for aligning region features with text embeddings.

3. **[TODO: describe the negative mining strategy for background suppression]** (Section 3.2, line 37)
   - Context: Needs the mechanism for reducing false positives on background regions.

4. **[TODO: describe the seen/unseen category split]** (Section 3.3, line 40)
   - Context: Needs the data partitioning protocol for zero-shot evaluation.

5. **[TODO: describe the training losses]** (Section 3.3, line 41)
   - Context: Needs the complete multi-task loss formulation.

## Structural Anomalies

1. **Missing Section 2:** The numbering jumps from Section 1 (Introduction) directly to Section 3 (Method). A "Related Work" section (Section 2) is absent.
2. **Introduction truncation:** Section 1 ends with "We propose RegionCLIP-Det to address both issues through..." -- the sentence is incomplete.
3. **No figures or tables:** The draft contains zero figures, tables, or visual elements.
4. **No references:** No bibliography or inline citations with proper reference keys (e.g., only informal "Author et al." style mentions in the Introduction).
5. **Abstract lacks numbers:** The abstract mentions "preliminary results" and "competitive performance" without any quantitative evidence.

## Content Inventory

| Content type | Count |
|-------------|-------|
| Complete paragraphs | 4 |
| Incomplete paragraphs | 1 (Introduction final paragraph) |
| TODO placeholders | 5 |
| Equations | 0 |
| Figures | 0 |
| Tables | 0 |
| Citations (formal) | 0 |
| Citations (informal name-drops) | 4 (CLIP, OVR-CNN, ViLD, GLIP) |

## Key Entities Extracted

- **Proposed method name:** RegionCLIP-Det
- **Core components:** (1) Class-agnostic RPN, (2) Region-text alignment module, (3) Combined detection head
- **Benchmarks mentioned:** COCO, LVIS
- **Prior work referenced:** CLIP, OVR-CNN, ViLD, GLIP
- **Two stated problems:** (a) Region features not aligned with CLIP visual embedding space, (b) Granularity mismatch causing background false positives
