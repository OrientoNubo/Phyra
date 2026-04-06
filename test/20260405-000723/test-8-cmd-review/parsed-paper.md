<!-- type: parsed-paper | generated: 2026-04-04 -->

# Parsed Paper: Structured Extraction

## Metadata

- **Title:** Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection
- **Authors:** Wei Zhang, Yuki Tanaka, Sarah Chen
- **Affiliation:** Institute of Computer Vision, National University of Technology
- **Venue:** ECCV 2026 (under review)

## Sections

| # | Section | Subsections |
|---|---------|-------------|
| 1 | Introduction | (none) |
| 2 | Related Work | Feature Pyramid Networks; Adaptive and Dynamic Networks; Efficient Detection |
| 3 | Method | 3.1 Problem Formulation; 3.2 Lightweight Adaptive Feature Aggregation (LAFA); 3.3 Implementation Details |
| 4 | Experiments | 4.1 Main Results on COCO val2017; 4.2 Ablation Study; 4.3 Cross-Backbone Results; 4.4 Results on Objects365 |
| 5 | Conclusion | (none) |

## Claimed Contributions

1. LAFA module: a lightweight module that learns per-region routing decisions for multi-scale feature aggregation, reducing FLOPs by 38% compared to BiFPN while improving accuracy.
2. Theoretical analysis: sparse scale selection preserves detection performance when the routing function has sufficient capacity.
3. Extensive experiments on COCO and Objects365, demonstrating consistent improvements across backbone architectures (ResNet-50, ResNet-101, Swin-T).

## Figures and Tables

| ID | Type | Description |
|----|------|-------------|
| Eq. 1 | Equation | Standard FPN top-down fusion formula |
| Eq. 2 | Equation | LAFA routing-based fusion formula |
| Table 1 | Table | Main results on COCO val2017 (5 methods, R-50 backbone) |
| Table 2 | Table | Ablation study: routing and sparse selection variants (5 configs) |
| Table 3 | Table | Cross-backbone results (R-101, Swin-T) |
| Table 4 | Table | Results on Objects365 (R-50) |

## Key Reported Numbers

- LAFA + R-50: 48.3 mAP, 42 FPS on V100 (COCO val2017)
- BiFPN + R-50 baseline: 46.1 mAP, 35 FPS
- NAS-FPN + R-50: 47.8 mAP, 28 FPS
- FLOPs reduction vs BiFPN: ~40% (abstract) / 38% (contribution claim)
- Adaptive routing contribution: +1.8 mAP over static fusion
- Sparse selection (K=2): best tradeoff, yielding +2.2 mAP over BiFPN baseline
- Objects365: 30.1 mAP vs BiFPN 28.3 mAP

## References

9 references cited [1]-[9], spanning FPN (2017), PANet (2018), EfficientDet/BiFPN (2020), NAS-FPN (2019), Dynamic Conv (2020), CondConv (2019), YOLOX (2021), YOLOv6 (2022), RT-DETR (2024).

## Detected Issues (non-evaluative)

1. **FLOPs reduction inconsistency:** Abstract states "approximately 40%" while contribution claim 1 states "38%". Minor discrepancy but should be reconciled.
2. **Missing theoretical analysis detail:** Contribution 2 claims "theoretical analysis showing that sparse scale selection preserves detection performance," but Section 3 provides only the formulation and routing mechanism, not a formal proof or bound.
3. **Code availability:** "Code will be released upon acceptance" -- no code or supplementary material currently available.
4. **Dataset scope:** Only COCO and Objects365 are used. No domain-specific datasets (e.g., autonomous driving, medical imaging) are tested.
5. **Training detail ambiguity:** Section 3.3 mentions both 1x and 2x schedules but does not clarify which schedule corresponds to which results in Table 1.
6. **No comparison with recent concurrent works:** Related work ends at RT-DETR (2024); no 2025-2026 concurrent methods are discussed.
7. **Gumbel-Softmax temperature:** The routing network uses Gumbel-Softmax during training but the temperature schedule and final temperature are not specified.
