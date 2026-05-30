<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# PointWorld — PointWorld: Scaling 3D World Models for In-The-Wild Robotic Manipulation

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | PointWorld |
| Paper full title | PointWorld: Scaling 3D World Models for In-The-Wild Robotic Manipulation |
| arXiv ID | 2601.03782 |
| Release date | 2026-01-07 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2601.03782 |
| PDF link | https://arxiv.org/pdf/2601.03782v1 |
| Code link | — |
| Project page | https://point-world.github.io |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Wenlong Huang | Stanford University (work done partly at NVIDIA) | https://wenlong.page/ | first author |
| Yu-Wei Chao | NVIDIA | — | co-author |
| Arsalan Mousavian | NVIDIA | — | co-author |
| Ming-Yu Liu | NVIDIA | — | co-author |
| Dieter Fox | NVIDIA | — | co-author |
| Kaichun Mo | NVIDIA | https://kaichun-mo.github.io/ | co-corresponding (equal advising) |
| Li Fei-Fei | Stanford University | https://profiles.stanford.edu/fei-fei-li | co-corresponding (equal advising) |

### 1.2 Keywords

3D world model, point flow, robotic manipulation, RGB-D, MPC, MPPI, DROID, scaling laws

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| DROID (Khazatsky et al.) | base model | 大規模真實機器人操作資料集,作者用於提取 3D 點流標註以建立訓練資料 |
| BEHAVIOR-1K (Li et al.) | base model | 光真實模擬環境,作為模擬域訓練資料來源,涵蓋全身操作 |
| FoundationStereo (FS) | influence | 用於替換感測器深度,提供更精準近距離操作深度估計 |
| VGGT | influence | 提供相機外參初始估計,後續再以機器人深度對齊優化 |
| Point Transformer v3 (PTv3) | base model | 作為點雲 backbone 處理串接的場景與機器人點雲 |
| DINOv3 | base model | 凍結的 2D 視覺編碼器,用於對場景點賦予影像特徵 |
| MPPI (Williams et al.) | influence | 取樣式 MPC 規劃器,在推論時用於從世界模型衍生動作 |

## 2. Research Overview

### 2.1 Research Topic

本研究提出 POINTWORLD,一個大規模預訓練的 3D 世界模型,用於野外環境(in-the-wild)的機器人操作。其核心想法是將狀態與動作統一表示為 3D 點流(point flow):場景以 RGB-D 反投影得到的點雲表示;機器人動作則透過 URDF 與正向運動學產生對應的 3D 點軌跡。模型在單次前向推論中預測未來 H 步的全場景 per-pixel 3D 位移,藉此隱含學習物件性、材質、關節結構與接觸動力學。作者整理約 200 萬條軌跡、500 小時的真實與模擬資料集,涵蓋單臂、雙臂、全身與行動操作,並系統性研究 backbone、動作表示、目標函數、部分可觀測性、資料混合與規模化等設計選擇。模型推論延遲約 0.1 秒,能與 MPPI 採樣式 MPC 結合,使單一預訓練模型在僅一張 RGB-D 影像、無需任何示範或微調的情況下,於真實 Franka 機器人上完成剛體推動、可變形物體、關節物體操作與工具使用等多樣任務。

### 2.2 Domain Tags

- robotics
- robotic manipulation
- 3D vision
- world models
- model-predictive control

### 2.3 Core Architectures Used

- **Point Transformer v3 (PTv3)**:作為主要的點雲 backbone,負責處理串接後的場景點與機器人動作點,以 U-net 階層化注意力同時建模局部接觸與長距離互動,並支援 50M 至 1B 參數的規模化擴展。
- **DINOv3 (frozen ViT)**:作為 2D 視覺編碼器,將場景點投影至校正後相機視角後抽取多層稠密特徵,為點雲提供物件性與外觀先驗,而不需顯式分割。
- **URDF + Forward Kinematics**:將機器人關節空間動作轉換為 embodiment-agnostic 的 3D 機器人點流,確保「想像中的動作」即使在遮擋下也是完全可觀測。
- **FoundationStereo + VGGT + CoTracker3 標註管線**:在資料側分別提供精準近距深度、初始相機外參、以及 2D 點追蹤,經由與機器人 mesh 對齊的優化程序產生高品質 3D 點流偽標註。
- **MPPI Sampling-Based MPC**:在推論時搭配預訓練 POINTWORLD 進行取樣式軌跡優化,以時間相關 cubic-spline 噪聲擾動末端執行器姿態,並依任務點目標成本選擇動作序列。
- **Aleatoric Uncertainty Head + Movement-Weighted Huber Loss**:作為訓練目標元件,以 movement weighting 聚焦稀疏動點監督,並以預測 log-variance 與 Huber 殘差正則化,抵抗真實資料中的偽標註雜訊。

### 2.4 Core Argument

作者主張現有世界模型在野外操作上之所以難以泛化,根本原因在於「狀態」與「動作」分屬不同模態的不一致表示:像素空間視訊模型缺乏顯式動作條件並難以保證物理一致性;傳統粒子或網格動力學模型則需要場景特定的物體性、材質或可觀測性先驗,難以跨化身、跨任務統一訓練;而以關節空間或末端執行器表示的動作又綁定於特定機器人形態,阻礙跨形態的資料聚合。為了讓世界模型像「下一個 token 預測」一樣能在大規模異質資料上進行單一目標的可規模化訓練,作者主張必須將狀態與動作放在同一個 3D 物理空間中,並以 3D 點流統一表達:場景由 RGB-D 反投影成部分可觀測的點雲,機器人動作則透過 URDF 與正向運動學轉成完整可觀測的點軌跡,如此一來模型只需學習「在 3D 幾何接觸下點如何位移」這個單一物理規律,即可隱式吸收物件分割、形狀補全、材質、重力與關節等知識。基於這個統一性,作者進一步論證:必須採用 chunked 多步預測以攤銷算力並維持時間一致性、加上以位移幅度為權重的 movement weighting 以對抗稀疏監督、並以 aleatoric 不確定度正則化處理偽標註的雜訊;最後透過約 2M 軌跡的大規模資料與 PTv3+DINOv3 backbone,讓單一檢查點以 0.1 秒推論延遲嵌入 MPPI MPC,即能在野外單張 RGB-D 觀測下完成多樣操作,從邏輯上閉合了「統一表示、規模化訓練、即時推論」三者的必要關係。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(280 words)

標題「PointWorld: Scaling 3D World Models for In-The-Wild Robotic Manipulation」直接揭示三個核心定位：(i) 這是一個 **3D world model** 而非 2D video model；(ii) 主軸是 **scaling**——把 3D 世界建模放上資料與模型規模的成長曲線；(iii) 應用標的是 **in-the-wild robotic manipulation**，意即不在實驗室條件、不靠特定示範資料的真實世界場景。

Abstract 以「人類能從一瞥與一個動作的設想，預期 3D 世界如何回應」這一動機開場，把 world modeling 定位成操作（manipulation）的核心能力。接著提出 PointWorld 的核心 framing：**state 與 action 共同表示為 3D point flows**——given 一張或數張 RGB-D 影像加上一段 low-level 機器人 action commands，模型輸出每個像素在 3D 空間中的位移軌跡。這個 framing 的關鍵是「以 3D point flows 取代 embodiment-specific action space (e.g., joint positions)」，因此可以同時 condition 在機器人實體幾何上、又能跨 embodiment 學習。

Abstract 的後半段轉向實作條件：作者整理了一個約 **2M trajectories、500 hours** 的資料集，跨 single-arm Franka 與 bimanual humanoid，涵蓋 real 與 simulated domain；並聲稱對 backbones、action representations、learning objectives、partial observability、data mixtures、domain transfers、scaling 都做了「rigorous, large-scale empirical studies」。最後給出兩個面向操作落地的具體承諾：**0.1s 的即時推論延遲**讓模型可塞進 MPC 框架；以及一個 single pre-trained checkpoint 在真實 Franka 上能執行 rigid pushing、deformable、articulated、tool-use 等任務，**無需 demonstration、無需 post-training、僅憑單張 in-the-wild RGB-D 影像**。

這段 abstract 同時設定 motivation、representation、dataset、empirical methodology 與 deployment 五條主軸，預告了論文後續的所有節結構。

### 3.2 Introduction

(380 words)

Introduction 的論述沿三個層次展開：問題、現有方法的缺口、以及作者提出的 unification 解法。

