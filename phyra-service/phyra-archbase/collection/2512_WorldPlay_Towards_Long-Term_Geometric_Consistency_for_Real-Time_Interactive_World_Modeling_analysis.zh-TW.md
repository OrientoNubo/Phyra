<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# WorldPlay — WorldPlay: Towards Long-Term Geometric Consistency for Real-Time Interactive World Modeling

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | WorldPlay |
| Paper full title | WorldPlay: Towards Long-Term Geometric Consistency for Real-Time Interactive World Modeling |
| arXiv ID | 2512.14614 |
| Release date | 2025-12-16 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2512.14614 |
| PDF link | https://arxiv.org/pdf/2512.14614v1 |
| Code link | https://github.com/Tencent-Hunyuan/HY-WorldPlay |
| Project page | https://3d-models.hunyuan.tencent.com/world/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Wenqiang Sun | Hong Kong University of Science and Technology; Tencent Hunyuan | https://github.com/wenqsun | first author (equal contribution); PhD student at HKUST ECE under Prof. Jun Zhang |
| Haiyu Zhang | Beihang University; Tencent Hunyuan | — | co-first author (equal contribution) |
| Haoyuan Wang | Tencent Hunyuan | https://www.whyy.site/ | co-first author (equal contribution) |
| Junta Wu | Tencent Hunyuan | — | co-author |
| Zehan Wang | Tencent Hunyuan | — | co-author |
| Zhenwei Wang | Tencent Hunyuan | — | co-author |
| Yunhong Wang | Beihang University | — | co-author |
| Jun Zhang | Hong Kong University of Science and Technology | https://eejzhang.people.ust.hk/ | corresponding author; Professor at HKUST ECE, IEEE Fellow |
| Tengfei Wang | Tencent Hunyuan | https://tengfei-wang.github.io/ | corresponding author; researcher at Tencent Hunyuan leading world-model team |
| Chunchao Guo | Tencent Hunyuan | — | corresponding author; Principal Research Scientist and Hunyuan 3D leader at Tencent |

### 1.2 Keywords

world model, interactive video generation, video diffusion, autoregressive diffusion, long-term geometric consistency, memory-augmented generation, distillation, real-time generation

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Oasis [9] | baseline | Distillation-based real-time interactive Minecraft world model; speed-prioritized but lacks long-term memory. |
| Matrix-Game 2.0 [17] | baseline | Real-time general-domain interactive world model with discrete action; suffers scene-revisit inconsistency. |
| GameCraft [31] | baseline | Continuous-action 720p general-domain world model; not real-time and limited long-horizon support. |
| WorldMem [67] | predecessor | Implicit FOV-based memory retrieval for consistency; Minecraft-only and not real-time. |
| VMem [32] | predecessor | Explicit 3D memory for static scenes via continuous camera control; not real-time, static-scene only. |
| CausVid [72] | influence | Distills bidirectional teacher into causal autoregressive student; basis for memory-aware Context Forcing. |
| Self-Forcing [21] | influence | Refines CausVid rollout to mitigate exposure bias; extended here with memory alignment. |
| Diffusion Forcing [6] | base model | Chunk-wise autoregressive diffusion training enabling next-chunk prediction used as WorldPlay's backbone. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於即時互動式世界模型 (real-time interactive world modeling) 的視訊生成任務,目標是讓模型在使用者持續以鍵盤與滑鼠輸入控制視角與動作時,能以串流方式 (streaming) 自迴歸地預測下一段 16 frame 的 720p 影片,同時兼具低延遲互動 (24 FPS) 與長時程幾何一致性 (long-term geometric consistency)。研究領域橫跨視訊擴散模型 (video diffusion)、自迴歸生成 (autoregressive generation)、3D-aware 場景生成、模型蒸餾 (distillation) 與記憶機制 (memory-augmented generation),並涵蓋第一人稱與第三人稱、寫實與風格化場景的通用世界建模,亦延伸至 3D 重建與文字觸發的可提示事件 (promptable events) 等下游應用。

### 2.2 Domain Tags

- computer vision
- generative AI
- video diffusion
- world models
- interactive 3D

### 2.3 Core Architectures Used

- **Diffusion Transformer (DiT) with 3D causal VAE**:作為 backbone 的 latent video diffusion 架構,每個 DiT block 由 3D self-attention、cross-attention 與 FFN 組成,並以 flow matching 訓練 latent video 的速度場 $v_k = z_0 - z_1$。
- **Diffusion Forcing 風格的 chunk-wise autoregressive diffusion**:把 full-sequence DiT 微調為以 4 個 latent ($\approx$ 16 frames) 為單位的 chunk-level 自迴歸生成器,各 chunk 賦予不同 noise level 並改用 block causal attention,使模型能在串流條件下進行 next-chunk prediction。
- **Dual Action Representation**:本論文提出的雙模態動作介面,將離散按鍵 (W/A/S/D) 透過 PE 與 zero-init MLP 注入 timestep embedding 以調制 DiT,連續相機姿態 $(R, T)$ 則以 PRoPE 形式作為相對位置編碼注入 self-attention,提供尺度自適應控制與精準空間索引。
- **Reconstituted Context Memory with Temporal Reframing**:本論文提出的記憶模組,動態從歷史 chunks 重建出時間鄰近 ($C^T_t$) 與基於 FOV 重疊與相機距離挑選的空間相關 ($C^S_t$) 上下文,並重新指派 RoPE 的位置編碼,將遠程關鍵 frame 在時間軸上「拉近」以避免 RoPE 外推衰減。
- **Context Forcing 蒸餾架構**:本論文提出的記憶感知蒸餾,讓 memory-augmented bidirectional teacher 與 causal student 在對齊的記憶上下文 $C_{j:j+3} - x_{j:j+3}$ 下做 distribution matching (DMD-style reverse KL),把 multi-step diffusion 蒸餾為 4-step real-time 生成器,同時保留長程記憶並抑制 error accumulation。
- **Streaming inference stack**:結合 sequence parallelism 與 attention parallelism 的混合並行、NVIDIA Triton 上的漸進式 VAE 解碼,以及 Sage Attention、float / matmul quantization 與 KV-cache,在 8×H800 上達成 720p 24 FPS 串流互動。

### 2.4 Core Argument

作者識別出當前互動式世界模型存在一個根本性的「速度 vs. 記憶」權衡:一類方法 (如 Oasis、Matrix-Game 2.0) 透過蒸餾達到即時速度,卻犧牲了重訪場景時的幾何一致性;另一類方法 (如 WorldMem、VMem) 引入顯式或隱式記憶以維持一致性,但複雜的記憶結構讓蒸餾難以收斂,因而無法即時。為同時擊破兩端的瓶頸,WorldPlay 主張必須從三個層面共同設計才合乎邏輯。第一,動作表示必須兼具「尺度自適應」與「精準空間定位」:純離散按鍵 (W/A/S/D) 雖能在不同尺度場景穩定學習,卻對記憶檢索而言位置模糊;純連續相機姿態 (R, T) 雖能精確定位,卻因訓練資料尺度差異造成不穩定。Dual Action Representation 將兩者並用,離散鍵調制 timestep,連續相機透過 PRoPE 注入 self-attention,因此既能穩健控制又能為記憶模組提供精確空間索引。第二,要解決長序列下 RoPE 相對距離無界增長造成「遠程記憶被衰減」的問題,Reconstituted Context Memory 動態挑選時間鄰近與空間相關 (FOV 重疊+相機距離) 的歷史 chunk 作為上下文,並以 Temporal Reframing 重新指派位置編碼,把幾何上重要的久遠 frame 「拉近」時間軸,迫使模型把它們視為近期記憶,從而避免外推偽影並維持一致性。第三,既有蒸餾方法假設 teacher 是無記憶的雙向模型,與記憶感知的因果 student 之間存在不可調和的條件分布錯配 p(x|C) misalignment,因此 Context Forcing 對 teacher 也施加與 student 對齊的記憶上下文,讓兩者在相同記憶條件下進行 distribution matching,如此才能在保留長程記憶的前提下蒸餾出 4-step 即時生成器。三項設計缺一不可,共同構成「即時 × 長程一致」這一目標的最小充分條件。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「WorldPlay: Towards Long-Term Geometric Consistency for Real-Time Interactive World Modeling」一次性鎖定本論文的兩個核心張力：real-time（即時性）與 long-term geometric consistency（長期幾何一致性）。Abstract 直接點名這是一個 streaming video diffusion model，並把 speed 與 memory 之間的 trade-off 定義為當前 interactive world model 領域的關鍵未解問題，這也是後續整篇 narrative 的主軸。

