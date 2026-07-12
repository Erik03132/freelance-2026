# GeekNeural — Token Dedup Engine

Движок дедупликации контекста для экономии токенов (до ~92%). Один и тот же
файл/текст в сессии передаётся модели один раз. 4 уровня: shell-hook, MCP,
браузер, IDE. Без телеметрии. См. `README.md` и `ADR-001-dedup-engine.md`.

## Команды
- `source shell/hook.sh` → `gn read <file>` / `gn stats`
- MCP: `python3 mcp_server/server.py` (регистрируется в opencode.jsonc)
- тесты: `PYTHONPATH=. python3 tests/test_dedup.py && PYTHONPATH=. python3 tests/test_mcp.py`
