<!-- type: review-scoring-report | generated: 2026-04-04 -->

# Review Scoring Report (Chair)

**Paper:** Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection
**Authors:** Wei Zhang, Yuki Tanaka, Sarah Chen

## Technical Development Path

**[2017] FPN (Lin et al., CVPR 2017)**
Introduced the top-down pathway with lateral connections for multi-scale feature fusion in object detection. Core limitation: uniform fusion applied identically to all spatial locations regardless of local content, with no mechanism to skip unnecessary cross-scale interactions.

**[2018] PANet (Liu et al., CVPR 2018)**
Added a bottom-up path augmentation to FPN, improving information flow from shallow high-resolution features to deep layers. Core limitation: fusion topology remains fixed and input-independent; computation scales with the number of pathways regardless of per-region utility.

**[2020] BiFPN (Tan et al., CVPR 2020)**
Introduced weighted bidirectional cross-scale connections with learnable scalar fusion weights. Core limitation: weights are input-independent parameters fixed after training, unable to adapt to instance-level variation in scale distribution.

**[2019] NAS-FPN (Ghiasi et al., CVPR 2019)**
Used neural architecture search to discover an optimal fusion topology. Core limitation: the discovered topology, while better than hand-designed ones, is still static and applied uniformly across all inputs and spatial locations.

**[2026] LAFA (Zhang et al., this paper)**
Proposes input-dependent routing via Gumbel-Softmax, enabling per-region dynamic selection of which scales to fuse. Core limitation (revealed by this review): the efficiency claim is unmeasured (no FLOPs data), the claimed theoretical analysis is absent, and the routing network's training procedure is underspecified.

## Dimension Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Novelty** | 6/10 | Input-dependent routing for FPN fusion is a natural next step after BiFPN's learnable weights and NAS-FPN's searched topology. The Gumbel-Softmax routing mechanism is borrowed from NAS/mixture-of-experts literature. The specific application to FPN lateral connections is new but predictable. No concurrent work comparison makes novelty margin hard to assess. |
| **Soundness** | 4/10 | Two of three stated contributions are not substantiated: FLOPs claim lacks measurement, theoretical analysis claim has no corresponding content. The empirical results themselves (mAP, FPS) appear internally consistent, but the gap between claims and evidence is a soundness issue. Training schedule ambiguity adds uncertainty. |
| **Significance** | 7/10 | Multi-scale detection efficiency is a high-impact problem. Simultaneous accuracy and speed improvement, if reproducible, has direct industrial value. The consistent cross-backbone results amplify potential impact. |
| **Clarity** | 5/10 | The paper is readable at the surface level, but clarity is fundamentally undermined by the mismatch between stated contributions and delivered content. Missing Gumbel-Softmax details, unspecified training schedules, and the FLOPs/FPS conflation create confusion about what was actually done and measured. |
| **Reproducibility** | 3/10 | No code release. Gumbel-Softmax temperature, annealing, and straight-through estimator details are missing. Training schedule per experiment is ambiguous. FLOPs are not measured, so even with code, the efficiency claim cannot be verified against the paper. |

## Weighted Score and Grade

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Novelty | 0.25 | 6 | 1.50 |
| Soundness | 0.25 | 4 | 1.00 |
| Significance | 0.20 | 7 | 1.40 |
| Clarity | 0.15 | 5 | 0.75 |
| Reproducibility | 0.15 | 3 | 0.45 |
| **Weighted Total** | **1.00** | | **5.10** |

**Grade Scale:**
- 8.0-10.0: Strong Accept
- 6.5-7.9: Weak Accept
- 5.0-6.4: Borderline / Weak Reject
- 3.0-4.9: Reject
- 1.0-2.9: Strong Reject

**This paper's grade: Borderline / Weak Reject (5.10)**

## Recommendation

**Revise and Resubmit**

The paper sits at the lower end of the borderline zone. The core idea has merit, but the claim-evidence gap is too wide for acceptance at a top venue. Specific revision targets:

1. **Gate to acceptance (must fix):**
   - Add direct FLOPs/GFLOPs measurements to all comparison tables (W1). If the 38-40% claim holds, Soundness rises to 6.
   - Either deliver the theoretical analysis or retract contribution 2 (W2). Honest contribution framing would raise Soundness to 5-6.
   - Fully specify Gumbel-Softmax training (W3). This alone could raise Reproducibility to 5.
   - Projected score after fixes: Soundness 6, Reproducibility 5 => weighted total 5.85 (still borderline, but closer to Weak Accept).

2. **Strengthen further (should fix):**
   - Discuss concurrent 2025-2026 methods (may affect Novelty score).
   - Unify and clarify training schedules across all tables.
   - Test on anchor-free or transformer-based detectors.
   - Expand Objects365 experiments.
   - Projected score with all fixes: Novelty 7, Soundness 6, Significance 7, Clarity 7, Reproducibility 6 => weighted total 6.55 (Weak Accept).

3. **Overall judgment:** The path from current state (5.10) to acceptance (6.5+) requires addressing all "must fix" items and at least half of the "should fix" items. This is achievable within a single revision cycle (estimated 3-4 weeks of additional experiments and writing).
