<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# SpatialStack — SpatialStack: Layered Geometry-Language Fusion for 3D VLM Spatial Reasoning

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | SpatialStack |
| Paper full title | SpatialStack: Layered Geometry-Language Fusion for 3D VLM Spatial Reasoning |
| arXiv ID | 2603.27437 |
| Release date | 2026-04-20 |
| Conference/Journal | arXiv preprint (CVPR 2026 listed on project page) |
| Paper link (abs) | https://arxiv.org/abs/2603.27437 |
| PDF link | https://arxiv.org/pdf/2603.27437 |
| Code link | — |
| Project page | https://spatial-stack.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Jian Zhang | Xiamen University (XMU) | https://jzh15.github.io/ | first author, equal contribution |
| Shijie Zhou | UCLA; Google | https://shijiezhou-ucla.github.io/ | co-first author, equal contribution |
| Bangya Liu | University of Wisconsin–Madison | https://pages.cs.wisc.edu/~bangya/ | co-first author, equal contribution |
| Achuta Kadambi | UCLA | https://visual.ee.ucla.edu/ | co-author (advisor, UCLA Visual Machines Group) |
| Zhiwen Fan | Texas A&M University (TAMU) | https://zhiwenfan.github.io/ | senior author |

### 1.2 Keywords

3D spatial reasoning, vision-language models, geometry-language fusion, hierarchical fusion, multi-level features, VGGT, embodied AI, multimodal LLM

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VG-LLM (Wu et al., ref [60]) | baseline | Single-layer geometry-vision fusion at patch level; reproduced as GVF-L23 baseline in this paper. |
| Spatial-MLLM (ref [50]) | predecessor | Dual-encoder VLM that fuses only final-layer vision and geometry features for spatial reasoning. |
| VLM-3R (ref [13]) | predecessor | Cross-attention based fusion of geometry encoder features into a VLM; deep-layer-only fusion. |
| VGGT (Wang et al., ref [46]) | base model | Visual Geometry Grounded Transformer used as the multi-view geometry encoder providing layer-wise features. |
| DeepStack (ref [36]) | influence | Inspires stacking of multi-level tokens directly into LLM decoder layers rather than the vision pathway. |
| Qwen2.5-VL / Qwen3.5 (refs [2], [43]) | base model | Open-source VLM backbones on which VLM-SpatialStack is instantiated. |
| DUST3R / CUT3R (refs [48], [47]) | influence | Feed-forward multi-view geometry transformers establishing the encoder family used by SpatialStack. |

## 2. Research Overview

### 2.1 Research Topic

本文針對大型視覺語言模型（VLM）在 3D 空間推理上的可靠性瓶頸，特別是其無法捕捉細粒度 3D 幾何與空間關係的根本問題。作者觀察到既有將多視角幾何 transformer（如 VGGT、DUST3R、CUT3R）整合進 VLM 的方法（Spatial-MLLM、VG-LLM、VLM-3R 等），普遍只融合幾何編碼器最後一層的特徵，因而丟棄中間層所蘊含的層次化幾何訊號，造成空間理解的結構性瓶頸。為此，本研究提出 SpatialStack——一種通用的分層幾何—語言融合（layered geometry-language fusion）框架，將幾何編碼器多個層次的特徵透過層特定 projector 對齊後，依序殘差注入 LLM decoder 的前幾層，於整個解碼過程中逐步累積由淺到深的幾何上下文。基於此框架，作者以 Qwen3.5／Qwen2.5-VL 為骨幹打造 VLM-SpatialStack，並於 VSI-Bench、SPAR-Bench、BLINK-Spatial、CV-Bench 等多項 3D 空間推理基準上達到 SOTA 表現，展現多層次融合對於低階幾何感知與高階空間推理之兼容能力。

### 2.2 Domain Tags

- computer vision
- multimodal learning
- vision-language models
- 3D scene understanding
- embodied AI

### 2.3 Core Architectures Used

- **SpatialStack（本文提出）**：通用的 layered geometry-language fusion 框架，將幾何編碼器多個層次的 patch features 透過 layer-specific projector 對齊後，以殘差方式依序注入 LLM decoder 的前幾層（layers 0、1、2），形成 layer-to-layer 的幾何—語言對應。
- **VLM-SpatialStack（本文提出）**：SpatialStack 的具體實例化，以 Qwen3.5（主要版本）與 Qwen2.5-VL（用於與既有 baseline 公平比較）作為 VLM 骨幹，並搭配凍結的 VGGT 幾何編碼器與可訓練的 geometry token merger 模組。
- **VGGT（沿用）**：作為多視角幾何編碼器，從未校正的多視角影像直接抽取 layer-wise 幾何特徵（取第 11、17、23 層的 patch tokens），於本文中保持凍結並僅作為特徵提供者。
- **Qwen3.5 / Qwen2.5-VL（沿用）**：作為 VLM backbone，提供 vision encoder 與 LLM decoder；訓練時 vision encoder 凍結，僅微調 fusion 模組與 LLM decoder。
- **DeepStack 範式（啟發來源）**：啟發本文將多層 tokens 直接堆疊注入 LLM decoder 的設計，但 SpatialStack 將堆疊對象從 visual tokens 改為 geometry tokens 並改注入語言端而非視覺端。
- **GVF 基線架構（對照組）**：本文重現的 Geometry-Vision Fusion 設定，將單層或多層幾何特徵加到 vision encoder 最後一層特徵後再送入 LLM，等同於 VG-LLM 的設計，用以對照 SpatialStack 的優勢。

### 2.4 Core Argument

作者主張既有 VLM 之所以在 3D 空間推理上失準，根因並非缺乏幾何輸入，而在於「融合層級錯位」：現有方法把幾何編碼器最後一層特徵與視覺 token 拼接，丟棄了中間層中對精細幾何邊界至關重要的訊號。透過 patch-wise 相似度可視化（Fig. 2 左側 heatmap）可見淺層特徵保留銳利的局部幾何邊界，而深層特徵則過度同質化，難以區分物理結構不同但語意相近的區域。進一步以 SPAR 任務難度層級進行定量分析（Fig. 4、Tab. 1）發現，注入幾何編碼器第 11 層對低階任務（深度、距離比較）最佳，注入第 23 層對高階任務（跨視角推理）最佳——層深與任務層級之間存在相反的單調趨勢。然而，若簡單把多層幾何特徵在「視覺 pathway」上相加，反而導致特徵彼此干擾，整體表現低於任一單層融合。據此，作者提出三項邏輯上必要的設計選擇：(1) 把融合從視覺端移至語言端，利用 LLM decoder 多層結構天然具備容納多尺度訊號的容量；(2) 受 DeepStack 啟發，以殘差方式將不同層次的幾何特徵分別注入 decoder 的前幾層（layers 0、1、2），形成層對層的幾何—語言對應；(3) 凍結視覺與幾何編碼器、僅訓練融合模組與 LLM，以保留預訓練表示並學會跨模態對齊。實驗顯示 SpatialStack 在四項基準的整體分數均優於單層或視覺端多層融合，且具更佳的跨任務泛化能力，從而論證分層幾何—語言融合相較於傳統晚期視覺—幾何融合的根本性優勢。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「SpatialStack: Layered Geometry-Language Fusion for 3D VLM Spatial Reasoning」就把整篇論文的核心定位寫死：這不是又一個新的 3D encoder，也不是新的 dataset，而是一個「分層的 geometry-language 融合策略」。重點落在 *layered* 與 *fusion* 兩個字，預示後文會強調「多層」對比「單層」。

Abstract 採用四段式骨架。第一句先確立問題：VLMs 在 reliable 3D spatial reasoning 上仍不可靠，而這是 embodied / physical AI 的 core capability，藉此把研究價值拉到應用層級。第二句把問題收斂到 root cause：模型抓不到 fine-grained 3D geometry 與 spatial relationships。

第三段點出現有 multi-view geometry transformer 整合方案的共同盲點——它們只 fuse final-layer 的 vision-geometry features，丟掉了 hierarchical signals，因此構成 bottleneck。這句話既總結 related work 的限制，也直接鋪陳自家方法的差異化主張。

第四段提出 SpatialStack 作為對策：progressively align vision、geometry、language across the model hierarchy；並基於這個框架實作 VLM-SpatialStack，宣稱在多個 3D spatial reasoning benchmarks 上達到 SOTA。

整段 Abstract 的故事邏輯是：應用需求 → VLM 痛點 → 既有方案的 architectural bottleneck → SpatialStack 的 layered 解法 → 實證與通用化承諾，為 §1 Introduction 鋪好「為何 layered fusion 才是正確問法」的伏筆。

