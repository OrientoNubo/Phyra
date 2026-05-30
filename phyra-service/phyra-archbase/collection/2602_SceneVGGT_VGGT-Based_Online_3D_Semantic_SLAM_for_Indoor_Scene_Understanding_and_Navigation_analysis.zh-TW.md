<!-- type: paper-read-notes | generated: 2026-05-08 | lang: zh-TW -->

# SceneVGGT — SceneVGGT: VGGT-Based Online 3D Semantic SLAM for Indoor Scene Understanding and Navigation

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | SceneVGGT |
| Paper full title | SceneVGGT: VGGT-Based Online 3D Semantic SLAM for Indoor Scene Understanding and Navigation |
| arXiv ID | 2602.15899 |
| Release date | 2026-02-19 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2602.15899 |
| PDF link | https://arxiv.org/pdf/2602.15899 |
| Code link | https://github.com/HBVC-AI/SceneVGGT |
| Project page | https://hbvc-ai.github.io/SceneVGGT/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Anna Gelencsér-Horváth | Pázmány Péter Catholic University, Faculty of Information Technology and Bionics; Eötvös Loránd University | https://ppke.hu/oktatok/gelencser-horvath-anna-dr | first author; corresponding author; equal contribution |
| Gergely Dinya | Eötvös Loránd University, Budapest, Hungary | — | co-first author; equal contribution |
| Dorka Boglárka Erős | Pázmány Péter Catholic University, Budapest, Hungary | — | co-author |
| Péter Halász | Pázmány Péter Catholic University, Budapest, Hungary | — | co-author |
| Islam Muhammad Muqsit | Pázmány Péter Catholic University, Budapest, Hungary | — | co-author |
| Kristóf Karacs | Pázmány Péter Catholic University, Faculty of Information Technology and Bionics, Budapest, Hungary | https://itk.ppke.hu/en/lecturers | senior author; group lead (AI Laboratory / HBVC-AI) |

### 1.2 Keywords

3D scene understanding, sequential processing, semantic SLAM, spatio-temporal mapping, assistive navigation, VGGT, sliding-window submap alignment, instance tracking

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al., CVPR 2025) | base model | Feed-forward multi-view transformer providing depth/pose estimates that SceneVGGT adapts for streaming SLAM. |
| VGGT-SLAM / VGGT-SLAM 2.0 (Maggio et al., 2025/2026) | baseline | Dense RGB SLAM via overlapping submaps with SL(4) optimization; compared on 7-Scenes pose/reconstruction. |
| StreamVGGT (Zhuo et al., 2025) | baseline | Streaming VGGT with causal attention; SceneVGGT follows its 7-Scenes evaluation protocol. |
| IncVGGT (anon., ICLR 2026 submission) | baseline | Bounded-memory incremental VGGT for long sequences; key memory-efficiency reference. |
| InfiniteVGGT (Yuan et al., 2026) | baseline | Endless-stream VGGT with rolling memory and pruning; SceneVGGT reuses its evaluation code. |
| IGGT (Li et al., 2025) | baseline | Instance-grounded geometry transformer for semantic 3D; SceneVGGT contrasts memory budget and TSR. |
| EmbodiedSAM (Xu et al., 2024) | influence | Online 3D instance segmentation via SAM; motivates SceneVGGT's 2D-to-3D mask lifting. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於室內場景的線上 3D 語意 SLAM,目標是在連續 RGB(-D) 串流上同時完成幾何重建、語意實例追蹤與輔助導航。作者以前饋式多視圖 transformer VGGT 為基礎,解決其記憶體隨序列長度暴增、缺乏時序一致性的限制,提出可長時間運行於單張 RTX 4090(峰值 < 17 GB VRAM)的串流式管線。系統將輸入切成滑動視窗子地圖,以重疊 keyframe 估計區塊間相機位姿,並利用 LiDAR depth 對 VGGT 預測深度做 metric scale grounding 以避免單眼漂移。語意層面則把 2D instance mask 透過 VGGT tracking head 提升到 3D,維持跨區塊一致的 instance ID,並以 Chamfer 距離做重識別、用 confidence decay 進行 RECENT/REMOVED/RETAINED 三態 change detection。最後將物件投影到 RANSAC 估計的地板平面,形成 2D top-down map,支援以 frontier-based exploration 結合語意目標(例如「找空椅子」)的視障輔助導航。研究主題橫跨 3D vision、SLAM、open-set 語意理解與 assistive robotics。

### 2.2 Domain Tags

- Computer Vision
- 3D Scene Understanding
- SLAM
- Robotics / Assistive Navigation
- Semantic Mapping

### 2.3 Core Architectures Used

- **VGGT (Visual Geometry Grounded Transformer)**:作為前饋式多視圖 backbone,提供每張 frame 的相機位姿、稠密深度與置信度,為 SceneVGGT 幾何重建層的核心預測器。
- **VGGT tracking head**:在每個 sliding-window block 內把 2D instance mask 上的取樣點跨 frame 傳播,用以將 2D 語意 lift 到 3D 並維持區塊內 tracklet ID 的一致性。
- **Sliding-window submap alignment with keyframe overlap**:作者提出的串流式幾何模組,將輸入切成大小為 $n$ 的 disjoint block 並重疊前一區塊的 $k$ 個 keyframe(實作為 $k = n = 10$),以重疊 anchor 估計 inter-block pose 變換,使峰值記憶體與序列長度脫鉤。
- **LiDAR-grounded metric scaling**:以遮罩後的 LiDAR depth 與 VGGT 深度的 L2 誤差最小化求出每個 block 的 median scale,套用到外參平移分量與深度圖以恢復 metric scale 並抑制單眼長期漂移。
- **Persistent tracklet memory with Chamfer-distance re-identification**:跨 block 維持一個 inactive tracklet pool,以 KD-tree 計算雙向最近鄰平均距離取較小者作為 Chamfer distance,於 30 cm 門檻下將新 tracklet 與舊物件合併以實現重識別。
- **Confidence-decay change detection**:以 RECENT/REMOVED/RETAINED 三態管理物件,透過將 3D 點反投影回當前視角並結合深度遮擋判斷,對「應可見卻未被偵測」的 tracklet 線性衰減 $c$ 值,$c \to 0$ 時轉為 REMOVED。
- **RANSAC-based floor-plane estimation**:以 RANSAC 從重建點雲擬合地板平面,並用法向夾角 $< 5^{\circ}$、偏移差 $< 0.1\,\text{m}$ 與最近 $l = 5$ 個歷史平面的多數決機制更新參考平面,降低短暫鏡頭抖動影響。
- **Floor-plane top-down projection + frontier-based exploration**:把帶語意的 3D 點雲投影到 2D 網格產生 mean density map,並以形態學膨脹做安全裕度,於目標不可見時退回 frontier-based exploration 完成輔助導航。
- **2D instance segmentor (YOLOv9e via Ultralytics, COCO 預訓)**:在 in-the-wild 評估中作為 2D mask 來源;ScanNet++ 量化評估則改用 ground-truth 9 類 mask 以隔離 segmentor recall 的影響。

### 2.4 Core Argument

作者指出,VGGT 等前饋式多視圖 transformer 雖能在短片段上產生高品質的稠密 3D 重建與相機位姿,但其全注意力架構對序列長度的記憶體與計算需求是平方級成長,且本質上不具跨片段時序一致性,因此無法直接應用於需即時、長時間運作的室內輔助導航。既有改進方向各有缺口:FastVGGT 著重加速、VGGT-SLAM 強化幾何但偏 offline、StreamVGGT/IncVGGT/InfiniteVGGT 解決記憶體但缺語意層的物件持續性,而 IGGT、EmbodiedSAM 則受限於 12–15 frame 的多影格記憶體預算或 mask 時序穩定度。為了同時滿足「bounded memory、metric scale、temporally coherent semantics、可導航」四項條件,作者主張必須把問題拆成三個邏輯上互相依存的模組:(1) 滑動視窗 + keyframe 重疊的子地圖對齊,搭配 LiDAR depth 做 metric grounding,以根本性地切斷記憶體與序列長度的耦合,並消除單眼系統長期漂移;(2) 將 2D instance mask 用 VGGT tracking head 投到 3D,並以持續性 tracklet memory + Chamfer 重識別維持跨區塊的物件 ID,使語意 map 不只「看得到」更能「記得住」;(3) 把帶語意的 3D 點雲投影到 RANSAC 估計的地板平面降到 2D,讓導航在低維可解釋空間中進行,以滿足即時性與安全裕度。這三層設計的必要性在於:任何一層缺失都會破壞輔助導航所需的「即時、可信、可解釋」性質,因而本框架被設計成一條由 geometry → semantics → navigation 的閉環管線,而非單純對 VGGT 做工程性加速。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(165 words)

標題「SceneVGGT: VGGT-based Online 3D Semantic SLAM for Indoor Scene Understanding and Navigation」一次性地把四個關鍵詞綁在一起：底層 backbone 是 VGGT、執行模式是 online、輸出層次是 3D semantic SLAM、應用域是室內場景理解與導航。讀者由此立刻知道這是一篇「把 feed-forward multi-view transformer 改造成可串流、可語義化、可導航」的系統論文，而非新模型。

Abstract 沿著「問題 → 方法 → 結果 → 用途」四步說故事。第一句點明動機：要把 SLAM 與 semantic mapping 合一，服務 autonomous 與 assistive navigation。第二句鎖定技術根源：基於 VGGT，並透過 sliding-window pipeline 解決長序列瓶頸。第三、四句鋪陳兩個核心設計：以 camera-pose transformation 對齊 local submaps 維持幾何一致性；以 VGGT tracking head 把 2D instance mask 提昇到 3D 並保留 temporally coherent identities，從而支援 change detection。第五句把 navigation 收斂為「物體位置投影到估計的 floor plane」這一 proof-of-concept。最後兩句下硬指標：GPU 記憶體峰值 <17 GB 且與序列長度無關、在 ScanNet++ 上具競爭力，且速度足以支援互動式 assistive navigation 配音回饋。Abstract 的關鍵承諾——bounded memory、temporal consistency、互動級延遲——剛好就是後文每個 module 要逐一兌現的，明確地預告了讀者該用甚麼鏡頭審視後續章節。

