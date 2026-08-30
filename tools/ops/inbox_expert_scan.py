#!/usr/bin/env python3
"""
inbox_expert_scan.py — детектор новых «фич/инструментов/статей/ссылок»
для экспертного разбора Hermes (дополнение к night_reader.sh + book_digest).

ЧТО ищем: мелкие заметки/ссылки/статьи, которые book_digest НЕ читает
(он берёт только «книги» — файлы >30KB). Сюда попадают: ссылки, статьи,
заметки об инструментах, скриншоты-тексты и т.п.

Откуда берём (источники сканирования):
  - vault/00-Inbox/                        (агентский инбокс)
  - ~/.../Obsidian/Личное/01. Входящие     (личный инбокс, до того как night_reader
                                            переложит его в Фазе 1b)
  - ~/.../Obsidian/Личное/Знания           (куда night_reader кладёт ИИ/маркет/CDP
                                            заметки по имени файла) — основной утренний источник

Исключаем: книги (есть source.md ИЛИ размер >30KB), daily-заметки (YYYY-MM-DD.md),
мусор (*.base, ~$*), уже обработанное (журнал state), личную жизнь
(Кухня/СПОРТ/Кино/Здоровье/Автомобили/Банки — не фичи).

Журнал обработанного: tools/ops/expert_review_state.json (md5 → дата).
Инициализация: --init-state заносит ВСЁ текущее как «уже обработано»,
чтобы не разбирать старый бэклог.

CLI:
  python3 inbox_expert_scan.py                 # новые за сутки → JSON в stdout
  python3 inbox_expert_scan.py --days 3        # окно N дней
  python3 inbox_expert_scan.py --json          # явный JSON (по умолчанию тоже)
  python3 inbox_expert_scan.py --mark PATH...   # пометить обработанными (после разбора)
  python3 inbox_expert_scan.py --init-state     # seed state текущим
  python3 inbox_expert_scan.py --paths-only     # только пути, по одному на строку
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
STATE_FILE = SCRIPT_DIR / "expert_review_state.json"

VAULT_INBOX = PROJECT_ROOT / "vault" / "00-Inbox"
PERSONAL_BASE = (
    Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "Личное"
)
PERSONAL_INBOX = PERSONAL_BASE / "01. Входящие"
PERSONAL_KNOWLEDGE = PERSONAL_BASE / "Знания"
PERSONAL_BOOKS = PERSONAL_BASE / "КНИГИ"

# Папки личной жизни — не разбираем как фичи
LIFE_FOLDERS = ("Кухня", "СПОРТ", "Кино", "Здоровье", "Автомобили", "Банки", "Хочу все знать")

BOOK_MAX_BYTES = 30 * 1024
SCAN_EXTS = {".md", ".txt", ".url", ".webloc", ".html", ".htm", ".textbundle"}

DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$", re.I)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE_FILE)


def md5_of(path: Path) -> str:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".url", ".webloc"):
        return "link"
    if ext in (".html", ".htm"):
        return "page"
    if ext in (".textbundle",):
        return "note"
    return "note"  # .md / .txt


def preview(path: Path, limit: int = 600) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    text = text.strip()
    if len(text) > limit:
        text = text[:limit] + "…"
    return text


def is_book(path: Path) -> bool:
    """Книга ли это (его читает book_digest)?"""
    try:
        if path.stat().st_size > BOOK_MAX_BYTES:
            return True
    except Exception:
        pass
    # В папке КНИГИ с source.md — точно книга
    if "КНИГИ" in str(path) and (path.parent / "source.md").exists():
        return True
    return False


def scan_sources() -> list[Path]:
    dirs = []
    for d in (VAULT_INBOX, PERSONAL_INBOX, PERSONAL_KNOWLEDGE):
        if d.exists() and os.access(str(d), os.R_OK):
            dirs.append(d)
    files: list[Path] = []
    for d in dirs:
        try:
            for f in d.iterdir():
                if not f.is_file():
                    continue
                # исключаем папки личной жизни (только для личного base)
                if "Личное" in str(f) and any(lf in str(f.parent) for lf in LIFE_FOLDERS):
                    continue
                if f.suffix.lower() not in SCAN_EXTS:
                    continue
                if f.name.startswith("."):
                    continue
                if DAILY_RE.match(f.name):
                    continue
                if is_book(f):
                    continue
                files.append(f)
        except Exception as e:
            log(f"⚠️ не могу прочитать {d}: {e}")
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Детектор новых фич-файлов для экспертного разбора")
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--json", action="store_true", help="вывести JSON (по умолчанию)")
    ap.add_argument("--paths-only", action="store_true", help="только пути, по строке")
    ap.add_argument("--mark", nargs="+", default=None, help="пометить обработанными (пути)")
    ap.add_argument("--init-state", action="store_true", help="seed state текущим")
    ap.add_argument("--date", type=str, default=None, help="конкретная дата YYYY-MM-DD")
    args = ap.parse_args()

    state = load_state()

    if args.init_state:
        for f in scan_sources():
            h = md5_of(f)
            if h:
                state[h] = {"path": str(f), "marked": datetime.now().isoformat()}
        save_state(state)
        log(f"💾 init-state: {len(state)} файлов помечены как обработанные")
        return 0

    if args.mark:
        for p in args.mark:
            fp = Path(p)
            h = md5_of(fp)
            if h:
                state[h] = {"path": str(fp), "marked": datetime.now().isoformat()}
        save_state(state)
        log(f"✅ помечено обработанными: {len(args.mark)}")
        return 0

    tdate = date.fromisoformat(args.date) if args.date else date.today()
    cutoff = (tdate - timedelta(days=args.days - 1)).isoformat()

    found = []
    for f in scan_sources():
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
        except Exception:
            continue
        if mtime.date().isoformat() < cutoff:
            continue
        h = md5_of(f)
        if h and h in state:
            continue  # уже разбирали
        rel = str(f)
        bucket = (
            "agent-inbox"
            if "00-Inbox" in rel
            else ("personal-inbox" if "01. Входящие" in rel else "personal-знания")
        )
        found.append(
            {
                "path": str(f),
                "name": f.name,
                "bucket": bucket,
                "kind": classify(f),
                "size": f.stat().st_size,
                "mtime": mtime.isoformat(timespec="seconds"),
                "preview": preview(f),
            }
        )

    found.sort(key=lambda x: x["mtime"])
    if args.paths_only:
        for it in found:
            print(it["path"])
    else:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    log(f"🔍 Новых фич-файлов (за {args.days}д): {len(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
