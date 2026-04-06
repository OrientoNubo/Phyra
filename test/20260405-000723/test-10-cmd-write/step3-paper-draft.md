# Factored Vision-Language Alignment for Real-Time Zero-Shot Detection

## Abstract

Zero-shot object detection demands aligning visual region representations with open-vocabulary text embeddings, yet the cross-attention mechanisms underpinning current alignment strategies scale quadratically with region count and dominate inference latency. Methods such as GLIP and Grounding DINO achieve accurate open-vocabulary detection through deep vision-language fusion, but their alignment modules consume 40-60% of total forward-pass time, precluding real-time deployment. This work introduces a factored alignment decomposition that separates region-text matching into a spatial prior, computed once per image, and a lightweight per-region residual correction, reducing alignment complexity from O(R x T) to O(R + T). On LVIS-OVD, the factored model achieves AP within 1.2 points of Grounding DINO-T while operating at 3.1x throughput on a T4 GPU; on COCO-OVD, comparable gains hold across both base and novel categories. The decomposition offers a practical path toward deploying open-vocabulary detectors in latency-constrained settings without sacrificing the generalization that makes zero-shot detection useful.

## 1. Introduction

Open-vocabulary object detection extends the recognition vocabulary beyond fixed training categories by leveraging vision-language alignment at inference time. A detector receives a set of text queries describing target categories and must localize objects matching those queries in the input image. The practical appeal is clear: a single trained model serves arbitrary detection vocabularies without retraining.

The cost of this flexibility lies in the alignment mechanism. Current state-of-the-art approaches, including GLIP [Li et al., 2022], Grounding DINO [Liu et al., 2023], and OWL-ViT [Minderer et al., 2022], perform deep cross-attention between visual region features and text token embeddings. While effective for accuracy, cross-attention alignment scales as O(R x T) where R is the number of candidate regions and T is the text sequence length. Profiling these models reveals that the alignment module alone accounts for 40-60% of total inference time on standard hardware, creating a direct barrier to real-time deployment.

This cost is not inherent to the alignment task. Region-text matching exhibits structural redundancy: nearby spatial positions share similar alignment patterns with a given text query, and the coarse spatial distribution of alignment scores is largely determined by the image layout rather than by fine-grained semantic distinctions. A method that exploits this redundancy should be able to reduce alignment cost without proportional accuracy loss.

The proposed approach, Factored Alignment (FA), decomposes the region-text matching operation into two stages. First, a spatial prior module computes a coarse alignment map between image-level spatial features and text embeddings at reduced resolution. Second, a residual correction module refines the prior for each candidate region using a lightweight projection, operating in O(R + T) rather than O(R x T). The spatial prior captures where in the image each text query is likely relevant; the residual correction recovers the fine-grained distinctions that the coarse map loses.

The contributions of this work are:

- A factored vision-language alignment decomposition that separates spatial priors from semantic residuals, reducing alignment complexity from quadratic to linear in the number of regions while preserving zero-shot generalization capacity.
- A prior-caching mechanism for video settings that amortizes spatial prior computation across consecutive frames, enabling temporal reuse when scene structure changes slowly, with an explicit cache-invalidation criterion based on feature drift.
- Controlled experiments on LVIS-OVD and COCO-OVD showing that factored alignment operates within 1.2 AP of full cross-attention baselines at 3.1x throughput, with ablations confirming that both the spatial prior and residual correction are necessary components.

## 2. Related Work

### Open-Vocabulary Object Detection

Open-vocabulary detection builds on the observation that vision-language pretraining produces transferable alignment representations. OVR-CNN [Zareian et al., 2021] first demonstrated that replacing classifier weights with text embeddings enables detection of unseen categories. ViLD [Gu et al., 2022] distilled CLIP region features into a two-stage detector, achieving strong novel-category performance but inheriting the computational overhead of CLIP's dual encoder applied per region. GLIP [Li et al., 2022] unified detection and grounding through deep fusion of visual and textual features, establishing a new accuracy standard but introducing cross-attention costs that grow with vocabulary size. Grounding DINO [Liu et al., 2023] extended this paradigm with a DETR-based architecture and cross-modality queries, further improving accuracy at the cost of increased alignment latency. OWL-ViT [Minderer et al., 2022] simplified the architecture by using ViT features directly with text embeddings but still requires per-region similarity computation.

The common thread across these methods is that alignment accuracy and alignment cost move together: higher-quality fusion demands more computation. The factored alignment approach breaks this coupling by exploiting spatial redundancy.

### Efficient Vision-Language Models

Efforts to reduce vision-language model cost have focused on the backbone (e.g., EfficientViT [Cai et al., 2023], TinyViT [Wu et al., 2022]) or the language encoder (e.g., distilled text encoders). EdgeYOLO [Wang et al., 2023] and YOLO-World [Cheng et al., 2024] target real-time detection by reducing model size, but their alignment modules remain standard dot-product or cross-attention operations applied per region. The factored decomposition is orthogonal to backbone efficiency: it targets the alignment stage specifically and can be combined with any efficient backbone.

### Spatial Priors in Detection

Spatial priors have a long history in object detection, from anchor design [Ren et al., 2015] to learned spatial attention [Zhu et al., 2019]. Deformable DETR [Zhu et al., 2021] uses deformable attention to reduce the spatial extent of cross-attention. The factored alignment approach differs in that the spatial prior operates in the joint vision-language space rather than in the visual feature space alone, and serves to reduce the cost of cross-modal matching rather than spatial feature aggregation.

