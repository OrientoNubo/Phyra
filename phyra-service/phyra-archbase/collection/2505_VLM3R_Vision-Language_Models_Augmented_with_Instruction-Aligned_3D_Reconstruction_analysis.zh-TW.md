<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# VLM-3R — VLM-3R: Vision-Language Models Augmented with Instruction-Aligned 3D Reconstruction

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | VLM-3R |
| Paper full title | VLM-3R: Vision-Language Models Augmented with Instruction-Aligned 3D Reconstruction |
| arXiv ID | 2505.20279 |
| Release date | 2026-04-21 |
| Conference/Journal | CVPR 2026 |
| Paper link (abs) | https://arxiv.org/abs/2505.20279 |
| PDF link | https://arxiv.org/pdf/2505.20279 |
| Code link | https://github.com/VITA-Group/VLM-3R |
| Project page | https://vlm-3r.github.io/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Zhiwen Fan | UT Austin | https://zhiwenfan.github.io/ | first author, corresponding author |
| Jian Zhang | Xiamen University (XMU) | — | co-first author |
| Renjie Li | Texas A&M University (TAMU) | — | co-author |
| Junge Zhang | UC Riverside (UCR) | — | co-author |
| Runjin Chen | UT Austin | — | co-author |
| Hezhen Hu | UT Austin | — | co-author |
| Kevin Wang | UT Austin | — | co-author |
| Peihao Wang | UT Austin | — | co-author |
| Huaizhi Qu | UNC Chapel Hill | — | co-author |
| Shijie Zhou | UCLA | — | co-author |
| Dilin Wang | Meta | — | co-author |
| Zhicheng Yan | Meta | — | co-author |
| Hongyu Xu | Meta | — | co-author |
| Justin Theiss | Meta | — | co-author |
| Tianlong Chen | UNC Chapel Hill | — | co-author |
| Jiachen Li | UC Riverside (UCR) | — | co-author |
| Zhengzhong Tu | Texas A&M University (TAMU) | — | co-author |
| Zhangyang Wang | UT Austin | https://www.ece.utexas.edu/people/faculty/atlas-wang | corresponding author, senior author |
| Rakesh Ranjan | Meta (Reality Labs) | — | corresponding author |

### 1.2 Keywords

vision-language model, 3D reconstruction, monocular video, spatial reasoning, instruction tuning, spatio-temporal benchmark, metric-scale geometry, embodied reasoning

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| CUT3R [72] (Wang et al.) | base model | 提供 metric-scale 多視角幾何重建，作為 VLM-3R 之 spatial/view token 來源編碼器。 |
| VSI-Bench [77] (Yang et al.) | predecessor | 視覺空間智能評測基準，VLM-3R 在其上比較並擴增訓練 QA 至 200K。 |
| LLaVA-3D [94] (Zhu et al.) | baseline | 需 RGB-D 與多視角輸入的 3D-LLM，VLM-3R 主張僅以單目影片即可達成。 |
| Spatial-MLLM [11] | baseline | 以 VGGT 注入幾何特徵之雙編碼器 VLM，但僅有正規化深度，缺乏 metric scale。 |
| VGGT [69] (Wang et al.) | influence | 前置多視角幾何 Transformer，論文指出其 scale-ambiguous 為改用 CUT3R 之動機。 |
| ROSS3D [68] | baseline | 結合多視角影像與深度監督的 RGB-D 空間 QA 方法，作為對照之依賴 sensor 路線。 |
| LLaVA-Next-Video [85] | base model | VLM backbone 與 two-layer projector 設計來源，VLM-3R 在其上整合 3D token。 |

## 2. Research Overview

### 2.1 Research Topic

本研究提出 VLM-3R，一個結合 3D 重建式指令微調（3D Reconstructive Instruction Tuning）的視覺語言模型框架，目標是讓 VLM 僅憑單目影片便能進行具幾何感知的空間與時間推理，無須額外的深度感測器或事先建構的 3D 地圖。研究範圍涵蓋：(1) 以 metric-scale 的多視角幾何模型 CUT3R 抽取隱式 3D tokens（spatial tokens 與 view tokens），並透過 Spatial-Visual-View Fusion 將其與 2D 視覺 token 對齊融合至語言空間；(2) 建立可擴展的 3D 視覺指令資料生成流程，從 ScanNet、ScanNet++、ARKitScenes 等資料集自動產生超過 200K 筆空間 QA 與 4,225 筆基於 Habitat 模擬器的 route planning 樣本；(3) 提出 VSTI-Bench（138.6K QA）以系統評估相機運動、相機—物件互動與物件相對位置等隨時間演變的空間關係，補足現有靜態 3D 評測之不足。

### 2.2 Domain Tags

- computer vision
- vision-language models
- 3D scene understanding
- spatial reasoning
- multimodal learning

### 2.3 Core Architectures Used

- **VLM-3R (本論文提出)**：端到端的 geometry-aware VLM 框架，整合視覺編碼器、metric-scale 幾何編碼器與 Spatial-Visual-View Fusion 模組，使 VLM 能僅憑單目影片進行空間與時間推理。
- **Spatial-Visual-View Fusion (本論文提出)**：以 cross-attention 將 spatial tokens $F'_t$ 與 view tokens $z'_t$ 注入 2D 視覺 token $H_v$，並透過 residual connection 與 two-layer projector 對齊至 LMM 輸入空間，是 VLM-3R 的核心融合機制。
- **CUT3R [72] (沿用)**：作為 metric-scale 多視角幾何重建編碼器，以 image encoder $f_{enc}$ 與 transformer decoder $f_{dec}$ 處理單目影片，輸出隱式 3D 表徵（spatial / view tokens）以及 3D point map $P_{map_t}$ 與相機姿態 $T_t$。
- **LLaVA-NeXT-Video [85] (沿用)**：作為 VLM backbone 與 two-layer projector 設計來源，VLM-3R 沿用其學習目標並整合 3D token。
- **CLIP ViT (沿用)**：作為視覺編碼器抽取 2D 視覺 token $H_v$，於訓練期間凍結。
- **LoRA [31] (沿用)**：以 rank 128、scale 256 的低秩適配方式微調 VLM 與 3D fusion attention block 及 projection layers，視覺與空間編碼器則保持凍結。
- **Habitat 模擬器 [59] (沿用)**：用於大規模生成具方向、可執行動作序列的 route planning 導航路徑，產生 4,225 筆 QA 樣本。

### 2.4 Core Argument

作者主張當前 VLM/LMM 在物理世界互動上的根本瓶頸，並非語言推理能力不足，而是缺乏直接從單目影片推得具 metric scale 之 3D 結構與相機運動的內生表徵。現有路線可分為兩類，皆有結構性缺陷：其一是仰賴深度感測器或預先建構之點雲／3D 地圖（如 LLaVA-3D、ROSS3D），使模型僅能在配備感測器的環境運作，難以利用海量單目影片資料；其二是以離線 SfM/SLAM 流程或如 VGGT 之多視角幾何 Transformer 提供幾何特徵（如 Spatial-MLLM、VG-LLM），但這些方法僅輸出正規化深度，喪失絕對尺度，導致距離估計、物體大小等 metric 級空間推理仍不準確，且多階段管線在新場景中緩慢且脆弱。作者由此推論：要讓 VLM 達到接近人類的視覺空間智能，必須具備 (a) 端到端、單目即可運作的架構、(b) 具 metric scale 的幾何先驗、以及 (c) 將相機視角資訊明確注入語言對齊空間以區分相機—物件相對運動。VLM-3R 因此選擇以 CUT3R（具 metric scale 之多視角幾何重建）作為幾何編碼器，將其產生的 spatial token 與 view token 透過 cross-attention 與 residual fusion 注入凍結的視覺語意特徵中，再以大規模 3D 重建式指令資料進行端到端對齊。此設計同時回應「為何不直接吃點雲」的疑問——因為點雲跨幀稀疏且大小不一，難以與語言 token 對齊；改採隱式 latent token 既保留幾何資訊又便於與 VLM 整合，成為解開上述瓶頸的邏輯必然解。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(260 words)

標題 "VLM-3R: Vision-Language Models Augmented with Instruction-Aligned 3D Reconstruction" 將兩個關鍵字並列：VLM 與 3D Reconstruction，並用 instruction-aligned 這個修飾詞表明兩者透過 instruction tuning 的方式對齊，而非把重建作為前置處理。Abstract 在前兩句先描述 LMM 從 2D image/video 拓展到 3D 場景的趨勢，將「human-like visual-spatial intelligence」立為遠景目標，建立一個讓讀者願意繼續讀下去的高層動機。

接著三句迅速點出現有路線的缺陷：要麼依賴 depth sensor，要麼依賴 off-the-shelf 演算法 pre-construct 3D map，兩者都限制 scalability。這裡其實已經暗示了論文方法的選位，也就是不需要 sensor、不需要預先建好的 3D map。

