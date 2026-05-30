<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# CircViT — Vision Transformers are Circulant Attention Learners

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | CircViT |
| Paper full title | Vision Transformers are Circulant Attention Learners |
| arXiv ID | 2512.21542 |
| Release date | 2025-12-25 |
| Conference/Journal | AAAI 2026 |
| Paper link (abs) | https://arxiv.org/abs/2512.21542 |
| PDF link | https://arxiv.org/pdf/2512.21542 |
| Code link | https://github.com/LeapLabTHU/Circulant-Attention |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Dongchen Han | Department of Automation, BNRist, Tsinghua University | — (https://scholar.google.com/citations?user=wv3U3tkAAAAJ&hl=en) | co-first author |
| Tianyu Li | Institute for Interdisciplinary Information Sciences, Tsinghua University | — | co-first author |
| Ziyi Wang | Department of Automation, BNRist, Tsinghua University | — | co-author |
| Gao Huang | Department of Automation, BNRist, Tsinghua University | https://gaohuang-net.github.io/ | corresponding author |

### 1.2 Keywords

Vision Transformer, self-attention, BCCB matrix, circulant matrix, Fast Fourier Transform, efficient attention, O(N log N) complexity, image classification

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| Vaswani et al. 2017 (Transformer / self-attention) | predecessor | 原始 self-attention 與 Transformer 公式，本文以其為改造對象並取代為 BCCB 結構注意力。 |
| Touvron et al. 2021 (DeiT) | baseline | 全域 self-attention 代表，作者觀察其 attention map 呈現 BCCB 樣式並改造為 CA-DeiT 比較。 |
| Liu et al. 2021 (Swin Transformer) | baseline | 局部視窗注意力代表，本文以 CA-Swin 形式替換其前兩階段並比較。 |
| Wang et al. 2021 (PVT) | baseline | 稀疏注意力（key/value 下採樣）代表，本文以 CA-PVT 形式比較並驗證。 |
| Rao et al. 2021 (GFNet) | influence | 以 DFT 卷積定理建立 $O(N \log N)$ 全域 depth-wise convolution，啟發本文以 2D DFT 實作。 |
| Guibas et al. 2021 (AFNO) | influence | 輸入相關頻域濾波器達成動態 depth-wise 卷積，提供以 DFT 取代注意力的設計借鑑。 |
| Davis 1979 (Circulant Matrices) | influence | BCCB 為 circulant matrix 的 2D 推廣，本文藉此理論證明 attention map 投影與 FFT 加速。 |

## 2. Research Overview

### 2.1 Research Topic

本文研究視覺 Transformer 中 self-attention 的高運算成本問題。作者觀察到視覺 Transformer 學到的 attention map 在實務上常近似於 BCCB（Block Circulant matrix with Circulant Blocks），即一種具循環結構、與 2D 全域卷積等價的特殊矩陣。基於此觀察，他們提出 Circulant Attention，將 attention map 顯式投影到 BCCB 子空間，並利用 2D 離散傅立葉轉換（FFT）將計算複雜度由 $O(N^2)$ 降為 $O(N \log N)$；同時保留與 vanilla self-attention 高度一致的運算範式。為彌補 BCCB 結構同時限制行與列總和為 1 所造成的表達瓶頸，作者再加入 token reweighting 模組強化關鍵 token。實驗於 ImageNet 分類、COCO 偵測與 ADE20K 分割上，將其套用於 DeiT、PVT、Swin 等代表性架構皆取得一致提升，並推出 CAT 系列模型，宣稱為 self-attention 的高效替代方案。

### 2.2 Domain Tags

- Computer Vision
- Deep Learning
- Vision Transformer
- Efficient Neural Architectures

### 2.3 Core Architectures Used

- **Circulant Attention (CA)**：本文提出的核心注意力機制，將 attention map 顯式投影到 BCCB 子空間，藉由 2D DFT 與 FFT 將注意力計算複雜度降為 $O(N \log N)$，是替代 vanilla self-attention 的主要產物。
- **Circulant Attention Transformer (CAT)**：本文設計的專屬骨幹模型家族（CAT-T/S/B），用於與 SOTA Vision Transformer 與 Mamba 變體在 ImageNet 上對齊比較。
- **Token Reweighting Module**：以 $T = \mathrm{SiLU}(xW_T)$ 形式的輕量輸入相依重加權（pre/post-reweighting），補償 BCCB 雙隨機性無法強調少數重要 token 的副作用。
- **DeiT (Touvron et al. 2021)**：全域 self-attention 代表，作者觀察其 attention map 呈 BCCB 樣式並改造為 CA-DeiT 進行對比。
- **PVT (Wang et al. 2021)**：稀疏注意力代表（key/value 下採樣），本文於前兩階段以 CA-PVT 形式替換其 attention 模組。
- **Swin Transformer (Liu et al. 2021)**：局部視窗注意力代表，本文以 CA-Swin 形式替換其前兩階段並比較。
- **2D Discrete Fourier Transform (2D DFT) / FFT**：本文用以實作循環卷積等價計算的數學工具，提供 $O(N \log N)$ 加速基礎並支撐 DFT-based multiplication ($\circledast$)。
- **BCCB Matrix**：將 attention map 約束至此子空間是本文方法的結構先驗，對應到具平移不變性的 2D 全域卷積。

### 2.4 Core Argument

作者主張現有降低 self-attention 運算量的手法（如 Swin 的視窗局部性、PVT 的 key/value 下採樣、BiFormer 的稀疏路由）本質上是「人工外加」的限制，會破壞自注意力的長程建模能力與可擴展性。他們透過視覺化 DeiT 的 attention map 發現：在不被人工約束時，自注意力本身就傾向學到 BCCB 結構，亦即近似於具平移不變性的 2D 全域卷積；相鄰 query 的 attention 分布近似為彼此的空間位移，正是 BCCB 矩陣與循環卷積對應的行為。這意味著 self-attention 名義上是 $O(N^2)$，但實際學到的就是可由 FFT 在 $O(N \log N)$ 內計算的結構。因此，與其用外加稀疏或局部性犧牲表達力，不如「順著」這個觀察，把 attention map 顯式約束在 BCCB 子空間。論證上，作者證明 BCCB 子空間以 $N$ 個正交基底張成，attention 矩陣的最近 BCCB 投影可寫為 $Q$、$K$ 的 2D 循環互相關，再經 2D DFT 即可一次到位地計算 attention 與輸出 $\sigma(\tilde{A})V$，且運算範式與 vanilla self-attention 幾乎一致，僅將 dense matmul 改為 DFT-based multiplication（$\circledast$）。為解決 BCCB 雙隨機性導致無法強調少數重要 token 的副作用，他們以輕量的輸入相依 SiLU 重加權（pre/post-reweighting）作為補償。整體而言，他們論點的核心在於：低複雜度不必靠犧牲全域性換取，而應「對齊」自注意力本身已存在的高效結構先驗，因而 Circulant Attention 在邏輯上是兼顧效率與表達力的必要設計。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(265 words)

標題「Vision Transformers are Circulant Attention Learners」採用宣告式句型,直接點出本文的核心主張:vision Transformer 在訓練後其實會自然學到 circulant 結構的注意力模式。這是一種「觀察先行、方法跟隨」的寫法 — 先把實證現象當作 thesis,再以此推動後續方法設計的合理性,讓讀者在看到方法之前就已經接受「BCCB 是真實存在的 pattern」這個前提。

Abstract 採用標準的「問題 → 既有方案缺陷 → 觀察 → 方法 → 性質 → 結果」六步結構。第一步指出 self-attention 的 $O(N^2)$ 複雜度在高解析度場景下構成負擔;第二步把先前以 locality / sparsity 為手段的方法歸類為「handcrafted patterns」,並批評它們會犧牲 model capacity — 這個批評為自家方法預先建立差異化空間。

