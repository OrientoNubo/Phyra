---
name: phyra-research-scoring
description: "Use this skill when generating research scoring reports for paper reviews. Provides the 5-dimension scoring system, weighted averages, grade mapping, and scoring constraints for /phyra-paper-review."
---

# phyra-research-scoring

**定位：** 研究評分框架，專門用於 `/phyra-paper-review` 的評分報告輸出。

---

## 技術發展路徑追蹤（必做）

- 必須識別至少 3 個直接前驅工作（predecessor works）
- 必須說明當前論文相對前驅工作的具體進展（不是泛泛的「改進了」）
- 必須識別當前論文試圖解決的、前驅工作遺留的問題
- 前驅工作必須按時間線排列，不得按重要性排列

---

## 評分維度（五維，各 1-10 分）

| 維度 | 描述 |
|---|---|
| 問題有效性（Problem Validity） | 問題是否值得解決，定義是否清晰 |
| 方法合理性（Method Soundness） | 方法邏輯是否自洽，假設是否成立 |
| 實驗充分性（Experimental Adequacy） | 實驗是否支撐聲稱，baseline 是否公平 |
| 新穎性（Novelty） | 與已有工作的本質差異 |
| 可重現性（Reproducibility） | 細節是否足夠，能否被他人復現 |

---

## 加權平均分對應等級

| 等級 | 數字範圍 | 含義 |
|---|---|---|
| Strong Accept | 8.5 - 10.0 | 在核心維度上明顯優於現有工作 |
| Accept | 7.0 - 8.4 | 貢獻清晰，問題次要，可接受 |
| Weak Accept | 5.5 - 6.9 | 有價值但存在需要修復的重大問題 |
| Borderline | 4.5 - 5.4 | 正負 reviewer 存在實質分歧 |
| Weak Reject | 3.0 - 4.4 | 當前版本不充分，修改後可重投 |
| Reject | 1.0 - 2.9 | 存在 fatal flaw，revision 無法修復 |

---

## 加權方式

各維度加權方式：

- 問題有效性 × 0.15
- 方法合理性 × 0.30
- 實驗充分性 × 0.30
- 新穎性 × 0.15
- 可重現性 × 0.10

加權平均分 = 問題有效性 × 0.15 + 方法合理性 × 0.30 + 實驗充分性 × 0.30 + 新穎性 × 0.15 + 可重現性 × 0.10

---

## 約束

- 每個維度的分數必須附帶具體理由，不得出現裸分
- 評分不得只基於結果數字的好壞；結果好但方法有根本缺陷的論文不應高分
- 加權平均分與等級不符時，必須在報告中說明原因（如單一維度的 fatal flaw 拉低整體）
