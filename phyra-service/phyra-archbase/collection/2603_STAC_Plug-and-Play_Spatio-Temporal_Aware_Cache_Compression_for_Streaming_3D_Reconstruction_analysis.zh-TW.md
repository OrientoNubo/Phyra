<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# STAC — STAC: Plug-and-Play Spatio-Temporal Aware Cache Compression for Streaming 3D Reconstruction

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | STAC |
| Paper full title | STAC: Plug-and-Play Spatio-Temporal Aware Cache Compression for Streaming 3D Reconstruction |
| arXiv ID | 2603.20284 |
| Release date | 2026-04-08 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.20284 |
| PDF link | https://arxiv.org/pdf/2603.20284v2 |
| Code link | — |
| Project page | https://stac-3r.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Runze Wang | University of Science and Technology of China (USTC), School of Artificial Intelligence and Data Science / GCL | https://rainzor.github.io | first author; Master's student |
| Yuxuan Song | University of Science and Technology of China (USTC) | — | co-author |
| Youcheng Cai | University of Science and Technology of China (USTC), Graphics and Geometric Computing Laboratory (GCL) | http://gcl.ustc.edu.cn/en/authors/cyc/ | corresponding author |
| Ligang Liu | University of Science and Technology of China (USTC), School of Mathematical Sciences / GCL | http://staff.ustc.edu.cn/~lgliu/ | senior author / lab head |

### 1.2 Keywords

streaming 3D reconstruction, KV cache compression, causal transformer, spatio-temporal sparsity, voxel-based token merging, VGGT, training-free, memory-efficient inference

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al.) | base model | Feed-forward transformer that jointly predicts cameras, depth, point maps and tracks; STAC compresses its causal-variant KV cache. |
| StreamVGGT | baseline | Causal variant of VGGT that maintains a linearly growing KV cache; STAC plugs in to compress it without retraining. |
| STream3R | baseline | State-of-the-art causal-VGGT for online 3D reconstruction; STAC integrates with it to cut memory ~10x and speed up 4x. |
| DUSt3R | influence | Pairwise pointmap regression baseline for dense reconstruction; compared against as a global-alignment online method. |
| MASt3R | influence | 3D-grounded matching extension of DUSt3R; compared as a pair-based streaming baseline. |
| H2O / StreamLLM | influence | LLM KV cache eviction (heavy hitters / sliding window) that inspires STAC's anchor + window design for 3D transformers. |
| Spann3R / CUT3R / Point3R | baseline | Online DUSt3R-family methods with persistent latents or 3D pointer memories; compared as streaming reconstruction baselines. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於串流式（streaming）3D 重建中的 KV cache 記憶體瓶頸問題。隨著 VGGT 等以 transformer 為核心的 3D 幾何模型擴展到因果（causal）變體（如 StreamVGGT、STream3R）以支援線上重建，KV cache 會隨輸入幀數線性成長，造成顯著的記憶體與延遲負擔；在受限預算下提早驅逐 token 又會嚴重損害幾何品質與時間一致性。作者觀察到 Causal-VGGT 的注意力同時具備空間與時間兩種結構化稀疏性：部分 head 對應視角／空間鄰近區域，另一些 head 則持續關注首幀、地標幀或相機 token。基於此，研究主題為設計一個免訓練、即插即用的「時空感知 KV cache 壓縮」框架 STAC，兼顧長期時序一致性、空間幾何資訊保留與 GPU 推論效率，使大型因果 transformer 能在固定記憶體下進行實時、長序列的 3D 重建。

### 2.2 Domain Tags

- computer vision
- 3D reconstruction
- efficient transformer inference
- streaming / online perception

### 2.3 Core Architectures Used

- **VGGT (Visual Geometry Grounded Transformer)**：被繼承的離線基礎模型，以單一 transformer 透過 global self-attention 同時預測相機參數、深度圖、point map 與 3D point tracks，提供 STAC 所建構的特徵骨幹與預測 head。
- **Causal-VGGT (StreamVGGT / STream3R)**：把 VGGT 的 global self-attention 換成 causal self-attention 並維持隨幀數線性成長的 KV cache 以支援串流推論，是 STAC 直接插入並進行壓縮的目標架構。
- **ViT image encoder**：對每一輸入幀進行 tokenization 產生視覺 token $F_t$，作為 Causal-VGGT decoder 的輸入。
- **Working Temporal Token Caching (本文提出)**：以 global reference token $M^{\text{refer}}$、sliding window token $M^{\text{window}}_t$ 與依衰減累積注意力分數動態挑選的 anchor token $M^{\text{anchor}}_t$ 構成短期高保真工作記憶。
- **Long-term Spatial Token Caching (本文提出)**：把驅逐 token 依 3D 座標分配到 voxel grid，於每個 voxel 維護短期 buffer $\mathcal{E}_u$ 與長期代表集 $\mathcal{G}_u$，並以一對一合併、多對一聚合與容量受限再合併（re-merging）來壓縮空間冗餘。
- **Chunk-based Multi-frame Optimization (本文提出)**：把已到達的連續幀分組為 chunk，於 chunk 內進行雙向注意力、跨 chunk 維持 causal 結構，以提升 GPU 平行度與局部一致性。
- **Custom CUDA merge-aware attention kernel**：在計算注意力輸出的同時更新重要性分數，並對 merged token 加上 $\log n$ count-based bias 以補償身分資訊流失。
- **Morton-code voxel indexing 與 kNN 檢索**：對 3D voxel 座標建立局部性保留索引，並於可見 voxel 集合 $V_t$ 的鄰域 $\text{Nbr}(V_t)$ 上做 kNN 查詢，以取得空間相關的 cached token $M^{\text{spat}}_t$。

### 2.4 Core Argument

作者主張：現有 Causal-VGGT 系列在串流 3D 重建中之所以陷入記憶體與延遲困境，並非因為架構表達能力不足，而是因為其 KV cache 管理策略「忽略了模型本身已經學到的時空結構化稀疏性」。透過注意力可視化，他們指出不同 head 各司其職——有的關注視角／空間鄰近區域（spatial sparsity），有的持續聚焦於首幀、語義穩定的地標幀或相機 token（temporal sparsity）。在這種結構下，對所有 token 一視同仁的均勻驅逐策略會同時犯兩個錯：早早丟掉真正具有長期價值的 anchor token，又無謂地保留大量在空間上高度冗餘的 view-dependent token。因此，邏輯上必要的解法是把記憶結構分成兩種互補形式：(1) Working Temporal Token Caching，藉由首幀全域參考、滑動視窗與以衰減累積注意力分數動態挑選的 anchor，維持高保真的短期工作記憶；(2) Long-term Spatial Token Caching，把被驅逐的 token 依 3D 座標放入 voxel grid，透過一對一合併、多對一聚合與容量限制下的再合併，將空間冗餘壓縮成緊緻的 voxel 級代表，保留早期觀測的幾何證據；再以 (3) Chunk-based Multi-frame Optimization 在維持因果性的前提下提升 GPU 利用率與局部一致性。這三者直接對應於前述觀察到的稀疏結構，是讓壓縮既「可塞回原模型而免訓練」又「在固定記憶體下不犧牲品質」的必然設計選擇，從而能達到近 10× 記憶體節省與 4× 推論加速。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(280 words)

標題「STAC: Plug-and-Play Spatio-Temporal Aware Cache Compression for Streaming 3D Reconstruction」一次給出三個關鍵承諾:這是一個「即插即用 (plug-and-play)」的模組、處理對象是「streaming 3D reconstruction」、技術手段是「spatio-temporal aware cache compression」。標題本身就把研究設定在「causal transformer 3D 重建的 KV cache 壓縮」這個交集問題上,並暗示這是一個 training-free 的後加掛模組,而非新架構。

Abstract 以三段式結構鋪陳故事。第一句先建立 streaming 3D reconstruction 的雙重需求:long-term temporal consistency 與 memory efficiency。接著指出現有 causal-VGGT 系列雖以 KV cache 解決前者,但 cache 隨 stream 長度線性成長造成記憶體瓶頸,且在受限預算下提早 evict 會嚴重劣化品質——這是論文要解決的具體問題。

第二段提出核心觀察「attention in causal transformers for 3D reconstruction exhibits intrinsic spatio-temporal sparsity」,將觀察直接接到方法名 STAC,並列出三個元件:Working Temporal Token Caching(用 decayed cumulative attention scores 保留長期 informative tokens)、Long-term Spatial Token Caching(以 voxel-aligned 表示壓縮空間冗餘 tokens)、Chunk-based Multi-frame Optimization(聯合處理連續 frames 提升時序一致性與 GPU 效率)。三個元件分別對應 temporal sparsity、spatial sparsity、計算效率三個面向。

第三段給出量化主張:reconstruction quality 達到 SOTA、memory 降低近 $10\times$、inference 加速 $4\times$。Abstract 同時配合 Figure 1 的 runtime–memory scaling 圖預示實驗主軸——per-frame runtime 與 cache memory 隨 stream 長度的成長曲線。整段 abstract 為後續章節劃出清楚分工:Introduction 講動機、Related Work 講定位、Observation 講 sparsity 證據、Method 拆解三元件、Experiments 驗證 $10\times$ 與 $4\times$ 數字。

### 3.2 Introduction

(760 words)

