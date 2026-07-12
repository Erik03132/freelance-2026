# GeekNeural — Token Dedup Engine

Сервис сокращает расход токенов до **92%** за счёт дедупликации контекста: если
в одной сессии один и тот же файл/кусок текста запрашивается несколько раз,
он передаётся модели **один раз** — без повторного чтения и «пустой» работы.

> «Не баг, а фича.» — GeekNeural

## Как устроено

- один и тот же файл не дублируется при повторных обращениях (content-addressed cache по sha256);
- поддержка популярных ИИ: ChatGPT, Claude, Gemini (через браузерное расширение / MCP);
- различает, где можно урезать расход, а где это нежелательно (volatile-файлы, мелкие файлы);
- интеграции на **четырёх уровнях**;
- **никакой телеметрии** — всё локально (sqlite в `~/.geekneural/`).

## Уровни интеграции

| # | Уровень | Что | Где |
|---|---------|-----|-----|
| 1 | shell-hook | `gn read` / `gn cat` / `gn stats` | `shell/hook.sh` |
| 2 | MCP-сервер | инструменты `cached_read`, `session_stats`, … | `mcp_server/server.py` |
| 3 | браузерное расширение | дедуп вставок в композер чата | `browser/extension/` |
| 4 | IDE-плагин | команда VS Code «копировать файл (дедуп)» | `ide/vscode/` |

Все уровни используют **одно ядро** `core/dedup.py` (чистый stdlib, без зависимостей).

## Быстрый старт

```bash
# слой 1 — shell
source tools/geekneural/shell/hook.sh
gn read path/to/big_file.py      # 1-й раз: полное содержимое
gn read path/to/big_file.py      # 2-й раз: ↺ ссылка, токены сэкономлены
gn stats                          # экономия по сессии

# слой 2 — MCP (регистрируется в opencode.jsonc / claude_desktop_config)
python3 tools/geekneural/mcp_server/server.py

# тесты
PYTHONPATH=. python3 tests/test_dedup.py
PYTHONPATH=. python3 tests/test_mcp.py
```

## Логика «где резать, где нет»

Не дедуплицируются (`core/dedup.py::VOLATILE_GLOBS`):
- `*.log`, `*.lock`, `/tmp/`, `*.pid`, `*.db`, `*.sqlite`
- рантайм-данные: `traces.json`, `smart_faq_counter.json`, `run.log`, `voice_cached_responses.json`
- файлы меньше `MIN_DEDUP_BYTES` (256 байт) — накладные > выгода

Это защищает от «урезания» живых/изменяющихся данных, где дедуп был бы ошибкой.

## Оценка экономии

`bytes_saved = bytes_raw − bytes_sent`, `pct = bytes_saved / bytes_raw`.
При N повторных чтений файла размером B в сессии: `pct ≈ (N−1)/N · 100%`.
Для типичной сессии агента (многократное перечитывание одних и тех же модулей)
экономия выходит в десятки процентов; в пределе — до ~92% на стабильном контексте.
