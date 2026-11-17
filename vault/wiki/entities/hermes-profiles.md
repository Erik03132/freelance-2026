---
type: wiki
tags: [hermes, profiles, multi-agent, soul, delegate-task, skills]
status: done
updated: 2026-11-17
sources: [06-Library/es-n-multiagent-gateway/digest.md, 06-Library/skill-library-v2/digest.md]
---

# Hermes Profiles: агент = профиль + SOUL + кеш скиллов

Источники: `06-Library/es-n-multiagent-gateway/digest.md` (2026-08-23) и `06-Library/skill-library-v2/digest.md` (2026-08-23). Оба помечены проектом `freelance-2026` / Hermes Profiles.

## Что известно из библиотеки

- Каждый эксперт — отдельный профиль (`femida`, `defender`, `marketer`, `financier`, `sherlock`, `health`), у профиля свой SOUL.
- Вызов подагента: `delegate_task(tasks=[{"goal": ..., "context": SOUL_<РОЛЬ> + data, "role": "leaf"}, ...])`. Роль `leaf` — исполнитель без дальнейшей делегации.
- Кеш скиллов профиля лежит в `~/.hermes/profiles/personal/cache/skills/` (по схеме `skill-library-v2`).
- Скиллы подключаются по тегам: `#marketing`, `#research`, `#legal`, `#security`, `#finance`, `#health`.

## Что это даёт

Изоляция контекста: эксперт получает только свой SOUL и данные задачи, а не всю историю координатора. Это тот же принцип, что AP-1 (свежий контекст на единицу работы) и `role: leaf` в субагентах.

## Чего в библиотеке нет

Дайджест `es-n-multiagent-gateway` называется «Hermes Telegram Gateway & 6-Agent Expert Council», но тела про Telegram-гейтвей в нём нет: только совет, формат вердикта и ссылки на `04-Decisions/2026-08-23-es-n-telegram-gateway-council.md` и `03-Lessons/2026-08-23-es-n-multiagent-gateway-lessons.md`. Детали гейтвея (транспорт, маршрутизация сообщений, авторизация) в `06-Library` отсутствуют — не выдумывать.

## Отношение к текущему стеку

Схема описывает Hermes-стек (профили, `~/.hermes/`), а не OpenCode. Переносится принцип: отдельный SOUL/инструкция на роль + выдача только релевантных скиллов по тегу. Путь `~/.hermes/profiles/...` в нашей системе не используется — см. `skill-library-v2` о состоянии плана.
