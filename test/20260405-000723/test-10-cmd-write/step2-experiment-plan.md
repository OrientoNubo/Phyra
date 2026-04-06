# Step 2: Experiment Planner Output

Input: Storyline from Step 1

## Experiment List

### E1: Main comparison -- Accuracy vs. throughput on LVIS-OVD

**Hypothesis**: Factored alignment achieves AP_rare within 1.5 points of full cross-attention baselines (GLIP, Grounding DINO) on LVIS while exceeding 2.5x throughput on T4 GPU.

**Setup**:
- Baselines: GLIP-T, Grounding DINO-T, OWL-ViT-B/16
- Metrics: AP, AP_rare, AP_common, AP_frequent, FPS (T4, batch=1), FLOPs
- Protocol: Standard LVIS v1 open-vocabulary split (base/novel categories per Gu et al., 2022)
- Falsification condition: If AP_rare drops more than 3.0 points below the strongest baseline, the factored decomposition is insufficient for rare categories.

**Priority**: P0 (core claim validation)

### E2: COCO-OVD generalization

**Hypothesis**: The accuracy-throughput trade-off observed on LVIS transfers to COCO open-vocabulary detection with comparable relative gains.

**Setup**:
- Dataset: COCO-OVD (48 base / 17 novel categories, Bansal et al., 2018)
- Same baselines, same metrics
- Falsification condition: If the relative throughput gain drops below 1.5x or AP_novel drops more than 2.0 points below GLIP-T, the method does not generalize.

**Priority**: P0 (generalization claim)

### E3: Ablation -- Factored decomposition components

**Hypothesis**: Both the spatial prior and the residual correction are necessary; removing either degrades AP by more than 1.5 points.

**Setup**:
- Variants: (a) full model, (b) spatial prior only (no residual), (c) residual only (no prior, equivalent to lightweight cross-attention), (d) random spatial prior + residual
- Dataset: LVIS-OVD
- Metrics: AP, AP_rare, FPS
- Falsification condition: If variant (b) or (c) matches full model within 0.5 AP, the removed component is redundant.

**Priority**: P0 (contribution validation)

### E4: Fine-grained category analysis (Risk R1)

**Hypothesis**: The factored alignment does not disproportionately harm fine-grained distinctions compared to full cross-attention.

**Setup**:
- Select 50 LVIS categories with highest inter-class visual similarity (measured by CLIP embedding cosine)
- Compare per-category AP between factored model and Grounding DINO-T
- Falsification condition: If mean per-category AP on the confusable subset drops more than 4.0 points, the spatial prior is too coarse for fine-grained tasks.

**Priority**: P1 (risk mitigation)

### E5: Cross-dataset transfer (Risk R2)

**Hypothesis**: Spatial priors learned on COCO transfer to Objects365 without retraining.

**Setup**:
- Train on COCO, evaluate on Objects365 validation (365 categories)
- Compare factored model vs. baselines under the same transfer setting
- Falsification condition: If factored model AP drops more than 5.0 points relative to full-attention baseline under transfer, the prior is domain-specific.

**Priority**: P1 (robustness claim)

### E6: Temporal prior caching in video (Contribution 2)

**Hypothesis**: Caching spatial priors across consecutive video frames maintains AP within 0.8 points of per-frame computation while increasing throughput by at least 1.4x.

**Setup**:
- Dataset: TAO-OVD or VID-OVD (video open-vocabulary detection)
- Cache reuse intervals: 1, 2, 4, 8 frames
- Cache invalidation based on feature drift threshold
- Metrics: AP, FPS, cache hit rate
- Falsification condition: If AP drops more than 2.0 points at 4-frame reuse or throughput gain is below 1.2x, caching does not provide meaningful benefit.

**Priority**: P1 (secondary contribution)

### E7: Latency breakdown analysis

**Hypothesis**: The alignment module accounts for less than 15% of total inference latency in the factored model, compared to 40-60% in baselines.

**Setup**:
- Profile each model component (backbone, neck, alignment, detection head) using PyTorch profiler
- Report wall-clock time per component on T4 GPU
- Falsification condition: If alignment still accounts for more than 25% of latency, the efficiency claim is overstated.

**Priority**: P1 (quantitative efficiency claim support)

## Priority Ranking Summary

| Priority | Experiments | Rationale |
|----------|------------|-----------|
| P0 | E1, E2, E3 | Core claims: accuracy-throughput trade-off, generalization, component necessity |
| P1 | E4, E5, E6, E7 | Risk mitigation and secondary contribution validation |
