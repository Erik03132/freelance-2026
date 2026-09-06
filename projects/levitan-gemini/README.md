levitan-gemini
==============

Вариант 2: **Gemini Live (speech-to-speech)** — одна модель принимает и отдаёт аудио
напрямую через LiveKit `AgentSession` + `RealtimeModel`
(`gemini-3.1-flash-live-preview`). НЕТ каскада STT->LLM->TTS, нет VAD (серверный
turn-detection), нет кастомной воронки-перехвата — модель сама ведёт диалог.

## Статус (итерация 31.08.2026)
- **Verified (smoke-тест, без прода):** ключ `GEMINI_API_KEY` работает, модель
  доступна, аудио-вход→аудио-выход на русском работает; латентность после ввода
  ≈2.5s против turn1 6.7s у livekit-стека. См. `chp.md` levitan.
- **Каркас (этот код):** `agent/gemini_agent.py` собран, но НЕ деплоен и НЕ
  протестирован звонком. Бизнес-промпт/инструменты те же, что в levitan-livekit.

## Сравниваемые метрики
- turn1 response latency (цель: <2s в потоке)
- удержание воронки (MIN_QTY 50, Ross-308 от 75₽)
- стоимость звонка (Gemini ~$0.005/мин in, ~$0.018/мин out — дёшево)
- качество диалога / естественность (speech-to-speech vs каскад)

## Установка

    python3.11 -m venv .venv
    .venv/bin/pip install -r requirements.txt   # подтянет levitan-common + google-genai

## Запуск

    source .venv/bin/activate
    python agent/gemini_agent.py

Env: `GEMINI_API_KEY`, `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`,
`LIVEKIT_SIP_URI`, `MANGO_VPBX_API_KEY`, `MANGO_VPBX_API_SALT`, `BITRIX_WEBHOOK_URL`.
Доп. тюнинг: `GEMINI_MODEL`, `GEMINI_VOICE` (Puck и др.), `GEMINI_LANGUAGE` (ru-RU).

## Известные ограничения/шаги
1. Echo cancellation при SIP-деплое (carrier отражает outbound аудио в вход → VAD
   прерывает модель) — решить до звонка.
2. Инструменты live: `manual_function_calls=False`, auto tool reply — нет ручного
   `end_call`; звонок завершается финальной фразой.
3. Модель `gemini-3.1-flash-live-preview` имеет limited mid-session update — при
   смене инструментов/инструкций пересоздаётся сессия.

## Структура

    agent/gemini_agent.py     — голосовой агент (AgentSession + RealtimeModel)
    agent/main.py             — (запуск через gemini_agent.main)
