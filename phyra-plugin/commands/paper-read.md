---
description: "Read an academic paper. Always produces a structured Markdown analysis (and a viewer HTML). Optionally produces a fixed slide-deck HTML."
argument-hint: "<paper-file-path-or-arxiv-url> [--lang-out zh-TW] [--slide|--no-slide] [--at]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "Agent", "SendMessage", "AskUserQuestion"]
---

# /phyra:paper-read

This command delegates to the `paper-read` skill, which contains the full
v0.9.0 workflow:

```
preflight → bibliographer → paper-parser → extract_figures →
  paper-analyzer →
  (optional) paper-slide-maker
```

Load and execute `${CLAUDE_PLUGIN_ROOT}/skills/paper-read/SKILL.md` with
`$ARGUMENTS`. Follow that skill's steps verbatim. Do not duplicate the
workflow here — the skill is the single source of truth.

If `${CLAUDE_PLUGIN_ROOT}` is unset (skill auto-resolution failed for some
reason), abort with the message:

```
Phyra paper-read v0.9.0 requires ${CLAUDE_PLUGIN_ROOT} to locate skill scripts.
Reinstall the plugin: /plugin install phyra@phyra
```

> For bilingual translated PDF, see `/phyra:paper-translate`. The two
> commands share the cache dir `<cwd>/.phyra/.cache/<STEM>/` so running
> them on the same PDF (in either order) reuses parsed metadata.
