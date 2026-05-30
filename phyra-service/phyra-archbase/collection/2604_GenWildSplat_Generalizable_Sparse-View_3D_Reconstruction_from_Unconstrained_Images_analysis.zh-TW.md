<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# GenWildSplat — Generalizable Sparse-View 3D Reconstruction from Unconstrained Images

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | GenWildSplat |
| Paper full title | Generalizable Sparse-View 3D Reconstruction from Unconstrained Images |
| arXiv ID | 2604.28193 |
| Release date | 2026-04-30 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2604.28193 |
| PDF link | https://arxiv.org/pdf/2604.28193 |
| Code link | — |
| Project page | https://genwildsplat.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|------|------|------|------|
| Vinayak Gupta | University of Maryland, College Park | https://vinayak-vg.github.io/ | first author |
| Chih-Hao Lin | University of Illinois Urbana-Champaign | https://chih-hao-lin.github.io/ | co-author |
| Shenlong Wang | University of Illinois Urbana-Champaign | https://shenlong.web.illinois.edu/ | co-author |
| Anand Bhattad | Johns Hopkins University | https://anandbhattad.github.io/ | co-author |
| Jia-Bin Huang | University of Maryland, College Park | https://jbhuang0604.github.io/ | senior/advisor |

### 1.2 Keywords

feed-forward 3D reconstruction, sparse-view, unposed images, in-the-wild, Gaussian Splatting, appearance modeling, transient occlusion, curriculum learning, novel view synthesis

### 1.3 Related Lineage

| Key | Relation | Brief |
|------|------|------|
| AnySplat | base model | Feed-forward Gaussian reconstruction backbone that GenWildSplat builds on; provides VGGT-based geometry transformer and prediction heads. |
| VGGT | base model | Transformer backbone used to extract multi-view features and pseudo-labels for depth and camera poses. |
| 3D Gaussian Splatting (3DGS) | predecessor | Foundational explicit 3D Gaussian primitives with real-time CUDA rasterization; the underlying scene representation. |
| WildGaussians | baseline | Optimization-based in-the-wild Gaussian method using uncertainty/embeddings; a key compared baseline. |
| NexusSplats | baseline | Hierarchical light decoupling with per-image and per-Gaussian transient embeddings; compared baseline. |
| Gaussian-in-the-Wild (GS-W) | baseline | CNN-conditioned appearance features with 2D occlusion masks for unconstrained photo collections; compared baseline. |
| DUSt3R / MASt3R | influence | Pose-free dense 3D estimation that motivates GenWildSplat's unposed sparse-view pipeline. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於從稀疏、未知相機姿態的網路照片(in-the-wild imagery)進行可泛化的 3D 場景重建,特別針對戶外旅遊地標等場景。輸入僅有 2–6 張影像,且伴隨光照差異(不同時間、季節、天氣)以及行人、車輛等暫態遮擋物。作者提出 GenWildSplat,一個 feed-forward 框架,結合 VGGT transformer 與多個預測頭,在單次前向傳遞中同時輸出深度、相機內外參與每像素 3D Gaussian 屬性,並透過 appearance adapter 與 light code 將 canonical Gaussian 顏色調變至目標光照。配合預訓練語意分割提供遮擋遮罩,以及合成資料的 curriculum learning 訓練策略,於 PhotoTourism 與 MegaScenes benchmark 上達到 SOTA 的即時 feed-forward 重建品質,免去傳統 per-scene 最佳化的耗時流程。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- Novel View Synthesis
- Gaussian Splatting

### 2.3 Core Architectures Used

- **VGGT transformer backbone**:24-layer transformer with alternating frame and global attention,負責從未知姿態的稀疏多視角影像萃取多視角特徵 $F_i$,提供幾何與語意資訊的統一表示。
- **AnySplat feed-forward framework**:本論文的基礎架構,提供 depth head $h_D$、camera head $h_C$、Gaussian head $h_{\mathrm{gauss}}$ 三個 DPT-based 預測頭,將 transformer 特徵解碼為 per-pixel depth、相機內外參與 canonical 3D Gaussian 屬性。
- **3D Gaussian Splatting (3DGS)**:底層的場景表示與可微分光柵化器,將每組 Gaussians $\mathcal{G}_{l_i}$ 渲染回 2D 影像 $\hat{I}_i$ 進行重建監督。
- **Light Encoder $\mathcal{E}_{\mathrm{Light}}$**:2D CNN-based 編碼器,將每張輸入影像映射為 16 維的 light code $L_i$,作為光照條件的 compact latent representation。
- **Appearance Adapter $F_{\mathrm{light}}$**:MLP,將 light code 與 canonical SH 係數 $c \in \mathbb{R}^{75}$ 結合,在 3D 空間調變每個 Gaussian 的顏色,實現 feed-forward 的外觀控制。
- **YOLOv8 Segmentation**:預訓練語意分割網路,偵測 person、car、bus、truck 等 COCO 類別的暫態物件,輸出二值遮罩 $S \in \{0,1\}^{H \times W}$ 用於 masked supervision。
- **DiffusionRenderer**:訓練資料合成工具,用於對 DL3DV 場景進行 offline unconditioned relighting,提供光照變化的合成資料。
- **SyncFix**:後處理工具,僅在最終視覺化結果時套用以提升品質,不參與 baseline 比較或量化評估。

### 2.4 Core Argument

作者識別出的根本問題是:既有 in-the-wild 3D 重建方法將「幾何」「光照」「暫態遮擋」三者糾纏在一個 per-scene 最佳化迴圈中——以隨機初始化的 appearance embedding 或可學遮擋遮罩共同最佳化幾何與外觀,使每個新場景或新光照都需要長時間的 test-time fine-tuning,且在稀疏視角下高度欠定容易崩潰;另一方面,現有 feed-forward 方法雖然快,但假設固定光照與乾淨輸入,完全沒有處理 in-the-wild 變異的能力。論文主張正確的解法必須將外觀與遮擋從幾何中**顯式解耦**,並透過**大規模預訓練先驗**取代 per-scene 最佳化:(1) 以 VGGT/AnySplat 提供的幾何 transformer 預測 canonical 3D Gaussians,使幾何與光照無關;(2) 由 light encoder 將每張影像映射為 compact light code,再由 appearance adapter (MLP) 對 canonical SH 係數進行調變,讓外觀建模成為 feed-forward 可預測的條件變換,而非 per-scene 學習的自由參數;(3) 採用外部預訓練分割網路(YOLOv8 segmentation)產生顯式遮擋遮罩,避免模型用自學遮罩「explain away」靜態結構而崩潰;(4) 由於缺乏 multi-view×multi-illumination 配對資料,作者以 curriculum learning(單場景光照變化 → 多場景 → 加入合成遮擋)逐步穩定訓練。此設計鏈使得僅以合成資料訓練的模型,即可在 3 秒內對未見真實場景完成稀疏視角、可控外觀、視角一致的重建,合理對應「解耦 + 先驗 + 顯式遮罩」這條邏輯主線。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「Generalizable Sparse-View 3D Reconstruction from Unconstrained Images」直接點出三個核心張力:**generalizable**(不需要 per-scene 訓練)、**sparse-view**(輸入觀察極少)、**unconstrained**(光照變化、瞬時遮擋)。這三個詞同時也是後續所有設計決策的判準。Abstract 用一段濃縮敘事鋪陳 motivation→method→evaluation 的弧線。

Motivation 的鋪陳採取「對照法」:現有方法(scene-specific optimization with appearance embeddings or dynamic masks)在 dense view 下可行,但在 sparse view 下會 fail;而既有 evaluation 多侷限於少數場景,generalization 也存疑。這同時為後文選擇 MegaScenes 這個更難的 benchmark 預留伏筆。

