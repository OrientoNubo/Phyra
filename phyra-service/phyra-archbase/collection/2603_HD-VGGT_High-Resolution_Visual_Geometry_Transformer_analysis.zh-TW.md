<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# HD-VGGT — HD-VGGT: High-Resolution Visual Geometry Transformer

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | HD-VGGT |
| Paper full title | HD-VGGT: High-Resolution Visual Geometry Transformer |
| arXiv ID | 2603.27222 |
| Release date | 2026-04-10 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.27222 |
| PDF link | https://arxiv.org/pdf/2603.27222 |
| Code link | — |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|------|------|------|------|
| Tianrun Chen | KOKONI 3D, Moxin Technology; Zhejiang University | https://tianrun-chen.github.io/ | first author, project lead, corresponding author |
| Yuanqi Hu | KOKONI 3D, Moxin Technology | — | co-first author |
| Yidong Han | Huzhou University | — | co-first author |
| Hanjie Xu | KOKONI 3D, Moxin Technology | — | co-first author |
| Deyi Ji | University of Science and Technology of China | — | co-first author |
| Qi Zhu | University of Science and Technology of China | — | co-first author |
| Chunan Yu | Nanjing University of Science and Technology | — | co-author |
| Xin Zhang | KOKONI 3D, Moxin Technology | — | co-author |
| Cheng Chen | KOKONI 3D, Moxin Technology | — | co-author |
| Chaotao Ding | KOKONI 3D, Moxin Technology | — | co-author |
| Ying Zang | Huzhou University | — | co-author |
| Xuanfu Li | Huawei | — | co-author |
| Jin Ma | Huawei | — | co-author |
| Lanyun Zhu | Tongji University | https://lanyunzhu.site/ | corresponding author |

### 1.2 Keywords

3D reconstruction, feed-forward 3D, high-resolution, Vision Transformer, feature upsampling, feature modulation, multi-view geometry, VGGT

### 1.3 Related Lineage

| Key | Relation | Brief |
|------|------|------|
| VGGT (Visual Geometry Grounded Transformer) | base model | 直接延伸的 backbone：以全域 self-attention 從多視角影像聯合預測相機與幾何，HD-VGGT 將其包裝為粗分支。 |
| DUSt3R | predecessor | 前饋 3D 重建範式的開山之作，提出由影像對直接回歸 point map，奠定本文走向。 |
| Fast3R | influence | DUSt3R 的可擴展性後續工作，HD-VGGT 在 Related Work 中視為前饋重建演進路線之一。 |
| Spann3R | influence | 處理長視訊序列的前饋重建變體，作為 HD-VGGT 對比的同類方法之一。 |
| π3 | concurrent | VGGT 的同期變體，主要解決 reference-view bias，本文以其為高解析度方向上的對照工作。 |
| DINOv2 | base model | 用作影像 patch token 抽取的 ViT backbone，是低解析度分支的特徵來源。 |
| AnySplat / FLARE | influence | 將前饋 3D 模型橋接到 3D Gaussian Splatting 的工作，作為前饋 3D 重建版圖中的相關方法。 |

## 2. Research Overview

### 2.1 Research Topic

本文針對前饋式多視角 3D 重建在高解析度輸入下的可擴展性與穩定性問題，提出 HD-VGGT 雙分支架構。低解析度分支沿用 VGGT backbone（DINOv2 + 全域 self-attention transformer）建立全域一致的粗略幾何骨架與相機姿態；高解析度分支則透過一個受高解析影像引導的 Learned Feature Upsampling 模組，將粗特徵融合高頻細節後送入輕量 refiner transformer，避免在原始解析度上付出 token 數量平方級的算力代價。此外，作者觀察到重複紋理、弱紋理、鏡面反射等視覺歧義區域容易產生不穩定 token，於是設計 Feature Modulation 機制，以核化 Gramian 統計在 RKHS 中偵測異常 token，並在早期 transformer 層加以抑制，從而提升幾何推論的穩健性，達成高保真且可擴展的高解析度 3D 重建。

### 2.2 Domain Tags

- computer vision
- 3D reconstruction
- multi-view geometry
- deep learning

### 2.3 Core Architectures Used

- **VGGT backbone (Tcoarse)**：作為低解析度分支，承接 DINOv2 patch tokens 後以深層 global self-attention transformer 在所有視角上聯合預測粗特徵 $F^{coarse}_i$ 與初始相機參數 $g^{coarse}$，提供全域一致的幾何骨架。
- **DINOv2 ViT**：作為影像 patch token 抽取器，將每張低解析度輸入影像編碼為 $K_0$ 個 $C$ 維 patch tokens，是低解析度分支的特徵來源。
- **Learned Feature Upsampling 模組 $U$**：本文提出的引導式升頻模組，由 $\phi_{guidance}$、$\phi_{feat}$、$\phi_{fuse}$ 三條淺層 conv 子網路組成，將粗特徵以高解析影像 $I^{HR}$ 為條件升頻，補回 backbone 端遺失的高頻幾何與紋理線索。
- **High-Resolution Refiner ($T_{refine}$)**：本文提出的輕量 refiner transformer（約 6 層，遠少於 backbone 的 24 層），在升頻後的高解析特徵上以局部化 attention 強化跨視角一致性並回歸最終 $\{D^{final}, g^{final}\}$。
- **Feature Modulation 模組**：本文提出的 training-free 異常 token 偵測與抑制框架，於 RKHS 中以 kernelized Gramian 二階統計量計算 anomaly saliency map $S_{anomaly}$，再經 projection gradient flow 精修為 $M_{refined}$，最後在 shallow 層以 $K'_{p,l} = (1 - M_{refined,p}) \cdot K_{p,l}$ 進行資訊閘控式 attention 抑制。
- **DPT Head 與 Pose Head**：依 Figure 1 所示掛在 refiner 後端，分別輸出高解析度 3D point maps 與相機姿態。

### 2.4 Core Argument

作者主張，要把前饋式 3D 重建推向真正高解析度，必須同時解決兩個本質問題：第一，VGGT 類架構的全域 self-attention 在 token 數上呈平方複雜度，將解析度加倍即代表 token 量約 4 倍、注意力代價約 16 倍，這使得直接放大整個 backbone 在硬體上不可行；第二，在重複紋理、弱紋理或鏡面等視覺歧義區域，transformer 早期層會輸出統計上不穩定的特徵 token，且這些不穩定性在解析度提高時更加放大，於後續層級被傳播放大，最終腐蝕跨視角幾何一致性。基於此，作者導出一個邏輯上必然的設計：粗、細解耦。先以低解析度分支高效求出全域一致的幾何骨架與相機，再以高解析影像作為條件，透過學習式 Feature Upsampling（受 IHR 引導，注入 backbone 端遺失的高頻細節）將粗特徵升頻，並用淺層 refiner transformer 微調，從而在不重跑全解析全域注意力的前提下取得高保真輸出。對於不穩定 token，作者進一步論證它們在統計上等價於動態場景的「事件」，故借用核化 Gramian 的二階統計量在 RKHS 中量化跨視角穩定性，建立分層 Bayesian 異常顯著圖並透過投影梯度流精修遮罩，最後在資訊閘控的注意力中抑制異常 token 的影響。整套架構因此既規避了平方級複雜度，又從特徵流形層面修復幾何訊號，使得 HD-VGGT 同時具備可擴展性與在困難視覺條件下的幾何可靠性。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(185 words)

標題「HD-VGGT: High-Resolution Visual Geometry Transformer」即點明本論文的兩個主軸：以 VGGT 為基底、目標是把 feed-forward geometry transformer 推到高解析度。Abstract 採取「動機 → 障礙 → 觀察 → 解法」四段式佈局。第一句就把高解析度的價值定錨在「許多幾何細節只在細空間尺度才浮現」，建立讀者為何需要關心 resolution 的直覺。接著以 VGGT 作為 state-of-the-art 範式代表，肯定 feed-forward 的進展，再立刻轉折指出真正的 scalability 障礙：token 數量同時隨 image resolution 與 view 數量成長，造成計算與記憶體成本爆炸。這一句為後續介紹的 quadratic complexity 鋪好引線。

第二個觀察則是論文的差異化核心 — 在 repetitive patterns、weak textures、specular surfaces 等視覺模糊區域，early-layer 會產生不穩定的 feature tokens 並污染 geometric inference，且解析度越高越嚴重。這個現象觀察為後文 Feature Modulation 的存在提供了問題定義。