Introduction 採取「應用情境 → 傳統 pipeline 不足 → transformer 進展 → causal 化但 KV cache 線性成長 → 我們的觀察與貢獻」五段式漏斗結構,層層收斂到 STAC 的設計動機。

第一段建立 dense 3D reconstruction 的應用價值(VR/AR、機器人、自駕),並把 SfM 與 MVS 視為傳統路線的代表,指出其運算成本與可擴展性問題,為後續 transformer-based 方法鋪陳必要性。

第二段切入 transformer 路線,以 VGGT 為代表,強調其聯合預測 camera、depth、point map、track 的統一性,但同時點出兩種限制:全域 self-attention 需要 batch 處理,不適合 streaming;StreamVGGT 與 STream3R 之類 causal 變體雖能 streaming,但 KV cache 隨序列線性成長,造成記憶體與延遲問題。這段是把問題從「能不能做 streaming」收斂到「streaming 下的 cache 成本」。

第三段直接給出 paper 的 key insight:Causal-VGGT 的 KV cache 在兩個互補維度上呈現 structured sparsity——spatial sparsity(tokens 與 3D 位置與視角變化相關)與 temporal sparsity(部分 tokens 持續跨 frames 貢獻)。並指出現有 streaming 方法 uniform 地對待所有 tokens,導致 informative tokens 過早被 evict、transient tokens 卻被保留——這是 STAC 要修正的核心錯誤。

第四段正式提出 STAC,強調 plug-and-play 與 training-free 兩個關鍵屬性,並把設計類比到「人類記憶」:Working Temporal Token Caching 對應短期工作記憶,結合 global reference tokens、sliding local window、以 decayed cumulative attention 動態維護的 anchor tokens;Long-term Spatial Token Caching 對應幾何感知的長期記憶,把 evicted tokens 組織進 voxel grid 並漸進合併成 voxel 級表示,在保留早期幾何資訊的同時 bound memory growth。最後 Chunk-based Multi-frame Optimization 則把已到達的 frames 分組做聯合處理,允許 chunk 內限定的雙向資訊交換而不違反 streaming constraint,同時提升 GPU 利用率。

第五段以三點 bullet 列出貢獻:(i) 識別並分析 causal transformer 3D reconstruction 中的 structured spatio-temporal sparsity,(ii) 提出整合 working temporal caching 與 long-term spatial caching 的 cache compression 模組,(iii) 引入 chunk-based multi-frame 策略提升時序一致性並利用硬體並行性。最後再次強調這是首個對 causal transformer-based 3D reconstruction 進行 training-free 系統性 KV cache 壓縮的研究,並重述量化結果——記憶體 $10\times$、推論 $4\times$、品質「virtually indistinguishable」於原始 Causal-VGGT。

整段 Introduction 的論證邏輯清楚:應用需求創造 streaming 必要性 → causal 化解決 batch 限制但帶來新瓶頸 → 觀察到 sparsity 提供解 → 三元件方法 → 量化結果。它替後續所有章節劃分了任務:§2 Related Work 必須定位 STAC 在 streaming 3D 與 KV compression 兩條線中的位置,§4 Observation 必須提供 sparsity 的視覺證據,§5 Method 必須兌現三元件的具體機制,§6 Experiments 必須驗證 $10\times$ 與 $4\times$ 的數字。

### 3.3 Related Work / Preliminaries

(870 words)

Related Work (§2) 採取雙軌策略——先在 image-based 3D reconstruction 領域定位,再在 KV cache compression 領域定位,藉此凸顯 STAC 處於兩條研究線交集的獨特性。

§2.1 把 image-based 3D reconstruction 分成三個世代敘事。Traditional methods 以 SfM 與 MVS 為代表,優點是準確且 robust,缺點是模組化、需要序列優化、計算成本高、對 noise/occlusion/viewpoint 敏感——這建立了「為什麼需要 feed-forward」的動機。Offline approaches 以 DUSt3R、MASt3R、VGGT 為代表,DUSt3R 把 dense reconstruction 表示為直接 pointmap regression、MASt3R 在 3D 中 ground correspondences、VGGT 統一 camera/depth/pointmap/feature track 預測。後續變體如 VGGT-Long、FastVGGT 透過平行化或 training-free token merging 擴展到 thousands of images,但仍依賴對所有 input tokens 的 full self-attention,推論成本是 quadratic,且新 frame 到達需要重新推論——這直接帶出 streaming 的需求。Online/Streaming approaches 中,Spann3R、CUT3R、Point3R 在 DUSt3R 範式上加入 memory mechanism(persistent latent tokens、spatial feature banks、3D-aware pointer memories),但需要 architectural specialization 或 task-specific fine-tuning;StreamVGGT 與 STream3R 則把 VGGT backbone 改成 causal 形式並維持成長中的 KV cache。STream3R 在 online benchmark 上達到 SOTA,但仍受 cache 線性成長之累——這把問題收斂到「Causal-VGGT 的 KV cache 壓縮」。

§2.2 切換到 KV cache compression 文獻。Eviction-based 方法 H2O、StreamLLM 只保留高重要性 tokens;Merge-based 方法把即將被 evict 的 tokens 併入鄰近 important tokens 以減少資訊損失;multimodal/streaming 框架(streaming video QA、LiveVLM、StreamMem)採用 query- 或 saliency-driven 的壓縮與檢索。但作者強調這些方法主要利用相鄰 frames 或 spatial regions 的相似性,沒有針對 streaming 3D reconstruction 中大型 transformer 的 KV cache 同時揭露 spatio-temporal sparsity 與 local spatial redundancy——STAC 的差異化定位就是「首個利用 causal transformer-based 3D 模型內部 spatio-temporal 結構設計的 KV compression scheme」。

§3 Preliminaries 提供進入 method 前的數學記號鋪墊。先用 Eq. (1) 定義 VGGT 的 multi-view decoder 用 global self-attention 把每幀 visual tokens $F_t$ 聚合為幾何感知 tokens $G_t$,接著 Eq. (2) 透過 prediction head 解碼 camera $c_t$、depth $D_t$、point map $P_t$。隨後切換到 Causal-VGGT,把 global self-attention 換成 causal self-attention,並透過 Eq. (3) 引入 KV cache $\mathcal{M}^{\ell,h}_t = \{k^{\ell,h}_\tau, v^{\ell,h}_\tau\}_{\tau=1}^{t-1}$ 跨層 $\ell$ 與 head $h$ 累積過去 frames 的 keys/values。Eq. (4) 把 streaming inference 的 decoder 計算寫成 $G_t = \text{Decoder}(\text{Causal SelfAttn}(F_t, \{\mathcal{M}^{\ell,h}_t\}))$,使讀者明白後續 STAC 要壓縮的對象就是這個跨層跨 head 的 cache 集合。

兩節合起來把舞台佈置完整:從 Related Work 看,STAC 同時延伸 streaming 3D reconstruction 與 KV cache compression 兩條線並彌合它們之間的空缺;從 Preliminaries 看,讀者已掌握 KV cache 的數學定義與 Causal-VGGT 的 streaming 計算流程,接下來能直接進入 §4 Observation 中的 sparsity 視覺證據與 §5 的三元件設計。這節同時暗示 STAC 將以 STream3R 與 StreamVGGT 為主要 baseline,並會在 sliding-window 變體(STream3R-W、StreamVGGT-W)的對照下展示 spatio-temporal awareness 的價值。

### 3.4 Method (overview narrative)

(1580 words)

§4 Observation 與 §5 Method 構成方法故事的「觀察 → 設計 → 機制」三段論。Observation 提供經驗證據說服讀者 sparsity 真實存在,Method 則據此設計三個互補元件。

§4 以 Fig. 2 為視覺核心,把 Causal-VGGT 中四個代表性 attention head 的 attention map 攤開:Spatial Head (L13-H15) 顯示出與 camera motion 對齊的空間注意,代表 loop closure 與 revisit 時跨幀 attention 集中於空間鄰近區域;Reference Head (L18-H13) 持續注意第一幀 tokens,顯示其作為 global reference 的角色;Landmark Head (L19-H2) 把注意力錨定於語義穩定的 landmark frame tokens,提供長期時序線索;Camera Head (L21-H13) 對 camera tokens 維持 long-range attention,負責傳遞全域 context。從這四個 head 的差異化行為,作者抽出兩類 sparsity:Spatial Sparsity(view-dependent tokens 在 spatially adjacent regions 出現冗餘,並在 Supplementary §A 中以 feature similarity 與 3D coordinate 分析驗證)與 Temporal Sparsity(分為 first-frame correlation、landmark-frame correlation、camera-token correlation 三種 pattern)。這段最關鍵的論述是:既有 streaming 3D 方法忽略這些差異化 pattern、把所有 tokens 一視同仁,導致 globally important tokens 被過早 evict——這是 STAC 要修正的具體錯誤,直接驅動 §5 的設計。

§5 開頭以 Fig. 3 提供 STAC 的整體架構圖,將方法拆成三個互補元件,清楚對應 §4 觀察到的兩種 sparsity 加上計算效率考量。

