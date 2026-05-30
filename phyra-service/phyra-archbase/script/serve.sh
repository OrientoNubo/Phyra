#!/usr/bin/env bash
# phyra-archbase — 啟動本機 HTTP 服務（前台、單次手動）
# 內網其他人開 http://<本機IP>:8037/ 即可瀏覽。Ctrl+C 結束。
# 換埠：PORT=9000 ./script/serve.sh
#
# 服務由 script/server.py 提供（純 stdlib）：靜態瀏覽 + 標籤/刪除 API。
#   • 標籤可自由編輯（免密碼）。
#   • 刪除論文需管理員密碼，啟動時用環境變數帶入（未設則刪除停用）：
#       PHYRA_ARCHBASE_ADMIN_PASSWORD='choose-a-secret' ./script/serve.sh

set -euo pipefail

PORT="${PORT:-8037}"
HOST="${HOST:-0.0.0.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Serving $ROOT on $HOST:$PORT"
echo "本機可用內網 URL："
for ip in $(hostname -I); do
  echo "  http://$ip:$PORT/"
done
echo

cd "$ROOT"
exec env PORT="$PORT" HOST="$HOST" python3 "$ROOT/script/server.py"
