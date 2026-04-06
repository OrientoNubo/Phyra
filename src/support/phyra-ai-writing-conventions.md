# Phyra AI Writing Conventions — 領域寫作慣例參考

> 本文件為 Phyra 學術寫作插件的領域慣例參考，由 `phyra-paper-writing` skill 引用。
> 涵蓋 CV、NLP、ML、Multimodal 四大領域及跨領域通用慣例。

---

## 1. Computer Vision (CV) — CVPR / ICCV / ECCV Style

### 1.1 Section Ordering

典型結構（最常見排列）：

```
1. Introduction
2. Related Work          ← 部分作者會移至 Method 之後
3. Method / Approach
4. Experiments
5. Conclusion
```

- CVPR 近年趨勢：Related Work 放在 Method 之後，以便讀者先理解本文方法再看定位。
- ECCV 偏向傳統順序（Related Work 緊接 Introduction）。

### 1.2 Citation Density

- 一般預期 **30–60 篇參考文獻**。
- 過少（<20）會被質疑 survey 不足；過多（>80）可能被認為灌水。
- Related Work 中每段應聚焦一個 sub-topic，每段引用 3–8 篇。

### 1.3 Figure Conventions

| 位置 | 用途 | 說明 |
|------|------|------|
| Figure 1 | **Teaser figure** | 全文最重要的一張圖，需一眼傳達核心想法 |
| Figure 2–3 | Architecture / pipeline diagram | 方法主圖，通常包含模組名稱與資料流箭頭 |
| 後續 figures | Qualitative comparisons | 與 baseline 的視覺比較，需標註方法名稱 |

- 圖片解析度建議 ≥ 300 dpi；向量圖（PDF/SVG）優先。
- Qualitative comparison 中，用紅色框或箭頭標示差異區域。

### 1.4 Table Conventions

- **粗體（Bold）** 標示最佳結果，**底線（Underline）** 標示次佳。
- 表格標題（caption）放在表格上方。
- 欄位對齊：數值靠右或置中，方法名稱靠左。
- 若結果差異在統計誤差範圍內，應加註標準差（±）。

### 1.5 Abstract Length

- 目標 **150–250 words**。CVPR/ICCV 模板無硬性限制但超過 250 words 會顯得冗長。
- 結構：問題 → 洞察 → 方法概述 → 關鍵結果數字。

### 1.6 常見應避免用語

- ❌ "In recent years, X has attracted increasing attention..."（陳腔濫調）
- ❌ "To the best of our knowledge, this is the first..."（除非確實如此且可驗證）
- ❌ "We propose a novel..."（在 abstract 第一句；reviewer 會翻白眼）
- ✅ 直接陳述問題與解法，不加不必要的修飾。

---

## 2. NLP — ACL / EMNLP / NAACL Style

### 2.1 Section Ordering

```
1. Introduction
2. Related Work          ← NLP 社群強烈傾向放在 Intro 之後
3. Background / Preliminaries（視需要）
4. Method
5. Experimental Setup
6. Results and Analysis
7. Limitations           ← ACL 2023 起為必要章節
8. Ethics Statement      ← ACL venues 要求
9. Conclusion
```

### 2.2 Ethics Statement

- ACL、EMNLP、NAACL 均要求附上 Ethics Statement。
- 內容涵蓋：資料來源合法性、標註者待遇、潛在社會影響、偏見風險。
- 長度通常 0.5–1 頁，不計入正文頁數限制。

### 2.3 Reproducibility Checklist

- ACL 系列會議要求填寫 reproducibility checklist（隨 submission 提交）。
- 論文中應明確列出：超參數、訓練時間、硬體規格、隨機種子數量。
- 建議在 Appendix 提供完整實驗設定表。

### 2.4 Citation Density

- NLP 論文引用量通常較高：**40–80 篇**。
- 原因：NLP 子領域眾多（parsing、generation、QA、summarization...），需廣泛定位。
- Pre-trained model 相關論文（BERT、GPT 系列等）幾乎是必引。

### 2.5 Limitations Section

- **ACL 2023 起為強制要求**，缺少此節可能被 desk-reject。
- 應誠實討論：方法的適用範圍、資料集的偏限、評估指標的不足。
- 不要寫成自我辯護；reviewer 期望看到真正的反思。

---

## 3. Machine Learning — NeurIPS / ICML / ICLR Style

### 3.1 Theoretical vs. Empirical Paper Conventions

**理論型論文（Theory paper）：**
- 主定理應在正文中完整陳述，證明可放 Appendix。
- 需提供 proof sketch 於正文中，讓 reviewer 能快速理解證明思路。
- Assumption 應編號並集中列出，方便查閱。

**實驗型論文（Empirical paper）：**
- 需在多個 dataset / benchmark 上驗證。
- Ablation study 為基本要求（見 §5.3）。
- 計算成本分析（FLOPs、GPU hours）越來越被重視。

