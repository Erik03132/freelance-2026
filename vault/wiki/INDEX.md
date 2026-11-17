---
type: wiki
tags: [wiki, index, knowledge-base]
status: done
updated: 2026-11-17
sources: [06-Library/_catalog.md]
---

# Wiki — скомпилированный слой знаний

Назначение: один экран на тему вместо перечитывания 3–4 диджестов. Собрано из `vault/06-Library/**` на 2026-11-17. Ничего не добавлено извне.

## Как читать

1. Этот файл → нужная страница в `entities/`.
2. Сырьё (digest.md внутри папки темы в `06-Library/`) — только если в вики нет ответа или нужна дословная цитата.
3. Где источники расходятся — `contradictions.md`. Карта «страница → файлы» — `sources.md`.

## Страницы

| Страница | Что покрывает | Источник (дата) |
|---|---|---|
| [geo-chatgpt-labrador](entities/geo-chatgpt-labrador.md) | GEO под ChatGPT: собственный робот, карточка 200 символов | geo-chatgpt-2026 (2026-08-20) |
| [geo-yandex-alisa](entities/geo-yandex-alisa.md) | GEO под Алису AI: привязка к топ-10 Яндекса | geo-yandex-alisa-2026 (2026-08-20) |
| [llms-txt](entities/llms-txt.md) | llms.txt: миф о видимости в ИИ, реальный кейс IDE-агентов | два диджеста Habr (2026-08-09/10) |
| [technical-seo-scale](entities/technical-seo-scale.md) | Технический SEO на миллионах страниц: Python, sitemap-мониторинг | seo-ecommerce-automation-2026 (2026-08-20) |
| [elevenlabs-realtime](entities/elevenlabs-realtime.md) | Speech-to-Speech ElevenLabs v1 Mini/Max, применимость к Levitan/AVM | eleven-realtime-2026 (2026-10-25) |
| [voice-stack-choice](entities/voice-stack-choice.md) | Vapi vs Mango + LiveKit + pipecat: когда что | tools/vapi-voice-ai (2026-09-23) |
| [cua-spaces](entities/cua-spaces.md) | Cua Spaces: изоляция агентов на своём железе, OpenCode как харнесс | cua-spaces-sdk-2026 (2026-10-25) |
| [expert-council](entities/expert-council.md) | Совет 6 экспертов, Chief Summary, пайплайн Sinergy | es-n-multiagent-gateway (2026-08-23), sinergy-expert-council (2026-08-23) |
| [hermes-profiles](entities/hermes-profiles.md) | Hermes Profiles: SOUL на агента, delegate_task, кеш скиллов | es-n-multiagent-gateway, skill-library-v2 (2026-08-23) |
| [skill-library-v2](entities/skill-library-v2.md) | Федеративная библиотека скиллов по тегам: план и его состояние | skill-library-v2 (2026-08-23) |
| [oss-weekly-2026-10](entities/oss-weekly-2026-10.md) | mattpocock/skills, hyperframes, claude-mem, openrig — вердикты | gh-weekly-2026-10-20 (2026-10-20) |
| [mustay-response-standard](entities/mustay-response-standard.md) | Batrak v3: HOOK-MATCH-PROOF, антипаттерны откликов | mustay-response-patterns (2026-08-23) |
| [notebooklm-mcp](entities/notebooklm-mcp.md) | Программный доступ к NotebookLM/Gemini Notebook через MCP | два диджеста (2026-08-09) |
| [agentic-ai-guide](entities/agentic-ai-guide.md) | Теория агентов: ReAct, типы памяти, мультиагентность, eval | books/nblm-agentic-ai-guide (2026-08-09) |
| [voice-analytics-bss](entities/voice-analytics-bss.md) | Речевая аналитика как автономный агент: RAG-оценка звонков | books/20260813_bss (2026-08-15) |

## Чего здесь нет

- Практики RAG-пайплайна `kb-prep`, Honcho, Firecrawl — в `06-Library` таких материалов нет (Honcho и Firecrawl не упоминаются вовсе, `kb-prep` тоже).
- Полные тексты статей и книг (`source.md`, 5–10 тыс. строк) — сюда не переносились.

## Обновление

Страница пишется/правится вручную по мере появления новых диджестов. Автогенерации и LLM на рантайме нет (HMS-1).
