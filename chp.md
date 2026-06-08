# 🏁 ЧЕКПОИНТ: 2026-06-08 11:27 MSK

## 🗓️ 07.06.2026 — Сессия: Прокачка экосистемы

### ✅ Сделано за предыдущую сессию

| Задача | Результат | Файл |
|--------|-----------|------|
| Neuform 71 DESIGN.md | Добавлены в Рембрандта — перед любым UI выбрать скилл | `skills/rembrandt-designer/SKILL.md` |
| FAL.AI статус | Обновлён: FAL работает ✅, Ideogram 4 = #1 приоритет | `skills/rembrandt-designer/SKILL.md` |
| MiniMax M1 (1M ctx) | TaskType.AGENT → minimax/minimax-m1, SWE-Bench 59% | `tools/model_router.py` |
| Perplexity Search as Code | TaskType.RESEARCH_DEEP → sonar-deep-research, DSQA 0.871 | `tools/model_router.py` |
| ParallelSearchEngine | Search as Code в llm_planner v2: 5 запросов параллельно | `agent-lab/llm_planner.py` |
| gemma4:12b | Скачана (7.4 GB) и прописана в habr + llm_engine | Ollama |

### 📊 Роутер задач (13 типов)
```
trivial/extract/translate/summarize/chat → FREE ($0)
code/reasoning                           → FREE (Kimi K2)
agent                                    → MID (MiniMax M1, $0.40/M)
research                                 → MID (sonar, $1/M)
research_deep (Search as Code)           → MID (sonar-deep-research, $2/M)
creative/long/vision                     → CHEAP ($0.10-0.15/M)
```

---

## 🗓️ 08.06.2026 — Сессия: Тест llm_planner Search as Code

### ✅ Сделано

| Задача | Результат | Файл |
|--------|-----------|------|
| Реализован `ParallelSearchEngine` | Класс был прерван рестартом — дописан полностью | `agent-lab/llm_planner.py` |
| Баг `search_stats` | Убрано обращение к несуществующему `PlanResult.search_stats` | `agent-lab/llm_planner.py` |
| `--demo-parallel` тест | ✅ ПРОЙДЕН: 5 запросов → 24.8s → синтез рынка AI-агентств | — |

### 📊 Результат Search as Code (рынок AI-агентств РФ 2026)
- **Игроки:** Сбер GigaChat Enterprise, Yandex B2B, MWS AI (МТС), FUTURE AI
- **Рынок:** ~30 млрд руб. к 2026 (MWS прогноз), 29% — AI-агенты
- **Боли:** интеграция с legacy-IT, качество данных, недоверие к автономности

### 🔧 Что проверить в следующей сессии
- [x] `python3 agent-lab/llm_planner.py --demo-parallel` — ✅ 24.8s, работает
- [x] Проверить синтаксис `llm_planner.py` (был прерван рестартом) — ✅ починен
- [ ] `python3 agent-lab/llm_planner.py --demo` — тест полного плана с параллельным поиском

---

## 📝 Git log (последние 10 коммитов)
```
742988fd fix: убрана жесткая привязка к ai-bureau — проект определяется из CWD
cca746d1 feat: start-day/finish-day скрипты для OpenCode сессий
3a7e7b90 fix: claude-mem failover — SESSION_LATEST.md + chp.md + launchd worker-daemon
2792e9b6 feat: habr_intelligence v2 — детектор фич + llms.txt ai-bureau
d14c33fc 🤖 night-audit: ruff --fix (1 исправлений)
ad4f967e 🤖 night-audit: ruff --fix (2 исправлений)
e1ed6b91 29.05: 7-шаговая воронка Анжелы + pipeline заказов + автодозвон
8baeed8e 🤖 night-audit: ruff --fix (8 исправлений)
c7205555 🤖 night-audit: ruff --fix (2 исправлений)
9190cae8 🤖 night-audit: ruff --fix (7 исправлений)
```

---

## 🟦 OpenCode Session: ai-bureau (2026-06-08 11:54)

Последний коммит: `5b029f90 chore: update ai-eggs submodule — content machine finalize`

