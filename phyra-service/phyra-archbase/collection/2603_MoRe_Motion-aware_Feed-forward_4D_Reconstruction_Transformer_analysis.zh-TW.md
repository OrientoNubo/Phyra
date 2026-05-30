<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# MoRe — MoRe: Motion-aware Feed-forward 4D Reconstruction Transformer

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | MoRe |
| Paper full title | MoRe: Motion-aware Feed-forward 4D Reconstruction Transformer |
| arXiv ID | 2603.05078 |
| Release date | 2026-03-06 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.05078 |
| PDF link | https://arxiv.org/pdf/2603.05078 |
| Code link | — |
| Project page | https://hellexf.github.io/MoRe/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Junton Fang | School of Software, Tsinghua University | — | first author (equal contribution) |
| Zequn Chen | Li Auto | — | co-first author (equal contribution); project lead |
| Weiqi Zhang | School of Software, Tsinghua University | — | co-first author (equal contribution) |
| Donglin Di | Li Auto | https://scholar.google.com/citations?hl=en&user=L8tcNioAAAAJ | co-author |
| Xuancheng Zhang | School of Software, Tsinghua University; Li Auto | — | co-author |
| Chengmin Yang | Li Auto | — | co-author |
| Yu-Shen Liu | School of Software, Tsinghua University | https://yushen-liu.github.io/ | corresponding author |

### 1.2 Keywords

4D reconstruction, feed-forward transformer, monocular video, motion-aware attention, attention forcing, grouped causal attention, streaming reconstruction, camera pose estimation

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al.) | base model | MoRe builds upon VGGT's transformer backbone for jointly inferring camera poses and depth across multiple views. |
| Dust3R (Wang et al., [41]) | predecessor | Pioneers point-map regression for reconstruction; MoRe inherits its confidence-weighted regression objective. |
| MASt3R ([18]) | influence | Improves correspondences and scalability of pointmap regression that MoRe extends to dynamic scenes. |
| Fast3R ([46]) | influence | Scalable feed-forward reconstruction baseline cited as motivation for efficient transformer design. |
| MapAnything ([16]) | baseline | Full-attention feed-forward baseline directly compared on Sintel/Bonn/TUM/ScanNet camera-pose benchmarks. |
| CUT3R ([40]) | baseline | Transformer-based persistent latent state for online dense reconstruction; key streaming-mode comparison. |
| Spann3R ([38]), StreamVGGT ([61]), Wint3R ([20]), Stream3R ([17]) | baseline | Streaming/causal-attention 4D reconstruction systems benchmarked against MoRe's streaming variant. |

## 2. Research Overview

### 2.1 Research Topic

本論文研究單目影片的 4D 場景重建 (4D reconstruction),目標是在動態場景中同時估計相機位姿、深度圖、點雲與動態遮罩。傳統 SfM/SLAM 在動態物體存在時因運動造成位姿估計失準;近年的 feed-forward 模型 (如 Dust3R、VGGT) 多在靜態資料上訓練,面對運動物體會混淆相機 token 的注意力;混合式優化管線雖可處理動態場景,但因多階段或迭代精煉,計算成本高、難以串流即時運作。作者提出 MoRe,以強健的靜態重建骨幹為基礎,透過 attention-forcing 訓練策略將動態運動與靜態結構顯式解耦,並設計 grouped causal attention 與 BA-like 全域聚合機制,使模型能以串流方式處理長序列影片並維持時間一致性,實現高效率、可泛化的動態 4D 重建。

### 2.2 Domain Tags

- Computer Vision
- 3D / 4D Reconstruction
- Dynamic Scene Understanding
- Visual SLAM / Streaming Inference

### 2.3 Core Architectures Used

- **VGGT backbone (inherited)**:作為 MoRe 的靜態重建骨幹,提供跨多視角聯合推論相機位姿與深度的 transformer 基礎,MoRe 在其上進行 fine-tuning 以擴展至動態場景。
- **ViT Encoder (inherited)**:對每幀 $I_t \in \mathbb{R}^{3 \times H \times W}$ 進行 patch tokenization,產生 image tokens 與 camera token,作為後續注意力聚合的輸入單元。
- **DPT Head (inherited)**:dense prediction transformer 頭部,負責由 token 特徵回歸出 per-frame 的 depth maps、point maps 與 motion masks。
- **Camera Head (inherited)**:由 camera token 解碼出每幀的 9 維相機參數 $g_t \in \mathbb{R}^9$,涵蓋旋轉與平移。
- **Motion-aligned Attention (proposed)**:訓練階段以 ground-truth motion mask 計算每個 image token 的 motion score $a_i \in [0, 1]$,並透過 confidence-like loss 強迫 camera token 的 attention 分布 $\{\alpha_i\}$ 偏離動態區域,推論時不需任何遮罩輸入,屬 test-time-free 設計。
- **Grouped Causal Attention (proposed)**:將傳統上三角 causal mask 改寫為 frame-wise causal mask,允許同幀內 image tokens 雙向互看、跨幀則嚴格因果,搭配 KV-cache 支援串流長序列推論並兼顧空間一致性。
- **BA-like Token Aggregation (proposed)**:在序列處理完成後,將 cached camera queries $Q^{\text{cam}}_t$ 對全序列 $[K_{1:T}, V_{1:T}]$ 重做一次 attention,模擬 bundle adjustment 的全域優化以修正長序列下的位姿漂移。
- **Confidence-weighted Regression Loss (inherited from Dust3R/VGGT)**:對 depth 與 point map 採用 $L_{\text{conf}} = \sum_i (\hat{c}_i \|\hat{y}_i - y_i\|_2^2 - \lambda \log(\hat{c}_i))$,聯合學習預測值與其置信度。

### 2.4 Core Argument

作者主張現有 feed-forward 4D 重建方法的根本問題在於:相機 token 的注意力無法區分動態物體與靜態背景,當動態區域擾動到原本應由靜態幾何主導的特徵聚合時,位姿與深度估計便會大幅退化 (如 Fig. 3 所示,VGGT 在動態場景中的 attention map 幾乎均勻分布)。要徹底解決此一退化,單純加大資料或加入光流、分割等顯式先驗都不夠,因為前者無法教導模型「哪些區域不該被信任」,後者則破壞 feed-forward 的簡潔性並增加推論成本。因此,作者的解法是在訓練階段以 ground-truth motion mask 將每個 image token 的「靜態先驗」(motion score) 注入到相機 token 的 attention 分布上,透過 confidence-like loss 強迫 attention 權重避開動態區域,而推論階段不需任何遮罩或額外輸入,完全 test-time-free。這是邏輯上必要的:既要保留 feed-forward 的低延遲,又要修正 attention 在動態場景被誤導的根因,只能在訓練監督層面動手術。其次,串流重建另一個必然問題是長序列下的全域漂移:嚴格 causal mask 雖能 KV-cache 加速,但相機 token 失去未來幀的全域資訊,長期累積誤差。作者再以 grouped causal attention (允許同幀內 image token 雙向互看,跨幀則嚴格因果) 維持空間一致性,並在序列處理完後對 cached camera queries 重做一次跨全序列 attention,模擬 bundle adjustment 的全域優化。兩個機制合起來,正好對應動態場景串流 4D 重建中「空間-運動解耦」與「時間-全域一致」這兩個必須同時解決的子問題。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題 "MoRe: Motion-aware Feed-forward 4D Reconstruction Transformer" 一次性把論文的三個關鍵字立起來：motion-aware（針對動態場景的設計動機）、feed-forward（與優化式管線的速度區隔）、4D Reconstruction Transformer（任務範疇與骨幹族系）。讀者在第一秒便能定位它在 4D 重建文獻中的位置：不是 SLAM、不是 hybrid optimization，而是一個直接前饋的 transformer 解法。

Abstract 採用「問題 → 既有限制 → 方法 → 結果」的緊湊論證鏈。開場句指出 4D scene 重建的核心痛點是 moving objects 會破壞 camera pose estimation；接著批評 optimization-based 方法雖有 additional supervision 但代價是 computationally expensive、無法 real-time。接著引入 MoRe 的兩個關鍵設計：建立在強 static reconstruction backbone 之上的 attention-forcing strategy 用以 disentangle dynamic motion 與 static structure；以及 grouped causal attention 用來捕捉 temporal dependencies 並適配 frame 間 token 長度的變化。最後並未列出具體數字，僅以 "extensive experiments on multiple benchmarks" 與 "exceptional efficiency" 收尾，把量化證據留給後文。

