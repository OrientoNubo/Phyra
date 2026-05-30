<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# TTT3R — TTT3R: 3D Reconstruction as Test-Time Training

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | TTT3R |
| Paper full title | TTT3R: 3D Reconstruction as Test-Time Training |
| arXiv ID | 2509.26645 |
| Release date | 2026-03-03 |
| Conference/Journal | ICLR 2026 |
| Paper link (abs) | https://arxiv.org/abs/2509.26645 |
| PDF link | https://arxiv.org/pdf/2509.26645 |
| Code link | https://github.com/rover-xingyu/TTT3R |
| Project page | https://rover-xingyu.github.io/TTT3R/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Xingyu Chen | Zhejiang University; Westlake University (Inception3D Lab) | https://rover-xingyu.github.io/ | first author |
| Yue Chen | Zhejiang University; Westlake University | — | co-author |
| Yuliang Xiu | Westlake University | — | co-author |
| Andreas Geiger | University of Tübingen; Tübingen AI Center | — | co-advisor |
| Anpei Chen | Westlake University (Inception3D Lab) | https://apchenstu.github.io/ | corresponding author / advisor |

### 1.2 Keywords

3D reconstruction, test-time training, recurrent neural networks, length generalization, pointmap regression, associative memory, fast weights, confidence-guided state update

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| CUT3R [89] | base model | Recurrent online 3D reconstruction model whose state-update rule TTT3R reformulates and replaces with a confidence-guided update. |
| VGGT [87] | baseline | Offline full-attention pointmap regressor used as the main full-attention baseline; shows quadratic memory growth contrasted in Fig. 2. |
| StreamVGGT [106] | baseline | Causal-attention online variant of VGGT, compared as an $O(t)$-memory streaming baseline. |
| Point3R [95] | baseline | Online RNN-style reconstructor with explicit point-anchored memory; baseline whose linear memory growth TTT3R avoids. |
| DUSt3R [91] | predecessor | Pioneering pixel-aligned pointmap foundation model that grounds the entire 3D reconstruction lineage adopted here. |
| DeltaNet [64, 98] | influence | Linear TTT formulation providing the fast-weight / closed-form gradient view that motivates TTT3R's update derivation. |
| TTT [73] | influence | Test-Time Training framework treating recurrent state as fast weights learned online; conceptual lens used to revisit CUT3R. |

## 2. Research Overview

### 2.1 Research Topic

本論文聚焦於以前饋式基礎模型 (feed-forward foundation model) 進行線上 3D 重建的長序列泛化問題。作者觀察到以 Transformer 全注意力為主的方法 (如 VGGT、Fast3R) 雖精度高,但記憶體與運算量隨輸入影格呈二次或線性成長,難以處理上千張影像;而以 RNN 為基礎、具固定大小狀態的 CUT3R 雖達常數記憶體,卻在輸入超過訓練 context 長度時嚴重退化,出現災難性遺忘 (catastrophic forgetting)。本文以 Test-Time Training (TTT) 的視角重新審視這類遞迴式 3D 重建模型,將狀態視為在測試時透過梯度下降線上更新的「快權重 (fast weights)」,而骨幹參數作為「慢權重 (slow weights)」扮演 meta-learner。研究主題即為:如何在不重新訓練的前提下,設計一條符合 TTT 框架的閉式狀態更新規則,讓模型在數千張影像的串流輸入下仍能維持精準的相機姿態、深度與點雲重建,並保持線性時間與固定記憶體成本。

### 2.2 Domain Tags

- 3D Computer Vision
- 3D Reconstruction Foundation Models
- Recurrent Sequence Modeling
- Test-Time Training / Online Learning

### 2.3 Core Architectures Used

- **CUT3R (base model)**:作為被改造的 RNN-based 線上 3D 重建骨幹,其凍結的慢權重提供 cross-attention $Q_{S_{t-1}} K_{X_t}^\top$,TTT3R 直接在其推論流程中插入新的閉式狀態更新規則,不微調任何參數。
- **Test-Time Training (TTT) / Fast-Weight Programmer**:本文的概念框架,將遞迴狀態 $S_t$ 視為由梯度下降在測試時線上更新的快權重,慢權重 (DUSt3R/CUT3R 訓練得到的 transformer 參數) 則扮演 meta-learner,提供梯度與學習率的計算函式。
- **Linear Attention / DeltaNet 形式的線性 RNN**:作為推導參考,提供 $\text{Update}(S_{t-1}, X_t) = S_{t-1} - \beta_t \nabla(S_{t-1}, X_t)$ 的閉式解析梯度形式,讓 CUT3R 的 softmax cross-attention 得以重寫為 TTT 規則。
- **Gated Linear Attention (per-token gating)**:提供 per-token 學習率 $\beta_t \in \mathbb{R}^{n \times 1}$ 的設計範式,TTT3R 的 confidence-guided 學習率正是此形式的具體實例。
- **DPT head + pixel-shuffle linear de-tokenizer**:沿用自 DUSt3R/CUT3R 的密集預測頭,將輸出 token $Y_t$ 還原為 pixel-aligned pointmap;相機姿態 $T_t$ 與內參 $C_t$ 則透過 PnP 與 Weiszfeld 演算法或 trunk attention 從 pointmap/token 推得。

### 2.4 Core Argument

作者主張 CUT3R 之所以無法泛化到長序列,根本原因在於其狀態更新規則中的 softmax 交叉注意力會強迫權重沿觀察 token 維度歸一化為 1.0,等同於把學習率固定為 1.0,使得新觀察永遠完全覆蓋歷史狀態,進而導致災難性遺忘。從 TTT 的角度看,這恰恰是缺少彈性、token 級可調學習率所致——而現代 RNN (DeltaNet、Mamba-2、Gated Linear Attention、Titans) 之所以能成功泛化,正是因為它們具備可學習或輸入相依的遺忘閘 / 學習率。基於此診斷,作者提出邏輯上必然的解法:既然問題出在「常數 1.0 學習率」,就應導入一個由「狀態查詢 $Q_S$ 與觀察鍵 $K_X$ 之對齊置信度 (alignment confidence)」決定的 per-token 學習率 $\beta_t$,讓置信度高 (代表當前觀察與歷史記憶一致) 時才大幅更新對應狀態 token,置信度低時則保留歷史。這個閉式更新規則 $\beta_t = \sigma(\sum_m Q_{S_{t-1}} K^\top_{X_t})$ 直接由 CUT3R 凍結權重內部已有的 cross-attention 對齊分數計算而得,因此 (1) 不需任何額外參數或微調,(2) 不增加任何計算成本,(3) 形式上與 Gated Linear Attention 的 per-token 學習率一致,將 CUT3R 嚴格嵌入 TTT 框架。其必然性在於:對齊置信度本身就是「該不該寫入此狀態 token」的最自然訊號,因此以它作為閘控,可在保留歷史記憶與吸收新觀察之間取得理論上合適的平衡,實現 2 倍的全域姿態估計提升、在 6GB 顯存下以 20 FPS 處理上千張影像。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

論文標題 "TTT3R: 3D Reconstruction as Test-Time Training" 直接將兩個關鍵詞綁在一起：3D reconstruction 與 test-time training (TTT)。這個命名宣告了論文的核心立場——把 RNN-based 3D reconstruction foundation model 的 state 更新視為一個 online learning 問題，而非傳統意義上的 forward inference。

Abstract 用一段濃縮的論述帶出整篇論文的主軸。它先肯定 modern RNN 因為 linear-time complexity 而成為 3D reconstruction 的有力 architecture，但旋即指出其致命弱點：當輸入長度超過訓練 context 時，效能顯著退化，揭示 length generalization 不足。接著作者提出本論文的 reframing 觀點——從 TTT 視角重新檢視 foundation model 的 state update，並把 memory state 與新觀察之間的 alignment confidence 用來導出一個 closed-form learning rate，藉此在「保留歷史資訊」與「適應新觀察」之間取得平衡。

最後 Abstract 以三個量化亮點收尾：training-free 的 TTT3R 在 global pose estimation 上相對於 baseline 取得 $2\times$ 提升、能以 20 FPS 處理數千張影像、僅需 6 GB GPU 記憶體。這些數字直接回應第 1 章將鋪陳的兩大痛點——length generalization 與 memory cost。Abstract 不僅交代了 what 與 how much，也預告了論文「以 TTT 視角分析 + 以 confidence 為 gate」的雙層敘事結構。

