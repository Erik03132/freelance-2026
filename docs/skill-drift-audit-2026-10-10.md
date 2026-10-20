# DRIFT-АУДИТ: скиллы OpenCode vs Hermes (2026-10-10)

**Задача:** устранить «кашу» — две системы, 110 активных скиллов Hermes и ~148 в
OpenCode (135 верхнего уровня + 13 персон), пересечения без единого источника.
Правило: **одна задача = один мастер, остальное — обёртки.**

## Цифры

| Метрика | Значение |
|---------|----------|
| Скиллов Hermes (активных / всего) | 110 / 123 (13 в `.archive/`) |
| Скиллов OpenCode | ~148 (135 top-level + 13 персон в `skills/agents/`) |
| Точных совпадений имён | 1 — `systematic-debugging` |
| Смысловых пересечений (дубль-риск) | 12 |
| Уникального в Hermes — кандидатов в импорт | 8 |
| Остаётся в Hermes (инфра/личное/инструменты) | ~70 |

## A. Дубли — свернуть к одному мастеру

| # | Hermes-скилл | OpenCode-мастер | Действие |
|---|--------------|-----------------|----------|
| 1 | `financier-unit-economics` | `agents/financier` | Слить pricing-playbook и CFO-чеклисты в OC-мастер; в Hermes — ссылка |
| 2 | `jobhunter` | `agents/batrak` | Мастер OC; Hermes — обёртка |
| 3 | `shrelock-research` | `agents/sherlock` | Мастер OC; Hermes — обёртка |
| 4 | `expert-source-review` | `expert-source-pipeline` | Мастер OC; Hermes — обёртка |
| 5 | `finish-day-progress` | `finish-day` | Мастер OC; Hermes вызывает, не дублирует |
| 6 | `systematic-debugging` | `systematic-debugging` | Мастер OC; Hermes — обёртка |
| 7 | `humanizer` | `brand-voice` | Слить список «AI-isms»-банов в OC; Hermes — обёртка |
| 8 | `secret-rotation` | `agents/ai-defender` | Мастер OC; Hermes — обёртка |
| 9 | `merge-reconciler` | `resolving-merge-conflicts` | Мастер OC; Hermes — обёртка |
| 10 | `blocked-page-recovery` | `web-search` | Мастер OC; Hermes — обёртка |
| 11 | `claude-design` | `frontend-design` | Мастер OC; Hermes — обёртка |
| 12 | `design-md` | `design-bridge` | Мастер OC; Hermes — обёртка |

Итого после сворачивания: **0 смысловых дублей**.

## B. Импорт в OpenCode (шорт-лист, нет аналога у нас)

| Скилл | Зачем | Для кого |
|-------|-------|----------|
| `grounded-citations` | Цитируемые источники в отчётах — спарка с нашим evidence-first (ADR-003) | Шерлок, Фемида, отчёты |
| `ocr-and-documents` | Текст из PDF/сканов (marker-pdf) — документы ai-bus, дела, КП | все проектные |
| `popular-web-designs` | 54 реальных дизайн-системы как HTML/CSS — быстрые референсы | Рембрандт, Артемий |
| `architecture-diagram` | Быстрые SVG-схемы архитектуры для ADR/КП | Кулибин, Игорек |
| `competitor-news-monitor` | Фоновый мониторинг компаний + дайджесты | Шерлок, ai-scout |
| `blogwatcher` | RSS-мониторинг блогов — контент-разведка | Шекспир, Шерлок |
| `text-unicode-hygiene` | Защита от кракозябр (частый баг в ТГ/кросах) | все |

Отложено: `research-paper-writing` (72 КБ, редкая задача), `weekly-review-planning`
(личный ритм — живёт в Hermes).

## C. Остаётся в Hermes (логические кластеры, без пересечений)

- **Hermes-инфра:** hermes-agent, hermes-infra-ops, hermes-vps-ops, hermes-knowledge-sync, hermes-profile-ssot, telegram-hermes-bot, vps-*, remote-vps-agent-ops, igor-hermes-telegram-vps, freelance-workspace-chief (обёртка OC-скилла)
- **Proxy/сеть:** igor-proxy-network, rf-split-proxy-routing (дубль ADR-002 полиси — оставить как раннтайм)
- **Личное/macOS:** apple-*, imessage, findmy, openhue, macos-*, macos-tm-nas-backup, maps, session-librarian, english-tutor
- **Офис-инструменты:** pdf, docx, xlsx, powerpoint, nano-pdf, notion, airtable, box, google-workspace, himalaya, email-*, gif-search, ocr-*
- **Креатив-инфра:** comfyui, touchdesigner-mcp, p5js, manim-video, ascii-video, baoyu-infographic, pretext, sketch, songwriting-and-ai-music, songsee
- **ML/LLM-инфра:** evaluating-llms-harness, weights-and-biases, serving-llms-vllm, llama-cpp, huggingface-hub, nous-inference-api, omni-route-provider, llm-wiki, arxiv
- **GitHub/делегирование:** github-* (5), claude-code, codex, opencode, computer-use, dogfood, spike, simplify-code, codebase-inspection, sdlc-review, plan, agent-personas, expert-council-adapter, xurl, youtube-content, product-price-monitor, teams-meeting-pipeline, weekly-review-planning, text-unicode-hygiene*

`text-unicode-hygiene` — импортировать в OC (B) и оставить как shared.

## D. Профили: 5 прямых совпадений + 3 аналога + 6 уникальных

| Профиль Hermes | OpenCode-агент | Вердикт |
|----------------|----------------|---------|
| chief | igorek | Мастер OC, Hermes — обёртка |
| sherlock / batrak / femida / financier / marketer | те же агенты | Мастер OC, Hermes — обёртки |
| health | aibolit | Мастер OC, обёртка |
| defender | ai-defender | Мастер OC, обёртка |
| bridge | botman | Частично; TG-релей — Hermes-side |
| personal / default / chief-vps-test | — | Инфра-профили, оставить |
| — | shakespeare, rembrandt, kulibin, artemiy, igorek | Нет в Hermes — **не добавлять** без повторяющихся TG-задач |

## E. Память

- **Мастер:** claude-mem (факты, переживающие сессию; projectId-карта).
- **Hermes `profiles/*/state`** — только оперативка сессий.
- Публикация долгоживущих уроков: OC пишет в vault `03-Lessons/`, Hermes ссылается.

## План действий

1. Аппрув шорт-листа B (7 скиллов) → копирование в `~/.config/opencode/skills/`
   (формат SKILL.md совместим, frontmatter OpenCode-типа).
2. Свернуть A-дубли: 6 мастеров в OC обогащаются содержимым Hermes, 6 Hermes-
   скиллов становятся обёртками (одна ссылка вместо копии).
3. Расширить воскресный автосинк скиллов: к диффу добавлять **drift-отчёт**
   (что появилось в Hermes / потерялось в OC), цель — 0 новых дублей.

## Метрики

- Смысловых дублей между системами: 0
- Мастер-скиллов в OC: единственный источник истины
- Новый скилл в Hermes — сначала проверка на дубль в OC (и наоборот)

## Связано

- `~/.config/opencode/AGENTS.md` п.13 (верификация), п.15 (lazy-load)
- `projects/ai-bus/` — появился из этого же принципа SSoT
