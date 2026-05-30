<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# PAS3R — PAS3R: Pose-Adaptive Streaming 3D Reconstruction for Long Video Sequences

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | PAS3R |
| Paper full title | PAS3R: Pose-Adaptive Streaming 3D Reconstruction for Long Video Sequences |
| arXiv ID | 2603.21436 |
| Release date | 2026-03-22 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.21436 |
| PDF link | https://arxiv.org/pdf/2603.21436v1 |
| Code link | https://pas-3r.github.io/PAS3R.io/ |
| Project page | https://pas-3r.github.io/PAS3R.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Lanbo Xu | State Key Laboratory of Human-Machine Hybrid Augmented Intelligence, Institute of Artificial Intelligence and Robotics, Xi'an Jiaotong University, China | — | first author |
| Liang Guo | State Key Laboratory of Human-Machine Hybrid Augmented Intelligence, Institute of Artificial Intelligence and Robotics, Xi'an Jiaotong University, China | — | co-author |
| Caigui Jiang | State Key Laboratory of Human-Machine Hybrid Augmented Intelligence, Institute of Artificial Intelligence and Robotics, Xi'an Jiaotong University, China | https://caiguijiang.github.io/ | corresponding author |
| Cheng Wang | University of East Anglia, Norwich, NR47TJ, United Kingdom | https://chengwang12.github.io/ | corresponding author |

### 1.2 Keywords

Online 3D reconstruction, Streaming reconstruction, Pose-adaptive update, Test-Time Training, Fourier transform, Trajectory consistency, Acceleration regularization, Spatiotemporal smoothing, Monocular video, Pointmap

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| TTT3R | baseline | 以 cross-attention 學習率調整與 state reset 緩解線上重建遺忘,PAS3R 直接對其 update 機制改良 |
| CUT3R | predecessor | 用 recurrent memory + local attention 將端對端 3D 重建擴展到線上場景,PAS3R 沿用其串流框架 |
| DUSt3R | influence | Transformer 端對端無校正 stereo 重建的開創之作,奠定整條 feed-forward pointmap 路線 |
| VGGT | baseline | 前饋式 global-attention Transformer 多視角重建,代表離線批次處理對照組 |
| Fast3r | baseline | 單次前饋多視角端對端重建,展示 global attention 的計算瓶頸 |
| InfiniteVGGT (IVGGT) | concurrent | 用自適應 KV-cache 將端對端線上重建延伸至長序列,與 PAS3R 同期針對長序列議題 |
| 3D Gaussian Splatting (3DGS) | influence | 新興的顯式可微渲染表示,雖非直接基線,但代表近期重建表示的演進方向 |

## 2. Research Overview

### 2.1 Research Topic

本論文鎖定「線上單目串流 3D 重建」此一電腦視覺次領域,目標是從連續輸入的單眼影片中,於常數記憶體下逐幀恢復相機姿態與稠密點雲幾何。研究核心議題在於長序列下的「穩定性—適應性」兩難:模型需快速吸收新視點資訊以擴展場景,卻又不能讓單一全域狀態被新觀測過度覆寫,造成歷史結構遺忘、軌跡漂移與幾何不一致。作者以 Test-Time Training 視角將狀態更新理解為 fast-weights 的線上梯度步,並引入相機運動量與影像頻譜結構作為更新強度的調控訊號,同時透過相對姿態約束、加速度正則化與輕量化線上時空穩定模組,系統性地處理長序列軌跡抖動與點雲邊界瑕疵問題。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- SLAM / Visual Odometry
- Online / Streaming Learning
- Test-Time Training

### 2.3 Core Architectures Used

- **Recurrent memory + cross-attention streaming backbone**:沿用 CUT3R 式的持久化 memory $S_{t-1} \in \mathbb{R}^{n \times c}$ 與輸入幀 $X_t$ 之間的 cross-attention 更新,構成 PAS3R 的串流主幹,使常數記憶體推論成為可能(§3.1, Fig. 1)。
- **Test-Time Training (TTT) fast-weights 更新觀點**:把 memory 視為推論期可動態更新的 fast weights,以 $\mathrm{Update}(S_{t-1}, X_t) = S_{t-1} - \beta \nabla(S_{t-1}, X_t)$ 表述線上梯度步,作為調控更新強度的數學框架(§3.1, Eq. 1)。
- **Pose-adaptive state update modulation(本文新增)**:以幀間平移量 $\Delta x$、旋轉量 $\Delta q$ 與灰階影像之 Discrete Fourier Transform 高頻能量比 $R$ 共同決定每幀的學習率權重 $s = s_1 \cdot s_2$,顯式對齊「幾何新穎度」(§3.1, Eq. 2–7)。
- **Trajectory-consistent training objective(本文新增)**:在訓練端聚合 ATE、RPE 與加速度正則項,連同 confidence-aware 3D regression loss 與 RGB loss 共同最佳化軌跡時間連貫性(§3.2, Eq. 8–14)。
- **Online spatiotemporal stabilization module(本文新增)**:推論時對相機平移以 One Euro filter、對旋轉四元數以 Slerp 進行時序平滑,並對輸出點雲套用 online bilateral filtering 以保留邊界並抑制平面瑕疵(§3.3, Eq. 15–16, Fig. 4–5)。
- **DUSt3R-style feed-forward pointmap regression**:沿襲 DUSt3R/CUT3R 的端對端 pointmap 預測範式,直接由 encoder–decoder 在每步輸出相機姿態、深度圖與稠密點雲,而非依賴傳統 SfM/MVS 後處理(§2.2, Fig. 1)。

### 2.4 Core Argument

作者認為現有線上串流 3D 重建之所以在長序列下失穩,根因在於「狀態更新強度」沒有對應到「該幀帶來的幾何新穎度」。傳統 RNN 式更新採固定學習率;TTT3R 等近期方法雖以 cross-attention 動態調整學習率,但其依據是特徵相似度,而非實際視點變化幅度。這導致兩種對稱的失敗模式:當相機發生劇烈位移或轉折時,attention 訊號未必同步放大,模型無法及時納入新幾何,造成軌跡漂移;反之當相機近乎靜止、影像高度相似時,過強的更新反而稀釋了已累積的歷史結構,引發幾何不一致與閃爍。作者主張只要回到物理直覺——以「幀間平移與旋轉量」加上「Fourier 頻譜表徵的影像結構豐富度」作為更新權重的顯式條件——就能讓 fast-weights 的步長真正對齊場景的幾何資訊增量,於是 pose-adaptive state modulation 成為邏輯上必要的修正。為了把這項局部修正延伸到長時序穩定性,他們進一步以 ATE、RPE 與加速度正則項約束軌跡的時間連貫性,並以線上雙邊濾波抑制殘留抖動與深度不連續處的瑕疵,三者共同構成從「單幀更新規則」到「長序列軌跡幾何」的閉環論證,使 PAS3R 能在維持串流常數記憶體的前提下,同時提升長序列與短序列的姿態、深度與點雲品質。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(290 words)

論文標題 *PAS3R: Pose-Adaptive Streaming 3D Reconstruction for Long Video Sequences* 直接點出三個關鍵字：pose-adaptive、streaming、long video。標題本身即傳達了論文的問題定位——不是處理任意 multi-view 影像集，而是針對「streaming 單目長序列」這一特定場景，並以 pose 自適應作為主要技術特徵。

Abstract 以「stability–adaptation dilemma」作為敘事支點開場：streaming 重建模型必須在「快速吸收新視角」與「保留已累積場景結構」之間取得平衡。作者隨即點名既有方法（uniform update 或 attention-based update）的失敗模式：在劇烈視角轉換時更新不足、在輕微變動時又過度覆寫歷史資訊，最終在長序列上呈現 trajectory drift 與 geometric inconsistency。

接著 abstract 揭示 PAS3R 的核心 insight：「frames contributing significant geometric novelty should exert stronger influence on the reconstruction state」。這個原則由三個技術元件落實：（1）motion-aware update mechanism，結合 inter-frame pose variation 與 image frequency cue 來估計 frame importance；（2）trajectory-consistent training objective，加入 relative pose constraint 與 acceleration regularization；（3）lightweight online stabilization module，抑制 high-frequency trajectory jitter 與 geometric artifact，且不增加 memory consumption。

最後 abstract 主張在多個 benchmark 上 PAS3R 顯著提升 trajectory accuracy、depth estimation 與 point cloud reconstruction quality，特別在長序列場景；同時於短序列保持 competitive，並提供 source code（pas-3r.github.io）。Keywords 列出 Online 3D reconstruction、Learning rates、Fourier transforms、Acceleration constraints、Spatiotemporal smoothing，呼應三大模組設計。

