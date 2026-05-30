<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# LeWM — LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | LeWM |
| Paper full title | LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels |
| arXiv ID | 2603.19312 |
| Release date | 2026-03-24 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2603.19312 |
| PDF link | https://arxiv.org/pdf/2603.19312 |
| Code link | — |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Lucas Maes | Mila & Université de Montréal | https://lucas-maes.github.io/ | first author, corresponding author |
| Quentin Le Lidec | New York University | https://quentinll.github.io/ | co-first author |
| Damien Scieur | Mila & Université de Montréal; Samsung SAIL | — | co-author |
| Yann LeCun | New York University | — | co-author |
| Randall Balestriero | Brown University | — | co-author |

### 1.2 Keywords

Joint-Embedding Predictive Architecture, world model, self-supervised learning, representation collapse, SIGReg, latent planning, model predictive control, Vision Transformer

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| PLDM (Sobal et al.) | baseline | 唯一既有的 end-to-end JEPA 方法,以 VICReg 加上額外正則項學習表徵,訓練不穩且需多項超參數 |
| DINO-WM | baseline | 以凍結的 DINO 預訓練 vision encoder 為基礎的 latent world model,LeWM 主要與其比較規劃速度與成功率 |
| DreamerV4 (Hafner et al.) | baseline | task-specific、reward-driven 的 generative world model,以 reconstruction 為主要學習訊號 |
| TD-MPC | baseline | state-based、reward-reconstruction 的 task-specific world model,作為 LeWM 的對照分類 |
| JEPA (LeCun, 2022) | predecessor | 提出 Joint-Embedding Predictive Architecture 框架,LeWM 直接延續此 latent 預測學習路線 |
| SIGReg (Sketched Isotropic Gaussian Regularizer) | influence | 提供 LeWM 唯一使用的 anti-collapse 正則項,將 latent 投影至隨機方向上做 Epps–Pulley normality test |
| I-JEPA / V-JEPA | influence | 以 EMA 與 stop-gradient 預訓練 JEPA 表徵的代表方法,LeWM 強調無需此類啟發式 |

## 2. Research Overview

### 2.1 Research Topic

本研究探討如何從原始像素端到端地學習一個穩定的 latent world model。作者聚焦於 Joint-Embedding Predictive Architecture (JEPA) 此一以低維潛在空間預測未來為核心的框架,目標是不依賴 reward、不仰賴 image reconstruction、也不需要凍結的預訓練 vision encoder,即可在 2D 與 3D 控制任務中進行 latent planning。研究主題涵蓋 representation collapse 的防止機制、單 GPU 可訓練的緊湊架構設計、以 Cross-Entropy Method 在 latent space 進行 model predictive control 的決策框架,以及透過 probing 與 violation-of-expectation 評估 latent 空間是否編碼具物理意義的結構與直覺物理理解能力。

### 2.2 Domain Tags

- machine learning
- self-supervised representation learning
- world models
- model-based reinforcement learning
- robot learning

### 2.3 Core Architectures Used

- **Vision Transformer (ViT-Tiny) encoder**:作為 LeWM 的影像編碼器,將每張 frame observation $o_t$ 映射到低維 latent $z_t$,使用 patch size 14、12 層、3 個 attention heads、hidden dim 192,並取最後一層 [CLS] token 經 1-layer MLP + Batch Normalization 投影。
- **Transformer-based predictor**:6 層、16 個 attention heads、10% dropout 的因果 transformer,以 Adaptive Layer Normalization (AdaLN) 注入 action 條件,自迴歸地由 $(z_t, a_t)$ 預測下一步 latent $\hat{z}_{t+1}$。
- **Joint-Embedding Predictive Architecture (JEPA)**:LeWM 所延續的整體學習框架,將動態建模置於 latent space 而非 pixel space,僅以 next-embedding prediction 為主訊號。
- **SIGReg (Sketched Isotropic Gaussian Regularizer)**:本文唯一的 anti-collapse 正則項,將 latent 投影到 $M$ 個隨機單位方向上,並對每個一維邊際施以 Epps–Pulley normality test,藉 Cramér–Wold 定理保證聯合分布為各向同性高斯。
- **Cross-Entropy Method (CEM) latent MPC planner**:在訓練後固定 world model,於 latent space 中以 CEM 進行有限視界軌跡優化,並以 receding-horizon 方式重規劃,實現比 DINO-WM 快至 48× 的 planning。
- **ResNet-18 encoder (ablation)**:作為 ViT 之外的替代視覺骨幹,用於驗證 LeWM 對編碼器架構的不敏感性。
- **Decoder for latent visualization (post-hoc)**:訓練後額外搭建、不參與訓練 loss 的解碼器,僅用於將 latent 可視化以驗證表徵保留的場景資訊。

### 2.4 Core Argument

作者指出現有 JEPA 系列方法之所以難以穩定地端到端訓練,根本原因在於 next-embedding prediction loss 本身存在一個 trivial 解:encoder 將所有觀察映射到單一常數表徵即可零成本滿足預測目標,造成 representation collapse。為了避開此退化,既有工作不得不引入 stop-gradient、exponential moving average、預訓練 frozen encoder、reward 訊號、reconstruction 目標、proprioceptive 輸入或多項加權的 VICReg 變體等啟發式手段,代價是六個以上的 loss 超參數、缺乏理論收斂保證與訓練不穩定。作者主張真正需要的是一個能直接約束 latent 邊際分布、具有理論保證且結構簡潔的 anti-collapse 正則項。基於此邏輯,他們採用 SIGReg:將 latent 投影到隨機單位方向上,以 Epps–Pulley 統計量檢定每個一維邊際是否為高斯,並由 Cramér–Wold 定理推得當所有一維投影皆為高斯時,聯合分布即為各向同性高斯,自然排除常數塌縮解。此設計使得整個訓練目標僅由 prediction loss 加上 SIGReg 兩項組成,有效超參數壓縮為單一 $\lambda$,可用對數複雜度 bisection search 調整;並且不再需要 stop-gradient 或 EMA,所有梯度可端到端流經 encoder 與 predictor,在 15M 參數、單 GPU 條件下達成穩定訓練,進而支援快速 latent MPC 規劃。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

論文標題「LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels」一次點明三個關鍵主張：屬於 JEPA 家族、強調「stable end-to-end」訓練、且直接從 pixels 學起，不依賴預訓練視覺骨幹。Abstract 隨即把這三點轉化成具體的對比敘事：作者指出現有 JEPA 方法為了避免 representation collapse，普遍仰賴 multi-term loss、exponential moving averages、pre-trained encoders 或 auxiliary supervision，導致系統「fragile」。在這個問題框架下，LeWM 被定位為「the first JEPA」能完全 end-to-end 從 raw pixels 穩定訓練，且 loss 只剩兩項（next-embedding prediction loss 與 Gaussian 化的 regularizer），可調超參數從六個降到一個。Abstract 接著拋出三條量化亮點來支撐「便宜且強」這個敘事：15M 參數、單張 GPU 數小時、planning 比 foundation-model-based world model 快 48×。最後，Abstract 把貢獻從 control 任務延伸到「physical understanding」，預告 §5 會用 probing 與 surprise evaluation 來證明 latent space 編碼了有意義的物理結構。整段 Abstract 為後文鋪好「簡單／穩定／便宜／可解釋」四條主軸。

### 3.2 Introduction

(540 words)

Introduction 從一個高度抽象的 AI 願景開場：希望 agent 能直接從感官輸入（特別是 vision）以單一統一範式跨任務學習，而不依賴手工狀態表徵。作者把 World Models 定位為實現此願景的關鍵家族，因其讓 agent 能在「imagination space」中規劃並自我改善，特別契合 offline、無環境互動的設定。接著，文章把焦點收束到 JEPA：相較於完整重建環境，JEPA 只在 compact latent space 中預測未來，因而更聚焦於「relevant features」。

