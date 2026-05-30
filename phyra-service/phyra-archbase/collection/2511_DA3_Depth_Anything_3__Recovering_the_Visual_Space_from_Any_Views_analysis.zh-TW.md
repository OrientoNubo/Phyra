<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# Depth Anything 3 — Depth Anything 3: Recovering the Visual Space from Any Views

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | Depth Anything 3 |
| Paper full title | Depth Anything 3: Recovering the Visual Space from Any Views |
| arXiv ID | 2511.10647 |
| Release date | 2025-11-13 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2511.10647 |
| PDF link | https://arxiv.org/pdf/2511.10647v1 |
| Code link | https://github.com/ByteDance-Seed/Depth-Anything-3 |
| Project page | https://depth-anything-3.github.io |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Haotong Lin | ByteDance Seed | https://haotongl.github.io/ | first author / equal contribution |
| Sili Chen | ByteDance Seed | — | equal contribution |
| Jun Hao Liew | ByteDance Seed | — | equal contribution |
| Donny Y. Chen | ByteDance Seed | — | equal contribution |
| Zhenyu Li | ByteDance Seed | — | co-author |
| Guang Shi | ByteDance Seed | — | co-author |
| Jiashi Feng | ByteDance Seed | — | co-author |
| Bingyi Kang | ByteDance Seed | https://bingyikang.com/ | corresponding author / project lead / equal contribution |

### 1.2 Keywords

any-view geometry, monocular depth estimation, camera pose estimation, depth-ray representation, plain transformer, DINOv2, teacher-student learning, feed-forward 3D Gaussian Splatting

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Depth Anything 2 (Yang et al., 2024) | predecessor | Direct predecessor in the Depth Anything series; DA3 outperforms it on monocular depth while extending to any-view inputs. |
| VGGT (Wang et al., 2025) | baseline | Prior SOTA visual geometry transformer; DA3 surpasses it by 35.7% pose and 23.6% geometry accuracy on the new benchmark. |
| DUSt3R (Wang et al., 2024) | influence | Pioneering transformer that regresses point maps from two views; founds the feed-forward multi-view geometry paradigm DA3 builds on. |
| Pi3 | baseline | Concurrent any-view geometry model used as a comparison baseline across pose and reconstruction metrics. |
| DINOv2 (Oquab et al., 2023) | base model | Vanilla pretrained ViT used unchanged as DA3's single plain transformer backbone. |
| DPT (Ranftl et al., 2021) | influence | Dense prediction transformer head architecture extended into the dual-DPT depth+ray prediction head. |
| MVSplat / pixelSplat-style feed-forward 3DGS (Chen et al., Charatan et al.) | baseline | Specialized feed-forward 3D Gaussian Splatting baselines outperformed by fine-tuning DA3 for FF-NVS. |

## 2. Research Overview

### 2.1 Research Topic

本研究聚焦於從任意數量、任意配置的視覺輸入(單張影像、多視角影像或影片串流,且相機姿態可有可無)中,重建出空間一致的三維幾何結構。作者將此任務統一為一個密集預測問題:同時輸出每個輸入像素對齊的深度圖與射線圖,藉此隱式地表達相機姿態並避免旋轉矩陣的正交性限制。研究範疇橫跨 monocular depth estimation、multi-view stereo、structure-from-motion、camera pose estimation 與 feed-forward novel view synthesis,並建立了一個涵蓋 5 個資料集、89 個場景的 visual geometry benchmark,以及一個包含 160 多個場景的 feed-forward NVS 基準,以系統性地評估泛化幾何模型在多項三維視覺任務上的能力。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- Multi-View Geometry
- Monocular Depth Estimation
- Novel View Synthesis

### 2.3 Core Architectures Used

- **Plain Vision Transformer backbone (vanilla DINOv2)**:作為 DA3 的單一骨幹網路,直接沿用大規模預訓練的 ViT 而不做任何架構特化,負責從每張輸入影像抽取 patch tokens,並繼承預訓練模型的 scaling 特性。
- **Input-adaptive cross-view self-attention**:在 backbone 的後段層中以 token 重排方式交替執行 within-view 與 cross-view attention(層數比 $L_s : L_g = 2 : 1$),使單一 transformer 能同時處理單張影像、多視角集合與影片輸入。
- **Camera encoder (lightweight MLP $E_c$)**:將已知的 FOV、四元數 $q_i$ 與平移 $t_i$ 編碼為每視角一個 camera token $c_i$,與 patch tokens 串接後參與所有 attention,使模型能無縫處理 posed 與 unposed 輸入。
- **Dual-DPT head**:在 DPT 架構基礎上分支出兩組 fusion layers 與輸出層,以共享的 reassembly modules 同時預測 depth map 與 ray map(包含 ray origin 與 direction),保留密集預測的對齊性。
- **Camera head $D_C$**:輕量 transformer,僅作用於每視角的 camera token 上,直接回歸 $(f, q, t)$,以避免在推論時從 ray map 反解 homography 的計算成本。
- **Monocular teacher (DINOv2 + DPT decoder)**:作為 teacher-student 範式中的 teacher,僅在合成資料上訓練、預測 scale–shift-invariant exponential depth,提供高品質 pseudo-label 對齊真實資料的稀疏/雜訊深度。
- **GS-DPT head (3DGS 應用)**:在 DA3 上額外微調的 DPT head,輸出每像素對齊的 3D Gaussian 參數 $\{\sigma_i, q_i, s_i, c_i\}$,將 DA3 轉為 feed-forward 3DGS 的最佳骨幹。

### 2.4 Core Argument

作者指出,當前統一的三維視覺模型雖試圖以一個架構處理多項任務,卻陷入兩個根本問題:其一,它們依賴複雜且任務專屬的多分支架構(例如 VGGT 的多階段設計與冗餘輸出頭),難以從大型預訓練模型中受益;其二,它們以 point map、global/local point map、pose、depth 等多重輸出做聯合訓練,看似互補,實際上產生 entanglement,反而降低姿態與幾何精度。Depth Anything 3 主張回到最小化建模:只需一個 plain transformer(直接採用 vanilla DINOv2,不做架構改造)做為骨幹,只需一個 depth-ray 表示做為預測目標——以每像素的射線原點與方向取代難以正規化的旋轉矩陣,即能保留相機姿態與投影尺度,並透過逐元素運算融合為一致點雲。為支援任意視角數,作者僅插入一個 input-adaptive cross-view self-attention 模組,並以 dual-DPT head 同時輸出深度與射線。為解決真實深度資料品質不足的問題,作者進一步以 teacher-student 範式,先在合成資料上訓練強力的 monocular teacher,再用其偽標籤對齊原始稀疏/雜訊深度,以保留幾何完整性同時提升細節。此一最小化策略之所以邏輯上必要,是因為唯有移除架構特化與多任務冗餘,才能直接繼承大型預訓練 backbone 的 scaling 能力,並讓單一目標的學習訊號集中、避免跨任務梯度干擾,從而以更簡潔的設計同時在 18/20 個視覺幾何設定上達到 SOTA、超越專門化的 monocular 模型,並成為 feed-forward 3DGS 的最佳骨幹。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(220 words)

標題「Depth Anything 3: Recovering the Visual Space from Any Views」一次點出三件事：這是 Depth Anything 系列的第三代、模型目標是「recover visual space」、輸入形式為「any views」。前兩代僅處理單張影像（monocular depth），DA3 把命題擴展到任意視角數量，並在腳註明確聲明「depth is the cornerstone of understanding the physical world」，把這篇論文定位成一次世代躍遷而非小幅修訂。

Abstract 的論述結構刻意走 minimal modeling 路線。作者先擺出問題：給定任意數量影像（含或不含已知 camera pose），預測 spatially consistent geometry。接著拋出兩個核心 insight：(1) 一個 plain transformer（如 vanilla DINO encoder）就足夠當 backbone，不需要架構特化；(2) 一個 depth-ray prediction target 就足以避開 multi-task learning 的複雜度。這兩點直接對應 §3 的方法論貢獻。

第三段交代訓練策略——teacher-student paradigm——並指出最終達到與 DA2 相當的 detail 與 generalization。第四段是量化成果：建立新的 visual geometry benchmark 涵蓋 camera pose estimation、any-view geometry、visual rendering 三種任務；DA3 在 pose accuracy 上比 SOTA VGGT 平均高 35.7%、reconstruction 高 23.6%；單張深度也勝過 DA2。最後特別強調訓練資料全為公開學術資料集。

Abstract 的鋪陳實際上把全篇骨架攤平：問題定義 → 兩個 minimal modeling 假設 → teacher-student 訓練 → benchmark 與量化勝出，為 §1 Introduction 把問題推向「為什麼這兩個假設值得驗證」鋪好了動機線。

### 3.2 Introduction

(673 words)

Introduction 走「動機 → 質疑既有 paradigm → 提出兩個極簡假設 → 條列具體貢獻」的四段式論證。第一段把 3D 空間感知定位為 human spatial intelligence 的基石，列舉 monocular depth、SfM、MVS、SLAM 等任務並指出它們之間概念高度重疊（常常只差 input view 數量），但 prevailing paradigm 卻是各任務各自開發專門模型。即使近期有 unified models（如 [91, 97]）嘗試合一，仍依賴 bespoke architectures、from-scratch joint optimization，無法善用 large-scale pretrained models——這就是要被打掉的稻草人。

第二段抽離既有 task 定義，回到「從任意視覺輸入恢復 3D 結構」這個更基本的目標，並把 minimal modeling 拆成兩個問句：是否存在 minimal prediction target，還是必須 joint modeling 多個任務？單一 plain transformer 是否足夠？兩個問題的答案都是 yes，而 DA3 就是用 specially chosen ray representation 來做 joint any-view depth and pose estimation 的單一 transformer。這段是全篇的論點核心，後續所有實驗都在驗證這兩個 yes。

第三段把方法落地：N 張輸入影像 → N 張 depth map 與 ray map（pixel-aligned）；backbone 用標準 pretrained ViT（DINOv2 風格）；關鍵架構修改是 input-adaptive cross-view self-attention，靠 token rearrangement 在選定層做跨視角資訊交換；prediction head 採新的 dual DPT，共享 feature backbone 但用不同 fusion 參數同時輸出 depth 與 ray；可選的 camera encoder 讓模型也能吃已知 pose。整段刻意強調 clean and scalable，繼承 backbone 的 scaling 性質，這直接呼應 abstract 第一個 insight。

