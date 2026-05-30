<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# OmniVGGT — OmniVGGT: Omni-Modality Driven Visual Geometry Grounded Transformer

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | OmniVGGT |
| Paper full title | OmniVGGT: Omni-Modality Driven Visual Geometry Grounded Transformer |
| arXiv ID | 2511.10560 |
| Release date | 2025-11-14 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2511.10560 |
| PDF link | https://arxiv.org/pdf/2511.10560 |
| Code link | https://github.com/Livioni/OmniVGGT-official |
| Project page | https://livioni.github.io/OmniVGGT-official/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Haosong Peng | HKUST | https://livioni.github.io/ | co-first author |
| Hao Li | NTU (Nanyang Technological University) | — | co-first author |
| Yalun Dai | NTU (Nanyang Technological University) | — | author |
| Yushi Lan | NTU (Nanyang Technological University) | — | author |
| Yihang Luo | NTU (Nanyang Technological University) | — | author |
| Tianyu Qi | Sun Yat-sen University (SYSU) | https://tymiracle.top/ | author |
| Zhengshen Zhang | National University of Singapore (NUS) | — | author |
| Yufeng Zhan | Beijing Institute of Technology / HKUST | https://ray-zhan.github.io/ | corresponding author |
| Junfei Zhang | Alibaba Group | — | corresponding author |
| Wenchao Xu | HKUST | https://huasion23.github.io/ | corresponding author |
| Ziwei Liu | NTU (Nanyang Technological University) | — | author |

### 1.2 Keywords

3D foundation model, multi-modal geometric inputs, depth estimation, camera pose estimation, multi-view stereo, vision-language-action, zero-convolution adapter, stochastic modality fusion

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al., 2025) | base model | OmniVGGT directly builds on VGGT's Alternating-Attention encoder and prediction heads as its RGB backbone. |
| Pow3R (Jang et al., 2025) | baseline | Closest competitor that injects auxiliary modalities; OmniVGGT removes its 2-input limit and runs ~30x faster. |
| DUSt3R (Wang et al., 2024) | predecessor | Pioneered feed-forward point-map regression from image pairs without geometric priors; foundational ancestor. |
| MASt3R (Leroy et al., 2024) | predecessor | Extends DUSt3R with pixel-wise correspondence for SfM-like tasks; included as a depth/pose baseline. |
| CUT3R (Wang et al., 2025) | baseline | Recurrent reformulation of DUSt3R; compared on depth and 3D reconstruction benchmarks. |
| Spann3R (Wang & Agapito, 2024) | baseline | Streaming/incremental 3D reconstruction baseline used on 7-Scenes and depth metrics. |
| ControlNet zero-conv (Zhang et al.) | influence | Inspires the zero-initialized convolution used in GeoAdapter to inject camera tokens without disrupting features. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於通用 3D 幾何感知基礎模型 (spatial foundation model) 的多模態輸入統一問題。當前主流方法如 VGGT、DUSt3R 等雖能以 feed-forward 方式同時解決深度估計、相機姿態估計與多視圖立體重建,但僅接受 RGB 影像為輸入,忽略了在 VR/AR、自駕、機器人等實際場景中常可取得的相機內外參與深度圖等輔助幾何線索;少數嘗試結合多模態的 Pow3R 又最多僅支援兩種輸入。作者提出 OmniVGGT,透過輕量化 GeoAdapter 與隨機多模態融合訓練,讓單一模型可在訓練與推論階段彈性接受任意數量、任意組合的幾何輔助輸入,並進一步將其作為視覺-語言-動作 (VLA) 模型的空間骨幹以提升機器人操控表現。

### 2.2 Domain Tags

- 3D Computer Vision
- Spatial Foundation Models
- Multimodal Learning
- Vision-Language-Action / Robotics

### 2.3 Core Architectures Used

- **VGGT backbone (Alternating-Attention encoder)**:作為 OmniVGGT 的 RGB 主幹,沿用其 $L=24$ 層 frame-wise 與 global self-attention 交替的 transformer 編碼器,並保留 depth head、point head、camera head 三組預測頭。
- **DINO patchifier**:作為影像 spatial token 的提取器,將輸入影像切塊並編碼為 spatial tokens $e_f$,直接繼承自 VGGT。
- **DPT prediction heads**:用於 dense 預測 depth map $\hat{D}$、point map $\hat{P}$ 與 confidence map $\hat{Y}$,沿用 VGGT 的設計。
- **GeoAdapter (本論文提出)**:輕量化的多模態注入模組,由 camera adapter 與 depth adapter 組成,負責將相機內外參與深度圖編碼並融入 spatial foundation model;新增僅 26.8M 參數。
- **Zero-initialized convolution (zero-conv,本論文採用)**:在 camera adapter 中將輔助相機 token 從零初始化逐步累積,確保訓練起始狀態等同原 VGGT、特徵空間不被破壞;靈感來自 ControlNet。
- **Placeholder tokens (本論文提出)**:以可學習的 camera placeholder token 與 depth placeholder token 取代缺失模態的位置,使模型在推論時可接受任意子集的輔助輸入。
- **Stochastic Multimodal Fusion 訓練策略 (本論文提出)**:每個 batch 隨機抽樣輔助 modality 子集 $Q \in [0, S]$、$O \in [0, S]$,並以機率 $p\%$ 完全使用 RGB-only,使單一模型同時支援任意輸入組合並學到穩健空間表徵。
- **Kosmos-VLA 1.6B + FCN action head**:作為下游 VLA 應用的宿主架構,OmniVGGT 將其產生的 spatial tokens 注入 VLM token 流以強化 3D 空間推理,並在 CALVIN 機器人操控基準上微調評估。

### 2.4 Core Argument

作者識別出的根本問題在於:現有 spatial foundation model 將「3D 任務統一」與「輸入模態統一」視為兩件事,僅統一了輸出端,輸入端卻僵化地只接受 RGB,造成在實務上唾手可得的相機內外參與深度資訊被白白浪費。直接把這些幾何線索灌入大型基礎模型又會帶來新的根本困難:深度圖是 dense per-pixel 訊號,而相機姿態是 global attribute,兩者性質迥異,若硬性注入會在訓練早期就破壞已預訓練好的特徵空間,導致表徵崩塌。因此作者主張解決方案在邏輯上必須同時滿足三項條件:(1) 注入機制要對基礎模型「無傷」,故採用 zero-conv 將 adapter 參數從零開始累積,使初始狀態等同原 VGGT,訓練可穩定演化;(2) 因為 missing modality 是常態,模型必須能自然處理缺項,故引入 placeholder token 與隨機多模態融合策略,在每個 batch 隨機抽樣 modality 子集,使測試時能接受任意子集而不需要重新訓練多份模型;(3) 該訓練策略還必須避免模型只是在「複製貼上」輔助線索,故隨機性同時迫使模型即使在 RGB-only 條件下也學到更穩健的空間表徵——這正是論文觀察到 OmniVGGT 在無輔助輸入時也勝過 VGGT 的根因。三者缺一不可,GeoAdapter 與 stochastic multimodal fusion 共同構成在「保留基礎模型能力」與「彈性吸收任意幾何輔助輸入」之間的最小必要設計。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(260 words)

標題「OmniVGGT: Omni-Modality Driven Visual Geometry Grounded Transformer」一次點出三個關鍵字：omni-modality（全模態）、visual geometry（視覺幾何）、grounded transformer（接地式 transformer，承襲 VGGT 的命名譜系）。標題本身就是一個位置宣告：作者把自己擺在 VGGT [63] 的延伸線上，而貢獻面是「打破 RGB-only 限制」。

Abstract 的敘事弧線分四段推進。第一段點出問題缺口：當前的 3D foundation model 趨勢是統一各種 vision task，但「大多假設 RGB-only 輸入」，忽略了現實中容易取得的 camera intrinsics、poses、depth maps 等幾何線索。這建立了「為什麼要做 omni-modality」的動機。第二段提出 OmniVGGT 框架，並把核心技術濃縮成一個元件名 GeoAdapter，強調它用 zero-initialized convolutions 漸進注入幾何資訊、不破壞 foundation model 的表徵空間，並維持與 VGGT 相當的推論速度。第三段引入第二個技術元件 stochastic multimodal fusion regimen，說明訓練時隨機取樣模態子集，使測試時能接受任意模態組合，且能避免 overfit 到 auxiliary cue。第四段把實驗成果壓縮成兩條主張：(1) 在 monocular/multi-view depth、MVS、camera pose 等任務上，無論是否提供 auxiliary input 都贏過先前方法；(2) 將 OmniVGGT 接到 VLA model 後，在機械手臂操作 benchmark 上同時超越 vanilla point-cloud baseline、並能從 auxiliary depth 取得進一步增益。