第四到第六句正式提出 VLM-3R，用一句話濃縮三個成分：(1) 從 monocular video 擷取 implicit 3D tokens（spatial tokens 表場景，view tokens 表 camera motion）；(2) 一條可擴展的資料生成 pipeline，產出 200K 以上的 3D reconstructive instruction-tuning QA pairs；(3) 一個新的 benchmark VSTI-Bench，含 138.6K QA pairs，五個任務專注於 evolving spatial relationships。

最後一句以 "Extensive experiments show..." 收尾，承諾 robust visual-spatial reasoning、temporal 3D context understanding，以及 monocular 3D 助理與 embodied reasoning 的應用空間。整段 Abstract 採取「目標—缺陷—方案—承諾」的標準結構，但在「方案」部分一次性披露架構、資料、benchmark 三項貢獻，為後文鋪好三條敘事主線。讀者讀完 Abstract 已能預期整篇論文會分別在 architecture、data pipeline、benchmark 三個面向展開，並且已被引導去注意 "metric-scale" 與 "without depth sensors" 這兩個關鍵差異點，為 §1 對既有方法的批判鋪陳了立場。

### 3.2 Introduction

(900 words)

Introduction 沿用「人類—機器」對比作為認知前提：第一段以 Adolph (2000) 的發展心理學引述，論述人類透過與物理世界互動形成 internal map，而當代 LLM 與 VLM 雖在文字推理與單影像理解上有進展，卻在距離估計這類最基本的 spatial 任務上失靈。這段的功能是把「spatial intelligence」確立為 VLM 的明顯短板，給後續方法存在意義。

第二段轉向技術現況的批判，分為兩條既有路線。第一條是依賴 depth sensor 的方法，缺點是只能在配備 sensor 的場景部署，且把 monocular video 的龐大資料排除在外。第二條是先用 SfM/SLAM 預建 3D map，再餵給語言模型，缺點是 multi-stage pipeline 適應新場景慢，且傳統 reconstruction 忽略 real-world scene scale，會 irreversibly 降低 VLM 的空間理解力。這段是論文選位的關鍵：作者刻意指出「scale ambiguity」會傷害 metric distance reasoning，這也是後文選擇 CUT3R 而非 VGGT/DUSt3R 的伏筆。

第三段正式引出 VLM-3R，將整篇論文的核心命題重述為「如何打造一個 end-to-end、 spatially aware 的 VLM 系統，能從 image sequence 直接解讀 scene geometry、camera movement、spatial relations，又無須 runtime reconstruction，同時整合 LLM 的常識」。接著作者用三、四句話描述方法：把 vision encoder 的 image-level semantics 與 metric-scale multiview stereo model 的 spatial information 統合進 geometry encoder，從中萃取 spatial tokens（場景）與 view tokens（camera motion），再透過 Spatial-Visual-View Fusion 與 language representation 對齊。這裡刻意強調 "metric-scale" 與 "disentangle changes in camera-object relative distance"，既呼應前段對 scale ambiguity 的批評，也預告了後文對 temporal reasoning 的處理方式。

第四段引入第二條敘事線：data curation pipeline。作者指出純架構創新不足，必須搭配大規模 instruction tuning 資料才能有顯著進展，因此提出可擴展的 3D video 資料生成流程。

第五段轉向 benchmark 動機。作者點明 VSTI-Bench 設計上的關鍵假設：場景皆為 static 3D scenes，因此所有 apparent motion 都來自 camera movement。這個設定讓 benchmark 能聚焦在「相機運動引發的 spatial relation 變化」上，並衍生五項 temporal 任務（camera displacement、camera-object relative distance、 camera-object direction、object-object frame-dependent relative position 等）。這段既為 §3 的 benchmark 章節暖身，也合理化 "static-only" 的限制。

最後一段以四點 contribution 列表收尾：(1) VLM-3R 框架本身；(2) Spatial-Visual-View Fusion 的設計；(3) 200K spatial QA pairs + 4,225 route-planning instances 的資料 pipeline；(4) 138.6K temporal QA pairs 的新 benchmark；並承諾在 VSI-Bench、VSTI-Bench、OST-Bench 上達到 SOTA，逼近使用 ground-truth depth 的 baseline。Introduction 的整體敘事流是「動機—缺陷—方案—資料—benchmark—貢獻」，每一段都精準對應後文的一個章節，使讀者在進入 §2 前已對全篇骨架了然於心。值得注意的是，作者反覆使用 "monocular video"、"end-to-end"、"metric-scale" 三個關鍵詞，明確劃出與 LLaVA-3D、SpatialVLM、Spatial-MLLM 等先前工作的差異邊界。

### 3.3 Related Work / Preliminaries

(900 words)

Related Work 切成三個小節，分別對應 LMM、spatial reasoning、3D reconstruction 三條獨立的文獻線，這個切法本身就在暗示 VLM-3R 的貢獻位於三者交集。

第一小節 "Large Multimodal Models" 從 CLIP、ALIGN 的對比預訓練開始，過渡到 Flamingo、BLIP-2 的 vision-language 解耦，再到 PaLM-E 等通用任務求解器，建立 LMM 的演進脈絡。接著鎖定 3D 擴展工作：LLaVA-3D 與 ROSS3D 用 multi-view image 加 depth supervision；SpatialRGPT 注入 monocular depth 增強區域特徵；Spatial-MLLM、VG-LLM、SpatialStack 則導入 VGGT 這類 multi-view geometry transformer，把 geometry-aware tokens 與 vision/language 特徵融合。作者在這裡丟出整篇論文最關鍵的批判：VGGT 預測的是 normalized depth，缺乏 global metric scale，導致 scale-ambiguous 的幾何表徵，無法處理 metric distance 與 object size 推理；同時許多方法仍依賴 RGB-D sensor 或 precomputed map。這條批評直接對應作者選擇 CUT3R 作為 spatial encoder 的決定，因為 CUT3R 從 monocular video 直接重建 globally aligned metric-scale 3D structure。

第二小節 "Spatial Reasoning for Visual-Spatial Intelligence" 從認知科學切入，引述 spatial schema 與 hierarchical scene encoding 的人類認知文獻，再列舉 VSI-Bench、VLM4D、Thinking in Dynamics、DynamicVerse 等 benchmark 的演進，描述 evaluation 從 static 拓展到 dynamic 場景的趨勢。接著作者點名 Gemini 1.5、GPT-4o、InternVL、ViLA、LongViLA、LongVA、LLaVA-OneVision 等 SOTA 模型在 localization、layout inference、memory recall 等任務上仍有顯著缺口，並把這個缺口歸因於缺乏 structured spatial representation 與 multi-view encoding。然後再次回到對 dual-encoder spatial VLM 的限制：normalized depth 無法處理 measurement-dependent reasoning。最後一句作為 transition，強調本文的方法「end-to-end 從 monocular RGB video 提取 3D 資訊並融入 LMM」，明確標示與 modular pipeline / additional sensor 路線的差異。

第三小節 "3D Reconstruction from Images" 是技術 preliminaries。作者快速回顧 SfM+MVS 的 modular pipeline 雖精準但慢，再過渡到 learnable MVSNet 與後續變體。重頭戲是 transformer-based reconstruction：DUSt3R 與 MASt3R 直接 regress pixel-aligned 3D point map，不需已知 camera；後繼工作如 MV-DUSt3R+、Fast3R、VGGT、Spatial Memory 把方法擴展到 multi-view、語意、dynamic 場景；CUT3R 則進一步處理 dynamic scenes 並維持 metric scale。這段的功能是把 CUT3R 放到合適的歷史座標：它不是任意挑的工具，而是在 scale ambiguity、dynamic adaptation 兩個維度上同時改進的選擇。

整段 Related Work 採取「立—破—承」的結構：立起既有工作的進展，破除其在 scale 與 sensor 依賴上的局限，承接到自己的方法。值得注意的是，作者沒有單獨設立 Preliminaries 段，而是把 CUT3R 的角色滲透在第一與第三小節，讓讀者讀完整段就能理解後文 §4 為何把 CUT3R 嵌入 spatial encoder，又為何只取 implicit token 而非 explicit point cloud。同時，這節對 VSI-Bench 的處理特別細緻，既肯定其 benchmark 價值，又指出其僅 5,000 QA 的規模不足以訓練 robust spatial VLM，為 §3 的 200K QA 資料 pipeline 提供必要性論證。

### 3.4 Method (overview narrative)

(1800 words)

論文把方法切成兩個並行的章節：§3 描述 scalable data + benchmark，§4 描述 architecture，兩者合在一起構成 VLM-3R 的完整方法論。這個切法本身傳達一個訊息——資料與架構同等重要，並非附屬關係。

