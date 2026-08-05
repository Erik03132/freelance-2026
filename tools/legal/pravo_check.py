#!/usr/bin/env python3
"""YU-4: pravo_check.py — проверка действующей редакции нормы через pravo.gov.ru.

Бесплатный официальный источник (ФНПА, publication.pravo.gov.ru API).
Использование:
    python3 pravo_check.py "ст. 333 ГК РФ"            # поиск по запросу
    python3 pravo_check.py --link <url>               # проверить ссылку publication.pravo.gov.ru
    python3 pravo_check.py --json "ст. 152-ФЗ"        # машиночитаемый вывод

Ключевое правило (Фемида, правило 2): запрещено выдавать норму без пометки
о редакции. Эта утилита даёт дату публикации действующей редакции.
"""

import argparse
import html
import json
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime

SEARCH_URL = "http://search.pravo.gov.ru/api/Search/NewSearch"
BASE_URL = "http://publication.pravo.gov.ru"


def fetch(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "pravo-check/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def search(query: str, limit: int = 5) -> list[dict]:
    """Поиск НПА в официальном банке правовых актов (search.pravo.gov.ru)."""
    params = urllib.parse.urlencode(
        {
            "searchtext": query,
            "sortorder": "1",
            "count": str(limit),
            "minDate": "01.01.1994",
            "maxDate": datetime.now().strftime("%d.%m.%Y"),
            "DocumentTypes": "1",
        }
    )
    try:
        raw = fetch(f"{SEARCH_URL}?{params}")
        return json.loads(raw).get("Documents", [])
    except Exception as e:
        return [{"error": f"search failed: {e}"}]


def check_link(url: str, timeout: int = 20) -> dict:
    """Проверка, что ссылка на publication.pravo.gov.ru живая и содержит дату публикации."""
    if "publication.pravo.gov.ru" not in url:
        return {"ok": False, "error": "не publication.pravo.gov.ru"}
    try:
        html_text = fetch(url, timeout)
    except Exception as e:
        return {"ok": False, "error": f"fetch failed: {e}", "url": url}
    date_m = re.search(r"\d{2}\.\d{2}\.\d{4}", html_text)
    title_m = re.search(r"<title>(.*?)</title>", html_text, re.S)
    return {
        "ok": True,
        "url": url,
        "published": date_m.group(0) if date_m else "дата не найдена",
        "title": (html.unescape(title_m.group(1)).strip()[:120] if title_m else "—"),
    }


def main():
    ap = argparse.ArgumentParser(description="Проверка редакции норм РФ через pravo.gov.ru")
    ap.add_argument("query", nargs="?", help="текст запроса, напр. «ст. 333 ГК РФ»")
    ap.add_argument("--link", help="проверить ссылку publication.pravo.gov.ru")
    ap.add_argument("--json", action="store_true", help="вывод JSON")
    args = ap.parse_args()

    if args.link:
        result = check_link(args.link)
    elif args.query:
        result = search(args.query)
    else:
        ap.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