### 3.2 Introduction

(370 words)

Introduction 的論證鏈條從「應用需求」推到「技術缺口」再推到「系統貢獻」。開篇先把場景訂在 cluttered, unfamiliar, constantly changing indoor environments 的 assistive navigation：系統必須維持 viewpoint 變化與遮蔽下都穩定的 temporally coherent 3D map，並同時承載語義以支援「找空座位、定位物件」這類具體任務；又因輸入是 continuous stream，real-time guidance 帶來低記憶體與低延遲的硬約束。這一段把後文所有設計選擇的評分軸都先豎好——時序一致、語義、串流、bounded memory。

第二段對比 assistive navigation 與 autonomous navigation：前者較寬鬆因為可借用人類操作者的判斷，但又因人為執行與感知資訊引入更高的不確定性。這個對比解釋了為何作者願意採用 proof-of-concept 等級的 navigation module，以及為何強調 human-in-the-loop。

第三段把目光轉向 backbone：VGGT 提供「足夠準確的 depth 與 camera pose」是 fast 3D reconstruction 的好起點，但 directly applying to long sequences 受限於記憶體急速膨脹與缺乏顯式 temporal consistency。這直接點出 SceneVGGT 必須補的兩個洞——`memory-bounded streaming` 與 `temporal coherence`，也預告了 §3.1 的 sliding-window 與 §3.2 的 tracklet 設計各自負責哪一塊。

第四段用四點 contribution 把 paper 的承諾條列化：(1) 透過把 2D instance mask 提昇到 3D 並用 VGGT tracking head 追蹤 instance，達成 3D temporally coherent semantic mapping；(2) 以 persistent object identities 與 timestamps 達成計算高效且時序一致的 change detection；(3) 把物體位置投影到 floor plane 以支援下游 assistive navigation；(4) 一個 proof-of-concept 的 assistive navigation module。Fig. 1 用單一 in-the-wild 辦公室場景同時展示 RGB 與 semantic 重建、navigation map 與規劃路徑，把四個 contribution 視覺化地黏起來，作為「整套 pipeline 確實會跑」的存在性證明。

整段 Introduction 的功能是把後文的閱讀順序固定下來：先講 streaming alignment（補 memory），再講 semantic lifting + change detection（補 temporal consistency），最後接 navigation 落地，與 §3 Methods 的三個小節一一對應。

### 3.3 Related Work / Preliminaries

(340 words)

Related Work 沒有列舉式的 paper bag，而是按照「VGGT 家族要克服甚麼瓶頸」一條主軸組織，把每個被引文獻定位成一個維度的 partial solution，再藉此反襯 SceneVGGT 的差異化定位。

第一段把 baseline 設成 VGGT 自己：feed-forward multi-view transformer 雖讓 dense 3D reconstruction 從一組 RGB 影像中變得可行，不再需要 heavy multi-view optimization，但 compute 與 memory 對序列長度 scale 得很差，且不能直接吃 streaming 資料。這建立了後續所有相關工作存在的理由。

第二段沿著「加速與規模」軸展開：FastVGGT 用 token merging 加速推論；SwiftVGGT 提出可擴展到 large-scale scenes 的變體；LiDAR-VGGT 用 coarse-to-fine 的方式把 LiDAR 與 RGB 融合，提供 metric scale 與 global consistency，但代價是要額外感測器。這幾篇讓讀者理解：scaling 與 metric 是兩個常被分開處理的問題，而 SceneVGGT 同時要兩者。

第三段沿著「長序列與 SLAM」軸展開：VGGT-Long 用 overlapping chunk 與 robust alignment + global adjustment，但 largely offline；VGGT-SLAM 與 2.0 顯式 formulate dense RGB SLAM，於 SL(4) manifold 上做 loop closure，處理 uncalibrated monocular ambiguity；SLAM3R、MUSt3R 則代表 learning-based 的 dense/global alignment 與帶 memory mechanism 的 multi-view stereo。這條軸讓 SceneVGGT 的「online、submap-based、用 LiDAR 做 metric grounding 而非 SL(4) 投影對齊」立場變得清晰。

第四段沿著「online streaming」軸推：StreamVGGT 用 causal attention + streaming state，但 context 仍會累積；IncVGGT 強調 bounded-memory；InfiniteVGGT 則用 rolling memory + pruning 對抗 long-horizon drift。這直接指向 SceneVGGT 在 §4 報告的 17 GB constant-memory 與 7.23 fps 數字要對標誰。

最後兩段把對比拉到語義層：IGGT 學 instance-grounded features 並用 mask 對接 VLM/LMM 做 open-vocabulary，但 multi-frame inference 在 12–15 幀就破 24 GB；EmbodiedSAM 用 SAM 做 online 3D instance segmentation，但 2D-to-3D lifting 對 mask layering/temporal consistency 仍敏感。這兩篇恰好就是 SceneVGGT 在 §4.2 唯一拿來做 context 比較的對手，把 §3.2 的 tracklet 設計動機釘死。

### 3.4 Method (overview narrative)

(1690 words)

Methods 章節以一段非常短的 overview 為總綱，明確宣告 pipeline 由三個 module 組成、按依存關係串接：(1) 以 VGGT 搭 LiDAR grounding，用 sliding-window alignment 與 pose-graph optimization 增量地建 3D map；(2) 把語義整合進這個 mapping 流程，強制 persistent object identities，使同一現實物體在整張地圖上拿到一致的 label，並在物件移動或出現時更新 3D map，達成 temporally consistent mapping；(3) 一個 proof-of-concept navigation module，利用 floor-plane projection 做 dimensionality reduction，借 SLAM back-end 的 robustness 提供 assistive 或 autonomous 導航。Overview 的關鍵設計選擇是把「幾何（streaming alignment）」、「語義（identity + change）」、「下游應用（floor-plane navigation）」分成三個 concern 拆解，並讓每個下層 module 都建立在上一個的輸出上。

§3.1 (Online 3D scene alignment for streams) 為整條 pipeline 鋪好幾何骨架。論文先承認其哲學立場：在 continuous stream 且無 global post-processing 的設定下，採取 pragmatic accuracy over exhaustive reconstruction，目的是支撐 temporally coherent semantic understanding 與 navigation。具體機制是把 stream 切成 contiguous, disjoint blocks of size $n$，每個 window 包含當前 block 加上前一 block 的 $k \le n$ 幀作為 keyframe anchor；作者實驗後選擇 $k = n$，於 RTX 4090 上設 $n=10$。Inter-block pose transform 由 $k$ 個 overlapping anchor 估出，使各 submap 始終對齊到初始的全域 anchor，這同時提供了把 VGGT 用於串流的 memory bound 與 temporal continuity。為解決 monocular VGGT 缺乏 metric scale 的問題，作者用感測器 depth 替 VGGT-predicted depth 做 grounding，並用 combined validity mask 排除（i）VGGT confidence 低於 $c=1.1$ 或落在最低 10% 的像素，與（ii）感測器可靠範圍外的像素；block scale 取「使 masked 預測 depth 與 masked LiDAR depth L2 誤差最小」的逐幀 scale 之中位數，套用於 extrinsic 平移與預測 depth map。最後刻意拋棄 VGGT 的 PCD head，改由 estimated pose + depth 反投 RGB-D，理由是控制誤差來源並維持 metric scale 一致性。

§3.2 (Lifting 2D semantics with change awareness) 在前一節的 metric 3D 之上加一層「物件本體」：每個 real-world object 表示為 3D 點雲，每點帶 instance type 與 ID，並在整段序列上保持一致以定義 global object over time。流程上先在 2D 做 instance segmentation 取得 mask 與 class，輕度 erosion 後做 inverse projection；以 uniform grid-based sampling 抽稀像素，由 VGGT tracking head 在 block 內逐幀 propagate，tracking head 在每個 block 的第一幀非 keyframe 處初始化一次。Tracklet 的定義很嚴格：只有在 block 第一張 keyframe 才能新建，後續幀的 mask 以 propagated points 的多數 track label 賦值，且必須與 mask 的 class 一致，這套 by-construction 的規則保證 cross-block 的 instance 一致性。中途冒出且無 propagated point 的 mask 標為 untracked、不新建 tracklet。為了跨時間缺口或 block 邊界做 re-identification，新 tracklet 與 inactive tracklet 之間用 sparse median-point 點雲的 Chamfer distance 比較，採雙向 KD-tree nearest-neighbor 平均距離取 minimum 以避免 partial observation 被懲罰，閾值 30 cm 以下即合併。Foreground 與 background 點雲分開維護，前景每點帶 class 與 global instance ID 但不存 RGB，避免每次更新都得 re-back-project 全部前景。Change-aware 部分為每個 tracklet 維護「最後觀察到的 frame index」與 confidence $c$，狀態機含 RECENT/REMOVED/RETAINED，每 block 末把 3D 點反投當前視角，若應在視野內卻無偵測就線性衰減 $c$，$c$ 歸零即標 REMOVED 對應真正的場景變化；out-of-view 物件變 RETAINED 並保留當下 $c$。

