# 🌙 Ночной аудит кода — 2026-05-19

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

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-19\')

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
 46 files changed, 1448 insertions(+)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

После тщательного анализа кода нашёл несколько серьёзных проблем:

## 🔴 КРИТИЧНЫЕ ПРОБЛЕМЫ

**ai-eggs/agent/angelochka_core.py:44**
- **Проблема:** Hardcoded Telegram ID создателя `_CREATOR_TG_ID = "176203333"` прямо в коде
- **Критичность:** 🔴 Критично
- **Исправление:** Вынести в переменную окружения `CREATOR_TELEGRAM_ID` в .env файле

**ai-eggs/agent/tg_bot.py:42**
- **Проблема:** Hardcoded admin ID `ADMIN_ID = 176203333` дублирует уязвимость
- **Критичность:** 🔴 Критично  
- **Исправление:** Использовать `os.getenv("ADMIN_TELEGRAM_ID")` вместо константы

## 🟡 ВАЖНЫЕ ПРОБЛЕМЫ

**ai-eggs/agent/angelochka_core.py:68-78**
- **Проблема:** Блок try-except поглощает ВСЕ исключения при чтении `roles_config.json`, включая критичные
- **Критичность:** 🟡 Важно
- **Исправление:** Обрабатывать конкретные исключения (FileNotFoundError, json.JSONDecodeError)

**ai-eggs/agent/bitrix_intelligence.py:89-97**
- **Проблема:** Функция `bx_get_all` потенциально может зациклиться если API вернёт некорректные данные пагинации
- **Критичность:** 🟡 Важно
- **Исправление:** Добавить счётчик итераций и максимальное количество запросов

**ai-eggs/agent/tg_bot.py:32-36**
- **Проблема:** Функция `_make_session()` принимает параметр `proxy_url`, но не использует его
- **Критичность:** 🟡 Важно
- **Исправление:** Удалить неиспользуемый параметр или реализовать прокси-логику

## 🟢 МИНОРНЫЕ ПРОБЛЕМЫ

**ai-eggs/agent/tg_bot.py:18-20**
- **Проблема:** Закомментированный импорт voice_engine создаёт мёртвый код
- **Критичность:** 🟢 Минорно
- **Исправление:** Удалить закомментированные строки или завернуть в try-except

**ai-eggs/agent/angelochka_core.py:13-18**
- **Проблема:** Импорт `rag_lite` в try-except с print, но без логирования
- **Критичность:** 🟢 Минорно
- **Исправление:** Использовать logging вместо print для консистентности

**ai-eggs/agent/bitrix_intelligence.py:30**
- **Проблема:** Глобальная переменная `MANAGERS = {}` может привести к race conditions при параллельных вызовах
- **Критичность:** 🟢 Минорно
- **Исправление:** Обернуть в класс или использовать thread-safe структуры

**ai-eggs/agent/bitrix_intelligence.py:154** (конец файла)
- **Проблема:** Функция `scan_deals()` обрывается незавершённым API-вызовом
- **Критичность:** 🟢 Минорно
- **Исправление:** Завершить реализацию функции или убрать незавершённый код

Основные риски связаны с безопасностью (hardcoded ID) и потенциальными зависаниями при некорректных ответах API.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-19 |
| ⏰ Время | 02:00:05 → 02:00:27 |
| 📁 Python файлов | 183 |
| 📝 Изменено за день | 46 |
| ⚡ ruff ошибок (E,F,S,B) | 1502 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 3 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 5 |

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
