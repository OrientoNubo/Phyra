<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# LongStream — LongStream: Long-Sequence Streaming Autoregressive Visual Geometry

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | LongStream |
| Paper full title | LongStream: Long-Sequence Streaming Autoregressive Visual Geometry |
| arXiv ID | 2602.13172 |
| Release date | 2026-03-13 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2602.13172 |
| PDF link | https://arxiv.org/pdf/2602.13172 |
| Code link | — |
| Project page | https://3dagentworld.github.io/longstream/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Chong Cheng | HKUST(GZ); Horizon Robotics | — | first author |
| Xianda Chen | Central South University (CSU) | — | co-author |
| Tao Xie | Horizon Robotics; Zhejiang University (ZJU) | — | co-author |
| Wei Yin | Horizon Robotics | — | co-author |
| Weiqiang Ren | Horizon Robotics | — | co-author |
| Qian Zhang | Horizon Robotics | — | co-author |
| Xiaoyang Guo | Horizon Robotics | https://xy-guo.github.io/ | project lead |
| Hao Wang | HKUST(GZ) | https://wanghao.tech/ | corresponding author |

### 1.2 Keywords

streaming 3D reconstruction, autoregressive visual geometry, gauge-decoupled, keyframe-relative pose, KV cache, attention sink, cache-consistent training, metric-scale reconstruction

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Stream3R [1] | baseline | 因果 Transformer + KV cache 的串流 3D 重建基線；長序列下出現 attention collapse 與軌跡崩塌 |
| StreamVGGT [2] | baseline | 加入 temporal causal attention 與 cache update 並蒸餾的串流模型；長期穩定性仍受 cache 汙染影響 |
| VGGT [15] | base model | 前向預測 pose / depth / pointmap / track 的多視角模型；LongStream 以其 1.3B 主幹初始化並改造成串流 |
| DUSt3R [13] | predecessor | 首個由影像對直接回歸 pointmap 與相對位姿的端到端模型；僅成對且需全域對齊 |
| MASt3R [14] | predecessor | 在 DUSt3R 上加入稠密特徵與互相匹配以提升校準；仍為成對處理且多視角融合昂貴 |
| π3 [16] | influence | 以排列等變設計消除參考視角偏差，但輸出仍存在全域 similarity 模糊性，缺乏 metric scale |
| CUT3R [45] | baseline | 以 RNN 維持遞迴狀態輸出 metric pointmap 的串流方法；長序列下長期相依性處理能力下降 |

## 2. Research Overview

### 2.1 Research Topic

本論文研究長序列串流式 3D 幾何重建：在嚴格的線上、未來不可見設定下，從連續影像流即時估計相機位姿與稠密幾何（depth 與 pointmap），並維持公里級的 metric 尺度與穩定性。作者鎖定既有自迴歸串流模型（如 Stream3R、StreamVGGT）將座標錨定於第一幀所導致的注意力衰減、尺度漂移與外推失敗，提出 LongStream：以 keyframe-relative pose 取代絕對位姿、以 orthogonal scale head 解耦 Sim(3) 尺度，並透過 cache-consistent training 與 periodic cache refresh 對齊訓練與推論的 KV cache 視野，抑制 attention sink 與長期記憶汙染，最終於 KITTI、vKITTI、Waymo、TUM-RGBD、ETH3D、7Scenes 等室內外資料集上以 18 FPS 達成數千幀、公里級的穩定 metric 重建。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- Visual SLAM / Geometry Foundation Model
- Streaming / Online Inference
- Autonomous Driving

### 2.3 Core Architectures Used

- **DINOv2-based ViT tokenizer**：作為前端 patch token 抽取器，將每張輸入影像 $I_i$ 編碼為 patch features $x^p_i \in \mathbb{R}^{P \times C}$，並與 keyframe / normal-frame camera token、register token、scale token 一同送入後續聚合器。
- **Causal Transformer aggregator (VGGT-style 24-layer backbone)**：從 VGGT 初始化的約 1.3B 參數主幹，採用 intra-frame 與 global attention 交替結構並以嚴格因果遮罩運作，配合共用的 KV cache 完成串流時序融合。
- **Keyframe-Relative Pose Head**：以 RAFT 風格的 AdaLN-modulated Transformer 進行迭代更新 $p^{(t+1)} = p^{(t)} + \Delta p^{(t)}$，輸出相對位姿 $T_{i \leftarrow k} = T_i T_k^{-1}$（含 translation、unit quaternion、focal offset），實現 SE(3) gauge invariance。
- **Orthogonal Scale Head**：接收專用 Scale Token，預測 log-scale $x_s$ 並透過 $s = \exp(\mathbf{w}^\top h_{\text{scale}})$ 得到正純量，僅作用於 translation、depth、pointmap，達成 Sim(3) 尺度解耦。
- **Depth & Pointmap Heads**：以 frame-level 與 patch-level 特徵預測 $D_i \in \mathbb{R}^{H \times W}$ 與 $X_i \in \mathbb{R}^{H \times W \times 3}$ 及置信度，並在 scale-invariant 空間最佳化以保持 $\partial L / \partial s = 0$。
- **Cache-Consistent Training (CCT) + Periodic Cache Refresh**：作者提出的訓練策略，於訓練時以 chunked sliding window 顯式傳遞並裁切 KV cache，使訓練與逐幀推論在數學上等價；並每 $N$ 個 keyframe 重置 sink 與 cache 以邊際化老化上下文。

### 2.4 Core Argument

作者主張既有串流式視覺幾何模型在長序列上失效的根因，是「gauge-coupled」設計與訓練／推論分布錯位這兩個交織的問題。第一，現行模型把所有位姿錨定到第一幀座標系並回歸絕對位姿，這在硬體限制下訓練只能看到小的 frame index，推論時卻需外推到大 index，造成「train-short, test-long」的位置外推 OOD；同時 metric scale 與幾何形狀在輸出層耦合，使尺度誤差直接拖累 pointmap。其邏輯上的必要解法是「gauge-decoupled」：在 SE(3) 上改為預測 keyframe-relative pose Tᵢ←ₖ，使長距外推被重寫為 index gap 有界、難度恆定的局部任務，並對任意世界座標重參數化保持不變；在 Sim(3) 上以 SI-Log 哲學設計獨立 scale head，使幾何分支於 scale-invariant 空間最佳化、∂L/∂s = 0，由 Scale Token 單獨吸收尺度。第二，作者觀察到 Transformer 的 attention sink 並非穩定機制本身的需要，而是訓練時看得到完整序列、推論時卻在滑動視窗中操作所造成的訓練／推論錯位症狀；因此提出 Cache-Consistent Training，在訓練時即顯式地傳遞並裁切 KV cache，使訓練與逐幀推論在數學上等價，再以 periodic cache refresh 重置 keyframe 上的 sink 與 cache 以邊際化老化上下文。在這條因果鏈下，從 anchor 解耦 → 尺度解耦 → cache 一致性 → 週期性記憶重置，共同構成消除長序列退化的閉環，使 metric 尺度與軌跡能在公里級延展中保持穩定。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「LongStream: Long-Sequence Streaming Autoregressive Visual Geometry」直接點出三個關鍵字：long-sequence、streaming、autoregressive，預告本作要解決的是「線上、逐幀、長序列」的視覺幾何重建問題，而非離線的多視圖整批處理。Abstract 立刻指出問題核心：現有 streaming autoregressive 模型（如 Stream3R、StreamVGGT）將 pose 錨定在第一幀，導致 attention decay、scale drift、extrapolation error，在數十公尺內就會崩潰（呼應 Figure 1 中「Collapse (>50 m)」的對比）。作者隨即提出三件事：第一，丟棄 first-frame anchor，改預測 keyframe-relative pose，把長距外推轉為「constant-difficulty local task」；第二，提出 orthogonal scale learning，把幾何與 metric scale 在目標層級解耦以抑制 drift；第三，識別出 Transformer 的 attention sink 與長期 KV-cache saturation 是長序列退化主因，並提出 cache-consistent training 搭配 periodic cache refresh 來縮小 train/inference gap。Abstract 最後給出量化承諾：在 strictly online、future-invisible 設定下達 SOTA，能以 18 FPS 穩定重建 kilometer-scale 序列。整段文字以「失敗診斷 → 三項對症解法 → 量化結果」的結構，為全文鋪陳一條清晰的因果故事線。

### 3.2 Introduction

(620 words)

Introduction 以應用情境（autonomous driving、AR/VR、embodied robotics）切入，強調這些領域同時要求「long-sequence」與「real-time」，從而限定了問題的雙重約束。接著建立兩條對立的技術路線：傳統 SfM/MVS 與近期 Transformer-based 方法雖精度高但本質上是 offline，每加入一幀都要重新處理整段序列；streaming 方法（Stream3R、StreamVGGT）雖以 causal Transformer 與 KV-cache 達成增量重建，但在長序列下會出現 catastrophic extrapolation failure，並引用 Figures 1、2 作為視覺證據——軌跡在數十公尺內就崩潰、memory 與 latency 在 VGGT/FastVGGT 上呈快速增長甚至 OOM。這個對照同時建立了「為何要做 streaming」與「為何現有 streaming 不夠」兩層動機。