第三步是論文的關鍵 insight:vision Transformer 的 attention map 經常近似 Block Circulant matrix with Circulant Blocks (BCCB),而 BCCB 與其他矩陣相乘可在 $O(N\log N)$ 時間內完成。第四步即把這個觀察轉成方法 — 顯式地把 attention map 投影到最近的 BCCB 矩陣,並提出對應的快速計算演算法。

第五步強調設計哲學:由於方法源自 self-attention 的 internal pattern 而非外加約束,因此既享有 $O(N\log N)$ 複雜度,又「largely maintains」原本的表達能力。第六步以 image classification、object detection、semantic segmentation 三類視覺任務概括實驗範圍。

整段 abstract 的論證軸線把「效率」與「表達力」這對 trade-off 重新框定為「observation-driven」而非「constraint-imposed」,為後續 §1 的 research question 「Can we explicitly set the attention map as a BCCB matrix...?」做好鋪陳。

### 3.2 Introduction

(425 words)

Introduction 的故事邏輯沿「成功 → 障礙 → 既有解的缺陷 → 新觀察 → research question → 方法概覽 → 貢獻」推進,每一步都收斂到下一節需要的前提。

開頭兩段先確立 Transformer 在 image classification、detection、segmentation、multimodal 任務上的 dominance,然後立刻轉向 $O(N^2)$ 帶來的 prohibitively high cost,把「全域感受野」與「計算可行性」設為核心張力。作者把 PVT、Swin、NAT、DAT、BiFormer 等 efficient attention 方法統一描述為「introducing handcrafted patterns」,並以 external constraints 一詞貶抑性地概括 — 這是修辭上的關鍵動作,讓所有先前方法都退化為一個共同的對立面,接著就有空間提出「另一條路」。

第三段是論文的轉折點:作者觀察到 vision Transformer 的 attention map 「frequently approximate」BCCB matrix。這裡並未馬上宣稱普適性,而是用 frequently / often 這類保守措辭,把這個現象定位為「值得利用的傾向」而非「定理」。接著用一句話把 BCCB 與 $O(N\log N)$ 的 2D DFT 計算連結起來,指出 self-attention 雖然形式上是 $O(N^2)$,卻 implicitly 學到能用 $O(N\log N)$ 計算的結構 — 這個對比本身就是論文的 selling point。

第四段才正式拋出 research question:「Can we explicitly set the attention map as a BCCB matrix to facilitate efficient computation, while preserving the high expressiveness of vanilla self-attention?」這個提問把後續 §4 的方法定位為「對觀察現象的顯式編碼」,而非又一次工程上的 patch。

接著作者預告方法概覽:把 attention map 垂直投影到 BCCB 子空間,並透過 2D DFT 與 FFT 把計算降到 $O(N\log N)$。Fig. 1 提供視覺對照,強調 circulant attention 與 vanilla self-attention「結構幾乎相同,只差在 BCCB 矩陣與 DFT-based multiplication」 — 這個「最小修改」的訴求支持了後段「不犧牲 capacity」的主張。作者亦提到 token reweighting module,用以彌補 BCCB 結構的固有限制,為 §4 的設計選擇預留鋪陳空間。

最後一段以三條 contribution bullets 收束:現象的揭示、方法的提出、跨任務實驗的驗證。三點分別對應 §3-4 的觀察與推導、§4 的演算法、§5 的實驗,把整篇論文的結構圖一次交給讀者,為 §3 的 preliminaries 做好過渡。

### 3.3 Related Work / Preliminaries

(810 words)

§2 與 §3 雖然分屬不同章節,但功能上構成同一個鋪陳單元:§2 用 literature 把問題空間切開,§3 把所需的數學工具一次性備齊。

§2 的 Vision Transformer 段落把先前工作分為兩大陣營 — 「locality-based」(Swin、CSwin、NAT)與「sparsity-based」(PVT、DAT、BiFormer)。這個二分並非中性,而是服務於本文論證:兩條路都被歸結為「handcrafted patterns」,共同特徵是「inevitably compromise the expressiveness of global self-attention」。透過這個統一批評,作者為自己的「intrinsic efficient structure」路線創造修辭上的第三條道路。

§2 的 Efficient architecture with DFT 段落則處理另一個技術譜系:GFNet、FNO、AFNO、AFFNet 等利用 DFT / FFT 的 token mixer。這段的角色是「方法工具的 lineage」 — 確認 DFT-based 計算在 vision 領域已有成熟案例,因此本文使用 2D DFT 並非冒進。但作者也明確區分:這些工作把 DFT 當成 global convolution 工具,本文則把 DFT 當成 attention 計算的內部加速器。差異在概念定位,而非數學機制。

§3 Preliminaries 在三個小節中堆疊本文方法所需的全部數學基礎,順序刻意安排。§3.1 重新整理 self-attention 的標準形式 $A = QK^\top/\sqrt{d}$、$O = \sigma(A)V$,並交代 $N = H\times W$ 的 reshape 慣例,讓 2D 結構的引入顯得自然。§3.2 介紹 circulant matrix:每行是前一行的 cyclic shift,可由首行 $c$ 完整決定;接著證明 $Cx$ 等同於 1D circular cross-correlation,即「不翻轉 kernel 的 1D depth-wise convolution with circular padding」。藉由 Cross-Correlation Theorem,得到關鍵公式

$$Cx = \mathcal{F}_{1D}^{-1}\big(\overline{\mathcal{F}_{1D}(c)} \odot \mathcal{F}_{1D}(x)\big),$$

並把複雜度從 $O(N^2)$ 降到 $O(N\log N)$。

§3.3 把上述結構推廣到 2D:BCCB 矩陣是 $H\times H$ 個 $W\times W$ circulant blocks 排成的 block circulant 結構,同樣可由首行 $b$ 完整決定;$Bx$ 等同於 2D circular cross-correlation,即 deep learning 中「circular padding 的 2D depth-wise convolution」。對應的 DFT-based 計算為

$$Bx = \mathcal{F}_{2D}^{-1}\big(\overline{\mathcal{F}_{2D}(b)} \odot \mathcal{F}_{2D}(x)\big) \triangleq b \circledast x,$$

其中 $\circledast$ 是作者自定義的 DFT-based multiplication 運算子。這個記號是後續 §4 公式的 syntactic backbone — 一旦 $\circledast$ 被定義,§4 的演算法可以幾乎不寫加總符號就把流程寫清楚。

Table 1 集中列出 $\mathcal{F}_{1D}, \mathcal{F}_{2D}, \overline{(\cdot)}, \sigma, \odot, \circledast, \|\cdot\|, \langle\cdot,\cdot\rangle$ 等 notation,這個前置整理對讀者進入 §4 至關重要,因為 §4 會密集使用 Frobenius inner product 來表達 BCCB 子空間的正交投影。

整體而言,§2 把競爭方法歸類為「handcrafted constraint」,§3 把 circulant / BCCB 的所有性質與快速演算法一次說完,兩者合力為 §4 鋪好兩種敘事:一是「我們的方法不是 handcrafted」,二是「BCCB 與 attention 的銜接已經有現成數學工具」。讀者進入 §4 時,既理解作者要解決什麼問題,也已經掌握所需的全部工具,因此 §4 的方法可以直接以「把 attention 投影到 BCCB 子空間」這個簡潔陳述展開,無需再次引入背景知識。

### 3.4 Method (overview narrative)

(390 words)

§4 的故事邏輯是「現象復現 → 形式化 → 高效演算法 → 限制補強 → 落地實作」,每一步都在為「circulant attention 既高效又不犧牲 capacity」這個核心宣稱蓄勢。

