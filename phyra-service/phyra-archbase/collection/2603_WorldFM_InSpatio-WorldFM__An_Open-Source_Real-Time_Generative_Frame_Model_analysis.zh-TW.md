<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# InSpatio-WorldFM — InSpatio-WorldFM: An Open-Source Real-Time Generative Frame Model

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | InSpatio-WorldFM |
| Paper full title | InSpatio-WorldFM: An Open-Source Real-Time Generative Frame Model |
| arXiv ID | 2603.11911 |
| Release date | 2026-05-06 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.11911 |
| PDF link | https://arxiv.org/pdf/2603.11911v3 |
| Code link | https://github.com/inspatio/worldfm |
| Project page | https://inspatio.github.io/worldfm/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Donghui Shen | InSpatio / Zhejiang University | — | first listed (alphabetical) |
| Guofeng Zhang | Zhejiang University, State Key Lab of CAD&CG / InSpatio | http://www.cad.zju.edu.cn/home/gfzhang/ | team lead / principal investigator |
| Haomin Liu | InSpatio / Zhejiang University | — | team member |
| Haoyu Ji | InSpatio / Zhejiang University | — | team member |
| Jialin Liu | InSpatio / Zhejiang University | — | team member |
| Jing Guo | InSpatio / Zhejiang University | — | team member |
| Nan Wang | InSpatio / Zhejiang University | — | team member |
| Siji Pan | InSpatio / Zhejiang University | — | team member |
| Weihong Pan | InSpatio / Zhejiang University | — | team member |
| Weijian Xie | InSpatio / Zhejiang University | — | team member |
| Xiaojun Xiang | InSpatio / Zhejiang University | — | team member |
| Xiaoyu Zhang | InSpatio / Zhejiang University | — | team member |
| Xianbin Liu | InSpatio / Zhejiang University | — | team member |
| Yifu Wang | InSpatio / Zhejiang University | — | team member |
| Yipeng Chen | InSpatio / Zhejiang University | — | team member |
| Zhewen Le | InSpatio / Zhejiang University | — | team member |
| Zhichao Ye | InSpatio / Zhejiang University | — | team member |
| Ziqiang Zhao | InSpatio / Zhejiang University | — | team member |

### 1.2 Keywords

world model, frame model, real-time generation, novel view synthesis, diffusion transformer, multi-view consistency, spatial memory, distribution matching distillation

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| PixArt-Σ (Chen et al.) | base model | Efficient text-to-image DiT chosen as the Stage I image-generation backbone of InSpatio-WorldFM. |
| RTFM (World Labs) | predecessor | Earlier real-time frame model with limited public details; motivates and is directly contrasted in spatial-memory design. |
| StarGen | baseline | Warps features from posed keyframes for spatial conditioning; compared as alternative spatial-memory strategy. |
| DMD / Distribution Matching Distillation (Yin et al.) | influence | Few-step distillation method used in Stage III to enable 2-step real-time denoising. |
| MapAnything | influence | Feedforward 3D foundation model used to estimate per-frame poses, depths, and the global point cloud for training data. |
| PRoPE (Projected Relative Positional Encoding) | influence | Camera-aware relative positional encoding adopted to inject geometry directly into self-attention. |
| Genie 3 / HY-World / LingBot-World | concurrent | Concurrent video-based world models cited as the prevailing paradigm InSpatio-WorldFM departs from. |

## 2. Research Overview

### 2.1 Research Topic

本論文研究「即時互動式 3D 世界模型」的生成範式。相對於現行以 video diffusion 為基礎、需在時間視窗內聯合產生多幀而導致互動延遲與長期空間漂移的 world model,作者提出 InSpatio-WorldFM:一個 frame-based 的世界模型,將每一幀獨立生成,並透過顯式 3D 錨點(point cloud rendering)與隱式空間記憶(reference frame 的 self-attention)維持跨視角的多視圖幾何一致性。系統由離線多視圖一致性模型(提供 3D 錨點與外觀參考)與線上 frame model(即時推論)構成,並以三階段訓練(預訓練 PixArt-Σ → 加入相機條件與空間記憶的中段訓練 → 以 DMD 進行 2-step few-step distillation)將影像生成器轉換為可即時部署於消費級 GPU 的互動式生成器。整體目標是以 frame-based 路線取代 video-based world model,在低延遲下提供穩定的 3D 場景結構與細節。

### 2.2 Domain Tags

- computer vision
- generative models
- world models
- spatial intelligence
- novel view synthesis

### 2.3 Core Architectures Used

- **PixArt-Σ (Diffusion Transformer)**:作為 Stage I 預訓練的影像生成 backbone,提供高品質且推論吞吐高的 text-to-image DiT 基礎,以利後續即時化部署。
- **Frame-based DiT with self-attention-only condition injection**:本論文核心架構,將 noisy target latent $z_t$、point cloud rendering $\hat{x}_{tgt}$ 與 reference image $x_{ref}$ 沿 width 維度 spatial-concat 後,透過 patch embedding 與 self-attention 完成單幀條件生成。
- **PRoPE (Projected Relative Positional Encoding)**:以 camera projection matrix $P_i$ 對 query/key/value 做相機相依的線性變換,將跨視角幾何對應關係原生注入 self-attention,取代 Plücker ray embedding 與純參數注入兩種替代方案。
- **Hybrid Spatial Memory**:結合「explicit 3D anchor(全域 point cloud 重投影到目標視角)」與「implicit memory(reference frame token 透過 self-attention 被檢索)」,分別維持粗粒度幾何與細粒度外觀。
- **MapAnything (feedforward 3D reconstruction)**:作為訓練資料 pipeline 的一部分,從真實影片估計 per-frame camera pose、depth 與 global point cloud。
- **Distribution Matching Distillation (DMD)**:於 Stage III 將多步 diffusion teacher 蒸餾為 2-step student,透過 frozen real-score 與動態 fake-score 之差作為 generator 的梯度訊號,並搭配 regression loss 穩定訓練,實現消費級 GPU 上的即時推論。
- **VAE encoder/decoder $E, D$**:提供 latent diffusion 所需的潛空間 $z = E(x)$,推論時亦透過 latent caching 等工程優化加速即時生成。

### 2.4 Core Argument

作者識別出當前 world model 的根本問題在於「以 video diffusion 為骨幹」這個架構選擇本身,而非單純的工程問題。Video-based 模型必須以雙向 attention 同時處理整個時間視窗中的多幀,即使套用 distillation 也會有 window-level 的依賴,使 truly real-time 的互動本質上不可能;同時,video model 的訓練目標偏向短期時間連續性,缺乏顯式的 3D 全域約束,導致長序列下空間誤差會累積成幾何漂移。從這個診斷可推得三個必要設計:(1)放棄逐視窗生成,改為「frame-by-frame 獨立生成」,才能徹底消除 window 級延遲;(2)由於放棄了時序鄰幀提供的隱含一致性,必須以「顯式 3D 錨點」(把全域 point cloud 重投影到目標視角)替代,才能在單幀生成下維持跨視角幾何;(3)為避免顯式錨點過強而模型只「複製」點雲、忽略外觀補全,需再加上「隱式空間記憶」(reference frame token 透過 self-attention 被檢索),並以漸進式條件注入(先給 reference,再加 anchor)強制模型發展兩條互補通道。最後,即時化只能靠 few-step distillation(DMD,2 步去噪)來補足計算預算,並選擇推論吞吐高的 PixArt-Σ 作為 Stage I 基底。論文的核心論證是:唯有「frame-based 架構 + 顯式 3D 錨點 + 隱式記憶 + few-step distillation」這個組合,才能同時逼近 video model 的視覺品質、保持 3D 一致性,並實現消費級 GPU 上的零延遲互動,因此這條技術路線是邏輯上必要而非偶然的選擇。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題 "InSpatio-WorldFM: An Open-Source Real-Time Generative Frame Model" 直接揭示三個核心定位：open-source、real-time、frame model。前兩者是相對於封閉商業系統（如 Genie 3）與高延遲 video-based world models 的差異化主張，而 "frame model" 一詞則暗示作者刻意與 video model 切割，把它當作另一種 paradigm 而非 video model 的子類。

