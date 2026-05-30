---
description: "Translate an academic paper into a side-by-side bilingual PDF using BabelDOC + Claude headless. Optionally also emits a translation-only PDF (--mono). Independent of /phyra:paper-read."
argument-hint: "<paper-file-path-or-arxiv-url> [--lang-out zh-TW] [--lang-in en] [--mono] [--qps 2] [--compress lossy|lossless|off] [--model sonnet]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "Agent"]
---

# /phyra:paper-translate

This command delegates to the `paper-translate` skill, which contains the
full v0.9.0 workflow:

```
preflight → resolve_input → (cache lookup) →
  paper-translator subagent:
    slice_pdf → translate_with_claude → build_dual
```

Load and execute `${CLAUDE_PLUGIN_ROOT}/skills/paper-translate/SKILL.md` with
`$ARGUMENTS`. Follow that skill's steps verbatim. Do not duplicate the
workflow here — the skill is the single source of truth.

If `${CLAUDE_PLUGIN_ROOT}` is unset (skill auto-resolution failed for some
reason), abort with the message:

```
Phyra paper-translate v0.9.0 requires ${CLAUDE_PLUGIN_ROOT} to locate skill scripts.
Reinstall the plugin: /plugin install phyra@phyra
```

> For analysis (Markdown + HTML viewer) and slide deck generation, see
> `/phyra:paper-read`.