接著進入根因分析，作者把問題歸結為「gauge-coupled」設計：模型被釘在 first-frame coordinate 上、被訓練去回歸 absolute pose，導致 position-fixed mapping。再加上硬體限制讓 training batch 只看得到較小 frame index，於是出現「train-short, test-long」的 domain gap，引用 ALiBi（[19]）與 Transformer-XL（[20]）作為類比。這段把後續方法論的三項設計都預先「動機化」了。

隨後 Introduction 把 LongStream 的主張一條條對應到診斷：對 SE(3) gauge，移除 fixed first-frame anchor、改回歸 keyframe-relative pose，將長距外推轉成 constant-difficulty 的 local estimation，並使預測對全域座標選擇 invariant；對 Sim(3) gauge，引入 orthogonal scale learning，幾何分支在 scale-invariant 空間優化形狀、由 dedicated scale head 獨立預測 global scale factor，以解 entanglement 並穩定 metric output；對 streaming Transformer 架構本身，識別 attention sink 與 long-term KV-cache contamination 為兩個主要病因，提出 cache-consistent training（在訓練時顯式傳遞並 trim KV cache 以對齊 inference context）與 periodic cache refresh（marginalize 過期 context）。

Introduction 末段以實驗範圍作收：outdoor（KITTI、vKITTI、Waymo）與 indoor（TUM-RGBD、ETH3D、7Scenes）皆達 SOTA，並再次強調「real-time 18 FPS、kilometer-scale、metric-scale」的工程承諾。最後用三條 bullet 把 contribution 結構化：(i) gauge-decoupled 設計（keyframe-relative pose + orthogonal scale decoupling）系統性消除 first-frame anchor 依賴；(ii) 將 attention-sink reliance 與 KV-cache contamination 識別為長期退化主因，並以 CCT + periodic refresh 緩解；(iii) 在 strictly online、future-invisible 設定下取得 SOTA 與 real-time throughput。整個 Introduction 的論述邏輯極其清晰：先描述應用約束，再用視覺與量化證據揭露現有 streaming 失敗，再診斷出 gauge-coupled 與 attention-bias 兩個根因，最後一一對應出本文三項解法，自然引導讀者進入 §2 Related Work 的脈絡比較與 §3 Methodology 的形式化展開。

### 3.3 Related Work / Preliminaries

(360 words)

Related Work 分為三條敘事線，把 LongStream 的定位從「3D 重建史」中精準切出來。第一條是 Classical SfM and MVS：以 COLMAP 系列（[3,4]）、MVSNet 家族（[6,11]）為代表，靠 feature matching、bundle adjustment 與 plane sweeping/cost volume 達成高精度，但 handcrafted、optimization-heavy，難以擴展到大型或動態場景，亦難以即時部署。這條線確立了「離線、最佳化、難 real-time」這個歷史包袱，作為後續學習式方法的對照背景。

第二條是 Offline 3D reconstruction，沿 DUSt3R → MASt3R → VGGT → π3 的演進敘述。DUSt3R 從 image pair 直接回歸 pointmap 與相對 pose，但仍是 pairwise，需要全域對齊；MASt3R 加入 dense feature 與 reciprocal matching 提升匹配與校正穩健性，但仍 pairwise、多視角融合昂貴；VGGT 用單次 feed-forward 從多視圖預測 pose、depth、pointmap、track，但依賴 fixed reference frame 與 absolute pose 監督，造成 reference 與 scale bias；π3 透過 permutation-equivariant 設計移除 reference-view bias，但輸出在 global similarity transform 下仍為 ambiguous，缺 metric scale。這條線精準鋪陳出 LongStream 想要解決的兩個遺留問題：reference/anchor bias 與 scale ambiguity。

第三條是 Streaming 3D reconstruction，這是與本作最直接競爭的一線。CUT3R 用 RNN 維護 recurrent state 輸出 metric pointmap，但 RNN backbone 對長期依賴薄弱、長序列下退化；Stream3R 改用 causal Transformer + KV-cache，可擴展到長串流，但會出現 attention collapse；StreamVGGT 加上 temporal causal attention 與 cache update，並以 distillation 改善一致性，但長期 cache contamination 仍難控。作者明確總結：existing streaming methods degrade noticeably as sequences grow and fail to generalize to much longer streams——這句話正好呼應 Introduction 的失敗診斷，也合理化 §3 將提出的 gauge-decoupled formulation 與 cache-consistent training。整節未獨立寫 Preliminaries，但已透過上述三線把 SE(3)/Sim(3) gauge、KV-cache、attention sink、metric scale 等關鍵詞順勢嵌入論述脈絡，讓讀者進入 Methodology 時對術語不感陌生。

### 3.4 Method (overview narrative)

(1320 words)

Methodology 以「整體設計 → 形式化 → 架構 → 機率框架與損失 → 訓練/推論一致性」的順序鋪陳，並在每一節結尾自然地把問題帶向下一節。§3.1 Overall 把 LongStream 定義為一個 gauge-decoupled streaming geometry framework，在統一的 spatiotemporal Transformer 中聯合預測 pose、depth、scale，呼應 Figure 3 的整體流程：ViT encoder 產生 patch token，並擴增 Camera、Register、Scale token 以區分 keyframe 角色；這些 token 經 causal aggregator 與共享 KV cache 融合，使長序列 streaming inference 成為可能。對每一幀，模型輸出 keyframe-relative pose $T_{i\leftarrow k}$、depth、pointmap 與 global scale $s$，且訓練與推論共享同一 layout，為後文 cache-consistent training 預埋伏筆。

§3.2 Gauge-Decoupled Formulation 是全文理論核心。作者主張一個穩健的幾何學習系統必須對 gauge freedom（任意 global coordinate 與 metric scale）保持理論不變性，因此將 SE(3) 與 Sim(3) 自由度分離處理。對 SE(3)，放棄 absolute pose regression，改學 gauge-invariant 的 relative pose $T_{i\leftarrow k} = T_i \circ T_k^{-1}$，其中 $k$ 為前一個 keyframe。此式在任意世界座標重參數化 $S \in SE(3)$ 下保持不變，於是同時達成兩個目標：把長距 OOD extrapolation 問題轉成 bounded $(i-k)$ 的 in-distribution local task；並消除 first-frame anchor 帶來的不對稱位置偏置。對 Sim(3)，採 SI-Log 哲學的 orthogonal scale learning：幾何分支在 normalized 空間以 scale-invariant 原則監督，scale head 獨立預測 global scale factor $s$，從架構與目標兩個層級同時解 entanglement。

§3.3 Network Architecture 把抽象設計落到模組。每幀預測 $\{h_i, p_{i\leftarrow k}, D_i, X_i, s\} = F_\theta(I_i)$，其中 $p_{i\leftarrow k} = [t_{i\leftarrow k}, q_{i\leftarrow k}, f_{i\leftarrow k}]$ 包含 translation、unit quaternion、focal-length offset。整體沿 VGGT-style streaming 架構：DINOv2 tokenizer + causal Transformer aggregator + 多個 task head。Tokenizer 為每幀產生 patch feature 並擴增 camera/register token（keyframe 與 non-keyframe 用不同 token），再加入共享 Scale Token，所有 token 串成 $H^{(0)} \in \mathbb{R}^{B\times S \times (P+T) \times C}$，由交替 intra-frame 與 global attention 的 Transformer block 在 strictly causal mask 下處理。

Relative pose head 同時取當前幀與其 keyframe 的特徵，預測 $T_{i\leftarrow k}$。為了讓模型「只學 (i, k) 之間的相對關係」，作者採 reference-aware attention：non-keyframe $i$ 的 token 只能注意到 keyframe $k$ 與 $k$ 到 $i$ 之間的 frame；keyframe 的 token 則只能注意到上一個 keyframe $k-1$ 與其間 frame。聚合後將當前幀與 keyframe 的 pose token 串接、線性投影為 $h_{\text{fused}}$，再以 RAFT 風格的 AdaLN-modulated Transformer 進行迭代式預測 $p^{(t+1)} = p^{(t)} + \Delta p^{(t)}$。Scale head 接收專用 Scale Token，預測無約束的 log-scale 變數 $x_s$，再透過 $s = \exp(w^\top h_{\text{scale}})$ 取得正值 scale，且只影響 translation、depth、pointmap，不動 rotation 與 FOV；scale head 僅在具備 metric ground truth 的資料集上訓練。Depth 與 pointmap head 共用聚合後的 frame-level 與 patch-level 特徵，輸出 $D_i \in \mathbb{R}^{H\times W}$、$X_i \in \mathbb{R}^{H\times W \times 3}$ 與 per-pixel confidence；幾何在 scale-invariant 空間優化、ScaleToken 獨立學習全域 scaling，從而完整實現 Sim(3) gauge decoupling。

§3.4 Probabilistic Framework and Loss Functions 將 gauge-decoupled 設計嵌入統一的機率框架，把總目標寫為 negative log posterior

$$\mathcal{L} = \mathcal{L}_{\text{geom}} + \mathcal{L}_{\text{depth}} + \mathcal{L}_{\text{pose}} + \mathcal{L}_{\text{scale}},$$