緊接著作者建立關鍵的問題敘事——JEPA 雖然概念簡單，卻 highly prone to collapse：模型會把所有輸入映射到幾乎相同的 representation 來作弊滿足 temporal prediction objective。這段設定了全文要解決的核心痛點，並帶出 Fig. 2 的方法分類圖：end-to-end 派（PLDM）需要許多 hyperparameters 且 anti-collapse 缺乏理論保證；foundation-based 派（DINO-WM）凍結預訓練 encoder 來避免 collapse 但失去 end-to-end 性質；task-specific 派（Dreamer、TD-MPC）依賴 reward 或 privileged state。LeWM 的賣點是「同時補足三個類別的缺點」：end-to-end、task-agnostic、pixel-based、reconstruction-free、reward-free，且只有一個超參數並具 provable anti-collapse。

論述策略上，Introduction 的次要敘事線是「降低門檻」：強調 LeWM 可在單張 GPU 訓練，這既是工程貢獻也是研究民主化的訴求，與 Abstract 的 15M 參數、單 GPU 一致。然後文章透過 Fig. 3 預告實證亮點——LeWM planning 0.98 秒、相對 DINO-WM 約 50× 加速；在 PushT 與 OGB-Cube 上，固定 FLOPs 預算下 success rate 顯著超越 DINO-WM。這些數字的功能是讓讀者在進入 Method 之前先相信「簡化方法不會犧牲性能」。

最後，Introduction 以 bullet 條列三項貢獻：(1) 提出可在單 GPU 訓練、兩項 loss、對架構與超參穩健、超參搜尋為對數時間複雜度的 end-to-end JEPA；(2) 在多樣 2D／3D 任務上以 15M 參數模型超越現有 end-to-end JEPA，且與 foundation-model-based 對手競爭，planning 最高快 48×；(3) 透過 probing 與 violation-of-expectation 評估 latent space 中的物理理解能力。這三項貢獻同時為後續 §3（Method 與 Latent Planning）、§4（Latent Planning Performance）與 §5（Quantifying Physical Understanding）三大實驗章節各鋪好一條敘事路線，使整篇 Introduction 既是動機 setup，也是論文結構的骨架。

### 3.3 Related Work / Preliminaries

(360 words)

Related Work 分成三條軸線，依序對應 LeWM 的三項定位主張。

第一條是 World Models 的 generative 派系。作者把 IRIS、DIAMOND、∆-IRIS、OASIS、DreamerV4 等視為 pixel-space generative simulator，能模擬 Minecraft、Counter-Strike、Crafter 等環境並提升 RL sample efficiency；Genie、HunyuanWorld 則代表生成全新可互動模擬器的方向。這段的論述功能是劃清界線：這些方法多假設可取得 reward signal、聯合建模 dynamics 與 value，而 LeWM 主動選擇 reward-free 設定，與 JEPA 線一致，目標是學「generic, task-agnostic」的 world model。

第二條是 JEPA 本身的演進。從 LeCun [5] 提出框架後，分支主要差在目標任務與避免 collapse 的策略。Self-supervised representation learning 一支（I-JEPA、V-JEPA、Echo-JEPA、Brain-JEPA）使用 EMA target encoder 與 stop-gradient 來防 collapse，但作者強調這些技巧「do not in general correspond to the minimization of a well-defined objective」，理論基礎薄弱。Action-conditioned latent world modeling 一支則分為兩類：依賴 pre-trained encoders（如 DINO-WM）以避免 collapse 但受限於預訓練表徵；以及 PLDM／VICReg 式 end-to-end 訓練，雖能聯合學表徵卻有 known training instabilities 與 scalability limitations。這段為 LeWM 的兩項 loss、Gaussian regularizer 設計打下對照背景，強調自家方法既 end-to-end 又有理論依據。

第三條是 Planning with Latent Dynamics，把 World Models 的使用方式拆成兩種：用 latent dynamics 做 RL policy training（Dreamer 系列），訓練完成後 world model 退出 control loop；以及在 test time 直接用 MPC 在 latent space 規劃（TD-MPC、DINO-WM、PLDM 等），world model 持續參與決策但計算成本較高。這段為 §3.2 Latent Planning 預埋伏筆——LeWM 採用後者 MPC 路線，因此 §4 中「planning speed」才會成為核心評估指標。

整體而言，Related Work 的功能不是單純列舉文獻，而是構造一個三維座標：reward 依賴度、是否 end-to-end、是否需 pre-trained encoder。在這個座標中，LeWM 被刻意定位在「reward-free × end-to-end × pixel-based」的角落，呼應 Fig. 2 並讓 §3 Method 自然成為填補此空缺的解。

### 3.4 Method (overview narrative)

(620 words)

§3 的整體敘事策略是「先設定學習問題，再給出最小可行方案，最後再說明如何用它做決策」。作者把 Method 章節拆成 §3.1 Learning the Latent World Model 與 §3.2 Latent Planning，分別對應「訓練」與「推論」兩個階段。

§3.1 開頭用一段 Offline Dataset 段落把問題設定講清楚：LeWM 處於 fully offline、reward-free 設定，只用 unannotated trajectories of observations 與 actions，呼應 §2 對 JEPA 的定位。這段刻意強調「behavior policies with no optimality requirements」，意思是訓練資料只需「足夠覆蓋環境動態」，不需專家示範或 reward，這同時是賣點，也限制了實驗評估的形態（goal-conditioned control 而非 reward maximization）。

接著 Model Architecture 段落描述兩個元件：一個 ViT encoder（tiny config，約 5M 參數，patch size 14，12 層、3 heads、hidden dim 192，從 last-layer [CLS] 取出 embedding 再經 1-layer MLP + BatchNorm 投影）以及一個 transformer predictor（6 層、16 heads、10% dropout，約 10M 參數，actions 透過 AdaLN 注入並初始化為零）。這裡的論述功能是讓讀者明白 LeWM 不是靠新奇架構取勝，所有元件都是現成構件；真正的貢獻在 loss 設計。投影層的 BatchNorm 設計是個小但關鍵的細節：因為 ViT 末端的 LayerNorm 會破壞 anti-collapse 目標，必須加投影抵消。

Training Objective 是 Method 的核心。作者把 loss 分成兩項：(1) prediction loss $L_{\text{pred}} = \|\hat z_{t+1} - z_{t+1}\|_2^2$，提供「可預測性」誘因；(2) anti-collapse 正則化 SIGReg，藉由 Cramér–Wold 把高維 normality test 化約為沿 $M$ 個隨機方向投影後的 univariate Epps–Pulley 統計量平均，使 latent 分佈逼近 isotropic Gaussian。完整 loss 是 $L_{\text{LeWM}} = L_{\text{pred}} + \lambda \, \text{SIGReg}(Z)$，只有兩個超參數 $M$ 與 $\lambda$，且作者宣稱 $M$ 對下游性能影響甚小，使 $\lambda$ 成為唯一有效超參，可用 bisection 以對數複雜度搜尋。Algorithm 1 提供約十行 pseudo-code，把訊息精煉到「結構簡單、可一頁實現」的程度。這段同時刻意對比 PLDM 的七項 loss，讓讀者直觀感受到「複雜度差距」。

§3.2 Latent Planning 把訓練好的 world model 接到決策環節。作者採取最簡單的選擇：在 latent space 跑 finite-horizon optimal control，cost 是「最終預測 latent state 與目標 latent embedding」之 squared distance $C(\hat z_H) = \|\hat z_H - z_g\|_2^2$；用 Cross-Entropy Method (CEM) 求解 $a_{1:H}^*$；以 receding-horizon MPC 緩解 auto-regressive rollout 累積誤差，每輪只執行前 $K$ 步即重新規劃。Fig. 4 用一張示意圖把整個 prediction–optimization 迴路圖像化。

整段 Method 的敘事邏輯是：先用「reward-free + offline」設定排除外部監督，再用兩項 loss 排除 collapse 與啟發式技巧，最後用 CEM + MPC 排除對額外 policy network 的需求——三層「拿掉東西」之後剩下的最小核心，就是 LeWM。這個 minimalism 也直接決定了 §4 的評估邏輯：在固定 FLOPs 與固定設定下比 success rate 與 planning time，因為這正是「簡化是否要付代價」的關鍵實驗問題。

### 3.5 Experiments (overview narrative)

