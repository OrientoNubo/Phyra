#!/usr/bin/env bash
#
# Phyra Academic Research Plugin - Uninstall Script
# Removes all phyra-prefixed items from ~/.claude/ and ~/.phyra/ data dirs.
# Does NOT remove user-created files or Agent Teams config from settings.json.
#
set -euo pipefail

CLAUDE_HOME="$HOME/.claude"
PHYRA_HOME="$HOME/.phyra"
removed=0

# --- Remove phyra- prefixed items from ~/.claude/ ---
for dir in skills agents commands; do
    target="$CLAUDE_HOME/$dir"
    [[ -d "$target" ]] || continue
    for item in "$target"/phyra-*; do
        [[ -e "$item" ]] || continue
        rm -rf "$item"
        removed=$((removed + 1))
        echo "  removed: $dir/$(basename "$item")"
    done
done

# --- Remove ~/.phyra/docs/ ---
if [[ -d "$PHYRA_HOME/docs" ]]; then
    count=$(find "$PHYRA_HOME/docs" -type f 2>/dev/null | wc -l)
    rm -rf "$PHYRA_HOME/docs"
    removed=$((removed + count))
    echo "  removed: ~/.phyra/docs/"
fi

# --- Remove ~/.phyra/examples/ ---
if [[ -d "$PHYRA_HOME/examples" ]]; then
    count=$(find "$PHYRA_HOME/examples" -type f 2>/dev/null | wc -l)
    rm -rf "$PHYRA_HOME/examples"
    removed=$((removed + count))
    echo "  removed: ~/.phyra/examples/"
fi

# --- Remove ~/.phyra/assets/ ---
if [[ -d "$PHYRA_HOME/assets" ]]; then
    count=$(find "$PHYRA_HOME/assets" -type f 2>/dev/null | wc -l)
    rm -rf "$PHYRA_HOME/assets"
    removed=$((removed + count))
    echo "  removed: ~/.phyra/assets/"
fi

echo ""
echo "Removed $removed items."
echo "Note: Agent Teams config in ~/.claude/settings.json was not modified."
echo "Phyra uninstall complete."
