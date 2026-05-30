---
name: experiment-design
description: "Use this skill when designing experiments, selecting baselines, planning ablation studies, choosing evaluation metrics, or checking experiment sufficiency for academic papers."
---

# Experiment Design Standards

> Guides the experiment-planner agent on how to design sufficient and convincing experiments.

## Baseline Selection Criteria (Must cover at least the following three categories)

### 1. Contemporaneous SOTA

The strongest competing method from the same period. Must be a genuine comparison; do not select a SOTA weaker than your own method.

- Selection principle: Must be the currently recognized best result on the same task
- Verification method: Check top venue papers and leaderboards from the past 1-2 years
- Note: Do not deliberately select a weaker "SOTA" to make your method look better

### 2. Classic Baseline

An established benchmark method in the field, typically 3+ years old and widely cited.

- Selection principle: The method must be widely recognized and cited in the field
- Significance: Demonstrates the degree of improvement over classic technical approaches
- Note: If the classic method has known improved versions, those should also be considered

### 3. Ablated Version

A simplified version with the paper's core design removed, used to verify the necessity of design choices.

- Selection principle: A corresponding ablation baseline should be designed for each core contribution of the paper
- Significance: Proves that each design decision is necessary
- Note: Ablation baselines should change only one variable at a time

## Ablation Study Design Standards

### Hypothesis-Driven

Each ablation experiment must have a clear hypothesis: after removing X, metric Y is expected to decrease, because Z.

- Write down expected results before the experiment
- If actual results do not match expectations, the reasons must be analyzed
- Hypotheses should be based on logical reasoning from the method design

### Ablation Granularity

Ablation must not only be "remove a module"; if the entire module is a contribution, the ablation granularity must be finer.

- For complex modules, design multi-level ablations
- For example: not only remove the entire attention module, but also test different attention variants
- Granularity should be fine enough to distinguish the impact of each design choice

### Contribution Quantification

Ablation results must be able to answer "how much does each design choice contribute?"

- Report the performance difference for each ablation experiment (absolute and relative values)
- Ensure the sum of contributions from all ablation experiments can explain the overall performance improvement
- If interaction effects exist, additional experiments are needed to verify

## Evaluation Metric Selection Principles

### Domain-Standard Metrics

Domain-standard metrics must be used.

- Explain in the paper why these metrics were chosen
- If proposing new metrics, standard metrics must also be reported as a reference
- Refer to common metric combinations from top venue papers in the field

### Primary Metric Specification

When using multiple metrics, you must specify which is the primary metric and explain why.

- The primary metric should most directly reflect the task objective
- Center the results discussion around the primary metric
- Auxiliary metrics provide multi-perspective performance evaluation

### No Cherry-Picking

Do not report only the subset of metrics favorable to your method.

- All pre-defined metrics must be fully reported
- Even if your method is not the best on certain metrics, present results honestly
- Honestly discuss the limitations of your method in the analysis

## Statistical Significance Requirements

See the domain-specific statistical conventions section in `ai-review-checklist.md`.

- Choose an appropriate statistical test method according to domain conventions
- Report p-value or confidence interval
- Mark statistical significance in results tables

## Experiment Sufficiency Self-Check Checklist

Before submitting the paper, use the following checklist to confirm the completeness of the experimental design:

- [ ] Is there a held-out test set (rather than using the validation set as the test set)?
- [ ] Were baseline results run by you or directly cited? If cited, is the environment consistent?
- [ ] Were the best hyperparameters selected on the test set or the validation set?
- [ ] What is the variance of the results? Were multiple experiments conducted?