第四段轉到資料策略。real-world depth（如 Baruch et al. 5、Reizenstein et al. 68）品質參差（Fig. 4），合成資料則覆蓋有限。作者採 pseudo-labeling：先在合成資料上訓一個強的 monocular teacher，再用它對 real-world data 生成 dense pseudo-depth，並透過 RANSAC scale-shift 對齊原始 sparse/noisy depth 以保留 geometric integrity。這段為 §4 Teacher-Student Learning 鋪好了動機。

第五段是 benchmark 貢獻：5 個資料集、超過 89 個 scenes，從 object-level 到 indoor/outdoor，直接量測 pose accuracy 並把預測 pose 與 depth 融合成 3D point cloud 來算 reconstruction accuracy。DA3 在 18/20 設定取得 SOTA，monocular depth 也勝過 DA2。

第六段把貢獻擴展到 FF-NVS：另外建一個含 160+ scenes 的 benchmark，僅在 backbone 上加一個 DPT head 預測 pixel-aligned 3D Gaussian，得到兩個發現——fine-tune geometry foundation model 大幅勝過 task-specific 設計；geometry 能力與 NVS 表現正相關。這直接把 DA3 推銷為 3D 視覺的通用 backbone，為 §5 Application 預埋伏筆。

### 3.3 Related Work / Preliminaries

(675 words)

§2 Related Work 切成三條敘事線，每條都用「傳統 → 早期學習 → transformer 時代 → 我們的差異化」結構走，目的是讓讀者一眼看出 DA3 在哪裡接棒、又在哪裡刻意走輕量路線。

第一條 Multi-view visual geometry estimation 從傳統 SfM/MVS pipeline（feature detection、matching、bundle adjustment、cost-volume MVS）談起，指出模組化在 well-textured 場景強健，但在 low texture、specular、大視角變化下脆弱。早期學習方法只是在元件層注入 robustness（learned detectors [20]、descriptors [22]、differentiable optimization layers [31, 33, 62]）；MVS 端則用 cost-volume networks [106, 114] 取代手刻 regularization。早期 end-to-end [86, 90] 雖然減少 engineering 複雜度，但卡在 scalability、generalization、處理任意輸入數量。轉折點是 DUSt3R [96]：用 transformer 直接預測兩視角間的 point map 並一起拿到 depth 與 relative pose。後續工作沿此擴展到 multi-view [10, 85, 94, 110]、video [19, 59, 94, 121]、correspondence [48]、camera 注入 [39, 43]、large-scale SfM [18]、SLAM [54]、3DGS view synthesis [11, 13, 41, 79, 108, 122]。代表作 [91]（即 VGGT）以 large-scale 訓練、multi-stage 架構與 redundancy 推到新高。DA3 在這條軸上明確標出自己的差異化定位：a minimal modeling strategy built around a single, simple transformer，把 §1 的 minimal 主張具體化。

第二條 Monocular depth estimation 回顧早期單域監督式方法（NYU 室內 [75]、KITTI 駕駛 [26]）難以跨域，到 modern generalists [6, 42, 95, 112, 113, 118] 倚賴 multi-dataset 訓練、ViT [67]、DiT [64] 與 affine-invariant depth normalization 等技術。作者立場很清楚：DA3 主要是為 unified visual geometry 設計，不是專做 monocular，但仍能達到 competitive monocular 表現——這是後面 §7.3 student model 的伏筆。

第三條 Feed-Forward Novel View Synthesis 從 NVS 的歷史 [8, 34, 49] 與 neural rendering 興起 [28, 44, 57, 77, 78] 切入，鎖定 feed-forward NVS 的吸引力（避免 per-scene optimization）。早期用 NeRF [12, 14, 35, 52, 107, 119]，近期改用 3DGS。代表手法以 epipolar attention [11]、cost volume [13]、depth prior [107] 等 geometry prior 強化 image-to-3D network；更近期則整合 multi-view geometry foundation model [85, 91, 96, 110]。問題是現有評估常綁在「單一 chosen foundation model」上 [41, 79, 116]。作者於是定位自己的工作：systematically benchmark 不同 geometry foundation model 對 NVS 的貢獻，並提出策略讓 feed-forward 3DGS 能同時處理 posed/pose-free、變動 view 數、任意解析度——這直接為 §5 與 §7.5 的 benchmark 設計鋪路。

論文沒有獨立的 Preliminaries 章節，幾何形式化挪到 §3.1 Formulation：以 $I=\{I_i\}_{i=1}^{N_v}$、深度 $D_i$、外參 $[R_i\,|\,t_i]$、內參 $K_i$ 與相機向量 $v_i\in\mathbb{R}^9$（含 $t_i$、quaternion $q_i$、FOV $f_i$）建立投影關係 $P=R_i(D_i(u,v)K_i^{-1}p)+t_i$。三條 Related Work 主軸與這個 formulation 共同把讀者推進 §3 的核心：用 depth-ray 取代 rotation matrix、用單一 transformer 統一所有任務的設計合理性。

### 3.4 Method (overview narrative)

(1480 words)

§3 Depth Anything 3 與 §4 Teacher-Student Learning 共同構成方法主體，敘事可拆成「形式化 → 架構 → 訓練範式 → 教師模型生態」四步。

§3.1 Formulation 先處理表示法選擇。直接 regress rotation matrix $R_i$ 受到 orthogonality 約束限制，作者改用 per-pixel ray map $r=(t,d)\in\mathbb{R}^6$，其中方向 $d=RK^{-1}p$ 故意不 normalize 以保留 projection scale，使世界座標點直接寫成 $P=t+D(u,v)\cdot d$。這個選擇讓 depth map 與 ray map 透過 element-wise 運算就能融合成 consistent point cloud。為了在 inference 端能拿回顯式相機參數，作者把 ray map 反推 camera 的問題轉成解 homography $H=KR$，先平均 ray origin 得到 camera center $t_c$，再用 DLT 解最小化 $\sum\|Hp_{h,w}\times M(h,w,3:)\|$，最後對 $H^*$ 做 RQ decomposition 取得 $K$、$R$。第三小節 minimal prediction targets 是論點轉折：作者明確反對 [91, 94, 110] 那類冗餘 multi-target（同時 pose、local/global point map、depth），主張 depth-ray 已是 minimal yet sufficient 的目標集合，並補一個極輕量 camera head $D_C$（只處理 1 個 token/view）來避免 inference 時解 ray map 的計算成本。

§3.2 Architecture 把上述形式化落到三個元件。Backbone 是 $L$ 層 ViT（DINOv2 預訓練），不改架構，靠 input-adaptive self-attention 達成跨視角推理：前 $L_s$ 層做 within-image self-attention，後 $L_g$ 層交替 cross-view 與 within-view，靠 tensor reordering 完成。預設 $L_s:L_g=2:1$，根據 Tab. 7 ablation 取得效能與效率最佳折衷。設計刻意讓單張影像時自然退化成 monocular depth，不付額外成本。Camera condition injection 在每個 view 前置一個 camera token $c_i$；若有相機參數 $(K_i, R_i, t_i)$ 就用 MLP $E_c$ 編碼為 $c_i=E_c(f_i,q_i,t_i)$，否則用共享可學 token $c_l$。Dual-DPT head 接收 backbone feature，先共用一組 reassembly modules，再分兩組 fusion layers（depth 分支與 ray 分支），最後兩個 output layers 給出 depth 與 ray map——共享 reassembly 又分支 fusion 的設計鼓勵兩個任務互相加強又避免 redundant intermediate representation。

§3.3 Training 的核心是 teacher-student paradigm：因為訓練資料來源混雜（real-world depth、3D reconstruction、合成），real-world depth 多半 noisy or sparse（Fig. 4），所以先在合成資料上訓 monocular relative depth teacher（即 Depth-Anything-3-Teacher），再用 RANSAC least squares 將 teacher 的 dense pseudo-depth 與原始 sparse/noisy depth 對齊，得到既保留細節又保留 geometric accuracy 的 pseudo label。Loss 設計上，所有 ground truth 先用 valid reprojected point map $P$ 的平均 $\ell_2$ norm 做 scale 正規化，total loss 是 $L = L_D(\hat{D},D) + L_M(\hat{R},M) + L_P(\hat{D}\odot d + t, P) + \beta L_C(\hat{c}, v) + \alpha L_{\text{grad}}(\hat{D}, D)$；$L_D$ 帶 confidence $D_{c,p}$ 與 $-\lambda_c \log D_{c,p}$ 規範項，$L_{\text{grad}}$ 用 horizontal/vertical finite difference 保邊。

§3.4 Implementation Details 給訓練配方：128 個 H100、200k steps、8k warm-up、peak lr $2\times10^{-4}$；base resolution 504×504（被 2、3、4、6、9、14 整除以相容常見比例），訓練尺寸從 8 種解析度隨機取樣；504×504 設定下 view 數從 [2, 18] 均勻取樣；batch size 動態調整以維持 token 數約略恆定；120k step 起把監督從 ground-truth depth 切換到 teacher label；pose conditioning 以 0.2 機率 random 啟用。

§4 Teacher-Student Learning 把 teacher 生態完整鋪開。§4.1 Constructing the Teacher Model 在 DA2 基礎上做兩件事：data scaling（加入 Hypersim、TartanAir、IRS、vKITTI2、BlendedMVS、SPRING、MVSSynth、UnrealStereo4K、GTA-SfM、TauAgent、KenBurns、MatrixCity、EDEN、ReplicaGSO、UrbanSyn、PointOdyssey、Structured3D、Objaverse、Trellis、OmniObject 等廣譜合成資料）與 representation 修正（從 DA2 的 scale-shift-invariant disparity 改成 scale-shift-invariant depth，並改為 exponential depth 以加強近距區分度）。Loss 由 ROE alignment global-local loss [95]、distance-weighted surface-normal loss、sky/object mask MSE 組成：normal loss 對 4 個鄰點計算 $w_i=\sum_j\|n_j\|-\|n_i\|$，把 $n_m=\sum w_i n_i/\|n_i\|$ 與 $\hat{n}_m$ 的 angular error 加進 $L_N$。Total $L_T=\alpha L_{\text{grad}}+L_{gl}+L_N+L_{\text{sky}}+L_{\text{obj}}$（$\alpha=0.5$）。

