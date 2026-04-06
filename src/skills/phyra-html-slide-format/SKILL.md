---
name: phyra-html-slide-format
description: "Use this skill when generating HTML slide reports or visual reports. Provides structure rules, font specs, visual constraints, and graph layout requirements. For colors and themes, see phyra-html-color-system."
---

# Phyra HTML Slide Format

HTML 報告的版面結構規範，確保所有視覺輸出具有一致的信息層次和佈局。配色規則請參照 `phyra-html-color-system` skill。

## 結構規範

- 採用垂直滾動（scroll）而非翻頁（pagination）
- 每個 section 是一個獨立的視覺塊，有明確的視覺邊界
- 每個塊最多包含 3 個核心信息點；超過 3 個必須拆分
- 不得在 slide 塊中放置大段 prose；prose 屬於 MD 報告
- 所有輸出為單一 HTML 文件（single-file delivery）

## 關係總圖（survey 和 graph 類報告必備）

- 必須使用 D3.js v7 力導向佈局（force-directed layout），使用 SVG 而非 Canvas
- 節點按聚類著色（clustered coloring）
- 邊的粗細代表關係緊密程度
- 必須支援縮放（d3.zoom）和節點拖動（d3.drag）
- 必須可交互（hover 顯示節點詳情，點擊高亮相關節點）
- 多屬性節點使用 SVG linearGradient 漸變色
- 圖必須有圖例（legend）

## 字體規範

除非特別指定，否則優先使用 **Noto Sans TC**（思源黑體）。

```css
font-family: 'Noto Sans TC', 'Helvetica Neue', Arial, sans-serif;
```

## 禁止的視覺行為

- 禁止超過兩層嵌套列表
- 禁止純粹的裝飾性元素（與信息無關的圖形）
- 必須為單一 HTML 文件，不得拆分為多檔
- 排版約束遵循 `phyra-typography` skill

## 配色系統

> 所有配色、主題、背景層、主題切換器的定義已移至 `phyra-html-color-system` skill。
> 生成 HTML 報告前，必須同時讀取該 skill 及其 reference 文件。

## 參考檔案讀取指引

生成 HTML 前，依需求讀取以下參考檔案：

**版面結構**（本 skill）：
- 本文件（`SKILL.md`）即為版面結構的全部規範

**配色和主題**（`phyra-html-color-system` skill）：
- `references/bg-layers.md` — 三層背景系統和 HTML 結構範本
- `references/switcher.js.md` — 主題選單切換器 JS
- `references/palette-light.md` + `references/palette-dark.md` — 100 種主題 CSS
- 依報告類型讀取 `references/slide-theme.md`、`references/scroll-theme.md` 或 `references/graph-theme.md`
