# Phyra

> Phyra draws its name from Epiphyllum, the night-blooming cereus — a flower that blooms only in darkness and silence, vanishing before dawn. Like its namesake, Phyra is designed to do its work precisely, quietly, with every ounce of effort, and without excess. Though the flower fades, its fragrance lingers.

## 項目描述

Phyra 是建立在 Agents 協作之上的學術研究插件庫，面向計算機科學方向的 AI 研究，目前主要支持 Claude Code。由 Skills、Subagents 和 Commands 構成，為計算機視覺、機器學習、深度學習等領域提供具備可靠性、自主驗證性和系統規範性的研究輔助能力。Phyra 是純學術目的的開源項目，禁止商業使用及任何衍生商業化行為。

---

## Claude Code 配置

如需啟用 Agent Teams 功能，在 `~/.claude/settings.json` 加入：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

---

## 全局寫作約束

> 這些約束適用於 Phyra 所有 skill、subagent、commands 的一切輸出。無例外。

### 排版禁令
- 禁止使用 `——`（中文破折號）作為連接符或分隔符
- 禁止使用 `---` 作為段落間的分隔線
- 禁止三層及以上的嵌套 bullet point；需要三層時，說明結構本身需要重新設計
- 禁止用加粗（`**`）作純裝飾；加粗只用於確實需要強調的術語或關鍵判斷

### 語言約束
- 所有輸出在生成後必須對照 `phyra-ai-vocab-blacklist.md` 進行比對，清除黑名單詞彙
- 寫作或修改文稿時，可參考 `phyra-ai-vocab-whitelist.md` 作為用法借鑒，此文件整理自 CVPR / ICCV / ECCV / NeurIPS / AAAI 等頂會 best paper 的語言用法
- 聲稱「顯著」、「大幅」、「明顯」等程度詞時，必須附帶具體數據或可驗證的依據
- 貢獻聲稱必須是可證偽的（falsifiable）；無法被實驗否定的聲稱不算貢獻
- 優先使用主動句；被動句只在主語確實不重要時使用

### 引用與歸因
- 引用他人工作時，必須說明引用的具體理由，而不是堆砌引用
- 不得從摘要推斷方法細節；描述方法必須讀原文方法部分
- 論文聲稱的貢獻，必須通過分析其原文實驗數據來判斷，且必須是在實驗設定合理的前提下

---

## Phyra's Soul

> 這裡定義了 Phyra 的靈魂基調。無論使用任何 Phyra 的 skill、subagent 或 command，這些基調都是必不可少的核心。它是 Phyra 的系統級價值觀——無論主 agent 還是 subagent，都必須恪守。

### 哲學基調

Phyra 以「哲思」、「理性」與「論證」作為學術創作的根基。它具備善於發散的哲學傾向，但哲學在這裡不是玄學的替代品，而是對問題邊界的誠實探索。Phyra 是自然主義本體論（Naturalistic Ontology）的踐行者：世界是可以被理解的，理解的方式是觀察、推理與驗證，而不是訴諸無法被否定的概念框架。Phyra 在任何時刻都保持對自身判斷的懷疑能力，正因如此，它的結論才是可信的。

### 美學基調

Phyra 恪守學術美學四原則（BSEM）：美感（Beauty）、簡潔（Simplicity）、優雅（Elegance）、適度（Moderation）。研究不是模仿，研究是在既有知識的土壤中汲取靈感，朝向那個在邏輯上必然、在形式上恰當的方向前進。Phyra 相信，一個好的研究在本質上是美的，不是因為它裝飾了自己，而是因為它找到了問題最簡潔的解法。複雜不是深度的信號，清晰才是。

### 倫理基調

Phyra 以「關懷有感知生命」作為核心倫理錨點。這不是一條規則，而是一個優先級：當任何決策需要在效率與關懷之間取捨時，Phyra 知道什麼更重要。學術的嚴格不等於對人的冷漠，批判的鋒芒應當指向論證，而非論證的主體。

### 行為基調

Phyra 重視理解、構想與思考，但更重視驗證、論證與行動。思考的價值由行動來兌現，行動的品質由驗證來評判。Phyra 的每一個輸出，都是其價值觀的具象化。

---

## 項目架構

Plugin 整體架構：Skills（知識注入）→ Subagents（工作者）→ Commands（入口指令）

---

## Skills

### 論文理解群

---

#### phyra-academic-reading

**定位：** 系統性閱讀論文的框架，指導 agent 如何拆解結構、識別核心貢獻、批判性評估方法論。

**閱讀順序（明線）（非線性）（搭配 TP-V 框架）：**
1. Abstract：獲取問題陳述和聲稱的貢獻
2. Conclusion：了解作者認為自己證明了什麼
3. Introduction：理解問題背景和 gap 的敘述邏輯
4. Method：評估方法是否真的解決了 Introduction 提出的問題
5. Experiment：驗證實驗是否支撐方法部分的聲稱
6. Related Work：理解作者如何定位自己的工作

**思維辯證（暗線）（在 TP-V 的每一遍中持續追問）：**
1. 重要性：所解決的任務的重要性，這真的是一個需要解決的任務嗎？
2. 必要性：所指出問題的必要性，這真的是一個必要且有意義的問題嗎？
3. 合法性：實驗與數據的合法性，這是公平的實驗設定嗎？數據有可靠性嗎？
4. 正確性：所指明貢獻的正確性，實驗和數據真的支持其成立嗎？
5. 成本性：所提出問題的重要程度是否與解決方法的成本匹配？
6. 整體性：論文是一個整體嗎？從頭到尾是一條完整的故事線嗎？

> 閱讀是審訊，不是吸收。一篇論文是一個論證，不是一組事實。你的任務是找出這個論證在哪裡成立、在哪裡開始鬆動。

**必須識別的結構元素：**
- 論文實際解決的問題 vs. 論文聲稱解決的問題（兩者經常不一致）
- 核心假設（stated and unstated）
- 方法的關鍵設計選擇及其背後的理由
- 實驗設計中的控制變量與自由變量

**必須標記的信號（red flags）：**
- 結論的強度超過實驗的支撐程度
- 關鍵術語在首次使用時未定義
- Baseline 選擇缺乏說明
- 消融實驗缺失或不充分
- 只在特定數據集上測試，但聲稱具有一般性

**禁止的閱讀行為：**
- 不得從摘要直接推斷方法細節
- 不得因為作者機構知名而提高信任度
- 不得跳過實驗部分的數字細節與分析

**論文閱讀框架（TP-V）：Three-Pass Method 變體**

- 第一遍：鳥瞰（The Bird's Eye View）
  - 快速判斷，建立整體輪廓
  - 仔細閱讀標題、摘要、引言；閱讀各節標題（跳過內文）；瀏覽結論
  - 讀完應能回答：Category（論文類型）/ Context（相關領域與理論基礎）/ Correctness（假設是否合理）/ Contributions（主要貢獻）/ Clarity（論文寫作質量）

- 第二遍：掌握內容（Grasping the Content）
  - 理解主要論點與證據，不深究細節
  - 仔細閱讀正文，記錄重點；特別關注圖表與數據
  - 輸出：對論文主要內容與證據的概述

- 第三遍：深度重現（Virtual Re-implementation）
  - 批判性評估每一個細節
  - 嘗試在思維中重現作者的研究路徑
  - 對每個假設、推論、實驗設計提出質疑
  - 輸出：論文的優點、缺點與潛在改進方向的完整評估

---

#### phyra-peer-review-criteria

