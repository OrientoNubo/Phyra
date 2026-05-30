---
name: html-slide-format
description: "Use this skill when generating HTML slide reports or visual reports. Provides structure rules, font specs, visual constraints, and graph layout requirements. For colors and themes, see html-color-system."
---

# Phyra HTML Slide Format

Layout structure specification for HTML reports, ensuring all visual outputs have consistent information hierarchy and layout. For color rules, refer to the `html-color-system` skill.

## Structure Specification

- Use vertical scrolling (scroll) rather than pagination
- Each section is an independent visual block with clear visual boundaries
- Each block contains at most 3 core information points; more than 3 must be split
- Do not place long prose in slide blocks; prose belongs in MD reports
- All output is a single HTML file (single-file delivery)

## Relationship Graph (required for survey and graph type reports)

- Must use D3.js v7 force-directed layout, using SVG rather than Canvas
- Nodes are colored by cluster (clustered coloring)
- Edge thickness represents relationship strength
- Must support zoom (d3.zoom) and node dragging (d3.drag)
- Must be interactive (hover shows node details, click highlights related nodes)
- Multi-attribute nodes use SVG linearGradient for gradient colors
- Graph must include a legend

## Font Specification

Unless otherwise specified, prefer **Noto Sans TC**.

```css
font-family: 'Noto Sans TC', 'Helvetica Neue', Arial, sans-serif;
```

## Prohibited Visual Behaviors

- No more than two levels of nested lists
- No purely decorative elements (graphics unrelated to information)
- Must be a single HTML file; do not split into multiple files
- Typography constraints follow the `typography` skill

## Color System

> All color, theme, background layer, and theme switcher definitions have been moved to the `html-color-system` skill.
> Before generating an HTML report, you must also read that skill and its reference files.

## Reference File Reading Guide

Before generating HTML, read the following reference files as needed:

**Layout structure** (this skill):
- This file (`SKILL.md`) contains the complete layout structure specification

**Colors and themes** (`html-color-system` skill):
- `references/bg-layers.md` -- 3-layer background system and HTML structure template
- `references/switcher.js.md` -- Theme dropdown switcher JS
- `references/palette-light.md` + `references/palette-dark.md` -- 100 theme CSS definitions
- Read `references/slide-theme.md`, `references/scroll-theme.md`, or `references/graph-theme.md` based on report type
