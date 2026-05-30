#!/usr/bin/env bash
# phyra-model-service — 共用模型服務啟動器。
#
# 跑這支就好：它會確保 .venv、然後啟動控制面 WebAPI（前台，Ctrl+C 結束）。
# 服務本身會拉起一個專屬的 managed Ollama（loopback :11500，預設），並在
# 關閉時一起收掉。其餘 Phyra 服務（如 phyra-dualtrans）會偵測到這個已在跑
# 的 Ollama 並直接重用，不會重複 spawn。
#
# 環境變數：
#   PORT=8041                    控制面 WebAPI 埠（預設 8041）
#   HOST=127.0.0.1               綁定位址（控制面預設只給本機）
#   PHYRA_MODEL_OLLAMA_PORT=11500    managed Ollama 的 loopback 埠
#   PHYRA_MODEL_OLLAMA_KEEP_ALIVE=10s  閒置多久後釋出 VRAM（每次呼叫會重置）
#   PHYRA_MODEL_MANAGE_OLLAMA=0  不要 managed Ollama（改用自己的 OLLAMA_HOST）

set -euo pipefail

PORT="${PORT:-8041}"
HOST="${HOST:-127.0.0.1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1;36m▶ %s\033[0m\n' "$1"; }
info() { printf '  %s\n' "$1"; }

command -v uv >/dev/null 2>&1 || {
  echo "找不到 uv。先安裝：curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
}

# venv：uv 把絕對路徑寫死進 .venv，搬過資料夾就會壞。先探測，壞了才重建。
step "檢查執行環境 (.venv)"
if uv run --no-sync python -c "import phyra_model_service, fastapi, uvicorn" \
     >/dev/null 2>&1; then
  info "環境正常，略過重建。"
else
  info "環境缺失或失效 — 重建中…"
  rm -rf .venv
  uv sync
  info "重建完成。"
fi

step "啟動 phyra-model-service 控制面"
info "綁定 $HOST:$PORT"
info "managed Ollama：loopback :${PHYRA_MODEL_OLLAMA_PORT:-11500}"
info "（Ctrl+C 結束服務）"
exec env PORT="$PORT" HOST="$HOST" uv run --no-sync \
  python -m phyra_model_service.service.app
