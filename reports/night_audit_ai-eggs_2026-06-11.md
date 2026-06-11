# 🌙 Ночной аудит кода — 2026-06-11

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:03  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 203 (проверяем: 2)  
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
ai-eggs/agent/_bx_explore.py:3:8: F401 [*] `csv` imported but unused
ai-eggs/agent/_bx_explore.py:4:8: F401 [*] `json` imported but unused
ai-eggs/agent/_bx_explore.py:6:8: F401 [*] `sys` imported but unused
ai-eggs/agent/_bx_explore.py:40:89: E501 Line too long (91 > 88)
ai-eggs/agent/_bx_explore.py:47:89: E501 Line too long (137 > 88)
ai-eggs/agent/_bx_explore.py:59:89: E501 Line too long (94 > 88)
ai-eggs/agent/_bx_turkey.py:6:1: E401 [*] Multiple imports on one line
ai-eggs/agent/_bx_turkey.py:6:13: F401 [*] `json` imported but unused
ai-eggs/agent/_bx_turkey.py:6:23: F401 [*] `re` imported but unused
ai-eggs/agent/_bx_turkey.py:6:27: F401 [*] `sys` imported but unused
ai-eggs/agent/_bx_turkey.py:33:16: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:48:17: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:52:15: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:80:17: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:84:15: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:118:89: E501 Line too long (94 > 88)
ai-eggs/agent/_bx_turkey.py:166:7: S108 Probable insecure usage of temporary file or directory: "/tmp/turkey_deals.csv"
ai-eggs/agent/_bx_turkey.py:178:89: E501 Line too long (91 > 88)
ai-eggs/agent/_fix_csv_read.py:3:8: F401 [*] `re` imported but unused
ai-eggs/agent/_fix_csv_read.py:14:5: B007 Loop control variable `i` not used within loop body
ai-eggs/agent/_fix_csv_read.py:21:89: E501 Line too long (103 > 88)
ai-eggs/agent/_fix_csv_read.py:25:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_csv_read.py:28:88: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_csv_read.py:30:89: E501 Line too long (89 > 88)
ai-eggs/agent/_fix_fuzzy.py:19:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_fuzzy.py:23:89: E501 Line too long (103 > 88)
ai-eggs/agent/_fix_fuzzy.py:24:89: E501 Line too long (94 > 88)
ai-eggs/agent/_fix_fuzzy.py:25:89: E501 Line too long (98 > 88)
ai-eggs/agent/_fix_fuzzy.py:29:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_fuzzy.py:33:89: E501 Line too long (97 > 88)
ai-eggs/agent/_fix_fuzzy.py:35:89: E501 Line too long (99 > 88)
ai-eggs/agent/_fix_fuzzy.py:41:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_fuzzy.py:45:89: E501 Line too long (97 > 88)
ai-eggs/agent/_fix_fuzzy.py:47:89: E501 Line too long (96 > 88)
ai-eggs/agent/_fix_fuzzy.py:51:89: E501 Line too long (103 > 88)
ai-eggs/agent/_fix_fuzzy.py:54:89: E501 Line too long (94 > 88)
ai-eggs/agent/_fix_fuzzy.py:55:89: E501 Line too long (98 > 88)
ai-eggs/agent/_fix_fuzzy.py:59:89: E501 Line too long (98 > 88)
ai-eggs/agent/_vk_auth.py:29:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:41:10: S603 `subprocess` call: check for execution of untrusted input
```

🔧 **ruff --fix:** 9 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-11\')

**Критических ошибок ruff (E,F,S,B):** 1708

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 chronicles/chronicle_2026-06-10.md        |  10 +
 dreams/dream_2026-06-09.md                |  34 ++++
 dreams/dream_2026-06-10.md                |  34 ++++
 dreams/patterns.md                        |  52 +++++
 reports/night_audit_ai-eggs_2026-06-09.md |  70 +++++++
 reports/night_audit_ai-eggs_2026-06-10.md | 136 +++++++++++++
 reports/night_audit_ai-eggs_2026-06-11.md |  79 ++++++++
 reports/planner_2026-06-09_1950.md        |  89 +++++++++
 tools/model_router.py                     |  10 +-
 19 files changed, 1334 insertions(+), 135 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

## 🔍 Найденные баги

### 1. **не до конца** обрабатывает пустые/невалидные JSON от LLM
**Файл:llm_planner.py:320** (`_judge` method)  
**Критичность:** 🔴 Критично  
**Исправление:**  
Текущее регулярное выражение достаточно "широкое":  
```python
match = re.search(r'\{[\s\S]*"score"[\s\S]*\}', raw)
```
если модель вернёт _два_ объекта (например, «```json{}``` и ещё один текст{}»), то `match.group()` вернёт всё с первой «{» до последней «}» и `json.loads` сломается.  
При этом последующий `json.loads(match.group() if match else raw)` может успеть распарсить _часть_ строки как невалидный JSON (например, если внутри будут неэкранированные переводы строк).  
→ Жёстко ограничьте регуляркой только первый JSON-блок  
```python
match = re.search(r'\{(?:[^{}]|(?R))*\}', raw)
if not match:
    raise ValueError("No JSON block found")