§4.2 Teaching Depth Anything 3 把 teacher 的 relative depth $\tilde{D}$ 用 RANSAC 解 $(\hat{s},\hat{t})=\arg\min\sum m_p(s\tilde{D}_p+t-D_p)^2$，得到 $D_{T\to M}=\hat{s}\tilde{D}+\hat{t}$ 餵給主模型。§4.3 Teaching Monocular Model 與 §4.4 Teaching Metric Model 把同套 teacher 推進到 monocular student（相對 depth）與 metric model（採 Metric3Dv2 [37] 的 canonical camera space 變換、$f^c$ 設 300，14 個資料集，stereo dataset 用 FoundationStereo [100] 預測當 label）。

整個 §3–§4 的敘事節奏是：先用 formulation 證明 depth-ray 為 minimal 表示，再用 architecture 證明 single transformer 為 minimal backbone，最後用 teacher-student 解決資料異質性，三個 minimal 主張環環相扣，把 §1 提的兩個 yes 拼成可訓練的具體系統，並交棒給 §5 把同一 backbone 推廣到 FF-NVS 應用。

### 3.5 Experiments (overview narrative)

(2090 words)

§6 Visual Geometry Benchmark 與 §7 Experiments 在敘事上分工明確：§6 先把評測基礎建好，§7 才開始拿 DA3 做攻防。

§6.1 Benchmark Pipeline 先講 pose 評測流程：對每個 scene 取所有影像、若超量則固定 random seed 取 100 張，餵 feed-forward 模型得到一致 pose 與 depth，再算 pose accuracy。Geometry 評測則進一步：用預測 pose + 預測 depth 重建，再用 evo [87] 把預測 pose 對齊到 GT pose，得到 transformation 把重建拉到 GT 座標系。為強化魯棒性，作者採 RANSAC-based alignment——重複從 pose 子集呼叫 evo，inlier 定義為 translation error 小於整體 deviation 的 median，挑出 inlier 數最多的 transformation 後用 TSDF fusion 融合 aligned point cloud。§6.2 Metrics 寫得很細：pose 用 [89, 91] 的 AUC 協議，由 Relative Rotation Accuracy 與 Relative Translation Accuracy 取 min 對 threshold 積分；主要 report Auc3 與 Auc30。Reconstruction 用 dist(R→G) 算 accuracy、dist(G→R) 算 completeness、平均得 Chamfer Distance；對 threshold $d$ 算 precision 與 recall 後取 F1。Visual rendering 端 PSNR、SSIM、LPIPS。§6.3 Datasets 是這一節的硬骨頭：HiRoom（30 個 Blender 室內場景，TSDF voxel 0.007m、F1 threshold 0.05m）、ETH3D（11 scenes，雷射感測 GT，threshold 0.25、voxel 0.039m）、DTU（22 scans、RMBG 2.0 [126] 去背、用 [124] 的 fusion）、7Scenes（11 倍降 frame、threshold 0.05、voxel 0.007）、ScanNet++（20 scenes、用 laser scan 重建做 GT、threshold 0.05、voxel 0.02、5 倍降 frame）。Visual rendering benchmark 含 DL3DV 140 scenes、Tanks and Temples 6 scenes、MegaDepth 19 scenes，每場景約 300 frame，每 8 張取 1 張當 target、其餘做 farthest point sampling 取 12 張當 input。

§7.1 Comparison with State of the Art 是論文的主要量化亮點。Baseline 包含 VGGT [91]、Pi3 [99]、MapAnything [43]、Fast3R [111]、DUSt3R [96]，作者特別點出 DA3 與 VGGT 立場最近但採新架構與不同 camera representation，與 Pi3 則屬 orthogonal。Pose estimation（Tab. 2）DA3-Giant 幾乎全部最佳，唯一例外是 DTU 的 Auc30；Auc3 至少有 8% 相對提升，ScanNet++ 的 Auc3 比第二名提升 33%。Geometry estimation（Tab. 3）DA3-Giant 在 5 個 pose-free 設定全部贏，整體相對 VGGT +25.1%、相對 Pi3 +21.5%；DA3-Large（0.30B 參數）即便比 VGGT（1.19B）小 3 倍仍在 10 個設定中贏 5 個，ETH3D 上特別亮眼。當 GT pose 可用時，所有方法都能得益、但 DA3 在 7Scenes 因 video 設定已經飽和而未顯著提升；作者指出 pose 條件下 model size scaling 帶來的增益小於 pose-free，顯示 pose estimation 比 depth estimation 更需要大模型。Monocular depth（Tab. 4）DA3 也勝 DA2 與 VGGT，teacher 排第一。Visual rendering（Tab. 5）對手分兩組：純 3DGS 模型 pixelSplat、MVSplat、DepthSplat 與替換 backbone 後的 Fast3R、MV-DUSt3R、VGGT。所有模型在 DL3DV 都比 OOD 資料表現好，顯示 3DGS-based NVS 對 trajectory/pose 分佈敏感；geometry-based 框架普遍勝過 task-specific 設計，且 NVS 表現與 geometry 能力正相關，DA3 是最強 backbone。

§7.2 Analysis for Depth Anything 3 把 §1 的兩個 yes 各自轉成 ablation。§7.2.1 Sufficiency of the Depth-Ray Representation（Tab. 6）以 ViT-L、view 10、batch 128、120k step 比較四種 head 組合：depth+pcd+cam、depth+cam、depth+ray、depth+ray+cam。結論是 depth+ray 在所有資料與指標上都打贏 depth+pcd+cam 與 depth+cam，相對 depth+cam 在 Auc3 上幾乎 100% 相對提升；加上 cam 變成 depth+ray+cam 在指標上沒進一步收益，但因為 camera head 只佔約 0.1% backbone 計算量，作者選 depth+ray+cam 作最終配置。§7.2.2 Sufficiency of a Single Plain Transformer（Tab. 7 a–c）把標準 ViT-L backbone 與 VGGT-style 雙 transformer（block 數三倍、用 ViT-B 對齊容量）比較；VGGT-style 表現掉到 baseline 的 79.8%，作者歸因於自家 backbone 全部 pretrained，VGGT-style 有 2/3 區塊未預訓練。Full Alt.（每層都交替 cross-view/within-view）也比 partial alternation 差（除了 7Scenes F1），確認 partial alternation 的設計合理性。

§7.2.3 Ablation and Analysis 接著拆其他元件：Dual-DPT head（Tab. 7 d）改成兩個獨立 DPT 後在多項指標上整體掉，確認 shared reassembly + 分支 fusion 的價值。Teacher supervision（Tab. 7 e、Fig. 8）拿掉 teacher label 後 DTU 略升，但 7Scenes、ScanNet++、特別是 HiRoom（合成、富細節）顯著掉，定性比較顯示 teacher 監督讓 depth map 細節明顯更豐富。Pose conditioning（Tab. 7 f、g）在 ground-truth pose fusion 評測下啟用 pose 條件全面更佳。Tab. 8 給 runtime 與容量分析：VGGT 一張 A100 80GB 可裝 400-500 張、34.1 FPS；DA3-Giant 容量 900-1000、37.6 FPS；DA3-Large 1500-1600 / 78.37 FPS；DA3-Base 2100-2200 / 126.5 FPS；DA3-Small 4000-4100 / 160.5 FPS——同等或更好效能下顯著更快、更省記憶體。Fig. 9 補野外場景（長城、Colosseum、自由女神）的 pose 與 depth 視覺化，秀魯棒性。

§7.3 Analysis for Depth-Anything-3-Monocular 分 teacher 與 student 兩段。§7.3.1 Teacher（Tab. 9）以 ViT-L、batch 64 跑 ablation：data 從 V2 升 V3 再加 multi-resolution 帶來 $\delta_1$ 從 0.919 到 0.938 的進步；geometry 比較 disparity、point map、depth 三種，depth AbsRel/SqRel 最佳；loss 比較 MAE-Loss、無 distance normalization 與 full loss，full loss 勝出。§7.3.2 Student（Tab. 10）顯示 monocular student 在 KITTI、NYU、SINTEL、ETH3D、DIODE 上都勝 DA2，ETH3D 提升超過 10%、SINTEL +5.1%。

§7.4 Analysis for Depth-Anything-3-Metric（Tab. 11）對手是 DepthPro [7]、Metric3D v2 [37]、UniDepthv1 [65]、UniDepthv2 [66]，benchmark 是 NYUv2、KITTI、ETH3D、SUN-RGBD、DIODE indoor。DA3-metric 在 ETH3D 取得 SOTA（$\delta_1=0.917$、AbsRel=0.104，比 UniDepthv2 的 $\delta_1=0.863$ 大幅領先）、SUN-RGBD AbsRel 0.105 最佳、DIODE 第二好；UniDepthv1/v2 在 NYUv2 與 KITTI 仍領先。Ablation 顯示拿掉 teacher 監督後 NYUv2/KITTI 數字微升、其他資料持平，但 Fig. 10 視覺化證實 teacher 帶來 sharper 邊緣與細節——「teacher 提供超越標準 metric 的 complementary knowledge」。

§7.5 Analysis for Feed-forward 3DGS 補完 NVS 端的對比公平性：所有 baseline 重新訓練、對齊 12 input context view 的 farthest point sampling 設定，採用 flash attention 與 fully shared data parallelism；除 pixelSplat 因 epipolar attention 慢只訓 100k step，其他在 8 張 A100 上訓 200k step、batch 1，並都加 depth loss 穩定收斂。Fig. 11 視覺化指出 DA3 在細結構（前/後 column 的柱子）與大尺度戶外 wide-baseline 場景（最後兩個場景）表現特別好，呼應 §7.1 的量化結論。

整個 §6–§7 的敘事閉環：先把 benchmark（資料、指標、流程）定義清楚 → 主結果證明 DA3-Giant 全面領先且 DA3-Large 以小博大 → 兩個 sufficiency ablation 單獨驗證 §1 兩個 yes → 其餘 ablation 補完 dual-DPT、teacher、pose conditioning 等子模組 → monocular、metric、3DGS 三條應用線都驗證同一 backbone 可橫掃，把 §3–§5 的方法論主張一次接上實證。

