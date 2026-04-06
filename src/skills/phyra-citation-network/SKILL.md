---
name: phyra-citation-network
description: "Use this skill when analyzing relationships between research papers, building citation graphs, mapping research lineage, or constructing logical development narratives between works."
---

# phyra-citation-network

**定位：** 引用網絡分析框架，指導 relationship-mapper agent 如何建立研究之間的關係圖。

---

## 關係類型定義（必須從此詞彙表選擇，不得自創）

- `builds-on`：後者明確以前者為基礎，進行擴展或改進
- `contradicts`：後者的結論與前者存在實質矛盾，且作者意識到了這一點
- `parallel`：兩者獨立解決相似問題，互不引用但方法高度相關
- `supersedes`：後者在所有主要指標上優於前者，且方法更通用
- `applies`：後者將前者的方法用於新的領域或任務
- `critiques`：後者對前者進行批判性分析，但不提供替代方案

---

## 關係表格（必填格式）

```
| 研究 A | 研究 B | 關係類型 | 方向（A→B 或 B→A）| 依據（一句話）|
```

---

## 時間線要求

- 關係方向必須在確認發表時間後再斷言；同年發表的論文必須標記「時間方向不確定」

---

## 禁止的推斷

- 不得從摘要推斷兩篇論文的技術關係；關係判斷必須基於方法部分
- 不得因為研究者來自同一機構而假設研究之間存在關係

---

## 邏輯線構建要求

必須能用一段 prose 描述從最早的前驅工作到當前研究的發展脈絡，每個節點之間的過渡必須說明驅動原因（是前一個方法的哪個限制導致了下一個方法的出現）。
