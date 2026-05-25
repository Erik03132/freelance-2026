# 🌙 Ночной аудит кода — 2026-05-25

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:02  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 191 (проверяем: 5)  
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

🔧 **ruff --fix:** 4 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-25\')

**Критических ошибок ruff (E,F,S,B):** 1591

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 ACTIVE_TASKS.md                           |  15 ++
 ai-eggs                                   |   0
 angel-backend                             |   0
 checkpoints/chp_20260524_230001.md        | 181 ++++++++++++++++++++
 chp.md                                    |   9 +
 reports/night_audit_ai-eggs_2026-05-24.md | 153 +++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-25.md |  76 +++++++++
 tools/antigravity_to_coach.py             | 273 ++++++++++++++++++++++++++++++
 8 files changed, 707 insertions(+)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Диагностика скрипта `tools/antigravity_to_coach.py`

1. antigravity_to_coach.py:273  
   **Критичность:** 🔴 Критично  
   **Описание:** При запуске скрипта с параметром `--id 12345` без `--dry-run` не проверяется, что после `--id` передан не-флаг, что приведёт к затираю выбранного ID появившимся флагом `--dry-run`.  
   **Исправление:**  
   ```
   if "--dry-run" in sys.argv[1:]:
       dry = True
   ```

2. antigravity_to_coach.py:145  
   **Критичность:** 🟡 Важно  
   **Описание:** `make_tool_use_block` принимает `args` в словаре `tc`, но `tc['args']` может быть `None`; `json.loads(None)` выбросит `TypeError`.  
   **Исправление:**  
   ```
   if isinstance(args, str) and args:
       try:
   ```

3. antigravity_to_coach.py:93–104  
   **Критичность:** 🟢 Минорно  
   **Описание:** При извлечении путей из аргументов значения не фильтруются от символов `"`, поэтому из строк типа `"../etc/passwd" "../../../../config"` может остаться спецификатор переменной `../etc/passwd`, приводяший к выходу за пределы проекта.  
   **Исправление:**  
   ```
   import pathlib
   f = pathlib.Path(args.get("TargetFile", "")).resolve()
   if not str(f).startswith(WORKSPACE_PATH):
       continue
   ```

4. antigravity_to_coach.py:152–157  
   **Критичность:** 🟡 Важно  
   **Описание:** Параметр `WORKSPACE_PATH` (151–152) захардкожен строкой `str(HOME / "freelance-2026")`, но в прод-окружении папка могла быть клонирована в другой каталог. Если в будущем сценарии требуется динамическое определение, код захочет обращаться к несуществующей директории.  
   **Исправление:** Передавать путь к workspace через переменную окружения `AG_WORKSPACE_DIR` с fallback-значением.

5. antigravity_to_coach.py:206  
   **Критичность:** 🟢 Минорно  
   **Описание:** Подсчёт токенов делением на 4 рискует недооценить цифровые строки и ASCII-буквы, что на длинных следствах может вызвать переполнение поля `out_tokens`, поскольку максимум не ограничен.  
   **Исправление:** Ограничить `out_tokens = max(1, min(10**6, len(all_text) // 4))`.

✅ Других критических или значимых проблем не обнаружено.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-25 |
| ⏰ Время | 02:00:02 → 02:00:33 |
| 📁 Python файлов | 191 |
| 📝 Изменено за день | 8 |
| ⚡ ruff ошибок (E,F,S,B) | 1591 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 1 |
| 🟡 Важных (Claude) | 2 |
| 🟢 Минорных (Claude) | 2 |

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
