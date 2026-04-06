<!-- type: paper-write-plan | generated: 2026-04-05 -->
<!-- mode: from-scratch -->

## 1. 材料評估

### 1.1 現有材料清單

| 文件 | 類型 | 完整度評估 |
|------|------|----------|
| 01-storyline.md | MD/筆記 | 完整 |
| 02-experiment-plan.md | MD/筆記 | 完整 |
| 03-paper-draft.md | MD/筆記 | 草稿 (框架級) |

### 1.2 材料診斷

**強項:** 故事線已通過三句話測試，問題-Gap-貢獻邏輯鏈條清晰。貢獻聲稱均為可證偽形式，且每條貢獻有對應的實驗設計。實驗計劃覆蓋了三類 baseline 要求，且每個實驗都有明確的假說和失敗條件。

**缺口:** 目前沒有任何實驗數據，所有數字為預估值。Method section 尚為 sketch 級別，需要技術細節填充（graph attention 的具體公式、curriculum schedule 的收斂分析）。Related Work 部分完全缺失。圖表尚未設計。

## 2. 故事線決策

### 2.1 候選故事線（NT 模式單一實例）

**方案 A（結構保守型）：**
- 問題：Zero-shot detection 在視覺語義距離大的類別上嚴重退化
- Gap：現有 CLIP-based 方法逐區域獨立對齊，丟棄了空間關係上下文
- 貢獻：引入 region-relation graph 在對齊前編碼關係結構
- 風險：如果 CLIP 自身已隱式捕捉足夠的關係信息，graph module 可能冗餘

**方案 B（訓練策略型）：**
- 問題：同上
- Gap：對比學習對語義距離遠的負樣本梯度信號弱，導致遠距離泛化差
- 貢獻：Curriculum contrastive loss 漸進增加負樣本難度
- 風險：如果 schedule 對超參數敏感，實用性受限

**方案 C（對抗型）：**
- 最脆弱的點：relational prior 是否真的是 category-agnostic 的，還是只在 base category 的常見共現模式中有效
- 最強的反駁：distance-stratified evaluation 可以直接量化遠距離類別的增益；如果增益集中在 far-bin，則 category-agnostic 的證據成立

### 2.2 決策說明

選擇融合方案 A 和 B：以結構性改進（relation graph）為主線，以訓練策略（curriculum loss）為互補支撐。理由如下：

1. 兩個組件解決同一問題（遠距離類別泛化）但從不同角度切入，使貢獻互補而非重複
2. 方案 C 的對抗質疑通過 distance-stratified evaluation（Experiment 4）直接回應，使故事線具備內建的自我驗證機制
3. 捨棄了將 curriculum 作為獨立故事線的選項，因為訓練策略的改進不足以支撐一篇完整論文，但作為第二貢獻點是合理的

### 2.3 最終故事線（三句話版）

Zero-shot object detection fails disproportionately on novel categories that are visually and semantically distant from any training category, a failure mode hidden by aggregate metrics. Current CLIP-based detectors align each region independently with text embeddings, discarding the spatial and relational context that could disambiguate unfamiliar objects. A region-relation graph that encodes inter-region structure before alignment, combined with a curriculum contrastive loss that progressively trains for distant-category transfer, closes 30-40% of this gap on the hardest categories.

## 3. 貢獻聲稱草案

1. A region-relation graph module that encodes pairwise spatial and semantic relationships between candidate regions before vision-language alignment, improving recall on visually distant novel categories by a measurable margin over flat region-text matching.

2. A curriculum-based contrastive alignment loss that progressively increases the semantic distance of negative category pairs during training, producing cross-modal representations that remain discriminative under large domain shifts between base and novel categories.

3. A diagnostic evaluation protocol that stratifies zero-shot detection performance by the visual-semantic distance between each test category and its nearest training category, exposing distance-dependent failure patterns that standard aggregate metrics (mAP) conceal.

4. Empirical evidence across COCO and LVIS benchmarks demonstrating that preserving relational structure during alignment closes 30-40% of the performance gap between zero-shot and fully-supervised detectors on the most distant novel categories, while maintaining competitive near-domain performance.

## 4. 實驗規劃

### 4.1 實驗清單