abstract 的敘事策略是「先點出 dilemma → 指責既有方法失衡 → 提出 pose-adaptive 為解 → 三模組對應 → 經驗結果背書」，為後續 Introduction 直接展開「為何 pose 變化幅度應該決定更新強度」的論證舖墊；它也為 §3.1 介紹的 frame importance score $s = s_1 \cdot s_2$ 與 §3.2 的 trajectory-consistent loss 預先定義了問題語彙。

### 3.2 Introduction

(740 words)

Introduction 採三段論結構：先建立 3D reconstruction 的背景脈絡，再聚焦於 streaming online 場景的核心痛點，最後揭示 PAS3R 的設計動機。

第一階段重述 3D reconstruction 的問題定義與表徵分類：explicit（point cloud、mesh、voxel、3DGS）vs. implicit（NeRF 系列）。作者特別點出 point cloud 表徵因 flexibility 與 downstream geometry 處理的相容性而仍被廣泛採用，從而合理化本文選擇以 dense point cloud 作為輸出形式。接著從「calibrated multi-view」過渡到「monocular uncalibrated」場景，宣示本文針對日常情境中常見、無相機參數的單目視訊。

第二階段建立 offline vs. online 的分類張力。Offline 方法（如 attention-based 全域處理）能直接從序列預測 pose，但 batch processing 導致 memory 隨序列長度線性成長；online 方法以 fixed-size state vector 達成 constant memory，卻引入 catastrophic forgetting：state 必須隨每個新視角更新，使早期 frame 在 state 中所佔比例隨序列推進而稀釋。這段論證將「constant memory」與「forgetting」拉成 trade-off，自然導向後續的 update mechanism 討論。

第三階段聚焦於最近的 TTT3R：它以 historical/incoming feature 之間的 cross-attention 動態調整 learning rate，部分緩解 forgetting，但缺乏對「視角變化幅度」的顯式建模。作者在此提出兩個失衡情境：（a）相機劇烈位姿變化時 update intensity 仍可能不足，模型難以快速吸收新幾何；（b）位姿變化微小時，過強更新反而覆寫歷史。這一觀察直接映射到 abstract 所述 dilemma，並把問題從「forgetting」進一步精煉為「update intensity 與 geometric novelty 的不對稱」。

提出 PAS3R 之後，introduction 以「中心思想 + 機制 + 訓練 + 推論」四段式展開：核心思想是 frame 對 state 的影響應由其 geometric novelty 決定；操作層面以 pose-adaptive state update mechanism 動態調整 update intensity，輸入訊號為 inter-frame camera motion 與 scene frequency；訓練端引入 trajectory-consistent objective（relative pose 與 acceleration regularization）以穩定時間序列；推論端附加 lightweight online stabilization 模組以抑制 jitter 與 artifact。最後宣告 PAS3R 在長序列上優於 SOTA online 方法，並在短序列保持 competitive。

Introduction 末段以四點 bullet 收束貢獻：（1）pose-adaptive streaming framework，依 camera motion 與 scene structure 調節 state update；（2）frame importance estimator，融合 inter-frame displacement 與 image frequency cue；（3）relative pose 與 acceleration regularization 的訓練目標；（4）efficient spatiotemporal stabilization strategy。四項貢獻一一對應 §3.1、§3.2、§3.3，使 introduction 直接成為 method section 的 outline。

整體而言，introduction 將敘事支點從「general 3D reconstruction」漸次收窄到「streaming」「monocular long sequence」「pose-adaptive update」，並透過對 TTT3R 的 specific critique 創造 research gap，為 §2 Related Work 中對 traditional / end-to-end / spatial consistency 三個子領域的橫向比較預作鋪陳，也為 §3 Approach 介紹 $s_1, s_2$ 設計提供問題語境。

### 3.3 Related Work / Preliminaries

(680 words)

§2 將既有研究組織為三條主線：traditional geometry-based、end-to-end learnable、spatial geometric consistency；每條主線都以「present limitation → 與 PAS3R 的 contrast」收束，使整節同時承擔 literature survey 與 positioning 雙重功能。本論文沒有獨立的 Preliminaries 節，TTT 與 fast/slow weights 等基礎概念被內嵌於 §3.1 的 update equation 推導中，因此 §3.3 的 walkthrough 主要對應論文 §2 三個子節。

§2.1 Traditional 3D Reconstruction Methods 從 multi-view geometry 理論出發，回顧 SfM、MVS 作為 offline 重建的奠基；以 COLMAP 為代表，feature extraction（SIFT/ORB/SuperPoint/SuperGlue）配合 global Bundle Adjustment 重建高精度 pose 與 dense point cloud。作者隨即指出此 paradigm 的代價：global optimization 必須同時取用所有歷史 frame，計算複雜度近似 cubic，難以滿足 real-time。SLAM 系統（ORB-SLAM2、DSO、SVO、DROID-SLAM、NICE-SLAM）以 keyframe + sliding window local optimization 緩解，但記憶體與計算仍隨序列長度增長，且在 low-texture 與 rapid motion 情境下 accumulated error 嚴重。本子節以「constant memory long-sequence」作為 PAS3R 的目標差異點。

§2.2 End-to-End 3D Reconstruction Methods 鋪陳深度學習路線。以 DUSt3R 為起點，介紹 Transformer-based dense unconstrained stereo reconstruction 不需 calibration 的範式，並指出其僅支援 image pair 的限制；後續 MUSt3R、MonST3R、Easi3R 等延伸至 multi-view，但仍受限。VGGT、Fast3r 採 feed-forward Transformer 與 global attention 支援單次 multi-view 推論，計算成本卻過高且無法處理 incremental frame，使其無法 online。在 online 軌跡上，CUT3R 用 recurrent network 維護 memory state、配合 local attention，將 end-to-end 範式延伸至 streaming；MUT3R、Point3R 等同期工作走類似路線。最近的 TTT3R 引入 cross-attention learning rate 與 state reset（從 Test-Time Training 視角），InfiniteVGGT 以 adaptive KV-cache 進一步延伸至長序列。但作者強調，這些更新機制都只依賴 attention 或 feature similarity，未顯式考慮 frame 間的 viewpoint change 幅度——這正是 PAS3R pose-adaptive state modulation 介入的位置。

§2.3 Spatial Geometric Consistency 補充第三條技術線。high-quality 重建除 trajectory 精度外，亦需 dense geometry 的空間一致性與 edge sharpness。end-to-end 方法直接 regress dense point cloud 時，因缺乏顯式 geometric constraint，常在 depth-discontinuous boundary 與 planar surface 出現高頻 artifact。傳統 smoothing（Gaussian、anisotropic diffusion、TV）能降噪但會模糊邊緣；bilateral filtering 系列則能保邊緣，PAS3R 因此引入 online bilateral spatial filtering 作為 §3.3 stabilization module 的空間部分。

三個子節的敘事邏輯共同設定了 PAS3R 的競爭場域：相對 traditional pipeline，主打 constant memory；相對 end-to-end online 方法（CUT3R、TTT3R、IVGGT），主打 explicit pose-aware update；相對於 dense geometry post-processing，主打 lightweight online edge-preserving refinement。三條 contrast line 直接對應後續 §3.1、§3.2、§3.3 三個 method 模組，也預先定義了 §4 比較對象（CUT3R、TTT3R、IVGGT、Mem4D）。

### 3.4 Method (overview narrative)

(330 words)

§3 Approach 以 framework overview 起手，將整體目標明確設為「improving the stability and reconstruction fidelity of online monocular 3D reconstruction over long video sequences」，並把 streaming 範式抽象為「persistent internal state 隨 frame 序貫更新」的問題。作者強調此 paradigm 的成敗繫於「each incoming frame 對 state 的更新強度」這一單一機制，而 PAS3R 的策略是 pose-adaptive state modulation：依 camera motion 與 scene characteristic 動態調整 update intensity。

Fig. 1 將整個 pipeline 視覺化為三條並行軸：（1）image stream 經 encoder 與 memory cross-attention 形成 streaming state；（2）training-time loss 流（3D regression、RGB、pose loss with ATE/RPE/acceleration）；（3）inference-time 的 online spatiotemporal stabilization。Fourier transform 與 learning rate 在圖中明確繪出，呼應 §3.1 中 image structural cue 與 frame importance score 的角色。

§3 的 overview 段落隨即將方法拆為三個子模組，並建立其互補關係：第一，§3.1 Pose-Adaptive State Update Modulation，負責「frame 該以多強的 learning rate 更新 state」的核心問題，輸入為 inter-frame pose variation 與 grayscale image 的 high-frequency component；第二，§3.2 Trajectory-Consistent Model Optimization，負責「即使 update 強度合理，trajectory 仍可能出現不自然 mutation」的補強，做法是引入 ATE、RPE、acceleration 三項 loss 約束 global accuracy、local consistency 與 motion smoothness；第三，§3.3 Online Spatiotemporal Stabilization，負責「即便 training 已加 regularization，inference 仍會殘留 jitter 與 boundary artifact」的後處理，採 One-Euro filter + Slerp 處理 trajectory，並以 bilateral filter 處理 point cloud。

