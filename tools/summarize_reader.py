#!/usr/bin/env python3
"""
Утреннее саммари ночного читателя → Telegram (тот же бот, что и /daily).

Находит digest-книги, прочитанные за последние N дней (frontmatter `read:`),
собирает содержательное сообщение: Заголовок · Суть · топ идеи · Оценка ценности.
Отправляет через ANGELOCHKA_BOT_TOKEN (тело бота) в TG_ADMIN_ID.

Использование:
  python3 tools/summarize_reader.py            # саммари за сегодня (без отправки)
  python3 tools/summarize_reader.py --days 1   # за последние сутки
  python3 tools/summarize_reader.py --send     # + отправка в Telegram
  python3 tools/summarize_reader.py --json     # вывод как JSON (машиночитаемо)

Интеграция: ночной читатель (night_reader.sh) вызывает с --send после Фазы 3.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT_BOOKS = PROJECT_ROOT / "vault" / "06-Library" / "books"
PERSONAL_BASE = Path(
    "/Users/igorvasin/Library/Mobile Documents/iCloud~md~obsidian/Documents/Личное"
)
PERSONAL_BOOKS = PERSONAL_BASE / "КНИГИ"
ENV_FILE = PROJECT_ROOT / "projects" / "ai-eggs" / ".env"
FALLBACK_ENV = PROJECT_ROOT / "ai-eggs" / ".env"

# Если скрипт запущен по пути native из дока, но компоненты ниже ожидают >= одинак версии — не важно


def env_get(key: str) -> str:
    for pf in (ENV_FILE, FALLBACK_ENV, PROJECT_ROOT / ".env"):
        try:
            for line in pf.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip('"').strip("'")
        except FileNotFoundError:
            continue
    return ""


def load_digest(p: Path) -> dict:
    """Парсим frontmatter + релевантные секции digest.md."""
    text = p.read_text(encoding="utf-8", errors="replace")
    meta: dict = {}
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"').strip("'")

    def section(name: str) -> str:
        sm = re.search(
            rf"^##\s*{re.escape(name)}\s*$(.*?)(?=^##\s*\S|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        return sm.group(1).strip() if sm else ""

    essence = section("Суть")
    ideas = section("Ключевые идеи")
    score = section("Оценка ценности")
    return {
        "title": meta.get("title") or p.parent.name,
        "read": meta.get("read", ""),
        "model": meta.get("model", ""),
        "essence": essence,
        "ideas": ideas,
        "score": score,
    }


def collect(days: int, target_date: date | None = None) -> list:
    if target_date is None:
        target_date = date.today()
    from_d = target_date - timedelta(days=days - 1)
    cutoff = from_d.isoformat()

    results = []
    for root in (VAULT_BOOKS, PERSONAL_BOOKS):
        if not root.exists():
            continue
        for d in root.iterdir():
            if not d.is_dir():
                continue
            dp = d / "digest.md"
            if not dp.exists():
                continue
            entry = load_digest(dp)
            if not entry["read"]:
                continue
            try:
                rd = date.fromisoformat(entry["read"].strip()[:10])
            except ValueError:
                continue
            if rd >= from_d:
                entry["dir"] = str(d)
                entry["source"] = "agent" if "06-Library" in str(d) else "personal"
                results.append(entry)
    results.sort(key=lambda x: x["read"], reverse=True)
    return results


def render(results: list, target_date: date | None = None) -> str:
    if target_date is None:
        target_date = date.today()
    if not results:
        return (
            f"📚 *Ночной читатель — тишина*\n\n"
            f"За последние сутки новых книг не прочитано.\n"
            f"Инбоксы пусты — всё разобрано."
        )
    lines = [
        f"🌅 *Утреннее саммари ночного чтения*",
        f"_({len(results)} кн. прочитано ночью, digest готовы)_\n",
    ]
    for i, r in enumerate(results, 1):
        title = r["title"] or "Без названия"
        src_icon = "🐣" if r["source"] == "agent" else "🗂️"
        lines.append(f"{i}. {src_icon} *{title}*")
        if r["essence"]:
            ess = r["essence"].split("\n")[0].strip()
            ess = (ess[:260] + "…") if len(ess) > 260 else ess
            lines.append(f"   💡 {ess}")
        idea_lines = [
            ln.strip()
            for ln in r["ideas"].splitlines()
            if ln.strip().strip("0123456789.- ") and re.search(r"[а-яёa-z]", ln, re.I)
        ]
        idea_lines = idea_lines[:2]
        for il in idea_lines:
            clean = il.lstrip("0123456789.- ")
            clean = (clean[:160] + "…") if len(clean) > 160 else clean
            lines.append(f"   → {clean}")
        sc = r["score"].strip()
        if sc:
            sm = re.search(r"^(\d{1,2})/10", sc)
            if sm:
                lines.append(f"   ⭐ Ценность: {sm.group(1)}/10")
        lines.append("")
    return "\n".join(lines)


def send_tg(text: str) -> bool:
    token = env_get("ANGELOCHKA_BOT_TOKEN")
    chat = env_get("TG_ADMIN_ID") or "176203333"
    proxy = env_get("TELEGRAM_PROXY") or ""
    if not token:
        print("ERR: ANGELOCHKA_BOT_TOKEN не найден", file=sys.stderr)
        return False
    payload = f"chat_id={chat}&text={urllib.request.quote(text)}&parse_mode=Markdown".encode()
    if proxy and "127.0.0.1" not in proxy and "localhost" not in proxy:
        try:
            from urllib.request import ProxyHandler, build_opener
            opener = build_opener(ProxyHandler({"http": proxy, "https": proxy}))
            with opener.open(
                f"https://api.telegram.org/bot{token}/sendMessage", data=payload, timeout=15
            ) as r:
                return 200 <= r.status < 300
        except Exception as e:
            print(f"⚠️ TGFallback: {e}", file=sys.stderr)
    try:
        with urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage", data=payload, timeout=15
        ) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print(f"ERR: {e}", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Утреннее саммари ночного читателя")
    ap.add_argument("--days", type=int, default=1, help="сколь дней назад читали")
    ap.add_argument("--date", type=str, default=None, help="конкретная дата YYYY-MM-DD")
    ap.add_argument("--send", action="store_true", help="отправить в Telegram")
    ap.add_argument("--json", action="store_true", help="вывести JSON")
    args = ap.parse_args()

    tdate = date.fromisoformat(args.date) if args.date else None
    results = collect(args.days, tdate)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    msg = render(results, tdate)
    print(msg)
    if args.send:
        ok = send_tg(msg)
        print(f"\n{'✅ отправлено' if ok else '❌ не отправлено'}")
        return 0 if ok else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())