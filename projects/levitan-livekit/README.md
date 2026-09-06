levitan-livekit
===============

Вариант 1: **LiveKit Agents** — классический каскад
`Deepgram STT → DeepSeek LLM (OpenAI-совместимый) → Yandex TTS` для голосового
агента Levitan (Азовский инкубатор). Это текущий продакшен-стек.

Сравниваемые метрики (заполняются при прогоне):
- turn1 response latency (базовый: ~6.7s)
- стабильность диалога, удержание воронки (MIN_QTY 50, Ross-308 от 75₽)
- стоимость звонка

## Установка

    python3.11 -m venv .venv
    .venv/bin/pip install -r requirements.txt   # подтянет levitan-common из ../levitan-common

## Запуск (агент-воркер регистрируется в LiveKit Cloud)

    source .venv/bin/activate
    python agent/main.py

Env обязателен: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`,
`LIVEKIT_SIP_URI`, `DEEPSEEK_API_KEY`, `YANDEX_TTS_FOLDER_ID`, `YANDEX_TTS_API_KEY`,
`DEEPGRAM_API_KEY`, `MANGO_VPBX_API_KEY`, `MANGO_VPBX_API_SALT`.

## Тесты

    .venv/bin/python -m pytest tests/ -v   # funnel + text_humanizer + stability_probe

## Структура агента

    agent/levitan_agent.py      — голосовой агент (AgentSession, воронка, save_lead/faq_lookup)
    agent/funnel.py             — воронка: перехват типовых ответов (fast-path), MIN_QTY, числа
    agent/funnel_config.json    — настройки воронки (минимум, город, породы)
    agent/text_humanizer.py     — живость TTS: вздох (breath_pcm), авто-паузы, темп
    agent/stability_probe.py    — probe стабильности TTS/LLM
