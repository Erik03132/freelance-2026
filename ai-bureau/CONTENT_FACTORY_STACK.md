# Content Factory — Technical Stack

---

## 🧠 Core (генерация)

| Компонент | Технология | Конфигурация |
|-----------|-----------|-------------|
| LLM | OmniRoute (`omni-auto`) | `http://217.149.23.113:20128/v1` |
| Fallback LLM | OpenRouter / локальная Ollama | `openrouter/deepseek-chat` |
| RAG-контекст | ChromaDB / JSON-индексы | `global_knowledge/` + кейсы |
| Prompt templates | YAML + Jinja2 | `content-factory/templates/*.yaml` |
| Валидация | Expert CLI (Grill-Me) | `modules/expert_cli/` |

**Язык:** Python 3.10+
**Запросы:** `requests` / `httpx` (async)

---

## 🔌 API Площадок

| Площадка | API | Метод | Авторизация |
|----------|-----|-------|-------------|
| **Telegram** | Bot API | `sendMessage`, `sendPhoto` | `BOT_TOKEN` |
| **VK** | VK API | `wall.post`, `photos.getUploadServer` | `VK_SERVICE_TOKEN` / `VK_USER_TOKEN` |
| **Яндекс Дзен** | RSS-лента | Автоподгрузка из `/rss.xml` | Без API |

**Библиотеки:** `python-telegram-bot`, `vk-api`, `feedparser`

---

## 🗄 Хранение

| Данные | Где | Формат |
|--------|-----|--------|
| Контент-план | `content-factory/calendar/` | JSON / YAML |
| Опубликованные посты | `global_knowledge/library/content/` | Markdown + JSON |
| Медиа (изображения) | `public/content/` | PNG / WebP |
| Аналитика | `content-factory/analytics/` | SQLite / JSON |
| Черновики | `content-factory/drafts/` | Markdown |

---

## 🚀 Инфраструктура

| Компонент | Хост | Статус |
|-----------|------|--------|
| OmniRoute | VPS 217.149.23.113:20128 | ✅ Есть |
| VPS (сервер) | 217.149.23.113 | ✅ Есть |
| Cron / Scheduler | systemd timer / PM2 | 🆕 Настроить |
| База данных | SQLite (локально) | ✅ Есть |
| Хранилище | Файловая система VPS | ✅ Есть |

---

## 📦 Зависимости

```txt
# requirements.txt
requests>=2.31
pyyaml>=6.0
jinja2>=3.1
python-telegram-bot>=20.0
vk-api>=11.0
feedparser>=6.0
pillow>=10.0
schedule>=1.2
```

---

## 🔄 Pipeline (полный цикл)

```bash
# 1. Сгенерировать контент
python3 brain/generator.py --topic "Голосовой агент для доставки" --type case --platform habr

# 2. Проверить через Expert CLI
./expert start "Вычитай этот пост: $(cat draft.md)"

# 3. Адаптировать под площадку
python3 adapters/telegram.py --input draft.md --output tg_post.md

# 4. Опубликовать
python3 publisher/telegram_bot.py --file tg_post.md --image screenshot.png

# 5. Записать в историю
python3 tracker/log.py --platform telegram --post-id 123 --status published
```

---

**Состав площадок:** Telegram ✅ · VK ✅ · Яндекс Дзен (RSS) ✅
**Всё остальное** (Habr, YouTube, VC.ru, МАКС) — пока не берём.

**Итог:** Вся инфраструктура уже есть. Добавить нужно только RSS-ленту для Дзен и адаптировать генерацию под три формата.

---

## 🎯 Фокус: Яндекс Дзен (первая площадка)

### Формат взаимодействия
**Не API, а RSS-лента.** Дзен сам забирает контент:

```
AI Bureau → astro build → /rss.xml → Яндекс Дзен → автопубликация
```

### Настройка
1. Добавить `@astrojs/rss` в проект (уже есть `@astrojs/sitemap` — аналогично)
2. Создать `src/pages/rss.xml.js`:
   ```js
   import rss from '@astrojs/rss';
   export const get = () => rss({
     title: 'AI Bureau',
     description: 'AI-агенты, RAG, голосовые боты',
     site: 'https://ai-bureau.pro',
     items: import.meta.glob('./blog/*.md'),
   });
   ```
3. В канале Дзен указать `https://ai-bureau.pro/rss.xml`
4. Готово — Дзен сам публикует статьи

### Плюсы
- ✅ Бесплатно
- ✅ Никакого API
- ✅ Автоматически
- ✅ Индексация Яндекса

### Минусы
- ⏱ Задержка 15-60 мин до публикации
- 📝 Только статьи (не подходит для коротких постов)
- 🔄 Нет двусторонней связи (не отвечает на комментарии через API)
