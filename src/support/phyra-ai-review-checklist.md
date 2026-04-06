# Phyra AI Review Checklist — 領域別評審標準

> **用途：** 供 `phyra-peer-review-criteria`、`phyra-experiment-design` 等 skill 參照。
> 評審時必須對照領域標準判斷，而非僅依賴通用原則。
> （參見 `Phyra-architecture.md` L184）

---

## 1. Computer Vision (CV)

### 1.1 Baselines

| 任務 | 預期 Baseline |
|------|--------------|
| Image Classification | ResNet-50/101, ViT-B/L, DeiT, Swin Transformer, ConvNeXt |
| Object Detection | Faster R-CNN, DETR, DINO, Co-DETR, YOLOv8+ |
| Semantic Segmentation | DeepLabv3+, SegFormer, Mask2Former |
| Instance / Panoptic Seg | Mask R-CNN, Mask2Former, SAM (zero-shot 場景) |
| Image Generation | StyleGAN2/3, Stable Diffusion, DiT |
| Video Understanding | VideoMAE, TimeSformer, InternVideo |

- 若論文聲稱 state-of-the-art，必須與**同期最強方法**比較，而非僅選較弱的經典方法。
- 使用 pre-trained backbone 時須標明預訓練數據集與規模。

### 1.2 Datasets

| 任務 | 標準數據集 |
|------|-----------|
| Classification | ImageNet-1K, ImageNet-21K (pre-train), CIFAR-10/100 |
| Detection | COCO val2017, LVIS, Objects365, VOC 2007/2012 |
| Segmentation | ADE20K, Cityscapes, COCO-Stuff, PASCAL Context |
| Generation | LSUN, FFHQ, ImageNet (FID 評估) |
| Self-supervised | ImageNet-1K (linear probe / fine-tune) |

- 數據集劃分必須使用官方 split；自定義 split 須說明理由並提供劃分方式。
- 應報告訓練集大小、影像解析度等關鍵資訊。

### 1.3 Metrics

| 任務 | 主要指標 | 輔助指標 |
|------|---------|---------|
| Classification | Top-1 / Top-5 Accuracy | Throughput (img/s), FLOPs |
| Detection | mAP@[.5:.95], AP50, AP75 | AP_S / AP_M / AP_L |
| Segmentation | mIoU | aAcc, mAcc, Boundary IoU |
| Generation | FID, IS | LPIPS, Precision/Recall |
| Video | Top-1 Acc, mAP | GFLOPs per clip |

### 1.4 Statistical Conventions

- 大規模數據集（ImageNet）通常**不要求**置信區間，但應報告超參設定與訓練細節。
- 小數據集或 few-shot 場景：需報告 **多次運行均值 ± 標準差**（至少 3 runs）。
- 消融實驗建議固定隨機種子以確保可重現。

### 1.5 Common Pitfalls

- **解析度不公平比較：** 不同方法使用不同輸入尺寸卻未標明或未校正。
- **Test-Time Augmentation (TTA)：** 使用 TTA 提升數字但未在表格中標註。
- **Pre-training 數據洩漏：** 使用包含測試集相關數據的預訓練模型（如 ImageNet-21K 包含部分下游任務類別）。
- **不公平的 FLOPs 比較：** 未統一計算 FLOPs 的方式（有無 backbone、有無 post-processing）。
- **Augmentation 差異：** 對比方法使用不同增強策略卻未控制變量。

---

## 2. Natural Language Processing (NLP)

### 2.1 Baselines

| 任務類型 | 預期 Baseline |
|---------|--------------|
| 通用理解 | BERT-base/large, RoBERTa, DeBERTa-v3 |
| 生成 | GPT-2/3/4, T5, LLaMA 2/3, Mistral, Qwen |
| 翻譯 | mBART, NLLB, GPT-4 (zero-shot) |
| 資訊擷取 | SpanBERT, UIE, ChatGPT (zero-shot) |
| 程式碼 | CodeLLaMA, DeepSeek-Coder, StarCoder |

- LLM 論文須比較**相同參數量級**的模型（7B vs 7B，不可只挑弱的比）。
- 若使用 instruction tuning 或 RLHF，須明確標註訓練階段。

### 2.2 Datasets

| 任務 | 標準 Benchmark |
|------|---------------|
| 通用理解 | GLUE, SuperGLUE, MMLU |
| 問答 | SQuAD 1.1/2.0, Natural Questions, TriviaQA |
| 摘要 | CNN/DailyMail, XSum, SAMSum |
| 翻譯 | WMT (指定年份), FLORES |
| 程式碼 | HumanEval, MBPP, DS-1000 |
| 長文本 | SCROLLS, LongBench, Needle-in-a-Haystack |

- 數據集版本須鎖定（如 SQuAD 1.1 vs 2.0 差異大）。
- 注意 few-shot prompt 的選擇方式是否一致。

### 2.3 Metrics

