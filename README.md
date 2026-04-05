# claude-code-memory

Give Claude Code persistent memory across conversations.

## The Problem

Every time you start a new Claude Code conversation, it forgets everything. Your decisions, your project context, your debugging breakthroughs — all gone. Claude Code's built-in memory (`CLAUDE.md`) is manual and limited. There's no automatic way to carry context forward.

## The Solution

A lightweight memory system that runs alongside Claude Code. No external services, no databases, no API keys. Just a Python script, a cron job, and a few rules in your `CLAUDE.md`.

```
You (conversation) ──→ inbox.md (one-line notes)
                            ↓
Claude Code transcripts ──→ daily-journal.sh (nightly cron)
(~/.claude/projects/*.jsonl)    ↓
                          memory/2026-04-05.md (daily log)
                                ↓
                          MEMORY.md (long-term, manually curated)
                                ↓
                          CLAUDE.md reads memory/ on startup ←── next conversation
```

**How it works:**

1. **During conversation**: Claude writes one-line notes to `memory/inbox.md` when something important happens
2. **Every night**: A cron job extracts your conversation transcripts + inbox entries into a daily log (`memory/YYYY-MM-DD.md`)
3. **Next conversation**: Claude reads the last 2 days of logs on startup, picking up right where you left off

## Quick Start (2 minutes)

```bash
# Clone
git clone https://github.com/Sunnyztj/claude-code-memory.git
cd claude-code-memory

# Install
./setup.sh ~/projects/memory

# Add memory rules to your CLAUDE.md
cat templates/claude-md-memory-rules.md >> ~/projects/CLAUDE.md

# Set up nightly cron (adjust time to your timezone)
crontab -e
# Add: 30 23 * * * ~/projects/memory/scripts/daily-journal.sh ~/projects/memory
```

That's it. Start a new Claude Code conversation and it will read your recent memory on startup.

## What Gets Remembered

Claude automatically captures to `memory/inbox.md`:
- Decisions you made ("decided to use PostgreSQL instead of MongoDB")
- Credentials and config ("new API key for Stripe: sk_live_...")
- Project milestones ("deployed v2.1 to production")
- Lessons learned ("Docker COPY defaults to root:600, need chmod for non-root")
- Architecture choices ("using NullClient pattern for optional integrations")

Format is dead simple — one line per entry:
```
- [2026-04-05] Decided to split the monolith into 3 services
- [2026-04-05] VPS-3 IP changed to 103.249.239.174
- [2026-04-05] Walk-forward validation is the only trustworthy backtest method
```

## How the Transcript Extractor Works

Claude Code saves full conversation history as JSONL files at:
```
~/.claude/projects/{project-hash}/{session-id}.jsonl
```

The `extract-transcript.py` script:
- **Auto-detects** your Claude Code transcript directory (no config needed)
- **Incremental processing** — tracks byte offsets per session file, only extracts new content
- **Smart truncation** — skips skill expansions and tool outputs, keeps user/assistant messages
- **Size-limited** — output capped at 8KB to avoid overwhelming the daily log
- **Zero dependencies** — Python stdlib only, works with Python 3.8+

## File Structure

After setup, your project looks like:
```
~/projects/
├── CLAUDE.md                    # Your project config (add memory rules here)
├── MEMORY.md                    # Long-term memory (manually curated)
└── memory/
    ├── inbox.md                 # Real-time capture (one-line entries)
    ├── 2026-04-05.md            # Daily log (auto-generated)
    ├── 2026-04-04.md            # Yesterday's log
    ├── .journal-state.json      # Incremental processing state
    └── scripts/
        ├── extract-transcript.py  # JSONL transcript extractor
        └── daily-journal.sh       # Nightly cron script
```

## Advanced: ClaudeClaw Integration

If you use [ClaudeClaw](https://github.com/moazbuilds/ClaudeClaw) (daemon mode for Claude Code), you can use its built-in cron instead of system crontab:

```bash
cp templates/claudeclaw-jobs/*.md .claude/claudeclaw/jobs/
```

This gives you:
- `daily-journal` — runs nightly, generates daily logs
- `weekly-memory` — runs Sunday night, promotes stable facts to MEMORY.md

## Advanced: Multi-Instance Coordination

Running multiple AI instances (e.g., Claude Code + ChatGPT)? See [openclaw-to-claudeclaw](https://github.com/Sunnyztj/openclaw-to-claudeclaw) for:
- **Intercom** — async communication channel between AI instances
- **Anti-loop rules** — prevents infinite bot-to-bot conversations
- **Soul Transfer** — migrate AI personality/identity between platforms

## Design Decisions

| Decision | Why |
|----------|-----|
| File-based, not database | Portable, git-friendly, works offline, Claude can read/write directly |
| Inbox pattern | Low overhead — one line, no structure. Reduces friction to near zero |
| JSONL extraction | Claude Code already saves everything. Mine it nightly instead of duplicating |
| Byte offset tracking | Don't re-process old conversations. Only new content gets extracted |
| Cron, not in-process | Works with any Claude Code setup. No plugins, no daemon, no dependencies |
| Manual MEMORY.md curation | Protects long-term memory from noise. Only stable facts survive |

## Requirements

- Claude Code (any version)
- Python 3.8+ (no external packages)
- cron (or ClaudeClaw for daemon-based scheduling)

## FAQ

**Q: Does this work without ClaudeClaw?**
Yes. ClaudeClaw is entirely optional. The core system is just a Python script + cron + CLAUDE.md rules.

**Q: Will this slow down Claude Code?**
No. The transcript extraction runs as a separate cron job, not during your conversation. The only in-conversation cost is ~50 tokens every 15-20 turns for an inbox checkpoint.

**Q: How much disk space does this use?**
Daily logs are typically 2-5KB each. A year of daily logs is under 2MB.

**Q: Can I use this with multiple projects?**
Yes. Set up a separate memory directory per project, or use one shared directory. The script auto-detects transcripts regardless.

## License

MIT

## Credits

Born from a real production setup that's been running daily since April 2026. For the full story behind this system, see [openclaw-to-claudeclaw](https://github.com/Sunnyztj/openclaw-to-claudeclaw).
