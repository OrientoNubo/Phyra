---
name: literature-search
description: "Use this skill when searching for related research, building literature collections, or conducting systematic literature surveys. Provides search order, three-line strategy (AT mode), keyword construction rules, and inclusion criteria."
---

# Literature Search Skill

**Purpose:** A search strategy knowledge base, guiding the literature-searcher agent on how to systematically find related research.

---

## Search Order (Standard Priority)

1. **arXiv** (preprints, broadest coverage, fastest)
2. **Semantic Scholar** (semantic search, most complete citation relationships)
3. **Google Scholar** (broadest coverage, but most noise)
4. **Domain-specific databases** (ACL Anthology / IEEE Xplore / ACM DL / PubMed, choose based on domain)
5. **GitHub** (find engineering implementations and research without papers)
6. **Technical blogs, industry reports** (find research results without academic publications)

---

## Three-Line Search Strategy (Parallel in AT Mode)

- **Thread A (Forward keyword search):** Start from core terms, construct keyword combinations, and search directly
- **Thread B (Citation backtracking):** After finding 1-2 core related papers, look up forward citations and backward citations
- **Thread C (Adjacent field expansion):** Identify terminology mappings to neighboring fields, search for the same class of problems across different communities

---

## Keyword Construction Rules

- Always try terms in different languages simultaneously (the same concept may have different names in different communities)
- When search results return fewer than 5 papers, try broader/superordinate concepts
- When search results return more than 50 papers, add constraints (time range, method type, etc.)

---

## Inclusion Criteria for Non-Paper Research

- **GitHub repo:** Stars > 100, or cited by well-known papers
- **Technical reports:** From an identifiable research institution or company
- **Blog posts:** Author has a verifiable research background and provides specific technical details

---

## Relevance Judgment

Each selected work must be able to answer:

- What problem is this research solving?
- What is its intersection with the current search objective? (Must be stated in one specific sentence; vague generalizations are not allowed)

---

## Search Metadata That Must Be Recorded

```
- Search time:
- Database used:
- Search terms:
- Total results:
- Number included:
- Inclusion rationale (one sentence per paper):
```
