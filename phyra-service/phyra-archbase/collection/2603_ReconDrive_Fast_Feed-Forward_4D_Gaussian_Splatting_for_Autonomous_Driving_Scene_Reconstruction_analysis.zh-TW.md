<!-- type: paper-read-notes | generated: 2026-05-08 | lang: zh-TW -->

# ReconDrive — ReconDrive: Fast Feed-Forward 4D Gaussian Splatting for Autonomous Driving Scene Reconstruction

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | ReconDrive |
| Paper full title | ReconDrive: Fast Feed-Forward 4D Gaussian Splatting for Autonomous Driving Scene Reconstruction |
| arXiv ID | 2603.07552 |
| Release date | 2026-03-08 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.07552 |
| PDF link | https://arxiv.org/pdf/2603.07552v1 |
| Code link | https://github.com/TuojingAI/ReconDrive |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Haibao Yu | Tuojing Intelligence; The University of Hong Kong | https://github.com/haibao-yu | first author; equal contribution; corresponding author |
| Kuntao Xiao | Tuojing Intelligence | — | equal contribution |
| Jiahang Wang | Tuojing Intelligence | — | co-author |
| Ruiyang Hao | King's College London; Tuojing Intelligence | — | co-author |
| Yuxin Huang | The University of Sydney; Tuojing Intelligence | — | co-author |
| Guoran Hu | Mohamed bin Zayed University of Artificial Intelligence; Tuojing Intelligence | — | co-author |
| Haifang Qin | Tuojing Intelligence | — | co-author |
| Bowen Jing | Tuojing Intelligence | — | co-author |
| Yuntian Bo | Tuojing Intelligence | — | co-author |
| Ping Luo | The University of Hong Kong | http://luoping.me | senior author |

### 1.2 Keywords

4D Gaussian Splatting, feed-forward reconstruction, autonomous driving, novel-view synthesis, VGGT, 3D foundation model, static-dynamic decomposition, LoRA fine-tuning

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al. 2025) | base model | 提供 3D foundation backbone(DINOv2+Alternating-Attention),作為 ReconDrive 的特徵主幹並以 LoRA 微調。 |
| 4DGS (Wu et al. 2024) | predecessor | 在 3DGS 上加入時間維度,是本文選用的核心場景表示形式。 |
| 3DGS (Kerbl et al. 2023) | influence | 高斯潑濺渲染的基礎方法,提供顯式幾何與即時渲染框架。 |
| Street Gaussians (Yan et al. 2024) | baseline | 代表性 per-scene 最佳化路線,本文以其作為自駕場景重建主要對比基線。 |
| STORM (Yang et al. 2025) | baseline | 以 Transformer 生成逐幀 Gaussian 的 feed-forward 方法,是同類前饋基線。 |
| SAM2 (Ravi et al. 2024) | base model | 用於萃取動態交通參與者的 instance mask,支撐 static-dynamic 分解。 |
| LoRA (Hu et al. 2022) | influence | 提供 parameter-efficient fine-tuning,將凍結的 VGGT 適配至駕駛域。 |

## 2. Research Overview

### 2.1 Research Topic

本研究關注自駕車閉環模擬所需的城市場景視覺重建與新視角合成。傳統 4D Gaussian Splatting (4DGS) 雖能兼顧幾何精度與即時渲染,但多採 per-scene 最佳化,需要 LiDAR 先驗並耗費大量算力,難以擴展到大規模都市環境;既有 feed-forward 方法雖速度快,卻在 photometric 品質上明顯落後。作者提出 ReconDrive,以 VGGT 等 3D foundation model 為骨幹,設計一個僅以多視角影像為輸入即可一次前饋產生 4D Gaussians 的框架,聚焦於提高動態場景表達能力、外觀保真度與相機標定一致性,並在 nuScenes 上同時評估場景重建、新視角合成與 3D 物件偵測/追蹤等下游任務。

### 2.2 Domain Tags

- Computer Vision
- Autonomous Driving
- 3D/4D Scene Reconstruction
- Novel-View Synthesis

### 2.3 Core Architectures Used

- **VGGT backbone (Wang et al. 2025)**:作為 3D foundation model 的特徵主幹,以 DINOv2 token 化與 24 層 Alternating-Attention 提取跨視角與時序的幾何一致 feature,在本文中以凍結權重 + LoRA 適配駕駛域。
- **DINOv2 encoder (Oquab et al. 2023)**:VGGT 的影像 tokenizer,以 patch size $p = 14$ 將降採樣後影像轉成 $d = 1024$ 的 dense token,作為後續 alternating attention 的輸入。
- **DPT head (Ranftl et al. 2021)**:Dense Prediction Head,將融合後的 transformer feature 上採樣回原始解析度,作為 GCPH 與 GPPH 的共用上採樣骨幹。
- **Hybrid Gaussian Prediction Heads (本文提出)**:由 GCPH 與 GPPH 雙路組成,GCPH 透過 depth + 相機內外參投影產生 Gaussian 中心,GPPH 以 raw image 與 dense feature 串接的 shortcut 回歸 opacity、scale、rotation、spherical harmonics 等外觀屬性。
- **Static-Dynamic 4D Composition (本文提出)**:以 SAM2 mask 區分靜態背景與動態交通參與者,對動態 Gaussian 以 $\mu_i(t) = \mu_{i,\text{init}} + v_i \cdot (t - T_s)$ 的 center-moving 線性運動模型表達時間維度。
- **SAM2 (Ravi et al. 2024)**:foundation segmentation model,用於從 context frame 萃取車輛、行人等 instance mask,提供動態分解所需的 pixel-wise 對應。
- **LoRA (Hu et al. 2022)**:parameter-efficient fine-tuning,以 rank $r = 8$、scaling factor $\alpha = 32$ 將凍結的 VGGT 適配到自駕資料分佈而不破壞通用幾何先驗。
- **Segment-wise Temporal Fusion (本文提出)**:將長序列切成 $\{[T_s, T_{s+1}]\}$ 區段,在每個區段內以兩個 context frame 產生 Gaussian,再透過 ego-pose 變換與速度場對齊融合成統一 4D 表示。
- **VGG-19 perceptual network (Simonyan & Zisserman 2014)**:訓練階段提供 perceptual loss 的高階 feature 抽取器,以 $L_1$ 距離鼓勵渲染影像與真實影像的感知一致性。
- **4D Gaussian Splatting (Wu et al. 2024) / 3DGS (Kerbl et al. 2023)**:本文採用的顯式場景表示,每個 Gaussian 以 $(\mu_i(t), R_i, s_i, \alpha_i, c_i)$ 描述位置、旋轉、各向異性尺度、不透明度與球諧色彩係數。

### 2.4 Core Argument

作者主張既有 feed-forward 4DGS 方法的限制可歸因於三個根因:(1) Photometric Deficiency:VGGT 之類 foundation feature 為了結構一致性而設計,缺乏高頻紋理細節,直接從骨幹 feature 回歸所有 Gaussian 屬性會犧牲外觀品質;(2) Temporal Staticity:多視角 foundation model 的隱含假設是靜態場景,無法明確表達車輛、行人等交通參與者的運動;(3) Domain & Calibration Mismatch:預訓練於通用資料的 3D foundation model 未利用駕駛資料天然具備的相機內外參標定,造成幾何錯位。基於這三個根因,作者的解法在邏輯上是必要的:Hybrid Gaussian Prediction Heads 將空間中心 (GCPH) 與外觀屬性 (GPPH) 分離回歸,GPPH 透過 shortcut 將原圖與 dense feature 串接以補回高頻紋理,GCPH 則顯式注入相機標定以鎖定 ego 座標,直接回應 (1) 與 (3);Static-Dynamic 4D Composition 透過 SAM2 mask 與兩幀位移計算速度向量,以「中心移動」式 Gaussian 顯式建模動態,回應 (2);Segment-wise Temporal Fusion 與 LoRA 微調則讓凍結的 VGGT 能擴展到長序列且不破壞通用幾何先驗。三項設計分別對應三個根因,構成從觀察到方法的閉合論證。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(250 words)

標題 "ReconDrive: Fast Feed-Forward 4D Gaussian Splatting for Autonomous Driving Scene Reconstruction" 已在三個關鍵詞上鎖定全篇定位：fast feed-forward 對應推論時間、4D Gaussian Splatting 對應表徵選擇、autonomous driving 對應應用域。Abstract 沿著「動機 — 缺口 — 方法 — 結果」四段式展開，先說明 closed-loop evaluation 需要 high-fidelity visual reconstruction 與 novel-view synthesis；接著指出 4DGS 雖在精度與效率間取得平衡，但 per-scene optimization 因 iterative refinement 而不可規模化，現有 feed-forward 方法則 photometric quality 不足，定義出本文要填補的缺口。

方法陳述聚焦在兩項 core adaptations：(1) Hybrid Gaussian Prediction Heads 將 spatial coordinates 與 appearance attributes 的 regression 解耦，以解決 generalized foundation features 的 photometric deficiency；(2) Static-Dynamic 4D Composition 透過 velocity modeling 顯式刻畫 temporal motion，以表達動態交通環境。Abstract 強調本框架是建構在 3D foundation model VGGT 之上，把整體故事鎖在「擴充 VGGT 而非從零起家」這條敘事線。

結果陳述以 nuScenes 為唯一 benchmark，跨 reconstruction、synthesis、3D perception 三類任務作評估，宣稱 ReconDrive 全面超越所有 feed-forward baselines，且在 nine 個 evaluation metrics 中於 eight 項勝過 per-scene optimization 方法。Abstract 最後以「superior quality with substantially fewer resources」作為價值定錨，並把 scalability 與 simulation 寫入收尾，使讀者直接連結到 §1 將要展開的閉環模擬動機。整段 abstract 並未提及具體 PSNR 或秒數，避免細節稀釋核心 claim，把數字延後到 §4 才出現，刻意把首頁節奏控制在 high-level positioning。

### 3.2 Introduction

(750 words)

Introduction 從 closed-loop evaluation 的需求切入，把 end-to-end 自駕系統需要與 simulated environment 互動的事實當作第一塊基石；接著把現有路徑歸納為三類：CARLA 等遊戲引擎的 asset importation、NeRF 或 video diffusion 的 implicit representation、以及 explicit geometric modeling，並把 4DGS 定位為「balance geometric accuracy, photometric fidelity, real-time rendering」的 ideal 選擇，建立論述軸線。

