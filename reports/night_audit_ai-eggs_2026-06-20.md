# 🌙 Ночной аудит кода — 2026-06-20

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 207 (проверяем: 2)  
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
ai-eggs/agent/angela_outbound.py:45:89: E501 Line too long (95 > 88)
ai-eggs/agent/angela_outbound.py:50:89: E501 Line too long (99 > 88)
ai-eggs/agent/angela_outbound.py:84:89: E501 Line too long (98 > 88)
ai-eggs/agent/angela_outbound.py:139:5: F841 Local variable `count` is assigned to but never used
ai-eggs/agent/angela_outbound.py:189:89: E501 Line too long (91 > 88)
ai-eggs/agent/angela_outbound.py:193:89: E501 Line too long (122 > 88)
ai-eggs/agent/angela_outbound.py:203:17: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/angela_outbound.py:204:21: S607 Starting a process with a partial executable path
ai-eggs/agent/angela_outbound.py:205:89: E501 Line too long (110 > 88)
ai-eggs/agent/angela_outbound.py:258:89: E501 Line too long (103 > 88)
ai-eggs/agent/angela_outbound.py:267:89: E501 Line too long (94 > 88)
ai-eggs/agent/angela_outbound.py:285:89: E501 Line too long (106 > 88)
ai-eggs/agent/angela_outbound.py:335:89: E501 Line too long (120 > 88)
ai-eggs/agent/angela_outbound.py:341:89: E501 Line too long (92 > 88)
ai-eggs/agent/angela_outbound.py:345:5: F841 Local variable `p` is assigned to but never used
ai-eggs/agent/angela_outbound.py:379:89: E501 Line too long (97 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-20\')

**Критических ошибок ruff (E,F,S,B):** 1800

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 ai-eggs                                   |   0
 angel-backend                             |   0
 checkpoints/chp_20260618_230001.md        |  25 ++++
 chp.md                                    | 110 ++++++++-------
 dreams/dream_2026-06-18.md                |  13 ++
 dreams/patterns.md                        |   7 +
 reports/night_audit_ai-eggs_2026-06-18.md | 126 +++++++++++++++++
 reports/night_audit_ai-eggs_2026-06-19.md | 199 +++++++++++++++++++++++++++
 tools/habr_intelligence.py                |   2 +-
 10 files changed, 563 insertions(+), 139 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

- **agent-lab/voice_angela_web.py:113** — при любой ошибке (нет ключа, 500-я от OpenRouter, тайм-аут) возвращается захардкоженное `"Извините, повторите, пожалуйста."`.  
  **Критичность:** 🟡 Важно  
  **Исправление:** разделяй открытые ошибки (`LLM unavailable`) и полезный fallback-сообщение; логируй полный текст исключения.

- **agent-lab/voice_angela_web.py:118-152** — `subprocess.run` вызывается синхронно и блокирует event-loop FastAPI; при 25-секундном тайм-ауте все падают под нагрузкой.  
  **Критичность:** 🔴 Критично  
  **Исправление:** переписать на `asyncio.create_subprocess_exec`, либо вынести TTS в background-worker/queue.

- **agent-lab/voice_angela_web.py:122,47-53** — на не-Mac-системах команды `say` и `ffmpeg` отсутствуют. Код упадёт с `FileNotFoundError`.  
  **Критичность:** 🔴 Критично  
  **Исправление:** автоматически определять платформу; если не macOS, поднимать альтернативный speech-API (`pyttsx3`, `edge-tts`, etc.).

- **agent-lab/voice_angela_web.py:53-58** — кеш живёт в памяти (`_cache`) и накапливает WAV-base64 без ограничения объёмов → OOM при долгом uptime.  
  **Критичность:** 🔴 Критично  
  **Исправление:** добавить TTL (`time.time() - ts > N`) и/или LRU-ограничение кол-ва записей (например, через `functools.lru_cache` или внешний `CacheDict`).

- **agent-lab/voice_angela_web.py:42** — `.env` пытается загрузить из `"ai-eggs/.env"`. Если директория mount-ится через Docker или переименуется, `load_dotenv` вернёт пустое значение и `os.getenv("OPENROUTER_API_KEY")` даст `""`, но ошибку не выкинет скрипт.  
  **Критичность:** 🟡 Важно  
  **Исправление:** после загрузки `.env` добавить проверку `if not OPENROUTER_KEY: raise RuntimeError("OPENROUTER_API_KEY not set")`.

- **agent-lab/voice_angela_web.py:75-78** — путь к файлу цен `_PRICE_CTX_FILE` жёстко зашит в `<project>/prices/prices.txt` без проверки существования; при его отсутствии `load_prices` вернёт `""`, но никак не сигнализирует оператору.  
  **Критичность:** 🟢 Минорно  
  **Исправление:** добавить `Path(file).expanduser().resolve().exists()` и, при отсутствии, логировать предупреждение (`logging.warning`).

- **agent-lab/voice_angela_web.py:141, 144** — командная строка `ffmpeg ... -y`. Путь к выходному WAV захардкожен в `/tmp/va_web.wav`; одновременные запросы будут перезаписывать один и тот же файл — race condition.  
  **Критичность:** 🔴 Критично  
  **Исправление:** генерировать уникальный tempfile (`tmp = tempfile.NamedTemporaryFile(delete=False)`) и удалять после чтения.

- **agent-lab/voice_angela_web.py:90-92** — правило `Клиент просит → ПЕРЕКЛЮЧАЮ_ОПЕРАТОРА` выдаёт ответ **внутри блока TTS**; реальный оператор не вызывается (callback, webhook, или transfer не реализованы).  
  **Критичность:** 🔴 Критично  
  **Исправление:** при получении триггер-фразы асинхронно вызывать Bitrix24 API для перевода на живого менеджера и сразу завершать сессию или отправлять нужный `transition_id`.

- **agent-lab/voice_angela_web.py:35** — закрытие прокси-переменных должно происходить ДО первого импорта `requests`/`aiohttp`, иначе уже созданные Session применяют старый proxy.  
  **Критичность:** 🟡 Важно  
  **Исправление:** вынести `LOAD_DOTENV` и затирание env-proxy выше любого `import requests`.

- **agent-lab/voice_angela_web.py (HTML)** — поле `<form id="chat-form" action="/ask-form"` оставляет fallback форму GET-ом в `/ask-form`, но метод спёрт коммитом. Пользователь получит 404, если JS отключён.  
  **Критичность:** 🟢 Минорно  
  **Исправление:** заменить `action="/ask"` и `method="POST"` или восстановить соответствующий endpoint.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-20 |
| ⏰ Время | 02:00:05 → 02:00:49 |
| 📁 Python файлов | 207 |
| 📝 Изменено за день | 10 |
| ⚡ ruff ошибок (E,F,S,B) | 1800 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 5 |
| 🟡 Важных (Claude) | 3 |
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
