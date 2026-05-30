<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# Tuna-2 — Tuna-2: Pixel Embeddings Beat Vision Encoders for Multimodal Understanding and Generation

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | Tuna-2 |
| Paper full title | Tuna-2: Pixel Embeddings Beat Vision Encoders for Multimodal Understanding and Generation |
| arXiv ID | 2604.24763 |
| Release date | 2026-04-27 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2604.24763 |
| PDF link | https://arxiv.org/pdf/2604.24763v1 |
| Code link | — |
| Project page | https://tuna-ai.org/tuna-2 |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|------|------|------|------|
| Zhiheng Liu | Meta AI; The University of Hong Kong | http://johanan528.github.io/ | joint first author |
| Weiming Ren | Meta AI; University of Waterloo | https://cs.uwaterloo.ca/~w2ren/ | joint first author |
| Xiaoke Huang | Meta AI | — | author |
| Shoufa Chen | Meta AI | — | author |
| Tianhong Li | Meta AI | — | author |
| Mengzhao Chen | The University of Hong Kong | — | author |
| Yatai Ji | The University of Hong Kong | — | author |
| Sen He | Meta AI | — | author |
| Jonas Schult | Meta AI | — | author |
| Belinda Zeng | Meta AI | — | author |
| Tao Xiang | Meta AI | — | author |
| Wenhu Chen | University of Waterloo | https://wenhuchen.github.io/ | senior author |
| Ping Luo | The University of Hong Kong | — | senior author |
| Luke Zettlemoyer | Meta AI | — | senior author |
| Yuren Cong | Meta AI | — | senior author |

### 1.2 Keywords

unified multimodal model, pixel-space generation, encoder-free, flow matching, masked feature learning, vision-language model

### 1.3 Related Lineage

| Key | Relation | Brief |
|------|------|------|
| Tuna (Liu et al., 2025) | predecessor | Direct predecessor; Tuna-2 progressively strips its VAE and representation encoder. |
| BAGEL (Deng et al., 2025) | baseline | 14B native UMM baseline compared on understanding and generation benchmarks. |
| Janus-Pro (Chen et al., 2025c) | baseline | Decoupled-representation UMM baseline (CLIP + VQ-VAE) compared in Table 1. |
| Show-o2 (Xie et al., 2025b) | baseline | Unified-vision-encoder UMM that motivates moving toward shared visual representations. |
| NEO / Mono-InternVL (Diao et al., 2025; Luo et al., 2025) | influence | Encoder-free vision-language model designs that inspired removing the representation encoder. |
| JiT (Li and He, 2025) | base model | Pixel-space flow-matching framework with x-prediction + v-loss adopted for Tuna-2's generation. |
| SigLIP 2 (Tschannen et al., 2025) | base model | Representation encoder used inside the Tuna-R variant for controlled comparison. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於原生統一多模態模型（native unified multimodal model, UMM）的視覺表徵設計，探討是否能完全捨棄預訓練視覺編碼器（VAE 與 representation encoder），改以原始 pixel 直接進行端到端訓練，同時支援視覺理解與圖像生成。作者以 Tuna 為基礎，先移除 VAE 形成 Tuna-R（保留 representation encoder），再進一步移除 representation encoder，僅以簡單的 patch embedding 層將影像送入 LLM decoder，並以 pixel-space flow matching（x-prediction、v-loss）執行高解析度圖像生成。為了在高維 pixel 空間中學到穩健表徵，論文提出 masking-based 視覺特徵學習機制，將遮罩同時應用於理解與生成範例。研究議題橫跨多模態理解、文字到圖像生成、圖像編輯，以及對 encoder-based 與 encoder-free UMM 的訓練動態與細粒度感知能力的系統性比較。

### 2.2 Domain Tags

- Computer Vision
- Multimodal Learning
- Generative Models
- Vision-Language Models

### 2.3 Core Architectures Used

- **Tuna-2 (proposed, encoder-free UMM)**：本論文主角，捨棄所有預訓練視覺編碼器，僅用 patch embedding 層把原始 pixel 餵入單一 transformer decoder，同時負責理解與生成。
- **Tuna-R (proposed intermediate variant)**：作為對照組，保留 SigLIP 2 representation encoder 但移除 VAE，用以隔離「移除 representation encoder」這一步的效果。
- **Qwen2.5-7B-Instruct (LLM decoder backbone)**：兩個變體都以此作為共用的語言/多模態 transformer 主幹，承擔 autoregressive 文字生成與 pixel-space 影像建模。
- **JiT-style pixel-space flow matching head**：採用 $x$-prediction 與 $v$-loss 直接在 pixel 空間進行 rectified flow，取代 latent diffusion 作為 Tuna-2 的生成路徑。
- **Patchify / Unpatchify layers**：取代 representation encoder，把影像切成 visual tokens 再還原回 pixel，是 encoder-free 設計的核心介面層。
- **SigLIP 2 So400M (representation encoder, 僅用於 Tuna-R)**：提供語義先驗給 Tuna-R 的視覺輸入，作為與 Tuna-2 對比編碼器影響力的基準。
- **Masking-based visual feature learning module**：以 learnable mask token 對部分 visual tokens 進行遮罩，理解時當作 regularizer、生成時化為 masked denoising 目標，用以在高維 pixel 空間學到更穩健的表徵。
- **Language modelling head**：負責理解任務的下一個 text token 預測，與 flow matching head 平行掛在 transformer 之後形成雙頭輸出。

### 2.4 Core Argument

作者指出，現有統一多模態模型仍普遍仰賴預訓練視覺編碼器（如 SigLIP、CLIP 用於理解，VAE 用於生成），即使近期所謂「unified representation」的方法把兩條路合併，也只是改用單一 vision encoder，並未真正擺脫編碼器帶來的固有限制。這些編碼器各自有預訓練的 inductive bias、固定輸入解析度，並會丟失對細粒度感知任務（如 OCR、計數、視覺細節推理）至關重要的低階像素資訊；同時，為了同時服務理解與生成，模型架構往往得拆成多塊模組，無法完全端到端最佳化，造成兩種任務之間的表徵錯配。基於此根因，作者主張解法必須是「徹底移除預訓練視覺編碼器」，讓單一 transformer 直接從原始 pixel 學習統一表徵：以 patch embedding 取代 representation encoder，並以 JiT 風格的 pixel-space flow matching（x-prediction + v-loss）取代 latent diffusion，使理解與生成共享同一條前向路徑，可一次端到端優化。但在高維 pixel 空間直接學習極易陷入 shortcut，因此他們再引入 masking-based 視覺特徵學習：對生成樣本以 masked denoising 強迫模型由部分觀測重建乾淨圖像，對理解樣本則作為 regularizer 迫使模型在不完整視覺輸入下推理，藉此學到更穩健、更具細節感知能力的 pixel-space 表徵。實驗顯示，雖然 encoder-based 的 Tuna-R 在預訓練早期收斂較快，但在足夠規模的訓練後 encoder-free 的 Tuna-2 在生成上與其相當，理解上特別在 pixel-centric、細粒度感知的 benchmark 上明顯勝出，證實去除預訓練視覺編碼器是邁向更強統一視覺表徵的可行且具擴展性的路徑。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(220 words)

標題「Tuna-2: Pixel Embeddings Beat Vision Encoders for Multimodal Understanding and Generation」直接點出論文的核心立場：在 unified multimodal model 中，直接使用 pixel embeddings 可以勝過依賴 pretrained vision encoders 的設計。標題刻意以「Beat」一詞挑戰主流共識，將 pixel-space modelling 從過去被視為「可行但較弱」的選項，重新定位為新一代 UMM 的可行主軸。

Abstract 的敘事邏輯分為三層。第一層先指出問題：現有 unified multimodal models 常常為 understanding 與 generation 採用不同的 visual representations（典型是 CLIP-like encoder 配 VAE），這種拆解導致兩個任務間的 misalignment，也阻擋了從 raw pixels 端到端最佳化的可能。第二層提出方案：作者引入 Tuna-2，一個 native UMM，直接從 pixel embeddings 進行 understanding 與 generation；架構上以簡單的 patch embedding layer 取代 modular vision encoder，完全移除 VAE 與 representation encoder。第三層則先給出實驗論點，避免讀者把這視為「為了極簡而犧牲品質」的設計：Tuna-2 在多個 multimodal benchmarks 上達到 state-of-the-art，pixel-space modelling 在高品質 image generation 上能與 latent-space approaches 完全競爭；同時，雖然 encoder-based variant 在 early pretraining 收斂較快，但 encoder-free 的 Tuna-2 在大規模訓練後的 multimodal understanding 表現更強，特別是在需要 fine-grained visual perception 的任務上。

