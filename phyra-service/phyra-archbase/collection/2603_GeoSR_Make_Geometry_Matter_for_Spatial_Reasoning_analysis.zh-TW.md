<!-- type: paper-read-notes | generated: 2026-05-08 | lang: zh-TW -->

# GeoSR — Make Geometry Matter for Spatial Reasoning

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | GeoSR |
| Paper full title | Make Geometry Matter for Spatial Reasoning |
| arXiv ID | 2603.26639 |
| Release date | 2026-03-27 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.26639 |
| PDF link | https://arxiv.org/pdf/2603.26639 |
| Code link | https://github.com/SuhZhang/GeoSR |
| Project page | https://suhzhang.github.io/GeoSR/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Shihua Zhang | National University of Singapore | https://github.com/SuhZhang | first author |
| Qiuhong Shen | National University of Singapore | — | co-author |
| Shizun Wang | National University of Singapore | — | co-author |
| Tianbo Pan | National University of Singapore | — | co-author |
| Xinchao Wang | National University of Singapore, Department of Electrical and Computer Engineering | https://sites.google.com/site/sitexinchaowang/ (https://cde.nus.edu.sg/ece/staff/wang-xinchao/) | corresponding author |

### 1.2 Keywords

VLMs, Spatial reasoning, 3D foundation models, Geometry tokens, Token masking, Gated fusion, 4D reasoning, Video understanding

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VG-LLM [50] | baseline | Extracts implicit geometry tokens via pretrained 3D model and uses additive token-level fusion for static spatial reasoning. |
| Spatial-MLLM [38] | baseline | Adds a spatial branch with space-aware frame sampling to preserve geometry-relevant evidence under limited video context. |
| VLM-3R [7] | baseline | Augments VLMs with instruction-aligned 3D reconstruction priors for static spatial reasoning. |
| GSM [53] | baseline | Most closely related; retrieves dynamic geometric evidence from priors and appends to vision tokens for 4D reasoning. |
| VSI-Bench [41] | influence | Representative static spatial reasoning benchmark used to evaluate viewpoint-robust spatial understanding. |
| DSR-Bench [53] | influence | Dynamic spatial reasoning (4D) benchmark used to evaluate spatiotemporal consistency over moving cameras and objects. |
| VGGT / pretrained 3D foundation models [32,34,36] | base model | Pretrained visual geometry grounding models that supply the implicit geometry tokens fed into the VLM. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於 Vision-Language Models (VLMs) 的 spatial reasoning 能力，涵蓋靜態場景（視角變化、可見性差異）與動態影片（鏡頭運動、物體運動、時間連續性）兩類設定。作者觀察到，雖然當前主流做法是把 pretrained 3D foundation models 萃取的 geometry tokens 注入 VLM，但在 naive token fusion 加上 standard fine-tuning 之下，模型往往仍依賴 2D 外觀捷徑，使 geometry tokens 在 spatial reasoning 中被嚴重低估甚至產生負面效果。論文提出 GeoSR 框架，透過 Geometry-Unleashing Masking 策略性遮蔽 2D vision tokens 以削弱 appearance shortcut，並以 Geometry-Guided Fusion 的 gated routing 在需要幾何證據的 token / frame 區域自適應地放大 geometry tokens 貢獻。整體目標是讓注入的 geometry tokens 真正成為 actionable evidence，並在 VSI-Bench 與 DSR-Bench 等 static / dynamic spatial reasoning benchmarks 上取得新的 state-of-the-art。

### 2.2 Domain Tags

- Computer Vision
- Vision-Language Models
- Spatial Reasoning
- 3D Scene Understanding
- Video Understanding

### 2.3 Core Architectures Used

- **Qwen2.5-VL-7B**：作為 static 與 dynamic 兩類設定共用的 backbone VLM，負責接收融合後的 vision / geometry tokens 與 prompt tokens 以產生答案。
- **VGGT (pretrained 3D foundation model)**：在 static spatial reasoning 中作為 frozen geometric tokenizer，從單目影像 / 影片擷取 implicit geometry tokens $F_G$。
- **$\pi^3$ dynamic geometry prior**：在 dynamic spatial reasoning 中替換 VGGT，提供能涵蓋鏡頭與物體運動的 spatiotemporal geometry tokens。
- **QFormer-style cross-attention bottleneck**：以 learnable bottleneck $B$ 先 attend 到 text tokens 取得 $F_B$，再 attend 到 $F_G$ 取得 question-relevant 的 compact evidence $Z_G$，同時輸出用於 TopK masking 的 relevance score $s$。
- **Geometry-Unleashing Masking**：本論文提出的訓練期遮罩模組，static 採 MAE-style random mask、dynamic 採基於 $s$ 的 TopK mask，以削弱 2D appearance shortcut，迫使模型查詢 geometry stream。
- **Geometry-Guided Fusion**：本論文提出的 gated fusion 模組，在 token-and-channel 層級以學到的 gate $\alpha = \sigma(W_g[V \Vert G] + b_g)$ 自適應控制 vision 與 geometry 特徵在每個位置的混合比例。
- **Spatiotemporal positional encodings (RoPE 及其時空延伸)**：用於 prompt / vision / geometry tokens，使融合後序列在 VLM backbone 中保有時空位置資訊。

### 2.4 Core Argument

作者指出 spatial reasoning 之所以難以單靠 VLM 解決，根本原因在於 2D vision tokens 只承載外觀語意，缺乏 3D 結構與時序幾何資訊；近期工作雖試圖從 pretrained 3D foundation models 取出 geometry tokens 注入 VLM，但他們發現一個 reproducible 的反直覺現象：在 naive token fusion 與 standard fine-tuning 下，VLM 會大量回退到「appearance-driven shortcuts」，因為對許多問題只看 2D 紋理就能勉強答對，使得 geometry tokens 形同 dispensable side signal，甚至在 dynamic 影片中拉低性能。換言之，問題不是 geometry 不夠好，而是模型「沒有被迫去用」geometry，並且 indiscriminate fusion 還會稀釋真正關鍵區域的幾何訊號。基於這個診斷，作者主張解法必須同時處理「使用是否有效」與「使用是否合理」兩件事：前者透過 Geometry-Unleashing Masking 在訓練時策略性遮掉部分 2D vision tokens，切斷外觀捷徑、強迫模型查詢 geometry tokens；後者透過 Geometry-Guided Fusion 的 gated routing，在 token 與 frame 層級依據幾何證據需求動態提升 geometry 的貢獻權重，避免均勻融合稀釋有用線索。兩個元件互補，使得 geometry tokens 從「可有可無」變成「actionable & controllable」，因此邏輯上必然能讓 VLM 在 viewpoint 變化、occlusion 與動態場景中更穩定地推理空間關係，這也解釋了為何 GeoSR 在 static 與 dynamic 兩類 benchmark 都能一致超越只做 naive injection 的 prior methods。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(240 words)

標題「Make Geometry Matter for Spatial Reasoning」直接點題：作者主張 geometry tokens 在現行做法中其實「沒有真的發揮作用」，論文要解決的就是這個被忽略的問題。Abstract 以三段式鋪陳問題、診斷與解法。第一句先確立背景：VLMs 在影像與影片理解上很強，但在 static 與 dynamic 兩種 spatial reasoning 場景下能力仍受限。第二句指出近期主流方向——把 pretrained 3D foundation models 抽出的 geometry tokens 注入 VLM——並隨即提出本文的關鍵觀察：在 naive token fusion 加上 standard fine-tuning 的常見配方下，這些 geometric cues 其實常被低度使用，因為 VLM 偏好倚賴 2D appearance shortcuts。這個觀察是整篇論文的支點，後續所有設計都環繞「如何強迫模型真的去用 geometry」而展開。

接著 Abstract 提出 GeoSR 框架，包含兩個互補組件：(1) Geometry-Unleashing Masking 在訓練時策略性地遮蔽部分 2D vision tokens，弱化 non-geometric shortcuts；(2) Geometry-Guided Fusion 是一個 gated routing 機制，能在 geometric evidence 重要的區域自適應地放大 geometry tokens 的貢獻。前者解決「要不要用」的問題，後者解決「在哪裡用、用多少」的問題，形成「effective + reasonable」的雙軸策略。

最後 Abstract 宣稱在 static 與 dynamic spatial reasoning 兩類 benchmarks 上一致超越前人並達到 SOTA，並附上 project page 連結。整段把問題、診斷、方法、結果壓縮成一條清楚的因果鏈，為後續 Introduction 中更詳細的動機鋪設與圖示鋪路。

### 3.2 Introduction

(720 words)

Introduction 的故事以四個邏輯階段推進：先確立任務的重要性、再揭示現有 paradigm 的失敗、接著提出關鍵原則、最後鋪陳兩個解法。第一段以 VLMs 在 image / video understanding 的成功開場，但隨即指出真實應用需要的是 spatial reasoning——回答物件「在哪、彼此怎麼關聯、隨時間如何變化」的問題。作者強調這在 static（場景剛性、視角變化）與 dynamic（運動、遮蔽、時序連續性）兩種設定都不可或缺，並引述近期 benchmarks 顯示 VLMs 雖擅長 semantic recognition，遇到 viewpoint changes、motion continuity、quantitative spatiotemporal judgments 仍非常脆弱。