§4.1 「Efficient Pattern in Vision Transformer」直接接續 §1 與 §3 的鋪陳。作者用 Fig. 2 視覺化 DeiT 的 attention map,顯示「沒有任何 handcrafted constraint 的 self-attention 也會學到近似 BCCB 的結構」。Fig. 3 進一步把 attention 視為「relative to query position」的 distribution,展示 consecutive query 的 attention map 呈現 approximate shift invariance — 這正是 2D global convolution 的行為。這兩張圖把 §1 中保守措辭的「frequently approximate」轉成可視化證據,為下一節的 explicit enforcement 提供現象基礎。最後作者把 research question 從「Can we observe this?」收斂到「Can we explicitly enforce a BCCB structure on the attention matrix?」,完成從觀察到設計的轉折。

§4.2 「Circulant Attention」是方法核心,以四個邏輯步驟展開。首先以 Frobenius norm 定義「最近的 BCCB 投影」 $\tilde{A} = \arg\min_{B\in\mathcal{B}} \|A-B\|$,把方法定位為「對 self-attention 的結構化近似」而非另起爐灶。其次證明由 one-hot first-row 構造的 $\{B_0, \dots, B_{N-1}\}$ 是 BCCB 子空間的正交基,因此投影有閉式解 $\tilde{A} = \tfrac{1}{N}\sum_k \langle A, B_k\rangle B_k$。第三步說明這個閉式解仍是 $O(N^2)$,接著導出 $\tilde{A}$ 首行 $a$ 等同於 $\hat{Q}$ 與 $\hat{K}$ 的 2D circular cross-correlation,因此可寫成 $a = \tfrac{1}{N\sqrt{d}}(Q \circledast K)\cdot \mathbf{1}_{d\times 1}$,並且輸出 $O = \sigma(\tilde{A})V$ 因 $\sigma(\tilde{A})$ 仍為 BCCB 而可寫成 $\sigma(a)\circledast V$。第四步給出總複雜度 $\Omega(\text{CA}) = N(\log_2 N)(4d+2) + 4Nd$,與 vanilla 的 $2N^2 d$ 對照,把 $O(N\log N)$ 的優勢以具體常數呈現。

§4.2 結尾的 token reweighting module 處理 BCCB 結構的固有限制:由於 $\sigma(\tilde{A})$ 同時讓 row sum 與 column sum 都為 1,模型無法 emphasize salient keys。作者提出 pre / post 兩種 reweighting 方案,以 input-dependent factor $T = \mathrm{SiLU}(xW_T)$ 補回這個缺失的自由度。

§4.3 「Implementation」交代落地細節:circulant attention 作為 plug-in 取代 DeiT、PVT、Swin 三類代表性模型 — 分別代表 global、sparse、local attention — 的 attention module;對 hierarchical 模型只替換前兩個 stage 以充分發揮 $O(N\log N)$ 在高解析度下的優勢;此外另設計 CAT 系列以與 SOTA 比較。這個布局直接對應 §5 的實驗表格。

### 3.5 Experiments (overview narrative)

(395 words)

§5 採「主任務 → 跨任務 → 效率 → 可解釋性 → ablation」的順序,目標是在多個維度上說服讀者:circulant attention 不只是計算上更便宜,還在性能、可擴展性、可視化上都站得住腳。

§5.1 ImageNet Classification 作為主戰場。作者沿用 baseline 的訓練設定(AdamW、300 epochs、cosine schedule、20-epoch warmup、RandAugment、Mixup、CutMix、random erasing)以維持公平比較。Table 2 left 把三類 baseline(DeiT、PVT、Swin)逐一替換為 CA 版本,每一對都呈現一致的提升:CA-DeiT-T 比 DeiT-T 高 2.8%、CA-PVT-T 高 3.0%,而 CA-PVT-S 用 30% 參數與 40% FLOPs 即可匹敵 PVT-L。這組對照同時涵蓋 global / sparse / local 三種 attention 範式,把「circulant attention 不挑架構」這個普適性論點具象化。Table 2 right 則把 CAT 系列與 VMamba、SOFT、PolaFormer、BiFormer、MILA、TransXNet、OverLoCK 等 SOTA 對齊比較,目的是擋住「baseline 太弱」的可能質疑。

§5.2 COCO 與 §5.3 ADE20K 把效率優勢推向 high-resolution 場景。在 detection 上 CA-PVT-S 比 PVT-L 高 1.3 box AP,FLOPs 卻少很多;在 segmentation 上最多帶來 3.7% mIoU 的提升。作者特別指出 detection 上的增益比 classification 更顯著,這個觀察與 §4 的 $O(N\log N)$ 主張形成回應 — 解析度越高,方法的相對優勢越明顯。

§5.4 Analysis and Visualization 從兩個角度補強。Fig. 4 的 (a)(b) 顯示在 1536² 解析度下 CA-DeiT-T 的 FLOPs 比 self-attention 少 8×、實測速度快 7×,而 (c)(d) 在 224² 預設解析度下也呈現更佳的 throughput-accuracy trade-off,把理論複雜度的優勢轉換為實機數據。Fig. 5 則展示「等效 global convolution kernel」的多樣性:從 bird-shaped、wire-shaped 等 input-dependent 形狀,到 local、global、half-plane、strip、cross 等空間模式 — 把 BCCB attention 的 expressive capacity 視覺化,反駁「結構化會限制表達力」的直覺擔憂。

§5.5 Ablation Study 用逐項堆疊的方式說明設計貢獻。從 DeiT-S 開始:單純導入 circulant attention 帶來微小 0.1% 下降(顯示 BCCB pattern 本身不損 capacity);把 head dimension 設為 $d=1$ 反而升至 80.2%(因為 circulant attention score 等同 $N$ 個 query-key pair 的加總,等效 head dimension 為 $Nd$);加上 token reweighting 達到 81.0%。同時作者也驗證在 vanilla DeiT-S 上加 token reweighting 只會帶來 0.2% 提升,排除「增益來自 reweighting 而非 BCCB」的解釋,強化方法歸因的可信度。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

§6 Conclusion 採用極為精簡的單段式結尾,沒有獨立的 Limitations 或 Future Work 子節 — 這在 efficiency-driven 的 vision Transformer 論文裡相對常見,但也構成本文寫作上的明顯保守選擇。

整段的論證結構是「現象 → 方法 → 結果 → 定位」四步壓縮版。第一步重新陳述觀察:vision Transformer 的 self-attention map「frequently exhibit nearly block circulant with circulant blocks (BCCB) structures」,這個語句與 §1、§4.1 的措辭幾乎一致,刻意維持「保守描述」的語調而不上升為定理。第二步把方法定位為「directly inspires our design」 — 強調 circulant attention 是 observation-driven 而非工程拼湊,這一點與 §1、§2 對 handcrafted pattern 的批評形成回呼。第三步以「extensive experiments across classification, object detection, and semantic segmentation」概括 §5 的實驗範圍,並用「fully demonstrate」做總結性宣稱。第四步把 circulant attention 定位為 self-attention 的「efficient and competitive alternative」,呼應 abstract 與 introduction 的同一用語,完成全文修辭上的閉環。

值得注意的是,本文並未明確列出 limitations,例如:BCCB 結構對 row sum 與 column sum 同時為 1 的約束在 §4.2 已被點出,但 §6 並未把它升級為討論議題;此外 token reweighting 在 vanilla DeiT-S 上效益有限的 ablation 結果,也沒有延伸到 future work 的方向。論文亦未討論 cross-resolution generalization、CLS token 處理、與非方形 token grid 的相容性等潛在限制。讀者若需相關討論,需自行從 §4.2 的 BCCB 結構推導與 §5.5 的 ablation 反推。

## 4. Critical Profile

### 4.1 Highlights

