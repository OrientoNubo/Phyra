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

**phyra-model-service 抽出（設計 A）**：模型層（managed Ollama / backends / runtime status）從 dualtrans 抽成共用 package `phyra_model_service`，供各服務與未來插件重用。
- package：`phyra-service/phyra-model-service/phyra_model_service/`
  — `backends/`（ollama native /api/chat + think off / openai / claude_cli）、`managed.py`（`ManagedOllama`，spawn/守護/teardown + idle 釋出 VRAM）、`runtime.py`（nvidia-smi + `/api/ps`）、`settings.py`（**統一 Ollama 預設的單一事實來源**）、`text.py`（`clean()`）、`retry.py`、`service/app.py`（薄控制面：`/healthz` `/api/runtime` `/api/ollama` `/api/models`）。
- dualtrans 改 import 該 package；`backends/{__init__,base,ollama}.py`、`runtime_status.py`、`pipeline/prompts.clean` 都成了**薄 re-export shim**（保留既有 import 路徑與測試）。`config.py` 的 ollama 設定全改走 `ModelSettings`。
- **熱路徑不經 HTTP**：翻譯 child（`python -m phyra_dualtrans.pipeline.translate_runner`）用同一 venv import package、直連 Ollama。
- 依賴：dualtrans `pyproject.toml` 以 `[tool.uv.sources]` editable path 指向 `../phyra-model-service`。
- 啟動：center `start.sh` 先起 model-service（擁有共用 Ollama :11500），等 `/api/tags` 就緒再起 dualtrans → dualtrans 走「偵測既有 Ollama 即重用」路徑、不重複 spawn。
- Runtime status badge 後端現由 `phyra_model_service.runtime.collect` 提供（dualtrans `runtime_status.py` 為 shim）；路由仍是 `web/routes_meta.py` 的 `GET /api/runtime?host=…`。
- 測試：package `tests/`（24）+ dualtrans `tests/`（117）= 141 全綠。
- 環境變數：新 canonical 前綴 `PHYRA_MODEL_OLLAMA_*` / `PHYRA_MODEL_*`；舊 `PHYRA_DUALTRANS_OLLAMA_*` / `OLLAMA_HOST` 仍以 alias 相容。idle VRAM 釋放預設 `PHYRA_MODEL_OLLAMA_KEEP_ALIVE=10s`。

## 標準約束（standing constraints）

- **secrets env-only**；per-user 偏好寫 browser localStorage，**絕不存 server**。
- **commit / push 只在使用者明確要求時做**。不要主動 commit 截圖、test PDF。
- dualtrans 中 `ollama` backend **不需密碼**；只有 `claude_cli` backend gated。
- 任何 GET query / log 都**不可**含 `api_key`。
- archbase：tag 編輯免密碼；delete 需 `PHYRA_ARCHBASE_ADMIN_PASSWORD`；綁 `0.0.0.0` 但無一般 auth，建議 `HOST=127.0.0.1`。
- 別動使用者的 port 8080 server。
- 使用者自己的 Ollama：port `18763`，model `qwen3-32b-trans`。phyra-model-service 的 managed Ollama 在 loopback `:11500` 跑 `qwen3:14b` 變體（`phyra-trans`）；dualtrans 重用之、不另 spawn。
- `drop_original` config 預設 `False`。