### 3.6 Conclusion / Limitations / Future Work

(155 words)

§8 Conclusion and Discussion 一頁不到，敘事節奏是「概括三個 minimal 主張 → 重述 benchmark 戰績 → 開放未來方向」。第一段先把方法精煉成一句宣言：plain transformer + depth-and-ray target + teacher-student supervision 即可 unify any-view geometry，無需 ornate architecture。Scale-aware depth、per-pixel ray、adaptive cross-view attention 三件事一起讓模型既繼承 pretrained feature 又輕量易擴。第二句把成績對齊回 §7：在 visual geometry benchmark 上 pose 與 reconstruction 都刷新紀錄，giant 與 compact 兩種變體皆勝過先前模型；同一 backbone 還能驅動高效率的 feed-forward NVS。

第二段定位 DA3 為「versatile 3D foundation model」的一步。Future work 列三條：擴展到 dynamic scenes、整合 language 與 interaction cues、探索更大規模 pretraining 來閉合 geometry understanding 與 actionable world model 的迴圈。論文沒有獨立 Limitations 章節，未明確列舉缺陷；訓練全用公開學術資料、模型與 benchmark 將釋出，以促進 general-purpose 3D perception 的後續研究。

## 4. Critical Profile

### 4.1 Highlights

- 提出 depth-ray representation:以每像素的射線原點 $t \in \mathbb{R}^3$ 與方向 $d \in \mathbb{R}^3$ 隱式編碼相機姿態,迴避 rotation matrix 的正交性約束,並透過 $P = t + D(u,v) \cdot d$ 以逐元素運算融合一致點雲(§3.1)。
- 直接採用 vanilla DINOv2 作為 backbone,未對 transformer block 做任何架構改造,僅以 token rearrangement 引入 input-adaptive cross-view self-attention(§3.2、Fig. 2)。
- Dual-DPT head 共享 reassembly modules、僅在 fusion 階段分流為 depth 與 ray 兩支,Tab. 6 顯示 depth + ray 配置相對 depth + cam 在 Auc3 上有近 100% 的相對提升(§3.2、Fig. 3)。
- 在新提出的 visual geometry benchmark(5 datasets、89 scenes)18/20 設定上達 SOTA,平均 pose accuracy 比 VGGT 高 35.7%、geometry accuracy 高 23.6%(Abstract、Tab. 2、Tab. 3)。
- DA3-Large(0.36B)以 1/3 參數規模在 5/10 設定上勝過 VGGT-1.19B,DA3-Giant 在 ScanNet++ 上 Auc3 比次佳模型有 33% 相對提升(§7.1、Tab. 2)。
- Monocular depth 上 DA3 同時超越 DA2 與 VGGT,例如 KITTI $\delta_1$ 由 DA2 的 94.6 提升至 95.3、ETH3D 由 86.5 提升至 98.6(Tab. 4)。
- 透過 teacher-student paradigm 以合成資料訓練 monocular teacher,再以 RANSAC scale-shift 對齊真實資料的稀疏/雜訊深度(Eq. 8),Fig. 8 顯示細節結構顯著改善。
- DA3-Giant 推論速度 37.6 FPS 略快於 VGGT 的 34.1 FPS,且在 80GB A100 上可處理 900–1000 張影像(VGGT 僅 400–500 張),DA3-Small 更可達 4000+ 張(Tab. 8)。
- 以 GS-DPT head 微調的 FF-NVS 變體在 DL3DV 上 PSNR 達 21.33,優於 pixelSplat、MVSplat、DepthSplat 等專門化 3DGS 模型(Tab. 5)。
- 全部訓練資料皆為公開學術資料集,作者明確標註各資料集的場景數與類型(Abstract、Tab. 1)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- Real-world 深度資料品質不足(noisy 或 sparse),作者 Fig. 4 直接展示 DL3DV、Co3dV2、WildRGBD 的瑕疵,並承認需依賴 teacher pseudo-label 才能補足(§4)。
- Pose conditioning 在 7Scenes 上幾乎沒有提升甚至略降,作者解釋為「limited video setting already saturates performance」(§7.1)。
- 在 metric depth 任務上,移除 teacher 監督反而在 NYUv2 與 KITTI 上略有提升,作者於 Tab. 11 公開記錄此 trade-off。
- 模型目前僅處理 static scenes,作者於 §8 conclusion 將 dynamic scenes、language/interaction cue 整合明確列為 future work,等同承認當前範圍受限。
- 訓練成本高昂:DA3-Giant 需 128 × H100 訓練約 10 天,連 ablation 也需 32 × H100 × 4 天(§7.2)。

#### 4.2.2 Phyra-inferred

- 「single plain transformer, no architectural modifications」的敘述與實際做法存在落差:作者仍引入 input-adaptive cross-view self-attention(透過 tensor reordering)、camera token MLP encoder 與 dual-DPT head,只是不更動 transformer block 內部結構,標題式聲明易誤導讀者對「最小化」程度的判斷(§3.2)。
- 自建 benchmark 中包含作者自家的 HiRoom 合成集(29 scenes,Blender 渲染),且 ScanNet++ 同時出現在 training 與 benchmark(雖宣稱 scene-level disjoint),這些設定都對 DA3 自身有利,但對 Pi3、VGGT 等基線是否同樣 leak-free 缺乏交叉驗證(Tab. 1、Tab. 2、§3.4)。
- 缺少與 classical SfM/MVS pipelines(COLMAP、OpenMVS)在同一 benchmark 上的對照,讀者無法判斷學習式方法相對非學習式方法在 well-textured 場景上的真實 advantage(§7.1)。
- Pose-conditioning ablation(Tab. 7 f, g)僅在「使用 GT pose fusion 評估」下進行,讀者無從得知 pose conditioning 對自由 inference(predicted pose)的影響,削弱了「pose 條件化有效」的因果證據(§7.2.3)。
- 用 $H \times W$ 個 ray 原點 $t$ 隱式表示一個本質上為 6-DoF 的相機姿態存在大量冗餘,Eq. 1 採取簡單平均回收 $t_c$、再以 DLT 解 $H = KR$,此 pipeline 對 per-pixel ray 噪聲的敏感度與 worst-case 行為未被分析(§3.1)。
- Cross-view 一致性僅透過共享 backbone 與 attention「隱式」建立,訓練 loss 中沒有顯式的 multi-view geometric consistency term(如重投影誤差或對應像素的 ray-ray 距離),點雲品質改善多依靠 representation 設計而非 supervision(§3.3)。
- Teacher 的失效模式幾乎未被檢驗:當 teacher 與 sparse GT 在某像素分歧過大時,RANSAC scale-shift 是否會把 teacher 的系統性偏差(如鏡面、遠景)透過 alignment 注入監督訊號,作者未做敏感度測試(§4.2、Eq. 8)。
- Tab. 8 中 max image count 雖達 900–4100,但 global blocks 仍是 $O((N_v \cdot H \cdot W)^2)$ attention,對「kilometer-scale long sequences」(VGGT-Long 嘗試解決的問題)是否真正擴展未做實驗驗證(§3.2)。

### 4.3 Phyra's Judgment (summary)

DA3 真正新穎的貢獻是 depth-ray representation 與「以 vanilla DINOv2 + 輕量 cross-view attention 即可勝過多階段架構」的實證,兩者皆有 Tab. 6、Tab. 7 的對照支持,屬於可被後續研究繼承的設計原則。Dual-DPT head、camera token、teacher-student alignment 則更接近 engineering refinement,效益實在但概念上是既有元件的組合。整體而言,「minimal modeling」的核心主張在 static、posed/unposed RGB 設定下被有效驗證,但 dynamic scenes、long-sequence memory、與 ray map 隱式 pose 的數值穩定性仍是未解的結構性問題。

## 5. Methodology Deep Dive

### 5.1 Method Overview

DA3 將任意視角的三維幾何重建問題重構為單純的密集預測任務:給定 $N$ 張輸入影像 $\mathcal{I} = \{I_i\}_{i=1}^{N_v}$,模型 $\mathcal{F}_\theta$ 輸出每張影像的深度圖 $\hat{D}_i \in \mathbb{R}^{H \times W}$ 與射線圖 $\hat{R}_i \in \mathbb{R}^{H \times W \times 6}$,並可選擇性地輸出相機參數 $\hat{c}_i$。架構上採用單一 plain transformer 作為 backbone(直接使用 vanilla DINOv2,不做架構特化),配合一個 input-adaptive cross-view self-attention 模組以支援任意視角數,以及一個 dual-DPT head 同時產生深度與射線預測(p.6 §3.2,p.7 Fig.3)。對於有相機姿態的情境,姿態經由輕量級 MLP 編碼為 camera token $c_i = E_c(f_i, q_i, t_i)$ 並與 patch tokens 串接,參與所有 attention 運算;若無姿態,則改用一個共享可學習的 placeholder token $c_l$(p.7 §3.2 "Camera condition injection")。

關鍵設計在於 depth-ray representation:相機姿態以每像素射線 $r = (t, d) \in \mathbb{R}^6$ 隱式表達,其中 $t \in \mathbb{R}^3$ 為射線原點(相機中心)、$d \in \mathbb{R}^3$ 為射線方向,且 $d$ 不做正規化以保留投影尺度(p.6 §3.1)。世界座標系下的三維點可由 $P = t + D(u,v) \cdot d$ 透過逐元素運算融合,避免了旋轉矩陣正交性約束的優化困難。模型透過 cross-view self-attention 在選定層中對 tokens 進行重排,使所有視角的 tokens 在這些層中聯合計算 attention,實現視角間的資訊交流;比例設定為 $L_s : L_g = 2 : 1$(p.7 §3.2 與 Tab.7)。