最後 Abstract 把這個結果上升為一個一般性主張：pretrained vision encoders 並非 multimodal modelling 的必要條件，end-to-end pixel-space learning 是一條面向 generation 與 perception 的可擴展路徑。這段宣告同時為 §2 的架構簡化設計與 §3 的對照實驗鋪好動機。

### 3.2 Introduction

(640 words)

Introduction 的論證結構從領域脈絡逐步收斂到本文的研究問題與答案。一開始，作者把 visual understanding 與 generation 定位為 multimodal AI 的兩大核心能力，並指出近期工作的趨勢是把兩者整合進 native UMM。引用 Transfusion、BAGEL、Tuna 等代表性工作後，作者點出建構 UMM 的關鍵挑戰：如何將輸入影像編碼成同時對 understanding 與 generation 都有效的 visual representation。

接著，文章鋪陳兩種既有設計光譜。早期 decoupled representations 以 CLIP 處理 understanding、以 VQ-VAE 等重建導向 encoder 處理 generation；近期則出現 unified visual representations，透過共享 vision encoder 對齊兩個任務。作者指出，無論是 decoupled 或 unified，仍然普遍依賴 pretrained vision encoders。這個觀察為下一段轉折鋪路。

轉折來自兩條外部證據：在 multimodal understanding 方面，NEO 等 native VLM 已經移除 representation encoder，採用端到端 encoder-free 架構；在 visual generation 方面，PixelFlow、JiT 等 pixel-space diffusion model 顯示 VAE 也未必是 high-fidelity synthesis 的必要元件。把兩條線索合在一起，作者提出本文的研究問題：能否完全跨越 pretrained vision encoders，從 raw pixels 直接建構 native UMM？

之後的段落直接給出肯定答案，並描述 Tuna-2 的設計演進路徑。第一步是 Tuna-R：移除 VAE、保留 representation encoder，以 pixel-space flow matching 配合 x-prediction 進行視覺生成；這個中間模型作為與 Tuna-2 的 controlled comparison 對照組。第二步是 Tuna-2：再進一步移除 representation encoder，僅以 patch embedding layer 與單一 transformer decoder 處理影像、影片與文字 token，完成 fully encoder-free 的 native UMM。

由於 pixel space 比 latent space 維度高、冗餘多，作者預先處理一個可能的反駁：在高維 pixel space 中學 unified representation 更困難，模型容易學到 superficial shortcuts。為此，他們引入 masking-based visual feature learning，以同一個 masking 操作分別作為 generation 的更難 denoising 目標與 understanding 的 regularization。

最後，Introduction 給出主要發現作為結論論點：在足夠的 visual pretraining 後，encoder-free 的 Tuna-2 在 generation 上與 encoder-based Tuna-R 競爭，在 understanding 上則持續勝出，尤其是 fine-grained perception benchmarks。作者由此推論：移除 pretrained vision encoders 可能反而有助於從 end-to-end pretraining 中學到更強的 fine-grained visual representations。

最後條列三項貢獻：(1) 提出 encoder-free native UMM Tuna-2 並達到 SOTA；(2) 在 controlled 設定下對 Tuna-2 與 Tuna-R 做對照分析，論證 encoder-free 設計的優勢；(3) 提供一系列 pixel-space UMM 的 ablation 與 training dynamics 分析，作為未來 native UMM 設計的參考。這份貢獻清單直接對應 §2 的方法、§3.2-3.6 的主要實驗與分析章節。

### 3.3 Related Work / Preliminaries

(380 words)

Related Work 在論文最後（§4）出現，分為兩個子節，依序對應本文的兩條主要技術路線：unified multimodal models 與 encoder-free architectures。它的角色不是建立 preliminaries，而是為「為何選擇移除 vision encoders」這個論點，提供文獻層次上的對照基礎。

§4.1 先定位 unified multimodal models 的主流設計。作者指出，UMMs 通常結合 AR language model 與 diffusion / flow matching 來分別承擔 text 與 visual generation；這種混合架構雖然在 understanding 上表現良好，但因為視覺端常採用 decoupled encoders，導致 representation mismatch 與訓練效率問題。為此，UniTok、TokLip、UniLip、UniFlow、UAE、OpenVision 3 等工作嘗試訓練 unified vision tokenizer，同時服務語意理解與視覺重建。Native UMM 一脈（Show-o、Tuna、Ming-UniVision、Transfusion-RAE）則進一步把 unified representation 做進主幹模型。作者強調一個關鍵限制：這些 native UMM 仍主要依賴 VAE latents 建構統一表示，這對需要 fine-grained visual perception 的任務形成瓶頸——這正是 Tuna-2 想要打破的限制。

§4.2 處理 encoder-free 路線。作者先回顧 LMM 的傳統 modular 架構：Flamingo 用 cross-attention、LLaVA 用 MLP connector，後續工作沿著這條路把模型、資料與任務範圍逐步放大。隨後出現 monolithic 的 encoder-free 取向：Fuyu、EVE、Chameleon、Mono-InternVL、NEO 等用簡單 MLP 或 patch embedding 將原始 pixel 切成 patch，與 language token 一同丟入單一 transformer。作者強調，本文的貢獻是把 representation encoder-based 與 monolithic 兩種設計同時整合進 pixel-space UMM，並在多 modal understanding 上達到高水準。

最後一段把焦點移到 visual generation。主流方法仍倚賴 KL- 或 VQ-regularized VAE 在 latent space 中操作，但 PixelFlow、DiP、PixelDiT、JiT 等近期工作顯示 pixel-space flow matching 有機會追上甚至超越 latent diffusion。然而這些研究多侷限於 small-scale、class-conditioned ImageNet 設定。作者明確指出 Tuna-2 的差異化貢獻：把 pixel-space flow matching 拓展到 large-scale unified multimodal pretraining，並支援 free-form text-to-image generation 與 image editing。

整體而言，§4 的敘事邏輯是「畫地圖、找縫隙、定位自身」：先描繪 UMM 與 encoder-free 兩個社群的最新進展，再指出兩者尚未交會之處，最後把 Tuna-2 放在這個交會點，作為連結 native UMM 與 pixel-space generation 的代表性嘗試。論文沒有獨立的 Preliminaries 一節；rectified flow 與 x-prediction 等背景是直接寫在 §2.1 的 method 描述中。

### 3.4 Method (overview narrative)

(660 words)

§2 的整體敘事採用「逐步簡化、逐步證成」的策略，把 Tuna-2 的最終形態包裝成從現有 UMM 一路簡化得到的自然終點，而不是憑空出現的新架構。

§2.1 從 Tuna 既有架構出發：vision encoder（含 VAE 與 representation encoder）+ LLM decoder + 兩個 modality-specific head（language modelling head 與 flow matching head）。作者把架構簡化拆成兩步走，每一步都對應一個明確的中間模型。第一步移除 VAE，保留 representation encoder，得到 Tuna-R。這個設計刻意呼應 LLaVA 系列的標準範式，作者把 Tuna-R 定位為 controlled comparison 的對照組，而不是最終答案。第二步進一步把 representation encoder 也移除，改用 simple patch embedding layer，把影像直接切 patch、丟給單一 transformer decoder，這就是 Tuna-2 的核心架構。作者強調這種 monolithic encoder-free 設計的好處在於擺脫 pretrained encoder 內建的 inductive bias（例如固定解析度與對 fine-grained 細節的有限取用），並把整個模型壓成單一統一 transformer。

由於拋棄 VAE 後不能再沿用 latent diffusion 的設計，§2.1 接著鋪陳 pixel-space image generation 的具體做法：採用 JiT 提出的 x-prediction + v-loss 範式做 pixel-space flow matching。透過 rectified flow 的線性 schedule 構造 noisy sample $x_t = t x_1 + (1-t) x_0$，模型 $\pi_\theta$ 直接預測乾淨影像 $x_\theta$，再經由 $v_\theta = (x_\theta - x_t) / (1-t)$ 轉成 velocity，迴歸到 ground-truth velocity $v = x_1 - x_0$ 上。Inference 階段用 Euler solver 在 $v_\theta$ 指引下從噪聲走回乾淨影像。這段安排是要說服讀者：移除 VAE 並不會犧牲 generation 的可訓練性，因為 pixel-space flow matching 已有可靠的訓練目標可用。

§2.2 處理一個 anticipated 反駁：在 high-dimensional pixel space 學 unified representation，比 compact latent space 困難得多，模型容易依賴 superficial shortcut。作者為此引入 masking-based visual feature learning。在訓練時依某個 masking ratio 隨機選一部分 image patch，用 learnable mask token 取代後再丟進 LLM decoder。同一個 masking 操作在兩種任務中扮演不同角色：對 generation 樣本，模型必須同時預測被遮罩與未被遮罩區域的乾淨影像，形成更難的 denoising 問題並讓 mask token 吸收 reconstruction 所需的上下文資訊；對 understanding 樣本，masking 則作為 regularization，迫使模型在部分視覺觀察下完成 multimodal reasoning。作者把這個策略類比到 MAE、SigLIP 2、MaskGIT、DeTok 等先例，定位為一個能同時收斂兩種任務的統一機制，並預告 §3.4 會以 ablation 證明其效用。

