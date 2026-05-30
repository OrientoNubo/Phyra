<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# Vista4D — Vista4D: Video Reshooting with 4D Point Clouds

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | Vista4D |
| Paper full title | Vista4D: Video Reshooting with 4D Point Clouds |
| arXiv ID | 2604.21915 |
| Release date | 2026-04-23 |
| Conference/Journal | CVPR 2026 (Highlight) |
| Paper link (abs) | https://arxiv.org/abs/2604.21915 |
| PDF link | https://arxiv.org/pdf/2604.21915 |
| Code link | https://github.com/Eyeline-Labs/Vista4D |
| Project page | https://eyeline-labs.github.io/Vista4D/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Kuan Heng Lin | Eyeline Labs; Columbia University | https://kuanhenglin.github.io/ | first author (intern at Eyeline Labs; PhD student at Columbia) |
| Zhizheng Liu | Eyeline Labs; UCLA | https://scholar.google.com/citations?user=Asc7j9oAAAAJ&hl=en | co-first author |
| Pablo Salamanca | Eyeline Labs; Netflix | — | author |
| Yash Kant | Eyeline Labs; Netflix | — | author |
| Ryan Burgert | Eyeline Labs; Netflix; Stony Brook University | — | author (intern) |
| Yuancheng Xu | Eyeline Labs; Netflix | — | author |
| Koichi Namekata | Eyeline Labs; Netflix; University of Oxford | — | author (intern) |
| Yiwei Zhao | Netflix | — | author |
| Bolei Zhou | UCLA | https://boleizhou.github.io/ | author (advisor) |
| Micah Goldblum | Columbia University | — | author (advisor) |
| Paul Debevec | Eyeline Labs; Netflix | — | senior author |
| Ning Yu | Eyeline Labs; Netflix | https://ningyu1991.github.io/ | corresponding / senior author (Lead Research Scientist) |

### 1.2 Keywords

video reshooting, 4D reconstruction, point cloud rendering, video diffusion model, camera control, novel-view synthesis, static pixel segmentation, Plücker embedding

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| TrajectoryCrafter | baseline | Explicit-prior 雙重重投影法產生單目訓練對；Vista4D 主要對照基線之一。 |
| GEN3C | baseline | 以 3D cache 與 pooling-based fusion 進行稀疏視角合成的點雲條件式重拍方法。 |
| EX-4D | baseline | 以 Depth Watertight Mesh 進行追蹤式 inpainting 訓練的點雲條件式重拍方法。 |
| ReCamMaster | baseline | 提供 MultiCamVideo 合成多視角資料集，並用 camera embeddings 控相機。 |
| CamCloneMaster | baseline | 以參考影片隱式複製相機軌跡的視訊重拍方法。 |
| Wan2.1-T2V-14B | base model | 作為微調起點的預訓練 text-to-video flow matching diffusion transformer。 |
| STream3R / π3 | influence | 端到端 4D 重建模型，提供深度與相機以建立世界座標 4D 點雲。 |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於「影片重拍 (video reshooting)」：給定單目來源影片，於後製階段沿任意新相機軌跡與視角重新合成同一動態場景，以實現虛擬攝影與視覺敘事控制。Vista4D 將來源影片與目標相機共同錨定於一個世界座標下、具時間持續靜態像素的 4D 點雲表示，並結合視訊擴散模型 (video diffusion) 的生成先驗以兼顧已見內容保留與未見內容的合理生成。研究議題涵蓋穩健的 4D 重建條件化、靜態/動態像素分割、含雜訊多視角資料訓練策略、相機精準控制 (Plücker embedding)、以及在動態場景擴展、4D 場景重組與長影片分塊推論等實際應用，最終於 CVPR 2026 被選為 Highlight。

### 2.2 Domain Tags

- Computer Vision
- Generative AI
- Video Generation
- 4D Reconstruction
- Novel View Synthesis
- Virtual Cinematography

### 2.3 Core Architectures Used

- **Wan2.1-T2V-14B**：作為基礎 video diffusion transformer，採用 flow matching 訓練目標，是 Vista4D 微調的起點 (僅訓練 patchify、self-attention、camera encoder 與 projector，其他參數凍結)。
- **4D point cloud representation (本論文提出)**：以世界座標、時間持續靜態像素為條件的顯式 4D 表徵，由 inverse perspective projection $\Phi^{-1}$ 與世界座標轉換 $\Omega$ 構成 (Eq. 1)，並透過靜態像素遮罩 $M^{\text{stc}}$ 建立 temporally-persistent 的點雲 $\overline{P}$。
- **In-context latent token concatenation (本論文提出)**：將 source video 與 point cloud render 的 patchified latent tokens 沿 frame dimension 串接到 noisy target latent tokens，取代 TrajectoryCrafter 的 cross-attention 注入，以更好保留來源外觀。
- **Plücker embedding camera encoder**：以 zero-initialized linear projection 注入 Plücker 形式的目標相機 $C^{\text{tgt}}=(K^{\text{tgt}}, T^{\text{tgt}})$，self-attention 後以 identity-initialized projection 結合，沿用 ReCamMaster 設計。
- **STream3R / π3 (4D reconstruction)**：端到端 4D 重建模型，分別用於合成多視角資料 (MultiCamVideo) 與真實世界單目資料 (OpenVidHD-0.4M 子集) 之深度與相機估計。
- **Grounded SAM 2 + RAM + Llama-3.1-8B-Instruct**：靜態像素分割 pipeline，以 RAM 取得語意類別、Llama-3.1-8B-Instruct 過濾動態名詞、Grounded SAM 2 分割逐幀動態像素並反轉得到 $M^{\text{stc}}$。
- **Wan2.1-I2V-14B (variant)**：第一幀條件版本，用於長影片 chunked autoregressive 推論以維持 chunk 間視覺一致性。

### 2.4 Core Argument

作者指出既有以顯式點雲為條件的影片重拍方法 (如 TrajectoryCrafter、GEN3C、EX-4D) 之根本問題：它們多以「無瑕疵深度圖」訓練，例如以 double re-projection 從目標影片正面視角生成訓練對，使任務退化為 inpainting；一旦推論時面對真實世界動態影片中不精確的單目深度與 4D 重建，生成模型便無法修正非正面視角下的幾何瑕疵與時間閃爍。同時，逐幀相機空間點雲在目標相機與來源影片重疊度低時，既無法保留已見外觀，也無法提供足夠相機訊號。隱式條件方法 (ReCamMaster、CamCloneMaster) 又因單目深度尺度不確定而導致相機控制不精準。Vista4D 的解法因此在邏輯上是必要的兩個對應修補：(1) 建立含「時間持續靜態像素」的世界座標 4D 點雲，使任何幀都可看見靜態內容，從而在大幅度新軌跡下仍能顯式保留外觀並提供豐富相機訊號；(2) 改以含 4D 重建瑕疵的合成多視角動態資料 (MultiCamVideo + STream3R) 與單目資料混合訓練，使模型學會「修正不完美點雲」而非僅 inpainting；並透過 in-context 串接 latent token 同時條件化來源影片與點雲渲染，以從來源影片補回幾何與外觀資訊。此設計直接回應了上述根因，因此能同時在相機準確度、3D 一致性、視覺保真度與動態場景擴展等下游應用上超越現有基線。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

標題「Vista4D: Video Reshooting with 4D Point Clouds」直接點出方法名稱與核心技術主軸，揭示作者把 video reshooting 問題重新定義為「以 4D point cloud 為 grounding」的任務。Abstract 緊接著鋪陳三個關鍵命題：第一，給定一段 input video，方法可以從 different camera trajectory and viewpoint 重新合成同一個動態場景；第二，現有 video reshooting 方法在 real-world dynamic videos 上會被 depth estimation artifacts 所困，且難以同時保留原內容外觀與維持精準的相機控制；第三，Vista4D 透過「以 static pixel segmentation 與 4D reconstruction 構建 4D-grounded point cloud representation」並「用重建後的 multiview dynamic data 進行訓練」來同時克服這兩個問題。

