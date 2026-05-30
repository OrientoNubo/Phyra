<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# LingBot-Map — Geometric Context Transformer for Streaming 3D Reconstruction

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | LingBot-Map |
| Paper full title | Geometric Context Transformer for Streaming 3D Reconstruction |
| arXiv ID | 2604.14141 |
| Release date | 2026-04-16 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2604.14141 |
| PDF link | https://arxiv.org/pdf/2604.14141 |
| Code link | https://github.com/robbyant/lingbot-map |
| Project page | https://technology.robbyant.com/lingbot-map |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Lin-Zhuo Chen | Nanjing University (3DV-lab, supervised by Yao Yao) | https://linzhuo.xyz | co-first author |
| Jian Gao | — | https://ygaojiany.github.io/ | co-first author |
| Yihang Chen | — | — | author |
| Ka Leong Cheng | — | — | author |
| Yipengjing Sun | — | — | author |
| Liangxiao Hu | — | — | author |
| Nan Xue | — | — | author |
| Xing Zhu | — | — | author |
| Yujun Shen | — | — | author |
| Yao Yao | Nanjing University, School of Intelligence Science and Technology (NJU-3DV Lab) | https://yoyo000.github.io/ | corresponding author |
| Yinghao Xu | HKUST (CSE); previously RobbyAnt | https://justimyhxu.github.io/ | corresponding author / project lead |

### 1.2 Keywords

streaming 3D reconstruction, geometric context attention, feed-forward 3D foundation model, SLAM-inspired attention, trajectory memory, camera pose estimation, transformer architecture, long-sequence inference

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al.) | base model | Feed-forward multi-view 3D foundation model whose ViT + alternating frame/global attention LingBot-Map adapts to streaming. |
| DUSt3R (Wang et al.) | predecessor | Pioneer feed-forward dense 3D regression from unposed images; defines the offline paradigm LingBot-Map streams. |
| CUT3R | baseline | RNN-style persistent recurrent state for streaming; cited as suffering from state forgetting. |
| StreamVGGT | baseline | Streaming VGGT variant via causal attention + caching; memory grows linearly, contrasted with GCA. |
| Stream3R | baseline | Causal-attention streaming reconstruction baseline compared in Figure 1 and tables. |
| Wint3R | baseline | Window-based streaming reconstruction compared head-to-head in Figure 1. |
| TTT3R | baseline | Test-time-training fix to recurrent state forgetting; LingBot-Map avoids TTT for real-time inference. |
| π3 | influence | Source of inspiration for the relative-pose loss formulation over the local sliding window. |

## 2. Research Overview

### 2.1 Research Topic

本研究關注串流式 (streaming) 3D 重建:給定連續視訊輸入,逐幀即時估計相機位姿與稠密深度/點雲,同時維持幾何精度、時序一致性與計算效率。作者指出此任務的核心挑戰是「選擇性地管理幾何上下文」——既要保留足夠長距離的觀測以避免漂移,又要讓串流狀態足夠精簡以支援長序列即時推論。論文提出 LingBot-Map,一個基於 Geometric Context Transformer (GCT) 與 Geometric Context Attention (GCA) 的前饋式 3D 基礎模型,將傳統 SLAM 中的「參考座標、局部視窗、全域地圖」結構抽象為三類學習式注意力上下文:anchor context (錨點上下文)、pose-reference window (位姿參考視窗) 與 trajectory memory (軌跡記憶)。該方法可在 518×378 解析度、超過一萬幀的長序列上以約 20 FPS 穩定推論,並於 Oxford Spires、7-Scenes、Tanks and Temples、ETH3D、NRGBD 等基準上同時超越串流式與迭代優化式既有方法。

### 2.2 Domain Tags

- computer vision
- 3D reconstruction
- SLAM
- deep learning
- foundation models

### 2.3 Core Architectures Used

- **Geometric Context Transformer (GCT)**: 本論文提出的整體骨幹,以交替堆疊的 Frame Attention 與 Geometric Context Attention 組成,負責處理串流影格並輸出每幀的相機位姿與深度圖。
- **Geometric Context Attention (GCA)**: 本論文核心設計,將串流上下文切分為 anchor context、local pose-reference window 與 trajectory memory 三種互補注意力,於統一框架內以端到端方式學會「該記什麼、該丟什麼」。
- **ViT backbone (DINOv2 init)**: 由 DINOv2 [47] 權重初始化的 Vision Transformer,以 patch size 14 將每張輸入影像編碼為 $M$ 個 image tokens,作為後續注意力模組的特徵來源。
- **Camera / Depth Heads**: 任務專屬輸出頭,分別從 camera token 預測絕對相機位姿 $\hat{P}_t$,從 image tokens 經由 DPT 風格深度頭預測稠密深度圖 $\hat{D}_t$。
- **VGGT 架構 (繼承)**: 作為前饋式 3D 基礎模型的基礎,LingBot-Map 沿用其 24 層交替式 frame/cross-frame attention 配置與監督形式,並將 cross-frame 全域注意力替換為 GCA 以支援串流。
- **Paged KV-cache + FlashInfer Runtime**: 推論時採用類 LLM 的 KV cache,以 paged 佈局管理 sliding-window 與 trajectory eviction,使 518×378、最高 1000 幀序列達到約 20 FPS。
- **Ulysses Context Parallelism**: 訓練時將不同 view 切分至多張 GPU 並透過 all-to-all 通訊計算注意力,克服長序列下 cross-frame attention 的 quadratic 記憶體瓶頸。

### 2.4 Core Argument

作者主張,既有串流式 3D 重建方法之所以在長序列與複雜場景下崩壞,根本原因不是模型容量不足,而是「上下文管理機制」設計失當。他們將既有路線歸納為三類失敗模式:(1) CUT3R 等以 RNN 維護單一持久狀態,壓縮過於激進造成幾何先驗遺忘;(2) StreamVGGT、Stream3R 等用 causal attention 加快取保留近乎完整歷史,但未做選擇性過濾,記憶體與計算隨序列線性膨脹,且把有用幾何訊號淹沒在冗餘中;(3) VGGT-SLAM、MASt3R-SLAM 等混合派以手工 keyframe 啟發式與 pose-graph 後端做選擇,擺脫不了非端到端與迭代最佳化的即時性瓶頸。作者由此抽出設計原則:串流狀態應「選擇性保留最重要的東西」,而選擇本身應從資料端到端學得,並以幾何先驗為結構約束。基於此,他們從經典 SLAM 的功能解構出發——必須同時維持「座標與尺度錨定」、「局部稠密配準」與「全域漂移修正」三種互補上下文——並一一對應為 GCA 中的 anchor context、local pose-reference window、trajectory memory。anchor 用前 n 幀建立尺度與座標系並作為固定參照;局部視窗保留最近 k 幀的完整影像 token 以提供稠密相對位姿線索;軌跡記憶則對更早的幀僅保留每幀 6 個壓縮 token,使每幀新增 token 數從 causal 的 (M+6) 降到 6,長序列下記憶體與計算近乎常數成長。如此既不放棄長距離一致性,也不犧牲即時性,邏輯上必然優於只能擇一犧牲的既有設計;再輔以漸進式訓練、context parallelism 與相對位姿損失,模型才得以在端到端框架下穩定學會「該記什麼、該丟什麼」。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(160 words)

標題「Geometric Context Transformer for Streaming 3D Reconstruction」直接點出三個關鍵字:GCT 這個新架構、streaming 設定、以及 3D 重建任務,暗示作者要把 offline 3D foundation model 的成功推廣到 online 場景。Abstract 隨即把 streaming 3D reconstruction 的目標收斂到三個同時必須兼顧的指標──geometric accuracy、temporal consistency、computational efficiency,這三點正好對應後文方法設計的三條主軸,也預示 baseline 方法被批評的方向。

接著 abstract 把方法定位成「受 SLAM 啟發的 feed-forward foundation model」,並命名為 LingBot-Map。這個定位很關鍵:它一方面承接 VGGT、DUSt3R 等 feed-forward 路線(no test-time optimization),另一方面把 SLAM 的 reference frame / local map / global map 三層空間記憶結構搬到 attention 裡,因此核心貢獻不是 backbone 而是 attention pattern。Abstract 列出三類 context──anchor context、pose-reference window、trajectory memory,分別對應 coordinate grounding、dense geometric cues、long-range drift correction,這三個對齊關係幾乎逐字出現在 §3.2,讀者可以把 abstract 視為後文 Method section 的 1:1 索引。

最後 abstract 給出兩個量化承諾用於誘發讀者繼續讀下去:518 × 378 解析度下約 20 FPS、可處理超過 10,000 frames 的序列;並聲稱在多個 benchmark 上勝過 streaming 與 iterative optimization-based 方法。這句話為 §6 的 Oxford Spires sparse / dense 兩個設定預先鋪好「速度 + 長序列」雙軸論述。Figure 1 同步以 ATE 與 reconstruction accuracy 兩個雷達圖視覺化此宣稱,讓讀者在進入正文前已經建立「LingBot-Map 在所有軸都領先」的第一印象。

### 3.2 Introduction

(720 words)

Introduction 用一個認知科學的譬喻開場:人類的空間記憶並不忠實地保留每一刻觀察,而是稀疏、結構化、有效率地保留關鍵 cue。作者藉此提問:能不能讓機器以同樣的「選擇性、有效率」方式做 streaming 3D reconstruction?這個 framing 為後文「不是儲存多少,而是儲存什麼」的設計哲學立下基調。

第二段把問題定位到當前研究脈絡。VGGT、Depth Anything 3 等 3D foundation model 已能在單次 feed-forward 中預測 camera pose、depth、point map,但都侷限在 offline、需要存取整個影像集合的設定。最近開始有方法試圖把這套能力 adapt 到 streaming,但長序列與複雜場景的 robustness 仍不足。作者把核心難題濃縮成一句話「selective context management」:在長期一致性所需的豐富 geometric context 與高效推論所需的緊湊 state 之間取得平衡。