§2.3 描述 training pipeline，呼應 encoder-free 設計帶來的訓練簡化。Tuna-2 採用兩階段、全程 end-to-end 的訓練：Stage 1 full model pretraining 透過 image captioning 與 text-to-image generation，建立 flow matching head 的良好初始化並讓 pixel-space 視覺輸入適應 unified modelling；Stage 2 SFT 以更小的 learning rate，混合 image editing、image instruction-following 與 high-quality image generation 資料，進一步強化任務泛化。Tuna-R 因為帶有 connector layer，需要在 Stage 1 之前再加一個短暫的 connector-alignment 階段，這個對比正好凸顯 Tuna-2 的「無 connector」優勢。

整體而言，§2 的故事弧是：先以 Tuna-R 證明「拿掉 VAE 沒問題」，再用 Tuna-2 證明「連 representation encoder 都可以拿掉」；接著用 masking-based learning 補強 pixel-space 的訓練困難，最後用簡化的兩階段 pipeline 收尾。這樣的安排為 §3 的 ablation 與對照分析鋪好了所有實驗變因。

### 3.5 Experiments (overview narrative)

(900 words)

§3 的實驗章節以「先建立 SOTA 級別、再用 ablation 與分析證成設計選擇」為主軸。整體分為六個子節：實驗設定、主要結果、訓練動態 ablation、masking ablation、Tuna-R 與 Tuna-2 的比較分析、attention map 視覺化分析。

§3.1 先把實驗條件交代清楚：LLM decoder 採用 Qwen2.5-7B-Instruct；Stage 1 pretraining 在 64 個節點上跑 300k steps、AdamW、lr=1e-4、序列長度 16k tokens/GPU，資料是 550M in-house image-text pair（70% captioning、30% T2I），加上 20% 的 Nemotron 文字資料；Stage 2 SFT 跑 50k steps、lr=2e-5，混合 FineVision 13M 對話、OmniEdit 2M 編輯、與高品質生成資料。Tuna-R 共用同樣的 LLM decoder，並使用 SigLIP 2 So400M 作為 representation encoder，多了 3k step 的 connector alignment 階段。這個對照確保兩者在資料與訓練流程上的差異被控制到最小。

§3.2 是主要結果，分四個面向。Image understanding 在九個 VQA benchmark 加三個 pixel-centric benchmark 上評估。Tuna-R 與 Tuna-2 全面超越原版 Tuna，並在 7B 級 native UMM 中拿下 SOTA；更關鍵的是 Tuna-2 在多數 understanding benchmark 上勝過 Tuna-R，尤其在 V*、CountBench、VisuLogic 等 fine-grained perception 任務上明顯領先 latent-space UMM，作者把這歸因於 pixel-space representation 對細節的保留以及 monolithic 架構在大規模聯合訓練中的優勢。

Image generation 在 GenEval 與 DPG-Bench 評估。Tuna-R 與 Tuna-2 都達到 SOTA 等級，與 BAGEL、Mogao、Tuna 並駕齊驅。Tuna-R 在生成上略強於 Tuna-2，作者解釋這是 representation encoder 帶入的 semantic prior 帶來的好處；但 Tuna-2 仍能在沒有 VAE、純 pixel-space 設定下保持競爭力。為了補足 GenEval 等 benchmark 偏向 alignment 與 world knowledge 的盲點，作者再做 LLM-judge 評估（GPT-5.4 與 Claude Opus 4.7 作裁判），結果顯示 Tuna-2 在生成品質上與 Tuna-R 相近、優於 Tuna，並在 diversity 上明顯領先，這個結果支撐 encoder-free 設計能同時兼顧品質與多樣性的論點。

Image editing 在 ImgEdit 上做。Tuna-2 大幅勝過 OmniGen、BAGEL、UniWorld、OmniGen2 等 unified baseline，但稍輸於 Tuna 與 Tuna-R，作者把這個差距歸因於 pretrained visual prior 在 fine-grained editing fidelity 上仍提供額外幫助。Image reconstruction 進一步檢驗 pixel-space representation 是否足以支援精細生成：在 ImageNet 驗證集上輕量微調後，Tuna-R 與 Tuna-2 的 rFID 與 PSNR 接近 FLUX.1 [dev] 的 VAE，明顯勝過 RAE 等 non-KL-regularized 對手。

§3.3 的 ablation 探討 generation 與 understanding 資料比例對訓練動態的影響。透過在 8g2u、7g3u 等不同混合比下觀察 MSE 與 CE loss 曲線，作者發現 MSE 對資料比例更敏感、CE 變化幅度小，並把 7:3 訂為兩個目標間的最佳平衡，沿用於所有實驗。

§3.4 直接驗證 §2.2 的 masking-based feature learning：在 Qwen2.5-1.5B backbone 上先 pretrain 50k steps，再分組以 50% 機率啟用 masking 繼續訓練 50k steps。結果顯示 masking 對 Tuna-R 與 Tuna-2 的 understanding 與 generation 指標都有提升，且 Tuna-2 受益更明顯；作者推論這是因為 SigLIP 2 已經有類似 masked prediction 的預訓練。最終策略是把 masking 應用於 pretraining 最後 40%。

§3.5 是 Tuna-R 與 Tuna-2 的縱向對照。隨著訓練資料規模拉長，Tuna-R 在早期 understanding benchmark 上領先，因 representation encoder 帶入語意先驗；但 Tuna-2 後期反超，呼應 encoder-free monolithic 設計更能吃下 large-scale 訓練紅利的論點。在 GenEval 上 Tuna-R 全程略勝，但差距在 SFT 後幾乎消失，與 REPA、Tuna 對 representation prior 的觀察一致。

§3.6 提供 attention map 視覺化作為質性證據。作者以 Tuna、Tuna-R、Tuna-2 與 LLaVA-OneVision-1.5、Qwen2.5-VL、Penguin-VL 等 baseline 對照，挑選包含 misleading linguistic context 與 visual distractor 的範例（shining window、purple object、dog cafe、football match）。Tuna-2 一致地把注意力放在語意對應的視覺區域，避免被文字 prior 或顯著但不相關的 distractor 誤導，從而支撐「encoder-free 設計學到更可靠的 cross-modal alignment」的整體主張。

### 3.6 Conclusion / Limitations / Future Work

(140 words)

§5 結論段落非常精簡，把整篇論文的核心訊息濃縮成三層宣告。第一層重申研究目標：Tuna-2 是一個 family of native unified multimodal models，目的是直接在 pixel space 完成 multimodal understanding 與 visual generation，徹底擺脫 VAE encoder 與 latent diffusion。

第二層概述方法與設計選擇：以 unified vision-language backbone 配合 pixel-space flow matching head，在單一框架中同時支援 image understanding、text-to-image generation 與 image editing；同時提供 encoder-based variant（Tuna-R）與 encoder-free monolithic variant（Tuna-2）兩個實例化版本，作為 controlled comparison 的兩端。

第三層收斂到實驗結論：Tuna-2 在 fine-grained visual understanding benchmark 上勝過 Tuna 與 Show-o2 等 latent-space unified model，同時在 image generation 上與 SOTA unified models 旗鼓相當，據此論證 pixel-space unified multimodal modelling 的有效性與可擴展性，並指出這是未來 native UMM 的一條值得追求的方向。論文未在此節獨立列出 limitations 或 future work，相關討論散落於 §3.2 對 editing 落差的歸因與 §3.5 對 generation 早期劣勢的分析中。

## 4. Critical Profile

### 4.1 Highlights

