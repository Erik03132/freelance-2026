#!/usr/bin/env python3
"""
Antigravity → AI Engineering Coach adapter.

Converts Antigravity transcript.jsonl files to Claude JSONL format
so that the AI Engineering Coach VS Code extension can analyse them.

Output layout (mirrors Claude Code):
  ~/.claude/projects/antigravity-<workspace>/<conv-id>.jsonl

Usage:
  python3 tools/antigravity_to_coach.py            # convert all
  python3 tools/antigravity_to_coach.py --dry-run  # just print stats
  python3 tools/antigravity_to_coach.py --id <conv-id>  # one session
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
HOME            = Path.home()
BRAIN_DIR       = HOME / ".gemini" / "antigravity" / "brain"
CLAUDE_PROJECTS = HOME / ".claude" / "projects"
WORKSPACE_NAME  = "freelance-2026"          # shown in Coach UI
PROJECT_KEY     = f"antigravity-{WORKSPACE_NAME.replace('/', '-')}"
WORKSPACE_PATH  = str(HOME / "freelance-2026")

# ── Helpers ────────────────────────────────────────────────────────────────

def clean_user_text(raw: str) -> str:
    """Strip wrapper tags added by Antigravity."""
    text = re.sub(r"<USER_REQUEST>\s*", "", raw)
    text = re.sub(r"\s*</USER_REQUEST>", "", text)
    text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
    return text.strip()


def iso_to_ms(ts: str | None) -> int | None:
    """Convert ISO-8601 timestamp to Unix milliseconds."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except Exception:
        return None


def make_tool_use_block(tc: dict) -> dict:
    """Convert Antigravity tool_call to Claude tool_use content block."""
    args = tc.get("args", {})
    # Antigravity sometimes JSON-encodes args as strings
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"raw": args}
    return {
        "type": "tool_use",
        "name": tc.get("name", "unknown"),
        "input": args,
    }


def extract_edited_files(tool_calls: list[dict]) -> list[str]:
    write_tools = {"write_to_file", "replace_file_content", "multi_replace_file_content"}
    files = []
    for tc in tool_calls:
        if tc.get("name") in write_tools:
            args = tc.get("args", {})
            if isinstance(args, dict):
                f = args.get("TargetFile") or args.get("target_file")
                if f:
                    files.append(str(f).strip('"'))
    return files


def extract_referenced_files(tool_calls: list[dict]) -> list[str]:
    read_tools = {"view_file", "grep_search", "list_dir"}
    files = []
    for tc in tool_calls:
        if tc.get("name") in read_tools:
            args = tc.get("args", {})
            if isinstance(args, dict):
                f = args.get("AbsolutePath") or args.get("SearchPath") or args.get("DirectoryPath")
                if f:
                    files.append(str(f).strip('"'))
    return files


def extract_tools_used(tool_calls: list[dict]) -> list[str]:
    return [tc.get("name", "") for tc in tool_calls if tc.get("name")]


def guess_workspace_from_transcript(steps: list[dict]) -> str:
    """Try to extract workspace path from Cwd args in tool_calls."""
    for step in steps:
        for tc in step.get("tool_calls", []):
            args = tc.get("args", {})
            if isinstance(args, dict):
                cwd = args.get("Cwd") or args.get("cwd")
                if cwd:
                    cwd = str(cwd).strip('"')
                    if "freelance-2026" in cwd:
                        return "freelance-2026"
    return WORKSPACE_NAME


# ── Core converter ─────────────────────────────────────────────────────────

