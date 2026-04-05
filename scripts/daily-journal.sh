#!/usr/bin/env bash
set -euo pipefail

# Daily journal generator for Claude Code
# Extracts today's conversations and creates a daily log.
#
# Usage:
#   ./daily-journal.sh [memory-dir]
#
# Default memory-dir: ~/projects/memory
# Add to crontab: 0 23 * * * /path/to/daily-journal.sh

MEMORY_DIR="${1:-$HOME/projects/memory}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$MEMORY_DIR/$TODAY.md"
INBOX="$MEMORY_DIR/inbox.md"

echo "[daily-journal] Starting for $TODAY"

# Step 1: Extract new transcript content
TRANSCRIPT=""
if [[ -f "$SCRIPT_DIR/extract-transcript.py" ]]; then
    TRANSCRIPT=$(python3 "$SCRIPT_DIR/extract-transcript.py" 2>/dev/null) || true
fi

# Step 2: Read inbox
INBOX_CONTENT=""
if [[ -f "$INBOX" ]]; then
    # Get lines starting with "- [" (actual entries, skip headers)
    INBOX_CONTENT=$(grep '^- \[' "$INBOX" 2>/dev/null) || true
fi

# Step 3: Generate log if there's content
if [[ -z "$TRANSCRIPT" && -z "$INBOX_CONTENT" ]]; then
    echo "[daily-journal] Nothing new today. Skipping."
    exit 0
fi

# Create or append to daily log
{
    if [[ ! -f "$LOG_FILE" ]]; then
        echo "# $TODAY Log"
        echo ""
    fi

    if [[ -n "$TRANSCRIPT" ]]; then
        echo "## Conversation Summary"
        echo ""
        echo "$TRANSCRIPT"
        echo ""
    fi

    if [[ -n "$INBOX_CONTENT" ]]; then
        echo "## Inbox Entries"
        echo ""
        echo "$INBOX_CONTENT"
        echo ""
    fi
} >> "$LOG_FILE"

# Step 4: Clear processed inbox entries
if [[ -n "$INBOX_CONTENT" && -f "$INBOX" ]]; then
    # Keep only the header (lines not starting with "- [")
    grep -v '^- \[' "$INBOX" > "$INBOX.tmp" 2>/dev/null || true
    mv "$INBOX.tmp" "$INBOX"
fi

echo "[daily-journal] Done: $LOG_FILE"
