<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# DriveVGGT — DriveVGGT: Calibration-Constrained Visual Geometry Transformers for Multi-Camera Autonomous Driving

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | DriveVGGT |
| Paper full title | DriveVGGT: Calibration-Constrained Visual Geometry Transformers for Multi-Camera Autonomous Driving |
| arXiv ID | 2511.22264 |
| Release date | 2026-03-30 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2511.22264 |
| PDF link | https://arxiv.org/pdf/2511.22264 |
| Code link | https://github.com/SII-skyboard/DriveVGGT |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Xiaosong Jia | Institute of Trustworthy Embodied AI, Fudan University | https://jiaxiaosong1002.github.io/ | first author (equal contribution) |
| Yanhao Liu | Shanghai Jiao Tong University; Shanghai Innovation Institute | — | co-first author (equal contribution) |
| Yu Hong | Shanghai Jiao Tong University; Shanghai Innovation Institute | — | author |
| Renqiu Xia | Shanghai Jiao Tong University | — | author |
| Junqi You | Shanghai Jiao Tong University | — | author |
| Bin Sun | Li Auto Inc. | — | author |
| Zhihui Hao | Li Auto Inc. | — | author |
| Junchi Yan | Shanghai Jiao Tong University | https://thinklab.sjtu.edu.cn/ | corresponding author |

### 1.2 Keywords

Feed-forward reconstruction, Visual Geometry Transformer, Autonomous Driving, Multi-camera, Calibration constraints, Ego-motion estimation, Depth estimation, Camera pose

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Visual Geometry Grounded Transformer) [33] | base model | 前饋式 transformer 重建基礎模型,DriveVGGT 直接以其為骨幹並改造注意力與解碼頭 |
| FastVGGT [27] | baseline | 對 VGGT 採用 region-based random sampling 加速推理,本論文在效能與速度上與其對比 |
| Streaming VGGT [53] | baseline | 以 memory cache 與 temporal causal attention 達成串流式重建,屬於同期改進 VGGT 方向 |
| Block-sparse global attention VGGT 變體 [31] | concurrent | 用塊狀稀疏全域注意力替代密集全域注意力,以提升 VGGT 效率 |
| DUSt3R-style end-to-end 3D reconstruction [35] | predecessor | 首個端到端同時預測位姿、內參與深度的前饋重建管線,奠定本論文取法的範式 |
| Permutation-equivariant 重建架構 [37] | influence | 解決 VGGT 對首幀位姿初始化敏感的順序偏差,啟發本論文重新設計位姿解碼 |
| AD 多視角解耦注意力工作 [24] | influence | 在自駕 6 視角中以解耦注意力維持時空幾何一致性,為 TVA/MCA 設計提供先例 |

## 2. Research Overview

### 2.1 Research Topic

本文聚焦於將前饋式視覺幾何 transformer(以 VGGT 為代表)從通用場景推廣到多相機自駕情境的 4D 場景重建任務。研究目標是在 360 度低重疊多視角影片下,同時恢復絕對尺度的深度、相機外參與自車軌跡,並兼顧長序列下的推理效率。作者觀察到自駕資料具備三個被既有 VGGT 忽略的領域先驗:相機間視野重疊稀疏、出廠校正提供絕對尺度,以及多相機相對位姿在行駛中保持剛性恆定。據此提出 DriveVGGT,以時序視訊注意力 (TVA)、多相機一致性注意力 (MCA) 與分解式位姿/自車運動解碼頭,將這些先驗顯式注入前饋網路。實驗在 nuScenes 6 相機資料集上驗證,在深度與位姿精度上同時超越 VGGT 與其加速變體,並將長序列推理時間縮短近一半。

### 2.2 Domain Tags

- Computer Vision
- 3D Scene Reconstruction
- Autonomous Driving Perception
- Multi-view Geometry

### 2.3 Core Architectures Used

- **VGGT (Visual Geometry Grounded Transformer)**:作為被繼承的前饋式重建骨幹,提供 image tokenizer、aggregator 與 DPT 風格的 depth/camera head,DriveVGGT 在其基礎上替換全域注意力並改寫解碼介面。
- **Temporal Video Attention (TVA)**:本論文新提出的模組,將注意力侷限於同一相機在時間軸上的序列,以 $O(M \cdot T^2)$ 取代原本 $O((M \cdot T)^2)$ 的全域複雜度,對應「Sparse Spatial Overlap」先驗。
- **Multi-camera Consistency Attention (MCA)**:本論文新提出的時空 window attention,把校正得到的相對外參透過 relative pose embedding 注入 token,於 $2k+1$ 幀鄰域內做跨相機一致性聚合,負責解決尺度模糊與跨視角錨定。
- **Factorized Decoding Heads**:把 VGGT 原本逐影像獨立預測的 camera head 拆成 sequential pose head、ego-motion head、relative pose head 與 scale head 四路,以 ego-motion pooling 與 extrinsic aggregation 強制剛體一致性並輸出絕對公制尺度。
- **DPT 解碼頭 [6]**:沿用自 VGGT 的多階段 refinement depth decoder,用以從幾何 token 生成高解析稠密深度與信心圖。
- **FastVGGT 變體 [27]**:作為 TVA 的可替換骨幹之一(DriveVGGT(fastVGGT)),展示本框架對既有 VGGT 加速版本的「universal plugin」相容性。

### 2.4 Core Argument

作者主張 vanilla VGGT 在自駕情境下表現不佳的根本原因不在模型容量,而在於它把多相機長序列影片視為通用且彼此對等的影像集合,完全沒有利用自駕平台的三項結構性先驗,因此既浪費算力又無法產生具絕對尺度與時空一致性的重建結果。具體而言,(i) 自駕為了 360 度覆蓋採用稀疏重疊配置,VGGT 的全域注意力在跨視角間做了大量幾何上不可能匹配的計算,並承受 $O((M \cdot T)^2)$ 的二次複雜度;(ii) 出廠校正提供了相機間的絕對距離,但 VGGT 沒有任何介面接收此資訊,輸出只能停留在相對尺度,造成尺度模糊;(iii) 自車所有相機共享同一個自運動且彼此外參剛性恆定,VGGT 卻為每張影像獨立預測位姿,既冗餘又破壞剛體一致性。基於這個診斷,解決方案在邏輯上必須三管齊下:用 Temporal Video Attention 將注意力侷限於同相機時間軸以匹配「重疊只在時間維度」的事實;以 Multi-camera Consistency Attention 與專用 scale head 顯式注入校正得到的相對外參作為「物理量尺」,讓網路得以將潛在表徵錨定到絕對公制尺度;再以分解後的 sequential pose head 與 ego-motion head 將「每相機相對首幀軌跡」與「全車自運動」解耦,從架構層級保證所有相機共享同一自運動且外參維持剛性。三個元件分別對應三個先驗,缺一即無法同時兼顧效率、絕對尺度與剛體一致性,因此這套組合並非工程堆疊,而是由問題結構直接導出的必要設計。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(約 320 words)

論文標題 "DriveVGGT: Calibration-Constrained Visual Geometry Transformers for Multi-Camera Autonomous Driving" 已將三個關鍵訊號鋪排到位：基底模型是 VGGT、所處領域是多相機自駕、技術立場是以「校正資訊作為幾何約束」。Abstract 緊接著用一個明確的因果鏈把標題展開：feed-forward reconstruction 已快速進展，VGGT 是代表性 baseline，但直接套用到 autonomous driving (AD) 會錯過三個 domain-specific priors。

作者把三個 priors 條列得相當乾淨，這也是整篇論文的論證骨架：(i) **Sparse Spatial Overlap** —— 360° 覆蓋下多相機之間 overlap 極小，使 global attention 無效率；(ii) **Calibrated Geometric Constraints** —— AD 場域在出車前已完成校正，可取得相機間絕對距離，但 vanilla VGGT 無法直接吸收此資訊以恢復絕對尺度；(iii) **Rigid Extrinsic Constancy** —— 多相機相對 pose 在駕駛過程中保持靜態，亦即 ego-motion 對所有相機共用。

對應地，作者宣告 DriveVGGT 由三個模組去逐一打靶：對 (i) 提出 **Temporal Video Attention (TVA)**，獨立處理每一台相機的 video stream；對 (ii) 提出 **Multi-camera Consistency Attention (MCA)**，並引入 scale head 以恢復絕對尺度；對 (iii) 把 decoding 拆成 factorized 的 sequential pose head 與 ego motion head。