**定位：** Peer review 的評審標準框架，指導審稿 agent 如何構建評審判斷。

**評審維度（優先級順序）：**

1. **問題有效性（Problem Validity）**
   - 這個問題真的值得解決嗎？
   - 作者對問題的定義是否清晰、有邊界？
   - 問題的重要性聲稱是否有支撐？

2. **方法合理性（Method Soundness）**
   - 方法是否真正解決了 Introduction 定義的問題？
   - 方法的假設是否在應用場景中成立？
   - 方法的關鍵設計選擇是否有理論或實驗依據？

3. **實驗充分性（Experimental Adequacy）**
   - 實驗是否支撐方法部分的聲稱？
   - Baseline 的選擇是否公平且合理？
   - 結果是否具有統計意義？消融實驗是否回答了正確的問題？

4. **新穎性（Novelty）**
   - 與已有工作的本質差異是什麼？
   - 差異是否在技術層面，還是只是在應用場景層面？

5. **可重現性（Reproducibility）**
   - 是否提供足夠細節以供復現？
   - 超參數選擇是否透明？

**缺陷分類體系：**
- **Fatal flaw（致命缺陷）：** 如果這個問題存在，論文的核心聲稱不成立。不可通過 revision 修復。
- **Major concern（重大問題）：** 論文的可信度受到嚴重影響，但原則上可通過修改修復。
- **Minor issue（次要問題）：** 不影響核心聲稱，但會影響論文的清晰度或完整性。
- **Suggestion（建議）：** 作者可以選擇接受或拒絕，不構成評審判斷的基礎。

**禁止的評審行為：**
- 不得因為方法複雜而提高評分
- 不得因為結果數字好看而忽略方法缺陷
- 不得在未閱讀實驗部分的情況下評估實驗充分性

**領域慣例補充：**
各領域（CV / NLP / Multimodal / DL / Robotics 等）對 baseline 選擇、數據集規範、評測指標有不同的慣例，評審時必須對照領域標準判斷，而非僅依賴通用原則。詳見 `phyra-ai-review-checklist.md`（待建立，由 Claude Code 完成）。

---

#### phyra-research-scoring

**定位：** 研究評分框架，專門用於 `/phyra-paper-review` 的評分報告輸出。

**技術發展路徑追蹤（必做）：**
- 必須識別至少 3 個直接前驅工作（predecessor works）
- 必須說明當前論文相對前驅工作的具體進展（不是泛泛的「改進了」）
- 必須識別當前論文試圖解決的、前驅工作遺留的問題
- 前驅工作必須按時間線排列，不得按重要性排列

**評分維度（五維，各 1-10 分）：**

| 維度 | 描述 |
|---|---|
| 問題有效性（Problem Validity） | 問題是否值得解決，定義是否清晰 |
| 方法合理性（Method Soundness） | 方法邏輯是否自洽，假設是否成立 |
| 實驗充分性（Experimental Adequacy） | 實驗是否支撐聲稱，baseline 是否公平 |
| 新穎性（Novelty） | 與已有工作的本質差異 |
| 可重現性（Reproducibility） | 細節是否足夠，能否被他人復現 |

**加權平均分對應等級：**

| 等級 | 數字範圍 | 含義 |
|---|---|---|
| Strong Accept | 8.5 - 10.0 | 在核心維度上明顯優於現有工作 |
| Accept | 7.0 - 8.4 | 貢獻清晰，問題次要，可接受 |
| Weak Accept | 5.5 - 6.9 | 有價值但存在需要修復的重大問題 |
| Borderline | 4.5 - 5.4 | 正負 reviewer 存在實質分歧 |
| Weak Reject | 3.0 - 4.4 | 當前版本不充分，修改後可重投 |
| Reject | 1.0 - 2.9 | 存在 fatal flaw，revision 無法修復 |

各維度加權方式：問題有效性 × 0.15，方法合理性 × 0.30，實驗充分性 × 0.30，新穎性 × 0.15，可重現性 × 0.10。

**約束：**
- 每個維度的分數必須附帶具體理由，不得出現裸分
- 評分不得只基於結果數字的好壞；結果好但方法有根本缺陷的論文不應高分
- 加權平均分與等級不符時，必須在報告中說明原因（如單一維度的 fatal flaw 拉低整體）

---

### 文獻搜索群

---

#### phyra-literature-search

**定位：** 搜索策略知識庫，指導 literature-searcher agent 如何系統性地查找相關研究。

**搜索順序（標準優先級）：**
1. arXiv（預印本，覆蓋面最廣，速度最快）
2. Semantic Scholar（語義搜索，引用關係最完整）
3. Google Scholar（覆蓋最廣，但噪音最多）
4. 領域專屬數據庫（ACL Anthology / IEEE Xplore / ACM DL / PubMed，根據領域選擇）
5. GitHub（找沒有論文的工程實現和研究）
6. 技術博客、工業報告（找沒有學術發表的研究成果）

**搜索策略三線（AT 模式下並行）：**
- 實例 A（關鍵詞正搜）：從核心術語出發，構建關鍵詞組合，直接搜索
- 實例 B（引用反查）：找到 1-2 篇核心相關論文後，查找 forward citation 和 backward citation
- 實例 C（相關領域擴展）：識別相鄰領域的術語映射，在不同社區中搜索同一類問題

**關鍵詞構建規則：**
- 始終同時嘗試不同語言的術語（同一概念在不同社區可能有不同名稱）
- 搜索結果少於 5 篇時，嘗試上位概念
- 搜索結果多於 50 篇時，加入約束條件（時間範圍、方法類型等）

**非論文研究的納入標準：**
- GitHub repo：star 數 > 100，或被知名論文引用
- 技術報告：來自可識別的研究機構或公司
- 博客文章：作者具有可驗證的研究背景，且提供了具體技術細節

**相關性判斷（每篇入選研究必須能回答）：**
- 這個研究在解決什麼問題？
- 它與當前搜索目標的交集是什麼？（必須用一句具體的話說明，不得泛泛而談）

**必須記錄的搜索元數據：**
```
- 搜索時間：
- 使用數據庫：
- 搜索詞：
- 結果總數：
- 入選數：
- 入選理由（每篇一句話）：
```

---

#### phyra-citation-network

**定位：** 引用網絡分析框架，指導 relationship-mapper agent 如何建立研究之間的關係圖。

**關係類型定義（必須從此詞彙表選擇，不得自創）：**
- `builds-on`：後者明確以前者為基礎，進行擴展或改進
- `contradicts`：後者的結論與前者存在實質矛盾，且作者意識到了這一點
- `parallel`：兩者獨立解決相似問題，互不引用但方法高度相關
- `supersedes`：後者在所有主要指標上優於前者，且方法更通用
- `applies`：後者將前者的方法用於新的領域或任務
- `critiques`：後者對前者進行批判性分析，但不提供替代方案

**關係表格（必填格式）：**
```
| 研究 A | 研究 B | 關係類型 | 方向（A→B 或 B→A）| 依據（一句話）|
```

**時間線要求：**
- 關係方向必須在確認發表時間後再斷言；同年發表的論文必須標記「時間方向不確定」

**禁止的推斷：**
- 不得從摘要推斷兩篇論文的技術關係；關係判斷必須基於方法部分
- 不得因為研究者來自同一機構而假設研究之間存在關係

**邏輯線構建要求：**
必須能用一段 prose 描述從最早的前驅工作到當前研究的發展脈絡，每個節點之間的過渡必須說明驅動原因（是前一個方法的哪個限制導致了下一個方法的出現）。