### 3.2 Introduction

(820 words)

Introduction 的論述脊椎是「動機 → 既有方案分類 → 共同侷限 → 本論文的關鍵觀察 → 解法與貢獻」。

第一段先把 spatial reasoning 拉高到 embodied agents 的 cognitive bridge，然後迅速把鏡頭收到 VLM 的 failure modes：估不準 relative distance（引 [28, 51]）、在動態場景中分不清 left/right（引 [65]）。這些具體 failure 同時為後續 low-level vs. high-level 任務劃分留伏筆。

第二段拋出全文的 framing question：*How can vision–language–geometry be effectively unified in VLMs to enable reliable spatial reasoning?* 接著用兩條既有路線回答：(i) 注入 explicit geometric inputs（3D-LLM、LEO、LLaVA-3D、Video-3D LLM）需要外部點雲/深度，限制應用；(ii) 接上 end-to-end multi-view geometry transformer（DUST3R、CUT3R、VGGT）+ VLM（Spatial-MLLM、VLM-3R、VG-LLM），不需傳統 SfM 流程。這個分類為 §2 Related Work 的章節結構直接定錨。

第三段挑出第二類路線的共同毛病：只 fuse geometry encoder 的 final-layer feature。這裡作者帶入一個技術根據——多數 geometry encoder 採 DPT 架構，本身就被設計來提取 multi-level representation；只取最後一層等同於把 hierarchical cues 丟掉。同時作者把 spatial tasks 的「hierarchical 本質」（從 depth estimation 到 goal-directed planning）並列，論證 single-level fusion 必然構成 bottleneck。這一段把問題從工程瑕疵升級為 architectural mismatch。

第四段公布本文的研究取徑：systematically study how fusion layers across vision encoders、geometry encoders、LLM decoders 影響 multimodal spatial reasoning。並預告主要發現——geometry-language fusion 與 vision encoding 一樣呈現 hierarchical pattern：shallow features 利於 fine-grained perception、deeper features 支撐 high-level reasoning。這個發現是後文 §3 量化分析的中心結論，也是整個 layered 解法的依據。

第五段正式介紹 SpatialStack：a general hierarchical fusion framework，不再只在 deep encoder layers 做 fusion，而是 progressively align geometry 與 language representations across model hierarchy，同時抓 local geometry 與 global semantics。這裡用 Fig. 1 對比 (a) conventional vision-geometry fusion 與 (b) SpatialStack 的 layered injection，視覺上把「stack」這個動作說清楚。

最後一段條列三點貢獻：(1) 第一個系統性的 layer-wise study，揭示 hierarchical geometry-language correspondence；(2) 提出 SpatialStack 這個 model-agnostic、超越 final-stage fusion 的框架；(3) 以 Qwen 系列為基底實作 VLM-SpatialStack 並在多個 benchmark 達 SOTA。這三點剛好對應後續的 §3（分析）、§4（方法）、§5（實驗），形成緊湊的章節伏筆，為 §2 Related Work 過渡做好準備。

### 3.3 Related Work / Preliminaries

(610 words)

Related Work 分為三個小節：MLLMs、Spatial Reasoning in VLMs、Vision-Language-Geometry Fusion。論述順序刻意從「general → spatial-specialized → geometry-aware」逐步收斂，最終在第三小節揭露本文要對抗的 architectural pattern。

第一小節 *Large Multimodal Models* 從 CLIP 的 contrastive 預訓練，到 Flamingo、BLIP/BLIP-2 的 bridging architecture，再到 InstructBLIP、LLaVA、MiniGPT-4、Qwen2.5-VL 帶起的 visual instruction tuning 路線。作者在這裡不是純粹做歷史回顧，而是著力強調這條路線確立了一個「only fuse final-layer visual features with the language backbone」的 paradigm。並引用最近的批判性分析 [22, 37, 42]，指出此 paradigm 偏向 semantic alignment、捕捉不到 fine-grained spatial / geometric structure。這一段為第三小節的批評埋下伏筆。

第二小節 *Spatial Reasoning in VLMs* 先列出量化此弱點的 benchmark：VSI-Bench、Spar Bench、BLINK、Cambrian-1、Cambrian-S 的 implicit 3D cognition 不足，以及 VLM4D 的 4D 動態挑戰。接著把回應這些缺口的工作分成兩條路線：(i) 注入 explicit 3D data（3D-LLM、LLaVA-3D、Video-3D LLM）；(ii) 改進 training paradigm（Spatial-SSRL 的 self-supervised RL、Visual Spatial Tuning 的 dataset 與 progressive pipeline）。作者明確指出後者是 *training objectives and data augmentation* 路線，而非 fusion architecture 本身——再次為自家「動 architecture」的定位讓路。

第三小節 *Vision-Language-Geometry Fusion* 是真正的 contrast section。先肯定 DUST3R series、CUT3R、VGGT 等 feed-forward geometry encoder 的進展，再把後續工作切成兩個 fusion 範式：(a) 建構 explicit spatial-semantic representation（distill 2D feature 到 3D/4D feature field、queryable 3D world model、語意 radiance field）；(b) implicit 將 geometric prior 融進 MLLM 的 latent space，本論文歸屬於後者。作者點名 Spatial-MLLM 的 dual-encoder、VG-LLM 的 patch-level fusion、VLM-3R 的 cross-attention、SSR 的 rationale-guided fusion，並下重話：*these integrations typically fuse only the final-layer features from the geometry and vision encoders*，因此丟失 intermediate layers 的 hierarchical cues、形成 fine-grained spatial reasoning 的 bottleneck。

收尾一句把矛頭指向自家方法：SpatialStack 直接針對此限制，提出 hierarchical fusion 並 progressively align multi-level geometry features 與 language backbone。這段為 §3 的 layer-wise 分析（為何 multi-level features 必要）提供了正當性，並預告 §4 將給出「在 language side 做 stacking」的具體解法。

### 3.4 Method (overview narrative)

(560 words)

論文的方法論呈現分為兩個敘事階段：§3 *How Multi-level Geometry Features Facilitate Spatial Reasoning*（先用 analysis 立論）與 §4 *Where to fuse Multi-level Geometry Features*（再給架構答案）。先 analysis、後 architecture 的安排，使 SpatialStack 的設計選擇看起來是經驗證據驅動，而不是憑空。

§3 先做 *qualitative analysis*：取 geometry encoder 不同層的 token，unflatten 回 H×W 空間佈局，挑一個 ROI patch 計算 patch-wise similarity heatmap。觀察結論直接支撐後文設計：shallow layer 保留 sharp local structures 與清晰幾何邊界，deeper layer 出現 *overly homogeneous activations*——也就是物理上不同的區域在 latent 中卻被映成相似。這提供「deep-only fusion 為何失準」的直觀理由。

接著 *quantitative analysis* 沿 SPAR 的 cognitive 三層分類，把任務切成 low-level（perception，BLINK relative depth、SPAR 的 Depth/Distance OC/OO/MV 變體）與 high-level（VSI-Bench 全集），刻意跳過 medium 與 high 以做出乾淨的兩極對比。實驗以 GVF（geometry-vision fusion）為 protocol：抽 VGGT 第 4/11/17/23 層特徵，projector 投影後加到 vision encoder 末層，再餵 LLM。Fig. 4 呈現的趨勢構成全文的核心發現——*shallow layers 利 low-level perception、deep layers 利 high-level reasoning*；layer 11 在 low-level 達峰，layer 23 在 high-level 達峰，兩種需求落在不同深度。

接著 §3 反向確認「天真 multi-layer 加總」並非萬靈丹：Tab. 1 顯示直接把多層幾何特徵都丟進 vision pathway，反而比單層 11 的 low-level 與單層 23 的 high-level 都差，呈現 *feature interference rather than synergy*。這個負結果是整章最關鍵的轉折，把問題從「要不要多層」推進到「在哪裡多層」。

§4 接棒回答 *where*。作者主張：vision pathway 容量有限、易產生 interference；LLM decoder 提供更彈性的高容量空間做 multi-scale 對齊。受 DeepStack 在 LLM 內 stack visual tokens 的成功啟發，他們把 geometry 整合搬到語言端，提出 SpatialStack——把 geometry encoder 多層特徵分別注入 LLM decoder 對應層，形成幾何表徵的 hierarchy。

