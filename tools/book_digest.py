#!/usr/bin/env python3
"""
B1: book_digest.py — конвейер «прочтения» книг.

Книга (md) → чанки → конспекты глав на free-каскаде → единый digest.md
(суть/идеи/паттерны/применимо к нам/оценка) → тезисы в claude-mem.

Использование:
  python3 tools/book_digest.py --input vault/00-Inbox/book.md \
      --slug building-effective-agents --title "Building Effective Agents"
  python3 tools/book_digest.py --input path/to/book.md --chunk-size 5000 --no-claude-mem
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai/gpt-oss-20b:free",
    "google/gemma-4-31b-it:free",
]

CHUNK_PROMPT = """Ты — конспектёр научно-практической литературы. Фрагмент книги ниже.

Задача: краткий конспект фрагмента (не более 250 слов), ТОЛЬКО:
1. Ключевые тезисы (маркированный список, до 5 пунктов)
2. Паттерны/фреймворки/концепции (если есть, с одним предложением объяснения)

Не добавляй воды, не пересказывай примеры. Пиши на русском.

=== ФРАГМЕНТ ===
{chunk}
"""

DIGEST_PROMPT = """Ты — редактор конспектов. Ниже конспекты глав книги «{title}».

Собери из них итоговый digest в строго этом формате (markdown, русский):

## Суть (2-3 предложения)
## Ключевые идеи
1. ...
## Паттерны/фреймворки
- **Название** — одно предложение
## Применимо к нам
- конкретные применения к нашим AI-агентам (агенты, пайплайны, evals, память)
## Оценка ценности
X/10 — почему

=== КОНСПЕКТЫ ГЛАВ ===
{chunks}
"""

CLAUDE_MEM_API = os.getenv("CLAUDE_MEM_SERVER_BETA_API", "http://localhost:37878")
CLAUDE_MEM_KEY = os.getenv("CLAUDE_MEM_SERVER_BETA_API_KEY", "")


def _load_claude_mem_config() -> None:
    """Вне opencode-сессии ключи claude-mem берём из settings.json."""
    global CLAUDE_MEM_API, CLAUDE_MEM_KEY
    if CLAUDE_MEM_KEY:
        return
    try:
        settings = json.loads(
            (Path.home() / ".claude-mem" / "settings.json").read_text(encoding="utf-8")
        )
        CLAUDE_MEM_KEY = settings.get("CLAUDE_MEM_SERVER_BETA_API_KEY", "")
        CLAUDE_MEM_API = settings.get("CLAUDE_MEM_SERVER_BETA_URL", CLAUDE_MEM_API)
    except Exception as e:  # noqa: BLE001
        print(f"[book_digest] claude-mem config not loaded: {e}", file=sys.stderr)


def call_llm(prompt: str, max_tokens: int = 4000) -> str | None:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        print("[book_digest] OPENROUTER_API_KEY не задан", file=sys.stderr)
        return None
    for model in FREE_MODELS:
        try:
            body = json.dumps(
                {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=240) as r:
                data = json.loads(r.read().decode())
            md = data["choices"][0]["message"]["content"].strip()
            if md:
                return md
        except Exception as e:  # noqa: BLE001 — каскад
            print(f"[book_digest] {model} failed: {e}", file=sys.stderr)
            continue
    return None


def split_chunks(text: str, chunk_size: int) -> list[str]:
    """Разбивка по заголовкам (# / ##), иначе по размеру."""
    sections = re.split(r"(?=^#{1,2} )", text, flags=re.MULTILINE)
    chunks: list[str] = []
    current = ""
    for sec in sections:
        if not sec.strip():
            continue
        if len(current) + len(sec) > chunk_size and current:
            chunks.append(current.strip())
            current = sec
        else:
            current += sec
        if len(current) > chunk_size * 2:
            chunks.append(current.strip())
            current = ""
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if len(c) > 200]


