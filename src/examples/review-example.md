# Phyra Peer Review Example

> **用途**：本檔案為 `phyra-peer-reviewer-chair` agent 的格式與深度參考（gold standard）。
> Chair agent 在撰寫最終報告前應讀取此範例，確保輸出在結構、具體性、與評分邏輯上達到同等水準。
>
> **論文資訊（虛構）**：
> - Title: *Adaptive Feature Pyramid Networks for Multi-Scale Object Detection*
> - Authors: Wei-Lin Chen, Satoshi Nakamura, Priya Raghavan (2026)
> - Venue: Submitted to ECCV 2026
> - arXiv: 2602.14387 (fictitious)

---

## Report 1: peer-review-report.md

<!-- type: peer-review-report | generated: 2026-03-15 -->

### Summary

本文提出 Adaptive Feature Pyramid Network（AFPN），在傳統 FPN 的 lateral connection 上引入 channel-spatial gating mechanism，使不同 scale 的 feature map 能根據輸入影像動態調整融合權重。作者在 COCO val2017 上報告 AFPN 搭配 Faster R-CNN ResNet-50 backbone 達到 42.7 mAP（+1.9 over vanilla FPN），並在 VisDrone-DET 小物體場景取得 34.1 mAP（+2.6）。整體 idea 直覺且合理，實驗涵蓋多個 backbone 與偵測框架，但在 gating mechanism 的理論動機、消融實驗完整性、以及與近期 concurrent work 的比較上仍有明顯不足。

### Strengths

**S1. 問題定位精準且動機清晰**
Multi-scale feature fusion 的 scale mismatch 問題已被多篇文獻指出（e.g., PANet, NAS-FPN），但本文首次從 information-theoretic perspective 量化不同 level 之間的 mutual information loss（Section 3.1, Fig. 2），為後續設計提供了具說服力的出發點。

**S2. Gating mechanism 設計兼顧效率與表達力**
Channel-spatial dual gating 僅增加 0.8 GFLOPs（Table 3），相較 BiFPN 的 repeated top-down/bottom-up（+2.1 GFLOPs）更為輕量。作者同時提供了 latency benchmark（Table 5）：在 V100 上僅增加 1.2 ms/image，具備實用部署價值。

**S3. 跨框架泛化驗證充分**
AFPN 分別在 Faster R-CNN、RetinaNet、FCOS 三個框架上均展示一致的增益（Table 2），且在 ResNet-50/101 和 Swin-T 三種 backbone 上趨勢穩定，降低了 method 對特定架構的依賴疑慮。

**S4. 小物件偵測場景表現突出**
VisDrone-DET 結果（Table 6）顯示 AFPN 在 AP_small 上的增益（+3.8）遠大於 AP_large（+0.7），與作者宣稱的「adaptive fusion 在 scale gap 大時效果更顯著」假說一致，具正面佐證效果。

**S5. 視覺化分析具參考價值**
Fig. 5 的 gating weight heatmap 清楚展示 shallow level 在小物件區域被 upweight 的現象，Fig. 6 的 GradCAM 比較也直觀呈現 AFPN 較 FPN 更精確地聚焦於目標邊界。

### Weaknesses

**W1. [Major] Information-theoretic analysis 缺乏嚴謹推導**
Section 3.1 聲稱 lateral connection 造成 mutual information loss，但估計方式僅採用 MINE estimator 在單一 seed 下的結果，未報告 variance。已知 MINE 在高維空間下 estimation bias 顯著（Belghazi et al., 2018, Table 1 報告 >15% relative error on dim>256）。此缺陷直接削弱了 gating mechanism 的理論動機：若 MI loss 量級不穩定，則設計決策可能建立在噪聲上。
**建議修正方向**：改用 InfoNCE bound 或至少報告 5 seeds 的 mean/std；若 MI loss 量級在 confidence interval 內包含零，需重新論述動機。