- 觀察並可視化 DeiT 在無任何 handcrafted 約束下，self-attention map 即近似 BCCB 結構（page 3, Fig. 2），並以「相鄰 query 的 attention 分佈呈現空間平移關係」進一步佐證 2D global convolution-like 的平移不變性（page 4, Fig. 3）。
- 在數學上證明 BCCB 子空間由 $N$ 個正交基底 $\{B_0, \dots, B_{N-1}\}$ 張成（page 4, Eq. 10），使 attention map 的最近 BCCB 投影 $\tilde{A}$ 可寫為 $Q$、$K$ 的 2D circular cross-correlation，再由 2D DFT 一次到位地計算（page 4, Eq. 11–16）。
- 將 self-attention 由 $\mathcal{O}(N^2)$ 降為 $\mathcal{O}(N \log N)$，且運算範式幾乎與 vanilla attention 一致，僅將 dense matmul 換成 DFT-based multiplication $\circledast$（page 1, Fig. 1; page 5, Eq. 17–18）。
- 以 plug-in 形式套用至 DeiT、PVT、Swin 三種代表性架構，於 ImageNet-1K 一致提升：CA-DeiT-T 由 72.2 → 75.0（+2.8），CA-PVT-T 由 75.1 → 78.1（+3.0）（page 5, Table 2 left）。
- 在參數／FLOPs 效率上展現高解析度優勢：CA-PVT-S 以約 30% 參數、40% FLOPs 即可匹敵 PVT-L 的 ImageNet 準確度，並在 COCO 上反超 PVT-L 1.3 box AP（page 6, Table 3）。
- 於 ADE20K semantic segmentation，CA-PVT-T 至 CA-PVT-L 一致提升 mIoU，最高達 +3.7 mIoU 增益且 FLOPs 反而下降（page 6, Table 4）。
- 理論複雜度節省可實際轉化為 wallclock 速度：$1536^2$ 解析度下 FLOPs 下降約 8×、推論加速約 7×（page 7, Fig. 4 a, b）。
- 引入輕量 input-dependent SiLU token reweighting（pre/post 兩種形式）以補償 BCCB 雙隨機性導致的 expressiveness 損失（page 5, Eq. 19–20; page 7, Table 5）。
- 提出 CAT-T/S/B 系列模型，在 ImageNet 上與多種 SOTA Transformer / Mamba 變體取得競爭性結果，CAT-B 達 85.0%（page 5, Table 2 right）。
- 從可視化角度展示等效 global convolution kernel 多樣性（鳥形、線狀、半平面、十字等），提供結構可解釋性（page 7, Fig. 5）。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 作者明白指出 BCCB 結構同時迫使 attention map 的 row 與 column 都各自為隨機矩陣（doubly stochastic），無法強調少數重要 token，是相對於 vanilla softmax-attention 的表達瓶頸（page 5, Token reweighting module 段落）。
- ablation 中作者承認，僅將 self-attention 直接替換為 circulant attention 會使 DeiT-S 退化 0.1%（79.8 → 79.7），須再搭配 head dimension $d=1$ 與 token reweighting 才能反超 baseline（page 7, Table 5）。
- 作者注意到 token reweighting 加在 vanilla DeiT-S 上反而下降 1.0%（80.0 vs. 79.8），暗示該模組與 CA 之間存在顯著耦合而非可獨立加總的增益（page 7, Table 5 最末行）。

#### 4.2.2 Phyra-inferred

- 「ViT 學到 BCCB pattern」這一核心觀察僅以少量 DeiT-S attention map 視覺化（Fig. 2、3）佐證，全文未提供量化的 projection residual $\|A - \tilde{A}\|_F / \|A\|_F$ 或 BCCB 子空間能量比例，更未跨層、跨 head、跨資料集統計，難以判定該結構先驗在多大範圍內成立。
- ablation（page 7, Table 5）顯示 raw circulant attention 反退化 0.1%，必須仰賴 $d=1$ 與 SiLU reweighting 才能反超 baseline，但作者未提供「vanilla self-attention + 相同 SiLU reweighting」之對照組，因此無法區分提升究竟來自 BCCB 結構先驗或來自重加權模組本身。
- 對於 PVT、Swin 等 hierarchical 模型僅在前兩個 stage 替換 attention（page 5, Implementation；Appendix Tables 7–9 顯示 res3/res4 仍使用原 PVT/Swin block），暗示後段語義層不適合 BCCB 假設，但全文並未針對此邊界提出機制性解釋或失敗案例分析。
- 採用 conditional positional encoding（Appendix B）以注入位置資訊，但 ablation 並未隔離 CPE 的貢獻；BCCB 結構本身為平移等變，若 CPE 才是真正打破對稱的關鍵，整體增益的歸因會被混淆。
- 將 attention 等價於 2D global depth-wise conv，與 GFNet（Rao et al. 2021）、AFNO（Guibas et al. 2021）的 frequency-domain token mixer 在運算結構上高度重疊，但全文僅在 Related Work 提及，未提供同訓練設定下的 head-to-head 比較，難以判斷 BCCB 框架相較既有 DFT-based 方法的真實 delta。
- circular padding 預設訊號具空間週期性，對自然影像邊界並不成立，論文未對 boundary artifact 進行分析（如以 zero-padded global conv 為對照），亦未報告偵測／分割中影像邊緣區域的分區誤差。
- Throughput-accuracy 曲線（page 7, Fig. 4 c, d）顯示在預設 $224^2$ 解析度下實際加速僅約 1.5×，遠低於 $1536^2$ 下的 7×，但摘要與結論將 CA 推為「promising alternative to self-attention」並未限定於高解析度場景，存在語境放大之嫌。

### 4.3 Phyra's Judgment (summary)

本文真正新穎之處在於把 ViT 學到的 attention pattern 與 BCCB 這個古典結構矩陣明確對齊，並把 DFT-based 全域 token mixer 重述為 self-attention 範式內的「最近 BCCB 投影」，提供新的詮釋角度。然而方法層面與 GFNet / AFNO 等 frequency-domain 設計的本質距離較小，且 ablation 顯示若不加上 SiLU reweighting 與 $d=1$ 的微結構調整，BCCB 結構本身相對於 vanilla self-attention 並未帶來增益。核心未解問題在於：增益究竟源自 BCCB 結構先驗、token reweighting、$d=1$、抑或 conditional positional encoding 之間的耦合，目前的實驗設計尚不足以乾淨拆分。

## 5. Methodology Deep Dive

### 5.1 Method Overview

CircViT 的核心觀察是：vision Transformer 學到的 attention map $A \in \mathbb{R}^{N \times N}$（其中 $N = H \times W$）在實務上常近似於 BCCB（Block Circulant matrix with Circulant Blocks）。BCCB 是 1D circulant matrix 的 2D 推廣，由 $H \times H$ 個 circulant blocks 組成、每個 block 是 $W \times W$ 的 circulant matrix，因此整個 $N \times N$ 矩陣完全由其**第一列**（first row，長度 $N$）決定。基於 2D Cross-Correlation Theorem，BCCB matrix 與其他矩陣相乘等價於 2D circular cross-correlation，可透過 2D DFT 在 $O(N \log N)$ 時間內完成。

Circulant Attention 顯式地將 attention map 投影到 BCCB 子空間，得到最近的 BCCB 矩陣 $\tilde{A} = \arg\min_{B \in \mathcal{B}} \|A - B\|$。作者證明 $\{B_0, \cdots, B_{N-1}\}$（每個 $B_k$ 的第一列為 one-hot vector）構成 BCCB 子空間的 orthogonal basis，因此 $\tilde{A}$ 的第一列 $a$ 可表示為 $Q$ 與 $K$ 的 2D circular cross-correlation 後在 head dimension $d$ 上求和；這個運算又可進一步用 2D DFT 加速為 $a = \frac{1}{N\sqrt{d}}(Q \circledast K) \cdot \mathbf{1}_{d \times 1}$，其中 $\circledast$ 是作者定義的 DFT-based multiplication。

