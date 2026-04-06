<!-- Step 2: Experiment Planner | NT mode | generated: 2026-04-05 -->

# Experiment Plan: Structure-Aware Vision-Language Zero-Shot Detection

## Baseline Coverage

| Baseline Type | Method | Selection Rationale |
|---|---|---|
| 同期 SOTA | CoDet (Ma et al., 2025), EdaDet (Shi et al., 2025) | Top-performing CLIP-based ZSD methods on COCO/LVIS in 2025 |
| 同期 SOTA | SHiNe (Ren et al., 2025) | Best reported result on LVIS rare categories using hierarchy-aware text |
| 經典方法 | ViLD (Gu et al., 2022) | Seminal CLIP-based ZSD work; widely cited, establishes the region-CLIP paradigm |
| 經典方法 | OV-DETR (Zang et al., 2022) | Representative of the DETR-family open-vocabulary approach |
| 消融基準 | Ours w/o relation graph | Removes the core relational module to quantify its contribution |
| 消融基準 | Ours w/o curriculum loss | Replaces curriculum loss with standard contrastive loss |
| 消融基準 | Ours w/o both | Flat alignment baseline to measure combined contribution |

## Experiment List

### Experiment 1: Main Comparison on COCO ZSD Benchmark

- **Hypothesis:** If the relation graph module preserves spatial priors during alignment, then our method will achieve higher AP on novel categories than flat-alignment baselines (ViLD, CoDet), because relational context disambiguates visually similar novel objects.
- **Method:** Train on COCO 48 base categories, evaluate on 17 novel categories. Report AP50 and AR100 for novel categories. Use ResNet-50 and Swin-T backbones. All baselines retrained under identical settings (same detector backbone, training schedule, image resolution).
- **Expected Result:** +2.5-4.0 AP50 over CoDet on novel categories; competitive or slightly better on base categories.
- **Failure Mode:** If improvement is less than 1.0 AP50, the relational module does not provide meaningful benefit over existing CLIP alignment strategies.
- **Priority:** 必做

### Experiment 2: Main Comparison on LVIS Open-Vocabulary Benchmark

- **Hypothesis:** If curriculum-based alignment builds robust cross-modal representations, then our method will show larger gains on LVIS rare categories (which have the greatest semantic distance from frequent categories) than on common categories, because the curriculum explicitly trains for distant transfers.
- **Method:** Train on LVIS frequent + common categories, evaluate on all categories. Report AP_rare, AP_common, AP_frequent, and overall AP. Compare against SHiNe, EdaDet, and ViLD.
- **Expected Result:** +3.0-5.0 AP_rare over SHiNe; AP_frequent within 0.5 of best baseline.
- **Failure Mode:** If AP_rare improvement is comparable to AP_frequent improvement, the curriculum does not specifically help distant-category transfer, weakening the core narrative.
- **Priority:** 必做

### Experiment 3: Ablation Study - Component Contribution

- **Hypothesis:** If both the relation graph and curriculum loss are independently necessary, then removing either one will cause a measurable AP drop (at least 1.0 AP50), because each addresses a different aspect of the generalization problem (structural vs. training dynamics).
- **Method:** Evaluate four variants on COCO ZSD: (a) full method, (b) w/o relation graph, (c) w/o curriculum loss, (d) w/o both. Report AP50 on novel categories. Repeat 3 times with different seeds; report mean and standard deviation.
- **Expected Result:** Full > w/o curriculum (+1.5-2.5) > w/o graph (+1.0-2.0) > w/o both (+3.0-4.5). Contributions should be roughly additive.
- **Failure Mode:** If removing one component shows negligible drop (<0.5 AP50), that component is not pulling its weight and the corresponding contribution claim must be weakened or dropped.
- **Priority:** 必做

### Experiment 4: Distance-Stratified Evaluation

- **Hypothesis:** If our method specifically improves generalization to distant categories, then performance gains will be monotonically larger for categories at greater visual-semantic distance from training categories, because the relational and curriculum mechanisms target exactly this regime.
- **Method:** Compute visual-semantic distance for each novel category (cosine distance between CLIP text embedding and nearest base category embedding). Partition novel categories into 3 distance bins (near/mid/far). Report per-bin AP50 for our method vs. CoDet and ViLD.
- **Expected Result:** Near-bin: +0.5-1.5 AP50; Mid-bin: +2.0-3.5 AP50; Far-bin: +4.0-6.0 AP50.
- **Failure Mode:** If gains are uniform across bins or largest in the near-bin, the distance-aware generalization claim is not supported.
- **Priority:** 必做

### Experiment 5: Graph Architecture Variants

- **Hypothesis:** If spatial relations (not just semantic co-occurrence) matter, then a graph that uses only spatial edge features will outperform a graph using only semantic edge features, because spatial layout is the information most absent from CLIP's text-only category representations.
- **Method:** Compare three graph variants: (a) spatial-only edges, (b) semantic-only edges, (c) both (full model). Evaluate AP50 on COCO novel categories.
- **Expected Result:** Spatial-only > Semantic-only; Full model best overall. Gap between spatial-only and semantic-only is at least 1.0 AP50.
- **Failure Mode:** If semantic-only matches or exceeds spatial-only, the "spatial relational prior" framing needs revision.
- **Priority:** 建議做

### Experiment 6: Curriculum Schedule Sensitivity

- **Hypothesis:** If the curriculum is robust, then moderate variations in the distance schedule (linear vs. cosine vs. step annealing, and +/-20% epoch scaling) will produce performance within 1.0 AP50 of the optimal schedule, because the benefit comes from the progressive principle rather than the exact schedule shape.
- **Method:** Test 5 curriculum variants on COCO ZSD. Report AP50 on novel categories for each. Also report training-time overhead.
- **Expected Result:** All variants within 1.0 AP50 of each other; training overhead < 5% compared to standard contrastive.
- **Failure Mode:** If performance variance across schedules exceeds 2.0 AP50, the method is brittle and requires careful tuning, undermining practical value.
- **Priority:** 建議做

### Experiment 7: Cross-Dataset Transfer

- **Hypothesis:** If the learned relational representations are dataset-agnostic, then a model trained on COCO base categories and evaluated on Objects365 novel categories will retain its advantage over flat-alignment baselines, because relational priors are scene-level properties that transfer across annotation vocabularies.
- **Method:** Train on COCO base categories, evaluate zero-shot on 100 Objects365 categories not overlapping with COCO. Report AP50.
- **Expected Result:** Advantage over CoDet maintained (at least +1.5 AP50).
- **Failure Mode:** If the advantage disappears on cross-dataset evaluation, relational priors may be dataset-specific.
- **Priority:** 有時間再做

### Experiment 8: Qualitative Analysis and Error Taxonomy

- **Hypothesis:** If relational context helps disambiguation, then our method's correct detections on hard novel categories will show spatial-context-dependent reasoning (e.g., correctly detecting "skateboard" when "person" is nearby), while baseline errors will include misclassifications to visually similar base categories.
- **Method:** Sample 200 detection results from each distance bin. Manually categorize errors into: localization error, misclassification to base category, misclassification to another novel category, background false positive. Compare error distributions between our method and CoDet.
- **Expected Result:** Our method reduces "misclassification to base category" errors by 30-50% relative, particularly in the far-distance bin.
- **Failure Mode:** If error types shift rather than reduce (e.g., fewer misclassifications but more background FPs), the relational module may introduce different failure modes.
- **Priority:** 有時間再做
