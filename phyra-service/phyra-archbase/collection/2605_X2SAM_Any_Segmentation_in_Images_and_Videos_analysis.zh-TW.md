<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# X2SAM — X2SAM: Any Segmentation in Images and Videos

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | X2SAM |
| Paper full title | X2SAM: Any Segmentation in Images and Videos |
| arXiv ID | 2605.00891 |
| Release date | 2026-05-05 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2605.00891 |
| PDF link | https://arxiv.org/pdf/2605.00891 |
| Code link | https://github.com/wanghao9610/X2SAM |
| Project page | https://wanghao9610.github.io/X2SAM |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Hao Wang | Sun Yat-Sen University; Peng Cheng Laboratory | https://github.com/wanghao9610 | first author |
| Limeng Qiao | Meituan Inc | — | co-author |
| Chi Zhang | Meituan Inc | — | co-author |
| Lin Ma | Meituan Inc | — | co-author |
| Guanglu Wan | Meituan Inc | — | co-author |
| Xiangyuan Lan | Peng Cheng Laboratory | — | corresponding author |
| Xiaodan Liang | Sun Yat-Sen University; Peng Cheng Laboratory | https://lemondan.github.io/ | corresponding author |

### 1.2 Keywords

Multimodal Large Language Model, Segment Anything, Video Object Segmentation, Referring Segmentation, Reasoning Segmentation, Grounded Conversation Generation, Visual Prompting, Mask Memory

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| SAM (Kirillov et al., 2023) | influence | 基礎影像分割模型，提供 promptable segmentation 範式但僅支援低階視覺提示。 |
| SAM2 (Ravi et al., 2024) | base model | X2SAM 採用其 mask encoder 與記憶傳播架構，作為影片分割能力的基礎。 |
| LISA (Lai et al., 2023) | predecessor | 首次以 `<SEG>` token 串接 MLLM 與分割模型的影像分割 MLLM，但僅限靜態影像。 |
| VISA (Yan et al., 2024) | baseline | 影片分割 MLLM 代表方法，支援文字到 mask 生成但缺視覺提示與統一架構。 |
| VideoLISA (Bai et al., 2024) | baseline | 將 LISA 延伸至影片之分割 MLLM，仍未統一影像與影片任務。 |
| X-SAM (Wang et al., 2025) | predecessor | 本作前身，影像中心的 any-segmentation MLLM；X2SAM 在其上加入 Mask Memory 並擴展至影片。 |
| Qwen3-VL (Bai et al., 2025) | base model | X2SAM 採用 Qwen3-VL-4B 之 vision encoder、projector 與 LLM backbone。 |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於將多模態大型語言模型（MLLM）的像素級分割能力，從靜態影像統一延伸至動態影片。作者觀察到目前生態嚴重碎片化：SAM 系列雖能產出高品質 mask 卻只能解讀低階視覺提示，無法理解複雜的對話式指令；以 LISA 為代表的影像分割 MLLM 雖能處理語言指令，但僅限靜態影像、缺乏視覺提示支援；VISA、VideoLISA 等影片分割 MLLM 雖支援時序文字到 mask 生成，卻沒有同時涵蓋影像、影片以及文字、視覺提示的統一架構。為彌合此鴻溝，X2SAM 同時面對三項挑戰：跨模態提示整合、影像與影片任務的時空統一表述，以及確保影片各幀分割一致性的 temporal coherence。論文的研究主題即是建立一個能在單一介面內處理 generic、open-vocabulary、referring、reasoning、GCG、interactive、visual grounded 等七大分割任務於影像與影片之上的統一 segmentation MLLM。

### 2.2 Domain Tags

- Computer Vision
- Multimodal Large Language Models
- Image and Video Segmentation

### 2.3 Core Architectures Used

- **Qwen3-VL-4B**：作為 X2SAM 的 vision encoder、vision projector 與 LLM backbone，提供全域視覺理解與多模態推理能力，並負責生成語言回應與 $\texttt{<SEG>}$ latent embedding。
- **SAM2 Mask Encoder**：被沿用作 fine-grained vision feature 的提取器 $g_m$，逐幀處理影像或影片以產生高解析度 mask 特徵 $Z_m$（原 SAM2 的 mask decoder 則被丟棄）。
- **Redesigned Mask Decoder $g_\psi$**：受 X-SAM 啟發重新設計的 decoder，加入 Query-to-Image Attention 與 zero-initialized Token-to-Image Attention，使 LLM 的 $\texttt{<SEG>}$ token embedding $Z_p$ 能直接條件化空間特徵以產生 mask。
- **Mask Memory Module $g_\omega$**（本作提出）：由 Memory Attention、Memory Encoder 及 FIFO Memory Bank 組成，將語言條件下的 guided vision feature 與 mask logits 一併存入記憶庫，提供時序一致的特徵 $Z_w$ 給後續幀解碼。
- **Region Sampler $g_r$**（parameter-free）：以 mask encoder 的高解析度特徵 $Z_m$ 為基礎做 point sampling 並 adaptive pooling，將視覺提示轉成 region embedding $H_r$ 注入 LLM。
- **LoRA**：對 LLM backbone 做參數高效微調，與其他模組（projectors、mask encoder、mask decoder、mask memory）一同在 unified joint training 中最佳化。

### 2.4 Core Argument

作者主張現有「影像分割 MLLM + 影片傳播器」的串接式設計（如 X-SAM 加 SAM2 的級聯）有根本性缺陷：影像分割 MLLM 把每一幀當成獨立輸入，逐幀解碼 mask 後再交由外部模組做時序傳播，導致語意 grounding 與時序一致性彼此脫鉤；同時 SAM2 的記憶機制只儲存低階視覺特徵，無法承載 LLM 所提供的語言條件，因此一旦目標物受遮擋、變形或多目標糾纏，frame-by-frame 解碼很容易產生 mask 漂移與身份切換。換言之，問題的根因不是缺資料或缺更大模型，而是「語言條件」與「時序記憶」在架構層被切開來。X2SAM 因此提出一條邏輯上必要的整合路徑：(1) 用 `<SEG>` token 將 LLM 的語意條件下放到 mask decoder，使 token 直接透過 Token-to-Image Attention 影響空間特徵；(2) 引入語言條件化的 Mask Memory 模組，將 MLLM 引導後的 vision feature 連同 mask logits 一起編碼進 FIFO memory bank，讓後續幀的 Memory Attention 能拉取「帶語意」的歷史特徵，而非單純像素特徵；(3) 把所有影像與影片分割任務改寫為以條件物件為中心的統一表述，以便用同一份監督訊號做 joint training。透過此設計，grounding、解碼、記憶被同步最佳化，論文據此論證唯有在架構上把語言與時序耦合，MLLM 才能在影片中真正穩定地完成由指令驅動的任意分割。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(245 words)

論文標題「X2SAM: Any Segmentation in Images and Videos」直接揭示三個關鍵字：any-segmentation、images、videos，標示這是一個試圖把 SAM 系列在影像端的「任意分割」能力延伸到影片的統一 MLLM。Abstract 採取「現況—缺口—方法—貢獻—結果」的標準鋪陳：先點出 MLLM 在 image-level 理解強，但 pixel-level 感知（特別是橫跨 image 與 video）受限；接著指出 SAM 系列雖能產生高品質 mask，卻只吃 low-level visual prompts、無法處理對話式指令；現有的 segmentation MLLMs 雖然縮小了這個 gap，但通常專精於 image 或 video 其中一邊，而且很少同時支援 textual 與 visual prompts。

在問題定義完成後，abstract 立刻引入 X2SAM 的核心構造：一個 unified segmentation MLLM，把 LLM 與 Mask Memory module 耦合起來——其中 Mask Memory 用來儲存 guided vision features，以維持影片 mask 的時序一致性。論文宣稱同一套 formulation 即可同時涵蓋 generic、open-vocabulary、referring、reasoning、grounded conversation generation、interactive、visual grounded segmentation 等任務，且 image 與 video 兩種輸入皆可。

Abstract 也預告兩項衍生貢獻：(1) 新的 V-VGD (Video Visual Grounded) segmentation benchmark，用來評估模型能否在影片中以互動式 visual prompt 分割物件 track；(2) unified joint training strategy，跨異質的 image 與 video 資料一起訓練。最後給出實驗高層結論：在影片分割上有強表現、image segmentation 上保持競爭力、且不犧牲 image/video chat 能力。整段 abstract 為後續論文鋪好「統一介面 + 時序記憶 + 聯合訓練」的三條主線。

### 3.2 Introduction

(615 words)

