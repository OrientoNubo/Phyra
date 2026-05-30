<!-- type: paper-read-notes | generated: 2026-05-09 | lang: zh-TW -->

# Genie — Genie: Generative Interactive Environments

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | Genie |
| Paper full title | Genie: Generative Interactive Environments |
| arXiv ID | 2402.15391 |
| Release date | 2024-02-23 |
| Conference/Journal | arXiv preprint (later ICML 2024 Best Paper) |
| Paper link (abs) | https://arxiv.org/abs/2402.15391 |
| PDF link | https://arxiv.org/pdf/2402.15391v1 |
| Code link | — |
| Project page | https://sites.google.com/view/genie-2024/ |

### 1.1 Author Information

| Author Name | Affiliation | Homepage | Role |
|---|---|---|---|
| Jake Bruce | Google DeepMind | https://jakebruce.ca/ | first author (equal contribution) |
| Michael Dennis | Google DeepMind | — | equal contribution |
| Ashley Edwards | Google DeepMind | https://ashedwards.github.io/ | equal contribution, corresponding author |
| Jack Parker-Holder | Google DeepMind | https://jparkerholder.github.io/ | equal contribution, corresponding author |
| Yuge (Jimmy) Shi | Google DeepMind | — | equal contribution |
| Edward Hughes | Google DeepMind | — | co-author |
| Matthew Lai | Google DeepMind | — | co-author |
| Aditi Mavalankar | Google DeepMind | — | co-author |
| Richie Steigerwald | Google DeepMind | — | co-author |
| Chris Apps | Google DeepMind | — | co-author |
| Yusuf Aytar | Google DeepMind | — | co-author |
| Sarah Bechtle | Google DeepMind | — | co-author |
| Feryal Behbahani | Google DeepMind | — | co-author |
| Stephanie Chan | Google DeepMind | — | co-author |
| Nicolas Heess | Google DeepMind | — | co-author |
| Lucy Gonzalez | Google DeepMind | — | co-author |
| Simon Osindero | Google DeepMind | — | co-author |
| Sherjil Ozair | Google DeepMind | — | co-author |
| Scott Reed | Google DeepMind | — | co-author |
| Jingwei Zhang | Google DeepMind | — | co-author |
| Konrad Zolna | Google DeepMind | — | co-author |
| Jeff Clune | Google DeepMind; University of British Columbia | — | co-author |
| Nando de Freitas | Google DeepMind | — | co-author |
| Satinder Singh | Google DeepMind | — | co-author |
| Tim Rocktäschel | Google DeepMind | — | equal contribution, senior author |

### 1.2 Keywords

Generative AI, Foundation Models, World Models, Video Models, Latent Action Model, Open-Endedness, Spatiotemporal Transformer, MaskGIT, VQ-VAE, Unsupervised Learning

### 1.3 Related Lineage

| Key | Relation | Brief |
|---|---|---|
| Phenaki (Villegas et al., 2023) | predecessor | Variable-length text-to-video with C-ViViT temporal-aware tokenizer;Genie 替換為更高效的 ST-ViViT。 |
| MaskGIT (Chang et al., 2022) | base model | Genie 動力學模型直接採用 MaskGIT 之雙向 masked token 解碼器來自迴歸生成下一影格 tokens。 |
| VQ-VAE (van den Oord et al., 2017) | base model | Genie 影片 tokenizer 與潛在動作 codebook 皆以 VQ-VAE 目標訓練,離散化潛在空間。 |
| ST-transformer (Xu et al., 2020) | influence | 提供時空交錯注意力骨幹,Genie 三大模組皆採用,使計算隨影格數線性成長。 |
| ViT (Dosovitskiy et al., 2021) | influence | Vision Transformer 為 Genie 各模組之 patch-based 表徵與注意力設計基礎。 |
| MAGVIT/W.A.L.T (Gupta et al., 2023) | influence | 近期高品質影片生成模型,啟發 Genie 採用離散化 token 與 transformer 架構放大 scale。 |
| RT-1 (Brohan et al., 2023) | baseline | 提供機器人示範影片資料集,Genie 用以驗證在無動作標籤情況下泛化至機器人視訊領域。 |

## 2. Research Overview

### 2.1 Research Topic

本研究提出 Genie——首個能僅以未標註網路影片進行無監督訓練的「生成式互動環境」基礎模型。其核心目標是在沒有任何動作標籤、文字標註或領域特定資料的情況下,從約三萬小時的 2D 平台遊戲影片中學會生成可由使用者逐影格操控的虛擬世界,並能以文字到圖像、手繪草圖或真實照片作為提示進入互動。Genie 由三個元件組成:時空(ST-transformer)影片 tokenizer、因果潛在動作模型(Latent Action Model, LAM)、以及以 MaskGIT 為基礎的動力學模型,模型總參數量達 11B。論文同時驗證該方法可遷移至機器人影片(RT-1 資料集),並展示所學潛在動作可用於從未見過的無動作影片中推論策略,為訓練未來通用 agent 提供新的資料來源。

### 2.2 Domain Tags

- Generative AI
- World Models
- Video Generation
- Reinforcement Learning
- Foundation Models

### 2.3 Core Architectures Used

- **ST-transformer (Spatiotemporal Transformer)**:Genie 三大模組共用的骨幹,以交錯的 spatial / temporal attention 取代全時空注意力,使主導計算量隨影格數 $T$ 線性成長,讓網路規模影片訓練可行。
- **VQ-VAE**:同時用於 video tokenizer(將每影格壓縮為離散 token $z_t$)與 latent action codebook(把連續潛在動作量化為 $|A|=8$ 的小型離散集合),提供 Genie 的離散表徵基礎。
- **Latent Action Model (LAM)**:本論文提出的核心元件,由 ST-transformer encoder/decoder 構成,在無監督下從相鄰影格 $(x_t, x_{t+1})$ 推出離散潛在動作 $\tilde{a}_t$;推論時 encoder 丟棄,僅保留 codebook 供使用者「按鍵」操控。
- **ST-ViViT video tokenizer**:本論文提出的時空感知 tokenizer,以 ST-transformer 替代 Phenaki 之 C-ViViT,在記憶體與 FVD 指標上皆優於 spatial-only ViT 與 C-ViViT(見論文 Table 3)。
- **MaskGIT dynamics model**:decoder-only 的 MaskGIT transformer,接收 $\boldsymbol{z}_{1:t-1}$ 與 stop-grad 後的 $\tilde{\boldsymbol{a}}_{1:t-1}$,以雙向 masked token 解碼預測下一影格 tokens;潛在動作以 additive embedding 而非 concatenation 方式注入,實驗顯示此選擇顯著改善可控性。
- **ViT (Vision Transformer)**:作為各模組 patch-based 表徵與注意力設計的共同基礎,Genie 在其上引入時空分離的注意力結構。

### 2.4 Core Argument

作者識別出當前生成式 AI 與世界模型的根本侷限:現有的影片生成模型雖然能在文字或圖像條件下產出視覺一致的內容,但缺乏「逐影格可控性」;傳統世界模型雖具備幀層級控制,卻必須仰賴大量帶有動作標籤的軌跡資料,使其難以擴展至網路規模,因為網路上海量的影片幾乎都不含動作或回饋標註。換言之,過去的方法被迫在「資料規模」與「互動性」之間二選一。Genie 主張要打破這個取捨,必須讓模型自行從像素層面學出一個有意義的離散動作空間。這引出三個邏輯上必要的設計:(1) 採用 ST-transformer 將時空注意力分離,使計算量隨影格數線性而非二次成長,讓網路規模影片訓練變得可行;(2) 引入 Latent Action Model,以 VQ-VAE 將連續潛在動作量化為極小的離散 codebook(|A|=8),強制模型把相鄰影格之間「最重要的變化」壓縮到可由人類當作搖桿按鍵使用的代碼,並在推論時丟棄編碼器只保留 codebook,以便由使用者直接指定動作;(3) 動力學模型採 MaskGIT 雙向解碼並把潛在動作以加性 embedding 而非串接方式注入,實驗顯示此設計顯著提升可控性。透過這三項設計,Genie 證明只用未標註影片即可獲得幀級可控的世界模型,且模型隨計算與參數規模呈現乾淨的 scaling 行為,因此被定位為「foundation world model」,並進一步暗示所學潛在動作可作為通用 agent 模仿學習的橋樑。

