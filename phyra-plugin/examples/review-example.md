# Peer Review Example

> **Purpose:** This file serves as a format and depth reference (gold standard) for the `peer-reviewer-chair` agent.
> The chair agent should read this example before writing the final report to ensure its output matches this level of structure, specificity, and scoring logic.
>
> **Paper information (fictitious):**
> - Title: *Adaptive Feature Pyramid Networks for Multi-Scale Object Detection*
> - Authors: Wei-Lin Chen, Satoshi Nakamura, Priya Raghavan (2026)
> - Venue: Submitted to ECCV 2026
> - arXiv: 2602.14387 (fictitious)

---

## Report 1: peer-review-report.md

<!-- type: peer-review-report | generated: 2026-03-15 -->

### Summary

This paper proposes the Adaptive Feature Pyramid Network (AFPN), which introduces a channel-spatial gating mechanism on top of the traditional FPN's lateral connections, enabling feature maps at different scales to dynamically adjust their fusion weights based on the input image. The authors report that AFPN paired with a Faster R-CNN ResNet-50 backbone achieves 42.7 mAP on COCO val2017 (+1.9 over vanilla FPN) and 34.1 mAP on VisDrone-DET for small-object scenarios (+2.6). The overall idea is intuitive and sound, and the experiments span multiple backbones and detection frameworks. However, notable deficiencies remain in the theoretical motivation for the gating mechanism, the completeness of ablation studies, and comparisons with recent concurrent work.

### Strengths

**S1. Precise problem identification with clear motivation**
The scale mismatch problem in multi-scale feature fusion has been noted by multiple prior works (e.g., PANet, NAS-FPN), but this paper is the first to quantify mutual information loss between different levels from an information-theoretic perspective (Section 3.1, Fig. 2), providing a convincing starting point for the subsequent design.

**S2. Gating mechanism balances efficiency and expressiveness**
The channel-spatial dual gating adds only 0.8 GFLOPs (Table 3), compared to BiFPN's repeated top-down/bottom-up (+2.1 GFLOPs), making it considerably lighter. The authors also provide a latency benchmark (Table 5): only +1.2 ms/image on V100, demonstrating practical deployment value.

**S3. Thorough cross-framework generalization validation**
AFPN shows consistent gains across Faster R-CNN, RetinaNet, and FCOS (Table 2), with stable trends across ResNet-50/101 and Swin-T backbones, reducing concerns about architecture-specific dependence.

**S4. Standout performance on small-object detection**
VisDrone-DET results (Table 6) show AFPN's gain on AP_small (+3.8) far exceeds its gain on AP_large (+0.7), consistent with the authors' hypothesis that "adaptive fusion is most effective when the scale gap is large" -- providing positive corroborating evidence.

**S5. Informative visualization analysis**
The gating weight heatmaps in Fig. 5 clearly show shallow levels being upweighted in small-object regions, and the GradCAM comparison in Fig. 6 intuitively demonstrates that AFPN focuses more precisely on target boundaries than FPN.

### Weaknesses

**W1. [Major] Information-theoretic analysis lacks rigorous derivation**
Section 3.1 claims that lateral connections cause mutual information loss, but the estimation uses only a MINE estimator with a single seed, with no reported variance. MINE is known to exhibit significant estimation bias in high-dimensional spaces (Belghazi et al., 2018, Table 1 reports >15% relative error for dim>256). This deficiency directly undermines the theoretical motivation for the gating mechanism: if the MI loss magnitude is unstable, the design decisions may be built on noise.
**Suggested fix:** Switch to the InfoNCE bound or at minimum report mean/std over 5 seeds; if the MI loss magnitude's confidence interval includes zero, the motivation must be reframed.

**W2. [Major] Ablation study lacks critical variants**
Table 4's ablation compares only channel-only / spatial-only / dual gating, but omits: (a) replacing gating with SE-block or CBAM, (b) the effect of gating placement (before vs. after lateral conv), (c) per-level contribution of gating across different FPN levels. Without (a), readers cannot determine whether the gains come from the gating architecture itself or from a generic attention effect.
**Suggested fix:** Add SE/CBAM drop-in replacement experiments and per-level ablation.

**W3. [Major] Missing comparison with important concurrent work**
DyFPN (arXiv 2601.09821), which also adopts dynamic fusion weights and reports 43.1 mAP on COCO, was publicly available before the ECCV 2026 submission deadline. This paper does not mention this concurrent work at all. While outperforming concurrent work is not strictly required, the differences must at minimum be discussed in Related Work so reviewers can assess the novelty margin.
**Suggested fix:** Add a qualitative comparison with DyFPN (design differences) and a quantitative comparison (if code/checkpoints are available).

**W4. [Minor] Insufficient VisDrone experimental setup description**
Section 4.3 does not specify which VisDrone train/val split version is used (VisDrone has 2019/2021 versions), nor does it report the image resizing strategy. Given that VisDrone image resolutions vary widely (960x540 to 2000x1500), the resize strategy significantly affects small-object AP, and omitting this information makes the results hard to reproduce.
**Suggested fix:** Clearly state the dataset version, resize/crop strategy, and detailed multi-scale training parameters.

**W5. [Minor] Inconsistent training schedules in Table 2**
Faster R-CNN results use the 2x schedule while FCOS uses the 1x schedule (footnote 3). Different schedules lead to different baseline saturation levels, potentially raising fairness concerns about AFPN's reported gains.
**Suggested fix:** Unify by reporting results under both 1x and 2x schedules.

**W6. [Suggestion] No failure case analysis**
All existing visualizations show only success cases. Adding scenarios where AFPN gating fails (e.g., extreme occlusion, dense crowds) would help readers understand the method's applicability boundaries.

### Overall Assessment

