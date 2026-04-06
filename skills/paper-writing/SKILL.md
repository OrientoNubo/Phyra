---
name: paper-writing
description: "Use this skill when writing, revising, or planning academic papers. Provides story line construction principles, gap analysis writing norms, contribution claim rules, abstract structure (5-paragraph), and prohibited writing behaviors."
---

# Paper Writing

> This skill defines academic writing standards, guiding paper-writing agents on how to construct story lines and write each section.

---

## Story Line Construction Principles

- The story line must grow from the logic of the method; do not work in reverse (creating a story first, then finding methods to support it)
- A good story line can be explained in three sentences: what problem -> why existing methods are insufficient -> how your method is fundamentally different
- The persuasiveness of the story line comes from the precision of the gap; the more specific the gap, the more powerful the story

### Three-Sentence Test

Before beginning to write any paper, complete the following test:

1. **Problem**: What problem are we solving? (one sentence)
2. **Insufficiency**: Why are existing methods insufficient? (one sentence, must be specific)
3. **Difference**: How is our method fundamentally different? (one sentence, not a pile of details)

If the three sentences cannot be naturally linked together, the story line is not yet mature, and writing should not begin.

---

## Gap Analysis Writing Standards

- The gap must cite specific prior work and its specific limitations; do not use unsourced generalizations like "existing methods cannot..."
- The gap description must help the reader understand: why this problem was not solved before you

### Acceptable Gap Statement Example

> While [Author et al., 2024] achieved strong performance on X, their method assumes Y, which does not hold when Z.

### Unacceptable Gap Statement Example

> Existing methods cannot handle complex scenarios effectively.

Reason for rejection: no specific citation, no specific limitation described, "complex scenarios" is vague.

---

## Contribution Claim Standards

- Contribution points: 3-4, no more, no fewer
- Each contribution must be experimentally verifiable or falsifiable
- Do not begin with "We propose..."; contribution claims should describe the nature of the contribution, not the action
- "First to..." claims are prohibited unless supported by thorough literature evidence

### Acceptable Contribution Claim Format

> A loss function that decouples X from Y, enabling Z without requiring W.

### Unacceptable Contribution Claim Format

> We propose a novel framework for X.

Reason for rejection: "We propose" describes an action rather than the nature of the contribution; "novel" is a self-describing adjective; lacks falsifiability.

---

## Abstract Structure (Five-Part)

The abstract must contain the following five parts, in order:

1. **Problem statement** (1-2 sentences): Define the problem to be solved and its importance
2. **Specific limitations of existing methods** (1-2 sentences): Point out specific shortcomings of prior work
3. **Core idea of this paper's method** (1-2 sentences): Describe the core idea of the method, not a pile of method details
4. **Main experimental results** (1-2 sentences): Must include numbers; report key metric improvements
5. **Broader significance** (1 sentence): Restrained indication of potential impact; do not exaggerate

The sentence limits for each part are hard limits. Recommended total abstract length: 150-250 words.

---

## Prohibited Writing Behaviors

The following behaviors are prohibited in all paper writing outputs, with no exceptions:

- Do not begin with "In recent years, X has attracted increasing attention..."
- Do not use self-describing adjectives such as "comprehensive" / "extensive" / "thorough" in contribution points
- Do not claim an advantage of the method without corresponding experimental support

### Additional Prohibited Patterns

- Do not use "To the best of our knowledge" as a basis for novelty
- Do not use more than one paragraph of background in the Introduction
- Do not merely list works in Related Work without comparative analysis

---

## Domain Writing Conventions

See `ai-writing-conventions.md`.

That file contains specific writing conventions for AI / CV / NLP and other domains, including:

- Common section structures and naming
- Standard formats for reporting experiments
- Figure and table description standards
- Domain-specific terminology conventions

When writing papers, follow both the general standards in this skill and the specific guidelines in the domain writing conventions file.

---

## Relationship to Other Skills

- **soul**: Global writing constraints (formatting prohibitions, language constraints) always apply
- **peer-review-criteria**: When writing, anticipate the points reviewers will check
- **experiment-design**: Reporting of experimental results must comply with the experiment design skill's standards
- **citation-network**: Citation selection and gap analysis should reference citation network analysis results
