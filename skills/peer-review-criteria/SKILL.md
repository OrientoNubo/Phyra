---
name: peer-review-criteria
description: "Use this skill when conducting peer review of academic papers, constructing review judgments, classifying defects, or evaluating research along the 5 review dimensions (problem validity, method soundness, experimental adequacy, novelty, reproducibility)."
---

# Peer Review Criteria Framework

> Guides the review agent on how to construct review judgments.

## Review Dimensions (In Priority Order)

### 1. Problem Validity

- Is this problem truly worth solving?
- Is the author's definition of the problem clear and well-bounded?
- Is the claim of problem importance supported?

### 2. Method Soundness

- Does the method truly solve the problem defined in the Introduction?
- Do the method's assumptions hold in the intended application scenarios?
- Are the key design choices in the method supported by theory or experiments?

### 3. Experimental Adequacy

- Do the experiments support the claims made in the Method section?
- Is the baseline selection fair and reasonable?
- Are results statistically significant? Do ablation studies answer the right questions?

### 4. Novelty

- What is the essential difference from existing work?
- Is the difference at the technical level, or only at the application scenario level?

### 5. Reproducibility

- Are sufficient details provided for reproduction?
- Is the hyperparameter selection transparent?

## Defect Classification System

### Fatal Flaw

If this issue exists, the paper's core claims do not hold. Cannot be fixed through revision.

### Major Concern

The paper's credibility is seriously affected, but in principle can be fixed through revision.

### Minor Issue

Does not affect core claims, but impacts the paper's clarity or completeness.

### Suggestion

The authors may choose to accept or reject; does not form the basis of the review judgment.

## Prohibited Review Behaviors

- Do not increase the score because the method is complex
- Do not overlook method flaws because the result numbers look good
- Do not evaluate experimental adequacy without having read the experiment section

## Domain Convention Supplements

Different domains (CV / NLP / Multimodal / DL / Robotics, etc.) have different conventions for baseline selection, dataset standards, and evaluation metrics. Reviews must be evaluated against domain-specific standards, not solely based on general principles. See `ai-review-checklist.md`.