最後 abstract 直接提出兩件主張：dual-branch architecture（low-res 抓全域結構、high-res 透過 learned feature upsampling 細修）以及 Feature Modulation（在 transformer 早期壓抑不可靠 token），並以 SOTA 重建品質作結。Abstract 的鋪陳同時為 §3.2 Introduction 的問題化敘事與 §3.4 Method 的雙主軸技術段落埋下伏筆。

### 3.2 Introduction

(640 words)

Introduction 採取「應用價值 → 古典方法 → feed-forward 範式 → VGGT → 雙重瓶頸 → HD-VGGT 解法」六段遞進。開場將 3D reconstruction 嵌進機器人、自駕、AR、digital content 等應用脈絡，立刻給讀者一個「為什麼還要做這件事」的答案；隨即把古典 SfM/MVS pipeline 定位為「精巧但 brittle、運算昂貴」的對照組，為 deep learning 路線的合法性做鋪陳。

第二段把 feed-forward 升格為新的範式，並把 VGGT 視為 paradigm shift 的代表 — 用 global self-attention 在單一 forward pass 內聯合估計相機與 dense geometry。這段作用是在進入問題前先確認 baseline 的地位，讓後續批評不會顯得空泛。

第三、四段是論文的「scalability bottleneck」敘事核心。第三段先建立「高解析度才能恢復 thin objects、sharp edges、subtle surface variations」與「越多 view 越強的 geometric constraint」這兩個 desirable property，再在第四段刻意點出兩者結合會讓 token 數量爆炸，迫使現有 feed-forward 模型必須對 resolution 與 view count 做嚴格上限。這個 setup 把第二章的 quadratic complexity 量化推導合理化。

第五段引入第二個更微妙的問題 — visually ambiguous region 在 early transformer layers 中會產出 statistically unstable feature tokens，這些 token 跨 view 不一致並把噪聲傳到深層；解析度提高後此類區域更顯著，因此成為 high-precision reconstruction 的關鍵障礙。這段是後文 Feature Modulation 的全部存在理由。

第六、七段直接把 HD-VGGT 的兩項貢獻定型：dual-branch（low-res branch 用原本的 VGGT backbone 估計一個 globally consistent 粗糙 3D，high-res branch 透過 dedicated feature upsampling 把 coarse 3D feature 與高解析度 image feature 融合）以及 Feature Modulation（偵測不穩定 token 並衰減其在 propagation 中的影響）。第六段並明確說明選擇 dual-branch 的理由是「避免 quadratic complexity 而仍能享受 high-resolution supervision」。

第八段以「scalable + robust」收尾，宣告 HD-VGGT 讓 feed-forward model 能在更高解析度上運作的同時提升幾何可靠性，並把整個方向定位為朝 real-world large-scale 高保真重建邁進的一步。這個收尾既為 §3.3 Related Work 的差異化敘事 — 既要與 feed-forward 3D 比，也要與 high-resolution deep learning 比 — 設下對照軸，也為 §3.4 Method 的雙主軸結構（hierarchy + feature stability）給出明確的章節路標。

### 3.3 Related Work / Preliminaries

(520 words)

§2.1 Feed-Forward 3D Reconstruction 採取「DUSt3R 開山 → 家族枝繁 → 共同盲點」三步推進。先以 DUSt3R 確立「直接從 image pair regress point map」的範式起點，再列舉 Fast3R（scalability 架構優化）、Spann3R（長視訊序列）、VGGT（global attention 多視角）、π³（解 reference-view bias）、Dens3R/CUT3R（更密的幾何預測與 static/dynamic 混合訓練）、FLARE 與 AnySplat（接 3D Gaussian Splatting）等代表作，把 feed-forward 領域的版圖描繪完整。重點落在收尾一句：這些工作幾乎都針對 standard-resolution，**高解析度是被低估的 frontier**。這就把 HD-VGGT 的 niche 釘住。

§2.2 High-Resolution Deep Learning 從更廣的 CV 視角列舉應對高解析度成本的三類策略：linear-attention 等高效 transformer 變體、多尺度架構、以及 patch-based 處理。作者明確聲明本文不修改 attention 本身、而是採用 hierarchical dual-branch 的「全域粗推理 + 局部細修」分工，理由是這樣對「高解析度 3D reconstruction」這個具體問題更直接。這段的功能在於把 HD-VGGT 在方法論軸線上的選擇與 generic high-res CV 工作做出區隔。

§3.1 Preliminaries: Revisiting VGGT Bottleneck 把上述兩段的「scalability 痛點」量化。它先描述 VGGT 的處理流程：N 張 $H_0 \times W_0$ 影像各自經 ViT (DINOv2) 產生 $K_0$ patch tokens，全部串接後做 global self-attention，總 token 數為 $N \cdot K_0$，attention 複雜度為 $O((N \cdot K_0)^2 \cdot C)$。隨後給出本文最具說服力的數字 — 若解析度由 $H_0 \times W_0$ 倍增為 $2H_0 \times 2W_0$，每張影像的 token 數 $K \approx 4K_0$，global attention 複雜度暴增 $4^2 = 16$ 倍，使高解析度 reconstruction 在現有硬體上「computationally infeasible」。

這個 16 倍因子是 §3.3 走向 §3.4 的關鍵橋樑：它不只解釋為何 naive scaling 不可行，也直接合理化 hierarchical dual-branch 的設計動機 — 與其讓整個 backbone 吞下高解析度 token，不如把全域幾何在低解析度先解掉，再用一個 lightweight refiner 處理高解析度細節。Preliminaries 段同時保留了符號 $T_{\text{coarse}}$、$F_i^{\text{coarse}}$、$g^{\text{coarse}}$ 等命名空間，為後續方法章節省下重新介紹基底架構的篇幅。

### 3.4 Method (overview narrative)

(1110 words)

Method 章節由兩條並行主線構成，分別對應 Introduction 點出的兩大問題。第一條是 §3.2 HD-VGGT: A Hierarchical Dual-Branch Architecture，第二條是 §3.3 Feature Modulation for Robust Geometric Inference。

第一條主線採「先動機、再分支、再融合」展開。§3.2 開場用一句話把設計哲學釘住 — **decouple global coarse scaffold 與 local fine refinement** — 這正回應 Preliminaries 的 16 倍 complexity 推導。§3.2.1 Low-Resolution Branch 直接重用標準 VGGT backbone（DINOv2 + 深層 transformer $T_{\text{coarse}}$）處理 downsample 到 518×518 的影像，輸出粗糙 3D-aware feature map $\{F_i^{\text{coarse}} \in \mathbb{R}^{h \times w \times c}\}$ 與初步相機參數 $g^{\text{coarse}}$。它的功能定位非常明確 — 在低解析度下用得起 global attention 的成本去解決全域幾何與相機 pose 一致性，把這個「scaffold」交給下一階段。§3.2.2 High-Resolution Branch 分兩步：(1) Learned Feature Upsampling，作者先用 bilinear 公式說明 naive 內插會充當 low-pass filter、丟失高頻幾何與紋理；於是改採以高解析度影像 $I^{HR}$ 作為 guidance 的條件式上採樣模組 $\mathcal{U}: (\mathbb{R}^{h \times w \times c}, \mathbb{R}^{H \times W \times 3}) \to \mathbb{R}^{H \times W \times c}$，用淺層卷積 $\phi_{\text{guidance}}$ 抽 $I^{HR}$ 的高頻線索、用 $\phi_{\text{feat}}$ 處理 interpolate 過的 coarse feature、再用 $\phi_{\text{fuse}}$ 融合兩流；(2) High-Resolution Refiner $T_{\text{refine}}$ 是一個比 backbone 淺很多的 transformer（例如 6 層 vs. 24 層），可以採用 localized attention，因為全域結構已經解決，只需在高解析度上做 multi-view consistency 與最終 regress。這條主線的合理性在於：global attention 的成本只付一次（且付在低解析度），refiner 雖在高解析度但層數淺、attention 範圍窄。