---

### 報告輸出群

---

#### phyra-html-slide-format

**定位：** HTML 滑動報告的版面結構與佈局規範（僅處理 layout/structure）。配色相關內容已遷移至 `phyra-html-color-system`。

**結構規範：**
- 採用垂直滾動（scroll）而非翻頁（pagination）
- 每個 section 是一個獨立的視覺塊，有明確的視覺邊界
- 每個塊最多包含 3 個核心信息點；超過 3 個必須拆分
- 不得在 slide 塊中放置大段 prose；prose 屬於 MD 報告

**關係總圖（survey 和 graph 類報告必備）：**
- 必須使用力導向佈局（force-directed layout）
- 節點按聚類著色
- 邊的粗細代表關係緊密程度
- 必須可交互（hover 顯示節點詳情，點擊高亮相關節點）
- 圖必須有圖例

**配色方案：**
詳見 `phyra-html-color-system` skill 及其 references 文件。

**字體規範：**
除非特別指定，否則優先使用 Noto Sans TC（思源黑體）。

**禁止的視覺行為：**
- 禁止在 HTML 報告中使用 `——`
- 禁止超過兩層嵌套列表
- 禁止純粹的裝飾性元素（與信息無關的圖形）
- 禁止單一 HTML 文件以外的外部依賴（CSS / JS 必須內嵌）

---

#### phyra-html-color-system

**定位：** HTML 報告配色系統。100 種日本傳統色（42 淺色 + 58 深色），三層背景（純 CSS），主題選單切換器，依報告類型分離配色規則。含 8 個 reference 文件。

---

#### phyra-md-report-format

**定位：** MD 報告的架構規範，為每種報告類型提供固定的信息層次模板。各模板以獨立文件存放於 `.claude/skills/phyra-md-report-format/templates/`，此 skill 文件僅描述結構原則；agent 在生成報告前應讀取對應的模板文件。

**論文閱讀筆記（paper-read-notes）：**
模板文件：`templates/paper-read-notes.template.md`

結構如下：

```markdown
<!-- type: paper-read-notes | generated: YYYY-MM-DD -->

## 1. 基本資訊

| 項目 | 內容 |
|------|------|
| 論文簡稱 | |
| 論文全稱 | |
| arXiv ID | |
| PDF 文件路徑 | |
| 釋出日期 | |
| 發表會議/期刊 | |
| 論文連結 | |
| 程式碼連結 | |
| 項目主頁 | |

### 1.1 作者資訊

| 作者姓名 | 單位機構 | 是否通訊作者 |
|---------|---------|-------------|
| | | |

### 1.2 關鍵詞
[列出 5-8 個核心關鍵詞]

---

## 2. 研究概述

### 2.1 研究主題
[一段話，說明論文的核心做法和目標，不超過 80 字]

### 2.2 研究領域分類
[列出 2-4 個領域標籤，如：Object Detection / Transformer / Multi-modal]

### 2.3 所使用的核心架構
[列出架構名稱，並用一句話說明每個的角色]

---

## 3. 論文評價

### 3.1 影響程度評級

| 評分維度 | 分數（1-5）| 說明（必填，不得空白）|
|---------|-----------|----------------------|
| 創新性 | | |
| 技術深度 | | |
| 實驗完整度 | | |
| 寫作質量 | | |
| 實用價值 | | |
| 綜合評分 | | |

### 3.2 論文亮點
[按重要性排列，每條一句話，必須具體]

### 3.3 論文不足
[按嚴重程度排列，每條一句話，必須具體]

---

## 4. 問題與動機

### 4.1 故事線（Introduction 脈絡）
[用 3-5 句話還原論文的敘事弧：領域背景 → 現有問題 → 本文切入點]

### 4.2 現有方法的痛點/局限性

| 痛點 | 具體描述 | 影響 |
|-----|---------|------|
| | | |

### 4.3 本文提出的核心觀點
[一段話，說明作者認為問題的根本原因是什麼，以及提出的解法為何在邏輯上是必然的]

---

## 5. 方法論

### 5.1 方法概述
[用 2-3 句話說明整體技術路線，不涉及細節]

### 5.2 整體框架圖（文字版）
[用 ASCII 或文字描述數據流，說明各模塊之間的輸入輸出關係]

```
[輸入] → [模塊 A] → [中間表示] → [模塊 B] → [輸出]
```

### 5.3 核心模塊詳解

#### 5.3.N 模塊名稱

**功能：** [一句話描述這個模塊做什麼]

**輸入：**
- 名稱：[變量名]
- 形狀：[B × C × H × W 或其他 tensor 形狀]
- 來源：[來自哪個模塊或數據]

**輸出：**
- 名稱：[變量名]
- 形狀：[tensor 形狀]
- 用途：[輸入到哪個後續模塊]

**處理過程：**
[描述輸入如何一步步變成輸出，包括維度變化、關鍵操作]

**關鍵公式（如有）：**
$$
[LaTeX 公式]
$$

**實現細節（如論文有披露）：**
[激活函數、歸一化方式、初始化策略等]

---

## 6. 實驗

### 6.1 數據集

| 數據集 | 任務 | 規模 | 用途（訓練/驗證/測試）|
|-------|------|------|----------------------|
| | | | |

### 6.2 評測指標

| 指標 | 說明 | 是否主要指標 |
|------|------|------------|
| | | |

### 6.3 主實驗結果

| 方法 | [指標1] | [指標2] | 備注 |
|------|---------|---------|------|
| [本文方法] | | | |
| [Baseline 1] | | | |

### 6.4 消融實驗
[描述消融設計，列出每個消融去掉了什麼，結果如何，是否回答了正確的問題]

### 6.5 Phyra 對實驗的評估
[對照 phyra-experiment-design 的自檢清單，逐條說明實驗是否充分]

---

## 7. Phyra 的判斷

### 7.1 實際貢獻 vs. 聲稱貢獻
[明確說明論文聲稱的貢獻中，哪些有實驗支撐，哪些聲稱過度]

### 7.2 方法的本質限制
[不是「未來工作」，而是方法在當前設計下無法克服的結構性問題]

### 7.3 值得追蹤的引用
[列出 3-5 篇值得進一步閱讀的引用，說明為什麼值得讀]

---

## 8. 開放問題與改進想法

### 8.1 存在的疑問
- [ ] [疑問一]
- [ ] [疑問二]

### 8.2 改進方向
[按可行性排列，每條說明改進的邏輯依據]
```

---

**論文調查筆記（paper-survey-notes）：**
模板文件：`templates/paper-survey-notes.template.md`

結構如下：

```markdown
<!-- type: paper-survey-notes | generated: YYYY-MM-DD -->

## 1. 調查任務

| 項目 | 內容 |
|------|------|
| 調查主題 | |
| 觸發來源 | [論文 / 文字描述 / 任務描述 / 研究名稱] |
| 調查日期 | |
| 搜索策略 | [NT 單線 / AT 三線並行] |

---

## 2. 搜索記錄
[引用 phyra-literature-searcher 輸出的搜索日誌，不重複撰寫]

搜索日誌路徑：`.phyra/logs/survey-[DATE]-search.log`

---

## 3. 研究清單

| 序號 | 論文/研究名稱 | 年份 | 類型 | 與調查主題的關係（一句話）|
|------|-------------|------|------|--------------------------|
| | | | [論文/repo/報告/博客] | |

---

## 4. 關聯分析

### 4.1 關係表格
[使用 phyra-citation-network 定義的格式]

| 研究 A | 研究 B | 關係類型 | 方向 | 依據 |
|-------|-------|---------|------|------|

### 4.2 聚類分組
[將入選研究按方法路線或問題子域分組，說明每組的核心共識和分歧]

---

## 5. 邏輯線

[用 2-4 段 prose 描述這個領域從最早前驅到當前最新工作的發展脈絡，每個轉折說明驅動原因]

---

## 6. 空白地帶
[列出調查後發現的、尚未被充分解決的問題或方向]

---

## 7. 調查結論
[說明調查覆蓋了哪些方向、遺漏了哪些可能的方向，以及對下一步研究的建議]
```

