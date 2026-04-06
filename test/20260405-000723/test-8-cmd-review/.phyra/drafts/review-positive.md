<!-- type: review-positive | generated: 2026-04-04 -->

# Peer Review: Positive Reviewer Draft

**Paper:** Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection
**Authors:** Wei Zhang, Yuki Tanaka, Sarah Chen

## Summary

This paper proposes Lightweight Adaptive Feature Aggregation (LAFA), a module that replaces static multi-scale fusion in detection necks with learned, input-dependent routing. The core idea is that not all spatial regions need all cross-scale interactions; by dynamically selecting top-K scale combinations per region, LAFA reduces computation while improving accuracy. The authors report 48.3 mAP at 42 FPS on COCO val2017 with R-50, outperforming BiFPN (46.1 mAP, 35 FPS) and NAS-FPN (47.8 mAP, 28 FPS).

## Strengths

**S1. Problem framing is sharp and well-motivated**
The observation that static fusion topologies waste computation on regions that do not benefit from cross-scale interaction is stated precisely in the Introduction. The authors correctly identify input-dependent routing as the missing ingredient, distinguishing their approach from prior work that focused on topology design (NAS-FPN) or weight learning (BiFPN). This framing positions the contribution clearly within the existing literature.

**S2. Simultaneous accuracy and speed improvement is rare and practically valuable**
Most FPN improvements trade speed for accuracy. LAFA achieves both: +2.2 mAP and +7 FPS over BiFPN. This is not a marginal result. The 42 FPS on V100 puts LAFA within real-time deployment range for many industrial applications, making this work immediately relevant beyond academic benchmarks.

**S3. Ablation study isolates the contribution of each component**
Table 2 cleanly separates the effect of adaptive routing (+1.8 mAP over static fusion) from sparse selection. The K=1/2/3 sweep shows a clear accuracy-efficiency tradeoff curve, with K=2 as the sweet spot. This level of ablation transparency is above average for the detection literature.

**S4. Cross-backbone generalization is convincing**
Results on R-50, R-101, and Swin-T all show consistent LAFA improvements (+1.9 to +2.3 mAP). The fact that LAFA works with both CNN and transformer backbones suggests the routing mechanism captures a general principle rather than exploiting architecture-specific artifacts.

**S5. Objects365 results demonstrate domain transfer**
Testing on Objects365 (365 categories, diverse image sources) beyond COCO shows that LAFA's routing mechanism generalizes to a more challenging distribution. The +1.8 mAP improvement on Objects365 is consistent with COCO gains.

## Weaknesses (noted constructively)

**W1. [Minor] FLOPs not directly reported**
The 38-40% FLOPs reduction is the headline efficiency claim, but no table includes a GFLOPs column. FPS is reported instead, which is hardware-dependent. Adding a FLOPs column to Tables 1 and 3 would make the efficiency claim hardware-independent and more convincing.

**W2. [Minor] Theoretical analysis claim is overstated**
Contribution 2 claims "theoretical analysis" but the paper provides only the formulation and empirical validation. This is more accurately described as "empirical analysis" or "design rationale." Adjusting the language would avoid overstatement without weakening the paper's actual content.

**W3. [Minor] Gumbel-Softmax details are incomplete**
The temperature schedule, initial temperature, and annealing strategy for Gumbel-Softmax are not specified. Since routing quality depends on these choices, their omission affects reproducibility. A brief paragraph or appendix entry would resolve this.

**W4. [Suggestion] Concurrent work discussion would strengthen positioning**
The related work section's most recent citation is 2024. Given that ECCV 2026 submissions exist in a context of rapid method development, discussing any known concurrent adaptive-fusion methods would preemptively address reviewer concerns about novelty overlap.

**W5. [Suggestion] Per-size AP breakdown across methods**
Table 1 reports APs/APm/APl only for LAFA. Extending this to all methods would let readers see where LAFA's gains concentrate (likely small objects), strengthening the narrative.

## Overall Assessment

LAFA addresses a real and well-defined limitation in multi-scale detection: the inefficiency of static fusion for spatially varying content. The solution is clean, lightweight, and the experimental evidence across multiple backbones and datasets is convincing. The weaknesses are primarily presentation-level (FLOPs reporting, theoretical claim language, hyperparameter details) and do not undermine the core contribution. This paper makes a solid incremental contribution to the detection efficiency literature and is above the acceptance threshold in its current form, with minor revisions recommended.