第二條主線 §3.3 Feature Modulation 處理 unstable token 問題。作者把 multi-view feature representation 假設為一個低維 isometric Riemannian manifold，並定義 **geometric singularities**（repetitive texture、textureless surface、specular highlights）為 manifold 平滑結構的破壞點。§3.3.1 Manifold Anomaly Detection via Kernelized Gramian Statistics 提出在 RKHS 中以 cross-view Gramian $G^{QQ}_{l,t,s} = Q_{l,t} Q_{l,s}^T / \sqrt{c}$ 與 $G^{KK}_{l,t,s}$ 抓二階幾何，再用 temporal expectation $S^X_{i-j} = \mathbb{E}_W[\mathbb{E}_{L_{i,j}}[G^X_{l,t,s}]]$ 與 temporal variance $V^X_{i-j}$ 描述 manifold 穩定度，最後融合 shallow/middle/deep 三層先驗 $\omega_{\text{shallow}}, \omega_{\text{middle}}, \omega_{\text{deep}}$ 形成 posterior anomaly saliency map $S_{\text{anomaly}}$。§3.3.2 Manifold Regularization via Projection Gradient Flow 對初步 mask $M_{\text{initial}}$ 用 projection 誤差的 gradient flow 做精修，總梯度 $\nabla A$ 結合 geometric residual 與 photometric residual 兩項，藉此得到 $M_{\text{refined}}$。§3.3.3 Information-Gated Attentional Suppression 強調不能整層全壓抑，否則會 out-of-distribution；改採 targeted early-stage gating — 在 shallow layers 對異常 token 直接 nullify Key 向量 $K'_{p,l} = (1 - M_{\text{refined}, p}) \cdot K_{p,l}$，封閉 corrupted information 的入口。

兩條主線在敘事上彼此互補：dual-branch 解的是「規模問題」、Feature Modulation 解的是「品質問題」，兩者都是 §3.5 Experiments 要驗證的對象。Method 章節同時為實驗章節留下兩個明確的 ablation 軸 — w/o FM 對應 Feature Modulation 的影響、不同 refiner 深度與 upsampling 設計則對應 dual-branch。

### 3.5 Experiments (overview narrative)

(810 words)

Experiments 採「Setup → Main Results 三任務 → Qualitative」的標準三段結構，目標是把 §3.4 兩條主線同時放上多個 benchmark 進行壓力測試。

§4.1 Experimental Setup 把評測廣度鋪滿：Camera pose 用 RealEstate10K（static）、Sintel（dynamic outdoor）、TUM-dynamics（dynamic indoor）、CO3Dv2（object-centric）四個風格迥異的資料集；point map reconstruction 用 7-Scenes、NRGBD、DTU 與高解析度 MVS-SYNTH；monocular depth 用 ScanNet、NYUv2，並特別測試「無 GT camera prior」條件以驗證 robustness。Metric 隨任務切換：pose 用 AUC@10/30、RRA、RTA、ATE、RPE；point map 用 Mean/Median Accuracy 與 Completeness（cm）；depth 用 AbsRel 與 $\delta_1$，且預測值都做 least-squares scale alignment。Baselines 涵蓋 geometry transformer 一脈（VGGT、$\pi^3$、WorldMirror）、DUSt3R 範式（DUSt3R、MASt3R、Fast3R、CUT3R），加上 FLARE、DA3、MonST3R 等其他代表作；尤其引入 ablation HD-VGGT (w/o FM) 直接隔離 Feature Modulation 的貢獻。Implementation 細節給出訓練資源 — 16 顆 Ascend 910C（CloudMatrix384 supernode）訓練兩週，並沿用 VGGT 的 data scheduling、optimizer 與 loss formulation。

§4.2 Main Results 依三任務組織。§4.2.1 Camera Pose Estimation 在四個 dataset 上全面領先：RealEstate10K AUC@30 87.01%、CO3Dv2 高精度 Pose AUC@10 提升至 86.5%、Sintel ATE 0.071、TUM-dynamics ATE 0.009。論述把這些數字解讀為「dual-branch + Feature Modulation 有效抑制 transient dynamics 與 specular reflection 造成的 ambiguity」，把方法主張與 dynamic/specular 數字直接對應。§4.2.2 Point Map Reconstruction 在 7-Scenes（3.9 cm Acc）、NRGBD（2.4 cm Acc）、DTU（95.3 cm mean Acc）皆刷新 SOTA；論述強調「high-resolution input 讓模型抓得到 standard-resolution 抓不到的細節」。§4.2.3 Monocular Depth Estimation 在 ScanNet（AbsRel 0.049）、NYUv2（AbsRel 0.035）皆勝過 $\pi^3$ 與 WorldMirror，並用 ScanNet w/o GT Pose 條件下的 AbsRel 0.121 作為 robustness 證據。

§4.3 Qualitative Analysis 用 Figure 2（depth）與 Figure 3（point map）補上量化結果以外的觀感層證據：SOTA 方法常見的 over-smoothing 與 boundary bleeding 在 HD-VGGT 結果中減輕，lamp poles、chair legs 這類細結構被保留，牆面與地面更平整一致；point map 上 baseline 容易遺漏的 thin-structured 物件在 HD-VGGT 中更完整。論述把這視為 dual-branch 的 high-resolution refiner 善用 detail visual cue 的具體例證。

整章的鋪陳邏輯是：Setup 確保 evaluation 涵蓋 static/dynamic/object/indoor 多種情境，Main Results 在三大任務齊頭並進地證明 SOTA，Qualitative 則把數字翻譯成可被視覺感知的細節優勢。所有結論都收束到方法章兩條主線各自的價值上 — 為 §3.6 Conclusion 「scalable + robust 缺一不可」的主張提供完整的實證後盾。

### 3.6 Conclusion / Limitations / Future Work

(200 words)

Conclusion 段（論文中合併為單一「Conclusion and Discussion」章）採「重申貢獻 → 提煉洞見 → 展望」三步收束，不另闢 Limitations 子節。

第一段重申 HD-VGGT 是針對 efficient and robust high-resolution feed-forward 3D reconstruction 設計的新架構，再一次把兩條主線並列：dual-branch design 搭配 dedicated feature upsampling module 讓模型「在不放大整個 transformer backbone 的前提下吃進高解析度影像與監督」，Feature Modulation 則在視覺模糊區域抑制不穩定 token 以提升穩健性，兩者合力產出更精確且更細緻的重建。

第二段是論文真正的核心 take-away — 把 high-resolution feed-forward 的問題重新定義為「architectural efficiency 與 feature stability 必須並行」，作者明確點出單靠任一面向都不夠。並期望 cross-resolution geometric refinement 與 feature-level robustness mechanism 兩個概念能啟發後續工作。

第三段給出 future work：進一步整合 geometric reasoning、large-scale image collection 與 high-resolution neural representation，把 feed-forward 3D reconstruction 推向 real-world deployment。整段沒有顯式 limitation 條列，未來方向偏向高層的研究路線而非具體缺陷修補，留給讀者自行從 Method 與 Experiments 推測潛在 trade-off（例如 refiner 層數選擇、Feature Modulation 的超參數依賴等）。

## 4. Critical Profile

### 4.1 Highlights

- 提出 dual-branch 架構，將粗略幾何骨架（low-resolution branch，沿用 VGGT backbone）與細節精修（high-resolution branch）解耦，避免 full-resolution global self-attention 的 $O((N \cdot K)^2)$ 計算成本（page 5–6, §3.2）。
- 量化指出 VGGT 的根本瓶頸：將輸入解析度加倍會使每張影像 token 數變為 4 倍、global attention 成本爆炸 $4^2 = 16$ 倍，為整篇論文的設計動機提供了清楚的 scaling 論述（page 3, §3.1）。
- Learned Feature Upsampling 模組以 high-resolution 影像作為條件訊號，透過 $\phi_{\text{guidance}}$、$\phi_{\text{feat}}$、$\phi_{\text{fuse}}$ 三條卷積路徑融合粗特徵與高頻細節，原則上可逆轉雙線性插值的 low-pass 濾波損失（page 5, Eq. 3–5）。
- High-Resolution Refiner 以 6 層淺層 transformer（相對 backbone 的 24 層）處理升頻後的特徵，並可採用 localized attention，因為「全域幾何已被解析」（page 5, §3.2.2）。
- Feature Modulation 將視覺歧義區（重複紋理、弱紋理、鏡面）類比為動態場景的「事件」，並借用 RKHS 中的 kernelized Gramian 二階統計建立分層 Bayesian anomaly saliency map $S_{\text{anomaly}} = \omega_{\text{shallow}} \odot \omega_{\text{middle}} \odot \omega_{\text{deep}}$（page 6, Eq. 10）。
- 在 RealEstate10K 上達到 AUC@30 = 87.01、CO3Dv2 上 Pose AUC@10 = 86.5，全面超越 VGGT、$\pi^3$、WorldMirror 等 baseline（page 7–8, Table 1–2）。
- 在 7-Scenes（Acc. 3.9 cm）、NRGBD（Acc. 2.4 cm）、DTU（Acc. 95.3 cm）三項 point-map 重建上同時刷新 SOTA（page 9, Table 3）。
- 在 ScanNet 與 NYUv2 monocular depth 上分別取得 AbsRel 0.049 與 0.035，並在 ScanNet「無 GT 相機姿態」設定下仍保有 0.121 的 AbsRel，優於 MASt3R 的 0.165（page 9–10, Table 4–5）。
- 質性結果聲稱可保留 lamp pole、chair leg 等細結構，並改善 baseline 在物體邊界出現的 over-smoothing 與 bleeding artifacts（page 10, §4.3，Figure 2–3）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

