---
name: phyra-typography
description: "Typography and formatting constraints for all Phyra outputs. Loaded by all agents and commands to enforce consistent typographic standards."
---

# Phyra Typography

> 此 skill 定義所有 Phyra 輸出的排版約束。所有 agent 和 command 必須遵守。

## 排版禁令

- 禁止使用 `——`（中文破折號）作為連接符或分隔符。使用逗號、分號或重新組織句子
- 禁止使用 `---` 作為段落間的分隔線。使用 `##` 標題作為結構分隔
- 禁止三層及以上的嵌套 bullet point；需要三層時，說明結構本身需要重新設計
- 禁止用加粗（`**`）作純裝飾；加粗只用於確實需要強調的術語或關鍵判斷

## 格式一致性

- MD 報告首行必須包含報告類型標識和生成日期
- 所有 MD 報告使用 `##` 標題層級作為主要結構單元
- HTML 報告中同樣禁止 `——` 字符
- 數字必須附帶來源（論文頁碼、實驗結果、搜索記錄）
