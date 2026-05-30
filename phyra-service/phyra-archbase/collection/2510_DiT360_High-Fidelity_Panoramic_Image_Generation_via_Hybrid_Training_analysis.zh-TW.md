<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# DiT360 — DiT360: High-Fidelity Panoramic Image Generation via Hybrid Training

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | DiT360 |
| Paper full title | DiT360: High-Fidelity Panoramic Image Generation via Hybrid Training |
| arXiv ID | 2510.11712 |
| Release date | 2025-10-13 |
| Conference/Journal | arXiv preprint (accepted to CVPR 2026) |
| Paper link (abs) | https://arxiv.org/abs/2510.11712 |
| PDF link | https://arxiv.org/pdf/2510.11712 |
| Code link | https://github.com/Insta360-Research-Team/DiT360 |
| Project page | https://fenghora.github.io/DiT360-Page/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Haoran Feng | Insta360 Research; Tsinghua University | https://fenghora.github.io/ (verified: https://fenghora.github.io/DiT360-Page/) | co-first author |
| Dizhe Zhang | Insta360 Research | — | co-first author; project lead |
| Xiangtai Li | Nanyang Technological University (S-Lab, MMLab@NTU) | https://lxtgh.github.io/ | co-author |
| Bo Du | Wuhan University, School of Computer Science | https://cs.whu.edu.cn/ | co-author |
| Lu Qi | Insta360 Research; Wuhan University | http://luqi.info/ | corresponding author |

### 1.2 Keywords

panoramic image generation, diffusion transformer, hybrid training, equirectangular projection, cubemap, circular padding, yaw loss, cube loss

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Peebles & Xie, 2023 (DiT) | base model | Diffusion Transformer architecture; DiT360 builds its hybrid panorama framework directly on the DiT backbone. |
| Black Forest Labs, 2024 (FLUX) | base model | FLUX DiT-based text-to-image model; provides the MSE training loss formulation and inpainting model used for panoramic refinement. |
| Rombach et al., 2022 (LDM / Stable Diffusion) | predecessor | Latent Diffusion Model that established VAE-latent denoising; conceptual predecessor for token-level supervision in DiT360. |
| Su et al., 2024 (RoPE) | influence | Rotary Positional Embedding mechanism that DiT360 exploits for position-aware circular padding at the token level. |
| Chang et al., 2017 (Matterport3D) | influence | Primary panoramic training/eval dataset; its polar blurring artifacts directly motivate DiT360's panoramic refinement. |
| Ye et al., 2024; Huang et al., 2025; Kalischek et al., 2025 (cubemap-based panorama generators) | baseline | Cube-mapping panorama generation baselines compared against and improved upon for boundary continuity and fidelity. |
| Zhang et al., 2024; Sun et al., 2025; Park et al., 2025 (ERP-based panoramic diffusion) | baseline | Equirectangular-projection panoramic diffusion baselines; DiT360 surpasses them on Matterport3D quantitative metrics. |

## 2. Research Overview

### 2.1 Research Topic

本研究聚焦於高保真 360° 全景影像生成 (panoramic image generation),屬於電腦視覺中文生圖 (text-to-image) 的延伸領域。作者觀察到既有方法多侷限於模型結構設計,卻無法克服極區嚴重畸變、0°/360° 邊界不連續以及真實感不足等問題,根本原因在於高品質真實全景資料的稀缺。為此,他們提出 DiT360,一個基於 Diffusion Transformer (DiT) 的混合訓練框架,將大量精選的 perspective 影像與有限的 panoramic 資料聯合訓練,在 pre-VAE 影像層級進行跨域轉換 (cubemap 重投影、極區 inpainting refinement),並在 post-VAE token 層級加入 circular padding、yaw loss 與 cube loss,以同時提升幾何保真度 (geometric fidelity) 與感知真實感 (photorealism),並原生支援 inpainting 與 outpainting 任務。

### 2.2 Domain Tags

- Computer Vision
- Generative Models
- Diffusion Models
- 360°/Panoramic Imaging

### 2.3 Core Architectures Used

- **Diffusion Transformer (DiT)**:作為 DiT360 的骨幹架構,負責在 post-VAE token 序列上以 transformer + RoPE 進行 latent 去噪,其顯式位置編碼正是 position-aware circular padding 得以在 token 層級成立的前提。
- **FLUX (DiT-based text-to-image)**:具體實例化的 base model,DiT360 在 FLUX 上以 LoRA 注入 attention 層進行微調,並沿用其 MSE flow-matching 損失作為 perspective 與 panoramic 分支的主要監督訊號。
- **FLUX.1 Kontext inpainting model**:用於 panoramic refinement 階段,對 cubemap 頂/底面中央被遮罩的極區進行重建,藉由 perspective 域的 inpainting 先驗清除 Matterport3D 既有的極區模糊。
- **VAE (latent autoencoder, 沿用自 LDM 體系)**:將 ERP 全景影像壓縮到 latent token 空間,使後續 circular padding、yaw loss、cube loss 等 token-level 監督得以在低維潛空間中執行。
- **Equirectangular Projection (ERP) 與 Cubemap (CP) 兩種全景表示**:同時被當作資料表示與監督介面,ERP 維持全域連續性供主要去噪使用,Cubemap 則作為 perspective image 重投影的目標、panoramic refinement 的中介、以及 distortion-aware cube loss 的監督空間。
- **LoRA (Low-Rank Adaptation)**:套用於 FLUX attention 層,讓大型預訓練 DiT 能在有限全景資料下進行參數高效率的領域適配,而不破壞 perspective 預訓練先驗。

### 2.4 Core Argument

作者主張,既有全景影像生成方法在邊界連續性、極區畸變與真實感上的弱點,根本原因不在模型結構,而在於「高品質、真實世界的全景訓練資料嚴重稀缺」,大多數方法因此只能依賴像 Matterport3D 這類有極區模糊瑕疵的合成或受限資料集,並過度依賴模擬數據。基於此資料中心 (data-centric) 的診斷,他們認為合理的解法不是再去設計新的卷積或注意力結構,而是讓模型「同時」學習兩種互補的資料來源:一方面利用網路上規模龐大、高真實感的 perspective 影像,將其視為 cubemap 的側面 (lateral face) 重投影回 ERP 空間,以遮罩方式提供跨域的真實感監督;另一方面對既有 Matterport3D 全景進行 cubemap 化,並在頂/底面中心區套用 inpainting 模型修復極區模糊,得到乾淨的全景訓練樣本。然而,單純混入兩域資料不足以強制模型學到正確的全景幾何性質,因此作者進一步在 post-VAE 的 token 空間設計三個幾何感知監督:position-aware circular padding 利用 DiT 顯式 RoPE 編碼的特性,讓 0°/360° 邊界 token 能直接交換特徵,確保水平環繞連續;rotation-consistent yaw loss 約束模型在隨機 yaw 旋轉下預測一致的雜訊,提供全域旋轉穩定性;distortion-aware cube loss 將雜訊投影到 cube 面上做面向式 MSE 監督,把 perspective 先驗轉移到全景域以準確還原極區畸變。三者與 perspective MSE 一起構成 hybrid loss,作者因而論證:唯有同時在影像層級 (跨域轉換+資料淨化) 與 token 層級 (旋轉/邊界/畸變幾何約束) 雙管齊下,才能在資料稀缺前提下,邏輯上必然地解決全景生成的真實感與幾何保真度兩難。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(210 words)

標題 "DiT360: High-Fidelity Panoramic Image Generation via Hybrid Training" 一次性宣告了三件事:採用 DiT 架構作為 backbone、處理 panoramic image generation 任務、核心方法是 hybrid training。Abstract 緊接著把作者的 framing 拉到一個與多數先前工作不同的角度:他們把 panoramic generation 在 geometric fidelity 與 photorealism 上的瓶頸,主要歸因於「缺乏大規模、高品質、真實世界的全景資料」,而非模型架構不足,這是一個 data-centric 的視角,作者在 abstract 開頭就明白和「focus on model design」的前人作品劃清界線。

接著 abstract 給出 DiT360 的方法骨架:在 image level (pre-VAE) 與 token level (post-VAE) 兩個 representation level 上同時操作 inter-domain transformation 與 intra-domain augmentation。Image level 包含 perspective image guidance 與 panoramic refinement;token level 則由 circular padding (boundary continuity)、yaw loss (rotational robustness)、cube loss (distortion awareness) 三個 hybrid supervision 組成。每個模組都對應一個明確的幾何或感知層面的問題,這種「模組對應問題」的列舉方式為後續章節建立了讀者的閱讀骨架。