Abstract 採用「對比—主張—方法—結果」四段式論述。第一句先樹立對立面：video-based world models 倚賴 sequential frame generation 與 window-level processing，因此 "incur substantial latency"。第二句提出本文的反命題：frame-based paradigm，每張 frame 獨立生成，達到 low-latency real-time spatial inference。第三句則回應一個自然的質疑——若 frame 獨立生成，如何維持跨 view 的一致性？作者以兩個技術詞彙作答：explicit 3D anchors 加上 implicit spatial memory，並聲稱可同時保留 global scene geometry 與 fine-grained visual details。

第四句揭示工程路徑：progressive three-stage training pipeline，從 pretrained image diffusion model 出發，經 controllable frame model，最終以 few-step distillation 蒸餾為 real-time generator。最後以 "consumer-grade GPUs" 作為部署訴求收尾，暗示後文會以 RTX 4090 等可及硬體為實驗平台。Abstract 的修辭策略已經為 §1 的三大批評（latency、spatial drift、frame-vs-video paradigm）鋪好梗概。

### 3.2 Introduction

(610 words)

Introduction 採取「大背景—痛點—對手—我們的解法」結構。開場先承認 video generation 的進展：強 motion priors、appearance、camera dynamics 的學習能力，並列舉 HY-World、LingBot-World、Genie 3 等近期作品，使讀者進入 world model 的研究脈絡，並暗示這已經是近期社群關注的主題。

接著作者切入論文的真正動機：「Despite this progress, most existing world models are still built upon video generation architectures.」此句明確圈出批判對象。隨後以兩個 bold 標題列出 video-based 範式的兩大缺陷：(1) Interactive latency remains inevitable——只要採用 bidirectional attention 與 full-window decoding，每一步推論都必須處理整個 window，distillation 也只是緩解而非根除；(2) Spatial errors accumulate over time——video model 主要為短期 temporal continuity 訓練，缺乏 enforce global spatial constraints 的機制，長序列下會出現 structural drift。這兩點構成全文方法設計的反向約束。

第三段引入直接競爭者：World Labs 的 RTFM。作者以兩句話將 RTFM 定位為「方向正確但細節不足、且不開源」的工作，藉此為自己的開源、技術透明的貢獻創造空間。隨後正式提出 InSpatio-WorldFM，並重申其 frame-based 屬性：每張 frame 直接從 spatial information 生成，而非作為連續 frame sequence 的一部分；這使得 scene geometry 可在不犧牲低延遲的前提下保持一致。

接著作者以 bullet 列出三個 key components：(1) Multi-view consistent training data curation，提供穩定跨視角學習訊號；(2) Progressive three-stage training pipeline，呼應 abstract 中的三階段；(3) Real-time generation enabled by few-step distillation，具體點到 2-step denoising 的選擇。最後以一段總結性宣稱收束：這些元件共同構成 real-time spatial intelligence 的 efficient foundation，並重申對 traditional video-based world models 的對位。

整段 introduction 的修辭工程相當細緻：作者先讓讀者接受 "video-based 是當前主流且 plausible" 的事實，再用兩個機制性論點（latency 是 architecture-induced、spatial drift 是 objective-induced）說服讀者必須跳出 video paradigm。然後 RTFM 提供了 "別人也走這方向" 的合法性，但同時用 "技術細節有限、不開源" 留下了論文的貢獻空間。最後三個 bullet 把抽象主張轉換成可驗證的工程承諾，明確 setup 後續 §2 對應的三個實作章節：data、architecture、distillation。對讀者而言，introduction 結束時應該已經能預期 §2 會分別解釋這三項，並且每一項都會回應前面提出的痛點。

### 3.3 Related Work / Preliminaries

(330 words)

本論文沒有獨立的 Related Work 節，而是把相關工作的引用與批評分散嵌入 Introduction（§1）以及 Method 各小節的開場與技術選型討論中。Walkthrough 因此把與相關工作及 preliminaries 直接相關的段落視為一個整體：包含 §1 對 video-based world models（[16, 38, 26, 11, 48, 29]）與 frame-based RTFM [37] 的對比、§2.3 對 base model 的選型理由（PixArt-Σ vs. 其他 DiT）、§2.4.1 對 camera pose encoding 三派方法（Plücker、PRoPE、pure parametric）的比較、以及 §2.4.1 對 spatial memory 設計（RTFM 的 posed frames 與 StarGen 的 warped feature）的對位。

這種「分散式」relate-while-design 的寫法服務一個目的：每個技術選擇都立刻對應一個被否決的替代方案，使方法章節同時承擔 ablation 的修辭功能。例如在 camera pose encoding 段落，作者並非單純說 "我們用 PRoPE"，而是先描述 Plücker 的局限是 additive（沒有直接調制 attention），再指出 pure parametric 缺乏明確 geometric structure，最後才得出 PRoPE 是 fastest convergence 與 most stable camera control 的選擇。

在 spatial memory 段落，作者明確點名 RTFM 與 StarGen [45] 的設計：RTFM 把 posed frames 當 primitive memory、StarGen warp posed keyframes 的 features，作者藉此突出自己的 hybrid 設計（explicit 3D anchors + implicit memory）相對於 single-modality memory 的優勢。

Preliminaries 部分集中在 §2.2 與 §2.5 兩處：§2.2 給出 latent diffusion 的標準損失 $L = \mathbb{E}_{z_{\text{tgt}}, \epsilon, t}[\|\epsilon - \epsilon_\theta(z_t, t, C)\|^2]$，並定義 condition set $C = \{x_{\text{ref}}, \pi_{\text{ref}}, \pi_{\text{tgt}}, \hat{x}_{\text{tgt}}\}$；§2.5 則簡要交代 DMD [42] 的兩個並行 score model 設計與 KL 近似。這兩段足以讓讀者跟上後續方法描述，但顯然假設讀者已熟悉 latent diffusion 與 score distillation。

### 3.4 Method (overview narrative)

(330 words)

§2 採取「framework overview → formulation → 三階段訓練」的層級式敘事。§2.1 以 Fig. 2 為錨：將系統切成 offline 與 online 兩階段——offline 用 multi-view consistent model（如 [49, 14]）或 panoramic generator（[31, 13, 46]）從單張 input image 產生 reference appearances 與 3D anchors；online 則由一個 frame model 進行 real-time inference。這個 offline/online 切分是整體論述的基礎：只有把昂貴的 multi-view consistency 計算外推到 offline，online 端才能維持 frame-based 的 low latency。