Abstract 在最後把訴求從「方法本身」延伸到「應用面」：宣稱在 4D consistency、camera control、visual quality 三個指標上勝過 SOTA baselines，並進一步泛化到 dynamic scene expansion 與 4D scene recomposition 等實際場景。這段 framing 設定了全文的三個審視維度，後續 §3 Introduction 與 §4 Experiments 會反覆呼應這三點。對讀者而言，Abstract 同時暗示了作者的方法定位，介於 explicit-prior（point cloud）與 implicit-prior（diffusion model 先驗）之間，為後續「兩條技術路線各有缺陷、Vista4D 取兩者之長」的論述鋪路。

### 3.2 Introduction

(520 words)

Introduction 從電影攝影機作為「敘事視覺語言」的隱喻切入，把 video reshooting 抬升到 post-production 中操控視覺說故事的新維度，這是非常典型 Eyeline Labs/Netflix 系作者群會採用的開場修辭。在這個包裝下，作者把 task 形式化為：給定 source video，從新的 camera trajectories 與 viewpoints 渲染同一個動態場景，且需同時做到「對 seen content 的忠實重建」、「對 unseen content 的合理生成」、以及「精準可控的相機」。

接著 Intro 給出技術選型的兩個前提：（1）採用 video diffusion models 作為 dynamic content 的強先驗；（2）結合 4D reconstruction 把 monocular source video 提升為 4D point cloud，提供 spatiotemporal grounding 與 camera control 的 rich signal。這兩個前提合起來定義了 Vista4D 的方法骨幹：以「temporally-persistent static pixels 的 4D-grounded point cloud」做空間錨定，再以 video diffusion 的生成先驗補完缺漏。

然後作者建立 contrast：既有 video reshooting 工作（[7–9]）以 per-frame depth-lifted point cloud 作為 conditioning，問題是它們通常在精準 depth maps 上訓練，因此遇到真實世界 dynamic videos 的 4D reconstruction 不準時，會出現 geometry artifacts 與 temporal flickering，且在挑戰性的 target trajectories 下相機控制與內容保留都會崩。這段把 baseline 的失敗原因歸因到「訓練/推論分布錯配」，為後續方法選擇做出具體 motivation。

接著 Intro 列出 Vista4D 的兩個關鍵設計：第一，建立 static pixels 跨幀可見的 4D-grounded point cloud（取代 per-frame 3D point cloud），讓 seen content 即使 target camera 與 source video 幾乎沒有 per-frame overlap 仍能被保留並提供 camera signal；第二，以「帶 4D-reconstructed depth artifacts」的 dynamic multiview video pairs 增強訓練，讓模型學會在 non-frontal view 的 noisy point cloud render 上仍可生成 plausible content。這個訓練資料設計也順勢解鎖了在 inference 時直接編輯 4D point cloud 的能力，引出後續的 application stories。

最後 Intro 以三點 contributions 收尾：(i) 提出 Vista4D，以 4D point cloud grounding 兼顧 geometric/physical plausibility 與 seen content preservation；(ii) 透過 quantitative、qualitative 與 user study 的廣泛比較，證明 content preservation、camera controllability、visual quality 全面勝出；(iii) 訓練設計使 Vista4D 額外延伸出 dynamic scene expansion、4D scene recomposition、long video inference with memory 等應用。這個 contribution list 同時定義了 §4 的評估面向與 §4.4 的 application 章節結構，把整篇論文的論證鏈鋪設完整。

### 3.3 Related Work / Preliminaries

(330 words)

Related Work 分成三條軸線，並刻意排序為「explicit prior、implicit prior、4D reconstruction」，與 Intro 中的方法定位完全對齊。第一條 axis「Video reshooting with explicit priors」回顧以 per-frame camera-space point cloud 作為 conditioning 的方法（[7–9, 12–14]），它們依賴 video depth estimators（[15–17]），並順帶把 depth prior 的應用面擴及 static scene NVS 與 video motion control。作者明確指出這條路線的弱點：「常在精準 depth maps 上訓練 → 對 real-world imperfect depth 不耐 → per-frame 條件難以保留 seen content 且難挑戰性 trajectory 上保持精準相機控制」，這直接合理化 Vista4D 的兩個關鍵設計（temporally-persistent point cloud + 含 artifact 的 multiview 訓練）。

第二條 axis「Video reshooting with implicit priors」介紹靠 camera embeddings 或 reference videos 對 video diffusion 做 finetune 的路線（[10, 21, 22]），並把它與 image- and camera-conditioned NVS 與 camera-controlled video generation 連結。對這條路線的批判則落在「monocular video 的 depth scale ambiguity 使 implicit-prior 的相機控制不精準，且無法像 point cloud 那樣顯式 preview」。這層對比把 Vista4D 推到「保留 explicit point cloud 的可預覽相機控制，同時引入 video diffusion 的隱式先驗來補足 reconstruction 不完美」的中間位置。

第三條 axis「4D reconstruction」說明 Vista4D 為何能假設 source video 可被 lift 成 world-space point cloud：傳統 SfM（[31–33]）對 dynamic scene 不夠 robust，而結合 learning-based depth（[15–17, 34–36]）與 SLAM（[40]）的 dynamic reconstruction 工作（[37–39]），以及近期 end-to-end 4D reconstruction 模型（[11, 44–47]）與 monocular 4D Gaussians（[48–50]）已能提供可用的 4D 表示。這段同時也預告 §3.4 與實驗中具體採用的 STream3R [11] 與 π3 [44] 兩個重建後端。

整體而言，Related Work 並未獨立陳述 preliminaries，而是把每條 axis 的痛點直接對應到 Vista4D 的設計選擇，讓 §3 Method 一進場就站在「explicit + implicit 混合，且訓練分布貼合 real-world reconstruction」這個已被反覆論證合理性的地基上。

### 3.4 Method (overview narrative)

(380 words)

§3 Method 的敘事節奏明確分為四步：先建立 4D-grounded representation，再說明訓練資料的選擇，接著討論 conditioning 設計，最後給出訓練細節。整節的核心 thesis 是：「以 temporally-persistent 的 4D point cloud 作為 explicit grounding，搭配能容忍 reconstruction artifact 的訓練資料與 in-context source video conditioning，讓 video diffusion 同時擁有顯式相機控制與隱式生成先驗」。

§3.1 先把 source video $X^{src}$ 透過 4D reconstruction 取得 $D^{src}, T^{src}, K^{src}$，再透過 segmentation 取得 static pixel mask $M^{stc}$，將每幀像素 lift 至 world-space point cloud $\vec{P}$（Eq. 1，由 inverse perspective projection $\Phi^{-1}$ 與 world-space transform $\Omega$ 組成）。關鍵差異在於使用 $M^{stc}$ 把 static pixels 設為「跨所有幀都 persistent」，得到 temporally-persistent 的 $\mathcal{P}$。從 target cameras 渲染 $\mathcal{P}$ 得到 point cloud render $X^{src \to tgt}$ 與 alpha mask $M^{src \to tgt}$，作為 4D-grounded 的條件，用來解決 baseline 在 target camera 與 source 重疊很少時崩掉的問題。

§3.2 直擊訓練分布問題。作者點明：因 4D reconstruction 不完美，inference 時的 point cloud render 在 non-frontal view 常含幾何 artifact（特別是動態像素）。既有方法以 double-reprojection 訓練於 artifact-free 的 frontal view，把 reshooting 簡化成 inpainting；Vista4D 反其道而行，使用「具 4D-reconstructed depth artifacts」的 multiview dynamic videos（如 MultiCamVideo + STream3R 重建），讓模型學會「校正不完美的點雲幾何」，並以 monocular real-world data（OpenVidHD-0.4M + π3）做 double-reprojection 補強泛化。

§3.3 處理 conditioning。除了 point cloud render，作者也將 source video 一併作為條件，以利用 diffusion model 的 implicit prior 傳遞 geometry/appearance；與 TrajectoryCrafter 的 cross-attention 注入不同，Vista4D 將 source video 與 point cloud render 的 patchified latent tokens 沿 frame 軸與 noisy target latent token concatenate，做 in-context conditioning（更能保留 source 內容、對 artifact 更穩健）。Loss 採 flow matching（Eq. 2），target cameras 以 Plücker embeddings 透過 zero-initialized 線性投影注入，self-attention 後再加 identity-initialized 投影，模仿 ReCamMaster 的設計。

