<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# X-Cache — X-Cache: Cross-Chunk Block Caching for Few-Step Autoregressive World Models Inference

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | X-Cache |
| Paper full title | X-Cache: Cross-Chunk Block Caching for Few-Step Autoregressive World Models Inference |
| arXiv ID | 2604.20289 |
| Release date | 2026-05-05 |
| Conference/Journal | arXiv preprint (Technical Report) |
| Paper link (abs) | https://arxiv.org/abs/2604.20289 |
| PDF link | https://arxiv.org/pdf/2604.20289v2 |
| Code link | — |
| Project page | https://x-cache-1.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|------|------|------|------|
| AI Infra Team, XPeng Inc. | XPeng Inc. (小鵬汽車) | https://x-cache-1.github.io/ (https://x-cache-1.github.io/en/) | corporate author (no individual authors disclosed) |

### 1.2 Keywords

world model, autoregressive video diffusion, diffusion caching, few-step distillation, DiT, KV cache, autonomous driving simulation, training-free acceleration

### 1.3 Related Lineage

| Key | Relation | Brief |
|------|------|------|
| FlowCache | baseline | Chunk-wise cross-step caching policy for AR video diffusion; relies on many-step cross-step redundancy that X-Cache argues fails in few-step regime. |
| SCOPE | baseline | Tri-modal scheduling with predictive extrapolation along the denoising trajectory; same cross-step assumption that X-Cache replaces with cross-chunk axis. |
| Block Cascading | influence | Sequence-level parallelization that pre-conditions on future chunks; ruled out for closed-loop interactive simulation, motivating X-Cache's intra-chunk constraint. |
| DiT (Diffusion Transformer) | base model | Block-wise transformer backbone; X-Cache caches per-block residuals at matching (denoising step, block) positions of the DiT. |
| Training-free cross-step DiT caching (TeaCache / FORA-line) | predecessor | Family of methods reusing block outputs across adjacent denoising steps in many-step DiTs; X-Cache identifies their core assumption as broken under few-step distillation. |
| Few-step distilled video diffusion | predecessor | Distillation to ~4-step denoising schedules required for real-time interactive simulation; defines the few-step regime X-Cache targets. |
| X-world (production driving world model) | base model | XPeng's multi-camera, action-conditioned causal-DiT world model with rolling KV cache that X-Cache is implemented on and validated against. |

## 2. Research Overview

### 2.1 Research Topic

本研究關注自駕系統閉迴圈評估與線上強化學習所仰賴的「即時世界模型」推理加速。XPeng 將 autoregressive video diffusion 蒸餾為 few-step 模型作為互動式模擬器,但現有 training-free diffusion caching 多沿 denoising step 軸重用 DiT block 輸出,在 4 步推理下幾乎無冗餘可用;而 sequence-level 平行化又需要尚未產生的未來條件,在閉迴圈生成中無法取得。作者提出 X-Cache,改沿「相鄰生成 chunk」軸快取每個 DiT block 的 residual,並設計結構與動作感知的 fingerprint、雙指標 gating、自適應每位置門檻,以及對 KV update chunk 的強制重算,於 X-world 多攝影機 causal DiT 世界模型上達成 71% block skip 率與 2.6× 推理加速,品質幾無退化。

### 2.2 Domain Tags

- Computer Vision
- Generative World Models
- Autonomous Driving
- Efficient Inference
- Diffusion Models

### 2.3 Core Architectures Used

- **Causal DiT (Diffusion Transformer)**:作為 X-world 世界模型的去噪骨幹,採 block-wise 殘差結構;X-Cache 在每個 $(t, b)$ 位置快取其 block residual $r^{(n)}_{t,b}$ 以供下一個 chunk 重用。
- **Autoregressive video diffusion with rolling KV cache**:以 chunk-by-chunk 因果生成方式串接歷史條件;rolling KV cache 以 FIFO 淘汰舊條目,提供有界記憶體下的長時序生成,也是 X-Cache 必須保護的誤差傳播臨界點。
- **Few-step distillation (S = 4)**:將多步去噪蒸餾為 4 步以滿足即時互動需求;此設定即是 cross-step caching 失效、cross-chunk caching 才有意義的根本前提。
- **adaLN-Zero conditioning**:每個 DiT block 透過 adaLN-Zero 注入時序嵌入與動作向量等條件;X-Cache 的 action-condition fingerprint 通道即是針對此注入路徑而設,以偵測跨 chunk 的離散控制變化。
- **Causal VAE (WAN 2.2 base)**:X-world 沿用 WAN 2.2 的 latent video diffusion 架構,以 causal VAE 將 7 路攝影機潛在空間編解碼為 12 FPS 同步影像;X-Cache 僅作用於 DiT 端,VAE 在實驗中保持原樣。
- **Multi-camera view-group fingerprint**:7 路攝影機按共享網格形狀分為 front / side / rear 三組 view group,每組共用一個 3D 子採樣 fingerprint,搭配 global mean 與 action-condition 兩條輔助通道,構成 dual-metric gating 的輸入表徵。

### 2.4 Core Argument

作者主張既有 diffusion caching 在 few-step 互動式 AR 世界模型上失效的根因,是它們全都建立在「相鄰 denoising step 之間 DiT block 輸出高度相似」這條假設之上;一旦蒸餾到 4 步,每一步都帶有實質且不可省略的結構性更新,跨 step 冗餘被擠壓殆盡,任何 cross-step 重用都會直接撞穿品質下限。同時,平滑外插類方法又會被外部 policy 在 chunk 邊界注入的離散煞車、轉向、變道指令(經 adaLN-Zero 進入每個 block)破壞局部平滑假設,而 sequence-level 平行解碼又因閉迴圈必須先看到當前 chunk 才有下一個 action 而失去前提。基於此,他們指出真正仍存在且不會被 few-step 蒸餾消滅的冗餘,是「物理場景在連續 chunk 之間緩慢演化」所帶來的跨 chunk 相似性——這條冗餘來自世界本身的時間連續性,而非 denoising 軌跡的鄰近性。因此邏輯上必須把快取軸從 denoising step 換到 generation chunk:在相同 $(t,b)$ 位置快取 block residual、用 3D 網格子採樣加上全域與動作通道的 fingerprint 偵測差異、用雙指標(cosine 全域方向 + 最大 token 偏差局部離群)守住安全邊界,並以每位置 EMA 自適應門檻取代手調全域閾值。最後,因 autoregressive 推理會把近似誤差透過 KV cache 永久寫入未來所有 chunk,他們進一步辨識出 KV update 這一寫入時刻為誤差放大臨界點,強制其完整計算以截斷誤差傳播。整套方案因此不是與 cross-step caching 競爭,而是在一條全新軸上恢復可被安全重用的冗餘。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(260 words)

標題 *X-Cache: Cross-Chunk Block Caching for Few-Step Autoregressive World Models Inference* 已將論文的三個關鍵約束直接寫入命名:加速軸是 cross-chunk(而非 cross-step)、加速粒度是 DiT block、目標部署情境是 few-step autoregressive world model 推論。abstract 把問題定位在 closed-loop interactive world simulation:autoregressive video diffusion 雖能滿足可控的多攝影機高擬真生成,但推論成本對 real-time 部署仍是瓶頸。接著 abstract 切割了現有 caching 方案為何無法直接套用——其一,cross-step caching 仰賴步間冗餘,在 few-step distillation 後幾乎被消除;其二,sequence-level parallelization(如 Block Cascading)需要事先知道未來 chunk 的 conditioning,但 closed-loop 互動式生成無法滿足。abstract 因此把 X-Cache 的貢獻命題化:它不是在 denoising step 之間取重用,而是改沿 generation chunk 軸取重用,以 block residual cache 為單位、以 dual-metric gating 在每個 block 上獨立決定 reuse 或 recompute,並以 structure- 與 action-aware fingerprint 作為輸入相似度判據。abstract 也預先把一個延伸危險(autoregressive KV cache 的污染)寫入設計動機:KV update chunk 必須無條件 full-compute 以切斷錯誤傳播。最後給出一個具體營運級驗證——在 X-world(production 多攝影機 action-conditioned 駕駛 world model,multi-block causal DiT、few-step denoising、rolling KV cache)上達成 71% block skip rate 與 2.6× wall-clock speedup,且品質衰退極小。整段 abstract 為後續論文奠定了「為什麼舊方法不行」與「新軸是什麼」這兩個立論支柱。

### 3.2 Introduction

(900 words)

