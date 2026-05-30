<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# DGGT — DGGT: Feedforward 4D Reconstruction of Dynamic Driving Scenes using Unposed Images

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | DGGT |
| Paper full title | DGGT: Feedforward 4D Reconstruction of Dynamic Driving Scenes using Unposed Images |
| arXiv ID | 2512.03004 |
| Release date | 2025-12-02 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2512.03004 |
| PDF link | https://arxiv.org/pdf/2512.03004v1 |
| Code link | https://github.com/xiaomi-research/dggt |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Xiaoxue Chen | AIR, Tsinghua University; Xiaomi EV | https://cxx226.github.io/ | co-first author |
| Ziyi Xiong | AIR, Tsinghua University; Xiaomi EV | — | co-first author |
| Yuantao Chen | AIR, Tsinghua University | — | author |
| Gen Li | AIR, Tsinghua University | — | author |
| Nan Wang | AIR, Tsinghua University | — | author |
| Hongcheng Luo | Xiaomi EV | — | author |
| Long Chen | Xiaomi EV | — | author |
| Haiyang Sun | Xiaomi EV | — | project leader |
| Bing Wang | Xiaomi EV | — | author |
| Guang Chen | Xiaomi EV | — | author |
| Hangjun Ye | Xiaomi EV | https://cn.linkedin.com/in/hangjun-ye-584b347 | corresponding author |
| Hongyang Li | The University of Hong Kong | — | author |
| Ya-Qin Zhang | AIR, Tsinghua University | — | author |
| Hao Zhao | AIR, Tsinghua University; Beijing Academy of Artificial Intelligence | https://sites.google.com/view/fromandto | corresponding author |

### 1.2 Keywords

feedforward 4D reconstruction, dynamic driving scenes, pose-free reconstruction, 3D Gaussian Splatting, novel view synthesis, diffusion refinement, scene editing, autonomous driving simulation

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| STORM (Yang et al., ICLR 2025) | baseline | 最直接前身;首個動態駕駛場景前饋模型,但需相機 pose 且僅支援固定短窗口輸入。 |
| NoPoSplat (ICLR 2025) | baseline | Pose-free 前饋 3DGS 重建,但僅限靜態場景,本文擴展至動態。 |
| MVSplat (Chen et al.) | baseline | 前饋 3D Gaussian Splatting 多視圖靜態場景重建基線。 |
| DepthSplat (Xu et al.) | baseline | 前饋深度+3DGS 靜態場景重建,作為靜態前饋對照。 |
| EmerNeRF (ICLR 2024) | baseline | 基於 NeRF 的逐場景優化動態駕駛場景重建,作為優化型基線。 |
| DeformableGS (CVPR 2024) | baseline | 可變形 3DGS 動態場景重建,逐場景優化基線。 |
| PVG (Chen et al., 2023) | predecessor | 周期振動 3DGS 時間建模,屬於時間條件式動態表示。 |
| VGGT (Wang et al.) | base model | ViT 多視圖幾何變換器,作者擴展為 VGGT++ 並借用相機 pose 預測思路。 |

## 2. Research Overview

### 2.1 Research Topic

本文研究自駕車場景下的 4D(3D 空間 + 時間)動態場景前饋重建問題。傳統動態場景方法多依賴逐場景最佳化(per-scene optimization)、需預先校準的相機 pose、且僅支援短時序窗口,難以做為自駕日誌的大規模預處理工具。本文提出 DGGT(Driving Gaussian Grounded Transformer),以 ViT 為骨幹、DINO 特徵搭配交替注意力(alternating attention),在單次前向傳遞中同時輸出每幀相機外/內參、像素對齊 3D Gaussian map、動態遮罩、3D 運動場、生命期(lifespan)參數與天空 Gaussian。其關鍵創新在於將相機 pose 由「輸入」改為「輸出」,使方法支援任意數量、未校準輸入影格與長序列;並以 diffusion-based rendering refinement 抑制鬼影/補洞瑕疵。實驗於 Waymo、nuScenes、Argoverse2 取得 SOTA 重建品質與具競爭力的推論速度,並能直接做 instance-level 場景編輯(增刪車輛、行人)。

### 2.2 Domain Tags

- computer vision
- 3D/4D scene reconstruction
- autonomous driving
- neural rendering

### 2.3 Core Architectures Used

- **ViT backbone with alternating attention**:作為 $f_\theta$ 的主幹,將輸入影像切 patch 後以 DINO-pretrained 特徵抽取器產生 $F_\text{dino}$,再透過 alternating-attention 精煉為 $F_\text{attn}$,作為所有下游 head 的共享 token。
- **DINO feature extractor**:提供凍結的視覺先驗 $F_\text{dino}$,在 Gaussian head 中與 $F_\text{attn}$ 融合以補足空間細節,提升外觀重建保真度。
- **Multi-head prediction (camera / Gaussian / lifespan / dynamic / motion / sky heads)**:由共享 token 並行輸出 per-frame 外/內參 $\Pi_t$、像素對齊 Gaussian map $G_t$、生命期 $\sigma$、動態遮罩 $M_d^t$、3D 運動場 $F(t_a, t_b)$ 與遠景天空 Gaussian。
- **Pixel-aligned 3D Gaussian Splatting with lifespan**:每像素編碼 $(c, \mu, r, s, o, \sigma) \in \mathbb{R}^{15}$,以 $\sigma$ 經 $o^{t'} = o^t \cdot e^{-\frac{1}{2}(t'-t)^2/\sigma^t}$ 調制時間可見度,穩定靜態區域之動態外觀(光影變化)。
- **Hemispherical sky Gaussians + lightweight MLP $H_\text{sky}$**:於固定半徑 $r_\text{sky}$ 的半球面均勻取樣,對遠距無界背景(天空)做專門建模,並由 MLP 精煉初始顏色與 scale。
- **Transformer-based motion head with neighborhood attention**:聯合處理 2D 影像多尺度特徵與 Gaussian map 的 3D 點,構成時空特徵雲,以鄰域注意力反覆精化每像素 3D 位移軌跡 $F(t_a, t_b) \in \mathbb{R}^{q \times 3}$。
- **Linear + SLERP pose interpolation and motion-guided mean interpolation**:對中介時刻 $t_i$,以 $\mu_d^{t_i} = \mu_d^{t_a} + \omega_{t_i} \cdot F(t_a, t_b)$ 內插動態 Gaussian 中心,相機平移以線性內插、旋轉以 SLERP 處理四元數。
- **Differentiable 3DGS rasterizer**:以 $\hat{I}^t = \text{Renderer}(\hat{G}^t, \Pi^t)$ 提供端到端監督訊號,讓 RGB / depth / opacity loss 反向流回各 head。
- **Single-step diffusion refinement (frozen VAE encoder + UNet + LoRA-finetuned decoder)**:基於 [43] 之單步 diffusion 框架,以渲染影像 $\hat{I}^{t_i}$ 與隨機取自輸入序列的參考影像 $I_\text{ref}$ 為條件,修補 ghosting 與 disocclusion holes。
- **VGG-16 Gram-matrix style loss**:用於 diffusion refinement 階段,於重建損失與 LPIPS 之外加強紋理銳利度與細節。

### 2.4 Core Argument

作者識別出的根因是:現有動態駕駛場景重建將「相機 pose 必須先給定」與「逐場景最佳化」當作前提,但實際自駕日誌通常無精準 pose 標定、且時序很長、規模巨大,因此既慢又難以泛化。即使是先前最接近的前饋方法 STORM,也仍要 pose、僅支援固定短窗口、長序列會退化;而 NoPoSplat、MVSplat 等 pose-free 前饋方法又只能處理靜態場景。作者認為這些限制都源於對任務輸入/輸出的錯誤分工——將原本可從像素學到的相機幾何當成外部需求,並把動/靜態混雜在單一表示裡。據此,他們的解法在邏輯上必須同時做三件事才能成立:(1)把 pose 改成模型輸出,以解除外部標定依賴並支援任意視圖數;(2)以共享 ViT token 餵給多個輕量 head(camera/Gaussian/lifespan/dynamic/motion/sky),藉「lifespan 參數調制時間可見度」與「dynamic head 顯式分離靜態背景與動態物體」維持時間一致性與可編輯性;(3)以 motion head 預測完整 3D 位移軌跡(而非僅速度),搭配線性/SLERP 插值填補稀疏時間戳之間的中介幀,並以單步 diffusion refinement 修補因運動估計誤差與大幅度視角變化造成的 ghosting 與遮擋洞。三者缺一,系統就無法在「單次前向、無 pose、長序列、動態」這四個約束下同時成立,因此這套組合是必要而非偶然的設計選擇。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(280 words)

