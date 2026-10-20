# STATUS — 2026-09-22 20:30

## КАЧЕСТВО ОТВЕТОВ: eval 11/11 (100%) ✅

**Программа улучшений качества выполнена (eval → каталог → LightRAG):**

| Шаг | Что | Результат |
|-----|-----|-----------|
| 1. Eval-набор | 11 золотых вопросов, `kb-prep eval` (CI для RAG) | baseline был 10/11 |
| 2. Каталог Доминанта | **29 карточек кроссов** regex-экстракцией (2 сек, детерминированно — LLM-вариант не осилил за час из-за rate-limit) + интеграция в /v1/search (карточка = топ-результат, score 999, не реранкуется) | **11/11 (100%)**, D853 сохранность 95-97% из карточки |
| 3. LightRAG | venv /srv/lightrag-venv (1.5.7), конфиг Nous LLM+эмбеддинги, скрипт /srv/lightrag_test.py | Инфраструктура готова; **инжест заблокирован исчерпанием free-квоты Nous** (экстракция таймаутится 480с) |

### Команды LightRAG (когда квота Nous восстановится)

```bash
# инжест справочника Доминанта (~5 мин при живой квоте):
ssh root@217.149.23.113 'cd /srv && /srv/lightrag-venv/bin/python3 lightrag_test.py --insert'
# графовый запрос (сравнения, связи):
ssh root@217.149.23.113 'cd /srv && /srv/lightrag-venv/bin/python3 lightrag_test.py "Сравни D853 и D104" hybrid'
```

### Архитектура качества ответов (итоговая)

```
Вопрос → код кросса в запросе? ──да──→ КАРТОЧКА из каталога (точные данные, 100%)
                                   └─нет→ вектор recall (MiniLM) → реранк (bge-reranker 384t)
                                          → порог 0.15 → LLM (Nous→OpenRouter free) → подвал со ссылками
Контроль: kb-prep eval (11 вопросов) после каждого изменения
```

### Уроки сессии (все в claude-mem)

- pdftotext перемалывает двухколоночные таблицы: короткие обрывки (<20 симв.) теряются при чанкинге → каталог/карточки для справочников
- Для каталогов с идентичной структурой (кроссы) — ID в payload + Qdrant-фильтр, не эмбеддинги
- Regex-экстракция регулярных таблиц детерминирована и бьёт LLM-экстракцию (2 сек vs часы, ноль галлюцинаций)
- Free-квоты (Nous/OpenRouter) исчерпываются за день активного использования — каскад моделей обязателен
- LightRAG 1.5.7: ainsert/aquery + initialize_storages + сигнатуры model= (не model_name)

---

## Сессия 2026-09-22 15:45 — ССЫЛКИ НА ИСТОЧНИКИ ✅

**Verified:** после каждого RAG-ответа бот добавляет подвал с прямыми ссылками
на PDF-исходники (программно, не через LLM — ссылки не галлюцинируют):

```
📚 Источники:
📖 Руководство по выращиванию уток Черри Велли: https://vezemcip.ru/books/cherry_valley.pdf
📖 Руководство по инкубации (2020): https://vezemcip.ru/books/russian_hatchery_guide_2020.pdf
```

| Компонент | Детали |
|-----------|--------|
| PDF-библиотека | 16 книг, 66 МБ → `/var/www/books/` на VPS, слаг-имена (ASCII) |
| Nginx | `location /books/` в vezemcip (HTTPS, Cache-Control 86400) — HTTP 200, Verified |
| Маппинг | `_BOOKS_SLUGS` в angelochka_core (stem → слаг), названия RU через `_ru_source` |
| Механика | `get_answer` обёртка: сброс `_last_rag_sources` на запрос → `_get_vector_context` фиксирует источники → подвал после ответа; лимит ТГ 4096 соблюдён (режем ответ, не подвал) |
| Каналы | Работает везде: ТГ, сайт, Битрикс (подвал в get_answer) |

