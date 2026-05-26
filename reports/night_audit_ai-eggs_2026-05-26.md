# 🌙 Ночной аудит кода — 2026-05-26

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:02  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 192 (проверяем: 5)  
> **Источник:** ТОП-5 критических файлов (нет git diff)

---

## ⚡ Фаза 1: Машинный анализ

### 🔍 ruff — lint
```
ai-eggs/agent/_archived/send_infra_report.py:17:89: E501 Line too long (90 > 88)
ai-eggs/agent/_archived/send_project_report.py:16:89: E501 Line too long (110 > 88)
ai-eggs/agent/_archived/send_project_report.py:19:89: E501 Line too long (188 > 88)
ai-eggs/agent/_archived/send_project_report.py:24:89: E501 Line too long (99 > 88)
ai-eggs/agent/_archived/send_project_report.py:29:89: E501 Line too long (143 > 88)
ai-eggs/agent/_archived/send_project_report.py:32:89: E501 Line too long (182 > 88)
ai-eggs/agent/_archived/send_project_report.py:35:89: E501 Line too long (143 > 88)
ai-eggs/agent/_archived/send_project_report.py:38:89: E501 Line too long (193 > 88)
ai-eggs/agent/_archived/send_project_report.py:41:89: E501 Line too long (299 > 88)
ai-eggs/agent/_archived/send_project_report.py:55:89: E501 Line too long (132 > 88)
ai-eggs/agent/a2a_protocol.py:166:9: S110 `try`-`except`-`pass` detected, consider logging the exception
ai-eggs/agent/a2a_protocol.py:176:89: E501 Line too long (91 > 88)
ai-eggs/agent/agg_temp.py:8:89: E501 Line too long (113 > 88)
ai-eggs/agent/agg_temp.py:25:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:25:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/agg_temp.py:47:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:47:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/analyze_scan.py:40:89: E501 Line too long (95 > 88)
ai-eggs/agent/analyze_scan.py:81:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:94:89: E501 Line too long (90 > 88)
ai-eggs/agent/analyze_scan.py:95:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:107:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:114:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:122:89: E501 Line too long (94 > 88)
ai-eggs/agent/analyze_scan.py:125:89: E501 Line too long (130 > 88)
ai-eggs/agent/analyze_scan.py:130:89: E501 Line too long (98 > 88)
ai-eggs/agent/analyze_scan.py:132:89: E501 Line too long (132 > 88)
ai-eggs/agent/angelochka_core.py:97:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:134:89: E501 Line too long (92 > 88)
ai-eggs/agent/angelochka_core.py:142:89: E501 Line too long (130 > 88)
ai-eggs/agent/angelochka_core.py:172:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:212:13: F841 Local variable `y` is assigned to but never used
ai-eggs/agent/angelochka_core.py:233:18: F821 Undefined name `re`
ai-eggs/agent/angelochka_core.py:233:62: F821 Undefined name `re`
ai-eggs/agent/angelochka_core.py:259:9: B007 Loop control variable `cat_key` not used within loop body
ai-eggs/agent/angelochka_core.py:338:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:348:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:362:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:473:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:485:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:486:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:503:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:504:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:517:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:533:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:534:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:576:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:594:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:603:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:618:1: E402 Module level import not at top of file
```

🔧 **ruff --fix:** 1 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-26\')

**Критических ошибок ruff (E,F,S,B):** 1595

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 ai-eggs                                   |  0
 angel-backend                             |  0
 reports/night_audit_ai-eggs_2026-05-26.md | 76 +++++++++++++++++++++++++++++++
 3 files changed, 76 insertions(+)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

🔍 **Анализ diff** (показаны только изменённые/добавленные фрагменты).  
Найденные ошибки и потенциальные провалы:

---

### angelochka_core.py
1. **angelochka_core.py:36–54**  
   **Проблема**: при сбое чтения или парсинга `roles_config.json` утечка начальных пробелов во-первых допускает, что в `_cfg` может быть `None`, а затем по-умолчанию выдаёт `"manager"`, а дальше маппится в `ROLE_EMPLOYEE`.  
   **Критичность:** 🟡 Важно  
   **Исправление**: явно задать `_cfg={}` после `json.JSONDecodeError`, а также после `FileNotFoundError` добавить `continue` или ретёрн по умолчанию, чтобы не пытаться вызвать `.get()` на `None`.

2. **angelochka_core.py:78**  
   **Проблема**: константа `_CREATOR_TG_ID` кастуется из **env** как `str` (`"176203333"`) без явной нормализации. Если в `.env` окажется пробел или `\r` из Windows-файла, сравнение `sid == _CREATOR_TG_ID` никогда не сработает.  
   **Критичность:** 🔴 Критично (скрытый полноценный сброс прав)  
   **Исправление**:  
   ```python
   _CREATOR_TG_ID = str(os.getenv("ADMIN_TELEGRAM_ID", "176203333")).strip()
   ```

3. **angelochka_core.py: поле `USER_ID` в messages**  
   **Проблема** в `_has_phone_in_history` (стр. 72–86). История может получиться из Telegram-объектов (`dict` с ключами `from`, `date`, `text` и т.д.), но код читает то `parts[0]`, то `content`, игнорируя структуру `message.entities`. Если объект сообщения имеет телефон как `contact`-entity, бот НЕ обнаружит номер текстом.  
   **Критичность:** 🟡 Важно (Phone-First Protocol не соблюдается)  
   **Исправление**: кроме регулярки сканировать `message.contact` если он есть.