| 任務 | 主要指標 | 注意事項 |
|------|---------|---------|
| 分類 / NLI | Accuracy, F1 (macro/micro) | 不平衡數據須報告 macro F1 |
| 生成 / 摘要 | ROUGE-1/2/L, BERTScore | ROUGE 須標明 stemming 設定 |
| 翻譯 | BLEU (sacreBLEU), COMET, chrF | 必須使用 sacreBLEU 而非自訂 BLEU |
| 問答 | EM, F1 | 須區分 token-level 與 span-level |
| 語言模型 | Perplexity, bits-per-byte | 須標明 tokenizer 與 context length |

### 2.4 Statistical Conventions

- **顯著性檢驗為必要項：** 至少應使用 paired bootstrap test 或 McNemar's test。
- 報告 **95% confidence interval**（尤其在小數據集上）。
- 多次隨機種子實驗：至少 3-5 runs，報告均值 ± 標準差。
- 使用 LLM 做 zero/few-shot 時，須報告 prompt sensitivity（不同 prompt 的變異程度）。

### 2.5 Common Pitfalls

- **Data Contamination（數據污染）：** LLM 的訓練語料可能包含測試集，須檢查並說明。
- **Tokenizer 不公平比較：** 不同 tokenizer 導致序列長度不同，直接影響 perplexity 和速度。
- **Prompt Engineering 偏差：** 僅報告最佳 prompt 的結果而非平均表現。
- **評估腳本不一致：** 不同論文使用不同版本的評估腳本（如 BLEU 計算方式差異巨大）。
- **微調 vs Zero-shot 混淆：** 將微調結果與他人的 zero-shot 結果比較而未標明。

---

## 3. Multimodal Learning

### 3.1 Baselines

| 任務類型 | 預期 Baseline |
|---------|--------------|
| 圖文對齊 | CLIP, SigLIP, EVA-CLIP |
| 圖文生成 | BLIP-2, InstructBLIP, LLaVA-1.5/NeXT |
| 多模態對話 | GPT-4V/o, Gemini, LLaVA, Qwen-VL |
| 影片理解 | Flamingo, VideoLLaMA, VideoChat |
| 文生圖 | DALL-E 3, Stable Diffusion XL, Midjourney (人工評估) |

- 跨模態方法須標明各模態 encoder 的預訓練來源與是否凍結。
- 多模態 LLM 須比較相同 LLM backbone 規模的方法。

### 3.2 Datasets

| 任務 | 標準 Benchmark |
|------|---------------|
| VQA | VQAv2, OK-VQA, GQA, TextVQA, ChartQA |
| Image Captioning | COCO Captions, NoCaps, Flickr30k |
| Retrieval | COCO Retrieval, Flickr30k Retrieval |
| 綜合評估 | MMBench, MME, SEED-Bench, MM-Vet |
| 影片 QA | MSRVTT-QA, ActivityNet-QA, EgoSchema |

### 3.3 Metrics

| 任務 | 主要指標 |
|------|---------|
| VQA | VQA Accuracy (官方 evaluation server) |
| Captioning | CIDEr, SPICE, CLIPScore |
| Retrieval | Recall@1/5/10 |
| 綜合 | 各 benchmark 自訂分數（MME score 等） |
| 人工評估 | Elo rating, win rate（須報告 annotator agreement） |

### 3.4 Statistical Conventions

- 涉及人工評估時，須報告 **inter-annotator agreement**（Cohen's kappa 或 Fleiss' kappa）。
- VQA 等自動指標通常不要求 CI，但 zero-shot 設定建議報告多 prompt 變異。
- 生成任務應結合自動指標與人工評估。

### 3.5 Common Pitfalls

- **訓練數據規模不對等：** 不同方法使用的圖文配對數量差距巨大（如 400M vs 1B）。
- **Evaluation Protocol 不一致：** 不同 VQA 評測方式（open-ended vs multiple-choice）結果不可比。
- **Vision Encoder 差異：** 使用不同解析度或不同預訓練的 vision encoder 卻未控制。
- **Cherry-picked 範例：** 定性範例只展示成功案例而不展示失敗案例。

---

## 4. Deep Learning (General / Architecture)

### 4.1 Baselines

| 方向 | 預期 Baseline |
|------|--------------|
| 新 Operator / Layer | 對應的標準組件（如新 attention → vanilla attention, linear attention） |
| 新 Architecture | 同等規模的 Transformer, CNN, MLP-Mixer, Mamba/SSM |
| 優化方法 | AdamW, SGD + momentum, Lion, Schedule-Free |
| 正則化方法 | Dropout, Weight Decay, Label Smoothing, Mixup |
| 高效訓練 | Standard training, LoRA, QLoRA, knowledge distillation |

- Architecture 論文須在**多個下游任務**上驗證通用性，不可只在單一任務上展示。
- 新組件須提供與標準組件的 **drop-in replacement** 比較。

### 4.2 Datasets

- 至少涵蓋兩個以上領域（如 CV + NLP）以證明通用性。
- 建議包含一個大規模任務（ImageNet / C4）和一個小規模任務。
- Scaling law 相關論文須覆蓋足夠多的模型規模點（至少 4-5 個量級）。

### 4.3 Metrics