論文未明確設立 limitations 段落；§5 Conclusion and Discussion（page 10–11）僅以 future work 的口吻提到「進一步整合 geometric reasoning、large-scale image collections 與 high-resolution neural representations」，並未承認任何具體缺陷。**作者實質上未公開討論方法的限制**。

#### 4.2.2 Phyra-inferred

- **聲稱效率卻完全沒有 FLOPs / memory / wall-clock 數據**：整篇論文的動機是「VGGT 的二次方複雜度阻礙 high-resolution scaling」（page 3），但 §4 Experiments 從頭到尾沒有任何 token 數、GPU memory、推論時間或 FLOPs 比較表，無法驗證 dual-branch 是否真的比 baseline 在相同硬體下更便宜。
- **HD-VGGT (w/o FM) ablation 被宣告但從未出現在任何表格**：§4.1 Baselines（page 7）明確說「include an ablation model HD-VGGT (w/o FM) which disables the Feature Modulation mechanism」，但 Table 1–5 完全沒有這一列，使 Feature Modulation 的貢獻無法被量化驗證。
- **MVS-SYNTH high-resolution benchmark 列了卻沒給結果**：§4.1（page 7）將 MVS-SYNTH 列為 high-resolution point-map 評測，但 Table 3 只有 7-Scenes、NRGBD、DTU，論文唯一直接針對 high-resolution 的證據被悄悄拿掉。
- **「High-resolution」全篇從未量化**：低解析度分支寫明 $518 \times 518$（page 3），但 high-resolution branch 究竟跑在 $1036 \times 1036$ 還是 $2048 \times 2048$、token 數與 baseline 對比為何，沒有任何一處交代。
- **未與直接競品 FastVGGT [7] 比較**：Reference [7]（FastVGGT, arXiv:2509.02560）正是針對 VGGT 加速的同類方法，但所有對比表格皆未列入，存在 cherry-picking baseline 的疑慮。
- **Feature Modulation 的「training-free」宣稱與其依賴互相矛盾**：§3.3.2（page 6）的 $M_{\text{refined}}$ 依賴 reprojection 與 photometric residual $r_{d,i}, r_{c,i}$，這些殘差需要模型已預測出幾何，而模型又被假設能因此 mask 掉錯誤 token，形成循環依賴；論文未說明在 forward pass 中如何打破此循環。
- **Eq. 10 的元素積缺乏理論依據**：$\omega_{\text{shallow}}$、$\omega_{\text{middle}}$、$\omega_{\text{deep}}$ 來自不同層、不同統計量（一階 vs 二階、$Q$ vs $K$ vs $QK$），直接逐元素相乘作為 posterior 並非任何標準 hierarchical Bayesian 推論的結果，更像是後設選擇的工程啟發式。
- **過度的數學包裝可能掩蓋方法的實質簡單性**：Riemannian manifold、Kolmogorov complexity、Shannon entropy、information-gating 等術語密集出現在 §3.3，但實際操作只是「在淺層把可疑 token 的 Key 向量設為 0」（Eq. 15），數學包裝與實作之間存在明顯落差。
- **自引比例偏高**：作者群（Deyi Ji、Lanyun Zhu、Tianrun Chen）的自引在 References 中佔比顯著（[5, 6, 9, 11, 12, 21–33] 等），且部分引用與本文方法的關聯性薄弱，影響相關工作論述的客觀性。
- **無 code、無 project page**：BIBLIO.json 中 `code` 與 `project` 皆為 null，方法的可重現性僅能依賴論文文字描述，且訓練細節寫得極度簡略（「2 weeks on 16 Ascend 910C，與 VGGT 相似策略」）。

### 4.3 Phyra's Judgment (summary)

HD-VGGT 的 dual-branch coarse-to-fine 結構在概念上合理，是把 VGGT 推向高解析度的自然且務實的工程路徑；Learned Feature Upsampling 的條件式設計也直觀地解決了下採樣造成的高頻資訊損失。然而論文最重大的兩個賣點——「scalable」與「robust」——都缺乏關鍵證據：前者完全沒有 FLOPs / memory / latency 比較，後者宣告的 ablation `HD-VGGT (w/o FM)` 在表格中神祕消失。Feature Modulation 段落的 RKHS / Bayesian / information-gating 數學包裝與實際只是「淺層 Key vector 歸零」的實作之間落差過大，使核心創新的可驗證性受損。整體上這是一篇方法直覺正確、表格數字漂亮，但實驗嚴謹度與透明度不足以支撐其論文書寫強度的工作。

## 5. Methodology Deep Dive

### 5.1 Method Overview

HD-VGGT 提出一個 **dual-branch hierarchical architecture**，將高解析度 3D 重建問題拆解為「粗略全域幾何」與「細粒度局部精修」兩個解耦的子任務（§3.2）。低解析度分支沿用 VGGT backbone（DINOv2 patch tokenizer + 全域 self-attention transformer $T_{coarse}$），輸入下採樣至 $518 \times 518$ 的圖像 $\{I^{LR}_i\}_{i=1}^N$，輸出粗略 3D-aware feature maps $\{F^{coarse}_i \in \mathbb{R}^{h \times w \times c}\}$ 與初始相機參數 $g^{coarse}$（公式 1）。此分支負責建立全域一致的幾何骨架與相機姿態，避免在原始解析度上付出 $O((N \cdot K)^2)$ 的注意力代價（§3.1 指出解析度加倍會導致 token 數約 4 倍、注意力代價約 16 倍）。

高解析度分支則由 **Learned Feature Upsampling 模組** $U$ 與 **High-Resolution Refiner transformer** $T_{refine}$ 組成。Upsampling 模組以高解析影像 $I^{HR}$ 作為 guidance，透過淺層卷積網路 $\phi_{guidance}$ 抽取高頻細節，並融合經 $\phi_{feat}$ 升頻的粗特徵 $F^{coarse}$，再以 $\phi_{fuse}$ 得到 $F^{hr}$（公式 3-5）。Refiner 為輕量 transformer（6 層 vs. backbone 的 24 層），可使用 windowed/local attention，最終輸出高保真 dense point maps $D^{final}$ 與精修相機參數 $g^{final}$（公式 6）。