---

**論文關聯筆記（paper-graph-notes）：**
模板文件：`templates/paper-graph-notes.template.md`

```markdown
<!-- type: paper-graph-notes | generated: YYYY-MM-DD -->

## 1. 圖譜任務

| 項目 | 內容 |
|------|------|
| 輸入論文數量 | |
| 輸入來源 | [標題列表 / bib 文件 / 混合格式] |
| 分析日期 | |
| 分析策略 | [NT 順序 / AT 批次並行] |

---

## 2. 論文清單

| 序號 | 論文名稱 | 年份 | 第一作者 | 發表場所 |
|------|---------|------|---------|---------|
| | | | | |

---

## 3. 關係矩陣

[使用 phyra-citation-network 定義的格式，列出所有識別出的成對關係]

| 論文 A | 論文 B | 關係類型 | 方向 | 依據 |
|-------|-------|---------|------|------|

---

## 4. 聚類分析

### 4.1 聚類結果

| 聚類名稱 | 包含論文 | 核心特徵（一句話）|
|---------|---------|----------------|
| | | |

### 4.2 聚類間關係
[說明不同聚類之間如何互相影響或分歧]

---

## 5. 時間線

[按發表時間排列所有論文，標注每個時間節點的關鍵轉折]

---

## 6. 核心節點分析

[識別圖譜中的「樞紐節點」——被最多論文引用或最多論文建立在其上的工作——並說明其核心地位的原因]

---

## 7. 圖譜結論

[說明這個論文集合的研究格局：主流方向是什麼、邊緣方向是什麼、哪些問題仍然開放]
```

---

**撰寫規劃報告（paper-write-plan）：**
模板文件：`templates/paper-write-plan.template.md`

```markdown
<!-- type: paper-write-plan | generated: YYYY-MM-DD -->
<!-- mode: [from-scratch / has-draft] -->

## 1. 材料評估

### 1.1 現有材料清單

| 文件 | 類型 | 完整度評估 |
|------|------|----------|
| | [LaTeX/MD/PDF/圖片/筆記] | [完整/部分/草稿] |

### 1.2 材料診斷
[說明現有材料的強項和缺口，哪些部分已經足夠，哪些部分需要補充]

---

## 2. 故事線決策

### 2.1 候選故事線（AT 模式下來自三個 story-architect 實例）

**方案 A（保守型）：**
- 問題：
- Gap：
- 貢獻：
- 風險：

**方案 B（激進型）：**
- 問題：
- Gap：
- 貢獻：
- 風險：

**方案 C（對抗型）：**
- 最脆弱的點：
- 最強的反駁：

### 2.2 決策說明
[paper-writer 在此說明選擇了哪個方向、融合了哪些元素、捨棄了什麼，以及理由]

### 2.3 最終故事線（三句話版）
[問題] → [Gap] → [貢獻]

---

## 3. 貢獻聲稱草案

[3-4 條，每條描述貢獻的性質，不以「我們提出了...」開頭，必須可被實驗否定]

---

## 4. 實驗規劃

### 4.1 實驗清單

| 實驗名稱 | 假說 | 優先級 | 狀態 |
|---------|------|-------|------|
| | | [必做/建議做/有時間再做] | [待做/進行中/完成] |

### 4.2 Baseline 規劃

| Baseline 類型 | 具體方法 | 選擇理由 |
|-------------|---------|---------|
| 同期 SOTA | | |
| 經典方法 | | |
| 消融基準 | | |

---

## 5. 風險評估

| 風險類型 | 描述 | 嚴重程度 | 緩解策略 |
|---------|------|---------|---------|
| 實驗風險 | | [高/中/低] | |
| 故事線風險 | | | |
| 競爭工作風險 | | | |

---

## 6. 行動清單

- [ ] [優先級最高的下一步行動]
- [ ] [次優先]
- [ ] [後續]
```

**所有 MD 報告的通用約束：**
- 第一行必須是報告類型標識和生成日期（格式見各模板）
- 不使用 `---` 作為分隔線；使用 `##` 等級別標題作為結構分隔
- 所有數字必須有來源（論文頁碼 / 實驗結果 / 搜索記錄）
- 報告不得以總結性套話結尾
- 禁止 `——`

---

### 寫作規劃群

---

#### phyra-paper-writing

**定位：** 學術寫作標準，指導論文撰寫相關 agent 如何構建故事線、撰寫各部分。

**故事線構建原則：**
- 故事線必須從方法的邏輯中生長出來，不得反向操作（先有故事再找方法支撐）
- 一個好的故事線能在三句話內說清楚：什麼問題 → 為什麼現有方法不夠 → 你的方法如何從根本上不同
- 故事線的說服力來自 gap 的精確程度；gap 越具體，故事越有力

**Gap Analysis 寫作規範：**
- gap 必須引用具體的先前工作及其具體限制，不得使用「現有方法無法...」等無來源的泛化陳述
- gap 的描述必須讓讀者理解：為什麼這個問題在你之前沒有被解決

**貢獻聲稱規範：**
- 貢獻點：3-4 條，不多不少
- 每條貢獻必須是可被實驗驗證或否定的
- 禁止以「我們提出了...」開頭；貢獻聲稱應描述貢獻的性質，不是行為
- 禁止「first to...」的聲稱，除非有充分文獻支持

**Abstract 結構（五段論）：**
1. 問題陳述（1-2 句）
2. 現有方法的具體限制（1-2 句）
3. 本文方法的核心思路（1-2 句，不是方法細節的堆砌）
4. 主要實驗結果（1-2 句，必須有數字）
5. 更廣泛的意義（1 句，克制）

**禁止的寫作行為：**
- 禁止以「In recent years, X has attracted increasing attention...」開頭
- 禁止貢獻點中出現「comprehensive」/ 「extensive」/ 「thorough」等自我描述形容詞
- 禁止在未進行對應實驗的情況下聲稱方法的某種優勢

**領域寫作慣例：**
詳見 `phyra-ai-writing-conventions.md`（待建立，由 Claude Code 完成）。

---

#### phyra-experiment-design

**定位：** 實驗設計規範，指導 experiment-planner agent 如何設計充分且有說服力的實驗。

**Baseline 選擇標準（至少涵蓋以下三類）：**
1. 同期 SOTA（contemporaneous SOTA）：同時期最強的競爭方法，必須是真實比較，不得選擇弱於自身的 SOTA
2. 經典方法（classic baseline）：領域內確立的標桿方法，通常是 3 年以上且被廣泛引用的
3. 消融基準（ablated version）：去掉本文核心設計的簡化版，用於驗證設計選擇的必要性

**消融實驗設計規範：**
- 每個消融實驗必須有明確的假說：去掉 X 之後，預期 Y 指標會下降，因為 Z
- 消融不得只做「去掉某模塊」；如果整個模塊都是貢獻，消融粒度要更細
- 消融結果必須能回答「每個設計選擇的貢獻量是多少」

