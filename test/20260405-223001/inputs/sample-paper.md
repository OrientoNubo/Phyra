# InfiniteVGGT: Visual Geometry Grounded Transformer for Endless Streams

**Authors:** Shuai Yuan, Yantai Yang, Xiaotian Yang, Xupeng Zhang, Zhonghao Zhao, Lingming Zhang, Zhipeng Zhang
**Affiliation:** AutoLab, Shanghai Jiao Tong University
**arXiv:** 2601.02281 (January 2026)
**Code:** github.com/AutoLab-SAI-SJTU/InfiniteVGGT

## Abstract

The grand vision of enabling persistent, large-scale 3D visual geometry understanding is challenged by the irreconcilable demands of scalability and long-term stability. While offline models like VGGT achieve inspiring geometry capability, their batch-based nature renders them irrelevant for live systems. Streaming architectures, though the intended solution for live operation, have proven inadequate. Existing methods either fail to support truly infinite-horizon inputs or suffer from catastrophic drift over long sequences. We propose InfiniteVGGT, a causal visual geometry transformer that operationalizes the concept of a rolling memory through a bounded yet adaptive and perpetually expressive KV cache. Our method devises a training-free, attention-agnostic pruning strategy that intelligently discards obsolete information, effectively "rolling" the memory forward with each new frame. Our contributions include: (1) an unbounded memory architecture for continuous 3D geometry understanding, built on a novel, dynamic, and interpretable explicit memory system; (2) state-of-the-art performance on long-sequence benchmarks and a unique capability for robust, infinite-horizon reconstruction without memory overflow; and (3) the Long3D benchmark, a new dataset for the rigorous evaluation of long-term performance on sequences of approximately 10,000 frames.

## 1. Introduction

The ability to reconstruct persistent 3D geometry from continuous video streams is fundamental to autonomous systems, augmented reality, and embodied AI. Current approaches to 3D visual geometry understanding fall into two paradigms: offline batch methods that process fixed-length inputs with high quality but unbounded memory, and online streaming methods that operate causally but suffer from error accumulation and catastrophic drift over time.

VGGT (Wang et al., CVPR 2025 Best Paper) demonstrated that a single feed-forward transformer can predict camera parameters, depth maps, and point clouds from unposed images. However, VGGT processes a fixed batch of frames, making it unsuitable for live, continuous operation. StreamVGGT extended this to causal operation but faces a critical limitation: its KV cache grows linearly with sequence length, eventually exhausting GPU memory.

The core computational paradox is that optimized kernels like FlashAttention avoid materializing full O(N^2) attention matrices for efficiency, yet traditional pruning methods require accessing these attention weights to gauge token importance. This creates a fundamental tension: the tool required to manage the size of the cache prevents us from intelligently shrinking it.

We resolve this paradox with InfiniteVGGT, which introduces three integrated mechanisms: (1) an immutable anchor token that preserves the first-frame KV cache as a global coordinate reference, (2) diversity-aware token retention that uses cosine similarity in key space as an attention-independent proxy for importance, and (3) layer-wise adaptive budget allocation that distributes non-uniform storage across transformer layers based on measured information diversity.

## 2. Related Work

**3D Reconstruction from Images.** Classical multi-view stereo methods (Schonberger and Frahm, 2016) rely on explicit feature matching and bundle adjustment. Learning-based approaches have evolved from depth estimation networks (Eigen et al., 2014) to end-to-end geometry prediction. DUSt3R (Wang et al., 2024) introduced pointmap regression, while MASt3R (Leroy et al., 2024) added local feature matching. CUT3R (Wang et al., 2025) and Point3R (Xu et al., 2025) further extended this line. VGGT (Wang et al., CVPR 2025) unified camera, depth, and point cloud prediction in a single transformer.

**Streaming 3D Understanding.** Real-time SLAM systems (Mur-Artal et al., 2015; Teed and Deng, 2021) process frames incrementally but rely on hand-crafted pipelines. Recent learned streaming methods include TTT3R (Zhang et al., 2025), which uses test-time training to adapt to each sequence, and StreamVGGT, which extends VGGT with causal attention but lacks memory management.

**KV Cache Compression.** Efficient attention mechanisms have been studied extensively in NLP (Beltagy et al., 2020; Kitaev et al., 2020). For vision transformers, token pruning (Rao et al., 2021) and merging (Bolya et al., 2023) reduce computational cost. H2O (Zhang et al., 2023) and SnapKV (Li et al., 2024) prune KV caches in language models using attention-based importance scores. Our approach differs fundamentally: we use cosine similarity in key space rather than attention weights, maintaining compatibility with FlashAttention.

## 3. Method

### 3.1 Preliminaries: VGGT and StreamVGGT