§2.2 把問題形式化為 conditional generative frame model：從 reference image $x_{\text{ref}}$ 與其 pose $\pi_{\text{ref}}$，加上 user-defined target pose $\pi_{\text{tgt}}$ 出發，生成 target-view image $x_{\text{tgt}}$。在 latent diffusion 框架下，模型學習 $\epsilon_\theta(z_t, t, C)$，condition 集 $C$ 包含 $x_{\text{ref}}$、兩個 camera pose 以及 $\hat{x}_{\text{tgt}}$（target viewpoint 的 point cloud rendering，用 [34, 36, 35, 21] 等 3D foundation model 產生）。$\hat{x}_{\text{tgt}}$ 在這裡被定義為 "explicit 3D spatial anchor"，這是後文 hybrid memory 的一條腿。

§2.2 末段宣告 three-stage pipeline 並給每階段一句話的功能定位：Stage I (Pre-Training) 選擇高效率的 DiT backbone；Stage II (Middle-Training) 把 image generator 改造為 controllable frame model with spatial memory；Stage III (Post-Training) 透過 DMD 蒸餾為 few-step generator。這個三段宣告同時也是後續 §2.3、§2.4、§2.5 的目錄。

§2.3 解釋為何選 PixArt-Σ：兼顧 fidelity 與 throughput，符合 real-time 需求。§2.4 是論文最厚的一段，分為 Fundamental Frame Model（架構、camera pose encoding 三派比較、hybrid spatial memory、training data、training strategies）與 Finetuning with Synthetic Data（Unreal Engine 構造的 ground-truth pose/depth 資料）。§2.5 則交代 DMD 的兩個關鍵實證發現：2-step denoising 比 1-step 更能保留 fine-grained details，以及在 1000-step schedule 下 $t_{\text{mid}} = 200$ 是 coarse-to-fine 切分的最佳點。整段 method 的論述軸線是「資料、架構、記憶、蒸餾」四件事如何各自回應 §1 的痛點。

### 3.5 Experiments (overview narrative)

(280 words)

§3 Evaluation 是一個輕量、以 qualitative 為主的章節，並沒有提供量化基準比較或 ablation 表格——這是 technical report 風格而非 conference paper 風格。整節只有大約三段文字，加上 Fig. 4 至 Fig. 8 五張定性圖。

評估目標被明確界定為兩件事：spatial consistency 與 generation quality，並橫跨 middle-trained fundamental frame model 與 post-trained distilled variant 兩個版本。第一段對應 Fig. 4：每個範例由一張 reference image 加上 10 張不同 camera viewpoint 的 rendered frames 組成。作者宣稱 fundamental frame model 在大幅 viewpoint change 下仍能保持 geometric structure 與 appearance consistency，並能 adapt 到 novel perspectives，藉此論證模型確實學到 3D spatial reasoning。

第二段轉向 distillation 與 real-time deployment 的 trade-off。具體數據：512×512 解析度下，distilled model 在單張 H-series GPU 上達到約 25 FPS，藉助 KV-cache management 與 efficient VAE latent caching 等工程優化；在 RTX 4090 上仍可達 10 FPS。這是全文唯一的量化效率宣稱，也是 "consumer-grade GPUs" 訴求的實證。隨後作者承認 distillation 帶來 quality-speed trade-off，但聲稱 perceptual difference 在實務上極小，並透過 fundamental 與 distilled 版本的視覺比對支持此說法——對照可見於 Fig. 5–7 與 Fig. 4 的關係。

第三段是 long rendering / temporal stability 的論述：在不同 historical frame contexts 下，模型仍能在不同 viewing distances 上維持 consistent geometry 與 fine details（Fig. 8），用以驗證 hybrid spatial memory 設計的有效性。整節缺乏與 baseline（如 RTFM、StarGen、Voyager、Gen3C）的直接 quantitative 對比，亦未報告 PSNR / LPIPS / FID 等指標，這是讀者需注意的重要 gap，也是 §3.6 limitation 之外的另一個論述弱點。

### 3.6 Conclusion / Limitations / Future Work

(290 words)

§4 Discussion and Conclusions 結構為 "重申貢獻 → Limitations → Future Work"，是技術報告的標準收束模式。

重申段（§4 開頭）以兩句話總結：採用 frame-based generation paradigm，並結合 explicit 3D anchors 與 implicit spatial memory，達到 multi-view spatial consistency 與 low-latency real-time inference。這裡作者刻意使用 "open-source" 與 "spatial intelligence" 這兩個詞，把整篇論文的定位從一個工程實作擴張到一個社群基礎建設與更廣泛的 AI 願景。

§4.1 Limitations 列出三項，恰好對應 method 的三個主要設計取捨：(1) Stable generation of dynamic content——frame-based model 與 multi-view consistency 訓練資料中 dynamic content 都很有限，因此動態場景生成仍不穩定。這實際上是把 video model 為了避免的 "long temporal modeling" 問題部分讓渡出去後的副作用。(2) Limited motion boundary——historical memory 依賴 multi-view consistent observations 或 panoramic observations，但這些 generation model 計算昂貴、只能 offline 運作，導致 online inference 出現 motion boundaries（即可探索範圍受限於 offline 預先生成的 scene）。(3) Interactive visual stability——frame-based 設計缺乏 consecutive frames 之間的 temporal constraints，導致互動時出現 frame jitter。這三項 limitation 誠實地揭露了 frame paradigm 對 video paradigm 的取捨成本：用 latency 與 spatial consistency 換來了 dynamic 能力與 temporal smoothness 的下降。

§4.2 Future Work 分兩個層次：效率端，作者點名 linear attention、efficient caching、VAE 優化等成熟技術，目標是讓 spatial inference 跑到 edge devices；以及一個視覺保真度的擴展——以 Gaussian Splatting (GS) primitives 取代 point cloud 作為 3D anchor，以提升 reflective effects。功能端則 highlight 兩個方向：(1) 改善 dynamic content 生成，(2) generation range 的 real-time expansion。這兩個方向恰好回應前述 limitation 的第 (1) 與 (2) 項，但第 (3) 項 frame jitter 並未在 future work 中明確收束，這是論文遺留的 open issue。

## 4. Critical Profile

### 4.1 Highlights

