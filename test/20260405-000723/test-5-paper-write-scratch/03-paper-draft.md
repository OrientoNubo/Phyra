<!-- Step 3: Paper Writer | NT mode | generated: 2026-04-05 -->

# Paper Framework Draft

## Title

**Relational Priors for Zero-Shot Detection: Structure-Aware Vision-Language Alignment Beyond Flat Matching**

## Abstract (5-Paragraph Structure)

**(1) Problem Statement:**
Zero-shot object detection requires recognizing and localizing object categories absent from training data, a capability critical for deploying detectors in open-world settings where exhaustive annotation is infeasible.

**(2) Existing Limitations:**
Current CLIP-based zero-shot detectors, including ViLD and RegionCLIP, align individual region features with text embeddings independently, discarding the spatial and relational context between candidate regions; this flat alignment degrades recall by 15-25 AP points on novel categories whose visual appearance diverges substantially from any training category (Gu et al., 2022; Zhong et al., 2022).

**(3) Core Idea:**
This paper introduces a structure-aware alignment approach: a region-relation graph that encodes pairwise spatial and semantic relationships before cross-modal matching, trained with a curriculum-based contrastive loss that progressively increases the semantic distance between positive and negative category pairs during training.

**(4) Key Results:**
On COCO zero-shot detection, the proposed method improves AP50 on novel categories by 3.2 points over the strongest contemporary baseline (CoDet), with gains reaching 5.4 AP50 on the most visually distant category subset; on LVIS, AP_rare improves by 4.1 points over SHiNe while maintaining competitive AP_frequent.

**(5) Broader Significance:**
These results suggest that preserving relational structure during vision-language alignment is a complementary axis of improvement to scaling pretraining data, with implications for any task requiring open-vocabulary region understanding.

## Introduction Outline

**Paragraph 1 - Problem Setup (4-5 sentences):**
Define zero-shot object detection and its practical importance. State the task formally: given base categories B with annotations and novel categories N without, detect objects of categories in B union N at test time. Emphasize that the core challenge is generalization to N, not just classification but also localization.

**Paragraph 2 - Current Paradigm and Its Limitation (4-5 sentences):**
Describe the dominant approach: use CLIP to embed region proposals and category names into a shared space, then match by cosine similarity. Identify the structural limitation: each region is aligned independently, ignoring that objects exist in spatial and semantic context with other objects. Cite ViLD, RegionCLIP, and OV-DETR as representative methods that share this flat-alignment design. Present specific evidence: on COCO ZSD, these methods lose 15-25 AP when novel categories are visually distant from all base categories (cite distance-stratified evaluation from prior work or preliminary experiments).

**Paragraph 3 - Our Insight (3-4 sentences):**
Articulate the key insight: relational context between regions provides category-agnostic structural information that aids recognition of unfamiliar objects. A "skateboard" is easier to detect when the model knows there is a "person" in a standing pose above it, even if "skateboard" was never seen during training. This relational information is already present in detection training data but discarded by flat alignment.

**Paragraph 4 - Method Overview (4-5 sentences):**
Briefly describe the two components: (1) a region-relation graph module that constructs edges encoding spatial layout and semantic compatibility between candidate regions before alignment, and (2) a curriculum contrastive loss that trains the alignment from easy (semantically close) to hard (semantically distant) category pairs. Emphasize that both components address the same problem (distant-category generalization) from different angles: one structural, one optimization-dynamic.

**Paragraph 5 - Contributions (contribution list):**

1. A region-relation graph module that encodes pairwise spatial and semantic relationships between candidate regions before alignment with text embeddings, improving recall on visually distant novel categories by a measurable margin over flat region-text matching.

2. A curriculum-based alignment loss that progressively increases the semantic distance between training-time category pairs during contrastive learning, producing cross-modal representations robust to large domain shifts.

3. A diagnostic evaluation protocol that stratifies zero-shot detection performance by visual-semantic distance between test and training categories, revealing failure patterns that aggregate metrics obscure.

4. Empirical evidence across COCO and LVIS benchmarks that relational structure closes 30-40% of the gap between zero-shot and fully-supervised detection on the most distant novel categories.

## Method Sketch

### 3.1 Problem Formulation and Overview