對應於 $p(D, X, p, s \mid I) \propto p(D \mid X, I) \cdot p(X \mid p, s, I) \cdot p(p \mid I) \cdot p(s)$ 的因子分解。Pose loss 對 RelPoseHead 的迭代輸出 $p_{\text{rel}} = [t, q, f]$ 加 $\gamma^{t-1}$ 折扣的 L1 監督，translation 項 $\ell_t$ 在 normalized coordinate 中計算以避免隱含的 global scale；Geometry loss 採 SI 風格在 normalized 空間做 L1，使 $\partial \mathcal{L}/\partial s = 0$，確保 $\mathcal{L}_{\text{geom}}$ 只監督 backbone 學 3D 結構；Scale loss 在 log 空間比較 $\hat{s}$ 與 $s_{\text{gt}}$ 以衡量相對誤差並穩定梯度，且只對 metric-calibrated 樣本啟用。

§3.5 KV Cache and Train–Inference Consistency 把架構問題收尾。先指出 streaming Transformer 常依賴 attention sink 維穩，但這種對 first-frame 的 fragile reliance 在長序列下會造成幾何 saturation、attention 不穩、keyframe jump 與 pose error，且 relative-pose 監督也救不了，顯示 sink anchoring 本身就是一種不對稱位置偏置。作者主張「short-horizon collapse」其實不是移除 sink 的後果，而是 train–inference mismatch 的症狀，遂提出 Cache-Consistent Training（Algorithm 1）：訓練時顯式在 chunk 之間 pass & trim KV cache，使 cache visibility 與推論一致；同時移除常駐 sink token、改用純 causal + sliding window mask，讓訓練與逐幀推論在數學上等價（呼應 Figure 4 中 sink 被大幅抑制、RPE 同步下降）。對 ultra-long sequence，CCT 仍不足以阻止 KV 累積造成的 long-term memory saturation，於是再加上 periodic cache refresh：每 $N$ 個 keyframe hard-marginalize 過期 context，類似 SLAM 的 state marginalization；因為整個模型都在 keyframe-relative 座標系運作，cache 可在任一 keyframe 重置而不破壞一致性。CCT 與 periodic refresh 的組合最終達成跨千幀仍穩定、attention 分布良好的 streaming 推論，為 §4 的實驗結果奠定方法論基礎。

### 3.5 Experiments (overview narrative)

(720 words)

Experiments 一節以「實作配方 → 量化結果 → 質化結果 → 消融」的標準四段式展開，並在每一段都把焦點對回方法論的三大主張：gauge-decoupled、cache-consistent、long-sequence stability。§4.1 Implementation Details 先給出工程基線：LongStream 從 VGGT 初始化，沿用 24 層 backbone（global 與 frame-level attention 交替）、約 1.3B 參數；訓練採 fixed visibility layout、固定 sliding window、keyframe interval 設為 10，使每個 batch 包含多次 keyframe 切換以充分監督 relative-pose 行為。優化器為 AdamW + cosine decay，peak lr $4\times 10^{-6}$、warmup 1k step；影像、depth、pointmap 全部 resize 到長邊 518，輔以 aspect-ratio jittering、interval sampling、cross-block shuffling。訓練分兩階段：第一階段 batch-independent 訓練，batch size 22、50k iteration、32 張 A100、約三天；第二階段轉為 KV-cache–consistent training，序列長度在 10–80 之間取樣、cache window 為 10，metric scale 監督只在有校正 ground truth 時啟用。推論期單卡可達 18 FPS，呼應 Abstract 的工程承諾。訓練資料覆蓋 Kubric、WildRGB、ScanNet、HyperSim、Mapillary、Replica、MVS-Synth、PointOdyssey、Virtual KITTI、Aria Synthetic Environments、Aria Digital Twin、Objaverse、Spring、Waymo Open 等多領域資料集，其中 BlendedMVS、Co3Dv2、MegaDepth、DL3DV 因無 metric ground truth 而排除於 scale 訓練之外。Baseline 涵蓋 offline transformer、streaming model 與 SLAM-style 系統：因 VGGT 與 π3 在長 clip 會 OOM，改以 FastVGGT 作為實務替代；streaming 端納入 CUT3R、TTT3R、Stream3R、StreamVGGT，SLAM 端納入 MASt3R-SLAM 與 VGGT-SLAM，並特別註記 VGGT-SLAM 以 16/32 frame 的 chunk 推論、實際存取了未來 frame，藉此與本作的 strictly online 設定形成對照。

§4.2 Quantitative Results 以三類任務串起本方法的價值。Camera pose estimation 在 vKITTI（training）、Waymo（held-out）與未見過的 KITTI、TUM-RGBD、Oxford Spires 上以 ATE 衡量；作者明確指出 streaming baseline 隨序列增長呈非線性誤差成長（對應 Tables 1–3），歸因於 long-horizon history saturation 與 contamination，而 LongStream 保持穩定；offline 模型則頻繁 OOM 或 tracking loss。3D reconstruction 在 7Scenes 與 TUM 上以 Chamfer Distance 與 F1@0.25 衡量（Table 4），並提醒讀者這些資料集 spatial extent 小、frame 密集，metric 已多處飽和、且部分方法的 all-frame failure 會把平均 CD 推高數個量級。Scale estimation 則以 vKITTI 為基準，報告 LongStream 達 0.9905 的 scale ratio，呼應 Sim(3) 解耦在 metric scale 上的有效性。

§4.3 Qualitative Results 用 Figures 5、6 把量化故事視覺化：戶外 kilometer-level 場景中，Stream3R 與 StreamVGGT 累積漂移、VGGT-SLAM 受 memory 限制與 tracking loss 困擾，LongStream 則保持軌跡連續與 metric 準確，甚至在無顯式 loop closure 模組的情況下「成功閉合大型 loop」；室內高度折疊的軌跡（強烈視角變化、遮擋、反覆回走）下，baseline 多顯不穩，LongStream 仍維持 globally coherent trajectory，從而把方法的優勢延伸至小尺度但動作劇烈的場景。

§4.4 Ablation Study 在單一 vKITTI 序列上驗證四項核心元件：keyframe-relative pose head、scale branch、CCT、periodic cache refresh。Table 5 顯示組合全部模組可將 ATE 從 8.043 降到 0.115，近乎兩個量級。其中 absolute → gauge-decoupled pose 的切換貢獻最大（Row 1 → Row 2），印證「分離 local geometry 與 global coordinate」是長序列泛化的關鍵；scale branch 對 metric 一致性不可或缺；periodic cache refresh 則阻止無限 stream 下的長期記憶飽和。整體實驗故事與方法論主張完全對齊：先用三類任務證明全面 SOTA，再用消融把功勞精確分配給每一個設計決策。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

Conclusion 以一段精煉收束：LongStream 在超長序列上達成穩定的 metric-scale 重建，克服既有方法的 drift 與 extrapolation failure；其 gauge-decoupled pose 設計與 cache-consistent training 能跨越數千幀維持 geometry 與 scale 一致，並在多樣的室內外資料集上同時取得高精度與 real-time 表現。Limitations 段落坦承三點：模型假設場景大致為靜態、依賴一個啟發式 keyframe 排程、在極長 window 下 pointmap 一致性仍有輕微退化。作者把這些限制定位為未來工作的明確方向，而非不可逾越的設計缺陷。附錄 §11 進一步補充：LongStream 不做顯式 loop-closure 優化（Figure 8 顯示重訪同一地點時的輕微漂移），加入輕量級 online loop-closure cue 是改善 global consistency 的可行下一步。整體 Conclusion 與 Limitations 的論述語氣保守、與正文承諾一致，沒有過度延伸到未驗證的 future claim。

## 4. Critical Profile

### 4.1 Highlights

