<!-- type: review-negative | generated: 2026-04-04 -->

# Peer Review: Negative Reviewer Draft

**Paper:** Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection
**Authors:** Wei Zhang, Yuki Tanaka, Sarah Chen

## Summary

The paper proposes LAFA, a module that uses learned per-region routing to dynamically select which scale combinations to fuse in a feature pyramid. The authors claim 48.3 mAP at 42 FPS on COCO val2017 with R-50, along with 38-40% FLOPs reduction over BiFPN. The method uses Gumbel-Softmax for differentiable routing during training and top-K selection during inference.

## Weaknesses

**W1. [Major] The central efficiency claim is unsubstantiated**
The paper's headline contribution is a 38-40% FLOPs reduction. However, not a single table reports actual FLOPs (GFLOPs or MACs). Only FPS is reported. FPS depends on hardware, batch size, framework implementation, and memory access patterns. The 42 vs 35 FPS difference (20% speedup) does not validate a 38% FLOPs reduction. Without a direct FLOPs measurement, the core efficiency claim is not verifiable. This is a fundamental gap: the paper promises something it does not measure.

**W2. [Major] "Theoretical analysis" contribution does not exist in the paper**
Contribution 2 explicitly states: "We provide theoretical analysis showing that sparse scale selection preserves detection performance when the routing function has sufficient capacity." No such analysis appears in Section 3 or anywhere else. There is no theorem, no bound, no formal argument. The ablation in Table 2 provides empirical evidence, not theoretical analysis. This is a false claim in the contributions list. Either the theory must be provided or the contribution statement must be retracted.

**W3. [Major] No comparison with concurrent 2025-2026 methods**
For a paper submitted to ECCV 2026, having no baseline more recent than 2024 (RT-DETR) is a serious gap. The multi-scale detection space has been highly active. Without situating LAFA against contemporary methods, the reviewer cannot assess whether the reported gains are competitive or already surpassed. The authors have a responsibility to survey concurrent work, even if experimental comparison is infeasible.

**W4. [Major] Gumbel-Softmax training details are critically incomplete**
The routing network is the core novel component, yet its training procedure is underspecified:
- Temperature schedule: not given
- Initial/final temperature: not given
- Annealing strategy: not given
- Whether straight-through estimator is used: not stated
Gumbel-Softmax routing is notoriously sensitive to temperature (Jang et al., 2017; Maddison et al., 2017). Without these details, the method is not reproducible, and the results may be highly sensitive to unreported choices.

**W5. [Moderate] Training schedule ambiguity undermines result interpretation**
Section 3.3 states both 1x and 2x schedules are used, but Table 1 does not specify which schedule produced the main results. If LAFA uses 2x while BiFPN uses 1x (or vice versa), the comparison is unfair. This ambiguity must be resolved.

**W6. [Moderate] Single detection paradigm limits generality claims**
All experiments use anchor-based or similar detection heads. No results with anchor-free (FCOS, CenterNet) or transformer-based (DETR, DINO-DETR) detectors are provided. The Introduction claims LAFA is a general-purpose module, but the evidence does not support this breadth. Cross-backbone variation (R-50, R-101, Swin-T) is not the same as cross-paradigm variation.

**W7. [Moderate] Objects365 experiment is insufficient**
Only a single backbone (R-50) is tested on Objects365, with only BiFPN as baseline. This does not constitute "extensive experiments" on Objects365 as implied by the contribution list. At minimum, R-101 and Swin-T should be tested, and FPN/PANet baselines should be included.

**W8. [Minor] Inconsistent FLOPs reduction numbers**
The abstract claims "approximately 40%" while the contributions section claims "38%." Neither number is backed by measurement. If approximate, the precision "38%" is misleading. If measured, the measurement should appear in a table.

## Strengths (acknowledged)

**S1.** The problem of input-dependent routing for multi-scale fusion is well-motivated and practically relevant.

**S2.** The ablation study in Table 2 is well-designed and clearly isolates the K parameter's effect.

**S3.** Cross-backbone results on R-50/R-101/Swin-T show consistent trends.

## Overall Assessment

This paper has a reasonable core idea but suffers from multiple integrity issues in its claims. The most serious is the nonexistent "theoretical analysis" listed as a contribution (W2). This is not a minor wording issue; it is a false claim in the formal contributions list. The missing FLOPs validation (W1) means the paper's headline efficiency metric is unmeasured. The absent concurrent work comparison (W3) and incomplete training details (W4) compound these problems.

The paper reads as a competent empirical study that has been oversold in its contribution claims. If the authors were to: (a) remove the theoretical analysis claim, (b) add FLOPs measurements, (c) fully specify Gumbel-Softmax training, and (d) discuss concurrent work, the remaining paper would be a reasonable workshop-level or low-tier-conference contribution. For ECCV, the novelty bar requires either genuine theoretical insight or a more comprehensive experimental treatment than what is currently provided.

Recommendation: Reject in current form. Significant revision required before resubmission.
