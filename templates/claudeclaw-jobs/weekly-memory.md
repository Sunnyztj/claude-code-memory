---
schedule: "20 14 * * 0"
---
Execute weekly memory consolidation.

## Rules
- **Only write long-term stable information** to MEMORY.md
- Long-term = facts that won't expire within a week (account balances, architecture decisions, lessons learned)
- Temporary information (meetings, bug fixes) does NOT go into MEMORY.md

## Steps

### 1. Read this week's daily logs
Read `~/projects/memory/` files from the last 7 days.

### 2. Find candidate-long-term entries
Collect all entries tagged with `[candidate-long-term]`.

### 3. Read current MEMORY.md
Read `~/projects/MEMORY.md`.

### 4. Update MEMORY.md
- New long-term info: append to appropriate section
- Expired info: delete or update
- Don't delete info you're unsure about

### 5. Report
Output: "Weekly memory update: added X, updated X, removed X".