Introduction 的論述沿著「能力光譜上的缺口」推進。首段先描繪 MLLM 的整體進展：在 captioning、VQA、visual editing 等 global understanding 任務上表現亮眼，但 dense、pixel-level 的時空輸出仍然薄弱，這對 fine-grained 任務形成阻礙。第二段把焦點切到 foundation segmentation models：SAM 與 SAM2 雖能產生密集 mask，卻仰賴 low-level 的 points 或 boxes，無法直接消化複雜對話指令。緊接著作者引入 Figure 2 的視覺對比，把現有 segmentation MLLM 分為兩組「結構性破碎」的陣營——LISA 一類的 image-only 模型不支援影片與 visual prompt；VISA、VideoLISA 一類的 video-only 模型則缺乏跨 image 與 visual prompt 的統一架構。這個三段式對比正是論文的「研究缺口」：沒有一個框架能同時詮釋 text + visual prompt 並同時涵蓋 image 與 video。

第四段宣告解法：X2SAM。作者把問題拆成三項技術挑戰，每一項都對應後續方法章節的一個元件：(1) Comprehensive Prompt Integration——讓 LLM 同時處理 interleaved text 與 V-Prompts；(2) Spatio-Temporal Task Formulation——把多種 image segmentation paradigm 改寫成可表達 video 目標的統一 formulation；(3) Temporal Coherence via Mask Memory——以 Mask Memory module 取代 frame-by-frame 解碼，與 Mask Decoder 互動並保留 guided vision features。這三點的鋪排不只說「我們做了什麼」，更鋪陳了「為什麼非得這樣做」。

接著 Figure 3 預告整體 MLLM 架構：global visual representation 加 fine-grained visual features，由 LLM 產生的 latent condition embedding 引導 Mask Decoder，再搭配 Mask Memory 維持影片一致性。Introduction 也順勢推出新基準 V-VGD，將 visual prompting 能力擴展到影片，並利用 Table 1 比對 X2SAM 與其他 chat/segmentation MLLM 的 input/output/task 維度——強調 X2SAM 是首個原生支援七大 image 與七大 video segmentation tasks 的方法。

最後三點 contribution bullet 總結：unified framework、V-VGD benchmark、unified joint training，並以實驗概述（影像競爭力、影片強勢、跨模態 OOD 表現）收尾。Introduction 因此扮演承先啟後的角色：先用 SAM/LISA/VISA 鋪好對手座標，再以三項技術挑戰把後續 §3 Method 的子節（Formulation、Framework、Training）的講述順序合理化，並提前埋好 V-VGD 與聯合訓練這兩條會在 §4 Experiments 被驗證的主線。

### 3.3 Related Work / Preliminaries

(465 words)

§2 Related Work 採三段分類加一段競品對照的結構，並沒有獨立的 preliminaries 段——X2SAM 的數學前提被併入 §3.1 Formulation。三大分類分別是 Multi-modal LLM、Image Segmentation MLLMs 與 Video Segmentation MLLMs，順序刻意呼應 introduction 中對「現況—缺口」的鋪陳。

第一段 Multi-modal LLM 把 MLLM 的演化軌跡定位在「task-specific fusion → instruction-tuned、visual feature tokenization」的脈絡，並重申 global understanding 強、pixel-level 弱的張力，作為後續討論的共同前提。第二段 Image Segmentation MLLMs 從 SAM 與其延伸出發，介紹研究界把 MLLM 與 segmentation 模型結合以處理 open-world、unified architecture、language-guided 任務的趨勢，並以 LISA 為代表，指出其結構限制：只能處理靜態影像，且常缺 V-Prompts 支援。第三段 Video Segmentation MLLMs 則點名 VISA 與 VideoLISA：它們做到了 temporal text-to-mask，但仍缺乏統一的 image+video 架構，且 frame-by-frame decoding 難以系統性地保留多模態 guided features，導致時序一致性脆弱。這三段一路把缺口縮小，使得「需要一個能同時吃 image+video，又能同時吃 text+visual prompt，且具備 mask memory」的論述自然成立。

最後一段「Analysis against SAM2 and X-SAM」是這節的關鍵差異化論述。作者選擇 SAM2 與 X-SAM 兩個最容易被誤認為「拼裝目標」的競品做正面比較：SAM2 雖具 memory-based propagation，但仰賴 low-level prompt、無 language reasoning 與 grounded conversation；X-SAM 雖支援 textual 與 visual prompts，但 image-centric 且不建模 temporal object identity。作者明確拒絕 X2SAM 等於 X-SAM+SAM2 級聯這個簡化解讀，強調 X2SAM 把 textual prompts、visual prompts 與生成的 <SEG> token 統一轉成 mask-aware conditions，並讓 language-conditioned Mask Memory 直接儲存 MLLM-conditioned decoder 給出的 guided visual features，把 semantic grounding 與 temporal propagation 聯合最佳化，而非分階段串接。

整節因此完成兩件事：(1) 為 X2SAM 在文獻光譜上佔位，劃出 image-only、video-only、cascade 三條被超越的軌跡；(2) 預告 §3 Method 必須回答「Mask Memory 如何同時消化語義 token 與時序傳播」這個被反覆強調的差異點。

### 3.4 Method (overview narrative)

(395 words)

§3 Method 採「Formulation → Framework → Training」三段式結構，刻意把概念層、架構層與最佳化層拆開，使讀者先理解 X2SAM 把世界看成什麼樣子，再看它如何被組裝與訓練。

§3.1 Formulation 先定義 inputs（text 或 visual prompt 加 single image 或 video sequence）與 outputs（contextual language response 加 binary segmentation mask）。其後的 Unified Formulation 是整章思路的關鍵：把所有 image 與 video segmentation 任務的「objects of interest」抽象成 conditional states，把 language instruction 視為 contextual input，並沿用 X-SAM 的 `<p>`、`</p>` 標記物件條件、以 `<SEG>` token 表示對應的 mask。`<SEG>` 在 LLM 輸出端的隱藏表徵會作為 mask decoder 的指引，再以 task-specific templates 對齊不同任務的回應格式。這層抽象讓 generic、referring、reasoning、GCG、interactive、VGD 等多元任務在 §3.2 共用同一條資料流。

§3.2 Framework 描繪整體架構（Figure 3）：給定指令 $X_q$ 與視覺輸入 $X_v \in \mathbb{R}^{T \times H \times W \times C}$（$T=1$ 為 image、$T>1$ 為 video），dual-branch visual extraction 由 vision encoder $f_v$ 抓 global representation $Z_v$、mask encoder $g_m$ 抓 fine-grained $Z_m$；經 projector 變成 $H_v$、region sampler $g_r$ 給出 $H_r$，與 token 化的指令 $H_q$ 一同送入 LLM $f_\phi$。LLM 自迴歸生成 $Y_q$ 與 SEG latent embedding，後者經 MLLM projector 變成 prompt token embedding $Z_p$。最後 mask decoder $g_\psi$ 整合 $Z_p$、learnable mask queries $Q_m$，以及由 mask memory module $g_\omega$ 透過 FIFO cache 提供的時序精煉特徵 $Z_w$，輸出 $Y_m$。Input Processing、Vision Encoder & LLM、Region Sampler、Mask Encoder & Decoder、Mask Memory 等小節依序定位每個元件的職責，但細節會在 §5 元件章節展開。

§3.3 Training 把訓練拆成兩階段：先做 Agnostic Segmentor Training（凍結 mask encoder，只用 mask-only SA-1B 訓 mask decoder，以 $L_{\text{mask}} = \lambda_{\text{bce}} L_{\text{bce}} + \lambda_{\text{dice}} L_{\text{dice}}$ 取得形狀與邊界先驗）；再做 Unified Joint Training，搭配 dimension-shifting pipeline、modality-aware batching、temporal-aware sampler 與 modality-specific gradient accumulation，並用 $L_{\text{joint}}$ 在 chat 與 segmentation 任務之間切換 loss 組合。整章因而為 §4 的實驗鋪好兩條主線：架構是否真能涵蓋 14 任務、聯合訓練是否確實有效率優勢。

### 3.5 Experiments (overview narrative)

(390 words)

§4 Experiments 的鋪陳節奏依序為：先界定評估對象（Tasks/Datasets/Metrics）、再交代 Implementation Details、再以 Ablation Studies 驗證關鍵設計、最後以 Benchmark Results 對外比較。整章的核心目標是檢驗 introduction 中提出的三項主張：unified formulation 是否真能涵蓋 14 任務、Mask Memory 是否真能改善時序一致性、Unified Joint Training 是否真能同時兼顧效能與效率。

§4.1 把任務面攤開：image 與 video 各有七項任務，含 generic、open-vocabulary、referring、reasoning、GCG、interactive/object-centric、visual grounded segmentation；資料端涵蓋 SA-1B（agnostic 階段）、X-SAM 同款 image 配置、VIPSeg/VSPW/YT-VIS19/YT-RefVOS/ReVOS/VideoGLaMM/YT-VOS19/DAVIS17 等 video 來源，並引入新建的 YT19-VGD 與 VIPSeg-VGD 作為 V-VGD benchmark。Metrics 維持各 sub-task 的標準（如 (V)PQ、mAP、mIoU、cIoU/gIoU、$\mathcal{J}\&\mathcal{F}$、METEOR、CIDEr、AP/AP$_{50}$），確保跨表可比較。

