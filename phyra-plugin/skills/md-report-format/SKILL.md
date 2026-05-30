---
name: md-report-format
description: "Use this skill when generating MD format reports or notes. Provides structural principles for all report types and directs agents to load the corresponding template from templates/ before generating output."
---

# Phyra MD Report Format

This skill describes the structural principles for all MD reports. Specific report templates are stored as individual files in the `templates/` directory; the agent should read the corresponding template file before generating a report.

## Loading Logic

Before generating a report of a given type, read `templates/{type}.template.md`

## Available Templates

| Type Identifier | Template File | Description |
|-----------------|--------------|-------------|
| `paper-read-notes` | `templates/paper-read-notes.template.md` | Paper reading notes |
| `paper-survey-notes` | `templates/paper-survey-notes.template.md` | Paper survey notes |
| `paper-graph-notes` | `templates/paper-graph-notes.template.md` | Paper relationship notes |
| `paper-write-plan` | `templates/paper-write-plan.template.md` | Writing plan report |

## Usage

1. Determine the report type to generate
2. Read the corresponding template file: `templates/{type}.template.md`
3. Fill in content following the template structure
4. Ensure compliance with the common constraints below

## Common Constraints for All MD Reports

- The first line must contain the report type identifier and generation date (format per each template)
- All numbers must have a source (paper page number / experiment result / search record)
- Reports must not end with generic summary boilerplate
- Typography constraints follow the `typography` skill (no `---` dividers, `——` symbols, etc.)