- 提出 frame-based 世界模型範式,將每一幀獨立生成以消除 video diffusion 在時間視窗上的雙向 attention 依賴,從架構層面繞開「window-level」延遲(page 2 §1)。
- 設計 hybrid spatial memory:以 point cloud rendering 作為顯式 3D 錨點、以 reference frame 透過 self-attention 作為隱式記憶,兩者沿 width 維度與 noisy latent 拼接後送入 DiT(Fig. 3, page 5)。
- 採用 PRoPE 將相機投影矩陣 $P_i$ 直接套用到 attention 的 query/key/value 上,作者指出在三種 pose encoding 中收斂最快、相機控制最穩定(page 6)。
- 三階段訓練 pipeline:Stage I 以 PixArt-Σ 作為基底、Stage II 加入相機條件與空間記憶並以 UE 合成資料微調、Stage III 以 DMD 蒸餾為 few-step generator(page 4 §2.2)。
- 提出 progressive condition injection:訓練早期僅給 reference frame、之後再引入 explicit anchor,以避免模型只「複製」point cloud 而忽略隱式記憶通道(page 6–7)。
- 在 DMD 蒸餾中發現 2-step denoising 顯著優於 1-step,且中間時間步 $t_{mid}=200$(在 1000 步 schedule 下)為最佳折衷(page 7–8)。
- Random anchor masking 作為後期正則化策略,降低模型對顯式 anchor 的依賴並維持隱式記憶通道的可用性(page 7)。
- 在 $512\times512$ 解析度下,單張 H-series GPU 上達到約 25 FPS,並可在 RTX 4090 消費級 GPU 上以 10 FPS 運行(page 12)。
- 訓練資料同時涵蓋 internet videos、DL3DV、RealEstate10K、自採視訊與 UE 合成資料,並設計 4 reference + 12 target 的取樣協議與 random shuffling/masking(page 6)。
- 開源宣告:程式碼釋出於 https://github.com/inspatio/worldfm,並提供 project page demo(page 1)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- **Stable generation of dynamic content**:frame-based 模型與多視圖一致性訓練資料皆缺乏動態內容,難以穩定生成動態場景(page 13 §4.1)。
- **Limited motion boundary**:歷史記憶仰賴 offline 多視圖一致性模型或全景觀測,這些離線生成模型的計算與記憶體成本過高,只能離線運行,因此線上推論時必然存在「motion boundary」(page 13 §4.1)。
- **Interactive visual stability**:由於放棄 frame 之間的時序約束,互動過程出現可見的 frame jitter(page 13 §4.1)。

#### 4.2.2 Phyra-inferred

- **完全沒有任何量化評估**:§3 Evaluation(page 12–13)整節僅有 Fig. 4–8 的 qualitative results,沒有 PSNR、SSIM、LPIPS、FVD、reprojection error 或 human study 的任何數值,因此「strong multi-view coherence」「minimal perceptual difference」等核心結論無法被驗證或反駁。
- **沒有 baseline 直接比較**:RTFM、StarGen、HY-World、LingBot-World、Genie 3、Voyager、Gen3C、Matrix-game 等 video-based world models 在 §1 與 §2.4.1 被多次援引作為對照動機(page 2、page 6),但全文沒有任何一張並排輸出或匹配軌跡的對比。
- **所有「empirically we find」設計選擇皆無 ablation**:PRoPE 對 Plücker 對 parametric(page 6)、hybrid memory 對 anchor-only 對 ref-only(page 6)、progressive 對 joint condition injection(page 6–7)、2-step 對 1-step DMD 與 $t_{mid}$ 掃描(page 7–8)四項主要技術主張均以文字宣稱,沒有對應曲線或表格。
- **「frame-by-frame independent」與 reference frame 機制存在內部張力**:Fig. 2 明確標示「Update Global Scene at keyframes」,代表 frame model 在 keyframe 區間內無狀態、跨 keyframe 仍有狀態;這個 state semantics 從未被分析,使得「真正零延遲」只在 keyframe 內部成立。
- **GPU 與解析度揭露不完整**:page 12 僅寫「a single H-series GPU」未指明 H100 / H800 / H200,而 25 FPS / 10 FPS 都鎖定 $512\times512$,沒有任何解析度 scaling 的數據。
- **訓練規模與算力預算完全缺失**:訓練 clip 數量、step 數、訓練時長、所用 GPU 規格與卡時皆未揭露,使得結果無法被同等規模重現。
- **誤差傳遞分析缺失**:幾何品質實際上由 MapAnything 等 feedforward 重建模型決定(page 6),作者承認「inevitably contain errors」並以 UE 微調修補(page 7),但 offline 誤差到 online 渲染的影響從未被量化。
- **Section 3 缺乏實驗協議**:沒有定義 test split、軌跡取樣方式、長度、評估場景數,僅以「diverse scene types」泛稱,無從判斷 cherry-picking 的程度。

### 4.3 Phyra's Judgment (summary)

InSpatio-WorldFM 的概念再框架化是有價值的:把「real-time world model」從 video diffusion 的窗格依賴中拉出來,改用 frame-based DiT + hybrid memory + few-step distillation 的組合,理論上同時解掉 latency 與長序漂移兩個問題。但這份 technical report 形式的論文沒有提供任何量化實驗、baseline 比較或 ablation,所有設計取捨都以「empirically we find」一句帶過,因此目前可信的部分主要是工程整合與架構主張,而不是實證證據。核心未解問題是:在匹配算力下,frame-based 是否真的優於 video-based world model,以及 keyframe 邊界處的 motion boundary 究竟有多明顯。

## 5. Methodology Deep Dive

### 5.1 Method Overview

InSpatio-WorldFM 將「即時互動式 3D 世界生成」重構為 frame-by-frame 的條件式 novel-view synthesis 問題。給定 reference image $x_\text{ref}$、其相機 pose $\pi_\text{ref}=(K_\text{ref}, E_\text{ref})$、目標 pose $\pi_\text{tgt}$,以及由 3D foundation model(MapAnything 等)從 reference frame group 重建出的全域 point cloud 在目標視角下的重投影 $\hat{x}_\text{tgt}$,模型需要產生與 $x_\text{ref}$ 幾何一致的 $x_\text{tgt}$。整個生成過程定義在 latent diffusion 框架下,以 VAE encoder $\mathcal{E}$ 與 decoder $\mathcal{D}$ 將 $H \times W \times 3$ 的 RGB 影像映射到 latent space $z=\mathcal{E}(x)$,並學習一個條件去噪網路 $\epsilon_\theta(z_t, t, C)$,其中條件集合 $C=\{x_\text{ref}, \pi_\text{ref}, \pi_\text{tgt}, \hat{x}_\text{tgt}\}$ 同時包含 implicit memory(reference frame)與 explicit anchor(point cloud rendering)。

架構上,InSpatio-WorldFM 採用 self-attention-only DiT(以 PixArt-Σ 為 Stage I 預訓練 backbone)。三個輸入 token 流——noisy target latent $z_t$、point cloud rendering $\hat{x}_\text{tgt}$、reference frame $x_\text{ref}$——經過 shared patch embedding 與 sinusoidal positional embedding 後,沿 **width 維度** 空間拼接成統一序列,再透過 stacked DiT blocks 進行 joint self-attention。相機幾何不以加性 ray embedding 注入,而是採用 **Projected Relative Positional Encoding (PRoPE)**:對每個 view $i$ 的相機投影矩陣 $P_i$,對 query 套用 $P_i^\top$、對 key/value 套用 $P_i^{-1}$,並結合 2D RoPE 處理影像內部空間結構。這種設計讓 attention 直接以幾何 correspondence 推理跨視角關係,而非靠模型隱式學習。最終輸出沿 width 切回三段,只保留 target 段送回 VAE decoder 還原 $I_\text{tgt}$。