§3.3 (Navigation) 把上述 3D semantic map 收斂成下游可用的 2D 表徵。作者把問題限制在 flat floor 室內場景，用 RANSAC 從重建的 3D 點雲估 floor plane，每隔幾個 block 重估一次，新平面與當前 reference 的法向量夾角 <5° 且 offset 差 <0.1 m 視為相同；不一致時與最近 $l$ 個估計比較，若多數匹配才更新 reference 並重算 navigation map，$l=5$ 對應約 4 秒視窗以抑制手機抖動。Navigation map 由 3D 點雲投到 2D grid 的 mean point density 累積而成，對 dwell time 較不敏感；reference plane 不變時各 block 直接以同 origin 與 scale 增量融合，變則全部 reproject。地圖以 morphological opening 去噪，每 block 刷新以反映物件狀態變化。Goal selection 採 semantic mask 過濾目標 class、丟棄小 connected component、以離使用者最近的 centroid 為目標；以 morphological dilation 擴張 occupied cell 形成 conservative free-space map，並把 LiDAR 未觀測的 unknown 區標為 non-traversable 但豁免 dilation；無可視目標時退回 frontier-based exploration，並在 unknown area 顯式依賴 human-in-the-loop（如白杖）以降低 assistive 場景的碰撞風險。三個 module 由此完成「streaming geometry → persistent semantics → 2D navigation」的承接。

### 3.5 Experiments (overview narrative)

(730 words)

Results 章節由四個小節組成，整體採用「先衡量幾何骨架、再衡量語義一致性、再用 qualitative 補榜上沒有的能力、最後標出 limitation」的順序，與 §3 Methods 的三個 module 大致一一對應，但故意把「running speed 與 GPU 峰值」這條 cross-cutting 維度貫穿全部表格。

§4.1 (Pose and reconstruction) 採用 7-Scenes 資料集，並沿用 StreamVGGT 的 evaluation protocol 做公平比較：pose 以 RMSE of ATE 衡量，reconstruction 以 Accuracy、Completeness、Normal Consistency 三項衡量。作者直接 build on InfiniteVGGT repository 提供的 evaluation code，並對 stride=2、最多 500 幀的設定做平均與中位數報告。Table 1 把 SceneVGGT、Infinite VGGT、VGGT*、VGGT**、VGGT SLAM、StreamVGGT、IncVGGT 排在一起，並補一欄 GPU model、VRAM、peak VRAM usage 與 speed，特別標註 InfiniteVGGT、IncVGGT、SceneVGGT 三者的 peak GPU memory「effectively independent of sequence length」——這是論文最希望讀者記得的硬指標。作者誠實聲明跨平台不能直接比較絕對速度，只 indicatively 報告，於 RTX 4090 上 SceneVGGT 取得 15 GB peak、7.23 fps、Acc median 0.0086、Compl median 0.0446，相對於 VGGT-SLAM 的 24+ GB 與 6.9 fps 是「以更小記憶體換相當速度與更佳精度」的定位敘事。

§4.2 (Semantics) 切到 ScanNet++ 的 validation 與 test split，刻意「使用 ground-truth instance mask 當作 model prediction 餵給後段」以把語義評估與某個 foundation model 的 recall 解耦，純粹量測自家 tracking + identity 的時序一致性。受限於 VGGT memory footprint 隨每 instance 追蹤點數成長，採 closed-vocabulary 設定、限定 9 個與 MS COCO 重疊的高頻 task-relevant class，並把這個選擇與 human attention 對少數關鍵目標的 prioritization 連結。指標是 dominance ratio 形式的 ID consistency：每個 GT ID 在所有幀中最常見的非零 predicted ID 即為 dominant，回報其覆蓋率，並另外回報「把 mid-block 出現但尚未被指派 tracklet（predicted ID=0）也計入」的版本。Table 2 列出三個 ScanNet++ 場景（09c1414f1b、25f3b7a318、acd95847c5）長度約 1029–1073 幀的結果，without-counting 版 90.14–95.72%、with-counting 版掉到 65.87–74.29%，差距正好量化了 §3.2 中「mid-block 不新建 tracklet」設計的代價。論文也提供 IGGT 的 TSR 98.9% 作 context，但同時點名其 multi-frame inference 在 12 幀就要 20 GB VRAM，以及 SpaTracker+SAM、SAM2 的 23.68%、57.89% TSR 作為 lower bound。完整 SceneVGGT pipeline（含 instance segmentation、labeling、tracking、navigation）多耗 2 GB 把 peak 推到 17 GB，且仍與序列長度無關。

§4.3 (Qualitative results) 補上「benchmark 沒覆蓋」的維度。作者用 Ultralytics 的 YOLOv9e 在 in-the-wild 自拍序列上做 2D segmentation，目的是展示 change detection 與 map update 在自然條件下的行為，這類事件在 ScanNet++ 上不會出現。Plane estimation 與 navigation 同樣以 qualitative 方式呈現，因為 assistive navigation 在這個設定下沒有公認 benchmark；作者選用「找空座位」這個具體任務，承認因為 dataset 不含對 navigation 輸出的執行動作，goal 可能在多個 candidate 間動態切換，但仍足以展示 capability。Runtime 在 1500 幀、stride 2 的 in-the-wild 序列上做 indicative 量測：alignment 階段 126.59 秒（5.92 fps for 750 frames），加 semantics 多 31.35 秒，再加 instance tracking 與 object/change management 多 50.79 秒，total 210.14 秒（3.57 fps），論文評為「足以支援 interactive assistive navigation 並留下 audio feedback 的 headroom」。整節的論證效果是讓讀者把 §4.1 的數字、§4.2 的 ID consistency、§4.3 的 qualitative 行為三者疊起來，得出「一套在 bounded memory 下同時兼顧幾何、語義、互動延遲」的整體圖像，銜接到 §4.4 的 limitation。

### 3.6 Conclusion / Limitations / Future Work

(195 words)

§4.4 用兩句話劃定誠實邊界：當前的 change-aware object memory 雖支援 appearance/disappearance 與 relocation update，但 pipeline 並未顯式建模 continuous object motion 或 fully dynamic scenes；此外作者預告要把 change detection 從「已被 recognize 的 instance」擴張到 unsegmented region 的更新。這直接回應 §3.2 tracklet 設計的兩個結構性限制——只在 block 第一張 keyframe 新建 tracklet、且 foreground/background 二分——並把它們轉成具體的 future work 入口。

§5 Conclusion 把全文重新打包為四件事的排列組合：sliding-window 設計與 camera-pose-based submap alignment 把 VGGT 擴張到 long indoor video stream；逐步整合 LiDAR-derived scale 抑制 monocular 系統典型的長期 drift，同時保留 navigation 所需的 metric consistency；以 VGGT tracking 完成 2D-to-3D semantic lifting，透過 persistent object memory 達成 temporally coherent instance identity 與 change-aware map update；floor-plane projection 提供 compact top-down 表徵以承接下游 assistive navigation。結論段語氣保守，刻意以「practical utility under realistic compute and memory constraints」收尾，把貢獻的價值錨定在「在受限硬體上落地」而非絕對 SOTA，與 §1 對 assistive navigation 的需求設定首尾呼應，也把 §3.2 §3.3 中那些看似工程性的選擇（30 cm Chamfer 閾值、5° 法向量容差、$l=5$ 多數投票、unknown 區不做 dilation 等）一次性地統合進「為 deploy 而生」的整體論述。

## 4. Critical Profile

### 4.1 Highlights

1. 在 RTX 4090 上 VRAM 峰值固定於 17 GB,且與序列長度脫鉤,完整管線實測 7.23 fps(僅對齊階段)、3.57 fps(對齊+語意+追蹤,1500 frames stride 2),足以驅動互動式 assistive navigation(Abstract、Table 1、§4.3)。
2. 在 7-Scenes 上 ATE-RMSE 中位數 0.0213 m、平均 0.0628 m;reconstruction accuracy 中位數 0.0120 m、completeness 中位數 0.0086 m,在 RTX 4090 同級硬體下優於 VGGT-SLAM(median accuracy 0.0173)(Table 1)。
3. 透過 LiDAR depth grounding 把 VGGT 預測深度錨定到 metric scale,根本切斷 monocular VGGT 在長序列上的 scale drift(§3.1)。
4. 採用 sliding-window 加 $k$ 個 keyframe overlap 的子地圖對齊(實作 $k = n = 10$),使每個 block 只需在 $n + k = 20$ frames 上跑 VGGT,把 attention cost 從 $O(T^2)$ 拆成 block 內 $O(n^2)$(§3.1)。
5. 在三個 $\sim 1000$-frame 的 ScanNet++ 場景上,不計 mid-block 新出現物件的 ID consistency 為 90.14%、95.72%、95.56%(Table 2),顯示 keyframe 重疊加 VGGT tracking head 對 cross-block instance 識別的有效性。
6. 引入以 Chamfer 距離(threshold 30 cm)加 per-frame median 點代表的 tracklet 重識別,並用 RECENT/REMOVED/RETAINED 三態機加 confidence linear decay 處理物件 appearance、disappearance、relocation(§3.2)。
7. Foreground 與 background 點雲分離儲存,instance label 與 ID 直接附在 3D 點上,避免每次更新時對整個累積點雲重做反向重投影(§3.2)。
8. RANSAC 平面估計搭配「最近 $l = 5$ 個 block 多數決」的更新策略,容忍手機等手持感測器在 $\sim 4$ 秒內的瞬間抖動(§3.3)。
9. 在無 segmented target 時 fall back 至 frontier-based exploration,把 unknown floor 標為 non-traversable 但跳過 morphological inflation,避免對未觀測區誤殺 free-space(§3.3)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- §4.4: 目前管線「does not explicitly model continuous object motion or fully dynamic scenes」,只能處理 appearance、disappearance、relocation 等離散變化。
- §4.4: change detection 僅限於 recognized instances,unsegmented region 的變化無法捕捉,作者明列為 future work。
- §4.3: runtime「is not benchmarked on a standardized public protocol」,僅以一段 1500-frame in-the-wild 序列做 indicative measurement。
- §4.2: 為避免 foundation-model recall 干擾語意評估,直接餵入 GT instance masks,等於跳過真實 segmentation 品質這一環。
- §4.2: ScanNet++ 評估限制在 9 個與 MS COCO 重疊的 closed-vocabulary 類別。
- §4.2: 與 IGGT 的 TSR 比較中,作者自陳「A direct comparison is not available」,僅引用 IGGT 自報的 98.9% 作為 context。
- Table 1 caption: 各 baseline 跑在不同 GPU(A100、A800、H100、RTX 4090),作者明言「no direct comparison for performance is possible due to hardware differences」。

