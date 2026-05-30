<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# Scal3R — Scal3R: Scalable Test-Time Training for Large-Scale 3D Reconstruction

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | Scal3R |
| Paper full title | Scal3R: Scalable Test-Time Training for Large-Scale 3D Reconstruction |
| arXiv ID | 2604.08542 |
| Release date | 2026-04-09 |
| Conference/Journal | arXiv preprint (CVPR 2026 Highlight) |
| Paper link (abs) | https://arxiv.org/abs/2604.08542 |
| PDF link | https://arxiv.org/pdf/2604.08542 |
| Code link | https://zju3dv.github.io/scal3r |
| Project page | https://zju3dv.github.io/scal3r |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Tao Xie | Zhejiang University; Horizon Robotics | https://github.com/xbillowy | first author |
| Peishan Yang | Zhejiang University | https://github.com/PeiPei233/ | co-author |
| Yudong Jin | Zhejiang University | https://github.com/krahets | co-author |
| Yingfeng Cai | Horizon Robotics | — | co-author |
| Wei Yin | Horizon Robotics | https://yvanyin.xyz/ | co-author |
| Weiqiang Ren | Horizon Robotics | — | co-author |
| Qian Zhang | Horizon Robotics | — | co-author |
| Wei Hua | Zhejiang Lab | — | co-author |
| Sida Peng | Zhejiang University | https://pengsida.net/ | co-author |
| Xiaoyang Guo | Horizon Robotics | https://xy-guo.github.io/ | co-corresponding author |
| Xiaowei Zhou | Zhejiang University (State Key Lab of CAD&CG) | https://xzhou.me/ | co-corresponding author |

### 1.2 Keywords

large-scale 3D reconstruction, feed-forward reconstruction, test-time training, global context memory, VGGT, RGB-only SLAM, long-sequence modeling, kilometer-scale scenes

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al.) | base model | Unified Transformer feed-forward model for camera/depth/pointmap; Scal3R builds directly on its backbone. |
| VGGT-Long | predecessor | Divide-and-conquer chunk-wise extension of VGGT; Scal3R adopts its chunking and alignment but adds global context. |
| FastVGGT | baseline | Token-merging acceleration of VGGT; compared as a scalability baseline that loses fine spatial cues. |
| DUSt3R / MASt3R | influence | Pioneer two-view feed-forward pointmap regression; motivates uncalibrated multi-view geometry pipeline. |
| TTT3R | baseline | Casts memory update as test-time learning with fixed token set; Scal3R replaces it with scalable neural memory. |
| LaCT | influence | Large-chunk test-time training for parallel GPU updates; inspires Scal3R's chunk-as-update-unit GCM design. |
| CUT3R / StreamVGGT / STream3R | baseline | Online/streaming feed-forward variants with memory tokens or causal Transformers; compared on long-sequence pose. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於從長序 RGB 影片進行公里級大規模 3D 場景重建。近期 feed-forward 模型(如 VGGT)能直接從多視角影像回歸幾何,但其注意力的二次方計算量與固定記憶體容量,使其難以擴展至上千張影像、長軌跡的城市或戶外場景。現有改良如 FastVGGT 透過 token merging 壓縮代價、VGGT-Long 採分塊重建後對齊,皆會損失全域脈絡或對局部誤差過度敏感。作者提出 Scal3R,在 VGGT backbone 中嵌入「神經全域脈絡記憶」(GCM)與「全域脈絡同步」(GCS)機制,以輕量子網路在推論時透過自監督快速更新,壓縮並保留長距資訊;搭配 GPU 間梯度 all-reduce 的 context parallelism,使各 chunk 能共享整段序列的全域脈絡,在 KITTI Odometry、Virtual KITTI、Oxford Spires 等基準上達成 SOTA 的位姿與重建精度,並維持高效率。

### 2.2 Domain Tags

- computer vision
- 3D reconstruction
- SLAM / SfM
- feed-forward geometry models
- test-time training
- large-scale scene understanding

### 2.3 Core Architectures Used

- **VGGT backbone**:作為 Scal3R 的基底 feed-forward 模型,以 DINOv2 encoder 加 24 層 frame-wise 與 global self-attention 交替的 Transformer,直接回歸 camera parameters、depth maps、point clouds 與 tracking feature grid。
- **Global Context Memory (GCM)**:作者提出的核心模組,接在每個 global attention layer 之後(共 4 個),以可學習 gate 向量 $\alpha$ 將 GCM 輸出與原始 token 殘差融合,負責壓縮並保留長距脈絡。
- **Adaptive Memory Unit (AMU)**:GCM 內部的輕量 MLP 子網路,以快權重 $W$ 形式存放上下文,在推論時透過 self-supervised dot-product loss 被線上更新,等同於 TTT 的 fast weights。
- **Test-Time Training (TTT) with large chunks**:沿用並改造 LaCT,將整個 chunk 視為單一更新單位,以提升 GPU 平行度與長序列下的可擴展性。
- **Global Context Synchronization (GCS) via context parallelism**:將分散在多 GPU 上的 chunk 視為 context parallelism 切分,藉由 PyTorch all-reduce 對 AMU 的梯度求和並廣播,實現跨 chunk、跨 GPU 的全域脈絡共享。
- **Chunk-wise alignment & pose-graph refinement**:沿用 VGGT-Long 的重疊區域 Sim(3) 對齊與 retrieval-based loop closure + pose-graph refinement,將各 chunk 預測融合為最終公里級重建。

### 2.4 Core Argument

作者主張:大規模 feed-forward 3D 重建的核心瓶頸並非單純的計算量,而是「全域脈絡的遺失」。在分塊處理(VGGT-Long)中,每個 chunk 獨立推論,缺乏跨段資訊使局部誤差被放大;在 token merging(FastVGGT)中,過度壓縮會破壞細粒度空間線索與長距依賴;傳統 RNN/線性注意力雖具次二次方複雜度,但其固定大小的隱狀態無法承載公里級場景的豐富脈絡。也就是說,問題的根源在於「記憶體容量」與「全域共享機制」同時不足。基於此,作者主張解法必須同時滿足兩個條件:(1) 記憶體本身要有足夠表達力以容納長距資訊,(2) 必須有跨 chunk、跨 GPU 的同步機制讓全域脈絡真正參與每段局部重建。Test-Time Training (TTT) 自然滿足條件 (1)——以一個可在推論時被自監督更新的非線性子網路取代固定隱狀態,將「脈絡」視為一份線上資料集寫入快權重 W;而將大塊 (whole chunk) 視為單一更新單位 (受 LaCT 啟發) 進一步改善 GPU 利用率與可擴展性。為滿足條件 (2),作者把分散到多 GPU 的 chunk 計算視為 context parallelism,藉由 all-reduce 將各 GPU 的 W 梯度求和並廣播,等價於在整段序列上做一次全域更新。如此一來,GCM 提供「容量」、GCS 提供「共享」,兩者結合在保留 VGGT 強幾何推理能力的前提下,使每個 chunk 的局部預測都能享有全域先驗,從而合理地解決長序列下精度與一致性同時退化的問題。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(約 220 words)

論文標題「Scal3R: Scalable Test-Time Training for Large-Scale 3D Reconstruction」直接點出三個關鍵字：scalability、test-time training (TTT)、large-scale 3D reconstruction，把方法手段（TTT）與目標（kilometre-scale 重建）綁在一起，暗示這不是另一個 small-scene feed-forward 改進，而是要處理 long sequence 的「容量」問題。

Abstract 採取「問題—觀察—方法—結果」的標準四段式骨架。第一段先界定任務：從 long video sequence 做大規模 3D scene reconstruction。第二段點出近期 feed-forward reconstruction model（直指 VGGT 一脈）的限制：long sequence 下 memory capacity 不足、無法捕捉 global contextual cues，使 accuracy 與 consistency 退化。第三段提出 motivation 類比：人類會用 global understanding 反過來指導 local perception，從而引出論文核心提案——一個 neural global context representation，能有效壓縮並保留長程 scene information。具體實作是「lightweight neural sub-networks」於 test time 透過 self-supervised objective 快速 adapt，宣稱可顯著放大 memory capacity 而不增加大量 compute overhead。第四段交代實驗範圍與訊號：KITTI Odometry 與 Oxford Spires 等 large-scale benchmark 上達到 leading pose accuracy 與 SOTA 3D reconstruction accuracy，並維持 efficiency，公開 code。

Abstract 的設定為後文鋪了三條伏筆：（1）「memory capacity」與 long-range context 將被形式化為 GCM／AMU 的容量設計；（2）「self-supervised online adaptation」對應到 §3.2 的 TTT 與 §4.2 的 chunk-wise update；（3）「kilometre-scale」與「efficiency」共同要求 chunk + 多 GPU 平行化的 inference pipeline，預告 §4.4。讀者進入 Introduction 時已經知道：論文要在 VGGT-style backbone 上加一個可在 test time 學習的 global memory 模組。

