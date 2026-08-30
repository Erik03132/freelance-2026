# Brief: прокачка системы агентов (новая сессия, 2026-08-20)

> Вводная для новой сессии Гермеса. Предыдущая сессия собрала «отдел вокруг
> Гермеса» (см. `handoff_hermes_agents_2026-08-20.md`). Здесь — что прокачивать
> дальше: оркестрация, роутинг, автономные пайплайны, память агентов.

## Что уже собрано (статус: рабочее)
«Отдел вокруг Гермеса» — связка агентов как скиллов:
```
Шерлок (поиск HH/Кворк, Firecrawl)
  → ЭКСПЕРТ (главный фильтр релевантности Игорю + советник по ЛЮБЫМ фичам)
  → [юр-риск] ФЕМИДА (legal review: РИД ст.1298/1373 ГК РФ, NDA, ПДн 152-ФЗ)
  → БАТРАК (аудит + отклик на вакансию/коворк)
  + МАРКЕТЕР (marketer-strategist, content-marketing, ponytail — упаковка)
```
- `skills.external_dirs` в `~/.hermes/profiles/personal/config.yaml` подтягивает
  скиллы из `~/.config/opencode/skills` + `~/.agents/skills` (проверено: видны).
- Скиллы: `sherlock-hh-kwork`, `batrak-agent`, `femida-agent`, `marketer-strategist`,
  `expert-source-review` + `expert-council` (4 роли: Expert/Skeptic/Analyst/Financier),
  `content-marketing`, `marketing-psychology`, `ponytail`.
- Smoke-тест пайплайна БЕЗ сети пройден: Шерлок отсёк 1C/PHP, Эксперт дал БРАТЬ.

## БЛОКЕР (не критично, но мешает реальному прогону)
- Managed Firecrawl НЕ активирован: `hermes portal info` → `Web tools: not configured`.
- Токен лежит в `~/.hermes/profiles/personal/.env` (TOOL_GATEWAY_USER_TOKEN, из буфера).
- Wrapper готов: `sherlock-hh-kwork/scripts/run_sherlock_curl.sh` (curl + SOCKS5-прокси,
  т.к. urllib его не понимает).
- Решение: включить Tool Gateway в Portal через БРАУЗЕР (мышкой) → `Web tools: via Nous Portal`.

## Что прокачивать в этой сессии (предложения)
1. **Оркестрация** — единая точка входа (callAgent) для всей связки, а не ручной запуск.
2. **Роутинг Эксперта** — когда он пропускает в Батрак, а когда в Фемиду/Маркетера.
3. **Автономные пайплайны** — cron: Шерлок (09:00 МСК) → Эксперт → сводка в Telegram.
4. **Память агентов** — claude-mem / vault, чтобы контекст не терялся между прогонами.
5. **Неблокирующие субагенты** — параллельный разбор (урок `03-Lessons/2026-08-08_nonblocking_subagents.md`).
6. **Identity-scoped агенты** — каждый со своим аудит-логом (задача BUZ-1 в ACTIVE_TASKS).

## Контекст пользователя (Игорь)
- РФ, Москва, 62 года. Комбинации клавиш НЕ работают (только мышь + набор).
- Ключи/секреты НЕ в чат — копирует мышкой в буфер, агент забирает через `pbpaste`.
- Мат свести к минимуму. Не гнать инструкции — автоматизировать.
- Стек: Python, FastAPI, LLM, RAG, AI agents, Telegram bots, Bitrix24, voice AI, OpenRouter.
- Цели: HH ≥120k₽/мес, Kwork ≥1500₽/ч. Красные флаги: 1C, Java, PHP, React Native.

## Где смотреть
- `~/freelance-2026/ACTIVE_TASKS.md` — активные задачи (HZ-8 подключение скиллов → done).
- `~/freelance-2026/freelance-agent/.agent/agents/` — описания агентов (soul-файлы).
- `~/freelance-2026/AGENT_EVOLUTION_ROADMAP.md` — архитектура (Этапы 0-2).
- `~/freelance-2026/vault/03-Lessons/` — уроки (в т.ч. nonblocking_subagents).
- Карта проектов claude-mem projectId: `freelance-agent`, `hh-ai-agent`, `ai-bureau` и др.