整段 abstract 為全文鋪了三條伏筆：static backbone fine-tune、attention 監督、causal streaming，正好對應後續 §3 的三個子節。

### 3.2 Introduction

(640 words)

Introduction 採取教科書式的「擴張—收縮—承諾」三段論。第一段先把 4D 重建放進 AR、robotics、digital twins 等應用情境裡，提升任務重要性，並交代 SfM/MVS 與 SLAM 等 classical pipeline 的歷史角色——它們在 static、controlled 環境下表現良好，但一旦物件 deform 或 camera 大幅運動就失效。這建立起「靜態假設崩壞」這個基本病灶。

第二段把鏡頭轉到 deep learning，並把現有方法切成兩派：real-time feedforward models（一次推論輸出 pose 與 depth/point cloud，但訓練資料偏 static，動態下退化）以及 hybrid optimization pipelines（整合 depth、optical flow、motion segmentation，但保留 multi-stage 或 iterative refinement，計算昂貴、不適合 streaming）。這個二分法明確界定了論文要打的空白。

第三段直接點名 gap：如何設計一個快速、可泛化、能在 streaming 或 long sequence 下處理 camera 與 object motion 的框架。隨即提出 MoRe，並用一句話框出 core innovation——「purely through training」教模型分辨 dynamic objects 與 static background，而不在 inference 引入 motion 或 segmentation prior。這把 MoRe 與 hybrid 派切割開來：別人靠 explicit module，我靠 supervision。

第四段補上 streaming side：grouped causal attention 加上 BA-like incremental refinement，並強調 attention 機制可適應 token 長度差異，refinement 則維持 temporal consistency。再以 "large-scale finetuning on diverse static and dynamic datasets" 收尾，補強通用性主張。

最後條列四點 contribution：(1) 統一的 motion-aware 4D 框架，能聯合估計 pose、depth、motion mask；(2) attention-forcing 訓練策略；(3) grouped causal attention 加 BA-like streaming refinement；(4) 在多個 benchmark 上達到 SOTA 與強泛化。

整節 introduction 為後文做了精準的引導：第二段的二分法直接對應 §2 的 Related Work 結構（4D Reconstruction、Learning-based、Streaming），第三段的「training 而非 inference prior」對應 §3.2 motion-aligned attention，第四段的 streaming refinement 對應 §3.3 grouped causal attention。讀者在離開 intro 時已經知道方法包含哪三塊，以及為何需要這三塊。

### 3.3 Related Work / Preliminaries

(540 words)

Related Work 沿用 Introduction 的三段式劃分，但把每段都寫成「他人做了什麼 → 限制 → 我們如何不同」的對照結構，這讓 §2 同時扮演 literature survey 與 positioning statement。

§2.1 4D Reconstruction 從 optimization-based systems 切入，列舉它們依賴 optical flow、masks 等 auxiliary cues，但 computationally heavy；接著提及 modular pipelines 借力 foundation model，仍嫌複雜；再列出 temporally aligned point-map regression 一派，批評其缺少 explicit motion-static disentanglement 且需要 dense 4D supervision。最後一句明確宣告 MoRe 保留 elegant feed-forward 架構，並把 motion-static 分離搬到 training 階段，確保 inference 仍 lightweight。這個段落把 §3 的整體哲學鎖定為「training-time supervision 取代 inference-time module」。

§2.2 Learning-based Reconstruction 的脈絡是 Dust3R → MASt3R → Fast3R → VGGT 的演進史，將焦點收斂到 transformer-based 方法的兩個共同弱點：inference cost 對 sequence length 的 quadratic scaling，以及缺乏 explicit motion modeling。這兩點正好對應 §3.3 的 causal attention（解 quadratic 與 streaming 問題）與 §3.2 的 motion-aligned attention（解 motion modeling 缺位）。換句話說，§2.2 為 §3 的兩個技術子節分別樹立了標靶。

§2.3 Streaming Reconstruction 把鏡頭轉向 SLAM 與 CUT3R-style persistent latent state，再點名近期採用 LLM-style causal attention 與 KV-caching 的系統。作者隨即指出 LLM-style causal attention 直接套用到 3D 重建上的兩個破綻：把 token 視為 flat sequence 會破壞 intra-frame 的 token correspondence；streaming 的硬性 causal 設定會讓誤差累積、產生 long-term context drift。對應地，§3.3 的 grouped causal attention 用 frame-wise mask 解第一個問題，BA-like token aggregation 解第二個問題。

整節 Related Work 的功能不只是 cite 文獻，而是把每個既有派別的弱點精準對應到後文的特定設計，使讀者進入 §3 時能直接讀出每個模組要解決的具體 baseline 問題。論文沒有獨立的 Preliminaries 章節，§3.1 Problem Formulation 才會給出符號定義與 streaming reformulation，但 §2 已經完成了概念層的鋪墊。

### 3.4 Method (overview narrative)

(290 words)

§3 Method 的開場宣告 MoRe 是針對 streaming input 設計的 feed-forward transformer，並搭配一個 BA-like global alignment module。Fig. 2 提供整體 pipeline：每個 frame 經 ViT Encoder 抽取 image token 並附帶一個 camera token，全部送入 Aggregated Transformer 中的 Motion-Aligned Frame Attention，最後由 Camera Head 與 DPT 分頭輸出 camera pose、point map、depth map 與 motion mask。

整章被切成四個子節，敘事順序刻意先抽象後具體：§3.1 Problem Formulation 先把 monocular video 重建寫成 streaming function，輸出每幀的 depth、camera parameter、point map，並進一步把 motion mask 加入輸出集合，但同時聲明 motion mask 並非 input、只在 training 用作 supervision；§3.2 Motion-aligned Attention 處理「如何在 training 把 motion 資訊灌進 attention」；§3.3 Grouped Causal Attention 處理「如何在 inference 同時兼顧 streaming causality 與 intra-frame spatial coherence」；§3.4 Training Objective 把上述兩個技術綁進統一的 loss 配方（confidence-weighted regression、BCE、attention alignment、relative camera loss）。

這個結構的核心邏輯是：先用 §3.1 把任務寫成 streaming 形式，逼出 causal 與 cache 的需求；再用 §3.2 處理 quality 端（怎樣讓 transformer 看對地方），用 §3.3 處理 efficiency 端（怎樣讓 transformer 跑得起來），最後用 §3.4 把兩者的監督訊號整合。Method 章不對任何模組做 component-level 細節展開（那留給後續章節），它只負責把「為何需要這三個模組」與「它們如何串成一條 pipeline」交代清楚，為後文的 quantitative 與 qualitative 比較設定詮釋框架——讀者進入 §4 時已經知道 attention forcing 與 grouped causal attention 是兩個獨立可剝離的元件，因此會自然期待後面的 ablation 證明這兩塊各自的貢獻。

### 3.5 Experiments (overview narrative)

(300 words)

§4 Experiments 的整體節奏是「資料 → 任務 → 消融」，刻意把 generalization 與 component-wise 證據分層呈現。

開場 Datasets 段落列出十二個訓練資料集，涵蓋 Dynamic Replica、PointOdyssey、Spring、Virtual KITTI、TartanAir、Co3Dv2、ScanNet、BlendedMVS、Hypersim、ARKitScenes、Waymo、OmniWorld-Game，並聲明 indoor/outdoor、static/dynamic、不同 lighting 與 motion pattern 都涵蓋；資料量少的 dataset 會被等比 duplicate 以平衡分布。這段重點不是 dataset 細節，而是建立「訓練分布夠廣 → 評測時的 zero-shot 結果可信」的因果鏈。

§4.1 Camera Pose Estimation 用 Sintel、TUM-dynamics、Bonn 三個 dynamic dataset 加上 ScanNet 一個 static dataset 評估，刻意聲明三個 dynamic dataset 完全沒在 training 中出現，藉此把表格結果框定為 zero-shot generalization 證據。指標選擇 ATE、RPEtrans、RPErot 並做 Sim(3) 對齊。論文同時把方法分為 full-attention 與 streaming 兩類做雙軌比較，並聲稱 full-attention 變體達到與 π3 相當的水準（儘管 training data 較少），streaming 變體則 outperform 現有 streaming baseline，證明 attention-forcing 的有效性。

