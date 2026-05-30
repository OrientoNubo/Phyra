<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# InfiniDepth — InfiniDepth: Arbitrary-Resolution and Fine-Grained Depth Estimation with Neural Implicit Fields

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | InfiniDepth |
| Paper full title | InfiniDepth: Arbitrary-Resolution and Fine-Grained Depth Estimation with Neural Implicit Fields |
| arXiv ID | 2601.03252 |
| Release date | 2026-01-06 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2601.03252 |
| PDF link | https://arxiv.org/pdf/2601.03252v1 |
| Code link | https://github.com/zju3dv/InfiniDepth |
| Project page | https://zju3dv.github.io/InfiniDepth |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Hao Yu | Zhejiang University; Li Auto | https://ritianyu.github.io/ | first author (equal contribution); MS student at ZJU, intern at Li Auto Autonomous Driving |
| Haotong Lin | Zhejiang University | https://haotongl.github.io/ | co-first author (equal contribution); PhD student at ZJU |
| Jiawei Wang | Zhejiang University | — | co-first author (equal contribution) |
| Jiaxin Li | Zhejiang University | — | co-author |
| Yida Wang | Li Auto | — | co-author |
| Xueyang Zhang | Li Auto | — | co-author |
| Yue Wang | Zhejiang University | — | co-author |
| Xiaowei Zhou | Zhejiang University | https://xzhou.me/ | co-author; senior advisor (3D Vision Group, ZJU) |
| Ruizhen Hu | Shenzhen University | — | co-author |
| Sida Peng | Zhejiang University | https://pengsida.net/ | corresponding author; tenure-track Assistant Professor at ZJU (3D Vision Group, School of Software Technology) |

### 1.2 Keywords

monocular depth estimation, neural implicit fields, arbitrary-resolution depth, fine-grained geometry, multi-scale local implicit decoder, novel view synthesis, Synth4K benchmark, metric depth completion

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| DPT (Ranftl et al., 2021) | predecessor | 提供 ViT + reassemble block 的多尺度特徵金字塔解碼架構，本文沿用其 reassemble 設計並將其輸出送入 implicit decoder。 |
| DINOv3 (Oquab/Siméoni et al., 2025) | base model | 採用 DINOv3 ViT-Large 作為影像編碼器，從 layer 4/11/23 抽取多尺度特徵 token。 |
| LIIF (Chen et al., CVPR 2021) | influence | 提供「以隱式函數學習連續 2D 影像表徵」的核心啟發，本文將其延伸至深度場以支援任意解析度查詢。 |
| DepthAnything / DepthAnythingV2 (Yang et al.) | baseline | 主要的相對深度估計強基線；在 KITTI/ETH3D/NYUv2/ScanNet/DIODE 與 Synth4K 上正面比較。 |
| MoGe / MoGe-2 (Wang et al.) | baseline | 以 affine-invariant point map 為訓練監督的 SOTA 相對深度方法，是 Synth4K 上的最強對手。 |
| PromptDA (Lin et al., CVPR 2025) | predecessor | metric depth 設定下的直接前作；本文沿用其 depth prompt 模組並將其應用於 implicit field 來做 metric 估計。 |
| ADGaussian (Liu et al.) | influence | 前饋式 NVS 方法，預測 pixel-aligned depth 與 Gaussian；本文用其作為 NVS 應用比較對象，凸顯 Infinite Depth Query 在大視角偏移下的優勢。 |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於單目深度估計（Monocular Depth Estimation, MDE），特別處理「任意輸出解析度」與「細粒度幾何細節」這兩個現有方法難以兼顧的目標。傳統與主流方法皆將深度表示為離散二維網格，受限於訓練影像尺寸，且需依賴卷積上採樣或 latent-to-patch 線性投影輸出深度，導致高頻細節遭平滑或無法捕捉局部幾何變化。作者提出 InfiniDepth，將深度建模為以連續 2D 座標為輸入的 neural implicit field：以 ViT 編碼影像、透過 reassemble block 建立多尺度特徵金字塔，再對任意座標做局部 bilinear 特徵取樣並以階層式 gated fusion 融合後送入 MLP head 預測深度。此表徵原生支援 4K/8K/16K 等任意解析度查詢與細節還原。論文同時涵蓋 relative 與 metric（結合 sparse depth prompt）兩種設定，並提出 Infinite Depth Query 把子像素查詢預算按 3D 表面元素加權分配，產生表面密度均勻的點雲以提升大視角偏移下的 novel view synthesis 品質。為突破現有 benchmark 解析度過低的限制，作者另建構 Synth4K 4K 合成基準與高頻 mask 來精準量測細節預測能力。

### 2.2 Domain Tags

- computer vision
- monocular depth estimation
- 3D reconstruction
- implicit neural representations
- novel view synthesis

### 2.3 Core Architectures Used

- **Neural Implicit Field for Depth (本文提出)**：將深度建模為 $d_I(x, y) = N_\theta(I, (x, y))$，以 MLP 參數化的隱式函數，讓輸出解析度與訓練解析度解耦，支援任意連續 2D 座標查詢（§3.1，page 3）。
- **Multi-Scale Local Implicit Decoder (本文提出)**：本文核心解碼器，由 Feature Query 與 Depth Decoding 兩模組組成，對任一連續座標在多尺度特徵金字塔上做 bilinear 取樣並階層式 gated fusion，最後以 MLP head 解碼深度（§3.2，Fig. 2，page 3）。
- **Residual Gated Fusion Block (本文提出)**：以可學習 channel-wise gate $g_k \in (0,1)^{C_{k+1}}$ 將淺層細節特徵 residual 注入深層語意特徵，由 high-resolution 到 low-resolution 階層融合，定義於 Eq. 3（page 4）。
- **Infinite Depth Query (本文提出)**：依 $w(x, y) = d_I(x, y)^2 / (|n(x, y) \cdot v(x, y)| + \varepsilon)$ 對應的 3D 表面元素 $\Delta S$ 加權分配子像素查詢預算，產生表面密度均勻的點雲（§3.3，Eq. 5，page 4）。
- **DINOv3 ViT-Large (沿用)**：作為影像編碼器，從 layer 4/11/23 抽取特徵 token，並分別投影至 hidden dim 256/512/1024（§3.4，page 5）。
- **DPT-style Reassemble Block (沿用自 [29])**：將不同 ViT 層的 token 重新組裝並上採樣（layer 4/11 分別 ×4/×2 上採樣）以建立多尺度特徵金字塔 $\{f^k\}_{k=1}^L$（§3.2，page 3；§3.4，page 5）。
- **Depth Prompt Module (沿用自 PromptDA [22])**：在 metric depth 設定下注入 sparse depth 輸入，組成 Ours-Metric 變體（§4.2，page 5）。
- **Gaussian Splatting Head (應用層)**：在 NVS 應用中接於深度模型之後，以 Infinite Depth Query 產生的均勻 3D 點作為 Gaussian centers 並預測 Gaussian 屬性（§4.5，page 8）。

### 2.4 Core Argument

作者主張：現有單目深度估計方法之所以同時受限於輸出解析度與細節保真度，根本原因不在編碼器或損失函數，而是「以離散 2D 網格表示深度」這個表徵選擇本身。網格化將深度輸出鎖定在訓練影像尺寸與固定像素位置，且必須透過卷積上採樣（造成平滑、模糊邊界）或 latent-to-patch 的線性投影（無法捕捉局部幾何變化）才能恢復逐像素深度，兩條路徑都會在物體邊界、薄結構與高頻區域系統性犧牲幾何細節。換言之，僅僅擴大網路或改良解碼頭只是在錯誤的表徵上做局部優化，無法繞過離散網格的內在限制。基於此診斷，作者主張深度應改以 neural implicit field 表徵——將深度視為輸入影像條件下、對連續 2D 座標 $(x, y)$ 的隱式函數 $N_\theta(I, (x, y))$——使輸出解析度與訓練解析度解耦，原生支援任意尺度查詢，且能以較少參數刻畫精細幾何。為將此抽象表徵落地，作者設計 multi-scale local implicit decoder：用 ViT 加 reassemble block 建構特徵金字塔，對任一連續座標在每個尺度以 bilinear 取樣局部鄰域特徵，再以 residual gated fusion 由淺（細節）到深（語意）層次化融合，最後 MLP head 解碼深度；此設計兼顧局部細節與全域語意，並能在查詢解析度遠高於訓練解析度時仍保持幾何一致性。進一步地，因隱式深度場對影像座標可微，作者用 autograd 求得法線，並依「深度平方 × 法線與視線夾角倒數」對應的 3D 表面元素 $\Delta S$ 反推每像素的 sub-pixel 查詢預算（Infinite Depth Query），生成表面密度均勻的點雲，使下游大視角 NVS 顯著減少破洞與失真。整體論證鏈條從「離散網格為何必然失敗」一路推導到「為何隱式場是必要解」與「為何同一隱式場可同時改善 relative/metric depth 與 NVS」，每一步替代方案皆被表徵層級的限制所排除，因此其解決方案在邏輯上是必要而非任意的。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(110 words)

