<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# RoundPipe — Efficient Training on Multiple Consumer GPUs with RoundPipe

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | RoundPipe |
| Paper full title | Efficient Training on Multiple Consumer GPUs with RoundPipe |
| arXiv ID | 2604.27085 |
| Release date | 2026-04-29 |
| Conference/Journal | arXiv preprint (cs.DC) |
| Paper link (abs) | https://arxiv.org/abs/2604.27085 |
| PDF link | https://arxiv.org/pdf/2604.27085 |
| Code link | https://github.com/ITcarrot/RoundPipe |
| Project page | https://itcarrot.github.io/RoundPipe/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Yibin Luo | Tsinghua University | https://storage.cs.tsinghua.edu.cn/~lyb/ | first author |
| Shiwei Gao | Tsinghua University | https://storage.cs.tsinghua.edu.cn/~gsw/ | co-author |
| Huichuan Zheng | Tsinghua University | — | co-author |
| Youyou Lu | Tsinghua University | https://storage.cs.tsinghua.edu.cn/~lu/ | advisor |
| Jiwu Shu | Tsinghua University | https://storage.cs.tsinghua.edu.cn/~jiwu-shu/ | senior advisor / corresponding author |

### 1.2 Keywords

pipeline parallelism, consumer GPU training, CPU offloading, round-robin scheduling, asymmetric stage splitting, near-zero bubble, LLM fine-tuning, PCIe-bound systems

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Mobius (Feng et al., ASPLOS'23) | baseline | PP+offloading on commodity GPUs; the closest predecessor that RoundPipe directly targets and outperforms. |
| ZeRO-Infinity (Rajbhandari et al., SC'21) | baseline | DP-based parameter/optimizer offload; representative of collective-heavy DP approach RoundPipe replaces. |
| ZeRO-Offload (Ren et al., ATC'21) | predecessor | Foundational CPU-offload optimizer; provides the host-side asynchronous optimizer pattern adopted. |
| GPipe (Huang et al., NeurIPS'19) | predecessor | Classical non-looped pipeline schedule used to motivate structural-bubble analysis. |
| Interleaved 1F1B (Narayanan et al., SC'21) | baseline | Looped pipeline schedule compared against; suffers from imbalance bubbles RoundPipe targets. |
| Looped BFS (Lamy-Poirier, 2023) | baseline | Memory-efficient looped schedule; main reference point in Figures 1 and 3 for bubble comparison. |
| Zero-Bubble Pipeline (Qi et al., ICLR'24) | influence | Schedule-reordering predecessor that motivates RoundPipe's near-zero-bubble target without long activation retention. |

## 2. Research Overview

### 2.1 Research Topic

本論文研究在多張消費級 GPU(如 RTX 4090)伺服器上,如何高效地對大型語言模型(LLM)進行微調與訓練。作者聚焦於消費級硬體面臨的兩大瓶頸:VRAM 容量受限,以及 PCIe 互聯頻寬遠低於 NVLink。在採用 CPU offloading 將參數、optimizer state、activation 卸載到主記憶體的設定下,他們重新檢視傳統 pipeline parallelism 排程,並指出既有 GPipe、1F1B、Interleaved 1F1B、Looped BFS 等排程因 weight binding 導致的結構性 bubble 與不平衡 bubble 問題。研究主軸是設計一個能在 PCIe 受限、CPU offloading 環境下逼近零 bubble 的 pipeline 排程,使消費級 GPU 訓練吞吐能逼近資料中心級硬體,並擴展可訓練的模型規模與 sequence 長度,具體目標包含 1.7B 至 235B(MoE)規模 LLM 的 LoRA / 全參數微調。

### 2.2 Domain Tags

- Distributed Systems
- Machine Learning Systems (MLSys)
- Deep Learning Training Infrastructure
- Pipeline Parallelism

### 2.3 Core Architectures Used

- **RoundPipe schedule (proposed)**:本論文提出的核心 pipeline 排程,以 round-robin 方式將前後向 stage 串成單一序列並分派至無狀態的 GPU worker pool,實現逼近零 bubble 的訓練流程。
- **Computation Dispatch Paradigm (proposed)**:作者提出的執行典範,將 GPU 視為 stateless execution worker,把 stage 計算動態分派到任一 GPU,從根本上打破傳統 pipeline 中 stage 與 GPU 的 weight binding。
- **Asymmetric stage splitting (proposed)**:對前向與反向 pass 採用不同的 layer 切分,利用 $\sum_i F_i + B_1 = L$ 與 $\sum_j B_j = L$ 等條件平衡單 stage 執行時間,消除 phase 邊界 bubble。
- **Priority-aware multi-stream transfer engine (proposed)**:每張 GPU 維護四條專用 communication stream,將 critical-path activation 傳輸與低優先級 parameter / gradient 傳輸交錯排程,以 longest-processing-time-first 演算法避免 head-of-line blocking。
- **Event-based fine-grained consistency protocol (proposed)**:以 layer 級 threading event 取代 step() 時的全域 barrier,在保留 staleness-1 語義下協調 master copy 與 optimizer copy 之間的 P/G copy 順序。
- **Automatic stage partitioning algorithm (proposed)**:以 $O(L^3)$ 複雜度搜尋 contiguous subsequence sum 候選的 $t_{\max}$,並用貪婪掃描找出滿足 GPU memory 限制的最小 stage 數。
- **Single-controller architecture (inherited from Ray / veRL/HybridFlow)**:採用控制平面與資料平面分離的設計,由 controller 統一指揮多個 GPU worker 與一個 optimizer worker 並行執行。
- **Pipeline parallelism with CPU offloading (inherited from Mobius)**:沿用 PP+offloading 的整體框架,把 parameter、optimizer state、activation 卸載到 host DRAM 並按需傳回 GPU。
- **Staleness-1 asynchronous CPU optimizer (inherited from ZeRO-Offload 系列)**:在主機端非同步執行 optimizer step,iteration $T+1$ 讀取 iteration $T-1$ 產生的權重,以隱藏 CPU optimizer 延遲。
- **Full activation recomputation (inherited from gradient checkpointing)**:作為論文的基本假設,只保留每個 transformer layer 的輸入,反向時重算中間 activation,並把 checkpointed activation offload 至 host DRAM。
- **Mixed-precision training with master/optimizer copies (inherited)**:維持低精度 master copy 與全精度 optimizer copy 兩份權重,搭配 RoundPipe 的事件協議在兩者之間同步更新。

### 2.4 Core Argument

作者主張現有 pipeline parallelism 排程之所以在消費級 GPU 上表現不佳,根本原因在於 weight binding:每個 stage 的權重與其對應的前向、反向計算被綁定在固定的 GPU 上,因此一旦模型本身存在天然不均衡(例如體積龐大的 LM head),最慢的 stage 就會拖累整條 pipeline,產生 structural bubble 與 imbalance bubble,且兩者間存在難以兼顧的 trade-off:粗粒度切分降低 imbalance bubble 但增加 structural bubble,細粒度切分則反之,實測 bubble ratio 可達 30%。論文的關鍵洞察是:在 CPU offloading 設定下,master weight 與 activation 本就駐留於主記憶體,並按需傳輸到 GPU 執行,因此 stage 沒有理由一定要綁定特定 GPU。基於此,作者提出 computation dispatch paradigm,將 GPU 視為無狀態的執行 worker pool,動態分派 stage,從而打破 weight binding。RoundPipe 把這個典範具體化為三項設計:(1) round-robin 分派,將前後向 stage 串成單一序列,在 GPU 間連續分派;(2) 非對稱 stage 切分,讓前向與反向採不同 layer 分割,平衡單 stage 執行時間;(3) staleness-1 非同步 optimizer,消除 iteration 邊界 bubble。為了讓此架構在實作上不退化,他們再加上 priority-aware transfer engine、layer 級事件式一致性協議、以及 $O(L^3)$ 的自動切分演算法。整體解法在邏輯上必要,因為僅有打破 weight binding 才能同時消除兩類 bubble,而 offloading 正好提供了這個前提。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(260 words)

標題 "Efficient Training on Multiple Consumer GPUs with RoundPipe" 直接定位本文主軸：在多顆 consumer-grade GPU 上做高效訓練。Abstract 緊湊地完成「問題—缺口—方法—結果」四步論證。問題端先指出在 consumer GPU 上 fine-tune LLM 很划算，但受限於 VRAM 與緩慢的 PCIe 互連；接著建立既有方案的缺口：將 pipeline parallelism 結合 CPU offloading 雖可降低通訊量，但既有 PP schedule 因「weight binding」把不均勻的 model stage 綁死在特定 GPU 上，使 throughput 受制於最重的 stage（如 LM head），產生嚴重的 pipeline bubble。在此鋪陳之上，作者宣示 RoundPipe 的核心提案：把 GPU 視為 stateless execution worker pool，以 round-robin 方式動態派送 computation stage，逼近 near-zero-bubble pipeline。為了把這個想法落地，Abstract 點名三個必要的系統元件：priority-aware transfer scheduling engine、fine-grained distributed event-based synchronization protocol，以及 automated layer partitioning algorithm，預示讀者後文 §4 會針對這三件事各寫一段。最後給出可量化的成果：在 8× RTX 4090 server 上 fine-tune 1.7B–32B 模型，相對 SOTA baseline 取得 1.48–2.16× speedup，並且是唯一能在單一 server 上以 31K sequence length 對 Qwen3-235B 做 LoRA fine-tuning 的系統。Abstract 並順帶宣告 GitHub 與線上文件連結，強調可重現性。整段 Abstract 為 §1 Introduction 預留了所有要展開的伏筆：weight binding 是何種具體機制、computation dispatch paradigm 為何可行、以及為何 4090 可以追平 datacenter 級 A800。讀完此段，讀者已能粗略繪出本文「為什麼—怎麼做—做得多好」的整體骨架。

### 3.2 Introduction

(900 words)

Introduction 從 LLM fine-tuning 的商業價值出發，論證 consumer-grade GPU（以 RTX 4090 為例，相對 A100 便宜約 80% 且算力相近）對小型公司與學術研究者具強烈經濟誘因，將「democratizing AI」當作整篇論文的訴求。接著立刻收斂到兩條硬體限制：VRAM 不足（訓練 8B 模型光 model states 就要 128 GB，遠超 4090 的 24 GB 或 5090 的 32 GB）與 PCIe 互連頻寬僅 NVLink 的不到 20%，兩條限制框定了本文的設計空間。

論文接著依序檢視既有解法並指出其各自不足：CPU offloading 與 activation recomputation 處理 VRAM 壓力；要 scale 到多 GPU 時，ZeRO-Infinity 一類 DP 方案需要在每層做 collective all-gather，會吃掉約 70% 的訓練時間；Mobius 等 PP+offloading 方案改用 P2P 通訊紓解頻寬壓力，但繼承了 pipeline bubble 缺陷。在這個敘事中，作者把問題的範圍從廣義的「VRAM 與通訊」逐步收斂到「pipeline bubble」這個具體痛點。

論文隨即命名核心矛盾為 weight binding issue：無論 standard looped 還是 flexible 切割，stage 的 weights 與其 forward/backward computation 都被綁死在某張 GPU 上，導致整條 pipeline 受限於最慢的 stage（典型如 LM head 所在的 stage），bubble 在 LLaMA-3.1-8B 上可達 30%。作者用 Figure 1(a)(b) 視覺化此困境，並順勢丟出他們的觀察支點：CPU offloading 既然已把 master weights 與 activation 放到 host memory，stage 就不必綁定 GPU，可在任意 GPU 上執行 — 這是 RoundPipe 的設計起點。

基於此觀察，作者揭示 RoundPipe 的兩項調度創新：asymmetric stage splitting（讓 forward 與 backward stage 各自分割，例如 forward 三層配 backward 一層以平衡執行時間）與 round-robin dispatch（將 stage 序列循環派送至各 GPU），共同達成 Figure 1(c) 所示的 near-zero-bubble pipeline。

Introduction 後半把「想法」擴展為三個落地挑戰並對應三個解法，做為對 §4 的預告：(1) host 與 GPU 之間大量 parameter/activation 移動會讓大型參數傳輸卡住 critical-path activation，需以 priority-aware transfer scheduling engine 解決 head-of-line blocking；(2) async optimizer update 引入 host-resident data 上的 race condition，需以 fine-grained distributed event-based protocol 在 layer 級別維持 ordering 而不重新引入 pipeline barrier；(3) 為了避免人工調參並維持 asymmetric partition 的 load balance，需以 $O(L^3)$ 的自動 stage-splitting 演算法計算 partition。

最後 Introduction 預告實驗結果：在 8× RTX 4090 上達 2.16× throughput 與 7.3× 序列長度；在 8× A800 SXM 上達 1.47× throughput 與 5.6× 序列長度；4090 throughput 在所有模型上皆達 A800 SOTA 的至少 76%；且是唯一能在 24 GB GPU 上 LoRA fine-tune 235B MoE 模型的系統。三點 contributions 條列收束：辨識 PP 在 consumer GPU 上的限制並提出 RoundPipe；給出 multi-stream 架構、event-based consistency 與 stage-splitting 演算法等系統設計；以全面實驗驗證效能。整段 Introduction 為 §2（背景與 weight binding 的細節證據）與 §3–§4（schedule 與系統實作）之間的分工清晰開好了路。

### 3.3 Related Work / Preliminaries

(1850 words)

§2 與 §6 共同構成本文的 preliminaries 與 related work 鋪墊。§2 從 memory pressure 切入：在 mixed-precision + Adam 配置下，Φ-parameter 模型 model states 占 $16\Phi$ bytes，32B 已達 512 GB；context window 擴大讓 activation footprint 隨序列長度線性膨脹，例如 LLaMA-3.1-8B 在 16K-token 單序列下即產生 68 GB 的 activation。在此壓力下，§2.1 系統檢視兩類紓緩技術。第一是 activation recomputation：只保留每層輸入，將每層 activation 壓縮到 $2sbh$ bytes 並在 backward 前重算；作者用 Figure 2 證明在 4090 上 recompute 比 reload 快 2.37–5.75×，因此即便用 layer-by-layer overlap 也壓不過，故將 full activation recomputation 列為本文預設假設並把 checkpointed activation offload 到 DRAM。第二是 weight/optimizer offloading：將 optimizer states、gradients 與 weights 移到 host memory 並由 CPU 執行 optimizer step，但 32B 模型的 host-side step 約 9.6s，與 GPU compute 同階，故前人多採 staleness-1 asynchronous update — iteration $T+1$ 讀取 iteration $T-1$ 後產生的權重，CPU 在背景套用 iteration $T$ 的 gradient。前人實驗已顯示一步 staleness 不傷收斂，這成為本文 §3.2 與 §4.3 的重要依賴。

§2.2 把鏡頭拉到多 GPU 場景並對比兩種 offloading 拓樸。DP-based（DeepSpeed ZeRO-Offload / ZeRO-Infinity）將 model states 切片到 data-parallel rank，但每次 forward/backward 都要 all-gather 完整參數，PCIe 上會吃掉約 70% 的訓練時間。PP-based（Mobius）則把 layer 切成 stage 派到各 GPU，stage weight 由 DRAM 預載；通訊量大幅下降到只剩 activation/gradient 的 P2P，但 inherits pipeline bubble 問題。這段把問題明確收斂到 schedule 設計上，為 §2.3 的 bubble 解剖鋪路。

§2.3 把 bubble 解剖為兩類。Structural bubble 來自 forward/backward 的 data dependency：非 looped 的 GPipe/1F1B 在開頭與結尾各有 GPU 閒置，bubble ratio 為 $\frac{S-1}{M+S-1}$；Zero-Bubble schedule 雖能填補但需長期保留 activation，與 recomputation 衝突且記憶體爆炸；Looped schedule（Interleaved 1F1B、Looped BFS）每 GPU 配 $v$ 個 stage 共 $S=vN$ 個，bubble 降至 $\frac{N(N-1)}{S \cdot M + N(N-1)}$。Imbalance bubble 則來自實際 stage 執行時間不均，Figure 3 顯示真實 bubble ratio 可達 30%，遠高於 ideal 估計。作者把現有 schedule 的核心 dilemma 釘在「stage 數必須是 GPU 數的整數倍」：粗切（如 GPipe）structural bubble 大；細切（如 looped）每 stage 只剩少數 layer，LM head 一進來就無法均衡 — 這個 dilemma 直接動機化了 §3 的 Computation Dispatch Paradigm。

§6 Related Work 補上 schedule 與 offloading 兩條線的全景。Pipeline schedule 線：synchronous schedule（GPipe、DAPPLE、Megatron-LM、Chimera）受 bubble 困擾；asynchronous（PipeDream 系列、Pipemare、XPipe、彈性平均）以 weight stashing 換效率，記憶體成本高；backward-splitting 的 zero-bubble schedule 透過延後 weight update 換取低 bubble；looped 方法（Interleaved 1F1B、Looped BFS）增加 stage 數但受 GPU 整數倍約束，partition 隨模型加深愈難平衡。RoundPipe 的差異化定位是「利用 heterogeneous memory 把 stage 與 GPU 解耦」，同時提供 synchronous（彈性 partition）與 asynchronous（無 GPU 記憶體 overhead）兩種變體。Offloading 線：weights/optimizer 到 CPU 或 NVMe（ZeRO-Infinity、StrongHold、Chunk-based）、activation 到 host（vDNN、Superneurons、FlashNeuron）、tensor-granularity 管理（Sentinel、LoHan）等多為 single-GPU 或 DP 設計，scale 到多 GPU 仍有通訊瓶頸。作者宣稱 RoundPipe 是 distributed training 與 host-memory offloading 的 co-design，這條 narrative 直接呼應 §3 提出的「offloading 解放 stage 綁定」此一設計動機。整體而言，§2 的細節 + §6 的鳥瞰共同證明：問題是真實的、解空間已被前人窮舉、而 RoundPipe 確實找到一條尚未被走過的對角線。

### 3.4 Method (overview narrative)

(3300 words)

§3 與 §4 一起構成本文的 method 章節：§3 給出抽象演算法層的 RoundPipe schedule、§4 給出可實作的系統設計。§3.1 從一個 strawman 反證開始：若僅做 flexible partition（Figure 1(b) 將 13 層配 4 GPU），雖然能藉由不均勻切割降低 imbalance bubble，卻因 stage 仍綁定 GPU，使「重 stage 」所在的 GPU（GPU 1）成為瓶頸，其餘 GPU 在等待時製造新的 structural bubble。作者把 CPU offloading 提升為設計槓桿，提出 Computation Dispatch Paradigm — model states 與 activation 駐留 host，computation（連同對應 stage 與 activation）動態派送到任一 GPU 執行；因為 weight transfer 本來就必要，重新指定目標 GPU 不增加額外通訊。Paradigm 一旦成立，flexible partition 與 low structural bubble 就可同時取得。

§3.2 將此 paradigm 具體化為 RoundPipe schedule。Round-robin dispatch 把 forward 與 backward stage 串成單一連續派送序列：把 $M$ 個 micro-batch 切成 $R = M/M_R$ 個 round（$M_R \geq N$），每個 round 內 $S_f$ 個 forward stage 後接 $S_b$ 個 backward stage，第 $i$ 個 stage slot 派到 $\text{GPU}_{(g_0 + i) \bmod N}$；round 與 round 之間以 $g_0 \leftarrow (g_0 + S) \bmod N$ 接續，使整條 pipeline 連續無斷層。Asymmetric stage splitting 則打破對稱性：以 $(F_1, F_2, \ldots, F_{S_f}, B_1)$ 為 forward partition、$(B_1, B_2, \ldots, B_{S_b})$ 為 backward partition，並在 $B_1$ 層融合 forward 與 backward（這部分的 forward 直接當 recompute 使用，省一次 forward），條件為 $\sum_i F_i + B_1 = L$ 且 $\sum_j B_j = L$。如此可讓每個 stage 的執行時間趨於相等，消除 forward/backward 邊界的 idle bubble。Async optimizer 的支援則自然湧現：因 round-robin 不依 iteration 為界，iteration $T$ 從 iteration $T-1$ 結束的位置接續派送（Figure 4），warm-up/cool-down bubble 被相鄰 iteration 吸收掉。

§3.3 進行 trade-off 分析。Bubble ratio 為 $\frac{N(N-1)}{M \cdot S + N(N-1)}$，雖與 looped schedule 同形，但 RoundPipe 的 $S = S_f + S_b$ 約為 looped 的 $\frac{4}{3}$ 倍（依「forward 一層約為 backward+recompute 1/3 時間」的經驗值），故 bubble 較小；加上 flexible partition 帶來的更佳 time balance，imbalance bubble 也更小。Roofline 分析（細節在 Appendix C）證明在常見 batch size（dense $B \geq 8$、MoE $B \geq 80$）下 PCIe transfer 可被 compute 完全 overlap，paradigm 並非 throughput–memory trade-off，而是 throughput-preserving 的 scheduling search-space 擴張。實作能否真的把 transfer 與 kernel 疊起來則由 §4.2 接手。

§4 將上述抽象映射到實作。§4.1 採 single-controller 架構（仿 Ray、veRL/HybridFlow），切分 control plane（負責 scheduling、ordering）與 data plane（負責 device transfer 與 kernel 執行）。系統由 controller、optimizer worker，以及每張 GPU 一個 GPU worker 組成（Figure 5）。使用者只看到 forward_backward() 與 step() 兩個 API：前者語意等同 PyTorch 的 forward+backward，accept input、return loss、in-place 累積 gradient，內部則由 controller 將 micro-batch 派至 GPU worker；後者把 gradient post-processing 與 weight update 派給 optimizer worker，後者操作 full-precision optimizer copy，與 GPU worker 並行不互相干擾。§4.1.2 點名三大實作挑戰並對應 §4.2–§4.4：data transfer overlap、async consistency、stage partition。

§4.2 處理 data transfer overlap。每個 stage 涉及兩類傳輸：(1) per-micro-batch 的 activation upload/download（critical path，下個 stage 必須等上個 stage 的 activation 抵達 host 並重新 upload）；(2) per-stage 的 parameter upload 與 gradient download（非 critical，可塞入空檔）。簡單 overlap 會 head-of-line blocking（Figure 6）。RoundPipe 採 multi-stream 架構：在預設 compute stream 之外另設四條 dedicated stream，分別處理兩類傳輸的雙向，並用 CUDA event 在 micro-batch 邊界同步。Activation 提前/延後一個 micro-batch 上傳/下載以避免阻擋 compute；參數與梯度則由 priority-aware transfer scheduling engine 切塊，按 longest-processing-time-first 將 tensor 從大到小貪婪指派到累計傳輸量最小的 window，特別大的 tensor（如 LM head）會先被切成小塊，確保塞得進每個 window，避免 PCIe contention（Figure 7）。

§4.3 處理 fine-grained parameter consistency。Mixed-precision + offloading 下參數有三份表示：GPU transient copy、CPU master copy（低精度）、optimizer copy（全精度）。RoundPipe 用 step() 當邏輯 barrier，在 async update 下需精確控制 P copy（master 同步權重）與 G copy（master 提取梯度），維持五條 ordering constraint：(1) P copy 等 GPU 完成前一輪 parameter upload；(2) GPU 等 P copy 完成才 upload 下一輪參數；(3) G copy 等 GPU 完成前一輪 gradient download；(4) GPU 等 G copy 完成才寫入下一輪 gradient；(5) data copy 必須夾在前後兩次 optimizer step 之間。Naive 的 blocking copy（Figure 8(a)）會把 step() 當成 hard barrier，重新製造 pipeline bubble。RoundPipe 改用 Event-Based Protocol（Figure 8(b)）：把 P copy 與 G copy 卸給 optimizer worker，用 threading event 點對點實現四條 dependency edge，第五條由 optimizer worker 的內部順序自然滿足。關鍵巧思在於把 event 綁在 layer 而非整模型上：淺層（Layer 1）正卡在 backward 結束到 next forward 開始的最緊縮路徑上，逐層釋放 event 讓 GPU worker 一拿到淺層權重就能開始 next iteration 的 forward，深層權重仍可同時在後台同步。

§4.4 給出自動 stage partition。輸入是前幾個 iteration 收集的 per-layer execution time 與 memory consumption，目標是最小化 $(M \cdot S + N(N-1)) \cdot t_{\max}$（呼應 §3.3）並滿足 GPU 記憶體上限。關鍵觀察是：每個 stage 必須含連續 layer，故 $t_{\max}$ 的候選值受限於所有 forward/backward 連續子序列和共 $O(L^2)$ 種；對每個候選，問題化為「至少需多少個連續 partition 使每個 partition 時間 $\leq t_{\max}$ 且 memory 不超界」，這是經典 greedy，掃一遍 layer 即可在 $O(L)$ 完成，總計 $O(L^3)$。Greedy 過程中 RoundPipe 優先把第一個 backward stage 填滿，因該 stage 與 fused forward 共用，能省下 recompute，這個微小設計選擇直接放大了 §3.2 fused-stage 的計算節省。整體鋪陳將「為何能 dispatch（§3.1）」「dispatch 之後 schedule 長什麼樣（§3.2）」「為何不會被 PCIe 拖垮（§3.3）」「如何在系統上正確且高效地實作（§4.1–§4.4）」一條線串完，為 §5 的實驗驗證鋪好基礎。

### 3.5 Experiments (overview narrative)

(1900 words)

§5 把 §3–§4 的設計帶入兩個截然不同的硬體環境檢驗。§5.1 設定兩台 server：8× RTX 4090（24 GB VRAM、Intel Xeon Gold 6330、800 GB DDR4、PCIe 4.0 32 GB/s）代表 consumer GPU 場景；8× A800 SXM（80 GB HBM2e、Xeon Platinum 8352Y、800 GB DDR4、NVLink 3.0 200 GB/s）代表 datacenter 上限。對照六個 baseline — DeepSpeed ZeRO-2、PyTorch FSDP（ZeRO-3）、ZeRO-Infinity、Megatron-TP、Megatron-PP、Mobius — 並加上 RoundPipe-sync 變體（關閉 async optimizer、在 CPU 同步執行 step）以隔離 schedule 與 async 兩個貢獻。Workload 涵蓋 Qwen3-1.7B、LLaMA-3.1-8B、GPT-OSS-20B（MoE）、Qwen3-32B、Qwen3-235B-A22B（MoE，僅做 LoRA $r=32$），sequence length 固定 2048，global batch size 分別為 512/256/128/128/64，全部使用 FP16 mixed-precision 與 full activation recomputation。每個 framework 在不 OOM 且 micro-batch 數 $\geq 8$ 的前提下個別調到最大 micro-batch。Metric 為 training throughput（tokens/s，10 iteration 平均，warm-up 後）與 max sequence length（micro-batch=1 下能跑完不 OOM 的最長序列）。

§5.2 在 4090 server 呈現核心結論（Figure 9、Figure 10）：RoundPipe 與 RoundPipe-sync 在五個模型上皆奪冠；RoundPipe 較最快既有系統提升 1.48–2.16× throughput，sync 變體提升 1.15–1.63×，效能差距歸因於更少的 pipeline bubble 與更佳的 communication–computation overlap。同時 RoundPipe 因嚴格限制駐 GPU layer 數，是唯一能在 24 GB GPU 上 LoRA fine-tune 235B 的系統。Max sequence length 上，扣掉 throughput 不堪用的 Megatron-TP 後，RoundPipe 較次佳 baseline 延長 4.7–7.3×；async 與否不影響此 metric（因記憶體不變）；235B-LoRA 甚至能跑出比 32B 全參數略長的序列，因 LoRA 產生的 intermediate activation/gradient 較少。

§5.3 把 RoundPipe 搬到 A800 server 測試其 paradigm overhead 是否可接受（Figure 11、Figure 12，Mobius 在 datacenter 上劣於 ZeRO-Infinity 故略過）。Throughput 上 RoundPipe 達 SOTA 的 0.98–1.47×：小模型（1.7B、8B）DP 因 NVLink 高頻寬占優，但 RoundPipe 完全不用 GPU peer-to-peer，只靠 PCIe host-to-device transfer 仍能緊咬；RoundPipe-sync 與 ZeRO-Infinity 同階，差距來自 CPU optimizer step。大模型（20B+）DP 受 full-parameter sync 拖累，TP/PP 占優，但 RoundPipe 透過更少的通訊與更少的 bubble 仍領先；Megatron-PP 在 Qwen3-32B 上因 64 層分到 8 GPU 後最後一 rank 多扛 LM head 而 OOM。重要的橋樑數據是：4090 上的 RoundPipe 在所有模型都達 A800 SOTA 的至少 76% throughput，作者以此宣稱 consumer GPU 不再只是「便宜替代品」，已能逼近 datacenter 級的絕對訓練速度。Max sequence length 在 A800 上延長 1.19–5.62×，於小模型可達 192K–288K，因 model state 與 stage-boundary activation 都在 host memory；大模型上其他 baseline 受限於 GPU 記憶體，RoundPipe 維持領先。

§5.4 strong-scaling 實驗（Figure 13）顯示 1→8 GPU 的 throughput 接近線性，partition 與 overlap 機制隨 GPU 數穩健運作。一個獨特觀察是 max sequence length 與 GPU 數無關（五個模型分別固定為 73K、49K、39K、28K、31K），這直接源自 Computation Dispatch Paradigm — GPU 只駐當前 stage 所需資料，其餘永遠在 host。

§5.5 對 Qwen3-1.7B 在 8× RTX 4090 上做兩個數量級的序列長度掃描（512 到 64K，Figure 14），throughput 隨 attention cost 平滑下降，證明系統對短長 context 都穩健，不存在某段急遽崩落的死區。

§5.6 兩個 ablation 切除式驗證設計貢獻。§5.6.1 用 pipeline simulator 在相同 layer-time profile 下比較五種 schedule（Figure 15）：RoundPipe-sync 較最佳 baseline 將 bubble 降低 23–55%，且 bubble ratio 隨模型加深、stage 變多而再降；啟用 async optimizer 後絕對 bubble ratio 壓到 4.5% 以下，剩餘的 idle 主要來自殘餘的 stage imbalance，由 §4.4 的自動 partition 控在低水位。Wall-clock 上自動 partition 對 1.7B–32B 在毫秒級（2.6–5.0 ms），對 94 層的 235B 也只 1.47 秒，相對訓練時間幾乎可忽略。§5.6.2 比較 blocking copy 與 event-based consistency（Figure 16）：後者每 iteration 省下 2.6–14 秒，且節省量隨可訓練參數量遞增（235B-LoRA 因只更新少量權重而獲益較少），證實 fine-grained per-layer event 是 async optimizer 真正落地、把 weight/gradient 同步藏進 GPU compute 的關鍵。

### 3.6 Conclusion / Limitations / Future Work

(70 words)

§7 Conclusion 是一段約 70 字的緊湊收束：作者重申 RoundPipe 是針對 consumer GPU server 設計的新 PP schedule，並把貢獻歸納到三件事 — 提出 Computation Dispatch Paradigm 並由 roofline 確認其不犧牲 compute-bound throughput；以 asymmetric stage splitting 平衡 forward/backward 執行時間；以 round-robin dispatch 解除 stage 與 GPU 的綁定，從而消除 stage imbalance、提升 pipeline 效率。最後以一句話指向 §5 實驗結果作為佐證。

論文並未獨立列出 Limitations 或 Future Work 章節，這在系統論文中常見：作者選擇把 trade-off 與限制散落在各方法/實驗小節而不集中收束。從文中可以推得的潛在限制包含：(1) §3.3 的 roofline 分析以 dense $B \geq 8$、MoE $B \geq 80$ 為前提保證 PCIe 完全 overlap，極小 batch 的場景未被覆蓋；(2) staleness-1 async optimizer 的收斂性仰賴前人結果（[24, 40]），本文未在 RoundPipe 框架內重新做收斂驗證；(3) 評估硬體限於 8 GPU 單機，跨節點 scaling 與相應的網路拓樸（如 InfiniBand 或多機 PCIe over network）未涵蓋；(4) §4.4 的自動 partition 需要前幾個 iteration 的 profiling 為輸入，冷啟動成本與動態 workload（例如 sequence length 隨資料分布變化）下的重 partition 開銷未量化；(5) §5.3 已揭露在小模型 + NVLink 充裕的情境下 DP 仍占優，意味 RoundPipe 的優勢場景集中於 PCIe-bound 與大模型，這個邊界可作為未來工作的擴展方向。讀完 §7，讀者應能將本文方法論定位為「以 host memory 為新自由度，重構 pipeline schedule 設計空間」，而非單純加上一個 offloading hack。

## 4. Critical Profile

### 4.1 Highlights

- 論文清楚地將既有 PP 排程的低效歸因於一個可被命名的根因 weight binding,並用 Figure 1(a)(b) 與 Figure 3 對 GPipe / 1F1B / Interleaved 1F1B / Looped BFS 進行統一框架下的 bubble 分解,在 8 GPU 上實測 bubble ratio 可達 30%(p.4, Figure 3)。
- 提出 Computation Dispatch Paradigm,將 GPU 視為 stateless worker pool,並用 §3.3 的 roofline 分析證明此重組在 dense 模型 $B \geq 8$、MoE 模型 $B \geq 80$ 時不會犧牲計算密度(p.6, Appendix C.4 Figure 17)。
- RoundPipe 排程同時整合 round-robin dispatch、asymmetric stage splitting 與 staleness-1 async optimizer,使 forward 與 backward 串成單一連續序列,並消除 iteration 邊界 bubble(p.5–6, Figure 1c, Figure 4)。
- Priority-aware transfer engine 用「longest-processing-time-first」把 parameter / gradient transfer 分塊塞進 activation transfer 之間的 idle window,解決了 head-of-line blocking(p.7, Figure 6, Figure 7)。
- Event-based parameter consistency protocol 將 P-copy / G-copy 卸載到 optimizer worker,並把同步事件綁定到 layer 粒度,使 layer 1 在深層仍在同步時就能開始下個 iteration(p.7–8, Figure 8)。
- 自動 stage 切分演算法以「候選 $t_{\max}$ 為所有連續子序列和」搭配 greedy packing,獲得 $O(L^3)$ 複雜度,實測 Qwen3-32B 切分僅 5.0 ms、Qwen3-235B 切分 1.47 s(p.8–11, §5.6.1)。
- 在 8×RTX 4090 上對 1.7B–32B 模型相對於最強既有系統取得 1.48–2.16× 訓練吞吐,且可在 24 GB VRAM 下完成 Qwen3-235B 的 LoRA 微調(31K sequence length, single server)(p.1, Figure 9, Figure 10)。
- 模擬實驗顯示 RoundPipe-sync 相對最佳 baseline 將 bubble ratio 降低 23–55%,RoundPipe(async)將絕對 bubble ratio 壓到 4.5% 以下(p.11, Figure 15)。
- 在 8×A800 SXM 上即使僅靠 PCIe host-to-device 傳輸不使用 NVLink,RoundPipe 在大模型上仍取得 1.47× 加速,並使 4090 達到 A800 baseline 76% 以上的吞吐(p.10, Figure 11)。
- 最大可訓練 sequence length 對 GPU 數量幾乎不變(1→8 GPU 上分別維持 73K / 49K / 39K / 28K / 31K),為 stage-boundary activation 全部存於 host memory 的副產物(p.10–11, §5.4)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- §2.1.2 與 §3.2 採用 staleness-1 async optimizer,作者並未自行驗證收斂性,僅引用 ZeRO-Offload 與 ZenFlow 的既有結論「one-step staleness 不傷害收斂」(p.3, p.5)。
- §5.3 承認 4090 的 VRAM bandwidth 限制使其相對 A800 仍有計算上限,因此 4090 的吞吐封頂在 A800 baseline 的 76% 左右,而非追平(p.10)。
- §3.3 的 roofline 分析揭露 MoE 需要 $B \geq 80$ 才落在 compute-bound 區間,代表在小 batch 情境下 PCIe 傳輸無法被完全隱藏(p.6, Appendix C.4 Figure 17)。
- §5.3 註腳指出 Megatron-TP 對 Qwen3-235B 因為 KV head 數為 4、無法切到 TP=8,屬於 baseline 的限制而非 RoundPipe 的優勢來源,作者於正文中未細究公平性(p.9 footnote 4)。
- §5.6.1 提到 RoundPipe 剩餘 4.5% 以下的 idle time「來自 stage 執行不平衡」,亦即 automatic partitioning 仍有殘餘 imbalance 無法消除(p.11)。

#### 4.2.2 Phyra-inferred

- 全文僅做 throughput / sequence length / bubble simulation 評估,沒有任何 loss curve 或下游 task accuracy,async staleness-1 + asymmetric splitting 對微調品質的實際影響未被驗證,讀者只能轉而相信引用文獻(§5 全章)。
- 評測完全侷限於 single 8-GPU server;Computation Dispatch Paradigm 在 multi-node、NIC 與 PCIe 共用根複合體的情境下行為未測,擴展性主張只支持到單機 strong-scaling(§5.4 Figure 13)。
- Mobius 是 §6.2 與 abstract 中最關鍵的對照組,但在 Figure 11 (A800) 的比較中被作者主動排除,4090 的對比也僅以柱狀圖呈現而無逐模型數值表,使得「擊敗最直接前作」的差距規模不易精確核實(p.10)。
- Auto stage-splitting 演算法只在「first few iterations」收集 per-layer time,假設工作負載穩態;對長序列、變動 batch、MoE expert routing 不均的情境未做敏感度分析(§4.4, §5.6.1)。
- §5.3 將 RoundPipe 在 A800 上 1.7B / 8B 小模型相對 DP 仍 0.98× 視為「近乎追平」,但這實際上代表 Computation Dispatch 在 NVLink-rich 與小模型情境下會略輸給標準 DP,作者未深究何時應退回 DP(p.10 Figure 11)。
- §5.6.1 的 bubble ratio 數據是用 simulator 跑的,而非從實際訓練 trace 抽取,因此「<4.5%」的數字無法直接對應到 wall-clock breakdown,實機部分缺少獨立驗證(p.11)。
- 全文未討論 fault tolerance:single optimizer worker 與 single controller 都是 SPOF,在以 commodity 為訴求的長時間微調情境下這是相當實際的風險(§4.1)。

### 4.3 Phyra's Judgment (summary)

RoundPipe 真正新的部分是「在 CPU offloading 已強制 weight 過 PCIe」這個前提下,把 stage 與 GPU 解綁的 Computation Dispatch Paradigm,以及它衍生出的 asymmetric splitting + round-robin schedule 三件套;這條 reasoning 邏輯緊密、bubble 分析自洽,屬於 schedule 層面的真實進展。其餘 priority-aware transfer、event-based consistency、$O(L^3)$ 切分演算法則屬於把這個 paradigm 落地的工程實作,個別構件並無理論突破,但合在一起是必要的。最關鍵的未解問題是 staleness-1 與 asymmetric splitting 對訓練品質的影響從未在本文被驗證,以及在多機 / NVLink-rich 環境下此 paradigm 的價值是否仍成立。

## 5. Methodology Deep Dive

### 5.1 Method Overview

RoundPipe 的核心方法立基於一個觀察:在 CPU offloading 設定下,model state 與 activation 本就駐留於 host memory 並按需上傳到 GPU 執行,因此 stage 不必綁定到特定 GPU。論文以此為基礎提出 **computation dispatch paradigm**——把 GPU 視為無狀態的 stateless worker pool,由 controller 動態地把 stage 分派到任一可用 GPU。在此典範下,pipeline schedule 不再受限於「stage 數必須是 GPU 數整數倍」的約束,獲得了嚴格更大的排程搜尋空間。論文的 roofline 分析(Appendix C)顯示在 typical batch size 下,PCIe 傳輸時間能被 GPU compute 完全 overlap,因此 dispatch paradigm 並非 throughput 與 memory 的 trade-off,而是一個 throughput-preserving 的重組。

基於 dispatch paradigm,RoundPipe schedule 由三個關鍵設計組成。第一,**round-robin dispatch**:把每個 round 中的 $S_f$ 個 forward stage 與 $S_b$ 個 backward stage 串成單一 $S = S_f + S_b$ 長度的線性序列,stage slot $i$ 分派到 $GPU_{(g_0 + i) \bmod N}$,跨 round 連續推進 $g_0 \leftarrow (g_0 + S) \bmod N$。第二,**asymmetric stage splitting**:forward 與 backward 採用不同的 layer 分割 $(F_1, \ldots, F_{S_f}, B_1)$ 與 $(B_1, B_2, \ldots, B_{S_b})$,前向被融合到第一個 backward stage 以避免重算,從而讓單 stage 執行時間在前後向間達成平衡,消除 phase boundary 處的 bubble。第三,**staleness-1 asynchronous optimizer**:把 optimizer step 與 GPU compute 並行,讓 iteration $T+1$ 讀取 iteration $T-1$ 產生的 weights,完全消除 iteration 邊界的 warm-up/cool-down bubble。

把上述抽象排程轉化為實際可運作的 training framework 還需四個系統層級設計。**Multi-stream transfer architecture** 在每張 GPU 維持 4 條獨立 communication stream(雙向各兩條,分別處理 activation 與 parameter/gradient)外加 compute stream,以充分利用 PCIe 雙向頻寬並避免 head-of-line blocking。**Priority-aware parameter transfer scheduling** 採用 longest-processing-time-first (LPT) 演算法,把非關鍵路徑的 parameter/gradient transfer 切片打包到 activation transfer 之間的閒置窗口。**Distributed event-based consistency protocol** 用 per-layer event 訊號取代 global barrier,讓淺層 (Layer 1) 在深層 layer 還在同步時就能開始下一輪 forward。**Automatic stage partitioning algorithm** 利用「contiguous subsequence sum 的可能值至多 $O(L^2)$ 個」的觀察,結合 $O(L)$ 的 greedy packing,得到整體 $O(L^3)$ 的 partitioning 複雜度。

### 5.2 Pipeline Diagram with Tensor Shapes

下圖以 forward stage $i$ 與其後的 backward stage 為例,展示 RoundPipe 在單個 round 中,host 與一張 GPU worker 之間的資料流。`B` 為 micro-batch size,`s` 為 sequence length,`d` 為 hidden dimension,`L` 為總層數,`F_i` 為 forward stage $i$ 包含的 layer 數,`B_j` 為 backward stage $j$ 包含的 layer 數,`P_i` 為 stage $i$ 全部 layer 的參數張量集合。Vocabulary size `V` 與每個 model 的 `d` 在論文方法章節未具體列出,以 `?` 標註(實驗章節僅提供模型名稱)。

```
Host (DRAM)
   ├→ Master Copy (FP16):     Full model params P[L, ...]               (size ≈ 2Φ bytes)
   ├→ Optimizer Copy (FP32):  P_fp32 + Adam states (m, v)               (size ≈ 12Φ bytes)
   ├→ Stage-boundary activs:  A_k for k ∈ stage boundaries, shape [B, s, d]
   └→ Gradient buffer (FP16): G[L, ...]                                  (size ≈ 2Φ bytes)

Controller dispatches stage slot i  →  GPU_{(g_0 + i) mod N}

  ┌─────────────────────────── GPU Worker ───────────────────────────┐
  │                                                                   │
  │  [Param Upload Stream]    Host → GPU                              │
  │      P_i: stage params, F_i × per-layer params (FP16)             │
  │      └→ chunked by LPT into M data-transfer windows               │
  │                                                                   │
  │  [Activation Upload Stream]  Host → GPU  (per micro-batch)        │
  │      A_in: [B, s, d]   (FP16)                                     │
  │                                                                   │
  │  [Compute Stream]                                                 │
  │      ── Forward stage i (F_i layers): ─────────────────────────   │
  │           [B, s, d] ──layer 1──▶ [B, s, d] ──...──▶ [B, s, d]     │
  │           (LM head, if present, projects to logits [B, s, V=?])   │
  │                                                                   │
  │      ── Backward stage j (B_j layers, with recompute): ─────────  │
  │           saved A_in: [B, s, d]                                   │
  │           recompute forward: [B, s, d] → cached activations       │
  │           backward: dY [B, s, d] ──▶ dX [B, s, d]                 │
  │           weight grads: dW for F_i / B_j layers (FP16)            │
  │                                                                   │
  │      ── First backward stage B_1 is fused: forward+backward       │
  │           in a single stage, avoiding one extra forward pass      │
  │                                                                   │
  │  [Activation Download Stream]  GPU → Host                         │
  │      A_out: [B, s, d]   (FP16)                                    │
  │                                                                   │
  │  [Gradient Download Stream]  GPU → Host                           │
  │      G_i: stage gradients (FP16)                                  │
  │      └→ chunked by LPT, large tensors (e.g., LM head) split       │
  └───────────────────────────────────────────────────────────────────┘

Host (continued)
   ├→ Optimizer Worker:   FP16 grads → FP32 cast → Adam step → FP16 cast
   │      coordinated by per-layer events (cf. §5.3.6)
   └→ Updated Master Copy P (FP16) ready for iteration T+2
        (iteration T+1's GPU compute proceeds concurrently)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Computation Dispatch Paradigm

**Function:** 把 stage 與 GPU 解耦,model state 與 activation 駐留 host,任何 GPU 在 requisite data 就緒後皆可執行任何 stage。

**Input:**
- Name: model state (params, optimizer state, activations)
- Shape: full-model resident on host DRAM, parameter slice $P_i$ for stage $i$
- Source: host memory pool

**Output:**
- Name: stage execution dispatch decisions
- Shape: a sequence of $(stage_i, GPU_{j})$ assignments
- Consumer: GPU workers via per-stream transfer engine

**Processing:**

對於 PP-based offloading (例如 Mobius),weight transfer 已是必要成本,把同一個 stage 改派到不同 GPU 不增加 communication volume,只是改變目標 GPU。Controller 在 dispatch 時只需保證:(1) 對應的 parameter slice 已在目標 GPU,(2) 上一 stage 的 activation 已 download 並 re-upload 到目標 GPU。論文以 roofline 分析證明 typical batch size 下 PCIe 不會 bottleneck compute,因此這個重組不破壞 throughput。

**Key Formulas:**

論文未給出此段落專屬的數學式,只給出 dispatch index 公式(見 §5.3.2)。

**Implementation Details:**

由 single-controller 統一決策(§4.1),GPU worker 為 stateless execution worker。Mobius 等既有系統把 stage 綁死到特定 GPU,RoundPipe 則允許 stage 動態 relocation。

---

#### 5.3.2 Round-Robin Dispatch Schedule

**Function:** 把每 round 的 $S = S_f + S_b$ 個 stage slot 連續分派到 $N$ 張 GPU,跨 round 接續推進,形成幾乎無 bubble 的 stage 流。

**Input:**
- Name: 每 round 的 stage slot 序列 $(F_1, \ldots, F_{S_f}, B_1, \ldots, B_{S_b})$
- Shape: 長度 $S$ 的 stage list
- Source: 由 §5.3.7 partitioning 演算法決定

**Output:**
- Name: dispatch table $\{(stage_i, GPU_{(g_0 + i) \bmod N})\}$
- Shape: $M$ 個 micro-batch × $S$ 個 stage 的 GPU assignment matrix
- Consumer: GPU workers

**Processing:**

把 $M$ 個 micro-batch 分成 $R = M / M_R$ 個 round,每 round 處理 $M_R \geq N$ 個 micro-batch。Round 內的 stage slot $i$(從 0 計數,跨越 forward-then-backward 序列)分派到 $GPU_{(g_0 + i) \bmod N}$。每張 GPU 在轉到下一個 stage slot 前,先在本 GPU 完成本 round 全部 $M_R$ 個 micro-batch。Round 之間:$g_0 \leftarrow (g_0 + S) \bmod N$,使新 round 的第一個 stage 接續分派到下一張 GPU。

**Key Formulas:**

每 round 中 stage slot $i$ 的 GPU index:

$$
\text{GPU}(i) = (g_0 + i) \bmod N, \quad i \in \{0, 1, \ldots, S-1\}
$$

Pipeline bubble ratio (與 looped schedules 同形式但 $S$ 較大):

$$
\text{Bubble Ratio} = \frac{N \cdot (N - 1)}{M \cdot S + N \cdot (N - 1)}
$$

由於 RoundPipe 的 $S = S_f + S_b$ 約為 looped schedules 的 $\frac{4}{3}\times$(論文以「forward 約是 backward+recompute 的 $\frac{1}{3}$」推得),bubble ratio 較小。

**Implementation Details:**

論文 Figure 1(c) 以 12-layer model + LM head 在 4 GPU 上展示,forward 三層一組、backward 一層一組。Round 之間無 pipeline flush,在 async optimizer 下連續執行。

---

#### 5.3.3 Asymmetric Stage Splitting

**Function:** 為 forward 與 backward 設計不同的 layer 分割,讓單 stage 執行時間在前後向間平衡,消除 phase 邊界 bubble。

**Input:**
- Name: 每層的 forward time $t^f_l$、backward time $t^b_l$、memory footprint(由 §5.3.7 演算法收集)
- Shape: 長度 $L$ 的時間/記憶體向量
- Source: 訓練前幾個 iteration 的 profiling

**Output:**
- Name: forward partition $(F_1, \ldots, F_{S_f}, B_1)$ 與 backward partition $(B_1, B_2, \ldots, B_{S_b})$
- Shape: 兩組 layer 數序列
- Consumer: round-robin dispatcher

**Processing:**

Forward 一個 transformer layer 通常比 backward(含 recompute)快約 3 倍,因此若強制 symmetric splitting(forward/backward 同分割),phase 邊界會出現 idle bubble。RoundPipe 把第一個 backward stage 中的 $B_1$ 層 forward 與 backward fuse,即此 fused stage 中的 forward 直接作為 recompute,省下一次完整 forward 計算。約束為 $\sum_i F_i + B_1 = L$ 與 $\sum_j B_j = L$,所有 stage 應有近似相同的執行時間。

**Key Formulas:**

Layer 數約束:

$$
\sum_{i=1}^{S_f} F_i + B_1 = L, \quad \sum_{j=1}^{S_b} B_j = L
$$

stage 時間平衡目標(代入 §5.3.7 的最佳化目標):

$$
\min \; t_{\max} \text{ s.t. } \forall \text{ stage } k, \; t_k \leq t_{\max}
$$

**Implementation Details:**

論文以「1 stage = 3 forward layers = 1 backward layer」作為典型比例(Figure 1 註腳)。實務上由 §5.3.7 的 $O(L^3)$ 演算法自動求解,不需手動調整。

---

#### 5.3.4 Staleness-1 Asynchronous Optimizer

**Function:** 把 optimizer step 與下一 iteration 的 GPU compute 並行,消除 iteration 邊界的 warm-up/cool-down bubble。

**Input:**
- Name: iteration $T$ 的完整 gradient $G^{(T)}$
- Shape: full-model gradient (FP16, host buffer)
- Source: GPU workers via gradient download stream

**Output:**
- Name: iteration $T$ 更新後的 master weights,供 iteration $T+2$ 讀取
- Shape: full-model FP16 master copy
- Consumer: 後續 iteration 的 parameter upload

**Processing:**

Iteration $T+1$ 讀取 iteration $T-1$ 完成 update 後的 weights,而 CPU 在背景把 iteration $T$ 的 gradient 套用到 model weights(§2.1.2)。Round-robin dispatch 只以 stage 序列定義,不依賴 iteration 邊界,所以 iteration $T$ 可以從 iteration $T-1$ 結束處接續分派,無需 pipeline flush。

**Key Formulas:**

Staleness-1 update rule(論文未列數學式,以下為標準形式之概念整理):

$$
W^{(T+2)} = W^{(T)} - \eta \cdot \text{Adam}(G^{(T)}, m^{(T-1)}, v^{(T-1)})
$$

論文引用既有研究(ZeRO-Offload [40]、[24])表明 1-step staleness 不傷害 convergence。

**Implementation Details:**

由 dedicated optimizer worker (CPU) 執行 Adam step,GPU workers 同時計算下一 iteration。具體 staleness 邊界與 master/optimizer copy 的同步由 §5.3.6 的 event-based protocol 維護。

---

#### 5.3.5 Multi-Stream Transfer Architecture & LPT Scheduling

**Function:** 用 4 條 communication stream + 1 條 compute stream 充分利用 PCIe 雙向頻寬,並把非關鍵的 parameter/gradient transfer 排入 activation transfer 的閒置窗口。

**Input:**
- Name: 待傳輸的張量集合(activation, parameter, gradient)
- Shape: activation $[B, s, d]$、parameter $P_i$、gradient $G_i$
- Source: host memory / GPU memory

**Output:**
- Name: 排程後的 transfer schedule
- Shape: 每個 data-transfer window 內的 (activation, parameter chunks) 配對
- Consumer: PCIe link、GPU compute stream

**Processing:**

每張 GPU 維持 4 條 dedicated stream:activation upload、activation download、parameter upload、gradient download,加上 compute stream。Activation 上傳/下傳分別比 compute 提早/延後一個 micro-batch,以避免阻塞 compute。Parameter/gradient 切成 $M$ 個 chunk,排入 activation 之間的閒置 window。Compute stream 與 activation transfer stream 在 micro-batch 粒度透過 CUDA event 同步,把時間線切成有界的 data-transfer window,避免 in-flight data 過多導致 OOM。

**Key Formulas:**

LPT scheduling:把 parameter/gradient tensors 按大小降序排列,每個 tensor 指派到目前累計傳輸量最小的 window;極大 tensor (例如 LM head) 先切片再排程。論文未給出 closed-form bound,引用 Graham 1969 [13] 為理論依據。

**Implementation Details:**

對應 Figure 6 vs Figure 7 的對比:Figure 6 的單 stream overlap 出現 head-of-line blocking,Figure 7 的多 stream + chunked 排程消除了該 blocking。「sufficient overlap」門檻(roofline 分析)為 dense model $B = 8$、MoE model $B = 80$。

---

#### 5.3.6 Fine-Grained Event-Based Consistency Protocol

**Function:** 在不阻塞 pipeline 的前提下,維持 master copy (P)、optimizer copy (G)、GPU transient copy 三者的 staleness-1 一致性。

**Input:**
- Name: 五個 ordering constraint 對應的事件依賴
- Shape: per-layer threading events(每個 layer 各自一組事件)
- Source: controller + optimizer worker + GPU workers

**Output:**
- Name: 同步後的 master/optimizer/transient copy 三組 weights/gradients
- Shape: per-layer 一致的張量
- Consumer: 後續 iteration 的 forward/backward

**Processing:**

論文歸納出五條 ordering constraint:
1. P copy 須等 GPU 完成上一 iteration 的 parameter upload
2. GPU 須等 P copy 完成才能上傳下一 iteration 的 parameter
3. G copy 須等 GPU 完成上一 iteration 的 gradient download
4. GPU 須等 G copy 完成才能寫入下一 iteration 的 gradient
5. Optimizer step 與 P/G copy 在 optimizer worker 內部依序執行

Blocking copy(Figure 8a)把 step() 視為硬 barrier,重新引入 pipeline bubble。RoundPipe 把 weight/gradient copy offload 到 optimizer worker,以 per-layer event 表達依賴(Figure 8b 的四條箭頭即 (1)–(4))。Layer 1(最淺層)位於 backward 結束與下一 forward 開始的緊接點,若以 model-level 同步會阻塞 layer 1;改為 per-layer event 後,optimizer worker 可在處理完早期 layer 後立即釋放對應 event,讓 GPU worker 開始 layer 1 的下一 forward,而較深的 layer 仍在同步中。

**Key Formulas:**

論文未提供形式化的事件代數,僅以五條 ordering constraint 與四條 dependency edge 表達(Figure 8b)。

**Implementation Details:**

事件採 point-to-point signaling,由 controller 動態建立並分派給 GPU/optimizer worker 等待或設定。對應 §4.3 與 §5.6.2 的 ablation:fine-grained protocol 相對 blocking copy 每 iteration 省下 2.6–14 秒,Qwen3-235B-LoRA 因更新參數量小所以提升較少。

---

#### 5.3.7 Automatic Stage Partitioning Algorithm

**Function:** 在 GPU memory 限制下,自動求出近似最佳的 forward/backward 非對稱 partition,最小化 pipeline 總 GPU 時間。

**Input:**
- Name: per-layer 的 forward/backward execution time 與 memory footprint
- Shape: 長度 $L$ 的時間/記憶體向量(profile 自前幾個 iteration)
- Source: 訓練啟動時的 profiling 階段

**Output:**
- Name: forward partition $(F_1, \ldots, F_{S_f}, B_1)$ 與 backward partition $(B_1, B_2, \ldots, B_{S_b})$
- Shape: 兩組 layer 數序列
- Consumer: §5.3.2 的 round-robin dispatcher

**Processing:**

最佳化目標(對應 §3.3 的公式):

$$
\min \; (M \cdot S + N \cdot (N - 1)) \cdot t_{\max}
$$

關鍵觀察:每個 stage 必須包含 contiguous layer,因此 $t_{\max}$ 的可能值僅限於 forward/backward 時間的 contiguous subsequence sum,共 $O(L^2)$ 個候選值。對每個候選 $t_{\max}$,問題化簡為:找出最小 partition 數,使每個 partition 的總時間 $\leq t_{\max}$ 且 memory 不超 GPU 容量。此 sub-problem 為經典 greedy 問題,$O(L)$ 線性掃描可解。整體複雜度:候選 $t_{\max}$ $\times$ greedy 掃描 $= O(L^3)$。

Greedy 過程中,演算法會優先把第一個 backward stage 填滿,因為 fused $B_1$ stage 跳過了 activation recompute,$B_1$ 越大則 saved compute 越多。

**Key Formulas:**

複雜度上界:

$$
T_{\text{partition}} = O(L^2) \cdot O(L) = O(L^3)
$$

**Implementation Details:**

實測 wall-clock(§5.6.1):Qwen3-1.7B、LLaMA-3.1-8B、GPT-OSS-20B、Qwen3-32B 分別為 2.9、2.9、2.6、5.0 ms;Qwen3-235B(94 層)為 1.47 秒,相對訓練數小時可忽略不計。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| the paper does not specify | LLM fine-tuning throughput / max-sequence-length micro-benchmark | sequence length 2048 (default); global batch sizes 512 / 256 / 128 / 128 / 64 for the five evaluated models | training-throughput micro-benchmark only (no held-out val/test split reported) |

備註：論文未指定實際 fine-tuning corpus，所有實驗皆以合成輸入量測 system-level throughput 與最大可訓練 sequence length，並非 task-accuracy benchmark。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Training throughput (tokens/s) | 暖機後 10 個 iteration 的 steady-state token/s 平均值 (§5.1) | yes |
| Maximum sequence length | micro-batch size = 1 下不發生 OOM 的最長 sequence length (§5.1) | yes |
| Pipeline bubble ratio (%) | 以 per-layer timing 重放 schedule 的 simulator 量測 idle 比例 (§5.6.1) | no |
| Per-iteration time (s) | blocking copy vs. event-based protocol 的單 iteration 牆鐘時間 (§5.6.2) | no |
| Partitioning wall-clock time (ms / s) | 自動分段演算法執行時間 (§5.6.1) | no |

### 6.3 Training and Inference Settings

- **Hardware (§5.1)**：兩台 8-GPU 單機伺服器。
  - 4090 server：8× RTX 4090 (24 GB)、Intel Xeon Gold 6330、800 GB DDR4、PCIe 4.0 (32 GB/s)。
  - A800 server：8× A800 SXM (80 GB HBM2e)、Intel Xeon Platinum 8352Y、800 GB DDR4、NVLink 3.0 (200 GB/s)。
- **Models (§5.1, Appendix Table 3)**：Qwen3-1.7B、LLaMA-3.1-8B、GPT-OSS-20B (MoE, $E_{\text{act}}=4$, $E=32$)、Qwen3-32B、Qwen3-235B-A22B (MoE, $E_{\text{act}}=8$, $E=128$)。
- **Training mode**：前四個模型做 full-parameter training；Qwen3-235B 僅做 LoRA fine-tuning ($r=32$)。
- **Precision & memory**：所有 framework 一律 mixed-precision (FP16) + full activation recomputation；checkpointed activation 也 offload 到 host DRAM (§2.1.1)。
- **Batch / sequence**：sequence length 預設 2048；global batch size 依模型分別為 512 / 256 / 128 / 128 / 64；每個 framework 在「不 OOM」且「micro-batch 數 $\geq 8$」前提下個別調至最大 micro-batch。
- **Optimizer**：Adam-class CPU-side optimizer，預設啟用 staleness-1 asynchronous update (§2.1.2)；RoundPipe-sync 為關閉非同步、改走 synchronous CPU optimizer step 的對照組。
- **Baselines (§5.1)**：DeepSpeed ZeRO-2、PyTorch FSDP (ZeRO-3 DP)、DeepSpeed ZeRO-Infinity、Megatron-PP、Megatron-TP、Mobius，以及內部對照 RoundPipe-sync。
- **Inference settings**：the paper does not specify (本論文僅評估 training，不報告 inference)。
- **Roofline / activation 計算細節**：見 Appendix B (activation size 公式 (12 + 4k/a)·sbh + 6sbm·E_act bytes per layer) 與 Appendix C (FLOPS 與 OI 推導)。

### 6.4 Main Results

**4090 server (8× RTX 4090, Figures 9 & 10)**

| Method | Throughput (tokens/s) | Max sequence length | Notes |
|---|---|---|---|
| ZeRO-2 / FSDP / ZeRO-Infinity / Megatron-PP / Mobius | 多數於 20B+ 模型 OOM；Mobius 為現有 PP+offload 對照 | 多數模型 OOM | 1.7B–8B 仍可跑，20B 起逐一 OOM (Figure 9 標註) |
| Megatron-TP | 在 Qwen3-1.7B 上 sequence length 與 RoundPipe 同級 | 在小模型上靠 activation sharding 取得長序列 | PCIe 下 throughput 不切實際；Qwen3-235B-LoRA 因 $k=4$ 不支援 TP=8，標 N/A |
| RoundPipe-sync | 1.15–1.63× 超過最佳既有系統 | 與 RoundPipe 相同 | 同步 CPU optimizer step |
| **RoundPipe** | **1.48–2.16× 超過最佳既有系統 (1.7B–32B)；唯一可在 24 GB GPU 上 LoRA 訓練 Qwen3-235B** | **較次佳 baseline 長 4.7–7.3×（排除 Megatron-TP 後）** | 1→8 GPU 下五個模型最大 sequence length 分別為 73K / 49K / 39K / 28K / 31K (§5.4) |

**A800 server (8× A800 SXM, Figures 11 & 12)**

| Method | Throughput (tokens/s) | Max sequence length | Notes |
|---|---|---|---|
| ZeRO-2 / FSDP | 在 1.7B / 8B 小模型上靠 NVLink 取得最佳 throughput | 大模型 OOM | DP 在小模型佔優 |
| ZeRO-Infinity | 與 RoundPipe-sync 相當 | 不 offload activation，較早 OOM | 慢於 RoundPipe 的差距來自 CPU optimizer step |
| Megatron-PP | Qwen3-32B 上 OOM（最後一個 rank 8 層 + LM head） | — | — |
| Megatron-TP | 小模型 sequence length 達 108K–242K | — | Qwen3-235B-LoRA 標 N/A |
| **RoundPipe** | **0.98–1.47× 超過 SoTA；4090 上的 RoundPipe 仍達 A800 SoTA 的 ≥76%** | **1.19–5.62× 超過 baselines；小模型推到 192K–288K** | 不使用任何 NVLink P2P，全靠 PCIe host↔device 傳輸 |

註：Mobius 在 A800 上被略過，因其在 datacenter GPU 上反而慢於 ZeRO-Infinity (§5.3)。

### 6.5 Ablation Studies

- **Pipeline schedule (§5.6.1, Figure 15)**：以 per-layer timing 重放 GPipe / 1F1B / Interleaved-1F1B / Looped-BFS / RoundPipe-sync / RoundPipe 六種 schedule 在 8 GPU、16 micro-batches 下的 bubble ratio。RoundPipe-sync 比最佳 baseline 降 23–55%；開啟非同步 optimizer 後絕對 bubble ratio < 4.5%。此 ablation 直接對應論文核心主張（asymmetric splitting + round-robin dispatch 能同時壓低 structural 與 imbalance bubble），屬 diagnostic 而非 sanity check。
- **Automatic stage partitioning wall-clock (§5.6.1)**：Qwen3-1.7B / 8B / 20B / 32B 分段時間為 2.9 / 2.9 / 2.6 / 5.0 ms；Qwen3-235B (94 層) 為 1.47 s。屬 cost sanity check，僅證明 $O(L^3)$ 可忽略，不直接量「partition 品質」（品質間接由 bubble ratio 反映）。
- **Fine-grained parameter consistency protocol (§5.6.2, Figure 16)**：以 blocking copy 為對照組，比較 per-iteration time。event-based protocol 每 iteration 省 2.6–14 s，省幅隨 trainable parameter 大小成長；Qwen3-235B-LoRA 因 trainable 較少而省得最少。此 ablation 精準對應 §4.3 設計，屬 diagnostic experiment。
- **缺漏的 ablation**：論文未單獨拆出 (a) priority-aware transfer scheduling engine（multi-stream + LPT chunking）關閉時的影響；(b) asymmetric vs. symmetric stage splitting 的單獨對照（asymmetric 的效益僅在整體 schedule 比較中隱含呈現）；(c) RoundPipe 在不同 micro-batch 數 $M_R$ 下的敏感度。這些是會直接驗證 §4.2 與 §3.2 個別組件的 diagnostic 實驗。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 同時對比 DeepSpeed ZeRO-2 / ZeRO-Infinity、PyTorch FSDP、Megatron-PP、Megatron-TP、Mobius 六個現役 SoTA training framework (§5.1)。
- [partial] Has cross-task / cross-dataset evaluation — 涵蓋 5 個不同規模與架構的模型（含 dense 與 MoE、含 LoRA 與 full-param），但任務面僅為 fine-tuning throughput 微基準，未跨多個下游 dataset / task。
- [covered] Has ablations that diagnose the new components — §5.6.1 對應 RoundPipe schedule、§5.6.2 對應 event-based consistency protocol，皆為診斷型 ablation 而非 sanity check。
- [covered] Has a scaling study — §5.4 報告 1→8 GPU strong scaling 與 GPU 數無關的 max sequence length；§5.5 報告 Qwen3-1.7B 在 512–64K sequence length 上的 throughput。
- [covered] Has an efficiency / wall-clock comparison — 主要指標即 throughput 與 per-iteration wall-clock（§5.2、§5.3、§5.6.2），並有跨硬體（4090 vs. A800）絕對時間比較。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — throughput 僅報 10 個 iteration 的平均值，未提供標準差、信賴區間或多 seed 結果 (§5.1)。
- [covered] Releases code / weights / data sufficient for reproducibility — 摘要明示開源於 https://github.com/ITcarrot/RoundPipe 並附 https://itcarrot.github.io/RoundPipe/ 文件；模型皆為公開權重，硬體與超參設定於 §5.1 與 Appendix Table 2、Table 3 詳列。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 識別 weight binding 是現有 PP 排程在消費級 GPU 上失效的根因。** *Supported.* §2.3 與 Figure 1(a)(b) 給出 trade-off 形式化,Figure 3 給出 8 GPU 上 ideal vs real bubble ratio 的差距(最高 30%),Figure 15 用 simulator 進一步把問題歸因到 stage execution imbalance。
- **Claim 2: Computation Dispatch Paradigm 是 throughput-preserving 的重組,不引入額外通訊瓶頸。** *Supported.* §3.3 的 roofline 分析(Appendix C)給出 OI 與 batch size 關係,並在 Figure 17 證明 dense $B \geq 8$、MoE $B \geq 80$ 即進入 compute-bound;§5.3 在 A800 上跑出 0.98–1.47× 的吞吐,實證重組未犧牲峰值。
- **Claim 3: RoundPipe 排程逼近 zero-bubble。** *Partially supported.* Figure 15 的 simulation 顯示 RoundPipe(async)<4.5%,但這是模擬而非實機 trace breakdown;Figure 9 的 1.48–2.16× 加速包含了 transfer engine 與 consistency protocol 的貢獻,排程本身對加速比的隔離貢獻並未被單獨拆出。
- **Claim 4: 在 8×4090 上對 1.7B–32B 取得 1.48–2.16× 吞吐並支援 235B LoRA。** *Supported.* Figure 9 與 Figure 10 直接展示;235B LoRA 在 24 GB GPU 上的可行性是其他系統做不到的硬指標。
- **Claim 5: 自動切分演算法以 $O(L^3)$ 達成近最佳負載平衡。** *Supported(複雜度部分);Partial(最佳性部分).* §5.6.1 給出 ms 級壁鐘時間支持複雜度主張,但「near-optimal」只透過殘餘 bubble <4.5% 間接論證,沒有與 ILP / brute-force 最佳解的差距比較。
- **Claim 6: RoundPipe 把 4090 提升到 A800 級訓練時間。** *Overclaimed.* §5.3 自述「at least 76% of A800」屬實,但「effectively bridging the performance gap」忽略了在小模型 + NVLink-rich 場景 DP 仍是更佳選擇,亦未納入 cost-per-token 或能耗等說服 democratization 主張的關鍵指標。

### 7.2 Fundamental Limitations of the Method

**1. Staleness-1 是論證的隱含前提,而非本文驗證的結論。** RoundPipe 的「iteration 邊界 bubble = 0」完全建立在 async optimizer 上,而 async semantics 的正確性、收斂率、對 fine-tuning quality 的影響,作者全部外包給 [24, 40]。一旦使用者需要嚴格 synchronous 訓練(例如某些 RLHF / preference 微調流程),RoundPipe 就退化為 RoundPipe-sync,加速比也從 1.48–2.16× 縮到 1.15–1.63×,這個 degradation 不是工程問題而是 paradigm 邊界。

**2. Computation Dispatch 的價值與 PCIe / offloading 強耦合。** §5.3 在 A800(NVLink + 80 GB HBM2e)上對 1.7B 與 8B 模型反而被 DP 略勝,且作者承認這時 NVLink 才是優勢來源。這代表 RoundPipe 的設計收益隨著「GPU memory 充足且互聯快」單調縮小,並不是一個普適的 schedule 改進,而是 PCIe-bound 場景下的特化解。

**3. 全部評測停在 single 8-GPU server,無 multi-node 擴展證據。** 一旦跨 node,bandwidth hierarchy 改變(NIC 與 PCIe 競爭、host memory 不再是均勻可達),round-robin dispatch 的均勻假設與 priority-aware engine 的 idle-window packing 都會重新定義;作者未說明 paradigm 在 NIC/RDMA 路徑上如何處理,也沒有給出 multi-server scaling 曲線,這對 democratization 主張是個結構性空缺。

**4. 控制平面是單點。** §4.1 的 single-controller 架構(Ray / HybridFlow style)在效能上合理,但對長時間 fine-tuning 場景缺少 checkpoint、failover 或 stage-level retry 的討論;optimizer worker 同樣是 single instance,當其 CPU 步驟意外停滯,async pipeline 會立即累積 staleness > 1,這在 commodity hardware(更易出現 PCIe link reset / memory ECC error)上不是邊緣情境。

### 7.3 Citations Worth Tracking

- **Mobius (Feng et al., ASPLOS'23, [12])** RoundPipe 直接的前作與最關鍵 baseline,理解 PP+offloading 的 weight binding 問題與 PCIe 70% communication 主張的源頭都需要先讀這篇。
- **Zero-Bubble Pipeline (Qi et al., ICLR'24, [36])** 另一條消除 bubble 的路線(reorder + delayed weight update),與 RoundPipe 的「打破 weight binding」形成對照,有助於判斷 schedule 設計空間還有哪些未被覆蓋的軸。
- **ZenFlow (Lan et al., 2025, [24])** RoundPipe 引用作為 staleness-1 收斂保證的依據之一,如果要評估 RoundPipe 在實際工作流的可信度,必須讀這篇了解 async update 在非 LM-head workload 上的行為。
- **ZeRO-Offload (Ren et al., ATC'21, [40])** 三份權重副本(transient / master / optimizer)的設計與 host-side optimizer 模式都源於此,是讀懂 §4.3 五條 ordering constraint 的前置。
- **HybridFlow / veRL (Sheng et al., EuroSys'25, [43])** §4.1 single-controller 架構直接借鑒,有助於理解 RoundPipe 控制平面在 RLHF / agentic 訓練下的延伸能力。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在 multi-node(2+ servers,NIC over Ethernet/IB)情境下,round-robin dispatch 是否仍保持 <4.5% bubble?跨 node activation transfer 的 critical path 與 PCIe idle window packing 如何重新對齊?
- [ ] Asymmetric stage splitting 與 staleness-1 async update 對下游品質(loss、benchmark accuracy、RLHF reward)的影響為何?LM head 的 forward / backward 切分是否會放大梯度方向的偏置?
- [ ] Auto-partition 只在「first few iterations」抽樣,當 sequence length 動態變化(packing、curriculum、長尾長度)或 MoE routing 不均時,partition 是否需要重新計算的檢測機制?
- [ ] 將 RoundPipe 與 expert parallelism 共部署於 MoE(例如 235B-A22B 的 128 experts)時,$E$ 個 expert 的 weight transfer 在 priority-aware engine 下會否擠壓 activation 的 idle window?
- [ ] 當 host memory 不夠裝下 master weight + activation(超大 context + 超大模型),把 NVMe 加入 offload 階層後 priority-aware engine 的 LPT 排程是否仍最佳?
- [ ] 在 NVLink-rich 系統(A800 / H100)上,何時應退回標準 DP / TP?是否存在自動偵測 paradigm 切換點的指標(例如 OI 與 ridge point 的距離)?
- [ ] Single optimizer worker 與 single controller 在長時間訓練下的故障模式為何?staleness 在 worker 暫時 stall 下會否累積 >1 而違反 §2.1.2 的收斂條件?

### 8.2 Improvement Directions

1. **加上 per-step 收斂驗證實驗(low effort, high value).** 即便不做完整 pretraining,也應在至少一個 fine-tuning workload 上提供 RoundPipe vs RoundPipe-sync vs DP 的 loss curve 與 task accuracy。本文目前完全外包此論證,加上即可大幅提升結論可信度。
2. **將 auto-partition 改為線上自適應(medium effort).** 既然 timing collection 已有 hook,當實測 stage time variance 超過閾值時觸發重新切分,可解決 §4.4 假設「工作負載穩態」失效的情境(動態 packing、長尾 batch)。理論基礎為 $O(L^3)$ 演算法 5 ms–1.5 s 的成本相對 iteration 級別可忽略。
3. **多階層 offload(medium-high effort).** 把 priority-aware engine 從 PCIe 二端 (host↔device) 擴成三層 (NVMe↔host↔device),用相同 LPT 思想在更大的 idle window 排程,可把 RoundPipe 的「最大 model 規模」進一步突破 host DRAM 上限。基礎來自 ZeRO-Infinity 的 NVMe 路徑。
4. **Multi-node 擴展(high effort).** 在 round-robin 中加入 locality-aware tier(node-local round-robin → cross-node round-robin),並把 NIC 加入 priority engine 作為第三條 channel。該方向能驗證 Computation Dispatch Paradigm 是否為通用 schedule 設計而非 single-server hack。
5. **Controller / optimizer worker 的容錯(high effort).** 引入 stage-level checkpoint(每 R 個 round 保留 master copy snapshot)與 optimizer worker 的 watchdog,在 commodity hardware 場景下避免單一 stall 立即累積 staleness。對 democratization 主張至關重要,因為消費級伺服器的故障率本來就高於 datacenter。