### 3.2 Introduction

(720 words)

Introduction 走的是一條「先指認問題、再提出 reframe、最後揭示解法」的三段式敘事。

第一段建立 3D reconstruction foundation model 的研究脈絡：這類模型從一組 RGB image 預測 camera pose 與 scene representation，目前 Transformer 因訓練效率與 long-range dependency 能力而成為主流架構，但 softmax attention 的 quadratic 複雜度仍是長序列下的瓶頸。即便有 KV-cache compression 與 flash attention 等工程優化，scalability 仍受限。Figure 2 用 GPU memory 隨輸入視角數成長的曲線把問題具象化：VGGT、Point3R 等 feed-forward 方法在數百張影像時就會超出 48 GB 上限，只有 CUT3R 因 RNN-based 設計維持常數記憶體使用，但 Figure 1 同時顯示 CUT3R 在訓練 context (大多 64-frame) 之外會嚴重退化。

第二段轉入 modern RNN 的進展，把問題抽象化：recurrent architecture 把歷史壓縮為 fix-length state，每個 output 只依賴當前 state 與新觀察，因此具備 linear complexity 與長序列 roll-out 能力，但代價是當序列長度超出訓練 context 時的效能崩潰。作者列出文獻中對此現象的三個歸因——state overfitting、state forgetting、unexplored state distribution——並指出像 training on longer sequences 與 TBTT 等補救手段儘管被引入 CUT3R，仍無法擴展到數百張影像級別。

第三段是論文的 reframe：作者主張用 TTT 的視角重看 RNN-based reconstruction，把 state update 視為 test-time online learning。在這個框架下，state 是一個 fast weight，由 in-context tokens 在測試時學得，而模型 weight 則扮演 meta-learner 角色 (slow weight)。這個視角自然連結到 associative recall 的觀念，並指出「以 adaptive learning rate 進行 gradient-based update 來平衡 forgetting 與 learning」是提升 length generalization 的關鍵。作者進一步觀察到 CUT3R 本身可被解讀為一個 TTT 機制，但其隱含的 learning rate 等同 1.0，因此會盲目地全盤接受新觀察。

最後一段端出 TTT3R 的核心貢獻：一個 inference-time、closed-form 的 state update rule，從 cross-attention alignment confidence 推導出 per-token learning rate，作為 stable、training-free 的 gating 機制來抑制 catastrophic forgetting，無需 fine-tuning 或新增參數。作者預告實驗結果——在 short-sequence benchmark 與 SOTA 方法相當，在 long-sequence 設定下顯著領先，且因為改動只在 update rule，運算成本與 baseline 完全相同。Introduction 的收束語清楚定位本文有兩個層次的貢獻：一個 TTT-based 分析框架，加上一個基於該框架的簡單實證 update rule。這同時為 §3 的方法推導與 §4 的實驗鋪好兩條主線。

### 3.3 Related Work / Preliminaries

(880 words)

Related Work 把整個 3D reconstruction 與 sequence modeling 的相關文獻拆成四個子敘事，每一個都對應到 TTT3R 為何能存在的某個前提。

第一段 SfM and SLAM 為傳統幾何派系定錨：這些方法靠 2D correspondence 或 photometric reprojection error 加 bundle adjustment 達成結構與 motion 估計，雖然在完整系統下相當有效，但在 small parallax、textureless 或 dynamic 場景下會崩潰。即便近年的 MegaSaM、VIPE 透過整合 semantic segmentation、optical flow 與幾何約束來改善 dynamic 場景，仍是 iterative optimization 的範式，存在 synchronization barrier 與 cumulative error，難以做到 real-time online inference。這段話把 TTT3R 定位為 data-driven feed-forward 路線。

第二段 Offline Reconstruction Foundation Model 從 DUSt3R 出發，描述以 Transformer-based architecture 直接預測 pixel-aligned pointmap 的開山之作，並指出其需要昂貴 global alignment 處理超過兩張 view 的問題。Fast3R 與 VGGT 用大型 feed-forward Transformer 配 global attention 一次處理多視角，達到 SOTA，但 full attention 帶來 quadratic 成本與 offline 的限制——每來一張新影像就要重跑全部。這為 TTT3R 「streaming、online、長序列」的目標立下對立面。

第三段 Online Reconstruction Foundation Model 切入最直接的 baseline 群：StreamVGGT 用 causal transformer cache 歷史 KV，但 GPU usage 仍隨視角線性成長；CUT3R 採 RNN 架構維持常數 memory state，卻飽受 forgetting 問題；Point3R 改用 explicit point-based memory 緩解 forgetting，但 memory cost 隨 view 線性累積。作者明確宣告 TTT3R 走的是相反路線——保留 implicit state memory，透過 closed-form state update rule 提升其 length generalization，使 memory 與 compute 都能在數千視角下保持不變。

第四段 Modern RNN 是 TTT3R 借力的理論底層。作者從 linear attention 開始，指出其因把所有 KV 壓進 finite-size state 而長序列退化，接著敘述 Mamba 等加入 forgetting gate 抑制 state divergence 的工作。然後串起 test-time training/regression 框架——把 RNN state 的 recurrent update 視為 online learning，state 即 fast weight，slow weight 則是 meta-learner，這正是 DeltaNet、TTT、Titans 等近期工作的共通骨幹。作者也順帶提到 CVD、Test3R 等已將 test-time learning 引入 3D reconstruction (但他們是 fine-tune pretrained model 在 test sequence 上做 self-supervised 的 geometric consistency)，並說明 TTT3R 想做的是更通用的 TTT 框架，同時兼顧 view scalability 與 memory retention。

Method 章節雖然標題寫 §3 METHOD，但其前段同時承擔 preliminaries 角色：3.1 Sequence Modeling for Pointmap Regression 把 pointmap regression 抽象為一個四步驟的 generic formulation——`Tokenize`、`Update`、`Read`、`De-tokenize`——並把 full attention 與 RNN 兩種主流方法用統一語言寫出。Full attention 寫成 state $\bS_{t-1}$ 不斷 append KV，導致 $O(t^2)$ 計算與成長中的 state；causal attention 把計算降到 $O(t)$，但 state 仍隨視角數線性增長。RNN-based 方法則用 one-to-one cross-attention 維持 fix-length state，計算與記憶體都是 $O(1)$，但會 forget。

3.2 REVISIT RNN-BASED RECONSTRUCTION THROUGH TTT 把上面的 RNN update 重寫為 TTT 形式 $\bS_{t-1} - \beta_t \nabla(\bS_{t-1}, \bX_t)$，並以 DeltaNet 的 reconstruction loss $\|\bS_{t-1}\bK_{\bX_t} - \bV_{\bX_t}\|^2$ 為例，導出 analytical gradient，把 key 解讀為「寫到哪裡」、value 解讀為「寫什麼」、learning rate 解讀為 memory plasticity 的 gate。同時整理 learning rate 設計光譜——scalar、condition-scalar、per-token——並用此語言把 CUT3R 的 update 等同於 $\beta_t = 1.0$ 的特例，揭露其無法平衡 retention 與 adaptation 的結構性缺陷。這段 preliminaries 為 3.3 提出 confidence-guided learning rate 鋪好了完整的數學背景。

### 3.4 Method (overview narrative)

(310 words)

Method 章節的敘事邏輯是「先建立統一的 sequence modeling 語言，再在這個語言上指認 CUT3R 的結構性弱點，最後給出最小但有效的修補」。

3.1 節先把所有 pointmap regression 方法統一成 `Tokenize → Update → Read → De-tokenize` 四步驟的 sequence modeling formulation，並用這個視角把 full attention、causal attention、RNN-based 三類方法的 update 與 read 寫在同一張對照表裡。讀者在這裡得到的關鍵 takeaway 是：full attention 的 $O(t^2)$ 與 RNN 的 $O(1)$ 之間的 trade-off 是結構性的，不是工程性的。

