# Survey Notes: Zero-Shot Object Detection with Vision-Language Models

**Search Date:** 2026-04-04
**Query:** zero-shot object detection with vision-language models
**Workflow:** NT (Normal Turbo)

## Search Log

| Database | Search Terms | Results Found | Selected |
|----------|-------------|---------------|----------|
| arXiv | zero-shot object detection vision-language models 2024 2025 | ~10 | 5 |
| Google Scholar / ScienceDirect | open-vocabulary object detection CLIP grounding DINO survey | ~10 | 4 |
| Semantic Scholar | zero-shot object detection recent papers | ~10 | 3 |
| arXiv / HuggingFace | OWL-ViT OWLv2 open-world object detection | ~10 | 2 |
| arXiv / GitHub | YOLO-World real-time open-vocabulary object detection | ~10 | 2 |

**Total unique papers selected:** 12

## Paper List with Annotations

### Foundational / Seminal Works

1. **CLIP: Learning Transferable Visual Models From Natural Language Supervision**
   - Authors: Radford et al.
   - Venue: ICML 2021
   - Relevance: Foundational vision-language model that enables zero-shot transfer to downstream tasks including detection. Nearly all subsequent open-vocabulary detectors build on CLIP's contrastive image-text pretraining paradigm.

2. **Zero-Shot Object Detection** (Bansal et al.)
   - Venue: ECCV 2018
   - Relevance: Early formulation of the zero-shot detection problem, establishing the task definition of detecting object categories unseen during training by leveraging semantic embeddings.

3. **Zero-Shot Object Detection: Learning to Simultaneously Recognize and Localize Novel Concepts** (Rahman, Khan, Porikli)
   - Venue: arXiv 2018
   - Relevance: Extended the ZSD framework to jointly handle recognition and localization of novel categories, setting the stage for later VLM-based approaches.

### Core Methods (Vision-Language Detection)

4. **Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection**
   - Authors: Liu et al. (IDEA Research)
   - Venue: ECCV 2024
   - Relevance: Achieves 52.5 AP on COCO zero-shot detection by fusing a Transformer-based detector (DINO) with language grounding. Proposes tight fusion via feature enhancer, language-guided query selection, and cross-modality decoder. Sets a new record on ODinW zero-shot benchmark (mean 26.1 AP).

5. **OWL-ViT: Simple Open-Vocabulary Object Detection with Vision Transformers** (Minderer et al., Google)
   - Venue: ECCV 2022
   - Relevance: Demonstrated that a simple architecture (ViT + CLIP backbone + lightweight detection head) can perform competitive open-vocabulary detection. Key insight: standard vision-language pretraining transfers well to detection with minimal architectural changes.

6. **OWLv2: Scaling Open-Vocabulary Object Detection** (Minderer, Gritsenko, Houlsby)
   - Venue: NeurIPS 2023
   - Relevance: Scaled OWL-ViT via self-training on web-scale data (1B+ examples). Improved AP on LVIS rare classes from 31.2% to 44.6% (43% relative improvement). Introduced objectness classifier for better filtering.

7. **YOLO-World: Real-Time Open-Vocabulary Object Detection** (Cheng et al.)
   - Venue: CVPR 2024
   - Relevance: Brought open-vocabulary detection to real-time speeds. Proposes RepVL-PAN for vision-language feature aggregation. Achieves 35.4 AP with 52.0 FPS on V100 on LVIS. Introduces prompt-then-detect paradigm with offline vocabulary encoding.

8. **GLIP: Grounded Language-Image Pre-training** (Li et al.)
   - Venue: CVPR 2022
   - Relevance: Reformulated object detection as phrase grounding, enabling contrastive training between object regions and language phrases. Foundation for Grounding DINO's approach.

### Incremental and Adaptive Approaches

9. **ZiRa: Zero-shot Generalizable Incremental Learning for Vision-Language Object Detection**
   - Venue: NeurIPS 2024
   - Relevance: Addresses incremental adaptation of VLODMs to specialized domains while preserving zero-shot generalization. Boosts zero-shot AP by 13.91 and 8.74 over CL-DETR and iDETR respectively.

10. **Revisiting Few-Shot Object Detection with Vision-Language Models**
    - Venue: OpenReview / arXiv 2023-2024
    - Relevance: Found that zero-shot VLM predictions (e.g., GroundingDINO) significantly outperform SOTA few-shot detectors (48 vs 33 AP on COCO), questioning the need for few-shot detection as a separate paradigm.

### Surveys and Overviews

11. **Vision-Language Model for Object Detection and Segmentation: A Review and Evaluation** (April 2025)
    - Venue: arXiv
    - Relevance: Comprehensive systematic review evaluating VLMs across eight detection and eight segmentation scenarios. Reveals distinct performance advantages and limitations of various VLM architectures.

12. **A Survey of Zero-Shot Object Detection** (SciOpen, 2024)
    - Relevance: Dedicated survey of ZSD methods, covering the evolution from semantic-embedding-based approaches to modern VLM-based methods. Identifies key challenges: seen-class bias and feature transferability.

## Relationship Analysis

### Methodological Lineage

The field has evolved through three generations:

**Generation 1 (2018-2020): Semantic Embedding Methods.** Early ZSD methods (Bansal et al., Rahman et al.) used word embeddings (Word2Vec, GloVe) to bridge seen and unseen categories. These suffered from domain gap between visual features and semantic spaces.

**Generation 2 (2021-2022): CLIP-based Transfer.** CLIP's contrastive pretraining on 400M image-text pairs created a shared vision-language embedding space. OWL-ViT showed this transfers directly to detection. GLIP demonstrated phrase grounding as an alternative formulation.

**Generation 3 (2023-present): Scaled Grounded Detection.** Grounding DINO, OWLv2, and YOLO-World represent the current frontier, each with a distinct trade-off: Grounding DINO prioritizes accuracy through tight multi-modal fusion; OWLv2 achieves scale through self-training; YOLO-World optimizes for real-time inference.

### Key Clusters

- **CLIP Descendants:** OWL-ViT, OWLv2 (direct CLIP backbone usage)
- **Grounding Paradigm:** GLIP, Grounding DINO (detection as phrase grounding)
- **Efficiency-Oriented:** YOLO-World (real-time inference, offline vocabulary)
- **Continual Learning:** ZiRa (preserving zero-shot ability during specialization)

### Identified Gaps

1. **Domain-Specific Evaluation:** Most benchmarks use COCO and LVIS. Evaluation on specialized domains (medical, satellite, industrial) remains sparse.
2. **Small Object Detection:** Zero-shot detection of small objects is poorly addressed; most VLMs struggle at low resolutions.
3. **Compositional Queries:** Detecting objects described by compositional attributes ("the red car next to the building") remains challenging.
4. **Temporal Consistency:** Applying zero-shot detection to video with temporal consistency is underexplored.
5. **Efficiency on Edge Devices:** Only YOLO-World targets real-time performance; deployment on mobile/edge hardware is an open problem.

## Suggested Next Reads

- **Grounding DINO 1.5** (if available): Expected improvements to the Grounding DINO architecture
- **YOLOE: Real-Time Seeing Anything** (Ultralytics): Next-generation open-vocabulary YOLO variant
- **DetCLIPv3**: Advancing open-vocabulary detection with more sophisticated prompt engineering
- Papers on **open-vocabulary 3D object detection**, which extends ZSD to point clouds
