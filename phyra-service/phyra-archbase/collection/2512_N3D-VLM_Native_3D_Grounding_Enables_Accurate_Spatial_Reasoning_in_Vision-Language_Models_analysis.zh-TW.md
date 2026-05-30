<!-- type: paper-read-notes | generated: 2026-05-08 | lang: zh-TW -->

# N3D-VLM — N3D-VLM: Native 3D Grounding Enables Accurate Spatial Reasoning in Vision-Language Models

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | N3D-VLM |
| Paper full title | N3D-VLM: Native 3D Grounding Enables Accurate Spatial Reasoning in Vision-Language Models |
| arXiv ID | 2512.16561 |
| Release date | 2025-12-18 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2512.16561 |
| PDF link | https://arxiv.org/pdf/2512.16561v1 |
| Code link | — |
| Project page | https://n3d-vlm.github.io |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Yuxin Wang | HKUST; Tencent AI Lab (intern) | https://w-ted.github.io/ | first author |
| Lei Ke | Tencent AI Lab | — | co-author |
| Boqiang Zhang | Tencent AI Lab | — | co-author |
| Tianyuan Qu | Tencent AI Lab; CUHK | — | co-author |
| Hanxun Yu | Tencent AI Lab; ZJU | — | co-author |
| Zhenpeng Huang | Tencent AI Lab; NJU | — | co-author |
| Meng Yu | Tencent AI Lab | — | co-author |
| Dan Xu | HKUST | https://www.danxurgb.net/ | corresponding author |
| Dong Yu | Tencent AI Lab | — | senior author |

### 1.2 Keywords

vision-language model, 3D grounding, spatial reasoning, monocular depth, chain-of-thought, RGB-D, 3D bounding box, data lifting

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Qwen2.5-VL [2] | base model | Base VLM that N3D-VLM fine-tunes for native 3D grounding and spatial reasoning. |
| SpatialRGPT / SpatialRGPT-Bench [8] | baseline | Region-level 2D spatial reasoning baseline; its bench is extended into N3D-Bench. |
| SpatialVLM [6] | predecessor | Single-RGB spatial QA without explicit 3D grounding; motivates native 3D approach. |
| SpatialLM [22] | baseline | Point-cloud 3D grounding limited to indoor categories; compared on grounding tasks. |
| SpatialReasoner [21] | baseline | Estimates object position/orientation but lacks size and broad generalization. |
| Omni3D [4] / DetAny3D [37] | predecessor | Prior single-image 3D detection datasets (~234K/~450K), surpassed by 2.78M lifted set. |
| Depth/intrinsics estimator [32] | influence | Used to lift 2D boxes into metric 3D and align inference-time depth/coordinate frame. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於賦予視覺語言模型 (VLM) 真正的 3D 空間理解能力。作者觀察到現有 VLM 多以 2D 影像為中心,缺乏對深度與物體在 3D 空間中位置/尺寸的內在感知,因而難以回答涉及距離、方位、相對大小等空間推理問題。本研究主張將 3D 空間理解拆解為「3D 物體定位 (grounding)」與「基於定位結果的 3D 空間推理」兩階段,並構建一個統一的 RGB-D 模型 N3D-VLM,以結構化語言直接輸出 3D bounding box (含 u, v, z 與 sx, sy, sz),再以鏈式思考 (CoT) 進行可解釋的幾何運算。為解決 3D 訓練資料稀缺問題,作者透過單目深度估計把大規模 2D 偵測標註提升到 3D,構建 2.78M 樣本資料集與 N3D-Bench 評測集,涵蓋多物體、視角轉換與 CoT 推理。

### 2.2 Domain Tags

- computer vision
- vision-language models
- 3D scene understanding
- spatial reasoning

### 2.3 Core Architectures Used

- **Qwen2.5-VL**:本研究的基底 VLM,N3D-VLM 在其上進行兩階段微調以加入 native 3D grounding 與 CoT 空間推理能力。
- **N3D-VLM (本文提出)**:統一的 RGB-D vision-language 框架,接受 image 與 monocular depth 輸入,直接輸出 metric-scale 3D bounding box 並進行顯式空間推理。
- **3D-aware Visual Encoder with Depth-aware Sinusoidal Positional Encoding (本文提出)**:把預測深度 back-project 為 point cloud 後,以 sinusoidal positional encoding 將座標 $(x, y, z)$ 注入 image features,確保 3D 幾何資訊在 token 層級可用。
- **Structured-language 3D Bounding Box Representation (本文提出)**:以 `bbox(id, class, u, v, z, sx, sy, sz)` 的結構化語言格式表示 3D 物體框,使 LLM 能以序列方式輸出可解碼的幾何結果。
- **CoT-based Spatial Reasoning Templates (本文提出)**:在 grounded 3D box 之上以模板化幾何步驟 (向量、夾角、時鐘方位) 生成顯式推理鏈,搭配 LLM 重述以提升自然度。
- **Monocular Depth & Camera Intrinsics Estimator [32]**:作為資料生成與推論時共享的深度/相機座標來源,確保訓練與推論在同一 metric 座標框架。
- **External 2D Segmentation & Tagging Models (SAM-style [24], RAM [38])**:用於 2D-to-3D lifting pipeline,提供物體 mask 與開放詞彙標籤,協助從 COCO/Objects365/OpenImages 構建 2.78M 規模的 3D 標註庫。

### 2.4 Core Argument

作者主張現有 VLM 之所以無法穩健地進行 3D 空間推理,根本原因在於模型「沒有原生的 3D 物體感知」: 既有方法要不依賴外部偵測/分割模組提供框,要不假設場景已具備 3D 標註,要不僅以端到端黑箱從 2D 像素直接輸出答案。這類做法導致 (1) 推理過程無法解釋、(2) 在物體類別與場景多樣性上難以泛化、(3) 一旦缺少外部模組或先驗 3D 資訊便完全失效。基於此診斷,作者主張正確解法必須讓 VLM 自身就具備「以文字描述為條件、直接輸出 metric-scale 3D bounding box」的能力,並讓所有空間推理顯式建立在這些 3D 框之上。為使這個目標可實現,他們進一步指出兩個必要條件:其一,3D 訓練資料必須在類別與場景上達到 2D 偵測等級的規模與多樣性,因此採用單目深度模型把 COCO/Objects365/OpenImages 等 2D 標註批次 lift 到 3D,規模達既有單張影像 3D 偵測資料集的六倍以上;其二,推理階段必須與資料生成階段共享同一個深度/相機座標系,因此模型在輸入端引入 depth-aware sinusoidal positional encoding,將 back-project 後的點雲座標注入影像特徵,確保預測的 3D 框落在一致的 metric 座標框架。最後,以 CoT 模板生成顯式幾何步驟 (向量、夾角、時鐘方位等),把空間推理從不可解釋的端到端輸出,轉為以 3D 框為基礎的可驗證計算,從而在邏輯上完整封閉「原生 3D 感知 → 顯式 3D 推理」這條鏈路。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(245 words)

標題「N3D-VLM: Native 3D Grounding Enables Accurate Spatial Reasoning in Vision-Language Models」直接點明全文兩個耦合命題：(1) 把 3D grounding「原生」放進 VLM 內部；(2) 這個能力能解鎖 accurate spatial reasoning。標題刻意把 native 3D grounding 設為原因、把 spatial reasoning 設為結果，預告全文的因果敘事——並非把 grounding 當輔助任務，而是把它當作 reasoning 的前置基礎。

Abstract 接著把這個因果敘事展開成四段論述。第一句先建立問題：當前 multimodal model 雖能基於 2D image 回答問題，但缺乏 intrinsic 3D object perception，導致無法理解 spatial relationship 與 depth cue。第二句宣告解法：N3D-VLM 是一個 unified framework，把 native 3D object perception 與 3D-aware visual reasoning 整合在同一模型中。第三句點出與 conventional end-to-end 模型的關鍵差異——後者直接從 RGB/RGB-D 輸出答案，而 N3D-VLM 先用 textual description 在 3D 空間中 localize objects、再 explicitly reason，因此提供 interpretable 與 structured 的空間理解。