§4.2 Video Depth Estimation 把場景延伸到 Sintel、Bonn、TUM、KITTI，加入 Abs Rel 與 δ<1.25，並沿用 scale-only alignment。這層證據把 §4.1 的 pose 結論延伸到 depth，形成「同一個模型同時擅長 pose 與 depth → 適合做統一 4D 重建」的論述閉環。

§4.3 Ablation Study 把 attention forcing、grouped causal attention、BA-like refinement 三個元件分別拆掉，對應 §3.2、§3.3、§3.3 後段的 BA module。三個 ablation 共同驗證了 method 章對每個模組功能的宣稱，並收束 §4 的整體論證：attention forcing 改善 pose 精度、GCA 改善 depth 與 spatial-temporal consistency、BA-like refinement 改善 long-sequence pose 穩定性。Experiments 章因此既證 SOTA 也證模組必要性。

### 3.6 Conclusion / Limitations / Future Work

(310 words)

§5 Conclusion 採用極短篇幅，僅以一段話收束全文：MoRe 是針對 monocular video 動態 4D 重建的 feed-forward network，attention-forcing 策略讓模型在 inference 不需 explicit motion prior 即可分離 dynamic motion 與 static geometry；streaming inference 結合 grouped causal attention 與 lightweight BA-like refinement，達成 efficient 且 temporally coherent 的重建。整個 conclusion 不引入新內容，僅把 §3 的兩個核心設計與 §4 的整體成果重新貼合。值得注意的是，正文 §5 沒有設立獨立的 Limitations 與 Future Work 子節，正文討論在此打住。

正文之外，supplementary 的 §10 Limitations 補上系統性的不足討論，可視為 conclusion 的延伸：第一，方法重度依賴 motion mask annotation 的精度與一致性，任何 mask 噪聲都會經 supervision 傳播到重建結果，因此在 mask 難以取得的真實場景下會被限制；作者建議未來探索 self-supervised 或更 robust 的 motion 監督方式以降低對 manual/heuristic mask 的依賴。第二，feed-forward 架構雖支援 real-time inference，但對超出 modeled temporal window 的 long-term temporal dependency 與複雜 dynamic interaction 仍力有未逮。第三，在 extremely fast、non-rigid motion 場景下，由於運動模式高度不規則，模型表現會下降。第四，heavy motion blur 場景中，camera 或 object 快速移動會嚴重劣化視覺線索，導致 attention alignment 失效，連帶造成 depth 不準、pose 不穩、geometry 變形。第五，目前模型未顯式處理 occlusion 與長時間 appearance 大幅變化的情形，會在重建出的 4D 場景中產生 artifact 與 inconsistency。

整體而言，conclusion 的功能是壓縮性的、給工程讀者帶走兩個記憶點（attention-forcing、streaming refinement）；limitations 段則替後續工作畫出五條清晰的研究路線：mask-free supervision、long-horizon temporal modeling、fast/non-rigid motion、motion-blur robustness、occlusion 與 appearance change handling。

## 4. Critical Profile

### 4.1 Highlights

- 提出 attention-forcing 訓練策略,以 ground-truth motion mask 將「靜態先驗 motion score $a_i$」注入 camera token 對 image token 的 attention 分布,推論時完全 test-time-free,不需任何遮罩或額外輸入 (§3.2, p.4)。
- 在 Sintel 動態資料集的 camera pose estimation 上,full-attention 版 MoRe 將 ATE 從 VGGT 的 0.1715 降到 0.0877,接近減半;streaming 版 MoRe 也以 ATE 0.1474 領先所有 streaming 基線 (Table 1, p.6)。
- Streaming 變體在 Bonn 上 ATE 0.0211、在 Sintel 上 ATE 0.1474,皆優於 CUT3R、StreamVGGT、Wint3R、Stream3R 等同類方法,顯示 attention-forcing 策略在 streaming 模式下仍維持有效 (Table 1, p.6)。
- 設計 grouped causal attention,讓同幀內 image token 雙向互看、跨幀嚴格因果,並用 KV-cache 支援 streaming 推論;消融顯示 GCA 將 Sintel 的 $\delta < 1.25$ 從 0.592 提升至 0.637 (Table 4, p.8)。
- BA-like refinement 在序列處理完後,讓 cached camera queries 對全序列重新 attend 一次,模擬 bundle adjustment;消融顯示移除此步驟會使 Sintel ATE 從 0.147 升至 0.155 (Table 3, p.8)。
- Video depth estimation 上,MoRe(FA) 在 Sintel 取得 Abs Rel 0.335 / $\delta < 1.25$ 0.645,優於 VGGT 的 0.387 / 0.584,且在 KITTI、Bonn、TUM 多項指標皆達 streaming 類別最佳 (Table 2, p.8)。
- 在純靜態場景 Co3Dv2 上,MoRe 取得 RRA@30 99.49 / RTA@30 98.11 / AUC@30 91.42,超越 VGGT 與 $\pi^3$,顯示 motion-aware 設計不犧牲靜態場景的精度 (Table 6, p.14)。
- 推論速度在 KITTI 512×144 上達 30.09 FPS,優於 VGGT (7.32)、CUT3R (16.58)、Spann3R (13.55),屬最快一檔 (Table 5, p.13)。
- 提供完整的 motion mask 抽取 pipeline:結合 SAM2 語意分割、SEA-RAFT 光流與 ego-flow,以統計門檻 $d_k > \mu_d + 2\sigma_d$ 自動標註 motion mask,降低對人工標註的依賴 (§7.1, p.12)。
- 對 attention loss 的設計做了原則性比較:以 hinge-style 的 confidence-like loss $L_{\text{attn}} = \frac{1}{M}\sum \max(0, a_i - C) \cdot \alpha_i$ 取代 KL divergence,消融顯示 KL 變體在 Sintel ATE 0.185 vs. 本文 0.147 上明顯較差 (Table 7, p.15)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 高度依賴 motion mask 標註的品質,任何雜訊或不一致都會經訓練傳播,在無高品質遮罩的真實場景中受限 (§10, p.15)。
- Feed-forward 架構難以捕捉超出建模時間窗的長期時序依賴與複雜動態互動 (§10, p.15)。
- 在極端快速或非剛性運動下穩健性下降,attention alignment 變得不可靠 (§10, p.15)。
- 在嚴重 motion blur 場景下會失效,造成深度不準、姿態不穩或幾何扭曲 (§10, p.15)。
- 未明確處理遮擋與長時間外觀變化,可能導致重建中的 artifacts 與不一致 (§10, p.15)。

#### 4.2.2 Phyra-inferred

- 訓練監督本身仰賴自製 pipeline 產生的 motion mask (SAM2 + SEA-RAFT + 統計門檻),但論文未量化此 pseudo-label 的精確度,等於是用未驗證的偽標籤監督 attention,Sintel/Bonn 等資料集無 GT motion mask 時的監督品質完全未知 (§7.1, p.12 與 §10 相互掩蓋)。
- 「BA-like refinement」名實不符:Eq. (5) 只是讓 camera token 對 cached KV 再做一次 attention,沒有任何 reprojection、最小化或迭代,卻冠以 bundle adjustment 之名;消融僅帶來 Sintel ATE 0.155 → 0.147 的邊際改善 (Table 3),提升幅度與名稱所暗示的「全域最佳化」不相稱。
- 在 ScanNet 靜態資料集上,MoRe(FA) 的 ATE 0.0375、RPEtrans 0.0147 反而略遜於 VGGT 的 0.0347、0.0151 (Table 1),顯示 attention-forcing 並非全面 Pareto-improvement,在純靜態場景可能引入輕微退化,但內文僅以「comparable」一筆帶過。
- 與聲稱的 SOTA $\pi^3$ 在 Sintel/TUM/Bonn/ScanNet 主表 (Table 1) 中沒有並列比較,$\pi^3$ 只出現在補充材料 Co3Dv2 的單一表格 (Table 6),關鍵動態場景的直接對比被迴避。
- TUM-dynamics streaming 結果 ATE 0.0260 反而劣於 full-attention 的 0.0115,差距超過 2×,但內文未說明 streaming/grouped causal attention 在此資料集失效的原因 (Table 1)。
- Grouped causal attention 的消融 (Table 4) 只比較「GCA vs. 標準 causal attention」,未與雙向 full attention 相比,因此無法區分 GCA 的增益是來自「同幀雙向」還是「causal 結構本身」,核心設計貢獻的因果歸因不完整。
- 訓練資料含 Dynamic Replica、PointOdyssey、Spring、Virtual KITTI、TartanAir 等大量合成或半合成資料,評測集 Sintel 也來自合成片段,真實世界資料 (Bonn/TUM/ScanNet) 上的領先幅度顯著小於 Sintel,顯示部分增益可能由 sim-to-sim overlap 貢獻而非泛化能力 (§4 Datasets, p.7 對照 Table 1)。
- 訓練成本 (64×A800 GPU、約兩天、100K iterations,§6, p.12) 與「efficient」的標題定位形成反差,而論文在效率敘事中只報告推論 FPS,未討論訓練可重現性與門檻。