標題「InfiniDepth: Arbitrary-Resolution and Fine-Grained Depth Estimation with Neural Implicit Fields」一次點出三個核心訴求：任意解析度、細粒度幾何、以及以 neural implicit fields 作為 depth 的承載形式。標題避免使用 monocular 一詞，但圖 1 與摘要立刻補上單張影像輸入的設定，並把賣點分成三格：(a) 任意解析度 depth maps、(b) fine-grained point clouds、(c) novel view synthesis 應用。這個三格圖是整篇論文的索引，後文每一節都會回扣其中之一。

摘要的論證鏈非常緊湊。第一句即點出問題本質：既有方法被「discrete image grids」這個 representation 綁住，因此 resolution 無法 scale、geometric detail 也難以還原。第二句提出 representation 層級的解法：把 depth 寫成 neural implicit fields，並以「a simple yet effective local implicit decoder」在連續 2D 座標 $(x, y)$ 上 query depth。第三句宣告為了驗證這個能力，作者另外 curate 了一個 4K synthetic benchmark Synth4K，涵蓋五款遊戲。最後兩句把貢獻收斂到：在 relative 與 metric depth estimation 上達到 SOTA、在 fine-detail 區域特別強、並回頭支撐圖 1(c) 的 NVS 應用。

摘要這樣鋪陳是為了把「representation 換掉」這件事推到 thesis 的中心位置——而不是把貢獻包裝成新的 decoder 或新的訓練 trick。它同時為 §1 Introduction 預留兩條延伸線：一條是要展開 grid representation 的具體缺陷與本方法的對應設計；另一條是要說明為什麼 NVS 能受益、以及為何需要新的 4K benchmark 才能凸顯這些好處。

### 3.2 Introduction

(630 words)

Introduction 採取「representation diagnosis → representation rewrite → downstream payoff → benchmark gap」四段式結構。第一段先把 monocular depth estimation 放回應用脈絡（autonomous driving、robotics），快速帶過 CRF-based 的傳統方法只是為了凸顯 deep learning 主流路線。第二段是論證的核心：作者把現有 ViT + 2D grid 的方法歸納為「regular 2D grids 表示 depth」這一類，然後指出兩個 grid 帶來的根本限制——(1) 訓練解析度即上限、(2) 從 latent 投影到 depth patches 時，convolutional upsampling 會 over-smooth、linear projection 又抓不到 local geometric variation。這段把所有失敗模式都歸因於 representation 而非 decoder，為後文「換 representation」鋪好邏輯坡道。

第三段正式提出 InfiniDepth。作者刻意先描述高層 pipeline——ViT encode → reassemble block 建 feature pyramid → 對任意連續座標 $(x, y)$ 在 local window 內聚合 multi-scale features → lightweight MLP 預測 depth——再說明這個 continuous and localized prediction paradigm 為何同時解掉前述兩個限制：因為 query 與 grid 解耦，模型不再被 training resolution 綁住；因為預測是 localized，反而能 capture geometric variations，於是圖 1(a)(b) 的 arbitrary-resolution depth 與 fine-grained point cloud 都成立。

第四段把故事延伸到 NVS。作者點明 feed-forward NVS 方法（如 ADGaussian、DepthSplat）會 unproject pixel-aligned depth，得到的 surface point cloud 因 perspective projection 與 surface orientation 出現 density imbalance，於是大視角位移時會破洞、出 artifact。作者的回應是 depth query strategy：依每個 pixel 對應的 3D surface element 比例分配 sub-pixel query budget，產生 spatially uniform 的 3D 點。這段是 §3.3 Infinite Depth Query 的精簡預告，也用來解釋為什麼 NVS 能成為一個 application 而不是 forced fit——因為 implicit field 的「可在任意座標 query」本來就是 sub-pixel sampling 所需。

第五段處理 evaluation 的方法論問題。作者先指出既有 real-world benchmark 的 GT depth 解析度低且稀疏，難以測 fine-grained 能力，因此需要 Synth4K：來自五款遊戲、4K GT depth、並透過 multi-scale Laplacian energy 建立 high-frequency mask 以針對 detail region 做 targeted evaluation。這段把 benchmark 從「實作細節」抬升為一條獨立貢獻線。

最後一段以三點 contributions 收束：representation、depth query strategy、Synth4K，正好對應前述四段的三條主線（depth estimation、NVS、benchmark）。整段 Introduction 的功能是把摘要裡濃縮的「representation 是病灶」展開成一條可驗證的路徑：representation 換成 implicit field → multi-scale local query 是必要的具體實作 → query 機制本身又解鎖 sub-pixel sampling 與 NVS 應用 → 既有 benchmark 不足以驗證 → 因此提出 Synth4K 與 HF mask。這個鋪排為 §2 Related Work（區分 relative / metric / INR 三脈）與 §3 Method（先寫 representation、再寫 decoder、再寫 query strategy）建立直接的章節對應。

### 3.3 Related Work / Preliminaries

(380 words)

Related Work 沒有獨立的 Preliminaries 子節，但 §3.1「Representing Depth as Neural Implicit Fields」事實上扮演 representation 的形式化前置——它將 implicit field 的一般式 $y = F_\theta(x)$ 改寫為 depth-specific 形式 $d_I(x, y) = N_\theta(I, (x, y))$，作為後續 decoder 設計的數學支點。

Related Work 切成三個段落，並非平均介紹所有 baselines，而是用來把「為什麼換 representation 是合理的下一步」這件事三方夾擊。第一段 Relative Depth Estimation 把近年 ViT + convolutional decoder 路線的代表（DepthAnything、MoGe、Marigold、PPD）並列，承認它們在 generalization、affine-invariant geometry、diffusion prior、boundary refinement 等面向各有強處，但統一收束在同一個診斷上：「all these methods represent depth as discrete 2D grids, limiting resolution scalability and fine detail recovery」。這句是整個段落的論證錨——它讓所有 baselines 不是被否定，而是被歸類到「representation 受限」的同一族群，從而留出 InfiniDepth 的差異化空間。

第二段 Metric Depth Estimation 處理另一個側面：sparse depth input 的補強路線，包括 PriorDA、Omni-DC、Marigold-DC、PromptDA。這段的功能不是批評既有方法，而是替後文 Ours-Metric 鋪路——作者要說明 InfiniDepth 在 metric setting 下，可以用同一個 prompt module（[22]）拼上 sparse depth 並超越現有方法，因此有必要先把這條路線畫清楚，並指出「fine-grained geometry recovery remains challenging」做為自己的切入縫隙。

第三段 Implicit Neural Representations 是論文 thesis 的譜系背景。作者快速串起 NeRF、PiFU、LIIF、AnyFlow、DeFiNe 五個關鍵節點：NeRF 與 PiFU 確立 INR 在 3D 與 pixel-aligned 領域的可行性；LIIF 與 AnyFlow 把 INR 推到 2D 連續訊號（image、optical flow）；DeFiNe 嘗試用 implicit 表示 multi-view scene，但「architectural constraints limit it to low-resolution outputs」——這正是作者要克服的具體障礙。透過這一段，作者把 InfiniDepth 不是定位成「另一個 depth estimator」，而是「INR 路線在 monocular depth 上的首個 arbitrary-resolution 落地」，與第一段的 grid-based 診斷形成對照，並順勢過渡到 §3 的 method 設計。

### 3.4 Method (overview narrative)

(680 words)

§3 Method 從最高層的 problem statement 起手：給定單張 RGB image，目標是對影像平面上「任意連續 2D 座標」估測 depth。作者刻意把問題改寫成連續形式，而不是慣用的「估一張 $H \times W$ depth map」，這個改寫本身就是論文的論點預告——把任務從 grid prediction 改寫為 functional approximation。

§3.1 Representing Depth as Neural Implicit Fields 提供 representation 的形式化基礎。先列出 INR 通式 $y = F_\theta(x)$，再轉寫為 depth specific 的 $d_I(x, y) = N_\theta(I, (x, y))$，其中 $(x, y) \in [0, W] \times [0, H]$、$I \in \mathbb{R}^{H \times W \times 3}$。這個形式化的關鍵價值不在數學新意，而在它把後續所有設計（multi-scale query、sub-pixel sampling、normal via autograd、Infinite Depth Query）統一在同一個 functional form 下——所有東西都是 $N_\theta$ 的不同 querying / supervision 行為。

