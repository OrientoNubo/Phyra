# Peer Review Draft: Critical (Negative Reviewer)

<!-- type: review-negative | generated: 2026-04-04 -->
<!-- paper: Efficient Multi-Scale Feature Aggregation for Real-Time Object Detection -->

## Summary

本文提出 LAFA，用 learned routing function 替代 FPN 中固定的 cross-scale fusion，聲稱在 COCO val2017 上以 R-50 backbone 達到 48.3 mAP / 42 FPS。以下 review 追溯論文中技術聲稱、方法設計與實驗設計的根本問題。

## Defect Analysis

### Technical Defects

**T1. [Major] 核心聲稱「per-region routing」與實際實作之間存在根本矛盾**

論文在 Abstract（"dynamically selects which scale combinations to fuse for each spatial region"）、Introduction（"per-region routing decisions"）、以及 Contribution #1 中反覆強調 routing 是 per-region 的。然而 S3.2 明確描述 routing network 使用 Global Average Pooling，這將空間維度完全消除，產生的 routing weight 是 per-image 的 scalar set，不包含任何空間位置資訊。

這不是措辭問題，而是技術聲稱與實作的不一致。若 routing 是 per-image 的，那麼論文的核心動機——「不同空間區域需要不同的 scale combination」——在方法層面並未被實現。LAFA 在此情況下退化為一個 image-level dynamic weighting scheme，其與 BiFPN 的 learnable scalar weight 的本質差異僅在於 weight 是 input-dependent 的，而非 per-region adaptive 的。

**T2. [Major] "Theoretical analysis" 貢獻不存在**

Contribution #2 聲稱提供了理論分析。Section 3 中不存在任何定理、引理、bound 或形式化推導。將一個方法的數學符號描述稱為 "theoretical analysis" 是對該術語的誤用。公式 $O_i = \sum_{j \in S_i} R_{ij}(P_i) \cdot \text{Align}(P_j, P_i)$ 是方法定義，不是理論結果。

這直接使三項貢獻之一無效。

**T3. [Major] Gumbel-Softmax training 與 hard top-K inference 的 discrepancy 未被分析**

Training 階段使用 Gumbel-Softmax 產生的是所有 scale 的 soft weighted combination（所有 scale 都有非零權重）。Inference 階段使用 hard top-K 將 K scale 以外的權重設為零。這意味著 model 從未在 training 中看到 inference 時的 actual computation graph。

在 knowledge distillation 和 pruning 文獻中，training-inference discrepancy 是已知的性能退化來源。論文未報告 soft inference（使用 Gumbel-Softmax 的 softmax output 而非 hard top-K）的性能，也未分析 discrepancy 的量級。

**T4. [Minor] FLOPs reduction 的 40% 數字來源不透明**

Abstract 聲稱「reducing redundant cross-scale interactions by approximately 40%」，S3.2 提到「This achieves the 40% FLOPs reduction reported in our experiments」。但 Section 4 中不存在任何 FLOPs 數據表。40% 的數字未被任何實驗數據直接支撐。

### Presentation Defects

**P1. [Major] Detection framework 在 main results 中未指明**

Table 1 比較了 FPN、PANet、BiFPN、NAS-FPN 與 LAFA，但未說明使用何種 detector（Faster R-CNN、RetinaNet、FCOS 等）。FPN 原始論文使用 Faster R-CNN；EfficientDet/BiFPN 使用自定義 detector head；NAS-FPN 的數字取決於搭配的 detector。若各 baseline 的數字取自不同的 detector 設定，則比較不成立。

若所有方法使用相同 detector，為何不標註？若使用不同 detector，則比較本身有問題。無論哪種情況，缺少此資訊都是 presentation 層面的重大缺失。

**P2. [Minor] Table 1 中 baseline 數字的來源不清**

FPN 在 R-50 上的 44.2 mAP 數字高於多數公開 benchmark 的報告值（通常在 37-42 之間，取決於 detector 和 training schedule）。若使用了特定的 re-implementation，需要說明 re-implementation 細節。若直接引用原論文數字，需要確保實驗設定（training schedule、image size、augmentation）完全一致。

**P3. [Minor] Related work 缺少 2024-2026 年的關鍵工作**

論文引用的最新工作是 RT-DETR (CVPR 2024)。2024-2026 年間，dynamic feature fusion 領域有持續發展。論文未引用或討論任何 2025-2026 年的相關工作，使讀者難以判斷 LAFA 相對當前 state-of-the-art 的定位。

### Conceptual Defects

**C1. [Major] 「不同區域需要不同 scale combination」的前提假設未被驗證**

整篇論文的動機建立在一個未驗證的假設上：在標準 FPN 中，不同空間區域確實需要不同的 scale combination，而非全部接收相同的 multi-scale fusion。作者在 Introduction 中以直覺論述（large objects 不需要 multi-scale fusion），但未提供任何實證。

合理的驗證方式包括：(a) 在 trained FPN 上分析不同區域的 feature utilization pattern；(b) oracle experiment 證明 per-region optimal scale selection 確實優於 uniform selection。論文兩者皆未提供。

**C2. [Minor] Sparse selection 優於 dense 的解釋缺失暗示作者可能不完全理解自己方法的工作原理**

K=2 sparse (48.3) 優於 dense (47.9) 是一個需要解釋的現象。作者僅將其描述為「best accuracy-efficiency tradeoff」，但 tradeoff 暗示 accuracy 和 efficiency 之間的取捨，而此處 accuracy 和 efficiency 同時改善。作者似乎未意識到這是一個需要解釋的異常，這引發對作者是否深入理解 routing mechanism 行為的疑慮。

## Overall Assessment

本文有三個互相關聯的結構性問題：

1. **核心聲稱與實作不符**（T1）：論文反覆聲稱 per-region routing，但實際 routing network 是 per-image 的。這不僅是措辭問題，而是動機與方法之間的斷裂。

2. **貢獻虛報**（T2）：三項聲稱貢獻中，第二項（theoretical analysis）在論文中不存在。

3. **核心假設未驗證**（C1）：「不同區域需要不同 scale combination」是整篇論文的出發點，但從未被驗證。

這三個問題的交互作用構成一個一致的 pattern：論文的 narrative（per-region adaptive routing based on theoretically motivated sparse selection）與論文實際展示的內容（image-level dynamic weighting with empirically tuned top-K）之間存在系統性的落差。

然而，必須承認，論文實際展示的 image-level dynamic weighting 本身可能是有價值的——48.3 mAP / 42 FPS 的結果若可復現，確實優於 BiFPN。問題在於論文將一個相對簡單的方法包裝為一個更宏大的敘事，而這個敘事在多個層面上不成立。

**Preliminary recommendation: Weak Reject**

若作者願意重新校準敘事（承認是 image-level dynamic weighting 而非 per-region routing）、移除虛假的 theoretical analysis 貢獻聲稱、並補充 T3/C1 的分析，本文仍有重投的可能。但目前版本的 narrative-reality gap 過大。
