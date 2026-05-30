<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# VGGT-World — VGGT-World: Transforming VGGT into an Autoregressive Geometry World Model

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | VGGT-World |
| Paper full title | VGGT-World: Transforming VGGT into an Autoregressive Geometry World Model |
| arXiv ID | 2603.12655 |
| Release date | 2026-03-13 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.12655 |
| PDF link | https://arxiv.org/pdf/2603.12655 |
| Code link | — |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Xiangyu Sun | UQMM Lab, The University of Queensland | [link](https://scholar.google.com/citations?user=Jf8vi_sAAAAJ&hl=en) | first author |
| Shijie Wang | UQMM Lab, The University of Queensland | — | co-author |
| Fengyi Zhang | UQMM Lab, The University of Queensland | — | co-author |
| Lin Liu | Beijing Jiaotong University | — | co-author |
| Caiyan Jia | Beijing Jiaotong University | — | co-author |
| Ziying Song | Beijing Jiaotong University | — | co-author |
| Zi Huang | UQMM Lab, The University of Queensland | — | co-author |
| Yadan Luo | School of EECS, The University of Queensland (UQMM Lab) | [link](https://luoyadan.github.io/uqmm/) (verified: [link](https://eecs.uq.edu.au/profile/2417/yadan-luo)) | corresponding author |

### 1.2 Keywords

geometry world model, VGGT, flow matching, autoregressive rollout, z-prediction, depth forecasting, geometry foundation model, latent world model, flow forcing

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al.) | base model | Frozen geometry foundation model whose layer-4 latent tokens VGGT-World repurposes as the predictive world state. |
| DUSt3R (Wang et al.) | predecessor | Early feed-forward multi-view reconstruction model that defined the GFM paradigm leading to VGGT. |
| Cosmos (NVIDIA) | baseline | 12B video world model in VAE latent space; main efficiency and forecasting baseline (3.6-5x slower). |
| Gen3R | baseline | 9B geometry-aware video generator with 3D priors; primary geometry-forecasting baseline compared on KITTI/Cityscapes/TartanAir. |
| Wan2.1 | baseline | Representative bidirectional video diffusion world model used as VAE-latent video generation reference. |
| Geometry Forcing | influence | Geometry-aware video diffusion injecting 3D priors; motivates moving prediction fully into geometry latent space. |
| DINO-World / DINO-Foresight | influence | Latent world models forecasting frozen DINO features; inspires VGGT-World's choice of frozen-feature predictive state. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於「世界模型 (world model)」中的幾何預測問題,屬於 3D 場景理解與未來預測 (future forecasting) 的交叉領域。傳統視訊世界模型 (video world model) 透過 VAE latent 重建未來 RGB 影格,將外觀資訊與場景幾何耦合,雖具視覺真實感卻常產生幾何不一致的結果,且訓練成本極高 (如 Cosmos 需要數千萬 GPU 小時)。作者主張改以凍結的 geometry foundation model (GFM,如 VGGT) 之 latent token 作為「世界狀態」,僅學習其時間演化,稱之為 geometry world modeling。研究範疇涵蓋深度預測 (depth forecasting)、3D 點雲預測、相機軌跡保持與計算效率分析,並針對高維 ($d=1024$) 幾何特徵空間下 flow matching 的最佳化困難與自回歸 rollout 的暴露偏差 (exposure bias) 提出解法。實驗於 KITTI、Cityscapes、TartanAir 進行,任務橫跨短期與中期未來幾何預測。

### 2.2 Domain Tags

- 3D vision
- world models
- future video / geometry forecasting
- generative modeling (flow matching)
- autonomous driving / embodied AI

### 2.3 Core Architectures Used

- **VGGT (frozen geometry foundation model)**:作為世界狀態的特徵抽取器與解碼器,提供 layer-4 的 token 作為 latent state,並以凍結的 $\Phi_{\text{dec}}$ 與 3D heads $\mathcal{H}_{\text{3D}}$ 將預測 token 解出 depth、point map 與相機資訊。
- **Temporal flow transformer (本論文提出, 0.43B 參數)**:輕量化、可訓練的時間動態模型,採 dual-stream causal processor $F_{\text{dual}}$ 加上 single-stream spatial denoiser $F_{\text{single}}$ 的雙階段設計,負責在凍結 VGGT latent 空間中預測下一個 chunk 的幾何狀態。
- **Flow matching with z-prediction**:以連續時間 flow matching 為生成框架,但將傳統 v-prediction 換成 clean-target z-prediction,以提升高維 ($d=1024$) 幾何空間中的 SNR 與訓練穩定性。
- **Chunk-wise autoregressive rollout**:以固定大小 sliding-window 的 chunk 為單位進行自回歸預測,維持常數記憶體並支援任意長 horizon 的幾何預測。
- **Two-stage latent flow-forcing curriculum (本論文提出)**:第一階段 teacher-forcing 訓練建立 vector field,第二階段以模型自身 ODE 部分去噪 rollout 作為混合條件 $\mathbf{c}_{i+1}^{\text{mix}}$,並對混合比 $\lambda$ 採線性退火排程,以緩解 exposure bias。
- **adaLN-conditioned transformer blocks**:以 Adaptive Layer Normalization 注入連續 flow time $\tau$,在 $L_d=8$ 個 dual-stream block 與 $L_s=8$ 個 single-stream block 中分離時間推理與空間細化。

### 2.4 Core Argument

作者主張現行視訊世界模型在幾何預測上失敗的根本原因不在「預測機制」本身,而在「世界狀態的表徵選擇」。將狀態壓縮到 video VAE latent ($d=16$) 雖然便於生成像素,但目標函數聚焦光度細節 (texture、lighting),與 3D 結構僅鬆散耦合,因此解碼後的未來影格雖視覺合理,場景佈局與動態物體位置卻可能嚴重失真。既有「幾何感知」的視訊生成 (Gen3R、GeoWorld、Geometry Forcing 等) 仍以 RGB 重建為核心,只是注入幾何先驗,並未直接預測 3D 幾何演化,且訓練成本仍極高。基於此,作者主張應直接在 GFM (VGGT) 的特徵空間中建模世界狀態,因為該空間已內建多視角幾何、空間一致性與度量結構,是更適合 3D 預測的 latent。然而 VGGT 特徵壓縮率低、維度高 ($d=1024$),直接套用 flow matching 的 v-prediction 會崩潰,且自回歸 rollout 會累積 exposure bias。為此,他們以 z-prediction (clean-target) 取代 v-prediction 以提升 SNR,並設計兩階段 latent flow-forcing curriculum 讓模型逐步適應自身產生的歷史。此設計不需訓練 video VAE 也不需微調重型生成 backbone,只訓練 0.43B 參數的輕量 temporal flow transformer,並以凍結 VGGT decoder 與 3D heads 解出 depth、point map 等輸出,因此該解法在邏輯上是「狀態空間錯置」這一根本病因的必然修正。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(210 words)

標題「VGGT-World: Transforming VGGT into an Autoregressive Geometry World Model」直白點出全文核心：把一個觀察型的 geometry foundation model（VGGT）改造成具備未來預測能力的 world model，且以 autoregressive 方式運作。Abstract 在第一句就建立論文的張力——現有 video-generation world models 把模型容量耗在 photometric 細節上，預測結果在幾何上卻常常不自洽——這個矛盾是後續所有設計選擇的動機根源。第二句拋出論文的代位方案：完全跳過 video generation，改為預測 frozen GFM features 在時間上的演化。接著用一句點明做法：把 frozen VGGT 的 latent tokens 當成 world state，訓練一個輕量的 temporal flow transformer 自回歸預測其未來軌跡。Abstract 隨即坦承在 $d=1024$ 的高維特徵空間裡會遇到兩個具體障礙——standard velocity-prediction flow matching 會崩潰、autoregressive rollout 會累積 exposure bias——並對應給出兩個技術回應：以 clean-target (z-prediction) parameterization 提高訓練 SNR，以及 two-stage latent flow-forcing curriculum 逐步把模型暴露在自己 partially denoised 的 rollouts 上。最後以三組實驗結果（KITTI、Cityscapes、TartanAir）量化說服力：在 depth forecasting 上勝過最強 baselines，速度快 3.6–5×，可訓練參數僅 0.43B。Abstract 完成「問題—觀點轉換—兩個工程關鍵—成果」四段式論證，已為後續 Introduction 鋪好結構模板。

### 3.2 Introduction

(910 words)

Introduction 採取「現況→缺口→反思→提案→預告貢獻」的標準五段推進。第一段先肯定 GFM（VGGT、DUSt3R 等）已能從單目 RGB 一次性恢復 camera pose、depth、point cloud，並指出這對 embodied agent 的 navigation 與 manipulation 有幫助；但隨即強調這類模型本質上是「observational」，只能解釋已見之景，無法預測未來——而 planning 與 control 在動態環境中需要的是 foresight。這一句話定下整篇論文的問題框架：geometry 模型缺一個「時間維度」。

第二段把目光轉向看似自然的解法——video-generation world models（Wan、MovieGen、Cosmos）——並用 Fig. 1 的失敗案例（破碎的 sheet-like 表面、cyclist 被錯置在 ego vehicle 前方）強調 video VAE latent 與 3D 結構之間是 loosely coupled。即便是注入 geometric prior 的 Gen3R、GeoWorld、GeometryForcing、GeoVideo，目標仍是 future RGB reconstruction 而非直接預測 3D 演化；同時點名 Cosmos 需要數千萬 GPU-hours、Gen3R 即使 finetune VAE 也要 24 張 H20 GPU 多日，宣告此 paradigm 對學術界 impractical。這段把 video-centric 路線徹底「降級」為「貴而不準」。

第三段是哲學上的轉折：作者主張癥結不在 forecasting mechanism，而在 world state representation 應該換掉。GFM features 已經內建 multi-view geometry 與 metric structure，是更合適的預測狀態空間。作者把這一觀點命名為 geometry world modeling，並對應引出 VGGT-World 的具體設計：抽取已觀測 frame 的 tokens 作為條件，訓練 temporal flow transformer 以 chunk-wise 方式自回歸預測未來 camera 與 patch tokens，再交給 frozen VGGT decoder/heads 解碼出 depth、point map 與 camera-motion cues。

第四段把 Abstract 中的兩個技術困難正式攤開：相比 video VAE 的 $d=16$，VGGT state 的 $d=1024$ 弱壓縮、優化困難；而 autoregressive rollout 又會引入 exposure bias，因為下一 chunk 必須條件於已偏離的歷史。對應提出 z-prediction parameterization 與 two-stage flow-forcing curriculum 作為解方，預告 §3.2 與 §3.3。

最後一段以實驗成果收束：跨 KITTI、Cityscapes、TartanAir 三個資料集，在 depth forecasting 上 mean AbsRel 相對最強 baseline 降低達 21% 與 32%、$\delta_1$ 在短中期皆改善；效率上比 Cosmos (12B) 與 Gen3R (9B) 快 3.6–5×，僅需 0.43B 可訓練參數。Introduction 因此預先把 §4 的核心數字搬到讀者眼前，為後續方法鋪墊「值得讀下去」的動機。

### 3.3 Related Work / Preliminaries

(620 words)

Related Work 切成三條敘事線，目的不是平鋪百科，而是把 VGGT-World 在學術地圖上「定位」出來。第一條是 Geometry Foundation Model：作者先回顧從 SfM、Bundle Adjustment 等迭代式幾何優化到端到端 feed-forward 重建（DUSt3R）的 paradigm shift，再談到 VGGT、π³、MapAnything 等近期 GFM 已能在單一 forward pass 中產出 camera pose、depth、point cloud 並支援彈性輸入輸出。但作者馬上下結論：這些模型仍受限於「observational input」，能解釋現在卻無法 forecast 未來——這正是論文要補的缺。

第二條是 Video Generation：作者羅列 SVD、Sora、Cosmos、Wan2.1 等 frontier 系統，承認其在 spatiotemporal prior 上的成就，但指出它們主要在 pixel 或 compressed video latent space 操作，缺乏顯式 3D 結構，因此長 horizon 下幾何不一致。即便是注入 geometric prior 的 Geometry Forcing、GeoWorld、Gen3R 等變體，仍仰賴 VAE-compressed latent，把 geometry 與 appearance 糾纏在一起，限制了 causal 3D dynamics 的表達。這條線把競爭對手鎖在「重、貴、不夠幾何」的位置。

第三條是 Latent World Model：作者整理近年用 vision encoder feature space 取代 VAE latent 的趨勢——DINO-Foresight 用 masked feature transformer 預測 frozen DINO tokens、DINO-World 直接在 DINOv2 特徵空間學 video dynamics、LAW 與 WOTE 在 BEV latent 中預測。這個 trend 帶出一個反覆出現的觀察：「predictive performance 取決於 latent 的選擇而非像素重建」。但作者刻意挑明 DINO 系列以 semantic invariance 為目標，並不顯式編碼 3D 幾何；GFM 反之同時包含 multi-view geometry、spatial consistency、metric structure，才是更合理的 latent backbone。

這三條線完成一個三角推論：GFM 缺 forecasting、video generation 太重且不夠幾何、latent world model 路線正確但 latent 選錯。VGGT-World 正好填在三者交點——「在 geometry foundation feature space 裡做 autoregressive world modeling」。Related Work 的最後一句直接寫出此立場宣示，把 §3 的方法部分自然接續。整體而言，這節並未鋪陳 preliminaries 公式，而是用三條 narrative 把方法選擇的理由「先論證好」，讓 §3 可以直接從 problem formulation 開始。

### 3.4 Method (overview narrative)

(2280 words)

§3 Our Approach 的 overview 段先把 VGGT-World 的整體框架以一句話定型：把 world modeling 重新定義為「在 frozen GFM 的 latent space 裡預測 geometry state 的時間演化」，而非重建未來 RGB。接著刻意把 spatial representation learning 與 temporal dynamics modeling 解耦——frozen VGGT encoder 抽取每一 frame 的 deterministic geometry state（§3.1）、輕量 temporal flow transformer 預測未來演化（§3.2）、frozen VGGT decoder 加原 3D heads 把預測軌跡解碼回幾何輸出。這樣的拆分一方面避免訓練 video VAE 或 fine-tune 重型 video backbone，另一方面保留了與 pretrained geometry decoder 的相容性。最後預告 §3.3 的 two-stage latent flow-forcing curriculum 是為了縮小 recursive rollout 的 train-test mismatch。

§3.1 Geometry World Modeling via Autoregressive Flow 把問題形式化。作者先說明 VGGT 共有 $L=48$ 個 transformer block（24 self-attention + 24 global-attention），其 frozen 3D head 會消費來自 layer $\{4, 11, 17, 23\}$ 的多尺度 feature；若預測更深層會丟棄 head 必需的早期表徵且無法回補，因此選擇最早的 decoder-compatible layer L4 作為預測狀態。據此把 $\Phi$ 切成 deterministic geometry encoder $\Phi_{\text{enc}}$（layer 0–4）與 feature propagator $\Phi_{\text{dec}}$（layer 5–47）。每個 frame 經過 encoder 後產生 $\mathbf{z}_t \in \mathbb{R}^{N \times d}$，其中 $d=1024$、$N = 5 + N_p$（5 個 special token 加 $N_p$ patch token）。Rollout 採 chunk-wise 設計：給定觀察歷史 $\mathbf{z}_{1:k}$，未來 horizon 切成 $S$ 個長度 $m$ 的 chunk，joint distribution 因式分解為 $\prod_{i=1}^{S} p(\mathbf{Z}_i \mid \mathbf{c}_i)$。為了維持固定 context 大小、避免 memory 爆炸，模型不累積歷史，而是以 sliding window 方式取最近 $k$ 個 frame 當條件 $\mathbf{c}_{i+1} = \hat{\mathbf{Z}}_i$。最後一個亮點是 3D Joint Decoding with Forecasted Horizon：把 rollout 出來的未來 chunks 與初始稀疏 context 拼成 $\mathbf{z}_{1:T}^{\text{full}}$ 一起餵進 $\Phi_{\text{dec}}$ 與 3D heads，「預測未來反過來改善現在的幾何估計」，因為長 horizon 的 world model 滾動本身就是時間正則化器。

§3.2 Chunk Transition in High-Dimensional Geometry Space 處理 $p(\mathbf{Z}_i \mid \mathbf{c}_i)$ 的具體建模。預設工具是 continuous-time flow matching：probability path $\mathbf{Z}_{i,\tau} = (1-\tau)\mathbf{Z}_i + \tau \epsilon$、ODE 由 velocity $v_\theta$ 主導。但作者透過 Fig. 2 觀察到在 $d=1024$ 的 VGGT latent space 裡，4k 次迭代後 v-prediction 仍呈雜訊狀，原因是 valid geometry state 只佔 ambient space 的結構化子集，isotropic Gaussian 主要把樣本擾出 manifold，使得 velocity estimation ill-conditioned。一個直觀替代是另外學 dimensionality reduction，但這會破壞與 frozen VGGT head 的對齊、毀掉 zero-shot 幾何先驗。作者因此選擇 z-prediction：直接預測 clean target latent $\mathbf{Z}_i$，提供更強的 denoising signal。實作上把網路 $F_\theta$ 拆成 dual-stream causal processor $F_{\text{dual}}$（早期 $L_d$ 層 double-stream block，cross-attend 到歷史 $\mathbf{c}_i$ 吸收 temporal physics）與 single-stream spatial denoiser $F_{\text{single}}$（後 $L_s$ 層 single-stream block，僅在 target chunk 內部做 self-attention 進行空間細化）。Continuous flow time $\tau$ 透過 adaLN 注入每一 block。這個切分呼應了近期關於 video diffuser 中 causality 與 spatial denoising 可分離性的分析。

§3.3 Latent Flow Forcing Curriculum 解 exposure bias。Stage 1 是 pure teacher-forcing：context $\mathbf{c}_i = \mathbf{Z}_{i-1}$ 為 oracle，loss 為 weighted z-prediction（式 9）。但 inference 時 context 來自模型自己的 $\hat{\mathbf{Z}}_{i-1}$，導致 train-test mismatch。Stage 2 採 trajectory-consistent flow forcing：把前一 chunk 從 noise 起 ODE-rollout，但僅積分到 $\tau_{\text{mid}}$ 得到 partially denoised state $\hat{\mathbf{Z}}_{i,\tau_{\text{mid}}}$，再以 $\lambda \in [0,1]$ 與 ground-truth 線性插值組成 mixed condition $\mathbf{c}_{i+1}^{\text{mix}}$（式 11）。優化目標 $\mathcal{L}_{\text{S2}}$（式 12）讓模型在 partially denoised history 條件下預測 clean target。為了穩定，作者把 $\lambda$ 從 0 線性 anneal 到 1，因為 mixed condition 注入的 variance 與 $\lambda^2 \mathbb{E}[\|E_i\|^2]$ 成正比，初期 rollout error 大，太高的 $\lambda$ 會違反 step-wise KL penalty 並使 ELBO 崩潰；隨訓練進行，rollout error 衰減，$\lambda$ 才安全地推向 inference-time 分佈。Appendix Theorem 1 進一步證明此目標等價於對 uncorrupted data likelihood 的 sequential ELBO 下界，curriculum 正是維持下界 tight 的條件。

### 3.5 Experiments (overview narrative)

(1860 words)

§4 Experiments 以三組資料集、三類 baseline、四類任務組成 evaluation 矩陣，並把所有對照都收斂到「geometry-centric latent forecasting 是不是真的更好」這個核心問題。Dataset 部分先列 Cityscapes（2,975 train / 500 val、30 frames、16 FPS、1024×2048）、KITTI（143 train / 13 val、512×1382、10 FPS）、TartanAir（Unreal Engine 合成、約 700k frames、室內外混合，依 Gen3R 的 90/10 split）。實作層面用 1 張 RTX Pro 6000 (96 GB)、AdamW、學習率 $2 \times 10^{-4}$、weight decay 0.05、$\ell_2$ gradient clipping = 1.0；Stage 1 batch size 64、Stage 2 batch size 48；初始 chunk size 為 4、autoregressive rollout stride 為 1；flow transformer 採 $L_d = 8$ double-stream + $L_s = 8$ single-stream，特徵維度 $d=1024$ 不壓縮。

評估指標方面，depth 用 mean AbsRel 與 $\delta_1$，並在 Cityscapes 上分 short (3 frames, 187.5 ms) 與 mid (9 frames, 562.5 ms)、KITTI 上分 short (2 frames, 200 ms) 與 mid (6 frames, 600 ms) 兩種 horizon。Point cloud 沿用 Gen3R 協議：先以 Umeyama similarity 對齊預測與 GT，再用 Farthest Point Sampling 取 20k 點，計算 Accuracy、Completeness、Chamfer Distance。Baselines 三類：pixel-space 2D generation（Cosmos 4B/12B、VISTA fine-tuned）、latent-space 2D generation（DINO-Foresight）、geometry-aware generation（Aether、WVD、Gen3R），並加上 Copy-Last 作為 trivial 基準。

§4.1 Depth Forecasting 是論文最核心的賣點。KITTI 上 VGGT-World 在所有 horizon 都拿到最佳結果，mean $\delta_1$ 達 94.0% / 89.4%，AbsRel 降到 0.065 / 0.098，相對最強 baseline 在 short / mid 各改善 21% / 15%。一個有趣的副觀察是 Cosmos 4B/12B 連 Copy-Last 都打不過，論證了「scaling video generation 而無 3D 先驗」會優先學 photometric realism；Aether 雖加了 geometry supervision，仍因 pixel-space representation 落後；DINO-Foresight 雖具競爭力，但其表現高度依賴 fine-tune 在 GT depth 上，而 VGGT-World 不需任何 GT depth fine-tune。Cityscapes 上挑戰更大——連續 ego-motion 與 perspective 變化使 short/mid gap 變寬——VGGT-World 仍把 AbsRel 與 $\delta_1$ 改進達 32%，證實在 metrically stable depth 下的優勢。Cityscapes 表還順帶做了 forcing ablation：no-forcing 已優於所有 baseline，加上 forcing 又進一步壓低 mid-term AbsRel，且 static $\lambda$（0.1 / 0.3 / 0.7）皆劣於線性 schedule。

§4.2 Point Map Forecasting 移到 TartanAir，在 1-view 與 2-view、是否提供 text/pose condition 的多種組合下與 Aether、WVD、Gen3R 比較。在 pose-free / text-free 設定下 VGGT-World 全面領先 Gen3R；即使對手吃了 explicit pose condition，仍然 competitive。w/o Forcing 與 full model 的差距驗證了 trajectory-consistent flow forcing 確實能緩解 rollout exposure bias。Fig. 4 的視覺對比也支撐這一點：Gen3R 在 wall、rooftop 等結構同質區崩成 disorganized geometry，VGGT-World 仍能維持 coherent 結構。

§4.3 Further Analysis 進一步從四個角度補強。第一，Forcing curriculum 的 ablation 顯示 dynamic schedule 比 static $\lambda$ 更穩，static 大 $\lambda=0.7$ 甚至會 catastrophically forget Stage 1。第二，Table 4 比較單張 frame 給 VGGT 的結果與 VGGT-World 在 short horizon 預測，後者在 Completeness 與 CD 上明顯更好——「foresight 反過來能改善 present perception」。第三，camera parameter forecasting 在 KITTI 與 TartanAir 經 Umeyama 對齊後，預測軌跡與 GT 全域結構相符，顯示 latent dynamics 隱式保留 camera motion cues。第四，Fig. 5 探討 horizon 長度的影響：CD 在第 7 frame 達 sweet spot，再長就劣化。Efficiency analysis 給出一個吸睛數字——Cosmos-12B 9.50 s/frame、Gen3R 6.90 s/frame、VGGT-World 1.9 s/frame，分別 5× 與 3.6× 提速；可訓練參數僅 0.43B，相對 Cosmos 的 12B 與 Gen3R 的 2.7B DiT + adapter 形成顯著對比。整節以「resource-constrained settings 下的 reproducibility 與 iteration speed」收尾，讓 efficiency 成為 quality 之外的第二條獨立論證線。

### 3.6 Conclusion / Limitations / Future Work

(140 words)

§5 Conclusion 的篇幅刻意短小，但結構嚴謹。首句把 VGGT-World 定位為「在高維 geometric latent space 直接做 world modeling 的 early attempt」，並以 contrast 強調儘管設計簡單、模型遠比 video-generation world models 輕，論文已在 forecasting quality 與 efficiency 兩條軸上同時超越對手；此論點呼應 §1 開頭挑戰 video-centric paradigm 的命題，使 introduction 與 conclusion 形成閉環。第二句把貢獻拉高到方法論層次：geometry-centric latent forecasting 是 full-frame generation 的有力替代路線。第三句補上一個被作者視為策略性的優勢——VGGT-World 不需要 GT depth 或 point cloud 監督，提供 scaling geometry world models 的彈性 foundation。最後一段未明確標 Limitations 而僅以 Future Work 作結：作者指出可加入 camera pose 與 action 條件以 enable richer conditioning，並提出 action-conditioned forecasting 對 embodied agent 的 controllable、interactive rollout 是自然延伸。完整的 limitations 與更詳盡的 future work 留給 Appendix Section D 處理。

## 4. Critical Profile

### 4.1 Highlights

- 把 world modeling 的「state space 選擇」獨立為核心問題,並主張 frozen GFM (VGGT) latent 比 video VAE latent 更適合 3D 預測,提供清楚的 paradigm 對比 (Fig. 1, §1)。
- 將 VGGT layer-4 的輸出鎖定為 predictive state,理由是「最早能餵回 frozen 3D heads 的 layer」,在不破壞 zero-shot geometric prior 的前提下定義了一個明確的 latent 介面 (§3.1)。
- 證實在 $d=1024$、weakly compressed 的 latent 空間中 standard v-prediction flow matching 直接崩潰,並以 z-prediction (clean-target) 取代;Fig. 2 顯示 4k iter 後 v-pred 仍是 noise,而 z-pred 已恢復出 PCA 對齊的結構。
- 提出 two-stage latent flow-forcing curriculum:Stage 1 teacher-forced、Stage 2 用 partially-denoised rollout 與 ground-truth 以 $\lambda$ 線性 anneal 混合 (Eq. 11),並在 Appendix A 給出 sequential ELBO 證明 (Theorem 1)。
- KITTI depth forecasting:short-term mean AbsRel 0.065、$\delta_1$ 94.0%,相對最強 baseline (DINO-Foresight) 改善 21%;mid-term 改善 15% (Table 1)。
- Cityscapes 在 short / mid 兩個 horizon 上 AbsRel 與 $\delta_1$ 最多改善 32%,於連續 ego-motion 場景中保持 metric 一致 (Table 2)。
- TartanAir 點雲預測在 pose-free / text-free 設定下 1-view Acc 1.16(對比 Gen3R 同設定 3.03),CD 2.85,證實 geometry-centric latent 對純幾何輸出有效 (Table 3)。
- Efficiency 顯著:1.9 s/frame,比 Cosmos-12B 快 5×、比 Gen3R 快 3.6×,可訓練參數僅 0.43B vs. Cosmos 12B 的全量更新 (Fig. 7)。
- 「forecast 未來反而改進當下感知」的反直覺結論:在 TartanAir 短水平上 Comp 1.06 vs. VGGT 1.22、CD 0.97 vs. 1.04 (Table 4),為 predictive perception 提供初步證據。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 自監督、幾何中心訓練在大規模、異質資料上的 scalability 尚未驗證 (§D Limitations,p.26)。
- 為了維持簡潔,刻意不接收 ground-truth depth、camera pose 或 action 等外部監督,因此「精細可控生成」能力有限,需後續加入 explicit conditioning (§D)。
- §3.3 末段亦自承 curriculum stability bound 高度依賴 rollout error 變異,過早給高 $\lambda$ 會讓 ELBO collapse,屬於設計上的脆弱點。

#### 4.2.2 Phyra-inferred

- KITTI / Cityscapes 的 depth 改善有相當部分可能來自「使用 frozen VGGT depth head」而非 temporal transformer 本身:Copy-Last (VGGT) baseline 在 KITTI 已達 $\delta_1$ 83.7% / 78.5% (Table 1),DINO-Foresight 又用的是 Depth Anything 而非 VGGT,跨方法比較把 decoder backbone 與 temporal modeling 兩個變因混在一起,看不出純粹的時序預測收益。
- TartanAir Table 3 中 VGGT-World 1-view 與 2-views 的 Acc / Comp / CD 數字完全相同 (1.1604 / 4.5297 / 2.8451),這要不是表格製作錯誤,就是兩種 view 設定在 pipeline 中其實同義,作者未說明。
- 同表中 VGGT-World 的 Comp = 4.53 比 Gen3R pose-free (Comp 2.54) 差近 80%,但摘要與 §4.2 一律以「significantly outperforms on all metrics」帶過,呈現了選擇性報告 — 真實情況是「點雲更精準但較稀疏」的 accuracy / completeness trade-off。
- 「未來預測改善當下」的 Table 4 中 Acc 反而從 0.8672 退步到 0.8764,只有 Comp 與 CD 下降;論文卻把這結果包裝為 predictive perception 的一般結論,證據強度與宣稱嚴重不對等。
- $\lambda$ ablation 只比較 static $\lambda \in \{0.1, 0.3, 0.7\}$ 與 linear schedule,沒有與 diffusion forcing [9]、self forcing [21] 或 scheduled sampling 直接對照,所以 curriculum 的必要性無法與其他 anti-exposure-bias 方法區分。
- 缺少對 chunk size $m$、history length $k$、$L_d$/$L_s$ 切分比例的 ablation,儘管 §3.2 的核心論述就是「causality 與 spatial denoising 可分離」。
- 「long-term horizon」在 Fig. 5 中其實是 $T=7$ 達到甜蜜點後立即退化,這個 horizon 比論文題目「autoregressive geometry world model」的暗示要短得多,長水平穩定性的證據相對薄弱。
- 訓練只用 1× RTX Pro 6000 (96 GB),KITTI 訓練序列僅 143 條,Cityscapes 與 TartanAir 也屬於受限規模;在這個量級上得出的「frozen GFM 是更佳 predictive state」結論需保留至大規模驗證。
- 動態前景 (車輛、行人) 在 layer-4 VGGT feature 中的代表性未被檢視,但 Cityscapes / KITTI 的失敗模式正是「mislocalized actors」(Fig. 1),作者用 Fig. 1 反駁 baseline 卻沒對自家方法在動態 region 做拆分式評估。

### 4.3 Phyra's Judgment (summary)

真正新穎的貢獻是「將 predictive state 從 video VAE 或 DINO 換成 GFM (VGGT) layer-4」這個 representation 選擇,以及為了讓它在 $d=1024$ weakly compressed latent 上能訓練起來而提出的 z-prediction + flow-forcing curriculum;這兩者合在一起確實構成一個有效的工程封裝。然而論文最有力的數值改善大多可被 frozen VGGT decoder 的強 prior 解釋,paper 並未做能切開「decoder 貢獻 vs. temporal transformer 貢獻」的 ablation,因此核心問題「temporal model 本身學到了多少幾何動態」仍未解決。整體定位介於 DINO-Foresight 的直接延伸與一個有實作價值的 efficiency baseline 之間,作為 geometry world model 的「early attempt」是合理的,但「establishes frozen GFM features as an effective predictive state」這類斷言略嫌過早。

## 5. Methodology Deep Dive

### 5.1 Method Overview

VGGT-World 將「世界模型」重新定義為 frozen geometry foundation model 特徵空間中的時間演化問題,而非 RGB 影格的生成問題。整體 pipeline 分為三個被明確分離的階段:(i) 空間表徵抽取由凍結的 VGGT encoder $\Phi_{\text{enc}}$(VGGT 前 4 層,共 48 層中 layer 0–4)負責,將每個觀察影格 $I_t$ 編碼為 tokenized 幾何狀態 $\mathbf{z}_t \in \mathbb{R}^{N \times d}$,其中 $N = 5 + N_p$ 包含 5 個 special tokens(camera + register tokens)與 $N_p$ 個 spatial patch tokens,$d = 1024$;(ii) 時間動力學由輕量級 temporal flow transformer $F_\theta$(0.43B 可訓練參數)負責,在 $k$-frame 歷史條件 $\mathbf{c}_i$ 下以 chunk-wise autoregressive 方式預測未來 $m$ 個 frame 的 clean latent;(iii) 3D 解碼由凍結的 $\Phi_{\text{dec}}$(layers 5–47)與原始 VGGT 3D heads $\mathcal{H}_{\text{3D}}$ 完成,將完整 trajectory $\mathbf{z}_{1:T}^{\text{full}}$ 解出 depth maps、point clouds 與 camera-motion 線索。

該設計面對兩個高維幾何空間獨有的挑戰。第一,$d = 1024$ 的 VGGT latent 屬於弱壓縮 (相較於 video VAE 的 $d=16$–$32$),standard velocity-prediction flow matching 在 isotropic Gaussian corruption 下會被 off-manifold 雜訊主導,使 velocity estimation ill-conditioned;Fig. 2 顯示即使訓練 4k iterations 後 $v$-prediction 仍呈現雜訊,而 $z$-prediction 則持續收斂到結構化的 latent。作者因此將 $F_\theta$ 直接參數化為預測 clean target chunk $\mathbf{Z}_i$,而非 velocity field $v_\theta$,以提升 SNR。第二,autoregressive rollout 的 exposure bias 來自於每個 chunk $\hat{\mathbf{Z}}_i$ 的誤差會污染下一步 condition $\mathbf{c}_{i+1}$,進而沿 horizon 累積 drift。

為解決 exposure bias,作者設計兩階段 latent flow-forcing curriculum:Stage 1 採用 oracle ground-truth 歷史進行 teacher forcing 以建立基礎 vector field;Stage 2 將模型自身的 partially-denoised ODE rollout state $\hat{\mathbf{Z}}_{i, \tau_{\text{mid}}}$ 與 ground-truth $\mathbf{Z}_i$ 透過 mixing parameter $\lambda$ 線性插值,作為下一個 chunk 的 mixed condition $\mathbf{c}_{i+1}^{\text{mix}}$;$\lambda$ 在訓練過程中由 0 線性退火至 1,逐步將模型暴露在 inference-time 自我條件分布上。$F_\theta$ 內部進一步分解為 dual-stream causal processor $F_{\text{dual}}$(早期 8 個 blocks 處理跨 history-target 的 temporal causality)與 single-stream spatial denoiser $F_{\text{single}}$(後期 8 個 blocks 專注於 intra-chunk 空間精化),呼應近期 video diffusion 分析中 temporal/spatial attention 自然分層的觀察。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: video I_{1:T} : [B, T, 3, H, W]
   │
   │  Φ_enc  (frozen VGGT layers 0-4)   per-frame, applied independently
   ▼
Geometry states z_{1:T} : [B, T, N, d]      N = 5 + N_p, d = 1024
   │
   ├──→ Observed history (k frames) : z_{1:k} : [B, k, N, d]
   │       │
   │       │  build sliding-window context
   │       ▼
   │    c_i = z_{(i-1)m+1 : (i-1)m+k} : [B, k, N, d]
   │
   └──→ Chunk-wise autoregressive rollout, for i = 1 … S
          │
          ├─ sample noise  Z_{i,1} ~ N(0, I) : [B, m, N, d]
          │
          ├─ Euler ODE solve  τ : 1 → 0  with predictor F_θ
          │     │
          │     │  at each τ-step:
          │     ▼
          │   F_θ(Z_{i,τ}, τ, c_i) :
          │      ├─ τ → adaLN scale/shift via MLP : [B, 2 d]   (broadcast)
          │      │
          │      ├─ F_dual  (L_d = 8 double-stream blocks)
          │      │     Q = adaLN(Z_{i,τ}, τ)        : [B, m·N, d]
          │      │     K,V = [adaLN(Z_{i,τ}, τ); c_i] : [B, (m+k)·N, d]
          │      │     asymmetric cross-attention   →  Z_{i,τ}^{(L_d)} : [B, m·N, d]
          │      │
          │      └─ F_single  (L_s = 8 single-stream blocks)
          │            Q,K,V = adaLN(·, τ)
          │            joint intra-chunk self-attention
          │            output (z-prediction)        →  \hat{Z}_i : [B, m, N, d]
          │
          ├─ stop integration at τ_mid for Stage-2 mixed condition
          │     \hat{Z}_{i, τ_mid} : [B, m, N, d]
          │
          └─ slide window:  c_{i+1} ← \hat{Z}_i  (last k frames)

Aggregate full trajectory:
   z_{1:T}^{full} = [z_{1:k} ; \hat{Z}_{1:S}] : [B, T, N, d]
   │
   │  Φ_dec  (frozen VGGT layers 5-47)   joint propagation across T
   ▼
Multi-scale feature hierarchy at layers {4, 11, 17, 23}
   self-attn + global-attn streams       : 4 × [B, T, N, d]   (per-stream)
   │
   │  H_3D  (frozen VGGT 3D heads)
   ▼
Outputs
   ├─ depth maps   D_{1:T} : [B, T, 1, H, W]
   ├─ point maps   P_{1:T} : [B, T, 3, H, W]
   └─ camera-motion cues from camera tokens : [B, T, ?]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Geometry State Encoder $\Phi_{\text{enc}}$

**Function:** 將每個 RGB 影格獨立編碼為 layer-4 的 VGGT latent,作為 world model 的 predictive state。

**Input:**
- Name: $I_t$
- Shape: `[B, 3, H, W]` (per frame; $T$ 個 frames 平行處理為 `[B, T, 3, H, W]`)
- Source: 原始觀察影格

**Output:**
- Name: $\mathbf{z}_t$
- Shape: `[B, N, d]`,$N = 5 + N_p$,$d = 1024$
- Consumer: 構成 sliding-window context $\mathbf{c}_i$ 並作為 $\mathbf{z}_{1:T}^{\text{full}}$ 起始 $k$ frames

**Processing:**

VGGT 由 $L = 48$ 個 transformer blocks 組成(24 self-attention + 24 global-attention)。$\Phi_{\text{enc}}$ 取前 4 層輸出。每個 frame 被 patchified 為 $N_p$ 個 spatial patch tokens 並串接 5 個 special tokens(camera + register tokens),共 $N$ tokens。Layer 4 是最早能與 frozen 3D heads 多尺度層 $\{4, 11, 17, 23\}$ 對齊的層,因此選為 predictive state。所有參數在訓練期間 frozen。

**Key Formulas:**

$$
\mathbf{z}_t = \Phi_{\text{enc}}(I_t) \in \mathbb{R}^{N \times d} \quad (\text{Eq. 1})
$$

**Implementation Details:**

paper 未明確指定 VGGT 的 patch size 與輸入解析度,故 $N_p$ 的具體數值未列出(以 `?` 表示)。$d = 1024$ 為原始 VGGT intermediate dimensionality,作者明確未做 feature compression(保留原維度以維持與 frozen heads 對齊)。

#### 5.3.2 Sliding-Window Context Constructor

**Function:** 將最近 $k$ 個(observed 或自我生成)幾何狀態組成下一個 chunk 的 condition,維持 inference 期間 context 大小固定。

**Input:**
- Name: $\mathbf{z}_{1:k}$ 或 $\hat{\mathbf{Z}}_{i-1}$
- Shape: `[B, k, N, d]` 或 `[B, m, N, d]`
- Source: 第 1 個 chunk 取自 $\Phi_{\text{enc}}$ 觀察狀態;後續 chunk 取自前一輪預測結果

**Output:**
- Name: $\mathbf{c}_i$
- Shape: `[B, k, N, d]`
- Consumer: $F_\theta$ 的 dual-stream block 作為 K, V

**Processing:**

採用 sliding window:預測完整 chunk $\hat{\mathbf{Z}}_i$ 後,從近期解碼序列中擷取最後 $k$ 個 frames 作為下一步 condition $\mathbf{c}_{i+1} = \hat{\mathbf{Z}}_i$(取最後 $k$ frames),不累積成長 history。此設計使 memory 隨 horizon 維持常數複雜度。

**Key Formulas:**

$$
p(\mathbf{z}_{k+1:T} \mid \mathbf{z}_{1:k}) = \prod_{i=1}^{S} p(\mathbf{Z}_i \mid \mathbf{c}_i) \quad (\text{Eq. 2})
$$

**Implementation Details:**

實驗中 initial chunk size $m = 4$,autoregressive stride 為 1。$k$ 在 1-view 與 2-view 評估中分別為 1 與 2(see Table 3)。

#### 5.3.3 Dual-Stream Causal Processor $F_{\text{dual}}$

**Function:** 在早期 transformer blocks 透過 noisy target chunk 對 clean condition 的 asymmetric cross-attention,建立 temporal causality 而不污染 history representation。

**Input:**
- Name: $\mathbf{Z}_{i,\tau}^{(l)}$, $\mathbf{c}_i$, $\tau$
- Shape: `[B, m, N, d]`, `[B, k, N, d]`, scalar (broadcast 至 `[B]` 後 MLP 投影為 adaLN scale/shift `[B, 2 d]`)
- Source: 前一個 dual-stream block 或 noisy 初值;sliding window 構造的 condition;ODE 當前 flow time

**Output:**
- Name: $\mathbf{Z}_{i,\tau}^{(l+1)}$
- Shape: `[B, m, N, d]`
- Consumer: 下一個 dual-stream block;最後一層接續至 $F_{\text{single}}$

**Processing:**

每個 block 將 noisy target 透過 adaLN 條件化於 $\tau$ 後作為 query,與 clean condition $\mathbf{c}_i$ 拼接成 K, V 進行 cross-attention。注意 condition 不被 adaLN 擾動,以保留 ground-truth 幾何資訊作為 anchor。共 $L_d = 8$ blocks。

**Key Formulas:**

$$
\mathbf{Z}_{i,\tau}^{(l+1)} = \mathbf{Z}_{i,\tau}^{(l)} + \text{Attn}\bigl(\text{Q} = \text{adaLN}(\mathbf{Z}_{i,\tau}^{(l)}, \tau),\; \text{K,V} = [\text{adaLN}(\mathbf{Z}_{i,\tau}^{(l)}, \tau); \mathbf{c}_i]\bigr) \quad (\text{Eq. 7})
$$

**Implementation Details:**

架構參考 [26](MM-DiT 風格 dual-stream block)。adaLN 將 $\tau$ 投影為 layer-wise scale 與 shift。paper 未明確列出 attention head 數與 FFN 寬度。

#### 5.3.4 Single-Stream Spatial Denoiser $F_{\text{single}}$

**Function:** 在深層 blocks 移除 condition,僅在 target chunk 內部進行 joint intra-chunk self-attention,專注於局部 spatiotemporal 幾何精化。

**Input:**
- Name: $\mathbf{Z}_{i,\tau}^{(L_d)}$, $\tau$
- Shape: `[B, m, N, d]`, scalar
- Source: $F_{\text{dual}}$ 最後一層輸出

**Output:**
- Name: $\hat{\mathbf{Z}}_i$ (z-prediction approximation of clean target)
- Shape: `[B, m, N, d]`
- Consumer: ODE solver 用於下一 Euler step;最終解 chunk 進入 trajectory aggregation

**Processing:**

每個 block 對 $m \cdot N$ 個 tokens 做完整 self-attention,允許跨 frame 與跨 token 的空間-時間細化,但不再回看 condition。共 $L_s = 8$ blocks。最後輸出即為當前 ODE 步的 clean-target 預測 $\hat{\mathbf{Z}}_i \approx F_\theta(\mathbf{Z}_{i,\tau}, \tau, \mathbf{c}_i)$。

**Key Formulas:**

$$
\mathbf{Z}_{i,\tau}^{(l+1)} = \mathbf{Z}_{i,\tau}^{(l)} + \text{Self-Attn}\bigl(\text{Q,K,V} = \text{adaLN}(\mathbf{Z}_{i,\tau}^{(l)}, \tau)\bigr) \quad (\text{Eq. 8})
$$

$$
\mathbf{Z}_i \approx F_\theta(\mathbf{Z}_{i,\tau}, \tau, \mathbf{c}_i) = F_{\text{single}}\bigl(F_{\text{dual}}(\mathbf{Z}_{i,\tau}, \tau, \mathbf{c}_i),\; \tau\bigr) \quad (\text{Eq. 6})
$$

**Implementation Details:**

paper 引用近期分析 [4] 表明 video diffusers 中 causality 與 spatial denoising 自然可分離,後期層 attention 趨於對角化。$L_d = L_s = 8$ 為實驗選擇。

#### 5.3.5 Chunk Rollout via Euler ODE Solver

**Function:** 在 latent flow space 從 noise 積分到 clean target,並在 Stage 2 訓練時於中介 $\tau_{\text{mid}}$ 停止以產生 partially-denoised state。

**Input:**
- Name: $\mathbf{Z}_{i, 1}$, $\mathbf{c}_i$
- Shape: `[B, m, N, d]`, `[B, k, N, d]`
- Source: $\mathbf{Z}_{i, 1} \sim \mathcal{N}(0, I)$;sliding window context

**Output:**
- Name: $\hat{\mathbf{Z}}_i$ 或 $\hat{\mathbf{Z}}_{i, \tau_{\text{mid}}}$
- Shape: `[B, m, N, d]`
- Consumer: trajectory aggregation 或 mixed condition 構造

**Processing:**

Standard flow matching probability path 為 $\mathbf{Z}_{i,\tau} = (1-\tau)\mathbf{Z}_i + \tau \epsilon$。給定 $z$-prediction 網路 $F_\theta$,對應 velocity 可由 $(F_\theta(\mathbf{Z}_{i,\tau}, \tau, \mathbf{c}_i) - \mathbf{Z}_{i,\tau})/(1-\tau)$ 解得,代入 Eq. 5 即可進行 Euler 積分。Inference 時 $\tau$ 從 1 → 0 完整積分;Stage 2 訓練時於 $\tau_{\text{mid}} \in (0, 1)$ 停止,得到結構化但未完全去雜訊的 rollout state。

**Key Formulas:**

$$
\hat{\mathbf{Z}}_{i, \tau_{\text{mid}}} = \text{ODESolve}\bigl(F_\theta, \mathbf{Z}_{i, 1}, \mathbf{c}_i, \tau \in [1 \to \tau_{\text{mid}}]\bigr) \quad (\text{Eq. 10})
$$

**Implementation Details:**

採用 Euler solver。paper 未明確列出 inference-time 步數與 $\tau_{\text{mid}}$ 排程細節(`?`)。

#### 5.3.6 Trajectory Aggregation, Frozen Decoder $\Phi_{\text{dec}}$ 與 3D Heads $\mathcal{H}_{\text{3D}}$

**Function:** 將觀察狀態與預測 chunks 串接成完整 trajectory,透過 frozen VGGT 後段層數聯合傳遞,再以原始 3D heads 解出 dense 幾何輸出;預測 future 同時改善 observed step 的 3D 估計。

**Input:**
- Name: $\mathbf{z}_{1:T}^{\text{full}} = [\mathbf{z}_{1:k}; \hat{\mathbf{Z}}_{1:S}]$
- Shape: `[B, T, N, d]`,$T = k + S \cdot m$
- Source: encoder 觀察狀態與 rollout chunks

**Output:**
- Name: $\mathcal{D}_{1:T}$, $\mathcal{P}_{1:T}$
- Shape: depth `[B, T, 1, H, W]`,point maps `[B, T, 3, H, W]`
- Consumer: 評估指標(AbsRel、$\delta_1$、Acc/Comp/CD)與下游應用

**Processing:**

完整 latent trajectory 經 $\Phi_{\text{dec}}$(layers 5–47,frozen)聯合傳遞,3D heads 從 layers $\{4, 11, 17, 23\}$ 在 self-attention 與 global-attention 兩個 stream 中各自取出多尺度 features 並解碼。此 joint decoding 產生額外 regularization:即使在稀疏觀察(如 $k=2$)下,future chunks 提供 long-horizon 一致性約束,因此提升 observed step $k$ 的幾何精度。

**Key Formulas:**

$$
\mathbf{z}_{1:T}^{\text{full}} = [\mathbf{z}_{1:k}; \hat{\mathbf{Z}}_{1:S}] \quad (\text{Eq. 3})
$$

$$
\mathcal{P}_{1:T},\ \mathcal{D}_{1:T} = \mathcal{H}_{\text{3D}}\bigl(\Phi_{\text{dec}}(\mathbf{z}_{1:T}^{\text{full}})\bigr) \quad (\text{Eq. 4})
$$

**Implementation Details:**

$\Phi_{\text{dec}}$ 與 $\mathcal{H}_{\text{3D}}$ 全部 frozen,不需 fine-tune ground-truth depth(對應 Table 1 中 KITTI 結果未經 depth fine-tuning 仍超越 DINO-Foresight)。

#### 5.3.7 Two-Stage Latent Flow-Forcing Curriculum

**Function:** 透過分階段訓練 $F_\theta$ 縮小 train-test mismatch:Stage 1 建立 oracle vector field;Stage 2 將模型暴露於自身 partially-denoised rollout 分布。

**Input / Output:**
- Stage 1 input: ground-truth $\mathbf{Z}_i$, oracle $\mathbf{c}_i = \mathbf{Z}_{i-1}$
- Stage 2 input: ground-truth $\mathbf{Z}_{i+1}$, mixed condition $\mathbf{c}_{i+1}^{\text{mix}}(\lambda, \tau_{\text{mid}})$
- Loss output: scalar 用於反向傳播至 $F_\theta$ 0.43B 可訓練參數

**Processing:**

Stage 1 採用 weighted z-prediction 形式以對抗高維 latent 的方差;Stage 2 凍結並承襲 Stage 1 權重,將 $\mathbf{Z}_i$ 透過 partial ODE rollout 至 $\tau_{\text{mid}}$ 得 $\hat{\mathbf{Z}}_{i, \tau_{\text{mid}}}$,再以 mixing $\lambda$ 與 ground-truth 線性插值構成 $\mathbf{c}_{i+1}^{\text{mix}}$,最後在 $\tau$ 上對 $\mathbf{Z}_{i+1, \tau}$ 預測 clean target。$\lambda$ 從 0 線性退火至 1。理論上(Appendix Theorem 1)該策略對應一個 sequential ELBO,而 mixed condition 的 variance scales as $\lambda^2 \mathbb{E}[\|E_i\|^2]$,因此 $\lambda$ 必須隨 rollout error 自然衰減而成長。

**Key Formulas:**

$$
\mathcal{L}_{\text{S1}} = \mathbb{E}_{\mathbf{Z}_i, \epsilon, \tau}\!\left[\,\left\| \frac{F_\theta(\mathbf{Z}_{i,\tau}, \tau, \mathbf{c}_i) - \mathbf{Z}_{i,\tau}}{1-\tau} - \frac{\mathbf{Z}_i - \mathbf{Z}_{i,\tau}}{1-\tau} \right\|_2^2\,\right] \quad (\text{Eq. 9})
$$

$$
\mathbf{c}_{i+1}^{\text{mix}}(\lambda, \tau_{\text{mid}}) = (1-\lambda)\mathbf{Z}_i + \lambda\,\hat{\mathbf{Z}}_{i, \tau_{\text{mid}}} \quad (\text{Eq. 11})
$$

$$
\mathcal{L}_{\text{S2}} = \mathbb{E}_{i, \lambda, \tau, \tau_{\text{mid}}}\!\left[\,\left\| \mathbf{Z}_{i+1} - F_\theta\bigl(\mathbf{Z}_{i+1,\tau}, \tau, \mathbf{c}_{i+1}^{\text{mix}}(\lambda, \tau_{\text{mid}})\bigr) \right\|_2^2\,\right] \quad (\text{Eq. 12})
$$

**Implementation Details:**

Optimizer AdamW,learning rate $2 \times 10^{-4}$,weight decay 0.05,gradient clipping $\ell_2$ norm 1.0。Stage 1 batch size 64,Stage 2 batch size 48。訓練於單張 RTX Pro 6000 (96 GB)。Table 2 之 $\lambda$ ablation 顯示固定大 $\lambda$($0.7$)會傷害短/中期表現,而線性退火(VGGT-World 主設定)同時優於 $w/o$ Forcing 與固定 $\lambda$,確認 curriculum 對 ELBO 緊度的必要性。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Cityscapes [10] | 短/中期 depth forecasting(都市駕駛場景) | 2,975 訓練序列 + 500 驗證序列;每段 30 frames、16 FPS、原始 1024×2048(評估時 resize + center-crop 至 224×448) | train / val(以 frame 19 為 target;短期由 [13,16] 預測 frame 19,中期由 [7,10] autoregressively 預測至 frame 19) |
| KITTI [16] | 短/中期 depth forecasting + camera parameter forecasting | 143 訓練序列 + 13 驗證序列;原始 512×1382、10 FPS(center-crop 至 224×448) | train / val(短期由 [9,11] 預測 frame 13,中期由 [5,7] autoregressively 預測至 frame 13) |
| TartanAir [53] | Point map forecasting + camera parameter forecasting | 大型合成資料集,~700k frames;原始 640×480、10 FPS(center-crop 至 280×280) | 90% train / 10% val(沿用 Gen3R [19] 切分);評估時隨機抽 10% 場景、每場景取 49 frames,以前 7 frames 之 aggregated point cloud 作為 long-horizon 評估目標 |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| AbsRel ↓ | 預測 depth 與 GT depth 之 mean Absolute Relative Error,衡量整體 depth 誤差 | yes |
| $\delta_1$ ↑ | Depth accuracy:預測值落在 GT 1.25 倍誤差比例內之比例 | yes |
| Accuracy ↓ | Predicted point cloud 與 GT 之 nearest-distance(預測點對 GT 的偏離) | yes(point map 任務) |
| Completeness ↓ | GT 對 predicted point cloud 之 nearest-distance(覆蓋率) | yes(point map 任務) |
| Chamfer Distance (CD) ↓ | Accuracy 與 Completeness 之合,整體 3D 幾何品質 | yes(point map 任務) |
| ATE ↓ (m) | Absolute Trajectory Error,Umeyama 對齊後相機軌跡誤差 | no(輔助分析) |
| RTE ↓ (m) | Relative Translation Error | no(輔助分析) |
| RRE ↓ (°) | Relative Rotation Error | no(輔助分析) |
| Latency (s/frame) | Normalized 每生成一 frame 之 inference 時間 | no(efficiency 分析) |
| Trainable params (B) | 可訓練參數量 | no(efficiency 分析) |

評估流程細節:depth 採 short-term(Cityscapes 187.5 ms / KITTI 200 ms)與 mid-term(Cityscapes 562.5 ms / KITTI 600 ms);point cloud 評估先以 Umeyama similarity alignment [47] 對齊 GT,再用 Farthest Point Sampling [39] 各取 20k 點計算指標。

### 6.3 Training and Inference Settings

- **Hardware**:1 張 RTX Pro 6000 (96 GB) GPU。
- **Optimizer**:AdamW,learning rate $2 \times 10^{-4}$,weight decay 0.05。
- **Gradient clipping**:$\ell_2$ norm = 1.0。
- **Batch size**:Stage 1 (Teacher-Forcing) batch = 64;Stage 2 (Trajectory-Consistent Flow Forcing) batch = 48。
- **Learning rate schedule**:the paper does not specify(僅給出固定 lr 與 weight decay)。
- **Training steps / total epochs**:the paper does not specify(僅在 Fig. 2 給出 200 / 1000 / 4000 iter 的 SNR 對照)。
- **Architecture**:Flow Transformer 採 FLUX.1 kontext [26] 風格,$L_d = 8$ double-stream + $L_s = 8$ single-stream blocks;latent dim 維持 1024,不做 feature compression(Appendix B.1)。Backbone 採 frozen VGGT [50],encoder $\Phi_{\text{enc}}$ 取 layer 0–4,decoder $\Phi_{\text{dec}}$ 取 layer 5–47 + 原 3D heads。
- **Positional encoding**:對 condition + predicted latents 串接序列套用 3D Rotary Positional Embedding (3DRoPE)(Appendix B.1)。
- **Chunk 設定**:Stage 1 chunk size = 4(前 2 frames 為 condition、後 2 frames 為 target);Stage 2 chunk size = 5,並僅對 rollout step 的後續部分 backpropagate 梯度以抑制 exposure bias(Appendix B.3)。
- **Inference**:固定 chunk size = 4,以 stride = 1 的 sliding window 進行 autoregressive rollout;condition $\mathbf{c}_{i+1}$ 取上一輪預測之最後 $k$ 個 frames(§3.1 Chunk-wise Autoregressive Rollout)。
- **Curriculum**:Stage 2 之 mixing ratio $\lambda$ 隨訓練進度由 0 線性 anneal 至 1。
- **監督需求**:不使用 ground-truth depth 或 point cloud 監督;僅以 frozen VGGT latent 為自監督目標。

### 6.4 Main Results

KITTI depth forecasting(Table 1 中 Mean Dataset Avg.):

| Method | AbsRel ↓ Short | AbsRel ↓ Mid | $\delta_1$ ↑ Short | $\delta_1$ ↑ Mid | Notes |
|---|---|---|---|---|---|
| Cosmos-4B [1] | 0.155 | 0.165 | 77.1 | 74.1 | Pixel-space 2D generation |
| Cosmos-12B [1] | 0.154 | 0.185 | 77.5 | 71.5 | 規模放大但 mid-term 反而退步 |
| Copy-Last (VGGT [50]) | 0.137 | 0.144 | 83.7 | 78.5 | 直接複製上一 frame 之 VGGT depth |
| Aether [44] | 0.096 | 0.124 | 87.9 | 84.7 | Geometry-aware video gen |
| DINO-Foresight [23] | 0.082 | 0.115 | 91.6 | 85.1 | 在 GT depth 上 fine-tune |
| **VGGT-World (ours)** | **0.065** | **0.098** | **94.0** | **89.4** | Short/Mid AbsRel 相對最佳 baseline 改善 21% / 15%,且未在 GT depth 上 fine-tune |

Cityscapes depth forecasting(Table 2 上半):

| Method | AbsRel ↓ Short | AbsRel ↓ Mid | $\delta_1$ ↑ Short | $\delta_1$ ↑ Mid |
|---|---|---|---|---|
| Cosmos-4B [1] | 0.189 | 0.247 | 76.3 | 70.5 |
| Cosmos-12B [1] | 0.181 | 0.241 | 78.2 | 72.4 |
| Copy-Last (VGGT [50]) | 0.154 | 0.212 | 84.1 | 77.8 |
| VISTA$_{\text{ft}}$ [15] | 0.124 | 0.153 | 86.4 | 82.8 |
| DINO-Foresight [23] | 0.114 | 0.136 | 88.6 | 85.4 |
| **VGGT-World (ours)** | **0.078** | **0.126** | **93.8** | **87.3** | AbsRel 較最佳 baseline 改善至多 32% |

TartanAir point map forecasting(Table 3,Pose-free + Text-conditioned 設定):

| Method | 1-view Acc.↓ | 1-view Comp.↓ | 1-view CD↓ | 2-view Acc.↓ | 2-view Comp.↓ | 2-view CD↓ |
|---|---|---|---|---|---|---|
| Aether [44] | 3.1547 | 4.5366 | 3.8457 | 2.7745 | 3.4420 | 3.1082 |
| WVD [61] | 4.3944 | 3.0660 | 3.7302 | 4.3794 | 2.5268 | 3.4531 |
| Gen3R [19] (text+pose-free) | 3.0250 | 2.5367 | 2.7809 | 2.2825 | 1.6643 | 1.9734 |
| Gen3R [19] (text, pose-free) | 3.4579 | 4.7384 | 4.0982 | 2.6029 | 3.1154 | 2.8591 |
| Gen3R [19] (text + pose) | 3.6427 | 7.8528 | 5.7478 | 2.7441 | 6.1423 | 4.4432 |
| **VGGT-World (ours)** | **1.1604** | 4.5297 | **2.8451** | **1.1604** | 4.5297 | **2.8451** | 

Notes:VGGT-World 在 Acc. 與 CD 上均明顯領先;Completeness 弱於部分 Gen3R 設定,顯示其誤差分佈偏向「預測較稀但精準」。Efficiency(Fig. 7):VGGT-World 1.9 s/frame,相對 Cosmos-12B(9.50 s/frame)約 5×、相對 Gen3R(6.90 s/frame)約 3.6× 加速;trainable parameters 僅 0.43B,而 Cosmos-12B 為 12.0B、Gen3R 約 2.7B (DiT) + geometry adapter,VGGT 1.3B backbone 完全 frozen。

### 6.5 Ablation Studies

- **Forcing curriculum vs. no forcing(Table 2 上半 + 下半)**:`w/o Forcing` 在 Cityscapes 為 AbsRel 0.079 / 0.131、$\delta_1$ 93.7 / 86.8;啟用 curriculum 後改善為 0.078 / 0.126、93.8 / 87.3。短期幾乎不變,**中期** $\delta_1$ +0.5、AbsRel −0.005,印證 Stage 2 的 Trajectory-Consistent Flow Forcing 主要對抗 long-horizon exposure bias。此為診斷性 ablation,直接對應 §3.3 主張。
- **Static $\lambda$ 比較(Table 2 下半)**:固定 $\lambda = 0.1 / 0.3 / 0.7$ 之 mid-term AbsRel 分別為 0.142 / 0.148 / 0.165、$\delta_1$ 為 85.0 / 84.9 / 81.4,皆劣於 linear-anneal 版本(0.126 / 87.3)。$\lambda = 0.7$ 表現最差,符合 §3.3 中「rollout error 早期過大時注入過量 variance 會破壞 ELBO 下界、甚至導致 Stage-1 catastrophic forgetting」之理論說明。屬於診斷性 ablation。
- **z-prediction vs. v-prediction(Fig. 2,定性)**:於 frozen VGGT layer-4 latent 中,v-prediction 在 4k iter 後仍 noisy;z-prediction 在 200 / 1000 / 4000 iter 持續累積結構化 latent,SNR 顯著較高。此為對 §3.2 核心設計選擇的定性診斷,但**僅 PCA 視覺化與 SNR 曲線,沒有以下游 depth/point cloud 指標的數字對照**,診斷強度受限。
- **未來預測對當下感知是否有助益(Table 4,TartanAir short-term)**:VGGT 為 Acc. 0.8672 / Comp. 1.2159 / CD 1.0416;VGGT-World 為 0.8764 / **1.0646** / **0.9705**。Accuracy 略退、但 Completeness 與 CD 顯著提升,支持「forecasting 反向強化當前 frame 之 holistic 3D 估計」之主張(§3.1 3D Joint Decoding)。屬診斷性。
- **Foresight horizon 長度(Fig. 5,TartanAir)**:CD 隨 horizon 增加先下降、約於 frame 7 達最佳,之後反升。回答了「向未來預測多遠最有利於當下幾何」這一具體問題,屬診斷性 ablation;但僅以單一資料集 + 單一 metric (CD) 報告,規模有限。
- **Sanity-check 風險**:Copy-Last (VGGT) baseline 並非 ablation 而是參考下界;但與 Cosmos-4B/12B 同列時亦帶有「video-gen baseline 是否打贏 trivial baseline」的檢驗意味,屬正當的 sanity 對照而非診斷。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — KITTI 對 Cosmos-12B、Aether、DINO-Foresight,TartanAir 對 Gen3R、Aether、WVD,涵蓋 pixel-space、geometry-aware video gen 與 latent foresight 三條 SoTA 線。
- [covered] Has cross-task / cross-dataset evaluation — 跨 KITTI / Cityscapes(depth)、TartanAir(point map)、KITTI + TartanAir(camera trajectory),且包含 short / mid / long horizon。
- [partial] Has ablations that diagnose the new components — Forcing curriculum 與 $\lambda$ schedule 有完整數字診斷;但 z-prediction vs. v-prediction 僅以 Fig. 2 視覺化呈現,未在下游 depth/point cloud metric 上做替換對照,核心設計之一缺乏量化診斷。
- [partial] Has a scaling study — 對 foresight horizon 長度有 Fig. 5 之掃描(TartanAir CD vs. horizon),但未對 model size、training data 量、chunk size 等做系統性 scaling 實驗。
- [covered] Has an efficiency / wall-clock comparison — Fig. 7 報告 normalized latency(VGGT-World 1.9 vs. Gen3R 6.90 vs. Cosmos-12B 9.50 s/frame)與 trainable / frozen parameter footprint。
- [missing] Reports variance / standard deviation / multiple seeds — 全文所有表格僅報告單一數字,未見任何 std、CI 或多 seed 平均。
- [missing] Releases code / weights / data sufficient for reproducibility — 文中未提及 code release、checkpoint、或 reproducibility artifact 連結;Appendix 雖列出超參數與 chunk-size 流程,仍不足以完整重現訓練。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1:Geometry world modeling 比 video world modeling 更適合 3D 預測** — *partially supported*。Fig. 1 與 Cosmos / Aether 的對比 (Table 1) 在 photometric-driven 對手上確實佔優,但跟同屬 latent world model 的 DINO-Foresight 相比,優勢縮小到 ~21% AbsRel,且 DINO-Foresight 用的 depth backbone 是 Depth Anything 而非 VGGT,decoder 因素未控制,因此不能完全歸因於 representation 選擇。
- **Claim 2:z-prediction 在 high-d GFM latent 上比 v-prediction 穩定** — *supported*。Fig. 2 的 SNR 曲線與 PCA 視覺化在 200 / 1k / 4k iter 三個檢查點都顯示 v-pred 無法收斂,z-pred 則逐步出現結構,屬於可重現且方向明確的證據。
- **Claim 3:Two-stage latent flow-forcing curriculum 能緩解 exposure bias** — *partially supported*。Table 2 下半段顯示 static $\lambda=0.7$ 確實 catastrophic,linear schedule 比 w/o forcing 在 mid-term AbsRel 從 0.131 降到 0.126(改善 ~4%),效應不大,且未與其他 anti-drift 方法 (diffusion forcing、self forcing) 比對。
- **Claim 4:Inference 比 Cosmos 快 5×、比 Gen3R 快 3.6×,trainable 0.43B 參數** — *supported*。Fig. 7 的 latency 與參數量資料具體,且方法本身 frozen 大量 backbone,效率優勢屬可驗證的工程結果。
- **Claim 5:Forecast 未來能改善當下幾何感知** — *overclaimed*。Table 4 顯示 Acc 0.8672 → 0.8764 反而退步,只有 Comp 與 CD 下降;單一資料集 (TartanAir)、單一 horizon、單一 metric 改善便包裝為「predictive perception」一般原理,證據明顯不足。

### 7.2 Fundamental Limitations of the Method

**Frozen-decoder bottleneck**。整個 pipeline 的最終幾何輸出都要過 frozen VGGT layer 5–47 與 3D heads;這意味著 (i) 預測 latent 一旦離開 VGGT 訓練時看到的 manifold,decoder 沒有機會 fine-tune 去吸收這個 distribution shift;(ii) 任何 VGGT 自身的弱點 (例如對動態物體、極端光照、非常規 FoV) 都會原封不動傳到預測結果。Paper 的「Upper Bound」(把真實未來影格直接丟給 VGGT) 也就是這個系統的天花板,而 Fig. 3、Fig. 8 的 Upper Bound 已經在 mid-term 出現可見誤差,代表這個天花板本身並不高。

**狀態空間對動態語意的覆蓋不足**。VGGT layer-4 是早期 self-attention 輸出,主要承載多視角幾何而非物件 semantic;但驅動 future forecasting 的關鍵恰是「車子會往哪移動、人會不會穿越馬路」這類 semantic-conditioned dynamics。論文沒有針對 dynamic foreground 做拆分式評估,因此方法在「靜態場景幾何外推」之外的能力是未知的;這不是調 hyper-parameter 能補齊的,屬於 representation level 的結構限制。

**Sliding-window context 帶來的記憶體瓶頸**。為了控制 memory,inference 用固定 size $k$ 的 window 取代累積 history (§3.1),這在 short / mid horizon 看不到問題,但在真正長水平場景 (例如 30 秒以上自駕) 中,前期觀察的場景結構會徹底丟失,導致 rollout 無法回到曾經出現過的拓樸 — 這個性質從 Fig. 5 在 frame 7 之後 CD 開始反升的曲線就可以看到端倪,但論文只把它解釋為「sweet spot」,而沒有承認這是 sliding-window 設計的內生缺陷。

**Curriculum 的穩定性依賴未驗證的變異假設**。§3.3 與 Appendix A 都明確指出 sequential ELBO 的 tightness 由 $\mathbb{E}[\|E_i\|^2]$ 控制,而早期訓練這個量「prohibitively large」,只能靠 $\lambda$ 從 0 慢慢 anneal 來避開崩潰;一旦資料或 chunk size 改變,annealing schedule 就需要重新調,而論文沒有給出 $\lambda(t)$ 的自適應準則,實作上是「只在當前實驗設定下穩定」的方法。

### 7.3 Citations Worth Tracking

- **Wang et al., VGGT [50]**:整個系統的 backbone 與 frozen decoder,理解 VGGT-World 的能力與限制必須先讀 VGGT 對 layer 結構與 3D head 的設計理由。
- **Karypidis et al., DINO-Foresight [23]**:最直接的 latent world model 對手,同樣是「frozen feature + temporal forecaster」,差別僅在 backbone 是 DINO 還是 VGGT;比較這兩篇能看出「representation 換掉」的真實邊際貢獻。
- **Huang et al., Self Forcing [21]** 與 **Chen et al., Diffusion Forcing [9]**:VGGT-World 的 flow-forcing curriculum 自承直接受這兩篇啟發又不採用,需讀原作才能評估「partially-denoised rollout state」相對於現有 anti-drift 機制是否真的是更好的選擇。
- **Wu et al., Geometry Forcing [56]**:雖然名字相近但屬於另一條技術路線 (在 video diffusion 內注入幾何先驗),是 VGGT-World 想要取代的「geometry-aware video gen」典型代表,讀完才能客觀判斷 representation 改寫 vs. prior injection 兩條路的權衡。
- **NVIDIA Cosmos [1, 36]**:作為 efficiency / scale baseline,且它的失敗模式 (Cosmos 在 KITTI depth 連 Copy-Last 都打不過) 是 VGGT-World 的核心 motivation,理解 Cosmos 的訓練目標與為何在幾何上崩潰,有助於評估「pixel-space 真的不行」這個前提是否完全成立。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 如果把 predictive state 換成 VGGT layer 11 / 17 / 23,代價是放棄部分 3D head 路徑,但語意更強,效果會如何?paper 只用 layer-4 的論證是「最早 decoder-compatible」,並未證明它就是最佳 trade-off。
- [ ] depth forecasting 的改善裡,「換成 VGGT decoder」與「temporal flow transformer」各佔多少比例?需要一個用 VGGT decoder 但 temporal model 退化為 identity / Copy-Last 的對照組才能拆開。
- [ ] 動態前景 (cars, pedestrians, cyclists) 的位置誤差 vs. 靜態背景幾何的誤差是否有顯著差異?整體 AbsRel 可能掩蓋 dynamic actor 的失敗。
- [ ] 若引入 action 或 ego-pose conditioning,$\lambda$ curriculum 與 z-prediction 的最佳化是否仍穩定?conditioning 通常會改變 latent 的 manifold 形狀。
- [ ] VGGT-World 在 50+ frame 真正長水平 rollout 時的失效模式是什麼?Fig. 5 只看到 7 frame,paper 沒有做更長水平的 stress test。
- [ ] Table 3 中 VGGT-World 1-view 與 2-views 數值完全一致是否為勘誤,還是 architecture 在這兩個輸入下退化為相同行為?
- [ ] Cosmos 與 Gen3R 在 photometric metric (FVD、LPIPS) 上明顯佔優,VGGT-World 在這些 metric 上的代價是多少?paper 完全不報告外觀品質。

### 8.2 Improvement Directions

1. **Ablation 拆分 decoder 與 temporal 貢獻** (低成本、高資訊量)。把 temporal transformer 替換為 (a) identity、(b) linear extrapolation、(c) 一個 small MLP,固定 VGGT decoder 不變,在 KITTI / Cityscapes 上重跑 depth forecasting;這能直接揭示「representation 換成 GFM」與「真的學到 temporal dynamics」各自貢獻多少 AbsRel,是現有實驗框架最容易補齊的關鍵 ablation。
2. **加入動態物體拆分式評估** (中成本)。利用 KITTI / Cityscapes 已有的 instance / semantic mask,把 AbsRel 拆成 static-bg 與 dynamic-fg 兩條;這能直接驗證 §1 引述的 baseline 失敗模式 (cyclist mislocalization) 在 VGGT-World 是否真的緩解,而不是被靜態背景的大面積精確度稀釋。
3. **以 LoRA / partial fine-tune 解凍 decoder** (中成本)。Frozen-decoder 是論文的 efficiency 賣點之一,但也是 representation 天花板;在預測 latent 上對 layer 5–47 開放 low-rank adaptation,可以測試「decoder 是否該為 predicted-not-real latent 微幅調整」,在維持 trainable 參數仍 < 1B 的前提下評估上限。
4. **改用 partially-denoised rollout 之外的 anti-drift 機制做 head-to-head** (中成本)。在同一個 backbone 上實作 diffusion forcing 與 self forcing 的 latent 版本,直接比較長水平 rollout 的 CD / AbsRel 軌跡;這能把 §3.3 的 curriculum 從「自己跟自己比 $\lambda$」推進到「跟其他 anti-drift 比」。
5. **Action / ego-pose conditioning** (中-高成本,作者已標示為 future work)。把 6-DoF camera delta 或 control token 注入 dual-stream block 的 cross-attention,可以同時 (i) 解決 §D 提到的可控性,(ii) 避開 sliding-window 在長水平丟失全域場景的問題,因為 pose 提供了「相機在世界中的絕對錨點」。
6. **多 layer 聯合 predictive state** (高成本但對的方向)。同時預測 layer-4 與 layer-11/17/23,讓 temporal model 學到 multi-scale 幾何演化,代價是 latent 體積膨脹;但能直接緩解「layer-4 語意不足以驅動 dynamic forecasting」的代表性瓶頸,屬於 representation 級別的根本改進。
