<!-- type: paper-survey-notes | generated: 2026-04-05 -->

## 1. Survey Task

| Item | Content |
|------|---------|
| Survey topic | Recent advances in vision-language models for zero-shot object detection, focusing on methods combining CLIP-based features with detection architectures |
| Trigger source | Text description |
| Survey date | 2026-04-05 |
| Search strategy | NT single-line |

## 2. Search Log

Five search sessions were conducted across Google Scholar, arXiv, Semantic Scholar, and CVPR/ECCV/ICCV proceedings. Primary search terms: "vision-language models zero-shot object detection CLIP," "open-vocabulary object detection CLIP features survey," "OWL-ViT GLIP Grounding DINO zero-shot detection," "YOLO-World DetCLIP RegionCLIP open-vocabulary detection," and "Grounding DINO 1.5 open-set detection." Approximately 50 total results were screened; 10 papers were selected based on direct relevance to CLIP-based detection architectures.

Search log path: `test-3-paper-survey/02-search-log.md`

## 3. Research List

| # | Paper / Research Name | Year | Type | Relationship to Survey Topic |
|---|----------------------|------|------|------------------------------|
| 1 | CLIP: Learning Transferable Visual Models From Natural Language Supervision | 2021 | Paper | Foundation model providing the contrastive image-text embedding space that all surveyed detectors build upon |
| 2 | RegionCLIP: Region-based Language-Image Pretraining | 2022 | Paper | First method to systematically extend CLIP from image-level to region-level representation for detection |
| 3 | OWL-ViT: Simple Open-Vocabulary Object Detection with Vision Transformers | 2022 | Paper | Established that minimal architectural additions to frozen CLIP ViT yield competent zero-shot detection |
| 4 | GLIP: Grounded Language-Image Pre-training | 2022 | Paper | Reformulated detection as phrase grounding with deep cross-modal fusion, enabling strong zero-shot transfer |
| 5 | DetCLIPv2: Scalable Open-Vocabulary Object Detection Pre-training via Word-Region Alignment | 2023 | Paper | Demonstrated that scaling region-text pretraining data and using word-level alignment improves novel-category generalization |
| 6 | Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection | 2024 | Paper | Combined DINO transformer with GLIP grounding for three-stage cross-modal fusion; became one of the most adopted zero-shot detectors |
| 7 | YOLO-World: Real-Time Open-Vocabulary Object Detection | 2024 | Paper | Achieved real-time OVD (52 FPS, 35.4 AP on LVIS) by embedding CLIP features into YOLO via RepVL-PAN |
| 8 | CLIFF: Continual Latent Diffusion for Open-Vocabulary Object Detection | 2024 | Paper | Proposed a generative diffusion-based paradigm for OVD, representing an alternative to discriminative approaches |
| 9 | Grounding DINO 1.5: Advance the Edge of Open-Set Object Detection | 2024 | Paper | Scaled Grounding DINO to 20M+ images with Pro (accuracy) and Edge (deployment) variants |
| 10 | A Survey on Open-Vocabulary Detection and Segmentation: Past, Present, and Future | 2024 | Paper | Comprehensive T-PAMI survey covering the full landscape of open-vocabulary detection methods |

## 4. Relationship Analysis

### 4.1 Relationship Table

| Research A | Research B | Relationship | Direction | Basis |
|-----------|-----------|-------------|-----------|-------|
| CLIP | RegionCLIP | builds-on | A->B | Extends image-level contrastive alignment to region-level representations |
| CLIP | OWL-ViT | builds-on | A->B | Attaches detection heads onto frozen CLIP ViT backbone |
| CLIP | GLIP | builds-on | A->B | Uses CLIP-style contrastive pretraining reformulated as phrase grounding |
| RegionCLIP | DetCLIPv2 | builds-on | A->B | Scales region-text alignment to 13M images with word-level granularity |
| GLIP | Grounding DINO | builds-on | A->B | Replaces Dynamic Head with DINO transformer for deeper cross-modal fusion |
| DetCLIPv2 | YOLO-World | builds-on | A->B | Adopts region-text contrastive objectives within real-time YOLO architecture |
| Grounding DINO | Grounding DINO 1.5 | supersedes | A->B | Surpasses original on all major benchmarks with scaled data and architecture |
| OWL-ViT | GLIP | parallel | -- | Both 2022; late-fusion vs. deep-fusion design philosophies |
| OWL-ViT | RegionCLIP | parallel | -- | Both 2022; detection heads vs. region-level fine-tuning |
| YOLO-World | Grounding DINO | parallel | -- | Both 2024; speed-optimized vs. accuracy-optimized OVD |
| CLIFF | Grounding DINO | parallel | -- | Generative vs. discriminative paradigms; both ECCV 2024 |