- 在嚴格 online、future-invisible 設定下，LongStream 於 KITTI 11 條序列上以平均 ATE 51.90 m 對比 StreamVGGT 的 226.15 m 達到約 4.4× 的軌跡誤差降低，並在最長的 KITTI 02（5.1 km、4661 frames）上把 StreamVGGT 的 303.35 m ATE 縮減至 134.70 m（Table 1, p.6）。
- 在 vKITTI 五個場景的平均 ATE 從 StreamVGGT 的 83.916 m 與 VGGT-SLAM 的 23.667 m 降至 1.610 m，Scene 20（711 m）上由 221.407 m 降至 4.030 m（Table 3, p.7）。
- 跨資料集泛化表現一致：TUM 0.076、Oxford Spires 19.815、Waymo 0.737 ATE，皆優於 SLAM 與其他串流基線（Table 2, p.7）。
- vKITTI 上 metric scale ratio 0.9905，顯示 orthogonal scale head 能在公里級序列維持穩定 metric 估計（§4.2 Scale estimation, p.8）。
- Ablation 顯示 RelPose head + Scale head + CCT + Cache Refresh 四件套將單一 vKITTI 序列 ATE 從 8.043 m 降至 0.115 m，約兩個數量級的改善，其中 absolute → keyframe-relative pose 帶來最大的單步增益（8.043 → 2.819）（Table 5, p.8）。
- 數學上證明 keyframe-relative pose $\mathbf{T}_{i\leftarrow k} = \mathbf{T}_i \mathbf{T}_k^{-1}$ 在任意 $\mathbf{G} \in \mathrm{SE}(3)$ world reparameterization 下嚴格不變，並透過 normalized geometry loss 達成 $\partial \mathcal{L}_{\text{geom}}/\partial s = 0$ 的 Sim(3) 正交解耦（Appendix §7, p.13）。
- Cache-Consistent Training 把訓練與逐幀推論的 attention 視野在數學上對齊，attention 視覺化顯示原本集中於第一幀的 sink 被顯著抑制，且 RPE 從 0.4667 降到 0.298（Figure 4, p.5；Figure 7, p.14）。
- 對比 VGGT 與 FastVGGT 在長序列出現 OOM 與線性增長的 latency，LongStream 在數千幀下保持穩定 memory 與 18 FPS 推論吞吐（Figure 2, p.2；§4.1, p.6）。
- 長序列穩定性測試中，KITTI #03（801 frames、561 m）相較 Stream3R 的 158.25 m ATE，LongStream 達到 3.81 m，且去除 cache refresh 變體仍維持 20.83 m，凸顯 sliding window + refresh 的疊加效益（Table 6, p.14）。
- 7Scenes 上 Chamfer Distance 2.260 為串流方法最佳，並在 F1@0.25 取得 0.641（次佳），驗證在小尺度室內場景同樣具競爭力（Table 4, p.8）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 模型仍假設場景大致為**靜態世界**，未處理動態物件，這是作者於 §5 Limitations 明確列出的限制（p.8）。
- 採用**啟發式 keyframe 排程**（固定 interval = 10），未學習自適應切換策略（§5, p.8；Appendix §10.1, p.14）。
- 在非常長的視窗下，pointmap consistency 出現**輕微退化**，attention 視覺化也顯示序列接近 80 frames 時注意力會逐步漂回早期歷史，與 cache saturation 一致（§5, p.8；Appendix §8, p.14）。
- **缺乏明確 loop-closure 機制**：當路徑回到同一地點時會出現 mild drift，作者明確將 online loop-closure 列為未來工作（Appendix §11, Figure 8, p.15）。
- KITTI 為 zero-shot 評測，但 vKITTI 同時用於訓練與評測，作者僅以「training」標註（§4.2, p.7），並未深入討論訓練／測試 leakage 風險。

#### 4.2.2 Phyra-inferred

- **Ablation 僅在「a single vKITTI sequence」上進行**（§4.4, p.8），單一軌跡無法支撐「兩個數量級改善」這類普遍性結論，特別是 Table 5 第 2、3 列的 ATE 落差作者自承來自「a few large trajectory outliers」，意味著 ablation 的訊號雜訊比相當低。
- **Periodic cache refresh 的 refresh interval 從未被定量 ablate**：論文僅說「every N keyframes」（p.6），但 §10.1 ablation 的 N 是 keyframe interval，與 refresh 週期是否相同不清楚，這個關鍵超參的敏感度因此完全未知。
- **與 baselines 的比較有大量 OOM／追蹤失敗（Table 1 中眾多「\*」）**，VGGT-SLAM、MASt3R-SLAM 在長序列基本無法跑完，使「SOTA」更接近「唯一能跑完」的結論而非 head-to-head 精度勝出。
- **CCT 在主文與 Figure 4／Figure 7 中以 SF-CCT 出現但從未定義**（p.5、p.14），讀者無法確認 SF-CCT 是否等同 CCT，或是否包含額外的 sliding-frame 機制。
- **Loss 式 (8) 中列出 $\mathcal{L}_{\text{depth}}$，但 §3.4 從未明確給出 depth loss 的形式與權重**，使 reproducibility 受損；式 (10) 的 $\gamma$ 衰減係數與式 (12) 與 $\mathcal{L}_{\text{geom}}$ 的相對權重也未列出。
- **Reference-aware attention** 規定「keyframe 僅 attend 到前一 keyframe $k-1$ 與其間 frames」（§3.3, p.4），在 keyframe 切換點等於主動切斷跨段資訊，但作者未量化這個設計對 keyframe 邊界的精度影響。
- **訓練成本龐大且未討論可重現性預算**：32 × A100 三天的第一階段加上 KV-cache 一致性第二階段（§4.1, p.7），但程式碼欄位為 `null`（BIBLIO），社群復現難度高。
- **Scale supervision 只用於 metric-calibrated 樣本**（§3.4, p.5），混合 metric 與非 metric 資料時對 scale head 是否產生 distribution skew 並未量化。

### 4.3 Phyra's Judgment (summary)

LongStream 真正新的貢獻是把「長序列退化」拆解為 SE(3)／Sim(3) 兩個 gauge 自由度的耦合 + train/inference KV cache 視野錯位，並用 keyframe-relative pose、orthogonal scale head 與 Cache-Consistent Training 三件相互獨立的設計同時消除，這是一條乾淨且有附錄證明支撐的因果鏈。其餘像 Scale Token、causal Transformer + KV cache、attention sink 觀察，多屬將既有工具（VGGT 主幹、MapAnything 的 scale token、StreamingLLM 的 sink 分析）對接到視覺幾何串流場景的工程整合。核心未解的問題是：在沒有 loop-closure、不處理動態世界、且 ablation 只在單一 vKITTI 序列上的條件下，論文聲稱的「公里級穩定 metric 重建」其上限與失效模式仍未被完整刻畫。

## 5. Methodology Deep Dive

### 5.1 Method Overview

LongStream 是一個建立在 VGGT-style 24 層 Transformer 主幹之上的串流式自迴歸視覺幾何模型，以單張影像 $I_i$ 為單位逐幀進入網路，經 DINOv2-based ViT tokenizer 抽取 patch tokens，並與 keyframe camera token、normal camera token、register tokens 以及共享的 scale token 串接後送入 causal aggregator。聚合器在嚴格因果遮罩下以「frame-level / global attention」交替堆疊（共 24 層），並在訓練與推論皆透過 shared KV cache 傳遞歷史上下文，使整段序列的計算複雜度由 offline 的 $O(S^2)$ 降為串流的 $O(S)$。最後依 token 角色分流到四個 heads：keyframe-relative pose head、orthogonal scale head、depth head 與 pointmap head（Sec. 3.1 / Sec. 3.3）。

該架構的兩個核心設計都直接落在「gauge」這個概念上。在 SE(3) 層面，模型不再回歸絕對位姿 $T_i$，而是預測 keyframe-relative pose $T_{i \leftarrow k} = T_i \circ T_k^{-1}$（Eq. 1 / Eq. 5）；這個重參數化在世界座標的右乘變換 $S \in SE(3)$ 下保持不變，並把長距外推問題重寫成 index gap $(i-k)$ 有界、難度恆定的 in-distribution 局部估計（Sec. 3.2）。在 Sim(3) 層面，幾何分支以 SI-Log 哲學在 scale-invariant 空間做 normalization，使 $\partial \mathcal{L}_{\text{geom}}/\partial s = 0$（Eq. 11），而獨立的 scale head 從專屬 scale token 預測 log-scale 並指數化為正純量 $s = \exp(\mathbf{w}^\top h_{\text{scale}})$（Eq. 7），尺度只回流到 translation、depth 與 pointmap，**不影響** rotation 與 FOV。

訓練與推論的對齊則由 Cache-Consistent Training（CCT）與 periodic cache refresh 完成。CCT 在訓練時以 chunk 為單位顯式傳遞並裁切 KV cache（Algorithm 1），讓訓練的 attention 視野在數學上等價於逐幀推論的滑動視窗，從而在不依賴 sink token 的情況下避免 short-horizon collapse；而 periodic cache refresh 則每 $N$ 個 keyframe 一次「硬性邊際化」過時上下文（重置 sink frame 與 KV cache，類似 SLAM 的 state marginalization），在 keyframe-relative 座標系下保持幾何連續性的同時清除老化特徵（Sec. 3.5）。第二階段以 cache window = 10、序列長度在 10$\sim$80 之間取樣的 KV-cache–consistent training 進一步把推論時的滑動視窗行為烘焙進權重，最終在單卡達到 18 FPS 推論並在公里級序列上保持穩定 metric scale（Sec. 4.1）。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: I_i ∈ [B, S, 3, H, W]              # H=W≤518 (long side capped); resize + aspect jitter
   │
   ▼
[1] ViT Tokenizer (DINOv2-based, frozen-init)
   │   patch features x_i^p ∈ [B, S, P, C]
   │   # P = (H/14)·(W/14) ≈ 1369 (518/14=37); C inherited from DINOv2 (paper does not specify)
   ▼
[2] Token Augmentation
   │   ├─ keyframe camera token (K-frames only)   ∈ [B, S_k, 1, C]
   │   ├─ normal camera token   (non-K frames)   ∈ [B, S_n, 1, C]
   │   ├─ register tokens                          ∈ [B, S, R, C]   # R = ?
   │   └─ scale token (shared across all frames)   ∈ [B, 1, 1, C]
   │   concat →  H^(0) ∈ [B, S, P+T, C]            # T = camera + R + scale
   ▼
