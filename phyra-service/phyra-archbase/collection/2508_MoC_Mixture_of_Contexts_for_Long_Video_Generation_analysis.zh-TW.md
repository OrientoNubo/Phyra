<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# MoC — Mixture of Contexts for Long Video Generation

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | MoC |
| Paper full title | Mixture of Contexts for Long Video Generation |
| arXiv ID | 2508.21058 |
| Release date | 2025-12-09 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2508.21058 |
| PDF link | https://arxiv.org/pdf/2508.21058 |
| Code link | — |
| Project page | https://primecai.github.io/moc/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|------|------|------|------|
| Shengqu Cai | Stanford University (work done at ByteDance Seed) | https://primecai.github.io/ | first author |
| Ceyuan Yang | ByteDance Seed | https://ceyuan.me/ | corresponding author |
| Lvmin Zhang | Stanford University | — | co-author |
| Yuwei Guo | CUHK | — | co-author |
| Junfei Xiao | Johns Hopkins University | — | co-author |
| Ziyan Yang | ByteDance Seed | — | co-author |
| Yinghao Xu | Stanford University | — | co-author |
| Zhenheng Yang | ByteDance | — | co-author |
| Alan Yuille | Johns Hopkins University | — | co-author |
| Leonidas Guibas | Stanford University | — | co-author |
| Maneesh Agrawala | Stanford University | — | co-author |
| Lu Jiang | ByteDance Seed | — | corresponding author |
| Gordon Wetzstein | Stanford University | — | senior author |

### 1.2 Keywords

long video generation, diffusion transformer, sparse attention, mixture of contexts, in-context retrieval, top-k routing, causal routing, content-aligned chunking

### 1.3 Related Lineage

| Key | Relation | Brief |
|------|------|------|
| LCT (Long-Context Tuning) | predecessor | Most closely related: expands single-shot DiT to ~8-shot scenes via dense interleaved 3D RoPE attention; MoC removes its quadratic cost. |
| FramePack | baseline | Compresses arbitrarily many frames into a fixed vector for next-frame prediction; example of lossy context compression MoC argues against. |
| MoBA (Mixture of Block Attention) | influence | LLM block-routing inspiration; MoC adapts the idea to multi-modal video with content-aligned chunking. |
| Radial Attention | baseline | Static $O(n \log n)$ sparsity mask from spatiotemporal energy decay; contrasts with MoC's learned dynamic routing. |
| VMoBA | concurrent | Trainable mixture-of-block scheme with layer-wise partitions and global/threshold block selection for VDMs. |
| VSA | concurrent | Hardware-efficient coarse-to-fine sparse kernel replacing full attention at training and inference. |
| Diffusion Forcing / RollingDiffusion | influence | Inject noise into historical context to combat error accumulation in long autoregressive generation. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於「長片段影片生成」(long-context video generation),核心議題是如何讓 Diffusion Transformer (DiT) 在分鐘級長度下仍能保留並回憶起跨鏡頭的人物身份、動作與場景佈局,而不會產生漂移或崩壞。作者將長影片生成重新表述為「模型內部的資訊檢索」問題,並提出 Mixture of Contexts (MoC):一個可學習、稀疏化的注意力路由模組,用以替代密集自注意力,克服其 $O(L^2)$ 的計算瓶頸。研究範圍涵蓋多模態 token 流(影格、鏡頭、字幕)、內容對齊的 chunking 策略、top-k 動態路由、強制錨點 (caption / intra-shot 區窗) 與因果遮罩,目標是在近線性成本下達到分鐘級記憶與一致性,同時不需修改 DiT 主幹或訓練流程。

### 2.2 Domain Tags

- video generation
- diffusion models
- efficient attention
- long-context modeling

### 2.3 Core Architectures Used

- **Mixture of Contexts (MoC)**:本論文提出的核心模組,以 mean-pooled chunk 描述子計算 query–chunk 相關性並執行 top-k 動態路由,取代 DiT 中的密集自注意力,負責將計算預算分配給真正攸關的歷史片段。
- **Diffusion Transformer (DiT) / MMDiT**:作為被改造的主幹網路,提供原本的 $Q, K, V$ 投影與 patch embedding;MoC 直接替換其 self-attention 層,不修改其餘訓練流程。
- **LCT (Long-Context Tuning)**:作為初始化權重與基線架構,提供 8-shot 場景級長窗 DiT 與 interleaved 3D RoPE 設定,MoC 在其上微調以驗證稀疏路由的效益。
- **Flash-Attention (var-len kernel)**:作為高吞吐的底層注意力核心,負責在內容對齊、長度不一的 chunk 上實際執行被路由後的稀疏注意力計算。
- **3D RoPE**:作為位置編碼,給予影格、鏡頭、字幕 token 各自的 3D 座標,使 MoC 的內容對齊 chunking 能與時空幾何結構一致。
- **Mixture-of-Experts 風格的硬路由**:作為設計類比,啟發了 MoC 的 context drop-off / drop-in 與 per-head 分布式路由,以避免 dead-route 並擴大全域涵蓋。

### 2.4 Core Argument

作者主張長影片生成的本質困難並非僅是算力不足,而是「記憶與選擇」問題:模型必須在漫長時間軸上挑出當下真正相關的歷史片段,並避免被冗餘或無關內容稀釋。現有路線都不夠理想——壓縮式方法 (keyframes、FramePack、TTTVideo) 把歷史塞進固定大小的潛在向量,無法回放細節;靜態稀疏或固定樣式 (Radial Attention、SparseVideoGen 等) 預先寫死哪些 token 對該互動,無法依內容自適應;LCT 則保留密集注意力,直接承受二次方成本。作者由此推論:解法必須同時具備 (1) 內容自適應的動態選擇、(2) 與影片自然邊界對齊的 chunk 切割、(3) 因果結構以避免「迴圈閉合」造成的反饋陷阱、(4) 強制的跨模態與區域錨點以穩定局部保真度。MoC 把每個 query 視為一個檢索器,以 mean-pooled chunk 描述子計算相關性,選 top-k 並透過 attention 端到端反傳梯度,因此即使 router 本身無參數,query/key 投影仍會被塑形以放大判別性相似度。配合 context drop-off / drop-in 防止「死路由」、per-head 分布式路由擴大全域涵蓋、內容對齊 chunking 維持語意同質,以及因果遮罩消除雙向迴路,作者認為這套設計是讓稀疏路由「不只是加速器、而是真正的長期記憶引擎」的最小必要條件,因此能在 ≈180k tokens 的分鐘級場景上同時取得 7× 注意力 FLOPs 削減、2.2× 端到端加速,並維持甚至超越密集基線的一致性與保真度。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「Mixture of Contexts for Long Video Generation」直接點出論文的核心提案：把長影片生成的注意力機制重塑為一種「上下文混合」(MoC) 的路由問題。Abstract 的論述順序非常工整：先把 long-context video generation 重新定義為 *memory problem*，主張模型必須跨長時域保留並檢索 salient events 而不能漂移或塌陷；再指出 scaling diffusion transformers (DiTs) 的根本瓶頸是 self-attention 的 quadratic cost，導致 memory 與 compute 都難以負擔且不易最佳化。

接著作者提出概念上的 reframing：把長影片生成視為 *internal information retrieval*，並引入一個 simple、learnable、sparse attention routing module — Mixture of Contexts (MoC) — 作為長期記憶檢索引擎。每個 query 動態挑選少量 informative chunks，再加上 mandatory anchors（caption、local windows）與 *causal routing*（避免 loop closures）。

最後 abstract 把貢獻收斂為一個 scaling 故事：隨著資料規模擴大並 *gradually sparsify* routing，模型自然把運算配置給 salient history，跨數分鐘維持 identities、actions、scenes 的一致性。Efficiency 是 retrieval 的副產物（near-linear scaling），讓 minute-scale training/inference 變得實際可行，並讓 memory/consistency 在分鐘尺度上 *emergent* 浮現。Abstract 透過「memory → quadratic bottleneck → retrieval reframing → MoC → emergent consistency」這條線，為後續章節奠定整體敘事框架。

### 3.2 Introduction

(560 words)

