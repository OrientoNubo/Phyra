# AI Review Checklist -- Domain-Specific Review Standards

> **Purpose:** Reference for `peer-review-criteria`, `experiment-design`, and similar skills.
> Reviews must be evaluated against domain-specific standards, not generic principles alone.

---

## 1. Computer Vision (CV)

### 1.1 Baselines

| Task | Expected Baselines |
|------|--------------------|
| Image Classification | ResNet-50/101, ViT-B/L, DeiT, Swin Transformer, ConvNeXt |
| Object Detection | Faster R-CNN, DETR, DINO, Co-DETR, YOLOv8+ |
| Semantic Segmentation | DeepLabv3+, SegFormer, Mask2Former |
| Instance / Panoptic Seg | Mask R-CNN, Mask2Former, SAM (zero-shot scenarios) |
| Image Generation | StyleGAN2/3, Stable Diffusion, DiT |
| Video Understanding | VideoMAE, TimeSformer, InternVideo |

- If a paper claims state-of-the-art, it must compare against the **strongest concurrent methods**, not only weaker classic ones.
- When using a pre-trained backbone, the pre-training dataset and scale must be specified.

### 1.2 Datasets

| Task | Standard Datasets |
|------|-------------------|
| Classification | ImageNet-1K, ImageNet-21K (pre-train), CIFAR-10/100 |
| Detection | COCO val2017, LVIS, Objects365, VOC 2007/2012 |
| Segmentation | ADE20K, Cityscapes, COCO-Stuff, PASCAL Context |
| Generation | LSUN, FFHQ, ImageNet (FID evaluation) |
| Self-supervised | ImageNet-1K (linear probe / fine-tune) |

- Dataset splits must use official splits; custom splits require justification and a description of the splitting method.
- Key information such as training set size and image resolution should be reported.

### 1.3 Metrics

| Task | Primary Metrics | Secondary Metrics |
|------|----------------|-------------------|
| Classification | Top-1 / Top-5 Accuracy | Throughput (img/s), FLOPs |
| Detection | mAP@[.5:.95], AP50, AP75 | AP_S / AP_M / AP_L |
| Segmentation | mIoU | aAcc, mAcc, Boundary IoU |
| Generation | FID, IS | LPIPS, Precision/Recall |
| Video | Top-1 Acc, mAP | GFLOPs per clip |

### 1.4 Statistical Conventions

- Large-scale datasets (ImageNet) generally **do not require** confidence intervals, but hyperparameter settings and training details should be reported.
- Small datasets or few-shot scenarios: report **mean +/- standard deviation over multiple runs** (at least 3 runs).
- Ablation experiments should fix random seeds to ensure reproducibility.

### 1.5 Common Pitfalls

- **Unfair resolution comparison:** Different methods use different input sizes without disclosure or correction.
- **Test-Time Augmentation (TTA):** Using TTA to boost numbers without noting it in the table.
- **Pre-training data leakage:** Using pre-trained models whose data overlaps with the test set (e.g., ImageNet-21K containing some downstream task classes).
- **Unfair FLOPs comparison:** Inconsistent FLOPs calculation methods (with/without backbone, with/without post-processing).
- **Augmentation differences:** Compared methods use different augmentation strategies without controlling for this variable.

---

## 2. Natural Language Processing (NLP)

### 2.1 Baselines

| Task Type | Expected Baselines |
|-----------|--------------------|
| General Understanding | BERT-base/large, RoBERTa, DeBERTa-v3 |
| Generation | GPT-2/3/4, T5, LLaMA 2/3, Mistral, Qwen |
| Translation | mBART, NLLB, GPT-4 (zero-shot) |
| Information Extraction | SpanBERT, UIE, ChatGPT (zero-shot) |
| Code | CodeLLaMA, DeepSeek-Coder, StarCoder |

- LLM papers must compare models of the **same parameter scale** (7B vs 7B; do not cherry-pick weaker models).
- If instruction tuning or RLHF is used, the training stage must be clearly labeled.

### 2.2 Datasets

| Task | Standard Benchmarks |
|------|---------------------|
| General Understanding | GLUE, SuperGLUE, MMLU |
| Question Answering | SQuAD 1.1/2.0, Natural Questions, TriviaQA |
| Summarization | CNN/DailyMail, XSum, SAMSum |
| Translation | WMT (specify year), FLORES |
| Code | HumanEval, MBPP, DS-1000 |
| Long-context | SCROLLS, LongBench, Needle-in-a-Haystack |

- Dataset versions must be pinned (e.g., SQuAD 1.1 vs 2.0 differ substantially).
- Ensure consistency in how few-shot prompts are selected.

### 2.3 Metrics

