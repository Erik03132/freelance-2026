#!/usr/bin/env python3
"""Скоринг лидов по 5 сигналам (LEAD-001). Детерминированный, только stdlib.

Классификацию сигналов делает агент (скилл `lead-copilot`), арифметику —
этот скрипт: одни и те же входные данные дают один и тот же балл.

Использование:
  python3 tools/lead_score.py --input lead.json
  python3 tools/lead_score.py --input lead.json --json --as-of 2026-11-17
  cat lead.json | python3 tools/lead_score.py --json
  python3 tools/lead_score.py --input lead.json --weights my_weights.json --dry-run

Пороги P0/P1 — placeholder: LEAD-002 PENDING, утверждает Игорь.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

SIGNALS: tuple[dict, ...] = (
    {"name": "service_match", "weight": 30, "max_level": 2, "title": "совпадение услуги/стека"},
    {"name": "budget", "weight": 20, "max_level": 2, "title": "бюджет/срок назван"},
    {"name": "decision_maker", "weight": 20, "max_level": 1, "title": "ЛПР в контакте"},
    {"name": "freshness", "weight": 15, "max_level": 2, "title": "свежесть запроса"},
    {"name": "channel", "weight": 15, "max_level": 2, "title": "канал/источник"},
)

THRESHOLDS: dict[str, int] = {"p0": 75, "p1": 50}
THRESHOLDS_STATUS = "placeholder: LEAD-002 PENDING, утверждает Игорь"

SERVICE_MATCH_LEVELS: dict[str, tuple[int, str]] = {
    "explicit": (2, "явное совпадение услуги/стека"),
    "partial": (1, "частичное совпадение"),
    "none": (0, "совпадения нет"),
}

CHANNEL_LEVELS: dict[str, int] = {
    "referral": 2,
    "recommendation": 2,
    "inbound": 2,
    "warm_inbound": 2,
    "reply": 1,
    "post_reply": 1,
    "event": 1,
    "network": 1,
    "outbound": 0,
    "cold": 0,
    "cold_outbound": 0,
    "scraped": 0,
}

BOOL_LEVELS: dict[str, bool] = {
    "true": True,
    "yes": True,
    "да": True,
    "1": True,
    "false": False,
    "no": False,
    "нет": False,
    "0": False,
}

BUDGET_KEYS = ("budget", "budget_rub", "deadline", "deadline_days")


class LeadError(Exception):
    """Ошибка входа — печатается в stderr, код выхода 2."""


def _load_json_text(text: str, what: str) -> object:
    if not text.strip():
        raise LeadError(f"{what}: пустой ввод (ожидался JSON-объект лида)")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise LeadError(
            f"{what}: битый JSON — {exc.msg} (строка {exc.lineno}, колонка {exc.colno})"
        ) from exc


def _read_json(source: str, what: str) -> object:
    if source in ("", "-"):
        return _load_json_text(sys.stdin.read(), f"{what} (stdin)")
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LeadError(f"{what}: не читается {path} — {exc.strerror}") from exc
    return _load_json_text(text, f"{what} ({path})")


def _parse_date(value: object, field: str) -> date:
    if not isinstance(value, str):
        raise LeadError(f"{field}: ожидалась дата ISO YYYY-MM-DD, получено {type(value).__name__}")
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise LeadError(f"{field}: неверная дата {value!r}, нужен ISO YYYY-MM-DD") from exc


def _as_bool(value: object, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        key = value.strip().lower()
        if key in BOOL_LEVELS:
            return BOOL_LEVELS[key]
    raise LeadError(f"{field}: ожидалось true/false, получено {value!r}")


def _signal_service_match(lead: dict, _as_of: date, _cfg: dict) -> tuple[int, str]:
    if "service_match" not in lead:
        raise KeyError("service_match")
    raw = lead["service_match"]
    if isinstance(raw, bool):
        return (2, "явное совпадение услуги/стека") if raw else (0, "совпадения нет")
    key = str(raw).strip().lower()
    if key not in SERVICE_MATCH_LEVELS:
        raise LeadError(
            f"service_match: ожидалось одно из {sorted(SERVICE_MATCH_LEVELS)} или true/false, получено {raw!r}"
        )
    level, label = SERVICE_MATCH_LEVELS[key]
    return level, label


def _signal_budget(lead: dict, _as_of: date, _cfg: dict) -> tuple[int, str]:
    if not any(k in lead for k in BUDGET_KEYS):
        raise KeyError("budget")

    amount = lead.get("budget_rub")
    raw_budget = lead.get("budget")
    if amount is None and isinstance(raw_budget, dict):
        amount = raw_budget.get("amount", raw_budget.get("rub"))
    elif (
        amount is None and isinstance(raw_budget, int | float) and not isinstance(raw_budget, bool)
    ):
        amount = raw_budget

    has_budget = False
    if amount is not None:
        if isinstance(amount, bool) or not isinstance(amount, int | float):
            raise LeadError(f"budget: ожидалось число в рублях, получено {amount!r}")
        if amount < 0:
            raise LeadError(f"budget: отрицательный бюджет {amount!r}")
        has_budget = amount > 0

    has_deadline = False
    deadline_label = ""
    if lead.get("deadline") is not None:
        has_deadline = True
        deadline_label = _parse_date(lead["deadline"], "deadline").isoformat()
    elif lead.get("deadline_days") is not None:
        days = lead["deadline_days"]
        if isinstance(days, bool) or not isinstance(days, int | float) or days < 0:
            raise LeadError(f"deadline_days: ожидалось неотрицательное число, получено {days!r}")
        has_deadline = days > 0
        deadline_label = f"{int(days)} дн."

    level = int(has_budget) + int(has_deadline)
    parts = []
    if has_budget:
        parts.append(f"бюджет {int(amount)} ₽")
    if has_deadline:
        parts.append(f"срок {deadline_label}")
    label = " + ".join(parts) if parts else "бюджет и срок не названы"
    return level, label


def _signal_decision_maker(lead: dict, _as_of: date, _cfg: dict) -> tuple[int, str]:
    if "decision_maker" not in lead:
        raise KeyError("decision_maker")
    ok = _as_bool(lead["decision_maker"], "decision_maker")
    return int(ok), "ЛПР в контакте" if ok else "ЛПР нет (посредник/неясно)"


def _signal_freshness(lead: dict, as_of: date, _cfg: dict) -> tuple[int, str]:
    if "request_date" not in lead:
        raise KeyError("freshness")
    request = _parse_date(lead["request_date"], "request_date")
    age = (as_of - request).days
    if age < 0:
        return 2, f"дата в будущем ({request.isoformat()}) — проверить"
    if age <= 7:
        return 2, f"{age} дн. назад"
    if age <= 30:
        return 1, f"{age} дн. назад (тёплый, но не свежий)"
    return 0, f"{age} дн. назад — устарел"


def _signal_channel(lead: dict, _as_of: date, _cfg: dict) -> tuple[int, str]:
    if "channel" not in lead:
        raise KeyError("channel")
    raw = lead["channel"]
    key = str(raw).strip().lower()
    if key not in CHANNEL_LEVELS:
        raise LeadError(f"channel: неизвестный канал {raw!r}, допустимо {sorted(CHANNEL_LEVELS)}")
    return CHANNEL_LEVELS[key], f"канал: {key}"


EVALUATORS = {
    "service_match": _signal_service_match,
    "budget": _signal_budget,
    "decision_maker": _signal_decision_maker,
    "freshness": _signal_freshness,
    "channel": _signal_channel,
}


def _default_config() -> dict:
    return {
        "weights": {s["name"]: s["weight"] for s in SIGNALS},
        "thresholds": dict(THRESHOLDS),
    }


def load_config(path: str | None) -> dict:
    cfg = _default_config()
    if not path:
        return cfg

    data = _read_json(path, "weights")
    if not isinstance(data, dict):
        raise LeadError("weights: ожидался JSON-объект")

    structured = "weights" in data or "thresholds" in data
    raw_weights = data.get("weights") if structured else data
    if raw_weights is not None:
        if not isinstance(raw_weights, dict):
            raise LeadError("weights: блок weights должен быть объектом {сигнал: вес}")
        known = {s["name"] for s in SIGNALS}
        for name, value in raw_weights.items():
            if name not in known:
                raise LeadError(f"weights: неизвестный сигнал {name!r}, допустимо {sorted(known)}")
            if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
                raise LeadError(
                    f"weights: вес {name!r} должен быть неотрицательным числом, получено {value!r}"
                )
            cfg["weights"][name] = value
        if sum(cfg["weights"].values()) <= 0:
            raise LeadError("weights: сумма весов должна быть > 0")

    if "thresholds" in data:
        raw_thresholds = data["thresholds"]
        if not isinstance(raw_thresholds, dict):
            raise LeadError("thresholds: ожидался объект {p0: N, p1: M}")
        for name in ("p0", "p1"):
            if name not in raw_thresholds:
                raise LeadError(f"thresholds: нет ключа {name!r}")
            value = raw_thresholds[name]
            if (
                isinstance(value, bool)
                or not isinstance(value, int | float)
                or not 0 <= value <= 100
            ):
                raise LeadError(
                    f"thresholds: {name!r} должен быть числом 0..100, получено {value!r}"
                )
            cfg["thresholds"][name] = value
        if cfg["thresholds"]["p0"] <= cfg["thresholds"]["p1"]:
            raise LeadError("thresholds: p0 должен быть больше p1")

    return cfg


def score_lead(lead: dict, cfg: dict, as_of: date) -> dict:
    total_weight = sum(cfg["weights"].values())
    missing: list[str] = []
    items: list[dict] = []

    for sig in SIGNALS:
        name = sig["name"]
        weight = cfg["weights"][name]
        try:
            level, label = EVALUATORS[name](lead, as_of, cfg)
        except KeyError:
            missing.append(name)
            level, label = 0, "нет данных"
        points = round(level * weight / sig["max_level"], 2)
        items.append(
            {
                "name": name,
                "title": sig["title"],
                "level": level,
                "max_level": sig["max_level"],
                "weight": weight,
                "points": points,
                "label": label,
            }
        )

    raw = sum(i["points"] for i in items)
    score = int(math.floor(raw * 100 / total_weight + 0.5))
    if score >= cfg["thresholds"]["p0"]:
        band = "P0"
    elif score >= cfg["thresholds"]["p1"]:
        band = "P1"
    else:
        band = "P2"

    lead_id = lead.get("id") or lead.get("lead_id")

    return {
        "id": lead_id,
        "score": score,
        "band": band,
        "as_of": as_of.isoformat(),
        "signals": items,
        "missing": missing,
        "complete": not missing,
        "total_weight": total_weight,
        "thresholds": {
            "p0": cfg["thresholds"]["p0"],
            "p1": cfg["thresholds"]["p1"],
            "status": THRESHOLDS_STATUS,
        },
    }


def render_text(result: dict) -> str:
    lead_id = result["id"] or "(без id)"
    lines = [f"{lead_id} → {result['band']}, {result['score']}/100"]
    for item in result["signals"]:
        lines.append(
            f"  {item['name']:<15} {item['level']}/{item['max_level']} × {item['weight']:<5g} "
            f"→ {item['points']:<6g} {item['label']}"
        )
    thresholds = result["thresholds"]
    lines.append(
        f"Пороги: P0 ≥ {thresholds['p0']:g}, P1 ≥ {thresholds['p1']:g} ({thresholds['status']})"
    )
    if result["missing"]:
        lines.append(f"Нет данных: {', '.join(result['missing'])}")
    return "\n".join(lines)


def write_ledger(path: str, result: dict) -> None:
    target = Path(path)
    records: list[dict] = []
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and record.get("id") == result["id"]:
                continue
            records.append(record)
    records.append(result)

    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=".lead_score_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        os.replace(tmp_name, target)
    except OSError:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lead_score.py",
        description="Скоринг лида по 5 сигналам: service_match, budget, decision_maker, freshness, channel.",
        epilog=(
            "Примеры:\n"
            "  python3 tools/lead_score.py --input lead.json\n"
            "  python3 tools/lead_score.py --input lead.json --json --as-of 2026-11-17\n"
            "  cat lead.json | python3 tools/lead_score.py --weights my_weights.json --dry-run\n"
            "\nПороги P0/P1 — placeholder: LEAD-002 PENDING, утверждает Игорь."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default="-",
        metavar="PATH",
        help="JSON-файл лида; '-' или пусто — читать stdin",
    )
    parser.add_argument(
        "--weights",
        metavar="PATH",
        help="JSON с весами и порогами: {weights: {сигнал: вес}, thresholds: {p0, p1}}",
    )
    parser.add_argument(
        "--json", action="store_true", help="вывести результат в JSON (машинный формат)"
    )
    parser.add_argument(
        "--as-of",
        metavar="YYYY-MM-DD",
        help="дата расчёта свежести; по умолчанию сегодня",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help="JSONL-леджер: дописать результат (запись с тем же id заменяется)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="посчитать и показать, но не писать в --out",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        as_of = _parse_date(args.as_of, "--as-of") if args.as_of else date.today()
        cfg = load_config(args.weights)
        payload = _read_json(args.input, "input")
        if not isinstance(payload, dict):
            raise LeadError("input: ожидался JSON-объект лида, получен " + type(payload).__name__)
        result = score_lead(payload, cfg, as_of)
    except LeadError as exc:
        print(f"lead_score: ошибка — {exc}", file=sys.stderr)
        return 2

    output = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        if args.json
        else render_text(result)
    )
    print(output)

    if args.out:
        if args.dry_run:
            print(f"lead_score: dry-run — запись в {args.out} пропущена", file=sys.stderr)
        else:
            try:
                write_ledger(args.out, result)
            except OSError as exc:
                print(f"lead_score: ошибка записи {args.out} — {exc}", file=sys.stderr)
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