§4 同時宣告 SpatialStack 是 model-agnostic 框架，並以 Qwen3.5 為主、Qwen2.5-VL 為對照實作 VLM-SpatialStack，以與既有 baseline 公平比較。整個方法章透過 *qualitative → quantitative → 反例 → 解法* 的鋪陳，把「為何 layered、為何在 LLM 端 layered」兩個問題都答清楚，為 §5 的詳細模組設計（geometry encoder、token merger、masked additive fusion、optimization）做好上層敘事鋪墊。

### 3.5 Experiments (overview narrative)

(540 words)

實驗章遵循「設定 → 主結果 → 一般能力 → ablation → 跨 benchmark 對照」的標準骨架，但每一節都有特定論證任務，而不只是堆 benchmark。

§5.1 交代 training setup：dataset 由 SPAR、LLaVA-Hound（皆來自 VG-LLM 的釋出子集）、VLM-3R 的 ScanNet split，加上 VSI-590K 中的 appearance-order 子集組成，總量約 200k。作者強調 dataset 在 spatial reasoning 類型上的廣度，以及 3D 幾何與文字描述間的 alignment。Optimization 使用 AdamW、batch size 64、lr 1e-5、cosine schedule、warmup 0.03；instruction tuning 期間 *vision encoder 與 VGGT geometry encoder 都凍結*，僅訓練 geometry token merger 與 LLM decoder。這些設定是後續比較公平性的基礎。

§5.2 主結果分三條線。第一條是 VSI-Bench：超過 5,000 條來自 egocentric indoor video 的 QA，混合 MCA 與 NA。Tab. 3 是全文最重的單一表，把比較拆成 proprietary（GPT-4o、Gemini-2.5 Pro）與 open-source 兩塊。在 open-source 下，SpatialStack-5B (Qwen3.5) 取得 67.5 的整體第一，超越 Cambrian-S-3B、Qwen3.5-4B、VG-LLM-4B、Spatial-MLLM-4B；而為了公平對照，作者另出一版 SpatialStack-4B (Qwen2.5)，在同一 base model 下也勝過 Spatial-MLLM、VG-LLM、Cambrian-S，論證 SpatialStack 的 *paradigm-level* 增益不是靠換更強的 base。Route Plan 雖無對應訓練資料卻仍領先所有 open-source，被作者解讀為 *zero-shot generalization* 的證據。

第二條 §5.2 是 CV-Bench（Tab. 4），測 2D / 3D 空間感知。SpatialStack 兩個版本在 2D、3D 子集都贏過同尺度 baseline 與同 base model 對照，凸顯 multi-level geometry stacking 在 unified spatial perception 上的好處。第三條是 General-purpose Capabilities（Tab. 5）：在 MMBench、Video-MME、BLINK、TempCompass 上整體成績與 Qwen3.5-4B 持平、各有勝負，作者用此論證 *no catastrophic forgetting*——即專精 spatial reasoning 不以犧牲一般 multimodal 能力為代價。

§5.3 Ablation 鎖定兩個會被審稿質疑的點。其一 *VGGT layer selection*（Tab. 6）：把 L23 換成 L21 或 L22，無論單層或多層組合都沒顯著差異，論證關鍵在 *broad sampling across depth* 而非具體哪一層。其二 *geometry-language fusion order*（Tab. 7）：對比 progressive 對齊（Geo-L11→LLM-L0、L17→L1、L23→L2）與反序版本及 vision fusion baseline，progressive 版本在 4 個 benchmark 中贏 3 個並拿下整體第一，支持 hierarchical 對齊是 *方向性* 的設計。

整章故事邏輯是：先證明 SOTA、再證明同 base 公平比也贏、再證明沒丟一般能力、最後用 ablation 排除「只是隨便挑層」與「順序無所謂」兩種反論，為 §6 的結論收尾鋪好台階。詳細表格分析留給 §6（合併文件中的 §6）展開。

### 3.6 Conclusion / Limitations / Future Work

(140 words)

Conclusion 採高度濃縮的單段寫法，沒有獨立的 Limitations 與 Future Work 小節。作者先重申命題：SpatialStack 是 *hierarchical fusion framework*，目的在橋接 vision、geometry、language for robust 3D spatial reasoning。隨後濃縮 §3 的核心發現——shallow geometry layer 保留 fine-grained spatial detail、deeper layer 提供 global semantic context；並重申那個關鍵反例：*naive multi-layer geometry-vision fusion 會造成 structural bottleneck，產生 feature interference 而非 synergy*。

接著把 SpatialStack 的解法定位為「將多層幾何特徵 progressively 對齊到 LLM decoder」，從而同時保住 local precision 與 high-level relational semantics。實證層面再次強調 SOTA among open-source、強 zero-shot generalization、以及不犧牲 general multimodal capability。

收尾的願景句把 SpatialStack 拔高為 *vision-language-geometry integration 的新 paradigm*，並指向 physical 3D world 中 truly understand and act 的 AI 系統。文中沒有明確列出 limitations、failure mode、或具體 future work 方向（例如更大尺度、real robot deployment、dynamic / 4D 任務的延伸），這是該 conclusion 的明顯缺項；the paper does not specify 後續路線圖的具體計畫，只以願景句帶過。對讀者而言，這意味著 limitations 與 future work 需要從 §3 的任務分類限制（醫只比 low/high 兩極、跳過 medium）與 §5 訓練資料規模（約 200k、缺 route plan 監督）反推，而非由作者主動標註。

## 4. Critical Profile

### 4.1 Highlights

- SpatialStack-5B (Qwen3.5) 在 VSI-Bench 達 overall 67.5%，於所有 open-source 模型中排名第一，並超越 GPT-4o 的 34.0% (Tab. 3, p. 7)。
- 在 cross-benchmark ablation 中同時於 VSI-Bench、SPAR-Bench、CV-Bench 上勝過 GVF-L23 與 GVF-L11/17/23 baseline，overall 從 68.43 提升至 69.14 (Tab. 2, p. 6)。
- 在 CV-Bench 上達 85.5% overall，其中 3D subset 達 92.2%，超越同樣以 Qwen3.5-4B 為底的 baseline (90.2%) (Tab. 4, p. 8)。
- Fig. 4 (p. 5) 透過注入 VGGT 單一層 (4/11/17/23) 的消融，揭示 low-level task 在 layer 11 達峰值 66.11、high-level 在 layer 23 達峰值 66.36，呈現相反的單調趨勢。
- Tab. 1 (p. 5) 發現視覺端 naive multi-layer fusion (overall 64.92) 反而低於單層 layer-23 注入 (65.35)，作為提出語言端融合的關鍵動機。
- Fig. 2 (p. 3) 與 Fig. C (p. 16) 的 patch-wise similarity heatmap 視覺化顯示淺層 VGGT 特徵保留銳利幾何邊界、深層則出現語意同質化現象。
- 在 VSI-Bench 的 Route Plan 任務上，於缺乏對應訓練資料的情況下仍達 41.2%，超越所有 open-source baseline，展現 high-level zero-shot 推理 (Tab. 3, p. 7)。
- Tab. 7 (p. 8) 的 fusion order ablation 顯示 progressive 配對 (Geo-L11→LLM-L0, ...) 在 4 項 benchmark 中 3 項勝過 reverse 配對。
- 訓練時凍結 vision encoder 與 VGGT geometry encoder，僅更新 LLM decoder 與 fusion modules，於 32 張 A100、effective batch 64、~200k 樣本、1 epoch 內完成 (Sec. 4.2 與 Tab. B, p. 15)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 文中承認 base Qwen3.5 在 BLINK-Spatial 上仍為最強，naive geometry-vision fusion 兩個 baseline 在此基準上「suffer severe performance drops」(Sec. 4.3, p. 6)。
- 文中說明 VGGT layer 4 因「insufficient network depth」於前期實驗效果不佳而被排除於選層範圍 (Sec. 5.3, p. 8)。
- 除上述兩處外，paper 並無獨立的 limitations 段落；其他結構性問題未公開討論。

#### 4.2.2 Phyra-inferred