(720 words)

實證章節橫跨 §4 Latent Planning Performance 與 §5 Quantifying Physical Understanding in LeWM，整體敘事分成三層問題：(1) 在多樣控制任務下 LeWM 是否與更複雜方法競爭？(2) 訓練動力學與超參設計是否真的更穩定簡單？(3) latent space 是否捕捉到有意義的物理結構？

§4.1 Planning evaluation setup 先建立評估場景。作者選了四個環境：Push-T（2D 推塊操作）、OGBench-Cube（3D 機械臂抓取）、Two-Room（2D 導航）、Reacher（DeepMind Control Suite 的 2-joint 夠到目標）。所有環境皆為連續動作空間，覆蓋 manipulation、navigation、locomotion 三類。Baselines 涵蓋兩條軸：JEPA 系（DINO-WM、PLDM）與通用 goal-conditioned offline 控制（GCBC、GCIVL、GCIQL）。重點比較對象是 PLDM（最接近的 end-to-end pixel JEPA，七項 loss）與 DINO-WM（凍結 DINOv2，但預設不給 proprioceptive 訊號以便公平比較）。為避免 per-environment 調參偏袒某方法，所有方法在所有環境共用一組超參。

§4.2 Towards Efficient Planning 是性能主敘事。在 PushT 上 LeWM 達 96% 成功率，超越 DINO-WM（74%）與 PLDM（78%），即便 DINO-WM 加上 proprioceptive 也僅 92%；Reacher 上 LeWM 86% 高於 PLDM 78%、DINO-WM 79%；OGBench-Cube 上 DINO-WM 86% 略勝 LeWM 74%，作者誠實歸因於該環境視覺更複雜且 3D 結構讓 encoder 訓練更難；Two-Room 上 LeWM 反而落後（87% vs PLDM 97%、DINO-WM 100%），作者主動承認這是 SIGReg 在 intrinsic dimensionality 過低資料集中的結構性弱點——把高維 latent 強制 Gaussian 化反而傷害了表徵。這種「主動指出不利結果」的敘事選擇強化全文可信度。Fig. 3 與 Fig. 6 共同證明：LeWM 在固定 FLOPs 下成績競爭，且 planning time 從 DINO-WM 的 47s 壓縮到 0.98s，達 48× 加速。

§4.3 Towards Stable Training 把焦點從「結果」轉到「過程」。Ablations 顯示：SIGReg 的內部參數（projections 數、integration knots 數）對性能幾乎無影響；embedding dim 過了某門檻就飽和；ResNet-18 替換 ViT 仍維持競爭力。這支撐了 §3 的「只有 $\lambda$ 是有效超參」聲明，並把超參搜尋從 PLDM 的 $O(n^6)$ 降到 $O(\log n)$。Training curves 部分以 Fig. 18／19 對比 LeWM 平滑單調的兩項 loss 與 PLDM 七項 loss 的 noisy、non-monotonic 行為，把「穩定」從口號落地為可視化證據。

§5 切換到「physical understanding」這條延伸戰線。§5.1 用 linear 與 MLP probes 從 latent embeddings 預測 Push-T 的 Agent Location、Block Location、Block Angle，LeWM 在 MLP 設定下的 Block Location 達 $r=0.999$、Block Angle $r=0.990$，全面勝過 PLDM 並逼近 DINO-WM——值得注意的是 DINO-WM 的優勢被作者解釋為 DINOv2 預訓練於 124M 圖片，因此把這個比較放在「不同公平性座標」上看。Decoding Latent Space 進一步用一個訓練後才接上的 decoder 從 192 維 [CLS] embedding 還原視覺場景（Fig. 8），證明即使從未用 reconstruction loss，latent 仍保留了足夠的物理狀態資訊。t-SNE 視覺化顯示 PushT latent 保留 spatial neighborhood structure。Temporal Latent Path Straightening 借用神經科學的 perceptual straightening 假說，發現 LeWM latent trajectories 在訓練中自然變直，甚至比有專門 temporal smoothness 正則的 PLDM 更直，是「emergent」現象。

§5.2 引入 violation-of-expectation 框架，在 TwoRoom、PushT、OGBench-Cube 三環境注入兩類擾動：visual perturbation（物體顏色突變）與 physical perturbation（物體傳送）。Fig. 10 顯示 LeWM 對 physical 擾動的 surprise（prediction MSE）顯著高於 visual 擾動（paired t-test, $p<0.01$），對 cube color 擾動則無顯著上升。這恰恰是想要的選擇性：模型對違反物理連續性的事件更敏感，對表面視覺變化較不敏感，符合直覺物理預期。整段實驗章節因此完成從「能控制」到「會理解」的論述閉環。

### 3.6 Conclusion / Limitations / Future Work

(310 words)

Conclusion 段落的功能是把整篇論文的論點壓縮成一段可記憶的總結，並順勢交代尚未解決的問題。作者重申 LeWM 是一個 stable end-to-end JEPA：encoder 把 image observations 映射到 latent space，predictor 在 embedding space 中以 action-conditioned 方式預測未來，兩者共同訓練。文章再度強調在多樣連續控制環境、僅用 raw pixel 輸入的條件下，LeWM 在「data efficiency、planning time、training time、stability」四項指標上勝過先前方法，同時保有競爭性的最終任務表現。穩定性與簡單性的根源被歸結為一個設計選擇：明確要求 latent embeddings 服從 isotropic Gaussian 以避免 collapse，這同時帶來 §5 觀察到的「principled training dynamics」與「interpretable and emergent representation properties」。這段並未引入新主張，而是把 §3、§4、§5 的論證收束到一句總結：LeWM 是現有 latent world model 的 scalable alternative。

Limitations & Future Work 段落主動點出三項弱點，且每項都直接對應一條未來研究方向，敘事節奏緊湊。第一，目前 latent world models 的 planning 只能處理短 horizon；hierarchical world modeling 被點名為解決長 horizon 推理與規劃的有望方向。第二，方法仍依賴具足夠互動覆蓋率的 offline dataset，採集成本高；更關鍵的是，當資料多樣性過低（intrinsic dimensionality 太小）時，SIGReg 在高維 latent 中強制 isotropic Gaussian 會失效——這正好回應 §4.2 中 Two-Room 表現下滑的觀察，使 limitations 與實證結果首尾呼應。作者建議透過大型多樣自然影片資料的 pre-training 提供更強表徵 prior，同時降低對特定領域資料的依賴。第三，現有 end-to-end latent world model 仍依賴 action labels 來預測未來狀態，這在實務上昂貴；解法方向是用 inverse dynamics modeling 學習 future action representations，以減少對顯式 action annotations 的依賴。整段透過「限制 → 對應方向」的對偶結構，把 LeWM 從「一篇結束的工作」轉化為「一個可繼續延伸的研究路徑」，為後續工作預留接口。

## 4. Critical Profile

### 4.1 Highlights

