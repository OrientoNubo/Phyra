#!/usr/bin/env bash
# Phyra Center — 一鍵啟動三條服務（主頁 + 翻譯 + 論文庫）。
#
# 同時拉起三個 WebUI，並在 Ctrl+C 時一起乾淨收掉：
#   • phyra-center     主頁 / 入口     預設 :8035
#   • phyra-archbase   論文庫瀏覽       預設 :8037（啟動前自動重生首頁）
#   • phyra-dualtrans  翻譯服務         預設 :8039
#
# 三條的輸出寫到 .logs/ 並即時 tail 出來（行首標明來源）。
#
# 環境變數：
#   CT_PORT=8035     主頁埠（烘焙進 archbase / dualtrans 的「返回 Center」banner）
#   AB_PORT=8037     論文庫埠
#   DT_PORT=8039     翻譯服務埠
#   HOST=0.0.0.0     綁定位址（127.0.0.1 = 只給本機）
#   NO_BROWSER=1     不要自動開瀏覽器
#   PHYRA_ARCHBASE_ADMIN_PASSWORD=secret
#                    論文庫「刪除」功能的管理員密碼（未設＝刪除停用）；
#                    標籤可自由編輯，不需密碼。

set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"   # …/phyra-service/phyra-center
SVC_DIR="$(dirname "$HERE")"               # …/phyra-service（archbase / dualtrans 的同層父目錄）
CT_DIR="$HERE"
AB_DIR="$SVC_DIR/phyra-archbase"
DT_DIR="$SVC_DIR/phyra-dualtrans"

CT_PORT="${CT_PORT:-8035}"
AB_PORT="${AB_PORT:-8037}"
DT_PORT="${DT_PORT:-8039}"
HOST="${HOST:-0.0.0.0}"
LOG_DIR="$HERE/.logs"
mkdir -p "$LOG_DIR"

c() { printf '\033[1;36m▶ %s\033[0m\n' "$1"; }

[ -x "$CT_DIR/script/server.py" ] || { echo "找不到 $CT_DIR/script/server.py" >&2; exit 1; }
[ -x "$AB_DIR/script/serve.sh" ]  || { echo "找不到 $AB_DIR/script/serve.sh"  >&2; exit 1; }
[ -f "$DT_DIR/scripts/start.sh" ] || { echo "找不到 $DT_DIR/scripts/start.sh" >&2; exit 1; }

pids=()
cleanup() {
  trap - INT TERM EXIT
  echo
  c "停止 Phyra Center…"
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  wait 2>/dev/null || true
  c "已全部停止。"
}
trap cleanup INT TERM EXIT

# 1) 論文庫：先重生首頁（banner 烘焙 PHYRA_CENTER_PORT），再啟動 ───────────
c "重生 phyra-archbase 首頁（banner ← :$CT_PORT）"
PHYRA_CENTER_PORT="$CT_PORT" python3 "$AB_DIR/script/generate_index.py"

c "啟動 phyra-archbase（:$AB_PORT）"
# 透傳 PHYRA_CENTER_PORT：server.py 刪論文後會就地重生首頁，banner port 需一致。
# PHYRA_ARCHBASE_ADMIN_PASSWORD 若有設亦會被繼承。
PORT="$AB_PORT" HOST="$HOST" PHYRA_CENTER_PORT="$CT_PORT" \
  bash "$AB_DIR/script/serve.sh" >"$LOG_DIR/archbase.log" 2>&1 &
pids+=($!)

# 2) 翻譯服務：背景跑；瀏覽器交給本腳本統一開（避免各開分頁） ────────────
c "啟動 phyra-dualtrans（:$DT_PORT；首次會下載 ~340MB 模型）"
PORT="$DT_PORT" HOST="$HOST" NO_BROWSER=1 \
  PHYRA_DUALTRANS_ARCHBASE_PORT="$AB_PORT" \
  PHYRA_DUALTRANS_CENTER_PORT="$CT_PORT" \
  bash "$DT_DIR/scripts/start.sh" >"$LOG_DIR/dualtrans.log" 2>&1 &
pids+=($!)

# 3) Center 主頁：純 stdlib，秒啟動 ─────────────────────────────────────
c "啟動 phyra-center（:$CT_PORT）"
PORT="$CT_PORT" HOST="$HOST" \
  PHYRA_ARCHBASE_PORT="$AB_PORT" PHYRA_DUALTRANS_PORT="$DT_PORT" \
  python3 "$CT_DIR/script/server.py" >"$LOG_DIR/center.log" 2>&1 &
pids+=($!)

# 即時輸出三邊 log
tail -n +1 -F "$LOG_DIR/center.log" "$LOG_DIR/archbase.log" "$LOG_DIR/dualtrans.log" &
pids+=($!)

# 服務就緒後開瀏覽器到 Center 主頁。等 Center /healthz 起來就開；
# dualtrans 可能還在拉 BabelDOC 模型，但 Center 永遠秒起，所以以 Center 為準。
if [ "${NO_BROWSER:-0}" != "1" ]; then
  (
    for _ in $(seq 1 60); do
      if curl -fsS "http://localhost:$CT_PORT/healthz" >/dev/null 2>&1; then
        url="http://localhost:$CT_PORT/"
        for opener in xdg-open open "${BROWSER:-}"; do
          [ -n "$opener" ] && command -v "$opener" >/dev/null 2>&1 \
            && { "$opener" "$url" >/dev/null 2>&1 & break; }
        done
        exit 0
      fi
      sleep 1
    done
  ) &
  pids+=($!)
fi

echo
c "Phyra Center 啟動中"
printf '  主頁：             http://localhost:%s/\n' "$CT_PORT"
printf '  論文庫：           http://localhost:%s/\n' "$AB_PORT"
printf '  翻譯服務：         http://localhost:%s/\n' "$DT_PORT"
if [ "$HOST" = "0.0.0.0" ]; then
  for ip in $(hostname -I 2>/dev/null || true); do
    printf '  內網：             http://%s:%s/  (Center)\n' "$ip" "$CT_PORT"
  done
fi
printf '  logs：             %s/{center,archbase,dualtrans}.log\n' "$LOG_DIR"
printf '  （Ctrl+C 一次停掉全部）\n\n'

wait