---

### tg_bot.py
4. **tg_bot.py:83–86**  
   **Проблема**: прежде чем применять `int(_admin_id_raw)` нет проверки на числовой формат и другие символы. Можно крэшнуться `ValueError`.  
   **Критичность:** 🟡 Важно  
   **Исправление**:  
   ```python
   try:
       ADMIN_ID = int(_admin_id_raw)
   except ValueError:
       raise ValueError("ADMIN_TELEGRAM_ID пустой или не является integer!")
   ```

5. **tg_bot.py: `_make_session` всегда ждёт `proxy_url`, но вызывается с `""`**  
   **Проблема**: поле `params` внутри `AiohttpSession().__init__` передано как строка `proxy_url` — ожидается `str | None`, но не лишнее имя аргумента.  
   **Критичность:** 🟢 Минорно (работает, но выглядит странно)  
   **Исправление**: убрать аргумент `proxy_url` из `_make_session`, использовать просто `timeout` или `proxy=proxy_url or None` при вызове.

---

### bitrix_intelligence.py
6. **bitrix_intelligence.py:46**  
   **Проблема**: метод `bx_post` делает **синхронный** блочный HTTP-запрос (`requests.post`) внутри PM2-скрипта, который теоретически может запускаться из `asyncio`\-цикла (через `chat_listener`). Это блокирующий вызов в потоке, где обработка должна быть non-blocking.  
   **Критичность:** 🟡 Важно (CPU/IO блок)  
   **Исправление**: переписать на `aiohttp.ClientSession` с `asyncio.run` отдельным демоном, или принудительно запускать в `ThreadPoolExecutor` через `asyncio.to_thread`.

7. **bitrix_intelligence.py:68**  
   **Проблема**: `max_iterations` жёстко 50. При большом флейме в CRM (`items` может быть пожиже бумерангом) есть вероятность словить бесконечный цикл, если Bitrix24 когда-то вернёт `next`=0 вместо `next=null`.  
   **Критичность:** 🟢 Минорно  
   **Исправление**: дополнительно проверить `next is not None`.

8. **bitrix_intelligence.py:44**  
   **Проблема**: используется голый `print()` для логов; при режиме `pm2 --no-daemonize` вывод станет перегружен, затерет места лога.  
   **Критичность:** 🟢 Минорно  
   **Исправление**: перейти на структурированный лог `logging`.

---

### Общие потенциальные краши

9. **Общее: merge всех файлов** — везде используется:  
   ```python
   BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   ```  
   **Проблема**: если кто-то запустит `.py` как `python path/to/angelochka_core.py`, `__file__` будет содержать относительный путь, и `dirname` даст неожиданный результат → `FileNotFoundError` при чтении `.env`.  
   **Критичность:** 🟢 Минорно  
   **Исправление**: везде оборачивать `__file__` в `pathlib.Path(__file__).resolve()`.

10. **tg_bot.py**  
   **Проблема**: переменная `bot` инициализируется глоабально как `None`, но позже создаётся в `main()`. Если ошибка поднялась до вызова `main()`, вызовы `bot = ...` в функциях останутся на `None`, попытаться `await bot.send_message()` -> `AttributeError`.  
   **Критичность:** 🟢 Минорно (всё в одном процессе, но тесты могут сломаться)  
   **Исправление**: создавать `bot` в `main()` и пробрасывать в `module`.

11. **tg_bot.py:NOOP import `os.environ`**  Необработанная проверка **anje** переменной окружения. Если `.env` потерян, бот заведётся в статусе LOG_ONLY и будет спокойно продолжать без VK_LOG_MODE, всё замолчит (без алерта).

---

### Мёртвый код
12. **angelochka_core.py:16–22**  
   **Проблема**: попытка импортировать `rag_lite`, но во всех местах, где используются `search_knowledge()`/`format_context_for_llm()`, проверяют `if search_knowledge is not None`, но в коде нет других использований — “импорт на всякий случай”.  
   **Критичность:** 🟢 Минорно  
   **Исправление**: удалить если не используется, или сделать `Optional` через `TYPE_CHECKING`.

---

✅ Код **вцелом чист**, но скрытые проблемы могут привести к:
- сбою разграничения прав доступа;
- пропуску телефона клиента;
- блокировке event-loop во время сканирования CRM/Bitrix24.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-26 |
| ⏰ Время | 02:00:02 → 02:01:09 |
| 📁 Python файлов | 192 |
| 📝 Изменено за день | 3 |
| ⚡ ruff ошибок (E,F,S,B) | 1595 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 1 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 6 |

### Метод аудита
```
Код писали: Gemini 2.5 Pro + Claude Opus (через Antigravity)
Проверяли:
  Фаза 1: ruff 0.15 (машина, 100% точность)
  Фаза 2: Gemini CLI 2.5 Pro (глубокий анализ, бесплатно)
  Фаза 3: moonshotai/kimi-k2 (cross-model review, OpenRouter)
  
Cross-Model Peer Review: два профессора из разных школ
проверяют код друг друга → максимум найденных багов
```

---

> 🤖 Сгенерировано: `tools/night_audit.sh v2` — Cross-Model Peer Review