Introduction 的論述分四步推進。第一步先把 driving world model 抬升為 autonomous driving 的基礎設施:它能透過條件化 ego action 與感測歷史生成未來觀察,從而支援端到端策略的 closed-loop 評估與 online RL,而這兩種能力是純 real-world 測試難以達成的;這一段把後文要加速的對象限縮為「互動式 simulator」,而非離線生成器。第二步把架構選擇收斂到 autoregressive video diffusion:相對於 bidirectional video diffusion 一次生成整段 clip,causal autoregressive 形式以 chunk by chunk 推進,每個 chunk 只條件化於既有內容,這個 streaming 結構天然契合「收到 action 立刻回應」的互動需求;再加上 persistent KV cache 把記憶體上界化、以及 few-step distillation 拉高吞吐量,得到的這個系統正是本文要加速的標的。第三步建立反差,逐一拆解既有方案的失效來源。其一,cross-step caching(DeepCache、δ-DiT、TimestepEmbedding-style、BWCache)假設相鄰 denoising step 的 block 輸出相近,但 few-step(S=4)規模下每一步都包含實質且非冗餘的結構更新,跨步重用空間幾乎消失;FlowCache 與 SCOPE 即使把 caching policy 改為 chunk-wise 或加入 predictive extrapolation,仍建立在 cross-step 冗餘前提且只在 many-step schedule 下被驗證。其二,interactive simulation 還暴露兩個結構性難題:一是許多 caching 方法仰賴 cached feature 的局部 smoothness 假設,但 per-chunk action 由外部策略發出,在 chunk 邊界本質上不平滑(離散煞車、轉向、變道指令透過 adaLN-Zero 進入每個 DiT block),smoothness 假設恰好在 world model 最該回應控制的時刻失效;二是 closed-loop 推論存在嚴格因果依賴,世界模型必須等到外部策略觀察到當前 chunk 並輸出對應 action 後才能繼續,因此排除了 Block Cascading 這類需要預知未來 conditioning 的 sequence-level parallel 方案,所有加速必須留在當前 generation 邊界內。第四步翻轉:作者指出 few-step autoregressive world model 仍有一條未被觸及的冗餘軸——cross-chunk。在自駕情境中物理場景變化相對於生成率而言緩慢且連續,於是同一 (denoising step, block) 位置在連續兩次生成之間的 block 輸入高度相似;這條冗餘來自物理連續性,不依賴 denoising trajectory 的接近性,因此在 few-step distillation 抹除 cross-step 冗餘後仍然存活。基於此,Introduction 列出五項貢獻:(1) cross-chunk block caching 本身,作者宣稱這是首個沿此軸操作的方法;(2) structure-aware、action-aware 的 compact fingerprint,於 latent 的 3D (F, H, W) grid 上採樣以保幾何均衡,並附 global mean channel 與 action-condition channel 補強 bulk drift 與控制敏感度;(3) KV update frame protection,辨識並強制 full compute 此關鍵點以切斷錯誤累積;(4) per-(t, b) adaptive cosine threshold,以 EMA 自我調節並由 quality floor 鉗制下界,免除手調;(5) 在 production driving world model 上的實證——71% skip、2.6× DiT speedup、品質衰退可忽略。Introduction 結尾還補了一個方法論說明:既有 caching 方案皆沿 cross-step 軸並在 many-step、one-shot 設定下評估,因此與本文目標場景不直接可比,實驗將以 ablation 與絕對表現為主而非 head-to-head。這段話為 §6 的實驗範圍寫法提供了正當性,並把讀者預期從「比贏 baseline」拉回「驗證新軸的可行性」。

### 3.3 Related Work / Preliminaries

(150 words)

論文沒有獨立的 Related Work 段落,既有方法的批判已壓進 Introduction。Section 2.1 *Preliminaries: AR Video Diffusion Inference* 在進入方法前先固定符號:$n$ 為 generation step(第 $n$ 個 video chunk),$t \in \{0, \dots, S{-}1\}$ 為 chunk 內 denoising step,$b \in \{0, \dots, B{-}1\}$ 為 DiT block index;chunk latent 自高斯雜訊起、經 $S$ 步迭代精煉,每步穿過全部 $B$ 個 block,並以標準 residual connection 串接:$x^{(n)}_{t,b} = x^{(n)}_{t,b-1} + f_b(x^{(n)}_{t,b-1}; c^{(n)}_t)$。由此定義 *block residual* $r^{(n)}_{t,b} = x^{(n)}_{t,b} - x^{(n)}_{t,b-1}$,這是後續 cross-chunk caching 的最小重用單位。Preliminaries 還明確指出 chunk 完成全部 denoising 後會多跑一次 *KV update pass*,以乾淨 latent 寫入 persistent KV cache 供未來 chunk 經 cross-attention 條件化,並在 rolling KV 容量上限時以 FIFO 淘汰最舊條目——這個流水細節是後文 §2.5 KV update frame protection 的根本依據,也預埋了「為何此 chunk 不能 skip」的物理理由。

### 3.4 Method (overview narrative)

(1500 words)

Section 2 把 X-Cache 拆成五個彼此互鎖的子模組,但敘事上是由一個觀察驅動的單一機制再層層加防護。先在 §2.2.1 重申關鍵觀察:在自駕等物理連續環境中,連續兩個 chunk 的場景相對於生成率變化平緩,因此同一 (denoising step, block) 位置的 block 輸入 $x^{(n)}_{t,b-1}$ 與 $x^{(n-1)}_{t,b-1}$ 高度相似;且這條 cross-chunk 冗餘獨立於 $S$,在 $S=4$ 的 few-step distillation 下仍然成立——這是與 cross-step caching 最根本的分野。§2.2.2 把這條觀察落為機制:當 (n, t, b) 處 block 被 full compute 時,將其 residual 緩存為 $\hat{r}_{t,b} \leftarrow r^{(n)}_{t,b}$;下一個 generation step $n{+}1$ 若 gating 判定可 skip,則以 $\tilde{x}^{(n+1)}_{t,b} = x^{(n+1)}_{t,b-1} + \hat{r}_{t,b}$ 完成附加式重用。緩存以 (t, b) pair 為索引,確保跨 chunk 重用發生於同一 denoising trajectory 位置,而不是任意配對。§2.2.3 規定 warmup:$n=0$(可組態為 $W \ge 1$)時所有 block 全算,以填滿 cache。

§2.3 是 gate 的核心:在 warmup 之外,X-Cache 對每個 block 單獨判斷可否 skip,判據由兩個指標組成。指標的輸入不是整個 block tensor,而是一個 fingerprint $\phi(x)$。輸入張量形狀為 $B \times V \times L \times C$,token 軸 $L$ 是被攤平的 $(F_g \times H_g \times W_g)$ 時空格;若沿一維 $L$ 均勻取樣會在 frame 與空間維度間覆蓋失衡,因此作者改在 3D grid 上取樣:給定預算 $K$ tokens,把三軸依 grid 縱橫比例配額為 $k_F : k_H : k_W \approx F_g : H_g : W_g$ 且 $k_F k_H k_W \approx K$,各軸取均勻間隔索引,以 Cartesian product 拿出形狀 $B \times V \times (k_F k_H k_W) \times C$ 的緊湊 fingerprint(實作 $K=32$);若 $L \le K$ 直接保留全 $x$,grid shape 不可得時退回 1D linspace。在多攝影機場景下,7 cameras 依共享 grid shape 分為 front/side/rear 三個 view group,group 內 cameras 沿 $V$ 軸堆疊並共享一份 per-group fingerprint。fingerprint 之外另附兩條 auxiliary channels:*Global channel* 為 per-view-group 沿 token 軸的序列均值,捕捉 sparse 空間樣本可能漏掉的 bulk latent drift;*Condition channel* 把 per-chunk action vector(透過 adaLN-Zero 進入 block)攤平後作為一筆額外 fingerprint entry,讓 input-similarity 直接對控制變化有敏感度。其餘 conditioning(dynamic-object、lane embedding、text)因為 padding 會跨 chunk 變動且時間尺度較慢,放任 cascade 與 anchor block 機制處理。Metric 1 是 cosine similarity,逐 entry 計算後對全部 entries 取 *最小值* 聚合($s_{cos} = \min_k s^{(k)}_{cos}$),只要任一 view group、global、或 action-condition 通道偏離就觸發 recompute;Metric 2 是 maximum token deviation,僅在 per-group 空間 fingerprints 上計算,各 group 取 *最大值* 聚合($d_{max} = \max_g d^{(g)}_{max}$)以捕捉局部 outlier。Skip 條件是 $\text{skip}(t, b) = (s_{cos} \ge \tau_{cos}(t, b)) \wedge (d_{max} < \tau_{dev})$,亦即兩個指標同時通過——這個保守聚合正是 fingerprint 走 sparse 路線時的安全網。

§2.4 把「取一個全域 cosine threshold」改成 per-(t, b) 自適應:對每個 (t, b) 維護觀察到的 cosine 相似度的 EMA $\bar{s}_{t,b} \leftarrow \alpha \cdot s^{(n)}_{cos} + (1-\alpha)\cdot \bar{s}_{t,b}$($\alpha=0.3$),threshold 取 $\tau_{cos}(t, b) = \max(\tau_{floor}, \bar{s}_{t,b} - m)$($\tau_{floor}=0.95$、$m=0.02$ 為實作預設,§3 表 1 改為 $\tau_{floor}=0.97$)。一致高相似度的 block 會把 EMA 推高,threshold 自然貼近其典型相似度以最大化 skip;相似度抖動的 block 則因 EMA 偏低而保守處理;quality floor 提供獨立於歷史的硬下界。整體效果是不需要外掛 budget controller 就能得到穩定的 per-chunk 計算量輪廓。

§2.5 將「方法本體可能踩到的雷」具象成四道防護。其一,*Denoising step 0 protection*:$t=0$ 時 latent 由高頻雜訊主導、conditioning 影響相對最大,且每個 KV update cycle 重新採樣雜訊並把上一 chunk 的乾淨輸出嵌入新 noisy latent,連續兩次生成在 $t=0$ 自然相似度低;預設強制 full compute,可選的 relax mode 改用近一的 $\tau^{strict}_0 = 0.999$。其二,*Anchor blocks*:前 $F_n$(預設 1)與後 $B_n$(預設 0)個 block 在所有 denoising step 都不被 skip,以保證 conditioning 透過 block 0 的 adaLN-Zero 必定被處理,改變後的輸出再 cascade 至下游 block 的 fingerprint。其三,*KV update frame protection*:若當前 generation step 的乾淨 latent 將被用於 KV update pass,X-Cache 進入 force-compute 模式——所有 block 全算,但 cache 仍然 attached 以刷新 fingerprints 與 residual,既保證 KV 條目精確,也避免下一個 generation 開頭的 double-heavy-frame penalty。其四,*Maximum staleness*:per-(t, b) 連續 skip 計數若超過 $M$,該 block 強制 recompute。整個 §2 因此是一條由「觀察 → 機制 → 度量 → 自適應 → 防雷」串成的封閉路徑,為 §3 的 settings 與量化結果鋪好評估目標。