§3.2 Multi-Scale Local Implicit Decoder 是把 $N_\theta$ 落實成具體網路的章節，分成 Feature Query 與 Depth Decoding 兩個模組。Feature Query 解釋如何從 ViT encoder 抽取多層 tokens、透過 reassemble block 投影成不同 hidden dimension，並把 shallow-layer features 上採樣形成 feature pyramid $\{f^k\}_{k=1}^L$；對任意連續座標 $(x, y)$，先映射到第 $k$ 層的 $(x_k, y_k)$，再以該位置周圍 $2 \times 2$ grid neighborhood 做 bilinear interpolation 得到 $f^k_{(x, y)} \in \mathbb{R}^{1 \times C_k}$。Depth Decoding 則描述如何 hierarchically fuse 這些 multi-scale local descriptors：以 residual gated fusion block 從 shallow 往 deep 融合，learnable channel-wise gate $g_k$ 控制各通道融合強度，最後對 $h_L$ 過 MLP head 得到 $d_I(x, y)$。這個設計的敘事重點是「shallow-to-deep」的順序——它讓 fine-grained detail 先進入、global semantics 後進入，與一般 DPT-style decoder 的 coarse-to-fine 形成對比。

§3.3 Infinite Depth Query 是 method 的第二條主線，把 implicit representation 的可微性與可任意 query 的特性兌現為 NVS 的具體收益。作者點出 per-pixel depth unprojection 的兩個 density imbalance 來源：depth-squared scaling（pixel 對應的 surface area 隨 $d^2$ 成長）與 surface orientation effect（normal 偏離 viewing direction 時 projected area 被壓縮）。對應的解法是 adaptive weight $w(x, y) = d_I(x, y)^2 / (|n(x, y) \cdot v(x, y)| + \varepsilon)$，並用該 weight 在每個 pixel 內分配 sub-pixel query budget。值得注意的是 $n(x, y)$ 不需要額外網路，而是從 $X(x, y)$ 對影像座標的 Jacobian 透過 autograd 算出——圖 4 用這個 normal map 做 sanity check，證明 implicit field 內部幾何品質足以支撐這個策略。

§3.4 Implementation Details 收束在 architecture 與 training 層級的選擇：encoder 是 DINOv3 ViT-Large、抽取 layer 4/11/23、hidden dimensions 256/512/1024、shallow 兩層分別上採 4×、2×；訓練資料是 Hypersim、VKITTI、TartanAir、IRS、UnrealStereo4K、UrbanSyn 等純 synthetic（理由是 real-world depth 噪聲與不完整不利於 fine-grained supervision）；loss 是在隨機抽取的 $N$ 個座標上計算 $l_1$；optimizer 為 AdamW、learning rate $1 \times 10^{-5}$、800k steps、8 GPU、batch 4/GPU。這個結尾的功能是把前面 representation-level 的論點 grounded 在可重現的訓練配方，並為 §4 Experiments 提供「同 encoder、同資料」的 ablation 可比性基準。

### 3.5 Experiments (overview narrative)

(810 words)

§4 Experiments 採取「先講 benchmark → 再講 setup → 再對 SOTA → 最後 ablation 與 application」的鋪排，這個順序本身傳達一個訊息：作者認為 evaluation 的設計與方法的設計同等重要。

§4.1 Synth4K 是整章的方法論前提。作者先解釋為何不能只靠 KITTI、ETH3D、NYUv2、ScanNet、DIODE 這類 real-world benchmark：它們的 GT depth 普遍 low-resolution、sparse、缺乏 edge 與 high-frequency structure 的覆蓋，因此 fine-grained capability 會被 evaluation 的 ceiling 蓋住。Synth4K 由五款遊戲（Synth4K-1 ∼ Synth4K-5，對應 CyberPunk 2077、Marvel’s Spider-Man 2、Miles Morales、Dead Island、Watch Dogs）組成、每集數百張 4K image-depth pair、並透過 multi-scale Laplacian energy 建立 high-frequency mask 以鎖定 detail region。這個 benchmark 設計直接呼應 §1 的論點：要凸顯 representation 帶來的 fine-grained 優勢，必須先有能解析這個維度的 evaluation。

§4.2 Experimental Setup 把評測分成 relative 與 metric 兩條軸線。Relative 採用 $\delta_1$（real-world）與 $\delta_{0.5}, \delta_1, \delta_2$（Synth4K 全圖與 HF region），定義為 $\max(d/d^*, d^*/d) < 1.25^t$ 的 pixel 比例。Metric 透過嵌入 PromptDA 的 depth prompt module（標記為 Ours-Metric）接受 sparse depth input，並改用更嚴格的 $\delta_{0.01}, \delta_{0.02}, \delta_{0.04}$ thresholds，理由是 sparse depth 已大幅減少 ambiguity，需要更嚴的尺度才能拉開差距。這段解釋了為何同一個方法在兩條軸上會用不同的 metric，避免讀者誤以為作者在挑指標。

§4.3 Comparisons with the State of the Art 對應四張主表。Relative baselines 包含 DepthAnything、DepthAnythingV2、DepthPro、MoGe、MoGe-2、Marigold、PPD，輸出皆對 GT 做 scale-and-shift alignment。Metric baselines 為 Marigold-DC、Omni-DC、PriorDA、PromptDA，所有方法吃同一組 sparse depth samples 與相同輸入解析度。Synth4K 上 baseline 輸出被 bilinear 上採到 4K，而 InfiniDepth 直接在 4K 連續座標 query。結論是：Synth4K 上全面領先（Table 1、Table 2），HF region 的領先幅度尤其顯著；real-world 上 Ours 與目前 SOTA 持平（Table 3），Ours-Metric 全面超越（Table 4，例如 ETH3D $\delta_{0.01}$ 96.7 對 PromptDA 92.8）。圖 5 與圖 6 提供 depth map 與 point cloud 的 qualitative 對照。

§4.4 Ablations and Analysis 切成三個對照。第一個是 representation：相同 encoder（DINOv3 ViT-Large）與相同訓練資料（Hypersim）下，把 implicit field 換成 DPT decoder 的 grid representation。Table 5 顯示 metric setting 下差距明顯（例如 KITTI $\delta_{0.01}$ 從 49.0 提升到 61.7），relative setting 下定量改善 moderate，但圖 7 顯示 fine-detail 區域的視覺品質仍有顯著提升；作者解釋這個落差是因為 relative depth 本身高度 ambiguous，定量指標容易飽和。第二個是 multi-scale feature query：把 multi-scale 換成只取 ViT 最末層 single-scale feature，效能在所有資料集都明顯下降。第三個是 image encoder：DINOv3 對 DINOv2 的對照，數字也支持 DINOv3 的選擇。

§4.5 Application: Single-View Novel View Synthesis 作為章末的 capstone，把方法的 representation-level 優勢延伸到下游任務。作者在 InfiniDepth 上接一個 lightweight Gaussian Splatting head，在 inference 階段先用 §3.3 的 depth query strategy 產生 surface-uniform 的 3D points 作為 Gaussian centers，再由 GS head 預測 Gaussian attributes。圖 1(c) 與圖 8 顯示 ADGaussian 因 pixel-aligned depth 在大視角位移下出現明顯破洞與 artifact，而 InfiniDepth 的結果更完整、穩定。這個 application 不只是收尾，更是回頭驗證 §3.3 設計的必要性：sub-pixel uniform sampling 不是炫技，而是 NVS 在大視角位移下品質的關鍵差異。

### 3.6 Conclusion / Limitations / Future Work

(120 words)

§5 Conclusion and Discussions 以三層收束整篇論文。第一層是 representation-level 結論：把 depth 寫成 neural implicit fields 這件事，能在任意連續 2D 座標上估深度，並在過程中保住 fine-grained geometric details。這句話是整篇文章最核心的 thesis 重述，刻意避免提及具體 architecture——意在強調貢獻屬於 representation 而非某個 decoder trick。第二層是 evidence-level 結論：在 Synth4K 與 real-world benchmarks 上、跨 relative 與 metric 兩個任務、皆驗證了 accuracy 與 detail recovery 的提升。第三層是 application-level 結論：搭配 depth query strategy 後，single-view NVS 在大視角位移下的品質也跟著提升。這個三層收束與 §1 的三點 contributions（representation、query strategy、Synth4K）完全對齊，使全文形成 closed loop。

Limitations and Future Work 段落點明一個明確邊界：本工作只在 single-view depth data 上訓練，未對 video 引入 temporal consistency 約束，套到 video 時可能 frame 之間 flicker。對應的 future work 是把 representation 擴展到 multi-view setting 以強化 temporal stability 與 3D consistency。最後作者把期望寫進 closing line：希望 InfiniDepth 能啟發 high-resolution、fine-grained depth estimation 的後續研究，並被整合到更廣的 3D perception 與 reconstruction pipeline。整段 limitation 的處理克制——只承認一個明確且具體的弱點，不替論文 oversell 也不過度防守，與全文「以 representation 為中心」的論證風格一致。

## 4. Critical Profile

### 4.1 Highlights