Introduction 以三層遞進建立問題意識。首先把 video generation 放進更大的脈絡 — content creation、autonomous simulation、interactive storytelling — 並指出 Transformer-based diffusion 雖能合成日益逼真的短片，但要推到 minute 或 hour 級就暴露 *long-term memory* 這個更深層的挑戰：模型必須在長時間軸上保留並檢索 salient events，而不漂移、不塌陷、不丟身份。作者點出兩個糾纏的瓶頸：dense self-attention 的 computational cost 在序列變長時不可承受；更關鍵的是 *learning to selectively recall the right context at the right time*，這已經不只是算力問題，而是學習問題。

第二層分析既有解法的根本侷限。作者強調 video data 的高度 *temporal redundancy*（相鄰 frame 像素相似、運動微小），於是先前工作走兩條路：把歷史壓縮成 compact representation（keyframes、frame packs、latent states），或是強加 fixed sparse / selective patterns 來稀疏化跨序列互動。兩者都「hard-code 一個 efficiency 與 fidelity 之間的妥協」：壓縮摘要會丟細節；static sparsity 或固定 selection 無法依「哪段過去 *此刻* 才重要」自適應，從而限制 long-range dependencies 與 narrative coherence 的保留能力。這段分析直接為「需要一個 *learnable*、*adaptive* 的 routing」鋪好動機。

第三層提出方法的概念框架。作者把 long-context video generation 重新表述為 *internal information retrieval*：每個 token 透過 learnable sparse attention routing 動態存取最相關的 context。具體實作分四點：(1) MoC 把 multi-modal token stream 沿著 frames、shots、captions 切成 *content-aligned chunks*；(2) 每個 query 透過 *parameter-free yet trainable top-k router* 只挑少數相關 chunks；(3) 強制激活兩個 mandatory anchors — cross-modal links 接所有 text tokens、intra-shot local window links — 以穩固 local fidelity 並把 routing capacity 留給真正的 long-range recall；(4) 加上 *causal routing mask* 阻止 pathological loop closures，把互動圖約束為 DAG，提升 minute-scale roll-out 的穩定性。實作上 selected key tokens 直接餵進 flash-attention kernel；訓練時 chunk 粒度與 routing 選擇性 *progressively* 變細，形成 gradual sparsification。

最後 Introduction 給出一個強烈的收束式 claim：以 MoC 取代 dense self-attention 等於把 long-video generation 變成 *internal in-context retrieval*；learned sparse routing 在不改 diffusion backbone、不改 training recipe 的前提下，把 compute 配置給 salient history，跨 minutes 維持 cross-shot identities、actions、layouts。Efficiency 只是副產物：MoC 修剪超過 85% 的 token pairs、削減 attention FLOPs 至多 7×，在約 180k token 的 minute-scale 場景帶來 2.2× 端到端加速。作者把這段主張定位為「第一個示範 learned sparse context routing 能突破 quadratic attention 實務障礙」的工作，自然銜接到後續的 Related Work 與 Method 章節。

### 3.3 Related Work / Preliminaries

(720 words)

Related Work 由一段 framing 起手：標準 self-attention 在 Transformer 上具 $O(L^2)$ 成本，是把架構推到 video 級長序列時的首要障礙；同時還有跨長時域維持 coherence、避免 visual degradation 的難題。作者用這段為三個子題鋪路 — Long Video Generation、Sparse Attention for Video Generation、Context Learning in Visual Generation — 每段都以「過往做法 → 侷限 → 自家方法的差異化定位」三段式論述。

第一段 *Long Video Generation* 指出多數既有 video generation 模型只能處理數秒。為了延長 horizon，先前工作分為幾條路線：TECO 用 recurrent state 的 temporally consistent transformer、NUWA-XL 用 diffusion-over-diffusion 階層先生 sparse keyframes 再遞迴內插；MALT、CausVid 等 autoregressive 框架在 frame/chunk/segment 層級延長生成，但飽受 *error accumulation* 之苦；RollingDiffusion、Diffusion Forcing 用「對歷史 context 注入受控噪聲再 denoise」緩解 compounding errors；MAGI-1、SkyReels-V2 把這套放大成 autoregressive denoising。一條 orthogonal 路線是把整段過去蒸餾成定長 latent — TTTVideo、LaCT 用可學 MLP 編碼 context、FramePack 用固定向量編碼任意多 frame 並做 next-frame 預測，並利用 keyframe / anchor frame 預先規劃。作者強調這些方法把生成推到一分鐘量級，但仍受限於對 context 的 lossy compression。最後鎖定最相近的工作 *LCT*：把 single-shot DiT 擴到最多 8 shots（≈8s、≈$2.3\times10^4$ tokens / shot），用 interleaved 3D RoPE，但仍維持 dense attention，FLOPs 與 memory 隨 $(8L_{\text{shot}})^2$ 增長。這段直接指出 LCT 的 quadratic ceiling，為 MoC 的差異化提供入口。

第二段 *Sparse Attention for Video Generation* 利用「attention matrix 多為稀疏」這一觀察來分類既有工作。Training-free pruners 包括 SparseVideoGen（profile head 在 spatial vs. temporal 的特化）、STA（tile-by-tile 利用 3D window 的 FlashAttention 友善 block）；通用過濾器 SpargeAttn / SageAttention 結合 token compression 與 softmax-aware 跳過；AdaSpa 用 blockified dynamic pattern 與 Fused LSE-Cached Search 跨 denoising step 重用 sparse indices；Jenga 做 training-free block-wise carving 加 progressive resolution。Trainable / structured 設計則有 VMoBA（learn 一個 mixture-of-block + global / thresholded 區塊選取）、VSA（hardware-efficient coarse-to-fine kernel，訓練與推論皆替代 full attention）、Radial Attention（從 spatiotemporal energy decay 推得 $O(n\log n)$ static mask）。作者收束指出這些工作「要嘛 prune 已產生的 dense map，要嘛強加固定 sparsity prior」，且重心多在 *加速短影片*；自家 MoC 則做 *deliberate, end-to-end routing of context sources*，焦點在 long-context memory / consistency，加速只是 sparsity 的副產物。

第三段 *Context Learning in Visual Generation* 把 context 視為一級信號：World model 路線中 WORLDMEM 用外掛 frame/state memory bank、依 FoV overlap 檢索；Context-as-Memory 顯式檢索少量歷史 frame；VMem 用 surfel-indexed、occlusion-aware memory 在 re-visit 時取出相關 view。Image side 則有 IC-LoRA 顯示 DiT 已有 in-context 能力、DSD 用 self-distillation 把 in-context generation 變成 paired 監督、OmniControl 提供 parameter-efficient image-conditioned control、FLUX-Context 把文圖串接做 in-context 編輯。作者結論這些工作共同顯示：在足夠規模下，*routing 與 in-context learning 都是強有力的 context 利用機制*。MoC 順著這條路線推進，主張在多個 context source 上 *end-to-end 學會路由*，做 deliberate selection 與 composition，而非依賴固定 retrieval 或單一 conditioning pathway。這段把全章收斂到 MoC 的方法立論：retrieval = 學習而來的 sparse routing，自然銜接到後續 Method 章節。

### 3.4 Method (overview narrative)

(330 words)

Method 章節以一段 high-level overview 把整個 MoC 的設計收束成三個共同運作的原則：(i) routes each query only to the most relevant chunks of context；(ii) aligns those chunks with natural video boundaries — frames、shots、caption tokens；(iii) enforces causality 讓資訊嚴格沿時間正向流動。作者明確表示要把 DiT backbone 的 dense attention 替換成 adaptive、content-aligned 的 MoC layer，目的是繞過 self-attention 的 quadratic 成本，但 *不更動 backbone 或訓練配方*。整體 pipeline 由 Fig. 1 視覺化呈現，章節再分為三節推進論述。

第一節 *Mixture of Contexts*（§3.1）定位為方法的數學核心：先重訪 DiT 的 vanilla attention，再導入 *Dynamic Routing via Top-k Selection*，把 query 對 chunk 的選擇形式化為一個 parameter-free 的 top-k operator。其中 chunk 的描述子採用 mean pooling，並用 DDAE 的 self-supervised 觀察論證該描述子已能捕捉 dominant semantics。為了避免 dead expert / dead route 等 MoE 常見病症，作者引入 *Context Drop-off* 與 *Context Drop-in* 兩個 stochastic 正則化。最後以 *Per-Head Distributed Routing* 強調 routing 是逐 head、逐 layer 獨立進行，形成 $L_{\text{layers}} \times H_{\text{heads}}$ 個獨立 router 的 ensemble，避免 global routing 的資訊瓶頸。

