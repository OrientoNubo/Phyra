<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# Voyager — Voyager: Long-Range and World-Consistent Video Diffusion for Explorable 3D Scene Generation

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | Voyager |
| Paper full title | Voyager: Long-Range and World-Consistent Video Diffusion for Explorable 3D Scene Generation |
| arXiv ID | 2506.04225 |
| Release date | 2025-06-04 |
| Conference/Journal | arXiv preprint (later ACM TOG) |
| Paper link (abs) | https://arxiv.org/abs/2506.04225 |
| PDF link | https://arxiv.org/pdf/2506.04225 |
| Code link | https://github.com/Tencent-Hunyuan/HunyuanWorld-Voyager |
| Project page | https://voyager-world.github.io |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Tianyu Huang | Harbin Institute of Technology | https://tyhuang0428.github.io/ | co-first author |
| Wangguandong Zheng | Southeast University | https://wangguandongzheng.github.io/ | co-first author |
| Tengfei Wang | Tencent Hunyuan | https://tengfei-wang.github.io/ | corresponding author |
| Yuhao Liu | City University of Hong Kong | — | co-author |
| Zhenwei Wang | City University of Hong Kong | https://zhenwwang.github.io/ | co-author |
| Junta Wu | Tencent Hunyuan | — | co-author |
| Jie Jiang | Tencent Hunyuan | — | co-author |
| Hui Li | Harbin Institute of Technology | — | co-author |
| Rynson W.H. Lau | City University of Hong Kong | — | co-author |
| Wangmeng Zuo | Harbin Institute of Technology | http://homepage.hit.edu.cn/wangmengzuo?lang=en | corresponding author |
| Chunchao Guo | Tencent Hunyuan | — | co-author |

### 1.2 Keywords

video diffusion, 3D scene generation, world model, RGB-D generation, camera-controllable generation, world cache, auto-regressive video, novel view synthesis

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| HunyuanVideo (Kong et al. 2024) | base model | Voyager 的視訊生成主幹採用 HunyuanVideo 的雙流／單流 DiT 與 3D-VAE。 |
| FlexWorld (Chen et al. 2025) | baseline | 以點雲投影 RGB 為條件的可控視角生成方法,本文主要對比基線之一。 |
| See3D (Ma et al. 2025) | baseline | 點雲扭曲影像條件下的新視角生成方法,被列為定量比較基線。 |
| ViewCrafter (Yu et al. 2024b) | baseline | 以點雲為條件的影像至視訊新視角生成,被作為主要對照方法。 |
| SEVA (Zhou et al. 2025) | baseline | 直接以相機參數為輸入的可控視角視訊生成,代表隱式相機條件路線。 |
| VGGT (Wang et al. 2025) | influence | 資料引擎中估計相機與深度的工具,亦做為基線重建的後處理。 |
| MoGE (Wang et al. 2024a) | influence | 用作穩健單目深度估計器,與 VGGT 深度做最小平方對齊。 |

## 2. Research Overview

### 2.1 Research Topic

本文研究如何從單張影像與使用者自訂相機軌跡,生成長距離、世界一致(world-consistent)且可探索的 3D 場景。屬於以視訊擴散模型(video diffusion)做場景級世界建模的新興方向,結合可控視角影像合成、新視角合成(NVS)與 3D 重建。重點議題包括:長序列下的時空一致性、以幾何作為條件以避免視覺幻覺、以及如何擺脫後處理 SfM/MVS 重建以直接得到可用的 3D 點雲場景。同時涵蓋大規模 RGB-D 視訊資料集自動化建構的資料引擎設計,屬於電腦視覺、生成模型與計算機圖學交會領域。

### 2.2 Domain Tags

- Computer Vision
- Generative Models
- Computer Graphics
- 3D Scene Generation
- Video Diffusion

### 2.3 Core Architectures Used

- **HunyuanVideo DiT (base backbone)**:本文以 HunyuanVideo 的「Dual-stream to Single-stream」full-attention DiT 作為去噪主幹,在其上進行 RGB-D 條件化微調。
- **3D-VAE (latent compression)**:沿用 HunyuanVideo 的 3D-VAE,將 $T \times 3 \times H \times W$ 視訊壓到 $(T/c_t+1) \times C \times H/c_s \times W/c_s$ 的時空 latent,讓擴散在低維 latent 空間進行。
- **World-Consistent Video Diffusion (proposed)**:作者提出的 RGB-D 聯合擴散模型,將 RGB 與 depth 沿高度軸拼為 $\mathbf{I}_k = [I_k, \Phi, D_k]_h$ 並以 partial RGB-D 與遮罩作條件,藉 DiT 的 full-attention 在像素層級耦合視覺與幾何。
- **Context-Based Control Blocks (proposed)**:複製 double/single-stream 的首個 block 為 $\hat{f}_D, \hat{f}_S$,以零初始化線性層 $l_D, l_S$ 殘差注入各層,強化幾何條件的控制力(類似 ControlNet 概念)。
- **World Cache with Point Culling (proposed)**:基於累積點雲的可見性與表面法向角度判斷,逐幀剔除冗餘點(約 $40\%$ 縮減),作為跨片段持久空間記憶。
- **Smooth Video Sampling (proposed)**:將輸入分為重疊一半的 segments,先以前段生成結果初始化重疊區噪聲,再對拼接後 segments 注入輕量噪聲做最後一輪 denoising,平順銜接相鄰片段。
- **Scalable Video Data Engine (proposed)**:以 VGGT 估相機與深度,MoGE 做穩健單目深度並以最小平方對齊,再用 Metric3D 校準到統一度量尺度,自動標註逾 10 萬段 RGB-D 訓練片段。

### 2.4 Core Argument

作者主張既有可控視角的視訊生成方法存在三項根本問題:(1)缺乏顯式 3D 結構支撐,長距離相機軌跡下空間一致性崩潰;(2)以「從點雲渲染的部分 RGB 影像」作為條件雖能引入幾何先驗,但在複雜遮擋場景中會出現錯誤遮擋與幻覺,反而注入不正確的訓練監督;(3)即使生成結果視覺上可接受,仍須經由 SfM 等後處理 3D 重建才能得到可用 3D 內容,既慢又會引入幾何瑕疵。據此,作者推論真正的解法必須讓模型同時感知「彩色」與「幾何」並在生成階段就完成 3D 化:因此提出 (a)同步輸出對齊的 RGB 與深度視訊,並在條件端額外注入「部分深度圖」以彌補部分 RGB 的歧義,使 DiT 的全注意力能在像素層級耦合視覺與幾何資訊;(b)為支援無限長探索,設計帶 point culling 的 world cache 持續累積點雲歷史,並以重疊片段加噪重去噪的 smooth video sampling 平順拼接相鄰片段,擺脫一般 auto-regressive 僅靠少量前幀記憶的限制;(c)由於現有資料集缺乏精準相機與度量深度,提出可擴充的資料引擎,先以 VGGT 估相機與深度,再用 MoGE 與 Metric3D 對齊到統一度量尺度,共構建逾 10 萬段訓練片段。整體方案在邏輯上是「為了端到端輸出 3D 一致世界,必須同時擁有像素級幾何條件、跨片段持久空間記憶與度量一致的訓練資料」三者缺一不可的必然結果。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「Voyager: Long-Range and World-Consistent Video Diffusion for Explorable 3D Scene Generation」一次點出四個關鍵字：long-range（長距離）、world-consistent（世界一致）、video diffusion（視訊擴散）、explorable 3D scene（可探索 3D 場景），把作品定位為「以 video diffusion 為手段、以可探索 3D 世界為目標」的生成框架，而非單純的 NVS 或 video model。

Abstract 先以實際應用（video gaming、virtual reality）切入，說明「使用者沿自定相機軌跡探索 3D 場景」是真實需求，並指出儘管 3D 物件生成已有進展，long-range、3D-consistent、explorable 場景仍是難題。接著正式提出 Voyager：以單張影像 + user-defined camera path，端到端生成 world-consistent 3D point-cloud sequences，免除 SfM/MVS 等後處理。

之後 Abstract 用三段式列出三大貢獻支柱：(1) World-Consistent Video Diffusion——共同生成對齊的 RGB 與 depth video 並以世界觀測為條件；(2) Long-Range World Exploration——具 point culling 的 world cache 加上 smooth video sampling 的 auto-regressive inference；(3) Scalable Data Engine——自動估計 camera pose 與 metric depth 以收集大規模訓練資料。最後以「視覺品質與幾何精度的明顯提升」與專案網址作結。

