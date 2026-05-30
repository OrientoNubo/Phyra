<!-- type: paper-read-notes | generated: 2026-05-08 | lang: zh-TW -->

# ZipMap — ZipMap: Linear-Time Stateful 3D Reconstruction via Test-Time Training

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | ZipMap |
| Paper full title | ZipMap: Linear-Time Stateful 3D Reconstruction via Test-Time Training |
| arXiv ID | 2603.04385 |
| Release date | 2026-04-08 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.04385 |
| PDF link | https://arxiv.org/pdf/2603.04385 |
| Code link | — |
| Project page | https://haian-jin.github.io/ZipMap |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Haian Jin | Google DeepMind; Cornell University | https://haian-jin.github.io/ | first author |
| Rundi Wu | Google DeepMind | — | co-author |
| Tianyuan Zhang | Massachusetts Institute of Technology | — | co-author |
| Ruiqi Gao | Google DeepMind | — | co-author |
| Jonathan T. Barron | Google DeepMind | — | co-author |
| Noah Snavely | Google DeepMind; Cornell University | — | advisor |
| Aleksander Hołyński | Google DeepMind | https://holynski.org/ | senior author |

### 1.2 Keywords

3D reconstruction, test-time training, feed-forward transformer, linear-time scaling, scene representation, camera pose estimation, depth estimation, stateful model, fast weights

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al., 2025) | baseline | Quadratic-time feed-forward 3D reconstruction model that ZipMap initializes from and aims to surpass in speed. |
| π3 (Wang et al., 2025) | baseline | Recent quadratic-time multi-view feed-forward reconstructor used as primary accuracy/speed comparison. |
| DUSt3R (Wang et al., 2024) | predecessor | Pioneered pairwise feed-forward dense 3D prediction; foundation of the multi-view feed-forward paradigm. |
| CUT3R (Wang et al., 2025) | baseline | Sequential linear-time reconstructor compared against; trades quality for scaling. |
| TTT3R (Deng et al., 2025) | baseline | Sequential TTT-based reconstruction baseline contrasted with ZipMap's bidirectional design. |
| LaCT (Zhang et al., 2025) | base model | Large-chunk Test-Time Training layer that ZipMap directly builds on for nonlinear fast-weight scene state. |
| TTT (Sun et al., 2024) | influence | Test-Time Training framework treating model parameters as fast-weight memory for linear-complexity sequence modeling. |

## 2. Research Overview

### 2.1 Research Topic

本論文研究大規模影像集合的前饋式 3D 場景重建,特別聚焦於相機姿態、深度圖與點雲的同步預測。現有 state-of-the-art 模型如 VGGT 與 π3 採用全域 self-attention 跨所有影像 token 建立幾何一致性,使得計算成本隨輸入影像數呈 quadratic 增長,難以擴展至數百張影像的長序列輸入;另一類序列式方法雖達到 linear 時間,但因遞迴處理而易累積誤差、犧牲品質。作者提出 ZipMap,以 Test-Time Training (TTT) 層取代全域 attention,將整個影像集合在單次前向傳遞中壓縮為 MLP 的 fast-weight 隱藏狀態,實現 linear-time、bidirectional 的高品質重建。同時這個 stateful 表徵亦可作為隱式場景表示,支援即時新視角查詢與串流重建延伸,目標是在大規模影像輸入下兼顧效率、品質與可查詢性。

### 2.2 Domain Tags

- computer vision
- 3D reconstruction
- deep learning

### 2.3 Core Architectures Used

