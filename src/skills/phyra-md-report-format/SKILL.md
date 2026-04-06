---
name: phyra-md-report-format
description: "Use this skill when generating MD format reports or notes. Provides structural principles for all report types and directs agents to load the corresponding template from templates/ before generating output."
---

# Phyra MD Report Format

此 skill 描述所有 MD 報告的結構原則。具體的報告模板以獨立文件存放於 `templates/` 目錄中，agent 在生成報告前應讀取對應的模板文件。

## 載入邏輯

在生成對應類型報告前，讀取 `templates/{type}.template.md`

## 可用模板

| 類型識別符 | 模板文件 | 說明 |
|-----------|---------|------|
| `paper-read-notes` | `templates/paper-read-notes.template.md` | 論文閱讀筆記 |
| `paper-survey-notes` | `templates/paper-survey-notes.template.md` | 論文調查筆記 |
| `paper-graph-notes` | `templates/paper-graph-notes.template.md` | 論文關聯筆記 |
| `paper-write-plan` | `templates/paper-write-plan.template.md` | 撰寫規劃報告 |

## 使用方式

1. 確認需要生成的報告類型
2. 讀取對應的模板文件：`templates/{type}.template.md`
3. 按照模板結構填寫內容
4. 確保符合下方的通用約束

## 所有 MD 報告的通用約束

- 第一行必須是報告類型標識和生成日期（格式見各模板）
- 所有數字必須有來源（論文頁碼 / 實驗結果 / 搜索記錄）
- 報告不得以總結性套話結尾
- 排版約束遵循 `phyra-typography` skill（禁止 `---` 分隔線、`——` 符號等）
