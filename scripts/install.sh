#!/usr/bin/env bash
#
# Phyra Academic Research Plugin - Installation Script
# Installs Phyra skills, agents, commands, examples, and assets
# into the user's ~/.claude/ and ~/.phyra/ directories.
#
# Usage:
#   ./scripts/install.sh            # interactive install
#   ./scripts/install.sh --update   # overwrite existing phyra files
#
set -euo pipefail

# --- Resolve project root ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

CLAUDE_HOME="$HOME/.claude"
PHYRA_HOME="$HOME/.phyra"
UPDATE=false

if [[ "${1:-}" == "--update" ]]; then
    UPDATE=true
fi

# --- Verify source directory exists ---
if [[ ! -d "$SRC_DIR" ]]; then
    echo "Error: source directory not found at $SRC_DIR"
    exit 1
fi

# --- Check for existing phyra files ---
existing_count=0
for dir in skills agents commands; do
    if [[ -d "$CLAUDE_HOME/$dir" ]]; then
        count=$(find "$CLAUDE_HOME/$dir" -maxdepth 1 -name 'phyra-*' 2>/dev/null | wc -l)
        existing_count=$((existing_count + count))
    fi
done

if [[ $existing_count -gt 0 && "$UPDATE" == false ]]; then
    echo "Found $existing_count existing Phyra items in ~/.claude/."
    read -rp "Overwrite them? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# --- Create target directories ---
mkdir -p "$CLAUDE_HOME/skills"
mkdir -p "$CLAUDE_HOME/agents"
mkdir -p "$CLAUDE_HOME/commands"
mkdir -p "$PHYRA_HOME/docs"
mkdir -p "$PHYRA_HOME/examples"
mkdir -p "$PHYRA_HOME/assets"

installed=0

# --- Skills (preserve directory structure) ---
for skill_dir in "$SRC_DIR"/skills/phyra-*; do
    [[ -d "$skill_dir" ]] || continue
    cp -r "$skill_dir" "$CLAUDE_HOME/skills/"
    installed=$((installed + 1))
    echo "  skill: $(basename "$skill_dir")/"
done

# --- Agents ---
for agent in "$SRC_DIR"/agents/phyra-*.md; do
    [[ -f "$agent" ]] || continue
    cp "$agent" "$CLAUDE_HOME/agents/"
    installed=$((installed + 1))
    echo "  agent: $(basename "$agent")"
done

# --- Commands ---
for cmd in "$SRC_DIR"/commands/phyra-*.md; do
    [[ -f "$cmd" ]] || continue
    cp "$cmd" "$CLAUDE_HOME/commands/"
    installed=$((installed + 1))
    echo "  command: $(basename "$cmd")"
done

# --- Support docs ---
for doc in "$SRC_DIR"/support/*.md; do
    [[ -f "$doc" ]] || continue
    cp "$doc" "$PHYRA_HOME/docs/"
    installed=$((installed + 1))
    echo "  doc: $(basename "$doc")"
done

# --- Examples ---
for ex in "$SRC_DIR"/examples/*; do
    [[ -f "$ex" ]] || continue
    cp "$ex" "$PHYRA_HOME/examples/"
    installed=$((installed + 1))
    echo "  example: $(basename "$ex")"
done

# --- Assets ---
for asset in "$SRC_DIR"/assets/*; do
    [[ -f "$asset" ]] || continue
    cp "$asset" "$PHYRA_HOME/assets/"
    installed=$((installed + 1))
    echo "  asset: $(basename "$asset")"
done

echo ""
echo "Installed $installed items."

# --- Agent Teams config ---
SETTINGS_FILE="$CLAUDE_HOME/settings.json"
echo ""
read -rp "Enable Agent Teams in ~/.claude/settings.json? [y/N] " enable_teams
if [[ "$enable_teams" =~ ^[Yy]$ ]]; then
    if [[ -f "$SETTINGS_FILE" ]]; then
        # Merge env key using a simple check
        if grep -q "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" "$SETTINGS_FILE" 2>/dev/null; then
            echo "Agent Teams config already present in settings.json."
        else
            # Use a temp file to merge via python/jq if available, otherwise manual
            if command -v jq &>/dev/null; then
                jq '.env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" \
                    && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
                echo "Added Agent Teams config to existing settings.json."
            else
                echo "Warning: jq not found. Please manually add to $SETTINGS_FILE:"
                echo '  { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }'
            fi
        fi
    else
        echo '{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }' > "$SETTINGS_FILE"
        echo "Created settings.json with Agent Teams config."
    fi
fi

echo ""
echo "Phyra installation complete."
