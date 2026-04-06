---
description: "Build a relationship graph from a list of papers, analyzing connections and generating visual graph report"
argument-hint: "<paper-list-or-bib-file> [--at]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob", "Agent", "SendMessage"]
---

# /phyra-paper-graph

> Build a relationship graph from a given list of papers, analyzing their connections and producing a visual graph report with structured notes.

Before doing anything else, load the `phyra-soul` skill. This is mandatory for every Phyra command and must not be skipped.

## Arguments

Parse `$ARGUMENTS` to extract:

- **Paper list**: the set of papers to analyze. Accepted forms:
  - A list of paper titles (one per line, comma-separated, or in a text file)
  - A BibTeX file (.bib) containing paper entries
  - A mixed-format file combining titles, DOIs, and/or BibTeX entries
  - A path to a directory containing paper files
- **Mode flag**: detect whether `--at` is present in the arguments
  - If `--at` is present, execute the AT (Agentic Turbo) workflow
  - If `--at` is absent, execute the NT (Normal Turbo) workflow

If `$ARGUMENTS` is empty or the paper list cannot be parsed, ask the user to provide a valid paper list or file path.

## NT Workflow (Normal Turbo)

Execute the following steps sequentially:

### Step 1: Parse Paper List

Read and parse the input to produce a normalized list of papers:

- Extract titles, authors, years, venues, and any available identifiers (DOI, arXiv ID)
- For BibTeX files, parse all entries and extract metadata
- For title-only lists, record titles as-is for downstream analysis
- Report the total number of papers identified

### Step 2: Sequential Content Analysis

For each paper in the list, sequentially dispatch `phyra-content-analyst`:

- Provide the paper's metadata and any available full text
- The analyst should extract: core contributions, methodology, key results, limitations, and connections to other works
- Collect all analysis results into a unified structure
- Process papers one at a time to maintain context coherence

### Step 3: Relationship Mapping

Dispatch `phyra-relationship-mapper` with all collected analyses.

- Integrate findings from every paper's content analysis
- Build a complete relationship graph identifying:
  - Citation links, methodological lineage, dataset/benchmark overlaps, conceptual clusters
- Identify central/influential papers and peripheral works; detect temporal evolution patterns

### Step 4: HTML Report

Dispatch `phyra-html-reporter` to create an HTML slide report.

- Feature a force-directed relationship graph as the primary visualization
- Nodes represent papers (size indicates centrality); edges are color-coded by relationship type
- Slides should cover: paper set overview, cluster analysis, evolution timeline, key relationships, and the interactive graph
- Follow `phyra-html-slide-format` conventions

### Step 5: Markdown Graph Notes

Dispatch `phyra-md-reporter` to write graph notes.

- Follow the `paper-graph-notes` template from `phyra-md-report-format`
- Include: paper inventory, per-paper summaries, relationship matrix, cluster descriptions, and trajectory insights

## AT Workflow (Agentic Turbo)

Execute the following steps, parallelizing where indicated:

### Step 1: Parse Paper List and Split into Batches

Parse the input same as NT Step 1. Then split the normalized paper list into batches:

- Target 3 to 5 papers per batch
- Group papers by proximity (similar topics or venues) when possible for richer local context

### Step 2: Parallel Content Analysis

Launch multiple `phyra-content-analyst` instances in parallel using `Agent` or `SendMessage`, one per batch:

- **phyra-content-analyst-1 (Batch A)**: analyze the first batch of papers
- **phyra-content-analyst-2 (Batch B)**: analyze the second batch of papers
- **phyra-content-analyst-N (Batch ...)**: continue for all remaining batches

Each instance performs the same analysis as NT Step 2, but only for its assigned batch. Wait for all batch analysts to complete before proceeding.

### Step 3: Relationship Mapping

Dispatch `phyra-relationship-mapper` after all parallel analysts have finished.

- Integrate analysis results from every batch
- Cross-reference findings between batches to discover inter-batch relationships
- Build the complete unified relationship graph (same depth as NT Step 3)
- Ensure no connections are missed due to batch boundaries

### Step 4: Parallel Report Generation

Launch both reporters in parallel:

- **phyra-html-reporter**: generate the HTML slide report with force-directed relationship graph (same requirements as NT Step 4)
- **phyra-md-reporter**: generate the Markdown graph notes (same requirements as NT Step 5)

Wait for both to complete. Present the output paths to the user.

## Output

Regardless of workflow mode, the final output includes:

1. An HTML slide report with an interactive force-directed relationship graph
2. A Markdown graph notes file following the `paper-graph-notes` template
3. A summary message to the user listing output file paths and key statistics (papers analyzed, relationships found, clusters identified, etc.)
