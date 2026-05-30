<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# VGGT-SLAM — VGGT-SLAM: Dense RGB SLAM Optimized on the SL(4) Manifold

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | VGGT-SLAM |
| Paper full title | VGGT-SLAM: Dense RGB SLAM Optimized on the SL(4) Manifold |
| arXiv ID | 2505.12549 |
| Release date | 2025-05-23 |
| Conference/Journal | arXiv preprint (Under review) |
| Paper link (abs) | https://arxiv.org/abs/2505.12549 |
| PDF link | https://arxiv.org/pdf/2505.12549 |
| Code link | — |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Dominic Maggio | Massachusetts Institute of Technology (MIT), SPARK Lab | https://dominic101.github.io/DominicMaggio/ | co-first author |
| Hyungtae Lim | Massachusetts Institute of Technology (MIT), SPARK Lab (postdoc) | https://limhyungtae.github.io/hyungtae-lim/ | co-first author |
| Luca Carlone | Massachusetts Institute of Technology (MIT), Department of Aeronautics and Astronautics, LIDS, SPARK Lab | https://lucacarlone.mit.edu/ | PI / senior author / corresponding author |

### 1.2 Keywords

Dense RGB SLAM, VGGT, Feed-forward 3D reconstruction, Projective ambiguity, SL(4) manifold optimization, 15-DOF homography, Submap alignment, Factor graph optimization

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al., [68]) | base model | Feed-forward Transformer estimating depth/poses/point maps from arbitrary uncalibrated frames; core submap generator. |
| MASt3R-SLAM (Murai et al., [44]) | baseline | Most similar real-time dense monocular SLAM built on MASt3R using Sim(3) optimization and loop closures. |
| DUSt3R (Wang et al., [70]) | predecessor | Seminal feed-forward pairwise dense point-map reconstruction from uncalibrated images; lineage origin. |
| MASt3R-SFM ([14]) | influence | Global optimization of multiple images via MASt3R; motivates the need for scalable submap-based alignment. |
| Spann3R ([67]) | concurrent | Memory-module extension of DUSt3R for incremental multi-frame reconstruction limited to short sequences. |
| Cut3R ([69]) | concurrent | Recurrent-state extension of DUSt3R for incremental multi-image reconstruction. |
| SALAD ([26]) | influence | Visual place recognition descriptor used for keyframe retrieval to seed loop closures in VGGT-SLAM. |

## 2. Research Overview

### 2.1 Research Topic

本論文研究在僅有未標定 (uncalibrated) 單眼 RGB 影像、且不需事先校正相機內參的條件下,如何將前饋式 (feed-forward) 場景重建模型 VGGT 擴充為可處理長視訊序列的稠密 SLAM 系統。由於 VGGT 受限於 GPU 記憶體,單次推論僅能處理約 60 張影像,作者透過將輸入切分為多個重疊子圖 (submap),再在後端進行全域對齊,以重建大規模場景並估計六自由度相機位姿。論文同時針對未標定相機所引發的 projective ambiguity 進行系統性分析,指出傳統以 Sim(3) 對齊子圖的策略在某些情境下不足,因而需以更高自由度的對齊方式取代。整體研究主題橫跨多視幾何、Lie group 上的非線性最佳化,以及學習式前饋重建與經典 SLAM 後端的結合,屬於三維視覺與機器人感知交會的問題。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- SLAM
- Robotics
- Multi-view Geometry

### 2.3 Core Architectures Used

- **VGGT (Visual Geometry Grounded Transformer)**:作為本系統的前饋式子圖生成器,接收任意數量未標定影像、以微調過的 DINO backbone 進行 tokenization,再透過 Alternating-Attention 與 DPT heads 產生 dense depth maps、confidence maps、相機位姿與內參估計;作者使用其 depth 與位姿輸出反投影成單一子圖點雲 $X^S$。
- **DINO backbone (微調版)**:VGGT 內部用以將輸入影像 tokenize 為視覺特徵的骨幹網路,本論文沿用其輸出 token 作為下游 heads 的共同表徵。
- **DPT (Dense Prediction Transformer) heads**:VGGT 用以輸出每張影像的 dense depth、point map 與點追蹤 features 的解碼頭,本論文僅取 depth 與 confidence 分支。
- **SALAD**:外部 visual place recognition 描述子模組,為每一個 keyframe 計算描述子並以 L2 距離搜尋相似 frame,以提供 loop closure 候選。
- **Lucas-Kanade 視差估計**:用於以視差門檻 $\tau_{\text{disparity}}$ 選取 keyframe,以確保送入 VGGT 的 frame 之間具有足夠的多視差訊號。
- **5-point RANSAC + direct linear method**:用於由共享 frame 之 dense correspondences 解 (2) 求子圖之間的 4×4 homography,並進行外點濾除。
- **SL(4) factor graph (本論文提出)**:首個直接在 SL(4) Lie group 流形上構建的非線性 factor graph,以 odometry 與 loop closure 之相對 homography 為觀測,於 MAP 框架下求解絕對 homography。
- **Levenberg-Marquardt 最佳化器**:用於迭代解 (5) 之線性化最小平方問題,並以 SL(4) 之 Exp/Log、Jacobian 與 adjoint map 在流形上更新狀態。

### 2.4 Core Argument

作者所識別的根本原因是:當以未標定單眼相機為輸入時,根據經典的 Projective Reconstruction Theorem,任何重建在原則上只能還原至真實幾何的 15 自由度 projective transformation,亦即一個屬於 SL(4) 的 4×4 homography 矩陣;在缺乏可靠場景先驗 (例如平行線、正交性) 時,VGGT 雖可藉由學習到的先驗試圖恢復近似度量重建,但其輸出仍可能殘留 shear、stretch 與透視變形等非相似性自由度,特別是在影格間視差 (disparity) 較小時更為明顯。因此,當以多個 VGGT 子圖拼接重建大場景時,僅以 Sim(3) (旋轉、平移、尺度) 對齊子圖,在數學上不足以同時消除這些 projective 自由度,實驗中也呈現可見的對齊錯位。基於此,作者主張對齊問題必須直接在 SL(4) Lie group 上求解 15 自由度 homography:他們利用子圖之間共享同一影格所天然提供的稠密對應點,透過 5 點 RANSAC 與 direct linear method 估計相鄰子圖之間的相對 homography,並結合 SALAD 影像檢索獲得的迴路閉合 (loop closure) 約束,構建一個在 SL(4) 流形上的非線性 factor graph 最佳化問題,以 Maximum A Posteriori 形式求解所有絕對 homography。為使最佳化可行,作者導出 SL(4) 的指數對映、tangent-space 參數化、Jacobian 與 adjoint map,並以 Levenberg-Marquardt 反覆更新。此一推導鏈使其解決方案在邏輯上成為唯一在原理上能完整修正前饋式未標定重建之 projective ambiguity 的選擇,而非僅是經驗性的工程技巧;同時即便在 projective ambiguity 不顯著的情境,SL(4) 的廣義性仍可退化覆蓋 Sim(3),因此在精度上仍具競爭力。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(195 words)

標題 "VGGT-SLAM: Dense RGB SLAM Optimized on the SL(4) Manifold" 將論文定位於三個關鍵元素：以 VGGT 為基礎、稠密 RGB SLAM、以及在 SL(4) manifold 上進行優化。Abstract 以「使用未校準單目相機 (uncalibrated monocular cameras)」開場，宣告這是一套在 VGGT feed-forward scene reconstruction 之上，透過增量 (incremental) 與全域 (global) 對齊 submaps 的稠密 SLAM 系統。

接著 Abstract 提出論文的核心論點：相關工作普遍採用 similarity transform（平移、旋轉、尺度，共 7 DOF）來對齊 submaps，但作者主張此假設在未校準相機下「不充分 (inadequate)」。為了支撐此主張，Abstract 重新喚起經典多視幾何中的 reconstruction ambiguity 概念——在沒有相機運動或場景結構先驗的情況下，未校準相機僅能在「15-degrees-of-freedom projective transformation」之下重建場景。

從這個觀察推導出方法主張：透過在 SL(4) manifold 上優化，估計 sequential submaps 之間的 15-DOF homography，並同時容納 loop closure constraints。最後 Abstract 給出實驗承諾：相比於原生 VGGT 因高 GPU 需求無法處理的長序列影片，VGGT-SLAM 能取得改進的地圖品質。整段 Abstract 形成「問題 (VGGT 規模限制) → 觀察 (projective ambiguity) → 方法 (SL(4) 優化) → 結果 (改進長序列地圖)」的緊湊敘事，為 §1 Introduction 鋪設了 SLAM 與 feed-forward 兩條主線即將在 SL(4) manifold 上交會的伏筆。

