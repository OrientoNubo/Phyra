<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# 4DLangVGGT — 4DLangVGGT: 4D Language-Visual Geometry Grounded Transformer

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | 4DLangVGGT |
| Paper full title | 4DLangVGGT: 4D Language-Visual Geometry Grounded Transformer |
| arXiv ID | 2512.05060 |
| Release date | 2025-12-04 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2512.05060 |
| PDF link | https://arxiv.org/pdf/2512.05060v1 |
| Code link | https://github.com/hustvl/4DLangVGGT |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Xianfeng Wu | State Key Laboratory of Precision Blasting, Jianghan University; School of EIC, Huazhong University of Science and Technology; Department of Computing, The Hong Kong Polytechnic University | https://maradona10wxf.github.io/ | co-first author |
| Yajing Bai | State Key Laboratory of Precision Blasting, Jianghan University; School of EIC, Huazhong University of Science and Technology | — | co-first author |
| Minghan Li | Harvard AI and Robotics Lab, Harvard University | — | co-author |
| Xianzu Wu | State Key Laboratory of Precision Blasting, Jianghan University; Department of Computer Science, Hong Kong Baptist University | — | co-author |
| Xueqi Zhao | State Key Laboratory of Precision Blasting, Jianghan University; School of Mathematics and Statistics, Hubei University of Education | — | co-author |
| Zhongyuan Lai | State Key Laboratory of Precision Blasting, Jianghan University | — | co-author |
| Wenyu Liu | School of EIC, Huazhong University of Science and Technology | — | co-author |
| Xinggang Wang | School of EIC, Huazhong University of Science and Technology | https://xwcv.github.io/ | corresponding author |

### 1.2 Keywords

4D scene understanding, language field, feed-forward reconstruction, open-vocabulary querying, VGGT, Gaussian Splatting alternative, semantic alignment, spatio-temporal transformer

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| 4DLangSplat (Li et al., 2025c) | baseline | Per-scene 4D Gaussian Splatting language field; primary baseline that motivates removing per-scene optimization. |
| StreamVGGT (Zhuo et al., 2025) | base model | Streaming feed-forward 4D geometry transformer used as the frozen geometry encoder backbone. |
| VGGT (Wang et al., 2025a) | predecessor | Feed-forward 3D visual geometry grounded transformer that StreamVGGT and this work build upon. |
| LangSplat (Qin et al., 2024) | baseline | Static 3D Gaussian Splatting language field; baseline for time-agnostic open-vocabulary querying. |
| DUSt3R (Wang et al., 2024) | influence | Pioneer feed-forward dense 3D reconstruction that informs the feed-forward paradigm adopted here. |
| LERF (Kerr et al., 2023) | influence | NeRF-based language field for open-vocabulary 3D querying; conceptual ancestor of language-grounded scene fields. |
| 4-LEGS (Fiebelman et al., 2025) | concurrent | Concurrent 4D Gaussian language field that lifts spatio-temporal video features for text localization in dynamic scenes. |

## 2. Research Overview

### 2.1 Research Topic

本論文研究如何在動態 4D 場景中建構語言對齊的語意場 (language field),以支援開放詞彙的時序敏感與時序不敏感查詢,服務於具身智慧、AR/VR 與 4D 場景理解等應用。作者觀察到既有方法多依賴 Gaussian Splatting 的逐場景最佳化,計算成本高、可擴展性差且難以即時部署,因此提出 4DLangVGGT,首個以 Transformer 為基礎的 feed-forward 統一框架,將動態幾何重建與視覺-語言對齊整合於單一網路中。框架以凍結的 StreamVGGT 作為幾何編碼器擷取時空幾何 token,並透過提出的 Semantic Bridging Decoder (SBD) 將幾何特徵投影到語言對齊的語意空間,結合 SAM/DEVA 遮罩、CLIP 與 MLLM/LLM 產生時序不敏感與時序敏感的雙重監督,並以 RGB 重建損失維持外觀保真。模型可跨多個場景聯合訓練、推論時直接套用,於 HyperNeRF 與 Neu3D 達到 state-of-the-art。

### 2.2 Domain Tags

- Computer Vision
- 3D/4D Scene Understanding
- Vision-Language Learning
- Dynamic Scene Reconstruction

### 2.3 Core Architectures Used

- **StreamVGGT (frozen geometry encoder)**:作為幾何骨幹,以交替的 spatial attention 與 causal temporal attention 在串流設定下產生時空幾何 token $\{G_t\}_{t=1}^T$ 與 camera token $\{C_t\}_{t=1}^T$,本論文將其凍結以保留大規模影片預訓練的時空幾何泛化能力。
- **VGGT**:StreamVGGT 的非串流前身,採用 DINO image encoder $E$ 與 Alternating-Attention transformer $D$,搭配 camera head $H_{\text{cam}}$ 與 DPT head $H_{\text{DPT}}$,是本論文 feed-forward 幾何路徑的概念基礎。
- **Semantic Bridging Decoder (SBD)**:本論文提出的核心模組,以 contextual-aware DPT $H_{\text{DPT}}^{\text{lang}}$ 將 geometry token 轉成統一 4D 特徵 $H_t \in \mathbb{R}^{h \times w \times c}$,再以雙頭 $f_{\text{Lang}}$ 與 $f_{\text{RGB}}$ 同時輸出語意嵌入與 RGB 重建。
- **DPT (Dense Prediction Transformer)**:結合卷積空間敏感性與 Transformer 全域建模的密集預測骨幹,在 SBD 中被重新引入以擷取跨空間與時間維度的長程依賴。
- **CLIP (OpenCLIP ViT-B/16)**:用於對遮罩區域產生 object-level 嵌入 $e_{i,t}^{\text{CLIP}}$,作為時序不敏感語意監督的 ground truth 來源。
- **SAM 與 DEVA**:分別作為靜態 Segment Anything Model 與時序遮罩追蹤模組,用於產生跨幀一致的物件級遮罩 $\{M_{i,t}\}$。
- **MLLM (Qwen2.5-VL-7B-Instruct) 與 LLM (e5-mistral-7b)**:MLLM $f_{\text{MLLM}}$ 對影片區域生成時序一致的描述,再由 LLM $f_{\text{LLM}}$ 編碼為動態語意嵌入 $e_{i,t}^{\text{dyn}}$,構成時序敏感監督。

### 2.4 Core Argument

作者主張現有 4D 語言場方法的根本限制在於將「場景表徵」與「語意場」一併綁定到逐場景最佳化的 Gaussian Splatting 流程上:每個新場景都必須重新跑一次昂貴的最佳化,模型無法跨場景泛化、難以擴展到大規模部署,也無法支援即時應用。同時,純粹的 feed-forward 幾何重建方法 (DUSt3R、VGGT、StreamVGGT) 雖然具備泛化與效率優勢,但只關心幾何與運動,完全缺乏語意對齊,無法回答開放詞彙查詢。作者由此推論:解法必須同時滿足三件事——(1) 維持 feed-forward 架構以避免逐場景訓練、(2) 重用已在大規模影片上預訓練的時空幾何表徵、以及 (3) 在不破壞幾何特徵結構保真度的前提下,額外建立一座從幾何 token 通往語言空間的橋樑。基於此邏輯,他們將 StreamVGGT 凍結作為幾何骨幹以鎖住強泛化能力,並設計 Semantic Bridging Decoder (SBD):以 contextual-aware DPT 將幾何 token 轉成具有長程依賴的統一 4D 特徵,再以雙頭分別輸出語意嵌入 (對齊 CLIP 靜態語意與 MLLM/LLM 產生的動態描述) 與 RGB 重建 (確保感知保真),透過時序不敏感與時序敏感雙重監督避免語意漂移。如此設計使框架可在 HyperNeRF 與 Neu3D 等多場景聯合訓練、推論時直接套用,既消除逐場景最佳化的部署瓶頸,也保留 VGGT 系列的時空幾何表徵優勢,從邏輯上必然能同時兼顧效率、泛化與語意一致性。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(290 words)

標題 "4DLangVGGT: 4D Language-Visual Geometry Grounded Transformer" 一次點出三個關鍵字：4D、語言對齊、與 VGGT 系譜的 visual geometry transformer，暗示這是一個把 feed-forward 幾何骨幹與語言場結合的工作。Abstract 的鋪陳分四步推進：先確立任務動機 (4D language field 對 embodied AI、AR/VR 與場景理解的重要性)；接著鎖定既有路線的痛點，明確指出當前方法 "primarily rely on scene-specific Gaussian splatting"，因此 per-scene optimization、generalization 不足、難以規模化；然後直接亮出核心命題：4DLangVGGT 是 "the first Transformer-based feed-forward unified framework for 4D language grounding"，並以兩個元件名稱 (StreamVGGT 幾何編碼器與 Semantic Bridging Decoder) 預告方法章節的拆解結構；最後給出可量化的實驗承諾——HyperNeRF 與 Neu3D 上 per-scene 訓練最高 2% 增益、multi-scene 訓練約 1% 增益，並附上程式碼連結強化可信度。

