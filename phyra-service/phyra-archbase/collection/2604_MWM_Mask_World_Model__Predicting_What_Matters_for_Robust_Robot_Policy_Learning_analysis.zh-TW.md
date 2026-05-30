<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# MWM — Mask World Model: Predicting What Matters for Robust Robot Policy Learning

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | MWM |
| Paper full title | Mask World Model: Predicting What Matters for Robust Robot Policy Learning |
| arXiv ID | 2604.19683 |
| Release date | 2026-04-22 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2604.19683 |
| PDF link | https://arxiv.org/pdf/2604.19683 |
| Code link | https://github.com/LYFCLOUDFAN/mask-world-model |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Yunfan Lou | National University of Singapore; Beijing Academy of Artificial Intelligence | — | first author (equal contribution) |
| Xiaowei Chi | The Hong Kong University of Science and Technology | https://github.com/litwellchi | co-first author (equal contribution) |
| Xiaojie Zhang | Beijing Academy of Artificial Intelligence; Peking University | — | co-first author (equal contribution); project leader |
| Zezhong Qian | Peking University | — | co-author |
| Chengxuan Li | Peking University | — | co-author |
| Rongyu Zhang | The Hong Kong University of Science and Technology; Nanjing University | — | co-author; project leader |
| Yaoxu Lyu | Beijing Academy of Artificial Intelligence; Peking University | — | co-author |
| Guoyu Song | Peking University | — | co-author |
| Chuyao Fu | Beijing Academy of Artificial Intelligence; Peking University | — | co-author |
| Haoxuan Xu | The Hong Kong University of Science and Technology | — | co-author |
| Pengwei Wang | Beijing Academy of Artificial Intelligence | — | co-author |
| Shanghang Zhang | Beijing Academy of Artificial Intelligence; Peking University | https://www.shanghangzhang.com/ | corresponding author |

### 1.2 Keywords

world model, semantic mask prediction, diffusion policy, video diffusion transformer, robot manipulation, vision-language-action, geometric information bottleneck, flow matching

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| π0 (Black et al., 2026) | baseline | RGB-centric generalist VLA policy, primary head-to-head baseline on LIBERO/RLBench/Real-world. |
| GE-ACT (Liao et al., 2025) | baseline | Multi-view video-diffusion world model coupled to an action head; RGB counterpart MWM directly contrasts. |
| Cosmos (NVIDIA et al., 2025) | baseline | Large video-generative world model used with IDM/Latent IDM as RGB world-model baselines on LIBERO. |
| OpenVLA (Kim et al., 2024) | baseline | Open Vision-Language-Action generalist policy serving as an RGB-centric reference baseline. |
| CogACT (Li et al., 2024) | baseline | Diffusion-action VLA baseline on LIBERO compared against MWM. |
| Dreamer-style world models (Hafner et al., 2024; 2025) | predecessor | Latent-space predictive world models for control; conceptual predecessor that motivates leaving pixel space. |
| Flow Matching (Lipman et al., 2023) | base model | Conditional flow-matching objective adopted for the mask-dynamics backbone training. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於「以世界模型為基礎的機器人操作策略學習」這一研究主題。具體而言，作者關注如何讓基於大規模影片生成式預訓練的 world model 真正服務於閉迴路控制，而非僅追求 RGB 像素層級的高保真重建。研究涵蓋語言條件式多視角操作（language-conditioned multi-view manipulation）、擴散式策略（diffusion policy）以及視覺-語言-動作（VLA）通用策略的穩健性與分布外泛化問題，並在 LIBERO、RLBench 等模擬基準與真實 Franka Emika Panda 機器人上進行系統性驗證。同時，作者透過隨機 token pruning 等壓力測試，探討模型在部分可觀測與紋理資訊缺失下的控制韌性。

### 2.2 Domain Tags

- Robotics
- Robot Learning
- Computer Vision
- Embodied AI
- Generative Models

### 2.3 Core Architectures Used

- **Mask World Model (MWM)**：作者提出的核心架構，將預測目標由未來 RGB 影格替換為未來語意 mask 的潛在表示，作為提供 mask-centric predictive features 的世界模型骨幹。
- **DiT-style Video Diffusion Transformer Backbone**：以 $N=28$ 層 transformer block 處理多視角 latent token 序列，配合 self-attention、text cross-attention 與 feed-forward，作為 mask 動態的生成骨幹（Figure 2，page 4）。
- **Shared Video VAE**：重用同一個預訓練 video VAE 同時編碼 RGB 觀測與經調色板渲染後的語意 mask，建立 RGB 與 mask 共享的連續潛在空間（page 3）。
- **Conditional Flow Matching**：採用 Lipman et al. (2023) 的 flow matching 目標，沿 noise 與 clean target 的線性內插路徑訓練速度場 $v_\theta$，作為 Stage 1 的 mask 預測損失。
- **AdaIN-style Timestep Modulation with RMSNorm**：以 timestep-dependent 的 $\alpha(s)$、$\beta(s)$ 對歸一化後的隱藏態進行 scale-shift 調變，穩定 VAE-normalized latent 上的 diffusion 訓練（Eq. 7，page 5）。
- **3D RoPE with Interpolation Scale**：在 $(t, h, w)$ token 座標上套用 3D RoPE，並依 VAE 的時空壓縮比設定 $\gamma=(\gamma_t, \gamma_h, \gamma_w)$，使位置相位在不同解析度間保持一致（Eq. 6，page 4）。
- **Mask-Guided Diffusion Policy Head**：由 action expert 與 action decoder 組成的擴散式策略頭，透過 cross-attention 從 backbone 的 predictive feature bank $H_t$ 取用控制相關特徵，於 action 空間以加權 score-matching 進行去噪。
- **Receding Horizon Control (RHC) Sampler**：推論時以 10-step Euler discrete diffusion sampling 產生 $H_a=36$ 步的動作 chunk，僅執行第一步並在下一時刻重新規劃。
- **Two-Stage Training Protocol**：Stage 1 以 $\mathcal{L}_{\text{mask}}$ 預訓練 mask 動態骨幹，Stage 2 僅以 $\mathcal{L}_{\text{act}}$ 端到端訓練動作頭並反向更新骨幹，使其 predictive features 對齊控制目標。

### 2.4 Core Argument

作者主張：機器人控制策略的脆弱性源自於 world model 的預測目標與控制目標之間的本質錯位。標準作法以 RGB 像素重建為訓練訊號，會迫使模型把容量分配給紋理、光照、反射、動態背景等與動作選擇無關的 nuisance variation，並把外觀變化與接觸相關運動纏繞在同一個表徵中；在閉迴路 rollout 中，這些外觀驅動的微小誤差會隨時間累積，造成預測漂移與在輕微分布偏移下的策略崩潰。基於此根因，作者認為解法在邏輯上必須把預測空間從「光度真實感」轉移到「決策相關的幾何結構」，因此提出 Mask World Model：以 video diffusion 架構預測未來語意 mask 的演化，透過 mask 形成的 geometric information bottleneck 強迫 backbone 聚焦於物體身分、空間佈局與接觸幾何，同時濾除冗餘外觀。為避免部署時依賴外部分割器，語意監督僅在離線訓練時使用，推論時模型只吃多視角 RGB；並透過共享 VAE 將離散 mask 編碼到與 RGB 一致的連續潛在空間，再以 flow matching 學習條件式潛在動態。最後，作者把 mask-centric 的預測特徵透過 cross-attention 餵入 diffusion policy head，以兩階段訓練讓 backbone 的隱藏狀態被動作損失進一步「控制對齊」，從而在保持 RGB 推論介面的同時，獲得對外觀變化更穩健、且在長時程任務上漂移更小的控制策略。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(210 words)

標題「Mask World Model: Predicting What Matters for Robust Robot Policy Learning」直接點明三個關鍵字：mask、world model、robust policy learning，暗示本文的核心主張是「預測重要的東西、而非預測像素」。Abstract 採取「問題-原因-解法-結果」四段論的標準鋪陳。第一段先肯定 video generative pre-training 作為 generalist robot policy 的潛力；第二段隨即指出標準做法的缺陷：聚焦於 high-fidelity RGB video prediction 會讓模型 overfit 到 dynamic backgrounds、illumination 等與 control 無關的 nuisance 因子，最終導致 fragile policies。這一段建立了讀者對 RGB-centric 路線的不信任，是後續切換預測空間的動機鋪墊。第三段提出 MWM 的核心設計：沿用 video diffusion 架構，但把預測目標從 pixels 改為 semantic masks 的時序演化，並把這個改動稱為 geometric information bottleneck，宣稱可同時保留 physical dynamics 與 contact relations、過濾 visual noise；同時強調 mask dynamics backbone 與 diffusion-based policy head 的端到端整合。第四段以實驗結果作收，宣告在 LIBERO、RLBench 兩個 simulation benchmark 上顯著超越 SOTA RGB-based world models，並補上 real-world 與 random token pruning 兩項 robustness 證據。Abstract 為後文鋪陳了三條主軸：semantic bottleneck、policy coupling、robustness/generalization。