§3.4 鎖定具體訓練配置：以 Wan2.1-T2V-14B 為底，先在 672×384 fine-tune 30,000 步、再在 1280×720 fine-tune 300 步，皆 49 frames、batch 8、AdamW lr 1e-5；只訓練 patchify 層、self-attention、camera encoders 與 projector，其餘凍結。資料處理上以 RAM + Llama-3.1-8B-Instruct + Grounded SAM 2 自動產生 static pixel mask。整節整體論述完成「為何要這樣建模、為何要這樣訓練、為何要這樣 condition」的完整因果鏈，為 §4 的全面比較提供 method-level 的辯護基礎。

### 3.5 Experiments (overview narrative)

(360 words)

§4 Experiments 的整體故事是：把 Vista4D 與「explicit-prior（point cloud 條件）」與「implicit-prior（camera embedding/reference video 條件）」兩派 SOTA 全面對齊比較，證明它在三個維度上同時勝出，並用 application 段落把方法的延展性實證化。

作者首先把 baseline 切成兩派：explicit-prior 包含 TrajectoryCrafter [7]（double-reprojection 訓練）、EX-4D [9]（Depth Watertight Mesh）、GEN3C [8]（pooling-based 3D cache）；implicit-prior 包含 ReCamMaster [10]（synthetic multiview camera-conditioned）與 CamCloneMaster [22]（reference-video camera 複製）。所有量化評估與 user study 採用 672×384 的 checkpoint，以求公平。

評估資料集自製 110 video-camera pairs：51 段來自 DAVIS [68] 與 Pexels [69]，搭配 π3 [44] 重建與 Grounded SAM 2 segmentation，再以自家 camera design UI 為每段設計 2–3 條 trajectory。

§4.1 量化比較鋪設三條 axis：(a)「Camera control accuracy + 3D consistency」用 translation/rotation/intrinsics error 與 SuperGlue 下的 reprojection error（RE@SG），Vista4D 在所有四個指標上皆最佳，明顯壓過 implicit-prior 派的 camera 不準與 explicit-prior 派的 3D consistency 不足；(b)「Novel-view video synthesis」用 iphone dataset [60]，以 mPSNR/mSSIM/mLPIPS、PSNR/SSIM/LPIPS、EPE 衡量，Vista4D 在 PSNR、LPIPS、EPE 上領先，作者也誠實點出 SSIM 落後 TrajectoryCrafter 但其輸出含明顯 artifact；(c)「Video fidelity」用 FID、FVD、CLIP-T、VBench 與 VBench-2.0，Vista4D 全面壓過 explicit-prior baselines，並解釋為何 implicit-prior 在 FID/FVD/consistency 上看似領先（因相機幾乎沒動）。

§4.2 質化比較與 user study（30 對、42 位受試者）顯示 Vista4D 在 source preservation、camera accuracy、overall fidelity 三個維度都拿到 67–77% 的偏好率，遠勝任一 baseline。Figure 6 也補上對 segmentation failure（如 tennis racket 未被分割）的 robustness 展示。

§4.3 Ablation 聚焦在「沒有 depth artifact 訓練」「沒有 source video」「cross-attention 注入」「沒有 temporal persistence」四種變體，結論：「含 artifact 訓練 + in-context source video」是 robust 的關鍵，去掉 temporal persistence 則會嚴重損害 static content 保留與相機準確度。

§4.4 把方法推到三個 application：dynamic scene expansion（共重建 casual scene capture 提供更豐富環境先驗）、4D scene recomposition（直接編輯點雲做插入/刪除/縮放，包含跨光照插入 rhino 的範例）、long video inference with memory（chunk-by-chunk 推論，藉 4D point cloud 保留靜態內容記憶）。這些 application 把 §3.2 的「訓練要對 artifact 穩健」的設計回收為實用的解鎖能力，閉合了論文的論證迴圈。

### 3.6 Conclusion / Limitations / Future Work

(260 words)

§5 Conclusion 以三段式收尾：先重述方法定位與核心結果，再點出已知限制，最後談 broader impacts 與致謝。作者重申 Vista4D 是一個「以 temporally-persistent 4D point cloud 對 seen content 進行顯式保留、並以 4D-reconstructed dynamic multiview data 訓練 video diffusion 以對抗真實世界點雲 artifacts」的 video reshooting 框架。它在 4D consistency、camera control accuracy、video fidelity 三個維度被量化、質化與 user study 全面驗證勝過 SOTA，且能延伸到 dynamic scene expansion、4D scene recomposition 與 long video inference with memory 等實際應用——這些再度呼應 §1 的 contributions 與 §4 的章節順序。

Limitations 段落集中在一個明確的設計缺口：使用者目前無法調控「要多忠於 point cloud」 vs.「要多依賴 video model prior 來修正幾何」之間的權衡。作者指出，當點雲本身有不完美時，模型只會以 fixed 的方式做修正；他們提議的 future work 是引入一個可在 explicit prior（point cloud）與 implicit prior（source video + camera embedding）之間 interpolate 的控制機制，讓使用者依 use case 取捨。這個方向也順帶承接了 §4.3 ablation 中觀察到的「兩種 prior 互補」結論。

Broader impacts 則承認，作為基於 video diffusion 的方法，Vista4D 繼承了大型生成模型固有的倫理疑慮：對任何影片進行相機控制都可能改變其情感影響與公眾觀感，引發 content ownership 與 transformative work 的爭議。最後致謝段點名來自 Eyeline Labs/Netflix 與外部合作者的技術討論、demo 演出與製作支援，沒有實質技術貢獻補充。整體 §5 短而精準，把方法成果、未解問題與後續方向一條線串起，為讀者留下「方法已 strong，但 controllability 仍是未來重點」的明確 takeaway。

## 4. Critical Profile

### 4.1 Highlights

- 在自製 110 段 video-camera pair 評測集上，Vista4D 在相機控制誤差全面領先：translation error 1.251、rotation error 4.647、intrinsics error 4.927，皆優於 GEN3C/EX-4D/TrajectoryCrafter (Table 1, p. 4)。
- 同表的 3D consistency 指標 RE@SG 為 7.504，遠低於最接近的 GEN3C (12.99) 與顯著優於 TrajectoryCrafter (120.5)，顯示 4D-grounded point cloud 確實壓低了重投影誤差 (Table 1, p. 4)。
- 在 iphone dataset 的 novel-view video synthesis 上，mPSNR 14.09、mLPIPS 0.461、EPE 1.142 同時取得最佳，EPE 約為次佳 TrajectoryCrafter (2.375) 的一半 (Table 2, p. 4)。
- 在 explicit-prior baseline 比較中，Vista4D 在 aesthetic quality (0.567)、imaging quality (0.716)、temporal style (0.253) 與 human anatomy (0.857) 等 VBench 子項皆為最高 (Table 3, p. 5)。
- User study 中 42 位受試者於 30 段 pair 上選出 Vista4D 在 source preservation (67.06%)、camera accuracy (68.17%)、overall fidelity (77.38%) 三維度皆以絕對多數勝出 (Table 4, p. 5)。
- 透過 in-context concatenate latent token 同時餵入 source video 與 point cloud render，讓模型學「修正不完美點雲」而非單純 inpainting (§3.2–3.3, p. 4)。
- 在訓練資料上採 MultiCamVideo + STream3R 的合成多視角資料與 OpenVidHD-0.4M 的 monocular + π3 混合 (1:1)，使 4D reconstruction artifact 暴露給模型 (§3.4, p. 5)。
- Figure 6 (p. 7) 演示了即使 Grounded SAM 2 漏切網球拍導致 streaking artifact，模型仍可透過 in-context source video 修正幾何瑕疵。
- 額外延伸應用：Figure 7 的 dynamic scene expansion、Figure 8 的 4D scene recomposition (含跨光照插入犀牛)、以及 Figure 9 的 chunk-autoregressive 長片推論 (>400 frames)，皆在同一架構下達成 (§4.4, pp. 7–8)。
- Plücker embedding 以 zero-init linear projection 注入、在 self-attention 後接 identity-init affine projector，這套輕量化 ReCamMaster-style 注入讓 14B base model 僅需訓練 patchify/self-attention/camera encoder/projector (§3.3, §B, p. 13)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- **缺乏 explicit/implicit prior 之間的使用者可調介面**：當點雲本身有瑕疵時，使用者無法決定模型該「忠於點雲」還是「以影片先驗修正」，作者點名這是未來延伸方向 (§5 Limitations, p. 8)。
- **生成式相機控制的倫理疑慮**：作者承認 video diffusion 重拍會深刻改變影片觀感與情緒效應，引發內容所有權與 transformative work 的爭議 (§5 Broader impacts, p. 9)。

