# Reddit Post Draft

**Subreddit:** r/ClaudeAI

**Title:** I built a persistent memory system for Claude Code (no plugins, no API keys, 2-min setup)

**Body:**

Claude Code's biggest pain point for me was losing context between conversations. Every new session, I'd spend the first 5 minutes re-explaining my project setup, architecture decisions, and what I did yesterday. CLAUDE.md helps, but manually maintaining it doesn't scale.

So I built a simple memory system that runs alongside Claude Code. It's been running in my production workflow daily and the difference is night and day — yesterday Claude referenced a Docker gotcha I hit 3 days ago ("COPY defaults to root:600, need chmod for non-root users") without me mentioning it. It just *knew*.

**How it works:**

1. During conversation, Claude writes one-line notes to `memory/inbox.md` (important decisions, credentials, lessons learned)
2. A nightly cron job extracts your conversation transcripts (Claude Code saves these as JSONL files at `~/.claude/projects/`) and combines them with inbox entries into a daily log
3. Next conversation, Claude reads the last 2 days of logs on startup via CLAUDE.md rules

That's it. No database, no external service, no API keys. Just a Python script (stdlib only), a shell script for cron, and a few rules in your CLAUDE.md.

**Setup is literally:**

```bash
git clone https://github.com/Sunnyztj/claude-code-memory.git
cd claude-code-memory
./setup.sh ~/projects/memory
# Add the memory rules to your CLAUDE.md
# Set up a nightly cron job
```

**What gets remembered automatically:**

- Architecture decisions ("switched from MongoDB to PostgreSQL")
- Deployment details ("VPS IP changed, new Nginx config")
- Lessons learned ("Docker COPY defaults to root:600, chmod needed")
- Account info, API keys, project milestones

**Key design decisions:**

- File-based (not a database) — Claude can read/write directly, git-friendly, works offline
- Inbox pattern — one line per entry, zero friction to capture
- Incremental JSONL extraction — tracks byte offsets, never re-processes old conversations
- Cron-based (not in-process) — works with vanilla Claude Code, no plugins needed

Works with any Claude Code setup. If you use ClaudeClaw (daemon mode), there are optional cron job templates included.

GitHub: https://github.com/Sunnyztj/claude-code-memory

Happy to answer questions. If you're curious about the backstory — this came out of a setup where I run two AI instances that share memory. The multi-instance coordination stuff is in a [separate repo](https://github.com/Sunnyztj/openclaw-to-claudeclaw).

**Pro tip:** Attach a screenshot of an actual `memory/2026-04-05.md` daily log when posting, so people can see what the output looks like.