訓練採三階段管線:Stage I 以 PixArt-Σ 取得 high-fidelity image prior;Stage II middle-training 引入 camera control、hybrid spatial memory 與 progressive condition injection(早期僅給 reference,後期才加入 anchor,並隨機 mask anchor 以避免過度依賴顯式 prior),並先在真實影片(DL3DV、RealEstate10K、自採資料)上以 16 幀採樣(4 幀作 reference group 構建 global point cloud、12 幀作 target)訓練,再以 Unreal Engine 合成資料微調以校正 feedforward 重建誤差;Stage III 以 **Distribution Matching Distillation (DMD)** 將 multi-step diffusion 蒸餾為 2-step 生成器,中間 timestep $t_\text{mid}=200$(在 1000-step schedule 上),第一步處理粗略結構、第二步精修細節,使 512×512 解析度下達到 H 系列 GPU 上約 25 FPS、RTX 4090 上 10 FPS 的即時推論。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Inputs (B = batch size, H = W = 512 baseline)
   ├→ x_ref         [B, 3, H, W]           reference RGB
   ├→ x̂_tgt        [B, 3, H, W]           point cloud rendering at π_tgt
   ├→ z_t (noisy)   [B, c_z, H/8, W/8]     noised target latent (c_z = ?)
   ├→ π_ref, π_tgt  [B, 3, 4] each         camera extrinsics (K, E)
   └→ t (timestep)  [B]

VAE Encoder  E(·)
   x_ref       ──→ z_ref     [B, c_z, H/8, W/8]
   x̂_tgt      ──→ ẑ_tgt    [B, c_z, H/8, W/8]
   (z_t already in latent space)

Shared Patch Embedding (patch size p = ?)
   each latent  [B, c_z, H/8, W/8]
        ──→     [B, N_patch, d]            with N_patch = (H/8/p)·(W/8/p)
                                            d = hidden dim (= ?)

Spatial Concatenation along WIDTH dimension
   [z_t_tokens ; ẑ_tgt_tokens ; z_ref_tokens]
        ──→     [B, 3·N_patch, d]

+ Sinusoidal Positional Embedding
        ──→     [B, 3·N_patch, d]

Camera Conditioning (PRoPE matrices from π_ref, π_tgt)
   per-view P_i derived from (K_i, E_i)
        ──→     used inside attention only (not added to tokens)

DiT Block × L  (L = ?)
   ┌─────────────────────────────────────────────────┐
   │  LayerNorm                                      │
   │  Q, K, V projection           [B, 3·N_patch, d] │
   │  Apply PRoPE:                                   │
   │     Q ← P_i^⊤ · Q                               │
   │     K ← P_i^{-1} · K          (K, V same form)  │
   │     V ← P_i^{-1} · V                            │
   │  + 2D RoPE for intra-image structure            │
   │  Self-Attention (full, joint over all 3 views)  │
   │  Residual + LayerNorm                           │
   │  FFN (MLP, ratio = ?)                           │
   │  Residual                                       │
   └─────────────────────────────────────────────────┘
        ──→     [B, 3·N_patch, d]

Width-wise Split → keep target slice only
        ──→     [B, N_patch, d]

Unpatchify / Linear head
        ──→     ẑ_tgt_pred   [B, c_z, H/8, W/8]

VAE Decoder  D(·)
        ──→     I_tgt        [B, 3, H, W]

Sampling: DMD 2-step (T=1000 schedule, t_mid = 200)
   step 1: t = T  → t_mid     (coarse structure)
   step 2: t = t_mid → 0      (detail refinement)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 VAE Encoder / Decoder

**Function:** 將 RGB 影像在 latent space 與 pixel space 之間互轉,降低 diffusion 計算量。

**Input:**
- Name: $x_\text{ref}$, $\hat{x}_\text{tgt}$, $x_\text{tgt}$
- Shape: $[B, 3, H, W]$,$H=W=512$(baseline configuration,§3 Evaluation)
- Source: Reference image、point cloud rendering、ground-truth target

**Output:**
- Name: $z_\text{ref}$, $\hat{z}_\text{tgt}$, $z_\text{tgt}$
- Shape: $[B, c_z, H/8, W/8]$
- Consumer: Patch embedding(編碼路徑); 最終影像輸出(解碼路徑)

**Processing:**

採用 PixArt-Σ 預訓練 VAE,空間下採樣率為 8。每個 view 獨立編碼,encoder 與 decoder 在三階段訓練中皆 frozen。

**Key Formulas:**

$$
z = \mathcal{E}(x), \qquad \hat{x} = \mathcal{D}(\hat{z})
$$

**Implementation Details:**

論文指明繼承自 PixArt-Σ 的 VAE,並在 Evaluation 段提到「efficient VAE latent caching」作為推論加速策略。Latent channel 數 $c_z$ 與是否在多幀間 cache reference latent 的具體實作細節,the paper does not specify。

#### 5.3.2 Shared Patch Embedding 與 Spatial Concatenation

**Function:** 將三個 latent 流以同一組 patch embedding 權重投影為 token 序列,並沿 width 拼接為單一序列以便 joint self-attention。

**Input:**
- Name: $z_t$, $\hat{z}_\text{tgt}$, $z_\text{ref}$
- Shape: $[B, c_z, H/8, W/8]$ 三個
- Source: VAE encoder(對 $\hat{x}_\text{tgt}$ 與 $x_\text{ref}$); diffusion 前向過程(對 $z_t$)

**Output:**
- Name: token sequence
- Shape: $[B, 3 \cdot N_\text{patch}, d]$,其中 $N_\text{patch}=(H/8/p)\cdot(W/8/p)$
- Consumer: DiT block stack 第一層

**Processing:**

每個 latent 透過 **shared** patch embedding(patch size $p$,線性投影到 hidden dim $d$)分別 patchify,再加上 sinusoidal positional embedding。關鍵步驟是「沿 width 維度空間拼接」(Fig. 3, page 5),產生 $z_t \mathbin\Vert \hat{z}_\text{tgt} \mathbin\Vert z_\text{ref}$ 的長序列。論文(§2.4.1, page 5)強調此 spatial concat 的設計使三個 view 的 token 在 self-attention 中可以彼此檢索。

**Key Formulas:**

$$
\mathbf{T} = \mathrm{Concat}_\text{width}\left(\mathrm{PatchEmbed}(z_t),\ \mathrm{PatchEmbed}(\hat{z}_\text{tgt}),\ \mathrm{PatchEmbed}(z_\text{ref})\right) + \mathrm{PE}_\text{sin}
$$

**Implementation Details:**

Patch size $p$、hidden dimension $d$ 沿用 PixArt-Σ 但 the paper does not specify 確切數值。Sinusoidal positional embedding 為附加項而非 RoPE(後者在 attention 內部處理)。

#### 5.3.3 PRoPE-modulated Self-Attention DiT Block

**Function:** 以相機投影矩陣調變 query/key/value,使 attention 直接在跨視角幾何空間中進行 correspondence 計算,並完成 cross-view feature 融合。

**Input:**
- Name: token sequence $\mathbf{T}$,相機投影矩陣 $P_\text{ref}$, $P_\text{tgt}$
- Shape: $[B, 3 \cdot N_\text{patch}, d]$;$P_i \in \mathbb{R}^{4 \times 4}$
- Source: 上一層 DiT block 輸出(或 patch embedding); $\pi_\text{ref}, \pi_\text{tgt}$

**Output:**
- Name: refined token sequence
- Shape: $[B, 3 \cdot N_\text{patch}, d]$
- Consumer: 下一層 DiT block 或 width-wise split

**Processing:**