VGGT takes N unposed images and predicts per-image camera extrinsics, depth maps, and 3D point maps through a vision transformer with alternating self-attention (within each image) and cross-attention (across images) layers. StreamVGGT extends VGGT to causal operation by maintaining a KV cache that accumulates tokens from all previously processed frames. However, this cache grows as O(T * P) where T is the number of frames and P is the number of patch tokens per frame, leading to unbounded memory consumption.

### 3.2 Diversity-Aware Rolling Memory

Given the KV cache K_t at time t after appending the new frame's tokens, we need to compress it to a fixed budget B while retaining the most informative tokens.

**Immutable Anchor Token.** We preserve the complete KV cache from the first frame as a permanent anchor. This is justified because VGGT establishes the first frame as the canonical coordinate system, and losing this reference causes coordinate drift.

**Diversity-Quantified Token Retention.** For each layer l and attention head h:

1. Compute the mean key vector: $\mu^{(l,h)} = \mathbb{E}[\hat{k} \in \hat{K}_{t,\text{cand}}^{(l,h)}][\hat{k}]$ where $\hat{k}$ denotes L2-normalized keys.

2. Calculate diversity score: $s_{\text{div}}^{(l,h)}(\hat{k}_i) = -\text{CosSim}(\mu^{(l,h)}, \hat{k}_i)$ using negative cosine similarity to identify the most dissimilar tokens.

3. Retain tokens with the highest diversity scores via TopK selection.

The key insight is that query tokens from the current frame assign near-identical attention weights to historically similar frames, making redundant tokens identifiable through key-space similarity without materializing attention matrices.

**Layer-wise Adaptive Budget Allocation.** Different transformer layers exhibit different information diversity patterns: shallow layers show high diversity (capturing subtle inter-frame differences), while early and deep layers show less diversity. We allocate non-uniform budgets:

$$p_{\text{bud}}^l = \frac{\exp(s_{\text{div}}^l / \tau)}{\sum_j \exp(s_{\text{div}}^j / \tau)}$$

where $\tau$ is a temperature hyperparameter. The per-layer budget is $B^l = p_{\text{bud}}^l \cdot B_{\text{total}}$, enforced via TopK selection.

### 3.3 Implementation Details

- Base model: StreamVGGT (pretrained VGGT with causal attention mask)
- Training-free modification: no fine-tuning required
- FlashAttention compatible: cosine similarity computation does not require full attention matrix
- Per-frame inference time remains constant regardless of sequence length
- Default total budget: B = 25,000 tokens per head
- Temperature: $\tau = 1.0$

## 4. Experiments

### 4.1 3D Reconstruction on Standard Benchmarks

**Datasets:** 7-Scenes (indoor, 300-500 frames with stride=2), NRGBD (diverse indoor scenes).

**Baselines:** CUT3R, TTT3R, Point3R, StreamVGGT.

**Table 1: 3D Reconstruction Results (7-Scenes and NRGBD)**

| Method | 7-Scenes Acc. (mean) | 7-Scenes Acc. (med) | NRGBD Acc. (mean) | NRGBD Acc. (med) | Comp. (mean) | Comp. (med) | NC (mean) | NC (med) |
|--------|---------------------|--------------------|--------------------|-------------------|-------------|------------|----------|---------|
| CUT3R | 0.058 | 0.025 | 0.112 | 0.078 | 0.031 | 0.008 | 0.541 | 0.573 |
| TTT3R | 0.062 | 0.027 | 0.165 | 0.098 | 0.028 | 0.006 | 0.553 | 0.582 |
| Point3R | 0.055 | 0.023 | 0.105 | 0.072 | 0.030 | 0.007 | 0.548 | 0.578 |
| StreamVGGT | 0.048 | 0.020 | 0.092 | 0.061 | 0.027 | 0.006 | 0.558 | 0.589 |
| **InfiniteVGGT** | **0.043** | **0.018** | **0.080** | **0.054** | **0.025** | **0.005** | **0.561** | **0.593** |

### 4.2 Long-Term Evaluation: Long3D Benchmark

**Table 2: Long3D Benchmark Results**

| Scene | Frames | CUT3R Acc. | TTT3R Acc. | InfiniteVGGT Acc. | InfiniteVGGT Comp. | InfiniteVGGT NC |
|-------|--------|-----------|-----------|-------------------|---------------------|-----------------|
| Classroom | 2,128 | 0.892 | 0.641 | **0.357** | 0.057 | 0.576 |
| Dormitory | 4,208 | 3.241 | 2.107 | **1.438** | 0.575 | 0.526 |
| Library | 4,726 | 2.985 | 1.893 | **1.121** | 0.571 | 0.508 |
| Badminton Court | 6,067 | 4.127 | 3.012 | **1.843** | 1.854 | 0.510 |
| Academic Building | 9,545 | OOM | 8.921 | **5.733** | 1.206 | 0.495 |