3.2 節是 reframe 的核心步驟。作者把 RNN 的 cross-attention update 改寫成 TTT 的 gradient descent 形式 $\bS_t = \bS_{t-1} - \beta_t \nabla(\bS_{t-1}, \bX_t)$，並把 CUT3R 的 softmax cross-attention 對應到一個 $\beta_t \equiv 1.0$ 的特例。這個對應揭露了一個關鍵 diagnostic：因為 softmax 沿 observation token 維度被 normalize 到 1.0，模型必然完全採納新觀察、丟棄歷史，這正是 catastrophic forgetting 的結構性源頭。同時，作者把 learning rate 的設計空間整理成 ScalarLR、ConditionLR、TokenLR 三類，預告下一節要走 TokenLR 路線但不引入新參數。

3.3 節推出 TTT3R 的 confidence-guided state update rule。核心構造是把 cross-attention alignment $\bQ_{\bS_{t-1}}\bK_{\bX_t}^\top$ 沿 spatial 維度 $m$ 做 mean，再經 sigmoid 得到 per-token learning rate $\beta_t = \sigma\left(\sum_m \bQ_{\bS_{t-1}} \bK_{\bX_t}^\top\right) \in \mathbb{R}^{n\times 1}$。alignment confidence 高的 state token 會得到較大的更新步伐，confidence 低的 (例如 textureless 區域) 則被抑制。整個 update rule 是 closed-form，不需要任何額外參數或 fine-tuning，可作為 plug-and-play 的 inference-time intervention 直接插進 CUT3R。這段方法敘事為實驗章節想驗證的命題——「training-free 改動就能換來 length generalization」——立下精確且可被驗證的承諾。

### 3.5 Experiments (overview narrative)

(330 words)

Experiments 章節的敘事重點是檢驗 §3 提出的 confidence-guided update rule 是否真的能在不付出額外計算成本下換來 length generalization，並且把驗證面向涵蓋從 pose、depth 到 dense reconstruction 的完整 3D reconstruction 任務鏈。

開場 baseline 段直接劃定對照組：CUT3R 是 TTT3R 的直接修補對象、Point3R 與 StreamVGGT 是分別走 explicit pointmap memory 與 KV-cache state 路線的延伸方案，VGGT 則作為 offline、full-attention 的 upper bound。比較維度刻意設定為三軸——reconstruction accuracy、GPU memory、inference speed——直接呼應 Introduction 中對「length generalization 但維持 RNN 記憶體優勢」的承諾。

4.1 Camera Pose Estimation 在 TUM dynamics 與 ScanNet 上以 ATE 為主指標，並用 Sim(3) alignment 移除尺度自由度。輸入 view 數從 50 掃到 1000，把 length generalization 變成可量化的曲線。這裡同時搭配 Figure 6 與 Figure 2 報告 FPS 與 peak GPU memory，讓「TTT3R 與 CUT3R 同等效率但 $2\times$ 精度」成為單張圖就能讀出的結論。

4.2 Video Depth Estimation 在 KITTI 與 Bonn 上同時報告 scale-invariant relative depth (Abs Rel、$\delta < 1.25$) 與 metric depth (僅限會輸出 metric pointmap 的 CUT3R、Point3R、TTT3R)。這個雙指標設計回應一個潛在質疑：long-sequence 上 Point3R 是否本來就贏？作者讓資料說話——Point3R 在 $\leq 300$ 幀內的 scale-invariant 表現很強，但在更長序列與 metric 尺度上明顯退化。

4.3 3D Reconstruction 在 7-scene 上以 chamfer distance 與 normal consistency 衡量幾何精度與表面品質，並刻意改用 long image sequence 而非過去文獻常用的 3–5 frame 稀疏取樣，把實驗難度拉到能凸顯 memorization capability 的層級。

整個實驗章節維持一條一致的故事線：在 short sequence 與 SOTA 持平、在 long sequence 顯著領先、且運算成本與 CUT3R 完全一致。Figure 7、8、9 各自把 length generalization 畫成曲線，使「training-free 改動換得 length 上的單調勝出」成為跨任務、跨資料集都成立的觀察，為 §5 Discussion 收斂結論留下充分的證據基礎。

### 3.6 Conclusion / Limitations / Future Work

(260 words)

Discussion 章節以三個段落分層收束：總結貢獻、誠實標記未解問題、開放後續研究方向。

開場段重申 TTT3R 的兩個層次貢獻：在概念層提供 Test-Time Training 視角來檢視當代 3D reconstruction foundation model；在工程層提供一個對 CUT3R 的簡單修補來顯著提升 length generalization。作者強調這個修補是在 forward pass 中完成、沒有 fine-tuning，因此屬於 lightweight、plug-and-play 的解。這個敘事呼應 Introduction 對 training-free 與 closed-form 的承諾，也讓讀者把整篇論文記住為「一個視角加一條 update rule」。

Limitations 段則誠實面對兩個未竟之處：第一，TTT3R 緩解但並未根除 state forgetting；第二，重建精度仍未追上 VGGT 這類 full-attention offline 方法——後者雖然慢且記憶體龐大，卻能完整保留歷史 context。作者把這個現象連結到 unexplored states hypothesis，亦即模型在短 context 上訓練時，其 recurrence 會把 state 帶到訓練未覆蓋的 OOD 區域，因此長序列泛化困難。為此作者提出一個可選的 TTT3R + State Reset 變體：週期性把 state 重置到初始值以避免 state overfitting，再用 global metric pose 對齊 chunk，無需額外優化即可保留 CUT3R 的速度與記憶體優勢。詳細設計留給 Sec. B in Sup.Mat。

Future Work 段把視野拉開：作者指出 test-time regression 在 associative recall 上展現的潛力之外，整個 design space 仍大量未被探索，並援引 Titans、TTT-done-right 等近期工作，主張開發更穩定、更可平行化的 recurrent architecture 是值得追求的長線方向。這個結尾邀請社群把 3D reconstruction foundation model 的設計與 modern RNN 的研究綁在一起，為下一代模型留出開放問題。

## 4. Critical Profile

### 4.1 Highlights

1. 將 RNN 式 3D 重建模型 (CUT3R) 重新詮釋為 Test-Time Training (TTT) 框架,把狀態 $S_t$ 視為由凍結骨幹當作 meta-learner 所驅動的 fast weight (Sec. 3.2, Fig. 3)。
2. 從理論上指出 CUT3R 之災難性遺忘的根因:softmax cross-attention 強迫權重沿觀察 token 維度歸一化為 $1.0$,等同於把學習率釘死在 $\beta_t = 1.0$ (Eq. 6, p. 6)。
3. 提出閉式狀態更新規則 $\beta_t = \sigma(\sum_m Q_{S_{t-1}} K^\top_{X_t})$,以 state query 與 observation key 之對齊置信度作為 per-token 學習率 (Eq. 7-8, p. 6-7)。
4. 整套修改完全不需微調、不引入任何新參數、不增加 FLOPs,直接重用 CUT3R 內部已計算的 cross-attention 分數 (Sec. 3.3, p. 7)。
5. 在 ScanNet 與 TUM-D 1000-frame 長序列 ATE 上對 CUT3R 取得約 $2\times$ 提升,且優於 Point3R 與 StreamVGGT (Fig. 7, p. 8)。
6. 推論成本維持線性時間與固定記憶體:單張 48GB GPU 上以 20 FPS 處理 1000 張影像、僅佔用 6GB;VGGT 與 Point3R 則在 700 frame 前即 OOM (Fig. 2、Fig. 6, p. 2/7)。
7. 在 7-scene 長序列 3D 重建上,Chamfer Distance 與 Normal Consistency 皆顯著優於 CUT3R,且 Chamfer 低於 Point3R,接近 offline 上界 VGGT (Fig. 9, p. 9)。
8. 對 KITTI 與 Bonn 的 metric depth,TTT3R 是唯一在長序列 ($>300$ frames) 仍持續優於 CUT3R 與 Point3R 的線上方法 (Fig. 8, p. 8)。
9. 與三種可學習的 gating 機制 (ScalarLR、ConditionLR、TokenLR) 在相同訓練預算下比較,training-free 的 TTT3R 反而全面勝出 (Table 1、Fig. 11, p. 18)。
10. 與三種非 TTT 啟發的 baseline (Reset、EMA、BurnIn) 比較,TTT3R 全面領先,並可與 Reset 疊加進一步取得最佳整體結果 (Table 5、Fig. 12, p. 19)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- TTT3R 只緩解但未根除 state forgetting,序列超過 $1000$ frames 時仍會崩潰 (Sec. 5, p. 10; Fig. 14, p. 21)。
- 與 offline 全注意力 VGGT 相比仍存在精度差距,因為 full attention 完整保留歷史 (Sec. 5, p. 10; Table 6, p. 22)。
- 短序列 ($\leq 64$ frames) 訓練範圍內,TTT3R 相對 CUT3R 的提升有限 (Sec. A.2, p. 18; Fig. 7)。
- 套用 TTT3R 更新規則重訓反而讓 video depth 退步,僅在 pose 上有微幅改善 (Sec. A.2、Table 1, p. 18)。
- 失敗根因被歸於 unexplored states hypothesis:短序列訓練的模型在長序列下狀態進入訓練未見過的分布 (Sec. B, p. 20)。
- State Reset 機制需要每 $100$ frames 重置一次,並依賴 global metric pose 對齊各 chunk,實際上是 chunk-level 拼接 (Sec. B, p. 20)。