整段為後續鋪陳定下三層敘事骨架：consistency（§4.1–4.2）、長度可擴展（§4.3）、資料可規模化（§4.4），讓讀者帶著明確期待進入主文。

### 3.2 Introduction

(720 words)

Introduction 採「應用 → 既有方法的三類缺陷 → 我們的整體解法 → 三項貢獻」的四段結構，把全文敘事一次撐起。

開頭先講 high-fidelity、explorable 3D scenes 在遊戲、影視、機器人模擬上的價值，指出傳統流程仰賴大量人工 layout 與 asset，而 data-driven 物件/簡單場景生成又受限於 3D scene data 稀缺，引出對「scalable 生成可導覽虛擬世界」的需求，建立問題正當性。

接著作者把目前以 NVS 與 video generation 取代 3D 表徵的研究概括成三個共通問題：(1) Long-Range Spatial Inconsistency——缺乏顯式 3D 結構，長軌跡下視角轉換難以保持一致；(2) Visual Hallucination——既有以 partial RGB 作為 3D 條件的方法在複雜遮擋下會出現錯誤的 occlusion（呼應 Figure 2 的對比）；(3) Post-hoc 3D Reconstruction——即使生成視訊精美，仍須額外重建步驟取得可用 3D，耗時且引入幾何瑕疵。這三點直接對映後續三大模組，等於是論文骨架的索引。

第三段引入 Voyager，將其定位為「從單張影像與使用者相機軌跡合成 long-range, world-consistent RGB-D videos」的框架，核心是 world-consistent video diffusion 配上 expandable world caching：以 depth map 反投影建立初始 world cache，將其投影到目標相機獲得 partial RGB-D 觀測作為 diffusion 條件，再把生成幀回灌更新 cache，形成 closed-loop。隨後強調與 RGB-only 方法的差異——同時引入 depth 作為空間先驗並聯合生成 RGB+depth，可直接做 3D 重建而免去 SfM。

第四段處理長度與資料兩個延伸問題：以 world cache 與 smooth video sampling 支援 auto-regressive 場景擴張，並以 point culling 移除冗餘點以節省記憶體；訓練端則提出 video reconstruction data engine，自動估計 camera pose 與 metric depth，使資料來源能跨真實拍攝與 Unreal Engine 渲染統一尺度，最終彙整超過 100,000 段 video clips。

收尾段呼應 Figure 1，宣稱方法產出更一致的幾何，可直接 3D 重建並支援 infinite world expansion，同時點出 3D generation、video transfer、depth estimation 等下游應用，為 §6 Application 預留鉤子。最後條列三項貢獻：world-consistent RGB-D video diffusion、world caching + auto-regressive sampling、scalable data engine 與 100K 訓練資料，與 Abstract 的三支柱一一對應，使後續每章節（§4 Method、§5 Experiments、§6 Application）都能被讀者明確定位回此處的三點宣告。

### 3.3 Related Work / Preliminaries

(620 words)

本書寫合併論文的 §2 Related Work 與 §3 Preliminaries，因為兩者共同的功能是「在進入 Voyager 方法前先把文獻定位與技術基底鋪好」。

§2.1 Camera-Controllable View Generation 將既有可控相機生成法分成三類：(a) NVS 透過多視重建合成新視角，仰賴密集視點，難處理單張輸入；(b) 把 camera parameter 隱式注入 model，雖能依視角生成圖像，但常見視點不一致；(c) 以輸入視 warp 出的 point cloud 作為條件，雖大幅提升空間一致性，但 warp 後的圖像仍含 artifact，會干擾訓練。作者藉此明確自己屬於第三類，但獨特之處在於「同時引入 warping depth 作為條件並聯合生成 RGB + depth」，把 §4.1 與 §4.2 的設計動機與既有路線的差距點清楚。

§2.2 Long-Range Video Generation 把長視訊生成切成 training-free、hierarchical、auto-regressive 三條路線，指出前兩者無法擴張到無限長度，後者則受限於 memory cache 難以保留遠期歷史。這直接導出 §4.3 的世界快取與 point culling：用 point cloud 而非 latent cache 來保留完整空間歷史，並以 smooth video sampling 在 auto-regressive 推論中連接 clips。

§3 Preliminaries of Video Diffusion Models 則是給後續方法所需的記號與基底模型一個交代。先用一句話介紹 diffusion 的 forward/reverse 過程，再說明 video diffusion 透過 3D convolution、attention、latent diffusion 進入時間維度。重點落在他們所選的骨幹 Hunyuan-Video：給定文字 $y$ 與 ground-truth video $[I_0, \dots, I_{T-1}]\in\mathbb{R}^{T\times 3\times H\times W}$，由 3D-VAE 取得 latent $z_0$，形狀為 $(T/c_t+1)\times C\times H/c_s\times W/c_s$；noisy latent $z_t$ 進入「Dual-stream to Single-stream」混合 DiT，雙流區塊 $f_D^i$ 分別處理 video 與 text latent，單流區塊 $f_S^i$ 在串接後共同處理；image-conditioned 時把 image latent 沿 channel 軸串到 $z_t$；訓練目標是預測 velocity $u_t = dz_t/dt$；推論用 first-order Euler ODE solver 還原 $z_0$，再由 3D-VAE decoder 輸出視訊。

這段技術鋪陳的策略意圖很明確：把 §4 中會反覆出現的 latent shape、雙/單流 block 命名、channel-wise 條件串接、velocity 訓練目標都先定義好，使讀者進入 §4.2 看到 $z'_{t,0} = f_{\mathrm{emb}}(\mathrm{concat}(z_t, z_{\mathrm{rgb}}, z_{\mathrm{depth}}))$ 與 Eq. (1)–(2) 時，能直接把 Voyager 的修改視為「在 Hunyuan-Video 的雙/單流 DiT 上加 depth concatenation 與 control blocks」，而非從零理解一個新架構。整體來看，§2 給「為什麼要做」的對手定位，§3 給「在誰之上做」的技術前提，共同把讀者引導至 §4 的方法主軸。

### 3.4 Method (overview narrative)

(360 words)

§4 Methodology: Voyager 開頭重申輸入輸出設定：給定影像 $I_0\in\mathbb{R}^{3\times H\times W}$ 與使用者自訂相機軌跡，目標是建立可探索的世界。作者把 video generation 與 3D world modeling 之間的落差概括為三個面向：long-range 視訊延伸的不一致、視覺條件帶來的幻覺、以及無法從視訊輸出重建世界，並對應宣告三組設計，作為 §4.1–4.4 的章節地圖。

§4.1 Geometry-Injected Frame Condition 是整個方法論的入口：作者解釋 camera parameter 作為隱式條件難訓練、純 warped RGB 作為顯式條件又會在複雜遮擋下幻覺，因此提出在 partial RGB image 之外再導入對齊的 partial depth map，由 depth map 與相機參數投影得到 point cloud，再 render 回各視角生成 partial RGB+depth+mask，作為後續 diffusion 的幾何條件。

§4.2 World-Consistent Video Diffusion 把這組條件接到 §3 預備的 Hunyuan DiT。先說明 channel-wise concatenation 的 baseline 做法在缺口大小變化大時不穩，因此提出 Depth-Fused Video Generation——把 RGB 與 depth 沿 height 軸串成 $\mathcal{I}_k=[I_k,\Phi,D_k]_h$，讓 full-attention DiT 能在 pixel 層級交互視覺與幾何資訊；再以 Context-Based Control Enhancement 複製首個 double/single-stream block 為 control blocks $\hat f_D, \hat f_S$，以 zero-initialized linear layer 注回主幹，加強對 partial 條件的 follow。

§4.3 Long-Range World Exploration 處理長度問題：以 World Caching with Point Culling 累積 RGB-D 投影所得 point cloud，並用 visibility mask 與 surface-normal 角度檢查決定加點，宣稱可省約 40% 點數；以 Smooth Video Sampling 透過 overlapping segment 初始化、再經平均與 light-noise 微擾後再 denoise，確保連續 clip 間色彩過渡無跳變。

