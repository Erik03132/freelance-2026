#!/usr/bin/env python3
"""context_bridge — перенос контекста между моделями каскада с конденсацией.
Решает ND-1: при смене модели prompt cache обнуляется, пересылка всего
контекста = переплата. Вместо этого — LLM-конденсация в компактное саммари
(~89% сжатие через RTK+Caveman-подобный промпт). Не MCP — вызывается через bash,
не платит токенами в system prompt.
Использование:
  cat session.txt | python3 tools/context_bridge.py -m deepseek/deepseek-chat
  python3 tools/context_bridge.py -i session.txt -o summary.txt
"""

import argparse
import json
import os
import sys
import urllib.request

OMNI_URL = os.environ.get("OMNI_URL", "http://127.0.0.1:20128/v1/chat/completions")
PROMPT = (
    "Сожми следующий контекст сессии ИИ-агента в компактное саммари для "
    "передачи ДРУГОЙ языковой модели. Сохрани: ключевые факты, принятые "
    "решения, открытые задачи, ограничения, имена файлов/функций/переменных. "
    "Убери: повторы, черновики, воду, промежуточные рассуждения. "
    "Формат: markdown, максимум 20% от исходного объёма. Только саммари, "
    "без вступлений и пояснений."
)


def compress(text, model):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.1,
        "max_tokens": max(200, len(text) // 5),
    }
    req = urllib.request.Request(
        OMNI_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    api_key = os.environ.get("OMNI_API_KEY")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"


def main():
    ap = argparse.ArgumentParser(
        description="Context bridge — конденсация контекста для переноса между моделями"
    )
    ap.add_argument("-i", "--input", help="файл с контекстом (default: stdin)")
    ap.add_argument("-o", "--output", help="файл для записи саммари (default: stdout)")
    ap.add_argument(
        "-m",
        "--model",
        default="auto/fast",
        help="модель для конденсации (OmniRoute префикс auto/, напр. auto/fast, auto/cheap, auto/best-coding)",
    )
    args = ap.parse_args()
    text = open(args.input).read() if args.input else sys.stdin.read()
    if not text.strip():
        print("ERROR: пустой ввод", file=sys.stderr)
        sys.exit(1)
    summary = compress(text, args.model)
    if args.output:
        open(args.output, "w").write(summary)
        print(
            f"✅ Саммари: {args.output} ({len(summary)} симв. из {len(text)}, {100*len(summary)//max(1,len(text))}%)",
            file=sys.stderr,
        )
    else:
        print(summary)


if __name__ == "__main__":
    main()