### 3.2 Introduction

(約 700 words)

Introduction 走「動機—現有方法的痛點—關鍵問題—我們的答案—貢獻」結構，把 abstract 的口號落到具體技術論述。

第一段先把 large-scale 3D reconstruction 放到應用脈絡（autonomous driving、robotics mapping、digital twin），並指出與 object-centric 重建的差異：跨 kilometre 場景需對齊 thousands of viewpoints、處理 depth 與 lighting 的劇烈變化、同時保留 global consistency 與 fine local detail。然後批評傳統路線：要麼假設 known intrinsics、要麼依賴 IMU/LiDAR 等 auxiliary sensor 與多階段 pipeline，flexibility 受限。

第二段把焦點切到 feed-forward 路線，特別點名 VGGT：用統一 Transformer 一次預測 camera、depth、point cloud，accuracy 高、cost 低、scaling 強。但隨即點出致命瓶頸——attention 的 quadratic complexity 在 ultra-long sequence 下不可行。第三段比較兩個既有改良：FastVGGT 用 token merging 砍冗餘，但 aggressive compression 丟失 fine-grained spatial cue 與 long-range dependency；VGGT-Long 採 divide-and-conquer，把序列切 overlapping chunks 分別重建再對齊，但每個 chunk 缺 global context，alignment 對 local accuracy 過度敏感，遇到大場景或 sparse 觀測就退化。

第四段提出本文的關鍵問題：3D foundation model 該如何像人類一樣 efficiently retain and leverage long-term contextual cues？答案分兩半：（a）一個能 compress and store long-term context 的 global context representation；（b）一個 efficient aggregation and sharing mechanism，把 context 在 reconstruction 時 exploit 出來。

第五段把上述抽象構想落為 Scal3R：以 VGGT 為骨幹，用 chunk-wise 處理解決 quadratic cost；同時插入一組 online-adapted、lightweight sub-networks，借鑑 subquadratic sequence modeling 的 TTT 路線，在 inference 時透過 self-supervised objective 聚合長程 context。作者強調這個 representation 比 fixed-size hidden state 容量更大，可緩解 over-compression 帶來的 long-range dependency degradation。

第六段補上「光有 store 不夠」的論點，引出 context aggregation mechanism：在 test time 協調多個 sub-networks 的 self-supervised online adaptation，讓 global cue 跨整個 sequence 共享，使 local reconstruction 不再對 sparse、ambiguous view 敏感，並維持 VGGT 的 scalability，使大規模多資料集訓練成為可能。

最後兩段交代實驗範圍與貢獻列表：在 Virtual KITTI 上訓練、在 KITTI 與 Oxford Spires 上做 zero-shot pose estimation 與 3D reconstruction 評估，宣稱 SOTA。三點 contribution 分別對應：（1）Scal3R 框架本身、（2）global context representation + aggregation 的設計、（3）跨 large-scale dataset 的實驗驗證。

Introduction 的鋪陳直接決定了 §3 與 §4 的結構：§3 要先把 VGGT 與 TTT 兩個 building block 講清楚；§4 才能把 GCM 與 GCS 拼上去。

### 3.3 Related Work / Preliminaries

(約 1100 words)

Related Work 切成三條線索，每條線索都收斂到「為什麼現有方法不夠」。第一條 SfM/SLAM：經典 SfM 靠 feature matching、triangulation、bundle adjustment，準但在 textureless 或 repetitive pattern 下退化；學習式擴展提升 robustness 但仍依賴 expensive global optimization；end-to-end 的 differentiable BA 雖去掉 explicit matching，仍受限於 scalability 與 efficiency；視覺 SLAM 雖能 real-time，但多假設 known intrinsic 或 auxiliary sensor，遇 reflective scene 易失效。第二條 feed-forward reconstruction：DUSt3R/MASt3R 開創 RGB-only 直接 regress pointmap，但兩視圖難以 scale；VGGT 為 multi-view SOTA，但 quadratic attention 限制長序列；CUT3R、StreamVGGT、STream3R 等 online variant 引入 memory state token 或 causal Transformer，但 fixed memory size 與有限 causal horizon 仍會 drift；TTT3R 進一步把 memory update 視為 test-time learning，但仍綁在 fixed-size token set。論文在此處明確定位自身：用 scalable global context representation 提供更大的 memory capacity 來處理 long-range dependency。第三條 memory mechanism：Mamba、RWKV、DeltaNet 等 linear-attention RNN 雖效率好，但把全部歷史壓進有限 hidden state，限制了 long-range 模能；TTT 與其後續（Titans、LaCT 等）改成把 recurrent state 換成 online-adapted non-linear network，顯著放大記憶容量；另一支則用 explicit cache/memory bank 顯式儲存歷史 feature，但又面臨 memory growth 與 compute overhead 的工程難題。整段把 Scal3R 放在 TTT-as-memory 路線上的「為大規模 3D」特化版。

Preliminary 接著補齊兩塊基礎。§3.1 VGGT：給定 RGB 序列 $\{I_i\}_{i=1}^N$，$f$ 一次輸出 camera parameter $c_i \in \mathbb{R}^9$、depth $D_i$、point cloud $P_i$、tracking feature grid $T_i$；架構由 DINOv2 encoder 切 patch、24 層交替的 frame-wise 與 global self-attention、以及多個 task head 組成，這個交替設計讓 intra-frame detail 與 inter-frame geometry 都能建模。

§3.2 Test-Time Training：先回顧 RNN 把 context 壓進固定大小 hidden state $h_t$，再以
$$h_t = \sigma(\theta_{ss} h_{t-1} + \theta_{sx} x_t)$$
形式化更新規則，並指出固定容量在 long sequence 下會資訊退化。TTT 的解法是引入 fast weights $W$，在 inner loop 用 self-supervised objective 動態存 context，外層主網路參數則做 stable generalization。每個 token 投影成 $q, k, v$，由 outer loop 學；fast weights $W$ 在 inner loop 透過 update 與 apply 兩動作運作：

$$\textbf{update}: W \leftarrow W - \eta \nabla_W \mathcal{L}(f_W(k), v),$$
$$\textbf{apply}: o = f_W(q).$$

這把 context 視為 unlabeled dataset、把 hidden state 視為一個小模型權重，因此容量遠超 fixed-size vector，又保有 scalability。這兩塊正好對應 §4.1 的 backbone 與 §4.2 的 GCM；讀者讀完 §3 已能預期 Scal3R = VGGT backbone × TTT-style memory，並準備好接受 chunk-level 平行化與 cross-GPU 同步的工程設計。

### 3.4 Method (overview narrative)

(約 1100 words)

Method 的論述邏輯是：先說「為什麼要切 chunk」，再說「切完之後怎麼把 global 找回來」，最後交代「怎麼訓練、怎麼推論」。整體框架預告（§4 開頭與 Figure 2）寫得很清楚：在 VGGT 之上嵌入一個 TTT-based context aggregation mechanism，既保留 VGGT 的 geometric reasoning，又可處理 thousands of input image。

§4.1 Model Overview 先複述 quadratic attention 的不可行，並對 VGGT-Long 的 chunk-only 策略下診斷——chunk 獨立處理就丟了 long-range context，對 local 不一致極為敏感。接著提出總體設計：把整段序列切成 $K$ 個 overlapping chunk $\{I_k\}$，chunk size $M$、overlap $O$，把 chunk 散佈到不同 GPU 平行處理，得到各 chunk 的 $c_k, D_k, P_k$。在 backbone 結構上，沿用 DINOv2 encoder + 交替 attention + 多 head 的 VGGT 架構，但在 global attention layer 之後插入 Global Context Memory (GCM) 模組，全模型共掛 4 個 GCM（後續 supplementary 指出在第 4、11、17、24 層）。每個 GCM 的「記憶體」由若干 Adaptive Memory Unit (AMU) 實作，AMU 是 lightweight neural sub-network，於 inference 時透過 self-supervised update 快速 adapt。GCM 對第 $i$ 個 global attention 輸出 token $\mathcal{X}_k^i$ 採用 gated residual：

$$\text{gate}(\mathrm{GCM}, \mathcal{X}_k^i; \alpha) = \alpha \otimes \mathrm{GCM}(\mathcal{X}_k^i) + \mathcal{X}_k^i,$$