三個模組的職責切分清晰：§3.1 是 input-side 的 adaptive gain，§3.2 是 training-side 的 regularizer，§3.3 是 inference-side 的 lightweight smoother。三者層層加強，使 streaming 重建在 constant memory 下達成 long-horizon stability。Section overview 也明示：所有設計皆需保持 streaming inference 的 efficiency，這成為後續 §4.4 ablation 與 §B.4 GPU/FPS 評估的隱含約束條件。具體公式、參數與算法細節留待 §5 method detail 處理，本節僅建立模組間的功能依賴與整體 information flow。

### 3.5 Experiments (overview narrative)

(440 words)

§4 Experiments 以「long-horizon stability + geometric fidelity」兩條評估主軸開場，明確區分 PAS3R 的評估與傳統 offline 重建之差異：streaming 系統必須隨 frame 進入而 sequential 地更新 state，因此「performance 隨序列長度的演化」與「最終值」同等重要。這個 framing 是後續所有實驗圖表設計的關鍵——多數圖以 frame 數為橫軸繪製 metric 曲線，而非僅報單一最終數值。

實驗設計分為四大子節：§4.1 camera pose estimation、§4.2 depth estimation、§4.3 3D reconstruction、§4.4 ablation study。Baseline 統一為 CUT3R、TTT3R、IVGGT、Mem4D，預處理 pipeline 與 CUT3R/TTT3R 對齊以確保 fair comparison。所有實驗於 8 張 RTX 4090 上執行；作者特別強調 PAS3R 僅引入 lightweight computation 並維持 constant memory，呼應 §2.1 對 traditional pipeline 的批評。

§4.1 在 ScanNet 上以 50–1000 frame 序列評估 ATE/RPE，Fig. 6 顯示主要對手 trajectory error 隨序列增長而 drift，而 PAS3R 增長明顯較緩；Sintel/TUM 短序列則於 Tab. 1 報數，PAS3R 取得最佳 RPE trans 與多項 second-best，rotational RPE 偶有落後但 long-horizon stability 補償。論述支點是「local 精度 < global trajectory consistency」。

§4.2 以 Bonn 為主，搭配 Sintel/KITTI 在三種 alignment（original、scale、scale+shift）下評 Abs Rel 與 $\delta < 1.25$。Fig. 7 顯示一個值得注意的 pattern：PAS3R 在 original 設定即取得最佳，而部分對手必須仰賴 scale alignment 才能挽回誤差，作者將此歸因於 pose-adaptive update 維持了 internal scene representation 的 coherence。Tab. 2 在短序列上展示 PAS3R 與 SOTA 整體 comparable，論證「長序列改進不犧牲短序列性能」。

§4.3 在 7-Scenes 上以 50–400 frame 評估 Acc/Comp/NC。Fig. 8 顯示 baseline 隨序列加長而退化，PAS3R 維持平穩，作者再次以 pose-adaptive update 防止「new frame 過度覆寫」解釋；Fig. 9 提供 Stair/Office/Kitchen 三場景 qualitative 比較，IVGGT/CUT3R/TTT3R 在 wall corner 出現 structural collapse 或 spatial drift，PAS3R 與 GT 對齊較佳。

§4.4 ablation 在 TUM1000、Bonn500、7Scene400 上分別 disable 三個模組。整體 trend 是 pose-adaptive state update 對所有 metric 都有顯著提升、trajectory-consistent training 全面溫和改善、stabilization module 在個別 metric 上略小卻在整體 trajectory 穩定性上不可或缺。三個模組職責互補的論點由此被經驗驗證。

Appendix B 進一步補 TUM 長序列 pose（Fig. 10）、ScanNet trajectory 視覺化（Fig. 11）、KITTI depth（Fig. 12）、NRGBD 短序列重建（Tab. 4、Fig. 13）以及 GPU memory/FPS（Fig. 14），全方位支撐「long-horizon 提升 + short-sequence 競爭力 + constant memory 保證」三點主張。詳細表格分析留待 §6。

### 3.6 Conclusion / Limitations / Future Work

(140 words)

§5 Conclusion 以三句話回顧整篇論文的論證鏈：（1）PAS3R 是針對 streaming monocular 3D reconstruction 設計的 pose-adaptive 框架，核心目標是解決長視訊上的 stability–adaptation dilemma；（2）方法論貢獻是「依 geometric novelty 動態調節 frame 影響力」，使模型既能快速適應新視角，又能保留累積場景結構；（3）trajectory-consistent training 與 lightweight online stabilization 進一步補強，於多個 benchmark 上顯著改善 camera pose、depth、reconstruction 品質，特別於長序列。結語句重申「pose-aware update strategy 對 robust streaming reconstruction 的重要性」這一核心立場。

Limitations 段落僅佔兩句：作者承認當前 benchmark 對「diverse long video stream」的覆蓋仍有限，並坦言 rotational trajectory accuracy 仍有改善空間（呼應 §4.1 中 RPE rot 偶遜於對手的觀察，以及 §B.1 在 TUM 上 RPE rot 略低的事實）。論文未明確列出 future work 段落，但兩項 limitation 已隱含後續方向：擴增更具多樣性的 long-sequence benchmark，以及強化 rotation 精度——可能透過更強的 quaternion-aware loss、rotation-specific regularization，或結合 IMU/event sensor 等附加 modality。整體而言，conclusion 收得相當保守，未過度推銷 generalization 至動態場景或大規模戶外資料的潛力，與全文「在既有 streaming 範式內穩健改進」的定位一致。

## 4. Critical Profile

### 4.1 Highlights

- 提出將 streaming 3D reconstruction 的 fast-weight update 強度顯式拆解為「相機運動量 $s_1 = w_1 \Delta x + w_2 \Delta q$」與「Fourier 高頻佔比導出的影像結構分數 $s_2$」之乘積 $s = s_1 \cdot s_2$,把 TTT3R 隱式於 cross-attention 中的 learning rate 改寫為帶物理意義的條件(p.6–7,Eq. 2–7)。
- 訓練端引入由 ATE、RPE 與 acceleration regularization 構成的軌跡一致性 loss $\mathcal{L}_{pose} = w_a \mathcal{L}_{ATE} + w_r \mathcal{L}_{RPE} + w_s \mathcal{L}_{acc}$,直接懲罰 $\|\Delta^2 \hat{x}_t\|_2$ 與 $\|\Delta^2 \hat{q}_t\|_2$ 來壓制相機軌跡的二階跳變(p.8–9,Eq. 10–13)。
- 推論端搭載 One Euro filter(平移)、Slerp(旋轉四元數)與點雲 bilateral filter 三件套,號稱在不增加記憶體下抑制 high-frequency jitter 與點雲邊界 artifact(p.9–10,Eq. 15–16,p.20–21,Eq. 17–20)。
- 在 ScanNet 1–1000 frames 的長序列評估中,ATE、RPE trans、RPE rot 三項曲線都明顯比 CUT3R、TTT3R、IVGGT 更平緩,顯示誤差累積速率受抑制(p.12,Fig. 6)。
- 在 Sintel 短序列上拿到最佳 RPE trans = 0.053,顯著低於 CUT3R 的 0.071 與 TTT3R 的 0.090;TUM 上 ATE = 0.027、RPE trans = 0.011 為最佳或並列最佳(p.12,Tab. 1)。
- Bonn dataset 在「未對齊」原始尺度設定下 depth 預測即接近 GT,而其他基線需要靠 scale alignment 才追上,間接支持 pose-adaptive update 維持了 internal scene scale 一致性的論點(p.12–13,Fig. 7)。
- KITTI 在 scale-and-shift-aligned 設定下取得最佳 Abs Rel 並在 $\delta < 1.25$ 上達到 91.4,優於 CUT3R 的 87.6 與 TTT3R 的 90.6(p.13,Tab. 2,p.22,Fig. 12)。
- 7-Scenes 1–400 frames 的 dense reconstruction 中,Accuracy 與 Completeness 隨序列長度變化幾乎持平,與基線的單調退化形成對比(p.13,Fig. 8;qualitative 見 Fig. 9)。
- GPU peak memory 在 50–1000 frames 範圍維持在約 4–6 GB,優於 IVGGT 隨長度上升的曲線,符合 streaming constant-memory 訴求(p.24,Fig. 14a)。
- Ablation 顯示移除 pose-adaptive update 會讓 TUM 1000 frames 的 ATE 從 0.052 升到 0.109,是三個元件中最大的單一貢獻(p.15,Tab. 3)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者在 §5 Limitations(p.15)明示「Current benchmarks provide limited coverage of diverse long video streams」,即現有 long-sequence benchmark 的場景多樣性不足,評估上限受限。
- 同段亦承認「rotational trajectory accuracy can be further improved」,對應 Tab. 1 與 Fig. 10 中 RPE rot 在 Sintel(0.688)與 TUM(0.475)落後 IVGGT(0.313)的事實。
- §B(p.21)註明 Mem4D 因 code 未公開,所有 Mem4D 數值皆引用自其原 paper,等於該基線無法在相同 preprocessing 下重跑驗證。
- §B.1(p.21)亦提到因 CUT3R 對 TUM 採間隔取樣,作者「slightly adjusted the time interval parameter of PAS3R」以符合 CUT3R 設定,主文 Tab. 1 的 TUM 結果並非完全 apples-to-apples。

