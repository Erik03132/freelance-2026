#!/usr/bin/env python3
"""
check_hh_links.py — аудит HH-ссылок в файлах leads.

Проверяет каждую hh.ru/vacancy/<...> ссылку: реальная вакансия ТОЛЬКО если
часть после /vacancy/ состоит из цифр (https://hh.ru/vacancy/<цифры>).
Любой текстовый slug (dalkos_ai_llm, ai_data_python_dev ...) — ФЕЙК:
он ведёт на поиск, а не на вакансию.

CP-1 (cli-for-agent): флаги, --help с примерами, --dry-run не нужен
(только чтение), идемпотентен, явные ошибки, pipeline-safe.

Примеры:
  python3 check_hh_links.py --file ../leads.md
  python3 check_hh_links.py --file leads.md --file other.md
  cat leads.md | python3 check_hh_links.py   # stdin
"""
import argparse
import re
import sys

URL_RE = re.compile(r'https?://(?:[a-z0-9.-]*\.)?hh\.ru/vacancy/([^)\s"\']+)')
EXIT_OK = 0
EXIT_FOUND_FAKE = 1
EXIT_ERROR = 2


def audit_text(text: str):
    """Возвращает список (url, tail, is_valid)."""
    results = []
    for m in URL_RE.finditer(text):
        tail = m.group(1).split('?')[0].split('#')[0]
        is_valid = tail.isdigit()
        results.append((m.group(0), tail, is_valid))
    return results


def main():
    ap = argparse.ArgumentParser(
        description="Аудит HH-ссылок: валидно только hh.ru/vacancy/<цифры>.",
        epilog='Примеры:\n'
               '  python3 check_hh_links.py --file ../leads.md\n'
               '  cat leads.md | python3 check_hh_links.py\n',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--file', action='append', default=[],
                    help='Путь к файлу leads (можно несколько раз).')
    args = ap.parse_args()

    texts = []
    if args.file:
        for path in args.file:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    texts.append((path, f.read()))
            except OSError as e:
                print(f"ОШИБКА чтения {path}: {e}", file=sys.stderr)
                sys.exit(EXIT_ERROR)
    else:
        data = sys.stdin.read()
        texts.append(("<stdin>", data))

    total = 0
    fakes = 0
    has_fake = False
    for src, content in texts:
        rows = audit_text(content)
        if not rows:
            continue
        print(f"\n=== {src} ({len(rows)} ссылок) ===")
        for url, tail, is_valid in rows:
            total += 1
            if is_valid:
                print(f"  [OK]    {url}")
            else:
                fakes += 1
                has_fake = True
                print(f"  [FAKE]  {url}  (slug '{tail}' не ведёт к вакансии)")
    print(f"\nИтого: {total} ссылок, фейк-slug: {fakes}")
    sys.exit(EXIT_FOUND_FAKE if has_fake else EXIT_OK)


if __name__ == '__main__':
    main()
