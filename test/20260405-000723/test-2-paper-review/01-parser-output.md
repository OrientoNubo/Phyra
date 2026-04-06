# Paper Parser Output

<!-- type: parser-output | generated: 2026-04-04 -->
<!-- source: sample-paper.md -->

## Metadata

| Field | Value |
|-------|-------|
| Title | Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection |
| Authors | Wei Zhang, Yuki Tanaka, Sarah Chen |
| Affiliation | Institute of Computer Vision, National University of Technology |
| Venue | ECCV 2026 (under review) |
| Domain | Computer Vision / Object Detection |
| Paper type | Method paper (new module for existing pipeline) |

## Claimed Contributions

1. **LAFA module**: A lightweight module that learns per-region routing decisions for multi-scale feature aggregation, reducing FLOPs by 38% compared to BiFPN while improving accuracy.
2. **Theoretical analysis**: Sparse scale selection preserves detection performance when the routing function has sufficient capacity.
3. **Extensive experiments**: Consistent improvements on COCO and Objects365 across backbone architectures (ResNet-50, ResNet-101, Swin-T).

## Structure Map

| Section | Content Summary |
|---------|----------------|
| Abstract | States problem (FPN overhead), proposes LAFA (input-dependent routing), reports 48.3 mAP / 42 FPS on COCO R-50, claims 40% cross-scale reduction |
| S1. Introduction | Motivates input-dependent routing as key bottleneck; argues static topologies waste computation on regions not needing cross-scale fusion |
| S2. Related Work | Covers FPN family (FPN, PANet, BiFPN, NAS-FPN), dynamic/adaptive networks (DynConv, CondConv, YOLOX), efficient detection (EfficientDet, YOLO, RT-DETR) |
| S3. Method | Formalizes LAFA: learned routing function R with Gumbel-Softmax training, top-K sparse selection at inference (K=2 default); routing network = GAP + 2 FC layers (r=16) |
| S4. Experiments | Main results on COCO val2017 (Table 1), ablation study (Table 2), cross-backbone R-101/Swin-T (Table 3), Objects365 (Table 4) |
| S5. Conclusion | Summarizes LAFA advantages; suggests adaptive routing can extend to other multi-scale vision tasks |

## Key Numerical Claims

| Claim | Value | Location |
|-------|-------|----------|
| LAFA mAP (R-50, COCO) | 48.3 | Table 1 |
| LAFA FPS (R-50, V100) | 42 | Table 1 |
| BiFPN mAP baseline | 46.1 | Table 1 |
| FLOPs reduction vs BiFPN | ~38-40% | Abstract, S3.2 |
| Adaptive routing contribution | +1.8 mAP (dense) | Ablation Table 2 |
| Best K setting | K=2 (48.3 mAP, 42 FPS) | Ablation Table 2 |
| LAFA mAP (Swin-T, COCO) | 51.1 | Table 3 |
| LAFA mAP (R-50, Objects365) | 30.1 | Table 4 |

## Cited Works (9 references)

1. Lin et al. FPN (CVPR 2017)
2. Liu et al. PANet (CVPR 2018)
3. Tan et al. EfficientDet / BiFPN (CVPR 2020)
4. Ghiasi et al. NAS-FPN (CVPR 2019)
5. Chen et al. Dynamic Convolution (CVPR 2020)
6. Yang et al. CondConv (NeurIPS 2019)
7. Ge et al. YOLOX (arXiv 2021)
8. Li et al. YOLOv6 (arXiv 2022)
9. Zhao et al. DETRs Beat YOLOs / RT-DETR (CVPR 2024)

## Extracted Equations

**FPN baseline formulation:**
$$O_i = f_{fuse}(P_i, \text{Upsample}(O_{i+1}))$$

**LAFA formulation:**
$$O_i = \sum_{j \in S_i} R_{ij}(P_i) \cdot \text{Align}(P_j, P_i)$$

where $S_i$ is a dynamically selected subset of scales and $R_{ij}$ is a routing weight from a lightweight network.
