"""Eval suite for trajectory_eval.py (AG-2) — траекторный слой оценки агентов.

Запуск: python3 tests/eval_trajectory.py
Кейсы из статьи «Agentic AI»:
  A (хорошо): lookup_order(123) → ответ
  B (терпимо): search_kb → lookup_order → ответ (лишний виток, recall=1)
  C (плохо): search_kb × 2 → «не знаю» (нужный инструмент не вызван)
  D (ужасно): lookup_order × 3 (зацикливание)
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

from trajectory_eval import TrajectoryEvaluator  # noqa: E402


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # Кейс A: идеально
    r = TrajectoryEvaluator(expected_tools=["lookup_order"], expected_steps=2).evaluate(
        [{"tool": "lookup_order", "args": {"order_id": 123}}]
    )
    if not r["passed"] or r["loop"] or r["recall"] != 1.0 or r["precision"] != 1.0:
        fails.append(f"Кейс A: {r}")

    # Кейс B: лишний виток, но нужный инструмент вызван (терпимо — recall=1, precision=0.5)
    r = TrajectoryEvaluator(expected_tools=["lookup_order"], expected_steps=2).evaluate(
        [
            {"tool": "search_kb", "args": {"query": "заказ 123"}},
            {"tool": "lookup_order", "args": {"order_id": 123}},
        ]
    )
    if r["loop"] or r["recall"] != 1.0 or r["precision"] != 0.5:
        fails.append(f"Кейс B: {r}")
    # steps_ok=True (2 == expected 2) — лишний виток виден в precision, не в шагах

    # Кейс C: нужный инструмент НЕ вызван (плохо, ответ «не знаю»)
    r = TrajectoryEvaluator(expected_tools=["lookup_order"]).evaluate(
        [
            {"tool": "search_kb", "args": {"query": "заказ 123"}},
            {"tool": "search_kb", "args": {"query": "123"}},
        ]
    )
    if r["recall"] != 0.0 or r["tools_missing"] != ["lookup_order"]:
        fails.append(f"Кейс C: {r}")

    # Кейс D: зацикливание (повтор пары подряд)
    r = TrajectoryEvaluator(expected_tools=["lookup_order"]).evaluate(
        [
            {"tool": "lookup_order", "args": {"order_id": 123}},
            {"tool": "lookup_order", "args": {"order_id": 123}},
            {"tool": "lookup_order", "args": {"order_id": 123}},
        ]
    )
    if not r["loop"] or r["loop_position"] != 2:
        fails.append(f"Кейс D: {r}")

    # Зацикливание НЕ детектится на разных аргументах
    r = TrajectoryEvaluator(expected_tools=["lookup_order"]).evaluate(
        [
            {"tool": "lookup_order", "args": {"order_id": 1}},
            {"tool": "lookup_order", "args": {"order_id": 2}},
            {"tool": "lookup_order", "args": {"order_id": 3}},
        ]
    )
    if r["loop"]:
        fails.append(f"Ложное зацикливание: {r}")

    # Порядок: in-order — эталонная последовательность содержится в фактической
    r = TrajectoryEvaluator(
        expected_calls=[{"tool": "auth"}, {"tool": "get_data"}], order_mode="in-order"
    ).evaluate(
        [
            {"tool": "auth", "args": {}},
            {"tool": "cache_get", "args": {}},
            {"tool": "get_data", "args": {}},
        ]
    )
    if not r["order_ok"]:
        fails.append(f"in-order должен пройти с лишней вставкой: {r}")

    # Порядок: exact — лишняя вставка ломает
    r = TrajectoryEvaluator(
        expected_calls=[{"tool": "auth"}, {"tool": "get_data"}], order_mode="exact"
    ).evaluate(
        [
            {"tool": "auth", "args": {}},
            {"tool": "cache_get", "args": {}},
            {"tool": "get_data", "args": {}},
        ]
    )
    if r["order_ok"]:
        fails.append(f"exact должен упасть с лишней вставкой: {r}")

    # Порядок: exact — точное совпадение проходит
    r = TrajectoryEvaluator(
        expected_calls=[{"tool": "auth"}, {"tool": "get_data"}], order_mode="exact"
    ).evaluate([{"tool": "auth", "args": {}}, {"tool": "get_data", "args": {}}])
    if not r["order_ok"]:
        fails.append(f"exact точное совпадение: {r}")

    # Аргументы: непустой tool + args словарь
    r = TrajectoryEvaluator(expected_tools=["x"]).evaluate([{"tool": "", "args": {}}])
    if r["args_ok"] or r["passed"]:
        fails.append(f"пустой tool должен быть провалом: {r}")

    # CLI-парсер: строковый формат tool(args)
    from trajectory_eval import _parse_calls

    calls = _parse_calls('lookup_order({"order_id": 123}); search_kb()')
    if calls != [
        {"tool": "lookup_order", "args": {"order_id": 123}},
        {"tool": "search_kb", "args": {}},
    ]:
        fails.append(f"_parse_calls: {calls}")

    # JSON-формат CLI
    calls = _parse_calls('[{"tool": "a", "args": {}}]')
    if calls != [{"tool": "a", "args": {}}]:
        fails.append(f"_parse_calls JSON: {calls}")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — траекторный слой (loop/precision/recall/order/args) работает")
