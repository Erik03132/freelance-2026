# 🌙 Ночной аудит кода — 2026-05-16

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 174 (проверяем: 1)  
> **Источник:** git diff HEAD~1 (1 файлов)

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
ai-eggs/agent/angelochka_core.py:91:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:147:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:157:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:171:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:202:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:214:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:215:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:222:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:234:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:235:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:248:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:264:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:265:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:303:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:321:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:330:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:345:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:468:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:487:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:566:18: B007 Loop control variable `score` not used within loop body
ai-eggs/agent/angelochka_core.py:573:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:577:89: E501 Line too long (98 > 88)
```

🔧 **ruff --fix:** 89 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-16\')

**Критических ошибок ruff (E,F,S,B):** 1448

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 dreams/dream_2026-05-15.md                     | 102 +++++++++++++++++++
 dreams/patterns.md                             |  86 ++++++++++++++++
 mango_api.py                                   | 136 +++++++++++++++++++++++++
 ok/2026-05-16_01/photo.png                     | Bin 1948762 -> 0 bytes
 ok/2026-05-16_02/photo.png                     | Bin 0 -> 104722 bytes
 ok/2026-05-16_03/photo.png                     | Bin 0 -> 158574 bytes
 reports/night_audit_ai-eggs_2026-05-15.md      | 110 ++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-16.md      |  76 ++++++++++++++
 test_mango_call.py                             |  67 ++++++++++++
 58 files changed, 1102 insertions(+), 2 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Проанализировал код и нашел несколько серьезных проблем:

## 🔒 **КРИТИЧНЫЕ ПРОБЛЕМЫ БЕЗОПАСНОСТИ**

**mango_api.py:16-17** — Хардкод API ключей в коде
- **Критичность:** 🔴 Критично
- **Исправление:** Вынести в переменные окружения:
```python
import os
VPBX_API_KEY = os.getenv('MANGO_API_KEY')
VPBX_API_SALT = os.getenv('MANGO_API_SALT')
if not VPBX_API_KEY or not VPBX_API_SALT:
    raise ValueError("Mango API credentials not found in environment")
```

## 🐛 **ЛОГИЧЕСКИЕ БАГИ**

**mango_api.py:61** — Неправильная обработка результата API
- **Критичность:** 🟡 Важно
- **Проблема:** Код проверяет `result not in (0, 1000, None)`, но согласно комментарию успех = 1000, а ошибки = 3xxx/4xxx/5xxx
- **Исправление:**
```python
if result.get('result') != 1000 and result.get('result') is not None:
    raise Exception(f"API Error: {result}")
```

**mango_api.py:52-56** — Отладочный вывод в production коде
- **Критичность:** 🟡 Важно
- **Проблема:** `print()` выводит payload с API ключами в логи
- **Исправление:** Заменить на logging с маскированием чувствительных данных

## 💣 **ПОТЕНЦИАЛЬНЫЕ КРЭШИ**

**mango_api.py:58** — Необработанное исключение JSON парсинга
- **Критичность:** 🟡 Важно
- **Исправление:**
```python
try:
    result = response.json()
except json.JSONDecodeError:
    raise Exception(f"Invalid JSON response: {response.text}")
```

**test_mango_call.py:20** — Отсутствие проверки структуры ответа
- **Критичность:** 🟡 Важно
- **Проблема:** Может упасть на `balance_result['balance']` если ключа нет
- **Исправление:**
```python
if balance_result.get('result') == 1000 and 'balance' in balance_result:
    print(f"   Баланс: {balance_result['balance']} {balance_result.get('currency', 'RUB')}")
```

## 🧟 **МЁРТВЫЙ КОД**

**mango_api.py:12** — Неиспользуемый импорт `uuid`
- **Критичность:** 🟢 Минорно
- **Исправление:** Убрать строку `import uuid` (uuid используется только в `make_call`, переместить импорт туда)

## ⚡ **ПРОБЛЕМЫ ПРОИЗВОДИТЕЛЬНОСТИ**

**mango_api.py:28** — Двойная сериализация JSON
- **Критичность:** 🟢 Минорно
- **Проблема:** JSON сериализуется дважды - в `generate_signature` и `make_request`
- **Исправление:** Вынести сериализацию в отдельную переменную

**Итог:** Найдено 7 проблем, 1 критичная (хардкод ключей), 4 важных, 2 минорных.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-16 |
| ⏰ Время | 02:00:05 → 02:00:28 |
| 📁 Python файлов | 174 |
| 📝 Изменено за день | 58 |
| ⚡ ruff ошибок (E,F,S,B) | 1448 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 1 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 2 |

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