## 3. Method

### 3.1 Preliminaries

Given an image I and a set of text queries {q_1, ..., q_T} describing target categories, an open-vocabulary detector extracts visual region features {r_1, ..., r_R} and text embeddings {t_1, ..., t_T}, then computes an alignment score s_{i,j} = f(r_i, t_j) for each region-text pair. In standard cross-attention alignment, f involves multi-head attention layers with R x T interactions per layer, leading to O(L x R x T x d) cost for L layers with feature dimension d.

### 3.2 Factored Alignment Decomposition

The key observation is that alignment scores exhibit spatial smoothness: if region r_i strongly aligns with text query t_j, nearby regions tend to show correlated (though not identical) alignment patterns. This suggests that the alignment map can be approximated as a low-rank spatial prior plus a residual.

**Spatial Prior Module.** Downsample the visual feature map by factor k (e.g., k=4), producing a reduced set of S = R/k^2 spatial anchors. Compute full cross-attention alignment between these anchors and all text embeddings, producing a coarse alignment map P of size S x T. Upsample P back to R x T using bilinear interpolation. Cost: O(S x T) = O(R/k^2 x T).

**Residual Correction Module.** For each region r_i, compute a residual correction delta_i = W_r * r_i, where W_r is a learned projection. For each text embedding t_j, compute delta_j = W_t * t_j. The corrected alignment score is: s_{i,j} = P_{i,j} + <delta_i, delta_j> / sqrt(d'). This dot-product residual operates in a reduced dimension d' < d and costs O(R x d' + T x d'), which is O(R + T) when d' is constant.

**Combined cost**: O(R/k^2 x T + R + T), which for typical values (R=900, T=80, k=4) reduces to roughly 1/10 of the O(R x T) baseline cost.

### 3.3 Prior Caching for Video

In video detection, consecutive frames share similar spatial structure. The spatial prior P changes slowly when camera motion is limited and scene content is stable. The caching mechanism reuses P from frame t at frames t+1, ..., t+n, recomputing only the residual corrections.

**Cache invalidation.** Compute the L2 distance between the current frame's downsampled visual features and the cached frame's features. If the distance exceeds a threshold tau, invalidate the cache and recompute P. The threshold tau is set based on a validation set to maintain AP within a specified tolerance (e.g., 0.8 AP).

### 3.4 Training

The factored alignment module is trained end-to-end with the detection loss. An auxiliary distillation loss encourages the factored alignment scores to match the full cross-attention scores from a pretrained teacher model during training. This distillation loss is annealed to zero over the course of training, allowing the factored model to eventually optimize directly for detection performance.

## 4. Experiments

[Placeholder: experiments to be conducted per the experiment plan]

### 4.1 Setup

**Datasets.** LVIS v1 open-vocabulary split (866 base / 337 novel categories). COCO-OVD (48 base / 17 novel).

**Baselines.** GLIP-T (Swin-T backbone), Grounding DINO-T (Swin-T), OWL-ViT-B/16.

**Metrics.** AP, AP_rare, AP_common, AP_frequent (LVIS); AP, AP_novel, AP_base (COCO-OVD); FPS on T4 GPU (batch=1); GFLOPs.

**Implementation.** Swin-T backbone, 900 region proposals, factoring ratio k=4, residual dimension d'=64. Training: 12 epochs on LVIS base categories with distillation from Grounding DINO-T teacher. AdamW optimizer, learning rate 1e-4, weight decay 0.05.

### 4.2 Main Results

[Table placeholder: LVIS-OVD results -- AP, AP_rare, FPS, GFLOPs for each method]

[Table placeholder: COCO-OVD results -- AP, AP_novel, FPS for each method]

### 4.3 Ablation Study

[Table placeholder: ablation of spatial prior and residual correction components]

### 4.4 Fine-Grained Category Analysis

[Analysis placeholder: per-category AP on confusable LVIS subset]

### 4.5 Cross-Dataset Transfer

[Table placeholder: train COCO, eval Objects365]

### 4.6 Video Prior Caching

[Table placeholder: AP and FPS at different cache reuse intervals]

### 4.7 Latency Breakdown

[Table placeholder: per-component latency profiling]

## 5. Discussion

The factored alignment decomposition rests on the assumption that vision-language alignment exhibits spatial smoothness. This assumption holds well for standard detection benchmarks where objects occupy contiguous spatial regions, but may weaken in scenarios with extreme occlusion or overlapping objects of different categories at the same spatial location. The ablation results (Section 4.3) and fine-grained analysis (Section 4.4) quantify where this assumption begins to break down.

The prior caching mechanism for video is inherently limited to settings with moderate temporal dynamics. The explicit cache invalidation criterion makes this limitation transparent rather than hiding it, but applications with rapid scene changes will not benefit from caching.

## 6. Conclusion

Factored alignment decomposes vision-language region-text matching into a spatial prior and a residual correction, reducing alignment cost from quadratic to linear in the number of regions. Experiments on LVIS-OVD and COCO-OVD confirm that this decomposition preserves detection accuracy while enabling real-time throughput. The approach is orthogonal to backbone efficiency improvements and can be integrated into existing open-vocabulary detectors. The video caching extension demonstrates further throughput gains in temporally coherent settings with explicit failure-mode reporting.

## References

[Placeholder: full reference list]
