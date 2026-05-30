<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# SpMem — Video World Models with Long-term Spatial Memory

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | SpMem |
| Paper full title | Video World Models with Long-term Spatial Memory |
| arXiv ID | 2506.05284 |
| Release date | 2025-06-05 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2506.05284 |
| PDF link | https://arxiv.org/pdf/2506.05284v1 |
| Code link | — |
| Project page | https://spmem.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Tong Wu | Stanford University | https://wutong16.github.io/ | co-first author |
| Shuai Yang | Shanghai Jiao Tong University; Shanghai Artificial Intelligence Laboratory | https://ys-imtech.github.io/ | co-first author |
| Ryan Po | Stanford University | — | co-author |
| Yinghao Xu | Stanford University | — | co-author |
| Ziwei Liu | S-Lab, Nanyang Technological University | — | co-author |
| Dahua Lin | The Chinese University of Hong Kong; Shanghai Artificial Intelligence Laboratory | — | co-author |
| Gordon Wetzstein | Stanford University | — | senior author / PI |

### 1.2 Keywords

video world models, long-term spatial memory, episodic memory, video diffusion transformer, autoregressive video generation, point cloud conditioning, TSDF fusion, long-horizon scene consistency

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| CogVideoX [79] | base model | 提供 latent video DiT 與 3D-VAE,本作以 CogVideoX-5B-I2V 為原型實作條件式擴散世界模型。 |
| DaS / DiffusionAsShader [25] | predecessor | 本作從 DaS 預訓練權重出發,並把它作為 point-map 條件式視訊生成的主要比較基準之一。 |
| TrajectoryCrafter [82] | baseline | 另一條 point-cloud 條件相機軌跡控制路線的代表方法,在 view recall 與用戶研究上對比。 |
| Wan2.1 (Inpainting) [66] | baseline | 目前最先進的開源視訊生成模型,作為 SOTA 對照組進行 inpainting 比較。 |
| CUT3R [69] | influence | 提供線上遞迴式靜態點圖重建,用於在自迴歸生成過程中持續更新 spatial memory。 |
| Mega-SaM [44] | influence | 用於資料集建構時的 4D 重建,擷取相機內外參與逐幀深度,以建立帶幾何標註的訓練資料。 |
| ControlNet [88] | influence | 本作的 condition DiT 採取類似 ControlNet 的零初始化 linear 旁路注入靜態點雲渲染條件。 |

## 2. Research Overview

### 2.1 Research Topic

本研究探討如何讓自迴歸式 video world model 在長時間、長距離鏡頭運動下仍能維持場景一致性。作者觀察到現有 video diffusion 世界模型受限於 attention 的二次方複雜度,只能保留少量近期 context frame 作為短期記憶,當鏡頭重新回到曾經造訪過的區域時,常出現嚴重遺忘與漂移。受人類記憶機制啟發,作者主張除了既有的 short-term working memory,還必須引入兩種長期記憶:以幾何為基礎、明確儲存世界靜態結構的 long-term spatial memory(以 TSDF-fusion 過濾動態元素後形成的全域點雲表示),以及由稀疏代表性歷史影格組成的 episodic memory,用以保留視覺細節與身分。整體研究主題橫跨 video diffusion、autoregressive 長視訊生成、3D 場景表示、相機可控生成與互動式世界模擬器,並透過自建配對資料集驗證該記憶框架對長期一致性的提升。

### 2.2 Domain Tags

- computer vision
- generative video models
- world models
- 3D scene representation

### 2.3 Core Architectures Used

- **CogVideoX-5B-I2V (latent video DiT + 3D-VAE)**:作為主幹的 latent video diffusion transformer,負責在 latent 空間建模影片分佈,本作以其 3D-VAE 編碼器/解碼器與 DiT block 為基底,並從 DaS 預訓練權重起步繼續訓練條件式世界模型。
- **Condition DiT(ControlNet 風格旁路)**:複製 CogVideoX 前 18 個 DiT block 形成獨立分支,專門編碼靜態點雲渲染條件,並透過 zero-initialized linear layer 將特徵加回主幹 DiT,實作對相機軌跡與靜態場景的硬性幾何引導。
- **Historical Cross-Attention 模組**:新增於若干 DiT block 之間,以當前生成的 video tokens 作為 query、以 episodic memory 中代表性歷史影格經 3D-VAE patchify 後的 reference tokens 作為 key/value,將遠距離歷史視覺細節注入當前生成。
- **Working Memory 拼接機制**:沿 frame 維度將 source video 最後五個 frame 的 tokens 與 target tokens 串接,提供 short-term 動態運動連續性。
- **TSDF-Fusion 體素表示 + CUT3R 線上點圖重建**:作為 long-term spatial memory 的儲存介面,CUT3R 在推論時以遞迴方式持續預測 metric-scale pointmaps 與相機參數,TSDF-Fusion 則透過加權平均自動壓低跨幀不一致(動態)體素的信心,維持以靜態幾何為主的全域點雲。
- **Mega-SaM 4D 重建管線**:僅用於資料集建構階段,以較精確但較重的 4D 重建擷取相機內外參與逐幀深度,產生配對訓練資料。
- **T5 文字編碼器與 Qwen 動作標註**:T5 將 action/text prompt 注入 DiT 進行語意條件化;Qwen 則於資料集建構時為 target frame 自動產生動作描述標註。

### 2.4 Core Argument

作者鎖定的根本問題是:現有 video world model 的「記憶」純粹由近期 RGB context frame 構成,屬於影像層級的短期記憶,缺乏對世界靜態幾何的持久 3D 表徵,因此一旦超出 sliding window,模型就只能依賴生成端的隱式記憶,於是出現重訪場景失憶與外觀漂移。其推論邏輯是:既然問題出在「記憶表徵的型態錯誤」,單純加長 context 或對遠處 frame 做下採樣只是緩解計算成本,本質上仍是有損的影像記憶,並未解決 3D 一致性。因此真正必要的修補是改變記憶的表徵介面 —— 把世界拆成靜態與動態:靜態部分以 TSDF-fusion + CUT3R 線上更新的全域點雲儲存,因為 TSDF 的加權平均會自動壓低跨幀不一致(也就是動態物體)的體素信心,天然完成動靜分離;動態部分仍交由 working memory 的近期影格驅動運動連續性;為彌補點雲過於稀疏無法保存外觀細節,再加入 episodic memory 作為稀疏歷史關鍵影格,在可見性掩膜偵測到大面積新區域時觸發加入,並透過 historical cross-attention 與當前生成 token 交換資訊。三者各司其職、由幾何骨架做硬約束、由像素 token 補回紋理身分,在邏輯上恰好對應到模型「該記得什麼」「該重新生成什麼」的決策邊界,因此作者宣稱這套幾何接地的長期記憶設計是維持長期一致世界生成的必要條件,而非僅是其中一種選擇。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「Video World Models with Long-term Spatial Memory」直接點出論文要解決的問題場域：video world models 的長期一致性，並指明補強的方向是「long-term spatial memory」。Abstract 先建立背景：emerging world models 以 autoregressive 方式逐幀生成 video，並由 actions（如 camera movements、text prompts）所驅動，這種範式天生需要 temporal context window，而 window 大小受限會在「revisit 先前已生成場景」時造成嚴重的 forgetting。這一鋪陳定義了論文的目標問題不是 single-shot generation 的品質，而是 long-horizon 下的 scene consistency。

接著 abstract 點出本文的核心 framing：以 human memory 機制為靈感，提出一個 geometry-grounded 的 long-term spatial memory 框架；這同時暗示了後續會出現 spatial、working、episodic 三種記憶的分工。作者並承諾兩件 deliverable：(i) 儲存與檢索 long-term spatial memory 的機制；(ii) 為訓練與評估 explicit 3D memory 而 curate 的客製化資料集。最後給出 evaluation 結論的方向：在 quality、consistency、context length 三個面向都優於相關 baselines。

對讀者而言，這一節已建立「為什麼純 frame-based context window 不夠」的痛點與「以 3D 幾何為錨」的解法主軸，為 §3.2 鋪平動機，也預告 §3.4 會出現三類記憶的具體實作。