---

## LLM-КАСКАД: Nous (longcat:free) → OpenRouter (free) ✅

**Verified end-to-end:** вопрос про инкубационное яйцо → RAG (3 чанка, top=0.999)
→ `✅ LLM (Nous): meituan/longcat-2.0:free` → структурированный ответ с фактами
(13–15°C, влажность 75–80%, до 18°C в жарком климате) и ссылкой на источник
(«Руководство по выращиванию уток Черри Велли»).

### Каскад call_llm (после всех патчей)

```
0. Nous Portal — meituan/longcat-2.0:free (бесплатная, ctx 1M, RU ок)
   → inference-api.nousresearch.com напрямую через US-прокси, NOUS_API_KEY в .env
1. OpenRouter напрямую (OmniRoute ОТКЛЮЧЁН — OMNI_MODELS пуст по умолчанию)
   → lite: ling-3.0-flash-vl / gemma-4-26b / nex-n2.5-pro (все :free)
   → std/pro: nemotron-3-ultra-550b / ling-3.0-flash-vl / gemma-4-26b (все :free)
2. Yandex GPT → 3. Ollama (оффлайн-страховка)
```

### Патчи этой сессии (все с бэкапами на VPS)

| Файл | Что | Бэкап |
|------|-----|-------|
| angelochka_core.py | +_get_vector_context → Knowledge API (kb_poultry) | .bak-20260922 |
| angelochka_core.py | +_call_nous (Nous первым), OmniRoute откл., free-модели в тирах | .bak2-20260922 |
| tg_bot.py | _make_session всегда через прокси; F.text → F.text.regexp(URL_RE) | .bak-20260922 |
| tool_digest.py | обрезка RAG-источника 250 → 1200 симв. (факты не режутся) | .bak-20260922 |
| .env | +NOUS_API_KEY, aiohttp-socks установлен | — |

### Именованные отказы (для истории)

- OmniRoute (127.0.0.1:20128): connection refused из кода бота при живом порте
  (ss показывает LISTEN) — причина не выяснена, ОТКЛЮЧЁН из каскада (env-флаг)
- meituan/longcat-2.0 на OpenRouter — НЕ бесплатная (402 при max_tokens=4096)
- OpenRouter баланс исчерпан — все платные модели 402
- Ollama qwen2.5:0.5b (последняя страховка) — генерирует бред, не годна для клиентов

---

## Сессия 2026-09-22 13:20 — хендлер-поглотитель F.text ✅

**Симптом:** бот отвечает «прошёл вебхук, polling работает», но на сообщения — тишина, лог пустой.

**Корень №2 (главный):** `@dp.message(F.text)` (инбокс-хендлер ссылок, ~строка 697)
матчил ЛЮБОЕ текстовое сообщение, а при отсутствии URL делал `return` с комментарием
«уходит в chat_handler» — **ложь для aiogram 3**: сработавший хендлер не передаёт
update дальше. Все тексты поглощались, chat_handler (LLM+RAG) никогда не вызывался.

**Фикс:** фильтр перенесён в декоратор — `@dp.message(F.text.regexp(URL_RE))`:
хендлер вызывается только для сообщений с URL, обычные тексты проваливаются
в catch-all `@dp.message()` → chat_handler.

**Проверено попутно:** воровства апдейтов НЕТ (при остановленном боте getUpdates
даёт 200 OK без 409; токен в hermes chief state.db — лишь старая история чата).
Меню на сервере ПУСТОЕ — «старое меню» у пользователя = кэш приложения Telegram
(лечится перезапуском приложения).

**Цепочка багов бота за сессию:** (1) crash-loop на прямом соединении с TG
(мёртвый fallback в _make_session) → (2) aiohttp-socks не установлен →
(3) хендлер-поглотитель F.text. Все три исправлены, бэкапы на VPS.

---