第一層把 world modeling 連到「spatial intelligence」這個更高目標：通用機器人必須能在非結構化環境裡預期世界如何演化，而人類從一瞥與一個 grasp 就能預測 deformation、articulation、stability、contact，作者用 Figure 3 說明這正是 3D action-conditioned 預測能涵蓋的能力面。

第二層回顧三類既有路線並指出各自的痛點：(i) **physics-based models** 預測準確但有 sim-to-real gap、需要場景特化建模；(ii) **learning-based dynamics models** 雖能從互動學習，但仰賴 domain-specific inductive bias，例如 full observability、objectness priors、material specification；(iii) **大型 video generative models** 視覺照真，但缺少 explicit action conditioning 並常違反物理一致性。作者明確點出：在「人類所能預期的」與「現行模型所能預測的」之間仍存在落差。

第三層提出 PointWorld 的中心哲學——**unification for scaling**：state 與 action 都用 3D 物理空間中的 point flows 表達。State 來自 RGB-D 重建的 full-scene point cloud；action 來自機器人本體的 dense 3D point trajectories（可由 URDF + forward kinematics 預生成）。在這個共同表示下，3D world modeling 簡化為「在 robot points 擾動下預測 full-scene 3D point flow」。作者強調這個表達同時捕捉 objectness、articulation、material properties，類比於 LLM 的 next-token prediction，但發生在 3D 空間與時間。

接著 introduction 預告兩個必需的支撐工程：(i) **資料**——他們從 DROID 與 BEHAVIOR-1K 構建跨 single-arm／bimanual／whole-body 的 real+sim 資料集，並利用近期 metric depth、camera pose、point tracking 的進展打造 markerless 3D 標註 pipeline；(ii) **設計原則的萃取**——對 backbone、action representation、objective、partial observability、data mixture、scaling、transfer 做系統研究。

最後段提出 deployment claim：在 0.1s 推論下與 MPPI 整合，single checkpoint 即可在實機 Franka 上完成 pushing、deformable、articulated、tool-use 等任務，無 demonstration 與 post-training。Contributions 三點 (model + recipe、dataset、real-robot demonstration) 為全文鋪設骨架，直接導向 §2 的 related work 對照。

### 3.3 Related Work / Preliminaries

(350 words)

§2 Related Work 將 PointWorld 放回三條既有研究脈絡，並用對比突出自身定位。

**World Modeling**。作者依 state-action 表達把領域切成幾類：video models（pixel-space state，光度重建或 joint-embedding 預測）；3D world models（meshes/explicit surfaces、radiance fields/Gaussians、particles）；以及 hybrid／hierarchical 結構。Action parameterization 也分了四種——joint-space、camera/navigation、textual prompts、2D cues——並提到下游動作生成可走 online planning、offline policy synthesis、inverse-dynamics 三條路徑。在這張地圖上，PointWorld 的差異化主張被一句話收斂：用 **3D point flow 作為共享 state-action 表示**，**強調 contact 與 geometry 而非 appearance**，**conditioning 在具體機器人/夾爪幾何上**，**能推理可見區之外**（與 2D cues 對比），且**在單一（或稀疏）RGB-D 與單次 real-time forward pass 內完成**。

**Dynamics Models in Robotics**。這段把 world model 落到機器人語境：physics-based simulators 與 learning-based models 是兩大支柱，下游應用涵蓋 policy learning、planning、model-based RL、exploration、safety filtering、design/verification、policy evaluation。作者批評既有 dynamics models 多半要 scene-specific modeling；自己的目標是 **pre-train 一個 single dynamics model** 跨 in-the-wild 場景泛化。他們指出，3D point flow 作為 state-action 空間能 **embodiment-agnostic** 地涵蓋 joint-space、end-effector、motion primitive 等先前作法，並且能在 partial RGB-D 上工作而不需 scene reconstruction、objectness/material priors。

**2D and 3D Flows for Manipulation**。第三條脈絡承接近年 point tracking 的進展，回顧 flows 在 policy learning、reward modeling、(sub-)goal 指定、visual servoing 中作為結構化介面的應用。這裡的關鍵 setup 是：作者**利用 depth、camera pose、point tracking 三項 3D 視覺進展**，從大型真實操作資料集 DROID 中抽出 3D scene flow（robot flow 由已知幾何、kinematics、proprioception 取得），讓 large 3D world model 可以 **以 stable regression loss 訓練**。

這三段共同把讀者帶到下一節：既然 representation 和監督都鋪好了，§3 就能直接進入 PointWorld 的 formulation。

### 3.4 Method (overview narrative)

(330 words)

§3 Method 將 3D world modeling 形式化為 action-conditioned full-scene 3D point flow prediction，並圍繞「state、action、prediction、objective、planning」五個關注點展開。

整體形式為 $F_\theta : \mathcal{S} \times \mathcal{A} \to \mathcal{S}$。作者刻意採 **chunked multi-step formulation**——一次 forward pass 預測 $H=10$ 步、每步 0.1s 的未來 state，理由是 temporal consistency 較佳且 amortize 計算。這一決策也正好對應到後續 §5 的 chunked vs. autoregressive ablation。

**State** 用 point flows 表示：每個 timestep 有 $N_S$ 個帶 3D 位置與時間恆定特徵的點，從 calibrated RGB-D 反投影、並以 forward kinematics 將 robot pixels 屏蔽掉。這個設計強調幾何而非外觀、容許 partial observability、不依賴 objectness 或 material 先驗，並可用 L2 loss 穩定訓練（不需 permutation matching）。**Action** 是 robot 自身的 3D point flows——以 URDF 與 joint configuration 序列做 forward kinematics 取出機器人表面點。這帶來兩個好處：行動是 **fully observable**（即便接觸發生在被遮擋的區域），且天然 embodiment-agnostic。實作上只在夾爪上 sample 數百點以平衡計算與接觸解析度。

**Dynamics prediction** 把初始 scene point cloud 與時間堆疊的 robot points 串成單一 point cloud，喂進 PTv3 backbone；scene 點以 frozen DINOv3（投影到 2D 視角）featurize，robot 點以 temporal embedding featurize；shared MLP head 一次輸出 $H$ 步的 per-point displacements。**Training objective** 為三項合計：movement weighting（用 ground-truth 位移過 sigmoid 得到 $w_{k,i}$，把訓練偏向實際在動的點）、aleatoric uncertainty regularization（預測 log-variance $s_{k,i}$ 同時抑制噪聲點）、以及 Huber loss 對 3D residual 提供 robustness（Equation 1）。Figure 4 視覺化說明這兩個權重分別捕捉「正在動的點」與「條件不確定的點」（如布邊）。

**用於操作（§3.2）**：PointWorld 整合進 MPPI 為核心的 sampling-based MPC——以 cubic-spline 噪聲擾動 nominal 軌跡、用模型 rollout、計算 cost、用指數加權更新 nominal。Cost 拆成 task cost（task-relevant 點到目標位置的 $\ell_2$）與 control regularization（path length、reachability），形成 Equation 2 的全軌跡優化。Method 章鋪好了 representation 與 inference loop，下一節就要回答：「資料從哪來？怎麼評估？」

### 3.5 Experiments (overview narrative)

(360 words)

實驗章（§5）以一條 **scaling roadmap** 為主軸，配合多組 controlled ablation 與 transfer 研究，最後落腳到實機 MPC，敘事節奏由小到大、由 component 到 system。

**§5.1 Scaling Roadmap（Figure 7）**。作者從 GBND baseline 出發，依序替換每個設計元件並量測 DROID 測試集上 moving 點的 $\ell_2$ 誤差。第一步把 backbone 從 GBND/PointNet 升級到 PTv3，因為 PTv3 的 point serialization + U-net hierarchy 能兼顧 local 結構與長程注意，且能 scale 到接近 GBND 的 $957\times$ 參數量而 memory/runtime 只是 modest 增長（Table 1）。第二步加入 movement weighting + uncertainty regularization + Huber loss 以穩定 noisy real-world 訓練。第三步引入 frozen DINOv3 多層特徵作為 2D pretrained prior。第四步把 PTv3 從 50M 推到 1B，得到大致 log-linear 的縮放收益（Figure 9）。