- **Tab. 5 BLINK 退步 5.66 pt 與「no catastrophic forgetting」聲稱矛盾**：SpatialStack-5B 在 BLINK 從 61.12 降至 55.46 (Tab. 5, p. 8)，paper 卻在同表結論強調「maintains robust general capabilities ... no catastrophic forgetting」，但 BLINK 本身就是空間感知 benchmark，這個退步反而最不該被忽略。
- **Tab. 7 progressive vs reverse overall 差距僅 0.62 pt**：Reverse 配置 overall 為 68.52，與未加幾何的 Qwen3.5 fine-tuned 完全相同，而 SpatialStack final 為 69.14；paper 卻將此差距詮釋為「hierarchical alignment is optimal」，無多 seed 重複難以排除單次訓練 noise。
- **GVF-L11/17/23 baseline 設計上偏 strawman**：直接將三層幾何特徵相加後注入視覺 pathway 的單一融合點，未配備 layer-specific projectors（與 SpatialStack 設計不對等），「feature interference」幾乎是必然結果；公平對照應採視覺端配備 layer-specific projectors 的多層融合。
- **Tab. 6 (p. 8) 顯示 layer 21/22/23 幾乎可互換**：paper 自承「broad sampling across network depth is more critical than specific layer indices」，這實際削弱了 Sec. 3 對「layer-task hierarchy」的精細描述，意味 Fig. 4 的單層差異可能部分源於 noise 而非結構性對應。
- **僅在 LLM decoder 最前三層 (0, 1, 2) 注入幾何**：paper 主張 progressive alignment，卻未消融注入中段或後段 decoder layer (例如 layer 12 或 23) 的效果；其論述的「shallow geo→shallow LLM, deep geo→deep LLM」對應在 LLM 側只用了「shallow LLM」一段，並不對稱。
- **Tab. 7 Vision Fusion baseline (68.38) 反而低於未動 Qwen3.5 (68.52)**：暗示視覺端注入幾何幾乎沒有幫助，SpatialStack 主要勝過的是「不做幾何融合」與訓練擾動，並非「正確設計的視覺端融合」。
- **缺乏跨 backbone 驗證 model-agnostic 聲稱**：paper 宣稱「SpatialStack ... can be applied to any open-source VLM」(Sec. 4.1, p. 5)，但實作只涵蓋 Qwen2.5-VL 與 Qwen3.5，沒有 LLaVA、InternVL 等其他家族的支持證據。
- **訓練資料 14.7% 來自 VLM-3R ScanNet split** (Tab. A, p. 14)：與 VSI-Bench 同源於 ScanNet 系列場景，存在 distribution overlap 風險，paper 未進行 leakage 檢查。

### 4.3 Phyra's Judgment (summary)

真正新的，是把多層幾何特徵以 layer-specific projector 對齊後 residual 注入到 LLM decoder 的設計選擇，加上一份 Sec. 3 的 layer-task 對應分析；其餘多為已有元件 (VGGT、Qwen、DeepStack 風格 stacking) 的工程組合。論文最薄弱之處在於關鍵聲稱的支撐證據不足：與 Qwen3.5 fine-tuned baseline 的 overall gap 僅 0.62 pt、reverse ordering 與 final ordering 差距同樣只有 0.62 pt，且 BLINK 上反而退步 5.66 pt，卻被概括為「no catastrophic forgetting」。核心未解問題是 gain 究竟來自 architecture (層對層 progressive alignment) 還是 training-data engineering，paper 提供的對照組設定不足以分離兩者。

## 5. Methodology Deep Dive

### 5.1 Method Overview

SpatialStack is a layered geometry–language fusion framework that augments a standard VLM with multi-level geometric features extracted from a frozen multi-view geometry transformer. Given $K$ uncalibrated input frames $\{I_k \in \mathbb{R}^{H \times W \times 3}\}_{k=1}^{K}$ and an instruction text $q$, the system produces a textual answer that grounds spatial reasoning in 3D structure. Two parallel encoders process the same input frames: a frozen vision encoder (Qwen2.5-VL or Qwen3.5 native ViT) yields semantic patch tokens that are spatial-merged and concatenated with text tokens to form the LLM input $H_0$, while a frozen multi-view geometry encoder (VGGT, 24 transformer layers) emits per-layer geometric features that capture progressively abstracted 3D structure (from sharp local boundaries at shallow layers to global multi-view context at deep layers, as motivated by the patch-similarity analysis in Fig. 2 left and §3).

The core innovation is the routing of geometry features. Rather than late-stage vision–geometry fusion (concatenating only the final VGGT layer with vision tokens, as in VG-LLM and Spatial-MLLM), SpatialStack extracts patch features from VGGT layers $\{11, 17, 23\}$, processes each through a dedicated, layer-specific token merger $M^{(l_i)}_{\text{geo}}$ that performs RMSNorm, window-wise spatial merging (window size $s \times s$, $s=2$) and a linear projection to the LLM hidden dimension $D_{\text{lang}}$, then adds the resulting tensors as residuals to the visual-token slice of LLM decoder hidden states at layers $\{0, 1, 2\}$ via masked additive fusion (Eq. 5). The mapping is progressive: shallow VGGT layer 11 to LLM layer 0, middle layer 17 to LLM layer 1, deep layer 23 to LLM layer 2; this ordering is shown empirically optimal in the ablation (Tab. 7).

