---
schedule: "0 14 * * *"
---
Execute daily memory consolidation.

## Steps

### 1. Run transcript extraction
```bash
python3 ~/projects/memory/scripts/extract-transcript.py
```

### 2. Read inbox
Read `~/projects/memory/inbox.md` and collect today's entries.

### 3. Generate daily log
Write to `~/projects/memory/YYYY-MM-DD.md` (today's date):

```markdown
# YYYY-MM-DD Log

## Key Points
- (3-5 most important items)

## Conversation Summary
(Distill from transcript — key decisions and actions only)

## Inbox Entries
(Moved from inbox.md)

## Tags
[candidate-long-term] (Tag stable facts suitable for MEMORY.md)
```

### 4. Clear inbox
Remove processed entries from inbox.md, keep the header.

### 5. Confirm
Output "Daily journal done: YYYY-MM-DD.md".

## Notes
- Adjust schedule to your timezone. Formula: `desired_local_hour - utc_offset = utc_hour`.
- Example: 23:30 in UTC+9:30 = 14:00 UTC → `0 14 * * *`.