- 在 7B 規模的 native UMM 中，Tuna-2 於 fine-grained 視覺理解 benchmark 全面領先 encoder-based 同類模型，如 OCRBench 79.7、CountBench 81.7、V* 59.2、VisuLogic 28.8 (Table 1, p. 6)。
- 在純 pixel-space 條件下執行 text-to-image generation，於 GenEval Overall 達 0.87、DPG-Bench Overall 86.54，與 latent-space 的 Mogao (0.89/84.33)、BAGEL (0.88/85.07) 同等競爭 (Table 2, p. 7)。
- 透過 controlled comparison（同一 LLM backbone、同一資料配方）首次清楚呈現「encoder-based 早期收斂快、encoder-free 後期反超」的訓練動態 (Figure 6, p. 10)。
- 提出 masking-based visual feature learning，在 Tuna-R 與 Tuna-2 上一致提升 OCRBench、MMVP、CountBench、GenEval，且 Tuna-2 受益更大 (Table 6, p. 9)。
- 採用 JiT 風格的 $x$-prediction + $v$-loss 訓練 pixel-space flow matching，將 pixel diffusion 從 ImageNet 級別擴展到 free-form text-to-image 與 image editing 的大規模設定 (§2.1, p. 4)。
- 在 image reconstruction 上達到 rFID 0.15 / PSNR 32.80 / SSIM 0.93，超越所有 unified tokenizer，逼近 FLUX.1[dev] 專用 VAE 的 0.06/33.65/0.93 (Table 5, p. 8)。
- 在 LLM-judge 評測中，Tuna-2 於 image diversity 顯著優於 Tuna 與 Tuna-R（GPT-5.4 48.4%、Claude Opus 4.7 41.9%）(Table 3, p. 8)。
- Attention map 可視化顯示 Tuna-2 在語言誤導與視覺干擾並存的「football match / dog cafe」反直覺案例下，仍能正確定位真實物件 (Figure 7, p. 11)。
- 端到端訓練 pipeline 簡化：encoder-free 設計省去 connector alignment 階段，stage 1 + stage 2 即可同時學會 understanding、generation、editing (§2.3, p. 5)。
- 隨資料規模擴大，encoder-based 在 generation 上的優勢逐漸收斂，SFT 後兩者 GenEval 表現幾乎相同，支持 encoder-free 在 scale 上的可行性 (Figure 6, p. 10)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 在 generation benchmark 上 Tuna-R 一致略勝 Tuna-2，作者明確承認 representation encoder 的 semantic prior 對 generation 仍有幫助 (§3.2 image generation 段落, p. 7；§3.5, p. 10)。
- Encoder-based 變體在 pretraining 早期收斂明顯較快，作者在 abstract 與 Figure 6 都直接承認此劣勢，僅以「足夠規模後反超」回應 (abstract, p. 1; §3.5, p. 10)。
- 在 ImgEdit 上 Tuna-2 (4.09) 落後 Tuna-R (4.18) 與 Tuna (4.31)，作者承認「pretrained visual priors may still provide benefits for fine-grained editing fidelity」(§3.2 image editing, p. 8；Table 4, p. 7)。
- 論文承認 high-dimensional pixel space 容易讓模型走 superficial shortcut，因此才需要 masking-based regularization 才能穩定訓練 (§2.2, p. 5)。

#### 4.2.2 Phyra-inferred

- 與 14B 的 BAGEL 比較被以灰底字體淡化，但 Tuna-2 在 MMVet (51.7 vs 67.2)、MMMU (50.7 vs 55.3)、MMVP (77.3 vs 85.0)、AI2D (79.6 vs 89.2)、V* (59.2 vs 70.2)、VisuLogic (28.8 vs 41.7) 全面落後，paper 的「state-of-the-art」結論其實只在 7B 內成立 (Table 1, p. 6)。
- 在 GenEval Overall 上 Tuna-2 (0.87) 反而**低於其前身 Tuna (0.90)**，論文僅以「competitive」帶過，但這直接反證「移除 encoder 提升統一表徵」對 generation 並不成立 (Table 2, p. 7)。
- Table 3 的 LLM-judge 評測只比較 Tuna 家族三個模型彼此，而非與外部 SOTA（如 BAGEL、Mogao）比較，diversity 領先可能反映**收斂不充分導致的高方差**，而不是受控的多樣性增益 (Table 3, p. 8)。
- Masking ablation (Table 6) 改用 Qwen-2.5-1.5B backbone 並只訓練 50k+50k steps，與正式 7B 訓練的 300k steps 存在數量級差距，masking 在 7B 規模的真實貢獻並未直接驗證 (§3.4, p. 10)。
- 「encoder-free」在語言端並不成立：模型仍以 pretrained Qwen2.5-7B-Instruct 為 backbone，視覺端的 inductive bias 被移除但語言端的 prior 保留，因此「end-to-end from raw pixels」的標題其實是 vision-only 半邊敘事 (§3.1, p. 6)。
- 訓練成本完全缺失：64 nodes × 300k steps × 16k token sequence 的實際 GPU-hour、與 encoder-based baseline 的 compute-matched 比較、以及 inference latency 均未報告，使「encoder-free 更可擴展」的主張缺少 cost-axis 證據 (§3.1, p. 6)。
- Pretraining data 為 550M 「in-house image-text pairs」，無法被外部團隊複現，使 controlled comparison 結論的可信度受限於資料配方的不可見性 (§3.1, p. 6)。
- 對「fine-grained perception」的優勢解釋停留在 attention map 的精選定性案例 (Figure 7, p. 11)，缺少量化的 attention IoU 或 probing 實驗來支持「pixel-level information 真的被保留」的因果敘事。
- 與真正 pure pixel-space generation 模型（如 JiT, PixelFlow, DiP）的直接 head-to-head 缺席，使讀者無法分辨增益來自「unified pretraining」還是單純「pixel-space flow matching 本身已經夠好」(§4.2 文獻段, p. 12)。

### 4.3 Phyra's Judgment (summary)

Tuna-2 的核心新意是把「encoder-free 多模態理解」與「pixel-space flow matching 生成」第一次在大規模 unified pretraining 中拼起來，並用 controlled Tuna-R baseline 量化兩條路線的訓練動態，這是 genuinely new 的 design study。但模型本身的多數元件（JiT 的 $x$-prediction、SigLIP 2 風格的 masking、Qwen2.5 backbone、Mono-InternVL/NEO 的 patch embedding 路線）都是現成積木的工程整合，論文真正貢獻屬「系統性整合 + 比較分析」而非新方法。仍未解決的核心問題是：在 generation 與 editing 上 encoder-free 仍輸給 encoder-based，且論文未能用 compute-matched 證據說明此差距會隨 scale 收斂；「移除 vision encoder」的論點目前更像是針對 understanding 任務成立的局部結論，而非統一表徵的全面解答。

## 5. Methodology Deep Dive

### 5.1 Method Overview

Tuna-2 是一個原生統一多模態模型 (native unified multimodal model)，其方法論可拆解為三個漸進式的架構簡化步驟與一個關鍵的訓練穩定化機制。作者以 Tuna (Liu et al., 2025) 為基準起點，原始 Tuna 由 VAE encoder、representation encoder (SigLIP 2)、LLM decoder 與兩個任務特化的 head (language modelling head 與 flow matching head) 組成。第一步是移除 VAE 並讓影像生成從 latent space 改在 pixel space 進行，但仍保留 representation encoder，得到中間設計 Tuna-R (§2.1)。第二步是進一步移除 representation encoder，僅以一個 simple patch embedding layer 將原始像素切塊並送入 LLM decoder，由單一 transformer 同時處理 image 與 text token，此即 Tuna-2 的最終形態。

在 pixel-space 影像生成上，Tuna-2 採用 JiT (Li and He, 2025) 的 x-prediction + v-loss 範式 (§2.1)。給定 source image $x_1$、sampled noise $x_0 \sim \mathcal{N}(0, I)$、timestamp $t \in [0,1]$，以 rectified flow 的 linear schedule 在像素空間構造 noisy sample $x_t = t x_1 + (1-t) x_0$。模型 $\pi_\theta$ 直接預測乾淨影像 $x_\theta = \pi_\theta(x_t, c, t)$，再經由解析變換 $v_\theta = (x_\theta - x_t)/(1-t)$ 轉成 velocity 並回歸 ground truth velocity $v = x_1 - x_0$；推論時以 Euler solver 由噪訊較高的 $x_t$ 迭代得到 $x_{t'} = x_t + (t' - t)v_\theta$。整個生成路徑與文字生成共享同一個 transformer backbone，因此 understanding 與 generation 可以一次端到端最佳化。

由於 pixel space 的維度遠高於 VAE latent space，模型容易學到 superficial shortcut，作者引入 masking-based 視覺特徵學習機制 (§2.2)。訓練時依 masking ratio 隨機選取部分 image patch，將其替換為 learnable mask token，再送入 LLM decoder。對生成樣本，模型必須在 masked 與 unmasked 區域同時預測 clean patch，同時形成更困難的去噪任務並讓 mask token 吸收脈絡資訊；對理解樣本，masking 則作為 regularizer，迫使模型在不完整視覺輸入下完成跨模態推理。此機制不從 pretraining 起點啟用：先以 50k steps 標準預訓練建立基礎多模態知識，再以 50% 機率啟用 masking 繼續 50k steps 進行 ablation；正式訓練則於 pretraining 的最後 40% 啟用 (§3.4)。Ablation 顯示 Tuna-2 受益幅度大於 Tuna-R，作者推測 SigLIP 2 已使用類似 masked prediction 預訓練是主要原因。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input
   ├→ Image (含 Image Prompt / source image): [B, 3, H, W]
   │     (training res H = W = 512, Table 5)
   │     │
   │     │  (Generation 樣本: 由 x_1 與 x_0 ~ N(0, I) 構造 x_t = t·x_1 + (1-t)·x_0)
   │     │
   │     ▼
   │   Patchify Layer (Tuna-2)            [取代 Tuna-R 的 Representation Encoder]
   │     │  patch size p (paper does not specify)
   │     ▼
   │   Visual tokens: [B, N_p, d_llm]
   │     where N_p = (H/p)·(W/p),  d_llm = 3584 (Qwen2.5-7B-Instruct)
   │     │
   │     │  (Optional) Masking-based Feature Learning
   │     │  隨機選取 mask ratio 比例的 patch → 替換為 learnable mask token
   │     │  (50% 機率啟用，於 pretraining 最後 40% 階段，§3.4)
   │     ▼
   │   Visual tokens (possibly masked): [B, N_p, d_llm]
   │
   └→ Text prompt: "..."
         │
         ▼
        Text Tokenizer (Qwen2.5-7B-Instruct)
         │
         ▼
        Text token embeddings: [B, T_text, d_llm]