### 3.2 Introduction

(560 words)

Introduction 從 world models 的定義切入：學習在 actions 條件下預測環境的 generative system，與 interactive simulation 場景天然契合。作者把 video diffusion 視為當前 world model 的主流架構，並特別點出 autoregressive next-frame prediction 是支撐互動式生成的關鍵範式，列了大量近期工作以建立讀者的領域地圖。隨後作者鎖定核心痛點：long-horizon consistency 不足，模型在「revisit 先前生成過的場景」時會出現嚴重 forgetting；其根因被明確歸因於 diffusion transformer 中 attention 的 quadratic complexity，迫使 context window 不能太大。

接著作者批判現有對策。第一類做法是直接把 context frames 數量壓低以保住可行性；第二類是近期出現的 progressive temporal downsampling，把較遠的 frames 壓縮以拉長 window。作者點出兩者的共同侷限：仍只是 image-based representation，沒有 persistent 3D understanding，因此只能勉強撐住外觀層面的時序一致，難以保證空間一致。這一段把問題從「context 不夠長」升級為「representation 不對」，為論文的 3D-grounded 主張做出 framing。

接著導入認知科學的隱喻：受 human memory（Baddeley）啟發，論文主張同時建模三種 memory：spatial、working、episodic，每一種都用一個專屬的表示。Working memory 對應現有方法慣用的 recent context frames，仍以像素資料記住 dynamic 與 static 的近期過去；spatial memory 是新引入的長期記憶，採 explicit 3D representation（point cloud）；episodic memory 則以稀疏 keyframes 形式補充少量重要視覺事件。這個三元劃分是貫穿全文的 mental model。

論文進一步交代一個關鍵的 design choice：在把新生成的內容寫入 spatial memory 之前，會先 filter 掉 dynamic parts，確保 spatial memory 只保留 static scene。這既呼應了人類 spatial memory 的功能定位，也回應了 §3.3 將提到的 dynamic-static 解耦。這一段是作者試圖回答「point cloud 為何能當 long-term memory」的核心論證。

最後作者宣示貢獻：(i) 結合 short-term working、long-term spatial、sparse episodic 的 memory 機制設計；(ii) 配套的 store 與 retrieve 機制以條件化新 frame 的生成；(iii) curate 出客製化資料集以訓練與驗證；(iv) 評估展示 quality 與 3D consistency 都優於 baselines。Introduction 也表態本工作的長遠願景是 infinite-length、consistent world generation，並串到 graphics、robotics 等下游應用。整體架構為 §3.3（領域定位）、§3.4（方法）、§3.5（實驗）建立了清晰的承接：問題已被定義為 representation 層面的 3D 缺失，下一步自然是介紹既有 long-context 與 controlled generation 文獻如何（不）解決它。

### 3.3 Related Work / Preliminaries

(680 words)

這一節同時對應論文的 §2 Related Work 與 §3.1 Preliminaries，整合處理是因為 §3.1 篇幅短，且功能上等同於 method 之前的背景鋪陳。Related Work 拆成四個 sub-thread：(i) image and video generation、(ii) autoregressive video generation、(iii) controlled video generation、(iv) long-context video generation；Preliminaries 則交代 diffusion model 的最低限度數學語言。

第一個 sub-thread 把 diffusion 定位為 image generation 的 SOTA，並交代它如何被擴展到 temporal 維度以支撐 video generation。作者列出 tokenization 改良、flow-matching objective 等正交方向，藉此告訴讀者本工作不是從 diffusion 的 base recipe 重新發明，而是站在這些既有 video diffusion backbone 之上。

第二個 sub-thread 處理 autoregressive video generation。作者區分兩種典型做法：以 spatio-temporal tokens 模仿 LLM-style next-token prediction，或者以條件 diffusion 模型在 clean previous frames 上續寫 future frames；另有一支以 per-frame 獨立 noise level 的 diffusion forcing 路線。作者刻意指出這些方法雖能藉 sliding window 達到 infinite-length 推論，但都受 limited memory 與 drift 困擾，這正是 §3.4 要 attack 的點。

第三個 sub-thread 是 controlled generation。作者把控制信號分成三類：camera control、structural conditioning（point clouds、tracking、3D-aware priors）、action 或 scene-level conditioning。作者特別點出當 camera trajectory 與 dynamic content 解耦時的限制，以及 point-cloud-grounded 方法雖能精準控制相機卻難以處理複雜 dynamic motion。這個批評為本論文的 dynamic-static decoupling design 預留了動機空間。

第四個 sub-thread 是 long-context video generation，也是與本文最直接競爭的子題。作者列出三條既有路線：(a) 訓練更長 context 的 attention，計算昂貴；(b) state-space 或 linear attention 等 efficient architecture，品質較弱；(c) 壓縮 prior frames 以降低 context length，但會損失資訊；(d) 把舊 frames grounding 到 3D representation（point cloud）後依未來 camera pose query。作者承認 (d) 與本文最近，但批評它無法處理 dynamic scenes。這個 framing 把本文定位為「(d) 的後繼者，但會處理 dynamic」。

該節結尾以一段 transition 把四條 thread 收束成本文路徑：採用 conventional concatenation 的 recent context frames 當 working memory，逐步預測並 filter 出新 frames 的 static point map 以更新 global spatial memory，並再加上稀疏 historical reference frames 為 episodic memory。這同時把 §3.2 Introduction 提出的三類 memory 與 §3.3 的文獻地圖鏈結起來。

最後 Preliminaries 段以最低成本交代 video diffusion 的數學語言：forward process $x_t = \alpha_t x_0 + \sigma_t \epsilon$、denoising loss $L(\theta) = \mathbb{E}_{t,x_0,\epsilon} \|\epsilon_\theta(x_t,t) - \epsilon\|_2^2$，並說明 video diffusion 通常採 latent 空間兩階段流程：先以 3D VAE encode video，再在 latent 上訓練 diffusion。作者揭露 prototype 是基於 CogVideoX，採 3D attention 的 diffusion transformer。這段背景的目的是讓 §3.4 可以直接以 ControlNet-style condition、condition latents 等術語切入，而不需要再展開 diffusion 細節。

### 3.4 Method (overview narrative)

(420 words)

Method 章節的開場將整套 framework 重新框定為兩件事的設計：「儲存新觀察進記憶」與「從記憶檢索資訊以條件化生成」。作者強調這個 design 同時受人類 spatial、working、episodic 三類記憶啟發，並把該章拆成 (i) 三類 memory 的構造與維護（§3.2 of paper）、(ii) 如何作為 conditional signal 注入 video diffusion 模型（§3.3）、(iii) 配套資料集 curation（§3.4）三條主線。讀者會在這節先建立 high-level mental model，細節留待 §5 的 method deep-dive 處理。

Spatial memory 的敘事核心是「以 explicit 3D 表示記住 static scene」。作者選 TSDF fusion 作為 storage primitive，因為它的 weighted averaging 規則本質上就是一個動靜態 filter：dynamic 物體在不同 frame 觀察的 depth 不一致，TSDF voxel 累積出低 confidence 與 noisy 值，自然被抑制。這與 §3.3 中對 point-cloud-grounded 方法「不擅長 dynamic」的批評形成回應：本文不是讓 point cloud 處理 dynamic，而是把 dynamic 排除出 spatial memory，讓 dynamic 由其他路徑承擔。

Working memory 對應 recent context frames，提供短期 motion 連續性。作者採 simple AR strategy：以最近 $k+1$ 個 latent frames 作條件，逐步生成後續 $N-k$ frames，迭代展開即可開放式延伸。這部分的論述刻意保持輕量，因為 working memory 並非本文的 novelty，而是要保住基準 baseline 的能力。

Episodic memory 補上 spatial memory 的不足：fused static point cloud 雖能保住幾何骨架，卻太稀疏，無法保留視覺細節（例如人物外觀、紋理）。作者透過 mask-based visibility check 監測新揭露區域大小，當超過閾值就把該 frame 加入 historical slots。這是把 episodic memory 觸發條件 grounding 在 spatial memory 的「未知區域」上的設計，與 spatial memory 形成耦合而非平行。