- LeWM 是首個僅用兩項 loss(next-embedding prediction + SIGReg)即可端到端從像素穩定訓練的 JEPA,將 PLDM 的 6 個 loss 超參數壓縮為單一 $\lambda$(Sec. 3.1, Eq. 3)。
- 模型僅 ~15M 參數,可在單張 NVIDIA L40S GPU 上於數小時內訓練完成(Sec. 1 contributions, App. D)。
- 在 Push-T 上,LeWM 規劃時間 0.98s,DINO-WM 為 47s,加速約 48×,主因是 LeWM 編碼產生的 token 數比 DINO-WM 少約 200×(Fig. 3)。
- Push-T 成功率:LeWM 96% > DINO-WM+proprioception 92% > PLDM 78% > DINO-WM 74%(Fig. 6),即使 LeWM 完全不使用 proprioceptive 輸入。
- Reacher 成功率:LeWM 86% > DINO-WM 79% > PLDM 78%(Fig. 6),為三個 JEPA 變體中最佳。
- 摒棄 stop-gradient、EMA、pre-trained frozen encoder 等啟發式技巧,梯度可端到端流經 encoder 與 predictor(Sec. 3.1)。
- $\lambda$ 為唯一有效超參數,可用 $O(\log n)$ bisection search 調整;PLDM 對應的網格搜尋為 $O(n^6)$(Sec. 4.3, App. G)。
- 在 Push-T 上,linear/MLP probing 顯示 LeWM 對 agent location、block location 的物理量恢復力與 DINO-WM(基於 DINOv2,預訓練於 ~124M 圖像)相當,且優於 PLDM(Tab. 1)。
- 即使 PLDM 內含明確的 temporal smoothness 正則項,LeWM 在訓練過程中仍展現出更高的 emergent temporal straightening,符合神經科學中的 perceptual straightening 假說(Sec. 5.1, Fig. 17, App. H)。
- Encoder 與 SIGReg 內部超參數(projection 數 $M$、integration knots 數)幾乎不影響下游成功率;ViT-Tiny 與 ResNet-18 表現相當(Tab. 8, Fig. 15)。
- 在 TwoRoom 與 Push-T 中,VoE 框架顯示 LeWM 對物理 teleport 擾動產生顯著的 surprise spike(paired t-test, $p<0.01$,Fig. 10)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 規劃僅限於短時程,長時程推理需要階層式 world model(Sec. 6 Limitations)。
- 方法仰賴具備充足互動覆蓋的 offline 資料集,蒐集成本高(Sec. 6)。
- 在 intrinsic dimensionality 極低的環境(如 Two-Room)中,將 latent 投影到高維空間並強制其逼近 isotropic Gaussian 可能導致表徵欠結構化,這正是 Two-Room 上 LeWM 87% 落後 PLDM 97%、DINO-WM 100% 的主因(Sec. 4.2 末段, Sec. 6)。
- OGBench-Cube 上 LeWM 74% 落後 DINO-WM 86%,作者推測歸因於 3D 場景視覺複雜度較高、encoder 訓練更困難(Sec. 4.2)。
- 預測 rollout 在 OGBench-Cube 上對 end-effector 朝向等細部資訊還原不佳,Tab. 4 顯示 block quaternion/yaw 的 probing 對所有方法皆困難(Sec. 5.1, Fig. 7, Fig. 11, Tab. 4)。
- VoE 中,OGBench-Cube 的 cube color 視覺擾動所誘發的 surprise 提升幅度較弱,且不具統計顯著性(Fig. 10 caption)。
- 仰賴 action label,作者建議未來以 inverse dynamics modeling 緩解(Sec. 6)。

#### 4.2.2 Phyra-inferred

- 「provable anti-collapse」的論證仰賴 Cramér–Wold 定理在 $M\to\infty$ 的漸近極限(App. A 的 weak convergence 表述);實作中僅以 $M=1024$ 個方向估計,有限樣本下並不保證避免任何形式的退化解,論文未給出 finite-$M$ 收斂率或樣本複雜度。
- 與 DINO-WM 的 probing 比較(Tab. 1, Tab. 4)結構性不對等:DINOv2 在 ~124M 自然圖像上預訓練,而 LeWM 僅看見 10–20k 條任務軌跡,作者亦於 Tab. 1 註腳承認此優勢;然而正文仍以「competitive with foundation-model」收斂,弱化了不對等的評估前提。
- PLDM 的 6 個損失係數僅在 Push-T 上以 256-config 網格搜尋,然後跨所有環境固定使用(App. C.2);任何 PLDM 在 OGBench-Cube、Reacher、TwoRoom 上的劣勢都可能來自此次優調參而非方法缺陷。
- 「只有一個有效超參數」的說法淡化了仍存在的多項設計選擇:projection 數 $M$、integration knots 數、quadrature 節點範圍 $[0.2,4]$、embedding dim 192、projection MLP 中的 BatchNorm(Sec. 3.1 自承為避免 LayerNorm 抑制 SIGReg 而引入)等,這些雖然對成功率不敏感,但仍是未驗證魯棒性的隱藏旋鈕。
- 與生成式 world model(DreamerV4、DIAMOND、IRIS)沒有任何同協議的量化比較;Fig. 2 雖將其歸類為「task-specific」並排除於主比較,但這是一個分類性論證而非實證論證。
- Section 3.1 將 BatchNorm 引入 projection MLP 以「讓 anti-collapse objective 能被有效優化」,本身即為一種 normalization 啟發式手段,與「無啟發式」的整體敘事略有張力。
- 訓練穩定性主要以 PushT 的訓練曲線(Fig. 18/19)與 Tab. 5 的 multi-seed 重測呈現,但未在更激進的學習率、更大的 ViT backbone、或 noisier 資料下做 stress test。
- 主結果條形圖(Fig. 6)未顯示 error bar;Tab. 5 雖宣稱多種子變異小,但僅針對單一環境呈報。

### 4.3 Phyra's Judgment (summary)

LeWM 真正新穎之處在於將 LeJEPA 提出的 SIGReg 移植到 action-conditioned latent world model,並證明僅憑 prediction + SIGReg 兩項即可取代 VICReg 衍生的 6 項 loss、EMA、stop-gradient 等啟發式手段,代表 JEPA 訓練配方的一次有意義簡化。其他主打成果(48× 規劃加速、單 GPU 訓練、強 probing 表現)主要源自編碼器的緊湊性與計算重新分配,屬於工程整合而非新的物理建模能力。本工作未解決的核心問題是:當資料從 224×224 玩具環境擴展到自然影片或高維機器人場景時,isotropic Gaussian 先驗是否仍與真實感知資料的內在流形相容,Two-Room 上的反例已預示了這個結構性風險。

## 5. Methodology Deep Dive

### 5.1 Method Overview

LeWorldModel (LeWM) 由兩個共同訓練的網路組成:一個將原始像素映射到低維 latent 的 vision encoder $\mathrm{enc}_\theta$,以及一個在 latent space 中建模環境動態的 predictor $\mathrm{pred}_\phi$。給定一段長度為 $T$ 的觀察序列 $o_{1:T}$ 與對應動作 $a_{1:T}$,encoder 將每個 frame 獨立映射為 $z_t = \mathrm{enc}_\theta(o_t)$,predictor 則以 teacher-forcing 的方式自回歸地由 $(z_t, a_t)$ 預測下一步 latent $\hat z_{t+1} = \mathrm{pred}_\phi(z_t, a_t)$。整個架構為 task-agnostic 與 reward-free,僅需 unannotated trajectories 即可訓練,且全部約 15M 參數可在單張 GPU 上完成端到端優化。LeWM 不使用 stop-gradient、EMA 或預訓練 frozen encoder,所有梯度直接流經 encoder 與 predictor 的所有參數。

架構上,encoder 以 ViT-Tiny 為 backbone(patch size = 14、12 層、3 個 attention heads、hidden dimension = 192,約 5M 參數),取最後一層 [CLS] token 通過一個 1-layer MLP + Batch Normalization 的 projector,得到 latent $z_t$。Projector 是必要設計:ViT 最後一層的 LayerNorm 會把表徵限制到單位球面附近,直接套用 anti-collapse 目標(高斯化 latent 邊際)會與該約束衝突,因此先以 BatchNorm 後的線性投影把 [CLS] token 映射到一個能被 SIGReg 有效優化的表徵空間。Predictor 為 6 層、16 個 attention heads、dropout 10% 的 Transformer(約 10M 參數),動作透過每層的 Adaptive Layer Normalization (AdaLN) 注入,其 AdaLN 參數初始化為零以漸進式地引入 action conditioning,並以 temporal causal masking 保證自回歸性。Predictor 之後同樣接一個與 encoder projector 同構的 1-layer MLP + BatchNorm。

