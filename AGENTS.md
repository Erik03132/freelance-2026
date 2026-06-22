# AGENTS.md — Монорепозиторий freelance-2026

Монорепозиторий фриланс-проектов: AI-агенты, RAG, голосовой AI, веб-разработка.

**Каскадная система, глобальные скиллы, правила эскалации:** `~/.config/opencode/AGENTS.md`
**Карта репозитория для IDE:** `PROJECT_CONTEXT.md`

---

## Архитектура репозитория

Репозиторий переходит к структуре `foundation + projects`:

```text
freelance-2026/
├── foundation/              # Универсальные скиллы, агенты, библиотеки
├── projects/                # Активные проекты
├── archive/                 # Закрытые/замороженные проекты
├── templates/               # Шаблоны проектов, скиллов, агентов
├── tools/                   # Глобальные скрипты
└── docs/ + chronicles/      # Глобальная документация и хроника
```

### G0 — универсальный оркестратор

```bash
./tools/go.sh new project <name>      # Создать новый проект
./tools/go.sh new skill <domain> <n>   # Создать foundation-скилл
./tools/go.sh new agent <id>           # Создать foundation-агента
./tools/go.sh boot                     # Boot: пинг API, проверка агентов
```

### Скрипты-генераторы (вызываются напрямую)

| Скрипт | Назначение | Пример |
|--------|------------|--------|
| `tools/new-project.sh` | Создать каркас нового проекта | `./tools/new-project.sh ai-sales-assistant` |
| `tools/new-skill.sh` | Создать foundation-скилл | `./tools/new-skill.sh code generate-tests` |
| `tools/new-agent.sh` | Создать foundation-агента | `./tools/new-agent.sh security-auditor` |

### Документация

| Файл | Назначение |
|------|------------|
| `foundation/docs/IDE_GUIDE.md` | Как работать в разных IDE со старыми и новыми проектами |

### Правила размещения

- **Foundation** (используется в 2+ проектах) → `foundation/`
- **Проектный код** → `projects/<name>/src/`
- **Проектные скиллы** → `projects/<name>/project-skills/`
- **Проектные агенты** → `projects/<name>/project-agents/`
- **Архив** → `archive/`
- **Глобальные скрипты** → `tools/`

---

## Активные проекты

| Проект | Описание | Стек | AGENTS.md |
|--------|----------|------|-----------|
| `projects/ai-bureau/` | Агентство AI-систем: кастомные агенты, RAG, GEO | Vite+React+TS | `projects/ai-bureau/AGENTS.md` |
| `projects/ai-eggs/` | Инфраструктура для птицеводства: Заботкина + Птенчикова | Python | `projects/ai-eggs/AGENTS.md` |
| `projects/ai-scout/` | Сбор и саммари из Telegram + YouTube, библиотека избранного | React+Vite+TS+Supabase | — |
| `projects/angel-backend/` | Бэкенд Анжелочки: autopilot, CRM-интеграции | Python | — |
| `projects/agent-lab/` | Лаборатория: LLM/поисковый/фото каскады, эксперименты | Python | — |
| `projects/dashboard/` | Дашборд / админка | Astro/TS | — |
| `projects/freelance-agent/` | Агент для фриланс-бирж, оркестратор | Node/TS | — |
| `projects/ivan-bureau/` | Проект бюро Ивана | — | — |
| `projects/my-project/` | Резервный/тестовый проект | — | — |
| `projects/ok/` | Проект ОК | — | — |
| `projects/svo-start/` | СВО-стартап | — | — |
| `projects/водоканал/` | Проект Водоканал | — | — |
| `projects/ai-grant-portal-temp/` | Временный грантовый портал | — | — |

## Архивные проекты

| Проект | Статус |
|--------|--------|
| `archive/ai-senat/` | 🔒 ЗАКРЫТ |
| `archive/ai-grant-consalt/` | 🔒 ЗАКРЫТ |

## Оставшиеся в корне (не тронуты)

| Путь | Что это |
|------|---------|
| `antigravity-brain/` | Локальный brain / knowledge (игнорируется git) |
| `src/` | Остатки старого dashboard-кода — решить отдельно |
| `НА_ПРОВЕРКУ_Своё_Подворье/` | Клиентская папка на проверке |

---

## Глобальные инструменты (tools/)

| Папка | Назначение |
|-------|------------|
| `tools/` | Ежедневная рутина: `habr_intelligence.py`, `morning_dream.sh`, `night_audit.sh`, `chronicle.sh`, `start_day.sh`, `finish_day.sh`, `save_session_state.sh`, `watchdog.py`, `ping_apis.sh`, `cleanup.sh` |
| `tools/angela/` | Runtime Анжелочки: `angela_outbound_v2.py`, `mango_api.py`, `get_daily_report*.py`, `send_report_today.py`, `get_stats.py` |
| `tools/deploy/` | Деплой: `deploy_cloud.sh`, `deploy_mustai.sh` |
| `tools/expect/` | Expect-скрипты для сервера: `check_server_tmp.exp`, `install_ssl.exp`, `rescue_bots.exp`, `final_fix.exp`, `final_start.exp` |
| `tools/media/` | Обработка изображений: `resize_cover.py` |
| `tools/beat-slideshow/` | Генерация слайд-шоу |

## Генераторы

| Скрипт | Назначение | Пример |
|--------|------------|--------|
| `tools/new-project.sh` | Создать каркас нового проекта | `./tools/new-project.sh ai-sales-assistant` |
| `tools/new-skill.sh` | Создать foundation-скилл | `./tools/new-skill.sh code generate-tests` |
| `tools/new-agent.sh` | Создать foundation-агента | `./tools/new-agent.sh security-auditor` |

## Архив one-off патчей

`_archive/patches/` — одноразовые `patch_*.py`, `fix_*.py`, `test_*.py`, бэкапы `voice_bridge.py.bak2`.

---

## Дорожная карта реструктуризации

- [x] **Phase 0 + Phase 1:** каркас `foundation/`, `projects/`, `archive/`, `templates/`, генераторы `new-project/skill/agent`
- [x] **Phase 2:** перенос активных проектов в `projects/`
- [x] **Phase 3:** дедублицикация скиллов → `foundation/skills/`
- [x] **Phase 4:** создание `config/{project,agents,skills}.yaml` для каждого проекта
- [x] **Phase 5:** перенос глобальных скриптов из корня в `tools/`
- [x] **Phase 6:** обновление IDE-адаптеров (OpenCode + Antigravity; Cursor — пока нет)
