---
name: html-color-system
description: "Color system for all Phyra HTML reports. Provides 100 Japanese color themes (from nipponcolors.com) with light/dark classification, 3-layer background, theme switcher, and per-report-type color rules."
---

# Phyra HTML Color System

Color system for all Phyra HTML reports. Based on 100 traditional Japanese colors from nipponcolors.com, divided into light themes (42) and dark themes (58), with automatic color adaptation for text, cards, formulas, and other elements.

## Light/Dark Classification Rules

Classification is based on the `--theme-text` value.
- `#1C1C1C` (dark text) → **Light themes** (bright background, dark text)
- `#F5F2EB` (light text) → **Dark themes** (dark background, light text)

This classification is set on the `<html>` element via the `data-theme-mode` attribute (`light` or `dark`), managed automatically by the theme switcher.

## CSS Variable Contract

### Base Variables (defined per theme)

| Variable | Purpose |
|----------|---------|
| `--theme-primary` | Theme color (base color) |
| `--theme-light` | Light tone (card background candidate) |
| `--theme-accent` | Accent color (CTA, chart main line) |
| `--theme-dark` | Dark tone (dark backgrounds, navigation) |
| `--theme-neutral` | Soft base (surface, dividers) |
| `--theme-text` | Recommended text color |

### Semantic Aliases (mapped from theme variables)

```css
:root {
  --p-primary : var(--theme-primary);
  --p-light   : var(--theme-light);
  --p-accent  : var(--theme-accent);
  --p-dark    : var(--theme-dark);
  --p-neutral : var(--theme-neutral);
  --p-text    : var(--theme-text);
}
```

### Derived Variables (auto-set by light/dark mode)

```css
/* Light mode */
[data-theme-mode="light"] {
  --p-bg-card        : rgba(255, 255, 255, 0.92);
  --p-formula-bg     : rgba(255, 255, 255, 0.92);
  --p-border         : rgba(28, 28, 28, 0.12);
  --p-text-secondary : rgba(28, 28, 28, 0.60);
  --p-bold-highlight : color-mix(in srgb, var(--p-accent) 15%, transparent);
  --p-gloss-top      : 0.22;
  --p-gloss-mid      : 0.06;
}

/* Dark mode */
[data-theme-mode="dark"] {
  --p-bg-card        : rgba(0, 0, 0, 0.35);
  --p-formula-bg     : rgba(0, 0, 0, 0.35);
  --p-border         : rgba(245, 242, 235, 0.12);
  --p-text-secondary : rgba(245, 242, 235, 0.60);
  --p-bold-highlight : color-mix(in srgb, var(--p-accent) 20%, transparent);
  --p-gloss-top      : 0.10;
  --p-gloss-mid      : 0.03;
}
```

## Theme Index (100 themes)

The full lookup table — 42 light themes (all `#1C1C1C` text) + 58 dark themes (all `#F5F2EB` text), with kanji / id / primary color — lives in `references/palette-index.md`. Read that file when you need to pick a theme by name or compare colors. Do **not** read it when you only need a single theme's CSS — go directly to `references/palette-light.md` or `references/palette-dark.md`.

## Agent Reference Guide

Before generating an HTML report, read the following reference files based on report type:

### Required for all HTML reports

1. `references/bg-layers.md` -- 3-layer background system and HTML structure template
2. `references/switcher.js.md` -- Theme dropdown switcher JS
3. Corresponding palette files: `references/palette-light.md` and `references/palette-dark.md`

### Additional reads by report type

| Report Type | Additional References |
|-------------|----------------------|
| Paper Read (slides) | `references/slide-theme.md` |
| Paper Survey (scroll + graph) | `references/scroll-theme.md` + `references/graph-theme.md` |
| Paper Graph (scroll + graph) | `references/scroll-theme.md` + `references/graph-theme.md` |
| Peer Review (scroll) | `references/scroll-theme.md` |
| Paper Write (scroll) | `references/scroll-theme.md` |

## Unified Footer

All HTML reports must include a unified footer at the bottom:

```html
<footer class="phyra-footer">
  Phyra NT Workflow | Paper Read Report | 2026-04-05
</footer>
```

Format: `Phyra {NT|AT} Workflow | {Report Type} | {YYYY-MM-DD}`

Report Type allowed values: Paper Read Report, Peer Review Report, Paper Survey Report, Paper Graph Report, Paper Write Report

Default theme: keshizumi. Other recommended themes: hanada, kurenai, yamabuki, fujimurasaki