#### 4.2.2 Phyra-inferred

- §3.1 的更新權重 $s_1$ 依賴 $\Delta x, \Delta q$,但這些量本身來自模型自身的姿態預測,而姿態預測又取決於 state 更新強度,形成 bootstrapping 迴圈;論文未說明第 1 幀如何初始化、亦未說明若早期 pose 估計不準是否會放大後續更新失衡。
- Eq. 6 把高頻佔比 $R$ 經 $\sigma(20(R-0.1))$ 映射為 $s_2$,陡度 20 與閾值 0.1、Eq. 4 的高通半徑 $r$ 都是 magic numbers,全文無對其敏感性的 ablation,讀者無從判斷該機制是真正的 frequency cue 還是被 sigmoid 飽和成近常數。
- Tab. 3 中「w/o spatiotemporal stabilization」的 ATE 為 0.04980,反而低於 Full Method 的 0.05214,Acc 也僅差 0.001,作者敘述「slightly improves certain individual metrics but degrades overall trajectory stability」與評估指標恰好就是 trajectory stability 指標,語意上自相矛盾,該模組的實際淨效益缺乏說服力。
- Tab. 4 顯示在 7-Scenes 短序列上 PAS3R 的 Acc/Comp(0.151 / 0.182)劣於 CUT3R(0.120 / 0.156),NRGBD 的 Comp 也輸給 CUT3R 與 TTT3R,主文「remains competitive on short sequences」對 dense reconstruction 而言其實是退步,僅 trajectory metric 才成立。
- Eq. 10 的 ATE 在訓練 loss 中直接比較 $\hat{x}_t / \hat{s}$ 與 $x_t / s$,但 streaming 推論時 trajectory 累積漂移無法用單一 scale 對齊;訓練端用全域 ATE、推論端不對齊,二者 distribution 不一致,可能解釋為何 RPE rot 改善有限。
- Eq. 12 的加速度懲罰 $\|\Delta^2 \hat{x}_t\|_2$ 隱含等時取樣假設,但 TUM 等資料集 timestamp 並非等距,而 §A.2 的 One Euro filter 卻在推論時又顯式以 $t'_{i-1}$ 補回時間間隔,訓練/推論對時間軸的處理不一致。
- §A.2 的 bilateral spatial filter 對每個預測點需在鄰域 $S$ 上做加權平均(Eq. 20),但全文未報告 neighbourhood 大小、$\sigma_s, \sigma_r$,亦未量測該步驟的 latency,使得 Fig. 14b 的 FPS 是否已含此後處理成本不清。
- Baseline 全為 end-to-end pointmap 方法,沒有與 TUM/KITTI 上的成熟 visual SLAM(ORB-SLAM2、DROID-SLAM)做 trajectory 比較,無法判斷 PAS3R 與經典 SLAM 在長序列上的真實差距。
- 訓練資料採 ScanNet++ : Waymo : TartanAir = 5 : 3 : 2,而測試集包含 ScanNet、7-Scenes、Bonn 等室內場景,雖宣稱 no overlap,但 ScanNet++/ScanNet 在場景分佈與感測器特性上高度同源,潛在 distribution leakage 未被討論。

### 4.3 Phyra's Judgment (summary)

PAS3R 真正新穎的部分,是把 streaming 3D reconstruction 的 update intensity 從 attention-implicit 重寫為「pose 量 + 影像頻譜結構」的顯式條件,這個 framing 本身有清楚的物理直覺,且 Fig. 6 的長序列 ATE 曲線給出了實證支持。然而軌跡一致性 loss 與 spatiotemporal stabilization 兩個元件的邊際貢獻在 ablation 中相當薄弱,部分指標甚至與作者敘述衝突,屬於工程性收尾而非核心貢獻。最關鍵的未解問題是:更新權重所依賴的 pose 量本身就是模型輸出,當前形式並未說明為何此 bootstrapping 在強漂移情境下不會失穩,而 dynamic scene 下 pose 微小但幾何劇變的失敗模式也完全未被觸及。

## 5. Methodology Deep Dive

### 5.1 Method Overview

PAS3R 採用串流式線上重建框架,沿用 CUT3R 與 TTT3R 的設計:模型維持一個持久化的記憶狀態 $S_{t-1} \in \mathbb{R}^{n \times c}$,以 cross-attention 與每幀進來的觀測 $X_t$ 互動並更新狀態。從 Test-Time Training 觀點,$S_t$ 可視為 fast weights,其更新依 Eq. (1) 寫成 $S_t = S_{t-1} - \beta\,\nabla(S_{t-1}, X_t)$,其中 $\beta$ 即每幀的學習率。整體推論流程為:輸入 $I_t$ 經 Encoder 抽取 patch token $X_t$,與記憶 $S_{t-1}$ 透過 cross-attention 融合,再交由 Decoder 同時回歸相機姿態 $(\hat{x}_t, \hat{q}_t)$、稠密 pointmap $\hat{I}_p$、depth map 以及 RGB 重建 $\hat{I}_r$;更新後的 $S_t$ 攜帶到下一幀。

PAS3R 的核心修改是在更新項上加入 pose-adaptive 的調控因子。模型不再使用固定 $\beta$ 或僅靠 cross-attention 相似度,而是把 $\beta$ 拆成兩個訊號的乘積:基於相機運動的位移分數 $s_1 = w_1\Delta x + w_2 \Delta q$(Eq. 2,綜合幀間平移與旋轉幅度),以及基於影像結構的品質分數 $s_2$。$s_2$ 由灰階 DFT 後的中心化頻譜 $F(u,v)$(Eq. 3)經高通遮罩 $M(u,v)$(Eq. 4)算出高頻能量比 $R$(Eq. 5),再以陡峭 sigmoid $s_2 = 1/(1+e^{-20(R-0.1)})$(Eq. 6)壓到 $[0,1]$;最終 $s = \mathrm{clip}(s_1 \cdot s_2, 0, 1)$(Eq. 7)即作為當幀的更新權重,使 fast weights 的步長對齊「視點變化幅度 × 影像可用結構量」。

訓練端引入 trajectory-consistent 目標:Pose loss 為 ATE(Eq. 10,絕對軌跡平移與旋轉誤差)、RPE(Eq. 11,相鄰幀相對位姿差)與加速度懲罰(Eq. 12,$\|\Delta^2 \hat{x}_t\|_2 + \|\Delta^2 \hat{q}_t\|_2$)的加權和(Eq. 13);總損失再以 $\lambda_1, \lambda_2, \lambda_3$ 結合 confidence-aware 3D regression loss(Eq. 8)、RGB loss(Eq. 9)與 Pose loss(Eq. 14)。推論時則套用一個輕量的線上時空穩定模組:平移走 One Euro filter(Eq. 15),旋轉以 Slerp 在歸一化後球面內插(Eq. 16),點雲端再以 online bilateral spatial filter 抑制邊界瑕疵與平面冗餘高頻,且不增加額外記憶體佔用。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: streaming frames {I_t}, t = 1..T
   I_t                                              [B, 3, H, W]
     │
     ├──────────────────────────────┐
     │                              │
     ▼                              ▼
  Encoder (per-frame ViT)        Grayscale convert
     │                              │
     ▼                              ▼
  X_t  (patch tokens)            I_gray             [B, 1, H, W]
        [B, N_patches, d]           │
        N_patches = (H/p)(W/p)      ▼
        p, d not specified       2D DFT + center shift
                                    │
                                    ▼
                                 F(u,v)             [B, H, W]
                                    │
                                    ▼
                                 High-pass mask M   [H, W]   (radius r)
                                    │
                                    ▼
                                 R = Σ(F·M) / (ΣF + ε)        [B]
                                    │
                                    ▼
                                 s_2 = sigmoid(20·(R − 0.1))  [B]

  prev pose (Δx, Δq)
        Δx ∈ ℝ_+                     [B]
        Δq ∈ ℝ_+                     [B]
     │
     ▼
  s_1 = w_1·Δx + w_2·Δq               [B]

  s = clip(s_1 · s_2, max=1.0)        [B]    ← used as β_t (fast-weights LR)

  Memory state
     S_{t−1}                          [B, n, c]   (n, c not specified)
     │
     ▼
  Cross-attention(S_{t−1}, X_t)
     ∇(S_{t−1}, X_t)                  [B, n, c]
     │
     ▼
  Update:  S_t = S_{t−1} − s · ∇(S_{t−1}, X_t)
     S_t                              [B, n, c]
     │
     ▼
  Decoder (per-frame)
     ├──→ Camera pose: x̂_t  [B, 3]   (translation)
     │                  q̂_t  [B, 4]   (rotation quaternion)
     ├──→ Pointmap   Î_p     [B, H, W, 3]
     ├──→ Depth      D̂_t    [B, H, W]
     └──→ RGB recon  Î_r     [B, 3, H, W]