§4.2 Implementation Details 揭露 baseline 用 Qwen3-VL 做 vision encoder + LLM、SAM2 做 mask encoder，加上 LoRA 微調 LLM；effective batch size 影像 128、影片 32，memory size 預設 8（最終採 6）。這些設定為後續的 ablation 比較提供可重現基線。

§4.3 Ablation Studies 連續驗證四個關鍵設計：(1) Mask Decoder 中 Token-to-Image attention 的 zero-init 比 random-init 更穩定，且明顯帶動影片端 metric；(2) Joint Training 比較 separate / simple / unified 三種策略，unified 把訓練成本從 ~5.2K GPU hours 壓到 3.3K，同時不損效能；(3) Mask Memory 從 single-scale → mask guide → class guide → multi-scale 階段性提升，最終 multi-scale 在 V-Gen.、V-Ref.、V-Rea. 都到頂；(4) Memory Size 顯示 6 frames 是最好折衷，過大反而引入冗餘雜訊。

§4.4 Benchmark Results 把模型放到 image 與 video 統一表 (Table 6) 對比各路 specialist 與 generalist：在 image 端維持與 X-SAM 相當水準、在 I-OV 上明顯提升；在 video 端對 UniPixel、HyperSeg、VideoGLaMM 等基線多有勝出；Reasoning Segmentation (Table 7) 與 Out-of-Domain (Table 8) 進一步顯示其推理能力與分布外泛化；V-VGD (Table 9) 則直接展示 Mask Memory 與 region sampler 在影片視覺提示下的領先。整章層層收斂，把 introduction 的承諾逐項落地。

### 3.6 Conclusion / Limitations / Future Work

(295 words)

§5 Discussion 採「Conclusion + Limitations and Outlook」兩段收束。Conclusion 段先回顧整篇論文的三條主線：第一，X2SAM 把多元 segmentation 任務統一成 instruction-following formulation，textual instruction 與 visual prompt 共用同一介面；第二，引入 Mask Memory module 把 image-centric 的 any-segmentation 能力延伸到影片，提升時序一致性；第三，新提出的 V-VGD benchmark 用以評估「以互動式 visual prompt 在影片中接地物件」的能力。緊接著肯定 adaptive joint training strategy 在異質 image 與 video 資料上實現有效率的 co-training，降低訓練成本同時平衡跨模態效能。最後總結實驗結論：在 task coverage 與 accuracy 之間取得良好折衷——image segmentation 維持競爭力、video segmentation 多項提升、image/video 一般理解能力被保留。這段並沒有引入新概念，主要扮演對 abstract 與 introduction 預告的回收。

Limitations and Outlook 則點出三項自我揭露的弱點：(1) 跨 image 與 video 的 unified training 成本仍偏高，影片樣本記憶體開銷尤其大；(2) 固定大小的 FIFO memory 對長影片中長時間遮擋、外觀劇變或目標稀疏重新出現的情境支撐不足；(3) 作為 unified generalist，在 narrowly focused 任務（如高度最佳化的 video object segmentation 或純影像 segmentation）仍可能落後 specialist 模型。這些限制其實對應 §4 中 V-Obj./VOS specialist 仍領先、Memory Size ablation 中 size 變大反而退步等實驗觀察，使結尾與實驗章節形成閉環。

Future work 沿著上述三點展開：探索更有效率的訓練、輕量化 backbone，以及 adaptive long-range memory 來改善可擴展性與穩健性。這個收尾不僅自然，也預告若有 X2SAM 後續版本，最可能的改進方向會是 memory 架構（從 fixed FIFO 走向 adaptive long-range）與訓練成本控制，而非任務覆蓋面的進一步擴張。

## 4. Critical Profile

### 4.1 Highlights

- X2SAM 是 Table 1 中第一個同時宣稱涵蓋 image 與 video 各 7 項分割任務（共 14 項）的 MLLM，在 input/output/task 三個欄位的支援廣度上勝過 X-SAM、Sa2VA、HyperSeg。
- Mask Memory 模組的消融（Table 4, p.8）顯示 V-Ref YT21 從 baseline 53.6 J&F 提升到 65.0 J&F、V-Rea 從 36.5 提升到 53.5 J&F，顯示語言條件化的 FIFO memory 對時序穩定性有實質貢獻。
- V-Rea 在 ReVOS 上達到 69.9 J&F（Table 7, p.10），相對於 HyperSeg 的 55.7 提升 +14.2，且 Ref 與 Rea 兩個子集分數幾乎一致（69.3/70.7），暗示推理與 referring 在統一架構下達到平衡。
- V-GCG 在 Video-GLaMM 評估協定下達到 75.8 mIoU（Table 18, p.18），相較作者重新評估後的 Video-GLaMM 54.3 mIoU 提升 +21.5。
- 在自建的 V-VGD 基準（Table 9, p.11）以 box prompt 在 YT-VIS19 取得 74.4 AP、VIPSeg 取得 57.8 AP，相對 SAM2-H 的 54.0 / 40.4 AP 大幅領先，顯示 region sampler 與 mask memory 對視覺提示的時序傳播有效。
- Unified joint training（Table 3, p.8）將訓練成本從 simple joint 的約 5.2K GPU-hours 縮減至 3.3K GPU-hours（−36.5%），同時維持 image 指標並提升 V-Gen mIoU 至 64.7。
- Token-to-Image Attention 採用 zero-initialization（Table 2, p.8）使 V-Ref YT21 從 baseline 53.6 上升到 60.8 J&F，並避免 random init 在 image 指標上的退步。
- Out-of-domain 評估（Table 8, p.10）在 ADE20K 達 31.2 PQ / 38.2 mIoU、YT-VIS-21 V-OV 達 60.3 AP / 78.0 AP50，均超越 X-SAM、HyperSeg 等近期 generalist。
- Image chat 能力（Table 20, p.18）MMBench 83.5、SEED-Bench 76.0、AI2D 82.0，幾乎追平甚至超越 LLaVA-OV 等 chat-only 基線，顯示加入 dense segmentation 並未明顯損及通用視覺理解。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- Section 5 Limitations（p.11）承認 unified training 在 video 樣本上記憶體成本高、整體運算昂貴。
- Section 5（p.11）指出固定大小 FIFO memory 在「長片段、長時間遮擋、外觀劇烈變化或目標稀疏再出現」時不足，這正是 Mask Memory 設計的核心場景。
- Section 5（p.11）承認作為 generalist 仍落後於專精模型，例如 video object segmentation 上不如 SAM2-H（Table 19，YT-VOS19 J&F 74.0 vs SAM2-H 88.8）。
- Section 4.4 Overall Performance（p.10）也明白點出 video VOS specialists 與 X2SAM 的差距是「維持通用介面的代價」。

#### 4.2.2 Phyra-inferred

- 對比 X-SAM（Table 6, p.9），X2SAM 在多個 image 指標上實際退步：I-Gen PQ 54.7→54.1、I-Ref RefCOCO 85.1→84.0、I-GCG mIoU 69.4→67.1、I-VGD point AP 47.9→45.9，論文僅以「remains competitive」帶過而未承認回歸的代價，使「擴展到 video 不損及 image」的論述被選擇性陳述。
- 主要的 V-GCG 對比（Table 18, p.18）使用作者「re-evaluated」後的 Video-GLaMM 數字 54.3 mIoU，而原始論文報告為 62.3 mIoU；75.8 vs 54.3 的 +21.5 提升是建立在重新評估的 baseline 上，重評理由與差距 8 mIoU 的成因論文並未交代。
- Memory size 結論不一致：§3.2 與 Table 12 的預設為 $K=8$，但 Table 5 顯示 $K=6$ 在 V-OV 與 V-Rea 才是最佳，且 Table 12 hyperparameters 註明「memory capacity is fixed at 8」與正文「we adopt 6 frames as the final memory size」直接衝突，難以判斷主表 Table 6 究竟用哪個設定。
- V-VGD 是作者自行構造的基準（Appendix B, p.13–14），visual prompt 自第一個可見 frame 自動產生（point/box/scribble/mask），SAM2-H 並未針對這個分布訓練，因此 Table 9 的「+20 AP」實質是 in-distribution vs zero-shot 的對比，而非架構優劣的乾淨對照。
- 主要實驗為 1 epoch、單次跑、未報告 seed variance（§4.2 Training Setup, p.8 與 Appendix D, p.15），所有「+X 點」聲明都缺乏統計顯著性支撐。
- 論文核心反例假設是「frame-by-frame X-SAM+SAM2 cascade 失敗」，但 §2 Analysis against SAM2 and X-SAM（p.4）只給出概念層論述，沒有實作出 cascade baseline 並比較 V-Rea / V-Ref，導致「joint coupling 比 cascade 更好」的核心結論缺乏直接證據。
- LLM 透過 LoRA（rank=128, $\alpha=256$, Table 12）微調，但 mask encoder / decoder / memory 全參數訓練，論文沒有分析究竟是 LLM 推理還是 mask 子網路在 V-Rea 上扮演主要角色，使「LLM 語意條件下放」的歸因無法驗證。
- Mask Memory 只儲存解碼後的 guided vision feature，當前一幀 mask 出現 identity switch 時，錯誤訊號會直接被寫入 memory bank 並傳播；論文宣稱解決 mask drift 但沒有針對 occlusion / re-identification 的失敗模式 ablation。