§5.1 Working Temporal Token Caching 處理 temporal sparsity。它把 time step $t$ 的 working temporal cache 寫成 $\mathcal{M}^{\text{temp}}_t = \mathcal{M}^{\text{refer}} \cup \mathcal{M}^{\text{window}}_t \cup \mathcal{M}^{\text{anchor}}_t$,三種 token 各自對應 §4 觀察到的 first-frame correlation、短期時序連續性、以及 landmark/camera 持續性 attention pattern。Global reference tokens $\mathcal{M}^{\text{refer}}$ 固定為第一幀 $m_1$,負責 unified coordinate alignment;Local window tokens $\mathcal{M}^{\text{window}}_t$ 用大小 $s$ 的 sliding window 捕捉 motion continuity;Anchor tokens $\mathcal{M}^{\text{anchor}}_t$ 在預算下動態維護,代表持續 informative 的 landmark 與 camera tokens。Anchor 的選擇透過兩步機制:Eq. (6) 計算 query-to-key 的 scaled dot-product attention $\alpha^{j,i}_t$,Eq. (7) 以 exponential decay 更新累積重要性 $s^i_t = \gamma s^i_{t-1} + \sum_j \alpha^{j,i}_t$,其中 $\gamma \in (0,1)$;Eq. (8) 對即將離開 sliding window 的 token 與既有 anchor 集合做 Top-K 選擇,確保只有 salient 且時序穩定的 features 被持久 cache。

§5.2 Long-term Spatial Token Caching 處理 spatial sparsity 與長序列下早期幾何資訊的保留。每個 voxel $u$ 維護 dual-cache:short-term 緩衝 $\mathcal{E}_u$ 收納近期 evicted tokens、long-term 集合 $\mathcal{G}_u$ 儲存合併後的 representatives。Token merging 被建模為 capacity-constrained online clustering,包含兩個互補操作。One-to-one merging:對 evicted token $m_e$,以 Eq. (9) 在 $\mathcal{G}_u$ 中以 cosine similarity 找最相近 $\hat{m}_p$,若 $\cos_k(m_e, \hat{m}_p) > \lambda$ 則用 Eq. (10) 做 weight-fusion,並更新累積權重 $Z(\hat{m}_p)$;否則 $m_e$ 進入 $\mathcal{E}_u$ 等待 aggregation。Many-to-one aggregation:當 $\mathcal{E}_u$ 滿時以 Eq. (11) 把所有緩衝 tokens 用 highest-scored pivot $m_q$ 加權聚合成新 representative $\hat{m}$ 加入 $\mathcal{G}_u$。Re-merging:當 $\mathcal{G}_u$ 達到容量,選最低累積重要性的 representative $\hat{m}_l$ 與其最相似鄰居融合並丟棄 $\hat{m}_l$ 來騰出 slot,細節在 Supplementary §B.2。Token retrieval 階段(Eq. (12))在 time step $t$ 把 decoded 3D points 體素化為 visible voxel 集合 $\mathcal{V}_t$,並用 kNN 擴張到 $\text{Nbr}(\mathcal{V}_t)$ 後檢索所有 long-term 與 short-term tokens。為補償 token merging 造成的 identity loss,作者引入 count-based bias(Eq. (13))$q \cdot k / \sqrt{d_h} + \log n$,其中 $n$ 是 merged token 的計數,效果是讓被多次合併的 tokens 在 attention 中獲得適當加權。整個設計兼顧 memory efficiency(voxel-aware 壓縮)、long-term consistency(保留早期 scene info)、feature diversity(dual-cache 避免過早 collapse)。

§5.3 Chunk-based Multi-frame Optimization 處理 GPU 利用率與重建一致性。它把連續到達的 frames 分成 temporal chunks 聯合處理,維持 chunk-causal 性質——time step $t$ 時 chunk 中只用 index $\le t$ 的 frames,但在 chunk 內部 attention 可以雙向計算,允許 limited intra-chunk information exchange 提升 local 幾何一致性。實作上,作者用 Morton codes 把 3D voxel coordinates 映射為 locality-preserving indices,並把 token selection、merging、retrieval 跨層批次處理以降低 KV cache 開銷。

整個 §5 的內部邏輯清楚:§5.1 解 temporal sparsity、§5.2 解 spatial sparsity、§5.3 解計算效率。三者透過共用的 importance score(Eq. 7)與共用的 query-key attention(Eq. 6)互相耦合——anchor selection 與 spatial cache 的 pivot token 都用同一個 score、retrieval 出的 spatial tokens 也參與 working temporal cache 的 attention 計算。這種設計使得 §6 Experiments 可以直接消融這四個元件(AC、SC、CB、CO)以驗證每個組件的必要性。

### 3.5 Experiments (overview narrative)

(1100 words)

§6 以「實作細節 → 主要評估(3D reconstruction、camera pose) → 消融」三段式驗證 STAC 的三項主要主張:可即插即用、$10\times$ 記憶體節省、$4\times$ 推論加速、品質可比。

§6.1 Implementation Details 給出可重現的超參:decay factor $\gamma = 0.9$、voxel grid 解析度 0.05、token merging cosine 閾值 $\lambda = 0.8$、每 voxel 最多 $|\mathcal{G}| = 4$ merged tokens 與 $|\mathcal{E}| = 8$ evicted tokens、kNN 半徑為 $2\times$ voxel。Cache 預算配置為:第一幀 KV cache 全保留;剩餘預算為每幀 token 數的 $8\times$,其中 50% 給 temporal window($s = 4$)、25% 給 anchor tokens、25% 給 retrieved merged tokens(不足時補上 evicted tokens)。所有 KV cache 用 float16 儲存、chunk size 為 4、實驗在單張 40GB A100 上跑,並實作了 custom CUDA kernel 同時計算 attention output 與 importance score。Baselines 分三類:Causal-VGGT 系列(STream3R、StreamVGGT 與其 sliding window 變體 -W、加上 STAC 的 -STAC)、online 方法(Spann3R、CUT3R、Point3R)、pair-based + global alignment 方法(DUSt3R、MASt3R、MonST3R)——這個分組讓讀者可以分別在「相同 backbone 不同 cache 策略」與「不同方法路線」兩個層次比較。

3D Reconstruction 評估在 NRGBD 與 7-Scenes 上,輸入解析度 $518 \times 392$、stride 5 取 keyframes(每段 200–300 frames)、報告 Accuracy / Completion / Normal Consistency 三個幾何指標,並用 total memory 與 end-to-end FPS 衡量效率。Table 1 是主結果表,要傳達兩層訊息:第一,把 STAC 加到 STream3R 與 StreamVGGT 上後,memory 大幅下降同時 FPS 提升,而 reconstruction 品質與原始 full-cache 模型相當甚至更好——這驗證 spatio-temporal sparsity 模型化的價值。第二,在相同 memory budget 下與 STream3R-W22、StreamVGGT-W26 比較(把 sliding-window 加大以匹配總記憶體),STAC 在三個幾何指標上都更好,直接駁斥「sliding window 已經夠用」的反論。Fig. 4 提供 7-scenes 與 NRGBD 上 STream3R-STAC 與 StreamVGGT-STAC 對比 -W 與 GT 的視覺結果,作為 Table 1 的定性佐證。作者還強調 STAC 在 long sequence 上的優勢:Spann3R 與 CUT3R 因 implicit/latent memory 受 long-term drift/forgetting 之苦、Point3R 雖有 spatial memory 但缺乏顯式時序推理,而 STAC 的 dual-cache 同時抓住長程時序與結構化空間,提供 compact 又 expressive 的記憶。

Camera Pose Estimation 在 Sintel、TUM Dynamics、ScanNet 上做(Table 2),報告 ATE、RPE trans、RPE rot,經 Sim(3) Umeyama alignment。STream3R-STAC 與 StreamVGGT-STAC 在大幅縮小 memory budget 的前提下達到與原模型相當的 pose 精度,並在 Sintel 與 TUM 等動態場景特別 robust——這把 STAC 的價值從「靜態幾何重建」延伸到「動態場景時序一致性」。

§6.3 Ablation Study 在 NRGBD 上以 STream3R-W8 為 baseline 逐一移除四個關鍵元件(Table 3):AC (Anchor Cache)、SC (Spatial Cache)、CB (Count-based Bias)、CO (Chunk-based Optimization)。w/o AC:時序穩定性下降,因為失去 persistent 幾何與 camera 資訊;w/o SC:memory 變小、速度更快但 reconstruction 品質明顯下滑——這直接反映 spatial cache 在保留早期 scene 證據的關鍵角色;w/o CB:識別性損失未補償導致品質微降,證明 count-based bias 的必要性;w/o CO:品質與 runtime 同時惡化,證實 chunk-based 處理對精度與並行性都不可或缺。Full 配置在所有指標上都最佳(Acc 0.0648、Comp 0.0142、NC 0.6995),整張 Table 3 構成「四元件缺一不可」的論證。

整節的論證鏈條完整:Implementation 確保可重現性、Reconstruction & Pose 雙任務驗證主張、Sliding-window 對照排除「更大 window 即可」的替代解釋、Ablation 證明每個元件都做出 marginal 貢獻。Fig. 1 的 runtime–memory 曲線在這節重新被引用,把 stream length 增長下 STAC 穩定 70 ms 上下、Causal-VGGT 從 90 ms 攀升到 257 ms 的對比視覺化,最直接呈現 $4\times$ 加速與 $10\times$ 記憶體下降的 scaling 故事。

### 3.6 Conclusion / Limitations / Future Work

