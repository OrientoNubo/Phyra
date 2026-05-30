<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# PhysInOne — PhysInOne: Visual Physics Learning and Reasoning in One Suite

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | PhysInOne |
| Paper full title | PhysInOne: Visual Physics Learning and Reasoning in One Suite |
| arXiv ID | 2604.09415 |
| Release date | 2026-04-10 |
| Conference/Journal | CVPR 2026 |
| Paper link (abs) | https://arxiv.org/abs/2604.09415 |
| PDF link | https://arxiv.org/pdf/2604.09415v1 |
| Code link | — |
| Project page | https://vlar-group.github.io/PhysInOne.html |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Siyuan Zhou | vLAR Group, The Hong Kong Polytechnic University | https://vlar-group.github.io/people.html | co-first author |
| Hejun Wang | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Hu Cheng | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Jinxi Li | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Dongsheng Wang | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Junwei Jiang | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Yixiao Jin | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Jiayue Huang | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Shiwei Mao | vLAR Group, The Hong Kong Polytechnic University | — | co-first author |
| Shangjia Liu | The Hong Kong Polytechnic University | — | co-author |
| Yafei Yang | vLAR Group, The Hong Kong Polytechnic University | — | co-author |
| Hongkang Song | vLAR Group, The Hong Kong Polytechnic University | — | co-author |
| Shenxing Wei | vLAR Group, The Hong Kong Polytechnic University | — | co-author |
| Zihui Zhang | vLAR Group, The Hong Kong Polytechnic University | — | co-author |
| Bing Wang | The Hong Kong Polytechnic University | — | co-author |
| Zhihua Wang | Syai Singapore | — | co-author |
| Chuhang Zou | Meta | https://zouchuhang.github.io/ | corresponding author |
| Bo Yang | vLAR Group, The Hong Kong Polytechnic University | https://yang7879.github.io/ | corresponding author |

### 1.2 Keywords

