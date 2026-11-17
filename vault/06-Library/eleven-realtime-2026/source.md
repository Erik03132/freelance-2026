---
type: article-digest
tags: [voice-agents, elevenlabs, source]
status: done
updated: 2026-10-25
---

# Source: ElevenLabs Eleven Realtime (верификация 25-26.10.2026)

## Первоисточники

1. **ElevenLabs blog — "Introducing Eleven Realtime"** (2026-10-20)
   https://elevenlabs.io/blog/realtime
   Key: STS класс моделей; v1 Max 98.8% Big Bench Audio / TTFA 570ms; v1 Mini 75.9% / 620ms; 90+ языков; 17k+ голосов; Artificial Analysis independent eval по 3 бенчмаркам; запуск в ElevenAgents + OpenAI-совместимый Realtime API.
   Цитата: «Big Bench Audio asks 1,000 reasoning questions by voice and scores the spoken answer. Realtime v1 Max answered 98.8% questions correctly, and v1 Mini answered 75.9%»
   Цитата: «V1 Max starts speaking in 0.57 seconds on average, and v1 Mini in 0.62 seconds»

2. **ElevenLabs Docs — Changelog 19.10.2026**
   https://elevenlabs.io/docs/changelog/2026/10/19.md
   Key: rollout постепенно по workspaces; model names `eleven_realtime_v1_mini` / `eleven_realtime_v1_max`; «rolling gradually across workspaces».
   Цитата: «Eleven Realtime is a new family of models for ElevenAgents voice agents, rolling out gradually across workspaces»
   Цитата: «You pick one model, and ElevenLabs handles the LLM, Speech to Text and Text to Speech settings behind it»

3. **ElevenLabs Docs — Realtime models**
   https://elevenlabs.io/docs/eleven-agents/customization/realtime-models
   Key: Max для multi-step tool calls; token limit ≥1024 для Max; Mini недоступна в ZRM/HIPAA; voice-only; OpenAI Realtime API-compatible (events + WebSocket transport не меняются).
   Цитата: «Token limit for Max: Eleven Realtime v1 Max needs a token limit of 1,024 or more, or no limit»
   Цитата: «Mini isn't available under either [ZRM or HIPAA]»
   Цитата: «If you've already built on OpenAI's Realtime API, you don't need to rewrite your client. The events and the WebSocket transport are the same»

4. **The Decoder — независимый разбор (20.10.2026)**, Matthias Bastian
   https://the-decoder.com/elevenlabs-releases-two-new-speech-to-speech-models-designed-for-real-time-ai-conversations
   Key: подтверждает цифры + pricing «per minute plus token costs, v1 Max costing more than v1 Mini»; Artificial Analysis Speech-to-Speech leaderboard: Max в «top left corner» (accuracy × latency).
   Цитата: «Pricing is per minute plus token costs, with v1 Max costing more than v1 Mini»

5. **ElevenLabs X-анонс (20.10.2026)**
   https://x.com/ElevenLabs/status/2112550784835715229
   Цитата: «No model on the Artificial Analysis leaderboard is both faster and more accurate»

6. **Coval benchmarks — независимый замер (dated 2026-10-21)**
   https://benchmarks.coval.ai/providers/elevenlabs
   Key: отдельно взятые STS-подмодели ElevenLabs: Scribe v2 Realtime 119 ms TTFS / 4.3% WER; Flash v2.5 ~194 ms TTFA / 1.9% WER — совокупный STACK-толлик для сравнения STS «all-in-one» с классической цепочкой.
   Цитата: «STT: Scribe v2 Realtime at 119 ms TTFS, with 4.3% WER. TTS: Flash v2.5 at 194 ms TTFA»

## Контекст-фты (не в дропе)

- Full-Duplex-Bench 95.8%; Speech Agent Arena task success 87.1%.
- «v1 Mini входит в «most use cases», Max — «reasons before it responds».
- Русский: не помечен особо; 90+ языков общий зонт.

## Скай-стата (локально связанное)

- ACTIVE_TASKS 🎙️ ELV (ELV-1/2/3); наш стек: custom/retell-conductor, levitan-voice-agent (livekit-sip, OmniRoute).
- Проверено 26.10.2026 по web (websearch). Статус: «проверено (src)», принятие миграции — нет.
