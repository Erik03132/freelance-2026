#!/usr/bin/env python3
"""
url_to_markdown.py — URL→чистый Markdown для AI-агентов

Использует curl.md для конвертации веб-страниц в оптимизированный
Markdown. Убирает навигацию, рекламу, скрипты — оставляет контент.

Экономия: 60-80% токенов по сравнению с сырым HTML.

Использование:
    # Из командной строки
    python3 tools/url_to_markdown.py https://vezemcip.ru
    python3 tools/url_to_markdown.py https://habr.com/ru/articles/123/ --objective "как работает RAG"
    python3 tools/url_to_markdown.py https://example.com --keywords "api,webhook"

    # Из кода
    from url_to_markdown import fetch_as_markdown
    md = fetch_as_markdown("https://vezemcip.ru")
    md = fetch_as_markdown("https://habr.com/article", objective="RAG pipeline")

Зависимости: npx (Node.js), curl.md (устанавливается автоматически через npx -y)
"""

import subprocess
import sys
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# === КОНФИГУРАЦИЯ ===

# Кэш на 1 час по умолчанию
CACHE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent / "ai-eggs" / "data" / "url_cache"
CACHE_TTL_HOURS = 1
MAX_CACHE_SIZE_MB = 50
TIMEOUT_SECONDS = 30


def _cache_key(url: str, objective: str = "", keywords: str = "") -> str:
    """Генерирует ключ кэша из URL + параметров."""
    raw = f"{url}|{objective}|{keywords}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached(key: str, ttl_hours: int = CACHE_TTL_HOURS) -> str | None:
    """Проверяет кэш. Возвращает markdown или None."""
    cache_file = CACHE_DIR / f"{key}.md"
    meta_file = CACHE_DIR / f"{key}.json"

    if not cache_file.exists() or not meta_file.exists():
        return None

    try:
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        cached_at = datetime.fromisoformat(meta.get("cached_at", "2000-01-01"))
        if datetime.now() - cached_at > timedelta(hours=ttl_hours):
            return None  # протухло
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None


def _save_cache(key: str, url: str, markdown: str, objective: str = "", keywords: str = ""):
    """Сохраняет результат в кэш."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / f"{key}.md"
    meta_file = CACHE_DIR / f"{key}.json"

    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    with open(meta_file, 'w') as f:
        json.dump({
            "url": url,
            "objective": objective,
            "keywords": keywords,
            "cached_at": datetime.now().isoformat(),
            "size_bytes": len(markdown.encode('utf-8')),
        }, f, indent=2)


def fetch_as_markdown(
    url: str,
    objective: str = "",
    keywords: str = "",
    fresh: bool = False,
    timeout: int = TIMEOUT_SECONDS,
    max_chars: int = 0,
) -> str:
    """
    Конвертирует URL в чистый Markdown через curl.md.

    Args:
        url: URL страницы
        objective: Сузить контент под конкретную цель (опционально)
        keywords: Фильтр по ключевым словам, через запятую (опционально)
        fresh: Принудительно обойти кэш
        timeout: Таймаут в секундах
        max_chars: Ограничить вывод по символам (0 = без лимита)

    Returns:
        Чистый Markdown-текст страницы.
        При ошибке — строка с описанием ошибки.
    """
    # 1. Проверяем кэш
    key = _cache_key(url, objective, keywords)
    if not fresh:
        cached = _get_cached(key)
        if cached:
            return cached if max_chars == 0 else cached[:max_chars]

    # 2. Метод 1: npx curl.md (локально, Mac)
    markdown = _try_npx(url, objective, keywords, fresh, timeout)

    # 3. Метод 2: HTTP API fallback (VPS, старый Node)
    if not markdown or markdown.startswith("❌"):
        markdown = _try_http_api(url, timeout)

    if not markdown:
        return f"⚠️ curl.md: не удалось загрузить {url}"

    # 4. Кэшируем
    _save_cache(key, url, markdown, objective, keywords)

    return markdown if max_chars == 0 else markdown[:max_chars]


def _try_npx(url: str, objective: str, keywords: str, fresh: bool, timeout: int) -> str:
    """Попытка через npx curl.md (требует Node >= 22)."""
    cmd = ["npx", "-y", "curl.md", url]
    if objective:
        cmd.extend(["--objective", objective])
    if keywords:
        cmd.extend(["--keywords", keywords])
    if fresh:
        cmd.append("--fresh")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "NODE_NO_WARNINGS": "1"},
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return ""
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return ""


def _try_http_api(url: str, timeout: int) -> str:
    """Fallback: curl https://curl.md/<domain+path> (работает везде)."""
    # Убираем протокол для curl.md API
    clean_url = url.replace("https://", "").replace("http://", "")
    api_url = f"https://curl.md/{clean_url}"

    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), api_url],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return ""
    except Exception:
        return ""