這段摘要完成的「三件事」與 §3.2 的銜接非常清楚：(i) 把問題定位在「動態 4D + 語言查詢」這個交集，為 Introduction 的 motivation 段落鋪軌；(ii) 把對手框定為以 Gaussian Splatting 為主的 per-scene 方法 (LangSplat、4DLangSplat、4-LEGS 等)，預示 §3.3 Related Work 會沿著「靜態 3D → 動態 4D → feed-forward reconstruction」的三線收束；(iii) 把方法命題簡化成「凍結 StreamVGGT 提供幾何，新增 SBD 提供語言對齊」這個極簡敘事，讓讀者預期 §3.4 會用 (i) geometry encoder、(ii) SBD、(iii) multi-objective training 三個小節來具體化。值得注意的是，abstract 中的數字 "up to 2%" 與 "1%" 並未說明指標是 mIoU 還是 Acc，這個曖昧性會在 §3.5 的實驗章節用 Table 1–3 補完。

### 3.2 Introduction

(700 words)

Introduction 用四段層層遞進來建立「為什麼非做不可」的論證鏈。第一段以下游應用 (human-robot interaction、AR/VR、intelligent surveillance) 開場，指出 3D vision-language learning 在靜態場景已經成熟，但延伸到 4D 時 "geometry and semantics evolve continuously over time"，直接套用 3D 方法會造成 "semantic drift and unstable alignment"。這段的功能是把「動態 4D 語言場」確立為一個尚未被充分解決的獨立問題。

第二段把火力集中在當前的代表方法 4DLangSplat 上：作者承認 Gaussian Splatting 在受控場景表現不錯，但其根本缺陷是 "the need for explicit per-scene optimization"，由此衍生出三項具體限制——計算成本高、跨影片可擴展性差、需為不同環境維護獨立模型。這段的修辭策略是把對手「降維」成單一痛點 (per-scene optimization)，從而為自己的 feed-forward 路線預留空位。

第三段引入第二個重要轉折：作者把目光轉向 feed-forward 4D geometric reconstruction 路線 (DUST3R、VGGT、StreamVGGT)，指出其優勢是 real-time 與 generalization，但「焦點僅限於幾何與運動，缺乏語意/語言對齊」。這段在邏輯上至關重要，因為它把研究空缺精確地定位在兩條路線的交集——既要 feed-forward，又要 language alignment——這正是 4DLangVGGT 要填補的縫隙。

第四段揭曉解法：4DLangVGGT 整合 4D Visual Geometry Transformer 與 Semantic Bridging Decoder (SBD)，前者沿用 StreamVGGT 的時空幾何表徵，後者把幾何感知特徵投影到語言對齊的語意空間。作者強調這是 "the first unified language field model that can be jointly trained across multiple dynamic scenes and directly applied during inference"，並再次以 Fig. 1 的定性對比與「2% / 1% 增益」的數字佐證可行性。

最後以三點 contribution 收尾：(1) 首個結合 4D 幾何重建與視覺-語言對齊的 feed-forward Transformer 框架；(2) 提出 SBD 模組，把動態場景特徵映射到語言對齊空間；(3) 可在 HyperNeRF 6 場景與 Neu3D 6 場景上聯合訓練，無須 per-scene optimization 即可推論。

Introduction 為後續章節鋪設了三條軸線：對 §3.3，它已經把「靜態 3D / 動態 4D / feed-forward reconstruction」三條 Related Work 子線命名出來；對 §3.4，它預告了三個元件 (geometry encoder、SBD、multi-objective training) 的拆分方式；對 §3.5，它預設了 per-scene 與 multi-scene 兩種訓練 regime 的雙軌比較，這也是後續 Table 1–3 的呈現邏輯。整體而言，Introduction 的核心修辭工程是把「per-scene optimization」與「缺乏語言對齊」拼成一個雙軸缺口，然後宣告自己的方法同時填補兩軸。

### 3.3 Related Work / Preliminaries

(610 words)

Related Work 與 Preliminaries 在敘事上承擔不同角色：Related Work 用三條子線收束既有方法地圖；Preliminaries 則為方法章節提供必要的符號與架構基底。

Related Work 分三條子線。第一條 "Static 3D Scene Understanding" 從 NeRF 出發 (LERF、OV-NeRF) 指出體積渲染慢，再轉到 3D Gaussian Splatting 時代 (LangSplat、GaussianGrasper、LangSurf) 強調速度與多模態融合的進展，但結論是「這些方法仍限於靜態場景」，把它們從可比基線中半部分排除。第二條 "Dynamic 4D Scene Understanding" 是真正的競爭者所在地：作者具體點名 4DLangSplat (用 object-wise video captions 與 status deformable network 監督 4D Gaussian Splatting) 與 4-LEGS (把時空 video features 提升至 4D Gaussian)，並一致地批評它們 "depend on Gaussian Splatting, which needs scene-specific optimization"，這個敘事一致性很重要——它讓 §3.4 的方法定位 (feed-forward + language) 順理成章。第三條 "Feed-forward Scene Reconstruction" 列舉 DUST3R、VGGT、StreamVGGT、SplatterImage、Flash3D、Niagara，明確指出這些 feed-forward 路線「焦點僅限於幾何重建，未統一語言基礎」。三條子線在交集處留下的空白，正是 4DLangVGGT 要佔據的位置。

Preliminaries 章節 "VGGT & StreamVGGT" 的功能是技術鋪墊。作者先複述 VGGT 的三階段流程：(1) 影像編碼器 $E$ (DINO/DINOv2) 把輸入序列 $\{I_t\}_{t=1}^{T}$ 轉成影像 token $\{F_t\}$，並為每張影像附加 camera token $\{C_t\}$；(2) Alternating-Attention transformer $D$ 在 frame-level 與 cross-frame self-attention 之間交替，輸出更新後的 camera token 與 geometry token $\{G_t\}$；(3) 多頭預測器 (camera head $H_{cam}$ 與 DPT head $H_{DPT}$) 解碼出相機參數 $O_t^c$ 與密集幾何預測 $O_t^g$。接著介紹 StreamVGGT 把 VGGT 擴展到 streaming 設定：以 causal temporal attention 進行 sequential inference，推論時只需維護 cache memory $M_t = M_{t-1} \cup [C_t, F_t]$，由此達到 real-time 效率與時序一致性。最終的 Eq. (1) 把整個 streaming 流程濃縮為三式：

$$F_t = E(I_t);\quad [C_t, G_t] = D([C_t, F_t] \mid M_{t-1});\quad O_t^c = H_{cam}(C_t),\ O_t^g = H_{DPT}(G_t).$$

這個鋪陳對 §3.4 的銜接相當精準：它定義了 $G_t$ 與 $C_t$ 兩種 token，使得方法章節可以直接說「凍結 StreamVGGT、保留 $G_t$ 餵給 SBD、保留 $C_t$ 在推論時做 inverse-projection」，而不必再贅述底層架構。換言之，Preliminaries 章節把 VGGT/StreamVGGT 變成黑盒元件供方法章節調用，這是 4DLangVGGT 「最小新增」設計哲學的伏筆——所有新內容都將集中在 SBD 與訓練目標上。

### 3.4 Method (overview narrative)

(900 words)

Method 章節的整體敘事策略是「最小新增」：把 StreamVGGT 整段凍結作為幾何骨幹，所有可訓練、需要新設計的部分集中在 Semantic Bridging Decoder (SBD) 與多目標訓練策略上。Fig. 2 一張圖就把這個結構講完——左側 Geometry Encoder 走 StreamVGGT，中段 SBD 接 DPT 與雙頭 (Semantic Head / RGB Head)，右側用 SAM/DEVA + MLLM/LLM/CLIP 生成 time-agnostic 與 time-sensitive 兩種語意監督訊號。

§4.1 StreamVGGT-based Geometry Encoder 主要做兩件事：闡明「為何凍結」與「兩種 token 的不同用途」。凍結的兩個理由是 (i) StreamVGGT 已在大規模影片上預訓練、時空表徵泛化性強；(ii) 凍結可避免重新學習幾何、把優化資源集中在語意對齊。Token 用途上，幾何 token $G_t$ 是 SBD 的輸入，提供以幾何為中心的表徵基礎；camera token $C_t$ 在訓練期間凍結但保留，主要供推論期使用 camera intrinsics/extrinsics 做 inverse-projection，把語意特徵注入 4D 點雲空間。這段確立了「訓練只動 SBD、推論才動相機」的職責分工。

§4.2 Semantic Bridging Decoder (SBD) 是這篇論文最具新意的部分，分兩階段。第一階段「Geometry-to-Contextual Representation Transformation」用一個新引入的 contextual-aware DPT (記為 $H_{DPT}^{lang}$) 處理 $G_t$，產出統一的 4D feature representation：

$$H_t = H_{DPT}^{lang}(G_t),\ \forall t \in [1, \cdots, T],$$

其中 $H_t \in \mathbb{R}^{h \times w \times c}$。DPT 的選用理由是它結合了局部卷積的空間敏感性與 Transformer 的全域建模能力，可同時捕捉空間與時序上的長距離依賴。值得注意的是這個 DPT 是 trainable 的——它正是 SBD 的學習主體。

第二階段「Dual-head Semantic and Reconstruction Decoding」把 $H_t$ 同時送入兩個獨立預測頭：

$$\hat{S}_t = f_{Lang}(H_t),\quad \hat{I}_t = \sigma(f_{RGB}(H_t)).$$

Semantic Head $f_{Lang}$ 把特徵投影到 $d$ 維語意 embedding 空間以對齊語言；RGB Head $f_{RGB}$ 把特徵還原到影像空間以重建 RGB frame，提供感知一致性的輔助監督。這個雙頭設計是 §3.5 ablation 重點驗證的對象。