#### 4.2.2 Phyra-inferred

- **camera accuracy 的評估與訓練/推論皆使用同一個 π3 模型來估姿態 (§4.1, p. 5；§E, p. 21)，存在 circular evaluation：被測影片的「真實相機」與生成影片的「預測相機」由同一個 4D reconstructor 給出，可能系統性偏好點雲條件式方法。
- **explicit-prior 方法的 FID/FVD/consistency 落後是被作者用一句「baselines 因相機跟得差所以畫面偏靜態才看起來好」帶過 (Table 3 caption, p. 5)，但並未提供「校正相機差異後再比 FID/FVD」的實驗來證實這個解釋。
- **base model 規模差異未被控制**：Vista4D 跑 Wan2.1-T2V-14B，而 ReCamMaster/CamCloneMaster 跑 Wan2.1-T2V-1.3B、TrajectoryCrafter 跑 CogVideoX-Fun-5B (Table 5, p. 21)，因此「Vista4D 勝出」與「14B 比 1.3B/5B 強」兩個因素糾纏，無消融。
- **mSSIM 0.480 落後 TrajectoryCrafter 的 0.492 (Table 2, p. 4) 被以「肉眼看就有 artifact，SSIM 抓不到」一句帶過，未做 LPIPS-against-SSIM 的散點分析或盲測來支持「SSIM 在此 misleading」的論點。
- **核心 ablation (no depth artifacts / no source video / cross-attn vs in-context / no temporal persistence) 全數搬到 Supplementary F (§4.3, p. 7)，主文僅以一段散文描述，讀者無法核對哪個設計到底貢獻多少分。
- **推論成本龐大且未被誠實標示為缺點**：672×384 解析度約 1195 秒/clip，1280×720 達 9924 秒 (~2.76 小時) /clip on A100 80GB (Table 5, p. 21)，在實際 post-production 工作流中是否可行幾乎沒被討論。
- **720p checkpoint 僅微調 300 步 vs 672×384 的 30,000 步** (§3.4, p. 5)，意味著公開的高解析度 demo 多半是欠訓 checkpoint，但所有量化評測也只在 672×384 比較，720p 品質沒有量化基準。
- **static pixel segmentation pipeline (RAM → Llama-3.1-8B → Grounded SAM 2 反向取靜態) 失敗代價的量化研究缺席**：論文只用 Figure 6 一個「漏切網球拍」例子佐證「robust」，沒有 stress test 數據 (§4.2 Robustness to segmentation failure, p. 7)。
- **user study 設計細節仍顯薄弱**：30 段 pair × 42 人 × 3 題，但未報告 inter-rater agreement、未說明是否有訓練/說明回饋、未排除「Vista4D 顯著是 14B base 的視覺辨識度」等可能引導效應 (§D, p. 17)。
- **長片推論建立在客製化的 chunk-autoregressive π3** (§A.1, p. 13)，這個延伸並非 π3 原本支援的模式，accuracy/drift 無量化評估，僅給三段 qualitative Figures (Fig. 9, 15)。
- **iphone dataset 上的絕對 PSNR 僅 14.09/14.14 (Table 2, p. 4)，整體仍處於低保真度區段，但作者僅做相對排名，未討論這個絕對水位是否實用。

### 4.3 Phyra's Judgment (summary)

Vista4D 真正新的貢獻是兩件互補的設計：(1) 把世界座標下的「時間持續靜態像素」當成 explicit 4D 條件，以及 (2) 用含 4D 重建瑕疵的多視角合成資料訓練，將任務從 inpainting 推到「修正不完美點雲」。其餘多數技術 (Plücker embedding、in-context token concat、Wan2.1 微調) 屬扎實工程整合而非概念創新。最關鍵未解的是 evaluator/inferer 同源 (π3) 帶來的循環評估、以及 base model 體量未被消融，使「方法贏」與「14B 贏 1.3B」難以分離。整體仍是 video reshooting 領域目前最完整的 explicit-prior 方案，但「贏多少來自設計、贏多少來自規模」尚未被釐清。

## 5. Methodology Deep Dive

### 5.1 Method Overview

Vista4D 將 video reshooting 形式化為「給定來源影片 $\mathbf{X}^{src}$ 與目標相機 $\mathbf{C}^{tgt}=(\mathbf{K}^{tgt}, \mathbf{T}^{tgt})$，合成同一動態場景在目標相機軌跡下的影片 $\mathbf{X}^{tgt}$」的條件式生成問題。其方法核心由三個彼此呼應的設計組成：(1) 建立含「時間持續靜態像素」的世界座標 4D point cloud $\bar{\mathbf{P}}$，使任何幀均能看到整個場景的靜態結構；(2) 改以含 4D 重建瑕疵的合成多視角動態資料 (MultiCamVideo + STream3R) 與真實單目資料 (OpenVidHD-0.4M + π3) 混合訓練，使模型學會「修正不完美點雲」而非僅 inpainting；(3) 透過 in-context concatenation 串接 patchified latent tokens 同時條件化來源影片、點雲渲染與 alpha mask，並以 Plücker embeddings 注入目標相機。

整體流程可分為前處理、渲染與生成三段。前處理階段以 4D reconstruction 模型 (STream3R 用於合成多視角、π3 用於真實單目) 估計每幀 depth $\mathbf{D}^{src}$、camera extrinsics $\mathbf{T}^{src}$、intrinsics $\mathbf{K}^{src}$；以 RAM + Llama-3.1-8B-Instruct 篩選動態名詞，並由 Grounded SAM 2 分割每幀動態像素，反轉得到 static pixel mask $\mathbf{M}^{stc}$。透過 Eq. 1 將 RGB-D 提升至世界座標得到 per-frame point cloud $\mathbf{P}$，再依 $\mathbf{M}^{stc}$ 將靜態像素跨所有幀持續，形成 $\bar{\mathbf{P}}$。

渲染階段將 $\bar{\mathbf{P}}$ 在使用者指定的 $\mathbf{C}^{tgt}$ 下投影，產出點雲渲染影像 $\mathbf{X}^{src \to tgt}$ 與 alpha mask $\mathbf{M}^{src \to tgt}$。生成階段以 Wan2.1-T2V-14B 為基礎之 flow matching DiT $\boldsymbol{\epsilon}_\theta$ 接收 $(\mathbf{X}^{src}, \mathbf{X}^{src \to tgt}, \mathbf{M}^{src \to tgt}, \mathbf{C}^{tgt}, \mathbf{X}^{tgt}_t, t)$，預測 velocity $\hat{\mathbf{V}}$；對單目資料因無 ground-truth $\mathbf{X}^{src}$，改以 double-reprojected $\mathbf{X}^{tgt \to src}$ 充當 occluded source。微調僅更新 patchify layers (for $\mathbf{X}^{src}$ and $\mathbf{X}^{src \to tgt}$)、self-attention layers、camera encoders 與 projectors，其餘 14B 權重凍結。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: source video X_src                        [B, T=49, 3, H=384, W=672]
   │
   ├→ 4D Reconstruction (STream3R / π3)
   │     ├→ Depth     D_src                      [B, 49, 1, 384, 672]
   │     ├→ Extrinsics T_src                     [B, 49, 4, 4]
   │     └→ Intrinsics K_src                     [B, 49, 3, 3]
   │
   └→ Dynamic Pixel Segmentation
         RAM tags → Llama-3.1-8B filter → Grounded SAM 2 → invert
         └→ Static mask M_stc                    [B, 49, 1, 384, 672]

