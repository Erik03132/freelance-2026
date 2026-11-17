"""Eval for tools/lead_score.py — LEAD-001 (детерминированный скоринг лидов).

Запуск: python3 tools/tests/eval_lead_score.py
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.lead_score import SIGNALS, main  # noqa: E402

AS_OF = "2026-11-17"


def _days_ago(n: int) -> str:
    return (date.fromisoformat(AS_OF) - timedelta(days=n)).isoformat()


def _run_cli(argv: list[str], stdin_text: str = "") -> tuple[int, str, str]:
    """Вызывает main() с подменой stdin/stdout/stderr."""
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin_text)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
    finally:
        sys.stdin = old_stdin
    return code, out.getvalue(), err.getvalue()


def _score_with(
    payload: dict, tmp: Path, weights: dict | None = None, extra: list[str] | None = None
) -> dict:
    lead_path = tmp / "lead.json"
    lead_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    argv = ["--input", str(lead_path), "--json", "--as-of", AS_OF]
    if weights is not None:
        weights_path = tmp / "weights.json"
        weights_path.write_text(json.dumps(weights, ensure_ascii=False), encoding="utf-8")
        argv += ["--weights", str(weights_path)]
    if extra:
        argv += extra
    code, out, err = _run_cli(argv)
    if code != 0:
        raise AssertionError(f"неожиданный код {code}: {err.strip()}")
    return json.loads(out)


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []
    try:
        with tempfile.TemporaryDirectory() as td:
            _checks(Path(td), fails)
    except AssertionError as exc:
        fails.append(f"остановка: {exc}")
    return len(fails), fails


def _checks(tmp: Path, fails: list[str]) -> None:
    # TP-1: максимум — все сигналы на полную, 100 баллов, P0
    r = _score_with(
        {
            "id": "max",
            "service_match": "explicit",
            "budget_rub": 250000,
            "deadline": "2026-12-10",
            "decision_maker": True,
            "request_date": _days_ago(2),
            "channel": "referral",
        },
        tmp,
    )
    if r["score"] != 100 or r["band"] != "P0":
        fails.append(f"TP-1: ожидали 100/P0, получили {r['score']}/{r['band']}")
    if r["missing"]:
        fails.append(f"TP-1: не должно быть пропусков, получили {r['missing']}")

    # TP-2: минимум — все сигналы в нуле, 0 баллов, P2
    r = _score_with(
        {
            "id": "min",
            "service_match": "none",
            "budget_rub": 0,
            "decision_maker": False,
            "request_date": _days_ago(32),
            "channel": "cold",
        },
        tmp,
    )
    if r["score"] != 0 or r["band"] != "P2":
        fails.append(f"TP-2: ожидали 0/P2, получили {r['score']}/{r['band']}")
    if not r["complete"]:
        fails.append(f"TP-2: сигналы переданы все, а complete=False: {r['missing']}")

    # TP-3: пустой объект — без падения, 0 баллов, все сигналы в missing
    r = _score_with({}, tmp)
    if r["score"] != 0 or r["band"] != "P2":
        fails.append(f"TP-3: пустой лид должен дать 0/P2, получили {r['score']}/{r['band']}")
    if len(r["missing"]) != len(SIGNALS):
        fails.append(f"TP-3: ожидали {len(SIGNALS)} пропусков, получили {r['missing']}")

    # TP-4: отсутствие одного сигнала не ломает расчёт (нет channel)
    r = _score_with(
        {
            "service_match": "explicit",
            "budget_rub": 100000,
            "decision_maker": True,
            "request_date": _days_ago(1),
        },
        tmp,
    )
    if r["missing"] != ["channel"]:
        fails.append(f"TP-4: ожидали missing=['channel'], получили {r['missing']}")
    if r["score"] != 75:
        fails.append(f"TP-4: ожидали 75 (без канала), получили {r['score']}")

    # TP-5: границы порогов на управляемых весах (только service_match=100, p0=100, p1=50)
    weights = {
        "weights": {
            "service_match": 100,
            "budget": 0,
            "decision_maker": 0,
            "freshness": 0,
            "channel": 0,
        },
        "thresholds": {"p0": 100, "p1": 50},
    }
    cases = [("explicit", 100, "P0"), ("partial", 50, "P1"), ("none", 0, "P2")]
    for value, expected_score, expected_band in cases:
        r = _score_with({"service_match": value}, tmp, weights=weights)
        if (r["score"], r["band"]) != (expected_score, expected_band):
            fails.append(
                f"TP-5: {value} ожидали {expected_score}/{expected_band}, получили {r['score']}/{r['band']}"
            )

    # TP-6: границы свежести 7 / 8 / 30 / 31 день
    fresh_cases = [(7, 2), (8, 1), (30, 1), (31, 0)]
    for days, expected_level in fresh_cases:
        r = _score_with({"request_date": _days_ago(days)}, tmp)
        level = next(s["level"] for s in r["signals"] if s["name"] == "freshness")
        if level != expected_level:
            fails.append(f"TP-6: {days} дн. → ожидали level {expected_level}, получили {level}")

    # TP-7: бюджет частично (только сумма или только срок) — level 1, а не 2
    for partial in ({"budget_rub": 90000}, {"deadline_days": 14}):
        r = _score_with(partial, tmp)
        level = next(s["level"] for s in r["signals"] if s["name"] == "budget")
        if level != 1:
            fails.append(f"TP-7: {partial} → ожидали level 1, получили {level}")

    # TP-8: битый JSON → код 2, ошибка в stderr, без трейсбека
    code, out, err = _run_cli(["--input", "-"], stdin_text='{"id": "x", ')
    if code != 2:
        fails.append(f"TP-8: битый JSON → ожидали код 2, получили {code}")
    if "битый JSON" not in err or "Traceback" in err:
        fails.append(f"TP-8: ожидали внятную ошибку в stderr, получили {err.strip()!r}")
    if out.strip():
        fails.append(f"TP-8: при ошибке stdout должен быть пуст, получили {out.strip()!r}")

    # TP-9: пустой вход → код 2 и сообщение про пустой ввод
    code, _out, err = _run_cli(["--input", "-"], stdin_text="")
    if code != 2 or "пустой ввод" not in err:
        fails.append(
            f"TP-9: пустой вход → ожидали код 2 + 'пустой ввод', получили {code}: {err.strip()!r}"
        )

    # TP-10: неизвестный канал → код 2 (валидация, а не молчаливый ноль)
    code, _out, err = _run_cli(["--input", "-"], stdin_text='{"channel": "telepathy"}')
    if code != 2 or "channel" not in err:
        fails.append(
            f"TP-10: неизвестный канал → ожидали код 2 + 'channel', получили {code}: {err.strip()!r}"
        )

    # TP-11: неизвестный сигнал в весах → код 2
    bad_weights = tmp / "bad_weights.json"
    bad_weights.write_text(json.dumps({"weights": {"vibe": 100}}), encoding="utf-8")
    code, _out, err = _run_cli(
        ["--input", "-", "--weights", str(bad_weights)], stdin_text='{"id": "x"}'
    )
    if code != 2 or "vibe" not in err:
        fails.append(
            f"TP-11: неизвестный вес → ожидали код 2 + 'vibe', получили {code}: {err.strip()!r}"
        )

    # TP-12: --out идемпотентен — повторный прогон не дублирует запись и не меняет файл
    ledger = tmp / "leads.jsonl"
    lead_path = tmp / "idem.json"
    lead_path.write_text(
        json.dumps({"id": "idem-1", "service_match": "explicit", "channel": "referral"}),
        encoding="utf-8",
    )
    argv = ["--input", str(lead_path), "--json", "--as-of", AS_OF, "--out", str(ledger)]
    first = _run_cli(argv)
    snapshot = ledger.read_text(encoding="utf-8")
    second = _run_cli(argv)
    if first[0] != 0 or second[0] != 0:
        fails.append(f"TP-12: код {first[0]}/{second[0]} вместо 0: {first[2]}{second[2]}")
    if ledger.read_text(encoding="utf-8") != snapshot:
        fails.append("TP-12: повторный прогон изменил леджер")
    if len(snapshot.strip().splitlines()) != 1:
        fails.append(
            f"TP-12: ожидали 1 строку в леджере, получили {len(snapshot.strip().splitlines())}"
        )
    if first[1] != second[1]:
        fails.append("TP-12: вывод нестабилен между прогонами")

    # TP-13: --dry-run не создаёт файл леджера
    dry_ledger = tmp / "dry.jsonl"
    code, _out, err = _run_cli(
        ["--input", str(lead_path), "--as-of", AS_OF, "--out", str(dry_ledger), "--dry-run"]
    )
    if code != 0 or dry_ledger.exists():
        fails.append(
            f"TP-13: dry-run создал файл или упал (код {code}, exists={dry_ledger.exists()})"
        )
    if "dry-run" not in err:
        fails.append(f"TP-13: dry-run должен сказать, что запись пропущена, stderr={err.strip()!r}")

    # TP-14: базовые веса согласованы (сумма 100) и пороги помечены как placeholder
    total = sum(s["weight"] for s in SIGNALS)
    if total != 100:
        fails.append(f"TP-14: сумма весов по умолчанию {total} != 100")
    r = _score_with({"id": "meta"}, tmp)
    if r["thresholds"]["p0"] <= r["thresholds"]["p1"]:
        fails.append("TP-14: p0 должен быть больше p1")
    if "LEAD-002" not in r["thresholds"]["status"]:
        fails.append("TP-14: пороги должны помечаться как placeholder (LEAD-002 PENDING)")


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(
        "✅ EVAL PASSED — lead_score: min/max, пропуски сигналов, границы порогов и свежести, "
        "ошибки входа, идемпотентность"
    )