Concatenated multimodal sequence: [B, N_p + T_text, d_llm]
                                   │
                                   ▼
                  ┌─────────────────────────────────────┐
                  │   LLM Decoder (Qwen2.5-7B-Instruct) │
                  │   Single unified transformer        │
                  │   (joint vision + language)         │
                  └─────────────────────────────────────┘
                                   │
                                   ▼
                  Hidden states: [B, N_p + T_text, d_llm]
                                   │
                       ┌───────────┴────────────┐
                       ▼                        ▼
            Language Modelling Head      Flow Matching Head (pixel-space)
            (text token positions)       (visual token positions)
                       │                        │
                       ▼                        ▼
            Vocab logits: [B, T_text, |V|]   Predicted clean image x_θ: [B, 3, H, W]
                       │                        │
                       │                        │  Eq. (3): v_θ = (x_θ - x_t) / (1 - t)
                       │                        ▼
                       │                   Velocity v_θ: [B, 3, H, W]
                       │                        │
                       │     ┌──────────────────┴──────────────────┐
                       │     │ Training: L_flow = E ‖v_θ − v‖²₂    │
                       │     │ Inference: x_{t'} = x_t + (t'-t)v_θ │
                       │     └─────────────────────────────────────┘
                       │                        │
                       ▼                        ▼
            Next-token text response   Unpatchify Layer
            (autoregressive)                    │
                                                ▼
                                       Image response: [B, 3, H, W]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Patchify Layer

**Function:** 將原始像素切塊並線性投影至 LLM hidden dim，取代 representation encoder 完成端到端 vision tokenization (§2.1)。

**Input:**
- Name: image $x$ (clean source image $x_1$ for understanding；noisy $x_t$ for generation training)
- Shape: [B, 3, H, W]
- Source: image captioning 樣本、text-to-image 生成樣本 ($x_t$ 由 Eq. 1 構造)、image editing 樣本 (Stage 2)

**Output:**
- Name: visual tokens
- Shape: [B, $N_p$, $d_{\text{llm}}$]
- Consumer: Masked Feature Learning (optional) → LLM Decoder

**Processing:**

H×W 影像被切成 $p \times p$ 不重疊 patch，flatten 後線性投影到 $d_{\text{llm}}$；$N_p = (H/p) \cdot (W/p)$。論文 §2.1 僅描述為 "simple patch embedding layers"。

**Key Formulas:**

無顯式公式 (純 linear projection，等同 ViT 風格 patch embedding 但無預訓練視覺 inductive bias)。

**Implementation Details:**

- 訓練解析度 $H = W = 512$ (Table 5 image reconstruction 設定)
- Patch size $p$、投影矩陣維度: the paper does not specify
- 不使用任何 pretrained vision encoder，這是與 Tuna-R 的關鍵區別 (Tuna-R 在此位置改用 SigLIP 2 So400M + connector layer)

#### 5.3.2 Text Tokenizer

**Function:** 將文字 prompt / response 編碼為 token id 並 embed 到 LLM 共享 hidden space。

**Input:**
- Name: text prompt $c_{\text{text}}$
- Shape: [B, $T_{\text{text}}$] (token id)
- Source: 用戶 prompt、image caption ground truth、editing instruction、text-only Nemotron 資料 (Stage 1)、conversation (Stage 2 FineVision)

**Output:**
- Name: text token embeddings
- Shape: [B, $T_{\text{text}}$, $d_{\text{llm}}$]
- Consumer: 與 visual tokens 串接後送入 LLM Decoder

**Processing:**

直接複用 Qwen2.5-7B-Instruct 自帶的 tokenizer 與 embedding table，未對 visual / text token 做特殊 prefix 處理 (§3.1)。

**Key Formulas:**

無。

**Implementation Details:**

- Tokenizer: Qwen2.5-7B-Instruct
- 序列長度於每張 GPU 上 pad 至 16k tokens (§3.1)

#### 5.3.3 LLM Decoder (Unified Transformer)

**Function:** 單一 transformer 同時處理 visual + text token，完成 multimodal understanding 與 generation 的共享 forward path (§2.1)。

**Input:**
- Name: 串接後序列 $z$
- Shape: [B, $N_p + T_{\text{text}}$, $d_{\text{llm}}$]
- Source: Patchify Layer 產生的 visual tokens (含 optional mask token 替換) + Text Tokenizer 的 text embeddings

**Output:**
- Name: hidden states
- Shape: [B, $N_p + T_{\text{text}}$, $d_{\text{llm}}$]
- Consumer: text 位置 → Language Modelling Head；vision 位置 → Flow Matching Head

**Processing:**

所有 token 走相同 transformer block，pixel patch token 與 text token 在同一 self-attention 中互動。Stage 1 同時進行 image captioning 與 text-to-image generation 的 joint pretraining，Stage 2 SFT 加入 image editing 與 image instruction-following。是否使用模態特化 attention mask 論文未細述。

**Key Formulas:**

無 (沿用 Qwen2.5 標準 architecture)。

**Implementation Details:**

- Backbone: Qwen2.5-7B-Instruct，$d_{\text{llm}} = 3584$ (公開模型常數，非論文揭露)
- Stage 1 pretraining: 300k steps、64 nodes、AdamW、lr $= 1 \times 10^{-4}$、序列 16k tokens/GPU (§3.1)
- Stage 1 資料: 550M in-house image-text pairs + 20% text-only Nemotron (Bercovich et al., 2025) (§3.1)；§3.1 描述 image-text 內部分配為 70% image captioning / 30% text-to-image generation；§3.3 ablation 結論為 7g3u (7:3 generation:understanding) 並聲稱「adopt this data sampling ratio in all experiments」(§3.3 結尾)，與 §3.1 描述存在表面不一致，需以原文為準
- Stage 2 SFT: 50k steps、AdamW、lr $= 2 \times 10^{-5}$ (§3.1)
- Stage 2 資料: 13M FineVision conversational + ~2M OmniEdit editing 範例 (§3.1)
- Tuna-R 額外 connector alignment stage: 3k steps、AdamW、lr $= 5 \times 10^{-4}$ (§3.1)；Tuna-2 因 encoder-free 不需要此階段 (§2.3)

#### 5.3.4 Language Modelling Head

**Function:** 在 text token 位置上執行 next-token prediction，輸出文字 response (§2.1, §2.3)。

**Input:**
- Name: text 位置 hidden states
- Shape: [B, $T_{\text{text}}$, $d_{\text{llm}}$]
- Source: LLM Decoder

**Output:**
- Name: vocabulary logits
- Shape: [B, $T_{\text{text}}$, $|V|$]
- Consumer: training 階段計算 cross-entropy loss；inference 階段做 autoregressive sampling

**Processing:**

標準 autoregressive language modelling head，沿用 Qwen2.5-7B-Instruct 的 LM head。Stage 1 對 image captioning 樣本生效，Stage 2 對 instruction-following / editing 對話的文字回應生效。

**Key Formulas:**

論文未顯式列出，惟為標準 next-token cross-entropy。

**Implementation Details:**

論文未公布額外修改，沿用基底 LLM 設計。

#### 5.3.5 Flow Matching Head + Unpatchify Layer (Pixel-space Generation)

**Function:** 在 vision token 位置上執行 pixel-space rectified-flow 影像生成，採用 JiT 的 x-prediction + v-loss (§2.1)。

**Input:**
- Name: noisy image $x_t$、conditioning $c$、timestamp $t$
- Shape: $x_t$: [B, 3, H, W]；$c$: text prompt (text-to-image) 或 text + reference image (image editing) 經各自 Patchify / Tokenizer 後的 token；$t$: [B]
- Source: training 端由 ground truth $x_1$、$x_0 \sim \mathcal{N}(0, I)$、$t \sim [0, 1]$ 構造；inference 端由 Euler solver 迭代