### 3.2 Introduction

(640 words)

Introduction 以「learning generalist robot manipulation policies that remain reliable under real-world visual variability」開場，把 robust generalist policy 確立為 central challenge，並指出 predictive world model 是有前景的方向，引用 Dreamer、V-JEPA、WoW 等代表工作以建立合法性。隨即在第二段拋出本文要攻擊的標靶：大多數 video world models 以 RGB pixels 為預測目標，而 photometric objective 與 control 是 misaligned 的；RGB frames 含有 texture、lighting、reflection、dynamic background 等 nuisance variation，迫使模型 entangle appearance 與 dynamics，並在 closed-loop 執行下因 appearance-driven errors 累積而導致 predictive drift 與 brittle policies。這一段以 Wang 2023、Grooten 2023、Liu 2025 等文獻支撐 RGB pixel prediction 的弊病，是整篇論文的 problem framing。

第三段提出本文立場：robust control 應該預測 decision-relevant dynamics 而非 photometric realism，並引入 MWM 作為解法（指向 Figure 1）。關鍵設計在於把 prediction space 從 future RGB frames 換成 future semantic masks，宣稱 semantic masks 能保留 object identity、spatial layout、interaction-relevant structure 而捨棄冗餘 appearance。作者特別強調一個工程上的便利：MWM 在 inference 時不需要 external segmentation model，semantic labels 只在 training offline 使用，deployment 仍是 raw multi-view RGB——這個論述同時回應了「semantic supervision 是否會增加部署成本」的潛在質疑。

接著鋪陳兩階段訓練 pipeline：Stage 1 以 conditional diffusion 預測 future semantic masks 學習 mask-centric predictor；Stage 2 訓練 diffusion policy 以 backbone 中間特徵為條件生成動作。作者強調這個 coupling 是 essential——policy 被顯式優化以從 mask-centric predictions 中萃取 control utility，而非把 mask 當作 auxiliary visualization。這段話為後續 §3.4、§3.5 的雙階段訓練協議與 §4.1 中 MWM-C1/C2/MWM 的對照實驗預留了論證入口。

第四段提供 results preview：LIBERO 98.3% 平均成功率、RLBench 68.3%、real Franka robot 四個任務 67.5% 平均成功率，並引入 robustness（visual token pruning）與 generalization（appearance shift）兩個壓力測試，預告 §4.3 的分析。最後以三條 contributions 收尾：（1）提出 MWM，inference 時純 RGB；（2）設計 mask-guided diffusion policy 並驗證 mask-centric features 對 control 的優勢；（3）研究多種 mask 利用方式，指出效益主要源於 representation 與 objective 的轉換、而非特定架構設計。第三點為後文的 ablation 與 MWM-C1/C2 對照鋪路，把論點從「我們有一個好架構」抬升到「mask-centric 是一條路線」。

### 3.3 Related Work / Preliminaries

(490 words)

Related Work 切成三個子節，每節都採取「描述現有路線→指出共通缺陷→點出 MWM 的差異」三段式結構，目的是把 MWM 定位在文獻地圖中既相關又獨立的位置。

§2.1 Video world models for robot policy learning 從 Dreamer 系列的 latent-space 預測動力學講起，再過渡到近期將 diffusion/transformer video generators 改造為 robotics predictive backbone 的工作（Cosmos、Sora-style 模型、GE 系列、Wow、MIND、EVA、ManipDreamer 等）。作者指出這條路線的共通弱點：optimize prediction in an appearance-centric space（RGB reconstruction 或相關 latents），鼓勵建模 nuisance variation 並 entangle appearance 與 interaction dynamics；即使是 LaDi-WM、MoWM、UniVLA、WristWorld、ManipDreamer3D 等並行的 diffusion world-model 變體，predictive target 依然主要是 photometric。這段把 §1 的批判落實到具體文獻上，並以「MWM predicts future semantic mask dynamics, using semantic supervision only during training and requiring no external segmenter at test time」明確區隔。

§2.2 Vision-Language-Action models 改從 generalist policy 端切入，列舉 RT-2、Octo、MoLe-VLA 等大型 VLA，再點出當任務需要 precise spatial relations 與 contact-sensitive control 時，policy 需要更顯式 expose object state 與 interaction geometry 的 representation。作者枚舉現有注入語意的做法：instruction-aligned token pruning（SemanticVLA）、auxiliary reconstruction（ReconVLA）、external grounding masks（RoboGround），然後強調 MWM 在 mechanism 與 deployment 上都不同——它把 semantics 當成 predictive lookahead 而非 input cue，並以 policy head 消費 mask-centric predictive features，同時保持 pure-RGB 介面。這段話特別重要，它把 MWM 與「以 mask 作為 input cue」的方法切割開，強化了 §3.3「inference 時不需 segmenter」的賣點。

§2.3 Structured representations under masking 把視野拉到更上游的表徵學習：object-centric representations（Slot Attention、MONet、Genesis-v2）與 masked modeling/token dropping（MAE、VideoMAE）構成的學術背景，論證 compact、structure-biased representations 比 raw pixels 更穩定的 broader intuition。MWM 把這個直覺實例化在 manipulation 上：以 semantic structure 作為 diffusion world model 的 predictive space 並耦合 diffusion policy head。文末順帶交代 random visual token pruning 的角色——只是 evaluation stress test，並非 modeling contribution——避免讀者誤以為 token pruning 是設計賣點，這也預先回應了 §4.3.1 的實驗定位。整節為後續 Method 的「為什麼預測 mask」與「為什麼不用 external segmenter」提供了文獻支持。

### 3.4 Method (overview narrative)

(380 words)

Method 開宗明義把 MWM 定義為 mask-centric world model，由 mask-dynamics backbone 與 diffusion policy head 兩個元件組成，並指向 Figure 2 作為視覺索引。整節的敘事邏輯遵循「動機—問題設定—骨幹—policy head—訓練流程」的線性鋪陳，目的是讓讀者在進入細節前先掌握整體資訊流。

§3.1 Motivation: Geometric Information Bottleneck 是承接 Introduction 的橋樑，用一段話複述 RGB nuisance 問題並把 mask prediction 命名為 geometric bottleneck，為後續所有設計選擇奠定詞彙。§3.2 Problem Setup 形式化任務：在時刻 $t$ 接收 multi-view RGB $o_t = \{o_t^{(v)}\}_{v=1}^V$ 與 language instruction $p$，輸出 continuous action $a_t$；強調學到的 closed-loop policy 應對 background、lighting、object color 等 photometric changes 不敏感。

§3.3 Mask Dynamics Backbone 是 Method 的主體，但本節僅作 overview：強調 offline semantic supervision、deployment 純 RGB 的 deployment philosophy；以共享 VAE 把離散 mask 渲染為 RGB 相容圖像 $\tilde m_t$ 後編碼，避免修改預訓練 VAE；經由 channel-wise normalization、temporal interpolation、multi-view stacking 形成定長 token 序列；以 conditional flow matching 在 memory（clean RGB latents）與 future（noised mask latents）混合序列上訓練；以 3D RoPE with interpolation scale 處理 VAE 壓縮造成的位置相位錯位；以 AdaIN-style timestep modulation 替代標準 adaptive normalization 增強穩定性；最後從 transformer blocks 緩存 hidden states 形成 multi-level predictive feature bank $H_t$ 供 policy head 使用。多視角處理以共享 spatiotemporal self-attention 為主、週期性插入 cross-view mixing。

§3.4 Mask-Guided Diffusion Policy 將 action 與 proprioceptive state 拼接為 $u_t = [a_t, s_t]$，作為 conditional denoiser 在 action space 上的輸入，loss 為 $\mathcal{L}_{act}$；test time 以 receding-horizon closed loop 執行。§3.5 Two-Stage Training Protocol 確立論文最核心的訓練哲學：Stage 1 以 $\mathcal{L}_{mask}$ 預訓練 backbone（n=4 memory frames、$\tau$=5 future latents）；Stage 2 從 Stage-1 checkpoint 開始僅以 $\mathcal{L}_{act}$ 端到端優化，VAE 凍結，DiT backbone 與 action expert 聯合訓練——關鍵是「不再加 mask loss，讓 $\mathcal{L}_{act}$ 的 gradient 將 backbone features 拉向 control-aligned」。Inference 採用 RHC、10-step Euler discrete diffusion sampling 預測 36-step action chunk，執行首步後 replan。整節為 §4 的雙階段對照實驗與 ablation 預先建立論證骨架。

### 3.5 Experiments (overview narrative)

(430 words)