## БОТ @Angella26bot ПОЧИНЕН: crash-loop на прямом соединении с TG ✅

**Симптом:** бот не отвечал (597+ рестартов ещё ДО правок этой сессии).

**Корень (баг в `_make_session`):** логика «сначала прямое соединение, прокси —
fallback» была мёртвым кодом — конструктор `AiohttpSession()` не бросает
исключений, fallback недостижим. Бот всегда ходил в api.telegram.org напрямую,
а с этого VPS прямой доступ таймаутит → `delete_webhook` падал → crash-loop.

**Фикс:** сессия всегда через `TELEGRAM_PROXY` (http://...@172.120.21.141:64468,
проверен через getMe/deleteMyCommands). Потребовался `pip install aiohttp-socks`
(aiogram требует для любого прокси). Бэкап: `agent/tg_bot.py.bak-20260922`.

**Verified:** `🔌 Сессия через прокси` в логах, вебхук удалён без таймаута,
polling работает, PID стабилен, 0 критических ошибок, счётчик рестартов замер.

---

## @Angella26bot ПРИВЯЗАН К RAG-БАЗЕ ✅

**Verified 2026-09-22:** ТГ-бот @Angella26bot (pm2 `angela-bot`, id 8336409939)
отвечает на вопросы через базу kb_poultry (MiniLM + reranker).

| Что | Результат |
|-----|-----------|
| Интеграция | `angelochka_core._get_vector_context` → `POST localhost:8080/v1/search` (kb_poultry, top_k=3) — основной источник, legacy (BM25/rag_lite/FAISS/Neon) — fallback |
| Тест интеграции | ✅ 3 чанка, top=0.990, русские названия источников («Руководство по выращиванию уток Черри Велли») |
| Меню бота | ✅ Удалены ВСЕ 57 чужих команд (default + all_private_chats + all_group_chats скоупы, verified пусто). Это были команды чужой агентской системы (codex_runtime, moa, subgoal, curator...) — потому «всё не работало» |
| Рестарт | pm2 restart angela-bot, PID 355873, стабилен, polling работает |
| Бэкап | `agent/angelochka_core.py.bak-20260922` |

**Механика:** пользователь пишет вопрос → chat_handler → get_answer →
_get_vector_context → Knowledge API (recall+rerank, ~2-4с) → контекст
«📚 ЭКСПЕРТНЫЕ ДАННЫЕ» в промпт → LLM отвечает со ссылкой на руководство.

**Примечания:**
- Старый rag_lite мёртв (data/rag_knowledge/chunks.json не существует) — теперь не критично, Knowledge API первый в цепочке.
- Регистрация меню в коде и так пропускалась («hangs») — меню не вернётся.
- Telegram API с VPS только через прокси `TELEGRAM_PROXY` (172.120.21.141:64468).

---

## Сессия 2026-09-22 03:30 — Reranker v3.0

## БАЗА ЗНАНИЙ ПО ПТИЦЕВОДСТВУ — MiniLM + Reranker v3.0 ✅

**Verified 2026-09-22:** двухступенчатый поиск: MiniLM recall → cross-encoder rerank.
16 книг / 1291 чанк в Qdrant `kb_poultry`. Реранкер поднимает семантически лучшие
чанки (пример: Cherry Valley с 5+ места на 1-е по запросу про температуру).

| Компонент | Значение |
|-----------|----------|
| Рекол | paraphrase-multilingual-MiniLM-L12-v2 (384-dim, RU+EN) |
| Реранкер | BAAI/bge-reranker-base, max_length=256, 10 кандидатов |
| Латентность поиска | 2.0–3.8 с (rerank on), ~0.4 с (rerank off) |
| RAM сервиса | ~1.1 ГБ (обе модели), свободно ~1.9 ГБ |
| Конфиг env | KB_MODEL, KB_RERANKER, KB_RERANK_MAX_LENGTH=256, KB_RERANK_FETCH=10 |
| API | /v1/search {query, top_k, rerank=true/false} — rerank отключается на лету |

