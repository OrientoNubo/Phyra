<!-- type: paper-graph-notes | generated: 2026-04-05 -->

## 1. Graph Task

| Item | Content |
|------|---------|
| Input paper count | 5 |
| Input source | Title list |
| Analysis date | 2026-04-05 |
| Analysis strategy | NT sequential |

## 2. Paper List

| # | Paper | Year | First Author | Venue |
|---|-------|------|-------------|-------|
| 1 | VGGT: Visual Geometry Grounded Transformer | 2025 | Wang | CVPR 2025 |
| 2 | InfiniteVGGT: Visual Geometry Grounded Transformer for Endless Streams | 2026 | Yuan | arXiv 2026 |
| 3 | DUSt3R: Geometric 3D Vision Made Easy | 2024 | Wang | CVPR 2024 |
| 4 | MASt3R: Grounding Image Matching in 3D | 2024 | Leroy | ECCV 2024 |
| 5 | CUT3R: Causal Unposed Temporal 3D Reconstruction | 2025 | Wang | arXiv 2025 |

## 3. Relationship Matrix

| Paper A | Paper B | Type | Direction | Basis |
|---------|---------|------|-----------|-------|
| DUSt3R | MASt3R | builds-on | A->B | MASt3R extends DUSt3R's pointmap regression with 3D-grounded feature matching |
| DUSt3R | VGGT | builds-on | A->B | VGGT generalizes DUSt3R's pointmap paradigm from pairs to multi-image collections |
| VGGT | CUT3R | builds-on | A->B | CUT3R adapts VGGT's architecture for causal autoregressive processing |
| VGGT | InfiniteVGGT | builds-on | A->B | InfiniteVGGT extends VGGT with rolling memory and KV cache pruning for streaming |
| MASt3R | VGGT | parallel | A<->B | Both extend DUSt3R with different goals: matching (MASt3R) vs. full geometry (VGGT) |
| InfiniteVGGT | CUT3R | supersedes | A->B | InfiniteVGGT removes CUT3R's fixed context limitation while achieving better accuracy |

## 4. Cluster Analysis

### 4.1 Cluster Results

| Cluster | Papers | Core Characteristic |
|---------|--------|-------------------|
| Pointmap Regression | DUSt3R, VGGT | Dense 3D pointmap prediction as unified representation replacing classical multi-stage pipelines |
| Geometry Transformer | VGGT, CUT3R, InfiniteVGGT | Transformer architectures that jointly predict multiple geometric quantities in a single forward pass |
| Feature Matching | MASt3R | Explicit 3D-grounded correspondence extraction for localization and matching tasks |
| Causal/Streaming | CUT3R, InfiniteVGGT | Sequential frame processing without requiring access to future observations |

### 4.2 Inter-Cluster Relationships

The Pointmap Regression cluster provides the foundational representation that all other clusters build upon. DUSt3R's core insight, that dense 3D pointmaps can be regressed directly from image pairs, is the substrate for both the Geometry Transformer and Feature Matching clusters. The Geometry Transformer cluster extends this to multi-image joint reasoning, while the Feature Matching cluster (MASt3R) enriches the pointmap framework with explicit correspondences. The Causal/Streaming cluster emerged specifically to address the batch-processing assumption in the Geometry Transformer cluster, converting joint reasoning into sequential processing.

## 5. Timeline

**2024-01 (CVPR 2024):** DUSt3R introduces pointmap regression, demonstrating that a ViT encoder-decoder can replace the classical detect-match-triangulate pipeline for 3D reconstruction from image pairs. This removes the need for handcrafted feature extractors and explicit geometric solvers.

**2024-07 (ECCV 2024):** MASt3R builds on DUSt3R by adding 3D-aware feature descriptors alongside pointmaps. The motivation is that DUSt3R lacks explicit correspondences, which are required for downstream tasks such as visual localization and SfM. MASt3R addresses this by grounding feature matching in the 3D coordinate frame predicted by the pointmap decoder.

**2025-01 (CVPR 2025):** VGGT scales the pointmap paradigm from pairwise to multi-image processing. DUSt3R's pairwise formulation requires quadratic global alignment for multi-view reconstruction. VGGT replaces this with a single feed-forward transformer that processes all images jointly, predicting cameras, depth, pointmaps, and 3D tracks in one pass.

**2025 (arXiv 2025):** CUT3R adapts VGGT for causal temporal processing. VGGT's requirement that all frames be available at once prevents real-time applications. CUT3R introduces autoregressive processing with a fixed context window, enabling frame-by-frame reconstruction at the cost of bounded context length.

**2026 (arXiv 2026):** InfiniteVGGT resolves CUT3R's fixed context limitation by introducing rolling memory with geometric importance-based KV cache pruning. This allows streaming reconstruction over unbounded sequences while retaining information from the full history, achieving both the scalability of streaming and the accuracy benefits of long-range context.

## 6. Hub Node Analysis

**DUSt3R** is the primary hub node in this graph. All four other papers either directly build on DUSt3R (MASt3R, VGGT) or transitively depend on it through VGGT (CUT3R, InfiniteVGGT). DUSt3R's hub status derives from its foundational contribution: by demonstrating that pointmap regression is a viable replacement for the classical reconstruction pipeline, it established the representation and training paradigm that the entire subsequent lineage adopts. Without DUSt3R's pointmap formulation, neither VGGT's multi-image extension nor MASt3R's 3D-grounded matching would have their current form.

**VGGT** serves as a secondary hub, mediating between the foundational work and the streaming/causal extensions. Both CUT3R and InfiniteVGGT build directly on VGGT's architecture, adapting its multi-image transformer for sequential processing.

## 7. Graph Conclusions

The mainstream research direction in this graph is the progression from batch-mode geometry prediction toward streaming and causal inference. The five papers trace a clear line: DUSt3R establishes the representation, VGGT scales it, and CUT3R/InfiniteVGGT temporalize it. MASt3R represents a parallel branch that prioritizes explicit correspondences over holistic geometry prediction; its relationship to the main line is complementary rather than competitive.

The primary open problem is memory-efficient long-range context management for streaming 3D reconstruction. While InfiniteVGGT addresses this through KV cache pruning, the trade-off between compression ratio and reconstruction quality remains an active question. A secondary open problem is unifying the feature matching branch (MASt3R) with the streaming branch (InfiniteVGGT), since current streaming methods do not produce explicit correspondences that downstream localization systems require.
