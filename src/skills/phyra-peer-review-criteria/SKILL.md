---
name: phyra-peer-review-criteria
description: "Use this skill when conducting peer review of academic papers, constructing review judgments, classifying defects, or evaluating research along the 5 review dimensions (problem validity, method soundness, experimental adequacy, novelty, reproducibility)."
---

# Peer Review 評審標準框架

> 指導審稿 agent 如何構建評審判斷。

## 評審維度（優先級順序）

### 1. 問題有效性（Problem Validity）

- 這個問題真的值得解決嗎？
- 作者對問題的定義是否清晰、有邊界？
- 問題的重要性聲稱是否有支撐？

### 2. 方法合理性（Method Soundness）

- 方法是否真正解決了 Introduction 定義的問題？
- 方法的假設是否在應用場景中成立？
- 方法的關鍵設計選擇是否有理論或實驗依據？

### 3. 實驗充分性（Experimental Adequacy）

- 實驗是否支撐方法部分的聲稱？
- Baseline 的選擇是否公平且合理？
- 結果是否具有統計意義？消融實驗是否回答了正確的問題？

### 4. 新穎性（Novelty）

- 與已有工作的本質差異是什麼？
- 差異是否在技術層面，還是只是在應用場景層面？

### 5. 可重現性（Reproducibility）

- 是否提供足夠細節以供復現？
- 超參數選擇是否透明？

## 缺陷分類體系

### Fatal flaw（致命缺陷）

如果這個問題存在，論文的核心聲稱不成立。不可通過 revision 修復。

### Major concern（重大問題）

論文的可信度受到嚴重影響，但原則上可通過修改修復。

### Minor issue（次要問題）

不影響核心聲稱，但會影響論文的清晰度或完整性。

### Suggestion（建議）

作者可以選擇接受或拒絕，不構成評審判斷的基礎。

## 禁止的評審行為

- 不得因為方法複雜而提高評分
- 不得因為結果數字好看而忽略方法缺陷
- 不得在未閱讀實驗部分的情況下評估實驗充分性

## 領域慣例補充

各領域（CV / NLP / Multimodal / DL / Robotics 等）對 baseline 選擇、數據集規範、評測指標有不同的慣例，評審時必須對照領域標準判斷，而非僅依賴通用原則。詳見 `~/.phyra/docs/phyra-ai-review-checklist.md`。