**Output:**
- Name: predicted clean image $x_\theta$，再轉成 velocity $v_\theta$，最後經 Unpatchify Layer 還原
- Shape: [B, 3, H, W]
- Consumer: training 階段送入 v-loss；inference 階段送入 Euler step 進行下一輪去噪

**Processing:**

1. 構造 noisy sample (Eq. 1)。
2. 模型直接預測乾淨影像 (Eq. 2)。
3. 解析地將 $x_\theta$ 轉成 velocity (Eq. 3)，這是與 latent diffusion 不同之處：模型輸出 $x_\theta$ 而非 $\epsilon$ 或 $v$。
4. 損失採 MSE on velocity (Eq. 4)。
5. 推論時用 Euler 步進: $x_{t'} = x_t + (t' - t) v_\theta$，逐步從 $t < t'$ 推到 $t' = 1$ 得到 clean output。
6. Unpatchify Layer 將 patch 序列 reshape 回 [B, 3, H, W] 影像。

**Key Formulas:**

$$
x_t = t x_1 + (1 - t) x_0, \quad t \in [0, 1] \tag{1}
$$

$$
x_\theta = \pi_\theta(x_t, c, t) \tag{2}
$$

$$
v_\theta = \frac{x_\theta - x_t}{1 - t} \tag{3}
$$

$$
\mathcal{L}_{\text{flow}} = \mathbb{E}_{t, c, x_1, x_0} \, \| v_\theta - v \|_2^2, \quad v = x_1 - x_0 \tag{4}
$$

**Implementation Details:**

- Sampler: Euler solver (§2.1 末段)
- 採用 JiT (Li and He, 2025) 的 x-prediction + v-loss 範式，與 latent diffusion 路線顯著不同
- 推論解析度 / 取樣步數: the paper does not specify

#### 5.3.6 Masking-based Visual Feature Learning

**Function:** 在 pixel space 訓練時對 visual token 套用 learnable mask token，迫使模型由部分觀測重建 / 推理，避免在高維 pixel 空間學到 shortcut (§2.2)。

**Input:**
- Name: visual token sequence + masking ratio
- Shape: [B, $N_p$, $d_{\text{llm}}$]；masking ratio 為純量
- Source: Patchify Layer 之後 (生成樣本作用於 noisy patch；理解樣本作用於 clean patch)

**Output:**
- Name: masked visual sequence (被選中的 patch 替換為共享的 learnable mask token)
- Shape: [B, $N_p$, $d_{\text{llm}}$]
- Consumer: LLM Decoder

**Processing:**

- Generation 樣本: 模型在被 mask 與未被 mask 的位置都需預測 clean patch，形成 harder denoising 任務並讓 mask token 吸收 visible context。
- Understanding 樣本: 模型在被 mask 視覺輸入下預測 ground-truth text response，等同 regularizer。
- 兩種樣本套用相同的 masking 操作 (§2.2 第二段)。
- 不從 pretraining 起點啟用: ablation 設定為先以 50k steps 標準預訓練建立基礎多模態知識，再以 50% 機率啟用 masking 繼續 50k steps (§3.4)。
- 正式訓練於 pretraining 最後 40% 階段啟用 (§3.4 結尾)。

**Key Formulas:**

無顯式公式 (mask token 為 learnable parameter，融入既有的 $\mathcal{L}_{\text{flow}}$ 與 LM cross-entropy，不改變損失形式)。

**Implementation Details:**

- 啟用機率: 50% (§3.4 ablation 設定)；正式 pretraining 啟用時段: 最後 40% (§3.4)
- Ablation 在 Qwen-2.5-Instruct-1.5B backbone 上完成 (§3.4)
- Tuna-2 受益幅度大於 Tuna-R，作者假設 SigLIP 2 已用 masked prediction 預訓練是主因 (§3.4)
- Masking ratio、mask token 維度: the paper does not specify
- 與既有方法的關聯: MAE (He et al., 2022)、SigLIP 2 (Tschannen et al., 2025) 用於 semantic learning；MaskGIT (Chang et al., 2022)、DeTok (Yang et al., 2025a) 用於 visual generation

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| In-house image-text pairs | Image captioning + text-to-image generation | 550M pairs (70% caption / 30% T2I) | Train (Stage 1 pretraining) |
| Nemotron (Bercovich et al., 2025) | Text-only language modelling | 20% of total pretraining data | Train (Stage 1 pretraining) |
| FineVision (Wiedmann et al., 2025) | Image instruction-following | 13M conversational examples | Train (Stage 2 SFT) |
| OmniEdit (Wei et al., 2024) | Image editing | ~2M examples | Train (Stage 2 SFT) |
| GQA (Hudson and Manning, 2019) | VQA (general) | the paper does not specify | Test |
| RealWorldQA (xAI) | VQA (real-world) | the paper does not specify | Test |
| MMVet (Yu et al., 2023) | VQA (multi-capability) | the paper does not specify | Test |
| MMMU (Yue et al., 2024) | Multi-discipline VQA | the paper does not specify | Test |
| MMVP (Tong et al., 2024) | Visual perception VQA | the paper does not specify | Test |
| SEED-Bench2+ (Li et al., 2024b) | Text-rich VQA | the paper does not specify | Test |
| AI2D (Kembhavi et al., 2016) | Diagram QA | the paper does not specify | Test |
| ChartQA (Masry et al., 2022) | Chart QA | the paper does not specify | Test |
| OCRBench (Liu et al., 2024) | OCR | the paper does not specify | Test |
| V* (Wu and Xie, 2024) | Fine-grained visual search | the paper does not specify | Test |
| CountBench (Paiss et al., 2023) | Object counting | the paper does not specify | Test |
| VisuLogic (Xu et al., 2025) | Visual logical reasoning | the paper does not specify | Test |
| GenEval (Ghosh et al., 2023) | Text-to-image alignment | the paper does not specify | Test |
| DPG-Bench (Hu et al., 2024) | Dense prompt T2I | the paper does not specify | Test |
| ImgEdit (Ye et al., 2025) | Instruction-guided image editing | the paper does not specify | Test |
| ImageNet validation (Deng et al., 2009) | Image reconstruction | the paper does not specify | Val (light finetune + eval) |
| In-house prompt set for LLM-judge | T2I quality / diversity | 1.5K prompts × 4 images | Test (GPT-5.4 / Claude Opus 4.7 judges) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| GenEval Overall | Object-focused text-image alignment composite (1-Obj./2-Obj./Count/Colors/Position/Col. Attr.) | yes |
| DPG-Bench Overall | Dense prompt-following score (Global/Entity/Attribute/Relation/Other) | yes |
| Per-benchmark VQA accuracy | Accuracy on GQA / RealWorldQA / MMVet / MMMU / MMVP / SEED-Bench2+ / AI2D / ChartQA / OCRBench / V* / CountBench / VisuLogic | yes |
| ImgEdit per-task + Total | Editing scores across Add/Adjust/Extract/Replace/Remove/Background/Style/Hybrid/Action and total | yes |
| LLM-judge Quality / Diversity (GPT-5.4, Claude Opus 4.7) | % of prompts where the model is preferred among Tuna / Tuna-R / Tuna-2 on realism+detail and intra-prompt variation | no |
| rFID | Reconstruction FID on ImageNet val | no |
| PSNR | Peak signal-to-noise ratio for reconstruction | no |
| SSIM | Structural similarity for reconstruction | no |
| Training MSE (flow matching) | Pretraining loss for generation branch, used in data-ratio ablation | no |
| Training CE (language modelling) | Pretraining loss for understanding branch, used in data-ratio ablation | no |

### 6.3 Training and Inference Settings

LLM backbone is `Qwen2.5-7B-Instruct` (Qwen et al., 2024); the masking ablation uses a smaller `Qwen-2.5-Instruct-1.5B` backbone. Stage 1 trains the full model end-to-end for 300k steps on 64 nodes with AdamW (Loshchilov and Hutter, 2017) at learning rate $1\times10^{-4}$. Stage 2 SFT runs 50k steps with AdamW at learning rate $2\times10^{-5}$. All training stages pad input sequences to 16k tokens per GPU. The paper does not specify per-GPU batch size, GPUs per node, total wall-clock, or LR schedule shape.

For Tuna-R, the representation encoder is `SigLIP 2 So400M` (Tschannen et al., 2025), and an extra connector-alignment stage trains only the connector for 3k steps with AdamW at learning rate $5\times10^{-4}$ before Stage 1.

The data-mixture ablation sweeps generation:understanding sampling ratios (denoted $x\text{g}y\text{u}$) and adopts $7\text{g}3\text{u}$ as the default (§3.3). The masking-based feature-learning scheme is enabled with probability 50% on both modalities and applied during the final 40% of pretraining; in the controlled study, models are first pretrained 50k steps without masking, then the masking arm trains for another 50k steps (§3.4).