標題「DGGT: Feedforward 4D Reconstruction of Dynamic Driving Scenes using Unposed Images」一次點出三個關鍵詞:feedforward、4D dynamic、unposed images,直接把論文要解決的痛點掛在標題上——前人方法多需 per-scene optimization 與相機 pose,於自駕場景無法規模化。Abstract 開門即建立動機:autonomous driving 需要能快速、可擴展地將 raw driving logs 轉成可重渲染的 4D 表徵,以支援訓練與評估,但既有 dynamic scene 方法仰賴 per-scene optimization、known camera calibration 或短 frame window,不切實際。

接著作者宣告 reformulation:把 camera pose 從「必要輸入」改成「模型輸出」,使 reconstruction 能直接從 sparse、unposed images 進行,並支援任意數量 views 以涵蓋長序列。論文將此框架命名為 Driving Gaussian Grounded Transformer (DGGT),並概述四個技術主軸:(i) 同時預測 per-frame 3D Gaussian map 與 camera parameters;(ii) 以 lightweight dynamic head 解耦 dynamics;(iii) 以 lifespan head 調制 visibility 以維持 temporal consistency;(iv) 以 diffusion-based rendering refinement 抑制 motion/interpolation artifacts、提升 sparse input 下的 novel-view 品質。

Abstract 末段強調這是「single-pass、pose-free」演算法,並用 Waymo、nuScenes、Argoverse2 三個大型 driving benchmark 給出量化保證:在各 dataset 自訓練與 zero-shot transfer 兩種設定下皆超越前人,且隨 input frame 增加仍能 scale 良好。最後揭露程式與模型已開源於 GitHub,凸顯可重現性。整體而言,這段文字將 DGGT 定位為「打破 pose-as-input 慣例」的 paradigm shift,並透過三個層級(問題痛點、設計哲學、實證成效)為後文 build 起期待:讀者帶著「pose 真能被 model 自己學出來嗎?」與「lifespan 與 diffusion refinement 為何不可或缺?」的疑問進入 Introduction。

### 3.2 Introduction

(360 words)

Introduction 的論述採三段式:problem framing、prior gap、design philosophy。第一段以 autonomous driving 訓練/評估的工程需求切入,主張 4D reconstruction 應像 pre-processing 一樣「a fraction of a second」即可完成,並能輸出 camera pose、3D Gaussian tracking、depth、dynamic map 等豐富中介資料以支援 instance-level scene editing(add car、remove cyclist)。Fig. 1 左用 teaser 展示這個能力,右則用 PSNR vs FPS 散點圖預告 DGGT 在 accuracy–efficiency 邊界上的優勢,讓讀者一眼看到全篇 punchline。

第二段把 feedforward 方向的既有努力(MVSplat、NoPoSplat、DepthSplat)點名為 static-only,將 STORM 標為 dynamic feedforward 的第一步,但批判其三項限制:仍需 pose、固定 frame 數的 short window、長序列退化。作者再將「pose-as-input」歸納為更深層的 formulation 缺陷,因為它阻礙 unposed 與 cross-dataset 部署。這段成功把 prior art 收斂到一個統一可被打破的假設上,為後續的「pose-as-output」翻轉鋪好正當性。

第三段闡述 design philosophy:「one-pass 預測整個 4D scene state,同時乾淨地分離 static background 與 moving entities,並維持 temporal coherence」。具體列出四項設計選擇:(i) camera pose 改成輸出;(ii) 在 pixel-aligned Gaussian map 上加 lifespan parameter 以調制時間 visibility;(iii) 以 dynamic head 產生 dynamic mask、以 motion head 估 3D motion 做 sparse timestamp 之間的 interpolation;(iv) 接 single-step diffusion refinement 抑制 ghosting 與 disocclusion 並補回 fine details。隨後簡介 backbone:ViT 編碼器融合 DINO features 與 alternating attention,共享 token 給 camera/Gaussian/lifespan/dynamic/motion/sky 六個 head,並用可微 GS renderer 提供監督訊號。

末段直接把實驗賣點塞進 Introduction:Waymo 27.41 PSNR、0.39 s 推論;zero-shot 至 nuScenes 25.31、Argoverse2 26.34;3D motion 0.183 m EPE3D 全面壓過 STORM;在 4/8/16-view 下 graceful scale,且支援 instance-level editing。這些數字形成「先給結論再展開細節」的強引導,讓讀者帶著明確的 expectation 進入 Method。

### 3.3 Related Work / Preliminaries

(330 words)

Related Works 採二分法 taxonomy 鋪陳:Dynamic scene reconstruction 與 Feedforward reconstruction,兩個軸線正好對應論文要同時解決的兩個維度,從而把 DGGT 的定位空缺自然浮現。

第一軸 Dynamic scene reconstruction 整理 NeRF 與 3DGS 在 dynamic 設定的延伸,並進一步把這些方法分為兩類:其一是 temporally conditioned representations,以 PVG 為代表,將 time 當作 explicit input、用 periodic vibration 訊號預測 3DGS,但因缺乏 disentangled、object-centric 表徵,難以支援 object editing 等下游任務;其二是 compositional scene graph,如 MARS(NeRFs)與 Street Gaussians(3DGS),透過將 dynamic entities 模組化為獨立 component 來支援 object-level manipulation,但代價是依賴外部 3D 標註(如 bounding box),取得成本高昂。作者再加一刀總結:多數現有方法都需 per-scene optimization,動輒數小時,因而不可規模化。這個段落為 DGGT 的「fast、feedforward、pose-free、無需外部 3D 標註」四重定位鋪好對立面。

第二軸 Feedforward reconstruction 從 vision transformer 重建 3D objects(LRM 系列)出發,接著到 scene-level feedforward 的代表作 Flash3D、MVSplat、NoPoSplat、DepthSplat,並指出這些雖能 generalize 跨場景且支援 real-time 推論,但仍侷限於 static environments。L4GM 是首個 4D feedforward reconstruction model 但偏向 object-level;STORM 是 driving 場景下的第一個 dynamic feedforward 框架,但受限於 input frame 數且難處理 long sequence。

最後段以一句 contrast 結束:DGGT 同時支援任意 input frame 數與不需 camera pose 兩項特性,因此比所有 prior art 更靈活、更高效。這段 related work 並未提供完整 preliminaries(沒有獨立小節介紹 3DGS rasterization、quaternion SLERP 等先備知識),而是把概念散布到 Method 中即用即講。整體鋪陳節奏緊湊,讀完即理解為何 DGGT 必須同時是 feedforward、pose-free、dynamic 與 long-sequence-friendly——任何缺一項都會掉回某個既有 baseline 的窠臼。

### 3.4 Method (overview narrative)

(300 words)

Method(§3)以三段式呈現,對應一條清晰的 dependency chain:先建立基本 pose-free feedforward 重建器(§3.1),再加上 dynamic decomposition 與 3D motion 處理動態(§3.2),最後接 diffusion refinement 修飾 sparse input 下的 rendering artifact(§3.3)。整章開頭即用 Fig. 2 給出全貌:輸入 unposed image 序列,經由 ViT 編碼器與 alternating attention 融合 DINO 特徵,再共享 token 餵給多個專用 head——camera head、Gaussian head、lifespan head、dynamic head、motion head、sky head——一次 forward 同時產生 camera 參數、pixel-aligned Gaussian map、dynamic mask、3D motion 與 sky Gaussian。

§3.1 Pose-Free Feedforward Reconstruction 鎖定「如何在沒有 pose 的情況下產生對齊的 per-frame 3D 場景」。作者把第一個 frame 設為 reference,所有 subsequent frame 對齊它;每個 pixel-aligned Gaussian 攜帶 15 維屬性,其中包含 lifespan parameter $\sigma$ 用以隨時間調制 opacity。由於 attention feature 偏 high-level semantics,作者將其與原始 DINO feature 融合,以保留外觀重建所需的空間細節。Sky 則以半球面採樣的 sky Gaussian 並配合 lightweight MLP 處理 unbounded 區域。

§3.2 Dynamic Decomposition with 3D Motion 處理 naïve 跨時間聚合產生的 ghosting:dynamic head 預測 dynamic mask,將 Gaussian map 分為 static 與 dynamic 兩部分,當前時刻的 full 表徵由「跨時間 static 聯集 + 當下 dynamic + sky」組成。對 sparse timestamp 之間的內插,motion head 預測 per-pixel 3D displacement,並以線性 interpolation 對 dynamic Gaussian 平移、SLERP 對 camera rotation 內插。

§3.3 接 single-step diffusion refinement,以 frozen VAE encoder + UNet denoiser + LoRA fine-tuned decoder 將 rendered frame 與隨機抽樣的 reference frame 一同 condition,專門修補 motion-induced ghosting 與 disocclusion gap。整體鋪陳由「重建幾何 → 解耦動態 → 修飾外觀」一氣呵成,為 §4 實驗中各 ablation 與 application 提供對應的設計動機。

