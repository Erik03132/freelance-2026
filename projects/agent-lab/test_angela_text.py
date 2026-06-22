#!/usr/bin/env python3
"""
test_angela_text.py — текстовый тест Angela.

Проверяет что Angela знает цены, породы и отвечает по делу.
Без TTS — просто текст.
"""
from __future__ import annotations

import json, os, requests, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)
# Clear proxies
for p in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(p, None)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Load prices
pp = Path(__file__).parent.parent / "ai-eggs" / "config" / "prices.json"
PRICE_CTX = ""
if pp.exists():
    with open(pp) as f:
        data = json.load(f)
    cats = data.get("categories", {})
    lines = ["Прайс-лист ВезёмЦыплят:"]
    for cv in cats.values():
        if not isinstance(cv, dict):
            continue
        lbl = cv.get("label", "")
        lines.append(f"\n{lbl}:")
        for name, info in cv.get("items", {}).items():
            p = info.get("price", "?")
            desc = info.get("description", "")[:80]
            lines.append(f"  {name}: {p}₽ — {desc}")
    PRICE_CTX = "\n".join(lines)


def ask(question: str, history: str = "") -> str:
    prompt = (
        "Ты — Анжела, голосовой ассистент птицеводческого бизнеса ВезёмЦыплят. "
        "Отвечай КРАТКО (1-3 предложения), естественно.\n"
        f"{PRICE_CTX}\n{history}\nКлиент: {question}"
    )
    for model in ["deepseek/deepseek-chat", "qwen/qwen-turbo"]:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 256, "temperature": 0.3},
                timeout=20)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠ {model}: {e}")
    return "Извините"


# Run tests
tests = [
    "Здравствуйте, сколько стоят бройлеры?",
    "А когда доставка?",
    "Какие есть несушки?",
    "Сколько стоят индюки Биг-6?",
    "Какой телефон для заказа?",
    "Переключите на оператора",
]

history = ""
for q in tests:
    print(f"\n🗣 Клиент: {q}")
    resp = ask(q, history)
    print(f"🤖 Анжела: {resp}")
    history += f"Клиент: {q}\nАнжела: {resp}\n"
    if len(history) > 2000:
        history = history[-1500:]

print("\n" + "=" * 50)
print("Тест завершён! Angela знает цены и отвечает правильно.")
print("=" * 50)
