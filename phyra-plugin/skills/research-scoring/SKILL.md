---
name: research-scoring
description: "Use this skill when generating research scoring reports for paper reviews. Provides the 5-dimension scoring system, weighted averages, grade mapping, and scoring constraints for /paper-review."
---

# research-scoring

**Purpose:** A research scoring framework, specifically for scoring report output in `/paper-review`.

**Relation to peer-review-criteria:** This skill is a quantitative complement to `peer-review-criteria`. When both are loaded (e.g. in `peer-reviewer-chair`), `peer-review-criteria` is the primary source for review judgment and dimension semantics. `research-scoring` adds the numeric scoring rubric, weighting method, grade mapping, and the predecessor-tracking requirement on top of those dimensions. If the two skills appear to disagree, follow `peer-review-criteria`.

---

## Technical Development Path Tracking (Required)

- Identify the direct predecessor works that the paper builds on. A reasonable depth is typically 2–4 works, depending on how mature the subfield is. Fewer than 2 is acceptable only when the paper genuinely opens a new line of work; more than 4 is acceptable when the lineage is dense.
- Explain the specific advances of the current paper relative to predecessor works (not vague statements like "improved")
- Identify the problems left by predecessor works that the current paper attempts to solve
- Arrange predecessor works chronologically, not by importance

---

## Scoring Dimensions (Five dimensions, each scored 1-10)

| Dimension | Description |
|---|---|
| Problem Validity | Whether the problem is worth solving; whether the definition is clear |
| Method Soundness | Whether the method logic is internally consistent; whether assumptions hold |
| Experimental Adequacy | Whether experiments support the claims; whether baselines are fair |
| Novelty | Essential differences from existing work |
| Reproducibility | Whether details are sufficient; whether others can reproduce the work |

---

## Weighted Average to Grade Mapping

| Grade | Score Range | Meaning |
|---|---|---|
| Strong Accept | 8.5 - 10.0 | Clearly superior to existing work on core dimensions |
| Accept | 7.0 - 8.4 | Clear contributions, minor issues, acceptable |
| Weak Accept | 5.5 - 6.9 | Valuable but has major issues that need to be fixed |
| Borderline | 4.5 - 5.4 | Substantive disagreement between positive and negative reviewers |
| Weak Reject | 3.0 - 4.4 | Current version is insufficient; can be resubmitted after revision |
| Reject | 1.0 - 2.9 | Contains a fatal flaw that cannot be fixed through revision |

---

## Weighting Method

Dimension weights:

- Problem Validity x 0.15
- Method Soundness x 0.30
- Experimental Adequacy x 0.30
- Novelty x 0.15
- Reproducibility x 0.10

Weighted average = Problem Validity x 0.15 + Method Soundness x 0.30 + Experimental Adequacy x 0.30 + Novelty x 0.15 + Reproducibility x 0.10

---

## Constraints

- Each dimension's score must be accompanied by a specific rationale; bare scores are not allowed
- Scoring must not be based solely on whether result numbers are good or bad; a paper with good results but fundamental method flaws should not receive a high score
- When the weighted average does not match the assigned grade, the report must explain the reason (e.g., a fatal flaw in a single dimension dragging down the overall score)