## 3. Section Walkthrough

### 3.1 Title and Abstract

(180 words)

論文以「Genie: Generative Interactive Environments」為題，標題本身就把核心 positioning 說清楚：這不是一個 video generation model，也不是傳統需要 action label 的 world model，而是「可互動的生成式環境」這個新範式。Abstract 緊扣三個賣點來鋪陳故事邏輯。第一，資料條件極弱：僅以 unlabelled Internet videos 訓練，無 action label、無 text annotation、無 domain-specific reward。這是後文凸顯方法價值的對照基礎。第二，能力強：在 11B 參數規模下被定位為 foundation world model，可由 text、synthetic image、photo、甚至 hand-drawn sketch 啟動，並在 frame-by-frame 層級可控。第三，方法骨架：spatiotemporal video tokenizer、autoregressive dynamics model、簡單可擴展的 latent action model 三個模組。Abstract 最後丟出延伸誘餌——所學到的 latent action space 可以反過來用於從 unseen videos 推論 policy，為訓練 generalist agents 提供新路徑。這段把「無監督從 video 學到可玩世界」與「latent action 是通往 agent 的橋樑」兩條主線同時架起，為後續 Introduction 的問題框定與 Methodology 的模組拆解預留鋪墊空間。

### 3.2 Introduction

(420 words)

Introduction 的故事邏輯是一條典型的「generative AI 已經做到 X，但還缺 Y，我們補上 Y」的拉力線。作者先回顧 transformer 帶動的生成式進展：從 language（GPT 系列）到 image（DALL·E、Imagen、Stable Diffusion），再到正在升溫的 video generation。接著馬上指出落差：video model 的 engagement 與 ChatGPT 級別的 interactivity 相比仍有 gulf，更別說 immersive experience。這一句承擔了立論支點：要的不是更好的 video，而是 interactive experience。

接下來作者用一個提問把研究目標推到台前——「能否從一大批 Internet video 裡，不只學到生成 image / video，而是學到整個 interactive experience？」隨即提出 generative interactive environments 這個新 paradigm，並把 Genie 落地為它的第一個實作：以 200,000 小時公開遊戲影片訓練、無 action 與 text label、卻能 frame-by-frame 控制的模型。為了把 Genie 與既有工作分得乾淨，作者交叉引用 Table 1，明確區別 World Models（需要 video + actions）、Video Models（video + text、僅 video-level 控制）與 Genie（僅 video、frame-level 可控），這個三方對照是後續 Related Work 的縮影。

模型骨架在這裡第一次給出結構性解釋：以 ST-transformer 為共用骨架，搭配 novel video tokenizer 與 causal latent action model，video token 與 latent action 一同送進採用 MaskGIT 的 dynamics model，autoregressive 地預測下一幀。作者特別強調做了 40M–2.7B 的 scaling sweep，並聲稱 architecture 隨 compute graceful 擴展，最終訓練出 11B 的主模型；訓練語料是 30k 小時、上百款 2D platformer 影片的 filtered subset。

最後 Introduction 為論文的「廣度敘事」鋪兩條伏筆。第一條是 generality：另訓一個 RT1 robot video 上的 action-free 版本，學到 consistent latent actions，暗示這個 recipe 不只限於 platformer。第二條是 agent：latent action 可被用來從 unseen action-free video 推 policy，把 Genie 與「unlock unlimited training data for generalist agents」這個更大願景連結起來。這兩條伏筆分別對應 §3.2 的 Robotics qualitative 與 §3.3 的 CoinRun BC 實驗，使後文的多元結果在 narrative 上不顯得鬆散。

### 3.3 Related Work / Preliminaries

(390 words)

Preliminaries 與 Related Work 在原文分屬 §2 開頭與 §4，但都負責「把 Genie 的選擇放回脈絡」這件事，故事邏輯一致。Preliminaries 先處理架構基底：所有模組共用基於 ViT 的 ST-transformer。作者明確點出動機——video token 數量可達 $O(10^4)$，full attention 的 quadratic memory 不可行；ST-transformer 把 attention 拆成 spatial（在 $1 \times H \times W$ tokens 內）與 temporal（在 $T \times 1 \times 1$ tokens 上、causal mask）兩層，再接一個 FFW；spatial layer 的成本對 frame 數呈 linear 而非 quadratic。這個 inductive bias 不只是工程小細節，它決定了之後 video tokenizer、LAM、dynamics 三者都可以在長序列上 scale，也成為後文 ablation（C-ViViT vs ST-ViViT）的判準。作者也提到一個非顯然設計：整個 ST block 只在 spatial+temporal 之後放一個 FFW，省掉 post-spatial FFW 把參數空間讓給其他模組，並聲稱這個調整顯著改善結果。

Related Work（§4）以四個對照軸把 Genie 的位置畫出來。第一軸 World Models：與 Ha & Schmidhuber、Dreamer 系、GAIA-1、UniSim 等對照——他們都需要 action（或加上 text）conditioning，Genie 則完全 unsupervised from video。第二軸 Video Models：包含 Phenaki、TECO、MaskViT 等 transformer-based 路線，作者承認方法上最像這群（同樣用 MaskGIT + ST-transformer + token），但目標更 agentic：顯式學一個 latent action space 讓使用者「玩」。第三軸 Playable Video Generation（PVG）：Menapace 等的 PVG 已有 latent action 概念，但侷限於 domain-specific static example，無法用 prompt 生成全新環境；Genie 的貢獻是把 inductive bias 換成 general method 並 scale 起來。第四軸 Environment generation 與 latent-action agent training：把 Genie 對齊到 PCG / LLM-写遊戲、以及 Edwards 2019、VPT、Schmidt & Jiang 2024 等以 latent action 做 imitation 或 pre-training 的線索；其中與 VPT 的對比最關鍵——VPT 仰賴人類標註的 action data 訓練 inverse dynamics，Genie 則完全從 Internet video 學 latent action 並可推到任意環境，避開 ground-truth action 的成本與 generalization 風險。這四軸鋪好後，§5 的方法細節與 §3 的實驗才能被讀者直接對應到「填補了哪一塊空白」。

### 3.4 Method (overview narrative)

(360 words)

Method 對應原文 §2，敘事骨幹是「三個模組 + 兩階段訓練 + 一個推論流程」。作者在 §2.1 把 Genie 拆成三件互相咬合的東西：(1) latent action model（LAM）負責從相鄰 frame 推 latent action $\tilde{a}_t$；(2) video tokenizer 把 raw frame 壓成 discrete token $z_t$；(3) dynamics model 在 past token 與 latent action 條件下預測下一 frame token。三者用 ST-transformer 為共同骨架，使整體計算複雜度對 frame 數線性放大，這是後續可擴到 11B 的前提。

訓練流程刻意被切成兩階段：先單獨訓 video tokenizer，因為 dynamics model 必須吃 token 才能訓；接著 co-train LAM（直接吃 pixel）與 dynamics model（吃 token）。這個切分背後的論述很重要——LAM 故意吃 pixel 而非 token，因為 ablation 顯示 token 化會把 motion 訊息壓掉、降低 controllability；但 LAM 的 codebook size 又被刻意限制（$|A|=8$），讓 latent action 維持人類可玩、且離散。LAM 的 encoder 看 $\boldsymbol{x}_{1:t+1}$、decoder 看 $\boldsymbol{x}_{1:t}$ 與 $\tilde{\boldsymbol{a}}_{1:t}$ 重建 $\hat{x}_{t+1}$，整個 LAM 除了 VQ codebook 外推論時都丟棄，使用者直接挑 $a \in [0, |A|)$ 取代。

video tokenizer 採 VQ-VAE 風格，但 encoder 與 decoder 都用 ST-transformer，使每個 $z_t$ 帶有 $\boldsymbol{x}_{1:t}$ 的時序資訊，作者把這個變體命名為 ST-ViViT，並對照 Phenaki 的 C-ViViT 凸顯成本對 frame 數線性。

dynamics model 是 decoder-only 的 MaskGIT transformer，吃 $\boldsymbol{z}_{1:t-1}$ 與 stopgrad 的 $\tilde{\boldsymbol{a}}_{1:t-1}$ 預測 $\hat{z}_t$，訓練時對 $\boldsymbol{z}_{2:T-1}$ 套 Bernoulli mask（mask rate 從 [0.5, 1] 均勻採樣），cross-entropy loss 對齊 ground-truth token。一個非顯然但被作者點名的設計：latent action 採 additive embedding 而非 concatenation，這對 controllability 有正向影響。