### 4.3 Phyra's Judgment (summary)

MoRe 的核心新意在於 attention-forcing:把「不該被信任的區域」以 soft prior 注入 camera token 的 attention 分布,並在推論時完全免除遮罩輸入,這個監督層的介入是邏輯上合理的「最小入侵」設計,實證上也對 Sintel 等動態場景帶來明顯增益。但 grouped causal attention 與 BA-like refinement 較偏 engineering integration,前者的因果歸因實驗不完整,後者名實不符且增益邊際。整體而言,論文真正回答的是「如何在 feed-forward 架構下用訓練監督替代測試時的運動先驗」,但未回答「motion mask pseudo-label 的品質下限為何」與「在強運動模糊、長時遮擋等極端條件下,attention-forcing 的失效模式」這兩個更根本的問題。

## 5. Methodology Deep Dive

### 5.1 Method Overview

MoRe 的整體方法建構在一個強大的靜態重建骨幹之上 (作者選擇 VGGT 作為基礎)，並透過兩項核心設計來解決動態場景下 4D 重建的兩大子問題：空間-運動解耦與時間-全域一致性。整體流程如 Figure 2 (page 3) 所示，模型輸入為單目影片序列 $\{I_t \in \mathbb{R}^{3 \times H \times W}\}_{t=1}^{T}$，每一幀經由 ViT Encoder 編碼為 image tokens，並與一個專屬的 camera token 串接後送入 transformer 主幹進行跨幀融合，最後由 Camera Head 與三個 DPT head 分別預測相機位姿 $g_t \in \mathbb{R}^9$、深度圖 $D_t$、點雲圖 $P_t$ 與動態遮罩 $M_t$。

第一個關鍵設計是 **Motion-aligned Attention (Sec. 3.2)**：作者觀察到 VGGT 等靜態 feed-forward 模型在動態場景中，camera token 的 attention 會均勻分布在整張影像 (Figure 3, page 4)，導致動態區域污染了應由靜態幾何主導的特徵聚合。為此，作者在訓練階段利用 ground-truth motion mask $M_t$ 將每個 image token 轉換為 motion score $a_i \in [0, 1]$，較高的 $a_i$ 對應靜態區域。此 score 透過 confidence-like loss $L_{attn}$ 監督 camera token 的 attention 權重 $\alpha_i$，迫使其避開動態區域。此設計完全 test-time-free，推論階段不需任何遮罩或額外輸入。

第二個關鍵設計是 **Grouped Causal Attention with BA-like Aggregation (Sec. 3.3)**：為支援串流推論，作者將傳統 LLM 風格的 upper-triangular causal mask 改寫為 frame-wise causal mask (Figure 4, page 5)，允許同幀內 image tokens 雙向互看以保持空間一致性，跨幀則嚴格因果以支援 KV-caching。然而嚴格 causal 會限制全域資訊交換，導致長序列下相機位姿漂移。因此作者額外設計了 BA-like aggregation：在序列處理完後，對 cached camera queries $Q_t^{cam}$ 重新做一次跨全序列的 attention (Eq. 5)，模擬 bundle adjustment 的全域優化步驟，得到 refined camera features $C_t^{opt}$。訓練時透過 duplicate camera token 的策略 (Sec. 3.4) 同時監督串流路徑與全域聚合路徑。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: 單目影片序列 {I_t}_{t=1}^T
   Shape: [B, T, 3, H, W]  (典型 H=W=518, 經 resize)
   │
   ▼
┌─────────────────────────────────────────────┐
│ ViT Encoder (per-frame, shared weights)      │
│  - Patchify, patch size s × s (s=14, DINOv2) │
│  - Output: image tokens per frame            │
└─────────────────────────────────────────────┘
   │  image tokens: [B, T, N, d]   where N = (H/s)·(W/s), d = embedding dim
   │
   ▼
┌─────────────────────────────────────────────┐
│ Camera Token Injection                       │
│  - 每幀附加一個 learnable camera token       │
└─────────────────────────────────────────────┘
   │  tokens: [B, T, N+1, d]
   │  ├─ camera token: [B, T, 1, d]
   │  └─ image tokens: [B, T, N, d]
   │
   ▼
┌─────────────────────────────────────────────┐
│ Aggregated Transformer (跨幀融合主幹)         │
│  訓練模式: full attention + Motion-aligned    │
│            Frame Attention (Sec. 3.2)         │
│  串流模式: Grouped Causal Attention (Sec.3.3)│
│  Layers: N_layer transformer blocks          │
└─────────────────────────────────────────────┘
   │  fused tokens: [B, T, N+1, d]
   │  ├─→ camera tokens: [B, T, 1, d]
   │  └─→ image tokens:  [B, T, N, d]
   │
   ├──────────────────┐
   │ (camera path)    │ (image path)
   ▼                  ▼
┌──────────────┐  ┌──────────────────────────┐
│ Camera Head  │  │ DPT Heads (×3, 共享 image│
│  MLP / 回歸  │  │  tokens 輸入)             │
│  預測 g_t∈R^9│  │  ├─ Depth DPT            │
└──────────────┘  │  ├─ Point map DPT        │
   │              │  └─ Motion mask DPT      │
   │              └──────────────────────────┘
   ▼                  │
 Poses               ├─→ Depth maps:    [B, T, H, W]
 [B, T, 9]           ├─→ Point maps:    [B, T, 3, H, W]
                     └─→ Motion masks:  [B, T, H, W]

(僅串流模式) BA-like Refinement (post-hoc, Eq. 5):
   cached Q^cam: [B, T, 1, d]  ←── 推論時保存
   全序列 KV:    [B, T, N+1, d]
   ▼
   C_t^opt = Attn(Q_t^cam, [K_{1:T}], [V_{1:T}])
   ▼
   refined camera features: [B, T, 1, d] → Camera Head → refined poses