Abstract 收尾以三個下游任務 (text-to-panorama、inpainting、outpainting) 與「eleven quantitative metrics」上的勝出作為 empirical claim,並提供 GitHub 連結。整體而言,abstract 同時設定了 problem framing (data scarcity)、解法 framing (hybrid training across two representation levels) 與驗證 framing (多任務、多指標),為 §1 Introduction 的展開鋪好路。

### 3.2 Introduction

(780 words)

Introduction 由四個遞進的段落構成,把 abstract 的論點展開為完整的 motivation。第一段把 panoramic image generation 放進 spatial intelligence 與 360° FoV 應用 (AR/VR、autonomous driving) 的脈絡,並指出與 perspective image generation 相比,polar regions 的 severe distortions 是阻礙部署的關鍵特性。第二段隨即盤點現有解法,以 ERP 與 cubemap (CP) 為兩條主線,作者刻意列出大量引用以證明此分類已被廣泛探索,接著用一句 "Despite the success achieved" 作為 pivot,指出真正瓶頸在於「real-world panoramic data 的稀缺與對 simulated data 的過度依賴」,這一句把 framing 從 model design 切換到 data-centric。

第三段是論文的 motivation 核心:作者指出「直接從 YouTube 等媒體平台抓 360° 資料」這個 heuristic 並不可行,因為缺少 horizon correction 與 aesthetic filtering 等 domain-specific curation,於是提煉出全篇核心問題 — 「在 panoramic 資料有限的情況下,如何讓模型獲得 real-world knowledge?」這個 research question 的形式是論文行文的關鍵 hinge,讓讀者明確知道後續方法必須回答這一個問題。

第四段給出 DiT360 的 hybrid training 解答結構,並把 abstract 中提到的兩層架構展開為更具體的職責分工:image level 負責 cross-domain regularization,以 masking + inpainting 修整既有 panoramic data 的 polar artifacts,並透過 projection-aware 方法把 perspective 資料投影到 panoramic space 作為 photorealistic guidance;token level 則在 latent space 進行 geometry-aware supervision,包括處理 ERP 邊界週期性 (0°/360° longitude) 的 circular padding、確保 global rotational consistency 的 yaw loss、以及補足 ERP supervision 不足的 distortion-aware cube loss。

最後兩段把貢獻收束為三點:(1) 提出 hybrid training framework,把焦點從 model design 移到 multi-domain data utilization;(2) 將 hybrid 概念拆解為 image-level regularization 與 token-level supervision 的多層次機制;(3) 在 text-to-panorama、inpainting、outpainting 三個任務上以多指標驗證優勢,並輔以 user study 證明對齊人類偏好。Introduction 還預先點名了在 Matterport3D validation set 上以 FID、Inception Score、BRISQUE 等九項指標達到 SOTA 的具體成果,並強調 inpainting/outpainting 不需額外 finetuning 即支援,以及方法天生具備 high-resolution photo-realistic 生成能力。

整段 introduction 為後續章節舖了三條伏筆:Related Work 必須對比 ERP-only、CP-augmented 與 stitching-based 三類方法的取捨;Method 必須具體交代 image-level 與 token-level 模組的數學形式;Experiments 必須在多個指標與任務上驗證 photorealism 與 geometric fidelity 同時兼得的主張。

### 3.3 Related Work / Preliminaries

(870 words)

Related Work 由兩個主題段組成,搭配 §3.1 中的 DiT preliminaries,共同為後續方法章節建立比較基準與技術詞彙。第一個主題段 "Text-to-Image Diffusion Models" 沿著 LDM → UNet → DiT 的演進脈絡推進,先把 diffusion 確立為取代 VAE 與 GAN 的主流 paradigm,再說明 latent space denoising 如何讓高解析度生成變得可行,最後指出 transformer-based 結構透過 explicit positional encoding 與 attention 操作獲得更佳 scalability。這段的結尾 framing 至關重要:作者明確指出 UNet 與 transformer 兩類結構都「依賴大規模的 perspective dataset」,從而合理化 DiT360 利用 perspective 資料補償 panoramic 資料不足的選擇,並把 inter-domain transformation 與 projection 設定為自然的橋梁。

第二個主題段 "Panoramic image Generation" 的結構更為複雜,作者把這條子領域切成三個世代:(1) 早期的 outpainting-based 方法,從 NFoV 拼回 360°,但內容多樣性有限;(2) text-to-panorama 興起後分化為兩條路線 — 多視角 perspective 拼接,常因物件重複與不連續而 perceptual realism 不足;以及 cubemap-based 方法,雖然較貼合 spherical geometry,但 cube faces 之間仍有 discontinuity,且帶來額外的計算與時間成本;(3) 直接在 ERP 上訓練的方法,雖能保留 global continuity 並讓模型學習 distortion patterns,卻在 0°/360° boundary alignment 與 polar region distortion 上仍然吃緊。作者特別點名近期 SMGD、SphereDiff、PanFusion 等試圖以 alternative convolution 解決問題的方法,指出它們「在實務上仍受限,且與 pretrained 模型的相容性較差」,這一句話為 DiT360 選擇 LoRA-on-Flux 而非改動 backbone 的設計埋下動機。最後段落總結:所有上述方法都受到 panoramic dataset 品質的限制,常常 inherit polar degradation 與 rendered-like appearance,從而把 framing 帶回 introduction 提出的 data-centric 觀點。

§3.1 的 "Revisit Diffusion Transformer" 在進入 method 章節前先建立 preliminaries:DiT 對 post-VAE image tokens $X \in \mathbb{R}^{N \times d}$ 進行 transformer 處理,N 為序列長度、d 為 embedding 維度;以 Rotary Positional Embeddings (RoPE) 注入 coordinate-dependent rotation,使模型能編碼 relative 與 absolute 位置資訊;並採用 flow-based scheduler 進行 progressive denoising。標準訓練目標是 denoising score-matching loss

$$L = \mathbb{E}_{X,c,\epsilon,t}\left[\|\epsilon - \epsilon_\theta(X_t, c, t)\|_2^2\right]$$

其中 $X_t$ 為時間步 t 的 noisy latent、$\epsilon$ 為加入的 Gaussian noise、$\epsilon_\theta$ 為模型預測的 noise。這段 preliminaries 為後續 §3.2、§3.3 中的 perspective MSE loss、yaw loss、cube loss 提供了統一的 noise-space supervision 框架,也讓讀者看見 RoPE 與 token reshape 是 circular padding 的技術前提。整體而言,這個合併的「Related Work + Preliminaries」段落同時做完了「定位差異」與「準備記號」兩件事,為 method 章節的展開提供了乾淨的入口。

### 3.4 Method (overview narrative)

(1480 words)

Method 章節的第一頁先交代整體 narrative,而不立刻進入個別模組細節。作者把 DiT360 框架切成兩個 complementary 的視角:image-level regularization (§3.2) 與 token-level supervision (§3.3),並聲明 §3.4 將展示同一 framework 如何 natively 支援 inpainting 與 outpainting,而不需額外 finetuning。Fig. 2 的 pipeline 圖把這個結構視覺化:perspective branch 先做 (a) perspective image re-projection 把 perspective 知識轉到 panoramic domain;panoramic branch 先做 (b) panoramic refinement 移除 polar blurring,接著在 token 端施加 (c) position-aware circular padding、(d) rotation-consistent yaw loss、(e) distortion-aware cube loss 三項 token-level hybrid supervision。

§3.1 的 Overview of DiT360 段落把 abstract 與 introduction 的 framing 用一句話收束:DiT360 採用 hybrid paradigm,透過兩個 training branches 同時利用 perspective 與 panoramic data,模組分為 image-level regularization 與 token-level supervision。Image level 的職責被定義為「跨 domain 知識引入,以 enhance perceptual quality 同時 regularize diversity 與 photorealism」;token level 則被定義為「跨多目標的 hybrid supervision,涵蓋 boundary continuity、rotational robustness、distortion awareness」。這段 overview 對方法給出一個 mapping 表 — 每個目標都對應一個明確的模組,讓讀者能在閱讀後續細節時帶著清晰的 mental model。

