<!-- type: paper-parser-output | generated: 2026-04-04 -->

## 1. Metadata

| Field | Value |
|-------|-------|
| Title | Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection |
| Authors | Wei Zhang, Yuki Tanaka, Sarah Chen |
| Affiliation | Institute of Computer Vision, National University of Technology |
| Venue | ECCV 2026 (under review) |
| arXiv ID | N/A |
| Code | Not yet released (promised upon acceptance) |

## 2. Structure Map

| Section | Heading | Content Summary |
|---------|---------|-----------------|
| Abstract | (untitled) | Proposes LAFA module; claims 48.3 mAP at 42 FPS on COCO val2017 with R-50; 40% FLOPs reduction vs BiFPN |
| Sec 1 | Introduction | Motivates input-dependent routing for multi-scale fusion; identifies uniform fusion as the bottleneck; states three contributions |
| Sec 2 | Related Work | Covers FPN lineage (FPN, PANet, BiFPN, NAS-FPN), adaptive/dynamic networks, efficient detection |
| Sec 3 | Method | Formalizes LAFA: routing network via GAP + 2 FC layers + Gumbel-Softmax; sparse top-K selection at inference |
| Sec 4 | Experiments | Main results on COCO val2017 (Table 1); ablation (Table 2); cross-backbone R-101/Swin-T (Table 3); Objects365 (Table 4) |
| Sec 5 | Conclusion | Summarizes LAFA benefits; suggests extension to other multi-scale vision tasks |

## 3. Claimed Contributions

1. LAFA module: learned per-region routing for multi-scale feature aggregation, reducing FLOPs by 38% vs BiFPN while improving accuracy
2. Theoretical analysis: sparse scale selection preserves detection performance given sufficient routing function capacity
3. Extensive experiments on COCO and Objects365 across ResNet-50, ResNet-101, Swin-T backbones

## 4. Key Equations

**Standard FPN fusion:**

$$O_i = f_{fuse}(P_i, \text{Upsample}(O_{i+1}))$$

**LAFA fusion:**

$$O_i = \sum_{j \in S_i} R_{ij}(P_i) \cdot \text{Align}(P_j, P_i)$$

where $S_i \subseteq \{3,4,5,6,7\}$ is dynamically selected, $R_{ij}$ is the routing weight from a lightweight predictor.

## 5. Experimental Setup (Extracted)

| Parameter | Value |
|-----------|-------|
| Backbones | ResNet-50, ResNet-101, Swin-T (ImageNet-1K pretrained) |
| Optimizer | SGD, momentum 0.9, weight decay 1e-4 |
| Batch size | 16 on 8 V100 GPUs |
| Schedule | 1x (12 epochs) and 2x (24 epochs), multi-step LR decay |
| Inference | Single-scale, no TTA |
| Sparse K | 2 (default) |
| Routing network | GAP + 2 FC layers (reduction ratio r=16) + Gumbel-Softmax |

## 6. Main Quantitative Results

### COCO val2017 (R-50 backbone)

| Method | mAP | AP50 | AP75 | APs | APm | APl | FPS |
|--------|-----|------|------|-----|-----|-----|-----|
| FPN | 44.2 | 63.8 | 47.9 | 27.1 | 47.5 | 58.3 | 38 |
| PANet | 45.1 | 64.5 | 48.8 | 27.8 | 48.2 | 59.1 | 34 |
| BiFPN | 46.1 | 65.3 | 50.1 | 28.5 | 49.3 | 60.2 | 35 |
| NAS-FPN | 47.8 | 66.9 | 52.0 | 29.7 | 50.8 | 62.1 | 28 |
| LAFA | 48.3 | 67.4 | 52.5 | 30.2 | 51.3 | 62.8 | 42 |

### Ablation (K selection)

| Configuration | mAP | FPS |
|--------------|-----|-----|
| BiFPN baseline | 46.1 | 35 |
| + Adaptive routing (dense) | 47.9 | 31 |
| + Sparse selection (K=3) | 47.7 | 38 |
| + Sparse selection (K=2) | 48.3 | 42 |
| + Sparse selection (K=1) | 46.8 | 48 |

### Cross-Backbone

| Method | Backbone | mAP | FPS |
|--------|----------|-----|-----|
| BiFPN | R-101 | 47.5 | 28 |
| LAFA | R-101 | 49.8 | 34 |
| BiFPN | Swin-T | 49.2 | 22 |
| LAFA | Swin-T | 51.1 | 29 |

### Objects365

| Method | Backbone | mAP | FPS |
|--------|----------|-----|-----|
| BiFPN | R-50 | 28.3 | 33 |
| LAFA | R-50 | 30.1 | 40 |

## 7. References (Parsed)

| # | Citation | Venue |
|---|----------|-------|
| 1 | Lin et al., Feature Pyramid Networks for Object Detection | CVPR 2017 |
| 2 | Liu et al., Path Aggregation Network for Instance Segmentation | CVPR 2018 |
| 3 | Tan et al., EfficientDet: Scalable and Efficient Object Detection | CVPR 2020 |
| 4 | Ghiasi et al., NAS-FPN: Learning Scalable Feature Pyramid Architecture | CVPR 2019 |
| 5 | Chen et al., Dynamic Convolution: Attention over Convolution Kernels | CVPR 2020 |
| 6 | Yang et al., CondConv: Conditionally Parameterized Convolutions | NeurIPS 2019 |
| 7 | Ge et al., YOLOX: Exceeding YOLO Series in 2021 | arXiv 2021 |
| 8 | Li et al., YOLOv6: Single-Stage Object Detection for Industrial Applications | arXiv 2022 |
| 9 | Zhao et al., DETRs Beat YOLOs on Real-time Object Detection | CVPR 2024 |