§4.4 Scalable Video Data Engine 則為前述模型的訓練資料把關：以 RealEstate10K、DL3DV 與自渲染 UE 場景共逾 100,000 clips 為素材，以 VGGT 取得 camera pose 與粗 depth、以 MoGE 透過 least-squares 對齊改善 depth、再以 Metric3D 校準 metric scale。整章敘事從「條件設計 → 模型結構 → 推論延伸 → 訓練資料」一氣呵成，為 §5 的多面向實驗鋪好評估基底。

### 3.5 Experiments (overview narrative)

(330 words)

§5 Experiments 採「能力分層、由近到遠」的安排：先看單段視訊品質、再看下游 3D 重建、再看跨領域 world-scale 評測，最後以 ablation 收束方法論主張。

§5.1 Video Generation 在 RealEstate10K 隨機抽樣 150 段 clip，與 SEVA、ViewCrafter、See3D、FlexWorld 在 image-to-video 任務上比較，採 PSNR、SSIM、LPIPS 評估視覺相似度。Table 1 顯示 Voyager 在三項指標上皆領先，Figure 4 則進一步呈現在大幅相機運動或細節物件保留上仍能維持合理性。這一節的角色是先確立「在熟悉 benchmark 與標準指標下 Voyager 至少不輸並普遍勝出」。

§5.2 Scene Generation 把同一批生成視訊接到 3DGS 重建：baselines 因僅輸出 RGB，要先用 VGGT 補出 camera 與 depth；Voyager 則因原生產出 RGB-D，可直接初始化點雲，也另測試以 VGGT 為共同基準的版本。Table 2 同時呈現 VGGT-post 與「Voyager 自帶 depth」兩列，並於後者三項指標再進一步提升，論證 depth 共生成不只是視覺輔助、實際提升幾何一致性。

§5.3 World Generation 將戰場拉到 WorldScore 的 2,000 個 static 例子，跨室內外、寫實與風格化，與 WonderJourney、WonderWorld、EasyAnimate、Allegro、Gen-3、CogVideoX-I2V 六種 SOTA 比較。Table 3 顯示 Voyager 取得最高 WorldScore Average，並在 Subjective Quality 拿下首位，作者特別點出他們因採 metric depth 條件而產生「比其他方法更大幅度的相機運動」，相對更難生成。

§5.4 Ablation Studies 分兩條軸：World-Consistent Video Diffusion 上比較三個訓練階段——RGB-only、RGB-D、加 control blocks——Table 4 顯示 depth 融合主要拉高 camera control 與 content alignment，control blocks 進一步補強 3D consistency；Long-range 部分則以 Figure 8 對比「保留全部點 / 僅保留不可見區域 / 加 normal check」與「無/有 smooth sampling」，論證 point culling 在維持品質下省 ~40% 儲存、smooth sampling 確保跨 clip 過渡無接縫。整體實驗鏈為 §6 的多元應用展示提供量化背書。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

§7 Conclusion 用一段話收尾：Voyager 是一個 world-consistent video generation framework，目標是 long-range world exploration；其 RGB-D video diffusion 能在使用者輸入相機軌跡下產出空間一致的 video sequences，並可直接用於 3D scene reconstruction，配合 auto-regressive 推論支援世界擴張。實驗證實在生成視訊與點雲兩端皆有高視覺保真與強空間一致性。

論文未設專門的 Limitations 或 Future Work 段落，僅在 §6 Application 隱含展望——透過 long video generation、image-to-3D、depth-consistent video transfer、video depth estimation 四個 demo 暗示後續延伸方向；對於失效情境、計算成本、無動態物件支援、依賴單張輸入等限制，paper does not specify。

## 4. Critical Profile

### 4.1 Highlights

- 在 RealEstate10K 上的 novel view synthesis 全面領先四個 baseline:PSNR 18.751、SSIM 0.715、LPIPS 0.277,優於 FlexWorld 的 18.278/0.693/0.281(Table 1, p.5)。
- 即使搭配同樣的 VGGT post-hoc 重建,Voyager 仍能在 3DGS 重建上勝出(PSNR 17.742 vs FlexWorld 17.623),改用自家生成的 depth 後再進一步提升至 18.035(Table 2, p.5)。
- 在 WorldScore 靜態 benchmark 上以平均分 77.62 拿下第一,超越 3D-based 的 WonderWorld(72.69)與所有四個 video baseline(Table 3, p.7)。
- 提出 jointly 生成對齊的 RGB 與 depth 視訊,並把兩者沿 height 軸串接 $[\,I_k, \Phi, D_k\,]_h$,讓 DiT 的 full-attention 能在 pixel level 同時耦合視覺與幾何資訊(Sec 4.2, p.4)。
- 在條件端用 partial depth $\hat{D}_k$ 取代僅靠 partial RGB $\hat{I}_k$ 的設計,直觀地解決複雜遮擋下 partial RGB 出現錯誤遮擋與幻覺的問題(Figure 2, p.2)。
- World cache 的 normal-check point culling 將儲存點數縮減約 40%,且在 Figure 8(p.7)的視覺結果與「全部保留」幾近一致。
- Smooth video sampling 透過重疊片段 noise re-init 與輕度 noise injection 再 denoise,提供 auto-regressive 拼接的色彩一致性策略(Sec 4.3, p.5)。
- Scalable data engine 將 VGGT(相機+深度)、MoGE(robust depth)以 least squares 對齊、再以 Metric3D 做 quantile-based metric 校準,構建超過 100,000 段 RGB-D 訓練 clip(Sec 4.4, p.5; App C, p.11)。
- 三階段訓練的 ablation 顯示 RGB-only 到 RGB-D 的躍升最大(Camera Control 74.98 → 85.04),Control block 再小幅補強到 85.95(Table 4, p.7)。
- 同一模型可不重訓即支援 long-range 探索、image-to-3D、depth-consistent video transfer 與 video depth estimation 四個應用(Figure 6, p.8)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者明白指出 video diffusion 無法單次 pass 生成長視訊,因此整套 long-range exploration 必須仰賴 auto-regressive(Sec 4.3, p.4)。
- DL3DV 因 camera 抖動過快被認為不適合 depth 訓練,僅能從原始 10K 影片中精挑 3,000 段,並在第二階段就被踢出訓練集(Sec 4.4, p.5; App A, p.11)。
- 作者承認不同 clip 各自獨立生成時會產生 color discrepancies,「無法直接拼接」,因此才需要 smooth video sampling(Sec 4.3, p.5)。
- VGGT 估出的 depth「不夠精準」,所以才需要 MoGE 做 least squares 對齊(Sec 4.4, p.5)。
- Channel-wise concatenation 「struggles to handle variable situations」,當缺失區域從小裂縫到大空白都可能出現時表現受限,這個 trivial baseline 才被 Depth-Fused 設計取代(Sec 4.2, p.4)。

#### 4.2.2 Phyra-inferred

- 在最直接量測 spatial 一致性的 WorldScore "3D Consistency" 軸上,Voyager 僅得 81.56,落後 WonderWorld(86.87)與 CogVideoX-I2V(86.21),這直接動搖「world-consistent」這個全文核心賣點(Table 3, p.7)。
- 與本文方法最接近的同期工作 GEN3C(Ren et al. 2025)被反覆引述為 partial-RGB conditioning 的代表,卻未出現在 Table 1/2/3 任何比較中,使「partial RGB+D vs 純 partial RGB」的關鍵 ablation 缺了最關鍵的對手(p.3, p.5 提到但無實驗對照)。
- Long-range 與 "infinite" exploration 只有 Figure 1 與 Figure 6(a) 的定性展示,沒有任何 drift、re-projection error、PSNR-vs-distance 曲線等量化指標,標題的 "Long-Range" 主張在文中完全不可驗證(Sec 4.3, p.4-5; Sec 6, p.7)。
- Video generation 評估只用 frame-wise 的 PSNR/SSIM/LPIPS、且僅 150 段測試,沒有 FVD、temporal metric 或 human eval,因此 flicker、temporal artifact 與 motion 不一致都不會反映在報告數字中(Sec 5.1, p.5-6)。
- 第三階段的 ControlNet block 「solely on the UE dataset」訓練(App A, p.11),意味著最終強化幾何 controllability 的關鍵模組只看過合成資料分佈,real-world 測試上的提升有相當機率混雜了第二階段 RGB-D 訓練的貢獻。
- Point culling 只報「約 40%」的相對縮減,沒有絕對記憶體用量、rendering FPS 或與 voxel hashing 等簡單 baseline 的對照,因此「scalable to arbitrary length」的工程主張無從佐證(Sec 4.3, p.5)。
- 整個 data engine 的 metric depth 是 Metric3D quantile scaling(Eq. 6, App C, p.11)的產物,從未在 NYU、KITTI、ScanNet 等帶 GT 的 depth benchmark 上驗證,所有訓練 label 都是 pseudo-label 卻被當成 ground truth。
- Smooth video sampling 只有 Figure 8 的定性對照,缺少 "w/o sampling vs w/ sampling" 的量化指標,且重疊片段的 re-denoise 額外計算開銷在全文未被披露(Sec 4.3, p.5; Fig 8, p.7)。
- 「the first video model that jointly generates RGB and depth sequences with given camera trajectories」這個主張僅以一句話列出,並未針對 image-level 或 single-frame RGB-D diffusion 工作做完整文獻盤點以支撐 "first"(Sec 1, p.3)。

