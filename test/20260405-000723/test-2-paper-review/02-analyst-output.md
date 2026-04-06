# Content Analyst Output

<!-- type: analyst-output | generated: 2026-04-04 -->
<!-- source: sample-paper.md -->

## Claim Map

下表追蹤論文中每個核心聲稱，並標記其證據來源與驗證狀態。

| # | Claim | Evidence Source | Verified? | Notes |
|---|-------|----------------|-----------|-------|
| C1 | 現有 FPN 方法對所有空間位置施加相同的 cross-scale fusion，造成冗餘 | Introduction 論述 (S1, para 2) | Partially | 動機合理但缺少量化證據（如 per-region fusion utility 的統計分析） |
| C2 | LAFA 透過 input-dependent routing 減少約 40% 冗餘 cross-scale interaction | Abstract + S3.2 | Partially | 40% 的數字僅在 FLOPs 層面呈現；未區分「冗餘」interaction 與「有用但被裁剪」的 interaction |
| C3 | LAFA 達到 48.3 mAP / 42 FPS (R-50, COCO val2017) | Table 1 | Yes (surface) | 數字本身可驗證，但缺乏 confidence interval 或 multi-run variance |
| C4 | Adaptive routing 貢獻 +1.8 mAP over static fusion | Ablation Table 2 | Yes | 消融設計合理：dense routing vs BiFPN baseline |
| C5 | Sparse selection (K=2) 同時改善 accuracy (+0.4 over dense) 和 speed | Ablation Table 2 | Anomalous | K=2 sparse 優於 dense routing 是反直覺的；論文未解釋為何減少 scale combination 反而提升精度 |
| C6 | 理論分析顯示 sparse selection 在 routing function 有足夠 capacity 時保留偵測性能 | Contribution list (S1) | Not found | 論文聲稱提供「theoretical analysis」，但 S3 中僅有公式化描述，無定理或證明 |
| C7 | 跨 backbone 一致改進 (R-101, Swin-T) | Table 3 | Yes | 增益幅度一致 (+2.3 R-101, +1.9 Swin-T)，趨勢可信 |
| C8 | Objects365 上的改進 (30.1 vs 28.3) | Table 4 | Yes (surface) | 僅報告單一 backbone，實驗規模較小 |

## Method Logic Evaluation

### Core Design Logic Chain

```
Observation: 靜態 FPN 對所有位置施加相同融合 (S1)
    |
    v
Hypothesis: 不同區域需要不同的 scale combination (S1, para 3-4)
    |
    v
Design: 學習 per-region routing function R_ij (S3.2)
    |
    v
Training: Gumbel-Softmax 實現可微分離散選擇 (S3.2)
    |
    v
Inference: Top-K 稀疏選擇減少計算 (S3.2)
```

### Logic Evaluation

**從 Observation 到 Hypothesis：合理但未量化。** 作者指出「for large objects occupying a single scale, the multi-scale fusion is redundant」，這是合理的直覺，但未提供任何實證（如統計不同尺度物件在 FPN 各層的 feature utilization rate）。

**從 Hypothesis 到 Design：邏輯成立。** 若接受 hypothesis，則 learned per-region routing 是自然的設計回應。

**Routing Network 設計選擇：未充分論證。** GAP + 2FC 的 routing network 是 image-level 的（GAP 消除空間維度），但論文聲稱的是 per-region routing。這存在矛盾：routing 決策是 image-level 的，不是 region-level 的。論文未討論這一 gap。

**Gumbel-Softmax 到 Top-K 的轉換：有隱患。** Training 時使用 soft Gumbel-Softmax，inference 時使用 hard top-K selection。Training-inference discrepancy 可能導致性能偏移，但論文未分析此影響。

**K=2 優於 dense 的異常：未解釋。** Ablation 表顯示 K=2 (48.3) 優於 dense routing (47.9)。若 dense routing 包含所有 scale 資訊，sparse selection 不應提升精度。可能的解釋包括 regularization effect 或 noise filtering，但作者僅將此描述為「best accuracy-efficiency tradeoff」而未深入分析。

## Experiment Sufficiency Analysis

### Covered

- [x] 主要 benchmark (COCO val2017) 上的 SOTA 比較
- [x] 多 backbone 泛化 (R-50, R-101, Swin-T)
- [x] 基本消融 (routing type, K 值)
- [x] 第二資料集驗證 (Objects365)
- [x] FPS 測量 (V100 single GPU)

### Missing or Insufficient

- [ ] **Multi-run variance**: 所有結果僅報告單次數值，無 standard deviation 或 confidence interval
- [ ] **理論分析的實驗驗證**: Contribution #2 聲稱有 theoretical analysis，但論文中不存在對應的定理或證明
- [ ] **Per-region routing 可視化**: 論文聲稱 per-region adaptive routing，但未提供任何 routing decision 的可視化（如 heatmap 顯示不同區域選擇了哪些 scale）
- [ ] **Training-inference gap 分析**: Gumbel-Softmax (training) vs hard top-K (inference) 的差異未量化
- [ ] **Detection head 資訊**: 使用何種 detection head (Faster R-CNN? RetinaNet? FCOS?) 未明確說明
- [ ] **Attention baseline 對比**: 未與 SE-Net、CBAM 等既有 attention mechanism 在相同位置的 drop-in replacement 進行比較
- [ ] **Latency breakdown**: 40% FLOPs reduction 的組成未分解（routing network 本身的開銷 vs 節省的 fusion 開銷）
- [ ] **失敗案例分析**: 無 failure case 討論

## Red Flags

**[RF-1] 幽靈貢獻 (Ghost Contribution)**
Contribution #2 聲稱「theoretical analysis showing that sparse scale selection preserves detection performance when the routing function has sufficient capacity」。論文中不存在此 theoretical analysis。S3 僅包含方法描述和公式定義，無任何定理、引理或形式化證明。這是一個明確的 overclaim。

**[RF-2] Image-level vs Region-level 矛盾**
S3.2 描述 routing network 使用 Global Average Pooling，這意味著 routing 決策是 per-image 的，而非 per-region 的。但論文在 Introduction 和 Abstract 中反覆強調「per-region」和「each spatial region」。除非作者指的是 per-scale-level（而非 per-spatial-location），否則存在技術描述矛盾。

**[RF-3] K=2 異常未解釋**
Sparse selection (K=2) 同時優於 dense routing 在 accuracy 和 speed 上。Speed 改善合理，但 accuracy 改善需要解釋。若無解釋，讀者無法區分這是有意義的 regularization effect 還是 training randomness。

**[RF-4] 缺少 detection framework 說明**
Main results (Table 1) 未說明使用何種 detection framework。FPN/PANet/BiFPN 可搭配不同 detector head，不同 head 對 feature pyramid 質量的敏感度不同。此遺漏使結果難以復現。

**[RF-5] Code 未公開**
「Code will be released upon acceptance」是常見做法，但結合 RF-4 的 framework 未說明和 routing network 的具體實作細節缺失，可重現性受到影響。
