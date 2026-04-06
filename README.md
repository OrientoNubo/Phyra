# Phyra

> Phyra draws its name from Epiphyllum, the night-blooming cereus -- a flower that blooms only in darkness and silence, vanishing before dawn. Like its namesake, Phyra is designed to do its work precisely, quietly, with every ounce of effort, and without excess. Though the flower fades, its fragrance lingers.

## About

Phyra is an academic research plugin for Claude Code, built on collaborative multi-agent architecture. It targets computer science and AI research, with primary support for Computer Vision, Machine Learning, and Deep Learning.

The system is composed of Skills, Subagents, and Commands, providing research assistance with reliability, self-verification, and systematic rigor.

Phyra is a purely academic open-source project. Commercial use and any derived commercial activities are prohibited.

## Installation

### From Marketplace

```
/plugin marketplace add OrientoNubo/Phyra
/plugin install phyra@phyra-marketplace
```

### Local Development

```bash
git clone https://github.com/OrientoNubo/Phyra.git
claude --plugin-dir ./Phyra
```

## Commands

| Command | Description |
|---|---|
| `/phyra:paper-read` | Systematic paper reading with the TP-V (Three-Pass Verification) framework. Outputs an interactive HTML slide report and structured Markdown reading notes. |
| `/phyra:paper-review` | Dual-reviewer peer review with an AC (Area Chair) process. Two independent reviewers produce drafts; a chair reconciles disagreements and writes a final report with scoring. |
| `/phyra:paper-survey` | Literature search and relationship mapping. Accepts papers, text descriptions, or research topics. Produces an HTML report with force-directed graph and Markdown survey notes. |
| `/phyra:paper-graph` | Citation network and relationship graph from a list of papers. Accepts title lists, BibTeX files, or mixed formats. Outputs an interactive HTML visualization and Markdown notes. |
| `/phyra:paper-write` | End-to-end paper writing assistance, from storyline design through experiment planning to draft writing. Supports both starting from scratch and revising an existing draft. |

## Execution Modes

Every command supports two execution modes:

**NT mode (default)** -- Sequential execution. Subagents run one after another in a fixed pipeline.

```
/phyra:paper-review paper.pdf
```

**AT mode (Agent Teams)** -- Parallel execution. Where the workflow allows, subagents run concurrently using Claude Code's Agent Teams feature.

```
/phyra:paper-review --at paper.pdf
```

To enable Agent Teams, add the following to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Architecture

Three-layer architecture: Skills (12) -> Subagents (12) -> Commands (5)

```
User
 |
 v
Command (/phyra:paper-*)
 |
 |--- [NT mode] ---> Subagent 1 -> Subagent 2 -> ... -> Output
 |
 |--- [AT mode] ---> Subagent 1 -> [Subagent 2a || 2b || 2c] -> Subagent 3 -> Output
```

| Layer | Count | Role |
|---|---|---|
| Skills | 12 | Knowledge injection: reading frameworks, review criteria, scoring rubrics, search strategies, report formats, writing standards, typography rules, color system |
| Subagents | 12 | Specialized workers that load skills and execute tasks: parsing, analysis, reviewing, searching, mapping, reporting, writing, planning |
| Commands | 5 | User-facing entry points that orchestrate subagent pipelines |

### NT vs AT Pipeline Example: /phyra:paper-review

**NT (Sequential):**

```
paper-parser -> content-analyst -> reviewer-positive -> reviewer-negative -> chair
```

**AT (Parallel):**

```
paper-parser -> content-analyst -> [reviewer-positive || reviewer-negative] -> chair
```

In AT mode, the two reviewers run in parallel and the chair can communicate directly with both reviewers to resolve disagreements.

## Global Writing Constraints

All Phyra output is governed by strict writing constraints:

**Typography** -- No Chinese em-dashes as connectors, no horizontal rules as separators, no more than two levels of nested bullets, bold only for genuinely emphasized terms.

**Vocabulary** -- All output is checked against a vocabulary blacklist of overused AI-paper phrases. A whitelist curated from best papers at CVPR, ICCV, ECCV, NeurIPS, and AAAI is available as a writing reference.

**Claims** -- Degree words ("significantly", "substantially") must be backed by specific data. All contribution claims must be falsifiable; claims that cannot be disproven by experiment do not count as contributions.

**Citations** -- Every citation must state a specific reason for inclusion. Method descriptions must be based on reading the full methods section, not inferred from the abstract.

## Components

### Skills (12)

- **academic-reading** -- Systematic paper reading framework (TP-V three-pass method)
- **peer-review-criteria** -- Peer review evaluation dimensions and flaw classification
- **research-scoring** -- Five-dimension scoring rubric with weighted grades
- **literature-search** -- Multi-source search strategies (arXiv, Semantic Scholar, Google Scholar, domain DBs)
- **citation-network** -- Relationship type vocabulary and citation graph construction rules
- **html-slide-format** -- HTML slide report layout and structure specification
- **html-color-system** -- 100-theme Japanese color palette (42 light + 58 dark), three-layer CSS background, theme switcher
- **md-report-format** -- Markdown report templates for each report type
- **paper-writing** -- Academic writing standards: storyline construction, gap analysis, contribution claims
- **experiment-design** -- Experiment design norms: baseline selection, ablation design, evaluation metrics
- **typography** -- Typography constraints applied to all output
- **soul** -- Core reasoning philosophy: naturalistic ontology, BSEM aesthetics, care-based ethics

### Subagents (12)

- **paper-parser** -- Parses PDF/LaTeX/MD/Word papers into structured content
- **content-analyst** -- Deep analysis: claim mapping, method logic, experimental sufficiency
- **peer-reviewer-positive** -- Constructive reviewer; considers repair possibilities for each issue
- **peer-reviewer-negative** -- Adversarial reviewer; probes root causes behind surface problems
- **peer-reviewer-chair** -- AC chair; reads only review drafts, reconciles disagreements, writes final reports
- **literature-searcher** -- Searches across databases; in AT mode runs three parallel strategies
- **relationship-mapper** -- Builds relationship tables and narrative logical threads
- **html-reporter** -- Produces single-file interactive HTML slide reports with D3.js graphs
- **md-reporter** -- Writes structured Markdown reports from templates
- **paper-writer** -- Executes paper writing or revision; never overwrites originals
- **experiment-planner** -- Designs experiments with hypotheses, baselines, and ablation plans
- **story-architect** -- Designs storylines and contribution frameworks; in AT mode runs conservative, aggressive, and adversarial instances

## Requirements

- Claude Code CLI

## License

**CC BY-NC 4.0** (Creative Commons Attribution-NonCommercial 4.0 International)

This project is for academic purposes only. Commercial use is strictly prohibited.

## Credits

- Color system: 100-theme Japanese color palette from [nipponcolors.com](https://nipponcolors.com)
- Chinese version: available on the `zh-hant` branch