- 將 monocular depth 從「離散 2D 網格」整體重塑為 neural implicit field $d_I(x, y) = N_\theta(I, (x, y))$，原生支援任意連續座標查詢與 4K/8K/16K 解析度輸出（Sec. 3.1，Fig. 1a）。
- 在 Synth4K 全 5 個子集的 zero-shot relative depth 全圖評估中於 $\delta_{0.5}/\delta_1/\delta_2$ 全部三項皆奪冠，例如 Synth4K-3 的 $\delta_1$ 達 93.9（次佳 88.6），領先幅度顯著（Table 1）。
- 在 Synth4K 高頻 (HF) 細節 mask 區域同樣全面領先，例如 Synth4K-3 $\delta_1$ 為 69.0（次佳 63.4），驗證細粒度幾何優勢（Table 1）。
- Metric depth 設定下接上 PromptDA 的 sparse depth prompt 模組後，Synth4K-1 $\delta_{0.01}$ 自 PromptDA 的 65.0 提升至 78.0，real-world DIODE $\delta_{0.01}$ 自 97.3 提升至 98.4（Tables 2, 4）。
- Decoder 僅 15M 參數，是與比較的 fine-grained 系列（DepthPro 29M、DepthAnythingV2 31M、MoGe-2 22M）中最輕量者（Table 6）。
- 利用 implicit field 對影像座標可微的特性，以 autograd 自 $\partial_x X \times \partial_y X$ 計算 surface normal，無需額外 normal head（Eq. 6，Fig. 4）。
- 提出 Infinite Depth Query，依 $\Delta S \propto d_I^2 / |n \cdot v|$ 為每像素分配 sub-pixel 查詢預算，產生表面密度均勻的 3D 點雲，在大視角偏移 NVS 中明顯減少破洞（Sec. 3.3，Fig. 1c, Fig. 8）。
- 建構 Synth4K：來自五款遊戲、4K 解析度的 RGB-D zero-shot 基準，並透過 multi-scale Laplacian energy 構造 HF mask 以針對細節區域評估（Sec. 4.1，Fig. 9）。
- Ablation 顯示拿掉 implicit field（改回 DPT 解碼器）會在 metric depth 全面退化，例如 Synth4K-1 $\delta_{0.01}$ 自 72.7 掉到 62.4、KITTI 自 61.7 掉到 49.0（Table 5）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 本工作只在單視角資料訓練，未顯式建模 temporal consistency，套用到影片時可能出現跨幀 flickering；作者列為 future work 將擴展至 multi-view 設定（Sec. 5 "Limitations and Future Work"，page 9）。

#### 4.2.2 Phyra-inferred

- 標榜的 SOTA 在 real-world relative benchmark 上其實落後 MoGe-2：KITTI 97.9 vs 98.3、NYUv2 97.6 vs 98.2、ScanNet 97.3 vs 98.4、五個資料集中僅 ETH3D 領先（Table 3），與摘要「state-of-the-art performance on … real-world benchmarks」的措辭存在落差，作者以「relative depth ambiguity 致指標飽和」帶過，但這同時意味 implicit field 的優勢可能集中於 synthetic 細節區域而非通用 real-world 場景（Sec. 4.4）。
- Synth4K 為作者自建基準且採自遊戲渲染，與訓練集 UnrealStereo4K、Hypersim、UrbanSyn 等同屬合成域，存在 in-domain favoring 風險；論文未提供 Synth4K 與訓練集間的領域距離量化或留一遊戲交叉驗證，難以排除 Table 1/2 的領先部分來自分布相似而非表徵優勢。
- 推論延遲 0.16 s/it 為 DepthAnythingV2（0.03）與 MoGe-2（0.05）的 3-5 倍（Table 6），且此數據僅針對 504×672 解析度的 depth 推論本身，未計入 Infinite Depth Query 為了求 surface normal 而執行的 autograd 反向圖建構成本，實際 4K/NVS pipeline 的延遲被低估。
- 「w/o Neural Implicit Fields」ablation 同時改變了「表徵（grid vs. implicit）」與「監督方式（pixel-wise vs. sub-pixel）」；Table 7 顯示僅換成 pixel-wise supervision 即可讓 Synth4K-1 $\delta_{0.01}$ 自 72.7 掉至 70.0，意味著 Table 5 中歸因於 implicit field 的部分增益實際可能來自 sub-pixel 監督，兩變因未被分離。
- Infinite Depth Query 僅以 qualitative 圖（Fig. 8, 13）對 ADGaussian 比較 NVS，正文與 supp. 都未報告 PSNR/SSIM/LPIPS 等量化指標；此設計被列為三大貢獻之一卻無數值證據，「fewer holes and artifacts」的宣稱不可獨立驗證。
- Fig. 1(a) 展示 16K 深度圖且摘要強調 arbitrary-resolution，但所有 quantitative 評估上限為 4K（Synth4K），8K/16K 的「能跑」與「跑得對」缺乏 ground truth 支撐，超解析度宣稱僅能視為視覺存在性而非精度保證。
- 訓練資料完全是 synthetic（作者明言為避免 real depth 的雜訊），此選擇雖合理卻可能解釋為何 real-world 數值不領先，且論文未做 synthetic-only vs. mixed 訓練的對照，使「網格才是瓶頸」之論點少了一個必要對照。

### 4.3 Phyra's Judgment (summary)

InfiniDepth 真正新的東西是**「以 local implicit field 取代 grid 表徵」這個視角切換**，並把它與 LIIF 風格的 multi-scale bilinear feature query、residual gated fusion 等小幅改進綁在一起；其餘大部分（DPT reassemble、DINOv3 backbone、PromptDA prompt 模組）皆為既有元件的工程整合。論文最強的證據來自合成 4K 與 metric+sparse depth 兩個設定，但在 real-world relative 上只與 MoGe-2 持平偏弱，因此「離散網格是根本瓶頸」這個宏大論點仍未在通用域被嚴格證成。Infinite Depth Query 是有趣的副產物，但缺乏量化 NVS 指標，目前比較像是 implicit field 可微性的展示而非獨立貢獻。

## 5. Methodology Deep Dive

### 5.1 Method Overview

InfiniDepth 把單目深度估計重新定式化為一個 conditional implicit field：給定 RGB 影像 $I \in \mathbb{R}^{H \times W \times 3}$ 與任意連續 2D 座標 $(x, y) \in [0, W] \times [0, H]$，目標為直接輸出深度值 $d_I(x, y) = \mathcal{N}_\theta(I, (x, y))$（Eq. 2，p. 3）。此設計把輸出解析度從 image grid 解耦，使同一模型可在訓練解析度以外進行任意尺度查詢，且能透過 autograd 對影像座標求導以解析法線。

整個 pipeline 由兩個主要階段組成（Fig. 2，p. 3）：第一階段 **Feature Query**，以 ViT 編碼器抽取多層特徵 token，經 reassemble block 構築多尺度特徵金字塔 $\{f^k\}_{k=1}^L$（淺層上採樣以保留高頻細節、深層維持原解析度以保留語意），再對每個尺度以 bilinear interpolation 從局部 $2 \times 2$ 鄰域取樣得到該座標的局部特徵 $f^k_{(x,y)}$。第二階段 **Depth Decoding**，將多尺度特徵以 residual gated fusion 從淺到深階層式融合（Eq. 3，p. 4），最後以 MLP head 解碼為單一深度標量。

訓練時模型不需在整張深度圖上回歸，而是隨機抽取 $N=100\text{k}$ 個 $(x_i, y_i, d_i)$ 配對並計算 $\ell_1$ 損失（Eq. 7，p. 5；supp. A.4），這也是「以隱式場表徵深度」帶來的關鍵彈性。在 metric depth 設定下，模型搭配來自 PromptDA [22] 的 depth prompt 模組以注入稀疏深度先驗，稱為 Ours-Metric。第三階段 **Infinite Depth Query**（Sec. 3.3）以可微分的 implicit field 計算每像素對應 3D 表面元素 $\Delta S$，依此分配 sub-pixel 查詢預算以產生表面密度均勻的點雲，供下游 NVS 任務使用。

### 5.2 Pipeline Diagram with Tensor Shapes

下圖以 ViT-L/p（patch size $p$ 在論文與補充材料皆未指明，標註為 `?`）為基準描繪單張影像、$N$ 個查詢座標的前向流程。所有非 batch 維度均依照論文與補充材料 §A.1 的明確數值；無法從文字推斷者標 `?` 並於 §5.3 對應模組的 Implementation Details 中註明。