在 memory-guided generation 段落，作者交代三種 memory 如何注入 diffusion model：static point cloud 渲染後以 ControlNet-style 的 condition DiT（複製 CogVideoX 前 18 個 DiT blocks，零初始化 linear 加回主 DiT）注入；recent context frames 沿 frame 維度 concat 到 target tokens；historical reference frames 經 3D VAE 編碼，透過新增的 historical cross-attention 與 video tokens 互動（video tokens 為 query，reference tokens 為 key/value）。這三條注入路徑各自對應一類 memory，並導向 §3.5 將驗證的三大主張：camera 控制力、static 一致性、dynamic 可信度。Dataset creation 段預告 §3.5 中所有實驗將仰賴一個 90K-clip、配對 3D spatial memory 的客製化資料。

### 3.5 Experiments (overview narrative)

(380 words)

Experiments 的敘事邏輯是「先建立評測場景，再用四套互補的證據逐一打 baseline」。Implementation details 確立了實驗的 base：以 CogVideoX-5B-I2V 為 backbone（從 DaS 預訓練起），video 長度 49、解析度 480×720，6,000 iterations，learning rate $2 \times 10^{-5}$，mini-batch 8，八張 NVIDIA-A100。Inference 採最近 5 frames 為 working memory，每次 AR 迭代會 predict、align、fuse 新 frames 的 point map 進 global point cloud，並依目標 camera trajectory 渲染 condition video。這些細節讓後續 baselines（TrajectoryCrafter、DaS、Wan2.1-Inpainting）的比較落在同一個 backbone 與 trajectory 條件下。

Metrics 與 baseline 的選擇緊扣 §3.4 的三大主張：作者特意挑 point-map-conditioned 方法為 baselines，因為這代表現有 long-context 路線中最強的 3D-aware 競品。Evaluation 沿兩條軸：(i) view recall consistency 用 PSNR/SSIM/LPIPS 比較反向 camera trajectory 下重訪同一 pose 的 paired frames，這直接測試 spatial memory 的 forgetting；(ii) general video quality 採 VBench 六項指標 plus user study。reversed-trajectory protocol 是這節的關鍵 design：它讓「revisit 一致性」可以被 reconstruction metric 量化，而非只能靠主觀評分。

Quantitative 結果（Table 1, Table 2）建立第一條證據：view recall 上大幅領先，VBench 多項指標也勝出；作者誠實指出 Wan2.1 在 imaging quality 與 background consistency 略勝，但歸因於它常產生較 static 的場景，藉此把 trade-off 攤開。Qualitative（Figure 4）建立第二條證據：用 significant camera motion、view recall pair、action prompt 三種 challenge 視覺化展示 baselines 的 failure mode（遺忘、變形、角色消失）。User study 建立第三條證據：邀請 20 位有 video/3D/4D 經驗的受試者，依 ControlNet 的 AHR 對 14 個 use cases 在 camera accuracy、static consistency、dynamic plausibility 三軸排序，本文皆領先。

Ablation 是第四條也是最重要的證據：移除 episodic memory、移除 working memory、full model 的三組對照（Table 3、Figure 5）顯示三類 memory 各自為 motion smoothness、static consistency、subject identity 做出明確貢獻，且 full model 在所有 VBench 維度都最佳。這節為 §3.6 的結論收束鋪陳：每一類 memory 都有實證上的必要性，整體 framework 的 design choice 是 justified 的。

### 3.6 Conclusion / Limitations / Future Work

(280 words)

Discussion 章把本文的 takeaway 收斂為一句：受人類記憶啟發、以 geometry 為基底的 long-term spatial memory，能在 quality、spatial consistency、context length 三軸上同時改善 video world models。這個收束並非泛泛之論，而是對應 §3.5 的三條證據（quantitative、qualitative、user study）。Conclusion 段並把 video world models 的價值定位拉回到 §3.2 預告的下游應用：content creation、agent/robot 的 training data 來源，呼應 introduction 的長期願景。

Limitations 段誠實列出三個失敗模式。第一，TSDF-Fusion 並非完美：當 camera pose 與先前觀察差異過大，fused volume 會引入 artifacts（Figure 6 用 Spiderman 在摩天樓間擺盪的極端 trajectory 為例，4D reconstruction 失敗導致 spatial memory 變得極度稀疏，連帶讓 camera 控制與一致性都崩壞）。第二，本文 memory 機制聚焦 spatial consistency，而與之互補的 frame packing 方向 [87] 主要解 character consistency；作者明確邀請 future work 結合兩者以同時解兩類一致性。第三，本文只 attack「forgetting」這一個失敗軸，沒有處理另一個經典問題：drift（誤差累積導致 image quality 隨時間退化）。這三點 limitation 都是針對 §3.4 的 design assumption 設限：TSDF 的 dynamic-static filter 在極端 camera motion 失效；point cloud + episodic slots 的記憶設計仍偏向場景幾何，對人物身分支援有限；AR 推論對 error accumulation 沒有額外校正機制。

Societal Impacts 段警示 video generation 可被改作 DeepFake 的風險，作者明確反對誤導性使用。Acknowledgment 提及 Google 與 Stanford Graduate Fellowship 的支持。整體而言，§3.6 的功能是把 §3.4–§3.5 證實過的 design contribution 與其邊界並列，讓後續工作可以精確接力：要嘛延伸 spatial memory 對極端 trajectory 的 robustness、要嘛把 character consistency 與 drift 補進這個 memory 框架。

## 4. Critical Profile

### 4.1 Highlights

- 將人類記憶理論直接映射到 video world model,提出 working / spatial / episodic 三類記憶並各自配置專屬表徵,是論文最具辨識度的概念框架(Sec 1, Fig 1)。
- 以 TSDF-fusion 加權平均自然壓低跨幀不一致 voxel 的設計,讓動靜分離成為融合過程的副產品,不需額外動態 mask 監督(Sec 3.2, Eq 2)。
- View Recall PSNR 達 $19.10$,大幅領先第二名 DaS 的 $12.01$;SSIM $0.6471$ vs $0.4512$;LPIPS $0.3069$ vs $0.5874$(Table 1)。
- 使用者研究在 Cam-Acc / Stat-Cons / Dyn-Plaus 三個面向 AHR 分別為 $3.626 / 3.385 / 3.401$,於四方法中皆位居首位(Table 1 right)。
- VBench 六項中四項最佳,尤以 Temporal Flickering($0.7580$)與 Subject Consistency($0.9359$)拉開差距(Table 2)。
- Episodic memory 採可見性 mask 觸發式關鍵影格收集,當新揭露區域超過閾值才入記憶集,屬於資料驅動的稀疏選取策略(Sec 3.2)。
- 條件注入採 ControlNet 風格:複製 CogVideoX 前 18 個 DiT block 作 condition DiT,再以 zero-initialized linear 加回主幹,訓練穩定且可保留 base model 能力(Sec 3.3)。
- 自建 90K paired 資料集,每筆樣本同時帶有 source/target 視訊、相機內外參、靜態點雲與 Qwen 標註的 action 文字,提供少見的 4D-grounded 訓練監督(Sec 3.4, Fig 3)。
- Ablation 顯示 working、episodic、spatial 三種記憶移除任一項皆會在 VBench 全面下降,full model 各項皆為最高,提供模組級必要性證據(Table 3, Fig 5)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 當連續相機之間距離過大或角度變化過急(如 Spider-Man 在大樓間擺盪),Mega-SaM 4D 重建會失敗,TSDF-Fusion 進一步把應屬靜態的點濾掉,造成 spatial memory 過度稀疏與相機控制失準(Sec 5, Fig 6)。
- 即便是本方法的 PSNR 也遠未達理想,作者明言「remembering each and every visual detail of a complex scene is a very challenging task」(Sec 4.1)。
- 本方法主要解 spatial consistency,而 character / identity 層面的長期一致性仍需與 frame packing 類方法 [87] 結合,作者明示為 future work(Sec 5)。
- Drift(誤差累積導致畫質退化)並未在本作中處理(Sec 5)。
- 影片生成模型潛在被改作 DeepFake 的社會風險被列入 Societal Impacts,但僅以反對立場表述,並無技術性緩解(Sec 5)。