訓練採 teacher-student 範式以解決真實深度資料品質不足的問題:先在合成資料上訓練 monocular relative depth teacher(Depth-Anything-3-Teacher),再對原始稀疏/雜訊深度透過 RANSAC 最小二乘對齊得到密集偽標籤(p.7 §3.3,p.10 Eq.8),於 120k 步後從 ground-truth 切換到 teacher labels(p.8 §3.4)。整體訓練在 128 張 H100 上跑 200k 步,base resolution 為 $504 \times 504$,並隨機從多種解析度與 2 至 18 視角中採樣。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: I = {I_i}_{i=1}^{N_v},  shape [B, N_v, 3, H, W]   (H=W=504, N_v ∈ [2,18])
   │
   │  Patchify (DINOv2 patch embed, patch_size=14)
   ▼
Patch tokens: x_p  [B, N_v, N_p, d]   (N_p = (H/14)·(W/14) = 36·36 = 1296, d=?)
                                       (d 為 DINOv2 隱藏維度,paper 未明示具體值)
   │
   │  Camera Encoding (optional)
   │  if poses available:  c_i = E_c(f_i ∈ R^2, q_i ∈ R^4, t_i ∈ R^3)  via MLP
   │  else:                c_i = c_l  (shared learnable placeholder)
   ▼
Camera tokens: x_c  [B, N_v, 1, d]
   │
   │  Concatenate per view: tokens_i = [c_i; x_p^i]
   ▼
Tokens: x  [B, N_v, N_p+1, d]
   │
   │  Plain Transformer Backbone (vanilla DINOv2, L blocks, L = L_s + L_g)
   │
   │  ── Stage A: first L_s blocks (within-view self-attention) ──
   │     reshape:  [B, N_v, N_p+1, d] → [B·N_v, N_p+1, d]
   │     for each block: attention 在每張影像內部 token 上運算
   │     (L_s : L_g = 2 : 1,  Tab.7)
   ▼
Tokens (after L_s):  [B·N_v, N_p+1, d]  →  reshape back  [B, N_v, N_p+1, d]
   │
   │  ── Stage B: subsequent L_g blocks (alternating cross-view / within-view) ──
   │     odd block (cross-view):
   │       reshape:  [B, N_v, N_p+1, d] → [B, N_v·(N_p+1), d]
   │       attention 跨所有視角 tokens 聯合運算
   │     even block (within-view):
   │       reshape back: [B·N_v, N_p+1, d]
   │     (input-adaptive: N_v=1 時退化為純 monocular,p.7)
   ▼
Feature tokens: F  [B, N_v, N_p+1, d]   (取多層 intermediate features 供 DPT 使用)
   │
   ├──→ Camera Head D_C (lightweight transformer on camera tokens only)
   │       input:  camera tokens 序列  [B, N_v, 1, d]
   │       output: ĉ_i = (f_i ∈ R^2, q_i ∈ R^4, t_i ∈ R^3)  →  [B, N_v, 9]
   │       (用於 inference 時快速回傳相機參數,p.7 §3.1)
   │
   └──→ Dual-DPT Head (Fig.3)
           │
           │  shared Reassemble modules (作用於 patch tokens,排除 camera token)
           │  輸入多層 features:  [B·N_v, N_p, d]  (取若干層,paper 未明示層數)
           │  Reassemble: token → 2D feature map at multiple scales
           ▼
        Reassembled features:  [B·N_v, C_k, H_k, W_k]  for k=1..K
           │
           ├──→ Depth Branch
           │       Fusion layers (depth-specific) → Output layer
           │       output: D̂  [B, N_v, H, W]    (per-pixel scalar depth)
           │
           └──→ Ray Branch
                   Fusion layers (ray-specific) → Output layer
                   output: R̂  [B, N_v, H, W, 6]   (origin t ∈ R^3, direction d ∈ R^3)
   │
   ▼
Outputs: F_θ : I ↦ {D̂, R̂, ĉ}     (ĉ 為灰色/可選輸出,p.7 §3.3)

3D Point Cloud Fusion (post-processing, element-wise):
   P = R̂(:,:,:,:3) + D̂ · R̂(:,:,:,3:)    →  [B, N_v, H, W, 3]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Patch Embedding & Camera Token Construction

**Function:** 將輸入影像切成 patches 並產生 patch tokens,同時為每張影像構造一個 camera token(若有姿態則編碼姿態,否則使用共享 placeholder)。

**Input:**
- Name: $\mathcal{I} = \{I_i\}_{i=1}^{N_v}$,以及可選的 $(K_i, R_i, t_i)$
- Shape: 影像 `[B, N_v, 3, H, W]`(H=W=504)
- Source: 原始多視角輸入

**Output:**
- Name: 串接後的 token 序列 $x$
- Shape: `[B, N_v, N_p+1, d]`,其中 $N_p = 1296$(36×36 patches),$d$ 為 DINOv2 隱藏維度(the paper does not specify)
- Consumer: Plain Transformer Backbone

**Processing:**

1. 對每張影像以 DINOv2 的 patch embedding 切分(patch_size=14,因 504 可被 14 整除,p.8 §3.4),得到 patch tokens $x_p \in \mathbb{R}^{B \times N_v \times N_p \times d}$。
2. 若提供 $(K_i, R_i, t_i)$:相機被表示為 $v_i = (f_i \in \mathbb{R}^2, q_i \in \mathbb{R}^4, t_i \in \mathbb{R}^3) \in \mathbb{R}^9$,經 MLP $E_c$ 編碼為 $c_i = E_c(f_i, q_i, t_i)$(p.7 §3.2);否則使用共享可學習 token $c_l$。
3. 將 camera token prepend 到 patch tokens 前:$\text{tokens}_i = [c_i; x_p^i]$,得到 `[B, N_v, N_p+1, d]`。

**Key Formulas:**

$$
c_i = E_c(f_i, q_i, t_i) \quad \text{若有姿態,否則 } c_i = c_l
$$

**Implementation Details:**

DINOv2 backbone 直接使用 vanilla 預訓練權重,「不做任何架構修改」(p.5 Fig.2 caption,p.7 §3.2)。Patch size 預設為 14,base resolution 為 $504 \times 504$,訓練時隨機抽樣於 $\{504{\times}504, 504{\times}378, 504{\times}336, 504{\times}280, 336{\times}504, 896{\times}504, 756{\times}504, 672{\times}504\}$;$504 \times 504$ 解析度下,視角數從 $[2, 18]$ 均勻採樣,batch size 動態調整以維持每步 token 總數大致恆定(p.8 §3.4)。Pose conditioning 在訓練時以 0.2 機率隨機啟用(p.8 §3.4)。DINOv2 hidden dimension $d$ 在論文中未明示具體值。

#### 5.3.2 Plain Transformer Backbone with Input-Adaptive Cross-View Self-Attention

**Function:** 以單一未改動的 ViT 同時處理視角內與跨視角的 token interaction;前 $L_s$ 層做 within-view attention,後 $L_g$ 層交替做 cross-view 與 within-view attention。

**Input:**
- Name: $x$
- Shape: `[B, N_v, N_p+1, d]`
- Source: §5.3.1 patch + camera token 串接結果

**Output:**
- Name: feature tokens $F$(以及多層 intermediate features 給 DPT 使用)
- Shape: `[B, N_v, N_p+1, d]`
- Consumer: §5.3.3 Dual-DPT Head 與 §5.3.4 Camera Head

**Processing:**

1. Stage A — 前 $L_s$ 層 within-view attention:將 tensor reshape 為 `[B·N_v, N_p+1, d]`,逐塊執行標準 self-attention,attention 範圍限定於同一張影像內部。
2. Stage B — 後 $L_g$ 層交替模式:奇數塊做 cross-view,將 tokens reshape 為 `[B, N_v·(N_p+1), d]`,attention 跨所有視角聯合計算;偶數塊做 within-view,reshape 回 `[B·N_v, N_p+1, d]`。Camera token 全程參與 attention(p.7 §3.2)。
3. 此設計為 input-adaptive:當 $N_v = 1$ 時,cross-view 與 within-view 在 token 排列上等價,模型自然退化為 monocular depth estimation,無額外開銷(p.7 §3.2)。
4. 取多層 intermediate features 輸出給 Dual-DPT(具體取哪幾層 the paper does not specify)。

**Key Formulas:**

$$
L = L_s + L_g, \quad \frac{L_s}{L_g} = \frac{2}{1}
$$

within-view 與 cross-view 的差異僅體現在 token 重排上,attention 運算本身保持標準 ViT 形式。

**Implementation Details:**

採用 vanilla DINOv2 ViT,「沒有引入特化的架構修改」(p.8 §4.1)。Layer 比例 $L_s : L_g = 2 : 1$ 是消融研究下的最佳配置(p.7 §3.2,Tab.7)。具體 $L$ 值、ViT 變體(S/B/L/G)、hidden dimension、head 數,paper 在 §3 與 §3.4 中未明確列出。Token rearranging 透過 tensor reordering 實現,不增加新參數(p.7 §3.2)。

#### 5.3.3 Dual-DPT Head

**Function:** 從 backbone 輸出的多層 feature tokens 同時產出深度圖與射線圖,兩個分支共享 reassembly 模組以保證對齊,僅在 fusion 與 output layer 上分離。

**Input:**
- Name: 多層 intermediate features $F$(僅取 patch tokens,排除 camera token)
- Shape: 多個 `[B·N_v, N_p, d]`(層數與選取規則 the paper does not specify)
- Source: §5.3.2 backbone

**Output:**
- Name: $\hat{D}, \hat{R}$
- Shape: $\hat{D}$ `[B, N_v, H, W]`,$\hat{R}$ `[B, N_v, H, W, 6]`
- Consumer: §5.3.5 損失函數;以及後處理的點雲融合

**Processing:**

1. **Shared Reassemble modules**(p.7 Fig.3):接收若干層的 patch tokens,將 token 序列重塑為 2D feature maps,並在多個尺度上產生特徵圖 `[B·N_v, C_k, H_k, W_k]`。此模組由兩分支共享,「以保證輸出對齊」(p.7 §3.2 "Dual-DPT head")。
2. **Two distinct Fusion stacks**:同一組 reassembled features 分別送入 depth-specific fusion layers 與 ray-specific fusion layers(Fig.3)。
3. **Output layers**:depth 分支輸出每像素深度;ray 分支輸出每像素 6 維 $(t, d)$。射線方向 $d$ 不做正規化以保留投影尺度(p.6 §3.1)。
4. 與標準 DPT 相比,差異在於:reassembly 共享(避免冗餘中間表示)、fusion 分離(允許兩任務在後段建立任務特化特徵),作者主張此設計「鼓勵兩任務間強互動,同時避免冗餘中間表示」(p.7 §3.2)。

