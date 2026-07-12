#!/usr/bin/env python3
"""GeekNeural CLI — интерфейс к ядру для shell-hook и ручных вызовов.

Примеры:
  gn read path/to/file.py            # дедуп-чтение (выводит контент или ссылку)
  gn read path/to/file.py --force    # принудительно полное содержимое
  gn read-text "..." --key mykey     # дедуп произвольного текста
  gn stats                           # сводка по сессии (экономия токенов)
  gn clear                           # сброс кеша сессии
"""
from __future__ import annotations

import argparse
import json
import sys

from core.dedup import DedupEngine, session_from_env


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gn", description="GeekNeural token dedup CLI")
    ap.add_argument("--session", default=None, help="session id (иначе $GEEKNEURAL_SESSION)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_read = sub.add_parser("read", help="дедуп-чтение файла")
    p_read.add_argument("path")
    p_read.add_argument("--force", action="store_true")
    p_read.add_argument("--json", action="store_true", help="выводить JSON, а не сырой контент")

    p_rt = sub.add_parser("read-text", help="дедуп произвольного текста")
    p_rt.add_argument("text")
    p_rt.add_argument("--key", required=True)
    p_rt.add_argument("--force", action="store_true")
    p_rt.add_argument("--json", action="store_true")

    sub.add_parser("stats", help="сводка экономии по сессии")
    sub.add_parser("clear", help="сброс кеша сессии")

    args = ap.parse_args(argv)
    sid = args.session or session_from_env()
    eng = DedupEngine(sid)

    if args.cmd == "read":
        res = eng.read(args.path, force=args.force)
        if args.json:
            print(json.dumps({"content": res.content, "ref": res.ref,
                              "deduped": res.deduped, "bytes_sent": res.bytes_sent,
                              "ref_count": res.ref_count, "reason": res.reason},
                             ensure_ascii=False))
        else:
            sys.stdout.write(res.content)
            if not res.content.endswith("\n"):
                sys.stdout.write("\n")
        return 0

    if args.cmd == "read-text":
        res = eng.read_text(args.text, args.key, force=args.force)
        if args.json:
            print(json.dumps({"content": res.content, "ref": res.ref,
                              "deduped": res.deduped, "bytes_sent": res.bytes_sent,
                              "ref_count": res.ref_count, "reason": res.reason},
                             ensure_ascii=False))
        else:
            sys.stdout.write(res.content)
            sys.stdout.write("\n")
        return 0

    if args.cmd == "stats":
        print(json.dumps(eng.stats_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "clear":
        n = eng.clear_session()
        print(json.dumps({"cleared": n}, ensure_ascii=False))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
