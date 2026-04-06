## Query Analysis

**Original query:** Recent advances in vision-language models for zero-shot object detection, focusing on methods that combine CLIP-based features with detection architectures

### Extracted Keywords

**Primary keywords:**
- vision-language models (VLM)
- zero-shot object detection
- CLIP
- open-vocabulary detection

**Secondary keywords:**
- feature alignment (region-level vs. image-level)
- grounding / phrase grounding
- contrastive learning
- detection architecture (transformer-based, YOLO-based)
- cross-modality fusion

**Synonym / community-variant terms:**
- "open-vocabulary detection" = "open-set detection" = "zero-shot detection" (overlapping but not identical; open-vocabulary is the broader term)
- "grounding" in NLP community vs. "open-vocabulary detection" in CV community address similar problems

### Scope

| Dimension | Constraint |
|-----------|-----------|
| Time range | 2021-2025 (CLIP published Jan 2021; field emerged since) |
| Task focus | 2D object detection (exclude segmentation-only, 3D, video unless directly relevant) |
| Method focus | Methods that explicitly leverage CLIP or CLIP-style contrastive VLM features within a detection pipeline |
| Venue preference | Top-tier CV/ML venues (CVPR, ECCV, ICCV, NeurIPS, ICLR, AAAI, T-PAMI) and arXiv preprints with significant impact |
| Exclusion | Pure image classification, pure text grounding without detection boxes, anomaly detection |

### Search Strategy (NT single-line)

Execute keyword forward-search across arXiv, Semantic Scholar, Google Scholar. After identifying 2-3 anchor papers (Grounding DINO, YOLO-World, OWL-ViT), trace backward and forward citations to fill gaps.