#### 4.2.2 Phyra-inferred

1. **短序列「best among online」的主張站不住**:Table 6 (p. 22) 顯示 ScanNet 90-frame ATE 上 TTT3R (0.064) 輸給並列工作 STream3R (0.052),Sintel ATE 上也僅以 0.201 vs 0.213 微幅領先,RPE rot 落後 STream3R;Sec. C.3 卻仍稱 "best overall performance among online methods",這只在加權 TUM-dynamics 後才成立。
2. **「$2\times$ pose 提升」的對比基準是已知會遺忘的 CUT3R**:Fig. 7 中當 frame 數 $\leq 700$ 時 Point3R 的 ATE 並未明顯落後,$2\times$ 改善並非相對當前最強 online 方法。
3. **Fig. 1 主視覺與 abstract 描述暗中啟用 State Reset**:Sec. B 自承 Fig. 1 與 Fig. 15 都使用 State Reset,但 abstract 描述「process thousands of images」沒有提示讀者主圖效果其實依賴每 100 frame 重置加 global pose chunk alignment,容易讓讀者誤認為純粹是 TTT 更新規則所致。
4. **閉式公式並非嚴格推導**:Eq. 8 (p. 7) 直接把 $\beta_t = 1.0$ 替換成 $\sigma(\sum_m Q K^\top)$,作者用「對齊置信度」直覺串聯 DeltaNet 框架,但並未證明此選擇對任何 loss surface 是最優的、也未推導與 GLA 之間的等價條件,屬於 motivated heuristic 而非真正的 closed-form derivation。
5. **可學習 gating 受訓練長度限制的論點未實證**:Sec. A.1 (p. 18) 主張 TokenLR 之所以輸是因為只能用 64-frame 訓練,但作者沒有以稍長 (例如 128 或 256 frame) 訓練序列重做 ablation,「若能訓更長就會贏」的反事實缺乏實證。
6. **方法泛用性僅在單一基底模型驗證**:全文只把 reformulation 套在 CUT3R 上,未對 Point3R、Spann3R 或其他 RNN-style 重建模型施加同樣的 closed-form $\beta_t$,因此「TTT framework for stateful 3D reconstruction」的泛用性主張僅有 $n=1$ 的證據。
7. **長序列 benchmark 多樣性不足**:1000-frame 量化實驗只跑 ScanNet 與 TUM-D 兩個室內資料集,Fig. 9 的 7-scene 也僅到 400 frame,缺少室外、動態、driving (KITTI 只到 500 frame depth) 在 $>1000$ frame 的量化結果,「scale to thousands of images」主要靠 in-the-wild qualitative (Fig. 15) 支撐。
8. **缺少對 $\sigma$ 飽和區域的分析**:論文沒有討論為何 mean-over-spatial 比 softmax 更適合作 per-token gate,也未回答 sigmoid 飽和是否導致部分 state token 從某時刻起永遠拿到接近 $1$ 的學習率而被過度覆寫。

### 4.3 Phyra's Judgment (summary)

真正新穎的是「診斷加極簡修補」:把 CUT3R 內部既有的 cross-attention 分數重新詮釋為 TTT 框架中的 per-token 學習率,並指出 softmax 等同把 $\beta_t$ 釘在 $1.0$ 是遺忘的結構性根因。改寫本身只是把 softmax 替換成 $\sigma(\text{mean})$,完全不改參數、不重訓,本質上是對既有模型內部訊號的再利用,屬於工程級巧思而非新演算法。核心未解問題是 state forgetting 仍未根除 ($>1000$ frame 仍需 State Reset 才能存活),且論文未解答「什麼樣的 $\beta_t$ 函數族真正最佳」。

## 5. Methodology Deep Dive

### 5.1 Method Overview

TTT3R 將 CUT3R 的 recurrent state update 重新詮釋為 Test-Time Training (TTT) 框架下的 online learning 步驟。在此觀點下,固定大小的 state $S_{t-1} \in \mathbb{R}^{n \times c}$ 被視為在測試時透過 gradient descent 動態更新的 fast weight,而 backbone 的 frozen 權重則作為 slow weights,扮演 meta-learner 的角色,從訓練資料中學到如何指導 fast weight 的線上更新 (Sec. 3.2)。原始 CUT3R 的 update 規則為 $S_t = S_{t-1} + \texttt{softmax}(Q_{S_{t-1}} K_{X_t}^\top) V_{X_t}$ (Eq. 3),作者將其改寫為 TTT 形式 $S_t = S_{t-1} - \beta_t \nabla(S_{t-1}, X_t)$,並指出此式中的 $\beta_t \equiv 1.0$,即 softmax 沿 observation token 維度歸一化的副作用 (Eq. 6)。

這個診斷揭示了 CUT3R 長序列泛化失敗的根本原因:固定的 unit learning rate 強迫每一步都把新觀察完全寫入 state,造成 catastrophic forgetting。TTT3R 的核心介入是將此固定值替換為一個由 cross-attention 對齊置信度導出的 per-token learning rate $\beta_t \in \mathbb{R}^{n \times 1}$:當 state token 與當前觀察的 key 對齊分數高時(代表觀察與歷史記憶一致),對該 token 施加較大的更新;對齊分數低時則保留歷史。此 learning rate 的計算重用了 update 內部本來就要計算的 alignment matrix $Q_{S_{t-1}} K_{X_t}^\top$,因此沒有新增任何參數或計算成本 (Eq. 7)。

最終的 closed-form update 為 $S_t = S_{t-1} - \beta_t \nabla(S_{t-1}, X_t)$,其中 $\nabla = -\texttt{softmax}(Q_{S_{t-1}} K_{X_t}^\top) V_{X_t}$ (Eq. 8)。此設計與 Gated Linear Attention 的 per-token learning rate 形式一致,將 CUT3R 嚴格嵌入 TTT 框架,並提供一個 training-free、plug-and-play 的長序列泛化方案,可直接套用到 frozen 的 CUT3R checkpoint 上而不需任何 fine-tuning。

### 5.2 Pipeline Diagram with Tensor Shapes

The figure on page 6 (Figure 4(b)) grounds the recurrent update path below: 將 CUT3R 的 vanilla update (上半) 替換為加入 per-token learning rate $\beta_t$ 的 confidence-guided update (下半),read-out 路徑保持不變。