最後 Abstract 用兩個量化承諾收束讀者期待：相比 vanilla VGGT 在 long-sequence 場景下 inference 時間下降 49.3%，並同時在 depth 與 pose estimation 上勝過近期 SOTA 變體；ablation 也會驗證每個模組各自的貢獻。這個 abstract 的結構價值在於：它不是把貢獻並列，而是把「prior → limitation → module」一一綁定，讓讀者在進入正文前就已經接受了「有三個獨立但互補的設計」這個閱讀框架，後續所有章節都依此節奏推進。

### 3.2 Introduction

(約 620 words)

Introduction 沿用 Abstract 的骨架但補上更密的論證。第一段先把領域趨勢點出 —— 從傳統 optimization-based pipelines 轉向 feed-forward transformer 架構，VGGT 是其中最具代表性的 baseline，泛化性強；但作者立刻把鏡頭拉回 AD：vanilla VGGT 的通用設計沒有顧到多相機車載平台特有的幾何與結構先驗。

第二段用三個段落級別的 bullet 把三大限制鋪滿。對 Sparse Spatial Overlap，作者強調 AD 相機在成本約束下會被刻意稀疏佈置，於是 global attention 無效率；又因 AD 應用裡相機數與 video 長度都會放大，O((M×T)²) 的 quadratic complexity 直接造成效能退化。對 Calibrated Geometric Constraints，作者指出車輛出車前的高精度校正可提供絕對尺度距離，但 VGGT 等 feed-forward 模型無法原生吃進這類資訊，導致 normalized latent 與 metric scale 之間出現 scale ambiguity。對 Rigid Extrinsic Constancy，作者提醒 AD 系統的多相機相對外參在駕駛過程中是固定的，若 VGGT 把 multi-view video 當成獨立影像集合處理，就會錯失這層 spatial-temporal rigidity。

第三段把三個 priors 一對一映射到三個模組，提供讀者一張 "prior → module" 的對照表：(1) TVA 把每台相機的 stream 獨立處理，避開非重疊區的冗餘 attention；(2) MCA 將已知校正外參注入 feed-forward 流程，並透過專門的 scale head 從 relative depth 過渡到 absolute metric depth；(3) decoding 階段不再對每張影像獨立預測 pose，而是把 camera tokens 沿兩個 factorized 維度池化，分別餵入 sequential pose head 與 ego-motion head，藉此確保預測軌跡與 sensor rig 的剛體掛載一致。

第四段給出實驗承諾的具體場景：在 nuScenes（6 顆低 overlap 相機）上，DriveVGGT 在 inference latency 上降低 49.3%，同時 pose 與 depth 指標皆勝過 vanilla VGGT 與其他 SOTA 變體，特別適合 long-sequence reconstruction。

最後 Introduction 收在四點 contributions：提出 scale-aware feed-forward 框架；引入 TVA 與 MCA 模組；以 factorized pose/ego-motion heads 重構 decoding；以及在 AD benchmark 上的全面實驗驗證。整段最重要的 setup 作用在於：它替後續 Related Works 設定了「為什麼 VGGT 系列既是 baseline 又是檢討對象」的判讀視角，也替 §3 Proposed Approach 預先把模組數與配對關係定錨。

### 3.3 Related Work / Preliminaries

(約 410 words)

Related Works 被切成三節，每一節的功能都不只是文獻回顧，而是替論文的三個 priors 之一鋪設定位空間。

**§2.1 Scene Reconstruction** 從 feed-forward reconstruction 的演進切入：先提 [35] 作為第一個 end-to-end 同時預測 pose、intrinsic 與 depth 的 pipeline，再延伸到 [50] 引入動態場景與 dynamic mask、[21] 用 motion probability 處理動態物件；接著鎖定 VGGT [33]，把它定位成簡化 pipeline 的 transformer-based feed-forward 代表；最後敘述兩條優化路線 —— [53] 用 memory cache 與 temporal causal attention 達到 streaming reconstruction、fastVGGT [27] 用 region-based random sampling 加速、以及 [31] 採 block-sparse global attention。這節的策略性意義是：它把實驗中要對比的 VGGT、StreamVGGT、fastVGGT 三個 baseline 一次接好戶口。

**§2.2 Temporal-Spatial Geometry Consistency** 處理跨幀與跨相機的一致性。它先點 monocular 的 temporal 文獻群（[9, 16, 30, 44, 41, 51, 48]），再進到 multi-view 同步（[2, 18]），最後落到 AD 場景：[24] 的 decoupled attention 用於 6-view 一致性，[11, 36] 是引入 probabilistic state 的 generative world models，[4] 強調顯式 spatial alignment 的 multi-view video generation。這節對應的是 Sparse Spatial Overlap 與 Rigid Extrinsic Constancy 兩個 priors，把 DriveVGGT 的 TVA + MCA 設計與「decoupled attention」這條 AD 文獻線索接起來。

**§2.3 Position Geometry Representation** 聚焦 pose 的表示方式：[17] 提出可同時表 4-DoF/6-DoF 的 camera positional encoding；[43] 用 spherical harmonics 作為 equivariant 表示；[25] 探索專門處理 position token 的 transformer 結構；[19] 提出類似 RoPE [29] 的 relative positional encoding。然後作者轉回 VGGT：它用 image pose tokens 解碼出 extrinsics 與 intrinsics，但需要把首幀 pose 單獨初始化作為其他幀的位置參考，這在不同輸入順序下會降低精度；[37] 因此提出 fully permutation-equivariant 架構去除這個 bias。

這節為 §3.2 Relative Pose Embedding 提供了直接的 baseline：DriveVGGT 把 calibration 已知的相對外參直接編碼為 token，繞開「首幀 pose 初始化」這個 fragility。三節合起來形成一張地圖，讓讀者在進入 Method 前清楚知道每個模組對應的文獻位置。

### 3.4 Method (overview narrative)

(約 290 words)

§3 Proposed Approach 以一段 framing 開場：DriveVGGT 的目標是把通用 feed-forward reconstruction 架構轉成 scale-aware、geometry-constrained 的 AD 框架。輸入被定義為 $M$ 個相機 $\times$ $T$ 個時間步的 multi-camera AD video，輸出則是 consistent 3D scene geometry、absolute metric depth 以及 camera trajectories。Fig. 2 直接亮出整套 pipeline，並把三個模組的協作關係定義清楚：(i) **TVA** 處理 intra-camera motion；(ii) **MCA** 在 calibration prior 引導下融合 cross-view 資訊；(iii) **Factorized Decoding** 強制 rigid extrinsic constancy。

接著章節內部以「prior → module → 數學定義」的節奏鋪陳。§3.1 把 TVA 的設計動機寫成「global attention 在 $O((M \times T)^2)$ 下不可行 + Sparse Spatial Overlap 使 cross-view attention 冗餘」，因此 TVA 只在同一台相機內做 attention，輸出每張影像的 sequential pose token 與 depth token。§3.2 把 calibration 視為「physical ruler」，先把 translation 做 zero-mean normalization、組成 10-D camera parameter vector，再以 learnable linear projection 投射到 transformer 隱空間，並指出由於 Rigid Extrinsic Constancy，這組 embedding 每個 sensor configuration 只需算一次。§3.3 的 MCA 用 spatiotemporal window attention 把 TVA 的局部 token 跨相機融合，並透過 ego-motion pooling 與 extrinsic aggregation 兩條 factorized pooling 把 vehicle 移動與相機掛載分離。§3.4 的 prediction heads 重用 VGGT 的 pose head 但拆成 relative 與 sequential 兩支，再乘成 global pose；同時新增 scale head 以 real-world 與 normalized 相對 pose 的比值估出絕對尺度。§3.5 的 loss 則沿用 VGGT 的 depth loss 並把 camera pose loss 拆成 $L_{rel}$ 與 $L_{seq}$ 兩項，總損失為 $L_{total}=\lambda_1 L_{depth}+\lambda_2(L_{rel}+L_{seq})$，$\lambda_1=0.1, \lambda_2=1.0$。整段 Method 的 narrative 把「為什麼這樣設計」與「如何落到符號」逐層綁緊，為後續實驗章節留好量測點。

### 3.5 Experiments (overview narrative)

(約 320 words)

§4 Experiments 的敘事節奏可拆成「dataset → setup → 三個量化實驗 → 視覺化 → ablation」五段。§4.1 建立 nuScenes 為主測試平台：1000 個 20 秒場景、6 顆相機、32-beam LiDAR，700/150 train/val 切分，2 Hz keyframe sampling；作者特別指出 nuScenes 的 sparse overlap 正好對齊 Sparse Spatial Overlap prior，是恰當的測試床。為解決 LiDAR raw return 對 high-resolution depth head 不夠 dense 的問題，作者另外提了一個兩段式 LiDAR Densification Pipeline：先做 spatiotemporal point aggregation（靜態用 ego-motion 對齊、動態用 3D bbox 在物件 local frame 累積以避免 ghosting），再以 bilateral filtering 或 morphology-based completion 做 depth completion，得到比 raw LiDAR 更稠密的監督訊號。