§3 一開頭明確定位：VSI-Bench 雖以人工標註與半自動工具產出 5,000 QA，卻難以擴展，因此需要一條基於既有 3D 資料集的自動 pipeline。作者特別強調 pipeline 嚴守原資料集的 train/test split，避免 data leakage——這是審稿人會立刻檢查的合規細節。接著 §3.2 拆成 General Spatial QA Generation 與 Route Planning Data Generation 兩塊：前者把 ScanNet、ScanNet++、ARKitScenes 這類含 3D geometry、semantics、instance metadata 的開源資料集，整合成統一的 spatio-temporal scene graph，每個 frame 是 temporal node，每個 object instance 是帶 global/local coordinate 與 semantic 屬性的 node，由此自動生成涵蓋 VSI-Bench 八項核心任務中七項的 QA pairs。後者用 Habitat simulator 模擬 agent 從起點依 navigation instruction 走到目標的過程，沿路採樣 navigable path 並產出對應文字描述，最終構成 4,225 個符合 VSI-Bench route planning 格式的 QA pairs。資料流程完成後，§3.3 引入 VSTI-Bench，定位是「從 static 3D 場景考察 temporal reasoning」，因此 apparent motion 全來自 camera。138.6K QA 拆成三大類：Camera Dynamics 49.6%、Camera-Object Interactions 38.4%、Object Relative Position 12.0%；底層也是同一套 spatio-temporal scene graph，從中計算 net camera displacement 等 temporal 量。Metric 部分對 MCA 採 Accuracy，對 NA 採 Mean Relative Accuracy（在 0.5 至 0.95 共十個 tolerance 上取平均），這是延續 VSI-Bench 的協議以利同等比較。

§4 的 architecture 章節從 overview 切入：輸入是 monocular video frame 序列 $\{I_t\}_{t=1}^{N}$ 與 language instruction，輸出是融合 visual、geometric、camera pose token 並與 language 對齊的回應。§4.1 將整體架構命名為 Geometry-Aware Vision-Language Model，強調維持原 VLM 的 generality，不要求 depth 或 pre-built 3D map。

3D Reconstructive Tokenization 是方法的核心子模組，採用 pre-trained CUT3R 逐 frame 處理。每個 image $I_t$ 先經 image encoder $f_{\text{enc}}$（一個 ViT）萃取 feature token $F_t$；接著 $F_t$ 連同 learnable pose query token $z$ 與前一個 recurrent state $s_{t-1}$ 一起送入 transformer decoder $f_{\text{dec}}$，輸出更新後的 state $s_t$、context-aware image token $F'_t$、pose-related token $z'_t$，形式化為：

$$F_t = f_{\text{enc}}(I_t),\quad [z'_t, F'_t], s_t = f_{\text{dec}}([z, F_t], s_{t-1})$$

下游 prediction head 從 $F'_t$、$z'_t$ 推出 metric-scale 3D point map $P_{\text{map}_t}$ 與相對 camera pose $T_t$。作者特別解釋為何選 CUT3R 而非 VGGT/DUSt3R：因為 CUT3R 輸出的是 metric-scale，避免 normalized scale 在 instruction alignment 階段引入的歧義。更關鍵的是，作者選擇不直接 fuse explicit point cloud，而是用 implicit latent representation：sparse、跨 frame 大小不一的 point cloud 難以 encode，相對地 $F'_t$ 與 $z'_t$ 提供 compact 的 3D + camera 表徵。為了讓 visual encoder 與 spatial encoder 產生的 token 數一致，input image 統一 resize 到 432×432。訓練期間 visual encoder 與 CUT3R 的 $f_{\text{enc}}$、$f_{\text{dec}}$ 全凍結。

Spatial-Visual View Fusion 把 spatial token $F'_t$ 與 view token $z'_t$ concat 成 $Z_{3D} = \text{Concat}(F'_t, z'_t)$，再與 VLM 的 native visual token $H_v$（由 CLIP ViT 抽取）做 cross-attention，其中 $H_v$ 當 query，$Z_{3D}$ 當 key/value：

$$H_{\text{attn}} = \text{softmax}\left(\frac{(H_v W_Q)(Z_{3D} W_K)^T}{\sqrt{d_k}}\right)(Z_{3D} W_V)$$

接著用 residual connection 保留原視覺外觀資訊：$H'_v = H_v + H_{\text{attn}}$。融合後的 token 經 two-layer projector（沿用 LLaVA-NeXT-Video 的設計）對齊到 LMM 輸入空間，最後與 language instruction token $H_{\text{instruct}}$ concat 成 $[H'_v; H_{\text{instruct}}]$ 餵入 transformer backbone。

訓練目標沿用 LLaVA-NeXT-Video 的 supervised fine-tuning loss，效率上採 LoRA，更新範圍限定在 3D fusion attention block 與 projection layer。這個設計選擇呼應 §3 的資料規模——既有 200K instruction-tuning data，又用 LoRA 控制 trainable parameter，能在 16 顆 H200 GPU 上 5 小時內完成 1 個 epoch（細節在 supplementary）。整節方法的敘事邏輯為：先用大規模 spatio-temporal scene graph 自動生成資料，再以 metric-scale geometry encoder + cross-attention fusion 把 implicit 3D token 注入 VLM，最後以 LoRA-based instruction tuning 把整套流程串接成 end-to-end 系統，為 §5 的多 benchmark 評估鋪好實驗條件。

### 3.5 Experiments (overview narrative)

(1800 words)

§5 的實驗結構由 implementation details、benchmark 評估、ablation 三大部分組成。整節敘事的主軸是「在多元 benchmark 上同時驗證 spatial、temporal、general 三個維度的能力」，以此回應 §1 提出的三條 contribution（架構、資料、benchmark）。

§5.1 先交代 baseline 與設定。作者把比較對象切成兩類：proprietary 系統（Gemini-2.5 Pro、GPT-4o）與 open-source 模型（ViLA、LLaVA-OneVision、LLaVA-NeXT-Video、Qwen2.5-VL、Spatial-MLLM、VG-LLM）。VLM-3R 的 fine-tuning 採 LoRA rank 128 / scale 256，凍結 visual 與 spatial encoder，僅放開 alignment block，訓練 1 epoch on H200 GPU。這個設定在 supplementary 才補完整 hyperparameter 表，但 main text 已給出最重要的兩個訊號：LoRA 與 single-epoch，暗示 cost 受控且收斂快。

§5.2 的 benchmark 評估開展五條獨立的證據鏈。第一條是 VSI-Bench：用 5,000+ egocentric QA 涵蓋八個 spatial 任務，VLM-3R 7B 取得 60.9 平均分，在 open-source 區域排名第一，並在 Absolute Distance（20.2 → 49.4）、Room Size（12.3 → 67.1）、Relative Direction（42.4 → 80.5）等任務上對 2D-only baseline 有大幅領先，作者把這歸因於 architecture 與 spatially oriented data 的協同作用。第二條是 VSTI-Bench，這是論文自建的 benchmark，VLM-3R 在所有五個任務上都拿下 open-source 最高分（平均 58.8），並把 view token 解讀為「使模型能 disentangle camera movement 與 object-centric spatial relation」的關鍵——這也直接呼應 §1 對 evolving spatial relation 的承諾。第三條是 ScanQA 與 SQA3D：作者依 Spatial-MLLM 協議在合併資料集上訓練，VLM-3R 在 ScanQA 上達 CIDEr 101.9，在 SQA3D 上 EM1 達 60.7、EM-R1 達 63.4，與需要 ground-truth depth 的 Video-3D LLM、LLaVA-3D 持平甚至略勝；這條證據強調 monocular-only 也能逼近 depth-supervised baseline，是論文最有說服力的單一 finding。第四條是 OST-Bench，用 online、temporally grounded 的 active exploration 設定來檢視 generalization；雖然 VLM-3R 只在 static indoor scene 訓練，仍在 Agent State、Agent-Object Spatial Relationship、Estimation 等類別超越 base model（42.9 vs. 39.3），作為「跨領域推廣」的證據。第五條是 general-purpose 評估：Video-MME 與 VQAv2。作者坦承純 VSI-only training 會把 Video-MME 從 62.7 拉到 59.9，於是用 LLaVA-3D 的 data-mixing 策略加入 30K LLaVA-Video 通用樣本，把 Video-MME 拉回到 62.1（差距縮到 1pp 內），同時在 Spatial Perception subset 反而提升 +3.7%。這個結果處理得相當坦白：承認 trade-off 存在，再用 mixing 策略修復，不迴避負面證據。