```
Input
  ├─ Image I            : [B, 3, H, W]
  └─ Query coords (x,y) : [B, N, 2]            (N = 100k during training; N = H·W or higher at inference)

  ▼
ViT-L Encoder (DINOv3 [34])
  full token sequence    : [B, T, 1024]         (T = H_t · W_t; H_t = H/p, W_t = W/p; p not specified)
  │
  ├─ extract layer  4    : [B, T, 1024]   ──┐
  ├─ extract layer 11    : [B, T, 1024]     │  (3 selected encoder layers)
  └─ extract layer 23    : [B, T, 1024]   ──┘
                                            │
                                            ▼
Reassemble Block (per-scale: project → reshape → upsample)
  f^1 (shallow, layer  4): [B,  256, 4·H_t, 4·W_t]   (project 1024→256, upsample ×4)
  f^2 (mid,     layer 11): [B,  512, 2·H_t, 2·W_t]   (project 1024→512, upsample ×2)
  f^3 (deep,    layer 23): [B, 1024,   H_t,   W_t]   (project 1024→1024, native resolution)
                                            │
                                            ▼
Per-coordinate scale mapping
  for each scale k: (x_k, y_k) = (x · w_k / W, y · h_k / H)
                                            │
                                            ▼
Bilinear Feature Interpolation on local 2×2 neighborhood N_k(x_k, y_k)
  f^1_{(x,y)} : [B, N,  256]
  f^2_{(x,y)} : [B, N,  512]
  f^3_{(x,y)} : [B, N, 1024]
                                            │
                                            ▼
Hierarchical Residual Gated Fusion (Eq. 3, p. 4)
  h_1 := f^1_{(x,y)}                                     : [B, N,  256]
  h_2  = FFN_1( f^2_{(x,y)} + g_1 ⊙ Linear_1(h_1) )      : [B, N,  512]
  h_3  = FFN_2( f^3_{(x,y)} + g_2 ⊙ Linear_2(h_2) )      : [B, N, 1024]
   (Linear_k: C_k → C_{k+1};  g_k ∈ (0,1)^{C_{k+1}} learnable channel gate; FFN_k: dim×4 → dim, ELU/ReLU)
                                            │
                                            ▼
MLP Head (3 linear layers, ReLU; final ELU)
  in 1024 → hidden 256 → hidden 256 → out 1
                                            │
                                            ▼
Output
  d_I(x, y)              : [B, N, 1]

────── (optional, only for NVS application; Sec. 3.3) ──────

Infinite Depth Query (per pixel (u, v))
  back-project to 3D     : X(u, v) ∈ R^3
  surface normal via autograd:
    n(u, v) = (∂_x X × ∂_y X) / ‖∂_x X × ∂_y X‖   (Eq. 6)
  adaptive weight:
    w(u, v) = d_I(u, v)^2 / ( |n(u, v) · v(u, v)| + ε )   (Eq. 5)
  CDF-based stratified inverse-transform sampling →
  sub-pixel coords (x, y) with jitter δu, δv ∼ U(-0.5, 0.5)   (supp. A.2)
  re-query d_I(x, y) → uniformly distributed 3D point cloud
```

### 5.3 Per-Module Breakdown

#### 5.3.1 ViT Image Encoder (DINOv3 ViT-Large)

**Function:** 將輸入影像編碼為多層 token 序列，作為後續 reassemble 與 implicit query 的特徵來源。

**Input:**
- Name: `I`
- Shape: `[B, 3, H, W]`
- Source: input RGB image

**Output:**
- Name: 三層 token 序列 `tokens_4, tokens_11, tokens_23`
- Shape: 各為 `[B, T, 1024]`，其中 $T = H_t \cdot W_t$
- Consumer: Reassemble Block

**Processing:**

ViT-L 將影像切為 patch 後通過 24 層 transformer block；論文僅取 layer 4、11、23 的輸出（對應淺、中、深三個語意/解析度層級，p. 5）。Layer 4 提供細節與紋理、layer 11 為中層結構、layer 23 為全域語意。token 數 $T$ 由 patch size $p$ 與輸入 $H, W$ 決定。

**Key Formulas:**

$$\text{tokens}_\ell = \text{ViT-L}_\ell(I), \quad \ell \in \{4, 11, 23\}$$

**Implementation Details:**

採用 DINOv3 [34] 的 ViT-Large 預訓練權重；論文 §3.4 與 supp. A.1 均未明示 patch size $p$，故 `T` 與 token 空間網格 $H_t \times W_t$ 標為 `?`。Encoder 在訓練 InfiniDepth 期間是否凍結未明確說明（在 GS head 訓練時則凍結，supp. A.4）。

#### 5.3.2 Reassemble Block

**Function:** 把不同深度層的 ViT token 投影到不同 hidden 維度並上採樣到不同空間解析度，構築由細到粗的特徵金字塔。

**Input:**
- Name: `tokens_4, tokens_11, tokens_23`
- Shape: 各為 `[B, T, 1024]`
- Source: ViT Image Encoder

**Output:**
- Name: 特徵金字塔 $\{f^1, f^2, f^3\}$
- Shape:
  - `f^1`: `[B, 256, 4·H_t, 4·W_t]`
  - `f^2`: `[B, 512, 2·H_t, 2·W_t]`
  - `f^3`: `[B, 1024, H_t, W_t]`
- Consumer: Feature Query

**Processing:**

1. 將每層 token 序列 reshape 回 2D 空間網格 $[B, 1024, H_t, W_t]$；
2. 線性投影到 hidden dim：layer 4 → 256、layer 11 → 512、layer 23 → 1024（p. 5）；
3. 對淺層做空間上採樣：layer 4 上採 ×4、layer 11 上採 ×2、layer 23 維持原解析度（Sec. 3.2，Sec. 3.4）。設計沿用 DPT [29] 的 reassemble 架構。

**Key Formulas:**

$$f^k \in \mathbb{R}^{h_k \times w_k \times C_k}, \quad (C_1, C_2, C_3) = (256, 512, 1024)$$

**Implementation Details:**

論文未指定上採樣方式（如 transposed convolution、bilinear、PixelShuffle 等），亦未說明 reassemble 內部是否包含 normalization 或 activation；詳細模組結構需參考 DPT [29] 設計，但本論文僅在 §3.2 文字交代「project to different hidden dimensions」與上採樣倍率。

#### 5.3.3 Feature Query (Bilinear Interpolation at Continuous Coordinate)

**Function:** 對任一連續 2D 影像座標 $(x, y)$，於每個尺度 $k$ 上以 bilinear interpolation 從局部 $2 \times 2$ 鄰域取樣，得到該座標的局部特徵向量。

**Input:**
- Name: 特徵金字塔 $\{f^k\}$ 與查詢座標 `(x, y)`
- Shape: $f^k$ 如上；座標 `[B, N, 2]`，$(x, y) \in [0, W] \times [0, H]$
- Source: Reassemble Block；Infinite Depth Query 或外部任意座標

**Output:**
- Name: $\{f^k_{(x,y)}\}_{k=1}^L$
- Shape: `[B, N, C_k]`，即 `[B, N, 256]`, `[B, N, 512]`, `[B, N, 1024]`
- Consumer: Hierarchical Residual Gated Fusion

**Processing:**

1. 將連續座標縮放到第 $k$ 尺度的網格座標：$(x_k, y_k) = (x \cdot w_k / W, y \cdot h_k / H)$；
2. 取局部鄰域 $\mathcal{N}_k(x_k, y_k) = \{(i, j) \mid i \in \{\lfloor x_k \rfloor, \lfloor x_k \rfloor + 1\}, j \in \{\lfloor y_k \rfloor, \lfloor y_k \rfloor + 1\}\}$；
3. 對該 $2 \times 2$ 鄰域做 bilinear interpolation 得 $f^k_{(x,y)}$。此操作對 $(x, y)$ 可微，是後續 autograd 求法線的基礎。

**Key Formulas:**

$$(x_k, y_k) = \left(x \cdot \frac{w_k}{W},\ y \cdot \frac{h_k}{H}\right)$$

$$f^k_{(x,y)} = \text{BilinearInterp}\big(f^k,\ \mathcal{N}_k(x_k, y_k)\big) \in \mathbb{R}^{1 \times C_k}$$

**Implementation Details:**

論文以 ablation 比較了「explicitly learning offsets vs. bilinear interpolation」與「cross-attention vs. shared MLP」兩類替代設計，詳見 supp.（main paper §4.4 提及）。在 §3.2 主文中採用最簡單且可微的 bilinear interpolation。

#### 5.3.4 Hierarchical Residual Gated Fusion

**Function:** 從最淺層（高解析度、細節）到最深層（低解析度、語意）依序融合多尺度局部特徵，產生供 MLP head 解碼的單一語意-細節整合特徵。

**Input:**
- Name: $\{f^k_{(x,y)}\}_{k=1}^L$
- Shape: 如 §5.3.3
- Source: Feature Query

**Output:**
- Name: $h_L$（此處 $L = 3$）
- Shape: `[B, N, 1024]`
- Consumer: MLP Head

**Processing:**

設 $h_1 := f^1_{(x,y)}$。對 $k = 1, \ldots, L-1$ 依序執行 residual gated fusion（Eq. 3，p. 4）：對前一層融合特徵 $h_k$ 先以 `Linear` 投影到 $C_{k+1}$ 維、與可學習通道閘 $g_k$ 做 element-wise 乘積、與該層特徵 $f^{k+1}_{(x,y)}$ 相加後送入兩層 FFN。重複至 $k = L - 1$ 得 $h_L$。

**Key Formulas:**

$$h_{k+1} = \text{FFN}_k\!\left(f^{k+1}_{(x,y)} + g_k \odot \text{Linear}_k(h_k)\right)$$