§4.2 給出 implementation：影像從 1600$\times$900 縮到 518$\times$280，intrinsic 一併調整；訓練分兩階段，先以 2e-4 lr 跑 20 epochs（每 epoch 1000 iterations，每次隨機餵入 3-10 frame 的 multi-camera 影像，即 18-60 張），再 freeze aggregator、以 1e-5 lr fine-tune 5 epochs；其他 baseline 同設定以保公平。

§4.3-§4.5 是論文的三個量化主軸：pose estimation（Table 1，AUC@30 與 AUC@15，三種 frame 數）、depth estimation（Table 2，Abs rel 與 $\delta_3$）以及 inference time（Table 3，三種 frame 數）。一致的對照組為 VGGT、StreamVGGT、fastVGGT，並把 DriveVGGT 拆成以 VGGT 為底的 DriveVGGT(VGGT) 與以 fastVGGT 為底的 DriveVGGT(fastVGGT)，同時測試 baseline 加上 relative pose embedding 的版本以隔離模組貢獻。

§4.6 用 30-frame（180 張）序列把 predicted depth 反投影成 global point cloud 做定性比較，凸顯 VGGT 與 fastVGGT 在 long-sequence 出現 temporal drift 與 ghosting，DriveVGGT 則維持軌跡穩定且重建細節更銳利。

§4.7 ablation 分三題：components（baseline TVA、加 relative pose embed、完整 DriveVGGT）；window size（$k=3,5,7$，論文選 $k=3$）；scale head（least squares vs. scale-based 對齊比較）。整體實驗設計把「速度、精度、模組必要性」三條線各自安插到對應表格，讓讀者能按圖索驥地對應回 §3 的設計動機。

### 3.6 Conclusion / Limitations / Future Work

(約 290 words)

§5 Conclusion 在正文中極為精簡，只用一段話把三個重點收束：DriveVGGT 是一個專為 multi-camera 幾何預測設計的 feed-forward reconstruction 模型；相較先前方法，它能有效利用 relative camera poses 來提升 camera pose 與 depth estimation 的精度；nuScenes 上的綜合評估顯示其表現勝過先前 feed-forward 方法，且運算成本較低。論文沒有單獨的 Limitations 或 Future Work 小節，這是值得注意的閱讀提示 —— 限制與未來方向其實散落在 §6 Supplementary Material 與部分 §4 段落中。

從補充材料可以反推出作者實際承認或暗示的若干邊界。§6.5 解釋了 DriveVGGT(fastVGGT) 為何反而比 DriveVGGT(VGGT) 慢：因為 TVA 把每台相機獨立處理後，每個 batch 只剩 1/6 的影像，落在 fastVGGT 的「不利區間」（fastVGGT 在影像數很少時比 VGGT 慢，僅在 150+ 張時才反超），這實質上點出 DriveVGGT 與 fastVGGT 的相容性是 sequence-length-dependent 的。§6.1 重申三項先驗的必要性，§6.2 把核心創新總結為「bridging the AD gap、avoiding $O((M \times N)^2)$、Universal AD Framework」，並在 Table 7 把與既有模型的差異列為 plug-in 式擴展，暗示後續工作可把 DriveVGGT 包成通用框架去整合更多 geometry transformer。§6.3 則從另一個角度標出未來方向：相比 GPS/IMU/GNSS 等外部 sensor 在挑戰交通環境中的不穩定，feed-forward 估出的 ego-pose 可作為 robust alternative，並把 task 進一步推向 multi-camera odometry 與 reconstruction 的聯合處理，這隱含了往 odometry/SLAM 整合的後續路線。整體而言，Conclusion 雖短，但與 Supplementary 合讀後仍能讀出三條延伸線：跨架構通用性、對外部 sensor 的替代性、以及與 sequence-length 相關的 efficiency trade-off。

## 4. Critical Profile

### 4.1 Highlights

- 作者在 Section 1 與 Fig. 1 將自駕情境的三項先驗(Sparse Spatial Overlap、Calibrated Geometric Constraints、Rigid Extrinsic Constancy)清楚對應到 vanilla VGGT 的三項缺陷,使每個架構元件都有對應的物理動機,而非單純堆疊技巧 (page 2–3)。
- 在 nuScenes 35 frame(210 張影像)的長序列情境下,DriveVGGT(VGGT) 推理時間從 vanilla VGGT 的 9666 ms 降至 4907 ms,約節省 49.3% (Table 3, page 12)。
- 同樣 35 frame 條件下,Camera Pose AUC@30 由 VGGT 的 0.6871 提升至 DriveVGGT(VGGT) 的 0.7200,AUC@15 由 0.5477 提升至 0.5811 (Table 1, page 11)。
- 深度估計在 35 frame 條件下,DriveVGGT(fastVGGT) 的 Abs Rel 為 0.3539、$\delta_3$ 為 0.8935,在所有對照組中最佳 (Table 2, page 12)。
- Window Attention 的 ablation 顯示 $k=3$ 已足夠,$k=5/7$ 僅將 AUC@30 由 0.8010 微幅推到 0.8033/0.8087,卻使推理時間從 3294 ms 暴增到 7263 ms,支持「Sparse Spatial Overlap 不需 global attention」的論證 (Table 5, page 13)。
- 透過 Multi-camera Consistency Attention 的 calibration 注入與 Eq. 13 的 scale head,作者在 Table 6 顯示 scale-based 對齊將 $\delta_3$ 從 least-squares 的 0.7412 拉到 0.8747,顯示絕對尺度確實被建立 (Table 6, page 14)。
- DriveVGGT 是 backbone-agnostic 的封裝,實驗同時以 VGGT 與 fastVGGT 為 TVA 主幹,展示對既有前饋幾何 transformer 的可插拔性 (Table 7, page 15)。
- 為了補強 nuScenes LiDAR 點雲過於稀疏的問題,作者提出兩階段 LiDAR Densification(時空點雲聚合 + 深度補全),並對動態物件以 3D bbox 在物件座標系內聚合,避免 ghosting (Fig. 4, page 10)。
- Fig. 5 的長序列 30 frame point cloud 視覺化顯示 vanilla VGGT 與 fastVGGT 的累積 pose drift 與重影,而 DriveVGGT 對遠處植被與道路結構保留較銳利的幾何 (Fig. 5, page 13)。
- 補充材料 Table 9 揭露了一個非顯然的工程觀察:TVA 將每個相機獨立成 batch 後,VGGT 在小 batch (6/30 張) 比 fastVGGT 更快,因此 DriveVGGT(VGGT) 反而比 DriveVGGT(fastVGGT) 整體更省時 (page 17)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者承認 LiDAR Densification 因為感測器同步與投影誤差會引入 "minor noise",但僅以 "yields a significantly richer supervision signal than raw LiDAR" 帶過,沒有量化此噪聲對訓練的影響 (Section 4.1, page 11)。
- 作者承認 DriveVGGT(fastVGGT) 比 DriveVGGT(VGGT) 慢,並在補充材料 Section 6.5 解釋是因 TVA 把每個相機切成 1/6 batch、而 fastVGGT 在小 batch 反而較慢 (page 17),但沒有討論此特性對其他更小 rig 的可擴展性。
- StreamVGGT 在 frame=25 與 frame=35 直接 OOM(Table 1、Table 2、Table 3),作者把這列出但並未討論 OOM 是否來自實作差異或記憶體預算配置不同。

#### 4.2.2 Phyra-inferred

