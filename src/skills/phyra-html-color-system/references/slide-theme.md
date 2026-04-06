# Slide 報告配色規則

適用於 Paper Read 等翻頁/滾動式 slide 報告的配色規則。

## 卡片（Card）樣式

```css
.slide-card {
  background: var(--p-bg-card);
  border: 1px solid var(--p-border);
  border-left: 4px solid var(--p-primary);
  border-radius: 8px;
  padding: 24px;
  color: var(--p-text);
}
```

## 標題樣式

```css
h1, h2, h3 {
  color: var(--p-text);
}

h1 { font-size: 1.8rem; }
h2 { font-size: 1.4rem; border-bottom: 2px solid var(--p-border); padding-bottom: 8px; }
h3 { font-size: 1.1rem; }
```

## 粗體高亮

重點文字不僅用粗體，還用高亮背景標記：

```css
strong {
  background: var(--p-bold-highlight);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 700;
}
```

## 表格樣式

```css
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

th {
  background: var(--p-primary);
  color: var(--p-text);
  padding: 8px 12px;
  text-align: left;
}

/* 淺色系：表頭用深色文字 */
[data-theme-mode="light"] th {
  color: #1C1C1C;
}

/* 深色系：表頭用淺色文字 */
[data-theme-mode="dark"] th {
  color: #F5F2EB;
}

td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--p-border);
  color: var(--p-text);
}

tr:hover td {
  background: rgba(128, 128, 128, 0.08);
}
```

## 公式塊樣式

公式塊的背景色和文字色必須與卡片一致，不使用特殊背景色：

```css
.formula, .katex-display, pre.math {
  background: var(--p-formula-bg);
  color: var(--p-text);
  padding: 12px 16px;
  border-radius: 6px;
  border: 1px solid var(--p-border);
  overflow-x: auto;
}

/* 行內公式 */
.katex, code.math {
  color: var(--p-text);
  background: transparent;
}
```

## LaTeX 渲染

當報告中包含數學公式時，必須嵌入 KaTeX 進行渲染：

```html
<!-- 在 <head> 中嵌入 KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '$', right: '$', display: false}
    ]
  });">
</script>
```

注意事項：
- 若報告中無數學公式，則不需要嵌入 KaTeX
- KaTeX 使用 CDN 載入（報告為本地 HTML，CDN 需要網路連線）
- 公式塊不應有與文字塊不同的特殊背景色

## 標籤（Tag）樣式

```css
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75em;
  font-weight: 600;
  background: color-mix(in srgb, var(--p-accent) 20%, transparent);
  color: var(--p-text);
}
```

## 評分條樣式

```css
.score-bar {
  height: 8px;
  border-radius: 4px;
  background: var(--p-border);
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  background: var(--p-accent);
  transition: width 0.6s ease;
}
```
