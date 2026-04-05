#!/usr/bin/env python3
"""
Extract user/assistant messages from Claude Code JSONL transcripts.
Outputs a compact summary suitable for feeding to a daily journal.

Usage:
    python3 extract-transcript.py

Auto-detects Claude Code transcript directory and state file location.
Processes incrementally using byte offsets — only new content is extracted.
Outputs to stdout. Max output size: 8KB.
No external dependencies — uses Python stdlib only.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

MAX_KB = 8


def detect_projects_dir():
    """Auto-detect the Claude Code projects directory."""
    claude_projects = Path.home() / ".claude" / "projects"
    if not claude_projects.exists():
        print(f"Error: {claude_projects} not found. Is Claude Code installed?", file=sys.stderr)
        sys.exit(1)
    candidates = []
    for d in claude_projects.iterdir():
        if d.is_dir() and list(d.glob("*.jsonl")):
            candidates.append((d, d.stat().st_mtime))
    if not candidates:
        print(f"Error: No JSONL transcripts found in {claude_projects}", file=sys.stderr)
        sys.exit(1)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def detect_state_file():
    """Find .journal-state.json relative to this script."""
    script_dir = Path(__file__).resolve().parent
    # Try: scripts/ → parent (memory dir)
    state = script_dir.parent / ".journal-state.json"
    if state.exists():
        return state
    # Try: same directory as script
    state = script_dir / ".journal-state.json"
    if state.exists():
        return state
    # Create in parent directory
    return script_dir.parent / ".journal-state.json"


def load_state(state_file):
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {"lastProcessed": {"timestamp": "1970-01-01T00:00:00Z", "sessionFiles": {}}}


def save_state(state_file, state):
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def find_session_files(projects_dir):
    """Find all .jsonl files (top-level only, skip subagent dirs)."""
    return sorted(projects_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)


def extract_messages(filepath, byte_offset=0):
    """Extract user/assistant text messages starting at byte_offset."""
    messages = []
    new_offset = byte_offset

    with open(filepath, "rb") as f:
        f.seek(byte_offset)
        for line in f:
            new_offset = f.tell()
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = obj.get("type")
            timestamp = obj.get("timestamp", "")

            if msg_type == "user":
                content = obj.get("message", {}).get("content", "")
                text = ""
                if isinstance(content, str):
                    if "<command-name>" in content or len(content) > 500:
                        text = content[:150] + "..." if len(content) > 150 else content
                    else:
                        text = content
                elif isinstance(content, list):
                    for c in content:
                        if c.get("type") == "text":
                            t = c["text"]
                            if len(t) > 500:
                                t = t[:150] + "..."
                            text = t
                            break
                if text.strip():
                    messages.append({"role": "user", "text": text.strip(), "ts": timestamp})

            elif msg_type == "assistant":
                content = obj.get("message", {}).get("content", [])
                texts = []
                if isinstance(content, list):
                    for c in content:
                        if c.get("type") == "text" and c.get("text", "").strip():
                            texts.append(c["text"].strip())
                elif isinstance(content, str) and content.strip():
                    texts.append(content.strip())
                if texts:
                    full = "\n".join(texts)
                    if len(full) > 300:
                        full = full[:300] + "..."
                    messages.append({"role": "assistant", "text": full, "ts": timestamp})

    return messages, new_offset


def format_output(all_messages):
    """Format messages into a compact summary."""
    if not all_messages:
        return ""

    lines = [f"# Conversation Summary — {datetime.now().strftime('%Y-%m-%d')}", ""]

    for msg in all_messages:
        ts = msg.get("ts", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M")
            except (ValueError, TypeError):
                time_str = "??:??"
        else:
            time_str = "??:??"

        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"**[{time_str}] {role}**: {msg['text']}")
        lines.append("")

    output = "\n".join(lines)

    max_bytes = MAX_KB * 1024
    if len(output.encode("utf-8")) > max_bytes:
        out_lines = output.split("\n")
        truncated = []
        size = 0
        for line in out_lines:
            line_size = len((line + "\n").encode("utf-8"))
            if size + line_size > max_bytes:
                break
            truncated.append(line)
            size += line_size
        output = "\n".join(truncated)
        output += "\n\n... (truncated to fit size limit)"

    return output


def main():
    projects_dir = detect_projects_dir()
    state_file = detect_state_file()
    state = load_state(state_file)
    session_offsets = state["lastProcessed"].get("sessionFiles", {})

    all_messages = []
    new_offsets = {}

    for filepath in find_session_files(projects_dir):
        fname = filepath.name
        offset = session_offsets.get(fname, 0)

        if filepath.stat().st_size <= offset:
            new_offsets[fname] = offset
            continue

        messages, new_offset = extract_messages(filepath, offset)
        all_messages.extend(messages)
        new_offsets[fname] = new_offset

    if all_messages:
        all_messages.sort(key=lambda m: m.get("ts", ""))
        print(format_output(all_messages))

    state["lastProcessed"]["timestamp"] = datetime.now(timezone.utc).isoformat()
    state["lastProcessed"]["sessionFiles"] = new_offsets
    save_state(state_file, state)

    print(f"\n--- Processed {len(all_messages)} new messages from {len(new_offsets)} session(s) ---", file=sys.stderr)


if __name__ == "__main__":
    main()