整體而言，abstract 為後續每一節都埋好鉤子：§1 將展開 motivation，§4 將細寫 GeoAdapter 與 stochastic fusion，§5 將分別驗證「不需 auxiliary 也贏」與「拿到 auxiliary 更贏」這兩條主張，並以 VLA 應用作為「實用價值」的封閉論證。

### 3.2 Introduction

(577 words)

Introduction 沿用「LLM 類比」的修辭策略開場：把 VGGT [63] 之於 3D vision 等比於 ChatGPT 之於 NLP，藉此把「general 3D foundation model」這個敘事框架先架起來，並列舉 monocular/stereo depth、pose estimation、novel view synthesis 等過去各自為政的子任務，作為被統一的對象。這段話的功能是把讀者帶進「unified feed-forward model」的世界觀，讓後續所有比較對象都能落在同一張地圖上。

接著作者拋出本文的核心張力：現有 unified model（DUSt3R、MASt3R、CUT3R、VGGT）都「unify task 卻沒 unify input modality」，幾乎只接受 RGB。Pow3R [22] 是少數嘗試多模態的工作，但被釘住的限制是「最多兩個 input（例如一對 RGB 與一對 depth）」。為了讓「為什麼這個限制重要」具體化，作者列舉了三個現實場景——VR/AR 的 RGB-D、自駕的 LiDAR、機器人應用中的相機內外參——把問題從學術合理性拉到工程現實性。

論文接著進入解法宣告。第一個技術主張是 GeoAdapter：作者把難點明確刻畫為「depth 是 dense per-pixel cue，camera pose 是 global attribute」，兩者性質不同，若粗暴注入 camera 幾何資訊會破壞大規模 foundation model 的 feature space、造成早期訓練不穩。為此採用 zero convolution 處理 camera pose，從零參數漸進初始化 adapter，兼顧穩定性、表徵保真與 negligible 計算開銷，並再次強調推論速度與 vanilla VGGT 相當。第二個技術主張是 stochastic multimodal fusion strategy：訓練時隨機指派 auxiliary modality，使測試時能接受任意數量的 modality 組合，且作者明確說這個策略還有第二層好處——學到的是更 generalized、robust 的 spatial representation，而不是「直接背 auxiliary input 對應的答案」這種 shortcut。

最後一段是貢獻收束。作者把實驗成果分成兩條敘事線：第一條是傳統 3D vision 任務（mono-/multi-view depth、MVS、camera pose），主張同時打贏「有 auxiliary」與「RGB-only」兩種設定下的 SOTA；第二條是 VLA 應用，作者刻意把它放在 introduction 結尾而非 abstract 末尾，藉此把論文的「實用性論證」明白標示為一個獨立貢獻：將 OmniVGGT 接入 VLA 後，spatial understanding 勝過 vanilla point-cloud baseline，並能利用 auxiliary depth 在機器人操作上拿到 consistent gain。

從敘事工程的角度看，這個 introduction 為 §2 留下「現有 spatial foundation model 為何停在 RGB-only」的回顧任務，為 §3 留下「VGGT 的 AA block 與 token 結構」的鋪陳任務，為 §4 留下「GeoAdapter 與 stochastic fusion 的具體設計」，為 §5 留下「兩條敘事線各自驗證」的實驗任務。

### 3.3 Related Work / Preliminaries

(519 words)

Related Work 與 Preliminary 合計兩節，承擔的敘事功能不同：前者把 OmniVGGT 放回譜系裡，後者把 VGGT 的內部機制顯式化、為 §4 的 GeoAdapter 鋪好詞彙與 notation。

§2.1「3D Reconstruction」用一段話交代傳統 SfM 與近期 NeRF [39]、3DGS [25] 的版圖。重點是兩個限制——per-scene optimization 與依賴精確 camera pose——這兩點之後在 §5.4 的 7-Scenes 實驗會被回收：當 view 極稀疏、view 之間幾乎無 overlap 時，「from-scratch 估 camera pose」就是傳統方法與多數 baseline 的瓶頸，而 OmniVGGT 能直接吃 auxiliary camera 把這個瓶頸拆掉。

§2.2「Spatial Foundation Model」是核心譜系：DUSt3R [66] 是離開 SfM 管線、直接從 image pair 預測 point cloud 的起點；MASt3R [29] 強化 pixel-wise correspondence；CUT3R [65] 用 recurrent 形式換取效率；VGGT [63] 進一步擴展為 multi-view feed-forward 架構，並已被應用到 SLAM [36]、4D reconstruction [27, 79] 與 novel view synthesis [35]。這段譜系最後落在一個明確 gap：這些模型「廣泛適用於 downstream task」但「通常被限制在 RGB-only input」。這個 gap 是 OmniVGGT 在文獻地圖上的座標。

§3 Preliminary 把 VGGT 的內部機制鋪出，為 §4 的描述準備 vocabulary。輸入影像集 $I$ 先經 DINO [40] backbone patchify 為 spatial token $e_f$，與 learnable 的 camera token $e_c$、register token $e_r$ concat，由 transformer encoder $E$ 聯合處理：

$$(\hat{e}_c, \hat{e}_r, \hat{e}_f) = E(e_c, e_r, e_f).$$

其 encoder 採用 Alternating-Attention（AA）方案：frame-wise self-attention 抓 intra-image 結構，global self-attention 跨 view 聚合資訊；經 $L$ 層 AA block 之後，refined 的 $\hat{e}_f$ 與 $\hat{e}_c$ 留下做預測，$\hat{e}_r$ 丟棄。Depth 與 point map 走 DPT [45] head 輸出 $\hat{D}$、$\hat{P}$ 與 confidence map $\hat{Y}$；camera head 把 camera token 過 4 層 self-attention 加 linear layer 出 intrinsics 與 extrinsics。

從敘事工程看，Preliminary 的選材有目的性：它特別點出三件事——(1) 三類 token（spatial、camera、register）的角色，(2) AA block 的 frame-wise / global 兩段式結構，(3) 三個 prediction head。這三件事正好對應 §4 GeoAdapter 的三個介入點：camera adapter 改寫 camera token、depth adapter 改寫 spatial token、auxiliary signal 透過每一層 AA block 漸進注入。換言之，Preliminary 已經為 §4 的圖 2 建立好「在哪裡加東西、加什麼東西」的座標系。

### 3.4 Method (overview narrative)

(308 words)

Methodology（§4）開宗明義列出三條敘事線：§4.1 給出「能吃任意 auxiliary input」的整體能力宣告，§4.2 落到 GeoAdapter 的多模態注入機制，§4.3 把 stochastic 訓練策略補上。三節之間的邏輯是「介面 → 模組 → 訓練」由外而內逐層展開。

§4.1 Overview 把 OmniVGGT 的輸入介面正式化：影像集 $I = \{I_i\}_{i=1}^N$ 加上任意數量的 camera 參數 $C = \{C_j\}_{j=1}^Q$ 與 depth maps $D = \{D_k, M_k\}_{k=1}^O$，其中 $Q \le N$、$O \le N$，每張影像可能伴隨 intrinsics $K \in \mathbb{R}^{3\times 3}$ 與 pose $G = [R \mid t] \in \mathbb{R}^{4\times 4}$，或伴隨 depth map 與其有效遮罩 $M$。所有資料一次餵入網路，end-to-end 輸出 3D point map、完整 camera pose 與 intrinsics、depth map、confidence map。圖 2 是這節的視覺主軸：三類 placeholder token（camera placeholder、depth placeholder）取代缺席的 modality，使輸入介面對「modality 不齊全」天然 robust。

§4.2 GeoAdapter 把上述介面具體化為兩個 adapter——camera adapter 與 depth adapter——共同遵循「normalize → encode → inject」三段式流程，差別在於 inject 的位置與是否經過 zero-conv（細節留給後續 §5 module-detail call）。這節最重要的敘事承諾是：camera 走 zero-conv 而 depth 不走，是經由 ablation 得到的設計選擇，並非隨意對稱。

§4.3 Training Procedure 把訓練拆成兩塊：(1) Loss 沿用 VGGT 的 multi-task 損失 $L = L_{\text{camera}} + L_{\text{depth}} + L_{\text{pmap}}$，camera 用 $\ell_1$，depth 與 point map 用 confidence-aware regression 並加上 gradient 項提升局部幾何一致性。(2) Stochastic Multimodal Fusion：對長度 $S$ 的影像序列，先均勻取 $Q \in [0, S]$ 決定多少張提供 GT camera（指派給前 $Q$ 張），再獨立取 $O \in [0, S]$ 決定多少張提供 GT depth（隨機指派位置）；並以機率 $p\%$ 的 batch 完全不給 auxiliary，保證「auxiliary-free 也能跑」這個基底情境穩定。