每個 DiT block 由 PRoPE-modulated self-attention 與 FFN 構成(Fig. 3 right panel)。對 view $i$ 的 token,先計算 $Q_i, K_i, V_i$,再以 $P_i^\top$ 對 $Q_i$、$P_i^{-1}$ 對 $K_i, V_i$ 線性變換,並在 view 內部疊加 2D RoPE。Self-attention 跨整個 $3 \cdot N_\text{patch}$ 序列進行,因此 target 的 query 可同時 attend 到 reference frame token(取得外觀)與 anchor token(取得幾何),實現 hybrid spatial memory。論文(§2.4.1, page 5–6)報告 PRoPE 相比 Plücker ray embedding 與 pure parametric injection,convergence 最快、相機控制最穩定。

**Key Formulas:**

$$
\tilde{Q}_i = P_i^\top Q_i, \qquad \tilde{K}_i = P_i^{-1} K_i, \qquad \tilde{V}_i = P_i^{-1} V_i
$$

$$
\mathrm{Attn}(\tilde{Q}, \tilde{K}, \tilde{V}) = \mathrm{softmax}\!\left(\frac{\tilde{Q}\tilde{K}^\top}{\sqrt{d_h}}\right) \tilde{V}
$$

**Implementation Details:**

DiT block 數 $L$、attention head 數、FFN expansion ratio、normalization 形式皆沿用 PixArt-Σ 但 the paper does not specify 確切數值。Stage II 訓練採 noise schedule biasing(增加 high-noise timestep 採樣機率以優先學幾何結構)、progressive condition injection(早期只給 reference,後期才加入 anchor)、random anchor masking(後期以一定機率遮蔽 anchor)三種策略。

#### 5.3.4 Width-wise Split 與 Unpatchify

**Function:** 從融合後的 token 序列中只保留 target view 的部分,還原為 latent feature map 並送入 VAE decoder。

**Input:**
- Name: refined token sequence
- Shape: $[B, 3 \cdot N_\text{patch}, d]$
- Source: 最後一層 DiT block

**Output:**
- Name: $\hat{z}_\text{tgt}^\text{pred}$
- Shape: $[B, c_z, H/8, W/8]$
- Consumer: VAE decoder

**Processing:**

論文(§2.4.1, page 5)明確指出「After passing through the full transformer, the output is split along the width dimension and only the target portion is retained as the final prediction」。即取序列前 $N_\text{patch}$ 個 token(對應 $z_t$ 區段),經 unpatchify(線性投影 + reshape)還原為 latent feature,作為 noise prediction $\epsilon_\theta$ 或 velocity prediction(取決於 diffusion 形式)。

**Key Formulas:**

$$
\mathcal{L} = \mathbb{E}_{z_\text{tgt}, \epsilon \sim \mathcal{N}(0,I), t}\left[\|\epsilon - \epsilon_\theta(z_t, t, C)\|^2\right]
$$

**Implementation Details:**

Unpatchify head 是否含 LayerNorm、輸出是預測 noise $\epsilon$ 還是 $v$-prediction,the paper does not specify。

#### 5.3.5 DMD Two-step Few-step Distillation

**Function:** 將 Stage II 多步 teacher 蒸餾為 2-step student generator,使單張 frame 能在消費級 GPU 上即時生成。

**Input:**
- Name: middle-trained multi-step model(teacher)、generator student
- Shape: 同 §5.3.3 token sequence,加 timestep $t \in \{T, t_\text{mid}\}$
- Source: Stage II checkpoint

**Output:**
- Name: $I_\text{tgt}$
- Shape: $[B, 3, H, W]$
- Consumer: 即時互動 viewer

**Processing:**

DMD(§2.5, page 7)同時維護 frozen base model(估計 real score)與 dynamically-updated fake model(估計 generator distribution score),以兩者 denoising 預測之差作為 generator 梯度,並佐以 base model deterministic sampler 產生的 noise–image pair 上的 regression loss 穩定訓練。InSpatio-WorldFM 採 2-step schedule:第一步從 $t=T$ 去噪到 $t_\text{mid}$,第二步從 $t_\text{mid}$ 去噪到 $0$。論文以系統性實驗找出 $t_\text{mid}=200$(於 1000-step schedule 上)為 coarse-to-fine 的最佳切點。

**Key Formulas:**

近似 KL gradient(VSD 形式):

$$
\nabla_\phi \mathcal{L}_\text{DMD}(\phi) \approx \mathbb{E}_{t, z_t}\left[w(t)\left(s_\text{fake}(z_t, t) - s_\text{real}(z_t, t)\right) \nabla_\phi G_\phi(\cdot)\right]
$$

加上 regression 穩定項:

$$
\mathcal{L}_\text{reg} = \mathbb{E}_{(\epsilon, x^\star)}\left[\|G_\phi(\epsilon) - x^\star\|^2\right]
$$

**Implementation Details:**

論文明確給出 $T=1000$、$t_\text{mid}=200$,並指出 1-step 在 high-noise 起點難以恢復細節、$t_\text{mid}$ 過大會讓第二步退化為 1-step。推論層級採 KV-cache 與 VAE latent caching 工程優化,512×512 解析度下單張 H 系列 GPU 約 25 FPS、RTX 4090 約 10 FPS。Generator 是否採 EMA、學習率、總訓練步數,the paper does not specify。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| DL3DV [22] | Real-world multi-view video for novel-view synthesis training | the paper does not specify | Train (Stage II middle-training) |
| RealEstate10K [51] | Real-world posed video clips for novel-view synthesis training | the paper does not specify | Train (Stage II middle-training) |
| Self-captured videos | In-house real-world video clips | the paper does not specify | Train (Stage II middle-training) |
| Unreal Engine synthetic data [12] | Synthetic trajectories with GT camera pose and depth | the paper does not specify | Train (Stage II finetuning with synthetic data) |

備註：每段 real video 隨機抽 16 frames，4 frames 作為 reference group 建構 global point cloud，其餘 12 frames 作為訓練 target；synthetic 資料採同樣的 4/12 split。論文未提供獨立的 validation/test split 或量化 benchmark dataset。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Qualitative multi-view consistency | 由 reference image + 10 個不同 camera viewpoint 的 rendered frames 視覺檢視幾何與外觀一致性（Fig. 4–8） | yes |
| FPS (frames per second) | 在 $512 \times 512$ 解析度下單卡的即時推論速度 | yes |
| GPU memory footprint | 是否能於 consumer-grade GPU 上運作（以 RTX 4090 可運行為指標） | partial |

論文未報告 PSNR、SSIM、LPIPS、FID/FVD 或任何量化的 view consistency 指標；所有「main claim」都僅以 qualitative figures 呈現。

### 6.3 Training and Inference Settings