第二段轉到方法論演進：早期 3D-aware MLLMs 仰賴 explicit 3D 輸入（depth、point clouds、pre-built 3D maps），但需要額外感測器或多階段重建，noise 大且難以擴展到只有 monocular 影像的常見情境。近期範式因此轉向用 pretrained visual geometry grounding models 從 monocular videos 抽出 implicit geometry features，注入 VLMs 作為 geometry tokens 的「injection paradigm」。這個鋪陳很關鍵：它建立了一個「看似直覺合理」的研究方向，作者隨後就要對它丟出反問。

第三段是論文的轉折點。作者直接提出未被探討的根本問題：「Do geometry tokens actually help spatial reasoning, or are they merely dispensable side signals?」並回報一個可重現但反直覺的現象——在 naive fusion + standard fine-tuning 之下，static 場景的增益相當有限，dynamic 場景甚至會「負增益」，如 Figure 1 所示。診斷是：模型傾向走 appearance-driven shortcuts，把 geometry 當成可有可無的副訊號；而 indiscriminately mixing geometry with appearance 還會稀釋 geometry 中真正有用的資訊。這段把「geometry injection 無效」這個問題從 anecdote 提升為 reproducible phenomenon，給後續方法一個明確標靶。

第四段提出指導原則：必須「compel the VLM to effectively rely on geometric information when spatial reasoning demands it」。緊接著兩段對應到 GeoSR 的兩個元件。Geometry-Unleashing Masking 解決「effective」面向：在訓練時策略性遮蔽部分 2D vision tokens 來削弱 non-geometric shortcuts，迫使模型去查詢 geometry tokens。Geometry-Guided Fusion 則解決「reasonable」面向：透過 gated routing 在 geometric evidence 真正重要的位置自適應放大 geometry tokens 的貢獻，而非把 geometry 視為對所有 tokens、所有 frames 一視同仁的補充。兩者搭配讓 geometry 變成「actionable and controllable」。

最後一段條列三項貢獻：(i) 報告 implicit geometry injection 在 naive fusion + standard fine-tuning 下無效甚至有害的可重現觀察；(ii) 提出 GeoSR 框架，以 Geometry-Unleashing Masking 與 Geometry-Guided Fusion 兩個簡單設計鼓勵 effective 與 reasonable 的 geometry 使用；(iii) 在 static 與 dynamic 兩類 benchmarks 上驗證一致改進。Introduction 因此完成「動機—診斷—原則—設計—驗證」的閉環，並為下一節 Related Work 中與既有 geometry-aware 工作的對比做好鋪墊。

### 3.3 Related Work / Preliminaries

(1180 words)

這個概念區段同時涵蓋 §2 Related Work（含 §2.1 與 §2.2）與 §3.1 Preliminary: Geometry-Aware Framework，三者合起來建立論文的學術座標與技術基線。

§2.1 General Video Understanding 從 image-to-video 的延伸切入：把 clip 視為 sampled frames、建模 temporal context，並區分三類工作——proprietary video VLMs（提供強上限參考）、open-source video-specialized models（強化 temporal modeling 與 long-context handling）、以及以 multi-frame prompting 與 instruction tuning 擴展通用 VLMs。作者刻意指出儘管這些模型在 general video understanding 上表現好，遇到 spatial reasoning 仍 brittle，原因是 supervision 偏向 semantic alignment，導致對 viewpoint、occlusion、motion 不穩，因此真正可靠的 spatial reasoning 需要 geometry-grounded evidence。這段話把後續注入 geometry 的必要性做了第一層鋪陳。

§2.2 Spatial Reasoning with VLMs 是論文真正競爭場的回顧，分為 static 與 dynamic 兩塊。Static 部分以 VSI-Bench 為代表 benchmark，介紹兩條技術路線：一是擴大 spatial QA 監督（SAT、SPAR），二是注入 3D foundation models 的 geometric priors（VG-LLM、Spatial-MLLM、VLM-3R）。作者特別指出這些方法多採用「uniform 或 naive fusion」，使 geometry cues 仍被低度利用——這正是 GeoSR 要瞄準的縫隙。Dynamic 部分（亦稱 4D reasoning）則處理空間關係隨時間因 camera/object motion 而改變的場景，要求 spatiotemporal consistency。LLaVA-4D 把 spatiotemporal prompts 嵌入 MLLM，而最相關的 GSM 從 dynamic geometry priors 取出問題相關的 dynamic geometric evidence 接到 vision tokens 後做為 VLM 輸入。作者再次指出：前者需要多影片輸入並仰賴 SfM-style reconstruction，限制 monocular in-the-wild scalability；後者雖採 monocular，但 geometry injection 的增益有限，這也正是後文要展示「indiscriminate fusion 無效甚至有害」的理由。Related Work 因此把 GeoSR 的定位收斂為：在 monocular videos 上把 geometry tokens 變成 actionable evidence。

§3.1 Preliminary 則扮演技術橋樑，先把這個 paradigm 形式化。給定影像或影片序列 $\{I_t\}_{t=1}^{T}$ 與文字提示 $Q$，框架把三條 stream 編碼為 vision tokens $F_V \in \mathbb{R}^{(H_V W_V T) \times C_V}$、prompt tokens $F_P \in \mathbb{R}^{L_P \times C_P}$、以及由 pretrained 3D model 抽出的 geometry tokens $F_G \in \mathbb{R}^{(H_G W_G T) \times C_G}$；fusion module $F(\cdot)$ 把 $F_G$ 融入 $F_V$ 得到 $F$，再連同 $F_P$ 餵入 VLM backbone。Figure 2 把這個 baseline 架構視覺化，並用 snow / flame icons 區分 frozen 與 trainable 元件。

接著作者列出兩種主流 fusion 模式以對應後續實作。其一是 static reasoning 常用的 Additive Fusion：

$$\boldsymbol{F}=\boldsymbol{F}_{V}+\mathrm{MLP}(\mathrm{Reshape}(\boldsymbol{F}_{G}))$$

其中 Reshape 與 MLP 用來對齊解析度與通道。其二是 dynamic reasoning 偏好的 QFormer Fusion，先以 learnable bottleneck $B \in \mathbb{R}^{L_B \times C}$ 透過 cross-attention 摘要 prompt 意圖得到 $F_B$，再用 $F_B$ 對 $\hat{F}_G = \mathrm{MLP}(F_G)$ 做 cross-attention 拿到 question-relevant geometry summary $Z_G$，最後與 vision tokens 沿 token 維度串接形成 $F=[\boldsymbol{F}_V, \mathrm{MLP}(\boldsymbol{Z}_G)]$。作者也提及 spatiotemporal RoPE 等位置編碼為簡潔起見省略。

關鍵的承上啟下放在這段末尾：在這個 paradigm 下，prompt / visual / geometric tokenizers 通常 frozen，只訓練 fusion module 與 fine-tune VLM backbone。然而作者直白指出，這個 standard recipe 並沒有讓 geometry tokens 在 spatial reasoning 中 actively useful，VLM 仍會仰賴 2D visual cues 而忽略 geometry stream，某些情境甚至移除 geometry branch 後表現反而更好（呼應 Figure 1）。這個結論把 §2 的脈絡批評與 §3.1 的形式化基線兩者鎖在一起，明確指出問題不是 geometry 本身沒用，而是 fusion + fine-tuning 的常見配方沒讓它能用，從而為下一章 §3.2 與 §3.3 引入兩個對症的設計做好結構性鋪陳。

### 3.4 Method (overview narrative)

(1820 words)

Method 章節從 Preliminary 之後分為兩個對應問題的解法區塊（§3.2 Geometry-Unleashing Masking、§3.3 Geometry-Guided Fusion）以及 §3.4 Implementation Details，整體故事是「先讓 geometry 被迫被使用，再讓它被合理使用，最後落地到 static / dynamic 兩個實際設定」。Figure 3 把兩個策略並列展示：(a) 顯示 masking 流程如何在 static 與 dynamic 場景下分別產生 random mask 與 TopK mask，(b) 顯示 gated fusion 如何把 redistributed geometry features 與 masked vision features 結合。