§3.2 的 Image-level regularization 由兩個子模組構成。Panoramic image refinement 處理的是 Matterport3D 等大規模 dataset 中 polar regions 模糊的問題:作者把 ERP 轉成 cubemap,在 top/bottom 兩個 face 的中心區域 (1024 解析度下為 256 ≤ u, v < 768) 上一個 binary mask M,把該區域填白後送入 perspective-domain inpainting 模型 (Flux Kontext) 重建,再投影回 ERP。這個流程被定義為一種 image-quality regularization step,在保留固有 distortion 特性的同時換取更乾淨的 training images。Perspective image guidance 則是雙向的另一半:把 Internet landscape image 視為 cubemap 的 lateral face,投影回 ERP 並產生對應 mask,以僅在 mask 區域生效的 MSE loss 注入訓練。作者特別說明為何只用 lateral faces — top/bottom 通常對應 sky 或 ground 的特殊視角,在 dataset 中覆蓋率太低。

§3.3 的 Token-level supervision 給出三個機制。Position-aware Circular Padding 利用 DiT 中 positional encoding 與 image content 的對應關係,在 VAE 壓縮並注入 noise 後把 latent token 從 $\mathbb{R}^{N \times d}$ reshape 成 $\mathbb{R}^{H \times W \times d}$,沿 width 維度把首尾 column 串接成 $\tilde{X}_t = [X_{-1}, X_t, X_0] \in \mathbb{R}^{H \times (W+2) \times d}$,positional encoding 也同步施加同樣操作,使模型學到 0°/360° boundary 兩端 column 的視覺一致性。Rotation-consistent Yaw Loss 隨機選取 yaw 角度 a,對 $X_t - \epsilon$ 與 $\epsilon_\theta$ 都做 yaw rotation 後計算 MSE,以 token-level supervision 強迫預測在不同 viewing angle 下保持一致。Distortion-aware Cube Loss 把 sampled noise 與 predicted noise 都 project 到 cube faces 上做 face-wise supervision,作者明確說明此設計是為了「把模型在 perspective priors 上的優勢轉移到 panoramic domain」,避免 ERP 上直接監督只會 reproduce distorted appearance 而非結構。值得一提的是,作者特別解釋為何 yaw loss 與 cube loss 都施加在 noise space 而非 latent token space — 因為 diffusion objective 本身已耦合 noise 與 semantics,且 noise space 與 flow-based scheduler 的對齊讓訓練更穩定。三個 supervision 透過 hybrid loss

$$L_{\text{pano}} = L_{\text{MSE}} + \lambda_1 L_{\text{cube}} + \lambda_2 L_{\text{yaw}}$$

組合,以 Flux 原本的 MSE loss 作為主項,輔以 cube loss 與 yaw loss。

§3.4 的 More Applications 用一段話交代延伸能力:藉由 inversion-based feature replacement (Feng et al., 2025),DiT360 可在 inpainting 與 outpainting 任務上 zero-shot 運作,且全程訓練皆在 1024×2048 解析度進行,使 high-resolution 生成成為原生屬性。這個收尾為 introduction 中「naturally supports inpainting and outpainting without additional finetuning」的承諾兌現,並引導讀者進入 §4 的實驗驗證。

### 3.5 Experiments (overview narrative)

(720 words)

Experiments 章節以三段式結構展開:Setup (§4.1)、Main Results and Comparisons (§4.2)、Ablation Study (§4.3)。Setup 段落交代了三個關鍵設定:其一是 model 基底 — DiT360 建構於 Flux 之上,以 LoRA 注入 attention layers,而非全參數 finetune,呼應 Related Work 中對 alternative convolution 與 pretrained model 相容性的批評;其二是 hybrid training 的資料組合 — 高品質 Internet landscape images 配合 Matterport3D 的大規模 panoramas;其三是 metrics 的多元覆蓋 — 涵蓋 realism、diversity、text-image alignment、perceptual quality 四個面向,作者強調這是為了「ensure a comprehensive assessment」,而非偏袒單一指標。完整的 implementation details、dataset preprocessing、metric 定義被推到 Appendix C,主文僅保留高層次描述。

§4.2 的 Main Results 與 baselines 列表呈現了一份頗具廣度的對手清單:PanFusion、MVDiffusion、SMGD、PAR、WorldGen、Matrix-3D、LayerPano3D、HunyuanWorld,涵蓋 stitching-based、ERP-based、cubemap-based 與大規模 synthetic data 路線。Qualitative comparison 透過 Fig. 4 的 red box 標註各 baseline 的代表性 artifacts,行文上把對手分成幾類分別評論:SMGD 與 PAR 因 structural modification 或 autoregression 而在 detail fidelity 上失利;Matrix-3D 雖改善 boundary alignment 卻在 fine-grained details 上 struggle;LayerPano3D 與 HunyuanWorld 仰賴大量 synthetic data,雖提高 geometric fidelity 卻產生 render-like appearance,且 iterative denoising 引入額外 artifacts。最終定位 DiT360 同時兼得 high perceptual realism 與 geometric fidelity。Quantitative comparison (Tab. 1) 報告 11 項指標,作者主張在「nearly all benchmarks 中排名第一」,並對少數略遜的指標 (CLIP Score、Q-Align 的 quality branch) 給出技術解釋 — 這兩個 metric 是為 perspective image 設計,可能未能完整反映 panorama 品質,這個解釋在邏輯上把 quantitative 結果的小瑕疵預先消化。

§4.3 的 Ablation Study 以 Flux + LoRA 為 baseline,逐項加入 circular padding、cube loss、yaw loss、perspective image guidance 四個模組,並在 Tab. 2 與 Fig. 5 上呈現結果。每個模組的解釋都對應一個機制理由:circular padding 因 left/right edge 共享 positional encoding 而提升邊界 consistency,反映在 FID 與 BRISQUE 的下降;cube loss 對 cubemap representation 的監督減少 polar artifacts,並反映在 IS、CS 等與 visual semantics 相關的 metric;yaw loss 強化 global rotation consistency,因此在 FAED (autoencoder pretrain on panoramas) 上表現最佳;perspective image guidance 則在 QAquality 與 QAaesthetic 等對 visual style 較敏感的 metric 上獲益。整段 ablation 的收尾把四個模組視為互補,證明它們的組合才能同時兼顧 perceptual realism 與 geometric fidelity。Experiments 章節整體在主文中刻意保持 narrative 層次,不細究每個指標的數值差距,把詳盡的 user study (Sec. E)、額外結果 (Sec. F) 與 implementation details (Sec. C) 都推到 Appendix,讓主文的論證流暢度優先於資料密度。

### 3.6 Conclusion / Limitations / Future Work

(290 words)

Conclusion 段落把全篇收束於三個 framing:(1) DiT360 是一個 geometry-aware 且 photorealistic 的 panoramic image generation framework,(2) 其核心在於 hybrid training 結合有限的高品質 panoramic data 與大規模 perspective images,以同時提升 realism 與 generalization,(3) 透過跨多個 representation level 的模組設計 — image-level regularization 處理 panorama 修整與 perspective knowledge 注入,token-level supervision 透過 rotation-aware 與 distortion-aware constraints 強化 latent space 中的 geometric consistency。作者把實驗成果定位為「在 text-to-panorama、inpainting、outpainting 上展現 superior image fidelity、boundary consistency、visual quality」,並把 DiT360 的角色提升為「為 3D scene generation 與 large-scale open-world environments 的後續研究建立 strong baseline」,把方法 framing 從單一任務工具升格為基礎設施。

Limitations 與 Future Work 被放在 Appendix H,坦承幾個 honest 的弱點:模型效能受到 dataset 多樣性與規模限制,在 high-resolution human faces 或 intricate scene details 等場景仍 suboptimal。Future work 給出三條路線:(1) 收集更大、更多元的高品質 dataset,直接拉高 generative capability 與 image resolution;(2) 利用 synthetic data augment training samples,進一步推進 panoramic image generation;(3) 把 framework 延伸到 three-dimensional scene generation 與理解,作為長期研究方向。這個排序與 Conclusion 中「strong baseline for future research in 3D scene generation」的承諾互相呼應,把 panoramic generation 定位為 3D 世界生成的中介步驟。整體收尾的 framing 一致 — data-centric 視角貫穿從 introduction 的問題提出、method 的 hybrid training 解法、到 future work 的 dataset 擴張與 3D 延伸,讓全篇呈現首尾扣合的論述結構。

## 4. Critical Profile

### 4.1 Highlights