### 3.5 Experiments (overview narrative)

(1900 words)

Section 3 與 Section 4 一同構成實驗論述,並把焦點如 Introduction 預告地放在 ablation 與絕對表現,而非與舊 caching 方法 head-to-head。§3.1 先定錨硬體與模型:所有實驗在 Alibaba T-Head 的 *Zhenwu (真武) 810E* 加速器(本文稱 PPU)上跑,單卡 96 GB HBM2e、原生支援 FP16/BF16/INT8,DiT forward 一律以 BF16 在單張 PPU 執行;這把後文所有 wall-clock 數字鎖在同一條件下。受測模型是 X-World——以 WAN 2.2 為底、causal VAE 加 DiT denoiser、12 FPS 同步生成 7 cameras 360° 影片的 production 駕駛 world model;streaming AR rollout 中每個 chunk 由高斯雜訊起算 4 步 denoising,搭配固定容量、FIFO 淘汰的 rolling KV cache 維持 long-horizon。資料集是 X-World 訓練分布的 internal held-out split,並嚴守 X-World 設計的 closed-loop 推論協定:每個 chunk 只能看到 1 frame 的 7-camera 初始歷史、僅屬於本 chunk 的 conditioning(ego action state、dynamic-agent poses、static road-element annotations、scene-level text caption),以及 rolling KV cache;causal 架構禁止任何 look-ahead。per-chunk action 不對模型預先公開,而是由錄製軌跡逐 chunk 重播以保再現性,從 DiT 視角與 live policy stream 不可區分。每段 clip 產生 264 frames(約 22 秒、12 FPS)的多攝影機未來影片,rollout 中沒有任何 per-frame visual ground truth。split 涵蓋三個情境組:7 個 *urban-street*(密集車流、行人、店面)、3 個 *highway*(高架快速道路與一般高速公路)、3 個 *urban u-turn*(劇烈航向變化、跨 chunk 變動最大),並以 u-turn 組壓力測 gating 假設。指標切成三類:compute 面回報排除 warmup chunks 的 *block skip rate*(以 cached residual 重用的 block 評估比例),並進一步沿 denoising step 與 block index 拆解;efficiency 面回報單張 PPU 的 *per-chunk DiT wall-clock* 與相對 same-seed/same-conditioning/same-KV 基線的 DiT speedup,且明確排除 VAE encoder/decoder、data loading、post-processing、跨裝置傳輸;fidelity 面把 X-Cache rollout 與其對應 full-compute reference rollout 在解碼後做 frame-level 比較,因兩支共用同一 decoder,差異純粹來自 DiT 端;以 PSNR、SSIM、LPIPS 跨 7 cameras 平均,並另外計算拼接 7-view 的 *7-cam* 列。default hyperparameters 集中在 Table 1:$F_n=1$、$B_n=0$、$W=1$、$\tau_{floor}=0.97$、$m=0.02$、$\alpha=0.30$、$\tau_{dev}=2.00$、最大連續 skip 關閉、KV-update-chunk 保護開、step-0 保護關。

§3.2 把結論用一段話定下來:三個 split 上 DiT speedup 介於 2.65× 到 2.70× 之間,SSIM 高於 0.9990、LPIPS 低於 4e-4、7-camera PSNR 介於 51 至 55 dB;品質排序由 urban street 51.37 dB → u-turn 52.04 dB → highway 54.67 dB,但 skip rate 與 DiT 時間在三個 split 間的差距分別不超過 0.3 個百分點與 30 ms,亦即品質落差是「同一 cache 擾動被各情境像素吸收的程度」造成,並非 gate 行為改變。Figure 3 的視覺殘差也佐證:三個情境的差異圖呈現相同稀疏模式,殘差集中在車道線與遠景植被,即使放大 20× 仍在顯示尺度下消失。一個反直覺現象是 u-turn 的 PSNR 略勝 urban street,儘管前者 cross-chunk motion 更大;作者以兩個 clip-level 性質解釋——u-turn 中真正轉向只佔 22 秒中少數,大半時間是直行或變道,clip 平均被「urban-like」frame 拉抬;轉彎中相機本身有 lateral motion blur,把 reference frame 的高頻紋理抹平,反而降低了 cache-induced 擾動會被 surface 出來的 pixel error。Figure 4 的 per-frame PSNR 證實這個敘事:u-turn 曲線在轉彎窗口外貼近 urban 水準,僅在 frame 50 至 140 間明顯下沉,過後回升。Figure 5 與 Figure 6 進一步揭示 gate 行為的場景無關性:per-(step, block) cross-chunk cosine 在三個情境下熱圖形狀幾乎相同,blocks 1–19 維持在 0.95 以上、blocks 20–26 跌至 0.90 左右、沿 step 軸變化僅約 0.02;per-block skip rate 也是相同切分(blocks 1–19 貼著 0.75 的理論 plateau、blocks 20–26 落到約 0.69),三個情境曲線幾乎重合。這代表 Table 2 中 0.3 個百分點的 skip 差異來自固定 block 集合內的小幅度變動,而非情境決定哪些 block 可重用;per-chunk reuse budget 比 cosine 測試更先觸頂,連 u-turn 都沒被拉低 skip rate。作者另外點明兩件事:per-frame PSNR 不在 chunk 邊界出現飄移,代表 22 秒內 KV-update protection 仍然有效;per-camera PSNR 排序(F-C 最高、Rear 中、四側 cameras 低 2–6 dB)不應被解讀為 cache 訊號,因為 gate 對每個 (t, b) 是基於 7-camera-aware fingerprint 做單一決定,單一 PSNR 應以 shaded 7-cam 列為準。

Section 4 ablation 鎖定其它 settings、僅在 264-frame highway 持出 clip 上每次調整一個保護或超參數。基線(no cache)為 3.637 s、Default(step-0 off、$\tau_{floor}=0.97$)為 1.406 s 與 53.384 dB PSNR、2.59× speedup、71.3% skip。$\textit{Step-0 protection}$ 開啟會把 skip rate 從 71.3% 拉回 53.5%、speedup 自 2.59× 退至 1.84×,但本 clip 下品質維持到 SSIM 與 LPIPS 第四位小數;作者保留此選項作為 night、heavy rain、急轉的安全餘裕。$\textit{KV-update-chunk protection}$ 關閉是唯一造成顯著品質崩潰的設定:PSNR 從 53.4 dB 跌至 21.5 dB、LPIPS 上升三個數量級,而 skip rate 只多 9 個百分點、speedup 反而退到 2.18×,trade-off 顯然不利,因此這個保護是 hard 必開。$\textit{Front anchor } F_n=1$ 改為 0 可額外多 1.9 個百分點 skip、節省約 70 ms,PSNR 大致持平;但 block 0 是所有後續 block 的 residual 基底,在 KV-update cycle 被 skip 時下游錯誤無法自然 bound,本資料集未強烈暴露此失效模式,作者寧取保守預設。$\tau_{floor}$ sweep 從 0.90 到 0.96 對所有報告指標皆無變化:cosine 相似度分布大量集中在 1.0(7 個 urban-street clip 的 median 與 p75 皆為 1.0),且實際 threshold 是 $\max(\tau_{floor}, \text{EMA} - m)$,多數 (t, b) cell 的 EMA-minus-margin 落在 0.94–0.95,因此低於約 0.94 的 floor 會被 EMA 項主導;這代表 gate 對該參數在當前測試分布上不敏感,但在分布偏移時 floor 仍然定義 gate 的最低門檻,故保留可組態並選保守預設。整段實驗論述把「default 為何安全」「拿掉哪些保護會立刻壞」「哪些保護是冗餘但保留作 margin」三件事各自釘住,為 §6 的 limitations 鋪設正當理由。

### 3.6 Conclusion / Limitations / Future Work

(400 words)

Section 5 *Limitations* 與 Section 6 *Conclusion* 共同界定本研究的承諾邊界與外推方向。Limitations 段先誠實標示資料的有限性:所有報告 rollout 都是來自 X-World 訓練分布的 internal held-out split,且只跑 22 秒 clip,情境僅含 urban street、highway 與 u-turn,並未在更長 horizon 或分布外場景(夜間、惡劣天氣、激進駕駛、長時間 highway 巡航)上量測 X-Cache;在這些場景中 cross-chunk similarity 模式可能偏移,adaptive EMA threshold 也需要時間重新校準,目前回報的 skip rate 與品質數字在外推前不能直接套用。Table 1 的預設值同樣是在單一 held-out clip 上調出來的,且作者刻意選擇*保守*而非*激進*的設定:7-camera PSNR 落在約 53 dB、SSIM 高於 0.999、LPIPS 低於 $4 \times 10^{-4}$,完全在 imperceptible 範圍內,因此降低 $\tau_{floor}$、放寬 $\tau_{dev}$、或對 cross-chunk cos 持續高的 block 取消 front anchor 等 sweep 都應能拿目前的品質餘裕去換更多 skip 與 wall-clock,但 Pareto frontier 尚未在現有測試集上被描繪。Conclusion 段把全文重新拉回主題化敘事:X-Cache 的價值在於「打開了一條 cross-step caching 觸不到的冗餘軸」——在 few-step autoregressive video diffusion 模型上,沿連續 generation chunk 對 block residual 做重用。預設配置在 X-World 上重用 71% 的 DiT block 評估,DiT wall-clock 提速 2.6–2.7×,且品質衰退人類不可見。此性質跨 urban street、highway、u-turn 都成立,並把背後機制歸因於 *DiT 中的 block 位置決定 cross-chunk cosine pattern*,而非場景內容——這是支撐方法泛化主張的核心 evidence。ablation 也被作者重新整理成設計守則:KV-update-chunk protection 是不可放棄的 hard safety,而 step-0 protection、front anchor、$\tau_{floor}$ 屬於目前 workload 不會觸發但仍保留的 *soft 餘裕*,以對抗 distribution shift、long-horizon drift 與測試 split 未涵蓋的極端工況。未來工作明確點出方向:其它共享相同 template 的 few-step interactive AR world model(以 WorldPlay 為代表)是自然的下一個延伸目標,但其更大、更突兀的 action transition 是否仍能維持本論文的速度與品質下限,作者表明仍需驗證;這把 X-Cache 的承諾範圍封閉在 X-World 類架構,並把跨架構泛化留作開放題。

