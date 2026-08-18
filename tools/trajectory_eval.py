#!/usr/bin/env python3
"""
AG-2: Траекторный слой оценки агентов (по статье «Agentic AI: стек агентного инженера»).

Оценивает НЕ ответ, а путь агента: какие инструменты вызвал, в каком порядке,
с какими аргументами, сколько витков, не зациклился ли.

Слои (от дешёвого к дорогому):
1. Зацикливание — повтор пары (tool, args) подряд → fail. БЕСПЛАТНО, без LLM.
2. Витки vs эталон — steps vs expected_steps, доля решённых за минимум.
3. Precision/Recall по инструментам — нужные позваны? лишних сколько?
4. Порядок вызовов — exact / in-order / any-order сравнение с эталоном.
5. Аргументы — синтаксис (схема) и семантика (опционально LLM-судья, узкий вопрос).

Использование:
    python3 trajectory_eval.py --calls '{"tool": "lookup_order", "args": {"order_id": 123}}' ... --expected '...' --expected-steps 2

    # как модуль:
    from trajectory_eval import TrajectoryEvaluator
    ev = TrajectoryEvaluator(expected_tools=["lookup_order"], expected_steps=2)
    r = ev.evaluate([{"tool": "search_kb", "args": {"query": "заказ 123"}},
                     {"tool": "lookup_order", "args": {"order_id": 123}}])
    # → {"loop": false, "steps": 2, "precision": 1.0, "recall": 1.0, "order": "any-ok", "passed": true}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys


class TrajectoryEvaluator:
    """Оценка траектории вызовов инструментов агента."""

    def __init__(
        self,
        expected_tools: list[str] | None = None,
        expected_calls: list[dict] | None = None,
        expected_steps: int | None = None,
        order_mode: str = "any-order",
    ):
        """
        expected_tools — какие инструменты ДОЛЖНЫ быть вызваны (для precision/recall).
        expected_calls — эталонная последовательность вызовов (для exact/in-order).
        expected_steps — ожидаемое число витков (для эффективности пути).
        order_mode   — 'any-order' | 'in-order' | 'exact'.
        """
        self.expected_tools = expected_tools or []
        self.expected_calls = expected_calls or []
        self.expected_steps = expected_steps
        self.order_mode = order_mode

    def evaluate(self, calls: list[dict]) -> dict:
        """calls — список {'tool': str, 'args': dict}. Возвращает отчёт."""
        loop_found, loop_pos = self._detect_loop(calls)
        used_tools = [c.get("tool", "") for c in calls]
        used_set = set(used_tools)
        exp_set = set(self.expected_tools)

        tp = len(used_set & exp_set)
        precision = tp / len(used_set) if used_set else 0.0
        recall = tp / len(exp_set) if exp_set else 1.0

        steps = len(calls)
        steps_ok = True
        if self.expected_steps is not None:
            steps_ok = steps <= self.expected_steps

        order_ok = self._check_order(calls)
        args_ok = self._check_args(calls)

        issues = []
        if loop_found:
            issues.append(f"зацикливание: повтор пары (tool,args) на витке {loop_pos}")
        if not order_ok:
            issues.append(f"порядок вызовов не совпал с эталоном ({self.order_mode})")
        if not args_ok:
            issues.append("аргументы не прошли синтаксическую проверку")
        if not steps_ok:
            issues.append(f"витков {steps} > эталона {self.expected_steps}")

        return {
            "loop": loop_found,
            "loop_position": loop_pos,
            "steps": steps,
            "expected_steps": self.expected_steps,
            "steps_ok": steps_ok,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "order_mode": self.order_mode,
            "order_ok": order_ok,
            "args_ok": args_ok,
            "tools_used": used_tools,
            "tools_missing": sorted(exp_set - used_set),
            "tools_extra": sorted(used_set - exp_set),
            "issues": issues,
            "passed": not issues,
        }

    def _detect_loop(self, calls: list[dict]) -> tuple[bool, int | None]:
        """Повтор пары (tool, args) подряд — красный флаг. Без LLM."""
        prev_key = None
        for i, c in enumerate(calls, start=1):
            key = json.dumps({"t": c.get("tool"), "a": c.get("args")}, sort_keys=True)
            if key == prev_key:
                return True, i
            prev_key = key
        return False, None

    def _check_order(self, calls: list[dict]) -> bool:
        if not self.expected_calls:
            return True
        used = [c.get("tool", "") for c in calls]
        expected = [c.get("tool", "") for c in self.expected_calls]
        if self.order_mode == "exact":
            return used == expected
        if self.order_mode == "in-order":
            it = iter(used)
            return all(any(e == x for x in it) for e in expected)
        # any-order: только набор инструментов
        return True

    def _check_args(self, calls: list[dict]) -> bool:
        """Синтаксическая проверка: args — словарь (не строка/None), tool — непустой."""
        for c in calls:
            if not c.get("tool"):
                return False
            args = c.get("args")
            if args is not None and not isinstance(args, dict):
                return False
        return True

    # --- BK-1: целостность траектории (урок BookTrans, Habr #1070088) ---
    # Каждому блоку (вызову) присваивается стабильный ID и хеш содержимого.
    # Replay (resume/fork) НЕ проходит, если хеш хоть одного блока изменился
    # (детекция drift/тамперинга траектории).

    @staticmethod
    def _block_hash(call: dict) -> str:
        canonical = json.dumps(
            {"t": call.get("tool"), "a": call.get("args")}, sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def seal(self, calls: list[dict]) -> list[dict]:
        """Подписывает траекторию: стабильный block_id + content hash на каждый блок."""
        sealed = []
        for i, c in enumerate(calls):
            sealed.append(
                {
                    "block_id": f"b{i:04d}",
                    "tool": c.get("tool", ""),
                    "args": c.get("args", {}),
                    "hash": self._block_hash(c),
                }
            )
        return sealed

    def verify_integrity(self, sealed: list[dict], replay_calls: list[dict]) -> dict:
        """Проверяет replay против подписанной траектории по block_id+hash.

        Replay НЕ проходит, если длина отличается или хеш любого блока изменился.
        Возвращает {integrity_ok, length_match, mismatches:[{block_id, sealed_hash, replay_hash}]}.
        """
        replay_sealed = self.seal(replay_calls)
        mismatches = []
        for i, block in enumerate(sealed):
            if i >= len(replay_sealed):
                break
            rh = replay_sealed[i]["hash"]
            if block["hash"] != rh:
                mismatches.append(
                    {"block_id": block["block_id"], "sealed_hash": block["hash"], "replay_hash": rh}
                )
        length_match = len(sealed) == len(replay_sealed)
        return {
            "integrity_ok": length_match and not mismatches,
            "length_match": length_match,
            "sealed_len": len(sealed),
            "replay_len": len(replay_sealed),
            "mismatches": mismatches,
        }


def _parse_calls(raw: str) -> list[dict]:
    """Парсит JSON-массив вызовов или строки вида tool(args)."""
    raw = raw.strip()
    if raw.startswith("["):
        return json.loads(raw)
    calls = []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if "(" in part:
            name, _, rest = part.partition("(")
            args = rest.rstrip(")")
            calls.append({"tool": name.strip(), "args": json.loads(args) if args else {}})
        else:
            calls.append({"tool": part, "args": {}})
    return calls


def main():
    ap = argparse.ArgumentParser(description="Траекторная оценка агента (AG-2)")
    ap.add_argument(
        "--calls",
        required=True,
        help='вызовы агента: [{"tool":"x","args":{}},...] или "tool1(a);tool2(b)"',
    )
    ap.add_argument("--expected-tools", default="", help="обязательные инструменты через запятую")
    ap.add_argument("--expected-calls", default="", help="эталонная последовательность (JSON)")
    ap.add_argument("--expected-steps", type=int, default=None, help="ожидаемое число витков")
    ap.add_argument("--order", default="any-order", choices=["any-order", "in-order", "exact"])
    ap.add_argument("--seal", action="store_true", help="BK-1: подписать траекторию (block_id+hash), вывести JSON")
    ap.add_argument(
        "--verify-against",
        default=None,
        help="BK-1: проверить целостность --calls против подписанного JSON-файла (replay)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ev = TrajectoryEvaluator(
        expected_tools=[t.strip() for t in args.expected_tools.split(",") if t.strip()],
        expected_calls=json.loads(args.expected_calls) if args.expected_calls else [],
        expected_steps=args.expected_steps,
        order_mode=args.order,
    )
    result = ev.evaluate(_parse_calls(args.calls))

    if args.seal:
        sealed = ev.seal(_parse_calls(args.calls))
        print(json.dumps(sealed, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.verify_against:
        with open(args.verify_against, encoding="utf-8") as f:
            sealed = json.load(f)
        report = ev.verify_integrity(sealed, _parse_calls(args.calls))
        if args.json or True:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(0 if report["integrity_ok"] else 1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(
        f"Ступени: {result['steps']}"
        + (f"/{result['expected_steps']}" if result["expected_steps"] else "")
    )
    print(f"Precision: {result['precision']}  Recall: {result['recall']}")
    print(
        f"Зацикливание: {'ДА на витке ' + str(result['loop_position']) if result['loop'] else 'нет'}"
    )
    if result["tools_missing"]:
        print(f"Не вызваны: {result['tools_missing']}")
    if result["tools_extra"]:
        print(f"Лишние: {result['tools_extra']}")
    for issue in result["issues"]:
        print(f"  ❌ {issue}")
    print("✅ ТРАЕКТОРИЯ OK" if result["passed"] else "❌ ТРАЕКТОРИЯ FAILED")
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