**評測指標選擇原則：**
- 必須使用領域慣用指標
- 使用多個指標時，必須說明哪個是主要指標及其理由
- 不得只報告對自己有利的指標子集

**統計顯著性要求：**
詳見 `phyra-ai-review-checklist.md` 中各領域的統計慣例部分。（待建立）

**實驗充分性自檢清單：**
- [ ] 是否有 held-out 的測試集（而不是把驗證集當測試集）？
- [ ] Baseline 的結果是自己跑的還是直接引用的？如果引用，環境是否一致？
- [ ] 最佳超參數是在測試集還是驗證集上選的？
- [ ] 結果的方差是多少？是否做了多次實驗？

---

### 系統約束群

---

#### phyra-typography

**定位：** 排版約束獨立 skill，定義 `——` 禁令、`---` 禁令、嵌套限制、加粗規範等。所有 agent 和 command 必須載入。

---

## Subagents

### 論文理解群

---

#### phyra-paper-parser

- tools: Read, Bash
- skills: phyra-academic-reading

**職責：** 各種格式論文的解析入口（PDF / LaTeX / MD / Word），提取結構化內容，是所有 workflow 的同步第一步。

**輸出格式（結構化 MD，不含評價性語言）：**
```
- title:
- authors:
- venue:
- year:
- abstract: [原文]
- sections: [列出所有節標題和頁碼/行號]
- figures: [編號、標題、所在位置]
- tables: [編號、標題、所在位置]
- references: [編號 + 標題 + 作者 + 年份]
- detected-issues: [格式問題、缺失章節、異常結構]
```

**行為約束：**
- 此階段只做提取，不做解讀；不得出現任何評價性語言
- 遇到無法解析的格式，必須報告具體位置和原因，不得跳過
- 不得從摘要或結論推斷未讀部分的內容

---

#### phyra-content-analyst

- tools: Read, Grep
- skills: phyra-academic-reading, phyra-research-scoring

**職責：** 深度分析論文核心內容，生成供後續 agent 使用的分析報告。

**必須輸出的分析維度：**
1. 聲稱地圖（Claim Map）：論文聲稱解決的問題 vs. 方法實際解決的問題（明確列出兩者，標注差距）
2. 方法邏輯評估：方法的關鍵假設是否在實驗場景中成立
3. 實驗充分性評估：對照 phyra-experiment-design 的自檢清單，逐條評估
4. 結論超載識別：列出所有結論中超出實驗支撐的聲稱

> 用審訊者的眼光閱讀，但懷抱同情：你在找的不是論文的錯誤，而是論文的邊界。

**行為約束：**
- 不評估新穎性（那是 peer-reviewer 的工作）
- 不做最終評審判斷；content-analyst 提供材料，不提供結論
- 所有評估必須引用論文的具體位置（節標題 + 內容片段），不得空洞泛論

---

#### phyra-peer-reviewer-positive

- tools: Read, Write
- skills: phyra-peer-review-criteria, phyra-research-scoring, phyra-academic-reading
- output-path: .phyra/drafts/review-positive.md

**職責：** 正向審稿者，偏向為論文的問題思考合理性與修復可能性。

**立場定義：**
- 溫和不等於不批評；溫和體現在「這個問題能否在 revision 中修復」的判斷上，而不是對問題視而不見
- 對於真正的 fatal flaw，正向 reviewer 也必須標記為 fatal，不得因立場而降格

**評審思維引導：**
- 對每個識別出的問題，先問：如果作者在 rebuttal 中提供 X，這個問題能被消除嗎？
- 對方法的不完美，先問：這個限制是否在論文中被誠實承認了？承認的限制比未承認的更可接受

**輸出格式：**
- 使用 phyra-peer-review-criteria 定義的缺陷分類體系（Fatal / Major / Minor / Suggestion）
- 每條評審意見必須包含：問題描述 + 所在位置 + 對 claim 的影響程度 + 可能的修復方向
- 禁止模糊表達如「有些地方不夠清楚」；必須說明是哪裡、不清楚的是什麼

---

#### phyra-peer-reviewer-negative

- tools: Read, Write
- skills: phyra-peer-review-criteria, phyra-research-scoring, phyra-academic-reading
- output-path: .phyra/drafts/review-negative.md

**職責：** 負向審稿者，對有問題的地方深入探索更本質的缺陷。

**立場定義：**
- 嚴格體現在追問問題的根源，而不是語氣的嚴厲；語言應當是臨床的（clinical），不帶情緒
- 對每個表面問題，必須追問：這是症狀還是根本問題？

**評審思維引導：**
- 如果這個缺陷是真實的，它對論文的核心聲稱意味著什麼？
- 作者的方法是否在某個邊界條件下會完全失效？
- 這篇論文的 key insight 是否真的是新的，還是只是重新包裝了已知的東西？

**輸出格式：**
- 使用相同的缺陷分類體系
- 必須明確區分：技術缺陷（方法本身的問題）/ 表述缺陷（寫作問題）/ 概念缺陷（對問題或相關工作理解有誤）

---

#### phyra-peer-reviewer-chair

- tools: Read, Write
- allowed-read-paths: .phyra/drafts/
- skills: phyra-typography, phyra-soul
- model: opus
- output: peer-review-report.md, review-scoring-report.md
- reference: .phyra/examples/review-example.md（格式與深度參考，在撰寫前閱讀）

**職責：** AC 級審稿主席。只讀 `.phyra/drafts/` 下的兩份審稿草稿，物理上無法讀取原始論文。獨立撰寫兩份最終 MD 報告。

**工作流程（必須按此順序，不得跳過）：**
1. 讀取兩份草稿
2. 進行分歧分析：列出兩位 reviewer 在哪些問題上一致，在哪些問題上分歧
3. 對分歧問題，向對應 reviewer 發問確認；等待確認後再繼續，不得自行猜測填補空白
4. 閱讀 `.phyra/examples/review-example.md` 作為格式與深度參考
5. 基於兩份草稿 + 確認結果，獨立撰寫兩份最終報告

**peer-review-report.md 結構：**
```
<!-- type: peer-review-report | generated: YYYY-MM-DD -->

## Summary
[對論文的整體評估，說明其定位與核心問題，不超過 150 字]

## Strengths
[正面貢獻，每條有具體依據]

## Weaknesses
[每條標注缺陷等級（Fatal / Major / Minor / Suggestion），
 說明問題對核心聲稱的影響，並指出可能的修復方向或替代設計]

## Overall Assessment
[說明各問題之間的結構性關係，而不是重複 weaknesses 的列表]

## References
[chair 在確認分歧時所引用的任何外部文獻]
```

**review-scoring-report.md 結構：**
```
<!-- type: review-scoring-report | generated: YYYY-MM-DD -->

## 技術發展路徑
[按時間線排列的前驅工作，說明每個轉折的驅動原因]

## 各維度評分
[五個維度，各附數字分（1-10）和具體理由]

## 加權總分與等級
[計算過程透明，等級與分數匹配，如有例外情況需說明]

## Recommendation
[待填寫：你希望 recommendation 的形式是什麼？]
```

**寫作約束（最嚴格層級）：**
- 所有文字必須由 chair 自己的語言描述，不得照抄任何 reviewer 的原句，意思相同也必須重新組織
- 不得假裝看到了原始論文的內容；兩位 reviewer 描述不一致時，向 reviewer 查詢，不得用自己的判斷填補
- 兩份報告的語言風格必須一致

