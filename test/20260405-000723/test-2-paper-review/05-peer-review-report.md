# Peer Review Report (Chair Synthesis)

<!-- type: peer-review-report | generated: 2026-04-04 -->
<!-- paper: Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection -->
<!-- synthesized from: 03-review-positive.md, 04-review-negative.md -->

## Divergence Analysis

在整合兩份 review 之前，先識別兩位 reviewer 的判斷分歧點與共識點。

**共識區域（兩位 reviewer 一致）：**
- "Theoretical analysis" 貢獻不存在，構成 overclaim (Positive-M1, Negative-T2)
- Image-level routing 與 "per-region" 聲稱之間存在落差 (Positive-M2, Negative-T1)
- K=2 sparse 優於 dense 的異常需要解釋 (Positive-M3, Negative-C2)
- Detection framework 未說明 (Positive-m1, Negative-P1)
- Multi-run variance 缺失 (Positive-m2)
- 實驗結果本身（48.3 mAP / 42 FPS）若可復現，具有實用價值

**分歧區域：**

| 議題 | Positive Reviewer | Negative Reviewer | Chair 判定 |
|------|-------------------|-------------------|-----------|
| per-image vs per-region 的嚴重性 | 措辭問題或技術精確性問題，可修正 | 核心聲稱與實作的根本矛盾，動機與方法斷裂 | 偏向 Negative：GAP 消除空間維度是事實，這使 Introduction 的 per-region 敘事失去方法支撐。但 Positive reviewer 指出的修正路徑可行，不構成 fatal flaw |
| 方法的實際價值 | 核心洞察合理，跨 backbone 泛化一致，模組化設計有利整合 | Image-level dynamic weighting 本身可能有價值，但被包裝為更宏大的敘事 | 兩者不矛盾：方法有實際價值，但論文的 framing 顯著誇大了方法的技術深度 |
| 核心假設未驗證 (C1) | 未提及 | 視為 conceptual defect：「不同區域需要不同 scale combination」未被實證 | 採納 Negative 觀點：此假設是全文動機基礎，缺乏驗證是實質性缺陷 |
| Gumbel-Softmax training-inference gap (T3) | 列為 Suggestion (sg3) | 列為 Major technical defect | 判定為 Minor-to-Major：確實是已知問題，但鑑於 K=2 的 ablation 結果穩定，實際影響可能有限。需要數據才能判斷嚴重性。 |
| 整體 recommendation | Weak Accept (conditional) | Weak Reject | 見下方 Overall Assessment |

## Summary

本文提出 LAFA，以 learned routing function 替代 FPN 的固定 multi-scale fusion。方法使用 GAP + FC 的 routing network 預測 scale 融合權重，inference 時進行 top-K sparse selection。在 COCO val2017 上報告 48.3 mAP / 42 FPS (R-50)，優於 BiFPN 和 NAS-FPN。

論文的核心問題是 narrative 與 reality 之間的系統性偏差：聲稱 per-region routing 但實作為 per-image；聲稱 theoretical analysis 但不存在；聲稱 40% FLOPs reduction 但未提供 FLOPs 數據。

## Strengths

**S1. 效率與精度的同步改善（兩位 reviewer 一致肯定）**
48.3 mAP / 42 FPS 在 R-50 上同時超越 BiFPN 的 mAP 和 FPS，若可復現，這是有實際部署價值的結果。

**S2. 跨 backbone/dataset 泛化（兩位 reviewer 一致肯定）**
R-50、R-101、Swin-T 上的增益方向一致（+1.9 至 +2.3 mAP），Objects365 上也有正面結果。

**S3. 消融實驗中 K 值掃描的設計合理（Positive reviewer 提出）**
K=1/2/3/dense 的比較提供了有意義的 tradeoff insight，儘管 K=2 > dense 的異常削弱了消融的說服力。

**S4. 模組化設計的實用性（Positive reviewer 提出）**
LAFA 作為 FPN drop-in replacement 的設計具備整合便利性。

## Weaknesses

**W1. [Major, Grade: B-] 核心聲稱與實作矛盾：per-region vs per-image routing**
兩位 reviewer 均識別此問題。Routing network 使用 GAP，routing 決策是 per-image-per-scale 的，而非 per-spatial-region 的。論文的 Introduction 敘事和方法實作之間存在根本性的語義落差。此問題通過以下方式可修正：(a) 如實修改敘事為 image-level adaptive weighting，或 (b) 重新設計 routing network 去除 GAP 實現真正的 spatial routing。

**W2. [Major, Grade: C+] "Theoretical analysis" 貢獻虛報**
兩位 reviewer 均確認論文中不存在 theoretical analysis。三項聲稱貢獻中一項為虛。修正方式簡單（移除或降級該聲稱），但此問題反映了論文整體敘事的 inflation tendency。

**W3. [Major, Grade: B-] 核心假設未驗證**
Negative reviewer 指出「不同區域需要不同 scale combination」作為全文動機，從未被任何實驗或分析驗證。需要 oracle experiment 或 feature utilization analysis 來支撐。

**W4. [Minor-Major, Grade: B] K=2 > dense 異常未解釋**
兩位 reviewer 均注意到此異常。缺乏解釋使讀者無法判斷這是有意義的 regularization effect 還是 training randomness。需要 multi-run variance 和 training curve 分析。

**W5. [Minor, Grade: C+] Detection framework 與 baseline 來源未說明**
Main results table 未指明 detector head。Baseline 數字（如 FPN 44.2 mAP）高於多數公開報告值。復現性受損。

**W6. [Minor, Grade: B] FLOPs reduction 聲稱缺乏數據支撐**
40% FLOPs reduction 在 Abstract 和 Method 中被引用，但 Experiment section 不包含任何 FLOPs measurement。

## Overall Assessment

**兩位 reviewer 的判斷在根本問題上高度一致**：三項 Major 共識（虛假 theoretical analysis 聲稱、per-image vs per-region 矛盾、K=2 異常）描繪出一個一致的 pattern——論文的 narrative 系統性地高於其實際技術內容。

**Negative reviewer 補充了兩個 Positive reviewer 忽略的重要問題**：核心假設未驗證 (C1) 和 training-inference discrepancy (T3)。這兩個問題進一步加深了對方法理解深度的疑慮。

**然而，兩位 reviewer 也一致認為方法的實際結果有價值**，且 Major 問題均可通過 revision 修正。核心分歧在於：Positive reviewer 認為修正後可接受，Negative reviewer 認為 narrative-reality gap 過大需要 resubmission。

**Chair judgment：本文實際的技術貢獻——image-level dynamic scale weighting with sparse selection——是有價值的增量改進，但論文的 framing 顯著高於實際。若作者重新校準敘事、移除虛假 contribution claim、補充缺失的實驗分析（multi-run variance、FLOPs data、detection framework specification），本文可在下一輪 revision 中達到可接受水準。**

**Recommendation: Major Revision (Revise and Resubmit)**
