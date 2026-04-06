<!-- type: paper-read-notes | generated: 2026-04-05 -->

## 1. 基本資訊

| 項目 | 內容 |
|------|------|
| 論文簡稱 | InfiniteVGGT |
| 論文全稱 | InfiniteVGGT: Visual Geometry Grounded Transformer for Endless Streams |
| arXiv ID | 2601.02281 |
| PDF 文件路徑 | /home/nubo/workspace/Phyra/test/20260405-223001/inputs/sample-paper.md |
| 釋出日期 | January 2026 |
| 發表會議/期刊 | arXiv preprint (未註明會議) |
| 論文連結 | arxiv.org/abs/2601.02281 |
| 程式碼連結 | github.com/AutoLab-SAI-SJTU/InfiniteVGGT |
| 項目主頁 | 未提供 |

### 1.1 作者資訊

| 作者姓名 | 單位機構 | 是否通訊作者 |
|---------|---------|-------------|
| Shuai Yuan | AutoLab, Shanghai Jiao Tong University | 未標註 |
| Yantai Yang | AutoLab, Shanghai Jiao Tong University | 未標註 |
| Xiaotian Yang | AutoLab, Shanghai Jiao Tong University | 未標註 |
| Xupeng Zhang | AutoLab, Shanghai Jiao Tong University | 未標註 |
| Zhonghao Zhao | AutoLab, Shanghai Jiao Tong University | 未標註 |
| Lingming Zhang | AutoLab, Shanghai Jiao Tong University | 未標註 |
| Zhipeng Zhang | AutoLab, Shanghai Jiao Tong University | 未標註 |

### 1.2 關鍵詞

3D Reconstruction, Streaming Vision, KV Cache Compression, Visual Geometry Transformer, Rolling Memory, Token Pruning, Long-Sequence Evaluation

## 2. 研究概述

### 2.1 研究主題

InfiniteVGGT 在 StreamVGGT 基礎上引入基於餘弦相似度的 KV cache 修剪策略，實現有界記憶體下的無限長序列因果 3D 幾何重建。

### 2.2 研究領域分類

3D Reconstruction / Streaming Vision / Efficient Transformer / KV Cache Management

### 2.3 所使用的核心架構

- **VGGT / StreamVGGT:** 基礎視覺幾何 Transformer，提供相機參數、深度圖和點雲的端到端預測
- **Rolling Memory (KV Cache):** 固定預算的 KV cache，通過多樣性感知修剪維持資訊量

## 3. 論文評價

### 3.1 影響程度評級

| 評分維度 | 分數（1-5）| 說明（必填，不得空白）|
|---------|-----------|----------------------|
| 創新性 | 4 | 用餘弦相似度替代注意力權重作為 token 重要性代理，解決了 FlashAttention 與修剪之間的真實矛盾 |
| 技術深度 | 3 | 三個組件各自簡潔，組合邏輯清晰，但單個組件的技術複雜度有限 |
| 實驗完整度 | 4 | 覆蓋標準基準、長序列基準、深度估計、消融實驗四個維度，Long3D 是有價值的新貢獻 |
| 寫作質量 | 4 | 問題動機清晰，FlashAttention 悖論的敘述有力，結構完整 |
| 實用價值 | 5 | 無需訓練、記憶體有界、常數每幀時間，可直接部署在現有 StreamVGGT checkpoint 上 |
| 綜合評分 | 4 | 工程導向的扎實工作，解決了一個真實且重要的系統瓶頸 |

### 3.2 論文亮點

- FlashAttention-pruning 矛盾的識別和解決方案在概念上清晰且實用（Section 1, 3.2）
- 無需訓練即可部署，降低了採用門檻（Section 3.3）
- Long3D 基準填補了長序列 3D 幾何評估的空白，最長序列達 9,545 幀（Section 4.2, Table 2）
- 餘弦相似度修剪在降低 42% 延遲的同時改善了重建品質（Table 4: 0.168 vs. 0.288 s/frame）

### 3.3 論文不足