**Key Formulas:**

$$
\hat{D}, \hat{R} = \text{DualDPT}(F) \quad\text{且}\quad P = t + D(u,v)\cdot d
$$

**Implementation Details:**

Reassemble、Fusion、Output 三類模組沿用 DPT(Ranftl 2021)架構,(p.5 Fig.2 caption)。具體 fusion blocks 數量、通道數、上採樣方式、共享層的具體選取,paper 未提供細節,參見 §5.4 對 prediction targets 充分性的消融(Tab.6)。

#### 5.3.4 Camera Head $\mathcal{D}_C$

**Function:** 在推論時直接從 camera tokens 預測相機參數,避免從密集 ray map 解 homography 的成本。

**Input:**
- Name: backbone 輸出的 camera tokens
- Shape: `[B, N_v, 1, d]`
- Source: §5.3.2 backbone

**Output:**
- Name: $\hat{c}_i = (\hat{f}_i, \hat{q}_i, \hat{t}_i)$
- Shape: `[B, N_v, 9]`($f \in \mathbb{R}^2, q \in \mathbb{R}^4, t \in \mathbb{R}^3$)
- Consumer: §5.3.5 損失函數;以及推論時的下游應用

**Processing:**

1. 一個 lightweight transformer 僅作用於 camera tokens 序列(每個視角 1 個 token)。
2. 輸出 FOV $f \in \mathbb{R}^2$、rotation quaternion $q \in \mathbb{R}^4$、translation $t \in \mathbb{R}^3$。
3. 由於每視角僅一個 token,額外計算成本可忽略(p.7 §3.1)。
4. 推論時可從 ray map 解 homography $H^* = \arg\min_{\|H\|=1} \sum \|H p_{h,w} \times M(h,w,3:)\|$ 並用 RQ 分解恢復 $K, R$(Eq.2,p.6),但此路線昂貴;Camera Head 提供快速備援。

**Key Formulas:**

$$
\hat{c}_i = \mathcal{D}_C(c_i^{(L)})
$$

其中 $c_i^{(L)}$ 為 backbone 最終層的 camera token。

**Implementation Details:**

Paper 將其描述為「a lightweight camera head」「a transformer」(p.7 §3.1),但具體層數、hidden size、訓練時是否與其他 head 同步反向傳播等細節 the paper does not specify。預測尺度也由 §5.3.5 中的全域 normalization 統一約束。

#### 5.3.5 Training Objectives

**Function:** 約束深度、射線、(可選)相機輸出,並用 gradient loss 強化邊緣銳利度與平面平滑性。

**Input:**
- Name: $\hat{D}, \hat{R}, \hat{c}$ 與 GT $D, M, P, v$
- Shape: 同 §5.3.3 / §5.3.4
- Source: 模型輸出與資料標籤(包含 teacher 偽標籤)

**Output:**
- Name: 純量損失 $\mathcal{L}$
- Shape: 標量
- Consumer: 反向傳播

**Processing:**

1. 所有 GT 訊號在計算損失前以共同尺度因子正規化,定義為「有效重投影 point map $P$ 的 mean $\ell_2$ norm」,確保跨模態幅度一致並穩定訓練(p.8 §3.3)。
2. 總損失為加權和:

$$
\mathcal{L} = L_D(\hat{D}, D) + L_M(\hat{R}, M) + L_P(\hat{D} \odot d + t, P) + \beta L_C(\hat{c}, v) + \alpha L_{\text{grad}}(\hat{D}, D)
$$

3. 深度損失採信心加權 $\ell_1$ 形式:

$$
L_D(\hat{D}, D; D_c) = \frac{1}{Z_\Omega}\sum_{p \in \Omega} m_p \big[D_{c,p}|\hat{D}_p - D_p| - \lambda_c \log D_{c,p}\big]
$$

其中 $D_{c,p}$ 為深度信心,$m_p$ 為 valid mask,$\Omega$ 為有效像素域(p.8 §3.3)。

4. Gradient loss:

$$
L_{\text{grad}}(\hat{D}, D) = \|\nabla_x \hat{D} - \nabla_x D\|_1 + \|\nabla_y \hat{D} - \nabla_y D\|_1 \quad (3)
$$

保留邊緣銳利同時鼓勵平面區域平滑(p.8 §3.3)。

5. 訓練 120k 步前以 GT depth 為監督;120k 步後切換為 teacher 對齊後的偽深度 $D_{T \to M}$(p.8 §3.4)。

**Key Formulas:**

對齊由 RANSAC 最小二乘求解(p.10 §4.2):

$$
(\hat{s}, \hat{t}) = \arg\min_{s>0, t} \sum_{p \in \Omega} m_p\big(s\tilde{D}_p + t - D_p\big)^2, \quad D_{T \to M} = \hat{s}\tilde{D} + \hat{t} \quad (8)
$$

inlier 閾值設為殘差 median 之 mean absolute deviation(p.10)。

**Implementation Details:**

所有損失項皆基於 $\ell_1$ norm,權重 $\alpha = 1$、$\beta = 1$(p.8 §3.3,文中於 "In practice, we set $\alpha = 1$ and $\beta = 1$" 處明確;$\lambda_c$ 的具體值 the paper does not specify)。Pose conditioning 訓練機率 0.2(p.8 §3.4)。本研究主張 depth-ray 是「最小且充分」的目標集合,Tab.6 顯示其優於 point map 或 pose+local/global point map+depth 的冗餘組合(p.6 §3.1,p.7),「冗餘目標雖能提升 pose 精度,卻常引入 entanglement 反而劣化幾何」(p.6 §3.1)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage |
|---|---|---|---|
| HiRoom (本論文新建) | Pose / geometry / NVS 評測 | 29 scenes (Blender 合成室內) | test |
| ETH3D [72] | Pose / geometry 評測 | 11 scenes (LiDAR) | test |
| DTU [1] | Object-level geometry 評測 | 22 scans (LiDAR) | test |
| 7Scenes [74] | 室內 pose / geometry 評測 | 7 scenes (LiDAR) | test |
| ScanNet++ [117] | 室內 pose / geometry 評測 | 20 scenes (LiDAR) | test (場景與 train 嚴格不重疊) |
| AriaDigitalTwin / AriaSyntheticENV [63] | Pose-geometry 訓練 | 237 / 99,950 scenes | train |
| ArkitScenes [5] | Pose-geometry 訓練 | 4,388 scenes (LiDAR) | train |
| BlendedMVS [115] | Pose-geometry 訓練 | 503 scenes (3D recon) | train |
| Co3Dv2 [68] | Pose-geometry 訓練 | 30,616 scenes (COLMAP) | train |
| DL3DV [53] | Pose-geometry + NVS 訓練 / NVS 測試 | 6,379 scenes（NVS 用 10,015；NVS 測試 140 scenes，與訓練集互斥） | train + test |
| HyperSim [69] | Pose-geometry 訓練 | 344 scenes (synthetic) | train |
| MapFree [3] | Pose-geometry 訓練 | 921 scenes (COLMAP) | train |
| MegaDepth [51] | Pose-geometry 訓練 / NVS 測試 | 268 scenes (COLMAP)；NVS 測 19 scenes (5000–5018) | train + test |
| MegaSynth [40] | Pose-geometry 訓練 | 6,049 scenes (synthetic) | train |
| MvsSynth [38] | Pose-geometry 訓練 | 121 scenes (synthetic) | train |
| Objaverse [17] | Pose-geometry 訓練 | 505,557 scenes (synthetic) | train |
| Omniobject [102] | Pose-geometry 訓練 | 5,885 scenes (synthetic) | train |
| OmniWorld [128] | Pose-geometry 訓練 | 1,039 scenes (synthetic) | train |
| PointOdyssey [127] | Pose-geometry 訓練 | 44 scenes (synthetic) | train |
| ReplicaVMAP [83] | Pose-geometry 訓練 | 17 scenes (synthetic) | train |
| ScanNet++ [117] | Pose-geometry 訓練 | 230 scenes (LiDAR) | train (與 test 場景互斥) |
| ScenenetRGBD [55] | Pose-geometry 訓練 | 16,866 scenes (synthetic) | train |
| TartanAir [98] | Pose-geometry 訓練 | 355 scenes (synthetic) | train |
| Trellis [104] | Pose-geometry 訓練 | 557,408 scenes (synthetic) | train |
| vKitti2 [9] | Pose-geometry 訓練 | 50 scenes (synthetic) | train |
| WildRGBD [103] | Pose-geometry 訓練 | 23,050 scenes (LiDAR) | train |
| Tanks and Temples [45] | NVS 評測 | 6 scenes (Training Data 去除 Courthouse) | test |
| KITTI [25] / NYU [76] / SINTEL / ETH3D / DIODE [88] / SUN-RGBD [81] | Monocular / metric depth 評測 | 標準 benchmark | test |
| Teacher 訓練語料 (Hypersim, TartanAir, IRS, vKITTI2, BlendedMVS, SPRING, MVSSynth, UnrealStereo4K, GTA-SfM, TauAgent, KenBurns, MatrixCity, EDEN, ReplicaGSO, UrbanSyn, PointOdyssey, Structured3D, Objaverse, Trellis, OmniObject) | Teacher 監督訓練 | 20 個合成資料集 | train (Teacher) |
| Metric depth 訓練語料 (Taskonomy, DIML-Outdoor, DDAD, Argoverse, Lyft, PandaSet, Waymo, ScanNet++, ARKitScenes, Map-free, DSEC, Driving Stereo, Cityscapes) | Metric depth 訓練 | 14 datasets | train (DA3-Metric) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| AUC@3 | Pose AUC，閾值 3°，由 RRA / RTA 中較小者構成 accuracy–threshold 曲線下面積 | yes |
| AUC@30 | Pose AUC，閾值 30° | yes |
| F1-score | Reconstruction $F_1 = \frac{2 \cdot \text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}}$，依距離門檻 $d$（HiRoom/7Scenes/ScanNet++ 為 0.05 m、ETH3D 為 0.25 m）判定 inlier | yes |
| Chamfer Distance (CD, mm) | DTU 上 $\text{dist}(R \to G)$ 與 $\text{dist}(G \to R)$ 之平均 | yes (DTU 主指標) |
| $\delta_1$ | Monocular / metric depth 中誤差 ratio $< 1.25$ 的像素比例 | yes |
| AbsRel | $|\hat{D} - D| / D$ 平均，metric depth 主指標 | yes |
| SqRel | $(\hat{D} - D)^2 / D$ 平均，僅在 teacher ablation 中報告 | no |
| PSNR / SSIM / LPIPS | NVS 渲染品質 | yes (NVS 主指標) |

