# Step 4: Experiment Planner Output

**Source:** `02-diagnosis.md` + `03-storyline-eval.md`
**Planner agent:** Phyra Experiment Planner (NT has-draft mode)
**Date:** 2026-04-05

## Experiment Design Overview

The experiment plan is driven by three goals:
1. Validate that RegionCLIP-Det achieves competitive detection performance on unseen categories.
2. Demonstrate that each design component (projection network, contrastive loss, negative mining) is individually necessary.
3. Confirm the two specific claims: (a) region-text alignment quality and (b) reduced background false positives.

## Baseline Selection (Three Required Types)

### Type 1: Contemporaneous SOTA

| Method | Venue | Rationale |
|--------|-------|-----------|
| GLIP-T / GLIP-L | CVPR 2022 | Unified detection-grounding model; strong across OVD benchmarks. Direct competitor in region-language alignment. |
| Grounding DINO | ECCV 2024 | Extends DINO with grounded pre-training; current SOTA on many OVD benchmarks. |
| OWL-ViT v2 | NeurIPS 2023 | Scales open-world detection with ViT backbone; represents the scaled-model approach. |
| RegionCLIP | CVPR 2022 | Closest prior work. Must be included to demonstrate clear improvement. |

**Selection rationale:** These four methods represent the three main technical approaches to open-vocabulary detection: (1) grounding-based (GLIP, Grounding DINO), (2) distillation-based (RegionCLIP), and (3) scaled vision-transformer-based (OWL-ViT v2). Including all three branches ensures the comparison is not biased toward a single paradigm.

### Type 2: Classic Baselines

| Method | Venue | Rationale |
|--------|-------|-----------|
| ViLD | ICLR 2022 | Established CLIP-distillation baseline for OVD; widely cited reference point. |
| OVR-CNN | CVPR 2021 | One of the earliest open-vocabulary detectors using CLIP embeddings as classifier weights. Demonstrates progress over the initial approach. |
| Zero-Shot YOLO (Bansal et al.) | ECCV 2018 | Pre-CLIP era ZSD method; shows how far the field has progressed with VLMs. |

**Selection rationale:** ViLD and OVR-CNN are the most cited early OVD methods and provide a historical performance reference. Zero-Shot YOLO represents the pre-VLM era and establishes a lower bound.

### Type 3: Ablated Versions (Ablation Baselines)

| Variant | What is removed | Hypothesis |
|---------|----------------|------------|
| RegionCLIP-Det w/o projection | Remove learned projection; use raw RoIAlign features directly with CLIP text embeddings | AP will drop substantially because raw region features are not in CLIP's embedding space. Validates the necessity of the projection network. |
| RegionCLIP-Det w/o contrastive loss | Replace contrastive alignment loss with a simple cosine similarity objective (no hard negatives, no temperature scaling) | AP will drop moderately because the alignment quality degrades without structured contrastive learning. Validates the loss design. |
| RegionCLIP-Det w/o negative mining | Remove hard negative mining; use random negatives only | Background false positive rate will increase noticeably, while AP on foreground categories may drop only slightly. Validates the background suppression claim. |
| RegionCLIP-Det w/ linear projection | Replace MLP projection with single linear layer | AP will drop slightly, showing that non-linear projection captures alignment patterns that a linear map cannot. Validates architecture depth. |
| RegionCLIP-Det w/o score fusion | Use only classification score from alignment (no localization score) | AP will drop because localization quality degrades; demonstrates that both signal sources are needed in the detection head. |

## Experiment Table Plan

### Experiment 1: Main Results on COCO OVD

**Setup:** COCO dataset, 48 base categories for training, 17 novel categories for zero-shot evaluation (standard OVD split from Bansal et al.).
**Metrics:** AP50_novel, AP_novel, AP_base, AP_all (following ViLD/RegionCLIP convention).
**Primary metric:** AP50_novel (standard for ZSD/OVD on COCO).
**Reported for:** All SOTA baselines, all classic baselines, RegionCLIP-Det.
**Implementation note:** For fair comparison, re-run RegionCLIP and ViLD using our codebase with identical backbone (ResNet-50 and Swin-B). For methods where code is unavailable, report published numbers and note the backbone.

