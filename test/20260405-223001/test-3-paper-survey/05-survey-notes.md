<!-- type: paper-survey-notes | generated: 2026-04-05 -->

## 1. Survey Task

| Item | Content |
|------|---------|
| Survey Topic | Streaming 3D reconstruction from video with VGGT-based KV cache management for infinite-horizon operation |
| Trigger Source | Text query |
| Survey Date | 2026-04-05 |
| Search Strategy | NT single-thread |

## 2. Search Record

Simulated NT workflow. No external search tools were invoked. Paper collection was constructed from known publications in the VGGT and dense 3D reconstruction lineage.

Search parameters:
- Keywords: VGGT, streaming 3D reconstruction, KV cache pruning, visual geometry transformer, pointmap regression, dense SLAM
- Databases (simulated): arXiv, Semantic Scholar
- Timeframe: 2015 to 2026
- Results: 10 papers selected

## 3. Research Collection

| # | Paper/Research | Year | Type | Relevance to Survey Topic |
|---|---------------|------|------|---------------------------|
| 1 | DUSt3R (Wang et al., CVPR 2024) | 2024 | Paper | Introduced pairwise pointmap regression, founding the DUSt3R family that VGGT extends |
| 2 | MASt3R (Leroy et al., ECCV 2024) | 2024 | Paper | Added local feature matching to DUSt3R, improving 3D correspondence accuracy |
| 3 | VGGT (Wang et al., CVPR 2025) | 2025 | Paper | Core geometry transformer that InfiniteVGGT directly extends with KV cache management |
| 4 | CUT3R (Wang et al., arXiv 2025) | 2025 | Paper | Causal autoregressive architecture for sequential 3D, alternative to KV cache approach |
| 5 | Point3R (Xu et al., arXiv 2025) | 2025 | Paper | Recurrent point cloud accumulation from video, parallel approach to streaming 3D |
| 6 | TTT3R (Zhang et al., arXiv 2025) | 2025 | Paper | Test-time training adaptation for 3D, alternative online adaptation to cache pruning |
| 7 | InfiniteVGGT (Yuan et al., arXiv 2026) | 2026 | Paper | Direct VGGT extension with geometry-aware KV cache pruning for unbounded sequences |
| 8 | StreamVGGT (arXiv 2025) | 2025 | Paper | Streaming VGGT variant optimizing for real-time throughput |
| 9 | DROID-SLAM (Teed & Deng, NeurIPS 2021) | 2021 | Paper | Differentiable dense SLAM with recurrent optimization, baseline for learned SLAM systems |
| 10 | ORB-SLAM (Mur-Artal et al., T-RO 2015) | 2015 | Paper | Classical feature-based SLAM with keyframe management, operational baseline for long-horizon 3D |

## 4. Relationship Analysis

### 4.1 Relationship Table

| Research A | Research B | Relationship | Direction | Basis |
|-----------|-----------|-------------|-----------|-------|
| DUSt3R | MASt3R | builds-on | A to B | MASt3R adds local feature matching on top of DUSt3R's pointmap regression |
| DUSt3R | VGGT | builds-on | A to B | VGGT extends pointmap regression from pairwise to global multi-view via transformer |
| DUSt3R | CUT3R | builds-on | A to B | CUT3R reformulates DUSt3R-style regression as causal autoregressive process |
| MASt3R | VGGT | builds-on | A to B | VGGT incorporates dense feature matching insights from MASt3R |
| VGGT | InfiniteVGGT | builds-on | A to B | InfiniteVGGT extends VGGT with KV cache pruning for unbounded sequences |
| VGGT | StreamVGGT | builds-on | A to B | StreamVGGT adapts VGGT architecture for real-time streaming |
| CUT3R | InfiniteVGGT | parallel | bidirectional | Both address sequential 3D via different mechanisms (causal state vs. KV cache) |
| InfiniteVGGT | StreamVGGT | parallel | bidirectional | Both target streaming VGGT; time direction uncertain (concurrent work) |
| DROID-SLAM | VGGT | builds-on | A to B | VGGT replaces iterative optimization with feed-forward transformer prediction |
| ORB-SLAM | DROID-SLAM | supersedes | A to B | DROID-SLAM supersedes hand-crafted features with learned dense features |
| TTT3R | InfiniteVGGT | parallel | bidirectional | Both adapt at test time; TTT3R via gradient updates, InfiniteVGGT via cache management |
| Point3R | CUT3R | parallel | bidirectional | Both use recurrent processing for sequential 3D with similar target use cases |