def push_to_claude_mem(title: str, digest: str) -> None:
    """Тезисы → claude-mem (kind=discovery, project=ai-bureau)."""
    _load_claude_mem_config()
    if not CLAUDE_MEM_KEY:
        print("[book_digest] claude-mem key отсутствует — пропуск push", file=sys.stderr)
        return
    # Извлекаем "Применимо к нам" и ключевые идеи для наблюдения
    applicable = re.search(r"## Применимо к нам\n(.*?)(?=\n## |\Z)", digest, re.S)
    ideas = re.search(r"## Ключевые идеи\n(.*?)(?=\n## |\Z)", digest, re.S)
    content = f"Книга: {title}\n"
    if ideas:
        content += f"Идеи:\n{ideas.group(1).strip()[:2000]}\n"
    if applicable:
        content += f"Применимо к нам:\n{applicable.group(1).strip()[:1500]}\n"
    try:
        body = json.dumps(
            {
                "content": content,
                "projectId": "ai-bureau",
                "kind": "discovery",
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{CLAUDE_MEM_API}/v1/memories",
            data=body,
            headers={
                "Authorization": f"Bearer {CLAUDE_MEM_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[book_digest] claude-mem: {r.status}")
    except Exception as e:
        print(f"[book_digest] claude-mem push failed: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Конвейер «прочтения» книг")
    ap.add_argument("--input", "-i", required=True, help="md-файл книги")
    ap.add_argument("--slug", "-s", required=True, help="slug (имя папки в 06-Library/books)")
    ap.add_argument("--title", "-t", required=True, help="Название книги")
    ap.add_argument("--author", "-a", default="", help="Автор")
    ap.add_argument("--chunk-size", type=int, default=6000, help="размер чанка (chars)")
    ap.add_argument("--no-claude-mem", action="store_true", help="не писать в claude-mem")
    ap.add_argument("--out", "-o", help="папка вывода (default: vault/06-Library/books/<slug>)")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"❌ [book_digest] Файл не найден: {src}", file=sys.stderr)
        sys.exit(1)

    out_dir = (
        Path(args.out)
        if args.out
        else (Path.home() / "freelance-2026" / "vault" / "06-Library" / "books" / args.slug)
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    text = src.read_text(encoding="utf-8", errors="replace")
    if len(text) < 2000:
        print(
            f"⚠️ [book_digest] Слишком короткий файл ({len(text)} chars) — это не книга?",
            file=sys.stderr,
        )
    chunks = split_chunks(text, args.chunk_size)
    print(f"[book_digest] {len(chunks)} чанков, ~{len(text)} chars")

    chapter_notes: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        print(f"[book_digest] чанк {i}/{len(chunks)}...")
        note = call_llm(CHUNK_PROMPT.format(chunk=chunk), max_tokens=1500)
        if note:
            chapter_notes.append(f"### Глава {i}\n{note}")
        else:
            print(
                f"⚠️ [book_digest] все free-модели не ответили на чанке {i} — пропуск",
                file=sys.stderr,
            )

    if not chapter_notes:
        print(
            "❌ [book_digest] Ни один чанк не законспектирован — digest не собран", file=sys.stderr
        )
        sys.exit(2)

    print("[book_digest] сборка digest...")
    digest = call_llm(
        DIGEST_PROMPT.format(title=args.title, chunks="\n\n".join(chapter_notes)), max_tokens=4000
    )
    if not digest:
        digest = "\n\n".join(chapter_notes)

    date = datetime.now().strftime("%Y-%m-%d")
    header = f"""---
title: {args.title}
author: {args.author}
read: {date}
model: {FREE_MODELS[0]}
status: read
---

# {args.title}

"""
    digest_path = out_dir / "digest.md"
    digest_path.write_text(header + digest, encoding="utf-8")

    # Кладём исходник рядом
    if src.parent != out_dir:
        target_md = out_dir / "source.md"
        if not target_md.exists():
            target_md.write_text(text, encoding="utf-8")

    print(f"✅ [book_digest] digest → {digest_path}")

    if not args.no_claude_mem:
        push_to_claude_mem(args.title, digest)


if __name__ == "__main__":
    main()
