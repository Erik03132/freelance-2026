# 🌙 Ночной аудит кода — 2026-05-27

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:04  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 193 (проверяем: 5)  
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
ai-eggs/agent/angelochka_core.py:479:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:491:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:492:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:509:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:510:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:523:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:539:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:540:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:582:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:600:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:609:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:624:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:747:88: E501 Line too long (93 > 88)
```

🔧 **ruff --fix:** 7 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-27\')

**Критических ошибок ruff (E,F,S,B):** 1641

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 ai-eggs                                            |   0
 angel-backend                                      |   0
 checkpoints/chp_20260526_230430.md                 |  25 ++++
 checkpoints/chp_20260527_0050.md                   |  47 +++++++
 checkpoints/chp_20260527_010501.md                 |  47 +++++++
 chp.md                                             |  72 ++++++----
 chronicles/chronicle_2026-05-26.md                 |   9 ++
 reports/night_audit_ai-eggs_2026-05-26.md          | 154 +++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-27.md          |  76 ++++++++++
 14 files changed, 514 insertions(+), 125 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Ниже — единственные **реальные** баги/уязвимости, которые **можно увидеть в показанном диффе**.

---

**angelochka_core.py:9**  
🔵 `import re` дублируется; `import re as _re_core` не используется дальше в коде  
🟢 Минорно  
Исправление: оставить только `import re` и убрать `_re_core`, заменив `_re_core.compile` на `re.compile`.

---

**angelochka_core.py:70**  
Проверка `if os.path.exists(_roles_path):` → если файл есть, но **символических ссылок нет**, то при `PermissionError` у нас закрыт **весь** блок `except`. Это не баг, но **может скрыть чтение битого/фейкового файла** и привести к **path-traversal**, т.к. имя файла может быть подставлено извне.  
🟡 Важно  
Исправление: явно отрабатывать `abspath`, убедиться, что читается только внутри директории бота; добавить `os.path.realpath`.

---

**angelochka_core.py:86**  
Паттерн `_PHONE_PATTERN` не проверяет начало/конец строки — пройдёт `"abc89012345678xyz"`.  
🟡 Важно  
Исправление: добавить якоря: `r'(?<!\d)(?:\+7|...)(?!\d)'`.

---

**tg_bot.py:45-60**  
Файл `LOG_ONLY_FLAG = os.path.join(AGENT_DIR, "LOG_ONLY")` создаётся/удаляется командой `/silent | /voice`. Если кто-то внешний (или сам процесс) создаст симлинк на `/etc/passwd`, можно повесить бесконечный цикл при проверке `os.path.exists`.  
🔴 Критично (Path-traversal / race condition)  
Исправление: использовать `os.path.realpath` и убедиться, что файл лежит **только** внутри `AGENT_DIR`.

---

**tg_bot.py:58-59**  
Валидация `try: ADMIN_ID = int(_admin_id_raw)` — если env содержит `"176203abc"` → `ValueError` уже выброшен, но **при этом бот не запустится** (блокирующая ошибка).  
🟡 Важно  
Исправление: поймать `ValueError`, сделать fallback на warning и graceful shutdown, либо беречь `None`.

---

**bitrix_intelligence.py:49-68**  
`bx_get_all` может уйти в **бесконечный цикл**, если API всегда возвращает `next: 0` или `next: ""`.  
🟡 Важно  
Исправление: добавить счётчик *эмпирического* лимита (например `> 500` итераций → raise).

---

**bitrix_intelligence.py:38**  
Весь файл — **синхронные** `requests.post(...)` в продакшен-скрипте, который вызывается *каждые 2 часа*. Если в момент вызова CRM не доступна → 2-факторное ожидание по таймауту 2×20 секунд (deal + user) × 50 страниц = **33 мин блока процесса**!  
🟡 Важно  
Исплавление: перенести на async HTTP (`httpx` / `aiohttp`) или вынести в отдельный worker.

---

💡 Больше **реального кода** не показано, поэтому других подтверждённых багов в этом диффе **не обнаружено**.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-27 |
| ⏰ Время | 02:00:04 → 02:00:47 |
| 📁 Python файлов | 193 |
| 📝 Изменено за день | 14 |
| ⚡ ruff ошибок (E,F,S,B) | 1641 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 1 |
| 🟡 Важных (Claude) | 5 |
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