- Completion 指標表現不佳，作者承認但未提供機制性解釋（Conclusion）
- 錨定幀假設脆弱：若首幀品質差或不具代表性，整個座標系受影響，缺乏魯棒性分析（Section 3.2）
- 所有基準均為室內場景，"infinite-horizon" 的泛化性聲稱缺乏室外或混合場景驗證（Section 4）
- 預算飽和分析（Table 5）僅為經驗觀察，缺乏理論解釋

## 4. 問題與動機

### 4.1 故事線（Introduction 脈絡）

持續 3D 幾何理解對自主系統和 AR 至關重要。VGGT 展示了單一 Transformer 可預測相機參數、深度和點雲，但受限於固定長度批處理。StreamVGGT 實現了因果操作但 KV cache 線性增長導致記憶體溢出。InfiniteVGGT 通過以餘弦相似度替代注意力權重的修剪策略，在有界記憶體下實現無限長序列處理。

### 4.2 現有方法的痛點/局限性

| 痛點 | 具體描述 | 影響 |
|-----|---------|------|
| VGGT 無法流式處理 | 固定批次輸入，不支援即時操作 | 排除所有即時應用場景 |
| StreamVGGT 記憶體無界 | KV cache 以 O(T*P) 增長 | 長序列必然 OOM（Long3D 全部失敗，Table 2） |
| FlashAttention 與修剪衝突 | 高效核心避免物化注意力矩陣，但修剪需要注意力權重 | 無法在保持效率的同時智能壓縮 cache |
| 現有方法的漂移問題 | 流式架構在長序列上出現災難性漂移 | TTT3R 在 9,545 幀上誤差達 8.921（Table 2） |

### 4.3 本文提出的核心觀點

作者認為 FlashAttention-pruning 矛盾是流式 3D 理解的根本瓶頸。他們的核心洞察是：歷史上相似的幀會從查詢 token 獲得幾乎相同的注意力權重，因此 key 空間中的餘弦相似度可以作為注意力重要性的代理指標，從而在不物化注意力矩陣的前提下識別冗餘 token。

## 5. 方法論

### 5.1 方法概述

InfiniteVGGT 在 StreamVGGT 的推理階段引入三個協同機制：不可變錨定 token 保持座標參考，多樣性感知修剪保留資訊量最大的 token，層自適應預算分配根據各層資訊多樣性分配非均勻儲存。

### 5.2 整體框架圖（文字版）

```
[新幀 Tokens] → [追加到 KV Cache] → [錨定幀保留（首幀完整保存）]
                                   → [候選 Token 池]
                                   → [計算 L2-normalized key 均值]
                                   → [負餘弦相似度評分]
                                   → [層自適應預算 Softmax 分配]
                                   → [TopK 選擇 → 壓縮後 KV Cache]
                                   → [FlashAttention 推理 → 輸出]
```

### 5.3 核心模塊詳解

#### 5.3.1 不可變錨定 Token

**功能：** 永久保留首幀的完整 KV cache 作為全局座標參考

**輸入：**
- 名稱：首幀 KV cache
- 形狀：論文未明確披露具體維度
- 來源：VGGT 對第一幀的編碼

**輸出：**
- 名稱：錨定 KV 對
- 形狀：與首幀 patch token 數量相同
- 用途：在每次注意力計算中作為固定前綴

**處理過程：**
首幀處理後，其 KV cache 被標記為不可修剪。在後續所有幀的推理中，錨定 token 始終參與注意力計算但不計入修剪預算。

**關鍵公式（如有）：**
無獨立公式。設計基於 VGGT 以首幀作為規範座標系的特性。

**實現細節（如論文有披露）：**
移除錨定後準確度下降 14.9%（Table 7: 0.047 vs. 0.040），NC 不受影響。

#### 5.3.2 多樣性量化 Token 保留

**功能：** 通過 key 空間餘弦相似度識別並移除冗餘 token

**輸入：**
- 名稱：候選 key 集合（排除錨定 token）
- 形狀：每層每頭的 key 向量集合
- 來源：當前累積 KV cache

**輸出：**
- 名稱：保留的 token 索引
- 形狀：每層每頭 B^l 個 token
- 用途：構成壓縮後的 KV cache

