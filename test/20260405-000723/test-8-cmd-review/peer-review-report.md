<!-- type: peer-review-report | generated: 2026-04-04 -->

# Peer Review Report (Chair Synthesis)

**Paper:** Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection
**Authors:** Wei Zhang, Yuki Tanaka, Sarah Chen
**Venue:** ECCV 2026 (under review)

## Summary

This paper proposes LAFA (Lightweight Adaptive Feature Aggregation), a module that introduces input-dependent routing into multi-scale feature pyramids for object detection. Rather than applying a fixed fusion topology to all spatial regions, LAFA uses a Gumbel-Softmax-trained routing network to select top-K scale combinations per region during inference. The authors report 48.3 mAP at 42 FPS on COCO val2017 with ResNet-50, claiming both accuracy and efficiency improvements over BiFPN and NAS-FPN.

## Divergence Analysis

The two reviewers agree on several points but diverge sharply in severity assessments. This section reconciles their positions.

### Points of Agreement

Both reviewers acknowledge:
- The core problem (input-dependent routing for multi-scale fusion) is well-motivated and practically relevant.
- The ablation study in Table 2 is well-designed and cleanly isolates the K parameter's effect.
- Cross-backbone results (R-50, R-101, Swin-T) show consistent improvement trends.
- FLOPs are not directly reported, which is a gap.
- The "theoretical analysis" contribution claim is not backed by actual theoretical content.
- Gumbel-Softmax hyperparameters are insufficiently specified.

### Points of Disagreement and Reconciliation

**1. Severity of the missing FLOPs measurement**

Reviewer+ treats this as Minor (presentation issue). Reviewer- treats this as Major (unsubstantiated central claim).

**Chair's ruling:** Reviewer- is correct. The 38-40% FLOPs reduction is stated in the abstract and as the first contribution. A claim this central must be directly measured. FPS alone does not validate FLOPs reduction, as Reviewer- correctly notes. The 20% FPS improvement (42 vs 35) is numerically inconsistent with a 38-40% FLOPs reduction unless FLOPs savings are partially offset by other bottlenecks, which the paper does not discuss. This is a Major weakness.

**2. Severity of the false "theoretical analysis" claim**

Reviewer+ downgrades this to "overstated language" (Minor). Reviewer- calls it a "false claim" (Major).

**Chair's ruling:** Reviewer- is correct. The contributions section makes an explicit promise ("We provide theoretical analysis showing...") that is entirely undelivered. In peer review, a contribution claim is a contract with the reader. Whether the authors intended to overstate or simply forgot to include the analysis, the effect is the same: a listed contribution has no corresponding content. This is Major.

**3. Overall paper quality and venue appropriateness**

Reviewer+ assesses the paper as "above the acceptance threshold" with minor revisions. Reviewer- recommends rejection, characterizing the paper as "workshop-level" after corrections.

**Chair's ruling:** Neither extreme is fully justified. Reviewer+ underweights the claim integrity issues (W1, W2); a paper that misstates its contributions cannot be "above threshold" regardless of experimental results. Reviewer-'s "workshop-level" assessment is too harsh given the solid cross-backbone empirical results and the practical value of simultaneous accuracy-speed improvement. The paper is in the borderline zone.

**4. Concurrent work gap**

Reviewer+ treats this as a suggestion. Reviewer- treats it as Major.

**Chair's ruling:** For ECCV 2026, the absence of any 2025-2026 baselines is a Moderate weakness. Complete absence of awareness of the contemporary landscape is concerning but not disqualifying if the paper's own results are strong. Upgrading from suggestion to Moderate, but not Major.

### Strengths (Reconciled)

**S1. Well-motivated problem with clear positioning**
Both reviewers agree. The paper identifies input-dependent routing as the missing element in FPN evolution. The framing is precise and distinguishes LAFA from topology-focused (NAS-FPN) and weight-focused (BiFPN) approaches.

**S2. Practical accuracy-speed tradeoff**
The simultaneous improvement in mAP (+2.2) and FPS (+7) over BiFPN is a genuinely useful result for practitioners, even if the FLOPs claim needs validation. Speed and accuracy co-improvement is uncommon in this space.

**S3. Clean ablation and cross-backbone consistency**
The K-sweep ablation is well-structured. Cross-backbone results on both CNN (R-50, R-101) and transformer (Swin-T) architectures reduce concerns about architecture-specific overfitting.

### Weaknesses (Reconciled)

**W1. [Major] Unsubstantiated FLOPs claim**
The headline efficiency number (38-40%) appears in the abstract and contributions but is never measured. Only FPS is reported, which is an inadequate proxy. The abstract-vs-contribution inconsistency (40% vs 38%) compounds the problem.

**W2. [Major] Nonexistent "theoretical analysis" contribution**
Contribution 2 promises formal analysis that does not appear anywhere in the paper. This is a claim integrity failure that must be corrected.

**W3. [Major] Incomplete Gumbel-Softmax specification**
The routing network is the core novelty, yet temperature schedule, annealing strategy, and straight-through estimator usage are all unspecified. This critically hinders reproducibility for the paper's central mechanism.

**W4. [Moderate] No contemporary baselines (2025-2026)**
All baselines predate 2025. For a 2026 venue, at least a qualitative discussion of concurrent adaptive-fusion methods is expected.

**W5. [Moderate] Training schedule ambiguity**
Both 1x and 2x schedules are mentioned but Table 1 does not specify which was used. This creates fairness ambiguity in the main comparison.

**W6. [Moderate] Limited detection paradigm coverage**
Only one detection paradigm is tested. Anchor-free and transformer-based detectors are absent, limiting the generality claim.

**W7. [Minor] Thin Objects365 evaluation**
Single backbone, single baseline on Objects365 does not constitute the "extensive experiments" implied.

### Overall Assessment

The paper presents a sound core idea with practical value: input-dependent routing for multi-scale feature fusion. The experimental results, while incomplete, show consistent trends across backbones and datasets. However, the paper is undermined by two claim integrity issues: an unmeasured headline efficiency metric and a nonexistent theoretical contribution. These are not presentation polish problems; they are structural mismatches between what the paper promises and what it delivers.

The gap between the two reviewers reflects this duality. The experimental substance is genuine and above average. The claim framing is below the standard expected at a top venue.

### Recommendation

**Revise and Resubmit**

The paper is not acceptable in its current form due to the claim integrity issues (W1, W2) and reproducibility gap (W3). However, the core contribution is real and the required revisions are feasible:

1. **Must fix:** Add GFLOPs measurements to all comparison tables. Either provide the promised theoretical analysis or retract that contribution claim. Fully specify Gumbel-Softmax training details.
2. **Should fix:** Clarify training schedule for all entries in Table 1. Add discussion of concurrent 2025-2026 methods. Extend Objects365 experiments to multiple backbones.
3. **Would strengthen:** Test with anchor-free or transformer-based detectors. Add per-size AP breakdown for all methods. Include failure case analysis.

If items 1 are addressed and results hold, the paper would likely reach the Weak Accept range at a subsequent submission.

## References

1. Jang, E., Gu, S., & Poole, B. (2017). *Categorical Reparameterization with Gumbel-Softmax*. ICLR 2017. -- Foundational reference for the routing mechanism's training procedure, relevant to W3.
2. Maddison, C.J., Mnih, A., & Teh, Y.W. (2017). *The Concrete Distribution: A Continuous Relaxation of Discrete Random Variables*. ICLR 2017. -- Alternative perspective on the same technique, relevant to W3.
