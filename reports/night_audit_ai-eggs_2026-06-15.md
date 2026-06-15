# 🌙 Ночной аудит кода — 2026-06-15

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:04  
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
ai-eggs/agent/angelochka_core.py:104:89: E501 Line too long (113 > 88)
ai-eggs/agent/angelochka_core.py:109:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:146:89: E501 Line too long (92 > 88)
ai-eggs/agent/angelochka_core.py:154:89: E501 Line too long (130 > 88)
ai-eggs/agent/angelochka_core.py:184:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:224:13: F841 Local variable `y` is assigned to but never used
ai-eggs/agent/angelochka_core.py:271:9: B007 Loop control variable `cat_key` not used within loop body
ai-eggs/agent/angelochka_core.py:350:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:360:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:374:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:420:89: E501 Line too long (90 > 88)
ai-eggs/agent/angelochka_core.py:485:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:497:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:498:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:515:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:516:89: E501 Line too long (89 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-15\')

**Критических ошибок ruff (E,F,S,B):** 1684

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 ai-eggs                                   |   2 +-
 angel-backend                             |   0
 checkpoints/chp_20260611_132924.md        |  37 ++++++
 checkpoints/chp_20260611_230005.md        |  66 ++++++++++
 chp.md                                    |  76 ++++++------
 chronicles/chronicle_2026-06-11.md        |  10 ++
 data/habr_intelligence_state.json         |   2 +-
 dreams/patterns.md                        | 195 ++++++++++++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-06-12.md | 166 +++++++++++++++++++++++++
 9 files changed, 515 insertions(+), 39 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

**Файл: angelochka_core.py:16**
- **Проблема:** Повторный импорт `import re as _re_core` вместе с `import re`  
- **Критичность:** 🟢 Минорно  
- **Исправление:** оставь `import re` один раз, удаляй `_re_core` и замени в паттерне `_re_core` → `re`

---

**Файл: angelochka_core.py:33**  
- **Проблема:** Отключённый модуль `RAG Lite` молча учитывается в логике, но не проверяется при использовании `search_knowledge(...)`  
- **Критичность:** 🔴 Критично — в случае `None` вызов `format_context_for_llm(None)` вызовет исключение `TypeError`  
- **Исправление:** везде, где вызываются `search_knowledge(..)` и `format_context_for_llm(...)` явно проверять `if search_knowledge is None: return ""`

---

**Файл: angelochka_core.py:80**  
- **Проблема:** Путь `roles_config.json` проверяется с `join()` и последующим `realpath`, но потом `with open(_roles_real)` используется без проверки `PermissionError`.  
- **Критичность:** 🔴 Критично — если файл существует, но недоступен в правах, потеряем трэйсбек и получим `ROLE_EMPLOYEE` без логов.  
- **Исправление:** унифицировать обработку `PermissionError` и `OSError` в один `except (FileNotFoundError, OSError) as _e:` и выводить их в `print`.

---

**Файл: angelochka_core.py:81-85**  
- **Проблема:** Проверка `not _roles_real.startswith(os.path.realpath(_agent_dir) + os.sep)` не учитывает, что `_agent_dir` без закрывающего слеша может быть префиксом для других директорий.  
- **Критичность:** 🟡 Важно — при неверном расположении конфига обход защиты возможен.  
- **Исправление:** использовать `os.path.commonpath` для корректного выявления родителя.

---

**Файл: tg_bot.py:78**  
- **Проблема:** У `aiogram` некорректный вызов сессии `bot = Bot(token=..., session=session)` должен быть раскрыт **до объявления `.get_me()` или `.start_polling()`, иначе** — вдынкт функция возвращает объект `Bot`, но потом в код не вызывается и он теряется.  
- **Критичность:** 🟡 Важно — потенциально возвращается объект как `bot`, но дальнейший код может упустить `Session` и вновь создавать `None`.  
- **Исправление:** сделать инициализацию `bot = Bot(TELEGRAM_TOKEN, session=_make_session())` непосредственно в `main()` или при выполнении `start_polling`.

---

**Файл: tg_bot.py:216** *(в обрезанном DIFF нет, но существует в комментах выше)*  
- **Проблема:** Распространяет добавление в `user_histories[user_id].append({'content': message.text})` без сохранения лимита.  
- **Критичность:** 🟡 Важно — истории могут раздуться до сотен МБ и вызвать OOM.  
- **Исправление:** добавлять только последние N сообщений (например, 20) через `deque(maxlen=20)`.

---

**Файл: bitrix_intelligence.py:53**  
- **Проблема:** `bx_post`, `bx_get_all` не имеют ретраев на сбои B24 (рефлектирует DevOps PM2 перезапуски).  
- **Критичность:** 🟡 Важно — один `requests.post` без единой попытки повтора под расстоянии 2 час.  
- **Исправление:** встроить retry ліьера (`from tenacity import retry, stop_after_attempt`) на `bx_post`.

---

**Файл: bitrix_intelligence.py:60,78**  
- **Проблема:** Нет проверки на HTTP-502/504 после `resp.json()`; при ошибке возвращается [] вместо RuntimeException/raise.  
- **Критичность:** 🔴 Критично — битый JSON или 502 может пропустить B24 ошибку и сохранить вложения.  
- **Исправление:** сделать `resp.raise_for_status()` и логировать `resp.status_code !=200`.

---

**Файл: bitrix_intelligence.py:37** *(ENV)*  
- **Проблема:** `BITRIX_URL = os.getenv(...)` не проверяет что строка непустая. При пустом значении начнётся конкат `//rest/1/…` потенциально ломает урлы или проглатывает credentials на другой домен.  
- **Критичность:** 🔴 Критично — пустой Webhook приведёт к `requests.post('///task.item ..')` и может решать запросы на localhost или fail, но не виден.  
- **Исправление:** добавить `assert BITRIX_URL, "PRODUCTION_BITRIX_WEBHOOK_URL missing in .env"` и проверку начала с https://.

---

**Файл: bitrix_intelligence.py:97**  
- **Проблема:** Нет проверки, что `items` не массив (случаи, когда API вернёт JSON со скрытым `{"error": "NO ACCESS"}`) → тогда `items=dict`, `.extend(items)` свалится в `TypeError`.  
- **Критичность:** 🔴 Критично — не хэндлишь пол Курсор без `list()`.  
- **Исправление:** if not isinstance(items, list): log_error … continue.

---

Подытоживая, код **не** чист, прыгают несколько потенциально критических мест.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-15 |
| ⏰ Время | 02:00:04 → 02:01:02 |
| 📁 Python файлов | 200 |
| 📝 Изменено за день | 9 |
| ⚡ ruff ошибок (E,F,S,B) | 1684 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 5 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 1 |

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