訓練目標為 prediction loss 與 anti-collapse regularizer 的兩項加權和:$\mathcal L_{\text{LeWM}} = \mathcal L_{\text{pred}} + \lambda\,\mathrm{SIGReg}(Z)$。$\mathcal L_{\text{pred}}$ 是預測 latent 與下一步 encoder latent 之間的 MSE;$\mathrm{SIGReg}$ 將一個 batch 中收集到的 latent 張量 $Z \in \mathbb{R}^{N \times B \times d}$ 投影到 $M$ 個從 $\mathbb{S}^{d-1}$ 取樣的隨機單位方向 $u^{(m)}$,對每個一維投影 $h^{(m)} = Z u^{(m)}$ 計算 univariate Epps–Pulley 常態性檢定統計量,再對所有方向取平均。由 Cramér–Wold 定理,當所有一維邊際都為高斯時,聯合分布即為各向同性高斯,因此 SIGReg 直接約束 latent 邊際分布,排除 encoder 將所有觀察映射到單一常數的塌縮解。實驗顯示 $M$ 對下游表現幾乎無影響,使 $\lambda$ 成為唯一有效的超參數,可用對數複雜度 bisection search 高效調整(預設 $\lambda = 0.1$、$M = 1024$)。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input
   ├→ observations  o_{1:T}   shape: [B, T, C=3, H, W]
   └→ actions       a_{1:T}   shape: [B, T, A]
                                        (A: env-specific action dim)

Per-frame flatten
   [B, T, 3, H, W]  ──reshape──▶  [B*T, 3, H, W]

ViT-Tiny encoder  (patch=14, L=12, h=3, hidden=192, ~5M params)
   patch tokens + [CLS] + pos. emb           [B*T, N_p+1, 192]
                                              (N_p = ?, depends on H, W
                                               not specified in paper)
   12× Transformer blocks (LayerNorm-based)  [B*T, N_p+1, 192]
   take last-layer [CLS] only                [B*T, 192]

Encoder projector  (1-layer MLP + BatchNorm)
   [B*T, 192]  ──▶  [B*T, d]   (d: embedding dim, ? — see §5.3.2)

Reshape back
   [B*T, d]  ──▶  z_{1:T}  shape: [B, T, d]

       ├──────────────────────────────────┐
       │                                   ▼
       │                          SIGReg(Z) (anti-collapse)
       │                          Z = z.transpose(0,1) ∈ R^{T×B×d}
       │                          project onto M=1024 random
       │                          u^{(m)} ∈ S^{d-1}; Epps–Pulley
       │                          per 1-D projection; mean over m
       ▼
Predictor  (Transformer: L=6, h=16, dropout=0.1, ~10M params)
   inputs:  z_{1:T}  [B, T, d]
            a_{1:T}  [B, T, A]   ──AdaLN(zero-init) per layer──┐
   temporal causal mask                                         │
   6× Transformer blocks ◀──────────────────────────────────────┘
                                                  [B, T, d]

Predictor projector  (1-layer MLP + BatchNorm, same as encoder’s)
   [B, T, d]  ──▶  ẑ_{1:T}  shape: [B, T, d]

Prediction loss (teacher forcing, Eq. 1)
   L_pred = ||ẑ_{t+1} − z_{t+1}||²₂
          ≡ MSE( z[:,1:],  ẑ[:,:-1] )         shapes: [B, T-1, d]

Final objective (Eq. 3)
   L_LeWM = L_pred + λ · SIGReg(Z)            λ = 0.1, M = 1024
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Vision Encoder (ViT-Tiny)

**Function:** 將單張原始像素 frame 映射為一個低維、與 SIGReg 目標相容的 latent vector。

**Input:**
- Name: $o_t$ (per-frame view of $o_{1:T}$)
- Shape: `[B*T, 3, H, W]`(由 `[B, T, 3, H, W]` reshape)
- Source: 離線資料集中的 raw pixel observations

**Output:**
- Name: 最後一層 [CLS] token embedding(尚未經 projector)
- Shape: `[B*T, 192]`
- Consumer: §5.3.2 Encoder/Predictor Projector

**Processing:**

依 ViT 標準流程,對每個 frame 取 patch size = 14 進行非重疊切塊得到 $N_p$ 個 patch token,加上一個可學習的 [CLS] token 與 positional embedding,送入 12 層 Transformer encoder(每層 3 個 attention heads、hidden dimension 192、自帶 LayerNorm 與 residual)。取最後一層的 [CLS] token 作為該 frame 的全域表徵。整體參數量約為 5M。注意到 ViT 最後一層的 LayerNorm 會把輸出拉到單位球面附近,因此此處的 [CLS] token 還不能直接餵給 SIGReg。

**Key Formulas:**

無顯式公式;遵循 Dosovitskiy et al. (2021) 的標準 ViT 前向計算。

**Implementation Details:**

- Backbone: ViT-Tiny configuration(paper §3.1 Model Architecture)
- Patch size: 14
- Depth / heads / hidden: 12 / 3 / 192
- 最後一層使用 LayerNorm(此為 projector 必要存在的原因)
- 影像解析度 $H, W$ 與 patch 數 $N_p$ 在正文未明確指出,paper 將實作細節(batch size、解析度、sub-trajectory 構造)放於 App. D,正文中未給出具體數值

#### 5.3.2 Encoder / Predictor Projector

**Function:** 將 ViT 最後一層 LayerNorm 後的 [CLS] token(或 predictor 的輸出)映射到一個可被 anti-collapse 目標有效優化的表徵空間。

**Input:**
- Name: [CLS] token(encoder 端)或 predictor 最後一層輸出(predictor 端)
- Shape: `[B*T, 192]` 或 `[B, T, d]`
- Source: §5.3.1 Vision Encoder 或 §5.3.3 Latent Predictor

**Output:**
- Name: $z_t$(encoder 端)或 $\hat z_{t+1}$(predictor 端)
- Shape: `[B*T, d]` → reshape `[B, T, d]`
- Consumer: §5.3.3 Latent Predictor 與 §5.3.5 SIGReg(encoder 端);§5.3.4 Prediction Loss(predictor 端)

**Processing:**

單層線性層後接 Batch Normalization。論文明確指出此投影是必要的,因為 ViT 最後一層的 LayerNorm 會限制表徵到單位球面附近,直接套用「latent 邊際為各向同性高斯」的 anti-collapse 目標會與該約束相互衝突;改用 BatchNorm 則保留沿各維度的尺度自由度,允許 SIGReg 把分佈推向高斯。

**Key Formulas:**

無顯式公式(單層線性 + BatchNorm)。

**Implementation Details:**

- 1-layer MLP + Batch Normalization
- Encoder projector 與 predictor projector 為「相同實作」但參數獨立
- 輸出維度 $d$ 在正文未明確給出具體數值,SIGReg 段落只以符號 $d$ 表示 embedding dimension;依 Sec. 4.3 ablation,$d$ 須足夠大才能達到良好效能,但效能會在某個門檻後快速飽和

#### 5.3.3 Latent Predictor (Transformer + AdaLN)

**Function:** 在 latent space 中以 teacher-forcing 的方式,自回歸地由當前 latent $z_t$ 與動作 $a_t$ 預測下一步 latent $\hat z_{t+1}$。

**Input:**
- Names: 歷史 latent $z_{1:T}$、動作 $a_{1:T}$
- Shapes: `[B, T, d]`,`[B, T, A]`
- Source: §5.3.2 Encoder Projector 的輸出 + 資料集中的 action sequence

**Output:**
- Name: $\hat z_{1:T}$(再經 §5.3.2 中的 predictor projector 輸出最終預測)
- Shape: `[B, T, d]`
- Consumer: §5.3.4 Prediction Loss

**Processing:**

Predictor 是一個 6 層、16 個 attention heads、dropout 10% 的 Transformer(約 10M 參數)。每層中,動作 $a_t$ 透過 Adaptive Layer Normalization (AdaLN) 注入到該 token 的 LayerNorm 條件參數中,讓 attention/MLP 的內部 normalization 能依動作改變 scale 與 shift。Self-attention 採用 temporal causal mask,使位置 $t$ 的 token 只能看到 $\le t$ 的 latent,符合自回歸 next-embedding 預測的因果設定。Predictor 取最後一層輸出,經 §5.3.2 描述的 1-layer MLP + BatchNorm projector,得到最終的 $\hat z$。

**Key Formulas:**

$$
\hat z_{t+1} = \mathrm{pred}_\phi(z_t, a_t)
$$

**Implementation Details:**

