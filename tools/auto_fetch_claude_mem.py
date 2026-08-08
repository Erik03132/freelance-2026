#!/usr/bin/env python3
"""
OH-3: Auto-fetch цикл — фоновый таймер, подтягивающий ключевые доки в claude-mem.

Режимы:
  one-shot:  python3 auto_fetch_claude_mem.py --sources list.json
  daemon:    python3 auto_fetch_claude_mem.py --sources list.json --interval 86400 --once-per-day

Источники: sitemap.xml / URL / локальные файлы → текст → memory_add (observation_add).
Правило: для РФ-сервисов и локальных — напрямую; зарубежные — только через прокси (ADR-002).
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, UTC
from pathlib import Path

API_BASE = os.getenv("CLAUDE_MEM_SERVER_BETA_API", "http://localhost:37878")
API_KEY = os.getenv("CLAUDE_MEM_SERVER_BETA_API_KEY", "")
PROJECT_ID = os.getenv("CLAUDE_MEM_SERVER_BETA_PROJECT_ID", "ai-bureau")

RU_DOMAINS = (
    "pravo.gov.ru",
    "sudact.ru",
    "arbitr.ru",
    "bitrix24.ru",
    "mango-office.ru",
    "yandex.ru",
    "vk.com",
)
LOCAL_DOMAINS = ("localhost", "127.0.0.1")


def _proxy_mode(url: str) -> dict:
    """ADR-002: РФ/localhost напрямую; зарубежные — через прокси."""
    host = urllib.parse.urlparse(url).hostname or ""
    for d in RU_DOMAINS + LOCAL_DOMAINS:
        if host == d or host.endswith("." + d):
            return {}
    return {}


def strip_proxies() -> None:
    for n in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "NO_PROXY",
    ]:
        os.environ.pop(n, None)


def fetch_url(url: str, timeout: int = 30) -> str:
    if _proxy_mode(url):
        strip_proxies()
    req = urllib.request.Request(url, headers={"User-Agent": "auto-fetch-claude-mem/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_sitemap(url: str, max_urls: int = 20) -> list[str]:
    body = fetch_url(url)
    import re

    locs = re.findall(r"<loc>(.*?)</loc>", body, re.S)
    return locs[:max_urls]


def push_to_claude_mem(content: str, kind: str = "auto_fetch", source: str = "") -> bool:
    """Вызывает server-beta /v1/memories (observation_add)."""
    import urllib.request

    payload = json.dumps(
        {
            "content": content,
            "kind": kind,
            "projectId": PROJECT_ID,
            "metadata": {"source": source, "fetched_at": datetime.now(UTC).isoformat()},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/v1/memories",
        data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status < 300
    except Exception as e:
        print(f"[auto_fetch] push failed: {e}", file=sys.stderr)
        return False


def process_source(src: dict, limit: int) -> dict:
    kind = src.get("type", "url")
    url = src.get("url", "")
    name = src.get("name", url)
    result = {"name": name, "url": url, "ok": 0, "failed": 0, "pushed": 0}

    try:
        if kind == "sitemap":
            urls = parse_sitemap(url, limit)
        else:
            urls = [url]

        for u in urls:
            try:
                text = fetch_url(u)
                if len(text.strip()) < 50:
                    result["failed"] += 1
                    continue
                result["ok"] += 1
                if push_to_claude_mem(text[:4000], source=u):
                    result["pushed"] += 1
            except Exception:
                result["failed"] += 1
    except Exception as e:
        result["failed"] += 1
        print(f"  ⚠️ {name}: {e}")

    return result


def main():
    ap = argparse.ArgumentParser(description="Auto-fetch ключевых доков в claude-mem")
    ap.add_argument("--sources", "-s", required=True, help="JSON-файл со списком источников")
    ap.add_argument(
        "--interval", "-i", type=int, default=0, help="интервал секунд (0 = one-shot, >0 = daemon)"
    )
    ap.add_argument("--limit", type=int, default=10, help="макс URL из sitemap")
    args = ap.parse_args()

    sources = json.loads(Path(args.sources).read_text(encoding="utf-8"))

    if args.interval == 0:
        for src in sources:
            r = process_source(src, args.limit)
            print(f"✅ {r['name']}: ok={r['ok']} failed={r['failed']} pushed={r['pushed']}")
        return

    print(f"[auto_fetch] daemon каждые {args.interval}с (Ctrl+C — стоп)")
    while True:
        for src in sources:
            r = process_source(src, args.limit)
            print(f"[{datetime.now():%H:%M}] {r['name']}: ok={r['ok']} pushed={r['pushed']}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
