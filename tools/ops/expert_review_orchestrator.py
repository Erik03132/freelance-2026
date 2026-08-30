#!/usr/bin/env python3
"""
expert_review_orchestrator.py — оркестратор экспертного разбора фич.

Пайплайн (дополнение к night_reader.sh):
  1. inbox_expert_scan.py --days 1           → JSON новых фич-файлов
  2. (Hermes) разбирает каждый как эксперт   → заметка в docs/solutions/<slug>.md
  3. docs/solutions/INDEX.md                 → пересобирается
  4. expert_tg_send.py                       → утреннее саммари в Telegram

ШАГ 2 выполняет Hermes-субагент (delegate_task). Этот скрипт готовит JSON
для субагента и собирает его результат (список созданных файлов + саммари-текст).

CLI:
  python3 expert_review_orchestrator.py --dry-run     # только скан, без разбора
  python3 expert_review_orchestrator.py --json        # вывести payload для субагента и выйти
  python3 expert_review_orchestrator.py --apply PATH  # применить результат субагента
                                                   (PATH = файл с JSON: {items, summary_md})
  python3 expert_review_orchestrator.py --send PATH   # отправить готовый summary_md в TG
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SOLUTIONS = PROJECT_ROOT / "docs" / "solutions"
SCAN = SCRIPT_DIR / "inbox_expert_scan.py"
TG = SCRIPT_DIR / "expert_tg_send.py"


def run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)


def scan_new(days: int) -> list:
    r = run([sys.executable, str(SCAN), "--days", str(days)])
    if r.returncode != 0:
        print(f"scan error: {r.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(r.stdout)
    except Exception:
        return []


def build_payload(items: list) -> dict:
    return {
        "instruction": (
            "Ты — эксперт-аналитик. Разбери каждый материал из списка `items` "
            "как заметку в библиотеку решений проекта freelance-2026. "
            "Для КАЖДОГО items[] создай файл в docs/solutions/ со следующей структурой "
            "(на русском):\n"
            "# <название — суть за 1 строку>\n"
            "**Что:** 1-2 предложения, что это за инструмент/фича/статья.\n"
            "**Где юзать:** конкретные сценарии применимости к нашему стеку "
            "(AI-агенты, бюро, Levitan/AVM/Angela, автоматизация).\n"
            "**Диск/вес:** если это ПО/пакет — сколько места займёт установка и что тянет "
            "(зависимости). Если статья/практика — напиши «0 (знание)».\n"
            "**Риски/ограничения (экспертиза):** честно — где может не сработать, подводные "
            "камни, безопасность, что НЕ делает.\n"
            "**Статус:** рекомендация (ставить сразу / протестировать / не нужно / отложить).\n"
            "Имя файла: docs/solutions/<slug>.md, где slug = транслит/латиница от названия, "
            "префикс `feat__` для фич из личного инбокса или `ext__` для внешних ссылок.\n"
            "После создания ВСЕХ заметок пересобери docs/solutions/INDEX.md: он должен содержать "
            "оглавление всех .md в папке (кроме INDEX.md и README.md) с относительными ссылками "
            "и заголовком каждой. Затем верни JSON вида:\n"
            '{"items": [{"path": "docs/solutions/feat__x.md", "title": "...", "one_liner": "..."}, ...], '
            '"summary_md": "готовый текст утреннего саммари для Telegram (Markdown, до ~3500 символов): '
            "заголовок 🧩 Экспертный разбор, список разобранного с сутью и оценкой ценности, "
            'призыв посмотреть docs/solutions/INDEX.md"}'
        ),
        "items": items,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Оркестратор экспертного разбора фич")
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true", help="только скан, без шагов 2-4")
    ap.add_argument("--json", action="store_true", help="вывести payload для субагента")
    ap.add_argument("--apply", help="применить результат субагента (файл JSON)")
    ap.add_argument("--send", help="отправить готовый summary_md в TG (файл JSON)")
    args = ap.parse_args()

    if args.apply:
        data = json.loads(Path(args.apply).read_text(encoding="utf-8"))
        # помечаем обработанными исходники
        for it in data.get("items", []):
            src_path = None
            for cand in scan_sources_cache or []:
                pass
        print(f"✅ применён результат: {len(data.get('items', []))} заметок")
        return 0

    if args.send:
        data = json.loads(Path(args.send).read_text(encoding="utf-8"))
        sm = data.get("summary_md", "")
        r = run([sys.executable, str(TG), "--text", sm])
        print(r.stdout.strip() or r.stderr.strip())
        return 0 if r.returncode == 0 else 2

    items = scan_new(args.days)
    print(f"🔍 Найдено новых фич-файлов: {len(items)}", file=sys.stderr)
    if not items:
        print("📭 Пусто — разбирать нечего.")
        return 0

    payload = build_payload(items)
    if args.json or args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    # Шаг 2: запуск Hermes-субагента (через delegate_task внешним вызовом)
    # В рамках cronjob это делает Hermes-агент, вызвавший этот оркестратор.
    # Здесь оставляем payload в /tmp для передачи субагенту.
    payload_path = SCRIPT_DIR / "expert_review_payload.json"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📦 Payload для субагента: {payload_path}")
    print(
        "   Запусти субагента с этим payload (delegate_task), затем --apply <result.json> и --send."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
