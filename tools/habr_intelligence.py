#!/usr/bin/env python3
"""
🧠 Habr Intelligence v2 — глобальный LLM-дайджест для AI-экосистемы.

Парсит RSS хабов Хабра, скорит по ключевым словам, затем прогоняет
Топ-5 статей через LLM и получает практические рекомендации:
«Как применить в нашей AI-экосистеме (ai-eggs, ai-bureau, agent-lab)?»

Место: /freelance-2026/tools/ (глобальный инструмент)
Cron:  5 9 * * * cd /Users/igorvasin/freelance-2026 && python3 tools/habr_intelligence.py

Использует корневой .env (/freelance-2026/.env)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape

import requests
from dotenv import load_dotenv

# ── Пути ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# ── Конфиг ────────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN  = os.getenv("ANGELOCHKA_BOT_TOKEN", "")
OWNER_CHAT_ID   = int(os.getenv("ADMIN_TELEGRAM_ID", "176203333"))
PROXY_URL       = os.getenv("HTTPS_PROXY", os.getenv("TELEGRAM_PROXY", ""))
OPENROUTER_KEY  = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_KEY      = os.getenv("GEMINI_API_KEY", "")
GEMINI_BACKUP   = os.getenv("GEMINI_BACKUP_KEY", "")

STATE_FILE = os.path.join(BASE_DIR, "data", "habr_intelligence_state.json")

# ── Хабы ──────────────────────────────────────────────────────────────────────
HABR_HUBS = [
    # AI / LLM
    "artificial_intelligence",
    "machine_learning",
    "natural_language_processing",
    "chatgpt",
    # Разработка
    "python",
    "api",
    "devops",
    "data_engineering",
    # Маркетинг / SEO
    "seo",
    "internetmarketing",
    "search_technologies",
    # Менеджмент
    "dev_management",
]

# ── Ключевые слова (вес 1-3) ───────────────────────────────────────────────────
KEYWORDS: dict[str, int] = {
    # SEO/GEO/AEO
    "seo": 3, "geo": 3, "aeo": 3, "serp": 3,
    "нейровыдача": 3, "ai overview": 3, "ai mode": 3,
    "поисковая оптимизация": 2, "яндекс": 2, "google search": 2,
    # AI агенты
    "agentic": 3, "ai agent": 3, "мультиагент": 3,
    "llm": 3, "large language model": 3,
    "gpt": 2, "gemini": 2, "claude": 2, "deepseek": 2, "qwen": 2,
    "промпт": 2, "prompt engineering": 3, "system prompt": 2,
    "rag": 3, "retrieval": 2, "embedding": 2, "vector": 2,
    "fine-tuning": 3, "дообучение": 3,
    "tool use": 3, "function calling": 3,
    "langchain": 2, "langgraph": 3, "crewai": 2,
    # Инфра / DevOps
    "fastapi": 2, "async": 1, "python": 1,
    "pm2": 2, "docker": 1, "ci/cd": 1, "deploy": 1,
    "cron": 2, "scheduler": 2, "webhook": 2,
    # Telegram / боты
    "telegram bot": 3, "бот": 2, "чат-бот": 2,
    # CRM / Продажи
    "bitrix": 3, "crm": 2, "воронка": 2, "автоматизация": 2,
    "лидогенерация": 3, "конверсия": 2,
    # Маркетинг
    "контент-маркетинг": 2, "smm": 2, "email": 1,
    # Аналитика
    "дашборд": 2, "аналитика": 1, "метрики": 2,
    # Медиа / Парсинг
    "парсинг": 2, "scraping": 2, "rss": 1,
    "youtube": 2, "транскрибация": 3, "whisper": 3,
}

STOP_KEYWORDS = [
    "gamedev", "counter-strike", "factorio", "unity", "unreal",
    "блокчейн", "crypto", "nft", "web3",
    "arduino", "raspberry", "электроника", "схема", "паяльник",
]

# ── Карта агентов экосистемы ───────────────────────────────────────────────────
ECOSYSTEM = """
Наша AI-экосистема состоит из следующих компонентов:

- **ai-eggs** (Python) — AI-агент для птицеводческого бизнеса (Азовский инкубатор).
  Агенты: Заботкина (CRM, Bitrix24), Птенчикова (контент, VK, OK).
  Модули: Habr-дайджест, фото-каскад, публикация на Авито.

- **ai-bureau** (Vite+React+TS) — Агентство AI-систем. RAG, GEO, кастомные агенты.
  Агенты: Игорек (архитектор), Кулибин (DevOps/интеграции), Артемий (фронтенд),
  Маркетолог (SEO/GEO/AEO), Шекспир (контент E-E-A-T), Шерл (разведка рынка).

- **ai-scout** (React+Vite+TS+Supabase) — Сбор и саммари из Telegram и YouTube.
  Библиотека избранного контента.

- **ai-sinergy** — Поиск и генерация новых идей и стартапов.

