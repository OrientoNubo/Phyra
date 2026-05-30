<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# GGGS — Geometry-Grounded Gaussian Splatting

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | GGGS |
| Paper full title | Geometry-Grounded Gaussian Splatting |
| arXiv ID | 2601.17835 |
| Release date | 2026-01-27 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2601.17835 |
| PDF link | https://arxiv.org/pdf/2601.17835 |
| Code link | https://github.com/HKUST-SAIL/Geometry-Grounded-Gaussian-Splatting |
| Project page | https://baowenz.github.io/geometry_grounded_gaussian_splatting/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Baowen Zhang | Hong Kong University of Science and Technology | https://baowenz.github.io/geometry_grounded_gaussian_splatting/ | first author |
| Chenxing Jiang | Hong Kong University of Science and Technology | — | co-author |
| Heng Li | Hong Kong University of Science and Technology | — | co-author |
| Shaojie Shen | Hong Kong University of Science and Technology | — | co-author |
| Ping Tan | Hong Kong University of Science and Technology | https://pingtan.people.ust.hk/index.html | senior author / likely corresponding |

### 1.2 Keywords

Gaussian Splatting, Stochastic Solids, Shape Reconstruction, Volume Rendering, Depth Rendering, Multi-view Consistency, Surface Reconstruction

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| 3D Gaussian Splatting (Kerbl et al. 2023) | base model | Provides the Gaussian primitive rasterization framework that this work re-grounds in stochastic-solid theory. |
| Objects as Volumes (Miller et al. 2024) | influence | Stochastic-solid volume rendering theory used to derive the attenuation coefficient and vacancy field for Gaussians. |
| PGSR (Chen et al. 2024) | baseline | Multi-view geometric regularization GS surface method, primary reconstruction baseline compared in qualitative/quantitative results. |
| 2DGS (Huang et al. 2024) | baseline | Replaces 3D Gaussians with 2D primitives for surface alignment; baseline whose normal-consistency loss is reused here. |
| GOF (Yu et al. 2024c) | baseline | Gaussian Opacity Fields with median-depth heuristic; contrasted as discrete-transmittance method that this paper supersedes. |
| NeuS / VolSDF (Wang 2021; Yariv 2021) | predecessor | Geometry-grounded NeRF predecessors that inspire equipping GS with a canonical geometry field. |
| GFSGS (Jiang et al. 2025) | concurrent | Concurrent work that also leverages stochastic solids, but to construct 2D surfels rather than re-derive 3D GS rendering. |

## 2. Research Overview

### 2.1 Research Topic

本文研究如何從 Gaussian Splatting (GS) 重建高保真且具多視角一致性的 3D 表面幾何。傳統 GS 雖在新視角合成 (novel view synthesis) 上具備即時效率,但其原語 (primitive) 並未內建表面定義,既有方法多以啟發式深度 (heuristic depth) 規則從輻射場萃取幾何,導致跨視角不一致、易受 floater 干擾、邊界鋸齒明顯。作者引入 Miller et al. 2024「Objects as Volumes」的隨機固體 (stochastic solid) 理論,證明 Gaussian primitive 在適當的衰減係數下可被嚴格視為一種隨機固體,使 GS 的光柵化渲染與 NeRF 式體渲染在數學上等價,從而首次為 GS 推導出標準的幾何場 (canonical geometry field)。在此基礎上,他們設計連續透射率下的中位數深度 (median depth) 計算與閉式梯度,提升幾何萃取精度並保留 GS 的優化效率。

### 2.2 Domain Tags

- Computer Vision
- Computer Graphics
- 3D Reconstruction
- Neural Rendering

### 2.3 Core Architectures Used

- **3D Gaussian Splatting (3DGS)**:作為基礎場景表徵,將場景以一組各向異性 3D Gaussian primitive 表示並透過 rasterization 進行即時渲染,本文在其上重新詮釋 primitive 的幾何意義。
- **Stochastic Solid Volume Rendering (Miller et al. 2024)**:提供以 vacancy $v(x)$ 與 attenuation coefficient $\sigma$ 為核心的隨機固體體渲染理論,本文用以為 Gaussian primitive 推導出唯一的 vacancy 表達式 $v(x)=\sqrt{1-G(x)}$ 並建立 canonical geometry field。
- **Continuous-Transmittance Median-Depth Renderer**:本文新提出的深度渲染模組,利用沿光線連續且單調的透射率,以 binary search 取得 $T(t_{med})=0.5$ 的中位深度,並推導出對所有貢獻 Gaussian 的 closed-form 梯度。
- **RaDe-GS Local Affine Approximation**:用來估計每顆 Gaussian 沿光線的峰值點 $t^*_i$,作為 stochastic-solid 衰減剖面分段定義 (Eq. 12) 的依據。
- **Mip-Splatting 3D Filter / GOF Densification / PGSR Multi-view Regularization & Exposure Compensation / 2DGS Normal-Consistency Loss**:沿用既有 GS 變體的工程組件,分別處理抗鋸齒、原語密化、跨視幾何一致性、曝光補償與法向一致性監督。
- **TSDF Fusion (Open3D) / Marching Tetrahedra**:後處理階段的網格萃取器,分別用於 DTU 物件級與 Tanks & Temples 大場景的 mesh 重建,且 Marching Tetrahedra 採用 $T<0.5$ 作為 inside/outside 判定。

### 2.4 Core Argument

作者鎖定的根本原因是:Gaussian Splatting 在設計上只是一組用於光柵化合成顏色的非物理原語,並沒有像 SDF/occupancy 那樣的標準幾何場 (canonical geometry field),因此所有現有 GS 表面重建方法都被迫以啟發式 (heuristic) 規則從輻射場推測深度——例如以 alpha 加權平均、或在離散透射率上取 T=0.5 的位置作為中位深度。這些啟發式做法會引入兩種結構性瑕疵:第一,深度依視角而定,在不同相機間缺乏一致性,使 floater 等視角相關偽影主宰幾何訊號;第二,因為透射率隨單顆 Gaussian 階梯式跳變,T=0.5 會被「卡」到單一 Gaussian 上,鄰近像素就可能落到不同 Gaussian,造成鋸齒狀深度。要根治這兩個問題,必須讓 Gaussian 原語本身擁有一個可被體渲染積分的連續幾何場;也就是說,問題不在「怎麼從 GS 解讀深度」,而是「GS 是否本來就是一種具幾何定義的體」。作者因此援引 Miller et al. 2024 的隨機固體理論,證明在唯一決定的空缺函數 v(x)=√(1−G(x)) 之下,單顆 Gaussian 的體渲染與其原始光柵化色彩完全一致——這把 GS 重新詮釋為帶有連續衰減剖面的隨機固體。隨之而來的中位深度因此落在視角無關的 0.5 等值面上,對 floater 更穩健;連續透射率讓 T=0.5 的解可由二分搜尋取得,且作者推導出對所有沿光線 Gaussian 的閉式梯度,讓深度監督平滑地分散到所有貢獻原語,提供更密集的優化訊號。整套方法在邏輯上是必要的,因為唯有從理論層面把 GS 接合到幾何場,才能同時解決多視角不一致、邊界鋸齒與梯度稀疏三個由啟發式深度衍生的根因。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(120 words)

論文標題 "Geometry-Grounded Gaussian Splatting" 已預示核心訴求：將 Gaussian Splatting 從一個原本只為 novel view synthesis 設計的 representation，重新「接地」到一個有原則的幾何基礎上。Abstract 在第一段就鋪陳出這個張力：GS 在影像合成上品質與效率俱佳，但要從 Gaussian primitives 抽出 shape 仍是 open problem；現有方法因 geometry parameterization 不足與 approximation，產生 multi-view 不一致與對 floaters 敏感的問題。

接著 Abstract 提出本文的關鍵理論宣稱 — Gaussian primitives 等價於某種 stochastic solids — 並把這個等價直接轉化為方法論主張：以此為基礎，可以把 Gaussians 當作 explicit geometric representation 直接處理，並利用 stochastic solids 的 volumetric 性質，rendering 出高品質的 depth maps 來抽取細節幾何。最後一句承諾在 public datasets 上達到 GS-based methods 中最佳的 shape reconstruction 結果，建立讀者對後續實驗的期待。

整個 Abstract 的敘事策略是「問題 → 理論橋樑 → 工程結果 → 實驗背書」，為 §1 Introduction 把這條 NeRF-style geometry-grounded 哲學移植到 GS 的論證鋪好路。

### 3.2 Introduction

(680 words)

Introduction 採用三段式 funnel：先從更廣的 multi-view reconstruction 領域切入（VR、自駕、機器人），再聚焦到 NeRF 系列（VolSDF、NeuS）所代表的 geometry-grounded radiance fields 哲學 — 從 SDF / occupancy 等 canonical geometry field 出發，rendering formulation 由幾何推導而來，因此能保證 cross-view 一致；但缺點是 dense ray sampling 帶來巨大訓練/推論成本。