### 3.5 Experiments (overview narrative)

(330 words)

Experiment(§4)以三層敘事承接 Method:先界定 protocol,再用 SOTA 比較證明整體效益,最後以 ablation 與 application 拆解設計貢獻。整章敘事邏輯與 Introduction 預告完全對齊——每一個 abstract 中宣稱的賣點都在這裡被一個對應實驗實證。

§4.1 Experimental protocol 將 Waymo Open Dataset 設為主訓練/評估場域(798 訓練、202 測試 scene),並用 nuScenes 與 Argoverse2 做 zero-shot 與 trained 兩條 generalization 軸線。指標選用 PSNR、SSIM 評估影像、RMSE 評估深度;3D tracking 則沿用 STORM 的 EPE3D、Acc5、Acc10、angular error。輸入設定為 20-frame、3-view 序列,固定取 frame 0/5/10/15 為 input、預測整 20 幀,既測 reconstruction 也測 NVS。

§4.2 Comparison with SOTA methods 是論文的主競技場。Baseline 涵蓋 optimization-based(EmerNeRF、3DGS、PVG、DeformableGS)、feedforward(LGM、GS-LRM、MVSplat、NoPoSplat、DepthSplat、STORM)以及作者擴充的 VGGT++。Tab. 1 在 Waymo 上 DGGT 以 27.41 PSNR、0.846 SSIM、3.47 D-RMSE、0.39 s 推論時間取得全項最佳,且同時是唯一 dynamic+pose-free 的方法。Tab. 2 在 nuScenes 與 Argoverse2 兩個 dataset 上做 zero-shot 與 trained 兩種設定,都明顯領先,作者並把此 generalization 歸因於 pose-free 設計減少了 dataset 特定相機軌跡的 overfit。3D motion 部分(Tab. 5)亦以 0.183 m EPE3D 領先 STORM 的 0.276,並由 Fig. 4 的 3D tracking 視覺化證實。

§4.3 Ablation study and Application 分四題:input view 數量擴展性(Tab. 3,DGGT 在 4/8/16 view 都穩定,STORM 隨 view 增加退化)、lifespan parameter(移除後 PSNR 從 27.41 掉到 24.21)、diffusion refinement(數值收益小但 Fig. 5/6 顯示 structural 修補明顯)、scene editing(Fig. 5 展示 add/remove/shift 車輛與插入跨場景 cyclist,並以 diffusion 修補 compositing hole)。整體實驗設計回應了 Introduction 的每一個宣稱,為 Conclusion 的 SOTA + scalable + editable 三項定論築好實證基礎。

### 3.6 Conclusion / Limitations / Future Work

(75 words)

Conclusion 章節極為精簡,以四句話收束全文。第一句重述貢獻定位:提出 pose-free、feedforward 的 4D scene reconstruction 框架,輸入為 unposed images。第二句點明方法統一了三件事——camera estimation、3D Gaussian reconstruction 與 3D motion prediction,並由 diffusion-based refinement 在 sparse input 下提升 fidelity。第三句以「large-scale datasets」與「SOTA performance with fast speed」一語帶過實驗成果,把 §4 的繁複表格濃縮成單一論斷,使讀者離開時帶走的是 paradigm shift 的整體印象而非個別數字。

接著 Limitations 與 Future Work 合併在同一段,只佔兩句:作者承認當 dynamic mask 不準或 tracking 在 heavy occlusion 下失效時,系統會產生 failure case;Future work 將集中於改善 dynamic modeling 與 enhancing tracking robustness,以更好地處理 complex dynamic scenes。

值得注意的是,這段 Conclusion 並未討論幾個其實在主文與 supplementary 中可見的潛在限制——例如 diffusion refinement 帶來的 PSNR/SSIM 收益偏小、模型仍需 LiDAR-based 3D bounding box 來建立訓練 dynamic mask、以及 Waymo-only training 對 sky/depth aligning 的依賴。作者選擇將 limitation 收緊到「mask 與 tracking 的 robustness」這一條軸線,使 future work 與全文 narrative(dynamic 解耦的精確度)保持一致,而非開放成多軸 wishlist。整體 Conclusion 的策略是「短、收斂、保留懸念」:不重複實驗數字、不延伸新主張,只把讀者帶回 Introduction 提出的核心翻轉(pose-as-output、single-pass、long-sequence-friendly),並以一個明確、可被後續工作接力的問題(occlusion 下的 dynamic tracking)結尾,使整篇論文在敘事上呈現閉環。

## 4. Critical Profile

### 4.1 Highlights

- 在 Waymo 上同時取得最佳 NVS 品質與具競爭力的速度:27.41 PSNR / 0.846 SSIM,單場景推論 0.39s(3 視圖 × 20 幀),勝過最佳化型 DeformableGS(25.29 PSNR、29 分鐘)與前饋型 STORM(26.38 PSNR、0.18s)(Tab 1)。
- 把「pose-free」「dynamic」「任意視圖數」三項先前各自孤立的能力首次合併到單次前饋過程中,以 Eq 7 的形式 $G_{sky}, \{G^t, F^t, M^t_d, \Pi^t\} = f_\theta(\{I^t\})$ 一次輸出全部 4D 狀態(Sec 3.1, Sec 3.2)。
- 跨資料集 zero-shot 表現顯著:僅以 Waymo 訓練即在 nuScenes 拿到 25.31 PSNR、Argoverse2 拿到 26.34 PSNR,均高於這兩個資料集上原生訓練的 STORM(24.54 / 24.97 PSNR)(Tab 2)。
- 提出 lifespan 參數 $\sigma$ 透過時間 Gaussian kernel 調制 opacity(Eq 1),讓「靜態但外觀隨時間變化」的區域(光照、陰影)不被誤分為動態,移除此參數時 PSNR 由 27.41 掉到 24.21(Tab 4, Fig 6)。
- 用顯式 per-pixel 3D 位移軌跡取代 STORM 的瞬時速度建模,在 Waymo Scene Flow 取得 0.183 m EPE3D / 85.42% Acc5 / 90.42% Acc10 / 0.328 rad 角誤差,全面領先 STORM 與 NSFP 系列(Tab 5)。
- 視圖數從 4 → 8 → 16 時 NVS PSNR 穩定上升(27.41 / 27.74 / 28.14),而 STORM 由 26.05 跌至 22.98,顯示時間視窗外推不會崩潰(Tab 3)。
- 以 single-step diffusion + frozen VAE encoder + LoRA decoder 的輕量 refinement 修補插值殘留的 ghosting 與 disocclusion 洞,可同時用於原始輸出與場景編輯後的合成圖(Sec 3.3, Fig 5)。
- Gaussian 級的靜/動分離直接支援 instance-level 編輯(刪車、移車、跨場景插入新車與行人),不需要重新訓練(Fig 5)。
- 架構是對 VGGT 的精簡擴展:共享 DINO + alternating-attention backbone 後接六個輕量 head(camera / Gaussian / lifespan / dynamic / motion / sky),訓練時凍結 feature extractor 與 camera head,降低收斂成本(Sec 3.1)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者在 Sec 5(Conclusions)明確指出當「dynamic mask 不準」或「在重度遮擋下 tracking 失敗」時,系統會出現失敗案例,並把這作為未來工作方向。
- 作者在 Sec 4.3(Diffusion Refinement 段落)承認 diffusion refinement 在 PSNR/SSIM 上只帶來極小的數值增益(0.09 dB),理由是 per-pixel 指標無法反映結構性瑕疵與補洞;但他們選擇保留此模組。
- 作者承認 VGGT++ 退化是因為 attention feature 保留的 RGB 細節有限(Sec 4.2),這也間接暴露 DGGT 必須額外把 DINO feature 與 attention feature 融合(Sec 3.1)才能維持 appearance fidelity,是被迫的工程修補。

#### 4.2.2 Phyra-inferred