其中 $\text{Linear}_k: \mathbb{R}^{C_k} \to \mathbb{R}^{C_{k+1}}$、$g_k \in (0, 1)^{C_{k+1}}$ 為通道級可學習閘、$\odot$ 為 element-wise 乘積、$\text{FFN}_k$ 為兩層 feed-forward。

**Implementation Details:**

依 supp. A.1，FFN 先把輸入維度 expand $4 \times$，過一個 nonlinear activation，再壓回原維度（標準 transformer FFN 結構）。閘 $g_k$ 的初始化方式、是否經 sigmoid（以保證落在 $(0, 1)$）論文未明確說明。

#### 5.3.5 MLP Head

**Function:** 把最深層融合特徵 $h_L$ 解碼為該座標的單一深度標量。

**Input:**
- Name: $h_L$
- Shape: `[B, N, 1024]`
- Source: Hierarchical Residual Gated Fusion

**Output:**
- Name: $d_I(x, y)$
- Shape: `[B, N, 1]`
- Consumer: 損失計算（訓練）、Infinite Depth Query / 反投影 / NVS（推論）

**Processing:**

3 層 linear，前兩層後接 ReLU，最後一層輸出後接 ELU。輸入維度 1024、hidden 維度 256、輸出維度 1（supp. A.1）。最後使用 ELU 是為避免梯度消失（vanishing gradient）。

**Key Formulas:**

$$d_I(x, y) = \text{ELU}\big(W_3 \cdot \text{ReLU}(W_2 \cdot \text{ReLU}(W_1 \cdot h_L + b_1) + b_2) + b_3\big)$$

其中 $W_1 \in \mathbb{R}^{256 \times 1024}$、$W_2 \in \mathbb{R}^{256 \times 256}$、$W_3 \in \mathbb{R}^{1 \times 256}$。

**Implementation Details:**

訓練時對 ground-truth 深度先取對數空間並用 2% / 98% 分位數做 affine-invariant normalization（supp. A.4，Eq. 13）；relative depth 設定下 MLP head 直接回歸正規化後的 $d_{\text{norm}}$。Metric 設定中則經 depth prompt 模組（PromptDA [22]）注入稀疏深度先驗。

#### 5.3.6 Infinite Depth Query

**Function:** 利用 implicit field 對影像座標可微的特性，將每像素查詢預算依 3D 表面元素 $\Delta S$ 加權重新分配，產生表面密度近似均勻的 sub-pixel 點雲，供大視角 NVS 使用。

**Input:**
- Name: 像素級深度 $d_I(u, v)$ 與相機內參
- Shape: $d_I$: `[B, H·W, 1]`；內參假設已知（論文未具體列出處理方式）
- Source: MLP Head（per-pixel query）

**Output:**
- Name: 表面密度均勻的 sub-pixel 查詢座標 $\{(x_j, y_j)\}_{j=1}^N$ 及對應 3D 點 $X(x_j, y_j)$
- Shape: 取決於每像素分配的子像素數量；總點數 $N$ 為超參
- Consumer: GS head（NVS application，supp. A.3）或下游 NVS pipeline

**Processing:**

1. 在像素中心取深度，反投影得 3D 點 $X(u, v)$；
2. 以 autograd 對 $X$ 關於 $(x, y)$ 求 Jacobian，得 surface normal $n(u, v)$（Eq. 6）；
3. 計算每像素對應的 differential surface area weight $w(u, v)$（Eq. 5），其中 $d^2$ 補償透視縮放、$|n \cdot v|$ 補償法向斜射造成的投影壓縮；
4. 將 $w$ 標準化為機率分佈 $p_i$，建立 CDF 並以 stratified inverse-transform sampling 抽出 $N$ 個目標機率 $q_j = (j + 0.5) / N$，反查到像素索引 $k_j$（supp. A.2，Eq. 8–11）；
5. 在該像素中心加上 sub-pixel jitter $\delta_u, \delta_v \sim U(-0.5, 0.5)$（Eq. 12），對 implicit field 重新查詢 $d_I(x, y)$ 並反投影得最終 3D 點。

**Key Formulas:**

$$w(x, y) = \frac{d_I(x, y)^2}{\big|n(x, y) \cdot v(x, y)\big| + \varepsilon} \propto \Delta S(x, y) \quad \text{(Eq. 5)}$$

$$n(x, y) = \frac{\partial_x X(x, y) \times \partial_y X(x, y)}{\big\|\partial_x X(x, y) \times \partial_y X(x, y)\big\|} \in \mathbb{R}^3 \quad \text{(Eq. 6)}$$

**Implementation Details:**

$\varepsilon$ 為小常數以避免除零（值未明示）；視線方向 $v(x, y)$ 由相機內參推得但具體實作（如 ray direction 計算）論文未列。Sampling 採 stratified inverse-transform 而非 multinomial，以降低變異。GS head 應用時點雲作為 Gaussian center，再以額外 MLP + 多個 linear head 預測 position offsets、color offsets、scales、opacities、rotations（supp. A.3）。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Hypersim [30] | Relative / metric depth (synthetic indoor) | the paper does not specify count | train |
| VKITTI [4] | Relative / metric depth (synthetic driving) | the paper does not specify count | train |
| TartanAir [43] | Relative / metric depth (synthetic SLAM) | the paper does not specify count | train |
| IRS [40] | Relative / metric depth (synthetic indoor stereo) | the paper does not specify count | train |
| UnrealStereo4K [37] | High-resolution synthetic stereo | the paper does not specify count | train |
| UrbanSyn [10] | Synthetic driving | the paper does not specify count | train |
| MatrixCity [20] | Synthetic city-scale | the paper does not specify count | train (App. B.2) |
| MVS-Synth [15] | Synthetic multi-view | the paper does not specify count | train (App. B.2) |
| BlendedMVS [50] | Multi-view stereo | the paper does not specify count | train (App. B.2) |
| CREStereo [19] | Stereo | the paper does not specify count | train (App. B.2) |
| FSD [45] | Stereo | the paper does not specify count | train (App. B.2) |
| DynamicReplica [17] | Dynamic stereo | the paper does not specify count | train (App. B.2) |
| Waymo [36] | Single-view NVS (driving) | a subset of train split | train (GS head) / test on unseen scenes (App. C.2) |
| Synth4K (Synth4K-1…5) | Zero-shot relative & metric depth at 4K | five subsets, "hundreds" of $3840 \times 2160$ pairs each | test (curated by this paper) |
| KITTI [9] | Zero-shot relative & metric depth | the paper does not specify count | test |
| ETH3D [32] | Zero-shot relative & metric depth | the paper does not specify count | test |
| NYUv2 [33] | Zero-shot relative & metric depth | the paper does not specify count | test |
| ScanNet [6] | Zero-shot relative & metric depth | the paper does not specify count | test |
| DIODE [38] | Zero-shot relative & metric depth | the paper does not specify count | test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| $\delta_1$ | Percentage of pixels with $\max(d/d^*, d^*/d) < 1.25$ for relative depth | yes |
| $\delta_{0.5}$ | Stricter threshold $< 1.25^{0.5}$ for high-resolution / fine-grained relative depth on Synth4K | yes |
| $\delta_2$ | Looser threshold $< 1.25^2$ for relative depth | no |
| $\delta_{0.01}$ | Percentage of pixels with $\max(d/d^*, d^*/d) < 1.01$ for metric depth (with sparse depth input) | yes |
| $\delta_{0.02}$ | Threshold $< 1.02$ for metric depth | no |
| $\delta_{0.04}$ | Threshold $< 1.04$ for metric depth | no |
| HF-mask evaluation | Same $\delta$ metrics computed only on high-frequency mask regions (Laplacian-energy sampled), targeting fine-detail performance | yes |
| Decoder parameter count (M) | Decoder size for efficiency comparison (App. A.5) | no |
| Inference time (s/it) | Wall-clock time on a single $504 \times 672$ image | no |

### 6.3 Training and Inference Settings

- **Backbone**: DINOv3 [34] ViT-Large encoder; features taken from layers 4, 11, 23 and projected to hidden dimensions 256 / 512 / 1024; layers 4 and 11 upsampled by 4× and 2× respectively (§3.4).
- **Decoder**: multi-scale local implicit decoder; FFN expands by 4× then compresses; MLP head has three linear layers with ReLU and a final ELU activation (input dim 1024, hidden 256) (App. A.1).
- **Optimizer / learning rate**: AdamW with learning rate $1 \times 10^{-5}$ (§3.4); GS head trained separately at $1 \times 10^{-4}$ with frozen ViT (App. A.4).
- **Training schedule**: 800k steps (§3.4).
- **Hardware / batch**: 8 NVIDIA GPUs, batch size 4 per GPU; the paper does not specify the GPU model (§3.4).
- **Loss**: $L_1$ on $N$ randomly sampled coordinate-depth pairs per image, $N = 100\text{k}$ in practice (§3.4, App. A.4); GS head adds an LPIPS perceptual term (App. A.4).
- **Depth normalization**: ground-truth depth converted to log space, then affine-normalized using 2% / 98% quantiles (App. A.4, Eq. 13).
- **Sub-pixel supervision**: RGB is resized but ground-truth depth keeps its original (often higher) resolution, so loss is computed at continuous sub-pixel coordinates (App. A.4).
- **Inference resolution**: real-world benchmarks resized to $504 \times 672$; Synth4K resized to $504 \times 896$. Baselines bilinearly upsampled to 4K, while InfiniDepth queries directly at 4K via implicit fields (App. C.1).
- **Metric depth**: 1500 sparse depth points sampled from ground truth as additional input for all metric methods; no alignment at evaluation. Relative depth uses scale-and-shift alignment to ground truth (App. C.1).
- **Infinite Depth Query**: stratified inverse-CDF sampling of sub-pixel coordinates, weighted by $w(x,y) = d_I(x,y)^2 / (|n \cdot v| + \varepsilon)$ where $n$ comes from autograd through the implicit field (§3.3, App. A.2).