Experiments 以「兩個 simulation benchmark + 一個 real-robot setup + 兩項 robustness/generalization 壓力測試」的結構鋪展，整體論證走向是「先在 simulation 證明 mask-centric 比 RGB-centric 更好，再在 real-world 證明 deployment 可行，最後在受控擾動下證明 representation 確實更 robust」。

§4.1 Simulation Experiments 同時涵蓋 LIBERO 與 RLBench：LIBERO 跑 Spatial、Object、Goal、Libero-10 四個 suite，每個 suite 取 best validation checkpoint 並評估 500 episodes；RLBench 跑六個代表性任務、每任務 20 episodes。Baseline 涵蓋 RGB-centric generalist policies（OpenVLA、CogACT、$\pi_0$）與 world-model pipelines（Cosmos+IDM、Cosmos+LatentIDM、GE-ACT、FiS-VLA），並在相同訓練資料下增測 MWM 的兩個簡化 variant：MWM-C1（顯式解碼 future mask 加 IDM）與 MWM-C2（直接以 predictive latent features 餵 policy head）。這個三方比較是論文最關鍵的論證——讓 RGB world model 與 mask world model 在配對的條件下對拍，以排除「效益是否來自架構而非 representation 改變」的疑慮。結果顯示 mask-centric 變體在 LIBERO 全 suite 一致勝出，且 long-horizon 任務（Libero-10）增益最大；MWM 完整版加上 wrist view 後達到 0.983 平均 SR；RLBench 上 MWM 達 68.3%，遠超 GE-ACT 的 30.8% 與 FiS-VLA 的 50.0%。

§4.2 Real-World Experiments 在 Franka Emika Panda 上配兩台 RealSense D435i（third-person + wrist），跑四個 language-conditioned 任務（bread+hotdog→basket、open drawer + put pen、pour water、book→shelf）。每任務 50 demonstrations，並使用 RoboEngine 自動標 mask；GE-ACT 與 $\pi_0$ 在相同資料與設定下 post-train 以求公平。每方法每任務 20 trials。MWM 取得 67.5% 平均 SR，遠超 GE-ACT 的 23.8% 與 $\pi_0$ 的 38.8%，最大增益落在 drawer manipulation 與 pouring 等 tighter goal constraints 任務上。

§4.3 Analysis: Robustness and Generalization 是論文的「representation quality 直接證據」。§4.3.1 Random Token Pruning 在 LIBERO 上以 nPAUC 量化壓力測試，掃描 $r \in \{0.1, \dots, 0.9\}$，MWM 取得 0.648 vs. GE-ACT 0.629，作者把優勢歸因於 mask token 集中在 object geometry 與 relations 上、對 missing tokens 較不敏感。§4.3.2 Visual Generalization 在 real-world 任務下施加 BG、Light、Color 三種 appearance shift，以 OOD-SR 與 Retain 兩個指標總結；MWM 取得 OOD-SR 42.1%、Retain 0.62，全面領先 baselines，且 BG shift 下 GE-ACT 近乎崩潰（3.8%）而 MWM 仍維持 27.5%。這兩個分析共同驗證 §1 與 §3.1 的核心 hypothesis：semantic bottleneck 真的能 yield decision-relevant representations。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

Conclusion 用一段話完成 wrap-up：回顧 MWM 的核心設計（以 future semantic masks 取代 photometric RGB 預測、緩解 photometric prediction 與 control utility 的 mismatch、僅 offline 用 semantic supervision、deployment 純 RGB、mask-centric predictive features 與 diffusion policy head 耦合進行 closed-loop control），複述三個 benchmark 與 real-robot 實驗的全面領先，並把整個論文的 take-away 提煉為一句結論：semantic prediction 是學習 decision-relevant dynamics representations 的 practical information bottleneck。

值得注意的是，本論文並未設立明確的 Limitations 或 Future Work 子節——這在 ICML/NeurIPS 風格的 preprint 中並不罕見，但確實構成審稿人可能挑戰的弱點。論文未討論的潛在限制至少包括：（1）對 RoboEngine 等 offline segmentation tool 的 label quality 依賴；（2）semantic mask 對非剛性物體、透明物或高頻 contact 的描述能力；（3）two-stage 訓練的 compute cost；（4）在更大 task 多樣性下 mask palette 是否需擴展。這些是讀者在內化論文時應自行補上的批判性思考，也是 §4.3 robustness 證據雖然亮眼但仍屬範圍受限的 stress test 的原因。

## 4. Critical Profile

### 4.1 Highlights

- 將 video diffusion 的預測目標從 RGB 像素改為 future semantic mask latents，藉此施加 geometric information bottleneck（§3.1, p.3）。
- 共用同一個 pretrained video VAE 同時編碼 RGB 與「以 fixed color palette 渲染後的 mask」，無需修改 VAE 即可把離散 mask 映射到連續 latent 空間（Eq. 1, p.3）。
- 兩階段訓練：Stage 1 用 conditional flow matching 學 future mask latents，Stage 2 凍結 mask loss 後僅以 $L_{\text{act}}$ 反向更新 backbone，使預測特徵「control-aligned」（§3.5, p.5）。
- 推論時僅吃多視角 RGB，部署不需要任何 external segmenter，介面與一般 RGB-only policy 相容（§3.3, p.3）。
- LIBERO 四個 suite 平均 SR 達 98.3%，超越 GE-ACT (96.5%) 與 π0 (94.2%)，其中 LIBERO-10 long-horizon 從 GE-ACT 0.944 提升至 0.960（Table 1, p.6）。
- RLBench 六任務平均 SR 68.3%，幾乎是 GE-ACT (30.8%) 的兩倍、領先 FiS-VLA (50.0%) 18.3 個百分點，Wine at Rack 達 90.0%（Table 2, p.7）。
- Real-world Franka 四任務平均 SR 67.5%，相對 π0 (38.8%) 與 GE-ACT (23.8%) 有顯著差距，且每任務僅用 50 demonstrations（Table 4, p.7）。
- Visual generalization 三種 shift（BG / Light / Color）下平均 OOD-SR 42.1%，是 π0 (19.2%) 的 2.2 倍、GE-ACT (12.5%) 的 3.4 倍；Retain ratio 0.62（Table 3, p.7）。
- random visual token pruning 壓力測試下 nPAUC 0.648 略勝 GE-ACT 0.629，作者將其歸因於 mask-centric token 把 capacity 集中於 object geometry（Table 5, p.7）。
- 提出 MWM-C1（顯式 future-mask decoding + IDM）與 MWM-C2（predictive latent feature head）兩個變體，把 design space 拆解為「decoded mask vs latent feature」與「mask vs RGB target」兩條軸（Algorithms 1–2, §C, p.15）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

The paper does not openly discuss limitations: it has no dedicated limitations section and no failure-mode analysis. The only scope caveats found are minor: §2.3 notes that random token pruning is adopted as an "evaluation stress test (not a modeling contribution)"，以及 §3.3 把 3D RoPE 的 $\gamma$ 與 cross-view frequency 的具體設定推給 appendix。Tables 7–8 (p.14) 顯示 MWM 與 GE-ACT 在 $r \geq 0.7$ 的高比例 pruning 下幾乎同時崩潰至 SR ≈ 0，但作者未把它列為 method 的限制。

#### 4.2.2 Phyra-inferred

- **Table 1 與正文於 MWM-C2 vs Cosmos w/ Latent IDM 結果不一致**: §4.1 正文聲稱「MWM-C2 improves over Cosmos w/ Latent IDM (0.873→0.918)」(p.6)，但 Table 1 顯示 Cosmos w/ Latent IDM avg = 0.919 而 MWM-C2 avg = 0.918——0.001 個百分點落後而非 4.5 個百分點領先；引文中的 0.873 baseline 不出現在表中。這是「same-camera, mask vs RGB latent world model」最乾淨的對照，方向被反向陳述。
- **wrist-view 對比不對等**: Table 1 中 MWM 主結果使用 3rd+wrist，而 Cosmos w/ IDM、Cosmos w/ Latent IDM、MWM-C1、MWM-C2 全是 3rd-only；同條件 baseline 只剩 π0 與 GE-ACT，無法把「mask vs RGB」與「相機數量」的貢獻拆開。
- **語意監督的標註上限沒被量化**: Stage 1 完全依賴 RoboEngine (Yuan et al., 2025) 自動標註 (p.6, p.13)，但 paper 未報告 mask annotation 的 precision/recall，也未測試標註雜訊對下游 policy 的敏感度，這是整個 pipeline 的單點故障。
- **「geometric information bottleneck」的因果證據薄弱**: 全文反覆主張 mask 預測會強迫 backbone 聚焦 geometry 而濾除 appearance，但只用 OOD-SR 與 token-pruning 兩個 proxy 推論，未做表徵分析（如 latent 上 linear probing appearance vs geometry attribute、或 mutual information 測量）。
- **token pruning 增益實際微小**: nPAUC 0.629 → 0.648 只是 ~3% 相對提升 (Table 5, p.7)，且交叉比對 Tables 7–8 顯示 MWM 的領先集中在中度 pruning ($r=0.5$–$0.6$) 並在極端 pruning 下與 GE-ACT 一起崩潰；單一 nPAUC 純量遮蔽了真實的「中段才有差、極端一起死」型態。
- **沒有 mask-as-input 對照組**: 若 RoboEngine 在推論時仍可用，直接把 mask 當作 observation channel 就能拿到 geometric prior。Paper 未做此對照，因此「預測未來 mask」相對於「使用當下 mask」是否真有控制價值無法從現有實驗判斷。
- **Stage 2 的「control-aligned drift」未被量化**: §3.5 主張 Stage 2 的 $L_{\text{act}}$ gradient 會讓 backbone 變得「more control-aligned」，但全文未報告 Stage 2 後 backbone 對 future mask 的預測 loss 變化；無法判斷 mask 預測能力是被加強、保留還是悄悄退化。