- Table 4 中 baseline(TVA) 的 AUC@30 = 0.039,接近隨機,意味 TVA 單獨完全無法重建多相機系統,但論文仍將 TVA 列為三大貢獻之一;該 ablation 並未隔離 factorized decoding,只能比較 TVA 對比 TVA+rel pose embed 對比完整 DriveVGGT,因此第三項貢獻的邊際效益完全沒有實驗證據 (Table 4, page 13)。
- "49.3% latency reduction" 是相對於 vanilla VGGT;但 Table 3 frame=35 顯示 fastVGGT = 4949 ms、DriveVGGT(VGGT) = 4907 ms,僅快 0.85%,意味在最強的速度對手上,DriveVGGT 的速度收益幾乎消失,但 Abstract 與 Introduction 沒有揭露這個對比 (Table 3, page 12)。
- Eq. 13 的 scale 估計為 $\mathrm{Avg}\!\left(\sum_j T^{rel}_{real}(j) / T^{rel}_{norm}(j)\right)$,當預測的 $T^{rel}_{norm}(j)$ 對於某對相機(尤其後排基線較短的相機對)接近零時,比值會發散;論文沒有任何對 scale head 的數值穩定性或 outlier 處理做敏感度分析。
- 整篇實驗只在 nuScenes 上進行,沒有 Waymo / Argoverse2 / PandaSet 的跨資料集驗證,但補充材料 Table 7 卻把 "Universal AD Framework" 列為核心貢獻,二者間的證據與宣稱範圍不對等 (Table 7, page 15)。
- 影像解析度從 nuScenes 原生 1600×900 大幅降到 518×280 才送入模型 (Section 4.2, page 11);這對 calibration-based scale 推導其實是不利的,因為更小的影像意味更粗的視差訊號,但論文沒有 ablate 解析度,使得 Abs Rel 的 ~3.5% 改善能否在原生解析度保留並不清楚。
- Pose 評估只報 AUC@30 / AUC@15;對自駕場景更直接的 ATE (Absolute Trajectory Error) 與 per-frame RPE 完全缺席,使得 ego-motion head 的優勢無法和傳統 VO/SLAM(ORB-SLAM3、DPVO 等)橫向比較 (Table 1, page 11)。
- 相對外參 $P_{cam}(j)$ 在 Eq. 6–7 被視為精確且靜態,但生產車輛因溫漂、震動、安裝偏差會持續引入 calibration drift;論文沒有對 $P_{cam}(j)$ 注入合成噪聲(例如 $1^\circ$ 旋轉、1 cm 平移)做 robustness 實驗,而這正是工程部署最關心的情境。
- Eq. 8–11 的下標出現不一致(例如 Eq. 11 將 $F^{rel}_{agg}(m)$ 寫成 $\sum_{j=1}^{N} F^{rel}(i,j)$,$m$ 與 $i$ 沒有對應),反映出論文校稿不嚴謹,讀者僅憑文字無法精準復現公式。

### 4.3 Phyra's Judgment (summary)

DriveVGGT 真正的新穎處在於把「三個自駕先驗」清楚對齊「三個架構修正」並在 nuScenes 上同時改善 pose、depth 與 inference time,這個診斷層面的工作是值得肯定的。然而 TVA、relative pose embedding 與 factorized decoding 在 ablation 中無法被各自獨立衡量,且最關鍵的 scale head 只用一張 Table 6 在 frame=15 上做了單點驗證,使「絕對尺度」的宣稱仍偏弱。剩下的核心未解問題是:在 calibration 不完美、跨資料集 rig、原生解析度的真實量產情境下,這套 calibration-constrained 設計能否同時保住「精度提升」與「近半推理加速」的雙重承諾。

## 5. Methodology Deep Dive

### 5.1 Method Overview

DriveVGGT 將通用前饋式重建模型 VGGT 改造成「scale-aware, geometry-constrained」的 4D 重建框架。輸入是 $M$ 台車載相機（nuScenes 為 6 台）在 $T$ 個時間步同步擷取的 $M \times T$ 張影像、以及一份出廠校正得到的相機間相對外參與內參。輸出包含每張影像的 dense metric depth、每相機相對自身首幀的 sequential pose、整車自運動 (ego-motion) 軌跡，以及將潛在表徵錨定到公制尺度的 scale 因子。整條管線取代 vanilla VGGT 的 global self-attention，改採三段式幾何化處理：(i) Temporal Video Attention (TVA) 只在同相機的時間軸上做 attention，從 $O((MT)^2)$ 降到 $O(M \cdot T^2)$，並對應「Sparse Spatial Overlap」先驗；(ii) Multi-camera Consistency Attention (MCA) 把校正得到的相對位姿透過 learnable embedding 與 TVA token 串接後，用尺寸 $2k+1$ 的時序視窗做跨相機 attention，對應「Calibrated Geometric Constraints」先驗；(iii) Factorized Decoding 透過跨相機平均得到 per-frame 的 ego-motion token、跨時間平均得到 per-camera 的 rigid extrinsic token，並餵入分離的 sequential pose head、ego/scale head 與 DPT depth head，對應「Rigid Extrinsic Constancy」先驗。

訓練目標沿用 VGGT 的 depth loss 與 pose loss 設計，但把原本耦合的 camera pose loss 拆成 $L_{rel}$（相對位姿）與 $L_{seq}$（序列位姿）兩項，並以 $\lambda_1 = 0.1, \lambda_2 = 1.0$ 的加權結合。實作上以 VGGT 與 FastVGGT 兩種骨幹構成 DriveVGGT(VGGT) 與 DriveVGGT(fastVGGT) 兩個變體，差別在於 TVA 階段是否套用 FastVGGT 的 region-based random sampling。整體輸入解析度被下調到 $518 \times 280$ 以匹配預訓練位置嵌入，並對深度與位姿做 scale normalization；scale 本身則作為額外監督訊號，從預測的 normalized 相對外參與真值相對外參的比值平均回推（式 (13)），再乘回 depth 與 translation 以恢復 metric scale。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input:  videos      [B, M, T, 3, H, W]      # H=280, W=518; nuScenes M=6
        intrinsics  [B, M, 3, 3]            # K(j) per camera
        extrinsics  [B, M, 4, 4]            # [R(j) | T(j)] per camera (rig-fixed)

Step 1 — Per-camera Pose Preprocessing (Sec. 3.2)
   extrinsics ─► T_norm(j) = (T_j − μ_T) / σ_T            [B, M, 3]
              ─► P_cam(j) = Concat(T_norm, R(j), K(j))    [B, M, 10]
              ─► Embed (linear / small MLP)               [B, M, D]   = F_pos^cam

Step 2 — Temporal Video Attention (TVA, Sec. 3.1)
   videos ─► reshape to per-camera streams                [B·M, T, 3, H, W]
          ─► VGGT encoder f(·) (shared, applied per cam)
              ├→ image / depth tokens   F_depth(i, j)     [B, M, T, P, d]   # P = (H/p)·(W/p)
              └→ sequential pose token  F_pos^seq(i, j)   [B, M, T, d]      # 1 pose token per frame
   Note: TVA only attends within {frames of camera m}, complexity O(M·T²·d).

Step 3 — Geometric–Visual Token Fusion (Sec. 3.3)
   For each (t, m):
     F_token(t, m) = Concat( F_pos^cam(m),                [B, M, D]
                             F_pos^seq(t, m),             [B, M, T, d]
                             F_depth(t, m) )              [B, M, T, P, d]
   ─► fused MCA tokens                                    [B, M, T, P+2, d_fused]   # d_fused = ?

Step 4 — Spatiotemporal Window Attention (MCA, Sec. 3.3, Eq. 9)
   For frame i, attend over { (m', t') : m' ∈ [1..M],  t' ∈ [i−k, i+k] }
   ─► refined tokens F(i, j)                              [B, M, T, P+2, d_fused]
   Complexity: O(M · N² · d) vs Full O(M · W · N² · d)   # see Fig. 3

Step 5 — Rigidity-Based Feature Aggregation (Sec. 3.3, Eq. 10–11)
   Ego-motion pooling   (avg over M cameras):
       F_agg^seq(t)  = mean_{m=1..M} F^seq(t, m)          [B, T, d]
   Extrinsic aggregation (avg over T frames):
       F_agg^rel(m) = mean_{t=1..T} F^rel(t, m)           [B, M, d]

Step 6 — Prediction Heads (Sec. 3.4)
   ├→ Sequential Pose Head        F^seq tokens   ─► g^seq(i, j)   [B, M, T, 6]   # R, T per cam-frame
   ├→ Relative Pose / Ego Head    F^rel + ego    ─► g^rel(i, j)   [B, M, 6]      # rig extrinsics
   ├→ DPT Depth Head (4 stages)   F_depth        ─► D_hat(i, j)   [B, M, T, 1, H, W]
   └→ Scale Head                  T^rel pred/gt  ─► scale         [B, 1]         # Eq. 13

Step 7 — Compose & Recover Metric Scale (Eq. 12)
   G^global(i, j) = G^seq(i, j) × G^rel(i, j)              [B, M, T, 4, 4]
   D_metric       = scale · D_hat                          [B, M, T, 1, H, W]
   T_metric       = scale · translation(G^global)          [B, M, T, 3]

