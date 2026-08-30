#!/usr/bin/env python3
"""
expert_tg_send.py — отправка экспертного саммари в Telegram (тот же бот/чат,
что и /daily и summarize_reader).

Использование:
  python3 expert_tg_send.py --text "..."            # отправить готовый текст
  python3 expert_tg_send.py --file path.md          # отправить содержимое файла
  python3 expert_tg_send.py --stdin                  # прочитать из stdin
"""

import argparse
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILES = [
    PROJECT_ROOT / "projects" / "ai-eggs" / ".env",
    PROJECT_ROOT / "ai-eggs" / ".env",
    PROJECT_ROOT / ".env",
]


def env_get(key: str) -> str:
    for pf in ENV_FILES:
        try:
            for line in pf.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip('"').strip("'")
        except FileNotFoundError:
            continue
    return ""


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
    ap = argparse.ArgumentParser(description="Отправка экспертного саммари в TG")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="готовый текст")
    src.add_argument("--file", help="файл с текстом")
    src.add_argument("--stdin", action="store_true", help="из stdin")
    args = ap.parse_args()

    if args.text is not None:
        text = args.text
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    ok = send_tg(text)
    print(f"{'✅ отправлено' if ok else '❌ не отправлено'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