### 4.3 Phyra's Judgment (summary)

Voyager 真正新的部分是「在 conditioning 端把 partial depth 加進來、再讓 DiT 同時輸出對齊的 RGB-D」這個 representation 抉擇,以及把 partial-RGB conditioning 路線(FlexWorld、ViewCrafter、See3D、GEN3C)推到 RGB-D 的合理下一步;world cache 的 normal-check culling 與 smooth video sampling 屬於工程性銜接層。然而,「world-consistent」的核心宣稱在 WorldScore 自己定義的 3D Consistency 軸上反而落後 WonderWorld 與 CogVideoX-I2V,真正的長距離一致性在文中沒有任何量化證據。最關鍵未解的問題是:partial-depth conditioning 帶來的提升,究竟是來自 depth 本身的幾何先驗,還是來自 RGB-D joint 輸出迫使 DiT 學到更乾淨的 latent 對齊?在沒有與 GEN3C 直接對打、也沒有量化 long-range drift 之前,這兩種解釋都無法區分。

## 5. Methodology Deep Dive

### 5.1 Method Overview

Voyager 是一個建立在 HunyuanVideo 雙流／單流 DiT 基礎模型上的 **world-consistent video diffusion** 框架。給定單張輸入影像 $I_0 \in \mathbb{R}^{3 \times H \times W}$、文字提示 $y$、以及使用者指定的相機軌跡 $\{c_k\}_{k=0}^{T-1}$,模型一次性生成 $T$ 幀對齊的 RGB-D 視訊,並支援透過 auto-regressive inference 進行任意長度的世界探索。其核心創新是把「幾何感知」內建於擴散過程本身,而非作為 post-hoc 後處理:輸入影像先以單目深度估計轉為點雲 $p_0$,該點雲被投影到每個目標視點 $c_k$ 上,得到 partial RGB image $\hat{I}_k$、partial depth map $\hat{D}_k$ 與 rendering mask $M_k = \text{render}(p_0, c_k)$,作為 DiT 的明確幾何條件。

第二項創新是 **depth-fused video generation**:不是僅用 partial depth 補完 RGB 缺失區域,而是讓擴散模型同時生成完整的 RGB 與 depth 兩種視訊。具體做法是把 RGB 與深度沿 height 軸串接成 $\mathcal{I}_k = [I_k, \Phi, D_k]_h$(中間以 placeholder 列 $\Phi$ 分隔),條件圖 $\hat{\mathcal{I}}_k$ 與 mask $\mathcal{M}_k$ 同樣以高度軸組合。這樣 DiT 的 full-attention 結構就能在 pixel level 直接耦合視覺與幾何資訊。為了強化幾何條件的控制力,Voyager 額外引入仿照 VideoPainter 的 **context-based control blocks** $\hat{f}_D, \hat{f}_S$,把第一層 double-stream 與 single-stream 區塊的輸出以 zero-initialized linear layer 回注每一層 transformer block。

第三項創新是 **長距離世界探索機制**:Voyager 維護一個跨片段累積的 **world cache** ——點雲集合 $\hat{p} \in \mathbb{R}^{(T \times H \times W) \times 3}$。每生成一個新片段,新點雲會被增量加入 cache,並透過 point culling(基於可見性 mask 與 surface normal 與當前視向的夾角是否超過 90°)去除冗餘點,儲存量約減少 40%。為了讓相鄰片段的色調與內容連續,作者設計 **smooth video sampling**:把序列切成重疊區為一半段長的 segments,前一片段的去噪結果作為當前片段重疊區的 noise initialization;兩片段推理完成後對重疊區做 averaging,再注入 light-level noise 並做最後一輪 denoising。

訓練資料則由 **scalable video data engine** 自動標註:VGGT 估計相機與初始深度,MoGE 提供 robust 單目深度並用 disparity 空間下的 least squares 對齊到 VGGT 的相機座標系,Metric3D 進一步將深度尺度校正到統一的 metric 範圍,共產出超過 100,000 段訓練片段,涵蓋 RealEstate10K、DL3DV 與 Unreal Engine 渲染合成資料。

### 5.2 Pipeline Diagram with Tensor Shapes

```
User Input
├─ Image I_0                           [B, 3, H, W]
├─ Text y                              (string)
└─ Camera trajectory {c_k}_{k=0..T-1}  [B, T, 4, 4]   (extrinsics + intrinsics)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  (A) Geometry-Injected Frame Condition                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Depth estimation on I_0  → D_0   [B, 1, H, W]    │   │
│  │ Unproject (D_0, c_0)     → p_0   [B, N=H*W, 6]   │   │
│  │ For each k:                                      │   │
│  │   M_k = render(p_0, c_k)         [B, T, 1, H, W] │   │
│  │   Î_k = I_warp ⊙ M_k             [B, T, 3, H, W] │   │
│  │   D̂_k = D_warp ⊙ M_k             [B, T, 1, H, W] │   │
│  │ Height-axis concat:                              │   │
│  │   Î_k = [Î_k, Φ, D̂_k]_h          [B, T, 3, 2H+1, W]│  │
│  │   M_k = [M_k, Φ, M_k]_h          [B, T, 1, 2H+1, W]│  │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  (B) 3D-VAE Encoder + Latent Concatenation              │
│   GT video [I_k, Φ, D_k]_h → z_0    [B, T', C, H', W']  │
│     where T'=T/c_t+1, H'=(2H+1)/c_s, W'=W/c_s           │
│   Cond latent  ẑ_0                  [B, T', C, H', W']  │
│   Mask down-pool m                  [B, T', 1, H', W']  │
│   Forward diffusion: z_0 → z_t      [B, T', C, H', W']  │
│   Patch embed:                                          │
│     z'_{t,0} = f_emb(concat(z_t, ẑ_0, m))               │
│                                     [B, L, d_model]     │
│     where L = T' * (H'/p) * (W'/p)                      │
└─────────────────────────────────────────────────────────┘
        │
        ├──→ Text encoder → z'_{y,0}  [B, L_text, d_model]
        ▼
┌─────────────────────────────────────────────────────────┐
│  (C) Depth-Fused DiT  (Eq. 1–2)                         │
│   Double-stream blocks  f_D^i × N_D                     │
│     (z'_{t,i}, z'_{y,i}) = f_D^i(z'_{t,i-1}, z'_{y,i-1}, t)│
│                                     [B, L, d_model]     │
│   Single-stream blocks  f_S^i × N_S                     │
│     z''_{t,i} = f_S^i(z''_{t,i-1}, t)                   │
│                                     [B, L+L_text, d_model]│
└─────────────────────────────────────────────────────────┘
        │           ▲
        │           │ (residual injection per block)
        ▼           │
┌─────────────────────────────────────────────────────────┐
│  (D) Context-Based Control Blocks  (Eq. 3–4)            │
│   z_D = f̂_D(z'_{t,0})               [B, L, d_model]     │
│   z_S = f̂_S(z_D)                    [B, L, d_model]     │
│   z'_{t,i}  += l_D(z_D)   (zero-init linear)            │
│   z''_{t,i} += l_S(z_S)   (zero-init linear)            │
└─────────────────────────────────────────────────────────┘
        │
        ▼
   Velocity prediction û_t            [B, T', C, H', W']
        │
        ▼   first-order Euler ODE solve
   Recovered latent z_0               [B, T', C, H', W']
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  (E) 3D-VAE Decoder                                     │
│   z_0 → [I_k, Φ, D_k]_h frames                          │
│   Split height-axis → I_k:  [B, T, 3, H, W]             │
│                     D_k:    [B, T, 1, H, W]             │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  (F) World Cache Update with Point Culling              │
│   New points p̂_new = unproject(D_k, c_k)                │
│                                     [B, T*H*W, 3]       │
│   For each frame k:                                     │
│     M_vis = render(p̂_cache, c_k)                        │
│     keep p ∈ p̂_new where ¬M_vis OR cos(n,v) < 0         │
│   p̂_cache ← p̂_cache ∪ kept points   [B, N_cache, 3]     │
│   (≈ 40% reduction vs. naive accumulation)              │
└─────────────────────────────────────────────────────────┘
        │
        ▼ (next clip)
┌─────────────────────────────────────────────────────────┐
│  (G) Smooth Video Sampling                              │
│   Overlap = T/2                                         │
│   z_t^{seg_n}[overlap] ← noised z_0^{seg_{n-1}}[overlap]│
│   After two-segment inference:                          │
│     merge = avg(seg_{n-1}[overlap], seg_n[overlap])     │
│     + light noise → final denoising round               │
└─────────────────────────────────────────────────────────┘
        │
        ▼
   Output: T-frame RGB-D video + accumulated point cloud
   (no SfM/MVS post-processing required)
```