Output: per-image metric depth, per-camera trajectories, ego-motion track
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Temporal Video Attention (TVA)

**Function:** 對每台相機獨立做時序 attention，建立同相機影像之間的初始幾何關聯，避免在低重疊跨視角間做無效計算，將複雜度從 $O((M \cdot T)^2)$ 降到 $O(M \cdot T^2)$。

**Input:**
- Name: `videos`
- Shape: `[B, M, T, 3, H, W]`，nuScenes 設定 $M=6$、$H=280$、$W=518$
- Source: 多相機同步影像序列（資料前處理已 resize、並同步調整 intrinsics）

**Output:**
- Name: `F_pos^seq, F_depth`
- Shape: `F_pos^seq` 為 `[B, M, T, d]`，`F_depth` 為 `[B, M, T, P, d]`，其中 $P$ 為每張影像的 patch 數
- Consumer: Geometric–Visual Token Fusion（§5.3.3 MCA）

**Processing:**

1. 將輸入 reshape 為 per-camera stream `[B·M, T, 3, H, W]`，使每個 mini-batch element 對應「同一相機在 $T$ 個時間步」的視訊。
2. 共享一個 VGGT encoder $f(\cdot)$ 套用於每條 stream，對應論文式 (1)：$f: \{I_i\}_{i=1}^N \mapsto \{(F_{\mathrm{pos}}(i), F_{\mathrm{depth}}(i))\}_{i=1}^N$，其中 $N$ 在 TVA 階段就是該相機的 $T$ 張影像。
3. 注意力範圍被嚴格限制在「同相機的時間軸」，對應式 (3)–(4)：$\mathrm{TVA}(\cdot) = \{f(\cdot)\}_{i=1}^M$，輸出每相機的 sequential pose token 與 depth token。
4. 此處的 $F_{\mathrm{pos}}^{seq}(i, j)$ 僅代表「相對該相機首幀」的位姿預測，尚未跨相機對齊；跨相機與絕對尺度由後續 MCA 與 Scale Head 補上。

**Key Formulas:**

$$
f: \{I_i\}_{i=1}^{N} \mapsto \{(F_{\mathrm{pos}}(i), F_{\mathrm{depth}}(i))\}_{i=1}^{N}
$$

$$
\{(F_{\mathrm{pos}}^{seq}(i, j), F_{\mathrm{depth}}(i, j))\}_{(i, j)} = \mathrm{TVA}\!\left(\{I(i, j)\}_{j=1}^{N}\right)
$$

**Implementation Details:**

骨幹直接沿用 VGGT (`DriveVGGT(VGGT)`) 或 FastVGGT (`DriveVGGT(fastVGGT)`)；FastVGGT 變體在此處引入 region-based random sampling 來加速。輸入解析度從 $1600\times900$ 下調到 $518\times280$，內參同步縮放。具體 $d$、$P$、patch size 與 head 數量 the paper does not specify。

#### 5.3.2 Relative Pose Embedding

**Function:** 把出廠校正得到的相機間相對外參與內參，編碼成單一向量並投影到 transformer 潛在空間，作為「physical ruler」注入 MCA，使網路得以把潛在表徵錨定到 metric scale。

**Input:**
- Name: `extrinsics, intrinsics`
- Shape: `[B, M, 4, 4]`、`[B, M, 3, 3]`
- Source: 出廠校正資料（駕駛前一次性取得，沿用 Rigid Extrinsic Constancy）

**Output:**
- Name: `F_pos^cam`
- Shape: `[B, M, D]`，$D$ 為 transformer 的 embedding 維度
- Consumer: MCA 的 Geometric–Visual Token Fusion

**Processing:**

1. 對所有 $M$ 台相機的 translation $T_j$ 做 zero-mean normalization：$T_{\mathrm{norm}}(j) = (T_j - \mu_T)/\sigma_T$（式 (5)），以對齊 transformer 的潛在分佈、提升數值穩定性。
2. 將 normalized translation、rotation 表徵（如 quaternion 或 Euler）、與內參 $K(j)$（焦距與 principal point）串接成 10 維向量 $P_{\mathrm{cam}}(j) = \mathrm{Concat}(T_{\mathrm{norm}}(j), R(j), K(j))$（式 (6)）。
3. 透過 learnable linear projection 或小 MLP 將 $P_{\mathrm{cam}}(j) \in \mathbb{R}^{10}$ 映射到 $F_{\mathrm{pos}}^{\mathrm{cam}}(j) \in \mathbb{R}^D$（式 (7)）。
4. 由於 rig 在行駛過程中保持剛體恆定，這組 embedding 每個 sensor configuration 只需計算一次，整段序列共用。

**Key Formulas:**

$$
T_{\mathrm{norm}}(j) = \frac{T_j - \mu_T}{\sigma_T}
$$

$$
P_{\mathrm{cam}}(j) = \mathrm{Concat}\!\left(T_{\mathrm{norm}}(j), R(j), K(j)\right) \in \mathbb{R}^{10}
$$

$$
F_{\mathrm{pos}}^{\mathrm{cam}}(j) = \mathrm{Embed}\!\left(P_{\mathrm{cam}}(j)\right) \in \mathbb{R}^{D}
$$

**Implementation Details:**

`R(j)` 採用何種 rotation parameterization（quaternion vs Euler）the paper does not specify。投影模組是 single linear layer 還是 MLP、$D$ 的具體值，the paper does not specify。

#### 5.3.3 Multi-Camera Consistency Attention (MCA)

**Function:** 在 TVA 之後注入相對外參先驗，並用 spatiotemporal window attention 把各相機獨立的 latent 對齊到統一、metric-scale 的 4D 表徵，同時維持線性於序列長度的複雜度。

**Input:**
- Name: `F_pos^cam, F_pos^seq, F_depth`
- Shape: `[B, M, D]`、`[B, M, T, d]`、`[B, M, T, P, d]`
- Source: §5.3.2 Relative Pose Embedding 與 §5.3.1 TVA

**Output:**
- Name: `F(i, j)`（refined token），以及 §5.3.4 用到的 $F^{seq}, F^{rel}$
- Shape: `[B, M, T, P+2, d_fused]`
- Consumer: Rigidity-Based Feature Aggregation（§5.3.4）與 Prediction Heads

**Processing:**

1. **Geometric–Visual Token Fusion**：為了控制計算量，只取 TVA 中四個 task-relevant 層的 token；對每個 $(t, m)$ 將 $F_{\mathrm{pos}}^{cam}(m)$、$F_{\mathrm{pos}}^{seq}(t, m)$、$F_{\mathrm{depth}}(t, m)$ 串接成 $F_{\mathrm{token}}(t, m)$（式 (8)），其中 $F_{\mathrm{pos}}^{cam}(m)$ 提供「該相機在車身上的固定位置」這個錨點。
2. **Spatiotemporal Window Attention**：採用以時間為軸的滑動視窗，視窗大小 $2k+1$（涵蓋 $i-k$ 到 $i+k$ 的前後幀），對所有 $M$ 台相機在該視窗內做 attention（式 (9)）。如此既能跨相機尋找對應，又避免跨遠距時間幀帶來的雜訊與 quadratic 成本；論文 Figure 3 對比 Full Attention 的 $O(M \cdot W \cdot N^2 \cdot d)$ 與 Window Attention 的 $O(M \cdot N^2 \cdot d)$，後者去掉了視窗數 $W$ 的乘子。
3. 輸出的 refined token 同時保留 image/depth 表徵與 pose 表徵，後續被 §5.3.4 拆成 ego-motion 與 rigid-extrinsic 兩條路徑。

**Key Formulas:**

$$
F_{\mathrm{token}}(t, m) = \mathrm{Concat}\!\left(F_{\mathrm{pos}}^{cam}(m), F_{\mathrm{pos}}^{seq}(t, m), F_{\mathrm{depth}}(t, m)\right)
$$

$$
\{F(i, j)\}_{(i, j)} = \mathrm{Attention}^{i}\!\left(\{\{F_{\mathrm{token}}(i, j)\}_{1}^{M}\}_{i-k}^{i+k}\right)
$$

**Implementation Details:**

視窗半徑 $k$、選用的「四個 task-relevant 層」具體 index、attention head 數、`d_fused` 的具體值，the paper does not specify。

#### 5.3.4 Factorized Decoding (Rigidity-Based Aggregation)

**Function:** 利用 rig 不形變的物理事實，把跨相機與跨時間的資訊解耦：跨相機平均得到「共用的自車運動」，跨時間平均得到「不變的 rig 安裝外參」，作為後續 head 的輔助約束訊號。