### 4.3 Phyra's Judgment (summary)

X2SAM 真正新穎的地方在於把 LLM 的 `<SEG>` 條件嵌入 mask decoder，再把「被語言引導後的 vision feature」寫進 FIFO memory，使 grounding 與時序傳播在同一份梯度下被聯合優化；這個耦合方式在 V-Rea、V-Ref、V-GCG 的數字上確實兌現。其餘大部分屬於 X-SAM 與 SAM2 兩個既有元件的工程整合（dual-branch encoder、region sampler、joint training pipeline）。論文未解決的核心問題是：相對於一個被認真調教過、共享同一個 MLLM 的 X-SAM+SAM2 cascade，X2SAM 的端到端耦合究竟貢獻多少；目前所有結論都只與 frame-wise 或 cascade-free baseline 對照，cascade 對照組缺席。

## 5. Methodology Deep Dive

### 5.1 Method Overview

X2SAM 是一個以 segmentation 為目標的統一 MLLM 架構，將指令驅動的像素級分割能力從靜態影像延伸至動態影片。核心設計圍繞兩個關鍵問題：(1) 如何讓 LLM 的語意條件深入引導 mask decoding，避免語言理解與空間預測脫鉤；(2) 如何在影片各幀間維持時序一致性，避免逐幀獨立解碼導致的 mask drift 與 identity switch。為此，作者建立 dual-branch visual extraction 架構：vision encoder $f_v$ 從 Qwen3-VL-4B 抽取全域語意表徵 $Z_v$，而 mask encoder $g_m$ 沿用 SAM2 設計擷取細粒度多尺度特徵 $Z_m$，分別承擔 semantic understanding 與 dense prediction 兩種互補任務。

LLM $f_\phi$ 接收三類輸入 token：投影後的全域視覺特徵 $H_v = W_v(Z_v)$、來自 region sampler $g_r$ 的區域特徵 $H_r$（用於視覺提示），以及 tokenized 文字嵌入 $H_q$。在 auto-regressive 生成過程中，LLM 同時輸出語言回應 $Y_q$ 與專屬的 `<SEG>` latent embedding，後者透過 MLLM projector 轉為 prompt token embedding $Z_p$，扮演 language understanding 與 mask prediction 之間的 semantic bridge。Mask decoder $g_\psi$ 結合 $Z_p$、learnable mask queries $Q_m$ 與來自 mask memory 模組 $g_\omega$ 的時序精煉視覺特徵 $Z_w$，最終合成分割 mask $Y_m \in \mathbb{R}^{T \times H \times W}$。Decoder 內部以 zero-initialized Token-to-Image Attention 將 $Z_p$ 注入 spatial features，確保訓練早期穩定收斂。

Mask memory 模組 $g_\omega$ 是 X2SAM 區別於前代 X-SAM 與一般 SAM2 cascade 設計的關鍵：它以 FIFO 策略維護一個容量 $K$ 的 memory bank，儲存「被 LLM 引導過」（即經過 mask decoder 解碼後）的 vision features 與 mask logits，並透過 memory attention 在解碼當前幀時拉取歷史語意脈絡。記憶體承載的不僅是低階 pixel features，而是 language-conditioned 的高階表徵，因此能在遮擋、變形或多目標糾纏場景下同步維持 grounding 與 temporal coherence；訓練上以 unified joint training 將影像與影片任務以 dimension-shifting pipeline 統一處理，搭配 modality-aware batching 與 temporal-aware sampler 提升效率。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input:
  X_v ∈ [B, T, H, W, 3]      (T=1: image;  T>1: video)
  X_q ∈ [B, L_q]             (text token IDs)
  V-Prompts (optional)       (points / boxes / regions)

  ┌─ Dual-Branch Visual Extraction ─────────────────────────────┐
  │                                                             │
  │  X_v ──► Vision Encoder f_v ─► Z_v ∈ [B, T, N_v, d_v]       │
  │           (Qwen3-VL-4B,                  │                  │
  │            patch + timestamp)            ▼                  │
  │                                Vision Projector W_v (MLP)   │
  │                                          │                  │
  │                                          ▼                  │
  │                                 H_v ∈ [B, T·N_v, d_l]       │
  │                                                             │
  │  X_v ──► Mask Encoder g_m ─► Z_m ∈ [T, B, h_s, w_s, d_m]    │
  │           (SAM2, frame-wise,         (multi-scale s=1..S)   │
  │            joint-training: trainable)        │              │
  │                                              ▼              │
  │                                  Region Sampler g_r         │
  │                                  (point-sample on Z_m,      │
  │                                   adaptive-pool, k=4)       │
  │                                              │              │
  │                                              ▼              │
  │                                  H_r ∈ [B, N_r, d_l]        │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘

  X_q ──► Tokenizer + Embed ─► H_q ∈ [B, L_q, d_l]

         (H_v ⊕ H_r ⊕ H_q)  ─► concatenated input sequence
                  │
                  ▼
   ┌─ LLM f_φ  (Qwen3-VL backbone, LoRA fine-tuning) ─────┐
   │   auto-regressive decoding                           │
   │                                                      │
   │   ──► Y_q  (language response, text tokens)          │
   │   ──► <SEG> hidden state  h_seg ∈ [B, N_seg, d_l]    │
   └──────────────────────────────────────────────────────┘
                  │
                  ▼
          MLLM Projector (MLP)
                  │
                  ▼
       Z_p ∈ [B, N_seg, d_p]   (prompt token embedding)
                  │
                  │  (per-frame iteration over t = 1..T)
                  ▼
   ┌─ Mask Memory Module g_ω ─────────────────────────────┐
   │                                                      │
   │   Z_m^{(t)} ∈ [B, h_s, w_s, d_m] (multi-scale)       │
   │                       │                              │
   │                       ▼                              │
   │   (a) Memory Attention                               │
   │        Q ← Z_m^{(t)}                                 │
   │        K,V ← Memory Bank (past guided features)      │
   │                       │                              │
   │                       ▼                              │
   │   Z_w^{(t)} ∈ [B, h_s, w_s, d_m]                     │
   │   (temporally-refined vision features, multi-scale)  │
   │                                                      │
   └───────────────────────┬──────────────────────────────┘
                           │
                           ▼
   ┌─ (b) Mask Decoder g_ψ ───────────────────────────────┐
   │      inputs:                                         │
   │        Q_m ∈ [N_q, d_q]   (learnable mask queries)   │
   │        Z_p ∈ [B, N_seg, d_p]                         │
   │        Z_w^{(t)} ∈ [B, h_s, w_s, d_m]                │
   │                                                      │
   │      blocks (× L):                                   │
   │        Self-Attn(Q_m)                                │
   │        Query-to-Image Attn(Q_m × Z_w)                │
   │        Token-to-Image Attn(Z_p × Z_w, zero-init)     │
   │        FFN                                           │
   │                                                      │
   │      ──► mask logits  M^{(t)} ∈ [B, N_q, H, W]       │
   │      ──► class preds  C^{(t)} ∈ [B, N_q, K_cls]      │
   └──────────────────────┬───────────────────────────────┘
                          │  (mask logits + downsampled Z_m)
                          ▼
   ┌─ (c) Memory Encoder ─────────────────────────────────┐
   │      Mask DS  +  Vision DS  ──► Memory Fuser         │
   │                              ──► Memory Projector    │
   │      ──► guided vision feature g^{(t)} ∈ [B, ?, ?, ?]│
   └──────────────────────┬───────────────────────────────┘
                          │
                          ▼
   ┌─ (d) Memory Bank (FIFO, capacity K) ─────────────────┐
   │      push g^{(t)}; pop oldest if |bank| > K          │
   │      (default K=8; ablation best K=6)                │
   └──────────────────────────────────────────────────────┘

Output:
  Y_q  (language response)
  Y_m ∈ [B, T, H, W]  (binary segmentation mask, concatenated over t)
