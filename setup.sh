#!/usr/bin/env bash
set -euo pipefail

# claude-code-memory setup
# Installs persistent memory for Claude Code in under 2 minutes.

MEMORY_DIR="${1:-$HOME/projects/memory}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  Claude Code Memory — Setup"
echo "  ==========================="
echo ""
echo "  Memory directory: $MEMORY_DIR"
echo ""

# ── Create memory directory ──────────────────────────────

mkdir -p "$MEMORY_DIR/scripts"
echo "  [1/5] Created $MEMORY_DIR"

# ── Copy scripts ─────────────────────────────────────────

cp "$SCRIPT_DIR/scripts/extract-transcript.py" "$MEMORY_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/daily-journal.sh" "$MEMORY_DIR/scripts/"
chmod +x "$MEMORY_DIR/scripts/daily-journal.sh"
echo "  [2/5] Installed scripts"

# ── Create templates ─────────────────────────────────────

if [[ ! -f "$MEMORY_DIR/inbox.md" ]]; then
    cp "$SCRIPT_DIR/templates/inbox.md" "$MEMORY_DIR/inbox.md"
    echo "  [3/5] Created inbox.md"
else
    echo "  [3/5] inbox.md already exists, skipping"
fi

if [[ ! -f "$MEMORY_DIR/.journal-state.json" ]]; then
    cp "$SCRIPT_DIR/templates/.journal-state.json" "$MEMORY_DIR/.journal-state.json"
    echo "  [4/5] Created .journal-state.json"
else
    echo "  [4/5] .journal-state.json already exists, skipping"
fi

# ── Show CLAUDE.md instructions ──────────────────────────

CLAUDE_MD_PATH=""
# Find project CLAUDE.md
if [[ -f "$HOME/projects/CLAUDE.md" ]]; then
    CLAUDE_MD_PATH="$HOME/projects/CLAUDE.md"
elif [[ -f "$(pwd)/CLAUDE.md" ]]; then
    CLAUDE_MD_PATH="$(pwd)/CLAUDE.md"
fi

echo "  [5/5] Setup complete!"
echo ""
echo "  ==========================="
echo ""
echo "  Next steps:"
echo ""
echo "  1. Add memory rules to your CLAUDE.md:"
echo "     cat $SCRIPT_DIR/templates/claude-md-memory-rules.md"
echo ""
echo "  2. Set up nightly cron (adjust time to your timezone):"
echo "     crontab -e"
echo "     # Add this line (runs at 11:30 PM):"
echo "     30 23 * * * $MEMORY_DIR/scripts/daily-journal.sh $MEMORY_DIR"
echo ""
echo "  3. Start Claude Code and test:"
echo "     cd ~/projects && claude"
echo "     > Write something to memory/inbox.md"
echo ""
echo "  Optional: If you use ClaudeClaw, copy the job files instead of cron:"
echo "     cp $SCRIPT_DIR/templates/claudeclaw-jobs/*.md .claude/claudeclaw/jobs/"
echo ""