接著正式提出 GenWildSplat,定義為 **feed-forward** 的 sparse-view outdoor reconstruction framework,**no per-scene optimization**。三個關鍵組件被簡短點名:(1) 用 learned geometric priors 從 unposed images 預測 depth、camera、3D Gaussians,放在 canonical space;(2) appearance adapter 對 target lighting 進行 modulation;(3) semantic segmentation 處理 transient objects。同時宣告訓練策略是 **curriculum learning on synthetic and real data**。

最後一句 commit 到具體的評測:PhotoTourism 與 MegaScenes,訴求 SOTA feed-forward rendering quality 與 real-time inference。整段 abstract 已暗示後文每一節要交代什麼:Introduction 必須解釋三組件為何缺一不可,Method 必須說明 canonical space 如何分解為 geometry/appearance,Experiments 必須證明 generalization 而不僅是擬合單一 benchmark。

### 3.2 Introduction

(620 words)

Introduction 採用「問題三因→既有方法二缺→我們的三項應對→curriculum 必要性→evaluation 預告」的五段論結構,層層收斂到本文貢獻。

第一段先提出 **in-the-wild reconstruction** 的三個難題:跨時間/季節的光照變化、瞬時遮擋(行人、車輛)、視角稀疏。這三點同時定義了問題範圍,也暗示了三類組件的必要性。接著用對照法切割現有 landscape:NeRF 與 Gaussian Splatting 系列依賴 per-scene optimization 與 dense views;feed-forward models 雖能 real-time 但只能處理 fixed lighting。Tab. 1 與 Fig. 2 被 explicit 引用作為視覺化證據——Fig. 2 三個 panel 分別對應 overfitting、camera dependency、limited appearance adaptation,直接 motivate 後續三個技術組件。

第二段正式宣告 GenWildSplat,並做出強烈的定位 claim:**第一個將 appearance 與 occlusion modeling 整合進 feed-forward 3D reconstruction paradigm 的方法**。隨後展開架構直覺:VGGT transformer 處理 sparse unposed multi-view images→specialized heads 解碼為 depth/camera/per-pixel Gaussians→形成一個 canonical representation 將 geometry 與 illumination 解耦。這裡作者主動承認 naive design 的失敗(直接 rasterize canonical Gaussians 會導致 multi-view inconsistency),為下一步引入 appearance adapter 做鋪墊。

第三段聚焦 **appearance adapter**:用 light encoder 估計 compact light code,將 canonical Gaussian colors 轉換到 target lighting space。緊接著引入 **occlusion handling**:利用 pre-trained segmentation network 產生 explicit occlusion masks,引導 model 在 supervision 時忽略 transient regions。這裡作者誠實揭露根本困難——理想上應該用 multi-view multi-illumination 配對資料訓練,但這類資料**不存在**,因此需要新的訓練策略。

第四段交代解法:用 unordered image collections 訓練,每張圖映射到 light code,由 appearance adapter 與 canonical color 共同生成 transformed colors,經 image reconstruction 監督。直接在大規模真實資料上訓練不穩定,因此提出 **curriculum**:先在合成資料上學 appearance,最後加入合成 occlusions。這段直接為 §3.5 的三階段 curriculum 鋪好基礎。

第五段預告 evaluation:在 PhotoTourism 與更具挑戰性的 MegaScenes 上 benchmark,並重申 GenWildSplat 甚至超越依賴 test-time fine-tuning 的 scene-specific methods,demonstrating large-scale priors 的力量。最後一句把全文意義提升到 generalizable 3D reconstruction 的方向陳述,作為章節 hook。

整體 Introduction 完成了三件事:**界定問題**(三難題)、**揭示 gap**(現有兩類方法都缺一塊)、**承諾 deliverable**(三組件 + curriculum + 兩 benchmark)。每一段都精確對應後續一個 method subsection,結構非常工整。

### 3.3 Related Work / Preliminaries

(600 words)

Related Work 採取 **三層分類** 的 taxonomy 寫法:**Optimization-based NVS → Feed-forward NVS → NVS in the Wild**,每層都用「能力 vs. 缺口」的對照敘事,逐步逼近本文的 niche。

第一層 **Optimization-based NVS** 簡述 3DGS [15] 的 explicit Gaussian primitives 與 CUDA-based real-time rasterization,並指出 few-view 變體(depth/camera regularization)雖有改進,但 per-scene optimization 的根本限制仍未解除。這段相對簡短,因為主要功能是樹立「optimization-based 方法在 test-time 不夠快」這一論點。

第二層 **Feed-forward NVS** 進一步細分為 **pose-aware** 與 **pose-free** 兩支。Pose-aware 又被 sub-classify 成三類:direct 3D Gaussian predictors、transformer-based LRM decoders、latent feed-forward models,這種精細分類凸顯作者對 feed-forward 領域的全貌掌握。Pose-free 系列則從 DUSt3R/MASt3R 串到 transformer cascades 與 latent self-supervision。本段以一句 punch line 收束:這些方法在 lighting variation 與 dynamic distractors 下會 degrade——精準對齊本文要解的問題。

第三層 **NVS in the Wild** 是最關鍵的一節,因為它直接對應本文的問題定位。作者把 in-the-wild 挑戰拆成 **Varying Appearance** 與 **Occlusion Modeling** 兩個 sub-axis。Varying Appearance 列舉 per-view latent embeddings、CNN-conditioned features、hash-grid fields、hierarchical light decoupling、diffusion-based harmonization 等多條路線,並 explicit 指出這些方法多需 **10+ hours 的 test-time optimization**——量化的痛點直接 set up 本文 3-second 的對比。Occlusion Modeling 則枚舉 robust regression、uncertainty features、2D occlusion masks、transient embeddings,並指出共同弱點:slow、training-intensive、缺乏 3D priors。

最後一段是 **positioning paragraph**,用一句話 cement 本文的差異:feed-forward、處理 sparse unposed images、varying lighting and dynamics、controllable appearance、view-consistent rendering、3 seconds、no per-scene optimization。這段把前三層 taxonomy 的所有缺口一次性收束到本文的解。

緊接著的 Preliminaries(§3.1 AnySplat)切換到技術鋪墊角色,介紹本文 build upon 的 backbone:AnySplat 透過 VGGT transformer 從 unposed images 抽取 multi-view features,再經三個 heads 輸出 depth、camera poses、3D Gaussian properties;以及 voxelization 與 confidence-based merging 來壓縮表示;訓練上不依賴 ground-truth 3D,而是用 VGGT pseudo-labels 與 2D rasterization supervision。這段鋪墊使讀者進入 §3.2 後不必反覆查閱 AnySplat 原文,也預留了 GenWildSplat 將在哪些地方擴展的接點:appearance adapter 與 occlusion handling 是 AnySplat 沒有的兩塊。

### 3.4 Method (overview narrative)

(720 words)

Method 章節以 **「formulation → architecture → 三組件 → 訓練流程」** 的脈絡推進,每個 subsection 都對應 Introduction 已經 promise 過的一個技術點,讀起來像是把第二章的承諾逐項兌現。

§3.2 **Problem Formulation and Overview** 先把任務形式化:給定 unposed input images $\mathcal{I} = \{I_1, \dots, I_N\}$ 在 varying illumination 與 transient objects 下,目標是重建 3D 場景以 render novel views under different appearance conditions while handling occlusions。模型寫成 $G_l = f_\theta(I, L)$,其中每個 Gaussian 由 $(\mu, \sigma, r, s, c_L)$ 構成,$c_L \in \mathbb{R}^{75}$ 是 appearance-dependent SH coefficients。Architecture 沿用 AnySplat 的三 heads 結構:depth head、camera head、Gaussian head,並新增一個 appearance adapter $\psi_\theta$ 對 canonical colors 做 modulation。這節同時宣告 curriculum training 將被用來逐步 refine geometry、appearance、occlusion——把後續三個 subsection 的順序合理化。