- **Large-Chunk Test-Time Training (TTT) Layer (LaCT-based)**:本論文核心模組,將所有輸入影像 token 透過單次 gradient descent 寫入 SwiGLU-MLP 的 fast weights $f_W$,作為非線性聯想記憶以 linear 成本聚合全域跨視角資訊。
- **Local Window Attention**:每個 view 內以 rotary positional encoding 進行的 self-attention,與 global TTT block 交錯堆疊 24 層,專責捕捉單視角內的空間關係。
- **DINOv2 Encoder**:沿用 VGGT 的預訓練 image tokenizer,將每張輸入影像 patchify 為 token 序列作為 backbone 輸入。
- **DPT-style Prediction Heads**:用於 point map、depth map 與 query head 的稠密預測;camera head 則沿用 VGGT 設計輸出四元數旋轉、3D 位移與兩個 intrinsics。
- **Muon-style Newton–Schulz Orthonormalization + L2 Normalization**:對 fast-weight 梯度做正交化並對更新後權重做 L2 正規化,以維持 TTT 更新數值穩定。
- **Gated Output Unit**:在 TTT 輸出後套用 $\mathrm{SiLU}(W_g o'_i)$ 形式的 gating,提升表現,消融顯示為關鍵元件。
- **Camera / Register / Query Tokens**:每張輸入影像附加 1 個 camera token 與 4 個 register tokens 用於姿態預測;ray-map 輸入則以 query token 取代 camera token,讓 fast weights 可被新視角即時查詢。

### 2.4 Core Argument

作者識別出當前 feed-forward 3D reconstruction 模型的根本瓶頸:它們依賴跨所有影像 token 的 global self-attention 來建立多視角幾何一致性,而 self-attention 的記憶體與計算量天生隨 token 數呈 quadratic 增長。當輸入達數百張影像時,quadratic 成本使 VGGT、π3 等模型在實務上難以運行;而現有 linear-time 替代方案(CUT3R、Point3R、TTT3R)為了避開此瓶頸,改採序列式遞迴處理,但這破壞了雙向 context、引入誤差累積,使重建品質明顯落後。作者主張:真正需要的不是更稀疏的 attention,而是一種能將「所有 token 的 pairwise 互動」壓縮成固定大小狀態、且仍保留雙向訊息整合能力的機制。Test-Time Training 層恰好提供此性質——將模型一部分參數視為 fast weights,在單次前向中以 gradient descent 將所有輸入 key-value 配對的關聯記憶寫入一個非線性 MLP,等價於一次「全域聯想記憶」的建立,但成本對 token 數呈 linear。基於 LaCT 的 large-chunk TTT 設計,作者以 local window attention(處理單視角空間關係)交錯 global TTT block(聚合跨視角資訊)構成 24 層 backbone,並用 Muon 風格的 Newton-Schulz 正交化與 L2 normalization 維持 fast-weight 更新穩定。此設計在邏輯上必然導出三項好處:(1) linear-time bidirectional 重建,使 750 frames 在 H100 上 10 秒內完成、較 VGGT 快逾 20 倍;(2) fast weights 本身即為可查詢的隱式場景表示,新視角查詢成本與輸入影像數無關;(3) 同一機制可平滑延伸為串流重建。因此 TTT 並非單純的效率技巧,而是同時解決「scaling」與「stateful queryable representation」兩個目標的核心設計。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題 "ZipMap: Linear-Time Stateful 3D Reconstruction via Test-Time Training" 把三個關鍵賣點壓進一行：linear-time 的計算複雜度、stateful 的表徵設計，以及作為實作基底的 test-time training。動詞 "Zip" 暗示把整個 image collection 壓縮進一個固定大小的 state。

Abstract 用一個明確的對立框架建立全文 motivation。它先描繪當前 feed-forward 3D 視覺領域的兩條路：一邊是 VGGT、π3 等以 global self-attention 取得高準確度但複雜度為 $O(N^2)$ 的 quadratic 模型；另一邊是 sequential reconstruction 路線，雖然把成本降到 linear 但犧牲品質。作者把 ZipMap 放在這個二元對立的「第三條路」位置：既要 linear-time、bidirectional，又要 match-or-surpass quadratic 模型的準確度。

接著 abstract 把方法骨架濃縮成一句口號式描述——以 test-time training layer 把整個 image collection 在「單一 forward pass」中 zip 成一個 compact hidden scene state。然後立刻給出最具衝擊力的數字證據：在單張 H100 GPU 上 700+ frames 不到 10 秒、比 VGGT 快超過 20 倍。

最後一句把「stateful 表徵」從成本優勢轉化為功能優勢：這個 hidden state 不只是中間產物，還可以即時查詢生成 novel-view、並支援 streaming reconstruction。這同時為後續 §3.4 (Implicit Scene Representation) 與 §4.4 的兩項 application 鋪好梗。整段 abstract 為 introduction 預留了三個必須回答的子問題：為什麼 quadratic 不行、TTT 為什麼能取代 attention、以及 stateful representation 額外帶來什麼。

### 3.2 Introduction

(450 words)

Introduction 把 abstract 的對立框架展開成一個三段式 motivation。第一段先肯定 deep learning 取代傳統 SfM 的成功，並把 VGGT 立為 state-of-the-art 標竿，但立刻指出其致命弱點：依賴 global attention 來建立跨影像的幾何一致性，使得運算量隨輸入影像數呈 quadratic 增長，「at scale 時 computationally prohibitive」。第二段點名 CUT3R、Point3R、TTT3R 等對手——它們用 sequential modeling 或 local partitioning 把成本壓到 linear，但「often reduce reconstruction quality」。這兩段把所有既存方法整齊切成「準確但慢」與「快但差」兩個 cluster，明確定位 ZipMap 要佔的空白象限。

第三段正式 introduce ZipMap，並把貢獻定義為「linear-time、bidirectional、且 match-or-exceed quadratic SOTA」。作者把方法核心一句話講完：用 Test-Time Training (TTT) layer 取代 global attention，把 image collection 壓縮進一個 MLP 的 fast-weights 中。這裡用了極其關鍵的隱喻——把 token sequence 變成 function（fast-weight MLP），而 forward pass 就是訓練那個 function。這個視角讓「全域聚合」的成本從 $O(N^2)$ self-attention 矩陣，轉成 $O(N)$ 的單步 gradient descent。

第四段把「state 不只是省成本工具」這個觀點推到前台：因為它本身就是一個 implicit scene representation，可以在 constant time 被 novel-view 查詢，也能 incrementally 做 streaming 更新。這是把 efficiency 論點延伸成 capability 論點，讓 ZipMap 不只是 "faster VGGT" 而是「具備 VGGT 不能做的事」。

最後一段給出 concrete 證據預告：long sequence 上 700+ images 在 10 秒內完成（75 FPS），比 VGGT 快 20 倍以上，且品質持平或勝出。這直接呼應 Figure 1 的 left/right panel，並為 §4.2 efficiency analysis 與 §4.1 benchmark 結果埋下對照基準。

整節 Introduction 的論述功能很清楚：建立一個「accuracy vs scalability 兩難」的 framing，宣稱 ZipMap 用 TTT 取代 attention 同時破解這個 trade-off，並把後續 §3 Method 必須回答的承諾——「TTT 為何能在 linear cost 下取代 global attention」——明確列出。

### 3.3 Related Work / Preliminaries

(550 words)

§2 用三個 sub-thread 把 ZipMap 同時放在三條技術路徑的交會點，每條 thread 都對應一類競爭者，並對每類提出明確區分點。

第一個 thread 是 Large-scale Structure-from-Motion，從 Building Rome in a Day、COLMAP 一路到 GLOMAP。這條 thread 的功能是把問題「大規模 3D reconstruction」的歷史定位清楚，並指出傳統 SfM 的三個結構性缺陷：sparse output、需要大量 image overlap、以及 time-consuming 的 MVS 階段。作者用「unified, rapid feed-forward pass」把 ZipMap 與此區分——這是把 SfM 視為前世代基線、不是直接競爭者。

第二個 thread 才是真正的對手：feed-forward 3D reconstruction models。從 2-image 的 DUSt3R、MAST3R 開始，延伸到 multi-view 的 Fast3R、FLARE、VGGT 與最新的 π3。作者明確指出這條主線的共同瓶頸：依賴 standard self-attention 來跨影像關聯結構與 pose 資訊，因此複雜度為 quadratic。即使是用 token merging、sparse attention 來加速的工作（FastVGGT、Block-Sparse Global Attention）也仍然是 quadratic runtime。接著切到另一個 sub-cluster：sequential 方法（CUT3R、TTT3R、Point3R、Spann3R）達成 linear scaling 卻代價是品質下降。作者在這裡把 ZipMap 與 sequential 方法的關鍵差異點得很白：「unlike other sequential solutions, does not require recurrent processing, making it less prone to error accumulation」。這個 framing 把 ZipMap 的 linear-time 從「改進版的 sequential」重新定位成「stateful 但非 recurrent」的新範式。

第三個 thread 是 linear-complexity sequence models 的歷史脈絡，從 Linear Transformer、Mamba、DeltaNet、RWKV 一路鋪到 TTT 與 LaCT。這個 thread 表面上是文獻回顧，實際上是把 ZipMap 的方法論基礎合法化。作者特別指出 Linear Transformer 與 Mamba 等現代 RNN 雖然 linear，但設計目標是 1D causal language sequence，「not well-suited to our setting with large in-context inputs (hundreds of images) and bidirectional dependencies」。這直接劃清「為什麼不能直接套 Mamba」。緊接著引入 Test-Time Training 的核心概念——把模型的部分參數當作 "fast-weight" memory，透過 online gradient descent 吸收 in-context information——並 highlight LaCT 的關鍵 contribution：以 nonlinear MLP fast weights 配合大 chunk 更新，達到 hardware efficiency 與 bidirectional context integration。

最後一句直接把 ZipMap 與 LaCT 綁在一起：「ZipMap is built on LaCT to overcome the scaling limitations of prior feed-forward reconstruction models」。這完成了整節的 narrative 收口——ZipMap 不是發明 TTT，而是把 LaCT 的 linear sequence model 工具應用到 multi-view 3D reconstruction 場域，因此既能 inherit linear scaling 與 bidirectional 的優點，又能用 TTT 的 compression 特性把 image collection 變成 queryable scene representation。這也精準鋪墊了 §3 Method 中 architecture 是 local attention + global TTT block 的設計選擇。

### 3.4 Method (overview narrative)

(1700 words)

§3 Method 用一個雙重目標宣告開場：一個有效的 3D foundation model 應同時具備 (1) 高效的 3D reconstruction 與 (2) queryable、persistent 的場景表徵。作者把 ZipMap 定義為一個 stateful feed-forward 模型，能在「單一 forward pass」中同時完成兩件事：linear-time bidirectional 預測 camera pose、depth map、point cloud；並讓 model weights 在同一 pass 中自動 adapt 成一個 implicit scene representation，可在 real time 查詢任意 target camera 的 colored point map。這個雙重目標把後續 §3.1–3.5 的所有設計動機收束到同一條主軸：所有模組都必須同時服務 reconstruction 與 query 兩個 endpoint。

接著的 architecture overview 把核心 design choice 一句話講完：用 local window attention 加 global large-chunk TTT block 取代 prior work（VGGT、π3、Fast3R、FLARE、MapAnything）的 global attention 設計。關鍵 contrast 是 "standard attention 維持一個不斷成長的 token buffer，TTT 把 visual context 壓縮進固定大小的 fast weights"，因此達成 $O(N)$ bidirectional reconstruction 同時 yield 一個 constant-time queryable scene state。這個對比把 ZipMap 的 linear scaling 與 stateful querying 兩個賣點推導成同一個架構決策的兩個 side effect，邏輯上非常乾淨。

§3.1 Input Tokenization 鋪設兩條輸入路徑：image input $\{I_1, \ldots, I_N\}$ 走 reconstruction 路徑、target ray map $T \in \mathbb{R}^{H \times W \times 9}$ 走 query 路徑。Image 用 pretrained DINOv2 encoder 抽 patch-level token；ray map 把 ray origin、direction、$r_o \times r_d$ 串成 9 維 per-pixel feature，patchify 後線性投影。每張影像配一個 camera token（用於預測 pose）與四個 register token；ray map 則把 camera token 換成 query token。這個雙路設計的功能是讓同一個 backbone 既能吃 input image 做 reconstruction、也能用 ray map 做 implicit state query，而 token 維度與排版完全一致。

§3.2 Feature Backbone 是整個方法的論點核心。作者把 backbone 設計成 $L = 24$ 個相同 block，每個 block 包含 (1) Local Window Attention 用 standard self-attention + RoPE 處理單張 view 內的 spatial relation；(2) Global Large-Chunk TTT Layer 用 LaCT 風格的 fast-weight MLP 聚合跨影像全域資訊。TTT block 的核心是一個 SwiGLU-MLP $f_W(x) = W_2(\mathrm{SiLU}(W_1 x) \circ (W_3 x))$，其 fast weights $W = \{W_1, W_2, W_3\}$ 透過單步 gradient descent 在「key-value reconstruction」這個 virtual objective $\mathcal{L}(f_W(k_i), v_i) = -f_W(k_i)^\top v_i$ 上更新。每個 token 都被投影成 $q_i, k_i, v_i$，per-token learning rate $\eta_i$ 由一個小 linear layer 從 token 自身預測。Gradient 算出後，套上 Muon 風格的 Newton-Schulz orthonormalization，再做 L2-normalized weight update 以維持穩定性。更新完的 fast weights $\hat{W}$ 直接套用於每個 token 的 query $q_i$ 得到 $o'_i = f_{\hat{W}}(q_i)$，這個操作在概念上等價於 self-attention 中查詢所有 key-value pair，但複雜度從 quadratic 降到 linear。最後再以 gated unit $\mathrm{SiLU}(W_g o_i)$ 配合 RMSNorm 產生最終輸出。值得注意的是，同一組 fast weights 也能直接套用到 target ray token 的 query $q^t_k$ 上，這就是 implicit scene state 查詢的數學定義——cross-attention 的線性化版本，且查詢成本 constant per ray，獨立於 input view 數量。

§3.3 Streaming Reconstruction 把 bidirectional 設定延伸到 online 場景。原本 fast weights 是用「所有 view 的 token 一次更新」，streaming 版改成「每進來一個 view 就更新一次」：$W^{(t)} \leftarrow \mathrm{TTTUpdate}(W^{(t-1)}; \{k_{t,i}, v_{t,i}\}_{i=1}^{p})$，使用相同的 virtual objective 但只用當前 view 的 visual token。主文僅評估 bidirectional 設定，streaming 結果放在 Appendix D.5。

§3.4 Prediction Heads 配置四個 head：camera head 沿用 VGGT 設計，從 camera token 預測 4D rotation quaternion + 3D translation + 兩個 intrinsics；point head 採 DPT-style，預測 local point map $P_i \in \mathbb{R}^{H \times W \times 3}$（沿用 π3 在相機座標系下的設計）；depth head 額外預測 depth map $D_i$ 與 confidence $\Sigma_i$，雖然定量上與 point head 接近，但視覺上更平滑且 confidence 可在推論時過濾噪點；query head 直接預測 target view 的 RGB 與 depth，無顯式場景表徵。

§3.5 Model Training 把多個 loss 組合：$\mathcal{L} = \mathcal{L}_{\mathrm{point}} + \mathcal{L}_{\mathrm{depth}} + w_c \mathcal{L}_{\mathrm{cam}} + (\mathcal{L}^t_{\mathrm{color}} + \mathcal{L}^t_{\mathrm{depth}})$，其中 $w_c = 5$、query loss 僅在 finetune 階段啟用。Point loss 採 scale-invariant 設計，全域 scale $\hat{s}$ 用 ROE solver 優化；depth loss 用 confidence-modulated L1 並加上 $-\alpha \log \Sigma_i$ 防止退化（$\alpha = 0.2$）；camera loss 先以第一張 frame 為 reference view 用 L1，再切換到 affine-invariant 損失（受 π3 啟發）。三階段訓練在 64 張 H100 上展開：(1) static dataset + reference view 訓 80K 步，TTT 用 $1\mathrm{e}{-4}$、其餘 $1\mathrm{e}{-5}$；(2) 加入 dynamic dataset 並用統一 $1\mathrm{e}{-5}$ 訓 40K 步；(3) 移除 reference view 再訓 60K 步。Token 維度 $d = 1024$、fast-weight MLP 中間維度 2048，每層 state size 為 $6d^2$。29 個公開 dataset，細節留 Appendix B.1。

### 3.5 Experiments (overview narrative)

(1200 words)

§4 Experiments 的 narrative 結構非常工整：用三個面向（benchmark accuracy、efficiency/scalability、ablation 與 capability）依序回應 introduction 中的承諾。開場句直接 frame 整節立場——「TTT-based architecture matches or surpasses state-of-the-art quadratic-time models (VGGT, π3) while being significantly more compute-efficient」——意即所有實驗的目標都是同時證明「品質不輸 quadratic」與「速度勝過 linear」這兩個方向。

§4.1 Benchmark Evaluation 用四類任務循序展開：camera pose estimation、point map estimation、depth estimation。每類都把 baselines 切成 $O(N^2)$ 與 $O(N)$ 兩組，便於讀者一眼看出 ZipMap 同時打敗哪一邊。Camera pose（Table 1, 2）涵蓋 RealEstate10K、Co3Dv2、Sintel、TUM-dynamics、ScanNet 五個資料集，ZipMap 與 VGGT、π3 持平，並大幅領先 CUT3R、TTT3R 等 linear baseline——關鍵 framing 是「在維持 linear 複雜度的前提下達到此準確度」。Point map（Table 3, 4）在 7-Scenes、NRGBD、DTU、ETH3D 四個資料集上 substantially outperform linear baseline、且與 quadratic SOTA 持平或超越。Figure 3 提供質性結果，特別 highlight 在 long-sequence、dynamic scene、internet photo collection 等 hard case 上的穩健性。Video depth（Table 5）在 Sintel、Bonn、KITTI 上 consistently 勝過 $O(N)$ 方法、整體勝過 VGGT；monocular depth 結果留到 Appendix Table 8，但作者在 NYU-v2 上 outperform 所有 baseline 用以證明 single-view geometric prior 仍然強。

§4.2 Efficiency and Scalability 是整節最核心的賣點。作者把 Figure 1 拆成兩個論點：bottom plot 顯示 750 frame 場景下 ZipMap 不到 10 秒完成、VGGT 需要 200+ 秒，速度差超過 20 倍；ZipMap 同時比同為 linear 的 CUT3R、TTT3R 快約 3 倍——作者把這歸因於 baseline 用 sequential 方式逐 frame 處理，inference 時 GPU utilization 偏低，與 ZipMap 用單一 bidirectional pass 的設計形成對比。Top plot 則同時展示 ATE on ScanNet-v2 與 π3 持平、勝過 VGGT、大幅勝過 CUT3R/TTT3R——把「速度」與「準確度」整合到單一 Pareto plot。Figure 4 則用 DL3DV 做兩種 long-sequence 壓力測試：(1) 用前 $N$ frame 增加 scene scale；(2) 沿固定 trajectory uniform subsample $N$ frame 增加 view density。在這兩個 setting 中，ZipMap 都與 quadratic baseline 持平，而 CUT3R、TTT3R 隨 $N$ 增大 error 急劇上升——這對應 §3 Related Work 中「sequential 方法因 recurrent 設計易累積誤差」的主張。

§4.3 Ablation Studies 用 Table 6 鎖定 TTT 設計的兩個 critical 元件：Newton-Schulz orthonormalization 與 gated unit。移除任一都顯著退化 ETH3D point map 準確度。動態 per-token learning rate $\eta(x)$ 也明顯勝過固定全域 TTT learning rate（0.1 或 1.0）。這些 ablation 把 §3.2 介紹的設計選擇從「方法描述」轉成「empirically necessary」。第二個 ablation 是 reference view 的取捨：在 standard benchmark 上，移除 reference view 並改用 affine-invariant loss 沒有 clear advantage，但在 long-sequence input 上明顯改善——作者把 standard benchmark 與 long-sequence 分開判斷，最終納入完整模型。

§4.4 Implicit Scene Representation 把 §3.2 的「fast weights = queryable scene state」這個理論主張轉成兩個 demonstration。第一個是「query state only」：在 novel camera pose 下查詢 RGB + depth 並 back-project 成 colored point cloud，與從 input image 重建出的 point cloud 高度吻合，證明 hidden state 同時 capture geometry 與 appearance。第二個是「inferring unseen structure」（Figure 5）：模型能延伸 wall、floor、ground 等常見 3D structure 到觀測之外的區域，雖然 deterministic 設計使其不能 hallucinate 高頻細節或完全未見物體，但展現出基本的 3D scene prior。Querying 速度約 100 FPS、與 input view 數量無關——這是 §3 Method 中 fast-weight apply 為 constant-time 的實驗驗證。

整節 Experiments 完成的 narrative 收口非常清楚：accuracy 賣點靠 §4.1 benchmark、efficiency 賣點靠 §4.2 runtime + long-sequence、design 合理性靠 §4.3 ablation、stateful capability 靠 §4.4 implicit representation——四個 sub-section 各自對應 introduction 中的一個承諾，沒有冗餘也沒有遺漏。

### 3.6 Conclusion / Limitations / Future Work

(235 words)

§5 Conclusion 用一段濃縮全文：ZipMap 是一個 stateful、bidirectional、linear-time 的 feed-forward 3D reconstruction 架構；在多項 benchmark 上 match 或 surpass quadratic-time SOTA、同時 substantially faster。作者刻意用三個並列子句把 contribution 對齊 abstract 中的承諾：linear scaling、queryable scene state for real-time novel-view、easy extension to streaming reconstruction。最後一句把意義拉到 vision 層次——「a new path toward scalable, high-fidelity 3D perception on large image collections」——把 ZipMap 從 incremental method paper 重新 frame 為一個範式級論點：當 scene 規模拉到 hundreds of images 時，stateful 設計可能取代 attention 成為 multi-view geometry 的預設架構。

§E Limitations（Appendix）誠實地指出主要弱點：當 input sequence 非常長、scene scale 遠超 training distribution 時，效能會出現明顯退化。作者把這個現象 frame 為「all existing feed-forward methods 共有的問題」，而非 ZipMap 獨有的缺陷——這個 framing 一方面降低被攻擊的面、另一方面預告未來方向是整個 sub-field 的共同議題。

Future direction（從現有 limitations 段可推出）包含：(i) 用更長的 training sequence 來擴展模型對大尺度場景的泛化能力；(ii) 結合 explicit spatial memory 或 hierarchical state 來突破 fast-weight MLP 的固定容量上限；以及進一步把 streaming 變體訓練到更長 context（目前僅 24 view，baseline 已達 64 view），預期能再放大 stateful 設計的優勢。整節結語把 ZipMap 定位成 long-sequence 3D perception 的起點而非終點。

## 4. Critical Profile

### 4.1 Highlights

- ZipMap reconstructs 750 frames in under 10 seconds on a single H100, achieving roughly 75 FPS and over 20× speedup over VGGT and 15× over $\pi^3$ at the same length (Figure 1, Table 7, p.14).
- The architecture replaces global self-attention with $L=24$ blocks of local window attention interleaved with large-chunk TTT layers, yielding $O(N)$ complexity while preserving bidirectional context (Figure 2, Section 3.2, p.3).
- On Sintel camera pose (Table 2, p.7), ZipMap reaches ATE $0.132$ — the best among $O(N)$ baselines and within striking distance of $\pi^3$ ($0.073$) and VGGT ($0.172$).
- On point-map estimation (Table 4, p.7), ZipMap attains ETH3D Acc. mean $0.254$ vs. CUT3R $0.593$ and TTT3R $0.763$, while remaining close to the quadratic $\pi^3$ ($0.188$).
- Video depth on Sintel (Table 5, p.7) gives AbsRel $0.248$ and $\delta<1.25$ of $0.695$, beating VGGT ($0.298 / 0.643$) and exceeding all $O(N)$ baselines by a wide margin.
- The Muon-style Newton–Schulz orthonormalization plus L2 normalization on fast-weight updates (Eq. 4–5, p.4) is shown to be load-bearing: removing it raises ETH3D Acc. mean from $0.337$ to $0.408$ (Table 6, p.8).
- The same fast weights $\hat{W}$ act as a queryable implicit scene state, supporting novel-view RGB+depth queries at roughly 100 FPS independent of $N$ (Section 4.4, Appendix A.2, p.13).
- A streaming variant obtained by view-by-view TTT updates (Eq. 8, p.4) outperforms CUT3R/TTT3R on streaming Sintel video depth (AbsRel $0.273$ vs $0.426$, Table 13, p.17) despite being finetuned with only 24-view context against baselines trained with up to 64 views.
- On long-sequence DL3DV (Figure 4, p.7) and ScanNet-v2 (Figure 1), ZipMap holds nearly flat ATE as $N$ grows while CUT3R and TTT3R degrade sharply, demonstrating that the fast-weight aggregator resists the error accumulation typical of recurrent linear-time models.
- Inferring unseen structure (Figure 5, p.8) shows the fast-weight state extrapolates plausible walls/floors/ground beyond the input views, suggesting the TTT memory captures basic 3D scene priors rather than only seen pixels.

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- Reconstruction quality degrades noticeably when sequence length and scene scale extend far beyond the training distribution; the authors point to context-parallel training and global alignment (e.g. VGGT-Long) as needed remedies (Appendix E, p.17–18).
- Novel-view RGB rendered from the implicit state shows blurry high-frequency artifacts; on Mip-NeRF 360 (Table 16, p.18) ZipMap is clearly behind AnySplat (e.g. PSNR $17.65$ vs $21.85$ at 16 views), and the authors explicitly disclaim SoTA NVS, framing query outputs as colored point clouds rather than photorealistic views (Appendix E, p.18).
- The streaming model was only finetuned at 24-view context due to time constraints, while streaming baselines were trained with up to 64-view context, so the streaming-table comparison (Tables 13–15, p.17) is acknowledged to under-sell ZipMap's potential rather than reflect a fully trained system (Appendix B.3 and D.5, p.15, 17).

#### 4.2.2 Phyra-inferred

- The model reuses VGGT's DINOv2 encoder, initializes local window attention from VGGT's frame-wise attention, and initializes a subset of TTT parameters from VGGT's global-attention weights (Section 3.5, p.5), so it is unclear how much of ZipMap's parity with VGGT comes from the TTT layer itself versus inheriting a strong VGGT prior — no from-scratch baseline isolates this.
- Training cost is 64 H100 GPUs for $80\text{K}+40\text{K}+60\text{K}$ iterations across 29 datasets (Section 3.5, p.5), but the paper never reports baseline training budgets, leaving open whether the quality gap over CUT3R/TTT3R reflects architecture or simply larger compute and data.
- The fast-weight state size is fixed at $6d^2$ per layer with $d=1024$ regardless of $N$ (Section 3.5, p.5); the paper offers no capacity-saturation experiment showing where this fixed state stops absorbing new views, even though the long-sequence degradation acknowledged in Appendix E is consistent with such saturation.
- The per-token learning-rate ablation (Table 6, p.8) only compares the learned $\eta(x)$ against two hand-picked global rates ($0.1$ and $1.0$); without a sweep or a learned-but-shared $\eta$ baseline, the claim that *dynamic* (rather than merely *tuned*) learning rates matter is undersupported.
- On RealEstate10K AUC@5 (Table 1, p.5), ZipMap ($53.34$) trails $\pi^3$ ($63.10$) by a substantial margin, and on Sintel ATE (Table 2) it nearly doubles $\pi^3$'s error — yet the abstract's "matching or surpassing" framing is not qualified to flag where the quadratic models still win.
- Querying the scene state is benchmarked qualitatively (Figures 5, 7) and via NVS (Table 16) but is never compared against the alternative of simply re-running ZipMap with the new view appended, so the practical value of the "constant-time query" claim over the trivially-fast $O(N)$ re-pass is not quantified.

### 4.3 Phyra's Judgment (summary)

ZipMap's central contribution — replacing global self-attention with a LaCT-style large-chunk TTT layer to obtain a genuinely linear-time, bidirectional, *quality-preserving* reconstructor — is the first credible demonstration that the recurrent-vs-quadratic dichotomy in feed-forward 3D can be broken, and the speed numbers (Table 7, Figure 1) are real. Much of the rest, however, is engineering refinement of LaCT applied to a VGGT-initialized backbone: Newton–Schulz, gating, dynamic $\eta$, depth+confidence head, three-stage curriculum. The unresolved core question is whether the fixed-size fast-weight state is a fundamental capacity ceiling for truly large scenes — the long-sequence degradation in Appendix E and the absence of a state-size scaling study suggest this may be the next bottleneck rather than a solved one.

## 5. Methodology Deep Dive

### 5.1 Method Overview

ZipMap 採用 stateful feed-forward 架構處理大規模影像集合的 3D 重建,在單次前向傳遞中同步預測 camera poses、depth maps 與 point maps。給定 $N$ 張輸入影像 $\{I_1, \dots, I_N\}$ 其中 $I_i \in \mathbb{R}^{H \times W \times 3}$,模型先以 pretrained DINOv2 encoder 對每張影像進行 patch tokenization,patch size $P=14$,每張影像產生 $p = HW/P^2 + 5$ 個 token(其中 5 個額外 token 為 1 個 camera token 與 4 個 register tokens),token 維度 $d = 1024$。Backbone 由 $L=24$ 層相同 block 構成,每個 block 包含兩個關鍵元件:per-frame local window attention(處理單視角內空間關係)與 global large-chunk TTT layer(跨視角資訊聚合)。

TTT layer 是整個架構的核心創新,以 SwiGLU-MLP 形式實作的 fast-weight function $f_W(x) = W_2[\text{SiLU}(W_1 x) \circ (W_3 x)]$ 取代傳統 self-attention 的 quadratic 成本。對於每個 TTT block,所有輸入 token 經由線性投影產生 query、key、value 三組向量 $\{q_i, k_i, v_i\}$,接著以一次 gradient descent 步驟更新 fast weights:目標函數為 $L(f_W(k_i), v_i) = -f_W(k_i)^\top v_i$,鼓勵 fast-weight function 記憶 $k \to v$ 的關聯映射。為維持訓練穩定性,gradient $g$ 先經 Newton-Schulz orthogonalization(取自 Muon optimizer),再以 L2 normalization 更新權重得到 $\hat{W}$。最後將更新後的 fast-weight MLP $f_{\hat{W}}$ 套用至每個 token 的 query $q_i$,並以 gated unit $\text{SiLU}(W_g o_i)$ 與 RMSNorm 產生最終輸出 $o_i$。此設計等價於對所有 token 的 pairwise key-value 互動進行壓縮,但成本對 token 數呈 linear scaling。

ZipMap 的 fast weights 同時扮演兩種角色:既是跨視角資訊聚合的中介機制,也是可查詢的 implicit scene representation。當查詢時,target ray map $T \in \mathbb{R}^{H \times W \times 9}$(每個 pixel 由 ray origin $r_o$、direction $r_d$ 與 $r_o \times r_d$ 串接而成)經 patchify 與線性投影後產生 query token $q_t^k$,直接套用至已更新的 $f_{\hat{W}}$ 即可在 constant time 內輸出新視角的幾何與外觀預測,成本與 $N$ 無關。模型最終接四個 prediction heads:camera head 預測 9 維相機參數(quaternion + translation + intrinsics)、point head(DPT-style)預測 local point map $P_i \in \mathbb{R}^{H \times W \times 3}$、depth head 預測 depth $D_i$ 與 confidence $\Sigma_i$、query head 預測 target view 的 RGB $I_t$、depth $D_t$ 與 confidence $\Sigma_t$。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: N images {I_1, ..., I_N}, I_i ∈ R^{H×W×3}        Shape: [B, N, H, W, 3]
   │
   │  Per-image DINOv2 encoder + patchify (P=14)
   │  + camera token + 4 register tokens
   ▼
Image tokens {x_i}, x_i ∈ R^{p×d}                       Shape: [B, N, p, d]
   where p = HW/P² + 5,  d = 1024
   │
   │  ┌──────────────────────────────────────────────┐
   │  │  Backbone block × L (L=24)                   │
   │  │                                              │
   │  │  (1) Local Window Attention (per-frame)      │
   │  │      with rotary positional encoding         │
   │  │      Input/Output shape: [B, N, p, d]        │
   │  │           │                                  │
   │  │           ▼                                  │
   │  │  (2) Global Large-Chunk TTT Layer            │
   │  │      ┌──────────────────────────────────┐    │
   │  │      │ Project tokens →                 │    │
   │  │      │   q_i, k_i, v_i ∈ R^{d}          │    │
   │  │      │   Shape: [B, N·p, d] for q/k/v   │    │
   │  │      │   per-token lr η_i ∈ R^{1}       │    │
   │  │      │           │                      │    │
   │  │      │           ▼                      │    │
   │  │      │ Compute g = ∇_W Σ η_i L(f_W(k_i),│    │
   │  │      │                          v_i)    │    │
   │  │      │   W = {W_1, W_2, W_3}            │    │
   │  │      │   each W_j shape: [d, 2d]/[2d,d] │    │
   │  │      │           │                      │    │
   │  │      │           ▼                      │    │
   │  │      │ Δ ← NewtonSchulz(g)              │    │
   │  │      │ Ŵ ← ‖W‖ · (W − Δ)/‖W − Δ‖       │    │
   │  │      │   (state size 6d² per layer)     │    │
   │  │      │           │                      │    │
   │  │      │           ▼                      │    │
   │  │      │ o'_i = f_Ŵ(q_i) ∈ R^{d}         │    │
   │  │      │ o_i  = RMSNorm(o'_i)·SiLU(W_g o'_i)│  │
   │  │      │   Shape: [B, N·p, d]             │    │
   │  │      └──────────────────────────────────┘    │
   │  │           │                                  │
   │  │           ▼  reshape back                    │
   │  │      Tokens [B, N, p, d]                     │
   │  └──────────────────────────────────────────────┘
   │
   │  After L blocks → final tokens [B, N, p, d]
   │
   ├─→ Camera Head ─→ {c_i} ∈ R^{9}                Shape: [B, N, 9]
   │                  (quat 4 + trans 3 + intrin 2)
   │
   ├─→ Point Head (DPT) ─→ P_i ∈ R^{H×W×3}        Shape: [B, N, H, W, 3]
   │
   ├─→ Depth Head (DPT) ─→ D_i ∈ R^{H×W},          Shape: [B, N, H, W]
   │                       Σ_i ∈ R^{H×W}            Shape: [B, N, H, W]
   │
   └─→ Query Path (parallel branch using last layer Ŵ):
        Target ray map T ∈ R^{H×W×9}              Shape: [B, H, W, 9]
            │
            │  Patchify + linear projection
            │  + special query token (replaces camera token)
            ▼
        Ray-map tokens {t_i}, t_i ∈ R^{p×d}        Shape: [B, p, d]
            │
            │  Project to q_t, then apply final-layer f_Ŵ
            │  (constant time per query, independent of N)
            ▼
        Query tokens through Query Head (DPT) →
            Target RGB I_t ∈ R^{H×W×3}             Shape: [B, H, W, 3]
            Target depth D_t ∈ R^{H×W}             Shape: [B, H, W]
            Target conf Σ_t ∈ R^{H×W}              Shape: [B, H, W]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Input Tokenization

**Function:** 將 $N$ 張輸入影像與選用的 target ray map 轉成統一維度的 token 序列,作為 backbone 的輸入。

**Input:**
- Name: $\{I_1, \dots, I_N\}$ 影像集合,以及 optional ray map $T$
- Shape: $[B, N, H, W, 3]$;$T$ 為 $[B, H, W, 9]$
- Source: 使用者輸入的影像序列與目標 camera 參數

**Output:**
- Name: image tokens $\{x_i\}_{i=1}^N$,ray-map tokens $\{t_i\}_{i=1}^M$
- Shape: $x_i \in \mathbb{R}^{p \times d}$,即整體 $[B, N, p, d]$,其中 $p = HW/P^2 + 5$、$d = 1024$
- Consumer: Feature Backbone(local window attention 與 TTT layer)

**Processing:**

1. 每張影像 $I_i$ 經 frozen DINOv2 encoder 抽取 2D spatial feature map(patch size $P = 14$),flatten 為 $HW/P^2$ 個 patch-level token。
2. 為每張影像追加 1 個 camera token(用於預測 camera 參數)與 4 個 register tokens(沿用 VGGT 設計),使每張影像最終得到 $p = HW/P^2 + 5$ 個 token。
3. 對 ray map $T$,每個 pixel 由 9 維向量構成($r_o \in \mathbb{R}^3$、$r_d \in \mathbb{R}^3$、$r_o \times r_d \in \mathbb{R}^3$),先 patchify 成非重疊 patch,flatten 後以 linear layer 投影至 token embedding 維度 $d$;ray map 的 camera token 位置改放置 special query token。

**Key Formulas:**

$$
T(u, v) = [\,r_o(u,v)\;\|\;r_d(u,v)\;\|\;r_o(u,v) \times r_d(u,v)\,] \in \mathbb{R}^9
$$

**Implementation Details:**

DINOv2 encoder 直接沿用 VGGT 的權重作為初始化,$d = 1024$。每張影像的 token 數量包含 5 個非空間 token(1 個 camera/query token + 4 register tokens),其餘為 spatial patch tokens。Ray map 的線性投影層權重未在 paper 中具體說明初始化方式(the paper does not specify)。

#### 5.3.2 Local Window Attention (per-frame)

**Function:** 在單一視角內以 self-attention 捕捉 spatial 局部關係,不跨影像交換資訊。

**Input:**
- Name: per-frame token sequence
- Shape: $[B, N, p, d]$,attention 在每個 view 的 $p$ tokens 內獨立計算
- Source: 上一層輸出(第一層為 Input Tokenization 的結果)

**Output:**
- Name: per-frame refined tokens
- Shape: $[B, N, p, d]$
- Consumer: 同一 block 內的 Global Large-Chunk TTT Layer

**Processing:**

1. 對每張視角的 $p$ 個 token 獨立執行 standard self-attention,N 個 view 之間互不溝通(這是「local」相對於「global TTT」的對比)。
2. 使用 rotary positional encoding(RoPE)為 token 位置注入相對位置資訊,使 attention 對應到 patch 在影像內的空間排列。
3. 此模組不跨 view 聚合,因此計算量對 $N$ 為 linear,對 $p$ 為 quadratic;由於 $p$ 為單張影像的 token 數而非整個 collection 的 token 數,成本可控。

**Key Formulas:**

paper 未列出特殊公式,沿用標準 self-attention 與 RoPE。

**Implementation Details:**

Local window attention 的權重以 VGGT 的 frame-wise attention 初始化。RoPE 細節(如 base frequency)the paper does not specify。

#### 5.3.3 Global Large-Chunk TTT Layer

**Function:** 透過 in-context fast-weight 更新將整個影像集合的全域幾何資訊壓縮至固定大小的 MLP 參數,並以 query 套用更新後的 fast weights 取得每個 token 的全域 context,等價於一次 linear-time 全域 associative memory。

**Input:**
- Name: 所有視角的 backbone tokens $\{x\}$,以及對應投影 $\{q_i, k_i, v_i\}_{i=1}^{N \times p}$ 和 per-token learning rate $\eta_i$
- Shape: $[B, N \cdot p, d]$ for q/k/v;$\eta_i$ 為 $[B, N \cdot p, 1]$
- Source: 同一 block 內 Local Window Attention 的輸出

**Output:**
- Name: token-wise refined output $o_i$ 與 layer 結束時保留的 $\hat{W}$(用於可選的 query 套用)
- Shape: $[B, N \cdot p, d]$
- Consumer: 下一個 backbone block(或最後一層後的 prediction heads / query path)

**Processing:**

1. 每個 token 投影為 query/key/value 三組向量,並以 small linear layer 從 token 預測 per-token learning rate $\eta_i$(Eq. 3)。
2. 計算虛擬目標 $L(f_W(k_i), v_i) = -f_W(k_i)^\top v_i$(Eq. 2),對 $W = \{W_1, W_2, W_3\}$ 取 gradient $g = \nabla_W \sum_{k=1}^{N \times p} \eta_i L(f_W(k_i), v_i)$(Eq. 3)。
3. 套用 Newton-Schulz orthogonalization 將 $g$ 正交化(取自 Muon optimizer):$\Delta \leftarrow \text{NewtonSchulz}(g)$(Eq. 4),並以 L2 normalization 更新 fast weights:$\hat{W} \leftarrow \|W\| \cdot \frac{W - \Delta}{\|W - \Delta\|}$(Eq. 5),維持更新數值穩定。
4. 將更新後的 $f_{\hat{W}}$ 套用至每個 token 的 query:$o'_i = f_{\hat{W}}(q_i)$(Eq. 6),這一步的成本對 token 數呈 linear,作用類同 self-attention 的 query 對所有 key-value 的查詢。
5. 最後以 gated unit 與 RMSNorm 產出輸出:$o_i = \text{RMSNorm}(o'_i) \cdot \text{SiLU}(W_g o'_i)$(Eq. 7),靈感取自 gated attention。

**Key Formulas:**

$$
f_W(x) = W_2 \big[ \text{SiLU}(W_1 x) \circ (W_3 x) \big]
$$

$$
L(f_W(k_i), v_i) = -f_W(k_i)^\top v_i
$$

$$
g = \nabla_W \sum_{k=1}^{N \times p} \eta_i\, L(f_W(k_i), v_i)
$$

$$
\Delta \leftarrow \text{NewtonSchulz}(g), \qquad \hat{W} \leftarrow \|W\| \cdot \frac{W - \Delta}{\|W - \Delta\|}
$$

$$
o_i = \text{RMSNorm}(f_{\hat{W}}(q_i)) \cdot \text{SiLU}(W_g\, f_{\hat{W}}(q_i))
$$

**Implementation Details:**

Fast-weight MLP 採 SwiGLU 形式,中間維度為 $2d = 2048$,使每層 fast-weight state 大小為 $6d^2$(對應 $W_1, W_2, W_3$ 三個矩陣)。Per-token learning rate $\eta_i$ 由一個 simple linear layer 從 token 直接預測。Backbone 一部分的 TTT 參數從 VGGT 的 global-attention 參數初始化。Newton-Schulz 正交化的迭代次數 the paper does not specify。

#### 5.3.4 Streaming Reconstruction Update (optional)

**Function:** 將 bidirectional 模式延伸為 sequential streaming,每次只用單張新進影像的 visual tokens 更新 TTT fast weights,實現持續的線上場景累積。

**Input:**
- Name: 上一時刻 fast weights $W^{(t-1)}$ 與當前視角的 $\{k_{t,i}, v_{t,i}\}_{i=1}^{p}$
- Shape: $W^{(t-1)}$ 形狀同前述 $W$;$\{k_{t,i}, v_{t,i}\}$ 為 $[B, p, d]$
- Source: 影像串流 $\{I_1, I_2, \dots\}$ 以及 backbone 對當前視角的局部處理

**Output:**
- Name: 更新後 fast weights $W^{(t)}$
- Shape: 與 $W$ 相同
- Consumer: 後續 streaming 步驟以及任何需要查詢場景狀態的 head

**Processing:**

1. 對每個新進視角 $I_t$,backbone 仍照常產生其 patch tokens,但 TTT 更新只使用該視角的 $p$ 個 visual token 投影。
2. 套用與 §5.3.3 相同的虛擬 KV-reconstruction 目標(Eq. 2)計算 gradient,僅在當前視角 token 上累加。
3. 以 Newton-Schulz + L2 normalization 進行 online 更新(沿用 Eq. 4–5),隨時間 $t$ 累積場景資訊。

**Key Formulas:**

$$
W^{(t)} \leftarrow \text{TTTUpdate}\big(W^{(t-1)}; \{k_{t,i}, v_{t,i}\}_{i=1}^{p}\big)
$$

**Implementation Details:**

論文主體聚焦 linear-time bidirectional 模式;streaming setting 的更詳細評估放在 Appendix D.5 中。Streaming 的具體 finetuning 流程細節在 Appendix B.3,主文中 the paper does not specify 完整訓練配方。

#### 5.3.5 Prediction Heads

**Function:** 從 backbone 處理後的 token 與 fast-weight 表徵中,輸出相機姿態、深度、點雲與(可選的)新視角 RGB/Depth 預測。

**Input:**
- Name: 最終 backbone tokens $[B, N, p, d]$;query path 額外接收最後一層 fast weights $\hat{W}$ 與 ray-map tokens $[B, p, d]$
- Shape: 詳見上方 pipeline diagram
- Source: 最後一層 backbone block(camera/point/depth head)以及最後一層 TTT 的 $\hat{W}$(query head)

**Output:**
- Name 與 Shape:
  - Camera head: $c_i \in \mathbb{R}^9$,形狀 $[B, N, 9]$(4D quaternion + 3D translation + 2 intrinsics)
  - Point head: $P_i \in \mathbb{R}^{H \times W \times 3}$,形狀 $[B, N, H, W, 3]$(local camera coordinates)
  - Depth head: $D_i \in \mathbb{R}^{H \times W}$ 與 confidence $\Sigma_i \in \mathbb{R}^{H \times W}$,形狀皆 $[B, N, H, W]$
  - Query head: target RGB $I_t \in \mathbb{R}^{H \times W \times 3}$、target depth $D_t \in \mathbb{R}^{H \times W}$、target confidence $\Sigma_t \in \mathbb{R}^{H \times W}$
- Consumer: 訓練 loss(§5 後續訓練段)、推論時下游應用(camera trajectory、dense point cloud、novel view synthesis)

**Processing:**

1. Camera head 使用與 VGGT 相同的設計,從每張影像的 camera token 預測 9 維相機參數。
2. Point head 採 DPT-style 結構,在每個 pixel 預測 camera-space 的 local 3D 點(類似 π³)。
3. Depth head 同為 DPT-style,額外輸出 self-learned confidence map $\Sigma_i$ 以在推論時過濾 noisy pixel;paper 觀察到 depth head 與 point head 量化效能相近,但 depth 結果在視覺上更平滑。
4. Query head 不依賴 explicit scene representation,直接由 ray-map tokens 通過更新後的 $f_{\hat{W}}$ 與 DPT-style 結構,輸出新視角的 RGB 與 depth(及 confidence),可在 constant time per query 完成,與輸入影像數無關。

**Key Formulas:**

paper 在此節未提供新公式,主要復用 §5.3.3 中 fast-weight 的 query 套用過程。

**Implementation Details:**

Camera head 沿用 VGGT 的設計,point/depth/query head 統一使用 DPT-style 架構。Query loss($\mathcal{L}^t_\text{color}$ 與 $\mathcal{L}^t_\text{depth}$)只在 finetuning 階段啟用,主訓練階段不使用。Confidence map 採用對數正則項($-\alpha \log \Sigma$),建模為 Laplacian negative log-likelihood,$\alpha = 0.2$。Head 內部卷積層數與通道數細節 the paper does not specify。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Aria Synthetic Environments | Static scene reconstruction | Large-scale synthetic indoor | train |
| ARKitScenes | Static indoor RGB-D | Large-scale real | train |
| BlendedMVS | Static MVS | Large-scale | train |
| Co3Dv2 | Object-centric multi-view | Large-scale real | train + test (camera pose, AUC@5/15/30) |
| DL3DV | Static outdoor scenes | 10K+ scenes | train + test (long-sequence camera ATE on 55 test scenes) |
| GTA-SfM | Static synthetic | — | train |
| Hypersim | Photoreal synthetic indoor | — | train |
| MapFree | Visual relocalization | — | train |
| MatrixCity | City-scale synthetic | Large-scale | train |
| Matterport3D | Indoor RGB-D | — | train |
| MegaDepth | Internet photos | Large-scale | train (excluded during query finetuning) |
| MidAir | Drone synthetic | — | train |
| MVS-Synth | Synthetic MVS | — | train |
| OmniObject3D | Object-centric | — | train |
| ScanNet | Indoor RGB-D | Large-scale | train + test (camera pose ATE/RPE; long-sequence pose & video depth) |
| ScanNet++ | High-fidelity indoor | — | train |
| ScenenetRGBD | Synthetic indoor | — | train |
| TartanAir | Visual SLAM | Large-scale | train |
| TartanGround | Ground-robot navigation | Large-scale | train |
| Unreal4k | Stereo synthetic | — | train |
| Virtual KITTI | Driving synthetic | — | train |
| Waymo | Autonomous driving | Large-scale | train |
| WildRGBD | In-the-wild RGB-D | — | train |
| BEDLAM | Dynamic humans | — | train (dynamic) |
| Dynamic Replica | Dynamic stereo | — | train (dynamic) |
| Kubric | Dynamic synthetic | — | train (dynamic) |
| OmniWorld | 4D world modeling | — | train (dynamic) |
| PointOdyssey | Long-term tracking | — | train (dynamic) |
| Spring | Dynamic scene flow | — | train (dynamic) |
| RealEstate10K | Camera pose | — | test only (AUC@5/15/30) |
| Sintel | Dynamic synthetic | — | test only (camera pose, video/monocular depth) |
| TUM-dynamics | Dynamic real | — | test only (camera pose) |
| Bonn | RGB-D dynamic | — | test only (video/monocular depth) |
| KITTI | Driving real | — | test only (video/monocular depth) |
| NYU-v2 | Indoor RGB-D | — | test only (monocular depth) |
| 7-Scenes | Indoor RGB-D | — | test only (point-map; long-sequence point) |
| NRGBD | Neural RGB-D | — | test only (point-map) |
| DTU | Multi-view stereo | — | test only (point-map) |
| ETH3D | Multi-view stereo | — | test only (point-map; ablations) |
| Mip-NeRF360 | Unposed NVS | — | test only (Appendix Tab. 16) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| AUC@5 / AUC@15 / AUC@30 | Pose AUC under angular error thresholds of $5°/15°/30°$ for camera pose estimation | yes |
| ATE | Absolute Trajectory Error of estimated camera trajectory | yes |
| RPE trans | Relative Pose Error — translation component | no |
| RPE rot | Relative Pose Error — rotation component | no |
| Acc. (mean / median) | Point-map accuracy: distance from predicted points to ground-truth surface | yes |
| Comp. (mean / median) | Point-map completeness: distance from ground-truth surface to predicted points | yes |
| N.C. (mean / median) | Normal consistency between predicted and ground-truth normals | no |
| AbsRel | Absolute relative error of predicted depth vs. ground truth | yes |
| $\delta < 1.25$ | Fraction of pixels with depth ratio within $1.25$ | yes |
| Wall-clock runtime (seconds) | End-to-end reconstruction time on a single H100 for $N$ frames | yes |
| FPS | Frames-per-second throughput at inference (reconstruction or query) | no |
| PSNR / SSIM / LPIPS | Novel-view-synthesis quality (Appendix only, not a main claim) | no |

### 6.3 Training and Inference Settings

- Hardware: 64 H100 GPUs for the main three-stage training; an additional 32 H100 GPUs for streaming finetuning (Appendix B.3).
- Training stages and schedule (Sec. 3.5):
  - Stage 1 (static datasets, designated reference view): 80K iterations, learning rate $1\text{e-}4$ for TTT blocks and $1\text{e-}5$ for all other modules; about 5 days.
  - Stage 2 (incorporate dynamic datasets, finetune): 40K iterations at uniform learning rate $1\text{e-}5$; about 2.5 days.
  - Stage 3 (remove reference view, affine-invariant camera loss from $\pi^3$): 60K iterations at learning rate $1\text{e-}5$.
  - Scene-state-query finetuning: 100K iterations; max images per GPU reduced from 48 to 44; color-based augmentation disabled; dynamic and inconsistent-collection datasets (e.g. MegaDepth) excluded; per scene 4–44 frames sampled, half input / half target (Appendix B.3).
  - Streaming finetuning: replaces transformer camera head with a 2-layer MLP; 60K steps at $1\text{e-}5$ with 36 images/GPU (12/scene), then 30K more at the same rate with 48 images/GPU (24/scene) (Appendix B.3).
- Optimizer: the paper does not specify the outer optimizer for the network weights; for the inner TTT update, the fast-weight gradient is processed by Newton–Schulz orthonormalization (Muon-style) followed by L2-normalized weight update (Eq. 4–5).
- Batch / context: per scene 2–48 frames sampled, capped at 48 images per GPU during the main training; FSDP with `torch.compile` applied to the TTT block (Appendix B.3).
- Data augmentation: color jitter, Gaussian blur, grayscale; input width 518 with random aspect ratio in $[0.33, 1.0]$ (Appendix B.3).
- Initialization: DINOv2 encoder reused from VGGT; local window-attention weights initialized from VGGT's frame-wise attention; a subset of TTT parameters initialized from VGGT's global-attention parameters (Sec. 3.5).
- Architecture sizes: $L = 24$ blocks; token dim $d = 1024$; fast-weight MLP intermediate dim $2048$; per-layer state size $6d^2$; patch size $P = 14$ (Sec. 3 / 3.5).
- Inference settings (Appendix A.2): single H100 SXM5, PyTorch 2.7.1, CUDA 12.8; softmax attention via `scaled_dot_product_attention` (cuDNN FlashAttention-2); input resolution $392 \times 518$ for VGGT / $\pi^3$ / Ours, $384 \times 512$ for CUT3R / TTT3R; runtimes averaged over 10 iterations after 2 warm-ups; long-sequence evaluation up to 750 frames (close to the 80GB memory limit). Baseline image widths: 512 for CUT3R/TTT3R, 518 for VGGT/$\pi^3$/Ours (Appendix A.1).

### 6.4 Main Results

**Camera Pose Estimation — RealEstate10K & Co3Dv2 (Table 1):**

| Method | RE10K AUC@5 | RE10K AUC@30 | Co3Dv2 AUC@5 | Co3Dv2 AUC@30 | Notes |
|---|---|---|---|---|---|
| Fast3R | 22.36 | 61.68 | 31.05 | 73.43 | $O(N^2)$ |
| FLARE | 38.47 | 80.01 | 23.84 | 73.99 | $O(N^2)$ |
| VGGT | 38.71 | 78.89 | 67.84 | 89.99 | $O(N^2)$ |
| $\pi^3$ | 63.10 | 87.40 | 57.12 | 87.93 | $O(N^2)$ |
| CUT3R | 46.92 | 81.68 | 24.88 | 71.72 | $O(N)$ |
| TTT3R | 46.37 | 81.51 | 22.61 | 69.46 | $O(N)$ |
| **Ours (ZipMap)** | **53.34** | **84.30** | **62.46** | **88.76** | **$O(N)$, best among linear-time** |

**Camera Pose — Sintel / TUM-dynamics / ScanNet (Table 2, ATE):**

| Method | Sintel ATE | TUM-dyn ATE | ScanNet ATE | Notes |
|---|---|---|---|---|
| VGGT | 0.172 | 0.012 | 0.035 | $O(N^2)$ |
| $\pi^3$ | 0.073 | 0.014 | 0.030 | $O(N^2)$, best overall on Sintel |
| CUT3R | 0.216 | 0.042 | 0.096 | $O(N)$ |
| TTT3R | 0.204 | 0.028 | 0.065 | $O(N)$ |
| **Ours** | **0.132** | **0.012** | **0.034** | **$O(N)$, best linear-time, ties VGGT** |

**Point-Map Estimation — DTU & ETH3D (Table 4, mean):**

| Method | DTU Acc | DTU Comp | ETH3D Acc | ETH3D Comp | Notes |
|---|---|---|---|---|---|
| VGGT | 1.308 | 1.929 | 0.270 | 0.304 | $O(N^2)$ |
| $\pi^3$ | 1.151 | 1.793 | 0.188 | 0.211 | $O(N^2)$, best on ETH3D |
| CUT3R | 5.045 | 6.437 | 0.593 | 0.747 | $O(N)$ |
| TTT3R | 5.337 | 6.593 | 0.763 | 0.881 | $O(N)$ |
| **Ours** | **1.228** | **1.649** | **0.254** | **0.249** | **best Comp on DTU & ETH3D** |

**Video Depth Estimation — scale-only alignment (Table 5):**

| Method | Sintel AbsRel | Sintel $\delta<1.25$ | Bonn AbsRel | KITTI AbsRel | KITTI $\delta<1.25$ |
|---|---|---|---|---|---|
| VGGT | 0.298 | 0.643 | 0.055 | 0.073 | 0.965 |
| $\pi^3$ | 0.228 | 0.672 | 0.051 | 0.038 | 0.986 |
| CUT3R | 0.432 | 0.510 | 0.072 | 0.152 | 0.805 |
| TTT3R | 0.426 | 0.522 | 0.061 | 0.149 | 0.812 |
| **Ours** | **0.248** | **0.695** | **0.059** | **0.057** | **0.974** |

**Runtime — single H100, seconds (Table 7, headline efficiency claim):**

| Method | $N=5$ | $N=50$ | $N=200$ | $N=500$ | $N=750$ |
|---|---|---|---|---|---|
| VGGT ($O(N^2)$) | 0.102 | 1.524 | 16.04 | 90.39 | 200.36 |
| $\pi^3$ ($O(N^2)$) | 0.087 | 1.186 | 12.19 | 68.26 | 151.16 |
| CUT3R ($O(N)$) | 0.206 | 2.056 | 8.222 | 21.03 | 31.25 |
| TTT3R ($O(N)$) | 0.206 | 2.036 | 8.267 | 20.77 | 31.20 |
| **Ours ($O(N)$)** | **0.125** | **0.712** | **2.681** | **6.671** | **9.999** |

At 750 frames, ZipMap is roughly $20\times$ faster than VGGT, $15\times$ faster than $\pi^3$, and about $3\times$ faster than CUT3R / TTT3R, while query-only operation reaches about 100 FPS (Sec. 4.2, Appendix A.2).

### 6.5 Ablation Studies

- **TTT components on ETH3D point-map (Table 6, reduced-compute setting).**
  - Removing the gated unit (Eq. 7): Acc. mean degrades $0.337 \to 0.354$, Comp. mean $0.357 \to 0.381$, N.C. mean $0.810 \to 0.802$. Diagnostic — directly tests the contribution of the gated output unit introduced in Sec. 3.2.
  - Removing Newton–Schulz orthonormalization (Eq. 4): Acc. mean $0.337 \to 0.408$, Comp. mean $0.357 \to 0.430$, N.C. mean $0.810 \to 0.787$. Diagnostic — isolates the Muon-style gradient preconditioning, the largest single contributor among the tested components.
  - Replacing the per-token learned learning rate $\eta(x)$ with a fixed global TTT lr of $0.1$ or $1.0$: Acc. mean $0.337 \to 0.411$ (lr 0.1) or $0.464$ (lr 1.0). Diagnostic — confirms that the data-dependent inner-loop step size is non-trivial, not just a tunable scalar.

- **Removing the reference view (Sec. 4.3, Appendix D.4, Tables 10–12, Figure 8).** Stage-2 ("Ours w/ ref") vs. Stage-3 ("Ours w/o ref") shows no consistent gap on the standard short-sequence benchmarks (e.g. Sintel ATE $0.125 \to 0.132$, ScanNet ATE unchanged at $0.034$). The motivating evidence is moved to long-sequence ScanNet/DL3DV plots, where removing the reference view reduces ATE as $N$ grows. This is a *targeted* ablation but its claimed benefit is supported only by the long-sequence figures, not by the headline tables — readers should treat it as a long-sequence-specific finding.

- **What is missing.** No ablation on the number of TTT blocks $L$, fast-weight hidden dim, chunk size, or window-attention size; no ablation that swaps TTT for a Mamba / DeltaNet / linear-attention variant to isolate whether the linear-time gains come specifically from large-chunk TTT versus any linear-recurrent backbone. The current ablations diagnose components *inside* the TTT block but leave the design choice "TTT vs other linear models" unverified. The "remove reference view" study is closer to a design-choice justification than a sanity check, but no full-scale stage-3-vs-stage-2 retraining sweep is reported.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — VGGT and $\pi^3$ are the current quadratic-time SoTA and are compared head-to-head on every benchmark (Tables 1–5, 7).
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — covers camera pose (5 datasets), point-map (4 datasets), video depth (3 datasets), monocular depth (4 datasets), and NVS (Mip-NeRF360, appendix).
- [partial] Has ablations that diagnose the new components (not just sanity checks) — Table 6 isolates gated unit, Newton–Schulz, and per-token $\eta$, but no ablation contrasts TTT with alternative linear-recurrent backbones or sweeps key hyperparameters like block count or chunk size.
- [covered] Has a scaling study (size, length, or compute) — long-sequence evaluations on DL3DV and ScanNet up to 750 frames (Figures 1, 4, 8, 9, 10), explicitly varying both scene scale and view density.
- [covered] Has an efficiency / wall-clock comparison — Table 7 reports per-method seconds on a single H100 from $N=5$ to $N=750$, with $20\times$-vs-VGGT and query-time $\approx 100$ FPS claims grounded in measured numbers.
- [missing] Reports variance / standard deviation / multiple seeds where relevant — runtimes are averaged over 10 iterations but no std reported; quality metrics in all tables are single numbers with no seed variance or confidence interval, and DL3DV plots drop the worst $5\%$ of scenes without showing dispersion.
- [partial] Releases code / weights / data sufficient for reproducibility — a project page is linked (`https://haian-jin.github.io/ZipMap`); the paper does not specify whether code or trained weights are released, and reproduction would require the 64-H100 multi-stage schedule plus the 29-dataset mixture.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **"Linear-time bidirectional reconstruction with quality matching or surpassing $O(N^2)$ models"** — *partially supported.* Table 7 (p.14) cleanly demonstrates the linear runtime; Tables 2, 3, 5 show parity or wins versus VGGT. But on RealEstate10K (Table 1) and Sintel ATE (Table 2), $\pi^3$ still leads materially, so "matching or surpassing" is true on average rather than uniformly.
- **"TTT compresses the entire image collection into a compact hidden state"** — *supported as a mechanism, not as a capacity guarantee.* The forward-pass equations (Eqs. 2–6, p.4) and the implicit-scene-query results (Figures 5, 7) confirm the hidden state encodes globally consistent geometry. There is no experiment varying state size or sequence length to characterize when the $6d^2$ state saturates, so "compact" is shown qualitatively but its limits are unmeasured.
- **"Real-time queryable implicit scene representation"** — *partially supported.* The constant-time query property is architecturally inevitable and the ~100 FPS figure (Appendix A.2) is plausible. But the queried output's *utility* is mostly demonstrated as colored point clouds (Figure 7); when held to NVS metrics (Table 16) the representation lags AnySplat by ~4 dB PSNR, which the authors themselves acknowledge.
- **"Extension to streaming reconstruction"** — *supported as a feasibility result, not as a SoTA claim.* Tables 13–15 show streaming ZipMap beating CUT3R and TTT3R, but at a 24-view finetuning context vs. baselines' 64-view context — the comparison demonstrates that the bidirectional model degrades gracefully into a streaming one, not that it is the best streaming reconstructor possible.
- **"More than 20× faster than VGGT"** — *supported.* Table 7 gives $200.4\,\text{s}$ vs. $9.999\,\text{s}$ at $N=750$, exactly the claimed factor; Figure 1 visualizes the same scaling curve.

### 7.2 Fundamental Limitations of the Method

The most important structural limitation is the fixed-size fast-weight state. The TTT block compresses *all* $N$ images' key–value pairs into a single MLP with $6d^2$ parameters per layer (Section 3.5, p.5). This is a hard information-theoretic ceiling: as $N$ grows the per-token "memory budget" shrinks proportionally, and gradient-descent writes inevitably interfere. The Appendix E observation that quality drops on sequences beyond the training distribution is consistent with this saturation; no experiment in the paper isolates state size from training-distribution effects, so the practical ceiling is unknown.

A second structural issue is the single TTT update per layer. Eq. 3 takes one gradient step per block, so the fast weights are a *one-shot* associative memory. Unlike attention, which retrieves on demand, the fast weights commit to an aggregation policy at write time. This makes the model architecturally vulnerable to ordering and chunking effects when streaming (Eq. 8, p.4), and arguably explains the gap to bidirectional ZipMap in the streaming tables — a limitation that more update steps cannot trivially fix without breaking the linear-time budget.

A third structural concern is that the queryable scene state shares its capacity with reconstruction-time aggregation. The implicit representation is the *same* fast weights that store the geometric reasoning needed for depth and pose heads. There is no separation between "scene memory" and "computation memory", so improving query fidelity (e.g. for NVS) likely competes with reconstruction accuracy — Table 16's modest NVS numbers and Appendix E's blur-artifact discussion both point to this fundamental coupling rather than a fixable training detail.

### 7.3 Citations Worth Tracking

- **LaCT (Zhang et al., 2025) [86]** — ZipMap is essentially LaCT applied to multi-view 3D; understanding LaCT's chunk-size tradeoffs and its empirical scaling laws is prerequisite to judging whether ZipMap's fast-weight state is well-sized.
- **VGGT (Wang et al., 2025) [68]** — both the architectural template (DINOv2 + window attention + camera/DPT heads) and the source of initialization weights; needed to assess how much of ZipMap's quality is inherited.
- **$\pi^3$ (Wang et al., 2025) [76]** — the strongest quadratic-time competitor and the source of the affine-invariant camera loss adopted in stage 3; remains the model to beat on Sintel and RealEstate10K.
- **TTT3R (Deng et al., 2025) [13]** — the most direct linear-time TTT baseline; reading it clarifies why a *recurrent* TTT setup accumulates error and motivates ZipMap's bidirectional choice.
- **Test-time regression unifying framework (Wang et al., 2025) [70]** — provides the theoretical lens (associative memory) under which the virtual key–value objective in Eq. 2 should be understood.

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] How does reconstruction quality scale with the fast-weight state size $6d^2$ — is there a measurable saturation point as $N$ grows, and does it explain the long-sequence degradation in Appendix E?
- [ ] How much of ZipMap's parity with VGGT survives if the local window attention and TTT parameters are trained from scratch instead of initialized from VGGT (Section 3.5, p.5)?
- [ ] What is the baseline training compute for CUT3R, TTT3R, and $\pi^3$ relative to ZipMap's 64-H100 × ~10-day budget — is the quality gap over linear-time baselines architectural or compute-driven?
- [ ] Does increasing the number of inner gradient steps per TTT layer (currently one, Eq. 3) close the bidirectional-vs-streaming gap, and if so at what runtime cost?
- [ ] Why does $\pi^3$ still dominate RealEstate10K AUC@5 ($63.10$ vs $53.34$, Table 1) — is this a training-data effect, a TTT capacity issue, or an architectural blind spot for forward-motion sequences?
- [ ] How does the constant-time query benchmark against the trivial alternative of appending the new view and re-running ZipMap end-to-end, in both latency and quality?
- [ ] Does the learned per-token $\eta(x)$ outperform a *tuned* shared $\eta$, or only the two arbitrary global rates ($0.1$, $1.0$) reported in Table 6?

