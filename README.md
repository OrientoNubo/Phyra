# Phyra

> Phyra draws its name from Epiphyllum, the night-blooming cereus -- a flower that blooms only in darkness and silence, vanishing before dawn. Like its namesake, Phyra is designed to do its work precisely, quietly, with every ounce of effort, and without excess. Though the flower fades, its fragrance lingers.

---

## About

Phyra 是建立在 Agents 協作之上的學術研究插件庫，面向計算機科學方向的 AI 研究，目前主要支持 Claude Code。

Phyra is an academic research plugin library for Claude Code, built on collaborative multi-agent architecture. It targets computer science and AI research, with primary support for **Computer Vision**, **Machine Learning**, and **Deep Learning**.

The system is composed of **Skills**, **Subagents**, and **Commands**, providing research assistance with reliability, self-verification, and systematic rigor.

Phyra is a purely academic open-source project. Commercial use and any derived commercial activities are prohibited.

---

## Features

Phyra provides five slash commands, each orchestrating a pipeline of specialized subagents.

### /phyra-paper-review -- Peer Review

Dual-reviewer peer review with an AC (Area Chair) process. Two independent reviewers (one constructive, one adversarial) each produce a review draft. An AC chair then analyzes disagreements between the reviewers, conducts a reconciliation process, and produces a final peer review report with scoring.

### /phyra-paper-read -- Paper Reading

Systematic paper reading using the TP-V (Technical Parsing and Verification) framework. Parses the paper, performs deep content analysis (claim mapping, experimental sufficiency evaluation), and outputs both an interactive HTML slide report and a structured Markdown reading note.

### /phyra-paper-survey -- Literature Survey

Literature search and relationship mapping. Accepts a paper file, text description, task statement, or research topic as input. Searches the literature, analyzes relationships and logical threads, and produces an HTML report with a force-directed relationship graph alongside a Markdown survey note.

### /phyra-paper-graph -- Paper Relationship Graph

Builds a citation network and relationship graph from a list of papers. Accepts title lists, BibTeX files, or mixed formats. Analyzes each paper, maps relationships across the entire set, and outputs an interactive HTML visualization and a Markdown relationship note.

### /phyra-paper-write -- Paper Writing

End-to-end paper writing assistance, from storyline design through experiment planning to draft writing. Supports both starting from scratch and revising an existing draft. When starting fresh, designs a storyline (with a three-sentence version, contribution claims, and risk conditions), plans experiments with hypotheses and priorities, and produces a full paper framework or draft.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/[username]/phyra.git
cd phyra

# 2. Install
chmod +x scripts/install.sh
./scripts/install.sh

# 3. Use (in any project directory)
/phyra-paper-read path/to/paper.pdf
```

For detailed installation options, see [INSTALL.md](INSTALL.md).

---

## Execution Modes

Every command supports two execution modes:

- **NT mode (default)** -- Sequential execution. Subagents run one after another in a fixed pipeline. No special configuration required.

  ```
  /phyra-paper-review paper.pdf
  ```

- **AT mode (Agent Teams)** -- Parallel execution. Where the workflow allows, subagents run concurrently using Claude Code's Agent Teams feature. Requires Agent Teams to be enabled.

  ```
  /phyra-paper-review --at paper.pdf
  ```

To enable Agent Teams, add the following to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

---

## Architecture

```
User
 |
 v
Command (/phyra-paper-*)
 |
 |--- [NT mode] ---> Subagent 1 -> Subagent 2 -> ... -> Output
 |
 |--- [AT mode] ---> Subagent 1 -> [Subagent 2a || 2b || 2c] -> Subagent 3 -> Output
```

The three-layer architecture:

| Layer      | Count | Role                                                    |
|------------|-------|---------------------------------------------------------|
| Skills     | 12    | Atomic capabilities (reading, reviewing, scoring, searching, reporting, writing, typography, color system, etc.) |
| Subagents  | 12    | Specialized agents that execute skills (parser, analyst, dual reviewers, chair, searcher, mapper, reporters, writer, planner, architect) |
| Commands   | 5     | User-facing slash commands that orchestrate subagent pipelines |

### NT vs AT Pipeline Example: /phyra-paper-review

**NT (Sequential):**

```
paper-parser -> content-analyst -> reviewer-positive -> reviewer-negative -> chair
```

**AT (Parallel):**

```
paper-parser -> content-analyst -> [reviewer-positive || reviewer-negative] -> chair
```

In AT mode, the two reviewers run in parallel and the chair can communicate directly with both reviewers to resolve disagreements.

---

## Components Overview

### Skills (12)

Academic reading, peer review, review scoring, literature search, citation network analysis, HTML report generation, Markdown report generation, paper writing, experiment design, soul (core reasoning guidelines), typography constraints (`phyra-typography` -- 排版約束（排版禁令、格式一致性）), and HTML color system (`phyra-html-color-system` -- HTML 配色系統（100 種日本傳統色、三層背景、主題切換）).

> Note: The color system was separated from `phyra-html-slide-format` into the dedicated `phyra-html-color-system` skill.

### Subagents (12)

Paper parser, content analyst, positive reviewer, negative reviewer, AC chair, literature searcher, relationship mapper, HTML reporter, Markdown reporter, paper writer, experiment planner, and story architect.

### Commands (5)

| Command                | Description                                      |
|------------------------|--------------------------------------------------|
| `/phyra-paper-review`  | Dual-reviewer peer review with AC chair          |
| `/phyra-paper-read`    | Systematic paper reading with TP-V framework     |
| `/phyra-paper-survey`  | Literature search and relationship mapping        |
| `/phyra-paper-graph`   | Paper relationship graph from citation analysis   |
| `/phyra-paper-write`   | Paper writing from storyline to experiments       |

---

## Requirements

- **Claude Code CLI** with Agent Teams support (for AT mode)
- macOS, Linux, or Windows (WSL)

---

## License

**CC BY-NC 4.0** (Creative Commons Attribution-NonCommercial 4.0 International)

This project is for academic purposes only. Commercial use is strictly prohibited.

---

## Credits

- Color system: 100-theme Japanese color palette from [nipponcolors.com](https://nipponcolors.com)

---

## Links

- [Installation Guide](INSTALL.md)
- [Changelog](CHANGELOG.md)
- [Architecture Document](doc/Phyra-architecture.md)