**§5.2 Ablations**。沿四個正交軸驗證 representation 設計：(i) **Action representation**——「夾爪 only point flows」勝過 whole-body flows 與 low-dim end-effector/joint baselines，並能在 DROID + B1K 跨 embodiment 取得正向轉移（Figure 11）；(ii) **Chunked prediction**——chunk-train + chunk-test 比 autoregressive teacher-forcing/self-feeding 漂移更小、計算更省（Figure 12）；(iii) **Partial observability**——隨機相機數訓練最 robust，多相機在訓練與推論都帶來增益（Figure 13）；(iv) **Scaling laws**——model size 與 data fraction 各自呈大致 log-linear 趨勢（Figure 9）。

**§5.3 Generalization**。在 in-domain（D→D, B→B）、cross-domain（D→B, B→D）、held-out real（D→H, B→H, D+B→H）下評估 zero-shot 與 finetuned 行為（Table 2）。結論是：模型在域內穩定泛化、不只是記憶；real↔sim cross-domain zero-shot 仍有 gap 但 finetune 1/20 步即可逼近；對 held-out lab 場景，pretrained 模型 zero-shot 已與 specialist 持平，finetune 後超越，並從 real+sim 共訓練得到輕微增益。

**§5.4 Real-world MPC（Figure 8）**。Franka + 單 RealSense D435 + FoundationStereo 深度，由 GUI 指定 task-relevant 點與目標。同一個 pretrained checkpoint 跑出 rigid pushing（tissue box 70%、book 20%）、deformable（scarf 80%、pillow 40%）、articulated（microwave 30%、drawer 90%）、tool-use（duster 60%、broom 60%）等八項任務的非零成功率。這把 abstract 中的承諾落地：single image、no demos、no finetune。下一節因此可以把全篇收束到 take-aways。

### 3.6 Conclusion / Limitations / Future Work

(120 words)

§6 Conclusion 簡短而直接：作者把 PointWorld 重新定位為「一個大型 pre-trained 3D world model，在 in-the-wild RGB-D 與 robot actions 之上以 3D point flows 的共享表示來預測 3D 環境動態」。論文總結了三條已經在 §3–§5 鋪陳的成果——leveraging 近期 3D vision 進展所建立的高品質 depth／camera pose／3D track 大規模資料集、針對 backbone designs／action representations／learning objectives／partial observability／data mixtures／domain transfers／scaling laws 的 empirical recipe，以及單一 pretrained checkpoint 即可支援 non-prehensile pushing、deformable、articulated、tool use 的真實機器人行為。

值得注意的是：**論文正文的 conclusion 段並未顯式列出 limitations 或 future work**——the paper does not specify 任何明確的 limitation 條目或後續方向計畫，僅在 acknowledgments 之前以正面口吻收束。讀者若需 limitations，需要從 §5 的失敗模式（例如某些任務的低成功率、real↔sim zero-shot gap、real-world 標註的 reprojection loss 殘餘）中推斷，作者本身未在 §6 中提出。

## 4. Critical Profile

### 4.1 Highlights

- 提出將 state 與 action 統一表示為 3D point flow 的單一表徵,使單一回歸目標即能同時學習物件性、形狀補全、關節結構、材質與重力等多重知識(p.4 Figure 3)。
- 整理約 2M 條軌跡、500 小時的真實 + 模擬資料集,涵蓋單臂 Franka、雙臂 humanoid、全身與行動操作,作者宣稱為目前最大的 3D dynamics modeling 資料集(p.6 §4)。
- 自建三階段 3D 標註管線(FoundationStereo depth + VGGT 初始化後對 robot mesh 對齊優化的 extrinsics + CoTracker3 2D-to-3D point tracking),於 DROID 上將 depth reprojection loss $\le 0.10$ 的場景數從原始 V1/V2 release 大幅拉升,並回收超過 60% 的 DROID 資料(p.6 Figure 5、p.8 §4)。
- 系統性 backbone roadmap 顯示從 GBND baseline 的 $\ell_2 = 0.0386$ 一路改進至最終 PTv3-1B 配方的 $\ell_2 = 0.0312$,呈現可重現的設計遞進(p.8 Figure 7)。
- PTv3-1B 在 957× GBND 參數量下,latency 僅約 $0.12\text{s}$,而 GBND 為 $13.46\text{ms}$ 級別但無法 scale,證明 PTv3 的記憶體與運算效率適合大規模 3D 世界模型(p.9 Table 1)。
- 模型大小 50M $\to$ 1B 與資料量 5%–100% 兩軸均呈現近 log-linear 的 prediction error 改進,符合 vision/language scaling law 預期(p.9 Figure 9)。
- 用 chunked prediction($H=10$, $0.1\text{s/step}$)取代 autoregressive rollout,在訓練/推論策略一致下顯著降低 drift,同時將 1 秒 horizon 的算力攤銷成單次 forward pass(p.10 Figure 12)。
- Movement weighting + aleatoric uncertainty + Huber 三項 objective 設計共同解決 1–5% 移動點稀疏監督與真實資料雜訊問題,且 uncertainty head 額外湧現出對物理屬性(如布邊緣變異大)的條件式不確定度建模(p.5 Figure 4、p.9 §5.1)。
- 單一預訓練 checkpoint 在實體 Franka 上以單張 in-the-wild RGB-D 完成 8 項 zero-shot 任務,涵蓋 rigid pushing、deformable、articulated 與 tool use,例如 drawer 90%、scarf 80%、tissue box 70%(p.11 Figure 8)。
- 隨機相機數訓練的 variant 在所有測試 camera count 下都最 robust,顯示 partial observability 可被 data augmentation 有效吸收(p.10 Figure 13)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者明確指出 sim 與 real 之間的 zero-shot transfer「remains challenging」,需 finetune 才能縮小差距,且 sim-only 預訓練在 held-out real 上並未超過 from-scratch baseline(p.11 §5.3)。
- 作者承認 real-world data 雜訊大,naïve $\ell_2$ loss 難以最佳化,僅 1–5% 的點實際在動,需多項 objective 組合才能穩定訓練(p.4 §3.1、p.9 §5.1)。
- 作者承認大多數 robot surface points 從不與場景接觸,因此實作上僅取 grippers(每 gripper 數百點)而非 full body,屬於效率折衷而非原始公式(p.4 §3.1 Action Representation)。
- 作者主動說明因 horizon 僅 1 秒,$\ell_2$ 絕對差距會看起來很小,並引述 [125] 表示 task-level success rate 常無法揭露 rollout fidelity 的差異,間接承認 $\ell_2$ 與下游任務之間有解讀落差(p.8 §4 Interpretation of the Metric)。

#### 4.2.2 Phyra-inferred

- 實機成功率變異極大:Book 20%、Microwave 30%、Pillow 40% 都低於 50%,但論文以平均的 zero-shot 成功敘事呈現,並未提供 trial 次數或失敗模式分類,難以判斷統計顯著性(p.11 Figure 8)。
- 評測集採「expert-filtered」處理,先以僅在 held-out test 上訓練的 expert model 透過 uncertainty objective 過濾掉 20% 點,這與訓練 objective 同源,可能讓 PTv3-based 模型在自家偏好下被高估,而 baseline 受罰(p.8 §4 Model Evaluation Protocol)。
- Held-out real 的 zero-shot 數字顯示 D$\to$H $\ell_2 = 0.0305$、D+B$\to$H = 0.0300,僅略好於 from-scratch specialist 的 0.0293,代表大規模預訓練在未見場景上的「on-par」其實是「打平」,論文以正面措辭包裝(p.10 Table 2)。
- D$\to$B 的 cross-domain $\ell_2 = 0.1460$,是 in-domain B$\to$B 的 0.0087 的近 17 倍,但內文僅以「remains challenging」一語帶過,未量化 sim-to-real gap 的工程後果(p.10 Table 2)。
- Chunked vs. autoregressive 的比較不對等:chunk 模型只用 chunk loss 訓、AR 模型用 AR loss 訓,沒有 dual-objective baseline,W=5 sliding-window 在第 5 步後崩壞可能是訓練分布外推的人為產物,而非 chunked 設計的本質優勢(p.10 Figure 12)。
- 真實 robot 部署需要使用者透過 GUI 手繪 object mask 並指定 target positions,「from a single image without demonstrations」的敘事掩蓋了每個任務仍需的人為任務規格化成本(p.11 §5.4)。
- 跨化身宣稱僅在資料層面成立:bimanual humanoid 與 mobile manipulation 僅在 BEHAVIOR-1K 模擬中評測,所有實機驗證都在 Franka 上,未證明點流表徵真能跨硬體泛化到 humanoid 實機(p.11 §5.4)。
- DINOv3 features 透過將 3D 點投影回 2D camera 取得,但對於透過 forward kinematics 推得的「imagined」occluded 區域(如 box 後方),這些點理論上沒有對應的 2D 像素,論文未說明特徵如何補完(p.4 Dynamics Prediction、p.9 §5.1)。
- MPPI 推論時 K 個 candidate trajectory 的 batched forward pass 真實 latency 未報告;0.1s 是單次 forward pass,但 sampling-based MPC 通常需數十至數百 sample 才收斂,實際控制頻率被刻意模糊(p.5 §3.2、p.9 Table 1)。
- Camera count ablation 中各條件差距均在 sub-cm 量級,Figure 13 雖宣稱 standard error 可忽略,但作者未提供誤差條,「robust to partial observability」的結論在缺少統計檢定下偏弱(p.10 Figure 13)。