### 8.2 Improvement Directions

1. **State-size scaling study.** Re-train ZipMap at $\{0.5\times, 1\times, 2\times, 4\times\}$ the current $6d^2$ state and measure quality vs. $N$. Logical basis: the long-sequence degradation acknowledged in Appendix E is exactly what fixed-state capacity exhaustion looks like, and this study would either rule it out or motivate the next architectural change.
2. **Multi-step TTT inner loop with budget control.** Allow $K$ inner gradient steps in the TTT layer and trade $K$ against block depth $L$. Logical basis: a single gradient step is a strong commitment; multi-step inner loops are exactly how DeltaNet/Titans recover capacity, and the streaming tables suggest the bidirectional model is leaving headroom on the table.
3. **Decoupled scene-memory vs. computation-memory.** Split the fast weights into a "store" set (only updated by Eq. 3) and a "compute" set (only used in Eq. 6) so that NVS-style query fidelity does not compete with reconstruction. Logical basis: Table 16 and Appendix E together imply the current shared-state design forces a Pareto frontier between point-cloud accuracy and rendered RGB quality.
4. **Hierarchical / chunked state for very long sequences.** Maintain multiple fast-weight states at coarser granularities and combine via a top-level TTT update. Logical basis: this is the analog of multi-resolution scene representations and would let the state capacity grow sub-linearly with $N$ without reverting to $O(N^2)$.
5. **Honest streaming retrain at 64-view context.** Refinetune the streaming variant at the same context length as CUT3R/TTT3R baselines. Logical basis: the authors themselves expect a "larger advantage" (Appendix D.5, p.17); resolving this would convert a feasibility demo into a definitive streaming-SoTA claim.
6. **Capacity-aware long-sequence training via context parallelism.** As Appendix E suggests, train on $N \gg 50$ sequences using CP. Logical basis: ZipMap's linear runtime makes long-context training cheaper than for VGGT/$\pi^3$, so it can plausibly be the first feed-forward 3D model trained on the regime where it will be deployed, eliminating the train/test scale mismatch.
