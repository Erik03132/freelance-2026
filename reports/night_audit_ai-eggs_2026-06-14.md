# 🌙 Ночной аудит кода — 2026-06-14

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:02  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 200 (проверяем: 5)  
> **Источник:** ТОП-5 критических файлов проекта ai-eggs (нет git diff)

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
ai-eggs/agent/_vk_auth.py:29:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:41:10: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_get_token.py:26:17: S105 Possible hardcoded password assigned to: "client_secret"
ai-eggs/agent/_vk_get_token.py:31:5: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_get_token.py:43:89: E501 Line too long (101 > 88)
ai-eggs/agent/_vk_photo_workaround.py:24:89: E501 Line too long (126 > 88)
ai-eggs/agent/_vk_photo_workaround.py:34:9: S603 `subprocess` call: check for execution of untrusted input
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
ai-eggs/agent/angelochka_core.py:98:89: E501 Line too long (113 > 88)
ai-eggs/agent/angelochka_core.py:103:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:140:89: E501 Line too long (92 > 88)
ai-eggs/agent/angelochka_core.py:148:89: E501 Line too long (130 > 88)
ai-eggs/agent/angelochka_core.py:178:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:218:13: F841 Local variable `y` is assigned to but never used
ai-eggs/agent/angelochka_core.py:265:9: B007 Loop control variable `cat_key` not used within loop body
ai-eggs/agent/angelochka_core.py:344:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:354:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:368:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:414:89: E501 Line too long (90 > 88)
ai-eggs/agent/angelochka_core.py:479:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:491:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:492:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:509:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:510:89: E501 Line too long (89 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-14\')

**Критических ошибок ruff (E,F,S,B):** 1683

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 ai-eggs                                   |   2 +-
 angel-backend                             |   0
 checkpoints/chp_20260611_132924.md        |  37 +++++++
 checkpoints/chp_20260611_230005.md        |  66 ++++++++++++
 chp.md                                    |  72 +++++++------
 chronicles/chronicle_2026-06-11.md        |  10 ++
 data/habr_intelligence_state.json         |   2 +-
 dreams/patterns.md                        | 110 ++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-06-12.md | 166 ++++++++++++++++++++++++++++++
 9 files changed, 426 insertions(+), 39 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Вот что я нашёл за 3-минутный аудит:

---

1. **ai-eggs/agent: telegram.collections.defauldict dict-эк».0-каналу][async-actor      3-й файлже `import re  # ... import re as _re_core` — дубликат импорта  
**ai-eggs/agent/angelochka_core.py:4-5**  
- **Критичность:** 🟢 Минорно  
- **Исправление:** оставьте только `import re`.

---

2. **Не защищён JSON-injection в `roles_config.json` при любой ошибке чтения приводит к пустому `_cfg = {}`, но код продолжает работать**  
**ai-eggs/agent/angelochka_core.py:65**  
- **Критичность:** 🔴 Критично  
- **Исправление:** Если конфиг обязателен — вызывать `sys.exit(1)` или хотя-бы возвращать `ROLE_EMPLOYEE`, а не `ROLE_CUSTOMER` по-умолчанию. Иначе любой сбой JSON даст максимальный доступ клиенту.

---

3. **Отсутствует проверка существования переменных окружения `ADMIN_TELEGRAM_ID`/`ANGELOCHKA_BOT_TOKEN`** в продакшен-части кода  
**ai-eggs/agent/tg_bot.py:34-37**  
- **Критичность:** 🔴 Критично  
- **Исправление:** добавить проверку `if not TELEGRAM_TOKEN: raise ValueError(...)` сразу после загрузки из `.env`.

---

4. **Потенциальный race-condition в `is_silent_mode()`** — одновременное чтение/запись файла-флага `LOG_ONLY` из разных процессов  
**tg_bot.py:75-78**  
- **Критичность:** 🔴 Критично  
- **Исправление:** воспользоваться атомарной файловой блокировкой (fcntl/portalocker) или in-memory переменной с перечитыванием при SIGHUP вместо чтения файла каждый раз.

---

5. **Захардкожен `ADMIN_TELEGRAM_ID` в тексте сообщений (`message.answer`)**  
**tg_bot.py: ≈50**  
- **Критичность:** 🟢 Минорно  
- **Исправление:** выводить ID из переменной окружения, а не строковый литерал `176203333`.

---

6. **Функция `_has_phone_in_history` может сломаться на `parts = msg.get("parts")` если `parts[0]` будет не строкой, а, например, `bytes()`**  
**angelochka_core.py:90-97**  
- **Критичность:** 🟡 Важно  
- **Исправление:** привести `parts[0]` к `str()` с обработкой `AttributeError`.

---

7. **Потенциальный path-traversal в `os.path.abspath(__file__)` при чтении `roles_config.json`, т.к. файл конфигурации лежит внутри каталога проекта**  
**angelochka_core.py:54-59**  
- **Критичность:** 🔴 Критично  
- **Исправление:** санитизировать/валидировать путь через `os.path.realpath` и контроль на выход за пределы проекта.

---

8. **В `bitrix_intelligence.py` отсутствует проверка SSL-сертификата при `requests.post`, что делает man-in-the-middle возможным**  
**bitrix_intelligence.py:bx_post()**  
- **Критичность:** 🔴 Критично  
- **Исправление:** передавать `verify=True` и настроить корневые сертификаты или использовать `REQUESTS_CA_BUNDLE`.

---

9. **Функция `bx_get_all` имеет ограничение `max_iterations = 50`, но при сбое API может вернуть лишь первую страницу без лога, что приведёт к недооценке `all_items[:limit]`**  
**bitrix_intelligence.py: bx_get_all**  
- **Критичность:** 🟡 Важно  
- **Исправление:** логировать, если достигли `max_iterations` без `next_page`, и выбрасывать Exception или установить специальный флаг «данные неполные».

---

10. **Dead-code: `import csv` и `import re` не используются в `tg_bot.py`**  
**tg_bot.py:2-4**  
- **Критичность:** 🟢 Минорно  
- **Исправление:** удалить лишние импорты.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-14 |
| ⏰ Время | 02:00:02 → 02:00:49 |
| 📁 Python файлов | 200 |
| 📝 Изменено за день | 9 |
| ⚡ ruff ошибок (E,F,S,B) | 1683 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 5 |
| 🟡 Важных (Claude) | 2 |
| 🟢 Минорных (Claude) | 3 |

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