第三個關鍵組件為 **Feature Modulation 機制**（§3.3），用於提升幾何穩健性。作者觀察到重複紋理、弱紋理、鏡面反射等視覺歧義區域會在早期 transformer 層產生統計上不穩定的 token，且解析度提高時不穩定性會被放大並腐蝕跨視角幾何一致性。Feature Modulation 透過三個步驟處理：(1) 在 RKHS 中以 kernelized Gramian 計算跨視角二階統計量，建立分層 Bayesian 異常顯著圖 $S_{anomaly}$；(2) 以投影梯度流精修遮罩得到 $M_{refined}$；(3) 在淺層 transformer 透過 information-gated attention 將異常 token 的 Key 向量歸零，從源頭阻斷錯誤訊號傳播。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: N high-resolution images {I^HR_i ∈ R^[B, N, H, W, 3]}
   │
   ├──[Downsample]──→ {I^LR_i ∈ R^[B, N, 518, 518, 3]}
   │                       │
   │                       ├──[DINOv2 ViT Patch Tokenizer]──→ F_i ∈ R^[B, N, K0, C]
   │                       │                                  (K0 patch tokens per image)
   │                       │
   │                       ├──[Coarse Transformer T_coarse]──→
   │                       │   - 24 layers (per VGGT)
   │                       │   - Global self-attention over N·K0 tokens
   │                       │   - Frame Attention + Global Attention 交替
   │                       │   - Feature Modulation 注入於淺層 (mask Keys of anomalous tokens)
   │                       │
   │                       └──→ {F^coarse_i ∈ R^[B, N, h, w, c]}, g^coarse ∈ R^[B, N, ?]
   │                            (low-res 3D-aware features + initial camera params)
   │                            注：論文未明確指定 h, w, c, K0, C 的具體數值
   │
   ├──[High-Resolution Branch]
   │       │
   │       ├──[Guidance Branch] φ_guidance(I^HR) ──→ F_guide ∈ R^[B, N, H, W, c']
   │       │   (shallow conv network 抽取高頻細節)
   │       │
   │       ├──[Feature Branch] φ_feat(Interpolate(F^coarse)) ──→ F_interp ∈ R^[B, N, H, W, c]
   │       │   (bilinear interpolation + conv refinement)
   │       │
   │       ├──[Fusion] φ_fuse(concat(F_guide, F_interp)) ──→ F^hr_i ∈ R^[B, N, H, W, c]
   │       │
   │       └──[Refiner Transformer T_refine]──→
   │           - 6 layers (vs. 24 in backbone)
   │           - Localized/window attention 為主
   │           - 強制多視角細節一致性
   │
   └──→ Output: D^final ∈ R^[B, N, H, W, 3] (high-fidelity 3D point maps)
                g^final ∈ R^[B, N, ?] (refined camera parameters)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Low-Resolution Branch (Coarse Backbone)

**Function:** 以 VGGT backbone 在低解析度上高效求出全域一致的粗略幾何骨架與相機姿態，作為後續精修的條件輸入。

**Input:**
- Name: $\{I^{LR}_i\}_{i=1}^N$
- Shape: `[B, N, 518, 518, 3]`
- Source: 將原始高解析輸入 $\{I_i \in \mathbb{R}^{H_0 \times W_0 \times 3}\}$ 下採樣至標準解析度

**Output:**
- Name: $\{F^{coarse}_i\}$, $g^{coarse}$
- Shape: $\{F^{coarse}_i \in \mathbb{R}^{[B, N, h, w, c]}\}$, $g^{coarse} \in \mathbb{R}^{[B, N, ?]}$
- Consumer: Learned Feature Upsampling 模組（以 $F^{coarse}$ 為輸入）與 Pose Head（以 $g^{coarse}$ 為初始姿態）

**Processing:**

低解析影像先通過 DINOv2 ViT 抽取每張影像的 $K_0$ 個 patch tokens，得到 $F_i \in \mathbb{R}^{K_0 \times C}$（§3.1）。隨後將 $N$ 張影像的 tokens 串接，餵入深層 transformer $T_{coarse}$，在共 $N \cdot K_0$ 個 tokens 上施加 global self-attention，計算複雜度為 $O((N \cdot K_0)^2 \cdot C)$。Frame attention 與 global attention 交替處理跨視角資訊。Feature Modulation 機制在 $T_{coarse}$ 的淺層 $L_{shallow}$ 注入 token masking（詳見 §5.3.4）。

**Key Formulas:**

$$\{F^{coarse}_i, g^{coarse}\} = T_{coarse}(\{I^{LR}_i\}_{i=1}^N) \quad (1)$$

**Implementation Details:**

論文指定低解析度為 $518 \times 518$（§3.2.1 範例），backbone 使用 DINOv2 作為 patch tokenizer，transformer 為 24 層深度（§3.2.2 與 refiner 對比時提及）。$K_0$、$C$、$h$、$w$、$c$ 的具體數值論文未明確指定。訓練於 16 張 Ascend 910C（CloudMatrix384 supernode），共 2 週，採用與 VGGT 相似的 data scheduling、optimizer settings 與 loss formulations（§4.1）。

#### 5.3.2 Learned Feature Upsampling Module

**Function:** 以高解析影像 $I^{HR}$ 為條件，將粗略特徵升頻並注入高頻細節，反轉下採樣造成的資訊損失。

**Input:**
- Name: $F^{coarse}$, $I^{HR}$
- Shape: $F^{coarse} \in \mathbb{R}^{[B, N, h, w, c]}$, $I^{HR} \in \mathbb{R}^{[B, N, H, W, 3]}$
- Source: $F^{coarse}$ 來自 Low-Resolution Branch，$I^{HR}$ 為原始高解析輸入

**Output:**
- Name: $F^{hr}$
- Shape: `[B, N, H, W, c]`
- Consumer: High-Resolution Refiner Transformer

**Processing:**

模組 $U$ 學習一個條件映射 $U: (\mathbb{R}^{h \times w \times c}, \mathbb{R}^{H \times W \times 3}) \rightarrow \mathbb{R}^{H \times W \times c}$（§3.2.2）。並行執行兩個分支：guidance 分支以淺層卷積網路 $\phi_{guidance}$ 從 $I^{HR}$ 抽取高頻細節（公式 3）；feature 分支先將 $F^{coarse}$ 以簡單插值（如 bilinear，對照公式 2 的 naive baseline）升至目標解析度，再經卷積精修網路 $\phi_{feat}$ 處理（公式 4）。最後以 $\phi_{fuse}$ 融合兩路特徵並輸出 $F^{hr}$（公式 5）。此設計避免了 naive bilinear upsampling 作為低通濾波器導致的高頻細節遺失（§3.2.2 對公式 2 的批評）。

**Key Formulas:**

$$F_{guide} = \phi_{guidance}(I^{HR}) \quad (3)$$
$$F_{interp} = \phi_{feat}(\text{Interpolate}(F^{coarse})) \quad (4)$$
$$F^{hr} = \phi_{fuse}(\text{concat}(F_{guide}, F_{interp})) \quad (5)$$

**Implementation Details:**

論文指出設計受 IHR-guided upsampling 文獻啟發（引用 [37]），$\phi_{guidance}$、$\phi_{feat}$、$\phi_{fuse}$ 均為「shallow convolutional network」（§3.2.2），但未明確指定層數、通道數、卷積核大小或 interpolate 的具體方式（推測為 bilinear，因公式 2 即為 bilinear 形式）。下採樣因子 $s$ 滿足 $H = s \cdot h$ 但具體數值未指定。

#### 5.3.3 High-Resolution Refiner Transformer

**Function:** 在已升頻的高解析特徵上執行輕量 transformer 推論，強制多視角細節一致性，並回歸最終高保真輸出。

**Input:**
- Name: $\{F^{hr}_i\}_{i=1}^N$
- Shape: `[B, N, H, W, c]`
- Source: Learned Feature Upsampling Module

**Output:**
- Name: $D^{final}$, $g^{final}$
- Shape: $D^{final} \in \mathbb{R}^{[B, N, H, W, 3]}$, $g^{final} \in \mathbb{R}^{[B, N, ?]}$
- Consumer: DPT Head 與 Pose Head（最終輸出）

**Processing:**

$T_{refine}$ 為淺層 transformer（6 層，相較於 backbone 的 24 層，§3.2.2），由於全域幾何已由 coarse branch 解析完畢，refiner 可採用更高效的 localized attention（如 window attention，見 Figure 1 的 "Window Attention" 模組）。Refiner 的目的是在不重跑全解析全域注意力的前提下，精修高解析特徵、強制多視角細節一致性，最終透過 DPT Head 與 Pose Head 回歸 dense 3D point maps 與精修相機參數。此設計使整體架構避開了 full-resolution global self-attention 的平方級複雜度。

**Key Formulas:**

$$\{D^{final}, g^{final}\} = T_{refine}(\{F^{hr}_i\}_{i=1}^N) \quad (6)$$

**Implementation Details:**

論文明確指出層數（6 層）與相對於 backbone 的比例（24 層），並提到「more efficient, localized attention mechanisms」（§3.2.2），但未明確指定 window size、head 數量或具體的 attention 變體。輸出最終透過 DPT Head（dense prediction transformer head，見 Figure 1）產生高解析 3D point maps。

#### 5.3.4 Feature Modulation: Manifold Anomaly Detection

**Function:** 在 RKHS 中以 kernelized Gramian 偵測跨視角統計上不穩定的 token，建立分層 Bayesian 異常顯著圖。

**Input:**
- Name: 每層 $l$、視角對 $(t, s)$ 的 Query/Key 向量 $Q_{l,t}, K_{l,t}, Q_{l,s}, K_{l,s}$
- Shape: `[B, N, K, c]`（$K$ 為 token 數量）
- Source: $T_{coarse}$ 各層的 attention QKV 投影

**Output:**
- Name: $S_{anomaly}$
- Shape: `[B, N, K]`（每個 token 一個 anomaly probability）
- Consumer: Manifold Regularization 步驟（產生 $M_{refined}$）

**Processing:**

對每個視角對 $(t, s)$ 計算 cross-view Gramians（公式 7），作為 kernel matrices 編碼特徵流形的二階幾何。將跨時序窗口 $W(t)$ 的 Gramians 序列建模為 matrix-valued stochastic process，並以 temporal expectation $\mathbb{E}_W[\cdot]$ 與 temporal variance $\mathbb{V}_W[\cdot]$ 估計其一階與二階矩（公式 8-9）。$S^X_{i-j}$ 代表流形的 stationary component，$V^X_{i-j}$ 量化「information-theoretic surprise」即異常程度。最後以分層 Bayesian 框架融合來自不同網路深度的多尺度先驗：$\omega_{shallow}$ 為高頻語義異常先驗、$\omega_{middle}$ 為中頻幾何不穩定先驗、$\omega_{deep}$ 為低頻空間正則化先驗（公式 11-13），三者乘積即為 token 級異常後驗（公式 10）。

**Key Formulas:**

$$G^{QQ}_{l,t,s} = \frac{Q_{l,t} Q^T_{l,s}}{\sqrt{c}}, \quad G^{KK}_{l,t,s} = \frac{K_{l,t} K^T_{l,s}}{\sqrt{c}} \quad (7)$$

$$S^X_{i-j} = \mathbb{E}_W[\mathbb{E}_{L_{i,j}}[G^X_{l,t,s}]] \quad (8)$$
$$V^X_{i-j} = \mathbb{V}_W[\mathbb{E}_{L_{i,j}}[G^X_{l,t,s}]] \quad (9)$$

$$S_{anomaly} = \omega_{shallow} \odot \omega_{middle} \odot \omega_{deep} \quad (10)$$

$$\omega_{shallow} = (1 - S^{KK}_{shallow}) \odot V^{QK}_{shallow} \quad (11)$$
$$\omega_{middle} = 1 - S^{QQ}_{middle} \quad (12)$$
$$\omega_{deep} = (1 - V^{QQ}_{deep}) \odot S^{QQ}_{deep} \quad (13)$$

**Implementation Details:**

論文指出此框架為「training-free」（§3.3），靈感來自動態場景分析文獻 [38]。關鍵觀察是將 static geometric singularities 視為與 dynamic events 統計上同構（§3.3 開頭），故借用動態分析的 Bayesian 框架。$\odot$ 為 Hadamard product。論文未明確指定 temporal window $W(t)$ 的大小、$L_{i,j}$ 層集合的具體選擇，或 shallow/middle/deep 的層數劃分閾值。

#### 5.3.5 Feature Modulation: Manifold Regularization & Information Gating

**Function:** 透過投影梯度流精修初始異常遮罩，並以早期資訊閘控於淺層 transformer 抑制異常 token 影響。

**Input:**
- Name: 初始遮罩 $M_{initial} = [S_{anomaly} > \alpha]$、3D point cloud、reprojection residuals $r_{d,i}, r_{c,i}$
- Shape: $M_{initial} \in \mathbb{R}^{[B, N, K]}$（boolean）
- Source: $S_{anomaly}$ 來自 §5.3.4，residuals 來自 reprojection error 計算

**Output:**
- Name: $K'_{p,l}$（masked Key vectors at shallow layers）
- Shape: `[B, N, K, c]`
- Consumer: Coarse Transformer $T_{coarse}$ 的 attention 計算（取代原 Key 向量）

**Processing:**

第一階段（Manifold Regularization）：將初始異常遮罩視為流形奇異點的粗略分割，透過投影梯度流（projection gradient flow）精修。將 3D 點雲視為場景流形的離散採樣，基於幾何殘差 $r_{d,i}$ 與光度殘差 $r_{c,i}$ 在流形上定義 vector field，計算每點的總聚合梯度 $\nabla A$（公式 14），其中 $w_i$ 將計算限制在初始穩定區域。$\nabla A$ 的大小代表局部流形扭曲程度，閾值化後得到精修遮罩 $M_{refined}$，更精確劃定幾何奇異區域邊界。

第二階段（Information-Gated Attentional Suppression）：論文指出 naive 全深度抑制等同於完全關閉資訊通道，會導致 out-of-distribution 行為（§3.3.3）。因此採用 targeted early-stage gating：僅在淺層 $L_{shallow}$ 對異常 token 的 Key 向量歸零（公式 15），於資訊源頭關閉受腐蝕的 data streams，避免錯誤在深層放大。後續幾何推論與高解析精修階段因此可基於 purified information substrate 運作。

**Key Formulas:**

$$\nabla A = \frac{1}{N} \sum_{i}^{N} \|w_i r_{d,i} \nabla r_{d,i}\| + \lambda \frac{1}{N} \sum_{i}^{N} \|w_i r_{c,i}\| \quad (14)$$

$$K'_{p,l} = (1 - M_{refined,p}) \cdot K_{p,l}, \quad \forall l \in L_{shallow} \quad (15)$$

**Implementation Details:**

論文指定 gating 僅施加於 $L_{shallow}$（§3.3.3），但未明確指定 $L_{shallow}$ 的具體層數範圍、閾值 $\alpha$ 的數值、$\lambda$ 權重，或 $r_{d,i}, r_{c,i}$ 的具體計算方式（推測 $r_d$ 為幾何投影誤差、$r_c$ 為光度誤差）。$N$ 在公式 14 中的具體含義（視角數或點數）論文未明確指定。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| RealEstate10K [39] | Camera pose estimation (static, mixed) | the paper does not specify | test |
| Sintel [40] | Camera pose estimation (outdoor, dynamic) | the paper does not specify | test |
| TUM-dynamics [41] | Camera pose estimation (indoor, dynamic) | the paper does not specify | test |
| CO3Dv2 [42] | Camera pose estimation (object-centric) | the paper does not specify | test |
| 7-Scenes [43] | Point map reconstruction (scene) | the paper does not specify | test |
| NRGBD [44] | Point map reconstruction (scene) | the paper does not specify | test |
| DTU [45] | Point map reconstruction (object) | the paper does not specify | test |
| MVS-SYNTH [46] | High-resolution point map reconstruction | the paper does not specify | test |
| ScanNet [47] | Monocular depth estimation (with / without GT pose) | the paper does not specify | test |
| NYUv2 [48] | Monocular depth estimation | the paper does not specify | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| AUC@10 / AUC@30 | 相機姿態誤差曲線下面積，於 10° 與 30° 閾值評估 pose 對齊精度 | yes |
| RRA@30 | Relative Rotation Accuracy，30° 閾值內的相對旋轉精度 | no |
| RTA@30 | Relative Translation Accuracy，30° 閾值內的相對平移精度 | no |
| ATE | Absolute Trajectory Error，整體軌跡與 GT 之差 | yes |
| RPEt / RPEr | Relative Pose Error 之 translation 與 rotation 分量 | no |
| Accuracy (cm) | 預測點雲到 GT 之距離（Mean / Median） | yes |
| Completeness (cm) | GT 點雲到預測點雲之距離（Mean / Median） | yes |
| AbsRel | Absolute Relative depth error，與 GT 經 least-squares 對齊後計算 | yes |
| δ1 | 深度像素中誤差比例落在 1.25 倍以內的比率 | no |

### 6.3 Training and Inference Settings

- **Hardware**：16 顆 Ascend 910C，於 CloudMatrix384 supernode 上訓練約 2 週。
- **Optimizer / LR schedule / batch size / steps**：the paper does not specify，僅說明採用「與 VGGT 相似」的 data scheduling、optimizer settings 與 loss formulations。
- **Resolution 設定**：low-resolution 分支沿用 VGGT backbone（例：$518 \times 518$），high-resolution 分支則透過 learned feature upsampling 達成倍增解析度（高解析度 token 數約為 $K \approx 4K_0$）。
- **Refiner 規模**：high-resolution refiner $T_{\text{refine}}$ 為 6 層，遠淺於 backbone 的 24 層。
- **Inference 設定**：所有深度預測都用 least-squares fit 對齊 GT scale；ScanNet 額外評估 with / without GT pose 兩種條件；其餘推論超參數 the paper does not specify。
- **Ablation 設定**：論文僅定義 HD-VGGT (w/o FM)（關閉 Feature Modulation）一組 ablation，但在 §4 主表中並未出現對應數據列。

### 6.4 Main Results

**Camera pose estimation — RealEstate10K / Sintel / TUM-dynamics**（Table 1）

| Method | RE10K AUC@30 ↑ | Sintel ATE ↓ | TUM-dyn ATE ↓ | Notes |
|---|---|---|---|---|
| Fast3R [14] | 61.68 | 0.371 | 0.090 | DUSt3R-paradigm |
| CUT3R [17] | 81.47 | 0.217 | 0.047 | mixed static/dynamic |
| FLARE [18] | 80.01 | 0.207 | 0.026 | foundation + 3DGS |
| VGGT [3] | 77.62 | 0.167 | 0.012 | base backbone |
| π3 [10] | 85.90 | 0.074 | 0.014 | permutation-equivariant |
| WorldMirror [49] | 86.28 | 0.096 | 0.010 | any-prior prompting |
| **HD-VGGT (Ours)** | **87.01** | **0.071** | **0.009** | dual-branch + FM |

**Camera pose estimation — CO3Dv2**（Table 2）

| Method | Pose AUC@10 ↑ | Pose AUC@30 ↑ | Notes |
|---|---|---|---|
| DUSt3R [13] | 70.1 | 76.7 | pairwise pointmap |
| MASt3R [50] | 78.2 | 81.8 | matching-grounded |
| VGGT [3] | 83.3 | 88.2 | base backbone |
| **HD-VGGT (Ours)** | **86.5** | **90.4** | object-level 大幅提升 |

**Point map reconstruction**（Table 3，皆為 Acc Mean / Comp Mean，cm，越低越好）

| Method | 7-Scenes Acc ↓ | NRGBD Acc ↓ | DTU Acc ↓ | Notes |
|---|---|---|---|---|
| Fast3R [14] | 9.6 | 13.5 | 334.0 | — |
| CUT3R [17] | 9.4 | 10.4 | 474.2 | — |
| FLARE [18] | 8.5 | 5.3 | 254.1 | — |
| VGGT [3] | 4.6 | 5.1 | 133.8 | base backbone |
| π3 [10] | 4.8 | 2.6 | 119.8 | — |
| WorldMirror [49] | 4.3 | 4.1 | 101.7 | 前 SoTA |
| **HD-VGGT (Ours)** | **3.9** | **2.4** | **95.3** | scene 與 object 同步刷新 |

**Monocular depth — ScanNet / NYUv2**（Table 4）

| Method | ScanNet AbsRel ↓ | ScanNet δ1 ↑ | NYUv2 AbsRel ↓ | NYUv2 δ1 ↑ |
|---|---|---|---|---|
| DUSt3R [13] | 0.081 | 0.909 | 0.143 | 0.814 |
| MASt3R [50] | 0.110 | 0.865 | 0.115 | 0.848 |
| VGGT [3] | 0.056 | 0.951 | 0.062 | 0.969 |
| π3 [10] | 0.054 | 0.956 | 0.038 | 0.986 |
| WorldMirror [49] | 0.052 | 0.957 | 0.063 | 0.968 |
| **HD-VGGT (Ours)** | **0.049** | **0.961** | **0.035** | **0.988** |

**Monocular depth — ScanNet w/ vs w/o GT Pose**（Table 5，AbsRel ↓）

| Method | w/ GT Pose | w/o GT Pose |
|---|---|---|
| DUSt3R [13] | 0.145 | 0.182 |
| MASt3R [50] | 0.131 | 0.165 |
| VGGT [3] | 0.119 | 0.140 |
| **HD-VGGT (Ours)** | **0.102** | **0.121** |

### 6.5 Ablation Studies

論文在 §4.1 Baselines 段落明確宣告：「we include an ablation model HD-VGGT (w/o FM) which disables the Feature Modulation mechanism」，意圖驗證 §3.3 提出的 Feature Modulation（Manifold Anomaly Detection + Projection Gradient Flow + Information-Gated Attentional Suppression）是否真的貢獻最終精度。

然而：

- **w/o FM 數據缺席**：Table 1–5 的主結果表格中皆未列出 HD-VGGT (w/o FM) 的對應數值，文中也沒有任何段落報告該變體在任一資料集上的 AUC、ATE、Acc 或 AbsRel。讀者無法量化 Feature Modulation 對最終分數的貢獻。
- **Dual-branch 拆解缺席**：論文未提供僅關閉 high-resolution branch 或僅使用 bilinear upsampling（公式 (2) 的 baseline）取代 learned feature upsampling 的對照組，因此 §3.2.2 的 learned upsampling 與 high-resolution refiner 各自的貢獻無法分離。
- **Feature Modulation 內部三步未拆解**：shallow / middle / deep 三個 prior（公式 (10)–(13)）、projection gradient flow refinement、以及 information-gated suppression 三個子模組之間未做 leave-one-out 比較，難以判斷誰是真正的關鍵。
- **是否回答對的問題？** 宣告的 ablation 設計方向正確（針對新提出的 FM 模組），但因實際數據未出現於正文，目前等同於缺少 ablation；剩下的 §4.2 比較皆為跨方法的 SoTA 競爭，不屬於診斷性 ablation，更接近 sanity-style 的 leaderboard 對照。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 與當前 SoTA 系列 VGGT、π3、WorldMirror 直接對比於 Tables 1–4。
- [covered] Has cross-task / cross-dataset evaluation — 涵蓋 pose estimation、point map、monocular depth 三任務，跨 RealEstate10K / Sintel / TUM-dynamics / CO3Dv2 / 7-Scenes / NRGBD / DTU / ScanNet / NYUv2 共 9 個資料集。
- [missing] Has ablations that diagnose the new components — §4.1 宣告了 HD-VGGT (w/o FM)，但 Tables 1–5 完全未列出該變體的數值，dual-branch 與 learned upsampling 也沒有拆解實驗。
- [missing] Has a scaling study — 沒有對輸入解析度、view 數量、或 refiner 深度（6 vs 24 層以外）做 sweep，§3.1 僅以理論 $O((N \cdot K_0)^2 \cdot C)$ 論述。
- [missing] Has an efficiency / wall-clock comparison — 全文未報告 latency、FPS、memory footprint、或與 VGGT 的高解析度推論成本對照，雖然 motivation 完全奠基於 efficiency。
- [missing] Reports variance / standard deviation / multiple seeds — 所有表格皆為單次點估值，無 std、無多 seed。
- [missing] Releases code / weights / data sufficient for reproducibility — 論文未附 code repository、checkpoint、或訓練超參數細節（optimizer、lr、batch size、steps 皆 the paper does not specify）。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1：Dual-branch 解耦使高解析度重建在計算上可行**——*partially supported*。架構描述清晰（page 4, Figure 1；§3.2），且 Tables 1–5 顯示準確度全面提升，間接暗示模型確實處理了更高解析度的輸入；但**沒有任何 FLOPs、memory、token 數、wall-clock 表格**佐證它比 single-branch full-resolution VGGT 更便宜或更可行，無法區分增益是來自「dual-branch 設計」還是單純「更多參數 / 更長訓練」。
- **C2：Learned Feature Upsampling 注入高頻細節，逆轉下採樣的資訊損失**——*partially supported*。Figure 2–3 的質性對比顯示邊界更銳利、細結構更完整，與設計直覺一致；但缺少對 $\phi_{\text{guidance}}$ 的消融（例如將其換成 bilinear），無法將 quality gain 歸因到此模組本身而非整個 high-res branch。
- **C3：Feature Modulation 提升歧義區的幾何穩健性**——*overclaimed*。§4.1 明文宣告了 `HD-VGGT (w/o FM)` ablation，但 Table 1–5 全部沒有此列；目前所有數字都是「有 FM」的整體模型，FM 的邊際貢獻完全沒有被量化。RKHS / kernelized Gramian / hierarchical Bayesian 的理論包裝因此處於「無證據支撐」狀態。
- **C4：在多個 benchmark 達成 SOTA**——*supported with caveats*。表格數字相對 $\pi^3$、WorldMirror 等近期 baseline 確有領先（如 7-Scenes Acc. 3.9 vs 4.3 cm，CO3Dv2 Pose AUC@10 86.5 vs 83.3），但領先幅度多在 0.3–3% 區間，且未與直接同類加速工作 FastVGGT [7] 比較，亦未在自己列為高解析度的 MVS-SYNTH 上給出結果。
- **C5：在動態 / 弱紋理場景下提升 robustness**——*partially supported*。Sintel ATE 從 $\pi^3$ 的 0.074 降至 0.071、TUM-dynamics 從 0.014 降至 0.009（page 7, Table 1），改善真實但量級小；論文未設計專門針對 specular / repetitive texture 的 stress-test benchmark，難以區分這是 FM 的功勞還是高解析度本身帶來的好處。

### 7.2 Fundamental Limitations of the Method

**Coarse branch 的錯誤無法被 refiner 修正。** Dual-branch 的設計前提是「low-resolution branch 已建立全域一致的幾何骨架與相機姿態」（page 4, §3.2.1），$g^{\text{coarse}}$ 直接影響到 high-res branch 的 token 對齊與 supervision。一旦低解析度階段在大尺度遮擋、極端 baseline 或重複紋理下產生姿態錯誤，後續 6 層 lightweight refiner（page 5）並無重新進行全域 multi-view 對齊的能力，錯誤會被放大且無回饋路徑可修正。

**「High-resolution」其實有上限，並未根本解決平方複雜度。** 論文以 token 數平方成長為動機（page 3），但 high-res branch 仍是 transformer，當解析度繼續推到 $2K \times 2K$ 以上時，即便只有 6 層、即便採用 windowed / localized attention，token 數仍會呈現 $4 \times$ 成長。論文未討論此 branch 的 scaling 上限，也未說明真正運行的解析度，因此「scalable」是相對於 VGGT 的暫緩，而非結構性突破。

**Feature Modulation 是 inference-time heuristic 而非真正的學習機制。** §3.3.3 將「異常 token」的 Key 向量設為 0（Eq. 15），這是一個 hard gating，無梯度反向傳遞至 backbone；模型在訓練時並未學到「該對哪類 token 降權」。此外，$M_{\text{refined}}$ 依賴模型自身的 reprojection 與 photometric residual（Eq. 14），形成「要先有預測才能 mask、mask 後又重新預測」的循環，論文未明確說明 forward pass 中是否多次迭代或如何打破循環，導致該機制的實際運作方式不透明。

**RKHS 與 hierarchical Bayesian 包裝缺乏對應的優化目標。** §3.3.1 中 $S^X$（stationary component）與 $V^X$（temporal variance）都只是統計量，論文沒有任何 loss term 顯式優化「manifold isometry」或「RKHS 中的 anomaly entropy」；所有訓練 loss 仍是 §4.1 提及的「與 VGGT 相同的 loss formulation」。這代表 §3.3 的數學框架在訓練中沒有作用，只在推論時用來決定一個布林 mask，理論強度與實作貢獻嚴重不匹配。

### 7.3 Citations Worth Tracking

- **[3] Wang et al., VGGT (CVPR 2025)**：HD-VGGT 的 backbone 與 baseline，理解 low-res branch 的全部行為與限制都需先讀懂 VGGT 的 global self-attention 設計與訓練 loss。
- **[37] Wimmer et al., AnyUp (arXiv 2510.12764, 2025)**：Learned Feature Upsampling 模組明確以此為靈感，欲評估 §3.2.2 的設計是否屬實質創新或僅為應用，必須對照原方法。
- **[38] Hu et al., VGGT4D (arXiv 2511.19971, 2025)**：作者自承 Feature Modulation 的「dynamic-event 類比」與 hierarchical Bayesian 框架直接源自此文，理解 HD-VGGT §3.3 是否屬於原創或重用須回查 VGGT4D。
- **[10] Wang et al., $\pi^3$ (arXiv 2507, 2025)**：所有表格中最強的同期競品，且也宣稱解決 reference-view bias，是評估 HD-VGGT 增益實質性的關鍵 baseline。
- **[7] Shen et al., FastVGGT (arXiv 2509.02560, 2025)**：直接針對 VGGT 加速的 training-free 方法，HD-VGGT 在所有效率相關討論中略過此文，是回應「scalability claim 是否成立」最重要的對照工作。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] HD-VGGT 在實驗中實際使用的 high-resolution 究竟是多少（$1036^2$、$1536^2$、$2048^2$？），對應的 token 總數、GPU memory peak 與單次前向 latency 與 baseline VGGT 相比為何？
- [ ] `HD-VGGT (w/o FM)` 在 Table 1–5 的所有指標上具體分別退步多少？若 FM 移除後與 baseline 差異微小，FM 的存在意義為何？
- [ ] §4.1 列出的高解析度 benchmark MVS-SYNTH 為何未出現在任何結果表？是訓練 / 評測未完成，還是結果不利於宣稱？
- [ ] §3.3.2 的 $M_{\text{refined}}$ 既需要模型已預測出 $r_{d,i}, r_{c,i}$，又被用來抑制 token 以改善預測——forward pass 中此循環如何被打破？是否需要二次 inference？若是，效率成本如何計算？
- [ ] Eq. 10 的 $\omega_{\text{shallow}} \odot \omega_{\text{middle}} \odot \omega_{\text{deep}}$ 三項元素積的具體理論依據為何？是否做過取單項、相加、log-sum 等替代形式的對比？
- [ ] Coarse branch 的姿態錯誤對最終 high-res 輸出的影響有多嚴重？是否有 case study 顯示低解析度誤判能否被 refiner 修正？
- [ ] 為何在 efficiency-focused 的論文中完全省略對 FastVGGT [7] 的比較？兩種方法是否能正交組合？