第四段則指出 enabling factor 是資料：作者建立 scalable data construction pipeline，用 depth estimation 把大規模 2D annotation lift 到 3D，產生比目前最大 single-image 3D detection dataset 多六倍的訓練資料，同時生成 CoT-oriented spatial QA。最後一句以 SOTA 作為承諾：在 3D grounding 與 3D spatial reasoning 兩類任務上同時超越既有方法。Abstract 因此為後續章節鋪設了三條主線——unified architecture、data lifting pipeline、雙任務 SOTA——讀者進入 §1 時已知道每一節各自要驗證哪一條主線。

### 3.2 Introduction

(720 words)

Introduction 採取「問題—文獻不足—觀念重構—解法—資料挑戰—貢獻」的六段式結構，把 abstract 的承諾展開為論證鏈。第一段從 VLM 的 2D 多模態能力切入，指出 real-world application 需要更深的 3D 結構與 spatial relationship 理解，而 effective 3D spatial reasoning 必須以 object-level 3D perception 為前提；缺少它，模型就無法 infer spatial configuration 或推理物理環境。這一段把「邁向真正多模態智慧」綁定到「具備 robust 3D 能力」上，建立任務動機。

第二段審視既有 specialized VLM 的三條路線：依賴 external perception model 取得 2D/3D box 或 mask、假設 3D box 或 spatial layout 已知、或讓 VLM 直接在 point cloud 中定位。作者指出三者共同弱點——侷限於有限類別的受限場景、依賴外部模組或預設空間資訊、且不支援 explicit spatial reasoning，因此難以泛化或整合進 unified VLM。

第三段是全文的觀念樞紐：作者主張 3D spatial understanding 應分解為 3D object localization 與 subsequent 3D spatial reasoning 兩個 core ability，並把 explicit 3D object perception 設為 reasoning 的 critical foundation。這個分解直接解釋了後文為何採用 grounding-then-reasoning 的兩階段設計，也解釋為何 grounded 3D bounding box 能同時提升 accuracy 與 interpretability。

第四段把分解落實到 N3D-VLM 設計：一個整合 3D detection、grounding 與 CoT reasoning 的 unified VLM，能直接 localize 物件、捕捉 depth cue，並在 grounding 結果上進行 inter-object distance 計算或 relative size 比較。作者特別與 SpatialLadder、SpatialReasoner 等 recent work 切割——後者只用 3D coordinate 或 2D grounding data 輔助理解，而 N3D-VLM 預測 comprehensive 3D bounding box，使 reasoning 更 generalizable 與 interpretable。

第五段轉向 enabling factor：3D 訓練資料稀缺。indoor 與 autonomous driving 的既有資料集 diversity、scale、category 都不足；相對地 2D detection 資料集場景與類別豐富。這一段為 §3.1 的 data lifting pipeline 鋪路。

第六段承諾解法：用 depth 與 camera estimation model lift 2D annotation 到 3D，並建構 spatial QA dataset 監督 CoT reasoning；同時為了確保 3D 輸出的 real-world scale 與 camera geometry 一致，data construction 與訓練使用同一 depth model，並導入 depth-aware positional encoding 注入 explicit depth cue。

第七段以三條 contribution 收束：unified RGB-D 模型具備 native 3D detection/grounding、data construction pipeline 把 2D 標註 lift 至 3D、以及 N3D-Bench 涵蓋 single/multi-object 與 explicit reasoning process 的 benchmark。Introduction 因此完整鋪好後續章節閱讀路徑：§2 對應第二段的文獻定位、§3.1 對應第五至六段的資料解法、§3.2 對應第四段的架構解法、§3.3 對應第七條 benchmark 貢獻、§4 則驗證所有 claim。

### 3.3 Related Work / Preliminaries

(580 words)

Related Work 分成 §2.1「VLM for 3D Spatial Understanding」與 §2.2「VLM for 3D Object Localization」兩節，刻意對應 §1 第三段的「localization + reasoning」二分。這個切分讓讀者立刻看出 N3D-VLM 想同時補上的兩個缺口：既有 spatial reasoning 工作缺 explicit 3D grounding，既有 3D grounding 工作缺 reasoning。

§2.1 把現有 spatial understanding 工作分為兩條技術路徑。第一條使用 point cloud、video、RGB/RGB-D 等 3D 或近 3D modality：GPT4Scene 從 point cloud 生成 object-marked image 加上 BEV 進行 3D captioning 與 QA、Think-in-Space 支援 multiple-choice route planning 與 relative distance reasoning。作者批評它們依賴額外的 3D 資訊或 object-level annotation，且通常侷限於 indoor environment。第二條從純 2D input 推理 spatial relation：SpatialVLM 處理 left/right/front/behind 等 single-image QA、SpatialRGPT 進一步支援 region-level reasoning。但這條路徑要不是 black-box end-to-end，要不就需要 external module 做 region localization，缺乏 explicit 3D 空間理解。這兩條批評共同指向同一個結論：不管是否使用 3D modality，現有方法都沒有把 3D grounding 顯式整合進 reasoning chain。

§2.2 處理 3D visual grounding 文獻。VLM-Grounder 透過 2D segmentation、multi-view matching 與 ensemble projection 在 video frame 上 localize 3D 物件；SeeGround 在已知 object position 的 view 下進行 3D grounding。這些方法依賴 external segmentation tool 或預先給定的 object-level information。SpatialLM 從 point cloud 預測 3D bounding box，但限於 indoor scene 的小類別集合且不支援 grounding 之外的 reasoning。SpatialReasoner 加入 object position 與 orientation 估計，但場景受限、不捕捉 object size、泛化能力差。

兩節文獻評析最後共同收束到 N3D-VLM 的差異化定位：模型 generalize 到多樣場景、輸出包含完整尺寸與位置的 full 3D bounding box，並同時支援 3D detection、3D grounding 與 downstream spatial reasoning。

值得注意的是，作者把 §3 The Proposed Framework 的開頭也納為 preliminaries 角色——它先用 (I, D) 形式化輸入、再說明 depth map D 可由 monocular depth estimation model 取得，並把 framework 拆成 data construction (Fig. 2) 與 model design with training/evaluation (Fig. 3) 兩大組件。這段定位文字其實是 Related Work 與 Method 之間的橋：它接住 §2 對「需要 unified、generalizable、grounding-driven reasoning」的批評，同時為 §3.1 的 data pipeline 與 §3.2 的 model architecture 設好討論順序——先解決 data scarcity，再談如何把 3D 線索注入 VLM。

### 3.4 Method (overview narrative)

(1500 words)

§3 整體採取「資料先行、架構次之、benchmark 收尾」的三段敘事。這個排序不是隨意的——它對應 §1 第五至六段的觀察「3D capability 的瓶頸首先是資料」，因此在解釋 model architecture 之前，先說服讀者作者已建立可支撐訓練的 3D 標註基礎。

§3.1 是整章佔篇幅最大的子節，分三步走。第一步「3D Detection Annotation Repository」說明 lifting pipeline：對 2D 標註的 image 取得 SAM2-style segmentation mask 與 monocular depth、把 depth back-project 成 camera-space point cloud、再結合 category 與 mask 推得 3D bounding box，並用 rule-based filter 移除 outlier 與不合理大小的 box。作者特別量化貢獻——2.78M 樣本，比 Omni3D 約 234K 與 DetAny3D 約 450K 大六倍以上——並列出三個來源 COCO、OpenImages、Objects365；對 OpenImages box 數較少的問題用 RAM 重新偵測補齊。第二步「Generation of 3D Localization Data」介紹 structured language 表示：每個 box 編碼為 `bbox(id, class, u, v, z, sx, sy, sz)`，其中 $(u, v)$ 是 3D 中心在 image plane 的投影、$z$ 為 depth、$s_x, s_y, s_z$ 為三軸尺寸；給定 camera intrinsics，$(u, v, z)$ 與 $(x, y, z)$ 可雙向轉換。Detection QA 直接由標註生成；grounding QA 採三策略——選取 category-unique 物件、處理多 instance 同類別物件（如 "Locate all the boys"）、以及對難以用 category 描述者改用 referring expression 或在 image 上渲染 2D box。第三步「Generation of 3D Spatial Reasoning Data」說明如何在 3D detection repository 上隨機取樣物件、套用 predefined template、產生包含確定性數值計算的 reasoning chain，再以 LLM rephrase 提升自然度。問題類型 follow SpatialRGPT 涵蓋相對 scale、spatial relation、absolute distance、clock direction、object dimension，並擴展到三個或更多物件的 multi-object reasoning。Fig. 2 中 boy/stroller 的 clock-direction 範例展示完整 reasoning chain：取出兩物件 3D 中心、計算 xz-plane 向量、求出與 positive x-axis 的夾角、再轉成 clock position。