第二段把矛頭指向 traditional 4DGS 的 per-scene optimization，舉 Street Gaussians 為代表，指出此 paradigm 仰賴 LiDAR priors、無法跨場景共享結構知識、每個新環境都產生重複計算。隨後對照 feed-forward 模型 VGGT，承認其在直接產出 explicit geometry 上的潛力，並順勢把「擴充 VGGT 至 4D」鎖定為敘事重心。三項 challenges 在此被點名：photometric deficiency（VGGT 特徵不足以回歸高保真外觀）、temporal staticity（static backbone 無法表達 dynamic motion）、domain and calibration mismatch（無法善用 driving dataset 的 pre-calibrated 內外參），這三點直接對應後文方法章節要逐一回應的設計動機。

第三段宣告 ReconDrive 的整體立場：以 vision-only 輸入、pre-trained VGGT-style backbone、直接 regress spatio-temporal Gaussian parameters。隨後以三個 design pillars 構築方法骨架：第一是 hybrid Gaussian prediction heads，把 raw image 與 dense pixel-wise features 串接以提供 photometric cues，並將 calibration 直接注入 centers head；第二是 static-dynamic 4D composition，借助 SAM2 取得 object masks，再透過 pixel-wise correspondence 賦予 dynamic Gaussians 速度；第三是 segment-wise temporal fusion，把長序列切段以處理 view sparsity。Fig. 1 在此被引用為 inference pipeline 的視覺索引，並補充訓練時凍結 VGGT 權重、以 LoRA fine-tune、以及引入 novel-frame projection loss 的細節。

第四段轉向實驗鋪陳，宣告作者在 nuScenes 上重現五個代表性 baselines、建立統一 benchmark，並在 reconstruction、novel-view synthesis、3D detection/tracking 三項上比較。此段的核心訊息是「八項超越 per-scene optimization、九項通通超越 feed-forward」，把 contribution 數字化，與 abstract 對齊。

最後以三條 bullet 收束 contributions：(1) 提出 feed-forward 的 4DGS 框架，免除 per-scene optimization 並涵蓋 cross-time novel-view synthesis；(2) 引入 hybrid prediction heads、static-dynamic composition、segment-wise fusion，並搭配 specialized training 把 3D foundation models 帶入 dynamic urban 場景；(3) 在 nuScenes 上建立 reproducing baselines 的 benchmark，並在多項 protocols 上達到 SOTA。Introduction 的鋪陳節奏明確：閉環需求 → 4DGS 為何適合 → 既有方法兩條失敗路線 → 三項 challenges → 三項 design pillars → benchmark 與 contributions，使讀者對 §2 將要對照哪些 baselines、§3 要逐一回應哪三條 challenge 都已預先 framed，承上啟下的功能完整。

### 3.3 Related Work / Preliminaries

(520 words)

Related Work 拆成兩個子題：Feed-Forward 3D and 4D Reconstruction，以及 Gaussian Splatting for Autonomous Driving Scene Reconstruction，分別對應「方法骨架的家系」與「應用域的家系」，這個切法使後文方法章節能在兩條 pedigree 上同時宣告貢獻。

第一子題從 DUSt3R 與 VGGT 出發，把 feed-forward 路線定位為「bypass traditional optimization、直接預測 3D point clouds 與 depth maps」的 paradigm；緊接著援引 FastVGGT 的 region-based random sampling 來代表效率改進，再以 Depth Anything V3、SAM3D 點到 generalizable 3D scene understanding 的最新進展。第二段把 paradigm 從 point clouds 推進到 Gaussian Splatting：MVSplat、AnySplat 是靜態場景的代表；StreamVGGT 引入 memory cache 與 temporal causal attention 來涵蓋 streaming 動態；DriveVGGT 則把 VGGT backbone 套入 scale-aware framework 以處理駕駛資料。本段最後一句點出 ReconDrive 的差異點：把焦點從 static geometric design 轉到 enhancing dynamic scene representation 與 novel-view fidelity，以「在 VGGT 公式上專為自駕複雜性適配」這條 framing 替後文 hybrid heads 與 static-dynamic composition 預埋伏筆。

第二子題從 per-scene optimization 路線切入。AutoSplat 以幾何約束強化高保真重建，PVG 引入 periodic vibration Gaussians 處理動態都市場景，StreetGaussians 把場景拆成 static backgrounds 與 moving vehicles，DrivingGaussian 引入 dynamic Gaussian graph，S3Gaussian 則用 spatial-temporal field network 建模 4D 動態。作者刻意以「需要每個場景數小時計算」的論點把這條路線整體框為 unscalable，與 introduction 對應。隨後轉到 feed-forward 子家族：DrivingForward 透過 interpolation 重建相鄰 frames，STORM 用 transformer 與 learnable motion tokens 生成 per-frame Gaussians 與 scene flow，但兩者都未善用 3D foundation model；最後援引 WorldSplat 的 4D-aware latent diffusion 與 DGGT 的 diffusion-based refinement，但批評 diffusion 增加 inference latency。

兩個子題的論述目的是建立「對照表」：證明既有 per-scene 方法慢、既有 feed-forward 方法弱（不論未用 foundation model 或加入 diffusion 而拖慢），讓 ReconDrive 同時主張「以 3D foundation model 達成 scalable 4D Gaussian prediction」與「不靠 iterative optimization 或 high-latency post-refinement」兩面優勢。Related Work 沒有 Preliminaries 子節，4DGS、SAM2、LoRA、VGGT 等概念是隨用隨引；其敘事任務集中在「替方法章節找對位置 — 既是 feed-forward 家族裡的 driving 專屬延伸，也是 driving GS 家族裡的 foundation-model 賦能版本」。

### 3.4 Method (overview narrative)

(1800 words)

Method 章節以三句 lead-in 把結構告知讀者：3.1 鋪 problem，3.2 鋪 backbone，3.3 鋪 4D 構成，3.4 鋪 training；這個拆法把「what to predict」「how to predict」「how to compose into 4D」「how to learn」四個階段順序展開，是典型的 reconstruction-pipeline 寫法。

3.1 先建立 problem formulation：輸入是 urban scene sequence $D = \{(I_t^o, C^o, E_t)\}$，每張影像 $I_t^o \in \mathbb{R}^{H \times W \times 3}$ 由第 $o$ 個相機在時間 $t$ 拍攝，相機帶 static calibration $C^o$，ego pose $E_t \in SE(3)$ 把 ego 座標映射到全域；目標是 feed-forward 地將 $D$ 映成解耦 static 與 dynamic 的 4D Gaussian Splatting，並能在任意 $t' \in [0, T]$ 與 novel viewpoint $E_{t'}^{novel}$ 下投影成像。緊接著作者把三項 challenge 重述為 scalability vs. efficiency、spatio-temporal modeling、geometric-photometric alignment，與 introduction 形成對位。Inference pipeline overview 引入 segment-wise representation：把場景切成 $\{[T_s, T_{s+1}]\}$，每段獨立生成 4D Gaussians；段內每個 Gaussian 以 center-moving 形式書寫為 $G_i(t) = (\mu_i(t), R_i, s_i, \alpha_i, c_i)$，static 背景的 $\mu_i(t)$ 不變，dynamic 物件採局部線性運動 $\mu_i(t) = \mu_{i,init} + v_i \cdot (t - T_s)$，把後文要回歸的核心參數 $v_i$ 預先點名。

3.2 把骨架拆成 feature backbone 與 hybrid prediction heads。Backbone 沿用 VGGT：輸入兩個 context frames、共 $2 \times O$（nuScenes 為 6）影像；經 patch size $p = 14$ 的 DINOv2 encoder 取得 $d = 1024$ 維 dense tokens，spatial grid 為 $(H'/p) \times (W'/p)$；隨後通過 24 層 Alternating-Attention Transformer，於 frame-wise self-attention 與 global self-attention 間交替，分別維持 timestamp 內 local 結構與跨 view、跨時間 geometric correlation。Hybrid heads 是本節 narrative 的轉折點：作者主張 VGGT 的 latent features 偏向 structural consistency 而缺 photometric detail，因此設計兩條 path —— GCPH 走幾何，GPPH 走外觀。GCPH 以 DPT upsample 得 $F_{C^o}^t$，再經 $3 \times 3$ conv 預測 pixel-wise depth $DP_t^o$，最後把深度圖以 calibration 投回 3D 空間以得 Gaussian centers，作者刻意強調此步驟把 calibrated sensor data 注入幾何流以避免 spatial misalignment。GPPH 則同樣 upsample 得 $F_t^o$，再 concatenate 原始影像形成 $FP_t^o$ 後過 conv，作者稱這個 shortcut 對於捕捉高頻 texture 與顏色至關重要。最後並用 LoRA（rank $r = 8$、scaling $\alpha = 32$）對 frozen VGGT 權重做 parameter-efficient adaptation。

3.3 處理「兩段 frame Gaussians 如何合成 4D」的核心問題。Dynamic mask 的取得依賴 SAM2 對 vehicles 的 instance-level 分割；速度估計則把 frame $T_{s+1}$ 的 3D bbox 標註轉換到 frame $T_s$ 的 ego coordinate，計算 displacement，並在 segment 內假設 rigid-body constant velocity，得 $v = \text{displacement} / (T_{s+1} - T_s)$；作者也補充：若資料無 3D 標註，可改用兩 frame Gaussian centers 做 displacement 計算。Pixel-wise mapping 把 dynamic motion flow $V$（$H' \times W' \times 3$）廣播至 mask 內所有像素，使第 $i$ 個 Gaussian 的 center 隨時間演化 $\mu_i(t) = \mu_i(T_s) + V(i) \cdot (t - T_s)$。Temporal alignment and fusion 則先以 $E_{T_i} \to E_{T_{i+1}}$ 的 ego 變換把 $G(T_{s+1})$ 空間搬到 $T_s$ ego frame，並對 centers、rotation、color coefficients 做變換；接著把 dynamic centers 以 $V$ 反推到 $T_s$；作者特別指出兩步順序不可互換，因 velocity field 是定義在 $T_s$ ego frame 中。最後把 $G(T_s)$ 與變換後的 $G'(T_{s+1})$ concatenate，加上 velocity flow 即構成段內最終 4D 表徵。

