#!/usr/bin/env python3
"""
💰 Cost Tracker — учёт расхода токенов и денег на LLM-вызовы.

Пишет каждый вызов в data/cost_tracker.json.
Поддерживает отчёты за день, неделю, месяц.

Использование:
    from tools.cost_tracker import track, report
    track(model="deepseek/deepseek-chat", prompt_tokens=120, completion_tokens=80, source="model_router")
    report()  # print в консоль

CLI:
    python3 tools/cost_tracker.py --report
    python3 tools/cost_tracker.py --report --period week
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# ── Пути ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "cost_tracker.json")

# ── Цены OpenRouter (USD за 1M токенов, входящие+исходящие усреднено) ─────────
# Обновлены June 2026. Input/output цены усреднены для простоты.
MODEL_PRICES: dict[str, float] = {
    # DeepSeek
    "deepseek/deepseek-chat":           0.14,   # $0.07-0.21/M
    "deepseek/deepseek-r1":             0.55,   # $0.55/M
    "deepseek/deepseek-r1-distill-qwen-7b": 0.10,
    # Qwen
    "qwen/qwen-turbo":                  0.05,
    "qwen/qwen-plus":                   0.20,
    "qwen/qwen-max":                    0.80,
    # Gemini (через OpenRouter)
    "google/gemini-2.0-flash-001":      0.10,
    "google/gemini-2.5-flash":          0.15,
    "google/gemini-2.5-pro":            1.25,
    # OpenAI
    "openai/gpt-4o-mini":               0.15,
    "openai/gpt-4o":                    2.50,
    "openai/gpt-4.1":                   2.00,
    "openai/gpt-4.1-mini":              0.40,
    # Anthropic
    "anthropic/claude-sonnet-4-5":      3.00,
    "anthropic/claude-haiku-3-5":       0.80,
    "anthropic/claude-opus-4":         15.00,
    # Mistral
    "mistralai/mistral-7b-instruct":    0.06,
    "mistralai/mixtral-8x7b-instruct":  0.24,
    # Meta
    "meta-llama/llama-3.1-8b-instruct": 0.06,
    "meta-llama/llama-3.3-70b-instruct": 0.40,
}

UNKNOWN_PRICE = 0.50  # дефолт для неизвестных моделей


def _price(model: str) -> float:
    """Цена за 1M токенов. Поиск по точному совпадению, затем по префиксу."""
    if model in MODEL_PRICES:
        return MODEL_PRICES[model]
    for key, price in MODEL_PRICES.items():
        if model.startswith(key.split("/")[0]):
            return price
    return UNKNOWN_PRICE


def _load() -> list[dict]:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save(records: list[dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    # Держим последние 10 000 записей
    records = records[-10_000:]
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, ensure_ascii=False, separators=(",", ":"))


def track(
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    source: str = "unknown",
    task: str = "",
    success: bool = True,
) -> float:
    """
    Записывает один LLM-вызов. Возвращает стоимость в USD.

    Args:
        model:             ID модели (напр. "deepseek/deepseek-chat")
        prompt_tokens:     входящие токены из ответа API
        completion_tokens: исходящие токены
        total_tokens:      если API вернул суммарно (иначе prompt+completion)
        source:            откуда вызов: "model_router", "llm_planner", etc.
        task:              краткое описание задачи
        success:           успешен ли вызов
    """
    if total_tokens == 0:
        total_tokens = prompt_tokens + completion_tokens

    cost_usd = (total_tokens / 1_000_000) * _price(model)

    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": round(cost_usd, 6),
        "source": source,
        "task": task[:80] if task else "",
        "success": success,
    }

    try:
        records = _load()
        records.append(record)
        _save(records)
    except Exception as e:
        # Никогда не ломаем основной поток из-за трекинга
        print(f"[cost_tracker] ⚠ save error: {e}", file=sys.stderr)

    return cost_usd


def report(period: str = "day", verbose: bool = False) -> dict:
    """
    Генерирует отчёт за период: 'day', 'week', 'month', 'all'.
    Возвращает dict и печатает в консоль.
    """
    records = _load()
    if not records:
        print("💰 Cost Tracker: данных нет")
        return {}

    # Фильтр по периоду
    now = datetime.now()
    cutoffs = {
        "day":   now - timedelta(days=1),
        "week":  now - timedelta(days=7),
        "month": now - timedelta(days=30),
        "all":   datetime.min,
    }
    cutoff = cutoffs.get(period, cutoffs["day"])

    filtered = [
        r for r in records
        if datetime.fromisoformat(r["ts"]) >= cutoff and r.get("success", True)
    ]

    if not filtered:
        print(f"💰 Нет данных за период: {period}")
        return {}

    # Агрегация
    total_tokens = sum(r.get("total_tokens", 0) for r in filtered)
    total_cost   = sum(r.get("cost_usd", 0) for r in filtered)
    calls        = len(filtered)

    by_model: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
    by_source: dict[str, int] = defaultdict(int)

    for r in filtered:
        m = r.get("model", "unknown")
        by_model[m]["calls"]  += 1
        by_model[m]["tokens"] += r.get("total_tokens", 0)
        by_model[m]["cost"]   += r.get("cost_usd", 0)
        by_source[r.get("source", "?")] += 1

    # Вывод
    period_labels = {"day": "сегодня", "week": "неделя", "month": "месяц", "all": "всё время"}
    label = period_labels.get(period, period)

    print(f"\n💰 Cost Report — {label}")
    print(f"{'─'*45}")
    print(f"  Вызовов:  {calls:>8,}")
    print(f"  Токенов:  {total_tokens:>8,}")
    print(f"  Стоимость: ${total_cost:>8.4f}")
    print(f"\n  По моделям:")
    for model, stats in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        print(f"    {model:<40} {stats['calls']:>4} вызовов  {stats['tokens']:>8,} токенов  ${stats['cost']:.4f}")
    print(f"\n  По источникам:")
    for src, cnt in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"    {src:<30} {cnt:>4} вызовов")
    print(f"{'─'*45}\n")

    return {
        "period": period,
        "calls": calls,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "by_model": dict(by_model),
        "by_source": dict(by_source),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Cost Tracker")
    parser.add_argument("--report", action="store_true", help="Показать отчёт")
    parser.add_argument("--period", default="day", choices=["day", "week", "month", "all"],
                        help="Период отчёта (default: day)")
    args = parser.parse_args()

    if args.report:
        report(period=args.period)
    else:
        parser.print_help()