第二節 *Attention Chunking and Routing*（§3.2）轉到 *如何切 chunk* 與 *哪些連結必須強制保留*。作者主張採 content-aligned chunking，沿 frames、shots、modality 邊界切分，避免 uniform window 把 mean-pooled key 污染。再導入兩個 mandatory anchor：*Fixed Cross-Modal Selection* 把所有 text tokens 視為 attention sink，提供低熵語意錨點與全局梯度高速公路；*Fixed Intra-Shot Selection* 強制 intra-shot 連結，把 sparse budget 留給真正的 long-range 依賴。最後 *Causality in sparse MoC* 引入 causal mask，把 routing graph 約束成 DAG，根除 ablation 中觀察到的 two-node feedback loop。

第三節 *Computation Efficiency*（§3.3）轉向 *實作層面*：以 torch.bucketize、prefix-sum、segment_reduce、head-major rearrange 等手法把 content-aligned 的 variable-length chunks 餵進單次 Flash-Attention var-len call，並推導 FLOPs：$\text{FLOPs}_{\text{MoC}} \approx Ld + 2LCd + 4Lk\bar{m}d$ 對比 dense 的 $4L^2d$，比值隨序列長度線性增長，為後續 Experiments 的 7× FLOPs 削減與 2.2× 加速提供理論基礎。

### 3.5 Experiments (overview narrative)

(340 words)

Experiments 章節聚焦於主實驗：long scene-level text-to-video generation with multiple shot cuts，這被定位為 AIGC video generation 的關鍵 use case。作者先說明 *Base model* 設定：採 LCT — 唯一支援長、多 shot、通用場景生成的架構 — 作為起點。LCT 是一個 3B 參數 MMDiT，從 image / single-shot / multi-shot videos 混合訓練，full self-attention 已被擴張到 scene-level context window（最多 8 shots、約 8 秒、每 shot 約 22k tokens），並用 interleaved 3D RoPE 給每個 shot 獨立絕對座標。作者直接從 pretrained LCT 初始化權重，*只把 attention module 換成 MoC*，再以與 LCT 相同的訓練流程做 fine-tune，藉此把實驗對比鎖定在 attention 機制本身的差異。

*Baselines* 設定為 LCT 的 dense attention 版；測試在 8-shot 序列上，每個 shot 為 8 秒、480p、12 FPS，整段 64 秒場景約 180k tokens。*Evaluation Metrics* 採用 VBench：以 Subject Consistency、Background Consistency 衡量主體與背景的長期保留；Motion Smoothness、Dynamic Degree 評估運動的流暢度與幅度；Aesthetic Quality、Image Quality 量測視覺品質；同時匯報 sparsity、FLOPs、相對於 Flash Attention 的 inference speedup 等運算指標。

*Quantitative Results*（Tab. 1）說明 MoC 在丟棄 85% context 的條件下仍取得 2.2× 加速，並在多數 VBench 指標上略勝 LCT；最顯著的提升出現在 motion diversity（Dynamic-Degree 從 0.46 升至 0.56），同時 Motion-Smoothness 不退化。作者把這詮釋為「learned, structure-aware sparsity 把運算從 redundant frames 重新配置給 salient visual events」。

*Qualitative Results*（Fig. 3）論證 mean-pooled descriptor 在影片場景中的合理性：相鄰 patch 與 frame 在 patch embedding 後位於極窄子空間，first principal component 常解釋 >90% 局部變異，而算術平均正是該 component 的估計子。這也說明 dot-product + mean-pool 雖看似簡單，卻因 query / key projection 仍隨訓練更新而具備高表達力。

*Qualitative Illustration of Coherence*（Fig. 4）進一步以五個 row 的視覺案例 — cityscape geometry、sketchbook → 實體建築、neon signage 對切、電腦側面 vent 與螢幕細節、車內多人物 identity — 證明 MoC 能跨數百乃至數千 frame 檢索 small details 與抽象語意。整章把「sparsify 卻不犧牲 fidelity」這個主軸用量化、定性與長期一致性三層視角共同論證，自然銜接到 Conclusion。

### 3.6 Conclusion / Limitations / Future Work

(290 words)

Conclusion 把全篇收束在一個強敘事 claim：Adaptive Mixture of Contexts (MoC) 證明 *learnable sparse attention routing* 可以扮演一個強而 data-driven 的 *memory retrieval engine*。作者把自家工作定位為「arguably the first」展示在訓練資料 scaling 條件下，搭配一個 efficient、learnable 的 sparse routing 機制，模型能夠 *develop* 出一套 sophisticated 的 long-term recall 方法，把 minute-scale memory 推到接近短影片生成的成本。作者強調 *critically*，這項能力 emerges *沒有* 顯式的 3D priors 或 Field-of-View 啟發式 — 哪段歷史 context 是 salient 完全由模型 from data 學到。因為 routing 是學出來的、推論時 implementation fast，MoC 被定位為下一代 *scalable、controllable、responsible* long-video generative models 的 blueprint，並把「移除 quadratic attention bottleneck」從單純的 efficiency gain 提升為「直接通往 emergent long-term memory」的方法論主張。

*Limitation and Future Work* 段落保持誠懇的範圍說明。作者指出目前的訓練與測試設定完全 *沿用 LCT 的設定*；MoC 在更長序列上節省運算的潛力 *尚未* 被探索。雖然方法已能在分鐘級 context 上達到接近短影片的成本，但目前的 runtime 仍依賴 *general-purpose variable-length attention* 與 framework-level gathers — 在已實現 7× FLOPs 削減的基礎上，仍有明顯加速空間。

作者列出具體的 future direction，全部指向 hardware–software co-design：block-sparse、chunk-aware variable-length attention、更高效的 customized CUDA / Triton kernels、fused routing+attention operators、persistent execution、改進的 K/V layout 或 quantization。這段同時承認當前實作的工程限制（短序列下 index gather 與 pooling overhead 反而抵銷加速，如附錄 §E 所示），也為後續工作預留明確方向，使 Conclusion 在敘事上既收束又開放，與全文「retrieval-as-attention 是 scalable long-video memory 的方法論主軸」這條主線保持一致。

## 4. Critical Profile

### 4.1 Highlights

- 將長片段影片生成重新表述為「模型內部資訊檢索」問題,並以可學習、無參數的 top-k chunk router 取代密集自注意力,這是論文最具概念張力的重構 (§3.1, p.4)。
- 在 ≈180k tokens、約 64 秒的 8-shot 場景上,以 85% sparsity 達到 attention FLOPs 削減 >7× 與端到端加速 2.2× (Tab.1, p.8)。
- 在 VBench 上 Dynamic-Degree 由 LCT baseline 的 0.4583 提升到 0.5625、Motion-Smoothness 維持在 0.9920,顯示稀疏化並未犧牲動態品質 (Tab.1)。
- Content-aligned chunking 沿著 frame、shot、modality 自然邊界切割 token stream,使 mean-pooled key 保持語意同質,避免 uniform window 在跨 shot cut 處的污染 (§3.2, p.6)。
- 強制的跨模態鏈接 (text tokens 佔 <1% tokens) 與 intra-shot 區窗扮演 attention sink,提供穩定的局部保真度與 well-conditioned 的 attention block (§3.2, p.6–7)。
- Causal routing mask 將 routing graph 約束為 DAG,Fig.2 顯示去除後會出現 shot 9 與 shot 11 互相 routing 的兩節點封閉迴路 (p.5)。
- Per-head distributed routing 把選擇下放至每個 head,形成 $L_{\text{layers}} \times H_{\text{heads}}$ 的獨立 router 集合,使聯集涵蓋遠大於單一 head 的 $k$ 個 chunk (§3.1, p.6)。
- Zero-shot 將 MoC kernel 直接套用到凍結權重的預訓練 DiT,在 >75% sparsity 下仍能保留主體身份與背景佈局 (Fig.6, Appendix D)。
- 在 Wan-2.1-1.3B (非 MMDiT 架構) 上以 81% sparsity 達到與 dense baseline 相當或更佳的 VBench 表現,初步驗證跨 backbone 的泛化性 (Tab.5, Appendix H)。
- 工程實作上使用 `torch.segment_reduce` on-the-fly pooling 加上 head-major 排列的 Flash-Attention var-len 呼叫,使 routing meta-data 的記憶體開銷低於總 GPU 預算的 0.1% (Appendix A、B)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 訓練與評估皆鎖定 LCT 的相同設定 (8-shot, 180k tokens),作者明確表示「ability of MoC to save computation on even longer sequences is yet to be explored」(p.10, Limitation and Future Work)。
- Runtime 仰賴通用 variable-length attention 與 framework-level gathers,作者承認 7× FLOPs 削減未完全轉換為等比例 wall-clock 加速,需要 hardware-software co-design 才能補滿 (p.10)。
- 對於短的 single-shot 6k token 序列,index gathering 與 pooling 的額外開銷反而超過稀疏化所節省的計算,使 end-to-end pipeline 變慢 (Appendix E, p.16–17)。
- 在 single-shot 設定中作者觀察不到 loop closure 現象並因此停用 causality,等同承認該機制對短序列無實質效益 (Appendix F, p.17)。

