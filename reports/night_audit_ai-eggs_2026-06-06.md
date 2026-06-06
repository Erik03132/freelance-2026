# 🌙 Ночной аудит кода — 2026-06-06

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
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
ai-eggs/agent/angelochka_core.py:479:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:491:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:492:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:509:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:510:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:523:90: E501 Line too long (93 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-06\')

**Критических ошибок ruff (E,F,S,B):** 1658

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 checkpoints/chp_20260530_230005.md               |  25 ++
 checkpoints/chp_20260531_235824.md               |  25 ++
 chp.md                                           |  14 +-
 ok/2026-05-31_02/photo.png                       | Bin 1467173 -> 0 bytes
 reports/night_audit_ai-eggs_2026-05-30.md        | 161 ++++++++
 reports/night_audit_ai-eggs_2026-05-31.md        | 138 +++++++
 reports/night_audit_ai-eggs_2026-06-01.md        | 139 +++++++
 tools/habr_intelligence.py                       | 471 +++++++++++++++++++++++
 tools/ping_apis.sh                               |  32 ++
 16 files changed, 1369 insertions(+), 40 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

📋 Найденные баги в диффе

- **photo_cascade.py:60** – не-ASCII (ru-RU) комментарии/печать внутри функции `_generate_leonardo`, в том числе print, которые будет выполнять в асинхронном коде с Leonardo-api.  
  **Критичность:** 🟢 Минорно  
  **Исправление:** Локализовать или убрать русскую раскладку внутри ключа Bearer и JSON-телах, а логи заменить на `logging`.

- **photo_cascade.py:84** – `gen.get("generated_images", [])` может вернуть `None`, если end-point прислал: `"generated_images": null` → `None` приходит в генераторах; при касте к `[]` вызов len() не упадёт, но `for img in []` пройдёт мимо.  
  **Критичность:** 🟡 Важно  
  **Исправление:** Не полагаться на значение по умолчанию, а явно проверять:  
  ```python
  raw_imgs = gen.get("generated_images") or []
  urls = [img["url"] for img in raw_imgs if img.get("url")]
  ```

- **photo_cascade.py:168** – ключ API Unsplash идёт прямо в заголовке GET-запроса; потенциально протекает в логи/прокси.  
  **Критичность:** 🟡 Важно  
  **Исправление:** Передавать через переменную, не логировать полные заголовки, а в конфигах использовать `https://` вместо `http://` для `PHOTO_PROXY_US`.

- **photo_cascade.py:206 (функция `get_photo`)** – в параметрах описаны `width`, `height`; но они передаются только в fallback `_placeholder_url()`, а для `_search_unsplash` не используются—возвращаются картинки оригинального размера, что приведёт к битым ссылкам, если запросил 512×512, а Unsplash отдал 4K.  
  **Критичность:** 🟡 Важно  
  **Исправление:** Добавить в `urls [...item["urls"]["raw"] + w=width&h=height]`, либо адаптировать сразу при формировании ответа.

- **photo_cascade.py:200, 205** – переменные `width` и `height` не-typed внутри целочислных аргументов, а в `picsum.photos` юзается в URL без валидатора. Ошибка типа + `width=0` приведёт к HTTP 400.  
  **Критичность:** 🟢 Минорно  
  **Исправление:** Добавить `assert width > 0 and height > 0`, обернуть в `pydantic` или `int` validation.

- **llm_engine.py:239-241** – `_search_duckduckgo` использует `async with httpx.AsyncClient` без явного `keepalive = False`, тем не менее коннект с DuckDuckGo оставляет открытый TCP-просмотр реального IP без прокси, что выводит из кэшей/логов реальный VPS и может заблокировать IP интернет-шлюзом.  
  **Критичность:** 🟡 Важно  
  **Исправление:** Добавить короткий `timeout=8` и `httpx.AsyncClient(proxies=PROXY_US)` если `PROXY_US` задан.

- **llm_engine.py:58-63** – в новом списке `OPENROUTER_MODELS` `"google/gemini-2.0-flash-001"` может выпадать по гео-ограничениям (OpenRouter → Google), но в коде `call_llm` продолжает использоваться: не обрабатывает `Error 403 blocked region`, что приведёт к 3 попыткам и TTL-фейл без fallback.  
  **Критичность:** 🔴 Критично (бот «умрёт» при первом же запросе)  
  **Исправление:** Проверку HTTP-кода 403 (Google geo-block) сделать достаточным основанием для скипа этой модели; либо убрать её из списка и оставить только новые stable.

✅ В остальном заметных багов (dead-code, off-by-one, race) не обнаружено.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-06 |
| ⏰ Время | 02:00:05 → 02:00:52 |
| 📁 Python файлов | 197 |
| 📝 Изменено за день | 16 |
| ⚡ ruff ошибок (E,F,S,B) | 1658 |
| 🔐 Hardcoded секретов | 1 |
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
  Фаза 3: moonshotai/kimi-k2 (cross-model review, OpenRouter)
  
Cross-Model Peer Review: два профессора из разных школ
проверяют код друг друга → максимум найденных багов
```

---

> 🤖 Сгенерировано: `tools/night_audit.sh v2` — Cross-Model Peer Review
