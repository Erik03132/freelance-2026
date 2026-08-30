#!/usr/bin/env python3
"""check_hh_links.py — audit HH vacancy links in leads files.

Real HH vacancy URL format: https://hh.ru/vacancy/<digits>
Any textual slug after /vacancy/ (e.g. dalkos_ai_llm) is a FAKE that
redirects to search, NOT a vacancy. This script flags those.

Usage:
  python check_hh_links.py [FILES ...]   # default: common leads files
  python check_hh_links.py --fix         # append [⚠️ ССЫЛКА-ФЕЙК] marker to fake lines

Exit code 0 if no fakes found, 1 if fakes present (pipeline-safe).
"""
import re
import sys
import os

URL_RE = re.compile(r'(https?://[^\s)\]]*hh\.ru/vacancy/[^\s)\]]+)')
DEFAULT_FILES = [
    os.path.expanduser("~/freelance-2026/jobhunter/leads.md"),
    os.path.expanduser("~/freelance-2026/jobhunter/leads_hh_2026-08-26.md"),
]
MARKER = "  [⚠️ ССЫЛКА-ФЕЙК: slug не ведёт к вакансии, уточнить реальный ID]"


def vacancy_tail(url: str) -> str:
    return url.split("/vacancy/")[1].split("?")[0]


def main():
    args = sys.argv[1:]
    do_fix = "--fix" in args
    files = [a for a in args if a != "--fix"] or DEFAULT_FILES

    fake_count = 0
    for fp in files:
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            lines = f.readlines()
        out = []
        file_fakes = 0
        for i, line in enumerate(lines, 1):
            for m in URL_RE.findall(line):
                if not vacancy_tail(m).isdigit():
                    file_fakes += 1
                    fake_count += 1
                    print(f"FAKE  {fp}:{i}  {m}")
            if do_fix and file_fakes and MARKER not in line and line.rstrip().endswith(")"):
                line = line.rstrip() + MARKER + "\n"
            out.append(line)
        if do_fix and file_fakes:
            with open(fp, "w", encoding="utf-8") as f:
                f.writelines(out)
            print(f"  marked {file_fakes} fake link(s) in {fp}")
    print(f"\nTotal fake HH links: {fake_count}")
    sys.exit(1 if fake_count else 0)


if __name__ == "__main__":
    main()
