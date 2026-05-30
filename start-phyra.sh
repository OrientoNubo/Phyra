#!/usr/bin/env bash
# Phyra Center — back-compat shim.
#
# The real start script now lives at:
#     phyra-service/phyra-center/script/start.sh
# This wrapper exists only so old habits / muscle-memory / cron jobs that
# still call `./start-phyra.sh` keep working. It forwards every env var
# and argument unchanged.
#
# 一鍵啟動主頁 + 翻譯 + 論文庫 + 模型服務 — 詳細用法見：
#     phyra-service/phyra-center/README.md
#     phyra-service/phyra-center/script/start.sh （頂端的環境變數註解）

set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/phyra-service/phyra-center/script/start.sh" "$@"