### 4.3 Phyra's Judgment (summary)

真正有原創性的是「以 3D point flow 同時表達 state 與 action」這個建模選擇,以及為了餵養它而打造的 DROID 重新標註管線,後者本身就是一份可獨立發表的工程貢獻。其餘關鍵元件 PTv3、DINOv3、chunked prediction、Huber、aleatoric uncertainty 都是既有配方的組合,scaling roadmap 雖然嚴謹但屬於工程驗證而非演算法突破。核心未解問題是:近 log-linear 的 $\ell_2$ 改進是否真能轉化為穩定的下游操作能力,目前 8 項實機任務中半數成功率低於 50%,加上 cross-domain $\ell_2$ 落差約 17×,顯示「統一表徵 + 規模化」距離承諾的「general world model for in-the-wild manipulation」仍有相當距離。

## 5. Methodology Deep Dive

### 5.1 Method Overview

POINTWORLD 將 3D world modeling 形式化為「action-conditioned full-scene 3D point flow prediction」:給定當前場景狀態 $s_t$ 與一段機器人動作序列 $a_{t:t+H-1}$,模型 $F^H_\theta$ 在「單次前向推論」中同時輸出未來 $H$ 個時間步的場景狀態 $s_{t+1:t+H}$。作者刻意採用 chunked(分段)多步預測而非單步遞迴 $s_{t+1} = F_\theta(s_t, a_t)$,以「攤銷算力」並維持時間一致性;預設 $H=10$,每步 0.1 秒,因此一次前向覆蓋 1 秒的物理動態,搭配 PTv3-1B 的 0.1 秒推論延遲,可在取樣式 MPC 中即時評估大量候選軌跡。

狀態與動作均以 3D 點流統一表示。場景狀態 $s_t = \{(p_{t,i}, f^S_i)\}_{i=1}^{N_S}$ 由一張或數張校準後的 RGB-D 透過 forward kinematics(FK)+ URDF 遮罩機器人像素後反投影得到,每點具有位置 $p_{t,i} \in \mathbb{R}^3$ 與時間恆定特徵 $f^S_i \in \mathbb{R}^{D_S}$;動作 $a_{t+k} = \{(r_{t+k,j}, f^R_{t+k,j})\}_{j=1}^{N_R}$ 則在時間 $t$ 一次性對機器人 surface 採樣,attach 到對應 link 後以 FK 沿動作序列向前推進,其中 $r_{t+k,j} \in \mathbb{R}^3$、$f^R_{t+k,j} \in \mathbb{R}^{D_R}$ 為時變特徵。實作上僅在 grippers 上採樣 300–500 點以聚焦接觸推理。將初始場景點與時間堆疊的機器人點 concatenate 成單一點雲交付 backbone,即為 embodiment-agnostic 的 interaction geometry 表示。

骨幹採用 Point Transformer v3(PTv3),場景點以「凍結 DINOv3」投影到 2D 視角後採樣多層特徵,機器人點則以 temporal embedding 標記其時間索引;PTv3 的 point serialization 與 U-net 階層使其在保持與 GBND baseline 相近記憶體與延遲的前提下放大到 957× 參數量。輸出階段一個共享 MLP head 對「場景點」逐點預測 $H$ 步位移與 aleatoric log-variance $s_{k,i}$。訓練目標結合三項設計來對抗 full-scene 預測的稀疏監督與偽標註雜訊:movement weighting $w_{k,i}$(以位移幅度作為權重)、aleatoric uncertainty regularization(以 $e^{-s_{k,i}}$ 加權殘差並懲罰過大 $s_{k,i}$)、以及 Huber loss $\rho_\delta$ 作為 robust regression。推論時將模型嵌入 MPPI:對 end-effector 軌跡採 cubic-spline 噪聲擾動產生 $K$ 條候選,每條經 FK 轉為 robot point flows 餵入 POINTWORLD 取得 rollout,以任務點 $I_{\text{task}}$ 的 L2 cost 與控制正則項計分,再以 $\omega_\ell \propto \exp(-J^{(\ell)}/\beta)$ 做加權更新標稱軌跡。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input
├─ RGB-D Observation                                 [B, V, 4, H_img, W_img]   (V ∈ {1,2,3})
│   └─ Mask robot pixels via URDF + FK
│       └─ Back-project (camera intrinsics/extrinsics)
│           └─ Grid downsample @ 1.5 cm
│               └─ Scene points  p_{t,i}             [B, N_S, 3]
│                   └─ Project to 2D views, sample frozen DINOv3 multi-layer feats
│                       └─ Scene features  f^S       [B, N_S, D_S]            (D_S = ?, DINOv3 ViT-L multi-layer)
│
├─ Joint configurations  {q_{t+k}}_{k=0}^{H}         [B, H+1, J]              (J = num joints)
│   └─ Sample robot surface points at t (grippers only, 300–500 pts/gripper)
│       └─ Attach to links; propagate via FK
│           └─ Robot point positions  r_{t+k,j}      [B, H, N_R, 3]
│               └─ Temporal embedding (time index k)
│                   └─ Robot features  f^R           [B, H, N_R, D_R]         (D_R = ?)
│
└─ Concatenate scene points with time-stacked robot points
        Combined positions                            [B, N_S + H·N_R, 3]
        Combined features                             [B, N_S + H·N_R, D_in]   (D_in mixes D_S, D_R, type embed)
        │
        └─ Point Cloud Backbone: PTv3 (U-net w/ serialized attention)
            ├─ Sizes evaluated: 50 M / 132 M / 411 M / 1 B params
            └─ Per-point features                     [B, N_S + H·N_R, d]      (d = ?, hidden dim)
                │
                └─ Take scene-point slice only        [B, N_S, d]
                    └─ Shared MLP head (predicts all H steps in one pass)
                        ├─ Predicted displacements Δ̂  [B, H, N_S, 3]
                        │   └─ P̂_{t+k,i} = p_{t,i} + Δ̂_{k,i}
                        └─ Log-variance  s_{k,i}      [B, H, N_S, 1]
                            │
                            └─ Training:  movement weight w_{k,i} · Huber(P̂ − P) · e^{−s} + s
                            │
                            └─ Inference (MPPI):  K cubic-spline EE perturbations
                                │   → K robot flow rollouts → cost J^{(ℓ)}
                                │   → ω_ℓ ∝ exp(−J^{(ℓ)}/β)
                                └─ Updated nominal EE trajectory             [B, T, SE(3)]
