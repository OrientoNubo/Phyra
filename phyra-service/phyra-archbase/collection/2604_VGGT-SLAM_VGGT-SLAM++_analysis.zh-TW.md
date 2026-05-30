<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# VGGT-SLAM++ — VGGT-SLAM++

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | VGGT-SLAM++ |
| Paper full title | VGGT-SLAM++ |
| arXiv ID | 2604.06830 |
| Release date | 2026-04-08 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2604.06830 |
| PDF link | https://arxiv.org/pdf/2604.06830v1 |
| Code link | — |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Avilasha Mandal | Indian Institute of Technology Delhi | — (https://www.linkedin.com/in/avilasha-mandal-291161250/) | first author |
| Rajesh Kumar | Addverb Technologies | — | co-author |
| Sudarshan Sunil Harithas | Brown University | https://sudarshan-s-harithas.github.io/ | co-author |
| Chetan Arora | Indian Institute of Technology Delhi | https://www.cse.iitd.ac.in/~chetan/ | senior author / corresponding |

### 1.2 Keywords

Visual SLAM, VGGT, Feed-forward 3D reconstruction, Digital Elevation Map (DEM), DINOv2 embedding, Visual Place Recognition, Covisibility graph, Sim(3) optimization

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT-SLAM (Maggio et al.) | predecessor | 直接前身;以 VGGT 為基礎的 SLAM,但僅靠稀疏 loop closure 與全域 Sim(3) 流形約束,本文針對其短期漂移加以補強。 |
| VGGT (Visual Geometry Grounded Transformer) | base model | 本系統的 feed-forward 子地圖產生器,提供深度、相機姿態與密集點雲。 |
| DUSt3R | influence | 首創以 transformer 直接由未校正影像對預測密集點雲與姿態,啟發後續 feed-forward 3D 重建潮流。 |
| MASt3R / MASt3R-SfM | influence | DUSt3R 的多視角延伸,引入學習式對應與全域精煉,屬同類 feed-forward 重建脈絡。 |
| FinderNet | influence | 首先在 LiDAR 上以 DEM 規範化做 loop detection;本文借用其 DEM 思想但改用 RGB 子地圖搭配 DINOv2。 |
| DROID-SLAM | baseline | 現代 dense SLAM 代表性 baseline,被引用作為記憶體與精度比較對象 (8GB front-end / 24GB back-end)。 |
| AnyLoc | influence | 作為 covisibility window 內的 Visual Place Recognition 模組,提供 chip-tile 對應檢索分數。 |

## 2. Research Overview

### 2.1 Research Topic

本論文屬於視覺 SLAM(Simultaneous Localization and Mapping)領域,聚焦於以 transformer 為基礎的密集視覺里程計與後端地圖最佳化整合。作者建構一套端到端的 RGB SLAM 系統 VGGT-SLAM++,以 feed-forward transformer VGGT 作為 submap 產生器,輸出相機姿態、深度與點雲;並提出以 Digital Elevation Map(DEM)為核心的緊湊地圖表徵,搭配 DINOv2 做結構感知嵌入,經 FAISS-HNSW 索引建構 covisibility graph,再以 AnyLoc 做 VPR(Visual Place Recognition)以高頻啟動 local bundle adjustment。研究主題涵蓋大尺度長序列軌跡的漂移抑制、平面場景下的幾何穩定性、以及 transformer 前端與經典後端最佳化的耦合。實驗於 KITTI、TUM RGB-D、7-Scenes、Virtual KITTI、EuRoC MAV 等基準上驗證精度與記憶體效率。

### 2.2 Domain Tags

- Computer Vision
- Robotics
- SLAM
- 3D Reconstruction

### 2.3 Core Architectures Used

- **VGGT (Visual Geometry Grounded Transformer)**: feed-forward transformer 前端,將每個 submap 的 RGB 影像群一次推論出相機姿態、深度與密集點雲,作為下游 Sim(3) 對齊與 DEM 生成的幾何來源。
- **Sim(3) odometry / motion-only solver**: 以 VGGT 預測為輸入,在相鄰 submap 間求解相對 Sim(3) 變換以建立時序一致軌跡,並作為 back-end 最佳化的初值。
- **DEM (Digital Elevation Map) module**: 以 RANSAC 與 SVD 擬合主平面後,將 VGGT 點雲離散化為 2.5D 高度網格並切成 $2 \times 2$ m tile/chip,提供結構保真且輕量的地圖表徵。
- **DINOv2 encoder**: 對每個 DEM tile 與 query chip 抽取 patch token,搭配 9×9 鄰域的 Gaussian 位置權重與基於梯度的 visibility mask,產生結構感知的嵌入向量。
- **FAISS-HNSW index**: 以 sublinear 複雜度於全域 DEM tile 嵌入庫上做近似最近鄰檢索,並以 submap 級投票匯聚相似度,用於建構 covisibility graph $G = (V, E)$。
- **AnyLoc VPR module**: 在 covisibility window 內對 chip-to-tile 對應做 Visual Place Recognition 精篩,輸出 submap-to-submap 的 loop edge。
- **Sim(3) local bundle adjustment back-end**: 以 $\log_{\mathrm{Sim}(3)}(T_j^{-1} T_i \hat{T}_{ij})$ 加權測地殘差為目標,經 Gauss–Newton 對覆蓋圖內 submap 群做高頻局部最佳化以抑制漂移。

### 2.4 Core Argument

作者主張現行以 transformer 為前端的 SLAM 系統(如 VGGT-SLAM)雖在長距離一致性上表現亮眼,但其修正行為過度依賴稀疏的 global loop closure:在兩次大基線回訪之間,前端持續累積漂移而後端卻處於被動等待狀態,導致短時尺度上的軌跡明顯抖動且平面場景下的退化更為嚴重。其根本成因在於:transformer 前端的高更新頻率與後端僅靠全域 loop closure 觸發強約束之間,存在 cadence 失衡——短時間視窗其實已蘊含足夠的多視角幾何資訊,只是缺乏快速可辨識且結構可驗證的 map 表徵讓後端能夠廉價地反覆使用。基於此觀察,作者提出空間矯正型後端的解法在邏輯上自然成立:首先必須有一種既緊湊又保留局部 affine 結構的 map 表徵,於是引入由 RANSAC 平面擬合與 softmax 高度聚合產生的 DEM 切片;接著必須讓深度神經編碼器能直接吃這種表徵以提供區分性嵌入,故選用 DINOv2 並輔以 9×9 鄰域之 Gaussian 權重與梯度遮罩;最後以 FAISS-HNSW 建 covisibility 索引、在 covisibility window 內以 AnyLoc 做 VPR,將 chip-to-tile 票數匯聚至 submap 級,觸發以 Sim(3) 對數映射殘差為目標的 local bundle adjustment。整體論證形成一條閉環:DEM 提供結構保真度、DINOv2 提供語意對齊、covisibility graph 限縮搜尋空間,因此後端能以高頻運轉、在 loop event 之間即時壓制漂移,並同時克服 VGGT-SLAM 在平面場景的失效與全域檢索的偽陽性問題。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題 "VGGT-SLAM++" 直接以 `++` 標示這是對既有 VGGT-SLAM [50] 的延伸與強化,暗示作者並非提出全新的 odometry 架構,而是在既有 transformer-based pipeline 上補上一層修正機制。Abstract 的敘事邏輯分為三層:首先定位 VGGT-SLAM++ 為一套完整的 visual SLAM 系統,front-end 由 VGGT feed-forward transformer 加上 Sim(3) solver 組成,負責產生 submap;其次點出 VGGT-SLAM 等先前 transformer-based pipeline 的核心限制——僅依賴 sparse loop closure 或 global Sim(3) manifold constraint,造成 short-horizon pose drift;最後揭露本文的修正策略,即透過 DEM-based covisibility graph 與 high-cadence local bundle adjustment (LBA) 提供 spatially corrective back-end。Abstract 也預告了三項關鍵技術元件:planar-canonical DEM、DINOv2 embedding 與 AnyLoc-based VPR retrieval。在貢獻定位上,作者強調 state-of-the-art accuracy、short-term drift 顯著降低、graph 收斂加速,以及 compact DEM tiles 與 sublinear retrieval 帶來的 bounded memory。Abstract 為後續 Introduction 鋪設了「front-end 跑得快、back-end 跟不上」這個張力,讓讀者對「為何需要 high-cadence LBA」與「DEM 為何是合適的中介表示」產生明確期待。

### 3.2 Introduction

(750 words)

Introduction 採取「歷史脈絡 → 當前缺口 → 我方主張 → 貢獻條列」的標準 SLAM 論文結構,推進邏輯非常工整。第一段先把 SLAM 拆解為 high-frequency front-end 與 slower back-end 兩個元件,並回顧從 optical flow [30, 49]、feature descriptor [3, 47, 61] 到 learned matcher [15, 62] 與 transformer-based 系統 [17, 42, 83, 97] 的演進,把 VGGT-SLAM [50] 定位為 dense transformer 路線中的代表作。

第二段切入問題:雖然 VGGT-SLAM 在 long-range consistency 上表現優異,但 corrective behavior 偏粗糙——front-end 持續累積 drift,back-end 卻必須等待 large-baseline revisit 才能觸發強約束。作者由此推出核心觀察:short temporal window 與 neighboring submap 已經提供足夠的 multi-view geometry 來抑制 drift,只要能夠快速找到並優化它們即可。這個觀察直接對應後續方法設計的兩個方向:(i) 提高 back-end 中 local correction 的 cadence,(ii) 用 compact、structure-preserving 的 map evidence 餵給每次 local optimization,讓它便宜又有判別力。

第三段引入兩個技術骨幹:DEM-augmented submap 與 covisibility search。每個 submap 會輸出一張 dense DEM,作為 spatially coherent 的 2.5D projection,既保留 local affine structure,又能透過 DINOv2 [59] encoder 產生 structurally aware embedding;接著用 FAISS-HNSW 建立 covisibility graph,並在 covisibility window 內透過 AnyLoc [33] 進行 VPR,避免在整張 map 上做 redundant search。作者特別強調 DEM 上做 loop detection 已能產生足夠 informative 的 constraint,並把得到的相對 pose 餵入 Sim(3) optimizer [69]。

第四段補上 RGB 對比視角的限制論證:per-frame RGB feature 受限於 low FOV 與 false-positive 風險,而 submap-level DEM 的 FOV 大、特徵豐富,因此能補強 transformer 在 planar scene(如 TUM RGB-D `freiburg1_floor`,Fig. 4)中的弱項。作者把貢獻定位為「semantic scalability + geometric stability」的統一框架,既處理 long-horizon 軌跡,也處理 near-planar 軌跡。

最後以三條 bullet 收束貢獻:(1) compact、geometry-preserving、與 DINOv2 兼容的 DEM map representation;(2) 基於 local affine structure 搜尋的 covisibility graph synthesis,降低搜尋空間並由 VPR 完成 candidate submap insertion;(3) 高 cadence 的 LBA back-end,在 loop event 之間持續抑制 odometry drift。Introduction 在最後一段預告 driving 與 robotics benchmark 的驗證,並承諾在 short-term drift、graph stabilization 與 final global consistency 三個維度都有改進,同時保持 runtime 在 practical budget 內,自然把讀者帶向 §2 的相關工作整理。

### 3.3 Related Work / Preliminaries

(370 words)

§2 Related Work 用兩個小節把背景文獻分為兩條主線,清楚劃出 VGGT-SLAM++ 站在哪兩座肩膀上。

第一條主線是 **Feed-Forward 3D Reconstruction Networks**。作者依時間軸鋪陳 transformer-based reconstruction 的演進:DUSt3R [87] 從未校正雙影像直接回歸 dense point 與 pose,MASt3R [56] 與 MASt3R-SfM [19] 把它擴到 multi-view 並加入 learned correspondence 與 global refinement;Spann3R [81]、Cut3R [86] 引入記憶或遞迴以處理較長序列;Pow3R [31]、Splatt3R [66] 則將公式擴展到 mixed cue 與 Gaussian-splat 表示;MapAnything [34] 則把十多個 reconstruction 任務統一進單一 feed-forward transformer。本段的收束點是 VGGT [83]——它把 feed-forward reconstruction 規模化到數百張 frame,並在單次前向中聯合預測 camera、depth 與 dense track。作者明確說明 VGGT 在本文的角色:作為 submap 生成器,提供 dense geometry 與 camera prior,讓後續的 spatially corrective Sim(3) optimization 有可優化的對象;同時點出 VGGT-SLAM 透過估計相鄰 submap 之間的相對變換來解決 projective ambiguity。

第二條主線是 **DEM for Compact, Structure-Aware Geometry**。作者先回顧 DEM canonicalization [28] 在 LiDAR loop detection [12] 中的價值——透過 roll/pitch normalization 與 top-down discretization 取得大幅 bandwidth 節省與 viewpoint robustness;接著以 FinderNet [28] 為對照,凸顯 DEM 既能支援 robust loop detection,又對 learned embedding 友善。

最關鍵的是,作者明確劃出與 FinderNet 的差異:FinderNet 訓練專屬網路、處理 dense LiDAR、目標是 5-DOF loop detection;VGGT-SLAM++ 則是把 dense RGB submap 轉成 image-like DEM,改用通用的 DINOv2 [59] 做 embedding,並在 transformer-generated point map 上處理 unconstrained DOF 的雜訊特性。這一段刻意把「DEM 不是 LiDAR 才能用」這個概念釐清,並把方法的三個優勢一次列齊:(i) 保留 affine structure 以利 geometric verification、(ii) 能乾淨通過 structure-aware encoder、(iii) 加速 covisibility synthesis。Related Work 的整體目標是論證為何「VGGT + DEM + DINOv2 + AnyLoc」是合理且新穎的組合,並為 §3 Method 將要展開的 pipeline 預先建立辭彙與動機。

### 3.4 Method (overview narrative)

(720 words)

§3 Method 以「Review → Overview → 子模組」結構展開,§3.4 在此聚焦於前兩段所建立的整體故事邏輯,而把每個子模組的細節留給後續節次。

**Review** 段先簡述 VGGT-SLAM 的運作:用 Lucas–Kanade [49] flow 量測連續 keyframe 之間的 disparity,當超過閾值 $\tau_{\text{disparity}}$(本文設為 40m)時就把 frame 加入 current submap;當 submap 累積到固定上限 $w$(設為 32)就 finalize 為 $S_{\text{latest}}$。每個 submap 會繼承前一 submap 的一個 transition frame $M_{\text{prior}}$ 以維持時間連續性,但與原始公式不同的是,本文把 loop closure frame 的數量設為 $w_{\text{loops}} = 0$,刻意把 loop closure 的責任從 front-end 移到 back-end 的 spatially drift-corrective 模組。每個 submap 經 VGGT 推論出 depth map、camera 與 point map。這段 Review 的策略是讓讀者理解「我們繼承了哪些設計」與「我們刻意改變了哪些設計」。

**Overview** 段則拉高視角描繪整條 pipeline(對應 Fig. 3):RGB frame 依 disparity 分群為 submap,送入 VGGT 取得 camera pose;每個 submap 透過 Sim(3) 變換對齊到前一個 submap 形成時間一致軌跡;接著對 point cloud 做 depth thresholding 移除 sky/cloud 等 floater;這條完整對齊的 point cloud 會進一步合成為 global planar-canonical DEM,並切成 2x2 公尺的 tile。每張 DEM tile 用 DINOv2 抽取 compact descriptor,索引在 FAISS-HNSW [18] 結構中作為可擴展的 retrieval gallery。

針對每個從 front-end 進來的 query submap,系統同樣構建 planar-canonical DEM,並切成 2x2 公尺的 chip 作為 loop detection 的查詢單元。Front-end tracking thread 會持續為這些 chip 生成 embedding,並對照 global DEM tile 的 embedding 找出 spatially proximal submap;以這些 spatial neighbor 為基礎建立 covisibility window,再以 AnyLoc [33] 作為 VPR 模組,在 covisibility region 內把 submap chip 當查詢、對應 tile 當 gallery,完成精確的 submap insertion。

從敘事邏輯看,§3.4 完成了三個鋪陳任務。第一,清楚定位 front-end 與 back-end 的「角色重分配」:front-end 仍快速產出 submap 與 Sim(3) odometry,但 loop closure 的責任完全移到 back-end,這是後續宣稱 high-cadence LBA 的合法性來源。第二,把 DEM 從一個「視覺化工具」重新定義為一個「retrieval 與 covisibility 的核心媒介」,並透過 chip-vs-tile 的 dual embedding 策略,讓 query submap 與 indexed map 在同一 embedding 空間比較。第三,把 covisibility 與 VPR 拆成兩階段——FAISS-HNSW 先做粗略 spatial proposal,AnyLoc 再做精細 loop verification——這個 cascaded design 是後續 §4 Experiments 中宣稱「sublinear retrieval、bounded memory、real-time runtime」的設計動機。

§3.4 也透過 overview 預告了後續會展開的具體模組:DEM-Augmented Submap、DINOv2-based DEM tile/chip embedding(含 Gaussian positional weight 與 visibility mask 的 weighted attention)、FAISS-HNSW covisibility graph、AnyLoc VPR、以及 Sim(3) back-end optimization。這讓 §3 後續每一小節都有清楚的位置感,避免讀者在多個技術詞彙(DEM、tile、chip、covisibility window、VPR、Sim(3))之間迷路。整體而言,§3.4 的故事就是:把 VGGT 當前向幾何引擎、把 DEM 當壓縮的對齊基底、把 covisibility graph 當搜尋空間裁剪器、把 LBA 當高頻校正器。

### 3.5 Experiments (overview narrative)

(560 words)

§4 Experiments 的 overview 段先建立評測協議與運算環境,再以一個整體性結論作為後續三個小節(§4.1 Quantitative Results、§4.2 Ablations、§4.3 Discussion)的入口。

在 **Datasets and Setup** 部分,作者選了五個涵蓋合成與真實場景的 benchmark:KITTI Odometry [26]、TUM RGB-D [70]、7-SCENES [64]、Virtual KITTI [22]、EuRoC MAV [8](EuRoC 結果留到 Appendix A1)。這個選擇兼顧 driving、indoor RGB-D、small-scale relocalization 與 weather/illumination 變化,讓 VGGT-SLAM++ 的「short-term drift 抑制 + global consistency 維持」可在多種場景被檢驗。Hardware 為 RTX 4090(24 GB VRAM)與 Threadripper PRO 5955WX(32 GB RAM);DEM rendering、DINO embedding 與 LBA 跑在 GPU,FAISS-HNSW 索引跑在 CPU,這個分工本身就支撐了 bounded memory 的論述。指標採用 ATE RMSE(meters)。

**Memory Profile** 段是這節的關鍵伏筆:推論時只把當前 covisibility window 內的 VGGT feature、DEM raster 與對應 tile 的 DINOv2 token 留在 GPU,window 外的 submap point cloud 落到磁碟;global DEM tile 以壓縮 2.5D grid(約 1–1.2 MB/tile)存放在 CPU RAM;FAISS-HNSW 隨節點增長呈 sublinear 記憶體成長。最終量化結果是 front-end ∼16 FPS、back-end 1.89 FPS,VRAM 峰值約 20 GB、RAM 約 8 GB,並與 DROID-SLAM [77](8 GB front-end、24 GB back-end)做對照。這段話既定義了「real-time、bounded memory」的具體含義,也提前回應未來可能的 reviewer 質疑。

**Structure-aware DEM** 段是另一條重要伏筆:作者用 zero-shot GDINO [45] 在 KITTI 360 的「parked vehicle」、TUM RGB-D `freiburg1` 的「teddy」與 7-SCENES 的「chess」上得到正確偵測,間接證明 DEM 保留了結構性語義。同時釐清一個潛在誤解:彩色版 DEM 只供人觀看,DINOv2 實際接收的是灰階版本,黃色為 ground plane、綠色越深表示高度越高。

§4.1 的快速概覽是:VGGT-SLAM++ 在所有 RGB、未校正相機輸入的 dataset 上都達到與 DROID-SLAM、MASt3R-SLAM、VGGT-SLAM 相當或更好的表現,並首次在 uncalibrated 設定下逼近 calibrated 系統如 MASt3R-SLAM 的 ATE。Virtual KITTI(Table 4)的多種天氣條件結果則被用來支撐「DEM 保留了強幾何 cue」的主張。作者也誠實揭露弱項——在 EuRoC 等灰階 dataset 上,因 VGGT 訓練資料為 RGB,front-end 表現遜於 classical pipeline,但 back-end 仍把 ATE 改善約 9%。整體而言,VGGT-SLAM++ 對 VGGT-SLAM baseline 在 KITTI、TUM、7-Scenes、Virtual KITTI、EuRoC 上分別降低 20%、45%、5%、14%、9% 的 ATE,跨四個主 dataset 平均從 17.13 m 降到 13.94 m,整體改進 18.6%。

§4.2 Ablation 預告了 DEM rendering 超參數對 KITTI 00–10 的影響——包括 reducer 選擇、softmax temperature $\tau$、解析度與 edge enhancement 強度——並把細節推到主表 Table 5 與 Appendix A3。§4.3 Discussion 則把整體實驗收束為兩句話:「方法在 ATE 與 runtime 上一致改進,同時記憶體使用低」、「monochrome 表現受限於 VGGT 訓練資料,但 back-end 仍帶來顯著 ATE 改進」,自然把讀者帶到 §5 Conclusion。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

§5 Conclusion 是一段相當緊湊的收束。作者首先重申系統定位:VGGT-SLAM++ 把 VGGT-derived odometry 與 DEM-based covisibility framework 以及 local bundle adjustment 結合在一起,藉由 compact DEM 保留 scene 的關鍵結構,再透過 DINOv2 embedding 達成 efficient retrieval。第二句話回收實驗成果——RGB dataset 上達到 SOTA,monochrome sequence 上也帶來顯著改進(此處呼應 §4.3 對 EuRoC 限制的承認)。

接著作者把 DEM 包裝為「以最小計算成本換取精度提升」的設計,藉此論證系統適合 real-time、edge platform 部署;這個「適合 edge」的訴求是論文在 robotics 應用面的市場定位,也與 §4 Memory Profile 中強調 bounded memory 的論述前後呼應。

關於 Limitations,Conclusion 並未獨立成段,但實際限制散落在 §4 各處:VGGT 對 monochrome 的弱項、front-end 仍依賴 transformer 的 RGB 訓練分布、calibrated 與 uncalibrated 之間僅有 marginal 差異(由 Appendix A1 補充)。從敘事邏輯看,作者選擇把限制嵌入結果討論而非單獨拉出,顯示其策略是「把限制定位為下一步的工程方向」而非根本性瓶頸。

Future Work 集中於兩條路:**model compression** 以進一步降低 computational burden,以及 **multi-modal sensing** 以提升 generalization。這兩條方向與 §1 末尾承諾的「practical runtime budget」與 §4 對灰階 dataset 的弱點直接對應——壓縮模型回應 edge 部署的算力與顯存限制,multi-modal 則直指 RGB-only transformer 在灰階、低光照、跨感測器條件下的瓶頸,並暗示後續可能引入 depth、IMU 或 LiDAR 等模態。整體 Conclusion 雖簡短,但成功把全文三條主線——transformer odometry、DEM-based retrieval、high-cadence LBA——以一個統一句串接,並把後續研究議程明確留給社群。

## 4. Critical Profile

### 4.1 Highlights

- 在四個 RGB benchmark 上對 VGGT-SLAM baseline (Sim(3)+SL(4) per-dataset average) 的 ATE 平均下降 18.6%,各別為 KITTI 20%、TUM 45%、7-Scenes 5%、Virtual KITTI 14%(§4.1)。
- 修補了 VGGT-SLAM 在平面場景的退化:TUM RGB-D `freiburg1_floor` 由 0.254m (Sim3) / 0.141m (SL4) 降至 0.077m (Table 2、Fig. 4)。
- 在多項長序列上 SL(4) 變體完全發散,而本文以 Sim(3) 後端在 KITTI 00、02、05–08 全數收斂 (Table 1、Appendix A6)。
- 在未校正 RGB 輸入下達成可與已校正 MASt3R-SLAM 相提並論的 ATE,例如 TUM 平均 0.036m 對 MASt3R-SLAM* 0.062m (Table 2)。
- 前端 $\sim$16 FPS、空間矯正後端 1.89 FPS,記憶體使用約 8GB RAM 與 20GB VRAM,優於 DROID-SLAM 的 8GB front-end + 24GB back-end (page 6)。
- 在 Virtual KITTI 五種 weather/illumination 變體下保持穩定,例如 Sequence 02 平均 0.18m 對 VGGT-SLAM (SL4) 0.27m (Table 4)。
- 以 GroundingDINO 對 DEM 進行 zero-shot 物件偵測成功識別 KITTI 360 的「parked vehicle」、TUM 的「teddy」、7-Scenes 的「chess」,作為 DEM 結構保真度的定性證據 (Fig. 5A–C)。
- DEM 的 top-down canonicalization 使 8 字形軌跡在從相反方向再訪同一中心點時仍能成功偵測 loop,克服了 RGB 前視野受限的問題 (Appendix A1、Fig. 1A)。
- 每塊 global DEM tile 壓縮為約 1–1.2MB 的 2.5D grid,FAISS-HNSW index 以 768 維描述子在 CPU 上以亞線性記憶體成長 (page 6)。
- 客製 GoPro 287.381m 路徑達成 ATE RMSE 7.17 ± 2m,且在 Cobot/Humanoid 平面場景達成 0.01–0.02m 的 ATE (Fig. 6B/C/F)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 在 monochrome/grayscale 序列(如 EuRoC)上 VGGT 前端表現顯著劣化,因為 VGGT 僅在 RGB 上訓練;後端只能將 ATE 改善 9%,絕對值仍遠落後 DROID-SLAM (§4.3 Discussion、Appendix A1、Table 6)。
- VGGT-SLAM 的 SL(4) 變體在多條長 KITTI 與 EuRoC 序列上不收斂,作者以此作為改採 Sim(3) 的動機,等同承認原 baseline 在長序列下不穩定 (Table 1、Appendix A6)。
- 結論段點名 model compression 與 multi-modal sensing 為 future work,意味目前計算負擔仍未達 edge deployment 標準 (§5 Conclusion)。

#### 4.2.2 Phyra-inferred

- KITTI 絕對 ATE 仍極高:Seq 02 = 223.21m、Seq 08 = 155.00m、Seq 00 = 119.00m (Table 1),20% 的相對增益在駕駛尺度下仍不足以作為定位來源,但論文未討論這個 usability gap。
- Table 5 的 DEM 超參數 ablation 中,大多數設定在多數序列上產生 identical 的 ATE(例如 Seq 03 全為 4.50、Seq 04 全為 0.95、Seq 09 全為 35.26),顯示 DEM 渲染參數其實並非主要增益來源,與論文敘事不符。
- 沒有任何實驗將 {DEM canonicalization, DINOv2 9×9 加權, FAISS-HNSW covisibility, AnyLoc VPR, 高頻 Sim(3) LBA} 拆開分別 ablate,使整體 18.6% 增益的歸因不可驗證。
- 已校正版本在 KITTI 上僅帶來邊際差異(Seq 05: 25.21 → 25.20m;Seq 03 維持 4.50m,Appendix A1),這暗示精度的瓶頸並非投影性歧異性,弱化了論文「DEM-based covisibility 為主要 driver」的說法。
- Virtual KITTI Sequence 06 的 VGGT-SLAM (Sim3) 與 VGGT-SLAM++ 在六種 weather variants 全部產出相同 ATE (Table 4),意味後端在該序列實際上沒有產生任何可量測的修正。
- 「High-cadence」後端僅 1.89 FPS,相對 16 FPS 前端仍慢約 8.5×,cadence 失衡只是被縮小而非被消除,而論文的核心敘事將其呈現為「跟上前端」。
- TUM `plant` 場景由 VGGT-SLAM (Sim3) 的 0.022m 退化到本文的 0.042m (Table 2),代表後端在某些場景反而傷害了精度,但論文未提出 failure analysis。
- VGGT-SLAM baseline 採「Sim(3)+SL(4) per-dataset averaged」計算,而 SL(4) 在多序列上完全發散,使該 baseline 被人為抬高,進而誇大 18.6% 的相對增益 (Table 1、Appendix A6)。
- 客製資料以 2m 精度的 GPS 作為 ground truth,卻報告 ATE RMSE 18 ± 2m 與 7.17 ± 2m (Fig. 6A/F),在路徑的局部區段上真實誤差與 GT 噪聲已不可區分。
- 無任何相對於 DROID-SLAM、MASt3R-SLAM、VGGT-SLAM 的 runtime/throughput 對照,僅給出本系統自身的絕對 FPS,使「real-time 與 bounded memory」對比難以驗證。

### 4.3 Phyra's Judgment (summary)

論文真正新穎的點是把 FinderNet 的 LiDAR DEM canonicalization 思路移植到 transformer 產生的 RGB submap,並讓凍結的 DINOv2 與 AnyLoc 直接消化此 representation,使 loop detection 能以高頻率啟動。其餘元件 (Sim(3) LBA、FAISS-HNSW、RANSAC + softmax 高度聚合) 都是現成工具的工程組合。最關鍵的未解問題是:18.6% 的增益究竟來自 DEM-DINOv2 retrieval,還是僅僅來自 LBA cadence 變高?論文沒有任何 ablation 能將兩者分離,使所謂的「DEM 是 driver」的論證在實證上站不住腳。

## 5. Methodology Deep Dive

### 5.1 Method Overview

VGGT-SLAM++ is an end-to-end RGB SLAM system whose architecture decouples three asynchronous threads: (i) a feed-forward front-end that consumes a sliding submap of $w=32$ keyframes and predicts depth, intrinsics, and per-frame camera poses through the pretrained VGGT transformer; (ii) a covisibility-graph constructor that turns each submap's dense point cloud into a planar-canonical Digital Elevation Map (DEM), tiles the DEM into $2\times2\,\text{m}$ patches, embeds each tile through a DINOv2 encoder, and indexes the resulting 768-d descriptors in a FAISS-HNSW gallery; and (iii) a back-end Gauss-Newton solver that ingests submap-to-submap loop edges proposed by an AnyLoc VPR pass over the covisibility window and minimizes a weighted geodesic residual on the $\mathrm{Sim}(3)$ manifold. Keyframes are admitted to the active submap when the Lucas-Kanade disparity between the candidate frame and the previous keyframe exceeds $\tau_{\mathrm{disparity}}=40\,\text{m}$; once $|I_{\mathrm{latest}}|=w$ the submap is finalized and forwarded to VGGT.

The conceptual novelty is the cadence rebalancing between the feed-forward front-end (~16 FPS) and a non-trivial spatially corrective back-end (~1.89 FPS) that no longer waits for global, large-baseline revisits. Two design decisions enable the high-cadence corrective layer. First, a DEM cuts the submap representation from a dense 3D point cloud to a 2.5D height field that retains local affine structure but is light enough to live in a sublinear retrieval gallery. Second, DINOv2 is used off-the-shelf with a 9×9 neighbourhood Gaussian-weighted aggregation and a gradient-derived visibility mask $m_j$ (dampening flat regions, emphasizing ramps and edges), so descriptors carry both DINOv2 semantics and DEM structural salience without requiring any task-specific finetuning. Loop candidates are scored by submap-level vote aggregation rather than per-tile, which suppresses the false-positive rate that single-frame VPR suffers due to limited RGB FoV. The original VGGT-SLAM contribution—deviating from $\mathrm{SL}(4)$ to a $\mathrm{Sim}(3)$ submap-pose optimization—is inherited; loop closures are explicitly excluded from $w_{\mathrm{loops}}$ (set to 0) so that the back-end controls when and how strongly to apply loop constraints rather than letting VGGT amortize them implicitly.

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: RGB frame stream                              [1, 3, H, W]
   │
   ▼
[Lucas-Kanade disparity vs prev keyframe]            scalar (m)
   │  if disparity > τ_disparity (40m): admit keyframe
   ▼
Active submap accumulator                            [N_kf ≤ w, 3, H, W]   (w = 32)
   │  when N_kf = w, finalize submap S_latest
   ▼
[VGGT feed-forward (a) Front-end]
   ├→ depth maps                                    [w, 1, H, W]
   ├→ camera poses (per-frame)                      [w, 4, 4]
   └→ dense point map (in submap frame)             [w, 3, H, W]   →   [w·H·W, 3]
   │
   ├→ depth-thresholded floater removal             [N_pts, 3]   N_pts ≤ w·H·W
   │
   ▼                                          ▼
[Sim(3) odometry: align S_i to S_{i-1}]      [Predecessor-frame inheritance M_prior]
   └→ relative pose T_{i,i-1} ∈ Sim(3)              [7]   (3 t + 4 q + 1 s; lie repr [7])
   │
   ▼
[(b) Covisibility Graph Construction]
   │
   ├→ RANSAC + SVD plane fit on point cloud         plane params [4]
   ├→ planar-canonical projection (3D → 2.5D)
   ├→ pixel-grid discretization at mpp = S/N_px     N_px = 90k (default)
   ├→ softmax-weighted height aggregation per cell
   └→ DEM tile raster                               [N_tiles, 1, H_t, W_t]   tile = 2×2 m
   │
   ▼
[DINOv2 encoder f_θ on each tile (and 9×9 nbhd)]
   ├→ token grid per tile                           [N_tiles, N_tok, 768]
   ├→ Gaussian weight w_j over 9×9 neighborhood     [9·9·N_tok]
   ├→ visibility mask m_j from |∇N(H)|              [9·9·N_tok]
   └→ aggregated tile descriptor v_k                [N_tiles, 768]
   │
   ▼
[Build / update FAISS-HNSW index] (CPU)             gallery: [N_tiles_global, 768]
   │
   │   Query submap arrives →
   │   build query DEM, split into chips χ_q        [N_chips, 1, H_t, W_t]
   │   embed chips through f_θ                      [N_chips, 768]
   ▼
[Cosine similarity + top-K retrieval]
   ├→ s(χ_q, τ_k) = vᵀ_q v_k / (‖v_q‖‖v_k‖)        per (chip, tile) score
   ├→ aggregate to submap level (Eq. 3)             Score(S) per candidate submap
   └→ covisibility graph G = (V, E)                 sparse adjacency
   │
   ▼
[AnyLoc VPR within covisibility window]
   ├→ chip ↔ tile correspondence retrieval
   └→ refined submap-to-submap loop edges            (i,j) ∈ E with weight Σ_{ij}
   │
   ▼
[(c) Spatially Corrective Back-end (concurrent)]
   ├→ pose graph with nodes T_i ∈ Sim(3)             [|V|, 7]
   ├→ residuals: log_{Sim(3)}(T_j^{-1} T_i T̂_{ij})   [|E|, 7]
   └→ Gauss-Newton minimization (Eq. 4)
   │
   ▼
Globally consistent submap poses {T_i ∈ Sim(3)}     [|V|, 7]
```

Note: $H, W$ are the VGGT-prescribed input resolution (the paper does not specify; mark as `?`). $N_{\mathrm{tok}}$ for DINOv2 patch tokens, $H_t, W_t$ for tile pixel dimensions, and the AnyLoc descriptor dimension are not disclosed in the paper.

### 5.3 Per-Module Breakdown

#### 5.3.1 Keyframe Selection & Submap Formation

**Function:** Convert a continuous RGB stream into discrete submaps of fixed cardinality, decoupling input frame-rate from VGGT's batched inference.

**Input:**
- Name: incoming RGB frames
- Shape: `[1, 3, H, W]` per timestep
- Source: external camera stream

**Output:**
- Name: $S_{\mathrm{latest}}$
- Shape: `[w, 3, H, W]` with $w=32$
- Consumer: VGGT submap generator

**Processing:**

For each incoming frame, compute Lucas-Kanade optical-flow disparity against the most recent keyframe; if disparity exceeds $\tau_{\mathrm{disparity}}=40\,\text{m}$, append to $I_{\mathrm{latest}}$. When $|I_{\mathrm{latest}}|=w$ the submap is finalized as $S_{\mathrm{latest}}$ and a single non-loop transition frame $M_{\mathrm{prior}}$ from the previous submap is inherited for temporal continuity. Loop-closure frames $w_{\mathrm{loops}}$ are explicitly set to $0$ (a deviation from the original VGGT-SLAM) so that loop handling is delegated entirely to the corrective back-end.

**Key Formulas:**

Disparity gating: append frame $f_t$ to $I_{\mathrm{latest}}$ if $\mathrm{disparity}_{\mathrm{LK}}(f_t, f_{\mathrm{prev\_kf}}) > \tau_{\mathrm{disparity}}$.

**Implementation Details:**

$w=32$, $\tau_{\mathrm{disparity}}=40\,\text{m}$, $w_{\mathrm{loops}}=0$. The paper does not specify the LK window size or pyramid levels.

#### 5.3.2 VGGT Feed-Forward Submap Generator

**Function:** Map a finalized submap of $w$ keyframes to dense per-frame depth, per-frame camera poses, and a unified submap point map in a single forward pass of the pretrained VGGT transformer.

**Input:**
- Name: $S_{\mathrm{latest}}$
- Shape: `[w, 3, H, W]`
- Source: keyframe selector

**Output:**
- Name: depth maps, camera poses, dense point map
- Shape: depth `[w, 1, H, W]`; poses `[w, 4, 4]`; points `[w, 3, H, W]`
- Consumer: Sim(3) odometry, DEM construction

**Processing:**

VGGT is invoked once per finalized submap (not per frame), producing geometry-rich predictions in a single feed-forward pass. After inference, depth thresholding removes far-field floaters (cloud / sky horizon noise). The resulting point cloud is consumed both by the front-end Sim(3) aligner and by the DEM module.

**Implementation Details:**

VGGT is used off-the-shelf (no finetuning); the paper notes that VGGT was trained on RGB and consequently underperforms on monochrome sequences such as EuRoC. Inference runs on GPU; at full operation VRAM is bounded near $20\,\text{GB}$ on an RTX 4090.

#### 5.3.3 Sim(3) Odometry (Front-end)

**Function:** Estimate the relative similarity transform aligning each new submap to its temporal predecessor, yielding an initially consistent (drift-prone) trajectory.

**Input:**
- Name: $S_{i}, S_{i-1}$ point clouds and VGGT poses
- Shape: poses `[w, 4, 4]` per submap
- Source: VGGT generator

**Output:**
- Name: $\hat{T}_{i,i-1} \in \mathrm{Sim}(3)$
- Shape: `[7]` (Lie-algebra representation; or `[4,4]` matrix form)
- Consumer: temporally coherent trajectory, back-end optimizer initialization

**Processing:**

A motion-only Sim(3) solver aligns successive submaps and resolves the projective ambiguity between independent VGGT reconstructions. Submaps inherit one transition frame $M_{\mathrm{prior}}$ to anchor temporal continuity. The aligned point cloud chain is later projected to a global planar-canonical frame for DEM rasterization.

**Implementation Details:**

The optimizer minimizes the relative-pose alignment residual on $\mathrm{Sim}(3)$; the specific cost form (point-to-point vs. point-to-plane) is not disclosed.

#### 5.3.4 DEM Construction

**Function:** Convert each submap's dense 3D point set into a compact 2.5D Digital Elevation Map defined on a single globally consistent plane, preserving local affine structure for downstream encoder ingestion.

**Input:**
- Name: dense point cloud
- Shape: `[N_pts, 3]`
- Source: VGGT + Sim(3) alignment

**Output:**
- Name: DEM tile raster $\{\tau_k\}$
- Shape: `[N_tiles, 1, H_t, W_t]`, tile size $2\times2\,\text{m}$
- Consumer: DINOv2 encoder

**Processing:**

A global plane is robustly fit via RANSAC and SVD. Continuous pixel coordinates are discretized into a regular grid at $\mathrm{mpp}=S/N_{px}$ (default $N_{px}\!\approx\!90\text{k}$). Heights falling into the same pixel are aggregated through a reducer; the softmax-weighted average performs best in the ablation. Optional Sobel-based edge enhancement modulates the normalized height. Tiles are partitioned into $2\times2\,\text{m}$ chips at "robust resolution".

**Key Formulas:**

$$
H(x,y) = \mathrm{red}_\tau\!\left(\{h^{(k)}_{x,y}\}\right), \qquad I(x,y) = \mathcal{N}(H)\,\bigl(1-\alpha_{\mathrm{edge}}\,\|\nabla \mathcal{N}(H)\|\bigr).
$$

**Implementation Details:**

Default reducer: softmax with $\tau=0.10$; default $N_{px}\!\approx\!90\text{k}$; ablations: half $45\text{k}$, high $180\text{k}$; edge enhancement $\alpha_{\mathrm{edge}}\in\{0, 0.5\}$. Each global DEM tile is stored on CPU as a compressed 2.5D grid (~$1$–$1.2\,\text{MB}$ per tile).

#### 5.3.5 DINOv2 Structure-aware Embedding

**Function:** Produce a normalized, geometry-aware 768-d descriptor per DEM tile (and per query chip) by combining DINOv2 self-supervised features with DEM-derived spatial weighting.

**Input:**
- Name: DEM tile $\tau_k$ (or query chip $\chi_q$)
- Shape: `[1, 1, H_t, W_t]`
- Source: DEM constructor

**Output:**
- Name: tile descriptor $v_k$ (or chip descriptor $v_q$)
- Shape: `[768]`
- Consumer: FAISS-HNSW index

**Processing:**

Each DEM tile is split into patches yielding tokens $\{p_j\}$ that are fed to $f_\theta$ (DINOv2 encoder). Tokens are aggregated over a $9\times9$ neighborhood centered on $\tau_k$ for global-gallery tiles, or over the entire submap region for query chips. The Gaussian positional weight $w_j$ down-weights tokens near tile boundaries; the visibility mask $m_j$ is derived from local DEM gradient magnitude so flat regions are suppressed and edges/ramps emphasized.

**Key Formulas:**

$$
v_k = \frac{\sum_j w_j\, m_j\, f_\theta(p_j)}{\sum_j w_j\, m_j}.
$$

**Implementation Details:**

Output dimension: $768$ (consistent with a DINOv2 ViT backbone). DINOv2 ingests grayscale DEMs; coloured DEMs are visualization-only. The $9\times9$ neighborhood applies to global tile embeddings; query-chip embeddings use a per-submap aggregation instead. The exact patch size for $\{p_j\}$ is not specified by the paper.

#### 5.3.6 FAISS-HNSW Covisibility Graph + AnyLoc VPR

**Function:** Provide sublinear nearest-neighbor retrieval over the global tile gallery, aggregate retrieved hits to the submap level by voting, and refine submap-to-submap loop candidates using AnyLoc VPR within a covisibility window.

**Input:**
- Name: query chip descriptors $\{v_q\}$ and global tile gallery
- Shape: queries `[N_chips, 768]`; gallery `[N_tiles_global, 768]`
- Source: DINOv2 embedder

**Output:**
- Name: covisibility graph $G=(V,E)$, refined loop edges
- Shape: $|V|$ submap nodes, $|E|$ loop edges with per-edge weights
- Consumer: spatially corrective back-end

**Processing:**

For each query chip, FAISS-HNSW returns top-K approximate nearest tiles; cosine similarities are aggregated to the parent submap by simple voting (Eq. 3). Submaps whose accumulated score exceeds threshold $\tau_s$ (or rank within top-K, $K=10$) are admitted as covisible neighbors. Within this window, AnyLoc performs a refined VPR pass: chip↔tile correspondences are retrieved and again submap-aggregated by vote, yielding submap-to-submap loop edges with per-edge confidence.

**Key Formulas:**

$$
s(\chi_q, \tau_k) = \frac{v_q^{\!\top} v_k}{\|v_q\|\,\|v_k\|}, \qquad \mathrm{Score}(S) \mathrel{+}= \sum_{\tau_k \in S} s(\chi_q, \tau_k).
$$

**Implementation Details:**

FAISS-HNSW resides fully on CPU and grows sublinearly via hierarchical graph compression. Top-K cap: $K=10$. The exact AnyLoc descriptor dimension and the value of $\tau_s$ are not specified.

#### 5.3.7 Spatially Corrective Back-end Optimization

**Function:** Run a high-cadence Gauss-Newton optimization over a spatial pose graph constructed from covisible submaps and AnyLoc-confirmed loop edges, suppressing front-end drift between conventional global loop events.

**Input:**
- Name: initial Sim(3) submap poses $\{T_i\}$, edge set $E$, relative transforms $\hat{T}_{ij}$, per-edge covariances $\Sigma_{ij}$
- Shape: poses `[|V|, 7]`; edges `[|E|, 7]`
- Source: front-end + AnyLoc VPR

**Output:**
- Name: globally consistent submap poses $\{T_i \in \mathrm{Sim}(3)\}$
- Shape: `[|V|, 7]`
- Consumer: trajectory consumer / map renderer

**Processing:**

The cost is the sum of weighted geodesic errors of all loop edges. The $\mathrm{Sim}(3)$ logmap converts similarity transforms into tangent-space residuals, enabling standard Gauss-Newton iteration. The back-end runs concurrently with the front-end at $\sim 1.89$ FPS, so corrections are applied on a scale much shorter than the loop-event interval.

**Key Formulas:**

$$
\min_{\{T_i \in \mathrm{Sim}(3)\}} \sum_{(i,j)\in E} \big\| \log_{\mathrm{Sim}(3)}\!\bigl(T_j^{-1} T_i\, \hat{T}_{ij}\bigr) \big\|^{2}_{\Sigma_{ij}}.
$$

**Implementation Details:**

Per-edge covariance $\Sigma_{ij}$ is derived from descriptor consistency and 3D alignment residuals; the precise weighting recipe is not specified. Local bundle adjustment runs on GPU; FAISS indexing and graph maintenance run on CPU. End-to-end memory profile: $\sim 8\,\text{GB}$ RAM, $\sim 20\,\text{GB}$ VRAM.

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| KITTI Odometry | Outdoor driving visual SLAM (RGB) | Sequences 00–10 (long-horizon, 上千公尺路徑) | test only (zero-shot evaluation) |
| TUM RGB-D | Indoor handheld RGB-D SLAM | 9 sequences (`360`, `desk`, `desk2`, `floor`, `plant`, `room`, `rpy`, `teddy`, `xyz`) | test only |
| 7-SCENES | Indoor RGB-D 場景定位 | 7 場景 (`chess`, `fire`, `heads`, `office`, `pumpkin`, `kitchen`, `stairs`) | test only |
| Virtual KITTI | 合成室外駕駛 (含天氣/光照變體) | 5 個序列 (01, 02, 06, 18, 20),每序列 6 種變體 (Clone/Fog/Morning/Overcast/Rain/Sunset) | test only |
| EuRoC MAV | 灰階 (monochrome) 無人機室內 SLAM | MH01–MH05 (附錄 A1) | test only |
| Custom GoPro HERO10 (GPS GT) | 戶外長路徑 SLAM | 287.381 m 與 406.8 m 兩段 | test only (定性 + ATE) |
| Custom OAK-1 + Humanoid kinematics | 人形機器人短路徑 | 1.8 m | test only |
| Custom OAK-1 + Cobot forward kinematics | 平面場景短路徑 | 1.8 m | test only |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| ATE RMSE (m) | Absolute Trajectory Error 的 root-mean-squared,評估估計軌跡與 ground truth 的全域對齊誤差 | yes |
| 收斂性 (convergence) | 是否成功收斂 (對 SL(4) 變體;以「–」標示未收斂) | no |
| Front-end FPS | 前端 tracking 吞吐量 (∼16 FPS) | no |
| Back-end FPS | 空間矯正後端吞吐量 (1.89 FPS) | no |
| VRAM / RAM 用量 | 記憶體佔用 (∼20 GB VRAM, ∼8 GB RAM) | no |
| Recall@k | ANN 檢索的召回率指標 (附錄 A4 提及作為 covisibility 檢索品質衡量) | no |

### 6.3 Training and Inference Settings

- 硬體:NVIDIA RTX 4090 GPU (24 GB VRAM) + AMD Ryzen Threadripper PRO 5955WX 16-Cores CPU (32 GB RAM)。
- 訓練:VGGT-SLAM++ 不進行端到端訓練,而是組合既有的 feed-forward VGGT、DINOv2 與 AnyLoc 模組;the paper does not specify 任何 fine-tuning 設定。
- Front-end keyframe 選取:disparity 閾值 $\tau_\text{disparity} = 40\text{m}$ (以 Lucas–Kanade flow 計算)。
- Submap 大小:每個 submap $|I_\text{latest}| = w = 32$ 張影像;與原 VGGT-SLAM 不同的是設定 $w_\text{loops} = 0$,把 loop closure 完全交給 spatially corrective back-end。
- DEM 預設超參數 (附錄 A3):softmax temperature $\tau = 0.02$、edge strength $\alpha_\text{edge} = 0.95$、解析度 90k pixels、4096 個 spatial tiles、tile 物理尺寸 $2 \times 2$ m。
- DEM tile embedding:DINOv2 編碼器 $f_\theta$ 對 9×9 tile 鄰域加權聚合,使用 768 維描述子。
- Retrieval:FAISS-HNSW 索引置於 CPU,Top-K = 10 covisible submaps。
- Back-end 最佳化:Sim(3) 上的加權 geodesic error,以 Gauss–Newton 求解 (附錄 A6)。
- Inference 配置:Front-end 約 16 FPS、back-end 約 1.89 FPS;DEM rendering、DINO embedding、LBA 在 GPU 執行,FAISS-HNSW 在 CPU 執行。
- Depth thresholding:距離超過約 30 m 的 floater 點會被過濾 (附錄 A2),邊界 $d_\text{min}, d_\text{max}$ 為 user-specified;the paper does not specify 確切數值。
- Optimizer / learning-rate schedule / training steps / batch size:the paper does not specify (本工作未訓練神經網路)。

### 6.4 Main Results

KITTI Odometry (ATE RMSE, m;平均欄為跨 11 個序列):

| Method | Uncalib. | 平均 ATE | Notes |
|---|---|---|---|
| ORB-SLAM2 (w/ LC) | ✗ | 54.82 | classical,calibrated |
| LDSO | ✗ | 22.43 | classical 最佳平均 |
| DROID-SLAM | ✗ | 554.82 | 含長序列上的大幅發散 |
| DPV-SLAM++ | ✗ | 25.75 | learning-based calibrated |
| VGGT-SLAM (Sim(3)) | ✓ | 81.22 | uncalibrated baseline |
| VGGT-SLAM (SL(4)) | ✓ | N/A | 多個序列未收斂 |
| **VGGT-SLAM++ (Ours)** | **✓** | **64.94** | **相對 VGGT-SLAM 平均下降 ∼20%** |

TUM RGB-D (ATE RMSE, m):

| Method | Uncalib. | 平均 ATE | Notes |
|---|---|---|---|
| MASt3R-SLAM | ✗ | 0.030 | calibrated SoTA |
| GO-SLAM | ✗ | 0.035 | calibrated |
| DROID-SLAM* | ✓ | 0.180 | uncalibrated baseline |
| MASt3R-SLAM* | ✓ | 0.062 | uncalibrated |
| VGGT-SLAM (Sim(3)) | ✓ | 0.079 | |
| VGGT-SLAM (SL(4)) | ✓ | 0.053 | |
| **VGGT-SLAM++ (Ours)** | **✓** | **0.036** | **uncalibrated 中最佳,逼近 calibrated SoTA;相對 VGGT-SLAM 下降 ∼45%** |

7-SCENES (ATE RMSE, m):

| Method | Uncalib. | 平均 ATE | Notes |
|---|---|---|---|
| MASt3R-SLAM | ✗ | 0.047 | calibrated SoTA |
| DROID-SLAM | ✗ | 0.050 | calibrated |
| VGGT-SLAM (Sim(3)) | ✓ | 0.067 | |
| VGGT-SLAM (SL(4)) | ✓ | 0.067 | |
| **VGGT-SLAM++ (Ours)** | **✓** | **0.064** | **uncalibrated 中最佳,相對 VGGT-SLAM 下降 ∼5%** |

Virtual KITTI (五個序列各取跨天氣的平均 ATE,m):

| Method | Seq 01 | Seq 02 | Seq 06 | Seq 18 | Seq 20 | Notes |
|---|---|---|---|---|---|---|
| DROID-SLAM | 1.14 | 0.07 | 0.04 | 2.20 | 4.16 | calibrated 表現最強 |
| CUT3R | 48.53 | 20.12 | 0.77 | 17.15 | 103.69 | learning-based 但顯著發散 |
| VGGT-SLAM (Sim(3)) | 1.80 | 0.26 | 0.47 | 1.11 | 6.39 | |
| VGGT-SLAM (SL(4)) | 4.62 | 0.27 | 0.47 | 1.11 | 6.98 | |
| **VGGT-SLAM++ (Ours)** | **2.13** | **0.18** | **0.47** | **1.11** | **6.17** | **跨天氣穩定,相對 VGGT-SLAM 下降 ∼14%** |

EuRoC MAV (附錄 A1, 平均 ATE RMSE, m):

| Method | Uncalib. | 平均 ATE | Notes |
|---|---|---|---|
| ORB-SLAM3 | ✗ | 0.056 | classical calibrated |
| DROID-SLAM | ✓ | 0.027 | uncalibrated 中最強 |
| VGGT-SLAM (Sim(3)) | ✓ | 2.938 | grayscale 上明顯弱化 |
| VGGT-SLAM (SL(4)) | ✓ | N/A | 多序列未收斂 |
| **VGGT-SLAM++ (Ours)** | **✓** | **2.666** | **相對 VGGT-SLAM 下降 ∼9%,但落後 classical/DROID** |

整體而言,跨四個 RGB 資料集 (KITTI / TUM / 7-Scenes / Virtual KITTI),相對於 VGGT-SLAM (Sim(3)+SL(4) 平均) baseline 由 17.13 m 降到 13.94 m,改善幅度 18.6%。

### 6.5 Ablation Studies

論文在 Table 5 (KITTI 00–10) 上對 DEM rendering 的多個超參數做了 ablation,並在附錄 A6 對 back-end 最佳化群選擇做了討論。

- **Reducer (Mean vs. Softmax)**:把預設的 softmax reducer 改成 mean reducer,平均 ATE 由 64.936 m 微幅升到 65.072 m。差異極小,屬於對 reducer 選擇的合理性檢核,而非真正能拉開差距的診斷。
- **Softmax temperature $\tau$**:由預設 $\tau = 0.02$ 改為 $\tau = 0.10$ 結果完全相同 (64.936 m);改為 $\tau = 0.005$ 略降到 64.711 m。雖然附錄 A3 解釋 $\tau \to 0$ 偏向 max、$\tau \to \infty$ 偏向 mean,但改動主要只影響 Seq 02 一條序列,缺乏跨序列趨勢,診斷力有限。
- **DEM 解析度**:half resolution (45k pixels, 2048 tiles) 反而把平均 ATE 由 64.936 m 降到 **58.893 m** (主因 Seq 02 由 223.21 m 降到 171.42 m、Seq 06 由 13.65 m 降到 5.85 m);high resolution (180k pixels) 升到 65.995 m。這暗示作者主文宣稱的「default」並非最佳設定,屬於有診斷意義的發現,但作者並未把 half-resolution 設為新的預設,值得標記為 inconsistency。
- **Edge enhancement** ($\alpha_\text{edge}$):「no edge enhancement」($\alpha = 0$) 與 default ($\alpha = 0.95$) 平均 ATE 差距僅為 64.711 vs. 64.936;「slight」 ($\alpha = 0.5$) 與 default 完全相同。這顯示 edge shading 對最終 ATE 影響非常小,本質上更像是視覺化的選擇而非必要組件。
- **Sim(3) vs. SL(4) back-end** (附錄 A6 + Table 1, 6):SL(4) 在多個 KITTI/EuRoC 長序列上完全 **未收斂** (Table 1 的 N/A,Table 6 的「–」)。這是真正具有診斷力的對照,直接支持選擇 7-DoF Sim(3) 的設計決策。
- **缺漏的關鍵 ablation**:論文沒有單獨拆解 (a) DEM-augmented covisibility graph vs. 原生 AnyLoc per-frame retrieval、(b) 高頻 LBA 本身的貢獻 (例如關掉 back-end LBA、只保留 odometry 的 ATE)、(c) DINOv2 與其他 encoder 的差異。這幾項才是支撐核心貢獻的診斷實驗,目前較像是用 baseline 的整體 ATE 提升 (18.6%) 來「總結性」交代,而非分項拆解貢獻來源。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — Tables 1–4 與附錄 Table 6 同時比較了 ORB-SLAM2/3、DROID-SLAM、DPV-SLAM++、MASt3R-SLAM、GO-SLAM、CUT3R、NICER-SLAM 與直接前身 VGGT-SLAM,涵蓋 classical 與 transformer-based 的最新 SoTA。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 共在 KITTI、TUM RGB-D、7-Scenes、Virtual KITTI、EuRoC 五個公開資料集加上多組自錄資料 (GoPro/OAK-1) 上評估,涵蓋室內/戶外、RGB/grayscale、planar/long-horizon。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — Table 5 主要在 DEM rendering 超參數 (reducer / $\tau$ / 解析度 / edge) 上掃描,且多數差異 < 0.3 m;真正診斷性的 covisibility graph 移除、back-end LBA 開關、DINOv2 替換、AnyLoc 替換等實驗皆缺席。Sim(3) vs. SL(4) 的對照算是一個有效診斷。
- [missing] Has a scaling study (size, length, or compute) — 論文未系統性掃描 submap 大小 $w$、tile 物理尺寸 ($2 \times 2$ m)、Top-K、序列長度或 submap 數量對精度/吞吐的影響。
- [partial] Has an efficiency / wall-clock comparison — 報告了自身 front-end ∼16 FPS、back-end 1.89 FPS、∼20 GB VRAM / ∼8 GB RAM,並與 DROID-SLAM 的 8 GB front-end + 24 GB back-end 做粗略對照,但未提供統一硬體下的逐方法 wall-clock/FPS 表。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 表格皆為單次數值,沒有 std / 多 seed;唯一的「±」出現在自錄 GoPro 序列,且為 GPS ground truth 的 2 m 量測精度,不是方法本身的變異。
- [missing] Releases code / weights / data sufficient for reproducibility — 論文未在內文或附錄提及 code repository、模型權重或資料集的釋出位置;the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 緊湊且 DINOv2-相容的 DEM-augmented map representation。** 部分支持。Fig. 5A–C 的 zero-shot GroundingDINO 偵測提供了結構保真度的定性證據,Table 2 的 `floor` 場景提供了平面退化緩解的量化證據;但缺乏 retrieval recall@k 或 descriptor 區分性指標來量化「DINOv2-相容」這一主張。
- **Claim 2: Covisibility graph 經 local affine structure 搜尋,降低 loop detection 的搜尋空間與時間。** 未驗證。論文沒有給出 FAISS-HNSW 在不同資料集上的查詢延遲、recall 或被過濾掉的候選比例,亞線性記憶體成長僅以 HNSW 的理論性質帶過 (Appendix A4)。
- **Claim 3: 高頻 LBA 抑制 loop event 之間的漂移。** 部分支持。Tables 1–4 的 net ATE 改善與此一致,但沒有任何 plot 顯示「兩次 loop 之間的 drift 曲線」對比,也沒有將 VGGT-SLAM 強制以同樣 cadence 跑 LBA 作為對照,因此「高頻 LBA」與「DEM 提供的更好邊」兩個因素被混淆。
- **Claim 4: 加速 graph convergence。** 過度宣稱。文中沒有任何 convergence curve、iteration count 或時間到收斂的對比實驗。
- **Claim 5: SOTA accuracy on uncalibrated RGB,與 calibrated 系統可比。** 對 RGB 資料集成立 (Tables 2, 3);但放到 EuRoC monochrome,DROID-SLAM 的 0.013–0.043m 對比本文的 1.6–4.15m (Table 6),稱 SOTA 在範圍上是過度延伸的。

### 7.2 Fundamental Limitations of the Method

DEM canonicalization 假設整個 submap 存在「單一全域主導平面」,以 RANSAC 擬合 $n^\top p + d = 0$ 並做 top-down discretization。對多層樓、樓梯、陽臺、地形分塊或室內+室外混合的場景,這個 2.5D 高度場無法表達,因而結構上限縮在 road-like 與 floor-like 場景;這不是 hyperparameter 問題,而是表徵本身的容量問題。

整個系統的精度上限被 VGGT 的可用性鎖死。EuRoC monochrome 結果證明,當前端幾何來源失效時,「空間矯正」後端無論 LBA cadence 多高都無法救回軌跡——後端能修正的是 pose graph 的不一致,而不是 depth/pose 估計本身的偏差。論文以「為訓練資料分布之外」概括此事,但這實際上揭示後端定位精度與前端 backbone 的訓練分布是強耦合的。

Covisibility 的篩選只到 FAISS-HNSW + AnyLoc 的 appearance 相似度為止,沒有再做 geometric verification(例如基於 3D 點雲的 RANSAC 對齊或 reprojection 檢查)。一旦 DINOv2 在某類紋理上產生 false positive(例如對稱建築立面、重複地磚),其相似度分數會直接以 $\Sigma_{ij}$ 形式進入 Sim(3) 最佳化目標 (Eq. 4),而 $\Sigma_{ij}$ 本身又由相同描述子衍生——這形成一個無 outlier rejection 的閉環。

Cadence 失衡只是被縮小:前端 16 FPS、後端 1.89 FPS 仍存在 $\sim$8.5× 落差。在快速移動或視角劇變下,後端依然落後多個 keyframe 才能完成一次矯正,意味著「short-term drift suppression」實際上是「中等時間尺度 drift suppression」,論文敘事與實測的時間常數對不上。

### 7.3 Citations Worth Tracking

- **[50] Maggio et al., VGGT-SLAM (arXiv:2505.12549)**:直接前身,本文所有 baseline 數字都以它為基準,理解其原始公式才能判斷本文增益是否來自 LBA cadence 而非 DEM。
- **[83] Wang et al., VGGT (CVPR 2025)**:整個 pipeline 的 geometry oracle,其在 monochrome 的失敗模式直接決定了本系統的精度上限。
- **[28] Harithas et al., FinderNet (WACV 2024)**:DEM canonicalization 的思想來源,本文作者之一即 FinderNet 共同作者;對照閱讀可看出哪些 design choice 是純粹移植、哪些是針對 RGB submap 的新發明。
- **[33] Keetha et al., AnyLoc (RAL 2023)**:VPR 模組,其在 DEM 影像域上的描述子行為決定了 covisibility window 內的 false positive 率。
- **[56] Murai et al., MASt3R-SLAM (CVPR 2025)**:本文 Tables 中最強的學習式 baseline,理解其 Iterative Sinkhorn matching 才能判斷 transformer-based SLAM 在哪些指標上仍未飽和。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 將 VGGT-SLAM 強制以本文的 LBA cadence (1.89 FPS) 跑、但保留其全域 loop closure 機制,精度差距是否仍然存在?亦即 DEM-DINOv2 retrieval 與「LBA 開得更勤」誰是真正的 driver?
- [ ] TUM `plant` 場景為何由 0.022m 退化到 0.042m?是 DEM 在近平面葉片上 RANSAC 擬合失敗,還是 AnyLoc 在重複紋理上產生 false positive 把錯誤約束注入 Eq. 4?
- [ ] FAISS-HNSW 的 recall@k 與查詢延遲在 viewpoint change vs illumination change 下分別是多少?論文聲稱亞線性卻無實測曲線。
- [ ] 從 loop edge 被偵測到 Sim(3) 完成更新並反映於前端追蹤之間的端到端 latency 是多少?「高頻矯正」的時間常數需要被量化。
- [ ] 在多層樓、樓梯、室內外切換等違反「單一主導平面」假設的場景下,系統會以什麼模式失效——RANSAC 不收斂、DEM 變成兩個錯位面、還是 retrieval 完全找不到鄰居?
- [ ] FAISS-HNSW index 在小時級長序列下是否真的 bounded?768 維 × 每 submap N tiles 在無移除策略下的成長曲線實測為何?
- [ ] 若把 VGGT 換成 MapAnything [34] 或 MASt3R [56],本文報告的 18.6% 增益是否仍轉移?還是它與 VGGT 特定的 noise 模式糾纏在一起?

### 8.2 Improvement Directions

1. **(高可行性) 拆開 cadence 與 retrieval 兩個變因的 ablation**:跑兩個對照組——(a) VGGT-SLAM + 1.89 FPS LBA(無 DEM)、(b) VGGT-SLAM++ 但 LBA 降到原 VGGT-SLAM 的 cadence——以分離「LBA 開得勤」與「DEM 提供更好的邊」對 ATE 的個別貢獻。論文目前完全沒有此拆解。
2. **(高可行性) 在 covisibility edge 進入 Sim(3) 最佳化前加 geometric verification**:對候選 (i, j) submap pair 做基於 3D 點雲的 RANSAC 對齊或 reprojection-error 檢查,只接受幾何一致的邊。這直接對應 §7.2 指出的「相似度同時當邊權重又當門檻」的閉環問題,且不需要重新訓練任何模型。
3. **(中可行性) 多層 DEM (stratified 2.5D × N layers)**:對單一 submap 擬合多個主導平面或以高度直方圖切片,使樓梯、陽臺、多樓層室內可以被表達。這把表徵的容量限制(§7.2 第一段)擴展到目前範圍之外的場景。
4. **(中可行性) 在 DEM 影像上 fine-tune 一個輕量 head 接到凍結的 DINOv2 之後**:DINOv2 訓練分布為自然影像而非 height field,加上小型 head 用 contrastive loss 對齊「同地點不同視角的 DEM tile」應能顯著提升 retrieval recall,對 monochrome 來源的 DEM 尤其有用。
5. **(中可行性) 對 Σij 的不確定性建模解耦 descriptor consistency**:目前 $\Sigma_{ij}$ 由 descriptor consistency 與 3D alignment residual 同時決定,這使前者既當邊也當權重。改為以 alignment residual 與 inlier ratio 為主導、descriptor 僅作為 gating 條件,可降低 self-confirming 的風險。
6. **(較低可行性) 在 grayscale/低光資料上 fine-tune VGGT 或加上 photometric augmentation pretrain**:這能直接攻克作者承認的 EuRoC 失效模式,但需要 retrain 上游模型,工程與計算成本較高。
