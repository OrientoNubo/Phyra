# Parsed Paper: Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection

## Metadata

- **Title:** Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection
- **Authors:** Wei Zhang, Yuki Tanaka, Sarah Chen
- **Affiliation:** Institute of Computer Vision, National University of Technology
- **Venue:** ECCV 2026 (under review)

## Sections

### Abstract
Proposes Lightweight Adaptive Feature Aggregation (LAFA), a module replacing fixed multi-scale fusion with a learned, input-dependent routing mechanism. Claims 48.3 mAP on COCO val2017 with ResNet-50 at 42 FPS (V100), outperforming BiFPN (46.1 mAP, 35 FPS) and NAS-FPN (47.8 mAP, 28 FPS). Claims 40% reduction in redundant cross-scale interactions.

### 1. Introduction
Identifies the uniform treatment of spatial locations in FPN-based methods as the key limitation. Argues input-dependent routing is the missing ingredient. States three contributions: (1) LAFA module with per-region routing, (2) theoretical analysis of sparse scale selection, (3) experiments on COCO and Objects365 across three backbones.

### 2. Related Work
Covers three strands: Feature Pyramid Networks (FPN, PANet, BiFPN, NAS-FPN), Adaptive/Dynamic Networks (Dynamic Convolution, CondConv, YOLOX), and Efficient Detection (EfficientDet, YOLO variants, RT-DETR). Positions LAFA as orthogonal to convolution-parameter adaptation.

### 3. Method
- 3.1 Problem Formulation: Standard FPN top-down fusion equation. Notes computation scales linearly with scales, quadratically with cross-scale connections.
- 3.2 LAFA: Replaces fixed fusion with routing function R. Uses global average pooling + two FC layers (reduction ratio r=16) for routing logits. Gumbel-Softmax during training, top-K selection (K=2 default) during inference.
- 3.3 Implementation: ResNet-50/101 or Swin-T backbones. SGD, batch 16 on 8 V100s. 1x/2x schedules. Single-scale inference.

### 4. Experiments
- 4.1 Main COCO results: LAFA R-50 achieves 48.3 mAP / 42 FPS.
- 4.2 Ablation: K=2 is optimal. Adaptive routing contributes +1.8 mAP; sparse selection further adds +0.4 mAP and speed gains.
- 4.3 Cross-backbone: LAFA improves over BiFPN on R-101 (+2.3 mAP, +6 FPS) and Swin-T (+1.9 mAP, +7 FPS).
- 4.4 Objects365: LAFA R-50 achieves 30.1 mAP vs BiFPN 28.3 mAP.

### 5. Conclusion
Summarizes LAFA's adaptive routing principle and suggests extension to other multi-scale vision tasks.

## Figures and Tables

- **Table 1** (Section 4.1): Main COCO val2017 comparison (5 methods, R-50 backbone). Columns: Method, Backbone, mAP, AP50, AP75, APs, APm, APl, FPS.
- **Table 2** (Section 4.2): Ablation study (5 configurations). Columns: Configuration, mAP, FPS, Delta mAP.
- **Table 3** (Section 4.3): Cross-backbone results (4 rows). Columns: Method, Backbone, mAP, FPS.
- **Table 4** (Section 4.4): Objects365 results (2 rows). Columns: Method, Backbone, mAP, FPS.
- **Equations:** Two key equations defining standard FPN fusion and LAFA routing-weighted fusion.

## References

9 references cited, spanning CVPR 2017-2024, NeurIPS 2019, and arXiv preprints. Key baselines: FPN [1], PANet [2], BiFPN/EfficientDet [3], NAS-FPN [4].

## Detected Issues

- The abstract claims "approximately 40%" reduction in cross-scale interactions, but the ablation table shows 38% FLOPs reduction (mentioned in contribution 1). Minor inconsistency in precision.
- Theoretical analysis (contribution 2) is claimed but not presented in the method section; no theorem or proof appears in the paper.
- Code availability is conditional on acceptance; no reproducibility artifacts are currently available.
- All experiments use a single GPU type (V100); no latency measurements on edge devices despite "real-time" framing.
