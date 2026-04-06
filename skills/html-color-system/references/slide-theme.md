# Slide Report Color Rules

Color rules for paged/scrolling slide reports such as Paper Read reports.

## Card Styles

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

## Heading Styles

```css
h1, h2, h3 {
  color: var(--p-text);
}

h1 { font-size: 1.8rem; }
h2 { font-size: 1.4rem; border-bottom: 2px solid var(--p-border); padding-bottom: 8px; }
h3 { font-size: 1.1rem; }
```

## Bold Highlight

Important text uses not only bold weight but also a highlight background:

```css
strong {
  background: var(--p-bold-highlight);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 700;
}
```

## Table Styles

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

/* Light mode: table header uses dark text */
[data-theme-mode="light"] th {
  color: #1C1C1C;
}

/* Dark mode: table header uses light text */
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

## Formula Block Styles

Formula block background and text colors must match cards; do not use special background colors:

```css
.formula, .katex-display, pre.math {
  background: var(--p-formula-bg);
  color: var(--p-text);
  padding: 12px 16px;
  border-radius: 6px;
  border: 1px solid var(--p-border);
  overflow-x: auto;
}

/* Inline formulas */
.katex, code.math {
  color: var(--p-text);
  background: transparent;
}
```

## LaTeX Rendering

When a report contains math formulas, KaTeX must be embedded for rendering:

```html
<!-- Embed KaTeX in <head> -->
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

Notes:
- If the report contains no math formulas, KaTeX embedding is not needed
- KaTeX is loaded via CDN (reports are local HTML files, CDN requires internet connection)
- Formula blocks should not have a special background color different from text blocks

## Tag Styles

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

## Score Bar Styles

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
