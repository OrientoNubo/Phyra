# Scroll Long Report Color Rules

Color rules for scroll-based long reports such as Survey, Review, and Graph reports. Shares base elements (cards, tables, bold highlights) with slide-theme, but has additional long-form layout rules.

## Base Inheritance

This report type inherits all card, table, bold, formula, and tag styles from `slide-theme.md`. Only additional or different rules are listed below.

## Section Styles

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

## Blockquote Styles

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

## List Styles

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

## Defect Severity Markers

Used for defect severity markers in Peer Review reports:

```css
.defect-fatal   { color: #E83015; font-weight: 700; }
.defect-major   { color: #E98B2A; font-weight: 700; }
.defect-minor   { color: #5DAC81; font-weight: 600; }
.defect-suggest  { color: var(--p-text-secondary); font-weight: 600; }
```

## Secondary Text

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
