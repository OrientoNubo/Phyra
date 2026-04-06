<!-- type: paper-graph-notes | generated: 2026-04-05 -->

## 1. Graph Task

| Item | Content |
|------|---------|
| Number of input papers | 5 |
| Input source | Title list with author and venue annotations |
| Analysis date | 2026-04-05 |
| Analysis strategy | NT sequential |

## 2. Paper List

| Seq | Paper Name | Year | First Author | Venue |
|-----|-----------|------|-------------|-------|
| 1 | End-to-End Object Detection with Transformers (DETR) | 2020 | Nicolas Carion | ECCV 2020 |
| 2 | Deformable Transformers for End-to-End Object Detection (Deformable DETR) | 2021 | Xizhou Zhu | ICLR 2021 |
| 3 | DETR with Improved DeNoising Anchor Boxes (DINO) | 2023 | Hao Zhang | ICLR 2023 |
| 4 | DETRs Beat YOLOs on Real-time Object Detection (RT-DETR) | 2024 | Yian Zhao | CVPR 2024 |
| 5 | DETRs with Collaborative Hybrid Assignments Training (Co-DETR) | 2023 | Zhuofan Zong | ICCV 2023 |

## 3. Relationship Matrix

| Paper A | Paper B | Relationship Type | Direction | Basis |
|---------|---------|------------------|-----------|-------|
| DETR | Deformable DETR | builds-on | A->B | Deformable attention replaces global attention to address convergence and small-object limitations |
| DETR | DINO | builds-on | A->B | Inherits set-prediction framework; improves denoising and query initialization |
| DETR | RT-DETR | builds-on | A->B | Retains end-to-end paradigm; redesigns encoder for real-time efficiency |
| DETR | Co-DETR | builds-on | A->B | Targets one-to-one matching inefficiency as primary research motivation |
| Deformable DETR | DINO | builds-on | A->B | Uses multi-scale deformable attention as base; adds contrastive denoising and mixed query selection |
| Deformable DETR | RT-DETR | builds-on | A->B | Decoder retains deformable cross-attention; encoder redesigned with hybrid architecture |
| Deformable DETR | Co-DETR | builds-on | A->B | Primary experimental baseline; collaborative training applied on its encoder-decoder |
| DINO | RT-DETR | builds-on | A->B | Query selection draws on DINO's mixed query selection with added uncertainty minimization |
| DINO | Co-DETR | parallel | Uncertain (both 2023) | Independently address training efficiency: denoising vs. hybrid matching |
| RT-DETR | Co-DETR | parallel | Uncertain | Solve orthogonal problems: inference speed vs. training supervision density |

## 4. Cluster Analysis

### 4.1 Cluster Results

| Cluster Name | Papers Included | Core Characteristic |
|-------------|----------------|-------------------|
| Attention mechanism reform | DETR, Deformable DETR | Explores how to compute attention in detection Transformers: global vs. sparse deformable |
| Training efficiency | DINO, Co-DETR | Addresses sparse supervision from one-to-one matching through denoising (DINO) or auxiliary one-to-many heads (Co-DETR) |
| Deployment efficiency | RT-DETR | Targets real-time inference through encoder architecture redesign |

### 4.2 Inter-Cluster Relationships

The attention mechanism cluster provides the architectural foundation for both subsequent clusters. Training efficiency and deployment efficiency clusters operate on orthogonal axes: the former maximizes the information extracted per training sample, while the latter minimizes per-sample inference cost. Their advances are largely composable; for instance, Co-DETR's collaborative training could in principle be applied to RT-DETR's architecture to improve its accuracy without affecting inference speed.

## 5. Timeline

- **2020 (ECCV)** DETR: Establishes end-to-end detection with Transformer + Hungarian matching. Breakthrough in removing NMS/anchors, but convergence requires 500 epochs and small-object performance lags behind Faster R-CNN.
- **2021 (ICLR)** Deformable DETR: Deformable attention enables multi-scale features and 10x faster convergence. This becomes the standard backbone for the DETR lineage.
- **2023 (ICLR)** DINO: Contrastive denoising + mixed query selection push DETR-family to 63.2 AP, achieving full parity with conventional detectors for the first time.
- **2023 (ICCV)** Co-DETR: Collaborative hybrid assignments reach 66.0 AP (with extra data). Demonstrates that enriching encoder supervision during training is complementary to decoder-side improvements.
- **2024 (CVPR)** RT-DETR: Efficient hybrid encoder achieves 108 FPS / 53.1 AP (R50 on T4), beating YOLO models on the real-time Pareto frontier. Validates practical deployment viability of the end-to-end paradigm.

## 6. Hub Node Analysis

**DETR** is the root hub of this graph: all four other papers cite it as foundational motivation and build directly upon its set-prediction formulation. However, **Deformable DETR** functions as the operational hub. While DETR established the conceptual framework, Deformable DETR provided the practical architecture (multi-scale deformable attention) that all three subsequent papers (DINO, RT-DETR, Co-DETR) use as their starting implementation. Removing Deformable DETR from this graph would sever the technical lineage between DETR's concept and the 2023-2024 papers' implementations.

## 7. Graph Conclusion

The DETR family's evolution follows a clear pattern: a paradigm-setting paper (DETR) is followed by an architectural fix (Deformable DETR), then a branching into precision optimization (DINO, Co-DETR) and efficiency optimization (RT-DETR).

The mainstream direction as of 2024 is convergence: combining training efficiency techniques with deployment-aware architectures. The gap between DETR-family and YOLO-family detectors has closed on both accuracy and speed fronts.

Open questions remain. First, the interaction between Co-DETR's collaborative training and RT-DETR's efficient encoder has not been fully explored; composing the two could yield a model that is both fast and maximally supervised. Second, all five papers evaluate on COCO; generalization to open-vocabulary detection, video, and 3D remains an active frontier where the end-to-end advantage of DETR is yet to be fully validated. Third, the scalability of DETR-family architectures under foundation-model regimes (billion-parameter backbones, web-scale pretraining) is an emerging direction that none of these five papers directly address.