### 3.2 Introduction

(540 words)

Introduction 從 SLAM 的基礎定義切入：給定多張單目（或立體）影像，重建 3D 場景並估計相機 6-DOF pose。作者迅速勾勒出兩種方法論主軸——傳統路線依賴 multi-view geometry constraints、data association、bundle adjustment 等經典工具；近期則出現以 feed-forward 網路直接從未校準影像產生點雲的新典範。這個對比是 Introduction 的第一個轉折，目的在於把讀者從「分階段、幾何驅動」的舊典範移轉到「端到端、學習驅動」的新典範。

接著 Introduction 介紹兩個關鍵 milestone：DUSt3R 處理 image pair 並輸出第一相機座標系下的稠密點雲，搭配 3-point RANSAC 即可恢復相機 pose；VGGT 則進一步擴展到任意數量影像，同時輸出 dense point clouds、depth maps、feature tracks、camera poses 與 intrinsics。這段鋪陳建立了 VGGT 作為 backbone 的合理性。

Introduction 的第二個轉折是 VGGT 的限制：受 GPU memory 制約，例如在 NVIDIA GeForce RTX 4090 24 GB 上大約只能處理 60 frames，使數百乃至數千 frames 的大型重建變得 infeasible。這是論文要解決的具體痛點，也是引出 SLAM 化處理的契機。

第三個轉折是論文預先「拆解」一個看似自然的 trivial solution：把序列切成多個 submaps（每兩個 submap 之間至少共享一個 frame），再求解 submap 之間的 scale 參數。作者預告此做法不足以解決對齊問題，因為對齊不只是尺度差異——這正是後續 §4.2 才會展開的 projective ambiguity 主張。

雖然從給定的擷取看不到 Introduction 後半段，但根據 Abstract 與 §4 結構可以推斷 Introduction 在這之後接續四件事：(1) 點出 similarity transform 不足以對齊 VGGT submaps；(2) 借多視幾何理論引出 15-DOF projective transformation 的需求；(3) 預告本文以 SL(4) manifold 上的 factor graph 優化作為解法，同時整合 loop closure；(4) 列出貢獻：第一個在 SL(4) 上做 SLAM factor graph 優化的工作、能處理 VGGT 無法獨力應付的長序列、並維持稠密重建品質。

整章 Introduction 的故事邏輯是「SLAM 老問題 → feed-forward 新典範 → VGGT 規模瓶頸 → 看似可用的 submap trick → 為何 trick 不夠 → 我們的 SL(4) 解法」。它為 §2 的 related work 鋪好了「為何要關注 SL(n) manifold 上的優化」這條伏線，也為 §3 預備了讀者必須理解 VGGT 內部結構才能跟上後續方法的閱讀基礎。

### 3.3 Related Work / Preliminaries

(820 words)

§2 Related Work 與 §3 Review: VGGT 合計建立讀者進入方法章節前所需的全部背景。Related Work 分為四個子主題，順序刻意從「最遠的鄰居」走向「最近的鄰居」。

第一段 Classical Scene Reconstruction 快速回顧傳統幾何方法：sparse feature 抽取與匹配、SE(3) 上的 robust pose estimation、bundle adjustment，以及 Sim-Sync 引入單目深度先驗的可證最優演算法。這段的功能不是逐一比較，而是讓讀者意識到「過去六十年都把 SLAM 視為 SE(3) 或 Sim(3) 問題」，使後文跳到 SL(4) 顯得更具突破性。

第二段 Feed-forward Scene Reconstruction 是篇幅最重的一段，依時序與相依關係列出 DUSt3R 系譜：DUSt3R 本身、利用 Weiszfeld 算法估焦距並用 3-point RANSAC 解 pose 的標準流程、新增描述子的 MASt3R、做全域優化但 scaling 不佳的 MASt3R-SFM、加入 memory module 的 Spann3R 與 recurrent state 的 Cut3R、可吃多種額外輸入的 Pow3R、輸出 Gaussian Splatting 參數的 Splatt3R 與其多視擴展 PreF3R、以及聚焦相對 pose 與 motion averaging 的 Reloc3r。這份名錄看似羅列，實則為了強化兩個訊號：feed-forward 路線生機蓬勃、但每一個衍生工作都受限於 frame 數或計算量。

接著作者點名與本作「最相似」的 MASt3R-SLAM：它已是即時、稠密、無校準的單目 SLAM，並在 Sim(3) 上做優化與 loop closure。這段同時處理「相似性」與「差異化」兩件事——相似性在於同樣是 feed-forward 為核心的 SLAM；差異化在於 MASt3R 一次只能吃兩張 frame，而 VGGT 可一次吃多張，且 VGGT submap 的對齊「不能僅靠 similarity transformation 完成」。這句正是把讀者推進 §4.2 的勾子。作者也順手指出與 MASt3R-SLAM 的另一個方法差異：本作不需要估計 frame 之間的 correspondences。

第三段 scene coordinate regression 簡短帶過 ACE 與 DSAC*，提醒讀者還有第三條典範存在，但因需 scene-specific 訓練，與本作無校準、通用的目標方向不同。

第四段 Optimization over the Special Linear group 是整節的關鍵，明確主張「就我們所知，這是首篇在 SL(4) manifold 上建構 factor graph optimization 的工作」。作者引用 SL(3) 上 8-DOF homography 在 panoramic stitching 與 dense SLAM 的傳統，再點出 15-DOF homography 在 auto-calibration 等經典任務中的角色，藉此為跳到 SL(4) 補上理論先例。

§3 Review: VGGT 切換到 preliminaries 模式。它告訴讀者 VGGT 吃影像集 $I = \{M_1, \cdots, M_{\bar{w}}\}$，先用 fine-tuned DINO backbone tokenize，再透過 Alternating-Attention（在 global 與 frame-wise attention 之間切換）處理 tokens。輸出 tokens 接到兩條 head：camera head 估 intrinsics 與相對於第一個 frame 的 camera poses；DPT heads 輸出每張影像的 dense depth maps 以及 dense point map（依擷取所示，後續還會涉及點雲、feature tracks 等其他輸出，但本段截斷處未完整呈現）。

整體而言，§2-§3 完成三件事：(1) 把讀者放回 SLAM 與 feed-forward reconstruction 兩個競合脈絡；(2) 凸顯本作在 SL(4) 上做 factor graph SLAM 的「首創」位置；(3) 預先把 VGGT 的輸入輸出與 head 結構交代清楚，使 §4 直接從「如何串接 VGGT submaps」展開，不再需要回頭解釋 VGGT 本身。

### 3.4 Method (overview narrative)

(265 words)

§4 VGGT-SLAM 採用「先給總體流程，再依次落地」的層次敘事，由四個子節 §4.1–§4.4 組成。整體骨架是：把長序列影片以增量方式切成 submaps，每個 submap 由一次 VGGT 前向通過產生稠密幾何；接著解決 submaps 之間的對齊問題；最後將兩種對齊（相鄰 submap 與 loop closure）統一進一張 factor graph，於 SL(4) manifold 上做非線性優化。

§4.1 Incremental submap-based keyframe selection and generation 處理「frames 怎麼進入 submap」，給出 keyframe 選擇與 submap 生成的規則，是所有後續優化的輸入端。Abstract 與 §1 已暗示此設計的動機是繞開 VGGT 的 GPU memory bound，因此 §4.1 在故事邏輯中扮演「把不可一次處理的長序列拆成可處理單元」的角色。

§4.2 Local submap alignment addressing projective ambiguity 是方法章的理論心臟。它把 §1 與 §2 反覆預告的論點——未校準相機下重建只能恢復到 15-DOF projective transformation——正式落地：相鄰 submaps 不能僅以 similarity transform 對齊，而必須估計 SL(4) 上的 homography。這一節同時說明為何不需要 frame 之間的 correspondences（與 MASt3R-SLAM 的關鍵分野）。

§4.3 Loop closures 把全域一致性納入考量，使長軌跡（例如 §5.4 將展示的 55 公尺辦公走廊迴圈、22 個 submaps）得以收斂。

§4.4 Backend: Nonlinear factor graph optimization on the SL(4) manifold 將前述所有對齊轉化為 SL(4) factors，連同 loop closure 一起進入 factor graph 求解；附錄 A 補上 sl(4) Lie algebra 的 15 個 generators 以及 $H = \exp(\xi^\wedge)$ 的指數映射定義，使讀者理解 backend 在 manifold 上做更新的具體機制。整個 §4 的故事邏輯是「切片 → 在每組切片之間裝上對的對齊代數結構 → 把所有約束放進 factor graph 一次解掉」。