§3.2 處理 effectiveness 面向。作者指出即使加了 geometry tokens，模型仍會走 2D appearance shortcut，因此提出在訓練時對 vision tokens $F_V$ 套用二元遮罩 $m \in \{0,1\}^{(H_V W_V T)}$ 得到 $\tilde{F}_V = m \odot F_V$，並以 Bernoulli switch $\delta \sim \mathrm{Bernoulli}(\beta)$ 控制是否啟用，避免 inference 時 distribution mismatch。針對如何決定 mask set $\mathcal{M}$，作者依 baseline fusion 形式給出兩種策略。對 static reasoning（搭配 Additive Fusion）採 MAE 風格的 random mask，從 $H_V W_V T$ 個位置中均勻抽 $K=\lceil \gamma (H_V W_V T) \rceil$ 個 token 遮蔽。對 dynamic reasoning（搭配 QFormer Fusion）則改採 query-style TopK mask：先利用既有 cross-attention 把 question-related geometry 凝聚到 $Z_G$，並從 $\mathrm{CrossAttn}_2$ 的 attention probability 張量 $A$ 得到每個 geometry token 的相關度 $u_j = \frac{1}{h L_B} \sum_{k,i} A_{k,i,j}$，再 min-max normalize 為 $s_j$；接著對 $s$ 取 TopK 選出對問題最關鍵的 geometry 位置作為 mask set，迫使模型只能從 geometry stream 中找答案。由於 vision 與 geometry 解析度可能不同，作者另以 2D 空間插值 $\hat{F}'_G = \mathrm{Interp}(\hat{F}_G,(H_V,W_V))$ 對齊。整段邏輯是：用 attention 識別「最值得倚賴 geometry 的位置」，然後正好把對應的 vision tokens 拿走，shortcut 就無路可退。