| Task | Primary Metrics | Notes |
|------|----------------|-------|
| Classification / NLI | Accuracy, F1 (macro/micro) | Imbalanced data requires macro F1 |
| Generation / Summarization | ROUGE-1/2/L, BERTScore | ROUGE must specify stemming settings |
| Translation | BLEU (sacreBLEU), COMET, chrF | Must use sacreBLEU, not custom BLEU |
| Question Answering | EM, F1 | Distinguish token-level vs span-level |
| Language Modeling | Perplexity, bits-per-byte | Must specify tokenizer and context length |

### 2.4 Statistical Conventions

- **Significance tests are required:** At minimum, use a paired bootstrap test or McNemar's test.
- Report **95% confidence intervals** (especially on small datasets).
- Multiple random seed experiments: at least 3-5 runs, reporting mean +/- standard deviation.
- When using LLMs for zero/few-shot evaluation, report prompt sensitivity (variance across different prompts).

### 2.5 Common Pitfalls

- **Data contamination:** LLM training corpora may contain the test set; this must be checked and disclosed.
- **Unfair tokenizer comparison:** Different tokenizers produce different sequence lengths, directly affecting perplexity and speed.
- **Prompt engineering bias:** Reporting only the best prompt's results rather than average performance.
- **Inconsistent evaluation scripts:** Different papers use different versions of evaluation scripts (e.g., BLEU calculation methods vary widely).
- **Fine-tuning vs zero-shot confusion:** Comparing fine-tuned results against another method's zero-shot results without labeling.

---

## 3. Multimodal Learning

### 3.1 Baselines

| Task Type | Expected Baselines |
|-----------|--------------------|
| Image-Text Alignment | CLIP, SigLIP, EVA-CLIP |
| Image-Text Generation | BLIP-2, InstructBLIP, LLaVA-1.5/NeXT |
| Multimodal Dialogue | GPT-4V/o, Gemini, LLaVA, Qwen-VL |
| Video Understanding | Flamingo, VideoLLaMA, VideoChat |
| Text-to-Image | DALL-E 3, Stable Diffusion XL, Midjourney (human evaluation) |

- Cross-modal methods must specify the pre-training source for each modality encoder and whether it is frozen.
- Multimodal LLMs must compare against methods with the same LLM backbone scale.

### 3.2 Datasets

| Task | Standard Benchmarks |
|------|---------------------|
| VQA | VQAv2, OK-VQA, GQA, TextVQA, ChartQA |
| Image Captioning | COCO Captions, NoCaps, Flickr30k |
| Retrieval | COCO Retrieval, Flickr30k Retrieval |
| Comprehensive Evaluation | MMBench, MME, SEED-Bench, MM-Vet |
| Video QA | MSRVTT-QA, ActivityNet-QA, EgoSchema |

### 3.3 Metrics

| Task | Primary Metrics |
|------|----------------|
| VQA | VQA Accuracy (official evaluation server) |
| Captioning | CIDEr, SPICE, CLIPScore |
| Retrieval | Recall@1/5/10 |
| Comprehensive | Each benchmark's own scoring (e.g., MME score) |
| Human Evaluation | Elo rating, win rate (must report annotator agreement) |

### 3.4 Statistical Conventions

- When human evaluation is involved, report **inter-annotator agreement** (Cohen's kappa or Fleiss' kappa).
- VQA and similar automatic metrics generally do not require confidence intervals, but zero-shot settings should report multi-prompt variance.
- Generation tasks should combine automatic metrics with human evaluation.

### 3.5 Common Pitfalls

- **Unequal training data scale:** Different methods use vastly different amounts of image-text pairs (e.g., 400M vs 1B).
- **Inconsistent evaluation protocol:** Different VQA evaluation modes (open-ended vs multiple-choice) produce incomparable results.
- **Vision encoder differences:** Using different resolutions or different pre-trained vision encoders without controlling for this.
- **Cherry-picked examples:** Qualitative examples show only successes, never failures.

---

## 4. Deep Learning (General / Architecture)

### 4.1 Baselines

| Direction | Expected Baselines |
|-----------|--------------------|
| New Operator / Layer | The corresponding standard component (e.g., new attention vs vanilla attention, linear attention) |
| New Architecture | Same-scale Transformer, CNN, MLP-Mixer, Mamba/SSM |
| Optimization Methods | AdamW, SGD + momentum, Lion, Schedule-Free |
| Regularization Methods | Dropout, Weight Decay, Label Smoothing, Mixup |
| Efficient Training | Standard training, LoRA, QLoRA, knowledge distillation |

- Architecture papers must validate generality across **multiple downstream tasks**, not just a single task.
- New components must provide a **drop-in replacement** comparison against the standard component.

### 4.2 Datasets

- Cover at least two domains (e.g., CV + NLP) to demonstrate generality.
- Include at least one large-scale task (ImageNet / C4) and one small-scale task.
- Scaling law papers must cover a sufficient number of model scale points (at least 4-5 orders of magnitude).

### 4.3 Metrics