## 4. Critical Profile

### 4.1 Highlights

- 提出第一個沿「相鄰 generation chunk」軸而非「相鄰 denoising step」軸的 training-free DiT caching 方法,直接針對 few-step distilled AR 世界模型(p. 2–3)。
- 在 production 級 X-world 多攝影機 causal DiT 上達成 71% block skip rate 與 2.6× DiT wall-clock 加速(Table 2,p. 9)。
- 解碼端品質保持在不可感知範圍:SSIM 全部高於 0.9990、LPIPS 低於 $4 \times 10^{-4}$、7-cam PSNR 介於 51–55 dB(Table 2)。
- 設計 structure-aware + action-aware fingerprint:在 latent 的 $(F_g, H_g, W_g)$ 3D 網格上以 $K=32$ token 比例採樣,加上 global mean 與 adaLN-Zero action channel,避免 1D 平鋪的覆蓋偏差(§2.3.1–§2.3.2)。
- Dual-metric gating 同時要求 $s_\mathrm{cos} \geq \tau_\mathrm{cos}(t,b)$ 與 $d_\mathrm{max} < \tau_\mathrm{dev}$,並以「跨 view group 取最小 cosine、取最大 deviation」做保守聚合(Eq. 7,§2.3.5)。
- 識別 KV update chunk 為 AR 推理特有的誤差放大臨界點,強制其完整計算;ablation 顯示移除此保護會使 PSNR 從 53.4 dB 直接崩到 21.5 dB(Table 3,p. 11)。
- 提出 per-$(t,b)$ EMA 自適應 cosine 門檻 $\tau_\mathrm{cos}(t,b) = \max(\tau_\mathrm{floor}, \bar{s}_{t,b} - m)$,以 $\alpha = 0.3$、$\tau_\mathrm{floor}=0.97$、$m=0.02$ 取代手調全域閾值(§2.4,Table 1)。
- 三類場景(urban / highway / u-turn)的 skip rate spread 不到 0.3 個百分點、DiT 時間差不到 30 ms,顯示 gating 行為由 block 位置而非場景內容決定(Table 2,Fig. 5–6)。
- 22 秒 rollout 的 per-frame PSNR 曲線在 chunk 邊界沒有可見漂移,實證 KV-update protection 在長時域下沒有累積誤差(Fig. 4)。
- 對抗性 u-turn 場景反而比 urban 街景略佳(7-cam PSNR 52.04 vs 51.37 dB),作者以「轉向佔比少、運動模糊降低高頻細節」自圓其說(§3.2)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 評估僅限 X-world 訓練分佈內、單一 22 秒長度的 13 段 held-out clip;夜間、惡劣天氣、激進駕駛、長時間高速巡航等情境完全未測,EMA 門檻在分佈外需要時間重新校準(§5,p. 12)。
- 預設超參數是在「單一 held-out clip」上挑選,刻意保守而非極限調校;Pareto frontier(降低 $\tau_\mathrm{floor}$、放寬 $\tau_\mathrm{dev}$、移除 front anchor)未繪製(§5)。
- 沒有與 FlowCache、SCOPE 等先前 caching 方法做 head-to-head 比較,理由是 regime 不同;作者主動承認實驗只能聚焦在 ablation 與絕對效能(§1,p. 3)。
- $\tau_\mathrm{floor} \in \{0.90, \dots, 0.96\}$ 的掃描所有指標皆無變化,作者承認這只證明在當前測試分佈下 floor 是無效的,而非保證在分佈外仍會無效(§4.4,p. 11)。
- 對其他 few-step 互動式 AR 世界模型(如 WorldPlay)的可遷移性「仍待驗證」,因其 action transitions 更大更突兀(§6,p. 12)。

#### 4.2.2 Phyra-inferred

- 全部 fidelity metrics(PSNR / SSIM / LPIPS)都是相對「full-compute baseline」而非 ground-truth video 計算的,因此衡量的是「對自家 baseline 的還原度」而非真實場景保真度;若 baseline 本身存在偏差且 X-Cache 將其放大,目前的指標體系完全看不出來(Table 2 caption 明示)。
- 評估資料量極小:13 段 22 秒的 clip 約 286 秒總時長,71% / 2.6× 的頭條數字建立在這個樣本量上;對於宣稱「production 驗證」的工作而言,缺乏分佈外、長時域與多元 episode 的覆蓋。
- 「regime mismatch 所以無法 head-to-head」是策略性迴避:FlowCache / SCOPE 至少可以在 4-step 上跑出一條品質-加速曲線,即便預期會劣化也應呈現,目前的論述等於同時宣稱無法比較且優於對手。
- 71% 的 skip rate 緊貼 $W=1$ + 4-chunk 重用窗所暗示的 0.75 理論上限(Fig. 6 dashed line),這意味著 gate 大多時候在「天花板處飽和」而非真正在發掘資料相關的 skip 機會;在更困難的分佈上是否還有探索空間無從得知。
- 側面攝影機(S-FL/FR/RL/RR)PSNR 系統性比 F-C 低 2–6 dB(Table 2),作者以「per-(t,b) 共用 7-camera-aware fingerprint」帶過,但沒有檢驗 view-group 設計是否系統性地對側面視角保護不足。
- 沒有任何 fingerprint + cosine + EMA + cache management 的 overhead 拆解;DiT wall-clock 為唯一報告口徑,gate 在每個 $(t,b)$ cell 都執行,其相對成本未被隔離。
- Adaptive threshold 的 quality floor 在 §4.4 被自證「在當前資料上不啟動」,亦即被論文作為「絕對安全保證」最重點包裝的元件,實驗上完全沒被觸發過。
- KV-update protection 的必要性僅以單 clip ablation 與 32 dB 落差證明;沒有測試任何介於「全跳」與「全算」之間的折衷(部分重算、加權混合、僅保護 K 而非 V),因此無法判斷此一 hard constraint 是否壓低了可能的加速天花板。
- Action channel 的單獨貢獻沒有 ablation:fingerprint 同時包含 spatial、global、condition 三類訊號,卻沒有逐一 leave-one-out,因此「action-awareness」的真實價值無法量化(§2.3.2)。

### 4.3 Phyra's Judgment (summary)

真正新穎的貢獻是觀念面的轉軸:作者點出 few-step distillation 已經消滅 cross-step 冗餘,但物理場景在連續 chunk 之間的緩慢演化讓 cross-chunk 冗餘仍然存在,並把它包裝成乾淨的 caching 軸,這是值得記住的概念貢獻。Dual-metric gate 與 KV-update protection 是合理的工程直覺,後者由 ablation 強力佐證,其餘部件(3D 網格 fingerprint、EMA 門檻)則屬於 DiT + rolling KV cache template 上的紮實工程細節。最關鍵未解的問題是分佈外行為:13 段 in-distribution clip、71% 緊貼 0.75 結構天花板、quality floor 從未啟動,這三件事合起來無法回答 X-Cache 在分佈漂移、長時域、或更突兀 action 流時是否仍然成立。

## 5. Methodology Deep Dive

### 5.1 Method Overview

X-Cache 把 training-free diffusion caching 的重用軸從「相鄰 denoising step」整個搬到「相鄰 generation chunk」。在 few-step distilled AR world model（X-World，$S=4$）中，每個 denoising step 都帶有實質且不可省略的結構性更新，因此跨 step 的 DiT block 輸出相似度被擠壓到無法安全重用；但 autonomous driving 場景在連續 chunk 之間的物理演化遠慢於生成速率，於是 *相同* $(t, b)$ 位置的 block input 在 chunk $n$ 與 chunk $n{+}1$ 之間仍高度相似。X-Cache 為每個 DiT block 在每個 denoising step 維護一份 residual cache $\hat r_{t,b}$，下一個 chunk 在通過該 block 時若 gating 通過，就以 additive reuse $\tilde x^{(n+1)}_{t,b} = x^{(n+1)}_{t,b-1} + \hat r_{t,b}$ 直接近似輸出，跳過 attention 與 MLP 計算（Eq. 3、Eq. 4）。

Gating 由兩個獨立指標守住安全邊界。第一個指標是「方向相似度」cosine：對 block input $x^{(n+1)}_{t,b-1}$ 取 structure- & action-aware fingerprint $\varphi(\cdot)$，逐條目（per view group spatial entry + global channel + action channel）對上一個 chunk 的同位置 fingerprint 算 cosine，再對所有條目取 *最小值* 作為 $s_{\cos}$；第二個指標是「局部離群」max-token deviation $d_{\max}$，只在 spatial fingerprint 上計算，對 view group 取 *最大值*。block 只有在 $s_{\cos} \ge \tau_{\cos}(t,b)$ 且 $d_{\max} < \tau_{\mathrm{dev}}$ 時才被 skip（Eq. 7）。$\tau_{\cos}(t,b)$ 不是手調全域常數，而是用該 $(t,b)$ 位置自身的 cosine 歷史 EMA 動態調整，並用 $\tau_{\mathrm{floor}}$ 從下方夾住做品質硬底線（Eq. 8、Eq. 9）。