- **agent-lab** (Python) — Лаборатория: LLM-каскад, поисковый каскад, фото-каскад.
  Прототипы и эксперименты перед боевым деплоем.

- **tools/** (глобальные скрипты) — chronicle.sh, morning_dream.sh,
  habr_intelligence.py и другие общесистемные инструменты.
"""

# ── RSS-парсинг ────────────────────────────────────────────────────────────────

def fetch_hub_rss(hub: str, max_items: int = 15) -> list[dict]:
    url = f"https://habr.com/ru/rss/hub/{hub}/all/"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Antigravity-HabrIntelligence/2.0"})
        if resp.status_code != 200:
            print(f"  ⚠ {hub}: HTTP {resp.status_code}")
            return []
        root = ET.fromstring(resp.content)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title       = item.findtext("title", "")
            link        = item.findtext("link", "")
            description = item.findtext("description", "")
            pub_date    = item.findtext("pubDate", "")
            categories  = [c.text for c in item.findall("category") if c.text]
            desc_clean  = re.sub(r"<[^>]+>", "", unescape(description or ""))
            desc_clean  = re.sub(r"\s+", " ", desc_clean).strip()[:400]
            items.append({
                "title": title, "link": link,
                "description": desc_clean, "pub_date": pub_date,
                "categories": categories, "hub": hub,
            })
        return items
    except Exception as e:
        print(f"  ⚠ {hub}: {e}")
        return []


# ── Скоринг ───────────────────────────────────────────────────────────────────

def score_article(article: dict) -> int:
    text = f"{article['title']} {article['description']} {' '.join(article['categories'])}".lower()
    score = 0
    matched: list[str] = []
    for kw, w in KEYWORDS.items():
        if kw.lower() in text:
            score += w * 10
            matched.append(kw)
    for stop in STOP_KEYWORDS:
        if stop.lower() in text:
            score -= 25
    article["_score"]    = max(score, 0)
    article["_keywords"] = matched
    return article["_score"]


# ── LLM-анализ ────────────────────────────────────────────────────────────────

def _build_prompt(article: dict) -> str:
    return f"""Ты — архитектор AI-экосистемы Antigravity. Тебе нужно дать короткую (2-3 предложения) практическую рекомендацию: как идею или технику из статьи можно применить в нашей системе.

{ECOSYSTEM}

СТАТЬЯ:
Заголовок: {article['title']}
Описание: {article['description'][:300]}
Теги: {', '.join(article['categories'][:5])}

Ответь СТРОГО в формате:
ПРИМЕНЕНИЕ: <2-3 предложения: что конкретно сделать и зачем>
ПРОЕКТ: <одно из: ai-eggs | ai-bureau | ai-scout | ai-sinergy | agent-lab | tools>
АГЕНТ: <одно из: Кулибин | Игорек | Маркетолог | Заботкина | Артемий | Шерл | Шекспир | —>
"""


def analyze_with_gemini(article: dict) -> dict:
    """LLM-анализ через Gemini REST API. Пробует основной, потом резервный ключ."""
    for key in filter(None, [GEMINI_KEY, GEMINI_BACKUP]):
        try:
            proxies = {}
            if PROXY_URL:
                proxies = {"https": PROXY_URL, "http": PROXY_URL}
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={key}"
            )
            payload = {
                "contents": [{"parts": [{"text": _build_prompt(article)}]}],
                "generationConfig": {"maxOutputTokens": 256, "temperature": 0.4},
            }
            resp = requests.post(url, json=payload, timeout=20, proxies=proxies)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return _parse_llm_response(text)
            elif resp.status_code == 429:
                print(f"  ⚠ Gemini 429 (квота), пробую резерв...")
                continue
            else:
                print(f"  ⚠ Gemini {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"  ⚠ Gemini error: {e}")
    return {"применение": "—", "проект": "—", "агент": "—"}


def analyze_with_openrouter(article: dict) -> dict:
    """Fallback: LLM-анализ через OpenRouter."""
    if not OPENROUTER_KEY:
        return {"применение": "—", "проект": "—", "агент": "—"}
    for model in ["google/gemini-2.0-flash-001", "deepseek/deepseek-chat", "qwen/qwen-turbo"]:
        try:
            proxies = {}
            if PROXY_URL:
                proxies = {"https": PROXY_URL, "http": PROXY_URL}
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": _build_prompt(article)}],
                    "max_tokens": 256,
                },
                timeout=25,
                proxies=proxies,
            )
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"]
                return _parse_llm_response(text)
            else:
                print(f"  ⚠ OpenRouter/{model}: {resp.status_code}")
        except Exception as e:
            print(f"  ⚠ OpenRouter error: {e}")
    return {"применение": "—", "проект": "—", "агент": "—"}


def _parse_llm_response(text: str) -> dict:
    result = {"применение": "—", "проект": "—", "агент": "—"}
    for line in text.strip().splitlines():
        if line.startswith("ПРИМЕНЕНИЕ:"):
            result["применение"] = line.replace("ПРИМЕНЕНИЕ:", "").strip()
        elif line.startswith("ПРОЕКТ:"):
            result["проект"] = line.replace("ПРОЕКТ:", "").strip()
        elif line.startswith("АГЕНТ:"):
            result["агент"] = line.replace("АГЕНТ:", "").strip()
    return result


def analyze_article(article: dict) -> dict:
    """Каскад: сначала Gemini, потом OpenRouter."""
    print(f"    🧠 LLM-анализ: {article['title'][:55]}...")
    result = analyze_with_gemini(article)
    if result["применение"] == "—" and OPENROUTER_KEY:
        result = analyze_with_openrouter(article)
    article["_llm"] = result
    return article


# ── Telegram ──────────────────────────────────────────────────────────────────

def send_telegram(text: str) -> bool:
    if not TELEGRAM_TOKEN:
        print("⚠ ANGELOCHKA_BOT_TOKEN не задан")
        return False
    proxies = {}
    if PROXY_URL:
        p = PROXY_URL.replace("socks5://", "socks5h://")
        proxies = {"https": p, "http": p}
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": OWNER_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, proxies=proxies, timeout=30)
        if resp.status_code == 200:
            print(f"✅ Отправлено в TG (chat_id={OWNER_CHAT_ID})")
            return True
        else:
            print(f"⚠ TG error: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"⚠ TG send error: {e}")
    return False


# ── Форматирование ────────────────────────────────────────────────────────────

def format_digest(articles: list[dict]) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    lines = [
        f"🧠 <b>HABR INTELLIGENCE — {today}</b>",
        "",
    ]
    for i, art in enumerate(articles, 1):
        score = art["_score"]
        stars = "⭐⭐⭐" if score >= 40 else ("⭐⭐" if score >= 20 else "⭐")
        kw_str = ", ".join(art["_keywords"][:3]) or art["hub"]
        llm = art.get("_llm", {})
        применение = llm.get("применение", "—")
        проект     = llm.get("проект", "—")
        агент      = llm.get("агент", "—")

        lines.append(f"{i}. <a href=\"{art['link']}\">{art['title']}</a>")
        lines.append(f"   {stars} | {kw_str}")
        if применение != "—":
            lines.append(f"   💡 {применение}")
            lines.append(f"   📂 {проект} · 🤖 {агент}")
        lines.append("")

    lines += ["─" * 20, "Antigravity · Habr Intelligence v2"]
    return "\n".join(lines)


# ── Дедупликация ──────────────────────────────────────────────────────────────

def load_sent_links() -> set[str]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return set(json.load(f).get("sent_links", []))
        except Exception:
            pass
    return set()


def save_sent_links(links: set[str]) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"sent_links": list(links)[-300:], "last_run": datetime.now().isoformat()}, f)


# ── Главная функция ───────────────────────────────────────────────────────────

def run(dry_run: bool = False) -> None:
    print(f"\n{'='*55}")
    print(f"HABR INTELLIGENCE v2 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*55}\n")

    sent_links = load_sent_links()
    all_articles: list[dict] = []

    for hub in HABR_HUBS:
        print(f"  📡 Хаб: {hub}")
        items = fetch_hub_rss(hub)
        all_articles.extend(items)
        print(f"     → {len(items)} статей")

    print(f"\nВсего: {len(all_articles)} статей")

    # Дедупликация
    seen: set[str] = set()
    unique: list[dict] = []
    for art in all_articles:
        if art["link"] not in seen and art["link"] not in sent_links:
            seen.add(art["link"])
            unique.append(art)
    print(f"Новых уникальных: {len(unique)}")

    # Скоринг
    for art in unique:
        score_article(art)

    ranked = sorted(unique, key=lambda x: x["_score"], reverse=True)
    relevant = [a for a in ranked if a["_score"] > 0]
    print(f"Релевантных (score > 0): {len(relevant)}\n")

    if not relevant:
        print("Нет релевантных статей. Пропускаю.")
        return

    top5 = relevant[:5]
    print("ТОП-5:")
    for art in top5:
        print(f"  [{art['_score']:3d}] {art['title'][:65]}")

    # LLM-анализ
    print("\n🧠 LLM-анализ...")
    for art in top5:
        analyze_article(art)

    digest = format_digest(top5)
    print(f"\n{'─'*55}\n{digest}\n{'─'*55}")

    if dry_run:
        print("\n[DRY RUN] В Telegram не отправляем.")
        return

    if send_telegram(digest):
        sent_links.update(a["link"] for a in top5)
        save_sent_links(sent_links)
        print("State сохранён.")
    else:
        print("⚠ Не удалось отправить. State НЕ обновлён.")


# ── Точка входа ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Habr Intelligence v2")
    parser.add_argument("--dry-run", action="store_true", help="Не отправлять в Telegram")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