- Transformer 深度 / heads / dropout:6 / 16 / 0.1
- 動作條件:每層 AdaLN,AdaLN 參數**初始化為零**,讓 action conditioning 在訓練初期幾乎不干擾 base 預測,再隨訓練漸進式地起作用,以穩定訓練
- Causal masking 防止資訊洩漏到未來時間步
- Predictor 之後接一個與 encoder 同構的 projector(BatchNorm)

#### 5.3.4 Prediction Loss

**Function:** 給予 encoder「學出對 predictor 而言可預測的表徵」的訊號,同時驅動 predictor 學習環境動態。

**Input:**
- Names: 真實下一步 latent $z_{t+1}$、預測 latent $\hat z_{t+1}$
- Shape: `[B, T-1, d]`(對齊後)
- Source: §5.3.2 Encoder Projector(target)、§5.3.3 + §5.3.2 Predictor 路徑(prediction)

**Output:**
- Name: $\mathcal L_{\text{pred}}$
- Shape: 純量
- Consumer: §5.3.6 Final Training Objective

**Processing:**

對每個 batch 取 `emb[:, 1:]` 作為 target、`next_emb[:, :-1]` 作為預測,計算 element-wise MSE 後對所有元素取平均(Eq. 1)。這是一個 teacher-forcing 設定:每一步 predictor 接收的 $z_t$ 都來自 encoder 對真實 $o_t$ 的編碼,而非自己上一步的預測。

**Key Formulas:**

$$
\mathcal L_{\text{pred}} \;\triangleq\; \big\lVert \hat z_{t+1} - z_{t+1} \big\rVert_2^2,
\qquad \hat z_{t+1} = \mathrm{pred}_\phi(z_t, a_t)
$$

**Implementation Details:**

- Reduction:`F.mse_loss`,即所有元素的平均平方誤差
- 由於梯度同時流經 $z_t$ 與 $z_{t+1}$,本損失若單獨使用會誘發塌縮(constant encoder 即可達到零損失),需要與 SIGReg 共同使用

#### 5.3.5 SIGReg Anti-Collapse Regularizer

**Function:** 直接約束 encoder 輸出的 latent 邊際分布,迫使其匹配各向同性高斯,藉此排除「將所有觀察映射到單一常數」這一 trivial 解,且不需要 stop-gradient、EMA 或預訓練 encoder 等啟發式手段。

**Input:**
- Name: latent 張量 $Z$(訓練中由一個 batch 蒐集而成)
- Shape: `[N, B, d]`(由 $z_{1:T}$ 經 `transpose(0,1)` 得到,$N = T$ 為 history length)
- Source: §5.3.2 Encoder Projector 的輸出

**Output:**
- Name: $\mathrm{SIGReg}(Z)$
- Shape: 純量
- Consumer: §5.3.6 Final Training Objective

**Processing:**

由於 univariate normality test 比 multivariate 版本更穩定可擴展,SIGReg 將 $Z$ 投影到 $M$ 個從單位球面 $\mathbb{S}^{d-1}$ 均勻取樣的隨機方向 $u^{(m)}$,得到 $M$ 個一維投影 $h^{(m)} = Z u^{(m)}$。對每個 $h^{(m)}$ 計算 Epps–Pulley 常態性檢定統計量 $T(\cdot)$,並對所有方向取平均(Eq. 2)。當所有一維邊際分布皆為高斯時,由 Cramér–Wold 定理可推得聯合分布為各向同性高斯,從而排除常數塌縮解(常數的所有一維投影是 Dirac mass,無法通過 Epps–Pulley 檢定)。

**Key Formulas:**

$$
\mathrm{SIGReg}(Z) \;\triangleq\; \frac{1}{M}\sum_{m=1}^{M} T\!\left(h^{(m)}\right),
\qquad h^{(m)} = Z\,u^{(m)},\;\; u^{(m)} \in \mathbb{S}^{d-1}
$$

**Implementation Details:**

- $M = 1024$ random projections(預設)
- 隨機方向 $u^{(m)}$ 從單位球面取樣
- Epps–Pulley 統計量 $T(\cdot)$ 定義細節置於 App. A,正文未展開
- ablation 顯示:$M$ 與 Epps–Pulley 的數值積分 knot 數對下游表現幾乎無影響,因此實際只需調 $\lambda$
- 在 pseudocode 中以 `mean(SIGReg(emb.transpose(0, 1)))` 形式進行 step-wise 應用;`transpose(0,1)` 把 `[B, T, d]` 變為 `[T, B, d]`,符合 $Z \in \mathbb{R}^{N \times B \times d}$ 的 convention

#### 5.3.6 Final Training Objective

**Function:** 將 prediction loss 與 anti-collapse regularizer 線性組合成 LeWM 唯一的訓練損失,使 encoder 與 predictor 端到端地共同優化。

**Input:**
- Names: $\mathcal L_{\text{pred}}$、$\mathrm{SIGReg}(Z)$
- Shape: 純量
- Source: §5.3.4 Prediction Loss、§5.3.5 SIGReg

**Output:**
- Name: $\mathcal L_{\text{LeWM}}$
- Shape: 純量
- Consumer: optimizer(梯度同時更新 encoder $\theta$ 與 predictor $\phi$)

**Processing:**

最終損失為兩項之和(Eq. 3),其中只有 $\lambda$ 是有效的超參數。論文強調:相較於唯一的 end-to-end JEPA baseline PLDM 需要 6 個以上的 loss 超參數(其多項 VICReg 變體加上其他額外 regularizer),LeWM 把超參數壓縮為單一 $\lambda$,且因為下游表現對 $\lambda$ 為 unimodal 的響應,可用對數複雜度的 bisection search 找最佳值,而非 grid search。

**Key Formulas:**

$$
\mathcal L_{\text{LeWM}} \;\triangleq\; \mathcal L_{\text{pred}} \;+\; \lambda \cdot \mathrm{SIGReg}(Z)
$$

**Implementation Details:**

- $\lambda = 0.1$(預設)
- 不使用 stop-gradient、EMA 或 frozen pre-trained encoder
- 所有梯度直接流經 encoder $\mathrm{enc}_\theta$ 與 predictor $\mathrm{pred}_\phi$ 的所有參數
- 整體模型(encoder + predictor + 兩個 projector)共約 15M 參數,可在單張 GPU 上於數小時內完成訓練

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| TwoRoom (Sobal et al.) | 2D continuous navigation between two rooms via a door | 10,000 episodes, avg. length 92 steps; collected by a noisy heuristic policy | Train world model 10 epochs; planning evaluation (budget 150 steps, goal sampled 100 steps ahead); the paper does not specify a held-out val/test split |
| Push-T (DINO-WM dataset) | 2D manipulation pushing a T-shaped block to a target | 20,000 expert episodes, avg. length 196 steps | Train world model 10 epochs; planning evaluation (budget 50 steps, goal 25 steps ahead); held-out set used for PLDM hyperparameter grid search |
| OGBench-Cube (single-cube variant) | 3D robotic-arm pick-and-place of a cube | 10,000 episodes, 200 steps each; collected with the OGBench heuristic | Train world model 10 epochs; planning evaluation (budget 50 steps, goal 25 steps ahead) |
| Reacher (DeepMind Control Suite) | 2-joint arm reaching a target in a 2D plane | 10,000 episodes, 200 steps each; collected by a Soft Actor-Critic policy | Train world model 10 epochs; planning evaluation (budget 50 steps, goal 25 steps ahead) |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Success Rate (%) | Fraction of goal-conditioned MPC rollouts that reach the target within the evaluation budget across the four environments | yes |
| Planning time (s) | Wall-clock time for one full CEM planning call, averaged over 50 runs | yes |
| Probing MSE | Mean-squared error of linear / MLP probes predicting physical quantities (agent/block/cube/end-effector position, joint state, yaw, quaternion) from a single latent embedding | no |
| Probing Pearson $r$ | Linear correlation between probe predictions and ground-truth physical quantities | no |
| Surprise (prediction MSE) | Open-loop predictor MSE used as the violation-of-expectation signal, compared between unperturbed, visually perturbed, and physically perturbed trajectories (paired $t$-test, $p<0.01$) | no |
| Temporal straightness | Cosine similarity between consecutive latent velocity vectors over training | no |

