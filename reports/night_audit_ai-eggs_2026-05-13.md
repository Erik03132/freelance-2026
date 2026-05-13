# 🌙 Ночной аудит кода — 2026-05-13

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 146 (проверяем: 3)  
> **Источник:** git diff HEAD~1 (3 файлов)

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
ai-eggs/agent/_archived/send_report.py:8:13: F821 Undefined name `os`
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
ai-eggs/agent/angelochka_core.py:44:89: E501 Line too long (99 > 88)
ai-eggs/agent/angelochka_core.py:61:89: E501 Line too long (101 > 88)
ai-eggs/agent/angelochka_core.py:85:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:141:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:151:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:164:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:191:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:203:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:204:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:211:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:223:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:224:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:233:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:249:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:250:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:288:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:306:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:315:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:330:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:453:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:472:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:551:18: B007 Loop control variable `score` not used within loop body
```

🔧 **ruff --fix:** 24 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-13\')

**Критических ошибок ruff (E,F,S,B):** 1285

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 ok/vezemcyp/2026-06-16/post.txt           |   5 +
 ok/vezemcyp/2026-06-17/post.txt           |   5 +
 ok/vezemcyp/2026-06-18/post.txt           |   5 +
 ok/vezemcyp/2026-06-19/post.txt           |   5 +
 ok/vezemcyp/ok_queue.json                 | 488 ++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-12.md | 118 ++++
 reports/night_audit_ai-eggs_2026-05-13.md |  76 +++
 reports/waza/waza-audit_2026-05-12.md     |  96 ++++
 tools/ping_apis.sh                        | 219 +++++++
 313 files changed, 9061 insertions(+), 14 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Проанализировав предоставленный diff, обнаружил следующие проблемы:

## 🐛 **Файл:297** — Потенциальный IndexError при обращении к citations
- **Критичность:** 🟡 Важно
- **Проблема:** `citations[0] if citations else ""` — проверяется только на пустоту списка, но не на то, что элементы в нём валидны
- **Исправление:** 
```python
"url": citations[0] if citations and len(citations) > 0 and citations[0] else "",
```

## 🔒 **Файл:279** — Отсутствие валидации переменной окружения OPENROUTER_KEY
- **Критичность:** 🟡 Важно  
- **Проблема:** Код проверяет только наличие ключа `if not OPENROUTER_KEY:`, но не его валидность (может быть пустой строкой)
- **Исправление:**
```python
if not OPENROUTER_KEY or not OPENROUTER_KEY.strip():
    return []
```

## 🧟 **Файл:270-315** — Мёртвая переменная PERPLEXITY_KEY
- **Критичность:** 🟢 Минорно
- **Проблема:** После переключения на OpenRouter переменная `PERPLEXITY_KEY` больше не используется, но может остаться в импортах/конфиге
- **Исправление:** Убрать все упоминания `PERPLEXITY_KEY` из кодабзы

## ⚡ **Файл:296** — Отсутствие обработки пустого response
- **Критичность:** 🟡 Важно
- **Проблема:** Код не проверяет, что `data["choices"]` не пустой список перед обращением к `[0]`
- **Исправление:**
```python
if resp.status_code == 200 and data.get("choices") and len(data["choices"]) > 0:
    content = data["choices"][0]["message"]["content"]
```

## 💣 **Файл:283-295** — Потенциальный JSON parsing crash
- **Критичность:** 🟡 Важно
- **Проблема:** `resp.json()` может выбросить JSONDecodeError если API вернёт невалидный JSON
- **Исправление:**
```python
try:
    data = resp.json()
except (ValueError, KeyError) as json_err:
    print(f"⚠️ Perplexity (OpenRouter): JSON parse error — {json_err}")
    return []
```

**Общий вердикт:** Код функционально корректен, но содержит несколько edge cases которые могут привести к runtime ошибкам в продакшене.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-13 |
| ⏰ Время | 02:00:05 → 02:00:22 |
| 📁 Python файлов | 146 |
| 📝 Изменено за день | 313 |
| ⚡ ruff ошибок (E,F,S,B) | 1285 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 0
0 |
| 🟡 Важных (Claude) | 4 |
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
