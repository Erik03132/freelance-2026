---
type: wiki
tags: [wiki, provenance]
status: done
updated: 2026-11-17
sources: [06-Library/_catalog.md]
---

# Карта источников

Пути относительны `vault/`. Дата — `updated` диджеста (или `read`, если `updated` не задан). Все файлы прочитаны 2026-11-17, изменены только в `vault/wiki/` и `vault/CLAUDE.md`.

| Страница вики | Файлы-источники | Дата источника |
|---|---|---|
| entities/geo-chatgpt-labrador.md | `06-Library/geo-chatgpt-2026/digest.md`, `06-Library/geo-chatgpt-2026/source.md` | 2026-08-20 |
| entities/geo-yandex-alisa.md | `06-Library/geo-yandex-alisa-2026/digest.md` | 2026-08-20 |
| entities/llms-txt.md | `06-Library/books/llms-txt-habr/digest.md`, `06-Library/books/20260809_llmstxt-_-----------__x2f_-/digest.md` | 2026-08-10 / 2026-08-15 |
| entities/technical-seo-scale.md | `06-Library/seo-ecommerce-automation-2026/digest.md` | 2026-08-20 |
| entities/elevenlabs-realtime.md | `06-Library/eleven-realtime-2026/digest.md` | 2026-10-25 |
| entities/voice-stack-choice.md | `06-Library/tools/vapi-voice-ai/digest.md` | 2026-09-23 |
| entities/cua-spaces.md | `06-Library/cua-spaces-sdk-2026/digest.md` | 2026-10-25 |
| entities/expert-council.md | `06-Library/es-n-multiagent-gateway/digest.md`, `06-Library/sinergy-expert-council/digest.md` | 2026-08-23 |
| entities/hermes-profiles.md | `06-Library/es-n-multiagent-gateway/digest.md`, `06-Library/skill-library-v2/digest.md` | 2026-08-23 |
| entities/skill-library-v2.md | `06-Library/skill-library-v2/digest.md`, `06-Library/skills-catalog/catalog.json` | 2026-08-23 / 2026-11-16 |
| entities/oss-weekly-2026-10.md | `06-Library/gh-weekly-2026-10-20/digest.md` | 2026-10-20 |
| entities/mustay-response-standard.md | `06-Library/mustay-response-patterns/digest.md` | 2026-08-23 |
| entities/notebooklm-mcp.md | `06-Library/books/20260808_notebooklm-mcp-_-pypi/digest.md`, `06-Library/books/20260808_github---jacob-bd_gemini-notebook-mcp-cli_-programmatic-access-to-gemini-notebook---via-command-line-interface-cli_-mo/digest.md` | 2026-08-09 |
| entities/agentic-ai-guide.md | `06-Library/books/nblm-agentic-ai-guide/digest.md` | 2026-08-09 |
| entities/voice-analytics-bss.md | `06-Library/books/20260813_bss--_-_-----_----215/digest.md` | 2026-08-15 |

## Материалы, не ставшие страницами

| Файл | Почему |
|---|---|
| `06-Library/books/20260808_about-python_trade_-_-pythonorg/digest.md` | Общая статья про Python: нет факта, которого нет в голове. Держать страницу = вода. |
| `06-Library/books/20260813_bss--_-_-----_----215/digest.md` | Стал страницей `voice-analytics-bss` (речевая аналитика, RAG-оценка звонков). |
| `06-Library/books/20260814_this-12-year-old-created-an-ai-receptionist-to-help-small-businesses---business-insider/digest.md` | Единичный новостной источник (Business Insider) о продукте Voxa. Переносимых фактов для стека мало, проверки нет — оставлено сырьём. |
| `06-Library/sinergy-expert-council/digest.md` (полностью) | Текст повреждён: пропала кириллица, читаются только структура и латиница. Взято только то, что уцелело (см. contradictions.md). |
| `06-Library/_catalog.md` | Индекс библиотеки, не источник фактов. В нём нет части папок (tools/, geo-*, gh-weekly, cua, eleven). |
| `source.md` всех папок | 5–10 тыс. строк первоисточников; в вики — только сжатые факты из digest.md. |

## Попутные упоминания тем (без собственных материалов)

- **Bitrix24** — только как пример в `tools/vapi-voice-ai/digest.md` и `mustay-response-patterns/digest.md`. Отдельного разбора нет.
- **Mango Office** — только ценовое сравнение в `tools/vapi-voice-ai/digest.md`; SIP-стек (baresip/DTMF) упомянут списком, деталей нет.
- **RAG (kb-prep, гибридный поиск)** — только формулировки в `mustay-response-patterns/digest.md` и раздел RAG в `books/nblm-agentic-ai-guide/digest.md`. Пайплайна `kb-prep` в библиотеке нет.
- **Honcho, Firecrawl, kb-prep** — в `06-Library` не встречаются (проверено grep 2026-11-17). Их разбор живёт в `ACTIVE_TASKS.md` (секция HMS), не в библиотеке.
- **Hermes** — только как Hermes Profiles/Agents в `es-n-multiagent-gateway/digest.md` и `skill-library-v2/digest.md`; отдельного материала про Hermes Agent как харнесс нет.
- **claude-mem** — только абзац в `gh-weekly-2026-10-20/digest.md`.