3.4 訓練章節列出三類 loss。Photometric 主軸由 perceptual loss $L_{percep} = \|\phi(\hat{I}) - \phi(I)\|_1$ 與 L2 loss $L_{l2} = \|\hat{I} - I\|_2$ 加權合成 $L_{render}$。Geometry 主軸引入 projection loss $L_{project} = L_{masked}(\lambda_{l1} \cdot L_{l1} + \lambda_{ssim} \cdot L_{ssim})$，把單一 source frame warp 到 reference frame 並只在 valid mask 內計分，目的是穩定 Gaussian center 預測並提升幾何精度。Regularization 主軸由 $L_{norm} = \lambda_{scale} \cdot E[\|\text{scalemaps}\|_2] + \lambda_{opacity} \cdot E[|\text{opacitymaps}|]$ 約束 scale 不爆與 opacity 趨近於 0/1。整體 end-to-end 損失 $L = L_{render} + L_{project} + L_{norm}$ 把三條軸線合一。Method 章節到此完成從 problem → backbone → 4D 構成 → training 的閉環，並把每個設計都明確 anchor 回 introduction 列出的三項 challenge，敘事同時兼顧 motivation 與 implementation。

### 3.5 Experiments (overview narrative)

(1010 words)

Experiments 章節以一句話開門：本節要在 nuScenes 上建立同時涵蓋 per-scene optimization 與 feed-forward 兩個家族的 visual urban scene reconstruction benchmark，並在多個 evaluation protocols 下比較方法效能。這個 framing 把「第一次有 feed-forward 方法在自駕場景上和 optimization 方法平起平坐」的對照需求說在最前。

4.1 Benchmark 鋪陳資料集與評估設計。nuScenes 原為 3D perception 設計，含 1,000 個 urban scenes、每段約 20 s、六台相機 multi-view；作者沿用原始 700 訓練場景訓 feed-forward 模型，從 validation split 挑出 14 個 representative 場景作為 evaluation set，刻意涵蓋 day/night、sunny/rainy、static/straight/turning、不同交通密度等條件，把覆蓋面寫進論述但同時控縮 evaluation 成本（detailed list 留至 Appendix）。Frame rate 採 12 Hz key frames，每 0.5 s（即每第 6 frame）作 context、其餘作 novel-view synthesis 對照，建立 reconstruction 與 synthesis 兩種任務的 frame split 規則。

評估協議分三類：(1) Visual Scene Reconstruction 在 context frames 上以 PSNR、SSIM、LPIPS 評估；(2) Novel-View Synthesis 在 non-context frames 上同樣用上述三指標；(3) Novel-View Synthesis for 3D Perception 透過模擬 ego trajectory 横向偏移 ±1m, ±2m, ±3m，再把 rendered multi-view 餵給 pre-trained UniAD（2 Hz），在 0m 與六個偏移共七個位置計算 3D detection 與 tracking（僅 vehicle 類）。整體論證鋪陳的關鍵點是：reconstruction 看 context fidelity，synthesis 看 view interpolation，perception 看下游 task 的 robustness，三層任務互補。

Baseline 設定上，optimization 家族選 Street Gaussians、PVG、DeformableGS、OmniRe，全部嫁接於 DriveStudio codebase，將其原本為 Waymo 設計的流程改寫支援 nuScenes 12 Hz；每個模型以 30,000 iterations per scene 訓練。Feed-forward 家族選 DrivingForward 為 SOTA 對手，並以多 frame 輸入確保公平。所有方法統一在 $518 \times 280$ 解析度下評估，使表 1、表 2 的數字可以直接對讀。

4.2 Main Experiment Results 從 implementation details 起手，列出 loss 權重 $\lambda_{percep} = 0.05, \lambda_{l2} = 1.0, \lambda_{l1} = 0.85, \lambda_{ssim} = 0.15, \lambda_{scale} = \lambda_{opacity} = 0.01$、AdamW + 8 步 gradient accumulation、兩階段訓練（10 epochs single-frame pre-training，學習率 $2 \times 10^{-5}$；2 epochs dual-frame fine-tuning，batch 2），dynamic-object masks 涵蓋五類車輛，整體耗 8 GPU-days 於 H800。

接著章節依任務逐項陳述結論。Visual reconstruction 上 PVG 最強 PSNR 29.58、OmniRe 最強 SSIM 0.8853、DeformableGS 最強 LPIPS；既有 feed-forward 與此差距明顯（DrivingForward PSNR 22.83）；ReconDrive 卻同時拿到 PSNR 32.66、SSIM 0.9589、LPIPS 0.0618，把 feed-forward 與 optimization 之間的 gap 直接抹平甚至倒轉。Novel-view synthesis 上 ReconDrive 同樣超越 DeformableGS 0.26 dB PSNR、0.0315 SSIM，並比 DrivingForward 多 2.11 dB PSNR、0.0368 SSIM 與 –0.0388 LPIPS，論證「inference speed 與 synthesis quality 不再是 trade-off」。3D perception 上 ReconDrive 取得 mAP 26.7%、AMOTA 18.9%，全面領先所有 baselines，凸顯下游任務 robustness。Inference efficiency 段落說明 ReconDrive 利用相鄰 segment 的 context frame 共享、加上 caching，每場景 15 s，雖略慢於 DrivingForward 的 5 s，但比 optimization 方法的 30 min 快了 orders of magnitude；作者用「superior balance」這句話結束此節，與 introduction 中的 scalability claim 對齊，同時為 §5 的結論收尾鋪好基礎。

### 3.6 Conclusion / Limitations / Future Work

(470 words)

Conclusion 首段先回到 introduction 的開場主題：閉環評估與模擬平台是自駕產業的基礎需求。接著重申 ReconDrive 的核心定位 — feed-forward 4DGS、針對大規模駕駛場景、單次 forward pass 即生成完整場景表徵；三項使其奏效的設計再次被點名：static-dynamic composition strategy、segment-wise Gaussian aggregation、specialized Gaussian prediction architecture，把 §3 的方法骨架在收尾時做一次 reinforce。

第二段把實驗結論拉到敘事高位：在新建 nuScenes benchmark 上，ReconDrive 在「nearly all evaluation metrics」上勝過 SOTA per-scene optimization baselines；作者寫出「to the best of our knowledge, this work represents the first instance where a feed-forward approach surpasses optimization-based methods」這句宣告，把全文價值錨定在 paradigm shift 而非單純效能改進，並把這個結果定義為「對 scalable, generative simulation environments 的 clear direction and renewed confidence」。

Limitations and Future Work 接著以五點清楚列出邊界。(1) Temporal Representation of Non-Rigid Motion：目前的 linear motion estimation 對複雜 non-rigid deformation 與高度非線性軌跡能力有限，未來可導入更具表達力的 temporal kernels 或 learnable deformation fields。(2) Temporal Consistency and Redundancy in Aggregation：以 pixel-wise output 做多 frame 後處理可能產生 Gaussian redundancy 並對 occluded 區域處理不佳，建議改為 latent space 中的整合式 temporal fusion。(3) Precision in Dynamic Object Extraction：仰賴 SAM2 的分割可能 boundary 不精或漏偵；同時直接位移 dynamic objects 會在背景留下 disocclusion artifact（"background holes"），未來可嘗試 joint inpainting 或 end-to-end motion modeling。(4) Computational Efficiency and Throughput：相對 optimization 雖快，但仍有 backbone 與 Gaussian sampling 的優化空間，特別針對 edge-computing 的即時性。(5) Scalability and Generalization：訓練資料尚集中於 nuScenes，未來需擴大至更多地理區域、極端天氣與駕駛行為（這裡作者甚至引用自家 StyleDrive 工作以鋪陳 driving-style 多樣性）。

整體而言，§5 的 narrative 走的是「再次定位 → 強調 paradigm-shift 的 first-instance 結果 → 明列邊界」三段式；其敘事意圖是把貢獻寫成「一個方向被證明可行」而非「一個產品 ready」，並把限制條列得足夠具體，使後續工作（無論本團隊或他人）能直接以此為 roadmap 接手。Conclusion 與 Limitations 一段式並列也讓讀者在離開正文前明確意識到：ReconDrive 是 feed-forward × 3D foundation model × 自駕場景這條技術路線的起點，不是終點。

## 4. Critical Profile

### 4.1 Highlights

- ReconDrive 是首個在 nuScenes 自駕場景重建上超越 per-scene optimization 基線的 feed-forward 4DGS 框架,於九項指標中拿下八項第一(Sec. 1, p. 2)。
- 在 visual scene reconstruction 上 PSNR 達 32.66、SSIM 0.9589、LPIPS 0.0618,顯著領先 PVG 的 29.58 與 OminiRe 的 0.8853(Tab. 1, p. 8)。
- Novel-view synthesis 上 PSNR 23.99 高於 DeformableGS 的 23.73,並較同類 feed-forward DrivingForward 提升 2.11 dB PSNR、降低 0.0388 LPIPS(Tab. 1, p. 8)。
- 推論速度 15s/scene,相對於 Street Gaussians 的 31min 與 OminiRe 的 35min 快約兩個數量級,且僅比 DrivingForward 慢 10s 即換得大幅品質提升(Tab. 1, p. 8)。
- 提出 Hybrid Gaussian Prediction Heads,將 GCPH 與 GPPH 解耦,GPPH 透過 shortcut 將原始影像與 dense feature concatenation 以補回高頻紋理,GCPH 則直接注入 camera intrinsic/extrinsic 進行 depth-to-3D projection(Sec. 3.2, p. 5)。
- Static-Dynamic 4D Composition 用 SAM2 抽取 vehicle/truck/bus/trailer/construction vehicle 五類 mask,以兩幀 3D bbox 位移除以時間差估計 velocity,再以 center-moving paradigm 顯式建模動態(Sec. 3.3 與 Eq. 4, p. 6)。
- Segment-wise Temporal Fusion 透過 caching 共用相鄰 segment 的 context frame,將長序列分段以平衡覆蓋率與即時渲染的 active Gaussian 數(Sec. 4.2 Inference Efficiency, p. 9)。
- 在 3D 感知下游任務(±1/2/3m 橫向偏移後讓 UniAD 重新偵測)達到 mAP 26.7%、AMOTA 18.9%,均高於所有 per-scene 與 feed-forward 基線,顯示重建品質可遷移到 perception(Tab. 2, p. 9)。
- 採用 frozen VGGT 加 LoRA (rank $r=8$, $\alpha=32$) 的 parameter-efficient fine-tuning,在 8 GPU-days 的 H800 訓練成本下完成 domain adaptation(Sec. 3.2 與 Sec. 4.2 Implementation Details, pp. 5, 8)。
- 提出 novel-frame projection loss(基於 backproject、ego-motion warp、grid_sample 與 valid mask)以穩定 unseen 時間點的 depth 預測(Sec. 3.4 與 Appendix B, pp. 6, 13–14)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 線性運動假設不足以表達非剛體形變或高度非線性軌跡,作者建議改用更具表達力的 temporal kernel 或 learnable deformation field(Sec. 5 Limitations, p. 10)。
- 多幀聚合採 pixel-wise 後處理會造成 Gaussian redundancy,並對遮蔽區域處理不佳(Sec. 5 Limitations, p. 10)。
- 動態物件抽取仰賴 SAM2,邊界不準或漏偵測會直接傳遞;且動態物件位移後在背景留下 disocclusion holes,需 inpainting 或 end-to-end motion modeling 才能緩解(Sec. 5 Limitations, p. 10)。
- 雖比 optimization 快,但仍非 edge-deployable real-time,需更輕量 backbone 與更有效率的 Gaussian sampling(Sec. 5 Limitations, p. 10)。
- 訓練資料僅 nuScenes 700 場景,在地理分布、極端天氣與駕駛行為多樣性上仍待擴充(Sec. 5 Limitations, p. 10)。
- Appendix C 自承直接使用 VGGT 的 point map 與 LiDAR 之間存在顯著 metric scale misalignment,需 calibration 注入才能對齊(Appendix C, p. 14)。