### 4.3 Phyra's Judgment (summary)

MWM 真正新的是「把 video world model 的預測目標從像素換成 semantic mask 但保留 RGB-only 推論介面」這個框架選擇；其餘（shared VAE、flow matching、AdaIN modulation、predictive feature bank、cross-attention 接 action head）都是已成熟組件的工程組裝。實驗在 LIBERO 已逼近飽和、在 RLBench 與 real-world OOD 上的領先幅度顯著且方向一致，是有說服力的工程結果。但核心因果論述（「semantic bottleneck 是 OOD 韌性的成因」）目前只有 OOD-SR 與 token-pruning 兩個 proxy，且 §4.1 正文與 Table 1 在最關鍵的同相機對照上出現方向不一致，是後續工作必須先釐清的破口。

## 5. Methodology Deep Dive

### 5.1 Method Overview

MWM (Mask World Model) 採用 **video diffusion** 架構預測未來 **語意 mask** 的演化而非 RGB 像素，從而對 backbone 強加一個 **geometric information bottleneck**：表徵被迫聚焦於物體身分、空間佈局與接觸幾何，並濾除紋理、光照、背景等與動作無關的 nuisance variation。系統由三個耦合元件組成：(i) **shared video VAE**，把多視角 RGB 與 rendered mask 編碼到同一個連續潛在空間；(ii) **DiT-style mask dynamics backbone**（28 層、hidden dim 2048、32 heads），以 conditional flow matching 從 RGB memory 與語言條件生成 future mask latents；(iii) **mask-guided diffusion policy head**（28 層、hidden dim 512、16 heads），透過 cross-attention 從 backbone 各層快取的 **Predictive Feature Bank** 萃取控制相關特徵以生成連續動作。

訓練分兩階段：**Stage 1** 在離線語意監督下以 $L_{\text{mask}}$ (Eq. 4) 預訓練 mask dynamics backbone；**Stage 2** 從 Stage-1 checkpoint 出發，僅以 $L_{\text{act}}$ (Eq. 8) 端到端訓練動作擴散頭，而梯度同時更新 backbone 使其 predictive features 與動作目標 control-aligned。**部署時 MWM 只吃多視角 RGB**（含 third-person 與 wrist 視角），不需外部 segmenter——這是「mask 僅作為訓練監督、不作為推論輸入」的核心設計：mask 是訓練時的 geometric prior，而非推論時的 input dependency。

關鍵技術選擇包括：(a) 共用一個固定預訓練 video VAE，把離散 mask 透過固定 color palette 渲染為 RGB-compatible image $\tilde{m}_t \in [0,1]^{H\times W\times 3}$ 後再編碼，達成 RGB 與 mask 的潛在介面統一；(b) 採用 **flow matching** (Lipman et al., 2023) 的 linear interpolation path，把 conditioning 注入 velocity field 而非 path；(c) **3D RoPE with interpolation scale** $\gamma=(\gamma_t, \gamma_h, \gamma_w)$ 補償 VAE 壓縮造成的 positional phase 偏移；(d) **AdaIN-style timestep modulation**，在 RMSNorm 後做 element-wise scale-shift，穩定 normalized VAE latents 上的條件生成；(e) **conditioning mask** $b \in \{0,1\}^{n+\tau}$ 將 memory slots 強制 diffusion time = 0（clean）、僅在 future slots 計算 $L_{\text{mask}}$，使 backbone 學到「以 clean memory 條件預測 noised future」的能力。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input (per training step):
   RGB memory frames:       o_t = {o^(v)_t}_{v=1..V}   [B, V=2, n=4, 3, 256, 256]
   Future mask render:      m̃_t (Stage 1 only)         [B, V=2, τ=5, 3, 256, 256]
   Language prompt:         p (token ids)              [B, L_text]
   Diffusion timestep:      s ∈ [0, 1]                 [B]
   Noise:                   ε ~ N(0, I)                [B, V, τ, 8, 8, 128]
   Proprio state (Stage 2): s_t                        [B, H_a=36, 7]
   GT action chunk (S2):    a_t (7-DoF + 1-DoF)        [B, H_a=36, 8]

   ├→ Shared Video VAE encoder E  (frozen, f_s=32, f_t=8, D=128)
   │     z^o = E(o_t):       [B, V=2, n=4, 8, 8, 128]   # RGB memory latents
   │     z^m = E(m̃_t):       [B, V=2, τ=5, 8, 8, 128]   # mask latents (Stage 1)
   │
   ├→ Text Encoder (T5-base, frozen) + linear projection to d_model
   │     [B, L_text] → [B, L_text, 768] → [B, L_text, 2048]   # c_text
   │
   ├→ Normalize & Interpolate & Stack
   │     channel-wise norm:     z̄ = (z - μ_VAE) ⊘ σ_VAE
   │     temporal interp to T̂:  ẑ ∈ [B, V, T̂=?, 8, 8, 128]    # canonical latent rate
   │     stack over V views, flatten (T̂, H', W') into tokens
   │     linear proj 128 → 2048
   │     Output token sequence: [B, N_tok, 2048]
   │     N_tok = V · (n+τ) · H' · W' = 2 · 9 · 8 · 8 = 1152  (when T̂ = n+τ)
   │
   ├→ Apply conditioning mask  b ∈ {0,1}^(n+τ)   (memory slots b=1, future slots b=0)
   │     z̃_s   = (1−s)·ẑ^m + s·ε                    # noised future at level s
   │     x_s   = b ⊙ ẑ^o + (1−b) ⊙ z̃_s              # composite latent sequence
   │     Shape: [B, 1152, 2048]
   │
   ├→ DiT-style Mask Dynamics Backbone (×N=28 transformer blocks)
   │     For each block ℓ ∈ {1,...,28}:
   │        AdaIN modulation:  x ← RMSNorm(x) ⊙ (1+α(s)) + β(s)        ; s injection
   │        Self-Attention:    x ← x + SelfAttn(x)  with 3D RoPE(γ_t·t, γ_h·h, γ_w·w)
   │        Cross-Attention:   x ← x + CrossAttn(Q=x, K=V=c_text)      ; text cond
   │        Feed-Forward:      x ← x + FFN(x)
   │        Cross-view mixing layer at ℓ ∈ {0, 3, 6, ..., 27}
   │        Cache hidden state h^(ℓ) ∈ [B, 1152, 2048] into bank H_t = {h^(1),...,h^(28)}
   │     Final hidden:  x_N ∈ [B, 1152, 2048]
   │
   ├→ [Stage 1 Branch]  Mask Decoder  (Stage 1 only, supervises future slots)
   │     gather (1-b) future slots from x_N:    [B, V·τ·H'·W' = 640, 2048]
   │     reproject 2048 → 128 and reshape:      [B, V=2, τ=5, 8, 8, 128]  # predicted v_θ
   │     L_mask = E[ w(s) · || v_θ(z_s, s, c_t) − (z_1 − z_0) ||^2 ]   # over (1-b) only
   │
   └→ [Stage 2 Branch]  Mask-Guided Diffusion Policy
         build action-state input:  u_t = [a_t, s_t]              [B, H_a=36, 15]
         linear projection 15 → d_act=512:                         [B, 36, 512]
         add noise:  ũ = u_t + σ·ε                                 [B, 36, 512]
         
         Action Expert (28-layer parallel transformer; d_act=512, 16 heads, cross-attn dim=2048)
         For each layer ℓ ∈ {1,...,28}:
            ũ ← ũ + SelfAttn(ũ)                                    [B, 36, 512]
            ũ ← ũ + CrossAttn(Q=W_Q·ũ, K=W_K·h^(ℓ), V=W_V·h^(ℓ))   # backbone layer ℓ
            ũ ← ũ + FFN(ũ)                                         [B, 36, 512]
         
         Action Decoder:  [B, 36, 512] → linear → [B, 36, 8]       # (Δx, Δθ, gripper)
         
         L_act = E[ λ(σ) · || ϕ_ξ(ũ, σ, H_t) + ε/σ ||^2 ]
         
         Inference: 10-step Euler discrete diffusion → 36-step action chunk
                    Receding Horizon Control: execute first action a_0, replan next step
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Shared Video VAE & Mask Rendering