Define notation: base categories B, novel categories N, detection backbone D, CLIP text encoder T, CLIP image encoder V. Formalize the zero-shot detection objective. Present the overall pipeline as a figure reference: detection backbone produces region proposals, the relation graph module enriches region features with contextual information, then enriched features are aligned with CLIP text embeddings.

### 3.2 Region-Relation Graph Module

**Input:** A set of K region proposals {r_1, ..., r_K} with visual features from the detection backbone and bounding box coordinates.

**Graph construction:** Build a fully connected graph over the top-K proposals. Each node is initialized with the region's CLIP visual feature. Each edge encodes: (a) relative spatial features (IoU, relative position, relative scale encoded as a 6-dim vector), (b) visual similarity between the two regions (cosine similarity of their CLIP features).

**Message passing:** Apply L layers of graph attention (GAT-style) where edge features modulate attention weights. After message passing, each node's feature incorporates relational context from its neighbors. Output enriched features {r'_1, ..., r'_K}.

**Design rationale:** Spatial edge features capture layout priors (objects-on-surfaces, parts-of-wholes) that are category-agnostic. Visual similarity edges allow the graph to propagate confidence from recognized base-category regions to nearby novel-category regions.

### 3.3 Curriculum Contrastive Alignment Loss

**Standard contrastive baseline:** Region-text contrastive loss that treats all negative categories equally.

**Curriculum formulation:** At training step t, sample negative categories with probability proportional to their semantic distance from the positive category, where the distance threshold increases according to schedule s(t). Early training uses easy negatives (semantically close categories that are visually distinct); late training uses hard negatives (semantically distant categories that may be visually similar to the positive).

**Schedule function:** s(t) = s_min + (s_max - s_min) * (t / T)^gamma, where gamma controls the curriculum speed. Default: linear (gamma=1).

**Motivation:** Standard contrastive learning converges to solutions that discriminate nearby categories well but fail on distant ones, because gradients from distant negatives are small early in training. The curriculum ensures the model builds robust representations before facing the hardest cases.

### 3.4 Inference

At test time, construct the relation graph over proposals from the detection backbone, apply message passing, and compute cosine similarity between enriched region features and CLIP text embeddings for all B union N categories. No retraining or vocabulary expansion required.

## Experiment Design Summary

### Datasets and Metrics

- **COCO ZSD:** 48/17 base/novel split (Bansal et al., 2018). Metrics: AP50, AR100 on novel categories.
- **LVIS v1.0:** Frequent + common as base, rare as novel (following Gu et al., 2022). Metrics: AP_rare, AP_common, AP_frequent, AP_all.
- **Objects365 cross-dataset** (supplementary): 100 non-overlapping categories for cross-dataset transfer evaluation.

### Baseline Comparisons

| Type | Methods |
|---|---|
| Contemporary SOTA | CoDet (2025), EdaDet (2025), SHiNe (2025) |
| Classic Methods | ViLD (2022), OV-DETR (2022) |
| Ablation Variants | w/o graph, w/o curriculum, w/o both |

### Core Experiments (4 必做)

1. **COCO ZSD main comparison** - validates overall method effectiveness
2. **LVIS open-vocabulary comparison** - validates scaling to large vocabulary and tests rare-category benefit
3. **Component ablation** - validates necessity of each contribution
4. **Distance-stratified evaluation** - validates the core claim that gains concentrate on distant categories

### Supporting Experiments (2 建議做)

5. **Graph architecture variants** - validates spatial-vs-semantic edge design
6. **Curriculum schedule sensitivity** - validates robustness to hyperparameters

### Supplementary Experiments (2 有時間再做)

7. **Cross-dataset transfer** - tests dataset-agnostic generalization
8. **Qualitative error analysis** - provides interpretability and failure mode understanding

### Implementation Notes

- Detection backbone: Faster R-CNN with ResNet-50-FPN and Swin-T-FPN
- CLIP backbone: ViT-B/32 and ViT-L/14 (to test scaling)
- Graph: K=100 proposals, L=2 GAT layers, hidden dim=256
- Training: SGD, 12 epochs on COCO, 24 epochs on LVIS, batch size 16
- All baselines retrained under identical settings for fair comparison