(290 words)

§7 以三個層次收尾:總結貢獻、指出限制、勾勒未來方向。

總結部分把 STAC 重新定位為「training-free framework for streaming 3D reconstruction with spatio-temporal aware cache compression」,並依次回顧三個元件的角色:Working Temporal Token Caching 透過 decayed cumulative attention 保留 informative tokens、Long-term Spatial Token Caching 把冗餘 features 壓縮為 voxel-based representations 以便 efficient reuse、Chunk-based Multi-frame Optimization 聯合 refine 連續 frames 同時利用 GPU parallelism。作者在這裡再次強調 STAC 同時做到 SOTA reconstruction quality 與顯著降低 memory/computational cost,並把貢獻提升到方法論層次:STAC 「establishes a unified paradigm for causal 3D perception under constrained memory」——意即這套 spatio-temporal 結構化壓縮思路有跨任務適用性。

未來工作則點名兩個方向:adaptive cache learning(用學習方式動態調整 cache 預算與閾值,而非依賴固定超參)與 multimodal extensions(把 spatio-temporal sparsity 模型推到其他模態,例如語言或音訊串流),目標是進一步提升 scalability 與 generalization。這兩個方向自然延伸自 §6.1 中固定的 $\gamma = 0.9$、$\lambda = 0.8$、voxel 解析度 0.05 等手調超參,以及 STAC 目前僅在 3D reconstruction backbone 上驗證的事實。

Limitation 部分誠實列出兩個邊界:第一,voxel-based spatial caching 用固定解析度 grid,在 large/unbounded outdoor scenes 中 active voxel 數會隨場景延展而成長導致 memory 上升——作者提出實務 workaround:把不常存取的 tokens offload 到 CPU 等外部儲存以減輕 GPU 壓力。第二,在高度動態環境下,fast object motion 會引入不一致的 token representations,影響 cache 穩定性。這兩點限制與 §6.2 中 STAC 在 Sintel/TUM 等動態場景仍 robust 的結果並不矛盾——前者說的是 voxel 機制的 scaling 邊界,後者說的是動態場景中 cache 穩定性的進一步上限,共同為 future work 中 adaptive cache learning 的必要性提供具體切入點。

## 4. Critical Profile

### 4.1 Highlights

- 作者在 Fig. 2（p.3）中以可視化方式同時揭露 Causal-VGGT 注意力的四種專業化 head（spatial / reference / landmark / camera），把「KV cache 應該如何壓縮」從工程直覺提升為以模型行為為依據的設計命題。
- 在固定 8× frame token 的 budget 下，STream3R-STAC 在 NRGBD 上達到 ACC mean $0.065$、Comp mean $0.014$、NC mean $0.700$，與 full STream3R（ACC $0.053$、NC $0.703$）幾乎沒有差距，但 runtime 記憶體僅 $0.86$ GB vs $19.75$ GB（Table 1, p.7）。
- 端對端 FPS 從 STream3R 的 $2.52$ 提升到 STream3R-STAC 的 $10.53$，達成論文標題宣稱的 $4\times$ 加速（Table 1, p.7）。
- 在相同 total memory 下，STAC 全面優於放大的 sliding window 變體：STream3R-W22 與 STream3R-STAC 都用約 $2.2$ GB，但 NC 為 $0.689$ vs $0.700$，FPS 為 $5.24$ vs $10.53$（Table 1, p.7）。
- Fig. 10（p.16）顯示在約 1500 幀的長序列上，per-frame 推論時間維持 $70$–$90$ ms 區間，KV cache 記憶體在前段成長後逐步飽和，active voxel 數收斂至 $\sim 2900$，驗證 bounded memory 的設計目標。
- Ablation（Table 3, p.8）拆解四個組件：移除 anchor cache 使 NC 從 $0.6995$ 降至 $0.6991$ 但記憶體降至 $0.572$ GB（不合理低 —— 應為打字錯誤，但拆解仍顯示 chunk-based optimization 對 runtime 影響最大，從 $138.12$ ms 縮短至 $71.18$ ms）。
- 補充材料 Fig. 6–8（pp.13–14）以 intra-voxel / inter-voxel / layer-wise 三種尺度量化 KV cache 的空間區域性，給 voxel-wise 壓縮提供了實證基礎而非僅憑 attention map。
- 為了讓 merge-aware attention 真正可加速，作者實作了自訂 CUDA kernel 同時計算 attention output 與 importance score，並以 Morton code 將 voxel 座標映射為 locality-preserving index（p.6），在工程細節上下了真功夫。
- 跨任務評估（Table 1 重建、Table 2 pose、Table 4 video depth）涵蓋 NRGBD、7-Scenes、Sintel、TUM、ScanNet、Bonn、KITTI 七個基準，比一般「training-free 模組」論文更完整。
- 在 Sintel 的 video depth 上，STream3R-STAC 的 Abs Rel $0.259$ / $\delta < 1.25$ 為 $69.6$，甚至略勝 offline full-attention VGGT 的 $0.297$ / $68.8$（Table 4, p.16），暗示適度壓縮在動態場景反而具去噪效果。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- **Voxel 解析度受限於固定 grid**：在大型或無界 outdoor 場景中 active voxel 數會隨場景擴張而成長，導致記憶體增加；作者僅提到「offload 到 CPU」作為未來方向（Limitation, p.8）。
- **動態場景下 cache 不一致**：高速移動物體會使同一 voxel 內的 token 對應到不同物理內容，造成 cache representation 不穩，作者承認這影響重建品質但未提出對策（Limitation, p.8）。

#### 4.2.2 Phyra-inferred

- **「$10\times$ 記憶體節省」的口徑游移**：Abstract 與標題使用的 $10\times$ 是相對於 full STream3R 的 runtime KV $19.75$ GB 對比 STAC 的 runtime $0.86$ GB；但 Table 1 的主數值欄是 total $2.20$ GB（含 voxel cache），相對基線只有 $\sim 9\times$，且僅比 W22 的 $2.19$ GB 小不到 $1\%$，論文未在 abstract 澄清這個差異。
- **Pose estimation 結果與「virtually indistinguishable」宣稱有出入**：Table 2 顯示 STream3R-STAC 在 Sintel 的 RPE rot 為 $1.486$ vs full STream3R 的 $0.867$（劣化 $71\%$）、ScanNet RPE rot $0.983$ vs $0.850$（劣化 $16\%$），對需要精確 trajectory 的下游應用而言並非可忽略的退化。
- **Video depth 在 KITTI 上明顯退化**：StreamVGGT-STAC 的 Abs Rel $0.192$ vs StreamVGGT $0.173$、$\delta < 1.25$ 為 $67.6$ vs $72.2$（Table 4, p.16），但論文沒有討論為何 outdoor / 大尺度場景上壓縮代價特別大。
- **Hyperparameter 敏感度沒有給出 robustness 結論**：Table 5 顯示 voxel 解析度從 $r=0.025$ 到 $r=0.10$，記憶體從 $4.861$ GB 變到 $1.119$ GB（差 $4\times$），但 ACC/Comp/NC 幾乎不動 —— 這代表「固定 budget」其實是被 $r$ 隱性設定的，使用者要在新場景上選 $r$ 缺乏指引。
- **Observation 採用「top 1024 keys per query」做可視化**：Sec. 4 與 Fig. 2 的稀疏結論建立在固定截斷上，但 Causal-VGGT 是 dense attention，論文沒有量化「除了 top 1024 之外的 attention mass 比例」，因此「結構化稀疏」的程度本身缺乏絕對量化。
- **未對照其他 LLM cache compression 方法**：論文反覆引用 H2O（[51]）、StreamLLM（[47]）、D2O（[37]），但只與 sliding window 直接比較，沒有把 H2O 之類的 importance-eviction 方法直接套到 Causal-VGGT 做 baseline，導致無法分離「3D voxel 結構」與「heavy-hitter 機制」的貢獻。
- **Token merging 數學近似缺實證**：Supp. Sec. B.2 的 re-merging 採用 small-angle approximation $\hat m_i \approx \hat m_p$ 與 $m_i \approx \hat m_i$，但補充材料未在實際 cache 上量化兩者的角度誤差或 $e^{-1}$ 加權項對最終重建品質的影響。
- **Chunk size 沒有 ablation**：固定 $4$ 是 throughput / memory 的關鍵旋鈕，但 Table 3 只 ablate「有無 chunk」，沒有 ablate $\{1, 2, 4, 8\}$ 等不同 chunk size 在串流嚴格性 vs GPU 利用率之間的取捨。

### 4.3 Phyra's Judgment (summary)

STAC 真正新穎的部分是「把 LLM KV cache eviction 與 token merging 與 3D voxel 空間索引結合」這個跨領域組合，而 observation（Fig. 2）對 Causal-VGGT 的 head 分工剖析也是有獨立貢獻價值的工程觀察。但其餘部分 —— anchor + sliding window + reference token、similarity-weighted 加權合併、count-based attention bias —— 幾乎都是 H2O / StreamLLM / D2O / ToMe 已知技術的線性組合，創新主要在「組裝方式」而非「演算法本質」。論文最大的未解問題是：spatial sparsity 真正帶來多少增益，相對於僅做 anchor + window + voxel-aware retrieval（沒有合併與 count-bias）能否更乾淨地拆解？目前 Table 3 只給了「全部 vs 拿掉一個」的破壞性測試，無法回答這個問題。

