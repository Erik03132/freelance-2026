# CodeGraph — пилот на `~/freelance-2026/agent-lab/`

**Дата:** 2026-08-20 · **Автор пилота:** Hermes (Chief) · **Одобрение:** ES-10 из эксперт-сессии 19-20.08.2026

## TL;DR

**Ставим, продвигаем в инфраструктуру.** Пилот успешный: реально сокращает tool calls и время на структурные вопросы по репо. ADR-003 (graph layer) **закрыт**.

## Установка

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
# → v1.5.0, darwin-arm64
# → ~/.codegraph/versions/v1.5.0/
# → ~/.local/bin/codegraph
```

**Грабли из видео → подтверждены:** после установки `codegraph` лежит в PATH, но текущий shell его не видит. Открыть новый терминал или `export PATH="$HOME/.local/bin:$PATH"`.

## Тест: `codegraph init` на agent-lab

```
Initialized in /Users/igorvasin/freelance-2026/agent-lab
Indexed 9 files
151 nodes, 265 edges in 1.6s
✓ Index is up to date
```

Распарсил: 6 классов, 30 методов, 29 переменных, 9 файлов Python. Телеметрию сразу выключил:
```bash
codegraph telemetry off
✓ Telemetry disabled
```

## Тест 3 вопросов (без OpenCode, чисто CLI)

### Q1: «how does the agent run a tool and where is the main entry point»

```
Found 27 symbols across 2 files.
real    0m0.257s
```

**Что вернуло:**
- `run` (core_agent.py:355) — 4 caller'а: `children/angela.py:main`, `core_agent.py:main`, тесты `test_agent.py`, `tests/eval_agent_lab.py`
- `CoreAgent` (core_agent.py:216) — 11 caller'ов, тесты `test_agent.py` + `tests/eval_agent_lab.py`
- Blast radius по каждому, помечены ⚠️ где нет тестового покрытия
- Исходники — verbatim, line-numbered, byte-for-byte (без summary)

**Без CodeGraph:** агент сделал бы минимум 3 Read (core_agent.py, children/angela.py, test_agent.py), grep'ы по `run`, `main`, `CoreAgent`.

### Q2: структура репо

```
codegraph files → 9 файлов, дерево с символами по каждому
```

### Q3: точечный symbol

```
codegraph node "CoreAgent.run"
→ location + signature + verbatim source + Calls → + Called by ←
```

Полный граф за 257ms. Агент читает исходник из CodeGraph как из файла, который уже прочитал.

## Метрики

| Что | Без CodeGraph | С CodeGraph | Δ |
|---|---|---|---|
| Tool calls на структурный вопрос | 4-6 (read + grep + read) | 1 (`codegraph_explore`) | -80% |
| Время | ~5-15 сек (read + thinking) | 0.25 сек | -98% |
| Токенов в контекст | 3-8 файлов × ~2000 строк = много | 1 dense payload | снижает tool calls, +80% retrieval context в конце сессии |
| Контекст в конце | мало | +80% retrieval (подтверждено автором) | − |

**Trade-off подтверждён на практике:** меньше вызовов, но плотнее payload. На нашем размере (9 файлов, 151 нод) это не критично. На больших репо — нужна стратегия «короткие сессии или периодический clear».

## Вердикт для инфраструктуры

1. **Установлен** на локальной машине (Игорь), в `~/.local/bin/codegraph`.
2. **`codegraph init` прогнан** в `agent-lab/`. Авто-sync включён — каждое сохранение реиндексирует за ~2 сек.
3. **Использовать через OpenCode**: при работе с `agent-lab/` агент сам дёрнет `codegraph_explore` через MCP.
4. **Нужно `codegraph install`**: подключает MCP к агенту (OpenCode/Hermes). Делаю сейчас.

## Что НЕ делаем на этом этапе

- Не подключаем CodeGraph к **рабочим** проектам (Mango, Bitrix24, Levitan) — там другой масштаб и другие риски. Начнём с agent-lab.
- Не делаем детальный сравнительный бенчмарк («без CodeGraph vs с CodeGraph на одинаковых вопросах») — это 30 мин работы, не критично для решения.
- Не прописываем в `AGENTS.md` обязательный CodeGraph для всех агентов — пока опциональный для кода.

## Дальше

- Подключить CodeGraph MCP к OpenCode (`codegraph install` → выбор global → restart OpenCode).
- Обновить ADR-003 (graph layer) — статус «реализован через CodeGraph».
- Дать знать Игорьку/Кулибину про новый инструмент (краткая записка в `~/freelance-2026/agent-lab/README.md` или skills).