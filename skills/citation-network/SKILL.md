---
name: citation-network
description: "Use this skill when analyzing relationships between research papers, building citation graphs, mapping research lineage, or constructing logical development narratives between works."
---

# citation-network

**Purpose:** A citation network analysis framework, guiding the relationship-mapper agent on how to build relationship graphs between research works.

---

## Relationship Type Definitions (Must select from this vocabulary; do not invent new types)

- `builds-on`: The latter work explicitly uses the former as a foundation, extending or improving upon it
- `contradicts`: The latter's conclusions substantially contradict the former, and the authors are aware of this
- `parallel`: Both independently address similar problems, do not cite each other, but their methods are highly related
- `supersedes`: The latter outperforms the former on all major metrics, and the method is more general
- `applies`: The latter applies the former's method to a new domain or task
- `critiques`: The latter provides critical analysis of the former, but does not offer an alternative

---

## Relationship Table (Required Format)

```
| Research A | Research B | Relationship Type | Direction (A->B or B->A) | Basis (one sentence) |
```

---

## Timeline Requirements

- Relationship direction must be asserted only after confirming publication dates; papers published in the same year must be marked "temporal direction uncertain"

---

## Prohibited Inferences

- Do not infer the technical relationship between two papers from their abstracts alone; relationship judgments must be based on the methods sections
- Do not assume a relationship exists between studies just because the researchers are from the same institution

---

## Logical Narrative Construction Requirements

You must be able to describe in prose the development trajectory from the earliest predecessor work to the current research. The transition between each node must explain the driving cause (which limitation of the previous method led to the emergence of the next method).