## 5. Methodology Deep Dive

### 5.1 Method Overview

STAC 是一個免訓練（training-free）、即插即用（plug-and-play）的 KV cache 壓縮框架，專為 Causal-VGGT 系列在串流式 3D 重建任務上設計。其核心動機來自第 4 節的觀察：Causal-VGGT 的注意力呈現 **空間稀疏性**（spatial sparsity，部分 head 對應視角／空間鄰近區域）與 **時間稀疏性**（temporal sparsity，部分 head 持續關注首幀、地標幀或相機 token）。傳統的均勻驅逐策略忽略此結構，導致長期重要的 anchor token 過早被丟棄，同時保留大量空間冗餘的 view-dependent token，使重建品質與時間一致性顯著下降。

STAC 由三個互補的元件組成：(1) **Working Temporal Token Caching**（§5.1，工作時序快取），整合首幀全域參考、滑動視窗、以及由衰減累積注意力分數動態挑選的 anchor token，維持高保真的短期工作記憶；(2) **Long-term Spatial Token Caching**（§5.2，長期空間快取），將被驅逐的 token 依其 3D 座標投放到 voxel grid 中，透過 one-to-one 合併、many-to-one 聚合、以及容量受限下的 re-merging，將空間冗餘壓縮為緊湊的 voxel 級代表，保留早期觀測的幾何證據；(3) **Chunk-based Multi-frame Optimization**（§5.3，多幀分塊優化），在保持因果性前提下，將數個近鄰幀組成 chunk 共同處理，提升 GPU 利用率與局部一致性。

具體流程上（見 Fig. 3，page 5），每個 chunk 內的 ViT-tokenized frames 經由 Causal-VGGT 的 self-attention 與 causal-attention 計算 geometry-aware 表示 $G$，attention 同時讀取 working temporal cache $\mathcal{M}^{\text{temp}}$ 與從 voxel grid 檢索出的 spatial cache $\mathcal{M}^{\text{spat}}$。每次 KV cache 存取後，工作時序快取會更新 token 的衰減累積分數 $s_i$（Eq. 7），保留 anchor / reference / window token、驅逐其餘者；被驅逐且具 3D 座標的 token 經 Head Decoder 後，依 voxel index 路由至對應 voxel：與長期代表相似度高（$>\lambda$）者進行 one-to-one 加權融合（Eq. 9–10），相似度低者暫存於短期 buffer $\mathcal{E}_u$，待 buffer 滿時以最高分數 token 為樞紐做 many-to-one 聚合（Eq. 11）並插入長期集合 $\mathcal{G}_u$；當 $\mathcal{G}_u$ 達到容量上限，再對最低累積權重的代表執行 re-merging 以釋放槽位。

### 5.2 Pipeline Diagram with Tensor Shapes

設輸入解析度為 $518 \times 392$（§6.1），ViT patch size 為 14（DINOv2 預設）；故每幀 tokenized 後為 $H' \times W' = 37 \times 28 = 1036$ 個 patch token。記符號如下：$B$=batch（通常為 1），$C_s$=chunk size=4（§6.1），$N_p=1036$=每幀 patch token 數，每幀額外含 4 個 camera token（VGGT 設定，paper 未明示具體數量，標 `?`），$d$=token embedding 維度（VGGT 預設 1024，paper 未明示，標 `?`），$L$=transformer 層數，$H$=每層 head 數，$d_h=d/H$=per-head 維度。

```
Input: streaming frames at time t
   │  shape: [B, C_s, 3, 518, 392]                      # chunk of C_s frames
   │
   ▼
ViT Image Encoder (DINOv2)                              # §3 Preliminaries
   │  shape: [B, C_s, N_p+?, d]                         # ?=camera tokens, e.g. 4
   │
   ▼
Per-chunk feature F_t                                   # entering Causal-VGGT decoder
   │  shape: [B, C_s, N_p+?, d]
   │
   ▼
─────────────  ×L Causal-VGGT Decoder Layers  ─────────────
   │
   ├─→ q,k,v projection
   │     q: [B, C_s, N_p+?, H, d_h]
   │     k: [B, C_s, N_p+?, H, d_h]
   │     v: [B, C_s, N_p+?, H, d_h]
   │
   ├─→ Working Temporal Cache  M^temp_t   (Sec. 5.1)
   │     M^refer  (first-frame tokens):       [B, N_p+?, L, H, 2, d_h]
   │     M^window (last s frames, s=4):       [B, s·(N_p+?), L, H, 2, d_h]
   │     M^anchor (Top-K by score s_i):       [B, K, L, H, 2, d_h]   # K = 25% of budget
   │
   ├─→ Long-term Spatial Cache  M^spat_t   (Sec. 5.2)
   │     Voxel grid V (resolution 0.05m)
   │     For visible voxels Nbr(V_t) via kNN (radius=2 voxels):
   │       G_u (long-term reps, |G|=4):       [B, |Nbr|·4, L, H, 2, d_h]
   │       E_u (short-term buffer, |E|=8):    [B, |Nbr|·8, L, H, 2, d_h]
   │     M^spat_t = G_u ∪ E_u
   │
   ├─→ Causal Self-Attention over (F_t, M^temp_t, M^spat_t)
   │     attn_logits = q · k^T / √d_h + log n     # count-bias, Eq. 13
   │     # n = merge count carried by each merged token
   │     output: [B, C_s, N_p+?, H, d_h]
   │
   ├─→ Score Update (Eq. 6, 7)
   │     α_{j,i} = softmax_i(q_j · k_all / √d_h)
   │     s_i ← γ·s_i + Σ_j α_{j,i},  γ=0.9
   │     score tensor s: [B, |M^temp_t|]
   │
   └─→ Anchor Re-selection (Eq. 8)
         M^anchor_{t+1} = TopK({m_i}, {s_i})     # over M^anchor_t ∪ m_{t-s}
─────────────────────────────────────────────────────────
   │
   ├─→ Per-layer/per-head outputs concatenated
   │     shape: [B, C_s, N_p+?, d]
   │
   ▼
Geometry-aware tokens G_t
   │  shape: [B, C_s, N_p+?, d]
   │
   ├─→ Head Decoder (DPT-style, [23])                   # Eq. 2
   │     camera params c_t:   [B, C_s, ?]               # paper does not specify
   │     depth maps D_t:      [B, C_s, 518, 392]
   │     point maps P_t:      [B, C_s, 3, 518, 392]
   │
   └─→ Evicted Tokens (with 3D coords from P_t)         # routed to spatial cache
         m_e = {k_e, v_e}: [B, N_evict, L, H, 2, d_h]
         3D coord: [B, N_evict, 3]
         │
         ▼
   Voxel Routing & Merging (Sec. 5.2)
         ├─→ if cos_k(m_e, m̂_p) > λ=0.8:                # Eq. 9, 10
         │     one-to-one merge into G_u
         ├─→ else: enqueue into E_u
         │     if |E_u| full: many-to-one aggregate     # Eq. 11
         │       m̂ = Σ ω(m,m_q)m / Σ ω(m,m_q)
         │       insert into G_u
         └─→ if |G_u| ≥ 4: re-merge least-weight rep    # Sec. 5.2
```

備註：每個 KV token 沿 layer/head 維度展開為 $[L, H, 2, d_h]$（2 對應 $k$ 與 $v$）；以 float16 存儲（§6.1）。`?` 標記之 camera token 數量、$d$ 與 head decoder 輸出 camera 參數維度於 paper 未明示。

### 5.3 Per-Module Breakdown

#### 5.3.1 ViT Image Encoder

**Function:** 將每幀 RGB 影像切 patch 並透過 DINOv2 編碼為 visual token，作為 Causal-VGGT decoder 的輸入。

**Input:**
- Name: streaming frames within chunk
- Shape: $[B, C_s, 3, 518, 392]$
- Source: 串流輸入；以 chunk size $C_s=4$ 分組（§5.3, §6.1）

**Output:**
- Name: $F_t$
- Shape: $[B, C_s, N_p+?, d]$，其中 $N_p=1036$（patch tokens），`?` 為 camera token 數量
- Consumer: Causal-VGGT decoder（§5.1 working temporal caching）

**Processing:**

每幀獨立經過 DINOv2 ViT [21]，輸出 visual token。沿 patch 軸 flatten 後與 camera token 拼接形成 $F_t$。輸出緊接進入 $L$ 層 Causal-VGGT decoder。

**Key Formulas:**

對應 paper 的 Eq. 1（VGGT 原始設定）：

$$
\{G_t\}_{t=1}^{T} = \text{Decoder}\!\left(\text{Global SelfAttn}(\{F_t\}_{t=1}^{T})\right)
$$

而 Causal-VGGT 將 global 改為 causal（Eq. 4），只能看 $\le t$ 的 KV cache。

**Implementation Details:**

Paper 沿用 VGGT [40] 與 StreamVGGT [52] / STream3R [16] 的 backbone 設定，未在 §5–6 重新揭露 ViT 架構超參數（layer 數、$d$、head 數等）。輸入解析度為 $518 \times 392$（§6.2），與 patch size 14 對齊。

#### 5.3.2 Working Temporal Token Caching