```

註：上述 $d$ (transformer embedding 維度) 與 $N_{layer}$ 在論文中未明確指定，標記為 `?` 並於 §5.3 各模組的 Implementation Details 中說明。

### 5.3 Per-Module Breakdown

#### 5.3.1 ViT Encoder

**Function：** 將每一幀 RGB 影像獨立編碼為 patch-level image tokens，提供後續跨幀融合的視覺表示。

**Input：**
- Name: $I_t$
- Shape: $[B, T, 3, H, W]$，論文 Sec. 6 提到 $H$ 經 resize 使長邊為 518 像素，短邊隨機縮放 0.8–1.2 倍作 augmentation
- Source: 原始單目影片序列輸入

**Output：**
- Name: image tokens $F_t^{img}$
- Shape: $[B, T, N, d]$，其中 $N = (H/s) \cdot (W/s)$
- Consumer: Aggregated Transformer

**Processing：**
每一幀獨立通過 ViT Encoder (與 VGGT/DUSt3R 相同的 patchify + transformer block 結構)，輸出 patch tokens。論文未明確列出方程式。

**Key Formulas：** 無顯式公式 (沿用 VGGT backbone)。

**Implementation Details：**
基於 VGGT 預訓練骨幹 (Sec. 3 與 Sec. 4 提及"Built upon a strong static reconstruction backbone")。Patch size $s$ 與 embedding 維度 $d$ 論文未明確指定 (the paper does not specify)。訓練時長邊 resize 至 518 像素，短邊以 0.8–1.2 倍隨機縮放作為 data augmentation (Sec. 6)。

#### 5.3.2 Camera Token Injection

**Function：** 為每一幀附加一個 learnable camera token，作為相機位姿與全域幾何資訊的查詢載體。

**Input：**
- Name: image tokens $F_t^{img}$
- Shape: $[B, T, N, d]$
- Source: ViT Encoder

**Output：**
- Name: tokens (camera + image)
- Shape: $[B, T, N+1, d]$
- Consumer: Aggregated Transformer

**Processing：**
每一幀的 image tokens 前 (或後) 拼接一個共享的 learnable camera token (參數化為一個可學習向量 $\in \mathbb{R}^d$)，形成 $N+1$ 個 tokens 的序列。訓練時，為支援 §5.3.6 的雙路徑監督，camera token 會被 duplicate 並移到序列末端 (Sec. 3.4)。

**Key Formulas：** 無顯式公式。

**Implementation Details：**
Camera token 為 learnable parameter，初始化方式論文未明確指定。訓練時的 duplicate 策略詳見 §5.3.6。

#### 5.3.3 Aggregated Transformer with Motion-aligned Frame Attention

**Function：** 透過跨幀 attention 融合所有幀的 image tokens 與 camera tokens，並在訓練階段透過 attention forcing 將動態運動與靜態結構解耦。

**Input：**
- Name: tokens (camera + image)
- Shape: $[B, T, N+1, d]$
- Source: Camera Token Injection 後的拼接序列

**Output：**
- Name: fused tokens $\{F_t^{cam}, F_t^{img,fused}\}$
- Shape: camera tokens $[B, T, 1, d]$，image tokens $[B, T, N, d]$
- Consumer: Camera Head 與 DPT Heads

**Processing：**

(1) **Motion score 計算 (Eq. 3, page 4)：** 對 ground-truth motion mask $M_t$ 進行 patch-level pooling，得到每個 image token $i$ 的 motion score：

$$
a_i = 1 - \frac{1}{s^2} \sum_{(u,v) \in m_i} m_i(u, v)
$$

其中 $m_i$ 為第 $i$ 個 patch 對應的 mask token (大小 $s \times s$)，$a_i \in [0, 1]$，較高值對應靜態區域。

(2) **Attention forcing loss (Eq. 8, page 5)：** 將 camera token 對 image tokens 的 attention 權重 $\alpha_i$ 視為機率分布，使用 confidence-like loss 強迫 $\alpha_i$ 對齊 motion score：

$$
L_{attn} = \frac{1}{M} \sum_{i=1}^{M} \max(0, a_i - C) \cdot \alpha_i
$$

其中 $M$ 為 image tokens 數量、$C$ 為控制懲罰區域的常數。此 loss 鼓勵 camera token 在 $a_i$ 較低 (動態) 的位置減小 attention，從而避開動態干擾。

(3) **跨幀 attention：** 訓練模式為 full attention，串流模式則改用 Grouped Causal Attention (詳見 §5.3.4)。

**Key Formulas：**
$$
a_i = 1 - \frac{1}{s^2} \sum_{(u,v) \in m_i} m_i(u, v)
$$

$$
L_{attn} = \frac{1}{M} \sum_{i=1}^{M} \max(0, a_i - C) \cdot \alpha_i
$$

**Implementation Details：**
Transformer block 數量 $N_{layer}$、head 數、$d$ 維度論文未明確指定。常數 $C$ 的具體數值論文未明確指定。Motion mask 來源於作者提出的 SAM2 + SEA-RAFT pipeline (Sec. 7.1)。此 attention forcing 僅在訓練階段啟用，推論階段完全 test-time-free。

#### 5.3.4 Grouped Causal Attention (串流推論專用)

**Function：** 在串流推論時兼顧時間因果性與幀內空間一致性，並支援 KV-caching 以避免重複計算。

**Input：**
- Name: tokens 序列 (含 camera + image tokens)
- Shape: $[B, T, N+1, d]$ (邏輯上)，實際以 KV cache 增量傳入每幀 $[B, 1, N+1, d]$
- Source: 串流輸入幀經 ViT Encoder + Camera Token Injection

**Output：**
- Name: 每幀融合特徵 $F_t$
- Shape: $[B, 1, N+1, d]$ per step
- Consumer: Camera Head、DPT Heads，以及 BA-like Refinement 的 cached KV

**Processing：**

(1) **Frame-wise causal mask (Figure 4, page 5)：** 不同於傳統 upper-triangular mask，此設計允許同一幀內的 N+1 個 tokens 雙向互看，跨幀則嚴格因果。

(2) **KV cache 累積 (Eq. 4, page 4)：** 處理第 $t$ 幀時，使用累積的 KV 進行 attention：

$$
F_t = \text{Attn}(Q_t, [K_{1:t-1}, K_t], [V_{1:t-1}, V_t])
$$

$$
KV_{1:t} \leftarrow [KV_{1:t-1}; (K_t, V_t)]
$$

第一對影像對 (initial image pair) 用於初始化 KV cache。

**Key Formulas：**
$$
F_t = \text{Attn}(Q_t, [K_{1:t-1}, K_t], [V_{1:t-1}, V_t])
$$

**Implementation Details：**
論文 Sec. 4.3 ablation 中比較了 GCA 與標準 causal attention，後者使用 FlashAttention 實作。Sec. 8.1 提到 inference 採用 input/output streamer 雙佇列，並引入 window-sliding 策略避免 KV cache 無限增長 (window 大小論文未明確指定)。

#### 5.3.5 BA-like Token Aggregation (post-hoc refinement)

**Function：** 在串流推論完整序列處理完後，對 cached camera queries 重新做一次跨全序列 attention，模擬 bundle adjustment 的全域優化以修正長序列下的位姿漂移。

**Input：**
- Name: cached camera queries $Q_t^{cam}$ 與全序列 KV
- Shape: $Q^{cam} \in [B, T, 1, d]$，$K_{1:T}, V_{1:T} \in [B, T, N+1, d]$
- Source: 串流推論過程中保存的 camera queries 與所有幀的 KV features

**Output：**
- Name: refined camera features $C_t^{opt}$
- Shape: $[B, T, 1, d]$
- Consumer: Camera Head (產生 refined poses)

**Processing：**
對每個 frame $t$ 的 camera token，跨全序列 KV 做一次 attention：

$$
C_t^{opt} = \text{Attn}(Q_t^{cam}, [K_{1:T}], [V_{1:T}])
$$

此步驟類似 BA 中的全域優化，使每個相機位姿都能受惠於全序列的幾何資訊，緩解嚴格 causal 帶來的累積誤差。論文 Sec. 4.3 ablation (Tab. 3) 顯示移除此模組後 ATE/RPE 明顯上升，證實其有效性。

**Key Formulas：**
$$
C_t^{opt} = \text{Attn}(Q_t^{cam}, [K_{1:T}], [V_{1:T}])
$$

**Implementation Details：**
此為 post-processing step，僅執行一次跨全序列的 attention。論文 Figure 5 (page 5) 顯示此步驟以 duplicated camera tokens 形式並行執行。計算成本為 $O(T \cdot T \cdot (N+1))$，但因僅執行一次且 cam token 數遠小於 image tokens，整體開銷可控。

#### 5.3.6 Dual-path Camera Token Supervision (訓練專用)

**Function：** 訓練階段同時監督串流路徑 (causal) 與全域聚合路徑 (BA-like) 的 camera token，確保兩條路徑的相機預測一致。

**Input：**
- Name: 原始 camera token 與 duplicated camera token
- Shape: 各為 $[B, T, 1, d]$
- Source: Camera Token Injection (原始) + 在序列末端複製的 duplicate

**Output：**
- Name: 兩組 predicted poses $\{\hat{g}_t^{stream}, \hat{g}_t^{dup}\}$
- Shape: 各為 $[B, T, 9]$
- Consumer: Camera Loss (Eq. 9)

**Processing：**

(1) **Duplicate 策略 (Sec. 3.4)：** 訓練時對每幀的 camera token 複製一份並移至序列末端，原始 token 與 duplicated token 都被解碼為相機參數。

(2) **Camera loss (Eq. 9, page 6)：** 對所有 frame pair $(i, j), i \neq j$ 的相對變換 $S_{i \to j}$ (含旋轉 $R_{i \to j}$ 與平移 $t_{i \to j}$) 計算監督：

$$
L_{cam} = \frac{1}{T(T-1)} \sum_{i \neq j} \left( \theta_{\hat{R}_{i \to j}, R_{i \to j}} + \| \hat{t}_{i \to j} - t_{i \to j} \| \right)
$$

(3) **梯度策略：** 對原始 (causal) camera token，計算從早期幀到晚期幀的相對變換 loss 時，較早 timestamp 的 token 梯度被 detached，以避免 backprop 穿透整條時間鏈；對 duplicated token 則保留全部時間關係的梯度。

**Key Formulas：**
$$
L_{cam} = \frac{1}{T(T-1)} \sum_{i \neq j} \left( \theta_{\hat{R}_{i \to j}, R_{i \to j}} + \| \hat{t}_{i \to j} - t_{i \to j} \| \right)
$$

**Implementation Details：**
$\theta_{\hat{R}, R}$ 表示旋轉矩陣間的角度誤差 (具體形式論文未明確指定，常見為 $\arccos((\text{tr}(\hat{R}^T R) - 1)/2)$)。Detach 策略的具體實作細節論文未明確指定。

#### 5.3.7 Output Heads (Camera Head + DPT Heads)

**Function：** 將 transformer 輸出的 camera tokens 與 image tokens 解碼為最終的位姿、深度、點雲與動態遮罩預測。

**Input：**
- Name: fused tokens
- Shape: camera tokens $[B, T, 1, d]$，image tokens $[B, T, N, d]$
- Source: Aggregated Transformer / Grouped Causal Attention / BA-like Refinement

**Output：**
- Name: $\{g_t, D_t, P_t, M_t\}$
- Shape: $g_t \in [B, T, 9]$，$D_t \in [B, T, H, W]$，$P_t \in [B, T, 3, H, W]$，$M_t \in [B, T, H, W]$
- Consumer: 最終 4D 重建結果與訓練 loss

**Processing：**

(1) **Camera Head：** MLP 將 camera token 解碼為 9 維位姿向量 (旋轉 + 平移 + 內參，與 VGGT 一致)。

(2) **三個 DPT Heads：** 共享 image tokens 輸入，分別預測 dense depth maps、point maps 與 motion masks (Sec. 3 Method Overview)。

(3) **Confidence-weighted regression loss (Eq. 6, page 5)：** 對 depth 與 point map 同時預測值與置信度 $\hat{c}_i$：

$$
L_{conf} = \sum_{i=1}^{N} \left( \hat{c}_i \| \hat{y}_i - y_i \|_2^2 - \lambda \log(\hat{c}_i) \right)
$$

其中 $\hat{c}_i \in [1, \infty)$，鼓勵高置信區域有低誤差，並對置信度本身做正則化。

(4) **Motion mask 的 BCE loss (Eq. 7, page 5)：** 像素級二元交叉熵：

$$
L_{motion} = -\frac{1}{N} \sum_{i=1}^{N} \left[ M_i \log(\hat{M}_i) + (1 - M_i) \log(1 - \hat{M}_i) \right]
$$

**Key Formulas：**
$$
L_{conf} = \sum_{i=1}^{N} \left( \hat{c}_i \| \hat{y}_i - y_i \|_2^2 - \lambda \log(\hat{c}_i) \right)
$$

$$
L_{motion} = -\frac{1}{N} \sum_{i=1}^{N} \left[ M_i \log(\hat{M}_i) + (1 - M_i) \log(1 - \hat{M}_i) \right]
$$

**Implementation Details：**
$\lambda$ 的具體數值論文未明確指定。三個 DPT heads 的具體架構 (層數、通道) 論文未明確指定，沿用 VGGT/Dust3R 風格。最終總 loss 為 $L_{conf}^{depth} + L_{conf}^{point} + L_{motion} + L_{attn} + L_{cam}$ 的加權和，各項權重論文未明確指定。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage |
|---|---|---|---|
| Dynamic Replica [15] | 4D 動態場景訓練 | the paper does not specify | train |
| PointOdyssey [56] | 長時點追蹤合成資料 | the paper does not specify | train |
| Spring [23] | scene flow / optical flow / stereo | the paper does not specify | train |
| Virtual KITTI [4] | 駕駛場景合成 | the paper does not specify | train |
| TartanAir [42] | visual SLAM 多樣化合成資料 | the paper does not specify | train |
| Co3Dv2 [30] | 物件多視角 3D | the paper does not specify | train + test (§9.1 静態 pose) |
| ScanNet [5] | 室內靜態 RGB-D | the paper does not specify | train + test (静態 pose) |
| BlendedMVS [49] | 多視角 stereo | the paper does not specify | train |
| Hypersim [31] | 室內合成 photorealistic | the paper does not specify | train |
| ARKitScenes [1] | 行動 RGB-D 室內 | the paper does not specify | train |
| Waymo [35] | 自駕感知 | the paper does not specify | train |
| OmniWorld-Game [60] | 多領域多模態 4D | the paper does not specify | train |
| Sintel [3] | 動態合成（pose + depth） | the paper does not specify | test (zero-shot) |
| TUM-dynamics [33] | 真實動態 RGB-D SLAM | the paper does not specify | test (zero-shot) |
| Bonn [27] | 真實動態 RGB-D 重建 | the paper does not specify | test (zero-shot) |
| KITTI [12] | 駕駛場景深度估計 | the paper does not specify | test |
| DAVIS [28] | 影片物件分割 | the paper does not specify | test (motion mask 質性) |

備註：訓練時，序列數較少的資料集會依比例重複採樣以平衡分佈。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| ATE | Absolute Translation Error，pose 軌跡與 ground truth 經 Sim(3) 對齊後的絕對平移誤差 | yes |
| RPE$_{\text{trans}}$ | Relative Translation Error，相鄰幀之間的相對平移誤差 | yes |
| RPE$_{\text{rot}}$ | Relative Rotation Error，相鄰幀之間的相對旋轉誤差 | yes |
| Abs Rel | Absolute Relative Error，預測深度與 GT 深度的平均比例偏差，scale-only 對齊後計算 | yes |
| $\delta < 1.25$ | 預測深度落在 GT $\times 1.25$ 倍率以內的像素比例 | yes |
| RRA@30 | Relative Rotation Accuracy（門檻 30 度），用於 Co3Dv2 静態 pose | no |
| RTA@30 | Relative Translation Accuracy（門檻 30 度），用於 Co3Dv2 静態 pose | no |
| AUC@30 | 0–30 度門檻下 RRA/RTA 的曲線下面積 | no |
| FPS | KITTI 512×144 解析度下單卡 A800 的推論速度 | no |

### 6.3 Training and Inference Settings

- **Optimizer**：AdamW [21]。
- **Schedule**：含 warm-up 階段，peak learning rate $1 \times 10^{-6}$。
- **Iterations**：100K iterations。
- **Sampling**：每個 iteration 從每段序列隨機抽取 2–24 frames，temporal interval 1–5。
- **Resolution**：較長邊固定為 518 px，較短邊以 0.8–1.2 倍隨機縮放作為 data augmentation。
- **Hardware**：64 張 NVIDIA A800 GPU，訓練約兩天。
- **Precision / memory**：採用 bfloat16 與 gradient checkpointing。
- **Batch size**：the paper does not specify。
- **Streaming inference**：使用 image-wise KV caching，並可加入 sliding window（消融中採 window=5）；效率測試在 KITTI 512×144 解析度、單張 A800 GPU 上量測。
- **Pose 對齊**：所有 pose 指標經 Sim(3) 對齊；depth 指標採 scale-only 對齊。

### 6.4 Main Results

Camera Pose Estimation（ATE / RPE$_{\text{trans}}$ / RPE$_{\text{rot}}$，數值取自 Tab. 1，僅列示 Sintel 與 Bonn 兩個動態基準作為摘要）：

| Method | Type | Sintel ATE | Sintel RPE$_t$ | Sintel RPE$_r$ | Bonn ATE | Bonn RPE$_t$ | Bonn RPE$_r$ | Notes |
|---|---|---|---|---|---|---|---|---|
| MapAnything [16] | FA | 0.2104 | 0.0919 | 2.7396 | 0.0248 | 0.0132 | 0.6927 | 全注意力 baseline |
| VGGT [39] | FA | 0.1715 | 0.0617 | 0.4695 | 0.0141 | 0.0100 | 0.6323 | 上一代 FA SoTA |
| **MoRe (FA)** | **FA** | **0.0877** | **0.0580** | **0.3899** | **0.0138** | **0.0099** | **0.6267** | **本文 FA 變體** |
| Spann3R [38] | Streaming | 0.3313 | 0.1111 | 4.4952 | 0.0344 | 0.0212 | 2.2539 | streaming baseline |
| CUT3R [40] | Streaming | 0.2163 | 0.0756 | 0.6518 | 0.0420 | 0.0094 | 0.6825 | persistent latent |
| StreamVGGT [61] | Streaming | 0.4159 | 0.1097 | 1.1056 | 0.0451 | 0.0148 | 0.5982 | – |
| Wint3R [20] | Streaming | 0.2251 | 0.0972 | 1.0922 | 0.0366 | 0.0084 | 0.7170 | window-based |
| Stream3R [17] | Streaming | 0.2144 | 0.0764 | 0.8674 | 0.0235 | 0.0108 | 0.6664 | LLM-style causal |
| **MoRe** | **Streaming** | **0.1474** | 0.0776 | **0.6157** | **0.0211** | 0.0117 | **0.6496** | **本文 streaming 主模型** |

Video Depth Estimation（Abs Rel / $\delta<1.25$，取自 Tab. 2）：

| Method | Type | Sintel Abs Rel | Sintel $\delta$ | Bonn Abs Rel | Bonn $\delta$ | KITTI Abs Rel | KITTI $\delta$ |
|---|---|---|---|---|---|---|---|
| VGGT [39] | FA | 0.387 | 0.584 | 0.055 | 0.970 | 0.073 | 0.961 |
| **MoRe (FA)** | **FA** | **0.335** | **0.645** | **0.055** | **0.971** | **0.066** | **0.967** |
| Stream3R [17] | Streaming | 0.397 | 0.632 | 0.070 | 0.952 | 0.079 | 0.949 |
| **MoRe** | **Streaming** | **0.254** | **0.637** | 0.068 | **0.961** | **0.072** | **0.966** |

Co3Dv2 静態 pose（取自 Tab. 6，AUC@30 為主要彙總指標）：

| Method | RRA@30 | RTA@30 | AUC@30 |
|---|---|---|---|
| VGGT [39] | 98.96 | 97.13 | 88.59 |
| $\pi^3$ [44] | 99.05 | 97.33 | 88.41 |
| **MoRe** | **99.49** | **98.11** | **91.42** |

效率（KITTI 512×144，單張 A800，取自 Tab. 5）：

| Method | FPS |
|---|---|
| VGGT [39] | 7.32 |
| Spann3R [38] (224×224) | 13.55 |
| CUT3R [40] | 16.58 |
| Stream3R$_\alpha$ [17] | 23.48 |
| Stream3R$_\beta$ [17] | 12.95 |
| Stream3R$_\beta$-W[5] [17] | 32.93 |
| **MoRe** | **30.09** |

論文亦聲稱 FA 變體與資料量更大的 SoTA $\pi^3$ [44] 表現相當（main text §4.1）。

### 6.5 Ablation Studies

論文於 Tab. 3、Tab. 4、Tab. 7 給出三組消融，全部使用相同訓練 schedule 與資料配置：

- **Attention forcing（Tab. 3，Sintel + TUM-dynamics）**：移除 attention forcing 後 Sintel ATE 由 0.147 升至 0.163、RPE$_{\text{rot}}$ 由 0.616 升至 0.660；TUM-dynamics ATE 由 0.026 升至 0.028。此消融直接針對「attention 是否能將動態與静態分離」這一核心宣稱，屬於 diagnostic ablation。
- **BA-like refinement（Tab. 3）**：拿掉 duplicated camera tokens 構成的後處理 refinement 後，Sintel ATE 由 0.147 升至 0.155、RPE$_{\text{trans}}$ 由 0.082 升至 0.085；改善幅度小於 attention forcing，顯示 refinement 主要扮演串流序列的全局一致性修正角色，仍具診斷意義但效應較弱。
- **Grouped Causal Attention vs. 標準 causal（Tab. 4，Sintel/Bonn/KITTI）**：以 FlashAttention 實作的 vanilla causal 為對照，Sintel Abs Rel 由 0.277 降至 0.254、$\delta<1.25$ 由 0.592 升至 0.637；其餘資料集亦一致改善。論文以多基準確認「frame 內雙向 + frame 間 causal」的設計貢獻，屬有效 diagnostic。
- **Loss design for attention alignment（Tab. 7，supplementary §9.3）**：以 KL-based alignment 取代 $L_\text{attn} = \frac{1}{M}\sum_i \max(0, a_i - C)\cdot\alpha_i$，Sintel ATE 由 0.147 退步到 0.185、RPE$_{\text{rot}}$ 由 0.616 退步到 0.707。此消融直接驗證「不要把 attention 強制 normalize 為機率分佈」的設計動機，屬針對 motion-gated formulation 的關鍵 diagnostic。

整體看，四組消融皆瞄準論文新提出的元件（attention forcing、grouped causal attention、BA-like refinement、motion-gated loss），不像單純 sanity check；惟論文未提供逐元件「同時關閉多個」的累加式消融、亦未在多個 seed 下重跑，所以無法判斷單次數值差是否在隨機波動範圍內。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 主表同時納入 FA 類的 VGGT [39]、MapAnything [16] 與 supplementary 中與 SoTA $\pi^3$ [44] 的 Co3Dv2 對比。
- [covered] Has cross-task / cross-dataset evaluation — 同時涵蓋 pose（Sintel/TUM/Bonn/ScanNet/Co3Dv2）、depth（Sintel/Bonn/TUM/KITTI）與 motion mask（DAVIS）共三類任務。
- [covered] Has ablations that diagnose the new components — Tab. 3/4/7 分別針對 attention forcing、grouped causal attention、BA-like refinement 與 motion-gated loss，皆對應論文新設計。
- [missing] Has a scaling study — 論文僅提到「資料量較 $\pi^3$ 少卻仍可比」，但未提供模型參數量、序列長度或計算量對性能的曲線研究。
- [covered] Has an efficiency / wall-clock comparison — Tab. 5 在 KITTI 512×144、A800 單卡上比較 FPS，並含 sliding window 變體。
- [missing] Reports variance / standard deviation / multiple seeds — 所有表格僅報單一數值，未見多 seed 或誤差棒。
- [partial] Releases code / weights / data sufficient for reproducibility — 提供 project page (`https://hellexf.github.io/MoRe/`)，但摘錄文字未明確列出 code / weights / 訓練資料清單的開源狀態。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 提出 attention-forcing,用訓練監督讓模型解耦動態與靜態,推論完全 test-time-free。** Supported。Table 3 的消融顯示移除 attention forcing 後 Sintel ATE 從 0.147 升至 0.163、TUM ATE 從 0.026 升至 0.028,Fig. 10 (p.14) 也視覺化呈現 attention 從動態物體上被抑制的對比,主張成立。
- **Claim 2: Grouped causal attention 同時維持空間一致性與時間因果,提升 streaming 重建。** Partially supported。Table 4 顯示 GCA 對 Sintel/Bonn/KITTI 的 depth 指標有穩定提升 (Sintel $\delta < 1.25$ 0.592 → 0.637),但 baseline 僅為「標準 causal attention」,缺少與雙向 full attention 的對照,因此「causal + 同幀雙向」這個組合相對於「直接用 full attention 截斷上下文」的優勢未被獨立驗證。
- **Claim 3: BA-like 全域聚合提供 bundle adjustment 風格的全域一致性。** Overclaimed。Eq. (5) 的實作只是 cached camera queries 對全序列 KV 重新 attend 一次,沒有最小化重投影誤差、無迭代、無顯式幾何約束,稱不上 bundle adjustment;Table 3 的增益 (Sintel ATE 0.155 → 0.147) 也偏邊際,與「全域最佳化」這個強標籤不相稱。
- **Claim 4: 在多基準上達 SOTA 並具強泛化。** Partially supported。Streaming 類別在 Sintel/Bonn 確實領先 (Table 1, 2);但與聲稱的 SOTA $\pi^3$ 在 Sintel/TUM/Bonn/ScanNet 主表完全沒有同表比較,僅在補充 Co3Dv2 (Table 6) 上對比;ScanNet 上 MoRe(FA) ATE 0.0375 略遜於 VGGT 的 0.0347,顯示「全面領先」的敘事過強。
- **Claim 5: 高效率、適合 real-time streaming。** Supported。Table 5 顯示 30.09 FPS,優於 VGGT/CUT3R/Spann3R/Stream3R$\beta$,加上 KV-cache 與 sliding window 設計,主張在推論端成立 (但訓練成本未在 efficiency 敘事中揭露)。

