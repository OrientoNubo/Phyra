#!/usr/bin/env bash
# phyra-dualtrans — 一次性下載 BabelDOC 模型 + SourceHan CJK 字型（約 340MB），
# 並驗證字型是否就緒。第一次使用前跑一次即可。

set -euo pipefail

echo "Running babeldoc --warmup (one-time, ~340MB) ..."
uv run --python 3.12 --with babeldoc==0.5.24 babeldoc --warmup || \
  uv tool run babeldoc --warmup

FONT_DIR="$HOME/.cache/babeldoc/fonts"
echo
echo "SourceHan Serif fonts in $FONT_DIR:"
ok=1
for f in SourceHanSerifTW-Regular.ttf SourceHanSerifHK-Regular.ttf \
         SourceHanSerifCN-Regular.ttf SourceHanSerifJP-Regular.ttf \
         SourceHanSerifKR-Regular.ttf; do
  if [ -f "$FONT_DIR/$f" ]; then
    echo "  ✓ $f"
  else
    echo "  ✗ $f  (missing)"
    ok=0
  fi
done
[ "$ok" = 1 ] && echo "warmup OK" || { echo "warmup INCOMPLETE"; exit 1; }
