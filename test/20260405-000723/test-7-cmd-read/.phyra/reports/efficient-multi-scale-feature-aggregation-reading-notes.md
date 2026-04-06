# Reading Notes: Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection

Zhang, Tanaka, Chen. ECCV 2026 (under review).

## Paper Identity

This paper proposes LAFA (Lightweight Adaptive Feature Aggregation), a module that replaces fixed multi-scale fusion in object detectors with learned, input-dependent routing. The core idea: not every spatial region needs information from every scale, so let the network decide which scales to fuse.

## Section-by-Section Summary

### Abstract

Claims 48.3 mAP on COCO val2017 with ResNet-50 at 42 FPS. Outperforms BiFPN by +2.2 mAP and +7 FPS. Reports ~40% reduction in redundant cross-scale interactions.

### 1. Introduction

The motivation is clean: FPN and its variants treat all spatial locations identically during cross-scale fusion. Large objects on a single scale receive unnecessary multi-scale aggregation; small objects near scale boundaries may receive suboptimal combinations. The authors frame this as a routing problem rather than a topology problem.

Three contributions are claimed: (1) the LAFA module, (2) theoretical analysis of sparse scale selection, (3) extensive experiments. Contribution 2 is not delivered in the paper body.

### 2. Related Work

Standard coverage of FPN variants, dynamic/adaptive networks, and efficient detectors. The positioning against dynamic convolution methods (CondConv, Dynamic Conv) is useful: LAFA adapts routing, not kernel weights. These are orthogonal ideas.

Notable omission: RT-DETR is discussed in related work but excluded from the main experimental comparison.

### 3. Method

**3.1 Formulation.** Standard FPN fusion: O_i = f_fuse(P_i, Upsample(O_{i+1})). Cost scales linearly with scales, quadratically with connections.

**3.2 LAFA.** The replacement: O_i = sum_{j in S_i} R_ij(P_i) * Align(P_j, P_i), where S_i is a dynamically selected subset. The routing network is a channel-attention-style block: GAP + FC (reduce by r=16) + FC + Gumbel-Softmax. At inference, top-K selection (K=2) prunes to two source scales per level.

**3.3 Implementation.** Follows standard Detectron2/MMDetection conventions. Missing details: initial learning rate, warmup epochs, augmentation pipeline.

### 4. Experiments

**Main results (Table 1).** LAFA R-50: 48.3 mAP / 42 FPS. Best in both accuracy and speed among the five compared methods. The FPS advantage over NAS-FPN (+14 FPS) is particularly notable.

**Ablation (Table 2).** Five configurations. Key takeaways:
- Adaptive routing (dense, all scales) adds +1.8 mAP but costs 4 FPS
- Sparse K=2 recovers the FPS loss and adds another +0.4 mAP
- K=1 is too aggressive: drops to 46.8 mAP
- K=3 is slightly worse than K=2 in both accuracy and speed

**Cross-backbone (Table 3).** LAFA shows consistent gains on R-101 (+2.3 mAP, +6 FPS) and Swin-T (+1.9 mAP, +7 FPS) over BiFPN. The gains are slightly larger on R-101 than Swin-T.

**Objects365 (Table 4).** +1.8 mAP and +7 FPS over BiFPN. The smaller mAP gain compared to COCO (1.8 vs 2.2) may reflect Objects365's different scale distribution.

### 5. Conclusion

Straightforward summary. Suggests extension to other multi-scale vision tasks (segmentation, depth estimation) as future work.

## Key Equations

1. Standard FPN: O_i = f_fuse(P_i, Upsample(O_{i+1}))
2. LAFA: O_i = sum_{j in S_i} R_ij(P_i) * Align(P_j, P_i)

The routing weights R_ij are predicted by: GAP(P_i) -> FC(C, C/r) -> ReLU -> FC(C/r, N_scales) -> Gumbel-Softmax (train) / top-K (inference).

## Key Definitions

- **LAFA:** Lightweight Adaptive Feature Aggregation. The proposed module.
- **Routing function R:** Per-scale prediction of which source scales to fuse. Implemented as a two-layer MLP on globally-pooled features.
- **Sparse selection:** At inference, only top-K routing weights are retained; rest are zeroed. K=2 by default.
- **Gumbel-Softmax:** Reparameterization trick enabling gradient flow through discrete sampling during training.

## Critical Observations

1. **Missing theoretical analysis.** Contribution 2 claims formal analysis showing sparse selection preserves performance, but the paper contains no theorems, lemmas, or proofs. This is a gap between claims and content.

2. **Per-image, not per-region routing.** The routing network applies global average pooling, collapsing spatial dimensions. The output is a single routing vector per scale level per image. The paper's language ("per-region routing") overstates what the architecture actually computes.

3. **"Real-time" scope.** All latency measurements use a V100 GPU. No mobile, edge, or even consumer GPU (e.g., RTX 3060) benchmarks. The real-time claim is narrowly scoped.

4. **Imprecise efficiency claim.** "40% reduction" appears in the abstract without specifying the metric. The text alternates between "cross-scale interactions" and "FLOPs." These are related but not identical quantities.

5. **Missing baseline.** RT-DETR, discussed in related work as a strong real-time detector, does not appear in any comparison table. Its absence weakens the empirical positioning.

## Open Questions

- How does LAFA perform when integrated with transformer-based detectors (e.g., DINO, Co-DETR)?
- What do the learned routing patterns look like? Do they correlate with object scale in interpretable ways?
- Would spatially-varying routing (per-region instead of per-image) yield further gains, and at what cost?
- How does the approach perform on tasks beyond detection, such as instance segmentation or panoptic segmentation?
- What is the training overhead of Gumbel-Softmax routing compared to standard FPN training?
