# 🌙 Ночной аудит кода — 2026-05-24

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:04  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 189 (проверяем: 5)  
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

🔧 **ruff --fix:** 1 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-05-24\')

**Критических ошибок ruff (E,F,S,B):** 1571

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 chronicles/chronicle_2026-05-22.md                 |     33 +
 reports/kimi_audit_2026-05-23.md                   |     91 +
 reports/night_audit_ai-eggs_2026-05-23.md          |     60 +-
 reports/night_audit_ai-eggs_2026-05-24.md          |     76 +
 tools/finish_day.sh                                |      9 +
 tools/import_cursor_skills.sh                      |     96 +
 tools/morning_dream.sh                             |     37 +-
 tools/night_audit.sh                               |     41 +-
 tools/sync_cursor_rules.sh                         |    152 +
 74 files changed, 404450 insertions(+), 9882 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Ниже ‒ только реально существующие баги, которые Gemini не отловил.

**tg_bot.py:23-31**  
**Проблема:** Три последовательные `load_dotenv(...)` вызываются с разными `override=True/False`; в итоге если человек уже передал переменную в ОС, то `.env`-файл всё равно НЕ перезапишет её первым `override=True`, а последующие вызовы (`override=False`) вернут старое значение.  
**Критичность:** 🟡 Важно  
**Исправление:** оставить ровно один `load_dotenv(_AGENT_ENV, override=True)` и удалить остальные.

---

**angelochka_core.py:49**  
**Проблема:** `os.getenv("ADMIN_TELEGRAM_ID", "176203333")` пишет строку `"176203333"` в `_CREATOR_TG_ID`, а затем сравнивается со строкой `sender_id`. Если в `roles_config.json` sender_id сохранён как `int`, условие `sid == _CREATOR_TG_ID` упадёт.  
**Критичность:** 🟡 Важно  
**Исправление:**  
```python
_CREATOR_TG_ID = str(os.getenv("ADMIN_TELEGRAM_ID", "176203333")).strip()
```

---

**angelochka_core.py:74**  
**Проблема:** при `json.JSONDecodeError` логируется только сообщение, но дальше выполнение продолжается: если файл повреждён, `roles_config.json` будет проигнорирован и все пользователи fallback-ят в `ROLE_CUSTOMER`, хотя админ может рассчитывать иначе.  
**Критичность:** 🟢 Минорно  
**Исправление:** после ловли `json.JSONDecodeError` считать конфиг невалидным иfallback к отсутствию файла (уже реализовано), поэтому достаточно добавить `pass` и оставить как есть, или добавить `continue`.

---

**bitrix_intelligence.py:73-78**  
**Проблема:** функция `bx_post` при любой ошибке (timeout, 404, 5xx, JSON с ошибкой внутри) возвращает `{}`, после чего вызывающий код использует `.get("result", [])`, получая пустой список. Это скрывает любые сбои интеграции с Битриксом и может привести к тому, что нулевая выручка/сделки не вызовут тревоги.  
**Критичность:** 🟡 Важно  
**Исправление:** добавить минимальное логирование и/или raise, иначе стратегия «fail-silent»:

```python
def bx_post(method, params=None):
    try:
        resp = requests.post(f"{BITRIX_URL}/{method}", json=params or {}, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("error"):
                log(f"Bitrix API error {method}: {data['error_description']}")
            return data
    except Exception as e:
        log(f"Request failed {method}: {e}")
    return {}
```

---

**bitrix_intelligence.py:85-86, 95-96**  
**Проблема:** при пагинации `start = next_page` может быть любым строковым значением (<https://training.bitrix24.com/rest_help/rest_sum/pagination.php>); в коде оно просто подставляется без проверки типа. Если Bitrix по-ошибке вернёт `next: "300_SYMBOLIC_HASH"`, скрипт должен упасть на `TypeError`.  
**Критичность:** 🟢 Минорно  
**Исправление:** явно привести к `int`: `params["start"] = int(next_page)`.

---

**tg_bot.py:217-225**  
**Проблема:** в `/status` и других админ-командах логика проверяет `is_admin(message.from_user.id)`, но `message` может прийти из **inline-запроса** или **реакции**, где `from_user is None`; не везде добавлена защита. Примеры строк:

```python
async def quick_report_callback(callback_query: types.CallbackQuery):
    ...
    if not is_admin(callback_query.from_user.id):
```

Если `from_user=None`, упадёт `NoneType.int`.  
**Критичность:** 🟢 Минорно (сценарий редко достижим)  
**Исправление:** добавить центральную обёртку:

```python
user_id = getattr(msg, 'from_user', None)
if user_id is None:
    return
user_id = user_id.id
```

---

**tg_bot.py:58-62 + ещё множество вызовов `requests` из других модулей**  
**Проблема:** `VoiceEngine`, `bitrix_intelligence.py`, `angelochka_core.py` используют синхронный `requests`/`requests.post` изнутри асинхронного кода (`dispatcher`, `async handler`). Это блокирует event-loop на время поллинга → весь бот подвисает.  
**Критичность:** 🔴 Критично (простановка запроса на 1–2 с задержит всех клиентов)  
**Исправление:** заменить на `aiohttp`, `httpx.AsyncClient`, или запростить через `asyncio.get_running_loop().run_in_executor`.

---

**bitrix_intelligence.py:SYS.PATH**  
**Проблема:** `sys.path.insert(0, AGENT_DIR)` может привести к импорту сторонних .py файлов из `ai-eggs/agent` под теми же именами, что установлены в `site-packages` (привет, `requests.py`).  
**Критичность:** 🟢 Минорно  
**Исправление:** использовать явный импорт как модуль: `from .env import load_dotenv` после превращения в пакет или отказаться от `sys.path.insert`.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-24 |
| ⏰ Время | 02:00:04 → 02:01:02 |
| 📁 Python файлов | 189 |
| 📝 Изменено за день | 74 |
| ⚡ ruff ошибок (E,F,S,B) | 1571 |
| 🔐 Hardcoded секретов | 0 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 1 |
| 🟡 Важных (Claude) | 3 |
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