**Function:** 把多視角 RGB 觀測與離散語意 mask 統一編碼到同一個連續潛在空間，避免修改預訓練 VAE 並提供一致的 context/target 介面。

**Input:**
- Name: `o_t`（RGB memory）, `m_t`（離散語意 mask, Stage 1 only）
- Shape: `o_t ∈ [B, V=2, n=4, 3, H=256, W=256]`，`m_t ∈ {0,1}^{H×W×C}` per frame
- Source: 多視角相機（third-person + wrist）、RoboEngine 離線標註（real-world）或模擬器（LIBERO/RLBench）

**Output:**
- Name: `z^o`（RGB latents）, `z^m`（mask latents, Stage 1 only）
- Shape: `z^o ∈ [B, V, n, H'=8, W'=8, D=128]`，`z^m ∈ [B, V, τ=5, 8, 8, 128]`
- Consumer: Norm & Interpolate & Stack 模組

**Processing:**

1. **Mask rendering**：將離散 mask $m_t \in \{0,1\}^{H\times W\times C}$ 透過固定 color palette 映射到 RGB-compatible image $\tilde{m}_t \in [0,1]^{H\times W\times 3}$，每個 semantic region 一個獨特顏色（機械臂/夾爪 vs. 任務相關物體）。
2. **Encoding**：以同一個凍結預訓練 3D VAE 的 encoder $E$ 分別編碼 $o_t$ 與 $\tilde{m}_t$（Eq. 1）：
   $$z^o_t = E(o_t),\quad z^m_t = E(\tilde{m}_t)$$
3. **Compression**：spatial 壓縮率 $f_s=32$（256/32 = 8），temporal 壓縮率 $f_t=8$（依賴於輸入時間長度的具體對應，paper 未給出 $n=4$ memory frames 與 $\tau=5$ future latents 在 ft=8 下的精確對齊規則）。

**Key Formulas:**

$$z^o_t = E(o_t),\quad z^m_t = E(\tilde{m}_t)$$

**Implementation Details:**
- VAE 在 Stage 1 與 Stage 2 全程**凍結**（appendix Table 6）。
- Color palette 為固定不可學的查找表，Real-world 任務透過 RoboEngine 離線生成 pixel-wise mask，模擬器則直接讀取真值 mask。
- 影像 resize 到 256×256，normalize 到 $[-1, 1]$ 後送入 VAE。
- $f_t=8$ 與 $n=4, \tau=5$ 的精確時間對應在論文正文未具體展開；附錄僅給出 $\gamma_t \approx 0.267$ 作為 RoPE interpolation scale，暗示 latent frame rate 與 RGB frame rate 之間的 phase 對齊已透過 RoPE 補償。

#### 5.3.2 Normalize & Interpolate & Stack（Latent Tokenization）

**Function:** 將不同視角、不同時間長度的 VAE latents 規範化、重採樣到固定 latent frame rate，並打包成 transformer 可吃的固定長度 token 序列，取代傳統的 pixel-space 3D patchification。

**Input:**
- Name: `z^o`, `z^m`
- Shape: `[B, V, n, 8, 8, 128]`、`[B, V, τ, 8, 8, 128]`
- Source: Shared Video VAE

**Output:**
- Name: tokenized sequence `x` 與 conditioning mask `b`
- Shape: `x ∈ [B, N_tok = V·(n+τ)·H'·W' = 1152, d_model=2048]`，`b ∈ {0,1}^{n+τ}`
- Consumer: DiT-style Mask Dynamics Backbone

**Processing:**

1. **Channel-wise normalization**（Eq. 2），用 VAE 統計量穩定數值範圍：
   $$\bar{z} = (z - \mu_{\text{VAE}}) \oslash \sigma_{\text{VAE}}$$
2. **Temporal interpolation** 把每個視角 latents 沿時間維度重採樣到 canonical latent frame rate $\hat{T}$，使不同 subsampling rate 與 VAE compression artifact 下訓練更穩定。
3. **Stack & flatten**：把 V 個視角沿 view 軸 stack，再把 $(\hat{T}, H', W')$ flatten 成 token 序列。
4. **Linear projection** 把 channel 維度 128 映射到 DiT hidden dim 2048。
5. **Conditioning mask** $b \in \{0,1\}^{n+\tau}$ 標記 memory slots（$b=1$，clean）vs. future slots（$b=0$，noised）。

**Key Formulas:**

$$\bar{z} = (z - \mu_{\text{VAE}}) \oslash \sigma_{\text{VAE}}$$

$$x_s = b \odot \hat{z}^o_{t-n+1:t} + (1-b) \odot \tilde{z}_s,\quad \tilde{z}_s = (1-s)\hat{z}^m_{t+1:t+\tau} + s\epsilon,\ \epsilon \sim \mathcal{N}(0, I)$$

**Implementation Details:**
- Resolution 256×256，spatial latent 8×8，channel D=128。
- Normalize 統計量 $(\mu_{\text{VAE}}, \sigma_{\text{VAE}})$ 從 VAE 訓練資料估計，與 RGB/mask 共用同一組（因兩者經 VAE 編碼後落在相同分布）。
- N_tok = 1152 假設 $\hat{T} = n + \tau = 9$；若 interpolation 後 $\hat{T}$ 不同，則 N_tok 需依 $\hat{T}$ 調整（paper 未明確列出 $\hat{T}$ 的具體值）。

#### 5.3.3 DiT-style Mask Dynamics Backbone

**Function:** 以 conditional flow matching 處理 normalized latent token 序列，學習從 RGB memory + 語言條件預測 future mask latents 的 velocity field，同時在每層快取 hidden state 形成 Predictive Feature Bank 供 policy head 消費。

**Input:**
- Name: token sequence `x`, text embedding `c_text`, timestep `s`
- Shape: `x ∈ [B, 1152, 2048]`, `c_text ∈ [B, L_text, 2048]`, `s ∈ [B]`
- Source: Tokenization 模組（x, b）；T5-base + linear proj（c_text）；採樣（s）

**Output:**
- Name: 最終 hidden `x_N`，多層 Predictive Feature Bank `H_t`
- Shape: `x_N ∈ [B, 1152, 2048]`，`H_t = {h^(1), ..., h^(28)}, h^(ℓ) ∈ [B, 1152, 2048]`
- Consumer: Mask Decoder（Stage 1）、Action Expert cross-attention（Stage 2）

**Processing:** 每個 transformer block（共 N=28 層）依序執行：

1. **AdaIN-style timestep modulation**（Eq. 7）：先 RMSNorm，再依 timestep embedding $s$ 做 element-wise scale-shift；$\alpha(s), \beta(s)$ 由 trainable scale-shift table 與 timestep projection 組合產生。
2. **Self-Attention with 3D RoPE**（Eq. 6）：對 token 的 $(t, h, w)$ 座標套用 3D Rotary Positional Embedding，並用 interpolation scale $\gamma=(\gamma_t, \gamma_h, \gamma_w)$ 補償 VAE 壓縮（附錄：$\gamma_t \approx 0.267, \gamma_h = \gamma_w = 32$）。
3. **Cross-Attention** 把 text embedding 作為 K/V 注入。
4. **Feed-Forward** layer。
5. **Cross-view mixing** 在 $\ell \in \{0, 3, 6, ..., 27\}$（每 3 個 block 一次，共 10 層）執行，使 third-person 與 wrist 之間資訊交流。
6. **Cache hidden state** $h^{(\ell)}$ 至 Predictive Feature Bank。

**Key Formulas:**

$$\bar{x} = \text{RMSNorm}(x),\quad \text{Modulate}(\bar{x}; s) = \bar{x} \odot \bigl(1 + \alpha(s)\bigr) + \beta(s)$$

$$\text{RoPE}(t, h, w) \leftarrow \text{RoPE}(\gamma_t\, t,\ \gamma_h\, h,\ \gamma_w\, w)$$

$$L_{\text{mask}} = \mathbb{E}\Bigl[ w(s)\,\bigl\| v_\theta(z_s, s, c_t) - (z_1 - z_0) \bigr\|_2^2 \Bigr]\quad (\text{僅在 } (1-b) \text{ slots 上計算})$$

**Implementation Details:**
- Layers N=28，hidden dim 2048，heads 32。
- Stage 1 學習率 $3 \times 10^{-4}$，AdamW，batch 128 (global)，warmup 1000 步，gradient clip 1.0，bfloat16，DeepSpeed ZeRO-2，8× A100 (80GB) 約 30k 步 / 3.5 天。
- Caption dropout $p=0.06$，conditioning frame 注入輕微 noise (0.1) 增強 robustness。
- Cross-view mixing 的具體 attention 結構（shared QKV vs. dedicated）論文未在正文展開，僅在附錄列出層 index。