```

---

### 2. Небезопасное пользование `eval()`-подобным set-building
**Файл:llm_planner.py:276-278** (research judge)  
**Критичность:** 🟡 Важно  
**Исправление:**  
В `RESEARCH_JUDGE_PROMPT` модель будет писать `"converged": true/false`, но строка `bool(data.get("converged", score >= …))` может получить из ответа `data["converged"] = "false"` → в Python `"false"` это **truthy** ⇒ цикл продолжится там, где должен был stop.  
→ Добавьте корректное преобразование  
```python
conv = str(data.get("converged", "")).lower()
converged = conv == "true"
```

---

### 3. Роскошный DoS: неограниченно растущий `previous_outputs`
**Файл:llm_planner.py:433**  
**Критичность:** 🟡 Важно  
**Исправление:**  
Массив `previous_outputs` при `task_type="research"` добавляет `new_output` без ограничения.  
Хотя далее используется only последние 3, вы держите в памяти **все** итерации. Если `max_iterations` когда-нибудь вырастет до 500 — памяти не хватит.  
→ Ограничьте список явно  
```python
previous_outputs.append(new_output)
previous_outputs = previous_outputs[-3:]   # всегда последние три
```

---

### 4. Отсутствует проверка на отрицательный `threshold` / `max_iterations`
**Файл:llm_planner.py:215, 224** (`__init__`)  
**Критичность:** 🟢 Минорно  
**Исправление:**  
Пользователь может вызвать `LoopPlanner(threshold=-10)` или `max_iterations=0` и получить падающий код / бесконечный цикл (`range(0)` → 0 итераций и `converged=False`, но стоп не сработает).  
→ Добавить валидацию в конструкторе  
```python
if not 0 <= threshold <= 1:
    raise ValueError("threshold must be between 0 and 1")
if max_iterations < 1:
    raise ValueError("max_iterations must be >= 1")
```

---

### 5. Два разных `ToolKit` создаются подряд — race-condition на `PROXY`?
**Файл:llm_planner.py:402-409**  
**Критичность:** 🟡 Важно  
**Исправление:**  
Строки 402-411 напрямую пересоздают `AsyncClient` и **никогда не закрывают** его (нет `await c.aclose()`).  
Вместо неявного большого `timeout=4.0` вы можете зависнуть или заблокировать event-loop.  
→ Использовать **один** `AsyncClient`, прокинутый в ToolKit, и закрывать в конце:  
```python
async with httpx.AsyncClient(proxy=PROXY, timeout=4.0) as http_client:
    toolkit_obj = ToolKit(client=http_client)
```

---

### 6. Использование `chr(10)` для `\n` — небезопасно для maintenance
**Файл:llm_planner.py:448**  
**Критичность:** 🟢 Минорно  
**Исправление:**  
`chr(10)` эквивалентно `'\n'` но хуже читаемо и может быть «обфускатором».  
→ Просто `'\n'` или `os.linesep`.

---

### 7. Никто не выгружает неиспользуемые импорты
**Файл:llm_planner.py: заголовок**  
**Критичность:** 🟢 Минорно  
**Исправление:**  
Судя по diff `asyncio` импортируется, но не используется (день назад уже был `.run` ⇒ хвост).  
(строка не показана, но там можно встретить `import asyncio`).

---

Лёгкая деплой-нота: если `PROXY` вдруг упадёт, `httpx.AsyncClient(proxy=PROXY)` выкинет 502. В catch-блоке вы **сбрасываете на PROXY_DIRECT**, но нигде **не логируете** детали ошибки — потом не разберёшь, какой именно прокси был test-fail. Хотя это не баг самого loop-кода, советую логировать `e` туда же в `_log`.

Итог: ошибки **реальные**, но не критические — быстро ремонтируются без изменения сигнатур.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-11 |
| ⏰ Время | 02:00:03 → 02:00:57 |
| 📁 Python файлов | 203 |
| 📝 Изменено за день | 19 |
| ⚡ ruff ошибок (E,F,S,B) | 1708 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 1 |
| 🟡 Важных (Claude) | 3 |
| 🟢 Минорных (Claude) | 3 |

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
