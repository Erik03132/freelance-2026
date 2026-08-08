#!/usr/bin/env python3
"""
AI-1: Markdown-зеркала ключевых страниц для ИИ-поиска (Алиса/ChatGPT/Perplexity).
HTML → чистый Markdown + вставка <link rel="alternate" type="text/markdown"> в <head>.

Использование:
  python3 tools/html_md_mirror.py path/to/page.html
  python3 tools/html_md_mirror.py path/to/page.html --out docs/mirrors/
  python3 tools/html_md_mirror.py --site dir/ --all
"""

import argparse
import html as html_mod
import re
import sys
from pathlib import Path

TAG = '<link rel="alternate" type="text/markdown" href="{mirror_url}">'

BLOCK_TAGS = re.compile(
    r"<(h[1-6]|p|div|section|article|li|tr|br|ul|ol|table|blockquote|header|footer)[^>]*>",
    re.I,
)


def html_to_markdown(raw: str) -> str:
    """Грубый HTML→Markdown: извлекает заголовки, абзацы, списки, ссылки."""
    # Извлекаем title
    title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    title = html_mod.unescape(title_m.group(1)).strip() if title_m else ""

    text = raw
    text = re.sub(r"<script.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    # Заголовки → #
    for i in range(1, 7):
        text = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            lambda m, n=i: "\n\n" + "#" * n + " " + _inline_to_md(m.group(1)).strip() + "\n",
            text,
            flags=re.S | re.I,
        )

    # Ссылки → [текст](url)
    text = re.sub(
        r"<a[^>]*href=[\"']([^\"']*)[\"'][^>]*>(.*?)</a>",
        lambda m: f"[{_inline_to_md(m.group(2)).strip()}]({m.group(1)})",
        text,
        flags=re.S | re.I,
    )

    # Списки
    text = re.sub(
        r"<li[^>]*>(.*?)</li>",
        lambda m: "- " + _inline_to_md(m.group(1)).strip() + "\n",
        text,
        flags=re.S | re.I,
    )

    # Блоки → перевод строки
    text = BLOCK_TAGS.sub("\n", text)
    text = re.sub(r"</(h[1-6]|p|div|li|tr)>", "\n", text, flags=re.I)

    # Инлайн
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.S | re.I)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.S | re.I)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html_mod.unescape(text)

    # Схлопнуть пустые строки
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [ln.rstrip() for ln in text.splitlines()]
    text = "\n".join(lines).strip()

    if title and not text.startswith("#"):
        text = f"# {title}\n\n{text}"

    return text


def _inline_to_md(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html_mod.unescape(s)


def inject_link_tag(raw: str, mirror_path: str) -> str:
    if TAG.split('"')[1].split('"')[0] and 'rel="alternate"' in raw:
        return raw
    tag = TAG.format(mirror_url=mirror_path)
    return re.sub(r"(<head[^>]*>)", r"\1\n    " + tag, raw, count=1, flags=re.I)


def process_file(src: Path, out_dir: Path | None) -> dict:
    raw = src.read_text(encoding="utf-8", errors="replace")
    md = html_to_markdown(raw)
    mirror_rel = src.with_suffix(".md").name
    updated = inject_link_tag(raw, mirror_rel)

    out_dir = out_dir or src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / mirror_rel
    md_path.write_text(md, encoding="utf-8")

    if 'rel="alternate"' in updated:
        src.write_text(updated, encoding="utf-8")

    return {
        "html": src,
        "mirror": md_path,
        "chars": len(md),
        "words": len(md.split()),
        "link_injected": 'rel="alternate"' in updated,
    }


def main():
    ap = argparse.ArgumentParser(description="HTML→Markdown зеркала для ИИ-поиска")
    ap.add_argument("target", help="HTML-файл или директория (с --all)")
    ap.add_argument("--out", "-o", help="Выходная директория для .md зеркал")
    ap.add_argument("--all", action="store_true", help="Обработать все .html в директории")
    args = ap.parse_args()

    target = Path(args.target)
    files = []
    if args.all and target.is_dir():
        files = sorted(target.rglob("*.html"))
    elif target.is_file():
        files = [target]
    else:
        ap.print_help()
        sys.exit(1)

    for f in files:
        if "node_modules" in str(f) or ".next" in str(f):
            continue
        out = Path(args.out) if args.out else f.parent
        r = process_file(f, out)
        print(
            f"✅ {r['html'].name} → {r['mirror'].name} "
            f"({r['words']} слов, link={'да' if r['link_injected'] else 'нет'})"
        )


if __name__ == "__main__":
    main()