### Почему 256/10 (отказы с именами)

- `mixedbread-ai/mxbai-rerank-xsmall-m-v1` — 401 (репозиторий закрыт)
- `cross-encoder/mmarco-mMiniLMv2-L6-H384-v1` — не существует
- `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` — быстрый, но провалил sanity-чек
  на RU (нерелевантный чанк про воду выше релевантного про температуру)
- `BAAI/bge-reranker-base` 512/20 — качество ок, но 8.2 с на запрос (CPU 4 ядра)
- **BAAI/bge-reranker-base 256/10 — выбран**: 1.9–3.8 с, качество проверено на
  3 запросах (не хуже 512/20, на «сколько корма бройлеру» — лучше: 512/20 ставил
  первым нерелевантный чанк про упаковочную машину)

### Бэкапы на VPS

- `backups/main.py.bak-20260922` — исходный TF-IDF
- `backups/main.py.bak2-20260922-tfidf` — TF-IDF + ingest_bulk
- `backups/main.py.bak3-20260922-minilm` — MiniLM без реранкера
- `backups/main.py.bak4-20260922-reranker512` — реранкер 512/20 (медленный конфиг)

### История сессии 2026-09-22 (02:00)

1. **Диск VPS растянут**: панель показывала 70 ГБ, раздел был 49.9 ГБ →
   `growpart /dev/sda 1 && resize2fs /dev/sda1` → 20 ГБ свободно (онлайн, без даунтайма).
2. **Установлен torch CPU + sentence-transformers** в `/opt/levitan/projects/ai-eggs/.server_venv`.
3. **main.py v2.0**: TF-IDF → MiniLM, VECTOR_DIM=384, все эндпоинты сохранены
   (/health, /v1/search, /v1/ingest, /v1/ingest_bulk, /v1/collections).
4. **kb_poultry пересоздана** (была 5000-dim TF-IDF) → 384-dim MiniLM, переиндексация 16 книг.
5. **Verified**: 4 поисковых запроса, scores 0.7–0.9, источники релевантные
   (инкубация → Russian Hatchery Guide/Ross, вакцинация → Ross 308/Cobb).

---

## Сессия 2026-09-22 01:50 — TF-IDF база (первичная загрузка)

**Verified:** 16 книг / 1291 чанк, поиск RU+EN работал (TF-IDF). Исправления:
kb_poultry была ПУСТАЯ вопреки прошлым отчётам; баг переобучения TF-IDF в
/v1/ingest → добавлен /v1/ingest_bulk; Knowledge API переведён с nohup на systemd;
kb-prep восстановлен в `~/.config/opencode/tools/kb-prep/` + symlink `/opt/homebrew/bin/kb-prep`.

### Пайплайн (полностью автоматический)

```bash
kb-prep pdf ~/Documents/Литература-по-птицеводству   # PDF → JSON (дубликаты skip)
kb-prep send ./kb_output                              # → VPS bulk ingest (MiniLM)
kb-prep search "температура инкубации"                # проверка поиска
kb-prep status                                        # здоровье + счётчики
```

Зависимости на Mac: только poppler (`brew install poppler`) — OCR не нужен,
все PDF с текстовым слоем. HTTP идёт через `ssh root@217.149.23.113` (порт 8080
закрыт снаружи).

---

## История: сессия 2026-09-22 00:30

### Что сделано