§2.2 的 inference 流程把三模組串起來：使用者給 prompt frame、tokenizer 編成 $z_1$、自己挑 $a_1$、查 codebook 得 $\tilde{a}_1$、dynamics 預 $z_2$、tokenizer decoder 還原成 frame，autoregressive 重複；可以用 ground-truth 推得的 action 重生原片，也可以換 action 生新軌跡。這段敘事為 §5 的模組級細節（codebook size、patch size、ST block 設計）與 §6 的 ablation 對照都鋪好錨點。

### 3.5 Experiments (overview narrative)

(380 words)

Experiments 對應原文 §3 與部分 §4，敘事邏輯是「先驗證 scale、再展示 generality、再證明 latent action 有 transfer 價值、最後用 ablation 收尾」，恰好對應 §3.1–§3.4 四個小節。

開頭先把 dataset 與 metric 設好。Platformers dataset 從 55M 段 16 秒、10FPS、160×90 影片濾到 6.8M（30k 小時），規模在主流 Internet video dataset 同個量級；Robotics 則合併 RT1、QT-Opt 等 ~130k demos + simulation + 209k real robot episode，全部當 video 用、不取 action。Metric 兩條：FVD 衡量 video fidelity、自定義 $\Delta_t\text{PSNR}$ 衡量 controllability，後者比較「用真 action 推得的 latent」與「random 採樣 latent」生出的 frame 與 ground-truth 的 PSNR 差距，差距越大代表 latent action 越能左右生成。

§3.1 Scaling 是論文的 quant 主軸：固定 tokenizer 與 LAM，把 dynamics model 從 41M 拉到 2.7B，training loss 隨 compute 與參數量 graceful 下降；再對 2.3B 做 batch size 128/256/448 sweep（1.9M/3.8M/6.6M tokens/batch），同樣穩定改善。最終 Genie 主模型是 10.1B dynamics + tokenizer + action model 共 10.7B，batch 512、125k step、256 TPUv5p、訓 942B token。

§3.2 Qualitative 把 generality 推到前台：以 Imagen2 生成圖、手繪 sketch、real photo 三類 OOD prompt 餵 11B Platformers 模型，仍出現 game-like 行為與一致的 latent action 語意；甚至 emergent 能力如 parallax（前景比中景與背景動更多）也出現了。Robotics 端用同樣 hyperparameter 訓的 2.5B 模型在 test split 達 FVD 82.7，並在無 action label 下學到 down/up/left 等具語意的 consistent latent actions，連 deformable object（洋芋片袋）的形變都能模擬。

§3.3 Training Agents 是 latent action 的 transfer 證據：在 procgen CoinRun（hard / easy 兩設定）上，把 frozen LAM 標 expert video 為 latent action、訓一個 $\pi(a_t|x_t)$，再用少量 ground-truth action 建 latent→real 的 mapping。結果即使 Genie 幾乎沒看過 CoinRun，只給 200 條 expert sample 就追平有 expert action 上限的 oracle BC，凸顯 latent action 是可遷移的。

§3.4 Ablation 收尾兩個關鍵設計選擇：LAM 用 pixel 比 token 在 controllability 上明顯較好；tokenizer 比較 ViT、C-ViViT、ST-ViViT 後，ST-ViViT 在 FVD 與 $\Delta_t\text{PSNR}$ 都贏，且記憶體只比 ViT 多一點、遠少於 C-ViViT。

### 3.6 Conclusion / Limitations / Future Work

(370 words)

Conclusion 對應原文 §5 加 Broader Impact，敘事邏輯是把 Genie 重新定位為「任何人都能 dream up 並走進去」的生成式 AI，再坦白工程上仍待補的洞，最後把 future direction 拉回兩個未完成承諾——更大的 video 來源與 generalist agent 訓練。

論文先把貢獻收束成一句：Genie 是僅以 video data 訓練、卻可被 prompt 出多樣 interactive、controllable environment 的新型 generative AI，並把使用者對象具體化到「even children」，呼應 Author Contributions 末段對 Seneca 與 Caspian Clune 兩位小朋友 sketch 的致謝。這個敘事把 Genie 從 model paper 推向 platform/paradigm 的姿態。

Limitations 列三項，每項都和方法核心對齊。第一，autoregressive transformer 的通病：會 hallucinate unrealistic future——這對 interactive 場景比 image 場景痛，因為每 frame 的錯誤會 compound。第二，spatiotemporal representation 雖然進步，仍只能 condition 在 16 frame memory 上，long-horizon consistency 不足，這直接限制 Genie 用作環境模擬器的時間尺度。第三，目前 Genie 只能跑在 ~1FPS，對 interaction 而言遠低於可用 frame rate。這三點同時界定了 future work 必須處理的三個方向：autoregressive 的可靠性、長上下文記憶、sampling 加速。

Future Work 把方向往兩個更大的願景投射。第一，把訓練語料從 platformer 與 robot 擴到「Internet video 的更大比例」，去模擬更 diverse、realistic、imagined 的環境——這條延伸自 §3.2 OOD prompt 與 Robotics 模型已展示的 generality。第二，把 latent action 用於訓練 generalist agent：作者重申 RL 領域長期的 bottleneck 是 environment diversity 不足，Genie 提供一條「以視覺資料量補環境量」的新路徑，§3.3 CoinRun 結果是這條路徑的早期實證。

Broader Impact 與 Reproducibility 補上 paper 的責任面與可驗證性：作者明確選擇 不釋出 model checkpoint、訓練資料與資料樣本，理由是要先與研究與遊戲社群對齊安全與合規；同時為了讓資源較少的研究者能複現，特別提供 Appendix F 的小規模、可在單台中階 TPU/GPU 跑通的 setup。這段聲明把限制與開放策略直接寫進論文敘事，使結論的「unlock 大規模未來」承諾不至於完全脫離實作可及性。

## 4. Critical Profile

### 4.1 Highlights

- 提出了首個僅以未標註網路影片即可訓練、且能逐影格控制的 generative interactive environment,在 Table 1 將其定位為與 World Models / Video Models 並列的第三類。
- 在 11B 總參數規模下展示 foundation 模型的 prompt 多樣性:可接受 text-to-image、hand-drawn sketch、real-world photo 作為起始幀並產生互動軌跡(Figure 1, Figure 10)。
- ST-transformer 將時空注意力分離,使主導計算項對影格數量呈線性而非二次增長(p. 3),是支撐網路規模影片訓練的關鍵架構決策。
- 從 40M 到 2.7B 參數呈現乾淨的 scaling 曲線,且 batch size 從 128 提升到 448 也帶來一致的 loss 下降(Figure 9),為 final 10.1B dynamics model 提供 scaling 依據。
- ST-ViViT tokenizer 在相近參數下顯著優於 C-ViViT(FVD 81.4 vs. 272.7)與 spatial-only ViT(FVD 114.5),並把記憶體從 1.6 GB 壓到 0.9 GB(Table 3)。
- LAM ablation 指出以 raw pixels 而非 tokenized images 餵入 encoder 可同時提升 Robotics 的 FVD(136.4 vs. 257.8)與 Δ_t PSNR controllability(2.07 vs. 1.65,Table 2),確認 tokenization 會丟失動作相關的細節。
- 把 latent action 以 additive embedding(而非 concatenation)注入 dynamics model 顯著提升可控性(p. 5),這是相對既有 transformer-based world model 的具體經驗修正。
- 不依賴動作標籤,僅以 6.8M / 30k hours 的策畫資料集就把 FVD 從 61.4 降到 54.8(Table 4),驗證資料品質遠勝於數量。
- Robotics 遷移實驗:同樣的超參數在 RT-1 + 模擬資料的混合集上達 FVD 82.7,且學到 down/up/left 等具語義的一致動作(Figure 13)。
- 在 CoinRun 上把 frozen LAM 接到一個 BC policy,僅用 200 個 expert label 就能匹配 oracle BC,顯示 latent actions 對未見環境具有可遷移的語義(Figure 15)。

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