StreamVGGT fails on all Long3D sequences due to memory overflow. CUT3R encounters OOM on the longest sequence. InfiniteVGGT processes all sequences with bounded memory (14.49 GB peak).

### 4.3 Video Depth Estimation

**Table 3: Video Depth Estimation (Bonn Dataset, 500 frames)**

| Method | Abs Rel | $\delta < 1.25$ |
|--------|---------|-----------------|
| TTT3R | 0.076 | 0.953 |
| StreamVGGT | 0.072 | 0.956 |
| **InfiniteVGGT** | **0.069** | **0.960** |

### 4.4 Ablation Studies

**Table 4: Pruning Strategy Comparison**

| Strategy | CD | NC | Time (s/frame) | Memory (GB) |
|----------|-----|-----|----------------|-------------|
| Attention weights | 0.036 | 0.567 | 0.288 | 17.30 |
| **Cosine similarity** | **0.032** | **0.570** | **0.168** | **14.49** |

Cosine similarity reduces per-frame latency by 42% while improving reconstruction quality.

**Table 5: Effect of Initial Budget Per Head**

| Budget | CD (300 frames) | CD (500 frames) |
|--------|-----------------|-----------------|
| B = 10,000 | 0.062 | 0.075 |
| B = 15,000 | 0.045 | 0.052 |
| B = 20,000 | 0.036 | 0.038 |
| B = 25,000 | 0.032 | 0.033 |
| B = 30,000 | 0.031 | 0.032 |

Budget saturation occurs around B = 25,000 tokens per head.

**Table 6: Layer-wise Adaptive Allocation**

| Configuration | Acc. | Comp. | NC |
|--------------|------|-------|-----|
| Uniform allocation | 0.098 | 0.057 | 0.554 |
| **Layer-wise adaptive** | **0.093** | **0.056** | **0.555** |

**Table 7: Anchor Frame Necessity**

| Configuration | Acc. | NC |
|--------------|------|-----|
| Without anchor | 0.047 | 0.570 |
| **With anchor** | **0.040** | **0.570** |

Anchor preservation improves accuracy by 14.9% without affecting normal consistency.

## 5. Conclusion

We presented InfiniteVGGT, a causal visual geometry transformer that resolves the fundamental trade-off between offline quality and online scalability. Through an interpretable explicit memory system combining anchor preservation, diversity-aware token selection, and dynamic layer-wise budgeting, InfiniteVGGT enables practical infinite-horizon 3D reconstruction with bounded GPU memory (14.49 GB peak) while maintaining state-of-the-art quality. The Long3D benchmark provides a rigorous testbed for future work on long-term 3D geometry understanding. A limitation is that our method underperforms on the completion metric compared to some baselines, which we identify as an area for future optimization.

## References

[1] Schonberger, J.L. and Frahm, J.M. Structure-from-Motion Revisited. CVPR 2016.
[2] Eigen, D. et al. Depth Map Prediction from a Single Image using a Multi-Scale Deep Network. NeurIPS 2014.
[3] Wang, S. et al. DUSt3R: Geometric 3D Vision Made Easy. CVPR 2024.
[4] Leroy, V. et al. Grounding Image Matching in 3D with MASt3R. ECCV 2024.
[5] Wang, J. et al. VGGT: Visual Geometry Grounded Transformer. CVPR 2025 (Best Paper).
[6] Wang, J. et al. CUT3R: Causal Unposed Temporal 3D Reconstruction. 2025.
[7] Xu, H. et al. Point3R: Point Cloud 3D Reconstruction. 2025.
[8] Zhang, Y. et al. TTT3R: Test-Time Training for 3D Reconstruction. 2025.
[9] Mur-Artal, R. et al. ORB-SLAM: A Versatile and Accurate Monocular SLAM System. IEEE TRO 2015.
[10] Teed, Z. and Deng, J. DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras. NeurIPS 2021.
[11] Beltagy, I. et al. Longformer: The Long-Document Transformer. 2020.
[12] Kitaev, N. et al. Reformer: The Efficient Transformer. ICLR 2020.
[13] Rao, Y. et al. DynamicViT: Efficient Vision Transformers with Dynamic Token Sparsification. NeurIPS 2021.
[14] Bolya, D. et al. Token Merging: Your ViT But Faster. ICLR 2023.
[15] Zhang, Z. et al. H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models. NeurIPS 2023.
[16] Li, Y. et al. SnapKV: LLM Knows What You Are Looking for Before Generation. 2024.
[17] Belghazi, M.I. et al. Mutual Information Neural Estimation. ICML 2018.