**Function:** 在固定 KV budget 下維持高保真短期工作記憶，整合 global reference、滑動視窗、與基於衰減累積注意力分數動態選出的 anchor token。

**Input:**
- Name: $F_t$（current frame features）、$M_t^{\text{temp}}$（前一步狀態）
- Shape: $F_t$: $[B, C_s, N_p+?, d]$；$M_t^{\text{temp}}$ 為三類 KV 的聯集（見下）
- Source: ViT encoder 與前一時刻的 cache 狀態

**Output:**
- Name: $M_t^{\text{temp}} = M^{\text{refer}} \cup M_t^{\text{window}} \cup M_t^{\text{anchor}}$（Eq. 5）；以及更新後的 anchor 集合 $M_{t+1}^{\text{anchor}}$
- Shape: 三類分別為 $[B, N_p+?, L, H, 2, d_h]$（refer，固定）、$[B, s(N_p+?), L, H, 2, d_h]$（window，$s=4$）、$[B, K, L, H, 2, d_h]$（anchor，$K=$ budget 之 25%）
- Consumer: Causal self-attention（Eq. 4, 6）；evicted 的 sliding window token $m_{t-s}$ 路由至 spatial cache（§5.3.3）

**Processing:**

1. **Cache 組成（Eq. 5）：** 將首幀 KV 作為固定 reference $M^{\text{refer}}$；維持大小為 $s$ 的滑動視窗 $M_t^{\text{window}}=\{m_{t-s},\dots,m_{t-1}\}$；anchor 集合 $M_t^{\text{anchor}}$ 在 KV budget 約束下由分數動態維護。
2. **分數計算（Eq. 6）：** 對當前幀的每個 query $q_t^j$ 與所有 cached key $k_t^{\text{all}}$（含 $M_t^{\text{temp}}$、$M_t^{\text{spat}}$、當前幀 $m_t$）做 scaled dot-product softmax，得 $\alpha_t^{j,i}$。
3. **分數更新（Eq. 7）：** 對 $M_t^{\text{temp}}$ 中每個 token，以衰減因子 $\gamma=0.9$ 累積：$s_t^i = \gamma s_{t-1}^i + \sum_j \alpha_t^{j,i}$；當前幀新 token 初始化為 $s_t^i = \sum_j \alpha_t^{j,i}$。
4. **Anchor 選取（Eq. 8）：** 在 $M_t^{\text{anchor}} \cup m_{t-s}$ 範圍內取 Top-K，作為新 anchor；未入選且具 3D 座標者，連同 evicted window token 進入 §5.3.3。

**Key Formulas:**

$$
M_t^{\text{temp}} = M^{\text{refer}} \cup M_t^{\text{window}} \cup M_t^{\text{anchor}}
$$

$$
\alpha_t^{j,i} = \text{Softmax}_i\!\left(q_t^{j} \cdot k_t^{\text{all}} / \sqrt{d_h}\right)
$$

$$
s_t^i = \gamma\, s_{t-1}^i + \sum_{j=1}^{N} \alpha_t^{j,i},\quad i \in \mathcal{I}(M_t^{\text{temp}})
$$

$$
M_{t+1}^{\text{anchor}} = \text{Top-K}\bigl(\{m_i\}, \{s_i\}\bigr),\ i \in \mathcal{I}(M_t^{\text{anchor}} \cup m_{t-s})
$$

**Implementation Details:**

衰減因子 $\gamma=0.9$；滑動視窗 $s=4$；KV budget 設為 $8\times$ 每幀 token 數，分配為 50% window、25% anchor、25% retrieved merged tokens（§6.1）。首幀 KV 完整保留。所有 KV cache 以 float16 儲存。為支援 merge-aware attention，作者實作自訂 CUDA kernel 同時計算 attention 輸出與重要性分數（§6.1）。

#### 5.3.3 Long-term Spatial Token Caching

**Function:** 利用 3D 空間冗餘將被驅逐的 token 壓縮為 voxel 級代表，避免長序列中過早遺失早期幾何證據；支援空間檢索並對 attention 注入 count-bias 補償身份損失。

**Input:**
- Name: evicted token $m_e=\{k_e, v_e\}$（含 3D 座標，由 head decoder 解碼之 point map 提供）
- Shape: $m_e$: $[B, N_{\text{evict}}, L, H, 2, d_h]$；對應 3D 座標 $[B, N_{\text{evict}}, 3]$
- Source: §5.3.2 之 evicted token、§5.3.4 之 chunk 內 head decoder

**Output:**
- Name: spatial cache $M_t^{\text{spat}}$（檢索結果，Eq. 12）
- Shape: $[B, |\text{Nbr}(V_t)|\cdot(|G|+|E|), L, H, 2, d_h]$，每 voxel $|G|=4$、$|E|=8$
- Consumer: Causal self-attention（Eq. 6）

**Processing:**

1. **Voxel 路由：** 依 token 的 3D 座標映射到 voxel index $u$；每 voxel 維護雙快取 $G_u$（長期代表）與 $E_u$（短期 buffer）。
2. **One-to-one merging（Eq. 9–10）：** 對 evicted $m_e$，在 $G_u$ 中以 key 空間 cosine similarity 找最相似代表 $\hat m_p$；若 $\cos_k(m_e, \hat m_p) > \lambda=0.8$，以 $\omega(\cdot,\cdot) = \exp(\cos_k(\cdot,\cdot))$ 加權融合並更新累積權重 $Z(\hat m_p) \leftarrow Z(\hat m_p) + \omega(m_e, \hat m_p)$。
3. **Many-to-one aggregation（Eq. 11）：** 若相似度未達 $\lambda$，將 $m_e$ 入隊到 $E_u$；當 $|E_u|$ 達上限，以 $E_u$ 中分數最高的 token $m_q$ 為樞紐，加權聚合 buffer 中所有 token 形成新代表 $\hat m$，插入 $G_u$，累積權重 $Z(\hat m)=\sum_{m\in E_u}\omega(m, m_q)$。
4. **Re-merging（§5.2）：** 若 $|G_u|$ 已滿（$=4$），選取累積權重最低的 $\hat m_l = \arg\min_{\hat m\in G_u} Z(\hat m)$，融入其在 $G_u\setminus\{\hat m_l\}$ 中最相似鄰居後將 $\hat m_l$ 移除，騰出槽位（implementation 細節 paper 指向 Sec. B.2 of Supplementary）。
5. **檢索（Eq. 12）：** 解碼當前幀 per-pixel 3D 點並 voxelize 得 visible voxel $V_t$；以 voxel 中心 kNN 擴展為 $\text{Nbr}(V_t)$（半徑為 2 voxel）；取 $M_t^{\text{spat}} = \{m \mid m\in G_u\cup E_u,\ u\in \text{Nbr}(V_t)\}$。
6. **Count-based attention bias（Eq. 13）：** 為補償合併造成的 identity loss，每個 merged token 攜帶計數 $n$，attention logits 改為 $q\cdot k/\sqrt{d_h} + \log n$。

**Key Formulas:**

$$
\hat m_p = \arg\max_{\hat m \in G_u} \cos_k(m_e, \hat m)
$$

$$
\hat m_p \leftarrow \frac{Z(\hat m_p)\,\hat m_p + \omega(m_e, \hat m_p)\,m_e}{Z(\hat m_p) + \omega(m_e, \hat m_p)}
$$

$$
\hat m = \frac{\sum_{m\in E_u} \omega(m, m_q)\,m}{\sum_{m\in E_u} \omega(m, m_q)}
$$

$$
M_t^{\text{spat}} = \{m \mid m \in G_u \cup E_u,\ u \in \text{Nbr}(V_t)\}
$$

$$
\text{logit} = q \cdot k / \sqrt{d_h} + \log n
$$

**Implementation Details:**

Voxel grid 解析度 0.05；cosine similarity 閾值 $\lambda=0.8$；每 voxel $|G|=4$、$|E|=8$；kNN 檢索範圍為 2× voxel radius（§6.1）。3D voxel 座標以 Morton code [7, 19] 映射為 locality-preserving 索引以提升 GPU 友善度（§5.3）。Token 選取、合併、檢索在前向傳播後跨 layer 批次化以降低 KV cache overhead（§5.3）。

#### 5.3.4 Chunk-based Multi-frame Optimization

**Function:** 在保持因果性前提下將近鄰幀分塊聯合處理，提升 GPU 利用率並改善局部幾何一致性。

**Input:**
- Name: 連續可用幀構成的 chunk
- Shape: $[B, C_s, 3, 518, 392]$，$C_s=4$
- Source: 串流輸入

**Output:**
- Name: chunk-level 幾何輸出（camera, depth, point maps）
- Shape: 與 §5.3.1 head decoder 輸出一致
- Consumer: 下游重建管線；evicted token 進入 §5.3.3

**Processing:**

於時刻 $t$，僅以索引 $\le t$ 的可用幀組成 chunk（chunk-causal，無未來幀洩漏）。**Chunk 內 attention 為雙向**，允許有限的 intra-chunk 資訊交換；**chunk 邊界**仍維持串流的因果限制。Chunk 級執行可攤銷 kernel launch 與資料搬運開銷，相較 frame-by-frame 顯著提升 GPU 效率（§5.3）。

**Key Formulas:**

無新增封閉式公式；該模組沿用 §5.1–5.2 的注意力與快取機制，差異在於 chunk 內 attention 為雙向、chunk 間維持因果。

