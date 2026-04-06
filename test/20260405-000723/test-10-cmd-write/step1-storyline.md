# Step 1: Story Architect Output

Topic: Efficient vision-language alignment for real-time zero-shot detection

## Three-Sentence Storyline

1. **Problem**: Zero-shot object detection requires aligning visual region features with open-vocabulary language embeddings at inference time, but current alignment mechanisms (e.g., cross-attention fusion in OVD models) scale quadratically with the number of candidate regions, making real-time deployment infeasible on edge devices.

2. **Gap**: Methods such as GLIP [Li et al., 2022] and Grounding DINO [Liu et al., 2023] achieve strong open-vocabulary detection accuracy by performing deep vision-language fusion, but their fusion modules introduce 40-60% of total inference latency because they recompute region-text alignment for every forward pass without exploiting the structural redundancy across spatial positions.

3. **Core Difference**: A factored alignment mechanism that decomposes region-text matching into a spatial prior computed once per image and a lightweight residual correction per region, reducing alignment complexity from O(R x T) to O(R + T) while preserving the expressiveness needed for zero-shot generalization.

## Contribution Claims (Draft)

1. A factored vision-language alignment decomposition that separates spatial priors from semantic residuals, reducing region-text matching cost from quadratic to linear in the number of regions.

2. A prior-caching strategy that amortizes spatial structure computation across frames in video settings, enabling temporal reuse without accuracy degradation on static-background benchmarks.

3. Empirical evidence on LVIS and COCO-OVD that the factored alignment achieves within 1.2 AP of full cross-attention baselines while operating at 3.1x the throughput on a T4 GPU.

## Risk Conditions

- **R1 (Accuracy cliff)**: If the spatial prior is too coarse, the residual correction may be insufficient for fine-grained categories (e.g., distinguishing "remote control" from "cell phone"). Mitigation: ablation on fine-grained subset of LVIS.
- **R2 (Distribution shift)**: The factored decomposition assumes spatial structure learned from training domains transfers to novel domains. If domain shift is severe, the prior becomes misleading. Mitigation: cross-dataset evaluation (train COCO, eval Objects365).
- **R3 (Temporal reuse collapse)**: Prior-caching assumes slow scene dynamics. Fast camera motion or frequent scene cuts invalidate the cache. Mitigation: define a cache-invalidation threshold based on feature drift and report failure modes explicitly.