X-Cache 在 AR inference 上額外加四道保險，其中只有第一道是「移除會直接撞穿品質底線」的硬性必要：(i) **KV update frame protection**，在會把 clean latent 寫進 rolling KV cache 的 generation step，強制所有 block full-compute，截斷誤差透過 KV 永久汙染未來 chunk 的傳播；(ii) **front anchor** $F_n=1$，block 0 永遠 full-compute，讓更新後的 conditioning 經 adaLN-Zero 注入後可以 cascade 到後續 block，使其 fingerprint 自然偏離舊 cache 而觸發重算；(iii) **denoising step-0 protection**（預設 off，可選 strict 模式 $\tau_0^{\text{strict}}=0.999$），因為 $t{=}0$ 受 noise resampling 與前一 chunk context 注入影響，自然 cosine 較低；(iv) **maximum staleness** $M$，限制單一 $(t,b)$ 連續 skip 次數。

### 5.2 Pipeline Diagram with Tensor Shapes

```
generation step n         (cache state)          generation step n+1  (target)
══════════════════         ══════════════         ══════════════════════════════
                           r̂_{t,b}  for all (t,b)
                           [B, V, L, C]                  init noise x^{(n+1)}_{0,0}
                                 │                            [B, V, L, C]
                                 │                                  ↓
                                 │                       Denoising loop t = 0..S-1   (S=4)
                                 │                                  ↓
                                 │                       Block loop  b = 0..B-1      (B ≈ 30)
                                 │                                  ↓
                                 │                       block input x^{(n+1)}_{t,b-1}
                                 │                            [B, V, L, C]
                                 │                                  ↓
                                 │            ┌─────────────────────┴─────────────────────┐
                                 │            │                                           │
                                 │            ↓ Fingerprint φ(x^{(n+1)}_{t,b-1})           ↓
                                 │            │                                           │
                                 │            ├→ 3D-grid subsample (K=32 tokens)           │
                                 │            │     spatial fp:  [B, V, k_F·k_H·k_W, C]    │
                                 │            ├→ global mean over L axis                   │
                                 │            │     global fp:   [B, V, 1, C]              │
                                 │            └→ action vector lift (adaLN-Zero c^{(n+1)}_t)│
                                 │                  action fp:   [B, 1, A, ?]              │
                                 │                                                         │
                                 │            ↓ Dual-metric gate vs cached φ(x^{(n)}_{t,b-1})│
                                 │                  s_cos = min over all fp entries  scalar │
                                 │                  d_max = max over view groups    scalar │
                                 │                                                         │
                                 │            ↓ Adaptive τ_cos(t,b)                         │
                                 │                  s̄_{t,b} ← α · s^{(n+1)}_cos + (1−α)·s̄_{t,b}
                                 │                  τ_cos(t,b) = max(τ_floor, s̄_{t,b} − m) │
                                 │                                                         │
                                 │            ↓ skip = (s_cos ≥ τ_cos) ∧ (d_max < τ_dev)    │
                                 │                     ∧ b ≥ F_n ∧ (t>0 if step-0 protect)  │
                                 │                     ∧ chunk is NOT a KV-update chunk     │
                                 │                                                         │
                                 │       ┌────────────────┴──────────────────┐             │
                                 │       │ skip = TRUE                       │ skip = FALSE│
                                 │       ↓                                   ↓             │
            cache READ ──────────┼──→ r̂_{t,b}                       f_b(x^{(n+1)}_{t,b-1}; c^{(n+1)}_t)
                                 │   [B, V, L, C]                      = r^{(n+1)}_{t,b}    │
                                 │       │                              [B, V, L, C]       │
                                 │       ↓                                   ↓             │
                                 │   x̃^{(n+1)}_{t,b}                   x^{(n+1)}_{t,b}     │
                                 │   = x^{(n+1)}_{t,b-1} + r̂_{t,b}     = x^{(n+1)}_{t,b-1}  │
                                 │   [B, V, L, C]                       + r^{(n+1)}_{t,b}   │
                                 │                                      [B, V, L, C]       │
                                 │                                           │             │
            cache WRITE ←────────┼───────────────────────────────────────────┘             │
                  r̂_{t,b}        │   r̂_{t,b} ← r^{(n+1)}_{t,b}                              │
                  [B, V, L, C]   │                                                         │
                                 └─────────────────────────────────────────────────────────┘

After all S denoising steps complete:
                                                  ↓ KV update pass on clean latent
                                                  ↓ FORCE full-compute for ALL blocks
                                                  ↓ append K, V to rolling KV cache
                                                       [B, V, L_kv, d_kv]   (FIFO eviction)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 AR Video Diffusion Inference (Preliminaries)

**Function:** 描述 X-World 在不啟用 X-Cache 時的 baseline forward pass，同時定下後續所有索引與 residual 的記號。

**Input:**
- Name: `x^{(n)}_{0,0}` (chunk-$n$ 初始 noise latent)
- Shape: `[B, V, L, C]`，其中 `L = F_g · H_g · W_g`
- Source: 從 $\mathcal{N}(0, I)$ 重新採樣（每個 KV update cycle 都會 resample），加上由前一 chunk 透過 rolling KV cache 餵入的 cross-attention context

**Output:**
- Name: `x^{(n)}_{S-1, B-1}`（chunk $n$ 完成 $S$ 步 denoising 後的 clean latent）
- Shape: `[B, V, L, C]`
- Consumer: KV update pass，再餵給 causal VAE decoder 解成像素影格

**Processing:**

對 $t = 0, \dots, S-1$ 內所有 $b = 0, \dots, B-1$ 串行展開 Eq. 1：
$$x^{(n)}_{t,b} = x^{(n)}_{t,b-1} + f_b\!\left(x^{(n)}_{t,b-1};\; c^{(n)}_t\right)$$
$f_b$ 是第 $b$ 個 DiT block，$c^{(n)}_t$ 包含 timestep embedding、action embedding、text embedding 等 conditioning。完成所有 $S$ 步後再多跑一次 forward 做 KV update（見 §5.3.6）。

**Key Formulas:**

$$r^{(n)}_{t,b} \;=\; f_b\!\left(x^{(n)}_{t,b-1};\; c^{(n)}_t\right) \;=\; x^{(n)}_{t,b} - x^{(n)}_{t,b-1} \quad\text{(Eq. 2)}$$

**Implementation Details:**

X-World 在 WAN 2.2 之上以 causal VAE + multi-block causal DiT 形成 latent video diffusion；7 顆 camera 在 12 FPS 下生成同步 360° 影像，distillation 後 $S = 4$。所有 DiT forward pass 在 BF16 下執行於單一 PPU（Alibaba T-Head Zhenwu 810E，96 GB HBM2e）。block 總數 $B$、batch $B$、camera 數 $V = 7$、token 軸 $L$、channel $C$、$F_g/H_g/W_g$ 具體數值論文未明確列出，但 Figure 5/6 暗示 $B \approx 30$（block 索引 0–29）。

#### 5.3.2 Cross-Chunk Residual Cache

**Function:** 把每個 fully-computed block 的 residual 以 $(t, b)$ 為 key 存下來，在下一個 generation step 同位置進行 additive reuse。

**Input:**
- Name: `r^{(n)}_{t,b}`（在 chunk $n$ 完整跑出來的 block residual）
- Shape: `[B, V, L, C]`
- Source: §5.3.1 Eq. 2 的 full-compute 結果

**Output:**
- Name: `r̂_{t,b}`（cache 內的 residual entry）和 reuse 路徑下的 `x̃^{(n+1)}_{t,b}`
- Shape: `[B, V, L, C]`
- Consumer: 下個 chunk $n{+}1$ 在 $(t,b)$ 通過 dual-metric gate 後讀取

**Processing:**

當 $f_b$ 在 chunk $n$ 完整計算後，立刻以 Eq. 3 寫入 cache：
$$\hat r_{t,\,b} \;\leftarrow\; r^{(n)}_{t,b}$$
chunk $n{+}1$ 在 gate 通過時以 Eq. 4 重用：
$$\tilde x^{(n+1)}_{t,b} \;=\; x^{(n+1)}_{t,b-1} + \hat r_{t,b}$$
cache 以 $(t, b)$ pair 索引，保證 reuse 一定發生在相同 denoising trajectory 位置。

**Key Formulas:**

$$\hat r_{t,b} \leftarrow r^{(n)}_{t,b} \quad\text{(Eq. 3)} \qquad \tilde x^{(n+1)}_{t,b} = x^{(n+1)}_{t,b-1} + \hat r_{t,b} \quad\text{(Eq. 4)}$$

**Implementation Details:**

第一個 generation step（$n = 0$）沒有任何 cached residual 可用，所以 X-Cache 在 warmup 期 $W \ge 1$（預設 $W = 1$）強制全部 block full-compute 來 populate cache。即使在 KV update chunk 上強制 full-compute，cache 仍維持 attached（即 fingerprint 與 residual 都會被 refresh），避免下一個 chunk 還要再付一次重算成本（避免「double-heavy-frame」）。論文沒有指定 cache 在記憶體中的具體配置或 quantization 策略。

#### 5.3.3 Structure-Aware, Action-Aware Fingerprint

**Function:** 為每個 $(t, b)$ 建一個遠小於 block input 的指紋，讓跨 chunk 相似度比較成本可控，同時保留結構性與動作性敏感度。

**Input:**
- Name: `x^{(n)}_{t,b-1}`（block input）
- Shape: `[B, V, L, C]`，其中 `L = F_g · H_g · W_g`
- Source: 上一個 block 的輸出，或在 $b = 0$ 時為 denoising step $t$ 的初始 latent

**Output:**
- Name: `φ(x^{(n)}_{t,b-1})`，由三個部分串接而成
  - spatial per-group fingerprint：`[B, V_g, k_F·k_H·k_W, C]`，$k_F k_H k_W \approx K = 32$
  - global channel：`[B, V_g, 1, C]`（沿 token 軸取平均）
  - action-condition channel：`[B, 1, A, ?]`，$A$ 為 frames-per-chunk × action 維度的 flatten 長度
- Consumer: §5.3.4 dual-metric gating

**Processing:**

不在 flatten 後的 1D token 軸做 uniform 子採樣，而是直接在 3D grid $(F_g, H_g, W_g)$ 上做：

1. 設 fingerprint token 預算 $K$，依 grid aspect ratio 把預算分配給三個軸 $k_F : k_H : k_W \approx F_g : H_g : W_g$，且 $k_F k_H k_W \approx K$。
2. 每個軸上取 uniformly spaced indices，用三軸 Cartesian product 從 $x$ 抽取 token，得到緊湊的 spatial fingerprint。
3. 對 token 軸取平均，得到 global channel，補捉稀疏 spatial 子採樣可能漏掉的 bulk drift。
4. 把該 chunk 的 action vector flatten 後作為一條 fingerprint entry append 進去；它的形狀只由 action 維度與 frames-per-chunk 決定，所以 chunk 內為常數，每個 generation step 才會更新一次。

**Key Formulas:**

$$\varphi(x) \;=\; \mathrm{concat}\big(\,\varphi_{\text{spatial}}(x),\; \varphi_{\text{global}}(x),\; \varphi_{\text{action}}(c)\,\big)$$

對於 `L ≤ K` 的 block 直接保留整個 $x$；如果 grid shape 在 runtime 拿不到，fallback 為沿 $L$ 軸的 1D `linspace`。

**Implementation Details:**

實作上 $K = 32$。multi-camera 的 7 顆 camera 依共享 grid shape 分成三個 view group（front、side、rear），group 內 camera 沿 $V$ 軸 stack，每個 group 共享一條 spatial fingerprint，所以 spatial fingerprint 實際上是 3 條獨立張量。動態物件 (dynamic-object) 與 lane embedding 因為跨 chunk padding 不穩定、變化時序又較慢，沒有放進 fingerprint，改由 §5.3.6 的 step-0 protection 與 anchor block 機制保護；text condition 同理。$A$（action fingerprint flatten 長度）、$F_g/H_g/W_g$、$V_g$ 各 group 大小（front=2, side=4, rear=1 可從 camera 命名推得）等具體數值論文沒有明列。

#### 5.3.4 Dual-Metric Gating

**Function:** 在 $(t, b)$ 對 fingerprint 做兩條獨立的相似度檢查，決定該 block 在 chunk $n{+}1$ 是 reuse cached residual 還是 full-compute。

**Input:**
- Name: 當前 fingerprint `φ(x^{(n+1)}_{t,b-1})` 與上一個 chunk 同位置的 cached fingerprint `φ(x^{(n)}_{t,b-1})`
- Shape: 同 §5.3.3
- Source: §5.3.3，搭配 §5.3.2 維護的 cache

**Output:**
- Name: `skip(t, b)` 的布林決策
- Shape: scalar per $(t, b)$
- Consumer: §5.3.2 的 reuse / compute 分支與 §5.3.5 的 EMA 更新

**Processing:**

兩個指標共同把關：

1. **Cosine similarity**（Eq. 5）：對 fingerprint 中每一條 entry $k$（每個 spatial view group + global + action）獨立算 cosine，然後對所有條目取 *最小值* $s_{\cos} = \min_k s^{(k)}_{\cos}$。任何一條 entry 偏離都會把整體 $s_{\cos}$ 拉低。
2. **Maximum token deviation**（Eq. 6）：只對 per-group spatial fingerprint 計算 max-element deviation，對 view group 取 *最大值* $d_{\max} = \max_g d^{(g)}_{\max}$；global 與 action channel 不參與這個指標（它們只走 cosine）。
3. 兩條都通過才能 skip：
$$\text{skip}(t, b) \;=\; \big(s_{\cos} \ge \tau_{\cos}(t,b)\big) \wedge \big(d_{\max} < \tau_{\mathrm{dev}}\big) \quad\text{(Eq. 7)}$$
這種「min-cosine + max-deviation」的保守聚合方式，等於要求所有 view group / global / action 通道一致夠像，且任何單一 token 都沒有大幅偏離。

**Key Formulas:**

$$s^{(k)}_{\cos} \;=\; \frac{\varphi^{(k)}\!\left(x^{(n+1)}_{t,b-1}\right) \cdot \varphi^{(k)}\!\left(x^{(n)}_{t,b-1}\right)}{\big\|\varphi^{(k)}(x^{(n+1)}_{t,b-1})\big\| \cdot \big\|\varphi^{(k)}(x^{(n)}_{t,b-1})\big\|} \quad\text{(Eq. 5)}$$

$$d^{(g)}_{\max} \;=\; \frac{\max\!\left|\varphi^{(g)}(x^{(n+1)}_{t,b-1}) - \varphi^{(g)}(x^{(n)}_{t,b-1})\right|}{\mathrm{mean}\!\left|\varphi^{(g)}(x^{(n)}_{t,b-1})\right| + \epsilon} \quad\text{(Eq. 6)}$$

**Implementation Details:**

實驗預設 $\tau_{\mathrm{dev}} = 2.00$（Table 1）。$\tau_{\cos}(t,b)$ 由 §5.3.5 動態給出。論文沒有特別揭露 $\epsilon$ 的數值，僅標示為防除零的小常數。

#### 5.3.5 Adaptive Per-Position Threshold

**Function:** 每個 $(t, b)$ 自行從歷史 cosine 學一個專屬 cosine 門檻，避免手調全域常數，同時保留全域硬底線。

**Input:**
- Name: 該位置每次 gate 評估時的 $s^{(n)}_{\cos}$
- Shape: scalar per $(t, b)$ per generation step
- Source: §5.3.4

**Output:**
- Name: `τ_cos(t, b)`
- Shape: scalar per $(t, b)$
- Consumer: §5.3.4 的 Eq. 7

**Processing:**

對每個 $(t, b)$ 維護 cosine EMA，每次 gate 在該位置被評估時更新（Eq. 8），閾值由 EMA 減去 margin $m$ 後再被 $\tau_{\mathrm{floor}}$ 從下夾住（Eq. 9）。跨 chunk cosine 一直高的 block 會累積出激進的 EMA、貢獻多數 skip；cosine 波動大的 block 自然保守、不容易過閾。$\tau_{\mathrm{floor}}$ 提供一條與歷史無關的絕對品質底線。

**Key Formulas:**

$$\bar s_{t,b} \;\leftarrow\; \alpha \cdot s^{(n)}_{\cos} + (1-\alpha) \cdot \bar s_{t,b} \quad\text{(Eq. 8)}$$

$$\tau_{\cos}(t, b) \;=\; \max\!\big(\tau_{\mathrm{floor}},\; \bar s_{t,b} - m\big) \quad\text{(Eq. 9)}$$

**Implementation Details:**

實驗預設 $\alpha = 0.30$、$m = 0.02$、$\tau_{\mathrm{floor}} = 0.97$（Table 1，Section 4.4 的 ablation 也確認此值）。論文的 §2.4 文字一度寫 $\tau_{\mathrm{floor}} = 0.95$，但 Table 1 與 Section 4.4 的 sweep 都以 0.97 為 default，本筆記以 Table 1 為準。Section 4.4 的 sweep 0.90–0.96 顯示在 X-World 當前 workload 下 floor 對指標完全沒影響——cosine 分布集中在 1.0，p75 都仍是 1.0，EMA 減 margin 後典型值約 0.94–0.95，於是任何 $\tau_{\mathrm{floor}} \le 0.94$ 都被 EMA 項蓋過。論文不保證在更偏離訓練分布的資料上 floor 仍會 inactive，所以選擇保留可調。

#### 5.3.6 Safety Mechanisms

**Function:** 在 dual-metric gate 之外再加四道保險，分別對應 cache 永久汙染、conditioning visibility gap、step-0 條件主導、與長 staleness 累積誤差。

**Input:**
- Name: gate 的 skip 候選 + chunk-level 標記（是否為 KV update chunk、是否為 step-0、是否為 anchor block）+ 連續 skip 計數器
- Shape: 標記為 booleans / scalars per $(t, b)$
- Source: §5.3.4 的 gate decision；KV update 計畫由 AR inference loop 給出

**Output:**
- Name: 最終 skip / compute 決策（覆寫 §5.3.4）
- Shape: boolean per $(t, b)$
- Consumer: §5.3.2 的 reuse / compute 分支

**Processing:**

四道保險如下，作用順序由外而內覆寫 gate：

1. **KV update frame protection**：對「會把 clean latent 寫進 rolling KV cache」的 generation step，所有 block 強制 full-compute。clean K/V 一旦寫進 KV cache，就會被未來所有 chunk 透過 cross-attention 看到，因此這一刻是 cache 誤差能否「永久汙染」未來的臨界點。
2. **Anchor blocks $F_n$ / $B_n$**：前 $F_n$ 個 block 在所有 denoising step 都強制 full-compute（預設 $F_n = 1$），讓 block 0 永遠先消化當前 chunk 的 conditioning（含經 adaLN-Zero 注入的 action），其變化再 cascade 進後續 block 的 fingerprint 觸發 recompute；最後 $B_n$ 個 block 同樣可指定為 tail anchor（預設 $B_n = 0$）。這是一條與 step-0 protection 獨立的 per-step 保證。
3. **Denoising step-0 protection**：$t = 0$ 時 noisy latent 由 high-level noise 主導、conditioning 對 block output 的相對影響最大，且 noise 在每個 KV update cycle 會 resample，加上前一 chunk 的 output 透過 noisy input 注入新 context，使 $t = 0$ 自然出現低 cosine。預設 $t = 0$ 強制 full-compute；optional relaxation 用 strict threshold $\tau^{\text{strict}}_{0} = 0.999$，幾乎任何細微變動都會把 cosine 拉到 0.999 以下，效果上仍接近強制保護。一旦 step 0 用更新後的 conditioning 完整算過，其輸出會 cascade 到後續 step。
4. **Maximum staleness $M$**：對每個 $(t, b)$ 維護連續 skip 計數，超過 $M$ 就強制重算，避免長期 reuse 造成累積偏移。

**Key Formulas:**

$$
\text{skip}_{\text{final}}(t, b) =
\begin{cases}
\text{False}, & \text{if KV update chunk} \\
\text{False}, & \text{if } b < F_n \text{ or } b \ge B - B_n \\
\text{False}, & \text{if } t = 0 \text{ and step-0 protection on} \\
\text{False}, & \text{if consecutive-skip}(t, b) \ge M \\
\text{skip}(t, b), & \text{otherwise (Eq. 7)}
\end{cases}
$$

**Implementation Details:**

實驗預設（Table 1）為：$F_n = 1$、$B_n = 0$、$W = 1$、$\tau_{\mathrm{floor}} = 0.97$、$m = 0.02$、$\alpha = 0.30$、$\tau_{\mathrm{dev}} = 2.00$、$M$ off、KV-update-chunk protection on、step-0 protection off。Section 4 的 ablation 顯示移除 KV update protection 後 PSNR 從 53.4 dB 崩到 21.5 dB、LPIPS 提升三個數量級——這是論文唯一一條「拿掉就直接撞穿品質」的硬性安全要求；step-0 protection、front anchor、$\tau_{\mathrm{floor}}$ 在 X-World 當前 workload 下沒有實質影響，但論文選擇保留，作為對 distribution shift（夜間、惡劣天候、大角度 trajectory）與長 horizon drift 的 margin。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| X-World internal held-out split | Closed-loop interactive multi-camera driving world simulation (264-frame / ~22 s clips at 12 FPS, 7 cameras) | 13 clips: 7 urban-street + 3 highway + 3 u-turn | test only (held-out from X-World training distribution) |
| Single held-out highway clip (264 frames) | Ablation rollout under same closed-loop protocol | 1 clip | test only (used exclusively for §4 ablations) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Block skip rate (%) | Fraction of DiT block evaluations reusing a cached residual during a rollout, excluding warmup chunks | yes |
| DiT wall-clock per chunk (s) | Average per-chunk DiT denoiser time on a single PPU, excluding the first chunk; excludes VAE encode/decode, data loading, post-processing, and inter-device transfer | yes |
| DiT speedup (×) | Ratio of baseline full-compute DiT time to X-Cache DiT time under identical seed, conditioning, and KV state | yes |
| PSNR (dB) | Pixel-level fidelity on decoded frames vs. full-compute reference, averaged per camera and on the stitched 7-camera image | yes |
| SSIM | Structural fidelity on decoded frames vs. reference | no |
| LPIPS | Perceptual fidelity on deep features vs. reference (Zhang et al., 2018) | no |

### 6.3 Training and Inference Settings

X-Cache 是 training-free 的方法,沒有額外訓練流程;所有實驗皆為 inference-only。

- **Hardware**: 單張 Zhenwu (真武) 810E PPU(Alibaba T-Head),內含 96 GB HBM2e,原生支援 FP16/BF16/INT8。所有 DiT forward pass 以 BF16 執行。
- **Backbone model**: X-World [21],基於 WAN 2.2 的 ego-centric 多相機 controllable world model;以 causal VAE + DiT denoiser 在 12 FPS 下生成 7 路同步 360° 影片。
- **Inference protocol**: streaming autoregressive rollout,每個 chunk 從 Gaussian noise 起始、執行 4-step 去噪,並以 FIFO 維護固定大小的 rolling KV cache。每個 clip 產生 264 frames(≈22 秒);每個 chunk 的 conditioning 包含 ego action、dynamic-agent poses、static road-element annotations、scene-level text caption,以及 1 frame 的 7-camera 起始歷史。actions 由錄製軌跡逐 chunk 重播以保證可重現,causal 架構禁止任何 look-ahead。
- **X-Cache default hyperparameters** (Table 1, §3.1.5): $F_n=1$, $B_n=0$, warmup $W=1$, $\tau_{\text{floor}}=0.97$, margin $m=0.02$, EMA $\alpha=0.30$, $\tau_{\text{dev}}=2.00$, max staleness $M$ off, KV-update-chunk protection on, denoising step-0 protection off。Fingerprint token budget $K=32$,在三個 view group(front/side/rear)上獨立計算。
- **Batch size / optimizer / learning rate / training steps**: the paper does not specify(method 為 training-free,inference batch size 同樣未明確標註)。
- **Comparison baseline**: 同模型的 no-cache full-compute run,使用相同 seed、conditioning 與 KV state,確保差異僅來自 DiT 端。

### 6.4 Main Results

| Method | 7-cam PSNR (dB) ↑ | SSIM ↑ | LPIPS ↓ | Skip (%) | DiT (s) | Speedup |
|---|---|---|---|---|---|---|
| Baseline full-compute (Urban Street) | — (reference) | — | — | — | 3.682 | 1.00× |
| Baseline full-compute (Highway) | — (reference) | — | — | — | 3.633 | 1.00× |
| Baseline full-compute (U-turn) | — (reference) | — | — | — | 3.688 | 1.00× |
| **X-Cache (Urban Street, n=7)** | **51.37** | **0.9990** | **3.3e-4** | **71.4** | **1.392** | **2.65×** |
| **X-Cache (Highway, n=3)** | **54.67** | **0.9991** | **1.9e-4** | **71.6** | **1.365** | **2.66×** |
| **X-Cache (U-turn, n=3)** | **52.04** | **0.9990** | **3.1e-4** | **71.3** | **1.364** | **2.70×** |

備註:7-cam 列為 stitched seven-view 圖上計算,並非 per-camera 數值的算術平均;Skip rate 排除 warmup,DiT wall-clock 排除每個 rollout 的第一個 chunk。論文第 2 頁明確指出 X-Cache 操作於 cross-chunk 軸,而既有 cache 方法皆為 cross-step 且僅在 many-step、one-shot 設定下評估,因此**未提供與其他 caching 方法的 head-to-head 對照**(只報告對 no-cache baseline 的絕對加速)。

### 6.5 Ablation Studies

所有 ablation 在同一條 264-frame highway held-out clip 上進行,每次只動一個旋鈕(Table 3)。Default 行為 PSNR 53.384 dB / SSIM 0.9990 / LPIPS 2.0e-4 / skip 71.3% / 1.406 s / 2.59×。

- **Step-0 protection (off → on)**: skip rate 從 71.3% → 53.5%,DiT 時間 1.41 s → 1.98 s(2.59× → 1.84×),但 PSNR/SSIM/LPIPS 在所示精度下不變。診斷意義明確 — 量化 step-0 保護的「成本」,並指出在當前 workload 下 cosine gate 已足以攔下會出問題的 step-0 reuse;論文仍保留為 distribution-shift 保險。屬於**有診斷價值的 ablation**。
- **KV-update-chunk protection (on → off)**: PSNR 暴跌至 21.461 dB,SSIM 0.8067,LPIPS 1.77e-1(三個數量級惡化),skip rate 僅多 9 個百分點,speedup 反而從 2.59× 下降到 2.18×。這是論文中**唯一造成嚴重品質崩潰**的 ablation,直接論證了 §2.5 將 KV update chunk 視為 hard safety requirement 的核心宣稱。屬於**強診斷實驗**。
- **Front anchor $F_n$ (1 → 0)**: skip rate +1.9 pp、DiT 省約 70 ms,PSNR 反而略升至 53.622 dB。論文承認當前 clip 並未強烈暴露 block-0 在 KV-update cycle 被跳過的失敗模式,默認仍保留 $F_n=1$ 作為對罕見場景的保險。**部分屬於 sanity check** — 量級小、且 paper 自己指出當前資料無法觸發其想保護的失敗模式。
- **Adaptive-threshold floor $\tau_{\text{floor}} \in \{0.90, \dots, 0.96\}$**: 所有指標在所示精度下不變(PSNR 53.37–53.40 dB,DiT 1.96–1.98 s)。論文坦承在當前 workload 下 floor 實際上 inactive(EMA-minus-margin 主導),只證明對此參數不敏感、無法證明在分佈外仍如此。**接近 sanity check** — sweep 範圍未觸及 floor 真正會 binding 的區段(< 0.94),也未在 distribution-shifted 資料上重複,因此沒有真正回答「floor 為何值得保留」。

整體而言,KV-update protection 的 ablation 是真正的診斷實驗;step-0 protection 屬於有意義的權衡量化;$F_n$ 與 $\tau_{\text{floor}}$ 兩個 sweep 的「無變化」結果在當前測試集上偏向 sanity check,作者亦明確承認這點(§4.4)。

### 6.6 Phyra Experiment Assessment

- [missing] Has at least one strong baseline (a current SoTA on the chosen task) — 唯一 baseline 是同模型的 no-cache full-compute;論文於 §1 明確主張 FlowCache、SCOPE、DeepCache、δ-DiT、BWCache、WorldCache 等 cross-step caching 方法「not applicable」於 few-step interactive AR 設定,因此未跑任何競爭基線。
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — 僅在 X-World 一個 world model 與單一內部資料分佈上評估,但切成 urban / highway / u-turn 三個 scenario subset(共 13 clips)以涵蓋不同運動強度;未跨資料集或跨任務。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — KV-update protection 與 step-0 protection 為真正的診斷實驗;$F_n$ 與 $\tau_{\text{floor}}$ sweep 在當前 workload 上趨近 no-op,paper 自己承認(§4.4)無法在現有資料上真正壓力測試。fingerprint 子採樣設計、auxiliary global / action channel、dual-metric vs. 單一 cosine、EMA margin $m$、view-group 聚合等元件均**未做 ablation**。
- [missing] Has a scaling study (size, length, or compute) — 全部 rollout 固定為 264 frames / ≈22 秒,未測試更長 horizon、不同 chunk 大小、不同去噪步數 $S$、不同 DiT block 數 $B$ 或多 PPU 規模。§5 limitations 明確列為未做。
- [covered] Has an efficiency / wall-clock comparison — Table 2 報 per-chunk DiT 秒數與相對 no-cache 的 speedup(2.65–2.70×);Table 3 在 ablation 中亦逐項列 DiT 時間與 speedup。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — Table 2 雖標註 $n=7$ / $n=3$,但僅報均值,未提供 std、CI 或多 seed 重跑;Figure 4 為單 representative session 的逐幀曲線。
- [missing] Releases code / weights / data sufficient for reproducibility — 內文只提供專案頁 https://x-cache-1.github.io/,未承諾釋出 X-Cache 程式碼、X-World 權重或測試 split;測試資料為 internal held-out split,reference baseline 模型亦為 production 模型。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Cross-chunk block caching 作為新軸(§1 contribution 1)**:支持。Table 2 在三類場景達成 71% skip 與 2.6–2.7× 加速,Fig. 5 跨場景 cosine heatmap 形狀近乎一致,皆證實 cross-chunk 軸真實存在且穩定。
- **Structure-aware + action-aware fingerprint(§1 contribution 2)**:部分支持。整體 fingerprint 在主結果中可運作,但 3D-grid vs 1D-flat、global channel、action channel 三項設計皆無 leave-one-out ablation,因此「structure-aware」與「action-aware」各自的邊際貢獻無法量化。
- **KV update frame protection(§1 contribution 3)**:強支持。Table 3 的單因子 ablation 顯示移除此保護會讓 PSNR 從 53.4 dB 崩潰到 21.5 dB、LPIPS 上升三個量級,這是全文最確鑿的因果證據。
- **Adaptive per-position thresholding(§1 contribution 4)**:部分過度宣稱。§4.4 的 $\tau_\mathrm{floor}$ 掃描證明 floor 在現工作量上完全不啟動,而「per-(t,b) EMA 取代單一全域閾值」並未直接 ablation(沒有與 single global threshold 對照),因此 adaptivity 帶來的好處只能間接推論。
- **在 production driving world model 上驗證(§1 contribution 5)**:支持但範圍有限。X-world 的 4-step、rolling KV cache、7-camera causal DiT 確實是 production 設定,但驗證資料是 13 段 in-distribution clip、總長約 286 秒,沒有 long-horizon 或 OOD 測試,「production validation」的廣度與真實部署存在落差。

### 7.2 Fundamental Limitations of the Method

**0.75 結構天花板**:在 $W=1$ warmup、4-chunk 重用視窗、front anchor $F_n=1$、KV-update force-compute 的預設下,可被 skip 的 block 比例的理論上限就是 Fig. 6 標示的 0.75 平台。論文的頭條 71% 已經緊貼此線,意味著 gate 多數時候運作在「結構性允許的最大 skip」處,而非由資料相似度動態決定。要再往上推不是調 threshold 的問題,而要重新設計 warmup 與保護結構,這超出當前方法定義。

**Cross-chunk 冗餘的場景依賴性**:整個方法的存在依據是「物理場景在相鄰 chunk 間平滑演化」。在 cut-in、突發煞車、場景切換、隧道進出、天氣突變等情境,fingerprint 的 cosine 必然下降,gate 會 fallback 為 full compute,加速優勢直接歸零。這是 cross-chunk 軸本身的結構性限制,而非實作問題。

**Reference-only fidelity 評估**:所有 PSNR / SSIM / LPIPS 均以 full-compute baseline 為參考,衡量的是「X-Cache 對自家無快取版本的還原度」。若 baseline 本身在某個 chunk 偏離 ground truth,X-Cache 沿同方向放大誤差時,當前指標無法偵測。要解決必須引入相對 ground-truth 的視訊指標(如 FVD、人類評估),不是參數調整能修復。

**KV-update chunk 的二元保護是硬約束**:Table 3 顯示在 KV update chunk 上允許 skip 會讓 PSNR 落差超過 30 dB。這意味著每個 KV update cycle 至少有一個 generation step 必須 100% 計算,直接替整體可達加速設下另一道天花板,且論文沒有探索 partial KV recompute、cached/clean 加權混合等中間態,意味著「降低 KV-update 成本」目前在此方法框架內是封閉的。

### 7.3 Citations Worth Tracking

- **[2] Block Cascading**:X-Cache 主動排除的 sequence-level parallelization 路線。理解它有助於評估「若 closed-loop 限制鬆綁(可容忍 action latency)」時 X-Cache 的相對位置,以及兩者是否可串接。
- **[13] FlowCache**:被作者指認為「同樣建立在 cross-step 假設之上」的最直接競品。值得追讀以判斷在 4-step regime 下,cross-step + cross-chunk 是否真的互斥,還是可以疊加。
- **[7] WorldCache**:同樣聚焦 world model token caching、且發表於同窗口的 sibling work,fingerprint-based gating 思路可能高度重疊,直接對照可看出 X-Cache 設計選擇的相對優劣。
- **[21] X-world**:X-Cache 的 base model。要判斷 X-Cache 的可遷移性必須先了解 X-world 的 multi-camera causal DiT、action conditioning、rolling KV cache 細節,因為許多保護機制(KV update、anchor block)都是針對其結構設計。
- **[9] Self Forcing**:提供 few-step AR video diffusion 的 distillation 框架,定義了 X-Cache 鎖定的「4-step 互動式」regime 從何而來,理解此文才能評估「few-step 蒸餾消滅 cross-step 冗餘」這條前提的普適性。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] EMA-based adaptive threshold 在分佈漂移(進入隧道、突降大雨、夜間切換)時的行為為何?$\bar{s}_{t,b}$ 的 lag 與 $\alpha=0.3$ 的反應速度是否會在過渡期讓 gate 過度自信?
- [ ] Cross-chunk(X-Cache)能否與 cross-step(FlowCache、SCOPE 風格)caching 組合,在兩條 gate 同時通過時取得加成 skip,還是兩者在 4-step regime 下會互相破壞品質?
- [ ] gate 本身(fingerprint + 兩個指標 + EMA 更新 + cache 管理)在每個 $(t,b)$ cell 的真實 overhead 是多少?DiT wall-clock 加速 2.6× 中,有多少被 gate 自身吃回去?
- [ ] 在場景連續性被打破的情境(cut-in、變道對抗、scene cut、緊急煞車)X-Cache 是否會優雅降級為近 full compute,還是會在 fallback 之前先輸出一段品質惡化的影像?
- [ ] 側面攝影機 PSNR 系統性低 2–6 dB,是否與 fingerprint 共用 view-group 有關?改用 per-camera fingerprint 是否能縮小差距,代價如何?
- [ ] 0.75 平台是 cross-chunk 軸的本質上限,還是只是 $W=1$ + 4-chunk reuse window 的人工結果?在 $W=0$ 或更大 reuse window 下,真正的天花板在哪?
- [ ] 將 X-Cache 應用到 WorldPlay、MAGI-1 等 action transition 更突兀的 AR 世界模型時,EMA 門檻是否需要重訓?fingerprint 設計是否需要修改 action channel 的權重?

### 8.2 Improvement Directions

1. **Hybrid cross-chunk + cross-step gating**(可行性高):在 cosine + deviation gate 之外再串一道 cross-step 相似度判斷,只在兩軸皆通過時 skip。理論依據是兩條冗餘軸來源獨立(物理連續性 vs 去噪軌跡鄰近性),即便 4-step 下 cross-step 訊號弱,聯合判斷仍可在 0.75 平台之上撿到少量 skip,且不違反當前的安全機制。
2. **Per-view-group / per-camera 自適應門檻**(可行性高):現行 $\tau_\mathrm{cos}(t,b)$ 對所有 view group 共用,而側面攝影機 PSNR 一致較低。改為 $\tau_\mathrm{cos}(t,b,g)$ 並讓 EMA 在 group 層級獨立追蹤,可在不犧牲總 skip rate 的情況下提高側面視角品質。依據是 Table 2 顯示的 2–6 dB 系統差距與 fingerprint 的 group-stacked 結構。
3. **Soft KV-update protection**(可行性中):Table 3 顯示 KV-update chunk 二元保護的 32 dB 落差暗示 binary on/off 過於粗。可嘗試 partial KV recompute(只重算 K 不重算 V,或反之)、或將 cached 與 clean KV 以權重混合,觀察能否在保留多數 skip 的同時控制誤差累積。基礎是 KV update 寫入持久 cache,寫入精度可能比即時計算精度更重要。
4. **Reuse window 與 staleness 上限的聯合掃描**(可行性中):當前 $M$ 計數器預設關閉、reuse window 隱含為 1 chunk。同時打開 $M$ 並擴大 reuse window 至 2–3 chunks,可區分 0.75 平台到底是設計選擇還是資料極限。物理連續性是多 chunk 性質,不應僅止於相鄰 chunk。
5. **Fingerprint geometry 的直接 ablation**(可行性高、貢獻偏實證):比較 3D 網格採樣 vs 1D linspace vs 隨機採樣 vs full-input 的品質-overhead 曲線,並逐一移除 global / action channel。這填補論文 §1 contribution 2 缺失的因果證據,且實作成本低。
6. **Ground-truth 端的 fidelity 量測**(可行性中):在現有 PSNR vs baseline 之外,加入相對 ground-truth video 的 FVD 或人類評估,並交叉比較「X-Cache vs GT」與「baseline vs GT」的差距。這是 §4.2.2 第 1 點的根本解,讓品質聲明不再是自我參照。