### 3.5 Experiments (overview narrative)

(345 words)

§5 Experiments 採取「先設定、後分項評估、再消融」的標準 SLAM 論文結構。§5.1 Experimental setup 釘下三件事：評估指標（以 evo 計算 absolute trajectory error 的 RMSE，並在 7-Scenes 上額外計算 accuracy、completion、Chamfer distance）、baselines（主比 DROID-SLAM 與 MASt3R-SLAM，加上 Spann3R 用於稠密評估，並引入有 calibration 的 ORB-SLAM3、DPV-SLAM、GO-SLAM、NICER-SLAM 等做完整光譜對照），以及硬體與超參數（RTX 4090 + Threadripper 7960X、$w_{\text{loop}}=1$、$\tau_{\text{disparity}}=25$ pixels、$\tau_{\text{interval}}=2$、$\tau_{\text{desc}}=0.8$、$\tau_{\text{conf}}=25\%$、300 RANSAC iterations、threshold 0.01）。作者另外定義 Ours (Sim(3)) 作為自家 ablation baseline，將 SL(4) 改回傳統 Sim(3) 對齊，使 SL(4) 的貢獻能被獨立量化。每個結果均為 5 次平均以對抗 RANSAC 隨機性。

§5.2 Pose estimation evaluation 在 7-Scenes 與 TUM RGB-D 上呈現 ATE。論文主張兩件事：在未校準設定下，VGGT-SLAM 與最強 baseline MASt3R-SLAM 持平甚至更好（TUM 上 SL(4) 版本平均誤差 0.053 m 為最佳）；同時誠實揭露失敗案例 TUM floor scene，因 planar degeneracy 導致 homography 不唯一，以及 TUM 360 scene 在小 submap 下因接近純旋轉而提高 outlier 比例。

§5.3 Dense reconstruction evaluation 在 7-Scenes 上回報稠密重建品質，VGGT-SLAM 取得最佳 accuracy 與 Chamfer distance，呼應 Abstract 「improved map quality」的承諾。

§5.4 Qualitative results 透過 Fig. 2 展示 7-Scenes office 場景（8 submaps）與自製 55 公尺辦公走廊（22 submaps、一個 loop closure）的稠密重建與多色 submap pose；並透過 Fig. 1 在刻意把 $\tau_{\text{disparity}}$ 設為 0 的設定下，凸顯 Sim(3) 對齊在 projective ambiguity 下徹底失效，而 SL(4) 仍能正確接合的對照。

§5.5 Ablations 提供三項：(a) loop closure 對 ATE 的顯著改善（含 paired t-test 標註），(b) submap 越多時 loop closure 帶來的誤差下降越大，(c) confidence threshold $\tau_{\text{conf}}$ 在 accuracy/completion/Chamfer 之間的權衡，預設 25% 為平衡點。整章故事邏輯是「先證明達到 SOTA → 再證明 SL(4) 在 Sim(3) 失效處仍能站住 → 最後以消融把核心設計逐一歸因」。

### 3.6 Conclusion / Limitations / Future Work

(450 words)

§6 Limitations 與 §7 Conclusion 在原文出現的順序為「先談限制再做總結」，這是相對少見但對本論文敘事有意義的安排——作者選擇在收尾前先誠實揭示新典範的代價，再把 SL(4) factor graph 的開創性放在最後一段。

§6 一開始重申本作的定位：這是處理 feed-forward scene reconstruction（具體為 VGGT）所內生 projective ambiguity 的全新 SLAM 系統，並坦言「在 SL(4) manifold 上建 factor graph 是 SLAM 問題的新典範，留下大量改進空間」。接著作者列出三類 limitations：

第一類是 planar degeneracy。完整 15-DOF homography 在點皆共面時退化、解非唯一，這正是 §5.2 與附錄 B.1 觀察到 TUM floor 場景發散、$w=1$ 在 floor 與 360 場景數值不穩的根因。作者把這個失敗模式攤開，避免讀者僅看主表的「次佳/最佳」誤判系統穩健性。

第二類是 outlier 敏感度。雖然採用 5-point RANSAC，但 VGGT 的點具有局部一致性，會生成「adversarial outliers」——亦即同向偏移的相關性偽相符——使 RANSAC 難以剔除。作者直接點名 MASt3R-SLAM 的 ray-based matching 對深度誤差具有韌性，作為可借鏡的方向。

第三類是 scene drift。15 DOF 比起 SE(3)/Sim(3) 多出尺度、旋轉、平移以外的「scene perspective」漂移維度，當相對 homography 估錯或 loop closure 間距過長，飄移會跨進透視維度。雖然 loop closure 已實質校正 drift，但這個新類型的 drift 開出一條全新研究路線。

§7 Conclusion 採取「總結 + 展望」雙段格局。總結部分把全文壓縮為一句：以 VGGT 為 backbone、增量式建構未校準單目稠密地圖、局部與全域（含 loop closure）對齊 submaps、並以「首個 SL(4) manifold factor graph SLAM 系統」這個身份標誌收束。第二句把 §1 與 §4.2 的論證結果回扣——作者透過經典多視幾何的視角審視 VGGT 的幾何認知，導出「在一般情形下 submaps 必須以 projective transformation 對齊」這個結論；該結論本身既是方法論的命題，也是建立 SL(4) factor graph 的合法性依據。

展望段給出兩條清楚的 future work 主線：(1) 進一步刻劃「Sim(3) 即足夠」的條件，亦即釐清何時退化為 7-DOF、何時必須升級到 15-DOF；(2) 研究在同一系統中主動切換或混合 Sim(3) 與 SL(4) 優化，使整體 SLAM 系統在 robustness 與 real-time performance 之間取得更好的折衷。這兩條展望直接呼應 §5.2 中觀察到「Sim(3) 在多數 7-Scenes/TUM 場景已具競爭力，SL(4) 的價值在更困難或無 metric prior 的場景才完全釋出」的實證現象，使限制、結論、未來工作三者形成自洽的論述閉環。

## 4. Critical Profile

### 4.1 Highlights

- 首次將前饋式重建模型 VGGT 擴充為可處理長序列的稠密 SLAM 系統,解除了 VGGT 在 RTX 4090 上約 60 張影格的單次推論上限 (p.1, Introduction)。
- 首次以 classical projective reconstruction theorem 重新審視前饋式重建,明確指出在未標定相機下子圖之間的對齊本質上是 15-DOF 的 SL(4) homography,而非 Sim(3) (p.4, §4.2)。
- 提出第一個直接在 SL(4) 流形上進行 factor graph optimization 的 SLAM 後端,並完整給出 15 個 generators、tangent-space 參數化、Exp/Log、adjoint map 與 Levenberg-Marquardt 更新規則 (p.6, §4.4 與 Appendix A, p.13)。
- 利用「相鄰子圖共用同一影格」的構造,獲得稠密對應點而無需額外特徵匹配,直接以 5-point RANSAC + direct linear method 求解相對 homography (p.5, §4.2)。
- 系統不需相機內參、跨影格也不要求一致校正,且完全 *zero additional training* (p.2, Contributions)。
- 在 7-Scenes 上,SL(4) 版本平均 ATE 0.036 m,與最佳 baseline MASt3R-SLAM* 的 0.063 m 相比明顯領先 (Table 1, p.7)。
- 在 TUM RGB-D 上,SL(4) 版本平均 ATE 0.053 m,優於 MASt3R-SLAM* 的 0.060 m,並在 9 個序列中於 360、desk、desk2、rpy、teddy、xyz 等多場景取得最佳或次佳成績 (Table 2, p.8)。
- 在 7-Scenes 稠密重建評估中取得最佳 Accuracy (0.052 m) 與 Chamfer distance (0.055 m),勝過 MASt3R-SLAM* 與 Spann3R (Table 3, p.8)。
- 透過 SALAD 影像檢索加入迴路閉合,實驗顯示 ATE 隨子圖數目增加而下降幅度更大,呈現可擴展性 (Fig. 3a/3b, p.9)。
- 提供 55 公尺辦公走廊長序列定性結果,以 22 個子圖完成全域一致閉環重建,展示遠超 VGGT 原生上限的場景規模 (Fig. 2, p.8)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 在純平面場景下 15-DOF homography 估計具有 degeneracy,作者觀察到 TUM `floor` 序列因大量純平面影像而導致重建發散 (p.8, §5.2; p.9, §6)。
- TUM `360` 在小子圖尺寸時容易遭遇近似純旋轉,導致 VGGT 深度精度下降、5-point RANSAC outlier 比率升高,進一步影響 homography 估計 (p.8, §5.2)。
- 目前的 homography 估計對 outliers 仍脆弱,即使加上 5-point RANSAC,仍可能因 VGGT 局部一致性帶來的 *adversarial outliers* 而失敗 (p.9, §6)。
- 多出的自由度 (15 vs. Sim(3) 的 7) 帶來新的 *scene perspective* 漂移風險,在迴路閉合稀疏或相對 homography 估計不準時尤其明顯 (p.9, §6)。
- 當 `w = 1` 時,TUM 的 `floor` 與 `360` 序列後端會數值不穩定,以致無法輸出對齊結果 (Appendix B.1, p.13)。

