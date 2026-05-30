<!-- type: paper-read-notes | generated: 2026-05-08 | lang: zh-TW -->

# SLAM3R — SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | SLAM3R |
| Paper full title | SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos |
| arXiv ID | 2412.09401 |
| Release date | 2025-03-23 |
| Conference/Journal | CVPR 2025 (Highlight) |
| Paper link (abs) | https://arxiv.org/abs/2412.09401 |
| PDF link | https://arxiv.org/pdf/2412.09401 |
| Code link | https://github.com/PKU-VCL-3DV/SLAM3R |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Yuzheng Liu | Peking University | https://ly-kc.github.io/ | joint first author |
| Siyan Dong | The University of Hong Kong | https://datascience.hku.hk/dr-dong-siyan/ | joint first author, corresponding |
| Shuzhe Wang | Aalto University | https://ffrivera0.github.io/ | co-author |
| Yingda Yin | Peking University | https://yd-yin.github.io/ | co-author |
| Yanchao Yang | The University of Hong Kong | https://yanchaoyang.github.io/ | corresponding |
| Qingnan Fan | VIVO | https://fqnchina.github.io/ | co-author |
| Baoquan Chen | Peking University | https://baoquanchen.info/ | corresponding |

### 1.2 Keywords

dense 3D reconstruction, monocular SLAM, RGB video, pointmap regression, feed-forward 3D, DUSt3R extension, sliding window, incremental registration, real-time

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| DUSt3R (Wang et al., 2024) | base model | Provides the end-to-end two-view pointmap regression backbone that I2P/L2W extend to multi-view and incremental settings. |
| Spann3R (Wang et al., 2024) | concurrent | Concurrent DUSt3R extension to video via spatial memory; SLAM3R contrasts it as drift-prone frame-by-frame baseline. |
| MASt3R (Leroy et al., 2024) | influence | Adds a match head to DUSt3R; cited as related end-to-end variant and used as reconstruction baseline. |
| DROID-SLAM (Teed & Deng, 2021) | baseline | Recurrent dense SLAM baseline compared on Replica/7 Scenes for accuracy and FPS. |
| NICER-SLAM (Zhu et al., 2024) | baseline | Monocular neural-implicit dense SLAM cited as the canonical sub-1-FPS RGB SLAM SLAM3R aims to surpass. |
| GO-SLAM (Zhang et al., 2023) | baseline | Monocular dense SLAM at ~8 FPS used to motivate real-time gap; compared on Replica. |
| DIM-SLAM (Li et al., 2023) | baseline | Monocular dense neural SLAM compared on Replica to demonstrate accuracy/completeness gains. |

## 2. Research Overview

### 2.1 Research Topic

本文聚焦於從單目 RGB 影片進行即時稠密 3D 場景重建。傳統作法將 SfM/SLAM 與 MVS 串接，需離線最佳化相機參數；近期 monocular dense SLAM 雖能產出完整幾何，卻普遍低於 1 FPS。DUSt3R 等 end-to-end pointmap regression 方法雖在雙視圖上展現高品質，但延伸至多視圖須仰賴昂貴的 global alignment，犧牲速度；concurrent 的 Spann3R 雖以 spatial memory 加速，卻有累積漂移問題。SLAM3R 主張完全省略相機參數估計，以 feed-forward 神經網路在 sliding-window 內直接回歸 local pointmap，再以另一個 feed-forward 模組將其 incrementally 對齊到全域座標系，目標同時兼顧重建準確度、完整度與 20+ FPS 的真即時效能。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- SLAM
- Deep Learning

### 2.3 Core Architectures Used

- **Image-to-Points (I2P) network**：本文提出的 inner-window 模組，以 multi-branch ViT 對一個 keyframe 與 $L-1$ 個 supporting frame 做 multi-view cross-attention 並 max-pool 聚合，於 sliding window 內直接回歸 local pointmap。
- **Local-to-World (L2W) network**：本文提出的 inter-window 模組，沿用與 I2P 對稱的 decoder 架構，將新 keyframe 的 local pointmap 直接 feed-forward 對齊到世界座標系，無需顯式相機參數最佳化。
- **Self-contained retrieval module**：本文提出，重用 I2P 前 $r$ 個 decoder block 加上 linear projection 與 average pooling，從 reservoir 中挑選 top-$K$ 與當前 keyframe 最相關的 scene frame 作為全域參考。
- **Reservoir sampling buffer**：沿用自 Vitter 的 reservoir 抽樣策略，於有界記憶體內維持一組無偏的歷史 scene frames，使系統能擴展至長影片。
- **Multi-branch Vision Transformer (ViT) backbone**：作為 I2P 與 L2W 的編解碼骨幹，由 $m$ 個 encoder block 與 $n$ 個 decoder block 組成；權重由 DUSt3R 預訓練模型 (224×224、$m=24$、$n=12$) 初始化。
- **DUSt3R pointmap regression head**：沿用 DUSt3R 的 linear head，從 decoded tokens 同時回歸 dense 3D pointmap $\hat{X}_i$ 與 confidence map $\hat{C}_i$。
- **PnP-RANSAC pose solver (OpenCV)**：作為下游工具，於評估時從預測的 scene points 與 ground-truth intrinsics 反推相機姿態以計算 ATE-RMSE。

### 2.4 Core Argument

作者主張現有 monocular dense SLAM 之所以難以同時達到準確、完整與即時，是因為它們仍受限於「先解相機姿態、再估場景表示」的交替最佳化框架；而即便最新的 end-to-end DUSt3R 在多視圖時也必須對成對影像做 global alignment，使得計算量隨幀數爆炸，實質失去 real-time 能力。Spann3R 雖以記憶體 token 串連單幀並避開全域最佳化，但純粹的 frame-by-frame 累積導致漂移與品質崩潰。作者由此推論：若希望兼顧效率與品質，必須一次處理多幀以攤平誤差，並把「對齊到世界座標」也設計成一個 feed-forward 預測，徹底跳脫顯式的相機參數最佳化迴路。據此提出兩階層架構：Image-to-Points (I2P) 在每個 sliding window 內以多分支 ViT 對 keyframe 與多個 supporting frame 做 multi-view cross-attention 並 max-pool 聚合，將 DUSt3R 推廣到任意視圖數，產生較單純逐對推論更穩定的 local pointmap；Local-to-World (L2W) 以對稱的 decoder 架構直接回歸 keyframe 在世界座標下的 pointmap，並透過 reservoir sampling 的 scene-frame buffer 與自洽的 retrieval 模組挑出長期歷史中最相關的參考幀，使新窗口能對齊到全域而非僅鄰近幀。此設計在邏輯上同時消除了相機參數最佳化、二視圖 pairing 爆炸與短期記憶漂移三項瓶頸，因此能在 20+ FPS 下達到準確且完整的稠密重建。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(140 words)

Title 與 Abstract 共同建立了論文的核心定位:SLAM3R 是一個以 monocular RGB video 為輸入、能即時 (real-time) 產生 dense 3D reconstruction 的系統。Title 中的「SLAM3R」此命名本身就暗示了論文對傳統 SLAM 範式的重新詮釋——作者在第 2 頁明確指出 3R 代表 3D Reconstruction,而非 Localization,顯示其重心是 mapping 而非 pose estimation。

Abstract 以三個遞進主張組織論述:第一,系統提供 end-to-end 解法,透過 feed-forward neural networks 同時整合 local 3D reconstruction 與 global coordinate registration;第二,引入 sliding window 機制將 video 切成 overlapping clips,直接從 RGB images regress 出 3D pointmaps,並 progressively align 與 deform 這些 local pointmaps;第三,強調此流程「without explicitly solving any camera parameters」,刻意凸顯與傳統 pose-optimization-based SLAM 的差異。

最後以實驗結果結尾:在多個 datasets 上達到 state-of-the-art reconstruction accuracy 與 completeness,同時維持 20+ FPS 的 real-time 效能。Abstract 亦附上 GitHub 連結,顯示作者意圖讓社群可重現結果。整體而言,Abstract 為讀者鎖定了「品質 vs. 效率 trade-off」這個論文要解決的核心張力,並承諾兩者兼得,直接為 §1 Introduction 鋪陳「現有方法在 accuracy/completeness/efficiency 三者中至少缺一」的問題框架。

