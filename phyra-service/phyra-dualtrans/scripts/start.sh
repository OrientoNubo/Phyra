#!/usr/bin/env bash
# phyra-dualtrans — 一鍵即用啟動器。
#
# 跑這支就好，其餘自動處理（給「只想開來用」的人；開發者用底層的
# scripts/serve.sh）。它會依序：
#   1. 確保 .venv 可用（搬過資料夾／第一次 clone 都自動修；健康則秒過）
#   2. 缺 BabelDOC 模型或 CJK 字型才自動 warmup（一次性 ~340MB）
#   3. 啟動 WebUI 服務（前台，Ctrl+C 結束）
#   4. 服務就緒後自動開預設瀏覽器
#
# 環境變數：
#   PORT=9000        換埠（預設 8039）
#   NO_BROWSER=1     不要自動開瀏覽器
#   HOST=127.0.0.1   只綁本機（預設 0.0.0.0，內網其他人也能連）

set -euo pipefail

PORT="${PORT:-8039}"
HOST="${HOST:-0.0.0.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1;36m▶ %s\033[0m\n' "$1"; }
info() { printf '  %s\n' "$1"; }
warn() { printf '\033[1;33m  ⚠ %s\033[0m\n' "$1"; }

command -v uv >/dev/null 2>&1 || {
  echo "找不到 uv。先安裝：curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
}

# 1) venv ──────────────────────────────────────────────────────────────
# uv 把絕對路徑寫死進 .venv，搬過資料夾就會壞（import 失敗）。先探測，
# 壞了才整個重建（健康時這步幾乎不花時間）。
step "檢查執行環境 (.venv)"
if uv run --no-sync python -c \
     "import phyra_dualtrans, fastapi, uvicorn, fitz, openai" \
     >/dev/null 2>&1; then
  info "環境正常，略過重建。"
else
  info "環境缺失或失效（常見於搬移資料夾後）— 重建中…"
  rm -rf .venv
  uv sync
  info "重建完成。"
fi

# 2) BabelDOC 模型 + CJK 字型 ─────────────────────────────────────────
step "檢查 BabelDOC 模型與 CJK 字型"
FONT_DIR="$HOME/.cache/babeldoc/fonts"
if [ -f "$FONT_DIR/SourceHanSerifTW-Regular.ttf" ] \
   && [ -d "$HOME/.cache/babeldoc/models" ]; then
  info "已就緒，略過 warmup。"
else
  info "首次使用 — 下載模型與字型（一次性，約 340MB，請稍候）…"
  bash "$ROOT/scripts/warmup.sh"
fi

# 3) 啟動服務 + 4) 就緒後開瀏覽器 ─────────────────────────────────────
step "啟動 WebUI 服務"
info "綁定 $HOST:$PORT"
if [ "$HOST" = "0.0.0.0" ]; then
  info "本機可用內網 URL："
  for ip in $(hostname -I 2>/dev/null || true); do
    info "  http://$ip:$PORT/"
  done
fi
LOCAL_URL="http://localhost:$PORT/"
info "本機開：$LOCAL_URL"
info "（Ctrl+C 結束服務）"

# 暴露提醒：綁 0.0.0.0 + 主機有 claude CLI + 沒設密碼 → 任何連得到的人
# 都能燒掉你的 Claude 額度。只是警告，不擋啟動。
if [ "$HOST" = "0.0.0.0" ] \
   && command -v claude >/dev/null 2>&1 \
   && [ -z "${PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD:-}" ]; then
  echo
  warn "服務綁 0.0.0.0、無認證，且 claude_cli 後端未設密碼。"
  warn "任何能連到此位址的人都能用 claude_cli 花掉你的 Claude 額度。"
  warn "建議擇一："
  warn "  • 只給自己用： HOST=127.0.0.1 ./scripts/start.sh"
  warn "  • 設密碼：     PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD='你的密碼' ./scripts/start.sh"
fi

# 背景等服務起來，再開瀏覽器；不阻塞、開不了也不讓主流程失敗。
if [ "${NO_BROWSER:-0}" != "1" ]; then
  (
    for _ in $(seq 1 60); do
      if curl -fsS "http://localhost:$PORT/healthz" >/dev/null 2>&1; then
        for opener in xdg-open open "${BROWSER:-}"; do
          [ -n "$opener" ] && command -v "$opener" >/dev/null 2>&1 \
            && { "$opener" "$LOCAL_URL" >/dev/null 2>&1 & break; }
        done
        exit 0
      fi
      sleep 1
    done
  ) &
fi

# 前台執行 uvicorn：Ctrl+C 會直接停掉服務（exec 取代本行程）。
exec uv run uvicorn phyra_dualtrans.web.app:app \
  --host "$HOST" --port "$PORT"