§3.2 闡述 model architecture，分兩個重點。「3D-aware Visual Encoding」先解釋為何採用 [32] 的 depth estimation model——它同時預測 depth map 與 camera intrinsics，保證所有預測 3D box 落在 metric scale 與一致的 coordinate system。隨後給出 fusion pipeline：先把每個像素 back-project 為 camera coordinate $P_{ij} = D_{ij} \cdot \text{intr}^{-1} \cdot [u_j, v_i, 1]^T$，得到 dense point cloud $P \in \mathbb{R}^{H \times W \times 3}$，再 downsample 到 $\hat{P} \in \mathbb{R}^{h \times w \times 3}$ 對齊 image feature $F_{img}$ 的空間解析度。對每個 3D 座標 $(x, y, z)$，沿三軸分別套用 sinusoidal positional encoding，再求和得到 $e_{coord} = \sum_{k \in \{x, y, z\}} \text{PE}(k)$，最後加到 image feature 上 $\tilde{F}_{img} = F_{img} + e_{coord}$。融合後 feature map 連同 prompt token 進入 LLM 進行 autoregressive prediction。「Training Strategy and Inference Pipeline」說明以 Qwen2.5-VL 為 base 進行兩階段訓練：第一階段訓 3D object localization、第二階段以 spatial reasoning 與部分 localization data 混合訓練 grounding-based reasoning，encoder 與 LLM 全參數 learnable。Inference 提供兩種模式——直接問空間問題讓模型自動分解為 grounding + reasoning，或先 explicit request grounding 再 follow-up 問題。

§3.3 補上 N3D-Bench 作為評估配套。作者批評現有 benchmark 場景與類別範圍狹窄，因此手動 curate 1,200 open-ended 與 800 numerical 含 CoT reasoning 的問題。Tab. 1 對比 SpatialRGPT-Bench：問題量從 1,406 提升到 2,000、object category 從 88 擴到 264（三倍）、物件數從 $\{1, 2\}$ 擴到 $\{1, 2, 3, >3\}$、新增 view change 與 explicit CoT reasoning 兩個維度。這節同時為 §4 的 N3D-Bench 結果做鋪墊，並讓讀者知道作者的評估難度設計超越既有 benchmark。整體來看，§3 透過 data → architecture → benchmark 的順序，把 §1 第三段的 localization+reasoning 二分論述完整落地，每個子節各自回應一個 §1 中提出的挑戰。

### 3.5 Experiments (overview narrative)

(1100 words)

§4 採取「setup → main results → ablation → causal mechanism」的標準 experiments 敘事，但在排序上刻意把 4.4 「3D Grounding Helps Spatial Reasoning」放在最後，作為對全篇核心 claim 的因果驗證。

§4.1 Experimental Setup 同時說明資料、metric 與三個 benchmark 的角色分工。訓練資料來自 §3.1 的 OpenImages、Objects365、COCO 三個來源衍生的 3D localization 與 spatial reasoning 集合。評估則設計三個 benchmark 對應不同維度：N3D-Bench 是作者自建的 multi-object、CoT、view-change benchmark；SpatialRGPT-Bench 涵蓋 1,404 open-ended 與 numerical 題、確認與既有評測一致；CV-Bench-3D 提供 1,200 multiple-choice 題、檢驗 multiple-choice format 下的泛化。3D grounding 用 RefCOCO 系列加上額外 Objects365 test set。Metric 上，spatial reasoning 對 open-ended 用 GPT-4o LLM-as-a-judge、numerical 用 ±25% tolerance string matching；grounding 同時報 projected IoU/center offset（將 3D box 投影到 image plane）與 3D IoU/3D offset（depth-aligned 後計算），3D metric 因 alignment noise 限定在 sampled subset。為了 fair comparison，除 SpatialRGPT 外所有方法在 SpatialRGPT-Bench 都以 image 上的 box 提供 object reference。

§4.2 Main Results 同時包含 spatial QA 與 grounding 兩類成果。在 spatial QA（Tab. 2）上，N3D-VLM-7B 在所有 benchmark 都拿下最高 accuracy。作者用兩個對比強化敘事：相對 base model Qwen2.5-VL-7B 提升明顯，特別在 numerical 題上，顯示 grounding-based reasoning 突破標準 QA 的數值理解上限；相對更新的 Qwen3-VL，雖然後者在 spatial reasoning 上勝過 Qwen2.5-VL，但 numerical 仍卡在 36.3% 與 40.7%，而 N3D-VLM 跑到 92.1% 與 78.0%。即使是 numerical 較強的 SpatialRGPT，在 N3D-Bench 上也只有 50.4%、仍遠落後 92.1%。在 3D object grounding（Tab. 3、Tab. 4、Fig. 4）上，N3D-VLM-7B 在 RefCOCO/+/g 與 Objects365 的 projected IoU/offset 全面領先 Qwen3-VL-8B 與 Qwen3-VL-30B-A3B；3D IoU 從 Qwen3-VL-30B 的 0.27 提升到 0.48、3D offset 從 1.86 降到 0.36。Fig. 4 的 qualitative 比較橫跨 indoor 與 outdoor 多樣場景，補強 grounding 泛化性的 claim。

§4.3 Ablation Study on Model Design 在 Objects365 5,565 image、341 class 的 validation set 上跑 3D detection F1@0.25。Tab. 5 列五個變體：(0) SpatialLM 原架構在 diverse point cloud 上崩盤（F1 2.2），暴露 point-cloud-encoder 路線的泛化問題；(1) 拿掉 depth input 的 3B 模型 F1 9.4；(2) 採 camera-space xy 預測 F1 10.8；(3) 採 image-space uv 預測 F1 12.8；(4) 把訓練量從 340K 擴到 1.7M 後 F1 跳到 22.9。三組對比分別驗證三個 design choice：(1)→(3) 顯示 depth input 帶來 +3.4 F1、(2)→(3) 顯示 image-space uv 優於 camera-space xy（作者解釋這是因為 base model 的 2D perception pretraining 與 image space 自然對齊）、(3)→(4) 顯示資料規模化貢獻最大、提升 +10.1 F1，回扣 §3.1 data pipeline 的價值。

§4.4 是全章敘事高潮：兩個實驗證明 native 3D grounding 顯式提升 spatial reasoning。第一個實驗把 N3D-VLM 的 grounding 結果餵給 Qwen3-VL，open-ended 從 66.3 升到 71.3（+7.5%）、numerical 從 36.3 升到 54.6（+50.4%），證明 grounding 對 reasoning 確實有正向因果效應；但 71.3 與 54.6 仍低於 N3D-VLM-7B 的 89.7 與 92.1，顯示作者模型不只受惠於 grounding，本身的 reasoning 能力也經過訓練。第二個實驗保留同一架構但 end-to-end 訓 QA，得到 80.6 與 62.4，仍低於 89.7 與 92.1，證明把 grounding 與 reasoning explicit 分開比 implicit 端對端更有效。兩實驗合起來把 §1 「localization + reasoning」二分論述從架構主張推進到 causal evidence。

### 3.6 Conclusion / Limitations / Future Work

(105 words)

§5 Conclusion 篇幅極短、語氣節制，但完整收束全文三條敘事主線。第一句重申 unified framework 立場：N3D-VLM 在單一模型內銜接 3D object perception 與 spatial reasoning，回扣 §1 第三段提出的 localization + reasoning 二分主張。第二句強調此整合的兩個正向後果——native 3D grounding 提供 accurate localization、explicit 3D-aware reasoning 提供 interpretable spatial understanding——把 §4.2 的 SOTA 與 §4.4 的因果證據濃縮成一句宣告。第三句把功勞歸給 enabling factor：scalable data construction pipeline 把 2D 標註投影到 3D，並支援建構 explicit reasoning dataset，使模型展現 reasonable generalization 與 structured reasoning foundation。最後一句以 extensive experiments 作為 closing 證據，再次強調 3D grounding 與 3D spatial reasoning 雙任務 SOTA。