其中 $\alpha \in \mathbb{R}^d$ 為可學習 gate vector，平衡 GCM 輸出與原 token；最終的 alternating attention 整合為 $\bar{\mathcal{X}}_k^i = \text{gate}(\mathrm{GCM}, \text{gattn}(\text{fattn}(\mathcal{X}_k^i)); \alpha) + \mathcal{X}_k^i$，再餵入各 task head。這段的論證重點：簡單的 gated insertion 既不改 VGGT 的 geometric prior，又把 long-range memory 接進去。

§4.2 Test-Time Training as Memory 處理 TTT 在 long context 的 efficiency 痛點：傳統小 batch update 對 GPU utilization 不友善。受 LaCT 啟發，作者把整個 chunk 的 token 視為一次 update unit，做 chunk-wise update，提升 throughput 與 memory capacity。GCM 內部由 Q/K/V projection、做 AMU 用的 compact MLP、以及 output projection 組成；給定 chunk token $\mathcal{X}_k$，先得 $K, V \in \mathbb{R}^{M \times d}$，按照式 (8) 一次性更新 AMU $W$，token-wise learning rate $\eta_i$ 由輸入預測，self-supervised loss 採 dot-product 形式 $\mathcal{L}(f_W(K), V) = \sum_i -f_W(k_i)^\top v_i$（式 9）。更新完後再用 $W$ 對 query $Q$ 做 $f_W(Q)$ 產出 token。這一段把 GCM 跟 TTT 嚴謹地黏起來。

接著的 Global Context Synchronization (GCS) 是把 chunk-local memory 升級為 sequence-wide memory 的關鍵：每張 GPU 處理一個 chunk、各自算自己的 AMU 梯度，再用 all-reduce 把梯度加總、廣播回每張 GPU，所以全 GPU 的 AMU 共享同一份「整段序列」的更新。形式上 $g = \sum_{j=1}^K \nabla_W \sum_{i=1}^M \eta_i \mathcal{L}_i$，把 chunk 平行視為 context parallelism。論文強調這利用 PyTorch 原生 all-reduce primitive，幾乎不增加 communication overhead，卻同時得到 local accuracy、cross-chunk consistency 與 overall reconstruction 三方面的提升。

§4.3 Training 列出 18 個訓練 dataset，覆蓋 indoor/outdoor、synthetic/real、不同尺度；sequential dataset 連抽整段、unordered dataset 抽同場景多視角再 shuffle。Loss 沿用 VGGT 的多任務組合 $\mathcal{L} = \lambda \mathcal{L}_{cam} + \mathcal{L}_{dpt} + \mathcal{L}_{xyz}$。實作上 GCM 與 backbone 端到端聯訓，AdamW、peak lr $1\times 10^{-4}$（GCM）／$1\times 10^{-5}$（backbone）、cosine decay + 2k warm-up、grad clip 1.0、32 張 A800 跑 60k iter ≈ 3 天。為提升 length generalization，每個 iteration 隨機把 32 GPU 分組，組內做 GCS，使有效序列長度在 1–32 chunk 間波動。

§4.4 Inference 把 §4.1–4.3 的設計整理成 pipeline：序列切 overlapping chunk，多 GPU 平行做 forward，GCS 跨裝置同步 context；得到各 chunk 的 3D 結果後，沿用 VGGT-Long 的 overlap 對齊：在重疊區估 similarity transform 做 point-cloud alignment，再融合成 kilometre-scale 重建；對含 revisit 的軌跡，再加 retrieval-based loop candidate 與 pose-graph refinement 以壓 global drift。論文也說明可在單 GPU 序列處理，僅犧牲 inference time。這段把抽象 mechanism 收斂為 reproducible 的工程流程，順勢過渡到實驗章節。

### 3.5 Experiments (overview narrative)

(約 1300 words)

Experiment 章節以三條軸線檢驗論文主張：pose accuracy、3D geometry accuracy 與 ablation；其底層問題是「GCM + GCS 是否真的在 long, large-scale 序列上帶來顯著且可重現的提升，且不犧牲效率？」

§5.1 Pose Accuracy 是論文的火力主場。Dataset 涵蓋 in-domain synthetic Virtual KITTI v2.0.3、out-of-domain real KITTI Odometry（11 段、271–4661 frame、長達 5 km）與 Oxford Spires（6 段、含 challenging loop closure 與 indoor/outdoor 混合）。指標採 Sim(3) 對齊後的 ATE、RRE（°/100m）、RTE（m/100m），同時補充在 ScanNet++、TUM-RGBD、Waymo 上的延伸比較（放在附錄 Table 4）。Baseline 涵蓋三類：VGGT-Long、FastVGGT 等同源改良；CUT3R、STream3R、StreamVGGT、TTT3R 等帶 memory 的 foundation model；MASt3R-SLAM、VGGT-SLAM 等 learning-based SLAM；以及假設 known intrinsic 的傳統 SfM/SLAM（COLMAP、MASt3R-SfM、DROID-SLAM、DPVO++）。

論文用 Table 1 + Figure 3 共同支撐主結論。Table 1 顯示 Scal3R 在 VKITTI2、KITTI、Oxford Spires 三個 dataset 上幾乎橫掃 feed-forward 與 streaming baseline；在最考驗 long-sequence 行為的 KITTI 上，ATE 由 VGGT-Long 的 25.94 大幅降到 14.55，RTE 由 9.67 降到 4.61；Oxford Spires 上 RRE/RTE/ATE 全面領先（7.87/6.55/4.45 vs VGGT-Long 30.91/20.79/15.46）。論述上點名幾個失敗 mode：MASt3R-SLAM、VGGT-SLAM 在 long sequence 直接 tracking failure；FastVGGT 出現 OOM；TTT3R 雖比 CUT3R 進步，仍受 fixed-size memory 拖累；連最強 baseline VGGT-Long 在 KITTI 之外也明顯落後。對傳統路線給出 fair concession：COLMAP 在 Oxford Spires 上很強，因為 feature matching 與 global optimization 條件好，但在更長更大規模的 video benchmark 上退化、且極慢。這形成「我們對 feed-forward 路線是 SOTA，並在合適情境下追上甚至超越古典 SfM」的論述。

Resource comparison 強化「scalable」這個賣點：在 KITTI 03/04/10（avg. 758 frame）上比較 peak GPU memory、總 inference time、FPS，所有方法在 RTX 4090 上跑，僅 FastVGGT 改用 A800。Scal3R 在單 GPU 上可行、memory 控在合理範圍，避開 long-context model 的 memory 爆炸。雖然 DPVO++、CUT3R 等 lightweight online 系統 throughput 較高，但 long sequence 的 accuracy 顯著輸給 Scal3R；COLMAP 比 Scal3R 慢逾 20×。runtime 隨 sequence 長度的擴展與 RPE 穩定性放在 supplementary。

§5.2 Geometry Accuracy 把焦點從 trajectory 移到 point cloud。Dataset 為 ETH3D（11 scene）、Virtual KITTI（50 scene）、Oxford Spires（6 scene），涵蓋 indoor/outdoor、不同 scale；指標為 Chamfer Distance 與 F1，先用 Umeyama 對齊到 ground truth。Table 2 顯示 Scal3R 在三個 dataset 都拿 best：ETH3D CD 0.11/F1 0.91，Oxford Spires 0.96/0.96，VKITTI2 0.40/0.91，相對 VGGT-Long 都有顯著提升。論文補充：tracking failure、OOM、large pose deviation 通常會直接拖垮重建，所以 pose 領先在這裡形成複利。ETH3D 的好結果還做了 transferability 論述——在較短的 indoor 序列也很穩。Figure 4 給定性比較，強調 Scal3R 在大尺度 outdoor 與 indoor local geometry 都更一致。

§5.3 Ablation Study 鎖定兩個設計選擇。第一是 sub-network 的 state size：1M → 2M → 4M，ATE/RTE/RRE 單調改善（4M 達到 0.85/0.84/0.87），佐證「更大 memory capacity → 更好 long-range context」的核心 hypothesis。第二是 global context 機制本身：w/o GCM（去掉 memory）與 w/o GCS（去掉跨 chunk 同步）兩個 ablation 對照 full model；w/o GCM 退化最大（ATE 19.00 vs full 13.70），w/o GCS 次之（15.80），表示 GCM 承擔主要 long-range context 責任，GCS 則負責讓它跨 chunk 傳播。值得注意，左右兩個 block 訓練設定不同，作者明確聲明「兩塊不可直接比較」，避免讀者誤讀數字差異。

整體實驗章節的論述策略是「先打 pose、再打 geometry、最後拆模型」：以 long, large-scale benchmark 作主戰場，用大量強 baseline 排除 foundation model 與 SLAM 兩條路線的競爭，再用 resource 與 ablation 收緊 efficiency 與設計必要性，使 §6 結論能直接宣稱 SOTA pose 與 geometry。

### 3.6 Conclusion / Limitations / Future Work

(約 80 words)