#### 4.2.2 Phyra-inferred

- Velocity 主要來自 nuScenes 提供的 3D bbox annotation 兩幀位移除以時間差(Eq. 3, Sec. 3.3),雖在第 6 頁順帶提到「無 3D 標註時可用兩幀 Gaussian center」,但論文並未提供任一無標註資料集上的數據,因此 feed-forward 宣稱在實際無 LiDAR/box 場景下其實未被驗證。
- Tab. 1 的「context frame」是每 6 幀取 1 幀做為 GT 來計算 reconstruction PSNR,而 ReconDrive 的輸入正是這些 context frame,因此 reconstruction 指標其實是在「輸入幀本身」上重渲染,32.66 dB 的領先包含對輸入過擬合的成分,與 optimization 基線在同樣 context frame 上訓練的 setup 並非完全等價評估。
- 整篇論文僅在 nuScenes 一個資料集上比較,沒有 Waymo / KITTI / Argoverse 等跨資料集泛化結果,而 feed-forward 主要賣點正是「免 per-scene optimization 的泛化性」,這一賣點未被獨立驗證。
- 訓練只有 700 個場景但要泛化到城市駕駛全域,且 LoRA 僅 $r=8$,Tab. 1 的高分有可能來自 14 個 validation scene 與訓練分布的相似性,論文未提供 train/val 場景幾何相似度或 leave-one-city-out 等控制實驗。
- Tab. 2 中 ReconDrive 的 mAP 26.7% 高於 DrivingForward 的 23.4%,但 PVG 在 detection (18.5%) 與 tracking (14.4%) 之間的差距遠小於 ReconDrive 在這兩項的差距(26.7 vs 18.9),顯示 detection 大幅領先但 tracking 相對保守,可能反映動態 Gaussian 的時間一致性其實比論文敘事更弱,而論文未討論此 gap。
- 無 ablation 拆分 GPPH 的 image shortcut、GCPH 的 calibration 注入、static-dynamic composition、segment-wise fusion 各自貢獻;Tab. 3 僅比較 1 vs 2 frame input,因此「三大 design pillars 各自必要」的因果敘事缺乏實驗支撐。
- 推論延遲 15s/scene 是「Gaussian 生成」時間,論文未報告含 SAM2 mask 抽取與 ego pose 處理的 end-to-end latency,實際部署成本被低估。
- LPIPS 0.2591 在 novel-view synthesis 上其實仍劣於 DeformableGS 的 0.2342(Tab. 1),作者敘事中以「comparable perceptual quality」帶過,實際上 perceptual 指標並未拿下第一。

### 4.3 Phyra's Judgment (summary)

ReconDrive 真正新的部分,是把 VGGT 風格的 3D foundation backbone 改造成可吐 4DGS 的 feed-forward 管線,並用 GPPH 的 image shortcut + GCPH 的 calibration 注入這兩個務實設計回應 photometric 與 calibration 兩個結構性缺陷;這在 nuScenes 上首次讓 feed-forward 在重建品質上與 per-scene optimization 平起平坐,具有典範意義。但 dynamic motion 仰賴 nuScenes 的 3D bbox、評估只在單一資料集且 reconstruction 指標其實是輸入幀重渲染,因此「免 per-scene optimization 的泛化性」這個 feed-forward 最關鍵的賣點仍未被獨立驗證。核心未解的問題是:當沒有 LiDAR 與 3D box 先驗時,ReconDrive 的 dynamic 表達能否仍維持 Tab. 2 的下游 perception 收益。

## 5. Methodology Deep Dive

### 5.1 Method Overview

ReconDrive 將「以多視角影像直接前饋產生 4D Gaussian Splatting」整體拆解為三個耦合模組，建構在 VGGT 風格的 3D foundation backbone 之上：(i) Feature Backbone (DINOv2 patch tokens + 24 層 Alternating-Attention Transformer) 負責從兩個 context frames $T_s, T_{s+1}$ 各 6 個相機共 $2\times O$ 張影像中萃取 spatio-temporal tokens；(ii) Hybrid Gaussian Prediction Head 將 Gaussian 屬性回歸拆成兩條路徑：Gaussian Center Prediction Head (GCPH) 以 DPT 上採樣 transformer features，預測 pixel-wise depth map 並透過相機 intrinsic/extrinsic 反投影為 ego-coordinate 下的 3D centers $\mu_i$；Gaussian Parameter Prediction Head (GPPH) 同樣以 DPT 上採樣，但透過 shortcut concatenate 原圖與 dense feature，再以 conv layer 回歸 rotation $R_i$、scale $s_i$、opacity $\alpha_i$ 與 spherical harmonics coefficients $c_i$；(iii) Static-Dynamic 4D Composition 利用 SAM2 抽取動態交通參與者的 instance masks，並從 nuScenes 3D bbox annotations 計算 per-object velocity $v_i$，將 mask 內 Gaussians 標記為動態並賦予速度向量，靜態 Gaussians 則 $\mu_i(t)=\mu_{i,\text{init}}$ 維持不變。

第二階段為 Temporal Alignment and Fusion：先將 $T_{s+1}$ 的 Gaussian centers、rotation 與 SH coefficients 透過 ego transformation $E_{T_s}^{-1}E_{T_{s+1}}$ 變換到 $T_s$ 的 ego coordinate，再以 velocity flow $V$ 將動態 Gaussians 的 center 移回 $T_s$ 時刻（這兩步順序不可調換，因為 velocity field 是在 $T_s$ ego frame 下定義的），最後 concatenate $G(T_s)$ 與變換後的 $G'(T_{s+1})$，配合 velocity flow 共同構成 segment $[T_s, T_{s+1}]$ 的 4D 表示。整體訓練端到端進行：以凍結的 VGGT 權重作為結構先驗，僅以 LoRA (rank $r=8$, scaling $\alpha=32$) 微調至駕駛域，並由三項 loss 構成：rendering loss $L_\text{render}=\lambda_\text{percep}L_\text{percep}+\lambda_\text{l2}L_\text{l2}$、projection loss $L_\text{project}=L_\text{masked}(\lambda_\text{l1}L_\text{l1}+\lambda_\text{ssim}L_\text{ssim})$、以及 norm loss $L_\text{norm}=\lambda_\text{scale}\mathbb{E}[\|s\|_2]+\lambda_\text{opacity}\mathbb{E}[|\alpha|]$，三者直接加總為 $L=L_\text{render}+L_\text{project}+L_\text{norm}$，其中 projection loss 是 ReconDrive 為解決 photometric deficiency 與 calibration mismatch 而新引入的關鍵設計，透過將單一來源幀 warp 至參考幀以強制幾何一致性。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: I_t^o ∈ [B, 2*O, H, W, 3]  (B=batch, O=6 for nuScenes, t∈{T_s, T_{s+1}})
   │
   ├→ [B, 2*O, H, W, 3] ─── Calibration C^o ∈ [B, O, 4, 4]  (intrinsics+extrinsics)
   │                       Ego pose E_t ∈ [B, 2, 4, 4]
   │
   ▼
Image Tokenization (DINOv2 encoder, patch size p=14)
   │  resize: H, W → H', W' (scale factor ?, 論文未明示 H'×W')
   │  patchify: (H'/14) × (W'/14) tokens per image, dim d=1024
   │
   ▼ tokens ∈ [B, 2*O, (H'/14)*(W'/14), 1024]
   │
   ▼
Alternating-Attention Fusion (24 Transformer layers, frozen + LoRA r=8, α=32)
   │  layers alternate: frame-wise self-attention ↔ global self-attention
   │  concat all 2*O views' tokens for global attention
   │
   ▼ fused tokens ∈ [B, 2*O, (H'/14)*(W'/14), 1024]
   │
   ├──────────────────────────────┬──────────────────────────────┐
   │                              │                              │
   ▼                              ▼                              │