```

註：標記為 `?` 的維度（$d_v$、$d_l$、$d_m$、$d_p$、$d_q$、$N_v$、$N_q$、$N_r$、$N_{seg}$、$h_s, w_s$ 之具體取值，以及 memory encoder 輸出的 spatial/channel 大小）論文未明確提供；多尺度索引 $s$ 與 mask decoder 區塊數 $L$ 同樣未指定，下方 Implementation Details 中有對應說明。

### 5.3 Per-Module Breakdown

#### 5.3.1 Vision Encoder + Vision Projector

**Function:** 從輸入 $X_v$ 抽取全域語意視覺表徵，並將其投影至 LLM token 空間，作為 LLM 的視覺輸入 prefix。

**Input:**
- Name: $X_v$
- Shape: `[B, T, H, W, 3]`，$T=1$ 為影像，$T>1$ 為影片
- Source: 原始影像或影片 frame 序列（含 timestamp 標記）

**Output:**
- Name: $H_v$
- Shape: `[B, T·N_v, d_l]`，$d_l$ 為 LLM hidden size
- Consumer: LLM $f_\phi$（與 $H_r$、$H_q$ 拼接）

**Processing:**

(1) Vision encoder $f_v$ 沿用 Qwen3-VL-4B：對每幀影像加上 timestamp 編碼，分割為 spatial patches，並投影為 latent embeddings $Z_v \in \mathbb{R}^{B \times T \times N_v \times d_v}$。
(2) Vision projector $W_v$（MLP）將 $Z_v$ 對齊至 LLM token 空間：$H_v = W_v(Z_v)$；視訊情況下沿時間維度展平，與其他 token 統一拼接。

**Key Formulas:**

$$
H_v = W_v(f_v(X_v))
$$

**Implementation Details:**

採用 Qwen3-VL-4B 預訓練權重；LLM 部分以 LoRA 微調。具體 patch size、$N_v$ 與 $d_v, d_l$ 數值論文未明示。Joint training 階段透過 dimension-shifting 將 `[B, T, H, W, 3]` 重排為 `[T, B, H, W, 3]` 後逐幀處理，再沿時間維度拼回。

#### 5.3.2 Mask Encoder

**Function:** 為每幀提取 high-resolution 的 multi-scale fine-grained features，作為 mask decoding 與 region sampling 的空間依據。

**Input:**
- Name: $X_v$
- Shape: `[B, T, H, W, 3]`（內部以 frame-wise 方式處理為 `[T, B, H, W, 3]`）
- Source: 原始影像或影片 frame 序列

**Output:**
- Name: $Z_m$
- Shape: `[T, B, h_s, w_s, d_m]`，多尺度 $s = 1, \dots, S$
- Consumer: Region Sampler $g_r$、Mask Memory $g_\omega$（Memory Attention 的 Query/輸入；Memory Encoder 的 Vision DS 來源）

**Processing:**

採用 SAM2 的 mask encoder 權重，逐幀提取多尺度 spatial features。在 agnostic segmentor training 階段保持 frozen；joint training 階段以較小 learning rate（$1\times10^{-5}$）解凍微調。

**Key Formulas:**

$$
Z_m = g_m(X_v)
$$

**Implementation Details:**

直接重用 SAM2 的 lightweight mask encoder；輸出 multi-scale resolution（$h_s, w_s$）與 channel $d_m$ 的具體數值論文未提供，僅指出沿用 SAM2 預訓練權重並支援多尺度。 

#### 5.3.3 Region Sampler

**Function:** 將使用者提供的 visual prompts（point、box 等）轉為 LLM 可消費的 region-level token 嵌入，使 LLM 能將視覺指引與語言指令對齊。

**Input:**
- Name: $Z_m$、V-Prompts（regions of interest）
- Shape: $Z_m$ 之 `[B, h_s, w_s, d_m]`；V-Prompts 為座標／區域描述
- Source: Mask Encoder $g_m$；使用者輸入

**Output:**
- Name: $H_r$
- Shape: `[B, N_r, d_l]`，$N_r$ 為 region 數
- Consumer: LLM $f_\phi$

**Processing:**

(1) 在 $Z_m$ 上對 V-Prompt 指定的 region 進行 point-sampling。
(2) 對 sampled point features 套用 adaptive pooling（kernel size = 4），聚合為 region-level representation。
(3) 投影對齊至 LLM token 維度 $d_l$。整體為 parameter-free（pooling 為固定運算，僅含投影層）。

**Key Formulas:**

$$
H_r = \mathrm{AdaPool}_{k=4}\bigl(\mathrm{PointSample}(Z_m, R)\bigr)
$$

其中 $R$ 為使用者提供的 regions。

**Implementation Details:**

論文設定 adaptive pooling kernel size $k=4$；具體 $N_r$ 隨輸入 V-Prompt 數動態決定。Region Sampler 屬 parameter-free 設計，計算量低且可直接整合到 LLM 輸入序列。

#### 5.3.4 LLM (Qwen3-VL backbone with LoRA) + MLLM Projector

**Function:** 統一處理文字指令與視覺 token，自迴歸生成語言回應 $Y_q$，並產生專屬 `<SEG>` latent embedding 作為 mask decoder 的 semantic condition。

**Input:**
- Name: $H_v, H_r, H_q$
- Shape: 拼接序列 `[B, T·N_v + N_r + L_q, d_l]`
- Source: Vision Projector、Region Sampler、Tokenizer

**Output:**
- Name: $Y_q$、$Z_p$
- Shape: $Y_q$ 為文字 token 序列；$Z_p \in $ `[B, N_seg, d_p]`
- Consumer: 使用者（$Y_q$）；Mask Decoder $g_\psi$（$Z_p$，作為 prompt token）

**Processing:**

(1) LLM $f_\phi$ 接受拼接後的多模態 token 序列，auto-regressive 生成 $Y_q$；輸出序列中的 `<SEG>` token 對應 hidden state $h_{seg} \in \mathbb{R}^{B \times N_{seg} \times d_l}$。
(2) MLLM Projector（MLP）將 $h_{seg}$ 映射為 prompt token embedding $Z_p$，作為語意指令注入 mask decoder。
(3) 依 unified formulation，所有任務透過 `<p>...</p>` 標示物件條件、以 `<SEG>` 標示對應 mask；任務模板（generic / referring / reasoning / GCG / interactive / VGD / OV 等）共用相同界面。

**Key Formulas:**

$$
(Y_q, h_{seg}) = f_\phi(H_v \oplus H_r \oplus H_q), \quad Z_p = \mathrm{MLP}(h_{seg})
$$

語言生成損失（auto-regressive）為 $\mathcal{L}_{ar}$，並於 segmentation 任務追加 mask 與 class 損失。

**Implementation Details:**

LLM 採用 Qwen3-VL-4B backbone 並以 LoRA 微調；MLLM Projector 為 MLP。Token 拼接順序、`<SEG>` token 的具體數量 $N_{seg}$（每個目標物件對應一個 `<SEG>`）與 $d_p$ 數值論文未明確提供。在 image-only 與 video chat 模式下，僅啟用 $\mathcal{L}_{ar}$；segmentation 任務則使用聯合損失 $\mathcal{L}_{joint}$。

#### 5.3.5 Mask Memory Module（Memory Attention + Memory Encoder + Memory Bank）

**Function:** 維護 language-conditioned 的時序記憶，為當前幀提供「帶語意」的歷史上下文，以維持跨幀 mask 一致性。

**Input:**
- Name: 當前幀 $Z_m^{(t)}$、Memory Bank 中的 guided vision features $\{g^{(t-1)}, g^{(t-2)}, \dots\}$；以及 mask decoder 反饋的 mask logits $M^{(t)}$
- Shape: $Z_m^{(t)} \in$ `[B, h_s, w_s, d_m]`；guided features 與其同形
- Source: Mask Encoder $g_m$（當前幀）；Memory Bank（歷史幀）；Mask Decoder（mask logits）

**Output:**
- Name: $Z_w^{(t)}$（temporally-refined features，送入 Mask Decoder）；$g^{(t)}$（更新進 Memory Bank）
- Shape: $Z_w^{(t)} \in$ `[B, h_s, w_s, d_m]`
- Consumer: Mask Decoder $g_\psi$；Memory Bank（FIFO 更新）

**Processing:**

(1) **Memory Attention**：以 $Z_m^{(t)}$ 為 Query，以 Memory Bank 中過去幀的 guided vision features 為 Key/Value 進行 cross-attention，產生 temporally-refined features $Z_w^{(t)}$。論文表 4 顯示 multi-scale 設計顯著優於 single-scale，並驗證 mask guidance 與 class guidance 的累積增益。
(2) **Memory Encoder**：Mask DS 與 Vision DS 分別下採樣 mask logits 與 $Z_m^{(t)}$，再經 Memory Fuser 融合並由 Memory Projector 投影為 guided vision feature $g^{(t)}$。
(3) **Memory Bank**：以 FIFO 策略維護容量 $K$ 的環形緩衝區；新幀的 $g^{(t)}$ 推入後，最舊項自動淘汰。

**Key Formulas:**

$$
Z_w^{(t)} = \mathrm{MemAttn}\bigl(Z_m^{(t)},\, \mathrm{Bank}_{<t}\bigr), \quad g^{(t)} = \mathrm{MemEnc}\bigl(Z_m^{(t)},\, M^{(t)}\bigr)
$$

$$
\mathrm{Bank}_t = \mathrm{FIFO}\bigl(\mathrm{Bank}_{t-1},\, g^{(t)};\, K\bigr)
$$

**Implementation Details:**

預設 $K=8$；ablation（表 5）顯示 $K=6$ 在 V-OV、V-Rea. 取得最佳結果，過大記憶（$K=8$）反而引入冗餘或噪聲。Memory bank 中 guided features 的具體 spatial/channel 維度論文未提供；Memory Encoder 內部 DS 比例與 Memory Fuser 的具體結構亦未細述。

#### 5.3.6 Mask Decoder

**Function:** 整合 LLM 提供的 semantic condition、learnable queries 與時序精煉視覺特徵，輸出當前幀的 mask logits 與 class predictions。

**Input:**
- Name: $Z_p$、$Q_m$、$Z_w^{(t)}$
- Shape: $Z_p \in$ `[B, N_seg, d_p]`；$Q_m \in$ `[N_q, d_q]`（learnable parameters）；$Z_w^{(t)} \in$ `[B, h_s, w_s, d_m]`
- Source: MLLM Projector；Decoder 自身可學參數；Mask Memory $g_\omega$

**Output:**
- Name: $Y_m^{(t)}$（mask）、$C^{(t)}$（class）
- Shape: mask logits 上採樣後為 `[B, N_q, H, W]`；class predictions 為 `[B, N_q, K_{cls}]`
- Consumer: 影格序列拼接後輸出 $Y_m \in$ `[B, T, H, W]`；mask logits 同時回饋至 Memory Encoder

**Processing:**

逐層堆疊以下子模組（圖 4(b)）：

(1) Self-Attention 在 $Q_m$ 內部交換訊息。
(2) Query-to-Image Attention：$Q_m$ 對 $Z_w^{(t)}$ 做 cross-attention，提取與每個 query 對齊的空間特徵。
(3) Token-to-Image Attention：$Z_p$ 對 $Z_w^{(t)}$ 做 cross-attention，將 LLM 的 semantic condition 注入空間特徵；該層採 zero-initialization，確保訓練早期不破壞既有的 spatial representation。
(4) FFN 輸出最終 query/token features，分別經 Cls. Pred.（softmax）與 Mask Pred.（sigmoid）產生類別與 mask logits。

**Key Formulas:**

$$
Y_m^{(t)},\, C^{(t)} = g_\psi\bigl(Z_p,\, Q_m,\, Z_w^{(t)}\bigr)
$$

訓練上聯合最佳化（segmentation 任務）：

$$
\mathcal{L}_{mask} = \lambda_{bce}\,\mathcal{L}_{bce} + \lambda_{dice}\,\mathcal{L}_{dice}, \quad \lambda_{bce}=\lambda_{dice}=5.0
$$

$$
\mathcal{L}_{joint} = \mathcal{L}_{ar} + \mathcal{L}_{mask} + \mathcal{L}_{cls}
$$

其中 $\mathcal{L}_{cls}$ 採 focal loss。

**Implementation Details:**

Token-to-Image Attention 的 zero-init 是 ablation（表 2）相較 random-init 的關鍵：random-init 在 I-Ref 上反而拉低 cIoU（如 RefCOCO/+/g 由 baseline 82.9/78.0/79.5 降至 82.5/77.2/79.4），zero-init 則可穩定提升至 83.3/77.8/79.5，並大幅改善 V-Ref（YT21 由 53.6 提升至 60.8 J&F）。Decoder 區塊堆疊層數 $L$、$N_q$ 與 $d_q$ 之具體數值論文未提供。Agnostic segmentor training 階段以 $\mathcal{L}_{mask}$（$\lambda_{bce}=\lambda_{dice}=5.0$）為唯一監督，batch size 128、learning rate $1\times10^{-4}$；joint training 階段 video batch size 32、image batch size 128，AdamW（weight decay 0.05），主實驗在 32 張 NVIDIA H800 上訓練 1 epoch。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| SA-1B [8] | Agnostic segmentor (mask-only) | the paper does not specify (large-scale) | train |
| LLaVA-1.5 + Image Benchmarks [15, 55–59] | I-Chat | 624.6K | train + eval (MME, MMBench, SEED-Bench, POPE, AI2D) |
| COCO [60] | I-Gen. (panoptic/semantic/instance) | 118.3K | train / val |
| ADE20K (A150) [46] | I-OV | the paper does not specify | val (out-of-domain, eval-only) |
| RefCOCO / RefCOCO+ / RefCOCOg [45] | I-Ref. | 302.4K (combined w/ gRefCOCO) | train / val / testA / testB |
| gRefCOCO [45] | I-Ref. (generalized) | included in 302.4K | val / testA / testB (out-of-domain, eval-only) |
| ReasonSeg [10] | I-Rea. | 0.2K | train / val / test (short/long/overall) |
| Grand-fGCG / RefCOCOgGCG / PSGGCG / FlickrGCG [28] | I-GCG | 196.1K | train / val / test |
| COCO-Int. [30] | I-Int. | the paper does not specify | train / val (point/scribble/box/mask) |
| COCO-VGD [22] | I-VGD | 117.3K | train / val (point/box) |
| VideoChatGPT VideoInstruct100K [44] + Video Benchmarks [61–64] | V-Chat | 13.3K | train + eval (VideoMME, MVBench, MLVU, LongVideoBench) |
| VIPSeg [38] | V-Gen. (panoptic) | included in 30.7K (V-Gen. total) | train / val |
| VSPW [39] | V-Gen. (semantic) | included in 30.7K | train / val |
| YT-VIS19 [40] | V-Gen. (instance) | included in 30.7K | train / val |
| YT-VIS21 [40] | V-OV | the paper does not specify | val (out-of-domain, eval-only) |
| YT-RefVOS21 [41] + DAVIS17-RefVOS [43] | V-Ref. | 14.3K | train / val |
| ReVOS [11] | V-Rea. | 18.4K | train / val (Ref./Rea./Overall) |
| MeVISGCG / YT-VOSGCG / VidSTGGCG / HCSTVGCG / VideoGCG [29] | V-GCG | 107.9K | train / val |
| YT-VOS19 [42] | V-Obj. | 13.4K | train / val (Seen/Unseen/All) |
| YT19-VGD + VIPSeg-VGD (newly constructed) | V-VGD | 16.3K | train / val (point/box) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PQ / VPQ | Panoptic quality for image / video panoptic segmentation | yes (V-Gen. headline; reported as VPQ1/2/4/6 and overall VPQ) |
| mIoU | Mean intersection-over-union for semantic segmentation, I-Int., I-GCG | yes (image semantic, GCG headline) |
| mAP / AP / AP50 | Mean average precision for instance, OV instance, and VGD segmentation | yes (V-OV, V-VGD headline) |
| cIoU | Cumulative IoU for referring / reasoning segmentation on images | yes (I-Ref., I-Rea. headline) |
| gIoU | Generalized IoU for referring / reasoning segmentation on images | no (secondary) |
| $\mathcal{J}$ / $\mathcal{F}$ / $\mathcal{J}\&\mathcal{F}$ | Region similarity, contour accuracy, and their average for video referring/reasoning/object segmentation | yes (V-Ref., V-Rea., V-Obj. headline) |
| METEOR / CIDEr | Caption-quality metrics for GCG segmentation | no (secondary) |
| Recall | Phrase-grounding recall for V-GCG | no (secondary) |
| mVC8 / mVC16 | Video consistency over 8/16 frames for VSPW | no (secondary) |
| Accuracy | Image / video chat benchmark accuracy (MME, MMBench, SEED, POPE, AI2D, VideoMME, MVBench, MLVU, LongVideoBench) | no (chat-preservation diagnostic) |
| GPU hours | Wall-clock training cost (used in joint-training ablation) | no (efficiency diagnostic) |

### 6.3 Training and Inference Settings

- **Hardware**: 32 NVIDIA H800 GPUs for main runs; 16 GPUs for ablations (App. D, Table 12).
- **Two-stage training**: (1) agnostic segmentor on SA-1B, mask encoder frozen, only mask decoder trained, $\text{lr} = 1\times 10^{-4}$, effective batch size 128, 1 epoch, max grad norm 0.01. (2) Unified joint training optimizes projectors, LoRA on the LLM ($r=128$, $\alpha=256$), mask encoder, mask decoder, and mask memory; $\text{lr} = 1\times 10^{-5}$ for the mask encoder and $1\times 10^{-4}$ for other modules; max grad norm 1.0; 1 epoch.
- **Batching**: per-device batch size $B=1$; image batch multiplier $4$ vs. video $1$, giving effective global batch size 128 for images and 32 for videos. Modality-specific gradient accumulation (image: every step; video: $\times 4$). Temporal-aware sampler groups clips of equal length.
- **Optimizer**: AdamW [48], $\beta_1 = 0.9$, $\beta_2 = 0.999$, weight decay $0.05$, cosine annealing schedule with warmup ratio $0.03$.
- **Initialization**: vision encoder, vision projector, and LLM from Qwen3-VL-4B [33]; mask encoder from SAM2 [9]; mask decoder from the agnostic segmentor stage.
- **Mask Memory**: capacity $K=8$ for ablations (Table 12), $K=6$ for the final model (App. C, justified by Table 5 ablation).
- **Region Sampler**: parameter-free, mask-encoder features, adaptive-pooling kernel $K=4$ (App. E, Table 15).
- **Dataset balancing**: temperature-resampling with $t = 0.1$ following [22].
- **Loss weights**: $\lambda_{\text{bce}} = \lambda_{\text{dice}} = 5.0$ in $\mathcal{L}_{\text{mask}}$ (Eq. 1); joint objective $\mathcal{L}_{\text{joint}} = \mathcal{L}_{\text{ar}} + \mathcal{L}_{\text{mask}} + \mathcal{L}_{\text{cls}}$ for segmentation, $\mathcal{L}_{\text{ar}}$ alone for chat (Eq. 2).
- **Preprocessing**: consecutive frame sampling, stride $1$, $8$ frames per video segmentation clip; $16$ frames for V-GCG; $64$ frames for video chat into the vision encoder (App. D).
- **Inference**: V-GCG averages over the three V-GLaMM sub-datasets (App. D); other tasks follow standard benchmark protocols. The paper does not specify a separate decoding strategy (e.g., greedy vs. sampling) for the LLM at inference.

### 6.4 Main Results

| Method | I-Ref. RefCOCO/+/g cIoU | I-OV ADE20K PQ/mIoU/mAP | V-Ref. YT21/DV17 $\mathcal{J}\&\mathcal{F}$ | V-Rea. ReVOS All $\mathcal{J}\&\mathcal{F}$ | V-GCG mIoU | V-VGD YT19/VIPSeg AP (Box) | Notes |
|---|---|---|---|---|---|---|---|
| LISA-7B [10] | 74.9 / 65.1 / 67.9 | – | – | – | – | – | image-only generalist |
| GLaMM-7B [28] | 79.5 / 72.6 / 74.2 | – | – | – | – | – | image-only |
| Sa2VA-8B [32] | 81.6 / 76.2 / 78.7 | – | – | – | – | – | image+video, no V-OV/V-Gen reported |
| X-SAM [22] | 85.1 / 78.0 / 83.8 | 20.9 / 28.8 / 16.2 | – | – | – | – | image-only baseline most directly comparable |
| VISA-7B [11] | – | – | 61.5 / 69.4 | 46.9 | – | – | video generalist |
| VideoLISA [12] | – | – | 61.7 / 67.7 | – | – | – | video generalist |
| HyperSeg [31] | – | – | 68.5 / 71.2 | 55.7 | – | – | image+video generalist |
| UniPixel-7B [52] | – | – | 71.0 / 76.4 | 63.7 | – | – | video generalist |
| VideoGLaMM [29] | – | – | 66.8 / – | – | 54.3 | – | video generalist |
| SAM2-H [9] | – | – | – | – | – | 54.0 / 40.4 | non-MLLM specialist |
| **X2SAM (ours)** | **84.0 / 78.4 / 81.9** | **31.2 / 38.2 / 20.2** | **78.5 / 79.0** | **69.9** | **75.8** | **74.4 / 57.8** | unified image+video MLLM, 4B-class backbone |

Headline reading (from Tables 6–9): X2SAM is competitive with X-SAM on image referring (slightly behind on RefCOCO/+, ahead on RefCOCOg val 81.9 vs. 78.0), substantially better on out-of-domain I-OV ADE20K (+10.3 PQ over X-SAM), and clearly leads MLLM-based video generalists on V-Ref. (+7.5 $\mathcal{J}\&\mathcal{F}$ over UniPixel-7B on Ref-YT21), V-Rea. (+6.2 over UniPixel-7B, +14.2 over HyperSeg on ReVOS All), V-GCG (+21.5 mIoU over VideoGLaMM), and V-VGD box (+20.4 AP over SAM2-H on YT-VIS19).

### 6.5 Ablation Studies

- **Mask decoder T2I attention (Table 2)**: removing T2I gives the baseline (I-Ref. RefCOCO 82.9, V-Ref. YT21 53.6 $\mathcal{J}\&\mathcal{F}$, V-Rea. All 36.5). Random-initialized T2I hurts I-Ref. testA (78.0 → 77.2). Zero-initialized T2I improves V-Ref. YT21 by +7.2 (53.6 → 60.8) and V-Rea. All by +10.8 (36.5 → 47.3). **Diagnostic**: directly contrasts random vs. zero init, isolating the integration-stability claim.
- **Joint training strategy (Table 3)**: separate training is the floor; "simple" joint training costs $\sim 5.2$K GPU-hours and reaches 54.4 I-Gen. PQ; the proposed unified strategy uses $3.3$K GPU-hours (–36.5%) while matching/improving image metrics and lifting V-OV mAP from 58.7 to 59.1. **Diagnostic**: answers "is the bespoke modality-aware batching worth it?" with both quality and wall-clock numbers.
- **Mask memory composition (Table 4)**: vs. baseline, "+ Single Scale" alone is roughly neutral (V-Gen. VPQ 42.9 → 42.7), "+ Mask Guide" lifts V-Ref. YT21 from 53.6 to 63.3, "+ Class Guide" further raises V-Rea. All to 51.6, "+ Multi Scale" gives best V-Ref. YT21 65.0 and V-Rea. All 53.5. **Diagnostic**: a clean component-by-component decomposition of the Mask Memory module.
- **Memory size (Table 5)**: K = 1, 2, 4, 6, 8. V-OV peaks at $K=6$ (60.2 mAP), V-Rea. All peaks at $K=6$ (57.5 $\mathcal{J}\&\mathcal{F}$); $K=8$ regresses on V-Ref. (65.0) and V-Rea. (53.5). Justifies the $K=6$ choice for the final model. **Diagnostic**: directly probes whether longer memory is monotonically better; the non-monotonic finding is the kind of negative-result evidence that is informative.
- **Agnostic-segmentor data source (Table 13, App. E)**: COCO vs. SAM-Sub vs. SAM-1B; SAM-1B is best on most splits (e.g., V-Gen. PQ 43.7 → 45.4, V-Rea. All 57.8 → 59.2). **Diagnostic** on data scaling for the warm-up stage.
- **Region sampler (Table 15, App. E)**: mask-encoder features beat vision-encoder features (I-Int. point mIoU 64.7 → 66.2); kernel $K=4$ is the sweet spot vs. $K \in \{2,8,\infty\}$. **Diagnostic**: justifies both the feature source and the pooling kernel.
- **MLLM backbone (Table 14, App. E)**: SigLIP2+Phi3-3.8B vs. SigLIP2+Qwen3-4B vs. Qwen3VL-4B; Qwen3VL-4B is best on most segmentation tracks. **Mostly a sanity check** that backbone choice isn't a confound, rather than a diagnostic of a novel component.
- **What's missing**: there is no ablation that turns off the Mask Memory entirely while keeping T2I (the closest is the "Baseline" row of Table 4, which inherits the simpler decoder), and no ablation isolating the agnostic-segmentor stage from the joint-training stage. The joint-training table (Table 3) compares strategies but not "no joint training at all".

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — Tables 6–9 compare against X-SAM [22], HyperSeg [31], UniPixel-7B [52], Sa2VA-8B [32], VideoGLaMM [29], SAM2-H [9], all current segmentation-MLLM or task-specific SoTA references.
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — the paper evaluates 14 segmentation tasks plus image and video chat across $\geq 20$ datasets including out-of-domain gRefCOCO, ADE20K, and YT-VIS21 (Tables 6–9, 16–21).
- [covered] Has ablations that diagnose the new components (not just sanity checks) — Tables 2, 4, 5, 13, 15 isolate T2I init, Mask Memory components, memory size $K$, agnostic-data scale, and region-sampler design; Table 3 diagnoses the joint-training pipeline. Only Table 14 reads as a backbone sanity check.
- [partial] Has a scaling study (size, length, or compute) — memory-size $K \in \{1,2,4,6,8\}$ (Table 5) is a length-of-context scaling study and joint-training cost is reported (Table 3, $3.3$K vs. $5.2$K GPU-hours), but there is no model-size scaling (only one 4B backbone is the final model) and no video-length / clip-length scaling beyond memory $K$.
- [partial] Has an efficiency / wall-clock comparison — Table 3 reports training GPU-hours for the joint-training variants, but inference latency / FPS / parameter count vs. baselines is not reported.
- [missing] Reports variance / standard deviation / multiple seeds where relevant — all numbers are single-run point estimates; the paper does not specify seed counts or report std.
- [partial] Releases code / weights / data sufficient for reproducibility — code link `https://github.com/wanghao9610/X2SAM` and a project page are advertised on page 1, and the new V-VGD construction pipeline is described in App. B; the paper does not specify whether trained weights are released, and the V-VGD splits depend on YT-VIS19 and VIPSeg licenses.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 一個統一 MLLM 同時處理 image 與 video 的 7+7 個分割任務** — Supported。Table 1（p.4）支援廣度第一，Tables 6–9 與 17–19 跨 14 任務皆有數字，介面確實未針對任務切分模型。
- **C2: Mask Memory 提升時序一致性** — Supported。Table 4（p.8）顯示加上 mask guide 後 V-Ref YT21 53.6→63.3 J&F、V-Rea 36.5→51.1 J&F；Table 5 進一步顯示 memory size 對長時序任務有正向斜率，至 $K=6$ 飽和。
- **C3: V-VGD 是新基準** — Supported as a new task formulation；Appendix B（p.13–14）給出 YT19-VGD、VIPSeg-VGD 的構造方式並在 Table 9 提供結果，但因 prompt 採「first visible frame 自動生成」，benchmark 的難度設定屬於內部選擇而非社群已驗證的協定。
- **C4: Unified joint training 降低成本而不損品質** — Partially supported。Table 3 顯示 5.2K→3.3K GPU-hours，但「simple joint」與「unified」的差別未在正文以演算法層級展開（dimension-shifting、modality-aware batching、temporal-aware sampler 是混合在一起的描述），36.5% 的歸因因此無法獨立切分。
- **C5: 擴展到 video 不犧牲 image 能力** — Overclaimed。對比 X-SAM 的 Table 6 顯示 I-Gen、I-Ref、I-GCG、I-VGD 多項指標都有 1–2.3 點下滑，論文以「remains competitive」帶過；I-OV 確實大幅進步（20.9→31.2 PQ），但這個提升很可能來自 Qwen3-VL backbone 升級而非 X2SAM 架構本身（Table 14 中 Qwen3VL-4B 對 Siglip2 baseline 已在 I-OV 領先）。