§3.3 **Appearance Modelling: Appearance Adapter** 對比現有 WildGaussians 與 NexusSplats 的 randomly initialized embeddings 必須在 test time 重新優化的弱點,提出 single forward pass 預測所有 scene parameters。具體上,2D CNN-based encoder $\mathcal{E}_{Light}$ 從每張 view 抽出 light code $\mathbf{L}_i$,MLP $F_{light}$ 把它與 canonical Gaussian colors $\mathcal{G}_c$ 結合產生 transformed colors $\mathcal{G}_{l_i}$,再各自獨立 rasterize 重建對應 input view,實現 self-supervised training without test-time optimization。這個設計直接對應 Introduction 提出的「ill-posed without paired multi-illumination data」問題。

§3.4 **Occlusion Modelling** 對比既有 visibility maps 與 uncertainty estimates 在 unsupervised training 下會 collapse(把困難區域權重壓低,連帶誤殺 sparse-view 中的靜態結構如樹木)。作者改用 pre-trained semantic segmentation network 偵測 person、car、bus、truck 等 transient classes,產生 binary mask $S$,以 $M = 1 - S$ 直接對 image domain 做 visibility weighting,loss 寫成 MSE 加 perceptual term 在 masked image 上。這個外部 prior 防止 model 自我合理化 transient content,穩定 dynamic regions 的梯度。

§3.5 **Curriculum Learning** 解釋為何不能直接 end-to-end 訓練:聯合學 geometry/lighting/occlusion 太不穩定;但只用 curated dataset 又學不到 in-the-wild prior。三階段策略因此被引入:**Stage 1** 在單一合成場景上學 illumination variation(無 transients)以 isolate appearance decomposition;**Stage 2** 加入 multi-scene 拓寬 geometry/appearance prior;**Stage 3** 加入 synthetic occluders 與 ground-truth masks,訓練模型同時預測 occlusion masks。Fig. 4 視覺化這三階段。

§3.6 **Training Framework** 收束整個訓練流程:每張 image 由 network 預測 geometry,light encoder 產生 compact light code,appearance adapter 在此 code 與 canonical color 上 condition 產生 transformed colors,rasterize 後與原圖比對。雖然訓練時不被要求 render novel views or lighting,模型仍能 generalize,並具備跨場景轉移 illumination 的能力(Fig. 8)——這個現象成為後續 §4.6 cross-scene appearance transfer 實驗的起點,並對既有 in-the-wild 方法形成 capability gap。

整章敘事節奏由「formulation → 兩個 modeling subsections → training strategy → end-to-end pipeline 收束」構成,每一節都同時做兩件事:**揭露既有方法缺陷** 與 **解釋本文 design 為何能解決**,讓讀者讀完後對 method 有 motivated 的理解,而非只是 description。

### 3.5 Experiments (overview narrative)

(640 words)

Experiments 章節按 **「實作細節 → 資料 → baselines → 兩個 benchmark 比較 → 跨場景能力 → ablation」** 的順序推進,結構上把「能力上界」與「組件貢獻」分開驗證。

§4.1 **Implementation Details** 先把架構規格落地:24-layer transformer with alternating frame and global attention;DPT-based 三 heads;light encoder 產 16-D 向量,經 MLP 擴展為 75-D 並 modulate per-Gaussian SH coefficients;YOLOv8 Segmentation 偵測 COCO transient categories。訓練從 AnySplat pre-trained weights 起步,perceptual loss weight $\lambda = 0.05$,curriculum 三階段共 40K iterations(10K/10K/20K),於單張 RTX A6000 上 2 days 完成。值得注意的是作者明確區分 **SyncFix** 只用於 visualization、不參與 baseline 對比——這個 disclosure 增加了 quantitative comparison 的可信度。

§4.2 **Datasets** 揭示訓練資料策略:從 DL3DV 取 700+ outdoor scenes,以 DiffusionRenderer 進行 offline unconditioned relighting(每場景 30 分鐘)製造 illumination diversity,並在 on-the-fly 階段以 COCO segments 在隨機位置 composite transient occluders。Evaluation 端用 PhotoTourism(6 input views, 3 scenes)與 20 個 MegaScenes(挑選 fewer than 20 registered images 的場景)。後者刻意避免 artificial subsampling,改採「天生 sparse」的場景,作者把這定位為 future-proof 的 sparse-view benchmark。

§4.3 **Baselines** 處理 fair comparison 的設計問題。GS-W、WildGaussians、NexusSplats 是 in-the-wild optimization baselines;SparseGS-W 與 MS-GS 因無公開實作而排除。為了與 feed-forward 方法對齊,作者構造三個 AnySplat 變體:vanilla AnySplat、StyleTransfer-AnySplat(用 CCPL)、DiffusionRenderer+AnySplat(用 DiffusionLight-Turbo 的 environment maps)。所有 baselines 用 Stable Diffusion 做 mask-based inpainting 處理遮擋。

§4.4 與 §4.5 進行兩個 benchmark 的比較。**PhotoTourism** 上 GenWildSplat 即便不做 scene-specific training,仍超越 optimization-based 方法,作者把功勞歸於 appearance adapter 透過 curriculum 學到的 prior,並把 inference time 壓在 3 秒。**MegaScenes** 上的對比更具殺傷力:既有方法在無 learned priors 下出現 noisy ground、novel view distortion、blurred skies 等典型 failure;GenWildSplat 則維持 clean、consistent renderings。對 feed-forward baselines 的對比則指出 2D style transfer 與 DiffusionRenderer 都因 per-image 處理而 multi-view inconsistent,只有在 3D 中 modulate appearance 才能達到 view-consistent photorealism。

§4.6 **Cross-scene appearance transfer** 是一個能力展示而非數值比較:GenWildSplat 把 appearance 從 geometry 拆開,可用 Bank of England 的光照風格套到 National Diet Building 上,而 prior in-the-wild methods 因為 jointly optimize 兩者所以無法做到。這個實驗回收了 §3.6 結尾預告的 capability。

§4.7 **Ablation Study & Analysis** 系統地拆解三個組件:移除 appearance adapter 導致 fixed single appearance、移除 occlusion handling 導致 transient objects 殘留、移除 curriculum 導致 color collapse。Tab. 4 的數值與 Fig. 9 的視覺化共同證明三組件缺一不可,而 full model 才得到 best PSNR/SSIM/LPIPS。整章把 quantitative comparison、qualitative comparison、capability demonstration、ablation 四種證據型態都覆蓋齊全。

### 3.6 Conclusion / Limitations / Future Work

(280 words)

§5 **Discussions** 將整篇文章收束為兩個段落:**Limitations** 在前、**Conclusion** 在後,這個倒序安排讓讀者最後一眼留在貢獻而非缺陷上,但同時也誠實揭露邊界,有助於讀者判斷適用範圍。

**Limitations** 列出四項並對應 Fig. 10 四個 panel。第一,sparse viewpoints 自然會留下 unseen regions,輸入沒覆蓋的區域會出現 incomplete geometry,這是 sparse-view 設定的本質限制而非方法缺陷。第二,當 test view 落在 training distribution 之外較遠處,model 可能產生 artifacts 或 double-layered geometry,反映了 viewpoint generalization 的邊界。第三,**indoor scenes** 仍是難題:當 occlusion mask 無法精確捕捉物件或 depth discontinuities 時,mask 會反過來 degrade reconstruction quality——這個 limitation 同時暴露了「依賴外部 segmentation prior」的雙刃性,既穩定訓練、也帶來新的失效模式。第四,方法不模擬 cast shadows 也不支援 realistic relighting,因此不適合需要 physically consistent illumination 的應用。這四項自然指向四條 future work:更強的 unseen-region completion、better viewpoint generalization、indoor-aware occlusion handling、physically-based relighting 模組。

