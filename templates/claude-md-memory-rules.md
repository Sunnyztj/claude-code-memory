## Memory System

> Add this section to your project's CLAUDE.md to enable persistent memory.

### On Startup (every new conversation)
1. Read this file
2. Read `memory/` directory for the last 2 days of logs
3. Read `memory/inbox.md` for pending items

### Real-time Capture
When you learn something worth remembering during conversation, write one line to `memory/inbox.md`:
```
- [YYYY-MM-DD] content
```

What to capture:
- Important decisions made by the user
- Account credentials, API keys, balances
- Project status changes (deployed, launched, broke)
- New clients, requirements, deadlines
- Lessons learned, gotchas, workarounds

### Periodic Checkpoint
Every 15-20 conversation turns, check if you have unwritten insights.
If yes, write to `memory/inbox.md`. This prevents memory loss when context compresses.

### End-of-Conversation Check
When the conversation is ending (user says goodbye, long silence, topic switch):
- Quick self-check: anything worth remembering today?
- If yes, confirm it's written to inbox.md
- One line is enough — the daily journal handles the rest

### How It Works (automatic, no action needed)
- **Nightly**: `daily-journal.sh` reads your conversation transcripts + inbox entries, generates `memory/YYYY-MM-DD.md`
- **Inbox**: Processed entries are cleared after journaling
- **Long-term**: Manually promote stable facts from daily logs to MEMORY.md