synthetic dataset, visual physics learning, world models, video generation, future frame prediction, physical property estimation, motion transfer, 3D/4D vision

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Physion (Bear et al., NeurIPS'21) | predecessor | Earlier physics-from-video benchmark with 8 phenomena and ~24K videos; PhysInOne scales orders of magnitude beyond it. |
| CLEVRER (Yi et al., ICLR'20) | predecessor | Synthetic collision QA dataset; representative simple-shape physics benchmark that PhysInOne supersedes in scale and complexity. |
| PAC-NeRF (Li et al., NeurIPS'23) | baseline | System-identification baseline; benchmarked on PhysInOne for physical property estimation (Young's modulus, viscosity, etc.). |
| SVD (Blattmann et al., 2023) | base model | UNet-based image-to-video model fine-tuned on PhysInOne to validate physics-aware video generation. |
| CogVideoX (Yang et al., 2024) | base model | Transformer-based TI2V model fine-tuned with LoRA/SFT/FLT on PhysInOne subsets. |
| Wan2.2 (Wan team, 2025) | base model | Latest Transformer + flow matching TI2V model used as a fine-tuning target on PhysInOne. |
| Physics-IQ (Motamed et al., arXiv'25) | concurrent | Physical-understanding benchmark with 66 scenes; PhysInOne offers far larger-scale training data plus benchmarking. |

## 2. Research Overview

### 2.1 Research Topic

本論文發表 PhysInOne：一個面向視覺物理學習與推理的大規模合成資料集，涵蓋力學、光學、流體力學與磁學四大日常物理領域，系統化整理 71 種基本物理現象並組合為 3,284 種 multiphysics 活動。作者使用 2,231 個 3D 物件、623 種材質與 528 個 3D 背景，建構出 153,810 個動態 3D 場景；每個場景以 12 個固定相機加 1 個移動單目相機渲染，產生 200 萬支具備 3D 幾何、語意分割、運動軌跡、物理屬性與文字描述等完整 ground-truth 標註的影片。透過 Chaos Physics、MPM 與 SPH 等多種模擬引擎，論文確保動力學遵循 Newton 定律、動量守恆、Hooke 定律等基本物理規律，並在 physics-aware video generation、long-/short-term future frame prediction、physical property estimation 與 motion transfer 四項應用上提供基準，為物理基礎的世界模型研究奠定資料基石。

### 2.2 Domain Tags

- computer vision
- video generation
- world models
- 3D/4D scene understanding
- physics simulation
- embodied AI

### 2.3 Core Architectures Used

- **Chaos Physics (UE5)**：論文採用 Unreal Engine 5 內建的 Chaos Physics 作為主要模擬引擎，負責 153,810 個動態 3D 場景中絕大多數剛體、碰撞、重力等日常物理現象的動力學計算。
- **MPM (Material Point Method, via Taichi)**：用於模擬可形變物件 (deformable) 與顆粒物質 (granular materials, e.g. sand, plasticine) 的非線性連續體動力學，由 Taichi 框架實作。
- **SPH (Smoothed Particle Hydrodynamics, via Doriflow)**：透過 Doriflow 套件對水、奶油、牛奶等液體進行流體模擬，支撐 fluid dynamics 子集的 ground-truth 生成。
- **SVD-XT**：作為 UNet-based image-to-video 基礎模型，於 PhysInOne 上以 LoRA / SFT / FLT 三種微調方式驗證 physics-aware video generation。
- **CogVideoX-1.5-5B**：Transformer-based text-image-to-video (TI2V) 模型，以 LoRA 在 83,650 對 text-video 子集上微調並由 PMF 指標評估物理可信度提升。
- **Wan2.2-5B**：最新的 Transformer + flow matching TI2V 模型，作為 PhysInOne 微調與 PMF 評測的代表性 SOTA baseline。
- **TiNeuVox / DefGS / FreeGave / TRACE**：四種 4D 場景建模方法 (deformation field 或 velocity field) 用於 long-/short-term future frame prediction 任務的 multiview 評測。
- **ExtDM / MAGI-1**：兩種 video prediction 模型 (ExtDM 從頭訓練於 PhysInOne 子集；MAGI-1 直接使用預訓練權重) 作為單目視角下的未來幀預測 baseline。
- **PAC-NeRF / GIC**：兩個 system identification baseline，用於 physical property estimation 任務上估計 Young's modulus、Poisson's ratio、viscosity、yield stress 等參數。
- **MotionPro / GoWithTheFlow**：兩個 optical-flow based motion transfer 方法，於 PhysInOne 273 個場景子集上評測複雜物理運動的轉移能力。
- **Physical Motion Fidelity (PMF)**：論文新提出的量化指標，以 DFT 將 $V_{\text{ref}}$ 與 $V_{\text{gen}}$ 轉換到頻域並比較能量 (squared amplitude)，定義為 $\text{PMF} = f_{\text{energy}}(\text{DFT}(V_{\text{gen}}), \text{DFT}(V_{\text{ref}}))$，用以衡量生成影片與參考影片之間動力學軌跡的差異。

### 2.4 Core Argument

作者主張現有 LLM/LVM/MLLM 與生成模型即便具備視覺逼真度，仍頻繁違反基本物理定律（如物體向上掉落、速度突變），其根本原因不在於模型架構，而在於缺乏「足夠大規模、足夠多樣、且具備密集物理標註」的訓練資料。過往視覺物理資料集普遍存在三類侷限：（1）規模僅數十至數千樣本，遠不足以驅動基礎模型學會物理常識；（2）只涵蓋單一或極少數現象（如僅 stacking、僅 collision、僅 fluid），無法支撐世界模擬器所需的 multiphysics 同時/序列發生；（3）幾乎全為單一同質背景下的簡化幾何（cube、ball），與真實世界的多物互動、複雜背景、異質材質脫節。作者由此推導：要讓模型真正學會物理，資料必須同時在「現象廣度（71 種基本現象）、活動複雜度（single/double/triple-physics）、場景多樣性（multiobject + complex background + 多材質）、標註豐富度（geometry/semantics/motion/properties/text）與絕對規模（百萬級影片）」五個維度同時放大。PhysInOne 正是針對此論斷的逐項回應——以四大物理領域 71 現象為骨架，透過 Chaos Physics/MPM/SPH 多套模擬器確保 ground-truth 動力學嚴格遵循 Newton 定律、動量守恆、Hooke 定律等基本法則，並以 12+1 多視角相機產生密集監督訊號。實驗證明，僅以子集對 SVD、CogVideoX、Wan2.2 微調，便可顯著提升新提出的 Physical Motion Fidelity (PMF) 指標與人類評分；同時在 future frame prediction、property estimation、motion transfer 上揭露現有方法在新視角與複雜物理動態下的明顯缺口。因此資料集的存在不只是工程量級的擴展，而是物理基礎世界模型研究在邏輯上不可或缺的前置條件。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(190 words)

標題 PhysInOne: Visual Physics Learning and Reasoning in One Suite 中的 "in One Suite" 一語暗示作者要把多種 visual physics 任務所需的訓練與評估資料整合進「同一個」資料集，而不是再做一份只能服務單一現象或單一任務的小型 benchmark。Abstract 開門見山地把 PhysInOne 定位為對抗 "physically-grounded training data scarcity" 的大型 synthetic dataset，並用三個量化指標立刻把它和先前工作區分開：2 million videos、153,810 dynamic 3D scenes、71 basic physical phenomena，覆蓋 mechanics、optics、fluid dynamics、magnetism 四大日常物理領域。Abstract 接著強調與既有資料集的兩個質性差異，一是 scenes feature multiobject interactions against complex backgrounds，二是 ground-truth annotations 同時涵蓋 3D geometry、semantics、dynamic motion、physical properties、text descriptions 五類，為後文「能同時支援 generation、prediction、estimation、transfer 多種任務」鋪好邏輯前提。最後 abstract 主動承認 fine-tuning 雖能 significantly enhance physical plausibility，但同時 expose critical gaps in modeling complex physical dynamics and estimating intrinsic properties；這個 "one-handed boast, one-handed honesty" 的收尾把全文定調為「我們提供新尺度的資料、並用實驗顯示這個尺度依然不夠把問題解決」，自然地把讀者導向 §1 對 data scale 與 physical reasoning 之間關係的論證。

### 3.2 Introduction

(900 words)

Introduction 採用「以資料規模史推論物理理解現況」的論證結構。第一段先列 Common Crawl、ImageNet、MS-COCO、LAION-5B、Objaverse-XL、Panda-70M，把「大規模、高品質資料是現代 ML 突破的催化劑」當作公理。第二段隨即指出儘管 LLM/LVM/MLLM/GenAI 在這些資料上取得進展，他們對 physical world 的理解仍然有限：AI 生成的影片頻繁違反基本物理定律（objects falling upward、suddenly shifting velocity），並引用近兩年 visual physics 學習工作說明這些方法 "typically trained on only dozens, hundreds, or thousands of data points"，把資料規模與物理理解能力直接掛鉤。第三段開始正面介紹 PhysInOne：作者依據大學物理教科書 Fundamentals of Physics 與近期 benchmark 工作 [62, 63] 鎖定 mechanics/optics/fluid dynamics/magnetism 四大可視化的日常物理領域，刻意排除 thermodynamics 與 acoustics，並從中萃取 71 個 key phenomena。每個 scene 同時或依序體現多個 phenomena，且嚴格遵循 Newton's Laws、Mass Conservation、(Angular) Momentum Conservation、Hooke's Law 等定律。每個 scene 配 13 段影片（12 fixed cameras + 1 smoothly moving monocular camera）並由人工撰寫一段品質標註的文字描述，搭配 3D mesh、moving trajectories、2D masks、materials、depths、camera poses 等 ground truth，主張這個量級 "orders of magnitude larger than all existing visual physics datasets"。第四到七段預告四個 emerging applications，這也是後續 §4 的骨架：(1) Physics-aware Video Generation，藉由 fine-tune SVD、CogVideoX、WAN，並用作者新提出的 PMF 量化 physical motion fidelity；(2) (Long-/Short-term) Future Frame Prediction，引用 Feynman 名言把「能不能預測下一幀」當成物理理解的試金石，並列出 TiNeuVox、DefGS、FreeGave、TRACE、ExtDM、MAGI-1 六個比較對象；(3) Physical Properties Estimation，benchmark PAC-NeRF 與 GIC，估計 Young's modulus、Poisson's ratio、viscosity 等參數；(4) Motion Transfer，評估 MotionPro 與 GoWithTheFlow，並坦承「結果仍然 largely unsatisfactory」。Introduction 的修辭策略很值得注意：每介紹一個應用，作者都同時給出一個 positive finding（fine-tune 後 PMF 進步、預測在 trained viewpoint 可用）和一個 negative finding（novel viewpoint 退化、複雜物體無法準確 inverse、physical motion 難以遷移），把 dataset 同時包裝為「能催化進步的訓練資源」與「能暴露現有方法極限的嚴格 benchmark」。最後一段以 "these findings represent just a fraction of its potential" 作收，把 §3 與 §4 設定為「示範性」而非「窮盡」，留下 community 接續使用的空間，自然將讀者帶往 §2 的 related work 比較。

### 3.3 Related Work / Preliminaries

(380 words)

Section 2 把與 PhysInOne 在資料層面相關的工作切成三條軸線，目的是要在 §3 開始介紹自家資料集之前，把「為什麼需要再造一個」的論述補完。第一條軸線是 Datasets for Learning Physical Dynamics：作者點名 ShapeStacks 與 StableText2Brick 只關心 stability、VOE/IntPhys2019/PHYRE/ADEPT/CLEVRER/ESPRIT/Physion/CoPhy/CRAFT/SPACE+ 多半只 examine 單物體軌跡是否符合 intuitive physics，而非嚴格驗證對 strict physical laws 的遵守，並補刀說這些資料集裡的物體幾乎全是 oversimplified shapes（cubes、balls）配 homogeneous colors 與 clean backgrounds；至於 fluid 專門資料集（ScalarFlow、TomoFluid、FLAME、Obstacles、Richter et al.、NeuroFluid）也只覆蓋煙或液體單一面向。第二條軸線是 Datasets for Learning Physical Properties：列舉 Physics101、Physion++、Materialistic、PAC-NeRF、PhysTwin、PhysXNet、SOPHY、PixieVerse、PhysVid、VoMP，批評它們 "usually focus on isolated individual objects or oversimplified 3D scenes"。第三條軸線是 Datasets for Testing Physical Understanding：列出 ComPhy、PerceptionTest、TraySim、GRASP、PhyBench、Physics-IQ、Morpheus、WorldModelBench、WISA、VBench-2.0、PhysBench、DynSuperCLEVR、VideoPhy、VideoPhy-2、PhyX、IntPhys2、PhyGenBench、UGPhysics、STI-Bench、PhyWorldBench、PisaBench、NewtonGen、NewtonBench-60K，並指出這些 benchmark 多半圍繞 text-image-video QA 或 narrow scenarios，缺乏 "the precise and diverse visual data and annotations needed to train or fine-tune large, general models"。三條軸線分別對應 §1 預告的訓練資料、屬性估計、評估三個用途，每一軸都得出同一個結論：existing datasets 在 phenomena 數、scene 數、object/background 複雜度與 annotation 完整度其中至少一項上有顯著缺口。最後 §2 把 Table 1 當成證據總結：PhysInOne 在 # Physical Phenomena (71)、# Physical Scenes (153,810)、# Dynamic Videos (2 million)、Multiobject Interactions、Multiphysics Activities、Complex Objects、Complex Backgrounds、相機數 (12 fixed + 1 monocular)、annotation 五項齊全等所有欄位都同時為「最大」或「唯一打勾」。這張表格把 §3 的章節合理化為「不是要再做一個 incremental dataset，而是要把過去碎片化的資料層面一次補齊」，並為 §3 接下來說明 dataset 構造管線提供承接。

### 3.4 Method (overview narrative)

(1200 words)

Section 3 的整體敘事是把資料集的構造拆成 phenomena 定義 → asset 採集 → scene 組合 → 動力學模擬 → 相機與影片渲染 → 標註與切分 六步管線（Figure 2）。§3.1 先把 §1、§2 已經提到的「71 basic physical phenomena」具體化：每個 phenomenon 是一個概念性的日常物理事件，受 Newton's Laws、Conservation of Momentum、Hooke's Law、Bernoulli's Principle 等一條或多條 fundamental law 支配，完整列表延後到附錄 5.1。重要的鋪陳是作者強調 "each basic physical phenomenon represents a conceptual occurrence in daily life, not a specific, concrete 3D scene"，這把 phenomenon 與 scene 兩個概念分層，為 §3.3 的 single/double/triple-physics 組合留下乘法擴張空間。§3.2 接著介紹 3D asset 採集策略：2,231 個來自 Sketchfab、FAB、BlenderKit 的 common objects（約 163 categories），按 physical 行為再細分為 solid、interactable（以 Blueprints 實作於 UE）、destructible（以 Geometry Collections 實作）、deformable（用 MPM 模擬）、granular（同樣用 MPM）、liquid（用 SPH）六類，再加上 623 個跨 plastic/metal/wood/stone/fabric 五大類別並可調整 friction、density、restitution 的 materials，以及 528 個涵蓋室內外、不同空間尺度的 backgrounds，所有資產都明確標示為學術與商業可用。§3.3 是把 §3.1 與 §3.2 連起來的關鍵：作者在 Step 1 把 phenomena 拆成 single-physics（71）、double-physics（C(71,2) 篩選後 943）、triple-physics（篩選後 2,270）三個 activity 等級，總共 3,284 個 conceptual activities；Step 2 為每個 activity 設計合理的背景；Step 3 把多個 asset 放進背景；Step 4 變更 material 與物理參數產生 scene 變體。最後 153,810 個 unique multiphysics multiobject scenes 平均對應每個 activity 46.84 個 scenes，且 single/double/triple 平均物件數為 3.9/6.3/7.8，作者用這個遞增證明場景複雜度確實隨 activity 級別遞增。§3.4 切到 simulation backend：UE5 的 Chaos Physics 處理多數 daily 場景、Taichi 的 MPM 處理 deformable 與 granular、Doriflow 的 SPH 處理 liquid；作者主動承認 simulator 不可能 perfect，但引用 [32, 60, 100] 主張 errors 已被 thoroughly studied 且足以推進研究。§3.5 處理「拍攝」：每個 scene 在上半球 elevation 30°-60° 均勻擺 12 個 static cameras 並依背景空間做 per-scene 微調，再加一個沿著預設軌跡圍繞 activity 的 monocular moving camera，輸出 1120×1120 解析度、30 FPS（laser activity 的 8,780 個場景用 60 FPS）平均 5.2 秒長的影片，總計 2 million dynamic videos。§3.6 收尾於標註：每個 scene 配一段平均 64 字、由人工撰寫並用 Qwen3 校對文法的英文段落，渲染同時輸出 depth、per-frame masks、3D trajectories、object meshes、material properties，覆蓋 geometry、semantics、motion、physical properties、textual descriptions 五個面向；最後採 8:1:1 切分 train/val/held-out test，並 enforce 所有 3D asset 只出現在單一 partition 以避免 data leakage，並補上 standardized development 與 independent validation 的品質流程。整節敘事的功能是把 §1、§2 點過的「scale、diversity、annotation」三個賣點轉成可重現的工程程序，並透過 phenomena/activity/scene 的層級遞推、與 single/double/triple physics 的組合爆炸，邏輯地論證為何能達到 153,810 scenes 與 2M videos 的量級，順勢為 §4 的四個下游任務提供足夠且分布合理的訓練/測試資料。

### 3.5 Experiments (overview narrative)

(1700 words)

Section 4 把 §1 預告的四個 emerging applications 一一展開，並維持「先驗證 PhysInOne 訓練有效、再揭露現有方法仍不足」的雙軌結論。§4.1 Physics-aware Video Generation 選了三個代表性架構作 fine-tune：UNet-based I2V SVD-XT、Transformer-based TI2V CogVideoX-1.5-5B、最新 Transformer + flow matching 的 Wan2.2-5B；每個模型都試 LoRA、SFT、FLT 三種微調策略。為了量化「物理運動正確性」，作者主張 FVD 等傳統指標只測視覺真實感、video VLM 缺乏物理理解、QA-based benchmark 又僅能定性評估，因此提出新指標 Physical Motion Fidelity (PMF)：對 reference video Vref 與在相同 initial frame 與 prompt 下生成的 Vgen，分別取 DFT，比較 squared amplitude 的 energy 差異，並聲明 frame-perfect alignment "is neither achievable nor desirable in generative tasks"。實驗從 PhysInOne 抽 83,650 text-video pairs 訓練、772 pairs 測試（test-small），結果（Table 2）顯示 SVDsft、Wan2.2sft 在 PMF 上明顯超過原 baseline，且 user study 評分與 PMF 高度相關，作為對新指標的人類驗證；右半部依四大物理領域分項，magnetism 與 fluid 普遍較高，mechanics 與 optics 較低，作者解讀為 future research 應對的難點。§4.2 切成 long-term 與 short-term 兩個 future frame prediction 子任務以對齊 video understanding 與 robot manipulation 兩種應用情境。§4.2.1 long-term 任務在 test-mini（103 scenes）上要求模型用前半段預測後半段（約 2.6 秒、78 幀），對比 4D modeling 路線（TiNeuVox、DefGS、FreeGave、TRACE）與 video prediction 路線（從零訓練的 ExtDM、預訓練的 MAGI-1），同時報告 PSNR/SSIM/LPIPS 與 PMF；Table 3 顯示在 trained viewpoint 各方法尚可，但 4D 方法在 novel viewpoint 全面退化，作者把這視為「3D 空間中的 complex physical motion 仍是公開難題」的證據。§4.2.2 short-term 任務模擬機器人控制需求，要求連續預測下一個 10 幀；只評估 DefGS、FreeGave、ExtDM、MAGI-1 四個方法，結論方向與 long-term 一致：seen view 表現可用、novel view 仍是瓶頸。§4.3 Physical Properties Estimation 在 test-tiny（20 scenes，每類 4 個）上評 PAC-NeRF 與 GIC 對 Elastic Solids（log10(E)、ν）、Plasticine（再加 log10(τY)）、Newtonian Fluids（log10(µ)、log10(κ)）、Non-Newtonian Fluids（再加 log10(τY)、log10(η)）、Granular Substances（θfric）五大類材料的反演精度，並額外估計 initial velocity v；除了 Table 5 直接比對估計誤差，作者還做 resimulation：用估計參數在 modified 初始條件下重渲染，再與 ground-truth physics 渲出來的 reference video 比 PSNR/SSIM/LPIPS/PMF（Table 6）。結論是兩個方法都 infer 出 plausible 屬性，但在 PhysInOne 的 complex object 與 intricate background 場景下精度顯著不足，圖 5 直接展示這些失敗的 resimulation 視覺結果。§4.4 Motion Transfer 用 PhysInOne val set 中 273 個 dynamic scenes 當 source，把 source object 替換成不同 shape 與 material 但保持相同 physics activity 來生成 target；評估 MotionPro 與 GoWithTheFlow 在 PSNR/SSIM/LPIPS 與 PMF 上的表現（Table 7），結論是兩者皆能維持高 visual fidelity，但無法準確遷移 multiphysics interactions（圖 6 顯示 ball 沒有正確下落、car 沒有正確被撞）。整個 §4 的整體敘事策略是把 PhysInOne 同時鋪成「微調資源」「benchmark testbed」「新指標 (PMF) 的試金石」三角；四個應用都遵循「fine-tune 進步 → seen 場景可用 → novel/複雜場景退化」的同構結論，把整篇文章的下半部寫成對未來研究方向的廣告，與 §5 的限制段落自然銜接。

### 3.6 Conclusion / Limitations / Future Work

(80 words)

Section 5 Conclusion 極為精簡，等同把全文五大要素濃縮為兩句：第一句重申 contribution，PhysInOne 是覆蓋 71 phenomena、153,810 dynamic 3D scenes、2 million videos 的 comprehensive dataset；第二句平衡 §4 的雙軌結論，承認 fine-tuning 在四個任務都顯著提升 physical plausibility，但 existing methods 仍然 struggle to accurately learn complex multiobject dynamics and physical properties，並把這個事實重新包裝為 "validating the dataset's value as a rigorous testbed"，把 dataset 同時當成資源與標尺。值得注意的是，正文沒有顯式的 Limitations 與 Future Work 小節，敘事上把 §4 各應用尾段隨手點出的弱點（novel-view 退化、complex-scene 反演不準、motion-transfer 失真）暗示為 future work 的方向；而 simulator fidelity 的不確定性則由 §3.4 段落中對 [32, 60] 的引用以及「errors are thoroughly studied and controlled」這個自我緩解陳述代為承擔。換言之，作者選擇不另立明確的 limitations 段落，而是把「資料集很大但仍不完美、模型微調有效但仍不夠」這個 honest framing 透過 abstract → introduction → applications → conclusion 反覆出現的「improve / yet expose gaps」修辭，讓讀者把限制與未來工作自行補完。這個結尾的功能是把整篇論文鎖定為一個 "infrastructure paper"：作者主張自己提供的是 community 可繼續挖掘的工具，而不是要把所有 visual physics 問題就此解決。

## 4. Critical Profile

### 4.1 Highlights

- 規模上將 visual physics dataset 推進到 2 million videos / 153,810 scenes，相較 Physion 的 24K 與 CLEVRER 的 10K 提升一至兩個數量級（Table 1, p.3）。
- 系統化定義 71 個 basic physical phenomena 並組合為 71 + 943 + 2270 = 3284 個 single/double/triple-physics 活動，是目前唯一明確標註多現象同時／序列發生的 dataset（§3.3, p.4–5）。
- 同時整合 Chaos Physics（UE5）、MPM（Taichi）、SPH（Doriflow）三套引擎，分別處理 rigid body、deformable/granular、liquid，避免單一 simulator 的物理覆蓋盲點（§3.4, p.5）。
- 每個場景以 12 個 fixed cameras 加 1 個 moving monocular camera、1120×1120 解析度、30 FPS（雷射場景 60 FPS）渲染，提供 seen 與 novel view 雙重評估能力（§3.5, p.5）。
- annotation 涵蓋 geometry、semantics、motion、physical properties、text 五個面向，平均每場景 64 詞的人工 text 並以 Qwen3 校對（§3.6, p.5）。
- 提出 Physical Motion Fidelity (PMF) 指標，透過 $\mathrm{DFT}(V_{gen})$ 與 $\mathrm{DFT}(V_{ref})$ 的能量比較量化 kinematic 偏差，避開 pixel-level 對齊不可能的問題（Eq. 1, p.6）。
- Wan2.2-5B 經 SFT 後 PMF 從 $2.041 \to 2.978$、human rating 從 $2.26 \to 5.95$，FVD 從 $258 \to 190$，三項指標一致改善（Table 2, p.6）。
- long-term future frame prediction 顯示所有 4D modeling 方法在 novel viewpoint 下 PSNR 平均下降約 5 dB（DefGS $22.85 \to 17.95$），明確暴露 3D 物理建模的泛化缺口（Table 3, p.6）。
- physical property estimation 上 PAC-NeRF 與 GIC 對 Young's modulus $E$、Poisson's ratio $\nu$、viscosity $\mu$ 的估計誤差動輒上百，量化呈現現有 system identification 在複雜場景下的失效（Table 5, p.7）。
- 資產規模可觀：2,231 objects（~163 categories）、623 materials（5 大類）、528 backgrounds，且全數採用允許學術／商業使用的 license（§3.2, p.4；Appendix 5.2, p.15）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者承認 simulator 並非完美，僅以「errors are thoroughly studied and controlled」帶過，未量化 simulation gap（§3.4, p.5）。
- 主動排除 thermodynamics 與 acoustics 兩個 everyday physics 領域，理由是「rarely visible or require additional sensory data」，但這也使 dataset 對「全領域 world model」的覆蓋不完整（§1, p.2）。
- motion transfer 結果「remain largely unsatisfactory」，承認複雜物理運動的轉移目前尚無 baseline 可達到可用水準（§1 與 §4.4, p.3, p.8）。
- 在 physical property estimation 中明言兩個 baselines「fall short of accuracy in scenes with complex objects and backgrounds」，但將此歸因於方法、而非資料設計（§4.3, p.8）。

#### 4.2.2 Phyra-inferred

- PMF 的核心函數 $f_{energy}$ 在主文 Eq. 1 完全未定義（是 L1、L2、ratio？沿哪個 frequency axis？正規化？），讀者無法重現該指標，這對一個被當作主要貢獻的 metric 是嚴重缺陷（§4.1, p.6）。
- 「fine-tuning on PhysInOne 提升 physical plausibility」的論點與表格不符：SVD-LoRA 與 SVD-FLT 都讓 PMF 從 $2.753$ 退步到 $2.446$ / $2.464$，CogVideoX-LoRA 幾乎無變化（$2.877 \to 2.869$），只有 SFT 一致有效（Table 2, p.6）。
- PMF 與 human rating 的「高度相關」是質性宣稱，論文未提供 Pearson／Spearman 數值或 scatter plot，難以驗證該 metric 的 human alignment（§4.1, p.6）。
- evaluation set 規模偏小：test-small 772、test-mini 103、test-tiny 20，特別是 property estimation 每個 material 類別只有 4 個 scenes，標準差動輒大於均值（如 PAC-NeRF 的 $\log_{10}(E)$ $117.18 \pm 68.44$），統計顯著性未討論（Table 5, p.7）。
- fine-tuning 僅用了 83,650 videos（不到 dataset 的 5%），整個 2M 規模的「scaling」貢獻並未透過 scale curve 實證，2M 與 100K 的差別未被驗證（§4.1, p.5）。
- 未與 concurrent 工作 NewtonGen [94]、VideoPhy [6]、Physics-IQ [63] 在共同 benchmark 上做頭對頭比較，「largest of its kind」之外的方法論優勢無法被證偽（Table 1, p.3）。
- 全為 synthetic data，未提供任何 sim-to-real transfer 實驗（例如把 fine-tuned model 拿到 real video 上評估 physics violation 率），這是 world model 訓練資料最關鍵的開放問題卻完全未觸碰（全文）。
- 公開資源不足：BIBLIO.json 中 `code: null`，論文未提供 simulation pipeline、PMF 計算、或 fine-tuning script 的釋出時程（基本資訊）。
- multiphysics 的「sequential vs simultaneous」在 dataset 中未被區分標註，後續模型若要學「因果序」資訊（A 撞 B 才導致 B 落水）將難以利用（§3.3, p.4）。
- per-domain 結果（Table 2 右半）顯示 mechanics 與 optics 系統性低於 magnetism 與 fluid，但作者僅以「challenges for future research」一語帶過，未調查是否來自 simulator quality（Chaos vs MPM/SPH）的不平衡（§4.1, p.6）。

### 4.3 Phyra's Judgment (summary)

PhysInOne 真正的新意在於把 visual physics 的「現象廣度 × 場景複雜度 × 標註豐富度 × 規模」四個軸同時拉到前所未見的水準，並以多 simulator 編排支撐 multiphysics 的概念，這層 dataset engineering 確實是領域稀缺品。但模型側貢獻偏弱：所謂「fine-tuning 顯著提升 physical plausibility」其實只在 SFT 條件且只在部分模型成立，PMF 指標定義未閉環，且全程沒有 sim-to-real 驗證。核心未解問題是「dataset 提供的物理 ground truth 是否能讓模型學到可遷移的物理 prior，而不只是 fit 到 synthetic 渲染分佈」——這在本文不存在實驗答案。

## 5. Methodology Deep Dive

### 5.1 Method Overview

PhysInOne 提出的並不是一個新的模型，而是一條完整的「視覺物理資料生產管線」（Figure 2，page 4）。整條管線的核心命題是：要讓 foundation models 真正理解物理，資料必須在現象廣度、活動複雜度、場景多樣性、標註豐富度、絕對規模五個維度同時放大；因此管線將日常物理拆解為 4 個 core areas（mechanics、optics、fluid dynamics、magnetism）下的 71 個 basic phenomena，再藉由組合操作放大為 3,284 個 multiphysics activities，最終實例化為 153,810 個動態 3D 場景並以 12+1 多視角相機渲染為約 2,000,000 支具備密集 ground-truth 的影片（page 2、page 4 Figure 2）。

管線上半段是「資產到活動到場景」的離散組合過程。§3.1（page 4）固定了 71 個 phenomena 及其 governing laws（Newton's Laws、Conservation of Momentum、Hooke's Law、Bernoulli's Principle 等，完整對應表在 Appendix 5.1）；§3.2（page 4）收集 2,231 個 3D objects（涵蓋 solid、interactable、destructible、deformable、granular、liquid 六種類型，約 163 categories）、623 個 materials（plastic、metal、wood、stone、fabric 五類，每類附帶可調 friction coefficient、density、restitution 等物理屬性）、528 個 3D backgrounds；§3.3（page 4–5）以四步驟流程（Emulating Multiphysics、Setting Up Backgrounds、Placing Multiobjects、Varying Materials）將 single/double/triple-physics activities 各自實例化，平均每個 activity 對應 $46.84$ 個 scenes，每場景平均 $3.9/6.3/7.8$ 個 3D assets，呈現複雜度遞增的階梯。

管線下半段是「模擬到渲染到標註」的連續訊號生產過程。§3.4（page 5）依 object type 將動力學 dispatch 至三套 simulator：Chaos Physics（內建於 UE5，處理絕大多數 rigid 與 destructible 動力學）、MPM（以 Taichi 實作，處理 deformable 與 granular）、SPH（以 Doriflow 實作，處理 liquid）。§3.5（page 5）為每個 scene 部署 12 個 fixed cameras（在上半球以仰角 $30^\circ$ 至 $60^\circ$ 均勻取樣）加 1 個 moving monocular camera（以 random elevation 預先定義繞行軌跡），以 $1120 \times 1120$ 解析度、$30$ FPS（laser 相關 8,780 scenes 為 $60$ FPS）渲染平均 $5.2$ 秒影片。§3.6（page 5）同步輸出 depth、per-frame object masks、3D trajectories、object meshes、material properties，以及平均 $\sim 64$ 個英文字、經 Qwen3 校稿的人工敘事文本，並以 $8{:}1{:}1$ 切分 train/val/held-out test，且確保 3D assets 不跨集合，以避免 data leakage。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: 4 everyday physics domains {Mechanics, Optics, Fluid Dynamics, Magnetism}
   │
   ├→ [§3.1, p.4] Phenomenon Taxonomy
   │     governing laws: {Newton's, (Angular) Momentum/Mass Conservation,
   │                      Hooke's, Bernoulli's, ...}
   │     output: basic_phenomena, shape [71]
   │
   ├→ [§3.2, p.4] Asset Collection (Sketchfab / FAB / BlenderKit)
   │     ├─ objects:      shape [2231]   (6 sub-types, ~163 categories)
   │     ├─ materials:    shape [623]    (5 categories, with physics params)
   │     └─ backgrounds:  shape [528]    (indoor + outdoor, multi-scale)
   │
   ├→ [§3.3 Step 1, p.4–5] Activity Composition (curated combinatorial)
   │     ├─ single-physics: shape [71]
   │     ├─ double-physics: shape [943]    (filtered from C(71,2)=2485)
   │     └─ triple-physics: shape [2270]   (filtered from C(71,3)=57155)
   │     output: activities, shape [3284]
   │
   ├→ [§3.3 Step 2–4, p.5] Scene Instantiation
   │     for each activity a in [3284]:
   │       Step 2  pick background      b  ∈ [528]
   │       Step 3  place N_obj objects  N̄_obj = {3.9, 6.3, 7.8} (single/double/triple)
   │       Step 4  assign materials     m_i ∈ [623]; sample physical params
   │     output: scenes, shape [153810]    (≈ 46.84 scenes per activity)
   │
   ├→ [§3.4, p.5] Physics Simulation (router by object type)
   │     ├─ Chaos Physics @ UE5:  rigid + destructible    → object state traj
   │     ├─ MPM @ Taichi:         deformable + granular   → particle traj
   │     └─ SPH @ Doriflow:       liquid                  → particle traj
   │     per-scene dynamics over T frames; FPS = 30 (60 for 8780 laser scenes)
   │     T̄ ≈ ⌊5.2 × FPS⌋ ≈ 156 frames (variable)
   │
   ├→ [§3.5, p.5] Multi-View Rendering
   │     per scene: 12 fixed cameras (upper hemisphere, elevation 30°–60°)
   │              + 1 moving monocular camera (random-elevation orbit)
   │     RGB tensor (per scene):  shape [13, T, 1120, 1120, 3]
   │     output: video corpus,    shape [≈2,000,000]   (= 153810 × 13)
   │
   └→ [§3.6, p.5] Joint Annotation Generation
         ├─ text:          ~64 English words / scene (Qwen3-proofread)
         ├─ depth:         shape [13, T, 1120, 1120]
         ├─ masks:         shape [13, T, 1120, 1120]   (per-frame object masks)
         ├─ 3D traj:       shape [N_obj_dyn, T, 3]
         ├─ meshes:        per-object, per-frame
         └─ properties:    {E, ν, μ, κ, τ_Y, η, θ_fric, ...}
         split: 8:1:1 (train / val / held-out test); 3D-asset-disjoint partitions
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Physical Phenomenon Taxonomy

**Function:** 定義整條管線的「物理詞彙表」，將日常物理離散化為一組可組合、可標註、且各自綁定 governing laws 的 basic phenomena。

**Input:**
- Name: `physics_areas`
- Shape: `[4]` (mechanics, optics, fluid dynamics, magnetism)
- Source: 由 textbook *Fundamentals of Physics* [39] 與 [62, 63] 推得（page 2）

**Output:**
- Name: `basic_phenomena`
- Shape: `[71]`
- Consumer: §3.3 Step 1 Activity Composition

**Processing:**

1. 從四個 core areas 中刪除 thermodynamics 與 acoustics（page 2 說明：兩者通常不可見或需要溫度/聲音額外感測）。
2. 依日常出現頻率與視覺可觀測性，逐一列舉如 gravity、reflection、buoyancy、magnetic attraction 等 71 個 basic phenomena。
3. 為每個 phenomenon 綁定一個或多個 governing laws，作為後續 simulator 參數設定與 ground-truth 校驗的依據。

**Key Formulas:**

paper 並未給出 phenomenon 的閉式定義；governing laws 以名稱列舉，例如 Newton's Laws、Conservation of (Angular) Momentum、Hooke's Law、Bernoulli's Principle（page 4 §3.1）。

**Implementation Details:**

71 個 phenomena 與其 governing laws 的完整對應表放在 Appendix 5.1（main text 未列出）。$71$ 是「廣度」維度的關鍵數字，相較 ShapeStacks/CLEVRER 的單一現象與 Physion 的 8 種，呈一個數量級的差距（Table 1，page 3）。

#### 5.3.2 3D Asset Collection

**Function:** 提供場景實例化所需的視覺與物理素材池，使同一個 phenomenon 能在不同物件、材質、背景下被反覆呈現以避免單一化。

**Input:**
- Name: `phenomenon_targets`
- Shape: `[71]`
- Source: §3.1 phenomenon 清單，作為「需涵蓋哪些互動類型」的需求向量

**Output:**
- Name: `assets = (objects, materials, backgrounds)`
- Shape: `objects [2231]`、`materials [623]`、`backgrounds [528]`
- Consumer: §3.3 Steps 2–4 Scene Instantiation

**Processing:**

1. **Objects** 從 Sketchfab [77]、FAB [30]、BlenderKit [11] 收集 $2{,}231$ 個物件，依與 phenomena 的互動形式劃分為六類：solid、interactable（可動部件，UE Blueprints）、destructible（可破壞，UE Geometry Collections）、deformable（MPM）、granular（MPM，例如 sand）、liquid（SPH，例如 water、cream、milk）。
2. **Materials** 收集 $623$ 個橫跨 plastic、metal、wood、stone、fabric 五類；每個 material 暴露 friction coefficient、density、restitution 等可調 physical attributes，作為「同一物件、不同材質」的變化軸。
3. **Backgrounds** 收集 $528$ 個 indoor 與 outdoor 環境（living rooms、bedrooms、factories、swimming pools 等），覆蓋不同空間尺度。

**Key Formulas:**

paper 未給出資產採樣機率的閉式表達；採集策略以「與 phenomena 直接相關」為篩選條件（page 4 §3.2），這也是 PhysInOne 與 Objaverse/XL 等通用 3D 倉儲的關鍵差異。

**Implementation Details:**

所有 3D assets 皆為 academic 與 commercial 雙授權（page 4）。資產類型直接決定 §3.4 的 simulator 路由：deformable/granular 走 MPM、liquid 走 SPH、其餘走 Chaos Physics。更多細節在 Appendix 5.2。

#### 5.3.3 Multiphysics Activity Composition

**Function:** 將 71 個 basic phenomena 透過組合操作放大為 3,284 個 multiphysics activities，模擬日常活動中多個物理現象同時或序列發生的複雜性。

**Input:**
- Name: `basic_phenomena`
- Shape: `[71]`
- Source: §3.1 輸出

**Output:**
- Name: `activities = single ∪ double ∪ triple`
- Shape: `[71] ∪ [943] ∪ [2270] = [3284]`
- Consumer: §3.3 Steps 2–4 Scene Instantiation

**Processing:**

1. **Single-physics:** 每個 basic phenomenon 直接視為一個 single-physics activity，得 $71$ 個。
2. **Double-physics:** 從 $\binom{71}{2} = 2485$ 個 pair 中經人工篩選保留物理意義合理者，得 $943$ 個 double-physics activities（page 4–5）。
3. **Triple-physics:** 從 $\binom{71}{3} = 57155$ 個 triple 中經篩選得 $2270$ 個 triple-physics activities（page 5）。

**Key Formulas:**

$$
|\mathcal{A}| = 71 + 943 + 2270 = 3284
$$

其中 $943 \ll \binom{71}{2}$、$2270 \ll \binom{71}{3}$ 體現「許多組合 lack physical meaning」的人工 curation 結果（page 4–5）。

**Implementation Details:**

paper 未公開 curation 的具體 rubric，僅描述為「careful selection」（page 4–5）。activities 此時仍是 conceptual，尚未實例化為具體 3D 場景，留待 Step 2–4 完成。

#### 5.3.4 Scene Instantiation Pipeline

**Function:** 把 conceptual 的 3,284 個 activities 物質化為 153,810 個 unique 動態 3D scenes，每個 scene 是一組 (背景, 物件群, 材質配置) 的具體 instance。

**Input:**
- Name: `(activities, assets)`
- Shape: `activities [3284]`、`(objects [2231], materials [623], backgrounds [528])`
- Source: §3.3 Step 1 與 §3.2

**Output:**
- Name: `scenes`
- Shape: `[153810]`
- Consumer: §3.4 Physics Simulation

**Processing:**

對每個 activity $a \in [3284]$ 重複以下流程：

1. **Step 2 — Setting Up Backgrounds:** 從 $528$ 個 backgrounds 挑選與 activity 物理可信的環境（例如 fluid 活動配 swimming pool）。
2. **Step 3 — Placing Multiobjects:** 從 objects 池中挑 $N_{\text{obj}}$ 個 assets 放入背景，$N_{\text{obj}}$ 隨複雜度增加：single/double/triple-physics 平均為 $3.9/6.3/7.8$（page 5）。
3. **Step 4 — Varying Materials:** 對每個 asset 替換 material 並重新採樣 friction、density、restitution 等 physical parameters，產生同一活動的多個變體場景。

**Key Formulas:**

$$
\bar{S}_{\text{per-activity}} = \frac{153810}{3284} \approx 46.84
$$

每個 activity 平均對應 $46.84$ 個 unique scenes（page 5）。

**Implementation Details:**

paper 未揭露 Step 2–4 的自動化程度（人工挑選比例、是否使用啟發式排版器等）；僅在 Appendix 5.3 提供更多細節。物件數階梯 $3.9 < 6.3 < 7.8$ 是場景複雜度與 activity 複雜度正相關的直接量化證據。

#### 5.3.5 Multi-Engine Physics Simulation

**Function:** 依據 scene 中物件的物理屬性，將動力學求解 dispatch 至三套不同 simulator，使所有 153,810 個 scenes 的 ground-truth trajectory 嚴格遵守 governing laws。

**Input:**
- Name: `scenes`
- Shape: `[153810]`
- Source: §3.3 Step 4 輸出

**Output:**
- Name: `dynamics_traj`
- Shape: 每個 scene 對應 $T$ 個 frames 的 object/particle states；$T$ 可變、$T \approx 5.2 \times \text{FPS}$
- Consumer: §3.5 Multi-View Rendering

**Processing:**

1. 對每個 scene 中的 assets 檢查類型，決定 simulator 路由。
2. **Chaos Physics @ UE5 [81]:** 處理絕大多數 daily phenomena（rigid body 動力學、destructible 破壞模擬）。
3. **MPM @ Taichi [79]:** 處理 deformable 與 granular，採用 Moving Least Squares MPM [43]。
4. **SPH @ Doriflow [27]:** 處理 liquid，採用 Smoothed Particle Hydrodynamics [35]。
5. 三個 simulator 在同一場景內可並行/串接，以支援 multiphysics activities 中異質物件共存的需求。

**Key Formulas:**

paper 未在 main text 列出 simulator 內部的 PDE 或離散化公式；僅引用 MPM [43]、SPH [35]、XPBD [60] 等原始論文。governing laws 在 simulator 中以參數約束形式生效（如 Newton's $F=ma$、Hooke's $\sigma = E\varepsilon$ 等隱含於各 solver）。

**Implementation Details:**

paper 明確承認「current simulators may not achieve perfect physical fidelity」，但其誤差「are thoroughly studied and controlled」並引用 [32, 60]（page 5）。physical parameter 的取值範圍在 Appendix 5.4。simulator 路由策略並未以可程式化的形式在 main text 揭露。

#### 5.3.6 Multi-View Rendering and Joint Annotation

**Function:** 將模擬結果以 12 fixed + 1 moving monocular cameras 渲染為高解析度影片，並同步輸出 geometry、semantics、motion、physical properties、text 五類 ground-truth annotations，最終產出 2 million 級的監督訊號。

**Input:**
- Name: `dynamics_traj`
- Shape: 每個 scene 的 $T$ frames 動力學狀態
- Source: §3.4 輸出

**Output:**
- Name: `(videos, annotations)`
- Shape:
  - `videos`：總計約 $2 \times 10^6$ 支（$153810 \times 13 = 1{,}999{,}530$），每支 $[T, 1120, 1120, 3]$
  - `depth`、`masks`：與 RGB 同形狀，$[13, T, 1120, 1120]$
  - `3D trajectories`：$[N_{\text{obj}_{\text{dyn}}}, T, 3]$
  - `text`：每 scene 約 $64$ 個英文字
- Consumer: §4 Applications（video generation、future frame prediction、property estimation、motion transfer）

**Processing:**

1. **相機部署（§3.5）：** 12 fixed cameras 在 upper hemisphere 以 elevation $\in [30^\circ, 60^\circ]$ 均勻取樣，positions 隨場景空間配置調整；1 moving camera 以 random elevation 沿預定軌跡環繞活動中心。
2. **渲染（§3.5）：** 解析度 $1120 \times 1120$、$30$ FPS；laser 相關的 $8{,}780$ scenes 因高頻光學動力學提升至 $60$ FPS；平均影片長度 $5.2$ s。
3. **annotation 同步輸出（§3.6）：** 渲染過程同時生成 depth images、per-frame object masks、object 3D trajectories、object meshes、material properties。
4. **文本標註（§3.6）：** 人工撰寫敘事段落並以 Qwen3 校稿，平均 $\sim 64$ 個 English words/scene。
5. **資料切分（§3.6）：** 以 $8{:}1{:}1$ 切分為 train/val/held-out test，並確保 3D assets 不跨 partition 出現以避免 data leakage。

**Key Formulas:**

$$
|\mathcal{V}| = |\mathcal{S}| \times (C_{\text{fix}} + C_{\text{mov}}) = 153810 \times (12 + 1) = 1{,}999{,}530 \approx 2 \times 10^6
$$

其中 $C_{\text{fix}} = 12$、$C_{\text{mov}} = 1$（page 5）。

**Implementation Details:**

paper 未具體說明 fixed cameras 在每個場景內的 azimuth 採樣方式（僅說「positions vary across scenes according to different spatial arrangements and backgrounds」）。moving camera 的 trajectory 描述為「typically circling the activity at random elevation angles」，未提供軌跡長度或速度的數值範圍。Annotation 品質依賴「standardized development and independent validation」的 workflow，細節在 Appendix 5.5、5.6。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| PhysInOne (full) | 全資料集劃分 | 153,810 個 3D scenes、2 million videos | 8:1:1 train/val/held-out test，3D assets 不跨切分以避免 leakage |
| PhysInOne train subset | Video generation fine-tuning（§4.1）；ExtDM from-scratch training（§4.2.1） | 83,650 text-video pairs | train（隨機抽樣 fine-tune SVD-XT、CogVideoX-1.5-5B、Wan2.2-5B 至收斂；ExtDM 同樣以此子集 train from scratch） |
| PhysInOne test-small | Video generation 評估（§4.1） | 772 text-video pairs | test |
| PhysInOne test-mini | Long-/short-term future frame prediction（§4.2） | 103 dynamic 3D scenes（seen + novel viewpoints） | test |
| PhysInOne test-tiny | Physical properties estimation（§4.3） | 20 scenes（5 material categories × 4 scenes） | test |
| PhysInOne val subset | Motion transfer（§4.4） | 273 dynamic 3D scenes（成對生成 source/target） | val |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| PMF (Physical Motion Fidelity) | 本論文新提出之指標，將 reference video $V_{\text{ref}}$ 與 generated video $V_{\text{gen}}$ 透過 DFT 轉到頻域後比較其能量（squared amplitude），定義為 $\text{PMF} = f_{\text{energy}}\bigl(\text{DFT}(V_{\text{gen}}), \text{DFT}(V_{\text{ref}})\bigr)$，分數越高代表動態軌跡越貼近 reference；用於量化物理運動保真度而非像素對齊 | yes |
| FVD | 視訊生成的 visual realism 傳統指標，越低越好 | no |
| Human Rating | User study 評分，越高代表人類感知到的物理合理性越強 | no |
| PSNR | 重建/預測影格的像素級訊噪比，越高越好 | no |
| SSIM | 結構相似度，越高越好 | no |
| LPIPS | 感知相似度距離，越低越好 | no |
| 物理參數估計誤差 | 對 $\log_{10}(E)$、$\nu$、$\log_{10}(\tau_Y)$、$\log_{10}(\mu)$、$\log_{10}(\kappa)$、$\log_{10}(\eta)$、$\theta_{\text{fric}}$、initial velocity $v$ 等與 ground truth 的差異（mean ± std），越低越好 | no |

### 6.3 Training and Inference Settings

- Hardware：the paper does not specify。
- Fine-tuning 對象：SVD-XT [10]、CogVideoX-1.5-5B [91]、Wan2.2-5B [83]，分別套用 LoRA、SFT、FLT 三種技術（見 §4.1，細節 in Appendix 5.7）。
- Fine-tuning 資料量：隨機抽樣 83,650 text-video pairs，所有模型 fine-tune 至 convergence。
- Batch size、optimizer、learning rate schedule、training steps：the paper does not specify（正文僅指向 Appendix 5.7；本次提供之 appendix 節錄到 §5.4 為止，未含這些超參數）。
- 資料合成端：Chaos Physics（UE5 [81]）處理多數剛體與互動；MPM via Taichi [79] 處理 deformable 與 granular；SPH via Doriflow [27] 處理 liquid（Blender 4.3.0、Doriflow 1.3）。
- Rendering：12 個 static cameras 均勻分佈於 elevation $30^\circ \sim 60^\circ$ 的上半球，加 1 個 monocular moving camera；解析度 $1120\times1120$、30 FPS（含 laser 的 8,780 個 scenes 為 60 FPS），平均長度 5.2 秒。
- 推論／預測設定：Long-term future frame prediction 預測「scene 後半段約 2.6 秒、約 78 frames」，輸入為前半段 video clip；Short-term 為連續即時預測「下 10 frames」（見 §4.2.1、§4.2.2）；MAGI-1 直接使用 pretrained model，未經 PhysInOne fine-tune。
- Resimulation 設定：對估出之物理參數，於 novel initial conditions（如改變物件位置）下重新模擬，與以 ground-truth physics 在相同 novel conditions 下渲染之 reference videos 比較（§4.3）。

### 6.4 Main Results

**Physics-aware Video Generation（test-small, 772 pairs；§4.1, Table 2）**

| Method | PMF ↑ | FVD ↓ | Human Rating ↑ | Notes |
|---|---|---|---|---|
| SVD [10] | 2.753 | 203 | 6.09 | baseline |
| **SVD$_{\text{sft}}$** | **3.147** | **143** | **6.08** | 在 SVD 系列中三項指標最佳 |
| SVD$_{\text{lora}}$ | 2.446 | 150 | 5.82 | LoRA 反而下降 |
| SVD$_{\text{flt}}$ | 2.464 | 147 | 5.45 | |
| CogVideoX [91] | 2.877 | 165 | 2.98 | baseline |
| CogVideoX$_{\text{lora}}$ | 2.869 | 149 | 2.95 | PMF 幾乎持平 |
| Wan2.2-5B [83] | 2.041 | 258 | 2.26 | baseline |
| **Wan2.2-5B$_{\text{sft}}$** | **2.978** | 190 | **5.95** | PMF 與 Human Rating 均最佳 |
| Wan2.2-5B$_{\text{lora}}$ | 2.785 | **178** | 4.80 | FVD 在 Wan 系列中最低 |
| Wan2.2-5B$_{\text{flt}}$ | 2.227 | 341 | 2.61 | FLT 反而劣化 |

依物理領域拆分（PMF）：多數模型在 magnetism 與 fluid 上得分較高、mechanics 與 optics 較低。

**Long-term Future Frame Prediction（test-mini, 103 scenes；seen / novel；§4.2.1, Table 3）**

| Method | PMF ↑ | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Notes |
|---|---|---|---|---|---|
| TiNeuVox [31] | 3.710 / 2.885 | 21.49 / 15.20 | 0.633 / 0.452 | 0.517 / 0.665 | |
| DefGS [90] | 3.980 / **3.347** | 22.85 / **17.95** | **0.833** / 0.598 | **0.192** / 0.348 | novel view 多項最佳 |
| TRACE [53] | 3.869 / 3.242 | 22.42 / 17.44 | 0.756 / 0.599 | 0.295 / 0.422 | |
| FreeGave [54] | 3.897 / 3.265 | 22.57 / 17.75 | 0.818 / **0.619** | 0.219 / **0.355** | |
| ExtDM [98] | 3.363 / – | 19.55 / – | 0.657 / – | 0.771 / – | 僅報告 seen view |
| MAGI-1 [1] | **4.086** / – | **23.14** / – | 0.788 / – | 0.364 / – | seen-view PMF/PSNR 最佳，未跑 novel view |

**Short-term Future Frame Prediction（test-mini；seen / novel；§4.2.2, Table 4）**

| Method | PMF ↑ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---|---|---|---|
| DefGS [90] | 4.536 / **3.728** | 26.02 / **20.92** | 0.861 / **0.739** | 0.206 / 0.322 |
| FreeGave [54] | **4.742** / 3.706 | **27.09** / 20.80 | 0.876 / 0.715 | 0.199 / 0.336 |
| ExtDM [98] | 3.774 / – | 22.14 / – | 0.717 / – | 0.715 / – |
| MAGI-1 [1] | 4.696 / – | 26.75 / – | **0.886** / – | **0.116** / – |

**Physical Properties Estimation（test-tiny, 20 scenes；§4.3, Table 5 + resimulation Table 6）**
PAC-NeRF [55] 與 GIC [14] 在 elastic solids、plasticine、Newtonian fluids、non-Newtonian fluids、granular substances 五類材料上互有勝負；resimulation 比較中 GIC 全面領先（PMF 5.938 vs. 5.617、PSNR 26.90 vs. 24.12、SSIM 0.950 vs. 0.942、LPIPS 0.074 vs. 0.086）。論文結論為兩者於本資料集複雜物件與背景下準確度均不足。

**Motion Transfer（val 子集 273 scenes；§4.4, Table 7）**

| Method | PMF ↑ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---|---|---|---|
| GoWithTheFlow [13] | 3.309 | 18.98 | 0.691 | 0.410 |
| **MotionPro [99]** | **3.484** | **20.28** | **0.775** | 0.467 |

Notes：本論文並未提出新模型作為「我方方法」；上方加粗者為各任務中表現最佳的條目，主張在於「以 PhysInOne fine-tune 後 SVD$_{\text{sft}}$、Wan2.2-5B$_{\text{sft}}$ 顯著優於原 baseline」，這是論文核心 claim 對應的結果。

### 6.5 Ablation Studies

本論文未設計傳統意義下針對自家「新模組」的 ablation（因為核心貢獻是 dataset 而非 model）。可視為 ablation 性質的對照如下：

- **Fine-tuning 技術對照（LoRA vs. SFT vs. FLT vs. baseline）**：在 SVD、CogVideoX、Wan2.2 三個模型上同時跑四種設定。結果顯示 SFT 對 SVD 與 Wan2.2 均明顯抬升 PMF（SVD：2.753 → 3.147；Wan2.2：2.041 → 2.978），但 FLT 反而劣化 Wan2.2（2.041 → 2.227，FVD 從 258 升到 341），LoRA 對 SVD 也是負向（2.753 → 2.446）。此對照能診斷「PhysInOne 的訓練訊號需要足夠強的 fine-tuning capacity 才能轉化成物理保真度」，屬於有診斷價值的設計，而非單純 sanity check。
- **依物理領域分項 PMF（Table 2 右半）**：將 PMF 拆成 mechanics / magnetism / optics / fluid 四欄。這是診斷性對照，揭露 mechanics 與 optics 較難學的弱點，而非單純展示總體分數。
- **Seen vs. Novel viewpoint（Table 3、Table 4）**：所有 4D 方法在 novel view 上一致退化（例如 DefGS PSNR 22.85 → 17.95），有效診斷出「現有方法在 3D 空間泛化物理動態的能力不足」，這是有意義的對照而非 sanity check。
- **缺乏的 ablation**：未對 PhysInOne 的「scale 對 fine-tuning 效果」、「資料子集（單／雙／三 physics）對結果」、「camera 數量對 4D 方法」等做拆解。整體而言，論文沒有針對 dataset 的成分（71 phenomena、12+1 cameras、annotation 完整性）做 ablate-by-removal 式診斷實驗，這是讀者最可能想看但缺席的 ablation。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline (a current SoTA on the chosen task) — 各任務挑了當期代表性方法（SVD、CogVideoX、Wan2.2、MAGI-1、DefGS、TRACE、FreeGave、PAC-NeRF、GIC、MotionPro、GoWithTheFlow），但論文未明確指出哪一個是該任務 SoTA、也未與最強通用基線（如最新 closed-source 視訊生成模型）對齊比較。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同一 PhysInOne 上跨 4 個任務（video generation、future frame prediction、physical property estimation、motion transfer）評估，雖未跨外部 dataset，但跨任務多樣性充足。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — 有 LoRA/SFT/FLT、seen/novel view、依物理領域拆分等診斷性對照（§6.5），但缺少對 dataset 規模、phenomena 涵蓋面、annotation 種類的 ablate-by-removal 分析。
- [missing] Has a scaling study (size, length, or compute) — 未報告改變 fine-tuning 樣本數（如 10k／30k／83k）或 epoch／step 的曲線，僅以單一 83,650 pairs 子集訓練至 convergence。
- [missing] Has an efficiency / wall-clock comparison — 全文未提供任一方法的訓練/推論 wall-clock、GPU hours、throughput 比較。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — Table 5 對物理參數估計報告 mean ± std（跨 4 scenes/category），但 video generation、future frame prediction、motion transfer 的所有指標皆為單次數值，未跑多 seeds。
- [partial] Releases code / weights / data sufficient for reproducibility — 提供 project page（https://vlar-group.github.io/PhysInOne.html）並聲明所有 3D assets 取自允許學術／商業使用之來源（Sketchfab、FAB、BlenderKit、ShareTextures），但正文未明確承諾 release 訓練 code、fine-tuned weights、或 PMF 計算腳本，the paper does not specify 是否會公開 fine-tuning checkpoints。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 規模與多樣性遠超既有 dataset。** 充分支持。Table 1 並排比較顯示 PhysInOne 在 # phenomena (71)、# scenes (153,810)、# videos (2M)、multiphysics、複雜物件與背景、相機數量、annotation 完整度等所有欄位均勝出（Table 1, p.3）。
- **C2: fine-tuning 在 PhysInOne 上能提升 video generation 的物理可信度。** 部分支持／有過度泛化嫌疑。Table 2 中 SVD-SFT 與 Wan2.2-SFT 確實同時改善 PMF、FVD、human rating，但 SVD-LoRA／SVD-FLT／CogVideoX-LoRA 並未改善甚至退步；論文 abstract 與 §4.1 的措辭未反映此分歧（Table 2, p.6）。
- **C3: PhysInOne 暴露現有方法在複雜物理動態與屬性估計上的 gap。** 充分支持。novel viewpoint 下 4D 方法 PSNR 普遍下降 4–6 dB（Table 3）、property estimation 多項參數誤差大於均值一個數量級（Table 5）、motion transfer PSNR 僅 18.98–20.28（Table 7），三條獨立證據一致（Tables 3, 5, 7, p.6–8）。
- **C4: PMF 是評估 physical motion fidelity 的有效新指標、且與人類感知高度相關。** 過度宣稱。指標公式只給到 $\mathrm{PMF} = f_{energy}(\mathrm{DFT}(V_{gen}), \mathrm{DFT}(V_{ref}))$，$f_{energy}$ 未定義；human correlation 僅靠 Table 2 兩列「同向」的觀察，未提供任何相關係數或統計檢定（Eq. 1 與 §4.1, p.6）。
- **C5: 動力學嚴格遵循 Newton 定律、動量守恆、Hooke 定律等。** 部分支持。引擎本身（Chaos／MPM／SPH）確實基於這些定律，但作者自承 simulator 有誤差且未量化，per-domain PMF 上 mechanics 反而低於 magnetism／fluid，間接顯示 simulation quality 不均衡（§3.4 與 Table 2 右側, p.5–6）。

### 7.2 Fundamental Limitations of the Method

**Synthetic-only 訓練資料的 sim-to-real gap 完全未被處理。** Dataset 全部由 UE5 Chaos、MPM 與 SPH 渲染，texture、lighting、相機軌跡都帶有可辨識的 synthetic signature。論文未提供 fine-tuned model 在任一 real video benchmark（如 VideoPhy、Morpheus、Physics-IQ real splits）上的評估，因此「improving physical plausibility」可能只是讓 generator 更接近 PhysInOne 的渲染分佈，而非真正吸收物理 prior。這在 architecture 不變的前提下無法以 dataset 工作本身解決。

**PMF 指標定義不閉環。** Eq. 1 把 PMF 寫成 $f_{energy}$ 套上 $\mathrm{DFT}$ 的差距，但對 video tensor 形狀為 $[T, H, W, C]$ 時 DFT 沿哪些軸、能量如何 aggregate、是否做 spatial／temporal normalization 完全未說明。從 Table 2–7 的數值範圍 1.5–6 也看不出有 well-defined upper bound 或 null baseline（如 random video 的 PMF 是多少）。沒有這些，PMF 既不可重現也不可作為跨論文比較的標準，與 FVD 並列為主要指標的定位站不住。

**評估規模與置信區間不足以支撐結論。** test-tiny 只有 20 個 scene、每 material 類別 4 個樣本，property estimation 的標準差幾乎都大於均值（例 PAC-NeRF 的 $\log_{10}(E)$: $117.18 \pm 68.44$），這個 sample size 下宣稱「baselines fall short」缺乏統計力。long-term prediction 的 test-mini 103 場景對於跨 method ranking 也偏小，特別是 MAGI-1 與 DefGS 的 PMF 差距僅 0.1，未做顯著性測試。

**多現象組合的學習效益未實證。** 3284 個 multiphysics activities 是論文的招牌數字之一，但所有 fine-tuning 與 benchmark 都沒有 ablation 比較「只訓 single-physics」vs「single+double+triple」對下游 PMF 的影響。如果 generator 學到的只是 71 個 atomic phenomena，那 943 + 2270 個組合活動就只是 data augmentation 而非 conceptual breakthrough，這個關鍵問題在當前 formulation 下沒有實驗答案。

### 7.3 Citations Worth Tracking

- **Physics-IQ [63] (Motamed et al., arXiv'25)**: 同期 physics understanding benchmark，且論文以它為主要 motivation 之一；要評估 PhysInOne 訓練收益是否能轉移到 real-world physics，這是現成的對照組。
- **NewtonGen [94] (ICLR'26)**: concurrent work，主打用 Newtonian dynamics 約束生成而非 dataset 規模，正好與 PhysInOne 形成「資料路線 vs 模型路線」對照，值得讀來判斷哪條路 ROI 較高。
- **PAC-NeRF [55] (Li et al., NeurIPS'23)**: 本文 property estimation 的主要 baseline，且 PhysInOne 的 elastic／plasticine／fluid／granular 五分類設計直接沿用其框架；要復現或改進 system identification 必讀。
- **VideoPhy [6] (Bansal et al., ICLR'25)**: 提供 text–video physical commonsense 的 human-rated benchmark；如果想把 PhysInOne fine-tuned model 拉到 real-world physics 評估，這是最直接的 sim-to-real 測試平台。
- **"How Far is Video Generation from World Model" [47] (Kang et al., ICML'25)**: 作者引用為 motivation，分析 video generator 違反物理的具體失敗模式，能幫助判斷 PMF 是否真正捕捉到了那些失敗模式。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在 PhysInOne 上 fine-tune 的 SVD/CogVideoX/Wan2.2，拿到 real-world video benchmark（如 VideoPhy 或 Physics-IQ real split）上，physical plausibility 是否仍然提升，還是只是 overfit 到 UE5 渲染分佈？
- [ ] PMF 中的 $f_{energy}$ 的精確定義是什麼（沿哪些軸做 DFT？如何 aggregate？是否 normalize？），以及它與 human rating 的 Pearson／Spearman 相關係數實際是多少？
- [ ] 為何 LoRA 對 SVD 與 CogVideoX 無效甚至退步，但對 Wan2.2 大幅有效（PMF $2.041 \to 2.785$）？是 base model 物理先驗強弱差異、還是 LoRA rank／layer 選擇問題？
- [ ] 把訓練集從 single-physics（71 類）逐步擴展到 +double（+943）、+triple（+2270），下游 PMF 與 human rating 的 scale curve 長什麼樣？multiphysics 組合是否真的帶來 marginal gain？
- [ ] 為什麼 per-domain PMF 上 mechanics 系統性低於 magnetism 與 fluid？是因為 Chaos Physics 在 mechanics 模擬上品質較差，還是因為 model architecture 對剛體運動的 inductive bias 較弱？
- [ ] test-tiny 只有 20 個 scenes、每 material 4 個樣本的情況下，PAC-NeRF 與 GIC 之間的 ranking 是否在更大樣本下穩定？標準差大於均值的多項估計是否其實不可區分？
- [ ] 將 fine-tuning 規模從 83,650 videos 擴大到全 2M，PMF 與 FVD 的改善是否持續，或在某個點飽和？整套 2M 規模的 marginal value 是多少？

### 8.2 Improvement Directions

1. **形式化並驗證 PMF**（最高可行性）：在 supplementary 補上 $f_{energy}$ 的完整公式（DFT 軸、normalization、距離度量）、null baseline（random video、frozen frame）的 PMF 數值、以及 PMF vs human rating 的 scatter plot 與相關係數。理由：這是論文目前最低成本就能彌補的硬傷，補完之後 PMF 才有資格作為跨論文 metric。
2. **加上 sim-to-real transfer 實驗**（中等可行性）：把 fine-tuned 的 SVD-SFT 與 Wan2.2-SFT 拿到 VideoPhy 與 Physics-IQ 的 real video splits，回報 physical plausibility 是否提升。理由：這直接回應 dataset 是否解決了 motivation 中所述的真實 video 物理違反問題，否則 dataset 的價值仍停留在 synthetic 自圓其說。
3. **跑 dataset scale curve**（中等可行性）：在固定 architecture／hyperparameter 下，以 10K／50K／200K／1M／2M 五檔訓練量 fine-tune Wan2.2-SFT，觀察 PMF 與 FVD 的 scaling law。理由：這會讓「2M 是必要的」這個論點從口號變成證據，也能告訴後人 dataset 該下載多少。
4. **multiphysics ablation**（中等可行性）：分別只用 single-physics、single+double、single+double+triple 三種子集 fine-tune，比較下游 PMF。理由：直接驗證 3284 個 activities 的概念貢獻是否大於 71 atomic phenomena 的 augmentation 效應，這是論文 narrative 的核心檢驗點。
5. **per-domain simulation quality 審計**（較低可行性，需 ground-truth 物理計算）：對 mechanics／optics／fluid／magnetism 各取若干 scene，把模擬軌跡與解析解或高精度求解器比較，量化 simulator-induced error 的分布；以此解釋 per-domain PMF 落差。理由：作者目前以「errors thoroughly studied」一筆帶過，但 per-domain 表現差異暗示 simulator quality 並不一致，量化後可幫助使用者選擇 domain subset。
6. **擴張到 thermodynamics 與 acoustics**（最低可行性）：以同樣 pipeline 加入 visible 熱效應（蒸氣、融化、熱輻射可視化）與 audio-conditioned 物理活動。理由：這兩個被排除的領域是 world model 完整性的明顯缺口，工程上可能需要新 simulator 與 sensor，成本最高，但在 dataset 持續演進的脈絡下是合理的下一步。