Conclusion 段非常精簡，把 Scal3R 收束為一個 scalable framework：以 neural global context 結合 online-adapted lightweight sub-networks 與 context aggregation，在 long RGB sequence 上維持 long-range dependency；並重申實驗已驗證 SOTA pose 與 3D geometry。論文沒有獨立的 Limitations 與 Future Work 子節，這部分 the paper does not specify。Acknowledgment 列出資金與致謝對象（含 LaCT 一作 Tianyuan Zhang 的討論），補強與 TTT/LaCT 路線的學術連結，但屬於致謝範疇而非研究展望。

## 4. Critical Profile

### 4.1 Highlights

- 在 KITTI Odometry(平均 758 frames)達到 ATE 14.55m,大幅領先次佳的 VGGT-Long(25.94m),且 RRE/RTE 也同步降低(Table 1, p. 6)。
- 在 Oxford Spires 重建 F1 score 達 0.96、Chamfer Distance 0.96,相對 VGGT-Long(F1 0.80、CD 3.41)為一個量級的提升(Table 2, p. 7)。
- 在 ETH3D(室內短序)與 Virtual KITTI2 同樣拿到 F1 0.91,顯示方法不僅適用於公里級場景,也能 transfer 到較短序列(Table 2, p. 7)。
- 單張 RTX 4090 即可推論 KITTI 758-frame 子集,peak memory 10.32GB,而 FastVGGT 需 A800 才能執行(Table 1, p. 6)。
- Runtime 隨 sequence length 近似線性成長:150 frames 51.19s、990 frames 382.80s,FPS 穩定維持在 2.59–2.93(Table 5, p. 16)。
- 較 COLMAP 在相同 KITTI 子集上快約 22 倍(300.76s vs 6614.73s),同時在 KITTI/VKITTI2 的 ATE 顯著更優(Table 1, p. 6)。
- 額外引入的 GCM module 僅 75.55M 參數(0.076B),掛載於 VGGT 的第 4、11、17、24 層 global attention 之後,屬輕量改造(Section A, p. 13)。
- Ablation 證實 GCM 為主要長距記憶來源:移除 GCM 使 ATE 由 13.70 退化至 19.00,移除 GCS 退化至 15.80(Table 3, p. 8)。
- AMU state size 由 1M 增至 4M 帶來一致改善(RRE 1.01→0.87、ATE 0.99→0.85),支持「容量越大、長距資訊保存越好」的設計直覺(Table 3, p. 8)。
- 在較密集的 ScanNet++(ATE 0.08)與 TUM-RGBD(ATE 0.07)亦達到最佳,顯示 global context 機制在 dense video regime 也仍然有效(Table 4, p. 16)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 在序列內出現劇烈光照或顏色變化時,跨 chunk 的對應會失效,GCS 無法可靠對齊(Section C.3, Figure 7, p. 16)。
- 在極端 view sparsity(數十張影像橫跨數百公尺至公里級)下,即使 local 預測也會因幾何約束不足而崩壞(Section C.3, p. 16)。
- 單 GPU 順序執行模式雖可行,但會顯著增加 inference time(Section 4.4, p. 6)。
- 當 feature matching 與 global optimization 條件良好時,COLMAP 仍可在較短序列上具競爭力,Scal3R 在 Oxford Spires 的絕對 ATE 並不勝過 COLMAP(Section 5.1; Table 1, p. 6)。

#### 4.2.2 Phyra-inferred

- Resource 比較(Table 1, p. 6)只在單張 4090 上跑 758-frame KITTI 子集,論文卻自我定位為公里級、上千 frames 的方法;真正大尺度設定(如 KITTI 00 的 4542 frames)的 peak memory 與 wall-clock 從未量測。
- State-size ablation(Table 3 左, p. 8)只掃了 1M/2M/4M 三個點,且 RRE 絕對差 0.14、ATE 差 0.14,樣本太少且差距太小,難以支撐「容量越大越好」作為一條 scaling law。
- 雖以效率為賣點,Scal3R 在 KITTI 子集上實際比 VGGT-Long 慢 1.78×(300.76s vs 168.83s, Table 1, p. 6);論文對「精度提升換取吞吐下降」這個 trade-off 沒有正面討論。
- GCS 在每個包含 GCM 的 layer 都對 AMU 梯度做一次跨 GPU all-reduce,但通訊量、頻寬依賴、以及跨節點(non-co-located)情境下的延遲完全未量化。
- AMU 結構為 $f_W(x) = W_2\bigl(\mathrm{SiLU}(W_1 x) \circ (W_3 x)\bigr)$,本質上是 SwiGLU MLP;論文未提供「相同架構但不做 inner-loop 更新、改為純前向學習」的對照,使「test-time training 帶來的增益」與「單純多塞參數」無法分離(Section A, p. 13)。
- 在 Oxford Spires 的絕對 pose 上 COLMAP ATE 0.15 遠勝 Scal3R 4.45(Table 1, p. 6),但論文以 "leading pose accuracy" 作為總結;此勝負其實限縮於 "RGB-only feed-forward" 子類別,該前提沒有在 abstract 與 introduction 顯著標出。

### 4.3 Phyra's Judgment (summary)

論文成功論證在 chunked feed-forward 3D reconstruction 中,真正的瓶頸是「跨 chunk 的全域脈絡共享」而非單純算力,並用 GCM(容量)+ GCS(共享)兩個機制把這個論點落地為可量測的精度提升。然而方法本身是 VGGT、VGGT-Long、LaCT、TTT 的組合工程化,真正新穎的部分僅在於把 chunk-level all-reduce 視為 context parallelism 並把它接到 TTT 框架上;AMU 的具體形式並非新模組。最關鍵的未解問題是:Scal3R 的勝出究竟來自 "test-time 內迴圈梯度更新" 這個語義,還是只是把一個更大的、可跨 GPU 同步權重的非線性 attention head 加到 VGGT 上——目前的 ablation 無法分辨這兩種解釋。

## 5. Methodology Deep Dive

### 5.1 Method Overview

Scal3R 將 VGGT 的「unified Transformer feed-forward 架構」直接搬過來作為幾何 backbone(DINOv2 patch encoder + 24 層交替注意力 + 多個 prediction heads),核心改動只有兩個:在 24 層 alternating attention 中的 4 層後方插入 **Global Context Memory (GCM)** 模組,並透過 **Global Context Synchronization (GCS)** 將 GCM 的內部「快權重 (fast weights)」更新跨 GPU 同步。整體推論時的執行單位是 **chunk**:輸入 $N$ 張 RGB 圖被切成 $K$ 個帶有 overlap $O$ 的 chunk(每個含 $M$ 張影像),分散到多個 GPU 並行處理。每個 chunk 在自身 GPU 上獨立跑一遍 backbone(包含與其他 chunk 同步的 GCM),最後 chunk 之間透過 VGGT-Long 的 similarity transform 對齊與融合,產生整段序列的 3D 重建。

每個 GCM 模組是一個輕量子網路,在推論期間以自監督目標被更新,扮演 chunk 內 token 的「壓縮記憶」。具體流程是:當某層 global attention 輸出 token $\mathcal{X}_k^i \in \mathbb{R}^{M \cdot K_p \times d}$ 時($K_p$ 為每張圖的 patch 數,$d$ 為 model dim),GCM 將其投影為 $Q, K, V$,把整個 chunk 內的所有 token 視為 **單一 update batch**(受 LaCT 啟發的 large-chunk update),透過 dot-product loss $\mathcal{L} = \sum_i -f_W(k_i)^\top v_i$ 對 AMU 的快權重 $W$ 做一次梯度更新,然後用更新後的 $f_W$ 把 $Q$ 映射為輸出 token,並透過可學習的 gate $\alpha \in \mathbb{R}^d$ 加回 residual stream:$\bar{\mathcal{X}}_k^i = \alpha \otimes \mathrm{GCM}(\mathcal{X}_k^i) + \mathcal{X}_k^i$。AMU 本身是個 compact MLP,paper 在 ablation 中比較 1M / 2M / 4M 三種 state size。

GCS 則是把「multi-chunk 分散在多 GPU」這件事重新詮釋為 **context parallelism**:在每個 GCM update step 上,各 GPU 計算自己 chunk 的本地梯度 $\nabla_W \sum_i \eta_i \mathcal{L}_i$,然後用 PyTorch 的 all-reduce 把 $K$ 個 chunk 的梯度求和並廣播,各 GPU 用同一個聚合梯度去更新各自的 $W$ 副本。由於 $W$ 的初始值同步,且每步聚合梯度也同步,所有 GPU 上的快權重在數學上等價於「在整段序列上做了一次全域更新」。實作上 communication overhead 很小,訓練時隨機把 32 張 A800 切成不同大小的 group(每 group 內做 GCS),讓 effective sequence length 在 1 到 32 chunk 間變動,以提升 length generalization。對齊階段沿用 VGGT-Long:用 overlap region 計算 chunk 間 similarity transform,有 revisit 時加上 retrieval-based loop closure 做 pose-graph refinement。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input RGB sequence I = {I_i}_{i=1..N}
   │  shape: [N, 3, H, W]
   ▼
