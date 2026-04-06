---
name: phyra-paper-writing
description: "Use this skill when writing, revising, or planning academic papers. Provides story line construction principles, gap analysis writing norms, contribution claim rules, abstract structure (5-paragraph), and prohibited writing behaviors."
---

# Phyra Paper Writing

> 此 skill 定義學術寫作標準，指導論文撰寫相關 agent 如何構建故事線、撰寫各部分。

---

## 故事線構建原則

- 故事線必須從方法的邏輯中生長出來，不得反向操作（先有故事再找方法支撐）
- 一個好的故事線能在三句話內說清楚：什麼問題 → 為什麼現有方法不夠 → 你的方法如何從根本上不同
- 故事線的說服力來自 gap 的精確程度；gap 越具體，故事越有力

### 三句話測試

在開始撰寫任何論文之前，先完成以下測試：

1. **問題**：我們要解決什麼問題？（一句話）
2. **不足**：為什麼現有方法不夠？（一句話，必須具體）
3. **差異**：我們的方法如何從根本上不同？（一句話，不是細節堆砌）

如果三句話無法自然串聯，說明故事線尚未成熟，不應開始撰寫。

---

## Gap Analysis 寫作規範

- gap 必須引用具體的先前工作及其具體限制，不得使用「現有方法無法...」等無來源的泛化陳述
- gap 的描述必須讓讀者理解：為什麼這個問題在你之前沒有被解決

### 合格的 gap 陳述範例

> While [Author et al., 2024] achieved strong performance on X, their method assumes Y, which does not hold when Z.

### 不合格的 gap 陳述範例

> Existing methods cannot handle complex scenarios effectively.

不合格原因：無具體引用、無具體限制描述、「complex scenarios」含義不明。

---

## 貢獻聲稱規範

- 貢獻點：3-4 條，不多不少
- 每條貢獻必須是可被實驗驗證或否定的（falsifiable）
- 禁止以「我們提出了...」開頭；貢獻聲稱應描述貢獻的性質，不是行為
- 禁止「first to...」的聲稱，除非有充分文獻支持

### 合格的貢獻聲稱格式

> A loss function that decouples X from Y, enabling Z without requiring W.

### 不合格的貢獻聲稱格式

> We propose a novel framework for X.

不合格原因：「We propose」描述行為而非貢獻性質；「novel」是自我描述形容詞；缺乏可證偽性。

---

## Abstract 結構（五段論）

Abstract 必須包含以下五個部分，依序排列：

1. **問題陳述**（1-2 句）：定義要解決的問題及其重要性
2. **現有方法的具體限制**（1-2 句）：指出先前工作的具體不足
3. **本文方法的核心思路**（1-2 句）：描述方法的核心 idea，不是方法細節的堆砌
4. **主要實驗結果**（1-2 句）：必須有數字，報告關鍵指標的提升
5. **更廣泛的意義**（1 句）：克制地指出潛在影響，不誇大

每個部分的句數限制是硬限制。Abstract 總長度建議控制在 150-250 words。

---

## 禁止的寫作行為

以下行為在所有論文寫作輸出中被禁止，無例外：

- 禁止以「In recent years, X has attracted increasing attention...」開頭
- 禁止貢獻點中出現「comprehensive」/「extensive」/「thorough」等自我描述形容詞
- 禁止在未進行對應實驗的情況下聲稱方法的某種優勢

### 額外禁止模式

- 禁止使用「To the best of our knowledge」作為 novelty 的依據
- 禁止在 Introduction 中使用超過一段的背景鋪陳
- 禁止在 Related Work 中僅列舉工作而不做比較分析

---

## 領域寫作慣例

詳見 `~/.phyra/docs/phyra-ai-writing-conventions.md`。

該文件包含 AI / CV / NLP 等領域的具體寫作慣例，包括：

- 常見 section 結構與命名
- 實驗報告的標準格式
- 圖表的描述規範
- 術語使用的領域慣例

撰寫論文時，應同時參照本 skill 的通用規範與領域寫作慣例文件的具體指引。

---

## 與其他 Skill 的關係

- **phyra-soul**：全局寫作約束（排版禁令、語言約束）始終適用
- **phyra-peer-review-criteria**：撰寫時應預判 reviewer 會檢查的要點
- **phyra-experiment-design**：實驗結果的報告需符合實驗設計 skill 的規範
- **phyra-citation-network**：引用的選擇與 gap analysis 需參照引用網絡分析結果