GCPH (Gaussian Center             GPPH (Gaussian Parameter        │
Prediction Head)                  Prediction Head)                │
   │                                 │                            │
   │ DPT upsample                    │ DPT upsample                │
   │ tokens → F_C^o ∈                │ tokens → F^o ∈              │
   │ [B, 2*O, H', W', d_C]           │ [B, 2*O, H', W', d_F]       │
   │                                 │ (d_C, d_F 論文未明示)        │
   │                                 │                            │
   │ Conv 3×3                        │ Concat shortcut:            │
   │ → depth map                     │ FP^o = [F^o ; I_resized^o] │
   │ DP^o ∈ [B, 2*O, H', W', 1]      │ ∈ [B, 2*O, H', W', d_F+3]   │
   │                                 │                            │
   │ Unproject with C^o              │ Conv layer                  │
   │ μ_i ∈ [B, 2*O, H'*W', 3]        │ → R_i ∈ [B, 2*O, H'*W', 4]  │
   │ (per-camera ego coord)          │ → s_i ∈ [B, 2*O, H'*W', 3]  │
   │                                 │ → α_i ∈ [B, 2*O, H'*W', 1]  │
   │                                 │ → c_i ∈ [B, 2*O, H'*W', k]  │
   │                                 │ (k = SH coeff count, 未明示) │
   │                                 │                            │
   └──────────────┬───────────────────┘                            │
                  │                                               │
                  ▼                                               │
       Per-frame Gaussian set                                     │
       G(T_s), G(T_{s+1}) each ∈                                  │
       [B, 2*O*H'*W', (3+4+3+1+k)]                                │
                  │                                               │
                  ▼                                               │
   ┌──────────────┴───────────────┐                               │
   │                              │                               │
   ▼                              ▼                               │
SAM2 (frozen)                 nuScenes 3D bbox                    │
   │ extract instance             │ per-object 3D location at     │
   │ masks for                    │ T_s, T_{s+1}                  │
   │ vehicles/peds                │                               │
   │ M^o ∈ [B, 2*O, H', W']       │                               │
   │ (binary)                     │                               │
   │                              │ transform bbox at T_{s+1}     │
   │                              │ into T_s ego coord            │
   │                              │ displacement = pos_{T_{s+1}}  │
   │                              │              − pos_{T_s}      │
   │                              │ v = displacement /            │
   │                              │     (T_{s+1} − T_s)           │
   │                              │ ∈ [B, N_obj, 3]               │
   │                              │                               │
   └──────────────┬───────────────┘                               │
                  │                                               │
                  ▼                                               │
       Velocity flow V ∈ [B, 2*O, H', W', 3]                      │
       (broadcast per-object v to mask pixels;                    │
        background pixels: v = 0)                                 │
                  │                                               │
                  ▼                                               │
Static-Dynamic 4D Composition                                     │
   │ For static pixels:  μ_i(t) = μ_i(T_s)                        │
   │ For dynamic pixels: μ_i(t) = μ_i(T_s) + V(i)·(t − T_s)       │
   │                                                              │
   ▼                                                              │