### 7.2 Fundamental Limitations of the Method

**Pseudo-label 監督的封閉迴圈。** Attention-forcing 仰賴 motion score $a_i$,但 $a_i$ 由 SAM2 的語意分割與 SEA-RAFT 的光流以統計門檻自動產生 (§7.1)。這意味著模型「不該注意的區域」是由另一組視覺基礎模型定義的,而非真實的物理運動。當 SAM2 分割破碎或 SEA-RAFT 在低紋理/重運動下失效時,錯誤的 pseudo-label 會直接以 $L_{\text{attn}}$ 形式被學進 attention,且因 inference 時無校正機制,錯誤無法回流修正。論文未提供 pseudo-label 與 GT motion mask 的一致性數據,這個監督源的品質下限完全未驗證。

**「BA-like」缺少 BA 的核心要素。** Bundle adjustment 的本質是對重投影誤差做非線性最小化、迭代收斂,並以 Jacobian 結構耦合相機與點。Eq. (5) 中 $C_t^{\text{opt}} = \text{Attn}(Q_t^{\text{cam}}, [K_{1:T}], [V_{1:T}])$ 只是一次前饋的 attention pass,沒有任何最小化目標、沒有迭代、沒有點–姿態耦合。它能做的只是讓 camera token 看見「未來幀的特徵」,本質上更接近 post-hoc bidirectional attention,而非全域最佳化。這個架構限制決定了 long-sequence drift 仍無法被根本壓制,只能在訓練分布內被 attention pattern 隱式吸收。