```
Input: I_t ∈ ℝ^[B, 3, H, W]                                (one RGB frame at time t)
   │
   │   Tokenize  (CroCo / DINO ViT, patch size p)
   ↓
X_t (image tokens)                              shape: [B, h*w, c]    h=H/p, w=W/p
   │
   ├──────────────────────────────────────────────────────────────────────┐
   │                                                                      │
   │   Linear projections                                                 │
   ↓                                                                      │
   K_{X_t}, V_{X_t} ∈ [B, h*w, c]      Q_{X_t} ∈ [B, h*w, c]              │
                                                                          │
   ┌── S_{t-1} ∈ [B, n, c]  (fast weight from previous step)              │
   │       │                                                              │
   │       │   Linear projection                                          │
   │       ↓                                                              │
   │   Q_{S_{t-1}} ∈ [B, n, c]                                            │
   │                                                                      │
   │   ┌── Cross-attention alignment ────────────────────────────────┐    │
   │   │   A_t = Q_{S_{t-1}} K_{X_t}^⊤              shape: [B, n, h*w]    │
   │   └────────────────────┬───────────────────┬───────────────────┘    │
   │                        │                   │                         │
   │   Confidence-guided LR │                   │ Gradient                │
   │   (Eq. 7)              ↓                   ↓ (Eq. 6 / 8)             │
   │   β_t = σ( mean_m A_t )                ∇ = - softmax(A_t) V_{X_t}    │
   │   shape: [B, n, 1]                     shape: [B, n, c]              │
   │                        │                   │                         │
   │                        └─────┬─────────────┘                         │
   │                              ↓                                       │
   │   State update (Eq. 8): S_t = S_{t-1} - β_t ⊙ ∇                      │
   │   shape: [B, n, c]                                                   │
   │                                                                      │
   └──────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  │   Linear projections on S_t
                                  ↓
                              K_{S_t}, V_{S_t} ∈ [B, n, c]
                                  │
   Readout (Eq. 1, cross-attn from X_t to S_t):
   Y_t = X_t + softmax( Q_{X_t} K_{S_t}^⊤ ) V_{S_t}        shape: [B, h*w, c]
                                  │
                                  ↓   De-tokenize (Linear + PixelShuffle, DPT head)
                          P_t (pointmap)                    shape: [B, H, W, 3]
                                  │
              ┌───────────────────┼───────────────────────────────┐
              ↓                                                   ↓
   PnP + Weiszfeld solver                              MLP / trunk attention
   (on pixel-aligned P_t)                              (on tokens X_t)
              ↓                                                   ↓
   T_t (camera pose)                                   C_t (camera intrinsics)
   shape: [B, 3, 4]                                    shape: [B, 3, 3]
```

### 5.3 Per-Module Breakdown

#### 5.3.1 Image Tokenizer

**Function:** 將輸入影格 patchify 並嵌入為 image tokens,作為後續 cross-attention 的 observation 來源。

**Input:**
- Name: $I_t$
- Shape: `[B, 3, H, W]`
- Source: streaming RGB image at time $t$ (data input)

**Output:**
- Name: $X_t$
- Shape: `[B, h*w, c]`
- Consumer: Q/K/V Linear Projections (§5.3.2)

**Processing:**

ViT-style 的 patch embedding,以 patch size $p$ 將 $H \times W$ 影像切成 $h \times w$ 個 patch (其中 $h = H/p, w = W/p$),每個 patch 經過線性投影與 positional encoding 後得到 channel 維度為 $c$ 的 token。This corresponds to $X_t = \texttt{Tokenize}(I_t)$ in Eq. 1.

**Key Formulas:**

$$
X_t = \texttt{Tokenize}(I_t) \in \mathbb{R}^{(h \times w) \times c}
$$

**Implementation Details:**

The paper specifies the tokenizer is either a DINO-style [15, 53] or CroCo-style [92, 93] ViT backbone, inheriting CUT3R's frozen configuration. Patch size $p$, channel dimension $c$, and exact backbone (e.g. ViT-Base vs. ViT-Large) are not specified in the TTT3R paper itself — they follow CUT3R [89]. 因為 TTT3R 是 training-free 的 inference-time intervention,tokenizer 完全凍結,沒有額外初始化或學習率設定。

#### 5.3.2 Q / K / V Linear Projections

**Function:** 將 state 與 observation tokens 線性投影到 query / key / value 子空間,提供後續 cross-attention 與 update 所需的所有矩陣。

**Input:**
- Name: $X_t$, $S_{t-1}$
- Shape: `[B, h*w, c]`, `[B, n, c]`
- Source: Image Tokenizer (§5.3.1) and State Update (§5.3.5) at previous step

**Output:**
- Names: $Q_{S_{t-1}}, K_{X_t}, V_{X_t}, Q_{X_t}, K_{S_t}, V_{S_t}$
- Shapes: $Q_{S_{t-1}}, K_{S_t}, V_{S_t} \in $ `[B, n, c]`; $Q_{X_t}, K_{X_t}, V_{X_t} \in $ `[B, h*w, c]`
- Consumer: Cross-Attention Alignment (§5.3.3) for the update path; Readout (§5.3.6) for the readout path

**Processing:**

Independent linear layers (沿用 CUT3R 的權重) 將 $X_t$ 與 $S_{t-1}$ 投影到 query / key / value。Update path 需要 $Q_{S_{t-1}}, K_{X_t}, V_{X_t}$;readout path 需要 $Q_{X_t}, K_{S_t}, V_{S_t}$。

**Key Formulas:**

對於 update path,$Q_{S_{t-1}}$ 透過對 $S_{t-1}$ 套用線性轉換得到,$K_{X_t}, V_{X_t}$ 則由 $X_t$ 線性投影。所有投影矩陣在 inference 時凍結。

**Implementation Details:**

The paper does not specify whether these projections are single-head or multi-head, nor the exact channel split — these inherit from CUT3R [89]. 所有線性層在 TTT3R 中均凍結,沒有重新訓練。

#### 5.3.3 Cross-Attention Alignment

**Function:** 計算 state queries 與 observation keys 之間的 alignment scores,作為「該寫入哪個 state token」的訊號;同一個 alignment matrix 同時被 §5.3.4 (LR 計算) 與 §5.3.5 (gradient 計算) 重用,因此不增加額外計算成本。

**Input:**
- Names: $Q_{S_{t-1}}, K_{X_t}$
- Shapes: `[B, n, c]`, `[B, h*w, c]`
- Source: Q/K/V Linear Projections (§5.3.2)

**Output:**
- Name: $A_t = Q_{S_{t-1}} K_{X_t}^\top$
- Shape: `[B, n, h*w]`
- Consumer: Confidence-Guided Per-Token Learning Rate (§5.3.4) and Closed-Form State Update gradient term (§5.3.5)

**Processing:**

Standard cross-attention score 計算,以 batched matrix multiplication 將 $Q_{S_{t-1}} \in \mathbb{R}^{n \times c}$ 與 $K_{X_t}^\top \in \mathbb{R}^{c \times (h \times w)}$ 相乘。每一列代表某個 state token 對所有 spatial observation tokens 的 alignment 分布。

**Key Formulas:**

$$
A_t = Q_{S_{t-1}} K_{X_t}^\top \in \mathbb{R}^{n \times (h \times w)}
$$

**Implementation Details:**

The paper does not mention attention scaling (如 $1/\sqrt{c}$);沿用 CUT3R 的實作。重點是同一個 $A_t$ 同時被 softmax 化用於 gradient 計算 (§5.3.5),也被 mean-over-$m$ + sigmoid 化用於 $\beta_t$ 計算 (§5.3.4),因此 TTT3R 相對於 CUT3R 的額外開銷僅為一個 mean reduction 與一個 sigmoid。

#### 5.3.4 Confidence-Guided Per-Token Learning Rate (Eq. 7)

**Function:** 將 cross-attention alignment 的整體置信度轉換為一個 per-state-token 的 scalar learning rate $\beta_t$,扮演 update 的 soft gate 角色。This is the central novelty of TTT3R.

**Input:**
- Name: $A_t = Q_{S_{t-1}} K_{X_t}^\top$
- Shape: `[B, n, h*w]`
- Source: Cross-Attention Alignment (§5.3.3)

**Output:**
- Name: $\beta_t$
- Shape: `[B, n, 1]`
- Consumer: Closed-Form State Update (§5.3.5)

**Processing:**

對 $A_t$ 沿 spatial 維度 $m = \{1, \ldots, h\} \times \{1, \ldots, w\}$ 取 mean,再經過 sigmoid 得到每個 state token 的 scalar learning rate。直觀上,當某個 state token $i$ 對所有 observation tokens 的平均對齊分數高時,代表當前觀察與該 state token 所編碼的歷史資訊一致(低不確定度),對應的 $\beta_{t,i}$ 接近 1,update 強度大;反之則 $\beta_{t,i}$ 接近 0,保留歷史 state。

