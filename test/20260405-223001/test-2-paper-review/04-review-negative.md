<!-- type: negative-reviewer-draft | generated: 2026-04-05 -->

## Summary

InfiniteVGGT extends StreamVGGT with a training-free KV cache pruning mechanism based on cosine similarity rather than attention weights, combined with an immutable anchor token and layer-wise adaptive budget allocation. The paper claims to resolve the tension between FlashAttention efficiency and cache management, enabling infinite-horizon 3D reconstruction. I find the problem framing compelling, but the experimental evaluation contains several significant gaps that weaken the paper's claims.

## Strengths

**S1. Clearly articulated computational paradox.**
The FlashAttention-pruning incompatibility is a genuine technical problem. The observation that FlashAttention avoids materializing O(N^2) attention matrices, which are exactly what traditional pruning requires, is a concrete and well-defined tension. This framing alone is a useful contribution to the community's understanding.

**S2. Simple, interpretable mechanism.**
The three-component design (anchor, cosine-similarity pruning, adaptive budgets) is easy to understand and implement. The training-free nature lowers the barrier to adoption. The cosine-similarity proxy has intuitive justification: redundant keys receive diffused attention, so removing them should minimally affect output quality.

## Weaknesses

**W1. Missing critical baselines for the core claim (Major).**
The paper claims to solve infinite-horizon reconstruction, yet the baseline comparison on Long3D (Table 2) is severely incomplete. StreamVGGT, the most direct baseline, is absent from Table 2 entirely because it runs out of memory. But StreamVGGT with a naive cache eviction strategy (e.g., FIFO, random eviction, or sliding window) would be the obvious control experiment. Without this comparison, we cannot distinguish InfiniteVGGT's contribution from the trivial observation that "any bounded cache is better than no cache management." Similarly, H2O and SnapKV, discussed in the related work (Section 2), are attention-based pruning methods that could be adapted to StreamVGGT. Table 4 compares "attention weights" vs. "cosine similarity" but does not specify whether "attention weights" refers to H2O, SnapKV, or a custom implementation, and this comparison is only shown on a single dataset.

**W2. The cosine-similarity proxy lacks theoretical grounding (Major).**
The paper argues that cosine-similar keys receive similar attention weights, making one redundant. This intuition is plausible but never formally justified. The relationship between key-space cosine similarity and the attention distribution depends on the query distribution, which changes with each new frame. A pair of keys that are similar to each other may both be highly relevant to the current query, meaning that removing one would lose important information. The paper provides no analysis of when this proxy fails, no bound on the approximation error relative to true attention-based importance, and no empirical analysis of the correlation between cosine-similarity rankings and attention-weight rankings across different layers and sequence lengths.

**W3. Long3D benchmark lacks independent validation (Major).**
Long3D is both proposed and used by the same authors to evaluate their method. The five scenes are all captured by the authors (presumably), with no external validation of ground-truth quality. The paper does not describe the capture setup, ground-truth acquisition method, or annotation pipeline. Without these details, it is impossible to assess whether the benchmark's ground truth is reliable. Furthermore, five scenes is a very small benchmark. The claim that Long3D enables "rigorous evaluation of long-term performance" is not supported by a five-scene dataset with no external validation.

**W4. Marginal improvements on standard benchmarks (Minor).**
On 7-Scenes, InfiniteVGGT achieves 0.043 mean accuracy vs. StreamVGGT's 0.048 (Table 1), an improvement of approximately 10%. On Bonn depth estimation, Abs Rel improves from 0.072 to 0.069 (Table 3), roughly 4%. These improvements are small and reported without any measure of variance. On standard-length sequences where StreamVGGT does not encounter memory issues, InfiniteVGGT's cache pruning is actively discarding information. The fact that it still improves slightly is interesting but could be within noise without statistical validation.

**W5. Layer-wise adaptive allocation shows negligible benefit (Minor).**
Table 6 shows that adaptive allocation improves accuracy from 0.098 to 0.093 and completion from 0.057 to 0.056, with NC changing from 0.554 to 0.555. These are extremely small differences. The mechanism adds complexity (temperature hyperparameter, per-layer diversity computation) for a benefit that is likely within measurement noise. The paper does not provide variance estimates to demonstrate that this difference is statistically meaningful.

**W6. Anchor frame vulnerability unaddressed (Minor).**
The anchor token permanently preserves the first frame's KV cache. The paper justifies this by noting that "VGGT establishes the first frame as the canonical coordinate system." However, this is an inherited design constraint from VGGT, not a principled choice. In real deployments, the first frame may be uninformative (e.g., motion blur, featureless wall, occlusion). The paper does not test robustness to degraded first frames, nor does it discuss any mechanism for anchor replacement or reinitialization.

**W7. Incomplete reporting in Long3D results (Minor).**
Table 2 reports CUT3R and TTT3R accuracy alongside InfiniteVGGT's accuracy, completion, and NC. But CUT3R and TTT3R's completion and NC values are missing. This makes it impossible to assess whether InfiniteVGGT's advantage is concentrated in accuracy or extends across all metrics. Selectively reporting metrics for different methods raises concerns about cherry-picking.

**W8. No analysis of failure modes or degradation patterns (Suggestion).**
The paper does not show how reconstruction quality degrades as sequence length increases beyond the budget capacity. A plot of accuracy vs. sequence length for different budget sizes would be far more informative than Table 5's two-point comparison (300 and 500 frames). For a paper whose core claim is about infinite-horizon operation, the absence of any analysis showing quality trajectories over thousands of frames is a notable gap.

## Overall Assessment

InfiniteVGGT addresses a real problem with an intuitive solution, and the training-free design is practically appealing. However, the experimental evaluation has significant gaps. The missing baselines on Long3D (W1) make it impossible to attribute the improvements to the specific pruning strategy rather than to simply having any bounded cache. The lack of theoretical or empirical analysis of when the cosine-similarity proxy fails (W2) leaves the method's reliability uncertain. The Long3D benchmark, while addressing a real need, lacks the rigor to support the claims made about it (W3). The improvements on standard benchmarks are marginal and unreported with variance (W4). The selective metric reporting in Table 2 (W7) is concerning.

The paper makes a useful conceptual contribution (the FlashAttention-pruning paradox and the cosine-similarity resolution), but in its current form, the experimental evidence does not adequately support the strength of the claims. The gap between what is claimed (state-of-the-art, robust infinite-horizon reconstruction) and what is demonstrated (modest improvements on short sequences, incomplete comparisons on long sequences) needs to be closed.

**Recommendation:** Weak Accept, conditional on addressing the missing baselines (W1) and providing statistical validation (W4).