**Streaming 與 full-attention 的不可調和差距。** Table 1 顯示 TUM-dynamics 上 streaming 版 ATE 0.0260,是 full-attention 版 0.0115 的 2.26 倍。這個差距不是訓練不足,而是嚴格 causal mask 在強相機抖動 + 動態物體共現的場景下,前幾幀缺乏未來資訊去校正初始姿態,後續 BA-like refinement 又只是一次 attention pass,無法回頭重估早期 token 的隱藏狀態。此限制是 causal 架構本身的結構性缺陷。

**Motion-aware 設計與靜態 SOTA 的潛在 trade-off。** ScanNet 上 MoRe(FA) 的 ATE/RPEtrans 略遜於 VGGT (Table 1),顯示對 attention 加上 motion-prior 監督即使在沒有運動的場景仍會留下印記。這暗示 attention-forcing 不是「對動態場景加分、對靜態場景無害」的純改進,而是調整了 attention 的歸納偏置,在純靜態 benchmark 上是有代價的。Co3Dv2 上的領先 (Table 6) 與 ScanNet 上的小幅落後並存,顯示靜態場景內的優劣會隨資料集分布而異。

### 7.3 Citations Worth Tracking

- **VGGT [39] (Wang et al., CVPR 2025)** — MoRe 的 backbone 與 attention 行為對照組;Fig. 3 的失效分析直接以 VGGT 為案例,理解 VGGT 的 camera token 設計是讀懂 attention-forcing 動機的前提。
- **CUT3R [40] (Wang et al., CVPR 2025)** — 唯一一個使用 transformer persistent latent state 做 online dense reconstruction 的 streaming 基線,是 MoRe 在 streaming 設計選擇上的主要對手,值得對比兩者對「長序列狀態維護」的不同假設。
- **$\pi^3$ [44] (Wang et al., 2025)** — 內文宣稱「comparable to SOTA $\pi^3$」但只在 Co3Dv2 上對比;讀此論文可獨立判斷 MoRe 在動態場景的領先是否真的超越 $\pi^3$。
- **MapAnything [16] (Keetha et al., 2025)** — full-attention feed-forward 重建的代表,Table 1/2 的主要 FA 對照;了解其 universal metric 3D reconstruction 框架有助於評估 MoRe(FA) 的相對定位。
- **Stream3R [17] (Lan et al., 2025)** — streaming 4D reconstruction 的 LLM-style causal transformer 代表,提供 sliding-window KV-cache 的設計參考;Table 5 中 Stream3R$\beta$-W[5] 達 32.93 FPS 略快於 MoRe,值得理解其與 MoRe 在效率/品質 trade-off 上的差異。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] Motion mask pseudo-label pipeline (SAM2 + SEA-RAFT + 統計門檻) 對 GT motion mask 的 IoU/Dice 是多少?在哪些場景會系統性失效並把錯誤監督進 attention?
- [ ] 為何 streaming 版在 TUM-dynamics 上 ATE 是 full-attention 版的 2.26 倍 (Table 1),而在 Sintel 上差距較小?這個 gap 是來自 causal mask 結構本身,還是 BA-like refinement 的能力上限?
- [ ] Grouped causal attention 對比「截斷上下文的 full attention」(而非標準 causal attention) 的增益是多少?「同幀雙向」與「causal 結構」這兩個設計各貢獻多少?
- [ ] Attention-forcing 在 ScanNet 等純靜態場景上略劣於 VGGT (Table 1),這個 trade-off 是否與訓練資料中動態/靜態樣本的混合比例有關?可否透過調整 $C$ 或 loss 權重消除?
- [ ] BA-like refinement 是否真正修正了「漂移」?若針對序列長度 (例如 50/100/200 frames) 做 ATE 退化曲線,refinement 的效益會隨長度單調增加嗎?
- [ ] 論文聲稱「comparable to $\pi^3$」但僅在 Co3Dv2 對比,在 Sintel/TUM/Bonn 等動態 benchmark 上 MoRe vs. $\pi^3$ 的數字實際為何?
- [ ] 訓練在 64×A800 上跑兩天 (§6),是否有資料效率分析 (例如僅用一半資料的退化曲線),以判斷是否大量算力是達成這些指標的必要條件?

