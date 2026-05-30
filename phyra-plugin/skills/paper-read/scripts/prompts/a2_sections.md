Produce section §3 Section Walkthrough of the paper-read-notes Markdown.

For each subsection (3.1 Title and Abstract, 3.2 Introduction, 3.3 Related
Work / Preliminaries, 3.4 Method overview narrative, 3.5 Experiments overview
narrative, 3.6 Conclusion / Limitations / Future Work):
  - Approximate word count of the section in the paper, formatted EXACTLY
    as `(N words)` where N is a single integer. Do NOT add breakdowns,
    semicolons, or co-section references. Do NOT write `(N words; §X 約 Y)`.
    If a Walkthrough subsection conceptually spans more than one numbered
    section in the paper, sum the word counts and emit a single `(N words)`.
  - Story logic in 250–400 words: what is claimed, what is established, what
    sets up the next section.

# Inputs

## PARSED_PAPER section list (for word counts and section anchors):

{parsed_sections}

## Paper text (full, may be truncated by length budget):

{pdf_text}

# Output

Emit ONLY this section:

## 3. Section Walkthrough

### 3.1 Title and Abstract

(N words)

[story logic, 250–400 words]

### 3.2 Introduction

(N words)

[story logic, 250–400 words]

### 3.3 Related Work / Preliminaries

(N words)

[story logic, 250–400 words]

### 3.4 Method (overview narrative)

(N words)

[narrative, 250–400 words. Does NOT include per-module detail — that goes in
§5 of the merged document, written by a different call.]

### 3.5 Experiments (overview narrative)

(N words)

[narrative, 250–400 words. Does NOT include detailed table-by-table analysis
— that goes in §6.]

### 3.6 Conclusion / Limitations / Future Work

(N words)

[narrative, 250–400 words.]
