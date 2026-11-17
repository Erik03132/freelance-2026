---
type: wiki
tags: [oss, skills, hyperframes, claude-mem, mattpocock, openrig, tools]
status: done
updated: 2026-11-17
sources: [06-Library/gh-weekly-2026-10-20/digest.md]
---

# OSS-неделя 13–20.10.2026: четыре вердикта

Источник: `06-Library/gh-weekly-2026-10-20/digest.md` (2026-10-20). Верификация: README всех репозиториев прочитаны 20.10.2026. Звёзды — со слов дайджеста, не перепроверялись.

## 1. mattpocock/skills — принято выборочно

- 298k★, MIT, «Skills for Real Engineers» (aihero.dev), 546 коммитов.
- Каталог: grilling, grill-me / grill-with-docs, tdd, to-spec / to-tickets, implement / implement-spec, triage, wayfinder, retro, handoff, prototype, research, diagnosing-bugs, domain-modeling, codebase-design, code-review (two-axis), pr, wizard, writing-for-agents, wait-what, to-questionnaire, teach.
- Установлено 7: grilling, domain-modeling, grill-with-docs, retro, wizard, to-tickets, writing-for-agents.
- Дубли не ставились: tdd, code-review, handoff, grill-me уже покрыты нашим каскадом.
- Идея к усвоению: GLOSSARY.md как общий язык — усиливает CONTEXT.md; grill-with-docs строит глоссарий и ADR в ходе собеседования и снижает многословие.

## 2. thedotmack/claude-mem — уже работает

Подключён с 2026-07-25 (server-beta :37878 плюс Postgres). Действий нет; подборка ошибочно считает его новым.

## 3. heygen-com/hyperframes — принято ядром

- 68.2k★, Apache-2.0, 5.7k коммитов; production у HeyGen, adopter'ы tldraw и TanStack.
- HTML + CSS + GSAP/Lottie/Three.js/Anime.js → детерминированный MP4 (headless Chrome + FFmpeg), без React и без build-степа; index.html играется прямо в браузере. ~400 готовых блоков, рендер на CI/Lambda.
- Установлено 10 скиллов: hyperframes (роутер), animation, audio, cli, core, creative, keyframes, registry, studio, media-use.
- Рантайм проверен: Node 24, ffmpeg в `/opt/homebrew/bin/ffmpeg`.
- Связка с PMO (prompt-motion.com): референс → адаптация промпта → рендер ролика.

## 4. mvschwarz/openrig — библиотека, не ставить

- 8k★, Apache-2.0. Мульти-агентные команды через tmux: RigSpec YAML (pods/edges), команды starter / workshop / factory, `rig send / broadcast / chatroom`, snapshot/restore, Slack.
- Риски: kernel-агент по умолчанию получает full access; пишет hooks/trust в `~/.claude.json` и `config.toml`; README сам требует бэкап.
- Перекрывается subagent + claude-handoff + worktree-per-task. Возвращаться при задаче на персистентные multi-window команды.

## Общий вывод недели

Три независимых сигнала (mattpocock, hyperframes, harness2) указывают в одну сторону: «агент = модель + редактируемые скиллы, глоссарий и память». Наш стек двигался этим путём; подборка ускоряет, а не меняет направление.

## Практическая деталь

`npx skills add` упал с E407 (перехватывающий прокси на уровне сети, npm-конфиг чист). Обход: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1` плюс ручное копирование core-скиллов. npmjs по политике прокси должен идти напрямую: при повторе 407 проверять сеть/VPN, а не проксировать.

## Связка

`skill-library-v2` — план федеративной библиотеки, который этим набором не реализован. `cua-spaces` — второй кандидат на изоляцию агентов, отклонён не был, ждёт железа.