**Implementation Details:**

Chunk size $C_s=4$（§6.1）。Cached token 經 voxelize 後以 Morton code 索引；token 選取／合併／檢索跨 layer 在前向結束後批次化以降低 KV cache overhead（§5.3）。所有實驗於單卡 NVIDIA A100 40GB 執行（§6.1）。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| NRGBD [2] | 3D reconstruction、video depth | 每段 200–300 frames(stride 5 取 keyframe) | test only(training-free) |
| 7-Scenes [30] | 3D reconstruction | 每段 200–300 frames(stride 5) | test only |
| Sintel [5] | camera pose、video depth | the paper does not specify per-sequence frame counts | test only |
| TUM Dynamics [31] | camera pose | the paper does not specify | test only |
| ScanNet [8] | camera pose | the paper does not specify | test only |
| Bonn [22] | video depth | the paper does not specify | test only(附錄 C.2) |
| KITTI [13] | video depth | the paper does not specify | test only(附錄 C.2) |

STAC 為 training-free 的 plug-and-play 模組,所有資料集皆僅用於評測,沒有微調或重新訓練。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| Accuracy (ACC) | 預測點雲到 GT 的距離(mean / median) | yes |
| Completion (Comp) | GT 到預測點雲的距離(mean / median) | yes |
| Normal Consistency (NC) | 表面法向量的一致性 | yes |
| Memory (GB) | 串流推論期間的 KV cache 與整體記憶體佔用 | yes |
| FPS | 整條 reconstruction pipeline 的 end-to-end 吞吐量 | yes |
| ATE | Sim(3) 對齊後的 absolute trajectory error | no |
| RPE trans / RPE rot | relative pose error 的平移與旋轉分量 | no |
| Abs Rel | scale-invariant 的 video depth 相對誤差 | no |
| $\delta < 1.25$ | depth 預測落在 GT 1.25 倍範圍內的比例 | no |

論文核心訴求為「在記憶體預算受限下維持 reconstruction 品質並提升吞吐」,因此 ACC / Comp / NC 與 Mem / FPS 同列為 primary。

### 6.3 Training and Inference Settings

STAC 不需要任何訓練:整套方法以 training-free 的方式插入 Causal-VGGT(STream3R [16] 與 StreamVGGT [52])backbone。

推論超參數設定:
- decay factor $\gamma = 0.9$、voxel 解析度 $r = 0.05$、merging 相似度門檻 $\lambda = 0.8$。
- 每個 voxel 上限 $|G| = 4$ merged tokens、$|E| = 8$ evicted tokens;kNN retrieval 在 $2\times$ voxel 半徑內進行。
- 第一個 frame 的 KV cache 完整保留,其餘預算為「frame token 數 $\times 8$」,其中 50% 配給 temporal window($s = 4$)、25% 給 anchor tokens、25% 給 retrieved merged tokens(不足時補 evicted tokens)。
- KV cache 以 `float16` 儲存;chunk-based multi-frame optimization 使用 chunk size $= 4$。
- 自製 CUDA kernel 同時計算 attention 輸出與 importance score。
- 硬體:single NVIDIA A100 40GB;3D reconstruction 評測使用 $518 \times 392$ 解析度輸入,每段 200–300 frames(stride 5)。
- batch size、optimizer、learning rate、training steps:不適用(training-free);base model 的訓練細節 the paper does not specify。

### 6.4 Main Results

NRGBD 主要結果(stride 5,Mem 括號為 runtime usage,排除 spatial cache 儲存):

| Method | ACC mean ↓ | Comp mean ↓ | NC mean ↑ | Mem (GB) ↓ | FPS ↑ | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| VGGT [40] | 0.017 | 0.012 | 0.740 | – | $<1$ | offline,完整 self-attention |
| Spann3R [38] | 0.068 | 0.020 | 0.637 | 0.37 | 57.21 | DUSt3R 系 online |
| Point3R [46] | 0.095 | 0.021 | 0.668 | 1.50 | 8.34 | 顯式 spatial pointer memory |
| STream3R [16] | 0.053 | 0.013 | 0.703 | 19.75 | 2.52 | 完整 KV cache |
| StreamVGGT [52] | 0.134 | 0.059 | 0.651 | 19.75 | 2.48 | 完整 KV cache |
| STream3R-W22 | 0.088 | 0.019 | 0.689 | 2.19 | 5.24 | sliding window,Mem 對齊 |
| **STream3R-STAC** | **0.065** | **0.014** | **0.700** | **2.20 (0.86)** | **10.53** | 本論文方法 |
| StreamVGGT-W26 | 0.174 | 0.061 | 0.634 | 2.57 | 5.41 | sliding window,Mem 對齊 |
| **StreamVGGT-STAC** | **0.126** | **0.047** | **0.682** | **2.57 (0.86)** | **10.49** | 本論文方法 |

關鍵讀法:STAC 在與 sliding-window 變體相同 memory budget 下,ACC / Comp / NC 全面勝出;對比完整 KV cache 的原版 backbone,記憶體下降近 $10\times$、FPS 提升約 $4\times$,而品質僅有微幅退化(NRGBD 上 NC 從 0.703 降到 0.700)。Camera pose(Sintel / TUM / ScanNet)與 video depth(附錄 Sintel / Bonn / KITTI)亦呈相同趨勢:STAC 對齊原 backbone,並在多數場景超越 sliding-window baseline。

### 6.5 Ablation Studies

主表 Ablation(Table 3,以 STream3R-W8 為 baseline,於 NRGBD 上量測 ACC / Comp / NC、Mem、Runtime):

- **w/o AC(移除 Anchor Tokens)**:NC 從 0.6995 退到 0.6991、Comp 從 0.0142 升至 0.0209,記憶體與 runtime 下降。直接驗證 anchor token 對長期一致性的貢獻,屬於針對「temporal sparsity」核心元件的 diagnostic ablation。
- **w/o SC(移除 Spatial Cache)**:Comp 升至 0.0199,但 Mem 從 2.21 GB 降到 0.572 GB、runtime 從 71.18 ms 縮到 39.08 ms。直接量化 voxel-based spatial cache 的品質-成本 trade-off。
- **w/o CB(移除 Count-based Bias)**:三項品質指標皆退步(ACC 0.0666、Comp 0.0175、NC 0.6973);這是針對 token merging 後 identity loss 的補償機制驗證,問題設定恰當。
- **w/o CO(移除 Chunk-based Optimization)**:runtime 從 71.18 ms 暴增到 138.12 ms,且 ACC 也退步,確認 chunk 處理同時影響品質與 GPU 效率。

附錄延伸 Ablation:
- 超參數(附錄 Table 5):掃 voxel 解析度 $r \in \{0.025, 0.05, 0.10\}$ 與 $\lambda \in \{0.6, 0.8, 0.9\}$,顯示 $r = 0.05, \lambda = 0.8$ 在品質-記憶體之間取得平衡。屬 hyperparameter 敏感度分析,而非單純 sanity check。
- 壓縮策略(附錄 Table 6):比較 attention-guided selection vs random selection、weighted merging vs uniform merging,證明「為何要用 attention 指引而非 uniform」,屬於對方法設計選擇的 diagnostic 比較。

整體而言,Ablation 設計針對 STAC 的四個核心元件分別關掉,並補上超參數與替代策略掃描,並非僅刪除最弱元件做 sanity check;唯一未被獨立 ablate 的是「first-frame reference token 與 sliding window 各自的貢獻」,可能值得進一步拆解。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 直接對齊 STream3R [16](當前 online 3D reconstruction SoTA)、StreamVGGT [52],並對照 offline VGGT [40] 與 DUSt3R 家族的 Spann3R / CUT3R / Point3R。
- [covered] Has cross-task / cross-dataset evaluation — 跨 3D reconstruction(NRGBD、7-Scenes)、camera pose(Sintel、TUM、ScanNet)、video depth(Sintel、Bonn、KITTI)三類任務、共 7 個資料集。
- [covered] Has ablations that diagnose the new components — Table 3 對 Anchor、Spatial Cache、Count-based Bias、Chunk Optimization 各自獨立關閉,並附超參數與替代策略掃描(附錄 Table 5、6)。
- [partial] Has a scaling study (size, length, or compute) — 附錄 C.3 在 1500 frames 長序列上量測 inference time、KV cache 與 voxel 數隨 frame index 的演化,但僅一條序列;沒有掃模型大小或 chunk size 的 scaling 曲線。
- [covered] Has an efficiency / wall-clock comparison — Table 1 同時報 Mem(GB)與 FPS,Fig. 1 顯示隨 frame 增長的 per-frame runtime 與 cache 記憶體,Table 3 也含 backbone runtime(ms)。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 全文僅報單次數值,沒有 std、信賴區間或多 seed 結果;對於 ACC 差距 $\sim 0.001$ 的比較難以判斷顯著性。
- [partial] Releases code / weights / data sufficient for reproducibility — 摘要提供 project page `https://stac-3r.github.io/`,但論文正文未明確聲明 code 或 CUDA kernel 的公開狀態,reproducibility 程度仰賴 project page 實際內容。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