接著 abstract 以三點 key innovations 構成全文骨架：(1) Dual Action Representation 處理 user 鍵鼠輸入的控制問題；(2) Reconstituted Context Memory 透過動態重建 context 與 temporal reframing 解決長期記憶衰減；(3) Context Forcing 是一種針對 memory-aware model 的 distillation 方法，藉由對齊 teacher 與 student 的 memory context 來在保留長程資訊的同時達成 real-time。

最後 abstract 給出量化承諾：720p、24 FPS 的長 horizon streaming video generation，並宣稱在多樣場景上具有 superior consistency 與 strong generalization。這段同時釘住 evaluation regime 的數字，讓讀者在進入 §4 與 §5 前就已知道要驗證的是「速度 × 一致性 × 通用性」三個維度，為 introduction 鋪設清楚的 expectation。

### 3.2 Introduction

(720 words)

Introduction 分四段推進。第一段把 world models 定位為從 language-centric 邁向 visual / spatial reasoning 的轉折點，並把 real-time interactive video generation 視為前沿任務，目標是 autoregressively 預測未來 frame chunks 以對 user 鍵盤指令給予即時回饋。

第二段直接提出核心 dilemma：speed 與 long-term geometric consistency 難以同時達成。作者把現有方法分為兩類：第一類（如 Oasis、Matrix-Game 2.0）以 distillation 換取速度卻犧牲記憶，導致場景重訪不一致；第二類（如 WorldMem、VMem）使用 explicit 或 implicit memory 維持一致性，但複雜的 memory 使 distillation 難以套用。Table 1 被引用以總覽這個未解問題，將「同時 low-latency 與 high-consistency」明確定為本文要攻克的目標。

第三段宣告 WorldPlay 的問題公式化：把任務視為 next chunk（16 frames）prediction，建立在 autoregressive diffusion 之上，並一次列出三個 ingredients。Dual Action Representation 結合 discrete keys（W/A/S/D）與 continuous camera poses (R, T)，前者提供 scale-adaptive 控制但缺乏精確空間 anchor，後者提供精準位置但訓練不穩定，兩者結合可同時支援 robust control 與 accurate location caching，為後續 memory retrieval 鋪路。

接著介紹 Reconstituted Context Memory，其關鍵 move 是不只「retrieve」，而是「reconstitute」：先依空間與時間 proximity 動態重建 context set，再透過 temporal reframing 改寫 retrieved frames 的 positional embeddings，把幾何上重要但時間久遠的 frame「拉近」，避免 Transformer 中的 long-range decay 與超出 RoPE 訓練範圍的外推 artifact。這個 framing 直接回應 §1 提出的 memory 衰減難題。

第四段闡述 Context Forcing，作為支撐 real-time 的 distillation 方法。作者指出既有 distillation（CausVid、Self-Forcing 等）失敗的根因是 distribution mismatch：memory-aware autoregressive student 試圖 mimic memory-less bidirectional teacher；即便給 teacher 加上 memory，context 的不對齊仍會讓兩者條件分布發散。作者的解法是 explicit 對齊 teacher 與 student 的 memory context，讓 distribution matching 真正可行，從而在不犧牲記憶的前提下達成 4-step 的即時推理並抑制 error drift。

最後一段把三個 ingredients 收束為系統承諾：720p、24 FPS 的 streaming generation；以 320K real + synthetic 影片訓練；並透過 Fig. 1 預示 first-/third-person、real / stylized 場景與 3D reconstruction、promptable event 等延伸應用。Introduction 因此同時完成了 problem framing、方法概述與 evaluation 範圍預告，為 §2 比對相關工作、§3 展開技術細節做好過渡。

### 3.3 Related Work / Preliminaries

(900 words)

§2 Related Work 與 §3.1 Preliminaries 共同負責定位與奠基。Related Work 分三條 narrative：Video Generation、Interactive and Consistent World Models、Distillation，刻意對應 §1 的三個 ingredients。

Video Generation 一段交代 diffusion model 已成為 video generative modeling 的主流，從 latent diffusion 進到 autoregressive video generation，並以 web-scale 資料展現 zero-shot 的世界感知能力，為將 video diffusion 用作 world model 奠定可行性。

Interactive and Consistent World Models 是本節的論辯核心。作者先指出現有 world model 多以 discrete 或 continuous action 控制 agent 與 virtual environment，再依「如何維持幾何一致性」分為兩派：explicit 3D reconstruction 派（Gen3C、VMem 等）依賴重建品質，難以支援長期一致性；implicit conditioning 派（WorldMem、Context-as-Memory）以 FOV 檢索歷史 frame，scalability 較佳但 real-time 仍未解。這段直接把 WorldPlay 定位在「implicit memory + real-time」的交集，並透過 Table 1 對比 Oasis、Matrix-Game 2.0、GameGen-X、GameCraft、WorldMem、VMem，凸顯只有 WorldPlay 同時具備 720p、Continuous + Discrete action、real-time、long-term consistency、long-horizon 與 general domain 六項能力。

Distillation 段落為 §3.4 Context Forcing 鋪路。作者回顧 adversarial distillation 的不穩定與 mode collapse 問題、VSD-based 方法的少步生成能力，以及 CausVid 從 bidirectional teacher 蒸餾出 causal student、Self-Forcing 進一步修正 rollout 策略以解決 exposure bias。然後點出尚未被解決的問題：在 memory-aware 設定下保留 interactivity 與 geometric consistency。這段刻意留下空白，讓 §3.4 的 context forcing 自然填補。

§3 Method 的開頭把問題公式化為 $N_\theta(x_t \mid O_{t-1}, A_{t-1}, a_t, c)$，其中 $O_{t-1}$ 是過往觀察、$A_{t-1}$ 是動作序列、$a_t$ 是當前動作、$c$ 是 text 或 image prompt。這個 formulation 把後續所有模組都釘在「next chunk prediction conditioned on past observation + action」的軌道上，並預告 §3.2–§3.5 的章節順序：action representation → memory → distillation → streaming optimization。

§3.1 Preliminaries 提供兩塊基礎。第一塊是 Full-sequence Video Diffusion Model：以 causal 3D VAE 編碼 video latent $z_0$，DiT 由 3D self-attention、cross-attention、FFN 組成，diffusion timestep 透過 PE + MLP 來 modulate，訓練採 flow matching，loss 為

$$L_{FM}(\theta) = \mathbb{E}_{k, z_0, z_1}\left[\lVert N_\theta(z_k, k) - v_k \rVert^2\right],$$

其中 $z_k$ 為 $z_0$ 與 noise $z_1$ 的線性插值，$v_k = z_0 - z_1$。第二塊是 Chunk-wise Autoregressive Generation：因為 full-sequence DiT 是 non-causal，無法支援無限長 interactive generation，作者借鑑 Diffusion Forcing，把 video latent $z_0 \in \mathbb{R}^{C \times T \times H \times W}$ 分為 $T/4$ 個 chunk，每個 chunk 含 4 個 latents、可解碼為 16 frames；訓練時對每個 chunk 加入不同 noise level $k_i$，並把 full-sequence self-attention 改為 block causal attention。

這兩段 Preliminaries 同時完成兩件事：一是把 chunk = 16 frames 的設定固定下來，使後續所有 throughput 與 latency 數字（720p、24 FPS）可被讀者校準；二是建立 block causal attention 與 chunk-wise noise schedule 作為後續 §3.3 memory 與 §3.4 context forcing 的操作對象。整節結尾把舞台清空，讓 §3.2 起的三個 key ingredients 可以直接掛上來，論文 narrative 從「位置」過渡到「機制」。

### 3.4 Method (overview narrative)

(1100 words)

§3 Method 的整體 storyline 是：先把問題拆成 control、memory、distillation 三個正交軸，再用 §3.5 把工程加速層蓋上去，最後以 Fig. 2 的 pipeline 把四者收束為一個 streaming generator。

§3.2 Dual Action Representation for Control 是第一塊磚。作者先把現有作法的兩極（純 discrete keys 透過 MLP 注入；純 continuous camera pose）各自的 failure mode 講清楚：discrete keys 能應付不同尺度場景但無法為 memory retrieval 提供精確位置；continuous (R, T) 提供精準 anchor 但因訓練資料的 scene scale 變異導致訓練不穩定。WorldPlay 的解法是兩者並存——以 PE 加 zero-initialized MLP 編碼 discrete keys 並併入 timestep embedding 來 modulate DiT blocks；以 PRoPE 將 continuous camera frustum 注入 self-attention，借其 relative encoding 比 raymap 更具 generalizability 的特性。這個雙軌設計同時解了「robust control」與「location caching」兩件事，後者是 §3.3 spatial memory 能運作的前置條件。