這三節合起來鋪好下一段 §5 的測試框架：「能不能可變組合 modality？能不能 RGB-only 也贏？能不能在實際 VLA 應用中發揮？」

### 3.5 Experiments (overview narrative)

(380 words)

Experiments（§5）採取「能力證明 → 任務逐項 → 應用落地 → 設計 ablation」四段式佈局，每一段都對應 §1 與 §4 中埋下的一個承諾。

開場先交代 setting：在 19 個公開資料集上端到端訓練（涵蓋 indoor/outdoor、synthetic/real、static/dynamic），架構沿用 VGGT 的 $L = 24$ AA block，camera GeoAdapter 為每層配獨立 linear encoder（共 $L+1$ 個），depth GeoAdapter 只用一個 kernel-size 14 的 conv 把 depth patchify 到與 spatial token 同維度；總共多出僅 26.8M 參數，在 32×A100 上訓十天。Metric 沿用社群慣例：depth 用 Abs Rel 與 $\delta < 1.25$，pose 用 RRA、RTA、AUC@$30^\circ$，3D 重建用 Acc、Comp、NC。

§5.1 Auxiliary Information Guidance 是最關鍵的 capability 驗證：以 Sintel zero-shot 驗證注入不同比例 GT auxiliary 的效應。這節同時兌現兩個 abstract 主張——(1) 即使 auxiliary-free 也勝 VGGT baseline；(2) 隨 auxiliary 比例上升，depth 與 pose 指標 monotonic 改善，並有跨 modality 的「外溢效應」（注入 depth 也能改善 pose），佐證 stochastic 訓練學到的是表徵而不是 shortcut。

§5.2、§5.3、§5.4 把能力宣告拆到三個傳統任務上：mono/multi-view depth（Sintel、Bonn、NYU-v2、ScanNet、ETH3D、DTU、T&T）、camera pose（Co3Dv2、RealEstate10K）、3D reconstruction（7-Scenes）。每一節都遵循同一敘事節奏——先在 RGB-only 設定下打平或贏過 SOTA，再展示加入 auxiliary 後的顯著躍升；7-Scenes 尤其用「sparse、無 overlap」這個極端情境，把「auxiliary camera 直接拆瓶頸」的故事推到最戲劇化。

§5.5 把場景換到 VLA 應用：在 Kosmos-VLA 1.6B + FCN action head 上把 OmniVGGT 的 spatial token 注入 VLM 端，於 CALVIN 兩種 split（ABCD→D、ABC→D）做 fine-tune 與 zero-shot 評估。這節兌現的是 §1 結尾的「實用價值」承諾：RGB 版超過 point-cloud baseline，加 depth 後更上一層。

§5.6 Architecture Ablation 回過頭驗證 §4 的設計選擇：四種變體 (a) Replace、(b) One-Layer Adapter、(c) Depth ZeroConv、(d) OmniVGGT 對照，明確顯示 (d) 同時在 RGB-only 與 full-auxiliary 兩種情境拿到最佳數字，並用 PCA 視覺化解釋為何 depth 不該過 zero-conv——若加上反而把 auxiliary depth feature 中的 edge/background 結構抑制掉。

整體而言，§5 的敘事邏輯是「從 capability 試水溫，到 task 全面碾壓，到下游應用落地，最後回頭交代為什麼設計長這樣」，把 §1 與 §4 的所有承諾逐一兌現。

### 3.6 Conclusion / Limitations / Future Work

(86 words)

§6 Conclusion 採極簡寫法，僅一段話：把貢獻濃縮成「unified feed-forward model，能同時處理任意數量的影像、auxiliary information 與其組合」，並再強調兩條主張——多任務 SOTA、推論效率高，最後升華為對 3D foundation model 發展方向的宣告，主張多模態整合於統一架構是值得繼續推進的路徑。

論文沒有獨立的 Limitations 或 Future Work 段落，這是 the paper does not specify 的部分。從正文可推得幾個未明言的限制：訓練成本（32×A100 十天）對學界複製不易；§5.1 顯示 auxiliary depth 對 pose 的幫助有上限（從注入比例的邊際遞減趨勢可見）；ScanNet 上 depth 指標被 GT noise 拖累（A.5 自陳），代表評估端仍有未解決的雜訊問題；VLA 端僅在 CALVIN 一個 benchmark 驗證，尚未涉及真機。Future Work 方向、開源計畫或更多 modality（如 LiDAR 點雲）的整合在正文中未被提及。

## 4. Critical Profile

### 4.1 Highlights

- 在 Sintel zero-shot 評估中,即使無任何輔助輸入,OmniVGGT 的 depth Abs Rel 從 VGGT baseline 的 0.722 降至 0.558,RRA@5° 由 95.69 提升至 96.15,作者用以支持「stochastic multimodal fusion 並非只是複製輔助線索」的主張 (Table 1, p. 5)。
- 全量注入 100% depth 後,在 Bonn 與 NYU-v2 的 $\delta < 1.25$ 雙雙達到 99.9%,接近完美對應,顯示 GeoAdapter 在「GT 線索完整可用」時能將下游 depth 任務逼至天花板 (Table 2, p. 6)。
- 在 7-Scenes 重建上加入相機參數 $K+RT$ 帶來 65.4% 的 mean Acc 改善 ($0.104 \to 0.036$),作者歸因於該資料集 3–5 幀稀疏視角讓 from-scratch pose estimation 成為瓶頸 (Table 5, p. 8)。
- 與 Pow3R 相比,OmniVGGT 同時打破「最多兩種輸入」限制並達成 $\sim 30\times$ 推論加速 ($\sim 0.2\text{s}$ vs $> 7\text{s}$),於 Re10K 與 CO3Dv2 的 AUC@30° 也分別領先 Pow3R w/ K (Pro) 16 與 11 點 (Table 4, p. 8)。
- GeoAdapter 僅引入 26.8M 額外參數 (相對 VGGT 主幹近乎可忽略),於 32 張 A100 上訓練 10 天即可微調完成 (§5 Implementation Details, p. 5)。
- Robust-MVD 設定下,OmniVGGT w/ D 在 ETH3D 與 DTU 的 $\tau$ 達 98.7% 與 99.5%,平均 rel 從 RGB-only 的 2.1 降到 1.0,顯示 dense depth 注入對 cross-view 一致性提供顯著實證貢獻 (Table 3, p. 7)。
- 在 CALVIN ABC→D zero-shot 上,RGB-only 的 OmniVGGT 將 Kosmos-VLA (w/ rgb) 的 Avg. Len 從 3.49 推升至 3.92,作者將其作為 spatial token 對機器人操控具泛化效益的證據 (Table 6, p. 8)。
- 消融實驗 (Table 7, p. 8) 清楚顯示 zero-conv 注入相機 token 的必要性:Replace 變體在無輔助輸入時 Abs Rel 高達 0.845,而 OmniVGGT 為 0.558,印證了「參數從零累積以避免破壞預訓練特徵空間」的設計動機。
- PCA token 視覺化 (Fig. 6, p. 8) 從定性層面展示加入 depth ZeroConv 會讓 auxiliary depth token 的判別性結構消失,直接支持「depth branch 不應再加 zero-conv」的設計選擇。
- 訓練端 $Q$ 與 $O$ 於 $[0, S]$ 獨立隨機抽樣,讓單一 checkpoint 在測試端可接受任意子集而無需重新訓練多模型 (§4.3, p. 4)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

論文沒有獨立的 Limitations 段落,作者只在方法與附錄中順帶承認兩點:(1) 對 depth branch 額外加上 zero-conv 會「干擾深度資訊的有效整合」,並透過 Fig. 6 的 PCA 視覺化說明 auxiliary depth token 訊號被壓抑,故被棄用 (§4.2, p. 4 與 §A.8, p. 5);(2) 在 ScanNet 上 VGGT 與 OmniVGGT 的 Abs Rel 都偏高,作者歸因於該資料集 GT depth 雜訊大 (例如牆面與地板不平滑) 而非模型缺陷 (§A.5, p. 2)。除此之外,論文未公開討論其他失敗模式或方法本身的限制。

#### 4.2.2 Phyra-inferred