### 8.2 Improvement Directions

1. **量化並公開 motion mask pseudo-label 的品質**(可行性最高)。在有 GT motion mask 的子集 (例如 Dynamic Replica、Sintel) 上計算 SAM2 + SEA-RAFT pipeline 的 IoU/precision/recall,並做「pseudo-label 噪聲水準 vs. 下游 ATE」的退化曲線。理由:這是論文最大的隱性風險點,實作成本低且能直接界定 attention-forcing 的監督上限。
2. **將「BA-like refinement」改為真正的可微分 BA layer**。把 cached camera queries 與 point map 共同輸入一個輕量的 Gauss-Newton 迭代模組,以 reprojection loss 做數步最小化。理由:目前的單次 attention pass 缺少「殘差→更新」的回授結構,這正是 long-sequence drift 無法根本壓制的原因;若加入即使 2–3 步的迭代,長序列 ATE 應該能進一步下降。
3. **補上「同幀雙向」與「causal 結構」的獨立消融**。設計三組對照:full attention (no causality)、純 causal、grouped causal,以分離兩個設計維度的貢獻。理由:目前 Table 4 的 GCA vs. causal 比較會把所有增益都歸給 GCA,但其中可能有相當部分來自任何一種「同幀雙向」設計。
4. **針對 streaming 版設計「lookback refinement」**。在 BA-like step 中,允許早期 frame 的 hidden state 也被重新更新 (而非只更新 camera token),例如以小步數的 cross-attention 反向傳遞未來幀資訊。理由:streaming 在 TUM-dynamics 上的大幅退化 (vs. FA) 顯示初始幀缺乏未來上下文是核心瓶頸,光更新 camera token 不足以彌合。
5. **以 self-supervised motion cue 取代 pseudo-label 監督**。用 photometric consistency / cycle-consistency 等自監督訊號取代 SAM2 + SEA-RAFT 產生的 mask,直接在訓練中端到端學 motion score。理由:可解除論文 §10 自承的「heavy dependence on motion mask quality」這個根本限制,但實作成本高、收斂風險高,故排序最後。