- 模型如同其它 autoregressive transformer 會 hallucinate 不真實的未來(§5, p. 11)。
- 受限於 16 frames 的時間記憶,長期一致性難以維持(§5, p. 11)。
- 推論大約僅 ~1 FPS,離可玩的互動 frame rate 仍有差距,需要未來進一步的效率改進(§5, p. 11)。
- 為避免被誤用,作者選擇不釋出 checkpoints、訓練資料與資料樣本(§Broader Impact, p. 11)。
- 可重現性對小算力研究者具挑戰,故僅在 Appendix F 附上 CoinRun 的單機 TPU 例子(§Reproducibility, p. 11)。

#### 4.2.2 Phyra-inferred

- 「無需動作標籤」的承諾在實際 agent 訓練流程被打破:Appendix E.1(p. 25)為了把 latent action 對應回 real action,仍需一個小型「expert action-labeled」字典,並用「200 expert samples 即可」的說法包裝這個依賴。
- Δ_t PSNR 是論文自定義的指標且僅在 t=4 報告(§3, p. 6),對於作者本身強調的「long-horizon consistency」這個議題完全沒有對應的可控性測量。
- 全篇 FVD 只與自家 ablation(ViT/C-ViViT/token-input)比較,沒有與同期 Phenaki、MAGVIT、Stable Video Diffusion 等同類影片模型對齊測量,FVD 81.4 / 54.8 在絕對品質上的位置因此難以判斷。
- |A|=8 是寫死的設計,且 Appendix C.1(p. 22)提到「增加 codes 會降低 human/AI playability」,但完全未量化在更大動作詞彙下 controllability 與 fidelity 的 trade-off,使「latent action 可作為通用 agent 介面」的論點僅在極窄詞彙下成立。
- §3.2 對 latent action 一致性的證據來自 Figure 17 的四個 prompt 圖以及 Robotics 的三個 prompt,屬於 hand-picked qualitative 展示;沒有跨資料集的量化指標(例如同一 latent action 下視覺位移向量的方差)。
- §3.3 的 BC 實驗僅在 CoinRun(同樣是 2D platformer)上完成,對於「foundation world model」這個定位最關鍵的 cross-domain transfer(例如 3D 環境、第一人稱視角)沒有任何實驗,Robotics 模型也只測 FVD 而沒有 BC。
- 6.8M videos 的篩選靠一個 11M ResNet18 二元分類器(Appendix B.1, p. 21–22),作者自承訓練樣本量約 10k 且資料來自 publicly available Internet videos,但對於該分類器的偏差(例如 streamer face filter 是否抹掉特定族群、特定遊戲)沒有任何審計。
- 11B 的 headline 數字幾乎完全是 dynamics model 的容量(10.1B);真正的方法創新——LAM——只有 300M,這項規模差異使得 scaling laws 圖(Figure 9)其實是在量「conditional video generator」如何 scale,而非量「learned action interface」本身的 scaling。

### 4.3 Phyra's Judgment (summary)

真正的新東西是 **LAM 把離散 latent action 當作可由人類操作的搖桿介面**這個概念,以及把 ST-transformer 推廣到 tokenizer / LAM / dynamics 三大模組的工程整合;ST-ViViT 與 additive-action embedding 是具有獨立價值的經驗發現。其餘大部分(MaskGIT 解碼、VQ-VAE tokenizer、scaling 行為、資料策畫)屬於把現有元件推向更大規模的工程努力。**核心未解問題**是這個 8-code 的 latent action 介面能否擴展到複雜動作空間、跨領域(3D、第一人稱、機器人 BC)以及長 horizon,目前所有正面結果都落在 2D platformer 與短於 16 frames 的窗口內。

## 5. Methodology Deep Dive

### 5.1 Method Overview

Genie 將「生成式互動環境」拆解成三個串接的離散 token 模組,並以 ST-transformer 為共同骨幹貫穿全流程。輸入端是 $T$ 影格的原始視訊 $\boldsymbol{x}_{1:T} \in \mathbb{R}^{T \times H \times W \times C}$;**Video Tokenizer**(VQ-VAE,200M 參數,patch size 4,codebook size 1024,embedding dim 32)將其壓縮為離散 token 序列 $\boldsymbol{z}_{1:T} \in \mathbb{I}^{T \times D}$,並以 ST-ViViT 在 encoder/decoder 兩側都注入時序因果性,使 $z_t$ 能依賴 $\boldsymbol{x}_{1:t}$。**Latent Action Model (LAM)**(300M 參數,patch size 16,codebook 僅 $|A|=8$ 個碼)以原始像素為輸入,經由 inverse-dynamics 風格的 encoder–decoder 在每對相鄰影格間萃取連續潛在動作 $\tilde{\boldsymbol{a}}_{1:T-1}$,再以 VQ-VAE 量化為極小離散集合;decoder 僅在訓練時提供重建訊號,推論時整個 LAM 除 codebook 外皆被丟棄,改由使用者直接輸入 $a_t \in [0, |A|)$。**Dynamics Model**(decoder-only MaskGIT transformer,主模型 10.1B 參數)以 $\boldsymbol{z}_{1:t-1}$ 與 stop-gradient 過的 $\tilde{\boldsymbol{a}}_{1:t-1}$ 作為條件,自迴歸地預測下一影格 token $\hat{z}_t$。

訓練分兩階段:先單獨訓練 video tokenizer,再凍結 tokenizer、共同訓練 LAM(從像素)與 dynamics model(從 token)。三個模組都採用 ST-transformer 的時空交錯注意力以使主導計算量隨 $T$ 線性而非二次成長,並省略 spatial layer 之後的 FFW 以將參數預算挪給其他元件,實驗顯示能顯著提升結果。三項關鍵設計選擇驅動整體效能:(1) 動力學模型把潛在動作以 **加性 embedding** 而非串接方式注入,顯著提升可控性(§3.4 ablation);(2) LAM 以 **像素而非 token** 為輸入,實驗顯示 pixel-input 在 Platformers 與 Robotics 兩個資料集上 $\Delta_t\text{PSNR}$ 均優於 token-input(Table 2);(3) tokenizer 採 ST-ViViT 而非 spatial-only ViT 或 full-attention C-ViViT,以記憶體換取最佳 FVD 與 $\Delta_t\text{PSNR}$(Table 3)。

推論時(§2.2,Figure 8),使用者提供初始影格 $x_1$,由 video tokenizer encoder 取得 $z_1$,再選擇離散動作 $a_1 \in [0, |A|)$,經 codebook 索引得到 $\tilde{a}_1$,送入 dynamics model 預測 $\hat{z}_2$;迭代此過程產生 $\hat{\boldsymbol{z}}_{2:T}$,最後由 tokenizer decoder 還原成像素影格 $\hat{\boldsymbol{x}}_{2:T}$。每影格採樣使用 25 個 MaskGIT 步驟,temperature=2,random sampling。模型在 16 影格、10 FPS、160×90 解析度的設定下訓練。

### 5.2 Pipeline Diagram with Tensor Shapes

