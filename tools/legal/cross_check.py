"""
YU-6: Авто-кросс-чек Фемиды на другой модели (Tier 2/3).
После генерации отчёта — проверка по ролям: риски / формулировки / пробелы.

Выживает только то, что устроило всех. Расхождения — «спорные пункты».

Использование:
    python3 cross_check.py отчёт.md --model <tier2/tier3>
    python3 cross_check.py отчёт.md --json
"""

import argparse
import json
import os
import re
from pathlib import Path

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

TIER_MODELS = {
    "tier0": "openai/gpt-oss-20b:free",
    "tier1": "google/gemma-4-31b-it:free",
    "tier2": "nvidia/nemotron-3-super-120b-a12b:free",
    "tier3": "nvidia/nemotron-3-ultra-550b-a55b:free",
}

FREE_CASCADE = ["tier2", "tier3", "tier0", "tier1"]

REVIEW_PROMPT = """Ты — независимый юридический рецензент. Проверяешь отчёт другого юриста-аналитика.

Роли проверки:
1. РИСКИ — что пропущено/недооценено?
2. ФОРМУЛИРОВКИ — где неточности, где нет дословной цитаты?
3. ПРОБЕЛЫ — какие нормы/практика упущены?

ОТЧЁТ ДЛЯ РЕЦЕНЗИИ:
---
{report}
---

Анти-смещения (обязательно):
1. ДЛИНА НЕ ВАЖНА: объёмный отчёт ≠ верный отчёт. Оценивай только факты и цитаты.
2. НЕ СОГЛАШАЙСЯ ПО УМОЛЧАНИЮ: если цитата или вывод не подтверждается текстом отчёта — так и скажи.
3. СНАЧАЛА ПРИЧИНА, ПОТОМ ВЕРДИКТ: изложи rationale, потом verdict. НИКОГДА наоборот.
4. КРИТЕРИИ БИНАРНЫЕ: каждое замечание — «подтверждено/не подтверждено фактом», без средних оценок.

Верни JSON (rationale ПЕРВЫМ полем):
{{
  "rationale": "разбор по ролям: что подтвердилось, что нет, с фактами",
  "verdict": "sustainable" | "needs_revision" | "reject",
  "risks_missed": ["..."],
  "inaccurate": ["пункт -> что неточно"],
  "gaps": ["..."],
  "sport_points": ["расхождения между рецензентом и отчётом"]
}}
Только JSON, без markdown.
"""


def review_report(report: str, tier: str = "tier2") -> dict:
    if not OPENROUTER_KEY:
        return {"verdict": "skipped", "error": "OPENROUTER_API_KEY не задан"}

    import urllib.request

    tiers = FREE_CASCADE
    if tier != "tier2":
        tiers = [tier] + [t for t in FREE_CASCADE if t != tier]

    last_error = None
    for t in tiers:
        model = TIER_MODELS[t]
        try:
            body = json.dumps(
                {
                    "model": model,
                    "messages": [{"role": "user", "content": REVIEW_PROMPT.format(report=report)}],
                    "temperature": 0.2,
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                OPENROUTER_URL,
                data=body,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())

            content = data["choices"][0]["message"]["content"]
            clean = re.sub(r"```json|```", "", content).strip()
            result = json.loads(clean)
            result["_model"] = model
            return result
        except Exception as e:  # noqa: BLE001 — каскад: пробуем следующую free-модель
            last_error = f"{t} ({model}): {e}"

    return {"verdict": "reject", "error": f"Все free-модели недоступны: {last_error}"}


def main():
    ap = argparse.ArgumentParser(description="Авто-кросс-чек Фемиды")
    ap.add_argument("report", help="путь к .md отчёту")
    ap.add_argument("--model", default="tier2", choices=list(TIER_MODELS.keys()))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = Path(args.report).read_text(encoding="utf-8")
    result = review_report(report, args.model)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    verdict = result.get("verdict", "?")
    print(f"Вердикт рецензента: {verdict}")
    for label, key in [
        ("Риски упущены", "risks_missed"),
        ("Неточности", "inaccurate"),
        ("Пробелы", "gaps"),
        ("Спорные пункты", "sport_points"),
    ]:
        items = result.get(key, [])
        if items:
            print(f"\n{label}:")
            for item in items:
                print(f"  - {item}")


if __name__ == "__main__":
    main()