- 「RGB-only 也勝過 VGGT」這個論述在資料集間並不一致:Table 2 顯示 OmniVGGT 在 Bonn 的 Abs Rel 反而從 VGGT 的 0.053 退化到 0.064、$\delta < 1.25$ 從 97.3% 退化到 95.5%,NYU-v2 的提升也僅 0.060→0.058,因此 Sintel 上的明顯領先未必能一般化。
- VLA 主結果 (ABCD→D) 中,OmniVGGT (w/ rgb-d) 的 Avg. Len 為 4.08,僅比 Kosmos-VLA (w/ rgb-d) 的 4.04 高 0.04 (相對提升 < 1%),用「outperforms by 0.04」來支持「superior spatial understanding」是強過載敘述 (Table 6, p. 8)。
- 論文宣稱 stochastic fusion 讓 RGB-only 更穩健,但 OmniVGGT 較 VGGT 多訓練 10 epoch 並使用 19-dataset 混合,沒有「VGGT 在相同訓練量下」的對照組,因此 RGB-only 改善的因果歸因不足以支持「來自 fusion 策略本身」。
- 所有 auxiliary 實驗都假設 GT depth/pose,完全沒有 noisy/biased 輔助輸入的 sensitivity 分析,而論文宣稱的應用場景 (VR/AR、自駕、機器人) 取得的線索皆帶顯著感測噪聲,這個落差讓「實用性」論點僅在理想條件下成立。
- Camera adapter 採用 $L+1=25$ 個獨立 encoder 並對每層注入,depth adapter 卻僅 1 個 encoder 注入一次;Table 7 (b) 的 One-Layer Adapter 同時關掉「per-layer 注入」與「多層 zero-conv」,因此無法隔離兩者的相對貢獻。
- Stochastic fusion 將相機 GT 指派給「序列前 Q 張」而 depth GT 指派給「隨機 O 個 index」(§4.3, p. 4),這個位置上的非對稱可能讓 camera token 學到 anchor-frame 偏置,但完全沒有 ablation 說明為何採此設計或測試時違反此分布的退化幅度。
- 訓練超參數 $p\%$ (純 RGB batch 比例) 在 §A.2 僅口頭設為 10%,這正是 fusion 機制的核心調節旋鈕,卻無 sweep 或 sensitivity 分析。

### 4.3 Phyra's Judgment (summary)

OmniVGGT 真正新穎的貢獻是「將 VGGT 的輸入端從固定 RGB 擴張為任意數量的多模態幾何線索」這個工程整合,核心元件 (zero-conv 來自 ControlNet、placeholder token 與 modality dropout 在 multimodal learning 已成熟、Alternating-Attention 直接沿用 VGGT) 多為既有設計的合理組合。實驗確實展示了在 GT 輔助輸入可用的理想條件下顯著增益,但「RGB-only 仍勝過 VGGT」與「VLA 提升源自更佳空間表徵」兩個延伸論點都缺乏控制變因實驗,目前更像 stochastic regularization 與更大訓練資料的副作用,而非 fusion 策略本身的證據。核心未解問題是:當輔助輸入帶噪、或測試 modality 分布偏離訓練分布時,GeoAdapter 是否仍穩定。

## 5. Methodology Deep Dive

### 5.1 Method Overview

OmniVGGT 的核心是「VGGT 主幹 + 輕量 GeoAdapter + 隨機多模態融合訓練」三件套設計,目標是讓單一 spatial foundation model 在訓練與推論階段都能彈性接受任意數量、任意組合的相機內外參與深度圖等幾何輔助輸入,而完全不破壞 VGGT 原本的純 RGB 推論能力 (paper §4.1)。輸入是一組影像 $I=\{I_i\}_{i=1}^{N}$ 加上選擇性的相機參數集合 $C=\{C_j\}_{j=1}^{Q}$ ($Q \le N$) 與深度圖集合 $D=\{D_k, M_k\}_{k=1}^{O}$ ($O \le N$),輸出則延續 VGGT 的三項預測:depth maps、camera poses、3D point maps,以及對應的 confidence maps。

GeoAdapter 由 camera adapter 與 depth adapter 兩個子模組組成,兩者皆採「正規化 → encode → 注入」三步流程,但**注入時機與機制刻意不對稱**:相機參數是 global attribute,需要在 $L=24$ 個 Alternating-Attention block 之前**逐層**透過 zero-initialized convolution ($\text{ZC}_l$) 加到 camera token 上,以避免一開始就破壞預訓練特徵空間;深度圖則是 dense per-pixel 訊號,只在 encoder **入口加一次**到 spatial token 上,且根據 ablation 實驗加 zero-conv 反而會干擾深度資訊整合 (paper §4.2 末段)。對於缺項的 frame,作者不留空,而是塞入可學的 `placeholder token` ($e^{\text{plh}}_c$ 與 $e^{\text{plh}}_d$),這一設計讓模型能在同一 forward pass 中混合處理「有/無相機」與「有/無深度」的不同 frame 子集。

訓練端的 stochastic multimodal fusion 策略才是讓上述架構真正可用的關鍵:每個 batch 都隨機抽樣 $Q \in [0,S]$ 個 frame 給 GT 相機、$O \in [0,S]$ 個 frame 給 GT 深度,且以機率 $p\%$ 的 batch 完全只用 RGB 訓練。這個策略一次解決了三件事:(1) 推論時可接受任意子集而不需要重新訓練多份模型;(2) 強迫模型即使在 RGB-only 條件下也學到穩健的空間表徵 (這正是 OmniVGGT 在無輔助輸入時也勝過 VGGT 的根因);(3) 維持訓練穩定性。整體 GeoAdapter 僅引入 26.8M 額外參數,推論速度與 VGGT 相當,在 8 張 NVIDIA A100 GPU 上以 32 卡訓練十天完成 (paper §5 Implementation Details)。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input (per training/inference instance):
  Images       I  ∈ R^{B × N × 3 × H × W}        (e.g. H=W=518, patch=14 ⇒ P=(H/14)×(W/14))
  Cam params   {K_j ∈ R^{3×3}, G_j=[R|t] ∈ R^{4×4}}_{j=1..Q},  Q ≤ N
  Depth + mask {D_k ∈ R^{H×W}, M_k ∈ {0,1}^{H×W}}_{k=1..O},     O ≤ N

  ├→ DINO patchify (per frame)
  │       I  → spatial tokens  e_f  ∈ R^{B × N × P × d}
  │
  ├→ Camera Adapter
  │     ├ Normalize: align coord origin to cam 1, scale by mean ‖t_j − t_1‖₂
  │     │     {K_j, G_j}  →  g_j = {q ∈ R^4, t ∈ R^3, f ∈ R^2}  ∈ R^{B × Q × 9}
  │     │
  │     └ For each AA layer l ∈ {0, …, L}:        # L = 24, so 25 independent encoders
  │           E^cam_l (single Linear)   :  g_j        → e^aux_{c,j,l} ∈ R^{B × N × d}
  │           Substitute placeholder    :  m_i · e^aux_{c,i,l} + (1−m_i) · e^plh_c
  │           ZC_l (zero-conv, init=0)  :  → injected into camera token e_c
  │
  ├→ Depth Adapter (encoder input only, not per-layer)
  │     ├ Per-batch normalize valid depths by mean over batch's valid pixels
  │     ├ Concat mask along channel    :  X_k = [D_k ; M_k]  ∈ R^{B × O × 2 × H × W}
  │     └ E^dpt (single Conv2d, k=14)  :  X_k → e^aux_{d,k} ∈ R^{B × N × P × d}
  │
  ├→ Build encoder inputs (Eq. 5, Eq. 8)
  │     Spatial : e'_f,i  = e_f,i + ( n_i · e^aux_{d,i} + (1−n_i) · e^plh_d )
  │     Camera  : e'_c,i,l = e_c,i,l + ZC_l( m_i · e^aux_{c,i,l} + (1−m_i) · e^plh_c )
  │     Register: e_r       ∈ R^{B × N × R × d}                       # R = ?  (not specified)
  │
  ├→ Alternating-Attention Encoder  ×L=24 blocks
  │     Each block:  Frame-Attention (intra-image)  →  Global-Attention (cross-view)
  │     Camera tokens receive ZC_l injection at every block.
  │     Output: (ê_c ∈ R^{B × N × d},  ê_r,  ê_f ∈ R^{B × N × P × d})
  │     ê_r is discarded after encoder (per VGGT).
  │
  └→ Prediction Heads (parallel, all from ê_f / ê_c)
        ê_f → DPT Depth Head : D̂ ∈ R^{B × N × H × W},  Ŷ_d ∈ R^{B × N × H × W}
        ê_f → DPT Point Head : P̂ ∈ R^{B × N × 3 × H × W}, Ŷ_p ∈ R^{B × N × H × W}
        ê_c → 4× Self-Attn + Linear : {K̂, Ĝ} parameterized as {q̂, t̂, f̂} ∈ R^{B × N × 9}
