# Текущий статус проекта (обновлено 11.05.2026)

---

## 🟢 Боевая система — ВСЁ РАБОТАЕТ

| Компонент | Статус | Uptime |
|-----------|--------|--------|
| angela-server | ✅ online | 2+ дня |
| angela-bot (TG) | ✅ online | 2+ дня |
| angela-vk-bot | ✅ online | 2+ дня |
| angela-listener | ✅ online | 2+ дня |
| angela-scheduler | ✅ online | 2+ дня |
| angela-autopilot | ✅ online | 2+ дня |
| ptenchikova-bot | ✅ online | 2+ дня |
| vezem-web (Astro) | ✅ online | 2+ дня |

---

## ✅ Завершено (09-11.05.2026)

### Инфраструктура
- [x] **Ночной аудит починен** — `night_audit.sh` + `night_audit_vps.sh`, chmod +x, grep/set-e фиксы
- [x] **finish_day автоматизирован** — `finish_day_cron.sh` (обёртка с lock, TG, логами)
- [x] **finish_day.sh стабилизирован** — `set +e` для фаз Git/NAS/внешний диск, pipefail фикс TTL-проверки
- [x] **Миграция cron → launchd на Mac** — 3 LaunchAgent plist (night_audit 02:00, morning_dream 07:00, finish_day 23:00)
- [x] **Удалены дубли из crontab** — только launchd для задач Mac
- [x] **VPS ночной аудит подтверждён** — работает обе ночи (10-11 мая)
- [x] **morning_dream.sh протестирован** — exit 0, анализирует хроники за 3 дня, выдаёт паттерны

### Инструменты
- [x] **curl.md установлен** — конвертация URL → Markdown (88% экономии токенов)
- [x] **url_to_markdown.py создан** — Python-обёртка с кэшем, CLI, fallback HTTP API
- [x] **Деплой url_to_markdown на VPS** — rsync + проверка npx

### Анализ
- [x] **Аудит requests.get** — 48 вхождений, 90%+ = API (JSON), url_to_markdown для будущих агентов
- [x] **Roadmap сводка** — `roadmap_status.md` артефакт с 14 этапами эволюции

---

## 📌 P1 — Ближайшие задачи

### 1. Habr Digest (запуск в продакшн)
- [ ] Добавить `habr_digest.py` в launchd/cron (ежедневно 09:00 MSK)
- [ ] Тест отправки в TG
- [ ] Добавить в VPS crontab как fallback

### 2. VK автопостинг (незавершён)
- [ ] Завершить `vk_autoposter.py` — автоматическая публикация по расписанию
- [ ] Интеграция с `angela-scheduler` на VPS

### 3. Контент ОК (Одноклассники)
- [ ] Адаптация ВК-постов для ОК
- [ ] Автопостинг в группу ОК

---

## 📌 P2 — Средний приоритет

### 4. Fine-tune Zabotkina
- [ ] Подготовить датасет из транскриптов звонков
- [ ] Запустить обучение на Colab + Unsloth
- [ ] Деплой модели на VPS (Ollama)

### 5. Обновить daily_report.py
- [x] Отчёты работают (fallback cron на VPS)
- [ ] Разделить на 2 сообщения: голые цифры (всегда) + AI-анализ (бонус)

### 6. NAS автобэкап
- [x] `sync_to_nas.sh` существует и работает вручную
- [ ] Автоматический запуск (зависит от доступности NAS)

---

## 🤖 Эволюция агентов (из AGENT_EVOLUTION_ROADMAP.md)

### ✅ Готово
- Ollama Zabotkina (v4_ru.pt)
- Транскрипция звонков (call_transcriber)
- Обучение из транскриптов (call_learner)
- Автоматизация рутины: cron→launchd, finish_day, night_audit, morning_dream
- url_to_markdown (экономия токенов)

### ⬜ Не начато (этапы 1, 3-6)
- Этап 1: agentClient.js, event_log.jsonl, message_schema
- Этап 3: CLI `agctl`
- Этап 4: Мониторинг (Prometheus, logAgent)
- Этап 5: skillLoader.js (модульные навыки)
- Этап 6: Внешние интеграции (Calendar, REST webhooks)

---

## 🏗️ Архитектура автоматизации (актуальная)

### VPS (72.56.38.19) — 24/7
| Время MSK | Скрипт | Описание |
|-----------|--------|----------|
| */15 мин | watchdog_cron.sh | Мониторинг PM2 |
| 00:30 | call_learner.py | Обучение из звонков |
| 02:05 | night_audit_vps.sh | Код-аудит + Gemini ревью |
| 20:10 | daily_report.py | Ежедневный отчёт |
| 20:12 | call_quality_report.py | Отчёт по звонкам |

### Mac (launchd) — при включении
| Время | Скрипт | Описание |
|-------|--------|----------|
| 02:00 | night_audit.sh | Код-аудит (локальный) |
| 07:00 | morning_dream.sh | Анализ паттернов |
| 23:00 | finish_day_cron.sh | Бэкап + чистка + TG |

---
## 🛠️ СОВЕРШЕНСТВОВАНИЕ СИСТЕМЫ (meta / ops)

### AI Engineering Coach — анализ сессий Antigravity
- **Цель:** понять паттерны ошибок агента (антипаттерны, token waste, session hygiene)
- **Что сделано:** написан адаптер `tools/antigravity_to_coach.py` (Antigravity JSONL → Claude формат)
  - 7 сессий / 104 запроса / 624 tool calls конвертированы → `~/.claude/projects/antigravity-freelance-2026/`
  - Расширение собрано: `/tmp/ai-coach/ai-engineer-coach-0.1.0.vsix`
- **Блокер:** Cursor 1.105.1 несовместим с расширением (требует VS Code ^1.118.0)
- **Варианты разблокировки:**
  1. Установить чистый VS Code (не Cursor) → установить .vsix
  2. Или: написать standalone Python-скрипт с теми же 45 правилами без VS Code
- **Ценность:** «5 мин строим — 555 мин исправляем» → найти системные причины
- **Приоритет:** LOW (не блокирует проект, делать когда будет время)