#### 5.3.4 Mask Decoder（Stage 1）

**Function:** 在 Stage 1 將 backbone 輸出的 future-slot tokens 解碼回 mask latent 空間，並提供 flow matching 訓練的監督訊號；Stage 2 不使用此模組。

**Input:**
- Name: `x_N`, conditioning mask `b`
- Shape: `x_N ∈ [B, 1152, 2048]`, gather (1-b) → `[B, V·τ·H'·W' = 640, 2048]`
- Source: DiT backbone 最後一層輸出

**Output:**
- Name: 預測的 velocity field `v_θ`
- Shape: `[B, V=2, τ=5, H'=8, W'=8, D=128]`
- Consumer: $L_{\text{mask}}$ loss（無下游模組）

**Processing:**

1. 依 conditioning mask 從 `x_N` gather 出 future slots。
2. Linear projection 把 hidden dim 2048 反投影到 VAE latent channel 128。
3. Reshape 成 `[B, V, τ, H', W', D]`，作為對 mask latent velocity field $v_\theta$ 的預測。
4. 與 ground-truth velocity $z_1 - z_0$（其中 $z_0 = \hat{z}^m$ clean target、$z_1 \sim \mathcal{N}(0, I)$）比對，計算 weighted MSE。

**Key Formulas:**

$$z_s = (1 - s)\, z_0 + s\, z_1,\quad s \in [0, 1]$$

$$L_{\text{mask}} = \mathbb{E}\Bigl[ w(s)\,\bigl\| v_\theta(z_s, s, c_t) - (z_1 - z_0) \bigr\|_2^2 \Bigr]$$

**Implementation Details:**
- $L_{\text{mask}}$ 只在 $(1-b)$ 的 future slots 上累加，memory slots 不參與 loss。
- Loss weighting $w(s)$ 的具體形式 paper 未在正文給出，附錄亦未詳述。
- Stage 2 開始後此模組停用，未進行 auxiliary mask loss（與「附錄比較加 auxiliary mask loss」之 ablation 對照）。

#### 5.3.5 Mask-Guided Diffusion Policy（Action Expert + Action Decoder）

**Function:** 以 backbone 各層 predictive features 為條件，在動作空間執行 conditional denoising 生成動作 chunk；Stage 2 訓練時 gradient 同時更新 backbone 使 features 更 control-aligned。

**Input:**
- Name: action chunk `a_t`、proprio state `s_t`、Predictive Feature Bank `H_t`、noise level `σ`、noise `ε`
- Shape: 組合輸入 `u_t = [a_t, s_t] ∈ [B, H_a=36, 15]`（7-DoF pose + 1-DoF gripper + 7-DoF state）；`H_t = {h^(ℓ) ∈ [B, 1152, 2048]}_{ℓ=1..28}`
- Source: 示範資料（$u_t$）、DiT backbone（$H_t$）、噪聲採樣（$\sigma, \epsilon$）

**Output:**
- Name: 預測動作 chunk
- Shape: `[B, H_a=36, 8]`（$\Delta x, \Delta \theta, \text{gripper}$）
- Consumer: Receding Horizon Controller（執行第 1 個動作後 replan）

**Processing:**

1. **Action token 構建**：把 action 與 proprio state 串接 $u_t = [a_t, s_t]$，linear projection 15 → 512 得到 action tokens。
2. **加噪**：$\tilde{u} = u_t + \sigma \epsilon$，其中 $\epsilon \sim \mathcal{N}(0, I)$。
3. **Action Expert (28 層 parallel transformer)**：每層 $\ell$ 依序執行 self-attention、**cross-attention 對應到 backbone 第 $\ell$ 層的 $h^{(\ell)}$**（K, V 來自 backbone hidden state）、FFN。
4. **Action Decoder**：linear projection 512 → 8，輸出去噪後的動作 chunk。
5. **訓練**：以 $L_{\text{act}}$ 端到端訓練；論文 §3.5 指出 backbone 在 Stage 2 與 action expert **聯合訓練**（gradient 流回 backbone），但附錄 A.1 描述 cross-attention 從「frozen DiT backbone」抽取 features —— 兩處用詞略有出入，較可能的解讀是：backbone 仍隨梯度更新，但在 cross-attention 看來其 KV 是當前 forward 的 features。
6. **推論**：Receding Horizon Control，10-step Euler discrete diffusion 採樣完整 36-step chunk，執行第 1 個動作後在下一時間步 replan。

**Key Formulas:**

$$\tilde{u} = u + \sigma\, \epsilon,\quad \epsilon \sim \mathcal{N}(0, I)$$

$$L_{\text{act}} = \mathbb{E}\Bigl[ \lambda(\sigma)\,\bigl\| \phi_\xi(\tilde{u}, \sigma, H_t) + \epsilon/\sigma \bigr\|_2^2 \Bigr]$$

**Implementation Details:**
- Layers 28，hidden dim 512，heads 16，cross-attn dim 2048（與 backbone 對齊），action chunk $H_a=36$。
- Stage 2 學習率 $5 \times 10^{-5}$（比 Stage 1 低）、batch 128 (global)，warmup 1000、gradient clip 1.0、bfloat16、AdamW；text dropout 在 Stage 2 停用。
- Stage 2 訓練 ~18k 步 / 1.5 天 per task suite（8× A100）。
- 動作空間 15-dim 為訓練輸入（含 7-DoF state），實際輸出可執行動作為 7-DoF pose + 1-DoF gripper（共 8-DoF）；論文正文與附錄對最終 decoder 輸出維度的描述可由「(Δx, Δθ, gripper) ×N」推得為 8-DoF。
- $\lambda(\sigma)$ 的具體 weighting schedule 論文未在正文展開。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| LIBERO (Liu et al., 2023) | Language-conditioned 模擬桌面操作，含 Spatial / Object / Goal / Libero-10 四個 suite | 130 個任務（每個 evaluation suite 10 個任務），主結果以每 suite 500 episodes 評估 | Train 用於 Stage 1+2；驗證用 held-out validation split 做 checkpoint selection；測試以隨機 seed 重複 500 episodes |
| RLBench (James et al., 2019) | Tabletop 多視角語言指令操作，主表報告 6 個代表性任務 | 100 個任務，本文評估 6 個任務（Sweep to Dustpan、Phone on Base、Umbrella Out、Frame off Hanger、Wine at Rack、Water Plants），每任務 20 episodes | Train/val 取自原 benchmark；測試以 best validation checkpoint 在 20 個 randomized episodes 評估 |
| Real-world Franka 任務集 | 4 個語言條件操作任務：(1) bread+hotdog→basket、(2) open drawer→put pen、(3) pour water→bowl、(4) book→shelf | 每任務 50 條 demonstrations；mask 由 RoboEngine (Yuan et al., 2025) 離線標註 | Per-task post-training 用 50 demos；測試每任務 20 trials；Visual generalization 額外在 BG / Light / Color 三種 shift 下各跑 20 trials |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| Success Rate (SR) | 成功 episode 比例，分別在 LIBERO（500 eps/suite）、RLBench（20 eps/task）、real-world（20 trials/task）上回報 | yes |
| OOD-SR | 在 BG / Light / Color 三種 appearance shift 下的平均 SR：$\text{OOD-SR} = \frac{1}{|C|} \sum_{c \in C} \text{SR}_c$ | yes |
| Retain | 將 OOD 表現相對 in-distribution 表現正規化：$\text{Retain} = \text{OOD-SR} / \text{SR}_{\text{ID}}$ | no |
| nPAUC (normalized Pruning AUC) | 對 random visual token pruning 的 robustness 摘要：$\text{nPAUC} = \frac{1}{|S||R|} \sum_{s \in S} \sum_{r \in R} \frac{\text{SR}_s(r)}{\text{SR}_s(0)}$，$R = \{0.1, \dots, 0.9\}$，$S$ 為四個 LIBERO suite | no |

### 6.3 Training and Inference Settings

