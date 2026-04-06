<!-- type: positive-reviewer-draft | generated: 2026-04-05 -->

## Summary

InfiniteVGGT proposes a training-free extension of StreamVGGT that enables infinite-horizon 3D reconstruction from continuous video streams by introducing a bounded, diversity-aware rolling KV cache. The paper identifies a genuine computational paradox (FlashAttention incompatibility with attention-based pruning) and resolves it through cosine-similarity-based token retention, immutable anchor tokens, and layer-wise adaptive budget allocation. Evaluation spans standard benchmarks (7-Scenes, NRGBD), a new Long3D benchmark with sequences up to 9,545 frames, and video depth estimation on the Bonn dataset.

## Strengths

**S1. Well-defined and practically relevant problem.**
The tension between offline reconstruction quality and online memory scalability is real and well-motivated. StreamVGGT's linear KV cache growth (O(T * P)) is a concrete engineering bottleneck: it fails on all Long3D sequences due to memory overflow (Table 2). The paper frames the problem not as an abstract scaling challenge but as a specific incompatibility between FlashAttention's efficiency mechanism and traditional pruning's need for materialized attention weights. This framing is precise, falsifiable, and anchored in measurable system constraints.

**S2. Elegant resolution of the FlashAttention-pruning paradox.**
The core insight, that cosine similarity in key space serves as a valid proxy for attention-based importance, is both theoretically motivated and empirically validated. Table 4 shows that cosine-similarity pruning achieves lower Chamfer Distance (0.032 vs. 0.036) and 42% lower per-frame latency (0.168s vs. 0.288s) compared to attention-weight pruning, while reducing memory from 17.30 GB to 14.49 GB. The reasoning is sound: if two keys are nearly identical, the softmax attention distribution over them will be nearly uniform, making one of them redundant. This avoids the O(N^2) materialization entirely.

**S3. Training-free design with strong practical implications.**
The method requires no fine-tuning of the pretrained StreamVGGT weights. This is a significant practical advantage: it means any future improvements to the base VGGT architecture can be immediately combined with InfiniteVGGT's memory management. The implementation details (Section 3.3) specify concrete hyperparameters (B = 25,000 tokens per head, temperature = 1.0), and Table 5's budget sweep confirms saturation around B = 25,000, lending credibility to the default choice.

**S4. Comprehensive ablation studies.**
The paper systematically evaluates each component. Table 4 compares pruning strategies. Table 5 demonstrates budget sensitivity with a clear saturation curve. Table 6 isolates the effect of layer-wise adaptive allocation (Acc. improving from 0.098 to 0.093). Table 7 quantifies the anchor frame's contribution (14.9% accuracy improvement). Each ablation answers a specific question about a design choice, and each is presented with concrete numbers.

**S5. Long3D benchmark fills a genuine evaluation gap.**
Existing benchmarks (7-Scenes with 300-500 frames) do not stress-test long-horizon capabilities. Long3D provides sequences from 2,128 to 9,545 frames across diverse environments. This is a meaningful contribution to the community: CUT3R encounters OOM on the 9,545-frame Academic Building sequence, and StreamVGGT fails on all Long3D sequences. InfiniteVGGT processes all of them with bounded memory (14.49 GB peak), demonstrating a qualitative capability that no existing baseline possesses.

**S6. Consistent improvements across multiple tasks and metrics.**
On 7-Scenes, InfiniteVGGT achieves the best mean accuracy (0.043 vs. StreamVGGT's 0.048, Table 1). On NRGBD, it leads on all reported metrics. On Bonn depth estimation, it achieves Abs Rel of 0.069 vs. StreamVGGT's 0.072 (Table 3). The improvements are modest but consistent, and they come with the added benefit of bounded memory, which is the primary contribution.

## Weaknesses

**W1. Completion metric underperformance (Minor).**
The authors acknowledge in the conclusion that InfiniteVGGT "underperforms on the completion metric compared to some baselines." However, the completion numbers in Table 1 actually show InfiniteVGGT leading (0.025 mean, 0.005 median vs. StreamVGGT's 0.027 and 0.006). This discrepancy between the stated limitation and the presented data is confusing. If the underperformance occurs on Long3D specifically, the paper should present completion metrics for baselines on Long3D sequences where they do not OOM.

**W2. Limited diversity in Long3D scenes (Minor).**
Long3D contains five scenes, all of which appear to be indoor or campus environments. It is unclear whether the method's advantages generalize to outdoor, dynamic, or textureless environments. The benchmark would benefit from greater scene diversity, though this does not undermine the demonstrated capability on the scenes tested.

**W3. Anchor frame assumption (Suggestion).**
The immutable anchor token permanently preserves the first frame's KV cache. This design assumes the first frame provides a reliable coordinate reference. In real-world deployment, the first frame might be occluded, poorly exposed, or unrepresentative. A discussion of failure modes or an adaptive anchor selection mechanism would strengthen the work.

**W4. Statistical reporting (Suggestion).**
No confidence intervals, standard deviations, or significance tests are reported. While the improvements are consistent across benchmarks, the magnitude is sometimes small (e.g., 0.043 vs. 0.048 on 7-Scenes accuracy). Variance reporting would help distinguish genuine improvements from noise.

## Overall Assessment

InfiniteVGGT makes a clear, well-scoped contribution: it enables truly infinite-horizon 3D reconstruction with bounded memory by replacing attention-based pruning with a cosine-similarity proxy that is compatible with FlashAttention. The problem is real, the solution is elegant and training-free, the ablations are thorough, and the Long3D benchmark fills a genuine gap. The weaknesses are minor and do not undermine the core claims. This is a solid contribution that advances the state of streaming 3D geometry understanding.

**Recommendation:** Accept.