[Training only — Trajectory-Consistent Optimization]
     {x̂_t, q̂_t}_{t=1..N}, {x_t, q_t}_{t=1..N}
        ├→ L_ATE  (Eq. 10)            scalar
        ├→ L_RPE  (Eq. 11)  N>1       scalar
        └→ L_acc  (Eq. 12)  N>2       scalar
     L_pose = w_a L_ATE + w_r L_RPE + w_s L_acc
     L      = λ_1 L_conf + λ_2 L_rgb + λ_3 L_pose

[Inference only — Online Spatiotemporal Stabilization]
     x̂_t                              [B, 3]
        └→ One Euro filter (Eq. 15) → x_t (smoothed)   [B, 3]
     q̂_t (normalized)                 [B, 4]
        └→ Slerp(q_{t−1}, q̂_t; α_{t−1}) (Eq. 16) → q_t [B, 4]
     Î_p                               [B, H, W, 3]
        └→ online bilateral spatial filter → Î_p'      [B, H, W, 3]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Frame Encoder

**Function:** 把當前幀 $I_t$ 編成 patch token 序列 $X_t$,作為與 memory 互動的觀測表徵。

**Input:**
- Name: $I_t$
- Shape: `[B, 3, H, W]`
- Source: streaming image input

**Output:**
- Name: $X_t$
- Shape: `[B, N_patches, d]`, `N_patches = (H/p)·(W/p)`,$p$ 與 $d$ 論文未明確說明
- Consumer: cross-attention update module(§5.3.4)

**Processing:**

每幀 $I_t$ 經 patchify 後通過 ViT 風格的 encoder 抽取 token。論文沿用 CUT3R 的串流框架(p.7 Sec. 3.2 註明「Our framework is compatible with streaming reconstruction architectures [13, 69]」),因此 encoder 結構與 CUT3R/TTT3R 一致。

**Key Formulas:**

$$
X_t = \mathrm{Encoder}(I_t)
$$

**Implementation Details:**

論文未揭露 patch size、embedding 維度或具體層數;表 1 與 §4.1 僅指出實驗在 8 張 NVIDIA RTX 4090 GPU 上進行,且預處理與 CUT3R/TTT3R 對齊以保公平比較。

#### 5.3.2 Image Structural Score(Fourier 分支)

**Function:** 以高頻能量比衡量當前幀的結構豐富度,輸出 $s_2$ 抑制弱紋理或近似靜止幀的更新強度。

**Input:**
- Name: $I_t$
- Shape: `[B, 3, H, W]`
- Source: streaming image input

**Output:**
- Name: $s_2$
- Shape: `[B]`,值域 $[0,1]$
- Consumer: total score 合成(§5.3.3 之後)

**Processing:**

先轉灰階 $I_{gray}$,接 2D DFT 並 `shift` 把零頻搬到中心,得到 magnitude spectrum $F(u,v)$(Eq. 3)。以半徑 $r$ 為閾值構造高通 binary mask $M(u,v)$(Eq. 4),計算高頻能量比 $R$(Eq. 5)。最後用斜率 20、中心 0.1 的 sigmoid 把 $R$ 映到 $[0,1]$ 得 $s_2$(Eq. 6)。

**Key Formulas:**

$$
F(u, v) = \mathrm{shift}\big(\|\mathcal{F}\{I_{gray}(x, y)\}\|\big)
$$

$$
M(u, v) = \begin{cases} 1, & u^2 + v^2 > r^2 \\ 0, & \text{otherwise} \end{cases}
$$

$$
R = \frac{\sum_{u,v} F(u,v)\cdot M(u,v)}{\sum_{u,v} F(u,v) + \epsilon},\qquad s_2 = \frac{1}{1 + e^{-20.0\,(R - 0.1)}}
$$

**Implementation Details:**

論文未列出 $r$ 與 $\epsilon$ 的具體數值;sigmoid 的 20 與 0.1 為硬編碼超參(Eq. 6 中明文寫死)。轉灰階是為了「消除色彩資訊對結構特徵的干擾」(p.7)。

#### 5.3.3 Pose Displacement Score

**Function:** 把幀間相機平移與旋轉幅度合成單一位移分數 $s_1$,作為視點變化的物理代理。

**Input:**
- Name: $\Delta x$, $\Delta q$
- Shape: `[B]`(皆為正值)
- Source: 由模型上一步輸出的相機姿態與當前預測差分得到

**Output:**
- Name: $s_1$
- Shape: `[B]`
- Consumer: total score 合成(§5.3.4)

**Processing:**

直接以可學或固定權重 $w_1, w_2$ 線性組合(Eq. 2)。$\Delta x$ 反映相機速度,$\Delta q$ 反映軌跡轉折或旋轉抖動;兩者皆為正值。

**Key Formulas:**

$$
s_1 = w_1\,\Delta x + w_2\,\Delta q
$$

**Implementation Details:**

$w_1, w_2$ 的具體數值與是否可學論文未明確說明,僅稱「respective weights」(p.6–7)。

#### 5.3.4 Pose-Adaptive State Update Modulation

**Function:** 把 $s_1, s_2$ 合成 fast-weights 學習率,並以 cross-attention 梯度更新 memory $S_{t-1} \to S_t$。

**Input:**
- Names: $s_1$、$s_2$、$S_{t-1}$、$X_t$
- Shapes: `[B]`、`[B]`、`[B, n, c]`、`[B, N_patches, d]`(論文僅明確 $S_{t-1} \in \mathbb{R}^{n\times c}$,batch 維度與 $n, c, d$ 之關係未細列)
- Source: §5.3.1–§5.3.3 與上一時刻 memory

**Output:**
- Name: $S_t$
- Shape: `[B, n, c]`
- Consumer: 下一幀的 cross-attention 與本幀 Decoder

**Processing:**

先合成總分 $s = s_1 \cdot s_2$ 並 clip 到上限 1.0(Eq. 7),作為當幀學習率 $\beta$。以 cross-attention 計算梯度函數 $\nabla(S_{t-1}, X_t)$,套入 TTT 形式的更新規則(Eq. 1)。語意上等同於把當幀 KV-cache 編碼到固定長度的 memory 裡,但更新強度受 $s$ 動態調控。

**Key Formulas:**

$$
s = \min\big(s_1 \cdot s_2,\ 1.0\big)
$$

$$
\mathrm{Update}(S_{t-1}, X_t) = S_{t-1} - \beta\,\nabla(S_{t-1}, X_t),\qquad \beta = s
$$

**Implementation Details:**

模型 weights(slow weights)在推論期間凍結,只更新 fast weights $S_t$(p.6)。此模組不改變 cross-attention 結構本身,僅重新分配每幀的更新步長,故與 CUT3R/TTT3R 的串流架構直接相容(p.7)。

#### 5.3.5 Decoder Heads

**Function:** 由更新後的 $S_t$(配合解碼路徑)同時回歸相機姿態、pointmap、depth 與 RGB 重建。

**Input:**
- Name: $S_t$(配合 decoder 內部之 query)
- Shape: `[B, n, c]`
- Source: §5.3.4

**Output:**
- Names / Shapes:
  - Camera pose:$\hat{x}_t$ `[B, 3]`、$\hat{q}_t$ `[B, 4]`
  - Pointmap $\hat{I}_p$:`[B, H, W, 3]`
  - Depth $\hat{D}_t$:`[B, H, W]`
  - RGB $\hat{I}_r$:`[B, 3, H, W]`
- Consumer: 訓練端損失(§5.3.6)、推論端穩定模組(§5.3.7)

**Processing:**

結構沿用 CUT3R 的多頭解碼器:由 memory 解出 pointmap、depth 與 RGB,並回歸 6-DoF 相機姿態(以 quaternion 表示旋轉、3D 向量表示平移)。論文 §3.2 未細述各頭的具體層配置,只說明損失與 CUT3R 一致並新增 Pose-loss。

**Key Formulas:**

論文未為 decoder 列獨立公式;輸出由 §5.3.6 的損失定義間接約束。

**Implementation Details:**

未明示;Fig. 1 顯示三個 decoder 共用同一條 memory 路徑,訓練時同時被 3D regression、RGB 與 Pose 損失監督。