第三段是分類批評,用來建立自家方法的差異化空間。作者把 prior streaming 工作分三類並各自指出缺陷:(1) CUT3R 用 persistent recurrent state,壓縮過於激進導致 state forgetting;(2) StreamVGGT、Stream3R 用 causal attention + caching,幾乎保留全部歷史,造成 memory / computation 線性甚至更高速增長,且無法分辨關鍵與冗餘;(3) VGGT-SLAM、MASt3R-SLAM 把 learned 3D model 接到 classical SLAM backend,雖然有結構化的 keyframe / pose graph,但依賴 hand-crafted heuristic 並依賴 iterative optimization,難以 real-time。這三類缺陷恰好對應方法要解決的三個面向。作者由此抽出設計原則:streaming state 應該選擇性保留「最重要的」而非「最多的」,並且這個選擇應該是在 geometric prior 上 grounded、但 end-to-end 從資料學出來的。

第四段引入 LingBot-Map 與其核心元件 Geometric Context Attention (GCA)。論述策略是把 classical SLAM 的洞見「robust real-time reconstruction 需要三種 spatial context:reference frame、local window、global map」直接映射到三個 learned attention 機制:anchor context (coordinate / scale grounding)、local pose-reference window (dense local geometry)、trajectory memory (drift correction)。關鍵宣稱是這個結構化但 learned 的表徵能在任意長序列下維持 nearly constant memory and computation per frame──作者特別點出 trajectory memory 把 local window 之外的 context 壓成 compact per-frame token,這正是 §3.2 複雜度分析(每幀只增加 6 tokens)的伏筆。

第五段補上訓練端的支援:progressive training + context parallelism (Ulysses) + relative loss formulation,讓模型能穩定地在大規模 long-sequence 資料上學習。這段為 §4.2 與 §4.3 預先打底,並暗示「光有架構不夠,還必須有對應的 scaling recipe」。

最後 contribution bullets 把全文 take-away 收成三點:(1) GCA 三層 context 的 streaming foundation model;(2) progressive + context-parallel + relative loss 的訓練 recipe;(3) 在 Oxford Spires、Tanks and Temples、ETH3D、7-Scenes 等 benchmark 上 SOTA。值得注意的是 contribution 同時宣稱 reconstruction quality 與 inference speed 兩軸領先,這直接對應 §6.2 dense setting 的 ATE + FPS 雙軸表格,顯示 introduction 的 contribution claim 與 experiment 設計是有意對齊的。

### 3.3 Related Work / Preliminaries

(620 words)

Related Work 分三段組織,從 traditional pipeline 走到 3D foundation model,再聚焦到 streaming 3D reconstruction,逐步把比較對象與設計缺口收斂到自家方法的 niche。

第一段「Traditional 3D Reconstruction」回顧 SfM、SLAM、MVS 三條傳統路線。作者強調這些 pipeline 通常 modular 且以 bundle adjustment 為核心,並指出深度學習過去十年主要是「替換 component」(如 feature extractor、matcher),而 VGGTSfM、DROID-SLAM、MVSNet 才開始嘗試 end-to-end。這段的潛台詞是:LingBot-Map 屬於 end-to-end 路線,但要保留 SLAM 的結構化記憶觀念──這也呼應 introduction 「SLAM 啟發但 learned」的口號。

第二段「3D Foundation Model」勾勒 LingBot-Map 直接繼承的家系。DUSt3R 是 paradigm shift,但只支援 two-view 並需要 alignment optimization;VGGT 用 cross-view attention 突破多視角限制並證明大規模資料 + 強架構能顯著提升品質。隨後作者列舉一系列後續方向(reconstruction accuracy、efficiency、dynamic scenes、novel view synthesis、multi-modal),刻意展示這條路線生態繁茂,但用一句結語收束「這些方法主要為 offline 設計,並未處理 streaming 特有的長期一致性與資源管理挑戰」,把 niche 留給自己。

第三段「Streaming 3D Reconstruction」是真正的競品分析。作者把現有 streaming 工作切成兩類:hybrid SLAM-based(整合 3D foundation model 與 SLAM pipeline,如 VGGT-Long、VGGT-SLAM、MASt3R-SLAM)與 end-to-end feed-forward。前者批評是依賴 hand-crafted component 與 careful tuning,後者再細分:CUT3R 用 RNN 維持 persistent state、TTT3R 透過 test-time training 緩解 forgetting、StreamVGGT 與 Stream3R、Wint3R 則改用 causal attention + caching。這個逐一點名的策略讓讀者在進入 experiment 表格前就已經對每個 baseline 的設計缺陷有預期──之後 §6 直接看到這些方法在長序列上 drift 嚴重,就會在故事邏輯上被解釋為「課文已預告」。

最後作者特別處理 concurrent works(LoGeR、Scal3R、ZipMap),這些方法和 LingBot-Map 一樣關心 long-sequence scaling。但作者強調它們都依賴 test-time parameter update(TTT 層、sliding window TTT、TTT compression),這帶來額外計算負擔且限制 real-time。對比之下 LingBot-Map 是純 feed-forward streaming,不需 test-time training 或 post-optimization,透過 compact geometric context 設計達成 real-time。這段話幾乎是在 introduction 的 claim 之外再開一個 differentiation axis:不只是「比現有 streaming 好」,而是「在 scaling 路線上選了 feed-forward 而非 TTT」,這個立場在 §6.4 ablation 中以「bounded window 反而比 full attention 在 ATE 上更好」的 counterintuitive 結果再次強化。整段 Related Work 的功能不只是 literature survey,而是逐步把 LingBot-Map 在設計光譜上的位置(end-to-end + structured context + feed-forward)精確定位出來。

### 3.4 Method (overview narrative)

(2800 words)

Method narrative 涵蓋 §3 Method 與 §4 Training & Inference,故事邏輯是「先把 streaming 表徵設計好(§3),再說明如何把它從 short-sequence 訓練 scale 到 long-sequence 並部署成 streaming 服務(§4)」。

§3.1 Overview 把問題形式化:給定影像串流 $I = \{I_1, I_2, \dots\}$,模型在每個新 frame $I_t$ 抵達時,僅依賴 $\{I_1, \dots, I_t\}$ 預測 camera pose $\hat{P}_t$ 與 depth map $\hat{D}_t$,不存取未來觀察。架構繼承 feed-forward 3D model 的 ViT backbone 加上交替的 frame-wise attention 與 GCA layer,最後接 task-specific head。這個 overview 的關鍵訊息是:GCA 是讓 streaming 變得可行的核心組件,而 anchor / pose-reference window / trajectory memory 三層 context 是 GCA 的內部結構──後續三個 subsection 就分別展開這三層。

§3.2 GCA 是整篇方法的核心。作者先重述 streaming 重建的核心 trade-off,再用 classical SLAM 的三層 spatial context 作為 prior,把 streaming state 切成三個 learned attention 機制。Anchor Context:取前 $n$ 個 frame 作為 anchor frame,在它們之間用 full attention 並加上 learnable anchor token,後續所有 frame 都以這些 anchor 為固定座標 / scale 參考;訓練時以 anchor frame 點雲到原點的平均距離 $s$ 把 ground-truth depth 與 translation 標準化到 canonical scale。Local Pose-Reference Window:維持最近 $k$ 個 frame 的完整 image token,提供 dense visual overlap 以利新 frame 註冊,並透過 §3.3 的 relative pose loss 強化 local consistency。Trajectory Memory:對於落在 anchor set 與 sliding window 之外的 frame,僅保留 camera + anchor + register 共 6 個 context token,丟棄 $M$ 個 image token,並注入 video temporal positional encoding。這節最後給出複雜度分析:per-frame context 由 $(n+k)\cdot M + 6T$ 構成,其中 $(n+k)\cdot M$ 為常數、$6T$ 線性增長,但每幀新增僅 6 tokens,相對 causal attention 的 $M+6$(典型 $M\approx 500$)減少約 80×;以 $n=3$、$k=16$、$T=10{,}000$ 計算,causal 累積約 $5\times 10^6$ tokens 而 GCA 僅約 $7\times 10^4$。Figure 3 視覺化四種 attention pattern 對比,把 GCA 的設計動機完整總結。

§3.3 GCT Framework 把三層 context 整合進完整架構並定義損失。每個 frame 的 image token 來自 DINOv2 初始化的 ViT,加上 camera token、4 個 register token、1 個 learnable anchor token,經多層 frame attention 與 GCA 交替處理,最後 camera head 與 depth head 預測 $\hat{P}_t$、$\hat{D}_t$。損失由三項組成:$L = \lambda_{\text{depth}} L_{\text{depth}} + \lambda_{\text{abs-pose}} L_{\text{abs-pose}} + \lambda_{\text{rel-pose}} L_{\text{rel-pose}}$,前兩項沿用 VGGT,但作者特意用 camera-to-world 而非 world-to-camera 參數化,理由是後者在長序列下 rotation 與 translation 強耦合導致 translation 對 rotation 誤差過於敏感。Relative pose loss 仿 $\pi^3$,在 sliding window 內所有 frame pair 上計算 geodesic rotation error 與 $\ell_1$ translation error;由於 window 只含已觀察 frame,這個 loss 天然滿足 causality。Progressive View Training 從短子序列開始、訓練中逐步增加 view 數,以避免早期 pose 誤差沿軌跡傳播導致發散。Context Parallel 採 Ulysses 策略把不同 view 分散到多 GPU、用 all-to-all 通訊計算 cross-frame attention,以解決 quadratic memory bottleneck。