接著作者把 Gaussian Splatting 當作對立面引入：rasterization 帶來速度與即時 novel view synthesis 的優勢，但 GS 沒有內生的 surface 概念，後續延伸方法（SuGaR、PGSR、2DGS、GOF 等）只能用 heuristic rules 從 radiance field 抽 depth/surface，導致 cross-view 不一致並對 floaters 敏感。Figure 1 的 side-by-side 比較被引用作為視覺證據，主張只要有 principled 的幾何基礎，就能拿到更高保真度的 reconstruction。

論文的核心構想在第三段揭曉：作者要把 geometry-grounded radiance fields 的哲學「移植」到 Gaussians 上，方法是借助 Miller et al. 2024 的 *Objects as Volumes* 給出的 stochastic 詮釋，證明 rendering 一個 Gaussian primitive 與 rendering 一個適當定義的 stochastic solid 在數學上是等價的（Section 4.1）。這個等價首次讓 GS 與 NeRF-based methods 共用同一個 rendering formulation，因此可以為 Gaussian primitives 推導出一個 geometric field，並進一步發展出近似 isosurface 的 depth-rendering 方法（Section 4.2），帶來 multi-view 一致與對 floaters 的 robustness。

第四段以 Figure 2 為座標，把 depth pipeline 的差別講清楚：先前方法把 median depth 定義為 transmittance 跌到 0.5 的位置，但因 transmittance 是 step-wise，無法捕捉重疊 Gaussians 的聯合效應，造成 jagged depth steps；stochastic solids 將 attenuation 在每個 primitive 內建模為連續，得到 smooth transmittance，因而能產生更細緻的 depth maps。實作上利用 transmittance 單調性以 binary search 找 0.5 交點，並針對 median depth 對所有沿光線 Gaussians 參數導出 closed-form 梯度，使 backpropagation 高效。

最後 Introduction 收於三條條列式 contributions：(i) 證明 Gaussian primitives 可視為 stochastic solids 並提供 shape reconstruction 的理論指引；(ii) 基於該理論提出 depth map rendering 與 optimization 的有效方法；(iii) 大量實驗顯示本法在 GS-based methods 中達到最佳 reconstruction accuracy，同時保持 GS 的 optimization efficiency。這三點同時為 §2 Related Work 把後續對比軸線（NeRF/SDF 派 vs. GS 派、heuristic depth vs. principled depth）以及 §4 方法章的兩個小節範圍 (4.1 理論等價、4.2 depth rendering) 做了明確錨定。

### 3.3 Related Work / Preliminaries

(1100 words)

§2 Related Work 與 §3 Preliminary 共同負責把讀者放到正確的技術座標系中。§2 分成兩個正交軸：2.1 Continuous Radiance Fields 從 NeRF 主幹出發，依「品質提升」與「效率提升」兩條支線整理 — Mip-NeRF / Mip-NeRF 360 解 anti-aliasing 與 unbounded scenes，Plenoxels、SVRaster、Instant-NGP 用 explicit grid / hash 加速；接著轉向 surface-aware 系列（VolSDF、NeuS、UNISURF、Neuralangelo、GeoSVR），強調這條線雖然 geometry 品質高，但 ray marching 帶來的時間開銷是其共同弱點。特別地，作者在這節主動引入 *Objects as Volumes*（Miller et al. 2024）作為理論背景，預告它是後續方法章橋接 GS 與 stochastic solids 的關鍵工具。

2.2 Primitive Based Representations 則聚焦 GS 家族：先回顧 3DGS 主軸，再條列 Mip-Splatting (anti-aliasing)、LightGaussian (compression)、VastGaussian (large-scale) 等 NVS 改進；隨後進入與本文最相關的 surface reconstruction 子線 — SuGaR / NeuGS 用 surface-aligned Gaussians、2DGS / Quadratic GS 改用 2D primitives、GFSGS 已嘗試結合 stochastic solids、3DGSR / GSDF 引入 implicit SDF、PGSR 加 multi-view 幾何 regularization。本節終結於一個尖銳的論點：所有這些方法的 depth extraction 仍然 heuristic，導致 noisy depth 與 weak supervisory signal，並把這個 gap 收攏為一個 fundamental question — Gaussian representations 是否能像 NeRF-based methods 一樣支持 intrinsic 的幾何概念？這個問題直接定義了後續方法章要回答的目標。

§3 Preliminary 則是純粹的工具箱章。3.1 Gaussian Splatting 給出 3D Gaussian 的標準參數化（opacity $o$、covariance $\Sigma$、center $\mathbf{x}_c$），介紹 local affine approximation 如何把 3D Gaussian 投影為 2D Gaussian，並寫出 2D opacity $\alpha(\mathbf{u})$ 的 closed-form；alpha-blending 的細節留給 supplementary。

3.2 Objects as Volumes 是更關鍵的鋪陳：作者直接引述 Miller et al. 2024 的核心結論 — 對一個 stochastic opaque solid，給定 occupancy $O$ 與 vacancy $v = 1-O$，attenuation coefficient 可由 vacancy 的對數梯度導出：
$$\sigma(\mathbf{x}, \omega) = |\omega \cdot \nabla \log v(\mathbf{x})| = \frac{|\omega \cdot \nabla v(\mathbf{x})|}{v(\mathbf{x})}$$
進而給出 free-flight distribution $p(t) = T(t)\sigma$ 與 transmittance $T(t)$ 構成的 volume rendering 公式。本節最後一段把整本論文的論證軸線一刀挑明：若把 3D Gaussian primitive 視為 stochastic solid 並設計合適的 $\sigma$，則其 volume rendering 應與其 rasterization rendering 等價 — 而這個等價，正是 §4.1 要證明的目標。

§2 與 §3 合起來在敘事上完成三件事：(a) 把 Gaussian Splatting 的 surface reconstruction 線在現有研究地圖上釘出座標，並指出共通弱點是 heuristic depth；(b) 引介 Objects as Volumes 作為等候出場的理論工具，把它從 §2 的相關工作收編到 §3 的 preliminary 工具箱；(c) 提示讀者，下一章 (§4 Method) 會以「重定義 Gaussian 的 attenuation coefficient」為支點，撬動整個 GS-based reconstruction 的理論基礎。讀完這兩節，讀者已具備：3D/2D Gaussian 的精確定義、stochastic solid 的 rendering 方程、以及為什麼這兩個世界會在本論文中相遇的動機。

### 3.4 Method (overview narrative)

(1500 words)

§4 Method 在敘事結構上是 "證明 → 應用 → 工程化" 的三拍子：4.1 確立 Gaussian primitive 與 stochastic solid 的等價性 (理論)、4.2 在這個等價之上設計新的 depth-rendering 方法並論證其優勢 (應用)、4.3 描述如何把這個 depth 嵌入到實際 optimization pipeline 中 (工程實踐)。整章從一條最小敘事 — 「先處理一個 Gaussian primitive，再延伸到多個」 — 展開。

4.1 Gaussian Primitives as Stochastic Solids 的目標是回答 §3 末尾抛出的核心命題：能否找到一個適當的 attenuation coefficient $\sigma$，使一個 Gaussian primitive 在 stochastic solid 體積渲染下的色彩，等同於 Gaussian Splatting rasterization 的色彩？論文以單一 ray 為基準，先寫出 GS 對單一 Gaussian 的 rendered color $C = c \cdot G(t^*)$，其中 $t^*$ 是 ray 上 Gaussian 響應極大值點。為了讓 attenuation coefficient 唯一決定，作者加入三條溫和的物理 / 數學約束：occupancy 與 Gaussian 響應同序、occupancy 在遠處趨於 0、occupancy 對 $\mathbf{x}$ 可微。在這些約束下，作者導出唯一解 $v(\mathbf{x}) = \sqrt{1 - G(\mathbf{x})}$。Figure 3 視覺化了這個結果：把 $G$ 直接 rasterize 出的 2D 投影，等同於把 stochastic solid（其 vacancy 場為 $\sqrt{1-G}$）以 Equation 3 的 $\sigma$ 進行 volume rendering。這個結果的份量在於：它讓 GS 與 NeRF/VolSDF 派系第一次共享同一個 volume rendering formulation，使得「為 Gaussian 抽出 geometric field」這件事從 heuristic 變成從 vacancy 場的 isosurface 自然衍生。

