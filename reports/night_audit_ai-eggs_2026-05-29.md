# 🌙 Ночной аудит кода — 2026-05-29

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:11:57  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 196 (проверяем: 5)  
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
ai-eggs/agent/_vk_auth.py:3:1: E401 [*] Multiple imports on one line
ai-eggs/agent/_vk_auth.py:25:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:37:10: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:48:11: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_auth.py:53:7: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_auth.py:54:7: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_auth.py:55:7: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_photo_workaround.py:6:1: E401 [*] Multiple imports on one line
ai-eggs/agent/_vk_photo_workaround.py:31:9: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_photo_workaround.py:61:13: S603 `subprocess` call: check for execution of untrusted input
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
```

🔧 **ruff --fix:** 8 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-29\')

**Критических ошибок ruff (E,F,S,B):** 1663

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 ai-eggs                                   |  0
 angel-backend                             |  0
 checkpoints/chp_20260528_230005.md        | 25 ++++++++
 chp.md                                    | 72 ++++++++---------------
 dreams/dream_2026-05-28.md                | 97 +++++++++++++++++++++++++++++++
 dreams/patterns.md                        | 86 +++++++++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-28.md | 70 ++++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-29.md | 76 ++++++++++++++++++++++++
 8 files changed, 379 insertions(+), 47 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

### Найденные проблемы

---

#### 1  
**Файл:** `ai-eggs/agent/tg_bot.py`, строки 1, 5  
**Проблема:** импорты `csv`, `time`, `re` и функции/классы этих модулей **никогда не используются** в коде.  
**Критичность:** 🟢 Минорно (мертвый импорт, раздувает импорт-лист).  
**Исправление:** удалить неиспользуемые импорты.

---

#### 2  
**Файл:** `ai-eggs/agent/angelochka_core.py`, строка 7  
**Проблема:** повторный `import re as _re_core` сразу после `import re`. Один и тот же модуль импортируется дважды под разными названиями.  
**Критичность:** 🟢 Минорно  
**Исправление:** оставить только один import (`import re`), убрать `_re_core`.

---

#### 3  
**Файл:** `ai-eggs/agent/angelochka_core.py`, строка 26  
**Проблема:** переменная `_CREATOR_TG_ID` сверяется со `sender_id` как **строка**, а в `tg_bot.py` переменная `ADMIN_TELEGRAM_ID` преобразуется в `int` и используется в качестве **числа**.  
  - `detect_role` принимает `sender_id` и сверяет его как строку → int 176203333 не совпадёт со строкой "176203333" при нестрогом сравнении.  
**Критичность:** 🔴 Критично (роль «creator» никогда не определится, даже если совпадает ID).  
**Исправление:** привести типы к единому формату:  
```python
_CREATOR_TG_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "176203333"))
```
и далее `if sid == str(_CREATOR_TG_ID):`.

---

#### 4  
**Файл:** `ai-eggs/agent/bitrix_intelligence.py`, строка 59 – 67 и все места использования `MANAGERS`  
**Проблема:** глобальная мутабельная структура `MANAGERS` инициализируется в `load_managers()`, но при повторном импортировании модуля или параллельном запуске в разных процессах через PM2 кэш **может оказаться неактуальным**. Кроме того, разные процессы будут иметь разные экземпляры этого словаря.  
**Критичность:** 🟡 Важно (состояние будет раздираться; при нескольких экземплярах разведывательный модуль увидит разные данные).  
**Исправление:** убрать мутабельный глобальный кэш, перенести загрузку в `__main__` или читать дисковый кэш/базу данных при необходимости.

---

#### 5  
**Файл:** `ai-eggs/agent/bitrix_intelligence.py`, строки 43 – 46  
**Проблема:** при отсутствии файла `.env` или пустой переменной `PRODUCTION_BITRIX_WEBHOOK_URL` скрипт продолжает работать. `bx_post` вызовет `requests.post("{BITRIX_URL}/{method}")` с `BITRIX_URL=""` → будет запрос к `/{method}`, что не тот URL.  
**Критичность:** 🔴 Критично (фактически поймаем 400/404 и никакого upfront-информирования).  
**Исправление:** добавить проверку:
```python
if not BITRIX_URL:
    log("🛑 PRODUCTION_BITRIX_WEBHOOK_URL не задан!")
    sys.exit(1)
```

---

#### 6  
**Файл:** `ai-eggs/agent/bitrix_intelligence.py`, строка 60  
**Проблема:** в теле `bx_post` исключения перехватываются, но **пустой словарь возвращается без записи в лог ошибки** (или возвращается `None`).  
**Критичность:** 🟡 Важно (тихий крах, не понятно, почему нет данных).  
**Исправление:** в секции `except` добавить лог или re-raise конкретное исключение.

---

#### 7  
**Файл:** `ai-eggs/agent/tg_bot.py`, строка 146  
**Проблема:** при обращении к `message.from_user.id` может быть `None` (например, при inline-запросах или во время реакций). Хотя в контексте `message` обычно этого нет, теоретически `from_user` == None приведёт к AttributeError, но это не обработано.  
**Критичность:** 🟢 Минорно  
**Исправление:** добавить проверку:
```python
if not message.from_user:
    return
```

---

#### 8  
**Файл:** `ai-eggs/agent/angelochka_core.py`, функция `_has_phone_in_history`, строки 111 – 114  
**Проблема:** в цикле `for msg in history:` при `parts` не проверяется, что `parts` действительно список (может попасться `None`, `dict`, etc.) → вызов `str(parts[0])` выкинет `TypeError`.  
**Критичность:** 🔴 Критично  
**Исправление:** сделать дополнительную проверку типа:
```python
if not isinstance(parts, (list, tuple)) or not parts:
    continue
```

---

#### 9  
**Файл:** `ai-eggs/agent/tg_bot.py`, строка 174  
**Проблема:** на VPS при перезагрузке контейнера/перезапуска PM2 `LOG_ONLY_FLAG` (файл `LOG_ONLY`) **не создаётся автоматически**; если кто-то его удалит — молчаливый режим перэйключится и может быть неочевидным.  
**Критичность:** 🟡 Важно  
**Исправление:** использовать `.env` параметр вместо «флаг-файла» (`SILENT_MODE=true/false`).

---

### Итого
🔴 x3 критичные,  
🟡 x4 важные,  
🟢 x2 минорные.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-29 |
| ⏰ Время | 02:11:57 → 02:13:02 |
| 📁 Python файлов | 196 |
| 📝 Изменено за день | 8 |
| ⚡ ruff ошибок (E,F,S,B) | 1663 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 4 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 4 |

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