§3.4 Inference System Design 把訓練好的模型部署成 streaming 系統。類比 autoregressive LLM 的 KV cache,但在 sliding window + trajectory eviction 下需要頻繁 append / discard,標準 contiguous layout 會反覆 reallocate 記憶體。作者改用 paged KV-cache(借鏡 vLLM)讓更新只影響新 append 的 token,並基於 FlashInfer 提供的 paged / sparse attention kernel;在 518 × 378、1000 frames、window 64 的設定下從 PyTorch baseline 的 10.5 FPS 提升到 20 FPS。為支援超長序列推論,額外每 $m$ frame 選一個 keyframe 保留進 KV cache。

§4 Training & Inference 把訓練拆成兩階段 curriculum。§4.1 Base Model 用 global attention 在短序列(2–24 views)、29 個資料集(包含 unordered multi-view 與 video,balanced sampling)上訓練 160K iter,建立通用 geometric prior,共耗 21,500 GPU hours。§4.2 Streaming Model 從 base model 直接接續(因為 GCA 與 global attention 共用 QKV 參數),把 view 數從 24 線性增長到 320、window size $k$ 在 16–64 間隨機抽樣,以 Ulysses parallelism dim 16、TorchTitan + Magi Attention 跑 15,360 GPU hours。§4.3 Training Data 區分 Stage 1(diverse short-sequence,nearby sampler)與 Stage 2(long-trajectory video,foldback video sampler 來避免 forward-time bias 並產生多樣 frame rate)。§4.4 Inference Modes 提供 Direct Output(預設,單一 GCA 三層 context 連續累積,在 ~3,000 frames 內穩定)與 VO mode(把序列切成重疊 window,window 內 reset 並用 Sim(3) align 接合,可處理數萬 frame 但代價是 alignment drift)。預設配置為 Direct mode、$k=64$、$m=1$、518×378、bfloat16。整段方法敘事的內在邏輯是:GCA 提供 streaming 可行性 → GCT framework 定義可訓練的目標 → 兩階段 curriculum + parallelism 提供 scaling → paged KV cache + dual mode 提供部署彈性,層層相扣為 §6 的 long-sequence、20 FPS 結果鋪好理論基礎。

### 3.5 Experiments (overview narrative)

(2500 words)

Experiments narrative 涵蓋 §5 Evaluation Benchmark 與 §6 Experiments,故事策略是「先把舞台搭好(benchmark + metric + baseline),再分三層敘述驗證:pose accuracy、reconstruction quality、ablation」,並透過 sparse / dense 雙設定把長序列當作核心戰場。

§5.1 Datasets 一次性建構五個互補的測試集,涵蓋 indoor / outdoor、object-centric / multi-scene、short / long sequence、synthetic / real 等多軸組合。Oxford Spires 是新引入的旗艦 benchmark,提供 LiDAR-inertial SLAM 取得的 ground-truth trajectory,挑選 13 個 scene,並設計兩個關鍵設定:sparse(320 frames、stride 12)落在 training 範圍內、用以與 offline / optimization-based / online 三類方法公平對比;dense(3,840 frames)則 stress-test 長序列 streaming。ETH3D、7-Scenes、Tanks and Temples、NRGBD 用於跨場景泛化驗證。§5.2 Metrics 採用標準的 AUC@3、AUC@30、ATE、RPE-trans、RPE-rot 對 pose 評估,reconstruction 則以 F1、Acc、Comp(Umeyama + ICP align)評估,並按資料集特性調整 voxel size 與 threshold。

§6.1 Baseline Methods 切成三類:offline feed-forward (VGGT、DA3、Fast3R、FastVGGT、Pi3)、optimization-based (DroidSLAM、MegaSAM、VIPE)、streaming (StreamVGGT、SLAM3R、InfiniteVGGT、Spann3R、Stream3R、CUT3R、TTT3R、Wint3R)。作者特別聲明所有 streaming 方法評測時不重置 internal state,確保公平比較長序列下的真實能力。

§6.2 Camera Pose Estimation 是論文最重要的實驗段。Sparse Oxford Spires 的結論是 LingBot-Map 在 streaming 設定下不只擊敗所有 streaming baseline,還超越最強 offline (DA3) 與 optimization-based (VIPE):AUC@15 從 DA3 的 49.84 拉到 61.64、ATE 從 12.87 / 24.78 / 10.52 (DA3 / VGGT / VIPE) 降到 6.42。作者把 offline 表現不佳歸因於訓練資料 viewpoint 數量有限、frame 距離近,在 Oxford Spires 大跳轉下 prior 失效;optimization-based 雖然顯式 minimize reprojection error 但 iterative 成本高;streaming baseline 則普遍 memory forgetting。Dense 設定(3,840 frames)是真正的 stress test:CUT3R ATE 從 18.16 飆到 32.47(+14.31)、Wint3R 從 21.10 升到 32.90(+11.80),而 LingBot-Map 從 6.42 僅升到 7.11(+0.69),序列拉長 12× 而誤差幾乎不變,直接驗證 GCA 三層 context 的長期一致性宣稱;同時 FPS 達 20.29,壓過 Wint3R(3.88)、InfiniteVGGT(7.78)、Stream3R-w(13.66)。Generalization 段把同一套敘事複製到 ETH3D、7-Scenes、Tanks and Temples,LingBot-Map 在三個資料集所有 metric 全部第一,在 Tanks and Temples 上 ATE 0.20 vs Stream3R 0.76(3.8× 改善),確立「不是 large-scale outdoor 的特化模型,而是 general-purpose streaming pose estimator」。Figure 5 提供質性對比,顯示在 outdoor-to-indoor 過渡與黑暗樓梯中 LingBot-Map 仍精準,而 DA3-Giant 與 VIPE 都 drift。

§6.3 3D Reconstruction 把 pose 改善延伸到 reconstruction 品質。ETH3D F1 從 Wint3R 的 77.28 跳到 98.98(+21.70),且 Acc(0.09 vs 0.28)與 Comp(0.03 vs 0.21)雙軸領先;7-Scenes 因 room-scale 提升空間有限,F1 80.39 仍排第一;NRGBD 上 F1 64.26 對 Wint3R 56.96 領先 7.30。Figure 6 質性圖呈現一個漸進式的對比結構:simple scene 中 baseline 還可接受、middle complexity 開始出現 duplicated structure 與 blurred surface、bottom 的 multi-building outdoor 則 baseline 完全失去 spatial coherence,而 LingBot-Map 始終保持銳利邊緣與連續 wall surface,把長序列 trajectory drift 對 reconstruction 的破壞性視覺化。

§6.4 Ablation Study 是因果鏈條的 self-validation。在 TartanAir + TartanGround、320 frames stride 8(實際 ~2,400 frames span)上以 5×10⁻⁵ fine-tune,逐項加入元件:加 Anchor Init AUC@3 從 9.80→13.63(+3.83)、加 Context Tokens 13.63→15.75(+2.12)、加 Video RoPE 7.46→5.98 ATE(−1.48,單一最大 ATE 改善)、缺 Relative Pose Loss 則 RPE-rot 從 2.26 退化到 5.35(2.4×)。這個結果序列把 §3.2 每一個設計動機都對應到一個量化貢獻。最後一個對照表把 pose-reference window size 64 與 full causal attention 比較:bounded window 速度 1.7× (20.29 vs 11.87 FPS)、記憶體 2.7× 節省(13.28 vs 36.06 GB),且 ATE 反而更低(5.98 vs 6.60),作者解釋 distant token 引入噪音、而 GCA 的 6-token 摘要保留 essential geometric cue 並濾除冗餘──這個 counterintuitive finding 是整篇論文的論證高潮:它同時顛覆「context 越多越好」的直覺,也回扣 introduction 的設計原則「不是儲存多少,而是儲存什麼」。

### 3.6 Conclusion / Limitations / Future Work

(350 words)

Conclusion 用三句話把全篇收束。第一句重申 LingBot-Map 是 streaming foundation model,核心在 GCA 把 streaming state 拆成 anchor / local pose-reference window / trajectory memory 三類 context,設計動機來自 classical SLAM 但完全 end-to-end 訓練。第二句把方法的量化承諾 anchor 在兩個數字上:per-frame context 增長量比 causal attention 減少約 80×,以及在 ~20 FPS 下穩定執行任意長序列。第三句把實驗結論定位:不只在 streaming 方法中拿到 SOTA,在 Oxford Spires 這類 large-scale dataset 上甚至超越 offline 與 optimization-based 方法,並把應用面延展到 autonomous navigation、AR、以及 embodied AI 等需要 persistent on-the-fly spatial understanding 的場景。

Limitations 三點誠實列出。其一,模型沒有 explicit loop-closure detection,意味著在重訪舊區域時 accumulated drift 仍可能存在,而 trajectory memory 是 implicit 的 drift correction;其二,trajectory memory 把每幀壓成固定 token 數,在數萬 frame 等級的超長序列下可能丟失細粒度 geometric detail──這暗示 §4.4 VO mode 雖能延展長度,但 fidelity 仍有上限;其三,作為 feed-forward 方法不做 test-time optimization,在極端挑戰場景下沒有 refinement 後手。這三點正好對應 introduction 中區隔自家方法的三條軸(no SLAM backend、compact memory、no TTT)各自留下的 trade-off。

Future Directions 把 limitations 轉成 roadmap:把 bundle-adjustment 風格的 refinement 與 explicit loop-closure 注入 attention 機制,在保持 end-to-end differentiability 前提下進一步逼近 classical SLAM backend;延伸到 dynamic scenes(處理移動物體);整合 LiDAR 或 IMU 的 multi-modal 輸入;以及把 LingBot-Map 當成 backbone 接到 novel view synthesis 或 navigation 等 downstream 任務。整段語氣保守,沒有承諾下一篇 paper,但把 LingBot-Map 從「streaming 重建模型」重新定位成「embodied 系統的空間 backbone」,呼應 conclusion 第一段對 embodied AI 的引用,讓讀者在離開時帶走「這不只是 streaming SLAM 的 learned 替代品,而是 spatial foundation model 的雛形」這個 take-away。

## 4. Critical Profile

### 4.1 Highlights