#### 5.3.6 Trajectory-Consistent Training Objectives(訓練專用)

**Function:** 在 fast-weights 局部更新之外,額外以全域與相對姿態誤差、加速度懲罰約束軌跡的時間連貫性。

**Input:**
- Names: $\{\hat{x}_t, \hat{q}_t\}_{t=1..N}$、$\{x_t, q_t\}_{t=1..N}$、$\hat{I}_p$、$\hat{I}_r$ 及對應 ground truth
- Shapes: 姿態為 `[B, N, 3]` / `[B, N, 4]`,影像/點雲為 `[B, H, W, *]`
- Source: §5.3.5 預測 + 資料集 GT

**Output:**
- Name: 純量總損失 $\mathcal{L}$
- Shape: scalar
- Consumer: 反傳更新 slow weights

**Processing:**

ATE 同時懲罰平移距離與旋轉夾角(以 quaternion 內積 $1-|\hat{q}_t \cdot q_t|$ 表示);RPE 比較相鄰幀的差分 $\Delta\hat{x}_t, \Delta\hat{q}_t$;加速度項取二階差分,僅當 $N>2$ 才有定義。三者線性組合得 $\mathcal{L}_{pose}$(Eq. 13),再與 confidence-aware 3D regression loss(Eq. 8,沿用 CUT3R)及 RGB L2 loss(Eq. 9)合成總損失(Eq. 14)。

**Key Formulas:**

$$
\mathcal{L}_{ATE} = \frac{1}{N}\sum_{t=1}^{N}\Big(\big\|\tfrac{\hat{x}_t}{\hat{s}} - \tfrac{x_t}{s}\big\|_2 + (1 - |\hat{q}_t \cdot q_t|)\Big)
$$

$$
\mathcal{L}_{RPE} = \frac{1}{N-1}\sum_{t=2}^{N}\Big(\|\Delta\hat{x}_t - \Delta x_t\|_2 + \|\Delta\hat{q}_t - \Delta q_t\|_2\Big)
$$

$$
\mathcal{L}_{acc} = \frac{1}{N-2}\sum_{t=3}^{N}\Big(\|\Delta^{2}\hat{x}_t\|_2 + \|\Delta^{2}\hat{q}_t\|_2\Big)
$$

$$
\mathcal{L}_{pose} = w_a\,\mathcal{L}_{ATE} + w_r\,\mathcal{L}_{RPE} + w_s\,\mathcal{L}_{acc}
$$

$$
\mathcal{L} = \lambda_1\,\mathcal{L}_{conf} + \lambda_2\,\mathcal{L}_{rgb} + \lambda_3\,\mathcal{L}_{pose}
$$

**Implementation Details:**

論文未公佈 $w_a, w_r, w_s, \lambda_1, \lambda_2, \lambda_3, \alpha$ 等具體權重值,亦未說明訓練時序列長度 $N$ 與 batch 配置;ATE 中的 $\hat{s}, s$ 為預測與 GT 點雲的尺度歸一化係數,與 CUT3R 之 Eq. 8 共用設定。

#### 5.3.7 Online Spatiotemporal Stabilization(推論專用)

**Function:** 在推論期以低成本濾波抑制軌跡高頻抖動與點雲邊界瑕疵,不增加 memory 佔用。

**Input:**
- Names / Shapes: $\hat{x}_t$ `[B, 3]`、$\hat{q}_t$ `[B, 4]`、$\hat{I}_p$ `[B, H, W, 3]`
- Source: §5.3.5

**Output:**
- Names / Shapes: 平滑後 $x_t$ `[B, 3]`、$q_t$ `[B, 4]`、精修後 $\hat{I}_p'$ `[B, H, W, 3]`
- Consumer: 視覺化 / 下游評估指標

**Processing:**

平移端套 One Euro filter(Eq. 15)以平滑因子 $\alpha_{i-2}, \alpha_{i-1}$ 對 $\hat{x}$ 做兩階滑動加權。旋轉端先把 $\hat{q}_i$ 與已平滑的 $q_{i-1}$ 歸一化,再用 Slerp 在 4-D 球面上做時間平滑(Eq. 16)。點雲端則對 $\hat{I}_p$ 套 online bilateral spatial filter,在保留物體輪廓銳利度的同時抑制平面區域的不自然凸起。

**Key Formulas:**

$$
\begin{aligned}
x_{i-1} &= \alpha_{i-2}\,\hat{x}_{i-1} + (1-\alpha_{i-2})\,x_{i-2} \\
x_i     &= \alpha_{i-1}\,\hat{x}_i + (1-\alpha_{i-1})\,x_{i-1}
\end{aligned}
$$

$$
\begin{aligned}
q_{i-1} &= \mathrm{Slerp}(q_{i-2}, \hat{q}_{i-1};\,\alpha_{i-2}) \\
q_i     &= \mathrm{Slerp}(q_{i-1}, \hat{q}_i;\,\alpha_{i-1})
\end{aligned}
$$

**Implementation Details:**

平滑因子 $\alpha$ 的決定方式(One Euro 的 cutoff 與 beta 等)與 bilateral filter 的 spatial / range sigma 論文均未列出,只引用 [11](One Euro)與 [62](bilateral filtering)兩篇方法。整模組強調「lightweight」「不增加 memory consumption」(p.9),屬純後處理,不影響 fast/slow weights。

Section §5 ready. Let me know if you want it tightened, or if §5.3 should be expanded with extra modules (e.g., 將 Encoder + Cross-attention 拆得更細,或把 RGB head 單獨列為一個小節)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| ScanNet++ [79] | Indoor RGB-D 室內場景，用於 fine-tuning | 與 Waymo、TartanAir 以 5:3:2 混合 | train (fine-tuning) |
| Waymo [56] | 戶外駕駛序列，用於 fine-tuning | 與 ScanNet++、TartanAir 以 5:3:2 混合 | train (fine-tuning) |
| TartanAir [71] | 合成多場景 visual SLAM 序列，用於 fine-tuning | 與 ScanNet++、Waymo 以 5:3:2 混合 | train (fine-tuning) |
| ScanNet [15] | Camera pose estimation（長序列） | 每場景取前 50–1000 frames | test |
| Sintel [7] | Camera pose estimation 與 depth estimation（短序列） | 短序列 | test |
| TUM dynamic [54] | Camera pose estimation（短序列與長序列附錄評估） | 主文短序列；附錄為前 50–1000 frames | test |
| Bonn [39] | Depth estimation | 主文 50–500 frames，ablation 用 500 frames | test |
| KITTI [23] | Depth estimation | 主文短序列，附錄 50–500 frames | test |
| 7-Scenes [52] | 3D reconstruction（長/短序列） | 50–400 frames，ablation 用 400 frames | test |
| NRGBD [52] | 3D reconstruction（短序列） | 短序列 | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| ATE | Absolute Trajectory Error，整體軌跡誤差（公尺） | yes |
| RPE trans | Relative Pose Error 之平移分量（公尺） | yes |
| RPE rot | Relative Pose Error 之旋轉分量 | no |
| Abs Rel | Depth 預測之 Absolute Relative Error | yes |
| $\delta < 1.25$ | 預測 depth 落在 ground truth 1.25 倍範圍內之比例 | no |
| Acc | 重建點雲之 Accuracy（誤差，越低越好） | yes |
| Comp | 重建點雲之 Completeness（誤差，越低越好） | yes |
| NC | Normal Consistency（越高越好） | no |
| GPU peak memory | 推論時 GPU 峰值記憶體使用量（GB） | no |
| FPS | 推論吞吐量（frames per second） | no |

### 6.3 Training and Inference Settings

Fine-tuning 採用 Scannet++、Waymo、TartanAir 之 5:3:2 混合資料（附錄 A.1），與所有測試集無重疊。影像解析度為 $512 \times 384$，每個 sample 最多 64 frames。網路以 ViT-Large 之 CUT3R 預訓練權重初始化，使用 AdamW [32] 優化器，初始 learning rate $1\mathrm{e}{-7}$，最大 learning rate $1\mathrm{e}{-6}$，採 linear warm-up 與 cosine decay。訓練於 8 張 RTX 4090 GPU 進行；推論實驗亦於 8 張 RTX 4090 GPU 的伺服器上完成。Batch size 與訓練步數 the paper does not specify。

Online stabilization 模組（附錄 A.2）使用 One Euro filter [11]，平滑因子 $\alpha_{i-1} = \tfrac{2\pi f_{i-1} t'_{i-1}}{2\pi f_{i-1} t'_{i-1} + 1}$，cutoff frequency $f_{i-1} = f_{\min} + \beta \cdot |v_{i-1}|$；$f_{\min}$ 與 $\beta$ 之具體數值 the paper does not specify。Pose-adaptive 模組中 high-pass 半徑 $r$、加權 $w_1, w_2$，以及 total loss 之 $\lambda_1, \lambda_2, \lambda_3$ 與 pose loss 之 $w_a, w_r, w_s$ 數值 the paper does not specify。