§4.3 Multi-Objective Training 把監督訊號分成兩大類。Semantic Loss 又再分為 time-agnostic 與 time-sensitive 兩支：前者用 SAM + DEVA 取得物件遮罩 $\{M_{i,t}\}$，再透過 CLIP 抽出每個 mask 區域的 embedding $e_{i,t}^{CLIP}$，組成 region-aligned 語意特徵圖 $S_t^{CLIP}$；後者進一步把 video-level 區域餵入 MLLM (Qwen2.5-VL-7B) 生成時序一致的描述，再用 LLM (e5-mistral-7b) 編碼為 dynamic 語意 ground truth $S_t^{dyn}$。最終 semantic loss 結合 L1 回歸與 cosine 相似度：

$$\mathcal{L}_{lang} = \sum_{t=1}^{T} \lambda_1 |\hat{S}_t - S_t|_1 + \lambda_2 (1 - \cos(\hat{S}_t, S_t)),\ \forall S_t \in \{S_t^{CLIP}, S_t^{dyn}\}.$$

Reconstruction Loss 用 L1–L2 hybrid 監督重建幀：

$$\mathcal{L}_{rgb} = \sum_{t=1}^{T} \lambda_{img} \|\hat{I}_t - I_t\|_1 + (1 - \lambda_{img}) \|\hat{I}_t - I_t\|_2^2,$$

其中 $\lambda_{img} \in [0, 1]$ 控制結構準確 (L1) 與像素平滑 (L2) 的取捨。最終目標 $\mathcal{L} = \alpha \mathcal{L}_{lang} + \beta \mathcal{L}_{rgb}$ 把語意對齊與視覺保真綁在一起。

整個 Method 章節為 §3.5 的實驗設計鋪好兩條伏筆：(i) RGB Head 是否真的有用？這在 ablation Table 4 直接被驗證 (移除後 IoU 掉約 5%、Acc 掉 1–2%)；(ii) DPT 是否優於更淺的架構？這在 Table 5 (UNet vs. MLP) 與 Appendix Table 7 (有無 DPT layer) 被進一步切片驗證。

### 3.5 Experiments (overview narrative)

(1400 words)

Experiments 章節以「兩個資料集 × 兩種訓練 regime × 兩類查詢」的三維矩陣展開，最後再用 ablation 與視覺化收尾。整體論證鏈是：先用 HyperNeRF 比 time-agnostic 與 time-sensitive 兩類查詢以驗證對動態語意的細粒度敏感性，再用 Neu3D 補充 long-range 但物件動態不顯著的場景以證明泛化能力，最後用 ablation 驗證 SBD 內部設計選擇。

§5.1 Experimental Setup 確立了實驗的三個基底。Training Data 沿用 4DLangSplat 提供的語意標註，特徵抽取上使用 OpenCLIP ViT-B/16 抽 CLIP 特徵、Qwen2.5-VL-7B-Instruct 抽動態語意、e5-mistral-7b 處理時變字幕，並訓練 autoencoder 把 CLIP 壓到 3 維、動態語意壓到 6 維。Implementation Details 顯示作者沿用 StreamVGGT 設定 (518px 輸入、最近 14 倍數裁切、最多 128 過去幀)，並用 batch size 8、初始 lr $4 \times 10^{-5}$、四張 RTX 3090 (24GB) 訓練，這個配置暗示方法的硬體門檻並不高。Baselines 對齊 4DLangSplat 的評測協議：time-agnostic 比較 LangSplat、Feature-3DGS、Gaussian Grouping、4DLangSplat；time-sensitive 比較 LangSplat、Deformable CLIP、Non-Status Field、4DLangSplat。值得注意的是 Per-scene 一欄帶 ✓/✗ 用以區分「per-scene 訓練」與「multi-video single-model 跨場景訓練」兩種 regime，這個欄位是後續主結果表格的核心結構性變數。

§5.2 Main Results 把兩種 regime 並排呈現。§5.2.1 HyperNeRF 上，Table 1 (time-agnostic) 顯示 per-scene 設定下 4DLangVGGT 在四個場景的平均 mIoU 達 85.02%、mAcc 98.77%，較 4DLangSplat 分別領先 2.07% mIoU、0.18% mAcc；multi-video 設定下 (Per-scene ✗) 平均 mIoU 仍有 83.99%，與 per-scene 結果差距很小，較 4DLangSplat 領先約 1% mIoU，凸顯跨場景泛化的可行性。Table 2 (time-sensitive) 在 americano、chick-chicken、split-cookie、espresso 四個場景上比較 Acc 與 vIoU，4DLangVGGT 在 per-scene 設定的平均 Acc 為 90.86%、vIoU 為 73.06%，超過 4DLangSplat (90.83% / 72.26%)；最有意思的是 multi-video 設定 (91.44% Acc / 74.74% vIoU) 反而比 per-scene 還好——作者解讀為跨場景訓練讓模型更能捕捉物件動態與語意狀態變化。

§5.2.2 Neu3D 把測試延伸到三個 long-range 場景 (coffee martini、cook spinach、cut roasted beef)，因為物件動態不顯著，只跑 time-agnostic 查詢。Table 3 顯示 4DLangVGGT 在 per-scene 平均達 87.41% mIoU、99.41% mAcc，再次領先 4DLangSplat (85.19% / 99.30%)；multi-video 設定的 85.64% mIoU / 99.37% mAcc 也接近 per-scene 結果，再次強化 cross-scene generalization 論點。

§5.2.3 Visualization 用 Fig. 3 (time-sensitive query "glasses contain darker brown liquid") 與 Fig. 4 (time-agnostic query "cookie") 作定性對比。Fig. 3 顯示 4DLangVGGT 能準確捕捉狀態轉變的時刻，而 4DLangSplat 經常產生時序不一致的遮罩或漏掉狀態邊界；Fig. 4 顯示在 fragmented cookie 場景下 4DLangVGGT 仍能輸出乾淨的物件遮罩，4DLangSplat 則明顯退化。這些定性結果替「方法在語意-時序動態上更敏銳」這個敘事補上肉眼可見的證據。

§5.3 Ablation Study 鎖定兩個設計選擇。Table 4 把 RGB Head 拿掉後，time-agnostic mIoU 從 83.99% 掉到 78.36% (-5.63%)、mAcc 從 98.67% 掉到 97.68% (-0.99%)、time-sensitive Acc 從 91.44% 掉到 88.52% (-2.92%)、vIoU 從 74.74% 掉到 70.94% (-3.80%)，作者由此論證 auxiliary reconstruction branch 對保留 appearance-level cues 不可或缺，並間接強化 semantic alignment。Table 5 比較 Semantic/RGB Head 的架構，UNet 全面優於 MLP (mIoU +0.95%、mAcc +1.16%、Acc +2.06%、vIoU +2.15%)，論點是 UNet 的層次化特徵能更好地捕捉細粒度結構。

附錄補充三個額外實驗以加強說服力：Appendix C.1 把 HyperNeRF 訓練的模型放到 Objectron 上做 cross-dataset 推論，視覺化顯示無 artifact 且渲染穩定；C.2 用語意相同但句法改寫的查詢 (paraphrased query) 測試 robustness，Table 6 顯示在 americano 與 chick-chicken 上，paraphrased 較 raw 的 Acc 降幅 (4DLangVGGT: -2.95% / -3.08%) 顯著小於 4DLangSplat (-14.73% / -7.36%)；Appendix D 的 Table 7 進一步移除 SBD 內部的 DPT layer，造成 +3.63% mIoU、+2.18% mAcc、+2.59% vIoU、+2.07% Acc 的全面退化，從而把 §4.2 的「DPT 是 SBD 學習主體」這個主張用數字釘死。

整體而言，§5 的論證鏈非常工整：兩個資料集驗證跨場景一致性、兩種 regime 驗證 feed-forward 的 deployment 優勢、兩類查詢驗證對時序動態的敏感度、三組 ablation (RGB Head / Head 架構 / DPT layer) 把方法的每個關鍵設計都單獨切片，並用 paraphrased query 與 cross-dataset 推論補上 robustness。

### 3.6 Conclusion / Limitations / Future Work

(350 words)

Conclusion 段落 (§6) 非常精簡，重申三個核心訊息：(1) 4DLangVGGT 是首個把 geometry-aware 4D perception 與 language grounding 統一在 feed-forward 架構中的框架；(2) 方法的關鍵元件是 Semantic Bridging Decoder (SBD)、auxiliary RGB head、與 joint supervision loss，三者合力 "bridges low-level geometric cues and high-level semantic alignment"；(3) 在 HyperNeRF 與 Neu3D 上的實驗證明 4DLangVGGT 不需 per-scene optimization 即可達到強效能與泛化，並在 scalability 與 efficiency 上勝過 Gaussian-splatting baseline。結語把這項工作定位成「通往 scalable, language-aware 4D semantic fields 的一步」，預告未來會擴展到更大規模資料集與更豐富的多模態監督。

Limitations 與 Future Works 段落 (Appendix E) 補上更具體的反思。Limitation 主要有兩點：第一，實驗只在 HyperNeRF 與 Neu3D 兩個資料集上驗證，作者直白地承認 "they do not fully reflect the scale and diversity of real-world environments"，因此泛化到更複雜大規模場景仍是未解問題；第二，動態語意監督的 fine-grained 程度仍有改進空間。

