# 🌙 Ночной аудит кода — 2026-05-22

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:12:24  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 183 (проверяем: 5)  
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
ai-eggs/agent/angelochka_core.py:95:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:151:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:161:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:175:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:206:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:218:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:219:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:226:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:238:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:239:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:252:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:268:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:269:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:307:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:325:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:334:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:349:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:472:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:491:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:577:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:581:89: E501 Line too long (98 > 88)
ai-eggs/agent/angelochka_core.py:599:89: E501 Line too long (94 > 88)
ai-eggs/agent/angelochka_core.py:601:89: E501 Line too long (91 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-22\')

**Критических ошибок ruff (E,F,S,B):** 1498

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 .../27_05_2026_12_bees/photo_old_phoenix.png"      | Bin 0 -> 859641 bytes
 .../28_05_2026_13_tips/photo.png"                  | Bin 858298 -> 2450474 bytes
 .../28_05_2026_13_tips/photo_old_phoenix.png"      | Bin 0 -> 858298 bytes
 .../29_05_2026_14_garden/photo.png"                | Bin 863479 -> 2156733 bytes
 .../29_05_2026_14_garden/photo_old_phoenix.png"    | Bin 0 -> 863479 bytes
 .../30_05_2026_15_rabbits/photo.png"               | Bin 675492 -> 1863805 bytes
 .../30_05_2026_15_rabbits/photo_old_phoenix.png"   | Bin 0 -> 675492 bytes
 .../31_05_2026_16_poultry/photo.png"               | Bin 686315 -> 1762367 bytes
 .../31_05_2026_16_poultry/photo_old_phoenix.png"   | Bin 0 -> 686315 bytes
 48 files changed, 1646 insertions(+), 61 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Проанализировав предоставленный diff, обнаружил несколько проблем:

## 🐛 Найденные проблемы

### **ai-eggs/agent/angelochka_core.py:69**
**Критичность:** 🟡 Важно
**Проблема:** Потенциальный crash при чтении roles_config.json — если файл существует, но не является валидным JSON, исключение JSONDecodeError обрабатывается, но если файла нет прав на чтение или другие IO ошибки, они попадут в общий Exception блок, что может скрыть реальную причину.
**Исправление:** 
```python
except (json.JSONDecodeError, FileNotFoundError, PermissionError) as _e:
    print(f"⚠️ detect_role: ошибка чтения roles_config.json: {_e}")
except Exception as _e:
    print(f"⚠️ detect_role: неожиданная ошибка: {_e}")
```

### **ai-eggs/agent/tg_bot.py:44-48**
**Критичность:** 🟡 Важно  
**Проблема:** Hardcoded fallback ID администратора в коде противоречит принципу "единого источника истины" из комментария выше.
**Исправление:** Убрать fallback или вынести в константу/переменную окружения:
```python
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID")) if os.getenv("ADMIN_TELEGRAM_ID") else None
if ADMIN_ID is None:
    raise ValueError("❌ ADMIN_TELEGRAM_ID обязателен в .env!")
```

### **ai-eggs/agent/bitrix_intelligence.py:73-74**
**Критичность:** 🟡 Важно
**Проблема:** Слишком агрессивная обработка ответа API — если `items` является словарем, код пытается извлечь `tasks` или `items`, но может получить пустой список даже при валидных данных другой структуры.
**Исправление:** Добавить логирование и более аккуратную обработку:
```python
items = data.get(key, [])
if isinstance(items, dict):
    # Логируем структуру для отладки
    log(f"API вернул dict вместо list для {method}: {list(items.keys())}")
    items = items.get("tasks", items.get("items", []))
```

### **ai-eggs/agent/bitrix_intelligence.py:58**
**Критичность:** 🟢 Минорно
**Проблема:** Мёртвый код — переменная `max_iterations` объявлена но используется только в range(), можно сделать проще.
**Исправление:** 
```python
for iteration in range(50):  # защита от бесконечного цикла
```

### **ai-eggs/agent/angelochka_core.py:36**
**Критичность:** 🟢 Минорно
**Проблема:** Импорт `traceback` внутри except блока неэффективен — лучше импортировать в начале файла.
**Исправление:** Добавить `import traceback` в секцию импортов.

## ⚠️ Потенциальные проблемы (требуют проверки полного кода)

### **ai-eggs/agent/bitrix_intelligence.py:111**
**Критичность:** 🟡 Важно
**Проблема:** Функция `scan_deals()` объявлена но код обрезан — нужно проверить обработку исключений при работе с API и парсинге дат.

### **ai-eggs/agent/tg_bot.py:30**
**Критичность:** 🟡 Важно
**Проблема:** Функция `_make_session()` создает сессию но нет явного управления её жизненным циклом — потенциальная утечка ресурсов.

## ✅ Хорошие практики в коде
- Правильное использование типов ролей через константы
- Грамотная обработка импортов с fallback'ами  
- Централизованная конфигурация через .env
- Логирование ошибок

**Общая оценка:** Код написан аккуратно, критических уязвимостей не обнаружено. Основные проблемы касаются обработки исключений и hardcoded значений.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-22 |
| ⏰ Время | 02:12:24 → 02:12:44 |
| 📁 Python файлов | 183 |
| 📝 Изменено за день | 48 |
| ⚡ ruff ошибок (E,F,S,B) | 1498 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 0
0 |
| 🟡 Важных (Claude) | 5 |
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