**Conclusion** 用一個段落 reaffirm 三項貢獻:GenWildSplat 是 generalizable feed-forward Gaussian-splatting framework,能在 3 秒內從 sparse、unconstrained 內景照片重建 3D 場景;成功的關鍵是 **appearance adapter** 在 3D 中直接 modulate Gaussian colors,以及 **robust occlusion handling**;最終達成 view-consistent、photorealistic renderings。最後一句把貢獻提升到 vision 層次:朝向 real-time、controllable、relightable 3D scenes from sparse internet imagery。**Acknowledgements** 列出提供回饋的合作者。整體 Discussions 完成「邊界誠實聲明 + 貢獻最終定位」的雙重收束。

## 4. Critical Profile

### 4.1 Highlights

- 在 MegaScenes 6-view 設定下,GenWildSplat 取得 PSNR 15.84,顯著超越最強 optimization baseline NexusSplats 的 13.92(+1.92),並將推論時間從 2.4 小時壓到 3 秒(Tab. 2)。
- 同樣在 MegaScenes 3-view 設定下,PSNR 達 14.43,優於 NexusSplats 的 13.17(+1.26),呈現出此設計在更稀疏觀測時仍維持優勢(Tab. 2)。
- 將 appearance modelling 從 per-scene optimisable embedding 重新設計為 feed-forward 條件變換:light encoder 產生 16-dim light code,再由 MLP 對 canonical SH coefficients $c \in \mathbb{R}^{75}$ 進行調變(Eq. 3, Eq. 4,§3.3)。
- 改用外部 YOLOv8 segmentation 產生顯式 transient mask $M = 1 - S$,避免如 WildGaussians/RobustNeRF 等用學習式 visibility 在稀疏視角下 explain away 靜態結構(§3.4, Fig. 2)。
- 三階段 curriculum learning(單場景照明 → 多場景 → 加入合成遮擋)的必要性由 ablation 強烈支持:移除後 PSNR 由 15.84 崩跌至 11.72(Tab. 4)。
- Appearance adapter 的 ablation 使 PSNR 從 15.84 降至 13.76,確認外觀調變並非可有可無的裝飾(Tab. 4)。
- 模型完全不在真實 in-the-wild 配對資料上訓練:訓練資料僅含 DL3DV 700 個戶外場景,加上 DiffusionRenderer 離線重照明與 COCO 物件合成遮擋(§4.2, §A.1),仍能 zero-shot 遷移到 PhotoTourism 與 MegaScenes。
- 提出 cross-scene appearance transfer:可以把 Bank of England 的光照套到 National Diet Building,既有 jointly-optimised 方法因外觀與幾何耦合而無法做到此事(Fig. 8)。
- 自行 curate 一個 20 個自然稀疏(每個 scene <20 registered images)的 MegaScenes benchmark,而非像 MS-GS/SparseGS-W 從密集 PhotoTourism 人工抽稀,讓稀疏視角的評測更接近實際拍攝情境(§4.2, §A.2)。
- 模組化設計:appearance adapter 與 occlusion handling 兩個元件原則上可外掛到 MVSplat、PixelSplat 等其他 pose-aware feed-forward backbone(§4.3)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 稀疏觀測無可避免會留下未觀察區域,造成幾何缺口(§5,Fig. 10a)。
- 當 test view 遠離 training distribution 時會出現 artifacts 與 double-layered geometry(§5,Fig. 10b)。
- 室內場景下,當 occlusion mask 無法正確分離物件或深度不連續時,品質會明顯退化(§5,Fig. 10c)。
- 不建模 cast shadow,也不支援物理一致的 relighting,使其無法應用於需要正確光影模擬的任務(§5,Fig. 10d)。

#### 4.2.2 Phyra-inferred

- 評測規模極小:PhotoTourism 僅 3 個場景、MegaScenes 僅 20 個場景(§4.2);在這個 n 級距下,少數 outlier 場景就足以左右 Tab. 2/3 的平均 PSNR/SSIM/LPIPS,使得 +1.92 PSNR 的優勢統計顯著性無從評估。
- 絕對重建品質仍偏弱:即使是「贏家」配置的 PSNR 也只在 14–16 區間(Tab. 2/3),遠低於常規 NVS 文獻的 25+;讀者容易把「在很差中相對較好」誤讀為「夠好」,尤其當 paper 同時主打 photorealistic claim。
- SyncFix [19] 後處理被套用於所有 figures 與 project page videos「showing only our method」(§4.1);雖然作者聲稱排除於量化表,此非對稱處理使所有 qualitative comparison(Fig. 1, 5, 6, 7, 8, 9)系統性偏向 GenWildSplat,讀者無從還原未經修飾的真實輸出。
- 沒有與最直接的競爭者 SparseGS-W [20] 與 MS-GS [18] 做量化比較,理由是「lack public implementations」(§4.3);但這兩篇恰好是「sparse-view + in-the-wild + Gaussian」交集中除本文外最相關的工作,缺席使「first」與「SOTA」的宣稱僅在 optimization-based 與 vanilla feed-forward 兩端被驗證。
- Light code 為 16 維、由 bottleneck 經 spatial averaging 取得的 global 向量(§B.2);此 capacity 結構性地只能表達 low-frequency global lighting,難以容納 dappled shadow、partial-shade boundary 等高頻空間光照,這也合理解釋為何 cast shadow 無法被建模。
- 「view-consistent」是 Tab. 1/3 的 ✓/✗ 註記,但全文沒有任何 multi-view consistency 的量化指標(例如 reprojection error 或 temporal warp loss);判斷只能依賴 Fig. 6/7 的 cherry-picked 視覺比較。
- 訓練的「relit ground truth」實際上來自 DiffusionRenderer [21] 的 pseudo-relighting(§A.1);因此 appearance adapter 在數學上是在蒸餾 DiffusionRenderer 的 lighting prior,模型外觀空間的上界等於 DiffusionRenderer 的覆蓋範圍,這是論文未討論的隱性依賴。
- Transient detection 寫死於 YOLOv8x.seg 的 25 個 COCO 類別(§B.3);旅遊地標常見的鷹架、市集攤位、施工機具、宗教擺設等不在清單上,將被當作靜態幾何 bake-in,但合成評測中此類 distribution shift 並不會出現。

### 4.3 Phyra's Judgment (summary)

真正新的部分是把 in-the-wild appearance modelling 重新表述為「對 canonical SH coefficients 的 feed-forward 條件變換」,搭配外掛而非自學的 transient mask:這個 reformulation 是巧妙的工程決策,而非方法論突破,卻足以解掉「per-scene optimisation 才能處理光照」這個長年瓶頸。其餘元件(VGGT backbone、AnySplat heads、DiffusionRenderer 重照明、YOLOv8 分割、curriculum learning)皆為現成積木,本文最佳定位是一篇細緻整合論文。最關鍵的未解問題是:PSNR 15 級別究竟是有用的工作點,還是只是「在難題中相對最好」?以及純合成訓練是否能延伸到實驗中刻意迴避的極端條件(夜景、雨霧、強逆光)?

## 5. Methodology Deep Dive

### 5.1 Method Overview

GenWildSplat 將 in-the-wild 稀疏視角重建問題分解為三個解耦子問題:幾何預測、光照建模、暫態遮擋處理,並以**大規模預訓練先驗**取代 per-scene 最佳化。給定 $V \in [2, 6]$ 張未知姿態的稀疏輸入影像 $\{I_i\}_{i=1}^V$,模型在單次 feed-forward pass 中同時輸出每像素深度 $D_i$、相機內外參 $(K_i, E_i)$,以及 per-pixel Gaussian 屬性 $(\boldsymbol{s}, \boldsymbol{r}, \boldsymbol{\sigma}, \boldsymbol{c})$,並反投影產生 canonical 3D Gaussians $\mathcal{G}_c$。canonical 表示僅編碼幾何與本徵外觀,與光照解耦。