#### 4.2.2 Phyra-inferred

1. **LiDAR depth grounding 把 SceneVGGT 從「VGGT streaming 改進」悄悄變成「RGB-D 系統」**:作者把 metric grounding 列為 contribution(§3.1)而非 caveat,但 Table 1 上的 InfiniteVGGT、IncVGGT、StreamVGGT 全為 monocular,等於拿 RGB-D 系統去比 monocular SLAM。論文沒有 LiDAR-off 的 ablation,讀者無從判斷 ATE 與 accuracy 改善有多少來自 sliding-window 設計、多少來自額外感測器。
2. **頭條的 ID consistency 數字遮蔽了 mid-block tracking 的設計級失效**:Table 2 顯示一旦把 mid-block 出現的物件納入計算,三個場景的 ID consistency 從 90/95/95% 跌到 74/69/65%,代表約 25–30% 的物件因為「new tracklets only initialized on the first keyframe of each block」(§3.2)而被直接放棄。論文沒有把這個失效模式跟 navigation 成功率做連結,但對 assistive 場景而言這正是最危險的情況(使用者剛轉頭看到的物件)。
3. **Reconstruction accuracy 的 mean 與 median 落差被掩蓋**:SceneVGGT accuracy mean 0.0446 是 median 0.0120 的 3.7 倍,而 InfiniteVGGT 同欄為 mean 0.025、median 0.005,代表 SceneVGGT 在 worst-case frames 的 outlier 顯著多於 InfiniteVGGT。論文敘述只強調 median,未解釋此落差的來源(可能是 sliding-window 邊界、LiDAR shadow,或 keyframe overlap 不足)。
4. **「Robust」斷言只由 3 個 GT-mask 場景支撐**:Table 2 僅含 3 個 ScanNet++ scene,且全部餵 ground-truth instance mask 進入 tracking pipeline,但 deployment 用的是 YOLOv9e+MS COCO。這等於評估了「假設 segmentation 完美時 tracking 多好」,而非「pipeline 在現實 mask 下多 robust」。
5. **第四項 contribution(assistive navigation)在數據上幾乎完全 unsupported**:§3.3 描述了 frontier-based exploration、free-space inflation、最近 seat 選擇,但 §4 對導航只有「visualization video for one scene」與「dynamic goal switching is sufficient to demonstrate the capabilities」,沒有 success rate、SPL、collision count,也沒有人類受測者實驗。
6. **Table 1 跨硬體比較幾乎無方法層意義**:VRAM 與 fps 在 A100、A800、H100、RTX 4090 之間並列,作者也明白這點,但仍把這欄塞進主表並在 abstract 引用「< 17 GB」當賣點,讀者只能解讀為「作者自己設置的 footprint」。
7. **核心超參數無 ablation**:$n$、$k$、Chamfer threshold 30 cm、confidence decay rate、RANSAC plane match thresholds(5°、0.1 m)、$l = 5$ 都是「we settled with」式的 magic numbers,在物件密集場景或快速移動場景下的 sensitivity 完全未檢驗。

### 4.3 Phyra's Judgment (summary)

SceneVGGT 真正具有新意的是 **persistent tracklet memory + Chamfer re-ID + 三態 confidence decay** 這套處理 cross-block 物件持續性的機制,這層在 IncVGGT、InfiniteVGGT 等同類 streaming VGGT 工作裡確實缺位。其餘三個支柱(sliding-window submap alignment、LiDAR metric grounding、floor-plane projection)都是已知技術的合理組合,工程價值高但概念新意有限。最大的 unresolved question 是 mid-block 物件追蹤失效(Table 2 一致性掉到 65–74%)是否會直接破壞 assistive navigation 的可信度,而論文用「GT mask + 3 個場景 + 質性 nav demo」的評估設計恰好讓這個問題無法被檢驗。把 LiDAR 當作 metric scale 來源卻與 monocular baselines 同表並列,也模糊了 SceneVGGT 究竟是 VGGT 的 streaming 改進還是一個 RGB-D SLAM 系統。

## 5. Methodology Deep Dive

### 5.1 Method Overview

SceneVGGT 將原本只能處理短片段的前饋式 multi-view transformer VGGT 改造成可長時間運行的串流式 3D semantic SLAM,核心策略是把任意長度的 RGB(-D) 序列切成大小為 $n$ 的 disjoint blocks,每個 block 額外攜帶 $k \le n$ 個來自前一 block 的重疊 keyframes,於是一次餵給 VGGT 的 pose head 與 depth head 的輸入長度恆為 $n+k$ frames(論文設定 $n=10$, $k=n$),從根本上把 GPU 記憶體與序列長度解耦,使峰值 VRAM < 17 GB 而與序列長度無關(§3.1)。每個 block 的相對位姿透過 $k$ 個 keyframe anchors 被組合到全域軌跡上,並利用 LiDAR depth 對 VGGT 預測深度做 metric scale grounding——以 confidence threshold $c=1.1$ 與感測器有效範圍構造 validity mask,再以使遮罩後預測深度與 LiDAR depth 之 L2 誤差最小的 per-frame scale 之 median 作為 block scale,套用到 extrinsic 的平移分量與深度圖上;point cloud 不走 VGGT 的 PCD head,而是用估計的 pose 與 metric depth 直接 back-project RGB-D frames(§3.1)。

語意層面,作者在每個 block 的第一個非 keyframe 上對 2D RGB 做 instance segmentation 並對 mask 做輕微 erosion,然後以 uniform grid 對每個 mask 取樣稀疏點,透過 VGGT tracking head 把這些被標記 tracklet ID 的點傳播到 block 內其餘 frames;後續 frame 中,每個 mask 以落入其內的 propagated points 之多數 track label 取得 tracklet ID(同時要求 class 一致),由於 keyframe 來自上一 block,跨 block 的 instance ID 一致性 by construction 成立(§3.2)。長時間漂移以 persistent tracklet memory 解決:新 tracklet 與 inactive tracklet 以 per-frame median points 構成的稀疏點雲做雙向 KD-tree nearest-neighbour Chamfer 距離比對,取兩方向均值的最小值,小於 30 cm 即合併;每個 tracklet 維護 last seen frame index 與 confidence $c$,end-of-block 時把所有物件 back-project 進當前視角,若應可見但無對應偵測則對 $c$ 做 linear decay,$c\to 0$ 時轉 REMOVED,出視野則轉 RETAINED 並凍結 $c$,組成 RECENT/REMOVED/RETAINED 三態 change detection(§3.2)。

導航模組假設室內地板平面,採 RANSAC [15] 在重建點雲上估計 floor plane,每數個 block 重新估計一次,以 normal 角度 $<5°$ 與 offset 差 $<0.1$ m 判定 plane 同一性,若新估計與當前不符則與最近 $l=5$ 個歷史估計比對,過半相符才更新並重投影既有 map(§3.3)。將 3D foreground/background 點雲投影到地板網格,以 per-cell 累積點數除以有觀測 frames 數得到 mean density map,morphological opening 去噪,morphological dilation 將佔據格膨脹做出保守 free-space;高度濾波相對 estimated floor 區分 known/unknown floor,unknown 區視為不可通行但不做膨脹。語意目標(例「找空椅子」)先以類別 mask 過濾並丟棄小的 connected components,再選 centroid 距使用者最近者;若目標不可見則退回 frontier-based exploration [16,17] 並以靠近使用者為次要偏好,local navigation 交由 human-in-the-loop(白手杖)以降低碰撞風險(§3.3)。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input RGB-D stream: frames {I_t}_{t=0..T-1}
   ├ I_t (RGB)        : [H, W, 3]      H=?, W=? (the paper does not specify)
   └ D_t^LiDAR        : [H, W]         metric depth from sensor

Stream partitioning (§3.1)
   │ block size n=10, overlap k=n=10
   └→ Window_b = [keyframes from b-1 (k frames) | block_b frames (n frames)]
      shape: [B=1, n+k=20, H, W, 3]

VGGT forward pass per window (depth + pose heads only; PCD head omitted)
   Window_b ──► VGGT(pose head, depth head)
       ├→ poses_pred  : [B, n+k, 4, 4]            SE(3) extrinsics in window frame
       ├→ depth_pred  : [B, n+k, H, W]            up-to-scale depth
       └→ depth_conf  : [B, n+k, H, W]            per-pixel confidence

Metric scale grounding (§3.1, c=1.1)
   depth_pred, depth_conf, D_t^LiDAR
       │ build validity mask M:
       │   M = (depth_conf >= 1.1)
       │       ∧ (depth_conf > 10th-percentile of depth_conf)
       │       ∧ (D_t^LiDAR within sensor reliable range)
       │ per-frame scale s_t = argmin_s ‖ M·(s·depth_pred − D_t^LiDAR) ‖_2
       │ block scale s_b = median_t s_t
       └→ depth_metric = s_b · depth_pred                  : [B, n+k, H, W]
          poses_metric.translation = s_b · poses_pred.t    : [B, n+k, 4, 4]

Inter-block alignment via k overlap keyframes (§3.1)
   poses_metric (k anchor frames overlap with previous block)
       └→ T_{b←b-1} : [4, 4]   relative transform from anchors
          T_b^global = T_{b-1}^global · T_{b←b-1}
          poses_global : [B, n+k, 4, 4]

RGB-D back-projection → incremental point cloud
   (RGB I_t, depth_metric_t, poses_global_t)
       └→ PCD_b (background + foreground split; §3.2)
          background pts : [N_bg_b, 3]
          foreground pts : [N_fg_b, 3 + class_id + global_inst_id]
          (no RGB stored in 3D)