[3] Causal Aggregator  (24 blocks; alternating intra-frame & global attention)
   │   with shared KV cache (sliding window W_c = 10 at inference / CCT)
   │   reference-aware mask: non-K_i attends only to K_k and frames in (k, i];
   │                         K_k attends only to K_{k-1} and frames in (k-1, k]
   │   H^(L) ∈ [B, S, P+T, C]                      # Eq. 3
   │
   ├──[4] Relative Pose Head  (AdaLN-modulated Transformer, RAFT-style iterative)
   │       h_fused = Proj([h_i, h'_k]) ∈ [B, S, C]                  # Eq. 6
   │       p^(t+1) = p^(t) + Δp^(t)  for t = 1..T_iter
   │       output: t_{i←k} ∈ [B, S, 3], q_{i←k} ∈ [B, S, 4],
   │               f_{i←k} ∈ [B, S, 2]                              # Eq. 4 / Eq. 10
   │
   ├──[5] Scale Head
   │       h_scale ∈ [B, C]  →  x_s = w^⊤ h_scale ∈ [B, 1]
   │       s = exp(x_s) ∈ [B, 1]  (>0)                               # Eq. 7
   │
   ├──[6] Depth Head
   │       D_i ∈ [B, S, H, W],  conf_D ∈ [B, S, H, W]
   │
   └──[6] Pointmap Head
           X_i ∈ [B, S, H, W, 3],  conf_X ∈ [B, S, H, W, 3]
                      ↑
   (geometry branch is normalized: ∂L/∂s = 0 ; s only re-applies at output time
    to translation / depth / pointmap, not to rotation / FOV)         # Eq. 11
```

### 5.3 Per-Module Breakdown

#### 5.3.1 ViT Tokenizer

**Function:** 將每張輸入影像獨立切 patch 並嵌入為 token 序列，作為下游 spatiotemporal Transformer 的視覺基底。

**Input:**
- Name: $I_i$
- Shape: `[B, S, 3, H, W]`，其中 $H, W \leq 518$（長邊上限）
- Source: 經 resize、aspect-ratio jittering、interval sampling、cross-block shuffling 後的訓練／推論影像（Sec. 4.1）

**Output:**
- Name: $x_i^p$
- Shape: `[B, S, P, C]`
- Consumer: Token Augmentation（[2]）

**Processing:**

每幀 $I_i$ 獨立通過 DINOv2-based tokenizer，切成 $P$ 個 non-overlapping patches 並嵌入到 $C$ 維特徵空間。tokenizer 在不同幀之間參數共享，亦不在此階段交換時序資訊，所有跨幀融合都留給 [3] aggregator。

**Key Formulas:**

$$
x_i^p \in \mathbb{R}^{P \times C}, \quad i = 1, \dots, S
$$

**Implementation Details:**

主幹以 VGGT 1.3B 權重初始化（Sec. 4.1），DINOv2 引用為 [48]。Patch size、$C$ 維度、register token 數量均未在正文中明示；以 DINOv2 慣例推論，$P \approx (518/14)^2 = 1369$，但「the paper does not specify」確切的 $C$ 與 $R$。

#### 5.3.2 Token Augmentation

**Function:** 在 patch tokens 之上拼接帶有「角色」語義的特殊 tokens，使 aggregator 能在 causal mask 下區分 keyframe / non-keyframe / scale，是 gauge-decoupled 設計能夠進入網路內部的入口。

**Input:**
- Name: $x_i^p$
- Shape: `[B, S, P, C]`
- Source: ViT Tokenizer

**Output:**
- Name: $H^{(0)}$
- Shape: `[B, S, P+T, C]`，其中 $T$ = camera token (1) + register tokens ($R$) + scale token (1)
- Consumer: Causal Aggregator（[3]）

**Processing:**

每幀按其在 keyframe schedule 中的角色取得對應的 camera token：keyframe 用「keyframe camera token」、非 keyframe 用「normal camera token」（兩者參數不同，但每個角色內部跨幀共享），加上若干 register tokens；接著對整個 batch / 整段序列附加一個共享的 scale token，用於 Sim(3) decoupling。所有 tokens 在 token 維度（軸 -2）concat 為 $H^{(0)}$。

**Key Formulas:**

$$
H^{(0)} \in \mathbb{R}^{B \times S \times (P+T) \times C}
$$

**Implementation Details:**

Scale token 的設計呼應同期工作 MapAnything [50]。Keyframe interval = 10（Sec. 4.1），保證每個 batch 內含多個 keyframe 轉換以供訓練。

#### 5.3.3 Causal Aggregator with Shared KV Cache

**Function:** 以嚴格因果方式融合所有 token 的時空資訊，並透過 shared KV cache 把跨 chunk 的歷史傳遞銜接成串流；reference-aware attention 把「相對於當前 keyframe」這個結構先驗灌進 attention pattern。

**Input:**
- Name: $H^{(0)}$
- Shape: `[B, S, P+T, C]`
- Source: Token Augmentation

**Output:**
- Name: $H^{(L)}$（$L = 24$）
- Shape: `[B, S, P+T, C]`
- Consumer: 4 個 task heads（Relative Pose / Scale / Depth / Pointmap）

**Processing:**

24 層 Transformer block 交替執行 intra-frame attention（在每幀內的 $P+T$ 個 token 之間 attend）與 global attention（跨幀 attend），全部受 causal mask 約束（Eq. 3）。Reference-aware attention 進一步收緊 mask：對於指派給 keyframe $k$ 的 non-keyframe $i$，其 tokens 只能 attend 到 $k$ 的 tokens 與 $(k, i]$ 之間幀的 tokens；keyframe $k$ 自己只能 attend 到上一個 keyframe $k-1$ 的 tokens 與 $(k-1, k]$ 之間幀的 tokens，而非整段歷史，這保證了「只學相對 (i, k)」的監督一致性（Sec. 3.3）。KV cache 在 chunk 間以 `trim(KV_new, window_size)` 滑動裁切（Algorithm 1），cache window = 10。

**Key Formulas:**

$$
H^{(l+1)} = \text{Block}^{(l)}\bigl(H^{(l)}, \text{AttnMask}\bigr)
$$

**Implementation Details:**

24 層、約 1.3B 參數，自 VGGT 初始化（Sec. 4.1）。Periodic cache refresh 每 $N$ 個 keyframe 重置 sink frame 與 KV cache，由於整模型運行在 keyframe-relative 座標系，重置不會破壞幾何一致性（Sec. 3.5）。$N$ 的具體值文中未明示。

#### 5.3.4 Keyframe-Relative Pose Head

**Function:** 從聚合特徵預測當前幀相對於其 reference keyframe 的相對位姿，是 gauge-decoupled 在輸出層的具體實現。

**Input:**
- Name: $h_i$（當前幀 frame token）與 $h'_k$（reference keyframe 對應 token）
- Shape: 各為 `[B, S, C]`
- Source: Causal Aggregator 的對應 token 通道

**Output:**
- Name: $\mathbf{p}_{i \leftarrow k} = [\mathbf{t}_{i \leftarrow k}, \mathbf{q}_{i \leftarrow k}, f_{i \leftarrow k}]$
- Shape: `t ∈ [B, S, 3]`, `q ∈ [B, S, 4]`（unit quaternion）, `f ∈ [B, S, 2]`（focal offset）
- Consumer: 由 $T_{i \leftarrow k} = T_i T_k^{-1}$ 重組成相機外參，下游用於軌跡與相對 pointmap 的對齊（Eq. 4 / Eq. 5）

**Processing:**

先把 $h_i$ 與 $h'_k$ 在通道維 concat 後通過線性投影得 $\mathbf{h}_{\text{fused}} = \text{Proj}([\mathbf{h}_i, \mathbf{h}'_k])$（Eq. 6）；接著仿照 RAFT [49] 的設計，由一個 AdaLN-modulated Transformer 在 $T$ 個 iteration 內以增量更新方式收斂相對位姿：$\mathbf{p}^{(t+1)} = \mathbf{p}^{(t)} + \Delta \mathbf{p}^{(t)}$。Translation 在 normalized coordinate space 計算其 L1 損失，避免 translation 監督隱式編碼 global scale。

**Key Formulas:**

$$
\mathcal{L}_{\text{pose}} = \sum_{t=1}^{T} \gamma^{t-1} \Bigl( \ell(\hat{q}^{(t)}, q_{i \leftarrow k}) + \ell_t(\hat{t}^{(t)}, t_{i \leftarrow k}) + \ell(\hat{f}^{(t)}, f_{i \leftarrow k}) \Bigr)
$$

**Implementation Details:**

$\ell$ 為 L1 loss，$\gamma$ 為 RAFT-style discount factor（具體值文中未明示）。Iterative 步數 $T$、AdaLN 的條件來源、以及 quaternion 的歸一化策略（投影到單位球或在 loss 中加正則）皆未在正文中具體給出。

#### 5.3.5 Orthogonal Scale Head

**Function:** 從 scale token 抽取一個全域的正純量，作為 Sim(3) gauge 中唯一承擔尺度的旋鈕；幾何分支在 scale-invariant 空間最佳化，由此 head 單獨吸收尺度。

**Input:**
- Name: $h_{\text{scale}}$
- Shape: `[B, C]`，取自 aggregator 最後一層 scale token 的特徵
- Source: Causal Aggregator

**Output:**
- Name: $s$
- Shape: `[B, 1]`（嚴格正實數）
- Consumer: 在 metric-calibrated 樣本上回乘 translation、depth、pointmap；不影響 rotation 與 FOV

**Processing:**

線性層輸出無約束 log-scale $x_s \in \mathbb{R}$，再經 $\exp$ 映射為正純量 $s$（Eq. 7）。在訓練時對 metric-calibrated 樣本以 log-space L1 比較預測與 ground truth：$\mathcal{L}_{\text{scale}} = \|\log \hat{s} - \log s_{\text{gt}}\|_1$（Eq. 12），對 multiplicative scale 給出對稱的相對誤差。

**Key Formulas:**

$$
s = \exp\bigl(\mathbf{w}^\top \mathbf{h}_{\text{scale}}\bigr)
$$

**Implementation Details:**

只在具備 metric ground truth 的資料集上監督；BlendedMVS [71]、Co3Dv2 [72]、MegaDepth [73]、DL3DV [74] 等不具 metric ground truth 的資料集在訓練時排除於 scale loss 之外，但仍貢獻 geometry / depth losses（Sec. 4.1 Training data）。

#### 5.3.6 Depth Head and Pointmap Head

**Function:** 從聚合特徵預測 per-pixel 深度與世界座標 3D 點圖，並輸出 per-pixel 信心度；這兩個 head 共同構成幾何分支，在 scale-invariant 空間學形狀，由 scale head 單獨負責尺度。

**Input:**
- Name: 聚合後的 frame-level 與 patch-level 特徵
- Shape: 等價於 `[B, S, P+T, C]` 中對應通道，經 head 內部上採樣到影像分辨率
- Source: Causal Aggregator

**Output:**
- Name: $D_i$（depth）與 $X_i$（pointmap）
- Shape: $D_i \in$ `[B, S, H, W]`、$X_i \in$ `[B, S, H, W, 3]`，伴隨 per-pixel 信心度（同 spatial 形狀）
- Consumer: 串流重建輸出；$X$ 經 normalization 後計算 $\mathcal{L}_{\text{geom}}$（Eq. 11）

**Processing:**

幾何分支以「先 normalize 再比較」的方式去除尺度依賴：

$$
\tilde{X}_{\text{pred}} = \frac{\hat{X}_{\text{raw}}}{\text{Norm}(\hat{X}_{\text{raw}})}, \qquad \tilde{X}_{\text{gt}} = \frac{X}{\text{Norm}(X)}, \qquad \mathcal{L}_{\text{geom}} = \|\tilde{X}_{\text{pred}} - \tilde{X}_{\text{gt}}\|_1
$$

如此 $\partial \mathcal{L}_{\text{geom}}/\partial s = 0$，gradient 不會把尺度回灌到 backbone；尺度由 [5] scale head 在輸出時統一回乘到 translation / depth / pointmap。Depth 分支的損失 $\mathcal{L}_{\text{depth}}$ 在 likelihood 分解中對應 $p(D \mid X, I)$（Eq. 8 / Eq. 9）。

**Key Formulas:**

$$
p(D, X, p, s \mid I) \propto p(D \mid X, I) \cdot p(X \mid p, s, I) \cdot p(p \mid I) \cdot p(s)
$$

**Implementation Details:**

Norm 函數的具體形式（如 trimmed mean depth、median scale 等）、信心度的參數化（softplus / sigmoid / per-pixel scalar）、以及 head 內部的解碼結構（DPT-style upsampler 或卷積上採樣）皆未在正文中明示。

#### 5.3.7 Cache-Consistent Training and Periodic Cache Refresh

**Function:** 把「訓練時看到的 attention pattern」與「逐幀串流推論的 attention pattern」在數學上對齊，從根源上消除 attention sink 依賴與 short-horizon collapse；並週期性地清除老化上下文以對抗無限串流下的長期記憶飽和。

**Input:**
- Name: chunked frames $\{c_1, \dots, c_N\}$ 與初始空 cache $\text{KV}^{(0)} = \emptyset$
- Shape: 每個 chunk 為 `[B, S_chunk, 3, H, W]`，cache 為 KV 張量列表
- Source: 訓練資料載入器（從 Kubric, WildRGB, ScanNet, HyperSim, Mapillary, Replica, MVS-Synth, PointOdyssey, vKITTI, Aria Synthetic Environments, Aria Digital Twin, Objaverse, Spring, Waymo Open 等資料集中採樣，序列長度 10$\sim$80）

**Output:**
- Name: per-chunk 預測 $\text{out}_i$ 與裁切後的 KV cache $\text{KV}^{(i)}$
- Shape: out 同各 head 的形狀；KV cache 受 sliding window 限制
- Consumer: 下個 chunk 的 aggregator forward

**Processing:**

訓練流程按 Algorithm 1：對每個 chunk $c_i$ 以 $(\text{out}_i, \text{KV}^{\text{new}}) = \text{model}(c_i, \text{KV}^{(i-1)})$ 前向，再以 $\text{KV}^{(i)} = \text{trim}(\text{KV}^{\text{new}}, \text{window\_size})$ 裁切 KV cache。訓練時**移除**常駐的 sink token，採用純 causal masking 加 sliding window，使訓練 attention 與逐幀推論的 attention 在數學上等價（Sec. 3.5、Figure 4）。Periodic cache refresh 則在每 $N$ 個 keyframe 重置 sink frame 與 KV cache，以「硬性邊際化」過時 context；因為網路工作在 keyframe-relative 座標系，cache 可在任意 keyframe 上 refresh 而不破壞一致性。

**Key Formulas:**

$$
\text{KV}^{(i)} = \text{trim}\bigl(\text{model}(c_i, \text{KV}^{(i-1)})_\text{KV}, \, \text{window\_size}\bigr)
$$

**Implementation Details:**

兩階段訓練：第一階段為 batch-independent 訓練，batch size = 22、50k iterations、3 天於 32 張 A100；第二階段為 KV-cache–consistent training，序列長度在 10$\sim$80 之間取樣、cache window = 10（Sec. 4.1）。優化器 AdamW、cosine decay、peak lr = $4 \times 10^{-6}$、warmup = 1k steps。Periodic cache refresh 的 $N$（每幾個 keyframe 重置一次）與 trim 的具體實作（哪些 tokens 永遠保留、哪些被驅逐）文中未進一步明示，但 Figure 3 已標示 cache 中部分 token 為「Cached」、部分為「Evicted」。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| Kubric [60] | 合成多視角影像生成 | 大規模合成資料 | train |
| WildRGB [61] | 真實 RGB-D 物件影片 | 多場景 | train |
| ScanNet [62] | 室內 RGB-D 重建 | 數百個場景 | train |
| HyperSim [63] | 室內合成影像 | 高擬真合成 | train |
| Mapillary [64] | 戶外街景深度 | 行星級資料 | train |
| Replica [65] | 室內擬真重建 | 多個房間 | train |
| MVS-Synth [66] | 多視角合成 | 合成資料 | train |
| PointOdyssey [67] | 長時 point tracking | 大規模合成 | train |
| Virtual KITTI [59] | 戶外駕駛合成 | Scene 01/02/06/18/20，最長 837 幀、711 m | train + test (作為 ablation 與 pose 主評估之一) |
| Aria Synthetic Environments [68] | 第一人稱合成 | 大規模 | train |
| Aria Digital Twin [68] | 第一人稱真實/合成 | 大規模 | train |
| Objaverse [69] | 3D 物件 | 大規模 | train |
| Spring [70] | 高解析光流/立體 | 高細節 | train |
| Waymo Open [57] | 戶外駕駛 | 含 #520018670 等長序列 | train (held-out for evaluation) |
| BlendedMVS [71] | 多視角立體 | 大規模 | train（不含 metric scale 監督） |
| Co3Dv2 [72] | 物件多視角 | 大規模 | train（不含 metric scale 監督） |
| MegaDepth [73] | 網路相片深度 | 大規模 | train（不含 metric scale 監督） |
| DL3DV [74] | 場景多視角 | 10K 場景 | train（不含 metric scale 監督） |
| KITTI [51] | 戶外駕駛 pose | 序列 00–10，最長 4661 幀 / 5.1 km | test (unseen) |
| TUM-RGBD [55] | 室內 RGB-D | 室內小尺度軌跡 | test (unseen) |
| Oxford Spires [56] | 大尺度 LiDAR-視覺 | 大尺度戶外 | test (unseen) |
| 7Scenes | 室內 RGB-D 重建 | 室內小場景 | test (重建評估) |
| ETH3D | 室內外重建 | 多場景 | 摘要中提及但 §6 表格未列出對應結果，the paper does not specify experimental usage |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| ATE (Absolute Trajectory Error, m) | 估計軌跡與 ground-truth 軌跡之絕對位置誤差，數值越低越好 | yes |
| RPE (Relative Pose Error) | 相鄰或局部相對位姿誤差，用於 ablation 與 attention 分析熱圖 | yes |
| Scale Error | 預測 metric scale 與 GT 之絕對偏差（log-space 比例），越低越好 | no |
| Chamfer Distance (CD) | 預測點雲與 GT 點雲之雙向最近鄰距離，越低越好 | no |
| F1@0.25 | 以 0.25 m 為閾值的點雲 F1 score，越高越好 | no |
| FPS | 推論吞吐量（單 GPU），用以驗證 real-time 主張 | no |
| Memory / Latency 曲線 | 隨序列長度成長的記憶體與延遲 (Figure 2)，用於與 VGGT/FastVGGT OOM 對比 | no |

### 6.3 Training and Inference Settings

- Backbone：自 VGGT 初始化，保留 24 層、global 與 frame-level attention 交替結構，約 1.3B 參數。
- Optimizer 與 schedule：AdamW + cosine decay；peak learning rate $4 \times 10^{-6}$，warmup 1k steps。
- Stage 1（batch-independent training）：batch size 22，50k iterations，於 32 張 A100 上約三天。
- Stage 2（KV-cache–consistent training, CCT）：以 sequence length 10–80 取樣，cache window 固定 10；keyframe interval 為 10，使每個 batch 涵蓋多次 keyframe 切換。
- 影像處理：images / depths / pointmaps resize 至長邊最多 518 px，並做 aspect-ratio jittering、interval sampling、cross-block shuffling。
- Metric scale 監督：僅在具校正 GT depth 的資料集上啟用 $\mathcal{L}_{\text{scale}}$，BlendedMVS / Co3Dv2 / MegaDepth / DL3DV 不參與 scale 訓練。
- Inference：單 GPU 達 18 FPS（GPU 規格 the paper does not specify，僅在 §1、§4.1、Figure 1 報告 18 FPS）。Cache window 推論時為 10，並啟用 periodic cache refresh，每 N 個 keyframes 重置 sink frame 與 KV cache（詳見 §10 附錄）。
- 進一步細節（如 dataset sampling weights、resume / EMA 等）作者註明 "Further implementation details are available in the Appendix"。

### 6.4 Main Results

KITTI ATE (m, ↓), 11 序列平均（Table 1，節選）：

| Method | KITTI 00 | KITTI 03 | KITTI 04 | KITTI 09 | Avg. | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| FastVGGT [75] | OOM | 62.38 | 10.27 | 194.75 | 189.29 | offline，多序列 OOM |
| MASt3R-SLAM [34] | OOM | 18.87 | 88.98 | OOM | 177.93 | optimization-based SLAM |
| VGGT-SLAM [58] | OOM | 169.83 | 13.12 | OOM | 263.37 | chunk-wise，可窺見 future frames |
| CUT3R [45] | 185.89 | 148.06 | 22.17 | 205.94 | 209.78 | RNN streaming |
| TTT3R | 190.93 | 105.28 | 11.62 | 211.01 | 177.73 | streaming |
| STream3R [1] | 190.98 | 158.25 | 102.73 | 216.31 | 227.77 | causal Transformer streaming |
| StreamVGGT [2] | 191.93 | 157.50 | 108.24 | 216.69 | 226.15 | streaming |
| **Ours (LongStream)** | **92.55** | **3.81** | **1.95** | **85.61** | **51.90** | 全序列最佳，18 FPS |

vKITTI / TUM / Oxford Spires / Waymo ATE (m, ↓)（Table 2、Table 3 節選）：

| Method | vKITTI Avg. | TUM | Oxford Spires | Waymo |
| --- | --- | --- | --- | --- |
| FastVGGT | 31.427 | 0.418 | 36.577 | 1.281 |
| MASt3R-SLAM | 98.714 | 0.082 | 37.728 | 7.625 |
| VGGT-SLAM | 23.667 | 0.123 (0.053†) | 31.003 | 7.431 |
| CUT3R | 55.276 | 0.542 | 32.440 | 9.396 |
| TTT3R | 28.099 | 0.308 | 36.214 | 3.486 |
| STream3R | 82.815 | 0.633 | 37.569 | 42.203 |
| StreamVGGT | 83.916 | 0.627 | 37.255 | 45.101 |
| **Ours (LongStream)** | **1.610** | **0.076** | **19.815** | **0.737** |

3D 重建（Table 4）：

| Method | 7Scenes CD ↓ | 7Scenes F1@0.25 ↑ | TUM CD ↓ | TUM F1@0.25 ↑ |
| --- | --- | --- | --- | --- |
| FastVGGT | 6.373 | 0.710 | 0.104 | 0.926 |
| MASt3R-SLAM | 5.987 | 0.691 | 0.057 | 0.954 |
| VGGT-SLAM | 6.306 | 0.696 | 1.993 | 0.633 |
| CUT3R | 6.281 | 0.274 | 0.474 | 0.533 |
| TTT3R | 6.231 | 0.260 | 0.249 | 0.792 |
| STream3R | 6.353 | 0.479 | 1.126 | 0.444 |
| StreamVGGT | 6.630 | 0.483 | 0.680 | 0.402 |
| **Ours (LongStream)** | **2.260** | 0.641 | 0.225 | 0.673 |

Scale estimation：vKITTI 上 LongStream 之 scale ratio 為 0.9905（接近 GT 的 1.0），驗證 metric-scale 一致性。

註：論文宣稱在所有「online benchmarks」皆達 SoTA；TUM / 7Scenes 的 CD 與 F1 在 offline SLAM-style baseline 上仍略遜，作者解釋為小場景指標已飽和、且其他方法在某些 scene 失敗造成 mean CD 被放大。

### 6.5 Ablation Studies

於 vKITTI 單一序列上進行（Table 5、Table 6、Table 7、Table 8）：

- **Gauge-decoupled relative pose（RelPose 開關）**：自 absolute pose regression 切換為 keyframe-relative pose，ATE 自 8.043 → 2.819（RPE 2.207 → 0.750）。為四項元件中單一收益最大者，直接驗證去除 first-frame anchor 對 long-range 外推的必要性，是診斷性而非僅為 sanity check。
- **Scale Head**：加入後 ATE 2.819 → 2.645、RPE 0.750 → 0.484、Scale Error 達 0.010。診斷 Sim(3) 解耦對 metric 一致性的貢獻；但作者註記 row 2 vs row 3 的 ATE 差距主要來自少數軌跡 outliers，需謹慎解讀。
- **Cache-Consistent Training (CCT)**：再加入後 ATE 2.645 → 0.984、RPE 0.484 → 0.454。直接針對 train–inference 不一致這個假設提供證據，搭配 Figure 4 / Figure 7 的 attention map 可確認 attention sink 被顯著抑制，是診斷性實驗。
- **Periodic Cache Refresh**：完整啟用後 ATE 0.984 → 0.115、RPE 0.454 → 0.126，整體相對於最弱基線降低近兩個數量級。針對 KV-cache saturation 假設給出證據，並在 §9 Table 6 進一步呈現「無 refresh 變體 (w/o SW)」隨序列長度成長之差異（如 KITTI #03 801 幀：20.83 vs 3.81），具備診斷性。
- **Keyframe interval $N$（附錄 §10.1, Table 7）**：$N=1$ 退化為 frame-to-frame tracking（ATE 4.047）；$N=15$ 因 22 幀 chunk 內 keyframe 切換過稀導致學不穩 (ATE 1.398)；$N=10$ 為最佳 (ATE 0.115)。屬於合理的超參掃掠，部分結果偏向 sanity check。
- **Cache window size $W$（附錄 §10.2, Table 8）**：$W=10$ ATE 0.115，$W=20$ 0.119，$W=30$ 0.516。直接檢驗作者「geometric saturation」論點，屬診斷性。

整體而言，主 ablation 是診斷性的（每一行都對應一個明確的設計假設），但僅在「single vKITTI sequence」上完成，跨資料集的 ablation generalization 並未報告。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 同時與 streaming SoTA (STream3R, StreamVGGT, CUT3R, TTT3R) 與 SLAM-style / offline baseline (MASt3R-SLAM, VGGT-SLAM, FastVGGT) 對比 (Table 1–4)。
- [covered] Has cross-task / cross-dataset evaluation — 涵蓋 KITTI、vKITTI、Waymo、TUM、Oxford Spires、7Scenes，且任務橫跨 pose estimation、3D reconstruction (CD/F1)、metric scale。
- [covered] Has ablations that diagnose the new components — Table 5 對 RelPose / Scale Head / CCT / Cache Refresh 逐項加減；Figure 4、Figure 7 透過 attention map 與 RPE heatmap 直接檢驗 attention sink 假設。
- [partial] Has a scaling study — §9 Table 6 以 15× / 30× / 60× / 199× / 801× 幀做序列長度掃掠，屬「length scaling」；但模型大小或計算量的 scaling study 並未提供。
- [partial] Has an efficiency / wall-clock comparison — Figure 2 給出 memory / latency 隨序列長度的曲線並標示 VGGT/FastVGGT OOM，並反覆宣稱 18 FPS，但未提供與所有 baseline 的逐序列 wall-clock 表格、亦未說明 GPU 規格（the paper does not specify）。
- [missing] Reports variance / standard deviation / multiple seeds — 全文僅報告單次數字，無 seed 平均、std 或信賴區間。
- [partial] Releases code / weights / data sufficient for reproducibility — 提供 Project Page (`https://3dagentworld.github.io/longstream/`) 與訓練資料清單、超參數，但論文文本未明確承諾 code/weights release，the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1：Keyframe-relative pose 系統性消除 first-frame anchor 依賴並把長距外推改寫為 constant-difficulty 局部任務。**
  *支持。* 數學上由 Appendix §7.1（p.13）證明 SE(3) gauge invariance，實驗上由 Table 5 第 1→2 列 ATE 8.043 → 2.819（p.8）以及 Figure 5 的長軌跡視覺化（p.6）支撐。但「constant-difficulty」是邏輯主張，論文未提供 index gap $i-k$ 與 RPE 的關係曲線，因此屬於「結構正確、量化未完整」。

- **Claim 2：Orthogonal scale learning 完全解耦幾何與 metric scale。**
  *支持。* Appendix §7.2（p.13）證明 $\partial \mathcal{L}_{\text{geom}}/\partial s = 0$，vKITTI scale ratio 0.9905（§4.2, p.8）支持其穩定性。但 Table 5 顯示加入 cache refresh 後 Scale Err. 反而從 0.032 升至 0.035，提示尺度與 cache 機制之間仍有耦合，作者未討論。

- **Claim 3：Cache-Consistent Training 對齊訓練／推論視野，suppresses attention sink。**
  *支持。* Figure 4 / Figure 7 的 attention map 直接視覺化 sink 抑制，且 RPE 從 0.4667 降至 0.298。但因 Figure 4 命名為「SF-CCT」而正文僅定義 CCT，結論的可驗證性受損。

- **Claim 4：Periodic cache refresh 邊際化老化上下文，使串流可延展至數千幀。**
  *部分支持。* Table 6（p.14）顯示「Ours w/o SW」在 KITTI #03 為 20.83 m，加上 refresh 後降至 3.81 m，差距顯著。但論文未 ablate refresh 週期本身，也未在多條 ≥1000 frames 序列上做 controlled comparison，因此「數千幀穩定」更多由 Figure 1 的單條 2.45 km 軌跡圖支撐，屬於「有效但未充分量化」。

- **Claim 5：在 strictly online、future-invisible 設定下達到 SOTA。**
  *部分支持／略有 overclaim。* Table 1–4 的 streaming 區塊確實全面領先，但同表中的 SLAM／offline 基線大量「\*」（OOM 或 tracking lost），導致「online 設定下的 SOTA」更像是「online 是唯一能完成長序列推論的設定」。對 FastVGGT、VGGT-SLAM 的「practical replacement」做法降低了直接可比性。

### 7.2 Fundamental Limitations of the Method

**Keyframe boundary 的資訊瓶頸。** Reference-aware attention 限制 keyframe $k$ 只 attend 到 $[k-1, k]$ 區間內的 frames（§3.3, p.4），這在 keyframe 切換點構成 information bottleneck。當 cache refresh 又週期性清除 keyframe 上的 sink 與 KV 時，跨段相依性僅由 fused $\mathbf{h}_{\text{fused}} = \text{Proj}([\mathbf{h}_i, \mathbf{h}'_k])$ 這個線性投影承載。對於在 keyframe 切換瞬間出現的快速旋轉、遮擋或視角跳變，這個瓶頸將難以由訓練資料覆蓋，而論文也未在 ablation 中量化邊界誤差。

**靜態世界假設與 metric scale 學習的耦合。** Scale head 僅以 metric-calibrated GT depth 監督（§3.4, p.5），但訓練資料同時混入 BlendedMVS、Co3Dv2、MegaDepth、DL3DV 等非 metric 集合。動態物件在這些非 metric 集合上對 SI-normalized geometry loss 的貢獻並未被處理，因此當推論場景含動態物件時，scale head 可能繼承「以靜態結構定錨」的偏差。這是一個方法層面的結構問題，加更多資料無法直接解決，需要顯式 motion masking 或 multi-hypothesis scale。

**Cache window 與長期記憶的硬性折衷。** Table 8（p.15）顯示 W=30 已使 ATE 從 0.115 升至 0.516，作者解釋為「geometric saturation」。這代表方法本質上**靠遺忘維持穩定**，而非真正建模長期相依性。對於需要回憶遠端線索的任務（loop-closure、跨 room re-identification），方法在當前公式下沒有可擴充路徑：擴大 W 即崩潰，refresh 又主動清除歷史，因此「長序列穩定」與「長距 memory」在此架構中是互斥的。

**Train-time 與 inference-time 等價性的代價。** CCT 把 training pipeline 鎖死在「chunk + trim」的固定 layout，使訓練 batch 必須遵守 sliding-window 視野。這在實作上限制了 batch independence、cross-block 並行與資料效率（§4.1 提及 batch-independent 為第一階段、cache-consistent 為第二階段，p.7），並暗示更大的 cache window 或可變視野需要重新訓練而非僅推論時切換，從而把「streaming geometry」的可擴充性綁死在訓練時的固定窗口。

### 7.3 Citations Worth Tracking

- **[1] STream3R (Lan et al., 2025)** — 直接 baseline 與 attention collapse 觀察的源頭；理解其 cache 設計才能判斷 LongStream 的差分增益是否來自 CCT 或 keyframe-relative pose。
- **[2] StreamVGGT (Zhuo et al., 2025)** — 同樣 VGGT-based 串流模型，含 distillation 與 temporal causal attention，是檢驗 LongStream「gauge-decoupled」是否真為必要的對照。
- **[15] VGGT (Wang et al., 2025)** — LongStream 的初始化主幹（1.3B），其 absolute pose supervision 與 reference-frame bias 是本文要打破的目標，理解其失效模式對驗證貢獻歸屬至關重要。
- **[22] StreamingLLM (Xiao et al., 2024)** — Attention sink 概念的原始來源；本文把 sink 觀察從 LLM 平移到視覺幾何串流，回讀原文能釐清 sink 是「機制本身需要」還是「train/inference mismatch 症狀」這個爭論的根據。
- **[50] MapAnything (Keetha et al., 2026)** — 同期使用 scale token 的工作，作者明確標為 concurrent；對照閱讀有助於釐清 LongStream 的 orthogonal scale 是否在 token 設計層面具備獨立性。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] Periodic cache refresh 的 refresh 週期 $N_{\text{refresh}}$ 與 keyframe interval $N_{\text{kf}}=10$ 是否相同？若不同，refresh 週期的敏感度為何，§10 為何未 ablate？
- [ ] Figure 4 與 Figure 7 中的「SF-CCT」是否等同正文 §3.5 定義的 CCT？若否，「SF」代表的 sliding-frame 變體與 CCT 的差異為何？
- [ ] Loss 式 (8) 中的 $\mathcal{L}_{\text{depth}}$ 具體形式、與 $\mathcal{L}_{\text{geom}}$、$\mathcal{L}_{\text{scale}}$ 的權重比，以及式 (10) 的衰減係數 $\gamma$ 取值，論文均未給出，能否復現？
- [ ] Table 5 顯示加入 cache refresh 後 Scale Err. 反而由 0.032 升至 0.035，這是否暗示 refresh 在重置 sink 時連帶擾動 Scale Token 的特徵？
- [ ] 在含動態物件場景（如 KITTI tracking、Waymo 動態 scene）下，scale head 因 SI-normalized loss 不直接看到動態結構，metric scale 是否會被靜態背景偏差地校準？
- [ ] Reference-aware attention 在 keyframe 切換點的 information bottleneck 對快速旋轉／遮擋場景貢獻多少誤差？是否能用 keyframe-boundary RPE 單獨量化？
- [ ] Table 1 中眾多 baselines 出現「\*」（OOM／tracking lost），若改以 chunked inference 給予所有 baselines 同等資源，平均 ATE 排名是否會改變？

### 8.2 Improvement Directions

1. **顯式定義並 ablate periodic cache refresh 週期。** 把 $N_{\text{refresh}}$ 從 keyframe interval 解耦為獨立超參，在 vKITTI Scene 20 與 KITTI 02 上掃 $N_{\text{refresh}} \in \{5, 10, 20, 40\}$，可直接回答「refresh 抑制 saturation 還是 keyframe 切換抑制 saturation」這個目前混淆的因果問題；可行性最高，僅需推論時掃描。
2. **加入輕量 online loop-closure cue。** 作者在 Appendix §11 已自承這是 mild drift 的根因，且 keyframe-relative pose 已天然提供 pose graph 的邊；在 keyframe 之間以 patch token similarity 觸發 relative-pose constraint 並做小型 PGO，預期在大 loop（如 vKITTI Scene 01、KITTI 00）上消除 revisit drift，且不破壞 streaming 性質。
3. **動態物件 motion masking 進入 geometry loss。** 用現成 video segmentation 或 optical-flow consistency 產生 dynamic mask，在 $\mathcal{L}_{\text{geom}}$ 與 $\mathcal{L}_{\text{scale}}$ 上對 dynamic pixel 加權為零，可直接緩解作者承認的 static-world 假設限制；風險是增加資料 pipeline 複雜度。
4. **Hierarchical / sparse cache 取代「全部清除」式 refresh。** 目前 refresh 與 W=30 即崩潰兩者顯示「長期 memory」與「穩定性」互斥；改為兩層 cache（短期 dense + 長期 sparse keyframe-only），可在不增加計算量的前提下保留遠端線索，理論基礎是 keyframe-relative formulation 已使任意 keyframe 都是有效錨點。
5. **可學習的 keyframe schedule。** 以 frame-level feature 距離或預測 RPE 不確定度作為觸發條件，取代固定 interval = 10；在快速運動或遮擋場景下動態縮短 keyframe 間距，符合作者列為 future work 的方向；可行性中等，需要重新設計第二階段訓練的視野對齊。
6. **多假設 / 多尺度 Scale Token。** 在大尺度室外與小尺度室內混訓時，單一全域 $s$ 容易被資料分佈拉扯；引入 per-keyframe scale token + 連續性正則項，可在不違反 SI-Log 哲學下提供局部 metric flexibility，預期在 7Scenes（CD 2.260 仍偏高）與 Oxford Spires 同時改善。