Inference for generation uses the rectified-flow Euler solver, predicting $x_\theta$ and converting to velocity via $v_\theta = (x_\theta - x_t)/(1-t)$ (Eq. 3); $x_{t'} = x_t + (t'-t)\,v_\theta$ (§2.1). The paper does not specify the number of sampling steps, classifier-free guidance scale, image resolution at inference, or decoding settings for understanding.

### 6.4 Main Results

Image understanding (selected columns from Table 1; 7B native UMMs unless noted):

| Method | MMMU | MMVP | OCRBench | V* | CountBench | VisuLogic | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-VL (7B) | 58.6 | 78.0 | 83.7 | 71.2 | 74.1 | 20.0 | Understanding-only LMM |
| BAGEL (14B) | 55.3 | 85.0 | 73.3 | 70.2 | 82.5 | 41.7 | Larger native UMM |
| Show-o2 (7B) | 48.9 | 76.7 | 32.4 | 44.5 | 63.5 | 26.9 | Latent-space UMM |
| Janus-Pro (7B) | 41.0 | 73.3 | 59.0 | 47.6 | 53.2 | 23.8 | Native UMM |
| Tuna (7B) | 49.8 | 70.7 | 74.3 | 52.4 | 73.5 | 22.4 | Prior latent-space UMM |
| Tuna-R (7B) | 51.1 | 74.7 | 78.3 | 57.6 | 77.8 | 26.2 | Encoder-based pixel-space variant |
| **Tuna-2 (7B)** | **50.7** | **77.3** | **79.7** | **59.2** | **81.7** | **28.8** | **This paper** |

Image generation on GenEval / DPG-Bench (Table 2; native UMMs):

| Method | GenEval Overall | DPG-Bench Overall | Notes |
| --- | --- | --- | --- |
| BAGEL† (14B) | 0.88 | 85.07 | Larger native UMM, LLM rewriter |
| Mogao (7B) | 0.89 | 84.33 | Native UMM |
| Tuna (7B) | 0.90 | 86.76 | Prior best in family |
| Tuna-R (7B) | 0.88 | 86.35 | Encoder-based variant |
| **Tuna-2 (7B)** | **0.87** | **86.54** | **This paper, encoder-free** |

LLM-judge T2I (Table 3, % preferred among Tuna / Tuna-R / Tuna-2):

| Method | GPT-5.4 Quality | GPT-5.4 Diversity | Claude 4.7 Quality | Claude 4.7 Diversity |
| --- | --- | --- | --- | --- |
| Tuna | 22.3 | 20.6 | 28.1 | 28.2 |
| Tuna-R | 35.7 | 30.9 | 37.2 | 29.9 |
| **Tuna-2** | **32.1** | **48.4** | **34.8** | **41.9** |

Image editing on ImgEdit (Table 4, total score):

| Method | Total | Notes |
| --- | --- | --- |
| FLUX.1 | 4.00 | Generation-only |
| Qwen-Image | 4.27 | Generation-only |
| GPT-Image | 4.20 | Closed unified model |
| BAGEL | 3.20 | Unified |
| OmniGen2 | 3.44 | Unified |
| Tuna | 4.31 | Prior best in family |
| Tuna-R | 4.18 | Encoder-based variant |
| **Tuna-2** | **4.09** | **This paper** |

Image reconstruction on ImageNet val (Table 5, unified tokenizers):

| Method | Res. | rFID $\downarrow$ | PSNR $\uparrow$ | SSIM $\uparrow$ |
| --- | --- | --- | --- | --- |
| TokenFlow | 384 | 0.63 | 22.77 | 0.73 |
| RAE | 256 | 0.61 | 19.20 | 0.44 |
| PS-VAE | 256 | 0.20 | 28.79 | 0.82 |
| Tuna-R | 512 | 0.12 | 32.22 | 0.93 |
| **Tuna-2** | **512** | **0.15** | **32.80** | **0.93** |

### 6.5 Ablation Studies

- **Generation : understanding data ratio (Figure 5, §3.3).** Sweeps multiple $x\text{g}y\text{u}$ mixtures and tracks MSE (flow matching) and CE (LM) curves on both Tuna-R and Tuna-2. Diagnostic: shows MSE is more sensitive to the mixture than CE and motivates the chosen $7\text{g}3\text{u}$ default. Limitation: end-task accuracy at each ratio is not reported, only training losses, so the "best trade-off" claim is anchored to loss curves rather than benchmark scores.
- **Masking-based feature learning (Table 6, §3.4).** Compares with/without masking on a 1.5B backbone for Tuna, Tuna-R, Tuna-2. Diagnostic on the proposed module: masking improves OCRBench, MMVP, CountBench, GenEval for both Tuna-R (e.g. OCRBench 58.3$\to$59.2; MMVP 56.7$\to$58.0) and Tuna-2 (OCRBench 55.4$\to$56.8; MMVP 52.3$\to$55.7; CountBench 53.4$\to$57.6), with a larger gain for Tuna-2. The design choice (50% probability, applied in the last 40% of pretraining, after a 50k-step warm start) is fixed; the paper does not ablate masking ratio, schedule, or whether masking helps generation alone vs. understanding alone.
- **Encoder-based vs. encoder-free (Figure 6, §3.5).** Plots OCRBench, MMVP, V*, GenEval vs. tokens consumed for Tuna-R vs. Tuna-2. Diagnostic of the central claim: Tuna-R leads early on understanding, Tuna-2 catches up and surpasses it at scale; on GenEval Tuna-R stays ahead but the gap shrinks and converges after SFT. This directly supports the paper's "encoder-free wins with scale on understanding, parity on generation" thesis.
- **Attention-map qualitative analysis (Figure 7, §3.6).** Compares attention maps of Tuna, Tuna-R, Tuna-2, LLaVA-OV-1.5, Qwen2.5-VL, and Penguin-VL on basic perception, misleading-prior, and counterintuitive prompts. This is illustrative rather than quantitative and reads as a sanity check / showcase rather than a controlled diagnostic, since no metric, sample size, or evaluator agreement is reported.
- **Image reconstruction probe (Table 5, §3.2).** Lightweight finetuning of the unified model on reconstruction shows Tuna-2 attains rFID 0.15 / PSNR 32.80 at 512px, near `FLUX.1[dev]-VAE` (rFID 0.06). Diagnostic for whether pixel-space tokens preserve enough information to reconstruct, supporting the encoder-free claim — but this is post-hoc finetuning, not zero-shot reconstruction.