- DiT360 在 Matterport3D 文生全景驗證集上於 11 個指標中拿下 9 項第一,FID 由 SMGD 的 46.72 降至 42.88,展現量化指標的整體領先 (Tab. 1, p. 7)。
- 針對極區的 FIDpole 由次佳的 60.16 (cube loss 單獨情境) 大幅降至 50.88,直接驗證了 polar refinement + cube loss 對極區畸變的修復效果 (Tab. 1, p. 7)。
- BRISQUE 從 Matrix-3D 的 16.37 降到 10.25,NIQE 從 LayerPano3D 的 3.79 降到 3.72,顯示無參考感知品質也同步提升 (Tab. 1, p. 7)。
- 使用者研究中 63 位受測者於「整體品質」項給出 80.9% 偏好率,大幅高於 HunyuanWorld 的 13.7% 與 Matrix-3D 的 5.1%,人類偏好與量化指標一致 (Tab. 3, p. 18)。
- 採取 data-centric 而非 architecture-centric 視角:將 panorama 生成困境歸因於高品質真實全景資料稀缺,而非新模型結構,並用混合 perspective + panorama 訓練回應 (§1, p. 2)。
- 位置感知的 circular padding 巧妙利用 DiT 內含 RoPE 的特性,在 token level 直接交換 $X_0$ 與 $X_{-1}$ 邊界欄,讓 0°/360° 邊界連續性「自然」由位置編碼學到 (§3.3, p. 6)。
- 針對 Matterport3D 既有極區模糊瑕疵,將 ERP 轉成 cubemap 後對 top/bottom 中心 256–768 區域以 Flux inpainting 修復再投影回 ERP,把資料淨化納入 pipeline (Fig. 3, p. 5; Eq. 2, p. 5)。
- 提出在 noise 空間 (而非 latent 空間) 計算 yaw loss 與 cube loss,並論證 noise 已耦合語意與結構,與 flow-based scheduler 在訓練穩定性上更相容 (§3.3 末, p. 7)。
- 模型原生支援 1024×2048 解析度生成,並透過 inversion + token replacement 不需額外微調即可進行 inpainting/outpainting (§3.4, p. 7; Fig. 7, p. 16)。
- ablation 中 circular padding 單獨將 FID 由 46.69 降到 43.71、BRISQUE 由 17.02 降到 13.61,顯示單一 token-level 機制即帶來顯著邊界連續性增益 (Tab. 2, p. 9)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 模型受限於可用資料集的多樣性與規模,在高解析度人臉與細節密集場景表現不佳;作者點出未來需收集更大規模、多樣化的高品質資料集 (§H Limitations, p. 18)。
- 作者承認「同步合成資料」雖可擴增訓練樣本,但目前框架尚未涵蓋此面向,並提出延伸至 3D 場景生成與理解作為長期方向 (§H Limitations, p. 18)。

#### 4.2.2 Phyra-inferred

- **訓練與驗證皆來自 Matterport3D**,且 polar refinement 又是針對 Matterport3D 特有的極區模糊用 Flux 修補後再餵回訓練,這構成資料管線與測試集之間的耦合,使 Tab. 1 的領先難以排除「對單一資料集瑕疵過擬合」(§C Dataset, p. 15; Tab. 1, p. 7)。
- **遺漏直接的 cubemap 競品 CubeDiff (Kalischek et al., 2025)**:該方法在 lineage 中被列為 baseline,但 Tab. 1 並未實測比較,空缺正好落在 DiT360 主打的 cubemap 對齊強項上 (Tab. 1, p. 7 vs §2 末, p. 3)。
- **CLIP Score 與 QAquality 落後被一句話帶過**,作者歸因為「這些指標為 perspective 設計」,但他們自身就大量使用 perspective 資料訓練,這個解釋與其 hybrid training 主張內部矛盾 (§4.2 Quantitative, p. 8)。
- **核心超參數 $\lambda_1, \lambda_2$ 數值未公開**,Eq. 10 引入的 hybrid loss 的權衡完全留白,複現性與敏感度分析雙雙缺失 (Eq. 10, p. 7; §C Implementation Details, p. 15)。
- **cube/yaw loss 在 noise 空間而非 latent 空間的選擇,僅以「實驗顯示」帶過**,沒有提供 noise vs latent 的對照 ablation,讓「noise 已耦合結構」這個論點停留在敘述而非證據 (§3.3 末, p. 7)。
- **使用者研究樣本僅 63 人,無 inter-rater agreement、無置信區間**,卻得出 80.9% 這種接近一面倒的結果,缺乏統計可信度交代 (§E, p. 18)。
- **perspective 分支只用網路 landscape 圖**,而 Matterport3D 是室內 RGB-D 資料集,兩域之間的 scene-type mismatch 並未被分析,對「perspective 知識真的轉移成功」的說法是個沒處理的空隙 (§C Dataset, p. 15)。

### 4.3 Phyra's Judgment (summary)

DiT360 真正新穎之處是把 panorama 生成的瓶頸重新定義為資料問題,並以 hybrid training + RoPE 感知的 token-level 幾何監督做出一個自洽的工程方案;circular padding 與 cube loss 的設計具備直觀理論基礎並有 ablation 支撐。但混合資料 + 極區 inpainting + Flux LoRA 三者在實作上強耦合於 Matterport3D 與 Flux 生態,所有量化結果皆於同一資料集上產出,因此「方法本身的可遷移性」與「指標領先究竟來自方法還是資料淨化」這兩個核心問題至今未被實驗區分開來。換言之,本文是一個說服力強的 single-dataset SOTA,但尚未證明它是 panorama 生成的 general framework。

## 5. Methodology Deep Dive

### 5.1 Method Overview

DiT360 是建立在 FLUX (Black Forest Labs, 2024) DiT backbone (Peebles & Xie, 2023) 上的全景影像生成框架，採用 LoRA (Hu et al., 2021) 注入 attention layers 以 fine-tune。整體訓練包含 perspective 與 panoramic 兩個 branch，並在 pre-VAE 影像層級與 post-VAE token 層級分別注入互補的監督機制 (paper §3)。模型基底沿用 DiT 的 latent sequence 表示 $X \in \mathbb{R}^{N \times d}$ ，其中 $N$ 為序列長度、 $d$ 為 embedding dimension，並採用 RoPE (Su et al., 2024) 為位置編碼，搭配 flow-based scheduler 進行漸進去噪。所有訓練在 1024×2048 ERP 解析度下進行 (paper §3.4)。

在 image level (pre-VAE) 上，DiT360 同時做 *跨域轉換 (inter-domain transformation)* 與 *內域增強 (intra-domain augmentation)*：(a) **perspective image guidance** 將高品質 internet perspective 影像視為 cubemap 的某個 lateral face，重投影回 ERP 空間並配合 mask 做 MSE 監督，把 photorealism 知識轉移到全景域；(b) **panoramic refinement** 將 Matterport3D ERP 全景拆成 cubemap，對 top/bottom 兩面中心區套用 perspective-domain inpainting model (Labs et al., 2025) 移除極區模糊瑕疵，再投影回 ERP 得到乾淨訓練樣本 (paper §3.2, Fig 3)。這兩個機制共同緩解高品質全景資料稀缺的問題。

在 token level (post-VAE) 上，DiT360 對 panoramic branch 的 noisy latent 加入三個 geometry-aware 監督 (paper §3.3, Fig 2c–e)：(c) **position-aware circular padding** 將 latent reshape 為 spatial grid 後，沿 width 維度以 $[X_{-1}, X_t, X_0]$ 拼接 (eq 5)，並對 RoPE 同步做相同 padding，讓 0°/360° 邊界 token 在注意力計算中可互相 attend；(d) **rotation-consistent yaw loss** 對隨機 yaw 角下的 noise 與 predicted noise 做 MSE (eq 6–7) ，強制全域 rotational robustness；(e) **distortion-aware cube loss** 把 noise 投影到 6 個 cube 面後做 face-wise MSE (eq 8–9)，把 perspective 先驗轉到全景域以準確還原極區畸變。三者與 panoramic 的標準 MSE 經 hybrid loss (eq 10) 線性組合：$L_{pano} = L_{MSE} + \lambda_1 L_{cube} + \lambda_2 L_{yaw}$ ，perspective branch 則使用 masked MSE $L_{perspective}$ (eq 4)。值得注意的是，cube/yaw loss 都在 latent noise space 而非 latent token space 計算，因為 noise prediction 已經編碼了豐富的 spatial 與 structural 資訊，且能與 flow-based scheduler 對齊以提升訓練穩定性 (paper §3.3 結尾段)。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input domains:
   ├→ Perspective image (Internet landscape):  [B, 3, H_p, W_p]   (resolution: paper does not specify)
   └→ Panoramic ERP (Matterport3D):             [B, 3, 1024, 2048]