### 3.2 Introduction

(720 words)

Introduction 的論述分為四個層次,層層收斂到 SLAM3R 的設計動機。

第一層,作者回顧 dense 3D reconstruction 的 traditional multi-stage pipeline:先以 sparse SLAM 或 SfM 估計 camera parameters,再以 MVS 補上 scene details。雖然品質高,但需要 offline processing,限制了即時應用。

第二層,聚焦 dense SLAM 系統:作者承認此類系統將問題視為一個完整的 system 來解,但指出它們「fall short in reconstruction accuracy or completeness, or rely heavily on depth sensors」。接著轉向近期的 monocular dense SLAM 系統(如 NICER-SLAM、GO-SLAM),指出這些方法雖然引入 advanced scene representations 達到 accuracy 與 completeness,卻以 efficiency 為代價——NICER-SLAM 速度遠低於 1 FPS。作者由此歸納出論文要挑戰的「三難困境」:accuracy、completeness、efficiency,目前方法至少缺一。

第三層,引入 two-view geometry 的近期突破作為靈感來源。DUSt3R 是 purely end-to-end 學習 dense reconstruction 的代表,在大規模資料訓練下能 real-time 產生高品質 paired-image 重建,但延伸到 multiple views 時需要 global optimization step,效率大幅下降。同期工作 Spann3R 雖以 spatial memory 加速,卻產生明顯 accumulated drift 與品質下降。這兩個 baselines 的限制,精準定義了 SLAM3R 必須超越的對手。

第四層,正式介紹 SLAM3R 的設計。作者強調 SLAM3R 進行的是 implicit camera localization,重心是 dense scene mapping。系統採用 two-hierarchy framework:先以 sliding window 處理短 clips 重建 local 3D geometry,再 progressively register 至 globally consistent 3D scene。兩個模組分別是 Image-to-Points (I2P) network 與 Local-to-World (L2W) network,皆以 feed-forward models 實作以維持效率。I2P 受 DUSt3R 啟發,選一個 keyframe 作為 local coordinate reference 並預測 dense 3D point map;L2W 則 incrementally 將 local reconstructions fuse 至 coherent global coordinate system。最關鍵的設計宣示是「without explicitly estimating any camera parameters」,這既是技術選擇也是哲學立場。

最後段以四個 bullet points 列出 contributions:(1) novel real-time end-to-end dense 3D reconstruction system;(2) I2P module 能同時處理任意數量影像,將 DUSt3R 從 two-view 擴展至 multi-view;(3) L2W module 直接 align local pointmaps 至 unified global coordinate system,免除 explicit camera parameter estimation 與 costly global optimization;(4) 在 multiple public benchmarks 上達 state-of-the-art。

Introduction 的敘事邏輯非常清晰:從 traditional → dense SLAM → monocular dense SLAM → end-to-end two-view 方法,逐步排除既有路徑,最後讓 SLAM3R 的「two-hierarchy feed-forward + no explicit camera parameters」設計成為唯一同時滿足三難的解。這也為 §2 Related Work 的詳細回顧與 §3 Method 的架構展開做好鋪陳——讀者進入下一節時,已能預期 SLAM3R 將如何「組裝」這些線索。

### 3.3 Related Work / Preliminaries

(710 words)

§2 Related Work 將文獻分為三大類,每一類都對應到 §1 鋪陳的某個 baseline 群,並在敘事中明確標示 SLAM3R 相對該群的差異化。

第一類「Traditional offline approaches」回顧 SfM + MVS 的經典 pipeline,並涵蓋近年以 neural implicit 與 3D Gaussian representations 增強重建品質的工作。作者強調這類方法的根本限制是 offline processing,並以此一句話將自己定位至 online dense reconstruction in SLAM 的脈絡——形同將 §3 之後的所有討論都鎖定在 real-time 條件下。

第二類「Dense SLAM」是 §2 最重要的一塊。作者先區分 early sparse SLAM 與 dense SLAM:後者納入詳細幾何資訊以改善 pose estimation,代表作如 DROID-SLAM 與 TANDEM。但作者立刻指出這些系統「focus on camera trajectory accuracy often results in incomplete and noisy 3D reconstruction」,這是一個重要的價值判斷——SLAM3R 願意犧牲 trajectory 品質換取 reconstruction 品質,§4.1 的實驗結果(Table 3 顯示 pose 與 reconstruction 並非正相關)就是此判斷的辯護。接著回顧整合 neural implicit 與 Gaussian representations 的 SLAM 系統,但批評它們「rely on additional depth sensors or focus primarily on novel view synthesis rather than producing detailed geometric reconstruction」。最後談到 monocular dense SLAM 系統的共同弱點:速度慢(GO-SLAM 僅 ~8 FPS)以及「alternate between solving for camera poses and estimating the scene representation」的範式。SLAM3R 在此被定位為 paradigm shift——「eliminates the need for explicitly solving camera parameters」。

第三類「End-to-end dense 3D reconstruction」直接面對 SLAM3R 最近的對手。作者首先把 DUSt3R 描繪為這條路線的開山之作,並指出它已啟發 single-view reconstruction、feature matching、novel view synthesis、dynamics reconstruction 等延伸工作,從而確立 end-to-end dense point prediction 的有效性。接著對 DUSt3R 自身限制做出精準批評:two-view 即時,但 multi-view 需 exhaustive pairing 加 global optimization,效能大幅下滑。MASt3R 雖以 match head 提升 keypoint correspondences 品質,卻又增加運算成本。

最後,作者用一整段對比 Spann3R——這是 §1 已暗示的「最近也最直接的對手」。Spann3R 以 spatial memory 擴展 DUSt3R 至 video,並以 unified coordinate system 進行 incremental reconstruction,規避 global optimization,但 frame-by-frame 的設計導致 accumulated drift。SLAM3R 在這裡明確差異化兩點:(1) 每個 hierarchy 的 network 都吃 multiple frames 而非單張,以壓低 drift;(2) 提出 self-contained retrieval module,在 register 新 frame 時不只看前幾張,還能從 long-term history 中選出相似 frames 作為 global scene reference。

這段論述策略性極強:作者刻意把 Spann3R 留到最後處理,因為它是 SLAM3R 最容易被混淆、也最需要明確切割的 concurrent work。透過「multi-frame input + retrieval module」這兩個具體技術差異,SLAM3R 為自己保留了清晰的方法學身分。整體 Related Work 的鋪陳,也讓 §3 Method 中 I2P 的「multi-view cross-attention」與 L2W 的「retrieval-based scene frame selection」兩項設計能直接對應到上述每一類批評,使方法選擇顯得既必要又合理。

### 3.4 Method (overview narrative)

(360 words)

§3 Method 以 problem statement 開場,將任務形式化為:給定 monocular RGB sequence $\{I_i \in \mathbb{R}^{H \times W \times 3}\}_{i=1}^{N}$,輸出 dense 3D pointcloud $P \in \mathbb{R}^{M \times 3}$,並明確列出三個目標——maximizing point recovery (completeness)、improving per-point accuracy、preserving real-time performance。這三個目標直接對應 §1 提出的三難困境,讓讀者能持續以同一組 criteria 檢視後續設計。

接著 system overview 揭示 two-hierarchy framework 的整體運作。系統先以 length-$L$ 的 sliding window 將 video 切為 overlapping clips $\{W_i \in \mathbb{R}^{L \times H \times W \times 3}\}$,預設 stride 為 1,確保每張 frame 至少被選為 keyframe 一次。Image-to-Points (I2P) network 處理每個 window,在 window 內選一張 keyframe 定義 local coordinate system,並 regress 該 window 中所有 frames 的 3D pointmaps。Local-to-World (L2W) network 則接手 incremental global registration:用第一個 window 初始化 world coordinate,之後將 I2P 產出的 (image, local pointmap) 對作為輸入,把後續 reconstructions 一一融入 unified global 3D coordinate system。

為了在長 video 上維持效率與準確性,L2W 維護一個有上限的 scene frames 緩衝集合;每當 register 新 keyframe,系統會從緩衝集合中 retrieve 最相關的 scene frames 作為 reference。這個設計同時回應了 §2 對 Spann3R「frame-by-frame 導致 drift」的批評,以及對 DUSt3R「multi-view 需 costly global optimization」的批評——SLAM3R 既不做 global BA,也不只看相鄰 frames。

