# Review Scoring Report

<!-- type: review-scoring-report | generated: 2026-04-04 -->
<!-- paper: Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection -->

## 技術發展路徑

**[2017] FPN (Lin et al., CVPR 2017)**
首次提出 top-down pathway + lateral connections 實現多尺度 feature fusion，成為後續所有 multi-scale detection 架構的基礎。核心限制：所有空間位置接受相同的 cross-scale fusion，fusion 方式為固定的 element-wise addition + 3x3 conv，無法根據輸入內容調整。

**[2018] PANet (Liu et al., CVPR 2018)**
在 FPN top-down pathway 之上增加 bottom-up path augmentation，使淺層 high-resolution feature 能更直接地傳遞至深層。核心限制：增加了路徑但融合權重仍然固定，未實現 input-dependent 的 fusion。增加的路徑同時帶來了額外的計算成本。

**[2019] NAS-FPN (Ghiasi et al., CVPR 2019)**
使用 neural architecture search 自動搜索最優的 cross-scale connection topology，跳脫了人工設計的固定路徑。核心限制：搜索得到的 topology 在部署後仍為靜態，無法根據 inference 時的不同輸入做出調整。搜索成本高昂，實際部署的拓撲仍然是 input-independent 的。

**[2020] BiFPN (Tan et al., EfficientDet, CVPR 2020)**
引入 weighted bidirectional cross-scale connections，首次在 FPN 系列中讓 fusion weight 成為可學習參數。核心限制：fusion weight 為 input-independent 的 learnable scalar，training 完成後固定，無法處理 inference 時不同影像的 scale distribution 差異。

**[2026] LAFA (Zhang et al., 本文)**
將 FPN fusion weight 從 static learned parameter 擴展為 input-dependent function（routing network），並引入 sparse selection 減少計算。相對前驅的具體進展：(a) fusion weight 由 input-dependent network 生成，而非固定參數；(b) top-K sparse selection 在維持精度的同時減少 inference 計算。遺留問題（由本次 review 揭示）：routing 為 image-level 而非聲稱的 per-region level，theoretical analysis 聲稱不成立，核心假設缺乏驗證。

## 五維評分

### 1. 問題有效性（Problem Validity）: 7/10

多尺度 feature aggregation 的效率問題在 real-time object detection 中是真實且重要的。FPN 及其變體的固定 fusion 確實存在「對所有位置施加相同 fusion」的特性，將此改為 adaptive 是一個合理的研究方向。

扣分理由：(a) 論文將問題定義為「per-region 需要不同 scale combination」，但未提供任何實證支撐此定義；(b) 問題的重要性聲稱（「redundant cross-scale interactions」）缺乏量化支持。問題的存在是直覺上合理的，但嚴格性不足。

### 2. 方法合理性（Method Soundness）: 5/10

LAFA 的核心設計——input-dependent routing + sparse selection——在邏輯上回應了問題定義。GAP + 2FC 的 routing network 是輕量且合理的選擇。Gumbel-Softmax 實現可微分離散選擇是成熟的技術。

扣分理由：(a) 聲稱 per-region routing 但使用 GAP 導致 routing 實際為 per-image，核心聲稱與實作矛盾；(b) "theoretical analysis" 貢獻不存在；(c) training (Gumbel-Softmax soft) 與 inference (hard top-K) 的 discrepancy 未分析；(d) routing network 為何選擇 GAP + 2FC 而非其他架構（如 spatial-aware routing）缺乏設計理由論述。方法本身可能有效，但論文對方法的理解和論述不充分。

### 3. 實驗充分性（Experimental Adequacy）: 6/10

正面：涵蓋 COCO 和 Objects365 兩個資料集、三種 backbone（R-50、R-101、Swin-T）、K 值的消融掃描。

扣分理由：(a) 所有結果為單次 run，無 variance 報告；(b) detection framework 未指明，baseline 數字來源不清；(c) 聲稱 40% FLOPs reduction 但無 FLOPs 數據表；(d) 缺乏 attention baseline 對比（SE/CBAM）；(e) K=2 > dense 異常未分析；(f) 無 routing decision 可視化；(g) Objects365 實驗規模偏小（單 backbone）。實驗覆蓋面尚可，但深度和嚴謹度不足。

### 4. 新穎性（Novelty）: 6/10

將 input-dependent dynamic weighting 引入 FPN fusion 是一個有意義的演進步驟，在 FPN -> PANet -> BiFPN -> NAS-FPN 的技術路徑上屬於自然的下一步。Gumbel-Softmax + top-K sparse selection 的組合在此 context 中是新的。

