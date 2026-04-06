<!-- Step 1: Story Architect | NT mode | generated: 2026-04-05 -->

# Storyline: Vision-Language Models for Zero-Shot Object Detection

## Three-Sentence Storyline

**Problem:** Zero-shot object detection (ZSD) requires localizing and recognizing objects from categories unseen during training, yet current methods struggle to maintain detection precision when the semantic gap between training and testing categories widens.

**Gap:** Existing CLIP-based zero-shot detectors, such as ViLD (Gu et al., 2022) and RegionCLIP (Zhong et al., 2022), treat region-level alignment as a simple feature-matching problem, discarding the spatial and relational structure that human-annotated detection data implicitly encodes; as a result, their recall degrades by 15-25 AP points on categories whose visual appearance diverges from any training-set category.

**Contribution:** A structure-aware vision-language alignment framework that preserves spatial relational priors during region-text matching, enabling zero-shot detectors to generalize to visually distant categories without additional training data or vocabulary expansion.

## Contribution Claims

1. A region-relation graph module that encodes pairwise spatial and semantic relationships between candidate regions before alignment with text embeddings, improving recall on visually distant novel categories by a measurable margin over flat region-text matching.

2. A curriculum-based alignment loss that progressively increases the semantic distance between training-time category pairs during region-text contrastive learning, forcing the detector to develop robust cross-modal representations rather than relying on superficial visual-semantic shortcuts.

3. A diagnostic evaluation protocol that stratifies zero-shot detection performance by the visual-semantic distance between test categories and the nearest training category, exposing failure modes that aggregate metrics (mAP) obscure.

4. Empirical evidence, across COCO and LVIS benchmarks, that preserving relational structure during alignment closes 30-40% of the performance gap between zero-shot and fully-supervised detectors on the most distant novel categories, while maintaining competitive performance on near-domain categories.

## Risk Conditions

**Risk 1: Relational structure may not transfer across domains.**
This story fails when the spatial relational patterns learned from base categories (e.g., "person riding horse") do not generalize to novel categories with fundamentally different spatial configurations (e.g., "microscope on slide"). If relational priors are category-specific rather than category-agnostic, the graph module adds parameters without adding generalization.

**Risk 2: CLIP embeddings may already capture sufficient relational information.**
This story fails when ablation shows that larger or better-pretrained CLIP backbones achieve comparable improvements without the explicit relational module, suggesting the gap we address is an artifact of limited pretraining scale rather than a structural limitation of flat alignment.

**Risk 3: The curriculum schedule may be brittle.**
This story fails when the curriculum-based loss requires extensive per-dataset hyperparameter tuning for the distance schedule, making the method impractical to apply to new benchmarks and undermining the claim of improved generalization.
