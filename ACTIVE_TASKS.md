# Текущие задачи (обновлено 26.05.2026)

> **Архив завершённых/протухших задач:** `_archive/tasks/`

---

## 🔴 P0 — Сегодня

### 1. 📞 CSV-загрузка в TG → автодозвон Mango → отчёт в TG
- [ ] **Telegram handler**: команда `/call_csv` или приём CSV-файла с телефонами
- [ ] **Конвейер**: CSV → `mango_autocall.py` → обзвон → результаты
- [ ] **Отчёт**: результат обзвона в TG (кто подтвердил/отказал/не дозвонились)
- [ ] **Исходники**: `tg_bot.py` (новый handler) + `mango_autocall.py` (уже есть)

### 2. 🔧 Баги ночного аудита (26.05) — из `reports/night_audit_ai-eggs_2026-05-26.md`
- [ ] **`angelochka_core.py:78`** — `_CREATOR_TG_ID` без `.strip()` → 🔴 сброс прав владельца
- [ ] **`angelochka_core.py:72-86`** — `_has_phone_in_history` не видит телефон-контакт
- [ ] **`tg_bot.py:72`** — orphaned lock при SIGKILL → бот не стартует
- [ ] **`bitrix_scanner.py:519`** — `CLOSED_STAGES` не frozenset → race condition
- [ ] **`bitrix_intelligence.py:46`** — синхронный `requests` в асинхронном коде

---

## 🟡 P2 — Средний приоритет

### 3. Контент-машина
- [ ] Яндекс.Дзен: статьи готовы, нужна публикация
- [ ] VK Канал А («ВезёмЦыплят»): группа не создана
- [ ] ОК: автопостинг готов, не запилен

---

## 🟢 P3 — По требованию (GEO/контент)

> Задачи не срочные. Выполнять после деплоя или по запросу.

### 4. GEO-видимость ai-bureau.pro
- [ ] Опубликовать 2 кейса на **VC.ru** с триплетами «AI Bureau → делает → AI-агентов»
- [ ] Добавить **Schema.org** (Organization + FAQPage) на ai-bureau.pro
- [ ] Добавить **FAQ-блоки** на страницы услуг
- [ ] Задеплоить **llms.txt** → `https://ai-bureau.pro/llms.txt` (файл создан в `public/`)

### 5. GEO-видимость vezemcip.ru
- [ ] Создать **llms.txt** в `vezemcip.ru/public/`
- [ ] Добавить **Schema.org** (LocalBusiness + Product) на vezemcip.ru
- [ ] FAQ-блоки: цены, породы, доставка
- [ ] Зарегистрировать в Яндекс Бизнес + 2GIS (карточки = вес в AI-выдаче)

### 6. GEO-монитор (инструмент готов)
- [ ] `python3 tools/geo_monitor.py --site vezemcip --dry-run` — первый замер VezemCip
- [ ] При запуске нового сайта → добавить в `SITES_CONFIG` в `tools/geo_monitor.py`
  - Шаблон: `name, domain, brand_patterns, queries (10-25 шт.)`
- [ ] **Правило Артемия**: каждый новый сайт → регистрация в GEO-мониторе ОБЯЗАТЕЛЬНА

---

## 🏗️ Архитектура автоматизации

### VPS (72.56.38.19) — 24/7
| Время MSK | Скрипт | Описание |
|-----------|--------|----------|
| */15 мин | watchdog_cron.sh | Мониторинг PM2 |
| 00:30 | call_learner.py | Обучение из звонков |
| 02:05 | night_audit_vps.sh | Код-аудит + Gemini ревью |
| 20:10 | daily_report.py | Ежедневный отчёт |
| 20:12 | call_quality_report.py | Отчёт по звонкам |

### Mac (launchd)
| Время | Скрипт | Описание |
|-------|--------|----------|
| 02:00 | night_audit.sh | Код-аудит (локальный) |
| 07:00 | morning_dream.sh | Анализ паттернов |
| 23:00 | finish_day_cron.sh | Бэкап + чистка + TG |
