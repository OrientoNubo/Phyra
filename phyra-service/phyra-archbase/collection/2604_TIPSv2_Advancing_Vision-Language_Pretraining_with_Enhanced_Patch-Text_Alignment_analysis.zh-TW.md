<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# TIPSv2 — TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | TIPSv2 |
| Paper full title | TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment |
| arXiv ID | 2604.12012 |
| Release date | 2026-04-13 |
| Conference/Journal | arXiv preprint (CVPR'26) |
| Paper link (abs) | https://arxiv.org/abs/2604.12012 |
| PDF link | https://arxiv.org/pdf/2604.12012 |
| Code link | https://github.com/google-deepmind/tips |
| Project page | https://gdm-tipsv2.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Bingyi Cao | Google DeepMind | https://scholar.google.com/citations?user=7EeSOcgAAAAJ&hl=en | first author, co-corresponding |
| Koert Chen | Google DeepMind | — | co-first author, co-corresponding |
| Kevis-Kokitsi Maninis | Google DeepMind | — | author |
| Kaifeng Chen | Google DeepMind (now at xAI) | — | author |
| Arjun Karpur | Google DeepMind (now at Epsilon Health) | — | author |
| Ye Xia | Google DeepMind | — | author |
| Sahil Dua | Google DeepMind | — | author |
| Tanmaya Dabral | Google DeepMind | — | author |
| Guangxing Han | Google DeepMind | — | author |
| Bohyung Han | Google DeepMind (now at Seoul National University) | — | author |
| Joshua Ainslie | Google DeepMind | — | author |
| Alex Bewley | Google DeepMind | — | author |
| Mithun Jacob | Google DeepMind | — | author |
| René Wagner | Google DeepMind | — | author |
| Washington Ramos | Google DeepMind (now at Google) | — | author |
| Krzysztof Choromanski | Google DeepMind | — | author |
| Mojtaba Seyedhosseini | Google DeepMind | — | author |
| Howard Zhou | Google DeepMind | — | author |
| André Araujo | Google DeepMind | https://andrefaraujo.github.io/ | senior author, co-corresponding |

### 1.2 Keywords

vision-language pretraining, patch-text alignment, masked image modeling, self-distillation, iBOT++, zero-shot segmentation, EMA teacher, synthetic captions

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| TIPS [33] | predecessor | First TIPS version that combines contrastive image-text learning with self-supervised losses; TIPSv2 directly extends it. |
| iBOT [68] | base model | Masked image modeling SSL objective that iBOT++ modifies by also supervising visible tokens. |
| DINO [5] / DINOv2 [38] / DINOv3 [45] | influence | Self-distillation SSL family providing the student-teacher EMA framework adapted by TIPSv2. |
| CLIP [40] | baseline | Original contrastive image-text pretraining paradigm; provides the $L_{\text{CLIP}}$ component. |
| SigLIP [64] / SigLIP2 [50] | baseline | Sigmoid-based contrastive vision-language encoders compared against; SigLIP2 also unifies SSL+contrastive. |
| Perception Encoder (PE) [4] | baseline | Recent vision-language encoder noted for global contrastive "decoder" behaviour and weak local semantics. |
| PaliGemma [3] | influence | Source of synthetic dense captions used for multi-granularity caption supervision. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於視覺-語言預訓練 (vision-language pretraining) 中 patch-level 表徵與文字嵌入之對齊問題,亦即如何讓 ViT 各個 patch token 能精準對應到語意層級的文字概念,以支撐 open-vocabulary segmentation、zero-shot dense prediction 等需要密集語意理解的下游任務。作者觀察到即便是 TIPS、SigLIP2 等同時整合 SSL 與 image-text contrastive 的最新模型,patch-text alignment 仍明顯不足,且大型 flagship 模型在此能力上反而落後其蒸餾出的小型學生模型。為此,作者在 TIPS 既有架構之上提出 TIPSv2,引入 iBOT++ 之新型遮罩影像建模 (MIM) 損失、head-only EMA 之輕量化自蒸餾機制,以及多粒度合成標題 (multi-granularity captions) 之文字監督策略,目標是在不犧牲全域影像-文字對齊的前提下,大幅提升 patch 層級的語意定位能力。

### 2.2 Domain Tags

- computer vision
- vision-language pretraining
- self-supervised learning
- representation learning

### 2.3 Core Architectures Used

- **Vision Transformer (ViT)** [13]:作為影像編碼器 $f$,負責將影像切成 patch token 並輸出 global embedding $e_g$ 與 patch embeddings $\{e_1, \dots, e_N\}$;TIPSv2 訓練 ViT-g (1.1B 參數) 並蒸餾至 ViT-SO/L/B 系列。
- **Standard Transformer text encoder** [53]:作為文字編碼器 $g$,將 caption 映射到文字嵌入 $e_t$,供 $L_{\text{CLIP}}$ 對齊使用。
- **iBOT++ (本文提出)**:在 iBOT [68] MIM 目標之上推廣 patch-level loss 至所有 token (包含 visible 與 masked),強制學生於每個 patch 都對齊老師表徵,如 Eq. (3) 所示。
- **Head-only EMA (本文提出)**:取消對整個 backbone 做 EMA,僅對 projection head $h_t$ 套用 EMA 更新且共享 encoder ($f_t = f_s$),藉 $L_{\text{CLIP}}$ 防止 collapse,於 ViT-B 上節省約 42% 訓練參數。
- **DINO global self-distillation head** [5]:沿用 TIPS 配方,以 $L_{\text{DINO}}$ 在 global embedding 上進行跨 crop 的自蒸餾。
- **CLIP-style image-text contrastive head** [40]:以 InfoNCE 形式的 $L_{\text{CLIP}}$ 對齊影像與文字模態,並沿用 TIPS 之雙 CLS 設計 (一者監督 web alt-text,另一者監督合成標題)。
- **PaliGemma + Gemini Flash captioner** [3, 22]:作為多粒度合成標題的來源,於訓練中以 PaliGemma 的精簡標題與 Gemini 的詳盡標題交替監督第二個 CLS token。

### 2.4 Core Argument

作者主張現行視覺-語言預訓練模型 patch-text alignment 不佳的根因,在於 iBOT 一類 MIM 目標僅對 masked tokens 施加 patch-level 損失,讓 visible tokens 的表徵可以「任意漂移」,只要足以重建被遮罩 token 即可,因此無法錨定到老師模型的語意空間。透過一組精心設計的蒸餾消融實驗 (Tab. 2),他們發現:(1) 將 masking ratio 降到 0、亦即在所有 token 上施加 patch-level 蒸餾損失,zero-shot segmentation 大幅躍升;(2) 學生視覺編碼器必須採隨機初始化,若以預訓練權重初始化則會被舊收斂區域困住,蒸餾增益完全消失。這兩點共同指出:patch-text alignment 是「對所有 patch 強制與老師對齊」這個監督訊號帶出來的,而非單純由更大模型或更多資料解決。基於此,作者邏輯上必然導出 iBOT++:保留 iBOT 的遮罩機制以維持全域重建能力,但同時把 patch-level 損失推廣到 visible tokens,讓學生在每一個 token 上都被錨到老師表徵。輔以 head-only EMA (因為 contrastive loss 已防止 encoder collapse,毋須對整個 backbone 做 EMA) 與多粒度標題 (web alt-text + PaliGemma + Gemini) 的文字監督,組成一個資源效率與密集對齊兼具的預訓練配方,使 TIPSv2 在 zero-shot segmentation 上達到 SOTA,並在 9 項任務、20 個資料集上維持與更大模型相當或更佳之全域表現。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(270 words)

標題 *TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment* 直接點出兩個關鍵詞：作為 TIPS 的後繼版本，以及核心改進是 patch-text alignment。Abstract 的敘事走的是「問題-觀察-方法-結果」四步結構，每一步都緊扣 patch-level 對齊這條主線。

第一步先建立問題：近期 vision-language 預訓練雖在 classification、retrieval、segmentation、depth 等下游任務取得進展，但模型仍難以把 dense patch representations 與對應概念的 text embeddings 對齊。這把讀者的注意力聚焦到「dense」這個維度，而不是已被廣泛驗證的 image-level 對齊。

第二步丟出反直覺觀察：作者發現一個 patch-level distillation 程序能顯著提升 patch-text alignment，且學生模型的對齊品質竟然超越教師模型。這個現象本身就是論文最賣點的 hook，它同時指向「現行 pretraining recipe 漏掉了什麼」這個問題。

第三步把觀察轉化為方法：受該現象啟發，作者提出 iBOT++,把 unmasked tokens 也納入 loss，從而把 distillation 階段的 trick 提前注入 pretraining；此外搭配 EMA 簡化策略以及 multi-granularity caption sampling 兩項輔助改進，組成完整的 TIPSv2 訓練 recipe。

第四步給出實驗承諾：在 9 個任務、20 個資料集上全面驗證，整體與最新 vision encoder 持平或更優，並開源 code 與 model。Abstract 透過這條敘事鏈，把「發現 → 方法 → 驗證」串成一條因果線，為後續 Introduction 的展開預留三個鉤子：為何小模型反而對齊更好、iBOT++ 與既有 MIM 變體的差異、以及 head-only EMA 的合理性。

### 3.2 Introduction

(660 words)

Introduction 採用「分歧-觀察-提案」三段式。第一段建立領域版圖：作者指出當前 large-scale pretraining 主要分為兩條路線。其一是 weakly-supervised contrastive/sigmoid 方法（CLIP、SigLIP、Perception Encoder），擅長 image-text alignment 與 zero-shot；其二是 self-supervised learning（DINO、iBOT），擅長 spatial 理解與 dense 任務。這個對比是論文的問題框架：兩條路線各有所長，但要同時兼顧 global 與 dense 仍是 open challenge。

第二段把分歧推到具體模型層面：DINOv2 強於 dense 任務但缺 text alignment；PE-core 提供穩固 image-text alignment 但 dense 表現不足；近期試圖統一的 TIPS、SigLIP2 仍難以維持 pixel/patch 級的精細對齊；DINO.txt、DINOv3 透過附加 text encoder 補救但多模態表現有限。作者引用 PE 的觀察作為支撐：final transformer layers 常退化成 global contrastive 「decoder」,丟失 local semantics。

第三段是論文最核心的轉折：作者揭示一個反直覺的趨勢，TIPS、SigLIP2 等 SOTA encoder 中,旗艦級大模型在 patch-text alignment 上反而輸給較小的學生模型。這個現象本身就指向 distillation 過程帶入了某些 pretraining 缺失的監督。透過對近期 spatially-aware 多模態 encoder 的研究,他們發現 distillation 之所以能改善 grounding alignment,是因為對「所有 patch tokens」都施加了有效監督。這個 insight 同時解釋了現象,也鋪好了方法層面的動機。

第四段正式登場 TIPSv2：作為 TIPS 的第二代,它把 distillation 的發現翻譯回 pretraining,核心是 iBOT++ —— 一個對 visible tokens 也施加 representation consistency 的 self-supervised 目標(對應 Fig. 1)。輔助元件有兩個：multi-granularity text augmentation（結合 PaliGemma 與 Gemini 的合成 caption）以及 resource-efficient 的 EMA 策略;標準 SSL 通常需要 full-model EMA,但因為加入了 text supervision,作者主張只對 projection head 做 EMA,顯著降低訓練時記憶體需求。

最後段給出三項 contribution：(1) 揭示 distillation 強化 spatial 感知能解鎖 patch-text alignment 的現象,並透過 ablation 鎖定 masking removal 與 initialization 是關鍵驅動因素;(2) iBOT++ 這個 masked objective;(3) 高效訓練 recipe（multi-granularity captions + head-only EMA）,在 9 任務 20 資料集上全面驗證。這三點分別預告 §3.2、§3.3、§3.4–3.5 的章節展開,為後續方法論留下清晰指引。

### 3.3 Related Work / Preliminaries

(990 words)

本節由 Section 2（Related Work）與 Section 3.1（Preliminaries）兩段共同組成,分工清楚：前者畫出領域座標,後者建立記號與 baseline。

Related Work 把 versatile image representation 的大規模 pretraining 歸納成三大典範：self-supervised visual learning、image-text contrastive learning、image captioning。論文明確表態自己建構在前兩者之上,目標是同時具備 native text-aligned 與 spatially aware 的視覺表徵。

在 SSL 段落,作者依序回顧 DINO 與 iBOT 的 student-teacher distillation + EMA 設計、DINOv2 的 well-tuned recipe、以及 DINOv3、WebSSL 把 recipe 擴展到 7B 參數、2B curated images 的大規模實驗。接著把自己的兩項貢獻定位於此脈絡：第一是把 iBOT 的 MIM 擴展為 iBOT++,允許同時對 visible 與 masked tokens 監督。作者刻意對比類似工作以凸顯差異：DMAE 預測 visible 與 masked patches（不是 tokens）、SimMIM 嘗試但未成功、MaskAlign 與 MR-MAE 是把 visible tokens 對齊到「另一個 frozen 的 pretrained 模型」,因此 MIM 中同時監督 visible 與 masked tokens 是過往未被探索的設計。第二是 EMA 簡化,只對 projection head 做 EMA,訓練參數量幾乎砍半。作者強調 SILC、TIPS、SigLIP2 雖也結合 SSL 與 contrastive,但都沒簡化 EMA 元件。

Contrastive vision-language pretraining 段落從 CLIP、ALIGN 起點,列出 OpenCLIP、SigLIP、PE、EVA、MetaCLIP 等近期實作,並提到合成 caption 的應用。TIPSv2 的差異在於同時結合 noisy web caption 與不同粒度的合成 caption,提供更廣的描述光譜。Knowledge distillation 段落則指出蒸餾常用於壓縮 vision-language encoder,而本文首次展示 distillation 在 spatially aware 設定下能反向強化 patch-text alignment,即使 teacher 本身對齊不佳。

Preliminaries（§3.1）把後續所有方法符號定義一次到位。給定 image-text pair 集合 $\{(I_k, T_k)\}$,image encoder $f$ 把 $I$ 對應到 $\{e_g, e_1, e_2, \ldots, e_N\}$,text encoder $g$ 把 $T$ 對應到 $e_t$;$f^g(I) = e_g$ 是 global embedding,$f(I) = \{e_1, \ldots, e_N\}$ 是 patch embeddings;$f$ 為 ViT,$g$ 為標準 transformer。總損失為 $L = L_{CLIP} + L_{DINO} + L_{iBOT}$。

接著拆解三項 loss。$L_{CLIP}$ 採 InfoNCE,把對應 $(e_g, e_t)$ 拉近、不對應拉遠;TIPS 的特色是使用兩個 CLS：一個對齊 web alt-text 抓 object-centric 細節,另一個對齊 PaliGemma synthetic caption 抓 dense spatial 關係。$L_{DINO}$ 是 global self-distillation：

$$L_{DINO} = -\sum_{i=1}^{M} h_t(f_t^g(I))^T \log h_s(f_s^g(I_i))$$

其中 $\{I_i\}_{i=1}^{M}$ 是 $M$ 個 local crops。$L_{iBOT}$ 是 patch-level MIM：

$$L_{iBOT} = -\sum_{i=1}^{N} m_i\, h_t(f_t(I)_i)^T \log h_s(f_s(I_{mask})_i)$$

其中 $m_i = 1$ 標示第 $i$ 個 patch 被遮蔽,因此 loss 只作用於 masked tokens。最後段補充 distillation 設定：teacher $f_t$ 從 EMA 改為 frozen 的較大模型,且 patch-level loss 不再施加 mask。這個微小差異正是論文後續放大解析的切入點,把 §3.1 與 §3.2 緊密接續。

### 3.4 Method (overview narrative)

(1660 words)

方法章節（§3.2–3.5）採「先解謎、再立論、再優化」的敘事結構,把整個 TIPSv2 recipe 拆成四個彼此承接的子問題。

§3.2 Bridging Pretraining and Distillation 是整篇論文的解謎段落。作者先用 Tab. 1 證明異象：TIPS ViT-L 學生在 zero-shot segmentation 全面壓制 ViT-g 教師（PC59 33.5 vs 11.4、ADE150 20.8 vs 2.6）,徹底反轉 [33] 中其他任務的趨勢。這暗示 pretraining recipe 在 ViT-g scale 對 image-only/global 任務有效,卻未能誘導出 patch-text alignment,而這個能力是在 distillation 階段才補上的。

為了拆解 distillation 與 pretraining 的差異,Tab. 2 用 ViT-L self-distillation baseline 做受控 ablation,系統性掃過 masking ratio 與初始化/凍結策略。三個關鍵發現浮現：(1) Masking ratio 從 0.75 降到 0.0,zero-shot mIoU 從個位數一路衝到 30+,證明對 visible tokens 施加 loss 是核心因素；(2) text encoder 對初始化不敏感；(3) student 視覺 encoder 必須隨機初始化,若用 pretrained 權重初始化會塌回原本的弱對齊區域,完全抵銷 distillation 的好處。作者把這個現象詮釋為「模型必須跳脫 pretrained convergence region 才能重新學習」。這節以「supervising all patch tokens 是 alignment 關鍵」收束,為下一節提供直接動機。

§3.3 iBOT++ 是把 §3.2 觀察翻譯成 pretraining 目標。作者修改 iBOT 的 $L_{iBOT}$,把求和項中的 $m_i$ 移除,得到

$$L_{iBOT++} = -\sum_{i=1}^{N} h_t(f_t(I)_i)^T \log h_s(f_s(I_{mask})_i)$$

讓 loss 同時作用於 masked 與 visible tokens。設計直覺是：原本的 iBOT 缺乏對 visible tokens 的直接監督,只要它們夠用來重建 masked tokens 就行,因此 visible representations 可以「行為任意」;iBOT++ 透過把 visible tokens 也錨定到 teacher,強迫 student 同時保留 local semantics 與 global context。Fig. 2 用 patch-level loss 的下降曲線證明 visible token 的表徵在 iBOT 中停滯、在 iBOT++ 中持續被錨定。Tab. 3 顯示 ViT-g 的 zero-shot segmentation 從 14.2/13.4/29.1/3.5 大幅躍升到 28.6/26.2/37.2/17.6。值得注意的是,作者在 §A.2 補充 ablation 後仍維持 75% masking ratio,說明 iBOT++ 是介於完全 masking 與完全無 masking 之間的折衷,並非「removing mask」的簡化版。

§3.4 Head-only EMA 是訓練效率優化。作者先回顧標準 self-distillation 為什麼需要 EMA：在純 SSL 場景中,EMA + stop gradient 是避免 student/teacher 表徵全部塌縮成常數的關鍵。但在 SSL + image-text contrastive 的混合場景下,$L_{CLIP}$ 已經對 $f_s, f_t$ 提供穩定的反塌縮信號,因此不需要對整個 vision encoder 做 EMA。具體做法是 $f_t = f_s$（共享 encoder）,只對 head $h_t$ 維持 EMA 更新。作者強調這個設計是必要的中間態：完全移除 EMA（連 head 都共享）會造成嚴重訓練不穩,在初步實驗中已被排除。這個簡化在 ViT-B 上削減 42% 訓練參數,顯著降低 memory overhead 與 training throughput,後續 ablation（Tab. 4）顯示效能不僅不退,部分任務還小幅提升。

§3.5 Multi-Granularity Text Captions 是資料層面的優化。作者用 Fig. 4 三組對比凸顯既有 caption 的不足：panda 的姿態（dangling legs）、illustration 的卡通屬性、車輛場景的秋季語境,都被 alt-text 與 PaliGemma caption 漏掉。解法是用 Gemini Flash 條件於 image、alt-text、PaliGemma caption 生成更詳盡的 caption。但作者觀察到一個反直覺現象：完全使用 Gemini caption 反而效果變差,因為過度詳細的描述會讓 batch 內 contrastive 任務變得過於容易,弱化表徵學習。最終策略是隨機 alternate Gemini 與 PaliGemma caption 來監督第二個 CLS token,在學習難度與細節抽取間取得平衡。

整個方法章節透過 Fig. 3 的整合圖收束,把 iBOT++、Head-only EMA、Multi-granularity Captions 三項改動清楚標示為三個綠框,接到 TIPS 既有架構的對應位置,為實驗章節的累積式 ablation 預先鋪好對照表結構。

### 3.5 Experiments (overview narrative)

(1480 words)

實驗章節（§4）以「先設置、再 ablation、再對比」的標準三段論展開,但每一段都明顯回扣方法章節的承諾。

§4.1 Experimental Setup 把評估範圍鋪到 9 個任務、20 個資料集,並嚴格遵循 [33] 的 protocol 以確保公平比較。所有評估都凍結 pretrained image-text representation,呼應論文「off-the-shelf 通用視覺 encoder」的定位。任務被切成 image-text 與 image-only 兩大類。Image-text 又再分 dense 與 global：dense 用 zero-shot segmentation 在 ADE150、PC59、PC60、VOC21 上評估,作者特別說明 TIPSv2 用最簡 cosine similarity 協議（patch features 上採後與 class name text feature 比對）,而 DINOv2（dino.txt）與 SILC 採用較貴的 TCL sliding window protocol —— 這個差異在後續比較中是關鍵框架;global 任務涵蓋 Flickr30K、DOCCI、COCO 的雙向 retrieval 與 ImageNet-1K zero-shot。Image-only 包含 PASCAL/ADE20k 的 linear-probe segmentation、NYUv2/NAVI 的 monocular depth 與 surface normal、ImageNet KNN 與 linear、UnED 上 8 個 domain 的 fine-grained retrieval。Training data 沿用 [33] 的 116M WebLI 子集,新增 Gemini 1.5 Flash 合成 caption。實作細節揭露兩階段訓練：低解析度 90k 步 batch 8192,高解析度 9k 步 batch 4096,ViT-g scale 在 512 顆 TPUv5 上訓練 2 天,並蒸餾出 SO、L、B 學生家族。

§4.2 Ablations 採累積式設計（Tab. 4）,從 reproduced TIPS ViT-g 開始,依序疊上 iBOT++、Multi-granularity Captions、Head-only EMA。最戲劇性的數字是 zero-shot segmentation ADE150 從 baseline 3.5 經 iBOT++ 跳到 17.6（+14.1 mIoU）,直接驗證方法章節的核心主張。Multi-granularity caption 進一步把 retrieval 與 segmentation 同步推高,Head-only EMA 在達成資源節省的同時部分指標仍微幅成長,證明這個簡化「不只是省錢」。

§4.3 Comparisons with Other Vision Encoders 是對外戰場。Fig. 5 以 PCA 圖質性展示 TIPSv2 patch embedding 的空間連貫性勝過 TIPS、SigLIP2,為下方數字結果定錨。Tab. 5 展示 dense image-text：TIPSv2 ViT-L 在四個 zero-shot segmentation benchmark 全部勝出,即使 SILC、DINOv2 採更貴的 TCL protocol 仍輸給 TIPSv2 簡單協議,這是論文最具說服力的單一結果。Tab. 6 的 global image-text：TIPSv2 在 7 項中拿下 5 項最佳或次佳,COCO 與 long-text DOCCI 全面領先;特別是 ViT-g 在 3 項上贏過 PE ViT-G,而 PE 的參數量多 56%、訓練 image-text pair 數量是 47 倍。Tab. 7 的 image-only：9 項中 7 項最佳/次佳,dense 任務尤其強（PASCAL +1.5、NYUv2 depth -0.019）;唯一相對弱的是 ImageNet classification,作者承認這是為了通用性付出的取捨。

Tab. 8 的 DINOv3 對比是收尾段落：選 ViT-L 為共同最大尺寸,且使用 DINOv3 的 TCL protocol 確保比較公平。在 6 項中 TIPSv2 拿下 4 項最佳,儘管 DINOv3 teacher 用了 6 倍參數、15 倍 image。Fig. 6 的 zero-shot segmentation 視覺化收束整節,展示「無任何後處理」的純 patch-text alignment 能力。整個實驗章節透過這條從 setup → ablation → 多面向 comparison → DINOv3 終戰的敘事鏈,把方法章節提出的三項改動逐一兌現,並把 TIPSv2 定位為「在資源較少前提下與 DINOv3 量級對手互有勝負」的通用 vision-language encoder。

### 3.6 Conclusion / Limitations / Future Work

(150 words)

Conclusion 段落極短,功能上是把整篇論文壓縮回三句話的 elevator pitch,並把所有貢獻重新對齊回 abstract 的承諾。作者開篇即定位 TIPSv2 為適用於多元多模態應用的新 vision-language encoder,接著重述問題切入點：透過調查既有模型 dense image-text alignment 的弱點,作者發現 patch-level distillation 顯著強化此能力。這個觀察直接催生 iBOT++,作為 iBOT MIM 的升級,顯著提升 dense image-text alignment。第三句總結兩項輔助改進：簡化 EMA setup 提升 vision-language pretraining 效率,以及多粒度 image caption 提升表徵穩健性。最後以 9 任務 20 資料集的全面驗證,以及「持平或超越過往 vision-language encoder」的整體結論收束。

值得注意的是,正文 Conclusion 並未明確列出 limitations 或 future work,例如 ImageNet classification 相對較弱、與 DINOv3 規模差距、或將 iBOT++ 推到更大資料/模型尺度的潛在方向。論文也未討論 multi-granularity caption 對下游 hallucination 風險的影響。這些議題僅散落於 §A.1（iBOT++ 對 CLIP 的泛化性驗證）與 §A.8（head-to-head 勝率統計）等附錄段落,顯示作者把擴展性留給後續工作,而把主結論集中在「方法簡單、效果一致、資源更省」這條核心訊息。

## 4. Critical Profile

### 4.1 Highlights

- 揭露反直覺現象:在 zero-shot segmentation 上,TIPS ViT-L (student) 的 PC59 mIoU 為 33.5,顯著超越其 ViT-g teacher 的 11.4(Tab. 1, p. 3)。
- Tab. 2 透過系統性消融鎖定兩個關鍵因子:masking ratio 由 0.75 → 0 使 PC59 從 16.0 提升到 31.4(rows 2→4),且 student vision encoder 必須隨機初始化,以 pretrained 初始化(row 7)會把增益完全抹除回 6.4(p. 4)。
- iBOT++ 僅是對 iBOT 的單行修改(Eq. 3 將 mask indicator $m_i$ 移除),即可在 TIPS ViT-g pretraining 上把 PC59 由 14.2 拉到 28.6、ADE150 由 3.5 拉到 17.6(Tab. 3, p. 5)。
- 累積消融(Tab. 4)顯示完整 TIPSv2 把 ADE150 zero-shot segmentation 從 3.5 提升至 19.1 mIoU,同時 Flickr I→T retrieval 由 92.0 升至 95.4。
- Head-only EMA 在 ViT-B 上削減 42% 的 trainable parameters,且 Tab. 4 顯示效能可保持(Sec. 3.4, p. 5)。
- TIPSv2 L/14 在 dense image-text 任務上設立 SOTA,例如 VOC21 由前一代最佳 30.5 (TIPS L/14) 拉到 44.4(Tab. 5, p. 7)。
- TIPSv2 g/14 在 5 項 global image-text 評估中有 3 項勝過 PE-core G/14,儘管 PE 多 56% 參數且看了 47× image-text pairs(Sec. 4.3, Tab. 6, p. 7)。
- iBOT++ 可外推至其他架構:套到 CLIP ViT-g + 2 CLS 後,PC60 zero-shot segmentation 由 18.2 提升到 28.2 mIoU(Tab. 11, appendix)。
- 在 ViT-L 同尺寸下,TIPSv2 L/14 在 6 項評估中於 4 項勝過 DINOv3 L/16(包含 COCO I→T retrieval 73.5 vs 63.7),儘管 DINOv3 teacher 用了 6× 參數與 15× 影像(Tab. 8, p. 8)。
- 訓練成本相對節制:ViT-g 規模僅在 512 TPUv5 chips 上跑 2 天即完成 pretraining(Sec. 4.1, p. 6)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- ImageNet classification 表現未領先:作者在 Sec. 4.3 (p. 8) 自承 "our models do not perform as well in ImageNet classification, a result of our focus on optimizing for general purpose capability"。
- Gemini 詳細 caption 若單獨使用會 trivialize $L_{\text{CLIP}}$,需要與 PaliGemma 隨機交替才能避免讓 batch 內判別過於容易(Sec. 3.5, p. 6)。
- Head-only EMA 是「必要的中間態」:作者揭露完全去除 EMA(連 head 也共享)會造成嚴重 training instability 與 performance degradation(Sec. 3.4, p. 5)。
- 與 DINOv2 (dino.txt) 與 SILC 的 zero-shot segmentation 對照中,對手使用更昂貴的 TCL sliding window protocol,通常會抬高分數,作者承認此 protocol 不對稱(Sec. 4.1, p. 6)。
- DINOv3 比較中作者承認 DINOv3 teacher 用 6× 參數與 15× 影像,屬於資源不對等的對照(Tab. 8 caption, p. 8)。

#### 4.2.2 Phyra-inferred

- 「小型 student 反超大型 teacher」的論述只在 TIPS(Tab. 1)與 SigLIP2(Tab. 14)兩個家族上驗證,DINOv3、PE、CLIP 等家族並未檢驗,將其包裝成「SOTA vision encoders 普遍現象」過度泛化。
- Tab. 12 顯示 iBOT++ pretraining 仍以 75% masking 最佳,與 Tab. 2 在 distillation 時偏好 0% masking 形成衝突;作者僅以「distillation 的 teacher 已具備強 local semantics」一句話帶過,並未透過 probe teacher feature 直接驗證此假設。
- 與 DINOv3 的對照(Tab. 8)只在 ViT-L 進行,但 TIPSv2 自家旗艦是 ViT-g;在 ImageNet KNN 與 ADE20k linear segmentation 兩項輸給 DINOv3 L/16(79.7 vs 82.3、51.4 vs 54.9),這兩個重要 image-only 指標的落後並未在主文中被檢視。
- Tab. 4 head-only EMA 的「comparable performance」其實在 NYUv2 depth(0.353 vs 0.354)與 KNN ImageNet(84.1 vs 84.3)各有微幅退步,作者僅報整體不變,未討論這些一致出現的小幅迴歸是否來自 head-EMA 對 representation 平滑化能力的削弱。
- Tab. 13 的 multi-granularity caption ablation 是在 full EMA 下做的,並未在 head-only EMA(實際 TIPSv2 設定)下重跑,因此「2 CLS + (web / PaliGemma+Gemini)」是否仍是最佳策略沒有交互效應驗證。
- Fig. 2「successful anchoring」的證據只是 visible-token patch loss 曲線,沒有直接 probe student 與 teacher 表徵的 representational similarity (e.g., CKA),因此「anchoring 是語意性的」屬於詮釋而非證據。
- Tab. 5 dense image-text 比較未包含 PE-spatial G/14,儘管它在 Tab. 7 image-only ADE20k 上達 49.3,是更接近 dense alignment 領域的對手。
- iBOT++ 將 patch-level loss 套用至 4× 更多 token,但 Sec. 4.1 沒有與 baseline iBOT 對齊的 throughput / memory 比較,實際 compute overhead 未量化。

### 4.3 Phyra's Judgment (summary)

真正新穎的發現是把「對所有 patch token 強制與 teacher 對齊」當成 patch-text alignment 的核心驅動,而非更大模型或更多資料;iBOT++ 是把這個觀察翻譯為 pretraining objective 的最小可行改動,且 Tab. 9–11 顯示其在 CLIP / TIPS 兩個系列穩定有效,屬於可被廣泛複用的方法層貢獻。Head-only EMA 與 multi-granularity captions 是工程性收斂優化,單獨增益有限但作為 cost / robustness trade-off 合理。核心未解疑問是:為何 distillation 偏好 mask=0、pretraining 卻偏好 mask=0.75,作者僅給出敘述性解釋而無可證偽的機制檢驗,這也是後續工作最該追的線。

## 5. Methodology Deep Dive

### 5.1 Method Overview

TIPSv2 在 TIPS 既有的 contrastive image-text learning 加 self-supervised learning 配方上提出三項主要改進(全部以 Fig. 3 中綠色邊框標示):**iBOT++**(增強的 masked image modeling 損失,將 patch-level 蒸餾推廣到 visible tokens)、**Head-only EMA**(只對 projection heads 做 EMA 而不對 backbone 拷貝 teacher,大幅降低訓練資源需求)、以及 **Multi-granularity Captions**(在訓練中以 web alt-text、PaliGemma、Gemini 三種粒度的 caption 隨機交替監督,提升表徵 robustness)。整體訓練目標為三種損失的加權和:

$$
\mathcal{L} = \mathcal{L}_{\text{CLIP}} + \alpha\,\mathcal{L}_{\text{DINO}} + \beta\,\mathcal{L}_{\text{iBOT++}}
$$

其中 $\alpha = 1.0$、$\beta = 2.0$,$\mathcal{L}_{\text{CLIP}}$ 為兩個 CLS 對應的 contrastive loss 之平均(p. 12, Appendix A.9)。

模型架構由 ViT 影像編碼器 $f$(ViT-g/14 為 1.1B 參數,patch size 14)、transformer 文字編碼器 $g$(B/L/g 變體固定 12 層,SO 變體採其標準層數)以及兩個 CLS 全域 embedding 構成,其中一個 CLS 由 web alt-text 監督、另一個由合成 caption 監督。給定影像 $I$,$f$ 輸出全域表徵 $f^g(I) = e_g$ 與 patch 表徵 $\{e_1, \ldots, e_N\}$;給定文字 $T$,$g$ 輸出 $e_t$。Projection heads $h_s$、$h_t$ 將 embedding 投影到高維 prototype 空間,並透過 EMA 維持 teacher target 穩定。在 head-only EMA 下,$f_t = f_s$,只有 head 受 EMA 更新。

訓練分兩階段:低解析度階段在 90k steps、batch 8192 下,以 1 個 224 解析度 global crop 加 $M=6$ 個 98 解析度 local crops 訓練;高解析度適配階段在 9k steps、batch 4096 下將 global crop 升至 448、local crops 升至 140。ViT-g 規模使用 512 個 TPUv5 晶片訓練 2 天(p. 6, §4.1)。較小變體(ViT-B、ViT-L、SO-400m)以 ViT-g 為老師透過 patch-level distillation 蒸餾而成,亦同樣經過高解析度適配。資料源為 [33] 篩選的 WebLI 116M 影像子集,文字監督結合 web 原生 alt-text、PaliGemma 合成 caption 與 Gemini 1.5 Flash 合成 caption。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input
   ├→ Image I: [B, 3, H, W]      H=W=224 (low-res) or 448 (high-res)
   │     ├→ Global crop x_g:        [B, 3, H, W]
   │     ├→ Local crops x_L (M=6):  [B, M, 3, 98, 98]  (low-res)
   │     │                          [B, M, 3, 140, 140] (high-res)
   │     └→ Masked view I_mask:     [B, 3, H, W] + binary mask m: [B, N]
   │                                (mask ratio = 0.75)
   └→ Captions T: 3 sources (web alt-text / PaliGemma / Gemini)
          └→ Sampler picks 2 captions per image → tokenize → [B, 2, L_T]
             (L_T = ?)

Image Encoder f (ViT-g/14, 1.1B params; head-only EMA ⇒ f_t = f_s)
   Patchify + 2 CLS + pos-embed:
       [B, 3, H, W] → [B, 2 + N, d]    N = (H/14)^2 ∈ {256, 1024}; d = ?
   Transformer blocks → [B, 2 + N, d]
   Split outputs:
       ├→ Global CLS_1 (alt-text branch)  e_g^(1):  [B, d]
       ├→ Global CLS_2 (synthetic branch) e_g^(2):  [B, d]
       └→ Patch tokens {e_1, …, e_N}:                [B, N, d]

Text Encoder g (transformer, 12 layers for B/L/g; SO uses its standard count)
   [B, L_T] → [B, d_t]    d_t = ?
       └→ e_t^(1), e_t^(2) for the two sampled captions: [B, 2, d_t]

Projection Heads (separate global head + patch head)
   Student head h_s : [B, *, d] → [B, *, K]    K = prototype dim, ?
   Teacher head h_t : EMA of h_s    (the only EMA component)
       └→ teacher prototypes use stop-gradient + EMA centering / sharpening

Losses (target from teacher (f_t = f_s) + h_t; gradient flows via student)
   ├→ L_CLIP    : InfoNCE on (e_g^(1), e_t^(1)) and (e_g^(2), e_t^(2)),
   │              averaged across the 2 CLS branches
   ├→ L_DINO    : cross-entropy on global prototypes
   │              h_t(f_t^g(I))  vs  h_s(f_s^g(x_L_i))   for i = 1..M
   └→ L_iBOT++  : cross-entropy on ALL N patch prototypes
                  h_t(f_t(I)_i)  vs  h_s(f_s(I_mask)_i)  for i = 1..N
                  (extends iBOT by dropping the m_i mask factor)

Total: L = L_CLIP + 1.0 · L_DINO + 2.0 · L_iBOT++
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Image Encoder (ViT)

**Function:** 將影像 patchify 後通過 ViT 萃取全域(CLS)與 patch 兩種粒度表徵,作為三個損失的共同 backbone;在 head-only EMA 下學生與老師共用同一份 encoder 權重 ($f_t = f_s$)。

**Input:**
- Name: `I`(原始影像)、`x_g`(global crop)、`x_L`(local crops)、`I_mask`(masked view)
- Shape: 影像 `[B, 3, H, W]`,$H=W \in \{224, 448\}$;local crops `[B, M, 3, 98, 98]` 或 `[B, M, 3, 140, 140]`,$M=6$
- Source: WebLI 影像 + 隨機 resize / crop / flip augmentation;`I_mask` 由遮罩模組生成

**Output:**
- Name: `e_g^(1)`、`e_g^(2)`(兩個 CLS 全域表徵)、`{e_i}`(patch 表徵)
- Shape: `[B, d]`、`[B, N, d]`,$N=(H/14)^2 \in \{256, 1024\}$,$d$ 為 hidden dim
- Consumer: Projection Heads(供 $\mathcal{L}_{\text{DINO}}$、$\mathcal{L}_{\text{iBOT++}}$);Contrastive Loss(供 $\mathcal{L}_{\text{CLIP}}$)

**Processing:**

1. Patchify:以 patch size 14 將影像切成 $N$ 個 non-overlapping patches,線性投影至維度 $d$。
2. 串接 2 個 learnable CLS tokens 並加上 position embeddings(由 $16 \times 16$ 升至 $32 \times 32$,§4.2)。
3. 通過標準 ViT 殘差堆疊;對 $I_{\text{mask}}$ 流程相同但 75% 的 patch 被替換為 mask token。
4. 將輸出切分為兩個 CLS 與 $N$ 個 patch tokens 後分送下游。

**Key Formulas:**

$$
f^g(I) = e_g, \qquad f(I) = \{e_1, e_2, \ldots, e_N\}
$$

**Implementation Details:**

ViT-g/14 的 image 端參數量為 1.1B(Tab. 16, p. 12);ViT-L、ViT-B、SO 變體分別為 304.0M / 86.3M / 413.3M。論文未明示 hidden dim $d$,故以 `?` 標示。Position embeddings 由 $16 \times 16$ 升至 $32 \times 32$,改善所有評估且額外成本低(§4.2, p. 6)。Patch size 14 對齊 DINOv2 與 TIPS 慣例;較小變體以 ViT-g 為老師、依 §3.1 的 patch-level distillation 蒸餾而成。

#### 5.3.2 Text Encoder

**Function:** 將文字 caption 編碼為與影像 CLS 對齊的全域文字表徵,提供 $\mathcal{L}_{\text{CLIP}}$ 的 anchor。

**Input:**
- Name: `T`(tokenized caption)
- Shape: `[B, L_T]`,$L_T$ 為 token 序列長度(論文未指定)
- Source: Multi-Granularity Caption Sampler 取樣後的 web alt-text 或 synthetic caption

**Output:**
- Name: `e_t^(1)`、`e_t^(2)`(對應兩個 CLS 分支的文字表徵)
- Shape: 每個 `[B, d_t]`(`d_t` 論文未明示)
- Consumer: Contrastive Loss

**Processing:**

1. Token embedding 加上 position embedding 後輸入 standard transformer(§3.1)。
2. ViT-B、ViT-L、ViT-g 變體固定 12 層;SO-400m 變體保留其標準層數(Appendix A.7)。
3. 取末端 [EOS]/CLS token 線性投影得到 $e_t$,沿用 TIPS / CLIP 慣例。

**Key Formulas:**

$$
g(T) = e_t
$$

**Implementation Details:**

文字端參數量:B/14 為 109.6M、L/14 為 183.9M、g/14 為 389.1M、SO/14 為 448.3M(Tab. 16)。Transformer parameterization 沿用 TIPS;除 layer 數外,其他超參數論文未列。

#### 5.3.3 Multi-Granularity Caption Sampler

**Function:** 在三種粒度(web alt-text、PaliGemma、Gemini Flash)的 caption 中為每張影像取樣兩個 caption 分配給兩個 CLS,提升文字監督的多樣性與 robustness(§3.5, Fig. 4)。

**Input:**
- Name: `(T_alt, T_PaliGemma, T_Gemini)` 三組 caption
- Shape: 每組 `[B, L_T]`
- Source: WebLI 原始 alt-text;PaliGemma 與 Gemini 1.5 Flash 離線生成的 synthetic captions

**Output:**
- Name: `T^(1)`、`T^(2)`(分別餵入兩個 CLS 分支)
- Shape: 每個 `[B, L_T]`
- Consumer: Text Encoder

**Processing:**

1. 對 CLS_1 分支:固定使用 web alt-text(object-centric、簡短、噪聲較大)。
2. 對 CLS_2 分支:在 PaliGemma 與 Gemini 兩個合成 caption 中均勻取樣(`2 CLS (web / PaliGemma, Gemini)`,Tab. 13),交替長短與細緻度,避免 Gemini 過長 caption 把 batch-level contrastive 任務變得過於簡單(§3.5, p. 6)。
3. Sampling 在每個 batch 內獨立進行,使每張影像在 epoch 之間看到不同 caption 組合。

**Key Formulas:**

$$
T^{(2)} \sim \text{Uniform}\bigl\{T_{\text{PaliGemma}},\; T_{\text{Gemini}}\bigr\}
$$

**Implementation Details:**

Gemini caption 由 Gemini 1.5 Flash 生成,並條件於原始影像、alt-text 與 PaliGemma caption,以涵蓋姿態、卡通風格、季節等 alt-text / PaliGemma 漏掉的語意(Fig. 4)。Tab. 13 的消融顯示 dual-CLS 加交替策略在 segmentation、retrieval、ImageNet 與 zero-shot segmentation 上同步提升,單 CLS 與不交替策略均較差。

#### 5.3.4 Projection Heads with Head-only EMA

**Function:** 將 encoder 輸出投影到高維 prototype 空間以計算 self-distillation 的 cross-entropy;同時透過僅對 head 做 EMA(`f_t = f_s`)提供穩定 teacher target,並大幅降低需要做 EMA 拷貝的可訓練參數量(§3.4)。

**Input:**
- Name: encoder 輸出(全域 `e_g`、patch `e_i`)
- Shape: `[B, d]` 與 `[B, N, d]`
- Source: Image Encoder

**Output:**
- Name: 學生 prototype `p_s = h_s(·)`、老師 prototype `p_t = h_t(·)`(stop-gradient)
- Shape: `[B, K]` 與 `[B, N, K]`,$K$ 為 prototype 維度(論文未指定)
- Consumer: DINO Loss、iBOT++ Loss

**Processing:**

1. 對全域與 patch 各自使用一組 projection head(MLP + L2-norm,沿用 TIPS / DINO 設計)。
2. Student head $h_s$ 透過反向傳播更新;Teacher head $h_t$ 透過對 $h_s$ 的 EMA 更新。
3. Encoder 的 student 與 teacher 共用同一份權重($f_t = f_s$),不再對 backbone 拷貝 EMA 副本。
4. 對 teacher prototype 進行 EMA centering 與 sharpening 以避免崩塌(§3.4, Appendix A.9)。

**Key Formulas:**

$$
p_t = h_t\bigl(f_s(I)\bigr), \qquad p_s = h_s\bigl(f_s(I_{\text{mask}})\bigr)
$$

$$
\theta_{h_t} \leftarrow \tau\, \theta_{h_t} + (1-\tau)\, \theta_{h_s}
$$

**Implementation Details:**

ViT-B 規模下,head-only EMA 將可訓練參數量(以及需 EMA 的拷貝)減少約 42%(p. 5)。論文於 §3.4 末段指出完全去掉 EMA(連 head 也共用)會導致嚴重的訓練不穩定與性能退化,因此保留 head EMA 是必要的中介設計。$\mathcal{L}_{\text{CLIP}}$ 已限制 encoder 不致崩塌,使該簡化在實務上可行。EMA decay $\tau$ 與 prototype 維度 $K$ 論文未明示。

#### 5.3.5 iBOT++ Loss(Patch-Level All-Token Distillation)

**Function:** 將 iBOT 的 patch-level cross-entropy 損失推廣到所有 patch tokens(masked + visible),強制 student 在每個位置都對齊 teacher 表徵,進而顯著提升 patch-text alignment(§3.3, Eq. 3, Fig. 1)。

**Input:**
- Name: 學生 prototype `h_s(f_s(I_mask)_i)`、老師 prototype `h_t(f_t(I)_i)`
- Shape: 每個 `[B, K]`,$i = 1, \ldots, N$
- Source: Projection Heads

**Output:**
- Name: scalar 損失 `L_iBOT++`
- Shape: `[]`
- Consumer: Total Loss

**Processing:**

1. Teacher 處理未遮罩影像 $I$,Student 處理遮罩影像 $I_{\text{mask}}$(mask ratio 0.75 為最佳,Tab. 12)。
2. 將兩者 patch 表徵投影到 prototype 空間並以 cross-entropy 比對。
3. 與原始 iBOT 不同,去除 $m_i$ indicator,對 visible 與 masked tokens 同等加總(Eq. 3 對比 Eq. 2)。

**Key Formulas:**

$$
\mathcal{L}_{\text{iBOT}} = -\sum_{i=1}^{N} m_i\, h_t\!\bigl(f_t(I)_i\bigr)^{\!\top} \log h_s\!\bigl(f_s(I_{\text{mask}})_i\bigr)
$$

$$
\mathcal{L}_{\text{iBOT++}} = -\sum_{i=1}^{N} h_t\!\bigl(f_t(I)_i\bigr)^{\!\top} \log h_s\!\bigl(f_s(I_{\text{mask}})_i\bigr)
$$

**Implementation Details:**

預訓練最佳 masking ratio 經 Tab. 12 消融確認為 0.75:完全去除 masking 會劣化 zero-shot segmentation,ratio 0.5 介於兩者之間。$\beta = 2.0$。Fig. 2 顯示 visible token 的 patch-level loss 在 iBOT++ 持續下降,但在原始 iBOT 因不被監督而停滯,證實 visible-token 對齊是關鍵機制。Tab. 3 (ViT-g 預訓練) 將 iBOT 換成 iBOT++ 在 ADE150 上由 3.5 → 17.6 mIoU(zero-shot segmentation)。

#### 5.3.6 DINO Global Self-Distillation Loss

**Function:** 對全域 CLS 表徵施加 self-distillation,使 student 從 local crops 抽出的 CLS 對齊 teacher 從 full image 抽出的 CLS,提供影像層級的不變性訊號(Eq. 1)。

**Input:**
- Name: 學生 prototype `h_s(f_s^g(I_i))`、老師 prototype `h_t(f_t^g(I))`
- Shape: 每個 `[B, K]`,$i = 1, \ldots, M$,$M=6$
- Source: Projection Heads

**Output:**
- Name: scalar 損失 `L_DINO`
- Shape: `[]`
- Consumer: Total Loss

**Processing:**

1. Teacher 處理 1 個全域 crop(224 或 448 解析度),取 CLS 與全域 head 投影。
2. Student 處理 $M=6$ 個 local crops(98 或 140 解析度),取 CLS 與全域 head 投影。
3. 對所有 $M$ 個 local-global 配對計算 cross-entropy 並加總。

**Key Formulas:**

$$
\mathcal{L}_{\text{DINO}} = -\sum_{i=1}^{M} h_t\!\bigl(f_t^g(I)\bigr)^{\!\top} \log h_s\!\bigl(f_s^g(I_i)\bigr)
$$

**Implementation Details:**

權重 $\alpha = 1.0$。Local / global crops 的解析度與數量在低解析度與高解析度兩階段不同(§4.1):低解析度 1×224 + 6×98、高解析度 1×448 + 6×140。Teacher target 受 EMA centering / sharpening 規範以避免 prototype 崩塌(Appendix A.9)。

#### 5.3.7 CLIP Contrastive Loss

**Function:** 對齊影像與文字模態,以 dual-CLS 設計分別處理 web alt-text(object-centric)與 synthetic caption(dense spatial),透過 batch-level InfoNCE 提供強分類訊號(§3.1)。

**Input:**
- Name: 影像 CLS `e_g^(1)`、`e_g^(2)`;文字 embedding `e_t^(1)`、`e_t^(2)`
- Shape: 每個 `[B, d]` 與 `[B, d_t]`
- Source: Image Encoder、Text Encoder

**Output:**
- Name: scalar 損失 `L_CLIP`
- Shape: `[]`
- Consumer: Total Loss

**Processing:**

1. 對每個 CLS 分支獨立計算 InfoNCE:對應的 (image, caption) 為正樣本,batch 內其餘 caption 為負樣本(沿用 CLIP)。
2. 將兩個 CLS 分支的 contrastive 損失平均得 $\mathcal{L}_{\text{CLIP}}$(Appendix A.9, p. 12)。

**Key Formulas:**

$$
\mathcal{L}_{\text{CLIP}} = \tfrac{1}{2}\Bigl(\mathcal{L}_{\text{InfoNCE}}\!\bigl(e_g^{(1)}, e_t^{(1)}\bigr) + \mathcal{L}_{\text{InfoNCE}}\!\bigl(e_g^{(2)}, e_t^{(2)}\bigr)\Bigr)
$$

**Implementation Details:**

兩個 CLS 分別承擔 web 與 synthetic 監督通道,使全域對齊同時兼顧 object-centric 與 dense spatial 描述(§3.1 末段)。CLIP 損失權重為 1.0(總損失公式中作為基準項)。$\mathcal{L}_{\text{CLIP}}$ 對 encoder 提供穩定且非崩塌的訓練訊號,是 head-only EMA 簡化設計能成立的關鍵前提(§3.4)。Optimizer 為 Adafactor;具體 temperature、learning rate、warmup schedule 論文未列。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| WebLI (filtered subset from TIPS [33]) | Image-text pretraining | 116M images | train |
| PaliGemma synthetic captions | Image-text pretraining (caption augmentation) | per WebLI image | train |
| Gemini 1.5 Flash synthetic captions | Image-text pretraining (caption augmentation, new) | per WebLI image | train |
| ADE20K (ADE150) | Zero-shot semantic segmentation; linear-probe semantic segmentation | 150 classes | val |
| Pascal Context (PC59 / PC60) | Zero-shot semantic segmentation | 59 / 60 classes | val |
| Pascal VOC (VOC21) | Zero-shot semantic segmentation; linear-probe semantic segmentation | 21 classes | val |
| Flickr30K | Image-to-text / text-to-image retrieval | standard split | test |
| DOCCI | Image-to-text / text-to-image retrieval (long-text) | standard split | test |
| COCO | Image-to-text / text-to-image retrieval | standard split | test |
| ImageNet-1K | Zero-shot classification; KNN; linear probe | 1000 classes | val |
| NYUv2 | Monocular depth (linear probe); surface normals (DPT) | scene-centric | val |
| NAVI | Monocular depth (DPT); surface normals (DPT) | object-centric | val |
| UnED (Food2k, CARS196, SOP, InShop, iNat, Met, GLDv2, Rp2k) | Fine-grained / instance-level retrieval | 8 domains | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| mIoU (zero-shot segmentation) | Mean intersection-over-union between patch-text similarity argmax (cosine to class-name embeddings, upscaled) and ground-truth masks; the headline TIPSv2 claim is patch-text alignment | yes |
| mIoU (linear-probe segmentation) | mIoU under a linear probe on frozen features for PASCAL VOC / ADE20k | no |
| Recall@1 (retrieval) | Top-1 retrieval recall for I$\rightarrow$T and T$\rightarrow$I on Flickr30K / COCO / DOCCI; also average R@1 on UnED | no |
| Top-1 accuracy (zero-shot ImageNet) | Nearest-class-text-embedding accuracy on ImageNet-1K | no |
| Top-1 accuracy (KNN / linear) | Frozen-feature classification on ImageNet-1K | no |
| RMSE (depth) | Root-mean-squared error of monocular depth prediction on NYUv2 (linear probe) / NAVI (DPT) | no |
| Angular RMSE (normals) | Angular RMSE on NYUv2 / NAVI surface normal estimation via DPT | no |

備註：所有評測都在 frozen image-text encoder 之上進行，遵循 TIPS [33] 的 protocol 以確保可比性。zero-shot segmentation 預設使用 patch feature 與 class-name text embedding 之間的 cosine similarity（搭配 final transformer 的 value embedding，取自 [67]）；對 DINOv3 的比較（Tab. 8）則使用 TCL [6] 較昂貴的 sliding window protocol 以保持公平。

### 6.3 Training and Inference Settings

- **硬體**：512 TPUv5 chips，ViT-g 預訓練約 2 天（Sec. 4.1）。
- **Pretraining schedule**：低解析度階段 90k steps、batch size 8192；接著高解析度 adaptation 階段 9k steps、batch size 4096。
- **Crops / resolution**：低解析度時 1 個 global crop @ $224$ 與 6 個 local crops @ $98$；高解析度時 global crop @ $448$、local crops @ $140$。Augmentations 僅有 random resize、crop、flip。
- **Optimizer**：Adafactor [43]（Sec. A.9）。
- **Learning rate schedule**：the paper does not specify。
- **Loss weighting**：$L = L_{\text{CLIP}} + \alpha L_{\text{DINO}} + \beta L_{\text{iBOT}}$，其中 $\alpha = 1.0$、$\beta = 2.0$；$L_{\text{CLIP}}$ 是兩個 caption（web、synthetic）對應 contrastive loss 的平均（Sec. A.9）。Projection head 以 EMA centering + sharpening 防止 collapse。
- **Masking ratio**：iBOT++ 預訓練採 0.75（由 Tab. 12 ablation 決定）。
- **EMA**：head-only EMA，僅對 projection head $h_t$ 做 EMA，主 vision encoder 設 $f_t = f_s$。
- **Distillation**：ViT-B / ViT-L / SO-400m 由 ViT-g teacher 透過 patch-level distillation 蒸餾（Sec. 3.1、A.7），text encoder 固定 12 層（SO 變體例外）。Distilled student 也會經過 high-resolution adaptation。
- **Inference**：features frozen；zero-shot segmentation 使用 final layer value embedding 上採樣到影像解析度後與 class-name embedding 做 cosine matching；PCA 視覺化時 patch-14 模型 forward @ $1372$、patch-16 模型 forward @ $1568$（Fig. 5、Fig. 7、Fig. 8）。
- **Ablation schedule**：100k steps @ resolution 224，無 high-res adaptation（Sec. 4.2）。
- **Data scale 對比**：PE [4] ViT-G 處理 $47\times$ 多的 image-text pairs；DINOv3 teacher 用 $6\times$ 參數與 $15\times$ 影像（Sec. 4.3）。

### 6.4 Main Results

**Dense image-text（zero-shot segmentation, ViT-L 級別比較，Tab. 5）**

| Method | PC59 | PC60 | VOC21 | ADE150 |
|---|---|---|---|---|
| SigLIP2 SO/14 | - | 19.6 | 26.8 | 15.6 |
| SILC B/16 | 31.6 | - | - | 19.3 |
| DINOv2 (dino.txt) L/14 | 30.9 | - | - | 20.6 |
| TIPS L/14 | 33.5 | 30.4 | 30.5 | 20.8 |
| **TIPSv2 L/14 (ours)** | **37.1** | **33.9** | **44.4** | **24.7** |

註：TIPSv2 使用較簡單的 cosine matching protocol，仍超越使用 TCL sliding window 的 SILC 與 DINOv2 (dino.txt)。

**Global image-text（Tab. 6）**

| Method | COCO I$\rightarrow$T | Flickr I$\rightarrow$T | DOCCI I$\rightarrow$T | COCO T$\rightarrow$I | Flickr T$\rightarrow$I | DOCCI T$\rightarrow$I | 0-Shot ImageNet |
|---|---|---|---|---|---|---|---|
| CLIP L/14 | 56.3 | 85.2 | 44.4 | 36.5 | 65.2 | 40.4 | 75.5 |
| OpenCLIP G/14 | 67.3 | 92.9 | - | 51.4 | 79.5 | - | 80.1 |
| SigLIP2 g/16 | 72.8 | 95.4 | - | 56.1 | 86.0 | - | 85.0 |
| SILC G/16 | 73.2 | - | - | 54.7 | - | - | 83.7 |
| PE-core G/14 | 75.4 | 96.2 | - | 58.1 | 85.7 | - | 85.4 |
| TIPS g/14 | 74.0 | 93.0 | 57.2 | 59.4 | 84.5 | 58.8 | 79.9 |
| **TIPSv2 g/14 (ours)** | **75.7** | 95.1 | **68.9** | **60.7** | 85.9 | **72.8** | 80.7 |

7 個欄位中拿到 5 個 best/second-best；COCO 三項與長文本 DOCCI 雙向皆為最佳，DOCCI 領先幅度顯著（+11.7 / +14.0）。

**Image-only（Tab. 7，largest-class 比較）**

| Method | PASCAL Seg. | ADE20k Seg. | NYUv2 Depth | NAVI Depth | NYUv2 Norm. | NAVI Norm. | UnED | ImageNet KNN | ImageNet lin |
|---|---|---|---|---|---|---|---|---|---|
| DINOv2 g/14 | 83.1 | 49.5 | 0.372 | 0.054 | 20.7 | 24.0 | 62.7 | 83.6 | 87.3 |
| PE-core G/14 | - | 41.5 | - | - | - | - | - | 86.8 | 89.5 |
| TIPS g/14 | 83.6 | 49.9 | 0.353 | 0.058 | 21.9 | 24.2 | 68.2 | 83.3 | 86.2 |
| **TIPSv2 g/14 (ours)** | **85.1** | **51.6** | **0.334** | 0.059 | 21.7 | 24.1 | 67.0 | 83.7 | 86.8 |

9 項中拿到 7 個 best / second-best；PASCAL Seg. 較前最佳 +1.5 mIoU、NYUv2 Depth $-0.019$ RMSE。ImageNet 純分類略遜，作者自陳是聚焦 general-purpose capability 的取捨。

**DINOv3 比較（ViT-L 對齊，Tab. 8）**

| Method | ADE20k Seg. | NYUv2 Depth | 0-Shot ImageNet | COCO I$\rightarrow$T | COCO T$\rightarrow$I | ADE150 0-shot Seg |
|---|---|---|---|---|---|---|
| DINOv3 L/16 | **54.9** | 0.352 | **82.3** | 63.7 | 45.6 | 24.7 |
| **TIPSv2 L/14 (ours)** | 51.4 | **0.339** | 79.7 | **73.5** | **57.4** | **25.1** |

DINOv3 teacher 用 $6\times$ 參數與 $15\times$ 影像，TIPSv2 仍在 6 項中拿下 4 項。

### 6.5 Ablation Studies

**A. Distillation factor isolation（Tab. 2，ViT-L self-distillation）**：系統地拆解蒸餾與預訓練的差異，以回答「為何蒸餾能放大 patch-text alignment」這個 diagnostic 問題。
- 移除 mask（masking ratio 從 0.75 降到 0）時 ADE150 從 5.9 跳到 20.0、PC59 從 16.0 跳到 31.4，顯示對 visible token 加 loss 是關鍵；
- 文字 encoder 是否從 pretrain 初始化影響不大（rows 4–6）；
- 但若把 vision encoder 用 pretrained 權重初始化（row 7），ADE150 崩到 2.4，顯示 student 必須從 random init「跳離原本的 convergence basin」才能學到 patch-text alignment。
這是真正的 diagnostic ablation，不是 sanity check，並直接導出 iBOT++ 的設計動機。

**B. iBOT++ 對 TIPSv2 預訓練的累積貢獻（Tab. 4，每行累加）**：
- baseline TIPS reproduced：ADE150 zero-shot seg 3.5；
- $+$ iBOT++：ADE150 跳到 17.6（$+14.1$），同時 ImageNet KNN +1.2、PASCAL Seg. 微跌 0.3（diagnostic）；
- $+$ multi-granularity captions：Flickr I$\rightarrow$T +1.1、T$\rightarrow$I +3.7、ADE150 +0.5；
- $+$ head-only EMA：整體大致持平，ADE150 再 +1.0，主訴求是資源節省（ViT-B 訓練參數減 42%）。
這個 ablation 有效切割三個元件，但 head-only EMA 的「省資源」面向沒有給出 wall-clock / memory 的具體數字（只有比例）。

**C. iBOT++ pretraining 的 masking ratio（Tab. 12）**：在 iBOT++ 框架下重新掃 0.0 / 0.5 / 0.75，發現 0.75 仍最佳（ADE150 13.6 vs 0.0 時的 1.0）。這正面回答了「既然 distillation 不需要 mask，為何 pretraining 仍要 mask」的對照問題，作者解釋是因為預訓練時 student 還沒有 teacher 的 local semantics 可以繼承，MIM 仍是必要的。Diagnostic 而非 sanity。

**D. iBOT++ 在 CLIP 上的 generalizability（Tab. 9–11）**：在 vanilla CLIP（ViT-L）、CLIP+head-only-EMA、CLIP 2-CLS（ViT-g）三個 setting 下，iBOT++ 一致超過 iBOT，PC60 zero-shot seg 例如從 8.0$\rightarrow$22.9（Tab. 9）。這是把元件拆出 TIPSv2 recipe 後測 portability，屬於良好的 diagnostic。

**E. Multi-granularity captions（Tab. 13，ViT-g）**：對比 1-CLS vs 2-CLS、以及不同 caption 來源組合，最佳是 2-CLS 「web / PaliGemma+Gemini 交替」。Diagnostic，但僅在 full EMA 下做，未交叉驗證 head-only EMA。

**F. SigLIP2 family scale 驗證（Tab. 14）**：顯示 SigLIP2 也呈現 ViT-B > ViT-g 的反直覺現象，這是 motivating 的觀察 ablation 而非新元件 ablation。屬於支撐主論點的 sanity-style observation。

整體而言，TIPSv2 的 ablation 設計大多是 diagnostic：每個新元件都有對應的對照實驗，並進一步在外部架構（CLIP）上驗證 iBOT++ 的可移植性。較弱的部分是 head-only EMA 缺少 wall-clock 量測，以及未做 random-seed 變異分析。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 同尺寸下對齊 SigLIP2、DINOv2 (dino.txt)、SILC、PE-core/PE-spatial、TIPS、DINOv3、FRANCA 等近期 SOTA（Tab. 5–8），是當前 vision-language pretraining 的主流強 baseline。
- [covered] Has cross-task / cross-dataset evaluation — 9 個任務、20 個 dataset，涵蓋 zero-shot seg、global retrieval、classification、depth、normals、fine-grained retrieval（Sec. 4.1、Tab. 5–8、Tab. 15）。
- [covered] Has ablations that diagnose the new components — Tab. 2 拆解 distillation 各因素、Tab. 4 累積式拆 iBOT++ / multi-granularity / head-only EMA、Tab. 9–11 在 CLIP 上獨立驗證 iBOT++、Tab. 12 對 mask ratio 反向質詢，皆為 diagnostic。
- [partial] Has a scaling study — 提供 ViT-B / L / SO / g 四檔的全評測（Tab. 15）與比較表中的 model-size 對齊，但沒有 compute / token budget scaling curve，且 ViT-g 已是預訓練上限。
- [partial] Has an efficiency / wall-clock comparison — 提到 head-only EMA 對 ViT-B 減少 42% trainable params、ViT-g 用 512 TPUv5 chips 訓 2 天，但沒有 throughput 或 memory 的數字化對照，亦無對 baseline 的 wall-clock 對比。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 全篇未提到 seed、std 或多次重跑，所有差距以單次數字呈現。
- [partial] Releases code / weights / data sufficient for reproducibility — 專案頁 https://gdm-tipsv2.github.io/ 宣稱釋出 code 與 model（Sec. 1），但訓練資料是 WebLI 的私有 filtered 子集（依 [33]），不可完整重現預訓練。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1**:patch-level distillation 顯著提升 patch-text alignment,且 student 可超越 teacher。**Supported**:Tab. 1 與 Tab. 2 row (1) vs (4) 給出大幅 gap (PC59 6.9 → 31.4)。但「為何 student 可超越 teacher」的機制仍只是「supervise all tokens + random init」這兩個現象描述,缺乏理論解釋。
- **Claim 2**:iBOT++ 為新型 SSL objective,顯著改善 patch-text alignment。**Supported**:Tab. 3、Tab. 4 row 2、Tab. 9–11 在 TIPS / CLIP / CLIP-2CLS 三個 setup 一致有大幅增益,跨架構可複製性高,屬最強證據。
- **Claim 3**:Head-only EMA「drastically reduces memory while retaining majority of performance」。**Partially supported**:Sec. 3.4 提供 ViT-B 42% 參數削減,但 Tab. 4 row 4 與 row 3 的對比在 NYUv2 depth、Normals、KNN 上各有微幅 regression,效能保持為「大致持平」而非無損;且未在 head-only EMA 條件下重做 caption ablation,組合互動未驗證。
- **Claim 4**:multi-granularity captions 提升 robustness。**Supported on global I/T**:Tab. 4 row 3 顯示 Flickr T→I retrieval 由 81.7 跳到 85.4。但 robustness 一詞未量化(例如 OOD caption、噪音 caption 的容忍度),目前證據只證明「在乾淨評估上表現更好」。
- **Claim 5**:TIPSv2 在 9 tasks / 20 datasets 上 generally on par with or better than recent encoders。**Supported in aggregate**:Fig. 10 head-to-head 統計、Tab. 5–8 細分均支持此 summary,但 ImageNet 與 NAVI normals/depth 等部分項目落後,作者也已自承。整體 claim 成立但「SOTA」應限定在 dense image-text 範疇。

### 7.2 Fundamental Limitations of the Method

**對 distillation 設定的隱性依賴**:Tab. 2 的關鍵發現之所以成立,是因為 frozen teacher 已具備足夠 local semantics,讓 student 可以「不需 MIM 也能習得 patch alignment」。但 pretraining 階段的 EMA teacher 是從 student 蒸餾出的同 backbone,無外部 strong prior,所以 iBOT++ 仍須依賴 75% masking(Tab. 12)以獲得 reconstruction 訊號。這意味著方法無法用 distillation-style 的「全 token 監督 + 無 masking」直接 bootstrap patch-text alignment 於 pretraining,結構上仍需要外部強 teacher 才能完整釋放本論文發現的潛能。

**InfoNCE 與 caption 細節度的內生衝突**:Sec. 3.5 指出更詳細的 Gemini caption 反而拉低效能,因為 batch 內可區分性升高使 contrastive loss 變 trivial。作者用 PaliGemma / Gemini 隨機交替繞過此問題,但這是 workaround 而非根因解決;當 captioner 持續變強(這幾乎是趨勢),trivialization 會更嚴重,需要更複雜的 sampling schedule 或改換 sigmoid-style loss。

**Head-only EMA 的適用邊界由 contrastive loss 撐起**:作者明確主張 head-only EMA 之所以可行,是因為 $L_{\text{CLIP}}$ 已防止 encoder collapse。一旦 contrastive 訊號被削弱(極度 noisy text、low-resource language、純 image 場景),encoder 缺少防 collapse 機制將回到傳統 full EMA 需求。此設計不可移植到 SSL-only regime,使該技巧難以推廣到非 vision-language 場景。

**recipe 對 Google 內部 captioner 的綁定**:multi-granularity captions 由 web alt-text + PaliGemma + Gemini Flash 組成,後兩者均為 Google 模型。雖然 PaliGemma 開源,Gemini Flash 不開放微調與 logit 存取;欲在外部複製此 recipe,caption 來源的可獲得性與品質一致性是隱性瓶頸,且論文未提供 ablation 顯示若以開源替代品(如 BLIP-2、LLaVA)替換 Gemini 結果會如何降級。

### 7.3 Citations Worth Tracking

- **TIPS [33]** (Maninis et al., ICLR 2025):TIPSv2 的直接前身,所有「保留」的設計(雙 CLS、PaliGemma synthetic captions、distillation 配方)都來自這裡;不讀此篇難以分辨 TIPSv2 真正的新增量。
- **iBOT [68]** (Zhou et al., ICLR 2022):iBOT++ 改動的目標物。要評估「visible token loss」是否真為新貢獻,必須對 iBOT 原始公式與其後續延伸(SimMIM、MaskAlign、MR-MAE)有清楚理解。
- **DINOv3 [45]** (Siméoni et al., 2025):dense feature 的另一條路線(Gram anchoring),且是 Tab. 8 主要直接對手;讀完可比較「外部對齊損失」vs「visible-token 監督」兩種 spatial coherence 哲學。
- **SigLIP2 [50]** (Tschannen et al., 2025):同樣整合 SSL + contrastive 的最近代表,且 Tab. 14 顯示其也有「小模型反超大模型」現象;是評估 TIPSv2 增量的關鍵 baseline。
- **PaliGemma [3]** (Beyer et al., 2024):synthetic caption 來源;了解其 caption 偏置(描述風格、物體聚焦)有助於診斷 multi-granularity 策略是否真的彌補了 caption 缺口,還是只在特定 evaluation 分布上 over-fit。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 為何 iBOT++ pretraining 偏好 masking ratio = 0.75,但 distillation 偏好 0%?能否設計一條 schedule(隨 teacher 表徵成熟度動態降低 mask ratio)直接驗證「teacher 強度決定最適 masking」此假設?
- [ ] iBOT++ 對 visible token 的 patch-level loss 是讓 student 表徵真正「語意對齊」teacher,還是僅讓 prototype logit 分佈逼近?需要 representational probing(CKA、neighbor agreement)而非單一 zero-shot segmentation 指標。
- [ ] Head-only EMA 與 multi-granularity captions 是否存在交互效應?Tab. 13 是在 full EMA 下進行,實際 TIPSv2 設定的最適 caption 策略未驗證。
- [ ] 為何 TIPSv2 在 ImageNet classification 上落後 DINOv2 / PE-core / DINOv3?是 dual CLS 拆分容量、$L_{\text{DINO}}$ 與 $L_{\text{CLIP}}$ 權重失衡,還是 caption 噪音傷害 global discrimination?
- [ ] iBOT++ 把 patch-level loss 從 25% (mask) 擴大到 100% (mask + visible) 的 token 量,實際 wall-clock 與 peak memory 提升多少?目前只報了「2 days on 512 TPUv5」絕對值,缺乏與純 iBOT 設定對齊的 throughput 比較。
- [ ] 把 iBOT++ apply 到純 SSL backbone(DINOv3、I-JEPA)而非 contrastive 變種,是否仍能保持增益?Tab. 11 只驗證 CLIP 2 CLS,純 SSL 場景下無 $L_{\text{CLIP}}$ 防 collapse 是否會破壞 head-only EMA 的前提?
- [ ] Gemini Flash caption 是否引入 LLM 偏置(過度形容、hallucinated 屬性)?Fig. 4 範例都是正面案例,若 caption 中存在系統誤差(如過度推斷季節、品牌),會如何傳遞到 vision encoder?

### 8.2 Improvement Directions

依可行性由高至低排序:

1. **重做 Tab. 13 caption ablation 於 head-only EMA 下**:成本最低,僅需重跑 ablation 矩陣,可填補目前最明顯的 ablation 缺口,並驗證 TIPSv2 預設 caption 策略是否在最終配置下仍是最優。
2. **加入 representation probing 取代 Fig. 2 的 loss 曲線**:用 CKA 或 patch-level neighbor agreement 對 visible token 的 student / teacher 表徵做相似度比較,可把「anchoring is semantic」的詮釋升級為證據,且可作為 ablation 工具偵測 head-only EMA 是否削弱對齊強度。
3. **在 dense image-text 表(Tab. 5)補上 PE-spatial G/14 對照**:該模型專為 spatial 任務優化,是 dense alignment 領域更接近的 baseline,目前 omission 弱化了 SOTA 主張的可信度。
4. **將 InfoNCE 改為 SigLIP-style sigmoid loss**:可結構性緩解詳細 caption trivialize $L_{\text{CLIP}}$ 的問題,移除 caption alternation 這個 workaround;Sec. 3.5 的觀察直接指向此問題,且 SigLIP2 已驗證 sigmoid loss 與 SSL 的相容性。
5. **設計 mask-ratio curriculum 驗證 teacher-quality 假設**:從 0.75 線性降到較低值,觀察 zero-shot segmentation 是否隨 teacher 成熟而受惠於更多 visible-token 監督;若假設成立,curriculum 應勝過固定 0.75。
6. **以 frozen 大型 teacher(如 DINOv3 7B)作為 pretraining 階段的 supplementary anchor**:在 EMA teacher 之外加入外部強 teacher 做 patch-level distillation,理論上可把 distillation 階段的 mask=0 優勢帶進 pretraining,直接挑戰 §7.2 提出的方法上限。
7. **量化 iBOT++ 的 compute / memory overhead 並提供 throughput-matched 比較**:在固定 GPU-hours 下對照 iBOT vs iBOT++,確認增益不只是「更多 effective FLOPs」帶來的;若需要,可考慮對 visible token 採 random subsampling 以保持 token-loss 數量一致。