注:`?` 標示的具體數值($c_t$、$c_s$、$N_D$、$N_S$、$d_{model}$、$p$ 等)詳見 §5.3 各模組的「Implementation Details」;這些值為 HunyuanVideo 主幹的設定,本論文未額外揭露具體數字。

### 5.3 Per-Module Breakdown

#### 5.3.1 Geometry-Injected Frame Condition

**Function:** 將輸入影像轉為點雲後,依使用者指定的相機軌跡渲染出 partial RGB、partial depth 與可見性 mask,作為擴散模型的顯式幾何條件,以避免僅用 partial RGB 在複雜遮擋下產生的視覺幻覺。

**Input:**
- Name: $I_0$, $\{c_k\}_{k=0}^{T-1}$
- Shape: $[B, 3, H, W]$,$[B, T, 4, 4]$(相機外參/內參)
- Source: 使用者輸入

**Output:**
- Name: $\hat{\mathcal{I}}_k$,$\mathcal{M}_k$
- Shape: $[B, T, 3, 2H+1, W]$,$[B, T, 1, 2H+1, W]$
- Consumer: §5.3.2 3D-VAE Encoder

**Processing:**

1. 對 $I_0$ 估計深度 $D_0$,以相機 $c_0$ unproject 為點雲 $p_0 \in \mathbb{R}^{N \times 6}$($N = H \times W$,通道為 $(x,y,z,r,g,b)$)。
2. 對每個目標視點 $c_k$,渲染可見性遮罩 $M_k = \text{render}(p_0, c_k)$,並把點雲投影回 2D 得 $\hat{I}_k$、$\hat{D}_k$。
3. 沿 height 軸串接 RGB 與深度:$\mathcal{I}_k = [I_k, \Phi, D_k]_h$、$\hat{\mathcal{I}}_k = [\hat{I}_k, \Phi, \hat{D}_k]_h$、$\mathcal{M}_k = [M_k, \Phi, M_k]_h$,中間夾入 placeholder 列 $\Phi$ 以幫助模型分離兩種模態。

**Key Formulas:**

$$
M_k = \text{render}(p_0, c_k), \quad \hat{\mathcal{I}}_k = [\hat{I}_k, \Phi, \hat{D}_k]_h
$$

**Implementation Details:**

論文未揭露使用何種單目深度估計器作為推理階段 $D_0$ 的來源,訓練階段的 ground-truth depth 由資料引擎(§5.3.7)以 VGGT + MoGE + Metric3D 對齊產生。論文支援多種 width-height ratio,訓練時從 $\{1, 1.25, 1.5, 1.75\}$ 中隨機抽樣。

---

#### 5.3.2 3D-VAE Encoding & Latent Concatenation

**Function:** 把高度軸串接後的 RGB-D 視訊壓縮到低維 latent 空間,並把噪聲 latent、條件 latent 與下採樣 mask 沿通道串接後送入 patch embedding。

**Input:**
- Name: GT 視訊 $[\mathcal{I}_k]_{k=0}^{T-1}$、$\hat{\mathcal{I}}_k$、$\mathcal{M}_k$
- Shape: $[B, T, 3, 2H+1, W]$
- Source: §5.3.1 Frame Condition

