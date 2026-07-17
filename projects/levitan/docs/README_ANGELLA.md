# Анжелла — голосовой агент по бройлерам (Левитан × ai-eggs)

## Архитектура (turbo-FAQ, как Айка, но с большим кэшем)

```
Клиент → Mango callback → baresip (8kHz PCM)
  → STT (faster-whisper) → ТЕКСТ
  → FAQ-КЭШ (fuzzy match, 202 триггера, порог 0.72)
        → HIT: мгновенный TTS (Яндекс SpeechKit, голос alena) — БЕЗ LLM (~300-500ms)
        → MISS: LLM (OpenRouter → Yandex fallback → локальный шаблон)
  → TTS (Яндекс primary, edge-tts fallback) → WAV 8kHz
  → baresip проигрывает клиенту
```

**Ключевая фишка:** ~90% типовых вопросов ловятся FAQ-кэшем → ответ мгновенный,
без задержки на LLM (которая даёт +2-4с). Это даёт «realtime-ощущение» даже без
Realtime API.

## Файлы

| Файл | Назначение |
|------|-----------|
| `deploy/levitan_faq_agent.py` | Основной движок (turn-based + FAQ-кэш + TTS/STT + Mango) |
| `deploy/levitan_webhook.py` | HTTP-сервер (порт 8087), принимает Mango-события → `events.jsonl` |
| `deploy/levitan_greeting.py` | Генерация приветствия в `/tmp/levitan_greeting_lead.wav` |
| `docs/ANGELLA_BROILERS_FAQ_CACHE.json` | 202 триггера FAQ (бройлеры, цены, логистика, возражения) |
| `docs/ANGELLA_BROILERS_KB.md` | База знаний |
| `deploy/deploy_angel.sh` | Деплой на VPS (systemd + baresip + rsync) |

## Запуск (локально / тест)

```bash
cd projects/levitan && source .venv/bin/activate
# 1. Сгенерировать приветствие
python3 deploy/levitan_greeting.py
# 2. Ручной тест-звонок
python3 deploy/levitan_faq_agent.py 79859234644
# 3. Или watch-mode (слушает events.jsonl от webhook)
python3 deploy/levitan_faq_agent.py
```

## Деплой на VPS

```bash
bash deploy/deploy_angel.sh
# Логи:
journalctl -u levitan-angel -f
journalctl -u levitan-webhook -f
```

## Статус интеграций

- ✅ **Яндекс SpeechKit TTS** — работает (`alena`, 8kHz PCM)
- ✅ **FAQ-кэш** — 202 триггера, 100% HIT на типовых вопросах
- ✅ **Mango callback + webhook** — готово (требует VPS + baresip)
- ⚠️ **LLM (OpenRouter)** — ключ заблокирован (403). Используется локальный
  шаблонный fallback (`_local_fallback` в `levitan_faq_agent.py`)
- ❌ **Яндекс Realtime API** — endpoint 404/403, недоступен (см. ADR-001)

## Восстановление LLM (когда появится ключ)

В `.env` прописать валидный `OPENROUTER_API_KEY` или `YC_API_KEY` с доступом
к foundation-моделям. Код уже умеет ротировать: OpenRouter → Yandex → local.
