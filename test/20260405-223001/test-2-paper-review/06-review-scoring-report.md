<!-- type: review-scoring-report | generated: 2026-04-05 -->

## 技術發展路徑

**前驅工作時間線：**

1. **VGGT (Wang et al., CVPR 2025):** 將相機參數、深度圖和點雲預測統一到單一前饋 transformer 中。建立了視覺幾何理解的 transformer 基線，但僅支援離線批次處理固定長度輸入。
2. **StreamVGGT (2025):** 將 VGGT 擴展至因果操作模式，通過累積所有已處理幀的 token 至 KV cache 實現串流推理。但 KV cache 隨序列長度線性增長 (O(T * P))，導致長序列時記憶體溢出。
3. **H2O / SnapKV (Zhang et al., NeurIPS 2023; Li et al., 2024):** 在語言模型中提出基於注意力權重的 KV cache 剪枝策略。這些方法需要完整注意力矩陣，與 FlashAttention 不相容。

**InfiniteVGGT 相對前驅工作的具體進展：** 解決了 StreamVGGT 遺留的記憶體無界增長問題，同時繞開了 H2O/SnapKV 依賴注意力矩陣的限制。具體方式是以 key 空間中的餘弦相似度替代注意力權重作為 token 重要性的代理指標，實現與 FlashAttention 相容的剪枝策略。

**前驅工作遺留的核心問題：** StreamVGGT 無法處理超過 GPU 記憶體容量的長序列；現有 KV cache 剪枝方法與高效注意力機制不相容。

## 各維度評分

### 問題有效性 (Problem Validity): 8/10

串流 3D 重建的記憶體可擴展性是自主系統和 AR 的實際瓶頸。StreamVGGT 在所有 Long3D 序列上因記憶體溢出而失敗（正面審稿人 S1 引用 Table 2），證實問題的真實性。FlashAttention-pruning 矛盾的定義清晰且可證偽。扣分原因：問題的範圍相對狹窄，專門針對 VGGT 架構的 KV cache 管理，而非串流 3D 理解的通用問題。

### 方法合理性 (Method Soundness): 6/10

三組件設計（錨點保留、餘弦相似度剪枝、逐層預算分配）直觀且易於理解。無需訓練是重要的實用優勢。然而，負面審稿人 W2 指出的問題是實質性的：餘弦相似度代理缺乏正式理論保證，其有效性依賴於查詢分佈（不同幀的查詢可能使同一對相似 key 的重要性截然不同）。論文未提供近似誤差的界限，未分析代理失效的場景，也未展示餘弦相似度排序與注意力權重排序的經驗相關性。逐層自適應分配的效益極為有限（Table 6: 準確度從 0.098 至 0.093，負面審稿人 W5），可能在噪聲範圍內。

### 實驗充分性 (Experimental Adequacy): 5/10

這是論文最薄弱的環節。負面審稿人 W1 識別的缺失基線問題是核心：Long3D 上缺少帶有簡單快取淘汰策略（FIFO、隨機、滑動窗口）的 StreamVGGT 作為對照組，無法區分「任何有界快取都優於無管理」與「餘弦相似度剪枝特別優越」。Table 2 的指標報告不對稱（負面審稿人 W7）：僅報告 InfiniteVGGT 的完整度和法線一致性，省略了 CUT3R 和 TTT3R 的對應數值。標準基準上的改進幅度小且無變異數報告（7-Scenes: 0.043 vs. 0.048; Bonn: 0.069 vs. 0.072）。Long3D 僅含五個場景，且為作者自行提出和評估，缺乏外部驗證（負面審稿人 W3）。

### 新穎性 (Novelty): 7/10

FlashAttention-pruning 矛盾的識別和餘弦相似度解法是有意義的概念貢獻。然而，各組件本身並非全新：token 剪枝在視覺 transformer 中已有廣泛研究（DynamicViT, Token Merging），餘弦相似度是基本的相似度度量。新穎性在於將這些已知工具組合應用於特定的 3D 視覺幾何場景，並識別出它們恰好能解決 FlashAttention 的相容性問題。這是應用層面的新穎性，而非方法論層面的根本突破。

### 可重現性 (Reproducibility): 7/10

論文提供了具體的超參數（B = 25,000 tokens per head, 溫度 = 1.0），基礎模型明確（StreamVGGT），且聲稱提供程式碼（github.com/AutoLab-SAI-SJTU/InfiniteVGGT）。無需訓練的特性降低了復現門檻。扣分原因：Long3D 基準的採集細節和標註管線未描述，使得基準本身難以獨立復現或驗證。逐層自適應預算的具體分配結果（各層實際獲得多少預算）未展示。

## 加權總分與等級

| 維度 | 分數 | 權重 | 加權分 |
|---|---|---|---|
| 問題有效性 (Problem Validity) | 8 | 0.15 | 1.20 |
| 方法合理性 (Method Soundness) | 6 | 0.30 | 1.80 |
| 實驗充分性 (Experimental Adequacy) | 5 | 0.30 | 1.50 |
| 新穎性 (Novelty) | 7 | 0.15 | 1.05 |
| 可重現性 (Reproducibility) | 7 | 0.10 | 0.70 |

**加權總分：6.25 / 10**

**等級：Weak Accept** (範圍 5.5 - 6.9)

加權總分 6.25 落在 Weak Accept 區間，與兩位審稿人的判斷一致（正面審稿人 Accept，負面審稿人 Weak Accept，綜合為 Weak Accept）。實驗充分性的 5 分是主要拉低因素：缺失的有界快取基線和不對稱的指標報告構成可修復但當前尚未解決的重大問題。方法合理性的 6 分反映了餘弦相似度代理缺乏理論保證的現實。問題有效性和新穎性的較高分數反映了該工作在概念層面的貢獻價值。

## Recommendation

**Weak Accept.** InfiniteVGGT 提出了一個有實際價值的概念貢獻（FlashAttention-pruning 矛盾及其解決方案），並展示了獨特的能力（以 14.49 GB 有界記憶體處理 9,545 幀序列）。然而，實驗評估的不完整性阻止了更高的評級。建議作者在修訂版中：(1) 補充帶有簡單快取淘汰策略的 StreamVGGT 作為 Long3D 基線；(2) 對標準基準結果增加變異數報告；(3) 提供 Long3D 的採集與標註細節以支持基準的獨立驗證。