```

### 5.3 Per-Module Breakdown

#### 5.3.1 DINO Patchification

**Function:** 將每張 RGB 影像切成 patch token,作為後續 transformer encoder 的 spatial token。沿用 VGGT 的 DINOv2 backbone,本論文未對其修改 (paper §3 Preliminary)。

**Input:**
- Name: $I$
- Shape: $[B, N, 3, H, W]$
- Source: dataset (e.g. resized to width 518)

**Output:**
- Name: $e_f$
- Shape: $[B, N, P, d]$ where $P = (H/14)\times(W/14)$
- Consumer: Depth Adapter (相加處) 與 Alternating-Attention Encoder

**Processing:**

每張 $H\times W$ 影像以 patch size 14 切成 $P$ 個 patch,經 DINOv2 編碼為 $d$ 維 token,所有 $N$ 個 frame 的 spatial token 沿 frame 軸串接,與後續 learnable camera token $e_c$、register token $e_r$ 一起送入 encoder (Eq. 1)。

**Implementation Details:**

論文沿用 VGGT 的 DINOv2 backbone 設定,未揭露 token 維度 $d$ 的具體數值;DINO patch 大小為 14,與 depth encoder 的 conv kernel size 對齊 (paper §5 Implementation Details)。

#### 5.3.2 Camera Adapter

**Function:** 將每個 frame 的相機內外參編碼成 camera token 維度的向量,並透過 zero-conv 在 $L+1=25$ 個位置(每個 AA block 之前各一次)注入到 learnable camera token,使預訓練特徵空間從零開始累積相機資訊而不被破壞。

**Input:**
- Name: $\{K_j, G_j\}_{j=1}^{Q}$
- Shape: 內參 $[B, Q, 3, 3]$、外參 $[B, Q, 4, 4]$;以及每 frame 的二元指示子 $m_i \in \{0,1\}$
- Source: 資料集中可選的相機標註

**Output:**
- Name: 對 camera token 的逐層加項 $\text{ZC}_l(\cdot)$
- Shape: $[B, N, d]$,於每個 AA block 之前加到 $e_c$
- Consumer: Alternating-Attention Encoder

**Processing:**

(1) **正規化座標系**:把第 1 個相機設為座標原點,並用其餘相機到原點的平均距離 $s$ 作 scale,將所有 pose 正規化 (Eq. 2, 3)。 (2) **參數化**:把 $\{K, G\}$ 表示為 9 維向量 $g = \{q, t, f\}$,其中 $q \in \mathbb{R}^4$ 為旋轉四元數、$t \in \mathbb{R}^3$ 為平移、$f \in \mathbb{R}^2$ 為視場 (FOV),沿用 VGGSfM 的參數化 [62]。 (3) **逐層編碼**:第 $l \in \{0,\dots,L\}$ 個 AA block 之前,以該層專屬的 $E^{\text{cam}}_l$ (單一 linear layer) 把 $g_j$ 投影為 auxiliary camera token $e^{\text{aux}}_{c,j,l} \in \mathbb{R}^d$ (Eq. 4)。 (4) **placeholder + zero-conv 注入**:對缺相機資訊的 frame 用零向量 $e^{\text{plh}}_c$ 替代,所有 token 經過該層 zero-conv $\text{ZC}_l$ 後加到 camera token (Eq. 5)。

**Key Formulas:**

$$
s = \frac{1}{Q-1}\sum_{j=2}^{Q}\|t_j - t_1\|_2,\qquad G'_j = G_j G_1^{-1}
$$

$$
e'_{c,i,l} = e_{c,i,l} + \text{ZC}_l\!\left(\,m_i \cdot e^{\text{aux}}_{c,i,l} + (1-m_i)\cdot e^{\text{plh}}_c\,\right)
$$

**Implementation Details:**

每個 $E^{\text{cam}}_l$ 是單一 linear layer,共 $L+1 = 25$ 個獨立 encoder;zero-conv 的權重從 0 初始化,使初始狀態下 GeoAdapter 對 VGGT 的輸出沒有任何擾動,訓練可從 VGGT 的預訓練狀態穩定演化 (paper §4.2 Camera Adapter; ControlNet-style zero-conv [Zhang et al.])。

#### 5.3.3 Depth Adapter

**Function:** 將每個 frame 的輔助深度圖與有效遮罩編碼成與 spatial token 同維度的 dense token,**僅在 encoder 入口一次性**加到 spatial token 上;與相機分支不同,深度分支不使用 zero-conv (ablation 顯示加 zero-conv 反而會被視為 noise)。

**Input:**
- Name: $\{D_k, M_k\}_{k=1}^{O}$
- Shape: $[B, O, H, W]$ (depth) 與 $[B, O, H, W]$ (mask);frame-level 指示子 $n_i \in \{0,1\}$
- Source: 資料集中可選的深度標註 (RGB-D、LiDAR、合成等)

**Output:**
- Name: 對 spatial token 的加項
- Shape: $[B, N, P, d]$
- Consumer: Alternating-Attention Encoder

**Processing:**

(1) **per-batch 正規化**:用 mask 找出有效像素,以該 batch 內所有有效深度的平均值正規化各 frame 的 depth (paper §4.2 Depth Adapter)。 (2) **拼接通道**:把正規化後的 depth 與 mask 沿 channel 維度拼接成 $X \in \mathbb{R}^{2 \times H \times W}$ (Eq. 6)。 (3) **單次卷積編碼**:用 kernel size $14$ 的 Conv2d $E^{\text{dpt}}$ 把 $X$ patchify 成與 spatial token 相同維度的 token $e^{\text{aux}}_{d,k}$ (Eq. 7)。 (4) **placeholder + 直接相加**:對缺深度的 frame 用 $e^{\text{plh}}_d$ 替代,然後直接加到對應 spatial token (Eq. 8),不經 zero-conv。

**Key Formulas:**

$$
X_k = [D_k\,;\,M_k] \in \mathbb{R}^{2\times H \times W},\qquad e^{\text{aux}}_{d,k} = E^{\text{dpt}}(X_k)
$$

$$
e'_{f,i} = e_{f,i} + \big(\, n_i\cdot e^{\text{aux}}_{d,i} + (1-n_i)\cdot e^{\text{plh}}_d \,\big)
$$

**Implementation Details:**

整個 depth GeoAdapter 只有一個 conv encoder (kernel 14, stride 14, output 維度對齊 spatial token);ablation Table 7 顯示 (c) Depth ZeroConv 變體在「有完整輔助」設定下 Abs Rel 反而劣化到 0.505 vs 完整版的 0.106,作者推論模型會把 zero-conv 早期輸出的弱訊號當 noise 過濾掉 (paper §5.6 與 Fig. 6 PCA 視覺化)。

#### 5.3.4 Alternating-Attention Encoder

**Function:** 沿用 VGGT 的 $L=24$ 層 Alternating-Attention 結構交替執行 frame-wise self-attention (捕捉單張影像內結構) 與 global self-attention (跨 view 聚合),在每個 block 之前接受 camera adapter 的 zero-conv 注入。

**Input:**
- Name: $(e'_c, e_r, e'_f)$
- Shape: camera $[B, N, d]$、register $[B, N, R, d]$ ($R$ 未在論文揭露)、spatial $[B, N, P, d]$
- Source: GeoAdapter 之後的合成輸入

**Output:**
- Name: $(\hat{e}_c, \hat{e}_r, \hat{e}_f)$
- Shape: 同輸入維度,$\hat{e}_r$ 在進入預測 head 前丟棄
- Consumer: Camera Head (吃 $\hat{e}_c$)、DPT Depth/Point Head (吃 $\hat{e}_f$)

**Processing:**

第 $l$ 個 block 先做 Frame-Attention(將同一 frame 內的 spatial token 之間自注意力),再做 Global-Attention(將所有 frame 的 token concat 後做跨 view 自注意力);camera token 在每個 block 之前都先收到 $\text{ZC}_l$ 的加項,因此「相機資訊隨深度逐層累積」。經過 24 個 block 後,$\hat{e}_r$ 丟棄,$\hat{e}_c$ 與 $\hat{e}_f$ 被三個 prediction head 平行使用 (Eq. 1, paper §3)。

**Implementation Details:**

論文未揭露 $d$ 與 register token 數 $R$;訓練使用 gradient checkpointing 以節省記憶體 (paper §5 Implementation Details)。

#### 5.3.5 Prediction Heads

**Function:** 三個平行 head 從 encoder 的 refined token 同時輸出 depth、3D point map 與 camera 內外參,沿用 VGGT 的 head 結構,本論文未做修改。

**Input:**
- Name: $\hat{e}_f$ (給 dense head)、$\hat{e}_c$ (給 camera head)
- Shape: $[B, N, P, d]$ 與 $[B, N, d]$
- Source: AA encoder

**Output:**
- Name: $\hat{D}, \hat{P}, \hat{Y}, \hat{K}, \hat{G}$
- Shape: $\hat{D} \in [B, N, H, W]$;$\hat{P} \in [B, N, 3, H, W]$;對應 confidence map $\hat{Y} \in [B, N, H, W]$;相機輸出 $[B, N, 9]$ (再轉回 $\{K, G\}$)
- Consumer: 下游任務 (depth/MVS/pose/3D reconstruction) 與 VLA 模型

**Processing:**

Depth head 與 Point head 採用 DPT [45],從 spatial token 重建 dense feature 後輸出 $\hat{D}$、$\hat{P}$ 與其 confidence map $\hat{Y}$。Camera head 把所有 camera token 通過 4 個 self-attention layer 接 1 個 linear layer,輸出參數化向量 $\{q, t, f\}$,再還原為內外參 (paper §3)。

**Key Formulas:**

訓練目標為三項加總

$$
\mathcal{L} = \mathcal{L}_{\text{camera}} + \mathcal{L}_{\text{depth}} + \mathcal{L}_{\text{pmap}}
$$

其中 $\mathcal{L}_{\text{camera}}$ 為 $\ell_1$ 回歸,$\mathcal{L}_{\text{depth}}$ 與 $\mathcal{L}_{\text{pmap}}$ 採 confidence-aware regression loss 並加上 gradient-based 局部一致性項 (paper §4.3 Training Objective)。

**Implementation Details:**

DPT head 與 camera head 結構未在本論文重述,沿用 VGGT 設定;論文未揭露各 head 的隱藏維度。

#### 5.3.6 Stochastic Multimodal Fusion (Training Procedure)

**Function:** 訓練端的隨機抽樣策略,讓單一模型能在推論時接受任意數量、任意組合的輔助輸入,並避免模型「複製貼上」輔助線索而非學到真正穩健的空間表徵。

**Input:**
- Name: 一個 batch 的 frame 序列 (長度 $S$),以及該 batch 所有可用的 GT 相機與深度
- Shape: 同主流程
- Source: 訓練資料 loader

**Output:**
- Name: 每個 sample 的指示子向量 $\{m_i\}_{i=1}^{N}$ 與 $\{n_i\}_{i=1}^{N}$
- Shape: 兩組長度 $S$ 的 0/1 mask
- Consumer: GeoAdapter 的 placeholder 切換邏輯

**Processing:**

對每個 sample:(1) 以 uniform 抽樣 $Q \in [0, S]$,將 GT 相機指派給序列前 $Q$ 個 frame ($m_{1..Q}=1$);(2) 獨立地以 uniform 抽樣 $O \in [0, S]$,將 GT 深度隨機指派給 $O$ 個 frame ($n$ 隨機位置為 1);(3) 額外有機率 $p\%$ 的 batch 完全只用 RGB 訓練,確保模型對「無輔助」case 保持穩定 (paper §4.3)。

**Implementation Details:**

論文未明示 $p\%$ 的具體數值與序列長度 $S$;此策略無需訓練多份模型,即可支援推論時 RGB-only、僅深度、僅相機、深度+相機等所有組合,實驗結果 (Table 1) 顯示注入比例越高效能越好,且即使在 RGB-only 條件下也比 baseline VGGT 略勝 (Sintel: $\delta < 1.25$ 71.46 vs 70.81)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| ARKitScenes [6] | Indoor 3D scene understanding | 1.2M frames | train (2.07%) + zero-shot test (Table 9) |
| BlendedMVS [71] | Mixed MVS | 1.1M frames | train (2.07%) |
| DL3DV [33] | Mixed scene 3D | 21M frames | train (17.81%) |
| Dynamic Replica [23] | Indoor dynamic | 2.8M frames | train (4.68%) |
| HyperSim [47] | Indoor synthetic | 70K frames | train (3.55%) |
| Kubric [16] | Object dynamic | 1.3M frames | train (1.67%) |
| MapFree [3] | Outdoor relocalization | 2.6M frames | train (9.03%) |
| MegaDepth [31] | Outdoor depth | 1.2M frames | train (2.07%) |
| Matterport 3D [44] | Indoor real | 1.9M frames | train (3.48%) |
| MVS-Synth [21] | Outdoor synthetic MVS | 12K frames | train (1.34%) |
| ScanNet [12] | Indoor real | 23M frames | train (4.75%) + multi-view depth test |
| ScanNet++ [72] | Indoor real | 7.8M frames | train (13.88%) |
| Spring [38] | Outdoor synthetic dynamic | 4.9K frames | train (0.5%) |
| TartanAir [67] | Mixed synthetic SLAM | 3M frames | train (9.36%) |
| UASOL [7] | Outdoor stereo | 1.3M frames | train (2.41%) |
| Unreal 4K [58] | Outdoor synthetic | 16K frames | train (1.81%) |
| Virtual KITTI [9] | Outdoor synthetic dynamic | 42K frames | train (3.44%) |
| Waymo [56] | Outdoor real dynamic | 7.9M frames | train (8.36%) |
| WildRGBD [68] | Object real | 1.9M frames | train (4.35%) |
| Sintel [8] | Mono-depth + pose (zero-shot) | 100 scenes × 10 imgs | test only (auxiliary-injection study, mono-depth, ablation) |
| Bonn [41] | RGB-D dynamic | the paper does not specify | mono-depth zero-shot test |
| NYU-v2 [54] | Indoor RGB-D | the paper does not specify | mono-depth zero-shot test |
| ETH3D [51] | MVS | the paper does not specify | multi-view depth + 3D recon test |
| DTU [1] | MVS | the paper does not specify | multi-view depth test |
| Tanks & Temples [26] | Large-scale recon | the paper does not specify | multi-view depth test |
| Co3Dv2 [46] | Camera pose | the paper does not specify | pose-estimation test |
| RealEstate10K [77] | Camera pose | the paper does not specify | pose-estimation test |
| 7-Scenes [53] | Sparse 3D recon | 3–5 frames/scene | 3D-reconstruction test |
| NRGBD [4] | RGB-D recon | the paper does not specify | 3D-reconstruction test (appendix) |
| OmniWorld-Game [78] | Game-rendered | the paper does not specify | auxiliary-injection zero-shot test (appendix) |
| CALVIN [37] | Robotic manipulation | the paper does not specify | VLA finetune + ABCD→D / ABC→D test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| Abs Rel | Absolute relative depth error 取所有 valid pixels 平均，越小越好 | yes |
| $\delta < 1.25$ | depth inlier 比例 (預測值與 GT 比值落在 $[1/1.25, 1.25]$ 內) | yes |
| RRA@5° | Relative Rotation Accuracy 在 $5°$ 閾值下 image-pair 命中比例 | yes |
| RTA@5° | Relative Translation Accuracy 在 $5°$ 閾值下命中比例 | yes |
| AUC@30° | $\min(\text{RRA}, \text{RTA})$ 對閾值曲線下面積，至 $30°$ | yes |
| Acc (mean / med) | Reconstruction accuracy 預測點到 GT 距離 | yes |
| Comp (mean / med) | Reconstruction completeness GT 點到預測距離 | yes |
| NC (mean / med) | Normal Consistency 預測 normal 與 GT 的 cosine 平均 | no |
| rel / $\tau$ (multi-view depth) | Robust-MVD 標準的 inlier-ratio 與相對誤差 | yes |
| Avg. Len. | CALVIN 上連續完成任務數的平均長度 | yes |
| Tasks Completed in a Row 1–5 | CALVIN 各 horizon 之成功率 | no |
| Inference Time | 每 batch 推論秒數 (相對 Pow3R 的效率對比) | no |

### 6.3 Training and Inference Settings

模型以 VGGT [63] 預訓練權重初始化，沿用 $L = 24$ 層 Alternating-Attention blocks。Camera GeoAdapter 配置 $L+1$ 個獨立 camera encoder (各為單一 linear layer)，Depth GeoAdapter 僅一個 depth encoder (kernel size 14 的單層 convolution，輸出維度對齊 spatial token)；GeoAdapter 共新增 26.8M 參數。訓練在 32 張 NVIDIA A100 GPU 上端到端跑 10 天，採 gradient checkpointing 節省顯存；fine-tune 共 10 個 epoch、每 epoch 12M iterations。Optimizer 為 AdamW，prediction heads 學習率 $2 \times 10^{-5}$、backbone $1 \times 10^{-5}$，搭配 5K-step linear warmup 與 cosine weight decay schedule。Stochastic multimodal fusion 中的「全 RGB 訓練 batch 機率」 $p$ 設為 $10\%$。輸入空間解析度自 $518 \times 168$ 至 $518 \times 518$ 不等，並使用 ColorJitter 增強光照魯棒性。每個 batch 取 2–24 frames，總計固定 24 frames，依 camera-pose similarity 排名選 top-N 後隨機抽樣 anchor frame 與其餘 frames。Ground-truth depth、point map、translation 皆以 point map 至原點的平均 Euclidean 距離歸一化 (與 GeoAdapter 內部歸一化不同)。推論時所有影像縮放至寬度 $518$、aspect ratio 對齊訓練集最近比例；Sintel auxiliary-injection 評估隨機自 100 scenes 各取 10 images 後平均。Batch size 與訓練 GPU memory footprint 等細節 the paper does not specify。

### 6.4 Main Results

Mono-depth (Table 2)，Sintel / Bonn / NYU-v2 zero-shot：

| Method | Sintel Abs Rel↓ | Sintel $\delta<1.25$↑ | Bonn $\delta<1.25$↑ | NYU-v2 $\delta<1.25$↑ |
|---|---|---|---|---|
| VGGT [63] | 0.271 | 67.7 | 97.3 | 94.8 |
| DUSt3R [66] | 0.424 | 58.7 | 82.5 | 90.7 |
| MASt3R [29] | 0.340 | 60.4 | 82.0 | 84.9 |
| CUT3R [65] | 0.428 | 55.4 | 96.2 | 90.9 |
| Pow3R [22] | 0.464 | 54.8 | 84.2 | 89.6 |
| Pow3R w/ D | 0.150 | 87.4 | 99.7 | 99.8 |
| **OmniVGGT** | **0.250** | **68.2** | 95.5 | **95.8** |
| **OmniVGGT w/ D** | **0.107** | **90.2** | **99.9** | **99.9** |

Multi-view depth average over ScanNet / ETH3D / DTU / T&T (Table 3)：

| Method | rel↓ | $\tau$↑ | Notes |
|---|---|---|---|
| VGGT [63] | 2.0 | 85.8 | RGB only |
| DUSt3R [66] | 3.3 | 72.9 | RGB only |
| Pow3R [22] | 3.1 | 73.6 | RGB only |
| Pow3R w/ (K+RT) | 2.7 | 79.5 | aux. pose |
| **OmniVGGT** | 2.1 | 85.9 | RGB only |
| **OmniVGGT w/ (K+RT)** | 2.1 | 85.9 | aux. pose |
| **OmniVGGT w/ D** | 1.0 | 94.8 | aux. depth |
| **OmniVGGT w/ (K+RT+D)** | **1.0** | **95.1** | full aux. |

Camera pose AUC@30° (Table 4)：

| Method | Re10K | CO3Dv2 | Time |
|---|---|---|---|
| VGGT [63] | 85.3 | 88.2 | $\sim$0.2s |
| Pow3R (Pro) [22] | 62.5 | 78.5 | $> 7$s |
| Pow3R w/ K (Pro) | 72.5 | 82.2 | $> 7$s |
| **OmniVGGT** | 85.9 | 88.4 | $\sim$0.2s |
| **OmniVGGT w/ D** | 85.5 | 91.3 | $\sim$0.2s |
| **OmniVGGT w/ K+RT** | **88.5** | **93.4** | $\sim$0.2s |

3D reconstruction on 7-Scenes (Table 5)：

| Method | Acc (mean)↓ | Comp (mean)↓ | NC (mean)↑ |
|---|---|---|---|
| VGGT [63] | 0.087 | 0.091 | 0.787 |
| CUT3R [65] | 0.126 | 0.154 | 0.727 |
| **OmniVGGT** | 0.104 | 0.112 | 0.763 |
| **OmniVGGT w/ D** | 0.085 | 0.085 | 0.789 |
| **OmniVGGT w/ (K+RT)** | **0.037** | 0.049 | 0.778 |
| **OmniVGGT w/ (K+RT+D)** | **0.036** | **0.036** | **0.810** |

VLA on CALVIN (Table 6)，**Avg. Len.**：

| Method | ABCD→D | ABC→D (zero-shot) |
|---|---|---|
| Kosmos-VLA (rgb) | 4.00 | 3.49 |
| Kosmos-VLA (rgb-d, point encoder) | 4.04 | 3.97 |
| **Ours (rgb)** | 4.07 | 3.92 |
| **Ours (rgb-d)** | **4.08** | **3.96** |

### 6.5 Ablation Studies

- **Auxiliary-injection ratio scaling (Table 1)**：在 Sintel 上將 GT depth/camera 注入比例自 $0\%$ 掃到 $100\%$。提供 $30\%$ depth 即把 Abs Rel 自 $0.558$ 降到 $0.169$ ($-69.7\%$)；$100\%$ depth 同時把 AUC@30° 自 $70.83$ 推到 $77.16$ (depth → pose 的 cross-modal gain，$+6.33$)，這直接針對「stochastic fusion 是否真的學到泛化空間表徵而非 input-output mapping」這個論文主張，是 diagnostic 而非 sanity check。
- **GeoAdapter architecture 變體 (Fig. 5, Table 7)**：(a) Replace、(b) One-Layer Adapter、(c) Depth ZeroConv、(d) full OmniVGGT。RGB-only 設定下 (d) 為 $\delta<1.25 = 71.46$、AUC@30° $= 70.83$，皆優於三變體；full-aux 設定下 (d) 同時打贏 (a) 在 Abs Rel ($0.106$ vs $0.655$) 與 AUC ($85.99$ vs $77.83$) 兩項。明確切開「camera token 是 replace / one-shot / per-layer zero-conv 注入」三種替代設計，是真正 diagnostic 的 ablation。
- **Depth-branch ZeroConv 必要性 (Table 7 (c) vs (d) 與 Fig. 6, Fig. 8)**：在 depth 分支加上 zero-conv 反而把 full-aux 的 Abs Rel 自 $0.106$ 惡化到 $0.505$；PCA 視覺化顯示 zero-conv 後 auxiliary depth token 的邊緣與背景結構被抑制、被網路當成 noise。為「為何只在 camera 分支用 zero-conv 而 depth 分支不用」提供了直接證據。
- **Cross-dataset 注入掃描 (Table 9 ARKitScenes、Table 10 OmniWorld-Game)**：在兩個未訓練資料集重複 Table 1 的 ratio sweep。OmniWorld 上 $100\%$ depth 將 Abs Rel 自 $0.240$ 降到 $0.095$，AUC@30° 自 $63.86$ 升到 $74.35$，驗證 scaling 行為非 Sintel 特例。Diagnostic。
- **Depth-ratio 對 7-Scenes / NRGBD 重建 (Tables 12, 13)**：附錄掃 $30/50/70/100\%$ depth 與 K+RT 的 Acc/Comp/NC。注意 Table 13 的 NRGBD 數值與 Table 12 的 7-Scenes 完全相同 (suspected copy-paste issue in the appendix)，無法獨立驗證 NRGBD 結論；建議使用者 cross-check 原始來源。
- **Sanity-check flag**：Table 6 的 Kosmos-VLA (w/ rgb) baseline 沒有任何 spatial encoder，與 OmniVGGT (w/ rgb) 的 $+0.07$ Avg. Len. 差距難以單獨歸因為 spatial-token 品質提升而非「extra encoder 帶來的容量」。這比較較像 sanity check 而非 ablate 出 OmniVGGT spatial token 的因果貢獻；理想應比較同等容量的 VGGT-tokens-injected baseline，paper 未做。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — VGGT [63] 為當前 spatial foundation model SoTA，亦比較 Pow3R (auxiliary-aware SoTA)、MASt3R、CUT3R、Fast3R、DUSt3R 等。
- [covered] Has cross-task / cross-dataset evaluation — 跨 mono-depth / multi-view depth / pose / 3D-recon / VLA 五類任務，Sintel、Bonn、NYU-v2、ScanNet、ETH3D、DTU、T&T、Co3Dv2、RealEstate10K、7-Scenes、ARKitScenes、OmniWorld、CALVIN 等十餘個資料集。
- [covered] Has ablations that diagnose the new components — Table 7 切分 (a)–(d) 四種 GeoAdapter 設計、Fig. 6/8 PCA 視覺化、Table 1 cross-modal injection sweep，皆針對 GeoAdapter 與 stochastic fusion 兩大主張。
- [partial] Has a scaling study — 有 auxiliary-information ratio scaling ($0\%\to100\%$，Tables 1, 9, 10) 與 frame-count 多視角實驗，但無 model-size 或 training-compute 的 scaling 曲線。
- [partial] Has an efficiency / wall-clock comparison — Table 4 報告 inference time 並聲稱比 Pow3R 快 $\sim 30\times$，但僅一個 setting；未報 throughput-vs-input-count、memory，亦無 GeoAdapter 之 isolated overhead 量測。
- [missing] Reports variance / standard deviation / multiple seeds — 全表皆為單次數字，無 std / multiple seeds / confidence interval；CALVIN 等小幅 ($+0.04$ Avg. Len.) 提升尤其需要。
- [partial] Releases code / weights / data sufficient for reproducibility — 只列出 project page (https://livioni.github.io/OmniVGGT-official/)；附錄詳載資料集、optimizer、warmup、學習率等 hyperparameter，但 code/weights/checkpoint 釋出狀態 the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

1. **「能彈性接受任意數量、任意組合的幾何輔助輸入」**:有支持。Table 1 (p. 5) 對 30/50/70/100% 的 depth 與 camera 注入比例展示單一 checkpoint 可穩定處理任意子集,Table 3、5 進一步驗證 (K+RT)、D、(K+RT+D) 等組合可由同一模型推論。
2. **「GeoAdapter 透過 zero-conv 注入幾何資訊而不破壞基礎模型表徵」**:有支持。Table 7 (p. 8) Replace 變體於無輔助輸入時 Abs Rel 為 0.845 vs OmniVGGT 0.558,支持 zero-conv 對保留 backbone 表徵的必要性;Fig. 6 的 PCA 視覺化提供額外定性佐證。
3. **「Stochastic multimodal fusion 讓 RGB-only 都比 VGGT 更穩健」**:部分支持。Sintel 與部分 7-Scenes 指標確實小幅領先 VGGT,但 Bonn 的 Abs Rel 與 $\delta < 1.25$ 反而退化、NYU-v2 改善幅度極小;且實驗未控制訓練資料量與 iteration 數差異,因果歸因不足。
4. **「OmniVGGT 推論速度與 VGGT 相當,並較 Pow3R 快約 30×」**:有支持。Table 4 (p. 8) 列出 OmniVGGT $\sim 0.2\text{s}$、Pow3R $> 7\text{s}$,且額外參數僅 26.8M。
5. **「整合至 VLA 後 spatial 表徵更豐富而提升 robotic manipulation」**:過度宣稱。Table 6 (p. 8) ABCD→D 的最強對比僅 +0.04 Avg. Len (4.04→4.08);ABC→D 的 Kosmos rgb-d baseline (3.97) 反而高於 OmniVGGT rgb (3.92),顯示 point-cloud encoder 在 zero-shot 也很強;OmniVGGT 的優勢主要來自「同模態 vs 同模態」的小幅領先,而非 spatial token 結構性勝過 point encoder。

### 7.2 Fundamental Limitations of the Method

**對輔助輸入精度的隱性依賴。** 全文「auxiliary input」實驗皆使用 GT depth 與 GT camera,而 stochastic fusion 訓練時是 subset dropout 而非 noise injection——一旦線上 depth 出現 systematic error (例如 ToF 在反光面失準、LiDAR 在雨天稀疏化) 或 camera 帶 calibration 漂移,模型沒有機制偵測或下調該模態權重。GeoAdapter 將輔助 token 直接 additive 注入到 spatial / camera token,結構上意味著「無條件相信」輔助輸入,這是現有設計無法克服的。

**Zero-conv 與 placeholder 的對稱性假設未被檢驗。** 作者主張 camera 為 global、depth 為 dense,因此前者用 zero-conv、後者直接相加,但這個對稱在 placeholder 機制下並非自洽:當大多 frame 缺 camera 而少數有時,zero-conv 累積的更新會在序列維度產生不均勻信號,長期可能讓 backbone 對「有 camera token 的位置」過擬合。Table 7 (b) 同時關掉 per-layer 注入與多層 zero-conv,因此無法判斷哪個性質才是真正關鍵設計。

**訓練分布與測試分布的位置耦合。** Stochastic fusion 將 camera GT 永遠分配到序列前 Q 張、depth GT 分配到隨機 index (§4.3, p. 4),這直接決定模型可推論的測試分布。當使用者只給最後一幀的 camera 或只給特定 anchor 的 depth,實際分布偏離訓練統計,但論文沒有任何 out-of-distribution modality placement 的測試,屬於設計層面而非工程層面的缺口。

**對 VLA 整合的「空間理解提升」缺乏 mechanistic 證據。** Table 6 顯示 OmniVGGT 與 point-cloud encoder baseline 的差距小於資料雜訊量級。論文沒有 attention map、linear probe 或 controlled task 來證明 OmniVGGT spatial token 真的編碼了比 point cloud 更多的 3D 結構,目前僅停留在「下游指標小幅好」的現象描述。

### 7.3 Citations Worth Tracking

- **VGGT (Wang et al., 2025) [63]**:OmniVGGT 直接的 backbone 與訓練配方來源;理解 Alternating-Attention 編碼器與 DPT prediction head 的細節對判讀本文必要。
- **Pow3R (Jang et al., 2025) [22]**:本文最直接的 baseline;理解其「最多兩種輸入」限制與架構,才能判斷 30× 速度差距的實質來源。
- **ControlNet zero-conv (Zhang et al.)**:GeoAdapter zero-init 注入的靈感來源;讀完可判斷 OmniVGGT 是否在 zero-conv 應用上有實質創新,還是直接搬用既有機制至新領域。
- **Kosmos-VLA / Kosmos-2 (Peng et al., 2023) [42]**:§5.5 整合的 VLA 架構底座;要評估「spatial token 是否真比 point encoder 好」必須先理解該基線的能力上下界。
- **DUSt3R (Wang et al., 2024) [66]**:整個 spatial foundation model 譜系的源頭;提供 feed-forward point-map regression 為何能 work 的理論直覺,有助於判讀本文歸納的 inductive bias 取捨。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 當 auxiliary depth/camera 帶有實際感測噪聲 (例如 ToF 反光誤差、IMU 漂移、LiDAR 稀疏化) 時,GeoAdapter 是否仍能優於 RGB-only,還是會被誤導至更差結果?
- [ ] 純 RGB batch 比例 $p$ 從 10% 改為 0%、5%、25%、50% 時,RGB-only 表現與 auxiliary-augmented 表現的 trade-off 曲線形狀為何?
- [ ] 為什麼 camera GT 必須分配到序列前 Q 張、depth GT 分配到隨機 index?若兩者皆改成「對 anchor frame 對稱隨機」,結果是否退化或保持?
- [ ] OmniVGGT vs VGGT 的 RGB-only 改善,有多少來自 stochastic fusion 機制本身,有多少來自更長訓練 (10 epoch × 12M iterations) 與 19-dataset 混合?
- [ ] 在 ABC→D zero-shot 上,Kosmos-VLA (w/ rgb-d, 4.04) 為何贏過 OmniVGGT (w/ rgb, 3.92)?spatial token 的優勢在 zero-shot 環境是否消失?
- [ ] 當測試時的 auxiliary 子集分布與訓練分布不一致 (例如只給最後一幀 camera、只給 anchor 之外幀的 depth) 時,模型穩定性如何?
- [ ] 為什麼 OmniVGGT 在 Bonn 上 RGB-only 退化於 VGGT,而 Sintel 卻明顯改善?是場景靜態/動態差異還是 GT 標註特性?

### 8.2 Improvement Directions

1. **加入 noisy auxiliary input 的評估與訓練增強。** 在 Sintel 與 ARKitScenes 上對 GT depth 加 Gaussian noise、systematic bias、或對 camera pose 加旋轉/平移擾動,觀察性能曲線。若退化嚴重,可在 stochastic fusion 中加入 noise injection 而非僅 dropout,讓模型學會降權低品質模態——目前 fusion 只教會「缺項」未教會「不可信」。可行性高,僅需 dataloader 加噪。
2. **VGGT 同訓練量對照組。** 用相同 19 資料集、10 epoch、12M iterations 重新微調 VGGT,以隔離「stochastic fusion 本身」與「更多訓練/資料」對 RGB-only 提升的相對貢獻。論文最具爭議的「RGB-only 也勝過 VGGT」主張需要這個對照才能歸因。可行性中等,計算成本與作者持平。
3. **對稱化 camera/depth GT 指派策略並 ablation。** 將 camera GT 改為隨機 index、或將 depth GT 改為前 O 張,觀察 stochastic fusion 對指派策略的敏感度。若敏感,則目前主結果隱含一個未公開的 inductive bias;若不敏感,則「camera 是 global」的論述更穩固。可行性高,純訓練配置變更。
4. **VLA spatial token 的 mechanistic probe。** 對 OmniVGGT 與 point-cloud encoder 的 feature 做 linear probing 以預測物件相對距離、抓取點 3D 座標等,提供「空間理解更佳」的直接證據,而非只看 Avg. Len 差距 0.04 的下游指標。可行性中等,需設計 probe 任務但訓練成本不高。
5. **超參數 $p$ sweep。** 在小型資料子集上跑 $p \in \{0\%, 5\%, 10\%, 25\%, 50\%\}$,確定當前 10% 是否落在最佳區段或只是「合理但未調過」。可行性高,只需數次小規模微調。
6. **將 zero-conv 應用至 depth branch 但採用 learned gating。** 既然原始 zero-conv 在 depth 上會壓抑訊號 (Fig. 6),可改用 sigmoid-gated residual,讓模型自學注入強度;這在 depth 真正帶噪時可能反而比目前 additive 設計更穩健。可行性中等,需要少量設計調整與重新訓練。