### 6.4 Main Results

Synth4K-1 full-image relative depth (Table 1):

| Method | $\delta_{0.5}$ | $\delta_1$ | $\delta_2$ | Notes |
|---|---|---|---|---|
| DepthAnything [48] | 70.4 | 83.8 | 93.0 | grid decoder |
| DepthAnythingV2 [49] | 67.3 | 81.3 | 91.0 | grid decoder |
| DepthPro [3] | 63.5 | 80.2 | 91.2 | targets sharp depth |
| MoGe [41] | 69.3 | 83.7 | 92.7 | point map |
| MoGe-2 [42] | 69.0 | 84.2 | 93.4 | strongest grid baseline |
| Marigold [39] | 54.6 | 72.9 | 85.1 | diffusion |
| PPD [46] | 61.5 | 81.1 | 92.5 | semantics-prompted DiT |
| **Ours** | **74.3** | **89.0** | **96.1** | implicit field, queried at 4K |

Synth4K-1 high-frequency-mask relative depth (Table 1):

| Method | $\delta_{0.5}$ | $\delta_1$ | $\delta_2$ |
|---|---|---|---|
| MoGe-2 [42] | 48.9 | 66.5 | 82.6 |
| MoGe [41] | 48.8 | 65.8 | 80.9 |
| DepthPro [3] | 43.4 | 62.4 | 80.6 |
| **Ours** | **49.2** | **67.5** | **83.1** |

Synth4K-1 metric depth with 1500 sparse points (Table 2):

| Method | $\delta_{0.01}$ | $\delta_{0.02}$ | $\delta_{0.04}$ |
|---|---|---|---|
| Marigold-DC [39] | 19.5 | 31.9 | 48.0 |
| Omni-DC [53] | 38.8 | 46.0 | 54.1 |
| PriorDA [44] | 44.8 | 67.2 | 80.7 |
| PromptDA [22] | 65.0 | 79.8 | 88.0 |
| **Ours-Metric** | **78.0** | **86.7** | **92.0** |

Real-world relative depth $\delta_1$ (Table 3):

| Method | KITTI | ETH3D | NYUv2 | ScanNet | DIODE |
|---|---|---|---|---|---|
| MoGe-2 [42] | 98.3 | 99.0 | 98.2 | 98.4 | 97.4 |
| MoGe [41] | 98.3 | 98.9 | 98.0 | 98.2 | 97.4 |
| DepthAnything [48] | 97.5 | 98.4 | 97.8 | 97.8 | 97.3 |
| **Ours-Relative** | 97.9 | **99.1** | 97.6 | 97.3 | **97.4** |

Real-world metric depth $\delta_{0.01}$ (Table 4):

| Method | KITTI | ETH3D | NYUv2 | ScanNet | DIODE |
|---|---|---|---|---|---|
| Marigold-DC [39] | 36.6 | 72.6 | 71.4 | 76.7 | 84.2 |
| Omni-DC [53] | 17.5 | 57.4 | 62.1 | 55.8 | 83.3 |
| PriorDA [44] | 54.1 | 85.7 | 78.1 | 82.7 | 94.3 |
| PromptDA [22] | 58.3 | 92.8 | 83.6 | 87.0 | 97.3 |
| **Ours-Metric** | **63.9** | **96.7** | **86.9** | **90.4** | **98.4** |

InfiniDepth wins decisively on Synth4K (full-image and HF-mask) and on real-world metric depth, while matching SOTA on real-world relative $\delta_1$ — consistent with the paper's thesis that the implicit-field representation pays off most where resolution and fine geometry matter, and saturates on coarse low-resolution real-world ground truth.

### 6.5 Ablation Studies

- **Depth representation (Table 5, metric)**: replacing the implicit field with a DPT-style grid decoder (same DINOv3 ViT-L encoder, same Hypersim training) drops $\delta_{0.01}$ on Synth4K-1 from 72.7 → 62.4 and on KITTI from 61.7 → 49.0. **Diagnostic** — directly isolates the paper's central claim.
- **Depth representation (Table 8, relative)**: removing implicit fields barely changes relative $\delta_{0.01}$ (e.g. Synth4K-1 82.5 → 82.4, ScanNet 97.2 → 97.1). The paper concedes metric saturation under scale-and-shift alignment and points to qualitative gains (Fig. 7) instead. **Honest but only partially diagnostic**, since the chosen metric saturates.
- **Multi-scale feature query (Table 5)**: querying only the encoder's final feature map drops Synth4K-1 $\delta_{0.01}$ from 72.7 → 66.6 and ScanNet from 88.5 → 86.2. **Diagnostic** — isolates the feature-pyramid component.
- **Image encoder DINOv3 → DINOv2 (Table 5)**: drops Synth4K-1 from 72.7 → 63.8 and KITTI from 61.7 → 57.9, with App. C.3 noting "no significant performance differences" for relative depth. **Mostly a backbone-quality control**, useful but largely a sanity check.
- **Sub-pixel vs. pixel-wise supervision (Table 7)**: sub-pixel supervision improves Synth4K-1 $\delta_{0.01}$ from 70.0 → 72.7 and KITTI from 58.8 → 61.7. **Diagnostic** — directly tests whether the implicit field's sub-pixel querying is actually exploited during training.
- **Feature-query design (Table 9)**: bilinear interpolation beats coordinate-offset MLP, coordinate-offset MLP with local ensemble, and cross-attention on every benchmark (e.g. KITTI 61.7 vs. 59.3 / 54.1 / 54.8). **Diagnostic** — justifies the simplest design.
- **Infinite Depth Query strategy**: only ablated qualitatively (Fig. 1c, Fig. 8, Fig. 13) against per-pixel ADGaussian for NVS; **no quantitative ablation** of the surface-area weight $w(x,y)$ vs. uniform sub-pixel sampling, so the contribution of the $d^2 / |n \cdot v|$ weighting itself is not isolated.

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — compares against MoGe-2 [42], DepthPro [3], DepthAnythingV2 [49], PPD [46] for relative; PromptDA [22], Omni-DC [53], PriorDA [44] for metric (Tables 1–4).
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — evaluates on Synth4K (5 subsets), KITTI, ETH3D, NYUv2, ScanNet, DIODE, plus Waymo for NVS (Tables 1–4, App. C.2).
- [partial] Has ablations that diagnose the new components (not just sanity checks) — depth representation, multi-scale query, sub-pixel supervision, and feature-query design are diagnostic, but the Infinite Depth Query weighting $w(x,y)$ is never quantitatively ablated against uniform sub-pixel sampling.
- [missing] Has a scaling study (size, length, or compute) — no sweep over ViT size, training steps, sample count $N$, or query density; only one ViT-L configuration is reported.
- [partial] Has an efficiency / wall-clock comparison — Table 6 reports decoder params and per-image time at $504 \times 672$, but does not report 4K inference cost or memory, which is the regime the paper actually targets.
- [missing] Reports variance / standard deviation / multiple seeds where relevant — all tables report single-run point estimates with no error bars or seed averaging.
- [partial] Releases code / weights / data sufficient for reproducibility — a project page is referenced (zju3dv.github.io/InfiniDepth) but the paper does not specify code/weight release; Synth4K is curated from commercial games (CyberPunk 2077, Spider-Man 2, Miles Morales, Dead Island, Watch Dogs) via ReShade, raising clear redistribution questions that the paper does not address.

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 提出 neural implicit depth representation 以實現 arbitrary-resolution 與 fine-grained estimation。** **Partially supported.** 在 Synth4K 全圖與 HF mask 兩種設定下確實全面領先（Table 1），且 ablation 顯示移除 implicit field 會明顯退化（Table 5）。但 arbitrary-resolution 部分的 16K/8K 宣稱缺乏 quantitative 評測，且 ablation 與 sub-pixel 監督混雜（Table 7），「離散網格不可行」的因果歸因強度不足。
- **C2: 設計 multi-scale local implicit decoder（reassemble + 階層 gated fusion + MLP head）。** **Supported as engineering**，Table 5 的 "w/o Multi-Scale Query" 顯示去掉多尺度會在所有資料集劣化（如 Synth4K-1 $\delta_{0.01}$ 自 72.7 → 66.6），但在架構新穎性層面與 LIIF/AnyFlow 等先前 implicit decoder 的差異主要落在「殘差 gated fusion」這個小設計，貢獻偏向 incremental。
- **C3: Infinite Depth Query 為大視角 NVS 產生表面均勻 3D 點。** **Overclaimed in evidence form.** 概念明確且 Fig. 8、Fig. 13 視覺上 ADGaussian 確有破洞而本方法完整，但無 PSNR/SSIM/LPIPS 量化結果、無 user study、無與「均勻取樣 3D 點 + 任何 GS 解碼」的消融，難以分辨增益來自 query 策略還是 GS head 設計本身。
- **C4: Synth4K 4K benchmark 與 HF mask 工具。** **Supported**，dataset curation 流程（ReShade 抽取、multi-scale Laplacian energy、temperature sharpening、multinomial sampling）描述完整（Sec. B.1），對社群可重用。但身為 dataset proposer 同時也是 benchmark 上最強方法，存在角色衝突，需第三方獨立驗證。
- **C5: Real-world benchmark 上 SOTA。** **Overclaimed.** Table 3 五個資料集中本方法僅在 ETH3D 居首，KITTI/NYUv2/ScanNet 皆落後 MoGe-2 約 0.3–1.1 個百分點；摘要與 Sec. 4.3 將其稱為「on par」屬於合理弱化，但與 abstract 中 "state-of-the-art performance ... on real-world benchmarks" 的強宣稱不一致。Metric 設定（Table 4）才是真正領先處。