§3.3 處理 reasonableness 面向。作者觀察 uniform additive 或 simple concatenation 都讓模型有空間「全面下調 geometry 並回頭吃剩下的 visual evidence」。Geometry-Guided Fusion 因此引入 token-and-channel-wise 的 learned gate：先對 masked vision feature $\tilde{F}_V$ 與 geometry feature $\tilde{F}_G$ 各自做 LayerNorm 得到 $V$、$G$，再以 $\boldsymbol{\alpha}=\sigma(\mathbf{W}_g[V \Vert G]+\boldsymbol{b}_g)$ 計算 gate，最後以 $F = \boldsymbol{\alpha} \odot V + (1-\boldsymbol{\alpha}) \odot G$ 自適應融合。對 static 設定，$\tilde{F}_G$ 直接由 $\mathrm{MLP}(\mathrm{Reshape}(F_G))$ 取得；對 dynamic 設定，作者把 $Z_G$ 中的 compact evidence 透過 $\tilde{F}_G = \mathrm{CrossAttn}_3(\hat{F}'_G, Z_G)$ 重新散布回 token 級的 fine-grained geometry feature map，使 dynamics 也能落到每個位置。dynamic 場景下作者進一步把 $Z_G$ 串接於 $F$ 之後形成 $[F, Z_G]$ 餵入 VLM，補充 global temporal context。整體 design intent 是讓 gate $\alpha$ 在 geometry 真正有用的位置壓低 $\alpha$、放大 $G$ 的貢獻，而不是均勻稀釋。

§3.4 Implementation Details 把方法落到具體系統：兩種設定都使用 Qwen2.5-VL-7B 作為 VLM backbone，static 採 VGGT 抽 geometry tokens、dynamic 改用 $\pi^3$ 以更好捕捉 dynamic geometry。masking 超參統一為 $\gamma=0.8$、$\beta=0.5$，static 的 mask 為 random、dynamic 為 TopK。資料上 static 用 SPAR-7M 與 LLaVA-Hound、dynamic 用 DSR-Train，皆訓練 1 epoch；static 用 batch size 64、lr $1\times 10^{-5}$、150 步 linear warmup 後 cosine 衰減，dynamic 用 batch size 32、lr $2\times 10^{-7}$、50 步 warmup。Inference 時 masking 一律關閉、餵入完整 vision tokens。所有實驗於 4×H200 GPU 上執行，static 約 14 小時（DeepSpeed ZeRO-2），dynamic 約 20 小時（ZeRO-3 Offload）。整段把「動機—設計—系統」收尾，使讀者進入 §4 之前對「GeoSR 是什麼、為什麼這樣設計、用什麼跑」三個問題都已有答案。

### 3.5 Experiments (overview narrative)

(1380 words)

Experiments 章節以「驗證—消融—分析」的三段結構展開，目標明確：證明 GeoSR 在 static 與 dynamic spatial reasoning 上同時有效，並逐步剝離各個設計元件以歸因增益來源。作者在開頭即點出實驗會涵蓋兩類 benchmark 加上 ablation 與超參數、計算成本分析，預先框定整章的論證範圍。

§4.1 Static Spatial Reasoning 採 VSI-Bench 作為主場景，benchmark 含 5k+ QA 對、288 段真實影片，場景以剛性為主但 viewpoint 與 visibility 變化大，正好考驗 viewpoint-robust 的幾何理解。任務分為 numerical（Obj. Cnt.、Abs. Dist.、Obj. Size、Room Size）與 multiple-choice（Rel. Dist.、Rel. Dir.、Route Plan、Appr. Order）兩類，依官方協定報告 multi-choice accuracy 與 numerical 的 mean relative accuracy。比較對象分三組：proprietary API 模型（GPT-4o、Gemini-1.5 系列）作上限參考；open-source 通用 video / VLM 模型（Qwen2.5-VL、LLaVA-Video、InternVL 系列）；以及 spatial reasoning 專用模型（SAT-LLaVA-Video、SPAR、Spatial-MLLM、VG-LLM）。Table 1 顯示 GeoSR 在同一評測協議下取得 51.9 平均分，超過 VG-LLM 的 50.7 與 Spatial-MLLM 的 48.4，於 Obj. Cnt.、Rel. Dist.、Route Plan 等子任務上為最佳或次佳。作者強調這代表 geometry tokens 在 reasoning 過程中真的被使用，而非只是 auxiliary context。

§4.2 Dynamic Spatial Reasoning 切到 DSR-Bench，含 1484 QA 對、575 段 in-the-wild 影片，因 object 與 camera motion 而需要 spatiotemporal consistency 才能答對。題型分 absolute、relative、Non-Temp. 三大類，再細分 distance、direction、orientation、speed、speed comparison、direction prediction 等子任務。作者比較 proprietary 模型（GPT-4o、GPT-5、Gemini-2.5）、通用 video/VLM 模型（Qwen2.5/3-VL、LLaVA-Video、VideoRefer、InternVL3.5）以及 spatial reasoning 模型（VLM-3R、VG-LLM、GSM）。Table 2 中 DSR-Bench 對通用模型挑戰極大（多落在 23–31），spatial reasoning 模型則明顯領先；GeoSR 平均分達 66.1，顯著超越前 SOTA GSM 的 58.9，並在每一個子任務都取得最高分。作者把這個結果解讀為：dynamic reasoning 對 geometry cues 特別敏感，而 GeoSR 透過 unleashing geometry 與 adaptive fusion 把這個 modality 的潛力真正釋放出來。

§4.3 Ablation Studies 將設計拆解，分別在 Table 3（static）與 Table 4（dynamic）對 Geometry-Unleashing Masking（Geo. Mask.）、Geometry-Guided Fusion（Geo. Fus.）、與原本的 naive fusion（Ori. Fus.）做組合對照。完整 GeoSR (a) 是參考點；把 Geo. Fus. 換回 Ori. Fus. (b) 兩個 benchmark 都掉分，顯示 naive fusion 無法把 geometry 變成 actionable evidence；只留 Geo. Mask.、移除兩種 fusion (c) 跌得更多，說明單純 masking 沒有合理的路由機制無法奏效；反過來保留 Geo. Fus.、移除 Geo. Mask. (d) 也明顯下滑，代表沒有 shortcut suppression 模型仍會 underutilize geometry；只留 Ori. Fus. (e) 則比 (d) 更差，再次凸顯 adaptive routing 的價值。最關鍵的是無 geometry 變體 (f)：static 上 (e) 與 (f) 差距小，呼應「直接注入幾何在靜態場景下增益有限」；dynamic 上 (f) 反而勝過 (e)，證實「未經控制的 geometry 注入可能負面」這個 Introduction 中的核心觀察，也成為 GeoSR 設計動機的反向佐證。

§4.4 Analysis 補完整體圖像。Table 5 的超參掃描驗證 $\gamma=0.8$、$\beta=0.5$ 是 sweet spot——太小留下 shortcut、太大過度刪除 context 損及穩定性。Table 6 的成本量測顯示，相對 vanilla Qwen2.5-VL-7B（0.37s、8.76B、18.04GB），加上 geometry baseline 為 0.40s / 9.16B / 18.81GB，GeoSR 進一步只增為 0.41s / 9.23B / 18.95GB，額外負擔幾乎來自 geometry projection 與 gating module，幾乎可忽略。這個分析支持作者「設計輕量但有效」的主張，並把 Experiments 章節收束到「強有效、穩消融、可負擔」三個結論，自然導入 §5 對全篇貢獻的總結。

### 3.6 Conclusion / Limitations / Future Work

(310 words)

Conclusion 章節（§5，含 Appendix C 的 Limitations 與 Future Work）以一段半的篇幅濃縮整篇論點。作者首先把研究問題重新框定為 existing geometry-aware VLMs for spatial reasoning 的一種 failure mode：在 naive token fusion 與 standard fine-tuning 的常見配方下，注入的 geometry tokens 往往未被善用，造成有限增益甚至負增益；這意味著 geometry priors 雖具資訊量，卻不會自動被 VLM backbone 視為可行動的證據。

接著作者重申 GeoSR 是針對此 failure mode 的對策，包含兩個互補設計：Geometry-Unleashing Masking 在訓練時弱化 vision-driven shortcuts、迫使模型查詢 geometry tokens；Geometry-Guided Fusion 透過 fine-grained gate 自適應路由 geometry evidence，使 geometry 在真正有用且必要的位置佔主導地位。這個摘要既呼應 Introduction 的「effective + reasonable」雙軸原則，也與 Experiments 中 ablation 對應，確保論文敘事閉環。最後作者強調 static 與 dynamic 兩類 benchmark 上一致改進，dynamic 設定的增益尤其顯著，這與 §4.3 中 motion 與 occlusion 削弱 appearance cues 的解讀一致。

Appendix C 的 Limitations and Future Work 則把鏡頭從 model side 拉到 data side。作者誠實指出 GeoSR 聚焦於 model-side 改進，但現有 benchmarks 的資料品質可能成為進一步進步的瓶頸：訓練與評測資料多由 automatic 或 semi-automatic pipelines 構造，部分問題在幾何上具有歧義、部分標註與視覺證據未必完全對齊，Figures 6 與 7 提供了具體例子（如 elephant vs. human 速度比較、character 與 table 之相對位置），這些 ambiguity 會同時影響所有方法。據此作者點出未來方向：在持續推動模型設計之外，必須改進資料品質，特別是 geometry-aware 的問題構造與 annotation consistency。整段把貢獻、局限與展望串成首尾呼應的結構，留下「方法層面已被解決、資料層面值得後續投入」的明確訊號。

## 4. Critical Profile

### 4.1 Highlights

- 提出一個 reproducible 的反直覺診斷：在 dynamic 場景下，naive geometry injection（Table 4 row (e) 62.8）甚至比完全不接 geometry branch（row (f) 64.0）更差，正面驗證 geometry tokens 在常見 pipeline 中真的被忽視（Sec 1, p.2；Fig 1, p.3）。
- Geometry-Unleashing Masking (GUM) 提供兩種互補設計：static 走 MAE-style random mask；dynamic 走 cross-attention TopK，由 QFormer 的 attention probability $A$ 計算 relevance score $s$ 並選最關鍵的 geometry 位置遮蔽對應 vision token（Sec 3.2, Eqs. 8–10, p.8）。
- Geometry-Guided Fusion (GGF) 用 token-and-channel-wise gate $\alpha = \sigma(\mathbf{W}_g[V \Vert G] + b_g)$ 取代 additive 或 concat fusion，讓 geometry 在需要時主導，避免 indiscriminate mixing 稀釋訊號（Sec 3.3, Eq. 12, p.9）。
- VSI-Bench 上以 Qwen2.5-VL-7B + VGGT 取得 avg 51.9，超越 VG-LLM 50.7、Spatial-MLLM 48.4 與 InternVL3-78B 48.4；Room Size 62.3、Appr. Order 59.5 為該 benchmark 新 SOTA（Table 1, p.11）。
- DSR-Bench 上以 Qwen2.5-VL-7B + π3 取得 avg 66.1，相對最強對手 GSM 58.9 提升 7.2 個百分點，且在全部 13 個 subtask 中皆為最佳（Table 2, p.12）。
- Ablation 顯示兩個元件互補：full model 66.1，去掉 GGF 換回 Ori. Fus. 降到 64.7，去掉 GUM 降到 64.9；同時 (f) 無 geometry 64.0 > (e) Ori. Fus. 62.8，再次量化「naive fusion 反向有害」（Table 4, p.13）。
- Computational overhead 極小：相對 baseline 9.16B / 0.40s / 18.81GB，GeoSR 為 9.23B / 0.41s / 18.95GB，幾乎只是加上 gating 與 projection（Table 6, p.14）。
- 對 QFormer 結構在 static 上的 ablation（Table 7, p.19）顯示 +QFormer 沒有提升（51.9 → 51.8），佐證作者把 query-style 機制只用在 dynamic 的 design choice。
- 超參數 $\gamma=0.8$、$\beta=0.5$ 在 DSR-Bench 上對 sweep 相對穩定（Table 5, p.14：$\gamma$ 0.4–0.8 落在 65.0–66.1，$\beta$ 0.3–0.7 落在 64.5–66.1）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- Appendix C（p.19）僅承認 dataset-side 限制：訓練/評測資料是 automatic 或 semi-automatic 流程產生，部分問題從幾何角度本身就 ambiguous，annotation 不一定對齊實際視覺證據（Fig 6 速度比較模糊、Fig 7 遮擋導致空間關係難判），並指出這會同時影響所有方法。論文沒有公開討論 method-side 的結構性 limitation。

#### 4.2.2 Phyra-inferred

- Ablation row (c)「GUM only」其實是「masking 開啟但 geometry 不接入 backbone」（Table 3/4 三欄都未勾），所以 58.1 / 49.6 的低分既包含「masking 帶來的訊號損失」也包含「沒有 geometry 補位」，無法獨立量化 GUM 的純效果（Table 3, 4, p.13）。
- Static 的相對提升非常有限（avg +1.2 over VG-LLM），且在 Obj. Size 上 57.4 < VG-LLM 58.6、在 Rel. Dir 上 44.4 < Spatial-MLLM 46.2，論文沒有針對這些 regression 給出解釋（Table 1, p.11）。
- Dynamic 強勢提升與 3D backbone 的更換糾纏在一起：GSM 用的是 [36] 的早期 dynamic prior，GeoSR 改用 π3 [36]（更新版本）作為 geometric tokenizer，但全文沒有「同樣 GSM 方法 + π3」的對照組來分離 geometry encoder 與 GUM/GGF 的貢獻（Sec 3.4, p.10；Table 2, p.12）。
- TopK masking 與 GGF 都來自同一條 cross-attention 通路（Eq. 8 的 $A$ 同時用來計算 mask 與後續 retrieval 的 $\tilde{F}_G$），形成「決定遮哪裡的人」與「決定要拿哪些 geometry 的人」是同一個 attention，這種耦合可能讓 mask 偏向 fusion 已經偏好的位置而非真正的 appearance-shortcut 位置（Sec 3.2, Eqs. 8–10, p.8；Sec 3.3, Eq. 14, p.9）。
- Inference 階段 mask 完全關閉（Sec 3.4, p.10），所以 GUM 對最終模型的作用本質上是 training-time regularization，不是讓推論時真的「不能看 appearance」，論文未量化 inference-time mask 的效果。
- 全部實驗只用 Qwen2.5-VL-7B 單一 backbone、單一 seed、單一 epoch（Sec 3.4, p.10），沒有報告 std、沒有跨 backbone 規模的趨勢，65–66 區間的差異是否在 noise floor 之內無法判定。
- 「geometry 真的被使用了」這個核心 claim 全部由下游 accuracy 推論而來，論文沒有對 gate $\alpha$ 的分布、attention shift、或對 geometry token 做 input-ablation 等 causal evidence 來直接證明 geometry 已經 actionable（Sec 3.3, 4, 全篇）。
- DSR-Train → DSR-Bench 是同一份工作 [53] 的訓練集與測試集，論文沒有報告其 split 設計（場景重疊、bounding-box 重複等），dynamic 上的大幅提升在 in-distribution generalization 與 cross-dataset transfer 之間沒有被分離（Sec 3.4, 4.2, p.10–12）。

### 4.3 Phyra's Judgment (summary)

GeoSR 真正新穎的部分是「為這個失敗模式命名並用 ablation 重現它」（naive injection 在 dynamic 上比 no-geometry 還差），這個診斷比兩個技術元件本身更有貢獻。GUM 與 GGF 個別來看都是已知套路（MAE-style masking + sigmoid gated fusion），其價值在於組合起來解這個特定問題；但論文沒有對「geometry 是否真的被使用」做機制層級的驗證，gate 分布、attention 變化、causal intervention 全部缺席。Static 的提升幅度落在 noise 量級邊緣，dynamic 的大幅提升又與 3D encoder 換新糾纏，目前難以判定 7.2 個點究竟有多少來自 GUM/GGF、多少來自 π3。

## 5. Methodology Deep Dive

### 5.1 Method Overview

GeoSR 在標準 VLM backbone (Qwen2.5-VL-7B) 之外，再加上一個被凍結的 geometric tokenizer (靜態場景使用 VGGT，動態影片使用 π3)，由它額外抽取出 implicit geometry tokens $F_G$，與原本的 2D vision tokens $F_V$ 並列輸入 LLM。作者觀察到一個 reproducible failure mode：當 $F_G$ 只是被加總 (additive fusion) 或拼接 (QFormer-style concat) 進 VLM、後續再做 standard fine-tuning 時，模型傾向於回退到 $F_V$ 中的 appearance shortcut，使 geometry tokens 形同 dispensable side signal，甚至在動態場景中拖累效能。GeoSR 不修改 tokenizers 與 LLM 架構，只在 geometry 分支與 LLM 之間插入兩個互補策略。

第一個策略是 **Geometry-Unleashing Masking (GUM)**，於訓練時以機率 $\beta=0.5$ 啟用，並以遮蔽率 $\gamma=0.8$ 將 $F_V$ 中部分 token 直接清零，迫使 VLM 在無法仰賴外觀紋理時主動向 geometry stream 求解。靜態設定下採 MAE-style 隨機遮蔽 (Eq. 7)；動態設定下，先以 learnable bottleneck $B$ 透過 cross-attention 從 $F_P$ 擷取 question intent 得到 $F_B$ (Eq. 2)，再以 $F_B$ 對 $\hat F_G$ 做 cross-attention 拿到 question-relevant 的 condensed evidence $Z_G$ (Eq. 8)，並從該 attention 的 head 與 bottleneck 維度平均後做 min-max normalization 得到 per-token relevance score $s$ (Eq. 9)，依 $s$ 經 2D spatial interpolation 對齊到 $(H_V, W_V)$ 後以 TopK 挑出最關鍵的 $K=\lceil\gamma H_V W_V T\rceil$ 個位置作為遮蔽集合 (Eq. 10)。Inference 階段關閉遮蔽，餵入完整 $F_V$。

第二個策略是 **Geometry-Guided Fusion (GGF)**，以 token-and-channel-wise gated routing 取代均勻融合。對 LayerNorm 後的 $\tilde F_V$ 與 $\tilde F_G$ 沿 channel 拼接後，過一層線性映射並施加 sigmoid，得到細粒度 gate $\alpha \in (0,1)^{(H_V W_V T)\times C}$，最終融合為 $F = \alpha \odot V + (1-\alpha) \odot G$ (Eq. 12, 15)。靜態設定下 $\tilde F_G = \mathrm{MLP}(\mathrm{Reshape}(F_G))$；動態設定下先以 $\hat F_G' = \mathrm{Interp}(\hat F_G, (H_V, W_V))$ 對齊解析度 (Eq. 11)，再以 $\hat F_G'$ 為 query、$Z_G$ 為 key/value 做 cross-attention 重新分散回 spatiotemporal grid (Eq. 14)。動態場景中還會把全域 $Z_G$ 額外拼接在 $F$ 之後一同送入 VLM，以保留 global dynamic context。GUM 處理「使用是否有效」的問題，GGF 處理「使用是否合理」的問題，兩者疊加才能把 geometry tokens 真正轉成 actionable evidence。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: T frames {I_t}, t=1..T  [B, T, H_I, W_I, 3]   +   text prompt Q
   │
   ├──[Visual Tokenizer (Qwen2.5-VL, frozen)]
   │     └─→ F_V   [B, H_V·W_V·T, C]
   │
   ├──[Geometric Tokenizer (VGGT / π3, frozen)]
   │     └─→ F_G   [B, H_G·W_G·T, C_G]
   │           └─MLP─→ F̂_G   [B, H_G·W_G·T, C]
   │
   └──[Prompt Tokenizer (frozen)]
         └─→ F_P   [B, L_P, C]

  ┌─ Geometry-Unleashing Masking (training only) ───────────────────┐
  │  B  [B, L_B=32, C]  (learnable, dynamic-only)                   │
  │  F_B = CrossAttn₁(B, F_P)                       [B, L_B, C]     │
  │  Z_G, A = CrossAttn₂(F_B, F̂_G)                                  │
  │     Z_G [B, L_B, C]   A [B, h, L_B, H_G·W_G·T]                  │
  │  s_j = norm( mean_{k,i} A[:,k,i,j] )            [B, H_G·W_G·T]  │
  │                                                                 │
  │  Static:   M = Rand(H_V·W_V·T, K)               K=⌈γ H_V W_V T⌉ │
  │  Dynamic:  s' = Interp(s, (H_V,W_V,T)) ;  M = TopK(s', K)       │
  │  δ ~ Bernoulli(β=0.5);                                          │
  │  m_j = 0 if (δ=1 ∧ j∈M) else 1                  [B, H_V·W_V·T]  │
  │  F̃_V = m ⊙ F_V                                  [B, H_V·W_V·T, C]│
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─ Geometry-Guided Fusion ────────────────────────────────────────┐
  │  Static:   F̃_G = MLP(Reshape(F_G))              [B, H_V·W_V·T, C]│
  │  Dynamic:  F̂_G' = Interp(F̂_G,(H_V,W_V))         [B, H_V·W_V·T, C]│
  │            F̃_G  = CrossAttn₃(F̂_G', Z_G)         [B, H_V·W_V·T, C]│
  │                                                                 │
  │  V = LN_v(F̃_V),   G = LN_g(F̃_G)                                 │
  │  α = σ( W_g · [V ‖ G] + b_g )                   [B, H_V·W_V·T, C]│
  │  F = α ⊙ V + (1−α) ⊙ G                          [B, H_V·W_V·T, C]│
  │                                                                 │
  │  Static:   feed F                               [B, H_V·W_V·T, C]│
  │  Dynamic:  feed [F, Z_G]                        [B, H_V·W_V·T+L_B, C]│
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  [VLM Backbone (Qwen2.5-VL-7B, fine-tuned)]
        ( fused tokens , F_P [B, L_P, C] ) ──→ answer text
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Visual Tokenizer (Frozen)

**Function:** 將輸入影格序列編碼為 2D vision tokens，作為 VLM 的標準視覺輸入。

**Input:**
- Name: $\{I_t\}_{t=1}^T$
- Shape: $[B, T, H_I, W_I, 3]$
- Source: 輸入影片

**Output:**
- Name: $F_V$
- Shape: $[B, H_V \cdot W_V \cdot T, C]$
- Consumer: GUM (5.3.5)、GGF (5.3.6)

**Processing:**

每個影格依 Qwen2.5-VL 的 visual encoder 切 patch 並 embed 為 token 序列，跨影格沿時間維串接成 $(H_V W_V T)$ 個 token。Tokens 在送入後續模組前已配備 spatiotemporal RoPE，論文敘述時為簡潔將 PE 省略。

**Key Formulas:**

$$
F_V \in \mathbb{R}^{B \times (H_V W_V T) \times C_V},\quad C_V = C
$$

**Implementation Details:** Backbone 為 Qwen2.5-VL-7B；visual encoder 在訓練時保持 frozen，僅 GGF 模組與 LLM 部分受 fine-tuning 影響。

#### 5.3.2 Geometric Tokenizer (Frozen)

**Function:** 由相同的單目影格抽取 implicit geometry tokens，提供 3D 結構與時序幾何證據。

**Input:**
- Name: $\{I_t\}_{t=1}^T$
- Shape: $[B, T, H_I, W_I, 3]$
- Source: 輸入影片 (與 visual tokenizer 共用)

**Output:**
- Name: $F_G$ (再經 MLP 投影成 $\hat F_G$)
- Shape: $F_G \in [B, H_G W_G T, C_G]$；$\hat F_G \in [B, H_G W_G T, C]$
- Consumer: GUM 中的 cross-attention (動態) 與 GGF 的 geometry stream

**Processing:**

由 pretrained 3D foundation model 在自身解析度下產生稠密 geometry tokens，然後以一層 MLP 把通道對齊到 LLM hidden size $C$。$H_G, W_G$ 不一定等於 $H_V, W_V$，故後續模組需要 spatial interpolation 對齊。

**Key Formulas:**

$$
\hat F_G = \mathrm{MLP}(F_G),\quad \hat F_G \in \mathbb{R}^{B \times (H_G W_G T) \times C}
$$

**Implementation Details:** 靜態設定使用 VGGT，動態設定改用 π3 (作者表示後者更能捕捉 dynamic geometry cues)；3D 模型在訓練時 frozen。

#### 5.3.3 Prompt Tokenizer (Frozen)

**Function:** 將語言指令 $Q$ 編碼為 text tokens，供 bottleneck 抽取 question intent 與 LLM 自身條件生成使用。

**Input:**
- Name: $Q$
- Shape: 文字字串
- Source: 使用者輸入

**Output:**
- Name: $F_P$
- Shape: $[B, L_P, C]$
- Consumer: 5.3.4 的 $\mathrm{CrossAttn}_1$、VLM backbone

**Processing:**

採 Qwen2.5-VL 的內建 text tokenizer 與 embedding，frozen 不訓練，輸出維度與 LLM 共用同一 $C$。

**Key Formulas:** 沿用 Qwen2.5-VL 標準 tokenization，論文未額外列出公式。

**Implementation Details:** $C_P = C$ 與 visual / geometry 投影後的通道一致，方便 cross-attention 與後續拼接。

#### 5.3.4 Bottleneck Cross-Attention (Dynamic Only)

**Function:** 以一組 learnable bottleneck tokens 把 question intent 與 question-relevant geometry 壓縮為固定長度的 condensed evidence，並回收 attention probability 作為 TopK 遮蔽用的 relevance score。

**Input:**
- Name: $B$ (learnable)、$F_P$、$\hat F_G$
- Shape: $B \in [B_{\!batch}, L_B, C]$；$F_P \in [B_{\!batch}, L_P, C]$；$\hat F_G \in [B_{\!batch}, H_G W_G T, C]$
- Source: 模組自身參數；prompt tokenizer (5.3.3)；geometric tokenizer (5.3.2)

**Output:**
- Name: $F_B$、$Z_G$、$A$、$s$
- Shape: $F_B, Z_G \in [B_{\!batch}, L_B, C]$；$A \in [B_{\!batch}, h, L_B, H_G W_G T]$；$s \in [B_{\!batch}, H_G W_G T]$
- Consumer: $Z_G$ → GGF 與 dynamic 模式下的 LLM 拼接；$s$ → GUM 的 TopK

**Processing:**

bottleneck $B$ 先以 cross-attention 對 $F_P$ 抽取 question intent 得到 $F_B$ (Eq. 2)，再以 $F_B$ 為 query、$\hat F_G$ 為 key/value 做第二次 cross-attention 取得 $Z_G$ (Eq. 8)。第二層 attention 的機率張量 $A$ 沿 head 與 bottleneck-tokens 維度做平均得到 $u_j$，再以 min-max 正規化得到 $s_j$ (Eq. 9)，做為「哪些 geometry token 對當前問題最相關」的指標。

**Key Formulas:**

$$
F_B = \mathrm{CrossAttn}_1(B,\ F_P)
$$

$$
Z_G,\ A = \mathrm{CrossAttn}_2(F_B,\ \hat F_G)
$$

$$
u_j = \frac{1}{h L_B}\sum_{k=1}^{h}\sum_{i=1}^{L_B} A_{k,i,j},\quad s_j = \frac{u_j - \min(u)}{\max(u) - \min(u) + \epsilon}
$$

**Implementation Details:** $L_B = 32$，僅在 dynamic 配置中啟用 (對應 GSM 的 QFormer fusion baseline)；$\epsilon$ 為數值穩定項。模組與 GGF 一同從零訓練。

#### 5.3.5 Geometry-Unleashing Masking (Training Only)

**Function:** 隨機關閉一部分 vision-token 位置，截斷 appearance shortcut，迫使 VLM 在缺失外觀資訊時改用 geometry stream。

**Input:**
- Name: $F_V$；動態模式下另需 $s$
- Shape: $F_V \in [B, H_V W_V T, C]$；$s \in [B, H_G W_G T]$
- Source: 5.3.1 visual tokenizer；動態模式下 5.3.4 的 relevance score

**Output:**
- Name: $\tilde F_V$
- Shape: $[B, H_V W_V T, C]$
- Consumer: GGF (5.3.6)

**Processing:**

每個 forward 抽 $\delta \sim \mathrm{Bernoulli}(\beta)$ 決定是否啟用遮蔽。啟用時挑選大小為 $K = \lceil \gamma (H_V W_V T) \rceil$ 的位置集合 $\mathcal{M}$：靜態設定為均勻隨機 (Eq. 7)；動態設定先把 $s$ 經 2D spatial interpolation 對齊到 $(H_V, W_V)$ 解析度後取 TopK (Eq. 10、11)。再由 $m_j = 0$ on $\mathcal{M}$、其他位置 $m_j = 1$ 構成二元遮罩，最終 $\tilde F_V = m \odot F_V$ (Eq. 5、6)。Inference 階段不抽 $\delta$、不啟動遮蔽。

**Key Formulas:**

$$
m_j = \begin{cases} 0, & \delta = 1 \wedge j \in \mathcal{M} \\ 1, & \text{otherwise} \end{cases},\quad \delta \sim \mathrm{Bernoulli}(\beta)
$$

$$
\mathcal{M}_{\text{static}} = \mathrm{Rand}(H_V W_V T, K),\quad \mathcal{M}_{\text{dynamic}} = \mathrm{TopK}(s_{\text{interp}}, K)
$$

$$
\tilde F_V = m \odot F_V,\quad K = \lceil \gamma (H_V W_V T) \rceil
$$

**Implementation Details:** 靜態與動態皆使用 $\gamma = 0.8$、$\beta = 0.5$。動態模式下 $s$ 是先在 $(H_G, W_G)$ 上產生再插值到 $(H_V, W_V)$，因此 TopK 的對應關係與 vision token 解析度一致。

#### 5.3.6 Geometry-Guided Fusion (GGF)

**Function:** 在 token 與 channel 兩個維度同時學一個細粒度 gate $\alpha$，讓 geometry feature 在需要時主導融合表示，避免幾何訊號被均勻混合稀釋。

**Input:**
- Name: $\tilde F_V$、$F_G$ (靜態) 或 $\hat F_G$、$Z_G$ (動態)
- Shape: $\tilde F_V \in [B, H_V W_V T, C]$；$\hat F_G \in [B, H_G W_G T, C]$；$Z_G \in [B, L_B, C]$
- Source: GUM (5.3.5)、geometric tokenizer (5.3.2)、bottleneck cross-attention (5.3.4)

**Output:**
- Name: $F$ (動態額外 append $Z_G$)
- Shape: $F \in [B, H_V W_V T, C]$；動態送入 LLM 的拼接序列為 $[B, H_V W_V T + L_B, C]$
- Consumer: VLM backbone (5.3.7)

**Processing:**

先得到對齊到 vision-token 解析度的 geometry feature $\tilde F_G$。靜態：$\tilde F_G = \mathrm{MLP}(\mathrm{Reshape}(F_G))$ (Eq. 13)。動態：先 $\hat F_G' = \mathrm{Interp}(\hat F_G, (H_V, W_V))$ 對齊解析度 (Eq. 11)，再以 $\hat F_G'$ 為 query、$Z_G$ 為 key/value 做 cross-attention，把全域 condensed evidence 重新分散回 spatiotemporal grid (Eq. 14)。然後對 $\tilde F_V, \tilde F_G$ 各做 LayerNorm，沿 channel 拼接 (圖 3 中標 `C` 的串接)，過 $W_g, b_g$ 與 sigmoid 得到 token-and-channel-wise gate $\alpha$ (Eq. 12)，最終以 $F = \alpha \odot V + (1-\alpha) \odot G$ 輸出 (Eq. 15)。動態模式下還會把 $Z_G$ 額外拼接到 $F$ 之後再餵入 LLM。

**Key Formulas:**

$$
\boldsymbol{V} = \mathrm{LN}_v(\tilde F_V),\quad \boldsymbol{G} = \mathrm{LN}_g(\tilde F_G)
$$

$$
\boldsymbol{\alpha} = \sigma\big(\mathbf{W}_g\, [\boldsymbol{V} \,\|\, \boldsymbol{G}] + \boldsymbol{b}_g\big),\quad \boldsymbol{\alpha} \in (0,1)^{B \times (H_V W_V T) \times C}
$$

$$
F = \boldsymbol{\alpha} \odot \boldsymbol{V} + (1-\boldsymbol{\alpha}) \odot \boldsymbol{G}
$$

**Implementation Details:** $\mathbf{W}_g, \mathbf{b}_g$ 為唯一新增的 fusion 參數；gate 同時在 token 與 channel 維度計算，因此可在不同位置、不同通道分別決定 vision 或 geometry 的權重。動態場景把全域 $Z_G$ 進一步附在 $F$ 之後，避免細粒度 fusion 丟失整體動態語意。

#### 5.3.7 VLM Backbone (Fine-Tuned)

**Function:** 接收融合後的多模態 token 序列與 prompt tokens，自回歸生成空間推理問題的答案。

**Input:**
- Name: $F$ (靜態) 或 $[F, Z_G]$ (動態)、$F_P$
- Shape: $[B, H_V W_V T (+L_B), C]$、$[B, L_P, C]$
- Source: GGF (5.3.6)、prompt tokenizer (5.3.3)

**Output:**
- Name: 答案 token 序列
- Shape: 自回歸生成的 token 序列
- Consumer: end-user / 評測腳本

**Processing:**

採標準 causal LM 自回歸生成；訓練目標為對應資料集中問題的答案 token 上的 cross-entropy。在 fine-tuning 階段 LLM 與 GGF 一同更新，tokenizers 與 3D 幾何模型保持 frozen。Inference 階段 GUM 關閉，$F_V$ 完整餵入 fusion module。

**Key Formulas:** 沿用 Qwen2.5-VL 的 next-token prediction，論文未額外給出公式。

**Implementation Details:** Backbone 為 Qwen2.5-VL-7B。靜態設定資料為 SPAR-7M 與 LLaVA-Hound 的子集 (與 VG-LLM 相同切分)，跑 1 epoch、Adam optimizer、batch size 64、learning rate $1\times10^{-5}$、linear warmup 150 steps、cosine decay 至 0；動態設定資料為 DSR-Train，跑 1 epoch、Adam、batch size 32、learning rate $2\times10^{-7}$、linear warmup 50 steps。Bottleneck length $L_B = 32$，遮蔽超參 $\gamma=0.8$、$\beta=0.5$。硬體為 4×H200 (141GB)；靜態以 DeepSpeed ZeRO-2 訓練約 14 小時，動態以 ZeRO-3 Offload 訓練約 20 小時。Inference 時關閉 GUM。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| SPAR-7M | Static spatial QA 監督訓練 | 7M-level QA pairs（沿用 [50] 的 split） | train |
| LLaVA-Hound | 一般影片指令調整資料 | the paper does not specify | train（與 SPAR-7M 同 split 設定） |
| DSR-Train | Dynamic spatial reasoning 監督訓練 | 依官方 protocol [53] | train |
| VSI-Bench | Static spatial reasoning 評測 | 5k+ QA pairs，288 部真實影片 | test |
| DSR-Bench | Dynamic spatial reasoning 評測 | 1484 QA pairs，575 部 in-the-wild 影片 | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Mean Relative Accuracy (numerical) | VSI-Bench 數值題官方指標，於多種相對誤差容忍度下取平均 | yes |
| Accuracy (multiple-choice) | VSI-Bench 選擇題與 DSR-Bench 各子類型的標準準確率 | yes |
| Average | 跨子任務平均（VSI-Bench、DSR-Bench 皆採 Avg. 欄位） | yes |
| Runtime / Model Size / Peak Memory | 在單顆 H200 上量測推論時間、參數量與峰值記憶體 | no |

### 6.3 Training and Inference Settings

- 硬體：4×H200 GPU（每張 141GB）；static 訓練約 14 小時，dynamic 約 20 小時。
- 分散式：static 使用 DeepSpeed ZeRO-2，dynamic 使用 ZeRO-3 Offload。
- Backbone：Qwen2.5-VL-7B；3D 模型 static 用 VGGT、dynamic 用 $\pi^3$，tokenizer 與 3D 模型訓練時凍結。
- Optimizer：Adam（兩種設定皆訓練 1 epoch）。
- Static：batch size $64$、learning rate $1\times 10^{-5}$、linear warmup 150 steps 後 cosine decay 至 $0$；masking ratio $\gamma=0.8$、enable probability $\beta=0.5$。
- Dynamic：batch size $32$、learning rate $2\times 10^{-7}$、linear warmup 50 steps（後續 schedule the paper does not specify）；bottleneck length $L_B=32$、$\gamma=0.8$、$\beta=0.5$。
- Inference：與訓練相同流程，但停用 masking，將完整 vision tokens 餵入 fusion module。
- 隨機種子與多次重跑策略：the paper does not specify。

### 6.4 Main Results

VSI-Bench（static spatial reasoning，Avg. 為平均分數）：

| Method | Avg. | Obj. Cnt. | Rel. Dir. | Notes |
|---|---|---|---|---|
| Gemini-1.5-Pro | 48.8 | 49.6 | 48.1 | proprietary API 上限參考 |
| Qwen2.5-VL-7B | 33.0 | 40.9 | 38.5 | 同 backbone 之純 VLM 基線 |
| InternVL3-78B | 48.4 | 71.2 | 39.5 | 大型開源 VLM |
| Spatial-MLLM | 48.4 | 65.3 | 46.2 | geometry-aware 基線 |
| VG-LLM | 50.7 | 67.9 | 40.7 | 直接對手（同 SPAR-7M split） |
| **GeoSR (Ours)** | **51.9** | **68.3** | **44.4** | 全 8 個子任務中於 Obj. Cnt./Abs. Dist./Room Size/Rel. Dist./Route Plan/Appr. Order 6 項奪冠或同分最佳 |

DSR-Bench（dynamic spatial reasoning，Avg. 為平均分數）：

| Method | Avg. | Abs. Dist. | Rel. Dist. | Notes |
|---|---|---|---|---|
| GPT-5 | 30.8 | 21.1 | 44.3 | 最強 proprietary 參考 |
| Qwen2.5-VL-7B | 23.5 | 18.8 | 19.3 | 同 backbone 之純 VLM 基線 |
| VLM-3R | 31.4 | 28.2 | 23.8 | geometry-aware 基線 |
| VG-LLM | 38.4 | 55.2 | 36.3 | static 強對手延伸到 dynamic |
| GSM | 58.9 | 87.0 | 76.1 | dynamic 上的 prior SoTA |
| **GeoSR (Ours)** | **66.1** | **88.0** | **83.0** | 13 個子任務全部取得最高分 |

### 6.5 Ablation Studies

論文於 Table 3（static）與 Table 4（dynamic）以 (a) 完整 GeoSR 為參考，逐一拆解三個元件 Geometry-Unleashing Masking（Geo. Mask.）、Geometry-Guided Fusion（Geo. Fus.）與 baseline 的 Original Fusion（Ori. Fus.）。

- (b) 將 Geo. Fus. 換成 Ori. Fus.（仍保留 Geo. Mask.）：static Avg. 從 $51.9 \to 50.0$、dynamic Avg. 從 $66.1 \to 64.7$，顯示 naive fusion 無法把 geometry tokens 變成可用證據。此項是診斷型 ablation，直接針對「fusion 機制本身」做變因控制。
- (c) 僅留 Geo. Mask.（無任何 fusion 模組）：static Avg. $\to 49.6$、dynamic Avg. $\to 58.1$（dynamic 掉幅特別大），證明僅靠遮罩無法把 geometry 資訊路由進 backbone，需要 routing 機制配合。屬診斷型。
- (d) 移除 Geo. Mask.、僅留 Geo. Fus.：static $\to 50.9$、dynamic $\to 64.9$。顯示沒有 shortcut 抑制時，模型仍會低度利用 geometry。屬診斷型。
- (e) 僅留 Ori. Fus.（既無 Geo. Mask. 也無 Geo. Fus.）：static $\to 50.2$、dynamic $\to 62.8$，再次顯示 adaptive routing 優於原生 fusion。屬診斷型。
- (f) 完全移除 geometry 分支：static $\to 49.8$、dynamic $\to 64.0$。值得注意的是 dynamic 上 (f) 反而高於 (e)，呼應 Fig. 1 「naive geometry injection 可能反而有害」的主張。此項較接近**動機驗證型**ablation，而非僅是 sanity check，因為它直接證偽「加 geometry 一定有幫助」的假設。
- 超參數分析（Table 5，DSR-Bench）：$\gamma\in\{0.4,0.6,0.8\}$ 對應 Avg. $\{65.0, 65.9, 66.1\}$；$\beta\in\{0.3,0.5,0.7\}$ 對應 $\{64.9, 66.1, 64.5\}$。屬合理但範圍偏窄的 sensitivity check（每個 axis 僅 3 個點）。
- Appendix B：在 static 上加入 QFormer 變體，Avg. 由 $51.9 \to 51.8$，論文據此論證 static 任務不需 global temporal aggregation。此屬架構選擇驗證型 ablation。

整體而言，主要 ablation 為診斷型（直接拆解 GeoSR 的兩個提案元件），但缺少對 masking 樣式（random vs. TopK 互換）以及 gate 設計（token-and-channel vs. token-only）的對照，導致無法完全分離兩元件對最終增益的貢獻。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — VSI-Bench 上對齊 VG-LLM/Spatial-MLLM 等 geometry-aware SoTA、DSR-Bench 上對齊 GSM 等同領域最強對手，並列入 GPT-4o/GPT-5/Gemini-2.5-Pro 為上限參考。
- [covered] Has cross-task / cross-dataset evaluation — 同時在 static（VSI-Bench）與 dynamic（DSR-Bench）兩個結構不同的 benchmark 評測，並對應使用不同 3D backbone（VGGT vs. $\pi^3$）。
- [covered] Has ablations that diagnose the new components — Tables 3、4 透過 (a)–(f) 系統性切換 Geo. Mask. 與 Geo. Fus.，(f) 還反向驗證 motivation（geometry 注入有時反而有害）。
- [missing] Has a scaling study — 僅使用 Qwen2.5-VL-7B 一個 backbone size，未報告 3B/32B/72B 等不同規模或不同訓練步數的 scaling 趨勢。
- [partial] Has an efficiency / wall-clock comparison — Table 6 給出 GeoSR vs. baseline 的 0.37s/0.40s/0.41s 推論時間、模型大小與峰值記憶體，但僅與自家 baseline 比較，缺少與 VG-LLM/GSM 等對手的等量對齊。
- [missing] Reports variance / standard deviation / multiple seeds — 全文皆為單次數值，未提供 seed 重跑或標準差，主結果差距（如 static 上 $+1.2$ Avg.）難以判斷顯著性。
- [partial] Releases code / weights / data sufficient for reproducibility — 論文僅提供 project page（https://suhzhang.github.io/GeoSR/），訓練資料 split 與超參數有寫，但是否釋出程式碼、權重或具體腳本 the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1：「geometry token 在 naive fusion + standard fine-tuning 下被嚴重低估、甚至有害」。** Supported。Fig 1（p.3）以 w/o Geo. vs w/ Geo. 直接呈現 dynamic 上的退化；Table 4 row (e) 62.8 < row (f) 64.0（p.13）量化了「naive injection 反而比沒有 geometry 還差」。診斷層次的證據完整。
- **Claim 2：「GUM 削弱 appearance shortcut，迫使模型查詢 geometry tokens」。** Partially supported。Table 3 (a) vs (d) 51.9 vs 50.9、Table 4 (a) vs (d) 66.1 vs 64.9 顯示加上 GUM 後分數提升，但「shortcut 變弱」這個機制 claim 沒有任何 attention/representation 層級的證據；row (c) 又把 geometry 餵入完全切斷，無法獨立估計 GUM 的純效果。
- **Claim 3：「GGF 用 gate 自適應放大 geometry 貢獻」。** Partially supported。Table 3/4 row (a) vs (b) 顯示替換成 Ori. Fus. 會掉 1.4–1.9 分，所以 gated routing 確實比 additive/concat 強；但論文沒有展示 $\alpha$ 在 token / frame 上的分布、沒有對「geometry 主導區域」做 case study，「fine-grained adaptive routing」這個機制 claim 仍停留在架構描述。
- **Claim 4：「在 static 與 dynamic 兩類 benchmark 上一致超越 prior methods，建立 SOTA」。** Supported on dynamic（DSR-Bench avg +7.2，全 13 subtask 最佳，Table 2, p.12）；marginally supported on static（VSI-Bench avg +1.2，且 Obj. Size、Rel. Dir 兩個 subtask 落後其他 spatial reasoning baselines，Table 1, p.11）。「一致」這個措辭對 static 結果略嫌過強。
- **Claim 5：「設計輕量、不需 heavy computation」。** Supported。Table 6（p.14）顯示 +0.07B 參數、+0.01s 延遲、+0.14GB 記憶體，相對 baseline overhead 微小。

### 7.2 Fundamental Limitations of the Method

GUM 是純粹的 training-time regularization。Inference 完全關閉 masking（Sec 3.4, p.10），意味著被部署的模型仍然能看見全部 vision tokens、仍然存在 appearance shortcut，GeoSR 的「強迫使用 geometry」效果只透過 training distribution shift 改變權重，沒有任何 inference-time 的結構保證。一旦 fine-tune 後 backbone 在新場景上再次找到 appearance 捷徑，論文的核心機制就無法在線阻止這種回退。

GUM 與 GGF 在 dynamic 設定上共用同一條 cross-attention（Eq. 8 的 $A$ 同時驅動 TopK mask 與下游 retrieval $\tilde{F}_G$，Sec 3.2–3.3, p.8–9）。決定「遮哪裡的 vision token」與決定「拿哪些 geometry 來 fuse」的 query 是同一組 bottleneck $B$，這種耦合讓 mask 自然指向 fusion 已經偏好的位置，而非「appearance shortcut 真正藏在哪裡」。如果 model 早期的 fusion attention 本身偏掉，masking 反而會強化錯誤偏好。

方法依賴 geometric tokenizer 是「夠好的」。若 3D foundation model（VGGT / π3）在某個場景失效或 noise 大，GUM 在訓練時遮掉 vision tokens 等於既切斷 appearance、又強迫 model 使用低品質 geometry，整體訊號預算淨減少。Sec 3.4 把 3D 模型整段 frozen，沒有任何 fallback 機制，方法在 OOD 場景上的 robustness 完全綁定外部 geometry encoder 的品質。

GGF 的 gate $\alpha$ 是 token-level / channel-level 的線性閘門，作用在 $\tilde{F}_V$ 與 $\tilde{F}_G$ 兩股已有 feature 上（Eq. 15, p.10），它本身不能創造 geometry 中不存在的訊號、也不能跨 token 重新組合 geometry。也就是說，當 geometry token 在某個區域本來就 missing 或錯誤，GGF 只能在「不用」與「全用」之間切換，無法替模型補出空間結構。這把方法的天花板牢牢釘死在 geometric tokenizer 的能力上。

### 7.3 Citations Worth Tracking

- **VG-LLM [50]**：static 場景的直接 baseline 與架構祖先，GeoSR 大量沿用其資料切分（SPAR-7M / LLaVA-Hound）與 additive fusion 形式，理解 [50] 才知道 GeoSR 改了什麼、保留了什麼。
- **GSM [53]**：dynamic 場景的最強 prior，也是 DSR-Train / DSR-Bench 的提出者；GeoSR 在 DSR-Bench 上 +7.2 的提升幾乎全部相對於它，要評估該提升是否合理需要看 GSM 的 retrieval 機制與 split 設計。
- **VSI-Bench [41]**：static spatial reasoning 的核心評測，理解其 metric（mean relative accuracy for numerical、accuracy for MCQ）與 subtask 偏向，是判斷 GeoSR 在 static 上 +1.2 是否實質提升的前提。
- **VGGT [32] 與 π3 [36]**：兩個 frozen geometric tokenizer 各自負責 static / dynamic，GeoSR 把 tokenizer 當黑箱，但其上限就是這兩個模型的 geometry 表徵品質，特別是 π3 的 permutation-equivariant 設計直接決定 dynamic 推理的 ceiling。
- **MAE [11]**：GUM 的 random masking 形式直接 cite [11]，要判斷 $\gamma=0.8$、$\beta=0.5$ 的選擇與 MAE 在 vision-only setting 上的觀察是否真能 transfer 到 multimodal masking，需回到 [11] 的 ablation。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] gate $\alpha$ 在 GeoSR 訓練後是否真的在「需要 geometry 的位置」（如遮擋、視角變化區域）顯著高於其他位置？論文沒有任何 $\alpha$ 的 visualization 或統計，integrity of Claim 3 仍不可驗證。
- [ ] 把 GUM 也保留在 inference（stochastic mask + ensemble 或 deterministic 掩碼）能否再進一步提升，或反而證明 training-time regularization 已經把「不靠 appearance」內化進權重？
- [ ] DSR-Bench 上的 +7.2 中，有多少來自把 3D backbone 從 GSM 用的 prior 換成 π3？做一組「GSM + π3」與「GeoSR + GSM 原本的 3D model」的對照，才能把 method gain 與 encoder gain 拆開。
- [ ] GUM 改成「mask geometry token 而非 vision token」會發生什麼？如果模型對 geometry 的依賴是真的，這個對稱實驗應該嚴重退化；若退化幅度小，反而暗示模型仍以 appearance 為主。
- [ ] 在 Qwen2.5-VL-72B、LLaVA-Video-7B 等不同 backbone 上，appearance shortcut 的強度是否相同、GUM 的最佳 $\gamma$ / $\beta$ 是否漂移？目前所有結論都綁在 7B 單一 backbone 上。
- [ ] DSR-Train 與 DSR-Bench 的場景／物件是否有重疊？GeoSR 的提升在 cross-domain 影片（例如 VLM4D [54]、4D-Bench [57]）上是否仍成立？
- [ ] TopK mask 與 fusion attention 共用 $A$ 的耦合，若把 mask 切換為一條獨立 attention 分支（重新訓練或從另一組 query 算），分數會更好還是更差？這直接檢驗該耦合是 feature 還是 bug。