### 7.2 Fundamental Limitations of the Method

**Fixed-size FIFO 無法承載長片段語意。** Mask Memory 是一個 $K$ frame 的 FIFO，當目標被遮擋超過 $K$ frame 後，引導特徵會被擠出 bank，模型只能依賴當下幀重新 grounding。Table 5 顯示 $K$ 從 1 到 6 才有單調收益，到 8 反而下滑，這是 FIFO 容量與雜訊兩端互相拉扯的結構性結果，加大 $K$ 不會解決問題。要根除需要替換 FIFO 為可選 keyframe 機制，但這會破壞作者在 §3.3 unified joint training 的 modality-aware batching 設計。

**Memory 只存「decode 後特徵」，錯誤會自我強化。** Memory Encoder 將當前幀的 mask logits 與下採樣 vision feature 一起寫入 bank（Figure 4c）。一旦某幀出現 identity switch 或 mask drift，錯誤的 logits 會被當成 ground truth-like 條件寫入 memory，並在 Memory Attention 中被後續幀檢索。論文未提供任何 confidence gating 或 re-grounding 機制，因此架構本身對「錯誤累積」沒有抵抗力，這也呼應作者承認的「prolonged occlusion」失敗模式，但根因不在 memory 大小，而在於缺乏校正回路。