訓練於 8× NVIDIA A100 (80GB) cluster，使用 DeepSpeed ZeRO-2；Stage 1 約 3.5 天 / 30k steps，Stage 2 每個 task suite 約 1.5 天 / 18k steps（Appendix A.2）。Optimizer 為 AdamW，Stage 1 learning rate $3 \times 10^{-4}$、Stage 2 為 $5 \times 10^{-5}$，weight decay $1 \times 10^{-5}$，warmup 1000 steps，gradient clip 1.0，batch size 128 (global)，bfloat16 精度（Table 6）。Backbone 為 28-layer DiT（hidden 2048、32 heads），action expert 為 28-layer transformer（hidden 512、16 heads），cross-view attention 每 3 個 block 插入一次（indices 0, 3, …, 27），text encoder 為 T5-base 投影至 2048 維（Appendix A.1）。Stage 1 memory window $n=4$ frames、預測 $\tau=5$ future latent frames，caption dropout $p=0.06$、conditioning frame noise injection 0.1；Stage 2 凍結 VAE、僅以 $\mathcal{L}_{\text{act}}$ 監督，action chunk $H_a=36$、action 維度 15（7-DoF pose + 1-DoF gripper + 7-DoF state）。VAE 將 256×256 RGB 壓成 8×8 latent patch，$f_s=32$、$f_t=8$，3D RoPE 使用 $\gamma = (\gamma_t \approx 0.267, \gamma_h=32, \gamma_w=32)$（Appendix A.1）。所有實驗使用固定 seed 42。Inference 採 Receding Horizon Control，10-step Euler discrete diffusion sampling 出 36-step action chunk，僅執行第一個 action 後於下一 timestep 重新規劃；real-world 部署以 10Hz 在 raw RGB 上執行（Appendix B）。

### 6.4 Main Results

LIBERO（Table 1，每 suite 500 episodes，3rd+wrist 視角）：

| Method | Spatial | Object | Goal | Libero-10 | Avg. | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| OpenVLA | 0.847 | 0.884 | 0.792 | 0.537 | 0.765 | RGB / 3rd |
| CogACT | 0.972 | 0.980 | 0.902 | 0.888 | 0.936 | RGB / 3rd |
| Cosmos w/ IDM | 0.768 | 0.750 | 0.694 | 0.488 | 0.675 | RGB world model / 3rd |
| Cosmos w/ Latent IDM | 0.948 | 0.992 | 0.892 | 0.842 | 0.919 | RGB world model / 3rd |
| $\pi_0$ | 0.968 | 0.988 | 0.958 | 0.852 | 0.942 | RGB / 3rd+wrist |
| GE-ACT | 0.982 | 0.976 | 0.958 | 0.944 | 0.965 | RGB world model / 3rd+wrist |
| **MWM (ours)** | **0.988** | **1.000** | **0.982** | **0.960** | **0.983** | Mask / 3rd+wrist |

RLBench（Table 2，best validation checkpoint，20 episodes/task）：

| Method | Sweep to Dustpan | Phone on Base | Umbrella Out | Frame off Hanger | Wine at Rack | Water Plants | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OpenVLA | 50.0% | 20.0% | 35.0% | 15.0% | 10.0% | 10.0% | 23.3% |
| $\pi_0$ | 30.0% | 30.0% | 30.0% | 70.0% | 10.0% | 30.0% | 33.3% |
| GE-ACT | 10.0% | 15.0% | 40.0% | 35.0% | 40.0% | 45.0% | 30.8% |
| CogACT | 50.0% | 50.0% | 55.0% | 45.0% | 30.0% | 25.0% | 42.5% |
| FiS-VLA | 55.0% | 50.0% | 50.0% | 70.0% | 55.0% | 20.0% | 50.0% |
| **MWM (ours)** | **55.0%** | **55.0%** | **85.0%** | **75.0%** | **90.0%** | **50.0%** | **68.3%** |

Real-world Franka（Table 4，每任務 50 demos post-train、20 trials）：

| Method | Task1 | Task2 | Task3 | Task4 | Avg. |
| --- | --- | --- | --- | --- | --- |
| GE-ACT | 35% | 20% | 10% | 30% | 23.8% |
| $\pi_0$ | 50% | 30% | 5% | 70% | 38.8% |
| **MWM (ours)** | **75%** | **55%** | **60%** | **80%** | **67.5%** |

Visual generalization（Table 3，跨 4 任務 × 20 trials/condition 的平均）：

| Method | SR$_{\text{ID}}$ | BG | Light | Color | OOD-SR | Retain |
| --- | --- | --- | --- | --- | --- | --- |
| GE-ACT | 23.8% | 3.8% | 18.8% | 15.0% | 12.5% | 0.53 |
| $\pi_0$ | 38.8% | 13.8% | 17.5% | 26.3% | 19.2% | 0.49 |
| **MWM (ours)** | **67.5%** | **27.5%** | **56.3%** | **42.5%** | **42.1%** | **0.62** |

Token pruning robustness（Table 5，nPAUC over $r \in \{0.1, \dots, 0.9\}$ × 4 LIBERO suites）：

| Method | nPAUC ↑ |
| --- | --- |
| GE-ACT | 0.629 |
| **MWM (ours)** | **0.648** |

### 6.5 Ablation Studies

- **MWM-C1（顯式 future-mask 解碼 + 獨立 IDM）vs Cosmos w/ IDM**：把 RGB world model 換成預測 semantic mask，LIBERO 平均 SR 由 0.675 提升到 0.810，long-horizon LIBERO-10 由 0.488 提升到 0.704。此 ablation 直接比較「同樣是 future prediction + IDM 架構，差別只在 RGB vs mask」，能診斷 representation shift 本身的價值，屬於有意義的對照。
- **MWM-C2（predictive latent feature + diffusion policy，不顯式解碼 mask）vs Cosmos w/ Latent IDM**：在 latent feature 方案上同樣比較 RGB vs mask，平均 SR 由 0.873（論文文字所述，表中為 0.919）提升至 0.918，Goal 與 LIBERO-10 改善明顯；論文以此論證在 semantic 空間中學 predictive feature 比在 RGB latent 空間更貼近控制需求。屬於診斷性 ablation。
- **MWM-C2 vs MWM-C1**：兩者都是 mask-centric，差別在是否顯式解碼 mask 再以 IDM 推 action。MWM-C2 由 0.810 提升至 0.918，支持「直接用 predictive latent feature」可避免顯式 mask rollout 與獨立 IDM 帶來的誤差傳播。屬於針對「explicit decode 還是 latent feature」這個設計選擇的診斷實驗。
- **MWM (3rd+wrist) vs MWM-C1/C2 (僅 3rd)**：加入 wrist 視角後 SR 由 0.918 升到 0.983；不過此 ablation 同時改變了「視角數」與「最終端到端設計」，無法單獨歸因於 mask backbone 設計，更像是 system-level upgrade 而非元件級別 diagnostic。
- **Stage-2 設計選擇（auxiliary mask loss、無 Stage-1 init）**：論文於 §3.5 明確說 appendix 會比較「Stage 2 加 auxiliary mask loss」與「不用 Stage-1 初始化、從零訓 policy」，但提供的 appendix（A–E）並未給出對應數據；因此此關鍵 ablation 在現有內容中 the paper does not specify。
- **Random token pruning（Table 5、Tables 7–8）**：嚴格而言這是 robustness stress test 而非元件 ablation；在 $r \le 0.5$ 區間 MWM 與 GE-ACT 大致相當，差距集中在中段 pruning ratio，且 nPAUC 差異僅 0.629 → 0.648，邊界較窄，較像 sanity-style 的 robustness probe，未能單獨診斷哪個設計元件帶來抗剪枝能力。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — LIBERO 上比較 $\pi_0$、GE-ACT、CogACT、Cosmos w/ Latent IDM 等近期 generalist VLA 與 video world model baselines（Table 1），RLBench 另比 FiS-VLA（Table 2）。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同時在 LIBERO（4 suites）、RLBench（6 tasks）與 real-world Franka（4 tasks）上評估，並追加 BG/Light/Color OOD shift（Tables 1–4、Table 3）。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — MWM-C1 / MWM-C2 / 完整 MWM 之間的對照能診斷「mask vs RGB」與「explicit decode vs latent feature」兩個設計選擇，但論文承諾的 Stage-2 auxiliary mask loss 與 from-scratch 比較未出現於 appendix；多視角影響也與架構升級綁在一起。
- [missing] Has a scaling study (size, length, or compute) — 文中未報告模型尺寸、demo 數量、訓練步數或 context 長度的 scaling 曲線；唯一近似量化的「壓力測試」是 token pruning，但那是 robustness 而非 capability scaling。
- [missing] Has an efficiency / wall-clock comparison — 僅於 Appendix A.2 提及自身訓練時間（Stage 1 約 3.5 天、Stage 2 約 1.5 天），未與 baselines 比較推論延遲、throughput 或 FLOPs。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 全文使用固定 seed 42（Appendix A.2），LIBERO 500 eps、RLBench 與 real-world 各 20 trials 皆只報告單點 SR，未報告 std 或多 seed 的不確定度。
- [partial] Releases code / weights / data sufficient for reproducibility — Abstract 提供 code repo 連結（github.com/LYFCLOUDFAN/mask-world-model），Appendix A 給出主要 hyperparameters 與硬體設定；但未明確說明是否釋出 pretrained weights、real-world demonstration 資料與 RoboEngine 標註流程細節。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

