# Levitan — сравнение 3 вариантов голосового агента

Проект разнесён на **3 standalone-подпроекта** (общая инфраструктура — в
`levitan-common`) для последующего честного сравнения результатов по завершении
каждого. Текущий прод-агент в `levitan/` **не трогается**.

## Структура

| Подпроект | Архитектура | Статус |
|-----------|-------------|--------|
| `levitan-livekit` | LiveKit Agents: Deepgram STT → DeepSeek LLM → Yandex TTS | ✅ работает (прод-стек) |
| `levitan-gemini` | Gemini Live (speech-to-speech): одна модель, аудио↔аудио | 🟡 scaffold + smoke Verified |
| `levitan-retell` | Retell Conductor (hosted, диалог через SIP URI) | ⏸ пауза (нет API-ключа) |
| `levitan-common` | Общий core SSoT (src/levitan, CRM, mango, config, data, scripts) | ✅ |

Каждый агент-проект зависит от `levitan-common` (`pip install -e ../levitan-common`).

## Сравниваемые метрики (заполнять при каждом прогоне)

| Метрика | livekit (baseline) | gemini | retell |
|---------|--------------------|--------|--------|
| turn1 response latency | ~6.7s | ~2.5s (smoke) / цели <2s в потоке | ? |
| Удержание воронки (MIN_QTY 50) | высокое (fast-path) | ? | ? |
| Естественность диалога | средний (каскад) | ожидается высокий (S2S) | ? |
| Стоимость / мин | ? | ~$0.005 in / $0.018 out | $0.07–0.31 |
| Завершение лида (save_lead → Bitrix) | ✅ | в scaffold | ✅ |
| Инфраструктура | VPS + LiveKit SIP (есть) | VPS + LiveKit SIP (тот же) | Retell SIP URI |

## Как гонять сравнение
1. Для каждого варианта: контрольный звонок по одному сценарию (п.4 «может 40/50/70»,
   MIN_QTY <50, barge-in, «чем можем быть полезны»).
2. Записывать в этот файл: latency (из логов turn1), исход диалога, лид в Bitrix.
3. После прогона всех трёх — выбрать победителя и перевести в прод (`levitan/`).

## Smмoke-тест Gemini Live (Verified, 31.08.2026)
- Ключ `GEMINI_API_KEY` (free) работает, модель `gemini-3.1-flash-live-preview` доступна.
- Аудио-вход (речь) → аудио-выход на русском работает.
- Латентность ~2.5s после конца ввода (livekit-каскад ~6.7s turn1) — выигрыш подтверждён.
- Засада: акустическое эхо при SIP (carrier-отражение → VAD прерывает модель) — решить
  до продакшена (echo cancellation).