§3.3 Reconstituted Context Memory 緊接著解 long-term consistency。作者先排除「全部 past frame 都當 context」的 naive baseline（運算上不可行、冗餘大），改採 reconstitute：對新 chunk $x_t$ 從 $O_{t-1}$ 重建 $C_t$，由兩部分組成——temporal memory $C^T_t$ 取最近 $L$ 個 chunk 確保 short-term motion 平滑，spatial memory $C^S_t$ 從非鄰近的 past frame 中以 FOV overlap + camera distance 的 geometric relevance score 取樣，避免長序列下的 geometric drift。重建之後的關鍵問題是：retrieved context 怎麼真正影響當前預測？作者指出 standard RoPE 之下，current chunk 與 past memory 的 relative distance 隨時間無界增長，最終會超出訓練 interpolation range 並弱化長程影響。Temporal Reframing 因此被提出：丟棄 absolute temporal index，重新分配 positional encoding，讓所有 context frame 與 current 之間維持固定且小的 relative distance，把幾何上重要的 past memory「拉近」，使其對當前預測仍具影響力。Fig. 4 以三圖（full context、absolute indices、relative indices）視覺化這個設計差異。

§3.4 Context Forcing 處理「real-time + memory」的 trade-off。作者先以 §1 的張力為起點：autoregressive 的 error accumulation 與 multi-step diffusion 的延遲，過去靠把 bidirectional teacher 蒸餾為 few-step autoregressive student 解決，formulation 為 distribution matching loss

$$\nabla_\theta L_{DMD} = \mathbb{E}_k\left(\nabla_\theta \mathrm{KL}\left(p_\theta(x_{0:t}) \,\|\, p_\mathrm{data}(x_{0:t})\right)\right).$$

然而在 memory-aware 場景下，teacher 通常是 short clip 訓練、無 memory 的 bidirectional model；即使加上 memory，bidirectional 與 causal 的本質差異仍會造成 conditional $p(x \mid C)$ 不對齊，使 distribution matching 失敗。Context Forcing 的核心 move 是把 memory context 一併對齊：student 以 self-rollout 方式生成 4 chunks，$p_\theta(x_{j:j+3} \mid x_{0:j-1}) = \prod_{i=j}^{j+3} p_\theta(x_i \mid C_i)$；teacher $V_\beta$ 則以 memory-augmented bidirectional model 構成，並 mask 掉 student 自身 rollout 的 chunk：

$$p_\mathrm{data}(x_{j:j+3} \mid x_{0:j-1}) = p_\beta(x_{j:j+3} \mid C_{j:j+3} - x_{j:j+3}).$$

這個對齊讓 teacher 的 distribution 盡量貼近 student，使 distribution matching 真正生效，進而在 4-step denoising 下保留 long-term consistency 並抑制 error accumulation；同時也避免 teacher 必須在 long video 與冗餘 context 上訓練，降低訓練成本。

§3.5 Streaming Generation with Real-Time Latency 是工程層的收束。為了在 8×H800 上達到 24 FPS、720p，作者採用三類優化：第一是 mixed parallelism——結合 sequence parallelism 與 attention parallelism，把每個 chunk 的 token 跨裝置切分以平均 workload；第二是 streaming deployment + progressive multi-step VAE decoding，藉 NVIDIA Triton 把 latent 一邊產生一邊以小 batch 解碼成 frame，壓低 time-to-first-frame；第三是 quantization 與 efficient attention，包括 Sage Attention、float quantization、matmul quantization 與 KV-cache。這三層讓前面三個 algorithmic 模組真正落地為 interactive streaming experience。

整個 §3 的敘事閉環是：dual action 為 memory 提供精準 anchor → reconstituted memory + temporal reframing 解決長程一致性 → context forcing 在不破壞 memory 的前提下完成 distillation → streaming engineering 把延遲壓到 real-time。每一段都針對前一段留下的副作用或瓶頸提出回應，使 §4 的 evaluation 可以同時對 speed、consistency、control 三軸下手。

### 3.5 Experiments (overview narrative)

(800 words)

§4 Experiments 的目的是同時驗證 §1 提出的三個承諾：long-term geometric consistency、real-time interactivity、generalization across diverse scenes。為此作者在 dataset、protocol、baseline、main result、ablation、application 六層展開。

Dataset 以 320K clip 規模刻意組合 real-world footage 與 synthetic environment。Real-world 部分先從公開來源 [Sekai, DL3DV] 篩除短片、低品質、有 watermark/UI、人群、抖動的片段；接著對 curated 影片做 3D Gaussian Splatting 重建，並沿 novel revisit trajectory 重新 render，再用 Difix3D+ 修補 floating artifact，多得 100K 高品質 real clip。Synthetic 部分包含 hundreds 個 UE 場景產出的 50K clip，與一個自建 game recording 平台收集的 170K 1st/3rd-person AAA 遊戲樣本。所有 clip 透過 vision-language model 產生 text annotation，缺少 camera 標註者由 VIPE 標出。這個資料配置直接服務 evaluation：revisit trajectory 是 long-term consistency 評估的前提，多樣場景是 generalization 的前提。

Evaluation Protocol 用 600 case（DL3DV、game video、AI-generated image）覆蓋短時與長時兩個 regime。短時設定下直接以 test trajectory 為輸入並對 GT frame 比較；長時設定則設計 cycle camera trajectory 強制 revisit，沿原路返回時將返程 frame 與初次經過的對應 frame 比較。指標分兩類：LPIPS / PSNR / SSIM 衡量視覺品質與一致性，$R_\mathrm{dist}$、$T_\mathrm{dist}$ 衡量 action 控制精度。Baseline 也分兩類：no-memory 的 action-controlled diffusion（CameraCtrl、SEVA、ViewCrafter、Matrix-Game 2.0、GameCraft）與 memory-equipped 的 Gen3C、VMem。

§4.1 Main Result 給出兩條 narrative。第一條是 short-term：WorldPlay 在 visual fidelity 上勝出、控制精度具競爭力；雖然 explicit 3D 方法在 rotation 上較準，但深度估計不準與尺度不一致使 translation 表現受限。第二條是 long-term：Matrix-Game 2.0 與 GameCraft 因缺乏 memory 表現崩落；Gen3C / VMem 雖有 explicit 3D cache 但受限於 depth 精度，作者主張 reconstituted context memory 的 implicit prior 更穩；context forcing 進一步抑制 error accumulation，使 visual quality 與 action accuracy 同時提升，且仍維持 real-time。Qualitative 比較（Fig. 6）以 first-/third-person、real / stylized 場景同時驗證 generalization。

§4.2 Ablation 把貢獻拆解到模組層級。Action representation 一節比對「只用 discrete」「只用 continuous」「dual」，顯示 discrete 缺乏細粒度控制、continuous 收斂困難，dual 取得最佳整體控制。RoPE design 一節對比 standard RoPE 與 reframed RoPE，後者在 visual metric 上明顯領先，並透過 Fig. 7 視覺化 error accumulation 與長程記憶衰減的差異。Context forcing 的 ablation 則對比兩種 misalignment：teacher 採 latent-level memory 選取會引發 collapse，過去的 self-rollout historical context 會引入 artifact；只有以乾淨 real-video sample 構成歷史 context 才能保留 distillation 品質。

§4.3 Application 把 evaluation 推向能力延伸。Long-term consistency 讓 [WorldMirror] 等 3D reconstruction model 能基於生成 frame 產出乾淨 point cloud（Fig. 1d）；text-based promptable event（Fig. 9）展示在 streaming 中即時觸發 smoke spread、balloon、rainbow 等動態事件，預示 navigation 之外的互動形式。整章節因此完成從 quantitative win → qualitative win → ablation 攻堅 → 應用泛化的四層論證，自然引導讀者進入 §5 的 Conclusion。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

§5 Conclusion 把全文壓縮成三個 take-away：WorldPlay 是同時具備 real-time interaction 與 long-term geometric consistency 的 world model；它讓使用者僅憑單張 image 或 text prompt 即可客製化獨特世界；雖然當前焦點在 navigation control，其架構已展現對 dynamic、text-triggered event 等更豐富互動形式的潛力。作者把貢獻定位為「control、memory、distillation 的系統性框架」，視之為通往 consistent + interactive virtual world 的關鍵一步。

Limitations 與 Future Work 留得相當精煉：作者承認延伸至更長 video duration、multi-agent interaction、複雜 physical dynamics 與更廣的 action 種類仍需進一步研究。整體收尾把研究野心延伸到 embodied agent 與 game development，但避開過度承諾，與 §1 的問題定義形成首尾呼應。

