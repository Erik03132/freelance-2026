"""
RSS-мониторинг: парсит ленты федеральных и региональных источников.
Запускается по расписанию через scheduler.py.
"""
import os
import json
import hashlib
import time
from datetime import datetime, timedelta

import feedparser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SEEN_PATH = os.path.join(DATA_DIR, "rss_seen.json")
RAW_DIR = os.path.join(DATA_DIR, "raw_feed")
os.makedirs(RAW_DIR, exist_ok=True)

# === Конфигурация RSS-источников ===
RSS_FEEDS = {
    # Федеральное законодательство и власть
    "government_ru": {
        "url": "http://government.ru/all/rss/",
        "category": "federal_executive",
        "priority": "high",
        "name": "Правительство РФ",
    },
    "kremlin_ru": {
        "url": "http://kremlin.ru/events/all/rss",
        "category": "federal_president",
        "priority": "high",
        "name": "Президент РФ — События",
    },
    # Профильные СМИ
    "rbc_politics": {
        "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
        "category": "media",
        "priority": "medium",
        "name": "РБК — Новости",
    },
    "tass_politics": {
        "url": "https://tass.ru/rss/v2.xml",
        "category": "media",
        "priority": "high",
        "name": "ТАСС",
    },
    "kommersant_law": {
        "url": "https://www.kommersant.ru/RSS/news.xml",
        "category": "media",
        "priority": "medium",
        "name": "Коммерсантъ",
    },
    "interfax": {
        "url": "https://www.interfax.ru/rss.asp",
        "category": "media",
        "priority": "medium",
        "name": "Интерфакс",
    },
    # Парламентские источники
    "pnp_ru": {
        "url": "https://www.pnp.ru/rss/index.xml",
        "category": "parliament",
        "priority": "high",
        "name": "Парламентская газета",
    },
    # Башкортостан
    "bash_inform": {
        "url": "https://www.bashinform.ru/rss/",
        "category": "bashkortostan",
        "priority": "high",
        "name": "БашИнформ — Новости Башкортостана",
    },
    # Право и регуляторика
    "garant_ru": {
        "url": "https://www.garant.ru/rss/hotlaw/",
        "category": "federal_law",
        "priority": "high",
        "name": "Гарант — Горячие документы",
    },
}


def _load_seen():
    """Загрузка уже обработанных записей."""
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_seen(seen):
    """Сохранение обработанных записей."""
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False)


def _entry_hash(entry):
    """Уникальный хеш записи."""
    text = (entry.get("title", "") + entry.get("link", "")).encode("utf-8")
    return hashlib.md5(text).hexdigest()


def scan_all_feeds(max_age_hours=48):
    """
    Сканирует все RSS-ленты, возвращает список новых записей.
    
    Returns:
        list[dict]: Новые записи с полями:
            - title, link, summary, published
            - source_id, source_name, category, priority
    """
    seen = _load_seen()
    new_items = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)

    for source_id, config in RSS_FEEDS.items():
        url = config["url"]
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                print(f"  ⚠️ {source_id}: RSS недоступен — {feed.bozo_exception}")
                continue

            count = 0
            for entry in feed.entries[:20]:  # Берём последние 20
                h = _entry_hash(entry)
                if h in seen:
                    continue

                # Парсим дату публикации
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published = datetime(*entry.published_parsed[:6])
                        if published < cutoff:
                            continue  # Слишком старая запись
                    except Exception:
                        pass

                item = {
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", ""))[:1000],
                    "published": published.isoformat() if published else datetime.now().isoformat(),
                    "source_id": source_id,
                    "source_name": config["name"],
                    "category": config["category"],
                    "priority": config["priority"],
                    "scraped_at": datetime.now().isoformat(),
                }
                new_items.append(item)
                seen[h] = time.time()
                count += 1

            if count:
                print(f"  📰 {source_id}: +{count} новых записей")

        except Exception as e:
            print(f"  ❌ {source_id}: ошибка — {e}")

    # Чистим старые хеши (> 7 дней)
    week_ago = time.time() - 7 * 86400
    seen = {k: v for k, v in seen.items() if v > week_ago}
    _save_seen(seen)

    # Сохраняем сырые данные в файл
    if new_items:
        today = datetime.now().strftime("%Y-%m-%d")
        raw_path = os.path.join(RAW_DIR, f"feed_{today}.json")
        existing = []
        if os.path.exists(raw_path):
            with open(raw_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.extend(new_items)
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"📡 RSS ИТОГО: {len(new_items)} новых записей из {len(RSS_FEEDS)} источников")
    return new_items


def scan_feed_by_id(source_id):
    """Сканирует один конкретный источник."""
    if source_id not in RSS_FEEDS:
        print(f"❌ Источник '{source_id}' не найден")
        return []

    config = RSS_FEEDS[source_id]
    seen = _load_seen()
    items = []

    try:
        feed = feedparser.parse(config["url"])
        for entry in feed.entries[:10]:
            h = _entry_hash(entry)
            if h in seen:
                continue
            items.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:1000],
                "source_id": source_id,
                "source_name": config["name"],
                "category": config["category"],
            })
            seen[h] = time.time()
    except Exception as e:
        print(f"❌ {source_id} error: {e}")

    _save_seen(seen)
    return items


if __name__ == "__main__":
    print("🔍 Запуск полного сканирования RSS...")
    items = scan_all_feeds()
    for item in items[:5]:
        print(f"\n  📋 {item['source_name']}: {item['title']}")
        print(f"     {item['link']}")