Future Work 提出三條線：(1) 擴展到更大、更多元的資料集，嚴謹評估 efficiency 與 robustness 在真實條件下的表現；(2) 借鑒 Mask Grounding 的精神 (Chng et al., 2024) 改善 fine-grained 與 precision 的動態語意監督，讓語言表述與局部視覺區域之間的對齊更精準；(3) 構建一個專為 4D language fields 設計的 domain-specific large model，作為 embodied AI、AR/VR、open-vocabulary 動態場景理解的 foundation model，把語意推理與幾何感知統一在更大尺度上。

整體來看，Conclusion 與 Limitations 的搭配在敘事上完成了兩個任務：一方面用 SBD + RGB Head + Joint Loss 三件套作為「方法可記憶的最小描述」收束全文；另一方面以「資料集規模有限、語意監督仍可細化、缺乏 4D 領域 foundation model」三個 limitation，把這篇工作定位為「proof-of-concept 階段」而非完成式，從而為未來的 scaling-up 與 foundation model 研究留下伏筆。值得注意的是，作者並未把 frozen StreamVGGT 是否限制了方法上限、或 SBD 是否能擴展到更高維 CLIP 特徵列為 limitation——這些是讀者可以追問的點。

## 4. Critical Profile

### 4.1 Highlights

- 提出首個 Transformer-based feed-forward 統一框架 4DLangVGGT,將動態幾何重建與 vision-language alignment 整合於單一網路,消除既有 4D Gaussian Splatting 方法所需的 per-scene optimization (§1, §3 contribution list)。
- 採用 frozen StreamVGGT 作為幾何骨幹,直接重用其在大規模影片上預訓練的 spatio-temporal representations,避免重學幾何並降低訓練成本 (§4.1)。
- Semantic Bridging Decoder 以 contextual-aware DPT 將 geometry tokens 轉成 unified 4D feature $H_t \in \mathbb{R}^{h \times w \times c}$,再經 dual head $f_{\text{Lang}}, f_{\text{RGB}}$ 同時輸出語意嵌入與 RGB 重建以維持 perceptual consistency (§4.2, Eq. 2–3)。
- Time-agnostic 監督以 SAM/DEVA mask + CLIP 對齊靜態物件語意,time-sensitive 監督則透過 Qwen2.5-VL-7B 產生 caption 再由 e5-mistral-7b 編碼,提供雙重 ground-truth (§4.3, Eq. 4–5; §A.1)。
- 在 HyperNeRF time-agnostic per-scene 設定下平均達 85.02 mIoU / 98.77 mAcc,較 4DLangSplat 的 82.95 / 98.59 高出約 2.07 mIoU (Table 1)。
- 在 HyperNeRF time-sensitive 設定下,multi-video single-model 設定 (91.44 Acc / 74.74 vIoU) 反而優於 per-scene (90.86 / 73.06),Acc +0.58、vIoU +1.68,顯示跨場景共享訓練未拖累時序辨識 (Table 2)。
- 在 Neu3D time-agnostic 上達 87.41 mIoU / 99.41 mAcc,相比 4DLangSplat 的 85.19 / 99.30 提升約 2.22 mIoU (Table 3)。
- Cross-query generalization 顯示 paraphrased query 下 4DLangVGGT 在 americano 僅下降 2.95,而 4DLangSplat 下降 14.73,說明對語言改寫較魯棒 (Table 6)。
- Ablation 顯示 RGB head 移除會使 mIoU 下降約 5.6、vIoU 下降約 3.8 (Table 4);DPT layer 加入帶來 +3.63 mIoU、+2.59 vIoU (Table 7);UNet head 較 MLP 全面領先 (Table 5),三項共同支撐架構選擇。
- 訓練資源輕量:僅 4 張 RTX 3090 (24 GB)、batch size 8、initial learning rate $4 \times 10^{-5}$,即可同時 fit HyperNeRF (6 scenes) 與 Neu3D (6 scenes) 的 multi-scene 模型 (§5.1, §A.1)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者明確指出實驗僅限於 HyperNeRF 與 Neu3D,場景數量小,無法充分反映 real-world 的 scale 與 diversity,對更複雜大規模環境的泛化仍待驗證 (§E Limitation, p. 16)。
- 作者承認 dynamic semantic supervision 的 fine-grained 對齊仍有改進空間,並引述 Mask Grounding (Chng et al., 2024) 作為未來改進方向,等同承認目前 mask-level 監督的精細度不足 (§E, p. 16)。
- 作者表示尚未建立 4D language field 的 domain-specific foundation model,意即現階段框架仍是 task-specific,並非可遷移的通用基底 (§E, p. 16)。

#### 4.2.2 Phyra-inferred

- 「Multi-video single model」實際上是在 HyperNeRF 6 個 scene 與 Neu3D 6 個 scene 上 jointly trained 後再於 *同一批* scene 推論,並未保留 held-out scene,因此 Table 1–3 中的 multi-scene 結果只能算 in-distribution 共享權重,並非真正的 cross-scene generalization,而論文卻反覆以「strong cross-scene generalization」描述 (§5.2.1, Table 1–3)。
- 關鍵 efficiency 主張缺乏量化證據:全文宣稱 feed-forward 取代 per-scene optimization 帶來 deployment efficiency 與 real-time 能力,但從未報告 inference latency、FPS、訓練時間或 GPU memory 與 4DLangSplat 的對照數字,使「scalability/efficiency」論點僅由架構描述支撐,而非數據 (§1, §5, §6)。
- HyperNeRF time-sensitive 的 per-scene 提升僅 0.03 Acc / 0.80 vIoU,Neu3D time-agnostic mAcc 僅 0.11 提升,卻在 abstract 與 §5.2.1 用「up to 2%」的最佳值來概括,屬於 selective framing,未呈現多數 metric 的實際幅度 (Abstract, §5.2.1, Table 2–3)。
- 與最直接的 concurrent 工作 4-LEGS (Fiebelman et al., 2025) 僅在 Related Works 一筆帶過,完全沒有任何 quantitative 或 qualitative 比較,使「first 4D Transformer-based language field」的優位敘事缺少同類對照 (§2)。
- Cross-dataset robustness 試驗僅以 Objectron 做 qualitative 視覺化,無 mIoU/Acc 指標 (Fig. 7),但在 §C.1 卻直接斷言「generalizes well beyond its training distribution」;Cross-query 試驗也僅含 americano、chick-chicken 兩類查詢,單樣本不足以支撐 linguistic robustness 的一般性結論 (§C.1, §C.2, Table 6)。
- StreamVGGT 預訓練品質本身決定 ceiling,但論文未對 backbone 解凍、替換 (例如改成 VGGT 或 DUSt3R)、或不同 memory cap (固定 128 frames) 做 ablation,讓 SBD 能否在弱 backbone 下仍奏效成為未檢驗的假設 (§4.1, §A.1)。
- 大量 hyperparameter 與壓縮選擇 ($\lambda_1=0.2, \lambda_2=0.01, \lambda_{\text{img}}=0.5$、CLIP→3D、dynamic→6D autoencoder、frame 裁切到 14 倍數) 既未 ablate 也未敘述敏感度,讀者無法判斷其對結果的真實影響範圍 (§A.1)。
- SAM/DEVA + MLLM 產生的 ground-truth 本身可能含遮罩錯誤或 caption 漂移,但論文未量測 supervision noise,也未提供 mask 失敗時模型行為,這對 dynamic state change (例如 closed→open) 的 evaluation 有直接影響 (§4.3, §5.2.1)。

### 4.3 Phyra's Judgment (summary)

真正具新意之處在於將 frozen StreamVGGT 當作 geometry backbone、再以 SBD 把 geometry tokens 投影到語言空間,從而把 4D language field 從 per-scene optimization 解放成 feed-forward inference;這個 *架構級* 重新定位是論文最值得肯定的一步。其餘環節 (CLIP + MLLM 雙重監督、DPT contextual head、UNet vs MLP) 屬於 engineering-only 組裝,效能增益亦多落在 0.1–2 mIoU 區間,並不戲劇化。核心未解問題仍是 *scale* 與 *true cross-scene generalization*:在 12 個訓練場景之外,框架是否仍能維持語意對齊、是否真有 deployment 級的 efficiency 優勢,論文均未提供決定性證據。

## 5. Methodology Deep Dive

### 5.1 Method Overview

整體框架可拆解為三個耦合元件：(1) 凍結的 **StreamVGGT geometry encoder**，作為時空幾何骨幹，從輸入影片序列 $\{I_t\}_{t=1}^T$ 抽取 **geometry tokens** $\{G_t\}$ 與 **camera tokens** $\{C_t\}$；(2) 可訓練的 **Semantic Bridging Decoder (SBD)**，將 geometry tokens 投影到語言對齊的語意空間；(3) **multi-objective training** 結合 time-agnostic 與 time-sensitive 雙重語意監督以及 RGB 重建損失 (paper §4)。整體設計避免逐場景最佳化的部署瓶頸,並可跨多場景聯合訓練、推論時直接套用。