#### 4.2.2 Phyra-inferred

- 多 shot 主結果只與 LCT dense baseline 比較,未對 concurrent 的 VMoBA、VSA、Radial Attention 跑同 base、同設定的對照,使「first work…overcome quadratic attention barrier」的定位欠缺 sparse-vs-sparse 的證據 (Tab.1, §2 vs §4)。
- Tab.1 中 Image Quality 由 0.5140 下降到 0.5003、Aesthetic Quality 僅由 0.5436 提升到 0.5454,作者以「slight reduction in appearance fidelity」一句帶過,未提供 FVD、人類偏好或 identity 一致性的量化評估,使「surpassing fidelity」的論述薄弱。
- §G 提出「progressive 從大 chunk/k 漸進收斂到小 chunk/k」的設計直覺,但 Tab.3 只做固定 chunk size 與 k 的笛卡兒 sweep,並未實際對「progressive schedule」做消融,使方法 recipe 與最終訓練實際使用 (chunk size 由 10240→1280, k=5, Appendix F) 之間存在未驗證的設計選擇。
- Appendix I 的 Outer Loop Context Routing 宣稱可在 autoregressive sampling 下將 shot 數擴大 2–3 倍,但全文未提供任何量化或定性結果,核心 scaling 主張因此停留在敘述層級。
- Context Drop-off 的 $p_{\text{max}}$ 與 Drop-in 的 Poisson 參數 $\lambda$ 在正文與 Appendix F 都未列出具體值,使這兩個被列為「self-correcting」核心元件的設計無法被獨立重現或對照。
- Tab.4 對 forced links 的消融僅在 chunk size 5120、k=5 的單一配置下進行,未交叉驗證在更小 chunk 或更高 sparsity 下,intra-shot 與 cross-modal anchor 是否仍是穩定訓練的必要條件。
- 「分鐘級記憶」的展示上限就是 8-shot ≈ 64 秒,完全未測試模型在超出訓練 horizon 的延伸 roll-out 行為,因此「emergent long-term memory」的命題本質上仍停留在 LCT 的能力邊界內。

### 4.3 Phyra's Judgment (summary)

論文真正具有原創性的部分是「將 long-video generation 重新框架為 in-context retrieval」並把 content-aligned chunking、causal routing 與 attention sink 三項設計湊成一個能與 Flash-Attention var-len kernel 相容的最小可訓練稀疏方案;這個整合本身是有價值的工程貢獻。多數構件 (top-k chunk routing, mean-pool descriptor, sink tokens, intra-window links) 則是 MoBA 與 LLM sparse-attention 文獻向 video DiT 的直接遷移,並非新理論。最關鍵未解的問題是:被選中的 chunk 是否真的扮演「長期記憶」,還是只是在高度冗餘的鄰近影格之間做了一個統計上更便宜的平滑器,因為論文既無 retrieval 解析、也無超出訓練 horizon 的 stress test。

## 5. Methodology Deep Dive

### 5.1 Method Overview

MoC 將 DiT 主幹中的 dense self-attention 替換為一個 adaptive Mixture of Contexts 層,核心由三個耦合元素構成:(1) **content-aligned chunking** 沿著 frame、shot、modality 邊界切分多模態 token stream,使每個 chunk 在 3D RoPE positional manifold 上保持語意同質性,進而強化以 mean-pooled key 為代理的 chunk descriptor 的判別力;(2) **per-head dynamic top-k routing** 為每個 query token $q_i$ 在 candidate chunk 集合 $\Phi$ 中挑選最相關的 $k$ 個 chunk(論文取 $k=5$),公式為 $\Omega(q_i) = \arg\max_{\Omega^* \subseteq \Phi,\,|\Omega^*|=k} \sum_{\omega \in \Omega^*} q_i^\top \phi(K_\omega)$,其中 $\phi$ 為 mean pooling;(3) **mandatory anchors + causal mask** 強制 visual query 永遠連到全部 caption tokens(cross-modal sink,佔總 token <1%)以及自身所屬 shot 的 token(intra-shot local window),並透過 causal mask 將 chunk pair $(i,j),\ j\geq i$ 的 edge 移除,保證 routing graph 為 DAG,杜絕論文 Fig. 2 所示的 two-node feedback loop。

由於 top-k 操作本身不可微,但被選中的 chunk 之 K/V 仍會接收 attention 端的梯度,因此即使 $\phi$ 是 parameter-less 的算術平均,query/key projection 矩陣仍會被 end-to-end 塑形為更具判別性的表示;DDAE 的觀察(DiT patch token 的第一主成分常解釋 >90% 的局部變異)為以 mean 取代更複雜 descriptor 提供合理性。為避免「dead route」(類似 MoE 的 dead expert),作者引入兩種 stochastic regularization:**Context Drop-off** 從 $\Omega(q_i)$ 中隨機移除 $\lfloor p_{\text{drop}}\cdot k \rfloor$ 個 chunk,$p_{\text{drop}} \sim \mathrm{Uniform}(0,p_{\max})$;**Context Drop-in** 從未選中的 chunk 中注入 $m \sim \mathrm{Poisson}(\lambda)$ 個。再配合 **Per-Head Distributed Routing** —— 每個 attention head 獨立做整套 routing,使整個網路為 $L_{\text{layers}} \times H_{\text{heads}}$ 個獨立 router 組成的 ensemble —— 雖然每個 head 嚴格 sparse,但跨 head/layer 聯集所覆蓋的 context 遠大於 $k$,從多重 sparse 視角還原 dense context manifold。

效率層面,所有 mandatory + top-k 後的 (query, key) 對被 head-major rearrange (`s x h d -> h s x d`) 後打包進 Flash-Attention 的 variable-length kernel。對單一 head,$\mathrm{FLOPs}_{\mathrm{MoC}} \approx Ld + 2LCd + 4Lk\bar{m}d$,相對 dense 的 $4L^2d$,在論文 worked example($L\!\approx\!180\text{k},\ C\!=\!36,\ k\!=\!5,\ \bar{m}\!\approx\!1024,\ d\!=\!128$)下達成 >7× FLOPs 削減,作者進一步回報 2.2× 的端到端推論加速,主因即把每個 query 的 effective context 從 $L$ 縮到 $k\bar{m} \ll L$,且整套運算 head-independent,可直接做 tensor parallel sharding。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: Multi-modal token stream + content boundaries
   tokens x:                  [B, L, D]      L ≈ 180k, D = model dim
   frame_id / shot_id / modality_id: [B, L] each
   │
   │ x: [B, L, D]
   ▼
[1] Content-Aligned Chunking                                 (Sec 3.2)
   torch.bucketize + prefix-sums (cu_seqlen, cu_shot)
   produces C variable-length chunks Φ = {ω_1, ..., ω_C}     C ≈ 36
   │
   │ chunk_assignment: [B, L];   cu_seqlen: [B, C+1]
   ▼
[2] QKV Projection (per transformer block)
   Q, K, V:                   [B, L, H, d]   d = 128, H = ?  (not specified)
   │
   │ K: [B, L, H, d]
   ▼
[3] Mean-Pool Chunk Descriptors  (φ = mean, Eq. 3)           (Sec 3.1)
   segment_reduce K along chunk axis
   pooled_K:                  [B, C, H, d]
   │
   │ Q: [B, L, H, d],  pooled_K: [B, C, H, d]
   ▼