值得指出的是，paper main text 的結論並未設置獨立的 Limitations 或 Future Work 段落——這對 main paper 是常見作法。但作者把侷限性的討論搬到 supplementary material 的 §A.3 Failure Cases：第一個失敗案例顯示模型把水面 duck reflection 誤識為實體，顯示模型對 specular reflection 的理解仍不足；第二個案例中模型雖在密集 jellyfish 場景成功偵測 30 隻、但仍漏掉若干個體，顯示在 dense object scene 下 3D grounding 仍有空間。這兩個 failure case 提供未來方向：specular/transparent surface 處理、以及 high-density 場景的 grounding recall。整體而言，conclusion 重述貢獻、附錄補上 honest 的 limitation 揭露，雖未顯式寫 future work，但兩個 failure mode 已自然指向後續研究路徑。

## 4. Critical Profile

### 4.1 Highlights

- N3D-VLM-7B reaches $92.1\%$ on N3D-Bench numerical questions versus $36.3\%$ for Qwen3-VL-8B and $50.4\%$ for SpatialRGPT, a 41.7-point gap on the headline metric (Table 2, p.7).
- The lifted 3D detection corpus contains 2.78M samples, roughly $12\times$ Omni3D ($\sim$234K) and $6\times$ DetAny3D ($\sim$450K), and is the central data contribution (§3.1, p.4).
- Projected IoU on RefCOCO climbs to $0.59$ versus $0.37$ for Qwen3-VL-8B and $0.38$ for Qwen3-VL-30B-A3B; on Objects365 the gap is $0.61$ vs $0.28$ (Table 3, p.7).
- After depth alignment, 3D IoU on RefCOCO/+/g reaches $0.48$ versus $0.27$ for Qwen3-VL-30B-A3B, with 3D center offset dropping from $1.86$ m to $0.36$ m (Table 4, p.7).
- Feeding N3D-VLM grounding outputs to a frozen Qwen3-VL lifts its N3D-Bench numerical accuracy from $36.3$ to $54.6$ ($+50.4\%$), giving direct evidence that explicit 3D boxes help downstream reasoning (Table 6, p.8).
- An end-to-end QA-only ablation of the same architecture only reaches $62.4$ numerical accuracy versus $92.1$ for the staged grounding-then-reasoning model, validating the decomposition (Table 6, p.8).
- Two design choices are isolated cleanly: adding depth input lifts $F_1@0.25$ from $9.4$ to $12.8$, and predicting pixel-space $(u, v)$ centers beats camera-space $(x, y)$ ($10.8 \to 12.8$) (Table 5, p.7).
- Scaling lifted training data from $340$K to $1.7$M nearly doubles $F_1@0.25$ ($12.8 \to 22.9$), supporting the data-scale claim of the lifting pipeline (Table 5, p.7).
- N3D-Bench triples the object-category coverage of SpatialRGPT-Bench ($264$ vs $88$) and is the first bench to combine multi-object reasoning, viewpoint shift, and explicit CoT in a single suite (Table 1, p.6).

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- Specular reflections are mistaken for real objects: a duck's reflection on water is grounded as a real duck (Fig. 9, §A.3, p.11).
- Dense-scene recall is incomplete: in the jellyfish example the model detects 30 but still misses several visible instances (Fig. 9, §A.3, p.11).
- 3D IoU and 3D center offset are reported only on a "sampled subset" after aligning predictions to ground-truth depth, explicitly to "mitigate the alignment noise" (§4.1 Metrics, p.6).
- SpatialReasoner [21] is omitted from 3D grounding tables because, even when prompted, its outputs "were inconsistent and often failed to follow a coherent 3D coordinate format" (§A.1, p.11), so the strongest "explicit 3D reasoning" prior is not directly compared on grounding.

#### 4.2.2 Phyra-inferred

- Training pseudo-labels, inference depth, and the depth alignment used at evaluation all come from the same model, MoGE-2 [32]; any systematic bias in MoGE-2's metric scale is therefore present in the labels, in the input, and in the evaluation oracle simultaneously, so the experiments cannot separate "the model learned 3D" from "the model learned MoGE-2's depth".
- The numerical-accuracy metric is a $\pm 25\%$ tolerance match (§4.1, p.6) — for a $2$ m distance any prediction in $[1.5, 2.5]$ m counts as correct — and no tighter threshold or absolute-error number is reported, so the $92.1\%$ headline rests on a permissive band.
- CoT answers are generated from fixed geometric templates plus an LLM rephrase (§3.1, p.5); the model is trained to imitate the deterministic formula path, so generalization to question forms outside SpatialRGPT-style templates is untested.
- N3D-Bench is constructed by the authors using the same lifting pipeline as training (§3.3, p.6); category coverage is broader than SpatialRGPT-Bench but the question-generation distribution and the depth backbone are shared with training, so the $90+\%$ numbers are partly self-evaluated.
- 3D extents $(s_x, s_y, s_z)$ are derived from the visible back-projected point cloud (§3.1, p.3–4), which systematically truncates occluded sides of objects; no ablation against truly 3D-annotated data quantifies this pseudo-label ceiling.
- SpatialLadder is 3B, while N3D-VLM-7B is the headline number; a fully like-for-like 7B comparison only covers Qwen2.5-VL-7B, Qwen3-VL-8B, SpatialReasoner-7B, and SpatialRGPT-VILA-1.5-8B, which is a narrower peer set than Table 2 suggests.

### 4.3 Phyra's Judgment (summary)

The genuinely new contribution is the *staged decomposition* — a single VLM that emits structured 3D bounding boxes and then runs explicit geometric CoT over them — combined with the engineering insight that monocular depth lifting can scale 3D supervision $6\times$ beyond DetAny3D. The architectural pieces (depth-aware sinusoidal PE, pixel-space $(u,v,z)$ output) are individually unsurprising, but the ablations defending them are tight. What remains unresolved is whether the headline gains reflect a 3D world model or a tight co-adaptation to MoGE-2's depth field and to template-matched benchmarks the authors built themselves; the paper does not run the experiments that would separate these.

## 5. Methodology Deep Dive

### 5.1 Method Overview

N3D-VLM 將「3D 空間理解」拆解為兩個可分離的子任務:**3D 物體定位 (grounding)** 與 **基於 3D 框的空間推理 (CoT reasoning)**,並將兩者整合在單一 vision-language model 中。模型以 RGB-D 為輸入 (RGB 影像 $I$ 加上由單目深度估計模型 [32] 預測的 metric-scale depth map $D$ 與相機內參 $\text{intr}$),並以結構化語言的形式直接輸出 3D bounding box,box 的表示為 `bbox(id, class, u, v, z, sx, sy, sz)`,其中 $(u, v)$ 為 3D 中心在影像平面上的 2D 投影、$z$ 為深度、$(s_x, s_y, s_z)$ 為三軸尺寸。給定相機內參,$(u, v, z)$ 與相機座標系下的 $(x, y, z)$ 可透過 deterministic projection 互轉,因此這個表示同時保留了 metric scale 與與既有 2D 預訓練資料的 image-space 對齊。

模型架構的核心是 **3D-aware visual encoding**:將每個像素以 $P_{ij} = D_{ij}\cdot \text{intr}^{-1}\cdot [u_j, v_i, 1]^\top$ back-project 為 3D 點,得到稠密點雲 $P \in \mathbb{R}^{H\times W\times 3}$,再降採樣成 $\hat{P}\in \mathbb{R}^{h\times w\times 3}$ 以對齊 vision encoder 輸出的 image feature $F_{\text{img}}\in \mathbb{R}^{h\times w\times c}$。三軸座標各自做 sinusoidal positional encoding 後相加得到 $e_{\text{coord}}$,並以 $\tilde{F}_{\text{img}} = F_{\text{img}} + e_{\text{coord}}$ 注入幾何訊號。融合後的特徵與 prompt tokens 一起送入以 Qwen2.5-VL [2] 為骨幹的 LLM,以 autoregressive 方式產生 grounding 結果或 CoT 推理。