幾何編碼路徑沿用 StreamVGGT 的 alternating-attention 架構：DINO image encoder $E$ 將 $I_t$ 轉成 image tokens $F_t$,搭配 camera token 後送入 aggregator $D$,在 frame-level 與 cross-frame self-attention 之間交替（採 causal temporal attention 以支援串流推論）,輸出 $\{C_t, G_t\} = D([C_t, F_t] \mid M_{t-1})$,其中 $M_t = M_{t-1} \cup [C_t, F_t]$ 為過去 token cache（最多 retain 128 frames,paper §5.1）。在本框架中,StreamVGGT 整段 **freeze**,理由有二：(i) 已在大規模影片資料預訓練,具強泛化的時空幾何表徵；(ii) 凍結可避免重學幾何,將訓練計算集中在語意對齊 (paper §4.1)。Camera tokens $C_t$ 雖凍結但在推論時被保留,用以將語意特徵反投影到 4D point cloud 空間。

語意橋接路徑為核心設計。SBD 先以 contextual-aware DPT $H_{\text{DPT}}^{\text{lang}}$ 處理 $\{G_t\}$,結合 local convolution 的空間敏感性與 Transformer 的全域建模能力,藉由 stacked self-attention layers 跨時空捕捉長程依賴,輸出 unified 4D feature $H_t \in \mathbb{R}^{h \times w \times c}$（公式 2）。$H_t$ 接著經由 dual-head decoding：semantic head $f_{\text{Lang}}$ 投影到 $d$-dim 語意嵌入 $\hat{S}_t \in \mathbb{R}^{h \times w \times d}$,RGB head $f_{\text{RGB}}$ 經 sigmoid $\sigma$ 重建出 $\hat{I}_t \in \mathbb{R}^{H \times W \times 3}$（公式 3）。雙頭設計確保語意對齊與外觀保真同時被優化,RGB 重建作為 auxiliary signal 強化感知一致性,在消融中對 mIoU 貢獻約 5%（Table 4）。

監督訊號分為兩路。**Time-agnostic supervision** 以 SAM/DEVA 取得物件遮罩 $\{M_{i,t}\}$,將遮罩區送入 CLIP 取得 $e_{i,t}^{\text{CLIP}} \in \mathbb{R}^{1 \times 1 \times d}$,賦予該物件所有像素形成 $S_t^{\text{CLIP}}$（公式 4）；**time-sensitive supervision** 將每個物件跨 frame 的 video-level regions 餵入 MLLM (Qwen2.5-VL-7B) 生成時間一致描述,再由 LLM (e5-mistral-7b) 編碼成動態語意 $e_{i,t}^{\text{dyn}}$ 並做 mask assignment 得 $S_t^{\text{dyn}}$（公式 5）。最終語意損失 $L_{\text{lang}}$ 結合 L1 regression 與 cosine similarity（公式 6）,RGB 損失 $L_{\text{rgb}}$ 採 L1–L2 hybrid（公式 7）,聯合目標 $L = \alpha L_{\text{lang}} + \beta L_{\text{rgb}}$（公式 8）。實作細節：CLIP autoencoder 壓至 3-dim,動態語意壓至 6-dim,輸入 frame resize 到 518 pixels 並 crop 到最近 14 的倍數,batch size 8,初始學習率 $4 \times 10^{-5}$,4× RTX 3090 (24GB) 訓練。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: video frames {I_t}_{t=1}^T
       I_t ∈ [B, T, 3, H, W]   where H=W≈518 (cropped to multiple of 14)

   │
   ▼  RGB frames I_t
┌─────────────────────────────────────────────────────────────┐
│  StreamVGGT Geometry Encoder (FROZEN)                       │
│                                                              │
│   ┌──────────────────────┐                                  │
│   │ DINO image encoder E │  I_t → F_t                       │
│   └──────────────────────┘                                  │
│       [B, T, 3, H, W] ──→ [B, T, N_p, d_v]                  │
│                                where N_p = (H/14)·(W/14)    │
│                                d_v = ? (DINO hidden dim)    │
│                                                              │
│   append camera token C_t:  [C_t, F_t]                       │
│       [B, T, 1+N_p, d_v]                                    │
│                                                              │
│   ┌────────────────────────────────────────┐                │
│   │ Alternating-Attention Aggregator D     │                │
│   │ (frame-level ↔ causal temporal attn,   │                │
│   │  cache M_t = M_{t-1} ∪ [C_t, F_t],     │                │
│   │  max 128 past frames)                  │                │
│   └────────────────────────────────────────┘                │
│       [B, T, 1+N_p, d_v] ──→ [B, T, 1+N_p, d_v]             │
│                                                              │
│   split → camera tokens C_t  : [B, T, 1, d_v]                │
│         → geometry tokens G_t: [B, T, N_p, d_v]              │
└─────────────────────────────────────────────────────────────┘
   │
   │ G_t (used for semantic alignment, trainable path below)
   │ C_t (frozen; used at inference to back-project to 4D point cloud)
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Semantic Bridging Decoder (SBD, TRAINABLE)                 │
│                                                              │
│   ┌────────────────────────────────────┐                    │
│   │ Contextual-aware DPT H_DPT^lang    │   (Eq. 2)          │
│   │ stacked self-attention over        │                    │
│   │ spatial + temporal dims            │                    │
│   └────────────────────────────────────┘                    │
│       G_t [B, T, N_p, d_v] ──→ H_t [B, T, h, w, c]          │
│                                where (h, w) = token map     │
│                                resolution, c = feature dim  │
│                                                              │
│         H_t [B, T, h, w, c]                                 │
│           │                                                  │
│           ├──────────────► f_Lang  (UNet, ablated MLP)       │
│           │                ──→ Ŝ_t [B, T, h, w, d]           │
│           │                where d = 3 (CLIP-AE) or          │
│           │                d = 6 (dyn-AE), per query mode    │
│           │                                                  │
│           └──────────────► f_RGB ∘ σ  (UNet)                 │
│                            ──→ Î_t [B, T, H, W, 3]           │
└─────────────────────────────────────────────────────────────┘
   │                                       │
   │ Ŝ_t                                   │ Î_t
   ▼                                       ▼
┌────────────────────────┐          ┌──────────────────────┐
│ Semantic Supervision   │          │ RGB Reconstruction   │
│ Ground-Truth Generation│          │ Loss L_rgb (Eq. 7)   │
│                        │          │ ‖Î_t − I_t‖_1 + L2   │
│ SAM/DEVA → {M_{i,t}}   │          └──────────────────────┘
│   M_{i,t} ∈ [B,T,N,h,w]│                   │
│                        │                   │
│ Time-agnostic (Eq. 4): │                   │
│   CLIP(I_t·M_{i,t})    │                   │
│   → e^{CLIP}_{i,t}     │                   │
│     [B,T,N,1,1,d]      │                   │
│   → S^{CLIP}_t          │                   │
│     [B,T,h,w,d]         │                   │
│                        │                   │
│ Time-sensitive (Eq. 5):│                   │
│   MLLM({I_t·M_{i,t}}_t)│                   │
│   → captions           │                   │
│   → LLM → e^{dyn}_{i,t}│                   │
│     [B,T,N,1,1,d]      │                   │
│   → S^{dyn}_t           │                   │
│     [B,T,h,w,d]         │                   │
│                        │                   │
│ S_t ∈ {S^{CLIP}_t,     │                   │
│        S^{dyn}_t}       │                   │
└────────────────────────┘                   │
   │                                          │
   │ L_lang (Eq. 6):                          │
   │   λ_1 ‖Ŝ_t − S_t‖_1                      │
   │   + λ_2 (1 − cos(Ŝ_t, S_t))              │
   ▼                                          ▼
        Joint Objective (Eq. 8):
        L = α · L_lang + β · L_rgb