Image-level Pre-VAE Regularization (paper §3.2)
─────────────────────────────────────────────────
  (a) Perspective branch — perspective image re-projection:
       perspective image [B, 3, H_p, W_p]
         ├→ treat as one cubemap lateral face
         └→ CubeMap → ERP with binary mask M
              ↳ ERP: [B, 3, 1024, 2048]   mask M: [B, 1, 1024, 2048]

  (b) Panoramic branch — panoramic refinement (Fig 3):
       Matterport3D ERP [B, 3, 1024, 2048]
         └→ ERP → CubeMap 6 faces:        [B, 6, 3, 1024, 1024]
              └→ Apply mask M(u,v) on top/bottom face centers (256 ≤ u,v < 768):
                  I_mask = I ⊙ M + (1-M)·I_miss
                    └→ Inpainting model (FLUX.1 Kontext, Labs et al. 2025):
                        refined cube faces [B, 6, 3, 1024, 1024]
                          └→ CubeMap → ERP:  [B, 3, 1024, 2048]   (blur-free)

Encoding (shared; paper §3.1)
─────────────────────────────────────────────────
  ERP [B, 3, 1024, 2048]
    └→ VAE Encoder:                        [B, C_lat, H_lat, W_lat]    (C_lat, H_lat, W_lat: ?)
         └→ Forward diffusion @ timestep t:
              X_t (noisy latent)
                └→ Patchify → tokens:      [B, N, d]                   (N, d: ?)
                     └→ Reshape to grid:   [B, H, W, d]   with H·W = N

Token-level Post-VAE Supervision (paper §3.3, Fig 2c–e)
─────────────────────────────────────────────────
  (c) Position-aware Circular Padding (eq 5):
        X_t [B, H, W, d]
          └→ concat([X_-1, X_t, X_0], dim=W) → X̃_t  [B, H, W+2, d]
              └→ same circular padding applied to RoPE pos. encoding
                  └→ DiT denoiser → ε_θ:   [B, H, W, d]

  (d) Rotation-consistent Yaw Loss (eq 6–7):
        sample yaw angle a ∈ [0, 360°)
          ├→ ε_yaw      = Rotate(X_t − ε, a)        [B, H, W, d]
          ├→ ε_{θ,yaw}  = Rotate(ε_θ, a)            [B, H, W, d]
          └→ L_yaw = E[‖ε_{θ,yaw} − ε_yaw‖²₂]       (scalar)

  (e) Distortion-aware Cube Loss (eq 8–9):
        ├→ ε_cube       = CubeMap(X_t − ε)          [B, 6, h_f, w_f, d]   (h_f, w_f: ?)
        ├→ ε_{θ,cube}   = CubeMap(ε_θ)              [B, 6, h_f, w_f, d]
        └→ L_cube = E[‖ε_{θ,cube} − ε_cube‖²₂]      (scalar)

  (panoramic) MSE objective (FLUX MSE):
        L_MSE = standard denoising MSE on ε vs ε_θ  (scalar)

  (perspective) Masked MSE (eq 4):
        L_perspective = L_MSE(ε ⊙ M, ε_θ ⊙ M)       (scalar)

Total panoramic-branch loss (eq 10):
        L_pano = L_MSE + λ₁·L_cube + λ₂·L_yaw       (λ₁, λ₂: paper does not specify)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Panoramic Image Refinement

**Function:** 將 Matterport3D ERP 全景的極區模糊以 cubemap-based inpainting 修復，產生 blur-free 的訓練樣本。

**Input:**
- Name: $I$ (single cube face from top/bottom)
- Shape: `[B, 3, 1024, 1024]`
- Source: Matterport3D ERP → `CubeMap(ERP)` 的 top/bottom face

**Output:**
- Name: $\hat{I}$ (refined cube face) → 重組為 blur-free ERP
- Shape: `[B, 3, 1024, 1024]` per face → 反投影後 `[B, 3, 1024, 2048]`
- Consumer: VAE encoder (作為 panoramic branch 的乾淨輸入)

**Processing:**

1. ERP → CubeMap，得到 6 個 face，每面 1024×1024 (paper §3.2, Fig 3)。
2. 對 top/bottom 兩個 face 定義 binary mask $M$ (eq 2)：中心 512×512 區為 0，其餘為 1。
3. 構造遮罩影像 $I_{mask} = I \odot M + (1-M) \cdot I_{miss}$ (eq 3)，其中 $I_{miss}$ 為同解析度的白圖。
4. 對 $I_{mask}$ 套用 inpainting model (FLUX.1 Kontext, Labs et al. 2025) 重建中心區，得到 $\hat{I}$。
5. 將 6 面 cubemap 反投影回 ERP 空間。

**Key Formulas:**

$$
M(u, v) = \begin{cases} 0, & \text{if } 256 \le u, v < 768 \\ 1, & \text{otherwise} \end{cases}
$$

$$
I_{mask} = I \odot M + (1 - M) \cdot I_{miss}
$$

**Implementation Details:**

- Inpainting backbone: FLUX.1 Kontext (Labs et al., 2025)。
- 固定 cube face 解析度 $H = W = 1024$；側面 4 face 不修改，僅修復 top/bottom 兩面。
- 此步驟為 image-quality regularization，同時保留 panorama 內在的 distortion 特性。

#### 5.3.2 Perspective Image Guidance

**Function:** 將高品質 perspective 影像視為 cubemap 的 lateral face，重投影到 ERP 空間並以 masked MSE 提供 photorealistic 監督，把 perspective 域知識轉移到全景域。

**Input:**
- Name: perspective image
- Shape: `[B, 3, H_p, W_p]` (paper does not specify $H_p, W_p$)
- Source: Internet 上篩選過的 landscape 影像

**Output:**
- Name: re-projected ERP $+$ binary mask $M$
- Shape: ERP `[B, 3, 1024, 2048]`，mask `[B, 1, 1024, 2048]`
- Consumer: VAE encoder → DiT → `L_perspective`

**Processing:**

1. 將 perspective 影像視為 cubemap 的某個 lateral face (Fig 2a)，並透過 cubemap → ERP 變換得到 re-projected ERP，同時產生對應的覆蓋 mask $M$。
2. 限制只投影到 lateral faces；top/bottom 因為對應 sky/ground 等罕見視角不採用。
3. 訓練時對 sampled noise $\epsilon$ 與 reparameterized predicted noise $\hat{\epsilon}_\theta$ 套用 mask 做 MSE，僅監督 mask 覆蓋區域以避免污染 panorama 其餘區域 (eq 4)。

**Key Formulas:**

$$
L_{perspective} = L_{MSE}(\epsilon \odot M, \hat{\epsilon}_\theta \odot M)
$$

**Implementation Details:**

- MSE 公式直接沿用 FLUX (Black Forest Labs, 2024) 的 denoising 公式 (eq 1)。
- mask $M$ 嚴格限制在 lateral face 對應的 ERP 區域，確保 cross-domain 監督只施加在合法範圍。
- 此設計在不需配對 panorama 監督下，將大規模 perspective 影像導入訓練，提升 generation diversity 與 photorealism。

#### 5.3.3 Position-aware Circular Padding

**Function:** 在 token 層級對 width 維度做 circular padding，並同步對 RoPE 位置編碼做相同 padding，讓 0°/360° 邊界 token 透過注意力直接互通，確保水平環繞的 seamless boundary。

**Input:**
- Name: noisy latent tokens $X_t$
- Shape: `[B, N, d]` → reshape → `[B, H, W, d]` (with $H \cdot W = N$；paper 未明示具體 $H, W, d$ )
- Source: VAE encoder + 噪聲注入 (forward diffusion @ timestep $t$)

**Output:**
- Name: padded tensor $\tilde{X}_t$
- Shape: `[B, H, W+2, d]`
- Consumer: DiT transformer layers (attention + feed-forward)

**Processing:**

1. 將 $X_t \in \mathbb{R}^{N \times d}$ reshape 為 $\mathbb{R}^{H \times W \times d}$ (paper §3.3, Fig 2c)。
2. 取首列 $X_0$ 與末列 $X_{-1}$。
3. 沿 width 維度 concat：$[X_{-1}, X_t, X_0]$ (eq 5)。
4. 對 RoPE positional encoding 做相同的 circular concat，確保位置語義與 token 一致對齊。
5. Padded tensor 進入 DiT 主幹。

