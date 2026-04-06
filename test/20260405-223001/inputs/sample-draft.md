# Efficient Memory Management for Streaming Visual Geometry Transformers

**Authors:** [TBD]
**Affiliation:** [TBD]

## Abstract

Streaming 3D reconstruction from monocular video requires processing frames causally while maintaining geometric consistency over time. Recent visual geometry transformers like VGGT achieve impressive offline performance but fail in streaming scenarios due to unbounded memory growth. We propose MemStream, a memory-efficient framework that introduces adaptive token management for streaming geometry transformers. Our approach maintains a fixed-size memory buffer through importance-weighted token selection, enabling infinite-length video processing with bounded GPU memory. Preliminary results on indoor reconstruction benchmarks suggest competitive performance with significantly reduced memory footprint.

## 1. Introduction

Visual geometry understanding from monocular video is a cornerstone of computer vision, enabling applications in autonomous navigation, augmented reality, and robotics. The recent VGGT model demonstrated that a single feed-forward transformer can jointly predict camera poses, depth maps, and 3D point clouds from unposed images, achieving state-of-the-art performance across multiple geometry tasks.

However, VGGT operates in batch mode, processing a fixed number of frames simultaneously. This design is fundamentally incompatible with streaming applications where frames arrive continuously. While StreamVGGT addresses this by adding causal attention masking, it accumulates all historical tokens in its KV cache, leading to linear memory growth that eventually exhausts GPU resources.

The core challenge is: how can we maintain a bounded-size KV cache while preserving the geometric information necessary for accurate reconstruction?

## 3. Method

### 3.1 Overview

Our framework consists of three components:
1. A streaming geometry transformer backbone (based on StreamVGGT)
2. A token importance scoring module
3. A memory management policy that enforces a fixed budget

### 3.2 Token Importance Scoring

[TODO: describe the importance scoring mechanism]
[TODO: compare attention-based vs. feature-based approaches]
[TODO: describe how to handle the coordinate reference frame]

### 3.3 Memory Budget Enforcement

[TODO: describe the eviction policy]
[TODO: describe per-layer budget allocation]

## 4. Experiments

[TODO: setup and results]