| Type | Must Report |
|------|-------------|
| Performance | Standard metrics for each task |
| Efficiency | **FLOPs** (forward + backward), **parameter count**, **memory usage** |
| Speed | Wall-clock time (training), Throughput (inference) |
| Scaling | Performance vs parameter count / FLOPs curves |

- FLOPs calculation method must be specified (fvcore, DeepSpeed profiler, manual derivation, etc.).
- Parameter count must distinguish between total params and trainable params.

### 4.4 Statistical Conventions

- Ablation experiments with different random seeds: at least 3 runs.
- Scaling law fitting must report R-squared and extrapolation reliability.
- Training curves (loss curves) should be included to verify convergence.

### 4.5 Common Pitfalls

- **Inconsistent FLOPs:** Different methods use different FLOPs accounting (whether embedding, head, and normalization are included).
- **Reporting only the best hyperparameters:** Failing to show hyperparameter sensitivity analysis.
- **Ignoring actual speed:** Low FLOPs but slower real-world inference due to poor hardware utilization.
- **Over-ablation:** Removing one component at a time while ignoring interactions between components.
- **Hidden training cost:** Not reporting the GPU type, quantity, and training time actually used.

---

## 5. Robotics / Embodied AI

### 5.1 Baselines

| Task Type | Expected Baselines |
|-----------|--------------------|
| Manipulation | BC (Behavior Cloning), RT-1/2, Diffusion Policy, ACT |
| Navigation | PointNav baselines, VLN-CE, Habitat baselines |
| Locomotion | PPO/SAC + MLP, AMP, model-based RL |
| Planning | SayCan, Code-as-Policies, VoxPoser |
| Foundation Models | RT-2, Octo, OpenVLA |

- Methods must be compared against approaches with **equivalent sensor inputs** (RGB-only vs RGB-D vs point cloud).
- Methods using foundation models must also be compared against task-specific methods.

### 5.2 Datasets / Benchmarks

| Environment | Standard Benchmarks |
|-------------|---------------------|
| Simulation - Manipulation | ManiSkill2, RLBench, MetaWorld, LIBERO |
| Simulation - Navigation | Habitat, iGibson, AI2-THOR |
| Simulation - Locomotion | IsaacGym, MuJoCo (locomotion suites) |
| Real World | DROID, Open X-Embodiment, Bridge V2 |
| Language Grounding | ALFRED, TEACh, Embodied QA |

- **Sim-to-Real:** If a method claims real-world transferability, real-world experimental results are mandatory.
- Simulation environments must specify the physics engine version and rendering settings.

### 5.3 Metrics

| Task | Primary Metrics | Supplementary Metrics |
|------|----------------|----------------------|
| Manipulation | Success Rate (%) | Completion Rate, Path Efficiency |
| Navigation | SPL (Success weighted by Path Length) | SR, Navigation Error |
| Locomotion | Reward, Velocity Tracking Error | Energy Consumption |
| Generalization | Success rate on novel objects / scenes | Sim-to-Real Gap |
| Safety | Collision Rate, Constraint Violations | -- |

### 5.4 Statistical Conventions

- At least **50-100 episodes** per task configuration (more in simulation).
- Report **mean +/- standard deviation** or **95% CI**; especially critical for real-world experiments.
- Real-world experiments must clearly report the number of trials, environmental conditions, and failure case analysis.
- At least 3 random seeds (5 recommended in simulation).

### 5.5 Common Pitfalls

- **Ignoring sim-to-real gap:** Validating only in simulation while claiming real-world applicability.
- **Over-simplified environments:** Using overly simple simulation (no disturbances, fixed lighting, deterministic dynamics).
- **Vague success criteria:** Not clearly defining what counts as "success" (e.g., whether a grasp must be held for N seconds).
- **Lack of generalization experiments:** Evaluating only on objects/scenes seen during training.
- **Missing hardware details:** Not reporting robot model, sensor specifications, control frequency, etc.
- **Insufficient reproducibility:** Not providing complete simulation configuration files or video evidence for real-world experiments.

---

## General Review Reminders

The following requirements apply to all domains:

1. **Baseline recency:** Baselines must include SOTA methods from the past 1-2 years. Comparing only against methods older than 3 years is insufficient.
2. **Fairness:** All compared methods must be evaluated under the same conditions (same data, comparable computational budget, same evaluation protocol).
3. **Open source and reproducibility:** Prefer citing baseline results with open-source code. If using self-reproduced numbers, this must be stated.
4. **Computational budget:** Total computational cost must be reported (GPU hours or carbon emission estimates), especially for large-scale experiments.
5. **Limitations:** Papers must honestly discuss the method's limitations and failure cases; showing only successes is unacceptable.

---

> **Maintenance note:** This checklist should be updated periodically as the field evolves. When new standard baselines or benchmarks appear (e.g., next-generation foundation models), maintainers should add them to the corresponding sections.
