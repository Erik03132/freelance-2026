# 🌙 Ночной аудит кода — 2026-06-07

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:00  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 197 (проверяем: 3)  
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
ai-eggs/agent/_vk_auth.py:29:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:41:10: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_get_token.py:26:17: S105 Possible hardcoded password assigned to: "client_secret"
ai-eggs/agent/_vk_get_token.py:31:5: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_get_token.py:43:89: E501 Line too long (101 > 88)
ai-eggs/agent/_vk_photo_workaround.py:24:89: E501 Line too long (126 > 88)
ai-eggs/agent/_vk_photo_workaround.py:34:9: S603 `subprocess` call: check for execution of untrusted input
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
ai-eggs/agent/angelochka_core.py:414:89: E501 Line too long (90 > 88)
ai-eggs/agent/angelochka_core.py:479:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:491:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:492:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:509:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:510:89: E501 Line too long (89 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-07\')

**Критических ошибок ruff (E,F,S,B):** 1660

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 ACTIVE_TASKS.md             |  24 +++++++
 agent-lab/llm_engine.py     |   2 +-
 agent-lab/photo_cascade.py  | 154 +++++++++++++++++++++++++++++++++++++++-----
 ai-bureau/AGENTS.md         |   5 +-
 ai-bureau/SESSION_LATEST.md |   4 +-
 ai-eggs                     |   0
 chp.md                      |  56 ++++++++++++++++
 tools/habr_intelligence.py  |   2 +-
 8 files changed, 225 insertions(+), 22 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

Проанализировал дифф. Найденные проблемы:

**/agent-lab/llm_engine.py:28** — неправильное имя модели Ollama в прямой отправке человеку из Gemini (не влияет на работу, но будет путаница)  
**Критичность:** 🟡 Важно  
**Исправление:** `OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b")` заменить на `OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:12b")` или другое существующее имя модели.

**/tools/habr_intelligence.py:40** — продублирована та же опечатка имени модели  
**Критичность:** 🟡 Важно  
**Исправление:** аналогично переправить на существующее имя.

**/agent-lab/photo_cascade.py:213** — метод `ideogram_prompt_builder` создает user-controlled JSON и отправляет его прямо в fal.ai без валидации  
**Критичность:** 🟡 Важно  
**Исправление:** добавить ограничение на длину/символы `subject`, `text_on_image`, `background`, `color_palette`; escaped quotes в `text_on_image` перед вставкой в промпт.

**/agent-lab/photo_cascade.py:261-268** — функция `_generate_ideogram` при ошибке печатает только 120 первых символов ответа; при слишком длинном HTML-респонсе потеряется точная причина сбоя  
**Критичность:** 🟢 Минорно  
**Исправление:** убрать [:120] или логировать до N символов, завершив строку, если есть ограничение лог-сервера.

**/agent-lab/photo_cascade.py:307-314** — метод `_generate_ideogram` возвращает список URL без TTL-валидации; фал.ai могут выдать временные CDN-ссылки, которые истекут, но на другой стороне нет повторной проверки  
**Критичность:** 🟡 Важно  
**Исправление:** серверу, скачивающему/кэширующему картинку, нужен retry с fallback на следующий слой каскада, если ссылка недоступна.

**/agent-lab/photo_cascade.py:333,340** — изменился порядок провайдеров: при `prefer_generated=False` `ideogram` вызывается до `placeholder`, что лишает `placeholder` шанса выполниться при пустом Unsplash или ошибке  
**Критичность:** 🟢 Минорно  
**Исправление:** в `get_photo()` в строке 340 порядок должен быть `["unsplash", "ideogram", "leonardo", "placeholder"]` при `prefer_generated=False`, если `leonardo` должен быть повторен при ошибке `ideogram`.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-07 |
| ⏰ Время | 02:00:00 → 02:00:31 |
| 📁 Python файлов | 197 |
| 📝 Изменено за день | 8 |
| ⚡ ruff ошибок (E,F,S,B) | 1660 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 0
0 |
| 🟡 Важных (Claude) | 4 |
| 🟢 Минорных (Claude) | 2 |

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