### 8.2 Improvement Directions

依可行性排序：

1. **加上 $\alpha$ 與 attention 的可視化／量化分析。** 不需重新訓練，只要在現有 checkpoint 上 dump 每個 token 的 $\alpha$ 與 cross-attention $A$，並對 VSI-Bench / DSR-Bench 的 subtask 分群統計。理由：Claim 2 與 Claim 3 都是機制層級的主張，沒有這層證據之前 7.1 中只能標記為 Partially supported；這也是讓 Phyra-inferred §4.2.2 第六項退場的最低成本路徑。

2. **補一組「baseline + 同一個 3D encoder」對照。** 讓 GSM、VG-LLM 都接 π3 / VGGT，重跑 DSR-Bench / VSI-Bench 一次。理由：dynamic 上 +7.2 的解讀完全取決於 encoder 是否中性。Sec 3.4 已經把所有 3D model frozen，加跑只需要 inference-side 替換，是分離 method gain 與 encoder gain 的最小代價方案。

3. **解耦 mask attention 與 fusion attention。** 為 TopK mask 訓練一條獨立的 query head（不分享 $B$），同 ablation 表跑一次。理由：Eq. 8 的 $A$ 同時用於 mask 與 retrieval 形成正回饋，獨立化後能直接檢驗 §7.2 第二段提到的耦合風險，並可能釋放上限。

4. **inference-time mask ensemble。** 在 inference 隨機 mask N 次取平均輸出，類似 MC-dropout。理由：GUM 目前只是 training regularization，若 inference 階段再次 enforce masking，可量化 §8.1 第二題並可能補上「shortcut 不只在訓練時被壓抑」這層保證；overhead 與 N 線性，可控。

5. **加入 geometry-side mask 對稱實驗。** 訓練一個「mask geometry token」的對照模型。理由：這是 §8.1 第四題的直接執行版本，能夠提供「模型確實依賴 geometry」的對稱證據，比 ablation row (f) 更有說服力。

6. **跨 backbone 規模 sweep。** 至少加跑 Qwen2.5-VL-3B 與 LLaVA-Video-7B 兩個尺寸。理由：當前所有結論建立在單一 7B 模型上，appearance shortcut 與 backbone 規模、訓練語料覆蓋面強相關，若 GUM 在更小或更大模型上效果消失，論文的「naive fusion 是 fundamentally underutilized」這個 framing 就需要修正為「特定規模下 underutilized」。