### 4.2 Cluster Grouping

**Cluster A: Region-level CLIP adaptation.** RegionCLIP and DetCLIPv2 share the core idea of bridging CLIP's image-level representations to region-level by training on region-text pairs. The consensus is that explicit region-text alignment is necessary; the divergence is on scale (RegionCLIP uses moderate data, DetCLIPv2 scales to 13M images) and granularity (phrase-level vs. word-level).

**Cluster B: Grounding-based detection.** GLIP, Grounding DINO, and Grounding DINO 1.5 form a lineage that treats detection as language grounding. The consensus is that deep cross-modal fusion (not just late-stage classification) is critical for strong zero-shot performance. The progression from GLIP to Grounding DINO shows that replacing CNN-based necks with transformer decoders improves fusion quality.

**Cluster C: Real-time open-vocabulary detection.** OWL-ViT and YOLO-World both prioritize inference efficiency, though from different starting points (ViT vs. YOLO). The key trade-off is that minimal architectural modifications preserve speed but limit the depth of vision-language interaction.

**Cluster D: Alternative paradigms.** CLIFF represents an emerging generative approach to OVD. It is currently a single data point, but its use of latent diffusion for distribution transfer suggests a potential direction away from purely discriminative methods.

## 5. Development Narrative

The field of vision-language zero-shot detection originates from CLIP (2021), which proved that contrastive pretraining on 400 million web image-text pairs creates an embedding space sufficient for zero-shot image recognition. The immediate limitation was granularity: CLIP aligns whole images with text, but detection requires region-level localization. The 2022 cohort attacked this gap through three parallel strategies. RegionCLIP fine-tuned CLIP on RPN-generated region-text pairs. OWL-ViT attached lightweight detection heads to a frozen CLIP ViT. GLIP reformulated detection as phrase grounding with deep cross-modal fusion. These three approaches established the fundamental design axes of the field: how much of CLIP to keep frozen, where to inject language information, and whether to treat detection as classification or grounding.

From 2023 to 2024, these threads matured. DetCLIPv2 validated that the region-text alignment paradigm scales with data. Grounding DINO merged GLIP's grounding formulation with the DINO transformer detector, achieving three-stage fusion that proved effective enough to become one of the most widely used zero-shot detectors. Grounding DINO 1.5 further scaled the approach and introduced an edge variant. YOLO-World addressed the speed gap, achieving 52 FPS at 35.4 AP on LVIS by re-parameterizing CLIP text embeddings into the YOLO network. CLIFF opened a generative direction using latent diffusion for open-vocabulary detection.

The current state of the field shows no single dominant paradigm. Discriminative grounding (Grounding DINO family), contrastive region alignment (RegionCLIP / DetCLIPv2 lineage), architectural re-parameterization (YOLO-World), and generative modeling (CLIFF) each offer distinct trade-offs. The primary unresolved tension is between depth of vision-language fusion (which improves accuracy on rare and novel categories) and inference speed (which determines practical deployability).

## 6. Open Gaps

- Real-time performance with deep fusion: Grounding DINO achieves strong accuracy through deep cross-modal fusion but runs below 5 FPS; YOLO-World achieves real-time speed with shallower fusion. No current method achieves both simultaneously.
- Long-tail and rare category detection: Even Grounding DINO 1.5, trained on 20M+ images, shows degraded performance on LVIS-rare categories compared to LVIS-common. The gap between common and rare category performance remains substantial.
- Continual / incremental learning: Most methods require retraining to incorporate new vocabulary or domains. CLIFF's generative approach hints at continual adaptation, but this direction remains underexplored.
- Robustness under distribution shift: Limited work examines how these VLM-based detectors perform under domain shift (weather, lighting, sensor type). One study (arXiv 2405.14874) raised this question but the area lacks systematic evaluation.
- Unified detection and segmentation: Most surveyed methods produce bounding boxes only. Extending zero-shot VLM detection to instance segmentation without separate segmentation heads remains an open architectural challenge.

## 7. Survey Conclusion

This survey covered the core trajectory from CLIP (2021) through the 2024 state of the art across four methodological clusters: region-level CLIP adaptation, grounding-based detection, real-time open-vocabulary detection, and generative paradigms. The coverage is strong for discriminative methods published at top venues (CVPR, ECCV, ICML, T-PAMI) from 2021-2024. Potential gaps include: (1) methods from the robotics and embodied AI communities that apply VLM detectors in closed-loop settings; (2) very recent 2025 preprints that may have emerged after the search window; (3) industry-specific applications (autonomous driving, medical imaging) where VLM-based detection is being adapted with domain-specific modifications. For next steps, a deeper investigation into the speed-accuracy Pareto frontier and rare-category performance would be the most productive directions.