- GCA 將每幀的串流 KV 上下文從 causal attention 的 $(M+6)$ tokens 壓到 $6$ tokens($M\!\approx\!500$),長序列下增量約 $80\times$ 降幅,理論上做到「近常數」per-frame 成本(§3.2 Complexity Analysis,page 6)。
- Oxford Spires sparse(320 frames)上 AUC@15 達 $61.64$,大幅超越最強 offline DA3 的 $49.84$、最強 optimization-based VIPE 的 $45.35$、最強 online CUT3R 的 $5.98$(Table 2)。
- Oxford Spires 從 sparse 到 dense(3,840 frames),ATE 僅由 $6.42 \to 7.11$($+0.69$),而 CUT3R $+14.31$、Wint3R $+11.80$,長序列穩定性差距達一個量級(Table 3)。
- 在 ETH3D 上 F1 衝到 $98.98$,較第二名 Wint3R 的 $77.28$ 高出 $+21.70$,Acc 與 Comp 同步領先($0.09/0.03$ vs $0.28/0.21$)(Table 5)。
- 7-Scenes ATE $0.08$、Tanks and Temples ATE $0.20$、AUC@30 $92.80$,在三個風格迥異基準上同時奪冠,顯示非單一場景特化(Table 4)。
- 64-frame 的 bounded pose-reference window 反而打敗 full causal attention:ATE $5.98$ vs $6.60$,且推論速度 $1.7\times$、記憶體 $2.7\times$ 改善(Table 7),作者解讀為過遠 image tokens 反而引入雜訊。
- 端到端 ablation 把每個元件貢獻拆得乾淨:anchor 帶來 AUC@3 $+3.83$,context tokens 帶來 $+2.12$,Video RoPE 帶來 ATE $-1.48$(Table 6,page 18)。
- 工程上採用 FlashInfer 的 paged KV-cache 替代 contiguous layout,使 PyTorch baseline 從 $\sim\!10.5$ FPS 提升到 $\sim\!20$ FPS($518\!\times\!378$,1000 frames,window=64,§3.4 page 7)。
- 訓練配方完整:兩階段(各 $160$K iter)、progressive view curriculum 將 view 數從 $24$ 線性加到 $320$、Ulysses context parallelism dim=$16$,合計 $\sim\!36{,}860$ GPU hours(§4.1, §4.2)。
- NRGBD F1 達 $64.26$,較 Wint3R 的 $56.96$ 高 $+7.30$,在 cluttered 室內細節場景中漂移控制最為突出(Table 5)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 模型未內建明確的 loop-closure detection,在重訪先前區域時無法主動修正累積漂移(§7 Limitations,page 19)。
- 軌跡記憶以每幀固定 $6$ tokens 壓縮,在數萬幀級別的超長序列下可能失去對 fine-grained 幾何細節的保留能力(§7 Limitations,page 19)。
- 純 feed-forward 設計不做 test-time optimization,缺乏 bundle-adjustment 級別的後續修正機制,在 challenging 場景下重建品質仍有提升空間(§7 Limitations,page 19)。

#### 4.2.2 Phyra-inferred

- Direct mode 僅在訓練長度 $\sim\!10\times$($\sim\!3{,}000$ frames)內穩定,超過此範圍即降級;論文 abstract 與 demo 強調的「$>\!10{,}000$ frames at 20 FPS」必須切換到 VO mode,而 VO mode 在 window 邊界 Sim(3) 對齊所引入的累積漂移雖在 §4.4 page 10 文字承認,但全篇沒有任何量化曲線——核心 headline 所依賴的場景沒有對應 benchmark。
- Table 1 中 Internal Game 資料集在 Stage 1 / Stage 2 各佔 $10.6\%$ / $10.8\%$ 的取樣比重,屬於不可重現的私有資料,使得相當比例的監督訊號無法被外部讀者驗證或複製。
- 所有 ablation(Table 6, Table 7)只在 TartanAir / TartanGround 合成資料上做,序列長度約 $2{,}400$ frames;Oxford Spires 上對 DA3 多出 $\sim\!12$ AUC@15、對 CUT3R 多出 $\sim\!56$ 的巨大差距,無法乾淨地歸因到 GCA 結構,因為訓練資料分布、FlashInfer runtime、view 曲線都同時改變。
- Related Work 明確定位為 baseline 的 hybrid 方法 VGGT-SLAM [42]、MASt3R-SLAM [46] 從未出現在 Tables 2/4/5,使「outperforms iterative optimization-based approaches」的主張其實只在 DroidSLAM/MegaSAM/VIPE 上成立。
- 軌跡記憶每幀保留 $6$ tokens(camera + anchor + $4$ register)從未做敏感度實驗——讀者無法判斷 $3$、$12$、$24$ tokens 是否會帶來更佳折衷,$6$ 是設計選擇而非實證最優。
- Anchor frames 直接取前 $n$ 幀且全程不可重選;若起手幀為低紋理、運動模糊、或 baseline 不足,整段軌跡都繼承壞的座標基準,但論文無針對 anchor 品質劣化的 robustness 實驗。
- $20$ FPS 的數字只在 $518\!\times\!378$、window=$64$ 的單一 setting 量測(§3.4),沒有 resolution、window size、batch 的 sweep;讀者無從推斷在 $1024$-frame window 或更高解析度下 $(n+k)\cdot M$ 主導項是否仍能維持即時性。

### 4.3 Phyra's Judgment (summary)

真正的新意是把經典 SLAM 的「reference / local window / global map」三層結構轉譯成一個學習式 attention mask,並把軌跡記憶壓到每幀 $6$ tokens,這個設計確實同時拿到長序列一致性與近常數 per-frame 成本。其餘大半屬於紮實工程:FlashInfer paged KV、Ulysses context parallelism、progressive view curriculum、相對位姿損失——重要但非概念性突破。最未解的核心問題是長序列優勢究竟來自 GCA 結構,還是來自 stage 2 大幅加重的長軌跡資料(包含 $10\%$ 不可重現的 Internal Game)與更深的預訓練;ablation 都在 TartanGround 合成資料上做,從未把這個變因拆乾淨,而 headline 的 $10{,}000$-frame 場景所依賴的 VO mode 漂移又完全沒被量化。

## 5. Methodology Deep Dive

### 5.1 Method Overview

LingBot-Map 的核心是 **Geometric Context Transformer (GCT)**，建立於 VGGT 的 ViT backbone（DINOv2 初始化）與交替的 frame attention / cross-frame attention 架構之上，但將 cross-frame attention 替換為 **Geometric Context Attention (GCA)**。GCA 將串流上下文顯式分解為三類互補的注意力子集：(1) **Anchor Context** — 前 $n$ 幀（通常 $n=3$）的完整 image tokens 加 learnable anchor token，建立座標系與絕對尺度，所有後續幀對其做 full attention 作為固定參照；(2) **Local Pose-Reference Window** — 最近 $k$ 幀（訓練時 $k \in [16, 64]$，預設推論 $k=64$）的完整 image tokens（每幀 $M+6$ tokens），提供稠密視覺重疊以支援局部相對位姿估計；(3) **Trajectory Memory** — 對視窗外的歷史幀僅保留 6 個 context tokens（1 camera + 4 register + 1 anchor），丟棄佔記憶體大宗的 image tokens，並注入 video temporal positional encoding 以維持時序順序，提供長距離漂移修正線索。

複雜度上，causal attention 每幀新增 $(M+6)$ tokens，T 幀總量為 $T \cdot (M+6) = MT + 6T$；GCA 每幀僅新增 6 個 trajectory tokens，總量為 $(n+k)\cdot M + 6T$，第一項為常數，第二項以每幀 6 tokens 線性成長。論文於第 6 頁給出具體例子：當 $n=3, k=16, T=10{,}000, M\approx 500$ 時，causal attention 累積 $\sim 5\times 10^6$ tokens，GCA 僅 $\sim 7\times 10^4$ tokens，每幀成長率降低約 80×，使 518×378 解析度、超過 10,000 幀的長序列得以以約 20 FPS 穩定推論。

訓練採兩階段策略：**Stage 1 (Base Model)** 使用標準 global attention 在 2–24 幀的多視角與短視訊資料上訓練 160K iterations（21,500 GPU hours），建立通用幾何先驗；**Stage 2 (Streaming Model)** 將 global attention 替換為 GCA（QKV 投影參數可直接遷移），以 progressive view curriculum 將訓練幀數從 24 線性增加至 320（受 context parallelism 之 GPU 記憶體上限限制），$k$ 在 $[16, 64]$ 隨機採樣，並透過 Ulysses context parallelism (parallelism dim=16) 分散注意力計算，再訓練 160K iterations（15,360 GPU hours）。Loss 為 $\mathcal{L} = \lambda_{\text{depth}} \mathcal{L}_{\text{depth}} + \lambda_{\text{abs-pose}} \mathcal{L}_{\text{abs-pose}} + \lambda_{\text{rel-pose}} \mathcal{L}_{\text{rel-pose}}$，其中相對位姿損失（受 π³ 啟發）僅在 sliding window 內所有 frame pairs 上計算，天然滿足 causal 約束。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: video frames T_1, ..., T_i ∈ R^{H×W×3}, H=378, W=518, patch=14
   │
   │ [B, 3, H, W] per frame → DINOv2 ViT backbone (per-frame, frame attention)
   ▼
Image Tokens per frame:           [B, M, C]              (M = (H/14)×(W/14) ≈ 27×37 ≈ 999, paper uses M≈500 for default config; C = ?)
   │
   │ Augment with learnable tokens (per frame)
   ▼
Augmented Token Set per frame:    [B, M+6, C]
   │   ├─ image tokens:           [B, M, C]
   │   ├─ camera token c:         [B, 1, C]
   │   ├─ register tokens r_1..4: [B, 4, C]
   │   └─ anchor token a:         [B, 1, C]
   │
   │ Stack all frames in streaming KV-cache (paged layout, FlashInfer)
   ▼