**Key Formulas:**

$$
\beta_t = \sigma\!\left(\textstyle\sum_m Q_{S_{t-1}} K_{X_t}^\top\right) \in \mathbb{R}^{n \times 1}
$$

其中 $\sum_m$ 採作者的 normalized 慣例 $\sum_m \equiv \tfrac{1}{m} \sum_{i=1}^{m}$,亦即沿 $h \times w$ 維度取 mean (Eq. 7)。

**Implementation Details:**

形式上與 Gated Linear Attention [97] 的 per-token learning rate 一致 (Sec. 3.2)。Sigmoid 將 raw alignment magnitude 壓縮到 $(0, 1)$。No new learnable parameters: 所需的 $Q_{S_{t-1}}, K_{X_t}$ 已由 §5.3.2 從 frozen CUT3R 權重產生,因此這個 LR 是「免費」的。Figure 5 (page 7) 視覺化了 image attention 作為 $\beta_t$ 的效果,顯示 textureless 區域對應低 $\beta_t$,有效抑制低品質的 state update。

#### 5.3.5 Closed-Form State Update (Eq. 8)

**Function:** 以 gradient descent 形式更新 fast-weight state,結合 §5.3.4 的 per-token learning rate 與 §5.3.3 的 alignment-driven gradient。

**Input:**
- Names: $S_{t-1}$, $\beta_t$, and inputs $A_t, V_{X_t}$ for the gradient term
- Shapes: $S_{t-1} \in $ `[B, n, c]`, $\beta_t \in $ `[B, n, 1]`, $A_t \in $ `[B, n, h*w]`, $V_{X_t} \in $ `[B, h*w, c]`
- Source: previous-step state, §5.3.4, §5.3.3, §5.3.2

**Output:**
- Name: $S_t$
- Shape: `[B, n, c]`
- Consumer: Readout (§5.3.6) at current step; State Update (§5.3.5) at the next step (recurrence)

**Processing:**

先以 row-wise softmax 將 $A_t$ 沿 observation 維度 $h \times w$ 歸一化,得到 attention weights;再與 $V_{X_t}$ 相乘得到 gradient $\nabla \in \mathbb{R}^{n \times c}$。最後以 element-wise 方式將 $\beta_t$ broadcast 到 $c$ 個 channel,對 $S_{t-1}$ 做 gradient descent step。

**Key Formulas:**

$$
\begin{aligned}
\nabla(S_{t-1}, X_t) &= -\,\texttt{softmax}\!\left(Q_{S_{t-1}} K_{X_t}^\top\right) V_{X_t} \in \mathbb{R}^{n \times c} \\[4pt]
S_t &= S_{t-1} - \beta_t \odot \nabla(S_{t-1}, X_t) \in \mathbb{R}^{n \times c}
\end{aligned}
$$

This is exactly Eq. 8 of the paper, with $\beta_t = \sigma(\sum_m Q_{S_{t-1}} K_{X_t}^\top)$.

**Implementation Details:**

完全 training-free:沒有新增參數,沒有 fine-tune。當 $\beta_t \equiv 1.0$ 時退化為 vanilla CUT3R 的 update (Eq. 3, Eq. 6)。$\odot$ 為沿 channel 維度的 broadcast multiplication ($\beta_t \in \mathbb{R}^{n \times 1}$ 廣播到 $\mathbb{R}^{n \times c}$)。Sec. 3.3 強調此 update 與 GLA 的 per-token LR 形式一致,並可作為 gated attention 的 soft gate,有助於 long-context extrapolation [59]。

#### 5.3.6 Readout & Pointmap De-tokenizer

**Function:** 從更新後的 state 讀出當前影格的 output token,再 decode 成 pixel-aligned pointmap。Read-out 路徑沿用 CUT3R,TTT3R 不修改此模組。

**Input:**
- Names: $X_t, S_t$ (and their projections $Q_{X_t}, K_{S_t}, V_{S_t}$)
- Shapes: $X_t \in$ `[B, h*w, c]`, $S_t \in$ `[B, n, c]`
- Source: §5.3.1 and §5.3.5

**Output:**
- Names: $Y_t$ (output token), $P_t$ (pointmap)
- Shapes: $Y_t \in$ `[B, h*w, c]`, $P_t \in$ `[B, H, W, 3]`
- Consumer: Camera Pose & Intrinsics Estimation (§5.3.7); $P_t$ is also the final 3D output

**Processing:**

Readout 為從 $X_t$ 對 $S_t$ 的 cross-attention,再加上 residual $X_t$。隨後將 $Y_t$ 透過 dense prediction de-tokenizer (linear + pixel shuffle [67] + DPT head [61]) decode 為 $H \times W$ 解析度的 pixel-aligned pointmap。

**Key Formulas:**

$$
Y_t = X_t + \texttt{softmax}\!\left(Q_{X_t} K_{S_t}^\top\right) V_{S_t},\qquad P_t = \texttt{De\text{-}tokenize}(Y_t)
$$

(Eq. 1, Eq. 2 line 2 inferred for the read direction.)

**Implementation Details:**

Pixel shuffle [67] 與 DPT head [61] 來自原 CUT3R/DUSt3R 一系的標準實作。在 TTT3R 中此模組同樣凍結,與 update 路徑共用同一份 frozen 權重。輸出 $P_t \in \mathbb{R}^{W \times H \times 3}$ 代表每一個像素的 3D 點座標,且這些 point 已對齊到一個 canonical 全域座標系 (Sec. 3.1)。

#### 5.3.7 Camera Pose & Intrinsics Estimation

**Function:** 從 pointmap (或 image tokens) 解出當前影格的 camera extrinsics $T_t$ 與 intrinsics $C_t$。

**Input:**
- Names: $P_t$ (primary), or $X_t$ (alternative path)
- Shapes: $P_t \in$ `[B, H, W, 3]`, $X_t \in$ `[B, h*w, c]`
- Source: §5.3.6 and §5.3.1

**Output:**
- Names: $T_t$ (camera extrinsics), $C_t$ (camera intrinsics)
- Shapes: $T_t \in \mathbb{R}^{3 \times 4}$, i.e. `[B, 3, 4]`; $C_t \in \mathbb{R}^{3 \times 3}$, i.e. `[B, 3, 3]`
- Consumer: downstream evaluation (camera pose estimation, video depth, 3D reconstruction; see §6 of the paper)

**Processing:**

論文提供兩條等價路徑 (Sec. 3.1):(1) 由 pixel-aligned pointmap $P_t$ 透過 PnP [41] + Weiszfeld [56] 求解 $T_t$ 與 $C_t$;(2) 從 image tokens $X_t$ 經由 MLP 或 trunk attention layers [86, 87] 直接 regress 出 pose 與 intrinsics。TTT3R 沿用 CUT3R 在這個模組的選擇,沒有修改。

**Key Formulas:**

The paper does not give explicit closed-form expressions for this module; PnP solves $\min_{T_t} \sum \|\pi(T_t \mathbf{P}_{t,i}) - \mathbf{u}_i\|$ (paraphrased) over pixel correspondences, and Weiszfeld is the iterated reweighted least-squares estimator used for the intrinsic component.

**Implementation Details:**

The paper does not specify which of the two paths is used for each downstream task — this is inherited from CUT3R [89]. 在 evaluation 時,Sim(3) alignment [81] 被套用在估出的相機軌跡與 ground truth 之間以計算 ATE (Sec. 4.1)。同樣地,此模組在 TTT3R 中完全凍結,所有的速度與精度提升均來自於 §5.3.4 與 §5.3.5 的 confidence-guided update。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| ScanNet [20] | Camera pose estimation、3D reconstruction | 室內 RGB-D 場景，長序列評估取 50–1000 views | test only（training-free 推論） |
| TUM-dynamics [71] | Camera pose estimation（動態場景） | RGB-D SLAM benchmark，長序列評估取至 1000 frames | test only |
| Sintel [13] | Camera pose estimation（短序列） | 50 frames per sequence | test only |
| KITTI [33] | Video depth estimation（metric, 室外） | 100–500 frames per sequence | test only |
| Bonn [55] | Video depth estimation（scale-invariant, 室內動態） | 100–500 frames per sequence | test only |
| 7-scenes [68] | 3D reconstruction | 室內 RGB-D，評估 50–400 views per scene | test only |