訓練採兩階段:第一階段以大規模 lifted 3D 偵測 / 定位資料 (2.78M,源自 COCO、Objects365、OpenImages,經 SAM2 [24] 取 mask、MoGe-2 [32] 取 depth、再以 rule-based filter 移除離群與不合理框) 訓練 3D 物體定位;第二階段以 3D spatial reasoning QA 與部分定位資料的混合資料訓練顯式的幾何推理。Encoder 與 LLM 在兩階段中皆為可訓練。在 inference 時,模型支援兩種模式:一是端到端從空間問題自動分解為「先 grounding 再推理」,二是使用者顯式請求 grounding 結果後再追問空間問題;兩者皆以 grounded 3D box 為推理基礎,確保推理可解釋且 metric-scale 一致。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input
  RGB image           I        ∈ [B, 3, H, W]
  Depth map           D        ∈ [B, H, W]            (from MoGe-2 [32])
  Camera intrinsics   intr     ∈ [B, 3, 3]            (from MoGe-2 [32])

I ─▶ Vision Encoder (ViT, Qwen2.5-VL backbone)
       └── F_img                ∈ [B, h, w, c]        (h, w, c = ?, inherited from Qwen2.5-VL)

(D, intr, pixel grid)
   ─▶ Per-pixel back-projection                       (Eq. 1)
       P_ij = D_ij · intr^{-1} · [u_j, v_i, 1]^T
       └── P                    ∈ [B, H, W, 3]
   ─▶ Spatial downsampling to feature resolution
       └── P̂                    ∈ [B, h, w, 3]
   ─▶ Per-axis sinusoidal PE   (axes α ∈ {x, y, z})   (Eq. 2)
       PE(α, 2i)   = sin(α / 10000^{2i/c})
       PE(α, 2i+1) = cos(α / 10000^{2i/c})
       └── PE(x), PE(y), PE(z)  each ∈ [B, h, w, c]
   ─▶ Per-axis sum             (Eq. 3)
       e_coord = Σ_{k∈{x,y,z}} PE(k)
       └── e_coord              ∈ [B, h, w, c]

Feature fusion (Eq. 4): additive injection of geometric cues
   F̃_img = F_img + e_coord     ∈ [B, h, w, c]

   ─▶ Flatten to token sequence
       └── F̃_img                ∈ [B, h·w, c]
   ─▶ Concatenate with prompt tokens of length L_p
       └── input tokens         ∈ [B, h·w + L_p, c]
   ─▶ LLM decoder (Qwen2.5-VL [2], autoregressive)
       └── output tokens (decoded as structured language)

Output
  3D Localization mode  : "bbox(id, class, u, v, z, sx, sy, sz), ..."   (see Fig. 3c)
  Spatial Reasoning mode: "<think> ... </think> answer"                  (CoT over 3D boxes)
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Depth & Intrinsics Estimator (MoGe-2 [32])

**Function:** 從單張 RGB 預測 metric-scale depth map 與 camera intrinsics,使後續 back-projection 與資料生成階段、推理階段共享同一個 metric 座標系。

**Input:**
- Name: $I$
- Shape: $[B, 3, H, W]$
- Source: 使用者輸入的 RGB 影像

**Output:**
- Name: $D$, $\text{intr}$
- Shape: $[B, H, W]$、$[B, 3, 3]$
- Consumer: §5.3.2 back-projection

**Processing:**

直接呼叫 MoGe-2 [32] 的預訓練模型;同一個深度模型也用於 §3.1 的 2D-to-3D lifting 資料生成,藉此確保訓練資料與推理時的 depth/intrinsics 來源一致。

**Implementation Details:**

論文未說明本模型是否在第二階段被微調,僅指出以 MoGe-2 [32] 為深度與內參來源,並將其輸出作為下游模組的固定幾何先驗。

#### 5.3.2 Pixel-to-Camera Back-projection

**Function:** 將每個像素以對應深度與相機內參 back-project 為相機座標系下的 3D 點,生成稠密點雲。

**Input:**
- Name: $D$, $\text{intr}$, 像素座標 $(u_j, v_i)$
- Shape: $[B, H, W]$、$[B, 3, 3]$、像素網格 $[H, W]$
- Source: §5.3.1

**Output:**
- Name: $P$
- Shape: $[B, H, W, 3]$
- Consumer: §5.3.3 downsampling

**Processing:**

對每個像素 $(u_j, v_i)$ 套用 Eq. (1) 進行 back-projection,得到該像素在相機座標系下的 3D 位置。

**Key Formulas:**

$$
P_{ij} = D_{ij}\cdot \text{intr}^{-1}\cdot
\begin{bmatrix} u_j \\ v_i \\ 1 \end{bmatrix}
$$

**Implementation Details:**

論文僅描述座標公式;未說明是否以 batched 矩陣運算或 broadcasting 實作,亦未說明對無效深度像素 (例如 $D_{ij}\le 0$) 的處理是否在此步驟發生 (注:資料生成階段使用 rule-based filter 移除無效深度,推理階段是否同樣處理論文未明示)。

#### 5.3.3 Spatial Downsampling

**Function:** 將像素層級的點雲 $P$ 降採樣到與 vision encoder 輸出特徵圖相同的空間解析度,以便逐位置與影像特徵相加。

**Input:**
- Name: $P$
- Shape: $[B, H, W, 3]$
- Source: §5.3.2

**Output:**
- Name: $\hat{P}$
- Shape: $[B, h, w, 3]$
- Consumer: §5.3.4 sinusoidal PE

**Processing:**

將 $P$ 從 $[H, W]$ 降採樣到 $[h, w]$,使其與 §5.3.5 輸出的 $F_{\text{img}}\in \mathbb{R}^{h\times w\times c}$ 對齊。

**Implementation Details:**

論文未指明降採樣方法 (例如 average pooling、stride sampling、或固定 patch grid 取中心點),亦未指明 $h$、$w$ 的具體數值;這些應與 Qwen2.5-VL [2] vision encoder 的 patch token grid 對齊。

#### 5.3.4 Sinusoidal Coordinate Embedding

**Function:** 將每個 3D 座標 $(x, y, z)$ 編碼為高維向量,使影像特徵在空間上具有 metric 幾何感知。

**Input:**
- Name: $\hat{P}$
- Shape: $[B, h, w, 3]$
- Source: §5.3.3

**Output:**
- Name: $e_{\text{coord}}$
- Shape: $[B, h, w, c]$
- Consumer: §5.3.6 feature fusion

**Processing:**

對 $\hat{P}$ 中每個位置的三個座標軸 $\alpha\in\{x, y, z\}$ 各自計算 sinusoidal positional encoding (Eq. 2,維度 $c$),再對三個軸的編碼逐元素相加 (Eq. 3) 得到 $e_{\text{coord}}$。

**Key Formulas:**

$$
\text{PE}(\alpha, 2i) = \sin\!\left(\frac{\alpha}{10000^{2i/c}}\right),\quad
\text{PE}(\alpha, 2i+1) = \cos\!\left(\frac{\alpha}{10000^{2i/c}}\right),\ \ i = 0, 1, \dots, \tfrac{c}{2}-1
$$

$$
e_{\text{coord}} = \sum_{k\in\{x,\,y,\,z\}} \text{PE}(k)
$$

**Implementation Details:**

論文使用標準 Transformer 風格的 sinusoidal 公式、頻率底數為 10000;未說明是否對 $(x, y, z)$ 在編碼前做歸一化或座標縮放,因此實際的 metric 數值範圍會直接決定不同頻率的相位旋轉,具體尺度處理由原始 metric depth 與下游訓練資料分布隱式決定。

#### 5.3.5 Vision Encoder

**Function:** 從 RGB 影像產生 patch-level 的視覺特徵,是 Qwen2.5-VL [2] 視覺骨幹的一部分。

**Input:**
- Name: $I$
- Shape: $[B, 3, H, W]$
- Source: 使用者輸入的 RGB 影像

**Output:**
- Name: $F_{\text{img}}$
- Shape: $[B, h, w, c]$
- Consumer: §5.3.6 feature fusion

**Processing:**

