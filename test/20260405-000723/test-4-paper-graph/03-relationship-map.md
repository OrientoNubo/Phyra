<!-- type: relationship-map | generated: 2026-04-05 -->

## 關係矩陣

| 論文 A | 論文 B | 關係類型 | 方向 | 依據 |
|-------|-------|---------|------|------|
| DETR | Deformable DETR | builds-on | A->B | Deformable DETR 以 DETR 的收斂慢和小目標精度低為出發點，用可變形注意力替換全局注意力來解決這兩個問題 |
| DETR | DINO | builds-on | A->B | DINO 繼承 DETR 的集合預測框架和匈牙利匹配，在 query 初始化和去噪訓練上做改進 |
| DETR | RT-DETR | builds-on | A->B | RT-DETR 沿用 DETR 的端到端檢測範式，針對推理效率重新設計 encoder 架構 |
| DETR | Co-DETR | builds-on | A->B | Co-DETR 直接以 DETR 的一對一匹配訓練效率問題為研究動機 |
| Deformable DETR | DINO | builds-on | A->B | DINO 使用 Deformable DETR 的多尺度可變形注意力作為基礎架構，並在其上疊加去噪訓練和 query selection 改進 |
| Deformable DETR | RT-DETR | builds-on | A->B | RT-DETR 的 decoder 基於可變形交叉注意力，encoder 部分則重新設計以提升效率 |
| Deformable DETR | Co-DETR | builds-on | A->B | Co-DETR 以 Deformable DETR 為實驗基線之一，其協作訓練策略直接作用於 Deformable DETR 的 encoder-decoder 架構 |
| DINO | RT-DETR | builds-on | A->B | RT-DETR 的 query selection 機制受 DINO 的 mixed query selection 啟發，並進一步加入不確定性最小化準則 |
| DINO | Co-DETR | parallel | 時間方向不確定 | DINO (ICLR 2023) 與 Co-DETR (ICCV 2023) 同年發表，兩者獨立解決 DETR 的訓練效率問題：DINO 側重去噪訓練，Co-DETR 側重混合匹配 |
| RT-DETR | Co-DETR | parallel | 時間方向不確定 | 兩者解決不同維度的問題：RT-DETR 專注推理速度，Co-DETR 專注訓練效率和精度上限，方法互不依賴 |

## 邏輯發展脈絡

DETR (2020) 開創了端到端目標檢測的新範式，用 Transformer 和二分匹配取代了 NMS 和 anchor 等手工設計，但付出了兩個代價：訓練收斂極慢（500 epochs）且小目標精度不足。Deformable DETR (2021) 直接回應了這兩個限制，其核心洞察是全局注意力既是 DETR 的理論優勢也是其實踐瓶頸。透過可變形注意力，Deformable DETR 將收斂速度提升 10 倍並啟用了多尺度特徵融合，小目標精度隨之改善。

然而 Deformable DETR 仍遺留了一個根本性問題：一對一匹配導致的稀疏監督。這個問題催生了兩個獨立的研究方向。DINO (ICLR 2023) 從 query 初始化和訓練信號的角度出發，整合了 DAB-DETR 的動態 anchor boxes 和 DN-DETR 的去噪訓練，並進一步提出對比去噪來抑制假陽性，將 DETR 系列的精度推至與傳統檢測器全面可比的水準。Co-DETR (ICCV 2023) 則從另一個角度切入同一問題：與其改善去噪或 query 初始化，不如直接在訓練時引入一對多匹配的輔助頭來增加 encoder 的監督密度，推理時再移除這些輔助頭以保持端到端。兩條路徑在同一年獨立收斂到了相近的性能水準。

在精度問題逐步被解決後，DETR 系列面臨的下一個挑戰是部署效率。RT-DETR (CVPR 2024) 綜合吸收了前序工作的成果（Deformable DETR 的多尺度處理、DINO 的 query selection 思路），並重新設計了 encoder 架構以實現實時推理。RT-DETR 的意義在於它首次證明端到端檢測器可以在速度-精度 Pareto 前沿上超越 YOLO 系列，從而回應了自 DETR 提出以來「端到端範式是否具有實用價值」這一持續存在的質疑。

總體而言，這五篇論文的發展軌跡呈現清晰的樹狀結構：DETR 為根節點，Deformable DETR 為主幹延伸，DINO 和 Co-DETR 在精度維度上形成兩個平行分支，RT-DETR 則在效率維度上開闢新的方向。