[Chunk Partitioning] (M = chunk size, O = overlap)
   │  shape per chunk: [M, 3, H, W],  K chunks total
   │  distributed: chunk_k → GPU_k
   ▼
[DINOv2 Patch Encoder]   (per-chunk, on each GPU)
   │  patches: [M, K_p, C]   (K_p = (H/p)·(W/p), p = patch size = ?)
   │  flatten across frames: [M·K_p, C]  ← treat as X_k^0
   ▼
┌──────────────────────────────────────────────────┐
│  ×24 layers of alternating attention             │
│                                                  │
│   X_k^i  ──[Frame Attention fattn]──► ...        │
│         shape: [M, K_p, d]   (intra-frame)       │
│                                                  │
│         ──[Global Attention gattn]──► X̄_k^i     │
│         shape: [M·K_p, d]    (inter-frame)       │
│                                                  │
│   if layer i ∈ {4 selected layers}:              │
│     ┌──────── GCM module ────────┐               │
│     │ X̄_k^i  shape [M·K_p, d]    │               │
│     │   │                        │               │
│     │   ├─►[QKV proj]            │               │
│     │   │   Q,K,V: [M·K_p, d]    │               │
│     │   │   η_i:   [M·K_p]       │               │
│     │   │                        │               │
│     │   ├─►[AMU update]          │               │
│     │   │   W ∈ ℝ^H_state        │               │
│     │   │   (H_state = 1M/2M/4M) │               │
│     │   │   ── all-reduce(∇W) ──►│  GCS across   │
│     │   │                        │  K GPUs       │
│     │   │                        │               │
│     │   ├─►[Apply]               │               │
│     │   │   o = f_W(Q): [M·K_p,d]│               │
│     │   │                        │               │
│     │   └─►[Output proj + gate]  │               │
│     │       α ⊗ GCM(X̄) + X̄       │               │
│     │       shape: [M·K_p, d]    │               │
│     └──────────────────────────────┘             │
│                                                  │
│   X_k^{i+1}  shape: [M·K_p, d]                   │
└──────────────────────────────────────────────────┘
   │
   ▼
[Output Heads]   (per chunk, per frame)
   ├─► Camera head  c_k:  [M, 9]
   ├─► Depth head   D_k:  [M, 1, H, W]
   ├─► Pointmap     P_k:  [M, 3, H, W]
   └─► Feature grid T_k:  [M, C, H, W]
   │
   ▼
[Chunk-Wise Alignment]   (VGGT-Long-style, on single GPU)
   │  overlap region → Sim(3) transform per chunk pair
   │  loop closure (retrieval) + pose-graph refinement
   ▼
Final reconstruction: aligned poses + fused point cloud
   shape: [N, 9] poses  +  fused [≈N·H·W, 3] point cloud
