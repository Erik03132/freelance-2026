#!/usr/bin/env python3
"""
OH-2: Obsidian-зеркало claude-mem — экспорт observations в структурированный волт.

kind → папки волта:
  session-summary → 10-Daily
  decision         → 04-Decisions
  bugfix/lesson    → 03-Lessons
  audit/review     → 05-Audits
  прочие           → 02-Knowledge/observations

Инкрементальность: файл {date}_{kind}_{id}.md — если уже существует, пропускаем (--force перезапишет).

Использование:
  python3 tools/obsidian_mirror.py --vault ~/freelance-2026/vault
  python3 tools/obsidian_mirror.py --vault ~/freelance-2026/vault --kind decision --days 30
  python3 tools/obsidian_mirror.py --vault ~/freelance-2026/vault --api --force
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DB = Path.home() / ".claude-mem" / "memories.db"
API_BASE = os.getenv("CLAUDE_MEM_SERVER_BETA_API", "http://localhost:37878")
API_KEY = os.getenv("CLAUDE_MEM_SERVER_BETA_API_KEY", "")
DEFAULT_VAULT = os.path.expanduser("~/freelance-2026/vault")

KIND_FOLDERS = {
    "session-summary": "10-Daily",
    "session": "10-Daily",
    "daily": "10-Daily",
    "decision": "04-Decisions",
    "adr": "04-Decisions",
    "bugfix": "03-Lessons",
    "lesson": "03-Lessons",
    "refactor": "03-Lessons",
    "discovery": "03-Lessons",
    "audit": "05-Audits",
    "review": "05-Audits",
    "change": "02-Knowledge/observations",
    "feature": "02-Knowledge/observations",
    "manual": "02-Knowledge/observations",
}

FRONTMATTER = """---
date: {date}
kind: {kind}
id: {id}
project: {project}
tags: [{tags}]
---

{content}
"""


def _fetch_api(query: str, limit: int = 50) -> list[dict]:
    import urllib.request

    url = f"{API_BASE}/v1/search?query={urllib.parse.quote(query)}&limit={limit}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        return data.get("observations", data.get("results", []))
    except Exception as e:
        print(
            f"[obsidian_mirror] API search failed ({e}) — falling back to local DB", file=sys.stderr
        )
        return []


def _read_local_db(db_path: Path, days: int) -> list[dict]:
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = conn.execute(
            "SELECT id, type, text, project, created_at FROM observations "
            "WHERE created_at >= ? ORDER BY created_at DESC LIMIT 300",
            (since,),
        ).fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "kind": r["type"] or "manual",
                "content": r["text"] or "",
                "project": r["project"] or "",
                "date": (r["created_at"] or "")[:10],
            }
            for r in rows
        ]
    except sqlite3.Error as e:
        print(f"[obsidian_mirror] DB read failed: {e}", file=sys.stderr)
        return []


def folder_for_kind(kind: str) -> str:
    k = kind.lower()
    for key, folder in KIND_FOLDERS.items():
        if key in k:
            return folder
    return "02-Knowledge/observations"


def export_to_vault(obs: list[dict], vault: Path, force: bool = False) -> dict:
    vault.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for o in obs:
        date = o.get("date") or datetime.now().strftime("%Y-%m-%d")
        kind = o.get("kind", "manual") or "manual"
        safe_kind = re.sub(r"[^a-z0-9_-]", "-", kind.lower())
        safe_id = re.sub(r"[^a-z0-9_-]", "-", str(o.get("id", "x")).lower())
        fname = f"{date}_{safe_kind}_{safe_id}.md"
        folder = folder_for_kind(kind)
        target = vault / folder
        target.mkdir(parents=True, exist_ok=True)
        filepath = target / fname
        if filepath.exists() and not force:
            skipped += 1
            continue
        project = o.get("project", "")
        content = o.get("content", "")
        tags = ", ".join(t for t in [kind, project] if t)
        body = FRONTMATTER.format(
            date=date, kind=kind, id=safe_id, project=project, content=content, tags=tags
        )
        filepath.write_text(body, encoding="utf-8")
        written += 1
    return {"written": written, "skipped": skipped, "vault": str(vault)}


def main():
    ap = argparse.ArgumentParser(description="Obsidian-зеркало claude-mem")
    ap.add_argument(
        "--vault", "-v", default=DEFAULT_VAULT, help="vault dir (default: ~/freelance-2026/vault)"
    )
    ap.add_argument("--db", default=str(DEFAULT_DB), help="локальная БД (fallback)")
    ap.add_argument("--kind", default="", help="фильтр kind (session-summary/decision/bugfix)")
    ap.add_argument("--project", default="", help="фильтр проекта")
    ap.add_argument("--days", type=int, default=7, help="окно дней")
    ap.add_argument("--api", action="store_true", help="тянуть через server-beta API")
    ap.add_argument("--force", action="store_true", help="перезаписать существующие файлы")
    args = ap.parse_args()

    if args.api:
        query = args.kind or "session summary decision bugfix audit"
        obs = _fetch_api(query, limit=200)
    else:
        obs = _read_local_db(Path(args.db), args.days)

    if args.kind:
        obs = [o for o in obs if o.get("kind") == args.kind]
    if args.project:
        obs = [o for o in obs if args.project in str(o.get("project", ""))]

    result = export_to_vault(obs, Path(args.vault), force=args.force)
    print(
        f"✅ Obsidian-зеркало: {result['written']} записано, {result['skipped']} пропущено → {result['vault']}"
    )


if __name__ == "__main__":
    main()
