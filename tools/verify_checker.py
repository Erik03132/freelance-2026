#!/usr/bin/env python3
"""
AV-1: «Проверяла» — независимый проход верификации другой моделью.
Для критических результатов: агент сделал → «Проверяла» подтвердила.

Использование:
    python3 verify_checker.py "результат агента" --model tier2
    python3 verify_checker.py --checklist тест_команда.txt

Форматы:
  --checklist — прогон тест-команды, подтверждение «зелёное» через факт вывода
"""

import argparse
import json
import os
import re
import subprocess
import sys

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
TIER_MODELS = {
    "tier0": "openai/gpt-oss-20b:free",
    "tier1": "google/gemma-4-31b-it:free",
    "tier2": "nvidia/nemotron-3-super-120b-a12b:free",
    "tier3": "nvidia/nemotron-3-ultra-550b-a55b:free",
}

FREE_CASCADE = ["tier2", "tier3", "tier0", "tier1"]

VERIFY_PROMPT = """Ты — независимый проверяющий («Проверяла»). Проверь результат другого агента.
Вердикт: подтверждено (verified) или нет (not_verified). Доказательства — прежде слов.

РЕЗУЛЬТАТ:
---
{result}
---

ПРАВИЛА:
- Подтверждай ТОЛЬКО если результат самодостаточен (код/вывод/данные).
- «Сделано формально, доказательств нет» = НЕ ПОДТВЕРЖДЕНО.
- Fixed ≠ Verified. Проверка должна «уметь краснеть» (валидировать значение, не наличие).

Анти-смещения (обязательно):
1. ДЛИНА НЕ ВАЖНА: длинный красивый ответ ≠ верный. Короткий ответ с фактами сильнее длинного без них.
2. НЕ СОГЛАШАЙСЯ ПО УМОЛЧАНИЮ: не поддакивай ожидаемому результату. Ищи, где можно «покраснеть».
3. СНАЧАЛА ПРИЧИНА, ПОТОМ ЦИФРА: изложи rationale, потом вердикт. НИКОГДА наоборот.
4. ТОЛЬКО ФАКТЫ ИЗ РЕЗУЛЬТАТА: не домысливай доказательства, которых нет в тексте.
5. КРИТЕРИИ БИНАРНЫЕ: каждое требование — «выполнено/не выполнено», без шкал и средних оценок.

Верни JSON:
{{
  "rationale": "ПОСЛЕДОВАТЕЛЬНО: сначала проверка каждого критерия с фактами из результата, потом вывод",
  "status": "verified" | "not_verified",
  "evidence": "что реально подтверждено (цитаты/факты из результата)",
  "missing": ["чего не хватает для верификации"],
  "recommendation": "короткая рекомендация"
}}
Порядок в JSON: rationale ПЕРВЫМ, status после него. Только JSON.
"""


def verify_result(result_text: str, tier: str = "tier2") -> dict:
    if not OPENROUTER_KEY:
        return {"status": "skipped", "error": "OPENROUTER_API_KEY не задан"}

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
                    "messages": [
                        {"role": "user", "content": VERIFY_PROMPT.format(result=result_text)}
                    ],
                    "temperature": 0.1,
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
        except Exception as e:  # noqa: BLE001 — каскад free-моделей
            last_error = f"{t} ({model}): {e}"

    return {"status": "not_verified", "error": f"Все free-модели недоступны: {last_error}"}


def verify_checklist(command: str) -> dict:
    """AV-1: прогон тест-команды. Verified = exit 0 + непустой вывод."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        passed = result.returncode == 0 and bool(stdout)
        return {
            "status": "verified" if passed else "not_verified",
            "command": command,
            "exit_code": result.returncode,
            "stdout": stdout[-500:],
            "stderr": stderr[-300:],
        }
    except subprocess.TimeoutExpired:
        return {"status": "not_verified", "command": command, "error": "timeout"}
    except Exception as e:
        return {"status": "not_verified", "command": command, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="«Проверяла» — независимая верификация")
    ap.add_argument("result", nargs="?", help="текст результата агента")
    ap.add_argument("--model", default="tier2", choices=list(TIER_MODELS.keys()))
    ap.add_argument("--checklist", help="прогнать тест-команду")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.checklist:
        result = verify_checklist(args.checklist)
    elif args.result:
        result = verify_result(args.result, args.model)
    else:
        ap.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = result.get("status")
        print(f"Статус: {'✅ Verified' if status == 'verified' else '❌ ' + str(status)}")
        for k, v in result.items():
            if k != "status":
                print(f"  {k}: {str(v)[:200]}")


if __name__ == "__main__":
    main()
