# Freelance Agent — Active Tasks

Задачи и инициативы по улучшению агента. Обновляется по ходу сессий.

---

## [NEW] Мультимодальная память (full-text + vector + graph)

**Статус:** Идея (из статьи habr.com/1061372)
**Приоритет:** высокий
**Дата:** 2026-07-23

### Контекст
Сейчас память агентов использует только vector search (Jaccard similarity) в `memory/`.
Статья AI Free показала: комбинация full-text + keyword + vector + graph даёт качественный скачок recall.

### План
1. Добавить full-text индекс (SQLite FTS5) поверх существующих фактов в `signals.jsonl`
2. Построить граф связей: задача → файл → ошибка → исправление
3. Сделать unified recall, который собирает результаты из всех источников и ранжирует
4. Интегрировать в `enrich_context`

---

## [NEW] Браузерная автоматизация для Кворка

**Статус:** Идея
**Приоритет:** высокий
**Дата:** 2026-07-23

### Контекст
Сейчас отклик генерируется в консоли (текст). Нужно, чтобы агент сам:
- Открывал страницу заказа на Кворк
- Заполнял форму отклика
- Отправлял

### План
1. Добавить browser-service (Playwright) в экосистему агентов
2. Сценарий: логин → поиск задачи → генерация отклика → отправка
3. Использовать KWORK_SILENT_AUTO.md стратегию

---

## [NEW] Recovery по уровням

**Статус:** Идея (из статьи habr.com/1061372)
**Приоритет:** средний

Сейчас healing только на уровне промпта (retry с коррекцией). Внедрить структурированное восстановление:
- Уровень вызова: повтор с экспоненциальной задержкой
- Уровень модуля: пересоздание воркера/клиента
- Уровень авторизации: перелогин
- Уровень приложения: полный перезапуск

---

## [DONE] Kwork: Silent Automation Strategy

**Статус:** DONE
**Дата:** 2026-07-23

### Что сделано
- Создан `.agent/rules/KWORK_SILENT_AUTO.md` — правила отклика как оператор втихаря с автоматизацией
- Добавлена команда `kwork` в CLI: `python main.py kwork "текст задачи" --budget 50000`
- Добавлен `KWORK_PROMPT_TEMPLATE` в генератор — без намёка на автоматизацию, только уточняющие вопросы

### Проверено
- Тестовый запуск на задаче «Оператор сверки цен» — отклик собран корректно, вопросы по формату данных заданы

---

## [NEW] Lead Finder — поиск клиентов через Sherl

**Статус:** Идея (из github.com/Kappaemme-git/codex-first-customer-finder-skill)
**Приоритет:** средний
**Дата:** 2026-07-23

### Контекст
Codex-скилл (903★) находит первых клиентов по публичным сигналам: demand, pain, timing, switching.
Методология: ICP → public signals → evidence score → outreach opener.

### Что делаем
1. Добавить Sherl скилл `lead-finder` — поиск потенциальных клиентов через Perplexity/Google
2. Режимы: b2b (компании с бизнес-триггерами), quick (5 сильных кандидатов), community (публичные запросы)
3. Интеграция с freelancer-agent: Sherl находит → передаёт задачу → генератор делает отклик
4. Источники: Кворк, HH, LinkedIn, публичные обсуждения (Хабр, TG)

---

## [NEW] Рембрандт: Scroll-World landing pages

**Статус:** Идея (из github.com/oso95/scroll-world, 4.8k★)
**Приоритет:** высокий
**Дата:** 2026-07-23

### Контекст
Скилл генерирует scroll-driven «пролёт по 3D-миру» лендинг для любого бренда.
Ключевые компоненты: scrub-engine.js (vanilla JS), промпт-темплейты сцен, seamless connector между сценами, мобильная portrait-версия.

### План
1. Внедрить scrub-engine.js в `design_generator.py` — генерация scroll-анимаций для лендингов
2. Скопировать промпт-темплейты (diorama, dive-in, connector) — адаптировать под бренд-систему Рембрандта
3. Добавить генерацию: портфолио, кейсы (A2A-шина, Levitan), лендинги под ключ
4. Мобильная версия 9:16 — отдельный portrait-chain для телефонов
5. Рендер: CSS 3D transforms / Three.js (вместо Higgsfield) — для работы без прокси
6. Использовать Apple Design spring-физику + backdrop-filter + типографику (см. apple-design.md)

---

## [DONE] Рембрандт: Apple Design system

**Статус:** DONE
**Дата:** 2026-07-23

### Что сделано
- Создан `.agent/agents/rembrandt/apple-design.md` — distilled Apple Design rules (WWDC 2018-2026)
- `design_generator.py`: внедрён `APPLE_DESIGN_RULES` в промпт (springs, translucency, typography, accessibility, 8 principles)
- `component_generator.py`: добавлены Apple Design требования (backdrop-filter, prefers-reduced-motion, touch targets, spring defaults)
- Каждый сгенерированный компонент включает `@media (prefers-reduced-motion)`, `@media (prefers-reduced-transparency)`, `@media (prefers-contrast)`

---

## [NEW] Openship — self-hosted деплой для Кулибина

**Статус:** Идея (из github.com/oblien/openship, 7.2k★)
**Приоритет:** средний
**Дата:** 2026-07-23

### Контекст
Openship — open-source deployment platform с CI/CD, БД, SSL, CDN, почтой, бекапами. TypeScript/Bun. Имеет MCP-интерфейс для AI-агентов.

### Что даёт
1. **MCP-интеграция** — A2A-диспетчер управляет деплоем через Openship MCP
2. **Push-to-deploy** — вместо runbook + pm2 resurrect
3. **Встроенный SMTP** (DKIM/SPF/DMARC) — почта без Mailgun
4. **Backups** БД + volumes — централизованно
5. **Dashboard** — единое окно для всех сервисов

### План
1. Развернуть Openship на VPS (Timeweb) через CLI: `curl -fsSL https://get.openship.io | sh`
2. Подключить проекты (Levitan, ai-eggs, freelance-agent) через `openship init` + `openship deploy`
3. Настроить MCP-мост с A2A-шин
