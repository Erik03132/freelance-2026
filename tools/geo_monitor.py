#!/usr/bin/env python3
"""
GEO-мониторинг — мультисайтовый монитор видимости в AI-поисковиках.
Проверяет все зарегистрированные сайты экосистемы (или конкретный).
Отправляет отчёт в Telegram.

Запуск:
  python3 tools/geo_monitor.py                      # все сайты, 25 запросов
  python3 tools/geo_monitor.py --site ai-bureau     # только ai-bureau.pro
  python3 tools/geo_monitor.py --site vezemcip      # только vezemcip.ru
  python3 tools/geo_monitor.py --dry-run            # тест: 3 запроса, без TG
  python3 tools/geo_monitor.py --queries 10         # кастомное число запросов
  python3 tools/geo_monitor.py --engine perplexity  # только Perplexity

Добавление нового сайта:
  Внести запись в SITES_CONFIG ниже — и он автоматически попадёт в мониторинг.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Загружаем .env из ai-eggs (мастер-файл ключей)
ENV_PATH = Path(__file__).parent.parent / "ai-eggs" / ".env"
load_dotenv(ENV_PATH)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Конфигурация ────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("ANGELOCHKA_BOT_TOKEN", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_TELEGRAM_ID", "176203333"))

# Прокси: сначала SSH-туннель, fallback — прямой SOCKS5
PROXY_TUNNEL = "socks5h://localhost:1080"
PROXY_DIRECT = os.environ.get("ALL_PROXY", "socks5://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469")

# ─── РЕЕСТР САЙТОВ ────────────────────────────────────────────────────────────
# Добавь сюда любой новый сайт — и он попадёт в мониторинг автоматически.
# Формат:
#   "key": {
#       "name": "Отображаемое имя",
#       "domain": "домен.ru",
#       "brand_patterns": [r"regex1", r"regex2"],   # что ищем в ответах AI
#       "queries": ["запрос1", "запрос2", ...],      # целевые вопросы
#   }

SITES_CONFIG: dict[str, dict] = {
    # ── AI Bureau (агентство) ────────────────────────────────────────────────
    "ai-bureau": {
        "name": "AI Bureau",
        "domain": "ai-bureau.pro",
        "brand_patterns": [
            r"ai[-\s]?bureau\.pro",
            r"ai[-\s]?bureau",
            r"antigravity\s*ai",
            r"антигравити",
        ],
        "queries": [
            "кто делает AI ботов для бизнеса в России",
            "AI бюро для малого бизнеса Россия",
            "создать чат-бота для бизнеса на нейросетях",
            "разработка AI агента для CRM",
            "как сделать Telegram бота с GPT",
            "RAG система для корпоративной базы знаний",
            "AI продавец для интернет-магазина",
            "автоматизация продаж с помощью нейросетей",
            "AI ассистент для отдела продаж",
            "интеграция ChatGPT в CRM Bitrix24",
            "нейросеть для обработки заявок",
            "голосовой AI бот для звонков",
            "лучшее AI агентство России 2026",
            "аутсорсинг AI разработки Россия",
            "AI автоматизация бизнеса малый бизнес цена",
            "GEO оптимизация сайта для нейропоиска",
            "llms.txt что это и зачем нужен",
            "как AI агент может заменить менеджера по продажам",
            "стоимость разработки AI бота для бизнеса 2026",
            "примеры внедрения AI в малый бизнес",
            "AI bureau what is it",
            "Antigravity AI bureau Russia",
            "AI Bureau pro",
            "ai-bureau.pro отзывы",
            "Antigravity AI агентство",
        ],
    },

    # ── VezemCip (инкубатор, птицеводство) ───────────────────────────────────
    "vezemcip": {
        "name": "ВезёмЦыплят",
        "domain": "vezemcip.ru",
        "brand_patterns": [
            r"vezemcip\.ru",
            r"везёмцыплят",
            r"везем\s*цыплят",
            r"азовский\s*инкубатор",
            r"incubird",
        ],
        "queries": [
            "купить цыплят бройлеров оптом Россия",
            "цыплята бройлеры с доставкой",
            "где купить суточных цыплят",
            "инкубатор цыплята Азов Ростов",
            "купить индюшат утят суточных",
            "птица для домашнего хозяйства купить",
            "бройлеры Кобб 500 купить",
            "цыплята Росс 308 оптом",
            "доставка птицы по России инкубатор",
            "птица для откорма купить недорого",
            "cыплята несушки купить",
            "Ломан Браун суточные цыплята",
            "откуда берут цыплят фермеры",
            "poultry chicks Russia buy",
            "vezemcip отзывы",
        ],
    },
}

# ─── API-функции ──────────────────────────────────────────────────────────────

async def _make_client(proxy: str) -> httpx.AsyncClient:
    """Создаём httpx-клиент с указанным прокси."""
    return httpx.AsyncClient(
        proxy=proxy,
        timeout=60.0,
        follow_redirects=True,
    )


async def query_openrouter(query: str, model: str, client: httpx.AsyncClient) -> str:
    """Запрос к OpenRouter API. Возвращает текст ответа."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 600,
    }
    try:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-bureau.pro",
                "X-Title": "GEO Monitor",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        log.warning("OpenRouter error [%s]: %s", model, e)
        return ""