4.2 Depth from Stochastic Solids 把上述理論轉化為可計算的 depth pipeline。先承襲 PGSR 等先前工作以 median depth $t_{med} = T^{-1}(0.5)$ 為幾何 regularizer 的目標；接著在「不同 Gaussians 的 ray 事件相互獨立」這個與 Blanc 2025、Condor 2025 一致的假設下，將總 transmittance 寫為 per-primitive 乘積 $T(t) = \prod_i T_i(t)$，並導出每個 Gaussian 在 ray 上的分段 closed-form：在 $t \le t_i^*$ 時 $T_i(t) = v_i(t)$，在 $t > t_i^*$ 時 $T_i(t) = v_i(t_i^*)^2 / v_i(t)$（推導留 supplementary）。這個分段公式繼承了 stochastic solid 的連續 attenuation profile，因此能描述「光線穿過 Gaussian 表面之前 / 之後」對 transmittance 的不對稱貢獻。

接著的 Discussion 子節是方法章的解釋核心：為什麼這個 median depth 帶來更好的 multi-view consistency？論點是 — 當 ray 上 transmittance 跌到 0.5 的位置位於主要貢獻 Gaussians 的響應峰之前時，整條 ray 的 transmittance 會與全 3D vacancy field 重合（Figure 6），因此 median depth 自然落在一個 view-independent 的 0.5-level isosurface 上。這個情境因為 optimization 會把高 opacity Gaussians 聚集到 surface 附近，故為常態。Figure 4、Figure 5 進一步比較不同 depth 定義：alpha-weighted expected depth 在前景/背景邊界會 interpolate 出 blurred silhouette；先前 GS-based 方法的 median depth 因為 transmittance 是 step-wise 而會 snap 到單一 Gaussian 上，產生 jagged 與 staircasing；本文的 stochastic-solid formulation 給出 smooth transmittance function，能同時保留 sharp boundary 並消除 staircasing。

4.2.2 Implementation 把演算法落地。Equation 10 並無 closed-form 解，因此 forward pass 利用 $T(t)$ 的單調性，以 binary search 找 0.5 crossing；backward pass 則導出 implicit-function gradient
$$\frac{\partial t_{med}}{\partial \theta} = -\frac{\partial T(t_{med}; \theta)}{\partial \theta} \Big/ \frac{\partial T(t; \theta)}{\partial t}\bigg|_{t=t_{med}}$$
並指出此梯度會分散到 ray 上所有貢獻的 Gaussians — 這與先前方法只把 median depth 的梯度施加在單一 Gaussian 上有根本差別，提供更稠密的 supervision，是 multi-view consistency 改善的另一個動力來源。

4.3 Optimization with Stochastic Solids 是工程化收尾：訓練同時使用 photometric loss、normal consistency loss、PGSR 的 multi-view regularization；為了維持 GS 速度，RGB 與 normal 仍以標準 GS approximation 渲染，僅將新的 stochastic-solid depth 用於幾何 regularization。作者明示這是一個 efficiency-driven 的折衷，並在最後一段把「將 volumetric formulation 推到 RGB 與 normal」放進 future work，為 §6 結論章預留接續話題。整章因此在敘事上同時完成三件事：建立等價性的數學基礎、把它兌現為 multi-view 一致的 depth、並用最小工程改動把它嵌入既有 GS 訓練 pipeline。

### 3.5 Experiments (overview narrative)

(700 words)

§5 Experiments 開頭以一句話宣示比較範圍：在多個 public datasets 上與 SOTA 對比。實作細節先交代：以 RaDe-GS 估計每個 Gaussian 的 ray 上極大值點 $t_i^*$、依 gsplat 採用 warp-level reductions 加速梯度累積、引入 Mip-Splatting 的 3D filter（不含其 2D filter）、densification 沿用 GOF、exposure compensation 沿用 PGSR、multi-view regularization 以 custom CUDA kernel 實作；作者並承諾開源。

評估 datasets 為 DTU 標準 15 場景（指標：Chamfer Distance）與 Tanks & Temples 6 場景（指標：F1-score）。Mesh 抽取在 DTU 用 TSDF fusion (Open3D)、在 TnT 大尺度場景用 Marching Tetrahedra；後者引入 GOF 啟發的 indicator function — 若一個點在任一訓練視角下 transmittance 落到 0.5 以下則視為 inside，否則為 outside。

5.1 Reconstruction Comparison 將本法置於 implicit (NeRF / VolSDF / NeuS / Neuralangelo) 與 explicit (3DGS / 2DGS / GOF / 3DGSR / RaDe-GS / GFSGS / PGSR / GeoSVR) 兩個世界的座標中。在 DTU 上，PGSR 與 GeoSVR 因 multi-view regularizer 已將精度推到接近 implicit 等級；本法搭配同樣的 regularization 後，達到 0.47 mean Chamfer，與 GeoSVR 持平並優於所有其他 GS-based 方法。在 TnT 上，本法以 0.60 F1-score 顯著勝過所有 GS-based baselines（包含 GeoSVR 0.56、PGSR 0.52），作者把這個優勢直接歸因於 §4 的 depth-rendering formulation：能呈現更精細的 geometric details、enforced view-consistent geometry、並對 floaters robust。Figure 7、Figure 9、Figure 10 提供視覺佐證。在運行時間上，本法在相同 iteration 數下比 GeoSVR (15 vs 53 min) 與 PGSR (25 vs 30 min) 快，慢於最快的 baselines 主要是因為 binary search 與 multi-view term 的額外開銷；作者點名「收緊 binary search 初始 depth interval」為可預見的加速空間，並列入 future work。

5.2 Multi-view Consistency 是回到核心論點的驗證實驗。作者定義 per-pixel cycle reprojection error：以 reference view 渲染 depth、將 pixel back-project 到 3D、投影到 neighbor 取對應 depth，再 back-project 與 reproject 回 reference 視角，量測原始位置與往返後位置的 Euclidean distance。比較對象為 PGSR (planar-based depth) 與 RaDe-GS (Gaussian ray-wise maximizer) — 並對 RaDe-GS 加上同樣的 multi-view regularization 以求公平。Figure 8 展示沿訓練 iteration 的 cycle error 演化：本法初始化更佳、收斂更快，並在 30K iteration 達到最低 reprojection error；其他兩法因 floaters 進一步惡化不一致性。這直接呼應 §4.2 Discussion 對 stochastic-solid median depth 之 multi-view 一致性的理論預測。

5.3 Ablation Study 在 TnT 上拆解貢獻來源（Table 3）：geometric multi-view term $L_{gc}$ 在本法中只帶來 marginal 增益，因為新的 depth formulation 已內生提供強 multi-view consistency；normal consistency loss 與 exposure compensation 則一致提升品質；最後與 PGSR、RaDe-GS 在相同 regularizer 配方下對比，本法仍勝出，說明關鍵差異不在 regularization，而在 depth-rendering formulation 本身。整章因此用「主結果 → 多視角一致性微觀驗證 → ablation 切片」三段式論證，扣住 §4 的兩個聲明：精度更高、跨視角一致性更強。

### 3.6 Conclusion / Limitations / Future Work

(330 words)

§6 Conclusion 的論文本體部分極短，僅一段：再次提綱挈領地把貢獻收回兩條 — 「揭示 Gaussian Splatting 的 intrinsic geometry，方法是把 Gaussian primitives 視為 stochastic solids 並設計合適的 attenuation function，使 volume rendering 與 rasterization rendering 等價」、以及「stochastic theory 因此讓 depth rendering 從 heuristic 提升為 principled 程序」，並聲明實驗顯示 SOTA。作者沒有額外重述每張 table 的數字，而是把這篇論文壓縮成「等價性 → principled depth → 最佳精度」的三步論證，與 Abstract 形成首尾呼應。

Limitation 與 Future Work 則被作者拆到 supplementary 的 §E。論文揭示了三個誠實的不足：(i) 為了維持 GS 的速度優勢，本法只在 depth 上採用 stochastic 體積渲染，RGB 與 normal map 仍走標準 GS approximation；作者預期將 stochastic theory 進一步整合進既有的 volume rendering 方法（如 Blanc 2025、Kheradmand 2025）能進一步提升 reconstruction 品質。(ii) Median depth 的 binary search 以固定 depth interval 初始化，這個 interval 必須足夠寬，導致 search step 數變多進而拖慢訓練；對 large-scale 場景，真實 median depth 甚至可能落在預設範圍之外，影響 optimization；adaptive bracketing 是明確的後續方向。(iii) 在 Marching Tetrahedra 階段，雖然 vertex placement 是 Gaussian-aware 的，後續的 3D Delaunay triangulation 仍是通用做法；對 thin / near-planar 結構往往需要更稠密的 vertices，因此設計 Gaussian-specific 的 tetrahedralization 與 refinement 策略是有意義的開放議題。

最後作者把更宏觀的 future work 拋出：既然本論文已經把 Gaussian-based 與 NeRF-based reconstruction 在 rendering formulation 上接通，未來可以將 Neuralangelo 等 NeRF 派系的 geometric regularization 直接借用到 GS-based methods，預期能進一步提升 shape quality。這同時把全文收尾於一個更大的研究地圖上：本論文的等價證明，是 GS 與 NeRF 兩派長期分流之後的一座可雙向通行的橋。