╔═══════════════════════ Semantics branch (§3.2) ═══════════════════════╗
║ 2D instance segmentation per non-keyframe in block_b                  ║
║    I_t ──► seg model (e.g. YOLOv9e on real-world; GT on ScanNet++)    ║
║       ├→ masks_t       : [N_inst_t, H, W]    binary masks (eroded)    ║
║       └→ class_t       : [N_inst_t]                                   ║
║                                                                       ║
║ Uniform grid sampling on first keyframe of block                      ║
║    masks_kf ──► sampled query points                                  ║
║       └→ Q_b : [N_query, 2]   pixel coords with tracklet ID labels    ║
║                                                                       ║
║ VGGT tracking head, initialised once per block at first non-keyframe  ║
║    (Q_b, Window_b) ──► tracked 2D points across (n+k) frames          ║
║       └→ tracks_b : [N_query, n+k, 2]   propagated pixel positions    ║
║                                                                       ║
║ Mask → tracklet assignment (per frame after keyframe)                 ║
║    For each mask_{t,j}: tracklet_id ← majority(track_label of points  ║
║    inside mask_{t,j})  s.t. class consistency holds; else "untracked" ║
║       └→ inst_id_map : [B, n+k, H, W]   per-pixel global instance ID  ║
║                                                                       ║
║ 2D→3D lifting using metric depth + poses                              ║
║    foreground points : [N_fg_b, 3 + class + global_inst_id]           ║
║                                                                       ║
║ Persistent tracklet memory + Chamfer re-identification                ║
║    new tracklet PCD vs. inactive tracklet PCD (per-frame median pts)  ║
║       d = min( mean_KD(A→B), mean_KD(B→A) )                           ║
║       merge if d < 0.30 m                                             ║
║                                                                       ║
║ Change detection state machine (per tracklet)                         ║
║    confidence c ∈ [0,1], states ∈ {RECENT, REMOVED, RETAINED}         ║
║    end-of-block: if in-FoV ∧ not occluded ∧ no detection → c ← c−Δ    ║
║                  if c ≤ 0 → REMOVED;  if out-of-FoV → RETAINED        ║
╚═══════════════════════════════════════════════════════════════════════╝

Floor-plane projection & navigation (§3.3)
   Aggregated PCD (background + foreground)
       └→ RANSAC plane fit every few blocks
          plane π : (n_x, n_y, n_z, d)
          plane validity check: angle(n,n_ref)<5°, |offset diff|<0.1 m;
          else compare against last l=5 estimates, majority vote to update

   Project PCD onto 2D grid aligned with π
       ├→ density_map  : [Gx, Gy]   Σ pts per cell / Σ frames observing cell
       ├→ height_map   : [Gx, Gy]   min height relative to π → known/unknown mask
       └→ obstacle_map : [Gx, Gy]   morphological opening + dilation (known only)

Goal selection (e.g. "find empty seat")
   semantic mask filter on class → drop small CCs → nearest centroid to user
   else frontier-based exploration on free-space + proximity preference
       └→ goal_xy : [2]    in 2D top-down map
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Sliding-Window Submap Construction

**Function:** 把無限長 RGB-D 串流切成大小為 $n$ 的 disjoint blocks,每個 window 額外帶 $k$ 個前一 block 的 keyframe,使得送進 VGGT 的輸入長度恆為 $n+k$,把記憶體與序列長度解耦。

**Input:**
- Name: `{I_t, D_t^LiDAR}`
- Shape: 每 frame `[H, W, 3]` 與 `[H, W]`
- Source: 來自 RGB-D 感測器(論文未指定具體解析度)

**Output:**
- Name: `Window_b`
- Shape: `[B=1, n+k, H, W, 3]`,搭配對應 LiDAR depth `[B, n+k, H, W]`
- Consumer: VGGT pose/depth heads(§5.3.2)

**Processing:**

把當前 block 的 $n$ 個 frames 與前一 block 的 $k$ 個 keyframe 串接成單一 window。$n=10$, $k=n=10$,故 window 長度為 20(§3.1, footnote 1)。Keyframe 角色是 cross-block alignment 的 anchor。

**Key Formulas:**

$$
\text{Window}_b = [\,\text{KF}_{b-1}^{(1)},\dots,\text{KF}_{b-1}^{(k)}\;|\;I_{b,1},\dots,I_{b,n}\,]
$$

**Implementation Details:**

NVIDIA RTX 4090(24 GB)。$k$ 嘗試過不同值,最終 $k=n$(§3.1)。論文未給出具體 $H, W$;$B$ 在串流推論時為 1。

#### 5.3.2 VGGT Pose & Depth Heads with LiDAR Metric Grounding

**Function:** 對每個 window 跑 VGGT 的 pose head 與 depth head 取得相機外參與 up-to-scale depth,然後以 LiDAR depth 推算 block-level metric scale,把單眼預測對齊到 metric units。

**Input:**
- Name: `Window_b`, `D^LiDAR`
- Shape: `[B, n+k, H, W, 3]`, `[B, n+k, H, W]`
- Source: §5.3.1

**Output:**
- Name: `poses_metric`, `depth_metric`
- Shape: `[B, n+k, 4, 4]`, `[B, n+k, H, W]`
- Consumer: inter-block alignment 與 RGB-D back-projection(§5.3.3)

**Processing:**

1. VGGT 推論得到 `poses_pred`, `depth_pred`, `depth_conf`(三者皆覆蓋 $n+k$ frames)。
2. 構造 validity mask:剔除 (i) `depth_conf < 1.1` 或落在所有 confidence 之最低 10% 的 pixel;(ii) 落在感測器可靠範圍外的 pixel(§3.1)。
3. 對每個 frame 解 per-frame scale,使遮罩後 `s · depth_pred` 與遮罩後 LiDAR depth 之 L2 誤差最小化;block scale 取所有 frame scale 之 median。
4. 把該 scale 套用到 extrinsic 的 translation 分量與 depth map 上;**VGGT 的 PCD head 完全跳過**,改以後續模組用估計 pose 與 metric depth 反投影 RGB-D frame 構建點雲(§3.1)。

**Key Formulas:**

$$
M_t = (\text{conf}_t \ge 1.1) \,\land\, (\text{conf}_t > p_{10}(\text{conf})) \,\land\, (D_t^{\text{LiDAR}} \in \mathcal{R}_{\text{sensor}})
$$

$$
s_t = \arg\min_{s} \big\| M_t \odot (s \cdot \hat{D}_t - D_t^{\text{LiDAR}}) \big\|_2,\qquad s_b = \mathrm{median}_t\, s_t
$$

**Implementation Details:**

confidence threshold $c=1.1$;最低 10% absolute filter 是為了避免大多數 depth estimate 不可靠時 alignment 被破壞。論文未給 VGGT backbone 的具體層數或參數量(此處承襲 base model VGGT [1])。

#### 5.3.3 Inter-Block Pose Composition & Incremental PCD

**Function:** 利用 $k$ 個 overlap keyframe 估出當前 block 相對前一 block 的 transform,把當前 block 的相對位姿組合到全域軌跡上,再用估計位姿與 metric depth 反投影 RGB-D 取得 incremental point cloud。

**Input:**
- Name: `poses_metric`, `depth_metric`, `I`
- Shape: `[B, n+k, 4, 4]`, `[B, n+k, H, W]`, `[B, n+k, H, W, 3]`
- Source: §5.3.2

**Output:**
- Name: `PCD_b`(背景 + 前景分開儲存)
- Shape: background `[N_bg_b, 3]`,foreground `[N_fg_b, 3 + class_id + global_inst_id]`
- Consumer: floor-plane navigation(§5.3.6)、tracklet memory(§5.3.5)

**Processing:**

從 window 中 $k$ 個 anchor frame 的相對位姿估計 $T_{b\leftarrow b-1}$,再以 $T_b^{\text{global}} = T_{b-1}^{\text{global}}\cdot T_{b\leftarrow b-1}$ 把當前 block 對齊全域軌跡(§3.1)。然後對 block 內 frame 的每個 valid pixel 用 metric depth 與 global pose 反投影出 3D points。前景(instance segmented)與背景分開維護;前景 point 直接存 3D position + class label + global instance ID,**不存 RGB**,以避免每次更新都對整張累積前景點雲做昂貴的 back-projection(§3.2)。

**Key Formulas:**

$$
\mathbf{X}_t^{\text{world}} = T_t^{\text{global}} \cdot \pi^{-1}(\mathbf{u}, D_t^{\text{metric}}(\mathbf{u}))
$$

**Implementation Details:**

論文未指定 keyframe 重疊位姿估計用的具體 solver(由 VGGT pose head 直接給出 $n+k$ frame 的相對位姿,組合即可)。

#### 5.3.4 2D→3D Semantic Lifting via VGGT Tracking Head

**Function:** 在每個 block 的第一個 keyframe 上初始化 tracklet,以 VGGT tracking head 把稀疏取樣的標記點傳播到 block 內其餘 frame,並用多數投票把 2D mask 對應到 tracklet ID,完成 2D instance mask 到 3D 物件的提升並維持跨 block ID 一致性。

**Input:**
- Name: `masks`, `class`, `Window_b`
- Shape: `masks: [N_inst_t, H, W]`(eroded binary), `class: [N_inst_t]`
- Source: 2D instance segmentation 模型(ScanNet++ 用 GT;in-the-wild 用 YOLOv9e [21])

**Output:**
- Name: `inst_id_map`
- Shape: `[B, n+k, H, W]`(每 pixel 全域 instance ID;背景為 0)
- Consumer: §5.3.3 前景 PCD 構建、§5.3.5 tracklet memory

**Processing:**

