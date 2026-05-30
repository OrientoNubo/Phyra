# Phyra — project context

Phyra monorepo 的工作根目錄。頂層分兩塊：`phyra-plugin/`（Claude Code plugin）與 `phyra-service/`（本地 / 線上 WebGUI 服務群）。`phyra-service/` 下每個服務都可單獨運行，也可由 phyra-center 整體啟動。

## 倉庫佈局

```
Phyra/                        ← monorepo 根（單一 git repo，名 Phyra）
├── phyra-plugin/             ← Claude Code research plugin（skills / agents / commands）
└── phyra-service/
    ├── phyra-center/         ← hub + 整體啟動腳本
    ├── phyra-archbase/
    ├── phyra-dualtrans/
    └── phyra-model-service/  ← 共用模型層（managed Ollama / claude headless），可被其他服務重用
```

## 服務佈局

| Service | Port | Path | 角色 |
|---|---|---|---|
| phyra-center | 8035 | `phyra-service/phyra-center/` | 著陸頁 / hub，列出 sibling tiles + 線上狀態 |
| phyra-archbase | 8037 | `phyra-service/phyra-archbase/` | 論文歸檔瀏覽（個人 paper collection） |
| phyra-dualtrans | 8039 | `phyra-service/phyra-dualtrans/` | PDF / arXiv → 雙語對照 PDF（FastAPI + BabelDOC） |
| phyra-model-service | 11500（Ollama） | `phyra-service/phyra-model-service/` | 共用模型服務：守住 managed Ollama + GPU/VRAM 狀態，供各服務 / 未來插件重用 |
| phyra-plugin | — | `phyra-plugin/` | Claude Code research plugin（skills / agents / commands） |

一鍵啟動：`./start-phyra.sh`（shim → `phyra-service/phyra-center/script/start.sh`）。

## 近期工作

dualtrans 的 **Runtime status badge**：Settings → Options 右側顯示 GPU + Ollama 狀態，抓 silent CPU fallback（nvidia-smi 死 → Ollama 自動切 CPU，~10× 慢）。
- 後端：`phyra_dualtrans/runtime_status.py` 探 `nvidia-smi` 與 Ollama `/api/ps`（size_vram 判 cpu/gpu/partial）。
- 路由：`web/routes_meta.py` 的 `GET /api/runtime?host=…`。
- 前端：`web/static/{index.html, app.js, styles.css}`，30 s 自動 re-probe、↻ 手動、backend 切換時觸發。
- 測試：`tests/test_runtime_status.py`。

## 標準約束（standing constraints）

- **secrets env-only**；per-user 偏好寫 browser localStorage，**絕不存 server**。
- **commit / push 只在使用者明確要求時做**。不要主動 commit 截圖、test PDF。
- dualtrans 中 `ollama` backend **不需密碼**；只有 `claude_cli` backend gated。
- 任何 GET query / log 都**不可**含 `api_key`。
- archbase：tag 編輯免密碼；delete 需 `PHYRA_ARCHBASE_ADMIN_PASSWORD`；綁 `0.0.0.0` 但無一般 auth，建議 `HOST=127.0.0.1`。
- 別動使用者的 port 8080 server。
- 使用者自己的 Ollama：port `18763`，model `qwen3-32b-trans`。dualtrans managed Ollama 在 loopback `:11500` 跑 `qwen3:14b` 變體。
- `drop_original` config 預設 `False`。
