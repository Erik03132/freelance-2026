# AGENTS.md — Контекст проекта AI Bureau

AI Bureau — агентство по разработке автономных ИИ-систем: кастомные AI-агенты, RAG, голосовой ИИ, AIO/GEO-оптимизация. Сайт на Vite + React + TypeScript, бот-лидогенератор (BureauBot) с Smart Fallback.

**Ключевые документы:** `WEBSITE_COPY.md`, `SMART_FALLBACK_STANDARD.md`, `MARKETING_ROADMAP.md`, `CHRONICLE.md`, `llms.txt`

**Главное правило:** Каждый день — хотя бы одно действие по продвижению. Системность бьёт гениальность.

## Session Workflow

### Старт сессии
1. Прочитай `chp.md` (корень монорепозитория) — глобальный чекпоинт
2. Прочитай `SESSION_LATEST.md` — последнее состояние проекта
3. Прочитай `CHRONICLE.md` — хроника проекта

### Завершение сессии
1. Если делал изменения — `git add . && git commit -m "..." `
2. Запусти: `bash tools/save_session_state.sh ai-bureau`
   - Обновит `SESSION_LATEST.md`
   - Допишет блок в `chp.md` в секцию `🟦 OpenCode Session`

> **Команды (для агента):** `start-day` → читай chp.md + SESSION_LATEST.md + CHRONICLE.md  
> `finish-day` → git commit + save_session_state.sh

> **Монорепозиторий:** `freelance-2026/AGENTS.md`
> **Каскадная система, глобальные скиллы, правила эскалации:** `~/.config/opencode/AGENTS.md`