### 8.2 Improvement Directions

1. **補上 efficiency 量化表（最高優先、最容易）**：以 token 數、peak GPU memory、wall-clock latency、FLOPs 四欄列出 VGGT、$\pi^3$、FastVGGT、HD-VGGT 在相同視角數與輸入解析度下的表現；論文現有架構不需修改即可產出此表，且可立即支撐「scalable」claim。
2. **完整的 FM ablation 矩陣**：在 Table 1–5 每一資料集都加入 `w/o FM`、`w/o Upsampling`、`w/o HR branch`（僅 coarse branch）三欄，並將 anomaly mask 的可視化（page 6 描述但未呈現）放入 supplement，量化 §3.3 各設計的邊際貢獻。
3. **FM 改為可微 soft gating 並納入訓練**：將 Eq. 15 的 hard $1 - M_{\text{refined}}$ 改為可學習的 sigmoid gate，把 $S_{\text{anomaly}}$ 作為輸入特徵而非二值化 mask，使 backbone 在訓練時能反向學到「該降權的 token 樣態」，理論上可同時改善穩健性與消除 forward pass 中的循環依賴。
4. **加入對 specular / repetitive-texture 的 stress benchmark**：在 ScanNet 鏡面區、Replica 玻璃場景、或合成的 checkerboard 重複紋理上分別評測，並提供 anomaly mask 的 IoU 與 depth error 相關性，將 §3.3 從「修飾性章節」提升為「具有獨立量化證據的貢獻」。
5. **Cascaded refinement 而非 single coarse-to-fine**：將 dual-branch 推廣為 multi-scale pyramid（如 $518 \to 1036 \to 2072$），並在每階段間共享 Feature Upsampling 與 light refiner，可避免單次 $4 \times$ 升頻造成的細節幻覺，並讓 high-res 上限更可控。
6. **與 FastVGGT 的正交整合實驗**：FastVGGT 是 attention-level 加速、HD-VGGT 是 architecture-level 解耦，兩者不衝突；正交組合既可進一步壓低成本，也能客觀展示 HD-VGGT 的貢獻獨立於既有加速技巧。