### 3.2 Appendix Conventions

- NeurIPS 允許不限長度的 Appendix（但 reviewer 不保證閱讀）。
- 常見 Appendix 內容：
  - 完整證明（Proofs）
  - 額外實驗結果（Additional experiments）
  - 超參數搜索細節（Hyperparameter search details）
  - Dataset 詳細資訊
- 正文應自成完整論述，Appendix 僅作補充。

### 3.3 Anonymous Submission Formatting

- **雙盲審查**：不得出現作者名稱、所屬機構。
- 自引時使用第三人稱："Previous work [XX] showed..." 而非 "Our previous work..."
- GitHub repo 連結：使用 anonymous repo（如 Anonymous GitHub）或標註 "will be released upon acceptance"。
- 致謝（Acknowledgements）在審查期間應移除。

### 3.4 Broader Impact Statement

- NeurIPS 自 2020 起要求 Broader Impact 或 Ethics statement。
- ICML / ICLR 目前無強制要求，但附上有加分效果。
- 應討論：正面社會影響、潛在負面影響、緩解措施。

---

## 4. Multimodal — 跨會議慣例

### 4.1 Demo / Visualization Expectations

- Multimodal 論文的 qualitative results 極為重要，reviewer 期望看到豐富的視覺化。
- 常見展示格式：
  - Image-text pairs 的 attention map 視覺化
  - 生成結果的 grid comparison（行 = 不同方法，列 = 不同 sample）
  - Video 相關工作需附 supplementary video 或提供連結

### 4.2 Multi-Dataset Evaluation Norms

- 至少在 **3 個以上** 不同 dataset 上進行評估。
- 涵蓋不同的 data distribution 與 task complexity。
- Cross-modal retrieval 論文常用：Flickr30k、COCO、CC3M 等。
- 如果僅在單一 dataset 上實驗，需充分解釋原因（如該任務僅存在一個公認 benchmark）。

### 4.3 Supplementary Material

- 強烈建議提供 supplementary material（PDF + video）。
- PDF 補充材料中放 additional qualitative results 與 failure cases。
- Failure case analysis 在 multimodal 論文中特別受歡迎。

---

## 5. 跨領域通用慣例

### 5.1 Related Work 寫法

**正確定位法（Positioning, not listing）：**
- 每段以 sub-topic 為主題，先概述該方向的發展脈絡，再說明本文的區別。
- 結構：前人做了 A → 但存在問題 B → 本文從 C 角度解決。
- 避免逐篇流水帳式列舉（"X did ..., Y did ..., Z did ..."）。

**分段策略：**
- 按技術主題分段，非按時間順序。
- 每段末尾應有一句話點明本文與該方向的關係或差異。

### 5.2 Contribution 陳述

- 列點式（bulleted list）為最常見格式，通常 3–4 點。
- 禁止使用自吹形容詞：comprehensive、extensive、thorough、significant。
- 每一點應具體且可驗證，例如："在 X benchmark 上達到 Y% 的提升" 而非 "大幅提升性能"。

### 5.3 Ablation Study 呈現

- 目的：驗證各設計選擇的貢獻，不是展示你做了很多實驗。
- 標準格式：固定其他元件，每次移除/替換一個元件。
- Table 應清楚標示 baseline（Full model）與各 variant 的差異。
- 建議以 **增量方式** 呈現（逐步加入元件）或 **消融方式**（逐步移除），擇一即可。

### 5.4 Figure / Table 編號與引用

- 所有 figure 和 table 必須在正文中被引用（"as shown in Figure 3"）。
- 首次引用應在 figure/table 出現之前或同一頁。
- LaTeX 中使用 `\ref{}` 而非手動編號，避免編號錯位。
- Figure caption 應能獨立閱讀（self-contained），不需回到正文即可理解圖意。
- Table caption 放在表格**上方**，Figure caption 放在圖片**下方**。

### 5.5 Notation Consistency

- 在 Method section 開頭或 Preliminaries 中定義所有符號。
- 向量用粗體小寫（**x**），矩陣用粗體大寫（**X**），純量用斜體（*x*）。
- 同一符號在全文中意義不得改變。
- 下標慣例保持一致（如 $x_i$ 表示第 $i$ 個 sample，$x^{(t)}$ 表示第 $t$ 個 iteration）。
- 數學符號首次出現時必須定義，不可假設讀者已知。

### 5.6 寫作語氣與用詞

- 使用主動語態為主："We propose..." 而非 "It is proposed that..."
- 避免口語化表達："a lot of" → "numerous" / "a large number of"
- 避免過度 hedging："We believe that maybe..." → "We hypothesize that..."
- 數字表達：句首拼寫（"Three experiments..."），句中可用阿拉伯數字（"across 3 datasets"）。

---

> **維護說明：** 本文件由 Phyra 團隊維護，隨各會議最新政策更新。
> 最後更新：2026-04-04
