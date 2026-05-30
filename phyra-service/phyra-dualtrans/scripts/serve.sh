#!/usr/bin/env bash
# phyra-dualtrans — 啟動本機 WebUI 服務（前台、單次手動）。Ctrl+C 結束。
# 內網其他人開 http://<本機IP>:8000/ 即可使用。換埠：PORT=9000 ./scripts/serve.sh

set -euo pipefail

PORT="${PORT:-8000}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Serving phyra-dualtrans from $ROOT on 0.0.0.0:$PORT"
echo "本機可用內網 URL："
for ip in $(hostname -I); do
  echo "  http://$ip:$PORT/"
done
echo

cd "$ROOT"
exec uv run uvicorn phyra_dualtrans.web.app:app --host 0.0.0.0 --port "$PORT"
