<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# G2VLM — G2VLM: Geometry Grounded Vision Language Model with Unified 3D Reconstruction and Spatial Reasoning

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | G2VLM |
| Paper full title | G2VLM: Geometry Grounded Vision Language Model with Unified 3D Reconstruction and Spatial Reasoning |
| arXiv ID | 2511.21688 |
| Release date | 2025-11-27 |
| Conference/Journal | arXiv preprint (accepted to CVPR 2026) |
| Paper link (abs) | https://arxiv.org/abs/2511.21688 |
| PDF link | https://arxiv.org/pdf/2511.21688 |
| Code link | https://github.com/InternRobotics/G2VLM |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Wenbo Hu | Shanghai AI Lab; UCLA | https://gordonhu608.github.io/ | first author (equal contribution) |
| Jingli Lin | Shanghai AI Lab; SJTU | — | co-first author (equal contribution) |
| Yilin Long | Shanghai AI Lab; FDU | — | co-first author (equal contribution) |
| Yunlong Ran | Shanghai AI Lab; ZJU | — | co-author |
| Lihan Jiang | Shanghai AI Lab; USTC | — | co-author |
| Yifan Wang | Shanghai AI Lab; SJTU | — | co-author |
| Chenming Zhu | Shanghai AI Lab; HKU | — | co-author |
| Runsen Xu | Shanghai AI Lab; CUHK | — | co-author |
| Tai Wang | Shanghai AI Lab | https://tai-wang.github.io/ | corresponding author |
| Jiangmiao Pang | Shanghai AI Lab | https://oceanpang.github.io/ | corresponding author |

### 1.2 Keywords

vision-language model, spatial intelligence, 3D reconstruction, spatial reasoning, Mixture-of-Transformer-Experts, feed-forward visual geometry, interleaved reasoning, two-streams hypothesis

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Qwen2-VL | base model | Pretrained VLM used to initialize the semantic perception expert (Qwen2-VL-2B). |
| VGGT (Wang et al.) | baseline | SOTA feed-forward 3D reconstruction model that G2VLM compares against on depth, point and pose tasks. |
| π3 (Wang et al.) | baseline | Permutation-equivariant feed-forward visual-geometry model whose loss design and architectural ideas G2VLM adopts. |
| DUSt3R / MASt3R | predecessor | Foundational feed-forward visual geometry works that motivate G2VLM's geometry expert and 3D point-map prediction. |
| Bagel | influence | Mixture-of-Transformer-Experts unification (understanding+generation) that inspires G2VLM's MoT design with two experts. |
| VLM-3R / Spatial MLLM | concurrent | Concurrent spatial VLMs that bolt a frozen geometry encoder (e.g., VGGT) onto a VLM; G2VLM instead trains a native geometric expert. |
| MoGe | influence | Provides the optimal-scale visual-geometry loss formulation (point/normal/ROE solver) reused for G2VLM's pretraining. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於視覺語言模型 (VLM) 的「空間智能」缺口:目前的 VLM 多以 2D image-text 資料隱式學習空間先驗,缺乏將多視角 2D 觀測「抬升」到 3D 表徵的視覺幾何學習過程,因此在空間理解與空間推理任務上表現不佳。作者提出 G2VLM,把 feed-forward 3D 重建 (depth、point map、camera pose) 與高層空間推理整合在同一個 VLM 內,並透過 Mixture-of-Transformer-Experts 架構讓「幾何感知 expert」與「語義感知 expert」共享 self-attention,實現幾何特徵與語言推理的雙向交互。研究範圍涵蓋單目深度估計、多視角點雲重建、相機姿態估計,以及 SPAR-Bench、OmniSpatial、MindCube、OST-Bench 等空間推理 benchmark,屬於 spatial-intelligence VLM 與 feed-forward visual geometry 的交叉領域。

### 2.2 Domain Tags

- computer vision
- vision-language models
- 3D reconstruction
- spatial reasoning
- embodied AI

### 2.3 Core Architectures Used

- **Mixture-of-Transformer-Experts (MoT)**:G2VLM 主架構,由 geometric perception expert 與 semantic perception expert 兩個 transformer expert 組成,透過共享 self-attention 在每一層 transformer block 內讓兩條 pathway 進行 in-context 互動。
- **Geometric Perception Expert ("where pathway")**:本論文新設計的幾何專家,搭配 DINOv2 vision encoder 與輕量化 transformer-decoder 形式的 3D geometry heads (local point head、camera head、global point head),從 RGB 序列預測 camera pose $T_i \in SE(3)$、pixel-aligned 3D point map $X_i$ 等幾何輸出。
- **Semantic Perception Expert ("what pathway")**:以預訓練 Qwen2-VL-2B 為基礎的語義專家,沿用 Qwen2 vision encoder 的 native dynamic resolution 與 Multimodal Rotary Position Embedding (M-RoPE),負責多模態理解與空間推理的 next-token prediction。
- **DINOv2 Vision Encoder**:作為 geometric expert 的低階視覺特徵抽取器,提供適合 3D 重建等 low-level vision 任務的自監督特徵。
- **Qwen2 Vision Encoder**:semantic expert 使用的多模態視覺編碼器,提供語義豐富的特徵以支援 VQA 與空間推理。
- **Permutation-Equivariant Feed-Forward Visual Geometry Backbone**:沿用自 π3 的設計,移除 VGGT 式的 camera token 並只用 global attention,使 LLM 能以一致方式處理 DINOv2 與 Qwen2 兩條視覺特徵流並支援可變視角數。
- **Two-Stage Training Pipeline**:第一階段 freeze semantic expert、從零訓練 geometric expert(視覺幾何 loss $\mathcal{L}_{VG} = \mathcal{L}_{points} + \lambda_{cam}\mathcal{L}_{cam} + \lambda_{normal}\mathcal{L}_{normal}$);第二階段 freeze geometric expert,以 cross-entropy loss 微調 semantic expert,讓模型可用大規模 in-the-wild 多視角影像/影片擴展空間理解。

### 2.4 Core Argument

作者主張 VLM 在空間任務上表現不佳的「根因」並非資料量不足或語言能力不夠,而是訓練範式根本缺少 visual geometry learning:當前 VLM 把多張影像或影片當成「flat」的 2D token 序列做 next-token prediction,從未被要求把 2D 觀測重建成一致的 3D 世界表徵,因此無法穩健回答距離、方位、視角變換等空間問題。論文借用認知科學的 two-streams hypothesis (ventral 對應「what」、dorsal 對應「where」) 作為理論框架,主張一個真正具備空間智能的 VLM 必須同時擁有獨立但互通的「what pathway」(語義) 與「where pathway」(幾何)。從這個診斷出發,他們的解法在邏輯上是必要的:(1) 引入專屬的 geometric perception expert 並由 DINOv2 encoder 與輕量 3D heads 輸出 camera pose、depth、point map,使 VLM 真正「學會」3D;(2) 採用 Mixture-of-Transformer-Experts 並以共享 self-attention 連接兩個 expert,讓幾何特徵能 in-context 地被語義 expert 取用,支援 interleaved reasoning;(3) 採二階段訓練,先在大量 3D-annotated 資料上從零訓練幾何 expert,再 freeze 幾何 expert、僅以 cross-entropy 微調語義 expert,以便用大量易取得的 in-the-wild 多視角影像/影片擴展空間理解能力,擺脫 3D 標註的稀缺瓶頸。實驗顯示這套設計同時在 3D 重建上接近 VGGT/π3,在 SPAR-Bench 上以 2B 規模超越 GPT-4o 18.5 點,證明「把低階幾何學習 native 內建到 VLM」是補上空間智能缺口的合理且必要路徑。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(210 words)

標題「G2VLM: Geometry Grounded Vision Language Model with Unified 3D Reconstruction and Spatial Reasoning」直接點出論文的兩條軸線：以 geometry 為基礎，並把 3D reconstruction 與 spatial reasoning 統一在同一個 VLM 內。Abstract 開門見山地把問題定位為：當前 VLM 在 spatial intelligence 上仍然脆弱，原因是缺少能從 2D 影像「重建 3D 空間」的 visual geometry learning 過程。作者把這個診斷直接連到方案：G2VLM 是一個 geometry grounded VLM，原生地利用學到的 3D visual geometry features 來預測 3D 屬性，並透過 in-context learning 與 interleaved reasoning 強化 spatial reasoning。Abstract 強調這個統一設計具備 scalability：模型可以在大量 multi-view images 與 videos 上訓練，同時享受到原本只能由難以蒐集的 3D 標註得到的 visual prior。實驗主張兩面齊備：在 3D reconstruction 上與 SOTA feed-forward 模型可比，在 spatial understanding 與 reasoning 上達到更佳或相當的結果。Abstract 的最後一句鋪陳論文的定位野心 — 把 semantically strong VLM 與 low-level 3D vision 任務統一，作為社群的 strong baseline，並指向 3D scene editing 等下游應用。整段 abstract 已經把「問題、診斷、方法骨幹、scaling 論述、實驗結論、未來應用」六件事壓縮完畢，為 §1 的展開鋪設好故事框架。