備註：TTT3R 為 training-free 介入，主論文不含模型訓練；附錄 A.2 的 finetune 變體沿用 CUT3R 的訓練資料、序列長度 4–64 frames，但本文僅用上述資料集做 inference 評估。

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| ATE (Absolute Translation Error, m) | Sim(3) 對齊後估計與 GT 相機軌跡的絕對位移誤差 | yes |
| RPE trans / RPE rot | Sim(3) 對齊後相鄰幀的相對平移／旋轉誤差 | no |
| Abs Rel | 預測深度與 GT 的絕對相對誤差，per-sequence scale 對齊 | yes（depth 主指標） |
| $\delta < 1.25$ | 預測深度落在 GT 1.25 倍區間內的比例 | yes（depth 主指標） |
| Chamfer Distance | 預測 pointmap 與 GT 點雲的 accuracy/completeness 平均距離 | yes（reconstruction 主指標） |
| Normal Consistency | 預測表面法向量與 GT 的一致性 | no |
| GPU Memory (GB) | 推論期峰值 GPU 記憶體佔用 | yes（efficiency 主訴求） |
| FPS | 每秒處理 frame 數 | yes（efficiency 主訴求） |

論文核心宣稱（"$2\times$ improvement in global pose estimation"、"20 FPS / 6 GB"）對應 ATE 與 GPU Memory / FPS 兩組指標。

### 6.3 Training and Inference Settings

- **Hardware**：所有方法在單張 48 GB NVIDIA GPU 上評估，input views 從 50 掃到 1000（OOM 即提前中止）；TTT3R 在 ScanNet 上以約 6 GB GPU memory、約 20 FPS 處理千張影像（§4 與 Fig. 2、Fig. 6）。
- **Training**：TTT3R 主結果為 training-free，僅修改 CUT3R 推論期的 state update rule，不需 fine-tune、不引入額外可學參數（§3.3）。
- **Finetune 變體（附錄 A.2）**：沿用 CUT3R 的訓練資料、序列長度 4–64 views；the paper does not specify optimizer、learning rate schedule、batch size、training steps。
- **Learnable gating ablation（附錄 A.1）**：凍結 encoder / decoder / output heads，只訓練新加入的 gating module（ScalarLR、ConditionLR、TokenLR），同樣使用 CUT3R 的資料與 4–64 views，受限於 48 GB GPU 無法訓練更長序列。
- **Inference**：online、forward-pass only；per-token learning rate $\beta_t = \sigma\bigl(\sum_m Q_{S_{t-1}} K_{X_t}^\top\bigr) \in \mathbb{R}^{n\times 1}$ 直接由 cross-attention alignment 算出（Eq. 7、Eq. 8）。
- **State Reset 變體（附錄 B）**：每 100 frames 將 state 重置為初值，chunk 之間以 global metric pose 對齊；除 Fig. 1、Fig. 13、Fig. 15 外，主論文量化結果均**不**使用 State Reset。

### 6.4 Main Results

長序列代表性數值（從 Fig. 7、Fig. 8、Fig. 9 視覺讀取，已標示估讀；表 6 為短序列 ScanNet 90 frames 的精確值）：

| Method | ScanNet ATE ↓（1000 views, m, 估讀） | TUM-D ATE ↓（1000 views, m, 估讀） | KITTI Abs Rel ↓（500 views, 估讀） | 7-scenes Chamfer ↓（400 views, 估讀） | Peak GPU @ 1000 views | FPS @ 1000 views |
| --- | --- | --- | --- | --- | --- | --- |
| VGGT [87]（offline） | OOM 約 200 views 後 | OOM 約 200 views 後 | OOM 約 150 views 後 | OOM 約 150 views 後 | >48 GB | OOM |
| StreamVGGT [106] | OOM 約 250 views 後 | OOM 約 250 views 後 | OOM 約 150 views 後 | OOM 約 150 views 後 | >48 GB | OOM |
| Point3R [95] | OOM 約 700 views 後 | OOM 約 700 views 後 | 約 0.13 | 較 CUT3R 改善但 >TTT3R | OOM | OOM |
| CUT3R [89] | 約 0.5–0.7 | 約 0.17 | 約 0.15 | 約 0.10–0.12（嚴重退化） | 約 6 GB（const） | 約 17–20 |
| **TTT3R (ours)** | **約 0.25–0.3** | **約 0.08** | **約 0.13** | **約 0.04** | **約 6 GB（const）** | **約 17–20** |

短序列 ScanNet（90 frames）ATE ↓ 摘錄自 Table 6：VGGT 0.035（offline 上界）、MASt3R 0.078、MonST3R 0.077、CUT3R 0.099、Point3R 0.106、StreamVGGT 0.161、STream3R 0.052、**TTT3R 0.064**。TTT3R 在 online 方法中最佳，但短序列上未追上 offline 的 VGGT。

核心定量訴求：相對於 CUT3R baseline，TTT3R 在長序列 pose 估計取得約 $2\times$ ATE 改善（§1、§4.1、Fig. 7），同時保持 CUT3R 等級的常數 GPU 記憶體與 real-time FPS（Fig. 2、Fig. 6），在 7-scenes 長序列重建上 Chamfer Distance 低於 Point3R、接近 offline 上界 VGGT（§4.3、Fig. 9）。

### 6.5 Ablation Studies

- **Learnable gating mechanism 對照（附錄 A.1，Table 1）**：在 CUT3R 加入 ScalarLR / ConditionLR / TokenLR 三種有參數的 gating，TokenLR 最強（TUM-D 1000 frames ATE 0.154、KITTI 500 frames Abs Rel 0.148），但仍顯著輸給 training-free 的 TTT3R（ATE 0.106、Abs Rel 0.131）。診斷性強：直接回答「閉式 confidence-derived 學習率是否必要」，並指出 learnable gating 因受限於 64-frame 訓練長度而吃虧。
- **Finetune TTT3R（附錄 A.2，Table 1、Fig. 11）**：以 4–64 views 微調，pose ATE 由 0.106 降至 0.091、但 depth $\delta < 1.25$ 由 86.9 降到 86.3。作者解讀為 finetune 偏向 global alignment，犧牲 per-view 預測；屬於誠實的 trade-off 報告。
- **Non-TTT baselines（附錄 A.3，Tables 2–5、Fig. 12）**：與 Reset / EMA / BurnIn 三種非 TTT 機制比較，對每個 baseline 先掃 hyperparameter（reset 週期、EMA shrinkage、burn-in interval）再用最佳值對打。TTT3R 全面勝出；TTT3R + Reset 進一步取得最佳 ATE 0.093 / Abs Rel 0.115。屬於診斷型 ablation，能回答「TTT 公式本身是否帶來增益、與 Reset 是否互補」。
- **State Reset 週期掃描（Table 2）**：50 / 100 / 150 frames 中 100 最佳；屬於必要的超參數選擇而非核心診斷。
- **缺口**：未對 confidence-guided learning rate 的關鍵設計做拆解（例如 $\sigma$ 與 mean-pool 的選擇、是否改用 max、是否拿掉 per-token 維度退化為 scalar），也未報告 random seeds 或變異數；對 head 數、state token 數 $n$、channel 維度 $c$ 等也未掃描——這些較像 sanity-check 的缺席而非已做過的 ablation。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — VGGT [87] 作為 offline full-attention 上界，並與同期 RNN/streaming SoTA Point3R [95]、StreamVGGT [106]、STream3R [40] 全數對打。
- [covered] Has cross-task / cross-dataset evaluation — 涵蓋 pose（ScanNet、TUM-D、Sintel）、video depth（KITTI、Bonn）、3D reconstruction（7-scenes）三項任務、共六個資料集。
- [covered] Has ablations that diagnose the new components — 附錄 A.1/A.3 直接對照 learnable gating 與非 TTT 機制，回答「為何要 TTT-derived 閉式 $\beta_t$」，屬於診斷而非 sanity check。
- [covered] Has a scaling study — Fig. 2、6、7、8、9 系統性將 input views 從 50 掃到 1000，主軸即為 length-generalization scaling。
- [covered] Has an efficiency / wall-clock comparison — Fig. 2 報告 GPU memory、Fig. 6 報告 FPS，並標示 OOM 點，與精度曲線並排呈現。
- [missing] Reports variance / standard deviation / multiple seeds — 全文表格與曲線皆為單次數值，未見誤差棒或多 seed。
- [partial] Releases code / weights / data sufficient for reproducibility — 摘要列出 project page `rover-xingyu.github.io/TTT3R`，但本文未明示是否同時釋出 inference code、checkpoints 與評估腳本，the paper does not specify。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