def fetch_multiple(urls: list[str], **kwargs) -> dict[str, str]:
    """Загрузить несколько URL. Возвращает {url: markdown}."""
    results = {}
    for url in urls:
        results[url] = fetch_as_markdown(url, **kwargs)
    return results


def clean_cache(max_age_hours: int = 24):
    """Удаляет устаревшие файлы из кэша."""
    if not CACHE_DIR.exists():
        return 0

    removed = 0
    for meta_file in CACHE_DIR.glob("*.json"):
        try:
            with open(meta_file, 'r') as f:
                meta = json.load(f)
            cached_at = datetime.fromisoformat(meta.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_at > timedelta(hours=max_age_hours):
                md_file = meta_file.with_suffix('.md')
                meta_file.unlink(missing_ok=True)
                md_file.unlink(missing_ok=True)
                removed += 1
        except Exception:
            pass

    return removed


# === CLI ===

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="URL → Markdown для AI-агентов (через curl.md)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python3 url_to_markdown.py https://vezemcip.ru
  python3 url_to_markdown.py https://habr.com/ru/articles/123/ --objective "RAG"
  python3 url_to_markdown.py https://example.com --keywords "api,webhook" --max-chars 5000
  python3 url_to_markdown.py --clean-cache
        """,
    )
    parser.add_argument("url", nargs="?", help="URL для конвертации")
    parser.add_argument("--objective", "-o", default="", help="Сузить контент под цель")
    parser.add_argument("--keywords", "-k", default="", help="Ключевые слова (через запятую)")
    parser.add_argument("--fresh", "-f", action="store_true", help="Обойти кэш")
    parser.add_argument("--timeout", "-t", type=int, default=TIMEOUT_SECONDS, help="Таймаут (сек)")
    parser.add_argument("--max-chars", type=int, default=0, help="Ограничить вывод (0=без лимита)")
    parser.add_argument("--stats", action="store_true", help="Показать статистику (размер vs сырой HTML)")
    parser.add_argument("--clean-cache", action="store_true", help="Очистить устаревший кэш")

    args = parser.parse_args()

    if args.clean_cache:
        removed = clean_cache()
        print(f"🧹 Удалено из кэша: {removed} записей")
        sys.exit(0)

    if not args.url:
        parser.print_help()
        sys.exit(1)

    # Получаем markdown
    md = fetch_as_markdown(
        args.url,
        objective=args.objective,
        keywords=args.keywords,
        fresh=args.fresh,
        timeout=args.timeout,
        max_chars=args.max_chars,
    )

    if args.stats:
        try:
            import requests as req
            raw = req.get(args.url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            raw_size = len(raw.content)
        except ImportError:
            # Fallback: используем curl
            try:
                r = subprocess.run(["curl", "-sL", args.url], capture_output=True, timeout=10)
                raw_size = len(r.stdout)
            except Exception:
                raw_size = 0
        except Exception:
            raw_size = 0

        md_size = len(md.encode('utf-8'))
        saving = ((raw_size - md_size) / raw_size * 100) if raw_size > 0 else 0

        print(f"📊 Сырой HTML: {raw_size:,} байт", file=sys.stderr)
        print(f"📄 curl.md:    {md_size:,} байт", file=sys.stderr)
        print(f"💰 Экономия:   {saving:.0f}%", file=sys.stderr)
        print(f"---", file=sys.stderr)

    print(md)
