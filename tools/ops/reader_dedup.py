#!/usr/bin/env python3
"""
Дедупликация ночного читателя.

Хранит md5 контента уже обработанных книг/ссылок в JSON-журнале.
Одни и те же книги/URL (одинаковый md5) больше НЕ обрабатываются.

Журнал: tools/data/reader_done.json
   {"md5": {"slug": "...", "date": "YYYY-MM-DD", "size": 1234}}

CLI:
  reader_dedup.py --check <md5>          # rc=0 если уже обработан, rc=1 если нет
  reader_dedup.py --add <md5> <slug>     # занести в журнал
  reader_dedup.py --has <file>           # вычислить md5 файла и проверить (rc=0 - дубль)
  reader_dedup.py --stats                # количество записей
"""

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JOURNAL = DATA_DIR / "reader_done.json"


def load() -> dict:
    if not JOURNAL.exists():
        return {}
    try:
        return json.loads(JOURNAL.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def file_md5(p: Path) -> str:
    """md5 нормализованного содержимого: CR (Windows переносы) игнорируются,
    чтобы rsync/VPS-копии не выглядели как разные книги."""
    h = hashlib.md5()
    with open(p, "rb") as f:
        # строковый режим с universal newline
        for raw in iter(lambda: f.read(1 << 20), b""):
            h.update(raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", type=str, default=None, help="md5 для проверки")
    ap.add_argument("--add", nargs=2, metavar=("MD5", "SLUG"), default=None)
    ap.add_argument("--has", type=str, default=None, help="файл: md5 -> проверить")
    ap.add_argument("--file", type=str, default=None, help="файл для вычисления md5")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    if args.stats:
        d = load()
        print(f"записей: {len(d)}")
        return 0

    if args.has:
        md5 = file_md5(Path(args.has))
        d = load()
        if md5 in d:
            print(f"DUPLICATE md5={md5} first={d[md5]['date']}")
            return 0
        print(f"UNIQUE md5={md5}")
        return 1

    if args.file:
        print(file_md5(Path(args.file)))
        return 0

    if args.check:
        d = load()
        if args.check in d:
            print(f"DUPLICATE (в журнале от {d[args.check]['date']})")
            return 0
        print("UNIQUE")
        return 1

    if args.add:
        md5, slug = args.add
        d = load()
        d[md5] = {"slug": slug, "date": date.today().isoformat()}
        save(d)
        print(f"добавлено: {slug} ({md5[:8]}…)")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
