#!/usr/bin/env python3
"""
Secret rotation (leaked-key recovery). See SKILL.md for the full technique.

Re-runnable: reads the NEW key from /tmp/.new_key_tmp, dry-run by default,
does a whole-file regex replace across all candidate .env* files (plus known
daemon env), and skips placeholders (your_key, <...>, ${...}, ***).

HARD RULES (from the user):
- Never print the key. Use cut -c1-30 for safe prefix verification only.
- Keys come from env, so we edit .env* files, NOT source code.
- Whole-file regex replace (NOT line-by-line): .env values can be multiline,
  so readlines() splits logical lines wrong.
"""
import argparse
import os
import re
import sys

KEY_FILE = "/tmp/.new_key_tmp"
ROOT = os.path.expanduser("~/freelance-2026")
DAEMON_ENV = os.path.expanduser("~/.omniroute/.env")

# Key shapes we rotate. OpenRouter keys look like sk-or-v1-...; OpenAI-style
# keys contain dots/underscores. Class MUST include . and _.
KEY_RE = re.compile(r"sk-[A-Za-z0-9._\-]{10,}")

# Which env var names hold the key (value to the left of '=').
TARGET_VARS = ("OPENROUTER_API_KEY", "OMNIROUTE_API_KEY", "OPENAI_API_KEY")


def find_env_files():
    files = []
    # whole-tree glob of .env* under the working root
    for name in os.listdir(ROOT):
        if name.startswith(".env"):
            p = os.path.join(ROOT, name)
            if os.path.isfile(p):
                files.append(p)
    if os.path.isfile(DAEMON_ENV):
        files.append(DAEMON_ENV)
    return files


def is_placeholder(val):
    v = val.strip().strip("'\"")
    if v in ("", "your_key", "***"):
        return True
    if v.startswith("<") and v.endswith(">"):
        return True
    if v.startswith("${") and v.endswith("}"):
        return True
    return False


def replace_in_file(path, new_key, dry_run):
    try:
        text = open(path, "r", encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"  ! skip (read error): {path}: {e}", file=sys.stderr)
        return 0
    # capture the existing key var name(s) present in this file
    changed = 0
    new_text = text
    for var in TARGET_VARS:
        # match "VAR=sk-..." possibly with surrounding quotes
        pat = re.compile(
            r'(?m)^(' + re.escape(var) + r'\s*=\s*[\'"]?)'
            r'(sk-[A-Za-z0-9._\-]{10,})'
        )
        def _sub(m):
            nonlocal changed
            prefix, old = m.group(1), m.group(2)
            if is_placeholder(old):
                return m.group(0)
            changed += 1
            return f"{prefix}{new_key}"
        new_text = pat.sub(_sub, new_text)
    if changed:
        print(f"  {'[DRY] ' if dry_run else ''}will change: {path}")
        if not dry_run:
            open(path, "w", encoding="utf-8").write(new_text)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="actually write changes (default: dry-run)")
    args = ap.parse_args()

    if not os.path.isfile(KEY_FILE):
        print(f"NEW key not found at {KEY_FILE}. Write it there first "
              f"(cat > {KEY_FILE} <<'EOF' ... EOF), never into chat.",
              file=sys.stderr)
        return 2
    new_key = open(KEY_FILE).read().strip()
    if not new_key or not KEY_RE.fullmatch(new_key):
        print("NEW key in", KEY_FILE, "does not look like a real key "
              "(sk-...{10,}). Aborting.", file=sys.stderr)
        return 2

    dry = not args.write
    print(f"Mode: {'DRY-RUN (no writes)' if dry else 'WRITE'}")
    files = find_env_files()
    print(f"Scanning {len(files)} .env* candidate(s)...")
    total = 0
    for p in files:
        total += replace_in_file(p, new_key, dry)
    print(f"Done. Files changed: {total}.")
    if dry and total:
        print("Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