**Claim 1（§1, p.2）**: 「MWM forecasts future semantic masks internally and runs purely on raw RGB at inference, using semantic supervision only during training」。
- **Supported**: §3.3 的 pipeline 與 §4.2 的 real-world deployment 描述明確說明測試時只吃 multi-view RGB；這是 engineering claim，protocol 可直接驗證。

**Claim 2（§1, p.2）**: 「mask-guided diffusion policy ... provides stronger control utility than RGB-centric prediction by emphasizing dynamics-relevant structure」。
- **Partially supported**: Tables 1, 2, 4 上 MWM 對 π0、GE-ACT 的絕對 SR 領先在 LIBERO（+1.8 pt）、RLBench（+35 pt）、Real-world（+28.7 pt）一致為正，且 Table 3 OOD-SR 42.1% vs 19.2% 提供了 robustness 佐證。但「stronger control utility ... emphasizing dynamics-relevant structure」屬機制性宣稱，目前沒有直接的表徵或干涉實驗支撐，只能由下游 SR 反推。

**Claim 3（§1, p.2）**: 「mask-centric designs consistently outperform future RGB prediction, which highlights that the performance gains primarily arise from the shift in representation and objectives, rather than reliance on a specific architectural design」。
- **Overclaimed**: 同相機條件下，MWM-C1 vs Cosmos w/ IDM 的 0.810 vs 0.675 (Table 1, p.6) 確實成立；但 MWM-C2 vs Cosmos w/ Latent IDM 在 Table 1 的 avg 為 0.918 vs 0.919（基本持平、甚至落後 0.001），與正文「0.873→0.918」描述不符。三個 mask 變體中只有兩個是同相機，且其中一個對照變成了「持平」而非「outperform」，「consistently」一詞並不嚴謹。

**Bonus claim（§4.3.1, p.7）**: 「semantic bottleneck ... makes the policy less sensitive to missing visual tokens」。
- **Partially supported**: nPAUC 0.648 vs 0.629 數值上勝出，但相對差距 ~3%；且兩者在 $r \geq 0.7$ 同時崩潰 (Tables 7–8, p.14)，因此「less sensitive」應限定在中度 pruning。

### 7.2 Fundamental Limitations of the Method

**離線標註管線是硬需求，部署 domain 受限。** Stage 1 全靠 RoboEngine 提供 pixel-wise semantic mask；任何沒有可靠 segmenter 可標註的場景（變形物、半透明物、無預訓練類別、密集堆疊的小零件）都拿不到訓練訊號。這不是「之後改用 self-supervised 即可」的工程問題，而是「mask 預測作為訓練目標」的本體論依賴：若世界中不能被乾淨切割成「robot 與 task-relevant objects」，整個 information bottleneck 假設就失效。

**mask 作為 bottleneck 會主動拋棄細粒度任務所需的紋理／材質資訊。** 把預測目標限制在 semantic mask 等於宣告「policy 不需要看顏色／紋理」；但很多任務需要 reading text on objects、區分同形狀但材質不同的物體（玻璃 vs 塑膠杯）、判斷食物熟度／液體濃稠度。在這些場景下 geometric bottleneck 從 feature 變 bug，paper 未討論這個邊界。

**監督只發生在很短的 horizon ($\tau=5$ latent frames) 上，但 closed-loop control 是長 horizon。** §3.5 設定 memory $n=4$、future $\tau=5$（共 9 frames），而 Stage 2 完全移除 $L_{\text{mask}}$。也就是說「semantic lookahead」只是一個非常局部的 cue，paper 主張的「long-horizon foresight」並未被預測目標本身保證，所有長序列 robustness 都得仰賴 Stage 2 微調過的隱式 representation。

**Two-stage 訓練讓 backbone 在 Stage 2 偷偷漂移，但 paper 從未量化。** Stage 2 完全靠 $L_{\text{act}}$ 反向梯度更新 backbone (§3.5)。理論上會使 backbone 從「mask predictor」逐步退化成「action conditioner」；當 representation 趨向 action-specific 後，原先對 OOD appearance 的不變性也可能跟著消失。Paper 沒有報告 Stage 2 後 mask prediction loss 是否仍維持，也沒有 Stage 2 不同步數下的 OOD 曲線——「mask 預測帶來的 OOD 韌性」與「action loss 微調」之間的取捨被當成黑箱。

### 7.3 Citations Worth Tracking

- **Berg et al. 2025, "Semantic World Models" (arXiv 2510.19818)**: 同名概念前作，§1 只一句帶過；兩篇核心主張高度重疊，必讀以判斷 MWM 真正的 delta。
- **Seo et al. 2023, "Masked World Models for Visual Control" (CoRL)**: 同樣叫「masked world model」但採 masked autoencoding（input dropping），與 MWM 的 semantic mask prediction 在 mechanism 完全不同；釐清這層命名混淆很重要。
- **Wang et al. 2023, "Denoised MDPs" (arXiv 2206.15477)**: paper 用來支撐「RGB 含 nuisance variation」的核心引用；其表徵分離方法是 MWM 沒有正面對照的 baseline。
- **Yuan et al. 2025, "RoboEngine" (arXiv 2503.18738)**: MWM 整個 mask 標註管線的依賴來源；理解 RoboEngine 的失敗模式即理解 MWM 部署上限。
- **Liao et al. 2025, "Genie Envisioner / GE-ACT" (arXiv 2508.05635)**: 主要 RGB world-model baseline；理解其 video diffusion + action head 設計，才能準確判斷 mask 替換像素到底改了什麼。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] Table 1 中 MWM-C2 (3rd-only) avg 0.918 vs Cosmos w/ Latent IDM 0.919 究竟是哪一個成立？正文 0.873→0.918 的數據出處為何？這直接影響「mask vs RGB latent」claim 的方向。
- [ ] Stage 2 微調後 backbone 的 future mask prediction loss 變化多少？mask predictor 能力是被保留還是被「吸收」進 action representation？
- [ ] 把預測目標從 semantic mask 改為 depth、surface normal、或 optical flow，是否能拿到相當的 OOD-SR？geometric bottleneck 的關鍵是「semantic 標籤」還是「非 RGB 的 geometric channel」？
- [ ] 若推論時直接把 RoboEngine mask 餵進 input channel（mask-as-input baseline），對比 mask-as-target 還會領先多少？
- [ ] memory $n=4$、future $\tau=5$ 的短預測 horizon 是否限制了 long-horizon 任務？把 $\tau$ 拉長到 16+ 是否能進一步壓低 LIBERO-10 與真機長序列任務的失敗率？
- [ ] mask 渲染所用的 fixed color palette 對結果敏感嗎？把不同 semantic class 對映到同色或對映到 ImageNet 平均色，性能會塌嗎？
- [ ] RoboEngine 在新類別（透明物、變形物、生鮮食物）標註失敗時，MWM 的 SR 退化曲線長什麼樣？標註 noise 與 policy 性能的彈性係數有多少？

### 8.2 Improvement Directions

1. **修正並補齊 Table 1 同相機對照，加上 mask-as-input baseline 與 wrist-only / 3rd-only 配對。** 最低成本就能澄清「camera 數量 vs prediction target」與「mask 預測 vs mask 觀測」兩條獨立軸；訓練 pipeline 已備好，只需多訓幾個 head。也能順便釐清 §4.1 正文與 Table 1 的數據不一致。
2. **量化 Stage 2 後 backbone 的 mask prediction 損失。** 在 Stage 2 不同 epoch 取 checkpoint、回測 Stage 1 的 $L_{\text{mask}}$；若 mask 能力快速衰退，OOD 韌性可能來自其他源頭（如初始化或 cross-view attention），需要重審 paper 的因果敘事。
3. **將預測目標推廣為「semantic mask + depth + flow」混合 channel。** depth 與 flow 都能用同一個 shared VAE 流程編碼；若混合通道進一步提升 OOD-SR，就能驗證「geometric bottleneck」假設並放鬆對 RoboEngine 的依賴。
4. **以 self-supervised slot attention 或 SAM-2 取代 RoboEngine。** paper 已引用 Locatello et al. 2020 等 object-centric 方法；用 SAM-2 或 slot 模型直接生成 mask，可移除「pre-trained robot segmenter」這一單點依賴並擴大可訓練 domain。
5. **將 future horizon $\tau$ 從 5 拉長到 16–32 並加入 hierarchical mask supervision。** Long-horizon 任務（LIBERO-10、book→shelf）正是 paper 主張 mask 帶來最大增益處；若預測 horizon 與下游 RHC 的 $H_a=36$ chunk 對齊，foresight 與 control 也可進一步耦合。
6. **加入 information-theoretic probe 量化 latent 中 appearance vs geometry 比例。** 用 linear probing 對 latent 預測背景紋理／光照標籤，並對照 RGB world model 的同類 probe，把「bottleneck」從定性敘事轉為可驗證量。