```

註:`K_p` 為每張影像的 patch 數量,`p` 為 DINOv2 patch size,`d` 為 backbone hidden dim,paper 沒在方法章節給出具體數值(見 §5.3 各模組的 Implementation Details)。

### 5.3 Per-Module Breakdown

#### 5.3.1 Chunk Partitioning

**Function:** 將 long sequence 切成有 overlap 的 chunk,使每個 chunk 可以被單張 GPU 處理,同時 overlap 提供後續對齊所需的共視 token。

**Input:**
- Name: $I = \{I_i\}_{i=1}^N$
- Shape: `[N, 3, H, W]`
- Source: 原始 RGB 影片序列

**Output:**
- Name: $\{I_k\}_{k=1}^K$,$I_k = \{I_{(k-1)(M-O)+1}, \dots, I_{(k-1)(M-O)+M}\}$
- Shape: 每個 chunk `[M, 3, H, W]`,共 $K$ 個 chunk
- Consumer: 每個 chunk 分配到一張 GPU,送入 DINOv2 encoder

**Processing:**

依照 chunk 大小 $M$ 和 overlap $O$,沿時間軸滑動切片,等同於 stride 為 $M-O$、window 為 $M$ 的 sliding window。Chunk 之間以 round-robin 方式分配到不同 GPU,**訓練時** 還會把 32 張 GPU 隨機分成多個 group,讓有效序列長度從 1 到 32 chunk 間變動。

**Key Formulas:** 無封閉形式公式;就是 sliding window 切片。

**Implementation Details:**

Paper 沒有在方法章節給出 $M$、$O$ 的具體數值。可以推測 chunk size 與 VGGT-Long 接近(約 32 frames),但需查 supplementary。**訓練資源**為 32 張 A800,訓練 60k iterations(約 3 天)。

#### 5.3.2 DINOv2 Patch Encoder

**Function:** 將每張 RGB 圖 patchify 並提取 per-frame token 特徵,作為 backbone 的輸入。

**Input:**
- Name: $I_k$
- Shape: `[M, 3, H, W]`
- Source: Chunk Partitioning

**Output:**
- Name: $F_k = \bigcup_{i \in \text{chunk}} F_i$,$F_i \in \mathbb{R}^{K_p \times C}$
- Shape: `[M, K_p, C]`,展平為 `[M·K_p, C]` 作為下層 token
- Consumer: 第一層 alternating attention block

**Processing:**

沿用 VGGT 的設定:DINOv2 ViT 把每張影像切成 patch,經 ViT trunk 取出 per-patch token。Token 來自 DINOv2 預訓練特徵,因此 channel 數 $C$ 由 DINOv2 model size 決定。

**Key Formulas:** 無新公式,即標準 ViT patch embedding。

**Implementation Details:**

Paper 引用 DINOv2 (Caron et al., ICCV 2021) 但沒指明 backbone 大小(ViT-S/B/L/g)。Patch size $p$、token 維度 $C$、$K_p$ 的具體數值在 §4 中均未出現,需要查 supplementary 或推測沿用 VGGT 的設定。

#### 5.3.3 Alternating Attention Block (Frame + Global)

**Function:** 在 backbone 中交替使用 frame-wise self-attention(intra-frame 細節)與 global self-attention(inter-frame 幾何一致性),共 24 層,是 VGGT 的幾何推理主體。

**Input:**
- Name: $\mathcal{X}_k^i$
- Shape: `[M·K_p, d]` (frame-wise 階段會 reshape 成 `[M, K_p, d]`)
- Source: 上一層 attention block 或 patch encoder

**Output:**
- Name: $\bar{\mathcal{X}}_k^i$
- Shape: `[M·K_p, d]`
- Consumer: 下一層 attention block,或 GCM 模組(若該層接 GCM)

**Processing:**

每層先做 **frame attention** $\text{fattn}(\cdot)$ —— 對每張影像內部的 $K_p$ 個 patch token 做 self-attention,捕捉 intra-frame 細節;再做 **global attention** $\text{gattn}(\cdot)$ —— 把 chunk 內所有 $M \cdot K_p$ 個 token 拉平做 self-attention,捕捉 inter-frame 幾何一致性。Residual connection 串起兩個 sub-block:

$$
\bar{\mathcal{X}}_k^i = \text{gattn}\bigl(\text{fattn}(\mathcal{X}_k^i)\bigr) + \mathcal{X}_k^i
$$

當該層後方接 GCM 模組時,公式變為:

$$
\bar{\mathcal{X}}_k^i = \text{gate}\bigl(\mathrm{GCM}, \text{gattn}(\text{fattn}(\mathcal{X}_k^i)); \alpha\bigr) + \mathcal{X}_k^i
$$

**Key Formulas:** 見上。

**Implementation Details:**

24 層中只有 4 層後方接 GCM(paper 第 5 頁文末說明)。Paper 沒具體列出是哪 4 層(例如 layer 6/12/18/24 還是其它配置),也沒給 attention head 數、$d$、FFN 寬度。

#### 5.3.4 Global Context Memory (GCM) Module

**Function:** 用一個會在推論時被 self-supervised 更新的輕量神經網路 (AMU) 充當「壓縮記憶」,將 chunk 內所有 token 的脈絡寫入快權重 $W$,再用更新後的 $W$ 把 query 投影為帶有 chunk 上下文的輸出 token。

**Input:**
- Name: $\mathcal{X}_k$ (= 該層 global attention 的輸出)
- Shape: `[M·K_p, d]`
- Source: 接在某層 global attention 之後

**Output:**
- Name: $\mathrm{GCM}(\mathcal{X}_k)$,經 gate 後再 residual 加回
- Shape: `[M·K_p, d]`
- Consumer: 該層的 residual stream(送入下一層 attention)

**Processing:**

1. **QKV projection**(linear layer):從 $\mathcal{X}_k$ 投出 $Q, K, V \in \mathbb{R}^{M \cdot K_p \times d}$。
2. **AMU update**(內 loop):用 $K, V$ 算 dot-product loss(eq. 9),對 $W$ 做一次梯度下降(eq. 8)。
3. **GCS all-reduce**:把本地梯度跨 GPU 求和廣播,所有 chunk 共用聚合梯度更新 $W$(見 §5.3.5)。
4. **Apply**:用更新後的 $f_W$ 把 $Q$ 映射為輸出 token $o = f_W(Q) \in \mathbb{R}^{M \cdot K_p \times d}$。
5. **Output projection + gate**:經輸出 linear,乘上可學習的 gate $\alpha \in \mathbb{R}^d$,再 residual 加回原 token。

**Key Formulas:**

更新規則(eq. 8, 9):

$$
W \leftarrow W - \nabla_W \sum_{i=1}^{M} \eta_i \, \mathcal{L}\bigl(f_W(k_i), v_i\bigr)
$$

$$
\mathcal{L}\bigl(f_W(K), V\bigr) = \sum_{i=1}^{M} -f_W(k_i)^\top v_i
$$

Gate 與 residual(eq. 5):

$$
\text{gate}(\mathrm{GCM}, \mathcal{X}_k^i; \alpha) = \alpha \otimes \mathrm{GCM}(\mathcal{X}_k^i) + \mathcal{X}_k^i
$$

**Implementation Details:**

- 每個 GCM 包含三層:QKV projection (linear)、AMU(compact MLP,作為快權重 $W$)、output projection。
- AMU state size $H_{\text{state}}$:ablation 比較 1M / 2M / 4M 參數,4M 最佳。
- Token-wise learning rate $\eta_i$ 從輸入 token 預測得來(具體 head 結構 paper 沒寫)。
- Eq. 8 中的 $M$ 在 paper 文字中先後被稱為「chunk size (M images)」和「token-wise」,實際展開應為 $M \cdot K_p$ tokens 一次更新;這是 paper 的 notation overloading,本筆記以 token 數為準。
- Loss 採 LaCT/TTT 風格的 dot-product loss(沒用 cosine 或 MSE)。

#### 5.3.5 Global Context Synchronization (GCS)

**Function:** 把分散在 $K$ 張 GPU 上、各自在 chunk 內計算的本地 GCM 梯度 all-reduce 求和並廣播,讓所有 GPU 上的 $W$ 副本在每步更新後保持一致,等價於在整段序列上做一次全域 update。

**Input:**
- Name: 各 GPU 上的 local gradient $\nabla_W \sum_{i=1}^M \eta_i \mathcal{L}_i$
- Shape: 與 $W$ 相同(`[H_state]`)
- Source: 各 GPU 內 GCM 的反向傳播

**Output:**
- Name: 聚合梯度 $g$,廣播後在每張 GPU 上更新 $W$
- Shape: 與 $W$ 相同
- Consumer: 各 GPU 的 AMU update step

**Processing:**

1. 各 GPU 計算本地 chunk 的梯度 $g_j = \nabla_W \sum_{i=1}^M \eta_i \mathcal{L}_i$。
2. 透過 PyTorch all-reduce 對 $K$ 張 GPU 的梯度求和:$g = \sum_{j=1}^K g_j$(eq. 10)。
3. 把 $g$ 廣播回所有 GPU,各 GPU 用同一個 $g$ 更新自己的 $W$ 副本。
4. 因為 $W$ 初始同步、每步聚合梯度也同步,所有 GPU 上的 $W$ 始終一致,等同於在整段序列上做一次全域更新。

**Key Formulas:**

$$
g = \nabla_W \sum_{j=1}^{K} \sum_{i=1}^{M} \eta_i \mathcal{L}_i = \sum_{j=1}^{K} \nabla_W \sum_{i=1}^{M} \eta_i \mathcal{L}_i
$$

**Implementation Details:**

- 用 PyTorch 內建的 all-reduce primitive,paper 強調 communication overhead 很小。
- **訓練時** 把 32 張 A800 隨機分成多個 group,每 group 內單獨做 GCS,使 effective sequence length 在 1 到 32 chunk 間變動。
- **推論時** 也照樣執行 GCS;若只有單張 GPU,則順序處理 chunks 並犧牲速度。

#### 5.3.6 Output Heads + Chunk-wise Alignment

**Function:** 從每個 chunk 的最終 token 預測 camera、depth、pointmap、feature grid,然後跨 chunk 對齊融合成整段序列的 3D 重建。

**Input:**
- Name: 最後一層 attention 後的 token $\bar{\mathcal{X}}_k^{24}$
- Shape: `[M·K_p, d]`
- Source: backbone 最後一層

**Output:**
- Name: $(c_k, D_k, P_k, T_k)$ per chunk,然後 aligned trajectory + fused point cloud
- Shape:
  - $c_k$: `[M, 9]`(camera intrinsic + extrinsic)
  - $D_k$: `[M, 1, H, W]`
  - $P_k$: `[M, 3, H, W]`
  - $T_k$: `[M, C, H, W]`
  - 對齊後:`[N, 9]` 全序列 pose + 融合點雲
- Consumer: 下游評估(pose accuracy / Chamfer distance / F1)

**Processing:**

1. **Output heads**:沿用 VGGT 的多任務 prediction heads(camera head、depth head、pointmap head、tracking feature head),每個 head 是輕量 conv/MLP,從 token 解出對應結構。
2. **Chunk-wise alignment**(VGGT-Long-style):利用相鄰 chunk 的 overlap region $O$ 個共視 frame 算 Sim(3) similarity transform,把所有 chunk 對齊到統一座標系,最後融合 pointmap。
3. **Loop closure**(僅當有 revisit):用 retrieval-based loop candidate discovery + pose-graph refinement 減少全域漂移。

**Key Formulas:**

VGGT 的 unified mapping(eq. 1):

$$
f\bigl(\{I_i\}_{i=1}^N\bigr) = \{\boldsymbol{c}_i, D_i, P_i, T_i\}_{i=1}^N
$$

Multi-task training loss(eq. 11):

$$
\mathcal{L} = \lambda \mathcal{L}_{cam} + \mathcal{L}_{dpt} + \mathcal{L}_{xyz}
$$

**Implementation Details:**

- $\mathcal{L}_{cam}$ 是 camera head 的 L1 loss;$\mathcal{L}_{dpt}, \mathcal{L}_{xyz}$ 結合 confidence-weighted term 與 gradient-based regularisation,paper 沒給 $\lambda$ 的具體數值。
- Optimizer: AdamW,GCM lr = $1 \times 10^{-4}$,backbone lr = $1 \times 10^{-5}$,cosine decay + 2k warm-up,gradient clipping max norm 1.0。
- 對齊:用 Umeyama 算法做 Sim(3) 估計;loop closure 的 retrieval 細節 paper 沒描述。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Virtual KITTI (v2.0.3) [7] | Pose accuracy + 3D reconstruction | 50 outdoor sequences, 223–837 frames, 52–711 m | Train + Test |
| KITTI Odometry [22] | Pose accuracy (zero-shot) | 11 urban driving sequences, 271–4,661 frames, 0.39–5.07 km | Test only |
| Oxford Spires [70] | Pose accuracy + 3D reconstruction (zero-shot) | 6 sequences with loop closures, 351–787 frames, 280–773 m | Test only |
| ETH3D [60] | 3D reconstruction (zero-shot) | 11 indoor/outdoor scenes, 14–76 frames | Test only |
| ScanNet++ [92] | Pose accuracy (supplementary) | 5 sequences, avg. 924 frames | Test only |
| TUM-RGBD [64] | Pose accuracy (supplementary) | All scenes, avg. 926 frames | Test only |
| Waymo [66] | Pose accuracy (supplementary) | 9 outdoor driving scenes, avg. 198 frames | Test only |
| Co3Dv2 [55], BlendedMVS [91], DL3DV [39], MegaDepth [36], WildRGB [86], ScanNet++ [92], HyperSim [56], Mapillary [2], Replica [63], MVS-Synth [28], Aria Synthetic Environments [46], Aria Digital Twin [46], Taskonomy [95], Tartanair [82], Mapfree [3], SceneNet RGB-D [42], MatrixCity [35] | Multi-task pretraining (depth, point, pose) | Mixed indoor/outdoor, synthetic/real, varied scales | Train only |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| ATE (m) | Absolute Trajectory Error after $\mathrm{Sim}(3)$ alignment with ground truth | yes |
| RRE ($^{\circ}$/100m) | Relative Rotation Error normalized by trajectory length | yes |
| RTE (m/100m) | Relative Translation Error normalized by trajectory length | yes |
| Chamfer Distance (CD) | Average of accuracy $\mathrm{dist}(\mathcal{P}\to\mathcal{G})$ and completeness $\mathrm{dist}(\mathcal{G}\to\mathcal{P})$ on aligned point clouds | yes |
| F1 score | Harmonic mean of precision and recall under a dataset-specific distance threshold $d$ (ETH3D: 0.25, VKITTI: 1.0, Oxford Spires: 4.0) | yes |
| RPE (m) | Relative Pose Error reported in the runtime-scaling analysis (supplementary Table 5) | no |
| Peak GPU Memory | Peak memory usage during inference on KITTI seq. 03/04/10 | no |
| Inference Time / FPS | Total wall-clock and throughput on KITTI seq. 03/04/10 (avg. 758 frames) | no |

### 6.3 Training and Inference Settings

- **Hardware (main training):** 32 NVIDIA A800 GPUs; training completes in roughly 3 days over 60k iterations.
- **Optimizer:** AdamW with peak learning rate $1\times10^{-4}$ for the GCM modules and $1\times10^{-5}$ for the VGGT backbone; cosine decay with a 2k-iteration linear warm-up; gradient clipping at max norm 1.0.
- **Batch / sequence construction:** at each iteration the 32 GPUs are randomly partitioned into groups; each group runs Global Context Synchronization (GCS) only within the group, yielding variable effective sequence lengths from 1 to 32 chunks for length generalization.
- **Loss:** multi-task objective $\mathcal{L} = \lambda \mathcal{L}_{cam} + \mathcal{L}_{dpt} + \mathcal{L}_{xyz}$ following VGGT [78]; $\lambda$ 的具體數值 the paper does not specify.
- **Inference (main):** chunk size $M = 60$, overlap $O = 30$ across all main benchmarks (the same setting is also applied to the VGGT-Long baseline for fairness); on ScanNet++ and TUM-RGBD the supplementary uses $M=120$, $O=60$; on Waymo $M=60$, $O=30$. Chunks are distributed across GPUs and run in parallel; alignment follows VGGT-Long [17] with retrieval-based loop discovery and pose-graph refinement on revisit trajectories. Single-GPU sequential execution is supported but slower.
- **GCM module:** 4 GCM modules attached after the 4th, 11th, 17th, and 24th global attention layers (Appendix A); each AMU is a 3-layer MLP with gating $f_W(x) = W_2\bigl(\mathrm{SiLU}(W_1 x)\circ(W_3 x)\bigr)$; number of heads $n_h = 1$, scaling factor $k = 4$; total newly added parameters 75.55M (≈0.076B).
- **Resource benchmark hardware:** all methods run on a single RTX 4090 except FastVGGT, which requires an A800.
- **Ablation training:** state-size ablations on 16 A800 GPUs for 60k iterations; global-context ablations on 8 A800 GPUs for 60k iterations; both use a subset of the training mix that excludes the object-centric WildRGB, Co3Dv2, and Aria Digital Twin (Appendix B.2).

### 6.4 Main Results

Pose accuracy (Table 1, dataset-average ATE in m; failed scenes assigned the worst valid score):

| Method | VKITTI2 ATE ↓ | KITTI ATE ↓ | Oxford Spires ATE ↓ | Notes |
|---|---|---|---|---|
| MASt3R-SLAM [44] | 78.33 | 191.71 | 29.22 | learning-based SLAM |
| VGGT-SLAM [41] | 17.18 | 214.88 | 26.85 | |
| StreamVGGT [101] | 68.97 | 226.15 | 34.35 | streaming |
| STream3R [33] | 70.87 | 227.77 | 34.65 | causal Transformer |
| CUT3R [80] | 50.75 | 209.78 | 28.01 | memory-token model |
| TTT3R [11] | 23.49 | 177.73 | 31.57 | TTT-based memory |
| FastVGGT [61] | 21.83 | 206.69 | 31.18 | token merging |
| VGGT-Long [17] | 1.03 | 25.94 | 15.46 | strongest feed-forward baseline |
| COLMAP [59] | 9.09 | 37.79 | 0.15 | classical SfM, very slow |
| MASt3R-SfM [34] | 40.57 | 171.28 | 25.83 | |
| DROID-SLAM† [71] | 2.47 | 50.71 | 23.97 | requires intrinsics |
| DPVO++† [40] | 0.48 | 52.69 | 29.17 | requires intrinsics |
| **Ours (Scal3R)** | **0.85** | **14.55** | **4.45** | best on all three; second-best RRE on VKITTI2 |

3D reconstruction (Table 2):

| Method | ETH3D CD ↓ / F1 ↑ | Oxford Spires CD ↓ / F1 ↑ | VKITTI2 CD ↓ / F1 ↑ |
|---|---|---|---|
| VGGT-Long [17] | 0.24 / 0.84 | 3.41 / 0.80 | 1.78 / 0.70 |
| FastVGGT [61] | 0.50 / 0.70 | 2.76 / 0.76 | 1.73 / 0.67 |
| TTT3R [11] | 0.43 / 0.59 | 9.03 / 0.31 | 3.49 / 0.49 |
| CUT3R [80] | 0.41 / 0.60 | 6.93 / 0.45 | 5.67 / 0.39 |
| **Ours (Scal3R)** | **0.11 / 0.91** | **0.96 / 0.96** | **0.40 / 0.91** |

Resource cost on KITTI 03/04/10 (avg. 758 frames, single RTX 4090 unless noted): Scal3R uses 10.32 GB peak memory and 300.76 s total time at 2.53 FPS — moderate memory, slower than lightweight online systems (DPVO++ 35.35 FPS, CUT3R 32.87 FPS) but ~22× faster than COLMAP (6614.73 s) and avoiding the OOM that FastVGGT hits on a 4090. Supplementary Table 4 additionally reports best ATE on ScanNet++ (0.08) and TUM-RGBD (0.07) and a competitive 1.52 on Waymo.

### 6.5 Ablation Studies

- **State size of the AMU sub-networks** (Table 3 left): increasing the GCM state size from 1M $\to$ 2M $\to$ 4M monotonically improves ATE (0.99 $\to$ 0.93 $\to$ 0.85), RTE (1.01 $\to$ 0.91 $\to$ 0.84), and RRE (1.01 $\to$ 0.95 $\to$ 0.87). This is a *diagnostic* experiment that directly tests the central claim that larger non-linear memory better preserves long-range context, and the monotone trend supports it.
- **Global context mechanism** (Table 3 right, complementary long-sequence subset): removing the cross-chunk synchronization (`w/o GCS`) raises ATE from 13.70 to 15.80, and removing the entire memory module (`w/o GCM`) raises ATE further to 19.00 with RTE 7.03 and RRE 1.30. The decomposition is *diagnostic* — it isolates the two proposed components and shows GCM carries the primary long-range signal while GCS contributes additional cross-chunk propagation.
- **Caveat on comparability:** the paper explicitly notes that the two ablation blocks are not directly comparable (different training sets, different GPU counts, different evaluation subsets — Appendix B.2). This means absolute numbers across the two blocks should not be cross-read, only intra-block trends.
- **Missing diagnostic ablations:** chunk size $M$ and overlap $O$, the gate $\alpha$, the number of GCM modules (4) and their attached layers, the scaling factor $k = 4$, the number of heads $n_h = 1$, and the choice of dot-product self-supervised loss are all design choices that are *not* ablated. The runtime-scaling table (Table 5) is closer to a sanity check than a diagnostic — it shows RPE stays in 0.07–0.08 m as length grows from 150 to 990 frames, but does not isolate which component delivers that stability.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — VGGT-Long [17], the strongest published feed-forward baseline, is included alongside FastVGGT, TTT3R, CUT3R, STream3R, and learning-based SLAMs, and Scal3R outperforms all on the three primary benchmarks (Table 1).
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — pose evaluated on VKITTI2, KITTI, Oxford Spires, plus supplementary ScanNet++, TUM-RGBD, Waymo; reconstruction evaluated on ETH3D, Oxford Spires, VKITTI2 (Tables 1, 2, 4).
- [covered] Has ablations that diagnose the new components (not just sanity checks) — Table 3 ablates GCM state size and separately removes GCM and GCS, isolating the two contributions claimed in the method.
- [partial] Has a scaling study (size, length, or compute) — supplementary Table 5 reports runtime/RPE scaling with sequence length (150 $\to$ 990 frames), and Table 3 sweeps GCM state size 1M/2M/4M; no scaling on backbone size, GPU count, or training compute is reported.
- [covered] Has an efficiency / wall-clock comparison — Table 1 reports peak memory, total time, and FPS on KITTI 03/04/10 against all baselines; Table 5 adds runtime scaling with length.
- [missing] Reports variance / standard deviation / multiple seeds where relevant — all reported numbers are single-run point estimates; no seed averaging or confidence intervals appear in any table.
- [partial] Releases code / weights / data sufficient for reproducibility — the abstract advertises a project page at `https://zju3dv.github.io/scal3r`, but the paper does not specify whether trained weights, training code, or evaluation scripts are released; the training data list is fully enumerated (Sec. 4.3).

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 公里級 RGB-only 重建** — Supported。Figure 1 與 Oxford Spires 上 280–773m 的軌跡展示具體達成尺度;Table 1/2 在 Oxford Spires 上的 ATE 4.45 與 F1 0.96 為直接量化證據。
- **C2: 神經式 global context representation 能壓縮並保留長距資訊** — Partially supported。Table 3 右側 "w/o GCM" 使 ATE 從 13.70 退化至 19.00,證實 GCM 重要;但缺少對照實驗確認效果來自 inner-loop 更新而非單純多 75M 參數,因此「神經 + 線上自監督」這個語義成份未被獨立驗證。
- **C3: GCS 把 chunk-wise 計算視為 context parallelism 並有效共享脈絡** — Supported but small effect。"w/o GCS" 使 ATE 由 13.70 升至 15.80(差 2.10),相對 GCM 的貢獻 5.30 而言為次要組件;論文的論述等比看待兩者,稍嫌過度。
- **C4: SOTA pose accuracy** — Supported within RGB-only feed-forward category。Table 1 與 Table 4 的比較對象多為同類 baseline,在這個範圍內 Scal3R 一致勝出;但 COLMAP 在 Oxford Spires 與 ScanNet++ 仍是 ATE 上的強對手,論文的「SOTA」應理解為類別內冠軍。
- **C5: SOTA 3D reconstruction accuracy 同時保有效率** — Supported on accuracy, overclaimed on efficiency。Table 2 的 F1 與 CD 全面領先;但 Table 1 顯示對最相近的 VGGT-Long,Scal3R 是「更準但更慢、記憶體類似」,「保有效率」更接近「未顯著退化」而非「兼具最佳吞吐」。