The data-mixture sweep partly reads as a sanity check because it reports only training losses; the masking and encoder-vs.-no-encoder ablations are genuinely diagnostic of the paper's two main contributions.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — Tables 1, 2, 4 compare against contemporaneous SoTA UMMs (BAGEL, Show-o2, Janus-Pro, Mogao, Tuna) and strong understanding/generation specialists (Qwen2.5-VL, FLUX.1, Qwen-Image, GPT-Image).
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — Evaluated on 12 understanding benchmarks (GQA, RealWorldQA, MMVet, MMMU, MMVP, SEED-Bench2+, AI2D, ChartQA, OCRBench, V*, CountBench, VisuLogic), GenEval, DPG-Bench, ImgEdit, and ImageNet reconstruction.
- [covered] Has ablations that diagnose the new components (not just sanity checks) — The masking-feature ablation (Table 6) and the Tuna-R vs. Tuna-2 scaling curves (Figure 6) directly probe the two proposed contributions.
- [covered] Has a scaling study (size, length, or compute) — Figure 6 plots accuracy vs. tokens consumed for both architectural variants, showing crossover behaviour as data scales.
- [missing] Has an efficiency / wall-clock comparison — No throughput, FLOPs, latency, memory, or training-time numbers are reported for Tuna-2 vs. Tuna-R or other UMMs; the paper does not specify wall-clock cost.
- [missing] Reports variance / standard deviation / multiple seeds where relevant — All tables report single-run point estimates; no error bars, seed averages, or confidence intervals are given, including for the GPT-5.4 / Claude-judge comparisons over 1.5K prompts.
- [partial] Releases code / weights / data sufficient for reproducibility — A project page is listed (https://tuna-ai.org/tuna-2), but the 550M pretraining corpus is in-house, the training code/weight release is not described in the experiment section, and key hyperparameters (batch size, GPUs per node, sampling steps, CFG scale) are not specified.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: Tuna-2 在多模態 understanding 與 generation benchmark 全面達 state-of-the-art。**
  *Partially supported.* 在 7B native UMM 群體內，Tuna-2 在 understanding 多項 pixel-centric benchmark 領先 (Table 1)；但在 GenEval 上 0.87 低於自家 Tuna 0.90 與 Mogao 0.89，與 14B 的 BAGEL 在 understanding 上仍有大幅差距 (Tables 1–2)。SOTA 主張只在「7B-scale native UMM、且僅看 understanding」時才完全成立。

- **Claim 2: 在足夠 pretraining 後，encoder-free 在 generation 上與 encoder-based 競爭、在 understanding 上具優勢。**
  *Supported with caveat.* Figure 6 的 trajectory 確實顯示理解端反超、生成端逐步收斂；但 SFT 後 ImgEdit 仍是 Tuna-R > Tuna-2 (4.18 vs 4.09, Table 4)，「生成端競爭」的結論在 editing 子任務並未真正成立。

- **Claim 3: Pretrained vision encoder 對 multimodal modelling 並非必要。**
  *Overclaimed.* 證據只能支持「在 understanding 上不必要」；在 generation 上作者自己承認 representation encoder 提供有用的 semantic prior (§3.5)，而 Table 4 顯示 editing 仍受益於 encoder。論文的 abstract 標題遠強於實驗實際支持的範圍。

- **Claim 4: Masking-based visual feature learning 提升 pixel-space 表徵的穩健性。**
  *Supported.* Table 6 在 OCRBench、MMVP、CountBench、GenEval 四個指標上一致提升，且 Tuna-2 受益大於 Tuna-R 的對比也合乎「SigLIP 2 已內建 masked prediction 故邊際效用較低」的解釋。但實驗在 1.5B backbone、100k steps 上完成，與 7B 主訓練 scale 不一致。

- **Claim 5: Pixel-space generation 可擴展至 large-scale unified pretraining。**
  *Supported.* Image reconstruction (Table 5, rFID 0.15) 與 free-form text-to-image / editing 結果共同支持 pixel-space flow matching 不再受限於 ImageNet 級別實驗，這是相對於 JiT、PixelFlow 的 scale 上實質推進。

### 7.2 Fundamental Limitations of the Method

**Pixel-space 訓練對 compute 的依賴是內生的，而非可調參數。** 論文核心發現是「encoder-based 早期領先、encoder-free 後期反超」(Figure 6)，這意味著 Tuna-2 的勝出建立在「足夠長的 pretraining」之上。當未來研究者算力有限或要快速迭代時，encoder-free 路線並不提供 favorable trade-off；同時論文沒有給出 cost-matched 的比較曲線，無法回答「假設只有一半 compute，Tuna-R 是否仍是更佳選擇」這個對實務最關鍵的問題。

**Encoder-free 的「unification」其實只解決了一半的 representation mismatch。** 論文的論點是預訓練 vision encoder 製造 understanding/generation 表徵錯配，但 Tuna-2 解法仍依賴 Qwen2.5-7B-Instruct 的 pretrained language prior。當 LLM backbone 自身對視覺 token 已有強烈分布偏好時，pixel embedding 經由 patch embedding 進入 LLM 後仍會被「強行對齊到 LLM 的 token 流形」上，因此 mismatch 並未從根源消除，只是從 vision-encoder 端轉移到了 LLM-tokenizer 端。

**Generation 端的 semantic prior 缺口是結構性的。** 作者承認 Tuna-R 在 GenEval 與 ImgEdit 上一致略勝，並引用 REPA 與 Tuna 的發現解釋之。這顯示 representation encoder 提供的 semantic prior 並非可被 raw pixel + masking 完全替代的工程缺陷，而是「在沒有對齊到語言/語意空間的初始條件下，flow matching head 的優化路徑會更曲折」的本質問題。論文的 masking 補丁在 understanding 上提升明顯，但在 generation 上增益僅 0.6 pt (47.6 → 48.2, Table 6)，顯示這條路無法靠同一機制補足。

**Controlled comparison 的範圍過窄，無法支撐通用結論。** Tuna-R 與 Tuna-2 共用同一 LLM backbone、同一資料配方、同一訓練步數，這在「比較兩種視覺端設計」是嚴謹的，但 7B 是 native UMM 的小型尺寸；當模型放大到 14B+（如 BAGEL）或資料增加一個數量級時，encoder 帶來的 inductive bias 是否仍會被 raw-pixel learning 吃掉，論文沒有任何 scaling-law 證據。「encoder-free is the future」的暗示因此屬於外推，而非實驗結論。

### 7.3 Citations Worth Tracking

- **JiT (Li and He, 2025), arXiv:2511.13720.** Tuna-2 直接挪用其 $x$-prediction + $v$-loss 作為 pixel-space generation 的核心；想理解 Tuna-2 為何能在 pixel space 訓練得起來，必須先讀 JiT 的 noise schedule 與 prediction target 設計。
- **NEO / Mono-InternVL (Diao et al., 2025; Luo et al., 2025).** Encoder-free LMM 的代表，Tuna-2 的 patch-embedding-only 設計直接承襲；對照閱讀可釐清 Tuna-2 在「encoder-free understanding」上有多少屬於原創、多少屬於整合。
- **Tuna (Liu et al., 2025), arXiv:2512.02014.** 直接前身，論文許多結論（resolution、ratio、attention map）都建立在與 Tuna 的對照上；要驗證 Tuna-2 的增益是否來自 raw-pixel 還是來自 SFT 配方差異，必讀 Tuna 的 ablation。
- **BAGEL (Deng et al., 2025), arXiv:2505.14683.** 14B native UMM 標竿，論文用灰字輕描淡寫地比較；想評估 Tuna-2 在 scale-matched 條件下的真實實力，BAGEL 的訓練細節與 benchmark 是必要對照。
- **REPA (Yu et al., 2024), arXiv:2410.06940.** 解釋為何 representation encoder 對 generation 仍有幫助的關鍵文獻，論文在 §3.5 直接引用；理解 Tuna-2 在 generation 上輸給 Tuna-R 的「結構原因」需從 REPA 的 representation alignment 觀點切入。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在 compute-matched（同 GPU-hour 而非同 step 數）的條件下，Tuna-2 何時、是否還能反超 Tuna-R？論文目前以 step 數為 x 軸，但 encoder-free 的單步成本未必相同。
- [ ] 將 LLM backbone 從 Qwen2.5-7B 換成完全 random-init 的 transformer 後，「encoder-free」主張是否仍成立？這是區分「真正端到端」與「依賴語言 prior」的關鍵實驗。
- [ ] Masking ratio 與 training step 的最佳排程在 7B 規模是否與 1.5B 規模一致？Table 6 在小模型上以 50% masking 後 50k steps 完成，無法外推。
- [ ] 為何 Tuna-2 在 GenEval Overall 反而低於前身 Tuna？是 raw-pixel 的本質劣勢，還是 SFT 資料配方差異所致？
- [ ] LLM-judge 評測中 Tuna-2 顯著高的 diversity，是來自更豐富的視覺先驗，還是來自尚未充分收斂導致的高 sampling variance？需要 FID + diversity score 雙軸評估。
- [ ] Encoder-free 設計是否能擴展到 video（時間維 token 數量級暴增）？論文僅在靜態圖像上實驗，pixel-space flow matching 的計算成本可能在 video 上失控。
- [ ] 若把 representation encoder 不是「移除」而是「以 EMA / lightweight distillation 的方式蒸餾進 LLM 第一層」，能否同時保留 encoder-based 的早期收斂優勢與 encoder-free 的後期理解優勢？

### 8.2 Improvement Directions

1. **加入 representation alignment loss（REPA 風格）作為 pretraining 的輔助目標。** 論文已自承 generation 端的差距源自 semantic prior 缺失；在 raw-pixel pipeline 中加入對 SigLIP 2 / DINOv2 feature 的 alignment loss，可在不重新引入 encoder 的情況下傳遞 semantic prior，且推論期不付任何成本。可行性高，與現有 pipeline 可加性整合。

2. **報告 compute-matched scaling curve 而非 step-matched curve。** 將 Figure 6 的 x 軸改為 GPU-hour 或 FLOPs，可直接回答「encoder-free 是否真的在 scale 上 favourable」這個論文核心主張。實作上只需重繪曲線，但對結論的可信度提升極大。

3. **以 head-to-head 比較 pure pixel-space 生成模型（JiT、PixelFlow、DiP）隔離貢獻來源。** 目前無法分辨增益來自 unified pretraining 還是 pixel-space flow matching 本身；加入 generation-only baseline 可釐清 unification 對 generation 的真實邊際效用。中等可行，需多訓一組 generation-only。

4. **將 masking 設計升級為 curriculum（前期低 ratio、後期高 ratio）。** 論文在 pretraining 最後 40% 才開始 masking，但 ratio 固定 50%；考慮到 Tuna-2 在高維 pixel space 易走 shortcut，動態 curriculum 可能進一步壓低 understanding 端 OCR / counting 的錯誤率。低成本高槓桿。

5. **建立 cost-axis benchmark 並提供 7B / 13B / 30B scaling laws。** 論文「encoder-free is scalable」目前是外推；在三個尺寸上重複 controlled comparison，可給出真正可被引用的 scaling law。可行性最低（compute 龐大），但對 native UMM 領域的長期影響最大。