- **未報告相機 pose 精度**:全文宣稱 pose 是模型輸出,但 Tab 1 / Tab 2 中沒有任何 ATE / RPE / rotation error 等 pose quality 指標,Tab 1 的「Pose-free」欄只是能力旗標,讀者無從判斷預測 pose 是否可被下游 SfM / SLAM / simulation 採用(Sec 3.1, Eq 7)。
- **「pose-free」存在訓練端漏洞**:camera head $H_{cam}$ 採 VGGT 預訓練權重並在訓練全程凍結(Sec 3.1),意味著 pose 預測能力是從一個用 calibrated multi-view 訓出的模型搬過來的;系統只在「推論時」pose-free,而上游監督仍隱含 pose 標定。
- **動態解耦並非自監督**:dynamic mask 的 GT 來自 Waymo LiDAR 3D box tracking 加上類別速度閾值(行人 > 0.2 m/s、車輛 > 0.5 m/s,Appendix A.1),沒有 LiDAR 標註的資料集無法以同流程取得監督,因此「跨資料集 generalize」與「跨資料集 train from scratch」的可行性繫於目標資料集是否提供同等品質的 box tracking。
- **Diffusion refinement 訓練資料極窄**:僅約 2,000 clips 來自 798 個 Waymo scene(Sec 3.3),且 Tab 2 zero-shot 結果未獨立 ablate diffusion 模組,讀者無法分辨跨資料集增益是來自 pose-free 幾何管線本身,還是這個只在 Waymo 風格上見過 artifact 的 refinement 模組。
- **長序列宣稱被 16-view 上限封頂**:Tab 3 只測 4 / 8 / 16 views,但 Waymo 每場景 190–200 幀(Sec 4.1),「arbitrary number of input views」並未在百幀以上實測;且 8-view NVS PSNR 27.74 與 4-view 27.41 差距僅 0.33 dB,16-view 也只升到 28.14,scaling 曲線疑似已飽和或欠訓。
- **Lifespan ablation 增益(3.20 dB)遠大於 diffusion ablation(0.09 dB)**:作者把 lifespan 解讀為「捕捉靜態區域外觀變化」,但同樣大的數字也可由「掩蓋靜/動分類誤差,讓被誤判為靜態的動態 Gaussian 在錯位時間自然衰減」解釋(Tab 4);文中沒有專門隔離光照/陰影變化案例的實驗來證實前者。
- **時間插值假設過強**:Eq 6 對 dynamic mean 走線性、對 camera translation 走線性、對 rotation 走 SLERP,等同假設 ego-motion 與物體軌跡在相鄰輸入幀之間皆為均勻運動;急轉彎、急煞、不等距時間戳的情境並無 robustness 實驗。
- **Motion head 受惠於外部預訓練**:$H_{motion}$ 以 TaPIP3D 預訓練權重初始化(Sec 3.2, ref [78]),Tab 5 的 SOTA 部分繼承自該預訓練;沒有「from-scratch」motion head 的 ablation 來區分新架構與預訓練的貢獻。

### 4.3 Phyra's Judgment (summary)

DGGT 真正的新穎處在於整合而非新原語:把「pose 改為輸出」「lifespan 調制可見度」「顯式 3D 軌跡 + 線性插值」「single-step diffusion 補洞」這四件事拼成一個前饋模型,並證明這個組合在 Waymo / nuScenes / Argoverse2 上同時打贏優化型與前饋型基線。但每個元件都來自既有方向(VGGT 給 backbone+pose、TaPIP3D 給 motion 預訓練、ADD 給 single-step diffusion、STORM 提供任務範式),所以貢獻偏 system integration 與 scaling。最關鍵的未解問題是:這套系統輸出的 pose 與 dynamic decomposition 是否真能撐起下游 simulation/perception 流水線——pose 精度、dynamic mask 跨資料集可遷移性、>16 view 的長序列穩定性,目前都沒被量化。

## 5. Methodology Deep Dive

### 5.1 Method Overview

DGGT 是一個**單次前向（single forward pass）** 的 4D 動態駕駛場景前饋重建模型，其核心設計哲學是「將相機 pose 由輸入改為輸出」。給定 N 張未校準（unposed）的 RGB 影格 $\{I_t\}_{t=1}^{N}$，模型 $f_\theta$ 在一次前向中聯合輸出每幀相機外/內參 $\Pi_t$、像素對齊的 3D Gaussian map $G_t \in \mathbb{R}^{H \times W \times 15}$、動態遮罩 $M_d^t$、3D 運動場 $F^t$ 與遠景 sky Gaussian $G_\text{sky}$。整體 pipeline 解除了傳統方法對外部 pose 標定與逐場景最佳化的依賴，使其能處理任意視圖數與長序列輸入。

骨幹採用 ViT 將輸入影格 patchify 後送入 DINO-pretrained encoder 取得 $F_\text{dino}$，再經 alternating attention 精修為 $F_\text{attn}$。多個輕量 head 共享此 token：camera head $H_\text{cam}$ 預測 pose、Gaussian head $H_\text{gs}$（融合 $F_\text{dino}$ 與 $F_\text{attn}$ 以保留外觀細節）輸出每像素 Gaussian、lifespan head $H_\text{life}$ 控制時間可見度、dynamic head $H_\text{dy}$ 產生動態遮罩、motion head $H_\text{motion}$ 預測 3D 運動軌跡，並有獨立 sky head $H_\text{sky}$ 處理遠景 hemisphere Gaussian。lifespan 參數 $\sigma$ 透過時間調制 opacity 來捕捉光照變化等靜態區域的時序變化（見公式 1）。

動態分解階段以 dynamic map 將 $G_t$ 拆為靜態 $G_s^t$ 與動態 $G_d^t$ 兩部分（公式 2），組合策略為「累積所有幀的靜態 Gaussian + 當前幀的動態 Gaussian + sky Gaussian」（公式 3）以避免移動物體的鬼影。對於稀疏時間戳之間的中介幀，motion head 預測完整 3D 位移軌跡 $F(t_a, t_b) \in \mathbb{R}^{q \times 3}$（不同於 STORM 僅建模速度），搭配線性插值（位移）與 SLERP（相機旋轉）填補中介幀。最後透過可微 GS renderer 渲染得到 $\hat{I}^{t}$，並經單步 diffusion-based refinement 模組 $f_\text{diffusion}$ 修補 ghosting 與 disocclusion 瑕疵（公式 11）。

### 5.2 Pipeline Diagram with Tensor Shapes

論文未明確說明 patch size、hidden dimension、query 數量 $q$ 等細節，標記為 `?`。

