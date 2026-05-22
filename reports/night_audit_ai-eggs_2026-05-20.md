# 🌙 Ночной аудит кода — 2026-05-20

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
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
ai-eggs/agent/angelochka_core.py:595:89: E501 Line too long (94 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-20\')

**Критических ошибок ruff (E,F,S,B):** 1502

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
 46 files changed, 1533 insertions(+)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Проанализировал дифф. Обнаружил несколько серьёзных проблем:

## 🔴 КРИТИЧНЫЕ БАГИ

**ai-eggs/agent/angelochka_core.py:73-84** — Необработанное исключение при чтении JSON
```python
with open(_roles_path, "r", encoding="utf-8") as _f:
    _cfg = json.load(_f)  # ← Может упасть на битом JSON
```
**Критичность:** 🔴 Критично  
**Исправление:** Добавить `json.JSONDecodeError` в except блок, сейчас ловится только общий Exception

**ai-eggs/agent/tg_bot.py:35** — Hardcoded admin ID в коде
```python
ADMIN_ID = 176203333
```
**Критичность:** 🔴 Критично  
**Исправление:** Вынести в переменную окружения `ADMIN_TELEGRAM_ID`

**ai-eggs/agent/bitrix_intelligence.py:111-115** — Необработанное исключение при работе с API
```python
def scan_deals():
    new_deals = bx_post("crm.deal.list", {
    # ← Отсутствует обработка None/пустого ответа
```
**Критичность:** 🔴 Критично  
**Исправление:** Добавить проверку результата перед `.get("result", [])`

## 🟡 ВАЖНЫЕ ПРОБЛЕМЫ

**ai-eggs/agent/angelochka_core.py:54-56** — Дублирование константы admin ID
```python
_CREATOR_TG_ID = "176203333"  # Игорь Васин (admin)
# В tg_bot.py: ADMIN_ID = 176203333
```
**Критичность:** 🟡 Важно  
**Исправление:** Использовать единый источник истины (переменная окружения)

**ai-eggs/agent/tg_bot.py:15-16** — Закомментированные импорты без удаления
```python
# from voice_engine import generate_voice, cleanup_voice
# from aiogram.types import FSInputFile
```
**Критичность:** 🟡 Важно  
**Исправление:** Удалить мёртвый код или реализовать функциональность

**ai-eggs/agent/bitrix_intelligence.py:75-80** — Race condition в методе `bx_get_all`
```python
while True:
    data = bx_post(method, params)
    # ← Нет защиты от бесконечного цикла при сбое API
```
**Критичность:** 🟡 Важно  
**Исправление:** Добавить счётчик итераций и timeout

## 🟢 МИНОРНЫЕ ЗАМЕЧАНИЯ

**ai-eggs/agent/angelochka_core.py:90-100** — Сложная вложенная логика в `_has_phone_in_history`
**Критичность:** 🟢 Минорно  
**Исправление:** Разбить на отдельные функции для читаемости

**ai-eggs/agent/bitrix_intelligence.py:25** — Загрузка .env в глобальной области
**Критичность:** 🟢 Минорно  
**Исправление:** Перенести в функцию инициализации

## ИТОГИ АУДИТА

Обнаружено **3 критичных** и **3 важных** проблемы. Основные риски:
- Необработанные исключения могут привести к краху бота
- Hardcoded admin ID создаёт проблемы безопасности
- Отсутствует защита от бесконечных циклов в API-интеграции

Рекомендую исправить критичные баги перед деплоем в продакшн.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-20 |
| ⏰ Время | 02:00:05 → 02:00:30 |
| 📁 Python файлов | 183 |
| 📝 Изменено за день | 46 |
| ⚡ ruff ошибок (E,F,S,B) | 1502 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 4 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 3 |

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