**處理過程：**
1. 對候選 key 進行 L2 正規化
2. 計算正規化 key 的均值向量 $\mu^{(l,h)}$
3. 計算每個 token 與均值的負餘弦相似度作為多樣性分數
4. 通過 TopK 選擇保留多樣性最高的 token

**關鍵公式：**
$$s_{\text{div}}^{(l,h)}(\hat{k}_i) = -\text{CosSim}(\mu^{(l,h)}, \hat{k}_i)$$

#### 5.3.3 層自適應預算分配

**功能：** 根據各層資訊多樣性分配非均勻儲存預算

**輸入：**
- 名稱：各層多樣性分數統計量
- 來源：5.3.2 的多樣性評分過程

**輸出：**
- 名稱：各層預算 $B^l$
- 用途：控制 5.3.2 中 TopK 的 K 值

**處理過程：**
對各層多樣性分數取均值後通過帶溫度的 Softmax 轉換為預算比例，再乘以總預算得到各層配額。

**關鍵公式：**
$$p_{\text{bud}}^l = \frac{\exp(s_{\text{div}}^l / \tau)}{\sum_j \exp(s_{\text{div}}^j / \tau)}, \quad B^l = p_{\text{bud}}^l \cdot B_{\text{total}}$$

**實現細節：**
$B_{\text{total}} = 25{,}000$ tokens per head, $\tau = 1.0$。淺層展現較高多樣性（捕捉幀間細微差異），早期和深層多樣性較低。層自適應分配相較均勻分配在準確度上改善 5.1%（Table 6: 0.093 vs. 0.098）。

## 6. 實驗

### 6.1 數據集

| 數據集 | 任務 | 規模 | 用途 |
|-------|------|------|------|
| 7-Scenes | 室內 3D 重建 | 300-500 幀（stride=2） | 測試 |
| NRGBD | 多樣室內 3D 重建 | 未明確 | 測試 |
| Long3D (新) | 長序列 3D 重建 | 5 場景, 2,128-9,545 幀 | 測試 |
| Bonn | 視頻深度估計 | 500 幀 | 測試 |

### 6.2 評測指標

| 指標 | 說明 | 是否主要指標 |
|------|------|------------|
| Accuracy (Acc.) | 重建點到真值的距離 | 是 |
| Completion (Comp.) | 真值到重建點的距離 | 是 |
| Normal Consistency (NC) | 法向量一致性 | 是 |
| Chamfer Distance (CD) | Acc. + Comp. 的綜合 | 是（消融實驗用） |
| Abs Rel | 深度估計的相對絕對誤差 | 是（深度任務） |
| $\delta < 1.25$ | 深度估計的閾值精度 | 是（深度任務） |

### 6.3 主實驗結果

**7-Scenes & NRGBD (Table 1):**

| 方法 | 7S Acc. (mean) | 7S Acc. (med) | NRGBD Acc. (mean) | NRGBD NC (mean) |
|------|----------------|---------------|--------------------|--------------------|
| InfiniteVGGT | 0.043 | 0.018 | 0.080 | 0.561 |
| StreamVGGT | 0.048 | 0.020 | 0.092 | 0.558 |
| CUT3R | 0.058 | 0.025 | 0.112 | 0.541 |
| TTT3R | 0.062 | 0.027 | 0.165 | 0.553 |

**Long3D (Table 2):** InfiniteVGGT 處理所有序列（峰值 14.49 GB），StreamVGGT 全部 OOM。最長序列（9,545 幀）上 TTT3R 誤差 8.921，InfiniteVGGT 為 5.733。

### 6.4 消融實驗

四組消融覆蓋了核心設計選擇：

- **修剪策略（Table 4）:** 餘弦相似度 vs. 注意力權重。餘弦相似度在 CD、延遲、記憶體三個維度全面勝出。回答了「為什麼不直接用注意力權重」的問題。
- **預算大小（Table 5）:** B 從 10,000 到 30,000。B=25,000 處出現飽和，但缺乏場景類型間的交叉驗證。
- **層自適應分配（Table 6）:** 自適應 vs. 均勻。改善幅度不大（Acc. 0.093 vs. 0.098），但方向正確。
- **錨定幀（Table 7）:** 有 vs. 無。14.9% 的準確度改善證實了首幀座標系保持的必要性。