### 7.2 Fundamental Limitations of the Method

**單張影像、單尺度監督的本質性限制。** 雖然表徵連續，但訓練只看單視角且每張影像隨機抽 100k 點；模型其實沒有任何機制保證**多視角一致性**或**跨幀時間一致性**。作者已承認時序 flickering，但更深層的問題是：implicit field 的容量被全部用來在 2D 影像條件下擬合單張深度，當 query 解析度遠超訓練解析度時，輸出會被 ViT token grid 的鋸齒（aliasing）與 reassemble block 的上採樣 prior 所主導，而非「真正自由」。這意味 16K query 並非真的有 16K 等價的監督訊號，本質仍在 4K 訊息天花板下做 plausible 插值。

**Surface normal 與 Infinite Depth Query 的可微性陷阱。** Eq. 6 透過 autograd 對 $X(x, y)$ 求 Jacobian，但 $X(x, y)$ 經過 bilinear interpolation 與 MLP 後，其導數受 ViT feature map 的離散化嚴重影響——bilinear feature interpolation 的二階導為零，這代表算出來的 normal 在 token 邊界附近會出現分段常數型 artifact。論文的 Fig. 4 normal map 看似平滑，但這是對單張低頻場景的展示；對高頻區域（恰是 Infinite Depth Query 想加密取樣的地方）此估計可能不可靠，造成 query 預算錯誤分配。

**監督密度上限受限於原始 GT 解析度。** 訓練宣稱「sub-pixel supervision」，但 Sec. A.4 揭露其實是「將 RGB resize、保留原 GT 解析度後抽 100k 點」，並未真的提供 sub-pixel ground truth；當訓練集 GT 本身解析度有限（例如 Hypersim 1024×768），所謂 sub-pixel 只是利用 grid 點之外的 bilinear-interpolated GT，與真正連續 depth field 的監督仍有落差。任意解析度宣稱在訓練端就有資料瓶頸。

**架構選擇的「網格不可行」論點未被嚴格證明。** 論文反覆主張 "grid-based representations 限制細節恢復"，但 Table 5 的 ablation 把表徵替換與其他訓練設定一併替換；更重要的是 DepthPro、MoGe-2 等同樣 grid-based 的方法在 real-world 全部五個 dataset 上仍與本方法持平或略勝（Table 3），這直接削弱「網格本身就是錯誤表徵」的宣稱。較合理的詮釋是：在合成高頻細節這個 niche，implicit + multi-scale local query 有優勢；但這是區域性勝利，不是表徵層級的必然性。

### 7.3 Citations Worth Tracking

- **LIIF (Chen et al., CVPR 2021，ref [5])** — 本工作 implicit decoder 的直接思想源頭，對「local implicit + bilinear feature ensemble」的設計選擇與其與 InfiniDepth bilinear interpolation 變體的比較最具參考價值。
- **PromptDA (Lin et al., CVPR 2025，ref [22])** — 同一通訊作者的 metric depth 直系前作，本論文 metric 路線的 prompt 模組完全來自此處，必讀以判斷 metric 增益是來自 implicit field 還是 prompt 模組。
- **MoGe-2 (Wang et al., 2025，ref [42])** — Synth4K 與 real-world 上最強 baseline，且 affine-invariant point map 監督是與「continuous coordinate」概念正交的另一條改進路線。
- **DINOv3 (Siméoni et al., 2025，ref [34])** — 唯一使用的 backbone，Table 5 顯示換成 DINOv2 會明顯退化（Synth4K-1 $\delta_{0.01}$ 72.7 → 63.8），有必要了解新增的特性是否就是本論文增益的真正來源。
- **ADGaussian (Song et al., 2025，ref [35])** — NVS 對照組與 Haotong Lin 同組之作，了解此 baseline 的弱點才能判斷 Infinite Depth Query 的「視覺勝利」是否公平。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在固定相同的 sub-pixel 監督與 multi-scale local query 下，將解碼頭從 implicit MLP 改為 grid + bilinear upsampling，是否仍能達到 Table 1 的細節精度？亦即「implicit」與「local + sub-pixel」誰才是真正的成因？
- [ ] Synth4K 五個遊戲與訓練集 UnrealStereo4K、UrbanSyn 之間的 domain gap 多大？若做 leave-one-game-out 或排除合成訓練資料的版本，HF mask 領先幅度還剩多少？
- [ ] Infinite Depth Query 的量化 NVS 指標（PSNR/SSIM/LPIPS）為何？若僅將 ADGaussian 的 per-pixel depth 換成 implicit depth 但不啟用自適應權重 $w(x, y)$，差距會落在哪裡？
- [ ] 由 autograd 對 bilinear-interpolated feature 求得的 normal 在 ViT token boundary 處是否出現可量化的 artifact？這是否反過來污染 Eq. 5 的權重分布？
- [ ] 在實際 4K 推論時，加上 normal 計算與 sub-pixel sampling 的端對端延遲是多少？Table 6 的 0.16 s/it 是否能延伸到 4K/16K 場景？
- [ ] 與 DepthPro（同樣強調 sharp 高解析）在 4K HF mask 區域的細節精度差距僅 1–3 個百分點，是否在 dense, very-thin structure（電線、髮絲）等極端設定下會反轉？
- [ ] real-world relative 上落後 MoGe-2 的根因是否真為「ambiguity 飽和」？若改用 boundary recall 或 edge-aware 指標，差距會被放大還是縮小？

### 8.2 Improvement Directions

1. **加入針對 implicit field 的 multi-view / 跨幀一致性損失。** 作者已點明 future work，但具體做法可借用 DeFiNe 的 epipolar consistency 或將相鄰幀的 implicit field 在共視點上做 photometric/geometric agreement 約束；此舉直接針對最大可動搖的能力——影片穩定性——且不需要重訓 backbone，邊際收益對下游 NVS、SLAM 應用很高。
2. **對 ablation 做變因解耦實驗。** 額外加入「grid + sub-pixel supervision」「implicit + pixel-wise supervision」兩個對角格，把 Table 5 與 Table 7 整合成 2×2 設計，才能合法支持 abstract 中「representation is the bottleneck」的因果宣稱。成本低、論證強度提升大。
3. **量化 Infinite Depth Query 對 NVS 的實質貢獻。** 在 Waymo BEV 設定下報告 PSNR/SSIM/LPIPS，並做 ablation：固定 GS head，比較 (a) per-pixel grid depth、(b) implicit depth + per-pixel query、(c) implicit depth + Infinite Depth Query 三條件，才能釐清增益是來自 implicit 還是 query 策略。
4. **將 normal estimation 改為混合監督。** 目前完全靠 autograd 推得，可在訓練時對 GT 提供的 normal map（Hypersim、TartanAir 都有）施加直接 supervision，使 implicit field 的高階導數結構更穩定，順便提升 Infinite Depth Query 在高頻區域的可靠性。
5. **建立第三方驗證的 4K real-world benchmark。** Synth4K 角色衝突明顯；可推動社群整合 ETH3D 高解析子集 + UnrealStereo4K test split + 1–2 個 LiDAR 高密度 4K 序列為共同高解析評測，降低自證偏差。
6. **以 PatchFusion 風格的 tile 式推論彌補 16K 解析度的計算瓶頸。** 既然 implicit field 在區域上是局部的，16K query 可拆成 patch 平行推論並 cache 共用 ViT token，減少 0.16 s/it × scaling 所帶來的線性放大，使 arbitrary-resolution 宣稱在工程上落地。