### 6.3 Training and Inference Settings

DA3 主模型在 128 張 H100 GPUs 上訓練 200k steps，warm-up 為 8k steps，peak learning rate $2 \times 10^{-4}$。Base 解析度為 $504 \times 504$（可被 2、3、4、6、9、14 整除以支援常見長寬比），訓練解析度從 $\{504\times504, 504\times378, 504\times336, 504\times280, 336\times504, 896\times504, 756\times504, 672\times504\}$ 隨機抽樣；在 $504\times504$ 下 view 數從 $[2, 18]$ 均勻抽樣，batch size 動態調整以維持每 step token 數近似不變。Supervision 在 120k steps 時由 ground-truth depth 切換為 teacher pseudo-label，pose conditioning 以 0.2 機率隨機啟動（§3.4）。Loss 權重 $\alpha = \beta = 1$。

Ablation 設定為 ViT-L backbone、最多 10 views、batch size 128、120k steps，於 32 張 H100 GPUs 上訓練約 4 天；DA3-Giant 完整訓練約需 10 天（§7.2）。

Teacher 模型使用 ViT-L backbone、batch size 64，在合成資料上以 depth + gradient + global-local + normal + sky/object mask loss 監督（§4.1、§7.3.1）。Metric depth 模型用 AdamW（encoder lr 5e-6、decoder lr 5e-5），canonical focal length $f_c = 300$，base 解析度 504、多 aspect ratio，5% 機率施加 90°/270° rotation augmentation，20% 機率改用原始 GT 監督，batch size 64 訓練 160k iterations（§4.4）。

NVS 模型在 8 張 A100 GPUs 上訓練 200k steps、batch size 1（pixelSplat 因 epipolar attention 過慢只訓 100k steps），凍結 DA3 backbone 僅 fine-tune GS-DPT head；輸出解析度 $H \times W = 270 \times 480$；測試時固定使用 12 個 farthest-point-sampled context views（§5.3、§7.5）。

Inference 上限與速度於單張 80 GB A100 上量測（場景 32 張、$504 \times 336$）：DA3-Giant 約 900–1000 images / 37.6 FPS；DA3-Large 約 1500–1600 images / 78.4 FPS；DA3-Base 約 2100–2200 / 126.5 FPS；DA3-Small 約 4000–4100 / 160.5 FPS（Tab. 8）。Pose evaluation 中每場景最多取 100 張影像（隨機種子固定），NVS 每場景每 8 張取 1 張為 target view（§6.1）。其餘細節（如 RANSAC inlier 比例、Adam betas）論文未明確說明。

### 6.4 Main Results

Pose accuracy (Tab. 2，AUC@3)：

| Method | HiRoom | ETH3D | DTU | 7Scenes | ScanNet++ |
|---|---|---|---|---|---|
| DUSt3R (0.57B) | 17.6 | 4.30 | 4.00 | 6.90 | 8.10 |
| Fast3R (0.65B) | 25.9 | 8.10 | 9.50 | 19.0 | 17.9 |
| MapAnything (0.56B) | 17.9 | 19.2 | 6.50 | 12.6 | 20.2 |
| Pi3 (0.96B) | 67.0 | 35.2 | 62.5 | 25.5 | 50.7 |
| VGGT (1.19B) | 49.1 | 26.3 | 79.2 | 23.9 | 62.6 |
| **DA3-Giant (1.10B)** | **80.3** | **48.4** | **94.1** | **28.5** | **85.0** |
| DA3-Large (0.36B) | 58.7 | 32.2 | 70.2 | 29.2 | 60.2 |

Reconstruction (Tab. 3，pose-free 設定；DTU 為 CD↓ mm，其他為 F1↑)：

| Method | HiRoom | ETH3D | DTU (CD↓) | 7Scenes | ScanNet++ |
|---|---|---|---|---|---|
| DUSt3R | 30.1 | 19.7 | 7.60 | 26.6 | 18.9 |
| Fast3R | 40.7 | 38.5 | 6.88 | 41.0 | 37.1 |
| MapAnything | 32.4 | 54.8 | 7.91 | 44.8 | 39.4 |
| Pi3 | 75.8 | 72.7 | 3.28 | 44.2 | 63.1 |
| VGGT | 56.7 | 57.2 | 2.05 | 47.9 | 66.4 |
| **DA3-Giant** | **85.1** | **79.0** | **1.85** | **53.5** | **77.0** |
| DA3-Large | 69.5 | 65.8 | 2.08 | 56.3 | 67.9 |

整體上 DA3-Giant 在 20 個 setting 中拿下 18 個 SOTA；相對 VGGT 平均 pose 改進 35.7%、reconstruction 改進 23.6%（abstract）；幾何相對 VGGT 平均 +25.1%、相對 Pi3 +21.5%（§7.1）。

Monocular depth (Tab. 4，$\delta_1 \uparrow$)：

| Method | KITTI | NYU | SINTEL | ETH3D | DIODE | Rank |
|---|---|---|---|---|---|---|
| DA2 | 94.6 | 97.9 | 77.2 | 86.5 | 95.2 | 2.60 |
| VGGT | 91.7 | 97.9 | 67.9 | 97.5 | 95.3 | 3.75 |
| **DA3** | **95.3** | 97.4 | 75.5 | **98.6** | **95.4** | **2.20** |
| Teacher | 97.2 | 97.9 | 81.4 | 99.8 | 96.6 | 1.00 |

Metric depth (Tab. 11，best per dataset)：DA3-Metric 在 ETH3D 取得 SOTA（$\delta_1 = 0.917$、AbsRel = 0.104），在 SUN-RGBD 取得 best AbsRel (0.105)，DIODE 取得第二（$\delta_1 = 0.838$）；NYUv2 / KITTI 仍由 UniDepthv1/v2 領先。

NVS (Tab. 5，PSNR↑/SSIM↑/LPIPS↓，DL3DV-Benchmarks)：

| Method | PSNR | SSIM | LPIPS |
|---|---|---|---|
| pixelSplat | 16.55 | 0.456 | 0.480 |
| MVSplat | 18.13 | 0.559 | 0.393 |
| DepthSplat | 19.24 | 0.620 | 0.322 |
| Fast3R | 19.30 | 0.604 | 0.320 |
| MV-DUSt3R | 20.01 | 0.645 | 0.294 |
| VGGT | 20.96 | 0.697 | 0.253 |
| **DA3 (Ours)** | **21.33** | **0.711** | **0.241** |

DA3 在 DL3DV、Tanks and Temples、MegaDepth 三組 NVS 測試集都同時取得最佳 PSNR / SSIM / LPIPS。

### 6.5 Ablation Studies

- **Prediction targets (Tab. 6)**：在無 camera condition 下比較 `depth+pcd+cam`、`depth+cam`、`depth+ray`、`depth+ray+cam`。`depth+ray` 全面勝出，相對 `depth+cam` 在 Auc3 取得近 100% 相對提升（HiRoom 10.8 → 48.7）；加上 cam head 後（`depth+ray+cam`）整體無顯著進一步提升，但因 cam head 計算量僅約 backbone 的 0.1%，最終仍保留作為推論便利。此 ablation 直接回答「ray 表示是否最小且足夠」的核心宣稱，非 sanity check。
- **Architecture (Tab. 7 a–c)**：相同參數規模下，VGGT 風格雙 transformer 僅達 baseline 的 79.8%（Auc3 由 39.2 → 3.72，HiRoom F1 47.0 → 14.5），而 Full Alt.（每層皆 alternate cross-view/within-view）在大部分 metric 上劣於 partial alternation，驗證「單一 plain transformer + $L_s : L_g = 2 : 1$」的設計決策。屬診斷性 ablation。
- **Dual-DPT head (Tab. 7 d)**：拆成兩個獨立 DPT head 後，HiRoom F1 由 47.0 掉到 11.5、Auc3 由 39.2 掉到 5.59，幾乎所有指標一致下降，證實 Dual-DPT 的共享 reassemble + 分流 fusion 是必要的。
- **Teacher supervision (Tab. 7 e + Fig. 8)**：移除 teacher pseudo-label 在 DTU 上略有提升，但在 HiRoom（Auc3 39.2 → 11.2、F1 47.0 → 16.0）顯著退步，7Scenes 與 ScanNet++ 也下滑；定性上 detail / 細結構明顯變差，證明 teacher 對細節而非粗結構至關重要。
- **Pose conditioning (Tab. 7 f vs g)**：在 ground-truth pose fusion 下，加入 pose condition 在 HiRoom F1 65.8 → 73.8、ETH3D F1 63.2 → 70.9、DTU CD 3.65 → 2.14、ScanNet++ F1 62.8 → 65.7 都有提升，僅 7Scenes 略降（46.0），論文歸因於該資料集在 pose-free 已飽和。屬針對性 ablation。
- **Teacher 自身 ablation (Tab. 9)**：分別檢視 (i) 訓練資料 V2 vs V3 vs V3+multi-resolution（$\delta_1$ 0.919 → 0.929 → 0.938）、(ii) 預測幾何形式 disparity / pointmap / depth（depth 在 AbsRel/SqRel 平衡最佳）、(iii) loss 變體（full > w/o distance normalization > MAE-loss）。三者皆是診斷性實驗，回答「資料、表示、loss 哪個改動真的有效」。
- **Metric depth teacher (Tab. 11 末兩列 + Fig. 10)**：移除 teacher 在 NYUv2 / KITTI 之 $\delta_1$ 略升，但 Fig. 10 顯示 sharpness 與 fine detail 顯著退化；論文以「metric 與 sharpness 之間 trade-off」解讀。此 ablation 部分偏向 sanity check，因為它沒有對 metric 失分提出量化的銳利度指標。
- **NVS backbone swap (Tab. 5)**：固定 GS-DPT head 改換 Fast3R / MV-DUSt3R / VGGT / DA3，DA3 全面領先；同時與專用 3DGS 模型 (pixelSplat, MVSplat, DepthSplat) 比較，驗證「強幾何 backbone 比專用架構更有效」的論點，屬診斷性對照。