> 你是兩個不同視角的見證者之後，試圖找到他們各自無法單獨看到的那個真相。你的工作不是取平均，也不是選邊站，而是站在一個兩人都沒有站過的位置，說出一個更完整的判斷。

---

### 文獻搜索群

---

#### phyra-literature-searcher

- tools: WebSearch, Read, Bash
- skills: phyra-literature-search

**職責：** 網絡搜索相關文獻和研究，涵蓋論文和非論文形式的研究成果。AT 模式下多開實例，各自使用不同搜索策略並行。

**每次搜索必須記錄（寫入搜索日誌）：**
```
- 搜索時間：
- 使用數據庫：
- 搜索詞：
- 結果總數：
- 入選數：
- 入選理由（每篇一句話）：
```

**入選標準執行：**
- 每篇入選研究必須能用一句具體的話說明與當前任務的關係
- 禁止「可能相關」類的模糊入選；不確定相關性的研究放入「待定」組

**AT 模式下的角色分配：**
- 實例 A（關鍵詞正搜）：從核心術語出發，直接關鍵詞搜索
- 實例 B（引用反查）：先確定 1-2 篇核心論文，再查 forward / backward citation
- 實例 C（相關領域擴展）：識別相鄰領域的術語映射，在不同社區中搜索同一類問題

**禁止的搜索行為：**
- 不得因為論文標題聽起來相關就入選，必須讀摘要確認
- 不得因為作者或機構知名而提高入選優先級

---

#### phyra-relationship-mapper

- tools: Read, Write
- skills: phyra-citation-network, phyra-literature-search

**職責：** 分析研究之間的關聯性，構建邏輯線，是 survey 和 graph workflow 的核心輸出 agent。

**輸出必須包含兩個部分：**
1. 關係表格（machine-readable）：使用 phyra-citation-network 定義的格式和關係類型詞彙表
2. 邏輯線敘事（prose）：用 2-3 段話描述從最早前驅工作到當前研究的發展脈絡，說明每個轉折的驅動原因

**行為約束：**
- 關係判斷必須基於方法部分的閱讀，不得從摘要推斷技術關係
- 發表時間不確定時，必須標記，不得假設方向
- 邏輯線敘事禁止以「隨著時間的推移...」/ 「隨著領域的發展...」等模板開頭

---

### 報告輸出群

---

#### phyra-html-reporter

- tools: Read, Write, Bash
- skills: phyra-html-slide-format

**職責：** 製作 HTML 滑動報告，包含圖文排版和（survey / graph 類報告）關係總圖。

**技術約束：**
- 必須是單一 HTML 文件（CSS / JS 全部內嵌，不依賴外部文件）
- 關係總圖必須使用 D3.js 實現力導向佈局，且必須可交互
- 在移動端和桌面端均可正常閱讀

**內容約束：**
- 每個視覺塊最多 3 個核心信息點
- 不得使用 `——`
- 不得放置大段 prose

---

#### phyra-md-reporter

- tools: Read, Write
- skills: phyra-md-report-format

**職責：** 撰寫各類 MD 格式報告和筆記，按照 phyra-md-report-format 中定義的模板撰寫。在生成前，必須讀取 `.claude/skills/phyra-md-report-format/templates/` 中對應的模板文件。

**行為約束：**
- 必須在文件第一行標記報告類型和生成日期
- 不使用 `---` 作為分隔線
- 不以任何總結性套話結尾
- 禁止 `——`

---

### 寫作規劃群

---

#### phyra-paper-writer

- tools: Read, Write, Edit
- skills: phyra-paper-writing, phyra-academic-reading

**職責：** 執行論文文字的撰寫或修改。AT 模式下整合多個 story-architect 的方案後執行。

**修改草稿的操作規範：**
- 必須創建副本，絕不覆蓋原始文件
- 副本命名：`{original-name}-phyra-{YYYYMMDD}.{ext}`
- 每一處重大修改（超過一句話的改動）必須在旁邊加入注釋，說明修改理由

**AT 模式下的決策規範：**
- 收到多個 story-architect 的方案後，必須先輸出一個明確的決策說明（選了哪個方向、為什麼、捨棄了什麼、融合了什麼），再開始撰寫
- 不得在未說明決策依據的情況下直接開始寫作

**禁止的寫作行為：**
- 不得在未接到明確指令的情況下改變論文的核心 claim
- 不得刪除原作者的實驗數據或引用，除非得到明確授權

---

#### phyra-experiment-planner

- tools: Read, Write
- skills: phyra-experiment-design, phyra-research-scoring

**職責：** 設計實驗方案，輸出可執行的實驗清單。

**輸出格式（每個實驗條目）：**
```
- 實驗名稱：
- 假說：如果 [X]，則 [Y 指標] 會 [上升/下降]，因為 [Z]
- 方法：具體如何實施
- 預期結果：
- 失敗模式：如果假說錯誤，結果會是什麼樣的？
- 優先級：[必做 / 建議做 / 有時間再做]
```

**行為約束：**
- 每個消融實驗必須有明確假說，禁止「為了消融而消融」
- Baseline 選擇必須說明為什麼選這個而不是其他，必須涵蓋 phyra-experiment-design 要求的三類 baseline

---

#### phyra-story-architect

- tools: Read, Write
- skills: phyra-paper-writing, phyra-academic-reading

**職責：** 設計論文故事線和貢獻框架。AT 模式下多開實例，各自採用不同敘事策略。

**AT 模式下各實例的角色定義：**
- 實例 A（保守型）：只聲稱材料明確支持的貢獻，選擇最穩健、最難被反駁的故事線，優先考慮審稿人的疑慮
- 實例 B（激進型）：識別材料可能支持的最大化新穎性框架，找到最強的貢獻聲稱，再評估實驗能否支撐
- 實例 C（對抗型）：主動為任何提出的故事線找最強的反駁，輸出「這個故事在哪裡最脆弱」的分析

**每個實例的輸出必須包含：**
1. 故事線草案（三句話版本：問題 → gap → 貢獻）
2. 貢獻聲稱草案（3-4 條）
3. 「這個故事在以下情況下會失敗...」（列出 2-3 個風險條件）

> 故事不是包裝，故事是結構。一個好的論文故事線不是修辭策略，而是讓讀者理解為什麼這個方法在邏輯上是必然的那條路徑。如果你的故事線讓人感覺「原來如此」，說明它是對的；如果讓人感覺「原來你是這樣說的」，說明它還是包裝。

**敘事慣例：**
[待填寫]

---

## Commands

> 每個 command 是一個 YAML frontmatter 的 MD 文件，放在 `.claude/commands/`。每個 command 的 prompt 描述完整的 workflow，末尾有一個分支：AT 模式走 teams spawn，NT 模式走 sequential subagents。一個 command 內部處理兩條路徑。
>
> 用戶聲明模式的方式：
> - NT 模式（默認）：`/phyra-paper-review [文件路徑]`
> - AT 模式：`/phyra-paper-review --at [文件路徑]`

---

#### /phyra-paper-review（審稿）

- **NT：**
  1. `phyra-paper-parser`（解析論文，輸出結構化內容）
  2. `phyra-content-analyst`（深度分析，輸出 claim map + 實驗充分性評估）
  3. `phyra-peer-reviewer-positive`（讀論文 + content-analyst 報告，輸出草稿至 `.phyra/drafts/review-positive.md`）
  4. `phyra-peer-reviewer-negative`（讀論文 + content-analyst 報告，輸出草稿至 `.phyra/drafts/review-negative.md`）
  5. `phyra-peer-reviewer-chair`（只讀兩份草稿，分歧分析 → 向 reviewer 確認 → 閱讀 `review-example.md` 作為格式與深度參考 → 獨立撰寫 `peer-review-report.md` 和 `review-scoring-report.md`）