#### 4.2.2 Phyra-inferred

- View Recall 評估採「同一段相機軌跡反向再走一次」的 paired-frame 比對,而 spatial memory 正是由前段生成的 frame 累積而來,因此這個指標衡量的是「在自己留下的點雲指引下能否重現自己」,不是真正的跨段記憶測試;baseline 因為沒有等價條件而結構性吃虧。
- 比較對象只挑了 point-map / inpainting 路線(TrajectoryCrafter, DaS, Wan2.1-Inpainting),完全沒有與作者自己 Related Work 中提到的 frame-packing 路線 [87] 與 long-context AR [24] 比;這兩條才是「擴大時間記憶」的直接對手,缺席使「3D memory 比影像記憶更有效」的核心主張無法被檢驗。
- 訓練資料是被 Mega-SaM 能成功重建的子集,意味著 Fig 6 失敗的這類軌跡在訓練分佈中本來就被剔除;500 段 MiraData 測試集源自同一資料源,評測本身對「困難軌跡」 under-represent。
- TSDF 的「自動動靜分離」依賴多視角不一致;對一台停在路邊但即將駛離的汽車、長時間靜止的人物、緩慢平移的招牌等慢動態,在 49 frame source 視窗內幾何觀測會相對一致,因而會被當作 static 烘進記憶且永不被更新。
- 整體訓練只跑 $6{,}000$ iterations 且自 DaS 預訓權重 fine-tune,ablation 並未拆分「DaS-style point map 條件」「historical cross-attention」與「spatial memory 累積」三者各自的貢獻,因此 Table 1 中對 DaS 的大幅領先究竟有多少來自 spatial memory 本身、有多少來自額外微調與 historical attention,仍不明朗。
- 訓練端用 Mega-SaM、推論端改用 CUT3R,兩者點雲品質與座標系處理不同;附錄 B 僅以一句「difference does not lead to a significant performance gap」帶過,沒有量化 ablation,推論期 CUT3R 的 drift 對長序列效能的衝擊被刻意低調處理。
- 使用者研究是 20 名「至少一年 video/3D/4D 生成經驗」的受試者對 14 案例做 1–4 排名,既無 inter-rater agreement(如 Kendall's W)也無對排名打結處理的說明,且受試者具備領域偏好,AHR 訊號偏弱。

### 4.3 Phyra's Judgment (summary)

真正新的一塊是把「世界靜態結構」拉出影像層,改以 TSDF-fused 全域點雲作為持久記憶介面,並在 cognitive memory taxonomy 下把 working / episodic / spatial 三類分別配置具體載體,這個架構性主張清楚且可被驗證。其餘多屬工程組合:ControlNet 式 zero-linear 注入、historical cross-attention、自建 paired dataset 都是現成元件的搭配。最關鍵未解的是,當動態物體運動緩慢、相機軌跡崎嶇、或生成長度遠超訓練視窗時,TSDF 的單調累積特性與 Mega-SaM 偏向易重建場景的資料分佈,會讓「3D memory 是長期一致世界生成的必要條件」這個論斷的適用邊界變得很窄。

## 5. Methodology Deep Dive

### 5.1 Method Overview

整體 pipeline 可拆為「資料準備 → 條件式 video DiT 訓練 → 自迴歸推論時的記憶讀寫」三個層次。基底模型沿用 CogVideoX-5B-I2V (從 DaS [25] 預訓練權重出發),為一 latent video diffusion transformer:輸入 video 先經 3D-VAE 壓縮成 latent,DiT 以 3D attention 在 spatio-temporal token 上去噪,輸出再經 VAE decoder 還原為 RGB。本作不改動 backbone 的去噪目標,而是在 condition 端疊加三條互補的記憶通道:short-term working memory、long-term spatial memory、episodic memory,並透過 ControlNet 風格的 zero-initialised linear 旁路與 historical cross-attention 注入主 DiT。

訓練資料以 MiraData 為來源,將每段影片切為 97 frames 的 clip,前 49 frames 作 source、後 48 frames 作 target、共享一張 transition frame。對每段 clip 用 Mega-SaM [44] 做 4D 重建,擷取 camera intrinsics/extrinsics 與 per-frame depth;以 source 段做 TSDF-Fusion 得到清乾淨的靜態體素場,再沿 target trajectory 用 point-based rendering 投影出 visibility mask 與 static-region rendering。target 段保留 RGB 全幀作為含動態元素的監督訊號。最終得到約 90K 組 paired sample,每組同時帶有 `(source video, static point cloud rendering on target trajectory, target RGB, action text)`。

推論階段採 sliding-window 自迴歸:每步以最近 $k+1$ latent frames 作 working memory、用 CUT3R [69] 對新生成 frames 做線上 point map 預測並對齊到全域座標系,再以 TSDF-Fusion 過濾動態雜訊後合併進 long-term spatial memory。當 visibility mask 偵測到目前視角揭露大面積未知區域時,將該 frame 加入 episodic memory keyframe set。生成下一步時,把 spatial memory 沿目標軌跡渲染成 condition video、透過 condition DiT 注入主 DiT,episodic frames 則經 3DVAE/patchify 後與當前 latent 在 historical cross-attention 中交換資訊。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Inputs (per autoregressive step)
  ├─ Recent context frames (working memory)         RGB        : [B, k+1, 3, H, W]   (k=5 at inference)
  ├─ Static point cloud rendering on target traj.   RGB        : [B, F, 3, H, W]     (F=49, H=480, W=720)
  ├─ Historical reference frames (episodic memory)  RGB        : [B, M, 3, H, W]     (M = #keyframes, ?)
  ├─ Action text prompt                             tokens     : [B, L_text]
  └─ Camera trajectory (intrinsics + extrinsics)    pose       : [B, F, 3, 4] + K

(1) Static point cloud render → VAE Enc. → Patchify
    [B, F, 3, 480, 720]
        └→ VAE Enc.        : [B, C_z, F', H', W']     (C_z=16, F'=⌈F/4⌉, H'=60, W'=90; CogVideoX 3D-VAE)
            └→ Patchify    : [B, N_cond, d]           (N_cond = F' · H'/p · W'/p, d = DiT hidden, ?)

(2) Recent context + zero-padding → VAE Enc. → Patchify
    [B, k+1, 3, 480, 720]  (zero-padded along time to F frames)
        └→ VAE Enc.        : [B, C_z, F', H', W']
            └→ Patchify    : [B, N_ctx, d]            (N_ctx aligned to target tokens for frame-level corresp.)

(3) Noise latent for target video
    z_t                    : [B, C_z, F', H', W']     → patchify : [B, N_tgt, d]

(4) Historical reference frames → VAE Enc. → Patchify (episodic tokens)
    [B, M, 3, 480, 720]
        └→ VAE Enc.        : [B, C_z, M', H', W']     (M' = ⌈M/4⌉)
            └→ Patchify    : [B, N_ref, d]            (keys/values for cross-attn)

(5) Action text → T5 encoder
    [B, L_text]            → T5 : [B, L_text, d_t]    → linear : [B, L_text, d]

────────────────────────────────────────────────────────────────────────────────
Condition DiT  (18 blocks copied from CogVideoX, processes condition latents)
    in : [B, N_cond, d]
    per block i ∈ {1..18}:
        h_cond_i ∈ [B, N_cond, d]
        └─ Zero-Linear(h_cond_i) : [B, N_tgt, d]   ─────┐  (added into main DiT block i)
                                                        │
Denoising DiT  (main path, 30 blocks total in CogVideoX-5B)
    in : concat([noise tokens, recent context tokens], dim=token) + text-cond via 3D attn
       : [B, N_tgt + N_ctx, d]
    block i:
        h_i = DiTBlock_i(h_{i-1}, text=[B, L_text, d])
        if i ≤ 18:
            h_i ← h_i + ZeroLinear(h_cond_i)            ◄────┘
        if i ∈ {His-Cross-Attn layers}:                 (≥1 inserted; exact count ?)
            q ← h_i (video tokens)            : [B, N_tgt, d]
            k,v ← episodic_tokens             : [B, N_ref, d]
            h_i ← h_i + CrossAttn(q,k,v)      : [B, N_tgt, d]
    out : [B, N_tgt, d]
        └→ unpatchify + VAE Dec. : [B, F, 3, 480, 720]   (newly generated frames)
────────────────────────────────────────────────────────────────────────────────

Memory Update (after decoding new frames)
  ├─ Predict per-frame point map (CUT3R, online recurrent):
  │     new_pts : [B, F, H_p, W_p, 3]   (H_p×W_p ~ 384×672 in dataset stage; inference uses CUT3R metric pts, ?)
  │     new_cam : [B, F, 6 or 3×4]
  ├─ TSDF-Fusion on new_pts → filter dynamic voxels
  │     voxel grid V : (D(v), W(v))     (max grid dim ≤ 1200; voxel size auto-rescaled)
  └─ Merge into global static point cloud (shared world coords via persistent CUT3R state)
     Update keyframe set if visibility-mask reveals area > τ
```

> 註:`d` (DiT hidden)、patch size `p`、patchify 後 `N_cond / N_ctx / N_tgt / N_ref` 的精確數值,以及 historical cross-attention 插入的層索引與層數,paper 並未明確列出,以 `?` 表示;對應細節寫入 §5.3 各模組的 Implementation Details。

### 5.3 Per-Module Breakdown

#### 5.3.1 Spatial Memory Storage (TSDF-Fusion + CUT3R)

**Function:** 以 TSDF voxel grid 增量地融合每一新生成 frame 的 static point map,維護一個跨時間的 global static point cloud,作為長期 3D 幾何骨架。

**Input:**
- Name: `new_pts_i, new_cam_i`(來自 CUT3R)、`d_i(v)`(該 frame 對 voxel `v` 的 truncated signed distance)、`w_i`(frame-level confidence, 預設 1)
- Shape: `new_pts_i` ≈ `[B, H_p, W_p, 3]`(inference 階段用 CUT3R 的 metric-scale pointmap,具體 `H_p×W_p` paper 未明說,以 `?` 標註);voxel grid 維度上限 1200(超過則按比例放大 voxel size)
- Source: 自迴歸生成的新 frames,經 CUT3R 線上 4D 重建(Fig. S1)

**Output:**
- Name: 更新後的全域 TSDF 體素場 `(D'(v), W'(v))`,以及由其 marching-cubes / point sampling 得到的 global static point cloud
- Shape: voxel grid `[D, H, W]`(D, H, W 由場景包圍盒決定,最大邊 ≤ 1200);輸出 point cloud 點數隨場景大小變動
- Consumer: §5.3.4 的 Static point cloud rendering 模組

**Processing:**

對每個新觀測 frame `i`,逐 voxel 執行加權平均更新:先把 CUT3R 預測的 per-pixel 3D points 投回 voxel grid,計算每個 voxel 的 truncated signed distance `d_i(v)` 與 weight `w_i`,再用下式更新 `D(v), W(v)`(Eq. 2)。動態物件因跨幀深度不一致,在 voxel 上累積成低 confidence、雜訊大的 TSDF,於最終融合中被自然壓抑,達到 implicit 動靜分離。Inference 採 CUT3R(而非 dataset 階段的 Mega-SaM)是為了 online、recurrent、共享 world coordinate;每步推論結束保存 CUT3R 的 state dict 與 pose retriever 參數作為下一步初始化。

**Key Formulas:**

$$
D'(v) = \frac{W(v) \cdot D(v) + w_i \cdot d_i(v)}{W(v) + w_i}, \qquad W'(v) = W(v) + w_i
$$

**Implementation Details:**

Mega-SaM 在資料建構期將輸入解析度 resize 到 384×672;TSDF 階段先依場景包圍盒與當前 voxel size 計算 grid dims,若最大邊超過 1200 則按比例放大 voxel size 以避免 OOM。Inference 期改用 CUT3R 是為了避免 NDC 座標下無法直接合併不同 stage 的重建,以及長視訊 GPU memory 限制。`w_i` 通常設 1。

#### 5.3.2 Working Memory (Recent Context Frames)

**Function:** 提供 short-term 動態上下文,讓模型在靜態幾何骨架之上產生時間連續、運動合理的動態元素。

**Input:**
- Name: 最近 `k+1` 張 latent frames(inference 取 `k=5`)
- Shape: `[B, k+1, 3, 480, 720]`,在時間維度 zero-padding 到 `F=49` 後送入 VAE Enc.
- Source: 上一輪自迴歸生成的最後幾張 frame

**Output:**
- Name: `ctx_tokens`
- Shape: `[B, N_ctx, d]`(經 3D-VAE 壓縮到 `[B, C_z=16, F', 60, 90]` 後 patchify;`N_ctx` 與 `d` 在 paper 未列具體值,以 `?` 標註)
- Consumer: 與 target video tokens 沿 frame 維度 concat,送入 Denoising DiT

**Processing:**

把 source video 的最後 5 frames 與目標序列的 token 沿 frame 維度 concat,等同於告訴 DiT「請從這段已生成的動態接續下去」;同時 target 的條件 token(來自 §5.3.4 渲染分支)也與 recent context tokens 配對,確保 frame-level correspondence。每次 autoregressive iteration 滑動更新這 `k+1` frames。

**Key Formulas:**

$$
\text{tokens}_{\text{in}} = \mathrm{concat}\bigl(\mathrm{Patchify}(\mathrm{VAE}(\text{ctx})),\ \mathrm{Patchify}(z_t)\bigr) \quad \text{along frame axis}
$$

**Implementation Details:**

Paper 明確指出「the latest 5 historical frames」;訓練時 video length 為 49 frames、解析度 480×720,batch size 8,8×A100,6000 iters,lr `2e-5`。Working memory 不改變 DiT backbone,只是 token concat。

#### 5.3.3 Episodic Memory (Representative Historical Slots + Historical Cross-Attention)

**Function:** 補回 spatial memory 中因 point cloud 過稀疏而流失的外觀細節與 identity,以稀疏 keyframe 形式存放長距離歷史。

**Input:**
- Name: `ref_frames`(historical reference frames),由 visibility-mask-driven selection 累加
- Shape: `[B, M, 3, 480, 720]`(`M` 隨生成過程動態變化, paper 未明確上限,以 `?` 標註);經 3DVAE 後 `[B, C_z, M', H', W']`,patchify 為 `[B, N_ref, d]`
- Source: 自迴歸過程中每當 newly revealed unknown region 超過閾值時,把該幀加入 memory set

**Output:**
- Name: 更新後的 video tokens `h_i`
- Shape: `[B, N_tgt, d]`(與輸入相同 shape,內容被 cross-attention 注入歷史資訊)
- Consumer: Denoising DiT 後續 block

**Processing:**

把當前正在生成的 video tokens 當作 query,reference tokens 當作 key/value,做 cross-attention(Sec. 3.3 第三點):

1. visibility-mask 監控:每步用當前 spatial point cloud 沿目標 trajectory 投影產生 visibility mask,計算「newly revealed unknown area」;當其超過預設 threshold 時觸發 keyframe 加入。
2. encoder:被選中的 frame 與當前生成 batch 共用 3DVAE / patchify pipeline,得到 `[B, N_ref, d]`。
3. attention:在 main DiT 的指定 block 之間插入 His. Cross Attn 層,query 來自 video tokens、key/value 來自 reference tokens。

**Key Formulas:**

$$
\mathrm{HisCrossAttn}(Q, K, V) = \mathrm{softmax}\!\Bigl(\frac{Q K^{\top}}{\sqrt{d_k}}\Bigr)\, V,\quad Q = h_{\text{video}},\ K = V = h_{\text{ref}}
$$

**Implementation Details:**

Paper 說明「we add a historical cross attention to guide information exchange」並標示在 Fig. 2 中插入於若干 DiT blocks 之間,但具體插入層數與位置 paper 未列(以 `?` 表示)。Visibility threshold 與最大 keyframe 數量亦未明說。Episodic memory 在 ablation(Table 3, Fig. 5)被證實對 long-term consistency 與 subject identity 至為關鍵。

#### 5.3.4 Condition DiT (Static Point Cloud Rendering Branch, ControlNet-style)

**Function:** 將 long-term spatial memory 沿目標 camera trajectory 渲染成「靜態 RGB 條件 video」,並透過零初始化 linear 旁路把每一條件 block 的特徵加進主 DiT,引導 camera control 與靜態區域一致性。

**Input:**
- Name: `cond_video`(沿 target trajectory 渲染的靜態點雲影像;未覆蓋區域填黑)
- Shape: `[B, F=49, 3, 480, 720]` → 3DVAE → `[B, C_z=16, F', 60, 90]` → Patchify → `[B, N_cond, d]`
- Source: §5.3.1 維護的 global static point cloud + 相機軌跡 → point-based rendering

**Output:**
- Name: 18 條 zero-initialised residuals `{Δh_i}_{i=1..18}`
- Shape: 每條 `[B, N_tgt, d]`,逐 block 加到主 DiT 對應層
- Consumer: 主 Denoising DiT 的前 18 個 block

**Processing:**

1. 用 pre-trained 3DVAE 把 condition video 編碼到 latent,patchify 成 token。
2. 從 CogVideoX 複製前 18 個 DiT block 作為 condition DiT,輸入即 condition tokens。
3. 每個 condition block 的輸出特徵先經一條 **zero-initialised linear**(初始權重為 0,訓練開始時不擾動主 DiT),再加到主 DiT 對應 block 的 feature map 上。等同 ControlNet 的訊號注入策略,確保訓練初期主分支行為不變,逐步學會吸收幾何條件。

**Key Formulas:**

$$
h_i^{\text{main}} \leftarrow h_i^{\text{main}} + W^{\text{zero}}_i \cdot h_i^{\text{cond}},\quad W^{\text{zero}}_i \big|_{t=0} = \mathbf{0}
$$

**Implementation Details:**

Backbone 為 CogVideoX-5B-I2V、總共 30 個 DiT block(常見 5B 設定),其中前 18 個用於 condition DiT,layer-by-layer 與主 DiT 配對。背景無 point cloud 區域在渲染時填黑。Condition DiT 與主 DiT 的權重在訓練中皆可微調,但 zero-init linear 是 ControlNet 風格的關鍵(Sec. 3.3 明說 “similar design as ControlNET [88]”)。

#### 5.3.5 Denoising DiT (Main Backbone with 3D Attention)

**Function:** 主去噪網路;把含噪 target latent、recent context latent、text condition、condition DiT 的注入訊號、episodic cross-attention 訊號整合,輸出去噪後的 target video latent。

**Input:**
- Name: `z_t`(噪聲 latent)、`ctx_tokens`、`text_emb`、`{Δh_i}` from condition DiT、`ref_tokens`(來自 episodic memory)
- Shape: 主 token 序列 `[B, N_tgt + N_ctx, d]`;text `[B, L_text, d]`(經 T5 + linear projection,d 同 DiT hidden,精確值 paper 未列,標 `?`)
- Source: §5.3.2、§5.3.3、§5.3.4 與 T5 文字編碼器

**Output:**
- Name: 去噪後 latent token,reshape + VAE Dec. 後的 RGB frame
- Shape: token `[B, N_tgt, d]` → unpatchify → `[B, C_z, F', 60, 90]` → VAE Dec. → `[B, F=49, 3, 480, 720]`
- Consumer: 寫入下一輪 working memory、CUT3R 4D reconstruction、TSDF 更新

**Processing:**

1. patchify 噪聲與 context latent,沿 frame 維度 concat,送進 3D self-attention DiT block。
2. 每個 block 內部 3D attention 同時處理空間與時間 token,並用 text embedding 做 cross-attention(沿用 CogVideoX 設計)。
3. 前 18 個 block 接收來自 condition DiT 的零初始化注入。
4. 在指定 block 之間插入 His. Cross Attn,讓 video tokens 可查詢 episodic frames。
5. 最終 block 輸出對應 target frames 的去噪 latent。

**Key Formulas:**

$$
\mathcal{L}(\theta) = \mathbb{E}_{t, x_0, \epsilon}\bigl\|\,\epsilon_\theta(x_t, t, c_{\text{ctx}}, c_{\text{cond}}, c_{\text{epi}}, c_{\text{text}}) - \epsilon\,\bigr\|_2^2
$$

其中 $x_t = \alpha_t x_0 + \sigma_t \epsilon$(Eq. 1),$\{c_*\}$ 為對應的記憶條件。

**Implementation Details:**

CogVideoX-5B-I2V 預訓練權重(從 DaS 微調而來);訓練 6000 iters、lr `2e-5`、mini-batch 8、8×A100;video 49 frames、480×720。3D-VAE temporal 壓縮約為 4×(`F'≈⌈F/4⌉`,具體 stride paper 未明說,以 `?` 表示)。Loss 沿用 latent diffusion 的 epsilon-prediction(Eq. 1)。

#### 5.3.6 Autoregressive Inference Loop with Memory Update

**Function:** 串接「生成 → 點雲預測 → TSDF 融合 → 渲染 condition video → 下一輪生成」,完成 long-horizon、open-ended video world model 推論。

**Input:**
- Name: `(global_pcl_t, episodic_set_t, recent_ctx_t, target_traj_{t+1}, action_text_{t+1})`
- Shape: 各記憶結構維度同前
- Source: 上一輪輸出 + 使用者給定的下一段 trajectory / action 提示

**Output:**
- Name: `target_video_{t+1}` 與更新後的 `global_pcl_{t+1}, episodic_set_{t+1}, recent_ctx_{t+1}`
- Shape: video `[B, 49, 3, 480, 720]`;記憶結構同前
- Consumer: 進入下一輪 autoregressive iteration

**Processing:**

1. 沿 `target_traj_{t+1}` 渲染 `global_pcl_t` → `cond_video`(無覆蓋處填黑),並計算 visibility mask。
2. 取最近 5 frames 作 working memory;選取 episodic keyframes(視 visibility 揭露面積決定是否新增)。
3. 跑 §5.3.5 的去噪過程得到 `target_video_{t+1}`。
4. 對新 frames 用 CUT3R 線上預測 metric-scale point map 與 camera params(保留 state dict 跨步)。
5. 用 §5.3.1 的 Eq. (2) 把過濾後的 point cloud 融合進 `global_pcl_{t+1}`。
6. 若新生成 frame 揭露超出 threshold 的未知區域,將其加入 `episodic_set_{t+1}`。
7. 更新 `recent_ctx_{t+1}` 為最新 5 frames,進入下一輪。

**Key Formulas:**

$$
\bigl(V_{t+1}, \mathcal{P}_{t+1}, \mathcal{E}_{t+1}\bigr) = \mathcal{F}_{\theta}\!\bigl(\mathcal{P}_{t},\ \mathcal{E}_{t},\ \mathcal{C}_{t},\ \tau_{t+1},\ a_{t+1}\bigr)
$$

其中 $\mathcal{P}$ 為 spatial memory、$\mathcal{E}$ 為 episodic memory、$\mathcal{C}$ 為 working memory、$\tau$ 為 camera trajectory、$a$ 為 action prompt。

**Implementation Details:**

CUT3R state dict 與 pose retriever 參數在每步存取,確保跨步 reconstruction 在同一 world coordinate;TSDF 在 inference 時對 voxel grid 大小做動態 rescaling 以避免 CUDA OOM。Visibility threshold、最大 episodic 數量、historical cross-attention 插入深度等具體超參 paper 未列(以 `?` 標註)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| MiraData [39] | Geometry-grounded video generation with paired static point cloud + future RGB supervision | 90K structured 97-frame clips (49 source + 48 target with shared transition frame); 480×720 resolution | Train: 約 90K samples（the paper does not specify an explicit train/val split）；Test: 500 randomly selected unseen sequences |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PSNR | View recall consistency on paired frames at the same camera pose under forward/reversed trajectories（重訪一致性） | yes |
| SSIM | 同上配對影格的結構相似度 | yes |
| LPIPS | 同上配對影格的感知距離（lower is better） | yes |
| VBench Aesthetic Quality [36] | 美學品質 | no |
| VBench Imaging Quality | 影像品質 | no |
| VBench Temporal Flickering | 時序閃爍程度 | no |
| VBench Motion Smoothness | 動作平滑度 | no |
| VBench Subject Consistency | 主體一致性 | no |
| VBench Background Consistency | 背景一致性 | no |
| User Study Cam-Acc | Average Human Ranking（1–4）of camera trajectory accuracy | no |
| User Study Stat-Cons | AHR of static-region consistency on revisits | no |
| User Study Dyn-Plaus | AHR of dynamic plausibility（動作合理性） | no |

Primary metrics are the view-recall PSNR/SSIM/LPIPS triplet, since the paper's central claim is improved long-term spatial consistency on revisited camera poses.

### 6.3 Training and Inference Settings

- Backbone：CogVideoX-5B-I2V [79]，pretrained from DaS [25]。
- Hardware：8× NVIDIA A100 GPUs。
- Mini-batch size：8。
- Optimizer：the paper does not specify（僅給出 learning rate）。
- Learning rate：$2 \times 10^{-5}$；schedule the paper does not specify。
- Training iterations：6,000。
- Training video length：49 frames，resolution 480×720。
- Architecture details（§3.3）：condition DiT 由 CogVideoX 前 18 個 pre-trained DiT blocks 複製而來；每個 main DiT block 的輸出特徵經 zero-initialized linear layer 加回 main DiT，類似 ControlNet [88]。並於指定 block 加入 historical cross-attention，以 video tokens 為 query、reference tokens 為 key/value。
- Inference（§4 與 Appendix A）：autoregressive；每步以最近 5 個 historical frames 作為 working memory；新生成影格的 point map 由 CUT3R [69] 線上預測（取代 dataset 階段使用的 Mega-SaM [44]，避免跨 stage 對齊與 CUDA 記憶體問題），經 TSDF-Fusion 過濾動態後並入 global static point cloud；保留 CUT3R 的 state dict 與 pose retriever 參數作為下一步的初始化以維持同一座標系。
- Episodic memory 寫入策略：mask-based visibility check，當新揭露區域超過 a predefined threshold（the paper does not specify the numeric threshold）即把當前影格納入 memory set。
- TSDF voxel grid（Appendix A）：以場景邊界估計初始 voxel size，若最大維度超過 1200 則等比例放大 voxel size 以避免記憶體溢出。
- Mega-SaM 預處理（Appendix A）：input video resize 至 384×672，再以 optical flow + Covariance-based Variable Decomposition 精修相機運動。
- 推論的 sampling steps、CFG scale、硬體配置 the paper does not specify。

### 6.4 Main Results

View recall consistency（reversed-trajectory paired frames）與 user study（AHR，1–4，higher is better）：

| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Cam-Acc ↑ | Stat-Cons ↑ | Dyn-Plaus ↑ |
|---|---|---|---|---|---|---|
| TrajectoryCrafter [82] | 11.71 | 0.4380 | 0.5996 | 1.6320 | 1.7802 | 1.6255 |
| DaS [25] | 12.01 | 0.4512 | 0.5874 | 2.5660 | 2.4396 | 2.7033 |
| Wan2.1-Inpainting [66] | 12.16 | 0.4506 | 0.5875 | 2.1760 | 2.3956 | 2.2701 |
| **Ours** | **19.10** | **0.6471** | **0.3069** | **3.6260** | **3.3846** | **3.4011** |

VBench general video quality：

| Method | Aesthetic ↑ | Imaging ↑ | Temporal Flickering ↑ | Motion Smoothness ↑ | Subject Cons. ↑ | Background Cons. ↑ |
|---|---|---|---|---|---|---|
| TrajectoryCrafter | 0.5255 | 0.6428 | 0.6160 | 0.9843 | 0.8830 | 0.9227 |
| DaS | 0.5635 | 0.6617 | 0.7520 | 0.9856 | 0.9325 | 0.9494 |
| Wan2.1-Inpainting | 0.5661 | **0.6788** | 0.6433 | 0.9868 | 0.9357 | **0.9513** |
| **Ours** | **0.5835** | 0.6701 | **0.7580** | **0.9886** | **0.9359** | 0.9506 |

Notes：本方法在 view recall（PSNR +6.94 dB vs. 最強基線 Wan2.1-Inpainting）與 user study 三項皆顯著領先；VBench 中 Wan2.1 在 Imaging 與 Background Consistency 略勝，作者解釋為 Wan2.1 inpainting 常生成偏靜態的場景（不跟隨幾何引導），自然更易拿到背景一致性高分。即便如此，PSNR 19.10 距離 perfect reconstruction 仍遠，作者承認複雜場景的逐細節記憶仍是難題。

### 6.5 Ablation Studies

Table 3 比較三種 memory 機制的組合（VBench 指標）：

| Variant | Aesthetic | Imaging | Flickering | Smoothness | Subject | Background |
|---|---|---|---|---|---|---|
| w/o episodic mem | 0.5603 | 0.6485 | 0.7260 | 0.9870 | 0.9326 | 0.9489 |
| w/o working mem | 0.5551 | 0.6384 | 0.6740 | 0.9862 | 0.9331 | 0.9453 |
| Full model | **0.5835** | **0.6701** | **0.7580** | **0.9886** | **0.9359** | **0.9506** |

- **w/o working memory（移除 recent context frames）**：在 Temporal Flickering（0.7580→0.6740）與 Motion Smoothness 下降最明顯，符合預期——working memory 主管短期動作連續性；Figure 5 也顯示動態主體的運動合理性顯著退化。此 ablation 直接針對「短期動態連續性」這個元件的設計目標，**屬於 diagnostic 而非 sanity check**。
- **w/o episodic memory（移除 sparse historical reference frames）**：所有 VBench 指標皆下降（Aesthetic 0.5603、Imaging 0.6485、Flickering 0.7260），Figure 5 顯示重訪時的角色／物件視覺細節遺失。作者主張 episodic memory 用於補足 fused point cloud 太稀疏、留不住外觀細節的弱點，**ablation 結果與設計動機對齊**。
- **Spatial memory 的 ablation 缺席**：論文宣稱的核心貢獻是 geometry-grounded long-term spatial memory（static point cloud + TSDF-Fusion），但 Table 3 並未提供「w/o spatial memory」的數值。Figure 5 雖視覺上展示了 Static Point Map 的角色，量化上卻只能從與基線的差距間接推論——這是 ablation 設計的一個缺口，使「spatial memory 對 PSNR/SSIM 提升貢獻多少」無法從 ablation 表中獨立量化。
- 缺少對 working memory 視窗長度（k=5）、episodic memory threshold、TSDF voxel size、condition DiT 抽取的 18 blocks 等設計選擇的敏感度分析；這些屬於 hyperparameter 層面的 diagnostic ablation 也都缺席。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline — 比較 TrajectoryCrafter [82]、DaS [25]、Wan2.1-Inpainting [66]，其中 Wan2.1 與 DaS 屬近期強 baseline，但同期主打 long-context 的 FramePack [87] 與 Long-context AR [24] 僅在 related work 提及、未納入定量比較。
- [missing] Has cross-task / cross-dataset evaluation — 訓練與測試皆在 MiraData 子集（500 unseen sequences），未在第二個資料集或第二個任務（例如 RealEstate10K、DL3DV、driving 場景）驗證泛化。
- [partial] Has ablations that diagnose the new components — working / episodic memory 的移除實驗具診斷性；但**缺 spatial memory 自身的 ablation**（核心貢獻卻未量化拆解），且無 hyperparameter 敏感度（k、threshold、voxel size）研究。
- [missing] Has a scaling study — 未報告模型大小（固定 5B）、context 長度、訓練資料規模或迭代步數的 scaling 曲線；只有單一 6,000-iteration 設定。
- [missing] Has an efficiency / wall-clock comparison — 沒有任何 per-frame latency、throughput、GPU memory、autoregressive 步數成本的數據對比；僅在 appendix 提到 CUT3R 取代 Mega-SaM 是出於記憶體考量，未量化。
- [missing] Reports variance / standard deviation / multiple seeds — Table 1、2、3 全為單點數值，無 std、無 confidence interval、無 multi-seed；user study 僅給平均 AHR 而無 inter-rater agreement 或變異數。
- [partial] Releases code / weights / data sufficient for reproducibility — 論文有 project page（https://spmem.github.io/），但本文未明確聲明 code / weights / 90K dataset 的釋出與授權；MiraData 為公開資料集、CogVideoX/CUT3R/Mega-SaM 皆有開源，理論上可重建 pipeline，但「9 萬筆配對資料 + 訓練 checkpoint」是否釋出 the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

1. **「Geometry-grounded 長期記憶能改善 revisit 一致性」**:Table 1 的 PSNR/SSIM/LPIPS 與 Fig 4 中段的 view recall 對比 supported;但要注意 baseline 不具備等價條件機制,這項支持帶有結構性偏向(見 §4.2.2)。
2. **「working / spatial / episodic 三類記憶各自必要」**:Table 3 與 Fig 5 顯示拿掉 working、episodic 任一者皆下降,partially supported;論文沒做「拿掉 spatial memory(只留另兩者)」的對照,因此 spatial 的必要性只能從與 baseline 的 gap 間接推測,不算直接 ablation 證據。
3. **「TSDF 能自動分離靜態與動態」**:Sec 3.2 給出機制論述,Fig S1 給出視覺示例,partially supported;論文沒有在動態保留 / 動態洩漏到靜態記憶這兩個方向給任何量化指標,只能在 Wan2.1 的反例旁佐證。
4. **「精準的相機控制」**:VBench 與使用者研究的 Cam-Acc $3.626$ supported,Fig 4 上排亦顯示在大幅相機運動下仍能跟隨軌跡。
5. **「paving the way towards long-term consistent world generation」(Abstract / Conclusion)**:overclaimed。訓練 clip 為 $49+48$ frames、推論長度與 throughput 數據未報、drift 未處理、character consistency 委由 future work,目前證據只能支撐「在 MiraData-like 場景、合理長度的 revisit 上比 point-map baseline 更好」。

### 7.2 Fundamental Limitations of the Method

**記憶介面本身丟失了外觀**。TSDF-fused 點雲只承載幾何骨架,episodic memory 僅以稀疏關鍵影格補回紋理,但兩者之間沒有一個 dense 的中介表徵能保存「這個位置這時段的光影 / 材質 / 季節」這類隨時間慢變的非幾何屬性。一旦 spatial memory 與 episodic frames 在這些屬性上互相矛盾,模型只能由 base diffusion prior 憑空猜,系統並無原則性的偏向。

**動靜分離條件不充分**。TSDF 的隱含假設是「同一 voxel 跨幀應觀測一致,動態物體因觀測不一致而被 weighted average 壓低」。這只在「相機有足夠 baseline 且動態物體運動相對相機足夠快」時成立。靜止相機 + 緩動主體、或動態主體在 49 frame 內相對 voxel 尺度位移有限的情況,動態會被當作高一致性靜態而烘進記憶且永遠無法剔除,因為 $W(v)$ 單調累積,沒有遺忘或負向更新機制。

**沒有閉環校正**。一旦 spatial memory 因 4D 重建失敗(Fig 6)寫入錯誤,後續 frame 在錯誤幾何引導下生成,新觀測又被 fuse 回同一錯誤體素,誤差會被加權平均所「平均化」、難以收斂回真值。論文未提出任何回滾、信心衰減或 keyframe 級重建重置機制。

**訓練分佈被 Mega-SaM 的可重建性所定義**。資料集挑選即偏向「Mega-SaM 能跑通的場景與軌跡」,因此模型沒有學過如何在重建退化的條件下優雅降級;Fig 6 的失敗模式不只是推論限制,而是來自訓練端的 selection bias,擴大訓練資料量只會放大同一偏差。

### 7.3 Citations Worth Tracking

- **[69] CUT3R(Wang et al., CVPR 2025)**:本作推論期 spatial memory 持續更新的核心模組,任何想復現 / 改進此線的人都得先理解其 stateful recurrent 設計與 NDC vs metric 座標處理。
- **[44] Mega-SaM(Li et al., CVPR 2025)**:訓練資料的 4D reconstruction backbone,其失敗模式直接決定本作的能力邊界。
- **[87] FramePack(Zhang & Agrawala, 2025)**:作者明示是互補而非競爭路線,從「character/identity 長期一致」切入,與本作的「scene geometry 長期一致」拼起來才是完整的 long-context world model 故事。
- **[13] Diffusion Forcing(Chen et al., NeurIPS 2024)**:替代的 AR 噪聲調度方案,可能與 spatial memory 條件機制疊加以解決 drift。
- **[25] DaS / DiffusionAsShader**:本作的 pretrained checkpoint 與主要 baseline,理解它的 point-map 條件設計才能正確衡量 SpMem 的增量貢獻。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在推論長度遠超訓練的 $49+48$ frame 視窗時(例如連續生成 $1{,}000$ frame),view recall 指標、CUT3R 累積誤差與 inference latency 的曲線各長什麼樣?論文完全未報。
- [ ] 對於緩動或長時靜止的動態物體(停在路邊的車、靜立的人),TSDF-Fusion 是否會把它們烘成 static memory?有沒有量化的「動態洩漏率」?
- [ ] 若拿掉 DaS 預訓權重從 CogVideoX-5B-I2V 直接 fine-tune,Table 1 對 DaS 的 gap 還會剩多少?也就是 spatial memory 本身對 DaS 的 net 增量是多少?
- [ ] Episodic memory 的可見性 mask 閾值如何選定,對最終一致性的敏感度為何?關鍵影格集在長序列下會無界增長嗎,有 capacity 上限策略嗎?
- [ ] 在非 MiraData 的分佈(室內、機器人操作視訊、第一人稱真實 ego-video)上,Mega-SaM/CUT3R 的可靠性差異是否會讓本框架失效?
- [ ] Historical cross-attention 的 reference token 數量增長時,attention 計算成本與品質權衡曲線為何?是否最終又落回 quadratic 的老問題?
- [ ] 使用者研究的 20 名受試者間 inter-rater agreement(Kendall's W 或 ICC)是多少?AHR 上 SpMem 與第二名的差距在統計上是否顯著?

### 8.2 Improvement Directions

1. **(最可行)為 TSDF voxel 加入信心衰減 / 負向更新機制**。目前 Eq 2 的 $W(v)$ 單調累積,把它改為 $W'(v) = \lambda W(v) + w_i$($\lambda < 1$),並允許在新觀測與舊觀測差異超出閾值時降權,理論上能讓錯誤幾何被後續 frame 校正,直接針對 §7.2 的「沒有閉環校正」。實作上只需改幾行融合程式,訓練流程不需重啟。
2. **以 neural feature field(3DGS 或 triplane)取代純 point cloud 作為 spatial memory**。點雲只攜帶幾何,episodic memory 是被迫補上的外觀補丁;若改用具特徵的 3D 表徵,可一次性同時承載幾何與低頻外觀,episodic memory 的角色就能退回「身分 / 細節」這種真正稀疏事件,符合 §7.2 第一段。
3. **與 FramePack [87] 結合**。作者已點名此路線解 character consistency,本作解 scene consistency,兩者直接 OR 起來(各自輸出條件 token 一起進 DiT)即可實驗。風險是 token 數量爆增與條件衝突,但這是少數作者明示鼓勵的擴展。
4. **在訓練資料端引入「困難軌跡」augmentation**。針對 Mega-SaM 失敗的軌跡類型(大幅角度跳變、高速穿越),用合成或半合成方式補入,並把 spatial memory 在這些 case 上強制設為 partial / corrupted,讓模型學會在記憶不可靠時 fallback 到 working memory,直接緩解 §7.2 第四段的 selection bias。
5. **(最具野心)把 TSDF + episodic 的兩階段表徵改寫成單一可學習的記憶模組**,例如以 cross-attention 將「歷史 frame token + 當前點雲 query」交由網路自行決定要從哪一邊取資訊,取代目前手工分流。代價是失去現有設計的可解釋性與動靜分離的硬保證,但能突破 TSDF 在動靜判定上的物理假設限制。