**Input:**
- Name: `F^{seq}, F^{rel}`（MCA refined token 中對應的 sub-token）
- Shape: `F^{seq}(t, m)` 形狀 `[B, M, T, d]`；`F^{rel}(i, j)` 形狀 `[B, M, T, d]`
- Source: §5.3.3 MCA 輸出

**Output:**
- Name: `F_agg^{seq}(t), F_agg^{rel}(m)`
- Shape: `[B, T, d]` 與 `[B, M, d]`
- Consumer: §5.3.5 Prediction Heads（Sequential Pose Head 與 Relative Pose / Ego Head）

**Processing:**

1. **Ego-Motion Pooling**：對每個時間步 $t$，跨 $M$ 台相機平均其 sequential pose token，得到一個 per-frame 的 ego-motion 表徵（式 (10)），確保所有相機在後續 decoding 時共享同一條自車軌跡。
2. **Extrinsic Aggregation**：對每台相機 $m$，跨整段 $T$ 幀的 relative pose token 平均，得到對 rig 安裝姿態的穩定估計（式 (11)），這個量在整段序列裡視為時間不變。
3. 兩條 aggregation 路徑明確把「會隨時間變化的自車運動」與「時間不變的 rig 外參」拆開，使最後 decoding 出來的相機軌跡天然滿足剛體約束。

**Key Formulas:**

$$
F_{\mathrm{agg}}^{seq}(t) = \frac{1}{M} \sum_{m=1}^{M} F^{seq}(t, m)
$$

$$
F_{\mathrm{agg}}^{rel}(m) = \frac{1}{T} \sum_{j=1}^{T} F^{rel}(i, j)
$$

**Implementation Details:**

論文式 (11) 在求和項使用 $N$ 與 $j$ 但語意上對應整段時間 $T$ 上的平均，且 token 標註方式略有混用；具體 attention head/projection 結構 the paper does not specify。

#### 5.3.5 Prediction Heads (Camera Pose / Depth / Scale)

**Function:** 把 MCA 與 aggregation 後的 token 解碼成最終輸出：序列位姿、相對外參、dense depth 與全域 metric scale。

**Input:**
- Name: `F_agg^{seq}, F_agg^{rel}, F_depth, T^{rel}_{real}, T^{rel}_{norm}`
- Shape: 詳見前述 §5.3.4 與 §5.3.1；`T^{rel}_{real}` 為校正得到的真值相對 translation `[B, M, 3]`，`T^{rel}_{norm}` 為網路預測的 normalized translation `[B, M, 3]`
- Source: §5.3.4 Aggregation、§5.3.1 TVA depth tokens、以及外部校正資料

**Output:**
- Name: `g^{seq}, g^{rel}, G^{global}, D_hat, scale`
- Shape: 序列位姿與相對位姿各為 `[B, M, T, 6]` 與 `[B, M, 6]`，組合後 `G^{global}(i, j) ∈ [B, M, T, 4, 4]`；深度 `[B, M, T, 1, H, W]`；scale `[B, 1]`
- Consumer: Loss（§5.3.6）與下游 4D 重建後處理

**Processing:**

1. **Camera Pose Head**：沿用 VGGT 的 camera head，但拆成兩個分支——Relative Pose Head 輸出時間不變的相對外參與內參，Sequential Pose Head 輸出每段視訊每相機的外參；兩者透過矩陣相乘合成全域位姿 $G^{global}(i, j) = G^{seq}(i, j) \times G^{rel}(i, j)$（式 (12)），其中 $G = \begin{bmatrix} R & T \\ 0 & 1 \end{bmatrix}$。
2. **Depth Head**：採用 VGGT 的 DPT head，內含 4 個 refinement sub-module，從 spatial-compressed geometry token 漸進解碼出 high-resolution dense depth 與 depth confidence map。
3. **Scale Head**：把 normalized 預測還原到真實尺度。對每台相機計算「真值相對 translation」與「預測 normalized 相對 translation」的比值，再對所有相機取平均得到 scale（式 (13)）。最終把 scale 乘回 depth 與位姿 translation 部分，即可恢復 metric-scale 的 world points。

**Key Formulas:**

$$
\mathbf{G}^{global}(i, j) = \mathbf{G}^{seq}(i, j) \times \mathbf{G}^{rel}(i, j)
$$

$$
\mathrm{Scale} = \mathrm{Avg}\!\left(\sum_{j} \frac{T^{rel}_{real}(j)}{T^{rel}_{norm}(j)}\right)
$$

**Implementation Details:**

DPT head 解析度與 channel 數沿用 VGGT 預設；scale 的 division 採 element-wise 還是只取 norm、Avg 是否包含 outlier-rejection，the paper does not specify。

#### 5.3.6 Training Loss

**Function:** 以 depth、relative pose、sequential pose 三項加權總和監督訓練，沿用 VGGT 的 depth loss 設計，並把 camera pose loss 因子分成 $L_{rel}$ 與 $L_{seq}$ 對應分解後的 head。

**Input:**
- Name: `D_hat, Σ_hat, g^{rel}, g^{seq}` 與其對應 ground truth
- Shape: 與 §5.3.5 輸出一致；ground-truth depth 由 §6 描述的 LiDAR Densification Pipeline 產生
- Source: §5.3.5 Prediction Heads 與資料前處理

**Output:**
- Name: `L_total`
- Shape: 標量
- Consumer: 反向傳播優化整條管線

**Processing:**

1. 總損失為加權和 $L_{total} = \lambda_1 L_{depth} + \lambda_2 (L_{rel} + L_{seq})$，論文設定 $\lambda_1 = 0.1$、$\lambda_2 = 1.0$（式 (14)）。
2. **Depth Loss**：對每個 $(i, j)$，含三項——uncertainty-weighted L1 depth error、uncertainty-weighted gradient error、以及 $-\alpha \log \hat{\Sigma}_{ij}$ 的不確定性正則項（式 (15)），與 VGGT 一致。
3. **Pose Loss**：相對位姿與序列位姿各自用 Huber loss $\|\cdot\|_{\epsilon}$ 配合學到的不確定性 $\Sigma$ 加權（式 (16)、(17)），保證鉗制 outlier 的同時維持平滑梯度。

**Key Formulas:**

$$
L_{total} = \lambda_1 L_{depth} + \lambda_2 (L_{rel} + L_{seq})
$$

$$
L_{\mathrm{depth}} = \sum_{i=1}^{T}\sum_{j=1}^{M} \left\| \hat{\Sigma}_{ij}(\hat{D}_{ij} - D_{ij}) \right\| + \left\| \hat{\Sigma}_{ij}(\nabla \hat{D}_{ij} - \nabla D_{ij}) \right\| - \alpha \log \hat{\Sigma}_{ij}
$$

$$
L_{\mathrm{rel}} = \sum_{j=1}^{M} \left\| \Sigma_{j}(\hat{\mathbf{g}}_{j} - \mathbf{g}_{j}) \right\|_{\epsilon}, \qquad L_{\mathrm{seq}} = \sum_{i=1}^{T} \left\| \Sigma_{i}(\hat{\mathbf{g}}_{i} - \mathbf{g}_{i}) \right\|_{\epsilon}
$$

**Implementation Details:**

訓練分兩階段：先以 lr $2 \times 10^{-4}$、batch 為隨機 3–10 frame（即 18–60 張影像）訓練 20 epoch（每 epoch 1000 iteration）；再凍結 aggregator、以 lr $1 \times 10^{-5}$ fine-tune 5 epoch。Huber 的 $\epsilon$ 與 depth loss 中的 $\alpha$ 具體值 the paper does not specify。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| nuScenes [3] | Multi-camera 4D 重建（pose、depth、inference time） | 1,000 個場景，每段 20 秒，6 路相機 360° 覆蓋、32-beam LiDAR、2 Hz keyframes | 700 scenes 訓練 / 150 scenes 驗證（the paper does not specify a separate test split） |

備註：作者另以 LiDAR Densification Pipeline（多 sweep 時空聚合 + 利用 3D bounding box 對動態物體在物體座標系內聚合 + bilateral / morphology 補洞）為 nuScenes 產生 dense depth ground truth，作為 supervised depth head 的訓練訊號（§4.1、Fig. 4）。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| AUC@30 ↑ | Camera pose 估計的 AUC，閾值 30°，數值越高越好（Table 1） | yes |
| AUC@15 ↑ | Camera pose 估計的 AUC，閾值 15°，較嚴格的姿態評估（Table 1） | yes |
| Abs Rel ↓ | Depth 估計的 absolute relative error，越低越好（Table 2） | yes |
| $\delta_3$ ↑ | Depth threshold accuracy（$\max(\hat d/d, d/\hat d) < 1.25^3$ 的比例），越高越好（Table 2） | no |
| Inference time (ms) ↓ | 在不同 frame 數（15/25/35）下的推論耗時（Table 3） | yes |