The core contribution (adaptive gating for FPN) is intuitively sound, and the experimental breadth is commendable. However, the three Major weaknesses form a structural problem: **the logical chain from theoretical motivation (W1) to design choices (W2) to positioning (W3) lacks a solid foundation.**

Specifically, if the MI analysis in W1 is unreliable, then the gating design loses its principled motivation and degrades to "yet another attention module." The lack of SE/CBAM comparison in W2 further fails to rule out this concern. Meanwhile, the concurrent work in W3 adopts a similar strategy, making the novelty claim require even more precise differentiation. The interaction of these three issues means the paper's core claim ("AFPN provides principled and effective adaptive fusion") currently lacks sufficient evidence.

That said, W1-W3 are all fixable experimental/argumentative gaps, not fundamental flaws. If the authors can address them in a revision, this paper has the potential to become a solid contribution.

### References

1. Belghazi, M.I. et al. (2018). *Mutual Information Neural Estimation*. ICML 2018. -- Used to assess the known limitations of the MINE estimator in W1.
2. Ghiasi, G., Lin, T.-Y., & Le, Q.V. (2019). *NAS-FPN: Learning Scalable Feature Pyramid Architecture for Object Detection*. CVPR 2019. -- Representative work on FPN architecture search, serving as a baseline reference for this paper.
3. Hu, J., Shen, L., & Sun, G. (2018). *Squeeze-and-Excitation Networks*. CVPR 2018. -- Attention baseline suggested in W2.

---

## Report 2: review-scoring-report.md

<!-- type: review-scoring-report | generated: 2026-03-15 -->

### Technical Development Path

**[2017] FPN (Lin et al., CVPR 2017)**
First proposed a top-down pathway with lateral connections for multi-scale feature fusion. Core limitation: all scales use the same 1x1 conv for fusion, unable to adaptively adjust each level's contribution weight based on the input.

**[2018] PANet (Liu et al., CVPR 2018)**
Added a bottom-up path augmentation on top of FPN's top-down pathway, alleviating the problem of shallow high-resolution features being diluted at deeper levels. Core limitation: the fusion path topology remains fixed, and feature importance weights are implicitly determined by the architecture, unable to dynamically adjust based on the scale distribution of different images.

**[2020] BiFPN (Tan et al., CVPR 2020)**
Introduced weighted bi-directional cross-scale connections with learnable fusion weights, the first in the FPN family to enable per-connection importance learning. Core limitation: fusion weights are input-independent scalar parameters that become fixed after training, unable to handle instance-level variation in scale distribution at inference time.

**[2026] AFPN (Chen et al., this paper)**
Proposes a channel-spatial gating mechanism that makes fusion weights an input-dependent function, achieving instance-level adaptive fusion. Core limitation (identified by this review): the theoretical motivation for the adaptive mechanism (MI analysis) and comparison against attention baselines are both insufficient, leaving the source of the gains unconfirmed.

### Per-Dimension Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Novelty** | 6/10 | The individual components of the gating mechanism (channel attention, spatial attention) are known techniques; novelty lies primarily in the specific placement choice of "integrating them into FPN lateral connections." The undiscussed differences with concurrent DyFPN further compress the novelty space. |
| **Soundness** | 5/10 | Experimental results themselves are credible (multi-framework/multi-backbone validation), but the reliability of the MI-based theoretical analysis is questionable (MINE single seed), and the ablation lacks critical attention baseline comparisons, leaving the "why it works" argument chain incomplete. |
| **Significance** | 7/10 | Multi-scale detection is a high-impact problem, and the method has practical advantages with low overhead (+0.8 GFLOPs). The small-object gains on VisDrone (+3.8 AP_small), if reproducible, have direct value for drone/surveillance applications. |
| **Clarity** | 7/10 | Overall structure is clear; Fig. 1's architecture diagram and Fig. 5's gating heatmap are informative. Main deductions for insufficient VisDrone experimental setup description and inadequately explained training schedule inconsistency. |
| **Reproducibility** | 5/10 | No code provided (only "upon acceptance" promise), VisDrone split version unlabeled, and MI estimation hyperparameters (MINE network architecture, learning rate) incompletely listed. |

### Weighted Total Score and Grade

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Novelty | 0.25 | 6 | 1.50 |
| Soundness | 0.25 | 5 | 1.25 |
| Significance | 0.20 | 7 | 1.40 |
| Clarity | 0.15 | 7 | 1.05 |
| Reproducibility | 0.15 | 5 | 0.75 |
| **Weighted Total** | **1.00** | | **5.95** |

**Grade mapping:**
- 8.0-10.0: Strong Accept
- 6.5-7.9: Weak Accept
- 5.0-6.4: Borderline / Weak Reject
- 3.0-4.9: Reject
- 1.0-2.9: Strong Reject

**This paper's grade: Borderline / Weak Reject (5.95)**

### Recommendation

**Recommendation: Revise and Resubmit**

This paper falls in the borderline zone. The core idea has practical value, but the argument chain is incomplete. Specifically:

1. **Required revisions (gate to acceptance):** Complete the MI analysis robustness verification (W1), add SE/CBAM attention baseline comparisons (W2), and discuss the DyFPN concurrent work (W3). If these three revisions are completed with positive results, Soundness is expected to rise to 7 and Novelty to 7, bringing the total to 6.75 (Weak Accept).

2. **Recommended revisions (to strengthen further):** Unify training schedules (W5), add failure case analysis (W6), and complete the VisDrone experimental setup description (W4).

3. **Overall judgment:** This paper is not suitable for acceptance in its current state, but the core idea and experimental scale are encouraging. The authors are advised to spend 2-3 weeks completing the above experiments and resubmit, or target the next deadline at a peer-level venue.