**Output:**
- Name: $z'_{t,0}$
- Shape: $[B, L, d_{model}]$,其中 $L = T' \cdot (H'/p) \cdot (W'/p)$
- Consumer: §5.3.3 DiT

**Processing:**

1. 3D-VAE Encoder 將 $T$ 幀視訊壓縮為 latent $z_0$,形狀為 $(T/c_t + 1) \times C \times H'/c_s \times W'/c_s$,其中 $H' = 2H+1$。
2. Forward diffusion 在 $z_0$ 上加噪得 $z_t$,條件視訊以同一 VAE 編碼為 $\hat{z}_0$,mask $\mathcal{M}_k$ 經 max-pooling 下採樣為 $m$。
3. 沿 channel 軸串接 $\text{concat}(z_t, \hat{z}_0, m)$,經 patch-embedding 層 $f_{emb}$ 投影回 transformer 維度:$z'_{t,0} = f_{emb}(\text{concat}(z_t, \hat{z}_0, m))$。

**Key Formulas:**

$$
z'_{t,0} = f_{emb}\bigl(\text{concat}(z_t, \hat{z}_0, m)\bigr)
$$

**Implementation Details:**

3D-VAE 直接沿用 HunyuanVideo 預訓練權重,具體 $c_t$、$c_s$、$C$、patch size $p$、$d_{model}$ 等本論文未揭露。Stage-1 訓練時僅串接 RGB 相關 latent;Stage-2 起加入深度 latent。

---

#### 5.3.3 Depth-Fused DiT (Double-Stream + Single-Stream)

**Function:** Hybrid Transformer 主幹,先以 dual-stream 區塊獨立處理視訊與文字 latent,再在 single-stream 階段把兩者串接以 full-attention 共同建模時空與跨模態關係,並在 pixel level 耦合 RGB 與深度。

**Input:**
- Name: $z'_{t,0}$、文字 latent $z'_{y,0}$、時間步 $t$
- Shape: $[B, L, d_{model}]$、$[B, L_{text}, d_{model}]$、scalar
- Source: §5.3.2 patch embedding 與文字編碼器

**Output:**
- Name: 速度預測 $\hat{u}_t$
- Shape: $[B, T', C, H'', W'']$(再經反 patch-embed 還原為 latent 形狀)
- Consumer: ODE solver → 3D-VAE Decoder

**Processing:**

雙流階段(Eq. 1)獨立處理視訊與文字 latent;單流階段(Eq. 2)把 $z'_{t, N_D}$ 與 $z'_{y, N_D}$ 串接後一起做 full-attention,目的是讓視覺、幾何與文字在像素層級互動。

**Key Formulas:**

$$
z'_{t,i},\; z'_{y,i} = f_D^i(z'_{t,i-1},\; z'_{y,i-1},\; t),\quad i = 1, \dots, N_D
$$

$$
z''_{t,i} = f_S^i(z''_{t,i-1},\; t),\quad i = 1, \dots, N_S, \quad z''_{t,0} = \text{concat}(z'_{t, N_D}, z'_{y, N_D})
$$

訓練目標為 velocity prediction:最小化 $\|\hat{u}_t - u_t\|_2^2$,其中 $u_t = dz_t/dt$。

**Implementation Details:**

主幹來自 HunyuanVideo,具體 $N_D$、$N_S$ 數值論文未揭露。每次推理生成 49 幀。Stage-1 訓練 RGB 通道、Stage-2 加入深度通道 fine-tune 全部 DiT 參數,Stage-3 凍結 DiT。

---

#### 5.3.4 Context-Based Control Blocks

**Function:** 仿照 VideoPainter 的輕量級控制模組,把第一層 double-stream 與 single-stream 區塊的早期特徵以 zero-initialized linear layer 加回每一層 transformer 區塊,強化幾何條件的 pixel-level controllability,解決僅在輸入層串接條件導致控制力不足的問題。

**Input:**
- Name: $z'_{t,0}$
- Shape: $[B, L, d_{model}]$
- Source: §5.3.2 patch embedding

**Output:**
- Name: 殘差項 $l_D(z_D)$、$l_S(z_S)$
- Shape: $[B, L, d_{model}]$
- Consumer: §5.3.3 每一層 DiT 區塊(殘差累加)

**Processing:**

1. 複製第一層 double-stream 與 single-stream 區塊作為 control blocks $\hat{f}_D$、$\hat{f}_S$,計算 $z_D = \hat{f}_D(z'_{t,0})$、$z_S = \hat{f}_S(z_D)$。
2. 對 DiT 每一層 $i$,以 zero-initialized linear layer $l_D, l_S$ 把 $z_D, z_S$ 加回對應 latent。

**Key Formulas:**

$$
z_D = \hat{f}_D(z'_{t,0}), \quad z_S = \hat{f}_S(z_D)
$$

$$
z'_{t,i} \leftarrow z'_{t,i} + l_D(z_D), \quad z''_{t,i} \leftarrow z''_{t,i} + l_S(z_S)
$$

**Implementation Details:**

Control blocks 僅在 Stage-3 訓練,此時主 DiT 參數凍結,僅訓練兩個複製出的 control blocks 與 zero-init 線性層。Stage-3 僅使用具有 ground-truth metric depth 的 UE 合成資料。

---

#### 5.3.5 World Cache with Point Culling

**Function:** 跨片段累積點雲歷史以支援長距離 auto-regressive 探索,並透過可見性與表面法向夾角檢查移除冗餘點,降低記憶體與計算開銷。

**Input:**
- Name: 新生成的 RGB-D 幀 $(I_k, D_k, c_k)$
- Shape: $[B, T, 3, H, W]$、$[B, T, 1, H, W]$、$[B, T, 4, 4]$
- Source: §5.3.3 解碼後的視訊輸出

**Output:**
- Name: world cache $\hat{p}$
- Shape: $[B, N_{cache}, 3]$(初始上界為 $T \times H \times W$ 但經 culling 大幅減少)
- Consumer: 下一片段的 §5.3.1 Frame Condition

**Processing:**

對每個新點:(1) 計算當前視點下既有 cache 的可見性遮罩 $M = \text{render}(\hat{p}, c_i)$;(2) 落在 invisible 區域的點直接加入 cache;(3) 落在 visible 區域的點,若既有點的表面法向與當前視向夾角超過 90°(代表既有點在當前視點是「背面」、不應遮擋新點),則新點仍加入 cache。論文回報此策略使儲存點數降低約 40%,同時避免多幀聚合造成的雜訊累積。

**Key Formulas:**

$$
\hat{p} \in \mathbb{R}^{(T \times H \times W) \times 3}, \quad M = \text{render}(\hat{p}, c_i)
$$

加入條件:點在當前視點 invisible,或現有可見點的表面法向 $\mathbf{n}$ 與視向 $\mathbf{v}$ 滿足 $\mathbf{n} \cdot \mathbf{v} < 0$。

**Implementation Details:**

Culling 採 per-frame 增量更新,具體渲染實作(rasterization vs. splatting)論文未明確說明。Ablation 顯示此策略相對於「儲存所有點」與「僅儲存不可見點」在視覺品質相當的前提下節省約 40% 儲存。

---

#### 5.3.6 Smooth Video Sampling

**Function:** 透過 overlapping segment 的 noise initialization 與後處理 averaging+denoising,消除相鄰 auto-regressive 片段間的色調不連續,維持長視訊的時序與光度一致性。

**Input:**
- Name: 前一片段去噪結果 $z_0^{(n-1)}$
- Shape: $[B, T', C, H'', W'']$
- Source: §5.3.3 上一片段的 DiT 輸出

**Output:**
- Name: 當前片段去噪結果 $z_0^{(n)}$
- Shape: $[B, T', C, H'', W'']$
- Consumer: §5.3.5 World Cache 更新

**Processing:**

1. 把連續輸出視訊切成 overlapping segments,重疊長度為一個 segment 長度的一半。
2. 當前 segment 的重疊區以前一 segment 對應位置的去噪結果作為 noise initialization,而非從 pure Gaussian noise 開始。
3. 兩個連續 segment 推理完成後,對重疊區做 averaging 並注入 light-level noise,執行最後一輪 denoising 以細化過渡。

**Key Formulas:**

$$
z_t^{(n)}[\text{overlap}] = \text{noise}\bigl(z_0^{(n-1)}[\text{overlap}], t\bigr)
$$

$$
z_0^{\text{merged}} = \text{denoise}\Bigl(\text{noise}\bigl(\tfrac{1}{2}(z_0^{(n-1)} + z_0^{(n)})_{\text{overlap}},\; t_{\text{light}}\bigr)\Bigr)
$$

**Implementation Details:**

論文未揭露 light-level noise 的具體 timestep,但定性結果(Figure 8)顯示啟用 smooth sampling 後,跨片段顏色漂移與內容不連續顯著減少。

---

#### 5.3.7 Scalable Video Data Engine

**Function:** 自動化標註相機參數與 metric depth,為訓練資料(超過 100,000 段視訊片段,涵蓋 RealEstate10K、DL3DV、UE 合成)提供幾何一致的監督訊號,擺脫對人工 3D 標註與傳統 SfM/MVS 的依賴。

**Input:**
- Name: 任意場景視訊 $\{I_k\}_{k=0}^{T-1}$
- Shape: $[B, T, 3, H, W]$
- Source: 開源資料集(RealEstate10K、DL3DV)與 UE 渲染

**Output:**
- Name: 相機外參 $C_{cam}^{metric}$、metric depth $d^{metric}$
- Shape: $[B, T, 4, 4]$、$[B, T, 1, H, W]$
- Consumer: §5.3.1 訓練時提供 ground-truth $(D_k, c_k)$

**Processing:**

1. **VGGT** 從整段視訊估計相機與初始深度,後者與相機座標系對齊但精度有限。
2. **MoGE** 提供 robust 單目相對深度;在 disparity 空間以 least squares 求出 scale 與 bias 把 MoGE 對齊到 VGGT 的相機座標系(只在 non-sky mask $\mathcal{M}$ 內最佳化)。
3. **Metric3D** 估計場景 metric depth 範圍,用其 0.2 與 0.8 quantile 計算 scale factor 把 MoGE 對齊深度進一步映射到 metric 尺度,同時對相機平移向量 $T$ 一併縮放,確保跨資料集尺度統一。

**Key Formulas:**

$$
\min_{scale, bias}\; \mathcal{M} \cdot \left(\frac{scale}{d_{MoGE}} + bias - \frac{1}{d_{VGGT}}\right)^2
$$

$$
s_{metric} = \frac{q(0.8, d_{Metric3D}) - q(0.2, d_{Metric3D})}{q(0.8, d_{MoGE}) - q(0.2, d_{MoGE})}
$$

$$
d^{metric} = s_{metric} \cdot d_{MoGE}, \quad C_{cam}^{metric} = \begin{pmatrix} R & s_{metric} \cdot T \\ 0 & 1 \end{pmatrix}
$$

**Implementation Details:**

DL3DV 因相機快速移動不適合深度訓練,僅 Stage-1 使用;Stage-2 移除 DL3DV;Stage-3 僅用 UE 合成資料以獲得 ground-truth metric depth。RealEstate10K 提供 74,766 段室內外視訊,DL3DV 由 3,000 段高品質視訊切為約 18,000 片段,UE 由 1,500 個場景模型渲染逾 10,000 段樣本,合計超過 100,000 段。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| RealEstate10K [Zhou et al. 2018] | Image-to-video / scene generation | 74,766 video clips (real-estate, mostly indoor) | train; 150 clips randomly sampled from the test split for evaluation in §5.1–5.2 |
| DL3DV [Ling et al. 2024] | Video diffusion training | ~3,000 curated videos segmented into ~18,000 clips | train (used only in stage 1; removed in stage 2 due to fast/shaky camera motion per Appendix A) |
| Unreal Engine (UE) renders (self-collected) | Video diffusion training with metric depth | 1,500 scene models, >10,000 rendered video samples | train (used in all three stages; sole dataset in stage 3 because it provides ground-truth metric depth) |
| WorldScore static benchmark [Duan et al. 2025] | World generation evaluation | 2,000 static test examples (indoor/outdoor, photorealistic/stylized) | test only (§5.3) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PSNR | Pixel-level fidelity between generated frame and ground-truth frame on RealEstate10K | yes |
| SSIM | Structural similarity between generated and ground-truth frames | no |
| LPIPS | Learned perceptual similarity (lower is better) | no |
| WorldScore Average | Aggregate score over 7 sub-dimensions on the WorldScore benchmark | yes |
| WorldScore: Camera Control | Adherence to the prescribed camera trajectory | no |
| WorldScore: Object Control | Controllability of object-level content | no |
| WorldScore: Content Alignment | Alignment between generated content and the prompt/input | no |
| WorldScore: 3D Consistency | Geometric consistency across viewpoints | no |
| WorldScore: Photometric Consistency | Photometric stability across frames | no |
| WorldScore: Style Consistency | Style coherence across the generated video | no |
| WorldScore: Subjective Quality | Human-judged visual quality | no |

### 6.3 Training and Inference Settings

訓練流程 (Appendix A) 採三階段：(1) 僅以 RGB 條件訓練 video model，使用全部三個資料集；(2) 加入 depth 條件聯合訓練 RGB-D，剔除 DL3DV (因 camera motion 過快不利 depth 監督)；(3) 凍結 DiT 參數，僅訓練新增的 ControlNet-style control blocks，且只在帶有 ground-truth metric depth 的 UE 資料上訓練。Backbone 為 Hunyuan-Video [Kong et al. 2024] 的 image-to-video model；單次生成 frame 數為 49；訓練時隨機從 [1, 1.25, 1.5, 1.75] 抽取 width-height ratio 以支援多比例輸出。

Inference 採 first-order Euler ODE solver (繼承 §3 的 flow-matching 公式，預測 velocity $u_t$)。長視頻採用 auto-regressive 與 smooth video sampling：將輸入切成重疊片段 (重疊長度為單一 segment 的一半)，重疊區以前一段生成結果作為 noise initialization；連續兩段推論完成後對重疊區做平均並注入 light-level noise，再執行最後一輪 denoising。World cache 採 point culling 策略 (不可見區域全部加入；可見區域若既有點 surface normal 與當前 view direction 夾角 >90° 則加入)，相較全量儲存可減少約 40% point 數量。

The paper does not specify hardware (e.g. GPU type/count), batch size, optimizer, learning-rate schedule, total training steps, inference resolution, or number of denoising steps.

### 6.4 Main Results

RealEstate10K novel view synthesis (Table 1):

| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Notes |
|---|---|---|---|---|
| SEVA | 16.648 | 0.613 | 0.349 | camera-parameter conditioning |
| ViewCrafter | 16.512 | 0.636 | 0.332 | point-cloud conditioning |
| See3D | 18.189 | 0.694 | 0.290 | point-cloud conditioning |
| FlexWorld | 18.278 | 0.693 | 0.281 | point-cloud conditioning |
| **Voyager** | **18.751** | **0.715** | **0.277** | RGB-D joint generation |

RealEstate10K 3DGS reconstruction (Table 2):

| Method | Post Rec. | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---|---|---|---|
| SEVA | VGGT | 15.581 | 0.602 | 0.452 |
| ViewCrafter | VGGT | 16.161 | 0.628 | 0.440 |
| See3D | VGGT | 16.764 | 0.633 | 0.440 |
| FlexWorld | VGGT | 17.623 | 0.659 | 0.425 |
| **Voyager** | VGGT | 17.742 | 0.712 | 0.404 |
| **Voyager (own depth)** | – | **18.035** | **0.714** | **0.381** |

WorldScore (Table 3, Average is the headline column):

| Method | WorldScore Avg | Camera Ctrl | Object Ctrl | Content Align | 3D Consist | Photo Consist | Style Consist | Subj Quality |
|---|---|---|---|---|---|---|---|---|
| WonderJourney | 63.75 | 84.6 | 37.1 | 35.54 | 80.6 | 79.03 | 62.82 | 66.56 |
| WonderWorld | 72.69 | 92.98 | 51.76 | 71.25 | 86.87 | 85.56 | 70.57 | 49.81 |
| EasyAnimate | 52.85 | 26.72 | 54.5 | 50.76 | 67.29 | 47.35 | 73.05 | 50.31 |
| Allegro | 55.31 | 24.84 | 57.47 | 51.48 | 70.5 | 69.89 | 65.6 | 47.41 |
| Gen-3 | 60.71 | 29.47 | 62.92 | 50.49 | 68.31 | 87.09 | 62.82 | 63.85 |
| CogVideoX-I2V | 62.15 | 38.27 | 40.07 | 36.73 | 86.21 | 88.12 | 83.22 | 62.44 |
| **Voyager** | **77.62** | 85.95 | **66.92** | 68.92 | 81.56 | 85.99 | **84.89** | **71.09** |

Voyager 在 RealEstate10K 上 PSNR 較最強 baseline FlexWorld 提升 0.473 dB，並在 SSIM/LPIPS 同步領先；自有 depth 直接做 3DGS 初始化進一步將 PSNR 推到 18.035 (而 baselines 必須額外跑 VGGT post-hoc 重建)。WorldScore 上 Average 較最強 baseline WonderWorld 高 4.93 分，Subjective Quality 為全表最高 71.09。

### 6.5 Ablation Studies

論文在 §5.4 與 Table 4 報告兩組 ablation：

- **World-consistent video diffusion (Table 4，於 WorldScore 子指標上比較)**：移除 depth condition 的 RGB-only 版 Camera Control 74.98、Content Alignment 48.92、3D Consistency 68.86；加入 depth 後分別躍升至 85.04 / 65.72 / 78.58 (分別 +10.06 / +16.80 / +9.72)；再加上 control blocks 達到 85.95 / 68.92 / 81.56。此 ablation 直接拆解了論文兩個核心貢獻 (depth fusion、context-based control blocks) 對應的指標增益，屬於 diagnostic 性質。
- **Long-range world exploration (Figure 8，僅 qualitative)**：(a) point culling — 全量儲存所有 point (302,992)、僅儲存不可見區 point (132,715)、加上 normal check (194,253) 三種策略比較，結論為 normal-check 視覺品質與全量相當但節省約 40% 儲存；(b) smooth sampling — 比較 w/ vs. w/o sampling 兩段 clip 的 transition 一致性。此組 ablation 回答了 cache 設計與 sampling 策略各自是否必要，但**僅以視覺與 point 數量呈現，未提供 long-video 場景下的量化指標** (例如 multi-clip PSNR/3D consistency drift)。

整體而言，Table 4 的 ablation 屬 diagnostic — 它對應論文宣稱的 method components 並顯示明顯增益；Figure 8 的長視頻 ablation 偏向 qualitative sanity check，缺乏量化是明顯不足之處。論文亦未對「是否使用 placeholder row Φ」、「partial depth vs partial RGB 單獨作為條件」等更細緻的設計選擇做拆解。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 在 RealEstate10K 上比較 SEVA、ViewCrafter、See3D、FlexWorld，且 WorldScore 上比較 WonderWorld、CogVideoX 等近期 SoTA。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時在 RealEstate10K (in-domain video + 3DGS reconstruction) 與 WorldScore (out-of-domain world generation) 兩個 benchmark 評估。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — Table 4 對 depth condition 與 control blocks 拆解到位，但 long-range 模組 (point culling、smooth sampling) 僅 qualitative，未量化。
- [missing] Has a scaling study (size, length, or compute) — 論文未報告 model size、training data 量、generation length 變化對指標影響的曲線。
- [missing] Has an efficiency / wall-clock comparison — 僅以「point culling 節省約 40% storage」帶過，未提供推論時間、memory peak、與 baselines 的 wall-clock 對比。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有 PSNR/SSIM/LPIPS/WorldScore 數字均為單次點估計，無誤差棒或多 seed 報告。
- [partial] Releases code / weights / data sufficient for reproducibility — 提供專案頁 https://voyager-world.github.io，但論文正文未明確聲明 code/weights/training data 釋出狀態，且 UE 自製資料、訓練超參數 (batch size、LR、steps、硬體) 皆未揭露，獨立復現難度高。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: World-Consistent Video Diffusion(jointly 生成 RGB-D)**:**partially supported**。Table 1、Table 4(p.7)的 ablation 確認了從 RGB-only 到 RGB-D conditioning 的提升,但 WorldScore 3D Consistency 81.56 仍落後 WonderWorld 86.87 與 CogVideoX-I2V 86.21(Table 3),說明「世界一致」這個 framing 在跨方法的 3D 一致性指標上沒有真的兌現。
- **C2: Efficient world caching + auto-regressive smooth sampling 支援 infinite exploration**:**weakly supported**。Figure 6(a)、Figure 8 提供視覺示意,Figure 8 的 point culling 結果說服力較強,但全文無 long-range 量化指標、無 cache 隨時間的 drift 曲線、無 inference 成本曲線,使「infinite」與「long-range」的主張停留在 demo 等級。
- **C3: Scalable video data engine**:**supported as a curation effort**。VGGT → MoGE 的 least squares 對齊(Eq. 5, App C, p.11)與 Metric3D quantile scaling(Eq. 6-8)在工程上是合理的合成方案,且確實產出 100K+ 訓練 clip;但作為「accurate camera + metric depth」的 claim,沒有對任何 depth GT 做誤差量化。
- **C4: First video model jointly generating RGB+depth with camera trajectories(Sec 1, p.3)**:**overclaimed**。"first" 屬於極端宣稱,但全文未對先前 image/video-level 的 RGB-D diffusion 工作做完整盤點,在沒有充分文獻調查支撐之下,此 claim 不應視為已被證明。

### 7.2 Fundamental Limitations of the Method

**靜態世界假設**:world cache 純粹累積 $(x,y,z,r,g,b)$ 點,並把它們重新投影回 partial RGB 與 partial depth 作為條件。這個 representation 在設計上不能表達移動物體、光照變化或場景動態,所以「explorable world」永遠是凍結時間點的世界。要支援動態場景,必須整個改成 4D 表示(例如帶 timestamp 的 dynamic Gaussian),不是參數調整可以彌補。

**Auto-regressive 漂移無修正機制**:每個 clip 之間僅靠 world cache 的點雲記憶銜接,smooth sampling 只負責顏色銜接、normal-check 只負責記憶體控制,整條 pipeline 沒有任何全域最佳化(類似 SfM 的 bundle adjustment)能修正累積的相機與幾何誤差。隨著 clip 數量增加,投影誤差會結構性地累積,這是 cache-based auto-regressive 範式本身的限制,而不是訓練多就能解決的問題。

**Pseudo-label 上限封頂**:訓練 label 完全來自 VGGT + MoGE + Metric3D 的組合,模型能學到的相機與深度精度,結構上不會超過這條 pipeline 中最弱一環(尤其 sky region 與 outdoor large-scale scene 上 Metric3D quantile scaling 並不穩健)。即使再放大資料量,精度都會卡在 data engine 自己的 noise floor。

**幾何條件本身的稀疏性瓶頸**:partial depth $\hat{D}_k$ 是從 cache 點雲投影出來的,當場景含薄結構(樹葉、纜線)、透明或反射表面時,cache 根本存不到可信的點,因此 DiT 在這些區域得不到任何幾何訊號,只能完全依靠 prior 進行 hallucination,這會反過來抵消「partial depth 比 partial RGB 更乾淨」這個論證的優勢。

### 7.3 Citations Worth Tracking

- **VGGT [Wang et al. 2025]**:整個 data engine 的相機與初始 depth 都由 VGGT 提供,Voyager 訓練 label 的天花板等同於 VGGT 的精度上限,理解它的失效模式就是理解 Voyager 的精度上限。
- **GEN3C [Ren et al. 2025]**:文中明指其屬於 partial-RGB conditioning 路線,卻未進入任何比較表;若要實證評估「加入 partial depth」帶來的真正增量,GEN3C 是最該補上的對照組。
- **FlexWorld [Chen et al. 2025]**:Voyager 全部主表中最強的 baseline,且也採 point-cloud-conditioned 路線,兩者差異本質上就是 RGB-only vs RGB-D conditioning,適合做為理解貢獻來源的對照。
- **WorldScore [Duan et al. 2025]**:Voyager 的招牌數字 77.62 來自此 benchmark,務必先讀 metric 定義(尤其是 3D Consistency 怎麼算),才能正確評估 Voyager 在該軸落後 WonderWorld 與 CogVideoX 的意義。
- **HunyuanVideo [Kong et al. 2024]**:Voyager 的 backbone(dual-stream / single-stream DiT、3D-VAE、velocity prediction)完全繼承自此,Voyager 能或不能做的事很大一部分是 base model 決定的。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在 single-pass 49 frames 之外、跨多個 clip 累積後,Voyager 的 3D 一致性如何隨 trajectory 長度衰減?是否存在量化的 drift 曲線?
- [ ] 在 NYU、KITTI 或 ScanNet 等帶 metric depth GT 的 benchmark 上,Voyager 生成的 depth 與其 data engine label 的 AbsRel / $\delta < 1.25$ 是多少?
- [ ] 為何在 WorldScore 自家的 3D Consistency 軸上 Voyager(81.56)反而落後 WonderWorld(86.87)與 CogVideoX-I2V(86.21)?是 metric 衡量的「一致性」與作者定義的「world-consistent」根本不同,還是方法在該軸真的較弱?
- [ ] 與最直接同類工作 GEN3C(Ren et al. 2025)在 RealEstate10K 與 WorldScore 上的 head-to-head 結果是什麼?「partial RGB+D 比純 partial RGB 好」這個論證在最相近 baseline 上是否仍成立?
- [ ] 第三階段 ControlNet 只在 UE 合成資料上訓練,若改在 real RGB-D(例如 ScanNet、ARKitScenes)上訓練,real-world 上的 camera control 與 3D consistency 會升或降?
- [ ] World cache 在數十個 clip 之後的記憶體峰值、point culling 後的絕對點數、render FPS 為何?point culling 與單純 voxel-hash / octree 比較的具體 trade-off?
- [ ] Smooth video sampling 中重疊區段 noise re-init 與額外 denoise 步驟,對 inference 時間與 PSNR/LPIPS 的量化影響為何?

### 8.2 Improvement Directions

1. **加入 FVD 與 human eval(高可行性)**:目前所有指標都是 frame-wise,加入 FVD 與小規模 human eval 立即能讓「視覺品質與時間一致性」獲得目前 PSNR/SSIM/LPIPS 偵測不到的證據;這是最低成本、最高 ROI 的補強。
2. **補上對 GEN3C 的直接對照(高可行性)**:GEN3C 是最接近的 partial-RGB conditioning 同期工作,在 Table 1-3 加入它,直接驗證「加 partial depth」是否真的是性能來源,而非 data engine 或 base model 帶來的增益。
3. **量化 long-range drift(中等可行性)**:沿著生成的 trajectory 在不同距離下回投影到 ground truth depth 並計算 re-projection error,或在合成 UE 場景上做 PSNR-vs-clip-index 曲線,讓 "long-range" 主張變成可驗證命題;邏輯依據在於 cache-based auto-regressive 缺乏 global correction,理論上一定有可量化的 drift。
4. **以 NYU/KITTI 評估 data engine 與生成 depth(中等可行性)**:現有 pipeline 把 VGGT/MoGE/Metric3D 的輸出當 GT,只要用標準 depth benchmark 量一次 AbsRel/$\delta$ 就能釐清訓練 label 的天花板,這直接對應「Pseudo-label 上限封頂」這個結構性問題。
5. **第三階段 ControlNet 改用 real + synthetic 混合(中等可行性)**:目前 stage-3 只看 UE,改混合 ScanNet、ARKitScenes 等真實 RGB-D 來源,可緩解合成域偏置,理論依據是 real distribution 的 occlusion 與材質統計與 UE 不同,讓 control block 看到真實分佈會直接改善 real-world camera-following。
6. **加入 cache 級別的全域微調步驟(較大改動)**:每生成 N 個 clip 後對 world cache 做一次輕量 bundle-adjustment 風格的相機/深度微調(可採 differentiable rendering),對應修正「auto-regressive 漂移無修正機制」這個結構性限制;邏輯依據是只要還在 cache-based 範式內,就必須有某種全域最佳化點才能收斂誤差。
7. **將 cache 升級為時間維度的 4D 表示(最大改動)**:把點雲帶上 timestamp 或改成 dynamic Gaussian splat,可從根本鬆綁「靜態世界假設」這個 fundamental limitation,讓框架支援動態場景;這是把 Voyager 從「探索靜態世界」推進到「探索動態世界」的最大潛在突破點,但需要重做 data engine 與訓練資料。