## 4. Critical Profile

### 4.1 Highlights

- 提出首個將 Gaussian primitive 嚴謹接合到 stochastic solid 理論的推導,證明 vacancy $v(x)=\sqrt{1-G(x)}$ 是唯一滿足三項約束 (occupancy 隨 $G$ 單調、遠處 $\to 0$、可微) 的解 (page 4, Eq. 6 與 supplementary §G)。
- 在此理論下,單顆 Gaussian 的 volume rendering 與其原始 rasterization 完全等價 ($c\,G(t^*)=c(1-v(t^*)^2)$),使 GS 與 NeRF 式渲染在數學上首次合流 (Figure 3, Eq. 7-8)。
- 將離散透射率改寫為連續形式 $T_i(t)$ (Eq. 12),解決了「$T=0.5$ 卡在單顆 Gaussian 上、相鄰像素跳到不同 Gaussian」造成的鋸齒深度問題 (Figure 5, §4.2.1 Discussion)。
- 推導出 median depth 對所有沿光線 Gaussian 參數的閉式梯度 $\partial t_{med}/\partial\theta = -(\partial T/\partial\theta)/(\partial T/\partial t)|_{t_{med}}$,讓深度監督密集分散到所有貢獻原語,而非單一 Gaussian (Eq. 13, supplementary §I)。
- 在 Tanks & Temples 6-scene subset 取得 mean F1-score 0.60,顯著領先 PGSR (0.52)、GeoSVR (0.56)、GFSGS (未列入但同期) 等 GS 方法 (Table 2)。
- 在 DTU 15-scene 取得 mean Chamfer Distance 0.47,與 explicit voxel 方法 GeoSVR (0.47) 並列最佳,並接近 implicit Neuralangelo (0.61) (Table 1)。
- 訓練時間 15.0 min (20k iter) / 25.3 min (30k iter),比 GeoSVR (53.3 min) 與 PGSR (30.5 min) 更快,顯示理論重構未犧牲 GS 的優化效率 (Table 1)。
- Cycle reprojection error 在 7K-30K iterations 全程低於 PGSR 與 RaDe-GS+multi-view,且收斂更快、覆蓋率更高 (Figure 8, Figure 13)。
- 在 Mip-NeRF 360 dataset 上,搭配 spherical Gaussian appearance model 後 indoor PSNR 達 32.18,逼近 RayGaussX (32.43),顯示理論可組合而非與 NVS-導向的方法互斥 (Table 4)。
- Forward pass 用 5 次 8-segment 平行二分搜尋取代逐次 mid-point,將深度誤差壓到 $0.8\times 8^{-5}\approx 2.4\times 10^{-5}$,等效於 15 次 binary-search iterations 但只需 5 次 traversal (supplementary §A.1)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 為維持效率,**只在深度通道採用 stochastic-solid 體渲染,RGB 與 normal 仍走 rasterization 近似**,作者承認這是內部不一致的折衷,並表明完整體渲染應可進一步提升精度 (§4.3, §E "Limitation and Future Work")。
- Binary search 採用固定初始區間 $r=0.4$,**對大尺度場景真實 median depth 可能落在區間外**,造成優化失效;作者點名「adaptive bracketing」為未來工作 (§E)。
- Marching Tetrahedra 中頂點放置雖 Gaussian-aware,**後續 Delaunay triangulation 仍是 general-purpose**,薄板與近平面結構需要密集頂點才能重建 (§E)。
- 雖宣稱橋接 Gaussian 與 NeRF 重建,**但未實際引入 NeRF 系列的 geometric regularization (例如 Neuralangelo 的 numerical gradient)**,作者將此列為未來工作 (§E)。

#### 4.2.2 Phyra-inferred

- **DTU 的提升完全消失於 GeoSVR 對比**:Ours (20k) 0.47 與 GeoSVR 0.47 完全並列 (Table 1),意味著在這個 dataset 上理論重新詮釋並未帶來實質精度優勢,真正的領先只出現在 TnT;論文未討論為何同樣的 stochastic-solid 公式在 DTU 失去效用。
- **Ablation 無法分離「連續透射率」、「閉式梯度」與「multi-view regularization」三者的貢獻**:Table 3 只切換 $L_{gc}$、$L_n$、exposure 三個正則項,但這些都是 PGSR 借來的;論文核心的兩項理論貢獻 (連續 $T_i(t)$ vs 階梯式、閉式 $\partial t_{med}/\partial\theta$ vs 單一 Gaussian 梯度) 從未被單獨消融,因此無法判斷 0.60 F1 中有多少來自理論、多少來自借用的 regularizer。
- **「view-independent 0.5-isosurface」是條件性結論而非定理**:§4.2.1 自承此性質僅在「overall transmittance crossing $T=0.5$ occurs before the peak of the contributing Gaussians」時成立,但作者只用「optimization clusters high-opacity Gaussians near the surface」這個經驗陳述支撐,沒有量化在 floater 嚴重或薄板場景中此前提失效的比例。
- **獨立性假設 (Eq. 11) $T(t)=\prod_i T_i(t)$ 在實務上多被違反**:GS 優化會讓多顆 Gaussian 在表面附近重疊,光線「撞擊不同 Gaussian 是統計獨立事件」的前提不嚴格成立,但論文僅引用 Blanc 2025/Condor 2025 一筆帶過,未對假設違反做敏感度分析。
- **缺少與同期 GFSGS 的直接比較**:GFSGS (Jiang et al. 2025) 同樣援引 stochastic solids,且在 DTU 取得 0.58 (Table 1) 但 TnT 數據完全沒列入 Table 2,而它正是最直接的同期競爭者;這個遺漏使 TnT 上的領先論述存在缺口。
- **Mip-NeRF 360 的 NVS 結果暴露純體渲染的代價**:Ours 在 outdoor 取得 PSNR 25.09,落後 RayGaussX 的 25.24;只有加上 RayGaussX 的 spherical Gaussian appearance model (Ours SG) 才能逼近,顯示「principled geometry」與「high-fidelity novel view synthesis」之間仍有 trade-off,而非全面雙贏 (Table 4)。
- **Binary search 帶來顯著常數成本,但未量化其於每像素的 FLOPs/latency overhead**:supplementary §A.1 描述 5 次 8-segment traversal 等效 15 次 binary-search iteration,可是與單純取最近 $T<0.5$ Gaussian 中心的最樸素 baseline 相比,深度精度 / 速度 trade-off 曲線完全沒有報告。

### 4.3 Phyra's Judgment (summary)

本文真正新穎的部分是「將 Gaussian primitive 嚴格證明為一種 stochastic solid」這個理論橋接,而非由此推得的工程結果——後者更像是把這個橋接的最低風險推論 (連續 $T_i(t)$ + binary search + 閉式梯度) 套到既有 PGSR/RaDe-GS 框架上。實驗顯示理論翻譯為精度提升的程度其實有限:DTU 與 GeoSVR 並列、TnT 領先但缺與最直接的同期 GFSGS 對比、NVS 落後 RayGaussX。核心未解的問題是:既然作者只把 stochastic-solid 公式應用到深度,RGB/normal 仍是 rasterization,則「geometry-grounded」的標籤是否名實相符,以及在完整體渲染下精度與效率的真正上下界,目前的實驗都還沒回答。

## 5. Methodology Deep Dive

### 5.1 Method Overview

GGGS is a two-phase method. **Phase 1** is a theoretical re-grounding: starting from Miller et al.'s stochastic-solid framework — where a solid is parameterized by a vacancy field $v(x) = 1 - O(x)$ and the attenuation coefficient is $\sigma(x,\omega) = |\omega \cdot \nabla v(x)| / v(x)$ (Eq. 3) — the authors impose three constraints (occupancy monotone in $G(x)$, vacancy $\to 1$ far from the center, differentiability) and derive the **unique** vacancy that makes the stochastic-solid volume rendering of a single Gaussian identical to its rasterized color: $v(x) = \sqrt{1 - G(x)}$ (Eq. 6). This identity (Eqs. 5, 7, 8) re-interprets a GS primitive as a continuous geometric field rather than a non-physical splat, supplying GS with the "canonical geometry field" that NeuS/VolSDF have but vanilla GS lacks.

**Phase 2** turns that theory into a depth renderer. Depth is defined as the median-transmittance crossing $t_{med} = T^{-1}(0.5)$ (Eq. 10). Under the new vacancy, the **per-Gaussian transmittance** $T_i(t)$ has a piecewise closed form around the Gaussian's ray-wise peak $t^*_i$ (Eq. 12), and assuming statistical independence of ray–Gaussian intersections, the total transmittance factorizes as $T(t) = \prod_i T_i(t)$ (Eq. 11). Because $T(t)$ is now smooth and monotone, the forward pass locates $t_{med}$ by an iterative binary search (5 passes × 8 segments, final error $\le 2.441 \times 10^{-5}$). The backward pass uses a **closed-form gradient** (Eq. 13)

