# 🌙 Ночной аудит кода — 2026-05-12

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:04  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 137 (проверяем: 3)  
> **Источник:** git diff HEAD~1 (3 файлов)

---

## ⚡ Фаза 1: Машинный анализ

### 🔍 ruff — lint
```
ai-eggs/agent/a2a_protocol.py:166:9: S110 `try`-`except`-`pass` detected, consider logging the exception
ai-eggs/agent/a2a_protocol.py:176:89: E501 Line too long (91 > 88)
ai-eggs/agent/agg_temp.py:3:1: E401 [*] Multiple imports on one line
ai-eggs/agent/agg_temp.py:6:89: E501 Line too long (113 > 88)
ai-eggs/agent/agg_temp.py:23:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:23:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/agg_temp.py:45:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:45:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/agg_temp.py:68:7: F541 [*] f-string without any placeholders
ai-eggs/agent/analyze_scan.py:3:1: E401 [*] Multiple imports on one line
ai-eggs/agent/analyze_scan.py:4:22: F401 [*] `datetime.datetime` imported but unused
ai-eggs/agent/analyze_scan.py:30:11: F541 [*] f-string without any placeholders
ai-eggs/agent/analyze_scan.py:39:89: E501 Line too long (95 > 88)
ai-eggs/agent/analyze_scan.py:54:11: F541 [*] f-string without any placeholders
ai-eggs/agent/analyze_scan.py:80:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:93:89: E501 Line too long (90 > 88)
ai-eggs/agent/analyze_scan.py:94:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:106:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:113:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:121:89: E501 Line too long (94 > 88)
ai-eggs/agent/analyze_scan.py:124:89: E501 Line too long (130 > 88)
ai-eggs/agent/analyze_scan.py:129:89: E501 Line too long (98 > 88)
ai-eggs/agent/analyze_scan.py:131:89: E501 Line too long (132 > 88)
ai-eggs/agent/angelochka_core.py:7:40: F401 [*] `hybrid_search.hybrid_search` imported but unused
ai-eggs/agent/angelochka_core.py:7:55: F401 [*] `hybrid_search.init_bm25_index` imported but unused
ai-eggs/agent/angelochka_core.py:8:25: F401 [*] `tool_digest.digest_context` imported but unused
ai-eggs/agent/angelochka_core.py:43:89: E501 Line too long (99 > 88)
ai-eggs/agent/angelochka_core.py:60:89: E501 Line too long (101 > 88)
ai-eggs/agent/angelochka_core.py:84:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:139:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:149:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:162:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:189:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:197:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:198:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:205:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:217:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:218:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:227:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:243:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:244:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:261:15: F541 [*] f-string without any placeholders
ai-eggs/agent/angelochka_core.py:282:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:300:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:309:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:324:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:446:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:465:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:544:18: B007 Loop control variable `score` not used within loop body
ai-eggs/agent/angelochka_core.py:551:89: E501 Line too long (114 > 88)
```

🔧 **ruff --fix:** 244 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-12\')

**Критических ошибок ruff (E,F,S,B):** 1423

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 reports/waza/waza-audit_2026-05-11.md              |  96 +++++++
 shared/event_log.jsonl                             |   1 +
 tools/finish_day.sh                                |  21 +-
 tools/finish_day_cron.sh                           | 111 +++++++++
 tools/night_audit_vps.sh                           | 152 +++++++----
 tools/url_to_markdown.py                           | 277 +++++++++++++++++++++
 tools/vk_autoposter.py                             |  39 +++
 tools/waza-audit.sh                                | 174 +++++++++++++
 utils/agentClient.js                               |  76 ++++++
 33 files changed, 2315 insertions(+), 185 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Проанализировав код, обнаружил несколько проблем:

## 🐛 Найденные проблемы

**Файл:39** — Функция `log()` объявлена но не используется в показанном коде
- **Критичность:** 🟢 Минорно  
- **Исправление:** Удалить неиспользуемую функцию или показать её применение

**Файл:39** — Незавершённый файл `vk_autoposter.py` 
- **Критичность:** 🟡 Важно
- **Исправление:** Код обрывается на 39 строке посреди функции. Нужно увидеть полную реализацию для проверки логики

**Файл:8-9** — Хардкод путей к venv и скриптам без проверки существования
- **Критичность:** 🟡 Важно  
- **Исправление:** Добавить проверку `os.path.exists()` для VENV_PYTHON и SMART_POSTER перед использованием

**Файл:252-266** — Потенциальная уязвимость в статистике
- **Критичность:** 🟡 Важно
- **Исправление:** В блоке `--stats` выполняется HTTP-запрос к пользовательскому URL без валидации. Добавить проверку на безопасные схемы:
```python
from urllib.parse import urlparse
parsed = urlparse(args.url)
if parsed.scheme not in ['http', 'https']:
    raise ValueError("Небезопасная схема URL")
```

**Файл:160** — Возможный path traversal в API URL
- **Критичность:** 🟡 Важно
- **Исправление:** В `_try_http_api()` URL очищается только от протокола, но может содержать `../`. Добавить валидацию:
```python
if '..' in clean_url or '//' in clean_url:
    return ""
```

**Файл:146-154** — subprocess без проверки команды
- **Критичность:** 🟡 Важно  
- **Исправление:** Хотя используется фиксированная команда `npx`, стоит добавить проверку доступности:
```python
if not shutil.which('npx'):
    return ""
```

## ✅ Хорошие практики в коде:

- Правильное использование timeout для subprocess
- Кэширование с TTL
- Обработка исключений в критических местах
- Использование pathlib для работы с путями

## Общая оценка:
Код достаточно качественный, но требует доработки обработки edge cases и завершения второго файла.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-12 |
| ⏰ Время | 02:00:04 → 02:00:17 |
| 📁 Python файлов | 137 |
| 📝 Изменено за день | 33 |
| ⚡ ruff ошибок (E,F,S,B) | 1423 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 0
0 |
| 🟡 Важных (Claude) | 5 |
| 🟢 Минорных (Claude) | 1 |

### Метод аудита
```
Код писали: Gemini 2.5 Pro + Claude Opus (через Antigravity)
Проверяли:
  Фаза 1: ruff 0.15 (машина, 100% точность)
  Фаза 2: Gemini CLI 2.5 Pro (глубокий анализ, бесплатно)
  Фаза 3: Claude Sonnet 4 (cross-model review, OpenRouter)
  
Cross-Model Peer Review: два профессора из разных школ
проверяют код друг друга → максимум найденных багов
```

---

> 🤖 Сгенерировано: `tools/night_audit.sh v2` — Cross-Model Peer Review
