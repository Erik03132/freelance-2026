# RW-1: Пилот repowise — ЧАСТИЧНО, блокер: облачная авторизация

> Дата: 06.08.2026 · Инструмент: repowise v0.1.99 (npm, AGPL)

## Что сделано
- Установлен глобально: `npm install -g repowise` → `/Users/igorvasin/.npm-global/bin/repowise`
- Команды изучены: `create` (контекст репо), `sync`, `query` (dependency graph:
  callers/references/deps/dead-symbols/impact/call-graph/graph), `config`, `mcp-serve`
- `repowise query dead-symbols` в open-code → ожидаемая ошибка «No graph found...
  Run repowise sync» (локальный граф генерируется через sync)

## Блокер (HT-3: имя отказа)
- `repowise create`/`sync`/`login` требуют **облачную OAuth-авторизацию через браузер**
  (repowise.ai), CLI ждёт токен в цикле → таймаут «Authentication timed out».
- Офлайн-режима нет: без логина не создаётся ни контекст, ни граф → пилот невозможен
  без участия пользователя (нужен браузерный логин или API-ключ).
- Дополнительно: `login --no-browser` завис без вывода (нет печати URL в этой версии).

## Вывод (частичный, по CLI-поверхности)
- Dependency-graph подсистема (query) — локальная и интересна (dead-symbols, impact —
  совпадает с идеей impact slice из ADR-003), но вход через облако.
- Сравнение с ADR-003: их скоринг/граф — облачный сервис, наш evidence-chain —
  локальный файловый. При платном/облачном характере repowise-графы остаются опцией,
  не заменой ADR-003.
- AGPL-решение: см. RW-4 (только внутренние репо).

## Статус
- ⚠️ ОТЛОЖЕНО до участия пользователя: выполнить `repowise login` (браузер),
  затем `repowise sync` + `query` на open-code и freelance-agent, замерить токены
  контекста vs ADR-003, закрыть gaps.