Method 在敘事節奏上刻意分兩節展開細節:§3.1 Inner-Window Local Reconstruction 處理 I2P 的 multi-branch ViT 架構、shared encoder、keyframe decoder 中的 multi-view cross-attention、supporting decoder、point regression head 與 confidence-aware loss;§3.2 Inter-Window Global Registration 處理 L2W 的 scene initialization (對 first window 做 $L$-way 全枚舉取最高 confidence)、reservoir sampling 維持有界記憶體、retrieval module、points embedding(將 3D pointmaps 以 patch embedding 注入 visual tokens)、registration decoder、scene decoder 與 loss。

Method 的整體鋪陳邏輯是:先說「two-hierarchy + feed-forward + no explicit camera」是骨架,再分別論證每個模組如何透過 minimal 但 effective 的修改擴展 DUSt3R,確保 §4 Experiments 能直接驗證每個設計選擇的貢獻——這是 §4.2 ablation studies 的伏筆。

### 3.5 Experiments (overview narrative)

(680 words)

§4 Experiments 以「Datasets」與「Implementation details」開場,為後續所有量化結果建立可信度與可重現性基礎。訓練資料採 ScanNet++、Aria Synthetic Environments、CO3D-v2 三個 dataset 的混合,涵蓋 scene-level 與 object-centric、real-world 與 synthetic 的多樣性,共抽取約 850K 個 video clips。評測則刻意選擇兩個 unseen datasets——7 Scenes(real-world、partial scenes)與 Replica(synthetic、complete scenes)——以驗證泛化能力。Implementation 上強調 I2P 與 L2W 都繼承 DUSt3R pre-trained weights、所有影像 center-crop 至 $224 \times 224$、使用 8 張 NVIDIA 4090D 訓練約一天;測試時 initial window length $L=5$、後續 incremental windows $L=11$。

§4.1 Comparisons 圍繞三個維度展開:reconstruction quality、camera pose、generalization。Evaluation metrics 採 NICER-SLAM 與 Spann3R 的設定:以 ground-truth depth 與 camera 反投影建立 GT pointcloud,用 Umeyama + ICP 對齊後計算 accuracy 與 completeness,並以 FPS 衡量效率、ATE-RMSE 衡量 pose。

論述策略上,作者讓 SLAM3R 同時以兩種 setting 出現:SLAM3R-NoConf(整合所有預測點)與 SLAM3R(以 confidence threshold 3 過濾)。在 7 Scenes 上 (Table 1) 同時打敗 optimization-based 的 DUSt3R/MASt3R 與 incremental 的 Spann3R,並在 average accuracy 與 completeness 同時領先,FPS 維持 ~25。在 Replica 上 (Table 2) 進一步加入 SLAM-based 對手 NICER-SLAM、DROID-SLAM、DIM-SLAM、GO-SLAM,結果顯示 SLAM3R 在 FPS > 1 的所有方法中最佳,且品質可比 offline optimization-based 方法。視覺結果以 Office-09 與 Office 2 (Figure 4) 證明 drift 顯著低於 Spann3R。

Camera pose 結果 (Table 3) 是論文敘事中刻意安排的「反直覺亮點」:以 PnP-RANSAC 從預測 pointmaps 反算 pose,SLAM3R 的 pose 並不領先,但作者以「pose 與 reconstruction error 並非正相關」這個觀察反過來支持其核心主張——effective end-to-end 3D reconstruction 不需先有精確 camera poses。這個論點與 §1 的設計哲學首尾呼應。

§4.2 Analyses 採 ablation 形式驗證每個設計選擇的價值。Effectiveness of the I2P model (Table 4) 顯示 reconstruction quality 隨 supporting views 增加而提升,且 efficiency 直到 window size 超過 11 才顯著下降,既證明 multi-view cross-attention 的有效性,也合理化「default window size = 11」的選擇。Advantages of the L2W model (Table 5) 將 local points 對齊方式換成 DUSt3R 的 global alignment (I2P+GA)、Umeyama+ICP (I2P+UI)、L2W without retrieval (I2P+L2W),最後與完整方法 (I2P+L2W+Re) 對比;結果顯示完整方法在 alignment accuracy 與 efficiency 上同時勝出。Analysis of the retrieval module 則以「最近 10 frames」為 baseline,證明 retrieval 提供的 implicit re-localization 能力顯著改善表現。

最後 In-the-wild scene reconstruction 透過 Tanks and Temples、BlendedMVS、Map-free Reloc、LLFF、ETH3D 與自拍 video (Figure 5) 展示 generalization。Supplementary 補充更多 quantitative 結果(Table 8 in ScanNet/Tanks/ETH3D)、scene frame 數量分析 (Table 9)、incremental reconstruction 視覺化 (Figure 7) 與 DTU dataset 結果 (Figure 8)。整體 Experiments 的論證鏈條極為完整:從主要 benchmark 比較,到對手中無法超越的 pose 弱點的轉化解釋,再到逐模組 ablation,最後以 generalization 收尾,層層回答 §3 Method 中每個設計選擇的必要性。

### 3.6 Conclusion / Limitations / Future Work

(155 words)

§5 Conclusion 以一段精簡的回顧總結 SLAM3R 的核心貢獻:novel and effective system、real-time、high-quality、dense 3D scene reconstruction、RGB videos 為輸入。作者再次強調 two-hierarchy neural network framework 與 streamlined feed-forward processes 兩項架構特徵,並重申「eliminating the need to explicitly solve any camera parameters」這項貫穿全文的設計哲學。實驗成就以「state-of-the-art reconstruction quality and real-time efficiency (20+ FPS)」一句帶過,呼應 §1 Introduction 設定的「accuracy + completeness + efficiency 三者兼得」目標。

Limitations and future work 段落極度簡短卻誠實,點出兩個直接源自設計選擇的代價:(1) 由於不預測 camera parameters,系統無法執行 global bundle adjustment——這正是 §3 與 §4 中「no explicit camera」的反面後果;(2) 從 scene point cloud 反推的 poses 仍不及專注於 camera localization 的 SLAM 系統,此點與 §4.1 Table 3 的結果一致。作者明確將上述兩項列為未來工作焦點,既守住論文的 scope,也為後續研究方向預留接口,結尾克制而不過度承諾。

## 4. Critical Profile

### 4.1 Highlights

- 在 Replica 上達到 3.57 / 2.62 cm 的平均 accuracy / completeness，同時維持 ~24 FPS，較 concurrent 的 Spann3R 之 10.32 / 13.33 cm 有顯著差距（Table 2）。
- 在 7 Scenes 上以 ~25 FPS 達 2.13 / 2.34 cm，於即時類別中全面領先 Spann3R 的 3.42 / 2.41 cm，且 accuracy 已逼近離線 DUSt3R 的 2.19 / 3.24 cm（Table 1）。
- 將 DUSt3R 的雙視圖 cross-attention 廣義化為 multi-view + max-pool 聚合，使 I2P 在 $L=11$ 時取得 2.38 / 2.03 cm，明顯優於兩視圖版本的 3.39 / 3.04 cm（Table 4）。
- 提出的 L2W + retrieval 取代 DUSt3R 的 global alignment，在 Replica 上同時拿下更佳的 3.62 / 2.70 cm 與 ~43 FPS 對齊速度，較 I2P+GA 的 4.87 / 3.00 cm @ ~3 FPS 提升一個量級（Table 5）。
- Reservoir sampling 維護有界的 scene-frame buffer，配合自洽的 retrieval module 取代鄰近幀策略，將 Replica accuracy 從 6.19 cm 改善至 3.62 cm（Table 5）。
- I2P 與 L2W 共用 ViT decoder 架構並可從 DUSt3R 224×224 權重初始化，整體模型在 8 張 4090D 上一天內即可訓練完成（page 7、page 9）。
- Scene initialization 透過將窗口內每張 frame 都試作為 keyframe、再選 confidence 最高者，提升首窗的全域座標基準品質（page 5）。
- 在 Tanks and Temples、BlendedMVS、Map-free Reloc、LLFF、ETH3D、DTU 與 in-the-wild 影片上展現可觀的 zero-shot 重建能力（Figure 5、Figure 8、Table 8）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 由於不顯式估計相機參數，系統無法進行 global bundle adjustment（page 8 Conclusion）。
- 由 scene point 反推的 camera pose 仍明顯落後於專注於定位的 SLAM 系統（page 8 Conclusion）。
- 隨著 window length 增大，重建品質先升後降，因為過長窗口會導致 frame 間 overlap 降低，且推論時間顯著上升（page 12、Figure 9）。
- 取太少或太多的 scene frame 都會傷害 registration：太少會卡在 local minima，太多則引入無關幀作為雜訊（page 12、Table 9）。