Temporal Alignment & Fusion                                       │
   │ Step 1: spatial transform G(T_{s+1}) into T_s ego coord       │
   │   using E_{T_s}^{-1} · E_{T_{s+1}}                            │
   │   (apply to centers, rotations, SH coefficients)              │
   │ Step 2: temporal align: move dynamic centers of               │
   │   transformed G(T_{s+1}) back to t=T_s via −V·(T_{s+1}−T_s)   │
   │   yielding G'(T_{s+1})                                        │
   │ Step 3: concatenate                                           │
   │   G_4D = [G(T_s) ; G'(T_{s+1})]                               │
   │   ∈ [B, 2 * 2*O*H'*W', (3+4+3+1+k)]                           │
   │                                                              │
   ▼                                                              │
4D Gaussians for segment [T_s, T_{s+1}]                           │
   │ + velocity flow V                                            │
   │                                                              │
   ▼                                                              │
Differentiable Rasterization (3DGS-style)                         │
   │ render at any t' ∈ [T_s, T_{s+1}], any novel viewpoint        │
   │   E_{t'}^{novel}                                              │
   │                                                              │
   ▼                                                              │
Rendered images Î ∈ [B, H', W', 3]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Feature Backbone (DINOv2 + Alternating-Attention Transformer)

**Function:** 將 $2\times O$ 張多視角 RGB 影像編碼為融合空間與時間幾何相關性的 dense tokens，作為後續 Gaussian regression 的共同特徵基底。

**Input:**
- Name: $I_t^o$
- Shape: `[B, 2*O, H, W, 3]`，$O=6$ (nuScenes)，$t\in\{T_s, T_{s+1}\}$
- Source: 兩個 context frame 的 $O$ 個 surround-view 相機

**Output:**
- Name: fused tokens
- Shape: `[B, 2*O, (H'/p)*(W'/p), d]`，$p=14$, $d=1024$
- Consumer: GCPH 與 GPPH 的 DPT upsampling

**Processing:**

1. Image Tokenization：每張影像先被 resize 至 $H'\times W'$（paper §3.2 僅提及 scale factor 為 3，未明示具體 $H'\times W'$ 數值；§4.1 提及 evaluation 解析度為 $518\times 280$，但 backbone 內部解析度未明說，因此標為 `?`）。
2. 以 DINOv2 patch encoder 將每張 resized 影像切為 patch size $p=14$ 的 token grid，輸出 dim $d=1024$。
3. 將 $2\times O$ 張影像的 tokens concat 後送入 24 層 Transformer。每層 Alternating-Attention 在「frame-wise self-attention」（同一時間戳同一相機內的 token）與「global self-attention」（跨相機跨時間戳的所有 token）之間交替，前者保留局部結構一致性，後者捕捉跨視角與時間的幾何相關性。

**Key Formulas:**

論文未提供具體公式表達 backbone 的 attention 形式。

**Implementation Details:**

- Backbone 採用預訓練 VGGT 權重並凍結，僅以 LoRA adapters 微調，rank $r=8$, scaling factor $\alpha=32$。
- 兩個 context frames 取自每段 ~20s 場景，依 §4.1 為每 0.5 秒（即每 6 張 12 Hz 關鍵幀）取一張 context frame。
- 推論時相鄰 segment 共享 context frame，啟用 caching 機制以消除冗餘計算（§4.2 Inference Efficiency）。
- 訓練分兩階段：(1) Single-frame pre-training 10 epochs (batch size 4, lr $2\times 10^{-5}$, weight decay 0.01)，每個輸入幀同時作為自身的 ground truth；(2) Dual-frame fine-tuning 2 epochs (batch size 2)。AdamW 優化器，gradient accumulation 8 steps。

#### 5.3.2 Gaussian Center Prediction Head (GCPH)

**Function:** 從 backbone 融合特徵直接回歸 pixel-wise depth，再透過相機標定反投影至 3D，獲得錨定於 ego 座標系的 Gaussian 空間中心 $\mu_i$；藉由顯式注入 calibration 解決 VGGT 在駕駛域的幾何錯位 (domain & calibration mismatch)。

**Input:**
- Name: fused tokens, calibration $C^o$, ego pose $E_t$
- Shape: tokens `[B, 2*O, (H'/p)*(W'/p), 1024]`；$C^o$ `[B, O, 4, 4]`；$E_t$ `[B, 2, 4, 4]`
- Source: Feature Backbone (5.3.1)；nuScenes 提供的 sensor calibration 與 ego pose

**Output:**
- Name: Gaussian centers $\mu_i$
- Shape: `[B, 2*O, H'*W', 3]`，每張影像每個 pixel 對應一個 3D center
- Consumer: Static-Dynamic 4D Composition 與 Temporal Alignment

**Processing:**

1. **DPT Upsample**：以 Dense Prediction Transformer (DPT, Ranftl et al. 2021) 將 tokens 上採樣回 $H'\times W'$ 的 dense feature map $F_{C_t}^o$。論文未明示輸出 channel 數，標為 `?`。
2. **Depth Prediction**：以一個 $3\times 3$ convolutional layer 將 $F_{C_t}^o$ 轉為 pixel-wise depth map $DP_t^o\in\mathbb{R}^{H'\times W'\times 1}$。
3. **Unprojection**：以相機 intrinsic 與 extrinsic 將每個 pixel $(u,v)$ 與其 depth $d$ 反投影到 3D，產生對應的 Gaussian center。注意兩個 frame 的 centers 各自位於該 frame 的 ego coordinate 中，跨幀對齊由後續模組處理。

**Key Formulas:**

論文未針對 unprojection 給出具體公式，但語意上等價於

$$
\mu_i = E_{T_s}^{-1}\cdot[(R^o\cdot K^{-1}\cdot[u,v,1]^\top\cdot d) + t^o]
$$

（此處 $K, R^o, t^o$ 分別為相機 intrinsic 與 ego→camera extrinsic，論文以高層描述帶過。）

**Implementation Details:**

- DPT 上採樣輸出的 feature dim $d_C$ 論文未明示。
- depth 預測 conv 的 kernel 為 $3\times 3$，輸出 channel 1。
- GCPH 顯式利用 nuScenes 提供的 pre-calibrated intrinsics/extrinsics，作者於 Appendix 進一步展示直接套用 VGGT 在駕駛場景時的空間錯位（本文未含 Appendix 內容）。

#### 5.3.3 Gaussian Parameter Prediction Head (GPPH)

**Function:** 從 backbone 融合特徵與原圖共同回歸 Gaussian 的外觀與幾何屬性 (rotation, scale, opacity, spherical harmonic coefficients)，藉由 raw image shortcut 補回 backbone feature 中遺失的高頻紋理，解決 photometric deficiency。

**Input:**
- Name: fused tokens, resized RGB images
- Shape: tokens `[B, 2*O, (H'/p)*(W'/p), 1024]`；resized images `[B, 2*O, H', W', 3]`
- Source: Feature Backbone (5.3.1)；輸入影像在 backbone 之前 resize 的版本

**Output:**
- Name: Gaussian parameters $(R_i, s_i, \alpha_i, c_i)$
- Shape: 各為 `[B, 2*O, H'*W', 4]`、`[B, 2*O, H'*W', 3]`、`[B, 2*O, H'*W', 1]`、`[B, 2*O, H'*W', k]`，其中 $k$ 為 SH 係數數量（論文未明示）
- Consumer: Static-Dynamic 4D Composition 後直接輸入 differentiable rasterization

**Processing:**

1. **DPT Upsample**：與 GCPH 對稱，將 tokens 上採至 $H'\times W'$ 的 feature $F_t^o$（channel 數 $d_F$ 論文未明示）。
2. **Shortcut Concatenation**：將 resized 原圖沿 channel 維度與 $F_t^o$ concat，得到 $FP_t^o\in\mathbb{R}^{H'\times W'\times(d_F+3)}$。此 shortcut 是 ReconDrive 補回 transformer feature downsampling 中遺失之高頻紋理與顏色細節的關鍵設計。
3. **Conv Regression**：以一個 conv layer 同時回歸 rotation matrix $R_i\in SO(3)$、anisotropic scale $s_i\in\mathbb{R}^3$、opacity $\alpha_i\in[0,1]$、spherical harmonics coefficients $c_i\in\mathbb{R}^k$。所有屬性均以 pixel-wise 方式輸出，與 GCPH 的 centers 對齊，形成 pixel-wise 對應的完整 Gaussian。

**Key Formulas:**

per-Gaussian kernel 定義 (paper Eq.1)：

$$
G_i(t) = (\mu_i(t), R_i, s_i, \alpha_i, c_i)
$$

**Implementation Details:**

- conv layer 的 kernel size 與輸出 channel 結構未明示。
- GPPH 與 GCPH 是兩個獨立的 prediction head（dual-path），共用 backbone tokens，但 DPT 與 conv 權重不共享。
- $R_i$ 的具體參數化（quaternion 或其他）論文未明說。

#### 5.3.4 Dynamic Object Mask & Velocity Estimation (SAM2 + 3D Bbox)

**Function:** 偵測動態交通參與者並估計其運動向量，是表達場景時間變化、解決 temporal staticity 的關鍵；輸出 pixel-aligned velocity flow 與 Gaussian dynamic/static 標記。

**Input:**
- Name: 兩個 context frames 的 RGB 影像、nuScenes 3D bounding box annotations、ego pose $E_t$
- Shape: 影像 `[B, 2*O, H, W, 3]`；bbox 為每段註記
- Source: 原始輸入與 nuScenes 標註

**Output:**
- Name: instance masks $M^o$、velocity flow $V$
- Shape: $M^o$ `[B, 2*O, H', W']` (binary)；$V$ `[B, 2*O, H', W', 3]`
- Consumer: Static-Dynamic 4D Composition

**Processing:**

1. **Mask Extraction**：使用 SAM2 (Ravi et al. 2024) 對兩個 context frames 抽取 vehicles/pedestrians 的 instance-level mask。SAM2 同時具備穩健 mask 與快速推論，與 ReconDrive 的即時性需求對齊。
2. **Per-object Velocity**：對每個動態 object，將其 $T_{s+1}$ 的 3D location 以 ego transformation 變換到 $T_s$ 的 ego coordinate，計算 displacement，並以 segment 內的 rigid-body constant velocity 假設估計 velocity。當無 3D bbox 標註時，亦可由兩幀 Gaussian centers 的中心位移估計，實現對未標註資料集的擴展。
3. **Velocity Flow Construction**：將每個 object 的速度向量廣播到對應 mask 區域內所有 pixel，形成 $V\in\mathbb{R}^{H'\times W'\times 3}$；mask 外的 pixel 速度為 0。Fig.2 顯示 image / mask / dense feature / Gaussian kernel 之間具有 pixel-wise 一致映射，使 velocity flow 可直接索引到對應 Gaussian。

**Key Formulas:**

velocity (paper Eq.3)：

$$
v = \frac{\text{displacement}}{T_{s+1}-T_s}
$$

dynamic Gaussian center 隨時間演化 (paper Eq.4)：

$$
\mu_i(t) = \mu_i(T_s) + V(i)\cdot(t-T_s),\quad t\in[T_s, T_{s+1}]
$$

**Implementation Details:**

- 動態類別涵蓋五類車輛：car, truck, bus, trailer, construction vehicle (§4.2)。
- SAM2 為現成 foundation model，未在 ReconDrive 中重新訓練。
- 假設「短時間 $[T_s, T_{s+1}]$ 內物體做剛體等速運動」是 ReconDrive 的限制之一，論文於 Limitations 中明確指出此假設無法表達非剛體變形或高度非線性軌跡。

#### 5.3.5 Static-Dynamic 4D Composition

**Function:** 將 GPPH/GCPH 輸出的 per-frame Gaussians 與 dynamic mask、velocity flow 結合，形成「中心移動」式的 4D 表示，把時間維度顯式注入進靜態 3D Gaussian 表達中。

**Input:**
- Name: per-frame Gaussians $G(T_s), G(T_{s+1})$、masks $M^o$、velocity flow $V$
- Shape: $G(\cdot)$ `[B, 2*O*H'*W', (3+4+3+1+k)]`；$M^o, V$ 同 5.3.4
- Source: GCPH/GPPH (5.3.2/5.3.3) 與 SAM2/bbox 模組 (5.3.4)

**Output:**
- Name: pixel-wise 4D Gaussians（每幀內已標記 static/dynamic）
- Shape: 同 input，但每個 Gaussian 額外帶有 dynamic 標記與 velocity 索引
- Consumer: Temporal Alignment & Fusion

**Processing:**

1. **Static**：對 mask 外的 pixel，$\mu_i(t)=\mu_{i,\text{init}}$，rotation/scale/opacity/SH 也保持時間不變。
2. **Dynamic**：對 mask 內 pixel，依 Eq.2/Eq.4 用 velocity flow 更新 center：
   $$
   \mu_i(t) = \mu_{i,\text{init}} + v_i\cdot(t-T_s)
   $$
   其餘屬性 $R_i, s_i, \alpha_i, c_i$ 在 segment 內維持不變。

**Key Formulas:**

dynamic center motion model (paper Eq.2)：

$$
\mu_i(t) = \mu_{i,\text{init}} + v_i\cdot(t-T_s),\quad t\in[T_s, T_{s+1}]
$$

**Implementation Details:**

- 假設 segment 內 rigid-body constant velocity；scale 與 SH 為時間恆定，因此非剛體變形或外觀劇變無法被建模。
- 所有 Gaussian 的時間外推皆只在 $[T_s, T_{s+1}]$ 內有效，跨 segment 的長時間對齊則由 segment-wise temporal fusion 處理（屬於 §3.1 推論流程，不在 §3.2/3.3 詳述）。

#### 5.3.6 Temporal Alignment & Fusion

**Function:** 將兩個 frame 的 Gaussian sets 合併到統一的 4D 表示，以 $T_s$ 的 ego coordinate 與 $T_s$ 的時間戳作為共同基準，解決多幀對齊問題。

**Input:**
- Name: $G(T_s), G(T_{s+1})$、ego poses $E_{T_s}, E_{T_{s+1}}$、velocity flow $V$
- Shape: $G(\cdot)$ `[B, 2*O*H'*W', (3+4+3+1+k)]`；$E_{T_\cdot}\in\mathbb{R}^{4\times 4}$
- Source: Static-Dynamic 4D Composition (5.3.5)

**Output:**
- Name: $G_{4D}$ for segment $[T_s, T_{s+1}]$
- Shape: `[B, 2 * 2*O*H'*W', (3+4+3+1+k)]`（兩幀 concat）
- Consumer: Differentiable Rasterization

**Processing:**

1. **Spatial Transform**：以 ego transformation $E_{T_s}^{-1}\cdot E_{T_{s+1}}$ 將 $G(T_{s+1})$ 的 centers、rotation 與 SH coefficients 變換到 $T_s$ 的 ego coordinate。對 SH 係數的旋轉處理論文未細述。
2. **Temporal Align**：對變換後的動態 Gaussians，套用 velocity flow $V$ 將 center 移回 $t=T_s$ 時刻，得到 $G'(T_{s+1})$。論文明示「先空間變換再時間對齊」的順序不可調換，因 $V$ 是在 $T_s$ ego frame 下定義的。
3. **Concatenate**：將 $G(T_s)$ 與 $G'(T_{s+1})$ 沿 Gaussian 數量維度 concat，與 velocity flow $V$ 共同構成最終 4D Gaussian splatting 表示，可在任意 $t'\in[T_s, T_{s+1}]$、任意 novel viewpoint $E_{t'}^\text{novel}$ 投影渲染。

**Key Formulas:**

論文未提供 spatial transform 的閉式表達，語意上：

$$
G'(T_{s+1}) = \mathcal{T}_\text{align}\bigl(\mathcal{T}_\text{spatial}(G(T_{s+1}); E_{T_s}^{-1}E_{T_{s+1}}); V\bigr)
$$

**Implementation Details:**

- 每段 segment 由相鄰兩個 context frames 構成，segment-wise 切分允許控制活動 Gaussian 數量、實作即時渲染（推論速度 15s/scene，§4.2）。
- 兩個 context frames 在 inference 時可被相鄰 segment 共享，啟用 caching 加速。
- 該模組屬於不可微的幾何變換，不引入額外可學參數。

#### 5.3.7 Training Losses

**Function:** 監督 Gaussian 屬性與 4D 表示的學習，平衡像素層級忠實度、感知一致性、幾何投影一致性與規則化。

**Input:**
- Name: rendered images $\hat I$ / $\hat I_\text{warped}$、ground-truth $I$ / $I_\text{warped, GT}$、scale/opacity maps
- Source: 渲染管線輸出與 GCPH/GPPH 預測

**Output:**
- Name: total loss $L$
- Shape: scalar
- Consumer: AdamW optimizer

**Processing:**

1. **Rendering Loss**：以 perceptual loss (VGG-19 layer feature 的 L1 距離) 與 L2 pixel-wise loss 監督渲染像素：
   $$
   L_\text{render} = \lambda_\text{percep} L_\text{percep} + \lambda_\text{l2} L_\text{l2}
   $$
   其中 $L_\text{percep}=\|\phi(\hat I)-\phi(I)\|_1$、$L_\text{l2}=\|\hat I - I\|_2$。
2. **Projection Loss**：將單一來源幀 $t$ warp 至參考幀 $t'$，在 valid warping mask 內計算 weighted L1 與 weighted SSIM：
   $$
   L_\text{project} = L_\text{masked}\bigl(\lambda_\text{l1} L_\text{l1} + \lambda_\text{ssim} L_\text{ssim}\bigr)
   $$
   其中 $L_\text{l1}$ 為 warped 預測影像與 warped GT 影像之間的 pixel-wise L1，$L_\text{ssim}=1-\text{SSIM}(\hat I_\text{warped}, I_\text{warped, GT})$。
3. **Norm Loss**：以 L2 規則化 Gaussian scale，以 L1 規則化 opacity 以鼓勵稀疏化（推 opacity 朝 0 或 1 收斂）：
   $$
   L_\text{norm} = \lambda_\text{scale}\,\mathbb{E}[\|\text{scale}_\text{maps}\|_2] + \lambda_\text{opacity}\,\mathbb{E}[|\text{opacity}_\text{maps}|]
   $$
4. **Total Loss**：
   $$
   L = L_\text{render} + L_\text{project} + L_\text{norm}
   $$

**Key Formulas:**

主要公式如上 (paper Eq.5/6/7/8)。

**Implementation Details:**

- 超參數：$\lambda_\text{percep}=0.05$, $\lambda_\text{l2}=1.0$, $\lambda_\text{l1}=0.85$, $\lambda_\text{ssim}=0.15$, $\lambda_\text{scale}=\lambda_\text{opacity}=0.01$。
- $\phi(\cdot)$ 為 VGG-19 某一卷積層的 feature extractor，論文未明示具體層級。
- projection loss 的 valid mask 細節留至 Appendix（不在文中提供）。
- 訓練於 H800 GPUs，整體耗費 8 GPU-days；分兩階段：(1) Single-frame pre-training 10 epochs (batch size 4, lr $2\times 10^{-5}$, weight decay 0.01)，每幀同時作 GT；(2) Dual-frame fine-tuning 2 epochs (batch size 2)。
- 在 nuScenes 2 Hz key frame 上以 $518\times 280$ 解析度評估，評估時將 context frames 的 PSNR/SSIM/LPIPS 用於 scene reconstruction，將非 context frames（每 6 幀一組中其餘第 2~5 幀）用於 novel-view synthesis。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| nuScenes (Caesar et al., 2020) | Urban scene reconstruction、novel-view synthesis、3D 物件偵測與追蹤 | 1,000 個城市場景，每段約 20 秒，6 個相機多視角影像 | Train：原始 700 個訓練場景；Val：從原始 validation split 中挑選 14 個代表性場景（涵蓋日/夜、晴/雨、靜止/直行/轉彎、不同車流密度），場景列表見 Appendix A；Test：論文未獨立切出 test split |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PSNR | Peak Signal-to-Noise Ratio，衡量渲染影像與真值之間的 pixel-level 強度誤差 | yes |
| SSIM | Structural Similarity Index Mapping，衡量結構相似度 | yes |
| LPIPS | Learned Perceptual Image Patch Similarity，衡量感知相似度 | yes |
| mAP (%) | 在 novel-view 渲染影像上以 UniAD 進行 3D 物件偵測（僅 vehicle 類）的平均精度 | yes |
| AMOTA (%) | 在 novel-view 渲染影像上以 UniAD 進行 3D 多物件追蹤（僅 vehicle 類）的平均指標 | yes |
| Inference Speed (per scene) | 對 $\approx 20$ 秒場景產生 4D Gaussians 的平均耗時 | no |

### 6.3 Training and Inference Settings

- Hardware：H800 GPUs，總計約 8 GPU-days（§4.2 Implementation Details）。
- Input resolution：將 nuScenes 原始 $1600 \times 900 \times 3$ 影像 resize 至 $518 \times 280 \times 3$（Appendix B）。
- Backbone：採用 VGGT 架構，DINOv2 patch size $p = 14$、token 維度 $d = 1024$、24 層 alternating-attention transformer；保留 camera token 與 4 個 register token，並將第 4、11、17、23 層的 token 餵入 GCPH 與 GPPH（Appendix B）。
- LoRA 設定：rank $r = 8$、scaling factor $\alpha = 32$（§3.2）。
- Loss 權重：$\lambda_{\text{percep}} = 0.05$、$\lambda_{l2} = 1.0$、$\lambda_{l1} = 0.85$、$\lambda_{\text{ssim}} = 0.15$、$\lambda_{\text{scale}} = \lambda_{\text{opacity}} = 0.01$（§4.2）。
- Optimizer：AdamW，gradient accumulation 8 steps（§4.2）。
- 兩階段訓練：(1) Single-frame pre-training 10 epochs，batch size 4、learning rate $2 \times 10^{-5}$、weight decay 0.01；(2) Dual-frame fine-tuning 2 epochs，batch size 2（§4.2）。learning rate schedule the paper does not specify。
- 訓練資料組裝：每個場景切成連續 6 frame clip（0.5 秒），第 1 與第 6 frame 為 context frame；project loss 以第 1 frame 作 target、第 2 frame 作 source；4D Gaussians 渲染至第 1–5 frame 的取樣機率為 [0.7, 0.3, 0.2, 0.1, 0.1, 0.05]（Appendix B）。
- 動態物件設定：對 car、truck、bus、trailer、construction vehicle 五類抽取 SAM2 mask 與運動向量（§4.2）。
- Depth clamp：GCPH 將 depth 限制在 $[1.5\,\text{m}, 110\,\text{m}]$（Appendix B）。
- 推論：相鄰 temporal segment 共享 context frame，採用 caching 機制消除冗餘計算；evaluation 時對所有方法統一以 $518 \times 280$ 解析度評估（§4.1、§4.2）。
- Evaluation 取樣：以 12 Hz key frame 為基準，每隔 6 frame（即 0.5 秒）為 context frame 用於 reconstruction，其餘 frame 作為 novel-view synthesis 的 ground truth；3D perception 任務則對 ego-vehicle trajectory 施加 $\pm 1$、$\pm 2$、$\pm 3$ m 的橫向位移，並以 2 Hz 餵入 UniAD（§4.1）。

### 6.4 Main Results

Table 1（nuScenes Reconstruction & Novel-View Synthesis）：

| Method | Recon PSNR | Recon SSIM | Recon LPIPS | NVS PSNR | NVS SSIM | NVS LPIPS | Inference / scene | Notes |
|---|---|---|---|---|---|---|---|---|
| Street Gaussians | 29.18 | 0.8824 | 0.1658 | 22.98 | 0.6959 | 0.2948 | 31 min | Per-scene optimization |
| PVG | 29.58 | 0.8839 | 0.2200 | 23.48 | 0.6919 | 0.2897 | 23 min | Per-scene optimization |
| DeformableGS | 28.93 | 0.8832 | 0.1610 | 23.73 | 0.6919 | 0.2342 | 46 min | Per-scene optimization；NVS LPIPS 為 baseline 中最佳 |
| OminiRe | 29.42 | 0.8853 | 0.1577 | 23.01 | 0.6885 | 0.2762 | 35 min | Per-scene optimization |
| Drivingforward | 22.83 | 0.7650 | 0.2563 | 21.88 | 0.6866 | 0.2979 | 5 s | Feed-forward baseline |
| **ReconDrive (Ours)** | **32.66** | **0.9589** | **0.0618** | **23.99** | **0.7234** | 0.2591 | 15 s | 9 個指標中贏 8 個；NVS LPIPS 略遜於 DeformableGS（0.2591 vs 0.2342） |

Table 2（3D Perception on Novel-View Rendered Scenes，offsets $\{0, \pm 1, \pm 2, \pm 3\}$ m）：

| Method | mAP (%) | AMOTA (%) |
|---|---|---|
| Street Gaussians | 14.6 | 11.9 |
| PVG | 18.5 | 14.4 |
| DeformableGS | 16.4 | 13.4 |
| OminiRe | 16.1 | 12.9 |
| Drivingforward | 23.4 | 13.3 |
| **ReconDrive (Ours)** | **26.7** | **18.9** |

主要觀察：ReconDrive 在 reconstruction 三個指標全面超越所有 baseline；在 NVS 上 PSNR/SSIM 為最佳，LPIPS 僅次於 DeformableGS；推論速度 15 s 比 per-scene optimization 方法快約兩個量級，但比 DrivingForward 的 5 s 慢 3 倍。

### 6.5 Ablation Studies

- **Spatial misalignment of original VGGT（Appendix C，Fig. 5–6）**：將原始 VGGT 直接套用於 nuScenes 多視角影像，比較其 point map 與 LiDAR ground truth 的距離分布。結果顯示存在顯著的 metric scale 偏移，但施加 global scale factor 後可與 LiDAR 對齊。此實驗用以動機化 GCPH 中加入 calibrated sensor parameter 的設計。屬於診斷性實驗，但只示意「scale 不對齊」這個既有現象，並未直接消融 GCPH 是否解決它（例如未提供「ReconDrive 不加 calibration」的 PSNR/SSIM 對照），因此偏向動機性說明而非完整的 component ablation。
- **Temporal input frames（Appendix D，Table 3）**：比較 single-frame 輸入的 ReconDrive-S 與 two-frame 輸入的 ReconDrive。在 NVS 上 PSNR 從 23.54 → 23.99（+0.45）、SSIM 從 0.6940 → 0.7234（+0.0294）、LPIPS 從 0.3177 → 0.2591（−0.058）。此 ablation 驗證「multi-frame fusion 擴展可重建視野」這一論點，方向正確但只覆蓋輸入 frame 數一個維度。
- **Dynamic Gaussian rendering（Appendix E，Fig. 7）**：將 dynamic Gaussians 隨時間渲染、遮蔽 static Gaussians，視覺上顯示移動車輛位置與 ground truth 對齊。屬於 qualitative sanity check，未提供量化指標。

整體而言，ablation 涵蓋面偏窄：論文宣稱的三大貢獻（Hybrid Gaussian Prediction Heads、Static-Dynamic 4D Composition、segment-wise temporal fusion）並未各自配對量化 ablation。Hybrid head 中「concatenate raw image」、「將 calibration 注入 GCPH」、LoRA fine-tuning、各個 loss 項（$L_{\text{percep}}$、$L_{\text{project}}$、$L_{\text{norm}}$）、segment 切分長度、dynamic mask 來源（SAM2 vs GT bbox）等關鍵設計皆無 ablation 對照。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 比較了 4 個 per-scene optimization SoTA（Street Gaussians、PVG、DeformableGS、OmniRe）與 feed-forward SoTA DrivingForward，且在 9 個指標中贏 8 個（§4.2、Tab. 1–2）。
- [partial] Has cross-task / cross-dataset evaluation — 任務面涵蓋 reconstruction、novel-view synthesis 與 3D detection/tracking 三種，但資料集只用 nuScenes 一個，未在 Waymo 或 KITTI 等其他駕駛資料集上驗證跨資料集泛化性（§4.1）。
- [partial] Has ablations that diagnose the new components — 只有 temporal frame 數一個量化 ablation（Tab. 3）與 VGGT scale 動機性分析（Fig. 5），三大 contribution 中的 Hybrid Prediction Heads 內部設計、static-dynamic composition、segment-wise fusion 皆未獨立量化消融。
- [missing] Has a scaling study — 未呈現 backbone 規模、segment 長度、context frame 數量超過 2、訓練資料量等任何 scaling 維度的實驗。
- [covered] Has an efficiency / wall-clock comparison — Tab. 1 報告 per-scene 推論時間（ReconDrive 15 s vs per-scene optimization 23–46 min vs DrivingForward 5 s），並於 §4.2 Inference Efficiency 段落明確比較（§4.2）。
- [missing] Reports variance / standard deviation / multiple seeds — 所有指標皆為單次數值，未提供標準差、信賴區間或多種子重跑結果。
- [partial] Releases code / weights / data sufficient for reproducibility — 摘要列出 GitHub 連結 `https://github.com/TuojingAI/ReconDrive`，但論文本身未說明釋出範圍是否包含預訓練權重、14 個 validation scene 的處理腳本與 UniAD 評測 pipeline；nuScenes 為公開資料集，可獨立取得。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1 — feed-forward 4DGS 在重建上超越 per-scene optimization。** *Partially supported.* Tab. 1 的 reconstruction PSNR/SSIM/LPIPS 全面領先,但 reconstruction 評估幀即訓練時看到的 context frame,這對 feed-forward 是 in-distribution rendering、對 optimization 則是 fitting target,雙方並非完全對等;在嚴格意義上 novel-view synthesis 結果(Tab. 1 右半)才是公平比較,而這裡 ReconDrive 僅領先 DeformableGS 0.26 dB PSNR、且 LPIPS 還低於 DeformableGS,「八/九 metrics 第一」的敘事被 reconstruction 列拉抬。
- **Claim 2 — Hybrid Gaussian Prediction Heads 同時解決 photometric deficiency 與 calibration mismatch。** *Overclaimed.* Appendix C(Fig. 5–6)只證明 raw VGGT 與 LiDAR 存在 metric scale misalignment,但沒有 ablation 拿掉 GCPH 的 calibration 注入或拿掉 GPPH 的 image shortcut 來量化各自貢獻;設計在邏輯上合理,實證上未被切開驗證。
- **Claim 3 — Static-Dynamic 4D Composition 顯式表達運動。** *Partially supported.* Appendix E 的 Fig. 7 視覺上呈現動態車輛位置正確,Tab. 2 的 AMOTA 18.9% 也高於所有基線,但 velocity 在實驗中是用 nuScenes 3D bbox 兩幀位移得到(Sec. 3.3, p. 5),「無標註時用兩幀 Gaussian center」的替代方案未在任何資料集上測試,因此 feed-forward 的動態表達在沒有 ground-truth box 時的可用性未被證明。
- **Claim 4 — segment-wise temporal fusion 加 LoRA 讓 frozen VGGT 可擴展到長序列。** *Partially supported.* Sec. 4.2 Inference Efficiency 提到透過 cache 相鄰 segment context frame 達 15s/scene,這驗證了效率;但論文沒有展示「不分段」與「不同 segment 長度」的對照,也沒有量化 LoRA 對 generalization 的影響(例如 full fine-tune vs LoRA 的對比)。
- **Claim 5 — feed-forward 路線可擴展到大規模都市重建。** *Overclaimed.* 唯一資料集 nuScenes、僅 14 個 validation scene、單城市;論文 Sec. 5 自己也承認需擴展到更多 geography 與天氣,因此「scalable to large-scale」目前只是 hours→seconds 的時間意義上的可擴展,而非地理或分布意義上的可擴展。

### 7.2 Fundamental Limitations of the Method

**動態建模對 3D bbox annotation 的隱性依賴。** Eq. 3 的 velocity 估計需要兩幀同 instance 的 3D location,這在實作上由 nuScenes annotation 提供;雖然作者口頭提出「兩幀 Gaussian center 也可」的替代,但 Gaussian center 的 instance correspondence 本身需要時序匹配,而 SAM2 在駕駛場景下對快速橫向穿越的 instance ID 一致性並不可靠。換言之,在沒有 LiDAR box 也沒有可信 video instance segmentation 的部署場景,Static-Dynamic Composition 會退化為靜態重建。

**Per-segment 線性運動 + center-moving 的表達上限。** Eq. 2 的 $\mu_i(t) = \mu_{i,init} + v_i \cdot (t - T_s)$ 假設 segment 內等速,且 Gaussian 的 rotation $R_i$ 與 scaling $s_i$ 在時間上恆定。對於轉向中的車輛、行人擺臂、被遮擋後重出現的物件,這個 kernel 結構在原理上無法表達;這不是訓練資料或損失函數能彌補的問題,而是表示式本身的限制。

**Reconstruction 指標的測試協定混淆。** Tab. 1 用「每 6 幀取 1 幀作為 context」同時當輸入與 reconstruction GT,等於要求 feed-forward 模型在它「看過的這一幀」上重渲染,這對 ReconDrive 是 in-distribution 任務;對 per-scene optimization 雖也在 context frame 上 fit,但兩者的「該指標反映什麼」並不相同。在現行設定下,「重建超越 optimization」的敘事在方法學上偏脆。

**Foundation backbone 的 metric scale 殘留問題。** Appendix C 揭示 VGGT 的 point map 與 LiDAR 存在 scale 不一致,而 ReconDrive 透過將 calibration 注入 GCPH 並讓 depth-to-3D 在 ego frame 完成來繞過這點。這個解法依賴每一台相機都有準確的 intrinsic/extrinsic;當部署到沒有精確 calibration 的車隊資料時,GCPH 的修正會反過來放大 calibration 雜訊,這是繼承自設計選擇的結構性脆弱性。

### 7.3 Citations Worth Tracking

- **VGGT (Wang et al. 2025)** — backbone 本體,要評估 ReconDrive 修改的合理性必須先讀懂 alternating-attention 與 DPT head 的原設計動機。
- **Street Gaussians (Yan et al. 2024)** — 主要 per-scene 對照,理解其 static-dynamic 拆解與 per-vehicle Gaussian model 對照 ReconDrive 的 SAM2-based 方案差異。
- **STORM (Yang et al. 2025)** — 同類 feed-forward + transformer + per-frame Gaussian + scene flow 的代表,雖未進 Tab. 1,但概念上是 ReconDrive 最直接的 prior baseline。
- **WorldSplat (Zhu et al. 2025)** 與 **DGGT (Chen et al. 2025a)** — diffusion-based 4D 駕駛重建的最新替代路線,評估「foundation feed-forward」相對「diffusion refinement」哪一邊在品質-延遲 trade-off 上勝出時必讀。
- **SAM2 (Ravi et al. 2024)** — 動態管線唯一的非可學部件,其 mask 邊界與 instance ID 一致性直接決定 ReconDrive 動態 Gaussian 的品質上限。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在沒有 nuScenes 3D bbox annotation 的資料集(例如 raw 車隊影片)上,velocity 改用兩幀 Gaussian center 對應時,Tab. 2 的 mAP/AMOTA 會掉多少?
- [ ] 拆解 ablation:單獨拿掉 GPPH 的 image shortcut、單獨拿掉 GCPH 的 calibration 注入、單獨拿掉 static-dynamic composition,各自對 PSNR/SSIM 的貢獻是多少?
- [ ] Tab. 1 的 reconstruction 評估在「context frame ≠ 訓練輸入」的協定下(例如 leave-one-out),feed-forward 是否仍領先 per-scene optimization?
- [ ] 跨資料集泛化:在 nuScenes 訓練、Waymo/Argoverse2 zero-shot 評估時,ReconDrive vs DrivingForward 的差距會擴大還是縮小?
- [ ] LoRA $r=8$ 是否飽和?提升至 $r=32$ 或 full fine-tune 對 PSNR 與 generalization 的影響為何?
- [ ] Segment 長度從 0.5s 拉到 2s/5s 時,線性運動假設何時開始顯著拖累 AMOTA?
- [ ] 含 SAM2 mask 與 ego pose 處理的 end-to-end latency 是多少,而不只是 Gaussian 生成的 15s?

### 8.2 Improvement Directions

1. **新增 calibration-noise robustness ablation。** 在 GCPH 的 intrinsic/extrinsic 上人為加入 0.5–2% 雜訊,量化 PSNR 退化曲線。理由:第 7.2 節指出 GCPH 把 calibration 視為硬約束,真實車隊資料 calibration 多數不精準,此實驗可暴露結構性脆弱性並指引下一版設計是否需要 calibration refinement head。
2. **Velocity self-supervision 路線實驗化。** 把論文順帶提到的「兩幀 Gaussian center 推 velocity」做成主路徑,並在無 3D box 的資料集(Argoverse 2 sensor split)報告 Tab. 2 同樣指標。理由:這是 feed-forward 賣點被獨立驗證的關鍵實驗,直接回應 7.1 Claim 3 的 overclaim 風險。
3. **將線性 Gaussian motion 換成短時 polynomial 或 SE(3) spline。** 在 Eq. 2 上加二次項 $\mu_i(t) = \mu_{i,init} + v_i (t-T_s) + \tfrac{1}{2}a_i (t-T_s)^2$,並讓 rotation 也可學到 angular velocity。理由:7.2 第二段的 kernel 表達上限,加上作者自己在 Sec. 5 承認線性假設不足,二次擴展是最低成本的下一步。
4. **解耦 reconstruction 評估協定。** 建議下一版 benchmark 使用 hold-out 的 5/6 幀做 reconstruction 與 novel-view synthesis 的同協定評估,讓 feed-forward 與 per-scene optimization 真正在「未見幀」上比較。理由:現行 Tab. 1 的雙重協定混淆了「對輸入幀重渲染」與「真泛化」,也是 4.2.2 與 7.1 都點到的問題。
5. **整合 video instance tracking 取代 SAM2 per-frame mask。** 採用 SAM2 的 video mode 或 DEVA 等具備 temporal ID consistency 的方法。理由:作者自己列為 future work,且 Tab. 2 detection-tracking gap (26.7 → 18.9) 也暗示 instance 一致性是當前瓶頸,屬中等成本高回報的改動。
6. **Edge-deployable backbone 替換實驗。** 將 VGGT(24-layer DINOv2-L)替換成更輕量的 ViT-S 或 distilled VGGT,並報告 PSNR–latency Pareto 曲線。理由:Sec. 5 自承部署延遲未達 real-time,且 ablation 可協助下游使用者判斷模型壓縮的損益點。