整體而言，所有 ablation 都對應到論文的具體設計宣稱，僅 metric depth 的 teacher ablation 因缺乏 sharpness 量化指標較接近 sanity check。

### 6.6 Phyra Experiment Assessment

- [covered] 至少一個強 baseline — 對 pose / geometry 有 VGGT、Pi3、MapAnything、Fast3R、DUSt3R 五個近期 SOTA（Tab. 2、Tab. 3）；NVS 另比 pixelSplat / MVSplat / DepthSplat（Tab. 5）；metric depth 比 DepthPro / Metric3Dv2 / UniDepthv1/v2（Tab. 11）。
- [covered] 跨任務 / 跨資料集評測 — 評測涵蓋 pose、geometry、monocular depth、metric depth、NVS 五任務，幾何 benchmark 含 5 個 dataset (HiRoom/ETH3D/DTU/7Scenes/ScanNet++)，monocular 5 個 dataset，NVS 3 個 dataset。
- [covered] 針對新元件的診斷性 ablation — depth-ray 表示 (Tab. 6)、單一 transformer vs VGGT-style (Tab. 7a–c)、Dual-DPT (Tab. 7d)、teacher 監督 (Tab. 7e、Tab. 9)、pose conditioning (Tab. 7f-g) 都直接對應論文核心設計。
- [covered] Scaling study — 提供 DA3-Small (0.022B) → Base (0.086B) → Large (0.30B) → Giant (1.10B) 四種規模的 pose / reconstruction 比較 (Tab. 2、Tab. 3)，並指出 pose 比 depth 更受益於 scaling。
- [covered] 效率 / wall-clock 比較 — Tab. 8 報告每個變體的 max image count、參數量與 FPS，並與 VGGT 對照（DA3-Giant 37.6 vs VGGT 34.1 FPS）。
- [missing] 報告 variance / 多 seed — 全文以單次評測數值呈現，未報告 standard deviation 或多 seed 結果。
- [partial] Reproducibility — 訓練資料全為公開 academic datasets，附錄列出完整 dataset、訓練 hyper-parameters 與 benchmark pipeline，並提供 project page (depth-anything-3.github.io)；但本文中未明確承諾釋出 code、weights 或 HiRoom 資料集的授權細節。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1:「a single plain transformer is sufficient as backbone」**:由 Tab. 7 a vs b 支持(VGGT-style 雙 transformer 架構在相近參數規模下退化至 baseline 的 79.8%),Tab. 7 c 也顯示全層 cross-view alternation 反而更差。然而「plain」並不嚴格成立:作者仍引入 token reordering、camera token、dual-DPT head,屬於 partial overclaim。
- **Claim 2:「depth-ray representation is a minimal yet sufficient target」**:Tab. 6 提供直接 ablation,depth + ray 在所有資料集 Auc3 與 F1 上都優於 depth + pcd + cam 與 depth + cam,且加入 cam head 不再提升。**Supported**。
- **Claim 3:「teacher-student paradigm 改善 real-world generalization」**:Tab. 7 e 與 Fig. 8 在 HiRoom、7Scenes、ScanNet++ 上支持此論點;但 Tab. 11 顯示 metric model 在 NYUv2 與 KITTI 上去除 teacher 反而略好,故結論應限縮為「對細節結構與 synthetic-style benchmark 有效」,屬於 **Partially supported**。
- **Claim 4:「在 18/20 設定上達 SOTA、平均 pose +35.7%、geometry +23.6%」**:Tab. 2 與 Tab. 3 直接支持,且 §7.1 給出每個指標的相對提升幅度。**Supported**,但需注意此 benchmark 由作者自建、且 HiRoom 與 ScanNet++ 與 training 有相關性。
- **Claim 5:「DA3 是 FF-NVS 的最佳 backbone」**:Tab. 5 顯示在 DL3DV、Tanks and Temples、MegaDepth 三個資料集上 DA3 backbone 全面優於 Fast3R、MV-DUSt3R、VGGT 與專門化 3DGS 模型。**Supported**,但比較範圍僅限於 12-context-view、$270 \times 480$ 解析度的單一設定。

### 7.2 Fundamental Limitations of the Method

**Static-scene 假設嵌入在 prediction target 中**。Depth-ray 表示假設每像素對應唯一 3D 點且相機外參全域一致,動態物體會違反 ray map 的一致性。要擴展到 dynamic scenes 需要新增 motion mask 或 temporal token,這已不是 fine-tuning 能解決,而是 representation 層面的修改。

**Per-pixel ray 對 6-DoF 姿態的冗餘編碼**。$H \times W$ 個 ray 原點原則上應全部相等於 $t_c$,$H \times W$ 個方向則被 $KR$ 約束為 3-parameter family。模型沒有任何結構性約束來保證這些冗餘自洽,Eq. 1 的平均化與 Eq. 2 的 DLT 解算把 per-pixel 噪聲累積到全域姿態。在 high-rotation 或 low-texture 區域(ray map 噪聲較大),此 pipeline 的最壞情況行為未被分析,可能成為 robustness 的隱藏成本。

**Teacher-student 的 bootstrap ceiling**。Student 模型的 supervision 上界是 teacher 在合成資料上能學到的 geometry,而 teacher 從未見過某些真實 domain(極端鏡面、戶外大尺度、aerial oblique)。當這些 domain 出現時,RANSAC alignment 的稀疏 inlier 不足以糾正 teacher 偏差,反而會把偏差以「對齊後的 pseudo-GT」形式注入 student 訓練。這是 self-distillation 系列方法的共通結構性弱點。

**Cross-view attention 的 quadratic memory**。Tab. 8 的 max image count 雖大,但 global block 仍對所有 view 的 patch token 做 full attention。當輸入是真正 km-level 長序列(如 VGGT-Long 的 chunk-and-loop 場景),此架構會碰到硬性記憶體上限,需依賴外部 chunking 策略,而非模型本身解決。

### 7.3 Citations Worth Tracking

- **VGGT (Wang et al., 2025)**:DA3 直接對標的前 SOTA,理解其 multi-stage 與冗餘輸出的設計動機,才能完整評估「minimal modeling」的反命題到底失去了什麼。
- **DUSt3R (Wang et al., 2024)**:奠定 feed-forward multi-view geometry 範式的開山之作,DA3 的 representation 與 head 設計都與其形成對照。
- **Depth Anything 2 (Yang et al., 2024)**:teacher-student 範式的直接前身,理解 DA2 才能判斷 DA3 在 monocular 與 multi-view 上的真正增量。
- **DINOv2 (Oquab et al., 2023)**:DA3 完全繼承的 backbone,要評估「scaling property」論點必須先了解 DINOv2 自身的 scaling 行為。
- **Pi3**:concurrent 的 permutation-equivariant 任意視角模型,提供與 DA3 不同設計哲學的對照(equivariance vs. token reordering)。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在含有移動物體的 dynamic scenes(如 KITTI tracking、自駕場景)上,DA3 的 ray map 與融合點雲會以何種模式失效?是否會在動態區域產生「鬼影」或姿態漂移?
- [ ] Eq. 1 的 ray origin averaging 與 Eq. 2 的 DLT 對 per-pixel ray noise 的敏感度如何?是否存在某些場景幾何(如純旋轉、純前向運動)導致 DLT 退化?
- [ ] 為何 pose conditioning 在 7Scenes 上沒有提升?是 saturation,還是與 motion blur、低解析度的特定交互?
- [ ] DA3-Giant 已用 1.10B 參數,進一步 scale 到 ViT-Huge/Enormous 是否仍有線性收益,或已接近 DINOv2 的 scaling ceiling?
- [ ] Teacher pseudo-label 與 sparse GT 嚴重分歧的像素被 RANSAC 視為 outlier 後,是否被完全丟棄?還是仍以某種形式進入 student 訓練?該機制對 systematic teacher bias 的吸收程度為何?
- [ ] 將 DA3 與傳統 COLMAP / bundle adjustment 在相同 benchmark 上正面對照,結果是否仍維持 23.6% geometry 領先?
- [ ] FF-NVS 評估僅在 12 context views、$270 \times 480$ 下進行,當 view 數降到 2–3 或解析度提升到 $1080 \times 1920$ 時,DA3 backbone 的優勢是否依然成立?

### 8.2 Improvement Directions

1. **加入顯式 multi-view consistency loss**(高可行性):以對應像素的 ray-ray 距離或 reprojection error 作為輔助 supervision,直接懲罰 ray map 的跨視角不一致,可在不改架構的前提下提升點雲幾何穩定性,理論上能緩和 §7.2 提出的冗餘編碼問題。
2. **後處理 bundle adjustment 精修**(高可行性):用預測的 depth 與 ray 作為 BA 初始值,在推論時對 pose 與 sparse 3D 點做數百步迭代,既能利用 DA3 的強 prior 又能拿回經典方法的數值精度,工程成本極低。
3. **Hierarchical / sliding-window cross-view attention**(中可行性):將 global blocks 改為 windowed cross-view + 周期性 global summary token,可把 Tab. 8 的 max image count 推到 10k 以上,直接回應 VGGT-Long 處理的長序列場景。
4. **將 dynamic mask 或 optical flow 注入 token stream**(中可行性):為每個 patch token 增加 motion channel,訓練時以合成動態場景(PointOdyssey、TartanAir)監督,可在不改 depth-ray formulation 的前提下處理 dynamic scenes,擴展 DA3 的適用範圍。
5. **直接以 teacher 蒸餾 DA3-Giant 的 monocular branch**(低成本):目前 monocular student 與 multi-view DA3 是分開訓練,若讓 DA3-Giant 的單視角分支同時 minimize teacher distillation loss,可避免「移除 teacher 在 NYU/KITTI 反而較好」(Tab. 11)所暗示的 supervision 衝突。
