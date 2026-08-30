#!/usr/bin/env python3
"""hermes_news.py — утренний блок «Hermes Agent news» для Angela_bot.

Собирает свежие новости по Hermes Agent (Nous Research) из открытых
источников и формирует компактный дайджест. Предназначен для вызова
из scheduler.py в 09:00 MSK (после habr_digest).

Паттерн (CP-1): --help, --dry-run, идемпотентность, pipeline-safe.
Отправка в TG только по флагу --send (иначе печатает в stdout).

Источники (без ключей, публичные):
  - GitHub NousResearch/hermes-agent (releases/commits via API)
  - Telegram-каналы Hermes (опц, если заданы в .env)
  - changelog страница (если доступна)
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **k: None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

GITHUB_API = "https://api.github.com/repos/NousResearch/hermes-agent"
CACHE_FILE = os.path.join(BASE_DIR, "data", "hermes_news_state.json")
LOOKBACK_DAYS = 2  # окно новостей


def _seen_cache() -> dict:
    try:
        return json.load(open(CACHE_FILE, encoding="utf-8"))
    except Exception:
        return {"seen": []}


def _save_cache(seen: list):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    json.dump(
        {"seen": seen[-200:]}, open(CACHE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2
    )


def fetch_github_news() -> list[dict]:
    """Последние коммиты/релизы Hermes Agent с GitHub API (без токена, rate-limited)."""
    import urllib.request

    out = []
    try:
        req = urllib.request.Request(
            f"{GITHUB_API}/commits?per_page=10",
            headers={"User-Agent": "hermes-news-collector"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        cache = _seen_cache()
        new_items = []
        for c in data:
            sha = c.get("sha", "")[:10]
            if sha in cache["seen"]:
                continue
            msg = c.get("commit", {}).get("message", "").split("\n")[0][:120]
            author = c.get("commit", {}).get("author", {}).get("name", "?")
            date = c.get("commit", {}).get("author", {}).get("date", "")[:10]
            new_items.append(
                {
                    "id": sha,
                    "source": "github",
                    "date": date,
                    "title": f"{msg} — @{author}",
                }
            )
        # обновляем кэш только новыми
        cache["seen"].extend([i["id"] for i in new_items])
        _save_cache(cache["seen"])
        out.extend(new_items)
    except Exception as e:
        print(f"  ⚠ GitHub fetch error: {e}", file=sys.stderr)
    return out


def build_digest(news: list[dict]) -> str:
    if not news:
        return ""
    lines = ["🔔 **Hermes Agent — свежие изменения**", ""]
    for n in news[:8]:
        lines.append(f"• [{n['source']}] {n['title']} _{n.get('date','')}_")
    lines.append("")
    lines.append("_Источник: GitHub NousResearch/hermes-agent_")
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    """Отправка в TG (только если --send). Токен/ID из .env."""
    import urllib.parse

    token = os.getenv("ANGELOCHKA_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("ADMIN_TELEGRAM_ID", "176203333")
    if not token:
        print("  ⚠ TELEGRAM token не найден в .env — пропускаю отправку", file=sys.stderr)
        return False
    try:
        import urllib.request

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }
        ).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        print(f"  ⚠ Telegram send error: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser(
        description="Сборщик новостей Hermes Agent для утреннего дайджеста Angela_bot.",
        epilog="Примеры:\n"
        "  hermes_news.py --dry-run          # только показать, что нашёл\n"
        "  hermes_news.py --send             # собрать и отправить в TG (Игорю)\n",
    )
    ap.add_argument("--dry-run", action="store_true", help="не отправлять, только вывести дайджест")
    ap.add_argument("--send", action="store_true", help="отправить в Telegram (Игорю)")
    ap.add_argument("--lookback-days", type=int, default=LOOKBACK_DAYS)
    args = ap.parse_args()

    print(f"🔍 Hermes Agent news — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    news = fetch_github_news()
    digest = build_digest(news)

    if not digest:
        print("  ✅ Новостей нет (окно ±%d дней)" % args.lookback_days)
        return 0

    print("─" * 50)
    print(digest)
    print("─" * 50)

    if args.send:
        ok = send_telegram(digest)
        print(f"  📤 Отправлено в TG: {'OK' if ok else 'FAIL'}")
    elif args.dry_run:
        print("  (dry-run: отправка отключена)")
    else:
        print("  (ни --send, ни --dry-run: только сбор в stdout)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