### 3.2 Introduction

(950 words)

Introduction 沿著 abstract 的診斷往下展開。作者先承認 VLM 已是強大的 foundation model，但隨即引述多篇 spatial reasoning benchmark 工作指出 VLM 在 spatial understanding 上有明顯落差，並把這個落差歸因於知識取得方式：目前 VLM 主要透過大規模 2D image-text 資料隱式學習物理世界知識，輸入端把多影像或 video frame 視為「平坦」的 2D 序列，缺乏顯式的 visual geometry 學習，無法把 2D 觀察提升為 coherent 的 3D 表徵。論文接著把解決方案類比於人類認知中的 two-streams hypothesis：ventral stream 對應物件辨識（多模態理解）、dorsal stream 對應空間定位（visual geometry learning）。這個類比成為整篇方法設計的精神支柱，也讓「為何要用兩個 expert」變得自然而非工程上的特設選擇。

接著作者導入 G2VLM 的整體架構：Mixture-of-Transformer-Experts (MoT)，由 geometric perception expert（where pathway）與 semantic perception expert（what pathway）組成，兩者透過 shared self-attention 互通。論文特別強調這個設計帶來的 scaling 優勢 — 模型從純 2D 影像學會 3D geometry，因此不再被難以蒐集的 depth maps、camera poses 等 3D 標註綁住，可以利用 in-the-wild 的 multi-view 影像與 video。這一段其實是回應 abstract 提出的「scalability」承諾，並把方法論放回到資料工程的現實。

訓練策略則以兩階段呈現：第一階段凍結 semantic expert（從 Qwen2-VL 初始化），對 geometric expert 在大規模 3D 標註資料上從頭訓練；第二階段解凍 semantic expert，與 geometric expert 共同在 spatial understanding 資料上訓練，讓語意端學會利用幾何特徵。Introduction 把這個流程描述得簡潔，足以讓讀者預期 §3 會給出細節。

最後 introduction 端出一連串具體實驗結果作為「先言實證」：在 Sintel monocular depth 上把 VGGT 的 Abs Rel 從 0.335 降到 0.297；在 SPAR-Bench 上比 GPT-4o 高 18.5 分；在四個 spatial reasoning benchmarks 上以 2B 模型達到優於或可比的成績。同時提及一個重要 finding — geometric 與 semantic 表徵存在 positive interplay，幾何端越強，spatial reasoning 的提升越大，這個觀察為 §4.3 的 ablation 預留鋪墊。Introduction 最後以四點 contributions 總結：首個統一 3D reconstruction 與 high-level spatial understanding 的 VLM、雙 expert 架構、實驗證明的 proficiency，以及作為社群 baseline 的願景。整段 introduction 完成了「問題 → 認知類比 → 架構主張 → 訓練策略 → 結果預告 → 貢獻」的標準論述弧線。

### 3.3 Related Work / Preliminaries

(720 words)

Related Work 分三個子塊，分別對應論文要切入的三個座標軸：unified VLM、spatial reasoning VLM、feedforward visual geometry。第一塊「VLMs as Unified Foundation Models」回顧 VLM 從多模態理解走向 any-to-any 統一範式的路徑，特別點名 Bagel 同樣採用 MoT 架構處理多模態理解與影像生成，以區辨自身位置：G2VLM 的 expert 並非處理「理解 vs 生成」，而是「visual geometry learning vs spatial reasoning」這兩個任務性質差異更大的軸，因此架構細節、預訓練目標與 joint training 策略都與 Bagel 不同。這段建立了「相似形體、不同任務」的方法學定位。

第二塊「Spatial Reasoning VLMs」串起一系列 spatial benchmark 與 spatial VLM。作者把同領域工作分為兩派：一派如 SpatialVLM、SpaceQwen 沿用標準 VLM 設計，把影像視為平坦的 2D 資料，僅靠 curated spatial 資料訓練；另一派如 VLM-3R、Spatial MLLM 已注意到 VLM 缺乏幾何特徵，做法是把凍結的 geometry encoder（如 VGGT）作為額外表徵接進 VLM。作者用這個對比凸顯 G2VLM 的差異：不是把幾何模型當作外掛 encoder，而是把 geometric expert 直接「原生」整合進 VLM 之內，使 visual geometry prediction 與 high-level spatial reasoning 共享同一套表徵與注意力。這個區分對應 §3.1 的 MoT 設計選擇。

第三塊「Feedforward Visual Geometry」則建立模型在另一條傳統的位置：DUSt3R、MASt3R 用 transformer 直接預測 pixel-aligned 3D point map，後續 MV-DUSt3R+、Cut3R、Fast3R、VGGT、π3 把這條路擴展到多視角，效率與準確度都超越 optimization-based pipeline。作者隨即指出這些方法的局限：它們專注 geometric reconstruction，缺乏更高層的 scene understanding，因此難以服務 spatial reasoning 任務。G2VLM 的價值主張因此明確 — 在一個框架內同時保有 feed-forward 架構的幾何精度與效率，並擴展出語意端的 spatial comprehension 能力。

整節 related work 的故事邏輯非常工整：先在 unified VLM 領域佔位（與 Bagel 區分），再在 spatial reasoning VLM 領域定位（從外掛幾何 encoder 進化到原生整合），最後在 feedforward visual geometry 領域對接（補上語意理解的缺口）。三條軸交會處正好就是 G2VLM 的設計空間，為 §3 的 Method 做了最有說服力的鋪墊：方法看似 ambitious，但在 related work 提供的座標系內，它的架構選擇是多條軸線交集的自然產物。

### 3.4 Method (overview narrative)

(1450 words)

Method 一開始就以一句話把整節 framing 完成：G2VLM 是統一 spatial 3D reconstruction 與 spatial understanding 的 unified geometry-grounded VLM，並列出 §3.1 架構、§3.2 geometric expert 學習、§3.3 semantic expert 學習三段。整節故事邏輯沿著「先設計、再學幾何、最後讓語意端用上幾何」推進。

§3.1 Model Architecture 把 MoT 拆成兩個 expert：geometric perception expert 接 DINOv2 encoder，把每張影像 $I_i$ 映射為 LLM hidden states $h_i$，再經過 lightweight transformer geometry heads 產出 camera pose $T_i \in SE(3)$ 與 pixel-aligned 3D point map $X_i$。semantic perception expert 則建構在預訓練 Qwen2-VL-2B 上，沿用 Qwen2 vision encoder 與 M-RoPE，並刻意做了一些「向 VLM 靠攏」的簡化：不使用 register tokens、僅使用 global attention、移除 VGGT 風格的 camera token、改採 π3 的 permutation-equivariant 設計。這些選擇的共同目標是縮小幾何端與語意端之間的表徵 gap，讓 LLM 能以同樣方式處理兩種 vision encoder 的輸出，避免特殊先驗破壞統一性。這段為後續的「為什麼幾何能直接餵給語意端做 reasoning」提供了架構基礎。

§3.2 Visual Geometry Learning 描述第一階段訓練：凍結 semantic expert（載入 Qwen2-VL 權重），geometric expert 從零訓練。Loss 設計沿用 MoGe 與 π3 的傳統，由三項加權組成：$L_{points}$、$L_{cam}$、$L_{normal}$。$L_{points}$ 用 optimal scale factor $s^*$ 對齊預測點圖與 ground-truth，並由 ROE solver 解出。$L_{cam}$ 是 rotation 與 translation 兩項的加權和：rotation 用 geodesic 角距，translation 用 Huber loss 比較 $s^* \hat{t}_{i\leftarrow j}$ 與 ground-truth。$L_{normal}$ 鼓勵局部表面平滑。整節從「凍結語意、專心學幾何」的策略，連到「點、相機、法向」三項組合監督的工程選擇，敘事上強調這是把幾何能力先穩定地裝進 expert 的一階段任務。

§3.3 Spatial Reasoning Learning 進入第二階段：以 cross-entropy 訓練 semantic expert，使其在 in-context learning 與 interleaved reasoning 中利用幾何特徵。論文在這裡花筆墨討論一個 design space：semantic expert 用 CE，geometric expert 該怎麼動？作者比較三種策略 — (1) CE Loss Only：凍結 geometric expert，逼語意端學會「使用」幾何特徵，並保留幾何能力不退化；(2) CE + CE：用 CE 微調 geometric expert，使其特徵專為 spatial understanding 客製；(3) VG + CE：同時保留 visual geometry loss 與 CE。在 ScanNet 的研究顯示（Figure 4），VG + CE 在兩端都最好，但需要大規模 3D 標註資料，scalability 受限。最後 G2VLM 選 CE Loss Only 作為主模型 — 凍結幾何端保住預訓練幾何能力，同時可在大量 video 資料上 scale；CE + CE 則被指定為 spatial reasoning 特化變體 G2VLM-SR。這個敘事把「為何不選看似最佳的 VG + CE」說清楚，是 trade-off 而非疏漏。

