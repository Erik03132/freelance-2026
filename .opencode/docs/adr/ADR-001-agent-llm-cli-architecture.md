# ADR-001: Модульная LLM-CLI архитектура автономных агентов

**Дата:** 2026-07-09
**Статус:** Accepted
**Контекст:** Прокачка агентов Артемий, Кулибин, Шерлок до уровня Рембрандта (Universal Designer Agent).

## Решение

Каждый агент реализуется как self-contained пакет в `freelance-agent/.agent/agents/<name>/`:

```
<name>/
├── __init__.py            # Python API (re-export публичных функций)
├── <name>.py              # CLI (argparse), точка входа
├── llm_client.py          # OpenRouter key loader + call_llm()
├── <domain>_config.py     # дефолтные настройки домена
├── <module1>.py           # генератор/анализатор (вызывает LLM)
└── <module2>.py
```

**Контракты (совместимо с Рембрандтом):**
- LLM через `https://openrouter.ai/api/v1/chat/completions`, модель `deepseek/deepseek-chat-v3-0324`, timeout 60s.
- Ключ: `OPENROUTER_API_KEY` из `.env` (parent dir) или env.
- Graceful fallback при отсутствии ключа (минимальный working output).
- CLI: `--help`, `--list-*` для перечисления возможностей, subcommand-style флаги.
- Python API: `from <name> import <func>` для вызова из других агентов.
- Вывод пишется в `<name>/output/`.

**Домены:**
- Артемий (`artemiy`): генерация фронтенда. `--framework astro|react|vanilla` (default astro). Модули: component_gen, page_gen, audit.
- Кулибин (`kulibin`): инженерный аудит. Языки: Python + JS/TS. Модули: code_analyzer, lib_scout, proto.
- Шерлок (`sherl`): разведка. Реальный поиск через Serper/Perplexity API (fallback OpenRouter). Модули: searcher, geo_scan, competitor, report.

## Альтернативы
- Единый shared-модуль `llm_client` — отвергнут: нарушает self-contained автономность каждого агента.
- Только профили без кода — отвергнут: пользователь выбрал LLM-CLI уровень.

## Последствия
- 3 новых пакета (~18 файлов) в `freelance-agent/.agent/agents/`.
- Профили агентов обновляются: +tools/skills, секция Python API, CLI usage.

## Дополнение (2026-07-09): перенос Рембрандта
Рембрандт перенесён из `projects/ai-eggs/agent/` в `freelance-agent/.agent/agents/rembrandt/`
по тому же паттерну (self-contained пакет + `python3 -m rembrandt`).
- Адаптированы пути поиска `.env` (восходящий поиск вместо `../.env`).
- Добавлен класс `RembrandtDesigner` (facade) — его ожидали legacy-модули ai-eggs.
- В `ai-eggs/agent/rembrandt.py` оставлен совместимый shim (importlib-загрузка глобального пакета).
- Тесты перенесены в `rembrandt/tests/` с поправкой импортов на `from rembrandt import ...`.
- Legacy-вызовы (`content_machine_orchestrator`, `sandbox_pipeline`, `sandbox_live_feed_demo`) работают через shim.
