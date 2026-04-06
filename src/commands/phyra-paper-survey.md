---
description: "Search and survey related literature on a topic, generating relationship graph and survey notes"
argument-hint: "<query-or-paper-path> [--at]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "WebSearch", "WebFetch", "Agent", "SendMessage"]
---

# /phyra-paper-survey

> Search and survey related literature on a given topic, producing a force-directed relationship graph and structured survey notes.

Before doing anything else, load the `phyra-soul` skill. This is mandatory for every Phyra command and must not be skipped.

## Arguments

Parse `$ARGUMENTS` to extract:

- **Query**: the user's research query. Accepted forms:
  - A path to an existing paper file (PDF, MD, BIB)
  - A free-text description of a research topic
  - A task description or research objective
  - A research project name
- **Mode flag**: detect whether `--at` is present in the arguments
  - If `--at` is present, execute the AT (Agentic Turbo) workflow
  - If `--at` is absent, execute the NT (Normal Turbo) workflow

If `$ARGUMENTS` is empty or ambiguous, ask the user to clarify their query before proceeding.

## NT Workflow (Normal Turbo)

Execute the following steps sequentially:

### Step 1: Parse User Query

Analyze the user query to extract:

- Primary search keywords and phrases
- Research scope and domain boundaries
- Time range constraints (if any)
- Specific venues or databases to prioritize (if mentioned)

If the query is a paper file path, read the paper first and derive keywords from its title, abstract, and key contributions.

### Step 2: Literature Search

Dispatch `phyra-literature-searcher` as a single-line search agent.

- Provide the extracted keywords and scope
- The searcher must record a search log documenting: queries used, databases checked, number of results per query, and filtering decisions
- Collect all discovered papers with their metadata (title, authors, year, venue, abstract)

### Step 3: Relationship Mapping

Dispatch `phyra-relationship-mapper` with the collected papers.

- Analyze citation relationships, methodological lineage, and conceptual connections
- Build a logical narrative that explains how the papers relate to each other
- Identify clusters, key foundational works, and emerging directions
- Produce structured relationship data suitable for graph visualization

### Step 4: HTML Report

Dispatch `phyra-html-reporter` to create an HTML slide report.

- Include a force-directed relationship graph as the central visualization
- Each node represents a paper; edges represent relationships (citation, method inheritance, dataset sharing, etc.)
- Slides should cover: overview, methodology clusters, timeline, key findings, and the relationship graph
- Follow `phyra-html-slide-format` conventions

### Step 5: Markdown Survey Notes

Dispatch `phyra-md-reporter` to write survey notes.

- Follow the `paper-survey-notes` template from `phyra-md-report-format`
- Include: search log summary, paper list with annotations, relationship analysis, identified gaps, and suggested next reads
- Save as a Markdown file in the workspace

## AT Workflow (Agentic Turbo)

Execute the following steps, parallelizing where indicated:

### Step 1: Parse User Query

Same as NT Step 1. Analyze the user query to extract keywords, scope, and constraints. If the query is a paper file path, read and parse it first.

### Step 2: Parallel Literature Search (3 instances)

Launch three `phyra-literature-searcher` instances in parallel using `Agent` or `SendMessage`:

- **phyra-literature-searcher-A (Keyword Search)**: direct keyword-based search across academic databases. Focus on exact matches and closely related terms.
- **phyra-literature-searcher-B (Citation Trace)**: start from known seed papers (from the query or initial results) and trace citation chains forward and backward.
- **phyra-literature-searcher-C (Adjacent Field Expansion)**: broaden the search to adjacent research fields and interdisciplinary connections that may not appear in direct keyword searches.

Each instance must maintain its own search log. Wait for all three to complete before proceeding.

### Step 3: Relationship Mapping

Dispatch `phyra-relationship-mapper` with the combined results from all three search instances.

- Deduplicate papers found by multiple searchers
- Integrate findings into a unified relationship analysis
- Note which papers were discovered by which search strategy (useful for understanding coverage)
- Build the complete relationship graph with all connections

### Step 4: Parallel Report Generation

Launch both reporters in parallel:

- **phyra-html-reporter**: generate the HTML slide report with force-directed relationship graph (same requirements as NT Step 4)
- **phyra-md-reporter**: generate the Markdown survey notes (same requirements as NT Step 5)

Wait for both to complete. Present the output paths to the user.

## Output

Regardless of workflow mode, the final output includes:

1. An HTML slide report with an interactive force-directed relationship graph
2. A Markdown survey notes file following the `paper-survey-notes` template
3. A summary message to the user listing output file paths and key statistics (papers found, clusters identified, etc.)