最後段落補上 implementation details 與訓練資料：geometric expert 預訓練分兩階段，先 224×224 用 lr 2e-4 跑 100K step，再 518×518 用 5e-4 跑 20K step；joint training 用 lr 2e-5 跑 16K step。所有訓練皆 bfloat16、gradient checkpointing、grad clip 1.0。資料涵蓋 ScanNet、Co3Dv2、BlendMVS、DL3DV、MegaDepth 等十餘組 3D 資料集，joint stage 加入 SPAR-7M、Omnispatial、Mindcube、OST-Bench training set 與 LLaVA-One-Vision 一般 VQA。這段把抽象架構落到工程現實，為 §4 的實驗結果鋪出可信的訓練底盤。整節 method 的故事弧線是「架構統一 → 幾何先穩 → 語意再學會用幾何 → 工程上 scale 得起來」。

### 3.5 Experiments (overview narrative)

(1230 words)

Experiments 的整體布局回應 introduction 的雙主張：模型在 visual geometry 上要與 SOTA feed-forward 模型可比、在 spatial understanding/reasoning 上要全面領先或具競爭力。§4 開頭以一段 overview 把這兩條評估線同時鋪好，並預告 §4.3 的 design ablation 將驗證關鍵設計選擇。

§4.1 Visual Geometry Results 走「三項任務、各自 benchmark」的路線。Monocular Depth 在 Sintel 與 NYU-V2 上以 Abs Rel 與 $\delta < 1.25$ 評測；Point Map 在 7-Scenes（stride 40 sampling）與 ETH3D（每 5 張）上做 Umeyama Sim(3) 對齊加 ICP 後計算 Acc.、Comp.；Camera Pose 在 Co3Dv2 上以 RRA、RTA 及 AUC@30 評估。論文反覆強調的論點是：G2VLM 不依賴 VGGT 風格的 camera token、不從預訓練 weights 微調（如 π3），仍能在這三類任務上取得 on-par 表現 — 例如 Sintel 上 Abs Rel 0.297 優於 VGGT 的 0.335。最後以 Figure 5 的 qualitative 結果展現對 object-level、structure-level、indoor、outdoor、靜態與動態場景的泛化能力。這段在敘事上完成了「我能做幾何、我做得不差」的實證承諾，同時為後續 spatial reasoning 的提升埋下「因為幾何端紮實所以語意端能用得好」的伏筆。

§4.2 Spatial Understanding & Reasoning Results 切換到第二條評估線，benchmark 涵蓋 SPAR-Bench、OmniSpatial、MindCube（spatial mental modeling）、OST-Bench（online spatio-temporal scene understanding），對手包含 proprietary 模型（GPT-4o、Claude）、open-source 模型（LLaVA、Qwen 系列、InternVL2.5）、以及 spatial expert 模型（SpaceMantis、Spatial-MLLM、SpaceQwen、VLM3R）。論文先點出 G2VLM 與 G2VLM-SR 都顯著超越 base model Qwen2-VL-2B，再強調 G2VLM-SR 在 SPAR-Bench 上以 2B 體量比 GPT-4o 高 18.48 分。對比 spatial expert 模型，G2VLM-SR 在四個 benchmark 全部領先；對比 open-source，僅在 OST-Bench 輸給 Qwen2.5-VL-72B，作者把這歸因於 online spatio-temporal 任務需要更大模型存放的世界知識，並把 scaling G2VLM 留作 future work。這個處理顯得有節制 — 不誇大、也不迴避 — 為小模型的論述補上邊界條件。

§4.3 Discussions and Ablation Study 把實驗的價值再往設計層次推。第一個問題是 encoder design：單一 vs. 雙 encoder。作者比較「都用 CLIP」與「DINO + CLIP」，發現雙 encoder 在兩條任務軸上皆勝出，並且 DINO 不只服務 low-level 幾何，還補足了多模態理解所缺乏的視覺資訊。第二個問題是 geometric expert 的 attention 機制：因為主流 alternating-attention 與 LLM 框架的一致 mask 不相容，作者比較 frame、global、mixed 三種 mask-based 變體，global attention 全面勝出（Figure 6b）。第三個問題接續探討 geometry 與 reasoning 的 interplay：global attention 同時帶來最佳的 spatial reasoning（Table 2），印證了「幾何越強、推理越強」的 positive interplay 主張。最後一個 ablation 把 geometry pretraining 整體拔掉：與只在 spatial 資料上 finetune 的 baseline 比，G2VLM 顯著勝出，證明學到的 visual geometry 表徵是模型效能的核心而非裝飾。整節 experiments 從「兩條任務軸的成績單」走到「設計選擇的因果證據」，把 method 的每個關鍵決策都用實驗釘住。

### 3.6 Conclusion / Limitations / Future Work

(150 words)

Conclusion 段落極為精煉，沿用 introduction 與 abstract 的核心 framing 收束全文：G2VLM 是一個 unified VLM，橋接 spatial intelligence 的兩個基本面 — 3D reconstruction 與 spatial understanding，並原生使用學到的 3D visual geometry features，透過 in-context learning 與 interleaved reasoning 強化 spatial reasoning。實驗結論被再次概括為「在 3D reconstruction 上與 SOTA 可比、在多數 spatial reasoning benchmark 上最佳」。Limitations 只點出一條：當模型 scaling 到更大尺寸時，訓練存在不穩定性，需要進一步的 optimization techniques、資料 curation 與算力。這個 limitation 與 §4.2 中提到「在 OST-Bench 上輸給 72B 模型、把 scaling 留給未來」的伏筆遙相呼應，在語意上一致。Future Work 沒有被列為獨立段落，而是被嵌進 conclusion 的最後一句：作者強調方法的 universality 與 effectiveness，希望 G2VLM 能作為社群的 strong baseline，解鎖更多 high-level 與 low-level 之間的 semantic spatial 應用，呼應 abstract 提到的 3D scene editing 願景。整段在篇幅上節制，但完成了「重申主張、誠實標示限制、指向後續方向」三項標準功能。

## 4. Critical Profile

### 4.1 Highlights

- 提出 G2VLM,首個在單一 VLM 內同時整合 feed-forward 3D reconstruction 與 spatial reasoning 的統一模型,以 two-streams hypothesis (ventral/dorsal) 為架構靈感 (page 2, Figure 2)。
- 採用 Mixture-of-Transformer-Experts 設計,讓 geometric 與 semantic 兩個 expert 透過 shared self-attention 互通,使 geometric features 能 in-context 地被 semantic expert 取用以支援 interleaved reasoning (page 3, Figure 3)。
- 在 Sintel 單目深度估計上將 Absolute Relative Error 從 VGGT 的 0.335 降到 0.297,並在 NYU-v2 上達到 $\delta < 1.25$ 為 0.954,接近 $\pi^3$ 的 0.956 (Table 1a, page 7)。
- 在 SPAR-Bench 上,G2VLM-SR-2B 取得 54.87 平均分,以僅 2B 參數量超越 GPT-4o 達 18.48 點,並超越 VLM3R-7B 的 43.21 (Table 1b, page 7)。
- G2VLM-SR 在 SPAR-Bench Low 子類 (59.99) 超越 human performance (55.31),具體 sub-task 如 Depth-OC 達到 80.27 對 human 的 72.75 (Table 3, page 14)。
- Ablation 證實 dual-encoder (DINOv2 + Qwen2 vision encoder) 同時改善 visual geometry 與 spatial understanding,顯示 DINO 的 low-level features 對高層 spatial reasoning 也有 complementary 貢獻 (Figure 6a, page 8)。
- 對 LLM-compatible 的 attention mask 做系統比較,證明 global attention 在 geometry training loss 與 SPAR-Bench 雙重指標上一致優於 frame attention 與 mixed attention (Figure 6b、Table 2, pages 7–8)。
- 提出可擴展的兩階段訓練流程:先以大規模 3D-annotated 資料訓練 geometric expert,再 freeze 它並僅以 cross-entropy 微調 semantic expert,藉此用 abundant in-the-wild 多視角影片資料擴展 spatial understanding,擺脫 3D 標註瓶頸 (page 4, §3.3)。
- 透過 ablation 量化 geometry pretraining 的貢獻:相對僅以 spatial data finetune 的 Qwen2-VL-2B baseline (48.93),G2VLM-SR 在 SPAR-Bench 上提升至 54.87,證實 visual geometry representations 是核心增益來源 (Table 2, page 8)。
- 確立 geometry 與 reasoning 之間的 positive interplay:在三種 attention variant 中,geometry loss 越低的設計同時也帶來更高的 SPAR-Bench 分數,呼應主張 (Table 2, page 8)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 大規模模型訓練的 instability 問題,作者明言此挑戰需要 advanced optimization、careful data curation 與大量計算資源才能克服 (§5 Conclusion, page 8–9)。
- visual geometry training 過程中存在 loss spikes,作者歸因於 noisy large 3D annotation data,並以 loss clipping > 10 與 smooth-to-0 作為 workaround,坦言進一步資料清理才能根治 (Supplementary §B, page 13)。
- VG + CE Loss 的 joint-training 雖然在 spatial reasoning 與 geometry 上同時最佳,但因仰賴大規模 3D-annotated 資料而 scalability 受限,迫使主模型退而選擇 CE Loss Only (§3.3, page 5)。
- 在 OST-Bench 上 G2VLM-SR-2B 並未取得最佳成績,被 Qwen2.5-VL-72B 超越,作者承認 online spatio-temporal scene understanding 偏好較大的 architecture,並將 scaling 留作 future work (§4.2, page 6)。