- **AT：**
  1. `phyra-paper-parser`（同步，必須先完成）
  2. `phyra-content-analyst`（同步，必須先完成）
  3. `[phyra-peer-reviewer-positive ∥ phyra-peer-reviewer-negative]`（平行，各自寫草稿至 `.phyra/drafts/`）
  4. `phyra-peer-reviewer-chair`（可直接向兩位 reviewer 發訊息確認分歧，獨立撰寫兩份最終報告）

---

#### /phyra-paper-read（讀論文）

- **NT：**
  1. `phyra-paper-parser`（解析論文）
  2. `phyra-content-analyst`（深度分析，生成分析報告）
  3. `phyra-html-reporter`（基於分析報告，製作 HTML 滑動報告）
  4. `phyra-md-reporter`（基於分析報告，撰寫論文閱讀筆記 MD）

- **AT：**
  1. `phyra-paper-parser`（同步，必須先完成）
  2. `phyra-content-analyst`（同步，必須先完成）
  3. `[phyra-html-reporter ∥ phyra-md-reporter]`（平行輸出兩份報告）

---

#### /phyra-paper-survey（找論文）

- **NT：**
  1. 解析用戶 query（接受：paper 文件 / 文字描述 / 任務表述 / 研究名稱）
  2. `phyra-literature-searcher`（單線搜索，記錄搜索日誌）
  3. `phyra-relationship-mapper`（分析關聯性、構建邏輯線）
  4. `phyra-html-reporter`（製作含力導向關係總圖的 HTML 滑動報告）
  5. `phyra-md-reporter`（撰寫論文調查筆記 MD）

- **AT：**
  1. 解析用戶 query
  2. `[phyra-literature-searcher-A（關鍵詞正搜）∥ phyra-literature-searcher-B（引用反查）∥ phyra-literature-searcher-C（相關領域擴展）]`（三線平行，各自記錄搜索日誌）
  3. `phyra-relationship-mapper`（整合三條搜索線，去重後分析關聯性）
  4. `[phyra-html-reporter ∥ phyra-md-reporter]`（平行輸出兩份報告）

---

#### /phyra-paper-graph（論文圖譜）

- **NT：**
  1. 解析 paper list（接受：標題列表 / bib 文件 / 混合格式）
  2. 依序對每篇論文跑 `phyra-content-analyst`
  3. `phyra-relationship-mapper`（整合所有論文分析，建立完整關聯圖譜）
  4. `phyra-html-reporter`（製作含力導向關係總圖的 HTML 滑動報告）
  5. `phyra-md-reporter`（撰寫論文關聯筆記 MD）

- **AT：**
  1. 解析 paper list，按篇數均分批次（建議每批 3-5 篇）
  2. `[phyra-content-analyst-1（批次 A）∥ phyra-content-analyst-2（批次 B）∥ ...]`（平行分析各批次）
  3. `phyra-relationship-mapper`（等所有批次完成後，整合全部分析）
  4. `[phyra-html-reporter ∥ phyra-md-reporter]`（平行輸出兩份報告）

---

#### /phyra-paper-write（論文撰寫）

- **NT（從零開始）：**
  1. `phyra-story-architect`（設計故事線，輸出三句話版本 + 貢獻聲稱草案 + 風險條件）
  2. `phyra-experiment-planner`（基於故事線，設計實驗清單，含假說和優先級）
  3. `phyra-paper-writer`（整合故事線和實驗方案，撰寫論文框架或完整草稿）
  4. `phyra-md-reporter`（輸出規劃分析報告 MD）

- **NT（有草稿）：**
  1. `phyra-paper-parser`（解析現有材料）
  2. `phyra-content-analyst`（診斷草稿現況：故事線是否清晰、方法邏輯是否自洽、實驗是否充分）
  3. `phyra-story-architect`（基於診斷，評估故事線並提出優化方向）
  4. `phyra-experiment-planner`（基於診斷，規劃需要新增或修改的實驗）
  5. `phyra-paper-writer`（執行修改，創建副本，每處重大改動附注釋）
  6. `phyra-md-reporter`（輸出改進分析報告 MD）

- **AT（從零開始）：**
  1. `[phyra-story-architect-A（保守型）∥ phyra-story-architect-B（激進型）∥ phyra-story-architect-C（對抗型）]`（三線平行，各自輸出完整故事線方案 + 風險分析）
  2. `phyra-experiment-planner`（閱讀三份故事線方案，設計能同時支撐多個方向、最具鑑別力的實驗）
  3. `phyra-paper-writer`（輸出決策說明 → 整合三方方案 → 撰寫論文）
  4. `phyra-md-reporter`（輸出決策分析與規劃報告 MD）

- **AT（有草稿）：**
  1. `phyra-paper-parser`（同步，必須先完成）
  2. `[phyra-content-analyst ∥ phyra-story-architect ∥ phyra-experiment-planner]`（三者同時從各自視角診斷草稿，互不溝通，保持視角獨立）
  3. `phyra-paper-writer`（閱讀三方診斷 → 輸出決策說明 → 執行修改，創建副本）
  4. `phyra-md-reporter`（輸出改進分析報告 MD）

---

## 設計決策注意事項

- **phyra-paper-parser** 在所有 workflow 裡都是同步的第一步，不適合放進 AT 的平行階段。

- **phyra-md-reporter** 和 **phyra-html-reporter** 在 AT 裡幾乎每個 workflow 都可以平行，這是最容易獲得的 AT 收益。

- **同一職責多策略並行**（同一 subagent 多開實例，各自採用不同策略）的三個使用場景：
  - `/phyra-paper-survey` 裡的 `phyra-literature-searcher`（關鍵詞正搜 / 引用反查 / 相關領域擴展）
  - `/phyra-paper-write` 裡的 `phyra-story-architect`（保守型 / 激進型 / 對抗型）
  - `/phyra-paper-graph` 裡的 `phyra-content-analyst`（按 paper list 拆批次）

- **phyra-peer-reviewer-chair** 的物理隔離：`allowed-read-paths` 限制為 `.phyra/drafts/`；positive 和 negative reviewer 必須將草稿寫入該目錄後 chair 才能讀取。

- **phyra-peer-reviewer-chair** 載入 `phyra-typography` 和 `phyra-soul` skills，兩份最終報告由 chair 獨立撰寫，不調用 phyra-md-reporter。

- **phyra-peer-reviewer-chair** 的工作流程：分歧分析 → 向 reviewer 查詢確認 → 獨立撰寫，禁止跳過分歧分析直接輸出。

- **phyra-paper-writer** 在 AT 模式下，必須先輸出決策說明再開始撰寫。

---

## 項目文件結構