**Key Formulas:**

$$
\tilde{X}_t = \bigl[X_{-1},\; X_t,\; X_0\bigr] \in \mathbb{R}^{H \times (W+2) \times d}
$$

**Implementation Details:**

- 沒有引入額外架構複雜度，與 pretrained DiT 完全相容 (paper §3.3)。
- 利用 DiT 顯式 RoPE 的特性：相同 spatial position 的 latent token 會產生一致 visual feature，因此左右邊界 column 經 padding 後可學到 boundary correspondence。
- 具體 $H, W, d$ 數值論文未明示。

#### 5.3.4 Rotation-consistent Yaw Loss

**Function:** 對隨機 yaw 軸旋轉後的 noise 與 predicted noise 做 MSE，強制模型在 spherical yaw rotation 下產生一致的預測，提供全域 rotational robustness。

**Input:**
- Name: $X_t$, sampled noise $\epsilon$, predicted noise $\epsilon_\theta$, random yaw angle $a$
- Shape: $X_t, \epsilon, \epsilon_\theta$ 為 `[B, H, W, d]`；$a$ 為純量 ($a \in [0, 360°)$ )
- Source: forward diffusion (產生 $X_t, \epsilon$ ) 與 DiT denoiser (產生 $\epsilon_\theta$ )

**Output:**
- Name: yaw-rotated noise targets $\epsilon_{yaw}$ 與 $\epsilon_{\theta, yaw}$；最終 scalar loss $L_{yaw}$
- Shape: rotated tensors `[B, H, W, d]`；loss 為 scalar
- Consumer: 加入 hybrid loss (eq 10) 反向傳播至 DiT

**Processing:**

1. 隨機採樣一個 yaw 角 $a$ (paper §3.3)。
2. 計算 $\epsilon_{yaw} = \text{Rotate}(X_t - \epsilon, a)$ (eq 6)。
3. 計算 $\epsilon_{\theta, yaw} = \text{Rotate}(\epsilon_\theta, a)$ (eq 6)。
4. 計算 MSE 得 $L_{yaw}$ (eq 7)。
5. `Rotate(·, a)` 表示將 ERP panorama 沿 yaw 軸旋轉 $a$ 度。

**Key Formulas:**

$$
\epsilon_{yaw} = \text{Rotate}(X_t - \epsilon,\; a), \quad
\epsilon_{\theta, yaw} = \text{Rotate}(\epsilon_\theta,\; a)
$$

$$
L_{yaw} = \mathbb{E}\!\left[\,\|\epsilon_{\theta, yaw} - \epsilon_{yaw}\|_2^2\,\right]
$$

**Implementation Details:**

- 在 latent **noise** space (而非 latent token space) 計算，與 flow-based scheduler 對齊以提升訓練穩定性 (paper §3.3 結尾)。
- yaw 角 $a$ 為訓練時隨機採樣；具體採樣分布論文未明示。
- 設計動機：標準 diffusion loss 無法捕捉 yaw 旋轉的 non-linear 影響，此 loss 強制模型在不同 viewing angle 下預測一致。

#### 5.3.5 Distortion-aware Cube Loss

**Function:** 將 noise 與 predicted noise 投影到 6 個 cube 面後做 face-wise MSE，把 perspective 先驗轉移到全景域以準確還原極區畸變模式。

**Input:**
- Name: $X_t$, $\epsilon$, $\epsilon_\theta$
- Shape: 各為 `[B, H, W, d]` (latent grid)
- Source: forward diffusion (產生 $X_t, \epsilon$ ) 與 DiT denoiser (產生 $\epsilon_\theta$ )

**Output:**
- Name: cube-space targets $\epsilon_{cube}, \epsilon_{\theta, cube}$ 與 scalar $L_{cube}$
- Shape: `[B, 6, h_f, w_f, d]` (face latent 解析度 $h_f, w_f$ paper does not specify)；loss 為 scalar
- Consumer: 加入 hybrid loss (eq 10) 反向傳播至 DiT

**Processing:**

1. 對 $X_t - \epsilon$ 套用 `CubeMap(·)` 變換得到 $\epsilon_{cube}$ (eq 8)。
2. 對 $\epsilon_\theta$ 套用相同變換得到 $\epsilon_{\theta, cube}$ (eq 8)。
3. 計算 face-wise MSE 得 $L_{cube}$ (eq 9)。
4. `CubeMap(·)` 將 ERP panorama 轉為 6 個 cube 面表示。

**Key Formulas:**

$$
\epsilon_{cube} = \text{CubeMap}(X_t - \epsilon), \quad
\epsilon_{\theta, cube} = \text{CubeMap}(\epsilon_\theta)
$$

$$
L_{cube} = \mathbb{E}\!\left[\,\|\epsilon_{\theta, cube} - \epsilon_{cube}\|_2^2\,\right]
$$

**Implementation Details:**

- 同樣在 latent **noise** space 計算，作者實驗指出 noise prediction 已編碼足夠的 spatial/structural 資訊，且與 flow-based scheduler 對齊更穩定 (paper §3.3 結尾)。
- 直接對 ERP 做監督容易讓模型只複製類似 distorted appearance，而非學到正確的 structural pattern；投影到 cube 面後做 face-wise 監督能傳遞 perspective 域的精確結構先驗。
- ablation 顯示此 loss 顯著減少極區 artifact，並提升 IS 與 CS 等與視覺語意相關的指標 (paper Table 2)。

#### 5.3.6 Hybrid Loss Design

**Function:** 將 panoramic branch 的 MSE 主要 objective 與 cube / yaw 兩個輔助 loss 線性組合，平衡 geometric fidelity 與 perceptual quality；perspective branch 另以 masked MSE 提供跨域監督。

**Input:**
- Name: $L_{MSE}$, $L_{cube}$, $L_{yaw}$ (panoramic branch)；$L_{perspective}$ (perspective branch)
- Shape: 皆為 scalar per batch
- Source: §5.3.3–§5.3.5 模組以及 §5.3.2 perspective guidance

**Output:**
- Name: $L_{pano}$ (panoramic branch total) 與 $L_{perspective}$
- Shape: scalar
- Consumer: optimizer (FLUX 主幹 + LoRA on attention layers，AdamW 風格訓練)

**Processing:**

1. 在 panoramic branch iteration 中，計算 $L_{MSE}, L_{cube}, L_{yaw}$ 並依 eq 10 加權合併。
2. 在 perspective branch iteration 中，計算 masked MSE $L_{perspective}$ (eq 4)。
3. 兩個 branch 在 hybrid 訓練流程中交替/混合更新 LoRA 權重 (paper §3, §4.1)。

**Key Formulas:**

$$
L_{pano} = L_{MSE} + \lambda_1\, L_{cube} + \lambda_2\, L_{yaw}
$$

**Implementation Details:**

- Backbone: FLUX (Black Forest Labs, 2024) + LoRA (Hu et al., 2021) 注入 attention layers (paper §4.1)。
- 訓練資料: Internet 高品質 landscape (perspective) + Matterport3D (panorama, Chang et al., 2017)。
- 訓練解析度: 1024×2048 ERP，所有訓練在此解析度下進行。
- 平衡係數 $\lambda_1, \lambda_2$ 具體數值論文未明示 (paper does not specify)。
- 此 hybrid loss 同時保證 perceptual quality、rotational robustness 與 distortion fidelity 在統一框架內被聯合優化 (paper §3.3 結尾)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Matterport3D (Chang et al., 2017) | Panoramic image generation | 10,800 panoramas across 90 building-scale scenes | 10k panoramas for training, remainder for validation (consistent with PanFusion) |
| Internet landscape images | Perspective branch (cross-domain regularization via re-projection) | 40k high-quality images | Training only; center-cropped to 1:1 and projected onto random panoramic regions |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| FID | Fréchet Inception Distance, realism on Inception features | yes |
| FID$_\text{clip}$ | FID variant excluding blurred polar regions for fair comparison | yes |
| FID$_\text{pole}$ | FID on polar regions to assess polar distortion (following SMGD) | yes |
| FID$_\text{equ}$ | FID on perspective projections to assess projection quality (following SMGD) | yes |
| FAED | Fréchet Auto-Encoder Distance, panorama-tailored variant of FID (Oh et al., 2021) | yes |
| IS | Inception Score for diversity, with Inception-v3 replaced by ResNet pretrained on Places365 | no |
| CS (CLIP Score) | Text–image alignment via CLIP | no |
| QA$_\text{quality}$ | Q-Align quality branch, perceptual quality | no |
| QA$_\text{aesthetic}$ | Q-Align aesthetic branch, perceptual quality | no |
| BRISQUE | No-reference perceptual quality (spatial-domain) | no |
| NIQE | No-reference "completely blind" perceptual quality | no |