The remaining LLM decoder layers $\{3, \ldots, L\}$ proceed unchanged, eventually producing the final hidden representation $H_L^{\text{llm}}$ used for next-token prediction. Crucially, both the vision encoder and the geometry encoder are kept frozen during instruction tuning; only the layer-specific geometry token mergers and the LLM decoder are trainable, optimised under a single next-token cross-entropy objective (Eq. 6) without any auxiliary losses. This design preserves pretrained 2D and 3D representations while letting the LLM learn to align and integrate them across the model hierarchy, yielding state-of-the-art results on VSI-Bench, SPAR-Bench, BLINK-Spatial and CV-Bench (Tab. 3, Tab. 4).

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: K multi-view frames {I_k}             [B, K, 3, H, W]
       Text instruction tokens T_txt          [B, M]
   │
   ├──> Vision Encoder (frozen, ViT)
   │       per-frame patch tokens V_k         [B, K, N,  D_vis]   (N = (H/p)(W/p))
   │       └─ Spatial Merger (stride s=2)
   │              per-frame merged ~V_k       [B, K, N', D_lang]  (N' = N/s² = N/4)
   │              concat over K frames        [B, K·N',  D_lang]
   │
   ├──> Tokenizer (trainable embeddings)
   │       text tokens T                       [B, M, D_lang]
   │
   ├──> Geometry Encoder VGGT (frozen, 24 transformer layers)
   │       per-view init Z₀^(k) = [c_k; r_k; p_k]
   │              (1 camera + R register + N patch)
   │              concat over K views          [B, K·(1+R+N), D_geo]
   │       layer-wise hidden states  Z_l       [B, K·(1+R+N), D_geo]   l ∈ {0,...,23}
   │       extract patch tokens (drop camera + register) at l ∈ {11, 17, 23}
   │              Z_{11}, Z_{17}, Z_{23}       [B, K·N, D_geo]
   │
   ├──> Layer-specific Geometry Token Mergers (trainable)
   │       M^(11)_geo : RMSNorm → window-merge(s×s) → Linear(D_geo·s² → D_lang)
   │              G_{11}                      [B, K·N', D_lang]
   │       M^(17)_geo                         [B, K·N', D_lang]
   │       M^(23)_geo                         [B, K·N', D_lang]
   │
   ├──> Build multimodal sequence
   │       H₀ = [~V ; T]                       [B, K·N' + M, D_lang]
   │
   └──> LLM Decoder (trainable, L layers)
          H^(0)' = H₀ + masked_add(G_{11}, V-slice)
          H^(1)  = f_llm^1(H^(0)')             [B, K·N' + M, D_lang]
          H^(1)' = H^(1) + masked_add(G_{17}, V-slice)
          H^(2)  = f_llm^2(H^(1)')             [B, K·N' + M, D_lang]
          H^(2)' = H^(2) + masked_add(G_{23}, V-slice)
          H^(3..L) = f_llm^L ∘ ... ∘ f_llm^3(H^(2)')
          Output  H_L^llm                      [B, K·N' + M, D_lang]
              └─ next-token logits             [B, K·N' + M, |V|]
```

Notation: `B` = batch, `K` = views per sample, `p` = ViT patch size (16), `s` = spatial merge stride (2), `R` = VGGT register-token count (paper does not specify; marked as `?` in §5.3.2), `D_vis`, `D_geo`, `D_lang` = encoder hidden sizes (paper does not specify exact integer values for the SpatialStack-5B variant).

### 5.3 Per-Module Breakdown

#### 5.3.1 Vision Encoder + Spatial Merger

**Function:** Encode each input frame into language-aligned patch tokens, then halve spatial resolution through a 2×2 merger before LLM ingestion.

**Input:**
- Name: $\{I_k\}_{k=1}^{K}$
- Shape: `[B, K, 3, H, W]`
- Source: raw RGB multi-view frames sampled from the input video or image set

**Output:**
- Name: $\tilde{V}$
- Shape: `[B, K·N', D_lang]`, with $N' = HW/(p \cdot s)^2$
- Consumer: concatenated with text tokens to form $H_0$, fed to LLM decoder

**Processing:**

Each frame $I_k$ is split into non-overlapping $p \times p$ patches and embedded by the frozen ViT to produce $V_k \in \mathbb{R}^{N \times D_{\text{vis}}}$ with $N = (H/p)(W/p)$. The Qwen2.5-VL pipeline applies window-attention plus hierarchical patch merging; the Qwen3.5 backbone is used in the SpatialStack-5B configuration. A spatial merger then groups every $2 \times 2$ neighbouring patches and projects them to $D_{\text{lang}}$, producing $\tilde{V}_k \in \mathbb{R}^{N' \times D_{\text{lang}}}$. The merged tokens of all $K$ frames are concatenated along the sequence dimension.

**Key Formulas:**

$$
\tilde{V} = [\tilde{V}_1; \ldots; \tilde{V}_K] \in \mathbb{R}^{(K \cdot N') \times D_{\text{lang}}}
$$

**Implementation Details:**

The vision encoder is **frozen** during instruction tuning to preserve pretrained semantic representations. The spatial merger and any projection layers within it are considered part of the vision pathway in Qwen2.5-VL/Qwen3.5; the paper does not specify whether they are tuned or frozen separately. Patch size $p = 16$ is inherited from the backbone; the merger stride is $s = 2$.

#### 5.3.2 Geometry Encoder (VGGT)

**Function:** Produce multi-view geometric features at multiple abstraction levels from the same $K$ input frames.

**Input:**
- Name: $\{I_k\}_{k=1}^{K}$
- Shape: `[B, K, 3, H, W]`
- Source: same RGB frames as the vision encoder

**Output:**
- Name: $\{Z_{11}, Z_{17}, Z_{23}\}$ (patch-token outputs at selected aggregator layers, after dropping camera/register tokens)
- Shape: each `[B, K·N, D_geo]`
- Consumer: layer-specific geometry token mergers $M^{(l_i)}_{\text{geo}}$

**Processing:**

For each view $k$, VGGT builds the initial token sequence as the concatenation of one camera token $c_k$, $R$ register tokens $r_k$, and $N$ patch tokens $p_k$. View-specific sequences are concatenated and processed jointly through 24 stacked transformer layers (Eq. 3). Unlike the original VGGT pipeline, the DPT prediction heads are not used; instead, hidden states from layers $l \in \{11, 17, 23\}$ are retained and stripped of camera and register tokens, leaving only the per-patch geometric features. The choice of layers (skipping the very shallow layer 4 found ineffective in preliminary tests, see §5.3 of the paper) provides a representative spread of shallow, middle and deep abstraction.

**Key Formulas:**

$$
Z_0^{(k)} = [c_k; r_k; p_k] \in \mathbb{R}^{(1+R+N) \times D_{\text{geo}}}
$$

$$
Z_L = f^{\text{geo}}_L \big( f^{\text{geo}}_{L-1} \cdots f^{\text{geo}}_1 \big( [Z_0^{(1)}; \ldots; Z_0^{(K)}] \big) \big)
$$

**Implementation Details:**

VGGT is kept **frozen** in evaluation mode during both training and inference to preserve learned 3D priors. The number of register tokens $R$, the geometry hidden size $D_{\text{geo}}$, and the precise patch size used by VGGT are not stated in the paper text; the source repository for VGGT is cited as the canonical reference.

#### 5.3.3 Geometry Token Reordering & Spatial Alignment

**Function:** Reorder VGGT patch tokens so that consecutive groups of $s^2$ tokens correspond to the same spatial region as a single merged vision token, ensuring cross-modal spatial alignment before fusion.

**Input:**
- Name: $Z_{l_i}$ (per VGGT layer)
- Shape: `[B, K·N, D_geo]`, stored in flat row-major order over $(h_{\text{patch}}, w_{\text{patch}})$
- Source: extracted layer outputs from §5.3.2

**Output:**
- Name: $Z_{l_i}^{\text{reord}}$
- Shape: `[B, K·N, D_geo]` (same tensor count, different traversal order)
- Consumer: Geometry-to-Language Projector $M^{(l_i)}_{\text{geo}}$ (§5.3.4)

**Processing:**

The grid $(h_{\text{patch}}, w_{\text{patch}})$ is partitioned into $s \times s$ windows, then re-permuted so that window indices come before within-window positions, and finally flattened back into a 1D sequence. Concretely:

1. Reshape: $(h_{\text{patch}}, w_{\text{patch}}) \to (h_{\text{patch}}/s,\; s,\; w_{\text{patch}}/s,\; s)$
2. Permute: $\to (h_{\text{patch}}/s,\; w_{\text{patch}}/s,\; s,\; s)$
3. Flatten to 1D of length $h_{\text{patch}} \cdot w_{\text{patch}}$

This window-major traversal mirrors the spatial-merger ordering on the vision side, so that subsequent window-wise pooling consumes geometry tokens that cover the same spatial footprint as the corresponding merged vision token.

**Key Formulas:**

$$
(h_{\text{patch}}, w_{\text{patch}}) \;\to\; \big(\tfrac{h_{\text{patch}}}{s}, s, \tfrac{w_{\text{patch}}}{s}, s\big) \;\to\; \big(\tfrac{h_{\text{patch}}}{s}, \tfrac{w_{\text{patch}}}{s}, s, s\big) \;\to\; h_{\text{patch}} \cdot w_{\text{patch}}
$$

**Implementation Details:**

The reordering is purely a shape/permutation operation and adds no learnable parameters. Window size $s = 2$ is shared with the vision-side spatial merger.

#### 5.3.4 Layer-specific Geometry-to-Language Projector $M^{(l_i)}_{\text{geo}}$

**Function:** Normalise, spatially merge and linearly project geometry tokens of each selected VGGT layer into the LLM hidden space, with **independent parameters per layer** so that shallow, middle and deep cues retain distinct semantics.

**Input:**
- Name: $Z_{l_i}^{\text{reord}}$
- Shape: `[B, K·N, D_geo]`
- Source: §5.3.3 reordered tokens

**Output:**
- Name: $G_{l_i}$
- Shape: `[B, K·N', D_lang]`, with $N' = N/s^2$
- Consumer: residual injection into LLM decoder layer $j$, where $j = i - 1$ (i.e. $G_{11} \to $ layer 0, $G_{17} \to$ layer 1, $G_{23} \to$ layer 2)

**Processing:**

Token-wise RMSNorm is applied first, following the Qwen2.5-VL design. The normalised tokens are grouped into non-overlapping spatial windows of size $s \times s$, and each window's $s^2$ tokens are merged (concatenated and linearly projected) into a single token of dimension $D_{\text{lang}}$. The result is a sequence of $N'$ tokens per view (and $K \cdot N'$ in total) that aligns one-to-one with the merged vision tokens.

**Key Formulas:**

$$
Z_{\text{norm}} = \mathrm{RMSNorm}(Z_{l_i}^{\text{reord}})
$$

$$
G_{l_i} = M^{(l_i)}_{\text{geo}}(Z_{l_i}) \in \mathbb{R}^{(K \cdot N') \times D_{\text{lang}}} \quad \text{(Eq. 4)}
$$

**Implementation Details:**

Three independent mergers $M^{(11)}_{\text{geo}}, M^{(17)}_{\text{geo}}, M^{(23)}_{\text{geo}}$ are trained from scratch. They are the principal source of trainable parameters introduced by SpatialStack on top of the base VLM. The window size $s = 2$ matches the vision-side spatial merger to guarantee one-to-one geometry–vision token correspondence at injection time. The exact internal architecture of the merge step (linear projection on concatenated $s^2 \cdot D_{\text{geo}}$ vectors versus pixel-shuffle style reshape) is described conceptually in §A.2 but the precise layer specification is not given.

#### 5.3.5 Layered Residual Injection into LLM Decoder

**Function:** Inject geometry features from progressively deeper VGGT layers into progressively deeper LLM decoder layers via masked additive residuals, restricted to the visual-token slice.

**Input:**
- Name: $\{G_{11}, G_{17}, G_{23}\}$ from §5.3.4 and decoder hidden states $H^{(j)}$
- Shape: $G_{l_i} \in $ `[B, K·N', D_lang]`; $H^{(j)} \in$ `[B, K·N' + M, D_lang]`
- Source: layer-specific projectors and the running LLM decoder

**Output:**
- Name: $H^{(j)\prime}$
- Shape: `[B, K·N' + M, D_lang]`
- Consumer: next decoder block $f^{\text{llm}}_{j+1}$

**Processing:**

At each of the first three decoder layers, geometry features are added to the visual-token slice of the hidden state only; text-token entries remain unchanged. The mapping is **progressive (shallow-to-shallow, deep-to-deep)**: $G_{11} \to$ LLM layer 0, $G_{17} \to$ LLM layer 1, $G_{23} \to$ LLM layer 2. The remaining $L - 3$ decoder layers operate on the standard hidden state without further geometry injection; the final hidden state $H_L^{\text{llm}}$ feeds the LM head for next-token prediction.

**Key Formulas:**

$$
H^{(j)\prime} = H^{(j)} + G_{l_{j+1}} \,, \qquad j \in \{0, 1, 2\}
\quad \text{(Eq. 5, masked to visual-token slice)}
$$

$$
H^{\text{llm}}_L = f^{\text{llm}}_L \big( f^{\text{llm}}_{L-1} \cdots f^{\text{llm}}_1 (H_0) \big) \quad \text{(Eq. 1)}
$$

**Implementation Details:**

The injection uses straight additive residuals (no gating, no cross-attention), and is masked so that only the $K \cdot N'$ visual positions receive the geometry contribution. The Reverse mapping ($G_{11} \to$ LLM layer 2, $G_{23} \to$ LLM layer 0) was tested in Tab. 7 and underperforms the progressive mapping on three of four benchmarks, supporting the layer-aligned design choice.

#### 5.3.6 Training Objective and Optimisation

**Function:** Fine-tune the trainable subset (layer-specific geometry token mergers and full LLM decoder) end-to-end under a single language-modelling objective.

**Input:**
- Name: instruction tuning batches $(q, o, C)$
- Shape: variable-length token sequences plus the multimodal context $C$ (frames and any supporting tokens)
- Source: SPAR + LLaVA-Hound + ScanNet split (VLM-3R) + selected portion of VSI-590K

**Output:**
- Name: scalar loss $\mathcal{L}_{\text{ce}}(\theta)$
- Shape: `[]` (scalar)
- Consumer: AdamW optimiser

**Processing:**

For every training example, the model produces conditional token probabilities over the answer sequence, and the loss is the standard next-token negative log-likelihood. No auxiliary geometry-prediction loss, no contrastive term, and no task-specific head are added; spatial priors emerge only from the architectural inductive bias and from the diversity of the instruction-tuning mixture.

**Key Formulas:**

$$
\mathcal{L}_{\text{ce}}(\theta) = - \sum_{i=1}^{|o|} \log P_{\theta}\!\left( o^{(i)} \mid o^{(<i)},\, q,\, C \right) \quad \text{(Eq. 6)}
$$

**Implementation Details:**

Optimiser AdamW; learning rate $1 \times 10^{-5}$; batch size 64; warmup ratio 0.03 with cosine schedule. The vision encoder and the geometry encoder (VGGT) are kept frozen; only the geometry token merger modules and the LLM decoder weights are updated. Training data combines SPAR (3D-grounded spatial QA), LLaVA-Hound (general video QA), the ScanNet split adopted in VLM-3R (VSI-Bench-style reformulations), and a selected portion of VSI-590K. The paper does not specify the total token count, the number of training steps, hardware configuration, or wall-clock training time.

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| SPAR-234k (subset) | 33 種室內空間 perception/reasoning QA（單視角、多視角、video） | 約 140k samples（從 234k 中抽 60%） | train |
| LLaVA-Hound-64k (subset) | 一般 video instruction-following / object-grounded reasoning | 約 38.3k samples（從 63.8k 中抽 60%） | train |
| VLM-3R ScanNet split | 6 類空間 QA（Object Counting、Relative Distance、Relative Direction、Object Size、Absolute Distance、Room Size） | 約 31.1k samples（從 51.8k 中抽 60%） | train |
| VSI-590K Appearance-Order subset | Appearance order（補 VLM-3R ScanNet split 缺少的時序 supervision） | 約 1.9k samples | train |
| VSI-Bench | Egocentric indoor video 空間 QA（含 MCA 與 NA tasks，如 Object Count、Abs./Rel. Distance、Object/Room Size、Rel. Direction、Route Plan、Appearance Order） | 超過 5,000 QA pairs | test |
| SPAR-Bench | 三層級（perception / reasoning / imagination）空間任務 | the paper does not specify | test（Low-Level 用 Depth-OC/OO/OC-MV/OO-MV、Dist-OC/OO/OC-MV/OO-MV） |
| BLINK / BLINK-Spatial | Multimodal fine-grained perception，含 Relative Depth | the paper does not specify | test（Relative Depth 歸入 Low-Level） |
| CV-Bench | 2D / 3D 空間 perception QA（依 COCO、Omni3D、ADE20K 構建） | the paper does not specify | test |
| Video-MME | 通用 video understanding | the paper does not specify | test（general capability） |
| MMBench | 通用 multimodal understanding | the paper does not specify | test（general capability） |
| TempCompass | Spatial-temporal reasoning | the paper does not specify | test（general capability） |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| VSI-Bench Avg. | MCA 任務的 mean accuracy 與 NA 任務在 $C \in \{0.5, 0.55, \dots, 0.95\}$ 下的 Mean Relative Accuracy 之平均 | yes |
| VSI-Bench per-task score | 8 個子任務（Obj. Count、Abs. Dist.、Obj. Size、Room Size、Rel. Dist.、Rel. Dir.、Route Plan、Appr. Order）的個別分數 | no |
| SPAR-Bench Avg. | SPAR-Bench 總平均分 | no |
| Low-Level Avg. | BLINK Relative Depth 與 SPAR-Bench 中 Depth-OC/OO/OC-MV/OO-MV、Dist-OC/OO/OC-MV/OO-MV 的平均（fine-grained perception 指標） | yes |
| High-Level Avg. | VSI-Bench 全任務平均（multi-view spatial fusion 與 3D relational reasoning 指標） | yes |
| BLINK-Spatial | BLINK 中空間相關子集的分數 | no |
| CV-Bench 2D / 3D / Avg. | 2D 與 3D 子集準確率及其平均 | no |
| MMBench / Video-MME / TempCompass | 一般多模態與時空推理能力分數，用於檢查 catastrophic forgetting | no |

### 6.3 Training and Inference Settings

- Base models：VLM-SpatialStack 以 Qwen3.5-4B 為主，並另以 Qwen2.5-VL-3B 作為公平比較基底；geometry encoder 為 frozen VGGT-1B。
- Trainable / Frozen：vision encoder 與 geometry encoder 全程凍結；只訓練 geometry token merger 與 LLM decoder（及其 fusion 模組）。
- Loss：單一目標 next-token negative log-likelihood (cross-entropy)，無輔助 loss、無 task-specific loss（Eq. 6）。
- Optimizer：AdamW，weight decay $0.01$。
- Learning rate / schedule：peak LR $1\times 10^{-5}$，cosine decay，warmup ratio $0.03$（appendix 中亦寫作 warmup 3%）。
- Batch size：effective batch size 64。
- Epochs / steps：1 epoch；checkpoint 每 1000 steps 存一次，logging 每 10 steps（總 step 數 the paper does not specify）。
- Precision / parallelism：bfloat16；torchrun + DeepSpeed ZeRO-2。
- Sequence length：12,800 tokens；每 video 取 4–8 frames；單樣本 pixel 預算 $16\cdot 28^2$ 至 $576\cdot 28^2$。
- Hardware：32× NVIDIA A100 80GB GPUs。
- Input pipeline（appendix A、C）：影像保持長寬比縮放至 518 px，必要時 center crop 並做 patch-aligned trimming，使 $H \bmod (p\cdot m)=0$、$W \bmod (p\cdot m)=0$（如 $p\cdot m = 14\cdot 2 = 28$）；VGGT patch tokens 經 window-wise reorder 以對齊 vision encoder 的 spatial merger 順序。
- Geometry-language fusion（appendix A.3）：geometry tokens 經 RMSNorm + 兩層 MLP projector 後，僅以 additive residual 注入到 LLM decoder layers $\{0,1,2\}$ 的 vision-token slice（Eq. 15、16），非 vision token（system prompt、text）不變；推論時於 prefill 階段套用一次，後續 decoding 走標準流程。
- Inference：greedy decoding（temperature $=0$, num_beams $=1$），KV cache 啟用，輸出去除 prompt prefix；VSI-Bench 遵循官方協議（MCA mean accuracy + NA Mean Relative Accuracy across $C=0.5,\dots,0.95$）。
- Evaluation 端的視覺前處理沿用 VG-LLM 的 518-pixel pipeline，並強制 $(W/p)\bmod m = 0$、$(H/p)\bmod m = 0$ 以對齊 token merger。

### 6.4 Main Results

VSI-Bench（節錄；完整 8 個子任務見 Tab. 3）：

| Method | VSI Avg. | Obj. Count | Abs. Dist. | Obj. Size | Room Size | Rel. Dist. | Rel. Dir. | Route Plan | Appr. Order | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Gemini-2.5 Pro | 51.5 | 43.8 | 34.9 | 64.3 | 42.8 | 61.1 | 47.8 | 45.9 | 71.3 | proprietary，整體第 1 |
| GPT-4o | 34.0 | 46.2 | 5.3 | 43.8 | 38.2 | 37.0 | 41.3 | 31.5 | 28.5 | proprietary |
| Spatial-MLLM-4B | 47.0 | 65.3 | 34.8 | 63.1 | 45.1 | 41.3 | 46.2 | 33.5 | 46.3 | geometry-aware baseline |
| VG-LLM-4B | 47.3 | 66.0 | 37.8 | 55.2 | 59.2 | 44.6 | 45.6 | 33.5 | 36.4 | single-layer GVF baseline |
| Cambrian-S-3B | 57.3 | 70.7 | 40.6 | 68.0 | 46.3 | 64.8 | 61.9 | 27.3 | 78.8 | open-source 第 3 |
| Qwen3.5-4B | 53.6 | 56.5 | 36.5 | 67.5 | 53.8 | 60.3 | 57.5 | 34.0 | 62.3 | base model（fine-tuned） |
| **SpatialStack-4B (Qwen2.5)** | **60.9** | **69.2** | **45.4** | **63.0** | **63.2** | **57.9** | **68.4** | **40.2** | **79.6** | open-source 第 2 |
| **SpatialStack-5B (Qwen3.5)** | **67.5** | **71.0** | **55.6** | **69.1** | **68.2** | **67.3** | **84.1** | **41.2** | **83.5** | open-source SoTA；Route Plan 為 zero-shot |

CV-Bench（Tab. 4）：

| Method | 2D (%) | 3D (%) | Avg. (%) | Notes |
|---|---|---|---|---|
| GPT-4o | 74.8 | 83.0 | 78.9 | proprietary |
| SPAR-8B | 72.3 | 89.1 | 80.7 | open-source |
| Qwen2.5-VL-3B | 67.9 | 70.4 | 69.2 | base |
| Qwen3.5-4B | 79.7 | 90.2 | 85.0 | base |
| VG-LLM-4B | 71.3 | 87.7 | 79.5 | dual-encoder baseline |
| **SpatialStack-4B (Qwen2.5)** | **75.4** | **87.0** | **81.2** | 超越同基底所有 baseline |
| **SpatialStack-5B (Qwen3.5)** | **78.9** | **92.2** | **85.5** | new SoTA on CV-Bench |

通用能力（Tab. 5，檢查無 catastrophic forgetting）：

| Method | MMBench | Video-MME | BLINK | TempCompass | Overall |
|---|---|---|---|---|---|
| Qwen3.5-4B | 83.25 | 62.44 | 61.12 | 66.84 | 68.41 |
| **SpatialStack-5B (Qwen3.5)** | **83.42** | **63.74** | 55.46 | **69.37** | 68.00 |

Cross-benchmark fusion 比較（Tab. 2，全部以 Qwen3.5 為基底）：

| Method | VSI-Bench | SPAR-Bench | BLINK-Spatial | CV-Bench | Overall |
|---|---|---|---|---|---|
| Qwen3.5 (fine-tuned) | 64.76 | 68.75 | **56.10** | 84.49 | 68.52 |
| GVF-L23（≈VG-LLM 設計） | 66.36 | 70.83 | 51.91 | 84.64 | 68.43 |
| GVF-L11/17/23（naive multi-layer） | 65.15 | 71.20 | 51.28 | 84.33 | 67.99 |
| **SpatialStack** | **67.52** | **71.39** | 52.12 | **85.53** | **69.14** |

零樣本 CV-Bench 比較（appendix Tab. C）：本方法在 Count / Relation / Depth / Distance / Overall 全面領先 SpatialRGPT 與 Spatialbot（Overall 86.5 vs. 72.7 / 68.0；SpatialVLM 因無釋出程式碼未列入）。

### 6.5 Ablation Studies

- Geometry injection layer（單層 GVF，Fig. 4 與 Tab. 1）：把單一 VGGT 層特徵注入 vision pathway。Low-Level 在第 11 層達峰（66.11），到第 23 層下降（64.33）；High-Level 隨層深單調上升（64.48 → 65.76 → 66.36）。此 ablation 直接驗證了「淺層保留細粒度幾何、深層編碼全域語意」這個論文的核心 motivation，屬於診斷型實驗。
- Naive multi-layer fusion on vision pathway（Tab. 1）：同時把第 11/17/23 層特徵都加進 vision tokens，Low-Level 64.69、High-Level 65.15、Overall 64.92，反而落後最佳單層配置；揭露 vision-pathway naive 多層融合會造成 feature interference 而非 synergy，正面回答「該不該直接堆到 vision side」。屬於診斷型實驗。
- Fusion location: vision vs. language（Tab. 7）：Vision Fusion baseline 整體 68.38，低於把幾何注入 LLM decoder 的 SpatialStack（69.14），佐證將多層幾何特徵注入語言側更有效。屬於診斷型實驗。
- Fusion order（Tab. 7，Reverse）：把 Geo-L11/L17/L23 反向對映到 LLM-L2/L1/L0，整體 68.52 低於正向（69.14），且在 4 個基準中 3 個落後正向方案；確認「淺幾何 → 淺 LLM、深幾何 → 深 LLM」的階層對齊有意義。屬於診斷型實驗，但僅比較兩種順序，未列出更多 permutation。
- VGGT layer selection（Tab. 6）：把最深層由 L23 換成 L21 或 L22（單獨或併入 +L11+L17 的 multi-layer），Low/High-Level 變動極小（如 +L23 vs. +L22：65.45/66.78 vs. 64.44/67.52），結論是「在網路深度上廣泛取樣」比挑哪一層更重要。比較像是 robustness check，靠近 sanity check 而非強診斷實驗。
- Geometry vs. vision feature responses（appendix F.1，Fig. C）：在 50% / 75% / 100% 相對深度比較 ROI similarity map，幾何特徵保留邊界、視覺特徵深層趨於均勻；屬於 qualitative diagnosis，支撐 motivation 但非定量 ablation。

整體而言，主要 ablation（注入層、fusion 路徑、fusion 順序）皆對應論文核心設計選擇；layer-selection ablation 偏 robustness check；缺少對 LLM 注入層 $\{0,1,2\}$ 數量、注入層位置、projector 容量、token 數量等的 ablation。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 與 Spatial-MLLM、VG-LLM、Cambrian-S 等同級 geometry-aware baseline 以及 GPT-4o、Gemini-2.5 Pro proprietary 模型在 VSI-Bench / CV-Bench 上比較（Tab. 3、Tab. 4）。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時報告 VSI-Bench、SPAR-Bench、BLINK(-Spatial)、CV-Bench、MMBench、Video-MME、TempCompass（Tab. 2、3、4、5）。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — 注入層、vision-vs-language fusion、fusion 順序屬診斷型；但 VGGT layer selection 偏 sanity check，且未對 LLM 注入層位置 / 數量、projector 設計、token merger stride 做系統性 ablation。
- [missing] Has a scaling study (size, length, or compute) — 僅給出 4B 與 5B 兩個離散規模、frame 數固定 4–8，無系統性 model size / data size / context length 的 scaling 曲線。
- [missing] Has an efficiency / wall-clock comparison — 全文未報告推論延遲、throughput、額外參數量或 FLOPs 的比較，且未量化 hierarchical fusion 帶來的開銷。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 主表與 ablation 皆為單一 run，未提供 std 或多 seed 結果。
- [missing] Releases code / weights / data sufficient for reproducibility — 論文僅在標題給出專案頁 https://spatial-stack.github.io/，正文與 appendix 未說明 code / checkpoint / 資料抽樣腳本是否釋出，the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 首個 systematic analysis of fusion layers across vision/geometry/LLM**。Partially supported. Fig. 4 與 Tab. 1 只測試 4 個 geometry encoder 單層 (4/11/17/23) 與 1 種 multi-layer 組合，且皆注入到 visual pathway；LLM decoder 端的 layer-wise 行為未被系統性分析，而這正是 SpatialStack 主張的關鍵 axis。
- **Claim 2: SpatialStack hierarchical fusion framework**。Supported as architectural design (Fig. 2 與 Eq. 5)。但「framework」一詞被論文後續延伸為「general / model-agnostic」，缺乏跨 backbone 證據 (見 §4.2.2)。
- **Claim 3: SOTA on multiple 3D spatial benchmarks**。Supported on VSI-Bench、SPAR-Bench、CV-Bench (Tab. 2, 3, 4)，但 not on BLINK-Spatial：Tab. 2 顯示 SpatialStack 反而低於 base Qwen3.5。
- **Claim 4: Strong cross-task generalization**。Partially supported. Tab. 2 overall 確有提升，但 BLINK 規律性退步顯示 generalization 不均勻，至少有一類任務系統性退步。
- **Claim 5 (隱含): Progressive alignment is optimal**。Weakly supported. Tab. 7 progressive vs reverse overall 僅相差 0.62 pt，且 reverse 在 VSI-Bench 上也達 67.22 (與 final 67.52 幾乎並列)；單次訓練、無信賴區間，難以排除 noise。
- **Claim 6: No catastrophic forgetting (Sec. 5.2, Tab. 5)**。Overclaimed. BLINK 從 61.12 退步至 55.46 即為一種針對空間感知的 catastrophic 退步；其他三項 (MMBench、Video-MME、TempCompass) 雖大致持平，仍不足以為此聲稱背書。

### 7.2 Fundamental Limitations of the Method

**架構與層深強耦合**：注入對應 (VGGT layers 11/17/23 → LLM layers 0/1/2) 是針對 VGGT-1B (24 層) 與 Qwen3.5-4B 手調的特定配對。換用其他 geometry encoder 或不同層數的 LLM 必須重新搜尋對應，「general framework」的定位實際上缺乏 layer-mapping 的自動化方法。

**Frozen geometry encoder 的能力上限**：Sec. 4.2 與 Sec. 5.1 明確凍結 VGGT，只訓練 fusion module 與 LLM。這保留預訓練表示，卻也代表下游任務無法回流調整 VGGT 的特徵；當 VGGT 對某類場景 (例如戶外、動態) 表示不佳時，SpatialStack 無法透過下游監督修補，效能上限被 VGGT 的預訓練分布所封頂。

**殘差只進入 decoder 前三層**：幾何訊號於 Eq. 5 僅注入 layer 0/1/2，之後 $L-3$ 層必須將其自身傳遞到 final hidden state。若中段 attention/MLP 將該訊號稀釋或覆寫，gain 會在深層 saturate；paper 沒有任何機制保證 layer 3 之後幾何訊號仍可讀取。同時，這也與 paper 主張的「progressive 對應」在 LLM 側並不對稱：geometry 端 shallow→deep 全用上，LLM 端只用 shallow。

**雙塔依賴**：方法必須同時擁有 vision encoder 與 separate geometry encoder。對於僅有單一 vision encoder 的 lightweight VLM (例如行動端佈署的 small VLM) 並不直接適用，且 VGGT-1B 本身在推論時就帶來顯著計算開銷。

### 7.3 Citations Worth Tracking

- **[36] DeepStack (Meng et al., NeurIPS 2024)**：SpatialStack 的直接靈感來源，理解 visual token stacking 與本文 LLM 端 geometry stacking 的差異是關鍵；本文是否「真正延伸」DeepStack 還是僅替換對象，需閱讀原文判斷。
- **[46] VGGT (Wang et al., CVPR 2025)**：backbone geometry encoder，其 layer-wise 輸出特性 (DPT 風格 multi-level extraction) 是 SpatialStack 設計合理性的基礎；理解 VGGT 各層實際表示什麼，有助於評估 layer 11/17/23 選擇。
- **[60] VG-LLM (Zheng et al., NeurIPS 2025)**：主要對照基線，patch-level GVF-L23 fusion 與 SpatialStack 在 visual pathway 上的最直接前身；SpatialStack 的訓練資料也大量沿用 VG-LLM 釋出的子集。
- **[53] Cambrian-S (Yang et al., 2025)**：強 open-source baseline，Tab. 3 顯示其在 VSI-Bench 的 Object Count、Room Size、Appearance Order 上仍超越 SpatialStack-4B (Qwen2.5)，閱讀原文有助於了解 spatial supersensing 風格是否與 layered fusion 互補。
- **[50] Spatial-MLLM (Wu et al., NeurIPS 2025)**：dual-encoder 前身，與 SpatialStack 採取相同的「外掛幾何 encoder」設計哲學但只融合最後一層，是分離「dual-encoder」與「multi-level fusion」貢獻的關鍵對照。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] BLINK-Spatial 為何在加入空間訓練後反而退步 5.66 pt？退步集中於哪些 sub-task (relative depth、jigsaw、forensic detection 等)？
- [ ] 若把幾何 token 也注入 LLM 中段或後段層 (例如 layer 12, 18, 22) 是否能進一步提升 high-level 推理？目前只測前三層，progressive 論述在 LLM 側並未真正驗證。
- [ ] 多 seed 重複訓練下，Tab. 2 與 Tab. 7 的 overall 0.62 pt gap 是否仍顯著？SpatialStack 與 reverse ordering 的 67.22 vs 67.52 是否在 noise 範圍內？
- [ ] 將 VGGT 以 LoRA 解凍微調是否能進一步改善 SPAR-Bench low-level 任務？目前 frozen geometry encoder 是否成為效能上限？
- [ ] 換用 LLaVA-OneVision、InternVL 等非 Qwen backbone 時，是否仍能維持 ~1 pt overall 改善以支撐「model-agnostic」聲稱？
- [ ] LLaVA-Hound 64k 通用視訊資料對 BLINK 退步的責任有多大？移除這部分訓練資料是否反而能保住 BLINK？
- [ ] 將融合層數從 3 擴大至 5 或 7 (例如 VGGT layer 4, 8, 11, 17, 20, 23) 是否會持續改善，或開始出現像 visual pathway 那樣的「feature interference」？

### 8.2 Improvement Directions

1. **多 seed 重複訓練 + 信賴區間 (容易)**：以 3-5 個 seed 重做 Tab. 2、Tab. 7、Tab. 5 的核心對照，量化 0.5-1.5 pt overall gap 的統計顯著性。沒有 seed variance，目前的「SOTA」結論存在被單次訓練 noise 蓋過的風險。
2. **BLINK-Spatial 退步歸因分析 (容易)**：依 BLINK sub-task 拆解 SpatialStack-5B 與 Qwen3.5-4B 的差異，識別退步集中區域。若退步主要來自純 2D 視覺感知，則暗示幾何注入污染了視覺 pathway 的某些 channel；若集中在 perspective/depth 等任務，則需要重新檢視 VGGT 特徵與 BLINK 標註的對齊。
3. **LLM decoder 注入點消融 (中等)**：在 layer 0/1/2 之外加入 middle (10/11/12) 與 late (20/21/22) 注入位置的對照組，驗證 progressive 確實優於 uniform 或 deep 配置。這是 paper 最大的證據缺口，補上後 progressive 論述才具完整性。
4. **Layer-specific projector 的 visual-pathway baseline (中等)**：將 GVF-L11/17/23 升級為 visual 端也使用 layer-specific projectors 的版本作為對照。只有此 baseline 才能真正分離「multi-layer 本身的 gain」與「在 LLM 端注入的 gain」，現行對比把兩個變因混在一起。
5. **跨 backbone 驗證 model-agnostic 聲稱 (中等到困難)**：在至少一個非 Qwen backbone (例如 LLaVA-OneVision-7B 或 InternVL) 上重做 SpatialStack vs base 的對照。Paper 自身宣稱 model-agnostic 但只做了 Qwen 系列，補上跨家族證據是支撐通用性的關鍵實驗。
6. **解凍 VGGT 做 LoRA 微調 (困難)**：在 fusion module 之外允許 VGGT 進行小幅 adapter 微調，觀察 SPAR low-level 是否進一步增益；需小心 over-fitting 與打破 VGGT 預訓練幾何先驗。
7. **加入 BLINK 風格訓練資料修復退步 (低到中等)**：將 BLINK 的 fine-grained perception 資料以 instruction-tuning 形式加入訓練 mixture，直接針對退步來源提供監督；風險是若退步源自 architecture 而非資料缺口，此修復無效，反而能反證 architecture 為退步原因。