Streaming Context for current frame T_i:
   │
   ├─→ Anchor Context             [B, n·(M+6), C]   (n=3, full image tokens, fixed reference)
   ├─→ Local Pose-Reference Win.  [B, k·(M+6), C]   (k=64 default, recent frames T_{i-k}..T_{i-1})
   ├─→ Trajectory Memory          [B, (i-n-k)·6, C] (only c, r_1..4, a per evicted frame, +temporal PE)
   └─→ Current Frame T_i tokens   [B, M+6, C]       (Q source for cross-frame attention)
   │
   │ 24 alternating blocks (initialized from VGGT base):
   │   ├─ Frame Attention: per-frame self-attention over [B, M+6, C]
   │   └─ Geometric Context Attention (GCA):
   │       Q from current frame [B, M+6, C]
   │       K,V from concat(Anchor ∪ Local Window ∪ Trajectory Memory ∪ Current)
   │       structured attention mask (Fig. 3d) restricts visibility
   ▼
Refined Tokens for T_i:           [B, M+6, C]
   │
   ├─→ Camera Token [B, 1, C] ──→ Camera Head ──→ P̂_i ∈ R^{B, 7 or 4×4}  (camera-to-world; rotation+translation)
   │
   └─→ Image Tokens [B, M, C] ──→ DPT-style Depth Head ──→ D̂_i ∈ R^{B, H, W}  + uncertainty Σ^D_i ∈ R^{B, H, W}

Notes on `?`:
  • Channel dim C and exact M not stated in the provided method excerpt; M depends on patch grid (≈ 27×37 = 999 tokens for 518×378 with patch=14, but the complexity analysis on p.6 uses M≈500 as a "typical value", suggesting either token reduction or a different effective count). The paper does not specify C explicitly in the excerpt.
  • Number of register tokens fixed at 4; anchor and camera tokens are 1 each, giving 6 context tokens per frame (matches paper).
