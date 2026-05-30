# Ollama 使用備忘（phyra-dualtrans）

> 場景：用本機 Ollama 跑 LLM，搭配 BabelDOC 把 AI/CV 論文翻成台灣繁體中文。
> RTX 5090（32 GB VRAM）。

## TL;DR — 受管 Ollama（v0.2 起，預設）

**phyra-dualtrans 自己管 Ollama。** 啟動 WebUI 服務 → 它在一個**專屬
loopback port**（預設 `11500`）spawn 一個設定好的 `ollama serve`、確保
翻譯模型存在；**關掉 WebUI → 連同這個 Ollama 一起關**。UI 的 Base URL
**留空即可**（預設值自動指向受管實例）。

* 受管實例用**獨立 port**，**不會**撞或殺掉系統 Ollama（:11434）或你
  自己手動跑的實例（例如 :18763）。
* port 已被佔用且**是** Ollama → 直接重用（關閉時不會去殺它）。
* `ollama` 不在 PATH / port 被非 Ollama 佔用 → 受管功能停用，server
  照常起，preflight 會清楚說明（不會崩）。

關掉整套：`PHYRA_DUALTRANS_MANAGE_OLLAMA=0`，改用 `OLLAMA_HOST` 指你
自己的 server（或在 UI 填 Base URL）。

## 模型選擇

預設建立並使用 **`phyra-trans`**：從 `qwen3:14b` 疊上翻譯參數的調校版。

| 項目 | 值 | 理由 |
|---|---|---|
| base | `qwen3:14b`（Q4 ≈ 9 GB） | 5090 32GB 大幅留白 → 可開真並行；比 32B 快 2–3×；繁中學術品質足夠 |
| num_ctx | 8192 | 逐段翻譯，單次 = system + 一段（<1–2K tok），8192 綽綽有餘且整個塞進 VRAM |
| temperature | 0.3 | 穩定、少漂 |
| top_p / repeat_penalty | 0.9 / 1.05 | 沿用既有翻譯配方 |

第一次啟動會 `ollama pull qwen3:14b`（一次性，數 GB）再 `ollama
create phyra-trans`。**想省這次下載**且你已經 pull 過 32B：設
`PHYRA_DUALTRANS_OLLAMA_BASE_MODEL=qwen3:32b`（共用既有權重，create 只
是疊參數、秒級完成）。要更快可改 `qwen3:8b` / `qwen2.5:7b-instruct`。

相關環境變數見 `.env.example`（`PHYRA_DUALTRANS_OLLAMA_*`）。

## VRAM 數學（為何 num_ctx 8192、別設 32768）

qwen3 Q4_K_M 權重 + 每個並行槽一份 KV cache。`num_ctx` 越大 KV 越大。
`num_ctx 32768 ×` 並行 → 32B 會 > 32 GB → Ollama 把一部分溢到 CPU →
稠密模型只要有一層在 CPU 就**慢 20–40×**（實測 ~2 tok/s）。逐段翻譯
用不到大 context，`8192` 足夠且全程在 GPU。受管實例已設好
`OLLAMA_NUM_PARALLEL`（預設 2）與 `OLLAMA_KEEP_ALIVE=-1`（模型常駐，
不反覆 load/unload）。

確認全程在 GPU：

```bash
curl -s 127.0.0.1:11500/api/ps | python3 -m json.tool
# size_vram 必須 == size（100% 在 GPU）；CONTEXT 應是 8192
```

## 為何走原生 /api/chat + think:false

qwen3 等 hybrid reasoning 模型在 OpenAI 相容 `/v1` 上**無法關 thinking**，
一句翻譯多燒 ~400 tokens 隱藏推理（~9× tokens、3–8× 慢）。所以
phyra-dualtrans 的 `ollama` backend **不走 `/v1`**，直接打原生
`POST /api/chat` 並帶 `"think": false`（預設）。是否開 thinking 由 UI
的「Enable model thinking」開關決定（預設關）。

## 繁體中文（台灣）品質

系統 prompt 已強制台灣用語、保留專有名詞英文原文（見
`pipeline/prompts.py`）。若仍偶混簡體，可在 pipeline 末端跑
`opencc -c s2twp.json` 做後處理（選用）。

## 監控 / 疑難排解

```bash
curl -s 127.0.0.1:11500/api/tags        # 受管實例有哪些模型
curl -s 127.0.0.1:11500/api/ps          # 載入狀態 / CONTEXT / size_vram
nvidia-smi                              # VRAM 占用
# WebUI: GET /api/ollama → {managed, host, model, model_status, ready}
```

| 症狀 | 處理 |
|---|---|
| 首次啟動久 / model_status=preparing | 在背景 pull base（數 GB），完成即 ready；不阻塞 server |
| `port busy but not Ollama` | 改 `PHYRA_DUALTRANS_OLLAMA_PORT` |
| `ollama binary not found` | 裝 Ollama，或設 `PHYRA_DUALTRANS_MANAGE_OLLAMA=0` 指自己的 server |
| 翻譯極慢（~2 tok/s）/ PROCESSOR 顯示 CPU | num_ctx/並行太大溢出 → 用 14B base、確認 `size_vram==size` |
| 想用既有 32B 免下載 | `PHYRA_DUALTRANS_OLLAMA_BASE_MODEL=qwen3:32b` |
