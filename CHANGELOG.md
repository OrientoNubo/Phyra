# Changelog

## v0.3.0 (2026-04-06)

### Restructured as Official Claude Code Plugin
- Migrated to official Claude Code plugin format with `.claude-plugin/plugin.json` manifest
- Added marketplace support (`.claude-plugin/marketplace.json`)
- Removed `phyra-` prefix from all component names (plugin namespace `phyra:` handles namespacing)
- Translated all content from Chinese/English mixed to English-only (`main` branch)
- Chinese version preserved in `zh-hant` branch
- Removed custom install/uninstall scripts (replaced by plugin system)
- Removed `src/` wrapper directory (files now at plugin root)
- Removed `doc/` directory (content merged into README.md)
- Commands now invoked as `/phyra:paper-read`, `/phyra:paper-review`, etc.

## [0.2.1] - 2026-04-06

### Changed
- Background layers now use nipponcolors.com PNG assets (`texture.png`, `gloss.png`) instead of CSS-only fallbacks
- Theme switcher `<select>` text forced to black (`#1C1C1C`) on white background for readability
- Content width is now adjustable via a draggable handle on the right edge
- Graph containers now include a fullscreen toggle button

## [0.2.0] - 2026-04-05

### Added
- `phyra-typography` skill: independent typography constraints extracted from phyra-soul
- `phyra-html-color-system` skill: dedicated color system with 100 Japanese themes (42 light + 58 dark), 3-layer CSS background, dropdown theme switcher, and per-report-type color rules
- `phyra-ai-vocab-blacklist.md`: vocabulary blacklist for academic writing (6 categories, 61 entries)
- KaTeX LaTeX rendering support in HTML reports
- D3.js v7 graph interactivity (zoom, drag, gradient nodes)
- Unified footer format for all HTML reports

### Changed
- `phyra-peer-reviewer-chair` now loads `phyra-typography` and `phyra-soul` skills
- `phyra-html-slide-format` stripped of color content (moved to phyra-html-color-system)
- Theme switcher changed from Next/Random buttons to select dropdown + Random
- `phyra-paper-review` Step 5 explicitly instructs chair to read review-example.md
- `phyra-soul` typography rules replaced with reference to phyra-typography skill

### Removed
- `phyra-html-slide-format/references/` directory (4 files migrated to phyra-html-color-system)

## v0.1.0 (2026-04-04)

Initial release of Phyra.

- 10 Skills (academic reading, peer review, scoring, literature search, citation network, HTML/MD report formats, paper writing, experiment design, soul)
- 12 Subagents (paper parser, content analyst, dual reviewers + chair, literature searcher, relationship mapper, HTML/MD reporters, paper writer, experiment planner, story architect)
- 5 Commands (paper-review, paper-read, paper-survey, paper-graph, paper-write)
- 100-theme Japanese color system (nipponcolors.com)
- NT (sequential) and AT (Agent Teams parallel) execution modes
- Install scripts for macOS/Linux/Windows
