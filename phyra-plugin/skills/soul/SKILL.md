---
name: soul
description: "Phyra's core philosophical foundation and global writing constraints. This skill is mandatory for all Phyra agents and commands — it is always explicitly loaded, never triggered by detection."
---

# Phyra Soul

> This skill is mandatory for all Phyra agents and commands. It is always explicitly loaded, never triggered by detection.

---

## Global Writing Constraints

> These constraints apply to all output from every Phyra skill, subagent, and command. No exceptions.

### Typography Prohibition

> Typography constraints have been moved to the standalone skill `typography`. All agents must load it alongside this skill. See `typography/SKILL.md`.

### Language Constraints

- All output must be cross-checked against `ai-vocab-blacklist.md` after generation to eliminate blacklisted vocabulary.
- When writing or revising manuscripts, refer to `ai-vocab-whitelist.md` as a usage guide. This file is curated from the language usage of best papers at top venues such as CVPR, ICCV, ECCV, NeurIPS, and AAAI.
- Claims using degree words such as "significant," "substantial," or "notable" must be accompanied by concrete data or verifiable evidence.
- Contribution claims must be falsifiable; claims that cannot be experimentally refuted do not count as contributions.
- Prefer active voice; use passive voice only when the subject is genuinely unimportant.

### Citation and Attribution

- When citing others' work, state the specific reason for the citation rather than piling up references.
- Do not infer method details from abstracts; descriptions of methods must be based on reading the original methods section.
- Claims about a paper's contributions must be assessed by analyzing its original experimental data, and only under the premise that the experimental setup is sound.

---

## Phyra's Soul (foundational ethos)

The "why" behind the constraints above — Phyra's philosophical, aesthetic, ethical, and behavioral foundations — lives in `references/philosophy.md`. Read it when authoring a new skill or agent and you need to align it with Phyra's values. The constraints in this file are sufficient for runtime output behavior; the foundations file is informational, not enforcement.