直接使用 Qwen2.5-VL [2] 的 ViT-style vision encoder 產生 patch token 特徵,並 reshape 回 $[h, w]$ 空間網格。

**Implementation Details:**

具體 patch size、$h$、$w$、$c$ 之數值論文未明示,皆由 Qwen2.5-VL [2] 的設定決定;在第一與第二階段訓練中,encoder 全部參數皆為可訓練 (`learnable`)。

#### 5.3.6 3D-Aware Feature Fusion

**Function:** 將深度感知的座標嵌入加到影像特徵上,讓每個 visual token 同時帶有「外觀」與「3D 位置」資訊。

**Input:**
- Name: $F_{\text{img}}$、$e_{\text{coord}}$
- Shape: $[B, h, w, c]$、$[B, h, w, c]$
- Source: §5.3.5、§5.3.4

**Output:**
- Name: $\tilde{F}_{\text{img}}$
- Shape: $[B, h, w, c]$
- Consumer: §5.3.7 LLM decoder

**Processing:**

逐位置、逐通道相加 (Eq. 4),不引入額外可訓練參數。

**Key Formulas:**

$$
\tilde{F}_{\text{img}} = F_{\text{img}} + e_{\text{coord}}
$$

**Implementation Details:**

採用最簡單的 additive injection,而非 concatenation 或 cross-attention;這也使得 ablation (Table 5 中變體 (1) 移除 depth 輸入) 可以直接以「不加 $e_{\text{coord}}$」實現,結果顯示加入 depth 提升 F1@0.25 從 9.4 至 12.8。

#### 5.3.7 LLM Decoder (Qwen2.5-VL Backbone)

**Function:** 以 autoregressive 方式產生結構化語言,輸出可以是 3D bbox 序列 (定位模式) 或 `<think>...</think>` 形式的 CoT 推理 (空間推理模式)。

**Input:**
- Name: 攤平後的 $\tilde{F}_{\text{img}}$ 與 prompt tokens
- Shape: $[B, h\cdot w, c]$ 串接 $[B, L_p, c]$,合計 $[B, h\cdot w + L_p, c]$
- Source: §5.3.6;text tokenizer 處理使用者問題

**Output:**
- Name: 解碼後的 token 序列
- Shape: $[B, L_{\text{out}}]$ (token id 序列)
- Consumer: 終端輸出 (定位結果或推理答案)

**Processing:**

- 第一階段:在 2.78M lifted 3D 偵測 / 定位資料上訓練 3D 物體定位,輸出 `bbox(id, class, u, v, z, sx, sy, sz)` 序列。
- 第二階段:以 3D spatial reasoning QA 與部分定位資料混合訓練,輸出包含顯式幾何步驟的 CoT,例如以 $\arctan2$ 計算 clock 方位、以歐式距離比較相對距離等。
- 推理階段支援兩種模式:模型自動分解 (先 ground 再推理) 或使用者顯式分步請求。

**Key Formulas:**

CoT 推理示例 (來自 §3.1):給定兩物體中心 $\mathbf{a},\mathbf{b}\in\mathbb{R}^3$,在 $xz$ 平面上計算向量、夾角與 clock 位置:

$$
\theta = \operatorname{atan2}(b_z - a_z,\ b_x - a_x),\quad
\text{clock} = 12 - \left\lfloor \frac{\theta_{\text{deg}}}{30} \right\rfloor
$$

**Implementation Details:**

LLM 採 Qwen2.5-VL [2] 為基底,encoder 與 LLM 全部參數皆於兩階段中持續訓練 (`fully learnable`);具體層數、注意力頭數、隱藏維度 $c$、序列長度上限等皆繼承 Qwen2.5-VL,論文未另行指定。對於 RefCOCO/+/g 與 Objects365 上的評測,3D 框透過已知 intrinsics 投影為 2D 框並以 IoU 與 center offset 衡量,3D IoU/offset 則在 depth-aligned 子集上報告以減少對齊噪聲 (詳見 §4.1)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| COCO [17] | 2D 偵測標註來源（lifted 至 3D） | the paper does not specify per-source 樣本數 | train |
| OpenImages [13] | 2D 偵測標註來源（以 RAM [38] 重新偵測後 lifted 至 3D） | the paper does not specify per-source 樣本數 | train |
| Objects365 [27] | 2D 偵測標註來源（lifted 至 3D）；3D detection 驗證集 | 訓練語料合計 2.78M samples（COCO+OpenImages+Objects365）；驗證集 5,565 images / 341 classes | train + val（ablation 評測） |
| Objects365 (test split) | 3D grounding 評測 | the paper does not specify | test |
| RefCOCO / RefCOCO+ / RefCOCOg [12] | 3D grounding 評測（projected IoU、projected offset、3D IoU、3D offset） | the paper does not specify | test |
| N3D-Bench（本文提出） | 3D spatial reasoning 評測 | 2,000 questions（1,200 open-ended + 800 numerical），264 object categories | test |
| SpatialRGPT-Bench [8] | 3D spatial reasoning 評測 | 1,404 open-ended + numerical questions，88 object categories | test |
| CV-Bench-3D [30] | 3D spatial reasoning 評測（multiple-choice） | 1,200 questions | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Open-ended accuracy | 以 GPT-4o [11] 作 LLM-as-a-judge 評估開放式答案是否正確 | yes |
| Numerical accuracy | 以 string matching 抽取預測數值，並採 $\pm 25\%$ 容忍度（沿用 [8]） | yes |
| Multiple-choice accuracy | CV-Bench-3D 多選題正確率 | no |
| Projected IoU | 將預測 3D bbox 投影至影像平面後，與 ground-truth 2D bbox 的 IoU | yes |
| Projected center offset | 投影後 3D bbox 中心與 GT 2D bbox 中心的位移（越小越好） | no |
| 3D IoU | 將預測 box 對齊至 GT 深度後計算的 3D IoU（在子集上回報以降低對齊雜訊） | yes |
| 3D center offset | 對齊後的 3D 中心位移（越小越好） | no |
| F1@0.25 / P@0.25 / R@0.25 | 3D detection ablation 在 $\text{IoU}=0.25$ 閾值下的 F1、Precision、Recall | no（僅 ablation 使用） |

### 6.3 Training and Inference Settings

- Backbone：模型基於 Qwen2.5-VL [2]，提供 3B 與 7B 兩個變體（N3D-VLM-3B / N3D-VLM-7B）。
- 訓練階段：兩階段訓練。Stage 1 僅以 §3.1 產生的 3D object localization 資料訓練；Stage 2 以 3D spatial reasoning 資料與部分 localization 資料的混合進行 grounding-based reasoning 訓練。兩階段中 vision encoder 與 language model 的所有參數皆可學習。
- 深度與相機內參：訓練與推論皆使用 MoGe-2 [32] 估計 depth map 與 camera intrinsics，以保證所有預測 3D bbox 處於 metric scale 並對齊同一座標系。
- 3D 表示：每個 3D bbox 以 structured language 編碼為 `bbox(id, class, u, v, z, sx, sy, sz)`，其中 $(u, v)$ 為 3D 中心於影像平面的 2D 投影、$z$ 為深度，$(s_x, s_y, s_z)$ 為三軸尺寸；在已知相機內參下 $(u, v, z)$ 與 $(x, y, z)$ 可雙向轉換。
- 位置編碼：對下採樣後的點雲 $\hat{P} \in \mathbb{R}^{h \times w \times 3}$ 之每個座標軸 $\alpha \in \{x, y, z\}$ 套用 sinusoidal positional encoding，並把三軸編碼相加後加到影像特徵 $F_{\text{img}}$ 上得到融合特徵 $\tilde{F}_{\text{img}}$。
- 推論模式：(1) 使用者直接提出 spatial question，模型自動拆解為「3D grounding → 基於 grounding 的 spatial reasoning」；(2) 使用者明確先要求 3D grounding，再以 grounding 結果發問。兩種模式下，reasoning 皆條件於 grounding 結果。
- 訓練語料規模：總計 2.78M lifted 3D 樣本；ablation 中觀察到從 340K 擴張至 1.7M 帶來顯著增益。
- 評測協定：SpatialRGPT-Bench 上除 SpatialRGPT 自身外，所有方法均以畫在影像上的 bounding box 提供物件參照；3D grounding 為公平比較，會將預測 box 對齊至 GT 深度後計算 3D 指標，且 3D 指標僅在採樣子集上回報以降低 alignment noise。
- Hardware、batch size、optimizer、learning rate schedule、training steps、inference 解碼設定：the paper does not specify。

