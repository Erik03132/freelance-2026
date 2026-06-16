# Habr Intelligence v2 — Расширение источников

## Цель
Добавить полнотекстовый анализ Habr-статей, парсинг VC.ru и GitHub Trending, и парсинг публичных Telegram-каналов в единый пайплайн Habr Intelligence v2.

## Источники

### 1. Habr — Полный текст
- Текущий: RSS сниппет (300 символов) для всех статей
- Цель: после скоринга, для ТОП-5 статей фетчим полный HTML статьи с `habr.com/ru/post/{id}/`
- Парсинг: `html2text` или regex — вытащить содержимое статьи (чистый текст)
- LLM-промпт использует полный текст вместо сниппета

### 2. VC.ru
- RSS: `https://vc.ru/rss` (тот же формат XML, что и Habr)
- Парсинг: `feedparser` или ручной ET.parse (как Habr)
- Скоринг: те же ключевые слова
- Hub-тег: `vc`

### 3. GitHub Trending
- Скрап: `https://github.com/trending`
- Парсинг HTML: repo name + description + stars
- Скоринг: по описанию и названию
- Hub-тег: `github`

### 4. Telegram (публичные каналы)
- Скрап: `https://t.me/s/{channel}` — HTML посты
- Каналы: @vibecoding_tg, @dailyprompts, @geekneural, @neyroseti_dr
- Парсинг: каждый пост → title (первые 100 символов), description (полный текст), link
- Скоринг: те же ключевые слова
- Hub-тег: `telegram/{channel}`

## Архитектура

```python
fetch_all_sources() -> list[dict]:
    habr_articles = fetch_habr_rss(HABR_HUBS)
    vc_articles   = fetch_vc_rss()
    github_items  = fetch_github_trending()
    tg_posts      = fetch_telegram_channels(TG_CHANNELS)

    all = deduplicate(habr + vc + github + tg)
    all = score(all)
    top5 = sorted(all, key=score)[:5]
    top5 = fetch_full_text(top5)  # для Habr-статей
    top5 = llm_analyze(top5)
    format_digest(top5)
```

- Дедупликация — по уникальному идентификатору (link/tg link)
- Топ-5 — общий для всех источников (склеиваем, сортируем, берём топ)
- LLM-анализ — для топ-5 с подписью источника
- Формат дайджеста — с указанием источника

## Формат дайджеста
```
🧠 HABR INTELLIGENCE — 16.06.2026

📡 Habr
1. Заголовок (ссылка)
   ⭐⭐⭐ | python, seo
   🔥 Фича
   📊 8/10 — полезно для SEO
   📋 Шаги
   📂 ai-bureau · 🤖 Маркетолог · СТАВИМ

📡 Telegram / @vibecoding_tg
2. Заголовок
   ...

📡 VC.ru
3. ...

📡 GitHub Trending
4. ...
```

## Конфиг
```python
TG_CHANNELS = [
    "vibecoding_tg",
    "dailyprompts",
    "geekneural",
    "neyroseti_dr",
]
```

## Файлы
- `tools/habr_intelligence.py` — основной файл (все изменения здесь)

## Тестирование
- `--dry-run` — уже есть, выводит дайджест в консоль
- Тест: прогнать каждый источник по отдельности, проверить вывод
