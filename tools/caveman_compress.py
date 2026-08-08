#!/usr/bin/env python3
"""
Caveman-компрессор: сжимает промпты/правила, сохраняя смысл.

Принцип:
- Убрать water words (очевидное, повторы, «важно», «критично»)
- Сократить до ключевых директив
- Сохранить все жёсткие правила (НИКОГДА, ЗАПРЕЩЕНО)
- Имена констант, пути, команды — не трогать

Использование:
  python3 tools/caveman_compress.py ~/freelance-2026/AGENTS.md --output /tmp/AGENTS_compressed.md
  python3 tools/caveman_compress.py --dir ~/.config/opencode/skills/ --suffix .compressed
  python3 tools/caveman_compress.py file.md --measure  # только замер, без записи
"""

import argparse
import re
from pathlib import Path

WATER_PHRASES = [
    r"(?im)^#+\s*.*\n",  # все заголовки (для зачистки дублей)
    r"(?i)\b(очень|весьма|крайне|действительно|безусловно)\s+",
    r"(?i)\b(важно отметить,?\s*что|следует отметить|необходимо подчеркнуть)\s*",
    r"(?i)\b(в данном случае|в контексте|в рамках)\s+",
    r"(?i)\b(является|представляет собой|выступает в качестве)\s+",
    r"(?i)\b(обратите внимание|стоит упомянуть|не лишним будет)\s*[,:]\s*",
    r"(?i)\b(как уже было сказано|как упоминалось|повторимся)\s*[,:]\s*",
    r"\n{3,}",  # multiple blank lines
    r"^---+$",  # horizontal rules
]

KEEP_PATTERNS = [
    r"(?i)\b(НИКОГДА|ЗАПРЕЩЕНО|ОБЯЗАТЕЛЬНО|КАТЕГОРИЧЕСКИ)\b",
    r"(?i)\b(MUST|NEVER|REQUIRED|FORBIDDEN|MANDATORY)\b",
    r"(?i)\b(ЖЕЛЕЗНОЕ ПРАВИЛО|КРИТИЧЕСКИ|HARD RULE)\b",
    r"`[^`]+`",
    r"https?://\S+",
    r"\b(v\d+\.\d+|v\d+\.\d+\.\d+)\b",
]

PRESERVE_SECTIONS = [
    "БЫСТРЫЙ ДОСТУП",
    "АВТОМАТИЧЕСКИЕ ПАТТЕРНЫ",
    "Жёсткие правила",
    "Каскадная система",
    "Правила эскалации",
    "Карта проектов",
]


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def compress_text(text: str) -> tuple[str, dict]:
    lines = text.split("\n")
    stats = {"original_chars": len(text), "original_tokens": estimate_tokens(text)}

    result_lines = []
    in_preserve_block = False
    preserved_sections = 0
    lines_removed = 0

    for line in lines:
        stripped = line.strip()

        if any(section in stripped for section in PRESERVE_SECTIONS):
            in_preserve_block = True
            preserved_sections += 1

        if stripped.startswith("## ") and in_preserve_block:
            pass
        elif stripped.startswith("#") and not any(s in stripped for s in PRESERVE_SECTIONS):
            in_preserve_block = False

        if not stripped and not in_preserve_block:
            lines_removed += 1
            continue

        has_keep = any(re.search(p, line) for p in KEEP_PATTERNS)
        if has_keep:
            result_lines.append(line)
            continue

        if in_preserve_block:
            result_lines.append(line)
            continue

        compressed = line
        for pattern in WATER_PHRASES:
            compressed = re.sub(pattern, "", compressed)

        compressed = re.sub(r"\s{2,}", " ", compressed)
        if compressed.strip():
            result_lines.append(compressed)
        else:
            lines_removed += 1

    result = "\n".join(result_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    stats["compressed_chars"] = len(result)
    stats["compressed_tokens"] = estimate_tokens(result)
    stats["chars_saved_pct"] = round(
        (1 - stats["compressed_chars"] / max(1, stats["original_chars"])) * 100, 1
    )
    stats["tokens_saved_pct"] = round(
        (1 - stats["compressed_tokens"] / max(1, stats["original_tokens"])) * 100, 1
    )
    stats["lines_removed"] = lines_removed
    stats["preserved_sections"] = preserved_sections

    return result, stats


def main():
    parser = argparse.ArgumentParser(description="Caveman-style prompt compression")
    parser.add_argument("path", help="File or directory to compress")
    parser.add_argument("--output", "-o", help="Output file (default: <input>.compressed)")
    parser.add_argument(
        "--dir", action="store_true", help="Path is a directory (compress all .md files)"
    )
    parser.add_argument(
        "--suffix", default=".compressed", help="Suffix for dir mode (default: .compressed)"
    )
    parser.add_argument("--measure", action="store_true", help="Only measure, don't write")
    parser.add_argument("--dry-run", action="store_true", help="Show stats, don't write")
    args = parser.parse_args()

    if args.dir:
        base = Path(args.path)
        files = list(base.rglob("*.md"))
        total_original = 0
        total_compressed = 0
        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            compressed, stats = compress_text(text)
            total_original += stats["original_tokens"]
            total_compressed += stats["compressed_tokens"]
            if not args.measure:
                out = fpath.with_suffix(args.suffix)
                out.write_text(compressed, encoding="utf-8")
                print(
                    f"  {fpath.name}: {stats['original_tokens']}→{stats['compressed_tokens']} tokens (-{stats['tokens_saved_pct']}%)"
                )
        print(
            f"\nTotal: {total_original}→{total_compressed} tokens (-{round((1-total_compressed/max(1,total_original))*100, 1)}%)"
        )
    else:
        fpath = Path(args.path)
        text = fpath.read_text(encoding="utf-8")
        compressed, stats = compress_text(text)

        print(f"Original:   {stats['original_tokens']} tokens ({stats['original_chars']} chars)")
        print(
            f"Compressed: {stats['compressed_tokens']} tokens ({stats['compressed_chars']} chars)"
        )
        print(f"Saved:      {stats['tokens_saved_pct']}% tokens, {stats['chars_saved_pct']}% chars")
        print(f"Lines cut:  {stats['lines_removed']}")
        print(f"Preserved:  {stats['preserved_sections']} sections")

        if not args.measure:
            out = (
                Path(args.output) if args.output else fpath.with_name(fpath.stem + "_compressed.md")
            )
            if args.dry_run:
                print(f"\nWould write to: {out}")
            else:
                out.write_text(compressed, encoding="utf-8")
                print(f"\nWritten: {out}")


if __name__ == "__main__":
    main()