#### 4.2.2 Phyra-inferred

- 在 Replica 上 SLAM3R 的 ATE-RMSE 為 6.61 cm，而 DROID-SLAM 為 0.33 cm（Table 7），相差約 20 倍；論文將此差距重新框成「end-to-end 重建可在不解 pose 的情況下達成」，但實際上代表此系統在任何需要可用軌跡的下游應用（重定位、SfM 後處理、感測器融合）皆不可直接替代傳統 SLAM。
- 整個 pipeline 鎖定在 224×224 解析度（page 7「All images are center-cropped to $224 \times 224$」），與 modern dense MVS / SLAM 相比明顯偏低，幾何細節與遠景小結構必然受架構上限限制；且 MASt3R baseline 是在 512×384 / 512×288 上跑（page 11），二者並未在同一解析度下對比，重建品質差異有部分來自輸入尺寸而非方法本身。
- 7 Scenes 的測試協議是「每 20 幀取一幀」（page 7），亦即每段序列只剩約十幾到幾十個 keyframe，這個取樣率刻意降低 drift 累積壓力；論文沒有在原生 frame rate 下回報長序列的 drift 曲線。
- 系統缺少形式化的 loop closure 機制，retrieval module 透過 correlation score 提供「軟性 re-localization」，但既無 pose graph，也無一致性約束；長閉合迴圈的全域一致性僅依賴 retrieval 是否恰好命中歷史幀。
- 問題定義硬編碼為「captures a static scene」（page 3），整篇實驗無一條測試動態場景，但作為通用 monocular reconstruction 系統，這個假設於室外或人物場景會直接失效，論文未討論此邊界。
- 多個關鍵超參數（window $L$、retrieved $K$、buffer $B$、co-registration $C_o$、update interval $R$、$\text{Skip}$）皆是「per-dataset 調過」（page 11 Sec. B），而 ablation 只覆蓋 $L$ 與 $K$，其餘參數的敏感度與長片段延展性沒有被檢驗。

### 4.3 Phyra's Judgment (summary)

真正新的貢獻是把「local-to-world 對齊」也轉成 feed-forward 預測——L2W + retrieval 在 Replica 同時拿下更高品質與一個量級的速度提升，這是脫離 DUSt3R 全域最佳化框架的實質突破；I2P 的 multi-view max-pool 也是合理且能提供一致量化增益的廣義化。其餘成分（reservoir sampling、sliding window、confidence threshold、scene initialization）屬於 engineering-only。最關鍵的未解問題是：在不顯式建立 pose 表示的前提下，這條路線能否同時做到 SLAM 級的軌跡精度與 dense MVS 級的幾何細節，目前 ATE 與 224×224 解析度兩端都顯示尚有結構性天花板。

## 5. Methodology Deep Dive

### 5.1 Method Overview

SLAM3R 將單目 RGB 影片的稠密重建問題，重新表述為「**從影像窗格直接迴歸點圖（pointmap）**」的端到端任務，並以兩個層級的前饋網路完成：Image-to-Points (I2P) 將短窗格內 $L$ 幀影像對齊到同一個區域座標系下的點圖，Local-to-World (L2W) 再把這些區域點圖逐步合併到全域座標系。整體繼承 DUSt3R 的多分支 ViT 設計，但取消了測試期的全域點雲對齊優化，改以前饋推論直接輸出對齊結果，因此可以做到 20+ FPS 的即時推論（paper §1, §3）。

I2P 的核心是一支共享權重的 image encoder $E_{img}$，加上兩支不對稱的 multi-view decoder：keyframe decoder $D_{key}$ 處理窗格中央的關鍵幀，supporting decoder $D_{sup}$ 處理其餘支援幀。兩支 decoder 在每一層透過 cross-attention 互相交換資訊，並對所有支援幀的 token 做 max-pooling 聚合，使 keyframe 的點圖能整合多視角線索而不會隨 $L$ 改變網路結構（paper §3.1, Fig. 2）。L2W 則新增一支 points encoder $E_{pts}$，把已註冊到世界座標的點圖編成 token，並由 registration decoder $D_{reg}$ 與 scene decoder $D_{sce}$ 互相做 cross-attention，把目前窗格的區域點圖搬到世界座標系下；此處的 retrieval 模組會重用 $D_{reg}$ 的前 $r=2$ 個 block 計算 keyframe 與 reservoir 中歷史 keyframe 的相似度，挑出最有重疊的 $K$ 幀作為「scene context」（paper §3.2, §3.3）。

訓練時兩個子網路分別最小化 confidence-aware 點圖回歸損失：I2P 因為輸出是區域座標、尺度不確定，loss 會用點到相機原點距離 $z$ 做尺度歸一化；L2W 則直接在世界座標下回歸，因此**不做尺度歸一化**，以保留多窗格之間一致的全域尺度。資料來自 ScanNet++、ASE、CO3D-v2 約 850K clips，在 8 張 NVIDIA 4090D 上訓練，輸入解析度固定為 $224 \times 224$（paper §3.4, §4.1）。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Monocular RGB video
        │   [B, N, 3, 224, 224]
        ▼
Sliding-window sampler  (stride s, window L=5 for I2P init / L=11 incremental)
        │   [B, L, 3, 224, 224]
        ▼
┌────────────────────────  I2P sub-network  ────────────────────────┐
│                                                                   │
│   E_img  (shared ViT encoder, m=24 blocks)                        │
│        │   per-frame tokens  F_i : [B, L, T, d]                   │
│        │   (T = number of patch tokens, d = encoder width)        │
│        │                                                          │
│        ├──► keyframe stream  F_key  : [B, 1, T, d]                │
│        └──► supporting stream F_sup : [B, L-1, T, d]              │
│                                                                   │
│   Multi-view decoder  (D_key + D_sup, n=12 blocks, weave-attn)    │
│        │   at each block:                                         │
│        │     - self-attn on each stream                           │
│        │     - cross-attn:  D_key  attends to                     │
│        │           max-pool_{j != key}( F_sup_j ) : [B, T, d]     │
│        │     - cross-attn:  D_sup  attends to F_key : [B, T, d]   │
│        ▼                                                          │
│   Regression head  (DPT-style)                                    │
│        │   pointmap   X̂_i : [B, L, 224, 224, 3]                  │
│        │   confidence Ĉ_i : [B, L, 224, 224]                     │
└───────────────────────────────────────────────────────────────────┘
        │   local pointmaps in keyframe coord  X̂_local : [B, L, 224, 224, 3]
        ▼
┌────────────────────────  L2W sub-network  ────────────────────────┐
│                                                                   │
│   Reservoir buffer S  (reservoir-sampled scene keyframes)         │
│        │   tokens of past keyframes  F_S : [|S|, T, d]            │
│        │   world pointmaps           X_S : [|S|, 224, 224, 3]     │
│        │                                                          │
│   Retrieval module  (reuse first r=2 blocks of D_reg)             │
│        │   query: current keyframe token F_key : [1, T, d]        │
│        │   key  : F_S                       : [|S|, T, d]         │
│        │   similarity score                  : [|S|]              │
│        │   pick top-K  ⇒  scene context  : [K, T, d] / [K,224,224,3]│
│        │                                                          │
│   E_pts  (points encoder, applied to world pointmaps in context)  │
│        │   point tokens  G : [K, T, d]                            │
│        │                                                          │
│   D_reg + D_sce  (multi-keyframe co-registration, Co=10)          │
│        │   D_reg input : F_key (Co current keyframes) [Co, T, d]  │
│        │   D_sce input : G (K scene-context frames)   [K,  T, d]  │
│        │   weave cross-attn between the two streams               │
│        ▼                                                          │
│   Regression head                                                 │
│        │   world pointmap  X̂_world : [Co, 224, 224, 3]           │
│        │   confidence      Ĉ_world : [Co, 224, 224]              │
└───────────────────────────────────────────────────────────────────┘
        │
        ▼