## 4. Critical Profile

### 4.1 Highlights

- 在 8×H800 GPU 上以 4-step denoising 達到 720p、24 FPS 的串流互動生成,將「real-time」與「long-term consistency」兩個目標首次同時打通(Sec. 3.5, p.6;Table 1, p.3)。
- Long-term (≥250 frames) 設定下取得 PSNR 18.94、SSIM 0.585、LPIPS 0.371,顯著領先次佳的 Gen3C(15.37 / 0.431 / 0.483),而後者並非 real-time(Table 2, p.7)。
- Short-term (61 frames) 在不犧牲一致性的情況下仍取得最佳 PSNR 21.92、SSIM 0.702、LPIPS 0.247,並把 $R_{\text{dist}}$、$T_{\text{dist}}$ 的 action accuracy 推到所有對照中最佳(Table 2, p.7)。
- Dual Action Representation 將 discrete keys 注入 timestep embedding、continuous camera 透過 PRoPE 注入 self-attention,full 設定相較 discrete-only 的 $R_{\text{dist}}$ 由 0.103 降至 0.028(Table 3, p.8)。
- Temporal Reframing 重新指派 RoPE 的 positional index,長序列下將 PSNR 從 14.03 提升到 16.27,直接驗證「長程記憶被 RoPE 衰減」是真實瓶頸(Table 4, p.8)。
- Context Forcing 對 teacher 與 student 同步施加對齊的 memory context,使 4-step distilled student 在 long-term 上與 100-NFE bidirectional teacher 相當甚至更佳(Table 6, p.16;Fig. 8, p.8)。
- 自建 320K 樣本資料集,涵蓋 Sekai 真實影片、DL3DV 經 3DGS 重建並以 Difix3D+ 修補的 customized trajectory、UE 合成場景、170K AAA 第一/三人稱遊戲錄製(Table 5, p.13)。
- 30 位人類評審於 600 cases 的 user study 中,對 WorldPlay 的偏好率為 Gen3C 72.9%、Matrix-Game 2.0 92.1%、ViewCrafter 78.4%、GameCraft 88.5%(Fig. 15, p.16)。
- 同一架構直接支援 3D 點雲重建與基於 KV-recache 的 promptable event(如天氣切換、火焰生成),示範框架可延伸到下游應用(Fig. 1d–e, p.1;Fig. 9, p.8;Fig. 17, p.16)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 目前僅聚焦於 navigation control,延伸到 multi-agent interaction 與更複雜 physical dynamics 仍是 open problem(Sec. 5, p.8–9)。
- 生成更長 duration 的影片仍需進一步研究,當前評估上限止於 ≥250 frames 的 cycle trajectory(Appendix F, p.18)。
- Action type 仍偏狹,擴展到更廣的離散+連續組合是 future direction(Appendix F, p.18)。

#### 4.2.2 Phyra-inferred

- Real-time 的「24 FPS」是建立在 8×H800 的 mixed parallelism 之上(Sec. 3.5, p.6),論文以「real-time」對齊 Oasis 與 Matrix-Game 2.0,但完全未報告單卡或消費級 GPU 上的 latency,因此 deployment cost 不可比。
- Long-term evaluation protocol 僅使用 cycle trajectory(沿原路返回,Sec. 4 evaluation, p.7),這對 FOV-overlap 觸發的 spatial memory 是最有利的設定;真正的 free exploration 中於任意未來時刻偶遇舊場景的情境並未被測試。
- Spatial memory 的 retrieval score 由 FOV overlap + camera distance 構成,但部署時若使用者只給離散按鍵,camera pose 是用「預設 relative translation/rotation」累加得到(Appendix A 末段, p.12),這會造成 pose drift 隨時長線性放大,但論文未提供 pose-noise robustness 的量化分析。
- Memory size ablation 只比較 (Spatial, Temporal) = (3,1) 與 (1,3) 兩組(Table 7, p.16),無法判斷 (1,3) 是真正最優還是局部 sweet spot,也未說明為何不同時放大兩者。
- Long-term 對照中包含 CameraCtrl、SEVA、ViewCrafter 等本就不為長序列 revisit 設計的方法(Table 2, p.7),其顯著劣勢有部分來自 task mismatch 而非單純架構落差,將其平鋪比較會放大 WorldPlay 的相對提升。
- Promptable event 與 video continuation 兩項應用僅有 qualitative 圖示(Fig. 9、Fig. 16),沒有指標衡量 prompt 觸發後場景一致性是否仍維持,亦未說明事件後再次 revisit 是否會被新 prompt 的內容污染。

### 4.3 Phyra's Judgment (summary)

WorldPlay 真正具新意的核心是 Context Forcing:它指認出「memory-aware causal student vs. memory-less bidirectional teacher」之間的條件分布錯配 $p(x \mid C)$ 是先前蒸餾失敗的根因,並用 chunk-level memory 對齊把這個錯配補起來,使 memory 與 distillation 第一次能共存。Reconstituted Context Memory 與 Temporal Reframing 則是對 WorldMem 的 FOV retrieval 與 RoPE 外推問題的合理工程整合,屬於「正確但可預期」的設計。Dual Action Representation 是兩個既有訊號的整合,屬實作貢獻。最未解的核心問題是:在 cycle trajectory 之外、面對長時程自由探索與運動世界時,這套 memory 是否能持續有效——目前的 evaluation protocol 並未直接觸及這個情境。

## 5. Methodology Deep Dive

### 5.1 Method Overview

WorldPlay 將即時互動式世界模型形式化為條件式自迴歸視訊擴散模型 $N_\theta(x_t \mid O_{t-1}, A_{t-1}, a_t, c)$,其中 $x_t$ 為下一個 chunk(4 個 latents,經 causal 3D VAE 解碼為 16 frames),$O_{t-1} = \{x_{t-1}, \dots, x_0\}$ 為過去觀察,$A_{t-1} = \{a_{t-1}, \dots, a_0\}$ 為過去動作,$a_t$ 為當前動作,$c$ 為文字或圖像提示 (paper §3, p.3)。骨幹採用基於 Diffusion Forcing [6] 的 chunk-wise autoregressive Diffusion Transformer:對於 video latent $z_0 \in \mathbb{R}^{C \times T \times H \times W}$,將其分成 $T/4$ 個 chunks $\{z_0^i \in \mathbb{R}^{C \times 4 \times H \times W}\}$,把全序列 self-attention 改為 block-causal attention,讓每個 chunk 只能 attend 自身與更早的 chunks。

整個 pipeline 由三個邏輯耦合的設計組成,共同保證「即時 × 長程一致」的目標 (Fig. 2, p.4)。第一,**Dual Action Representation** 在動作介面層解耦穩健性與精度:離散按鍵 $k_t$ 透過 PE 與 zero-initialized MLP 編碼後與 timestep embedding 相加並調制 DiT block,連續相機姿態 $(R, T)$ 則透過 PRoPE [33] 轉成 $D_{\text{proj}}$,以加性方式注入 self-attention 形成相機 frustum 之間的相對幾何編碼 (Eq. 2, Eq. 3, p.4)。第二,**Reconstituted Context Memory** 於記憶介面層為每個新 chunk 動態重建上下文 $C_t$:由時間鄰近的最近 $L$ 個 chunks 組成 temporal memory $C_t^T$,加上以 FOV 重疊與相機距離評分挑選的 spatial memory $C_t^S$,並透過 **Temporal Reframing** 把所有 context chunks 的 RoPE 位置索引重新指派為與當前 chunk 距離很小的固定值,迫使遠程幾何相關 frames 被視為近期記憶 (Fig. 4, p.5)。第三,**Context Forcing** 於蒸餾介面層消解 teacher–student 的條件分布 $p(x \mid C)$ 錯配:對 student 進行 4-chunk 自展開 self-rollout,同時讓 teacher $V_\beta$ 也吸收與 student 對齊的記憶上下文(僅遮蔽當前要去噪的 $x_{j:j+3}$),使分布匹配損失能在保留長程記憶的條件下將 50-step bidirectional teacher 蒸餾成 4-step causal student (Fig. 5, p.5)。

最終整合 KV-cache、mixed sequence/attention parallelism、SageAttention [79]、float 量化以及 progressive multi-step VAE decoding,WorldPlay 在 $8\times$H800 GPUs 上達到 24 FPS、720p 串流互動,且 long-term LPIPS、PSNR、SSIM 與動作精度 $R_{\text{dist}}, T_{\text{dist}}$ 同時優於 Matrix-Game 2.0、GameCraft、Gen3C、VMem 等 baselines (Table 2, p.7)。