| 類型 | 必須報告 |
|------|---------|
| 效能 | 各任務對應的標準指標 |
| 效率 | **FLOPs**（forward + backward）, **參數量**, **記憶體使用** |
| 速度 | Wall-clock time (training), Throughput (inference) |
| Scaling | 性能 vs 參數量 / FLOPs 曲線 |

- FLOPs 計算必須標明計算方式（fvcore, DeepSpeed profiler, 手動推導等）。
- 參數量須區分 total params 與 trainable params。

### 4.4 Statistical Conventions

- 不同隨機種子的消融實驗至少 3 runs。
- Scaling law 擬合須報告 R-squared 及外推可靠性。
- 訓練曲線（loss curve）建議附上以驗證收斂性。

### 4.5 Common Pitfalls

- **FLOPs 不一致：** 不同方法的 FLOPs 統計口徑不同（是否包含 embedding, head, normalization）。
- **僅報告最佳超參數：** 未展示超參數敏感性分析。
- **忽略實際速度：** FLOPs 低但實際推理速度因硬體利用率低反而更慢。
- **過度消融：** 每次只移除一個組件而忽略組件間的交互作用。
- **訓練成本隱藏：** 未報告實際使用的 GPU 類型、數量、訓練時間。

---

## 5. Robotics / Embodied AI

### 5.1 Baselines

| 任務類型 | 預期 Baseline |
|---------|--------------|
| 操作 (Manipulation) | BC (Behavior Cloning), RT-1/2, Diffusion Policy, ACT |
| 導航 (Navigation) | PointNav baselines, VLN-CE, Habitat baselines |
| 移動 (Locomotion) | PPO/SAC + MLP, AMP, model-based RL |
| 規劃 (Planning) | SayCan, Code-as-Policies, VoxPoser |
| 基礎模型 | RT-2, Octo, OpenVLA |

- 須與**同等感測器輸入**的方法比較（RGB-only vs RGB-D vs point cloud）。
- 使用 foundation model 的方法須與 task-specific 方法對比。

### 5.2 Datasets / Benchmarks

| 環境 | 標準 Benchmark |
|------|---------------|
| 模擬 - 操作 | ManiSkill2, RLBench, MetaWorld, LIBERO |
| 模擬 - 導航 | Habitat, iGibson, AI2-THOR |
| 模擬 - 移動 | IsaacGym, MuJoCo (locomotion suites) |
| 真實世界 | DROID, Open X-Embodiment, Bridge V2 |
| Language Grounding | ALFRED, TEACh, Embodied QA |

- **Sim-to-Real：** 若方法聲稱可遷移至真實世界，必須提供真實世界實驗結果。
- 模擬環境須標明 physics engine 版本與 rendering 設定。

### 5.3 Metrics

| 任務 | 主要指標 | 補充指標 |
|------|---------|---------|
| 操作 | Success Rate (%) | Completion Rate, Path Efficiency |
| 導航 | SPL (Success weighted by Path Length) | SR, Navigation Error |
| 移動 | Reward, Velocity Tracking Error | Energy Consumption |
| 泛化 | 新物件 / 新場景的成功率 | Sim-to-Real Gap |
| 安全 | Collision Rate, Constraint Violations | — |

### 5.4 Statistical Conventions

- 每個任務配置至少 **50-100 episodes**（模擬中可更多）。
- 須報告 **均值 ± 標準差** 或 **95% CI**，真實世界實驗尤其重要。
- 真實世界實驗須明確報告試驗次數、環境條件、失敗案例分析。
- 不同隨機種子至少 3 runs（模擬環境中建議 5 runs）。

### 5.5 Common Pitfalls

- **Sim-to-Real Gap 忽略：** 僅在模擬中驗證卻聲稱適用於真實場景。
- **環境過度簡化：** 使用過於簡單的模擬環境（無干擾、固定光照、確定性動力學）。
- **成功率定義模糊：** 未明確說明「成功」的判定標準（如抓取是否需要維持 N 秒）。
- **缺乏泛化實驗：** 僅在訓練時見過的物件 / 場景上評估。
- **硬體細節缺失：** 未報告機器人型號、感測器規格、控制頻率等關鍵資訊。
- **可重現性不足：** 未提供模擬環境的完整配置檔或真實世界實驗的影片佐證。

---

## 通用評審提醒

以下要求適用於所有領域：

1. **Baseline 時效性：** baseline 須包含近 1-2 年內的 SOTA 方法，不可僅與 3 年以上的舊方法比較。
2. **公平性：** 所有比較方法須在相同條件下評估（相同數據、相同計算資源範圍、相同評估協議）。
3. **開源與可重現：** 優先引用有開源代碼的 baseline 結果；若使用自行復現的數字須說明。
4. **計算預算：** 須報告總計算成本（GPU hours 或碳排放估算），尤其是大規模實驗。
5. **局限性：** 論文須誠實討論方法的局限性與失敗案例，不可僅展示成功場景。

---

> **維護說明：** 此 checklist 應隨領域發展定期更新。當新的標準 baseline 或 benchmark
> 出現時（如新一代基礎模型），應由維護者補充至對應章節。
