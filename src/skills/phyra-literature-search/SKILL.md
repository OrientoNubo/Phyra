---
name: phyra-literature-search
description: "Use this skill when searching for related research, building literature collections, or conducting systematic literature surveys. Provides search order, three-line strategy (AT mode), keyword construction rules, and inclusion criteria."
---

# Literature Search Skill

**定位：** 搜索策略知識庫，指導 literature-searcher agent 如何系統性地查找相關研究。

---

## 搜索順序（標準優先級）

1. **arXiv**（預印本，覆蓋面最廣，速度最快）
2. **Semantic Scholar**（語義搜索，引用關係最完整）
3. **Google Scholar**（覆蓋最廣，但噪音最多）
4. **領域專屬數據庫**（ACL Anthology / IEEE Xplore / ACM DL / PubMed，根據領域選擇）
5. **GitHub**（找沒有論文的工程實現和研究）
6. **技術博客、工業報告**（找沒有學術發表的研究成果）

---

## 搜索策略三線（AT 模式下並行）

- **實例 A（關鍵詞正搜）：** 從核心術語出發，構建關鍵詞組合，直接搜索
- **實例 B（引用反查）：** 找到 1-2 篇核心相關論文後，查找 forward citation 和 backward citation
- **實例 C（相關領域擴展）：** 識別相鄰領域的術語映射，在不同社區中搜索同一類問題

---

## 關鍵詞構建規則

- 始終同時嘗試不同語言的術語（同一概念在不同社區可能有不同名稱）
- 搜索結果少於 5 篇時，嘗試上位概念
- 搜索結果多於 50 篇時，加入約束條件（時間範圍、方法類型等）

---

## 非論文研究的納入標準

- **GitHub repo：** star 數 > 100，或被知名論文引用
- **技術報告：** 來自可識別的研究機構或公司
- **博客文章：** 作者具有可驗證的研究背景，且提供了具體技術細節

---

## 相關性判斷

每篇入選研究必須能回答：

- 這個研究在解決什麼問題？
- 它與當前搜索目標的交集是什麼？（必須用一句具體的話說明，不得泛泛而談）

---

## 必須記錄的搜索元數據

```
- 搜索時間：
- 使用數據庫：
- 搜索詞：
- 結果總數：
- 入選數：
- 入選理由（每篇一句話）：
```