```

### 5.3 Per-Module Breakdown

#### 5.3.1 ViT Backbone (DINOv2-initialized)

**Function:** 將每張輸入影像獨立編碼為 image tokens 序列，提供強幾何先驗的視覺表徵。

**Input:**
- Name: `T_i`（當前幀影像）
- Shape: `[B, 3, H, W]`，其中 $H=378$, $W=518$
- Source: 輸入視訊串流的當前幀

**Output:**
- Name: `image_tokens_i`
- Shape: `[B, M, C]`，其中 $M$ 為 patch grid 大小（patch_size=14，理論上 $M = \lfloor H/14 \rfloor \times \lfloor W/14 \rfloor = 27 \times 37 = 999$，但論文 §3.2 複雜度分析使用 $M \approx 500$ 作為「typical value」），$C$ 為通道數（論文未明確指定）
- Consumer: Token Augmentation 模組（§5.3.2）

**Processing:**
1. 將 $H \times W$ 影像切為 14×14 patches。
2. 每個 patch 經 ViT 線性投影至 $C$ 維 token。
3. 加上 positional encoding，經 24 個 transformer blocks 處理（與 VGGT 對齊）。

**Key Formulas:**

每幀獨立編碼，無跨幀互動：
$$
\text{image\_tokens}_i = \text{ViT}_{\text{DINOv2}}(T_i)
$$

**Implementation Details:**

ViT backbone 從 DINOv2 (Oquab et al.) 初始化，patch size = 14 pixels。輸入解析度標準化為最大邊 518 pixels（保持 aspect ratio）。Stage 1 訓練時的 photometric augmentation 包括 brightness/contrast/saturation ±0.5、hue ±0.1（probability 0.9），random grayscale (p=0.05)，spatial rescaling [0.8×, 1.2×]，aspect ratio [0.33, 1.0]。Co-jittering（同一場景所有幀套用相同色彩變換）以 p=0.3 啟用。

#### 5.3.2 Token Augmentation

**Function:** 為每幀的 image tokens 附加 6 個 learnable context tokens（camera, register×4, anchor），承載跨幀幾何資訊與壓縮表徵。

**Input:**
- Name: `image_tokens_i`
- Shape: `[B, M, C]`
- Source: ViT Backbone (§5.3.1)

**Output:**
- Name: `augmented_tokens_i`
- Shape: `[B, M+6, C]`
- Consumer: Frame Attention / GCA blocks（§5.3.3, §5.3.4）

**Processing:**

對每幀拼接 6 個 learnable tokens：
1. 1 個 camera token $c \in \mathbb{R}^C$
2. 4 個 register tokens $r_1, r_2, r_3, r_4 \in \mathbb{R}^C$
3. 1 個 learnable anchor token $a \in \mathbb{R}^C$

Anchor token 用於讓網路識別並區分 anchor frames 與後續 streaming frames。

**Key Formulas:**

$$
\text{augmented\_tokens}_i = [c; r_1; r_2; r_3; r_4; a; \text{image\_tokens}_i] \in \mathbb{R}^{B \times (M+6) \times C}
$$

**Implementation Details:**

所有 6 個 context tokens 為 learnable parameters。論文未指定 $C$ 的具體數值。Trajectory Memory 對 evicted frames 僅保留這 6 個 context tokens，丟棄 image tokens，這是 GCA 達成近常數每幀記憶體成長的關鍵。

#### 5.3.3 Frame Attention

**Function:** 在每幀內部執行 self-attention，refine 該幀的 token 表徵，不涉及跨幀資訊。

**Input:**
- Name: `augmented_tokens_i`
- Shape: `[B, M+6, C]`
- Source: Token Augmentation（首次）或前一個 GCA block（後續）

**Output:**
- Name: `frame_refined_tokens_i`
- Shape: `[B, M+6, C]`
- Consumer: 同層的 GCA block

**Processing:**

對每幀獨立執行 multi-head self-attention：
$$
\text{frame\_refined}_i = \text{MHSA}(\text{augmented\_tokens}_i)
$$
Q, K, V 皆來自同一幀的 $M+6$ tokens。

**Implementation Details:**

與 VGGT 的 frame attention 設計一致。Frame Attention 與 GCA 在 24 個 blocks 中交替排列。

#### 5.3.4 Geometric Context Attention (GCA)

**Function:** GCA 為本論文核心創新，以結構化 attention mask 將跨幀注意力分為 anchor、local window、trajectory memory 三類互補上下文，取代 VGGT 的 global cross-frame attention，使每幀計算與記憶體開銷近乎常數。

**Input:**
- Name: 當前幀 query tokens `Q_i`，以及上下文集合 `KV_context`
- Shape:
  - `Q_i`: `[B, M+6, C]`（來自 Frame Attention 輸出）
  - `KV_context`: 由四部分串接：
    - Anchor: `[B, n·(M+6), C]`，$n=3$
    - Local Window: `[B, k·(M+6), C]`，$k \in [16, 64]$，預設 $k=64$
    - Trajectory Memory: `[B, (i-n-k)·6, C]`（若 $i > n+k$）
    - Current frame self: `[B, M+6, C]`
- Source: Anchor frames（初始化階段保留）、KV-cache、當前 Frame Attention 輸出

**Output:**
- Name: `gca_output_i`
- Shape: `[B, M+6, C]`
- Consumer: 下一層 Frame Attention，或最終輸出至 prediction heads

**Processing:**

1. 從 KV-cache（FlashInfer paged layout）讀取 anchor、local window、trajectory memory 的 tokens。
2. 將四部分串接為 K, V：
   $$
   K = V = \text{concat}(\text{Anchor}, \text{LocalWin}, \text{TrajMem}, \text{Current}_i)
   $$
3. 套用結構化 attention mask（Fig. 3d）：當前幀 attend 到 anchor 全 tokens、最近 $k$ 幀全 tokens、所有更早幀的 6 個 context tokens。
4. 計算 multi-head attention：
   $$
   \text{gca\_output}_i = \text{softmax}\left(\frac{Q_i K^\top}{\sqrt{d_k}} \odot \text{mask}\right) V
   $$
5. 對於 anchor frames（前 $n$ 幀）內部，套用 full attention（彼此互相 attend），其餘幀對 anchor 為 read-only。

**Key Formulas:**

每幀注意力上下文 token 總數：
$$
N_{\text{GCA}} = n \cdot (M+6) + k \cdot (M+6) + (T - n - k) \cdot 6 = (n+k) \cdot M + 6T
$$

對比 causal attention：
$$
N_{\text{causal}} = T \cdot (M+6) = MT + 6T
$$

新增單幀 token 比較：causal 為 $(M+6)$，GCA 為 $6$，比例約為 $(M+6)/6 \approx 84$（當 $M=500$），論文表述為「reduced by roughly 80×」。

**Implementation Details:**

- Anchor frames 數 $n=3$（論文 §3.2 預設）。
- Local window size $k$：訓練時隨機採樣自 $[16, 64]$，預設推論 $k=64$（§4.4）。
- Trajectory Memory 的 6 tokens（1 camera + 4 register + 1 anchor，無 image tokens）注入 video temporal positional encoding（引用 [72]）以維持時序順序。
- 推論時實作於 FlashInfer，採 paged KV-cache layout 避免 contiguous re-allocation overhead。
- Stage 2 訓練從 base model 權重初始化，QKV projections 參數可直接遷移（GCA 與 global attention 的參數化相同），加速收斂。
- 24 個 blocks 中 Frame Attention 與 GCA 交替排列（與 VGGT 一致）。

#### 5.3.5 Camera Head

**Function:** 從 GCA 處理後的 camera token 預測當前幀的絕對相機位姿（camera-to-world transformation）。

**Input:**
- Name: `camera_token_i`
- Shape: `[B, 1, C]`（從 `gca_output_i` 提取第 0 個 token）
- Source: 最終 GCA block 的輸出

**Output:**
- Name: `P̂_i`
- Shape: `[B, ?]`，論文未明確指定具體參數化（典型為 7-dim quaternion+translation 或 4×4 matrix）
- Consumer: Loss 計算 / 下游應用

**Processing:**

Camera Head 將 camera token 映射至位姿參數。論文採用 **camera-to-world** 參數化（與 VGGT 的 world-to-camera 不同），原因為 world-to-camera 中 rotation 與 translation 耦合，translation 對 rotation error 高度敏感，特別在長序列下會放大誤差。

**Key Formulas:**

絕對位姿損失（沿用 VGGT [75]）：
$$
\mathcal{L}_{\text{abs-pose}} = \sum_{i=1}^{N} \|\hat{P}_i - P_i\|_\epsilon
$$

**Implementation Details:**

具體 head 架構（MLP 層數、輸出維度）論文未明確說明。參數化選擇 camera-to-world 是相對 VGGT 的改動。

#### 5.3.6 Depth Head (DPT-style)

**Function:** 從 GCA 處理後的 image tokens 預測當前幀的稠密深度圖與不確定性圖。

**Input:**
- Name: `image_tokens_i_refined`
- Shape: `[B, M, C]`（從 `gca_output_i` 提取後 $M$ 個 tokens）
- Source: 最終 GCA block 的輸出

**Output:**
- Name: `D̂_i`, `Σ^D_i`
- Shape: `D̂_i: [B, H, W]`，`Σ^D_i: [B, H, W]`，其中 $H=378, W=518$
- Consumer: Loss 計算 / 點雲重建

**Processing:**

採 DPT-style 架構（如圖 4 所示，標記為 "DPT" 與 "Dc"），將 token grid 上採樣回原始解析度，輸出深度與 per-pixel uncertainty。

**Key Formulas:**

深度損失（沿用 VGGT [75]）：
$$
\mathcal{L}_{\text{depth}} = \sum_{i=1}^{N}\left[ \|\Sigma^D_i \odot (\hat{D}_i - D_i)\|_\epsilon + \|\Sigma^D_i \odot (\nabla \hat{D}_i - \nabla D_i)\|_\epsilon - \alpha \log \Sigma^D_i \right]
$$

其中 $\Sigma^D_i$ 為預測 uncertainty map，$\odot$ 為 element-wise 乘法，$\nabla$ 為深度梯度，$\alpha$ 為 uncertainty 正則項權重。

**Implementation Details:**

DPT-style decoder 具體層數論文未列出。Loss 同時懲罰深度值與深度梯度誤差，並透過 uncertainty re-weighting 提升對 textureless 與遮擋區域的 robustness。

#### 5.3.7 Relative Pose Loss (Training-only)

**Function:** 在 sliding window 內所有 frame pairs 上計算相對位姿損失，鼓勵局部軌跡一致性。受 π³ [83] 啟發。

**Input:**
- Name: window 內所有預測位姿 $\{\hat{P}_i\}_{i=1}^{k}$
- Shape: per-pose 同 §5.3.5
- Source: Camera Head 對 window 內 $k$ 幀的輸出

**Output:**
- Name: 純量損失 $\mathcal{L}_{\text{rel-pose}}$
- Shape: scalar
- Consumer: 加權至總 loss

**Processing:**

對 window 內所有 $i \neq j$ 的 frame pairs 計算相對位姿，分別計算 rotation 的 geodesic error 與 translation 的 $\ell_1$ error。

**Key Formulas:**

$$
\mathcal{L}_{\text{rel-pose}} = \frac{1}{k(k-1)} \sum_{\substack{i \neq j \\ i,j \in \{1,\ldots,k\}}} \left[ \mathcal{L}_{\text{rot}}(i,j) + \lambda_{\text{trans}} \mathcal{L}_{\text{trans}}(i,j) \right]
$$

其中 $\mathcal{L}_{\text{rot}}(i,j)$ 為相對 rotation 的 geodesic error，$\mathcal{L}_{\text{trans}}(i,j)$ 為相對 translation 的 $\ell_1$ error。

**Implementation Details:**

由於 window 僅包含已觀測幀，此損失天然滿足 causal 約束。$\lambda_{\text{trans}}$ 具體數值論文未指定。此 loss 為訓練時加入，推論時不參與。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| BlendedMVS | Multi-view 3D 重建訓練 | Multi-view, single-scene | Train (Stage 1: 1.1%, Stage 2: 1.9%) |
| HyperSim | Multi-view 室內合成 | Multi-view, single-scene | Train (Stage 1: 5.8%, Stage 2: 5.7%) |
| MegaDepth | Multi-view 深度估計 | Multi-view, multi-scene | Train (Stage 1: 3.9%) |
| Unreal4K | Video 合成場景 | Video, single-scene | Train (Stage 1: 1.0%, Stage 2: 0.9%) |
| WildRGBD | Video 物件中心 | Video, single-scene | Train (Stage 1: 5.8%, Stage 2: 1.9%) |
| TartanAir | Video 多場景軌跡 | Video, multi-scene | Train (Stage 1: 3.9%, Stage 2: 7.6%); Ablation testbed |
| TartanAirV2 | Video 多場景軌跡 | Video, multi-scene | Train (Stage 1: 5.8%, Stage 2: 10.8%) |
| TartanGround | Video 地面機器人軌跡 | Video, multi-scene | Train (Stage 1: 5.8%, Stage 2: 10.8%); Ablation validation set (320 frames @ stride 8) |
| Waymo | Video 戶外駕駛 | Video, multi-scene | Train (Stage 2: 0.9%) |
| PointOdyssey | Video 動態場景 | Video, single-scene | Train (Stage 1: 0.3%, Stage 2: 0.9%) |
| VirtualKITTI | Video 戶外駕駛合成 | Video, multi-scene | Train (Stage 1: 0.8%, Stage 2: 1.9%) |
| Kubric | Video 合成 | Video, single-scene | Train (Stage 1: 0.3%, Stage 2: 0.9%) |
| DL3DV | Video 多場景 | Video, multi-scene | Train (Stage 1: 11.0%, Stage 2: 5.7%) |
| MVS-Synth | Multi-view 合成 | Multi-view, single-scene | Train (Stage 1: 1.7%) |
| GTA-SFM | Multi-view SfM 合成 | Multi-view, single-scene | Train (Stage 1: 1.7%) |
| CO3D | Multi-view 物件 | Multi-view, single-scene | Train (Stage 1: 5.5%) |
| SceneRGBD | Video 室內合成 | Video, single-scene | Train (Stage 1: 7.3%, Stage 2: 5.7%) |
| Mapfree | Video 重定位 | Video, multi-scene | Train (Stage 1: 3.9%, Stage 2: 1.5%) |
| Aria Synthetic Environments | Video egocentric 合成 | Video, single-scene | Train (Stage 1: 7.3%, Stage 2: 5.7%) |
| ADT (Aria Digital Twin) | Video egocentric | Video, single-scene | Train (Stage 1: 1.0%) |
| Objaverse | Mesh 物件 | Mesh, single-scene | Train (Stage 1: 2.7%) |
| Texverse | Mesh 物件 | Mesh, single-scene | Train (Stage 1: 2.7%) |
| ScanNet++ | Video 室內 | Video, single-scene | Train (Stage 1: 3.9%, Stage 2: 2.8%) |
| ScanNet | Video 室內 | Video, single-scene | Train (Stage 1: 1.9%, Stage 2: 2.8%) |
| MatrixCity | Video 城市規模 | Video, multi-scene | Train (Stage 1: 1.7%, Stage 2: 7.6%) |
| MidAir | Video 空拍合成 | Video, multi-scene | Train (Stage 1: 2.9%, Stage 2: 5.7%) |
| KITTI-360 | Video 戶外駕駛 | Video, multi-scene | Train (Stage 2: 3.8%) |
| Internal Game | Video 多場景遊戲 | Video, multi-scene | Train (Stage 1: 10.6%, Stage 2: 10.8%) |
| Gibson | Mesh 室內導航 | Mesh, multi-scene | Train (Stage 2: 2.6%) |
| Matterport3D | Mesh 室內 | Mesh, multi-scene | Train (Stage 2: 2.6%) |
| HM3D | Mesh 室內 | Mesh, multi-scene | Train (Stage 2: 2.6%) |
| Oxford Spires | Camera pose + 3D 重建（戶外大規模） | 13 scenes;  sparse 320 frames、dense 3,840 frames | Test |
| ETH3D | Camera pose + 3D 重建（室內外混合） | 全部 frames | Test |
| 7-Scenes | Camera pose + 3D 重建（室內 RGB-D） | 7 scenes, stride 5 下採樣 | Test |
| Tanks and Temples | Camera pose 估計（戶外多視角） | 6 scenes (Barn, Caterpillar, Church, Ignatius, Meeting Room, Truck) | Test |
| NRGBD | 3D 重建（室內 RGB-D） | stride 5 下採樣 | Test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| AUC@3 / AUC@15 / AUC@30 | 相對 pose error 在 $3°$、$15°$、$30°$ 角度閾值下的 Area Under the Curve，衡量 pose 估計準確度 | yes |
| ATE (m) | Absolute Trajectory Error，經 Sim(3) 對齊後的全域軌跡一致性誤差 | yes |
| RPE-trans | Relative Pose Error（translation），衡量 frame-to-frame 局部平移精度 | no |
| RPE-rot | Relative Pose Error（rotation），衡量 frame-to-frame 局部旋轉精度 | no |
| F1 | 重建點雲與 ground-truth 之 F1 score（ETH3D 用 $d=0.1$ m 或 $0.25$、voxel $0.039$ m；7-Scenes 與 NRGBD 用 voxel $4.0/512$、$F_1$ threshold $0.05$） | yes |
| Acc | Accuracy，重建點雲到 ground-truth 之距離 | no |
| Comp | Completeness，ground-truth 點雲到重建點雲之距離 | no |
| FPS | 每秒處理幀數，衡量推論速度 | no |
| Memory (GB) | GPU 記憶體佔用量 | no |

### 6.3 Training and Inference Settings

訓練分為兩階段。**Stage 1（base model）**: ViT backbone 從 DINOv2 初始化（patch size 14），採 24 層交替的 frame attention 與 cross-frame attention（架構同 VGGT），全程使用 global attention 而非 GCA；optimizer 為 AdamW（base lr $2 \times 10^{-4}$、weight decay $0.05$），lr schedule 為前 5% 從 $10^{-8}$ 線性 warmup 至 base，後 95% cosine annealing 回 $10^{-8}$；訓練 160K iterations；每樣本隨機抽 2–24 views，dynamic batch sampler 每 GPU 最多 48 images。資料增強包含色彩抖動（brightness/contrast/saturation $\pm 0.5$、hue $\pm 0.1$，機率 0.9）、隨機灰階（機率 0.05）、空間 rescale ($[0.8\times, 1.2\times]$，aspect ratio $[0.33, 1.0]$)、co-jittering（機率 0.3）。分散式訓練採 FSDP + gradient checkpointing + bfloat16 mixed precision，總計約 21,500 GPU hours。

**Stage 2（streaming model）**: 從 base model 權重初始化，將 global attention 替換為 GCA；訓練 160K iterations，base lr $5 \times 10^{-4}$，warmup 與 cosine schedule 同 Stage 1；views 數採 progressive curriculum 從 24 線性增至 320；local pose-reference window $k$ 訓練時隨機從 $[16, 64]$ 抽樣。採用 Ulysses context-parallelism（並行維度 16），實作於 TorchTitan + Magi Attention，總計約 15,360 GPU hours。Loss 為 $L = \lambda_{\text{depth}} L_{\text{depth}} + \lambda_{\text{abs-pose}} L_{\text{abs-pose}} + \lambda_{\text{rel-pose}} L_{\text{rel-pose}}$，其中 $L_{\text{rel-pose}}$ 對 sliding window 內所有 frame pair 計算 geodesic rotation error 與 $\ell_1$ translation error；具體 $\lambda$ 數值 the paper does not specify。

**Ablation 設定**: 從 Stage 1 checkpoint 微調，lr $5 \times 10^{-5}$，progressive view curriculum 同主訓練，每組 ablation 約 3,840 GPU hours，於 TartanGround validation set（320 frames @ stride 8，時間跨度約 2,400 frames）評估。

**Inference**: 預設 Direct Output Mode，$k = 64$、keyframe interval $m = 1$、解析度 $518 \times 378$、bfloat16；KV-cache 採用 paged layout（基於 FlashInfer），於 1000 frames、window 64 設定下達 ~20 FPS（PyTorch contiguous baseline 為 ~10.5 FPS）。VO Mode 用於極長序列（數萬 frames），以 overlapping windows + 視窗間 Sim(3) 對齊。Direct mode 在 keyframe selection 下可穩定處理約 10× 訓練長度（~3,000 frames）。

### 6.4 Main Results

**Oxford Spires (sparse, 320 frames):**

| Method | Type | AUC@15 ↑ | AUC@30 ↑ | ATE ↓ | Notes |
| --- | --- | --- | --- | --- | --- |
| Fast3R | offline | 1.20 | 2.99 | 34.80 | |
| VGGT | offline | 23.84 | 35.09 | 24.78 | |
| DA3 | offline | 49.84 | 56.68 | 12.87 | 最強 offline baseline |
| Pi3 | offline | 38.64 | 48.65 | 14.03 | |
| DroidSLAM | optim | 8.58 | 21.41 | 21.84 | |
| MegaSAM | optim | 15.91 | 28.03 | 13.80 | |
| VIPE | optim | 45.35 | 51.88 | 10.52 | 最強 optim baseline |
| CUT3R | online | 5.98 | 14.95 | 18.16 | 最佳 online competitor |
| TTT3R | online | 13.92 | 25.90 | 19.35 | |
| Wint3R | online | 11.61 | 23.42 | 21.10 | |
| Stream3R | online | 9.67 | 15.21 | 29.58 | |
| **LingBot-Map (Ours)** | **online** | **61.64** | **75.16** | **6.42** | 較 DA3 提升 +11.80 AUC@15、ATE 降 50%；較 CUT3R AUC 提升 ~10× |

**Oxford Spires (dense, 3,840 frames):**

| Method | ATEsparse ↓ | ATEdense ↓ | $\Delta$ ATE | FPS ↑ |
| --- | --- | --- | --- | --- |
| CUT3R | 18.16 | 32.47 | +14.31 | 29.21 |
| TTT3R | 19.35 | 25.05 | +5.70 | 28.97 |
| Wint3R | 21.10 | 32.90 | +11.80 | 3.88 |
| InfiniteVGGT | 30.49 | 31.75 | +1.26 | 7.78 |
| Stream3R-w | 33.03 | 33.73 | +0.70 | 13.66 |
| **LingBot-Map (Ours)** | **6.42** | **7.11** | **+0.69** | **20.29** |

**ETH3D / 7-Scenes / Tanks & Temples (camera pose):**

| Method | ETH3D AUC@30 ↑ | ETH3D ATE ↓ | 7-Scenes AUC@30 ↑ | 7-Scenes ATE ↓ | T&T AUC@30 ↑ | T&T ATE ↓ |
| --- | --- | --- | --- | --- | --- | --- |
| Stream3R | 64.76 | 1.67 | 73.70 | 0.10 | 81.33 | 0.76 |
| Wint3R | 58.71 | 0.86 | 63.02 | 0.12 | 57.85 | 0.88 |
| TTT3R | 56.12 | 1.22 | 71.23 | 0.10 | 71.30 | 0.66 |
| InfiniteVGGT | 62.20 | 1.46 | 73.40 | 0.12 | 77.76 | 1.00 |
| **LingBot-Map (Ours)** | **86.20** | **0.22** | **78.59** | **0.08** | **92.80** | **0.20** |

**ETH3D / 7-Scenes / NRGBD (3D reconstruction F1):**

| Method | ETH3D F1 ↑ | 7-Scenes F1 ↑ | NRGBD F1 ↑ |
| --- | --- | --- | --- |
| StreamVGGT | 58.11 | 69.44 | 45.08 |
| CUT3R | 67.63 | 58.98 | 32.22 |
| TTT3R | 68.48 | 77.25 | 53.55 |
| Wint3R | 77.28 | 78.81 | 56.96 |
| Stream3R | 72.87 | 78.79 | 54.07 |
| **LingBot-Map (Ours)** | **98.98** | **80.39** | **64.26** |

### 6.5 Ablation Studies

論文以 Tab. 6 進行四組元件 ablation（baseline 為僅含 relative pose loss 的 row 1），於 TartanGround 驗證集評估。

- **Anchor Initialization (row 1 → row 2)**: 加入 anchor frames 與 learnable anchor token，AUC@3 從 9.80 → 13.63（+3.83）、ATE 從 8.59 → 7.88。此 ablation 直接診斷 GCA 的「coordinate/scale grounding」角色，回答了「monocular streaming 是否需要顯式 reference frame」的問題，屬於診斷型實驗。
- **Context Tokens / Trajectory Memory (row 2 → row 4)**: 在 anchor 之上加入 6-token per-frame compact memory，AUC@3 從 13.63 → 15.75（+2.12）、ATE 從 7.88 → 7.46（−0.42）。直接驗證「lightweight trajectory memory 是否能對抗 long-range drift」，屬診斷型。
- **Relative Pose Loss (row 3 vs row 4)**: 移除 $L_{\text{rel-pose}}$ 後 RPE-rot 由 2.26 → 5.35（2.4× 惡化）、ATE 由 7.46 → 8.25。這個對照特別揭示 rotation 比 translation 對 pairwise 監督更敏感，屬於有資訊量的診斷實驗。
- **Video RoPE (row 4 → row 5)**: 加入 video temporal positional encoding，ATE 由 7.46 → 5.98（−1.48，整組 ablation 中最大單一改善）、AUC@3 +0.64、AUC@30 +1.95。此 ablation 回答「trajectory memory 是否需要時序順序」，是核心診斷而非 sanity check。
- **Pose-Reference Window vs Full Causal Attention (Tab. 7)**: $k = 64$ 對比保留所有歷史 image tokens 的 full causal attention。bounded window 在 ATE (5.98 vs 6.60)、RPE-trans (1.33 vs 1.50)、FPS（20.29 vs 11.87，1.7×）、memory（13.28 vs 36.06 GB，2.7×）皆勝出，僅 RPE-rot (1.93 vs 1.71) 略遜。此實驗同時量化效能與精度權衡，並佐證「過多歷史 image tokens 會引入噪音」的設計假設，屬有效診斷。

整體而言，五組 ablation 都對應 GCA 的具體設計選擇（anchor、memory、relative loss、temporal RoPE、bounded window），每組都改變 metric 並提供方向性洞察，沒有出現純 sanity check（例如「移除整個模型」之類的退化對照）。較弱之處是：缺少對 anchor 數量 $n$、window 大小 $k$、keyframe interval $m$ 的 sweep（僅在 Tab. 7 比較 $k=64$ 與 full），亦未對 trajectory memory 的 token 數（固定為 6）做敏感度分析。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 比較對象包含 offline SoTA（VGGT, DA3, Pi3）、optim SoTA（VIPE, MegaSAM, DroidSLAM）與 streaming SoTA（CUT3R, TTT3R, Wint3R, Stream3R, InfiniteVGGT, StreamVGGT, SLAM3R），多為 2025–2026 近期工作。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時評估 camera pose（Oxford Spires, ETH3D, 7-Scenes, Tanks & Temples）與 3D reconstruction（ETH3D, 7-Scenes, NRGBD），跨室內/戶外、短/長序列。
- [covered] Has ablations that diagnose the new components (not just sanity checks) — Tab. 6 與 Tab. 7 對 anchor、context tokens、relative loss、video RoPE、bounded window 五個 GCA 元件分別作對照，每組都對應特定設計假設並產生方向性 metric 變化。
- [partial] Has a scaling study (size, length, or compute) — Tab. 3 透過 sparse(320) vs dense(3,840) 評估 12× sequence length scaling 並與 baselines 比較 $\Delta$ ATE，正文亦聲稱可外推至 ~10,000 frames；但缺少模型尺寸或訓練 compute 的 scaling curve。
- [covered] Has an efficiency / wall-clock comparison — Tab. 3 報告 FPS（LingBot-Map 20.29 vs 競品 3.88–29.21），Tab. 7 額外比較 FPS 與 GPU memory（13.28 vs 36.06 GB），Sec. 3.4 對比 FlashInfer paged 與 PyTorch contiguous KV-cache（20 vs 10.5 FPS）。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有表格皆為單次數值，未報告 std、信賴區間或多 seed 平均。
- [covered] Releases code / weights / data sufficient for reproducibility — 論文首頁列出 GitHub (https://github.com/robbyant/lingbot-map) 與專案網站，附錄詳列 29 個訓練資料集與抽樣比例、optimizer/lr/iteration、context-parallel 設定、推論 hyperparameter，對重現具備充分文件層級的揭露（實際 release 內容需檢視 repo 才能確認）。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: GCA 三層上下文(anchor + window + trajectory memory)以近常數 per-frame 成本維持長序列一致性。** *Supported.* 複雜度推導(§3.2 page 6)+ Table 3 上 sparse→dense ATE 僅 $+0.69$ + Table 7 上 bounded window 同時優於 full causal 的 ATE 與速度,共同證實架構主張。
- **Claim 2: Progressive training + context parallelism + relative pose loss 是穩定長序列訓練的有效配方。** *Partially supported.* Table 6 拆解了 Rel. Loss、Anchor Init、Context Tokens、Video RoPE 各自的貢獻,但只在 TartanGround 上做;對 progressive curriculum 本身與 Ulysses dim 的選擇沒有對照組,讀者無法判斷其中哪個元件是必要的、哪個只是加速收斂。
- **Claim 3: 在 Oxford Spires、T&T、ETH3D、7-Scenes 上全面超越既有 streaming 方法。** *Supported.* Tables 2/4/5 在所有列出的 streaming baselines 上皆領先,且差距遠大於度量噪聲。
- **Claim 4: 同時超越 offline 與 iterative optimization-based 方法。** *Partially supported / overclaimed.* 在 Oxford Spires sparse(Table 2)上確實打敗 DA3、Pi3、VGGT 與 DroidSLAM/MegaSAM/VIPE;但 Related Work 點名的 hybrid 派 VGGT-SLAM、MASt3R-SLAM 完全沒進表,且 offline 方法本身並非為 $320$+ frames 訓練,比較條件對 LingBot-Map 有利這點作者只當成優勢敘述而未充分加註。
- **Claim 5: $\sim\!20$ FPS 在超過 $10{,}000$ frames 序列上穩定推論。** *Partially supported.* Table 3 在 $3{,}840$ frames 上量到 $20.29$ FPS(Direct mode);超過 $\sim\!3{,}000$ frames 後 Direct mode 退化、必須切到 VO mode(§4.4 page 9–10),而 VO mode 的 throughput 與 boundary 漂移都沒單獨量化,所以 $10{,}000$+ 的 headline 並無對應 benchmark 數字。

### 7.2 Fundamental Limitations of the Method

**Anchor 機制本質脆弱、不可重選。** 座標系與絕對尺度由前 $n$ 幀一次性釘死,後續所有幀以這些 anchor 作為固定參照(§3.2 page 5)。若初始幀是低紋理、運動模糊或基線不足,scale $s$ 從一開始就有偏,而整條軌跡都繼承這個偏差;架構上沒有任何「重新評估或替換 anchor」的路徑,因此這不是訓練可以補的瑕疵,而是設計層級的單點故障。

**軌跡記憶為內容無關的均勻壓縮,結構上排除真正的 loop closure。** 每個被驅逐的幀都壓到固定 $6$ tokens(camera + anchor + 4 register),不論該幀是否觀察到日後會被重訪的關鍵地標(§3.2 page 5)。當相機真的回到舊區域時,當前 query 看到的歷史只是這些壓縮 summary,缺乏跨時間 dense correspondence 所需的 image tokens——也就是說,即便加上學習式 detection,attention 也無從以足夠資訊修正。作者把 loop closure 列為 future work(page 19),但成因是結構性,不是「還沒實作」。

**Feed-forward 設計沒有 rewrite 過去預測的機制。** 一旦 frame $t$ 給出有偏的 $\hat{P}_t$ 與 $\hat{D}_t$,後續幀只能透過 attention 回看 $t$ 的壓縮 token 做隱式平滑,但已輸出的 pose 與 depth 不可被覆寫。對於含顯著尺度模糊或長距離重訪的序列,這是相對於 bundle-adjustment-style 後端的硬上限,任何純 feed-forward 公式都無法跨越。

**對 offline base model 的不可分割依賴。** Stage 1 用了 $\sim\!21{,}500$ GPU hours 的 global attention 預訓練才把 GCA 換上去(§4.1, §4.2);query/key/value 投影權重從 global 直接遷移到 GCA。論文沒有任何 from-scratch GCA 的對照,因此「GCA 為何可行」這個問題的答案被預訓練吃掉了——讀者無法分辨贏面是 GCA 的結構紅利,還是 base model 本身的特徵紅利,這對未來把 GCA 套到其他 backbone 的可遷移性是個未驗證的前提。

### 7.3 Citations Worth Tracking

- **VGGT [75] (Wang et al.)**——LingBot-Map 的 backbone 與 frame/global attention 範式直接繼承自此;許多 loss 定義(depth、abs-pose)沿用 VGGT 的形式,理解 VGGT 是復現本論文工程細節的前提。
- **TTT3R [7] (Chen et al., ICLR 2026)**——streaming 派中與本文設計哲學最對立的方案(用 test-time training 修補 RNN 遺忘);兩者一起讀可看清「learned selective context vs. test-time adaptation」這個分歧的關鍵實驗證據。
- **MASt3R-SLAM [46] / VGGT-SLAM [42]**——Related Work 標榜要超越的 hybrid 派,但實際從未進表;若要驗證 LingBot-Map 對 iterative optimization 的「全面勝出」主張,必須親自比對這兩篇的官方數字。
- **π3 [83] (Wang et al.)**——relative pose loss 的直接靈感來源(§3.3);其 camera-to-world 參數化與 pairwise rotation/translation 解耦設計是理解 LingBot-Map 為何在 RPE-rot 顯著領先的關鍵。
- **DUSt3R [81] (Wang et al.)**——feed-forward dense 3D regression 的開山之作,定義了所有後續方法被串流化前的 offline baseline 形式;不讀此篇就無法判斷 LingBot-Map 在「從 offline 走到 streaming」這條軸線上實際移動了多遠。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] VO mode 的 window-boundary Sim(3) 對齊每次到底引入多少漂移?在 $10{,}000$ / $30{,}000$ frames 量級下與 Direct mode 的可外推誤差曲線長什麼樣子?
- [ ] Anchor 品質劣化(低紋理、模糊、低 baseline)時系統如何降級?是否存在自動偵測壞 anchor 並 fallback 的策略空間?
- [ ] 軌跡記憶每幀 $6$ tokens 是否為最優?$3$、$12$、$24$ 在 ATE / 記憶體 / RPE-rot 上會畫出怎樣的 Pareto?
- [ ] Oxford Spires 上 $\sim\!56$ AUC@15 的躍升,有多少能歸因到 GCA 結構,有多少來自 stage 2 加重的長軌跡資料(尤其 Internal Game)?
- [ ] 若不從 VGGT-style 全 attention base 遷移,直接 from scratch 訓 GCA,收斂與最終效能會落在哪裡?
- [ ] 在 $1024\!\times\!1024$ 解析度或 window=$256$ 時,$(n+k)\cdot M$ 主導項是否仍能維持 $\sim\!20$ FPS?還是 anchor + window 段才是真正的瓶頸?
- [ ] 如何在不破壞 causal streaming 的前提下,把顯式 revisit detection 接到 GCA 的 attention mask 上而不引爆 KV 成本?

### 8.2 Improvement Directions

1. **(易)為軌跡記憶 token 數加一組敏感度實驗。** 既有的 TartanGround ablation 套件已就緒,只需把 $6$ 換成 $\{3, 12, 24\}$ 重跑 fine-tune;這直接回應 §4.2.2 中「為何是 $6$」的設計選擇,也讓 fine-grained 細節保留度有實證依據。
2. **(易)在 Tables 2 / 4 / 5 補上 VGGT-SLAM 與 MASt3R-SLAM。** Related Work 已把它們框為 baseline,實驗框架對齊成本低;補完後「outperform optimization-based」的主張才成立完整版,而非只在 DroidSLAM/MegaSAM/VIPE 上。
3. **(中)以學習式 anchor-quality score 取代「固定取前 $n$ 幀」。** 在 anchor 階段 attach 一個輕量 head 預測該幀 scale-grounding 可信度,允許串流前 $K$ 幀內延後或重選 anchor;這直接修補 §7.2 的「初始化單點故障」結構性問題,且不破壞 causal 性質。
4. **(中)為偵測到的 revisit 暫時恢復 image tokens。** 當軌跡 token 之間相似度超過閾值時,在當下 decode step 把對應歷史幀的 image tokens 從 cache 中拉回 active context,推論完即釋放;這在不引入 bundle adjustment 的前提下提供類似 loop closure 的修正能力,且仍是 feed-forward 的。
5. **(難)做一次純 GCA from-scratch 訓練,把 base model 紅利拆乾淨。** 若效能仍接近現有結果,GCA 結構的可遷移性與獨立貢獻才被釘住;若顯著退化,則必須把「結論依賴 VGGT 預訓練」明寫進方法假設,以正確界定後續工作的適用條件。
