#!/usr/bin/env python3
"""YU-5: anonymize.py — деперсонализация персданных перед облаком.

CLI + библиотека. Заменяет ФИО, паспорта, ИНН, СНИЛС, счета, телефоны,
email на заглушки ФИО_1/ПАСПОРТ_1/... и выдаёт карту замен (заглушка → оригинал).
Карта хранится локально и НЕ уходит в облако.

Использование:
    python3 anonymize.py файл.txt                       # анонимизирует файл → файл.anon.txt + карта.json
    python3 anonymize.py --stdin < договор.txt          # stdin → stdout (только текст)
    python3 anonymize.py --restore карта.json файл.anon.txt   # восстановить оригинал 1:1

Правила (Фемида, правило 4): замена до облака, карта локально, в отчёте только заглушки.
"""

import argparse
import json
import re
import sys
from pathlib import Path

FIO_RE = re.compile(r"\b([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)(?:\s+([А-ЯЁ][а-яё]+))?\b")
PASSPORT_RE = re.compile(r"\b\d{4}\s?\d{6}\b")
INN_RE = re.compile(r"\b\d{10,12}\b")
SNILS_RE = re.compile(r"\b\d{3}-\d{3}-\d{3}\s\d{2}\b")
ACCOUNT_RE = re.compile(r"\b\d{20}\b")
PHONE_RE = re.compile(r"(\+7|8)?[\s(-]*(\d{3})[\s)-]*(\d{3})[\s-]*(\d{2})[\s-]*(\d{2})\b")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")

PATTERNS = [
    ("ПАСПОРТ", PASSPORT_RE),
    ("СНИЛС", SNILS_RE),
    ("ИНН", INN_RE),
    ("СЧЕТ", ACCOUNT_RE),
    ("ТЕЛЕФОН", PHONE_RE),
    ("EMAIL", EMAIL_RE),
    ("ФИО", FIO_RE),
]


def anonymize(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Заменяет ПДн на заглушки. Возвращает (текст, карта замен)."""
    mapping: list[tuple[str, str]] = []
    for label, pat in PATTERNS:
        for i, m in enumerate(re.finditer(pat, text), 1):
            token = f"{label}_{i}"
            text = text.replace(m.group(0), token, 1)
            mapping.append((token, m.group(0)))
    return text, mapping


def restore(text: str, mapping: list[tuple[str, str]]) -> str:
    """Восстанавливает оригинал из заглушек по карте (1:1)."""
    for token, value in mapping:
        text = text.replace(token, value, 1)
    return text


def main():
    ap = argparse.ArgumentParser(description="Деперсонализация персданных")
    ap.add_argument("file", nargs="?", help="файл с ПДн")
    ap.add_argument("--stdin", action="store_true", help="читать stdin, писать stdout")
    ap.add_argument("--restore", metavar="MAP", help="восстановить по карте замен (JSON)")
    args = ap.parse_args()

    if args.restore:
        data = json.loads(Path(args.restore).read_text(encoding="utf-8"))
        mapping = [(t, v) for t, v in zip(data["tokens"], data["values"])]
        text = (
            sys.stdin.read() if args.file is None else Path(args.file).read_text(encoding="utf-8")
        )
        sys.stdout.write(restore(text, mapping))
        return

    text = sys.stdin.read() if args.stdin else Path(args.file).read_text(encoding="utf-8")
    anon, mapping = anonymize(text)
    if args.stdin:
        sys.stdout.write(anon)
        return
    out = Path(args.file).with_suffix(Path(args.file).suffix + ".anon.txt")
    out.write_text(anon, encoding="utf-8")
    map_path = Path(args.file).with_suffix(".map.json")
    map_path.write_text(
        json.dumps(
            {"tokens": [t for t, _ in mapping], "values": [v for _, v in mapping]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"✅ {args.file} → {out} (замен: {len(mapping)})")
    print(f"🗺️  Карта замен: {map_path} — НЕ отправлять в облако!")


if __name__ == "__main__":
    main()