def extract_brand_hit(text: str) -> bool:
    """Проверяет, упоминается ли наш бренд в тексте ответа."""
    return bool(BRAND_RE.search(text))


def extract_competitors(text: str, top_n: int = 5) -> list[str]:
    """
    Извлекает домены/бренды конкурентов из текста ответа.
    Ищет паттерны вида site.ru, company.com и т.п.
    """
    domain_re = re.compile(
        r"\b([a-zA-Zа-яА-Я0-9-]{2,30}\.(ru|com|pro|io|ai|org|рф))\b",
        re.IGNORECASE,
    )
    # Исключаем наш бренд и служебные домены
    exclusions = {
        "ai-bureau.pro", "openrouter.ai", "openai.com", "perplexity.ai",
        "google.com", "yandex.ru", "wikipedia.org", "chatgpt.com",
    }
    found = [m.group(0).lower() for m in domain_re.finditer(text)]
    return [d for d in found if d not in exclusions][:top_n]


# ─── Движки (выбор модели) ────────────────────────────────────────────────────

ENGINES = {
    "perplexity": "perplexity/sonar",
    "gpt": "openai/gpt-4o-mini",
}


# ─── Основная логика ──────────────────────────────────────────────────────────

async def run_geo_check(
    queries: list[str],
    engines: list[str],
    dry_run: bool = False,
) -> dict:
    """
    Прогоняет все запросы через выбранные движки.
    Возвращает словарь с результатами.
    """
    results = {engine: [] for engine in engines}
    all_competitors: list[str] = []

    # Пробуем SSH-туннель, fallback на прямой прокси
    proxy = PROXY_TUNNEL
    try:
        async with await _make_client(proxy) as client:
            await client.get("https://openrouter.ai", timeout=5.0)
            log.info("Прокси: SSH туннель ✅")
    except Exception:
        log.warning("SSH туннель недоступен, fallback на прямой SOCKS5")
        proxy = PROXY_DIRECT

    async with await _make_client(proxy) as client:
        total = len(queries) * len(engines)
        done = 0

        for query in queries:
            for engine_name in engines:
                model = ENGINES[engine_name]
                log.info("[%d/%d] %s | %s | %.60s...", done + 1, total, engine_name, model, query)

                text = await query_openrouter(query, model, client)
                hit = extract_brand_hit(text)
                competitors = extract_competitors(text)
                all_competitors.extend(competitors)

                results[engine_name].append({
                    "query": query,
                    "hit": hit,
                    "snippet": text[:300] if hit else "",
                    "competitors": competitors,
                })

                done += 1

                # Небольшая задержка — не спамим API
                if not dry_run:
                    await asyncio.sleep(1.5)

    return results, all_competitors


def build_report(results: dict, all_competitors: list[str], engines: list[str]) -> str:
    """Формирует текстовый отчёт для Telegram."""
    now = datetime.now().strftime("%d.%m.%Y | %H:%M MSK")

    total_queries = sum(len(results[e]) for e in engines)
    total_hits = sum(r["hit"] for e in engines for r in results[e])
    sov = round(total_hits / total_queries * 100) if total_queries else 0

    # Строки по движкам
    engine_lines = []
    for e in engines:
        e_hits = sum(r["hit"] for r in results[e])
        e_total = len(results[e])
        pct = round(e_hits / e_total * 100) if e_total else 0
        engine_lines.append(f"  • {e.capitalize():12s}: {e_hits}/{e_total} ({pct}%)")

    # Запросы с попаданием
    hit_queries = []
    for e in engines:
        for r in results[e]:
            if r["hit"]:
                hit_queries.append(f'  ✅ «{r["query"][:60]}» [{e}]')

    hit_section = "\n".join(hit_queries[:10]) if hit_queries else "  ❌ Нет упоминаний"

    # Топ конкурентов
    comp_counter = Counter(all_competitors).most_common(5)
    comp_lines = "\n".join(
        f"  {i+1}. {domain} ({cnt} упом.)"
        for i, (domain, cnt) in enumerate(comp_counter)
    ) or "  Данных нет"

    # Вывод-рекомендация
    if sov >= 30:
        verdict = "🟢 Отлично! SoV ≥30% — бренд хорошо видим в AI."
        action = "Продолжать текущую контент-стратегию."
    elif sov >= 10:
        verdict = "🟡 Умеренно. SoV 10–30% — есть прогресс."
        action = "Усилить публикации кейсов на VC.ru / Habr с триплетами."
    else:
        verdict = "🔴 Слабо. SoV < 10% — бренд почти не цитируется."
        action = "Срочно: 2 кейса на VC.ru + обновить Schema.org + добавить FAQ-блоки."

    report = f"""📊 *GEO-МОНИТОРИНГ ai\\-bureau\\.pro*
🗓 {now}

🔍 Запросов проверено: *{total_queries}*
✅ Упоминаний бренда: *{total_hits}/{total_queries}* ({sov}%)
🏆 Share of Voice: *{sov}%*

📈 *По движкам:*
{chr(10).join(engine_lines)}

🎯 *Запросы с упоминанием:*
{hit_section}

👥 *Конкуренты в ответах:*
{comp_lines}

💡 *Вывод:* {verdict}
📌 *Действие:* {action}"""

    return report


