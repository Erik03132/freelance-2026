---
type: wiki
tags: [voice-agents, realtime, elevenlabs, speech-to-speech, levitan, avm, latency]
status: done
updated: 2026-11-17
sources: [06-Library/eleven-realtime-2026/digest.md]
---

# ElevenLabs Realtime (Speech-to-Speech v1)

Источник: `06-Library/eleven-realtime-2026/digest.md` (2026-10-25), верифицировано по elevenlabs.io/blog/realtime, changelog 19.10.2026, the-decoder 20.10.2026, benchmarks.coval.ai.

## Что это

Класс Speech-to-Speech: STT + VAD/turn-taking + LLM + TTS в одном входе и одной WebSocket-конфигурации. API OpenAI-совместимый: миграция для тех, кто уже на OpenAI Realtime, — смена endpoint и имени модели. Паттерн: end-to-end STS становится новой единицей роутинга голосовых агентов вместо ручной сборки STT→LLM→TTS.

## Две версии

| | v1 Mini | v1 Max |
|---|---|---|
| Big Bench Audio (1000 вопросов, рассуждение по голосу) | 75.9% | 98.8% |
| TTFA (время до первого аудио) | 620 ms | 570 ms |
| Назначение | ассистенты, дешёвые диалоги | сложные задачи, multi-step tool calls |
| Ограничения | default, низкая цена | token limit ≥1024 или без лимита; в таблице помечено «NOT в ZRM/HIPAA» |

Ключевое: Mini не «так же точна» — разница 23 п.п. В дропе они подавались как пара равных. Обе версии voice-only, для текстовых задач не годятся.

## Независимая проверка

Artificial Analysis прогнала три бенчмарка: Big Bench Audio (рассуждение), Full-Duplex-Bench (перебивания, «угу» — 95.8%), Speech Agent Arena (Elo, task success 87.1%). Coval по отдельным моделям ElevenLabs: Scribe v2 Realtime — 119 ms TTFS. Языков 90+, голосов 17k+. Цена — за минуту плюс токены (Max дороже Mini); независимой цифры нет.

## Применимость к Levitan/AVM

Плюс: turn-taking (перебивания, «угу») — наша боль, лид-тишина 5 с против обрезанного приветствия. Одна обученная модель снимает этот класс ошибок абстрактно: VAD, STT и turn-логика внутри.

Против миграции сейчас:

1. Внутренний LLM закрыт → теряем роутинг OmniRoute, кастомный русский промпт-стек, контроль цены.
2. Оплата ElevenLabs из РФ картами нерешаема без плательщика-посредника.
3. 152-ФЗ: передача аудио Mango-звонков в US-облако = ПД собеседников без согласия. Вероятное «не для обзвона», нужен юр-вывод.
4. Наш текущий TTFA уже приличный: выигрыш надо мерить, а не брать на веру.

## Статус

ELV-1 (бенчмарк Mini против нашего стека на 10 русских репликах) — после решения оплаты и 152-ФЗ. ELV-2 (ElevenAgents как альтернатива Retell для MVP) — низкий приоритет. ELV-3 — урок про категорию «end-to-end STS» для ADR AVM.

## Оговорка

Пункт про ZRM/HIPAA в источнике противоречит сам себе (таблица относит ограничение к Max, список умолчаний — к Mini). См. `contradictions.md`, п.3.
