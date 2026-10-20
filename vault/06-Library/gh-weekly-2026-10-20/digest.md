---
type: article-digest
tags: [gh-trending, skills, video, multi-agent, инструменты]
status: done
updated: 2026-10-20
---

# Растущие OSS неделя 13–20.10.2026 — разбор

Источник: подборка Игоря (4 проекта). Верификация: README всех репо прочитаны 20.10.2026.
Применённое установлено в `~/.config/opencode/skills/` (задачи — в ACTIVE_TASKS, секция GH).

## 1. mattpocock/skills — ПРИНЯТО (выборочно)

- 298k★, MIT, «Skills for Real Engineers» (aihero.dev), активный (546 коммитов).
- Каталог: grilling-примитив, grill-me / grill-with-docs, tdd, to-spec / to-tickets,
  implement / implement-spec, triage, wayfinder, retro, handoff, prototype,
  research, diagnosing-bugs, domain-modeling, codebase-design, code-review
  (two-axis), pr, wizard, writing-for-agents, wait-what, to-questionnaire, teach.
- **Установлено (7):** grilling, domain-modeling, grill-with-docs, retro, wizard,
  to-tickets, writing-for-agents.
- Дубли НЕ ставились: tdd / code-review / handoff / grill-me уже покрыты нашим
  AGENTS-каскадом (Grill Session, Two-axis Review, claude-handoff).
- Ключевая идея к усвоению: **GLOSSARY.md как shared language** — усилит наш
  CONTEXT.md; grill-with-docs строит глоссарий + ADR в ходе собеседования,
  снижает многословие и токены агента.

## 2. thedotmack/claude-mem — УЖЕ РАБОТАЕТ

Мы подключены с 2026-07-25 (server-beta :37878 + Postgres). Действий нет.
Примечание: подборка маркирует его как «растущий» — подтверждение выбора верное.

## 3. heygen-com/hyperframes — ПРИНЯТО (ядро)

- 68.2k★, Apache-2.0, 5.7k коммитов. Production у HeyGen; ADOPTERS: tldraw, TanStack.
- Что делает: HTML + CSS + GSAP/Lottie/Three.js/Anime.js → детерминированный MP4
  (headless Chrome + FFmpeg); без React и без build-степа; index.html играется
  прямо в браузере. Каталог готовых блоков (~400), render на CI/Lambda.
- **Установлено (core-набор, 10 скиллов):** hyperframes (роутер), animation,
  audio, cli, core, creative, keyframes, registry, studio, media-use.
- Рантайм для рендера: Node 24 ✓, ffmpeg ✓ (`/opt/homebrew/bin/ffmpeg`).
- Связка с PMO (prompt-motion.com): референс → адаптация промпта → рендер ролика.
  HyperFrames — недостающий рендер-движок для этого воркфлоу.

## 4. mvschwarz/openrig — БИБЛИОТЕКА (гипотеза, не ставить сейчас)

- 8k★, Apache-2.0. Мульти-агентные команды через tmux: RigSpec YAML (pods/edges),
  команды starter / workshop / factory, rig send / broadcast / chatroom,
  snapshot/restore, Slack-интеграция.
- Риски (ai-defender): kernel-агент по умолчанию получает full access; пишет
  hooks/trust в `~/.claude.json` / `config.toml`; README сам требует бэкап.
- Пока не ставим: перекрывается нашим subagent + claude-handoff +
  worktree-per-task (OR-2). Возвращаться при появлении задачи на персистентные
  multi-window команды.

## Общий вывод

Три независимых сигнала недели (mattpocock, hyperframes, harness2 — см.
ACTIVE_TASKS H2): индустрия повышает ставку на «агент = модель + редактируемые
скиллы/глоссарий/память». Наш стек двигался этим путём — подборка только
ускоряет.

## Установка HyperFrames — обход, о котором помнить

`npx skills add` упёрся в E407 (перехватывающий прокси на уровне сети, npm-конфиг
чист). Обход: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1` → ручное копирование
core-скиллов. npmjs по ADR-002 должен ходить напрямую; при повторе 407 —
проверить сеть/VPN, не проксировать.
