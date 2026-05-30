#!/usr/bin/env bash
# phyra-dualtrans — 安裝 systemd user service，開機自動跑、登出後也活著。
# 預設埠 8000；換埠：PORT=9000 ./scripts/install-service.sh

set -euo pipefail

PORT="${PORT:-8000}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UV_BIN="$(command -v uv)"
UNIT_DIR="$HOME/.config/systemd/user"
UNIT="$UNIT_DIR/phyra-dualtrans.service"

mkdir -p "$UNIT_DIR"
cat > "$UNIT" <<EOF
[Unit]
Description=phyra-dualtrans local WebUI server
After=network.target

[Service]
WorkingDirectory=$ROOT
Environment=PORT=$PORT
ExecStart=$UV_BIN run uvicorn phyra_dualtrans.web.app:app --host 0.0.0.0 --port $PORT
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now phyra-dualtrans.service

echo "Installed $UNIT"
echo
echo "狀態："
systemctl --user --no-pager status phyra-dualtrans.service | head -n 5 || true
echo
echo "本機可用內網 URL："
for ip in $(hostname -I); do
  echo "  http://$ip:$PORT/"
done
echo
echo "登出後仍要持續：sudo loginctl enable-linger $USER"
echo "停止：           systemctl --user stop phyra-dualtrans"
echo "重啟：           systemctl --user restart phyra-dualtrans"
echo "解除安裝：       systemctl --user disable --now phyra-dualtrans && rm '$UNIT'"