```

備註：DINO hidden dim $d_v$、SBD 內部維度 $c$、token-map 解析度 $(h, w)$ 在論文中未明確給出具體數值,故以 `?` 標示並於 §5.3 各模組「Implementation Details」說明。

### 5.3 Per-Module Breakdown

#### 5.3.1 StreamVGGT Geometry Encoder (Frozen)

**Function:** 從輸入影片序列抽取時空幾何 token,作為語意對齊的幾何基礎,並提供 camera tokens 供推論時反投影使用。

**Input:**
- Name: $\{I_t\}_{t=1}^T$
- Shape: `[B, T, 3, H, W]`,其中 $H = W \approx 518$（依 paper §5.1 cropped to nearest multiple of 14）
- Source: 原始影片 frames

**Output:**
- Name: geometry tokens $\{G_t\}$、camera tokens $\{C_t\}$
- Shape: $G_t$ `[B, T, N_p, d_v]`（$N_p = (H/14) \cdot (W/14)$,$d_v$ 為 DINO hidden dim,paper 未明列）；$C_t$ `[B, T, 1, d_v]`
- Consumer: $G_t$ 進入 SBD 的 contextual-aware DPT；$C_t$ 在推論期反投影到 4D point cloud space

**Processing:**

依 paper §3 與 §4.1 描述,流程為 $F_t = E(I_t)$（DINO 將 $I_t$ patchify 成 image tokens）,接著 $[C_t, G_t] = D([C_t, F_t] \mid M_{t-1})$,其中 $D$ 為 alternating-attention transformer,在 frame-level self-attention 與 cross-frame causal temporal attention 之間交替；cache $M_t = M_{t-1} \cup [C_t, F_t]$ 於串流推論時逐 frame 更新（公式 1）。

**Key Formulas:**

$$
F_t = E(I_t); \quad [C_t, G_t] = D\big([C_t, F_t] \,\big|\, M_{t-1}\big); \quad M_t = M_{t-1} \cup [C_t, F_t]
$$

**Implementation Details:**

採用 StreamVGGT aggregator,整段 freeze。輸入 frames resize 到 518 pixels 並 crop 到 14 的倍數以對齊 DINO patch grid。Cache 最多保留 128 past frames 以平衡記憶體與時序依賴。Image encoder 使用 DINO/DINOv2 (paper §3 引用 Caron et al., 2021；Oquab et al., 2023)。$d_v$ 與 $N_p$ 的具體數值論文未明確標示。

#### 5.3.2 Contextual-aware DPT $H_{\text{DPT}}^{\text{lang}}$

**Function:** 將 geometry tokens 轉換為具長程時空依賴的 unified 4D feature representation,提升語意可分性。

**Input:**
- Name: $\{G_t\}$
- Shape: `[B, T, N_p, d_v]`
- Source: StreamVGGT geometry encoder

**Output:**
- Name: $\{H_t\}$
- Shape: `[B, T, h, w, c]`,其中 $h, w$ 為 token map 解析度,$c$ 為轉換後特徵維度
- Consumer: dual-head（semantic head $f_{\text{Lang}}$ 與 RGB head $f_{\text{RGB}}$）

**Processing:**

依 paper §4.2 描述,DPT 結合 local convolution 的空間敏感性與 Transformer 的全域建模能力,藉由 stacked self-attention layers 將 geometry tokens 轉成 contextually enriched feature,跨 spatial 與 temporal 維度捕捉長程依賴（公式 2）。此模組與 StreamVGGT 內部的幾何 DPT head 不同,為獨立引入的語意導向 DPT,且在訓練中保持可學習。

**Key Formulas:**

$$
H_t = H_{\text{DPT}}^{\text{lang}}(G_t), \quad \forall t \in [1, \dots, T]
$$

**Implementation Details:**

paper 並未明列 self-attention layer 數量、$c$ 的具體值、或 $(h, w)$ 對應 input resolution 的明確 downsampling 比例。論文僅指出此模組在訓練時保持可訓練 (trainable during optimization)。

#### 5.3.3 Dual-Head Decoder (Semantic Head $f_{\text{Lang}}$ 與 RGB Head $f_{\text{RGB}}$)

**Function:** 將 unified 4D feature 同時投影到語意嵌入空間（對齊 CLIP/MLLM-LLM 語意）以及 image space（RGB 重建以維持感知保真）。

**Input:**
- Name: $H_t$
- Shape: `[B, T, h, w, c]`
- Source: contextual-aware DPT $H_{\text{DPT}}^{\text{lang}}$

**Output:**
- Name: 預測語意 $\hat{S}_t$、重建影像 $\hat{I}_t$
- Shape: $\hat{S}_t$ `[B, T, h, w, d]`,其中 $d = 3$（CLIP autoencoder 壓縮維度）或 $d = 6$（動態語意 autoencoder 壓縮維度,paper §5.1）；$\hat{I}_t$ `[B, T, H, W, 3]`
- Consumer: $\hat{S}_t$ 進入 $L_{\text{lang}}$；$\hat{I}_t$ 進入 $L_{\text{rgb}}$

**Processing:**

依 paper §4.2 描述,$f_{\text{Lang}}$ 將 $H_t$ 投影到 $d$-dim 語意嵌入空間以對齊 CLIP（time-agnostic）或 MLLM/LLM（time-sensitive）監督；$f_{\text{RGB}}$ 經 sigmoid $\sigma$ 將 $H_t$ 解碼回 image space 以重建 RGB frames（公式 3）。Ablation Table 5 顯示 UNet 設計在 mIoU、mAcc、Acc、vIoU 上均優於 MLP（+0.95% mIoU、+1.16% mAcc、+2.06% Acc、+2.15% vIoU）,顯示 UNet 階層式特徵對細粒度結構的價值。

**Key Formulas:**

$$
\hat{S}_t = f_{\text{Lang}}(H_t), \quad \hat{I}_t = \sigma(f_{\text{RGB}}(H_t)), \quad \forall t \in [1, \dots, T]
$$

**Implementation Details:**

兩個 head 採 UNet 架構（Table 5 ablation 確認）。語意維度 $d$ 由外部 autoencoder 決定：CLIP 特徵壓至 3-dim,動態語意（e5-mistral-7b 編碼）壓至 6-dim,follow 4DLangSplat 的設定 (Li et al., 2025c)。RGB head 末端使用 sigmoid 將輸出映射到 $[0, 1]$。

#### 5.3.4 Semantic Supervision Generation (SAM/DEVA + CLIP / MLLM + LLM)

**Function:** 產生 time-agnostic 與 time-sensitive 雙重語意 ground truth,作為 $\hat{S}_t$ 的監督訊號。

**Input:**
- Name: $I_t$、object masks $\{M_{i,t}\}_{i,t=1,1}^{N,T}$
- Shape: $I_t$ `[B, T, 3, H, W]`；$M_{i,t}$ `[B, T, N, h, w, 1]`,$N$ 為物件數
- Source: 原始 frames、SAM (Kirillov et al., 2023) + DEVA (Cheng et al., 2023) 物件級 mask

**Output:**
- Name: $S_t^{\text{CLIP}}$、$S_t^{\text{dyn}}$
- Shape: 兩者皆為 `[B, T, h, w, d]`
- Consumer: 進入 $L_{\text{lang}}$ 與 $\hat{S}_t$ 對齊

**Processing:**

**Time-agnostic** (公式 4)：對每個 mask 區域 $I_t \cdot M_{i,t}$ 取 CLIP embedding $e_{i,t}^{\text{CLIP}} = f_{\text{CLIP}}(I_t \cdot M_{i,t}) \in \mathbb{R}^{1 \times 1 \times d}$,再將該 embedding 賦予該 mask 內所有像素,加總得 $S_t^{\text{CLIP}} = \sum_{i=1}^{N} e_{i,t}^{\text{CLIP}} \cdot M_{i,t}$。

**Time-sensitive** (公式 5)：將每個物件跨 frame 的 video-level regions $\{I_t \cdot M_{i,t}\}_{t=1}^T$ 餵入 MLLM ($f_{\text{MLLM}}$,Qwen2.5-VL-7B) 生成時間一致 caption,再由 LLM ($f_{\text{LLM}}$,e5-mistral-7b) 編碼成 $\{e_{i,t}^{\text{dyn}}\}_{t=1}^T$,做 mask assignment 得 $S_t^{\text{dyn}} = \sum_{i=1}^{N} e_{i,t}^{\text{dyn}} \cdot M_{i,t}$。

**Key Formulas:**

$$
e_{i,t}^{\text{CLIP}} = f_{\text{CLIP}}(I_t \cdot M_{i,t}), \quad S_t^{\text{CLIP}} = \sum_{i=1}^{N} e_{i,t}^{\text{CLIP}} \cdot M_{i,t}
$$

$$
\{e_{i,t}^{\text{dyn}}\}_{t=1}^{T} = f_{\text{LLM}}\!\left(f_{\text{MLLM}}\!\left(\{I_t \cdot M_{i,t}\}_{t=1}^{T}\right)\right), \quad S_t^{\text{dyn}} = \sum_{i=1}^{N} e_{i,t}^{\text{dyn}} \cdot M_{i,t}
$$

**Implementation Details:**

CLIP 採 OpenCLIP ViT-B/16 (paper §5.1)。MLLM 採 Qwen2.5-VL-7B-Instruct (Bai et al., 2025)。LLM 採 e5-mistral-7b (follow 4DLangSplat 對 time-varying captions 的處理)。雙重監督使模型同時學到靜態物件級語意與時間動態語意,避免時序語意漂移。

#### 5.3.5 Multi-Objective Joint Loss

**Function:** 結合語意對齊損失與 RGB 重建損失,聯合優化語意一致性與外觀保真。

**Input:**
- Name: $\hat{S}_t, S_t \in \{S_t^{\text{CLIP}}, S_t^{\text{dyn}}\}$、$\hat{I}_t, I_t$
- Shape: $\hat{S}_t, S_t$ `[B, T, h, w, d]`；$\hat{I}_t, I_t$ `[B, T, H, W, 3]`
- Source: dual-head decoder、ground-truth generation、原始 frames

**Output:**
- Name: scalar loss $L$
- Shape: `[1]`
- Consumer: backpropagation 更新 SBD 參數（StreamVGGT 凍結）

**Processing:**

語意損失結合 L1 regression 與 cosine similarity（公式 6）以同時對齊絕對值與方向；RGB 重建採 L1–L2 hybrid（公式 7）,L1 強化結構準確,L2 強化像素平滑。最終目標為加權和（公式 8）。Ablation Table 4 顯示移除 RGB Head 會導致 mIoU 下降約 5%、Acc 下降 1–2%,印證 auxiliary RGB branch 對語意對齊的支援作用。

**Key Formulas:**

$$
L_{\text{lang}} = \sum_{t=1}^{T} \lambda_1 \|\hat{S}_t - S_t\|_1 + \lambda_2 \big(1 - \cos(\hat{S}_t, S_t)\big), \quad S_t \in \{S_t^{\text{CLIP}}, S_t^{\text{dyn}}\}
$$

$$
L_{\text{rgb}} = \sum_{t=1}^{T} \lambda_{\text{img}} \|\hat{I}_t - I_t\|_1 + (1 - \lambda_{\text{img}}) \|\hat{I}_t - I_t\|_2^2
$$

$$
L = \alpha L_{\text{lang}} + \beta L_{\text{rgb}}
$$

**Implementation Details:**

$\lambda_1, \lambda_2$ 為語意損失權重；$\lambda_{\text{img}} \in [0, 1]$ 控制 L1/L2 trade-off；$\alpha, \beta \geq 0$ 控制兩大目標相對貢獻。論文未明列上述權重的具體數值。Optimizer 與 scheduler 細節未給出,僅標示 batch size 8、初始學習率 $4 \times 10^{-5}$、4× RTX 3090 (24GB) GPUs (paper §5.1)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| HyperNeRF (Park et al., 2021) | 4D 開放詞彙語意 grounding（time-agnostic 與 time-sensitive 查詢） | 6 個動態場景（§1） | 同時用於 per-scene 訓練與 multi-video single-model 訓練／推論；評估 scene 包含 americano、chick-chicken、split-cookie、torchocolate、espresso（Tables 1–2） |
| Neu3D (Li et al., 2022) | 4D time-agnostic 語意 grounding（長序列、動態較弱） | 6 個動態場景（§1） | per-scene 與 multi-video single-model 訓練／推論；評估 scene 為 coffee martini、cook spinach、cut roasted beef（Table 3） |
| 4DLangSplat semantic annotation set (Li et al., 2025c) | 動態場景語意分割監督標註 | the paper does not specify 規模 | 作為 HyperNeRF / Neu3D 的語意 ground-truth 來源（§5.1） |
| Objectron (Ahmadyan et al., 2021) | 跨資料集泛化視覺化驗證 | the paper does not specify | 僅在附錄 C.1 用於 cross-dataset 推論（不參與訓練） |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| mIoU | time-agnostic 查詢下，預測 mask 與 GT mask 的平均 IoU（附錄 A.1） | yes |
| mAcc | time-agnostic 查詢下，正確預測像素的平均比例（附錄 A.1） | no |
| Acc | time-sensitive 查詢下，正確判定的 frame 比例（附錄 A.1） | yes |
| vIoU | time-sensitive 查詢下，預測時間區間內的空間對齊 IoU（附錄 A.1） | yes |

### 6.3 Training and Inference Settings

- **硬體**：4 張 NVIDIA GeForce RTX 3090 (24 GB) GPU（§5.1）。
- **Batch size**：8（§5.1）。
- **Optimizer**：AdamW，weight decay $1 \times 10^{-4}$，gradient clipping $1.0$（附錄 A.1）。
- **Learning rate schedule**：初始學習率 $4 \times 10^{-5}$；warm-up 20 epochs，之後採 constant 或 cosine decay（§5.1、附錄 A.1）。
- **Training steps / epochs 總數**：the paper does not specify。
- **Loss 權重**：$\lambda_1 = 0.2$、$\lambda_2 = 0.01$（Eq. 6），$\lambda_{\text{img}} = 0.5$（Eq. 7）。$\alpha, \beta$（Eq. 8）the paper does not specify。
- **凍結策略**：StreamVGGT 幾何 encoder 全程凍結，僅訓練 Semantic Bridging Decoder（§4.1、附錄 A.1）。
- **輸入處理**：frames resize 到 518 像素後 center-crop 到 14 的最近倍數，以符合 StreamVGGT 的 patch 結構（§5.1、附錄 A.1）。
- **Streaming memory**：推論時最多保留 128 個過去 frame 的 cache token（§5.1）。
- **Feature 維度壓縮**：CLIP 512-d 經 autoencoder 壓到 3-d；E5 4096-d 壓到 6-d（附錄 A.1）。
- **語意監督模型**：CLIP 為 OpenCLIP ViT-B/16；MLLM 為 Qwen2.5-VL-7B-Instruct；LLM 為 e5-mistral-7b（§5.1）。
- **推論流程**：StreamVGGT 抽取 geometry tokens → SBD 同時輸出 RGB 與 semantic embeddings；幾何分支輸出 depth map 與 camera pose，經 inverse-projection 上抬成 3D point cloud，再以 RGB／semantics colorize 形成 4D 語意場（附錄 A.2、Fig. 5）。

### 6.4 Main Results

HyperNeRF, time-agnostic（Average，Table 1）：

| Method | mIoU | mAcc | Notes |
|---|---|---|---|
| LangSplat | 73.54 | 97.72 | per-scene |
| Feature-3DGS | 38.40 | 70.75 | per-scene |
| Gaussian Grouping | 57.02 | 82.22 | per-scene |
| 4DLangSplat | 82.95 | 98.59 | per-scene，前 SoTA |
| **4DLangVGGT (Ours, per-scene)** | **85.02** | **98.77** | 較 4DLangSplat +2.07 mIoU |
| **4DLangVGGT (Ours, multi-video)** | **83.99** | **98.67** | 單一模型跨 6 個 scene 推論，仍勝過所有 per-scene 基線 |

HyperNeRF, time-sensitive（Average，Table 2）：

| Method | Acc | vIoU | Notes |
|---|---|---|---|
| LangSplat | 54.01 | 22.65 | per-scene |
| Deformable CLIP | 61.80 | 44.72 | per-scene |
| Non-Status Field | 87.58 | 68.57 | per-scene |
| 4DLangSplat | 90.83 | 72.26 | per-scene，前 SoTA |
| **4DLangVGGT (Ours, per-scene)** | **90.86** | **73.06** | 較 4DLangSplat +0.03 Acc／+0.80 vIoU |
| **4DLangVGGT (Ours, multi-video)** | **91.44** | **74.74** | 跨場景單模型反而最高 |

Neu3D, time-agnostic（Average，Table 3）：

| Method | mIoU | mAcc | Notes |
|---|---|---|---|
| Feature-3DGS | 34.46 | 90.47 | per-scene |
| Gaussian Grouping | 57.51 | 94.79 | per-scene |
| LangSplat | 60.93 | 98.04 | per-scene |
| 4DLangSplat | 85.19 | 99.30 | per-scene，前 SoTA |
| **4DLangVGGT (Ours, per-scene)** | **87.41** | **99.41** | 較 4DLangSplat +2.22 mIoU |
| **4DLangVGGT (Ours, multi-video)** | **85.64** | **99.37** | 跨場景單模型仍微幅勝出 |

### 6.5 Ablation Studies

- **移除 RGB Head（Table 4，HyperNeRF, multi-video）**：mIoU 從 83.99 → 78.36（−5.63），mAcc 從 98.67 → 97.68，Acc 從 91.44 → 88.52，vIoU 從 74.74 → 70.94。**這是真正的診斷性實驗**，因為作者把 RGB head 設計為輔助分支，實驗驗證了「外觀重建可強化語意對齊」的核心主張，而非單純確認「多任務有幫助」。
- **Heads 架構：UNet vs MLP（Table 5）**：UNet 比 MLP 在 mIoU/mAcc/Acc/vIoU 各高 +0.95／+1.16／+2.06／+2.15。屬於診斷性，但結論偏可預期（hierarchical features 勝過 shallow MLP），且僅比較兩種架構，缺少其他常見 head（例如 transformer head 或更深 MLP）的對照。
- **Hlang_DPT 層（附錄 D, Table 7）**：移除 contextual DPT 後，mIoU −3.63、mAcc −2.18、vIoU −2.59、Acc −2.07。直接驗證了 SBD 的核心新組件 $H^{\text{lang}}_{\text{DPT}}$（Eq. 2）對語意鑑別力的貢獻，屬於診斷性實驗。
- **跨 query 泛化（附錄 C.2, Table 6）**：在 americano／chick-chicken 兩個 scene 上將 query 改寫為語意相同但語法不同的版本，4DLangVGGT 退化僅 −2.95／−3.08，而 4DLangSplat 退化 −14.73／−7.36。這是有價值的穩健性實驗，但只覆蓋兩個 scene、只與單一基線比較，較像 spot-check。
- **缺口**：缺少對「凍結 vs fine-tune StreamVGGT encoder」、「time-agnostic vs time-sensitive 監督拆解」、「semantic loss 中 L1 vs cosine 兩項拆解（$\lambda_1, \lambda_2$）」、以及「latent 維度 (3-d, 6-d) 選擇」等核心設計選擇的拆解，這些都是 §4 主動提出但未被 ablation 驗證的決策。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — 4DLangSplat（CVPR 2025）為當前 4D language field 的代表 SoTA，並在 HyperNeRF/Neu3D 上同時使用 LangSplat、Feature-3DGS、Gaussian Grouping、Deformable CLIP、Non-Status Field 等多個基線（Tables 1–3）。
- [partial] Has cross-task / cross-dataset evaluation (not just one benchmark) — 在 HyperNeRF 與 Neu3D 兩個資料集上評估，並在附錄 C.1 對 Objectron 做 cross-dataset 視覺化；但 Objectron 僅有定性結果、無數值指標，且兩個訓練資料集均屬同類「動態場景重建」基準。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — RGB Head 與 DPT layer ablation 直接針對 SBD 的新組件且結果顯著；但 Heads 架構僅 UNet vs MLP 兩點比較，且 time-agnostic／time-sensitive 監督的拆解、$\lambda_1/\lambda_2$ 權重敏感度等關鍵設計選擇未被 ablation。
- [missing] Has a scaling study (size, length, or compute) — 全文未提供模型大小、序列長度（雖有 128 frame cache 上限，但無在不同長度下的效能曲線）或訓練資料量的 scaling 實驗。
- [missing] Has an efficiency / wall-clock comparison — 摘要與引言反覆強調「feed-forward 部署效率」優於 per-scene Gaussian Splatting，但實驗章節未提供 inference latency、FPS、訓練時間或記憶體佔用的量化對比。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有 Tables 1–7 僅報告單一數值，未見 std、信賴區間或 multi-seed 結果；不同 scene 的差異也未做統計顯著性檢定。
- [partial] Releases code / weights / data sufficient for reproducibility — 摘要提及「Our code released in 4DLangVGGT Repository」（§Abstract），但未在論文內列出 weights、訓練 epoch 總數或完整超參數（例如 $\alpha, \beta$ 與總訓練步數），重現所需資訊不完整。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 首個 Transformer-based feed-forward 統一 4D language field 框架。** *Partially supported.* 架構本身確實是 first-of-its-kind 的整合,但與最相關的 concurrent 工作 4-LEGS 完全沒有 quantitative 對照 (§2),「first」之主張僅由時間排序與 GS 類方法相比成立,並未在同等 feed-forward 對手中受檢驗。
- **Claim 2: SBD 能在不破壞幾何結構的前提下,將 geometry tokens 投影到語言對齊空間。** *Supported.* Table 4 (移除 RGB head 損失約 5 mIoU)、Table 5 (UNet vs MLP)、Table 7 (DPT 帶來 +3.63 mIoU) 三組 ablation 共同支撐 SBD 子模組對最終效能的貢獻。
- **Claim 3: 模型可 jointly trained across multiple scenes 並 directly applied during inference。** *Supported in distribution, overclaimed out of distribution.* 在 HyperNeRF 6 + Neu3D 6 同 batch 訓練、同 batch 推論的設定 (Tables 1–3) 是成立的,但 §5.2 描述為「cross-scene generalization with shared training weights」忽略了 *held-out scene* 的缺席;Objectron 的 cross-dataset 實驗僅有 qualitative 圖 (Fig. 7),不足以證明 out-of-distribution generalization。
- **Claim 4: 達到 SOTA,per-scene 提升至多 2%、multi-scene 約 1%。** *Partially supported.* HyperNeRF/Neu3D 的 mIoU 確實穩定優於 4DLangSplat,但提升幅度高度集中在 mIoU,mAcc 多在 0.1–0.2 之譜;time-sensitive Acc 在 HyperNeRF per-scene 僅 +0.03,「up to 2%」 是上界而非平均,abstract 的描述偏向 best-case framing。
- **Claim 5: 在 deployment efficiency 上優於 GS-based 方法。** *Unsupported by numbers.* 全文僅以「avoids per-scene optimization」推論 efficiency,未提供 inference FPS、訓練時間或 memory 對照表,屬於 architectural argument 而非實證結論。

### 7.2 Fundamental Limitations of the Method

**Backbone-bounded ceiling.** 因 StreamVGGT 全程 frozen,模型語意品質與時序穩定度受 backbone 預訓練分布所封頂;當測試影片落入 StreamVGGT 弱項 (long-range tracking、低紋理、嚴重遮擋) 時,SBD 即使再精細也無法重建幾何資訊。論文沒有檢驗 backbone 替換或部分解凍,意味這項依賴目前是 *結構性*、而非 hyperparameter 級的問題。

**Mask-supervision bottleneck.** Time-agnostic 監督完全建立在 SAM/DEVA 產生的 object mask 上,time-sensitive 監督也須先有 per-object masked region 才能餵給 MLLM。當 SAM/DEVA 在動態、遮擋、或細小物件上漏 mask 或 ID switch 時,監督訊號會直接噪化。論文沒有提供 mask quality 與下游 mIoU 的相關分析,這個 dependency 不是靠調 loss 權重能解掉的。

**Compression-bounded language fidelity.** 將 CLIP (512D) 壓到 3D、dynamic (4096D) 壓到 6D 雖讓 head 可學,但對 open-vocabulary query 而言這是極為激進的 dimensional bottleneck,任何細粒度語意 (如「dark brown liquid」 vs 「light-colored liquid」) 都需在 6D 內被分離;此設計在 query 多樣性增加時會迅速飽和,且論文未量化 autoencoder 重建誤差對最終 grounding 的影響。

**Scene-scale gap between training and the deployment claim.** 「scalable, real-world deployment」需要在數百到數千場景上展示,但目前只在 12 個 HyperNeRF/Neu3D 場景上聯合訓練;framework 是否會在更大 scene mix 下出現 *semantic interference* (相似物件跨 scene 混淆) 是未知的。這不是 future work,而是當前 multi-scene 結果與 efficiency narrative 的核心張力。

### 7.3 Citations Worth Tracking

- **Zhuo et al., 2025 (StreamVGGT).** 整篇方法以此為 frozen backbone,要判斷 4DLangVGGT 的能力上限,必須先讀懂 StreamVGGT 的 streaming attention、memory cache 與其 known failure modes。
- **Li et al., 2025c (4DLangSplat).** 主要 baseline 與監督管線 (caption + e5-mistral) 來源;比較與差距理解都需從這篇開始。
- **Fiebelman et al., 2025 (4-LEGS).** 唯一 concurrent 的 4D language field 工作,論文卻未做 quantitative 比較,讀者必須自行對照其評估設定才能判斷 4DLangVGGT 的相對優劣。
- **Wang et al., 2025a (VGGT).** StreamVGGT 的 static 前身,關係到 alternating attention、camera/geometry token 設計的 *為什麼*,對理解 SBD 為何能直接接 geometry tokens 至關重要。
- **Chng et al., 2024 (Mask Grounding).** 作者明示為 future direction;若要評估「fine-grained alignment」是否真有提升空間,Mask Grounding 是最相關的對照基線。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在真正 *held-out* scene (例如把 HyperNeRF 切 train/test、或在 Neu3D 上訓練、HyperNeRF 上推論) 下,multi-scene 模型的 mIoU 衰退幅度為何?目前 Table 1–3 的 multi-scene 設定無法回答此問題。
- [ ] 與 4DLangSplat 相比,4DLangVGGT 的 inference latency、per-frame FLOPs、訓練 wall-clock 究竟差幾個數量級?「real-time、scalable」的主張需要這些數字。
- [ ] 將 CLIP 壓縮到 3D、dynamic feature 壓縮到 6D 各自損失多少 retrieval 精度?在 query 數量擴大到上百條 paraphrased query 時是否仍維持 cross-query 穩健性?
- [ ] 若把 StreamVGGT 替換成 DUSt3R / VGGT 或部分解凍 last $k$ blocks,SBD 還能否維持目前的 mIoU?backbone 是否其實仍是 bottleneck?
- [ ] SAM/DEVA 的 mask quality (例如 IoU 與 ID consistency) 與最終 vIoU 的 correlation 為何?在 mask 失敗的 frame 區間,模型輸出表現如何?
- [ ] Time-sensitive 設定下 multi-scene 反勝 per-scene (HyperNeRF Acc 91.44 vs 90.86) 的成因是 regularization、資料量增加,還是 per-scene 模型過擬合?未經分析便無法判斷哪一個才是主導因素。
- [ ] 對 4-LEGS 在相同 HyperNeRF/Neu3D 設定下的 head-to-head 比較數字為何?目前完全缺席,使 「first」claim 缺乏 concurrent baseline。

### 8.2 Improvement Directions

1. **Held-out scene split + 量化 efficiency 表。** 將 HyperNeRF/Neu3D 切成 train/val/test scene,並補上 inference FPS、訓練時間、GPU memory 對 4DLangSplat 的直接比較表;這對所有 efficiency/generalization 主張都是最低成本的補強,且不需要修改方法。
2. **Backbone ablation。** 對 StreamVGGT 換成 VGGT、DUSt3R,以及 last-$N$ block 解凍,做 mIoU 變化曲線。理由:可以分離 SBD 的功勞與 backbone 預訓練的功勞,讓 contribution claim 更乾淨。
3. **Mask-quality 隔離實驗。** 用 GT mask 取代 SAM/DEVA 跑一次 oracle 上界,並用刻意 degrade 的 mask 跑一次 lower-bound;這能直接量化「supervision noise 是不是當前瓶頸」,並引導未來該投資 mask 還是 SBD。
4. **替換 autoencoder 維度為 32D / 64D。** 目前 3D / 6D 是相當激進的壓縮;放寬維度或改用 PCA-then-residual 可在不改架構下提升細粒度 query 區分度,代價只是 head 輸出維度與 GPU memory。
5. **加入 Mask Grounding 風格的 token-level 對齊損失。** 作者已將其列為 future work;最低破壞性的做法是 freeze 既有兩 head,並新增一條 token-pixel attention loss,以細化 dynamic 描述對局部區域的 grounding 精度。
6. **Concurrent baseline 對照。** 加入 4-LEGS 的同設定 mIoU/vIoU,即使僅在一個 scene 子集做也能立刻補上「first 4D language field」claim 缺失的對照證據。
7. **Cross-dataset quantitative。** 將 Objectron 視覺化升級為帶 mIoU 的 cross-dataset 表;若無 ground-truth 語意 mask,可用 CLIP retrieval-based proxy 指標,先建立可衡量的 OOD baseline。
