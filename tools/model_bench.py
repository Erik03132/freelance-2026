#!/usr/bin/env python3
"""HZ-5 — Model Benchmark Harness (Mini-SWE "Bash Only" contract).

По уроку Habr #1070296: цифра агентного бенчмарка = model + harness. Чтобы
честно сравнивать МОДЕЛИ, фиксируем минимальную поверхность инструментов
(только `bash`, без редакторов/веба/агент-скаффолда) и гоним одинаковую
задачу по моделям. Разница между прогонами — вклад МОДЕЛИ, не обвязки.

Контракт (DSH-5 Minimal-mode):
  - доступен ровно один инструмент: `bash` (subprocess, temp dir, timeout);
  - модель решает задачу bash-командами, без внешних вызовов агента;
  - верификатор детерминирован и офлайн (subprocess в sandbox).

Офлайн: `python3 tools/model_bench.py --selftest` (pure, для eval_gate).
Лайв:    `python3 tools/model_bench.py --live --models deepseek/...` (нужен
         OPENAI_BASE_URL + OPENAI_API_KEY, наш OmniRoute).

Без live-ключа офлайн-часть валидирует механику харнесса (верификатор +
контракт), не делая сетевых вызовов.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

# --- Контракт: единственный доступный инструмент ---
MINIMAL_TOOL_SURFACE = "bash"

# Модели по умолчанию (FREE_MODELS cascade); переопределяется --models.
DEFAULT_MODELS = [
    "deepseek/deepseek-chat",
    "openrouter/meta-llama/llama-3.3-70b-instruct",
    "openrouter/google/gemini-flash-1.5",
]


def _run_bash(solution: str, timeout: int = 30) -> tuple[int, str, str]:
    """Исполняет решение модели как bash-скрипт в изолированной temp-директории."""
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, "solution.sh")
        with open(script, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\nset -euo pipefail\n")
            f.write(solution)
        try:
            p = subprocess.run(
                ["bash", script], cwd=d, capture_output=True, text=True, timeout=timeout
            )
            return p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired:
            return 124, "", "timeout"


# (id, prompt, verify(stdout, stderr, rc) -> (passed: bool, score: int))
TASKS: list[tuple[str, str, callable]] = [
    (
        "hello_world",
        "Выведи ровно одну строку: HELLO",
        lambda out, err, rc: (
            out.strip() == "HELLO" and rc == 0,
            1 if out.strip() == "HELLO" else 0,
        ),
    ),
    (
        "reverse_string",
        "Выведи строку 'abcdef' в обратном порядке (fedcba).",
        lambda out, err, rc: (
            out.strip() == "fedcba" and rc == 0,
            1 if out.strip() == "fedcba" else 0,
        ),
    ),
    (
        "sum_range",
        "Выведи сумму целых чисел от 1 до 10 (одно число).",
        lambda out, err, rc: (out.strip() == "55" and rc == 0, 1 if out.strip() == "55" else 0),
    ),
]


def run_solution(task: tuple, bash_solution: str) -> dict:
    """Прогоняет bash-решение по задаче. Детерминировано, офлайн."""
    tid, prompt, verify = task
    rc, out, err = _run_bash(bash_solution)
    passed, score = verify(out, err, rc)
    return {"task": tid, "passed": passed, "score": score, "rc": rc, "stdout": out.strip()[:120]}


def compare_models(results: dict[str, list[dict]]) -> list[dict]:
    """Сводит результаты по моделям. Pure — для таблицы/отчёта."""
    rows = []
    for model, runs in results.items():
        total = len(runs)
        passed = sum(1 for r in runs if r["passed"])
        score = sum(r["score"] for r in runs)
        rows.append({"model": model, "passed": passed, "total": total, "score": score})
    rows.sort(key=lambda r: (-r["score"], -r["passed"]))
    return rows


def call_model(prompt: str, model: str) -> str:
    """Лайв-вызов модели через OpenAI-совместимый endpoint (OmniRoute)."""
    base = os.environ.get("OPENAI_BASE_URL")
    key = os.environ.get("OPENAI_API_KEY")
    if not base or not key:
        raise RuntimeError("Для --live нужны OPENAI_BASE_URL и OPENAI_API_KEY (OmniRoute)")
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("pip install openai для --live режима")
    client = OpenAI(base_url=base, api_key=key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"Ты решаешь задачу ТОЛЬКО через bash. Инструмент: {MINIMAL_TOOL_SURFACE}.",
            },
            {
                "role": "user",
                "content": prompt + "\nВерни ТОЛЬКО bash-скрипт в блоке ```bash ... ```.",
            },
        ],
        timeout=60,
    )
    return resp.choices[0].message.content or ""


def _extract_bash(text: str) -> str:
    import re

    m = re.search(r"```bash\s*(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def run_bench(models: list[str]) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    for model in models:
        runs = []
        for task in TASKS:
            try:
                sol = _extract_bash(call_model(task[1], model))
                runs.append(run_solution(task, sol))
            except Exception as e:  # noqa: BLE001
                runs.append({"task": task[0], "passed": False, "score": 0, "error": str(e)[:120]})
        results[model] = runs
    return results


def selftest() -> int:
    fails = []
    # Контракт: единственный инструмент — bash
    if MINIMAL_TOOL_SURFACE != "bash":
        fails.append("CONTRACT: MINIMAL_TOOL_SURFACE != 'bash'")
    # TP: верное решение проходит
    good = run_solution(TASKS[0], "echo HELLO")
    if not good["passed"] and not good["score"]:
        fails.append("TP MISS: верное решение hello_world не прошло")
    # TP: неверное решение падает
    bad = run_solution(TASKS[0], "echo WRONG")
    if bad["passed"] or bad["score"]:
        fails.append("FP: неверное решение прошло верификацию")
    # compare_models корректно сортирует по score
    rows = compare_models(
        {"m1": [{"passed": True, "score": 1}], "m2": [{"passed": False, "score": 0}]}
    )
    if rows[0]["model"] != "m1":
        fails.append("compare_models: сортировка по score сломана")
    if fails:
        print("❌ MODEL_BENCH SELFTEST FAILED:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(
        f"✅ MODEL_BENCH SELFTEST PASSED — контракт bash-only OK, {len(TASKS)} задач, верификатор+сводка OK"
    )
    return 0


def main():
    ap = argparse.ArgumentParser(description="HZ-5 Model Benchmark Harness (Bash Only)")
    ap.add_argument(
        "--selftest", action="store_true", help="Офлайн-проверка механики (для eval_gate)"
    )
    ap.add_argument(
        "--live", action="store_true", help="Лайв-прогон по моделям (нужен OPENAI_BASE_URL+KEY)"
    )
    ap.add_argument(
        "--models", nargs="*", default=None, help="Список моделей (иначе DEFAULT_MODELS)"
    )
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if args.live:
        models = args.models or DEFAULT_MODELS
        res = run_bench(models)
        print(
            json.dumps(
                {"tool_surface": MINIMAL_TOOL_SURFACE, "results": compare_models(res)},
                ensure_ascii=False,
                indent=2,
            )
        )
        sys.exit(0)
    print("Используй --selftest (офлайн) или --live (нужен OPENAI_BASE_URL+OPENAI_API_KEY).")
    sys.exit(2)


if __name__ == "__main__":
    main()
