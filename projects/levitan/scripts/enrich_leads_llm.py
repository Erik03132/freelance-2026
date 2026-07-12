#!/usr/bin/env python3
"""
LLM enrichment of transcribed Adygea leads.

Reads data/adygea_leads/leads_raw.json, runs each transcript through
DeepSeek (OpenRouter) to extract structured CRM fields, and writes
enriched JSON + a clean Markdown table.
"""

import json
import os
import signal
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "adygea_leads", "leads_raw.json")
OUT_JSON = os.path.join(BASE, "data", "adygea_leads", "leads_enriched.json")
OUT_MD = os.path.join(BASE, "data", "adygea_leads", "leads_table.md")

PROMPT = """Проанализируй транскрипт разговора голосового бота с сельхозпроизводителем (фермером/КФХ).
Компания закупает зерновые, масличные, бобовые культуры у производителей.

Верни ТОЛЬКО JSON без markdown-разметки:
{{
  "status": "lead|callback|no_interest|no_answer|other",
  "product": "культуры которые фермер планирует продавать (через запятую, в именительном падеже)",
  "volume": "объём в тоннах, если назван (например '400-500' или '50'); пусто если не назвал",
  "ready_date": "когда готов к отгрузке/продаже (дата или 'уже', 'завтра', 'через неделю')",
  "price_info": "что сказано про цену (ожидания, диапазон); пусто если нет",
  "notes": "кратко: ключевые договорённости, возражения, что просил перезвонить"
}}

Правила:
- status=lead если выразил интерес продать / готов обсудить
- status=callback если просил перезвонить позже
- status=no_interest если отказал / не планирует продавать
- Заполняй ТОЛЬКО то, что реально прозвучало. Не выдумывай.

ТРАНСКРИПТ:
{transcript}"""


def timeout(signum, frame):
    raise TimeoutError()


def extract(transcript, retries=3):
    for attempt in range(retries):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                json={
                    "model": "deepseek/deepseek-chat-v3-0324",
                    "messages": [{"role": "user", "content": PROMPT.format(transcript=transcript)}],
                    "max_tokens": 400,
                    "temperature": 0.1,
                },
                timeout=30,
            )
            content = r.json()["choices"][0]["message"]["content"].strip()
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            print(f"  LLM err: {e}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    return {}


def main():
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(900)
    data = json.load(open(RAW, encoding="utf-8"))
    for i, r in enumerate(data):
        tr = r.get("transcript", "")
        if not tr:
            continue
        print(f"  [{i+1}/{len(data)}] {r['name'][:28]}...", file=sys.stderr)
        ex = extract(tr)
        r["llm"] = ex
        r["status_llm"] = ex.get("status", "")
        r["product_llm"] = ex.get("product", "")
        r["volume_llm"] = ex.get("volume", "")
        r["ready_date_llm"] = ex.get("ready_date", "")
        r["price_llm"] = ex.get("price_info", "")
        r["notes_llm"] = ex.get("notes", "")
        # incremental save
        json.dump(data, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        time.sleep(0.5)

    # Sort: real leads/callbacks first
    rank = {"lead": 0, "callback": 1, "other": 2, "no_interest": 3, "no_answer": 4, "": 5}
    data.sort(key=lambda x: rank.get(x.get("status_llm", ""), 2))
    json.dump(data, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    hot = [r for r in data if r.get("status_llm") in ("lead", "callback")]
    print(f"\n## 🔥 Интересные клиенты Адыгеи — {len(hot)} из {len(data)}\n", file=sys.stderr)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(f"# Интересные клиенты Адыгеи (по расшифровкам звонков)\n\n")
        f.write(f"Всего обработано звонков >15с: {len(data)} | Интересных (lead/callback): {len(hot)}\n\n")
        f.write("## Горячие лиды\n\n")
        f.write("| # | Имя | Район | Телефон | Культура | Объём (т) | Готовность | Цена | Договорённости |\n")
        f.write("|---|------|-------|---------|----------|-----------|------------|------|----------------|\n")
        for i, r in enumerate(hot, 1):
            name = r["name"].replace("Глава: ", "").replace("Дир.: ", "").replace("Предс.: ", "")
            f.write(f"| {i} | {name} | {r['district']} | {r['phone']} | {r.get('product_llm') or '—'} "
                    f"| {r.get('volume_llm') or '—'} | {r.get('ready_date_llm') or '—'} "
                    f"| {r.get('price_llm') or '—'} | {r.get('notes_llm') or '—'} |\n")
        f.write("\n## Все остальные\n\n")
        f.write("| # | Имя | Район | Телефон | Статус | Культура | Объём |\n")
        f.write("|---|------|-------|---------|--------|----------|--------|\n")
        n = 0
        for r in data:
            if r.get("status_llm") in ("lead", "callback"):
                continue
            n += 1
            name = r["name"].replace("Глава: ", "").replace("Дир.: ", "").replace("Предс.: ", "")
            f.write(f"| {n} | {name} | {r['district']} | {r['phone']} | {r.get('status_llm') or '—'} "
                    f"| {r.get('product_llm') or '—'} | {r.get('volume_llm') or '—'} |\n")
    print(f"Saved → {OUT_JSON}\nSaved table → {OUT_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