扣分理由：(a) routing network 的個別組件（GAP + FC + Gumbel-Softmax）均為已知技術，novelty 主要在於組合與應用位置；(b) 論文未引用或討論 2024-2026 年的 concurrent work，使 novelty margin 無法被準確評估；(c) 若承認 routing 是 image-level 的（而非 per-region），則方法退化為一個 input-dependent version of BiFPN's learnable weights，novelty space 進一步壓縮。

### 5. 可重現性（Reproducibility）: 5/10

正面：backbone 和 training schedule 的基本設定已說明（S3.3）。

扣分理由：(a) detection framework 未指明；(b) routing network 的具體超參數（Gumbel-Softmax temperature、temperature annealing schedule）未完整列出；(c) code 未公開（upon acceptance）；(d) baseline 數字是 re-implementation 還是引用原論文未說明；(e) FPN level 設定（P3-P7 或其子集）在不同 backbone 上是否一致未說明。

## 加權總分與等級

| 維度 | 權重 | 分數 | 加權分 |
|------|------|------|--------|
| 問題有效性 (Problem Validity) | 0.15 | 7 | 1.050 |
| 方法合理性 (Method Soundness) | 0.30 | 5 | 1.500 |
| 實驗充分性 (Experimental Adequacy) | 0.30 | 6 | 1.800 |
| 新穎性 (Novelty) | 0.15 | 6 | 0.900 |
| 可重現性 (Reproducibility) | 0.10 | 5 | 0.500 |
| **加權總分** | **1.00** | | **5.750** |

**等級對照：**

| 等級 | 範圍 |
|------|------|
| Strong Accept | 8.5 - 10.0 |
| Accept | 7.0 - 8.4 |
| Weak Accept | 5.5 - 6.9 |
| Borderline | 4.5 - 5.4 |
| Weak Reject | 3.0 - 4.4 |
| Reject | 1.0 - 2.9 |

**本文等級：Weak Accept (5.75)**

**等級與實質判斷的一致性說明：** 加權總分 5.75 落在 Weak Accept 區間下緣。此數字反映了問題有效性尚可 (7) 但方法合理性 (5) 和可重現性 (5) 偏低的分布。鑑於方法合理性中的主要失分原因（per-region vs per-image 矛盾、虛假 theoretical analysis 聲稱）均為可修正問題，5.75 的數字與 "Major Revision" 的建議一致——目前版本不適合直接接受，但問題不屬於 fatal flaw 層級。

## Recommendation

**Recommendation: Major Revision (Revise and Resubmit)**

### 必要修正（gate to acceptance）

1. **重新校準 per-region 敘事**：承認 routing 為 image-level，或重新設計 routing network 實現真正的 spatial routing。修改 Abstract、Introduction、Contribution #1 中的相關措辭。
2. **移除或實質化 theoretical analysis 聲稱**：刪除 Contribution #2 中的 "theoretical analysis" 表述，或補充形式化的 approximation bound / preservation theorem。
3. **補充 multi-run variance**：至少 3 次 run 的 mean/std，覆蓋 main results 和 ablation。
4. **明確 detection framework**：在 Table 1 和 S3.3 中標註 detector head。
5. **提供 FLOPs 數據**：以表格形式報告各方法的 FLOPs，支撐 40% reduction 聲稱。

### 建議修正（strengthen further）

6. 補充 SE/CBAM attention baseline 在相同位置的 drop-in comparison
7. 分析 K=2 > dense 的原因（training curve 比較、regularization effect 假說驗證）
8. 提供 routing decision 可視化（per-image routing weight distribution）
9. 分析 Gumbel-Softmax soft inference vs hard top-K inference 的性能差異
10. 討論 2024-2026 年的 concurrent work

### 預估修正後分數

若必要修正 1-5 完成且結果正面：方法合理性可提升至 7（消除核心矛盾）、實驗充分性可提升至 7（variance + FLOPs data）、可重現性可提升至 6（framework 說明 + FLOPs data），預估加權總分：

7 x 0.15 + 7 x 0.30 + 7 x 0.30 + 6 x 0.15 + 6 x 0.10 = 1.05 + 2.10 + 2.10 + 0.90 + 0.60 = **6.75 (Weak Accept, upper range)**

若建議修正 6-10 也完成，新穎性可提升至 7，總分可達 **7.05 (Accept)**。