第二階段透過 light encoder $\mathcal{E}_{Light}$ 從每張輸入影像萃取 16 維 light code $\mathbf{L}_i$,代表該影像的全域低頻光照特徵。Appearance Adapter $F_{light}$(5 層 MLP)以 $\mathbf{L}_i$ 為條件,將 canonical Gaussian 的 SH 顏色係數 $\boldsymbol{c} \in \mathbb{R}^{75}$ 調變為對應目標光照的 $\boldsymbol{c}_{L_i}$,使每個視角擁有對應的光照轉換版 Gaussians $\mathcal{G}_{l_i}$。每組 $\mathcal{G}_{l_i}$ 經 differentiable rasterizer 渲染回對應視角產生 $\hat{I}_i$,與原 GT 影像構成自監督訓練訊號。

最後,YOLOv8x segmentation 網路產生暫態遮擋 binary mask $S_i$,經由 visibility weight $M_i = 1 - S_i$ 對 GT 與 rendering 逐元素相乘,使重建損失只計算靜態區域。整體訓練透過三階段 curriculum learning(單場景光照變化 → 多場景泛化 → 加入合成遮擋)穩定收斂,僅以合成資料訓練即可泛化至真實 PhotoTourism 與 MegaScenes 場景,3 秒內完成稀疏視角的可控外觀重建。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: Sparse unposed images {I_i}_{i=1}^V              [V, 3, H, W]
   │
   ├─→ [V, 3, H, W] ──→ Geometry Transformer φ_θ (24-layer VGGT,
   │                       alternating frame & global attention)
   │                       │
   │                       ↓ Multi-view features F = [V, T, D]
   │                       │       (T tokens, D channels; ?, ?)
   │                       │
   │                       ├──→ Depth Head h_D (DPT)
   │                       │       ↓ D = [V, 1, H, W]
   │                       │
   │                       ├──→ Camera Head h_C (DPT + MLP, pooled feats)
   │                       │       ↓ K = [V, 3, 3], E = [V, 4, 4]
   │                       │
   │                       └──→ Gaussian Head h_gauss (DPT)
   │                               ↓ per-pixel attributes:
   │                                 s = [V, H, W, 3]   scale
   │                                 r = [V, H, W, 4]   rotation (quat)
   │                                 σ = [V, H, W, 1]   opacity
   │                                 c = [V, H, W, 75]  canonical SH
   │
   ├─→ [V, 3, 256, 256] ──→ Light Encoder E_Light
   │                          (U-Net encoder, 6 levels,
   │                           channels=[32,64,128,128,256,512],
   │                           bottleneck MLP + spatial avg.)
   │                          ↓ L_i = [V, 16]
   │
   │  Unproject: μ = E_i^{-1} K_i^{-1} D_i(u,v)·[u,v,1]^T
   │             ↓
   ▼  Canonical 3D Gaussians G_c = {μ, σ, r, s, c}
                                    [N, 86] per-Gaussian
                                    (N = V·H·W, ≤ after voxel merge)
   │
   │  ┌── L_i = [V, 16] ──┐
   │  │                    │
   ▼  ▼                    │
Appearance Adapter F_light (5-layer MLP)
   Input  = concat(c, L_i) = [V, N, 91]   (75 + 16)
   Output = c_{L_i}        = [V, N, 75]
   │
   ▼ Light-transformed Gaussians
     G_{l_i} = {μ, σ, r, s, c_{L_i}}        [V, N, 86]
     (geometry shared; color replaced per-view)
   │
   ▼ Differentiable Rasterizer R(G_{l_i}, K_i, E_i)
   │                                       ↓
   │                                   Î_i = [V, 3, H, W]
   │                                       │
   │  YOLOv8x.seg(I_i) ─→ S_i = [V, 1, H, W]
   │                       │
   │                       ▼ M_i = 1 − S_i
   │
   ▼  I_m = I_i ⊙ M_i,   Î_m = Î_i ⊙ M_i
        L = MSE(I_m, Î_m) + λ · Percep(I_m, Î_m)    (λ = 0.05)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Geometry Transformer (VGGT Backbone)

**Function:** 從多視角 unposed 影像中萃取共享的 multi-view 幾何與語意特徵,作為三個下游預測頭的共用 representation。

**Input:**
- Name: $\{I_i\}_{i=1}^V$
- Shape: `[V, 3, H, W]`
- Source: 原始稀疏輸入影像