$$
\frac{\partial t_{med}}{\partial \theta} = - \frac{\partial T(t_{med}; \theta)/\partial \theta}{\partial T(t;\theta)/\partial t \big|_{t = t_{med}}}
$$

that propagates depth supervision to **all** contributing Gaussians along the ray, in contrast to prior methods where the gradient is pinned to the single Gaussian containing the $T=0.5$ jump.

To preserve GS's optimization speed, only **depth** is rendered with the volumetric formulation; RGB and normals retain the standard GS rasterized approximation. This is presented as a deliberate efficiency trade-off, with full volumetric RGB/normal rendering left as future work.

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input
  Multi-view images               [V, H, W, 3]
  Camera intrinsics/extrinsics    [V, ...]
  Scene Gaussian parameters θ:
      centers      x_c            [N, 3]
      opacities    o              [N, 1]
      scales       s              [N, 3]      (diagonal of S in Σ = R S S^T R^T)
      rotations    q (quaternion) [N, 4]
   │
   ├─(a)─ Project & Tile-Sort  ──────────────────────────────────────────────
   │       3D → 2D:  Σ'_2D = J W Σ W^T J^T               (Eq. 21)
   │       Per-tile cull + per-ray depth sort
   │       For each ray (pixel) r ∈ [H·W]:
   │         contributing Gaussians M_r (variable; M ≤ N)
   │         peaks       t*_i      [M_r]
   │         per-Gaussian params   [M_r, 11]
   │
   ├─(b/c)─ Continuous Per-Gaussian Transmittance  ─────────────────────────
   │       v_i(t) = sqrt(1 - G_i(t))                     (Eq. 6 along ray)
   │       T_i(t) piecewise around t*_i                  (Eq. 12)
   │       T(t) = Π_i T_i(t)                             (Eq. 11)
   │
   ├─(d/e)─ Forward: Binary Search for t_med where T = 0.5  ────────────────
   │       Init bracket [t_init − 0.4, t_init + 0.4]; t_init from RaDe-GS
   │       5 iterations × 8 segments (7 segment points / iter)
   │       Each iter: traverse M_r Gaussians, evaluate T at 7 points → [7]
   │                  pick sub-interval that brackets 0.5
   │       Mask pixel if both bracket ends fall on the same side of 0.5
   │       Output:    t_med                              [H, W]
   │
   ├─ Auxiliary rasterization (standard GS, NOT volumetric):
   │       RGB         C           [H, W, 3]
   │       Normal      n̂           [H, W, 3]
   │
   ├─ Losses:  L = L_photo + L_n (normal consistency, 2DGS) + L_gc (PGSR multi-view)
   │
   └─(f)─ Backward: Closed-form ∂t_med/∂θ_i  ───────────────────────────────
           Pass 1, traverse M_r Gaussians:
             ∂T/∂t |_{t_med} = Σ_i (0.5 / T_i(t_med)) · ∂T_i/∂t |_{t_med}     (Eq. 16)
           Pass 2, traverse M_r Gaussians:
             ∂T/∂θ_i        = (0.5 / T_i(t_med)) · ∂T_i/∂θ_i                 (Eq. 17)
           ∂L/∂θ_i = (∂L/∂t_med) · ∂T/∂θ_i / (− ∂T/∂t |_{t_med})              (Eq. 18)

Output
  Depth map           [H, W]
  Gradients to θ:     {[N, 3], [N, 1], [N, 3], [N, 4]}