### 6.4 Main Results

3D Spatial Reasoning（Tab. 2，accuracy）：

| Method | N3D-Bench Open / Num | SpatialRGPT-Bench Open / Num | CV-Bench-3D MC | Notes |
|---|---|---|---|---|
| GPT-4o [11] | 63.5 / 27.8 | 76.3 / 55.8 | 72.4 | closed-source |
| Gemini-2.5-Flash [28] | 64.2 / 36.7 | 82.4 / 42.2 | 86.0 | closed-source |
| Qwen2.5-VL-7B [2] | 55.0 / 22.5 | 74.4 / 38.2 | 75.8 | base model |
| Qwen3-VL-8B [29] | 66.3 / 36.3 | 89.2 / 40.7 | 91.3 | open-source SoTA baseline |
| SpatialLadder-3B [14] | 48.9 / 18.1 | 55.9 / 26.5 | 74.9 | spatial-specialized |
| SpatialReasoner-7B [21] | 54.8 / 27.4 | 63.2 / 33.7 | 80.3 | spatial-specialized |
| SpatialRGPT-VILA-1.5-8B [8] | 63.1 / 50.4 | 92.7 / 62.7 | 63.3 | spatial-specialized |
| **N3D-VLM-3B (ours)** | **77.0 / 90.1** | **80.5 / 73.3** | **96.3** | **本文方法** |
| **N3D-VLM-7B (ours)** | **89.7 / 92.1** | **95.7 / 78.0** | **93.3** | **本文方法** |

3D Grounding，projected metrics（Tab. 3）：

| Method | RefCOCO Proj.IoU↑ / Off.↓ | RefCOCO+ Proj.IoU↑ / Off.↓ | RefCOCOg Proj.IoU↑ / Off.↓ | Objects365 Proj.IoU↑ / Off.↓ |
|---|---|---|---|---|
| Qwen3-VL-8B [29] | 0.37 / 0.16 | 0.34 / 0.26 | 0.36 / 0.14 | 0.28 / 0.12 |
| Qwen3-VL-30B-A3B [29] | 0.38 / 0.14 | 0.36 / 0.16 | 0.38 / 0.13 | 0.28 / 0.13 |
| **N3D-VLM-7B (ours)** | **0.59 / 0.06** | **0.53 / 0.10** | **0.54 / 0.08** | **0.61 / 0.05** |

3D Grounding，3D-aligned metrics（Tab. 4，RefCOCO/+/g 合併）：

| Method | 3D IoU ↑ | 3D Offset ↓ |
|---|---|---|
| Qwen3-VL-8B [29] | 0.20 | 1.88 |
| Qwen3-VL-30B-A3B [29] | 0.27 | 1.86 |
| **N3D-VLM-7B (ours)** | **0.48** | **0.36** |

主要觀察：N3D-VLM 在三個 spatial reasoning benchmark 的 open-ended、numerical、multiple-choice 三類題型上多數欄位取得最高分；對 numerical 類別的提升幅度最大（如 N3D-Bench numerical 由 base 22.5 提升至 92.1）。在 3D grounding 上，N3D-VLM-7B 不僅大幅超越同級 Qwen3-VL-8B，亦勝過更大的 Qwen3-VL-30B-A3B，顯示 native 3D grounding 設計對 localization 精度的助益。

### 6.5 Ablation Studies

模型設計（Tab. 5，Objects365 驗證集 5,565 images / 341 classes，$\text{IoU}=0.25$）：

| Variant | F1 ↑ | P ↑ | R ↑ | 變更 |
|---|---|---|---|---|
| (0) SpatialLM [22]-340K | 2.2 | 2.3 | 2.4 | point cloud encoder + LLM 架構 |
| (1) 3B-340K-nodepth | 9.4 | 10.9 | 9.4 | 移除 depth 輸入 |
| (2) 3B-340K-cameraxy | 10.8 | 11.6 | 10.7 | 直接於 camera $(x,y,z)$ 空間預測中心 |
| (3) 3B-340K-imageuv | 12.8 | 13.6 | 12.9 | full design：depth + 預測 $(u,v,z)$ |
| (4) 3B-1.7M-imageuv | 22.9 | 24.3 | 22.9 | 同 (3)，訓練資料擴張至 1.7M |

- (1) vs (3)：加入 depth 輸入使 F1 從 9.4 提升至 12.8，回答了「depth-aware visual encoding 是否有用」的核心設計問題。
- (2) vs (3)：在 image-space $(u, v)$ 空間預測比直接在 camera-space $(x, y)$ 預測更佳（10.8 → 12.8），作者解釋是因為 base model 的 2D 預訓練先驗與 image-space 表徵自然對齊。此屬診斷型 ablation。
- (3) vs (4)：訓練樣本由 340K 擴大至 1.7M 帶來大幅增益（F1 12.8 → 22.9），驗證 data construction pipeline 規模化的價值；但這同時混淆「pipeline 品質」與「樣本數」兩個變因——若希望嚴格量化資料 quality 的貢獻，應再加上「相同樣本數但取自既有 3D dataset」的對照組。
- (0) vs (1)–(4)：與 SpatialLM 之比較主要凸顯 indoor-only 點雲 encoder 在多樣化資料上的泛化不足，較接近 sanity check 而非對 N3D-VLM 各組件的細部診斷。

3D grounding → spatial reasoning 解耦（Tab. 6，N3D-Bench）：

| Method | N3D-open ↑ | N3D-num ↑ | 解讀 |
|---|---|---|---|
| Qwen3-VL-8B（直接作答） | 66.3 | 36.3 | baseline |
| Qwen3-VL-8B（給定本模型 grounding 結果） | 71.3 | 54.6 | 提供 grounding 即提升 +7.5% / +50.4%，顯示 grounding 對 reasoning 的因果貢獻 |
| QAonly-7B（同架構，端到端 QA，不解耦） | 80.6 | 62.4 | 同架構但不顯式分階段訓練 |
| **N3D-VLM-7B（full）** | **89.7** | **92.1** | 解耦 grounding + reasoning 的完整方法 |

此 ablation 屬診斷型：第一個對照（將 grounding 結果灌入第三方 model）特別好地隔離了「grounding 品質」對 reasoning 的影響；第二個對照（QAonly-7B）則直接質詢「顯式 grounding-then-reasoning」的必要性。可惜的是，paper 未提供 N3D-VLM 用 GT 3D bbox 作答的 oracle upper bound，難以判斷剩餘 gap 屬於 grounding error 還是 reasoning error。