Global point cloud   (concat / fuse along time)  : [?, 3]
```

注：$T$ 與 $d$ 在 paper 中沿用 DUSt3R/CroCo 的 ViT 設計但未明列具體數值，故以符號保留；$|S|$ 為 reservoir 當下大小，$K$ 為單次 retrieval 取出的 scene-context 幀數，$Co$ 為一次 co-registration 同時處理的 keyframe 數（paper 設為 10）。

### 5.3 Per-Module Breakdown

#### Module 1 — Image Encoder $E_{img}$

- **Function**: 把每張 RGB 幀獨立編碼成 patch token 序列，作為 I2P 與 L2W 共用的視覺特徵來源。
- **Input**: 單一影像 $I_i \in \mathbb{R}^{224 \times 224 \times 3}$。
- **Output**: 影像 token $F_i \in \mathbb{R}^{T \times d}$，其中 $T$ 為 patch 數、$d$ 為 token 寬度。
- **Processing**: 使用 $m=24$ 層 ViT block（沿用 DUSt3R 的 CroCo 預訓練權重），所有幀共享同一組權重；I2P 與 L2W 訓練/推論時也共用此 encoder，以確保 reservoir 中歷史 keyframe 的 token 可以直接被 retrieval 重用，不必重新前向。
- **Key Formulas**: $F_i = E_{img}(I_i)$。
- **Implementation Details**: paper §3.1 與 §4.1 指出輸入解析度固定為 $224 \times 224$、encoder 深度 $m=24$；具體 patch size 與 $d$ 沿用 DUSt3R-224 設定，paper 本文未額外列出。

#### Module 2 — I2P Multi-view Decoder $D_{key} / D_{sup}$

- **Function**: 在窗格內以 keyframe 為錨，融合 $L-1$ 張支援幀的線索，輸出對齊到 keyframe 座標系的稠密點圖。
- **Input**: keyframe token $F_{key} \in \mathbb{R}^{T \times d}$ 與支援幀 token $\{F_{sup,j}\}_{j=1}^{L-1}$，每個皆為 $\mathbb{R}^{T \times d}$。
- **Output**: 經 $n=12$ 層解碼後的 keyframe 與支援幀解碼特徵，後接 regression head 得到 $\hat{X}_i \in \mathbb{R}^{224 \times 224 \times 3}$ 與 $\hat{C}_i \in \mathbb{R}^{224 \times 224}$，全部位於 keyframe 區域座標系。
- **Processing**: 每一個 decoder block 包含 self-attention、cross-attention、FFN；其中 $D_{key}$ 的 cross-attention 對所有支援幀 token 先做 element-wise **max-pooling**，再讓 keyframe 對 pooled token 做 attention，使網路可在不改變參數量的前提下接受任意 $L$；$D_{sup}$ 的 cross-attention 則統一對 $F_{key}$ attend，得到「以 keyframe 為條件」的支援幀表徵。
- **Key Formulas**: 多支援幀聚合
$$F_{sup}^{pool} = \max_{j=1,\dots,L-1} F_{sup,j}, \qquad F_{sup}^{pool} \in \mathbb{R}^{T \times d}.$$
I2P 訓練損失（含尺度歸一化）
$$\mathcal{L}_{I2P} = \sum_{i=1}^{L} M_i \cdot \left( \hat{C}_i \cdot \mathrm{L1}\!\left( \tfrac{1}{\hat{z}} \hat{X}_i,\; \tfrac{1}{z} X_i \right) - \alpha \log \hat{C}_i \right),$$
其中 $z, \hat{z}$ 為 GT/預測點到 keyframe 相機原點的平均深度，$M_i$ 為有效像素遮罩。
- **Implementation Details**: paper §3.1 指 $L=5$（初始）與 $L=11$（incremental）；解碼器深度 $n=12$；尺度歸一化是兩個子網路差異最大的訓練細節。

#### Module 3 — I2P Regression Head

- **Function**: 把 decoder 輸出的 token 映射回稠密點圖與 per-pixel confidence。
- **Input**: keyframe / 支援幀的 decoder 輸出 token，皆為 $\mathbb{R}^{T \times d}$。
- **Output**: 點圖 $\hat{X}_i \in \mathbb{R}^{224 \times 224 \times 3}$（keyframe 座標系下的 3D 點）、信心 $\hat{C}_i \in \mathbb{R}^{224 \times 224}$。
- **Processing**: 採 DUSt3R 的 DPT-style 上採樣 head，將 token 重新排列回 $(H/p, W/p)$ 的特徵圖後逐步上採樣到 $224 \times 224$，並以兩個獨立分支分別輸出 3 通道點座標與 1 通道 confidence；confidence 通過 softplus 保證為正。
- **Key Formulas**: $(\hat{X}_i, \hat{C}_i) = \mathrm{Head}_{I2P}(\mathrm{Dec}(F_i))$；$\hat{C}_i = 1 + \mathrm{softplus}(\cdot)$（沿用 DUSt3R 慣例）。
- **Implementation Details**: paper 並未針對 head 結構給出新設計，僅說明沿用 DUSt3R 的回歸頭與信心建模。

#### Module 4 — Retrieval Module

- **Function**: 在 L2W 階段，從 reservoir 中挑出與目前 keyframe 最具空間重疊的 $K$ 張歷史 keyframe，作為 scene context，避免每一輪都對所有歷史幀做 cross-attention。
- **Input**: 當前 keyframe token $F_{key} \in \mathbb{R}^{T \times d}$；reservoir 中已註冊的歷史 keyframe token $\{F_{S,k}\}_{k=1}^{|S|}$。
- **Output**: 索引集合 $\mathcal{K} \subset \{1,\dots,|S|\}$，$|\mathcal{K}| = K$，以及對應的 scene-context token / 世界點圖。
- **Processing**: **重用 $D_{reg}$ 的前 $r=2$ 個 decoder block** 對 $(F_{key}, F_{S,k})$ 各別做前向，從輸出 token 預測一個純量重疊分數，依分數做 top-$K$；因為 encoder token 在 reservoir 中是被快取的，整個 retrieval 不需重跑 $E_{img}$，計算量遠低於完整 L2W。
- **Key Formulas**: 對每個候選 $k$，重疊分數
$$s_k = \phi\!\left( D_{reg}^{(1:r)}(F_{key},\, F_{S,k}) \right), \qquad \mathcal{K} = \mathrm{TopK}_k\, s_k.$$
- **Implementation Details**: paper §3.3 指明 $r=2$；reservoir 採用 reservoir sampling 維持上限大小 $B$，使早期幀也有機會被保留，避免單純 FIFO 造成的 forgetting。

#### Module 5 — Points Encoder $E_{pts}$

- **Function**: 把已註冊到世界座標的點圖編成與影像 token 相容的序列，讓 L2W decoder 可以同時 attend 影像與幾何資訊。
- **Input**: 世界座標下的點圖 $X^w \in \mathbb{R}^{224 \times 224 \times 3}$（來自 reservoir 中已註冊的 keyframe）。
- **Output**: 點 token $G \in \mathbb{R}^{T \times d}$，與 $E_{img}$ 的輸出維度對齊。
- **Processing**: 將點圖視為 3 通道「影像」做 patch embedding 後，再經少量 transformer block 形成 token；輸出維度刻意設為與影像 token 相同的 $d$，方便在 $D_{sce}$ 中與影像 token 共用 attention 邏輯。
- **Key Formulas**: $G = E_{pts}(X^w)$。
- **Implementation Details**: paper §3.2 指 $E_{pts}$ 為 L2W 新增模組，I2P 子網路不使用。

#### Module 6 — L2W Decoders $D_{reg} + D_{sce}$（Multi-keyframe Co-registration）

- **Function**: 同時把 $Co$ 張當前 keyframe 的區域點圖搬到世界座標系，並參考 $K$ 張 retrieval 出的 scene context，做多 keyframe 共同註冊。
- **Input**:
  - 當前 keyframe 影像 token $F_{key} \in \mathbb{R}^{Co \times T \times d}$（$Co=10$）。
  - Scene-context 點 token $G \in \mathbb{R}^{K \times T \times d}$。
- **Output**: 對 $Co$ 張當前 keyframe，輸出世界座標點圖 $\hat{X}^w \in \mathbb{R}^{Co \times 224 \times 224 \times 3}$ 與 confidence $\hat{C}^w \in \mathbb{R}^{Co \times 224 \times 224}$。
- **Processing**: $D_{reg}$ 處理當前 keyframe 流、$D_{sce}$ 處理 scene-context 流，兩者在每一層做 weave-style cross-attention（與 I2P 的 max-pool 類似但作用在「current ↔ history」軸上），最後接一個與 I2P 結構相同的 regression head 輸出世界座標點圖。
- **Key Formulas**: L2W 訓練損失（**不做尺度歸一化**）
$$\mathcal{L}_{L2W} = \sum_{i=1}^{Co} M_i \cdot \left( \hat{C}^w_i \cdot \mathrm{L1}\!\left( \hat{X}^w_i,\, X^w_i \right) - \alpha \log \hat{C}^w_i \right).$$
省略 $1/z$ 是為了讓網路學到「跨窗格一致的全域尺度」，這是 SLAM3R 能用前饋方式做全域對齊的關鍵設計（paper §3.4）。
- **Implementation Details**: $Co=10$、$K$ 由 retrieval 決定；I2P 的損失含 $1/z, 1/\hat{z}$，L2W 的損失刻意拿掉，這個對比是 paper 強調的兩階段差異（paper §3.4, §4.1）。

#### Module 7 — Reservoir Buffer

- **Function**: 維護一個有界大小的歷史 keyframe 池，供 retrieval 與 scene context 取用，是把「在線 SLAM」與「前饋網路」接合的記憶體層。
- **Input**: L2W 完成註冊的 keyframe 影像 token $F_{key}$ 與其世界座標點圖 $X^w$。
- **Output**: 動態更新的集合 $S$，元素數 $|S| \le B$，每筆同時存 $F_{key}$ 與 $X^w$（影像 token 已在 $E_{img}$ 處算過，可直接快取）。
- **Processing**: 採用 **reservoir sampling**：當 $|S| < B$ 時直接寫入；達到上限後以遞減機率覆寫舊條目，使任意時刻 $S$ 都是已處理 keyframe 的近似均勻取樣，避免單純 FIFO 在長序列時遺失早期場景。
- **Key Formulas**: 對第 $t$ 個進入的 keyframe，當 $|S|=B$ 時以機率 $B/t$ 替換隨機一條既有條目；否則直接 append。
- **Implementation Details**: paper §3.3 強調 reservoir 的上限 $B$ 是控制 retrieval 計算量與長期記憶權衡的主要旋鈕；$B$ 的具體數值 paper 正文未列。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| ScanNet++ [71] | 室內場景 RGB 影片重建（real-world，iPhone + DSLR frames，由 COLMAP 註冊） | 每 epoch 隨機抽 4000 clips（stride = 3 取樣） | train |
| Aria Synthetic Environments (ASE) [3] | 合成室內場景重建 | 前 450 個 scenes，每 epoch 抽 2000 clips（stride = 2） | train |
| CO3D-v2 [41] | object-centric 重建 | 41 個類別、每類別最多 50 個 scene sequences；每 epoch 抽 2000 clips | train |
| 7 Scenes [51] | 真實室內 partial-scene 重建與 camera pose 評估 | 7 scenes（Chess/Fire/Heads/Office/Pumpkin/RedKitchen/Stairs），每 sequence 取 1/20 frames | test（unseen） |
| Replica [54] | 合成完整場景重建與 camera pose 評估 | 8 scenes（Room 0-2, Office 0-4），全 video frames 輸入 | test（unseen） |
| ScanNet [11] | 真實室內場景重建（補充比較） | 3 個抽樣 scenes（0011_00, 0015_00, 0019_00） | test（補充，§C） |
| Tanks and Temples [26] | 大場景重建（generalization） | 3 個 scenes（Ignitius / Truck / Caterpillar） | test（補充，§C） |
| ETH3D [49, 50] | 高解析度 multi-view stereo（generalization） | 3 個 scenes（plant_scene_1 / table_3 / sofa_1） | test（補充，§C） |
| BlendedMVS [69] | 大規模 MVS（generalization） | the paper does not specify | test（僅 qualitative，Fig. 5） |
| Map-free Reloc [2] | metric-scale relocalization（generalization） | the paper does not specify | test（僅 qualitative，Fig. 5） |
| LLFF [35] | forward-facing scene reconstruction | the paper does not specify | test（僅 qualitative，Fig. 5） |
| DTU [1] | unorganized image collections 重建 | the paper does not specify | test（僅 qualitative，Fig. 8） |
| In-the-wild captured videos | 泛化測試 | the paper does not specify | test（僅 qualitative） |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Accuracy (cm) | $\text{Accuracy} = \frac{1}{P}\sum_{i=1}^{P}\min_j D(x_i, y_j)$，重建點雲到 GT 點雲的最近鄰平均 Euclidean 距離 | yes |
| Completeness (cm) | $\text{Completeness} = \frac{1}{Q}\sum_{j=1}^{Q}\min_i D(x_i, y_j)$，GT 點雲到重建點雲的最近鄰平均距離 | yes |
| FPS | $\text{FPS} = F/\text{time}$，整段影片總幀數除以重建總時間，用以衡量 real-time 能力 | yes |
| ATE-RMSE (cm) | $\sqrt{\frac{1}{F}\sum_{i=1}^{F} D(T_i^{gt}, T_i^{pred})^2}$，預測與 GT camera trajectory 中心位置的 RMSE | no（次要分析；camera pose 由 PnP-RANSAC 從預測點雲反推） |

評估流程：所有重建點雲先以 Umeyama [58] + ICP [43] 對齊到 GT，再計算 accuracy / completeness。FPS 在單張 NVIDIA 4090D 上量測。GT 點雲由 GT depth 與 camera 參數 back-projection 得到。

### 6.3 Training and Inference Settings

- **硬體**：8 × NVIDIA 4090D GPUs，each 24 GB；total training 約一天。
- **Batch size**：每 GPU 4，總有效 batch size = 32。
- **影像解析度**：所有訓練與測試影像 center-crop 為 $224 \times 224$；採用 DUSt3R 標準 data augmentation。
- **權重初始化**：I2P 與 L2W 從 DUSt3R 224 預訓練權重出發（$m = 24$ encoder blocks、$n = 12$ decoder blocks，linear head）。
- **Optimizer / learning rate / schedule**：the paper does not specify。
- **訓練階段**（§A）：
  - I2P：clip length = 11，中間 frame 為 keyframe；100 epochs，約 6 hours。
  - Retrieval module：固定其餘權重，僅更新 linear projection；以 L1 loss 監督 correlation score 對齊 I2P mean confidence；50 epochs，約 2 hours。
  - L2W：clip length = 12，前 6 frames 為 scene frames、後 6 為待註冊 keyframes；200 epochs，約 16 hours；GT pointmaps 中無效點以 (0, 0, 0) 填補；不做 scale normalization 以維持與 scene frames 一致尺度。
- **Inference 設定**：
  - Initial window length $L = 5$；後續 incremental windows 用 $L = 11$ 提供更多 supporting views。
  - Sliding-window stride = 1，使每個 frame 都至少當過一次 keyframe。
  - Replica（full video）：window stride 內 frame skip = 20，多 keyframe 共同註冊 $C_o = 10$、retrieval top-$K = 10$、reservoir 更新間隔 $R = 20$；reservoir 採 Vitter [59] 採樣（$\Pr(\text{insert}) = B/\text{id}$，超過容量時隨機替換）。
  - 7 Scenes（每 20 frames 取樣）：$\text{Skip} = 1$、$C_o = 2$、$K = 5$、$R = 1$。
  - SLAM3R 主表 confidence threshold 固定為 3；SLAM3R-NoConf 不做 confidence 過濾。
  - Camera pose：由預測 scene points + GT intrinsics 餵入 OpenCV [6] PnP-RANSAC 反推。

### 6.4 Main Results

7 Scenes [51]，Acc / Comp（cm，average over all sequences）：

| Method | Acc. ↓ | Comp. ↓ | FPS ↑ | Notes |
|---|---|---|---|---|
| DUSt3R [64] | 2.19 | 3.24 | <1 | offline，pairwise + global alignment |
| MASt3R [28] | 3.04 | 3.90 | ≪1 | triangulation-based |
| Spann3R [61] | 3.42 | 2.41 | >50 | concurrent，frame-by-frame incremental |
| SLAM3R-NoConf (Ours) | 2.40 | 2.24 | ∼25 | 不做 confidence 過濾 |
| **SLAM3R (Ours)** | **2.13** | **2.34** | **∼25** | confidence threshold = 3，FPS > 1 群中 Acc / Comp 皆 SoTA |

Replica [54]，Acc / Comp（cm，average over 8 scenes）：

| Method | Acc. ↓ | Comp. ↓ | FPS ↑ | Notes |
|---|---|---|---|---|
| DUSt3R [64] | 3.49 | 2.48 | <1 | 1/20 frames（記憶體限制） |
| MASt3R [28] | 4.71 | 3.36 | ≪1 | 1/20 frames |
| NICER-SLAM [79] | 3.65 | 4.16 | ≪1 | 結果取自原論文 |
| DROID-SLAM [56] | 5.50 | 12.29 | ∼20 | 結果取自 NICER-SLAM |
| DIM-SLAM [29] | 11.60 | 7.85 | ∼3 | 結果取自 NICER-SLAM |
| GO-SLAM [75] | 3.81 | 4.79 | ∼8 | 僅報 average |
| Spann3R [61] | 10.32 | 13.33 | >50 | concurrent |
| SLAM3R-NoConf (Ours) | 3.76 | 2.62 | ∼24 | |
| **SLAM3R (Ours)** | **3.57** | **2.62** | **∼24** | FPS > 1 群中 Acc / Comp 皆超越所有 baseline |

Camera pose（ATE-RMSE，cm；Table 3）：

| Method | 7 Scenes | Replica | Notes |
|---|---|---|---|
| DUSt3R (w/PnP) | 8.02 | 4.76 | 從預測 pointmap 經 PnP 反推 |
| MASt3R (w/PnP) | 6.28 | 1.67 | |
| NICER-SLAM | 8.55 | 1.88 | |
| DROID-SLAM | 5.66 | 0.33 | SLAM-specialized |
| DIM-SLAM | — | 0.46 | |
| GO-SLAM | — | 0.39 | |
| Spann3R | 11.70 | 32.79 | |
| **SLAM3R (Ours)** | **8.41** | **6.61** | 7 Scenes 上略勝 NICER-SLAM 與 Spann3R；Replica 上落後純 SLAM 系統 |

主要訊息：在 FPS > 1 的方法中，SLAM3R 在兩個 unseen benchmark 的 Acc 與 Comp 同時奪冠，且維持 ∼25 FPS 的 real-time 重建；camera pose 雖落後專注於 localization 的 DROID-SLAM / GO-SLAM，但作者明示重建品質與 pose error 並非完全正相關，這正是 end-to-end 點雲重建的論述支點。

### 6.5 Ablation Studies

1. **I2P window length（Table 4 / Fig. 9，Replica keyframe-only Acc / Comp）**
   - 變項：window 長度從 2（等價 DUSt3R two-view）→ 5 → 11（default）→ 15 → 51。
   - 結果：Acc 由 3.39 → 2.62 → 2.38 → 2.27 → 2.23；Comp 由 3.04 → 2.28 → 2.03 → 1.94 → 1.86；FPS 在 ≤ 11 時穩定（42.55 → 40.11），到 51 時掉到 11.97。
   - 診斷性：直接回答「multi-view cross-attention 是否真比 DUSt3R two-view 強」與「為何 default 取 11」；同時指出 diminishing return（重疊變少 + 推論變慢），結論明確。屬有效 diagnostic ablation。

2. **L2W 對齊策略（Table 5，Replica full scene）**
   - 對照：I2P+GA（DUSt3R global alignment 優化）、I2P+UI（Umeyama + ICP）、I2P+L2W（取最近 10 frames 為 reference，無 retrieval）、I2P+L2W+Re（Full，retrieval top-K）。
   - 結果（Acc / Comp / FPS）：4.87 / 3.00 / ∼3、7.47 / 3.86 / ∼1、6.19 / 3.54 / ∼92、**3.62 / 2.70 / ∼43**。
   - 診斷性：同時對照「優化 vs 神經對齊」與「nearest-frame vs retrieval」兩個正交因子。Full 顯示 L2W 本身比 GA 與 UI 都好；Re 把 6.19 → 3.62，明確證實 retrieval 對減少累積 drift 的貢獻，是真正診斷 retrieval 必要性的實驗。

3. **Scene frame 數量對 registration 的影響（Table 9，Replica）**
   - 變項：scene frame 數 1 / 5 / 10 / 20 / 30 / 40 / 50。
   - 結果：Acc 4.18 → 3.99 → **3.57** → 3.57 → 3.59 → 4.15 → 4.27；FPS 從 ∼398（1 frame）下滑到 ∼37（50 frames）。
   - 診斷性：標準 hyperparameter sweep；驗證「太少會掉進 local minimum、太多會引入無關 frame 干擾」的論點，並合理化 Replica K = 10 / 7 Scenes K = 5 的選擇。屬有效 diagnostic。

4. **Confidence filtering（Table 1, 2 中 SLAM3R vs SLAM3R-NoConf）**
   - 結果：7 Scenes 2.40/2.24 → 2.13/2.34；Replica 3.76/2.62 → 3.57/2.62。
   - 診斷性：偏向 sanity check —— 顯示 confidence head 有用、但兩者差距很小，主要訊息是「confidence threshold = 3 是合理預設」，並未深入分析 confidence 與真實 error 的相關性。

整體看這四個 ablation 中，前三個（window length、alignment 策略、scene frame 數）都是真正診斷新組件的實驗；只有 confidence filter 偏向 sanity check。**缺少對「multi-view cross-attention + max-pool 聚合」這一核心架構創新的 head-to-head ablation**（例如改用 mean-pool、concat、或 DUSt3R 原生 cross-attention 串接的對照），讀者只能從 window-length 表間接推得其價值。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — DUSt3R [64]、MASt3R [28]、Spann3R [61]、NICER-SLAM [79]、DROID-SLAM [56]、GO-SLAM [75]、DIM-SLAM [29] 同台，涵蓋 end-to-end 與 SLAM 兩條路線的當代代表（Tables 1-3, 6-7）。
- [covered] Has cross-task / cross-dataset evaluation — 主表測 7 Scenes + Replica，補充再加 ScanNet、Tanks and Temples、ETH3D、BlendedMVS、Map-free Reloc、LLFF、DTU 與 in-the-wild 影片（Table 8、Figs. 5, 8）。
- [partial] Has ablations that diagnose the new components — window length、alignment 策略、retrieval、scene-frame 數皆為 diagnostic（Tables 4, 5, 9），但缺少對 multi-view cross-attention 聚合方式（max-pool vs 替代）的直接 ablation。
- [partial] Has a scaling study — window length 2 → 51（Table 4 / Fig. 9）與 scene frame 1 → 50（Table 9）算長度面的 scaling，但**沒有模型大小、訓練資料量或 compute 的 scaling 分析**。
- [covered] Has an efficiency / wall-clock comparison — 所有主表都同列 FPS（Tables 1-2, 4-5, 9），且明確區分 FPS > 1 / < 1 兩組。
- [missing] Reports variance / standard deviation / multiple seeds — 全文僅報單次數值，no std、no seed sweep；reservoir sampling 為隨機過程但未標註隨機性影響。
- [covered] Releases code / weights / data sufficient for reproducibility — Abstract 標明 https://github.com/PKU-VCL-3DV/SLAM3R；訓練資料與超參在 §A、§B 詳述。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1 — 「即時 end-to-end RGB 稠密重建，20+ FPS」**：SUPPORTED。Tables 1–2 一致回報 ~24–25 FPS，且為實際完整 pipeline（非單純 alignment overhead），確實落在 real-time 區間。
- **Claim 2 — 「I2P 將 DUSt3R 廣義化到任意視圖數並提升品質」**：SUPPORTED。Table 4 顯示從 $L=2$ 的 3.39 / 3.04 cm 單調改善到 $L=11$ 的 2.38 / 2.03 cm，且 efficiency 在 $L \le 11$ 內穩定。
- **Claim 3 — 「L2W 直接將 local pointmap 對齊到全域，省去顯式相機參數最佳化與 costly global optimization」**：PARTIALLY SUPPORTED。Table 5 在 alignment 子問題上同時贏過 GA 與 Umeyama+ICP；但 Table 6–7 的 ATE 顯示，相較於有 BA 的 SLAM 方法仍差一到兩個量級，等於只是「在重建度量上不需要 GA」，而非「全域一致性不需要 GA」。
- **Claim 4 — 「在 accuracy 與 completeness 上達 state-of-the-art real-time」**：SUPPORTED 但有限定。在 FPS > 1 的群組內確實全面領先（Tables 1–2）；對比離線 DUSt3R / MASt3R 時，部分場景（如 7 Scenes Heads、Stairs）DUSt3R accuracy 仍較佳，論文措辭「comparable to」較為精確。
- **Claim 5 — 「self-contained retrieval 提供長期歷史的 implicit re-localization」**：SUPPORTED。Table 5 的 I2P+L2W vs I2P+L2W+Re 顯示從 6.19 / 3.54 cm 改善至 3.62 / 2.70 cm，幅度足以證明 retrieval 不只是錦上添花。

### 7.2 Fundamental Limitations of the Method

**沒有可微分的 pose 表示，導致 BA 與感測器融合受阻。** 整個系統把「相機參數」當成 pointmap 預測的副產物（透過 PnP-RANSAC 從預測點雲反推），這意味著任何下游需要 $\text{SE}(3)$ 軌跡的應用都必須事後解算，並承擔 PnP 解的雜訊；同時也使得 IMU、輪速計、GPS 等感測融合在架構上找不到自然介面。論文以「end-to-end 不需 pose」框成優勢，但 ATE 落差是這個框架的結構性代價而非工程偏差。

**224×224 解析度與 DUSt3R 預訓練綁定。** I2P / L2W 都是從 DUSt3R-224 初始化（page 7），訓練資料也統一裁切到 $224 \times 224$。這個尺寸對於 SLAM / MVS 任務偏低，意味著「室外大尺度、細結構、遠景物件」的幾何上限是被 backbone 鎖死的；要升到 512 必須重訓全部模組並重新調節所有超參數，且 multi-view cross-attention 的記憶體會以 $T^2$ 成長，不是免費的工程工作。

**Drift 控制完全寄望於 retrieval 而沒有形式化 loop closure。** L2W 的全域一致性來自「找到夠相關的 scene frame 一起 refine」，這對短期 drift 與部分中期 drift 有用，但對「真正閉合一個大迴圈」沒有強制機制：若 retrieval 在關鍵幀沒有命中歷史，系統沒有 fallback 也沒有後驗修正。Replica 上 6.61 cm 的 ATE 一部分就是這個結構問題的訊號。

**對 static rigid scene 做了強假設。** Problem statement（page 3）即定義在 static scene 上，pointmap regression 也預設世界座標下的點是時間不變的；MonST3R 等動態擴展工作之所以存在，正是因為這個假設無法處理人、車、可動家具。SLAM3R 在當前公式下無法以加 loss 或加 head 來「軟化」這個假設，需要重新設計 representation。

### 7.3 Citations Worth Tracking

- **DUSt3R (Wang et al., 2024) [64]** — SLAM3R 的 backbone、loss、初始權重全來自此；任何 reproduction 或延伸都必須先吃透其 pointmap 公式與 confidence loss。
- **Spann3R (Wang & Agapito, 2024) [61]** — 同問題、不同架構的 concurrent work；用「spatial memory token」串連單幀，是理解「為何 SLAM3R 選擇多幀窗口而非 token 化記憶體」最直接的對照組。
- **MASt3R (Leroy et al., 2024) [28]** 與其延伸 **MASt3R-SfM [14]** — 加 match head 走 SfM 路線的 DUSt3R 變體；若要把 SLAM3R 升到高解析度與 BA-friendly，MASt3R 的 matching loss 與 keypoint geometry 是最現成的銜接點。
- **DROID-SLAM (Teed & Deng, 2021) [56]** — Replica 0.33 cm ATE 的 baseline，是 SLAM3R pose 落差的正面參照；理解其 dense bundle adjustment 模組對於日後設計「SLAM3R + 輕量 BA」幫助最大。
- **MonST3R (Zhang et al., 2024) [74]** — DUSt3R 在動態場景下的延伸，正是 SLAM3R 目前缺席的領域；想把這條路線推到非 static scene，這篇是最直接的設計來源。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在 7 Scenes 原生 frame rate（不取 1/20）下，drift 是否會隨序列長度線性累積？論文目前的取樣協議遮蔽了這個維度。
- [ ] Multi-view cross-attention 的「diminishing returns」（Figure 9）是 224×224 解析度下的 overlap 不足造成，還是 max-pool 聚合本身的容量瓶頸？在 512 解析度重訓後 $L > 15$ 的曲線會不會重新單調上升？
- [ ] Retrieval module 在強感知混淆場景（重複走廊、相似房間）的 false-positive 率如何？論文以 confidence regression 訓練，但 confidence 對 perceptual aliasing 並非設計上的偵測信號。
- [ ] 為何 SLAM3R 的 pose 在 7 Scenes（8.41 cm）與 Replica（6.61 cm）皆落後 DROID-SLAM 約 20 倍，而 reconstruction 卻全面贏過？這個 decoupling 是 PnP-from-pointmap 的雜訊上限，還是缺乏 BA 的本質限制？
- [ ] Reservoir buffer 的大小 $B$ 在實驗中實際取何值，且當影片長度 $\to \infty$ 時 retrieval 命中率與重建品質如何衰減？論文僅描述機制而未做 scaling study。
- [ ] 是否能在不破壞 ~24 FPS 的前提下加上輕量 pose head 與 sliding-window BA，把 ATE 拉到接近 DROID-SLAM 的等級？
- [ ] L2W 的 scene decoder 能同時 co-register 多個 keyframe（page 9 supplementary），但實驗只取 $C_o = 10$；不同 $C_o$ 對 throughput vs 一致性的曲線完全沒有揭露。

### 8.2 Improvement Directions

1. **以 MASt3R-512 或 DUSt3R-512 預訓練重新初始化並重訓 I2P / L2W。** 預訓練權重已存在，只需付出重訓代價，但 224×224 是當前 accuracy 與 completeness 的明顯天花板，且高解析度重訓後 multi-view 的 diminishing returns 很可能延後出現，等於同時拿到品質與 $L$ 的 headroom。
2. **加上輕量 pose head + 在 retrieved scene frames 上做 windowed pose graph optimization。** 重建品質已不錯，real-time 預算亦有餘裕；明確 $\text{SE}(3)$ 表示能直接緩解 ATE 落差，並打開與 IMU / GPS 等感測融合的介面，是「結構性升級而非性能調校」。
3. **將 L2W 的 free-form pointmap regression 改寫為「先預測 keyframe 之 rigid transform，再在世界座標下回歸殘差變形」。** 此舉把「全域對齊」與「局部幾何修正」解耦，符合 rigid scene 的物理結構，能避免 pointmap 在世界座標中產生不合理的非剛性形變，也讓 retrieval 命中失敗時的退化模式更可預測。
4. **以 MonST3R 風格資料訓練 dynamic mask head，並讓 L2W 對被遮罩區域略過 scene-frame 對齊。** 此延伸可在保留主架構的情況下打破「static scene」假設，是擴展可用場景最直接的路徑。
5. **以真正的 loop-closure pair（例如重複走訪同一位置）作為 retrieval 的監督，取代目前以 I2P confidence regression 的代理目標。** 當前訓練讓 retrieval 學「視覺相似」，但 SLAM 任務真正需要的是「重訪偵測」；改換監督後 retrieval 將變成可信賴的 loop detector，與第 2 點搭配可形成完整的全域一致性閉環。