由於 BCCB 矩陣經 row-wise Softmax 後仍為 BCCB（保留結構），輸出 $O = \sigma(\tilde{A})V$ 同樣可以透過 $O = \sigma(a) \circledast V$ 一次到位地計算，整體運算範式與 vanilla self-attention 高度一致，只是把 dense matmul 換成 DFT-based multiplication。為了補償 BCCB 同時限制 row 與 column sum 為 1（doubly stochastic）所造成的「無法強調少數重要 token」副作用，作者進一步加入輸入相依的 token reweighting 模組 $T = \mathrm{SiLU}(xW_T)$，可作用於 $V$（pre-reweighting）或最終輸出（post-reweighting）。實作上，此模組可作為 plug-in 替換 DeiT、PVT、Swin 等模型既有的 attention，並在 hierarchical 模型的前兩個 stage 啟用。

### 5.2 Pipeline Diagram with Tensor Shapes

下圖以 single-head 為主視角描述前向流程；多頭 ($h$ heads) 時各 head 獨立執行下列運算後再做 head-wise summation。$N = H \times W$ 為 spatial token 數，$d$ 為每個 head 的 channel 維度，$C$ 為輸入 token embedding 維度。

```
Input x  [B, N, C]            (N = H × W)
   │
   ├─→ Linear W_Q  ─→ Q  [B, N, d]
   ├─→ Linear W_K  ─→ K  [B, N, d]
   ├─→ Linear W_V  ─→ V  [B, N, d]
   └─→ Linear W_T ─→ SiLU ─→ T  [B, N, d]   (token reweighting factor)

   [Pre-reweighting variant]   V ← V ⊙ T   [B, N, d]

── BCCB attention score path (computing first row a) ──

Q, K  [B, N, d] ──Reshape──→ Q̂, K̂  [B, H, W, d]
   │
   F2D(Q̂)            [B, H, W, d]  (complex)
   F2D(K̂) → conj ─→  F2D(K̂)*       [B, H, W, d]  (complex)
   │
   Hadamard ⊙       :  F2D(K̂)* ⊙ F2D(Q̂)   [B, H, W, d]  (complex)
   F⁻¹_2D            ─→  (Q ⊛ K)            [B, H, W, d]  (real)
   Reshape           ─→  [B, N, d]
   Sum over d (× 1_{d×1}) + scale 1/(N√d)
   │
   a  [B, N]                                     (Eq. 15)
   │
   Row-wise Softmax  ─→  σ(a)  [B, N]            (first row of σ(Ã))

── DFT-based output path (computing O = σ(a) ⊛ V) ──

σ(a)  [B, N] ──Reshape──→ σ̂(a)  [B, H, W]
V     [B, N, d] ──Reshape──→ V̂   [B, H, W, d]

   F2D(σ̂(a))  [B, H, W]  (complex) → conj
   F2D(V̂)     [B, H, W, d]  (complex)
   │
   Broadcast Hadamard ⊙ : F2D(σ̂(a))* ⊙ F2D(V̂)   [B, H, W, d] (complex)
   F⁻¹_2D ─→ σ(a) ⊛ V    [B, H, W, d]  (real)
   Reshape ─→  O          [B, N, d]              (Eq. 16)

   [Post-reweighting variant]   O ← O ⊙ T   [B, N, d]
   │
   (Multi-head merge / Linear projection W_O) ─→ Output  [B, N, C]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Q/K/V and Reweighting Projection

**Function:** 把 token sequence 投影成 query、key、value，以及 input-dependent 的 reweighting 向量。

**Input:**
- Name: `x`
- Shape: `[B, N, C]`
- Source: patch embedding 或上一層 block 輸出

**Output:**
- Name: `Q, K, V, T`
- Shape: 各為 `[B, N, d]`（per head；多頭時為 `[B, h, N, d]`）
- Consumer: 2D reshape 與 BCCB attention score module；`T` 進入 token reweighting

**Processing:**

每個 head 以線性投影 $Q = xW_Q$, $K = xW_K$, $V = xW_V$ 取得三組向量；同時以另一條 input-dependent 線性層加 SiLU 取得 reweighting factor $T = \mathrm{SiLU}(xW_T)$。多頭時每個 head 的 $W_{Q/K/V} \in \mathbb{R}^{C \times d}$；hierarchical 模型會在前兩個 stage 套用 circulant attention，較深層 stage 維持原本的 attention（見 Table 6–9）。

**Key Formulas:**

$$
Q, K, V = xW_Q, xW_K, xW_V; \quad T = \mathrm{SiLU}(xW_T)
$$

**Implementation Details:**

CA-DeiT 的 ablation（Table 5）顯示將 head dimension 設為 $d=1$（搭配大量 heads，使 $h \cdot d$ 仍等於 $C$）效果最佳，比 DeiT-S baseline 提升 0.4%。這是因為 circulant attention 的 score $a_k$ 已是 $N$ 個 query–key inner product 的總和（Eq. 14），等效 head dimension 為 $Nd$，因此即使 $d=1$ 仍有充分容量。

#### 5.3.2 2D Reshape Adapter

**Function:** 在 1D token sequence（`[B, N, d]`）與 2D feature map（`[B, H, W, d]`）之間互相轉換，使 2D DFT 能正確套用。

**Input:**
- Name: `Q, K, V`（或 `σ(a)`）
- Shape: `[B, N, d]`（或 `[B, N]`）
- Source: 線性投影或 Softmax

**Output:**
- Name: `Q̂, K̂, V̂`（或 `σ̂(a)`）
- Shape: `[B, H, W, d]`（或 `[B, H, W]`）
- Consumer: `F2D` / `F⁻¹_2D` 運算

**Processing:**

只是把 spatial 維度 $N$ split 成 $H \times W$，channel 維度 $d$ 保留；論文約定 `F2D, F⁻¹_2D` 的輸入/輸出可視為 1D 序列（reshaping 不顯式畫出）。

**Key Formulas:**

$$
\text{reshape}: \mathbb{R}^{N \times d} \leftrightarrow \mathbb{R}^{H \times W \times d}
$$

**Implementation Details:**

論文未具體說明對 non-square spatial 或非 $2^k$ 解析度的 padding 策略；對於 hierarchical 模型，前兩個 stage 維持完整 spatial 解析度（如 $56 \times 56$、$28 \times 28$），這正是 circulant attention 帶來顯著效率優勢的場景。

#### 5.3.3 BCCB Attention Score (DFT-based Q ⊛ K)

**Function:** 透過 2D DFT 算出 BCCB attention map $\tilde{A}$ 的第一列 $a$，等價於 $Q$ 與 $K$ 的 2D circular cross-correlation 在 channel 維度上求和。

**Input:**
- Name: `Q̂, K̂`
- Shape: `[B, H, W, d]`
- Source: 2D reshape adapter

**Output:**
- Name: `a`
- Shape: `[B, N]`
- Consumer: row-wise Softmax

**Processing:**

依 Eq. 15，先對 $Q̂$ 與 $K̂$ 各做 2D DFT，將 $K$ 的頻譜取共軛後與 $Q$ 的頻譜做 Hadamard product，再做 inverse 2D DFT 得到 $Q \circledast K \in \mathbb{R}^{N \times d}$；接著與 $\mathbf{1}_{d \times 1}$ 內積（即沿 channel 維度求和），最後乘上 scaling factor $1/(N\sqrt{d})$。整體複雜度 $O(N \log N \cdot d)$，遠低於 vanilla 的 $O(N^2 d)$。

**Key Formulas:**

$$
a = \frac{1}{N\sqrt{d}}\left[\mathcal{F}_{2D}^{-1}\!\left(\overline{\mathcal{F}_{2D}(Q)} \odot \mathcal{F}_{2D}(K)\right)\right] \cdot \mathbf{1}_{d \times 1}
= \frac{1}{N\sqrt{d}} (Q \circledast K)\cdot \mathbf{1}_{d \times 1}
$$

**Implementation Details:**

實作上 `F2D` 用 FFT 完成；論文未明示是否使用 `torch.fft.rfftn`（real-input FFT 可省一半計算），the paper does not specify。此步驟對應於以 BCCB 投影替代 dense $QK^\top$，等價於 2D global depth-wise convolution 的 score 計算。

#### 5.3.4 Row-wise Softmax & DFT-based Output (σ(a) ⊛ V)

**Function:** 套用 row-wise Softmax 取得 $\sigma(\tilde{A})$（仍為 BCCB），再以 DFT-based multiplication 算出 $O = \sigma(\tilde{A})V$。

**Input:**
- Name: `a, V̂`
- Shape: `a` 為 `[B, N]`；`V̂` 為 `[B, H, W, d]`
- Source: BCCB score module 與 2D reshape

**Output:**
- Name: `O`
- Shape: `[B, N, d]`
- Consumer: token post-reweighting 或多頭合併線性層

**Processing:**

由於 $\sigma(\tilde{A})$ 仍是 BCCB，由其第一列 $\sigma(a)$ 完全決定。對 $\sigma(a)$（reshape 為 $H \times W$）做 2D DFT 後取共軛，與 $\mathcal{F}_{2D}(V̂)$ 在 spatial dim 廣播相乘（V 多了 channel 維度 $d$），再做 inverse 2D DFT 得到 $\sigma(a) \circledast V \in \mathbb{R}^{H \times W \times d}$，最後 reshape 為 $[B, N, d]$。整體仍為 $O(N \log N \cdot d)$。

**Key Formulas:**

$$
O = \mathcal{F}_{2D}^{-1}\!\left(\overline{\mathcal{F}_{2D}(\sigma(a))} \odot \mathcal{F}_{2D}(V)\right) = \sigma(a) \circledast V
$$

**Implementation Details:**

由 Eq. 17 拆解，本步驟需要 1 次 `F2D`（對 $\sigma(a)$）、1 次 `F2D`（對 $V$）、1 次 element-wise product 與 1 次 `F⁻¹_2D`，貢獻 $N(\log_2 N)(d+1) + 2Nd + N(\log_2 N)d$ FLOPs。Softmax 僅作用於長度 $N$ 的第一列，因此實作上只需對 `a` 做一次 1D Softmax 即可。

#### 5.3.5 Token Reweighting Module

**Function:** 透過輸入相依的 SiLU 門控對 token 強度做縮放，補償 BCCB doubly-stochastic 結構無法凸顯特定 token 的限制。

**Input:**
- Name: `x`
- Shape: `[B, N, C]`
- Source: block 輸入；`T` 由 `Linear W_T + SiLU` 產生，shape `[B, N, d]`

**Output:**
- Name: `V ⊙ T`（pre）或 `O ⊙ T`（post）
- Shape: `[B, N, d]`
- Consumer: pre 進入 BCCB 路徑；post 為最終輸出

**Processing:**

兩種變體：
- Pre-reweighting：在進 attention 前對 value 加權 $O = \mathrm{CirAttn}(Q, K, V \odot T)$（Eq. 19）。
- Post-reweighting：在 attention 結束後對輸出加權 $O = \mathrm{CirAttn}(Q, K, V) \odot T$（Eq. 20）。

Ablation（Table 5）顯示 post-reweighting 略優（80.9% vs 81.0%），因此 CAT 系列預設採用 post-reweighting。在 baseline DeiT-S 上單獨加入 token reweighting 反而下降（80.0%，−0.2），代表其增益主要來自補償 BCCB 結構的限制。

**Key Formulas:**

$$
T = \mathrm{SiLU}(xW_T) \in \mathbb{R}^{N \times d}, \quad
O = \begin{cases} \mathrm{CirAttn}(Q, K, V \odot T) & \text{pre} \\ \mathrm{CirAttn}(Q, K, V) \odot T & \text{post} \end{cases}
$$

**Implementation Details:**

$W_T \in \mathbb{R}^{C \times d}$，與 $W_V$ 同維度但獨立參數；FLOPs 增量約 $0.4$G（CA-DeiT-S：4.4G → 4.8G，Table 5），參數量增加約 2M。論文未說明 $W_T$ 是否與 $W_V$ 共享 head 切分策略，the paper does not specify。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| ImageNet-1K (Deng et al. 2009) | Image classification (1,000 classes) | 1.28M training images / 50K validation images | train / val (no separate test split used) |
| COCO (Lin et al. 2014) | Object detection & instance segmentation | 118K training images / 5K validation images | train / val |
| ADE20K (Zhou et al. 2019) | Semantic segmentation (150 categories) | 20K training / 2K validation images | train / val |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| Top-1 Accuracy (%) | ImageNet-1K classification accuracy | yes |
| FLOPs | Floating-point operations, used as the efficiency proxy alongside accuracy | yes |
| #Params | Model parameter count, reported alongside accuracy/FLOPs trade-offs | no |
| $\text{AP}^b$, $\text{AP}^b_{50}$, $\text{AP}^b_{75}$ | COCO box average precision (overall, IoU=0.5, IoU=0.75) | yes (detection headline) |
| $\text{AP}^m$, $\text{AP}^m_{50}$, $\text{AP}^m_{75}$ | COCO mask average precision (overall, IoU=0.5, IoU=0.75) | no |
| mIoU (%) | Mean Intersection-over-Union on ADE20K semantic segmentation | yes (segmentation headline) |
| Throughput (images/s) / FPS | Inference speed measured on an RTX3090 GPU | no |

### 6.3 Training and Inference Settings

分類訓練設定遵循各 baseline 的原始 recipe，以確保 fair comparison。所有 ImageNet-1K 模型 train from scratch 共 300 epochs，使用 AdamW optimizer (Loshchilov and Hutter 2018)，搭配 cosine learning rate decay，並在前 20 epochs 進行 linear warm-up；初始 learning rate 為 $1\times10^{-3}$，weight decay 為 $0.05$。資料增強與正則化包含 RandAugment、Mixup、CutMix 與 random erasing。預設輸入解析度為 $224^2$，CA-Swin-B 額外提供 $384^2$ 的設定。

COCO 物件偵測使用 Mask R-CNN 框架，遵循 baseline 的 1× 與 3× schedule，FLOPs 在 $1280\times800$ 解析度下計算。ADE20K 語意分割對 PVT 系列搭配 SemanticFPN (Kirillov et al. 2019) decoder、對 Swin 系列搭配 UperNet decoder，FLOPs 在 $512\times2048$ 解析度下計算（涵蓋 encoder + decoder）。

架構層面，circulant attention 作為 plug-in 替換原始 attention module，並採用 conditional positional encodings (Chu et al. 2023) 引入位置資訊；對 hierarchical 模型 (Swin、PVT、CAT)，attention replacement 主要限制於前兩個 stage（詳見 Appendix B 的 Table 6–10）。預設使用 head dimension $d=1$ 並搭配 post token reweighting (Eq. (20))。

效率量測 (Fig. 4) 的 throughput 與 FPS 在 RTX3090 GPU 上測得；the paper does not specify training hardware, batch size, gradient accumulation, mixed precision, EMA, drop path rate, or random seed counts。

### 6.4 Main Results

ImageNet-1K classification — circulant attention 套用於三種代表性 baseline 與專屬 CAT 家族：

| Method | Top-1 (%) | FLOPs | Notes |
| --- | --- | --- | --- |
| DeiT-S (Touvron et al. 2021) | 79.8 | 4.6G | global self-attention baseline |
| **CA-DeiT-S** | **81.0 (+1.2)** | **4.8G** | 本文方法 plug-in 於 DeiT-S |
| PVT-S (Wang et al. 2021) | 79.8 | 3.8G | sparse attention baseline |
| **CA-PVT-S** | **81.7 (+1.9)** | **4.0G** | 以 PVT-L 30% 參數量達同等精度 |
| PVT-L (Wang et al. 2021) | 81.7 | 9.8G | larger sparse attention baseline |
| **CA-PVT-L** | **82.9 (+1.2)** | **10.1G** | — |
| Swin-T (Liu et al. 2021) | 81.3 | 4.5G | local window attention baseline |
| **CA-Swin-T** | **82.2 (+0.9)** | **4.6G** | — |
| Swin-B@$384^2$ | 84.5 | 47.0G | high-resolution baseline |
| **CA-Swin-B@$384^2$** | **85.1 (+0.6)** | **47.1G** | — |
| BiFormer-B (Zhu et al. 2023) | 84.3 | 9.8G | SoTA bi-level routing attention |
| MILA-S (Han et al. 2024b) | 84.4 | 7.3G | SoTA Mamba-style |
| TransXNet-B (Lou et al. 2025) | 84.6 | 8.3G | SoTA dual dynamic token mixer |
| **CAT-T** | **83.6** | **4.3G** | 本文 specialized model |
| **CAT-S** | **84.5** | **7.9G** | 與 TransXNet-B 相近精度但 FLOPs 較低 |
| **CAT-B** | **85.0** | **15.2G** | 與 OverLock-B (85.1, 16.7G) 相近精度 |

COCO Mask R-CNN (1× schedule，節錄 highlight 列)：

| Method | $\text{AP}^b$ | $\text{AP}^m$ | FLOPs | Notes |
| --- | --- | --- | --- | --- |
| PVT-S | 40.4 | 37.8 | 305G | baseline |
| **CA-PVT-S** | **44.2 (+3.8)** | **40.7 (+2.9)** | **269G** | FLOPs 反而下降 |
| PVT-L | 42.9 | 39.5 | 494G | larger baseline |
| **CA-PVT-L** | **46.3 (+3.4)** | **41.9 (+2.4)** | **444G** | CA-PVT-S 即可超越 PVT-L 1.3 box AP |
| Swin-S | 45.7 | 41.1 | 358G | baseline |
| **CA-Swin-S** | **46.8 (+1.1)** | **42.2 (+1.1)** | **361G** | — |

ADE20K semantic segmentation (節錄)：

| Backbone | Decoder | mIoU | FLOPs | Notes |
| --- | --- | --- | --- | --- |
| PVT-T | S-FPN | 35.7 | 158G | baseline |
| **CA-PVT-T** | **S-FPN** | **39.4 (+3.7)** | **135G** | 最大 mIoU gain |
| Swin-S | UperNet | 47.6 | 1038G | baseline |
| **CA-Swin-S** | **UperNet** | **48.6 (+1.0)** | **1040G** | — |

Efficiency (Fig. 4)：在 $1536^2$ 解析度下，CA-DeiT-T 相對 self-attention 達到 $8\times$ FLOPs 縮減與 $7\times$ 實測加速；於 $224^2$ ImageNet 預設解析度下 throughput-accuracy trade-off 最高可達 $1.5\times$ 推論速度，並同時保有更高精度。

### 6.5 Ablation Studies

Ablation 在 ImageNet-1K 以 CA-DeiT-S 為基底進行 (Table 5)：

- **Circulant attention vs. self-attention.** 將 DeiT-S 的 self-attention 直接換為 circulant attention，Top-1 由 79.8% 微降至 79.7% (-0.1%)，FLOPs 由 4.6G 降至 4.4G。此 ablation 直接回答「BCCB 結構是否犧牲表達力」這個關鍵問題，結論為近乎無損。
- **Head dimension $d=1$.** 在 circulant attention 上設 $d=1$ 並改用更多 heads，Top-1 提升至 80.2% (+0.5)，已超越 DeiT-S baseline。論文以 Eq. (14) 解釋：因 attention score 是 $N$ 對 query-key 的 summation，等效 head dimension 為 $Nd$，故 $d=1$ 仍足夠表達。此為 diagnostic 實驗，驗證 circulant attention 與 self-attention 對 head 規劃的需求差異。
- **Token reweighting (pre vs. post).** 加入 token reweighting (Eq. (19)/(20)) 將精度推升至 80.9% (pre) / 81.0% (post)，post-reweighting 微幅勝出並被選為預設。此 ablation 直接針對 BCCB 強制 row/column 同時 sum-to-one 所引入的 saliency 限制，屬 diagnostic。
- **Token reweighting 是否是普遍 trick？** 額外將 token reweighting 套用於原始 DeiT-S（不換 attention），Top-1 僅由 79.8 升至 80.0% (+0.2)，遠小於套在 circulant attention 上的 +0.8。此 control 排除「reweighting 本身就是強招」的解釋，使其成為正當的 component 診斷而非 sanity check。
- **未做的 ablation.** 論文未獨立 ablate (a) 將 circulant attention 限制於前兩 stage 的選擇 vs. 全部 stage、(b) conditional positional encoding 的貢獻、(c) FFT 實作 vs. 直接以 Eq. (11) 形式計算的精度等價性，這些屬 diagnostic 缺口。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — Table 2 right 與 BiFormer-B、TransXNet-B、MILA-S、OverLock-B、FasterViT、VMamba 等 2024–2025 SoTA 比較，CAT-S/B 在相近 FLOPs 下精度相當或更佳。
- [covered] Has cross-task / cross-dataset evaluation — 同時涵蓋 ImageNet-1K classification、COCO Mask R-CNN detection/instance segmentation、ADE20K semantic segmentation 三項任務 (Tables 2–4)。
- [covered] Has ablations that diagnose the new components — Table 5 分別 ablate circulant attention、head dimension、token reweighting，並以 DeiT-S + reweighting 的 control 排除替代解釋。
- [partial] Has a scaling study — 模型 size 上從 T/S/M/L/B 皆有 (Table 2)，且 Fig. 4(a–b) 在 input resolution 從預設到 $1536^2$ 的 sequence-length scaling 展示 $8\times$ FLOPs / $7\times$ 速度優勢；但缺少 dataset scale 或訓練 compute 的 scaling 研究。
- [covered] Has an efficiency / wall-clock comparison — Fig. 4 在 RTX3090 上回報 FLOPs、FPS 與 throughput-accuracy trade-off，含 $1.5\times$ inference speedup 的實測數據。
- [missing] Reports variance / standard deviation / multiple seeds — 所有 Top-1、AP、mIoU 皆為單一數值，未報告 multi-seed 結果或誤差棒。
- [partial] Releases code / weights / data sufficient for reproducibility — 論文標題下提供 `github.com/LeapLabTHU/Circulant-Attention` 的 Appendix 連結，且 Appendix B 完整列出 CA-DeiT/CA-PVT/CA-Swin/CAT 各 variant 的架構表 (Tables 6–10)；the paper does not specify pretrained weight 釋出或訓練 hardware/batch size 等可完全重現的訓練細節。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: ViT 在無外加約束下學到近似 BCCB 的 attention pattern**：**部分支持**。Fig. 2、Fig. 3（page 3–4）提供視覺化證據與相鄰 query shift-invariance 的定性說明，但缺乏跨層／head／資料集的量化指標（如 projection residual、能量比例），「frequently approximate」的強度未被定量界定。
- **C2: Circulant Attention 達成 $\mathcal{O}(N \log N)$ 複雜度且運算範式與 vanilla attention 高度相似**：**支持**。Eq. 17（page 5）給出嚴謹複雜度推導，Fig. 4(a, b)（page 7）顯示 $1536^2$ 下約 8× FLOPs 與 7× wallclock 加速。
- **C3: 作為 plug-in 模組廣泛適用於各類 ViT 架構**：**部分支持**。Tables 2–4（page 5–6）涵蓋 DeiT、PVT、Swin 三種範式且皆有提升，但 PVT 與 Swin 僅替換前兩個 stage，論文宣稱的「廣泛適用」實際範圍受限於早期高解析度層。
- **C4: 在保留全域建模能力的同時優於 handcrafted sparse／local attention**：**部分支持**。Table 2 left（page 5）顯示對 PVT、Swin 一致改善，Table 3 COCO 結果（page 6）的高解析度優勢明顯，但與直接以 GFNet／AFNO 取代 attention 的對照從缺，難以證明優勢來自「保留全域性」而非單純使用 DFT。
- **C5: BCCB 結構先驗本身即為性能來源**：**過度宣稱（overclaimed）**。Table 5（page 7）顯示直接套用 circulant attention 較 DeiT-S 退化 0.1%，需配合 $d=1$ 與 token reweighting 才能反超，論文卻將整體增益歸因於 BCCB 觀察，缺乏對 reweighting 與 $d=1$ 的對照拆解。

### 7.2 Fundamental Limitations of the Method

**雙隨機性瓶頸無法在 BCCB 結構內部解決。** vanilla attention 中 softmax 僅強制 row-stochastic，因此不同 query 可同時 emphasize 少數關鍵 key；但 BCCB 結構同時迫使 row 與 column 之和皆為 1（doubly stochastic），意味「少數 token 吸引大量 attention」這種 saliency-driven pattern 結構性不可實現。作者以外掛式 SiLU token reweighting 補償，但此模組作用於 attention 之外（pre 或 post 乘以 $T$），無法恢復 attention map 內部的 saliency 表達能力，這是方法層級而非工程層級的限制。

**translation-equivariance 被硬編碼進 attention 算子。** BCCB matrix 等價於 circular-padding 的 2D global depth-wise convolution，意味 attention 對輸入的處理在所有空間位置上完全等價（僅依賴相對位置）。對於需要絕對位置或對稱破缺的視覺任務（細粒度空間定位、document parsing、OCR、dense matching 等），此先驗構成 representational ceiling；CPE 能注入部分位置資訊，但 attention 本身的 shift-equivariance 不可破壞。

**circular padding 與自然影像邊界假設不一致。** 2D DFT 的 circular convolution 假設訊號具空間週期性，邊界處的 query 會「看到」對側邊界的 key。對於有明確邊界語義的偵測／分割任務，這是潛在的 noise source；論文僅報告整體 mIoU/AP 提升，未針對影像邊緣區域做分區評估，因此 boundary artifact 的實際代價不明。

**BCCB 假設僅在早期、高解析度、低語義階段成立。** 作者僅在 PVT、Swin 的前兩 stage 替換 attention（Appendix Tables 7–9），暗示後段（low-resolution、high-semantics）的 attention 並不近似 BCCB。這顯示該結構先驗並非 self-attention 的普遍性質，而是 ViT 早期視覺層的局部性質，限制了其作為「self-attention 通用替代」的範圍。

### 7.3 Citations Worth Tracking

- **Rao et al. 2021 (GFNet)**：以 DFT convolution theorem 建立 $\mathcal{O}(N \log N)$ 全域 depth-wise convolution，是與本文最直接的並行設計，閱讀後可判斷 Circulant Attention 相對於既有 frequency-domain mixer 的真實 delta。
- **Guibas et al. 2021 (AFNO)**：提出 input-dependent frequency filters 達成動態 depth-wise convolution，與本文「BCCB attention 動態由 $Q$、$K$ 決定」形成對照，是評估 novelty 邊界的關鍵 reference。
- **Davis 1979 (Circulant Matrices)**：BCCB 的數學基礎，是檢視 Eq. 10–16 推導正確性以及是否存在更緊投影／更穩定 normalization 形式的入口。
- **Han et al. 2024a (InLine / Bridging the divide)**：本文同團隊近作，討論 softmax 與 linear attention 的橋接，與本文的「結構化 attention map」走向相關，可參考其對 attention 表達力的拆解方式。
- **Touvron et al. 2021 (DeiT)**：本文 BCCB 觀察的取樣對象，閱讀其原始訓練設定與 attention 行為可幫助評估 BCCB 觀察是否具普遍性，或僅是 DeiT 特定 inductive bias 的副作用。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 在跨層、跨 head、跨資料集的尺度下，量化 attention map 與其最近 BCCB 投影的 relative residual $\|A - \tilde{A}\|_F / \|A\|_F$ 為何？此距離是否與下游任務性能相關？
- [ ] 若以「vanilla self-attention + 相同 SiLU pre/post-reweighting + $d=1$」為對照組，是否能複現 CA-DeiT 的增益？也就是 BCCB 結構先驗本身是否仍有非平凡貢獻？
- [ ] 為何 PVT、Swin 僅替換前兩 stage？是否曾對 stage 3、4 套用 CA？若效果劣化，是否與後段語義層偏離 BCCB 假設一致？
- [ ] CPE 對 CA 模型增益的貢獻為何？若移除 CPE，CA-DeiT 相對 DeiT 的差距會如何變化？
- [ ] 在訓練設定一致的條件下，CA 相較 GFNet、AFNO、AFFNet 的精度／延遲曲線實際差距為何？
- [ ] $1536^2$ 的高解析度速度優勢能否轉化為更具挑戰性的 dense prediction 任務（如 panoptic segmentation、video object segmentation）的端到端優勢？
- [ ] 在 BCCB 假設下，circular padding 對影像邊界區域的偵測／分割誤差影響如何？以分區（中心 vs. 邊界）AP/mIoU 評估能否揭露 boundary artifact？

### 8.2 Improvement Directions

1. **隔離式 ablation：cleanly 拆解 BCCB、$d=1$、SiLU reweighting 與 CPE 各自貢獻**。可行性最高，僅需在 DeiT-S 上加跑因子化 ablation，即可定量判定增益歸因。論點基礎：Table 5 已顯示 raw CA 退化、需多項組合才反超，現有 ablation 不足以證明 BCCB 為主因。
2. **加入 BCCB-fit 量化指標並按層 gating**。可行性高。在 baseline DeiT 推論時計算每層 $\|A - \tilde{A}\|_F$，據此決定哪些層適合替換為 CA，避免「stage 3/4 不適用」這種啟發式邊界。論點基礎：作者僅替換前兩 stage 已暗示 BCCB 先驗具層級特異性。
3. **以 GFNet／AFNO 為頭對頭 baseline 在同一訓練 recipe 下重跑**。可行性中。需重新訓練若干配置以對齊 augmentation／epoch，但能直接回答「BCCB 框架是否本質上優於既有 frequency-domain mixer」。論點基礎：兩者在 $\mathcal{O}(N \log N)$ 全域 conv 結構上幾乎等價，差別主要在於是否「動態由 $Q$、$K$ 決定」。
4. **改用 zero-padded 2D conv（線性卷積）替代 circular-padded BCCB 並比較**。可行性中。可透過 zero-padded FFT 維持 $\mathcal{O}(N \log N)$ 並消除 boundary artifact，代價為常數倍 FLOPs 增加。論點基礎：自然影像非週期，BCCB 對邊界的處理不符合視覺先驗。
5. **將 reweighting 內化進 attention，而非外掛 Hadamard product**。可行性中低。例如以 frequency-domain 的非均勻濾波改寫 reweighting，使其能影響 attention 內部之 saliency 分布；目標是緩解雙隨機性瓶頸。論點基礎：當前 SiLU 重加權僅修飾輸出 $V$ 或前置縮放，無法改變 attention 矩陣本身的 doubly-stochastic 性質。
6. **引入混合層設計（hybrid stages）：早期 CA、晚期 vanilla 或 linear attention**。可行性中。將現有「前兩 stage 替換」延伸為更系統化的 pattern，並在 dense prediction 任務上驗證。論點基礎：BCCB 為 translation-equivariant，不適合需要絕對位置或語義特異性的後段 high-level 層。