```

未指明的維度(`D_S`、`D_R`、`d`、以及 `D_in` 內部組態與 DINOv3 取用的層數)在 §5.3 對應模組的「Implementation Details」中標註為 the paper does not specify。

### 5.3 Per-Module Breakdown

#### 5.3.1 Scene Point Construction

**Function:** 將校準後的 RGB-D 觀測轉成部分可觀測、機器人像素已遮罩的場景點雲,作為世界模型的初始狀態 $s_t$。

**Input:**
- Name: RGB-D images + camera intrinsics/extrinsics + current joint config $q_t$ + URDF
- Shape: `[B, V, 4, H_img, W_img]` 影像張量 + `[B, V, 3, 4]` 外參 + `[B, J]` 關節
- Source: 真實實驗為 RealSense D435 + FoundationStereo 估計深度;訓練資料則為 DROID 經 FoundationStereo + 優化外參處理後的標註

**Output:**
- Name: scene points $\{(p_{t,i}, f^S_i)\}_{i=1}^{N_S}$(僅幾何位置,特徵在 §5.3.3 注入)
- Shape: positions `[B, N_S, 3]`
- Consumer: §5.3.3 DINOv3 featurization;隨後與機器人點 concatenate 進 §5.3.4 PTv3

**Processing:**

1. 以當前 $q_t$ 與 URDF 跑 FK,將機器人 surface mesh 投影到每個視角,得到 robot pixel mask。
2. 將非機器人像素以相機內外參反投影到 robot base frame 得到 3D 點。
3. 對所有點做 1.5 cm grid downsampling(論文於 §4 的 evaluation 與 visualization 段落明示;訓練時亦使用以控制 $N_S$)。
4. 點數 $N_S$ 在不同 forward pass 之間「可變」,且不需要 point tracker(對應關係只在模型 forward 內部維持)。

**Key Formulas:**

$$
p_{t,i} = K^{-1} \cdot d(u_i, v_i) \cdot [u_i, v_i, 1]^\top,\quad (u_i, v_i) \notin \text{RobotMask}(q_t, \text{URDF})
$$

**Implementation Details:**

- 真實機器人推論使用 1 顆 RealSense D435,深度由 FoundationStereo 重新估計;訓練資料的 DROID 部分使用 FoundationStereo 深度 + VGGT 初始化後再以 robot-depth alignment 優化的外參(報告中位數平移誤差 1.8 cm、旋轉 1.9 度)。
- $N_S$ 數值上界由 1.5 cm grid downsample 決定;具體 $N_S$ 範圍 the paper does not specify。

#### 5.3.2 Robot Point Flow Generation

**Function:** 將 embodiment-specific 的 joint-space 動作序列轉成 embodiment-agnostic 的 3D 點軌跡,作為世界模型的條件動作。

**Input:**
- Name: joint configuration sequence $\{q_{t+k}\}_{k=0}^{H}$ + URDF
- Shape: `[B, H+1, J]`
- Source: 訓練時來自 teleoperation log;推論時來自 MPPI 採樣的 EE 軌跡經 IK 反算

**Output:**
- Name: robot point flows $a_{t:t+H-1} = \{(r_{t+k,j}, f^R_{t+k,j})\}$
- Shape: positions `[B, H, N_R, 3]`
- Consumer: §5.3.3 temporal embedding;之後與場景點 concatenate

**Processing:**

1. 在時間 $t$ 對機器人 surface 採樣一次 $N_R$ 點,將每點 attach 到所屬 link。
2. 對 $k = 0, \dots, H-1$,以 $q_{t+k}$ 經 FK 將每個 link 的固定點推進到世界座標,得到 $r_{t+k,j}$。
3. 為避免大量 inactive 點稀釋學習信號並節省算力,「僅在 grippers 上採樣」,每個 gripper 採 300–500 點(由 gripper 幾何複雜度決定)。

**Key Formulas:**

$$
r_{t+k,j} = T^{\text{world}}_{\text{link}(j)}(q_{t+k}) \cdot r^{\text{local}}_j
$$

**Implementation Details:**

- DROID 為單臂 Franka(1 個 gripper,300–500 點);BEHAVIOR-1K 為雙臂 humanoid(2 個 gripper)。
- ablation 中對照組「whole-body 2000 點」、「whole-body 500 點」、「6-DoF EE pose + gripper openness」、「joint pos + gripper openness」均落後 gripper-only flows(Figure 11)。

#### 5.3.3 Feature Encoding (DINOv3 + Temporal Embedding)

**Function:** 對場景點注入語義先驗,對機器人點注入時間索引,使 PTv3 能從統一的點集區分兩類來源並做 chunked 預測。

**Input:**
- Scene positions `[B, N_S, 3]`、相機內外參、原始 RGB
- Robot positions `[B, H, N_R, 3]`、時間索引 $k \in \{0, \dots, H-1\}$

**Output:**
- Scene features $f^S_i$ `[B, N_S, D_S]`(time-constant)
- Robot features $f^R_{t+k,j}$ `[B, H, N_R, D_R]`(time-varying)
- Consumer: §5.3.4 PTv3 backbone

**Processing:**

1. 將每個 scene point 投影到所有 calibrated camera 的影像座標。
2. 從凍結 DINOv3(ablation 顯示 ViT-L > ViT-S,multi-layer > 單層)取出對應位置的多層 patch features。
3. 多視角特徵聚合(平均或可見性加權,the paper does not specify 確切聚合方式)後成為 $f^S_i$。
4. 對 robot points,將時間步索引 $k$ 編碼為 temporal embedding 並逐點 broadcast 到 $N_R$ 個點。
5. 額外注入點類型 embedding(scene vs. robot)以利 backbone 區分。

**Key Formulas:**

$$
f^S_i = \text{Aggregate}_v\left( \text{DINOv3}_{\text{multi-layer}}\big(\text{RGB}_v\big)[\pi_v(p_{t,i})] \right)
$$

**Implementation Details:**

- DINOv3 全程 frozen,僅作為 feature extractor。
- $D_S$、$D_R$ 數值的 paper does not specify;Roadmap(Figure 7)顯示由 DINOv2 ViT-S → ViT-L → DINOv3 ViT-L → multi-layer 漸進帶來連續 $\ell_2$ 下降。

#### 5.3.4 Point Cloud Backbone (PTv3)

**Function:** 在 concatenated 點雲上做長距離 attention,輸出每個輸入點的高維特徵以供下游 head 解碼動態。

**Input:**
- Combined positions `[B, N_S + H·N_R, 3]`
- Combined features `[B, N_S + H·N_R, D_in]`(scene/robot feat + 點類型 embedding)
- Source: §5.3.1 + §5.3.2 + §5.3.3

**Output:**
- Per-point features `[B, N_S + H·N_R, d]`
- Consumer: §5.3.5 displacement head(僅取場景點切片)

**Processing:**

1. PTv3 以 point serialization 將點轉為序列(模擬 GBND 的局部 grouping)。
2. U-net 階層在逐步 coarser 的點集上做 attention,實現長距離傳播。
3. 解碼回原始解析度,輸出每點 $d$ 維特徵。

**Key Formulas:**

PTv3 內部結構引用自 [152],本論文未給出新方程。

**Implementation Details:**

- 評估規模:50M / 132M / 411M / 1B 參數;Table 1 顯示 PTv3-1B 達 GBND 957× 參數,但記憶體僅 4.30×、FLOPs 3.57×、推論延遲 123.65 ms(論文宣稱 ≈ 0.12 s)。
- 預設 $H = 10$、每步 0.1 s;hidden dim $d$ 與各層 channel 設定 the paper does not specify(僅以總參數量描述)。
- Ablation 顯示 PTv3 顯著優於 PointNet / PointNet++ / SparseConv / Transformer,主要受益於 serialization + 階層化 attention。

#### 5.3.5 Displacement Head and Training Objective

**Function:** 從場景點特徵預測 $H$ 步 3D 位移與 aleatoric log-variance,並以三重設計穩定訓練。

**Input:**
- Scene-point features 切片 `[B, N_S, d]`(從 §5.3.4 輸出抽出 scene 對應位置)
- Source: §5.3.4 PTv3

**Output:**
- Predicted displacements $\hat{\Delta}_{k,i}$ → predicted positions $\hat{P}_{t+k,i}$ `[B, H, N_S, 3]`
- Log-variance $s_{k,i}$ `[B, H, N_S, 1]`
- Consumer: §5.3.6 MPPI rollout(推論);訓練 loss(訓練)

**Processing:**

1. 共享 MLP head 對每個 scene point 一次性回歸 $H$ 個時間步的位移與 log-variance。
2. 訓練時以 ground-truth 位移幅度 $\delta_{k,i}$ 計算 movement likelihood $m_{k,i}$ 並正規化為 $w_{k,i}$,聚焦在實際移動的點。
3. 殘差以 Huber loss $\rho_\delta$ 取代純 L2,降低偽標註離群點影響。
4. 以預測的 $s_{k,i}$ 對殘差做 $e^{-s_{k,i}}$ 加權,再加 $s_{k,i}$ 自身正則,構成 aleatoric uncertainty regularization。
5. 由 2D tracker 標記為「不可見」的點不參與 supervision。

**Key Formulas:**

$$
m_{k,i} = \sigma\big(\kappa(\delta_{k,i} - \tau)\big),\quad w_{k,i} = \frac{m_{k,i}}{\sum_{k,i} m_{k,i}}
$$

$$
\mathcal{L} = \frac{1}{2} \sum_{k,i}^{H, N_S} w_{k,i} \left[ \rho_\delta\!\left(\hat{P}_{t+k,i} - P_{t+k,i}\right) e^{-s_{k,i}} + s_{k,i} \right]
$$

**Implementation Details:**

- $\tau$、$\kappa$、Huber 閾值 $\delta$ 的具體數值 the paper does not specify。
- 評估時,「mover」類別由相同的 movement likelihood 過濾;real-world test set 另以一個只在 held-out test split 上訓練的 expert model 預測 uncertainty,保留 confidence 最高的 80% 點作為去噪後的評估集。

#### 5.3.6 MPPI-Based Action Inference

**Function:** 在推論時,以 POINTWORLD 作為動態模擬器,結合取樣式 MPC 求解 end-effector 軌跡,完成真實機器人零示範操作。

**Input:**
- 初始 $s_0$(從單張 RGB-D 構造)
- 任務點集合 $I_{\text{task}} \subseteq \{1, \dots, N_S\}$ 與目標位置 $\{g_i\}_{i \in I_{\text{task}}}$(GUI 或 VLM 指定)
- 當前 $E_{\text{measured}}$、控制正則項 $c_{\text{ctrl}}$

**Output:**
- 優化後的 EE 軌跡 $E_{0:T}$ `[B, T+1, SE(3)]`,送至下層控制器執行
- 真實實驗每次 optimization rolls out 30 步(3 次 autoregressive forward pass)

**Processing:**

1. 對標稱 EE 軌跡採 $K$ 條 cubic-spline(time-correlated)噪聲擾動 $\ell_{1:K}$。
2. 對每條 $E^{(\ell)}_{1:T}$ 經 IK + §5.3.2 流程轉為 robot point-flow $a^{(\ell)}_{1:T}$。
3. 以 POINTWORLD 在 $a^{(\ell)}_{1:T}$ 條件下 rollout 場景動態,得到 $s^{(\ell)}_{1:T}$。
4. 累加軌跡 cost $J^{(\ell)} = \sum_k\!\left[c_{\text{task}}(s_k) + c_{\text{ctrl}}(E_k)\right]$。
5. 以 $\omega_\ell \propto \exp(-J^{(\ell)}/\beta)$ 加權更新標稱軌跡,迭代收斂後取出。

**Key Formulas:**

$$
c_{\text{task}}(s_k) = \frac{1}{|I_{\text{task}}|} \sum_{i \in I_{\text{task}}} \big\| p_{k,i} - g_i \big\|_2^2
$$

$$
\arg\min_{E_{0:T}} \sum_{k=1}^{T} \!\left[ c_{\text{task}}(s_k) + c_{\text{ctrl}}(E_k) \right]\quad \text{s.t.}\quad s_{1:T} = F^T_\theta(s_0, a_{1:T}),\ E_0 = E_{\text{measured}}
$$

**Implementation Details:**

- 推論延遲 0.1 s/forward 使得在每次 MPPI 迭代中可批次評估大量 $K$ 條候選。
- 任務涵蓋 rigid pushing(tissue box / book)、deformable(scarf / pillow)、articulated(microwave / drawer)、tool use(duster / broom);成功率分別介於 20–90%(Figure 8)。
- $K$、$\beta$、$T$、cubic-spline 節點數、$c_{\text{ctrl}}$ 具體形式 the paper does not specify(註明 Further details in Appendix)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| DROID [7] | 真實世界 single-arm Franka 操作（in-the-wild scenes） | 約 200 小時、>60% 原始資料經 3D 標註後保留 | train/val/test 切分；§5.3 額外切出 CLVR lab 作為 held-out 真實環境（90% finetune、10% test） |
| BEHAVIOR-1K (B1K) [8] | 模擬中 bimanual／whole-body／mobile manipulation（photorealistic 家庭環境） | 過濾前約 1100 小時 teleoperation；過濾後保留含 active contact 與物體位移的 trajectory | train/val/test 切分；論文未明確指出比例 |
| 合計 (DROID + B1K) | 跨真實／模擬之 3D 動力學建模 | 約 2M trajectories、約 500 小時 | 用於 pre-training POINTWORLD |
| 真實機器人部署集合（§5.4） | 8 項真實任務：tissue box、book、scarf、pillow、microwave、drawer、duster、broom | 每任務多次 trial（單一 RealSense D435、Franka on wheeled base） | 僅作 zero-shot 評測，不參與訓練；無 demonstrations、無 finetuning |

備註：DROID 的 3D 標註並非原資料集自帶，而是由作者以 FoundationStereo [9] + 自訂 extrinsics 優化 + CoTracker3 [11] 的 pipeline 重新產生（§4）。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| $\ell_2$ mover | 在 ground-truth 判定為「移動點」的子集上，逐點逐時間步的 3D 位置 $\ell_2$ 誤差，視窗為 1 秒（10 步）；真實資料另以一個僅在 test split 訓練的 expert model 過濾不可靠點，僅保留 model confidence 前 80% 的點 | yes |
| $\ell_2$ static | 在「靜態點」子集上的逐點 $\ell_2$ 誤差；用以檢查模型不會誤動不該動的點 | no |
| Real-world success rate | §5.4 中 8 項真實任務的成功率（每任務分別報告） | no（次要，但為「能用於下游 manipulation」的關鍵證據） |
| Compute metrics（Params / Memory / FLOPs / Latency） | Table 1 用於 backbone 比較；latency 以 ms 計，PTv3-1B 約 0.12 s | no（用於效率論證） |

注意：論文指出在約 40,000 條 trajectory、每條 10,000 點的評測規模下，$\ell_2$ 標準誤 $\le 10^{-5}\,\text{m}$，因此僅報告 mean。

### 6.3 Training and Inference Settings

- **預測視窗與步長**：chunked prediction，$H = 10$ 步、每步 0.1 s（總 1 秒），單次 forward pass 同時預測 10 步。
- **Backbone**：以 PTv3 [152] 為預設，掃描 50M / 132M / 411M / 1B 四個尺寸；scene point 用 frozen DINOv3 ViT-L 多層特徵投影獲得，robot point 用 temporal embedding。
- **訓練目標**：weighted Huber loss + aleatoric uncertainty regularization（公式 1），movement weight 由 ground-truth displacement 經 $m_{k,i} = \sigma(\kappa(\delta_{k,i} - \tau))$ 算出後 normalize；CoTracker3 標記為不可見的點不計入 loss。
- **資料稀疏性處理**：grid downsampling 1.5 cm（visualization 上以 nearest neighbors upsample 回 image resolution）。
- **MPC 推論（§5.4）**：sampling-based MPPI [12]，在 SE(3) 上規劃 $T$ 步 end-effector pose；時間相關的 cubic-spline noise，$K$ 個 trajectory 樣本，cost 為 task cost（$\frac{1}{|I_{\text{task}}|}\sum_{i \in I_{\text{task}}} \|p_{k,i} - g_i\|_2^2$）加 control regularization；每次優化 rollout 30 步（即 3 次 autoregressive forward pass）。深度由 FoundationStereo 估計，object mask 與 target 由 GUI 人工指定。
- **Finetune 預算（§5.3）**：每次 finetune 僅用原訓練步數的 1/20（即 5%）。
- **未明確項目**：硬體（GPU 型號／數量）、global batch size、optimizer、learning rate schedule、總訓練步數、warmup、$\tau$ / $\kappa$ / Huber $\delta$ / MPPI 的 $K, T, \beta$ 具體數值，主文均未指明，論文表示細節置於 Appendix（本任務僅取得實驗主文與部分 Appendix，未涵蓋這些超參數頁）。

### 6.4 Main Results

實驗以 $\ell_2$ mover（公尺、越低越好）為主指標，分兩類展示：(a) 從 GBND baseline 升級到 POINTWORLD 的 roadmap（DROID test set，Figure 7 / Table 1 對應的 backbone 部分）；(b) 真實機器人 zero-shot success rate（Figure 8）。

| Method | $\ell_2$ mover ↓ | $\ell_2$ static ↓ | Notes |
|---|---|---|---|
| GBND baseline [5]（roadmap 起點） | 0.0390 | 0.0066 | Table 1；relational inductive bias 但 memory 與 long-range 不易擴展 |
| PointNet [161] | 0.0369 | 0.0084 | |
| PointNet++ [162] | 0.0368 | 0.0073 | |
| SparseConv [163] | 0.0396 | 0.0076 | 參數量 33×GBND 但效果未提升 |
| Transformer [164] | 0.0339 | 0.0071 | |
| PTv3-50M | 0.0331 | 0.0067 | |
| PTv3-132M | 0.0324 | 0.0061 | |
| PTv3-411M | 0.0315 | 0.0059 | |
| **PTv3-1B（POINTWORLD final）** | **0.0312** | **0.0056** | 約 957× GBND 參數量、latency 約 0.12 s |

Roadmap 累積增益（Figure 7，DROID test $\ell_2$ mover）：GBND baseline 0.0386 → 加 Huber 0.0370 → +movement weighting 0.0348 → +uncertainty 0.0348（持平但更穩定）→ DINOv2 ViT-S 0.0350 → DINOv2 ViT-L 0.0342 → DINOv3 ViT-L 0.0335 → multi-layer 0.0332 → 50M 0.0334 → 132M 0.0331 → 411M 0.0324 → 1B 0.0315 → Sonata 預訓 + 全配方 0.0312。

真實機器人 success rate（§5.4，Figure 8，皆為 zero-shot、單張 in-the-wild RGB-D、無 demonstrations 或 post-training）：

| Task | Type | Success Rate |
|---|---|---|
| Tissue Box | rigid pushing | 70% |
| Book | rigid pushing | 20% |
| Scarf | deformable | 80% |
| Pillow | deformable | 40% |
| Microwave | articulated (revolute) | 30% |
| Drawer | articulated (prismatic) | 90% |
| Duster | tool use | 60% |
| Broom | tool use | 60% |

Generalization（Table 2，$\ell_2$ mover ↓）：

| Setting | Zero-Shot | Finetuned (1/20 updates) |
|---|---|---|
| D→D（in-domain real） | 0.0315 | – |
| B→B（in-domain sim） | 0.0087 | – |
| D→B（real→sim） | 0.1460 | 0.0107 |
| B→D（sim→real） | 0.0558 | 0.0378 |
| D→H（held-out real） | 0.0305 | 0.0271 |
| B→H | 0.0531 | 0.0299 |
| D+B→H | 0.0300 | 0.0272 |
| From-Scratch specialist on H | 0.0293 | – |

關鍵觀察：D→H zero-shot（0.0305）已逼近 from-scratch specialist（0.0293），finetune 後的 D+B→H（0.0272）反超 specialist；real→sim 的 zero-shot 落差很大（0.1460）但 finetune 後迅速拉近（0.0107）。

### 6.5 Ablation Studies

1. **Backbone**（Table 1）— 移除 PTv3，改換 GBND / PointNet / PointNet++ / SparseConv / Transformer。$\ell_2$ mover 從 0.0312（PTv3-1B）升至 0.0339（Transformer）至 0.0396（SparseConv）；同時 PTv3 在記憶體與 latency 上仍可控（PTv3-1B latency 約 0.12 s vs Transformer 30.43 ms 但精度劣於 PTv3-50M）。**屬診斷型**：同時揭示「relational inductive bias 在 partial observability 下不足」「local message passing 難以長程建模」兩個機制性結論，不只是規模對比。

2. **Training objective**（Figure 7）— 逐項加入 Huber、movement weighting、uncertainty regularization。單獨 movement weighting 會放大 noise，須與 uncertainty head + Huber 同用才穩定；最終配方對比純 $\ell_2$ baseline 在 DROID test 從 0.0386 → 0.0348 / 0.0348 / 0.0332。**屬診斷型**：作者特別指出真實資料只有 1–5% 點在動，因此這組 ablation 對應「為何天真 $\ell_2$ 不可用」的實際病灶。

3. **Pre-trained 2D features**（Figure 7）— DINOv2 ViT-S / ViT-L / DINOv3 ViT-L / multi-layer 比較。從 0.0350 一路降到 0.0332。**屬診斷型偏小**：證明 frozen 2D feature 重要，但未拆出「objectness prior 來源」的因果（例如未換 SAM / CLIP 等對照）。

4. **Action representation**（Figure 11）— 五個變體：gripper-only point flow（本文）、whole-body 500 點、whole-body 3000 點、low-dim EEF pose、low-dim joint position。在 B1K 上 point flow 全面勝過 low-dim；在 DROID 上 whole-body flow 反而劣於 low-dim，gripper-only 同時取得跨 embodiment 最佳（Franka + bimanual humanoid）。**屬診斷型**：直接對應「為什麼選 gripper 點而非整身」這個 design 決策。

5. **Chunked vs. autoregressive prediction**（Figure 12）— 對比 teacher-forcing AR、self-feeding AR、chunk + sliding window $W=1$ / $W=5$、chunk + chunk（本文）。chunk + chunk 在第 10 步仍維持 $\ell_2$ mover 約 0.04，而 chunk-trained + W=1 推論則飆升至 0.07–0.08。**屬診斷型**：同時揭示「training/inference strategy 必須對齊」這一更普適的結論。

6. **Partial observability / camera count**（Figure 13）— 訓練時用 1 / 2 / 3 / random 個 camera，測試時掃 1 / 2 / 3。random 訓練的版本在所有測試設定下最佳，且推論加 camera 永遠有幫助（即便訓練是 fixed-count）。**屬診斷型**：證實模型對 partial observability 有實際容忍度，而非過擬合到固定視角。

7. **Scaling laws**（Figure 9）— data fraction 5–100%、model 50M–1B 各掃一軸。log-linear 下降，無明顯飽和。**屬診斷型偏 sanity**：規模實驗本身正確，但未報告 token / step 與 compute optimal 的關係（無 Chinchilla-style 等量比較）。

8. **Annotation quality**（Figure 5）— 對比四種 annotation pipeline（Sensor depth + V1 / V2 extrinsics、FS + VGGT、FS + 本文 optimized extrinsics），用 depth reprojection loss、F1 @ 5 mm / 20 mm 三項指標。本文 pipeline 在所有指標主導且保留更多 scenes < 0.10 depth-loss。**屬診斷型**：直接對應「真實 3D 標註值得這麼大功夫嗎」這個 dataset-side 的設計決策。

可疑為 sanity check 而非診斷的部分：scaling-law 圖只證實「越大越好」但不揭示 compute-optimal 配方；DINOv2 → DINOv3 的對比僅單向上升，未對 backbone × feature 做交叉，難以分離兩者貢獻。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — GBND [5]（Science Robotics 2025 review 中代表性 learning-based dynamics model）作為起點，並橫向對比 PointNet / PointNet++ / SparseConv / Transformer 五種主流 point cloud backbone（Table 1）。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時在 DROID（real）、BEHAVIOR-1K（sim）兩個來源訓練評測，並在 8 項真實機器人任務（rigid pushing、deformable、articulated、tool use）上 zero-shot 部署（Figure 8）。
- [covered] Has ablations that diagnose the new components (not just sanity checks) — backbone、training objective、action representation、chunked prediction、partial observability 五組皆是針對 design decision 的對照（§6.5 第 1–6 點）。
- [covered] Has a scaling study (size, length, or compute) — 模型 50M / 132M / 411M / 1B 與資料 5% / 10% / 25% / 50% / 100% 雙軸（Figure 9），呈 log-linear。
- [covered] Has an efficiency / wall-clock comparison — Table 1 同表報告 Params / Memory / FLOPs / Latency；論文強調 PTv3-1B 推論約 0.12 s，並對比 pixel-based diffusion 的 seconds-long 推論。
- [partial] Reports variance / standard deviation / multiple seeds where relevant — $\ell_2$ 指標僅報告 mean，理由是 40k trajectory × 10k 點下 standard error $\le 10^{-5}\,\text{m}$；但真實機器人 success rate（每任務 10 次 trial 量級）未報告 trial 數或 binomial CI，且 main table 並非多 seed 平均。
- [partial] Releases code / weights / data sufficient for reproducibility — 摘要與結論承諾「Code, dataset, and pre-trained checkpoints will be open-sourced」，但本文取得時間點下未驗證實際發佈狀態；訓練超參數（optimizer、batch size、learning rate schedule、總步數、$\tau$ / $\kappa$ / MPPI 參數）主文皆未明示，需仰賴未取得的 Appendix。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 統一的 3D point flow 表徵讓 state 與 action 在共享 3D 空間中對齊,並支援跨化身學習。** 部分支持。Figure 11 顯示 gripper-only point flow 在 DROID 與 B1K 上同時優於低維 EEF/joint baselines,確實證明點流動作對跨化身有正向遷移;但實機評測全部集中在單臂 Franka,bimanual humanoid 僅在 BEHAVIOR-1K 模擬內驗證,跨化身在硬體層面仍未證明。
- **Claim 2: 大規模 3D 標註管線產出最大規模的 dynamics modeling 資料集。** 完全支持。Figure 5 的 depth reprojection loss 與 F1 alignment 指標都顯示新管線勝過 DROID 原始 V1/V2 與單純使用 VGGT 的方案,且在 0.10 loss 門檻下保留場景數明顯更多。
- **Claim 3: 提出可規模化的 3D 世界模型訓練配方(backbone、objective、features、scale)。** 完全支持。Figure 7 的 roadmap 與 Figure 9 的 scaling 曲線提供清楚的逐步消融與 log-linear 證據,Table 1 量化了 PTv3 相對其他 backbone 的計算/參數效率。
- **Claim 4: 0.1 秒即時推論可整合 MPPI 完成 in-the-wild 多樣操作。** 部分支持並有過度宣稱嫌疑。0.1s 單次 forward pass 屬實(Table 1 PTv3-1B = 0.12s),但 MPPI 真正所需的 K-sample batch latency 與控制頻率未報告;Figure 8 的 8 項任務確實展示多樣性,但 Book 20% 與 Microwave 30% 的成功率不足以宣稱「general」manipulation 能力。
- **Claim 5: 單一 checkpoint 不需 demonstrations 或 post-training 即可部署。** 部分支持。模型權重確實 zero-shot 不變,但部署仍需人工繪製 mask 與透過 GUI 指定目標位置;此外 held-out real 的 zero-shot $\ell_2$ 與 from-scratch specialist 幾乎打平(0.0305 vs 0.0293,Table 2),pretraining 在新場景上的真正優勢在 finetune 後才顯現。

### 7.2 Fundamental Limitations of the Method

**Pseudo-label 上限即模型上限。** DROID 的 3D ground truth 由 FoundationStereo + VGGT-refined extrinsics + CoTracker3 三個現成模型串成,任何上游錯誤(立體匹配在反射/透明物體的失效、tracker 對遮擋的 visibility 誤判)會永久寫進訓練 signal。Aleatoric uncertainty head 只能讓模型對雜訊「不那麼自信」,並不能修正系統性偏差;當部署遇到玻璃瓶、深色軟物等對 stereo depth 不友善的情境時,模型必然繼承這些感知盲區。

**$\ell_2$ point flow 與任務成功之間沒有直接梯度。** 訓練 objective 是 per-point displacement L2,推論時 MPPI 的 cost 是 task-relevant 點到目標位置的 L2;這意味著模型對「物體被推到位但路徑不同」與「物體錯過但路徑像」會給出近似的 cost,沒有 contact event、grasp success、joint constraint satisfaction 等離散事件的概念。論文自己引用 [125] 承認 task-level success 與 $\ell_2$ 解耦,但其方法本身無法突破這層解耦。

**Chunked prediction 的固定 horizon $H=10$ 是硬限制。** 模型只在 1 秒視窗內訓練與評測,Figure 12 顯示 sliding window 超出 $W$ 後 error 急速劣化。對於需要長程規劃的任務(多步插拔、序列工具使用、長 horizon 的可變形物體操作),目前架構必須以 autoregressive chunk 串接,而 self-feeding rollout 的 drift 已被論文自身證實會劣化,這是一個結構性而非工程性的瓶頸。

**Action 表徵綁定 URDF 可知。** 論文反覆強調動作是「robot 自身幾何透過 forward kinematics 投影成的 point flow」。這對工業臂與已知 humanoid 成立,但對 soft robot、tendon-driven 手、可變形夾爪、人手或第三方物體當作動作媒介(如「抓住扳手再去操作螺絲」中的扳手)會立即失效——後者既不是場景也不是 robot。

### 7.3 Citations Worth Tracking

- **DROID (Khazatsky et al. 2024, ref [7])** — 本工作的真實資料源頭,理解 DROID 原始 calibration 缺陷與覆蓋分布是判斷 PointWorld 泛化邊界的前提。
- **FoundationStereo (Wen et al. 2025, ref [9])** — 整套 3D 標註管線的 depth 基礎,直接決定模型可用的物理保真度;讀完才能評估反射/透明物體的失敗模式。
- **CoTracker3 (Karaev et al. 2025, ref [11])** — 提供 2D point track 與 visibility map,其遮擋判斷的 false negative/positive 直接決定哪些訓練樣本被遮蔽,是雜訊源頭之一。
- **Ai et al. 2025, "A review of learning-based dynamics models" (ref [5])** — 本論文的 baseline GBND 與分類框架皆出自此 survey,讀後可定位 PointWorld 在整個 dynamics-model 譜系中的位置。
- **PTv3 (Wu et al. 2024, ref [152])** — 全部 scaling 結論依附此 backbone,理解其 serialization 與 U-Net 注意力結構才能判斷 1B 之後是否還能再 scale。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] Book 20%、Microwave 30% 等低成功率任務的失敗主要來自 dynamics 預測誤差、MPPI 採樣不足,還是 mask/goal 規格化雜訊?論文未提供 failure mode 分類。
- [ ] MPPI 在實機部署時的 K 是多少、batched forward latency 與實際控制頻率為何?僅報告單次 0.1s 不足以還原 closed-loop 性能。
- [ ] 對 occluded 區域(box 後側、抽屜內側)的 displacement 預測,DINOv3 features 透過 2D 投影無法取得,模型實際是用什麼填補這些位置的特徵?
- [ ] Real 與 sim 的 $\ell_2$ 差 17 倍(D$\to$B = 0.1460 vs B$\to$B = 0.0087),這個差距是模擬器物理偏離真實、rendering domain gap,還是動作分布差異主導?
- [ ] $H=10$、$0.1\text{s/step}$ 的設計選擇從何而來?延長 horizon(如 H=20 或 30)在訓練成本與 drift 之間的 trade-off 是否真的不可行?
- [ ] 在 humanoid 實機上 zero-shot 部署是否成立?目前所有實機實驗皆為 Franka,跨化身宣稱缺乏硬體驗證。
- [ ] 評測時使用 expert-filtered top 80% 的點;若改用未過濾的全集或不同過濾比例,各 baseline 的相對排名是否仍然穩定?

### 8.2 Improvement Directions

1. **加入接觸事件輔助 loss(高可行性)。** 既然 ground-truth flow 已知,可額外監督「接觸發生 vs 未發生」的離散標籤,讓模型在 cost 層具備 contact awareness,直接緩解 §7.2 中 $\ell_2$ 與任務成功解耦的問題。
2. **訓練時混合 chunk 與 autoregressive 兩種 rollout objective(中可行性)。** Figure 12 顯示純 chunk 模型在 sliding-window 推論下會崩壞;若以隨機機率交替 teacher-forcing chunk 與 self-feeding step,可同時保有 chunk 的算力效率與 AR 的長 horizon 一致性。
3. **以 VLM/SAM 自動產生 task-relevant points,取代 GUI(中可行性)。** §3.2 已提及目標可由 VLM 指定 [145],但實機評測仍仰賴人工繪製 mask,將之自動化才能讓「single image, no demonstrations」的宣稱完整成立。
4. **加入 multi-modal head(如 mixture-of-Gaussians 或 small diffusion head)替代純 L2 回歸(中可行性)。** 目前 aleatoric uncertainty 僅給出 scalar variance,無法表達「物體可能往左也可能往右」的雙峰分佈;對 deformable 與 articulated 任務這種多模態結果普遍存在,L2 + log-variance 會被推回平均位置而失去物理意義。
5. **以 simulator privileged information 進行 distillation 而非僅 L2 finetune(較低可行性,但收益高)。** 目前 sim-to-real 落差由 finetune 的少量更新硬縮,但 BEHAVIOR-1K 提供完整 contact、mass、joint state,若以這些 privileged signal 訓練 teacher、再 distill 給 RGB-D-only student,可能根本性改善 D$\to$B 與 B$\to$D 的 17× $\ell_2$ 差距。
6. **針對反射/透明物體加入 stereo-aware data augmentation 或材質特定的不確定度上限(較低可行性)。** PointWorld 的感知上限被 FoundationStereo 鎖死;在訓練時人為注入 stereo 失效樣本(模擬玻璃、鏡面),讓 uncertainty head 學會在這些區域主動放棄預測,可避免 MPC 規劃對虛假深度過度自信。