詳細題型拆分（Tab. 7、Tab. 8）顯示 N3D-VLM 在數值化題型（distance、ver./hor. dis.、width/height）的提升尤其顯著，但在 N3D-Bench 的 `wide/thin`（3B 為 45.5）等部分題型上遜於 7B 變體，提示對小尺寸物件的尺寸比較仍受 grounding 精度限制。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 同時對比 closed-source SoTA（GPT-4o、Gemini-2.5-Flash）與 open-source SoTA / 任務專家（Qwen3-VL-8B/30B-A3B、SpatialRGPT、SpatialReasoner、SpatialLadder、SpatialLM），baseline 覆蓋面充足（Tab. 2、Tab. 3、Tab. 4）。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時評測 spatial reasoning（N3D-Bench、SpatialRGPT-Bench、CV-Bench-3D）與 3D grounding（RefCOCO/+/g、Objects365），跨任務跨資料集均有比較。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — depth 輸入、image-uv vs camera-xy、grounding-then-reasoning 解耦皆為診斷型 ablation；但缺少對 sinusoidal positional encoding、兩階段訓練順序、以及 grounding 給定 GT 時的 oracle upper bound 等更細的分解。
- [partial] Has a scaling study (size, length, or compute) — 提供 model size（3B vs 7B）與 data size（340K vs 1.7M）兩條 scaling 軸；但僅各兩點，無法擬合 scaling trend，且未有 compute / FLOPs 軸。
- [missing] Has an efficiency / wall-clock comparison — 全文未報告推論延遲、tokens/s 或 GPU memory 比較；對需要先 grounding 再 reasoning 的兩步推論，這項缺漏較為可惜。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有主表與 ablation 皆為單一數字，未報告多 seed 變異或信賴區間。
- [partial] Releases code / weights / data sufficient for reproducibility — 作者於 §1 結尾承諾 “release code, checkpoints, and datasets upon acceptance”，但截至論文提交時尚未提供，目前僅能透過 project page 取得有限資訊。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: Unified RGB-D model with native 3D detection/grounding enabling spatial reasoning** (§1, p.3). *Supported.* Tables 2–4 show consistent gains over Qwen2.5-VL, Qwen3-VL, SpatialRGPT, and SpatialLM across both spatial reasoning and 3D grounding metrics.
- **C2: Scalable data pipeline that lifts 2D annotations into 3D** (§1, p.3). *Supported on scale, partial on quality.* The 2.78M corpus and the $340$K $\to$ $1.7$M ablation in Table 5 ($F_1@0.25$: $12.8 \to 22.9$) directly defend the scale claim. Quality is defended only indirectly: there is no ablation against a true 3D-annotated subset, so the pseudo-label ceiling is undocumented.
- **C3: Benchmark with explicit reasoning, multi-object, view-change** (§1, p.3; Table 1, p.6). *Supported as artifact, partial as evaluation.* N3D-Bench exists and is broader than SpatialRGPT-Bench, but the same team built it using the same lifting pipeline as training — the cross-bench number on SpatialRGPT-Bench numerical ($78.0$) is the more independent evidence and is itself substantial.
- **Implicit claim: state-of-the-art across three benchmarks.** *Supported with a caveat.* Table 2 is consistently best on all three, but the largest margin is on N3D-Bench (self-built); on SpatialRGPT-Bench numerical the lead over SpatialRGPT is $78.0$ vs $62.7$ (15.3 points), much smaller than the $92.1$ vs $50.4$ gap on N3D-Bench numerical.
- **Implicit claim: grounding-first decomposition is necessary, not just helpful.** *Supported.* Both Table 6 ablations point the same way: feeding grounding to Qwen3-VL helps it ($36.3 \to 54.6$), and removing the decomposition from N3D-VLM hurts it ($92.1 \to 62.4$).

### 7.2 Fundamental Limitations of the Method

**Depth-model coupling.** The entire system is anchored to MoGE-2's coordinate frame: 3D pseudo-labels at training time, the depth tensor concatenated at inference, and the alignment oracle used to compute 3D IoU all come from the same predictor. The reported metric-scale accuracy is therefore upper-bounded by MoGE-2's accuracy and cannot be evaluated independently of it. Failure modes that MoGE-2 itself cannot handle (mirrors, glass, very-far-field, low-texture sky) propagate verbatim into N3D-VLM and would be invisible to the current evaluation because the labels share the failure.

**Template-bound reasoning.** The CoT traces are produced by deterministic geometric formulas (vector subtraction, $\mathrm{atan2}$, clock-position rounding) and then LLM-rephrased for naturalness (§3.1, p.5). The model learns to emit the formula trajectory, not to choose which formula applies; there is no mechanism for composing new geometric operations or for recognizing that a question lies outside the template family. The $92.1\%$ numerical accuracy on N3D-Bench is therefore partly an in-distribution score on the same template family the model was trained to imitate.

**Pseudo-label extent ceiling.** The 3D extents $s_x, s_y, s_z$ are derived from the back-projected visible point cloud of the 2D mask (§3.1, p.3–4). This systematically underestimates the occluded sides of every object, especially in cluttered scenes. The trained model therefore inherits a "thin-side" bias that no current evaluation surfaces because RefCOCO/Objects365 have no 3D ground truth either, and SpatialRGPT-Bench numerical questions are mostly distance-based, which is dominated by center error, not extent error.

**Self-evaluation entanglement.** N3D-Bench is generated by the same authors using the same lifting pipeline as training, so the $90+\%$ numbers measure agreement between the model and its own data-generation prior, not agreement with an independent ground truth. The same observation applies to the 3D IoU column in Table 4: predictions are aligned to GT depth before scoring, which structurally deletes the dimension where MoGE-2 dependency would hurt most.

### 7.3 Citations Worth Tracking

- **[32] Wang et al., MoGE-2** — the monocular depth/intrinsics estimator that anchors the metric frame at training, inference, and evaluation. Reading its error analysis is a precondition for interpreting N3D-VLM's numbers.
- **[22] SpatialLM** — closest 3D-grounding-from-VLM baseline; its indoor-only failure on outdoor scenes (Fig. 6, p.13) is the empirical case that motivates N3D-VLM's broader 2D-lifting strategy.
- **[8] SpatialRGPT (and SpatialRGPT-Bench)** — defines the bench protocol, the $\pm 25\%$ tolerance, and the question-type taxonomy that N3D-Bench extends; the strongest non-N3D numerical baseline in Table 2.
- **[21] SpatialReasoner** — the closest prior "explicit 3D reasoning" attempt without full bounding boxes; the contrast clarifies what *box-level* explicit 3D buys over center-only or orientation-only outputs.
- **[37] DetAny3D** — the strongest prior single-image 3D detection dataset ($\sim$450K) and the reference point for the $6\times$ scale claim; reading it sets a calibration for what "lifted 3D data" should look like.

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] How much of the gain survives if MoGE-2 is replaced by Depth Anything v2 [36] or Metric3D at inference, with training kept the same?
- [ ] What is the unaligned 3D IoU (no depth alignment) on RefCOCO and Objects365, and what fraction of error is metric-scale versus localization?
- [ ] What absolute median error in meters does the model achieve on SpatialRGPT-Bench distance/height questions, beyond the $\pm 25\%$ pass rate?
- [ ] How does CoT accuracy degrade on question templates held out from training (e.g., volume comparison, occluded-object reasoning, multi-step geometric chains)?
- [ ] How robust is the model on real RGB-D sensor inputs (Kinect, ARKit LiDAR) versus MoGE-2 estimates, where the depth distribution differs structurally?
- [ ] On the dense-scene failure mode (jellyfish), what is the recall as a function of object count, and does extra training data fix recall or just per-object precision?
- [ ] Does the N3D-VLM-3B advantage over N3D-VLM-7B on CV-Bench-3D ($96.3$ vs $93.3$, Table 2) reflect noise or capacity-saturation on a 1.2K-question multichoice bench?

### 8.2 Improvement Directions

1. **Report unaligned 3D metrics alongside aligned ones** (highest feasibility). Add a column in Tables 3–4 with raw 3D IoU and per-axis $(x, y, z)$ error so readers can separate metric-scale error from localization error. Justification: aligning predictions to GT depth structurally removes the dimension where MoGE-2 coupling would manifest, so the current numbers cannot answer the depth-coupling question.
2. **Cross-depth-backbone ablation** (high feasibility). Train a second model with Depth Anything v2 and evaluate both models with both depth backbones at inference. Justification: if accuracy collapses when the train-time and inference-time depth disagree, the model is fitting MoGE-2 specifically rather than 3D structure; the current paper cannot rule this out.
3. **Independent held-out test slice** (medium feasibility). Have human annotators draw 3D boxes on a few hundred Objects365 images that the lifting pipeline could not see, and report results separately. Justification: this is the only way to bound the pseudo-label ceiling without circular evaluation.
4. **Held-out template generalization** (medium feasibility). Train on a subset of CoT templates (e.g., distance, clock direction) and evaluate on a strictly held-out template family (e.g., volume, occluded-object reasoning). Justification: the current $92.1\%$ N3D-Bench number is consistent with both "the model learned geometry" and "the model learned templates"; this experiment separates them.
5. **Program-of-thought head instead of templated CoT** (lower feasibility). Replace the LLM-rephrased deterministic trace with a small DSL emitted by the model and evaluated by an external calculator, so that geometric correctness is decoupled from language fluency and the LLM-as-a-judge pass rate stops conflating the two. Justification: this directly attacks the template-bound limitation in §7.2 and would let CoT generalize compositionally, at the cost of an additional decoding head.
