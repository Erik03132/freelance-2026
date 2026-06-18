# 🌙 Ночной аудит кода — 2026-06-18

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:04  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 206 (проверяем: 3)  
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
ai-eggs/agent/angelochka_core.py:103:89: E501 Line too long (113 > 88)
ai-eggs/agent/angelochka_core.py:108:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:145:89: E501 Line too long (92 > 88)
ai-eggs/agent/angelochka_core.py:153:89: E501 Line too long (130 > 88)
ai-eggs/agent/angelochka_core.py:183:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:223:13: F841 Local variable `y` is assigned to but never used
ai-eggs/agent/angelochka_core.py:270:9: B007 Loop control variable `cat_key` not used within loop body
ai-eggs/agent/angelochka_core.py:349:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:359:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:373:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:419:89: E501 Line too long (90 > 88)
ai-eggs/agent/angelochka_core.py:484:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:496:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:497:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:514:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:515:89: E501 Line too long (89 > 88)
```

🔧 **ruff --fix:** 2 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-18\')

**Критических ошибок ruff (E,F,S,B):** 1778

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 agent-lab/voice_angela_web.py             | 335 ++++++++++++++++++++++++++++++
 ai-eggs                                   |   0
 angel-backend                             |   0
 checkpoints/chp_20260617_230316.md        |  69 ++++++
 data/habr_intelligence_state.json         |   2 +-
 dreams/dream_2026-06-17.md                |  31 +++
 dreams/patterns.md                        |  23 ++
 reports/night_audit_ai-eggs_2026-06-17.md |  70 +++++++
 reports/night_audit_ai-eggs_2026-06-18.md |  79 +++++++
 9 files changed, 608 insertions(+), 1 deletion(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

**agent-lab/voice_angela_web.py:6, 189, брауз.указатели**  
**Критичность:** 🔴 Критично  
**Исправление:** Скрипт явно заточен под macOS (`use macOS say command`), но прод в VPS Linux (см. комментарий «на VPS будет Kore»). В линуксовом контейнере команда `say -v Milena` завершится ошибкой → TTS всегда будет `None`, а PyPI-библиотеки / сторонние сервисы (elevenlabs, silero, coqui, etc.) не установлены. Нужно либо запаковать проверенный Linux-совместимый TTS на контейнер (espeak-ng, coqui), либо в рантайме проверять платформу `sys.platform == "darwin"` или `.startswith("darwin")` и отдавать либо WAV из кеша, либо использовать REST-TTS.

---

**agent-lab/voice_angela_web.py:67–75**  
**Критичность:** 🟡 Важно  
**Исправление:** Функция `load_prices()` кэширует результат глобально. Если во время работы процесса файл `prices.json` изменится (например, обновит менеджер Bitrix), Анжела продолжит выдавать старые цены. Также при одновременном старте множества gunicorn-worker’ов каждый сохранит свой снапшот → можно получить «рассинхронные» цены между репликами. Рекомендуем держать кэш **ограниченным по времени** (`functools.lru_cache(ttl=300)`) либо совсем читать при каждом запросе.

---

**agent-lab/voice_angela_web.py:91–101**  
**Критичность:** 🟡 Важно  
**Исправление:** В POST-запросе не передаётся ни one-time, ни session-id, а prompts у бота содержат историю (`history`) в кодировке *str(history)*. Длина истории клиента ограничена 2500 символами клиентским JS-ом, но нет серверной валидации: злоумышленник может слать `history` размером в мегабайт и либо исчерпать rate-limit OpenRouter, либо тайм-аут FastAPI. Добавьте серверный хард-лимит (например, 4000 символов) перед отправкой в модель и/или откидывайте самые старые строки.

---

**agent-lab/voice_angela_web.py:117, 156**  
**Критичность:** 🟢 Минорно  
**Исправление:** Используется системный `/tmp/va_web.wav`. При одновременных запросах нескольких пользователей они будут перезаписывать один файл, и случится race-condition (файл считается другим процессом). Замените на `tempfile.NamedTemporaryFile(delete=False, suffix=".wav")`.

---

**agent-lab/voice_angela_web.py:143**  
**Критичность:** 🟡 Важно  
**Исправление:** Shell-команды (`say`, `ffmpeg`) вызываются без проверки их присутствия в `$PATH`. Если сервер разворачается в контейнере без `ffmpeg`, воспроизведение не будет происходить, лог содержит только `⚠ TTS: FileNotFoundError`. В `Dockerfile` нужно явно обеспечить наличие `apt install -y ffmpeg`, а также проверять статус `subprocess.run(..., check=True)` и водить дружественный sentry-лог.

---

**agent-lab/voice_angela_web.py:43**  
**Критичность:** 🟢 Минорно  
**Исправление:** Если путь `prices.json` будет обозначен через симлинк или каталог окажется недоступен (`os.access(pp, os.R_OK) == False`), `load_prices()` просто вернёт пустую строку без ведома в логах. Пользователь получит «цены неизвестны», но девопсы не поймут, почему. Добавьте единый `logger.error()` при `pp.exists() == False` или `PermissionError`.

---

**agent-lab/voice_angela_web.py:191**  
**Критичность:** 🔴 Критично  
**Исправление:** Статический фронт JavaScript хардкодит `audio.play()` в браузере. Если ресурс не имеет право на автоматическое воспроизведение (chrome + autoplay-policy «AudioContext was not allowed to start»), воспроизведение остановится молча, и пользователь не поймёт, что ответ проговорен. Добавьте `audioEl.play().catch(() => console.warn('Autoplay blocked'));` чтобы не ломать весь fetch-цикл.

---

**agent-lab/voice_angela_web.py:119, 128**  
**Критичность:** 🟢 Минорно  
**Исправление:** Пакет `base64` импортируется внутри `generate_tts` на каждый вызов TTS из-за `import base64`. Добавляет 10-15 мс overhead, особенно при частых repeated requests. Вынесите `import base64` на уровень модуля.

---

**agent-lab/voice_angela_web.py:89**  
**Критичность:** 🔴 Критично  
**Исправление:** Литерал `"..." + '\n'.join(lines)` в `prompt` полностью открыт DOM-based XSS через `history`, если злоумышленник постит JavaScript-трепет в поле client-side. Хотя в `load_prices()` есть `html.escape`, сам `history` не эскейпится. Вставьте `html.escape(history)`.

---

**agent-lab/voice_angela_web.py:165–167**  
**Критичность:** 🟡 Важно  
**Исправление:** В FastAPI `@app.post("/ask")` синхронная функция выполняется `requests.post(...)` (блокирующая). При 10+ одновременных вызовах серверные «вики-воркеры» начнут тащить тайм-ауты. Оборачивайте external-запрос в `httpx.AsyncClient()` (асинхронно) либо пока переходим на поток-воркеры из-за блокированного GIL.

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-18 |
| ⏰ Время | 02:00:04 → 02:01:01 |
| 📁 Python файлов | 206 |
| 📝 Изменено за день | 9 |
| ⚡ ruff ошибок (E,F,S,B) | 1778 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ✅ |
| 🔴 Критичных (Claude) | 3 |
| 🟡 Важных (Claude) | 4 |
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