§5.3 的 ablation 把架構拆成五個變體與 baseline，全部以 VSI-Bench 平均分排序。完整版 2D-3D fusion 拿到 60.90 為基準，依次為：w/o Spatial Token 59.46、w/o View Token 59.09、2D-2D Fusion 58.12、Explicit Points Fusion 57.87、LLaVA-NeXT-Video ft (w/o C&G Token) 57.74。這份排序傳達三個訊息：(1) spatial 與 view token 都必要，少一個就掉分，且 view token 對 direction-sensitive 任務影響更大；(2) 純 2D-2D fusion 雖比沒有 fusion 好，但仍比 2D-3D fusion 差約 2.8 分，證實 3D 結構整合的必要；(3) 最有意思的對比是 token-level fusion 勝過 explicit point cloud fusion（60.90 vs. 57.87），這直接回應 §4 設計時為何選 implicit latent 而非 explicit point cloud——sparsity 與不一致大小確實有害。Ablation 末尾作者自承 Object Size 比 baseline 略低（69.15 vs. 70.82），把它歸因於 monocular 3D reconstruction 的精度上限，這也為 §6 的 limitation 預留接口。

整段實驗敘事採「廣度—深度—自省」的節奏：先用五個 benchmark 把 VLM-3R 放到不同維度上比較，再用 ablation 拆解每個元件的貢獻，最後留下一個誠實的弱點作為過渡。最關鍵的論證是：在 monocular 設定下，VLM-3R 不僅勝過 open-source baseline，更能在 ScanQA/SQA3D 上接近 depth-supervised 模型，並在 OST-Bench 上展現跨域泛化，三者合起來支撐了 §1 對 "approaching depth-based baselines while maintaining strong generalization" 的承諾。

### 3.6 Conclusion / Limitations / Future Work

(280 words)

Conclusion 段採用標準的「重申貢獻—承認限制—指向未來」三段式結構，但篇幅克制，僅約 280 字。第一句把 VLM-3R 重新定位為「透過 reconstructive instruction tuning 顯著增強 VLM」的框架，刻意把 instruction tuning 而非 architecture 放在中心位置——這個措辭呼應 §3 的資料貢獻與 §4 的架構貢獻都是必要條件，缺一不可。

第二句濃縮三項要素：200K curated training instances、Spatial-Visual-View fusion module、metric-scale geometric information 與 camera view context 的整合，並再次強調「不需 depth sensor 或 pre-computed 3D map」這個賣點。值得注意的是這裡新增了一個說法——「help disentangle object semantics from egocentric camera motion」，把 view token 的功能上升到語意/相機解耦的層次，這在 §4 沒有被明確提到，是 conclusion 才補上的詮釋。

第三、四句轉向 benchmark 貢獻：再次點名 138.6K temporal QA pairs 的 VSTI-Bench，定位為「填補 temporal reasoning 評估缺口」的工具。同時作者插入一句相當坦白的 hedging："broader applicability and ultimate performance remain closely tied to the challenges of large-scale 4D data collection and the accuracy of end-to-end 3D reconstruction"——這既是免責聲明，也指出兩條未來改進路徑：4D 資料規模與重建精度。

最後一句正面承認 limitation：「current datasets prioritize static indoor scenes, leaving the exploration of dynamic and extreme environments for future work」。這條限制與 §3 的 benchmark 設計（all motion comes from camera, static scenes only）一致，並未掩飾，且明確把 dynamic scene 與 extreme environment 標為 future work，給後續論文留下接口。整段 Conclusion 不渲染、不擴張，只把承諾過的事重申一遍並劃定有效範圍，是篇幅短但收尾完整的處理。

## 4. Critical Profile

### 4.1 Highlights

- 採用 CUT3R 作為 metric-scale geometry encoder，避免 VGGT 等 normalized-depth 方案在絕對距離與物體尺寸推理上的尺度不確定性（p.3、p.5 §4.1）。
- 提出 Spatial-Visual-View Fusion，以 cross-attention 將 spatial tokens $F'_t$ 與 view tokens $z'_t$ 注入 visual tokens $H_v$，再透過 residual $H'_v = H_v + H_{\text{attn}}$ 保留外觀資訊（Fig. 3、Eq. 2-3，p.5）。
- 自動化資料生成管線產出超過 200K spatial QA 與 4,225 個 Habitat-based route planning 樣本，覆蓋 VSI-Bench 七種任務類型（Table A，p.15）。
- 提出 VSTI-Bench，含約 138.6K QA、五種子任務，分布於 Camera Dynamics 49.6%、Camera-Object Interactions 38.4%、Object Relative Position 12.0%（Fig. 2，p.3）。
- 在 VSI-Bench 達到 Avg 60.9，於 open-source VLM 排名第一，較 fine-tuned LLaVA-NeXT-Video-7B 基線的 57.7 高 3.2 pp（Table 1，p.7）。
- 在 Absolute Distance 從 baseline 14.0 提升至 49.4、Room Size 從 47.8 提升至 69.2、Relative Direction 從 43.5 提升至 80.5，是同基線下最顯著的改進（Table 1，p.7）。
- 在 VSTI-Bench 達到 Avg 58.8，較最強對照組 LLaVA-NeXT-Video-72B 的 44.0 高 14.8 pp，但仍與 Human Level 77.0 存在差距（Table 2，p.7）。
- 在 ScanQA / SQA3D 僅以 monocular video 即可逼近需要 ground-truth depth 的 Video-3D LLM（CIDEr 101.9 vs. 102.1；SQA3D EM 60.7 vs. 58.6）（Table 3，p.7）。
- 在 OST-Bench 上 VLM-3R 42.9 全面超越其 base model LLaVA-Video-7B 的 39.3，特別在 Estimation（28.3 vs. 16.1）與 Agent-Object（34.4 vs. 28.8）類別（Table 7，p.8）。
- Token-level fusion 較 explicit point clouds fusion 高 3.0 pp（60.90 vs. 57.87），驗證隱式 latent token 在跨幀稀疏與大小不一情境下優於直接餵點雲（Table 6，p.8）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 論文明確指出當前資料集僅涵蓋 static indoor scenes，dynamic 與 extreme 環境留待 future work（Conclusion，p.8）。
- 作者承認模型表現「closely tied to the challenges of large-scale 4D data collection and the accuracy of end-to-end 3D reconstruction」，將之列為廣泛應用的瓶頸（Conclusion，p.8）。
- Ablation 顯示 Object Size 略低於不含 C&G token 的 2D fine-tuned 基線（69.15 vs. 70.82），作者歸因於「room for improvement in monocular 3D reconstruction quality」（§5.3，p.8）。

#### 4.2.2 Phyra-inferred

- VSI-Bench 上 architectural-only 增益僅 3.2 pp（60.90 vs. LLaVA-NeXT-Video ft 57.74，Table 6），但 fine-tuned 2D 基線本身較未微調的 LLaVA-NeXT-Video-7B 35.6 高出約 22 pp，顯示主要增益來自 200K 指令資料而非 Spatial-Visual-View Fusion 本身。
- Object Size 在完整模型上反而退化（69.15 < 70.82，Table 6），暗示 CUT3R token 注入對該子任務有負向作用，且論文僅以「reconstruction quality」帶過，未診斷此 regression 的失敗模式。
- VSTI-Bench 由作者以同一 spatio-temporal scene graph 管線、自同一批 ScanNet / ScanNet++ / ARKitScenes 場景自動生成（p.4 §3.3），與 VLM-3R 訓練資料同源同管線，可能存在 task-format 與標註偏差，使該基準對自家方法系統性有利。
- 對 Spatial-MLLM（4B、Avg 47.0）與 VLM-3R（7B、Avg 60.9）的比較同時混雜 base model 大小、訓練資料規模與 metric-scale geometry 三個變因（Table 1），無法以受控實驗孤立「metric scale 優於 normalized depth」這項核心論點。
- CUT3R encoder 全程 frozen（§4.1，p.5），代表幾何誤差不會透過下游 loss 修正，且論文未提供 reconstruction error 與 VSI-Bench task error 的相關性分析。
- VSI-only 訓練使 Video-MME 由 62.7 降至 59.9，須額外混入 30K LLaVA-Video 才回升至 62.1（Table 5，p.8），顯示空間能力提升以一般 video QA 退化為代價，且回補後仍未達到 base model 表現。
- VSTI-Bench 設計刻意限定 static 3D scenes，使得「temporal reasoning」實質退化為 camera trajectory 分析（p.2、p.4），規避了真正的物體運動與相機運動解耦問題。

### 4.3 Phyra's Judgment (summary)

VLM-3R 真正的工程貢獻有二：以 metric-scale 的 CUT3R 取代 normalized-depth 編碼器，以及將其輸出以 implicit latent token 而非 explicit point cloud 餵入 VLM，後者經由 Table 6 token vs. explicit point fusion 的 3.0 pp 差距得到直接支持。然而 VSI-Bench 上絕大多數的數字躍進主要來自 200K 自動生成的 instruction data，而非 Spatial-Visual-View Fusion 架構本身（架構增益僅 3.2 pp）。論文未透過受控實驗孤立 metric scale 相對 normalized depth 的真正貢獻，亦未診斷 Object Size 在加入 3D token 後反而退化的成因，這兩個未解問題使「metric-scale geometry 是視覺空間智能瓶頸」此核心主張仍待更乾淨的驗證。

