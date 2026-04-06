# Towards Robust Zero-Shot Object Detection via Vision-Language Alignment

**Authors:** [TBD]
**Affiliation:** [TBD]

## Abstract

Zero-shot object detection (ZSD) aims to detect objects of unseen categories without training examples. While vision-language models like CLIP have shown remarkable zero-shot classification ability, adapting them for detection remains challenging due to the gap between image-level alignment and region-level localization. We propose RegionCLIP-Det, a framework that bridges this gap through a novel region-text alignment module that operates on proposal features. Preliminary results on COCO and LVIS suggest competitive performance with significantly fewer training categories.

## 1. Introduction

The ability to detect arbitrary objects described in natural language is a long-standing goal in computer vision. Traditional object detectors require bounding box annotations for every target category, making them expensive to scale. Zero-shot detection addresses this by transferring knowledge from seen to unseen categories.

Recent vision-language models, particularly CLIP, have demonstrated strong zero-shot transfer for image classification. However, detection requires localizing objects within images, which CLIP's image-level training does not directly support. Several approaches have attempted to bridge this gap. OVR-CNN proposed using CLIP embeddings as classifier weights. ViLD distilled CLIP features into a two-stage detector. GLIP unified detection and grounding through reformulation.

Despite these advances, two fundamental problems remain:
1. Region features extracted from detection backbones are not aligned with CLIP's visual embedding space
2. The granularity mismatch between image-level and region-level representations causes false positives on background regions

We propose RegionCLIP-Det to address both issues through...

## 3. Method

### 3.1 Overview

Our framework consists of three components:
1. A proposal generator (class-agnostic RPN)
2. A region-text alignment module (our main contribution)
3. A detection head that combines localization and classification scores

### 3.2 Region-Text Alignment Module

Given region proposals from the RPN, we extract region features using RoIAlign. The key challenge is projecting these features into CLIP's embedding space without losing localization information.

[TODO: describe the projection network architecture]
[TODO: describe the contrastive learning objective]
[TODO: describe the negative mining strategy for background suppression]

### 3.3 Training Strategy

[TODO: describe the seen/unseen category split]
[TODO: describe the training losses]