### 6.3 Training and Inference Settings

- **Hardware**: a single NVIDIA L40S GPU is used for both training and planning (App. D).
- **Frameworks**: training with `stable-pretraining` and `stable-worldmodel`; evaluation with PyTorch and Gymnasium (App. D).
- **Data pipeline**: frame-skip of 5 (5 raw actions are grouped into one action block), batch size 128, sub-trajectories of 4 frames × 4 action blocks, image resolution $224\times224$ (App. D).
- **Encoder**: ViT-Tiny (Hugging Face), patch size 14, 12 layers, 3 heads, hidden dim 192, $\sim$5M params; $z_t$ is the last-layer `[CLS]` token followed by a 1-layer MLP projector with BatchNorm (the projector is required because the ViT's final LayerNorm would otherwise prevent the SIGReg objective from being optimized) (§3.1, App. D).
- **Predictor**: ViT-S backbone, 6 layers, 16 heads, 10% dropout, $\sim$10M params; actions injected via AdaLN initialised to zero; learned positional embeddings with causal masking; history length $N=3$ on PushT and OGBench-Cube and $N=1$ on TwoRoom (§3.1, App. D).
- **Loss**: $\mathcal{L}_{\text{LeWM}} = \mathcal{L}_{\text{pred}} + \lambda\,\text{SIGReg}(Z)$ with $\lambda=0.1$, $M=1024$ random projections, no stop-gradient / EMA / pretraining (§3.1).
- **SIGReg quadrature**: trapezoid scheme over $T$ nodes uniformly distributed in $[0.2,4]$ (App. A).
- **Training length**: 10 epochs per environment (App. E).
- **Optimizer / learning-rate schedule**: the paper does not specify.
- **Planner**: CEM with 300 sampled action sequences, 30 elites, initial sampling variance 1; 30 CEM iterations on PushT and 10 on the other environments; planning horizon $H=5$ (which is 25 environment timesteps under frame-skip 5); receding-horizon MPC where the entire optimised sequence of length $H$ is executed before replanning (App. B, App. D).
- **Decoder (visualisation only)**: a lightweight transformer decoder with 196 learnable query tokens producing $16\times16\times3$ patches, trained post-hoc and never used during world-model training (App. D).

### 6.4 Main Results

| Method | Two-Room SR (%) | Reacher SR (%) | Push-T SR (%) | OGBench-Cube SR (%) | Notes |
|---|---|---|---|---|---|
| **LeWM (ours)** | **87** | **86** | **96** | **74** | End-to-end from pixels, 15M params, single GPU; planning $\sim$0.98 s |
| DINO-WM + prop. | 100 | – | 92 | – | Adds proprioceptive input; not pixels-only |
| PLDM | 97 | 78 | 78 | 65 | End-to-end pixels, 7-term VICReg-style loss |
| DINO-WM | 100 | 79 | 74 | 86 | Frozen DINOv2 encoder, $\sim$200× more tokens; planning $\sim$47 s |
| GCBC | 100 | – | 75 | 84 | Goal-conditioned behavioural cloning on DINOv2 features |
| GCIQL | 100 | – | 20 | 64 | Offline goal-conditioned RL |
| GCIVL | 100 | – | 33 | 56 | Offline goal-conditioned RL |
| Random | 0 | 10 | 2 | 48 | Reference lower bound |

Headline efficiency claim (Fig. 3): LeWM full planning takes $0.98$ s vs. $47$ s for DINO-WM, i.e. $\sim$48× faster; under a fixed-FLOPs planning budget, LeWM reaches $90\%$ vs. $13\%$ on Push-T and $74\%$ vs. $48\%$ on OGB-Cube.

### 6.5 Ablation Studies

- **SIGReg weight $\lambda$ (Fig. 16)** — sweeps $\lambda \in \{0.01, 0.05, 0.09, 0.095, 0.1, 0.2, 0.5\}$ on Push-T. Success rate stays above $80\%$ for $\lambda \in [0.01, 0.2]$, peaks near $\lambda=0.09$, and collapses at $\lambda=0.5$ where the regulariser overwhelms $\mathcal{L}_{\text{pred}}$. Diagnostic: directly tests the only effective hyperparameter and motivates the bisection-search claim.
- **Number of SIGReg projections $M$ (Fig. 15, center)** — sweeps $M\in\{64,256,512,1024\}$. Success rate is essentially flat ($\sim$80–95%). Useful as a robustness check, but borders on a sanity check rather than a diagnostic of *what SIGReg buys*; it does not include an ablation that drops SIGReg entirely (which presumably would collapse, but the paper does not report the curve).
- **Number of integration knots in Epps–Pulley quadrature (Fig. 15, right)** — sweeps $\{4,8,12,17,32\}$ knots. Performance is again largely insensitive. Sanity-check-flavoured: confirms numerical stability of the quadrature, not a property of the world-modelling design.
- **Embedding dimension (Fig. 15, left)** — sweeps $\{8,24,96,192,384\}$. Performance is poor below $\sim$184 and saturates above; gives a usable threshold but is a capacity sweep rather than a component ablation.
- **Encoder architecture (Tab. 8, App. G)** — replaces the default ViT-Tiny encoder with a ResNet-18 backbone; LeWM remains competitive, supporting the claim that the method is encoder-agnostic. Diagnostic of the architectural-robustness claim.
- **Training variance / multi-seed (Tab. 5, App. G)** — retrains with multiple random seeds and reports "consistently high success rates with low variance"; supports the stability claim.
- **Training-curve comparison vs. PLDM (Figs. 18–19)** — qualitative ablation against the closest competing objective: LeWM's two terms decrease monotonically while several of PLDM's seven terms are noisy / non-monotonic. Diagnostic of the central "fewer hyperparameters → more stable training" thesis.

Missing diagnostics worth flagging: there is no ablation that *removes* SIGReg (or replaces it with VICReg / EMA+stop-grad) while keeping everything else fixed — that would be the most direct test of whether SIGReg is what prevents collapse end-to-end.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — DINO-WM (frozen DINOv2 encoder, ICML 2025) and PLDM are compared, plus GCBC/GCIQL/GCIVL on OGBench (Fig. 6).
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — four environments spanning 2D navigation, 2D manipulation, 3D manipulation, and continuous control (TwoRoom, Push-T, OGBench-Cube, Reacher).
- [partial] Has ablations that diagnose the new components (not just sanity checks) — $\lambda$ sweep, training-curve comparison, and encoder swap are diagnostic, but there is no ablation that removes SIGReg entirely or substitutes it with VICReg-style anti-collapse to isolate SIGReg's contribution.
- [partial] Has a scaling study (size, length, or compute) — embedding-dimension sweep covers representation capacity, but there is no study of model size, dataset size, training length, or planning horizon scaling.
- [covered] Has an efficiency / wall-clock comparison — Fig. 3 reports $0.98$ s vs. $47$ s planning time for LeWM vs. DINO-WM ($\sim$48× speed-up) and a fixed-FLOPs comparison on Push-T and OGB-Cube.
- [partial] Reports variance / standard deviation / multiple seeds where relevant — App. G Tab. 5 reports multi-seed stability and probing tables include $\pm$ values, but main planning results in Fig. 6 are reported as point success rates without seed counts or error bars.
- [covered] Releases code / weights / data sufficient for reproducibility — the abstract advertises a website and code repository, and training/evaluation are built on the released `stable-pretraining` and `stable-worldmodel` libraries (App. D, refs. [49, 50]); the paper does not specify whether trained weights are released.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1**:「首個能端到端、僅以兩項 loss 從像素穩定訓練的 JEPA」(Sec. 1, Sec. 3.1)。**Supported**:Fig. 18/19 顯示 LeWM 各 loss 平滑單調收斂,而 PLDM 七項目標呈非單調波動;Tab. 5 顯示多種子穩定。
- **Claim 2**:「在多樣 2D/3D 控制任務以 15M 參數達成強表現」(Sec. 1)。**Partially supported**:Push-T、Reacher 上 LeWM 為最佳(Fig. 6),但 OGBench-Cube 落後 DINO-WM 12pp,Two-Room 落後 PLDM 10pp、落後 DINO-WM 13pp;「strong」一詞涵蓋了 4 環境中的 2 個 winner。
- **Claim 3**:「規劃比 foundation-model-based world model 快達 48×」(Sec. 1, Fig. 3)。**Supported in wall-clock terms**;但加速主要來自 token 數降低約 200×(Fig. 3 caption),並非演算法層級的新穎,屬於架構選型結果。
- **Claim 4**:「latent 空間編碼有意義的物理結構」(Sec. 1, Sec. 5)。**Partially supported**:Push-T 上 location 類量 probing 與 DINO-WM 相當(Tab. 1);但 OGBench-Cube 上 block quaternion、block yaw、joint velocity 的 linear 與 MLP probing 皆遠落後 DINO-WM(Tab. 4),旋轉與動量資訊未被有效編碼。
- **Claim 5**:「能可靠偵測物理上不合理的事件」(Sec. 1, Sec. 5.2)。**Partially supported**:teleport 擾動在三環境皆顯著($p<0.01$,Fig. 10);但 cube color 視覺擾動在 OGBench-Cube 上不顯著,「reliably detects」的範圍實為「物理連續性違反」,而非廣義 implausibility。

### 7.2 Fundamental Limitations of the Method

**Isotropic Gaussian 先驗與內在維度的錯配。**SIGReg 的目標是讓 $d=192$ 的 latent 邊際分布逼近標準高斯。當環境的 intrinsic dimensionality 顯著低於 $d$(例如 Two-Room 只有平面位置 2 維)時,正則項與動力學需求產生衝突:勉強將 2 維結構分散到 192 維高斯會犧牲幾何保真度。作者在 Sec. 4.2 與 Sec. 6 已承認此現象,但這是 SIGReg 框架本身的結構性限制,只能透過「自適應目標分布」或「動態 $d$」改寫才能根治,並非超參數可調好。

**漸近保證 vs. 有限實作。**Cramér–Wold 定理保證的是「對所有 1D 投影皆為高斯時聯合分布為各向同性高斯」,但 SIGReg 僅在 $M=1024$ 個 i.i.d. 方向上估算 Epps–Pulley 統計量。論文未提供 finite-$M$ 下避免常數塌縮或低秩塌縮的保證,App. A 的「weak convergence」明確以 $M\to\infty$ 為前提。實務上 $M$ 可被視為一個「精度旋鈕」,但其與 collapse 風險的定量關係仍未刻畫。

**Encoder 容量瓶頸暴露於視覺複雜環境。**LeWM 採用 ViT-Tiny(~5M 參數,patch 14)從零訓練,在 Two-Room 與 Push-T 等簡單背景上夠用,但 OGBench-Cube 的 3D 視覺複雜度即足以讓 LeWM 落後於使用凍結 DINOv2 的 DINO-WM。這暗示在「真實機器人/自然影片」設定中,從零訓練的小型 ViT 不太可能與大型預訓練 vision foundation 競爭,而 SIGReg 對更大 backbone 的訓練動力學是否仍穩定,論文未驗證。

**Action label 與 dense offline 軌跡的依賴。**LeWM 的 prediction loss 直接 condition 在 $a_t$ 上(Eq. 1),且訓練資料假設為連續軌跡。這排除了無動作標註的純 video 預訓練(此正是 V-JEPA 系列的優勢區),也使「將 LeWM 應用於大規模未標記影片以獲得通用 priors」這個方向需要先發明 inverse dynamics 配套。

### 7.3 Citations Worth Tracking

- **[25] Balestriero & LeCun, LeJEPA(arXiv:2511.08544)**:SIGReg 的原始論文,理解 LeWM 必讀的前序工作,涵蓋 Epps–Pulley 統計量、Cramér–Wold 應用、quadrature 細節。
- **[22] Sobal et al., PLDM**:LeWM 唯一直接競爭的 end-to-end JEPA baseline;若要評估 LeWM 的相對貢獻,必須讀懂 PLDM 七項 loss 的個別作用,以判斷 SIGReg 是否真的「概念上等價於 VICReg + 6 項補丁」。
- **[18] Zhou et al., DINO-WM(ICML 2025)**:foundation-based latent WM 的代表;評估「end-to-end vs. frozen foundation encoder」trade-off 的關鍵對照。
- **[44] Garrido et al., Intuitive Physics from V-JEPA(arXiv:2502.11831)**:VoE 評估方法的直接前身,理解 surprise 指標的設計選擇與其在自監督模型中的詮釋極限。
- **[55] Wang et al., Temporal Straightening for Latent Planning(arXiv:2603.12231)**:Sec. 5.1 中 emergent straightening 主張的最新比較對象,用於判斷 LeWM 的 straightening 是否真的「更強」或只是不同度量下的副產品。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在自然影片(非合成、流形非高斯)上,SIGReg 強制 isotropic Gaussian 是否仍與下游預測目標相容,還是會像 Two-Room 一樣產生表徵欠結構化?
- [ ] 將 encoder 從 ViT-Tiny 擴大到 ViT-B/L 或更大時,SIGReg 是否仍維持 Sec. 4.3 所示的訓練平滑性,還是會因為大量參數放大有限-$M$ 的估計噪聲而失穩?
- [ ] OGBench-Cube 上落後 DINO-WM 的 12pp 是來自 encoder 容量、isotropic 先驗錯配,還是 CEM 規劃在更高維 dynamics 下的偏差,Sec. 4.2 的歸因僅為推測,需 controlled ablation。
- [ ] 在固定的計算預算下,以同樣 256-config 網格逐環境重新調 PLDM 的 6 個係數,Fig. 6 的勝負是否仍然成立?
- [ ] Sec. 3.1 中 projection MLP 內的 BatchNorm 是否本身就在隱性提供 anti-collapse 訊號?移除 BatchNorm 而僅保留 SIGReg 是否仍能避免塌縮?
- [ ] 當 offline 軌跡轉為純探索性(非 expert / heuristic policy)時,SIGReg 是否仍能誘導出對下游規劃有用的結構,或僅是 Gaussian 殼?
- [ ] 對於非 task-agnostic 的生成式 WM(DreamerV4、DIAMOND),在同樣 0.98s 規劃預算與相同資料集下,LeWM 是否仍維持速度優勢與接近的成功率?

### 8.2 Improvement Directions

1. **以 inverse dynamics 取代或補充 action label conditioning。**作者已在 Sec. 6 提及;比階層式 WM 更易實作,且能直接釋放在大規模未標記影片上預訓練的可能性,進而緩解 OGBench-Cube 的 encoder 容量瓶頸。
2. **在 SIGReg 之外允許目標分布為 anisotropic Gaussian 或 mixture。**Two-Room 的反例直接指向「目標分布應與資料 intrinsic dimensionality 匹配」;最小擴充是將協方差設為可學習對角,並對其譜施加正則。Cramér–Wold 推論在這個擴充下仍適用。
3. **逐環境重新調 PLDM 的 6 個損失係數作為公平 baseline。**目前 PLDM 的劣勢部分混入了「fixed across environments」的調參假設(App. C.2);這項實驗成本中等,但可量化 LeWM「真實」的方法層 advantage。
4. **將 encoder 換成預訓練後再聯合微調。**作者於 Sec. 6 已提示在大規模自然影片上做表徵預訓練;這是縮小與 DINO-WM 在 OGBench-Cube 上 12pp 差距最直接的路徑,且不需修改 SIGReg 框架。
5. **以 finite-$M$ collapse 風險上界補強理論部分。**目前 App. A 僅給出 $M\to\infty$ 的弱收斂,但 Epps–Pulley 統計量在固定 $M$、固定 sample size 下的 deviation bound 可由現有 U-statistic 文獻推得,能將「provable」的範圍從漸近收斂提升到工程可信的有限樣本保證。
6. **加入階層式 / multi-resolution latent prediction。**作者於 Sec. 6 列為主要 future work;雖然工程成本最高,但是唯一能解決短時程規劃限制與長時程 rollout 誤差累積的結構性升級。
