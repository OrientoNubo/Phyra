# Peer Review Draft: Constructive (Positive Reviewer)

<!-- type: review-positive | generated: 2026-04-04 -->
<!-- paper: Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection -->

## Summary

本文提出 LAFA (Lightweight Adaptive Feature Aggregation)，將傳統 FPN 中固定的多尺度融合替換為學習式的 input-dependent routing mechanism。LAFA 使用輕量級 routing network 預測各 scale 的融合權重，並在 inference 時透過 top-K sparse selection 減少計算量。在 COCO val2017 上以 ResNet-50 backbone 達到 48.3 mAP / 42 FPS，超越 BiFPN (46.1 mAP / 35 FPS) 和 NAS-FPN (47.8 mAP / 28 FPS)。

本文的核心洞察——不同空間區域需要不同的 scale combination——是合理且有實際價值的研究方向。以下 review 著重於如何通過修正使本文達到可接受狀態。

## Strengths

**S1. 問題切入角度具啟發性**
作者從「固定拓撲在不同區域造成不等量的計算浪費」這一角度重新審視 FPN，這在 PANet/BiFPN/NAS-FPN 的演進中是一個尚未被充分探索的方向。即便該動機尚需更強的實證支撐，其出發點值得肯定。

**S2. 效率與精度的同步改善具實用價值**
LAFA 在 mAP 和 FPS 兩個維度同時優於 BiFPN，而非以一換另一。這在工業部署場景中有直接意義。48.3 mAP / 42 FPS 的性能點處於實時偵測的實用區間。

**S3. 跨 backbone 泛化趨勢一致**
R-50、R-101、Swin-T 三種 backbone 上的增益方向一致且幅度穩定（+1.9 至 +2.3 mAP），降低了「method 僅在特定 backbone 上有效」的疑慮。

**S4. 消融實驗的 K 值掃描具參考價值**
K=1/2/3/dense 四個設定的比較為使用者提供了 accuracy-speed tradeoff 的清晰選擇空間。K=1 的退化幅度 (46.8 mAP) 和 K=3 與 dense 的接近 (47.7 vs 47.9) 提供了有意義的設計 insight。

**S5. 方法的模組化設計有利於整合**
LAFA 作為 FPN 的 drop-in replacement，不改變 backbone 或 detection head，使其具備高度的整合便利性。

## Weaknesses

### Fatal Flaw

無。本文不存在根本性不可修復的缺陷。

### Major Concerns

**M1. Contribution #2 的 "theoretical analysis" 不存在**
論文在 Introduction 中聲稱「We provide theoretical analysis showing that sparse scale selection preserves detection performance when the routing function has sufficient capacity」。然而 Section 3 中僅包含方法的數學描述（公式化 routing function 和 sparse selection），不包含任何定理、引理或形式化證明。這構成一個明確的 overclaim。
**修正方向**：(a) 移除 theoretical analysis 的貢獻聲稱，將其改為 empirical observation；或 (b) 補充形式化分析，例如證明在某些條件下 top-K selection 的 approximation error 有 upper bound。選項 (a) 是最低成本的修正。

**M2. Image-level routing 與 "per-region" 聲稱之間的語義落差**
Routing network 使用 Global Average Pooling（S3.2），產生的 routing weight 是 per-image-per-scale 的，而非 per-spatial-region 的。但 Abstract 和 Introduction 多次使用「each spatial region」和「per-region routing」。若作者意指 per-scale-level 的 routing（即不同的 FPN level 接收不同的 scale 組合），措辭需修正。若作者確實意圖 per-spatial-location routing，則 GAP 的設計與此意圖不符，需要替換為 spatial-aware routing（如 per-pixel gating）。
**修正方向**：釐清 "region" 的定義。若為 per-level，修正 Introduction/Abstract 措辭；若為 per-location，修改 routing network 去除 GAP。

**M3. K=2 優於 dense routing 的異常需要解釋**
Ablation 顯示 K=2 sparse (48.3 mAP) 優於 dense routing (47.9 mAP)。在常規理解下，dense routing 包含了 sparse 的所有資訊，不應更差。這可能是 regularization effect（sparse selection 作為 implicit regularization 防止 overfitting），但論文未給出任何解釋。
**修正方向**：(a) 增加一段分析討論 sparse selection 的 regularization 效果假說；(b) 提供 training curve 比較 dense vs K=2，觀察是否存在 overfitting 差異；(c) 報告多次 run 的 variance 以排除隨機波動。

### Minor Issues

**m1. Detection framework 未明確說明**
Table 1 的 main results 未指明使用何種 detector head（Faster R-CNN、RetinaNet 或 FCOS）。鑑於不同 detector 對 feature pyramid 的敏感度不同，這是復現結果的必要資訊。
**修正方向**：在 Table 1 caption 或 S3.3 中明確標註 detector framework。

**m2. 缺乏 multi-run variance**
所有表格僅報告單次結果，未附 standard deviation。在 COCO 上 0.2-0.5 mAP 的波動是常見的。
**修正方向**：報告至少 3 次 run 的 mean 和 std。

**m3. Objects365 實驗規模偏小**
Objects365 僅報告 R-50 單一 backbone，且未提供 ablation 或 per-category 分析。
**修正方向**：至少增加一個 backbone 的 Objects365 結果，或提供 per-category breakdown。

### Suggestions

**sg1. 補充 routing decision 可視化**
為了驗證 LAFA 確實在不同 scale 的物件上做出不同的 routing 選擇，建議提供 routing weight 的可視化（如 heatmap 或 per-image routing distribution histogram）。這將直接佐證論文的核心假說。

**sg2. 與 attention mechanism baseline 對比**
增加 SE-block 或 CBAM 作為 drop-in replacement 在相同位置的比較，可以幫助讀者區分增益是來自 adaptive routing 的特定設計還是一般性的 attention 效果。

**sg3. 討論 Gumbel-Softmax 的 temperature 與 training-inference gap**
Training 使用 soft Gumbel-Softmax 而 inference 使用 hard top-K，建議報告不同 temperature 下的性能變化以及 soft vs hard inference 的比較。

## Overall Assessment

LAFA 提出了一個實用且直覺合理的方向：讓多尺度融合根據輸入自適應。實驗覆蓋多 backbone、多資料集，主要結果令人鼓舞。論文的三個 Major concerns 均可通過修正解決：M1 是措辭問題，M2 是技術描述的精確性問題，M3 需要補充分析但不動搖方法本身。若作者在 revision 中解決 M1-M3 並補充 multi-run variance，本文有潛力成為 solid contribution。

**Preliminary recommendation: Weak Accept (conditional on revision addressing M1-M3)**