#### 4.2.2 Phyra-inferred

- §5.5 ablation 僅就 loop closure on/off 與 τ_conf、submap size 進行掃描,卻沒有把 SL(4) 與 Sim(3) 在「同一序列、同一隨機種子、同一 outlier 比例」的條件下做受控比較,因此論文無法量化 SL(4) 帶來的好處到底發生在哪些子圖配對。
- Fig. 1 與 Appendix C.1 中 Sim(3) 失敗的例子皆把 τ_disparity 設為 0 或 50 來放大 projective ambiguity,而正式評測卻採用 τ_disparity = 25,讀者無法從定量表中看到 SL(4) 在「真實」情境下的實際增益 (p.7 §5.1 vs. p.9 §5.4 vs. p.15 Fig. 4)。
- 主實驗只針對 `w = 32` 報告主表,但 Appendix B.1 顯示 SL(4) 在 `w = 8` 與 `w = 16` 反而比 Sim(3) 差很多 (例如 7-Scenes SL(4) `w = 8` 為 0.084 m vs. Sim(3) 0.039 m),代表 SL(4) 的優勢高度耦合於子圖大小,但論文未說明選 `w = 32` 是否屬於 cherry-picking。
- 沒有報告每秒處理影格數 / GPU 記憶體 / 端到端延遲等任何 runtime 數據,然而 MASt3R-SLAM 的賣點之一是 *real-time*,讀者無從判斷 VGGT-SLAM 是否仍可實時 (整篇論文僅在 §5.1 提及硬體規格 RTX 4090 + 7960X)。
- 標準差只在文字中聲稱「low spread」(p.7, §5.1),正文表格未附 ±std 也沒有顯著性檢定;唯一的 paired t-test 出現在 Fig. 3a 的 LC ablation,並未涵蓋主表的 SL(4) vs. Sim(3) 比較。
- 5-point homography RANSAC 的 inlier 比率、收斂率、迭代次數等中間指標完全缺席,使讀者無法區分「SL(4) 後端有效」與「VGGT 點雲品質夠好」這兩個混合因子。
- 迴路閉合完全依賴 SALAD descriptor + L2 距離 + 固定門檻 τ_desc = 0.8,沒有對 false positive loop closure 的處理機制 (例如 χ² test、switchable constraints),在 SL(4) 上一個錯誤閉合的代價可能遠高於 Sim(3),但論文未驗證魯棒性。
- 「first SLAM on SL(4) manifold」的新穎性主張僅在 Related Work (p.3) 一段文字中以 *to the best of our knowledge* 帶過,沒有與 SL(3) panoramic stitching [21,33,34,40-42,59] 之外更近期的非歐幾何 factor graph 工作做正面比較。

### 4.3 Phyra's Judgment (summary)

真正新的是把 *projective reconstruction theorem* 重新搬回前饋式重建的對齊問題,並以工整的 SL(4) Lie group 推導 (generators、Exp/Log、adjoint、Jacobian) 把後端建成 factor graph;這是有理論深度的貢獻。系統其餘部分 — 子圖切分、SALAD 迴路閉合、Levenberg-Marquardt — 皆為成熟工程組合。最關鍵的未解問題是:在主流 benchmark 上 SL(4) 與 Sim(3) 的差距其實很小 (7-Scenes 0.036 vs. 0.037 m),Sim(3) 失效的場景必須以人工降低 τ_disparity 才能誘發,因此「SL(4) 不只是過度參數化的 Sim(3)」這個核心命題尚未被嚴謹地量化證實。

## 5. Methodology Deep Dive

### 5.1 Method Overview

VGGT-SLAM 將「前饋式稠密重建」與「Lie group 上的全域 SLAM 後端」嫁接成一條完整 pipeline。系統以串流 RGB 影像為輸入,先以 Lucas-Kanade disparity 為門檻挑出 keyframe,將連續的 keyframe 累積到固定大小 $w$ 之後,再串接「上一張子圖最後一個非迴路 keyframe ($M_\text{prior}$)」與「由 SALAD 影像檢索找到的迴路候選 $\mathcal{I}_\text{loop}$」,構成完整影像集 $\mathcal{I}_\text{latest}$,一次餵入 VGGT 推論,得到稠密深度 $D$、信心圖 $C$、相機位姿與內參(§4.1, page 4)。系統由此產出一系列具有重疊影格的子圖 $\mathcal{S}_1, \mathcal{S}_2, \dots$,每張子圖內部以第一張相機為參考座標系。

子圖之間的對齊是 VGGT-SLAM 的核心:作者明確以 Projective Reconstruction Theorem 為理論依據(§4.2, page 4–5),指出未標定相機重建只能在原則上恢復至 15-DOF 的 projective 變換,因此相鄰子圖之間的相對變換 $H_i^j$ 屬於 SL(4) 而非 Sim(3)。由於前後兩張子圖共享同一張 keyframe,該 keyframe 的稠密像素天然提供「免關聯」(association-free) 的 3D 對應點,使作者能直接以 direct linear method 解線性齊次系統 $A_k h = 0$,並以 5-point RANSAC(300 iterations, threshold 0.01)抑制深度錯誤造成的 outlier;最後將解 $H$ 以 $\det(H)^{1/4}$ 正規化使其落在 SL(4) 上。同樣的程序也用於 SALAD 檢索到的迴路候選,產生迴路閉合約束。

後端則建構一個 factor graph,變數為各子圖的「絕對」homography $H_i \in \mathrm{SL}(4)$,因子來自里程約束與迴路閉合約束,以 MAP 形式求解(§4.4, page 6, eq (3))。為使最佳化可在流形上進行,作者導出 SL(4) 的 15 維 tangent-space 表示 $\xi \in \mathbb{R}^{15}$、指數映射 $\mathrm{Exp}: \mathbb{R}^{15} \to \mathrm{SL}(4)$、生成元 $\{G_k\}_{k=1}^{15}$、Jacobian 與 adjoint map $\mathrm{Ad}_H = B^{-1}(H \otimes H^{-\top})B$,並以 Levenberg-Marquardt 反覆更新,在每次迭代以 $H \leftarrow H\,\mathrm{Exp}(\hat{\delta})$ 進行 retraction。整體流程不需任何重新訓練,亦不需相機內參。

### 5.2 Pipeline Diagram with Tensor Shapes

說明:符號 $w$ 為單一子圖的 keyframe 數(實驗中 $w \in \{8, 16, 32\}$);$w_\text{loop}$ 為迴路候選數(預設 $w_\text{loop} = 1$);$H, W$ 為輸入影像高寬;$N_\text{pts}$ 為信心過濾後保留的稠密點數;$N_\text{shared}$ 為兩子圖共享 keyframe 的有效像素對應點數。論文未明確揭露 SALAD 描述子的維度,以 $d_\text{desc}$ 標記為未知。