## 5. Methodology Deep Dive

### 5.1 Method Overview

VLM-3R 採用「凍結 backbone + 可學習融合層」的端到端架構，將單目影片直接轉換為具 metric scale 的隱式 3D tokens，並透過 Spatial-Visual-View Fusion 模組注入語言對齊空間，最後交由 LLM backbone 完成空間—時間推理。整體輸入為 monocular video 影格序列 $\{I_t\}_{t=1}^N$（每張 $I_t \in \mathbb{R}^{H \times W \times 3}$）與語言指令；輸出為自然語言回答 $X_a$。架構主幹沿用 LLaVA-Next-Video 的 two-layer projector 設計，使其能與既有 VLM 生態對接，避免在新環境中引入 pre-built 3D map 或 depth sensor 的依賴。

3D 編碼器選用 CUT3R（一個具 metric scale 的多視角幾何 transformer）。對每一影格，CUT3R 先以 image encoder $f_{\text{enc}}$（例如 ViT）抽取 frame token $F_t$，再將其與一個可學習的 pose query token $z$ 及前一時刻的 recurrent state $s_{t-1}$ 一併送入 transformer decoder $f_{\text{dec}}$，輸出更新後的 state $s_t$、context-aware 影像 token $F'_t$ 與 pose-related token $z'_t$。預測頭再從這些 token 解出 metric-scale point map $P_{\text{map},t}$ 與相對相機位姿 $T_t$（這兩者僅作為 CUT3R 的監督信號，VLM-3R 本身只取 $F'_t$ 與 $z'_t$ 作為 spatial / view tokens）。為確保影像與幾何 token 數量一致，輸入影像被縮放到統一尺寸（例如 $432 \times 432$），且訓練時 $f_{\text{enc}}$、$f_{\text{dec}}$ 與原 VLM 的 visual encoder 全部 frozen。論文選擇 implicit latent token 而非直接餵入 explicit point cloud，原因在於跨幀點雲稀疏、大小不一且難以與 language token 對齊，而 latent token 仍保留幾何資訊並天然適配 transformer 的序列輸入。

Spatial-Visual-View Fusion 將 $Z_{3D} = \text{Concat}(F'_t, z'_t)$ 與 VLM 原生 visual token $H_v$（由 frozen CLIP ViT 抽取）以 cross-attention 融合：$H_v$ 作為 query，$Z_{3D}$ 提供 key/value，並透過 residual connection 保留 2D 外觀資訊得到 $H'_v$。$H'_v$ 經 two-layer projector 對齊到 LLM 詞嵌入空間後，與 instruction token $H_{\text{instruct}}$ 串接送入 transformer backbone。訓練時凍結 visual encoder 與 CUT3R，僅以 LoRA（rank 128, scale 256）更新 LLM 與 fusion / projector 模組，沿用 LLaVA-NeXT-Video 的監督式微調目標，在 200K 3D 重建式指令資料上端到端對齊 visual appearance、metric 幾何與相機視角資訊（pp. 4–6, Figure 3）。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input:
  Video  : V ∈ [B, N, 3, H, W]              # H = W = 432, N = 影格數
  Text   : X_q ∈ [B, L_q]                   # token id 序列

(a) Visual Encoder (frozen, e.g. CLIP ViT)
   ┌─ per-frame ─────────────────────────────────────────────┐
   │ I_t ∈ [B, 3, 432, 432]                                  │
   │   └→ ViT patch embed + transformer                      │
   │        H_v,t ∈ [B, P, d_v]                              │  # P = patch 數, d_v = ?
   └─ stack over N frames → H_v ∈ [B, N, P, d_v]            │
                                                             │
(b) Spatial Encoder = CUT3R (frozen)
   ┌─ per-frame, recurrent over t = 1..N ────────────────────┐
   │ I_t ∈ [B, 3, 432, 432]                                  │
   │   └→ f_enc (ViT)                                        │
   │        F_t ∈ [B, P, d_g]                                │  # d_g = CUT3R token dim, ?
   │   └→ f_dec([z, F_t], s_{t-1})                           │
   │        F'_t ∈ [B, P, d_g]   (spatial tokens, 場景結構)  │
   │        z'_t ∈ [B, K_z, d_g] (view tokens, 相機位姿)     │  # K_z = pose query 數, ?
   │        s_t  ∈ [B, d_s]      (持續狀態, 不送入 LLM)       │  # d_s = ?
   │   └→ prediction heads (僅供 CUT3R 監督):                 │
   │        P_map,t ∈ [B, P, 3]    (metric-scale point map)  │
   │        T_t     ∈ [B, 4, 4]    (相對相機位姿)             │
   └─ stack over N frames →                                  │
        F' ∈ [B, N, P, d_g],  z' ∈ [B, N, K_z, d_g]          │
                                                             │
   ─ Concat 形成 3D token：                                   │
     Z_3D = Concat(F', z') ∈ [B, N, P + K_z, d_g]            │

(c) Spatial-Visual-View Fusion (LoRA-trainable)
   H_v   ∈ [B, N, P,        d_v]   (queries source)
   Z_3D  ∈ [B, N, P + K_z,  d_g]   (keys/values source)

   per-frame cross-attention:
     Q = H_v   · W_Q ∈ [B, N, P,        d_k]                 # d_k = ?
     K = Z_3D  · W_K ∈ [B, N, P + K_z,  d_k]
     V = Z_3D  · W_V ∈ [B, N, P + K_z,  d_v]
     A = softmax(Q · Kᵀ / √d_k) ∈ [B, N, P, P + K_z]
     H_attn = A · V ∈ [B, N, P, d_v]

   residual：H'_v = H_v + H_attn ∈ [B, N, P, d_v]

(d) Two-Layer Projector (LLaVA-NeXT-Video 設計, LoRA-trainable)
     H'_v ∈ [B, N, P, d_v]
       └→ Linear → GELU → Linear
         H_proj ∈ [B, N, P, d_LLM]                           # d_LLM = LLM hidden size, ?
       └→ flatten frames：[B, N·P, d_LLM]

(e) Text Embedding
     X_q ∈ [B, L_q]
       └→ token embedding
         H_instruct ∈ [B, L_q, d_LLM]

(f) Sequence Concatenation → LLM Backbone (LoRA-trainable)
     H_in = [H_proj ; H_instruct] ∈ [B, N·P + L_q, d_LLM]
       └→ transformer decoder (LLM)
         logits ∈ [B, L_out, |V|]                            # |V| = 詞表大小

Output:
  X_a：自回歸解碼出的自然語言回答
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Visual Encoder（凍結的 2D 視覺主幹）

**Function:** 將每一影格抽成 frame-level 語意 token $H_v$，提供物件外觀與場景語意先驗。

**Input:**
- Name: $I_t$
- Shape: `[B, 3, 432, 432]`（每幀；整段影片為 `[B, N, 3, 432, 432]`）
- Source: 原始 monocular video

**Output:**
- Name: $H_v$
- Shape: `[B, N, P, d_v]`
- Consumer: Spatial-Visual-View Fusion（作為 cross-attention 的 query）

**Processing:**

論文沿用 LLaVA-Next-Video 的 visual backbone（例：CLIP ViT），每幀獨立抽取 patch token。為使 visual token 與 spatial token 數量對齊，輸入影像被統一縮放至 $432 \times 432$（p. 5）。VLM-3R 訓練期間此編碼器全程凍結，不參與梯度更新。

**Key Formulas:**

$$
H_{v,t} = f_{\text{vis}}(I_t), \quad H_v = \{H_{v,t}\}_{t=1}^{N}
$$

**Implementation Details:**

論文僅指明使用 LLaVA-Next-Video 之 pre-trained visual encoder（如 CLIP ViT）並在訓練時凍結（pp. 5–6）；patch 數 $P$ 與通道維 $d_v$ 等具體數值，the paper does not specify。

---

#### 5.3.2 Spatial Encoder（CUT3R，凍結的 metric-scale 幾何 transformer）

**Function:** 從單目影片以遞迴方式抽取具 metric scale 的隱式 3D 表徵，產出 spatial token $F'_t$（場景結構）與 view token $z'_t$（相機視角）。

**Input:**
- Name: $\{I_t\}_{t=1}^{N}$、可學習 pose query $z$、前一時刻狀態 $s_{t-1}$
- Shape: $I_t \in [B, 3, 432, 432]$；$z, s_{t-1}$ 為內部 latent，論文未列具體維度
- Source: 原始 monocular video（與 visual encoder 共用同一 resized 輸入）