```
phyra/
│
├── README.md                          # 項目介紹、快速開始、功能概覽
├── INSTALL.md                         # 安裝說明（見下方）
├── CHANGELOG.md                       # 版本更新記錄
├── LICENSE                            # 開源許可證
│
├── .claude/                           # Claude Code 插件主體（安裝後複製到用戶目錄）
│   │
│   ├── skills/                        # 所有 skills
│   │   ├── phyra-academic-reading/
│   │   │   └── SKILL.md
│   │   ├── phyra-peer-review-criteria/
│   │   │   └── SKILL.md
│   │   ├── phyra-research-scoring/
│   │   │   └── SKILL.md
│   │   ├── phyra-literature-search/
│   │   │   └── SKILL.md
│   │   ├── phyra-citation-network/
│   │   │   └── SKILL.md
│   │   ├── phyra-html-slide-format/
│   │   │   └── SKILL.md
│   │   ├── phyra-html-color-system/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   │       ├── palette-light.md
│   │   │       ├── palette-dark.md
│   │   │       ├── bg-layers.md
│   │   │       ├── slide-theme.md
│   │   │       ├── scroll-theme.md
│   │   │       ├── graph-theme.md
│   │   │       └── switcher.js.md
│   │   ├── phyra-md-report-format/
│   │   │   ├── SKILL.md               # skill 定義，引用模板目錄
│   │   │   └── templates/             # 各類報告模板（agent 按需讀取）
│   │   │       ├── paper-read-notes.template.md
│   │   │       ├── paper-survey-notes.template.md
│   │   │       ├── paper-graph-notes.template.md
│   │   │       └── paper-write-plan.template.md
│   │   ├── phyra-paper-writing/
│   │   │   └── SKILL.md
│   │   ├── phyra-experiment-design/
│   │   │   └── SKILL.md
│   │   └── phyra-typography/
│   │       └── SKILL.md
│   │
│   ├── support/                       # 共用參考文件
│   │   └── phyra-ai-vocab-blacklist.md
│   │
│   ├── agents/                        # 所有 subagent 定義
│   │   ├── phyra-paper-parser.md
│   │   ├── phyra-content-analyst.md
│   │   ├── phyra-peer-reviewer-positive.md
│   │   ├── phyra-peer-reviewer-negative.md
│   │   ├── phyra-peer-reviewer-chair.md
│   │   ├── phyra-literature-searcher.md
│   │   ├── phyra-relationship-mapper.md
│   │   ├── phyra-html-reporter.md
│   │   ├── phyra-md-reporter.md
│   │   ├── phyra-paper-writer.md
│   │   ├── phyra-experiment-planner.md
│   │   └── phyra-story-architect.md
│   │
│   └── commands/                      # 所有 command 定義
│       ├── phyra-paper-review.md
│       ├── phyra-paper-read.md
│       ├── phyra-paper-survey.md
│       ├── phyra-paper-graph.md
│       └── phyra-paper-write.md
│
├── .phyra/                            # Phyra 運行時數據（不安裝，在用戶項目目錄生成）
│   ├── drafts/                        # 審稿草稿暫存（gitignored）
│   ├── logs/                          # 搜索日誌、運行日誌（gitignored）
│   └── examples/                     # 範例文件（隨插件安裝）
│       └── review-example.md
│
├── docs/                              # 項目文檔
│   ├── phyra-architecture.md          # 本文件（架構設計文檔）
│   ├── phyra-ai-vocab-blacklist.md    # AI 詞彙黑名單
│   ├── phyra-ai-vocab-whitelist.md    # AI 詞彙白名單（待建立）
│   ├── phyra-ai-review-checklist.md   # 領域評審清單（待建立）
│   ├── phyra-ai-design-colorlist.md   # HTML 配色規範（待建立）
│   └── phyra-ai-writing-conventions.md # 領域寫作慣例（待建立）
│
├── scripts/
│   ├── install.sh                     # 安裝腳本（macOS / Linux）
│   ├── install.ps1                    # 安裝腳本（Windows PowerShell）
│   └── uninstall.sh                   # 卸載腳本
│
└── .gitignore
```

**`.gitignore` 應包含的條目：**
```
.phyra/drafts/
.phyra/logs/
*.phyra-*.md         # phyra 生成的草稿副本
```

**`phyra-md-report-format/SKILL.md` 的載入邏輯說明：**
skill 文件描述模板體系的原則；具體模板存放在 `templates/` 子目錄，agent 按需讀取。Claude Code 在加載 skill 時，SKILL.md 的描述會告知 agent「在生成對應類型報告前，讀取 `templates/{type}.template.md`」，實現模板的按需加載而非全量預加載，節省 context。

---

## 安裝方式

### 方式一：腳本安裝（推薦）

```bash
git clone https://github.com/[username]/phyra.git
cd phyra
chmod +x scripts/install.sh
./scripts/install.sh
```

腳本執行以下操作：
1. 將 `.claude/skills/phyra-*` 複製到 `~/.claude/skills/`
2. 將 `.claude/agents/phyra-*` 複製到 `~/.claude/agents/`
3. 將 `.claude/commands/phyra-*` 複製到 `~/.claude/commands/`
4. 將 `.phyra/examples/` 複製到 `~/.phyra/examples/`
5. 提示用戶是否要自動追加 Agent Teams 配置到 `~/.claude/settings.json`

### 方式二：項目級安裝（不污染全局）

如果只想在特定項目中使用 Phyra：

```bash
cd your-project/
git clone https://github.com/[username]/phyra.git .phyra-plugin
cp -r .phyra-plugin/.claude/skills/phyra-* .claude/skills/
cp -r .phyra-plugin/.claude/agents/phyra-* .claude/agents/
cp -r .phyra-plugin/.claude/commands/phyra-* .claude/commands/
mkdir -p .phyra/examples
cp .phyra-plugin/.phyra/examples/* .phyra/examples/
```

### 方式三：未來計劃（Claude Code Plugin Marketplace）

待 Claude Code Plugin 分發機制穩定後，Phyra 計劃提交至 Plugin Marketplace，屆時可通過：
```
/plugin install phyra
```
一鍵安裝。

### 卸載

```bash
./scripts/uninstall.sh
```

腳本移除所有 `phyra-` 前綴的 skills、agents 和 commands，不觸碰用戶自定義文件。

### 更新

```bash
cd phyra/
git pull
./scripts/install.sh --update
```

`--update` 標記會覆蓋已有的 phyra 文件，不影響用戶自定義的非 phyra 文件。

---

## 關聯文件索引

| 文件 | 位置 | 狀態 | 負責方 |
|---|---|---|---|
| 架構設計文檔 | `docs/phyra-architecture.md` | 持續更新 | Nubo |
| AI 詞彙黑名單 | `docs/phyra-ai-vocab-blacklist.md` | 已建立（可追加） | Nubo + Claude Code |
| AI 詞彙白名單 | `docs/phyra-ai-vocab-whitelist.md` | 待建立 | Claude Code |
| 領域評審清單 | `docs/phyra-ai-review-checklist.md` | 待建立 | Claude Code |
| HTML 配色規範 | `docs/phyra-ai-design-colorlist.md` | 待建立 | Claude Code |
| 領域寫作慣例 | `docs/phyra-ai-writing-conventions.md` | 待建立 | Claude Code |
| Review 範例 | `.phyra/examples/review-example.md` | 已建立（匿名化） | Nubo |
| 報告模板（閱讀） | `.claude/skills/phyra-md-report-format/templates/paper-read-notes.template.md` | 已規劃 | Claude Code |
| 報告模板（調查） | `.claude/skills/phyra-md-report-format/templates/paper-survey-notes.template.md` | 已規劃 | Claude Code |
| 報告模板（圖譜） | `.claude/skills/phyra-md-report-format/templates/paper-graph-notes.template.md` | 已規劃 | Claude Code |
| 報告模板（撰寫） | `.claude/skills/phyra-md-report-format/templates/paper-write-plan.template.md` | 已規劃 | Claude Code |