**語言條件只在當下幀注入。** `<SEG>` token 的 latent embedding $Z_p$ 是由當前對話輪生成的，Memory Bank 內儲存的 guided feature 雖然「曾被語言引導」，但 Memory Attention 階段並未再次以最新文字條件對歷史特徵做 re-projection。這使得「指令在 frame 1 給出，目標在 frame 30 才出現」的場景無法獲得真正的長程語言錨定，論文的 V-Rea 高分主要來自 ReVOS 這類短片段測試（§4.1, p.7），不能延伸到長片段。

**Joint training 的平衡靠手工常數。** §3.3 與 Table 12 顯示 image batch multiplier=4、video accumulation=4、image batch=128、video batch=32、resampling temperature $t=0.1$、$\lambda_{bce}=\lambda_{dice}=5.0$ 等都是固定常數。當資料集組合改變（加入新任務或縮放某一語料），整套配方必須重新試誤；論文沒有提供任何自動化或 loss-aware 的調節機制，因此「unified joint training」更像一份具體的訓練配方而非可遷移的方法論。

### 7.3 Citations Worth Tracking

- **X-SAM (Wang et al., 2025)** — 直接的前身與最強的 image baseline；理解 X2SAM 必須先掌握 X-SAM 的 mask decoder 架構與 mixed fine-tuning 配方，且大多數 image 指標的對照都針對它。
- **SAM2 (Ravi et al., 2024)** — Mask Memory 設計直接借自 SAM2 的 memory bank / memory attention，差別只在「儲存的 feature 是否被 LLM 引導」；對照 SAM2 原始設計可以判斷 X2SAM 的增量貢獻。
- **VideoGLaMM (Munasinghe et al., 2024)** — V-GCG 基準與資料來源，且 Table 18 的 +21.5 mIoU 數字依賴於對 VideoGLaMM 的重新評估；原文細節對解讀此對比至關重要。
- **HyperSeg (Wei et al., 2024)** — 唯一同時宣稱跨 image+video 的競爭 generalist，是 V-Rea / V-Ref 的主要對照組，理解其架構差異有助於判斷 Mask Memory 的真正貢獻。
- **LISA (Lai et al., 2023)** — `<SEG>` token 範式的起點；X2SAM 的 token-conditioned mask decoder 沿用此抽象，回頭讀 LISA 對於理解後續 `<p>...</p>` 條件擴展與 zero-init T2I attention 動機很關鍵。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 一個共享同一個 Qwen3-VL backbone、認真調教的 X-SAM+SAM2 cascade（即 image 端用 X-SAM 解第一幀、SAM2 用 X-SAM 的 mask 作 prompt 做時序傳播）在 V-Rea / V-Ref 上會落後 X2SAM 多少？論文 §2 反例假設依賴此對照但實驗未提供。
- [ ] 為什麼 I-GCG mIoU 由 X-SAM 的 69.4 退步到 67.1、I-VGD point AP 由 47.9 退步到 45.9（Table 6, 9）？是 video co-training 排擠、還是 LoRA rank/alpha 設定差異所致？
- [ ] Memory size 的最終設定到底是 $K=6$（§4.3 結語）還是 $K=8$（Table 12 主訓練 hyperparameter），主表 Table 6 採用哪一個？兩者的差距會否改變對 HyperSeg / UniPixel 的勝負判定？
- [ ] V-GCG 的 Video-GLaMM「re-evaluated」結果為 54.3 mIoU 而原報告為 62.3 mIoU（Table 18），兩者差 8 點的具體原因（資料子集、評估腳本、metric 實作）是什麼？
- [ ] 在「目標被遮擋超過 $K$ frame」、「同類多目標糾纏」、「目標離場再回場」這三種 author 自己點名的長尾情境上，Mask Memory 的失效率是多少？論文沒有 stress test。
- [ ] 1 epoch、單次跑的訓練配置下，主表的勝負是否在 seed variance 之內？所有 ±1 點等級的提升是否能複現？
- [ ] V-VGD 自動 prompt 取自第一個可見 frame，若改為隨機可見 frame 或人類標註的 prompt，YT-VIS19 box AP 74.4 會掉多少？