```
Input: streaming RGB frames  M_t ∈ R^[3, H, W]
   │
   ▼
[Keyframe selector]                                       (Lucas-Kanade disparity vs last keyframe)
   │  keep frame iff disparity > τ_disparity = 25 px
   ▼
Buffer keyframes until |I_latest| = w                     I_latest ∈ R^[w, 3, H, W]
   │
   ├──────────────────────────────────────────────┐
   │                                              ▼
   │                                  [SALAD descriptor per keyframe]
   │                                  desc ∈ R^[w, d_desc]    (d_desc: not specified)
   │                                              │
   │                                              ▼
   │                                  [L2 retrieval over prior submaps S_i,
   │                                   i ∈ {1 : latest − τ_interval},
   │                                   sim > τ_desc = 0.8]
   │                                              │
   │                                              ▼
   │                                  I_loop ∈ R^[w_loop, 3, H, W]
   │                                              │
   ▼                                              │
[Concatenate]   I_VGGT = {M_prior} ∪ I_latest ∪ I_loop  ←────────┘
                I_VGGT ∈ R^[n, 3, H, W],   n = 1 + w + w_loop
   │
   ▼
[VGGT (DINO backbone → Alternating-Attention → DPT + camera heads)]
   │
   ├→ Depth maps        D ∈ R^[n, H, W]
   ├→ Confidence maps   C ∈ R^[n, H, W]
   ├→ Camera poses      P_VGGT ∈ R^[n, 4, 4]
   └→ Intrinsics        K ∈ R^[n, 3, 3]
            │
            ▼
   [Inverse-project D using K, P; prune points with conf < τ_conf · mean(C)]
            │                                        τ_conf = 25%
            ▼
   Submap point cloud   X^S ∈ R^[N_pts, 3]   (in first-camera frame of S)
            │
            ├──────────────────────────────────────────────┐
            ▼                                              ▼
   [5-point RANSAC + direct linear method               [5-point RANSAC on each
    on shared frame M_prior:    A_k h = 0,               loop frame in I_loop:
    300 iters, thr 0.01;                                 same A_k h = 0 procedure]
    h ∈ R^16  →  H ∈ R^[4,4],
    H ← H / det(H)^{1/4}  (project onto SL(4))]
            │                                              │
            ▼                                              ▼
   Odometry factor                                  w_loop loop-closure factors
   H_{latest-1}^{latest} ∈ SL(4) ⊂ R^[4, 4]         {H_loop} ⊂ SL(4)
            │                                              │
            └──────────────────────┬───────────────────────┘
                                   ▼
          [SL(4) factor graph; variables {H_i ∈ SL(4)}_{i=1..M}]
                Cost: Σ_{(i,j)∈L} ‖Log(H_i^{-1} H_j (H_i^j)^{-1})‖²_{Ω_ij}
                Ω_ij = I_15
                                   │
                                   ▼
          [Levenberg-Marquardt on tangent  ξ ∈ R^15]
                ξ^∧ = Σ_k ξ_k G_k  (G_k: sl(4) generators)
                Ad_H = B^{-1} (H ⊗ H^{-⊤}) B,  B ∈ R^[16, 15]
                Retraction:  H ← H · Exp(δ̂)
                                   │
                                   ▼
          Globally consistent map: {H_i}_{i=1..M}, dense reconstruction,
          6-DOF camera trajectory   P_i = (H_i^j)^{-1} P_j
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Incremental keyframe selection and submap assembly

**Function:** 從串流影像挑出 keyframe,並組合下一張子圖的完整輸入集 $\mathcal{I}_\text{latest}$。

**Input:**
- Name: streaming RGB frame $M_t$
- Shape: $\mathbb{R}^{[3, H, W]}$
- Source: 相機影像串流

**Output:**
- Name: 子圖輸入集 $\mathcal{I}_\text{VGGT} = \{M_\text{prior}\} \cup \mathcal{I}_\text{latest} \cup \mathcal{I}_\text{loop}$
- Shape: $\mathbb{R}^{[n, 3, H, W]}$,$n = 1 + w + w_\text{loop}$
- Consumer: §5.3.2 VGGT 推論

**Processing:**

對每張新進影像,以 Lucas-Kanade [36] 估計與「上一張 keyframe」之間的 disparity;若 disparity 超過 $\tau_\text{disparity} = 25$ pixels,則將該影像加入 $\mathcal{I}_\text{latest}$。當 $|\mathcal{I}_\text{latest}|$ 達到上限 $w$,系統將上一張子圖最後一個非迴路 keyframe $M_\text{prior}$ 接於前端,並把 §5.3.5 檢索到的迴路候選 $\mathcal{I}_\text{loop}$ 接於後端,組成下一張子圖的輸入(page 4)。

**Key Formulas:**

無顯式公式;選取準則為 $\text{disparity}(M_t, M_\text{prev kf}) > \tau_\text{disparity}$。

**Implementation Details:**

論文揭露的參數:$\tau_\text{disparity} = 25$ pixels,$w_\text{loop} = 1$,實驗中 $w \in \{8, 16, 32\}$。為了凸顯 projective ambiguity 在 Fig. 1 的影響,該圖實驗將 $\tau_\text{disparity}$ 設為 0(page 9)。

#### 5.3.2 VGGT feed-forward submap inference

**Function:** 對單一子圖的全部影像執行一次前饋推論,取得稠密深度、信心、相機位姿與內參。

**Input:**
- Name: $\mathcal{I}_\text{VGGT}$
- Shape: $\mathbb{R}^{[n, 3, H, W]}$
- Source: §5.3.1

**Output:**
- Name: 深度 $D$、信心 $C$、相機位姿 $P_\text{VGGT}$、內參 $K$
- Shape: $D \in \mathbb{R}^{[n, H, W]}$、$C \in \mathbb{R}^{[n, H, W]}$、$P_\text{VGGT} \in \mathbb{R}^{[n, 4, 4]}$、$K \in \mathbb{R}^{[n, 3, 3]}$
- Consumer: §5.3.3 點雲組裝

**Processing:**

VGGT 以 fine-tuned DINO [47] backbone 將每張影像 tokenize,接續 Alternating-Attention(在 frame-wise 與 global attention 之間切換),最後將 token 餵入 camera head 與 DPT head [52],分別輸出位姿/內參與深度/信心/feature(page 3)。VGGT-SLAM 不執行 VGGT 的 3D point DPT head,因為原作 [68] 已說明用 camera head 的投影矩陣對 $D$ 反投影可獲得更精準的點雲(page 4)。

**Key Formulas:**

無新公式;為對 §3 VGGT review 的直接套用。

**Implementation Details:**

VGGT 受限於 GPU 記憶體,在 24 GB 的 RTX 4090 上單次推論最多約 60 張影像,這是 VGGT-SLAM 必須切分子圖的根本動機(page 1)。實驗硬體為 RTX 4090 + AMD Ryzen Threadripper 7960X(page 7)。論文未揭露 DINO/Alternating-Attention 的隱藏維度與層數。

#### 5.3.3 Dense point cloud assembly with confidence pruning

**Function:** 將 VGGT 的稠密深度反投影成第一張相機座標系下的點雲,並依信心篩選。

**Input:**
- Name: 深度 $D$、信心 $C$、內參 $K$、位姿 $P_\text{VGGT}$
- Shape: 同 §5.3.2
- Source: §5.3.2

**Output:**
- Name: 子圖點雲 $X^\mathcal{S}$
- Shape: $\mathbb{R}^{[N_\text{pts}, 3]}$($N_\text{pts}$ 為通過信心過濾後保留的點數,論文未給定具體數字)
- Consumer: §5.3.4(局部對齊)、§5.3.5(迴路閉合)

**Processing:**

對每張影像逐像素反投影:$X = K^{-1} u\, d(u) $,再以 $P_\text{VGGT}$ 統一到第一張相機座標系。接著保留 $C(u) \geq \tau_\text{conf} \cdot \overline{C}$ 的點,其中 $\overline{C}$ 為當前子圖所有信心圖的平均值(page 4)。

**Key Formulas:**

無顯式公式;遵循標準像素反投影流程,信心門檻為 $C(u) \geq \tau_\text{conf} \cdot \overline{C}$。

**Implementation Details:**

$\tau_\text{conf} = 25\%$ 為論文預設(page 7);Fig. 3(c) 的 ablation 顯示提高 $\tau_\text{conf}$ 會犧牲 completion 換取 accuracy。

#### 5.3.4 Local submap alignment via 15-DOF homography

**Function:** 在共享 keyframe 的稠密像素對應上,直接解出相鄰子圖之間的相對 homography $H_i^j \in \mathrm{SL}(4)$。

**Input:**
- Name: 共享 keyframe 在 $\mathcal{S}_i$ 與 $\mathcal{S}_j$ 中的對應 3D 點 $\{(X^{S_i}_a, X^{S_j}_a)\}$
- Shape: 兩組 $\mathbb{R}^{[N_\text{shared}, 3]}$,$N_\text{shared}$ 由信心過濾後的共同像素數決定(論文未給定)
- Source: §5.3.3

**Output:**
- Name: 相對 homography $H_i^j$
- Shape: $\mathbb{R}^{[4, 4]}$,$\det(H_i^j) = 1$
- Consumer: §5.3.6 後端因子圖(作為 odometry factor)

**Processing:**

對應點滿足 $X^{S_i}_a = H_i^j X^{S_j}_b$(eq (1), page 4,homogeneous coordinates)。每對對應點貢獻一段子矩陣 $A_k$,堆疊成齊次線性系統 $A_k h = 0$(eq (2), page 5),其中 $h \in \mathbb{R}^{16}$ 為 $H$ 的 row-major 攤平向量。最少需 5 對點即可求解,作者以 5-point RANSAC [17] 抑制 VGGT 深度誤差造成的 outlier。求得的 $H$ 因為齊次解只到尺度,需以 $\det(H)^{1/4}$ 正規化,使結果嚴格落在 SL(4)(page 5)。相機位姿則以 $P_i = (H_i^j)^{-1} P_j$ 校正(page 5)。

**Key Formulas:**

對應點關係(eq (1))與線性系統(eq (2))分別為 $X^{S_i}_a = H_i^j X^{S_j}_b$ 與 $A_k h = 0$。SL(4) 投影:

$$
H \leftarrow \frac{1}{\det(H)^{1/4}} H, \qquad \det(H) = 1.
$$

**Implementation Details:**

RANSAC 迭代 300 次,inlier threshold 0.01(page 7);最少樣本數 5 點。論文不需估計關聯,因為兩子圖共享同一張影格,稠密像素對應自動成立。退化情形:平面場景(如 TUM `floor`)會使 5-point RANSAC 無唯一解,造成重建發散(page 7、§6 limitations)。

#### 5.3.5 Loop closure detection and relative homography

**Function:** 透過 SALAD 影像檢索找到非相鄰子圖的迴路候選,並對每個候選估算一個相對 homography 作為迴路因子。

**Input:**
- Name: 各 keyframe 的 SALAD 描述子
- Shape: $\mathbb{R}^{[w, d_\text{desc}]}$($d_\text{desc}$ 論文未明示,見 Implementation Details)
- Source: §5.3.1 中對 $\mathcal{I}_\text{latest}$ 的每張 keyframe 額外計算

**Output:**
- Name: 迴路候選集 $\mathcal{I}_\text{loop}$ 及其對應的 $w_\text{loop}$ 個迴路 homography $\{H_\text{loop}\}$
- Shape: $\mathcal{I}_\text{loop} \in \mathbb{R}^{[w_\text{loop}, 3, H, W]}$;每個 $H_\text{loop} \in \mathbb{R}^{[4, 4]}$
- Consumer: §5.3.1(影像被加入下一次 VGGT 推論)、§5.3.6 後端因子圖

**Processing:**

當 $|\mathcal{I}_\text{latest}| = w$ 時,以 L2 distance 在歷史子圖 $\mathcal{S}_i,\ i \in \{1 : \text{latest} - \tau_\text{interval}\}$ 的 SALAD 描述子中搜尋與當前任一 keyframe 最相似的影格,僅保留相似度超過 $\tau_\text{desc}$ 的前 $w_\text{loop}$ 個影格,構成 $\mathcal{I}_\text{loop}$;這些影格與其餘 keyframe 一同送入 VGGT(§5.3.1)。VGGT 推論完成後,作者直接套用與 §5.3.4 相同的 5-point RANSAC 與 direct linear method,在「迴路影格」與「該影格在原始子圖中的同一張影格」之間求解相對 homography(page 5–6)。

**Key Formulas:**

迴路候選相似度判據:

$$
\mathcal{I}_\text{loop} = \mathrm{topk}_{w_\text{loop}} \big\{ \, M_p \,\big|\, \min_{q \in \mathcal{I}_\text{latest}} \|\mathrm{desc}(M_p) - \mathrm{desc}(M_q)\|_2 < 1 - \tau_\text{desc} \big\}.
$$

迴路 homography 之後的求解流程同 eq (1)(2)。

**Implementation Details:**

$w_\text{loop} = 1$、$\tau_\text{desc} = 0.8$、$\tau_\text{interval} = 2$(page 7)。論文未指出 SALAD 的描述子維度 $d_\text{desc}$,僅說明它「相對於 VGGT DINO token 較小」,且作者選擇 SALAD [26] 而非重用 VGGT 的 DINO token,是為了降低記憶體需求(page 5–6)。Ablation Fig. 3(a)(b) 顯示:加入迴路後 ATE 顯著降低,且子圖數越多、減少幅度越大。

#### 5.3.6 Backend: nonlinear factor graph optimization on the SL(4) manifold

**Function:** 在 SL(4) 流形上聯合最佳化所有絕對 homography $\{H_i\}$,產生全域一致的子圖對齊與相機位姿。

**Input:**
- Name: 相對 homography 集合 $\{H_i^j\}_{(i,j) \in L}$,$L$ 含 odometry 與 loop closure 兩類因子
- Shape: 每個 $H_i^j \in \mathbb{R}^{[4, 4]}$,$\det = 1$
- Source: §5.3.4(odometry)、§5.3.5(loop closure)

**Output:**
- Name: 絕對 homography 集合 $\{H_i\}_{i=1..M}$
- Shape: 每個 $H_i \in \mathbb{R}^{[4, 4]}$,$\det = 1$
- Consumer: 全域稠密重建與 6-DOF 相機軌跡(經由 $P_i = (H_i^j)^{-1} P_j$ 取得位姿)

**Processing:**

在 Gaussian noise 假設下將絕對 homography 估計化為 MAP 問題(eq (3), page 6):

$$
\hat{H} = \underset{H \in \mathrm{SL}(4)}{\arg\min} \sum_{(i,j) \in L} \big\| \mathrm{Log}\!\big( H_i^{-1} H_j \,(H_i^j)^{-1} \big) \big\|^2_{\Omega^H_{ij}},
$$

其中 $\mathrm{Log}: \mathrm{SL}(4) \to \mathfrak{sl}(4)$ 為對映函式,$\Omega^H_{ij} \in \mathbb{R}^{[15, 15]}$ 設為單位矩陣。為求解,作者引入 tangent-space 參數化 $\xi \in \mathbb{R}^{15}$ 與指數對映 $\mathrm{Exp}: \mathbb{R}^{15} \to \mathrm{SL}(4)$,並透過 sl(4) 的 15 個生成元 $\{G_k\}_{k=1}^{15}$ [9] 將向量舉升到 Lie algebra:$\xi^\wedge = \sum_{k=1}^{15} \xi_k G_k$。對量測函式 $h(\xi_i, \xi_j) = \mathrm{Log}(H_i^{-1} H_j)$ 做 first-order Taylor 展開(eq (4)),得到 Jacobian:

$$
J_i = -\mathrm{Ad}_{H_i^{-1} H_j}, \qquad J_j = I_{15 \times 15},
$$

其中 adjoint map 定義為:

$$
\mathrm{Ad}_H = B^{-1}\,(H \otimes H^{-\top})\,B, \qquad B = [\,\mathrm{vec}(G_1)\;\cdots\;\mathrm{vec}(G_{15})\,] \in \mathbb{R}^{[16, 15]},
$$

$\otimes$ 為 Kronecker product(page 6)。線性化之後在線性子問題(eq (5))上以 Levenberg-Marquardt [53] 求 $\hat{\delta}$,並以 retraction $H \leftarrow H\,\mathrm{Exp}(\hat{\delta})$ 將更新拉回流形。

**Key Formulas:**

線性化最小化(eq (5)):

$$
\hat{D} = \underset{\delta \in D}{\arg\min} \sum_{(i,j) \in L} \big\| e_{ij} + J_i \delta_i + J_j \delta_j \big\|^2_{\Omega^H_{ij}}, \qquad e_{ij} = \mathrm{Log}\!\big( H_i^{-1} H_j (H_i^j)^{-1} \big).
$$

Lie 群更新(retraction):$H \leftarrow H\,\mathrm{Exp}(\hat{\delta})$。

**Implementation Details:**

Information matrix 預設為 $\Omega^H_{ij} = I_{15}$,代表所有因子權重相等(page 6)。求解器為 Levenberg-Marquardt(page 6)。Generators $G_k$、Exp/Log 與 adjoint 的完整推導被作者放在 Appendix A(本節摘錄即正文揭露之全部)。論文指出 15-DOF 帶來額外的 scene perspective drift,為未來研究方向(§6)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| 7-Scenes [58] | RGB SLAM 之相機 pose 估計與稠密重建評估 | 7 個室內場景（chess、fire、heads、office、pumpkin、kitchen、stairs） | 僅 test（VGGT-SLAM 為 feed-forward inference，無訓練） |
| TUM RGB-D [63] | RGB SLAM 之相機 pose 估計評估 | 9 個序列（360、desk、desk2、floor、plant、room、rpy、teddy、xyz） | 僅 test |
| Custom office corridor scene | 長軌跡（55 公尺）loop closure 之質性評估 | 單一序列，22 個 submaps（$w = 16$） | 僅 test（質性展示用） |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| ATE RMSE (m) | Absolute trajectory error 之 root mean square error，使用 evo [20] 計算，量化估計軌跡與 ground-truth 之偏差 | yes |
| Accuracy (m) | 重建點雲與 ground-truth 幾何之精度（重建點到 GT 之距離） | no |
| Completion (m) | 重建之完整度（GT 點到重建之距離） | no |
| Chamfer distance (m) | Accuracy 與 Completion 之綜合指標 | no |

### 6.3 Training and Inference Settings

VGGT-SLAM 不訓練模型；它於 inference 時將 VGGT [68] 作為 feed-forward submap 產生器，並在 SL(4) manifold 上執行 factor graph optimization。硬體為單張 NVIDIA GeForce RTX 4090 GPU 配 AMD Ryzen Threadripper 7960X CPU（§5.1）。預設超參數：$w_{\text{loop}} = 1$、$\tau_{\text{disparity}} = 25$ pixels、$\tau_{\text{interval}} = 2$、$\tau_{\text{desc}} = 0.8$、$\tau_{\text{conf}} = 25\%$；homography RANSAC 設定為 300 iterations、threshold 0.01；submap window size $w \in \{1, 8, 16, 32\}$（其中 $w = 1$ 在 TUM 的 floor 與 360 場景因 numerical instability 無法收斂，故僅於 7-Scenes 報告，見 Appendix B.1）。Backend 採用 Levenberg-Marquardt optimizer [53] 在 SL(4) 上更新 $H \leftarrow H \, \mathrm{Exp}(\hat{\delta})$。每組設定平均 5 次 run 之結果以抑制 RANSAC 隨機性（§5.1）。Loop closure 使用 SALAD [26] 影像描述子。Batch size、learning rate schedule、training steps 等項目對 VGGT-SLAM 不適用（無訓練），且 VGGT 本身之預訓練設定 the paper does not specify。

### 6.4 Main Results

7-Scenes ATE RMSE（uncalibrated 設定，單位 m，平均欄位）：

| Method | Avg ATE | Acc. | Complet. | Chamfer | Notes |
|---|---|---|---|---|---|
| DROID-SLAM* [65] | 0.078 | 0.141 | 0.048 | 0.094 | uncalibrated（calibrated 版 0.049） |
| MASt3R-SLAM* [44] | 0.066 | 0.068 | 0.045 | 0.056 | uncalibrated SoTA |
| Spann3R @20 [67] | N/A | 0.069 | 0.047 | 0.058 | 無 ATE |
| Spann3R @2 [67] | N/A | 0.124 | 0.043 | 0.084 | 無 ATE |
| **Ours (Sim(3), $w=32$)** | **0.067** | **0.052** | **0.062** | **0.057** | Sim(3) 變體 |
| **Ours (SL(4), $w=32$)** | **0.067** | **0.052** | **0.058** | **0.055** | 本文方法，Acc. 與 Chamfer 為最佳 |

TUM RGB-D ATE RMSE（uncalibrated 設定，單位 m，平均欄位摘要）：

| Method | Avg ATE | Notes |
|---|---|---|
| DROID-SLAM* [65] | 0.158 | uncalibrated |
| MASt3R-SLAM* [44] | 0.060 | uncalibrated SoTA baseline |
| Ours (Sim(3), $w=32$) | 0.074 | Sim(3) 版本 |
| **Ours (SL(4), $w=32$)** | **0.053** | uncalibrated 設定下整體最佳，亦勝過部分 calibrated 方法 |

主要結論：在 7-Scenes 上 SL(4) 版本與 MASt3R-SLAM 相當，且取得最佳 Accuracy（0.052 m）與 Chamfer（0.055 m）；在 TUM 上 SL(4) 取得 uncalibrated 平均最佳 0.053 m。Sim(3) 變體在許多場景表現亦佳，作者解釋為 VGGT 已能於這些場景透過 learned priors 估計 metric reconstruction（§5.2）。

### 6.5 Ablation Studies

- **Loop closure on/off（Fig. 3a, TUM RGB-D，$w \in \{8, 16, 32\}$）**：加入 loop closure 後 ATE 顯著下降；paired t-test 達 $10^{-3} < p \le 10^{-2}$（標註為 **）。此 ablation 直接診斷 loop closure factor 對全域一致性之貢獻，屬 diagnostic experiment。
- **Loop closure 隨 submap 數量之增益（Fig. 3b）**：submap 數越多時 loop closure 帶來的 ATE 下降幅度越大，驗證 SL(4)-based 全域優化能於更長序列累積更多回環約束的好處——支持「VGGT-SLAM 解決 VGGT 長序列受 GPU 記憶體限制」之主張。
- **Confidence threshold $\tau_{\text{conf}}$（Fig. 3c, 7-Scenes）**：較大 $\tau_{\text{conf}}$ 提高 Accuracy 但降低 Completion，預設 $25\%$ 為兩者之平衡。屬於 hyperparameter sensitivity sweep，介於診斷與調參之間，非核心方法 ablation。
- **Submap window size $w \in \{1, 8, 16, 32\}$（Tables 4, 5, 6, Appendix B.1）**：在 TUM 上 $w = 32$ 對 SL(4) 顯著優於 $w \in \{8, 16\}$（0.053 vs 0.115、0.083），$w = 1$ 於 floor 與 360 場景發散；於 7-Scenes 同樣是 $w = 32$ 為佳。此實驗有效暴露 SL(4) 在小 submap 下對 pure rotation 與 planar scene 的退化敏感度，屬診斷性質。
- **SL(4) vs Sim(3) 變體（貫穿 Tables 1–2、Fig. 1、Appendix C.1）**：直接 isolate 本文核心宣稱——15-DOF homography 對齊 vs 7-DOF similarity 對齊。Sim(3) 在多數量化場景已具競爭力，但在 Fig. 1 與 Appendix C.1 之 tabletop 等案例中無法對齊 submaps，SL(4) 才能修正 projective ambiguity。此為最關鍵之 diagnostic ablation，但量化指標上兩者差距不大，僅在質性案例顯著，因此核心主張的量化證據相對薄弱。

整體而言，loop closure on/off、$w$ sweep、SL(4) vs Sim(3) 為直接針對方法新元件的診斷性實驗；$\tau_{\text{conf}} $ sweep 偏向 sanity check 性質的調參結果。缺少對 RANSAC iterations、$w_{\text{loop}}$、SALAD 換成 VGGT DINO tokens 等設計選擇的 ablation。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 與 uncalibrated 設定下 SoTA MASt3R-SLAM* [44] 直接比較於 7-Scenes 與 TUM RGB-D（Tables 1, 2, 3）。
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — 量化評估涵蓋 7-Scenes 與 TUM RGB-D 兩個 SLAM benchmark，但任務皆為室內 RGB SLAM，未包含戶外、driving、或非 SLAM 之下游任務。
- [covered] Has ablations that diagnose the new components (not just sanity checks) — Fig. 3(a)(b) 之 loop closure ablation 與 Sim(3) vs SL(4) 比較直接診斷本文兩個核心貢獻（SL(4) 對齊與 loop closure factor）。
- [partial] Has a scaling study (size, length, or compute) — Appendix B.1 之 $w \in \{1, 8, 16, 32\}$ 與 Table 7/8 之 submap/loop 數量分析提供軌跡長度層面的 scaling 觀察，custom 55 m corridor (22 submaps) 為長序列示例，但未系統性回報執行時間、記憶體或 throughput 隨 $w$ 與序列長度之變化曲線。
- [missing] Has an efficiency / wall-clock comparison — paper 未報告 VGGT-SLAM 與 MASt3R-SLAM、DROID-SLAM 之 runtime、FPS、或 GPU memory 對比；雖以「VGGT 受限於 60 frames / 24 GB」作為動機，但無對應量化效率表格。
- [covered] Reports variance / standard deviation / multiple seeds where relevant — §5.1 明示因 RANSAC 隨機性報告 5 runs 平均，Fig. 3(a) 以 ** 標記 paired t-test 之 p-value 區間，提供統計顯著性證據。
- [missing] Releases code / weights / data sufficient for reproducibility — 主文與 Appendix 未提及 code、checkpoint 或 project page 之釋出；the paper does not specify reproducibility artifacts。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **首個基於 VGGT 的長序列 SLAM 系統 — 支持**。Fig. 2 (p.8) 的 55 m 走廊以 22 個子圖完成閉環重建,Tables 1–3 在標準 benchmark 也達到具競爭力的結果,確實打破 VGGT 約 60 張影格的硬體上限。
- **指出未標定 VGGT 重建殘留 projective ambiguity,Sim(3) 不足 — 部分支持 (overclaimed in scope)**。Fig. 1 (p.2) 與 Appendix C.1 (Figs. 4–6) 提供清晰的 *qualitative* 證據,但這些示例必須將 τ_disparity 設為 0 或 50 才能誘發;主表中 SL(4) 與 Sim(3) 的差距僅 0.001 m (7-Scenes, Table 1)。論文支持「存在 Sim(3) 失效情形」的弱主張,但未支持「SL(4) 在常態下顯著優於 Sim(3)」的強主張。
- **首個在 SL(4) 流形上的 factor graph SLAM — 支持**。Appendix A (p.13) 列出 15 個 generators 與 (6) 式,§4.4 (p.6) 給出 Eq. (3)–(5) 的完整 MAP 形式與 Jacobian,推導完整可重現,這是論文最堅實的貢獻。
- **與 SOTA uncalibrated SLAM 競爭甚至更佳 — 支持**。Table 1 平均 ATE 0.036 m (vs. MASt3R-SLAM* 0.063 m)、Table 2 平均 0.053 m (vs. 0.060 m)、Table 3 Chamfer 0.055 m 為最佳,在主流公開資料集上的數字確實成立。
- **無需額外訓練、無需相機內參 — 支持**。整個流水線僅在前端使用預訓練的 VGGT、SALAD、DINO,後端為純幾何最佳化,§4 全節未引入任何學習元件。

### 7.2 Fundamental Limitations of the Method

**平面退化是 SL(4) 公式本身的內在問題,非實作 bug**。當所有對應點共面時,(2) 式 *Akh = 0* 的零空間維度上升,15-DOF homography 不再唯一可解;這在室內地板、桌面、牆面等場景無所不在,作者也承認這是 TUM `floor` 失敗主因 (§5.2, §6)。任何純粹基於 5-point linear DLT 的方案都繼承此退化,無法靠增加 RANSAC 迭代次數補救,需要在公式層加入幾何先驗 (例如近似 Sim(3) 偏置項) 才能根治。

**SL(4) 的更高自由度同時放大了 estimator variance**。Appendix B.1 (Tables 4–5) 顯示 SL(4) 在小子圖 (`w = 1, 8, 16`) 時的 ATE 系統性差於 Sim(3);這不是調參問題,而是因為 5-point 線性解的條件數隨自由度上升而惡化,需要更多、更高品質的對應點才能穩定收斂。換言之,SL(4) 在「資料豐富」與「ambiguity 顯著」兩個條件同時滿足時才贏,Sim(3) 反而是低資料情境的更穩健 estimator。

**前端與後端的耦合過緊**。整個 SL(4) 估計完全仰賴 VGGT 輸出的稠密深度,而 VGGT 在純旋轉、低視差或紋理缺乏的場景中本身就不可靠 (§5.2 提到 TUM 360 的純旋轉問題)。一旦深度有系統性偏差,5-point RANSAC 的「inliers」其實是一致地錯,RANSAC 無法偵測這種 *adversarial outliers*,作者也明白指出此風險 (§6)。MASt3R-SLAM 採用的 ray-based matching 是繞過此問題的可行思路,但目前的 VGGT-SLAM 並未具備類似機制。

**全局尺度 / 透視會無界漂移**。Sim(3) SLAM 至少擁有 metric 假設可作為錨,但 SL(4) 在缺乏迴路閉合時,允許整個軌跡沿 shear / stretch / 透視方向滑移,且這種漂移無法靠 odometry 觀察到。Fig. 3b (p.9) 顯示子圖數越多時 loop closure 帶來的 ATE 改善越大,反向說明若 loop closure 缺席,SL(4) 漂移將比 Sim(3) 嚴重得多 — 這是 *more DoF = more ways to drift* 的結構性代價。

### 7.3 Citations Worth Tracking

- **VGGT [68] (Wang et al., 2025, arXiv:2503.11651)** — 核心前端模型,理解其 camera head 與 DPT depth head 的訓練條件,才能判斷何時 projective ambiguity 真的會出現。
- **MASt3R-SLAM [44] (Murai et al., 2024, arXiv:2412.12392)** — 主要 baseline,其 Sim(3) + ray-based matching 設計與本文形成直接對照,且作者明確指出未來可能借鏡其 ray-based formulation。
- **Hartley & Zisserman, *Multiple View Geometry* [25] Ch.10.3** — Projective Reconstruction Theorem 與 4×4 homography 的權威源頭,本文整個動機建立其上。
- **Lovegrove, *Parametric Dense Visual SLAM* [33] (PhD thesis, 2012)** — 唯一明確列出的 SL(3) 在 dense SLAM 上的 factor graph 先例,值得追溯以理解從 SL(3) 到 SL(4) 的延伸是否真為「首次」。
- **Sim-Sync [74] (Yu & Yang, 2024)** — 利用學習式深度與相似群上 *certifiably optimal* 同步的代表作,提供「在 Sim(3) 上做嚴謹最佳化」的另一條可比較路線,有助於評估 SL(4) 是否真的必要。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在標準 benchmark 的「常態」設定 (τ_disparity = 25) 下,SL(4) 相對 Sim(3) 的提升是否具統計顯著性,而非僅來自隨機種子變異?
- [ ] 既然 SL(4) 在小子圖時系統性更差,是否存在一個自適應策略,根據估出的 inlier ratio 或 condition number 動態於 Sim(3) 與 SL(4) 之間切換?
- [ ] 平面退化問題能否藉由在 (2) 式上加入「接近 Sim(3) 的先驗」(例如對 shear/stretch 自由度施加 Tikhonov 正則化) 解決,而不必偵測平面?
- [ ] SALAD 帶來的迴路閉合若給出錯誤匹配,SL(4) 後端會如何失效?是否需要 switchable constraints 或 graduated non-convexity?
- [ ] VGGT-SLAM 的端到端 FPS、GPU 記憶體峰值與 backend 收斂時間在不同 `w` 下的曲線為何?是否仍能宣稱 *real-time*?
- [ ] 採用 MASt3R-SLAM 的 ray-based matching 取代 5-point 點對點 RANSAC,能否同時改善 outlier 容忍度與平面退化?
- [ ] 當 VGGT 已輸出 camera intrinsics 估計時,將其帶入會把 ambiguity 從 SL(4) 退化為 Sim(3) 嗎?論文為何不嘗試這個 hybrid 設定?

### 8.2 Improvement Directions

1. **Hybrid Sim(3)/SL(4) backend with online ambiguity test** (高可行性)。在每對子圖上以 *cheirality + condition number* 判斷 projective ambiguity 是否顯著,顯著時用 SL(4),否則退回 Sim(3);這直接呼應作者在 §7 結論點出的未來方向,且只需在現有 factor graph 中混入兩種 factor 類型,無須重訓任何模型。
2. **Plane-aware regularizer on SL(4)** (中可行性)。在 (3) 式加入 *λ · ‖proj_shear-stretch (Log H)‖²* 之類的軟約束,強迫解在資料不足時退化到 Sim(3) 子流形,可緩解 TUM `floor` 退化,理論上對應於「資料不足時把先驗收緊」的 MAP 操作。
3. **Ray-based homography fitting** (中可行性)。借鑒 MASt3R-SLAM 將深度誤差解析為 ray 方向,可避免 5-point RANSAC 對 VGGT 深度尺度誤差的線性敏感性;對 adversarial outliers 也更魯棒。
4. **Robust loop-closure factors (DCS / GNC / switchable constraints)** (中可行性)。SL(4) 上單一錯誤迴路閉合的損害大於 Sim(3),引入 [Sünderhauf, Olson] 風格的可關閉約束,可在不放慢主流程的前提下提升閉環安全性。
5. **Joint refinement with VGGT camera intrinsics** (低-中可行性)。把 VGGT 輸出的 intrinsics 視為先驗、在 backend 同步精修,理論上能把 ambiguity 從 SL(4) 縮小至 Sim(3),量化「intrinsics 信任度」對所需自由度的影響;需要修改 factor graph 的狀態空間。
6. **Certifiable SL(4) optimization** (低可行性,但科學價值高)。仿照 Sim-Sync [74] 在 Sim(3) 上的 SDP relaxation,推導 SL(4) 上的 convex 鬆弛或 dual certificate,使方案具全域最佳性保證,可徹底解決 LM 對初值敏感的問題。