#### 4.2.2 Phyra-inferred

- Camera Pose AUC@30 在 Co3Dv2 上僅 74.81,顯著落後 VGGT (88.59) 與 $\pi^3$ (88.41) 達 13 點以上,但作者僅以「未使用 camera tokens」與「未從 pretrained weights fine-tune」帶過,未量化此設計選擇對下游 spatial reasoning 是否實質損失 (Table 1a, page 7)。
- Point Estimation 在 ETH3D 上 Acc. 為 0.414、7-Scenes Acc. 為 0.046,皆明顯遜於 VGGT (0.28、0.022) 與 $\pi^3$ (0.194、0.016),但 abstract 與正文均以「on-par/comparable」概括,缺乏對品質落差的誠實討論 (Table 1a, page 7)。
- G2VLM-2B (非 SR 版) 在 OST-Bench 上 24.60 反而低於 base model Qwen2-VL-2B 的 22.59 與微幅落後,且 OmniSpatial 也僅 44.13,顯示「直接訓練 geometry expert」未必對所有 spatial benchmark 都有正向遷移,但作者僅突出 G2VLM-SR 的成果而未討論此 regression (Table 1b, page 7)。
- 「positive interplay」的證據僅靠 attention variant 三點構成的單調關係 (Table 2),沒有控制 geometry quality 與 reasoning quality 的獨立操弄實驗 (例如固定 attention 改變 pretraining 規模),因此 interplay 仍可能只是 confounding。
- 與最直接的 concurrent 對手 VLM-3R 與 Spatial-MLLM 的「frozen VGGT encoder」設計,缺乏 apples-to-apples 比較:作者以 7B 對 2B 取得勝出,但未在相同 base VLM、相同訓練資料下對照「frozen geometry encoder vs. native trained expert」,使核心架構主張難以隔離 (§4.2、§2 Related Works, pages 3, 6)。
- Joint-training stage 僅 16K iterations 且 lr 為 2e-5,相對於第一階段 100K + 20K iterations 顯得極短,但論文未討論 semantic expert 是否因此 underfit,也未報告 G2VLM-SR 在 visual geometry tasks 上是否退步 (§3.3 Implementation Details, page 5)。
- 訓練資料混合涵蓋 17 個 3D dataset 以及 SPAR-7M、Mindcube、OST-Bench 訓練集,但 Mindcube 與 OST-Bench 同時也是評估 benchmark;雖然使用其官方 train split 屬合規,作者未討論 in-domain training 對 generalization 結論的影響 (§3.3 Training Data, pages 5–6)。

### 4.3 Phyra's Judgment (summary)

論文最有力的貢獻是「在 VLM 內 native 訓練 geometric expert,而非 bolt 上 frozen encoder」這個架構主張,並以 SPAR-Bench 上 2B 規模超越 GPT-4o 18.5 點作為強力證據;這個發現對 spatial-VLM 路線設計確實有指引價值。然而 visual geometry 端的 point/pose 指標仍明顯落後 VGGT 與 $\pi^3$,作者以「on-par」描述略有過度推銷,且 geometry-reasoning 的「positive interplay」證據單薄,本質上只在三個 attention variant 上做點對點比較。核心未解問題是:這套方法的勝出究竟來自 native geometry pretraining 本身,還是來自 dual encoder + 大規模 spatial-reasoning 訓練資料的綜合效應,目前無法分離。整體仍是一篇紮實且方向正確的 baseline,但「unified」的 narrative 比實證結論更前衛。

## 5. Methodology Deep Dive

### 5.1 Method Overview

G2VLM 採用 Mixture-of-Transformer-Experts (MoT) 架構,由兩個並行但互通的 transformer expert 組成:geometric perception expert(對應 dorsal stream / "where pathway")負責 visual geometry learning,semantic perception expert(對應 ventral stream / "what pathway")負責 multimodal understanding 與 spatial reasoning。每個 expert 都擁有獨立的 QKV projection 與 FFN 參數,但在每一層 transformer block 中,所有 token(包含 geometric tokens、semantic visual tokens 與 text tokens)會進入一個共享的 multi-modal self-attention 計算,使兩條 pathway 能在 in-context 條件下雙向交換資訊,並支援 interleaved reasoning。

模型輸入為 $N$ 張 RGB 影像 $(I_i)_{i=1}^{N}$,$I_i \in \mathbb{R}^{3 \times H \times W}$,以及文字 query。Geometric expert 使用 DINOv2 vision encoder 抽取 low-level 視覺特徵,配合 lightweight transformer-decoder-based geometry heads(local point head、camera head、global point head)輸出每張影像的 camera pose $T_i \in \text{SE}(3) \subset \mathbb{R}^{4 \times 4}$、相機座標系下的 pixel-aligned point map $X_i \in \mathbb{R}^{H \times W \times 3}$,以及深度與點雲。Semantic expert 以預訓練的 Qwen2-VL-2B 為基礎,沿用其 Qwen2 vision encoder(支援 native dynamic resolution)與 Multimodal Rotary Position Embedding (M-RoPE),輸出由 text de-tokenizer 解碼成自然語言答案。為了縮小兩條 pathway 的表徵差異,作者在 geometric expert 中刻意簡化了一些 visual geometry 模型常見的設計:不使用 register tokens、僅使用 global attention 層、移除 VGGT 式的 camera token,並改採 $\pi^3$ 的 permutation-equivariant 設計。