### 6.3 Training and Inference Settings

DiT360 is built on top of Flux (Black Forest Labs, 2024) with LoRA inserted into the attention layers (§C). Fine-tuning runs on 5 H20 GPUs using AdamW (Loshchilov & Hutter, 2019) at learning rate $2 \times 10^{-5}$ for 20 epochs, with per-GPU batch size 1 and gradient accumulation 3. The paper notes that the guidance scale is critical for convergence: training uses guidance scale 1.0 (most stable), while inference uses guidance scale 3.0 with 28 sampling steps. All training is conducted at 1024×2048 resolution (§3.4). The hybrid loss balancing coefficients $\lambda_1$ (cube loss) and $\lambda_2$ (yaw loss) in Eq. (10) — the paper does not specify their numerical values. Learning-rate schedule details (warm-up / decay) — the paper does not specify. Total wall-clock training time — the paper does not specify.

### 6.4 Main Results

Text-to-panorama on the Matterport3D validation set (Tab. 1; lower is better for FID/FAED/BRISQUE/NIQE, higher for IS/CS/QA):

| Method | FID↓ | FID$_\text{clip}$↓ | FID$_\text{pole}$↓ | FID$_\text{equ}$↓ | FAED↓ | IS↑ | CS↑ | QA$_\text{quality}$↑ | QA$_\text{aesthetic}$↑ | BRISQUE↓ | NIQE↓ | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PanFusion | 124.87 | 120.75 | 182.09 | 108.12 | 11.06 | 1.30 | 28.35 | 3.83 | 3.56 | 27.38 | 4.31 | |
| MVDiffusion | 108.19 | 117.26 | – | – | 4.39 | 1.58 | 34.65 | 3.97 | 3.25 | 44.79 | 4.91 | |
| SMGD | 46.72 | 45.04 | 65.69 | 34.84 | 3.29 | 1.40 | 31.14 | 4.05 | 3.77 | 30.35 | 4.75 | |
| PAR | 47.72 | 47.26 | 76.93 | 27.39 | 2.97 | 1.34 | 33.85 | 3.91 | 3.54 | 32.26 | 4.38 | |
| WorldGen | 67.11 | 62.97 | 79.32 | 33.45 | 3.29 | 1.40 | 34.61 | 4.30 | 3.59 | 32.31 | 4.82 | |
| Matrix-3D | 60.91 | 56.70 | 77.21 | 26.73 | 3.08 | 1.56 | 34.59 | 4.48 | 3.78 | 16.37 | 3.95 | |
| LayerPano3D | 62.82 | 60.34 | 80.37 | 38.67 | 2.98 | 1.50 | 34.40 | 4.73 | 3.93 | 33.91 | 3.79 | best QA$_\text{quality}$ |
| HunyuanWorld | 76.75 | 75.65 | 106.58 | 41.75 | 2.91 | 1.53 | 34.73 | 4.67 | 3.85 | 39.12 | 5.18 | best CS (tied with Ours via FAED) |
| **Ours (DiT360)** | **42.88** | **41.60** | **50.88** | **24.77** | **2.91** | **1.60** | 34.68 | 4.69 | **4.19** | **10.25** | **3.72** | SoTA on 9 of 11 metrics; CS and QA$_\text{quality}$ marginally below top |

User study (Tab. 3, 63 participants): DiT360 wins on Text Alignment 28.3%, Boundary Continuity 34.0%, Realism 63.8%, Overall Quality 80.9% — leading all four categories against PanFusion, Matrix-3D, and HunyuanWorld.

### 6.5 Ablation Studies

Ablations build on a Flux + LoRA baseline (Tab. 2, Fig. 5), adding one component at a time over the baseline rather than removing one from the full model.

- **Circular padding**: cuts FID 46.69 → 43.71, FID$_\text{clip}$ 45.90 → 42.36, BRISQUE 17.02 → 13.61. Diagnostic — directly targets the 0°/360° boundary continuity claim, and the FID/BRISQUE drops corroborate the qualitative claim that identical positional encodings on left/right edges fix seam discontinuities.
- **Cube loss**: improves FID$_\text{pole}$ 66.03 → 60.16, FID$_\text{equ}$ 28.91 → 26.30, IS 1.51 → 1.57, CS 34.39 → 34.62. Diagnostic — FID$_\text{pole}$ is the metric specifically designed to measure polar-region quality, so the gain isolates the cube loss's stated goal of distortion-aware supervision. The qualitative comparison in Fig. 6 (Sec. A) further isolates polar-region behavior.
- **Yaw loss**: improves FAED 3.23 → 2.98 (best single-component FAED in the table), with smaller gains on FID and IS. Diagnostic — FAED uses panorama-pretrained autoencoders sensitive to global rotational consistency, which matches the loss's design intent.
- **Perspective image guidance**: largest gains on QA$_\text{quality}$ 4.40 → 4.54 and QA$_\text{aesthetic}$ 3.97 → 4.02, with FID essentially unchanged (46.69 → 46.03). Diagnostic for the stated claim (photorealism / diversity transfer from perspective data), since QA metrics are perceptual-style sensitive; however, FID barely moving is notable and the paper does not break down whether the gain comes from data scale or projection method.
- **Full model**: best on every reported metric, confirming the components are complementary.

Concerns: the ablation is one-at-a-time addition rather than leave-one-out from the full model, so component interactions are not isolated. There is no ablation of the panoramic refinement step (Fig. 3), the hybrid-loss coefficients $\lambda_1, \lambda_2$, or the choice of computing yaw/cube losses in noise space versus latent space (the paper justifies this design choice in §3.3 prose but does not run the comparison). No seeds or variance are reported, so the ~1–4 point FID differences between components cannot be tested for significance.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — compares against 8 baselines including recent 2025 methods (SMGD, PAR, WorldGen, Matrix-3D, HunyuanWorld) spanning ERP, cubemap, autoregressive, and DiT-based paradigms.
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — quantitative evaluation is only on Matterport3D, but the method is qualitatively shown to generalize to inpainting and outpainting (§3.4, §B) without retraining.
- [covered] Has ablations that diagnose the new components (not just sanity checks) — each of the four ablated components targets a metric aligned with its design intent (FID$_\text{pole}$ for cube loss, FAED for yaw loss, BRISQUE for circular padding, QA for perspective guidance).
- [missing] Has a scaling study (size, length, or compute) — no study of data scale (e.g. varying the 40k perspective / 10k panorama splits), LoRA rank, or training-step count.
- [missing] Has an efficiency / wall-clock comparison — no training-time, inference-time, or memory comparison against baselines is reported.
- [missing] Reports variance / standard deviation / multiple seeds where relevant — single-run numbers throughout Tabs. 1–2; no error bars on the user study (n=63) either.
- [partial] Releases code / weights / data sufficient for reproducibility — code repo is announced at github.com/Insta360-Research-Team/DiT360 (abstract); the paper does not state whether trained LoRA weights or the curated 40k landscape dataset will be released, and Matterport3D requires separate licensed access.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 混合 perspective + panorama 訓練同時改善真實感與幾何保真度。** 由 Tab. 1 主表 (FID 42.88、FIDpole 50.88、BRISQUE 10.25 全為最佳) 與 Tab. 2 ablation (perspective guidance 將 QAaesthetic 從 3.97 推到 4.02、Ours all 推到 4.19) 同向支持。**Supported**,但因 perspective 與 panorama 兩域的相對貢獻沒做交叉切割,效應比例未明確。
- **Claim 2: Image-level regularization (panoramic refinement + perspective guidance) 提供跨域真實感與多樣性。** Tab. 2 顯示 perspective guidance 單獨對 FID 改善有限 (46.69 → 46.03) 但對 QAaesthetic、QAquality 有正向影響;panoramic refinement 本身沒有獨立 ablation 列。**Partially supported**:refinement 的因果效應只能透過 Fig. 3 視覺差異與整體 FIDpole 推論,缺乏「無 refinement、其他全保留」的對照。
- **Claim 3: Token-level supervision (circular padding、yaw loss、cube loss) 強制邊界、旋轉、畸變一致性。** Tab. 2 三者均單獨帶來 FID/FIDpole 下降,並與 Fig. 5 的色框視覺證據一致。**Supported**。
- **Claim 4: 不需額外微調即可原生支援 inpainting/outpainting。** §3.4 與 Fig. 1、Fig. 7 提供質性結果,但全文無 inpainting/outpainting 的量化指標 (FID、LPIPS、edit-fidelity 皆無)。**Partially supported / 屬於宣稱**:能力存在,但「品質達 SOTA 等級」沒被量化證明。
- **Claim 5: 在 11 項指標上達到 SOTA。** Tab. 1 顯示 9/11 第一,於 CS 與 QAquality 落後 LayerPano3D / Matrix-3D。作者用「perspective 指標偏差」開脫但無實證。**Overclaimed (mild)**:應改述為「9/11 指標 SOTA、2 項略落後」。