### 6.5 Phyra 對實驗的評估

- 消融實驗覆蓋了所有三個核心組件，每個消融回答了明確的設計問題
- 缺失項：（1）首幀品質對錨定策略的影響分析；（2）室外場景驗證；（3）預算飽和值在不同場景類型間的穩定性
- Baseline 選擇合理（CUT3R, TTT3R, Point3R, StreamVGGT），涵蓋了 2025-2026 年的主要競爭方法
- Long3D 基準的引入使實驗評估有獨特價值，但該基準尚未經過第三方獨立驗證

## 7. Phyra 的判斷

### 7.1 實際貢獻 vs. 聲稱貢獻

- **「無界記憶體架構」:** 支撐充分。Long3D 結果（Table 2）確認了在 9,545 幀上以 14.49 GB 峰值完成重建，StreamVGGT 全部 OOM。
- **「長序列基準上的 SOTA」:** 支撐充分。Tables 1-3 在所有測試基準上均為最佳（準確度維度）。但 Completion 指標並非全面最佳，聲稱需要限定為「準確度維度的 SOTA」。
- **「Long3D 基準」:** 支撐充分（待公開發布驗證）。5 場景、最長 9,545 幀，確實填補了評估空白。

### 7.2 方法的本質限制

- **首幀依賴：** 整個座標系錨定在第一幀上。若第一幀退化（運動模糊、遮擋），所有後續幀的座標系都會受影響。這不是未來工作可以修補的問題，而是架構的結構性約束。
- **場景記憶遺忘：** 固定預算意味著隨著序列增長，早期場景的細節必然被丟棄。對於需要回訪（loop closure）的場景，這構成根本限制。
- **離線-在線品質差距：** 即使在短序列上（Table 1），InfiniteVGGT 的品質仍然低於離線方法可達到的理論上限。有界記憶體的代價是不可消除的。

### 7.3 值得追蹤的引用

- **VGGT [5]:** CVPR 2025 Best Paper，InfiniteVGGT 的基礎架構。必讀，理解端到端幾何 Transformer 的設計。
- **H2O [15]:** NeurIPS 2023，KV cache 修剪的先驅工作（基於注意力權重）。理解 InfiniteVGGT 所替代的基線方法。
- **SnapKV [16]:** LLM 中的 KV cache 壓縮。與 InfiniteVGGT 的方法論形成對比（注意力 vs. 相似度）。
- **TTT3R [8]:** 測試時訓練的替代路線。理解為什麼 InfiniteVGGT 的無訓練路線在長序列上更穩定。
- **DUSt3R [3]:** CVPR 2024，pointmap regression 的開創工作。理解 VGGT 系列的技術起源。

## 8. 開放問題與改進想法

### 8.1 存在的疑問

- [ ] 錨定幀策略在首幀品質不佳時的退化行為是什麼？是否可以動態更新錨定幀？
- [ ] Completion 指標的下降是否源自多樣性修剪偏好保留幾何邊界 token 而丟棄填充區域的 token？
- [ ] 層自適應預算的改善幅度較小（Table 6），是否存在更有效的預算分配策略？
- [ ] 25,000 的預算飽和值在室外場景或動態場景中是否仍然適用？

### 8.2 改進方向

- **動態錨定更新：** 在檢測到座標系漂移時，用最新的高品質幀替換部分錨定 token。需要定義漂移檢測指標，可行性中等。
- **分層記憶池：** 將 KV cache 分為近期（高解析度）和遠期（壓縮）兩個池，類似 CPU cache 層次結構。可改善 loop closure 能力，但增加了系統複雜度。
- **室外場景驗證：** 在 KITTI、Waymo 等駕駛數據集上測試，驗證方法的場景泛化性。實施成本低，應優先執行。
- **Token 合併替代修剪：** 將冗餘 token 合併而非丟棄，可能改善 Completion 指標。需要驗證合併操作是否保持 FlashAttention 兼容性。