- **Backbone**：PixArt-Σ [8]，一個 efficient Diffusion Transformer，作為 Stage I 的 image generation prior。
- **Camera pose encoding**：在三種策略（Plücker ray embedding、PRoPE、pure parametric injection）中採用 PRoPE [20]，因其收斂最快、camera control 最穩定。
- **Stage II training data 構成**：每個 real video clip 抽 16 frames，使用 MapAnything [17] 等 feedforward reconstruction model 估計 per-frame camera pose 與 depth；4 frames 為 reference group、12 frames 為 target；synthetic 資料來自 Unreal Engine 並採 stochastic motion sampling 或 pre-defined motion templates，並以 collision avoidance 強制 viewpoint validity。
- **Stage II training strategies**：(1) noise schedule biasing — 提高 high-noise timesteps 取樣機率；(2) progressive condition injection — 早期僅 inject reference frame（implicit memory），後期才逐步加入 explicit anchor；(3) random anchor masking — 後期以一定機率遮蔽 explicit anchor。
- **Stage III post-training**：採用 Distribution Matching Distillation (DMD) [42]，維持 frozen base model（real score）與 dynamically-updated fake score model，並輔以 pre-computed noise-image regression loss。
- **Few-step schedule**：採用 2-step denoising，且關鍵的 intermediate timestep 設為 $t_{mid} = 200$（基於 1000-step schedule），優於 1-step 與較大的 $t_{mid}$。
- **Inference resolution**：$512 \times 512$。
- **Inference hardware**：單張 H-series GPU 約 25 FPS；RTX 4090 可達 10 FPS，並結合 KV-cache management 與 efficient VAE latent caching 等 engineering optimizations。
- **未指明項目**：optimizer、learning rate schedule、batch size、training steps、warmup、Stage II 與 Stage III 的具體訓練輪數、teacher–student 之 step 數、資料量總規模 — the paper does not specify。論文亦未提供 appendix 描述這些設定。

### 6.4 Main Results

| Method | Multi-view consistency (qualitative) | FPS @ 512×512 | Notes |
|---|---|---|---|
| Teacher (Stage II fundamental frame model) | strong；跨 10-frame 視點維持幾何與外觀一致（Fig. 4） | the paper does not specify | Multi-step diffusion；未量化評估 |
| **InSpatio-WorldFM (distilled, Stage III, this paper)** | **與 teacher 接近，無明顯結構崩壞或 artifact（Fig. 5–8）** | **~25 FPS on H-series GPU；10 FPS on RTX 4090** | **2-step DMD distillation，$t_{mid}=200$** |
| RTFM [37] (World Labs) | 論文中作為 prior frame-based world model 動機性比較 | 未比較 | 未公開 source code，僅以 narrative 提及；本文未做 head-to-head |
| StarGen [45] | 以 warped features 提供 spatial conditioning | 未比較 | 僅在 hybrid spatial memory 段落作 design contrast，未量化比較 |

論文的 main claim「strong multi-view consistency + real-time on consumer-grade GPU」僅由 qualitative figures（Fig. 4–8）與 FPS 數字佐證；未提供任何與 video-based world model（如 Voyager、Gen3C、Matrix-Game、HunyuanWorld 等所引用的方法）之量化對比。

### 6.5 Ablation Studies

論文沒有正式的 ablation table；以下是文中以敘述形式呈現的 design comparisons，並評估它們是否屬於 diagnostic ablation：

- **Camera pose encoding：Plücker vs PRoPE vs pure parametric injection** — 結論為 PRoPE「fastest convergence and the most stable camera control」。屬合理的 design ablation，但**未提供量化曲線或數字**，難以驗證宣稱；偏向 narrative 而非 diagnostic。
- **Condition injection：self-attention vs cross-attention** — 文中聲稱「injecting condition information through self-attention yields higher generation quality」。**僅以 empirical 一句帶過，無任何指標**，屬於 sanity-style 描述而非診斷性實驗。
- **Hybrid spatial memory：explicit anchor + implicit memory vs single source** — 文中以 RTFM（純 posed frames）與 StarGen（warped features）作 design contrast，但**未在自家 pipeline 上做「移除 explicit anchor」或「移除 implicit memory」的 controlled ablation**。這是論文核心 claim，卻只有 motivational 描述，**該 ablation 缺失**是主要弱點。
- **Synthetic finetuning 量** — 聲稱「even a small amount of synthetic finetuning yields a significant improvement」。**未給出 step-vs-quality 曲線**，無法判斷「過量會破壞 natural appearance」這條 claim 的轉折點。
- **DMD step 數：1-step vs 2-step** — 結論為 2-step 較佳，但**僅有 qualitative claim**「sharper details」，無數字。屬合理 ablation 方向但執行不完整。
- **DMD intermediate timestep $t_{mid}$ 掃描** — 提到「systematic evaluation」找到 $t_{mid}=200$ 為最佳，但**未呈現 sweep 表或圖**；屬正確的 diagnostic 問題，但讀者無法檢視。

整體而言，所有 ablation 都以散文形式呈現、缺乏量化證據；camera encoding 與 DMD timestep 的問題設計合理但未充分執行，hybrid spatial memory 這個方法核心則**根本沒有 controlled ablation**，是最關鍵的缺口。

### 6.6 Phyra Experiment Assessment

- [missing] Has at least one strong baseline — 論文僅在敘述中提及 RTFM [37]、StarGen [45] 等 frame-based 先例，但**未做任何 head-to-head 量化比較**，也未對比 video-based world models（Voyager、Gen3C、Matrix-Game 等）。
- [missing] Has cross-task / cross-dataset evaluation — 評估僅限於自家 qualitative 範例（Fig. 4–8），**未在任何標準 benchmark（如 RealEstate10K test split、Tanks and Temples、ScanNet、DL3DV held-out）上回報數字**，亦無跨 task 評估。
- [partial] Has ablations that diagnose the new components — camera encoding、DMD step/$t_{mid}$ 屬 diagnostic 方向，但全為 narrative；hybrid spatial memory 此核心元件**沒有 leave-one-out controlled ablation**。
- [missing] Has a scaling study — 論文**未報告任何 model size、data scale 或 compute scaling 實驗**，僅 fix 在 PixArt-Σ 一個 backbone。
- [partial] Has an efficiency / wall-clock comparison — 提供自家在 H-series GPU（~25 FPS）與 RTX 4090（10 FPS）@ $512\times512$ 的數字，**但未與任何 video-based 或 frame-based baseline 在相同硬體下比較 FPS / latency**。
- [missing] Reports variance / standard deviation / multiple seeds — **完全未報告任何 variance、std 或多 seed 結果**；所有結論為 qualitative 單次觀察。
- [partial] Releases code / weights / data sufficient for reproducibility — 論文宣告 project website 與 GitHub 連結，並標榜為「open-source」；但**未在文中說明 release 範圍（weights / training code / data pipeline / synthetic UE assets）**，也未提供 license 或 commit reference，實際可重現性需驗證 repo 內容才能確認。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1:Frame-based 範式可消除 video model 的 window-level 延遲**。架構層面成立(self-attention only、單幀獨立生成),Fig. 3 與 page 12 提供的 25 FPS / 10 FPS 數字支持「絕對速度」可達 real-time;但「相對於 video-based 在同畫質下更快」這個更強的 claim 並未被實驗支持,因為沒有任何 video baseline 跑同一條軌跡的比較。**部分支持。**
- **Claim 2:Hybrid spatial memory(顯式 anchor + 隱式 reference)維持 multi-view consistency**。僅由 Fig. 4–8 的 qualitative frames 支持,沒有 cross-view PSNR、reprojection error 或長軌跡 consistency 指標。**過度宣稱(quality assertion 缺乏可驗證指標)。**
- **Claim 3:DMD 2-step distillation 在維持品質的同時實現 real-time**。Fig. 4(teacher)與 Fig. 5–8(student)是僅有的證據,作者文字稱「perceptual difference remains minimal」(page 12),但沒有 teacher–student 的數值差距、也沒有 user study。**部分支持(時間達標,品質保持為宣稱)。**
- **Claim 4:Progressive condition injection 防止模型過度依賴 explicit anchor**。Page 6–7 描述機制與動機合理,但沒有「joint vs progressive」的對照訓練曲線或結果圖。**僅以理論支持,實驗未支持。**
- **Claim 5:消費級 GPU 上可即時部署**。page 12 給出 RTX 4090 上 10 FPS 的明確數字,屬於可獨立驗證的工程結果。**支持。**
- **Claim 6:Open-source 釋出**。GitHub 連結存在(page 1);本論文未說明釋出範圍(weights / training code / data pipeline),需要實際檢查 repo 才能確認。**待 repo 驗證。**

