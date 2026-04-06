# 滾動式長報告配色規則

適用於 Survey、Review、Graph 等滾動式長報告的配色規則。與 slide-theme 共享基礎元素（卡片、表格、粗體高亮），但有額外的長文排版規則。

## 基礎繼承

本報告類型繼承 `slide-theme.md` 的所有卡片、表格、粗體、公式、標籤樣式。以下僅列出額外或不同的規則。

## Section 樣式

```css
section {
  max-width: 100%;
  margin: 0 auto;
  padding: 40px 0;
}

section + section {
  border-top: 1px solid var(--p-border);
}
```

## Blockquote 樣式

```css
blockquote {
  border-left: 3px solid var(--p-accent);
  padding: 12px 20px;
  margin: 16px 0;
  background: color-mix(in srgb, var(--p-accent) 8%, transparent);
  color: var(--p-text);
  font-style: italic;
  border-radius: 0 6px 6px 0;
}
```

## 列表樣式

```css
ul, ol {
  padding-left: 20px;
  color: var(--p-text);
}

li {
  margin-bottom: 6px;
  line-height: 1.6;
}

li::marker {
  color: var(--p-accent);
}
```

## 缺陷等級標記

用於 Peer Review 報告中的缺陷等級標記：

```css
.defect-fatal   { color: #E83015; font-weight: 700; }
.defect-major   { color: #E98B2A; font-weight: 700; }
.defect-minor   { color: #5DAC81; font-weight: 600; }
.defect-suggest  { color: var(--p-text-secondary); font-weight: 600; }
```

## 次要文字

```css
.text-secondary {
  color: var(--p-text-secondary);
  font-size: 0.85em;
}

.text-muted {
  color: var(--p-text);
  opacity: 0.5;
  font-size: 0.8em;
}
```