async def send_telegram(text: str, chat_id: int) -> bool:
    """Отправляет сообщение в Telegram (MarkdownV2)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    # TG может идти напрямую
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, json=payload)
            if r.status_code == 200:
                log.info("Telegram ✅ отправлено в chat %d", chat_id)
                return True
            log.warning("Telegram ответил: %s", r.text[:200])
    except Exception as e:
        log.exception("Ошибка отправки TG: %s", e)
    # Fallback через прокси
    try:
        async with httpx.AsyncClient(proxy=PROXY_DIRECT, timeout=30.0) as client:
            r = await client.post(url, json=payload)
            return r.status_code == 200
    except Exception as e:
        log.exception("Ошибка TG через прокси: %s", e)
        return False


def save_json_result(results: dict, engines: list[str], sov: int) -> Path:
    """Сохраняет сырые результаты в JSON для истории."""
    out_dir = Path(__file__).parent.parent / "reports"
    out_dir.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    out_path = out_dir / f"geo_monitor_{date_str}.json"
    data = {
        "date": date_str,
        "sov_pct": sov,
        "engines": engines,
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info("Результаты сохранены: %s", out_path)
    return out_path


# ─── Entrypoint ───────────────────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(description="GEO-мониторинг — мультисайтовый монитор")
    parser.add_argument("--dry-run", action="store_true", help="Тест: 3 запроса, без отправки TG")
    parser.add_argument("--queries", type=int, default=25, help="Число запросов на сайт (дефолт 25)")
    parser.add_argument("--engine", choices=["perplexity", "gpt", "both"], default="both",
                        help="Движок для проверки")
    parser.add_argument("--site", choices=list(SITES_CONFIG.keys()) + ["all"], default="all",
                        help="Сайт для мониторинга (дефолт: все)")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        log.error("OPENROUTER_API_KEY не найден. Проверь ai-eggs/.env")
        sys.exit(1)

    # Выбор движков
    if args.engine == "both":
        engines = ["perplexity", "gpt"]
    else:
        engines = [args.engine]

    # Выбор сайтов
    sites_to_check = (
        {args.site: SITES_CONFIG[args.site]}
        if args.site != "all"
        else SITES_CONFIG
    )

    log.info("=== GEO-МОНИТОРИНГ | dry_run=%s | сайты: %s | движки: %s ===",
             args.dry_run, list(sites_to_check.keys()), engines)

    all_reports: list[str] = []

    for site_key, site_cfg in sites_to_check.items():
        # Задаём бренд-паттерны для этого сайта
        global BRAND_RE
        BRAND_RE = re.compile("|".join(site_cfg["brand_patterns"]), re.IGNORECASE)

        # Выбор запросов
        queries = site_cfg["queries"]
        n = min(3, len(queries)) if args.dry_run else min(args.queries, len(queries))
        selected_queries = queries[:n]

        log.info("--- Сайт: %s (%s) | %d запросов ---",
                 site_cfg["name"], site_cfg["domain"], n)

        results, all_competitors = await run_geo_check(selected_queries, engines, args.dry_run)

        # Статистика
        total_queries = sum(len(results[e]) for e in engines)
        total_hits = sum(r["hit"] for e in engines for r in results[e])
        sov = round(total_hits / total_queries * 100) if total_queries else 0

        # Отчёт для этого сайта (подставляем имя сайта)
        report = build_report(results, all_competitors, engines)
        report = report.replace(
            "GEO\\-МОНИТОРИНГ ai\\-bureau\\.pro",
            f"GEO\\-МОНИТОРИНГ {site_cfg['name'].replace('-', '\\-')}",
        )
        all_reports.append(report)
        print("\n" + "─" * 60)
        print(report)
        print("─" * 60 + "\n")

        save_json_result(results, engines, sov)

    # Отправка TG — один за другим
    if not args.dry_run:
        for report in all_reports:
            sent = await send_telegram(report, ADMIN_CHAT_ID)
            if sent:
                log.info("Отчёт отправлен в Telegram ✅")
            else:
                log.warning("Telegram недоступен. Отчёт только в stdout.")
            await asyncio.sleep(2)  # пауза между сообщениями
    else:
        log.info("DRY-RUN: TG не отправлен (%d отчётов)", len(all_reports))


if __name__ == "__main__":
    asyncio.run(main())