1. 對每個 instance mask 做輕微 erosion 以降低反投影邊緣噪音(§3.2)。
2. 在 block 第一個 keyframe 上對每個 labeled mask 做 uniform grid-based sampling,得到 query points $Q_b$,每點繼承所屬 mask 的 tracklet ID(新 tracklet 只在每個 block 的第一個 keyframe 上初始化)。
3. 在每個 block 的第一個非 keyframe 上初始化一次 VGGT tracking head,沿 window 內所有 frame 把 $Q_b$ 傳播。
4. 後續 frame 中,對每個 mask,以落在其內部之 propagated point 的多數 track label 作為 mask 的 tracklet ID,並要求 mask class 與 tracklet class 一致。沒有任何 propagated point 命中的 mask 標為 "untracked"(中途出現的物件),當前 block 不為其新增 tracklet;沒有任何 frame 觀測到的 tracklet 視為 inactive(§3.2)。
5. 由於 keyframes 來自上一 block,跨 block 的 instance ID 一致性 by construction。

**Key Formulas:**

$$
\text{id}(m_{t,j}) = \mathrm{mode}\big\{\,\text{track\_id}(p)\;\big|\;p \in \text{tracks}_{t},\, p \in m_{t,j}\,\big\}\ \text{s.t. class}(m_{t,j}) = \text{class}(\text{tracklet})
$$

**Implementation Details:**

評估時類別限制為與 MS COCO [20] 重疊的 9 個高頻、任務相關類別(§4.2),以維持有限記憶體預算。Uniform grid sampling 的具體 stride 論文未指定。

#### 5.3.5 Persistent Tracklet Memory & Change Detection

**Function:** 維護所有曾出現物件的長時記憶,以 Chamfer 距離做跨 block / 時間缺口的 re-identification,並以 confidence decay 把每個 tracklet 標記為 RECENT / REMOVED / RETAINED 三態,支援場景變化更新。

**Input:**
- Name: 新 tracklet 與 inactive tracklet 之 sparse PCD
- Shape: 每 tracklet 為 per-frame median points 構成的稀疏點雲 `[N_pts, 3]`
- Source: §5.3.4 lifted 前景點雲

**Output:**
- Name: `tracklet_state`
- Shape: 每 tracklet 一個 state ∈ {RECENT, REMOVED, RETAINED} 與 confidence $c \in [0,1]$
- Consumer: §5.3.6 navigation map(只把 RECENT/RETAINED 投影成障礙)

**Processing:**

1. **Re-identification(§3.2):** 對每個新初始化的 tracklet,將其 sparse PCD(由 per-frame instance point cloud 的 median points 組成)與所有 inactive tracklet 的 sparse PCD 用 KD-tree 計算雙向最近鄰平均歐氏距離;最終距離取兩方向均值的最小值,以避免懲罰部分觀測。距離 $< 0.30$ m 即合併兩 tracklet ID。使用 median points 同時減輕「物件含洞」造成的反投影偽影。
2. **Three-state change detection(§3.2):** 每個 tracklet 維護最後觀測 frame index 與 confidence $c$。本 block 中觀測到的物件 RECENT,$c=1$。Block 結束時把所有物件 3D points 反投影到當前視角,用 depth image 檢查是否被遮擋;若應可見但無對應偵測,則 $c$ 做 linear decay,$c\le 0$ 轉 REMOVED(對應真實的場景變化);out-of-view 則轉 RETAINED 並凍結當前 $c$。

**Key Formulas:**

$$
d_{\text{Cham}}(A,B) = \min\!\Big(\tfrac{1}{|A|}\sum_{a\in A} \min_{b\in B}\|a-b\|_2,\ \tfrac{1}{|B|}\sum_{b\in B} \min_{a\in A}\|b-a\|_2\Big)
$$

$$
c_{t+1} =
\begin{cases}
1, & \text{if observed in current block (RECENT)}\\
c_t - \Delta, & \text{if in-FoV} \land \text{not occluded} \land \text{no detection}\\
c_t, & \text{if out-of-FoV (RETAINED)}
\end{cases},\ \text{REMOVED if } c \le 0
$$

**Implementation Details:**

merge threshold 30 cm。論文未給出 $\Delta$ 的具體數值(僅描述為 linear decay)。Chamfer 距離以 KD-tree 加速。

#### 5.3.6 Floor-Plane Projection & Navigation

**Function:** 把帶語意的 3D 點雲投影到 RANSAC 估計的地板平面降到 2D top-down map,並結合 frontier-based exploration 與語意目標選擇,輸出可供輔助導航使用的 free-space map 與 goal。

**Input:**
- Name: 累積 PCD(背景 + 前景,前景帶 class 與 instance ID)
- Shape: `[N_total, ≥3]`
- Source: §5.3.3 + §5.3.4 + §5.3.5

**Output:**
- Name: `obstacle_map`, `goal_xy`
- Shape: `[Gx, Gy]`,`[2]`
- Consumer: 下游 audio-feedback assistive navigation 模組(proof-of-concept,§3.3)

**Processing:**

1. **Floor estimation(§3.3):** 每隔幾個 block 用 RANSAC [15] 對重建點雲擬合一個地板平面 $\pi:\,n^\top x + d = 0$。新估計與當前 reference plane 滿足 $\angle(n_\text{new}, n_\text{ref}) < 5°$ 且 $|d_\text{new}-d_\text{ref}| < 0.1$ m 視為同一平面;否則與最近 $l$ 個歷史估計比對,若多數相符則更新 reference plane 並對所有累積點重新投影、重算 navigation map。輔助導航 benchmark 設 $l=5$(對應 5 個 block、約 50 frames、~4 秒),以抑制短促手機晃動的影響。
2. **Density / known-floor maps(§3.3):** 把 3D 點雲投影到對齊 $\pi$ 的 2D 網格;density map 對每格累積 $\sum$ points / $\sum$ frames-with-any-observation 得到不受物件停留時間影響的 mean map;用 morphological opening 去噪;每 block 重新刷新以反映 change detection 結果。known/unknown floor 由 minimum-height map 對 $\pi$ 做 height-based 二值化。
3. **Obstacle inflation:** 對「已知 floor + 已偵測物件」的 occupied cell 做 morphological dilation 形成保守 free-space;unknown floor 視為不可通行但**不**做膨脹(因其本身已不可走)。
4. **Goal selection(§3.3):** 以類別 mask 過濾場景(例如 "chair"),丟棄小的 connected components 抑制偽偵測,選 centroid 距使用者最近者為 goal。若無目標可見,退回 frontier-based exploration [16,17],以靠近使用者作為次要偏好;unknown 區內局部導航交由 human-in-the-loop(白手杖)以降低碰撞風險。

**Key Formulas:**

$$
\pi:\ \hat n^\top x + \hat d = 0,\quad (\hat n,\hat d) = \mathrm{RANSAC}\big(\{\mathbf{X}_i\}\big)
$$