**Output:**
- Name: $F'_t$（spatial tokens）、$z'_t$（view tokens）；附帶監督信號 $P_{\text{map},t}$、$T_t$
- Shape: $F' \in [B, N, P, d_g]$、$z' \in [B, N, K_z, d_g]$；$P_{\text{map},t} \in [B, P, 3]$、$T_t \in [B, 4, 4]$
- Consumer: Spatial-Visual-View Fusion（提供 cross-attention 的 key/value，concat 成 $Z_{3D}$）

**Processing:**

對每一影格 $I_t$，CUT3R 先用 image encoder $f_{\text{enc}}$（ViT）抽取 feature token $F_t$，再以 transformer decoder $f_{\text{dec}}$ 處理 $[z, F_t]$ 並結合前一狀態 $s_{t-1}$，得到更新後 state $s_t$、context-aware token $F'_t$ 與 pose-related token $z'_t$（Eq. 1, p. 5）。專屬 prediction heads 從 $F'_t, z'_t$ 解出 metric-scale 點圖 $P_{\text{map},t}$ 與相對相機位姿 $T_t$，這兩者僅供 CUT3R 內部訓練；VLM-3R 推論時只將 $F'_t, z'_t$ 串接為 $Z_{3D}$ 送入後續融合層（p. 5）。論文強調 CUT3R 輸出的是 metric scale，而非 normalized 深度（如 VGGT/DUSt3R），這正是區別於 Spatial-MLLM、VG-LLM 的關鍵設計動機（pp. 2–3, 5）。

**Key Formulas:**

$$
F_t = f_{\text{enc}}(I_t)
$$

$$
[z'_t, F'_t],\, s_t = f_{\text{dec}}([z, F_t], s_{t-1})
$$

$$
Z_{3D} = \text{Concat}(F'_t, z'_t)
$$

**Implementation Details:**

CUT3R 權重在訓練時 frozen（包含 $f_{\text{enc}}$ 與 $f_{\text{dec}}$，p. 5）。輸入影像縮放至 $432 \times 432$ 以對齊 token 數量。token 維度 $d_g$、pose query 數量 $K_z$、recurrent state 維度 $d_s$，the paper does not specify。

---

#### 5.3.3 Spatial-Visual-View Fusion（2D–3D Cross-Attention，可學習）

**Function:** 將 metric-scale 3D 幾何與相機視角資訊以 cross-attention 注入 2D 視覺 token，使 $H_v$ 在保留外觀的同時獲得 metric-aware 的 3D context。

**Input:**
- Name: $H_v$、$Z_{3D}$
- Shape: $H_v \in [B, N, P, d_v]$、$Z_{3D} \in [B, N, P + K_z, d_g]$
- Source: 5.3.1 Visual Encoder、5.3.2 Spatial Encoder

**Output:**
- Name: $H'_v$（融合後 3D-aware visual tokens）
- Shape: `[B, N, P, d_v]`
- Consumer: Two-Layer Projector

**Processing:**

論文採 cross-attention 結構，以 $H_v$ 為 queries、$Z_{3D}$ 為 keys/values（Eq. 2, p. 5），以 frame 為單位獨立計算注意力，並對輸出加上 residual connection 保留原始 2D 語意：

$$
H_{\text{attn}} = \text{softmax}\!\left(\frac{(H_v W_Q)(Z_{3D} W_K)^\top}{\sqrt{d_k}}\right) (Z_{3D} W_V)
$$

$$
H'_v = H_v + H_{\text{attn}}
$$

論文於 ablation（Table 6, p. 8）對比了 (i) 完整 2D–3D fusion（60.90）、(ii) 移除 spatial token（59.46）、(iii) 移除 view token（59.09）、(iv) 改為 2D–2D fusion（58.12）、(v) 改用 explicit point cloud fusion（57.87），結果顯示 token-level 的 2D–3D 融合在 VSI-Bench 平均分上最佳，驗證 spatial token 對 3D 結構建模、view token 對 egocentric 方向推理的必要性，以及 implicit token 較 explicit point cloud 更穩定的設計選擇。

**Key Formulas:**

$$
H_{\text{attn}} = \text{softmax}\!\left(\frac{(H_v W_Q)(Z_{3D} W_K)^\top}{\sqrt{d_k}}\right) (Z_{3D} W_V)
$$

$$
H'_v = H_v + H_{\text{attn}}
$$

**Implementation Details:**

$W_Q, W_K, W_V$ 為可學習 projection matrices，$d_k$ 為 key dimension（具體數值 the paper does not specify）。此模組與 projector 一同以 LoRA（rank 128, scale 256）更新（p. 6）；attention head 數、normalization 種類、initialization 方式，the paper does not specify。

---

#### 5.3.4 Two-Layer Projector（對齊到 LLM 詞嵌入空間，可學習）

**Function:** 將融合後的 3D-aware visual token $H'_v$ 投影到 LLM backbone 的詞嵌入維度，使其能與文字 token 串接送入 transformer。

**Input:**
- Name: $H'_v$
- Shape: `[B, N, P, d_v]`
- Source: Spatial-Visual-View Fusion

**Output:**
- Name: $H_{\text{proj}}$
- Shape: 投影後 `[B, N, P, d_{\text{LLM}}]`，flatten 後 `[B, N·P, d_{\text{LLM}}]`
- Consumer: LLM Backbone（與 $H_{\text{instruct}}$ 串接）

**Processing:**

沿用 LLaVA-Next-Video 的 two-layer projector（p. 5）：兩層線性層加非線性活化函數，將 $d_v$ 映射至 $d_{\text{LLM}}$，再以時間順序展平所有 frame 的 token，以便 LLM 將 visual evidence 視為一段長序列輸入。

**Key Formulas:**