### 6.3 Training and Inference Settings

- **輸入解析度**：將 nuScenes 原始 1600×900 影像縮放至 518×280，並同步調整 intrinsics 以保持 ground-truth 一致（§4.2）。
- **Scale 處理**：對 depth map 與 camera pose 進行 scale normalization（與 VGGT 一致），但額外將 scale 本身納入訓練監督。
- **訓練階段一**：每 batch 隨機抽取 3–10 frame 的 multi-camera 影像（即 18–60 張 image），共 20 epochs；每 epoch 1,000 個 iteration，learning rate $2\times 10^{-4}$。
- **訓練階段二**：凍結 aggregator，再 fine-tune 5 epochs，learning rate $1\times 10^{-5}$。
- **公平比較**：所有對照模型（VGGT、StreamVGGT、fastVGGT）皆以相同流程重新訓練（§4.2）。
- **Loss**：$L_{\text{total}} = \lambda_1 L_{\text{depth}} + \lambda_2 (L_{\text{rel}} + L_{\text{seq}})$，$\lambda_1=0.1$、$\lambda_2=1.0$；pose loss 使用 Huber loss（§3.5, Eqs. 14–17）。
- **Window size**：MCA 預設 $k=3$（即 window size = 3，§4.7、Table 5）。
- **推論測試長度**：分別以 15、25、35 frames（每 frame 6 cameras，即 90 / 150 / 210 images）進行評估（§4.3）。
- **硬體、batch size、優化器、warmup / decay schedule**：the paper does not specify。
- **程式碼**：作者提供 GitHub 連結（`https://github.com/SII-skyboard/DriveVGGT`），但 the paper does not specify weights / configs 是否同步釋出。

### 6.4 Main Results

**Pose Estimation（AUC@30 ↑，nuScenes，Table 1）**

| Method | Rel. pose embed | frame=15 | frame=25 | frame=35 | Notes |
|---|---|---|---|---|---|
| VGGT [33] | ✗ | 0.8531 | 0.7866 | 0.6871 | vanilla baseline |
| StreamVGGT [53] | ✗ | 0.7005 | OOM | OOM | 長序列 OOM |
| fastVGGT [27] | ✗ | 0.8246 | 0.7707 | 0.6830 | training-free 加速版 |
| VGGT [33] | ✓ | 0.8164 | 0.7403 | 0.6445 | 直接加 rel pose 反而退化 |
| fastVGGT [27] | ✓ | 0.7915 | 0.7321 | 0.6477 | 同上 |
| **DriveVGGT (VGGT)** | ✓ | **0.8635** | **0.8010** | **0.7200** | 在所有 frame 數均最佳 |
| DriveVGGT (fastVGGT) | ✓ | 0.8534 | 0.7844 | 0.6995 | 次佳 |

**Depth Estimation（nuScenes，Table 2）**

| Method | Rel. pose embed | Abs Rel ↓ (f=35) | $\delta_3$ ↑ (f=35) | Notes |
|---|---|---|---|---|
| VGGT [33] | ✗ | 0.3605 | 0.8858 | baseline |
| StreamVGGT [53] | ✗ | OOM | OOM | 25/35 frames OOM |
| fastVGGT [27] | ✗ | 0.3660 | 0.8825 | |
| **DriveVGGT (fastVGGT)** | ✓ | **0.3539** | **0.8935** | 長序列 depth 最佳 |
| DriveVGGT (VGGT) | ✓ | 0.3601 | 0.8892 | f=15 略遜於 vanilla VGGT（0.3805 vs. 0.3666） |

**Inference Time（ms，Table 3）**

| Method | frames=15 | frames=25 | frames=35 | Notes |
|---|---|---|---|---|
| VGGT [33] | 2268 | 5241 | 9666 | 長序列接近 10 s |
| StreamVGGT [53] | 6916 | OOM | OOM | |
| fastVGGT [27] | 1950 | 3341 | 4949 | |
| **DriveVGGT (VGGT)** | **1836** | **3294** | **4907** | 35 frames 較 vanilla VGGT 降 49.3% |
| DriveVGGT (fastVGGT) | 2390 | 3823 | 5043 | 短序列因 fastVGGT 額外 token aggregation 而較慢（§6.5 補充說明） |

整體而言，DriveVGGT (VGGT) 在 pose 與 inference time 上同時取得最佳；DriveVGGT (fastVGGT) 則在 depth metric 上取得最佳，二者互補。

### 6.5 Ablation Studies

- **Component ablation（Table 4，frame=25）**：以 TVA-only 為 baseline，AUC@30 僅 0.039（顯示無 cross-camera 資訊的多相機系統幾乎無法估姿態）；加入 relative pose embedding 後 AUC@30 跳到 0.7855；再加完整 MCA 構成 DriveVGGT，AUC@30 達 0.8010、推論時間從 2052 ms 升至 3294 ms。此 ablation 直接對應論文三大 prior 中的 (ii) Calibrated Geometric Constraints 與 (iii) Rigid Extrinsic Constancy，屬於診斷性 ablation。**注意**：TVA-only baseline 的 0.039 AUC 看起來像是 sanity check（確認沒有 cross-view 訊號就無法解多相機外參），其實際資訊量低於後兩列。
- **Window size（Table 5，frame=25）**：$k=3$ AUC@30 = 0.8010、time = 3294 ms；$k=5$ → 0.8033 / 4924 ms；$k=7$ → 0.8087 / 7263 ms。AUC 隨 window 變大微幅提升（< 0.01），但推論時間翻倍以上，作者據此認為 $k=3$ 已足夠，間接支持 Sparse Spatial Overlap 主張。屬於合理的效率—精度 trade-off 診斷。
- **Scale head（Table 6，frame=15）**：以 least-squares 對齊（即不靠 scale head）vs. scale-based（用 scale head 預測的 scale）對比 depth。Abs Rel：0.3805 (LS) vs. 0.3666 (scale-based)；$\delta_3$：0.8747 vs. 0.7412。Abs Rel 顯示 scale head 有效，但 $\delta_3$ 反而下降，論文未討論此矛盾，屬於弱點：宣稱「scale head 能轉到 real-world scale」缺乏更直接的 metric-scale 評估指標（例如以公尺為單位的 RMSE）。
- **缺失的 ablation**：(a) 無 ego-motion / sequential pose head 拆分前後的對比；(b) 無 TVA 改回 global attention 在相同其他模組下的對比；(c) 無對 dense depth ground-truth pipeline 與直接用稀疏 LiDAR 監督的比較。這些是直接驗證論文核心宣稱的診斷實驗，目前未涵蓋。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline — 對 VGGT [33]、StreamVGGT [53]、fastVGGT [27] 進行比較，皆為 VGGT 系列近期 SOTA；但未與 AD 專用 feed-forward 重建方法（如 Driv3r [7]、Rig3r [20]）做直接比較。
- [missing] Has cross-task / cross-dataset evaluation — 全部實驗僅在 nuScenes 上進行，未覆蓋 Waymo、KITTI、Argoverse 等其他 AD 資料集，亦未跨任務驗證。
- [partial] Has ablations that diagnose the new components — Component ablation（Table 4）與 window size（Table 5）為診斷性，但未拆分 sequential / ego-motion factorized head、未對比 TVA vs. global attention，覆蓋不完整。
- [missing] Has a scaling study — 雖測試 15/25/35 frames，但未對模型大小、相機數量、image 解析度做 scaling 實驗。
- [covered] Has an efficiency / wall-clock comparison — Table 3 完整提供 ms-level inference time，並指出 35-frame 場景下較 VGGT 降 49.3%。
- [missing] Reports variance / standard deviation / multiple seeds — 所有表格僅給單一數值，未報告 std 或 seed 變異。
- [partial] Releases code / weights / data sufficient for reproducibility — 第 1 頁提供 GitHub repo（`SII-skyboard/DriveVGGT`），但 the paper does not specify 權重、densified depth GT pipeline 與訓練 config 是否同步公開。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **「TVA 解決 Sparse Spatial Overlap 並降低 $O((M\cdot T)^2)$ 複雜度」** — *被支持*。Table 3 顯示 frame=35 從 9666 ms 降至 4907 ms,Table 5 顯示縮窗到 $k=3$ 不會犧牲精度,二者一起證明 cross-view global attention 在自駕情境的多餘性。
- **「MCA + 校正注入啟用絕對公制尺度」** — *部分支持*。Table 6 對比 least-squares 與 scale-based 對齊,$\delta_3$ 從 0.7412 提升到 0.8747,但只在 frame=15 報告且僅一個 metric;沒有報告 metric depth 在不同距離 bin (0–20 m / 20–50 m / 50+ m) 的分層誤差,而自駕對遠距 metric 才是關鍵。
- **「Factorized decoding 強制 rigid extrinsic constancy」** — *證據不足*。Table 4 沒有「TVA + MCA 但不 factorize」這一列,因此 factorized pose head 的邊際貢獻無法量化;論文只用 Fig. 5 的視覺化暗示其效果。
- **「對 vanilla VGGT 在長序列上推理時間減少 49.3%」** — *對 VGGT 被支持,對最強 baseline 不被支持*。Table 3 frame=35:相對 VGGT 確實 −49.3%,但相對 fastVGGT 只 −0.85%;Abstract 與 Section 1 沒揭露這個更強對手的接近平手結果。
- **「DriveVGGT 是任意幾何 transformer 的通用插件 (Universal AD Framework)」** — *被高估*。論文只示範了 VGGT 與 fastVGGT 兩個同源 backbone,未測試 DUSt3R、MASt3R、Streaming VGGT、Block-sparse VGGT 等;且實驗只跑在 nuScenes 一個 rig 配置 (6 相機、固定外參),「Universal」尚未跨資料集或跨車型驗證 (Table 7, page 15)。