**Output:**
- Name: $\boldsymbol{F}$
- Shape: `[V, T, D]`(T 為每視角 token 數,D 為 channel 數;the paper does not specify exact T, D values
- Consumer: Depth Head $h_D$、Camera Head $h_C$、Gaussian Head $h_{gauss}$

**Processing:**

採用 24 層 transformer 架構,以 alternating **frame attention** 與 **global attention** 交替處理。Frame attention 在單一影像 token 內進行 self-attention 以捕捉 intra-view 幾何結構;global attention 跨所有 $V$ 個視角的 token 進行 attention 以建立 cross-view 對應與 multi-view consistency。輸出特徵 $\boldsymbol{F} = \phi_\theta(\mathcal{I})$ 同時編碼語意與幾何資訊,使下游 head 共享一致的場景表示。

**Key Formulas:**

$$
\boldsymbol{F} = \phi_\theta(\mathcal{I})
$$

**Implementation Details:**

- 24-layer transformer,alternating frame / global attention
- 從 AnySplat 預訓練權重初始化(本身建立於 VGGT 之上)
- 使用 VGGT 預訓練模型產生 depth 與 camera pose 的 pseudo-labels;不使用 GT 3D 資料
- T、D 兩個維度論文未明示,因此標記為 `?`

#### 5.3.2 Prediction Heads (Depth / Camera / Gaussian)

**Function:** 將共享的 backbone 特徵分解為三組互補的場景參數:per-pixel depth、global camera pose、per-pixel Gaussian attributes。三者統一採用 DPT-based 架構。

**Input:**
- Name: $\boldsymbol{F}$
- Shape: `[V, T, D]`
- Source: Geometry transformer

**Output:**
- Depth $\boldsymbol{D}$: `[V, 1, H, W]`
- Intrinsics $\boldsymbol{K}$: `[V, 3, 3]`
- Extrinsics $\boldsymbol{E}$: `[V, 4, 4]`
- Per-pixel Gaussian: scale $\boldsymbol{s}$ `[V, H, W, 3]`、rotation $\boldsymbol{r}$ `[V, H, W, 4]`、opacity $\boldsymbol{\sigma}$ `[V, H, W, 1]`、canonical SH $\boldsymbol{c}$ `[V, H, W, 75]`
- Consumer: Unprojection module

**Processing:**

三個 head 共用 DPT 主幹,透過 multi-scale feature fusion 預測:
- $h_D$:卷積融合產生 dense depth map。
- $h_C$:對 high-level features 做 spatial pooling,接 MLP 輸出 global pose 與 intrinsics(compact latent representation)。
- $h_{gauss}$:輸出 per-Gaussian 的 anisotropic covariance(scale + rotation)、opacity 與 75 維 canonical SH 顏色係數。

**Key Formulas:**

$$
\boldsymbol{D} = h_D(\boldsymbol{F}), \quad (\boldsymbol{K}, \boldsymbol{E}) = h_C(\boldsymbol{F}), \quad (\boldsymbol{s}, \boldsymbol{r}, \boldsymbol{\sigma}, \boldsymbol{c}) = h_{\mathrm{gauss}}(\boldsymbol{F})
$$

**Implementation Details:**

- DPT-based dense prediction backbone
- $\boldsymbol{c} \in \mathbb{R}^{75}$ 對應 SH 階數 4($25 \times 3 = 75$ channel),屬於 appearance-independent canonical 表示
- Camera head 透過 pooled features + MLP 輸出 compact 參數,而非 dense per-pixel

#### 5.3.3 Unprojection to Canonical 3D Gaussians

**Function:** 結合 depth 與 camera 將每像素 Gaussian 反投影到世界座標,綁定 $h_{gauss}$ 預測屬性,形成 canonical 3D 表示 $\mathcal{G}_c$。

**Input:**
- $\boldsymbol{D}$, $\boldsymbol{K}$, $\boldsymbol{E}$, $(\boldsymbol{s}, \boldsymbol{r}, \boldsymbol{\sigma}, \boldsymbol{c})$
- Shape: 如 §5.3.2 輸出
- Source: 三個預測頭

**Output:**
- Name: $\mathcal{G}_c$
- Shape: `[N, 86]`,每個 Gaussian 為 $\{\boldsymbol{\mu} \in \mathbb{R}^3, \boldsymbol{\sigma} \in \mathbb{R}^+, \boldsymbol{r} \in \mathbb{R}^4, \boldsymbol{s} \in \mathbb{R}^3, \boldsymbol{c} \in \mathbb{R}^{75}\}$;原始 $N = V \cdot H \cdot W$,經 voxel 合併後 $N$ 較小
- Consumer: Appearance Adapter

**Processing:**

每像素 $(u, v)$ 透過 $\boldsymbol{\mu} = E_i^{-1} K_i^{-1} D_i(u,v) [u, v, 1]^\top$ 反投影到世界座標。Appearance-independent 屬性 $(s, r, \sigma)$ 與 canonical SH $c$ 直接綁定到對應 3D 點。延用 AnySplat 的 voxelization + confidence-based merging 機制,於每個 voxel 內合併重疊 Gaussian 以形成 compact 表示。

**Key Formulas:**

$$
g_l = \{\boldsymbol{\mu}, \boldsymbol{\sigma}, \boldsymbol{r}, \boldsymbol{s}, \boldsymbol{c}_L\}
$$

**Implementation Details:**

- 繼承自 AnySplat 的 voxelize-then-merge 流程
- Canonical 表示與目標光照解耦,$c$ 不隨視角改變
- $N$ 的確切數值依 voxel resolution 而定,論文未明示

#### 5.3.4 Light Encoder

**Function:** 將每張輸入影像壓縮為代表全域低頻光照的緊緻 latent 向量,作為後續 appearance modulation 的條件輸入。

**Input:**
- Name: $I^{(i)}$
- Shape: `[V, 3, 256, 256]`
- Source: 原輸入影像 resize 至 $256 \times 256$

**Output:**
- Name: $\mathbf{L}_i$
- Shape: `[V, 16]`
- Consumer: Appearance Adapter

**Processing:**

採用 U-Net encoder-only 架構,六層 residual conv blocks,每 block 含 2 個 conv + group normalization + 非線性激活。Block counts $[1, 2, 2, 4, 4, 4]$,latent channel widths $[32, 64, 128, 128, 256, 512]$,輸入 $256 \times 256$ 每層 halving。Bottleneck 後透過 multiple MLP layers + spatial averaging 產生 16 維 extrinsic lighting 向量。不使用 intrinsic features。

**Key Formulas:**

$$
\mathbf{L}_i = \mathcal{E}_{Light}(I^{(i)}), \quad i = 1, \dots, V
$$

**Implementation Details:**

- Encoder-only U-Net,參考 Latent Intrinsics [56]
- 16 維向量設計目的為捕捉 low-frequency global lighting
- 不需 GT 光照標註,完全 self-supervised via image reconstruction loss

#### 5.3.5 Appearance Adapter

**Function:** 以 light code 為條件,將 canonical SH 顏色係數調變為目標光照下的 SH 係數,實現 feed-forward 可預測的 appearance transformation,取代 baseline 中的 per-scene embedding optimization。

**Input:**
- Concatenated vector: $[\boldsymbol{c}; \mathbf{L}_i]$
- Shape: `[V, N, 91]`($75 + 16$)
- Source: canonical Gaussians 與 Light Encoder

**Output:**
- Name: $\boldsymbol{c}_{L_i}$
- Shape: `[V, N, 75]`
- Consumer: Differentiable Rasterizer

**Processing:**

5 層 MLP $\psi_\theta$ 將 16 維 light code 與 75 維 per-Gaussian conditioning vector concat 後映射回 75 維 SH 空間。對每個視角 $i$ 與每個 canonical Gaussian 進行此轉換,得到 view-specific 的 light-transformed Gaussians $\mathcal{G}_{l_i} = [\tilde{c}_{i,1}, \dots, \tilde{c}_{i,N}]^\top$。其餘屬性 $(\mu, \sigma, r, s)$ 跨 view 共享。

**Key Formulas:**

$$
\boldsymbol{c}_{L_i} = \psi_\theta(\boldsymbol{c}, \mathbf{L}_i)
$$

$$
\mathcal{G}_{l_i} = F_{\text{light}}(\mathcal{G}_c, \mathbf{L}_i), \quad i = 1, \dots, V
$$

**Implementation Details:**

- 5-layer MLP,輸入 $91$ 維,輸出 $75$ 維
- 與 WildGaussians、NexusSplats 不同:本方法**不**在 test time 對 embedding 做 per-image 最佳化,而是直接透過 learned mapping 預測,使 inference 維持 feed-forward(3 秒)
- 同一 $\mathcal{G}_c$ 加上不同 $\mathbf{L}_i$ 即可產生不同光照下的渲染,支援 cross-scene appearance transfer

#### 5.3.6 Differentiable Rasterizer & Masked Supervision

**Function:** 將 light-transformed 3D Gaussians 渲染回 2D 影像,並以 pretrained segmentation 提供顯式遮擋遮罩,使 reconstruction loss 只在靜態區域監督,避免模型透過自學 visibility 「explain away」靜態結構。

**Input:**
- Rasterizer:$\mathcal{G}_{l_i}$, $K_i$, $E_i$
- Segmentation:$I_i$,shape `[V, 3, H, W]`

**Output:**
- Renderings $\hat{I}_i$,shape `[V, 3, H, W]`
- Occlusion mask $S_i \in \{0, 1\}^{H \times W}$
- Visibility $M_i = 1 - S_i$
- Consumer: 訓練 loss

**Processing:**

每組 $\mathcal{G}_{l_i}$ 獨立經 standard 3DGS CUDA rasterizer 渲染,如 Eq. (2):$\hat{I}_j = \mathcal{R}(\mathcal{G}_l, K_j, E_j)$。並行地,YOLOv8x.seg 偵測 COCO 中常見的暫態類別並合併為 binary mask $S(p) = 1$ 表示 transient pixel。Visibility weight $M = 1 - S$ 對 GT 影像與 rendering 逐元素相乘:$I_{\text{m}} = I \odot M$、$\hat{I}_{\text{m}} = \hat{I} \odot M$。最終 loss 結合 MSE 與 perceptual:

**Key Formulas:**

$$
\hat{I}_j = \mathcal{R}(\boldsymbol{\mathcal{G}}_l, \boldsymbol{K}_j, \boldsymbol{E}_j)
$$

$$
\mathcal{L} = \mathrm{MSE}(I_{\text{m}}, \hat{I}_{\text{m}}) + \lambda \cdot \mathrm{Percep}(I_{\text{m}}, \hat{I}_{\text{m}})
$$

**Implementation Details:**

- Segmentation 使用 YOLOv8x.seg(COCO 預訓練)
- Transient 類別:person, bicycle, car, motorcycle, bus, train, truck, boat, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, suitcase, chair, keyboard, book
- Perceptual loss 權重 $\lambda = 0.05$
- 外部 segmentation prior 防止模型崩潰式地把靜態結構標記為暫態

#### 5.3.7 Curriculum Learning Strategy

**Function:** 透過三階段漸進式訓練拆解「光照解耦」「跨場景泛化」「遮擋處理」三項任務,避免 ill-posed 條件下 end-to-end 訓練導致 Gaussian 顏色崩潰(消融實驗 Tab. 4 中,without curriculum 的 PSNR 從 15.84 降至 11.72)。

**Input:**
- Stage 1:單一合成場景 + DiffusionRenderer 產生的多種光照變化(無 transients)
- Stage 2:+ DL3DV 700+ 戶外場景(多 scene 光照配對)
- Stage 3:+ COCO 合成遮擋物(2–10 個 segments,影像下半部隨機放置,GT mask 可用)

**Output:** 收斂後可泛化至真實 in-the-wild 場景的全參數模型

**Processing:**

Stage 1(Lighting):於單一合成場景在無遮擋與固定幾何條件下,專注學習 light code 與 appearance adapter 對 SH 的調變,避免幾何或遮擋干擾外觀分解。

Stage 2(Multi-scene):導入多場景以建立跨環境的 geometry + appearance 先驗,讓 backbone 與 head 適應 scene diversity。

Stage 3(Occlusion):加入合成遮擋物並使用 GT mask 監督,使模型同時學會在 transient 條件下穩定預測,並可泛化至真實 occlusions。

**Implementation Details:**

- 訓練迭代數:Stage 1 = 10K、Stage 2 = 10K、Stage 3 = 20K,合計 40K
- 硬體:單張 RTX A6000,共 2 天
- 初始化:AnySplat 預訓練權重
- 後處理:可選 SyncFix [19],僅用於可視化,不參與定量比較
- 訓練資料完全為合成,僅在 evaluation 時面對真實 PhotoTourism 與 MegaScenes 場景

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| PhotoTourism | Sparse-view 3D reconstruction / NVS under varying illumination | the paper does not specify | test (evaluation benchmark) |
| MegaScenes | Sparse-view outdoor 3D reconstruction with transient occlusions | the paper does not specify | train + test (evaluation benchmark) |

備註:摘要僅列出 PhotoTourism 與 MegaScenes 作為評測 benchmark,並提到使用 "synthetic and real data" 配合 curriculum learning 訓練,但提供的頁面未揭露 synthetic 資料來源、scene/影像數量或 train/val/test 切分細節,故以 "the paper does not specify" 標註規模。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| the paper does not specify | 提供的頁面僅宣稱 "state-of-the-art feed-forward rendering quality",未列出具體指標(例如 PSNR / SSIM / LPIPS) | the paper does not specify |

備註:NVS 任務慣例上會使用 PSNR、SSIM、LPIPS,但本次提供的 experiments + appendix 頁面並未明確列出評測指標,因此不在此處臆測。

### 6.3 Training and Inference Settings

- **Hardware**: the paper does not specify。
- **Batch size**: the paper does not specify。
- **Optimizer**: the paper does not specify。
- **Learning rate schedule**: the paper does not specify (僅提到使用 "curriculum learning on synthetic and real data")。
- **Training steps**: the paper does not specify。
- **Inference settings**: 單次 feed-forward pass,約 3 秒完成從 2–6 張 unposed 影像到 3D Gaussians 的重建,無需 per-scene optimization,可達 real-time inference (見 Figure 1 與摘要)。
- **Inputs at inference**: 2–6 張 sparse、unposed 影像;輸出包含 depth、camera parameters、canonical-space 3D Gaussians,並可在 target lighting condition 下生成 novel views。

備註:詳細訓練超參數應在 appendix,但本次提供的內容僅含第 1 頁(標題 + Figure 1 + 摘要),無法引用具體 appendix 數值。

### 6.4 Main Results

| Method | [Metric 1] | [Metric 2] | Notes |
| --- | --- | --- | --- |
| **GenWildSplat (ours)** | the paper does not specify | the paper does not specify | 摘要宣稱在 PhotoTourism 與 MegaScenes 上達到 state-of-the-art feed-forward rendering quality,且推論時間約 3 秒、無需 test-time optimization |
| Per-scene optimization baselines (appearance embeddings) | the paper does not specify | the paper does not specify | 摘要將其列為對比的既有方法類別,需要 extensive per-scene training,在 sparse views 下會失敗 |
| Per-scene optimization baselines (dynamic masks) | the paper does not specify | the paper does not specify | 同上,屬於既有 scene-specific optimization 路線 |

備註:本次提供的頁面未含 main results 表格的具體數值或具名 baseline (例如 NeRF-W、Ha-NeRF、K-Planes、pixelSplat、MVSplat 等),因此無法填入具體 metric 數字或粗體勝出列;以 "the paper does not specify" 標註空缺。

### 6.5 Ablation Studies

The paper does not specify ablation results in the provided pages. 從摘要可推斷可能的消融候選為:(a) 移除 appearance adapter (檢驗 target lighting 控制能力)、(b) 移除 semantic segmentation for transient objects (檢驗 occlusion handling)、(c) 移除 curriculum learning (檢驗 synthetic→real 階段式訓練的必要性)、(d) 改變輸入視角數 (2 vs 4 vs 6,Figure 1 已視覺化)。但由於 experiments + appendix 文本未提供,本次無法判斷各 ablation 對 metric 的具體影響,亦無法區分 diagnostic 與 sanity check。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline (a current SoTA on the chosen task) — 摘要泛指對比 "appearance embeddings" 與 "dynamic masks" 兩類 per-scene optimization 方法,但未在提供頁面中具名列出 SoTA baseline (如 NeRF-W、pixelSplat、MVSplat),具體強度待 main results 表格佐證。
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — 摘要明確提到在 PhotoTourism 與 MegaScenes 兩個 benchmark 評測,屬於 cross-dataset,但仍同屬 NVS 單一任務。
- [missing] Has ablations that diagnose the new components (not just sanity checks) — 提供頁面未呈現任何 ablation 表或敘述,無法判斷是否診斷 appearance adapter / semantic segmentation / curriculum learning。
- [partial] Has a scaling study (size, length, or compute) — Figure 1 展示 2/3/4/5/6 views 的輸入稀疏度視覺結果,屬於 input-views 的 sparsity 掃描,但未見模型大小或 compute 的 scaling 曲線。
- [partial] Has an efficiency / wall-clock comparison — 摘要與 Figure 1 標示 "3 secs" feed-forward 與 real-time inference,但未在提供頁面中與 per-scene optimization baseline 並列具體 wall-clock 數字。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 提供頁面無 seed、std 或 confidence interval 相關描述。
- [missing] Releases code / weights / data sufficient for reproducibility — 提供頁面僅含 project page URL (https://genwildsplat.github.io/),未明確承諾 release code、weights 或 training data。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 「首個將 appearance 與 occlusion modelling 整合進 feed-forward 3D reconstruction 的方法」(§1)**:在「同時做兩件事 + feed-forward + Gaussian Splatting」的交集內,實驗中沒有反例(AnySplat 不做、WildGaussians/NexusSplats 是 optimisation-based);**Supported**,但定義組合很狹窄,屬於「在四個限定條件下才為首」的 first。
- **C2: 「SOTA on PhotoTourism and MegaScenes」(Abstract, §4)**:Tab. 2 數字確實全面領先所有 reported baselines;**Supported with caveats**,因為 (a) 評測場景數小、(b) 沒有比 SparseGS-W [20] 與 MS-GS [18]、(c) PSNR 絕對值仍偏低。
- **C3: 「Cross-scene appearance transfer」(Fig. 8, §4.6)**:這是相對於 jointly-optimised 方法的真正能力差異,Fig. 8 視覺上有說服力;**Partially supported**,因為僅 qualitative,沒有定義「成功 transfer」的量化指標(色彩保真度、structural similarity 對 target lighting reference)。
- **C4: 「3 秒內 feed-forward 推論取代 per-scene optimisation」(Tab. 2)**:時間數字明確(3s vs. 2.4–8 hrs);**Supported**。
- **C5: 「純合成資料訓練 → 實場景泛化」(§3.5, §A.1)**:Fig. 5/6 與 Tab. 2 顯示對未見真實場景能 zero-shot;**Partially supported**,因為「合成資料」其實是 DL3DV 真實照片經 DiffusionRenderer 重照明後的版本,distribution gap 比論文敘述的「only synthetic」要小,且絕對品質仍弱。
- **C6: 「Curriculum learning 是穩定收斂關鍵」(§3.5)**:Tab. 4 的 PSNR 11.72 vs. 15.84 是強支持;**Supported**。

### 7.2 Fundamental Limitations of the Method

**Light code 的低頻瓶頸**。Appearance adapter 接收的是 16 維、經全局 spatial averaging 的 light code,再由一個 5 層 MLP 把它與每個 Gaussian 的 conditioning vector 映射到 75 維 SH 係數(§B.2, §B.4)。這條路徑在數學上限定了:同一張影像下,所有 Gaussian 共享同一個照明描述子,差異只能來自 canonical color 與 MLP 內部對 conditioning vector 的反應。也就是說,空間變化的硬陰影、視角依賴的高光、由場景外物件投來的 cast shadow,皆無法被表達,這不是訓練資料不足而是表示能力的結構性上界,作者在 §5 將「不支援 cast shadow」歸為 limitation,但實際上是這個設計的直接推論。

**外掛分割器的封閉類別**。Occlusion modelling 完全外包給 YOLOv8x.seg + 25 個 COCO 類別(§B.3),所以模型在訓練與推論時對「什麼是 transient」的定義是固定的。對於 COCO 之外但在旅遊地標常出現的施工鷹架、市集攤位、群眾遮陽傘、宗教旗幟等,系統會將其視為靜態幾何 bake-in。要解此問題不是 fine-tune 就能修,而需要把 occlusion 的判定改回模型內部(這正是論文刻意避開的方向,因為自學 mask 在稀疏視角下會崩),呈現一個結構性 trade-off。

**Distillation 而非真正 inverse rendering**。訓練流程的 stage 1 與 stage 2 都仰賴 DiffusionRenderer [21] 對 DL3DV 場景做 pseudo-relighting(§A.1),appearance adapter 因此在學習一個 conditional mapping,其外觀空間的上界等於 DiffusionRenderer 在 outdoor 場景上的覆蓋範圍。論文沒有給出 DiffusionRenderer 在 outdoor 上的失效模式分析,但作者自己的 Fig. 7 row 2 顯示 DiffusionRenderer 在「夜景」上輸出非寫實的 dimmed 影像,意味著 GenWildSplat 對夜景、雨霧、強逆光等情境也將繼承相同的弱點。

**Per-image lighting + per-image rasterisation 的隱性不一致**。架構上,canonical Gaussians $\mathcal{G}_c$ 是共享的,但每張 view $i$ 都用自己的 $L_i$ 經 MLP 產生獨立的 $\mathcal{G}_{l_i}$,再被獨立 rasterise(Eq. 4)。「view-consistent」並非 emerge 自一個顯式約束,而是希望 $L_i$ 與 $L_j$ 在訓練時被推到夠近。實作上沒有任何 cross-view light code 一致性 loss,也沒有 multi-view photometric consistency 約束。當 input views 的光照差異超出訓練分布時,沒有機制阻止 $L_i \neq L_j$ 各自自洽地把場景「解釋成不同的東西」。

### 7.3 Citations Worth Tracking

- **AnySplat [11]**(SIGGRAPH Asia 2025):本文的直接 base model,VGGT backbone + DPT heads + voxel merging 全部繼承自此;不讀無法判斷哪些 design choice 是 GenWildSplat 的貢獻、哪些是承襲。
- **DiffusionRenderer [21]**(CVPR 2025):整個 stage 1/2 訓練資料的 lighting variation 全由它生成,GenWildSplat 的外觀分布上界等於這個模型;讀者必須了解其失效模式才能正確判讀 GenWildSplat 的泛化邊界。
- **MS-GS [18]** 與 **SparseGS-W [20]**:本文聲稱「first」與「SOTA」但因「無公開實作」未直接比較,實則是同一細分領域(sparse + in-the-wild + Gaussian)最相關的工作;追蹤其 arXiv 可定位本文真正競爭位置。
- **VGGT [40]**(CVPR 2025):geometry transformer 與 pseudo-label 來源,decides 本文的 pose 與 depth 上限;若 VGGT 在某類場景退化,GenWildSplat 不可能更好。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] PSNR 隨 input view 數量的縮放曲線為何?Tab. 2 只回報 3 與 6 view,Fig. 1 視覺展示 2–6 但沒有對應數字;在 2 view 是否仍維持優勢、12 view 是否會被 optimisation baselines 反超,皆未知。
- [ ] 在 COCO 之外的常見旅遊地標 transient(鷹架、市集攤位、群眾遮陽傘、宗教擺設)出現時,模型是會 bake-in 為靜態幾何,還是會被 light code 吸收為照明變化?論文未做此 distribution-shift 測試。
- [ ] 「View-consistent」的量化證據為何?把同一場景由 $V$ 個 input view 重建後,任意兩 view 之間的 reprojection PSNR 或 warp loss 為多少?Tab. 1/3 只用 ✓/✗ 標記。
- [ ] 在 DiffusionRenderer 已知失效的條件(夜景、強逆光、霧雨)下,GenWildSplat 是否也同樣失效,亦或 curriculum 給予了模型某種額外韌性?Fig. 7 row 2 暗示前者但無系統性驗證。
- [ ] SyncFix-on 與 SyncFix-off 的量化 gap 究竟有多大?目前讀者看到的 Fig. 5/6/7 視覺品質,有多少來自 GenWildSplat 本身、多少來自後處理?
- [ ] 把 light code 從 16 維 global 向量換成 spatially-aware feature map,在不重訓骨幹的情況下是否能直接改善 Fig. 10d 的 cast shadow 缺失?
- [ ] 加入第四個 curriculum stage(real PhotoTourism 影像 + 不重照明)是否會讓 PSNR 從 15.84 進一步上推,還是會破壞 stage 1/2 學到的 lighting disentanglement?

### 8.2 Improvement Directions

1. **加上 multi-view consistency 量化指標(最易)**。Tab. 3 已用 ✓/✗ 暗示這是賣點,只需在現有 evaluation pipeline 中加入「重建後跨 view 的 reprojection PSNR/SSIM」即可。理由:讓 C3 與 C5 從 qualitative claim 升級為 measurable claim,也讓 4.2.2 的第六條批評自動消解。
2. **Light code 由 global 16-dim 改為 spatial 2D feature map(中等)**。保留 light encoder backbone 但取消 spatial averaging,讓 MLP 接收 per-Gaussian 在 2D feature map 上的 bilinear sample。理由:§7.2 第一條結構性瓶頸的直接修補,可望讓 cast shadow 與 partial-shade boundary 進入表示空間,且不需要更動 curriculum。
3. **改用 open-vocabulary segmentation(中等)**。把 YOLOv8/COCO 換成 Grounded-SAM 或 OpenSeeD,以文字 prompt 動態定義 transient 類別。理由:旅遊地標的 transient 分布長尾且非 COCO 子集;改完後 §7.2 第二條 trade-off 可被部分緩解,且不需要重新訓練幾何 backbone。
4. **新增 stage 4:真實 in-the-wild 影像微調(較難)**。在 stage 3 後加入 PhotoTourism 訓練 split,以 masked photometric loss 微調 appearance adapter 與 light encoder,凍結幾何 backbone。理由:§7.1 的 C5 與 §7.2 第三條都指向「真實資料 distribution gap」;若幾何凍結則不會破壞 stage 1/2 的 disentanglement。
5. **顯式建模 cast shadow(最難)**。在 canonical Gaussians 上額外預測 per-Gaussian shadow receiver mask,並讓 light code 控制方向性 shadow projection。理由:這是 §5 與 §7.2 第一條共同指出的最深層限制;但需要新的 shadow supervision(可由 DiffusionRenderer 的 buffer 或 ray-traced synthetic data 提供),屬於下一篇 paper 的份量。