1. **以 TTT 視角統一 stateful 3D reconstruction 的分析框架**:概念上 supports (Sec. 3.2、Fig. 3),但「框架」本身不是可量化貢獻,僅作為敘事鷹架,沒有獨立 ablation。
2. **指出 softmax 強制 $\beta_t = 1.0$ 是 CUT3R 遺忘的結構根因**:supports;Eq. 6 的代數重寫直觀且正確,並可由 Sec. A.3 的 Reset/EMA/BurnIn baselines 全面落後 TTT3R 間接驗證 (Table 5)。
3. **closed-form per-token 學習率 $\beta_t = \sigma(\sum_m Q_{S_{t-1}} K^\top_{X_t})$ 解決長序列遺忘**:partially supports;在 ScanNet/TUM-D 1000-frame ATE (Fig. 7) 與 7-scene Chamfer (Fig. 9) 上明確優於 CUT3R 與 Point3R,但 Sec. 5 與 Fig. 14 自承超過 1000 frame 仍崩潰,「解決」應降級為「顯著緩解」。
4. **training-free、無額外計算/記憶體成本**:supports;Fig. 6 顯示 TTT3R 與 CUT3R FPS 曲線幾乎重合,Fig. 2 顯示 GPU 記憶體均維持 6GB 以下。
5. **$2\times$ 全域 pose 提升 + 20 FPS + 6GB 處理 1000 張影像**:supports for the magnitude claim against CUT3R baseline (Fig. 7);但若以「相對最強 online 競品」衡量則 overclaimed,Point3R 在 $\leq 700$ frames 範圍內並未顯著落後。

### 7.2 Fundamental Limitations of the Method

**固定大小 state 的資訊論上限不可被 gating 函數突破**:無論 $\beta_t$ 如何設計,狀態維度 $n \times c$ 對長序列輸入存在 lossy compression bound,因此 RNN 路線無法在資訊保留上達到 offline full-attention 的上界。TTT3R 把 CUT3R 內部訊號發揮到極致,但這條 plug-and-play 路徑無法縮小與 VGGT 之間的精度差距。

**$\beta_t$ 完全寄生於 cross-attention 訊號**:gate 與 gradient 共用同一組 $Q K^\top$,當 cross-attention 自身對齊錯誤 (textureless 區域、動態物件、運動模糊) 時,「對齊置信度」也會跟著錯,沒有獨立的 confidence 來源可以校正。Sec. 3.3 的圖示展示了 textureless 區域被低估,但作者並未提供更高層次的不確定度估計來補救。

**unexplored states 是 training-time 問題,inference-time 修補無法根治**:Sec. B 自承 $>1000$ frames 必須以 State Reset 切片才能存活,本質上把 streaming 重建退化為 chunked offline alignment,並依賴外部 global metric pose;這意味 TTT3R 是「短 horizon 內最佳化的後處理」,並未真正完成 streaming length generalization。

**公式與 CUT3R 的具體架構深度耦合**:推導需要骨幹恰好計算 $Q_{S_{t-1}} K^\top_{X_t}$ 這個對齊矩陣;對改用 KV-cache (StreamVGGT) 或 explicit point memory (Point3R) 的模型,此 closed-form 並不適用,因此「general TTT framework」的理論主張缺乏跨模型實證。

### 7.3 Citations Worth Tracking

1. **Ruiz & Gu 2025 [62] (Length Generalization in Recurrent Models)**:作者用以解釋 TTT3R 為何仍會在 $>1000$ frame 失敗;若想理解 State Reset 為何有效、以及未來如何根治 forgetting,這是必讀的 prior。
2. **Yang et al. 2023 [97] (Gated Linear Attention)**:TTT3R 的 per-token 學習率正對應 GLA 的 TokenLR 形式;比較兩者公式可看出 TTT3R 的「training-free」優勢與限制邊界。
3. **Sun et al. 2024 [73] (TTT for RNNs)**:fast/slow weights 的核心框架來源,理解此文後 Eq. 4-6 的代數重寫與「online learning」敘事才會落地。
4. **Behrouz et al. 2024 [6] (Titans)**:concurrent 的 test-time memory 方向,具備 explicit forget gate 與更豐富的 memory 結構,可作為 TTT3R 下一步可能的延伸方向。
5. **Wang et al. 2025 [89] (CUT3R)**:base model;TTT3R 的所有設計選擇 (state shape、cross-attention 形式、metric pose head) 都繼承自此,不讀此文無法判斷 TTT3R 改了什麼、沒改什麼。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] $\beta_t$ 的設計空間是否存在比 $\sigma(\text{mean})$ 更佳的選擇,例如 $\sigma(\max_m \cdot)$ 或 token-level entropy?
- [ ] 若以更長訓練序列 ($\geq 256$ frames) 訓 TokenLR,是否真能追上 training-free 的 TTT3R?Sec. A.1 缺少此實證。
- [ ] State Reset 的 $100$-frame chunk 大小是任務獨立還是場景相依?在 in-the-wild driving / outdoor video 上是否仍最佳?
- [ ] $\sigma(\cdot)$ 在輸入和值很大時飽和,是否導致部分 state token 從某時刻起永遠拿到接近 $1$ 的學習率而被過度覆寫,進而抹去早期可重用的長期記憶?
- [ ] 在 dynamic scenes 下 cross-attention 的對齊置信度本身就不可靠 (動態物件出現偏移峰值),此時 $\beta_t$ 是否會放大錯誤而非抑制?
- [ ] TTT3R 的 closed-form 更新能否直接遷移到其他 RNN 重建模型 (Spann3R、Point3R) 而不必重新推導?如果不行,「general framework」主張的邊界在哪?
- [ ] State Reset 加 global metric pose alignment 的失敗模式為何?metric pose 估錯時整段重建會如何崩,是否需要 fallback?

### 8.2 Improvement Directions

1. **以 max 或 entropy-weighted aggregation 取代 $\sum_m$**:把 Eq. 7 改為 $\beta_t = \sigma(\max_m Q_{S_{t-1}} K^\top_{X_t})$ 或以 attention entropy 作為 gate。Logical basis:associative recall 在意「最強匹配」而非「平均匹配」;若 attention 是 peaky,mean 會稀釋掉 confident match 訊號;entropy 則是更標準的「對齊不確定度」度量。
2. **以更長序列重新 finetune TTT3R 規則**:Sec. A.2 在 64-frame finetune 下 depth 退步,屬於 unexplored states 的訓練版本;改用 $256$ 至 $1024$ frame 訓練 (即便需要 gradient checkpointing) 應可同時改善 pose 與 depth。Logical basis:作者本人提出的 unexplored states hypothesis 直接指向此方向。
3. **跨模型驗證 TTT 重寫的通用性**:把同套 closed-form gating 套用到 Point3R 的 explicit memory update 與 Spann3R,檢驗框架是否真正通用。Logical basis:若僅在 CUT3R 上有效,「framework」主張應降為「CUT3R 特例」。
4. **凍結 closed-form gate 之上加可學習 residual**:保留 $\sigma(\sum_m Q K^\top)$ 作為先驗,額外加入小型 learnable residual gate 在 dynamic / textureless 場景中校正。Logical basis:在「training-free」與「fully trainable」之間插值,理論上能吸收兩端優點而代價極低。
5. **將 State Reset 換成 learnable forget gate**:目前 State Reset 是硬性周期清零並依賴 metric pose 對齊;改為輸入相依的 soft reset signal (類似 Mamba-2 的 selective state) 應可在不依賴外部對齊的前提下避免 unexplored states。Logical basis:soft reset 可被 backprop 訓練,擺脫對 global pose head 的隱性依賴。
