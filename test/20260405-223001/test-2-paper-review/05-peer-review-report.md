<!-- type: peer-review-report | generated: 2026-04-05 -->

## Summary

InfiniteVGGT proposes a training-free KV cache management system for StreamVGGT that enables infinite-horizon 3D reconstruction from continuous video streams. The method replaces attention-weight-based pruning with cosine-similarity-based token retention, resolving an incompatibility between FlashAttention and traditional cache management. Three integrated mechanisms are introduced: an immutable anchor token preserving the first frame's coordinate reference, diversity-aware token retention via cosine similarity in key space, and layer-wise adaptive budget allocation across transformer layers. Both reviewers agree on the practical relevance of the problem and the elegance of the cosine-similarity proxy. The primary disagreement concerns the sufficiency of the experimental evidence.

## Strengths

**Clear, well-scoped problem formulation.** Both reviewers recognize the FlashAttention-pruning paradox as a genuine computational tension. The positive reviewer notes that the problem is "precise, falsifiable, and anchored in measurable system constraints." The negative reviewer agrees this framing "alone is a useful contribution."

**Elegant, training-free solution.** The cosine-similarity proxy achieves 42% latency reduction (0.168s vs. 0.288s per frame) and lower Chamfer Distance (0.032 vs. 0.036) compared to attention-weight pruning (Table 4 of the paper). The training-free design means the method can be applied to future VGGT variants without retraining.

**Thorough component-level ablations.** The positive reviewer highlights Tables 4-7 as systematically evaluating each design choice. Budget sensitivity (Table 5) shows clear saturation at B = 25,000. Anchor preservation yields a 14.9% accuracy improvement (Table 7).

**Qualitative capability gap on long sequences.** InfiniteVGGT is the only method that processes all Long3D sequences (up to 9,545 frames) with bounded memory at 14.49 GB peak. StreamVGGT fails on all Long3D sequences; CUT3R encounters OOM on the longest.

## Weaknesses

**Missing bounded-cache baselines on Long3D (Major).** The negative reviewer identifies a critical gap: StreamVGGT with naive eviction strategies (FIFO, random, sliding window) is the obvious control for Long3D. Without this comparison, the improvements could be attributed to any bounded cache rather than the specific cosine-similarity mechanism. The positive reviewer does not address this gap. Additionally, the H2O and SnapKV methods discussed in the related work are not included as baselines. This is a significant omission that weakens the paper's core claim about the superiority of its pruning strategy.

**Cosine-similarity proxy lacks formal justification (Major).** The negative reviewer correctly notes that the proxy's validity depends on the query distribution. Two keys similar to each other may both be highly attended by the current query, making removal of one costly. No approximation bounds, failure-mode analysis, or empirical correlation between cosine-similarity rankings and attention-weight rankings is provided. The positive reviewer's characterization of the reasoning as "sound" is based on intuition rather than demonstrated guarantees.

**Long3D benchmark rigor (Major).** Five scenes with no external validation of ground-truth quality, no description of the capture setup, and no annotation pipeline details. The positive reviewer acknowledges limited scene diversity (W2) but grades it as Minor. Given that Long3D is both proposed and evaluated by the same authors, and that it is the primary vehicle for the paper's strongest claim (infinite-horizon capability), the lack of rigor is a more substantial concern.

**Selective metric reporting in Long3D (Minor).** Table 2 reports completion and NC only for InfiniteVGGT, omitting these metrics for CUT3R and TTT3R on scenes where they complete. This asymmetry prevents a full comparison and raises concerns about cherry-picking.

**Marginal improvements on standard benchmarks without variance (Minor).** Improvements on 7-Scenes (0.043 vs. 0.048) and Bonn (0.069 vs. 0.072) are consistent but small. Neither reviewer found evidence of statistical significance testing. The positive reviewer acknowledges this (W4) but classifies it as a suggestion.

**Layer-wise adaptive allocation: negligible measured benefit (Minor).** Table 6 shows accuracy improving from 0.098 to 0.093, a 5% change with no variance reported. The negative reviewer argues this could be within noise. The mechanism adds a temperature hyperparameter whose sensitivity is not explored.

**Anchor frame vulnerability (Suggestion).** Both reviewers note that permanently fixing the first frame as anchor is fragile in real-world deployment. No robustness analysis for degraded first frames is provided. An adaptive anchor selection mechanism would strengthen the practical claims.

## Overall Assessment

The reviewers converge on the problem's importance, the solution's elegance, and the practical value of the training-free design. They diverge on whether the experimental evidence adequately supports the claims. The positive reviewer assigns Accept, citing thorough ablations, consistent improvements, and a qualitative capability gap on long sequences. The negative reviewer assigns Weak Accept, identifying missing baselines (particularly bounded-cache alternatives on Long3D), lack of theoretical grounding for the cosine-similarity proxy, and insufficient benchmark rigor.

The chair's assessment: the paper makes a genuine conceptual contribution (the FlashAttention-pruning paradox and its resolution) and demonstrates a unique capability (processing 9,545-frame sequences with bounded memory). However, the three Major weaknesses collectively create uncertainty about whether the specific design choices are optimal or merely sufficient. The missing bounded-cache baselines (W1 of negative review) are the most actionable concern; addressing them would either confirm the cosine-similarity mechanism's advantage or reveal that simpler strategies suffice.

**Consolidated recommendation:** Weak Accept. The conceptual contribution and demonstrated capability are valuable, but the experimental gaps prevent a confident Accept. A revision addressing the bounded-cache baselines and adding variance reporting would resolve the primary concerns.

## References

- Positive reviewer draft (Section S2): Table 4 data on latency and Chamfer Distance
- Positive reviewer draft (Section S4): Tables 4-7 ablation coverage
- Positive reviewer draft (Section S5): Long3D capability analysis, Table 2
- Negative reviewer draft (Section W1): Missing baselines argument
- Negative reviewer draft (Section W2): Cosine-similarity proxy critique
- Negative reviewer draft (Section W3): Long3D validation concerns
- Negative reviewer draft (Section W4): Marginal improvements, Table 1 and Table 3
- Negative reviewer draft (Section W7): Selective metric reporting in Table 2
