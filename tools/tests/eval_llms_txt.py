"""Eval for LL-1 llms.txt validator — offline, deterministic.

Запуск: python3 tools/tests/eval_llms_txt.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.llms_txt_validator import parse_llms_txt, validate_llms_txt  # noqa: E402


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    VALID = (
        "# My Project\n"
        "> Описание проекта на естественном языке.\n"
        "## Документация\n"
        "- [Guide](https://example.com/guide): подробное руководство\n"
        "- [API](https://example.com/api)\n"
        "## Контакты\n"
        "- [Email](https://example.com/contact): связь\n"
    )
    r = validate_llms_txt(VALID)
    if r["score"] != 100 or r["findings"]:
        fails.append(f"VALID должен дать 100/0: {r}")
    pr = parse_llms_txt(VALID)
    if not pr["title_is_first"] or pr["h1_count"] != 1 or pr["description"] is None:
        fails.append(f"VALID parse неверен: {pr}")
    if len(pr["sections"]) != 2:
        fails.append(f"VALID: ожидали 2 секции, получили {len(pr['sections'])}")

    # пусто -> critical, score 0
    r = validate_llms_txt("")
    if not any(f["severity"] == "critical" for f in r["findings"]) or r["score"] != 0:
        fails.append(f"EMPTY: ожидали critical/score 0: {r}")

    # только пробелы -> critical
    r = validate_llms_txt("   \n  \n")
    if not any(f["check"] == "empty" for f in r["findings"]):
        fails.append(f"WHITESPACE: ожидали empty: {r}")

    # \r\n смесь парсится корректно
    r = validate_llms_txt("# T\r\n> d\r\n## S\r\n- [X](https://e.com)\r\n")
    if r["score"] != 100:
        fails.append(f"CRLF: ожидали 100: {r}")

    # два H1 -> high
    r = validate_llms_txt("# A\n> d\n# B\n## S\n- [X](https://e.com)")
    if not any(f["check"] == "multiple_h1" for f in r["findings"]):
        fails.append(f"TWO_H1: ожидали multiple_h1: {r}")

    # описание до заголовка -> high
    r = validate_llms_txt("> описание раньше\n# Title\n## S\n- [X](https://e.com)")
    if not any(f["check"] == "description_before_title" for f in r["findings"]):
        fails.append(f"DESC_BEFORE: ожидали description_before_title: {r}")

    # H1 не первый (проза перед) -> high
    r = validate_llms_txt("проза спереди\n# Title\n> d\n## S\n- [X](https://e.com)")
    if not any(f["check"] == "title_not_first" for f in r["findings"]):
        fails.append(f"TITLE_NOT_FIRST: ожидали title_not_first: {r}")

    # описание не цитатой -> medium no_description
    r = validate_llms_txt("# Title\nобычный абзац вместо цитаты\n## S\n- [X](https://e.com)")
    if not any(f["check"] == "no_description" for f in r["findings"]):
        fails.append(f"NO_DESC: ожидали no_description: {r}")

    # битый буллет -> medium
    r = validate_llms_txt("# T\n> d\n## S\n- не ссылка, просто текст")
    if not any(f["check"] == "malformed_bullets" for f in r["findings"]):
        fails.append(f"MALFORMED: ожидали malformed_bullets: {r}")

    # посторонний текст в секции -> medium
    r = validate_llms_txt("# T\n> d\n## S\nлишний абзац внутри секции\n- [X](https://e.com)")
    if not any(f["check"] == "stray_text" for f in r["findings"]):
        fails.append(f"STRAY: ожидали stray_text: {r}")

    # http:// -> low
    r = validate_llms_txt("# T\n> d\n## S\n- [X](http://example.com)")
    if not any(f["check"] == "http_link" for f in r["findings"]):
        fails.append(f"HTTP: ожидали http_link: {r}")

    # веса корректны (critical=40)
    r = validate_llms_txt("нет H1 вообще")
    if not any(f["severity"] == "critical" and f["weight"] == 40 for f in r["findings"]):
        fails.append(f"WEIGHT: ожидали critical weight 40: {r}")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — LL-1 llms.txt validator (parse+validate, edge cases OK)")