$$
H_{\text{proj}} = \text{Proj}_2\big(\sigma(\text{Proj}_1(H'_v))\big)
$$

**Implementation Details:**

論文僅說明採用 LLaVA-NeXT-Video 的 two-layer projector 結構並以 LoRA 更新（pp. 5–6）；活化函數類型、隱藏維度與 $d_{\text{LLM}}$ 具體數值，the paper does not specify。

---

#### 5.3.5 LLM Backbone（LoRA 微調的語言模型）

**Function:** 接收 3D-aware visual token 與 instruction token 的串接序列，自回歸生成回答 $X_a$，完成空間—時間推理與物件—相機關係解讀。

**Input:**
- Name: $H_{\text{in}} = [H_{\text{proj}}; H_{\text{instruct}}]$
- Shape: `[B, N·P + L_q, d_{\text{LLM}}]`
- Source: Two-Layer Projector + token embedding 後的 $H_{\text{instruct}} \in [B, L_q, d_{\text{LLM}}]$

**Output:**
- Name: 自回歸 logits 與最終文字回答 $X_a$
- Shape: `[B, L_{\text{out}}, |V|]`，$|V|$ 為詞表大小
- Consumer: 下游 QA 評測（VSI-Bench、VSTI-Bench、OST-Bench、ScanQA、SQA3D、Video-MME、VQAv2）

**Processing:**

LLM backbone 沿用 LLaVA-NeXT-Video（7B），訓練時其它模組（visual encoder、CUT3R）皆 frozen，僅對 LLM 與 3D fusion attention block、projection layers 套用 LoRA 進行微調（p. 6）。論文使用與 LLaVA-NeXT-Video 相同的 supervised fine-tuning objective（autoregressive language modeling），在 200K 3D 重建式指令對加上 30K LLaVA-Video 一般影片資料（Table 5, p. 8）上訓練 1 epoch（p. 6）。實驗顯示此設計在 VSI-Bench 上將 7B baseline 從 35.6 提升至 60.9（Table 1, p. 7），且在 OST-Bench 上對 LLaVA-Video-7B 的多項類別（Agent State、Agent–Object Spatial Relationship、Estimation）皆有改善（Table 7, p. 8），同時在 Video-MME 與 VQAv2 上維持泛化能力。

**Key Formulas:**

$$
\mathcal{L} = -\sum_{l=1}^{L_{\text{out}}} \log p_\theta\big(x_l \mid x_{<l}, H_{\text{in}}\big)
$$

**Implementation Details:**

LoRA rank 128、scale 256；除 alignment block 外，visual encoder 與 spatial encoder 全程凍結；訓練 1 epoch，硬體為 NVIDIA H200 GPU（p. 6）。學習率、batch size、optimizer 設定、warmup schedule，the paper does not specify。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| ScanNet [17] | Indoor 3D scene source for QA generation | the paper does not specify scene count | train (QA generation source) |
| ScanNet++ [80] | Indoor 3D scene source for QA generation | the paper does not specify scene count | train (QA generation source) |
| ARKitScenes [8] | Indoor 3D scene source for QA generation | the paper does not specify scene count | train (QA generation source) |
| 200K Spatial Reconstructive QA (curated) | 3D reconstructive instruction tuning across 7 VSI tasks | 207,779 QA pairs (Table A) | train |
| Route Planning (Habitat-generated) | High-level navigation instruction following | 4,225 QA pairs | train |
| LLaVA-Video [86] (general subset) | General video QA for data mixing | 30K samples | train (mixing) |
| ScanQA [4] | 3D question answering | 4,675 validation QA pairs | train (official split) + val |
| SQA3D [48] | Situated 3D QA | 3,519 test QA pairs | train (official split) + test |
| VSI-Bench [77] | Visual-spatial intelligence (8 tasks) | ~5,000 QA pairs | test |
| VSTemporalI-Bench (proposed) | Spatio-temporal reasoning (5 tasks) | 138.6K QA pairs | train + test |
| OST-Bench [44] | Online spatio-temporal scene understanding | the paper does not specify | test (zero-shot generalization) |
| Video-MME [22] | General video understanding | the paper does not specify | test |
| VQAv2 [24] | General image VQA | the paper does not specify | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Accuracy (ACC) | Exact or fuzzy match for Multiple-Choice Answer (MCA) tasks | yes |
| Mean Relative Accuracy (MRA) | $\text{MRA}=\tfrac{1}{10}\sum_{\theta\in\{0.5,0.55,\dots,0.95\}}\mathbf{1}[\,|\hat{y}-y|/y < 1-\theta\,]$, used for Numerical Answer (NA) tasks | yes |
| Avg. (VSI-Bench / VSTI-Bench) | Mean across all sub-task scores; the headline number used to rank methods | yes |
| Exact Match (EM, EM-R) | SQA3D scoring: strict EM and a refined variant | yes (for SQA3D) |
| CIDEr / BLEU-1 / BLEU-4 / METEOR / ROUGE-L | Standard caption-style metrics for ScanQA generative answers | yes (for ScanQA) |
| Video-MME Overall (%) | Aggregated multi-domain video understanding accuracy | no (auxiliary) |
| VQAv2 Exact Match | Image VQA accuracy under exact match | no (auxiliary) |

### 6.3 Training and Inference Settings

- **Base model**: initialized from `LLaVA-Video-7B-Qwen2`; vision tower is `google/siglip-so400m-patch14-384`; spatial encoder is CUT3R [72], frozen. Input frames resized to $432 \times 432$ (Sec. 4.1).
- **Tunable parts**: LoRA on the VLM, the cross-attention fusion block, and the MM MLP adapter. Visual encoder and CUT3R remain frozen (Appendix A.2).
- **LoRA**: rank $r=128$, $\alpha=256$ (Sec. 5.1, Appendix A.2).
- **Hardware**: 16 × NVIDIA H200 GPUs, ~5 hours per run, DeepSpeed ZeRO-2 via `accelerate` + `torchrun` (Appendix A.2). The main text says "Training is performed for one epoch on NVIDIA H200 GPUs" (Sec. 5.1).
- **Batch / accumulation**: per-device train batch size $1$, gradient accumulation $8$ (Appendix A.2).
- **Optimizer / schedule**: learning rate $2\times10^{-5}$, cosine LR schedule, warmup ratio $0.03$, weight decay $0$.
- **Epochs**: configured for $5$ but the released run "concluded after the first epoch" (Appendix A.2), matching the "one epoch" claim in Sec. 5.1.
- **Precision**: BF16 + TF32 enabled. Gradient checkpointing on. Max sequence length $32{,}768$ tokens.
- **Fusion dimensions**: spatial tokens $F'_t \in \mathbb{R}^{729\times 768}$, view token $z'_t \in \mathbb{R}^{1\times 768}$, visual tokens $H_v \in \mathbb{R}^{729\times 1152}$; one cross-attention layer + 2-layer MLP projector mapping $1152 \to 3584$ (Appendix A.1).
- **Inference**: monocular video only — no depth sensor or pre-built map. Detailed inference-time hyperparameters (e.g. number of sampled frames, decoding settings) — the paper does not specify.

### 6.4 Main Results

VSI-Bench (open-source block, Avg. across 8 tasks; Table 1):

| Method | Avg. | Abs. Dist. (NA) | Rel. Dir. (MCA) | Notes |
|---|---|---|---|---|
| LLaVA-NeXT-Video-7B | 35.6 | 14.0 | 42.4 | 2D-only baseline |
| Spatial-MLLM-4B | 47.0 | 34.8 | 41.3 | dual-encoder spatial VLM |
| VG-LLM-4B | 47.3 | 37.8 | 44.6 | geometry-aware |
| LLaVA-NeXT-Video-7B (Finetuned) | 57.7 | 43.6 | 64.9 | same data, no C&G tokens |
| Gemini-2.5 Pro (proprietary) | 51.5 | 34.9 | 61.1 | API model, not in open-source ranking |
| **VLM-3R (7B)** | **60.9** | **49.4** | **80.5** | best open-source; +25.3 over its 2D base |

VSTemporalI-Bench (Avg. across 5 tasks; Table 2): **VLM-3R 58.8** vs. LLaVA-NeXT-Video-72B 44.0, Gemini-2.5 Pro 42.4, GPT-4o 38.2; human level 77.0.

ScanQA val / SQA3D test (Table 3): **VLM-3R** reaches CIDEr 101.9, BLEU-4 15.5, METEOR 19.7, ROUGE-L 49.1 on ScanQA, and EM 60.7 / EM-R 63.4 on SQA3D — competitive with depth-using Video-3D LLM (CIDEr 102.1) while video-only.

OST-Bench Overall (Table 7): **VLM-3R 42.9** > LLaVA-Video-7B base 39.3, and clearly above LLaVA-3D 30.1 / Spatial-MLLM 26.8.

General-purpose (Table 4): **VLM-3R** Video-MME 59.9 vs. LLaVA-NeXT-Video 62.7, but Spatial Perception 70.4 vs. 66.7 (+3.7). VQAv2 EM 52.57 vs. 54.63.

### 6.5 Ablation Studies

All variants share the 200K spatial training set and are evaluated by VSI-Bench Avg. (Table 6).

- **Remove spatial tokens (w/o Spatial Tok.)**: Avg. drops $60.90 \to 59.46$ ($-1.44$). Diagnoses the contribution of the geometry stream $F'_t$ to layout/depth reasoning — a real diagnostic of the proposed module.
- **Remove view tokens (w/o View Tok.)**: Avg. drops $60.90 \to 59.09$ in Table 6, although the prose claims a drop to $50.09$ for direction-sensitive tasks; the two numbers are inconsistent and the paper does not reconcile them. Either way, it isolates the camera-pose token $z'_t$, which is a diagnostic ablation.
- **2D-2D fusion** (replace 3D tokens with another copy of 2D features): $60.90 \to 58.12$ ($-2.78$). Tests whether gains come from extra parameters/attention rather than from 3D content — a useful control, not just a sanity check.
- **Explicit point-cloud fusion**: $60.90 \to 57.87$ ($-3.03$). Justifies the design choice of token-level over explicit-geometry fusion; diagnostic of the representation choice.
- **LLaVA-NeXT-Video ft (w/o C&G Tok.)**: $60.90 \to 57.74$ ($-3.16$). Same data, no geometry/camera tokens — isolates architectural contribution from data contribution. This is the most informative ablation.
- **Data mixing (Table 5)**: VSI-only 59.9 vs. VSI + 30K LLaVA-Video 62.1 on Video-MME. This is closer to a sanity check that domain training does not catastrophically hurt general video QA, rather than a diagnostic of VLM-3R's spatial mechanism.

The ablation suite covers the two new token streams, the choice of implicit-vs-explicit geometry, and the data-vs-architecture decomposition — directly aligned with the paper's claims. Missing: no ablation on the number of cross-attention layers, on freezing vs. tuning CUT3R, or on the choice of CUT3R [72] vs. VGGT [69] under matched training.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — compares against Gemini-2.5 Pro, GPT-4o, and recent open-source spatial VLMs (Spatial-MLLM, VG-LLM, Video-3D LLM, LLaVA-3D) on VSI-Bench, VSTI-Bench, ScanQA, SQA3D, and OST-Bench (Tables 1, 2, 3, 7).
- [covered] Has cross-task / cross-dataset evaluation — five distinct benchmarks: VSI-Bench, VSTI-Bench, ScanQA, SQA3D, OST-Bench, plus Video-MME and VQAv2 for generality (Sec. 5.2).
- [covered] Has ablations that diagnose the new components — w/o Spatial Tok., w/o View Tok., 2D-2D fusion, Explicit Points fusion, and a no-token finetuned baseline isolate each design choice (Table 6).
- [missing] Has a scaling study — no experiments varying model size, video length, number of frames, or training-data scale; only a single 7B configuration is reported.
- [missing] Has an efficiency / wall-clock comparison — Appendix A.2 lists training cost (16 × H200, ~5 h) but provides no inference latency, FLOPs, or comparison against multi-stage SLAM/depth pipelines that the introduction critiques.
- [missing] Reports variance / standard deviation / multiple seeds — every number is a single run; no error bars, confidence intervals, or seed averages.
- [partial] Releases code / weights / data sufficient for reproducibility — a project page (`vlm-3r.github.io`) is referenced and hyperparameters are given in Appendix A, but the paper's text does not explicitly state that code, weights, or the 200K + 138.6K QA data will be released.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **「以 monocular video 達到不需 depth sensor 或 pre-built 3D map 的端到端空間推理」**：支持。Table 1 顯示 VLM-3R 在 VSI-Bench Avg 60.9 領先所有 open-source 對照；Table 3 在 ScanQA / SQA3D 與需要 depth 的 Video-3D LLM、LLaVA-3D 達到可比表現（CIDEr 101.9 vs. 102.1；EM 60.7 vs. 58.6），claim 成立。
- **「Spatial-Visual-View Fusion 是性能關鍵」**：部分支持。Table 6 顯示移除 spatial token 降至 59.46、移除 view token 降至 59.09、改用 2D-2D fusion 降至 58.12，三者排序一致，但相對於同樣訓練資料下的 2D-only fine-tuned baseline 57.74，整體增益僅 3.2 pp，遠小於資料微調本身帶來的約 22 pp 提升（35.6 → 57.7，Table 1）；架構貢獻被 overstate。
- **「metric-scale geometry 優於 normalized depth」**：overclaimed。Table 1 比較對象 Spatial-MLLM-4B 與 VG-LLM-4B 同時在 base model 大小（4B vs. 7B）與訓練資料上不同，論文未提供「同 base model + VGGT vs. CUT3R」的受控實驗，metric-scale 的具體貢獻量化缺席。
- **「scalable data pipeline 產出 200K spatial QA + 4,225 route planning」**：支持。Table A 列出 task-level 計數合計 207,779，supplementary §B 詳述自 ScanNet / ScanNet++ / ARKitScenes 衍生與 Habitat 模擬流程，可重現性具體。
- **「VSTI-Bench 系統性評估時間維度空間推理」**：作為資料貢獻支持，作為評估貢獻部分支持。Fig. 2 與 §3.3 描述 138.6K QA 與五子任務分布，但 QA 由 scene graph 自動產生，未報告 human verification 比例，且 Human Level 77.0 是否來自獨立評測者亦未說明。

### 7.2 Fundamental Limitations of the Method

CUT3R encoder 全程 frozen 構成第一個結構性瓶頸：論文承認模型表現「tied to the accuracy of end-to-end 3D reconstruction」（Conclusion，p.8），但既然下游 loss 不傳回 CUT3R，metric-scale 的系統性偏差會無修正地進入 spatial token，並在 Object Size 等任務上以 negative transfer 的形式呈現（Table 6 完整模型 69.15 < 純 2D fine-tune 70.82）。此設計選擇使 VLM-3R 的能力上界由 CUT3R 的重建精度決定，而後者本身在新場景與大尺度環境下的可靠性並未被本文評估。

VSTI-Bench 的 static-scene 假設構成第二個結構性限制：§3.3 明言「Since the scenes are static, all apparent motion arises from camera movement」（p.2），這使 temporal reasoning 在資料層面被簡化為 camera trajectory 推斷，無法檢驗模型在「相機與物體同時運動」的真實 4D 場景下的能力。在此設計下取得高分並不意味著模型真正具備 spatio-temporal disentanglement，論文也明確將 dynamic 與 extreme environments 排除（Conclusion，p.8）。

訓練資料與評測資料的同源性是第三個難以避免的問題：200K 訓練 QA 與 138.6K VSTI-Bench 皆由同一 spatio-temporal scene graph 管線、自同一批 ScanNet / ScanNet++ / ARKitScenes 場景自動產出（§B.1、§B.2，p.14-16），即使作者宣稱遵守 train/test split，question template、距離計算口徑與物件命名空間共享，意味著模型擬合資料生成器特性比擬合空間概念本身更容易，而論文未提供跨資料生成器（例如人工標註）的泛化驗證。

混合一般 video QA 後 Video-MME 仍未回到 LLaVA-NeXT-Video-7B 的 62.7（VSI+LLaVA 為 62.1，Table 5，p.8），顯示 spatial fine-tuning 對一般理解能力存在不可逆的折損，這在僅以 LoRA 微調 fusion block 與 projector 的設定下難以結構性解決。

### 7.3 Citations Worth Tracking

- **CUT3R [72] (Wang et al., 2025)**：VLM-3R 的 metric-scale 幾何骨幹，整體性能上界由其重建品質決定；理解其失敗模式是評估 VLM-3R 可靠性的前提。
- **VSI-Bench [77] (Yang et al., 2024)**：本文最重要的評測基準與訓練資料來源，了解其 task taxonomy 與標註慣例可幫助判斷 200K 自動生成資料的偏差。
- **Spatial-MLLM [76] / [11]**：最直接的競爭者，其 normalized-depth 路線與 VLM-3R 的 metric-scale 路線形成核心對照；應驗證兩者在同 base model 下的真實差距。
- **VGGT [69] (Wang et al., 2025)**：論文用以對比的另一條多視角幾何 transformer 路線，理解其 normalized depth 設計決策有助於判斷 metric-scale 的真正必要性。
- **LLaVA-3D [94] (Zhu et al., 2024) 與 ROSS3D [68]**：depth-supervised 路線代表，與 VLM-3R 在 ScanQA / SQA3D 的對照（Table 3）是「monocular 是否真能逼近 RGB-D」這個 claim 的關鍵基準。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在固定 base model（例如 LLaVA-NeXT-Video-7B）與相同 200K 訓練資料下，將 CUT3R 替換為 VGGT，VSI-Bench Absolute Distance 與 Room Size 會下降多少？這是孤立 metric-scale claim 的最小受控實驗。
- [ ] 為何加入 3D token 後 Object Size 從 70.82 退化至 69.15（Table 6），失敗案例集中於哪些 object size scale 或 viewpoint 條件？
- [ ] CUT3R 在每個測試 scene 的 reconstruction error（例如 chamfer distance、camera pose error）與該 scene 上 VSI-Bench task accuracy 的 per-scene 相關係數是多少？
- [ ] VSTI-Bench 138.6K 自動生成 QA 與其報告的 Human Level 77.0 之間，人工抽檢的 question validity 與 answer correctness 比例為何？
- [ ] 模型在 ScanNet 家族之外（例如 Matterport3D、Hypersim、KITTI）的場景上是否仍維持 VSI-Bench 等級的相對排名，或退化至 base model 水準？
- [ ] view token $z'_t$ 對 Camera Displacement 與 Camera Movement Direction 兩個任務分別貢獻多少？目前 Table 6 只回報 overall avg，缺乏 per-task ablation。
- [ ] 將 CUT3R 解凍並以小學習率聯合微調，能否同時改善 Object Size regression 與一般 Video-MME 表現？

### 8.2 Improvement Directions

1. **加入「同 base model + VGGT」對照實驗**：在 LLaVA-NeXT-Video-7B 與相同 200K 訓練資料下，將 CUT3R 替換為 VGGT 並比較 Absolute Distance、Object Size、Room Size 的 delta。此為孤立 metric-scale claim 最直接的方式，且只需替換 spatial encoder，工程成本可控。
2. **以 LoRA 解凍 CUT3R 的 decoder $f_{dec}$**：當前 CUT3R 全程 frozen 是 Object Size regression 的最可能來源；對 $f_{dec}$ 加入 LoRA 並以下游 task loss 微調，理論上可使幾何 token 對齊 VLM 的需求空間，且不會破壞 CUT3R 的 metric-scale 預訓練先驗。
3. **VSTI-Bench 的人工抽樣驗證**：對每個子任務隨機抽取 200-500 筆 QA 進行 human label 檢驗，並回報 inter-annotator agreement。此為相對 cheap 的 credibility upgrade，可顯著提升基準的引用價值。
4. **per-task ablation 補強**：將 Table 6 拆解至 VSI-Bench 與 VSTI-Bench 的子任務層級，特別呈現 view token 對 Camera Displacement、spatial token 對 Object Size 的個別影響。實作上只需重跑既有 ablation 變體於完整 task split。
5. **加入 dynamic-scene 訓練資料**：在現有靜態管線之外整合 MonST3R 或 DynamicVerse 類型的動態場景重建，使 VSTI-Bench 後續版本可包含真正的物體運動，並驗證 view token 是否能在「相機與物體同時運動」設定下仍解耦兩者。
6. **Object Size-targeted loss**：針對 ablation 中觀察到的 size regression，加入以 ground-truth bounding box 尺寸為監督的輔助 head，在 spatial token 路徑上強化尺寸資訊保留，不影響其他任務 backbone。