### 7.2 Fundamental Limitations of the Method

第一,AMU 的具體形式 $f_W(x) = W_2\bigl(\mathrm{SiLU}(W_1 x) \circ (W_3 x)\bigr)$ 是一個 SwiGLU MLP,inner-loop 更新規則是對 $\sum_i -f_W(k_i)^\top v_i$ 做梯度下降。這在數學上等價於把一個非線性 fast-weight attention head 接到 VGGT,並用 chunk-level 自監督 loss 線上調整其 key–value 映射。它沒有引入新的 3D 幾何先驗,只是擴大了「可在序列上動態調整的參數量」。因此方法的天花板由 VGGT backbone 的幾何推理力決定,GCM 是在 backbone 給出的特徵分佈內做更好的長距聚合,而非彌補 backbone 的幾何盲點。

第二,GCS 仰賴在每個 GCM-augmented layer 對 AMU 梯度做一次跨 GPU all-reduce(Eq. 10, p. 5)。這個設計把 inference 的 wall-clock 與 GPU 數量、互連拓撲耦合;在單機多卡且 NVLink 連通的訓練/評測環境中通訊近乎免費,但跨節點部署時 all-reduce 延遲會成為主導,Scal3R 的 "scalable" 並未在此情境下被驗證。

第三,失敗模式(Figure 7, p. 16)顯示在劇烈光照變化下對應失效。GCM 操作的是 frozen DINOv2 encoder 的特徵,當 encoder 本身對 appearance shift 不穩定時,inner-loop 的梯度步驟並不能合成不存在的對應訊號;瓶頸已從「記憶體容量」轉移到「特徵穩定性」,而後者方法本身無法處理。