1. **「識別並分析 causal-transformer 3D 重建中的結構化時空稀疏性」**：Fig. 2（p.3）+ 補充材料 Fig. 6–8（pp.13–14）的 intra/inter-voxel 與 layer-wise 分析共同支持，**充分支持**。但「稀疏」缺乏絕對量化（attention mass 留在 top-K 的比例未報告）。
2. **「Spatio-temporal aware cache compression module」**：Table 3 的 ablation 顯示 anchor cache 與 spatial cache 各自有效，**部分支持**。問題是 ablation 沒有把 spatial cache 內的「one-to-one merging / many-to-one aggregation / re-merging」三步驟分別關掉，無法判斷哪一步是真正的關鍵設計。
3. **「Chunk-based multi-frame strategy」**：Table 3 顯示移除 chunk-based optimization 使 runtime 從 $71.18$ ms 升至 $138.12$ ms（$\sim 1.94\times$）並使 ACC/Comp 退化，**充分支持**。但這個觀察其實只說明「batching 比逐幀計算快」，並非新穎發現。
4. **「$\sim 10\times$ 記憶體節省、$4\times$ 推論加速」**：在 STream3R 上 FPS 從 $2.52 \to 10.53$（$4.18\times$），runtime memory 從 $19.75 \to 0.86$ GB（$23\times$），對應 abstract 的 $4\times$ 與 $10\times$ 屬於合理但**口徑寬鬆** —— total memory 比較只有 $\sim 9\times$（$19.75 / 2.20$），論文未在 abstract 區分。
5. **「重建品質與 full Causal-VGGT virtually indistinguishable」**：在 NRGBD 與 7-Scenes 重建任務上**支持**（Table 1），但在 pose（Table 2）與 KITTI video depth（Table 4）上**有明顯退化**，並非全任務都成立 —— 此宣稱**在重建任務上成立、整體上略嫌過度**。

### 7.2 Fundamental Limitations of the Method

**Voxel-based spatial cache 與 3D 輸出強耦合**：STAC 的 Long-term Spatial Token Caching 必須在每個 timestep 由 head decoder 先產生 per-pixel 3D 點才能 voxelize 並 retrieve。這意味著 STAC 不能在「pre-decoder layers 的 attention」直接套用 —— 它不是一個與 LLM cache compression 對等的「純 attention 層級」方法，而是必須等到模型已經輸出 3D 幾何。這在某些下游 head（如 camera-only 或 feature-track-only 推論）上是冗餘成本，論文未討論這種架構耦合的代價。

**靜態場景假設內建於 voxel 索引**：當物體在 voxel 之間移動時，同一個 voxel 在不同時間裡承載的 KV token 對應到不同物理內容，但合併演算法（cosine similarity > $\lambda$）仍會把它們融合。這不只是「dynamic scene 較困難」（作者承認的限制），而是 voxel 假設本身與動態世界的不相容 —— 任何不放棄 voxel 結構的修補都只能緩解、無法消除。

**$\lambda$、$\gamma$、$|G|$、$|E|$ 等超參數缺乏自適應機制**：論文用一組固定值（$\lambda=0.8$、$\gamma=0.9$、$|G|=4$、$|E|=8$、chunk size $=4$）跑所有 benchmark；Table 5 顯示 $r$ 和 $\lambda$ 對品質曲線扁平、對 memory 曲線陡峭。也就是說 STAC 的「memory budget」實際上是被 voxel 解析度與場景大小共同決定的、會隨場景而漂移，而不是真正受使用者控制的固定 budget。要把它部署到未知場景就需要每場景重新調參。

**Training-free 也意味著無法修補底層模型偏誤**：因為不重訓練，STAC 無法解決 Causal-VGGT 本身的歸納偏誤（例如某些 head 過度依賴 first frame 而在長序列遺忘中段重要 landmark）。論文把 first-frame 全保留視為設計，但這也會放大 first-frame 的偏誤，當第一幀品質差或視角偏離後續軌跡時會持續造成系統性錯誤。

### 7.3 Citations Worth Tracking

- **STream3R [16]（Lan et al., 2025）**：STAC 的主要 backbone，論文中 best-performing 變體都建立在它之上；理解 STAC 一定要先理解 STream3R 如何把 VGGT causalize。
- **VGGT [40]（Wang et al., 2025）**：所有 Causal-VGGT 變體的源頭，定義了 frame-as-token 的多 head 結構，是判斷「spatial / reference / landmark / camera」head 分工是否來自訓練或架構的關鍵原始文獻。
- **H2O [51]（Zhang et al., 2023）與 StreamLLM [47]（Xiao et al., 2023）**：STAC 的 anchor + sliding window 設計直接源於這兩篇 LLM 工作；判斷 STAC 的 3D-specific 創新要剝掉這兩篇的貢獻才能看清。
- **D2O [37]（Wan et al., 2024）**：similarity-weighted merging $\omega(\cdot, \cdot) = \exp(\cos_k(\cdot, \cdot))$ 與累積權重 $Z$ 直接借自 D2O，是判斷合併公式創新性的對照組。
- **Token Merging / ToMe [3]（Bolya et al., 2022）**：count-based attention bias $\log n$ 出自 ToMe；對 token merging 在 ViT 上的歷史脈絡有一篇就夠的入門。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 把 spatial cache 完全關閉、只保留 anchor + window + first-frame reference + voxel-aware retrieval（不做合併），重建品質會退化多少？這能直接量化「合併」相對於「結構化選擇」的邊際貢獻。
- [ ] 對 Causal-VGGT 直接套用 H2O / StreamLLM 而不引入 voxel 結構，得到的品質-記憶體 Pareto 曲線在哪？這是論文宣稱「3D 結構化 sparsity 比 LLM 通用方法好」的最直接缺失對照。
- [ ] 為何在 KITTI（outdoor, 大尺度）上 StreamVGGT-STAC 的 video depth $\delta<1.25$ 從 $72.2$ 退化到 $67.6$？是 voxel 解析度 $r=0.05$ 不適合 outdoor，還是 first-frame reference 在大位移下產生負面偏誤？
- [ ] Anchor token 的 attention score decay $\gamma=0.9$ 對應的有效記憶長度為 $1/(1-\gamma)=10$ 幀，但論文評估序列為 200–300 幀；長序列上是否需要 layer-dependent 或 head-dependent 的 $\gamma$？
- [ ] Chunk size 從 $1$ 到 $8$ 的 quality vs throughput 曲線形狀為何？chunk-causal 是否在 chunk 內部洩漏「未來資訊」進而高估 streaming 品質？
- [ ] Voxel cache 的 active voxel 數在 Fig. 10 上看似收斂，但 1500 幀後是否真的有上界？需要 5k+ 幀的 stress test 才能驗證 bounded memory 宣稱。
- [ ] First-frame 全保留的策略在第一幀視角極端（背向後續軌跡、過曝、模糊）時會發生什麼？論文所有 benchmark 的第一幀品質是否都偏好這個設計？

### 8.2 Improvement Directions

1. **Per-head sparsity-pattern 路由**（高可行性）：Fig. 2 顯示 spatial / reference / landmark / camera 四類 head 行為差異極大，但 STAC 對所有 head 套用同一個 $(|G|, |E|, \gamma, \lambda)$。把 head 依稀疏 pattern 分群、各群套用不同 budget 與 $\gamma$，可在不重訓練前提下進一步壓縮 —— 因為 reference head 幾乎只看 first frame，根本不需要 anchor budget。
2. **以 voxel 內方差為條件的自適應 $\lambda$**（中可行性）：補充材料 Fig. 6 顯示 intra-voxel similarity 平均為 $0.84$ 但長尾延伸到 $0.4$ 以下，固定 $\lambda=0.8$ 在低相似 voxel 中會頻繁丟入 $\mathcal{E}_u$ buffer。改為 $\lambda_u = \mu_u - \sigma_u$（voxel 內 cosine 分布的均值減一倍標準差），讓動態場景中的 voxel 自然提高合併門檻，可緩解作者承認的 dynamic scene 限制。
3. **時間不變性檢查作為合併 gate**（中可行性）：在 one-to-one merging 之前先檢查 incoming token 與既有代表 token 的 frame index 距離，若超過 threshold（例如 30 幀以上）則要求更高 cosine similarity 才允許合併。這直接針對「動態場景下 voxel 內容跨時間不一致」的問題。
4. **取代 Morton code 為 octree 動態解析度**（中可行性）：論文承認固定 voxel 解析度在 outdoor 不擴展，octree 結構可在地表稠密區用細解析度、空曠區用粗解析度，幾乎不增加 retrieval 成本（kNN 改為 hierarchical）。
5. **把 chunk-causal 顯式化為 streaming latency budget**（低可行性、需重訓練）：目前 chunk size $=4$ 等於用「4 幀延遲」換 GPU 利用率，但論文沒把這個 trade-off 暴露給使用者。可以引入動態 chunk（依 GPU 排隊狀態調整 chunk size），讓 STAC 在 latency-critical 場景退回 chunk size $=1$，在 throughput-critical 場景擴大到 chunk size $=8$+。
6. **與 LLM cache compression 的直接 head-to-head benchmark**（最重要、低工程成本）：把 H2O 與 StreamLLM 的選擇規則直接套到 Causal-VGGT 並評估，給出明確的 Pareto 曲線。即使 STAC 仍然贏，這個對照也讓 3D-specific 增益的量化可信度大幅提升。
