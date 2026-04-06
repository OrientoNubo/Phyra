<!-- type: paper-graph-notes | generated: 2026-04-06 -->

## 1. Graph Task

| Item | Content |
|------|---------|
| Papers analyzed | 5 |
| Input source | Title list (paper-list.txt) |
| Analysis date | 2026-04-06 |
| Analysis strategy | NT sequential |

## 2. Paper List

| # | Paper | Year | First Author | Venue |
|---|-------|------|-------------|-------|
| 1 | DUSt3R: Geometric 3D Vision Made Easy | 2024 | Wang | CVPR 2024 |
| 2 | MASt3R: Grounding Image Matching in 3D | 2024 | Leroy | ECCV 2024 |
| 3 | VGGT: Visual Geometry Grounded Transformer | 2025 | Wang | CVPR 2025 |
| 4 | CUT3R: Causal Unposed Temporal 3D Reconstruction | 2025 | Wang | arXiv 2025 |
| 5 | InfiniteVGGT: Visual Geometry Grounded Transformer for Endless Streams | 2026 | Yuan | arXiv 2026 |

## 3. Relationship Matrix

| Paper A | Paper B | Type | Direction | Basis |
|---------|---------|------|-----------|-------|
| DUSt3R | MASt3R | builds-on | A -> B | MASt3R extends DUSt3R's pointmap regression with local feature matching for improved dense correspondence. |
| DUSt3R | VGGT | builds-on | A -> B | VGGT generalizes the pairwise pointmap idea to multi-view batch prediction via a transformer that jointly outputs cameras, depth, and pointmaps. |
| MASt3R | VGGT | parallel | A <-> B | Both improve 3D from images but via different routes: MASt3R adds matching to pairwise pointmaps, VGGT replaces pairwise with batch multi-view prediction. |
| VGGT | CUT3R | builds-on | A -> B | CUT3R adapts the multi-view geometry transformer to causal (autoregressive) processing for sequential frame-by-frame 3D reconstruction. |
| VGGT | InfiniteVGGT | builds-on | A -> B | InfiniteVGGT adds a rolling KV-cache memory mechanism to VGGT for constant-memory processing of arbitrarily long video streams. |
| CUT3R | InfiniteVGGT | supersedes | B -> A | InfiniteVGGT addresses the same streaming 3D goal as CUT3R but achieves it with a more scalable rolling KV-cache approach rather than fixed causal windows. |

## 4. Cluster Analysis

### 4.1 Cluster Results

| Cluster | Papers | Core Feature |
|---------|--------|-------------|
| Pointmap Regression | DUSt3R, MASt3R | Train networks to directly regress 3D pointmaps from image pairs, bypassing explicit camera estimation. |
| Multi-View Geometry Transformer | VGGT (bridge node) | Scale pointmap prediction from pairs to arbitrary multi-view batches via feed-forward transformer with global attention. |
| Streaming / Causal | CUT3R, InfiniteVGGT (bridge node) | Enable frame-by-frame 3D reconstruction from streaming video without requiring future frames. |

### 4.2 Cross-Cluster Relationships

VGGT serves as the primary bridge between the pointmap regression cluster and the streaming cluster. It inherits the dense geometry prediction paradigm from DUSt3R while introducing the transformer backbone that both CUT3R and InfiniteVGGT subsequently adapt for causal inference. InfiniteVGGT is a secondary bridge node, connecting the batch transformer approach (Cluster B) with the streaming paradigm (Cluster C) by converting VGGT's batch architecture into a rolling-memory streaming system.

The pointmap regression cluster (DUSt3R, MASt3R) represents an "encoder-decoder for geometry" paradigm that processes fixed image pairs. The streaming cluster represents the shift toward online, incremental processing demanded by robotics and AR applications.

## 5. Timeline

**CVPR 2024**: DUSt3R demonstrated that dense 3D reconstruction can be reframed as a pointmap regression task, eliminating the classical pipeline of feature extraction, matching, and bundle adjustment. This simplification showed competitive results with drastically reduced engineering complexity.

**ECCV 2024**: MASt3R observed that DUSt3R's dense pointmaps lacked fine-grained correspondence information needed for downstream tasks like relocalization. Adding a jointly-trained local feature head enabled both geometry and matching in one forward pass.

**CVPR 2025**: VGGT addressed the fundamental limitation of pairwise methods: they require expensive global optimization (e.g., global alignment or bundle adjustment) to integrate information across more than two views. By processing all views simultaneously through a transformer with cross-view attention, VGGT achieved globally consistent multi-view geometry in a single feed-forward pass.

**2025**: CUT3R recognized that VGGT's batch paradigm cannot handle streaming video (all frames must be available upfront). By applying causal attention masking, CUT3R enabled sequential, online 3D reconstruction where each new frame is processed using only previously observed context.

**2026**: InfiniteVGGT identified the memory scaling problem in CUT3R's approach: the causal attention context grows linearly with sequence length, eventually exceeding GPU memory for long videos. The rolling KV-cache solution compresses past geometric context into a fixed-size memory, achieving constant per-frame compute regardless of total sequence length.

## 6. Hub Node Analysis

**VGGT** is the hub node of this graph. It has the highest degree (4 connections) and serves as the pivot between the foundational pairwise methods and the streaming methods. Two papers build directly on it (CUT3R, InfiniteVGGT), and it builds on the foundational DUSt3R. Its architectural choice (a feed-forward transformer for multi-view geometry) established the backbone that both subsequent streaming methods adapt.

**DUSt3R** is the root node. It has 2 outgoing builds-on connections and initiated the core idea (pointmap regression) that the entire graph builds upon. Without DUSt3R's paradigm of treating 3D reconstruction as dense regression, neither the transformer-based extension (VGGT) nor the matching-augmented variant (MASt3R) would have their foundational formulation.

## 7. Graph Conclusions

The dominant research direction in this graph is the progression from pairwise to batch to streaming 3D reconstruction. The field moved from processing two images at a time (DUSt3R) to processing many images at once (VGGT) to processing frames one at a time from an infinite stream (InfiniteVGGT).

MASt3R represents a complementary but somewhat peripheral direction: improving the quality of pairwise predictions rather than scaling to more views. Its parallel relationship with VGGT suggests the community bifurcated into "make pairs better" versus "go beyond pairs" approaches.

Open problems visible from this graph include: (1) combining MASt3R's fine-grained matching with VGGT/InfiniteVGGT's multi-view architecture; (2) handling dynamic scenes in the streaming paradigm (all five methods assume static geometry); (3) achieving real-time performance on edge devices, where even the streaming methods require substantial GPU resources.