### 7.2 Fundamental Limitations of the Method

**單一資料集評估的耦合風險。** DiT360 的 polar refinement 是專為 Matterport3D 模糊極區設計,其 inpainting 區域 ($256 \le u, v < 768$) 也直接綁在 Matterport3D 的 1024×1024 cube 面上 (Eq. 2, p. 5);訓練資料、refinement 目標、驗證集三者皆為同一資料集的不同切分。在沒有任何 cross-dataset 結果的前提下,Tab. 1 領先究竟是「方法優勢」還是「對單一 distribution 的精緻過擬合」是當前實驗無法區分的。

**對 Flux 生態的雙重綁定。** 主模型用 Flux + LoRA、polar refinement 又用 Flux Kontext (Labs et al., 2025);這代表所有「真實感」上限受限於 Flux 自身的自然影像先驗。當測試 prompt 偏離 Flux 強項 (如卡通、藝術風格、非自然光照),refinement 與生成可能同時失效,而論文未做跨風格評估。

**輔助損失停在 noise 空間的選擇是經驗性的,而非結構性的。** Eq. 8、Eq. 9 將 cube loss 定義在 $\mathrm{CubeMap}(X_t - \epsilon)$ 與 $\mathrm{CubeMap}(\epsilon_\theta)$ 上,作者僅以「noise 預測已編碼空間結構」帶過。這表示幾何監督是間接的:模型沒有被告知「最終影像」的 cube 應長什麼樣,只被告知「噪聲」的 cube 應長什麼樣。當 VAE 解碼或 flow scheduler 變動時,這個對應關係不必然守恆。

**hybrid data 的可擴展性受人工 curation 限制。** 作者自陳網路 360° 影片直接拿來訓練不可行,需要 horizon correction 與 aesthetic filtering (§1, p. 2),但 perspective 分支也僅使用 40k 「人工挑選的 landscape」(§C, p. 15)。這代表此框架不會「給更多資料就更好」,而是「給更多人工 curated 資料才更好」,違背了 data-centric 主張的可擴展性精神。

### 7.3 Citations Worth Tracking

- **Peebles & Xie, 2023 (DiT)**:DiT360 整個 token-level 設計 (RoPE-aware circular padding、noise-space auxiliary loss) 都建立在 DiT 的 RoPE + transformer latent 假設上,要評估 DiT360 的可遷移性必先理解 DiT 哪些性質是被當作前提使用。
- **Black Forest Labs, 2024 (FLUX) 與 Labs et al., 2025 (FLUX.1 Kontext)**:base model 與 polar refinement 工具皆來自 Flux 家族,任何後續比較或改進若想脫離 Flux 必須先讀此兩篇以定位耦合點。
- **Su et al., 2024 (RoPE)**:circular padding 的「同位置編碼 → 同視覺特徵」推論完全依賴 RoPE 的旋轉等變性質,這個論證的成立區間需要回到 RoPE 原文檢驗 (尤其在 2D / non-causal 情境下)。
- **Kalischek et al., 2025 (CubeDiff)**:DiT360 在 §2 將其列為 cubemap baseline,但 Tab. 1 沒有實測;若想公平評斷 DiT360 對 cubemap 路線的優勢,CubeDiff 是最該補上的對照。
- **Sun et al., 2025 (SMGD)**:FIDpole / FIDequ 兩個 polar-aware 指標的源頭,也是 Tab. 1 中 ERP 路線的最強對手 (FID 46.72);理解其球面流形假設有助於判斷 DiT360 cube loss 與 SMGD 球面卷積各自的歸納偏差差異。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] DiT360 在非 Matterport3D 的 panorama 資料 (例如戶外、街景、空拍) 上是否仍然 SOTA,還是 Tab. 1 的領先主要受益於 polar refinement 對 Matterport3D 模糊瑕疵的針對性修補?
- [ ] hybrid loss 中 $\lambda_1, \lambda_2$ 的實際數值與敏感度為何,改變一個量級是否會翻轉 Tab. 2 中三個 token-level 模組的相對重要性?
- [ ] 把 cube loss 與 yaw loss 從 noise 空間改到 latent (或 pixel) 空間,訓練穩定性與最終 FIDpole 會如何變化?作者僅以一句話排除了這個替代方案。
- [ ] 在 Tab. 1 中缺席的 CubeDiff (Kalischek et al., 2025) 與 DreamCube (Huang et al., 2025) 等 cubemap 路線方法,直接比較後 DiT360 是否仍在 FIDpole 與邊界一致性上勝出?
- [ ] perspective branch 的 40k landscape 資料規模如果擴大到 200k 或縮小到 10k,QAaesthetic 與 FID 會呈現什麼樣的 scaling 曲線,是否存在飽和點?
- [ ] CLIP Score 與 QAquality 上的落後究竟是「指標對 perspective 偏好」造成的,還是 hybrid training 在某些 prompt 類別下確實降低了文字對齊?能否用 prompt 分類分析驗證?
- [ ] 原生 inpainting/outpainting 的量化品質 (例如以 LPIPS、reference-FID、edit consistency 衡量) 與專為該任務微調的方法相比表現如何?

### 8.2 Improvement Directions

1. **補上 cross-dataset 與 cross-domain 評估 (可行性最高)**:在不重新訓練的情況下,於 Pano2Vid、Insta360 公開戶外 panorama、或 360-1M 等資料集上跑現有 checkpoint 計算 FID/FIDpole/BRISQUE。理由:這是區分「方法優勢」與「Matterport3D 過擬合」的最低成本實驗,而 §C 已闡明 validation 切分,只需把 inference set 換掉即可。
2. **公開 $\lambda_1, \lambda_2$ 並補上 sensitivity sweep**:Eq. 10 是整個 hybrid 監督的權衡核心,目前完全黑箱。理由:三個 token-level loss 在 Tab. 2 各自貢獻接近 (FID 改善 2–3 點),很可能彼此競爭,sweep 可以暴露這個交互作用並提供 reproduction 起點。
3. **補做 noise-space vs latent-space 的 cube/yaw loss 對照**:作者主張 noise space 與 flow scheduler 對齊,但這應該被驗證。理由:如果 latent space 結果接近,則「noise 已耦合結構」的論點不成立但結論仍 robust;反之則該論點獲得實證,兩者皆是有價值的訊息。
4. **將 polar refinement 換成非 Flux 的 inpainting model (例如 SDXL inpaint 或 LaMa)**,觀察最終 FIDpole 是否退化。理由:目前 refinement 與 base model 都來自 Flux 生態,若 polar refinement 對 inpainting backbone 不敏感,代表方法是 backbone-agnostic;若敏感,代表 Tab. 1 的領先有相當部分來自 Flux 生態優勢,需要在論文中誠實揭露這個耦合。
5. **新增 inpainting/outpainting 的量化評估表 (LPIPS、reference-FID、CLIP-edit-consistency)**:目前 §3.4 與 Fig. 7 僅有質性結果。理由:作者已將「原生支援」列為三大貢獻之一,缺乏量化是這個 claim 的最薄弱處,補強的邊際成本相對於整體實驗極低。
6. **將 perspective 分支擴展為含天/地視角的 cubemap 全六面 re-projection**:目前刻意只用 lateral face (§3.2, p. 5) 因為 top/bottom 視角資料稀缺。理由:若能透過合成 sky / aerial / ground 影像補上,理論上可以解除 cube loss 在 top/bottom 面上「只有 panorama 端有監督」的不對稱,進一步壓低 FIDpole。