### 5.2 Pipeline Diagram with Tensor Shapes

```
INPUTS (per generation step t)
  ├─ Text/image prompt c
  │    └→ pretrained text/image encoder ────────────────→ c_emb  [B, L_c, D_c]
  │
  ├─ Action a_t = (k_t, p_t)
  │    ├─ Discrete key k_t ∈ {W, A, S, D, ...}
  │    │    └→ PE + zero-init MLP ─────────────────────→ k_emb  [B, 1, D]
  │    │                                                      │
  │    │                                       added to timestep embedding
  │    │                                                      ↓
  │    │                                       modulates DiT blocks (AdaLN-style)
  │    │
  │    └─ Continuous pose p_t = (R ∈ R^{3x3}, T ∈ R^3) + intrinsics
  │         └→ D_proj (PRoPE [33])  ─────────────────────→ D_proj  [B, 4, H, W, ?]
  │                                                      │
  │                            applied to (Q, K, V) of self-attention (Eq. 3)
  │
  └─ Past clean chunks O_{t-1} = {x_0, ..., x_{t-1}}    [B, C, 4(t-1), H, W]
       │
       ▼
  ┌─────────────────── Reconstituted Context Memory (Sec 3.3) ───────────────────┐
  │                                                                              │
  │  Temporal memory  C^T_t = {x_{t-L}, ..., x_{t-1}}            [B, C, 4L, H, W]│
  │       L = 3 chunks (Appendix A)                                              │
  │                                                                              │
  │  Spatial memory   C^S_t ⊂ O_{t-1} - C^T_t                                    │
  │       sampled by score(FOV-overlap, camera-distance)         [B, C, 4·1, H, W]│
  │                                                                              │
  │  Temporal Reframing: re-assign RoPE temporal indices so all ctx chunks       │
  │       sit at small fixed relative distance to current chunk x_t (Fig 4c)     │
  │                                                                              │
  │       ─────► concatenated context  C_t                       [B, C, 16, H, W]│
  └──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
  Init noise  z_d ~ N(0, I)                                       [B, C, 4, H, W]
       │
       ▼
  ┌─────────── AR Diffusion Transformer N_θ (Sec 3.1, Sec 3.2) ──────────┐
  │   for s = d, d-1, ..., 1   (d = 4 denoising steps after CF)           │
  │     z_s = patchify+embed(z_s) ────────────────────→ tokens  [B, M, D] │
  │     for each block:                                                   │
  │        Attn1 = Attn(R^T ⊙ Q,  R^{-1} ⊙ K,  V)             (3D RoPE)   │
  │        Attn2 = D_proj ⊙ Attn((D_proj)^T⊙Q,                            │
  │                              (D_proj)^{-1}⊙K,                         │
  │                              (D_proj)^{-1}⊙V)             (PRoPE)     │
  │        out  = Attn1 + zero_init(Attn2)                                │
  │        out  = block_causal_mask(out)                                  │
  │        out += cross_attn(out, c_emb)                                  │
  │        out  = AdaLN(out, time_emb + k_emb)                            │
  │        out  = FFN(out)                                                │
  │     z_{s-1} = denoise_step(z_s, out, k_s)                             │
  │   KV-cache reused across steps (Appendix Algorithm 2)                 │
  └───────────────────────────────────────────────────────────────────────┘
       │
       ▼
  Predicted clean latent  x_t                                     [B, C, 4, H, W]
       │
       ▼
  Causal 3D VAE progressive decode (multi-step, streaming)        [B, 16, 3, 720, 1280]
       │
       ▼
  Streaming output @ 24 FPS  →  user observes, issues next a_{t+1}
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Dual Action Representation

**Function:** 把使用者鍵盤/滑鼠輸入同時編碼成「尺度自適應」的離散按鍵與「精準空間定位」的連續相機姿態,前者調制 timestep,後者注入 self-attention 為記憶模組提供精確空間索引。

**Input:**
- Name: `a_t = (k_t, p_t)`
- Shape: `k_t` 為離散按鍵 token id `[B, 1]`;`p_t = (R ∈ R^{3×3}, T ∈ R^3)` 加上 camera intrinsics(對所有訓練視訊統一處理,paper 並未公開 intrinsics 的具體 channel 數)
- Source: 互動式 controller stream;對只有相機姿態的 case,以 thresholding 將相對 $\Delta R, \Delta T$ 反推為離散 key;對只有 key 的 case,以預定義 $(\Delta R, \Delta T)$ 反推為連續姿態 (Appendix A, p.12)

**Output:**
- Name: `(k_emb, D_proj)`
- Shape: `k_emb` $\in \mathbb{R}^{B \times 1 \times D}$;`D_proj` 為作用於 Q/K/V 的相對位置張量,shape `[B, 4, H, W, ?]`(具體最後一維為 PRoPE 投影矩陣維度,paper 未明示)
- Consumer: `k_emb` 加到 timestep embedding 後送入 DiT 的 AdaLN 調制路徑;`D_proj` 進入每個 self-attention block 的 Eq. 3

**Processing:**

1. 離散 keys 路徑:`k_t` 經 sinusoidal/learned PE 後,通過一個 zero-initialized MLP 編碼為 `k_emb`,再與 diffusion timestep $k$ 的 PE+MLP embedding 相加,得到 fused time embedding。zero-init 保證訓練早期不擾動 pretrained backbone。
2. 連續姿態路徑:把 $(R, T)$ 與 intrinsics 依 PRoPE [33] 規則投影為相對 frustum 位置編碼 $D_{\text{proj}}$,在 self-attention 中與 video latent 的 3D RoPE $R$ 並行作用 (Eq. 2 對應 Attn1,Eq. 3 對應 Attn2)。

**Key Formulas:**

$$
\text{Attn}_1 = \text{Attn}(R^\top \odot Q,\; R^{-1} \odot K,\; V)
$$

$$
\text{Attn}_2 = D_{\text{proj}} \odot \text{Attn}\big((D_{\text{proj}})^\top \odot Q,\; (D_{\text{proj}})^{-1} \odot K,\; (D_{\text{proj}})^{-1} \odot V\big)
$$

$$
\text{Output} = \text{Attn}_1 + \text{zero\_init}(\text{Attn}_2)
$$

**Implementation Details:**

PRoPE 較常見的 raymap 表示更具泛化性 (paper §3.2)。zero-init MLP 與 zero-init 的 Attn2 殘差路徑共同確保動作條件以漸進方式注入,訓練早期不破壞 pretrained DiT 的視訊先驗。Ablation (Table 3, p.8) 顯示 Discrete-only 在 $R_{\text{dist}}/T_{\text{dist}}$ 上分別為 $0.103/0.615$,Continuous-only 為 $0.038/0.287$,Full Dual 為 $0.028/0.113$,證實兩者互補。

#### 5.3.2 Chunk-wise Autoregressive Diffusion Transformer Backbone

**Function:** 把 pretrained bidirectional video DiT [28, 62] 微調為 chunk-wise causal AR 生成器,作為 next-chunk prediction 的核心。

**Input:**
- Name: noisy current chunk `z_k^t` 與 context `C_t`
- Shape: `z_k^t` $\in \mathbb{R}^{B \times C \times 4 \times H \times W}$;`C_t` 在 §5.3.3 形成,shape `[B, C, 16, H, W]`(3 temporal + 1 spatial,共 4 chunks × 4 latents)
- Source: 噪聲 latent 加上重建後的記憶上下文

**Output:**
- Name: 預測 velocity $v_k$ 或 clean latent `x_t`
- Shape: `[B, C, 4, H, W]`
- Consumer: 多步 denoising loop,最終送入 causal 3D VAE 解碼

**Processing:**

1. 把 `z_k^t` 與 `C_t` 沿 temporal 軸拼接,patchify 為 token 序列 `[B, M, D]`(`M` 為 spatial-temporal patch 總數)。
2. 將原本的 full 3D self-attention 改為 **block-causal attention**:當前 chunk 內部 full attention,跨 chunk 只能向過去 attend,實現自迴歸性。
3. 每層套用 §5.3.1 的 Attn1 + Attn2,接 cross-attention(條件 `c_emb`)、AdaLN 時間/動作調制、FFN。
4. 訓練以 flow matching loss(Eq. 1)監督;推理時用 KV-cache(Appendix Algorithm 2)避免重複計算過去 chunks 的 K/V。

**Key Formulas:**

$$
\mathcal{L}_{\text{FM}}(\theta) = \mathbb{E}_{k, z_0, z_1}\left\| N_\theta(z_k, k) - v_k \right\|^2,\quad v_k = z_0 - z_1,\quad z_k = (1-k)z_0 + k z_1
$$

**Implementation Details:**

Stage One 訓練:bidirectional 30K iters → 替換成 block-causal attention 再訓 30K iters,輸入長度 61 frames (4 chunks),Adam,lr $=1\text{e-}5$,batch size $64$ (Appendix A, p.12)。Causal 3D VAE 將 16 latents 解碼為 61 frames(因果 VAE 邊界導致首 chunk 為 13 frames、後續每 chunk 16 frames)。Backbone channel `C` 與 hidden `D` 沿用 HunyuanVideo/Wan 預訓練模型,paper 未在正文中給出具體數值。

#### 5.3.3 Reconstituted Context Memory

**Function:** 為每個新 chunk 動態挑選與重新編碼歷史 chunks,克服「全 context 計算不可行」與「RoPE 相對距離無界增長導致長程記憶衰減」兩個問題。

**Input:**
- Name: 過去 chunks $O_{t-1}$、當前相機姿態 $p_t$
- Shape: $O_{t-1}$ $\in \mathbb{R}^{B \times C \times 4(t-1) \times H \times W}$
- Source: 已生成並 detach 的 clean latents

**Output:**
- Name: 上下文記憶 `C_t`(已重新指派 PE)
- Shape: `[B, C, 4(L+|C^S|), H, W] = [B, C, 16, H, W]` 當 `L=3, |C^S|=1`
- Consumer: 與當前噪聲 chunk 一同送入 §5.3.2 的 AR DiT

**Processing:**

1. **Temporal memory** $C_t^T = \{x_{t-L}, \dots, x_{t-1}\}$:取最近 $L=3$ 個 chunks 確保短期運動連續性。
2. **Spatial memory** $C_t^S \subseteq O_{t-1} - C_t^T$:對非鄰近 chunks 計算 geometric relevance score(FOV 重疊 + 相機距離),取分數最高的 $1$ 個 chunk,以注入長程幾何錨點。
3. **Temporal Reframing**:丟棄絕對時間索引,把 $C_t^T$ 與 $C_t^S$ 的 RoPE 時間位置全部重新指派,使其與當前 chunk 的相對距離為一個小且固定的值(Fig. 4c, p.5)。

**Key Formulas:**

$$
C_t = \text{Reframe}\big(C_t^T \cup C_t^S\big),\quad C_t^T = \{x_{t-L}, \dots, x_{t-1}\},\quad C_t^S = \arg\!\max\nolimits_{x \in O_{t-1} \setminus C_t^T} \text{Score}_{\text{geo}}(x, p_t)
$$

**Implementation Details:**

Appendix A 設定 `L = 3`、spatial memory length `= 1`。Score 由 FOV overlap 與 camera distance 組合,paper 未給出公式權重。Ablation (Table 4, p.8) 顯示 long-term test 上 Reframed RoPE 對 naive RoPE 改善 PSNR $14.03 \to 16.27$、$T_{\text{dist}}$ $1.341 \to 0.991$。Reframing 同時防止超出 RoPE 訓練插值範圍造成的 extrapolation artifacts (Fig. 7, p.8)。

#### 5.3.4 Context Forcing Distillation

**Function:** 將 50-step bidirectional teacher 蒸餾為 4-step causal student,並透過對齊 teacher/student 的記憶上下文,解決 memory-aware 模型在 distribution matching distillation 中的 $p(x \mid C)$ 錯配問題。

**Input:**
- Name: pretrained AR student $N_\theta$、bidirectional teacher $V^{\text{fake}}_\beta$ 與 frozen reference $V^{\text{real}}$、真實 video clip
- Shape: 訓練樣本沿用 §5.3.2 之 `[B, C, 4·n, H, W]`,`n = 4` chunks 自展開
- Source: dataset $D$ 採樣 `x_{0:j-1}` 作為前置 context

**Output:**
- Name: 更新後的 `θ`(student)與 `β`(teacher)
- Consumer: 部署時僅 student 推理,4-step denoising

**Processing:**

1. Progressive 訓練:漸進增加最大 chunk 長度 $m$,sample $j \sim \mathrm{Uniform}\{0, \dots, m\}$。
2. **Self-rollout**:從 $x_{0:j-1}$ 起,student 對 $i = j, \dots, j+3$ 依次以 $C_i \subseteq \{x_0, \dots, x_{i-1}\}$ 為 context 並用隨機抽取的 $s$ 個 denoising steps 自展開生成 `x_i`。
3. **Memory alignment**:把 teacher 的 context 設為 $C^{\text{tea}} = C_{j:j+3} - x_{j:j+3}$,即遮蔽掉當下要去噪的 chunks 但保留與 student 一致的歷史 + 空間記憶。
4. 對 $\hat x_{j:j+3} = \text{AddNoise}(x_{j:j+3}, k)$ 計算 fake/real score,進行 distribution matching:

**Key Formulas:**

$$
p_\theta(x_{j:j+3}\mid x_{0:j-1}) = \prod_{i=j}^{j+3} p_\theta(x_i \mid C_i)
$$

$$
p_{\text{data}}(x_{j:j+3}\mid x_{0:j-1}) = p_\beta\big(x_{j:j+3} \mid C_{j:j+3} - x_{j:j+3}\big)
$$

$$
\nabla_\theta \mathcal{L}_{\text{DMD}} = \mathbb{E}_k\!\left[\nabla_\theta \mathrm{KL}\big(p_\theta(x_{0:t}) \,\|\, p_{\text{data}}(x_{0:t})\big)\right]
$$

**Implementation Details:**

Stage Three 訓練:student lr $= 1\text{e-}6$,teacher (fake score) lr $= 2\text{e-}7$,2K iters,batch $64$,其餘超參沿用 Self-Forcing [21] (Appendix A, p.12)。Real-score teacher 凍結。Ablation (Fig. 8, p.8) 對比三種 context 設置:misaligned context 直接導致蒸餾崩潰,self-rollout historical context 因 teacher 訓練時看的是 clean memory 而出現 artifacts,從真實視訊取樣的 historical context (即本方案) 結果最佳。經此設計,4-step student 在長時間 rollout 下仍維持與 teacher 相當的長程一致性,並解決 exposure bias 與 error accumulation。

#### 5.3.5 Streaming Generation Optimizations

**Function:** 將 4-step distilled student 部署為 24 FPS、720p 即時互動服務,涵蓋平行化、量化、漸進解碼。

**Input:**
- Name: AR student `N_θ` checkpoint、causal 3D VAE
- Shape: 推理時 chunk 為 `[B=1, C, 4, H, W]`
- Source: §5.3.4 蒸餾後的 student

**Output:**
- Name: 連續 RGB 影像串流
- Shape: 每 chunk `[1, 16, 3, 720, 1280]` 以 progressive 子批方式流出
- Consumer: 終端使用者顯示

**Processing:**

1. **Mixed parallelism**:結合 sequence parallelism [34] 與 attention parallelism,把整個 chunk 的 tokens 跨 8 張 H800 平均切分,而非常見的 model replication 或單純時間維度切分,讓每 chunk 計算負載均衡。
2. **Streaming deployment**:基於 NVIDIA Triton Inference Framework,配合 progressive multi-step VAE decoding——DiT 一輸出 latent 即將其前段 frames 先解碼推送,後段繼續解碼,壓低 time-to-first-frame。
3. **Quantization & efficient attention**:使用 SageAttention [79]、float quantization、matmul quantization,並在 self-attention 與 cross-attention 開啟 KV-cache 消除重複計算 (Appendix Algorithm 2)。
4. 推理迴圈(Algorithm 2):每個新 chunk 在 step $s = d$ 且 $i > 1$ 時 reset KV cache 以容納新 reconstituted context $C_i$,然後 4 步 denoise 並 append 結果。

**Key Formulas:**

$$
\text{Throughput} \approx \frac{16 \text{ frames per chunk}}{\text{latency per chunk}} \;=\; 24\ \text{FPS}\quad (\text{8}\times\text{H800, 720p})
$$

**Implementation Details:**

paper 未給出每模組量化精度的具體 bit 數;SageAttention 採 8-bit attention,float quantization 與 matmul quantization 的精度 (FP8/INT8) 未明確。Time-to-first-frame 與每 chunk 的具體 latency 數值在 paper 中亦未展開。互動延遲品質透過 24 FPS 維持流暢操作的事實間接證實 (Sec 3.5, p.6)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage |
|---|---|---|---|
| Sekai (real-world dynamics) | Real-world video for navigation/world-modeling training | 40K clips (12.5%) | train |
| DL3DV (real-world 3D scene) | 3D-reconstruction-then-rerender for revisit trajectories | 60K clips (18.75%) | train |
| UE Rendering (synthetic 3D scene) | Custom-trajectory rendering of UE scenes | 50K clips (15.625%) | train |
| Game Video Recordings (1st/3rd-person AAA) | Simulation-dynamics recording with designed trajectories | 170K clips (53.125%) | train |
| In-house test set (DL3DV + game videos + AI-generated images) | Short-term & long-term cycle-trajectory evaluation | 600 cases | test |
| VBench | Multi-dimension video-generation benchmark | the paper does not specify | test (App. C.5) |
| WorldScore | World-generation benchmark for the user study | 300 cases (combined with 300 custom trajectories) | test (App. D, user study) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PSNR | Pixel-level visual fidelity vs. GT (short-term) or vs. initial-pass frame (long-term return path) | yes |
| SSIM | Structural similarity vs. reference frames | no |
| LPIPS | Perceptual distance vs. reference frames | no |
| $R_{\text{dist}}$ | Rotation-error of the generated camera pose vs. the input pose | yes |
| $T_{\text{dist}}$ | Translation-error of the generated camera pose vs. the input pose | yes |
| Real-time / FPS | Whether streaming generation runs at 24 FPS at 720p | yes |
| VBench dimensions | 16 dimensions including Subject/Background/Overall Consistency, Motion Smoothness, Aesthetic/Imaging Quality, Scene, etc. | no |
| Human preference rate | Pairwise A/B preference across visual quality, control accuracy, long-term consistency | no |

長期一致性的設計是用「沿同一軌跡返回」時，回程影格與去程影格的 PSNR/SSIM/LPIPS 來量化（§4 Evaluation Protocol）。

### 6.3 Training and Inference Settings

- Backbone：採用 pretrained DiT-based video diffusion model（HunyuanVideo / Wan，[28, 62]）；chunk 大小為 4 latents（解碼為 16 frames）。記憶體設定：temporal memory 3 chunks、spatial memory 1 chunk（App. A）。
- Stage 1 (Action Control)：先 bidirectional 30K iters，再替換為 block causal attention 並訓練 30K iters；訓練長度 61 frames（4 chunks），Adam，lr $1\text{e}{-5}$，batch size 64。
- Stage 2 (Memory)：在更長影片上同時訓練 bidirectional 與 AR action model，加入 §3.3／§3.4 的 context memory；其餘超參同 Stage 1。
- Stage 3 (Context Forcing)：以 bidirectional model 為 teacher、AR model 為 student 進行蒸餾；採 progressive training 漸進延長最大 latent 長度。Student lr $1\text{e}{-6}$、fake-score bidirectional model lr $2\text{e}{-7}$；2K iters，batch size 64；其餘超參遵循 Self-Forcing [21]。Algorithm 1 給出詳細流程。
- Inference：4 denoising steps，KV cache + Algorithm 2 的 streaming 流程；當輸入只有 camera pose 或只有 discrete action 時，透過閾值化或預設位移／旋轉互轉。
- Hardware / latency：on $8\times$ H800 GPUs，可達 720p、24 FPS streaming。混合並行（sequence parallelism [34] + attention parallelism）、Triton streaming + progressive VAE decoding、Sage Attention [79]、float / matmul 量化、KV-cache（§3.5）。
- Annotation：vision-language model [81] 產生 caption，無 camera 標註者用 VIPE [20] 估計 pose，pose collapse 影片被濾掉；無 discrete action 者由 continuous pose 投影到 $x,y,z$ 軸後閾值化得到（App. B）。
- 隨機種子數、跑數、誤差棒：the paper does not specify。

### 6.4 Main Results

Table 2，long-term ($\geq 250$ frames) 設定（粗體為本論文方法）：

| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ | $R_{\text{dist}}$ ↓ | $T_{\text{dist}}$ ↓ | Real-time |
|---|---|---|---|---|---|---|
| CameraCtrl | 10.09 | 0.241 | 0.549 | 0.733 | 1.117 | ✗ |
| SEVA | 10.51 | 0.301 | 0.517 | 0.721 | 1.893 | ✗ |
| ViewCrafter | 9.32 | 0.277 | 0.661 | 1.573 | 3.051 | ✗ |
| Gen3C | 15.37 | 0.431 | 0.483 | 0.357 | 0.979 | ✗ |
| VMem | 12.77 | 0.335 | 0.542 | 0.748 | 1.547 | ✗ |
| Matrix-Game-2.0 | 9.57 | 0.205 | 0.631 | 2.125 | 2.742 | ✔ |
| GameCraft | 10.09 | 0.287 | 0.614 | 2.497 | 3.291 | ✗ |
| Ours (w/o Context Forcing) | 16.27 | 0.425 | 0.495 | 0.611 | 0.991 | ✗ |
| **Ours (full)** | **18.94** | **0.585** | **0.371** | **0.332** | **0.797** | **✔** |

Short-term (61 frames) 上 Ours (full) 同樣最佳：PSNR 21.92／SSIM 0.702／LPIPS 0.247／$R_{\text{dist}}$ 0.031／$T_{\text{dist}}$ 0.121。VBench (Fig. 14) 在 Subject/Background/Overall Consistency、Motion Smoothness、Scene 等向度均勝過 Gen3C / ViewCrafter / GameCraft / Matrix-Game-2.0；Human study (Fig. 15) 對全部四個 baseline 的 preference rate 均 $> 70\%$（vs. Gen3C 72.9%、vs. ViewCrafter 92.1%、vs. Matrix-Game-2.0 78.4%、vs. GameCraft 88.5%），對自家 bidirectional teacher 也維持 48.1% / 51.9%，顯示蒸餾後品質幾乎無損。

### 6.5 Ablation Studies

- **Dual Action Representation (Table 3，bidirectional model 上驗證)**：只用 discrete keys 時 $R_{\text{dist}}=0.103$、$T_{\text{dist}}=0.615$；換成 continuous pose 顯著改善至 $0.038/0.287$；雙重表示再降到 $0.028/0.113$，PSNR 也由 21.47 → 22.09。直接診斷「discrete vs. continuous vs. both」對控制精度的貢獻，是有效的 component-level ablation，不只是 sanity check。
- **Reframed RoPE (Table 4，long-term)**：把 absolute temporal index 換成 reframed RoPE 後 PSNR 14.03 → 16.27、$R_{\text{dist}}$ 0.805 → 0.611；Fig. 7 同時展示 standard RoPE 會撞到訓練範圍上限導致 error accumulation 與長距離 spatial memory 衰退。直接驗證 §3.3 的 temporal reframing 主張。
- **Context Forcing 的 memory alignment (Fig. 8 + Table 6)**：(a) teacher/student context 不對齊 → 蒸餾崩壞；(b) 用 self-rollout 歷史當 context → bidirectional teacher 給出失準 score、產生 artifact；(c) 從 real video 取歷史 chunk 對齊 → 結果最佳。Table 6 進一步比較 Student (AR, NFE 100)、Teacher (Bidirectional, NFE 100)、Final (Distilled, NFE 4)：distilled 版以 4 步達到 PSNR 18.94 / LPIPS 0.371，超過 100 步的 student (16.27 / 0.495)，逼近 teacher (19.31 / 0.383)。這直接回答「context 對齊是否必要」與「蒸餾是否會犧牲長期一致性」。
- **Memory Size (Table 7)**：spatial 3 / temporal 1 vs. spatial 1 / temporal 3，後者整體較佳（PSNR 16.27 vs. 16.41 接近，但 SSIM 0.425 / LPIPS 0.495 / $R_{\text{dist}}$ 0.611 / $T_{\text{dist}}$ 0.991 全面較好），同時論文主張更大 spatial memory 會讓 teacher 訓練與蒸餾更難。屬於 design-choice 驗證，偏向 sanity check 而非深入 scaling study（沒掃到更大 memory size）。
- **w/o Context Forcing 列 (Table 2)**：作為 §3.4 的整體消融，移除 context forcing 後 long-term PSNR 由 18.94 掉到 16.27，且失去 real-time，直接量化 distillation 的價值。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 與 7 個近期 baseline 比較（含 memory-based Gen3C、VMem 與 real-time Matrix-Game-2.0），覆蓋 §2 識別出的兩條主線。
- [partial] Has cross-task / cross-dataset evaluation — 主表只跑自建 600-case 測試集；補充另外做了 VBench 與 WorldScore + 用戶研究，但並未在獨立的標準 benchmark（例如 RealEstate10K、Tartan、Ego4D 等）跨域報數。
- [covered] Has ablations that diagnose the new components — Dual Action（Table 3）、Reframed RoPE（Table 4）、Context Forcing 對齊與 self-rollout 變體（Fig. 8 / Table 6）、teacher/student/distilled NFE 比較皆對應論文三大貢獻。
- [partial] Has a scaling study — 只有 memory size 1+3 vs. 3+1 的小掃描（Table 7）與長度上 short-term 61 vs. long-term $\geq$250 frames，沒做模型參數量或資料規模的 scaling。
- [covered] Has an efficiency / wall-clock comparison — Table 2 的 Real-time 欄、§3.5 報告 720p / 24 FPS on $8\times$ H800、Table 6 給 NFE 100 vs. 4 的對比，明確量化推論成本。
- [missing] Reports variance / standard deviation / multiple seeds — 全文未提供 std、seed 數或信賴區間；the paper does not specify。
- [partial] Releases code / weights / data sufficient for reproducibility — 提供 project page 與 online demo（hunyuan.tencent.com 上 sceneTo3D），但內文未明示 code、weights 或 training data（含 170K 私錄遊戲影片、UE 資產）的開源狀態。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 24 FPS、720p 串流互動 (real-time)** — *Supported(有條件)*。Sec. 3.5 的 mixed parallelism、Sage Attention、KV cache、progressive VAE decoding 共同支撐此速率,但前提是 8×H800;未驗證單卡可行性。
- **C2: Long-term geometric consistency** — *Supported on cycle protocol*。Table 2 的 ≥250 frames 區段顯示 PSNR 18.94 顯著領先(Gen3C 15.37、Matrix-Game 2.0 9.57);但 evaluation 採用「沿原路返回」式 cycle trajectory,屬於對 FOV-overlap retrieval 最有利的測法,未測試非對稱的長時程 free exploration。
- **C3: Dual Action Representation 兼具 robust 與 precise control** — *Supported*。Table 3 顯示 full 版本相對 discrete-only 在 $R_{\text{dist}}$、$T_{\text{dist}}$ 各降約 4–5×,且 PSNR/SSIM 同步提升,實驗符合主張。
- **C4: Reconstituted Context Memory + Temporal Reframing 緩解長程衰減** — *Supported*。Table 4 的 reframed RoPE 對比 naive RoPE 在所有 5 個指標皆顯著改善,Fig. 7 的 qualitative 對照亦呼應 RoPE 外推 artifact 的具體形態。
- **C5: Context Forcing 為 memory-aware 模型提供可行 distillation** — *Supported,且為最強證據*。Table 6 顯示 4-step distilled 在 long-term 上與 100-NFE teacher 相當(SSIM 0.585 vs 0.599);Fig. 8 的兩個失敗 ablation(misaligned context 直接 collapse、self-rollout context 出現 artifact)使「memory 對齊」成為 necessity 而非 nice-to-have。

### 7.2 Fundamental Limitations of the Method

**固定大小的 memory window 是延遲常數的代價**。為維持 per-chunk 推論時間恆定(Sec. C.2 強調「generation time per chunk does not grow with length」),memory context 必須有界——當前設定為 3 個 temporal + 1 個 spatial chunk(Appendix A, p.12)。在真正無界的探索中,可被「召回」的歷史資訊量上限恆定,只能透過更聰明的 retrieval 重新分配,無法跨越此上限。這意味著在足夠長的軌跡下,某些重要 spatial cue 必然被擠出 memory,且方法本身無法察覺此遺失。

**Spatial retrieval 對 pose accuracy 的依賴未被閉環處理**。Reconstituted Context Memory 的 spatial branch 以 FOV overlap 與 camera distance 計算 relevance score(Sec. 3.3),前提是 camera pose 可信。然而部署時當使用者只給 discrete keys,系統用預設 relative R, T 累加得到 pose(Appendix A, p.12),這條 open loop 會讓 pose drift 隨時間累積,retrieval 也跟著退化。模型既未感知 pose uncertainty,也沒有 self-correction 機制。

**Distillation 鏈是耦合的**。Context Forcing 要求 teacher $V_\beta$ 本身是 memory-augmented 的 bidirectional model,且必須與 student 共用相同 memory 結構(Sec. 3.4)。這意味著任何 memory 設計上的修改都需要重新訓練 teacher 與 student;backbone 升級或 memory schema 變動都不是低成本動作。

**評測協議定義了一致性的可達上限**。Long-term 設定明確採用「customized cycle trajectories: 沿軌跡前進再返回」(Sec. 4 evaluation, p.7),這是對 FOV-based retrieval 最有利的場景。論文沒有 minute-scale 的 stochastic exploration 評測,因此「long-term geometric consistency」的真實邊界目前停留在「return-on-same-path」這個語意上,而非完整的「revisit at arbitrary future time」。

### 7.3 Citations Worth Tracking

- **Self-Forcing [21]** — Context Forcing 的直系前作;欲理解 distillation 為何選擇此 rollout 形式、以及 exposure bias 處理細節,需從此入。
- **Diffusion Forcing [6]** — 整個 chunk-wise autoregressive backbone 的根源,理解 next-chunk prediction 與 noise schedule 的設計必讀。
- **WorldMem [67]** — FOV-based memory retrieval 的開山,WorldPlay 的 Reconstituted Context Memory 是其顯式延伸。
- **PRoPE [33]** — Continuous camera 注入 self-attention 的關鍵組件,牽涉到為何 $R$ 與 $D_{\text{proj}}$ 能組合為相容的 relative encoding。
- **CausVid [72]** — Bidirectional → causal autoregressive distillation 的範式起點;理解 Context Forcing 為何把問題定為 distribution matching 之前必須讀。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 若使用者僅輸入 discrete keys,部署時的累加 pose drift 多大,Spatial memory retrieval 的命中率會隨軌跡長度如何衰減?
- [ ] Memory size ablation 只測 (3,1) 與 (1,3)(Table 7),(5,5)、(3,3) 等更大的設定是否能持續改善,或在 distillation 階段崩壞?
- [ ] 在超出 ≥250 frames、minute-scale 的 free exploration 下,long-term 指標的退化曲線是線性、漸近,還是存在 cliff?
- [ ] 場景中存在動態物件(NPC、車輛、天氣)時,revisit 的「一致性」應如何定義,WorldPlay 對這類「應變」與「應持」的混合內容如何決策?
- [ ] Context Forcing 的成功是否依賴 teacher 與 student 同 backbone 同 memory size?跨 backbone 蒸餾(例如蒸到 3B 模型)是否仍收斂?
- [ ] Promptable event 之後若再次回到該位置,KV-recache 引入的內容是否仍被視為「該地的 ground truth」並被 memory 再保留?
- [ ] 320K 訓練資料中 53% 來自 AAA 遊戲錄製(Table 5),real-world 表現的提升究竟來自 Sekai+DL3DV 共 100K,還是 game data 的 stylistic transfer 副作用?

### 8.2 Improvement Directions

1. **將 pose uncertainty 納入 spatial relevance score**(可行性高):當前 retrieval score 只看 FOV overlap 與相機距離,將累積誤差作為衰減因子加入,能在 deployment 中自動降權那些「我以為去過但其實不確定」的歷史 chunk。理據:open-loop pose 累加是 deployment 與 training 之間最明顯的 distribution shift。
2. **以 free-exploration / 隨機 revisit benchmark 補強評測**(可行性高,僅需評測側修改):目前 cycle trajectory 是 protocol-friendly 但 task-restricted;改用「隨機分支 + 機率性回訪」的軌跡,能直接揭露 fixed-size memory 的真實 horizon。理據:claim 強於評測,需要對齊。
3. **landmark / semantic memory tier**(可行性中):在 temporal+spatial 之上新增一個以場景顯著度(如 vision-language similarity)為 score 的 memory 層,讓「具辨識度的少數地標」能跨越長距離保留。理據:純 FOV+distance 不能優先保留語意上重要的場景。
4. **Memory 的 write-back 機制**(可行性低,但理論收益大):目前 retrieved memory 為唯讀,長序列累積誤差無法被修正;若引入低頻的「校正寫回」(例如以新生成的高一致性 chunk 取代舊 memory),可緩解 drift。理據:當前 memory 與生成是單向耦合,結構上限制了長期穩定性。
5. **小 backbone 上的蒸餾驗證**(可行性中):若 Context Forcing 能在 3B 級別 backbone 上保持收斂,可去掉 8×H800 的硬體閘門,讓 real-time claim 觸及消費級硬體。理據:目前 latency 受限於 backbone 尺寸而非演算法本身,蒸餾鏈本就為削減推論成本而生。
