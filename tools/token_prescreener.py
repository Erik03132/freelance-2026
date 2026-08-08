#!/usr/bin/env python3
"""
Пре-скринер токенов перед тяжёлым LLM-запросом.
Оценивает стоимость запроса до отправки, помогает соблюдать недельный бюджет.

Использование:
  python tools/token_prescreener.py "текст промпта"
  python tools/token_prescreener.py --file prompts/system.txt
  python tools/token_prescreener.py --budget 5.0 --model deepseek-chat "текст"
  echo "промпт" | python tools/token_prescreener.py --stdin
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import tiktoken

    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


MODEL_PRICING = {
    "deepseek-chat": {"input": 0.14, "output": 0.28, "cached_input": 0.0028},
    "deepseek-v4-flash": {"input": 0.14, "output": 0.28, "cached_input": 0.0028},
    "anthropic/claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "anthropic/claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "openai/gpt-4.1": {"input": 2.00, "output": 8.00},
    "x-ai/grok-4.5": {"input": 0.002, "output": 0.006},
}
DEFAULT_MODEL = "deepseek-chat"
RU_TOKEN_FACTOR = 1.5
DEFAULT_OUTPUT_ESTIMATE = 500


def estimate_tokens(text: str, model: str = DEFAULT_MODEL) -> int:
    if HAS_TIKTOKEN:
        try:
            enc = tiktoken.encoding_for_model(model)
            return len(enc.encode(text))
        except (KeyError, ValueError):
            pass
    return max(1, len(text) // 4)


def count_ru_word_ratio(text: str) -> float:
    ru_chars = sum(1 for c in text if "а" <= c.lower() <= "я" or c.lower() == "ё")
    total_chars = max(1, len(text.strip()))
    return ru_chars / total_chars


def estimate_cost(
    text: str,
    model: str = DEFAULT_MODEL,
    output_tokens: int = DEFAULT_OUTPUT_ESTIMATE,
    is_cached: bool = False,
) -> dict:
    base_tokens = estimate_tokens(text, model)
    ru_ratio = count_ru_word_ratio(text)
    adjusted_tokens = int(base_tokens * (1 + ru_ratio * (RU_TOKEN_FACTOR - 1)))

    pricing = MODEL_PRICING.get(model, MODEL_PRICING[DEFAULT_MODEL])
    input_rate = pricing["cached_input"] if is_cached else pricing["input"]

    input_cost = (adjusted_tokens / 1_000_000) * input_rate
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "model": model,
        "input_tokens_raw": base_tokens,
        "input_tokens_adjusted": adjusted_tokens,
        "output_tokens_est": output_tokens,
        "ru_ratio": round(ru_ratio, 2),
        "ru_factor": RU_TOKEN_FACTOR,
        "is_cached": is_cached,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "total_cost_rub": round(total_cost * 85, 2),
    }


def format_report(result: dict, budget: float = 0.0) -> str:
    lines = [
        f"Модель:           {result['model']}",
        f"Токенов вход:     {result['input_tokens_adjusted']}",
        f"  (raw: {result['input_tokens_raw']}, RU-коррекция: {result['ru_ratio']:.0%} ×{result['ru_factor']})",
        f"Токенов выход:    ~{result['output_tokens_est']}",
        f"Кэш-хит:          {'да' if result['is_cached'] else 'нет'}",
        "",
        "Стоимость:",
        f"  вход:   ${result['input_cost_usd']:.6f}",
        f"  выход:  ${result['output_cost_usd']:.6f}",
        f"  итого:  ${result['total_cost_usd']:.6f} (~{result['total_cost_rub']:.2f} ₽)",
    ]
    if budget > 0:
        pct = (result["total_cost_usd"] / budget) * 100
        status = "OK" if pct <= 10 else ("WARN" if pct <= 50 else "BLOCKED")
        lines.extend(
            [
                "",
                f"Бюджет:     ${budget:.2f}",
                f"Расход:     {pct:.1f}% [{status}]",
            ]
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Token pre-screener for LLM requests")
    parser.add_argument("text", nargs="?", help="Prompt text to analyze")
    parser.add_argument("--file", "-f", help="Read prompt from file")
    parser.add_argument("--stdin", action="store_true", help="Read prompt from stdin")
    parser.add_argument(
        "--model", "-m", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--output", "-o", type=int, default=DEFAULT_OUTPUT_ESTIMATE, help="Estimated output tokens"
    )
    parser.add_argument("--cached", action="store_true", help="Assume prompt cache hit")
    parser.add_argument(
        "--budget", "-b", type=float, default=0.0, help="Weekly budget in USD for context"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--models", action="store_true", help="List supported models and pricing")
    args = parser.parse_args()

    if args.models:
        print(json.dumps(MODEL_PRICING, indent=2))
        return

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.stdin:
        text = sys.stdin.read()
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    result = estimate_cost(
        text,
        model=args.model,
        output_tokens=args.output,
        is_cached=args.cached,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result, args.budget))


if __name__ == "__main__":
    main()