$$
\rho(g) = \frac{\sum_{t}\#\{p\in\mathbf{X}_t : \mathrm{proj}_\pi(p)=g\}}{\sum_{t}\mathbb{1}[\,\exists p\in\mathbf{X}_t,\ \mathrm{proj}_\pi(p)=g\,]}
$$

**Implementation Details:**

plane-equality thresholds:angle $5°$、offset $0.1$ m;歷史視窗 $l=5$ blocks(50 frames, ~4 s)。論文未指定 grid resolution、dilation kernel size 或 morphological opening kernel size。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| 7-Scenes [18] | Pose accuracy 與 reconstruction 評估（ATE、Acc、Compl.、NC） | 以 stride=2、最多 500 frames 為單位的序列 | test（依 StreamVGGT [10] 的 evaluation protocol） |
| ScanNet++ [19] | Semantic ID consistency 評估（lift 2D GT instance masks 至 3D 並追蹤 tracklet） | 三個場景（`09c1414f1b`、`25f3b7a318`、`acd95847c5`），長度約 1029–1073 frames，stride=1 | val + test split 中隨機挑選的 office / apartment 場景 |
| In-the-wild 自錄序列 | Qualitative 2D segmentation、change detection、map update、navigation 示範 | 代表性序列約 1500 frames（stride=2，等效 750 frames） | 僅作為 qualitative + runtime 量測，無 train/val/test 切分 |

備註：MS COCO [20] 僅作為 YOLOv9e [21] 預訓練分類體系（與 ScanNet++ 評估時 9 個 task-relevant 類別的對齊依據），本文未在 COCO 上訓練或評估，故不列入。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| ATE RMSE (m) | Average Trajectory Error 的 Root Mean Square Error，量測 pose accuracy；報告 mean 與 median | yes |
| Accuracy (Acc) | Reconstruction 點雲與 ground truth 之間的 mean distance（accuracy 方向） | yes |
| Completeness (Compl.) | Reconstruction 點雲對 ground truth 的覆蓋距離（completeness 方向） | yes |
| Normal Consistency (NC) | 重建表面法向量與 ground truth 法向量的一致性 | no |
| Peak GPU VRAM (GB) | 在 300-frame 序列上實測的尖峰顯存佔用，用以驗證「memory 不隨序列長度成長」之主張 | yes |
| Speed (fps) | 在 300-frame 序列上實測的處理速度，作為線上 / 互動式可行性指標 | yes |
| ID Consistency w/o (%) | 對每個 ground-truth track，跨 frames 出現次數最多的非零 predicted ID 之佔比（不計 mid-block 才出現的物件） | yes |
| ID Consistency w (%) | 同上，但將 mid-block 已語意偵測但尚未指派 tracklet（predicted ID = 0）的情況一併計入 | no |
| Temporal Success Rate (TSR) | IGGT [13] 中提出的時序追蹤成功率；本文僅作為 context 引用，未在 SceneVGGT 上量測 | no |
| Dominance ratio | 用於計算 ID consistency 的中介量：每條 GT track 之 dominant predicted ID 佔比 | no |

### 6.3 Training and Inference Settings

- **訓練**：本文未訓練任何新模型；SceneVGGT 直接以預訓練 VGGT [1] 的 pose、depth 與 tracking head 進行 feed-forward 推理，2D segmentation 採用 MS COCO 上預訓練的 YOLOv9e [21]（Ultralytics [22]）。因此 batch size、optimizer、learning rate schedule、training steps 等皆 the paper does not specify。
- **硬體**：主要實驗於 NVIDIA RTX 4090（24 GB VRAM）。Table 1 中 baseline 因來自原文獻而使用不同硬體（A100 80 GB、H100 80 GB、A800 40 GB），作者明確指出「no direct comparison for performance is possible due to hardware differences」。
- **Sliding-window 設定**：block size $n = 10$，跨 block 重疊 anchor frames $k = n = 10$（作者試過不同 $k$ 後選定此值）。
- **Depth 過濾**：以 VGGT depth confidence 門檻 $c = 1.1$、外加最低 10% 分位數的相對門檻，以及 LiDAR 可靠工作範圍，構成 combined validity mask；以 masked depth 對 LiDAR depth 取 per-frame L2 最小化、跨 frame 取 median 得到 block scale，並套用於 extrinsics 平移分量與 predicted depth。
- **Tracking**：VGGT tracking head 於每個 block 的第一個 non-keyframe 初始化一次；mask 上以 uniform grid sampling 取點傳播；mask 與 tracklet 之 ID 指派需 class consistency 一致。
- **Re-identification**：以 Chamfer distance（KD-tree 雙向最近鄰平均後取最小值，避免懲罰部分觀測）比對新 tracklet 與 inactive tracklet，閾值 30 cm 以下則合併。
- **Object state 機制**：以 RECENT / REMOVED / RETAINED 三態管理；偵測到應可見卻無 association 時對 confidence $c$ 做線性 decay，$c \to 0$ 時轉 REMOVED。
- **Floor plane 與 navigation**：以 RANSAC [15] 估計 floor plane；新舊平面視為相同需法向量夾角 $< 5^\circ$ 且偏移差 $< 0.1\,\text{m}$；以最近 $l = 5$ 個 block estimates（約 50 frames、$\sim 4$ 秒）做 majority vote 才更新；2D map 以 morphological opening 去噪、以 dilation 擴張障礙；未觀測 floor 由 minimum-height map 相對 floor plane 的 height-based filtering 得二值 known/unknown mask；無目標可見時退回 frontier-based exploration [16, 17]。
- **語意評估設定**：採用 closed-vocabulary（與 MS COCO 重疊的 9 個 task-relevant 類別），以 ScanNet++ ground-truth instance masks 作為輸入，以排除 foundation model recall 對結果的影響；ScanNet++ 評估 stride = 1，使用 10 個 keyframes。
- **Inference 量測**：1500-frame、stride=2（等效 750 frames）序列上：alignment 126.59 s（5.92 fps）、+semantics 31.35 s、+instance tracking 與 change management 50.79 s，總計 210.14 s（3.57 fps）。完整 pipeline 尖峰 VRAM 17 GB，獨立於序列長度。

### 6.4 Main Results

7-Scenes pose 與 reconstruction（最多 500 frames、stride=2；GPU/Speed 標準化於 300-frame 序列），以及 SceneVGGT 自報之 17 GB total peak VRAM（含 semantics + tracking + navigation）：

| Method | ATE Mean (m) | Acc Mean | Compl. Mean | NC Mean | Peak VRAM | Speed (fps) | Hardware |
|---|---|---|---|---|---|---|---|
| Infinite VGGT [12] | 0.043 | 0.025 | 0.561 | – | 14.49 GB | 5.95 | A100 (n/a cap) |
| VGGT* [12 報告] | 0.0055 | 0.0067 | 0.948 | – | 60+ GB | – | A100 80 GB |
| VGGT** [11 報告，sparse sampling] | 0.087 | 0.091 | 0.787 | – | – | 8.53 | H100 80 GB |
| VGGT-SLAM [6]（SL(4), w=16，本文自測） | 0.067 | 0.0173 | 0.612 | – | $>$ 24 GB | 6.9 | RTX 4090 24 GB |
| StreamVGGT [10] | n/a | 0.0241 | 0.915 | – | 80+ GB | 2.16–2.2 | A800 40 GB |
| IncVGGT [11] | n/a | 0.0266 | 0.901 | – | 9 GB | 11.74 | A100 80 GB |
| **SceneVGGT (alignment only, 本文)** | **0.0628** | **0.0120** | **0.5775** | – | **15 GB（pipeline 全開 17 GB）** | **7.23** | **RTX 4090 24 GB** |

註：表 1 NC 欄位並非所有 baseline 皆報告（Infinite VGGT 報 NC1）；Acc/Compl. 欄位除上表 mean 外亦提供 median（SceneVGGT 為 0.0213 / 0.0086）。

ScanNet++ semantic ID consistency（10 keyframes、stride=1；GT masks 作輸入）：

| Scene | Length (frames) | ID cons. w/o | ID cons. w |
|---|---|---|---|
| **09c1414f1b** | **1073** | **90.14%** | **74.29%** |
| **25f3b7a318** | **1054** | **95.72%** | **69.29%** |
| **acd95847c5** | **1029** | **95.56%** | **65.87%** |

Context（非直接可比；引自 IGGT [13] 文獻）：IGGT TSR 98.9%（但 multi-frame inference 限制在 $\sim 12$ frames、20 GB VRAM 內），SpaTracker+SAM 23.68%、SAM2 57.89%。

主要主張之佐證：(i) SceneVGGT 在 RTX 4090 上達到 ATE mean 0.0628 m、Acc mean 0.0120、總 pipeline VRAM 17 GB 不隨序列長度成長；(ii) ID consistency 在三個 ScanNet++ 場景上 w/o 介於 90–96%、w 介於 66–74%；(iii) 1500-frame 序列上端到端 3.57 fps，足以支援互動式 assistive navigation。

### 6.5 Ablation Studies

本文未提供傳統意義上的元件消融表。可被視為「設定研究」或「敏感度檢查」的有：

- **Anchor 重疊量 $k$**：作者敘述「We have experimented with different values of $k$, and settled with $k = n$」，但未報告各 $k$ 對 ATE / Acc / Compl. 的數值差異。屬於 sanity check，未診斷 overlap 對 inter-block alignment 漂移的具體貢獻。
- **ID consistency w/o vs w**：差距（如 09c1414f1b：90.14% → 74.29%；25f3b7a318：95.72% → 69.29%）可視為「mid-block 才出現的新物件未被當前 block 初始化新 tracklet」此設計選擇造成的代價，間接量化了「new tracklet 僅在 block 第一個 keyframe 建立」這條規則的影響；但作者未直接以「移除此規則」做對照，因此只能算 partial diagnostic。
- **Depth confidence 門檻 $c = 1.1$、最低 10% 分位、re-ID Chamfer 30 cm、平面相同性 $5^\circ$ / $0.1\,\text{m}$、majority window $l = 5$**：均為定值報告，未提供敏感度掃描。
- **完整 pipeline 額外開銷拆解**：alignment 126.59 s、+semantics +31.35 s、+tracking & change mgmt +50.79 s（總 210.14 s / 3.57 fps），以及 17 GB 總 VRAM 中 semantics + tracking + navigation 額外佔 2 GB。屬效率拆解而非診斷新元件之必要性。

整體而言，現有「ablation」多為 sanity check 與設定報告，未針對「LiDAR grounding」「persistent object memory / Chamfer re-ID」「change-aware state machine」「floor-plane majority update」等核心新元件做開關對照，無法回答這些元件各自對最終 ATE、Acc、ID consistency 的邊際貢獻。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline (a current SoTA on the chosen task) — Table 1 對齊 StreamVGGT、IncVGGT、Infinite VGGT、VGGT-SLAM、原始 VGGT，但作者自承「no direct comparison for performance is possible due to hardware differences」，且 SceneVGGT 之 ATE 0.0628 與 VGGT* 0.0055、Compl. 0.5775 與多數 baseline 0.78–0.94 相比明顯落後，未在主指標上贏過 SoTA。
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — pose / reconstruction 用 7-Scenes，semantic ID consistency 用 ScanNet++，navigation 用 in-the-wild 自錄序列，跨任務但每項評估規模小（ScanNet++ 僅 3 個場景、navigation 僅 qualitative）。
- [missing] Has ablations that diagnose the new components (not just sanity checks) — 未對 LiDAR grounding、Chamfer re-ID、RECENT/REMOVED/RETAINED state machine、floor-plane majority window 等核心新元件做開關對照，僅有 $k = n$ 的設定描述，屬 sanity check。
- [partial] Has a scaling study (size, length, or compute) — 強調 peak VRAM 與序列長度無關，並在 1500-frame in-the-wild 序列上量測端到端 runtime，但未提供「序列長度 vs ATE / drift / VRAM」的掃描曲線。
- [covered] Has an efficiency / wall-clock comparison — Table 1 並列各方法之 Peak VRAM 與 fps（標準化於 300 frames），並另行拆解 1500-frame 序列上各模組耗時（126.59 / +31.35 / +50.79 s）與總 17 GB pipeline VRAM。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 全文僅報 mean / median，無 std、無多 seed，ScanNet++ 僅單次 run、單一 stride、單一 keyframe 數。
- [partial] Releases code / weights / data sufficient for reproducibility — 第一頁列出 project page & code 連結 `https://hbvc-ai.github.io/SceneVGGT/` 並提供 supplementary 視覺化影片（Scene 09c1414f1b），但本文未陳述 license、weights 釋出範圍或 in-the-wild 資料是否公開。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

論文於 §1 列出四項 contribution,加上 abstract 隱含的 bounded-memory 主張,逐項評估:

1. **3D temporally coherent semantic mapping by lifting 2D instance masks into 3D and tracking instances using the VGGT tracking head**: **partially supported**。Table 2 顯示在 keyframe-起源物件上 ID consistency 達 90–95%,確實證明 tracking head 加 tracklet memory 可維持跨 block ID;但 mid-block 物件的一致性掉到 65–74%,且只在 3 個 GT-mask 場景上量測,「temporally coherent」對連續 1000-frame 串流中約 25–30% 的物件並不成立。
2. **Computationally efficient, temporally consistent change detection enabled by persistent object identities and timestamps**: **partially supported**。RECENT/REMOVED/RETAINED 三態機與 confidence decay 在 §3.2 完整描述,但 §4 對 change detection 的量化只剩 in-the-wild 質性影片,沒有 precision/recall on appearance/disappearance/relocation 事件;「efficient」也只能間接從整體 17 GB 與 7.23 fps 推得,而非直接量到 change-detection 模組本身的 cost。
3. **Floor-plane projection of object locations to support downstream assistive navigation**: **mechanism-level supported, outcome-level not**。RANSAC 平面、5° 與 0.1 m 多數決更新、型態學 inflation 在 §3.3 流程清楚,但「supports downstream navigation」的 evidence 只有一段影片,屬於可信的設計但非實證的成果。
4. **A proof-of-concept assistive navigation module**: **overclaimed as a top-level contribution**。沒有 success rate、SPL、collision rate,沒有人類受測者實驗,把它與其他三項並列為 contribution 不符合一般 SLAM/navigation 論文的 evidence 標準。
5. **Bounded memory regardless of sequence length**(abstract 與 Table 1 caption): **supported within tested range**。Table 1 已標註「peak GPU memory is effectively independent of sequence length」,但實測長度只到 500 與 1500 frames 兩點,並未證明真正的 endless 行為(InfiniteVGGT 才是 endless 主張)。

### 7.2 Fundamental Limitations of the Method

**LiDAR 依賴是架構級限制,而非工程細節**。§3.1 把 LiDAR depth 嵌入 block 內 per-frame scale 估計、全域 scale 校正、validity mask 與 sensor operating range 過濾這條主路徑;一旦移除 LiDAR,整個 pipeline 會回到 monocular VGGT 的 scale ambiguity 並失去 absolute units。也就是說,SceneVGGT 不是「monocular 也能跑、加 LiDAR 更好」的系統,而是「沒 LiDAR 就壞掉」的系統,這在「VGGT 的 streaming 改進」這個論述下是一個概念性 mismatch,不是調參能解決的。

**Mid-block 物件無法獲得 tracklet 是設計級盲點**。§3.2 明確規定「new tracklets are initialized only on the first keyframe of each block」,因此任何在 keyframe 之間出現的物件會被標為 untracked,直到下一個 block 的第一個 keyframe 才有可能被 tracklet 化。這在 assistive navigation 中正好對應最糟情境:使用者剛轉頭、剛走進新空間 1 秒內看到的椅子、門、人,很可能落在 untracked 區。要修復必須改寫 tracklet initialization 規則(例如引入 mid-block 候選池),屬於設計修改而非超參數調整。

**評估設計把語意品質與 segmentation 品質徹底解耦**。§4.2 餵入 ScanNet++ GT instance mask 跑 ID consistency,但 §4.3 deployment 用 YOLOv9e。當實際 segmentation mask 在 frame 之間 wobble、漏物件、邊界不穩,Chamfer 30 cm 重識別、confidence decay、RANSAC plane fit 都會被連動干擾,但論文沒有對應的 metric 設計可以定位這些干擾。這是評估架構的根本問題,不是「未來補做 ablation」可以掩過的。

**Floor-plane 假設限制了「indoor scene understanding」的廣度**。§3.3 開頭直接寫「we restrict our setting to indoor environments with a flat floor plane」,排除了樓梯、坡道、多層空間、戶外、不平地面;對 assistive navigation 的視障使用者而言,樓梯與門檻偵測恰好是核心需求。Top-down 投影本身也丟失了 3D 障礙(低矮桌、空中懸掛物)的高度資訊,而這些對 collision risk 高度相關。

### 7.3 Citations Worth Tracking

- **IncVGGT** (Anonymous, ICLR 2026 submission, [11]): SceneVGGT 在 streaming 與 bounded-memory 那一面最直接的對手,在 A100 上只用 9 GB VRAM、11.74 fps,reconstruction accuracy median 0.0266 與 SceneVGGT 0.0120 處於同一量級。讀完才能判斷 SceneVGGT 的優勢有多少來自 LiDAR、多少來自 sliding-window 設計本身。
- **IGGT** (Li et al., 2025, [13]): 作者自承沒做直接比較,但 IGGT 的 TSR 98.9% 是 SceneVGGT 暗示對標的數字。要評估 mid-block tracking 失效是否是 SceneVGGT 落後的主因,必須讀懂 IGGT 的 instance-grounded feature clustering 如何處理 mid-clip 物件出現。
- **InfiniteVGGT** (Yuan et al., 2026, [12]): SceneVGGT 直接 reuse 其評估代碼,而其 reconstruction accuracy mean 0.025 比 SceneVGGT 的 0.0446 低近兩倍,是理解「mean–median gap 從哪來」的對照組;rolling memory 加 pruning 也是 mid-block 物件處理的潛在替代設計。
- **VGGT** (Wang et al., CVPR 2025, [1]): tracking head 是 SceneVGGT 全部 cross-frame 語意傳播的核心元件,但論文對 tracking head 在多重遮擋、快速視角變動下的失效模式只字未提,需直接讀原文確認 tracking head 設計範圍。
- **EmbodiedSAM** (Xu et al., 2024, [14]): SceneVGGT 自稱解決了 EmbodiedSAM 在 mask layering 與 temporal consistency 上的問題,但無直接比較;其 SAM-based 2D-to-3D lifting 是「不依賴 LiDAR、不依賴 keyframe-only init」的替代設計,值得用來對照 §3.2 的限制。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在完全 monocular(關掉 LiDAR depth grounding)設定下,SceneVGGT 的 ATE 與 long-term scale drift 會退化到什麼程度,從而能與 InfiniteVGGT、IncVGGT 做 apples-to-apples 比較?
- [ ] Table 2 mid-block 物件造成的 25–30% ID consistency 落差,是否會直接導致 navigation 模組挑錯目標(例如把同一張椅子重複當成兩個目標)?有無端到端的 navigation success rate 來量化這個影響?
- [ ] Chamfer threshold 30 cm 在物件密集場景(餐廳成排椅子、書架)中是否會 over-merge 不同實例?是否需要與 object class 的 typical size 掛鉤的 adaptive threshold?
- [ ] 用實際 YOLOv9e mask 取代 ScanNet++ GT mask 後,ID consistency 會掉多少?亦即 mask quality 對 tracking pipeline 的敏感度有多大?
- [ ] RECENT/REMOVED/RETAINED confidence linear decay 的速率與 block size $n$ 之間的耦合關係如何?快速繞房一圈時,REMOVED 是否會誤殺長時間離開視野但仍存在的物件?
- [ ] 在樓梯、坡道、低矮障礙物等違反 flat-floor 假設的場景,§3.3 的 RANSAC 平面切換策略(5°、0.1 m、$l = 5$)會出現什麼可預測的失效模式?
- [ ] 為什麼 SceneVGGT 的 reconstruction accuracy mean(0.0446)遠高於 median(0.0120)?是 sliding-window 邊界效應、LiDAR shadow,還是 keyframe overlap 不足造成的 outlier?

### 8.2 Improvement Directions

排序由高至低為「可行性 × 預期收益」:

1. **把 mid-block tracklet 初始化納入設計**。目前 §3.2 規定 new tracklets 只在 block 第一個 keyframe 開,可改為「block 任何 frame 累積 untracked mask 到候選池,block 結束時用 Chamfer 距離與既有 inactive tracklet 比對,若皆不匹配則於下一 block 的第一個 keyframe 視為新 tracklet」。理由:Table 2 的 65–74% 一致性正好對應目前被丟棄的 untracked masks,這是改動最小、收益最直接的設計補洞。
2. **加入 LiDAR-off ablation**。對 7-Scenes 與自家 in-the-wild 序列同時跑「LiDAR depth grounding 開/關」兩條路徑,把 ATE、accuracy、跨 block scale drift 並列在 Table 1 同欄。理由:這是把 SceneVGGT 從「RGB-D 系統」拉回「VGGT streaming improvement」論述所必須的單一實驗,實作只需把 metric grounding 換成 VGGT 自身 depth scale。
3. **以實際 segmentation(YOLOv9e、SAM 或 SAM2)取代 GT mask 重跑 Table 2**。即使僅重跑同樣三個 ScanNet++ 場景,也能量化 deployment 落差。理由:目前的數字在 deployment scenario 是 upper bound,讀者只能猜下界。
4. **加入 quantitative navigation benchmark**。例如在 Habitat-Matterport 或 Replica 上跑 ObjectNav 或 Find-the-Seat,報 SPL、collision count、success rate;就算只有 5–10 個 scene,也比 §4 的「visualization video」嚴謹得多。理由:這是把第四項 contribution 從 overclaimed 移到 supported 的唯一路徑。
5. **針對核心超參數做 sensitivity sweep**。對 $n$、$k$(目前 $k = n = 10$)、Chamfer threshold(30 cm)、confidence decay rate、$l$ 做 $\pm 50\%$ 的 ablation,挑兩個 7-Scenes 場景跑即可。理由:目前這些值都是「we settled with」的 magic numbers,讀者無法判斷適用範圍。
6. **擴展 change detection 到 unsegmented regions**。如作者在 §4.4 點到的方向,可在 background 點雲上以 voxel-level confidence 加平均深度殘差做 unsupervised 變化檢測。理由:這直接擴大第二項 contribution 的覆蓋面,但實作複雜度高,故排在較後面。
7. **替換 floor-plane 假設,改用 traversability prediction**。把 §3.3 的 RANSAC 平面換成 learned traversability map(以高度 gradient 加 semantic 一起評估),解決樓梯、坡道盲點。理由:結構性改動最大,但能讓 assistive navigation 真正涵蓋目標族群關心的場景。