```
Input video x_{1:T}                              [B, T, H, W, C] = [B, 16, 90, 160, 3]
   │
   ├──────────────────────────────────────────────────────────────────┐
   │                                                                  │
   ▼                                                                  ▼
┌──────────────────────────┐                            ┌──────────────────────────┐
│  Video Tokenizer         │                            │  Latent Action Model     │
│  (VQ-VAE + ST-ViViT)     │                            │  (ST-transformer, |A|=8) │
│  patch=4, |V|=1024       │                            │  patch=16, encoder takes │
│  embed_dim=32            │                            │  pixels x_{1:T}, decoder │
│                          │                            │  reconstructs x_{t+1}    │
│  Encoder:                │                            │                          │
│   patch embed →          │                            │  Encoder (causal):       │
│   [B, T, H/4, W/4, d_v]  │                            │   x_{1:T} →              │
│   ST-blocks (causal      │                            │   continuous ã_{1:T-1}   │
│   in time) →             │                            │   shape [B, T-1, d_a]    │
│   [B, T, H/4, W/4, d_v]  │                            │                          │
│   VQ quantize →          │                            │  VQ codebook (|A|=8):    │
│   z_{1:T} ∈ ℤ^{T×D}      │                            │   ã → discrete a_{1:T-1} │
│                          │                            │   shape [B, T-1]         │
│  Output (train+infer):   │                            │                          │
│   z_{1:T}                │                            │  Decoder (train only):   │
│   shape [B, T, D]        │                            │   x_{1:t}, ã_{1:t} →     │
│   D = (H/4)·(W/4) = ?    │                            │   x̂_{t+1}                │
│   (paper does not        │                            │                          │
│    specify D explicitly) │                            │  Inference: discard all  │
└──────────────┬───────────┘                            │  except codebook;        │
               │                                        │  user supplies a_t       │
               │                                        └──────────────┬───────────┘
               │                                                       │
               │   z_{1:T-1}                                            │   ã_{1:T-1}
               │   [B, T-1, D]                                          │   [B, T-1, d_dyn]
               │                                                       │
               ▼                                                       ▼
            ┌──────────────────────────────────────────────────────────────┐
            │  Dynamics Model (decoder-only MaskGIT, ST-transformer)       │
            │  Input tokens:    z_{1:T-1}        [B, T-1, D]               │
            │  Action embeds:   ã_{1:T-1}        [B, T-1, d_dyn]   ← additive,
            │                                                       NOT concat
            │  At train time: random Bernoulli mask on z_{2:T-1},          │
            │  rate ~ U(0.5, 1)                                            │
            │  Stack of L ST-blocks (spatial attn within frame,            │
            │  causal temporal attn across frames, 1 FFW per block)        │
            │  Output logits over codebook V for ẑ_{2:T}                   │
            │  shape [B, T-1, D, |V|]    |V|=1024                          │
            │  Loss: cross-entropy(ẑ_{2:T}, z_{2:T})                       │
            └──────────────────────────────┬───────────────────────────────┘
                                           │ ẑ_{2:T} ∈ ℤ^{(T-1)×D}
                                           ▼
                              ┌────────────────────────────┐
                              │  Tokenizer Decoder         │
                              │  ẑ_{2:T} → x̂_{2:T}         │
                              │  shape [B, T-1, H, W, C]   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              Generated frames x̂_{2:T}
                              [B, 15, 90, 160, 3]

Inference loop (§2.2):
  x_1 ──tokenizer.encode──► z_1 ──┐
                                  ├─ dynamics ─► ẑ_2 ─ decode ─► x̂_2
  user picks a_1 ∈ [0,|A|) ──VQ──► ã_1 ──┘
  (repeat for t=2..T, autoregressively feeding ẑ_{1:t-1}, ã_{1:t-1})
```

### 5.3 Per-Module Breakdown

#### 5.3.1 ST-transformer Backbone

**Function:** 共用骨幹,以 $L$ 個時空 block 交錯執行 spatial attention(每影格內 $H \times W$ token)與 temporal attention(跨 $T$ 影格、causal mask),並在 spatial+temporal 之後接單一 FFW,使主導計算量隨影格數線性而非二次成長。

**Input:**
- Name: token sequence(視模組而定:patch embeds、video tokens 或 action embeds)
- Shape: `[B, T, H', W', d]`
- Source: 上游 patch embedding 或上一個 ST-block

**Output:**
- Name: 同形狀的 contextualized representation
- Shape: `[B, T, H', W', d]`
- Consumer: 下一個 ST-block 或 task-specific head

**Processing:**

1. Spatial self-attention over $1 \times H' \times W'$ tokens within each timestep。
2. Temporal self-attention over $T \times 1 \times 1$ tokens with causal mask。
3. Single feed-forward layer after both attention layers(刻意省略 post-spatial FFW 以節省參數,作者指出這顯著改善結果)。

**Key Formulas:**

主導 spatial 注意力的計算複雜度為

$$
\mathcal{O}(L \cdot T \cdot (H' W')^2 \cdot d)
$$

對 $T$ 為線性,而 full space-time attention(如 C-ViViT)為 $\mathcal{O}(L \cdot (T H' W')^2 \cdot d)$,對 $T$ 為二次。

**Implementation Details:**

採 bfloat16 與 QK-norm(Dehghani 等, 2023; Henry 等, 2020)以穩定大規模訓練。論文未公開 $L$、head 數、$d$ 等具體超參數。

---

#### 5.3.2 Video Tokenizer (ST-ViViT VQ-VAE)

**Function:** 將原始影格序列壓縮為離散 token,提供 dynamics model 的目標空間,並在 decoder 階段把預測 token 還原為像素。

**Input:**
- Name: $\boldsymbol{x}_{1:T}$
- Shape: `[B, T, H, W, C]` = `[B, 16, 90, 160, 3]`
- Source: 原始 RGB 影片(160×90, 10 FPS, 16 frame clips)

**Output:**
- Name: $\boldsymbol{z}_{1:T}$
- Shape: `[B, T, D]`,其中 $D$ 為每幀 token 數,paper 未明示 $D$ 的具體值
- Consumer: dynamics model(輸入)、tokenizer decoder(推論時還原像素)

**Processing:**

1. patch size 4 → 將每幀切為 $(H/4) \times (W/4)$ patches。
2. ST-ViViT encoder 以 causal temporal attention 整合 $\boldsymbol{x}_{1:t}$ 的歷史資訊到 $z_t$。
3. VQ-VAE 量化:對每個 patch embedding 找出 codebook 中最近鄰索引,得到 $z_{t,i} \in \{1,\dots,|V|\}$,$|V|=1024$,embedding dim 32。
4. Decoder 以同樣 ST-ViViT 結構從 token 還原像素,訓練以重建 + commitment loss(標準 VQ-VAE 目標)。

**Key Formulas:**

VQ-VAE 標準目標函數:

$$
\mathcal{L}_{\text{VQ}} = \|x - \hat{x}\|_2^2 + \|\mathrm{sg}[z_e(x)] - e\|_2^2 + \beta\,\|z_e(x) - \mathrm{sg}[e]\|_2^2
$$

其中 $z_e(x)$ 為 encoder 輸出,$e$ 為對應 codebook 向量,$\mathrm{sg}[\cdot]$ 為 stop-gradient。

**Implementation Details:**

200M 參數;patch size 4;codebook size 1024,embedding dim 32(作者指出此組合在重建品質與下游預測之間取得最佳折衷)。Tokenizer 於第一階段單獨訓練,之後參數凍結供 dynamics model 使用。論文未明示每幀產生的 token 數 $D$;若依 patch size 4 計算可能為 $(H/4)\cdot(W/4)$ 量級,但 paper does not specify。

---

#### 5.3.3 Latent Action Model (LAM)

**Function:** 在無動作標籤的影片中,以 inverse-dynamics 形式從相鄰影格之間萃取「最重要的變化」並量化為極小離散動作集 $|A|=8$,使其可作為人類可操控的搖桿按鍵。

**Input:**
- Name: $\boldsymbol{x}_{1:T}$(訓練時 encoder 用整段影片;decoder 額外用 $\boldsymbol{x}_{1:t}$ 與 $\tilde{\boldsymbol{a}}_{1:t}$)
- Shape: `[B, T, H, W, C]`
- Source: 原始像素(消融實驗顯示 pixel-input 優於 token-input,Table 2)

**Output:**
- Name: $\tilde{\boldsymbol{a}}_{1:T-1}$(連續 latent,經 VQ 後得離散 $a_{1:T-1}$)
- Shape: 連續為 `[B, T-1, d_a]`,離散為 `[B, T-1]`,$a_t \in [0, 8)$
- Consumer: dynamics model(以加性 embedding 注入);推論時整個 LAM 除 codebook 外被丟棄,$a_t$ 由使用者提供

**Processing:**

1. Encoder 為 ST-transformer,以 causal temporal mask 一次處理整段 $\boldsymbol{x}_{1:T}$,輸出每對相鄰影格之間的連續 latent $\tilde{a}_t$。
2. VQ-VAE 量化 $\tilde{a}_t$ 至 codebook(size $|A|=8$,embedding dim 32),強制把資訊壓進極小離散集合。
3. Decoder 接收 $\boldsymbol{x}_{1:t}$ 與 $\tilde{\boldsymbol{a}}_{1:t}$,預測 $\hat{x}_{t+1}$;由於 decoder 只能看到歷史與動作,$\tilde{a}_t$ 必須編碼相鄰影格間最重要的變化才能重建。
4. 推論時整個 encoder/decoder 皆丟棄,只保留 codebook 供使用者輸入 $a_t$ 索引。

