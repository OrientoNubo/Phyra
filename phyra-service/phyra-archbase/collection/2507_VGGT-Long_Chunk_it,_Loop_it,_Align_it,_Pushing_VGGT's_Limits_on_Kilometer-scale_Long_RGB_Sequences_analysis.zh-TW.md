<!-- type: paper-read-notes | generated: 2026-05-02 | lang: zh-TW -->

# VGGT-Long — VGGT-Long: Chunk it, Loop it, Align it, Pushing VGGT's Limits on Kilometer-scale Long RGB Sequences

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | VGGT-Long |
| Paper full title | VGGT-Long: Chunk it, Loop it, Align it, Pushing VGGT's Limits on Kilometer-scale Long RGB Sequences |
| arXiv ID | 2507.16443 |
| Release date | 2026-03-16 |
| Conference/Journal | arXiv preprint |
| Paper link (abs) | https://arxiv.org/abs/2507.16443 |
| PDF link | https://arxiv.org/pdf/2507.16443 |
| Code link | https://github.com/DengKaiCQ/VGGT-Long |
| Project page | — |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|-------------|-------------|----------|------|
| Kai Deng | College of Computer Science, Nankai University | [link](https://scholar.google.com/citations?hl=en&user=ZH9MilgAAAAJ) | first author |
| Zexin Ti | School of Intelligence Science and Technology, Nanjing University | — | co-author |
| Jiawei Xu | College of Computer Science, Nankai University | — | co-author |
| Jian Yang | College of Computer Science, Nankai University; School of Intelligence Science and Technology, Nanjing University | — | co-author |
| Jin Xie | School of Intelligence Science and Technology, Nanjing University | [link](https://csjinxie.github.io/) | corresponding author |

### 1.2 Keywords

VGGT, 3D reconstruction, monocular, long sequence, loop closure, Sim(3) alignment, chunk-based processing, foundation model

### 1.3 Related Lineage

| Key | Relation | Brief |
|-----|----------|-------|
| VGGT (Wang et al., 2025) | base model | VGGT-Long 直接以 VGGT 為核心 3D 基礎模型,在其輸出之 pointmap 與 confidence 上進行分塊與對齊 |
| MASt3R-SLAM (Murai et al., 2025) | baseline | 以 MASt3R 為基礎建構之 SLAM 系統,作為大規模序列重建的主要對手與比較對象 |
| DUSt3R (Wang et al., 2024) | predecessor | Transformer 端到端 3D 視覺基礎模型的開創者,VGGT 系列方法的直接前身 |
| MASt3R (Leroy et al., 2024) | predecessor | DUSt3R 的後續模型,提供無需校正的 3D 對應與相機參數估計能力 |
| CUT3R (Wang et al., 2025) | baseline | 另一個 Transformer-based 多視角重建方法,於長序列實驗中作為比較基準 |
| Fast3R (Yang et al., 2025) | baseline | 快速版本的 Transformer 3D 重建模型,因 drift 與記憶體限制無法處理長序列,作為比較對象 |
| VGGT-SLAM (Maggio et al., 2025) | concurrent | 同期工作,以 SL(4) factor graph 對齊 submap 建立 SLAM 系統,但聚焦室內場景 |

## 2. Research Overview

### 2.1 Research Topic

本研究聚焦於以單目 RGB 影片串流進行公里級、未經相機校正的 3D 場景重建,屬於自駕車場景下的長序列三維感知問題。作者觀察到近期以 Transformer 為基礎的 3D 視覺基礎模型(如 DUSt3R、MASt3R、CUT3R、Fast3R 與 VGGT)雖在小規模場景中能直接從未校正影像端到端輸出 pointmap 與相機參數,卻因自注意力的記憶體開銷與累積飄移,在數千幀的戶外長序列上完全無法執行或產生嚴重 drift。傳統 SLAM/SfM 雖具可擴展性,卻倚賴複雜的後端最佳化、特徵工程或已知內參。本論文以 KITTI、Waymo 與 Virtual KITTI 等戶外駕駛資料集為基準,探討如何以最小系統開銷釋放 VGGT 的 local 重建能力,使其能擴展至公里級的全域一致重建。

### 2.2 Domain Tags

- Computer Vision
- 3D Reconstruction
- SLAM
- Autonomous Driving

### 2.3 Core Architectures Used

- **VGGT (基礎模型)**:作為本論文的核心 3D 視覺基礎模型,負責在每個 chunk 內部端到端輸出 local pointmap、相機參數與 per-pixel confidence,是整套 chunk-and-align pipeline 的局部重建引擎。
- **ViT Encoder + Alternating Attention(VGGT 內部架構)**:VGGT 採用的 Transformer backbone,以交替 frame-wise 與 global self-attention 處理多視角影像,自注意力的二次方記憶體成本即是本論文要克服的根本瓶頸。
- **DINOv2-based Visual Place Recognition (VPR) 模型**:用於從每張影像萃取全域描述子 $d_i$,搭配 cosine similarity 與 NMS 進行 loop 候選偵測,是輕量 loop closure 模組的視覺前端。
- **IRLS + Huber + Weighted Umeyama 對齊器**:本論文提出的 confidence-aware Sim(3) 對齊器,在相鄰 chunks 重疊區以 Huber 損失與 VGGT confidence 加權迭代求解閉式 Umeyama,藉此自然壓制動態物與天空雜訊。
- **sim(3) 切空間 Levenberg–Marquardt 全域最佳化器**:將所有 chunk 變換 $\{S_k\}$ 與 loop 約束以 $\log_{\mathrm{Sim}(3)}$ 映射至 7 維 Lie 代數做非線性最小平方,刻意取代 pose graph / bundle adjustment,以維持「無 SLAM 後端」的極簡設計。

### 2.4 Core Argument

作者主張長序列 3D 重建效能不彰的根本原因並非基礎模型能力不足,而是 VGGT 等模型的記憶體上限(在 24 GiB 4090 GPU 上僅能處理約 60–80 張影像)使其無法吞下整段公里級序列,而既有將基礎模型整合進 SLAM 的方案(如 MASt3R-SLAM)又把問題歸結為需要 pose graph、bundle adjustment 等沉重後端,反而稀釋了基礎模型本身的價值。基於此,他們提出『chunk-and-align』的極簡哲學:將序列切成具重疊的 chunks,讓 VGGT 在每個 chunk 內部產出高品質的 local pointmap 與 confidence,再以 confidence-aware 的 IRLS(Huber + 加權 Umeyama)在重疊區估計相鄰 chunk 之間的 Sim(3) 變換,以此天然壓制天空、行人與快速移動車輛等動態雜訊。為解決 Sim(3) 累積 drift,他們以 VPR(DINOv2 backbone)做迴路偵測與 NMS 過濾,並針對每對候選 loop 重新組成跨時段的『loop-centric chunk』讓 VGGT 重新推論一次,以更寬基線得到高品質 loop 對齊,最後在 sim(3) 切空間以 Levenberg–Marquardt 對所有 chunk 變換做全域最小平方最佳化。整套設計刻意避開 factor graph 與 bundle adjustment,以證明只要基礎模型夠強,公里級全域一致重建可以不需要傳統 SLAM 後端,僅靠 chunking、對齊與輕量 loop 修正即可達成,且無需相機校正或深度監督。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(190 words)

標題 "VGGT-Long: Chunk it, Loop it, Align it, Pushing VGGT's Limits on Kilometer-scale Long RGB Sequences" 直接以三個動詞 (Chunk / Loop / Align) 預告全篇方法骨幹，並把目標限定在「公里級 long RGB sequence」這個非常具體的尺度上。副標 "Pushing VGGT's Limits" 也明確表態：本文不重新訓練模型，而是想把既有的 VGGT 推到它原本能力的邊界之外。

Abstract 採用「現況 → 痛點 → 我們的對策 → 結果」四段式佈局。第一句先承認 3D foundation model 在感知能力上已有突破，第二句立刻點出 memory limitation 才是把這些模型搬到大規模 RGB stream 上的真正瓶頸。接著提出 VGGT-Long 的三個關鍵字：chunk-based processing、overlapping alignment、lightweight loop closure optimization，並且強調三個「不需要」：no camera calibration、no depth supervision、no model retraining，讓讀者立即理解這是一個 plug-on top of VGGT 的後處理框架而非新模型。

最後段交代評測範圍 (KITTI、Waymo、Virtual KITTI) 並聲稱在 foundation model 通常 fail 的 long sequence 上仍能得到 accurate and consistent geometry，把全文定位成「將 foundation model 帶入 autonomous driving 級的真實場景」。Abstract 在邏輯上鋪好了 §1 Introduction 要展開的 scalability gap 與 minimalist philosophy。

### 3.2 Introduction

(720 words)

Introduction 採用 problem-framing → paradigm-review → bottleneck-diagnosis → philosophy-statement → contributions 的五段式結構，是全篇論證鏈的縮影。

第一段先定義場景：autonomous driving 的 monocular RGB stream 與 indoor 小場景在 trajectory length、frame correspondence sparsity、dynamic object、weather 上有本質差異。作者藉此排除掉所有 "依賴 LiDAR / IMU / stereo" 或 "假設 known intrinsics" 的工作 (refs [3, 6, 44, 45, 46, 47])，把研究問題收斂成 "scalable, calibration-free monocular RGB reconstruction"，並聲稱這是 autonomous system 的關鍵需求。

第二段把鏡頭轉到 3D vision 的 foundation model 浪潮，依時間軸列出 DUSt3R → MASt3R → CUT3R → Fast3R → VGGT 的演化，強調這條線想用單一深度模型取代 SfM/SLAM 的 multi-component pipeline，並能 backprop 全系統。但作者隨即作出一個關鍵分流判斷：CUT3R 與 Fast3R 即便在幾十個 frame 的短序列上仍 drift 嚴重，而 VGGT 雖然 local reconstruction quality 是 SOTA，瓶頸卻在 compute and memory，而不是模型能力本身。這個診斷把後續所有設計合理化。

第三段量化這個 memory bottleneck：self-attention 是 quadratic scaling，Flash-Attention 雖把 compute 降到 linear，但 GPU memory 仍不可承受；具體數字是 VGGT 在 24 GiB RTX 4090 上只能處理 60–80 張影像，而 KITTI Seq 00 約 4,600 frame，硬體需求遠超現況。這段把 "scalability" 從一個抽象詞變成一個可度量的硬限制。

第四段轉向哲學立場。作者以 MASt3R-SLAM 為對照組，指出該系統雖把 MASt3R 整合進 SLAM，但仍依賴 pose graph optimization 與 bundle adjustment 等 backend。作者提出本文的反命題："must large-scale reconstruction always equate to system-level complexity?"，並主張 minimalist approach：既然 VGGT 已是強大的 engine，問題只是 scalability，就應該 unlock 模型本身的潛能，而非再蓋一層 SLAM backend。

第五段把哲學落到方法名 "chunk-and-align" 上：overlapping chunk 處理、相鄰 chunk robust alignment、loop closure 修正 drift，明確聲明 "avoid the need for a graph-based optimization backend (such as bundle adjustment)"，並把這個結論抬升為論文 thesis："a sufficiently powerful base model may not necessarily require a system-level backend to assist."

最後 contribution list 以三點收束：(1) 第一個把 monocular 3D reconstruction model 推到 kilometer-scale 無界戶外、且不需 calibration 與 depth supervision 的系統；(2) 提出 chunk-and-align pipeline 解決 memory limit、且能匹配 calibrated 傳統方法的精度；(3) 處理 long sequence 上的 accumulated Sim(3) drift，證明 VGGT 可作為大規模重建系統的 robust front-end。這三點剛好對應後續 §3.1、§3.2–§3.3、以及實驗章節的論證內容。

### 3.3 Related Work / Preliminaries

(440 words)

Related Work 分成三條線，逐一讓 VGGT-Long 在 SfM、SLAM、以及 Transformer-based 3D Vision 三個社群中找到自己的座標。

第一條線是 SfM。從經典 incremental pipeline (keypoint detection、feature matching、bundle adjustment) [1, 8, 26] 講起，承認其 robustness 但點名其在 textureless 與 ambiguous 場景的限制。接著引入 hybrid 與 fully differentiable 的學習化方向 (PixSfM、DFSfM、VGGSfM) [12, 16, 27, 31, 32, 37, 39]，指出它們改進了 track 與 structure，但 scalability 與 generalization 仍是痛點。這條線把作者的工作與「end-to-end learning 取代 classical SfM」的趨勢做出區隔：本文不取代 SfM，而是借用 foundation model 的局部能力。

第二條線是 SLAM 與 visual odometry。作者把傳統 SLAM [21, 22] 與 learning-based SLAM [14, 33] 並列，指出兩類方法或者 scale 不到 long sequence、或者依賴 pre-calibrated camera。重點放在 MASt3R-SLAM [23] 與 concurrent 的 VGGT-SLAM [19]：前者在 MASt3R 之上以 pose graph optimization 與 bundle adjustment 確保 global consistency；後者用 SL(4) factor graph 對齊 submap，主打 indoor 場景。作者在這裡明確把 VGGT-Long 定位為 "lightweight pipeline with Sim(3) transformations，prioritizing simplicity and scalability over a full SLAM framework"，呼應 §1 的 minimalist philosophy。

第三條線是 Transformer-based 3D vision。從 DUSt3R / MASt3R 的 uncalibrated pair-wise 估計講到 CUT3R、Fast3R，最後落點在 VGGT 的 SOTA local reconstruction quality，並反覆強調這條線共同的限制：computational/memory cost 把它們鎖死在短序列。這個共識正是 §1 所診斷的 bottleneck，也使讀者預期方法章節必然以 chunk + 對齊作為對策。

收尾段把全文 thesis 重申一次：相對於另起 SLAM 系統，本文選擇 unlock VGGT 的潛能，使用 chunk-and-align 把它擴展到 long-sequence、large-scale 場景，且 overhead 最小。本章不引入 preliminaries 級的數學定義 (Sim(3)、IRLS、Huber loss 等留待 §3 Method 才正式登場)，因此扮演的是「設定 baseline 與 contrast 對象」的角色，為 Method 章節的取捨理由 (例如為何用 Sim(3) 而非 SL(4)、為何不做 bundle adjustment) 做語境準備。

### 3.4 Method (overview narrative)

(280 words)

Method 章節以一段不到十行的 overview 統攝全篇，接著三個小節 (3.1 Sequence Chunking and Local Aligning with Confidence、3.2 Loop Detection and Loop-wise SIM(3) Aligning、3.3 Global SIM(3) LM-based Optimization) 依序對應 chunk → loop → align 的流程。Figure 2 提供 pipeline 圖：RGB stream (無 calibration) 進入 VGGT，得到 chunk-wise pointmap，進行 chunk-wise SIM(3) aligning；同時用 VPR 模型偵測 loop pair、做 NMS filter 後對 loop chunk 重新跑一次 VGGT，得到 loop-wise SIM(3) constraint；最後將 sequential 與 loop 兩類約束送入 LM-based loop correction optimization。

敘事邏輯是「從局部到全局、從序列到拓撲」。§3.1 解決短序列內的精度與 memory 問題：把長度為 $N$ 的 sequence 切成 $K$ 個 overlap 大小為 $O$ 的 chunk，每個 chunk 獨立丟給 VGGT 取得 pointmap $P_k$ 與 confidence $c_k$，再以 IRLS + Huber loss 在重疊區做 confidence-weighted 的 Sim(3) 對齊。這一步的精神是「相信 VGGT 對 dynamic object 的低 confidence 標記」，把 sky、oncoming vehicle、raindrop 等不利對齊的點自然濾掉 (Fig. 4)。

§3.2 解決 long sequence 的 drift 累積：用 DINOv2-based VPR [13] 對每張 frame 抽 global descriptor，做 cosine similarity nearest neighbour 加 NMS，挑出時間上距離夠遠的 loop pair；對每對 pair 把兩端各自鄰近 frame 串成一個 "loop-centric" batch 再丟給 VGGT，得到一個跨時段的高品質局部重建，再透過 $S_{ij} = S_{i,\text{loop}} \circ S^{-1}_{j,\text{loop}}$ 推出 loop closure 變換。

§3.3 把所有 sequential 與 loop constraint 寫成單一 Sim(3) 上的 nonlinear least squares，用 logSim(3) 對映到 7-D tangent space，再以 Levenberg–Marquardt 解，避免 factor graph 與 bundle adjustment 的工程負擔。整章節節相扣地落實 §1 的 minimalist 主張。

### 3.5 Experiments (overview narrative)

(370 words)

實驗章節 (§4) 以一段資料集與硬體設定開場，再分為 Metrics、Experiment Settings、CPU Memory Management Strategy、KITTI/Waymo/Virtual KITTI 主結果、以及 Loop Optimization Analysis & Ablation Study 五個子節。整體敘事採用「先界定評估方法、再展示通用性、最後拆解貢獻」三個層次。

§4.1–4.2 先把評估規則講清楚。tracking 採用 ATE (RMSE) [29]；reconstruction 沿用 VGGT 的 Accuracy / Completeness / Chamfer Distance。由於 monocular 重建有 scale ambiguity，所以先做粗對齊再用 ICP [25] 細對齊才計算 reconstruction metric；對所有 Transformer-based 方法統一保留 confidence > 0.75× 平均 confidence 的點，以避免 outlier 拖累指標。Inference 設定遵循 VGGT (518-pixel 寬)，並且先跑 VPR 再釋放其顯存，再讓 VGGT 拿到足夠資源。

§4.3 是一個工程細節節，但對 thesis 至關重要：為了讓 CPU memory 不在 KITTI Seq 00 這類規模上爆掉，作者設計把每個 chunk 的結果寫到磁碟、對齊時只 lazy-load 相關 pair，最後輸出採 stream writing。這把 §1 提到的 "memory bottleneck" 從 GPU 延伸到 CPU/RAM，補完整個 scalability 故事。

§4.4 是主結果展演。三個 dataset 各自挑一個敘事重點：KITTI 用來證明「在 foundation model 全部 OOM、MASt3R-SLAM tracking lost、傳統 calibrated SLAM 仍是強對手」的環境下，VGGT-Long 是 11 條序列中唯一能全部跑完、且 ATE 與 calibrated baseline 競爭的方法 (Table 1)；Waymo (Table 2、Table 3) 用來展示 urban 多樣場景下 tracking 與 point map 雙指標的領先，並提醒 LiDAR GT 對 overpass 等高處結構覆蓋不全，因此鼓勵讀者搭配 Fig. 10–13 看 visual；Virtual KITTI (Table 4) 用 fog/rain/sunset 等合成 domain shift 證明 robustness 不依賴 retraining 或 domain adaptation。作者也順帶解釋 baseline 失敗原因：MASt3R-SLAM 在長直路上長時間不產生新 keyframe 而 tracking lost；CUT3R 採類 NeRF 的 continuous state token，難以承載大規模戶外幾何細節。

§4.5 是論點收束。Table 5 報告 runtime，證明每個 chunk 約 2.6–2.8s、Sim(3) 對齊約 0.2s、LM 優化只需數毫秒就能在 3 個 iteration 內收斂；Table 6 的 ablation 把 LC、IRLS、confidence weight 三個元件逐一拆掉，顯示移除 LC 會讓 Seq 00 的 ATE 從 8.67 飆到 58.69，IRLS 對應約 13% 退化，最終三者全開最佳。這同時驗證「foundation model + minimalist back end」這一全篇主張。

### 3.6 Conclusion / Limitations / Future Work

(110 words)

§5 Conclusion 只有一段，且未獨立設置 Limitations 與 Future Work 子節，因此整體結束相當收斂。作者重述貢獻：VGGT-Long 是一個 simple yet effective 的框架，把 monocular RGB-only 3D reconstruction 拓展到 long、unbounded video sequence，並且不需 camera calibration 即可克服既有 3D vision foundation model 的 GPU memory 限制；KITTI、Waymo、Virtual KITTI 三個 dataset 的廣泛實驗證實該方法在真實與合成、市區與高速、晴天與雨霧等多重條件下都能維持 accurate 且 scalable 的 3D 重建。

論文沒有顯式列出 limitation，但行文中其實留下了線索：Fig. 8 已點出 KITTI Seq 08 因 2D RGB loop detection 在「同地點不同方向」失效而無法形成 loop；Waymo Seq 371159869 也提到 LiDAR GT 對高架結構覆蓋不足而使 metric 失真；MASt3R-SLAM 的 tracking lost 分析也暗示 keyframe sparsity 是 monocular 系統的共同弱點。Future Work 僅以一句話承諾「持續研究如何提升 3D foundation model 在長戶外序列上的 accuracy 與 consistency」，未具體承諾改 loop detection、加 dynamic object 模型或推進 real-time，因而把後續方向開放給社群延伸，而非自我綁定具體里程碑。整段在風格上呼應 §1 的 minimalist 主張：用最少的話收尾，把舞台留給結果與 thesis。

## 4. Critical Profile

### 4.1 Highlights

- 在 KITTI Odometry 11 條序列上,VGGT-Long 是唯一能完整跑完所有序列的 foundation-model-based 方法,反觀 VGGT、Fast3R、CUT3R 全部 OOM,MASt3R-SLAM 全部 Tracking Lost(Table 1, p. 7)。
- 不需相機內參、不需 depth supervision,在 chunk size 60 設定下 KITTI Avg.* (排除 Seq. 01) 達 ATE RMSE $19.298\,\text{m}$,優於 DROID-SLAM ($75.846\,\text{m}$) 與 DPV-SLAM++ ($27.138\,\text{m}$)(Table 1, p. 7)。
- 在 Waymo Open Dataset 9 個 segments 上 ATE 平均 $1.996\,\text{m}$,顯著低於 MASt3R-SLAM 的 $5.560\,\text{m}$ 與 CUT3R 的 $9.872\,\text{m}$(Table 2, p. 7)。
- 在 Waymo 的 point map 重建指標 Chamfer Distance 平均 $2.021\,\text{m}$,於全部 9 個 segments 上皆排名第一,擊敗 DROID-SLAM、MASt3R-SLAM、CUT3R(Table 3, p. 8)。
- Confidence-aware IRLS + weighted Umeyama 能自然抑制天空、行人與快速移動車輛對 Sim(3) 對齊的污染,作者更強調這比 LiDAR GT 還能更準確地剔除高密度動態車流(Fig. 4, p. 5)。
- Virtual KITTI 在 fog、rain、sunset、overcast 等 6 種條件下 ATE 全部維持穩定,All Avg. $2.0538\,\text{m}$,而 CUT3R 在相同設定下崩盤至 $38.0189\,\text{m}$(Table 4, p. 8)。
- 提出 loop-centric chunk 策略:對每對 VPR 候選 loop,把跨時段子序列重新組批送回 VGGT,使其以更寬基線重新推論,再以 $S_{ij} = S_{i,\text{loop}} \circ S_{j,\text{loop}}^{-1}$ 串接出 loop 約束(Fig. 5 與 Eq. 4, p. 5)。
- Global Sim(3) LM 最佳化在 sim(3) 切空間上對所有 chunk 變換做 unconstrained optimization,平均 3 次迭代收斂,C++ 實作每次迭代僅 $0.4\text{–}1.3\,\text{ms}$(Fig. 7, p. 5; Table 5, p. 9)。
- 整體 chunk 處理 $\sim 2.6\text{–}2.8\,\text{s/chunk}$、chunk align $\sim 0.2\,\text{s}$,加上磁碟 offload 策略,在 24 GiB RTX 4090 上即可處理 KITTI Seq. 00 (4542 frames) 等公里級序列(Table 5, p. 9; Sec. 4.3, p. 6)。
- Ablation 顯示拿掉 loop closure 會讓 Seq. 00 的 ATE 從 $8.67\,\text{m}$ 暴衝至 $58.69\,\text{m}$,確認 loop closure 是系統能在公里級維持精度的主要支柱(Table 6, p. 9)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- KITTI Seq. 08 在 3D 空間有重疊但對應不同行駛方向,純 2D RGB 的 VPR loop detection 無法辨識為 loop,因此 Avg.* 報表也保留 Seq. 08 的較高誤差作為已知缺陷(Fig. 8 caption, p. 12; Sec. 4.4, p. 7)。
- KITTI Seq. 01 為高速序列,運動模式與其他序列差異過大,作者另開 Avg.* 欄將其排除,等同承認方法在高速 ego-motion 下表現劣化(Table 1 caption, p. 7)。
- Waymo 的 LiDAR GT 因感測器架設高度低於攝影機,無法看到天橋等高處結構,導致重建指標數值僅供參考,作者明確要求讀者改看視覺對照圖(Table 3 caption, p. 8)。
- 在 Seq. 05 的中央十字路口仍可見部分區域未對齊,作者歸因為該段 RGB 影像沒有顯式 loop closure 約束(Sec. 4.4, p. 7;對應 Fig. 1)。
- 大於 chunk size 90 的設定無法在 24 GiB 4090 上跑,需切換到 48 GiB L20 GPU,代表 chunk size 與 GPU 記憶體之間有硬性綁定(Sec. 4, p. 6)。

#### 4.2.2 Phyra-inferred

- KITTI Avg.* 19.298 m 仍遠高於有 calibration 的 ORB-SLAM2 w/ LC 的 9.464 m(Table 1),作者標題宣稱「accuracy comparable to traditional methods」未明確標出此差距,在 KITTI 這類已校正基準上實際是落後的。
- Chunk size 是極敏感的超參數:同一 KITTI 平均 ATE 從 chunk 30 的 $39.564\,\text{m}$ 跳到 chunk 60 的 $19.298\,\text{m}$、chunk 90 的 $20.938\,\text{m}$、chunk 120 的 $22.814\,\text{m}$(Table 1),但全文未提供任何選擇 chunk size 的指引或自動化策略。
- Ablation Table 6 只比較單一序列且只移除單一元件,真正能撐起表現的是 loop closure(移除後 Seq. 00 ATE 上升 $\sim 6.8\times$),其餘 IRLS 與 confidence weight 各自只貢獻 $\sim 13\%$ 與類似量級,作者把三者並列為「all components yield optimal performance」過度均勻化了貢獻分布。
- VPR loop detection 完全沒有 recall / precision 指標,只報告閾值 $\tau_s$ 與 NMS 行為,因此「loop closure 顯著降誤差」無法從本論文證據判斷是來自高品質的 loop 偵測還是 loop-centric chunk 的對齊強度。
- 同期工作 VGGT-SLAM (Maggio et al., 2025) 在相關工作章節被點名為以 SL(4) factor graph 處理 submap 對齊的對手,卻在所有實驗表格中缺席,作者未說明是 VGGT-SLAM 不適用於戶外或單純未跑。
- Loop 之間 chunks 的 Sim(3) 變換是純鏈式串接,單一 chunk 對齊失敗會沿整段傳播,而論文未提供 chunk-pair 對齊失敗的偵測或回復機制(Sec. 3.1, p. 3)。
- Fig. 1 預告了 iPhone 14 Pro 拍攝的「Large Indoor Scene (465m)」案例,但全文沒有任何室內或手機影像的量化結果,該宣傳圖實質上未被實驗章節支持。
- Seq. 02 即使有 loop、且使用最佳 chunk 60 設定,ATE 仍高達 $34.16\,\text{m}$(Table 1),屬於含 loop 序列中的明顯異常點,論文未對此案例給出 failure analysis。

### 4.3 Phyra's Judgment (summary)

VGGT-Long 真正新的部分是「不要 factor graph、不要 bundle adjustment,把 foundation model 當夠強的 local engine,只靠 chunk 重疊區的 confidence-aware Sim(3) IRLS 與 loop-centric 重推論就能撐到公里級」這個系統哲學,而非任何單一演算法元件 (IRLS、Umeyama、VPR、Sim(3) LM 都是現成工具)。在工程上,它證明了 VGGT 加上極輕量縫合確實可以在 KITTI / Waymo / Virtual KITTI 上跑得動且重建品質可觀,但「accuracy comparable to traditional methods」在 calibration 充足的 KITTI 上其實仍落後 ORB-SLAM2 w/ LC。核心未解問題是:當 VPR 看不到 loop (反向行駛、長直道) 或 VGGT 在某 chunk 失敗時,本系統沒有任何 recovery 機制,這是「拒絕 SLAM 後端」哲學留下的代價。

## 5. Methodology Deep Dive

### 5.1 Method Overview

VGGT-Long 將公里級 RGB 序列分解為三個串接階段:**chunking + 局部對齊**、**loop detection + loop-wise 對齊**、以及 **global Sim(3) LM 最佳化**。第一階段以 sliding window 將輸入序列 $I=\{I_1,\dots,I_N\}$ 切成 $K$ 個有重疊的 chunks,每個 chunk 獨立餵給凍結的 VGGT,輸出 chunk-local 的 pointmap $P_k\in\mathbb{R}^{H\times W\times 3}$、confidence map $c_k\in\mathbb{R}^{H\times W}$ 與相機位姿。對相鄰 chunk 在重疊區的 3D 對應點,以 confidence-weighted IRLS(Huber loss + 加權 Umeyama)估計 Sim(3) 變換 $S_{k,k+1}$,使得天空、行人、迎面車等低 confidence 點被天然過濾;實作上更直接丟棄 confidence 低於整 chunk median 之 0.1 倍者(p. 4)。

第二階段以 DINOv2-backbone 的 VPR 模型對每張影像抽全域描述子 $d_i$,以 cosine similarity > $\tau_s$ 且 $|i-j|>\Delta t_{\min}$ 的條件挑出候選 loop pair,再以 NMS 在時間鄰域抑制冗餘配對。對每組 $(I_i,I_j)$,作者把以 $i$ 與 $j$ 為中心的兩段子序列拼成一個 *loop-centric chunk* 重新送進 VGGT,以更寬基線得到高品質局部重建,並用 $S_{ij}=S_{i,\text{loop}}\circ S_{j,\text{loop}}^{-1}$(式 4)組合出跨時段的 Sim(3) 約束。第三階段不建 factor graph,直接在 $\mathfrak{sim}(3)$ 切空間以 LM 最小化序列約束加 loop 約束的 log-residual(式 5),變數僅有 chunk 級的數十個 Sim(3),通常 3 次 iteration 收斂、C++ 實作每次 < 1.3 ms(Fig. 7)。整體論證是:當 foundation model 夠強時,公里級全域一致重建並不需要傳統 SLAM 後端,僅以 chunk-and-align + 輕量 loop 修正即可達成,且不需相機內參或深度監督。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input: I = {I_1, ..., I_N}                                                 [N, 3, H_in, W_in]   (W_in=518, H_in 依長寬比)
   │
   ├─ (a) Sequence Chunking ──────────────────────────────────────────────────────────────
   │      切成 K 個有重疊 chunks，第 k chunk: frames [(k-1)(L-O), (k-1)(L-O)+L)
   │      C_k                                                              [L, 3, H_in, W_in]   (L=chunk size, O=overlap)
   │
   ├─ (b) VGGT per-chunk inference (frozen) ─────────────────────────────────────────────
   │      ┌── ViT Encoder ──┐
   │      │   patch tokens   │                                              [L, N_tok, d_tok]    (d_tok=?, 論文未給)
   │      └─ Alternating Attn┘
   │      ┌── Decoding Heads ──┐
   │      │  pointmap  P_k     │                                            [L, H, W, 3]
   │      │  confidence c_k    │                                            [L, H, W]
   │      │  camera pose T_k   │                                            [L, 4, 4]            (chunk-local frame)
   │      └────────────────────┘
   │
   ├─ (c) Chunk-wise Sim(3) Aligning  (相鄰 C_k, C_{k+1} 重疊區) ───────────────────────
   │      建立對應 {(p_k^i, p_{k+1}^i)} 並取 (c_k^i, c_{k+1}^i)              [M_k, 3] × 2, [M_k] × 2
   │      IRLS (Huber + weighted Umeyama)
   │      → S_{k,k+1} ∈ Sim(3)                                              [4, 4]  (R, t, s)
   │
   ├─ (d) Loop Detection & NMS ────────────────────────────────────────────────────────
   │      VPR (DINOv2 backbone) per frame I_i → d_i                         [N, D_vpr]           (D_vpr=?)
   │      cosine sim 矩陣篩選 + |i-j|>Δt_min + NMS
   │      → loop pairs L = {(i, j)}                                         [N_L, 2]
   │
   ├─ (e) Loop-wise Sim(3) Aligning ─────────────────────────────────────────────────────
   │      對每對 (i, j) 組成 loop-centric chunk (拼接 i 與 j 鄰域子序列)
   │      C_loop                                                            [L_loop, 3, H_in, W_in]
   │      VGGT(C_loop) → P_loop, c_loop                                     [L_loop, H, W, 3], [L_loop, H, W]
   │      與 C_i, C_j 各自做 chunk-wise Sim(3) align (同 (c))
   │      → S_{i,loop}, S_{j,loop}                                          各 [4, 4]
   │      組合 S_ij = S_{i,loop} ∘ S_{j,loop}^{-1}  (式 4)                  [4, 4]
   │
   └─ (f) Global Sim(3) LM Optimization ─────────────────────────────────────────────────
          變數: {S_k}_{k=1..K}                                              [K, 4, 4]
          殘差: log_{Sim(3)}(S_{k,k+1}^{-1} S_k^{-1} S_{k+1})              每項 [7]
                log_{Sim(3)}(S_{ij}^{-1} S_i^{-1} S_j)                     每項 [7]
          LM 在 sim(3) 切空間最小化 (式 5)
          → 全域對齊後之 chunk poses {S_k^*}                                 [K, 4, 4]
          → 拼接後輸出 colored point cloud + camera trajectory
```

說明:`d_tok`、`N_tok`、`D_vpr` 在本論文未明示,皆以 `?` 標記;`H, W` 是 VGGT 輸出之特徵解析度,paper 未給確切數字,僅交代輸入寬度被下採樣到 518 pixels 並保持長寬比(p. 6)。

### 5.3 Per-Module Breakdown

#### 5.3.1 Sequence Chunking

**Function:** 將任意長度 RGB 序列以 sliding window 切成有重疊的固定大小 chunks,使每個 chunk 都落在 VGGT 的 GPU 記憶體上限內。

**Input:**
- Name: `I = {I_1, ..., I_N}`
- Shape: `[N, 3, H_in, W_in]`,其中 $W_{in}=518$,$H_{in}$ 由長寬比決定
- Source: 原始 RGB 影片串流(KITTI / Waymo / Virtual KITTI)

**Output:**
- Name: `{C_k}_{k=1..K}`
- Shape: 每個 `C_k` 為 `[L, 3, H_in, W_in]`
- Consumer: §5.3.2 VGGT per-chunk inference

**Processing:**

依參數 chunk size $L$、overlap $O$,第 $k$ 個 chunk 為 frames index 從 $(k-1)(L-O)$ 到 $(k-1)(L-O)+L$ 的子序列(§3.1)。實驗預設 overlap 設為 $L/2$(Tab. 1 caption)。$L$ 取 30/60/90/120 並比較,$L=90$ 在 KITTI 上 ATE 最佳(Tab. 1)。輸入端依 VGGT 設定下採樣寬度至 518 並保持長寬比(p. 6)。

**Key Formulas:**

Chunk index 範圍:

$$
\mathrm{idx}(C_k) = \big[(k-1)(L-O),\; (k-1)(L-O)+L\big)
$$

**Implementation Details:**

$L\le 60$ 在 24 GiB RTX 4090 可行,$L\ge 90$ 切換至 48 GiB L20;chunk 數量在 KITTI 各序列為「數十個」(p. 6);每 chunk 載入磁碟約 25 ms、寫回 95 ms,但相對 chunk 處理時間可忽略(§4.5)。本模組無學習參數。

#### 5.3.2 VGGT Per-Chunk Inference

**Function:** 對每個 chunk 獨立執行凍結的 VGGT,產出 chunk-local 的 pointmap、confidence 與相機參數。

**Input:**
- Name: `C_k`
- Shape: `[L, 3, H_in, W_in]`
- Source: §5.3.1 chunking

**Output:**
- Name: `(P_k, c_k, T_k)`
- Shape: `P_k ∈ [L, H, W, 3]`、`c_k ∈ [L, H, W]`、相機外參 `T_k ∈ [L, 4, 4]`(chunk-local 座標系)
- Consumer: §5.3.3 chunk-wise Sim(3) align、§5.3.5 loop-wise align、最終輸出

**Processing:**

VGGT 以 ViT encoder + alternating attention + 多個 decoding heads 從 raw uncalibrated RGB 直接回歸 dense pointmap、per-pixel confidence 與相機參數(§3.1, Fig. 2)。VGGT-Long 不重新訓練、不微調,僅作 forward;chunk 內部 60–80 張影像下,VGGT 已能輸出穩定且精度高的 local 重建(§1)。

**Key Formulas:**

無顯式公式;以 Fig. 2 中的 `VGGT(C_k) → (P_k, c_k, T_k)` 表示。

**Implementation Details:**

VGGT weights 來自 Wang et al. 2025,凍結;輸入寬度 518,長寬比保持(§4.2)。每 chunk 處理約 2.6–2.8 s(Tab. 5,$L=75$)。記憶體上限是本系統需要 chunking 的根本原因(§1)。在 24 GiB GPU 上 $L\le 60$ 可行;chunk 處理完即把結果寫盤,以避免 CPU 記憶體爆量(§4.3)。

#### 5.3.3 Chunk-wise Sim(3) Aligning (Confidence-aware IRLS)

**Function:** 在相鄰 chunk 重疊區估計 $S_{k,k+1}\in\mathrm{Sim}(3)$,使得 $C_{k+1}$ 對齊到 $C_k$,並用 confidence 與 Huber 共同抑制動態與低品質點。

**Input:**
- Name: 對應點集 `{(p_k^i, p_{k+1}^i), (c_k^i, c_{k+1}^i)}`
- Shape: 兩組 `[M_k, 3]` 與兩組 `[M_k]`,$M_k$ 為重疊區有效點數
- Source: §5.3.2 VGGT 輸出 + 重疊 frame 索引

**Output:**
- Name: `S_{k,k+1}`
- Shape: `[4, 4]`,等價於 $(s, R, t)$
- Consumer: §5.3.6 global LM(作為 sequential 約束)

**Processing:**

對重疊區建立 3D-3D 對應後,先丟棄 confidence 低於整 chunk median 的 0.1 倍者(§3.1, p. 4);剩餘點以 IRLS 解 weighted Umeyama:每次 iteration 用上一輪殘差 $r_i^{(t)}=\|p_k^i - S^{(t)} p_{k+1}^i\|_2$ 算 Huber 影響權,再乘上 model confidence $c_i$ 形成本輪權重 $w_i^{(t)}$,每輪以閉式 weighted Umeyama 解 $S^{(t+1)}$(式 1–3)。

**Key Formulas:**

$$
S^*_{k,k+1} = \arg\min_{S\in\mathrm{Sim}(3)} \sum_i \rho\big(\|p_k^i - S p_{k+1}^i\|_2\big)
$$

$$
S^{(t+1)} = \arg\min_{S\in\mathrm{Sim}(3)} \sum_i w_i^{(t)} \|p_k^i - S p_{k+1}^i\|_2^2,\qquad w_i^{(t)} = c_i \cdot \frac{\rho'(r_i^{(t)})}{r_i^{(t)}}
$$

**Implementation Details:**

ablation 顯示移除 confidence-weighting(把 confidence map 正規化為均勻值)與移除 IRLS 都會明顯掉分;Seq. 00 上,關掉 LC 使 ATE 升到 58.69 m,關掉 IRLS 使整體掉約 13%(Tab. 6)。每對相鄰 chunk 對齊耗時約 0.2–0.3 s(Tab. 5)。Huber loss 之 threshold、IRLS 終止條件論文未明示。

#### 5.3.4 Loop Detection (VPR + NMS)

**Function:** 跨整段序列偵測同一地點的非相鄰 chunk pair,輸出高 confidence 的 image-level loop pairs。

**Input:**
- Name: `{I_i}_{i=1..N}`
- Shape: `[N, 3, H_in, W_in]`
- Source: 原始輸入序列

**Output:**
- Name: loop pairs `L`
- Shape: `[N_L, 2]`(每列為 `(i, j)`)
- Consumer: §5.3.5 loop-wise alignment

**Processing:**

用預訓練 VPR 模型(DINOv2 backbone, Izquierdo & Civera 2024)抽 per-image 全域描述子 $d_i$。以 cosine similarity 做 nearest-neighbour 搜尋,若 $\mathrm{sim}(d_i,d_j)>\tau_s$ 且 $|i-j|>\Delta t_{\min}$ 視為候選 loop。再以 NMS 在時間鄰域取最強匹配,避免時序鄰近的重複(§3.2)。

**Key Formulas:**

$$
(I_i, I_j)\in L \iff \cos(d_i, d_j) > \tau_s \;\wedge\; |i-j| > \Delta t_{\min}
$$

**Implementation Details:**

VPR 與 VGGT 不能同時佔顯存:pipeline 先跑完整段 VPR,再釋放 VPR 權重才載入 VGGT(§4.2)。VPR per-frame 約 17–21 ms(Tab. 5)。$\tau_s$、$\Delta t_{\min}$、NMS 視窗大小、描述子維度 $D_{vpr}$ 論文皆未給出具體數值。

#### 5.3.5 Loop-wise Sim(3) Aligning (Loop-centric Chunk)

**Function:** 對每組候選 loop pair,組「跨時段」的 loop-centric chunk 重跑 VGGT,以更寬基線得到高品質 loop 對齊變換 $S_{ij}$。

**Input:**
- Name: loop pair `(I_i, I_j)` + 各自鄰域子序列
- Shape: 拼接後 `C_loop ∈ [L_loop, 3, H_in, W_in]`
- Source: §5.3.4 loop pairs + §5.3.1 原始序列

**Output:**
- Name: `S_ij`
- Shape: `[4, 4]`
- Consumer: §5.3.6 global LM(作為 loop closure 約束)

**Processing:**

把以 $i$、$j$ 為中心的兩段子序列拼成新的 `C_loop`,送進 VGGT 得到 loop-centric pointmap;再用 §5.3.3 的 chunk-wise IRLS 把 loop-centric chunk 對齊到 $C_i$ 與 $C_j$,得到 $S_{i,\mathrm{loop}}$ 與 $S_{j,\mathrm{loop}}$,以鏈式組合得到 $S_{ij}$(式 4, Fig. 5)。

**Key Formulas:**

$$
S_{ij} = S_{i,\mathrm{loop}} \circ S_{j,\mathrm{loop}}^{-1}
$$

**Implementation Details:**

該設計的關鍵在於「不同時段的同一地點在新 chunk 內共存」,讓 VGGT 看到更寬基線、更穩定地聯解兩端幾何;但 chunk 內子序列窗大小 $L_{\mathrm{loop}}$、各端取多少 frame 來拼接,paper 未明示。在 KITTI Seq. 08 上,雖有 3D 重疊但行駛方向相反導致 2D RGB 視覺 loop 偵測失敗,該段也就無法得到 $S_{ij}$ 修正(Fig. 8 caption)。

#### 5.3.6 Global Sim(3) LM Optimization

**Function:** 將所有 chunk 的 Sim(3) 變數同時最小化序列約束與 loop 約束,得到全域一致的 chunk pose 集合 $\{S_k^*\}$。

**Input:**
- Name: 變數 `{S_k}_{k=1..K}`、約束 `{S_{k,k+1}}` 與 `{S_{ij}}_{(i,j)\in L}`
- Shape: 變數 `[K, 4, 4]`;序列約束 `[K-1, 4, 4]`;loop 約束 `[N_L, 4, 4]`
- Source: §5.3.3 sequential、§5.3.5 loop

**Output:**
- Name: `{S_k^*}`
- Shape: `[K, 4, 4]`
- Consumer: 最終把每個 chunk 的 pointmap 變換到全域座標,輸出 colored point cloud 與 camera trajectory

**Processing:**

直接以 LM 解非線性最小平方,不建 factor graph;殘差以 $\log_{\mathrm{Sim}(3)}$ 投影到 7 維 $\mathfrak{sim}(3)$ 切空間,使得最佳化變成無約束問題(§3.3)。

**Key Formulas:**

$$
\{S_k^*\} = \arg\min_{\{S_k\}} \sum_{k=1}^{K-1} \big\|\log_{\mathrm{Sim}(3)}(S_{k,k+1}^{-1} S_k^{-1} S_{k+1})\big\|_2^2 + \sum_{(i,j)\in L} \big\|\log_{\mathrm{Sim}(3)}(S_{ij}^{-1} S_i^{-1} S_j)\big\|_2^2
$$

**Implementation Details:**

KITTI 上變數通常數十個,LM 平均 3 次 iteration 收斂(Fig. 7);每次 iteration C++ 實作 0.4–1.3 ms,Python 3.5–13 ms(Tab. 5、§4.5)。Ablation 顯示拿掉 loop closure 後 Seq. 00 ATE 從 8.67 m 暴增至 58.69 m,證明 LM + loop 約束對長序列 drift 抑制至關重要(Tab. 6)。LM damping 初值、收斂閾值、$\log_{\mathrm{Sim}(3)}$ 的具體實作(BCH 截斷階數等)paper 未明示。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
| --- | --- | --- | --- |
| KITTI Odometry [11] | 單目相機追蹤 (ATE) 與長序列 3D 重建 | 11 個序列 (Seq. 00–10),共 25,311 frames,單序列最長約 5067 m / 4661 frames | 僅作為 test;VGGT-Long 不需重訓練 |
| Waymo Open Dataset v1.4.1 [30] | 都市駕駛場景下相機追蹤與點雲重建 | 9 個 segments,每段約 196–199 frames,長度 42–351 m | 僅作為 test |
| Virtual KITTI v1.3.1 [9] | 合成域 (fog/rain/sunset 等) 的魯棒性評估 | 5 個 scenes (01/02/06/18/20),frame 數 223–837,長度 51–711 m,每個 scene 6 種天氣/光照條件 | 僅作為 test |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
| --- | --- | --- |
| ATE RMSE [m] | 估測軌跡與 GT 軌跡對齊後的絕對位置誤差均方根,評估長期軌跡一致性 (見 §4.1) | yes |
| Accuracy [m] | 預測點雲中每個點到最近 GT 點的歐氏距離 | no |
| Completeness [m] | GT 點雲中每個點到最近預測點的歐氏距離 | no |
| Chamfer Distance [m] | Accuracy 與 Completeness 的平均,綜合衡量重建品質 | yes (重建主指標) |
| Runtime (ms / s per chunk / iter) | 各模組的 wall-clock 時間 (Table 5),用於佐證可即時運行的論點 | no |

重建指標前先做粗對齊,再以 point-to-point ICP [25] 精化後計算;Transformer-based 方法保留 confidence > $0.75 \times$ 平均 confidence 的點,DROID-SLAM 等則保留 inverse depth > $0.75 \times$ 平均 inverse depth 的點 (§4.2)。

### 6.3 Training and Inference Settings

VGGT-Long 是 training-free pipeline:不重訓練 VGGT、不需相機內參、不需 depth supervision (§1, §5)。所有實驗皆為推論。

- **Hardware**: Ubuntu 22.04,12 顆 Intel Xeon Gold 6128 3.40 GHz CPU,67 GiB RAM。chunk size $\le 60$ 使用 NVIDIA RTX 4090 (24 GiB VRAM);chunk size $\ge 90$ 使用 NVIDIA L20 (48 GiB VRAM) (§4)。
- **Chunk 設定**: chunk size $L \in \{30, 60, 90, 120\}$,overlap $O$ 設為 $L/2$ (Table 1 註解)。
- **VGGT 推論**: 輸入影像下採樣至寬 518 px,高度依 aspect ratio 維持 (§4.2)。
- **Confidence 過濾門檻**: 對齊階段直接丟棄 confidence $< 0.1 \times$ chunk 內中位數 confidence 的點 (§3.1);重建指標計算階段則保留 $> 0.75 \times$ 平均 confidence (§4.2)。
- **VPR (Visual Place Recognition)**: 使用以 DINOv2 [24] 為 backbone 的預訓練模型 [13];推論先跑完整段 VPR、釋放其顯存後再載入 VGGT (§4.2)。
- **Loop 檢測**: 以 cosine similarity 門檻 $\tau_s$ 與最小幀距 $\Delta t_{\min}$ 篩選候選對,再以 NMS 抑制鄰近重複匹配 (§3.2);具體 $\tau_s$ 與 $\Delta t_{\min}$ 數值,the paper does not specify。
- **Global LM 最佳化**: Sim(3) Levenberg-Marquardt,在 sim(3) tangent space 上做無約束優化,平均 3 個 iterations 收斂,每步 $0.4$–$1.3$ ms (C++) 或 $3.5$–$13$ ms (Python) (§3.3, Fig. 7, Table 5)。
- **Disk I/O**: 每個 chunk 讀取約 25 ms、寫入約 95 ms,因 chunk 數量少,對總時間影響可忽略 (§4.5)。
- **CPU memory 策略**: chunk 結果落盤,對齊時僅載入相關 chunk pair 後立即釋放;最終點雲與相機 pose 採 stream writing 寫出 (§4.3)。
- 其他超參數 (例如 IRLS 迭代上限、Huber loss $\delta$、$\tau_s$ 與 $\Delta t_{\min}$ 具體值),the paper does not specify。

### 6.4 Main Results

**KITTI Odometry — ATE RMSE [m] $\downarrow$ (Avg. over 11 seqs / Avg.\* 排除 Seq. 01)** (Table 1)

| Method | Calib. | Avg. | Avg.* | Notes |
| --- | --- | --- | --- | --- |
| ORB-SLAM2 (w/ LC) [21] | Required | 54.816 | **9.464** | 經典 SLAM,需內參 |
| LDSO [10] | Required | **22.425** | 23.500 | direct SLAM |
| DROID-SLAM [33] | Required | 100.278 | 75.846 | learning-based,長序列誤差大 |
| DPV-SLAM++ [18] | Required | 25.749 | 27.138 | |
| MASt3R-SLAM [23] | No Need | / | / | 全 11 seqs Tracking Lost |
| CUT3R [41] / Fast3R [43] / VGGT [40] | No Need | / | / | 多數 OOM 或 drift 過大 |
| **VGGT-Long (L=30)** | **No Need** | **44.713** | **39.564** | **本論文 (chunk 30)** |
| **VGGT-Long (L=60)** | **No Need** | **26.358** | **19.298** | **chunk 60 為次佳整體表現** |
| **VGGT-Long (L=90)** | **No Need** | **22.718** | **20.938** | **chunk 90 取得 Avg. 第三** |
| **VGGT-Long (L=120)** | **No Need** | **25.597** | **22.814** | **chunk 越大未必更好** |

**Waymo Open Dataset — ATE RMSE [m] $\downarrow$ / Chamfer [m] $\downarrow$** (Tables 2, 3,平均跨 9 segments)

| Method | Calib. | ATE Avg. | Chamfer Avg. | Notes |
| --- | --- | --- | --- | --- |
| DROID-SLAM [33] | Required | 4.396 | 4.870 | Segment 520018670 Tracking Lost |
| MASt3R-SLAM [23] | No Need | 5.560 | 3.474 | |
| CUT3R [41] | No Need | 9.872 | 5.343 | |
| Fast3R [43] / VGGT [40] | No Need | OOM | OOM | 全 segments OOM |
| **VGGT-Long (Ours)** | **No Need** | **1.996** | **2.021** | **ATE 與 Chamfer 皆為最佳** |

**Virtual KITTI — ATE RMSE [m] $\downarrow$,跨 5 scenes × 6 conditions 平均** (Table 4)

| Method | All Avg. | 備註 |
| --- | --- | --- |
| DROID-SLAM [33] | **1.5200** | 需內參,Scene 06 Rain 條件下 Tracking Lost |
| MASt3R-SLAM [23] | / | 全部 Tracking Lost |
| CUT3R [41] | 38.0189 | drift 嚴重 |
| Fast3R / VGGT | OOM | — |
| **VGGT-Long (Ours)** | **2.0538** | **無需內參下唯一可完整跑完所有 scene+condition 的 calibration-free 方法** |

**Runtime (Table 5, chunk size = 75)**: 在 KITTI Seq. 00 (4542 frames) 上,VPR 約 21.3 ms/frame、chunk 處理約 2.81 s/chunk、chunk 對齊約 0.28 s/iter、LM 最佳化在 C++ 為 1.25 ms/iter (Python 13.4 ms/iter),整體可在近即時範圍內完成 km-scale 序列。

主要訊息: VGGT-Long 是 KITTI/Waymo/Virtual KITTI 三個資料集上,在 **完全無需相機內參** 的條件下,唯一能跑完所有 km-scale 長序列的方法,且 ATE 與 Chamfer 皆與需內參的傳統/深度 SLAM 方法相當或更佳;對比的 VGGT/Fast3R/CUT3R/MASt3R-SLAM 普遍因 OOM 或 Tracking Lost 而失敗。

### 6.5 Ablation Studies

Table 6 在 KITTI Seq. 00 與 Seq. 05 上對三個元件做消融 (ATE RMSE [m] $\downarrow$):

| LC | IRLS | Weight | Seq. 00 | Seq. 05 |
| --- | --- | --- | --- | --- |
| ✗ | ✓ | ✓ | 58.69 | 36.01 |
| ✓ | ✗ | ✓ | 12.29 | 10.98 |
| ✓ | ✓ | ✗ | 11.28 | 10.13 |
| ✓ | ✓ | ✓ | **8.67** | **8.31** |

- **移除 Loop Closure (LC)**: Seq. 00 ATE 從 8.67 m 暴增到 58.69 m (約 6.8×),Seq. 05 從 8.31 m 升到 36.01 m。直接驗證 §3.2 / §3.3 提出的 loop detection + Sim(3) LM 全域優化在 km-scale 累積 drift 上的核心貢獻,屬於診斷性消融。
- **移除 IRLS (退化為 single-pass confidence-weighted alignment)**: Seq. 00 升至 12.29 m (相對最佳劣化約 42%,論文聲稱 "13% drop" 似乎指 Seq. 05 上的相對變化或別種計算)。診斷 §3.1 中 IRLS + Huber loss 對動態物體 outlier 的抑制效果。
- **移除 Confidence Weight (將 confidence map 正規化為均勻值)**: Seq. 00 升至 11.28 m、Seq. 05 升至 10.13 m。診斷 §3.1 中以 VGGT 自帶 confidence 作對齊權重的價值。

**評估**: 三個消融都是 **診斷性** 而非單純 sanity check,各自對應 method section 中的一個獨立技術元件 (loop closure / IRLS / confidence weighting),且結果與作者敘事一致 (LC 是最大貢獻來源)。但仍有缺口:
- 只在 KITTI Seq. 00 / Seq. 05 兩條序列做,未涵蓋 Waymo 與 Virtual KITTI;在 Waymo (短段、大量無 loop 的場景) 上 LC 是否仍主導效果並未被驗證。
- 未消融 chunk size $L$ 與 overlap ratio $O/L$ 之外的關鍵設計 (例如 Sec. 3.2 的 loop-centric chunk 構造、confidence 過濾門檻 0.1× 中位數、VPR 模型選擇),這些設計選擇缺乏量化支持。
- 缺少對 LM 全域優化 vs. 純成對 Sim(3) 鏈乘的對比 (即 LC 的 *形式* 是否必要,而不只是 LC 的存在)。

### 6.6 Phyra Experiment Assessment

- [covered] Has at least one strong baseline — 對比包含當前 calibration-free SoTA MASt3R-SLAM [23] 與 VGGT [40] 本身,以及需內參的 DROID-SLAM、DPV-SLAM++ 等強 baseline (Tables 1–4)。
- [covered] Has cross-task / cross-dataset evaluation — 跨 KITTI、Waymo、Virtual KITTI 三個資料集,涵蓋真實駕駛、都市駕駛、合成域 (fog/rain/sunset),且同時報告軌跡 (ATE) 與重建 (Accuracy/Completeness/Chamfer) 兩種任務 (Tables 1–4)。
- [partial] Has ablations that diagnose the new components — Table 6 對 LC、IRLS、confidence weighting 三個元件做了診斷性消融,但僅限 KITTI 兩條序列,且未涵蓋 loop-centric chunk 構造、chunk size、LM 形式等其他關鍵設計。
- [covered] Has a scaling study — Table 1 報告 chunk size $L \in \{30, 60, 90, 120\}$ 對 ATE 的影響 (chunk 越大記憶體需求越高,且需要 L20 48 GiB GPU,§4),屬於計算/規模 trade-off 研究。
- [covered] Has an efficiency / wall-clock comparison — Table 5 給出每個元件的 wall-clock (VPR ms/frame、chunk 處理 s/chunk、LM ms/iter,並區分 C++ vs. Python),Fig. 7 顯示 LM 在 3 iters 內收斂;但缺少與 baseline (例如 MASt3R-SLAM) 的端到端 throughput 對比。
- [missing] Reports variance / standard deviation / multiple seeds — 所有 ATE 與 Chamfer 數值皆為單次推論結果,無多 seed、無 confidence interval、無方差;由於 VGGT-Long 為 deterministic pipeline 這部分風險較低,但 IRLS 初始化等仍可能存在隨機性。
- [covered] Releases code / weights / data sufficient for reproducibility — 摘要明確提供 GitHub repo (https://github.com/DengKaiCQ/VGGT-Long);VGGT 權重與三個資料集皆為公開來源,可重現性條件齊備 (但具體 $\tau_s$、$\Delta t_{\min}$ 等超參數需從 repo 確認)。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **C1: 首個將單目 3D 重建擴展到公里級、未校正戶外場景的系統。** *Supported.* Table 1 顯示 VGGT-Long 是唯一在 KITTI Odometry 全部 11 條序列都成功收尾的 calibration-free 方法,Fast3R / VGGT / CUT3R 大多 OOM,MASt3R-SLAM 全部 Tracking Lost。
- **C2: chunk-and-align pipeline 解決 foundation model 在長序列上的記憶體瓶頸。** *Supported.* Sec. 4.3 的磁碟 offload 策略與 Table 5 的 chunk-wise 處理時間驗證了 24 GiB GPU 即可推進到 KITTI Seq. 00 (4542 frames)。
- **C3: 在不引入複雜 backend (factor graph / bundle adjustment) 的前提下處理 Sim(3) 累積 drift。** *Partially supported / 措辭過鬆.* 系統實際上仍有一個全域非線性最小平方最佳化 (Eq. 5, Sec. 3.3),只是維度被壓到 chunk 級 (數十個 Sim(3) 變數)。所以是「以更小規模的 LM 取代 pose-graph / BA」,而不是真的「沒有 backend」;Fig. 6 與 Table 6 的 ablation 也顯示拿掉這個 LM-based 全域校正會讓 Seq. 00 ATE 從 $8.67\,\text{m}$ 漲到 $58.69\,\text{m}$,這就是 backend 的角色。
- **C4: accuracy comparable to traditional methods with calibrated cameras.** *Partially supported / 在 KITTI 上略過頭.* Waymo (Table 2) 與 Virtual KITTI (Table 4) 上的對比確實壓過 DROID-SLAM、MASt3R-SLAM、CUT3R;但 KITTI Avg.* 19.298 m 對比 ORB-SLAM2 w/ LC 的 9.464 m 仍是 $\sim 2\times$ 的差距,而 ORB-SLAM2 正是「traditional method with calibration」的代表。
- **C5: confidence-aware alignment 能抑制天空與動態物體。** *Supported.* Fig. 4 的視覺對照與 Table 6 中拿掉 weight 後 Seq. 00 ATE 從 $8.67\,\text{m}$ 升到 $11.28\,\text{m}$ 給出量化證據。

### 7.2 Fundamental Limitations of the Method

**Loop detection 完全綁在 2D 影像 VPR 上,結構性無法處理反向 loop 與外觀劇變。** Seq. 08 是作者自承的失敗案例:同一條路相反方向行駛時,DINOv2-based 全域描述子的餘弦相似度不會被觸發,Eq. 4 的 $S_{ij}$ 約束就拿不到。本系統設計上沒有任何 3D 幾何層級的 loop 候選機制 (例如 chunk pointmap 之間的 overlap 偵測或語義級對齊),因此在城市道路、高速公路雙向、或同一區域跨季節重訪等情境會結構性失效。

**Chunk 之間的對齊是純鏈式 Sim(3) 串接,單點失敗會沿時間傳播。** Sec. 3.1 的 IRLS 只在相鄰 chunk 重疊區運作,沒有 cross-chunk 的多視圖一致性檢查。一旦某對 chunks 因為 occlusion、夜間、強反光使得 VGGT 的 confidence 整體偏低,該對齊就會吞下系統性偏差,並透過 $S_k$ 的鏈式定義把誤差累積給之後所有 chunks,直到下一個 loop 才有機會被 Eq. 5 的全域 LM 拉回來。在無 loop 的長直道路 (Seq. 02、Seq. 10) 上這個結構性弱點直接體現在 Table 1 的高 ATE 數字。

**整套 pipeline 是 offline / batch 的,沒有任何 streaming 路徑。** chunk-wise SIM(3) 對齊、VPR 全序列查詢、loop-centric chunk 重推論、global LM 都假設整段影片已經結束。這對自駕車這個目標應用其實是個重大限制:車載感知無法等一整段公里級序列收尾再重建。論文宣稱「near real-time」只描述每個 chunk 的處理時間,並未對應 incremental 場景的端到端延遲。

**對 VGGT 本身的失敗模式沒有 fallback。** 整個方法把 VGGT 視為黑盒的 local engine;如果某個 chunk 內 VGGT 的 pointmap 或 camera pose 整體偏離 (例如重複紋理、長隧道、雪天),confidence map 也可能整體錯估,IRLS 拿不到正確的 weighting,後續所有對齊都建立在錯誤的 local prior 上。論文沒有 chunk 級的健康檢查 (例如 reprojection-based sanity check),這是「相信基礎模型就好」哲學的代價。

### 7.3 Citations Worth Tracking

- **[40] VGGT (Wang et al., 2025).** 整套系統的 local engine,理解其 confidence head 的訓練方式與 pointmap 輸出協定是判斷本論文上限的前提。
- **[23] MASt3R-SLAM (Murai et al., 2025).** 主要對手與設計哲學的反例;作者的「沒有 SLAM backend」論述只有對照 MASt3R-SLAM 的 pose graph + bundle adjustment 才能看出實際取捨。
- **[19] VGGT-SLAM (Maggio et al., 2025).** 同期工作,主張在 SL(4) manifold 上做 submap factor graph 對齊,直接挑戰本文的 Sim(3) 假設;值得追看是否能補上室外大規模實驗。
- **[13] Izquierdo & Civera 2024 VPR (DINOv2-based).** 本文 loop detection 的全部依賴,理解其失敗模式 (反向視角、季節變異) 等同於理解本論文的 loop closure 失敗模式。
- **[6] GigaSLAM (Deng et al., 2025).** 同一作者的前作,以 hierarchical Gaussian splats 解大規模單目 SLAM;對照可看出作者群從「自建大型 representation」轉向「靠基礎模型 + 輕縫合」的方法論演化。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] VPR loop detection 的 recall / precision 在 KITTI、Waymo、Virtual KITTI 各為多少?Table 6 的 LC 行只比 on/off,無法判斷誤差降低是來自 loop-centric chunk 的對齊精度,還是 loop 偵測本身。
- [ ] Loop-centric chunk (Fig. 5) 相較於直接以 VPR 命中的兩張影像做 PnP / Sim(3) 對齊,實際邊際貢獻有多大?論文沒有 ablate 「拿掉 loop-centric 重推論、改用直接配對」這個對照組。
- [ ] Chunk overlap size $O$ 對精度與速度的曲線?論文僅在 Table 1 caption 提到「overlap was set to half of the chunk size」,沒有掃描。
- [ ] 在無任何 loop 的純直線長序列 (例如人為截斷的 KITTI Seq. 01 子段) 上,系統的 drift 隨距離成長為 $\mathcal{O}(\cdot)$ 多大?這直接決定了「不靠 backend」哲學的適用上界。
- [ ] Fig. 1 預告的 iPhone 14 Pro 室內 465 m 序列在量化結果上是什麼樣子?VGGT 訓練分布偏戶外,室內手持是否會讓 confidence map 失真?
- [ ] 當某對相鄰 chunks 的重疊區大量被動態物體佔據 (擁擠十字路口) 時,IRLS 會丟掉太多點,殘存匹配是否仍足以唯一決定 7-DoF Sim(3)?論文未報告此 degenerate 情況的處理。
- [ ] 把 VGGT 換成更小的 DUSt3R / MASt3R 作為 chunk engine 時,chunk-and-align 框架還能維持公里級表現嗎?這能分離「框架價值」與「VGGT 強度」兩個變因。

### 8.2 Improvement Directions

1. **加上 3D-aware loop 候選機制 (高可行度,直接補 Seq. 08 的洞).** 在 VPR 之上,額外用 chunk 的 pointmap 做幾何 overlap 檢查 (例如以 chunk 級 BEV occupancy 比對),讓「同地點不同方向」的 loop 也能被觸發。理據:Seq. 08 的失敗根源在於描述子是 view-dependent,而 chunk pointmap 已經是 view-invariant 的 3D 結構。
2. **chunk 級健康檢查 + 局部回退 (中可行度).** 在每個 chunk 對齊後,以 reprojection error 或 confidence 分位數做 sanity check;若該 chunk 偏離 (例如 confidence median 跌破閾值),則自動縮短 chunk size 或重疊度重推論。理據:目前系統一旦 VGGT 在某 chunk 失敗,誤差就鏈式傳播到序列終點,這是無 backend 哲學最脆弱的點。
3. **streaming / incremental 變體 (中可行度,工程量大).** 把 VPR 的全序列查詢改為滑動窗的線上 KNN,LM 全域最佳化改為以最新 chunk 為核心的局部 marginalization,讓系統可以在車載即時跑。理據:目標應用是自駕車,但目前 pipeline 是 offline batch,實用上有落差。
4. **adaptive chunk sizing (中可行度).** 根據 ego-motion 速度或 scene complexity (例如 optical flow 統計或 VGGT confidence 分布) 動態調整 chunk size,而非全序列固定。理據:Table 1 顯示 chunk 60 → 90 → 120 在不同序列上的最佳值並不一致,表示存在 per-segment optimum。
5. **以 cross-chunk multi-view consistency 取代純鏈式 Sim(3) (低可行度,接近退回 SLAM).** 對 chunks 之間的多重 hop 做 minimal pose graph (但仍以 Sim(3) 而非 SE(3)) 最佳化,等於部分恢復 backend。理據:這會讓 C3 的「沒有 backend」宣稱變弱,但能直接修掉 §7.2 第二段提到的鏈式誤差問題。