### 8.2 Improvement Directions

1. **加入 confidence-gated memory write。** 在 Memory Encoder 寫入 bank 之前，依當前幀 mask 的 entropy 或 IoU-with-prediction 設一個門檻，避免低品質幀污染後續檢索。基礎邏輯：FIFO 目前無條件覆寫，作者也承認 prolonged occlusion 失敗，這正是錯誤被無條件寫入記憶的症狀。可行性高，僅需在 Figure 4c 後加一層 gating。
2. **Hybrid memory：FIFO + keyframe slot。** 保留 $K$ frame 的短期 FIFO，再額外維護 1–2 個由置信度或語意相似度選出的長期 keyframe slot。Table 5 顯示 $K$ 增至 8 開始引入雜訊，問題在於均勻 FIFO 把近期與重要幀同等對待，分離兩種記憶可同時擴大時間視野與抑制雜訊。
3. **每隔 $N$ frame 重新注入語言條件。** 將 `<SEG>` token 的 $Z_p$ 重新計算並透過 cross-attention 對 memory bank 做 re-projection，使長片段不只靠視覺特徵延續 grounding。此舉直接針對 §7.2 第三點（語言只在當下幀注入）的結構限制。
4. **加入真正的 X-SAM+SAM2 cascade baseline。** 用同一個 Qwen3-VL backbone 與 X-SAM 解碼器，搭配 stock SAM2 propagation，跑 V-Ref / V-Rea / V-VGD 三個任務作為對照實驗。這是 §2 反例假設的直接驗證，缺它則 C1/C2 的「joint coupling 必要性」結論無法成立；可行性取決於是否願意重訓 X-SAM 一份 Qwen3-VL 版本。
5. **報告 seed variance 與多 epoch 趨勢。** 至少 3 seed × 1 epoch、或 1 seed × 多 epoch 的對照，讓 ±1 點級別的勝負有統計依據。技術門檻低，僅是計算成本問題，但對所有 generalist 比較表的可信度提升明顯。
6. **V-VGD prompt 多樣化。** 訓練與評估皆採「隨機 frame 取 prompt」與「人類標註 prompt」的設定，避免「第一可見 frame」造成的協定依賴。這會把 V-VGD 從 in-distribution 對比轉為更接近真實使用情境的測試，且不需改架構。