Inference 採 streaming 模式：模型維持固定大小的 memory state，對每個 incoming frame 以 cross-attention 增量更新，並透過 pose-adaptive learning rate 與線上 spatiotemporal stabilization 模組產生 camera pose 與 dense point cloud。所有 baseline（CUT3R、TTT3R、IVGGT、Mem4D）使用與 CUT3R/TTT3R 相同之 preprocessing pipeline 以確保公平比較；Mem4D [10] 因尚未開源，數值取自其原論文。

### 6.4 Main Results

Sintel 與 TUM 之 camera pose 比較（Tab. 1，主文）：

| Method | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | TUM ATE ↓ | TUM RPE trans ↓ | TUM RPE rot ↓ |
|---|---|---|---|---|---|---|
| Mem4D [10] | 0.263 | 0.091 | 0.812 | 0.061 | 0.020 | 0.517 |
| CUT3R [69] | 0.209 | 0.071 | 0.632 | 0.047 | 0.015 | 0.448 |
| TTT3R [13] | 0.210 | 0.090 | 0.730 | 0.029 | 0.013 | 0.379 |
| IVGGT [81] | 0.237 | 0.096 | 0.806 | 0.027 | 0.012 | **0.313** |
| **PAS3R (Ours)** | **0.211** | **0.053** | **0.688** | **0.027** | **0.011** | **0.475** |

Sintel、Bonn、KITTI 之 depth 比較（Tab. 2，主文）：

| Method | Sintel Abs Rel ↓ | Sintel $\delta<1.25$ ↑ | Bonn Abs Rel ↓ | Bonn $\delta<1.25$ ↑ | KITTI Abs Rel ↓ | KITTI $\delta<1.25$ ↑ |
|---|---|---|---|---|---|---|
| Mem4D [10] | 0.520 | 43.1 | 0.072 | 95.7 | 0.140 | 82.0 |
| CUT3R [69] | 0.432 | 47.0 | 0.077 | 93.8 | 0.122 | 87.6 |
| TTT3R [13] | 0.406 | 48.8 | 0.069 | 95.4 | 0.114 | 90.6 |
| IVGGT [81] | 0.329 | 66.0 | 0.059 | 97.4 | 0.185 | 69.8 |
| **PAS3R (Ours)** | **0.407** | **48.7** | **0.064** | **96.6** | **0.115** | **91.4** |

7-Scenes 與 NRGBD 之 3D reconstruction 比較（Tab. 4，附錄 B.3）：

| Method | 7-Scenes Acc ↓ | 7-Scenes Comp ↓ | NRGBD Acc ↓ | NRGBD Comp ↓ |
|---|---|---|---|---|
| Mem4D [10] | 0.185 | 0.178 | 0.271 | 0.212 |
| CUT3R [69] | 0.120 | 0.156 | 0.100 | 0.078 |
| TTT3R [13] | 0.156 | 0.196 | 0.105 | 0.080 |
| IVGGT [81] | 0.124 | 0.106 | 0.110 | 0.109 |
| **PAS3R (Ours)** | **0.151** | **0.182** | **0.103** | **0.087** |

Notes：論文真正的主打結論在於長序列的 trajectory 穩定性（Fig. 6 ScanNet 50–1000 frames、Fig. 10 TUM 50–1000 frames），以及長序列 reconstruction 穩定性（Fig. 8 7-Scenes 50–400 frames）。在 Fig. 6 中 PAS3R 之 ATE 與 RPE trans 隨序列長度成長明顯較其他 baseline 緩慢，於 Fig. 10 TUM 長序列亦呈現對 CUT3R/TTT3R/IVGGT 之顯著領先。Bonn depth 在 Fig. 7 之 original setting 下 PAS3R 領先最多，顯示其 geometry 預測在無 post-hoc 對齊下已較一致。

### 6.5 Ablation Studies

Tab. 3（主文）以 TUM 1000 frames、Bonn 500 frames、7-Scenes 400 frames 對三個元件分別移除並評估：

- **w/o pose-adaptive state update**：TUM ATE 由 0.05214 大幅惡化至 0.10854，RPE trans 由 0.00354 升至 0.00374，Acc 由 0.018 升至 0.048。此 ablation 直接驗證 §3.1 之核心元件，是本文最關鍵的 diagnostic experiment，結果支持 pose-adaptive update 為長序列穩定性的主要來源。
- **w/o trajectory-consistent training**：TUM ATE 0.05616、RPE trans 0.00459、RPE rot 0.59215，較 full method 全面退化；7-Scenes Acc 由 0.018 升至 0.023。此 ablation 對應 §3.2 的 ATE/RPE/acceleration loss，是合理的 diagnostic。
- **w/o spatiotemporal stabilization**：TUM ATE 反而較 full method 略佳（0.04980 vs. 0.05214），但 RPE trans 顯著惡化（0.01138 vs. 0.00354），Comp 則打平（0.019 vs. 0.021）。論文承認此模組在某些單一 metric 上會略有平滑代價，但對 RPE trans 與整體穩定性有貢獻。此結果偏向設計取捨之說明，diagnostic 力度較前兩者為弱。

整體而言，三項 ablation 對應 §3.1/§3.2/§3.3 三個 contribution，屬於 component-wise 的 diagnostic 實驗，而非單純 sanity check。但**未進一步拆解 pose-adaptive 內部**（例如僅去除 inter-frame motion 分數 $s_1$ 或僅去除 Fourier 分數 $s_2$、調整 $w_1, w_2$ 或 high-pass 半徑 $r$），亦未對 trajectory-consistent loss 之三個項（ATE/RPE/acceleration）分別 ablate；這些原本可以回答「pose 線索 vs. frequency 線索哪個更重要」「acceleration 約束是否真正必要」等更細的診斷問題，目前付之闕如。Fig. 2、Fig. 3、Fig. 4、Fig. 5 為對應之 qualitative ablation 視覺化。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 同時與 CUT3R、TTT3R、IVGGT、Mem4D 四個近期 online streaming 3D reconstruction baseline 比較，其中 TTT3R 為 ICLR 2026 同期 SoTA。
- [covered] Has cross-task / cross-dataset evaluation — 涵蓋 camera pose（ScanNet/Sintel/TUM）、depth（Sintel/Bonn/KITTI）、3D reconstruction（7-Scenes/NRGBD）三個任務、共七個資料集。
- [partial] Has ablations that diagnose the new components — 三個主元件各有一次 leave-one-out ablation，但未對 pose-adaptive 內部（$s_1$ vs. $s_2$、$w_1, w_2$、$r$）與 pose loss 三項（ATE/RPE/acceleration）做更細的分項拆解，難以判斷各 sub-component 的相對貢獻。
- [covered] Has a scaling study — Fig. 6（ScanNet）、Fig. 7（Bonn）、Fig. 8（7-Scenes）、Fig. 10（TUM）、Fig. 12（KITTI）皆以序列長度（50–1000 或 50–500 frames）為橫軸，是本文最強的 scaling 證據。
- [covered] Has an efficiency / wall-clock comparison — 附錄 B.4 之 Fig. 14 報告 ScanNet 50–1000 frames 之 GPU peak memory（GB）與 FPS，並與 CUT3R/TTT3R/IVGGT 比較。
- [missing] Reports variance / standard deviation / multiple seeds — 全文表格與曲線僅報告單次數值，未提供 std、信賴區間或多 seed 平均；對 0.027 vs. 0.027（TUM ATE）此類接近持平之比較難以判斷統計顯著性。
- [partial] Releases code / weights / data sufficient for reproducibility — Abstract 提供專案頁 https://pas-3r.github.io/PAS3R.io/，附錄 A.1/A.2 給出 fine-tuning 混合比、優化器與部分公式，但 $w_1, w_2, w_a, w_r, w_s, \lambda_{1,2,3}, f_{\min}, \beta, r$ 等超參數與訓練步數均未明確列出，且 weights 是否釋出未說明。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: Pose-adaptive state update modulation 改善長序列穩定性。** 由 Fig. 6(ScanNet)、Fig. 10(TUM)的 ATE/RPE trans 曲線與 Tab. 3 ablation(移除後 TUM ATE 從 0.052→0.109)支持,**結論成立**;但 RPE rot 改善有限(Tab. 1 Sintel 0.688、TUM 0.475 均非最佳),對「rotation 適應性」是部分支持。
- **C2: Trajectory-consistent training 提升 temporal coherence。** Tab. 3 中移除此項時 RPE rot 上升(0.526→0.592),可視為 weak support;但 ATE 在「移除 trajectory-consistent training」與 Full Method 之間僅差 0.004,**屬於部分支持**,主文宣稱「consistent improvements across all metrics」略嫌誇張。
- **C3: Online spatiotemporal stabilization 不增加記憶體即可抑制 jitter 與 artifact。** 視覺上 Fig. 4、Fig. 5 看似有改善,但 Tab. 3 量化指標反而顯示 ATE 與 Acc 在「移除此模組」時更佳,**屬於 overclaimed**,該元件的量化淨效益未被說服性地證明,目前較像「定性 polish」而非「定量提升」。
- **C4: 在維持短序列競爭力的前提下顯著改善長序列。** 對 trajectory metric(Tab. 1、Fig. 6、Fig. 10)成立;但對 dense reconstruction 的短序列指標(Tab. 4: 7-Scenes Acc 0.151 vs CUT3R 0.120),**屬於 overclaimed**,短序列點雲重建實際上退步。
- **C5: 滿足 streaming constant-memory 條件。** 由 Fig. 14a 直接支持,**結論成立**,記憶體曲線確實平坦於 IVGGT。