**Key Formulas:**

訓練目標為下一幀重建 + VQ commitment(simplified):

$$
\mathcal{L}_{\text{LAM}} = \mathbb{E}_{t}\Big[\|x_{t+1} - \hat{x}_{t+1}\|_2^2\Big] + \mathcal{L}_{\text{VQ}}(\tilde{a}_t)
$$

**Implementation Details:**

300M 參數;patch size 16;codebook size $|A|=8$,embedding dim 32。消融(Table 2)顯示 pixel-input 在 Platformers 與 Robotics 上 $\Delta_t\text{PSNR}$ 分別為 1.91 vs. 1.33、2.07 vs. 1.65,優於 token-input;FVD 在 Platformers 上略遜(40.1 vs. 38.8),但在 Robotics 上顯著更佳(136.4 vs. 257.8)。

---

#### 5.3.4 Dynamics Model (MaskGIT Transformer)

**Function:** 以過去 token 與潛在動作為條件,自迴歸生成下一影格的 token,完成幀層級可控的世界模擬。

**Input:**
- Names: $\boldsymbol{z}_{1:t-1}$、$\tilde{\boldsymbol{a}}_{1:t-1}$(stop-gradient)
- Shapes: $\boldsymbol{z}$ 為 `[B, T-1, D]`,$\tilde{\boldsymbol{a}}$ 為 `[B, T-1, d_dyn]`
- Source: video tokenizer(token)、LAM codebook(action embedding)

**Output:**
- Name: $\hat{\boldsymbol{z}}_{2:T}$(每個位置在 $|V|=1024$ 上的 logits)
- Shape: `[B, T-1, D, |V|]`
- Consumer: 訓練時計算 cross-entropy 對 ground-truth $\boldsymbol{z}_{2:T}$;推論時取樣後 feedback 給下一步,並由 tokenizer decoder 還原成像素

**Processing:**

1. Token embedding 後,以 **加性** 方式注入 $\tilde{a}_t$ embedding(而非 concat),作者明確指出此設計顯著提升可控性。
2. ST-transformer(decoder-only MaskGIT)堆疊,causal 結構讓模型一次看完 $\boldsymbol{z}_{1:T-1}$ 與 $\tilde{\boldsymbol{a}}_{1:T-1}$,並輸出全部 $\hat{\boldsymbol{z}}_{2:T}$。
3. 訓練時對 $\boldsymbol{z}_{2:T-1}$ 以 Bernoulli($p$) 隨機 mask,$p \sim U(0.5, 1)$;模型學習在不同 mask 比例下重建被遮蓋的 token。
4. 推論時每幀執行 25 個 MaskGIT 並行解碼步驟,temperature=2,random sampling。

**Key Formulas:**

訓練 cross-entropy(僅在被 mask 的位置計算):

$$
\mathcal{L}_{\text{dyn}} = -\sum_{t=2}^{T}\sum_{i \in \mathcal{M}_t} \log p_\theta\big(z_{t,i} \,\big|\, \boldsymbol{z}_{1:t-1},\ \mathrm{sg}[\tilde{\boldsymbol{a}}_{1:t-1}]\big)
$$

加性動作注入(對比 concat 的關鍵設計):

$$
h_{t,i} = \mathrm{Embed}(z_{t,i}) + \mathrm{Embed}(\tilde{a}_t)
$$

**Implementation Details:**

最終 Genie dynamics model 為 10.1B 參數,batch size 512,共訓練 125k 步,使用 256 個 TPUv5p;加上 tokenizer 與 LAM 共 10.7B 參數,訓練 942B token。採用 bfloat16 與 QK-norm 穩定大規模訓練。Scaling 實驗(Figure 9)顯示 dynamics model 從 40M 到 2.7B 參數呈現乾淨的 power-law 行為,batch size 從 128 擴到 448(1.9M→6.6M tokens)亦帶來一致的 loss 下降。

---

#### 5.3.5 Inference / Action-Controllable Video Generation

**Function:** 在推論時把整個系統當作可逐影格操控的虛擬環境,玩家輸入離散動作即可生成對應的下一影格。

**Input:**
- Name: prompt frame $x_1$(可為 OOD 圖像、文字到圖像生成、手繪草圖、真實照片);使用者動作序列 $a_{1:T-1} \in [0, |A|)$
- Shape: $x_1$ 為 `[B, 1, H, W, C]`;每個 $a_t$ 為純量索引
- Source: 使用者(人類玩家)

**Output:**
- Name: $\hat{\boldsymbol{x}}_{2:T}$
- Shape: `[B, T-1, H, W, C]`
- Consumer: 顯示介面 / 玩家;在訓練 agent 場景下也可作為模擬軌跡

**Processing:**

1. 將 $x_1$ 經 tokenizer encoder 取得 $z_1$。
2. 玩家選擇 $a_1 \in [0, |A|)$,以 codebook 索引得到 $\tilde{a}_1$。
3. dynamics model 以 $z_1, \tilde{a}_1$ 預測 $\hat{z}_2$(以 25 步 MaskGIT 並行解碼)。
4. 重複 step 2–3:$\hat{\boldsymbol{z}}_{1:t-1}, \tilde{\boldsymbol{a}}_{1:t-1} \rightarrow \hat{z}_t$。
5. 將 $\hat{\boldsymbol{z}}_{2:T}$ 經 tokenizer decoder 還原為 $\hat{\boldsymbol{x}}_{2:T}$。

**Key Formulas:**

整體推論為 $T-1$ 步的條件採樣:

$$
\hat{z}_t \sim p_\theta\big(z_t \,\big|\, \hat{\boldsymbol{z}}_{1:t-1},\ \tilde{\boldsymbol{a}}_{1:t-1}\big),\quad t = 2,\dots,T
$$

**Implementation Details:**

每幀 25 個 MaskGIT 取樣步驟,temperature=2,random sampling。模型可從一張或多張 prompt frame 啟動;論文指出每個離散動作的語意在不同初始影格間保持一致,因此「學習 latent action 的對應關係」就像學習新搖桿的按鍵配置。模型目前約 1 FPS,作者列為未來改進方向之一(§5 Conclusion)。

## 6. Experiments

### 6.1 Datasets

| Dataset | Task | Scale | Usage (train/val/test) |
|---|---|---|---|
| Platformers (filtered Internet 2D platformer videos) | 視訊生成、世界模型訓練 | 6.8M 個 16s clips（30k 小時，10 FPS、$160 \times 90$）；自原始 55M 個 clips（244k 小時）篩選而來 | 訓練（11B Genie 主模型；論文未明確切分 val/test split） |
| Robotics（RT1 + 模擬資料 + Kalashnikov et al. 2018 的 209k episodes） | 跨域視訊生成驗證 | $\sim$130k robot demos + 209k real robot episodes + 模擬資料；不使用 action labels | 訓練 2.5B 模型；test split 上回報 FVD=82.7 |
| CoinRun (Procgen, hard mode) | Behavioral Cloning 評估與可復現 case study | BC 實驗用 expert sequences（來自 R2D2 agent）；reproducible case study 收集 10M transitions（10k seeds × 1000 timesteps） | 在 held-out test levels 上評估 |

### 6.2 Evaluation Metrics

