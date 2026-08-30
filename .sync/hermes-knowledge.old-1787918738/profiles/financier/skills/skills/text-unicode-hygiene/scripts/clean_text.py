#!/usr/bin/env python3
"""Thin CLI over watermarks-remover's text_unicode module.

Layer A only (invisible Unicode + space homoglyphs). stdlib-only, no Docker, no LLM.
Источник модуля: guillaumemeyer/watermarks-remover (MIT).

Примеры:
  python3 clean_text.py inspect input.txt
  python3 clean_text.py clean input.txt -o input.cleaned.txt
  python3 clean_text.py clean input.txt --nfkc --aggressive-homoglyphs
  cat input.txt | python3 clean_text.py clean -
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import text_unicode as tu


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write(path: str | None, text: str) -> None:
    if path is None:
        sys.stdout.write(text)
    else:
        Path(path).write_text(text, encoding="utf-8")


def cmd_inspect(args: argparse.Namespace) -> int:
    text = _read(args.file)
    report = tu.inspect_text(text, aggressive=args.aggressive)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(tu.human_report(report))
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    text = _read(args.file)
    cleaned, stats = tu.clean_text(
        text,
        nfkc=args.nfkc,
        aggressive_homoglyphs=args.aggressive_homoglyphs,
        normalize_spaces=not args.keep_spaces,
        strip_emoji_glue=args.strip_emoji_glue,
        strip_bidi=args.strip_bidi,
    )
    _write(args.output, cleaned)
    if not args.quiet:
        summary = {
            "input_length": stats["input_length"],
            "output_length": stats["output_length"],
            "removed_count": stats["removed_count"],
            "replaced_count": stats["replaced_count"],
            "nfkc_changed": stats["nfkc_changed"],
        }
        print(json.dumps(summary, ensure_ascii=False), file=sys.stderr)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ins = sub.add_parser("inspect", help="Найти невидимые Unicode и homoglyphs в тексте")
    p_ins.add_argument("file", help="путь к файлу или '-' для stdin")
    p_ins.add_argument("--json", action="store_true", help="вывод в JSON")
    p_ins.add_argument("--aggressive", action="store_true", help="искать confusables (кириллица→латиница и т.п.)")
    p_ins.set_defaults(func=cmd_inspect)

    p_clean = sub.add_parser("clean", help="Почистить текст от невидимых символов")
    p_clean.add_argument("file", help="путь к файлу или '-' для stdin")
    p_clean.add_argument("-o", "--output", help="куда писать результат (по умолчанию stdout)")
    p_clean.add_argument("--nfkc", action="store_true", help="дополнительно NFKC-нормализация")
    p_clean.add_argument("--aggressive-homoglyphs", action="store_true", help="заменять кириллические буквы на латинские")
    p_clean.add_argument("--keep-spaces", action="store_true", help="не заменять homoglyph-пробелы на обычные")
    p_clean.add_argument("--strip-emoji-glue", action="store_true", help="снимать ZWJ между эмодзи (сломает ❤️‍🔥)")
    p_clean.add_argument("--strip-bidi", action="store_true", help="снимать bidi-управляющие символы (испортит RTL/LTR смешанный текст)")
    p_clean.add_argument("--quiet", action="store_true", help="не выводить summary в stderr")
    p_clean.set_defaults(func=cmd_clean)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