### 7.2 Fundamental Limitations of the Method

**Calibration 依賴的單向性。** 整個 MCA 與 scale head 都把 $P_{cam}(j)$ 視為「物理量尺」並一次性嵌入 $F^{cam}_{pos}(j)$,其架構假設 calibration 永遠正確;但量產車隊的外參會因震動、溫漂、感測器更換而漂移,而模型既沒有 online 校正路徑,也沒有對 calibration 殘差的不確定性建模,因此一旦校正退化,scale head 會把錯誤外參當作 ground truth ruler,把不準的尺度傳遞給 depth 與 ego-pose。

**單 rig 設定的耦合。** Eq. 7 的 $F^{cam}_{pos}(j)$ 在每個 sensor 配置只計算一次,意味模型權重與該 rig 的 baseline、視角分佈共生;遷移到不同車型(Waymo 5 camera、Argoverse 7 camera 或乘用車後加裝感測器)需要重新嵌入並可能重訓,削弱了「前饋通用模型」應有的 zero-shot 能力。論文沒有探討 cross-rig fine-tune 成本,也未提供 calibration token 的 generalization 機制(例如將 $P_{cam}$ 編碼為 RoPE-like 連續函數,而非離散 token)。

**Sparse Overlap 假設並非處處成立。** TVA 把每個相機獨立處理,完全靠時間軸的 self-overlap 建立幾何;但在高速公路低紋理場景、隧道內部、強逆光、或單相機被雨滴遮蔽時,單視角時序連續性會崩解,而 MCA 的 window attention 只在 $\pm k$ frame 內聚合。模型缺少跨相機 fallback 機制,使得「sparse overlap」的工程假設一旦被破壞(例如下雨後前後相機都失焦),整個尺度與軌跡都會同時失敗。

**深度 GT 的 LiDAR 偏差繼承到評估。** 兩階段 densification 雖填補空洞,但仍以 LiDAR 為信源,其在玻璃、水面、植被薄層、超出 50 m 距離的覆蓋本來就不可靠;Table 2 的 Abs Rel 與 $\delta_3$ 因此測量的是「對 LiDAR-densified pseudo-GT 的相似度」,而不是真正的 metric depth 準確度。當下游使用者期待用 DriveVGGT 取代 LiDAR 時,這層 pseudo-GT 偏差就轉成系統性低估了真實誤差。

### 7.3 Citations Worth Tracking

- **VGGT [33]** — DriveVGGT 的 backbone 基線;閱讀其 token 設計、camera head 與 DPT depth head 是讀懂本論文 Section 3.4 的前置。
- **Pi3 (permutation-equivariant) [37]** — 直接針對 VGGT 對「首幀位姿初始化」敏感的順序偏差,是本論文 sequential pose head 的另一條替代路徑;比較兩者可澄清 factorized decoding 的取捨。
- **Rig3R [20]** — 同期 "Rig-aware" 重建工作,問題定位幾乎與 DriveVGGT 重疊但解法不同,缺少於本論文的對照實驗,值得獨立評估。
- **Cameras as Relative Positional Encoding [19]** — 用 RoPE 風格將相機視為相對位置編碼,有機會替換 Eq. 7 的 concat-and-MLP 嵌入,提供更原則化的 calibration injection。
- **Block-sparse VGGT [31]** — 用塊稀疏 global attention 處理同一個算力瓶頸,是對 TVA 的天然 baseline,本論文僅在 Related Works 一筆帶過、未做頭對頭實驗。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在 $P_{cam}(j)$ 注入合成噪聲(例如 $\pm 1^\circ$ 旋轉、$\pm 1$ cm 平移)後,Table 1 的 AUC@30 與 Table 6 的 scale 對齊精度會如何退化?
- [ ] Table 4 的 baseline(TVA) AUC@30 = 0.039 是真的近隨機,還是排版錯誤(應為 0.39)?若為真,TVA 是否應被重新定位為「必要前處理」而非獨立貢獻?
- [ ] 為何沒有 "TVA + MCA 不 factorize pose head" 這列 ablation?factorized decoding 對最終 AUC 的邊際貢獻具體是多少?
- [ ] 將輸入解析度從 518×280 改回 nuScenes 原生 1600×900 後,49.3% 的推理加速與 Abs Rel 改善是否同時保留?
- [ ] DriveVGGT 是否能在 Waymo Open Dataset(5 camera、不同基線)或 Argoverse 2(7 camera)上零再訓練 / 少量微調轉移?
- [ ] 套用 scale head 後,frame=25/35 在 metric 單位下的 ATE 與 per-frame RPE 是多少?與傳統 VO(ORB-SLAM3、DPVO)相比落在哪個檔次?
- [ ] Eq. 13 對 $T^{rel}_{norm}(j) \to 0$ 的相機對(例如 BACK_LEFT–BACK_RIGHT 短基線)是否會造成尺度發散?是否需要加 robust averaging(median / Huber)?

### 8.2 Improvement Directions

1. **加入 calibration-noise robustness 實驗** — 對 $P_{cam}(j)$ 注入可控擾動並重跑 Table 1 / Table 6。理由:這是量產車隊最常見的退化模式,而 MCA 與 scale head 的整個邏輯都站在「校正可信」之上,缺少這個實驗等於對部署情境完全沉默。可行性最高,只需 inference-time 修改。
2. **補上 factorized-decoding-only ablation 與 metric pose 指標** — 在 Table 4 加入 "TVA+MCA, no factorized head" 列,並在 Table 1 旁加上以 m 為單位的 ATE / RPE。理由:目前三大貢獻只能聯合驗證,且 AUC@30 對 metric scale 不敏感,擴充指標才能對齊 VO 文獻。可行性高,純評估端工作。
3. **跨資料集驗證 "Universal" 宣稱** — 在 Waymo 或 Argoverse 2 上重訓並比較對 nuScenes 預訓練權重的 zero-shot / few-shot 表現。理由:Table 7 將 "Universal AD Framework" 列為核心貢獻,但只有單 rig 證據;跨 rig 是該宣稱成立的唯一充分條件。可行性中等,需要重建另一條 LiDAR Densification 管線。
4. **將 $F^{cam}_{pos}(j)$ 改為 RoPE-style 相對位置編碼** — 採 [19] 的精神,將相機外參作為連續 attention bias 而非 concat token。理由:concat 嵌入綁死於特定 rig token 數,RoPE 形式才能在不同 $M$ 之間共享參數,真正支撐 "Universal" 宣稱;同時也減低 Eq. 7 的線性 MLP 對小擾動過擬合的風險。可行性中等,需架構改動。
5. **以可學習權重或不確定性取代 Eq. 13 的均值 scale 估計** — 例如將每對相機的 $T^{rel}_{real}/T^{rel}_{norm}$ 加上由 confidence head 給出的權重,或在分母接近零時切換到 log-scale 形式。理由:目前的算術平均對 outlier 與小基線高度敏感,僅在 frame=15 / 單一 metric 驗證難以保證部署情境穩定。可行性中等,但能直接強化 scale head 的核心宣稱。