### Что сделано
* **API-ключи:** Найдены свежие ключи в `ai-eggs/.env`. OpenRouter и Gemini ключи рабочие, проверены. Gemini геозаблокированы из РФ.
* **Индексация знаний:** 253 вектора из 22 файлов (бэклог, стратегия, проекты, скиллы). OpenRouter `text-embedding-3-small`.
* **Server.js:** Полностью переписан. `apiPost` через `https` модуль (вместо fetch). Гибридный поиск, retry 2x. Лид-воронка: stage-зависимые system prompt, `callLLM` с контекстом, сохранение в `leads.json`. Timeout 30s.
* **Визуал:** Радикальный редизайн — split-screen hero с нейро-графом (Canvas 2D, force-directed, mouse interaction, particles, 24 узла). Секции: 01 Компетенции (нумерованный список с `animation-timeline: view()`), 02 Суверенитет данных (governance-блок с радиальным градиентом), 03 Хаб экспертизы (горизонтальный scroll-snap). Прогресс-бар сверху.
* **Цветовая тема:** Светлая, нейтральная. Все хардкоды oklch заменены на CSS-переменные.
* **Чат (`<dialog>` + Popover API):** BureauBot в `<dialog>` с `showModal()`, backdrop blur, `@starting-style` entry/exit. Индикатор прогресса воронки.
* **index.html:** Починен (были битые теги).
* **useChat.ts:** Починен баг передачи leadData. Убран хардкод ответов.
* **Сборка:** `vite build` — без ошибок. CSS 12 KB / JS 158 KB.
* **Инфраструктура:** Backend (:3001) + Frontend (:3000) запущены. End-to-end тест пройден (все 4 стадии воронки + RAG-ответы).
* **InteractiveNeuralGraph:** Force-directed Canvas с 24 узлами, mouse repulsion, edge glow, particle flows, pulsing nodes.

### Следующие шаги
1. Найти рабочий US/SOCKS5-прокси для Gemini (если нужно будет использовать Gemini API).
2. Добавить View Transitions API для смены секций.
3. Добавить CSP-метатег (Content-Security-Policy).
4. Деплой на VPS/хостинг.
5. Отрефакторить сервер на Express/Fastify для production.

---

## 🗓️ 08.06.2026 — Сессия: Баги, дайджест, Ollama

### ✅ Сделано

| Задача | Результат | Файл |
|--------|-----------|------|
| `night_audit.sh` — 7 багов | `$AGENT_DIR`, CHANGED_PY, gemini флаги, sonnet модель, TG имя файла, SSH хардкод в .env | `tools/night_audit.sh` |
| `ask_deep()` в model_router | Фасад над ParallelSearchEngine — одна строка для параллельного поиска | `tools/model_router.py` |
| `gemma4:e2b` откат | 12b слишком тяжёлая (55 мин на 3 предл.), конфиги откачены на e2b | `llm_engine.py`, `habr_intelligence.py` |
| `habr_intelligence.py` — 4 бага | chatgpt хаб 404, Gemini NO_PROXY_SESSION, KeyError фича, задвоенный код | `tools/habr_intelligence.py` |
| launchd → новый скрипт | Старый `habr_digest.py` заменён на `habr_intelligence.py` | `LaunchAgents/com.antigravity.habrdigest.plist` |
| Telegram без прокси | SOCKS5 мёртв, Telegram работает напрямую | `tools/habr_intelligence.py` |
| Дайджест отправлен | 5 статей проанализировано через OpenRouter/DeepSeek | TG @Angella_bot |

### 📋 В план (не срочно)

| # | Задача | Проект | Источник |
|---|--------|--------|---------|
| 1 | **AI-квалификация лидов Bitrix24** — Pydantic `LeadQualification`, Redis debounce, промпт по шаблону. +35% квалифицированных лидов, ответ 30 сек вместо 2-3 часов | ai-eggs/Анжела | Habr 08.06.2026 |
| 2 | **GEO/AEO оптимизация** ai-bureau.pro перед деплоем | ai-bureau | Habr 08.06.2026 |
| 3 | **JSON-LD + Knowledge Graph** — видимость в ChatGPT/Perplexity | ai-bureau | Habr 08.06.2026 |
| 4 | **RAG latency оптимизация** — Chroma кеширование, мониторинг | ai-bureau | Habr 08.06.2026 |
| 5 | **gemma4:e2b** вернуть когда стабилизируется сеть Ollama | tools | — |

### 🔧 Технический долг
- SOCKS5-прокси мёртв — нужен новый для Gemini API (OpenRouter работает без прокси)
- Gemini-ключи дают 429/таймаут — каскад падает на OpenRouter (OK, но Gemini дешевле)

---