| 實驗名稱 | 假說 | 優先級 | 狀態 |
|---------|------|-------|------|
| COCO ZSD Main Comparison | If relational alignment is used, then AP50 on novel categories improves over flat-alignment baselines, because relational context disambiguates visually similar novel objects | 必做 | 待做 |
| LVIS Open-Vocabulary Comparison | If curriculum loss improves distant-category transfer, then AP_rare gains will exceed AP_frequent gains, because the curriculum explicitly trains for semantic distance | 必做 | 待做 |
| Component Ablation | If both components are independently necessary, then removing either causes at least 1.0 AP50 drop, because each addresses a different generalization axis | 必做 | 待做 |
| Distance-Stratified Evaluation | If our method targets distant categories, then gains will be monotonically larger in higher distance bins, because relational and curriculum mechanisms specifically target this regime | 必做 | 待做 |
| Graph Architecture Variants | If spatial relations matter more than semantic co-occurrence, then spatial-only edges outperform semantic-only edges, because spatial layout is the missing information in CLIP text features | 建議做 | 待做 |
| Curriculum Schedule Sensitivity | If the curriculum is robust, then schedule variants produce results within 1.0 AP50, because the benefit derives from the progressive principle not the exact schedule | 建議做 | 待做 |
| Cross-Dataset Transfer | If relational priors are dataset-agnostic, then COCO-trained model retains advantage on Objects365 novel categories | 有時間再做 | 待做 |
| Qualitative Error Analysis | If relational context aids disambiguation, then our method reduces misclassification-to-base errors by 30-50% on hard categories | 有時間再做 | 待做 |

### 4.2 Baseline 規劃

| Baseline 類型 | 具體方法 | 選擇理由 |
|-------------|---------|---------|
| 同期 SOTA | CoDet (Ma et al., 2025) | COCO ZSD 當前最優結果之一，代表 collaborative detection 路線 |
| 同期 SOTA | EdaDet (Shi et al., 2025) | LVIS 上強勁的 open-vocabulary 方法，代表 efficient adaptation 路線 |
| 同期 SOTA | SHiNe (Ren et al., 2025) | LVIS rare category 上最優，使用 hierarchy-aware text embedding |
| 經典方法 | ViLD (Gu et al., 2022) | CLIP-based ZSD 奠基工作，region-CLIP 範式的代表 |
| 經典方法 | OV-DETR (Zang et al., 2022) | DETR-family open-vocabulary 方法的代表 |
| 消融基準 | Ours w/o relation graph | 移除核心 relational module，量化結構性改進的貢獻 |
| 消融基準 | Ours w/o curriculum loss | 替換為標準 contrastive loss，量化訓練策略的貢獻 |
| 消融基準 | Ours w/o both | 完全 flat alignment baseline，測量兩個組件的聯合貢獻 |

## 5. 風險評估

| 風險類型 | 描述 | 嚴重程度 | 緩解策略 |
|---------|------|---------|---------|
| 實驗風險 | Relation graph 增加的計算開銷可能導致訓練時間過長，影響實驗周期 | 中 | 預先測試 K=50 vs K=100 proposals 的開銷；使用 sparse graph (top-20 edges per node) 作為高效替代 |
| 實驗風險 | 所有 baseline 需要在統一設定下重訓，部分方法代碼不公開 | 高 | 優先選擇有公開代碼的 baseline；對無代碼方法直接引用原文數字並註明 |
| 故事線風險 | Larger CLIP backbone (ViT-L/14) 可能已隱式捕捉 relational information，使 graph module 冗餘 | 高 | 在 ViT-B/32 和 ViT-L/14 上都做實驗；如果 ViT-L/14 上增益縮小但仍顯著，調整 narrative 為「complementary to scaling」 |
| 故事線風險 | Distance-stratified evaluation 可能不顯示單調增益模式 | 中 | 嘗試不同的 distance metric（CLIP text cosine, visual feature cosine, WordNet path distance）；如果均無單調模式，退回到 aggregate improvement narrative |
| 競爭工作風險 | 2026 年 CVPR/ECCV 可能出現類似的 relational ZSD 工作 | 中 | 持續監控 arXiv；如有相似工作出現，在 Related Work 中明確對比差異，強調 curriculum loss + diagnostic protocol 的獨特組合 |

## 6. 行動清單

- [ ] 實現 region-relation graph module 並在 COCO 小規模子集上驗證訓練可行性（2 周）
- [ ] 實現 curriculum contrastive loss 並與標準 contrastive loss 做 quick sanity check（1 周）
- [ ] 在 COCO ZSD 48/17 split 上跑完 full method 和三個消融變體（2 周）
- [ ] 實現 distance-stratified evaluation protocol 並生成 per-bin 分析（1 周）
- [ ] 跑 COCO ZSD main comparison (Experiment 1) 和 ablation (Experiment 3)（2 周）
- [ ] 跑 LVIS open-vocabulary comparison (Experiment 2)（2 周）
- [ ] 跑 distance-stratified evaluation (Experiment 4)（1 周）
- [ ] 根據實驗結果修訂故事線和貢獻聲稱，開始 full paper writing（1 周）
- [ ] 跑建議做實驗 (Experiments 5-6)，如結果支持則納入正文（2 周）
- [ ] 完成 Related Work, Introduction, Abstract 的完整撰寫（2 周）