Image-to-World Lifting (Eq. 1)
   P = Ω( Φ⁻¹([X_src, D_src], K_src), T_src )    [B, 49, N≤H·W, 3]

Static Persistence
   {P, M_stc} → P̄ (static pixels persist across all 49 frames)
                                                 [B, 49, N'≈?, 3]
                       (paper does not specify N' or merge/dedup strategy)

User-defined Target cameras  C_tgt = (K_tgt, T_tgt)
                                                 [B, 49, 3, 3] / [B, 49, 4, 4]

Differentiable Point Cloud Rendering at C_tgt
   ├→ Point cloud render X_src→tgt               [B, 49, 3, 384, 672]
   └→ Alpha mask        M_src→tgt                [B, 49, 1, 384, 672]

Wan2.1 VAE Encoder (per stream; T compress 4×, S compress 8×)
   X_src,    X_src→tgt (+M_src→tgt as 4ch?), X^tgt_t (noisy)
        ⇒ z_src,  z_srctgt,  z^tgt_t            [B, T'=13, C=16, H'=48, W'=84]

Patchify (patch p=1×2×2; paper does not specify)
   each z → tokens                               [B, 13·24·42, D=?]

In-context Concatenation along frame dim
   [tokens(z_src) ⊕ tokens(z_srctgt) ⊕ tokens(z^tgt_t)]
        ⇒ joint sequence                         [B, 3·(13·24·42), D=?]

Plücker Camera Embedding for C_tgt
   per-pixel rays                                [B, 49, 6, 384, 672]
   → downsample / encode to latent grid          [B, 13, 6, 48, 84]
   → zero-init linear projection (added pre self-attn)
   → identity-init linear projection (after self-attn)

DiT ε_θ (Wan2.1-T2V-14B, partial finetune)
   self-attention over joint sequence + camera projections
   trained: patchify(X_src), patchify(X_src→tgt), self-attn, cam encoders/projectors
   frozen : everything else
   → predicts V̂ for target tokens               [B, 13·24·42, D=?]
   → un-patchify                                 [B, 13, 16, 48, 84]

Flow Matching Loss (Eq. 2)
   L = ‖ ε_θ(X^tgt_t, X_src→tgt, M_src→tgt, X_src, C_tgt, t) − V ‖,  V = X^tgt − ε

VAE Decoder
   predicted target latent → X^tgt               [B, 49, 3, 384, 672]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 4D Reconstruction Front-End

**Function:** 從來源影片估計每幀 depth、extrinsics、intrinsics，作為點雲提升 (Eq. 1) 的輸入。

**Input:**
- Name: $\mathbf{X}^{src}$
- Shape: $[B, 49, 3, 384, 672]$
- Source: 使用者輸入

**Output:**
- Name: $(\mathbf{D}^{src}, \mathbf{T}^{src}, \mathbf{K}^{src})$
- Shape: $[B, 49, 1, 384, 672]$, $[B, 49, 4, 4]$, $[B, 49, 3, 3]$
- Consumer: §5.3.3 點雲提升模組

**Processing:** 對 MultiCamVideo (合成多視角時間同步資料) 採用 STream3R (跨視角 causal transformer)，對真實單目影片採用 π3 (permutation-equivariant feed-forward)。兩者皆為 frozen，不參與後續微調。

**Key Formulas:** N/A (僅作為前端推論)。

**Implementation Details:** Depth 數值範圍 (metric vs scale-ambiguous)、世界座標慣例與第一幀對齊策略，論文未明確說明 (the paper does not specify)。

#### 5.3.2 Dynamic Pixel Segmentation Pipeline

**Function:** 產生 static pixel mask $\mathbf{M}^{stc}$，以決定哪些像素可在 4D 點雲中跨幀持續。

**Input:** $\mathbf{X}^{src}$，$[B, 49, 3, 384, 672]$。

**Output:** $\mathbf{M}^{stc}$，$[B, 49, 1, 384, 672]$ (binary)，供 §5.3.3 使用。

**Processing:** (1) 以 RAM (Recognize Anything Model) 對每幀產生語意標籤；(2) 以 Llama-3.1-8B-Instruct 從標籤集合中篩出「動態」主體/名詞；(3) 將動態名詞作為 Grounded SAM 2 的 prompt 進行分割；(4) 對每幀動態遮罩取 logical NOT 得 $\mathbf{M}^{stc}$。整體設計受 Uni4D 啟發。

**Key Formulas:** 無顯式公式；為 LLM-guided open-vocabulary segmentation pipeline。

**Implementation Details:** 論文於 §4.2 Robustness 與 Fig. 6 表明對分割失敗 (例如未將 tennis racket 標為動態) 具備一定 robustness，因 in-context 條件化的 source video 可由視訊先驗修正 streaking 等瑕疵。

#### 5.3.3 World-Space Point Cloud Lifting and Static Persistence

**Function:** 將 RGB-D 提升至世界座標形成 per-frame $\mathbf{P}$，再依 $\mathbf{M}^{stc}$ 跨幀持續靜態像素得到 4D 點雲 $\bar{\mathbf{P}}$。

**Input:** $(\mathbf{X}^{src}, \mathbf{D}^{src}, \mathbf{K}^{src}, \mathbf{T}^{src}, \mathbf{M}^{stc})$，shapes 同 §5.3.1 / §5.3.2。

**Output:** $\bar{\mathbf{P}}$，$[B, 49, N', 3]$，N' 為靜態跨幀累積後的點數 (paper does not specify 上限或去重策略)。

**Processing:** 以 Eq. 1 將像素 $[\mathbf{X}^{src}, \mathbf{D}^{src}]$ 經 inverse perspective $\Phi^{-1}(\cdot, \mathbf{K}^{src})$ 轉為相機空間 3D 點，再以 extrinsics $\Omega(\cdot, \mathbf{T}^{src})$ 變換至世界空間。對 $\mathbf{M}^{stc}=1$ 的像素，將其世界座標下的 3D 點視為跨所有 49 幀皆可見；對 $\mathbf{M}^{stc}=0$ 的像素 (即動態) 僅在當幀有效。

**Key Formulas (Eq. 1):**

$$
\vec{P} = \Omega\!\left(\Phi^{-1}\!\left([\vec{X}^{src}, \vec{D}^{src}], \vec{K}^{src}\right), \vec{T}^{src}\right)
$$

**Implementation Details:** $\Phi^{-1}$ 的具體 parameterization (e.g., inverse-depth vs linear-depth)、靜態點重複合併之去重 (e.g., voxel-grid downsampling) 與每點屬性 (RGB、normal、半徑) 論文未明確規範。

#### 5.3.4 Target Camera Point Cloud Rendering

**Function:** 將 $\bar{\mathbf{P}}$ 在使用者指定的 $\mathbf{C}^{tgt}$ 下進行可微分點雲渲染，產出 RGB 影像與覆蓋率 alpha mask 作為 in-context 條件。

**Input:** $(\bar{\mathbf{P}}, \mathbf{C}^{tgt})$，分別為 $[B, 49, N', 3]$ 與 $\mathbf{K}^{tgt}\in[B,49,3,3]$、$\mathbf{T}^{tgt}\in[B,49,4,4]$。

**Output:** $\mathbf{X}^{src \to tgt}\in[B,49,3,384,672]$ 與 $\mathbf{M}^{src \to tgt}\in[B,49,1,384,672]$，供 §5.3.5。

**Processing:** 對每個目標相機，將 $\bar{\mathbf{P}}$ 之 3D 點透過 perspective projection 投影至像素平面並著色，同時記錄每像素是否被點雲覆蓋以形成 alpha mask。

**Key Formulas:** 標準針孔投影 $\mathbf{x} = \mathbf{K}^{tgt}\,[\mathbf{R}^{tgt}|\mathbf{t}^{tgt}]\,\mathbf{X}_{world}$，論文未提供顯式公式。

**Implementation Details:** Renderer 類型 (Pulsar / 3DGS-style splatting / NeRF-based)、point radius、alpha 合成方式論文未指定。

#### 5.3.5 In-Context Conditioning Video DiT (Wan2.1-T2V-14B)

**Function:** 以 in-context concatenation 同時條件化來源影片、點雲渲染、alpha mask 與目標相機，預測 noisy target latent 之 flow matching velocity。

**Input:**
- Name: $(\mathbf{X}^{src}, \mathbf{X}^{src \to tgt}, \mathbf{M}^{src \to tgt}, \mathbf{X}^{tgt}_t, \mathbf{C}^{tgt}, t)$
- Shape: 影像 $[B,49,3,384,672]$、mask $[B,49,1,384,672]$、相機 $\{[B,49,3,3],[B,49,4,4]\}$、scalar $t$
- Source: §5.3.1, §5.3.4 與 forward diffusion 之 noisy target

**Output:**
- Name: 預測 velocity $\hat{\mathbf{V}}$
- Shape: 對應目標 latent，un-patchify 後為 $[B,13,16,48,84]$
- Consumer: Eq. 2 flow matching loss / VAE decoder

**Processing:**
1. **VAE 編碼**：以 Wan2.1 VAE (T 壓縮 4×、S 壓縮 8×、16 latent channels) 將 $\mathbf{X}^{src}$、$\mathbf{X}^{src \to tgt}$ (與 $\mathbf{M}^{src \to tgt}$ 一同處理) 與 $\mathbf{X}^{tgt}_t$ 編碼至 $[B, 13, 16, 48, 84]$。
2. **Patchify**：對 $\mathbf{X}^{src}$ 與 $\mathbf{X}^{src \to tgt}$ 各有可訓練的 patchify layer (patch size 論文未說明，Wan2.1 預設為 $1\times2\times2$)；切成 token 序列 $[B, 13\cdot24\cdot42, D=?]$。
3. **In-context 串接**：沿 frame 維度將三 stream tokens 串接，joint 序列長度為單一 stream 的 3 倍：$[B, 3\cdot(13\cdot24\cdot42), D]$。
4. **Plücker camera 注入**：將 $\mathbf{C}^{tgt}$ 編碼為 6 通道 Plücker rays $[B,49,6,384,672]$，downsample 至 latent 解析度後，以 zero-initialized linear projection 加至 self-attention 輸入；self-attention 後再經 identity-initialized projection 殘差合併 (受 ReCamMaster 啟發)。
5. **Self-attention DiT layers**：14B DiT 處理 joint 序列；只訓練 patchify layers ($\mathbf{X}^{src}$, $\mathbf{X}^{src \to tgt}$)、self-attention layers、camera encoders、projectors，其餘參數凍結。
6. **Un-patchify**：取 joint 序列中對應 noisy target 的 token 子集，還原為 latent 形狀並輸出 velocity。

**Key Formulas (Eq. 2):**

$$
\mathcal{L} = \left\lVert \boldsymbol{\epsilon}_\theta\!\left(\vec{X}^{tgt}_t, \vec{X}^{src \to tgt}, \vec{M}^{src \to tgt}, \vec{X}^{src}, \vec{C}^{tgt}, t\right) - \vec{V} \right\rVert
$$

其中 $\mathbf{V} = \mathbf{X}^{tgt} - \boldsymbol{\epsilon}$，$\mathbf{X}^{tgt}_t$ 為對 $\mathbf{X}^{tgt}$ 加入 sampled Gaussian $\boldsymbol{\epsilon}$ 的 noisy latent。

**Implementation Details:**
- Base model: Wan2.1-T2V-14B (pretrained text-to-video flow matching DiT)。
- Resolution schedule: 先以 $672\times384$ 訓練 30,000 steps，後接 $1280\times720$ 共 300 steps。
- 視訊長度 49 frames，global batch size 8，optimizer AdamW，learning rate $1\times10^{-5}$。
- 對單目資料 (無 ground-truth $\mathbf{X}^{src}$)，以 $\mathbf{X}^{tgt \to src}$ (double-reprojected) 與其 alpha mask 充當 occluded source video。
- 確切 patch size、token 維度 $D$、layer 數、camera encoder 結構與 frozen/unfrozen 參數明細列於 Supplementary B；本文僅給出高階摘要 (the paper does not specify these in the main text)。

#### 5.3.6 Training Data Curation

**Function:** 構造同時涵蓋多視角合成資料與真實單目資料的混合訓練集，使模型同時學會「修正不完美點雲」與「填補未見區域」。

**Input / Output:** Source-target video pairs 及其 4D 重建輸出 (depths、cameras) 與分割遮罩。

**Processing:**
- **MultiCamVideo (合成多視角時間同步)**：直接以 STream3R 對所有視角進行 4D 重建；source 視角點雲渲染至 target 視角，自然產生非正面視角下的幾何瑕疵 (Fig. 3 (b))，使模型暴露於真實推論時的失敗模式。
- **OpenVidHD-0.4M 60K 子集 (真實單目)**：以 π3 重建，並依 TrajectoryCrafter 之 double re-projection (target → heuristic source camera → target) 產生 occluded paired data。

**Key Formulas:** 無顯式公式；為資料管線設計。

**Implementation Details:** 動態名詞篩選使用 Llama-3.1-8B-Instruct，靜態遮罩由 Grounded SAM 2 動態遮罩反轉取得。混合比例論文未明文揭露 (the paper does not specify)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| MultiCamVideo [10] | 多視角時間同步合成影片 (4D reconstruction by STream3R [11]) | 4 種 intrinsics × 各取前 512 個 scenes (共 ~2,048 scenes) | train |
| OpenVidHD-0.4M [65] | 真實世界單目影片 (4D reconstruction by π3 [44]) | 60K 子集，過濾掉標記為 "static" 的影片並用 PySceneDetect 切除剪接 | train |
| DAVIS [68] | 真實世界動態影片 | 13 部影片 | test (110 video-camera 評估集的一部分) |
| Pexels [69] | 真實世界動態影片 (royalty-free stock) | 38 部影片 | test (110 video-camera 評估集的一部分) |
| iphone dataset [60] | 真實世界 time-synchronized multiview 動態場景 NVS | the paper does not specify exact count | test (novel-view video synthesis 評估，Table 2) |

備註：總共 51 部影片 (DAVIS 13 + Pexels 38) 各設計 2–3 條 target camera trajectories，組成 110 video-camera pairs 用於 Table 1, 3 與 user study。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Translation / Rotation / Intrinsics error | 將生成影片用 π3 [44] 與 source 共同 4D 重建後，與 target cameras 比對 (公式見 Supplementary E) | yes |
| RE@SG (reprojection error under SuperGlue) | 用 SuperPoint [58] landmarks + SuperGlue [57] 計算 source 與 output 之間的 per-frame 3D consistency | yes |
| mPSNR / mSSIM / mLPIPS | iphone dataset [60] 上的 masked novel-view 合成品質 | yes |
| PSNR / SSIM / LPIPS | iphone dataset 上未遮罩的整幀合成品質 | no |
| EPE (endpoint error) | optical flow endpoint error，衡量生成影片與 ground truth 的場景動態還原 | yes |
| FID [71] / FVD [72] | 影片視覺保真度與分佈相似度 | no |
| CLIP-T [73] | 與 prompt 的對齊度 | no |
| VBench [61] (aesthetic quality, imaging quality, subject consistency, background consistency, temporal style) | 影片品質多維評估 | no |
| VBench-2.0 [62] (human anatomy) | 人體解剖正確性 | no |
| User study (source preservation / camera accuracy / overall fidelity) | 42 位參與者於 30 對 video-camera pairs 上的偏好率 | yes |

### 6.3 Training and Inference Settings

- Base model：Wan2.1-T2V-14B [2]，主 checkpoint；另額外 finetune Wan2.1-I2V-14B 用於 long-video chunked inference (Supplementary C.2)。
- 解析度與步數：先以 $672 \times 384$ finetune 30,000 steps，再以 $1280 \times 720$ finetune 300 steps，每段影片 49 frames。
- Optimizer：AdamW，learning rate $1 \times 10^{-5}$，global batch size 8。
- 可訓練參數：source video 與 point cloud render 的 patchify layers、self-attention layers、camera encoders、projector；其餘凍結 (Supplementary B 詳述 zero-init alpha-mask patchify 與 identity-init projector)。
- 條件 dropout：source video / point cloud render / prompt / camera 條件各 10% random drop；I2V 變體額外對 image 條件做 30% drop 並加 $\alpha = 0.05$ 的 noise augmentation $\tilde{X}_{\text{img}} = (1-\alpha)X_{\text{img}} + \alpha \epsilon$ (Supplementary C.2)。
- 資料採樣：multiview 與 monocular videos 採 1:1 比例；MultiCamVideo 因 source/target first frame 必相同，做 50% random time-reversal 以打破 matching-first-frame 限制。
- Inference：所有方法皆 50 steps；硬體為 NVIDIA A100 80GB；Vista4D 在 $672 \times 384$ 下 segmentation 22.75s、4D reconstruction (π3) 3.110s、model inference 1195s，720p 下 model inference 上升至 9924s (Table 5)。
- 評估時統一以 $672 \times 384$ checkpoint 進行所有量化比較與 user study；對不支援不同首幀 source/target camera 的 baselines，採用 TrajectoryCrafter 的 `infer_direct` 流程作公平比較 (Supplementary D)。

### 6.4 Main Results

Camera control 與 3D consistency (110 video-camera pair eval set，Table 1)：

| Method | Translation err ↓ | Rotation err ↓ | Intrinsics err ↓ | RE@SG ↓ | Notes |
|---|---|---|---|---|---|
| ReCamMaster [10] | 1.574 | 12.79 | 11.16 | 23.66 | implicit prior |
| CamCloneMaster [22] | 2.132 | 23.77 | 6.422 | 23.38 | implicit prior |
| TrajectoryCrafter [7] | 1.434 | 6.838 | 6.671 | 120.5 | explicit, point cloud |
| EX-4D [9] | 1.325 | 5.941 | 5.182 | 13.11 | explicit, point cloud |
| GEN3C [8] | 1.309 | 4.751 | 5.085 | 12.99 | explicit, point cloud |
| **Vista4D (ours)** | **1.251** | **4.647** | **4.927** | **7.504** | 全項最佳，RE@SG 大幅領先 |

Novel-view video synthesis (iphone [60]，Table 2)：

| Method | mPSNR ↑ | mLPIPS ↓ | PSNR ↑ | LPIPS ↓ | EPE ↓ | Notes |
|---|---|---|---|---|---|---|
| ReCamMaster | 10.84 | 0.692 | 10.96 | 0.755 | 4.681 | |
| CamCloneMaster | 11.14 | 0.651 | 11.17 | 0.713 | 4.318 | |
| TrajectoryCrafter | 13.82 | 0.569 | 13.06 | 0.656 | 2.375 | SSIM 在 mSSIM/SSIM 為 0.492/0.320 |
| EX-4D | 12.85 | 0.596 | 12.64 | 0.669 | 4.269 | |
| GEN3C | 12.19 | 0.608 | 12.06 | 0.679 | 3.019 | |
| **Vista4D (ours)** | **14.09** | **0.461** | **14.14** | **0.514** | **1.142** | mSSIM 0.480 (TrajectoryCrafter 較高，但作者指其有可見 artifacts) |

Video fidelity (Table 3)：Vista4D 在 CLIP-T (0.326)、aesthetic quality (0.567)、imaging quality (0.716)、temporal style (0.253)、human anatomy (0.857) 取得最佳；FID/FVD 與 subject/background consistency 略遜於 implicit-prior baselines，作者解釋為這些方法 camera 幾乎不動，靠近 source 自然分數高。

User study (Table 4，42 人 × 30 pairs)：Vista4D 在三項偏好率分別為 source preservation 67.06%、camera accuracy 68.17%、overall fidelity 77.38%，皆遠高於最強 baseline (CamCloneMaster 11–15% 區間、GEN3C 5–11%)。

### 6.5 Ablation Studies

論文於 §4.3 與 Supplementary F 報告 ablations，組合以下設計：(a) no depth artifacts (一律使用 double reprojection 訓練，等同只做 inpainting)；(b) no source video (移除 source video 條件)；(c) cross-attention source video injection (改用 TrajectoryCrafter 風格而非 in-context concat)；(d) no temporal persistence (取消 static pixel 跨幀持續性)。主要結論：

- Depth artifacts + in-context source video：兩者結合是 Vista4D 對 4D reconstruction artifacts (空間：非正面視角的不準確深度；時間：抖動深度) 的關鍵。屬診斷型 ablation，直接對應 §3.2 與 §3.3 的核心宣稱。
- Cross-attention vs. in-context source 條件 (對應 §3.3)：in-context 對 source content 保留更佳、對 point cloud artifacts 更穩健。屬診斷型 ablation，回答了 "為何不沿用 TrajectoryCrafter 的 cross-attn 注入"。
- 移除 temporal persistence (對應 §3.1)：當 source video 與 target cameras 每幀重疊低時，static content 保留與 camera 控制均下降。屬診斷型 ablation。
- 無 source video / 無 depth artifacts 兩支單獨 ablation 偏向 sanity check (預期會壞)，但與其他組合一起呈現時，能切出「資料端」與「條件端」的貢獻。

⚠️ 限制：論文僅以定性圖示 (Supplementary F) 呈現，未在正文提供 ablation 的量化數字表 (即未報出每個變體在 Table 1/2/3 metrics 上的差值)；the paper does not specify 各 ablation 在 RE@SG / EPE / FID 等指標上的具體下降幅度。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 與五個近期 SoTA 比較：TrajectoryCrafter (ICCV'25)、GEN3C (CVPR'25)、EX-4D、ReCamMaster (ICCV'25)、CamCloneMaster (SIGGRAPH Asia'25)，涵蓋 explicit-prior 與 implicit-prior 兩類。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 量化跑 110 video-camera pair eval set (DAVIS+Pexels)、iphone dataset 真實多視角；定性涵蓋 dynamic scene expansion、4D scene recomposition、long-video inference 三個衍生應用。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — Depth artifacts、in-context vs cross-attn、temporal persistence 屬診斷；但只有定性結果，未配合 Table 1–3 上的數值差，難以量化各成分的貢獻 (Supplementary F)。
- [missing] Has a scaling study (size, length, or compute) — 未針對模型大小 (僅用 14B) 或訓練步數做 scaling 研究；只有 $672 \times 384 \to 1280 \times 720$ 兩個解析度 checkpoint，且 720p 僅 train 300 steps，並非 scaling 探究。
- [covered] Has an efficiency / wall-clock comparison — Table 5 列出 segmentation、4D reconstruction、model inference 的秒數 (A100 80GB，50 steps)，並坦承 Vista4D 較慢 (in-context conditioning + 較大 base model)。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — Table 1–3 皆為單一 run 的點估計，無 std 或 multi-seed；user study 的偏好率亦未報置信區間。
- [partial] Releases code / weights / data sufficient for reproducibility — 文中宣稱會於 project page (eyeline-labs.github.io/Vista4D) 釋出 code、weights、110-pair eval set 與 camera design UI；但訓練資料含 OpenVidHD-0.4M 60K 子集的具體 ID list、MultiCamVideo 子集索引並未於正文列出，且發表時實際 release 狀態無法從論文文字本身驗證。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1：在 explicit 4D point cloud grounding 下顯式保留可見內容、並提供豐富相機訊號。**
  支持。Table 1 (p. 4) 的 RE@SG 7.504 vs GEN3C 12.99；Table 4 (p. 5) 的 67.06% source preservation 偏好率，皆吻合此主張。但「temporal persistence 帶來多少分」需看 Supplementary F 的 ablation 才能拆解，主文只給定性論述。
- **Claim 2：以含 4D 重建瑕疵的多視角資料訓練讓模型學會修正而非 inpaint。**
  部分支持。Figure 3 (p. 3) 直觀說明訓練/推論瑕疵分布的對齊；Figure 6 (p. 7) 顯示對 segmentation 失敗的修正能力。然而「修正 ≠ inpaint」的決定性實驗（如同視角下強制注入合成 depth artifact 看模型修復）並未提供，仍以 ablation+qualitative 為主。
- **Claim 3：camera control、3D consistency、video fidelity 全面超越 SOTA。**
  部分支持。camera control (Table 1) 與 3D consistency 是清楚勝出；但 fidelity 上 explicit-prior 內部的確最佳，對 implicit-prior 卻在 FID/FVD/subject/background consistency 落後 (Table 3, p. 5)。作者以「baseline 相機跟不上所以畫面靜態」解釋，但無實驗校正混淆，故這項屬 partial。
- **Claim 4：方法可延伸至 dynamic scene expansion、4D scene recomposition、long video inference with memory。**
  部分支持。三個應用都有 qualitative demo (Figs. 7–9, 13–15)，且確實展示同一 checkpoint 多用途；但三項皆無量化評估 (沒有 expansion 的 fidelity 對照、沒有 recomposition 的 user study、長片無 drift 量測)，故定性可信、定量未驗。

### 7.2 Fundamental Limitations of the Method

**循環評估與 4D backbone 相依性。** 推論時用 π3 做 4D reconstruction，camera accuracy 評估時也用 π3 把生成影片回算成相機姿態 (§E, p. 21)。這意味 Vista4D 的「相機準確度」其實在比「生成影片是否能被 π3 重建出與訓練條件一致的姿態」。要消除這層循環，需要至少一個獨立 SfM/SLAM (例如 GLOMAP) 或 ground-truth multi-camera capture，但作者明說傳統方法在動態場景下會崩，因此目前無法在現有公開資料集上提供獨立 verification。

**對 static/dynamic segmentation 的承諾過強。** 所有「temporal persistence」的價值都建立在「可被 RAM+Llama+Grounded SAM 2 正確標為靜態的像素」上 (§3.4, p. 5；§C.1, p. 15)。當場景幾乎全動 (流水、群眾、煙、火、晃動樹葉) 或 segmentation 漏切大面積動態主體時，世界座標 4D point cloud 等同退化為單幀 3D point cloud，方法相對 baseline 的優勢應顯著縮小。論文沒有報告這類 worst-case 上的退化曲線。

**推論成本與 base model 綁定。** 1195 秒/49 frames (672×384) 與 9924 秒/49 frames (1280×720) 的成本來自 14B base model + in-context token concat (Table 5, p. 21)。In-context concat 的 attention cost 隨 frame 維度線性放大，且這一架構選擇是核心貢獻之一，難以被「換小模型」消除而不傷害品質。後製場景下 hours-per-clip 的延遲意味著此方法目前不適合 iterative directing。

**explicit prior 與 video model prior 之間沒有可調融合介面。** 作者已點明這是 Limitation (§5, p. 8)。在當前公式 (Eq. 2, p. 4) 中，模型在訓練時就決定了「在哪些情況忠於點雲、在哪些情況忠於 source video」，使用者只能透過 segmentation 邊界或重建出的點雲幾何間接影響行為。這在 production 中等於「導演無法在 take 之間調整 trade-off」，是一個結構性而非超參數性的限制。

### 7.3 Citations Worth Tracking

- **[7] TrajectoryCrafter (ICCV 2025)**：本文最重要的對照基線、double-reprojection 技術源頭、以及 baseline inference 模式 (`infer direct mode`) 的提供者。讀此文可理解 explicit-prior 路線的「inpainting 化」根因。
- **[10] ReCamMaster (ICCV 2025)**：提供 MultiCamVideo 訓練資料、以及 Plücker embedding + identity-init projector 的注入範式。Vista4D 的工程基底大量來自此論文。
- **[11] STream3R / [44] π3**：本論文 4D reconstruction backbone；尤其 π3 同時負責訓練、推論、評測，理解其失效模式對複現與獨立 verification 至關重要。
- **[2] Wan2.1-T2V-14B**：base model；由於本文未做 base model 規模 ablation，要評估 Vista4D 真實貢獻必須先理解這個 14B 模型相對 1.3B/5B 在 motion/geometry 上的天生差距。
- **[62] VBench-2.0**：本文用於 human anatomy 0.857 vs baseline 最高 0.790 的關鍵差距 (Table 3, p. 5)；要判斷此一指標是否真正衡量「點雲修正能力」而非「14B base model 的 prior」，需先理解該 benchmark 的定義與已知偏差。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 若改用獨立於訓練 backbone 的 4D reconstructor (例如 MegaSAM 或 GLOMAP) 重做 Table 1 的相機誤差評估，Vista4D 的領先幅度是否仍維持？
- [ ] 在「全動態場景」(例如海浪、群眾) 上，static pixel 比例 < 10% 時，temporal persistence 帶來的優勢相對 GEN3C 是否會消失？論文未提供此切片。
- [ ] base model 控制：把 baselines 也接到 Wan2.1-T2V-14B 重訓，相對 Vista4D 還剩多少差距？
- [ ] Table 3 中 implicit-prior 在 FID/FVD/consistency 上的優勢若用「相機軌跡相似度」校正後是否真的反轉，還是 Vista4D 在自然圖像分布上仍偏離？
- [ ] 720p checkpoint 僅 300 步微調，量化評測在 672×384 進行；若把所有指標重做於 720p，Vista4D 的優勢是否仍成立？
- [ ] long video inference 的 chunk-autoregressive π3 在 N>3 個 chunk 後的 drift 是多少？論文僅給三段 qualitative。
- [ ] 4D scene recomposition 中，被插入物件的光照一致性是來自 video model prior 還是 point cloud appearance baking？換不同光照條件 source video 時是否仍 plausible？

### 8.2 Improvement Directions

1. **獨立的相機評估管線**。把 camera accuracy 評估從 π3 換成 SfM-only baseline (如 GLOMAP)，或使用 multi-camera capture 提供 ground-truth 相機，消除 inferer/evaluator 同源造成的循環偏差。可行性高、改動只在評測腳本。
2. **增加 base-model size 控制 ablation**。提供 Wan2.1-T2V-1.3B + Vista4D 條件設計的版本，與 ReCamMaster (Wan2.1-T2V-1.3B) 公平對拍。可行性中等，需要額外微調預算但訓練配方既有。
3. **加上 explicit/implicit prior 的可控融合 knob**。在 inference 時加入 classifier-free guidance 對 point cloud 條件做 strength scaling (s_pc) 或對 source video 條件做 (s_src)，使導演可在「忠於點雲」與「信賴 video model 補洞」間連續切換。作者本人在 Limitations 也提及，技術上是 inference-only 改動。
4. **誠實的 720p 量化評測**。延長 1280×720 微調到與 672×384 相當的 step 預算後，在同一 110 pair 評測集重跑 Tables 1–3，公開 720p 真實 SOTA 落點。可行性中等，主要是算力。
5. **dynamic-heavy scenes 的 stress test**。建立一個專門「< 10% static pixel」的子集，再跑 Vista4D vs GEN3C/EX-4D，量化 temporal persistence 在退化情境下的剩餘價值。可行性高，純資料分群與重跑。
6. **減少推論延遲**。對 in-context concatenated latent 試 token-length pruning 或 caching (例如對 source video tokens 在 denoising 多步間 reuse KV)，並評估 quality/latency Pareto。可行性中等、潛在收益大但需要 attention 層改動。
7. **long video 的量化評估指標**。針對 chunk-autoregressive 推論定義 inter-chunk drift (例如 SuperGlue RE 在 chunk 邊界的跳變、或同一靜態物件跨 chunk 的 LPIPS) 並回填到 Table 1/2。可行性高、純評測層改動。
