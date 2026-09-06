levitan-common
==============

Общий пакет инфраструктуры Levitan (SSoT) для сравнения 3 вариантов голосового
агента. Содержит весь общий не-agent код: обзвон (Mango), CRM, lead_storage,
campaign_manager, webhook, prompts, config, data-структуры.

Схема репозитория (монорепо, projects/):

    levitan/            — текущий ПРОД-агент (живой на VPS, НЕ трогаем)
    levitan-common/     — общая инфраструктура (этот пакет)
    levitan-livekit/    — вариант 1: LiveKit Agents (DeepSeek+Yandex+Deepgram)
    levitan-gemini/     — вариант 2: Gemini Live (speech-to-speech)
    levitan-retell/     — вариант 3: Retell Conductor (на паузе, нет API-ключа)

Каждый агент-проект — standalone, зависит от `levitan-common` (pip install -e).

## Установка (в каждом агент-проекте)

    pip install -e ../levitan-common

## Запуск обзвона/CRM (эфемерный веб-сервер + dialer)

    python main.py            # FastAPI: webhook + campaign mgr
    python scripts/dialer_bot.py --help

## Структура

    src/levitan/            — core-модули (mango_client, crm_enricher, lead_storage, ...)
    crm/                    — CRM (FastAPI + sqlite: crm.db пересоздаётся из database.py)
    config/                 — настройки агентов/ретелла
    data/                   — runtime-структура (пустые папки; рабочие данные у прода в levitan/)
    scripts/                — dialer, s2t, campaign, снятие лидов и т.д.
    main.py                 — entry point (FastAPI webhook + campaign)