### Experiment 2: Main Results on LVIS

**Setup:** LVIS v1.0, train on frequent + common categories, evaluate on rare categories.
**Metrics:** AP_rare, AP_common, AP_frequent, AP_all, plus AP at IoU=0.5 and IoU=0.75.
**Primary metric:** AP_rare (directly measures zero-shot generalization to rare categories).
**Rationale:** LVIS has a natural long-tail distribution; rare categories serve as a realistic zero-shot testbed.

### Experiment 3: Ablation Study

**Setup:** COCO OVD split, ResNet-50 backbone (smaller scale for efficiency).
**Metrics:** AP50_novel, AP_novel, plus background FP rate (for negative mining ablation).
**Format:** Table with one row per ablation variant.
**Analysis required:** For each variant, report the absolute drop from full RegionCLIP-Det and discuss whether the result matches the stated hypothesis.

### Experiment 4: Background False Positive Analysis

**Setup:** COCO OVD split. Compute FP rate on proposals that have IoU < 0.1 with any ground truth box (background proposals).
**Metrics:** Background FP rate at confidence threshold 0.3 and 0.5; FP rate vs. recall curve.
**Compared against:** ViLD, RegionCLIP, GLIP (methods for which we can compute per-proposal scores).
**Rationale:** This directly validates the second motivating problem. If RegionCLIP-Det does not show lower background FP rates, the second problem statement is not supported by evidence.

### Experiment 5: Embedding Space Visualization

**Setup:** Extract region features for 500 random proposals from COCO val, project into alignment space, and visualize via t-SNE alongside CLIP text embeddings for the 17 novel categories.
**Expected result:** Region features should cluster near their matching text embeddings after alignment, with clear separation from non-matching categories.
**Comparison:** Show the same visualization for raw RoIAlign features (before projection) to demonstrate the effect of the alignment module.

### Experiment 6: Sensitivity to Number of Seen Categories

**Setup:** Vary the number of base (seen) training categories from 10 to 48 on COCO, evaluate AP50_novel at each point.
**Format:** Line plot with number of seen categories on x-axis, AP50_novel on y-axis.
**Rationale:** Tests the claim in the abstract ("competitive performance with significantly fewer training categories"). Must show a graceful degradation curve and identify the minimum number of seen categories needed for competitive performance.

### Experiment 7: Cross-Dataset Generalization (Optional but Recommended)

**Setup:** Train on COCO base categories, evaluate on Objects365 validation set (categories not in COCO).
**Metrics:** AP50 on Objects365 novel categories.
**Rationale:** Addresses potential reviewer concern about generalization beyond the training dataset distribution.

## Evaluation Metrics Summary

| Metric | Role | Used in |
|--------|------|---------|
| AP50_novel | Primary metric for ZSD on COCO | Exp 1, 3, 6 |
| AP_novel | Secondary, stricter IoU threshold | Exp 1, 2, 3 |
| AP_rare (LVIS) | Primary metric for LVIS evaluation | Exp 2 |
| Background FP rate | Validates second problem statement | Exp 3, 4 |
| Qualitative t-SNE | Validates alignment quality | Exp 5 |

## Statistical Rigor Requirements

- All main results (Exp 1, 2) must be averaged over 3 runs with different random seeds; report mean and standard deviation.
- Ablation (Exp 3) may use a single seed if computational budget is constrained, but this must be noted.
- For the main comparison, if the difference from the closest competitor is less than 1.0 AP, a paired t-test or bootstrap confidence interval is required.

## Compute Budget Estimate

| Experiment | Estimated GPU-hours (A100) |
|-----------|---------------------------|
| Main COCO (3 seeds) | 72 |
| Main LVIS (3 seeds) | 96 |
| Ablation (5 variants, 1 seed) | 40 |
| FP analysis | 4 |
| Embedding viz | 1 |
| Sensitivity (5 points, 1 seed) | 40 |
| Cross-dataset | 24 |
| **Total** | **~277** |