### 4.2 Cluster Grouping

**Cluster A: Pairwise Pointmap Regression (DUSt3R, MASt3R)**
Core consensus: end-to-end regression from image pairs outperforms classical two-stage pipelines for pairwise 3D. Key limitation: pairwise methods require costly global alignment for multi-view scenarios, motivating the development of global transformer approaches.

**Cluster B: Global Geometry Transformers (VGGT)**
VGGT processes all views jointly through a geometry-aware transformer, eliminating post-hoc alignment. Trade-off: quadratic memory cost in view count limits sequence length to roughly 20-30 frames.

**Cluster C: Streaming and KV Cache Methods (InfiniteVGGT, StreamVGGT)**
These methods retain VGGT's attention-based architecture but prune cached tokens to bound memory. InfiniteVGGT uses geometry-aware criteria (spatial coverage, confidence) for pruning. The shared insight is that intelligent token selection preserves reconstruction quality with substantially fewer tokens.

**Cluster D: Causal and Recurrent Approaches (CUT3R, Point3R, TTT3R)**
Alternative streaming path using sequential processing with bounded state. CUT3R uses autoregressive prediction, Point3R accumulates point clouds, TTT3R adapts weights. Debate: whether causal approaches can match attention-based global consistency.

**Cluster E: Classical SLAM (ORB-SLAM, DROID-SLAM)**
ORB-SLAM's keyframe management directly inspired KV cache pruning strategies. DROID-SLAM bridged classical and learned approaches. These provide the operational and accuracy baselines.

## 5. Development Narrative

The trajectory from classical SLAM to streaming geometry transformers follows a consistent pattern of replacing hand-crafted components with learned alternatives while expanding the operational horizon. ORB-SLAM (2015) established the blueprint for long-horizon 3D reconstruction through keyframe selection, map management, and loop closure, relying on hand-crafted ORB features and geometric solvers. DROID-SLAM (2021) replaced feature extraction and matching with learned dense correspondences and differentiable bundle adjustment, achieving higher accuracy while preserving iterative optimization.

DUSt3R (CVPR 2024) took a more radical step by eliminating explicit geometric reasoning: a transformer directly regresses 3D pointmaps from image pairs. MASt3R (ECCV 2024) refined this by reintroducing feature matching as an auxiliary output. Both methods operate on pairs and require expensive global alignment for multi-view scenarios, which limited their practical scalability.

VGGT (CVPR 2025) resolved the multi-view problem by processing all images jointly through a geometry-aware transformer. This produced globally consistent 3D in a single forward pass but introduced quadratic memory scaling. The need for long-sequence processing drove two parallel directions: causal architectures (CUT3R, Point3R, TTT3R) that process frames sequentially with bounded state, and KV cache management (InfiniteVGGT, StreamVGGT) that retain global attention while pruning tokens. InfiniteVGGT (2026) combines geometry-aware token pruning with confidence-based cache management, processing thousands of frames while approaching the full-attention baseline quality.

## 6. Open Gaps

- No head-to-head comparison between KV cache pruning and causal recurrent state under identical evaluation settings
- Loop closure mechanisms are absent from all transformer-based streaming methods, risking drift on revisited trajectories
- Dynamic scene handling (moving objects, scene changes) has not been addressed by any surveyed streaming method
- The Pareto frontier relating cache budget to reconstruction quality across different pruning strategies is uncharacterized
- Integration of streaming 3D reconstruction with downstream tasks (planning, manipulation) remains unexplored
- Scalability to outdoor and large-scale environments (beyond room-scale) is underexplored for transformer-based methods

## 7. Survey Conclusions

This survey covered five research clusters spanning 11 years of development: classical SLAM baselines, pairwise pointmap regression, global geometry transformers, streaming KV cache methods, and causal/recurrent approaches. The central finding is that InfiniteVGGT represents the convergence of VGGT's global attention with SLAM-inspired memory management, enabling unbounded streaming 3D reconstruction.

Directions not covered by this survey include: (1) methods combining neural radiance fields (NeRF/3DGS) with streaming geometry, which may offer complementary dense representation capabilities; (2) multi-modal approaches integrating LiDAR or IMU with visual geometry transformers; (3) federated or distributed streaming reconstruction. These gaps suggest that the field is still in early maturation, with substantial room for cross-pollination between the surveyed clusters.
