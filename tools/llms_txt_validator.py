#!/usr/bin/env python3
"""LL-1 — Детерминированный валидатор llms.txt (урок Habr #1070334).

Спецификация (llmstxt.org, Дж. Ховард): H1 первой значимой строкой (ровно 1) →
`> Описание` цитатой сразу под заголовком → `## Секции` с буллетами
`- [Name](url): пояснение`. Сеть НЕ трогаем — валидируем структуру текста.

Архитектура (как в статье): parse_llms_txt (парсер, сохраняет ПОРЯДОК) отдельно
от validate_llms_txt (правила со SEVERITY_WEIGHT, score = 100 − Σ весов).

Использование:
    python3 tools/llms_txt_validator.py path/to/llms.txt
    python3 tools/llms_txt_validator.py --json < llms.txt

Офлайн: `python3 tools/tests/eval_llms_txt.py` (deterministic, для eval_gate).
"""

from __future__ import annotations

import argparse
import json
import re
import sys

SEVERITY_WEIGHT = {"critical": 40, "high": 25, "medium": 12, "low": 5}

_H1 = re.compile(r"^#\s+\S")
_H2 = re.compile(r"^##\s+\S")
_BULLET_OK = re.compile(r"^-\s+\[[^\]]+\]\([^)]+\)")


def parse_llms_txt(text: str) -> dict:
    """Парсит текст в структуру. Сохраняет порядок (нарушается чаще всего)."""
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")

    first_idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if first_idx is None:
        return {
            "title": None, "title_is_first": False, "h1_count": 0,
            "description": None, "description_before_title": False,
            "sections": [], "malformed_entries": [], "stray_lines": [],
        }

    h1_count = sum(1 for ln in lines if _H1.match(ln))
    ti = next((i for i, ln in enumerate(lines) if _H1.match(ln)), None)
    title_is_first = ti is not None and ti == first_idx
    title = lines[ti].lstrip("#").strip() if title_is_first else None

    # описание до заголовка: цитата встретилась выше строки с H1
    description_before_title = ti is not None and any(
        lines[k].strip().startswith(">") for k in range(ti)
    )

    # описание = блочная цитата сразу после заголовка
    description = None
    i = (ti + 1) if ti is not None else first_idx + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith(">"):
        description = lines[i].lstrip()[1:].strip()
        i += 1

    sections: list[dict] = []
    in_section = False
    cur = None
    malformed: list[str] = []
    stray: list[str] = []

    for ln in lines[i:]:
        s = ln.strip()
        if not s:
            continue
        if _H2.match(ln):
            cur = {"name": ln.lstrip("#").strip(), "entries": []}
            sections.append(cur)
            in_section = True
            continue
        if in_section:
            if s.startswith("-"):
                if _BULLET_OK.match(ln):
                    cur["entries"].append(s)
                else:
                    malformed.append(s)
            else:
                stray.append(s)
        else:
            if not s.startswith("#"):
                stray.append(s)

    return {
        "title": title,
        "title_is_first": title_is_first,
        "h1_count": h1_count,
        "description": description,
        "description_before_title": description_before_title,
        "sections": sections,
        "malformed_entries": malformed,
        "stray_lines": stray,
    }


def validate_llms_txt(text: str) -> dict:
    """Прогоняет структуру по правилам. Возвращает {score, findings, parsed}."""
    p = parse_llms_txt(text)
    findings: list[dict] = []

    def add(sev: str, check: str, msg: str) -> None:
        findings.append({"severity": sev, "check": check, "weight": SEVERITY_WEIGHT[sev], "message": msg})

    if not text or not text.strip():
        add("critical", "empty", "файл пустой — читать нечего")
    elif p["h1_count"] == 0:
        add("critical", "no_h1", "нет H1 — читать нечего")

    if p["h1_count"] > 1:
        add("high", "multiple_h1", f"более одного H1: {p['h1_count']}")
    if p["h1_count"] > 0 and not p["title_is_first"]:
        add("high", "title_not_first", "H1 не первой значимой строкой")
    if p["description_before_title"]:
        add("high", "description_before_title", "описание стоит раньше заголовка")

    if p["h1_count"] > 0 and p["title_is_first"] and p["description"] is None:
        add("medium", "no_description", "нет описания цитатой сразу под заголовком")
    if p["malformed_entries"]:
        add("medium", "malformed_bullets", f"битый формат буллета: {len(p['malformed_entries'])}")
    if p["stray_lines"]:
        add("medium", "stray_text", f"посторонний текст вне буллетов: {len(p['stray_lines'])}")

    if re.search(r"\(http://", text or ""):
        add("low", "http_link", "ссылки на http:// вместо https://")

    score = 100 - sum(f["weight"] for f in findings)
    # critical (пусто/нет H1) = читать нечего → принудительно красная зона
    if any(f["severity"] == "critical" for f in findings):
        score = 0
    if score < 0:
        score = 0
    return {"score": score, "findings": findings, "parsed": p}


def main():
    ap = argparse.ArgumentParser(description="LL-1 llms.txt validator")
    ap.add_argument("path", nargs="?", help="путь к llms.txt (иначе stdin)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.path:
        with open(args.path, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    rep = validate_llms_txt(text)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return
    print(f"Score: {rep['score']}/100")
    for f in rep["findings"]:
        print(f"  [{f['severity'].upper()} -{f['weight']}] {f['message']}")
    print("✅ llms.txt валиден" if not rep["findings"] else "❌ llms.txt имеет нарушения")


if __name__ == "__main__":
    main()