**W2. [Major] 消融實驗缺少關鍵變體**
Table 4 的 ablation 僅比較 channel-only / spatial-only / dual gating，但缺少：(a) gating 替換為 SE-block 或 CBAM 的對比，(b) gating 位置（before vs. after lateral conv）的影響，(c) gating 在不同 FPN level 的 per-level contribution。缺少 (a) 使讀者無法判斷增益究竟來自 gating 架構本身還是一般性 attention 效果。
**建議修正方向**：補充 SE/CBAM drop-in replacement 實驗以及 per-level ablation。

**W3. [Major] 未與同期重要工作比較**
ECCV 2026 投稿截止前已公開的 DyFPN（arXiv 2601.09821）同樣採用 dynamic fusion weight，且在 COCO 上報告 43.1 mAP。本文完全未提及此 concurrent work。儘管 concurrent work 不一定需要勝過，但至少需要在 related work 中討論差異，否則審稿者無法評估 novelty margin。
**建議修正方向**：加入 DyFPN 的定性比較（設計差異）及定量比較（若可取得 code/checkpoint）。

**W4. [Minor] VisDrone 實驗設定描述不足**
Section 4.3 未說明 VisDrone 的 train/val split 版本（VisDrone 有 2019/2021 兩版），也未報告影像 resize 策略。鑒於 VisDrone 影像解析度差異極大（960x540 ~ 2000x1500），resize 策略對小物件 AP 影響顯著，缺少此資訊使結果難以復現。
**建議修正方向**：明確標註 dataset version、resize/crop 策略、及 multi-scale training 的詳細參數。

**W5. [Minor] Table 2 的 training schedule 不一致**
Faster R-CNN 結果使用 2x schedule，但 FCOS 使用 1x schedule（footnote 3）。不同 schedule 下 baseline 的飽和程度不同，可能導致 AFPN 增益的公平性存疑。
**建議修正方向**：統一使用 1x 和 2x 兩種 schedule，分別報告結果。

**W6. [Suggestion] 缺乏 failure case 分析**
現有視覺化僅展示成功案例。建議補充 AFPN gating 失效的場景（e.g., 極端遮擋、dense crowd），有助於讀者理解 method 的適用邊界。

### Overall Assessment

本文的核心貢獻（adaptive gating for FPN）在直覺上合理且實驗廣度值得肯定，但三個 Major weakness 形成了一個結構性問題：**理論動機（W1）→ 設計選擇（W2）→ 定位（W3）之間缺乏穩固的邏輯鏈**。

具體而言，若 W1 的 MI analysis 不可靠，則 gating 的設計便失去了 principled motivation，退化為 "yet another attention module"；W2 缺乏與 SE/CBAM 的對比進一步無法排除此疑慮；而 W3 的 concurrent work 恰好採用相似策略，使 novelty 主張更需要精確的差異論述。三者交互作用下，本文的核心 claim（"AFPN 提供了 principled and effective adaptive fusion"）目前證據不足。

然而，W1-W3 皆為可修正的實驗/論述缺失，並非根本性 flaw。若作者能在 revision 中補齊，本文有潛力成為 solid contribution。

### References

1. Belghazi, M.I. et al. (2018). *Mutual Information Neural Estimation*. ICML 2018. — 用於評估 W1 中 MINE estimator 的已知 limitation。
2. Ghiasi, G., Lin, T.-Y., & Le, Q.V. (2019). *NAS-FPN: Learning Scalable Feature Pyramid Architecture for Object Detection*. CVPR 2019. — FPN 架構搜索的代表性工作，作為本文 baseline 參考。
3. Hu, J., Shen, L., & Sun, G. (2018). *Squeeze-and-Excitation Networks*. CVPR 2018. — W2 中建議的 attention baseline。

---

## Report 2: review-scoring-report.md

<!-- type: review-scoring-report | generated: 2026-03-15 -->

### 技術發展路徑

**[2017] FPN (Lin et al., CVPR 2017)**
首次提出 top-down pathway + lateral connections 實現多尺度 feature fusion。核心限制：所有 scale 使用相同的 1x1 conv 融合，無法根據輸入自適應調整不同 level 的貢獻比重。