第四,長序列重建仍依賴 VGGT-Long 的 chunk-wise alignment 與 retrieval-based loop closure 做最終融合(Section 4.4, p. 6)。GCM 並不執行 loop closure,因此在沒有 revisit 的單向長軌跡上,累積漂移仍透過 chunk-by-chunk Sim(3) 對齊累加;global context 提升的是局部一致性而非全域閉環。

### 7.3 Citations Worth Tracking

- **LaCT [100]** (Zhang et al., 2025, "Test-time training done right") — Scal3R 的 chunk-as-update-unit 設計直接源於此,理解 LaCT 的並行化分析才能看懂 Scal3R 為何能在 GPU 上跑得動 inner loop。
- **TTT3R [11]** (Chen et al., 2025) — 與 Scal3R 同期、最直接的 baseline,論文以「fixed-size token set 不足」作為差異化主軸,讀完才能判斷 Scal3R 真正的 delta 是否如其所宣稱。
- **VGGT-Long [17]** (Deng et al., 2025) — Scal3R 的 chunking、alignment、loop closure 流程幾乎全盤繼承,讀此論文有助於把 Scal3R 的貢獻切離為「architectural」與「pipeline-inherited」兩部分。
- **VGGT [78]** (Wang et al., CVPR 2025) — base model,定義了 alternating frame/global attention 與 output heads,Scal3R 在其上嫁接 GCM。
- **Test-time regression unifying framework [79]** (Wang et al., 2025) — 將 TTT 與 fast-weight attention、associative memory 統一在同一座標系下,提供判斷 GCM 是否「實質上等價於某種已知 attention」的理論工具。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在不切 chunk、單 GPU 順序執行下,Scal3R 處理 KITTI 00(4542 frames)的 peak memory 與 wall-clock 為何?目前 Table 1 與 Table 5 都未涵蓋這個極限情境。
- [ ] 若把 AMU 改為「相同架構、相同參數量,但不做 inner-loop 更新,只在 outer loop 端到端訓練」,ATE/RRE 會退化多少?這是分離「TTT 語義」與「多塞參數」唯一直接的對照。
- [ ] Chunk size $M$ 與 overlap $O$ 的敏感度為何?ScanNet++/TUM 用 $M=120$、KITTI 用 $M=60$,這是被調出來的還是有理論依據?
- [ ] GCS 的 all-reduce 在跨節點(InfiniBand 而非 NVLink)場景下,通訊延遲佔 inference 時間的比例為何?這決定 "scalable" 是否能延伸到資料中心級部署。
- [ ] AMU 的最小可用 state size 為多少?是否存在一個閾值,低於此值 GCS 帶來的同步不再有正面效益?
- [ ] DINOv2 encoder 凍結是否就是 Figure 7 失敗模式的根本原因?若把 encoder 一同 fine-tune 並加入 appearance augmentation,跨 chunk 對應穩定性能否改善?
- [ ] 在 Oxford Spires 的長閉環序列上,最終 ATE 中由 GCM 帶來的局部一致性貢獻、與由 retrieval-based loop closure + pose-graph refinement 帶來的全域對齊貢獻,各佔多少?

### 8.2 Improvement Directions

1. **新增「fixed-weight AMU」對照組**(可行性最高):保留 GCM 模組架構與參數量,但在 inference 時關閉 inner-loop 梯度更新,只用 outer-loop 學到的 $W_1, W_2, W_3$。若效果掉得有限,代表 Scal3R 的增益主要來自架構與 GCS,而非「test-time training」;這個結果無論正反都對社群極有價值。
2. **加入 chunk-size sensitivity sweep**(可行性高):在固定模型權重下,把 $M$ 從 30 掃到 240、$O$ 從 0 掃到 $M/2$,報告 ATE 與 wall-clock 的 Pareto 曲線。這可以驗證論文選的 $M=60/120$ 是否為 sweet spot,還是僅止於 baseline 比照公平。
3. **量化 GCS 通訊開銷並嘗試階層化 all-reduce**(中等可行性):先 profile 每層 GCM 的 all-reduce 時間,再用 ring/tree all-reduce 或 hierarchical reduce-scatter + all-gather 取代直接 all-reduce,讓跨節點延遲下降。
4. **在 outer loop 同步 fine-tune DINOv2 encoder 並加入光照/色彩 augmentation**(中等可行性):針對 Figure 7 的 failure mode,讓 encoder 學到對 appearance 不變的特徵,再給 GCM 接手做長距聚合,從根本上解決跨 chunk 對應不穩。
5. **把 loop closure 內化進 GCM**(較難):目前 retrieval + pose-graph refinement 是 post-hoc 步驟,可嘗試讓 AMU 的 key/value 帶有 global descriptor,並在 GCS 同步時加入「跨 chunk 相似度檢索」做為 inner-loop 額外損失,使 GCM 自身具備閉環能力,而非依賴外掛模組。