[4] Per-Head Top-k Routing (Eq. 3)                           (Sec 3.1 / 3.2)
   scores = Q · pooled_K^T :  [B, L, H, C]
      ├─ pre-routing mask: caption + intra-shot edges forced in
      ├─ causal mask: scores[..., j ≥ i] = -inf
      ├─ top-k:        keep best k per (sample, query, head)    k = 5
      ├─ Context Drop-off: drop ⌊p_drop · k⌋ random chunks
      └─ Context Drop-in:  add m ~ Poisson(λ) random chunks
   │
   │ Ω(q_i):                  [B, L, H, k']    k' ≈ k after perturbation
   ▼
[5] Variable-Length Gather (head-major)                      (Sec 3.3)
   rearrange "s x h d -> h s x d"; gather selected K, V tokens
   │
   │ packed Q: [B·H·L, d]
   │ packed K, V: [B·H·L·k·m̄, d]                   m̄ ≈ 1024
   ▼
[6] Flash-Attention varlen Kernel (Eq. 2)
   Attn(q_i, K_Ω, V_Ω) = Softmax(q_i K_Ω^T / √d) · V_Ω
   │
   │ attn_out:                [B, L, H, d]
   ▼
[7] Head Merge + Output Projection
   o:                         [B, L, D]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Content-Aligned Chunking

**Function:** 將多模態 token stream 沿 frame、shot、caption 等 content-aware 邊界切成 $C$ 個語意同質的 variable-length chunks,使後續以 mean-pooled key 作為 chunk descriptor 仍保有判別力。

**Input:**
- Name: `x`,以及 `frame_id`、`shot_id`、`modality_id` 三組邊界 id
- Shape: `x` 為 `[B, L, D]`;每個 boundary id 表為 `[B, L]`
- Source: DiT patch embedding 的輸出,加上上游解析得到的 frame/shot/modality 邊界

**Output:**
- Name: `chunk_assignment`、`cu_seqlen`、`cu_shot`
- Shape: `chunk_assignment` 為 `[B, L]`(取值於 $\{0,\dots,C-1\}$);`cu_seqlen` 為 `[B, C+1]`
- Consumer: §5.3.2 Mean-Pool Chunk Descriptor + Top-k Routing

**Processing:**

1. 收集 `frame_id`、`shot_id`、`modality_id` 三組邊界,並用 `torch.bucketize` 將每個 token 映射到所屬 chunk。
2. 同步建立 prefix-sum 表 `cu_seqlen`、`cu_shot`,作為下游 Flash-Attention varlen call 的 segment metadata。
3. 額外保留每個 query token 的 shot id,供 §5.3.3 的 intra-shot mandatory link 與 causal mask 使用。

**Key Formulas:** 無顯式公式;與 LLM 中固定窗 chunking(如 MoBA)的差別在於 chunk 大小不均勻、且嚴格貼合 frame/shot/modality 邊界。

**Implementation Details:** 全程 GPU 上完成;chunk 數量 $C$ 因內容而異,worked example 中 $C=36$、$\bar{m}\approx 1024$;intra-shot 邊界即 LCT 8-shot 場景的 shot 切點。

#### 5.3.2 Mean-Pool Chunk Descriptor + Per-Head Top-k Routing

**Function:** 為每個 chunk 計算一個 representative key descriptor,並針對每個 query token 在 per-head 層級獨立挑出 top-k 個最相關 chunk。

**Input:**
- Name: `Q`、`K`、`chunk_assignment`
- Shape: `Q`、`K` 為 `[B, L, H, d]`(論文取 $d=128$,$H$ 未明確列出);`chunk_assignment` 為 `[B, L]`
- Source: 本層的 QKV linear projection + §5.3.1 chunking 結果

**Output:**
- Name: `pooled_K`、`selected_idx`(僅 top-k,尚未經 mandatory anchor 與 causal mask)
- Shape: `pooled_K` 為 `[B, C, H, d]`;`selected_idx` 為 `[B, L, H, k]`,$k=5$
- Consumer: §5.3.3 Mandatory Anchors + Causal Mask

**Processing:**

1. 對 `K` 沿 chunk 維度做 `segment_reduce` mean,得到 `pooled_K`;此步代價約 $Ld$ adds,可忽略。
2. 計算 `scores = Q @ pooled_K.transpose(...)`,形狀 `[B, L, H, C]`,FLOPs ≈ $2LCd$。
3. 在 (sample, query, head) 軸上各自取 top-k chunks。
4. top-k 雖不可微,但被選中 chunk 的 K/V 仍接受梯度,間接塑形 query/key projection 與 mean-pooled descriptor。

**Key Formulas:**

$$
\Omega(q_i) = \Big[\arg\max_{\Omega^* \subseteq \Phi,\,|\Omega^*|=k}\ \sum_{\omega \in \Omega^*} q_i^\top \phi(K_\omega)\Big],\quad \phi(K_\omega) = \tfrac{1}{|\omega|}\sum_{t \in \omega} K_t
$$

**Implementation Details:** $\phi$ 為簡單算術平均,正當性由 DDAE 提供(DiT patch token 在局部子空間中第一主成分常解釋 >90% 變異,故 mean ≈ first-PC estimator);router 本身完全 parameter-less,語義由 attention 端的梯度透過被選中 chunk 反向傳遞給 Q/K 投影。

#### 5.3.3 Mandatory Anchors + Causal Mask

**Function:** 在 top-k 之前,透過 pre-routing mask 強制兩種固定連接(全 caption tokens、同 shot tokens),並用 causal mask 將 chunk-level edge 限制成 DAG,杜絕 loop closure。

**Input:**
- Name: `scores`、 query 與 chunk 的 `shot_id`、modality 標籤
- Shape: `scores` 為 `[B, L, H, C]`
- Source: §5.3.2 計算的 query–chunk dot-product 評分

**Output:**
- Name: 最終 `Ω(q_i)`(尚未經隨機擾動)
- Shape: `[B, L, H, k]`
- Consumer: §5.3.4 Drop-off / Drop-in regularization

**Processing:**

1. **Cross-modal sink:** 將 visual query 指向所有 caption/text chunk 的位置標記為「強制保留」,直接寫入 selected set,不佔 top-k budget(text 佔 <1% tokens)。
2. **Intra-shot window:** 將 query 所屬 shot 的 chunk 強制保留,提供 fallback 路徑並保留每個 shot 內部的局部保真度。
3. **Causal mask:** 對 chunk pair $(i,j),\ j\geq i$ 將 score 設為 $-\infty$,top-k 後 routing graph 為 DAG(對應 Fig. 2 描述的 loop closure 反例)。
4. 在強制保留之外,於剩餘 chunks 上做 top-k 補滿 budget。

**Key Formulas:** 無新公式;causal mask 直接作用於 §5.3.2 Eq. 3 的 dot-product 評分。

**Implementation Details:** 強制連接於 pre-routing 階段完成,確保 top-k 不會把 budget 浪費在 caption / intra-shot 這類已強制保留的 chunk 上;對於 fine-tune 預訓練 LCT 模型尤其關鍵,可保住每個 shot 內部的 fidelity 並提供穩定的梯度通道。

#### 5.3.4 Context Drop-off / Drop-in Regularization

**Function:** 對 top-k 結果做隨機擾動,防止 dead route(類比 MoE dead expert)、平衡 routing 分佈,並逼迫網路在 context 缺席或多餘時仍能 robust 輸出。

**Input:**
- Name: `Ω(q_i)`(已含 mandatory + top-k)
- Shape: `[B, L, H, k]`
- Source: §5.3.3 輸出

**Output:**
- Name: 擾動後的 `Ω(q_i)`
- Shape: `[B, L, H, k']`,$k'\approx k$(隨機浮動)
- Consumer: §5.3.6 Variable-Length Gather + Flash-Attention

**Processing:**

1. **Drop-off:** 抽 $p_{\text{drop}} \sim \mathrm{Uniform}(0, p_{\max})$,從 $\Omega(q_i)$ 隨機移除 $\lfloor p_{\text{drop}}\cdot k\rfloor$ 個 chunk,促使網路學到 redundancy。
2. **Drop-in:** 抽 $m \sim \mathrm{Poisson}(\lambda)$,從未選中的 chunks 中隨機加入 $m$ 個,使 underutilized chunk 也接收梯度,長期均衡 routing 分佈。

**Key Formulas:**

$$
p_{\text{drop}} \sim \mathrm{Uniform}(0,\,p_{\max}),\qquad m \sim \mathrm{Poisson}(\lambda)
$$

**Implementation Details:** router 為 parameter-less,因此擾動不會干擾 routing 自身學習;真正關鍵的 chunk 會經由 attention 端梯度自我強化(query/key projection 自校正)。論文未公布 $p_{\max}$ 與 $\lambda$ 的具體數值。

#### 5.3.5 Per-Head Distributed Routing

**Function:** 在 (layer, head) 層級獨立執行整套 routing,使整個 DiT 等效於 $L_{\text{layers}}\times H_{\text{heads}}$ 個獨立 router 的 ensemble,在每個 head 嚴格 sparse 的同時讓全網覆蓋遠超 $k$ 的 context。

**Input:** 任一 transformer block 的 `Q`、`K`、chunk descriptors。
- Shape: `[B, L, H, d]`,各 head 各自走完 §5.3.2–§5.3.4 流程
- Source: 上一層 block 輸出 + 本層 QKV projection

**Output:** 各 (layer, head) 自己的 selected chunk 集合與 attention output。
- Shape: 每 head 為 `[B, L, d]`,合併後為 `[B, L, D]`
- Consumer: 本層 output projection / 下一層 block

**Processing:** 同一 query token 在不同 head 取得不同 top-k 集合;雖然每個 head 只能看 $k$ 個 chunk,但跨 head/layer 的 union 涵蓋顯著大於 $k$ 的 context。

**Key Formulas:** 無新公式;為架構設計選擇。

**Implementation Details:** 不同 head 在 DiT 中專門化方向不同(低階紋理 vs 高階語意身分),需要不同歷史片段;此設計即源自此先驗。所有運算 head-independent,可直接用 tensor parallelism + sharding 在多 GPU 並行。

#### 5.3.6 Flash-Attention Variable-Length Kernel

**Function:** 把每個 query 在 mandatory + top-k + 擾動後的 (query, key) 對打包進 Flash-Attention 的 variable-length kernel,完成最終的 fine-grain attention。

**Input:**
- Name: `Q`、 gathered `K_Ω`、 gathered `V_Ω`、 prefix-sum `cu_seqlen`
- Shape: head-major rearrange (`s x h d -> h s x d`) 後,packed `Q` 為 `[B·H·L, d]`、packed `K, V` 為 `[B·H·L·k·m̄, d]`(每 query 平均檢索 $k\bar{m}$ 個 token)
- Source: §5.3.5 各 head 的 selected indices + §5.3.1 的 prefix-sum 表

**Output:**
- Name: `attn_out`
- Shape: `[B, L, H, d]`,merge head + output projection 後為 `[B, L, D]`
- Consumer: residual + FFN + 下一個 transformer block

**Processing:**

1. head-major rearrange,使 GPU gather coalesced。
2. Flash-Attention varlen call:對每個 query token,只在其 $\Omega(q_i)$ 對應的 $k\bar{m}$ 個 key 上做 softmax(下式)。
3. 整體 head-independent,可在多裝置切分。

**Key Formulas:**

$$
\mathrm{Attn}(q_i, K, V) = \mathrm{Softmax}\!\left(\frac{q_i K_{\Omega(q_i)}^\top}{\sqrt{d}}\right) V_{\Omega(q_i)}
$$

每 head 的 FLOPs:

$$
\mathrm{FLOPs}_{\mathrm{MoC}} \approx Ld + 2LCd + 4Lk\bar{m}d,\qquad \mathrm{FLOPs}_{\mathrm{dense}} = 4L^2d
$$

**Implementation Details:** 在 worked example $L\!\approx\!180\text{k},\ C\!=\!36,\ k\!=\!5,\ \bar{m}\!\approx\!1024,\ d\!=\!128$ 下,論文回報 $\mathrm{FLOPs}_{\mathrm{MoC}}\approx 2.32\times 10^{12}$、$\mathrm{FLOPs}_{\mathrm{dense}}\approx 1.66\times 10^{13}$,削減比例 $\frac{\mathrm{FLOPs}_{\mathrm{dense}}}{\mathrm{FLOPs}_{\mathrm{MoC}}} \approx \frac{2L}{Cd + 2k\bar{m}}$ 大於 7×;端到端推論加速 2.2×(VBench 8-shot 480p 場景,≈180k tokens)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Curated multi-shot narrative dataset (LCT [14] protocol; movies/TV/documentaries, segmented by PySceneDetect, captioned by Gemini-1.5) | Long, scene-level multi-shot text-to-video generation | 約 500K 標註 scenes（平均 5 shots/scene，約 2.5M shot clips） | Training (multi-shot model) |
| Mined long single-shot videos with substantial temporal variation, sub-shot 切分後當作 multi-shot | 平滑過渡（無硬切）的 multi-shot 資料增強 | 約 1M scene-level samples | Training (multi-shot model) |
| VBench / VBench++ [21, 22] | Video generation 評估基準 | the paper does not specify the per-prompt count used in this paper's evaluation | Evaluation (test) |
| Vchitect dataset [11, 33] | Single-shot 480p text-to-video（Wan-2.1-1.3B 實驗） | the paper does not specify | Training (Wan-2.1-1.3B 實驗) |

註：Single-shot 320×192/12 FPS 的對照實驗使用上述 multi-shot 訓練資料中的 image + single-shot video 部分聯合訓練；論文未另外列獨立資料集。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Subject Consistency (VBench) | 主要 subject 在整段影片中是否被忠實保留 | yes |
| Background Consistency (VBench) | 背景在整段影片中是否被忠實保留 | yes |
| Motion Smoothness (VBench) | 動態流暢度（無 jitter / 突兀切換） | yes |
| Dynamic Degree (VBench) | 影片中動態的程度（鼓勵動態而非靜止內容） | yes |
| Aesthetic Quality (VBench) | 每幀的視覺美學品質 | no |
| Image Quality (VBench) | 每幀的技術品質 | no |
| Sparsity | 被剪除的 attention token-pair 比例 | yes |
| FLOPs | Attention 的乘加計算量 | yes |
| End-to-end speedup vs. Flash Attention [8, 9] | 整體生成 wall-clock 加速倍率 | yes |

論文核心主張是「在 minute-scale 多 shot 場景下，以 learned sparse routing 在大幅降低 FLOPs / 提升速度的同時，維持甚至超越 dense baseline 的品質」，因此 VBench 四項一致性/動態指標 + sparsity / FLOPs / speedup 為 primary。

### 6.3 Training and Inference Settings

- 主架構（multi-shot）：以 LCT [14] 的 3B-parameter MMDiT [10] 為 base model，將 self-attention 換成 MoC，沿用 LCT 的訓練流程（identical training scheme as LCT）；context 為 8 shots × 8s × 480p × 12 FPS，每段約 22k tokens、整段 scene 約 180k tokens（§4 Base model / Baselines）。
- Multi-shot model 訓練設定（Appendix F）：聯合訓練 images + single-shot videos + multi-shot videos；chunk size 從 10240 → 5120 → 2560 → 1280 漸進縮小；top-k = 5；強制 intra-shot link 與 cross-modal link（每個 shot 對自身做 self-attention，每個 chunk 同時 attend 到 local 與 global prompt）；learning rate 9e-5；訓練 20k iterations。
- Single-shot model 訓練設定（Appendix F）：8s × 320×192 × 12 FPS（約 6.3k tokens/影片）；chunk size 256、top-k = 3；啟用 intra-chunk link 與 forced cross-modal link（每個 chunk 強制 attend 自身與 prompt tokens）；未啟用 causality（未觀察到 closed-loop 病態）；learning rate 9e-5；訓練 10k iterations。
- Ablation 訓練設定（Appendix G）：統一使用 16× H100；single-shot ablation 訓 30k iterations、multi-shot ablation 訓 10k iterations；learning rate 2e-5。
- Wan-2.1-1.3B 實驗（Appendix H）：在 Vchitect 資料集 480p 解析度上，dense / MoC 兩設定各以 32 GPUs 訓 1 天（2000 iterations）；chunk size = 1560（Wan-2.1-1.3B 一個 frame 的 token 數）；MoC 僅套在 self-attention（Wan 為 regular DiT 而非 MMDiT）。
- Inference：Attention 以 Flash-Attention 2 [8, 9] 的 var-len kernel 執行，配合 head-major 重排與 on-the-fly `segment_reduce` mean pooling；其餘 batch size、sampler、step 數等推論設定 the paper does not specify。
- FLOPs 範例（§3.3）：在 L≈180k、$\bar m \approx 1024$、k=5、C=36、d=128 下，$\text{FLOPs}_{\text{MoC}} \approx 2.32\times 10^{12}$ vs. $\text{FLOPs}_{\text{dense}} \approx 1.66\times 10^{13}$，約 7× 縮減。

### 6.4 Main Results

Multi-shot 8-shot scene（≈64 秒、180k tokens；Tab. 1）

| Method | Subject Cons. ↑ | Background Cons. ↑ | Motion Smooth. ↑ | Dynamic Degree ↑ | Aesthetic ↑ | Image Quality ↑ | Sparsity ↑ | FLOPs ↓ | Notes |
|---|---|---|---|---|---|---|---|---|---|
| LCT [14] (dense) | 0.9378 | 0.9526 | 0.9859 | 0.4583 | 0.5436 | **0.5140** | 0% | $1.7\times 10^{13}$ | Dense baseline |
| **Ours (MoC)** | **0.9421** | **0.9535** | **0.9920** | **0.5625** | **0.5454** | 0.5003 | **85%** | $\mathbf{2.3\times 10^{12}}$ | 7× FLOPs ↓、2.2× end-to-end speedup |

Single-shot 8s × 320×192 × 12 FPS（約 6.3k tokens；Tab. 2）

| Method | Subject Cons. ↑ | Background Cons. ↑ | Motion Smooth. ↑ | Dynamic Degree ↑ | Aesthetic ↑ | Image Quality ↑ | Sparsity ↑ | FLOPs ↓ |
|---|---|---|---|---|---|---|---|---|
| Base 3B MMDiT [10] | 0.9380 | 0.9623 | 0.9816 | 0.6875 | 0.5200 | 0.6345 | 0% | $1.9\times 10^{10}$ |
| **Ours (MoC)** | **0.9398** | **0.9670** | **0.9851** | **0.7500** | **0.5547** | **0.6396** | **83%** | $\mathbf{4.1\times 10^{9}}$ |

Wan-2.1-1.3B 上的單 shot 實驗（Tab. 5）

| Method | Subject Cons. ↑ | Background Cons. ↑ | Motion Smooth. ↑ | Dynamic Degree ↑ | Aesthetic ↑ | Image Quality ↑ | Sparsity ↑ |
|---|---|---|---|---|---|---|---|
| Dense Attention | 0.9512 | 0.9339 | 0.9869 | 0.4219 | 0.5154 | 0.5831 | 0% |
| **MoC (ours)** | **0.9549** | **0.9537** | 0.9833 | **0.6250** | **0.5204** | **0.6016** | **81%** |

Zero-shot sparsification（Appendix D, Fig. 6）：將 MoC（>75% sparsity）直接套到預訓 dense DiT 而不微調，仍能維持一定程度的 subject identity、背景佈局與粗略動態，論文未提供量化 VBench 數字。

### 6.5 Ablation Studies

- Chunk size sweep（Tab. 3，single-shot，固定 k=3）：chunk size 從 64 → 1024 改變。極小 chunk（64、128）雖能將 sparsity 推到 92–96%，卻顯著傷害 Dynamic Degree（0.34、0.29）與 Aesthetic；中等 chunk（256）在品質與 sparsity 取得平衡（83% sparsity、Dynamic 0.46）；大 chunk（1024）反而把 sparsity 拉到只剩 35%、卻不再帶來明顯品質提升。診斷意義充足，揭露 chunk size 對 long-context recall 的非單調影響，並支持論文「漸進式從大 chunk/大 k 收斂到小 chunk/小 k」的訓練曲線假設。
- Top-k sweep（Tab. 3，single-shot，固定 chunk = 256）：k 從 1 → 6。k=1 時各項 consistency 接近飽和（0.999）但 Dynamic Degree 崩到 0.13、Image Quality 反而最高 0.7421，顯示模型退化成幾乎複製近鄰 → 缺乏動態；隨 k 上升 Dynamic Degree 與 Aesthetic 整體上升、consistency 略降。屬於有效的診斷型 ablation，量化了 routing fan-out 的取捨。
- Forced links + Context Drop In/Out（Tab. 4，multi-shot，chunk 5120、k=5）：
  - 完全沒有 forced link：訓練極不穩定，Dynamic Degree=0.0000、Image Quality=0.1552，模型基本崩潰。
  - 只加 force cross-modal、不加 intra-shot：仍崩潰（Image Quality 0.1572、Dynamic 0.02）。
  - 加 force intra-shot、不加 cross-modal：穩定恢復（Dynamic 0.5729、Image Quality 0.4472）。
  - 同時加 intra-shot + cross-modal：Image Quality 進一步提升到 0.5104。
  - 再加 Context Drop In/Out：Subject/Background/Motion/Image Quality 全面再升（Image 0.5061、Background 0.9579）。
  此 ablation 直接對應論文方法章節的兩個關鍵設計（intra-shot anchor 與 cross-modal sink、drop-in/drop-out 正則化），屬於診斷型而非 sanity check。
- Causality ablation（Fig. 2，multi-shot，定性）：移除 causal mask 並把 k 設為 1，觀察到 shot 9↔shot 11 形成兩節點 feedback loop、人物身份混淆。屬於針對 §3.2 因果路由設計的診斷型 ablation，但僅有 routing-count 圖示與定性 frame，未報告 VBench 數字。
- Zero-shot sparsification（Appendix D）：將 MoC 直接插入凍結權重的 dense 模型，驗證 mean-pool descriptor 本身的可用性。此實驗目的明確是驗證 router 設計而非 sanity check，但僅有定性結果，未提供 VBench 量化。
- 漏掉的 ablation：context drop-off 與 drop-in 兩項從 Tab. 4 的「Drop In & Out」合併開關呈現，未拆開單獨評估各自的貢獻；per-head distributed routing 與 content-aligned chunking（vs. 等寬切塊如 MoBA 風格）未提供獨立的對照數字 — 這兩個是 method 章節重點宣稱、卻缺乏直接 ablation 支援的設計。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline (a current SoTA on the chosen task) — 主任務只比 LCT [14]（同一團隊先前工作）一個 dense baseline；論文自述 LCT 是「the only available architecture that supports long, multi-shot video generation for general scenes」（§4），但未與 Radial Attention、VMoBA、VSA、SparseVideoGen、STA、AdaSpa、SpargeAttn 等同期 sparse-attention 基線在同一設定下量化對照。
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — 涵蓋 multi-shot scene-level、single-shot 320×192 與 Wan-2.1-1.3B 480p 三種設定，但全部評估都用 VBench/VBench++ 一個 benchmark；無 long-range narrative coherence 的客觀基準（如 identity-preservation 量化、retrieval 正確率），僅以 Fig. 4 定性展示。
- [covered] Has ablations that diagnose the new components (not just sanity checks) — Chunk size、top-k、forced intra-shot/cross-modal links、Context Drop In/Out、causal mask 的 ablation 直接對應 §3 的方法選擇，並能解釋 trade-off（見 Tab. 3、Tab. 4、Fig. 2）。
- [partial] Has a scaling study (size, length, or compute) — Appendix B / Fig. 5 提供針對 shot 數（≈sequence length L）的 FLOPs 與 latency benchmark，呈現近線性擴展；但沒有針對模型參數量、訓練資料量或訓練步數的 scaling 曲線，亦未對「越長越好」做端到端品質的長度外推量化（outer loop 章節僅定性聲稱可延伸 2-3×）。
- [covered] Has an efficiency / wall-clock comparison — 報告 85% sparsity、>7× attention FLOPs 縮減與 2.2× end-to-end 加速（180k tokens 場景，§Abstract / §4 / Tab. 1），並有 Fig. 5 的 latency 線圖。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有 Tab. 1–5 都只回報單一數值，沒有 std、信賴區間或 multi-seed 結果。
- [missing] Releases code / weights / data sufficient for reproducibility — 論文僅提供 project page（https://primecai.github.io/moc/），未在正文或 appendix 中聲明釋出 code、checkpoint 或訓練資料；訓練資料來自私有 LCT 流程整理的非公開電影/電視資料，難以複製。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: MoC 作為長期記憶檢索引擎,能在分鐘級時間軸上維持身份、動作與佈局一致性。** 部分支持。Fig.3 與 Fig.4 提供定性證據,Tab.1 的 Subject/Background Consistency 略勝 LCT,但所有測試樣本都在 LCT 訓練 horizon (8 shots, 64 秒) 之內,沒有任何超出該長度的 generalization 證據,因此「minute-scale memory emergence」的因果鏈未被完整建立。
- **Claim 2: >7× attention FLOPs 削減與 2.2× 端到端加速。** 支持。Tab.1 與 §3.3 的 FLOPs 推導 ($Ld + 2LCd + 4Lk\bar{m}d$ vs $4L^2d$) 一致,Fig.5 的 latency benchmark 也呈現近線性 scaling,屬可驗證的硬性結果。
- **Claim 3: 維持甚至超越 dense baseline 的 fidelity。** 過度宣稱。Tab.1 中 Image Quality 退步、Aesthetic Quality 幾乎持平,僅 Dynamic-Degree 大幅上升;沒有 FVD、CLIP-T 或人類偏好評估,「surpassing fidelity」的措詞超出證據強度。
- **Claim 4: 因果路由消除病態 loop closure。** 支持。Fig.2 提供前後對比與 routing count 視覺化,單一直接的 ablation 即可成立此因果性。
- **Claim 5: 第一個以學習式 sparse routing 突破 quadratic attention 障礙的工作。** 過度宣稱。同期的 VMoBA、VSA 都是 trainable sparse attention for VDM,且論文本身在 §2 列為 concurrent;在沒有 head-to-head 比較下,「first」與「only」的定位站不住腳。

### 7.2 Fundamental Limitations of the Method

**Mean-pooled descriptor 的資訊瓶頸。** 整個 routing 訊號壓縮在每個 chunk 的單一 mean 向量上,作者以 DDAE [43] 與「first principal component 解釋 >90% local variance」為其辯護,但這只在 chunk 內語意同質時成立。當一個 shot 內含多個對象、突發動作或鏡頭變化時,mean 會把判別資訊抹平,query 將無法靠 dot-product 區分這個 chunk 與另一個外觀相似但語意不同的 chunk。這是「以單向量為 chunk 索引」這個設計的結構性上限,無法靠更多訓練資料消除。

**Routing 仍需評分所有 chunks。** 每個 query 需與全部 $C$ 個 chunk 的 mean key 做 inner product,成本 $2LCd$。在 paper 的 180k token 場景中 $C=36$ 尚屬可控,但 $C$ 隨序列線性成長,當目標推到 hour-scale 時 routing 本身會反過來成為瓶頸。Appendix I 提出的 outer loop hierarchical routing 是緩解方案,但它本質上是把同樣的 mean-pool + top-k rule 多套一層,並未解決「全集合排序」的根本成本,而且未經量化驗證。

**「檢索」與「記憶」的概念混淆。** MoC 沒有任何持久化的 memory store,所謂 retrieval 仍是對當前 forward pass 的 KV 序列做 attention。長距離資訊能否被回放,完全取決於 query/key projection 是否在訓練中學到放大這些距離上的相似度,而論文沒有提供任何 routing decision 的可解釋性分析 (例如同一角色的後續 shot 是否真的 retrieve 到首次出場的 shot)。在缺乏這類證據下,模型展現的「一致性」更可能來自相鄰冗餘 chunk 的局部平滑與 intra-shot/cross-modal anchor 的硬性約束,而非 router 主動的長距離 recall。

**訓練-推論 sparsity 綁定。** Sparsity 是在 fine-tune 階段就刻入網路的權重塑形,模型推論時無法依需求動態調整 $k$ 或 chunk size;Tab.3 的 sweep 都是獨立重訓的結果。這意味著任何 deployment 想在「品質」與「成本」之間調整,都得重新訓練,失去了某些 training-free sparse 方法 (如 SparseVideoGen, AdaSpa) 的部署彈性。

### 7.3 Citations Worth Tracking

- **[14] Long-Context Tuning (LCT)** — MoC 的唯一 base 與唯一比較對象,理解 LCT 如何把 single-shot DiT 透過 interleaved 3D RoPE 擴展至 8-shot scene 是讀懂 MoC 改了什麼的前提。
- **[28] MoBA** — Top-k chunk routing 的方法源頭,MoC 對 video 的調整 (content-aligned chunking, causality, anchor links) 唯有對照 MoBA 才能看出真正的 delta。
- **[40] VMoBA / [61] VSA** — 同期的 trainable sparse attention for video diffusion,論文未做頭對頭比較,讀者必須自行追蹤這兩篇才能判斷 MoC 的相對位置。
- **[26] Radial Attention** — 靜態 $O(n \log n)$ mask 的代表;與 MoC「動態學習式 routing」的論證形成最重要的方法論對立。
- **[43] DDAE** — MoC 為 mean-pool descriptor 辯護的核心理論依據,若該論文的 representation linearity 結論不成立,MoC 的 router 設計會失去理論根基。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在同一 LCT base 與相同 180k token 場景下,MoC vs VMoBA vs VSA vs Radial Attention 的 quality–FLOPs Pareto 曲線會落在哪裡?
- [ ] 當 roll-out 長度推到 16 或 32 個 shot (超出訓練 horizon),routing 是否仍能 retrieve 到首場 shot,還是會退化為僅依賴 intra-shot 與相鄰 chunk?
- [ ] 對被選中的 top-k chunks 做語意化追蹤 (例如同角色的 face token 是否真的 attend 到先前 shot 的 face chunk),能否提供 MoC 確實在做「retrieval」而非「local smoothing」的直接證據?
- [ ] Appendix I 提出的 outer loop context routing 在實測上能否兌現「shot 數擴大 2–3 倍」的宣稱,且這種擴展對 identity consistency 有多大代價?
- [ ] Tab.3 的 chunk size $\times$ k sweep 與 Appendix F 實際採用的「漸進 schedule」(10240 → 1280, k=5) 之間的差距,如果直接做 progressive ablation,Pareto 是否會明顯優於任何固定組合?
- [ ] Context Drop-off ($p_{\text{max}}$) 與 Drop-in ($\lambda$) 的具體值為何,移除其中之一的單因子消融是否會破壞 routing 的穩定性?
- [ ] 在 hard scene cut (語意完全更換) 與 smooth multi-shot (角色/場景延續) 兩類情境下,MoC 的 routing 行為與一致性指標是否呈現可區分的差異?

### 8.2 Improvement Directions

1. **同 base 的 sparse-vs-sparse 評測表。** 把 VMoBA、VSA、Radial Attention 都 plug 到 LCT base 上跑相同的 8-shot benchmark,並補上 FVD 與人類偏好。這是最低成本卻最能釐清「MoC 有多新」的補強,作者已掌握所有必要資源。
2. **Multi-vector chunk descriptor。** 將每個 chunk 的 mean 改為 top-k principal vectors 或 small set of cluster centers,讓 router 能區分內部 bimodal chunk;這直接針對 §7.2 的 mean-pool 瓶頸,只需改寫 descriptor 函式 $\phi(K_\omega)$,routing 與 Flash-Attention 後段無需動。
3. **Progressive chunk/k schedule 的正式 ablation。** 沿著作者在 §G 的直覺,設計 cosine 或 step-wise schedule 並對比固定設定的 Pareto;若預期成立,可能在同 sparsity 下進一步推升 Dynamic-Degree 而不犧牲 Subject Consistency。
4. **Routing 解釋性實驗。** 對訓練後模型抽取 routing decision,以角色/物件 ID 為 ground truth 計算 retrieval precision/recall;若分數高,可正面支持「learned long-term memory」的核心宣稱;若低,則需重新定位 MoC 為「結構化稀疏化器」而非檢索器。
5. **Block-sparse Triton 融合 kernel。** 作者已在 Limitation 提到 var-len attention 是 wall-clock 上限,將 routing + gather + attention 融合為單一 persistent kernel 是把 7× FLOPs 兌現為對應 wall-clock 的最直接路徑。
6. **Outer loop routing 的量化驗證。** 把 Appendix I 的階層式 routing 實作完成並接到 autoregressive sampling,報告 16-shot 與 32-shot 的 consistency 指標;這是唯一能讓「分鐘級」變成「多分鐘級」宣稱的實驗,且方法已成形,只缺執行。
