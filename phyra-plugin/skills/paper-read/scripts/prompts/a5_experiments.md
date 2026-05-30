Produce section §6 Experiments of the paper-read-notes Markdown.

# Inputs

## Paper text (experiments + appendix pages):

{pdf_text}

# Output

Emit ONLY this section:

## 6. Experiments

### 6.1 Datasets

(Table: Dataset | Task | Scale | Usage (train/val/test). One row per dataset
the paper actually uses. If a dataset is referenced but not used in this
paper's experiments, omit it.)

### 6.2 Evaluation Metrics

(Table: Metric | Description | Primary?. Mark the headline metric the
paper's main claim depends on as Primary = yes.)

### 6.3 Training and Inference Settings

(Hardware, batch size, optimizer, learning rate schedule, training steps,
inference settings. Cite the paper's appendix when relevant. If the paper
omits a setting, write "the paper does not specify".)

### 6.4 Main Results

(Table: Method | [Metric 1] | [Metric 2] | Notes. Bold the row corresponding
to this paper's method.)

### 6.5 Ablation Studies

(For each ablation: what was removed, what changed in the metric, and
whether the ablation answers the right question. Flag ablations that look
like sanity checks rather than diagnostic experiments.)

### 6.6 Phyra Experiment Assessment

Check each item below. Format: `- [covered|partial|missing] item — one
sentence of evidence`.

- Has at least one strong baseline (a current SoTA on the chosen task)
- Has cross-task / cross-dataset evaluation (not just one benchmark)
- Has ablations that diagnose the new components (not just sanity checks)
- Has a scaling study (size, length, or compute)
- Has an efficiency / wall-clock comparison
- Reports variance / standard deviation / multiple seeds where relevant
- Releases code / weights / data sufficient for reproducibility