```
Input: {I_t}_{t=1}^N                                     [B, N, 3, H, W]
   │
   ├→ Feature Extractor (DINO-pretrained ViT, frozen)
   │      patchify + encode                              [B, N, L, d]   (L=H/p × W/p, d=?)
   │      → F_dino                                       [B, N, L, d]
   │
   ├→ Feature Aggregation (Alternating Attention)
   │      → F_attn                                       [B, N, L, d]
   │
   ├→ Camera Head H_cam (frozen, from VGGT) ────────→ Π_t = (extrinsics, intrinsics)
   │      input:  F_attn                                 [B, N, L, d]
   │      output: Π_t                                    [B, N, 7+4]   (quat+trans+intrinsics; exact dim ?)
   │
   ├→ Feature Fusion: concat(F_dino, F_attn) ────────→ F_fused  [B, N, L, 2d] (融合方式 ?)
   │
   ├→ Gaussian Head H_gs ────────────────────────────→ G_t       [B, N, H, W, 15]
   │      per-pixel: (c, μ, r, s, o, σ) = (3+3+4+3+1+1)
   │
   ├→ Lifespan Head H_life ──────────────────────────→ σ_t       [B, N, H, W, 1]   (已併入 G_t)
   │
   ├→ Dynamic Head H_dy ─────────────────────────────→ M_d^t     [B, N, H, W, 1]   (sigmoid prob)
   │      input: F_attn
   │
   ├→ Sky Head H_sky (lightweight MLP) ──────────────→ G_sky     [B, K, 15]        (K=?, hemisphere samples)
   │
   └→ Motion Head H_motion (transformer-based)
          inputs: query pixels Q (from M_d^{t_a}=1)     [B, q, 2]   (q=?)
                  G^{t_a}, G^{t_b}                      [B, H, W, 15] each
                  I^{t_a}, I^{t_b}                      [B, 3, H, W] each
          → F(t_a, t_b)                                 [B, q, 3]   (3D displacement per query)

Dynamic Decomposition (per timestamp t)
   G_s^t = G_t ⊙ (1 − M_d^t)                            [B, N, H, W, 15]
   G_d^t = G_t ⊙ M_d^t                                  [B, N, H, W, 15]

Motion Interpolation (intermediate t_i ∈ [t_a, t_b])
   ω_{t_i} = (t_i − t_a) / (t_b − t_a)                  scalar
   μ_d^{t_i} = μ_d^{t_a} + ω_{t_i} · F(t_a, t_b)        [B, q, 3]
   Π_{t_i}: trans 線性插值, rot SLERP(quat)             [B, 7]

Composition
   Ĝ^t = (∪_{t'=1}^{N} G_s^{t'}) ∪ G_d^t ∪ G_sky        [B, M, 15]   (M=∑frames + sky pts)

Differentiable GS Renderer
   Î^t = Renderer(Ĝ^t, Π_t)                             [B, 3, H, W]

Diffusion-based Refinement (post-render)
   z = VAE_enc(concat(Î^{t_i}, I_ref))                  [B, c_z, H/8, W/8]   (c_z=?)
   z' = UNet_denoise(z)                                 [B, c_z, H/8, W/8]
   Ĩ^{t_i} = VAE_dec_LoRA(z')                           [B, 3, H, W]

Output: {Π_t, G_t, F^t, M_d^t}_{t=1}^N, G_sky, Ĩ^{t_i}
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Feature Extractor + Aggregation（ViT Backbone）

**Function:** 將未校準輸入影格序列映射為共享的 spatial-temporal token 表徵，供下游所有 head 使用。

**Input:**
- Name: $\{I_t\}_{t=1}^{N}$
- Shape: `[B, N, 3, H, W]`
- Source: 原始未校準 RGB 影格

**Output:**
- Name: $F_\text{dino}$, $F_\text{attn}$
- Shape: `[B, N, L, d]`（兩者同形）
- Consumer: 下游所有 head（其中 $F_\text{attn}$ 餵 camera/dynamic/lifespan，$F_\text{dino}+F_\text{attn}$ 融合後餵 Gaussian head）

**Processing:**

1. 影格 patchify 為 token 序列。
2. 通過 DINO-pretrained feature extractor 取得 $F_\text{dino}$（高層語義為主）。
3. 經 alternating attention 機制精修，輸出 $F_\text{attn}$（page 4 文字段）。

論文於 Sec 3.1 指出 $F_\text{attn}$「primarily encodes high-level semantics and lacks sufficient detail for appearance reconstruction」，故 Gaussian head 才需要與 $F_\text{dino}$ 融合。

**Key Formulas:**

無顯式公式，僅文字描述：$F_\text{attn} = \text{AlternatingAttn}(F_\text{dino})$。

**Implementation Details:**

訓練時 feature extractor 與 camera head 凍結（page 3：「we freeze the feature extractor and camera head, while training the remaining heads from scratch」），其餘 head 從零訓練。Patch size、token 維度 $d$、alternating attention 的層數與「alternating」具體交替形式（spatial↔temporal？frame↔frame？）論文未說明。Backbone 衍生自 VGGT (Wang et al.)，並擴展為 VGGT++（Tab. 1 對照）。

#### 5.3.2 Camera Head $H_\text{cam}$

**Function:** 從共享 token 預測每幀相機外參與內參，使方法支援未校準輸入。

**Input:**
- Name: $F_\text{attn}$
- Shape: `[B, N, L, d]`
- Source: Feature Aggregation

**Output:**
- Name: $\Pi_t$
- Shape: `[B, N, ?]`（外參 + 內參，論文未指定具體參數化維度）
- Consumer: differentiable GS renderer；motion interpolation 中的 SLERP/linear 插值

**Processing:**

$\Pi_t = H_\text{cam}(F_\text{attn})$（page 3）。第一幀 $I_1$ 被指定為 reference frame，其相機原點為世界座標原點，所有後續幀均對齊至此參考系，確保 3D 定位的時序一致性。

**Key Formulas:**

$$
\Pi_t = H_\text{cam}(F_\text{attn})
$$

**Implementation Details:**

訓練時凍結（pretrained from VGGT 思路衍生）。論文未具體說明 pose 參數化（例：四元數 vs. 6D rotation、是否含焦距/principal point）。第一幀作為 world origin，使用 cross-frame attention 完成多幀對齊。

#### 5.3.3 Gaussian Head $H_\text{gs}$ + Lifespan Head $H_\text{life}$

**Function:** 對每像素生成 3D Gaussian 屬性（顏色、位置、旋轉、尺度、不透明度、生命期），構成像素對齊 Gaussian map。

**Input:**
- Name: $F_\text{dino}$, $F_\text{attn}$
- Shape: 各 `[B, N, L, d]`
- Source: Feature Extractor + Feature Aggregation（兩者融合）

**Output:**
- Name: $G_t$
- Shape: `[B, N, H, W, 15]`，每像素編碼 $(c, \mu, r, s, o, \sigma)$，維度為 $3+3+4+3+1+1=15$
- Consumer: dynamic decomposition；GS renderer

**Processing:**

論文 Sec 3.1 給出 $G_t = H_\text{gs}(F_\text{dino}, F_\text{attn})$（page 4）：兩特徵融合（具體融合運算如 add/concat 未說明），由 Gaussian head 產生每像素 15 維 primitive。Lifespan $\sigma_{i,j}^t \in \mathbb{R}^+$ 控制 Gaussian 的時序傳播：給定參考時刻 $t$，在另一時刻 $t'$ 的 opacity 依高斯衰減（公式 1）。較大的 $\sigma$ 表示更持久的 Gaussian，較小則時序快速消逝。論文於 Sec 3.1 強調此 lifespan 設計相對 STORM 能更精確捕捉靜態區域的外觀變化（如光照），並穩定動態分解。

**Key Formulas:**

$$
o^{t'} = o^t \cdot \exp\!\left(-\tfrac{1}{2} \cdot \frac{(t' - t)^2}{\sigma^t}\right) \quad \text{(Eq. 1)}
$$

$$
G_t = H_\text{gs}(F_\text{dino}, F_\text{attn})
$$

**Implementation Details:**

Lifespan head 與 Gaussian head 是兩個輕量 head，但 lifespan 參數 $\sigma$ 直接歸入 $G_t$ 的 15 維編碼中。訓練時對 lifespan 施加 $\ell_1$ 正則 $L_\text{lifespan} = \|1/\sigma\|_1$（page 5），假設多數場景為靜態（即偏好較大 $\sigma$）。融合運算的具體形式（concat vs. add vs. cross-attn）論文未詳述。

#### 5.3.4 Dynamic Head $H_\text{dy}$ + Sky Head $H_\text{sky}$

**Function:** Dynamic head 預測動態區域機率圖以分離移動物體與靜態背景；sky head 對距景天空使用 hemisphere 上均勻採樣的 Gaussian 補強無界區域。

**Input:**
- Dynamic head：$F_\text{attn}$，`[B, N, L, d]`
- Sky head：hemisphere 上以固定半徑 $r_\text{sky}$ 均勻採樣的 3D 點 + 投影所得初始顏色

**Output:**
- $M_d^t$：`[B, N, H, W, 1]`（sigmoid 輸出，每像素動態機率）
- $G_\text{sky}$：`[B, K, 15]`（K = hemisphere 採樣數，論文未指定）

**Processing:**

Dynamic：$M_d^t = H_\text{dy}(F_\text{attn})$（page 4）。隨後將 Gaussian map 拆解：

$$
G_s^t = G_t \odot (1 - M_d^t), \quad G_d^t = G_t \odot M_d^t \quad \text{(Eq. 2)}
$$

Sky（page 3）：在固定半徑 $r_\text{sky}$ 的半球面上均勻採樣中心點，固定 rotation 與 opacity，將 3D 座標投影回輸入影格擷取 pixel color 作為初始 RGB；以輕量 MLP $H_\text{sky}$ 精修顏色與 scale，提升一致性。

任意時刻 $t$ 的完整 Gaussian 表徵組合為：

$$
\hat{G}^t = \left(\bigcup_{t'=1}^{N} G_s^{t'}\right) \cup G_d^t \cup G_\text{sky} \quad \text{(Eq. 3)}
$$

**Key Formulas:**

公式 2、公式 3 如上。

**Implementation Details:**

Dynamic head 以 BCE 監督（公式 9）：$L_\text{dynamic} = \text{BCE}(M_d, \hat{M}_\text{dynamic})$。Sky 區域使用 rendered opacity 與 ground-truth $\hat{M}_\text{sky}$ 監督（公式 9 中的 $L_\text{opacity}$）。Hemisphere 採樣數 K、$r_\text{sky}$ 具體值論文未說明。Sky MLP 為「lightweight」，深度/寬度未詳述。

#### 5.3.5 Motion Head $H_\text{motion}$（3D Motion Estimation + Interpolation）

**Function:** 對每個查詢像素預測完整 3D 位移軌跡（非僅速度），用於對齊不同時間戳間的動態 Gaussian 並合成中介幀。

**Input:**
- Query pixels $Q$：`[B, q, 2]`（從 $M_d^{t_a}=1$ 的像素中選取，q 數量論文未指定）
- $G^{t_a}, G^{t_b}$：`[B, H, W, 15]` 各一
- $I^{t_a}, I^{t_b}$：`[B, 3, H, W]` 各一

**Output:**
- $F(t_a, t_b)$：`[B, q, 3]`（每查詢像素的 3D 位移向量）
- Consumer: Motion interpolation → 動態 Gaussian 平移

**Processing:**

論文 Sec 3.2（page 4–5）描述：影像先被編碼為 multi-scale features，與從 Gaussian map 擷取的 3D 點聯合構成 spatio-temporal feature cloud。每個時刻 $t_a$，將 $M_d^{t_a}$ 中為 1 的像素作為 query $Q$，反投影得到初始 3D 位置，再以 neighborhood-to-neighborhood attention 迭代精修軌跡：

$$
F(t_a, t_b) = H_\text{motion}(Q \mid G^{t_a}, G^{t_b}, I^{t_a}, I^{t_b}) \quad \text{(Eq. 5)}
$$

中介時刻 $t_i \in [t_a, t_b]$ 的動態 Gaussian 中心：

$$
\mu_d^{t_i} = \mu_d^{t_a} + \omega_{t_i} \cdot F(t_a, t_b), \quad \omega_{t_i} = \frac{t_i - t_a}{t_b - t_a} \quad \text{(Eq. 6)}
$$

相機 pose 對 $t_i$：translation 線性插值 $\Pi^{t_a} \to \Pi^{t_b}$，rotation 以 SLERP 對 quaternion 插值。

**Key Formulas:**

$$
F(t_a, t_b) = H_\text{motion}(Q \mid G^{t_a}, G^{t_b}, I^{t_a}, I^{t_b}) \quad \text{(Eq. 5)}
$$

$$
\mu_d^{t_i} = \mu_d^{t_a} + \omega_{t_i} \cdot F(t_a, t_b) \quad \text{(Eq. 6)}
$$

**Implementation Details:**

Motion head 為 transformer-based，以 TAPIP3D（[78]）的預訓練權重初始化（page 5），再以 photometric loss 在插值幀上微調。Query 數 q、neighborhood-to-neighborhood attention 的具體尺寸與層數論文未詳述。整體前向過程綜合為公式 7：

$$
G_\text{sky}, \{G_t, F^t, M_d^t, \Pi_t\}_{t=1}^{N} = f_\theta(\{I_t\}_{t=1}^{N}) \quad \text{(Eq. 7)}
$$

#### 5.3.6 Differentiable GS Renderer

**Function:** 將組合好的 Gaussian 集合與相機參數渲染為 2D 影像，提供可微監督路徑。

**Input:**
- $\hat{G}^t$：`[B, M, 15]`（M = 累積靜態 + 當前動態 + sky Gaussian 總數）
- $\Pi_t$：`[B, N, ?]`

**Output:**
- $\hat{I}^t$：`[B, 3, H, W]`
- Consumer: 訓練 loss（公式 8、10）；diffusion refinement 的輸入

**Processing:**

$$
\hat{I}^t = \text{Renderer}(\hat{G}^t, \Pi_t) \quad \text{(Eq. 4)}
$$

採用標準 3DGS 可微 rasterization，反向傳播訊號回傳至所有 head。

**Key Formulas:**

公式 4 如上。

**Implementation Details:**

訓練每個 iteration 隨機採樣 $N \in [4, 8]$ 張輸入影格，搭配 $2N$ 張 ground-truth target，模型輸出 $2N$ 張插值幀。Reconstruction loss 為 $\ell_2$ 加 LPIPS：

$$
L_\text{rgb} = L_{\ell_2} + \lambda_\text{LPIPS} L_\text{LPIPS} \quad \text{(Eq. 8)}
$$

整體訓練目標（公式 10）為：

$$
L_\text{feedforward} = L_\text{rgb} + \lambda_\text{opacity} L_\text{opacity} + \lambda_\text{dynamic} L_\text{dynamic} + \lambda_\text{lifespan} L_\text{lifespan}
$$

權重 $\lambda$ 的具體數值論文未公開。

#### 5.3.7 Diffusion-based Rendering Refinement $f_\text{diffusion}$

**Function:** 針對運動估計誤差與大幅度視角變化造成的 ghosting / disocclusion 瑕疵，以單步 diffusion 進行影像空間後處理修復。

**Input:**
- $\hat{I}^{t_i}$：`[B, 3, H, W]`（GS renderer 輸出的中介幀）
- $I_\text{ref}$：`[B, 3, H, W]`（從輸入序列隨機抽取的參考影格）

**Output:**
- $\tilde{I}^{t_i}$：`[B, 3, H, W]`（refined 影像）

**Processing:**

兩張影像 frame-wisely concat 後送入 frozen VAE encoder 取得 latent，再經 UNet denoiser 去噪，最後由 LoRA-finetuned decoder 解碼回 RGB（page 5，Sec 3.3）：

$$
\tilde{I}^{t_i} = f_\text{diffusion}(\hat{I}^{t_i}, I_\text{ref}) \quad \text{(Eq. 11)}
$$

**Key Formulas:**

公式 11 如上。整體目標：

$$
L_\text{diffusion} = L_\text{Recon} + L_\text{LPIPS} + \lambda_\text{Gram} L_\text{Gram} \quad \text{(Eq. 12)}
$$

其中 $L_\text{Gram}$ 為基於 VGG-16 features Gram matrices 的 style loss，用以提升銳度與細節。

**Implementation Details:**

基於 single-step diffusion 框架（Adversarial Diffusion Distillation, [43]）。VAE encoder 凍結，UNet 為 denoiser，decoder 採 LoRA 微調。訓練資料為作者從 798 個 Waymo training scenes 中精選約 2,000 clips，輸入為帶瑕疵的插值幀，輸出為對應 refined 幀。$\lambda_\text{Gram}$ 數值、UNet 架構規模、LoRA rank 論文未說明。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Waymo Open Dataset | 4D dynamic driving scene reconstruction、NVS、3D motion estimation | 798 training scenes、202 test scenes，每場景 190–200 frames | train: 798 scenes(訓練集) / test: 202 scenes(Scene Flow validation split，附錄 A.2) |
| nuScenes (v1.0) | 跨資料集泛化 NVS（zero-shot 與 target-domain training） | 約 1,000 scenes，每場景約 20s，camera 12 Hz；本文隨機抽取 600 scenes | train: 500 scenes(僅 trained 設定) / test: 100 scenes |
| Argoverse2 Sensor Dataset | 跨資料集泛化 NVS（zero-shot 與 target-domain training） | 約 1,000 sequences，camera 約 20 Hz；本文選用 600 sequences | train: 500 sequences(僅 trained 設定) / test: 100 sequences |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PSNR (dB) | 對 rendered RGB image 與 ground-truth 計算的 peak signal-to-noise ratio，數值越高越好 | yes |
| SSIM | 結構相似度，數值越高越好 | no |
| LPIPS | Learned perceptual similarity，數值越低越好（主要用於 nuScenes/Argoverse2） | no |
| D-RMSE | Depth RMSE，僅在 non-sky 有效區域計算，且 pose-free 方法（NoPoSplat、Ours）採用 linear alignment 後再計算 | no |
| EPE3D (m) | 3D scene flow 端點誤差，數值越低越好 | no |
| Acc5 / Acc10 (%) | 3D motion 在 5/10 cm（或 5/10% 相對閾值，論文未明確）內被視為正確的比例 | no |
| θ (rad) | 3D motion vector 的 angular error，數值越低越好 | no |
| Inference time (s) | 每場景推論時間（與 PSNR 一同呈現於 Fig.1 與 Tab.1，做為 accuracy–efficiency tradeoff 的依據） | no |

### 6.3 Training and Inference Settings

- **Hardware（training）**：8 × NVIDIA H200 GPUs，訓練約 24 小時、約 5,000 iterations 收斂（Appendix A.2）。
- **Hardware（evaluation）**：所有 baseline 與本方法統一在 NVIDIA A100 上評測，以對齊 STORM 的計時條件（Appendix A.2）。
- **Batch size、optimizer、learning rate schedule**：the paper does not specify。
- **Input sampling（training）**：每個 iteration 隨機取 $N \in [4, 8]$ 張 input images，並預測 $2N$ 個 interpolated frames，以對應的 $2N$ ground-truth 影像監督（§3.2 Training Objectives）。
- **影像解析度與資料對齊**：所有資料集統一 down/resample 到 $518 \times 518$，augmentation、optimizer、schedule 皆與 Waymo 設定一致；nuScenes/Argoverse2 的 trained 設定通常約 1,000 epochs 收斂（Appendix B.1）。
- **Frozen 模組**：feature extractor 與 camera head 在訓練時凍結，其餘 heads 從頭訓練（§3.1）。motion head 以 TAPIP3D 預訓練權重 [78] 初始化，再以 photometric loss on interpolated frames 微調。
- **Loss 權重 $\lambda_{\text{LPIPS}}, \lambda_{\text{opacity}}, \lambda_{\text{dynamic}}, \lambda_{\text{lifespan}}, \lambda_{\text{Gram}}$**：the paper does not specify。
- **Diffusion refinement training data**：自 798 個 Waymo training scenes 整理出約 2,000 個 clips，input 為含 artifacts 的 interpolated frames、target 為對應 ground-truth frames（§3.3）。
- **Inference setup（main table）**：3 個 camera 視角（forward、front-left、front-right），以 frame ID $\{0, 5, 10, 15\}$ 作為 input、預測 frame 0–19（共 20 frames），場景數為 Scene Flow validation 的 202 scenes；per-scene optimization baselines 統一 fit 5,000 iterations，feedforward 方法不受該迭代限制（Appendix A.2）。
- **Pose-free 深度對齊**：NoPoSplat 與 Ours 預測 relative depth，計算 D-RMSE 前先做 linear alignment（Appendix A.2）。

### 6.4 Main Results

Waymo（3 views、20 frames per view、interpolation between adjacent input views，Tab.1）：

| Method | PSNR ↑ | SSIM ↑ | D-RMSE ↓ | Inference time | Notes |
|---|---|---|---|---|---|
| EmerNeRF | 24.51 | 0.738 | 33.99 | 14 min | per-scene；dynamic；need-pose |
| 3DGS | 25.13 | 0.741 | 19.68 | 23 min | per-scene；static |
| PVG | 22.38 | 0.661 | 13.01 | 27 min | per-scene；dynamic |
| DeformableGS | 25.29 | 0.761 | 14.79 | 29 min | per-scene；dynamic |
| LGM | 18.53 | 0.447 | 9.07 | 0.06 s | feedforward；static |
| GS-LRM | 25.18 | 0.753 | 7.94 | 0.02 s | feedforward；static |
| MVSplat | 20.56 | 0.697 | 10.13 | 0.08 s | feedforward；static |
| NoPoSplat | 24.31 | 0.751 | 9.08 | 23.22 s | feedforward；pose-free；static |
| DepthSplat | 23.26 | 0.696 | 10.05 | 0.11 s | feedforward；static |
| STORM* (replicated) | 26.05 | 0.819 | 5.91 | 0.50 s | feedforward；dynamic；need-pose |
| STORM | 26.38 | 0.794 | 5.48 | 0.18 s | feedforward；dynamic；need-pose |
| VGGT++ | 22.50 | 0.749 | 3.80 | 0.24 s | feedforward；pose-free；static |
| **Ours (DGGT)** | **27.41** | **0.846** | **3.47** | **0.39 s** | **feedforward；dynamic；pose-free** |

Cross-dataset generalization（Tab.2）：

| Setting / Method | nuScenes PSNR ↑ | nuScenes SSIM ↑ | nuScenes LPIPS ↓ | Argoverse2 PSNR ↑ | Argoverse2 SSIM ↑ | Argoverse2 LPIPS ↓ |
|---|---|---|---|---|---|---|
| Zero-shot MVSplat | 17.84 | 0.563 | 0.451 | 18.67 | 0.647 | 0.304 |
| Zero-shot NoPoSplat | 19.75 | 0.545 | 0.394 | 22.00 | 0.646 | 0.237 |
| Zero-shot DepthSplat | 19.52 | 0.601 | 0.376 | 22.05 | 0.636 | 0.280 |
| Zero-shot STORM | 17.77 | 0.669 | 0.394 | 20.83 | 0.542 | 0.326 |
| **Zero-shot Ours** | **25.31** | **0.794** | **0.152** | **26.34** | **0.812** | **0.155** |
| Trained STORM | 24.54 | 0.784 | 0.267 | 24.97 | 0.791 | 0.240 |
| **Trained Ours** | **26.63** | **0.813** | **0.122** | **26.96** | **0.831** | **0.118** |

3D motion estimation（Waymo Scene Flow，Tab.5）：

| Method | EPE3D (m) ↓ | Acc5 (%) ↑ | Acc10 (%) ↑ | θ (rad) ↓ |
|---|---|---|---|---|
| NSFP | 0.698 | 42.17 | 54.26 | 0.919 |
| NSFP++ | 0.711 | 53.10 | 63.02 | 0.989 |
| STORM | 0.276 | 81.12 | 85.61 | 0.658 |
| **Ours** | **0.183** | **85.42** | **90.42** | **0.328** |

### 6.5 Ablation Studies

- **Lifespan parameter（Tab.4、Fig.6）**：移除 lifespan 後 PSNR 由 27.41 掉到 24.21（−3.20）、SSIM 由 0.846 掉到 0.774、LPIPS 由 0.109 升到 0.169。論文歸因於 lifespan 用於建模 static 區域隨時間的外觀變化（如光照），缺它會讓 Gaussian 無法吸收這些細節並推擠到動態分解。屬於診斷性 ablation：直接驗證了 §3.1 提出的 $\sigma$ 確實在分擔「靜態外觀變化」這個職責，而非單純背景重建的 sanity check。
- **Diffusion refinement（Tab.4、Fig.5、Fig.6）**：移除 refinement 後 PSNR 從 27.41 → 27.32（−0.09）、SSIM 從 0.846 → 0.844、LPIPS 從 0.109 → 0.108（LPIPS 反而些微更低）。作者承認 PSNR/SSIM 的數值收益小，但論述其價值在於修補 ghosting/disocclusion 與 scene editing 的 hole（Fig.5 紅框）。**這個 ablation 的問題**在於：所選度量（pixel-wise PSNR/SSIM、LPIPS）對 refinement 想解決的「結構性 artifact」並不敏感，作者也明確點出這個錯位，但未補上 user study、editing 任務的下游量化、或 artifact 局部度量等更對應的數值診斷，因此 refinement 的「實質貢獻」其實並未被定量證明，僅靠定性圖支持。
- **Number of input views（Tab.3，4 / 8 / 16 views）**：本身同時是 ablation 與 scaling study。Ours 在 reconstruction PSNR 維持 30.54 / 31.41 / 30.66，NVS PSNR 為 27.41 / 27.74 / 28.14；STORM 在 reconstruction 從 26.55 → 25.11 → 23.69、NVS 從 26.05 → 25.44 → 22.98 顯著退化。**這個 ablation 直接打中本論文的 selling point**（任意數量輸入、長序列 robust），對 §1 對 STORM「short window / fixed frames」的批評提供關鍵實證，屬於高診斷力實驗。
- **Ablation 涵蓋面的缺口**：論文沒有對 dynamic head $H_{dy}$、motion head $H_{\text{motion}}$、sky head $H_{\text{sky}}$、以及 pose-free 相對於 pose-conditioned 變體做 isolation 實驗。也就是「所有 head 一起拿掉 $\Rightarrow$ 沒有此 head」的取捨，並未個別量化。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — STORM (ICLR 2025) 為 feedforward dynamic driving scene 當前 SoTA，並另含 NoPoSplat、DepthSplat、VGGT++ 等多個近期強 baseline（Tab.1）。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時在 Waymo、nuScenes、Argoverse2 上評測，且涵蓋 NVS 與 3D motion estimation 兩個 task（Tab.1、Tab.2、Tab.5）。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — lifespan 與 #views 為診斷性實驗，但 dynamic head / motion head / sky head / pose-free vs. pose-conditioned 都缺獨立 ablation；diffusion refinement 的度量選擇與其聲稱的貢獻錯位（§6.5）。
- [covered] Has a scaling study (size, length, or compute) — Tab.3 系統性比較 4 / 8 / 16 input views 下的 reconstruction 與 NVS 表現，明確展示對 sequence length 的 scaling。
- [covered] Has an efficiency / wall-clock comparison — Tab.1 與 Fig.1(Right) 報告每場景 inference time（從分鐘級到秒級）以及 PSNR–FPS 散點，且統一在 A100 上量測（Appendix A.2）。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 全部 PSNR/SSIM/LPIPS/D-RMSE/EPE3D 皆為單點數值，未報告多 seed 平均、std、或信賴區間，論文未說明任何 run-to-run variance。
- [partial] Releases code / weights / data sufficient for reproducibility — 摘要與首頁註明 code 與 models 將釋出於 https://github.com/xiaomi-research/dggt ，但部分關鍵超參（optimizer、learning rate、loss 權重 $\lambda_{\cdot}$、batch size）論文並未在正文或附錄中具體交代。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1:Pose-free dynamic feedforward 4D 重建在單次前饋中完成。** **Supported**(Eq 7 形式化、Tab 1 同時提供 PSNR/SSIM/D-RMSE/inference time、Fig 3 視覺驗證)。
- **Claim 2:支援任意輸入視圖數、可擴展到長序列。** **Partially supported**:Tab 3 只到 16 views,雖然趨勢比 STORM 穩定,但 Waymo 場景原生長度為 190–200 幀,作者選擇不在這個量級實測,因此「任意長度」目前只在 4–16 視圖的小範圍內被驗證。
- **Claim 3:在 SOTA 重建品質下保持具競爭力的速度。** **Supported on quality, partially on speed**:rendering 品質確實 SOTA(Tab 1),但 0.39s 並非最快(GS-LRM 0.02s, MVSplat 0.08s),作者也未在主表中強調這點。
- **Claim 4:Zero-shot 跨資料集泛化。** **Supported**(Tab 2:nuScenes 25.31 / Argoverse2 26.34,均高於對方資料集原生訓練的 STORM)。但 zero-shot 評測僅針對 NVS,沒有包含 pose accuracy 或 motion estimation 的跨資料集數字。
- **Claim 5:Diffusion refinement 抑制 motion/interpolation artifacts。** **Partially supported / quantitatively weak**:Tab 4 顯示 PSNR/SSIM 增益僅 0.09 / 0.002(基本上在雜訊範圍內),作者改以 Fig 5 / Fig 6 的定性圖佐證,但沒有 FVD、user study 或 perceptual metric 量化結構性修補品質。
- **Claim 6:Instance-level scene editing。** **Supported qualitatively**(Fig 5),但沒有編輯保真度 / 一致性 / 時序穩定性的量化指標,也沒有與 OmniRe、MARS、Street Gaussians 這類專為編輯設計的 scene-graph 方法做對照。

### 7.2 Fundamental Limitations of the Method

**Pose 既是輸出也是無人監督的盲點。** 系統把 camera pose 從「輸入」改為「輸出」是核心設計訴求,但 $H_{cam}$ 在訓練全程凍結並繼承自 VGGT(Sec 3.1),整篇論文又不報告任何 pose 品質指標。這意味著當預測 pose 漂移時,失敗只會在 rendering 上表現為輕微模糊或細節錯位,而不會被任何指標直接捕捉。此問題不能靠加大資料修掉:結構上需要一個獨立 pose evaluation 流程,或讓 camera head 也在 photometric loss 下被微調,否則 pose 只能是 rendering 的副產品而非可驗證的輸出。

**靜/動二分法把所有複雜度留給 mask。** Eq 2 中 $G^t_s = G^t \odot (1 - M^t_d)$、$G^t_d = G^t \odot M^t_d$ 強制每個 Gaussian 二選一,所以非剛性運動(行人四肢、行車過程中飄揚的衣物與旗幟)、純外觀變化(陰影、反光、剎車燈閃爍)、半透明動態(雨、霧、廢氣)都會在訓練分布偏向「整輛車是動的」時被錯誤歸類。Lifespan 參數 $\sigma$ 只能緩解靜態側的 appearance drift,無法表達物體內部的非剛性結構運動;這是表示空間的根本限制。

**Sparse-timestamp 插值假設下游解不開。** 動態 Gaussian 中介幀位置是 $\mu^{t_i}_d = \mu^{t_a}_d + \omega_{t_i} \cdot F(t_a, t_b)$(Eq 6),也就是相鄰兩個輸入時刻之間做線性運動;相機則以線性平移 + SLERP 旋轉。在自駕場景中,急煞、急轉、紅綠燈交替起步、行人變向都會破壞線性假設,而 diffusion refinement 是 2D image-space 模組,只能塗掉 rendering 上的徵狀,無法回填底層 3D 軌跡誤差。要根治需要替換為非線性運動解碼器或讓 motion head 直接預測中介時刻。

**編輯保真度被 mask 上限封頂。** 場景編輯靠的是 dynamic Gaussian 與 static Gaussian 的乾淨切割,但車輛的陰影、地面接觸點、車身反射、排氣 plume、輪轂動態都不被 dynamic mask 覆蓋,因此移除一輛車後路面上的陰影與輪痕仍會殘留。Mask 又是用 LiDAR box 粗略生成(Appendix A.1),box 之外的「附屬效應」永遠不會進入 dynamic 集合;這個不是參數量或訓練資料的問題,而是 mask 監督本身的解析度問題。

### 7.3 Citations Worth Tracking

- **STORM, [71], Yang et al., ICLR 2025.** 直接前身;Tab 1、Tab 2、Tab 3、Tab 5 的所有主比較都對它,理解 STORM 的 pose-conditioned 公式與 velocity-only 運動模型,才能精確判斷 DGGT 真正放鬆了哪些假設、保留了哪些。
- **VGGT, [52], Wang et al., CVPR 2025.** 共享 ViT backbone 與 frozen camera head 的來源;DGGT 未報告的 pose accuracy 上限基本上由 VGGT 在駕駛資料上的 pose 表現決定,讀完 VGGT 才能評估 DGGT pose 的可靠度天花板。
- **NoPoSplat, [74], Ye et al., ICLR 2025.** 靜態 pose-free 對照;比讀此文可隔離「pose-free 設計」與「dynamic 處理」各自的貢獻,也是 Tab 1 中除 DGGT 外唯一打勾「pose-free」的方法。
- **TaPIP3D, [78], Zhang et al., 2025.** Motion head 的預訓練來源;Tab 5 的 EPE3D 增益有多少來自 TaPIP3D 的 3D point tracking 能力、有多少來自 DGGT 的端到端微調,只有讀過原文才能拆解。
- **PVG, [5], Chen et al., 2023.** 主要的 temporally conditioned 3DGS baseline;能看清「顯式靜/動分離 + lifespan」相對於「時間作為輸入」的代表性差異,也是說明為何後者在編輯任務上吃虧的最佳對照。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] DGGT 預測的 camera pose 在 Waymo 上的 ATE / RPE 是多少?是否與 VGGT 在駕駛資料上的 pose 表現一致,或者因為下游 Gaussian loss 的回流而偏離?
- [ ] 把輸入幀數從 16 推到 32 / 64 / 完整 200 幀時,PSNR、temporal flicker、GPU memory 與 inference time 各自怎麼 scale?是否存在 Tab 3 看不到的崩潰點?
- [ ] Diffusion refinement 模組在 nuScenes / Argoverse2 上單獨 ablate 後,zero-shot 增益還剩多少?它的訓練資料(2,000 Waymo clips)是否成為跨域瓶頸?
- [ ] 若 dynamic mask 的監督訊號從 LiDAR box 換成更弱的來源(光流自監督、僅 2D detection、無監督),動態解耦與 NVS 品質會掉多少?
- [ ] 4-view reconstruction PSNR 30.54 對比 4-view NVS PSNR 27.41(Tab 3)的 3.13 dB 差距,有多少來自插值誤差、有多少來自未見視角 reconstruction 誤差?diffusion refinement 在哪一側貢獻較多?
- [ ] 對非剛性主體(行人四肢擺動、騎乘者踩踏、晃動的樹葉)以及純外觀變化(剎車燈、轉向燈、反光面),系統是把它們歸入 dynamic、static + lifespan、還是兩邊都失敗?需要分類別的 PSNR / D-RMSE 拆解。
- [ ] 在編輯後的場景中,移除車輛留下的陰影與輪痕、插入車輛的接地與光照不一致,diffusion refinement 能修補到何種程度?是否能量化「編輯一致性」?

### 8.2 Improvement Directions

1. **(高可行)補上 pose 精度評估表。** 模型已經輸出 $\Pi^t$(Eq 7),用 Waymo / nuScenes / Argoverse2 提供的 GT pose 直接算 ATE / RPE / rotation error 即可,不需要新訓練。這是目前評估缺口最大、實作成本最低、回報最高的單一改動,亦能驗證「pose-as-output」是否真的可靠。
2. **(高可行)做一次 32 / 64 / 完整 scene 的長序列壓力測試。** 既然作者宣稱 arbitrary length 且 Tab 3 看起來穩定,把曲線畫到 Waymo 場景原生長度(190 幀)上才能讓論點成立或暴露真正的飽和點;不需要修改架構。
3. **(中可行)把 dynamic head 從 binary 換成多類別。** LiDAR box 已包含類別(車 / 行人 / 騎乘者),監督是免費的;多類別 dynamic mask 可讓編輯模組區分「整體位移的剛體」與「非剛性主體」,並能讓 Eq 6 對行人改用更短時域窗或 piece-wise 模型。
4. **(中可行)以可學習 motion decoder 取代純線性插值。** 已有 $H_{motion}$ 預測 $F(t_a, t_b)$ 的 3D 軌跡,可再加一個 lightweight head 直接輸出中介時刻 $t_i$ 的位置 / 速度,而不是固定走 $\omega_{t_i} \cdot F(t_a, t_b)$;在急煞、轉彎場景的 ghosting 應顯著降低,且不增加 inference cost(motion head 已存在)。
5. **(中可行)讓 diffusion refinement 跨資料集訓練。** 現行 2,000 Waymo clips 是跨域瓶頸;改用 Waymo + nuScenes + Argoverse2 混合 + per-dataset LoRA adapter,zero-shot 表 2 的增益就更可信,並能進一步壓縮 PSNR/SSIM 與 LPIPS 的數字差距。
6. **(較低可行)鬆綁 frozen camera head,做端到端 pose 微調。** 這會破壞作者「凍結 VGGT pretrained head」的訓練穩定性,需要重設學習率與 warmup,但能消除「pose-free at inference 但訓練端隱含 calibration」的爭議,並讓 pose 質量隨 rendering loss 一起最佳化,是長期值得投入的結構性升級。
