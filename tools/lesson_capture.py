#!/usr/bin/env python3
"""
Lesson-файлы в волте (ce-compound паттерн + ADR-001 self_improve_log зеркало).
При завершении крупной задачи = lesson в vault/03-Lessons/ + claude-mem.

Использование:
  python3 tools/lesson_capture.py "Фикс 403 в avito.ts" \
    --project freelance-agent \
    --type bugfix \
    --files "src/mcp-servers/avito.ts" \
    --context "При 403 ротируем окружение, не селекторы"
"""

import argparse
import os
from datetime import datetime
from pathlib import Path


LESSON_TEMPLATE = """# {title}

**Date:** {date}
**Project:** {project}
**Type:** {lesson_type}

## What happened

{context}

## Files changed

{files}

## Solution

{solution}

## Lessons

1. {lesson_1}

## Related

- Self-improvement log: ~/.config/opencode/docs/self_improve_log.md
"""


def generate_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in slug)
    slug = slug.strip("-")
    return slug[:60]


def main():
    parser = argparse.ArgumentParser(description="Capture a lesson from completed work")
    parser.add_argument("title", help="Lesson title")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument(
        "--type",
        "-t",
        default="bugfix",
        choices=["bugfix", "feature", "refactor", "decision", "discovery", "change"],
    )
    parser.add_argument("--files", "-f", nargs="*", default=[], help="Files changed")
    parser.add_argument("--context", "-c", default="", help="What happened")
    parser.add_argument("--solution", "-s", default="", help="Solution applied")
    parser.add_argument("--lesson", "-l", nargs="*", default=[], help="Key lessons (up to 3)")
    parser.add_argument("--claude-mem", action="store_true", help="Also add to claude-mem")
    parser.add_argument("--output", "-o", help="Output directory (default: vault/03-Lessons)")
    args = parser.parse_args()

    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_slug = datetime.now().strftime("%Y%m%d")
    slug = generate_slug(args.title)

    workspace = Path(os.environ.get("FREELANCE_WORKSPACE", os.path.expanduser("~/freelance-2026")))
    output_dir = Path(args.output) if args.output else workspace / "vault" / "03-Lessons"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{date_slug}_{slug}.md"
    filepath = output_dir / filename

    lessons = args.lesson if args.lesson else ["(fill in)"]
    while len(lessons) < 3:
        lessons.append("")

    content = LESSON_TEMPLATE.format(
        title=args.title,
        date=date,
        project=args.project,
        lesson_type=args.type,
        context=args.context or "(describe what happened)",
        files="\n".join(f"- {f}" for f in args.files) if args.files else "- (list files)",
        solution=args.solution or "(describe the solution)",
        lesson_1=lessons[0],
    )
    if len(lessons) > 1 and lessons[1]:
        content += f"2. {lessons[1]}\n"
    if len(lessons) > 2 and lessons[2]:
        content += f"3. {lessons[2]}\n"

    filepath.write_text(content, encoding="utf-8")
    print(f"Lesson saved: {filepath}")

    if args.claude_mem:
        print('claude-mem hint: memory_add kind=decision content="..."')
        print(f"  title: {args.title}")
        print(f"  projectId: {args.project}")
        print(f"  kind: {args.type}")


if __name__ == "__main__":
    main()