**[2018] PANet (Liu et al., CVPR 2018)**
在 FPN 的 top-down pathway 之上增加 bottom-up path augmentation，緩解了淺層 high-resolution feature 在深層被稀釋的問題。核心限制：融合路徑仍為固定拓撲，feature 的重要性權重由架構隱式決定，無法根據不同影像的 scale distribution 動態調整。

**[2020] BiFPN (Tan et al., CVPR 2020)**
引入 weighted bi-directional cross-scale connections 與 learnable fusion weights，首次在 FPN 系列中實現 per-connection 的重要性學習。核心限制：fusion weight 為 input-independent 的 scalar parameter，在 training 完成後即固定，無法 handle inference 時 scale distribution 的 instance-level 變異。

**[2026] AFPN (Chen et al., 本文)**
提出 channel-spatial gating mechanism，使 fusion weight 成為 input-dependent function，實現 instance-level adaptive fusion。核心限制（由本次 review 揭示）：adaptive 機制的理論動機（MI analysis）與 attention baseline 比較皆不足，尚無法確認增益來源。

### 各維度評分

| 維度 | 分數 | 評分依據 |
|------|------|----------|
| **Novelty（新穎性）** | 6/10 | Gating mechanism 的個別組件（channel attention, spatial attention）皆為已知技術，novelty 主要在於「將其整合進 FPN lateral connection」的特定位置選擇。與 concurrent DyFPN 的差異未被釐清，進一步壓縮 novelty space。 |
| **Soundness（技術正確性）** | 5/10 | 實驗結果本身可信（多框架/多 backbone 驗證），但 MI-based 理論分析的可靠性存疑（MINE single seed），且消融缺少關鍵 attention baseline 對比，使 "why it works" 的論證鏈不完整。 |
| **Significance（影響力）** | 7/10 | Multi-scale detection 是高影響力問題，且方法具備低開銷（+0.8 GFLOPs）的實用優勢。VisDrone 上的小物件增益（+3.8 AP_small）若可復現，對 drone/surveillance 應用有直接價值。 |
| **Clarity（寫作品質）** | 7/10 | 整體結構清晰，Fig. 1 的架構圖與 Fig. 5 的 gating heatmap 具說明力。主要扣分在於 VisDrone 實驗設定描述不足以及 training schedule 不一致未被充分解釋。 |
| **Reproducibility（可復現性）** | 5/10 | 未提供 code（僅承諾 upon acceptance 釋出），VisDrone split 版本未標註，且 MI estimation 的 hyperparameter（MINE network architecture, learning rate）未完整列出。 |

### 加權總分與等級

| 維度 | 權重 | 分數 | 加權分 |
|------|------|------|--------|
| Novelty | 0.25 | 6 | 1.50 |
| Soundness | 0.25 | 5 | 1.25 |
| Significance | 0.20 | 7 | 1.40 |
| Clarity | 0.15 | 7 | 1.05 |
| Reproducibility | 0.15 | 5 | 0.75 |
| **加權總分** | **1.00** | | **5.95** |

**等級對照**：
- 8.0-10.0：Strong Accept
- 6.5-7.9：Weak Accept
- 5.0-6.4：Borderline / Weak Reject
- 3.0-4.9：Reject
- 1.0-2.9：Strong Reject

**本文等級：Borderline / Weak Reject（5.95）**

### Recommendation

**Recommendation: Revise and Resubmit**

本文處於 borderline 區間，核心 idea 具實用價值但論證鏈不完整。具體而言：

1. **必要修正（gate to acceptance）**：補齊 MI analysis 的 robustness 驗證（W1）、SE/CBAM attention baseline 對比（W2）、以及 DyFPN concurrent work 討論（W3）。這三項修正若完成且結果正面，預計可將 Soundness 提升至 7、Novelty 提升至 7，總分達 6.75（Weak Accept）。

2. **建議修正（strengthen further）**：統一 training schedule（W5）、補充 failure case 分析（W6）、完善 VisDrone 實驗設定描述（W4）。

3. **整體判斷**：本文不適合以目前狀態直接接受，但核心構想與實驗規模值得鼓勵。建議作者以 2-3 週時間補齊上述實驗後重新投稿，或投稿至同級會議的下一輪 deadline。