訓練分為兩階段。Stage 1 凍結以 Qwen2-VL 權重初始化的 semantic expert,從隨機初始化開始在大規模 3D-annotated 資料上訓練 geometric expert,使用 visual geometry (VG) loss $\mathcal{L}_{VG} = \mathcal{L}_{\text{points}} + \lambda_{\text{cam}} \mathcal{L}_{\text{cam}} + \lambda_{\text{normal}} \mathcal{L}_{\text{normal}}$,並先以 $224 \times 224$ 訓練 100K 步、再以 $518 \times 518$ 訓練 20K 步。Stage 2 進行 joint-training:作者比較了 CE Loss Only、CE + CE 與 VG + CE 三種策略,雖然 VG + CE 效果最好但需要大量 3D 標註資料,因此主要的 G2VLM 採用 CE Loss Only(凍結 geometric expert、僅以 cross-entropy 微調 semantic expert),既保留 geometric expert 的 3D 重建能力,又能用大量易取得的 in-the-wild 影片擴展 spatial reasoning。針對純 spatial reasoning 任務,則額外提供以 CE + CE 訓練的變體 G2VLM-SR。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: N RGB images (I_i)_{i=1..N}, each I_i in R^{3 x H x W}
       + text query tokens                              (H,W = 224 or 518)
   │
   ├──[B, N, 3, H, W]→ DINOv2 Encoder        ──→ [B, N, C_v, d]   (geometric tokens)
   │                                              │
   ├──[B, N, 3, H, W]→ Qwen2 Vision Encoder  ──→ [B, N, C_v', d]  (semantic vision tokens)
   │                                                              │
   └──[B, L_text]   → Text Tokenizer        ──→ [B, L_text, d]   (semantic text tokens)
                                                                 │
                                                                 ▼
   ┌──────────────────── MoT Transformer Block (× num_layers) ────────────────────┐
   │                                                                              │
   │   Geometric Expert                              Semantic Expert              │
   │   ─────────────────                             ─────────────────            │
   │   QKV_geo:  [B, N·C_v, d] ──┐               ┌── QKV_sem:                     │
   │                             │               │     [B, N·C_v' + L_text, d]    │
   │                             ▼               ▼                                │
   │           ┌─── Shared Multi-Modal Self-Attention ───┐                        │
   │           │  concat: [B, N·C_v + N·C_v' + L_text, d]│                        │
   │           │  global attention over all tokens       │                        │
   │           └────────────────────┬────────────────────┘                        │
   │                                │                                             │
   │                  ┌─────────────┴─────────────┐                               │
   │                  ▼                           ▼                               │
   │   FFN_geo: [B, N·C_v, d]         FFN_sem: [B, N·C_v' + L_text, d]            │
   └──────────────────────────────────────────────────────────────────────────────┘
                  │                           │
                  ▼                           ▼
   geometric hidden states          semantic hidden states
   h_i in R^{C x d}                 [B, N·C_v' + L_text, d]
   reshape: [B, N, C_v, d]                    │
                  │                           ▼
                  ▼                  Text De-Tokenizer ──→ answer tokens [B, L_out]
   ┌──── Geometry Heads ────┐
   │ (lightweight Transformer decoders)
   │
   ├─ Local Point Head ──→ X_i in R^{H x W x 3}     batched: [B, N, H, W, 3]
   ├─ Camera Head      ──→ T_i in SE(3) ⊂ R^{4x4}   batched: [B, N, 4, 4]
   └─ Global Point Head ─→ [B, N, H, W, 3]          (training stabilization)

Notation:
  B       = batch size
  N       = frames per scene (2–24 sampled in training)
  H, W    = 224 (stage 1a) or 518 (stage 1b); aspect ratio in [0.5, 1.0]
  C_v     = #DINOv2 patch tokens per image (= ?, depends on patch size; paper does not specify)
  C_v'    = #Qwen2-VL vision tokens per image (?, dynamic resolution; paper does not specify)
  d       = hidden dimension shared across experts (?, paper does not specify)
  L_text  = text token length
  L_out   = generated answer length
```

### 5.3 Per-Module Breakdown

#### 5.3.1 DINOv2 Vision Encoder (Geometric Path)

**Function:** 將每張輸入影像編碼為 low-level、3D-aware 的 patch token 序列,作為 geometric perception expert 的視覺輸入。

**Input:**
- Name: 多視角 RGB 影像 $(I_i)_{i=1}^{N}$
- Shape: `[B, N, 3, H, W]`,其中 $H, W \in \{224, 518\}$
- Source: 訓練資料集中隨機取樣的 2–24 張同一場景影像

**Output:**
- Name: geometric visual tokens
- Shape: `[B, N, C_v, d]`
- Consumer: Geometric Perception Expert(§5.3.3)

**Processing:**

每張影像獨立通過 DINOv2 backbone,被切分成不重疊的 patch 並映射到 $d$ 維 token 序列。Stage 1a 使用 $224 \times 224$ 解析度、stage 1b 使用 $518 \times 518$ 並隨機 aspect ratio 介於 $0.5$–$1.0$。論文選用 DINOv2 而非 CLIP/SigLIP 等 language-contrastive encoder,理由在 §4.3 ablation 中得到驗證:DINOv2 對 low-level vision 任務(如 3D reconstruction)更為合適,且其特徵能補充 multimodal vision encoder,提升下游 spatial reasoning 表現。

**Key Formulas:**

(此模組為標準 DINOv2 forward pass,論文未提供新的公式。)

**Implementation Details:**

論文未指定 DINOv2 的具體版本(如 base/large/giant)、patch size 與輸出 hidden dimension $d$,故 $C_v$ 與 $d$ 標為 `?`。Encoder 在 stage 1 期間隨 geometric expert 一起更新,在 stage 2 中與 geometric expert 一同被凍結(主模型 G2VLM 的 CE Loss Only 設定)。

#### 5.3.2 Qwen2 Vision Encoder + Text Tokenizer (Semantic Path)

**Function:** 將輸入影像與文字 query 分別轉成 semantic expert 可消化的 token 序列,並提供 Multimodal Rotary Position Embedding (M-RoPE) 所需的位置資訊。

**Input:**
- Name: 多視角 RGB 影像 $(I_i)_{i=1}^{N}$ + 文字 query
- Shape: 影像 `[B, N, 3, H, W]`、文字 `[B, L_text]`
- Source: 同 §5.3.1 的影像;文字來自 user query

**Output:**
- Name: semantic visual tokens、semantic text tokens
- Shape: `[B, N, C_v', d]` 與 `[B, L_text, d]`
- Consumer: Semantic Perception Expert(§5.3.4)

**Processing:**

Qwen2 vision encoder 支援 native dynamic resolution,因此 $C_v'$ 會隨輸入解析度動態變化。Tokenized 的影像與文字 token 在進入 semantic expert 之前已套用 M-RoPE,以保留時序、影像位置與 inter-frame 關係。Text tokenizer 沿用 Qwen2-VL-2B 的詞表。

**Key Formulas:**

(沿用 Qwen2-VL 既有設計,論文未提供新公式。)

**Implementation Details:**

Semantic 路徑的 vision encoder 與 tokenizer 直接繼承 Qwen2-VL-2B 預訓練權重。論文強調此設計可以「直接 leverage off-the-shelf pretrained VLM」,日後可替換為更強的 VLM。$C_v'$、$d$ 等具體維度論文未明寫。

#### 5.3.3 Geometric Perception Expert

**Function:** 以 transformer 將 DINOv2 patch token 進一步推理出 3D-aware 的 hidden states,並透過 shared self-attention 與 semantic expert 互通資訊。

**Input:**
- Name: geometric visual tokens
- Shape: `[B, N, C_v, d]`(進入 attention 前 reshape 為 `[B, N·C_v, d]`)
- Source: DINOv2 Vision Encoder(§5.3.1)

**Output:**
- Name: geometric hidden states $h_i \in \mathbb{R}^{C \times d}$
- Shape: `[B, N, C_v, d]`(此處 $C = C_v$)
- Consumer: Geometry Heads(§5.3.7)

**Processing:**

Geometric expert 為一個多層 transformer,每一層包含獨立的 QKV projection 與 FFN,但其 attention 計算與 semantic expert 共享(§5.3.5)。為了縮小與 semantic expert 之間的表徵差距並便於 scaling,作者刻意簡化了傳統 visual geometry 模型的若干設計:不使用 register tokens、僅使用 global attention(不採 VGGT/$\pi^3$ 的 alternating frame/global attention),並移除 VGGT 的 camera token,改用 $\pi^3$ 的 permutation-equivariant 設計,使所有影像 token 的處理方式一致、不需要特殊 prior。Ablation(§4.3)顯示 global attention 在 LLM-compatible 框架下優於 frame attention 與 mixed attention,且能進一步提升 spatial reasoning 表現。

**Key Formulas:**

$$
f\left((h_i)_{i=1}^{N}\right) = \left(T_i, X_i\right)_{i=1}^{N}
$$

(將 hidden states 對應到每張影像的 camera pose 與 point map;對應論文 Eq. 1。)

**Implementation Details:**

層數、attention head 數與 FFN 維度論文未明寫。Stage 1 從零開始訓練(包含 DINOv2 encoder 上方的這個 transformer 與下方的 geometry heads),AdamW、cosine scheduler、bfloat16、gradient checkpointing、grad clipping 1.0;先以 $\text{lr}=2\times 10^{-4}$ 訓練 100K 步($224^2$,32× A800,7 天),再以 $\text{lr}=5\times 10^{-4}$ 訓練 20K 步($518^2$,64× A800,3 天)。

#### 5.3.4 Semantic Perception Expert

**Function:** 以基於 Qwen2-VL-2B 的 transformer 處理視覺與文字 token,並透過 shared self-attention 取用 geometric expert 的 3D-aware 特徵,完成 multimodal understanding 與 spatial reasoning。

**Input:**
- Name: semantic visual tokens + semantic text tokens
- Shape: 串接後 `[B, N·C_v' + L_text, d]`
- Source: Qwen2 Vision Encoder + Text Tokenizer(§5.3.2)

**Output:**
- Name: semantic hidden states
- Shape: `[B, N·C_v' + L_text, d]`(以及自回歸生成階段的 `[B, L_out, d]`)
- Consumer: Text De-Tokenizer(§5.3.6)

**Processing:**

Semantic expert 為一個多層 transformer,每層擁有自己的 QKV projection 與 FFN,但 attention 與 geometric expert 共享。M-RoPE 提供位置資訊。Stage 1 完全凍結;stage 2 解凍並以 cross-entropy(CE)loss 微調(主模型 G2VLM 的 CE Loss Only)。當 G2VLM-SR 變體採 CE + CE 設定時,geometric expert 也會由 CE loss 反向傳播微調,但 geometric heads 在 stage 2 一律不再 backprop visual geometry loss(VG + CE 變體例外,但因擴展性問題不被選為主模型)。

**Key Formulas:**

主要訓練目標為標準的 next-token cross-entropy:

$$
\mathcal{L}_{\text{CE}} = -\sum_{t} \log p_\theta(y_t \mid y_{<t}, \text{visual context})
$$

(論文僅以文字描述為「standard language modeling loss (cross-entropy)」,未列出顯式公式;此處依語意補上標準形式以利閱讀。)

**Implementation Details:**

初始化於 Qwen2-VL-2B 權重。Stage 2 使用 AdamW、$\text{lr}=2\times 10^{-5}$、16K 步、64× A800、3 天、bfloat16、gradient checkpointing、grad clipping 1.0。Joint-training 比較了三種策略(§3.3):CE Loss Only(主 G2VLM)、CE + CE(G2VLM-SR)、VG + CE(實驗最佳但 scaling 受限,故未採納為主模型)。

#### 5.3.5 Shared Multi-Modal Self-Attention (MoT Layer)

**Function:** 在每一層 transformer block 中,讓兩個 expert 的 token 進入同一個 multi-head self-attention 計算,實現 geometric 與 semantic 表徵的雙向交互。

**Input:**
- Name: 兩個 expert 各自投影出的 $Q, K, V$
- Shape: 串接後 `[B, N·C_v + N·C_v' + L_text, d]`
- Source: Geometric Expert 的 QKV projection(§5.3.3)、Semantic Expert 的 QKV projection(§5.3.4)

**Output:**
- Name: 經 attention 處理後的 token 表徵
- Shape: 與輸入相同 `[B, N·C_v + N·C_v' + L_text, d]`,接著按來源拆分回各 expert 的 FFN
- Consumer: 兩個 expert 各自的 FFN(同層後段)

**Processing:**

依 MoT 設計(Liang et al.; Bagel),attention 是兩個 expert 之間唯一共享的計算;QKV projection 與 FFN 仍各自獨立。所有 geometric tokens、semantic visual tokens 與 text tokens 被串接成一個序列後做 global self-attention,使 geometric token 可以從 semantic context 取得 high-level 提示,語意 token 也能 in-context 地讀取 3D-aware 特徵以支援 interleaved reasoning(例如先預測 3D 結構、再用該結構回答空間關係問題)。

**Key Formulas:**

$$
\text{Attn}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^\top}{\sqrt{d_k}}\right) V,
\quad Q = [Q_{\text{geo}}; Q_{\text{sem}}],\ K = [K_{\text{geo}}; K_{\text{sem}}],\ V = [V_{\text{geo}}; V_{\text{sem}}]
$$

(論文以文字描述「shared multi-modal self attention」,未列出顯式式子;此處以標準 multi-head attention 形式呈現拼接結構以利理解。)

**Implementation Details:**

論文未明寫 attention head 數、是否使用 FlashAttention 等具體實作。可以推測使用 bfloat16 與 gradient checkpointing(與整體訓練設定一致)。Ablation 顯示 global mask 在此共享層中表現最佳。

#### 5.3.6 Geometry Heads (Local Point / Camera / Global Point)

**Function:** 將 geometric expert 的 hidden states $h_i$ 解碼成 task-specific 的 3D 預測:相機座標系下的 pixel-aligned point map、camera pose,以及全域點雲(用於穩定訓練)。

**Input:**
- Name: geometric hidden states $(h_i)_{i=1}^{N}$
- Shape: `[B, N, C_v, d]`
- Source: Geometric Perception Expert(§5.3.3)

**Output:**
- Name / Shape:
  - Local Point Head $\to$ point map $X_i \in \mathbb{R}^{H \times W \times 3}$,batched `[B, N, H, W, 3]`
  - Camera Head $\to$ pose $T_i \in \text{SE}(3) \subset \mathbb{R}^{4 \times 4}$,batched `[B, N, 4, 4]`
  - Global Point Head $\to$ 全域座標系點雲 `[B, N, H, W, 3]`(僅用於穩定訓練)
- Consumer: 下游 evaluation(monocular depth、point map、camera pose),以及空間推理時提供給 semantic expert 的 in-context 3D 特徵

**Processing:**

三個 head 都被設計為 lightweight transformer decoder,各自從 geometric hidden states 解出對應目標。Local Point Head 預測 camera 坐標系下的 per-pixel 3D 點,Camera Head 預測每張影像的 SE(3) pose,Global Point Head 在訓練時並行預測同一場景的全域點雲以增強 supervision 訊號、穩定優化過程。

**Key Formulas:**

Visual Geometry 總損失(對應論文 Eq. 2):

$$
\mathcal{L}_{VG} = \mathcal{L}_{\text{points}} + \lambda_{\text{cam}} \mathcal{L}_{\text{cam}} + \lambda_{\text{normal}} \mathcal{L}_{\text{normal}}
$$

點雲重建損失,使用 optimal scale $s^*$(對應 Eq. 3):

$$
\mathcal{L}_{\text{points}} = \frac{1}{3 N H W} \sum_{i=1}^{N} \sum_{j=1}^{H \times W} \frac{1}{z_{i,j}} \left\| s^{*} \hat{x}_{i,j} - x_{i,j} \right\|_{1},
\quad s^{*} = \arg\min_{s} \sum_{i,j} \frac{1}{z_{i,j}} \left\| s \hat{x}_{i,j} - x_{i,j} \right\|_{1}
$$

相機損失對所有有序 pair $i \neq j$ 平均(Eq. 4–6):

$$
\mathcal{L}_{\text{cam}} = \frac{1}{N(N-1)} \sum_{i \neq j} \left( \mathcal{L}_{\text{rot}}(i,j) + \lambda_{\text{trans}} \mathcal{L}_{\text{trans}}(i,j) \right)
$$

$$
\mathcal{L}_{\text{rot}}(i,j) = \arccos\!\left( \frac{ \mathrm{Tr}\!\left( (R_{i \leftarrow j})^{\top} \hat{R}_{i \leftarrow j} \right) - 1 }{ 2 } \right),
\qquad
\mathcal{L}_{\text{trans}}(i,j) = H_{\delta}\!\left( s^{*} \hat{t}_{i \leftarrow j} - t_{i \leftarrow j} \right)
$$

法向量損失(Eq. 7):

$$
\mathcal{L}_{\text{normal}} = \sum_{i=1}^{N} \sum_{j=1}^{H \times W} \arccos\!\left( \hat{n}_{i,j} \cdot n_{i,j} \right)
$$

**Implementation Details:**

Heads 為 lightweight transformer decoder,具體層數、隱藏維度與 head 數論文未指定。$z_{i,j}$ 為 ground-truth depth(GT $x_{i,j}$ 的 z 分量),由 MoGe 提出的 ROE solver 求得;$\lambda_{\text{cam}}, \lambda_{\text{normal}}, \lambda_{\text{trans}}$ 為 pre-defined 超參數,具體數值論文未列出。$H_{\delta}$ 為 Huber loss。Stage 2 中,Geometry Heads 在主模型 G2VLM(CE Loss Only)與 G2VLM-SR(CE + CE)中皆不再接受 VG loss 的監督,僅 VG + CE 變體會持續以 VG loss 微調以保留 3D 重建能力。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| ScanNet | Indoor RGB-D scenes (geometry + spatial reasoning annotations) | the paper does not specify | train (geometry pretrain + joint-train ablation) |
| Co3Dv2 | Object-centric multi-view | >1000 test sequences | train + test (camera pose) |
| BlendedMVS | Multi-view stereo | the paper does not specify | train (geometry) |
| DL3DV | Real-world scenes | the paper does not specify | train (geometry) |
| MegaDepth | Internet photo depth | the paper does not specify | train (geometry) |
| WildRGBD | RGB-D objects in the wild | the paper does not specify | train (geometry) |
| TartanAir | Synthetic SLAM | the paper does not specify | train (geometry) |
| Taskonomy | Indoor scenes | the paper does not specify | train (geometry) |
| ARKitScenes | Real-world indoor RGB-D | the paper does not specify | train (geometry) |
| HyperSim | Photorealistic synthetic indoor | the paper does not specify | train (geometry) |
| Habitat | Synthetic embodied scenes | the paper does not specify | train (geometry) |
| ScanNet++ | High-fidelity indoor scenes | the paper does not specify | train (geometry) |
| GTA-SFM | Synthetic outdoor | the paper does not specify | train (geometry) |
| MatrixCity | City-scale rendering | the paper does not specify | train (geometry) |
| Aria Synthetic Environments | Egocentric synthetic | the paper does not specify | train (geometry) |
| Map-free | Visual relocalization | the paper does not specify | train (geometry) |
| Internal synthetic indoor | Indoor synthetic | the paper does not specify | train (geometry) |
| SPAR-7M | Spatial reasoning instruction data | 7M samples (implied by name) | train (joint-training) |
| OmniSpatial (train split) | Spatial reasoning | the paper does not specify | train (joint-training) |
| MindCube (train split) | Spatial mental modeling | the paper does not specify | train (joint-training) |
| OST-Bench (train split) | Online spatio-temporal scene understanding | the paper does not specify | train (joint-training) |
| LLaVA-OneVision | General VQA | the paper does not specify | train (joint-training) |
| Sintel | Monocular depth (synthetic, dynamic) | the paper does not specify | test (depth) |
| NYU-v2 | Monocular indoor depth | the paper does not specify | test (depth) |
| 7-Scenes | Indoor RGB-D point map | keyframes sampled with stride 40 | test (point map) |
| ETH3D | Multi-view stereo benchmark | every 5th image sampled | test (point map) |
| SPAR-Bench | Spatial reasoning (Low / Medium / High) | full + tiny (50 q/task) | test |
| OmniSpatial (SI, PT 子集) | Spatial reasoning | two main categories evaluated | test |
| MindCube | Spatial mental modeling | the paper does not specify | test |
| OST-Bench∗ | Online spatio-temporal QA | subset with $\le 15$ input frames | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Abs Rel | Absolute relative depth error (lower better) | yes |
| $\delta < 1.25$ | Depth prediction accuracy at threshold 1.25 (higher better) | no |
| Acc. | Point-map accuracy after Sim(3)+ICP alignment (lower better) | yes |
| Comp. | Point-map completion (lower better) | no |
| RRA@30 | Relative Rotation Accuracy at 30° (higher better) | no |
| RTA@30 | Relative Translation Accuracy at 30° (higher better) | no |
| AUC@30 | Area Under Curve of $\min(\text{RRA},\text{RTA})$ vs threshold (higher better) | yes |
| SPAR-Bench Avg / Low / Medium / High | Mean accuracy across spatial reasoning sub-tasks | yes |
| MindCube Avg (Rotation, Among, Around) | Spatial mental-modeling accuracy | yes |
| OST-Bench∗ Avg (A. State, A. Info, AO.) | Online spatio-temporal scene QA accuracy | no |
| OmniSpatial∗ Avg (SI, PT) | Spatial Interaction + Perspective Taking accuracy | no |

### 6.3 Training and Inference Settings

兩階段訓練皆使用 AdamW + cosine scheduler、bfloat16 精度、gradient checkpointing,並以 1.0 為 gradient norm clipping 閾值 (§3.3 與 Appendix B)。

Stage 1 (geometric perception expert pretraining,凍結 semantic expert,從零初始化 geometry expert):
- Sub-stage 1: 解析度固定 224×224,lr = 2e-4,100K iterations,32× A800 GPUs,約 7 天。
- Sub-stage 2: 解析度提升至 518×518、aspect ratio 隨機介於 0.5–1.0,lr = 5e-4,再訓練 20K iterations,64× A800 GPUs,約 3 天。
- 每個 batch 從一個隨機場景中隨機抽取 2–24 frames (與 VGGT 一致)。
- VG loss 權重: $\lambda_{\text{normal}} = 1.0$, $\lambda_{\text{cam}} = 0.2$, $\lambda_{\text{trans}} = 200.0$;local point map alignment resolution = 4096;對 loss > 10 進行 clip 並平滑為 0 以避免 noisy 3D annotation 造成的訓練不穩。

Stage 2 (joint training,解凍 semantic expert): AdamW + cosine scheduler,lr = 2e-5,16K iterations,64× A800 GPUs,約 3 天,不再 clip loss。預設策略為 **CE Loss Only** (凍結 geometry expert);另外訓練一個變體 G2VLM-SR 採用 **CE + CE Loss** (geometry expert 也以 CE 微調) 以強化 spatial reasoning。

Inference: global point head 僅用於穩定訓練,推論時不使用 (Appendix A);其餘 settings (batch size、frame 數、generation 參數) the paper does not specify。

### 6.4 Main Results

Visual Geometry (Sintel depth, ETH3D point, Co3Dv2 pose; Table 1a):

| Method | Sintel Abs Rel ↓ | ETH3D Acc. ↓ | Co3Dv2 AUC@30 ↑ | Notes |
|---|---|---|---|---|
| Fast3R | 0.544 | 0.832 | 73.43 | baseline |
| CUT3R | 0.418 | 0.617 | 75.82 | baseline |
| FLARE | 0.606 | 0.464 | 73.99 | baseline |
| VGGT | 0.335 | 0.280 | 88.59 | SoTA, 用 camera token |
| π³ | **0.277** | **0.194** | 88.41 | SoTA, fine-tune from pretrained |
| **G2VLM (Ours)** | **0.297** | 0.414 | 74.81 | **無 camera token、無 fine-tune from VGGT/π³ 權重** |

Spatial Understanding & Reasoning (Table 1b,選取 headline 數字):

| Method | SPAR-Bench Avg | MindCube Avg | OST-Bench∗ Avg | OmniSpatial∗ Avg |
|---|---|---|---|---|
| GPT-4o | 36.39 | 38.81 | 37.58 | 46.16 |
| Claude-4-Sonnet | – | 44.75 | – | – |
| Qwen2.5-VL-72B | 39.40 | 37.25 | 31.09 | 43.03 |
| LLaVA-OneVision-7B | 31.20 | 47.43 | 37.14 | 38.32 |
| Spatial-MLLM-7B | 32.15 | 32.06 | 20.97 | 43.67 |
| VLM3R-7B | 43.21 | 42.09 | – | 44.21 |
| Qwen2-VL-2B (base) | 24.60 | 37.83 | 17.94 | 41.18 |
| **G2VLM-2B (Ours)** | 41.66 | 38.83 | 17.18 | 44.92 |
| **G2VLM-SR-2B (Ours)** | **54.87** | **48.33** | 31.42 | **49.20** |

G2VLM-SR 在 SPAR-Bench 上以 2B 參數超過 GPT-4o 達 18.48 分,並在 SPAR-Bench / MindCube / OmniSpatial 上拿下所有對手中的最佳;OST-Bench 仍輸給 Qwen2.5-VL-72B,作者歸因為線上時空理解需要更大的知識儲存。

### 6.5 Ablation Studies

1. **Joint-training loss strategy** (Figure 4, on ScanNet): 比較 CE-only / CE+CE / VG+CE 三種監督。VG+CE 同時提升 geometry 與 spatial reasoning,但需要昂貴的 3D annotation,因此主模型採 CE-only,並另以 CE+CE 訓練 G2VLM-SR — 這是有診斷價值的實驗,直接驗證「geometry supervision 是否有助 reasoning」。
2. **Encoder design: single vs. dual** (Figure 6a): single CLIP encoder vs. dual (DINO for geometry + CLIP for VLM)。Dual encoder 在兩種任務上都最佳,且作者特別指出 DINO 對 spatial reasoning 也有實質幫助,而非只惠及 low-level geometry — 為核心架構選擇提供直接證據。
3. **Attention mechanism** (Figure 6b, Table 2): frame-only / mixed / global attention。Global attention 在 geometry training loss 與 SPAR-Bench (52.34 → 53.64 → 54.87) 上同步遞增,作者用此論證「geometry 進步 ⇒ reasoning 進步」的 positive interplay — 這是論文主要因果論點的關鍵診斷。
4. **Impact of geometry pretraining** (Table 2): 與只在 spatial 資料上 finetune 的 Qwen2-VL-2B (48.93) 相比,G2VLM-SR (54.87) 領先 5.94 分,證明 geometry expert 並非可被同等規模 finetune 取代。
5. **Sanity-check 標記**: Qwen2-VL-2B (base) vs. (finetuned) 主要為 sanity check,確認 spatial 訓練資料本身有效;但 frame-vs-mixed-vs-global 與 single-vs-dual encoder 都屬於診斷性 ablation,設計合理。整體 ablation 缺一項是「移除 normal loss / camera loss / global point head」對 geometry 的個別影響,論文未提供。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — geometry 端比較 VGGT 與 π³ (Table 1a),reasoning 端比較 GPT-4o、Claude-3.7/4-Sonnet、Qwen2.5-VL-72B、VLM3R-7B (Table 1b)。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 跨 Sintel / NYU-v2 / 7-Scenes / ETH3D / Co3Dv2 / SPAR-Bench / MindCube / OST-Bench / OmniSpatial 共九個資料集。
- [covered] Has ablations that diagnose the new components (not just sanity checks) — encoder design、attention mechanism、joint-training loss strategy 三項皆針對論文新提出的 dual-expert 與訓練策略。
- [partial] Has a scaling study (size, length, or compute) — 結論段提到「leave the scaling of our model to future work」;唯一接近 scaling 的是與 7B/72B baselines 的橫向比較 (G2VLM 僅 2B),並無自家模型的多尺寸曲線。
- [missing] Has an efficiency / wall-clock comparison — 論文僅報告自家訓練耗時 (32/64 A800 × 7+3 天),未對 inference latency / FLOPs / throughput 與 VGGT、π³、其他 VLM 做橫向比較。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有表格皆為單一 run 數值,無 std 或多 seed。
- [partial] Releases code / weights / data sufficient for reproducibility — 首頁標示 Project Page 與 GitHub 連結,但 the paper does not specify 是否釋出權重、訓練資料清單細節,且部分訓練資料 (internal synthetic indoor) 為內部資產。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 「首個統一 spatial 3D reconstruction 與 spatial understanding 的 VLM」(§1, page 2)** — Supported as a positioning claim:Table 1a 與 Table 1b 顯示同一個模型同時跑 geometry 與 reasoning 任務,這是 VLM-3R / Spatial-MLLM 等 frozen-encoder 設計沒做到的層級。但「first unified」是相對而言,Bagel 等 MoT 工作已經有跨任務 unification 的範式。
- **C2: 「MoT 的 dual-expert + shared self-attention 架構」(§1, §3.1, page 2–4)** — Partially supported:架構本身可運作,且 Figure 6a 證實 dual encoder 比 single encoder 好,但「shared self-attention 帶來 mutual improvement」並未直接消融——例如沒有對照「兩 expert 完全獨立、不共享 attention」的 baseline。
- **C3: 「3D 重建達到 SOTA-comparable」(§1, §4.1, page 2, 6)** — Overclaimed:depth 上確實接近甚至小勝 VGGT,但 ETH3D Acc. 0.414 對 VGGT 的 0.28、Co3Dv2 AUC@30 為 74.81 對 VGGT 的 88.59,差距達 13–47% 相對誤差,難以稱為 comparable (Table 1a, page 7)。
- **C4: 「在 SPAR-Bench、MindCube、OmniSpatial 上達 best」(§1, §4.2, page 2, 6)** — Supported:Table 1b 在三個 benchmark 上 G2VLM-SR-2B 都是 open-source / spatial expert 中的最佳,且超越 GPT-4o 18.48 點的數字確實成立。OST-Bench 則確實如作者承認被 72B 模型超越。
- **C5: 「geometry 進步同步帶動 reasoning 進步 (positive interplay)」(§4.3, page 8)** — Partially supported:Table 2 的三個 attention variant 確有單調關係,但樣本量太小且為 confounded variables;這只是 suggestive evidence,而非因果證明。
- **C6: 「以 abundant 2D 多視角資料 scaling 即可,不必依賴 3D 標註」(§1, §3.3, page 2, 5)** — Partially supported:第二階段 freeze geometry expert 確實只用 cross-entropy 在 spatial-understanding 資料上訓練,符合此主張;但第一階段仍重度依賴 17 個 3D-annotated dataset,所以「擺脫 3D 標註稀缺瓶頸」只成立於擴增 reasoning 能力,而非整體訓練。

### 7.2 Fundamental Limitations of the Method

**Frozen geometry expert 與 reasoning supervision 的單向耦合。** 主模型採用 CE Loss Only 策略,意味著 spatial reasoning 任務的 gradient 永遠不會回傳到 geometry expert。這在 scalability 上是優勢,但也固化了 geometry 表徵的能力上限:當下游 reasoning 任務需要的幾何抽象 (例如 affordance、object-level 關係) 不存在於 pretraining 的 depth/point/pose 監督裡時,模型無法 in-context 重塑 geometry features。作者自己在 ablation 中承認 VG+CE 是最佳設計,但因 scalability 退而求其次,這個 trade-off 是架構層級的本質缺陷。

**Camera-token-free 與 permutation-equivariant 設計的精度代價。** 為了與 LLM 框架對齊,G2VLM 主動放棄了 VGGT 的 camera token 與 alternating-attention,僅保留 global attention。Table 1a 上 Co3Dv2 AUC@30 落後 VGGT 13.78 點,顯示這個設計選擇對 camera pose 估計造成實質損失。這不是訓練細節能彌補的,而是架構簡化所付出的固定成本——若要追回精度,就得重新引入 camera 專屬 inductive bias,但那會破壞 dual-expert 的對稱性。

**「Native geometry expert」對比「frozen encoder bolt-on」的 confound 無法在當前實驗下分離。** G2VLM 同時更動了三件事:(1) 用 native trained expert 取代 frozen VGGT、(2) 改用 Qwen2-VL-2B base、(3) 使用 SPAR-7M 等更大 spatial 訓練資料。Table 1b 雖然優於 VLM-3R-7B,但缺乏「同 base model、同訓練資料、僅換 frozen vs. native」的 ablation,因此「native 才是關鍵」這個架構級主張在現有實驗下是 underdetermined 的。

### 7.3 Citations Worth Tracking

- **VGGT (Wang et al. 2025) [57]** — G2VLM 在 geometry 上的最強對手與 baseline;讀者要評估「unified 是否值得」的代價,必須直接閱讀 VGGT 的 alternating-attention 與 camera token 設計細節。
- **$\pi^3$ (Wang et al. 2025) [67]** — G2VLM 直接複用其 permutation-equivariant 設計、normal loss 與 geometry head 架構;理解這篇可釐清 G2VLM 哪些是繼承、哪些是新創。
- **Bagel (Deng et al. 2025) [18]** — 啟發 G2VLM 的 MoT-based unification 思路 (understanding + generation);若想評估 MoT 在 cross-task unification 上的一般性,Bagel 是直接對照。
- **VLM-3R (Fan et al. 2025) [21]** — 與 G2VLM 設計哲學最直接對立的 concurrent work (frozen geometry encoder bolt-on);追蹤這條 thread 才能判斷「native expert vs. frozen encoder」的長期勝負。
- **MoGe (Wang et al. 2025) [61]** — 提供 G2VLM 採用的 optimal-scale point loss 與 ROE solver;對閱讀第 (3)–(7) 式 loss formulation 不可或缺。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在固定 base VLM 與訓練資料的條件下,單純把 frozen VGGT encoder 換成 native trained geometric expert,SPAR-Bench 究竟能提升多少?亦即「native vs. bolt-on」的純架構增益尚未隔離。
- [ ] G2VLM-SR 在 visual geometry tasks (depth、point、pose) 上是否相對 G2VLM 退步?論文僅報告 G2VLM 的 geometry 結果,但 SR 版本經 cross-entropy 微調後,geometry 能力是否被 catastrophic forgetting 影響並未測量。
- [ ] 為何 G2VLM-2B (非 SR) 在 OST-Bench 上 (24.60) 與 OmniSpatial 上 (44.13) 反而比 base Qwen2-VL-2B (22.59、43.90) 改善有限甚至落後 SR 版本許多?直接訓練 geometry expert 對哪一類 spatial tasks 是負遷移?
- [ ] Camera pose 在 Co3Dv2 AUC@30 上落後 VGGT 13.78 點的具體原因是「無 camera token」還是「permutation-equivariant」?哪一個是更關鍵的精度殺手?
- [ ] 在 SPAR-Bench 訓練集已被納入 joint-training data 的情況下,SPAR-Bench 上的 SOTA 結果有多少是 in-domain generalization、多少是真正的 spatial intelligence?在 held-out 的 spatial benchmark (例如 MMSI-Bench、EmbSpatial-Bench) 上的成績如何?
- [ ] interleaved reasoning 的實際 token-level 行為長什麼樣?Figure 1 的 qualitative example 顯示模型「直接預測 3D」再回答,但論文未量化此 chain 對最終答案的貢獻——若關掉 interleaved 路徑,僅靠 hidden state 流動,效果會掉多少?
- [ ] 模型 scaling 到 7B / 13B 時,作者提到的 training instability 究竟是 loss spikes、divergence 還是 reasoning expert collapse?未來 scaling 受限的具體 failure mode 是什麼?

### 8.2 Improvement Directions

1. **加入「frozen-encoder vs. native-expert」的 controlled ablation** — 改動成本低 (重用 VLM-3R 的 frozen VGGT 設定即可),可直接回答 C2 與 §7.2 提出的 confound 問題,讓「native」主張站得住腳。
2. **報告 G2VLM-SR 在 geometry tasks 上的退化幅度,並嘗試 LoRA/Adapter 方式微調 semantic expert** — 若 freeze 整個 geometric expert 仍導致 SR 版本 geometry 能力下降,則 LoRA 可平衡 reasoning 增益與 geometry 保留;這也直接對應 §7.2 第一段的根本限制。
3. **重新引入 camera-pose 專屬 inductive bias 但保留 LLM-compatible attention mask** — 例如把 camera token 設計成可選的 prompt token,僅在需要 pose 預測時注入。理由是 Table 1a 顯示 pose 落後最嚴重 (13.78 點),而 §3.1 自陳此設計是為「scalable」而砍掉,但代價可量化。
4. **以 curriculum 設計局部開放 VG + CE joint training** — 既然作者承認 VG+CE 表現最佳,只是 3D 標註資料 scalability 不夠,可採「前期 VG+CE,後期 CE Only」的 curriculum,以小量 3D-annotated data 持續校準 geometry expert,理論上能取得兩種策略的中間最佳點。
5. **在 held-out spatial benchmark (MMSI-Bench、EmbSpatial-Bench) 上補測** — 直接回應 §8.1 的訓練/評估資料污染疑慮;feasibility 中等,需取得對應評估資料。
6. **以 geometry-quality scaling sweep 取代 attention-variant ablation 來證 positive interplay** — 在固定 attention 下,改變 pretraining iterations 或 dataset 規模產生不同 geometry quality 的 checkpoints,再評估 SPAR-Bench;這比「三 attention variant」更能建立 geometry → reasoning 的因果關係。
