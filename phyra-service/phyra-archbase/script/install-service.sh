#!/usr/bin/env bash
# phyra-archbase — 安裝 systemd user service，讓 HTTP 服務開機自動跑、登出後也活著。
# 預設埠 8037；換埠：PORT=9000 ./script/install-service.sh
#
# 服務由 script/server.py 提供（靜態瀏覽 + 標籤/刪除 API）。要啟用「刪除」功能，
# 安裝時帶入管理員密碼，會寫進 unit 的 Environment=：
#   PHYRA_ARCHBASE_ADMIN_PASSWORD='choose-a-secret' ./script/install-service.sh

set -euo pipefail

PORT="${PORT:-8037}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
UNIT="$UNIT_DIR/phyra-archbase.service"

PW_LINE=""
if [ -n "${PHYRA_ARCHBASE_ADMIN_PASSWORD:-}" ]; then
  PW_LINE="Environment=PHYRA_ARCHBASE_ADMIN_PASSWORD=${PHYRA_ARCHBASE_ADMIN_PASSWORD}"
fi

mkdir -p "$UNIT_DIR"
cat > "$UNIT" <<EOF
[Unit]
Description=phyra-archbase local HTTP server
After=network.target

[Service]
WorkingDirectory=$ROOT
Environment=PORT=$PORT
Environment=HOST=0.0.0.0
$PW_LINE
ExecStart=/usr/bin/python3 $ROOT/script/server.py
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now phyra-archbase.service

echo "Installed $UNIT"
echo
echo "狀態："
systemctl --user --no-pager status phyra-archbase.service | head -n 5 || true
echo
echo "本機可用內網 URL："
for ip in $(hostname -I); do
  echo "  http://$ip:$PORT/"
done
echo
echo "登出後仍要持續：sudo loginctl enable-linger $USER"
echo "停止：           systemctl --user stop phyra-archbase"
echo "重啟：           systemctl --user restart phyra-archbase"
echo "解除安裝：       systemctl --user disable --now phyra-archbase && rm '$UNIT'"