| Задача | Статус |
|--------|--------|
| DNS vezemcip.ru → 217.149.23.113 | ✅ Исправлено |
| HTTPS (Let's Encrypt) | ✅ Работает |
| Порт 80 открыт | ✅ |
| Angelochka Seller (сайт) :8022 | ✅ FAQ lookup + Yandex GPT |
| Angelochka Bitrix :8023 | ✅ CRM + звонки |
| Angelochka Expert :8024 | ✅ RAG + 18 книг |
| Nginx proxy /api/ → Seller | ✅ |
| price_updater (cron 6ч) | ✅ ТГ + ВК + сайт |
| Бот-продавец 20/20 тестов | ✅ 100% |

### Архитектура ботов

```
profiles/
├── seller.py    (сайт)     — только продажи, FAQ, цены
├── bitrix.py    (Битрикс)  — звонки, CRM, задачи
└── expert.py    (ТГ)       — 18 книг + всё что знают первые два

core/
├── llm.py          — Yandex GPT + OpenRouter fallback
├── loader.py       — загрузка цен/FAQ/знаний
└── rag_service.py  — MiniLM embeddings + reranker
```

### Knowledge Platform (VPS)

| Компонент | Порт | Статус |
|-----------|------|--------|
| Qdrant (Docker) | :6333 | ✅ 3 коллекции (384-dim MiniLM) |
| Knowledge API | :8080 | ✅ ingest + search |
| Seller | :8022 | ✅ |
| Bitrix | :8023 | ✅ |
| Expert | :8024 | ✅ |

### RAG-пайплайн

```
Mac (PDF) → PyMuPDF/Tesseract → Чанки → JSON
                                        │
                                        ▼
                              VPS POST /v1/ingest
                                        │
                                        ▼
                              MiniLM embeddings (384-dim)
                                        │
                                        ▼
                              Qdrant similarity search + reranker
                                        │
                                        ▼
                              Yandex GPT → ответ
```

### Книги по птицеводству

**На VPS (kb_poultry):**
- Ross 308 — 54 чанка ✅
- Ещё 11 книг восстановлено ✅
- 6 книг в процессе восстановления (rate limiting)

**На Mac (исходники):**
- `/Users/igorvasin/Documents/Литература-по-птицеводству` — PDF оригиналы
- Скрипт: `/tmp/kb-prep` или `process_book.py`

### Инструменты для Mac CLI

```bash
# Установка (один раз)
brew install tesseract tesseract-lang poppler
pip3 install pymupdf requests

# Команды
kb-prep pdf ~/Documents/Литература-по-птицеводству/ross308.pdf
kb-prep send output/ross308.pdf.json
kb-prep search "цена бройлеров"
```

### Следующие шаги

| # | Задача | Приоритет | Статус |
|---|--------|-----------|--------|
| 1 | Дособрать 6 книг (rate limit) | Высокий | ✅ НЕ БЫЛО НУЖНО — все 16 книг загружены 2026-09-22 |
| 2 | Обработать PDF из `~/Documents/Литература-по-птицеводству` на Mac | Высокий | ✅ Сделано (kb-prep) |
| 3 | Подключить tg_bot.py к Expert профиль | Средний | — |
| 4 | Перевести все книги на MiniLM embeddings | Средний | ✅ Сделано 02:30 (v2.0) |
| 5 | Добавить reranker (cross-encoder) | Низкий | ✅ Сделано 03:30 (v3.0, bge-reranker-base 256/10) |
| 6 | Освободить диск Mac (был 100% полон) и диск VPS (99%) | Средний | — |

### Команды для входа

```bash
# SSH
ssh root@217.149.23.113

# Проверка
curl -s http://localhost:8080/health
curl -s http://vezemcip.ru/api/health

# Логи
tail -f /opt/levitan/projects/ai-eggs/logs/server_seller.log
tail -f /opt/levitan/projects/ai-eggs/logs/server_expert.log

# Перезапуск
systemctl restart angelochka-seller angelochka-bitrix angelochka-expert
cd /srv/knowledge-platform && docker-compose restart qdrant
```

### Переменные окружения

```
YANDEX_API_KEY=[REDACTED — see .env, rotate advised]
YANDEX_FOLDER_ID=b1gaikufqg8b6i83he8n
QDRANT_API_KEY=sk-antigravity-qdrant-2026
KB_VPS_URL=http://217.149.23.113:8080/v1
```