### 7.2 Fundamental Limitations of the Method

**更新訊號的循環依賴。** PAS3R 的核心邏輯是「以幀間 pose 變化決定當前更新強度」,但這個 $\Delta x, \Delta q$ 來自模型在 $t-1, t$ 兩步上的自身預測。當模型已經因為早期錯誤產生 drift,$\Delta x, \Delta q$ 的尺度也會跟著被污染,進而誤導後續更新權重。論文沒有提供任何外部 pose proxy(如光流、特徵匹配位移),意味著一旦進入失穩區段,系統缺乏自我糾正的閉環訊號,這是 framing 層級而非工程層級的限制。

**Pose 量無法捕捉 dynamic scene novelty。** 整套加權邏輯假設「相機未動 ⇒ 場景未變」,但真實串流場景普遍含有移動物體、光照變化或半透明結構;這些情況下 $s_1 \approx 0$ 會強行壓低更新權重,反而忽略真正的幾何新訊。Fourier 高頻佔比 $s_2$ 雖部分緩解,但只反映影像紋理量,並不對應動態幾何。論文評估也未包含明確 dynamic scene 設定,這項盲區是現行公式無法繞過的。

**訓練 loss 與推論 setting 的 alignment 失配。** Eq. 10 的 ATE loss 假設可在 mini-batch 內以一個全域 scale 對齊整段預測軌跡,但 streaming 推論時根本沒有這個對齊機制;同樣,Eq. 12 的二階差分隱含等時假設,卻在推論時用 One Euro filter 顯式補上 $t'_{i-1}$。訓練/推論的時間-尺度規約不一致,使得 trajectory-consistent loss 的 gradient 對推論軌跡的實際助益被稀釋,對應到 ablation 中該項的邊際貢獻偏弱。

**Spatiotemporal stabilization 的角色不明確。** One Euro filter 與 bilateral filter 都是 hand-crafted 後處理,參數 $f_{\min}, \beta, \sigma_s, \sigma_r$ 全文未報告且未消融;Tab. 3 顯示移除後部分量化指標反而變好。這意味著該模組只是把預測微調到「視覺更平滑」的方向,而非真的修正 systematic error,從方法論看它只是定性 polish 而非結構性貢獻,難以擴展到需要嚴格 metric 改善的下游任務。

### 7.3 Citations Worth Tracking

- **[13] TTT3R(Chen et al., ICLR 2026)** — PAS3R 的直接前作,理解其 cross-attention learning rate 與 state reset 的具體形式,才能準確判斷 PAS3R 在 fast-weight update 上的修改邊界。
- **[69] CUT3R(Wang et al., CVPR 2025)** — recurrent memory + local attention 的串流框架,PAS3R 的 backbone 與 $\mathcal{L}_{conf}, \mathcal{L}_{rgb}$ 沿用其定義,且其 fine-tuned ViT-Large 權重是初始化來源。
- **[57] Sun et al., "Learning to (learn at test time)"(arXiv 2024)** — TTT 把 state 視為 fast weights、模型參數視為 slow weights 的原始 framing,Eq. 1 的 update 形式直接源自此處,讀通它有助於評估 pose-adaptive update 是否仍合於 TTT 假設。
- **[81] InfiniteVGGT (IVGGT)(Yuan et al., arXiv 2026)** — 同期的長序列 streaming 方法,以 adaptive KV-cache 解決相同問題;其在 RPE rot、Bonn depth 等指標上常勝過 PAS3R,是判斷「pose-adaptive vs cache-adaptive」兩種思路差異的關鍵對照。
- **[70] DUSt3R(Wang et al., CVPR 2024)** — feed-forward pointmap reconstruction 的奠基之作,理解整條 CUT3R→TTT3R→PAS3R 路線必先回到此處,特別是 confidence-aware regression loss 的最初定義。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 第 1 幀(無前序 pose)時 $\Delta x, \Delta q$ 如何初始化?是設為 0 從而讓 $s_1 = 0$、還是退化回 TTT3R 的 cross-attention learning rate?論文未明說。
- [ ] Eq. 4 的高通半徑 $r$、Eq. 6 的 sigmoid 陡度 20 與閾值 0.1 是否經過 ablation?換成不同 frequency cue(例如 image gradient norm 或 Laplacian)會掉多少?
- [ ] Eq. 2 中 $w_1, w_2$ 把不同單位(meters 與 quaternion distance)線性相加,具體取值與其對 $s_1$ 飽和的影響在哪裡可以驗證?
- [ ] Tab. 3 中「w/o spatiotemporal stabilization」在 ATE 與 Acc 上反而更佳,那為何 Fig. 4、Fig. 5 的視覺改善與表格量化結果相反?是 metric 不敏感還是 cherry-picked scene?
- [ ] 在含有 dynamic objects 的場景(例如 TUM dynamic 中真正含人移動的子集)PAS3R 是否會因為 $s_1$ 偏小而錯失幾何更新?paper 雖列了 TUM dynamic,但未拆出 dynamic-only subset 的指標。
- [ ] §A.2 的 bilateral filter 在 long sequence point cloud 上的時間複雜度如何?Fig. 14b 的 FPS 是否已包含此後處理?
- [ ] 訓練資料 ScanNet++ : Waymo : TartanAir = 5 : 3 : 2 是否經過 mixing-ratio 掃描?5:3:2 為何優於 1:1:1?

### 8.2 Improvement Directions

1. **以外部 motion proxy 替代自我預測 $\Delta x, \Delta q$(高可行性)**:在 update gating 中改採輕量光流(如 RAFT-tiny)或 ORB 特徵位移作為 motion 訊號,打破 §7.2 提到的循環依賴;邏輯基礎是 motion proxy 不依賴 reconstruction state,因此在系統失穩時仍能提供獨立的更新訊號。
2. **將 $s_1, s_2$ 學習化(中可行性)**:把目前 hand-crafted 的 $s_1 \cdot s_2$ 換成一個小型 MLP 吃 $(\Delta x, \Delta q, R)$,在 trajectory loss 監督下端到端學習;邏輯基礎是現行 magic numbers(Eq. 6 的 20、0.1、Eq. 4 的 $r$)缺乏理論依據,讓監督信號自己挑超參更穩健。
3. **加入 scene-flow / feature-novelty term 處理 dynamic scenes(中可行性)**:把 $s_1$ 擴展為 $w_1 \Delta x + w_2 \Delta q + w_3 \cdot \text{novelty}_{feat}$,其中 novelty 項衡量當前 KV 與 memory 的特徵殘差;邏輯基礎是 §7.2 指出單靠 pose 量無法捕捉 camera 不動但場景變動的情況,此項直接補上盲區。
4. **訓練端改為 windowed ATE(中可行性)**:把 Eq. 10 的全段 ATE 換成滑動視窗(例如 16-frame)內的對齊誤差,使訓練 loss 與 streaming 推論的可達 alignment 範圍一致;邏輯基礎是現行 loss 假設可在訓練樣本內全域對齊,但推論時根本不存在這個對齊機制,windowed 版本可消除此 distribution mismatch。
5. **量化評估 stabilization 的真實淨效益(低成本但需重做實驗)**:報告含與不含 One Euro / bilateral 的 FPS、latency、以及在 dynamic 與 high-jitter benchmark 上的指標差;邏輯基礎是 Tab. 3 已暴露此模組量化收益不明,需要更細的拆解才能判斷它是否值得保留。
6. **加入經典 SLAM baseline 對照(可行,僅缺實驗)**:在 TUM、KITTI 上補跑 ORB-SLAM2、DROID-SLAM 的 trajectory 指標,讓「streaming pointmap 比經典 SLAM 強多少」這個關鍵問題有據可循;邏輯基礎是現行 baselines 全為同質 end-to-end pointmap,無法定位 PAS3R 在 SLAM 文獻全景中的真實位置。