### 7.2 Fundamental Limitations of the Method

**離線–線上耦合使「真正即時」只在預先計算的視野內成立**。系統的 multi-view consistent observations 與 global point cloud 必須由 offline stage 產生(Fig. 2),frame model 只是在這個預先計算的 3D 場景上做 novel view rendering。當使用者越過「motion boundary」(作者於 page 13 自述)時,系統必須觸發 offline stage 重建場景,這部分不是即時。換言之,frame-based 解決的是「同一個預先計算場景內」的 latency,而不是「任意自由探索」的 latency,這是當前 formulation 結構性的範圍限制。

**3D 一致性的責任被外包給 feedforward 3D foundation model**。Point cloud 由 MapAnything / VGGT / MoGe 等模型估出的 pose 與 depth 投影而成(page 6),frame model 只是在被注入的 anchor 上做生成。如果這些上游模型在 textureless、reflective、dynamic、長基線等情況下出錯,frame model 必須仰賴隱式記憶「修正」幾何;但作者沒有探討錯誤上限,也沒有量化「anchor 錯多少時模型仍可恢復」,這代表整個 pipeline 的幾何上限其實由外部模型決定,而非 frame model 本身。

**放棄時序建模是設計選擇而非可調旋鈕**。frame jitter 之所以存在(page 13),是因為 frame-based 架構本質上沒有 frame 之間的 conditional dependence;若加入時序平滑或 frame-to-frame attention,就會重新引入 window-level 計算,這正是這套方法刻意要避開的代價。也就是說,「低 latency」與「時序穩定」在當前 formulation 內是互斥的,不存在純算法層面的 free lunch。

**靜態場景假設深植於資料與架構**。訓練資料(DL3DV、RealEstate10K、UE 場景)幾乎全為靜態觀測,reference frame 與 point cloud 也只能描述靜態幾何;frame model 沒有任何持久動態狀態的表示。要支援動態內容(作者列為 future work),需要新的記憶機制(例如時間索引的動態 anchor),不是調參能解決的。

### 7.3 Citations Worth Tracking

- **DMD / Yin et al. [42]**:本論文的 Stage III 與「2-step + $t_{mid}=200$」等核心即時化主張全建在 DMD 上,理解原始 DMD 的 score-matching 架構與 KL 近似才能判斷此處的 2-step 改動是真貢獻或是 hyperparameter 工程。
- **PRoPE / Li et al. [20]**:整個相機條件注入機制直接套用 PRoPE,但本文沒有 ablation;讀原論文可瞭解 PRoPE 在 cross-view 任務上的原始定位以及其對 attention rank 的影響。
- **RTFM / WorldLabs [37]**:本論文反覆以 RTFM 作為對照(page 2、page 6),且在 hybrid memory 部分明確聲稱優於 RTFM 的「posed frames as primitive memory」,讀 RTFM blog 是判斷此 claim 的唯一參考。
- **StarGen / Zhai et al. [45]**:被列為另一條替代設計(warp posed-keyframe features),作者群與本論文有重疊,理解 StarGen 為何被本作者群放棄轉向 anchor 設計,有助於辨認真正的設計動機。
- **MapAnything / Keetha et al. [17]**:整個 offline 階段的 pose / depth / point cloud 由 MapAnything 提供,實際上決定 InSpatio-WorldFM 的幾何上限,讀此論文可釐清誤差特性與適用域。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在固定軌跡與 reference image 下,InSpatio-WorldFM 與 video-based world model(例如 Voyager、Gen3C、Matrix-game)在 PSNR / LPIPS / FVD 上的實際差距是多少?
- [ ] 當系統觸發 offline stage 更新 global scene 時,跨 keyframe 邊界是否出現可見的 seam 或外觀漂移,且更新過程的延遲是多少 ms?
- [ ] 25 FPS 中 point cloud rendering、VAE encode/decode、DiT forward、2-step denoising 各自占多少 ms,瓶頸是 attention 還是 VAE?
- [ ] 把 PRoPE 換回 Plücker 或 pure parametric,在同樣訓練步數與資料下,multi-view consistency 與相機控制誤差的差距具體有多大?
- [ ] 當 MapAnything 的 pose/depth 估計誤差超過某個閾值(例如平移誤差 > 5%、depth RMSE > 10%)時,frame model 會優雅退化還是產生「自信但錯誤」的幾何?
- [ ] 「H-series GPU」實際是 H100 / H800 / H200 哪一張,並且在無 KV-cache 與無 VAE latent caching 的純前向下,FPS 是多少?
- [ ] 在使用者離開 offline 預先計算的 3D 範圍時,單次線上「擴展」的最壞延遲是多少,是否可被使用者察覺為卡頓?

### 8.2 Improvement Directions

1. **補上量化評估表**(可行性最高):在現有 checkpoint 上計算 cross-view PSNR / LPIPS、長軌跡 reprojection error、以及對 video baseline 的 FVD,即可把 §3 的所有 qualitative 主張轉為可驗證結果。理由是模型已存在、軌跡已產生,缺的只是評估腳本,屬於零訓練成本。
2. **公開四項核心 ablation**(可行性高):PRoPE vs Plücker vs parametric、hybrid vs anchor-only vs ref-only、progressive vs joint condition injection、2-step DMD 的 $t_{mid}$ 掃描。作者文字描述本身就暗示這些對照已跑過,只需要把表整理出來。
3. **以軌跡預測驅動的非同步 offline 擴展**(中可行性):根據使用者過去 N 幀的相機運動預測未來軌跡,在背景觸發 offline stage 預先擴張 global scene,把 motion boundary 推到實際視野之外。理由是 motion boundary 是當前互動性的最大破口,而 GPU 在 2-step DMD 下其實有空閒可被 offline 工作占用。
4. **在推論端加入輕量時序正則**(中可行性):部署一個 frame-to-frame 後處理模組(例如基於上一幀 latent 的 EMA 或 learned 1-step refine),只看相鄰兩幀,不引入 window-level 訓練依賴,以降低 frame jitter。理由是 jitter 的根因是 inference-time 隨機性,不一定要從訓練端解。
5. **以 Gaussian Splatting 作為新的顯式 anchor**(較低可行性,作者亦列為 future work):GS 可表達 view-dependent specular 與反射,而 point cloud 不行;由於 anchor 通道在架構上是獨立 condition,替換 anchor 表示對 DiT 主幹影響小,主要工作集中在 offline 重建。理由是當前 anchor 是視覺保真上限的關鍵瓶頸,且 GS 已有成熟 feedforward 方法可餵入此 pipeline。
