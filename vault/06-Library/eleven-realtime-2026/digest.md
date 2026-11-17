---
type: article-digest
tags: [voice-agents, speech-to-speech, elevenlabs, realtime, latency, levitan, avm, буферизация-стека]
status: done
updated: 2026-10-25
---

# Eleven Realtime — Speech-to-Speech одного агентом (2026-10-20)
Источник: дроп ТГ 25.10.2026 → верифицировано: [[source]] (elevenlabs.io/blog/realtime, docs changelog 19.10.2026, the-decoder 20.10.2026, benchmarks.coval.ai). Связано: ACTIVE_TASKS секция 🎙️ ELV.

## Главный вывод
Класс Speech-to-Speech моделей: STT + VAD/turn-taking + LLM + TTS = **один вход**, одна WebSocket-конфигурация. OpenAI-совместимый Realtime API — миграция для тех, кто уже на OpenAI Realtime = смена endpoint + model name. Паттерн: **end-to-end STS модель становится новой единицей роутинга голосовых агентов** (вместо ручной сборки стека STT→LLM→TTS).

## Две версии (дроп совпадает с фактами)
| | v1 Mini | v1 Max |
|---|---|---|
| Big Bench Audio (рассуждение по голосу, 1000 вопросов) | 75.9% | 98.8% |
| TTFA (время до первого аудио) | 620 ms | 570 ms |
| Для чего | ассистенты, дешёвые диалоги | сложные задачи, multi-step tool calls |
| Режимы | default, низкая цена | token limit ≥1024 или без лимита; NOT в ZRM/HIPAA |

**Умолчания дропа (важно):**
1. Mini НЕ «так же точна» — 75.9% vs 98.8% (−23 п.п.). Дроп подавал как пару равных.
2. Mini недоступна в Zero Retention Mode / HIPAA.
3. Обе — voice-only, для text-only не годятся.
4. Русский: 90+ языков обе. 17k+ голосов. Pricing: за минуту + токены (Max > Mini; независимой цифры нет).

## Независимая верификация (не self-report)
Artificial Analysis независимо прогнала 3 бенчмарка: Big Bench Audio (рассуждение), Full-Duplex-Bench (диалоговая динамика: перебивания, «угу» — 95.8%), Speech Agent Arena (Elo, task success 87.1%). Coval (бенчмарк STT/TTS отдельных моделей ElevenLabs): Scribe v2 Realtime 119 ms TTFS / Flash v2.5 — для сравнения с классическим стеком.

## Маппинг на наш стек (Levitan/AVM)
- **Что сильного:** turn-taking «угу»/перебивания — наш боль (лид-тишина 5с против обрезанного приветствия). Одна модель предполагает и сводит этот класс ошибок абстрактно — VAD, STT и turn-логика в одном обученном входе.
- **Что против миграции сейчас:**
  1. внутренний LLM закрыт → теряем OmniRoute-роутинг, кастомный русский промпт-стек, контроль цены;
  2. оплата ElevenLabs из РФ (карты) — нерешаема без плательщика-посредника;
  3. **152-ФЗ:** передача аудио Mango-звонков в US-облако = ПД собеседников без согласия → вероятный «не для обзвона», нужен юр-вывод Фемиды;
  4. наш текущий TTFA уже приличный — выигрыш мерить, не брать на веру.

## Task-и
ACTIVE_TASKS: ELV-1 (бенчмарк 11RT Mini vs наш стек, 10 русских реплик — ПОСЛЕ решения оплаты и 152-ФЗ), ELV-2 (ElevenAgents как Retell-альтернатива MVP, низкий приоритет), ELV-3 (урок для следующего ADR AVM: категория «паттерн end-to-end STS»).