def convert_transcript(conv_id: str, transcript_path: Path) -> list[dict] | None:
    """
    Convert one Antigravity transcript.jsonl → list of Claude JSONL lines.
    Returns None if the file is empty or has no user/model turns.
    """
    steps: list[dict] = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    steps.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except OSError:
        return None

    if not steps:
        return None

    ws_name = guess_workspace_from_transcript(steps)
    claude_lines: list[dict] = []
    step_uuid_map: dict[int, str] = {}

    for step in steps:
        source = step.get("source", "")
        ts     = step.get("created_at")
        idx    = step.get("step_index", 0)
        step_uuid_map[idx] = str(uuid.uuid4())

        # ── User message ──────────────────────────────────────────────────
        if source == "USER_EXPLICIT" and step.get("type") == "USER_INPUT":
            raw_content = step.get("content", "")
            text = clean_user_text(raw_content)
            if not text:
                continue
            claude_lines.append({
                "type":      "user",
                "uuid":      step_uuid_map[idx],
                "sessionId": conv_id,
                "timestamp": ts,
                "cwd":       WORKSPACE_PATH,
                "entrypoint": "cli",
                "message": {
                    "role":    "user",
                    "content": text,
                },
            })

        # ── Model response ────────────────────────────────────────────────
        elif source == "MODEL" and step.get("type") == "PLANNER_RESPONSE":
            tool_calls   = step.get("tool_calls", []) or []
            response_text = step.get("content", "") or ""
            thinking      = step.get("thinking", "") or ""

            # Build content array (text + tool_use blocks)
            content_blocks: list[dict] = []
            if response_text:
                content_blocks.append({"type": "text", "text": response_text})
            elif thinking:
                content_blocks.append({"type": "text", "text": thinking[:500]})
            for tc in tool_calls:
                content_blocks.append(make_tool_use_block(tc))

            if not content_blocks:
                continue

            # Estimate tokens (rough: 4 chars ≈ 1 token)
            all_text = response_text + " ".join(
                json.dumps(tc.get("args", {})) for tc in tool_calls
            )
            out_tokens = max(1, len(all_text) // 4)

            parent_uuid = None
            if idx > 0 and (idx - 1) in step_uuid_map:
                parent_uuid = step_uuid_map[idx - 1]

            claude_lines.append({
                "type":       "assistant",
                "uuid":       step_uuid_map[idx],
                "parentUuid": parent_uuid,
                "sessionId":  conv_id,
                "timestamp":  ts,
                "message": {
                    "role":  "assistant",
                    "model": "gemini-2.5-flash-preview",
                    "content": content_blocks,
                    "usage": {
                        "input_tokens":  0,
                        "output_tokens": out_tokens,
                    },
                },
                # Extra metadata (not used by Claude parser but harmless)
                "_editedFiles":     extract_edited_files(tool_calls),
                "_referencedFiles": extract_referenced_files(tool_calls),
                "_toolsUsed":       extract_tools_used(tool_calls),
            })

    # Only keep sessions that have at least one user turn
    has_user = any(l.get("type") == "user" for l in claude_lines)
    return claude_lines if has_user else None


# ── Main ───────────────────────────────────────────────────────────────────

def run(dry_run: bool = False, filter_id: str | None = None) -> None:
    CLAUDE_PROJECTS.mkdir(parents=True, exist_ok=True)
    out_dir = CLAUDE_PROJECTS / PROJECT_KEY
    out_dir.mkdir(exist_ok=True)

    conv_dirs = sorted(BRAIN_DIR.iterdir()) if BRAIN_DIR.exists() else []
    total = converted = skipped = 0

    for conv_dir in conv_dirs:
        if not conv_dir.is_dir():
            continue
        conv_id = conv_dir.name
        if filter_id and conv_id != filter_id:
            continue

        transcript = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if not transcript.exists():
            continue

        total += 1
        lines = convert_transcript(conv_id, transcript)
        if lines is None:
            skipped += 1
            continue

        out_file = out_dir / f"{conv_id}.jsonl"
        req_count = sum(1 for l in lines if l.get("type") == "user")

        if dry_run:
            print(f"  {conv_id[:8]}… → {len(lines)} Claude lines  ({req_count} requests)")
        else:
            with open(out_file, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(json.dumps(line, ensure_ascii=False) + "\n")
            print(f"  ✅ {conv_id[:8]}… → {out_file.name}  ({req_count} requests)")
        converted += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total: {total} | Converted: {converted} | Skipped (empty): {skipped}")
    if not dry_run and converted > 0:
        print(f"\n📂 Output: {out_dir}")
        print("🚀 Reload AI Engineering Coach extension to see your sessions!")


if __name__ == "__main__":
    dry   = "--dry-run" in sys.argv
    fid   = None
    if "--id" in sys.argv:
        idx = sys.argv.index("--id")
        if idx + 1 < len(sys.argv):
            fid = sys.argv[idx + 1]
    run(dry_run=dry, filter_id=fid)
