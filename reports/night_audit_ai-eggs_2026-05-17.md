# 🌙 Ночной аудит кода — 2026-05-17

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:16  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 182 (проверяем: 2)  
> **Источник:** git diff HEAD~1 (2 файлов)

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

🔧 **ruff --fix:** 40 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-17\')

**Критических ошибок ruff (E,F,S,B):** 1525

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 ai-eggs                                            |   0
 angel-backend                                      |   0
 checkpoints/chp_20260516_230045.md                 |  83 +++++++++++++++++++++
 reports/night_audit_ai-eggs_2026-05-17.md          |  76 +++++++++++++++++++
 .../17_05_2026_02_rabbits/photo_creative.png"      | Bin 0 -> 2039012 bytes
 .../17_05_2026_02_rabbits/photo_visionxl.png"      | Bin 0 -> 1933948 bytes
 6 files changed, 159 insertions(+)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Анализирую код...

## 🐛 Найденные проблемы:

### **mango_api.py:70-71** — Логирование чувствительных данных
- **Критичность:** 🔴 Критично
- **Проблема:** API ключи и подписи выводятся в консоль через `print(f"Payload: {payload}")`, что может привести к утечке в логах
- **Исправление:** 
```python
# Безопасное логирование без секретов
safe_payload = {k: "***" if k in ("vpbx_api_key", "sign") else v for k, v in payload.items()}
print(f"Payload: {safe_payload}")
```

### **mango_api.py:82-84** — Неправильная обработка API ошибок
- **Критичность:** 🟡 Важно
- **Проблема:** Код проверяет `result.get('result') not in (0, 1000, None)` но только печатает ошибку, не бросает исключение. Это может привести к тихому игнорированию ошибок API
- **Исправление:**
```python
if result.get('result') not in (0, 1000, None):
    error_msg = f"Mango API Error: {result}"
    print(error_msg)
    raise Exception(error_msg)
```

### **mango_api.py:17** — Потенциальный path traversal
- **Критичность:** 🟡 Важно  
- **Проблема:** Код ищет `.env` файл через `parent.parent`, что может быть небезопасно при манипуляциях с путями
- **Исправление:** Использовать `resolve()` и проверить что путь находится в ожидаемой директории:
```python
_env_path = Path(__file__).resolve().parent.parent / ".env"
_env_path = _env_path.resolve()  # Нормализация пути
```

### **test_mango_call.py:12** — Отсутствует импорт get_balance
- **Критичность:** 🔴 Критично
- **Проблема:** Используется функция `get_balance()` которая не импортирована и возможно не существует в `mango_api.py`
- **Исправление:** Добавить функцию в `mango_api.py` или убрать из теста

### **mango_api.py:72-76** — Отсутствие timeout и retry логики
- **Критичность:** 🟡 Важно
- **Проблема:** Запрос может зависнуть на 30 секунд при проблемах с сетью, нет retry при временных сбоях
- **Исправление:**
```python
for attempt in range(3):
    try:
        response = requests.post(url, data=payload, timeout=10)
        break
    except requests.Timeout:
        if attempt == 2:
            raise
        time.sleep(1)
```

### **mango_api.py:15-19** — Переменные окружения не валидируются
- **Критичность:** 🟡 Важно
- **Проблема:** Пустые `VPBX_API_KEY` и `VPBX_API_SALT` приведут к некорректным подписям, но ошибка проявится только при запросе
- **Исправление:**
```python
VPBX_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
VPBX_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")

if not VPBX_API_KEY or not VPBX_API_SALT:
    raise ValueError("MANGO_VPBX_API_KEY и MANGO_VPBX_API_SALT должны быть установлены")
```

## Итого: 6 проблем (2 критичных, 4 важных)
Основные риски: утечка секретов в логах и необработанная ошибка импорта.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-17 |
| ⏰ Время | 02:00:16 → 02:00:40 |
| 📁 Python файлов | 182 |
| 📝 Изменено за день | 6 |
| ⚡ ruff ошибок (E,F,S,B) | 1525 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 2 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 0
0 |

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