| Metric | Description | Primary? |
|---|---|---|
| FVD (Frechet Video Distance) | video-level 生成品質指標，與人工視訊品質評估高度對齊（Unterthiner et al., 2019） | yes |
| $\Delta_t \text{PSNR}$ | 自訂 controllability 指標：$\text{PSNR}(x_t, \hat{x}_t) - \text{PSNR}(x_t, \hat{x}'_t)$，比較使用 ground-truth 推得 latent actions 與隨機抽樣 latent actions 之生成差異；越大代表 latent actions 控制力越強。實驗皆報告 $t=4$ | yes |
| Mean % levels solved (out of 100) | CoinRun BC 評估指標，5 seeds 平均並回報 95% CI | no（僅用於 §3.3 agent 訓練實驗） |
| Tokenizer reconstruction PSNR | tokenizer 訓練時的重建品質（附錄 Table 6） | no |

### 6.3 Training and Inference Settings

- **硬體**：最終 Genie 使用 256 TPUv5p；scaling 實驗使用 64–256 顆 TPUv2/v3；reproducible case study 可在單顆 16 GB TPU 上跑滿（Appendix F）。
- **模型規格**：video tokenizer 200M params（patch size 4、codebook 1024 codes、embedding dim 32）；LAM 300M params（patch size 16、$|A|=8$、embedding dim 32）；最終 dynamics model 10.1B params（48 layers、36 heads、$d_{\text{model}}=5120$、k/q size 128，FLOPs $6.6 \times 10^{22}$，Appendix Table 12），合計 10.7B params。
- **序列長度**：16 frames @ 10 FPS。
- **Batch size 與步數**：最終 Genie 用 batch size 512、訓練 125k steps、共 942B tokens；scaling 實驗用 batch size 256、200k steps、750B tokens。
- **Optimizer**：AdamW，dynamics model 用 max_lr 3e-5、min_lr 3e-6、$\beta_1=0.9$、$\beta_2=0.9$、weight_decay 1e-4、5k warmup steps（Appendix Table 9）；tokenizer 用 max_lr 3e-4、cosine decay、10k warmup（Appendix Table 8）。
- **數值穩定性**：採用 bfloat16 與 QK norm 以穩定大規模訓練（Dehghani et al., 2023; Henry et al., 2020）。
- **平行化**：batch parallelism + ZeRO stage-3 sharding；較大模型再加 tensor parallelism（Appendix Table 10）。
- **Inference**：每張 frame 進行 25 個 MaskGIT steps，temperature 2，random sampling；latent action 以 additive embedding 加入（而非 concat）。
- **資料篩選 pipeline**：人工標註 10k 影片（5–1 評分），訓練 11M ResNet18 二分類器，依信心度規則篩選；篩選後資料雖只剩 $\sim$10%，但 FVD 反而從 61.4 降到 54.8（Appendix Table 4）。

### 6.4 Main Results

| Method | FVD ($\downarrow$) | $\Delta_t \text{PSNR}$ ($\uparrow$) | Notes |
|---|---|---|---|
| 580M model on original 55M Platformers dataset | 61.4 | the paper does not specify | 資料篩選消融基線（Appendix Table 4） |
| 580M model on curated 6.8M Platformers dataset | 54.8 | the paper does not specify | 證明資料品質 > 數量 |
| **Genie 11B on Platformers** | **the paper does not specify** | **the paper does not specify**（主表僅以定性結果與 ablation 中的 2.5B 變體報告數字） | 11B foundation world model；OOD 提示（text-to-image、手繪、實拍）皆能產生可控 trajectory（Fig. 10, 12, 17） |
| **Genie 2.5B on Robotics (test split)** | **82.7** | **the paper does not specify** | 同一套 Platformers hyperparameters 直接搬用，學到 robotic arm 控制與物件變形（Fig. 11, 13） |
| Oracle BC（access 到 expert ground-truth actions，CoinRun） | — | — | 上界基準；BC 結果見 Fig. 15 |
| **Genie LAM-based BC（CoinRun）** | — | — | 在僅 200 個 expert action labels 下即可達到 oracle 水準，且 LAM 從未見過 CoinRun |
| Random agent（CoinRun） | — | — | 下界基準 |

論文的 headline 主張（高保真、可控、可從 OOD 影像 prompt 出可玩世界）主要靠定性展示（Fig. 1, 2, 10–14, 17）支持，量化 FVD/$\Delta_t \text{PSNR}$ 數字大多落在 ablation 表格中。

### 6.5 Ablation Studies

- **LAM input：pixels vs. tokens（Table 2）**——把 LAM encoder 的輸入從原始 frames 改成 tokenizer 產生的 $z$。Platformers 上 token-input 取得稍低 FVD（38.8 vs. 40.1），但 $\Delta_t \text{PSNR}$ 大幅變差（1.33 vs. 1.91）；Robotics 上 token-input 兩個指標都輸（FVD 257.8 vs. 136.4、$\Delta_t \text{PSNR}$ 1.65 vs. 2.07）。這是診斷性 ablation：直接質問「dynamics 訊號該從像素還是 tokens 抽取」，並用 controllability 指標揭露 tokenization 會丟失動作相關訊號。
- **Tokenizer architecture：ViT vs. C-ViViT vs. ST-ViViT（Table 3）**——固定 $\sim$200M 參數、patch size 10、batch 128、序列 16，比較三種 tokenizer。ST-ViViT 取得最佳 FVD 81.4（vs. ViT 114.5、C-ViViT 272.7）與最佳 $\Delta_t \text{PSNR}$ 1.66；C-ViViT 雖具完整 space-time attention 但記憶體 1.6 GB（vs. ST-ViViT 0.9 GB、ViT 0.3 GB）且過擬合明顯。屬診斷性 ablation：證明「線性 cost 的時空注意力組合」優於「平方 cost 的 joint attention」。
- **Dataset curation（Appendix Table 4）**——比較未篩選 55M vs. 篩選後 6.8M（皆 580M model）。FVD 從 61.4 降到 54.8。介於診斷與 sanity check 之間：確立「品質 > 數量」但未做更精細的 curation rule ablation。
- **Tokenizer batch size（Appendix Table 6）**——batch 64 vs. 384，PSNR 從 35.7 升到 36.5。屬 sanity check 等級的 scaling sweep。
- **Codebook size（§C.1 一句話帶過）**——「增加 codes 數會提升性能但降低人類可玩性」，但論文未提供量化表，較像設計取捨陳述而非 ablation。

整體而言，LAM input 與 tokenizer architecture 兩項是真正的 diagnostic ablations，且都與論文的核心架構主張對齊；缺少的是 dynamics model 設計選擇（如 additive vs. concat action embedding，文中只在 §2.1 一句帶過未量化）以及 codebook size $|A|$ 的量化掃描。

### 6.6 Phyra Experiment Assessment

- [partial] Has at least one strong baseline (a current SoTA on the chosen task) — Tokenizer ablation 與 ViT 及 C-ViViT (Phenaki) 比較，但 Platformers 上的 11B Genie 並未與 Phenaki、TECO、MaskViT、UniSim、GAIA-1 等可比視訊/世界模型直接 head-to-head 比 FVD，主表幾乎沒有外部 baseline。
- [covered] Has cross-task / cross-dataset evaluation (not just one benchmark) — 同一架構分別在 Platformers、Robotics(RT1+模擬+Kalashnikov)、CoinRun(BC) 三個截然不同的 domain 訓練/評估，並以 OOD（手繪、實拍、Imagen2 圖像）做 prompt。
- [covered] Has ablations that diagnose the new components (not just sanity checks) — LAM input（pixel vs. token）與 tokenizer architecture（ViT/C-ViViT/ST-ViViT）兩個 ablation 直接針對論文新提出的設計選擇做診斷。
- [covered] Has a scaling study (size, length, or compute) — Fig. 9 與 Appendix Table 10：dynamics model 從 41M 到 2.7B 參數的 7 點 scaling、以及 2.3B 模型在 batch 128/256/448 的 batch-size scaling，皆顯示 loss 隨 compute 一致下降。
- [partial] Has an efficiency / wall-clock comparison — Tokenizer ablation 表附 memory（0.3 / 1.6 / 0.9 GB）、Appendix Table 10 列出每個 scaling 點的 training time（3–16 days）與 FLOPs，但沒有直接的 inference latency 或與 baseline 的 wall-clock 對比；論文也明白指出當前僅 $\sim$1 FPS。
- [partial] Reports variance / standard deviation / multiple seeds where relevant — Fig. 15 的 BC 結果有「averaged over 5 seeds with 95% confidence intervals」；但 FVD、$\Delta_t \text{PSNR}$、scaling curves 皆為單次數字，未報告多 seed 變異。
- [missing] Releases code / weights / data sufficient for reproducibility — Broader Impact 段明確聲明「We have chosen not to release the trained model checkpoints, the model's training dataset, or examples from that data」。Appendix F 提供 CoinRun 上的小型可復現 case study 作為 partial 緩解，但主 11B 模型與 Platformers 資料皆不釋出。

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

- **Claim 1**:「首個僅靠未標註影片就能 frame-level 控制的 generative environment」。**支持**——Table 1 所定位的設計確實前所未見,Figure 17 在 platformer、Figure 13 在 robotics 都示範了可重複的 latent action 語義。但是「無需動作標籤」在 agent 訓練端被 Appendix E.1 的「expert action 字典」削弱,屬於部分支持。
- **Claim 2**:「foundation world model,11B 參數,能對 OOD prompt 泛化」。**部分支持**——Figure 10 的 sketch / photo / text-to-image prompt 確實能產生看似合理的軌跡,但缺乏量化 OOD generalization 的測量(例如 OOD prompt 下的 FVD 或 controllability),全靠 cherry-picked qualitative。
- **Claim 3**:「ST-transformer 是支撐這種規模訓練的關鍵」。**支持**——Table 3 的 C-ViViT vs. ST-ViViT 比較與 Figure 9 的 scaling 曲線提供了直接證據。
- **Claim 4**:「latent actions 學自網路影片可遷移到未見環境的 imitation learning」。**部分支持**——Figure 15 在 CoinRun 上達到 oracle 水準,但 CoinRun 與訓練資料同屬 2D platformer 且 oracle 本身在 200 samples 已飽和,並沒有真正驗證跨領域遷移;同時 latent→real 的對應仍需 ground-truth action,削弱了「unlock unlimited data」的口號。
- **Claim 5**:「scales gracefully with compute」。**支持**——Figure 9 的左中右三圖各自呈現 monotonic 改善,且 final 10.1B 模型的訓練細節(942B tokens, 256 TPUv5p, 125k steps)有完整紀錄。

### 7.2 Fundamental Limitations of the Method

**離散 latent action 詞彙的容量瓶頸**。整個方法把「動作」壓縮到 |A|=8 的 codebook,並由 reconstruction loss 決定每一個 code 的語意。這在 2D platformer 這種離散按鍵語意豐富、視覺位移可區辨的環境是可行的,但若要處理連續控制(機械臂力控)或多模態動作(攝影機運動 + 角色行為 + 環境互動),codebook 必然要擴大,而作者在 Appendix C.1 已經承認擴大會降低 playability。換言之,這個介面的「可玩性」與「動作豐富度」存在無法在當前公式下消除的取捨。

**動作監督仍以隱藏方式進入 agent pipeline**。論文在 abstract 與 §1 強調「training without any ground-truth action labels」,但在 §3.3 與 Appendix E.1 中,latent→real action 的對應字典 D 是用 ground-truth action labeled 的 expert sequences 構造的。也就是說,Genie 把動作標註從「訓練世界模型」推遲到「部署時 calibrate 介面」,而非真正消除它;對下游使用者而言,動作標註的需求並未消失。

**短時間視窗、低 frame rate 是架構級而非工程級的限制**。雖然作者把 16 frames、~1 FPS 列為「可未來改進」,但 ST-transformer 的 temporal attention 仍是 causal full attention,把窗口擴大會讓 cost 線性放大,而 MaskGIT 對每幀 25 sampling steps 的固定開銷使 FPS 提升必須改架構(例如 distillation、parallel decoding)。在當前公式下,長期一致性與互動 latency 無法同時改善。

**評估指標的封閉性使「品質」難以與外部模型比較**。FVD 與 Δ_t PSNR 都是論文自家在自家 dataset 上量測的;Δ_t PSNR 更是新提出且僅 t=4。沒有與 Phenaki、MAGVIT、SVD 等同期 video model 在共同 benchmark 對齊的數字,使外界難以判斷 ST-ViViT 帶來的 FVD 81.4 是相對怎樣的水準,也使 scaling 曲線的「斜率優勢」缺乏外部錨點。

### 7.3 Citations Worth Tracking

- **Chang et al. 2022, MaskGIT** — dynamics model 的解碼骨幹,理解 Genie 的 frame-by-frame 生成必須先理解 MaskGIT 的雙向 masked decoding 與 temperature 採樣行為。
- **Villegas et al. 2023, Phenaki** — 最直接的前驅(C-ViViT temporal tokenizer),Genie 的 ST-ViViT 之所以「更好」要看 Phenaki 在做什麼以及它的 quadratic cost 是怎麼產生的。
- **Baker et al. 2022, VPT** — 在「用網路影片做動作 inference」這條 thread 上的對立陣營(用人類標 labels 訓 inverse dynamics model);與 Genie 的 latent action 路線形成清晰的對照。
- **Schmidt & Jiang 2024, Learning to Act Without Actions** — 同期 latent action 路線,適合用來檢驗 Genie 的設計選擇是否獨特。
- **Yang et al. 2023, UniSim / Hu et al. 2023, GAIA-1** — 同時期 scaling-up world model,但仍依賴 text + action labels;閱讀後可定量理解「放棄 action labels」帶來的實際機會成本。

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

- [ ] 當 |A| 從 8 擴展到 64、256 甚至連續時,FVD、Δ_t PSNR 與 BC 下游表現的 trade-off 曲線長什麼樣?是否存在最佳 codebook 大小,還是隨任務複雜度單調上升?
- [ ] 在 platformer 上學到的 LAM,移植到 3D 第一人稱環境(如 ProcThor、Habitat)或機器人 BC 時,latent action 的語意是否仍 cluster 為 down/up/left 這類人類可理解的方向?
- [ ] 把時間窗口從 16 frames 擴展(例如以 sliding-window 或 recurrent memory)後,長期一致性與 ~1 FPS 的瓶頸何者先成為 binding constraint?
- [ ] Δ_t PSNR 在 t = 8、16、32 時的 controllability 衰減曲線如何?是否存在某個 t 之後 latent action 完全失效,使「可控」變成短窗口幻覺?
- [ ] ResNet18 binary classifier 篩出的 6.8M videos 相對 55M 原集合,在遊戲類型、視覺風格、語言地區上的分布偏差為何?這個偏差是否解釋了模型對某些 OOD prompt 表現特別好或壞?
- [ ] 把 LAM encoder/decoder 拉到更大規模(例如 LAM 也 scale 到 1B 以上)是否能突破 codebook 必須極小的限制,讓 |A| 增大但不犧牲 controllability?
- [ ] 在 BC 評估中,若把 expert action 字典換成完全 unsupervised 的 latent→real 映射(如 Edwards et al. 2019 的 self-play 風格),200 樣本飽和的結論是否仍成立?

### 8.2 Improvement Directions

1. **替換 Δ_t PSNR 為跨 t 的 controllability 曲線並加入外部 benchmark**(高可行)。在現有 evaluation pipeline 上多加 t∈{1,4,8,16} 的測量,並在 UCF-101 / Kinetics 等公開 video model benchmark 上 report FVD;這樣外界才能定位 ST-ViViT 的絕對水準,且能診斷 long-horizon controllability 何時失效。
2. **量化 latent action consistency**(中可行)。設計一個自動指標——例如同一 latent code 在 N 個不同 prompt 下,角色 bounding box 的位移向量平均餘弦相似度——把 Figure 17 的「看起來一致」升級為可重複測量,並在不同 |A| 下繪曲線,這直接攻擊 §4.2.2 提到的 hand-picked 證據問題。
3. **在 LAM 旁訓練一個獨立的 inverse dynamics model 作為 calibrate-free baseline**(中可行)。把 §3.3 的 expert dictionary D 換成自動學習的對應(用 self-supervised 對齊,例如 latent action 與真實 action 的 mutual-information maximization),如果效果接近就能真正兌現「無需 action labels」的承諾。
4. **將 ST-transformer 的 temporal layer 改為 chunked / linear-attention**(中可行)。把 16 frames 限制提升到 64–128 frames,直接攻擊作者承認的長期一致性瓶頸,且不改動 LAM 與 dynamics 的訓練 loss。
5. **多領域聯合訓練 LAM,測試 latent action 是否會自我正則化為跨領域語義**(較困難)。把 platformer + robotics + driving 影片混合餵 LAM,觀察 8 個 codes 是否會 specialize 還是 share 跨領域基本動作(平移、旋轉、抓取);若能 share,就能把 Genie 從「2D platformer foundation model」推到真正的「foundation world model」。
6. **以 distillation / parallel decoding 把 inference frame rate 從 ~1 FPS 提到 10+ FPS**(較困難)。MaskGIT 的 25 sampling steps 是 FPS 主因,可借鑑 consistency models 或 progressive distillation 的方法,在保留 fidelity 的前提下壓低 sampling steps,直接解 §5 列為未解的 efficient frame rate 問題。