```

Shapes the paper does not specify (e.g., the dimensionality and packed layout of `θ_i` per Gaussian on the ray, and the warp-level reduction tensor sizes used for gradient accumulation in the custom CUDA kernel) are marked or noted in the relevant module's "Implementation Details" below.

### 5.3 Per-Module Breakdown

#### 5.3.1 Gaussian Primitive Parameterization & 2D Projection

**Function:** Define the scene as a set of 3D anisotropic Gaussians and project each one onto the image plane via a local affine approximation, exactly as in vanilla 3D GS.

**Input:**
- Name: scene parameters $\theta$
- Shape: centers $[N, 3]$, opacity $[N, 1]$, scales $[N, 3]$, quaternions $[N, 4]$
- Source: optimized parameters (initialized from SfM point cloud, GOF densification strategy)

**Output:**
- Name: 2D Gaussians on image plane (one per view)
- Shape: 2D centers $[N, 2]$, screen-space covariances $\Sigma'_{2D}$ $[N, 2, 2]$
- Consumer: per-tile rasterizer / per-ray sort (§5.3.3)

**Processing:**

For each Gaussian, the paper writes the 3D primitive (Eq. 1, supplementary Eq. 19) as $G(x) = o \exp(-(x-x_c)^\top \Sigma^{-1} (x-x_c))$. Camera-frame covariance is $\Sigma_{cam} = W \Sigma W^\top$ (Eq. 20), and the projected 2D covariance via the perspective-projection Jacobian $J \in \mathbb{R}^{2\times 3}$ is

$$
\Sigma'_{2D} = J W \Sigma W^\top J^\top.
$$

The 2D Gaussian's pixel-space response (Eq. 2) is $\alpha(u) = o \exp(-(u-u_c)^\top \Sigma'^{-1}_{2D} (u-u_c))$. Crucially, the paper proves (supplementary) that this $\alpha$ equals the **maximum value of $G$ along the pixel's view ray**, i.e. $\alpha = G(t^*)$ where $t^* = \arg\max_t G(o + \omega t)$ — the link that makes the stochastic-solid identity in §5.3.2 possible.

**Key Formulas:**

$$
G(x) = o\, e^{-(x-x_c)^\top \Sigma^{-1} (x-x_c)}, \qquad
\Sigma'_{2D} = J W \Sigma W^\top J^\top, \qquad
\alpha = G(t^*).
$$

**Implementation Details:**

The implementation reuses the local-affine projection from RaDe-GS to estimate each Gaussian's ray-wise peak $t^*_i$ efficiently. The 3D filter from Mip-Splatting is applied (without its 2D filter); densification follows GOF; exposure compensation follows PGSR.

#### 5.3.2 Stochastic-Solid Reformulation: Deriving the Vacancy Field

**Function:** Re-interpret each Gaussian primitive as a stochastic solid by deriving the **unique** vacancy function $v(x)$ that makes the volume-rendered color of the Gaussian equal to its rasterized color.

**Input:**
- Name: Gaussian function $G(x)$ along a view ray $l: o + \omega t$
- Shape: scalar field, samples evaluated as $G(t)$
- Source: §5.3.1

**Output:**
- Name: vacancy $v(x)$ and induced attenuation $\sigma(x,\omega)$
- Shape: scalar fields
- Consumer: per-Gaussian transmittance $T_i$ (§5.3.3)

**Processing:**

Starting from Miller et al.'s rendering equation (Eq. 4), a single Gaussian's volume-rendered color reduces (Eq. 7) to $C = c(1 - v(t^*)^2)$, where $t^*$ is the ray-wise maximum point. Equating this with the rasterized color $C = c\,G(t^*)$ (Eq. 5) gives $v(t^*) = \sqrt{1 - G(t^*)}$ (Eq. 9). Imposing the three additional constraints — (i) occupancy monotone in $G$, (ii) vacancy $\to 1$ as $x$ moves away from $x_c$, (iii) differentiability of $o(x)$ — extends this from the ray-peak point to the full 3D field, yielding the unique closed form (Eq. 6). The attenuation coefficient then comes from Eq. 3 and is well-defined wherever $v > 0$.

**Key Formulas:**

$$
v(x) = \sqrt{1 - G(x)}, \qquad
\sigma(x, \omega) = \frac{|\omega \cdot \nabla v(x)|}{v(x)}.
$$

**Implementation Details:**

The uniqueness proof and the constraint that $v(t^*) = \sqrt{1-G(t^*)}$ extends globally to $v(x) = \sqrt{1 - G(x)}$ are deferred to the supplementary material; the paper does not specify additional numerical safeguards (e.g. clamping for $v \to 0$ at the Gaussian center where $G \to o$).

#### 5.3.3 Per-Gaussian Continuous Transmittance

**Function:** Compute the closed-form transmittance contributed by the $i$-th Gaussian along a ray, replacing the step-wise alpha-compositing transmittance of vanilla GS with a continuous profile.

**Input:**
- Name: ray $l$, ordered Gaussians intersecting the ray
- Shape: per-ray list of $M_r$ Gaussians with parameters $\theta_i$ and peaks $t^*_i$ $[M_r]$
- Source: §5.3.1 (projected/sorted)

**Output:**
- Name: per-Gaussian transmittance $T_i(t)$ and total $T(t)$
- Shape: scalar functions of $t$ along each ray
- Consumer: forward binary search (§5.3.4), backward gradient (§5.3.5)

**Processing:**

Each $T_i(t)$ is integrated from the attenuation $\sigma$ inside Gaussian $i$ alone (derivation in the supplementary). The result is piecewise around the peak $t^*_i$: before the peak, $T_i$ equals the vacancy along the ray; after the peak, $T_i$ continues as the squared-vacancy-at-peak divided by current vacancy, which preserves smoothness at $t^*_i$ and yields $T_i \to 1$ as $t \to \infty$ (per Figure 6). Assuming independence of ray–Gaussian intersection events (following Blanc et al. 2025a/b; Condor et al. 2025), the per-Gaussian transmittances multiply.

**Key Formulas:**

$$
T_i(t) =
\begin{cases}
v_i(t), & t \le t^*_i \\
v_i(t^*_i)^2 / v_i(t), & t > t^*_i
\end{cases}
\qquad
T(t) = \prod_i T_i(t).
$$

**Implementation Details:**

$t^*_i$ is taken from the local-affine projection of RaDe-GS. The paper does not specify how Gaussians whose peak lies outside the search bracket are pruned, or the precise per-Gaussian parameter packing used in the warp-level reduction.

#### 5.3.4 Forward Pass: Iterative Binary Search for $t_{med}$

**Function:** Locate the median-transmittance depth $t_{med}$ at which $T(t_{med}) = 0.5$, exploiting the monotonicity of $T(t)$.

**Input:**
- Name: per-ray ordered Gaussians + initial depth estimate $t_{init}$
- Shape: $[M_r]$ Gaussians per ray; $t_{init}$ scalar per ray (from RaDe-GS, $[H, W]$ overall)
- Source: §5.3.1, §5.3.3

**Output:**
- Name: median depth map $t_{med}$
- Shape: $[H, W]$ (with a binary mask for pixels failing the bracket test)
- Consumer: geometric losses, mesh extraction (TSDF / Marching Tetrahedra)

**Processing:**

Initialize the search bracket as $[t_{init} - r, t_{init} + r]$ with $r = 0.4$. In each of 5 iterations, divide the current interval into **8 segments** using **7 segment points**, traverse the $M_r$ Gaussians along the ray to evaluate $T$ at each point, then select the unique sub-segment whose endpoint transmittances bracket 0.5. One such 7-point pass is informationally equivalent to three classical bisection steps, so 5 iterations $\approx 15$ bisections, giving a depth-error bound of $0.8 \cdot 8^{-5} \approx 2.441 \times 10^{-5}$. On the first pass, the transmittances at the bracket endpoints $t_{init} \pm r$ are also recorded; if both lie on the same side of 0.5, the pixel is masked out of the geometric regularization losses.

**Key Formulas:**

$$
t_{med} = T^{-1}(0.5), \qquad
\text{final error} \le 0.8 \times 8^{-5} \approx 2.441 \times 10^{-5}.
$$

**Implementation Details:**

Bracket radius $r = 0.4$ during training; iterations fixed at 5. The authors note further speedup is possible by tightening the initial bracket and leave it for future work. Multi-view regularization is implemented in a custom CUDA kernel; gradient accumulation uses warp-level reductions following gsplat.

#### 5.3.5 Backward Pass: Closed-form Gradient

**Function:** Backpropagate $\partial L / \partial t_{med}$ to **all** Gaussian parameters $\theta_i$ along the ray in closed form, without iterating the binary search.

**Input:**
- Name: upstream gradient $\partial L / \partial t_{med}$, plus the forward-pass $t_{med}$ and per-ray Gaussians
- Shape: $\partial L / \partial t_{med}$ $[H, W]$; per-ray $[M_r]$
- Source: loss computation; §5.3.4 forward pass

**Output:**
- Name: parameter gradients $\partial L / \partial \theta_i$
- Shape: matches each Gaussian parameter tensor (centers $[N, 3]$, opacities $[N, 1]$, scales $[N, 3]$, quaternions $[N, 4]$)
- Consumer: optimizer (Adam, default GS settings)

**Processing:**

Implicit differentiation of $T(t_{med}; \theta) = 0.5$ gives Eq. 13. Two passes through the $M_r$ Gaussians on each ray are required:

- **Pass 1** computes $\partial T(t;\theta)/\partial t \big|_{t_{med}}$ as a sum over Gaussians (Eq. 16), exploiting $\prod_{j\ne i} T_j = T / T_i = 0.5 / T_i$.
- **Pass 2** computes, for each contributing Gaussian, $\partial T(t_{med}; \theta) / \partial \theta_i$ analogously (Eq. 17).

Combining via Eq. 13/18 distributes the depth gradient across **all** $M_r$ Gaussians on the ray, giving denser supervision than prior methods that pin the gradient to a single "critical" Gaussian.

**Key Formulas:**

$$
\frac{\partial T(t;\theta)}{\partial t}\bigg|_{t_{med}}
= \sum_i \frac{0.5}{T_i(t_{med}; \theta_i)} \frac{\partial T_i(t;\theta_i)}{\partial t}\bigg|_{t_{med}},
$$

$$
\frac{\partial T(t_{med};\theta)}{\partial \theta_i}
= \frac{0.5}{T_i(t_{med}; \theta_i)} \frac{\partial T_i(t_{med};\theta_i)}{\partial \theta_i},
$$

$$
\frac{\partial L}{\partial \theta_i}
= \frac{\partial L}{\partial t_{med}} \cdot
\frac{\partial T(t_{med};\theta)/\partial \theta_i}
     {-\, \partial T(t;\theta)/\partial t \big|_{t_{med}}}.
$$

**Implementation Details:**

Per-Gaussian terms $\partial T_i/\partial t$ and $\partial T_i/\partial \theta_i$ are obtained directly from the closed form of Eq. 12. Pass 2 is implemented by modifying the standard GS color-accumulation backward kernel to additionally accumulate $\partial T(t_{med};\theta)/\partial \theta_i$. Warp-level reductions follow gsplat.

#### 5.3.6 Loss Composition & Optimization

**Function:** Train Gaussian parameters end-to-end with photometric, normal-consistency, and multi-view geometric losses, while keeping RGB and normal rendering in the standard GS rasterized form for efficiency.

**Input:**
- Name: rendered RGB $C$, normal $n$, depth $t_{med}$, ground-truth images
- Shape: $[H, W, 3]$, $[H, W, 3]$, $[H, W]$
- Source: §5.3.1 (RGB/normal), §5.3.4 (depth)

**Output:**
- Name: scalar loss $L$ and parameter updates
- Shape: scalar
- Consumer: optimizer

**Processing:**

The total loss combines the standard GS photometric loss (Kerbl et al. 2023), the normal-consistency loss from 2DGS (Huang et al. 2024) — denoted $L_n$ in the ablation — and the multi-view geometric regularization $L_{gc}$ from PGSR (Chen et al. 2024) which penalizes per-pixel cycle reprojection error. RGB and normals use the standard GS rasterized approximation; depth uses the stochastic-solid pipeline of §5.3.3–§5.3.5. Geometric regularization is enabled at 7K iterations across all baselines for fair comparison.

**Key Formulas:**

$$
L = L_{photo} + L_n + L_{gc}.
$$

(The exact weights are stated to be in the supplementary material, which is not reproduced in the main text.)

**Implementation Details:**

Mesh extraction uses TSDF fusion (Open3D) on DTU and Marching Tetrahedra on Tanks & Temples; an indicator function classifies a 3D point as "inside" if its transmittance falls below 0.5 in any training view. Reported runtimes on DTU: 15.0 min @ 20K iters, 25.3 min @ 30K iters; on TnT: 32.1 min mean — competitive with PGSR (30.5 / 42.9 min) and faster than GeoSVR (53.3 / 66.4 min).

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| DTU [Jensen et al. 2014] | Multi-view shape reconstruction (Chamfer Distance) | 15-scene standard split, half-resolution images | Used for reconstruction evaluation；the paper does not specify a separate train/val/test split beyond following prior work's protocol |
| Tanks & Temples (TnT) [Knapitsch et al. 2017] | Large-scale shape reconstruction (F1-score) | 6-scene common subset (Barn, Caterpillar, Courthouse, Ignatius, Meetingroom, Truck) | Used for reconstruction evaluation following prior work |
| Mip-NeRF 360 [Barron et al. 2022] | Novel view synthesis 與 shape reconstruction (qualitative) | Outdoor 與 indoor scenes (split per Table 4) | Used for NVS quantitative comparison（附錄 D）以及 specular regions 的 qualitative 比較 |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| Chamfer Distance (CD) | DTU 上 reconstructed mesh 與 ground-truth point cloud 之間的雙向最近點平均距離，越低越好 | yes |
| F1-score | TnT 上 reconstructed mesh 在固定距離閾值下的 precision/recall 調和平均，越高越好 | yes |
| Optimization time | 每個 scene 的平均訓練時間（minutes / hours），用以說明 efficiency trade-off | no |
| Cycle reprojection error | reference view 與 neighboring view 之間 depth 的 forward–backward 重投影像素距離，用於診斷 multi-view consistency | no |
| PSNR / SSIM / LPIPS | Mip-NeRF 360 上 novel view synthesis 的影像品質指標（附錄 D） | no |

### 6.3 Training and Inference Settings

- Hardware：the paper does not specify GPU / CPU 規格。
- Iterations：DTU 報告 20k 與 30k 兩個版本（Table 1），TnT 與 multi-view consistency 實驗在 30k iterations 內 evaluate；geometric regularization 在所有方法中於 7K iterations 啟動（§5.2）。
- Optimizer / batch size / learning rate schedule：the paper does not specify；implementation 沿用 RaDe-GS [Zhang et al. 2024]、GOF [Yu et al. 2024c] 的 densification、Mip-Splatting [Yu et al. 2024a] 的 3D filtering（不含 2D filter）、以及 PGSR [Chen et al. 2024] 的 exposure compensation（§5 Implementation Details）。
- Loss weights（附錄 C）：$w_n = 0.05$、$w_{pc} = 0.6$、$w_{gc} = 0.02$，photometric 中 $\lambda = 0.2$。
- Depth rendering（附錄 A.1）：以 RaDe-GS 的 $t_{init}$ 為起點，初始 bracket $[t_{init}-r, t_{init}+r]$ 設 $r = 0.4$，每次 traversal 將區間切成 8 段（等同 3 次 binary search），共重複 5 次，最終深度誤差 $\le 0.8 \times 8^{-5} = 2.441 \times 10^{-5}$；當 bracket 兩端 transmittance 同側於 0.5 時，遮罩該 pixel 不參與 geometric regularization。
- Mesh extraction（§5）：DTU 用 Open3D 的 TSDF fusion [Curless and Levoy 1996]；TnT 用 Marching Tetrahedra [Guédon et al. 2025a; Yu et al. 2024c]，indicator 定義為「該點若在任一 training view 中被遮蔽（transmittance < 0.5）則判為 inside」。
- Multi-view regularization 以 custom CUDA kernel 實作；gradient accumulation 採 gsplat [Ye et al. 2025] 的 warp-level reductions。
- Inference settings：the paper does not specify 額外的 inference-time hyperparameters。

### 6.4 Main Results

DTU（Chamfer Distance↓，15-scene 平均，Table 1 節錄）：

| Method | DTU Mean CD ↓ | Time | Notes |
| --- | --- | --- | --- |
| Neuralangelo [Li et al. 2023] | 0.61 | > 12h | Implicit；最強 implicit baseline |
| 3D GS [Kerbl et al. 2023] | 1.96 | 7.8m | Explicit baseline |
| 2D GS [Huang et al. 2024] | 0.80 | 11.3m | Explicit |
| GOF [Yu et al. 2024c] | 0.74 | 52m | Explicit |
| RaDe-GS [Zhang et al. 2024] | 0.68 | 8.2m | Explicit，本工作沿用其 $t^*_i$ |
| GFSGS [Jiang et al. 2025] | 0.58 | 16.8m | Explicit |
| PGSR [Chen et al. 2024] | 0.52 | 30.5m | Explicit，使用 multi-view regularization |
| GeoSVR [Li et al. 2025] | 0.47 | 53.3m | Explicit SoTA |
| **Ours (20k)** | **0.47** | **15.0m** | 與 GeoSVR 並列最佳，但時間僅約 1/3.5 |
| **Ours (30k)** | **0.48** | **25.3m** | 與 GeoSVR 相當 |

TnT（F1↑，6-scene 平均，Table 2 節錄）：

| Method | TnT Mean F1 ↑ | Time | Notes |
| --- | --- | --- | --- |
| Neuralangelo | 0.50 | > 24h | 最強 implicit |
| 2D GS | 0.30 | 15.5m | Explicit |
| GOF | 0.46 | 71.6m | Explicit |
| RaDe-GS | 0.45 | 12.1m | Explicit |
| PGSR | 0.52 | 42.9m | Explicit |
| GeoSVR | 0.56 | 66.4m | 先前 explicit SoTA |
| **Ours** | **0.60** | **32.1m** | 全 method 最佳，比 GeoSVR 高 0.04 且快約 2× |

要點：在 DTU 上，本方法在 explicit Gaussian Splatting 類別中與 GeoSVR 並列最佳並顯著快於它；在 TnT 上，本方法以 F1 = 0.60 全面超越所有 explicit 與 implicit baselines（包含 Neuralangelo 的 0.50）。Multi-view consistency 圖（Figure 8、13）亦顯示本方法在 30K iterations 達到最低的 cycle reprojection error，且在前景區域比 PGSR 與加上 multi-view regularization 的 RaDe-GS 更早達到完整覆蓋。

### 6.5 Ablation Studies

論文在 TnT 上提供一張 ablation 表（Table 3），對照三種 depth-rendering backbone（PGSR、RaDe-GS、Ours）以及三個 loss / module 開關 $L_{gc}$（geometric cycle-consistency）、$L_n$（normal consistency / single-view geometric）、`exposure`（PGSR 的 exposure compensation）：

- 移除 $L_{gc}$（Ours 列：0.60 → 0.60）：F1 持平。作者解釋因為本文的 stochastic-solid depth 已經提供強 multi-view consistency，使 explicit 的 cycle-consistency 懲罰只剩邊際效益。此實驗診斷了「stochastic 深度在 multi-view 一致性上是否已足夠」這個關鍵問題，屬 diagnostic ablation。
- 移除 $L_n$（normal consistency / 單視圖 geometric loss）（0.60 → 0.57）：F1 下降 0.03，顯示 normal-from-depth 的監督在本 pipeline 中仍貢獻明顯，與 photometric 形成互補。
- 移除 `exposure`（exposure compensation）（0.60 → 0.59）：F1 微幅下降 0.01，屬輕度貢獻，較像 sanity check。
- Backbone 替換：在相同正則化下，PGSR backbone 的 F1 = 0.52、RaDe-GS = 0.52、Ours = 0.60，直接孤立出本文 depth-rendering formulation 的貢獻（+0.08 F1），這是真正的 diagnostic ablation。

整體而言，ablation 設計直接圍繞論文核心主張（stochastic-solid depth 與其 multi-view 一致性）展開，但缺一些可進一步揭示機制的實驗，例如：binary-search 步數 / 初始 bracket $r$ 的敏感度、是否使用 closed-form gradient（vs. 對單一 Gaussian 反傳）的對照、以及 $T = 0.5$ 閾值改變後的退化行為。論文亦未做僅在 RGB / normal 上加入 stochastic volumetric rendering 的對照（作者自承為 future work）。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline (a current SoTA on the chosen task) — DTU 與 TnT 上同時對比 Neuralangelo（implicit SoTA）與 GeoSVR / PGSR（explicit SoTA），Table 1、Table 2。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 在 DTU（CD）、TnT（F1），以及 Mip-NeRF 360（NVS：PSNR/SSIM/LPIPS）三個資料集評測，並涵蓋 reconstruction 與 novel view synthesis 兩個任務。
- [partial] Has ablations that diagnose the new components (not just sanity checks) — Table 3 透過替換 backbone 直接孤立 stochastic-solid depth 的貢獻（+0.08 F1），但未對 binary search 步數、initial bracket $r$、或 closed-form gradient vs. single-Gaussian gradient 做對照，缺少對方法內部機制更細的診斷。
- [missing] Has a scaling study (size, length, or compute) — 僅報告 DTU 上 20k 與 30k 兩個 iteration 點，未對 Gaussian 數量、scene 規模或計算預算做 scaling 曲線。
- [covered] Has an efficiency / wall-clock comparison — Table 1、Table 2 報告每個 baseline 的平均優化時間（如 Ours 15.0m vs. GeoSVR 53.3m on DTU；Ours 32.1m vs. GeoSVR 66.4m on TnT）。
- [missing] Reports variance / standard deviation / multiple seeds where relevant — 所有 Chamfer / F1 / PSNR 數值皆為單點報告，論文未提供 std 或多 seed 結果。
- [partial] Releases code / weights / data sufficient for reproducibility — §5 Implementation Details 寫到「We will release our code」，但截至本稿無實際 repository 連結，亦未提及 pretrained weights 或 evaluation scripts，僅項目頁 https://baowenz.github.io/geometry_grounded_gaussian_splatting 列於標題。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1: 證明 Gaussian primitive 等價於 stochastic solid,並推得唯一的 vacancy $v=\sqrt{1-G}$**。**Supported.** Supplementary §G 給出完整推導 (從局部仿射近似 $\to$ 1D Gaussian along ray $\to$ 三項約束 $\to$ 唯一解),Figure 3 視覺化等價性;這是論文最紮實的貢獻。
- **Claim 2: 連續 $T(t)$ 下的 median depth 具備跨視角一致性與抗 floater 性**。**Partially supported.** Figure 8 / Figure 13 的 cycle reprojection error 確實顯示比 PGSR、RaDe-GS 低,但「view-independent 0.5-isosurface」需要前提 $t_{med}<t^*$ (§4.2.1);此前提的失效率沒有量化,因此一致性是經驗觀察而非理論保證。
- **Claim 3: 閉式梯度提供「dense supervision」分散到所有貢獻 Gaussian**。**Supported in derivation, undertested in ablation.** Eq. 13 與 supplementary §I 推導正確,但 Table 3 沒有單獨切換「閉式梯度 vs 單一 Gaussian 梯度」的版本,因此「dense supervision 帶來 X% 提升」這類強因果陳述目前缺乏直接證據。
- **Claim 4: 在 GS 系列中達到最佳重建精度**。**Partially supported.** TnT F1 0.60 確實領先 (Table 2);但 DTU CD 0.47 僅與 GeoSVR 並列、且 GeoSVR 在 explicit 框架內;同期 GFSGS 在 TnT 上未被列入比較。「best among GS-based」的措辭嚴格說只在 TnT 站得住。
- **Claim 5: 維持 GS 的優化效率**。**Supported.** Table 1 顯示 25.3 min (30k) 比 PGSR (30.5 min)、GeoSVR (53.3 min) 都快,雖落後純 NVS-導向的 RaDe-GS (8.2 min),但在帶 multi-view regularization 的方法中屬最快級別。

### 7.2 Fundamental Limitations of the Method

**體渲染與 rasterization 的內部不一致**。論文以 stochastic-solid 嚴格重新詮釋 Gaussian,但僅將之應用到 depth,RGB 與 normal 仍以 rasterization 近似 (§4.3)。這意味著「geometry-grounded」只在深度通道成立,而 photometric loss 與 normal loss 所監督的物件,本質上是另一種數學模型的輸出。理論橋接的力量被自我截短:若日後將色彩也改為 volumetric,既有的精度數字就無法外推,因為 RGB 渲染變了會回過來改變 floater 分佈與 transmittance shape。

**獨立性假設限制理論在重疊場域的成立**。Eq. 11 的 $T=\prod_i T_i$ 仰賴「光線撞擊不同 Gaussian 屬統計獨立事件」,但 GS 優化的本質就是讓多顆 Gaussian 重疊以提升 photometric 表現。當重疊率高時,真實的 transmittance 並非各 Gaussian 透射率的簡單乘積;論文未提供任何敏感度分析,使得理論的適用域實際上窄於文字所暗示。

**Median depth 的 view-independence 只是條件性質**。§4.2.1 自承「median depth 與 vacancy field 重合」需要 $t_{med}<t^*$ (即 $T=0.5$ 在所有貢獻 Gaussian 的峰值之前發生)。在薄結構、半透明物件、或 floater 嚴重的訓練早期,這個條件不一定成立,而此時 median depth 又退化為與舊有 GOF/2DGS 類似的 view-dependent 估計。論文用「optimization clusters high-opacity Gaussians near surface」的經驗描述帶過,沒有給出該條件失效的覆蓋率與對應 reconstruction 誤差。

**固定 binary-search 區間在大尺度場景的崩潰風險**。Forward pass 以 $[t_{init}-0.4, t_{init}+0.4]$ 為初始區間 (supplementary §A.1),且若兩端透射率同號就 mask 該像素以放棄幾何監督。在 Tanks & Temples 之外的更大場景 (例如 KITTI、街景級),$t_{init}$ 的誤差可能超過 0.4 metric units,導致大量像素被 mask 而失去深度約束,作者也明確點名為未來工作 (§E)。在當前形式下,本方法並非「規模無關」。

### 7.3 Citations Worth Tracking

- **Miller et al. 2024, "Objects as Volumes" (CVPR)**:本文的全部理論基礎,提供 stochastic solid 的衰減係數定義與唯一性證明的原型;不讀此文無法判斷 GGGS 是否真正貼合原始 framework 還是做了實質擴展。
- **Jiang et al. 2025, "GFSGS: Geometry Field Splatting with Gaussian Surfels" (CVPR)**:同期把 stochastic solid 套到 Gaussian 的工作,但用的是 2D surfel 而非 3D Gaussian;對比兩篇能看出「primitive 維度的選擇」對理論結論的影響,是判斷本文新穎度的關鍵對照組。
- **Chen et al. 2024, "PGSR" (TVCG)**:本文 multi-view regularization 完全借用 PGSR (Eq. 26-31),且 ablation Table 3 顯示 $L_n$ 與 exposure 對 F1 提升不可忽視;不讀 PGSR 會誤判 GGGS 的 F1 增量歸屬。
- **Yariv et al. 2021, "VolSDF" / Wang et al. 2021, "NeuS"**:作者宣稱要把 NeRF 的 geometry-grounded 哲學帶入 GS,但未實際採用 SDF 那種顯式 surface anchor;讀這兩篇能看到 GGGS 與真正「以 surface 為錨」之間的距離有多大。
- **Zhang et al. 2024, "RaDe-GS"**:本文用以估計每顆 Gaussian 沿光線的峰值點 $t^*_i$ 與 binary search 的 $t_{init}$,效能與精度都仰賴它;而 RaDe-GS 在 Table 1 也是一個敗於 GGGS 的 baseline,構成「同作者群方法迭代」的有趣 trace。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 若把 stochastic-solid 公式同時應用到 RGB 與 normal 通道 (作者明列為 future work),DTU/TnT 精度與訓練時間各會變動多少?目前無法判斷理論的完整潛力。
- [ ] 在 ablation 中單獨切換「連續 $T_i(t)$」、「閉式 $\partial t_{med}/\partial\theta$」、「multi-view $L_{gc}$」,F1 0.60 中各占多少?目前只能聯合評估三者。
- [ ] 條件 $t_{med}<t^*$ (view-independent isosurface 的前提) 在 TnT/DTU 的滿足率為何?若降到例如 80% 以下,cycle reprojection error 的退化曲線?
- [ ] 與同期 GFSGS 在 TnT 上的直接比較 (F1)?目前 Table 2 缺此項,使「best among GS」的措辭存在缺口。
- [ ] 獨立性假設 $T=\prod_i T_i$ 在 Gaussian 重疊密度高的區域 (例如 thin structures) 偏差有多大?若改用相關修正項 (例如 Condor et al. 2025) 重建精度會否提升?
- [ ] Binary search 的固定 $r=0.4$ 在 Mip-NeRF 360 outdoor 或更大場景中失效像素比例?是否與 outdoor PSNR 落後 RayGaussX 的現象相關?
- [ ] Marching Tetrahedra 用「任一 training view 中 transmittance < 0.5 即視為 inside」的 inside/outside indicator,在多視角覆蓋不均的場景中是否系統性產生孔洞或贅肉?

### 8.2 Improvement Directions

1. **將 ablation 擴展到「連續透射率 only」與「閉式梯度 only」兩個獨立變體** (高可行性):兩者皆已有完整推導,只需在 codebase 中切換 $T_i(t)$ 與 backward pass 即可,能直接回答理論貢獻的歸屬問題,作為論文修訂版的關鍵實驗。
2. **加入 GFSGS 在 TnT 的對比** (高可行性):GFSGS 已開源,只需跑一次標準 6-scene F1 評估,可堵上「best among GS」陳述的最直接質疑。
3. **將 binary search 的 $r$ 由固定改為 per-ray adaptive** (中可行性):利用 RaDe-GS 提供的 $t^*$ 分佈估計每條 ray 的合理區間,作者已點名為 future work;此舉可同時解決 large-scale 場景失效與計算量過大兩個問題。
4. **把 stochastic-solid 公式擴展至 RGB 與 normal,並與 RayGauss/RayGaussX 對比 NVS** (中可行性,計算成本高):這是把「principled」標籤名實相符的最直接方法,理論上會提升 specular 區域品質並消除內部不一致,實作上需重寫 forward kernel。
5. **針對條件 $t_{med}<t^*$ 失效情況設計後備分支** (中可行性):當 binary search 偵測到 transmittance 在 Gaussian peak 之後才下穿 0.5,改用 confidence-weighted fallback (例如 expected depth) 並 mask 對應 multi-view loss,可避免理論前提失效時的優化噪聲。
6. **以 Neuralangelo 風格的 numerical-gradient eikonal regularizer 替換目前的 normal consistency loss** (低可行性):需要為 stochastic Gaussian solid 定義 SDF-like 場,但本論文已明確指出此方向 (§E),長期可大幅提升薄結構與低紋理區域的幾何品質。
