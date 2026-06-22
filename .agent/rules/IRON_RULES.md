# 🔩 ЖЕЛЕЗНЫЕ ПРАВИЛА АГЕНТА (IRON RULES)
# Фундаментальные правила, действующие ВСЕГДА, в ЛЮБОМ проекте.
# Читать при КАЖДОМ старте сессии. Нарушение = ГРУБАЯ ОШИБКА.
# Обновлено: 2026-04-30

---

## 1. 🚀 АВТОНОМНЫЙ ДОСТУП К СЕРВЕРУ

**ЗАПРЕЩЕНО просить пользователя вводить серверные команды.**
Агент выполняет ВСЕ деплои, рестарты, чтение логов **САМОСТОЯТЕЛЬНО** через `run_command` + SSH.

### Реквизиты:
- **SSH-ключ:** `/Users/igorvasin/freelance-2026/.ssh_agent_key`
- **Сервер:** `root@72.56.38.19` (Timeweb VDS)
- **Шаблон:**
  ```bash
  ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no root@72.56.38.19 'КОМАНДА'
  ```

> Если агент пишет «зайди на сервер и выполни...» — это **ГРУБОЕ НАРУШЕНИЕ**.

---

## 2. 🌐 ЯЗЫК И СТИЛЬ ОБЩЕНИЯ

- Общаться **на русском языке**
- Не повторять информацию, которую пользователь уже знает
- Не предлагать пользователю сделать то, что агент может выполнить сам
- Быть кратким, по делу

---

## 3. 📂 СТРУКТУРА РАБОЧЕЙ СРЕДЫ

```
/Users/igorvasin/freelance-2026/           ← Корень всех проектов
├── .agent/rules/                          ← Фундаментальные правила (этот файл)
├── .ssh_agent_key                         ← SSH-ключ для VPS
├── PROJECT_CONTEXT.md                     ← Карта репозитория для IDE
├── AGENTS.md                              ← Карта проектов и роадмап
├── chp.md                                 ← Чекпоинт текущего состояния
├── ACTIVE_TASKS.md                        ← Дорожная карта задач
├── foundation/                            ← Универсальные скиллы и агенты
│   ├── skills/<domain>/<skill>/
│   └── agents/<agent>/
├── projects/                              ← Активные проекты
│   └── <project-name>/
│       ├── config/{project,agents,skills}.yaml
│       ├── project-skills/
│       ├── src/
│       └── docs/
├── archive/                               ← Закрытые проекты
├── templates/                             ← Шаблоны проектов, скиллов, агентов
├── tools/                                 ← Общие скрипты
├── reports/                               ← Дневные отчёты сессий
├── chronicles/                            ← Хроники дней (автозапись)
├── dreams/                                ← 🌙 Dreaming: паттерны из хроник
│   ├── patterns.md                        ← Кумулятивная память (читать при boot)
│   └── dream_YYYY-MM-DD.md               ← Ежедневные dream-отчёты
└── [другие глобальные папки]/
```

**Правило:**
- Foundation-скиллы и агенты лежат в `foundation/`.
- Проектные знания лежат в `projects/<name>/config/` и `projects/<name>/project-skills/`.
- При старте сессии читай `PROJECT_CONTEXT.md`, затем `projects/<name>/AGENTS.md`.

---

## 4. 🔒 ПРОТОКОЛЫ

### Finish Day (команда: "финиш", "конец дня"):
1. Перезаписать `chp.md`
2. Создать `checkpoints/chp_YYYYMMDD_HHMM.md`
3. Создать `reports/report-day_YYYY-MM-DD_HHMM.md`
4. Запустить `bash ~/freelance-2026/tools/finish_day.sh`

### 🌙 Morning Dream (cron 07:00 MSK или вручную):
```bash
bash ~/freelance-2026/tools/morning_dream.sh          # анализ за 3 дня
bash ~/freelance-2026/tools/morning_dream.sh --days 7  # за неделю
```
Анализирует хроники → извлекает паттерны → обновляет `dreams/patterns.md`.
При boot можно прочитать `dreams/patterns.md` для быстрого восстановления контекста.

### 🎯 Content Outcomes (перед публикацией контента):
```bash
python3 ~/freelance-2026/tools/content_grader.py -f draft.md --rubric all
```
Отдельный grader по E-E-A-T, Human-First, VK Farm. FAIL → переделка.

### Деплой на VPS:
1. rsync код → VPS (через SSH-ключ)
2. Перезапуск PM2 из ecosystem.config.js
3. Проверить `pm2 list` после деплоя

### NAS бэкап (Synology DS720+):
- IP: 192.168.0.107, user: erik03132
- Встроен в finish-day (Фаза 4)

---

## 5. 💰 ЦЕНООБРАЗОВАНИЕ

1500₽/час × ОБЩЕЕ_время_всех_агентов + 50% = ourPrice.
Если бюджет клиента > ourPrice → берём бюджет − 10%.

---

## 6. 🔍 SEARCH-FIRST PROTOCOL (обязательный каскад решений)

**ПЕРЕД тем как писать код или решать техническую проблему — ОБЯЗАТЕЛЬНЫЙ каскад:**

```
┌──────────────────────────────────────────────┐
│  1️⃣  СВОИ СКИЛЛЫ                             │
│     grep/find по skills/ и knowledge/        │
│     Если решение найдено → ИСПОЛЬЗОВАТЬ      │
│                                              │
│  2️⃣  GITHUB                                  │
│     Поиск рабочих библиотек и примеров       │
│     Если нашёл → адаптировать                │
│                                              │
│  3️⃣  СВОЯ ГОЛОВА                             │
│     Только если 1️⃣ и 2️⃣ не дали результата   │
│     Писать собственное решение               │
└──────────────────────────────────────────────┘
```

### Где искать скиллы:
| Тип | Путь |
|-----|------|
| Foundation | `/Users/igorvasin/freelance-2026/foundation/skills/<domain>/<skill>/SKILL.md` |
| Проектные | `/Users/igorvasin/freelance-2026/projects/<project-name>/project-skills/<skill>/SKILL.md` |
| OpenCode global | `~/.config/opencode/skills/` |
| Knowledge Items | `/Users/igorvasin/.gemini/antigravity/knowledge/*/` |
| Brain (артефакты прошлых сессий) | `/Users/igorvasin/.gemini/antigravity/brain/*/artifacts/` |

> **НАРУШЕНИЕ:** агент тратит 20+ минут на изобретение решения, которое УЖЕ есть в скиллах — это **ГРУБАЯ ОШИБКА**.

---

## 7. 🧠 BOOT SEQUENCE

При старте сессии по команде `boot` / `старт` / `инициализация`:
1. Прочитать **этот файл** (IRON_RULES.md)
2. Прочитать `chp.md` — текущий чекпоинт
3. Прочитать `ACTIVE_TASKS.md` — активные задачи
4. Прочитать `dreams/patterns.md` — кумулятивные паттерны из Dreaming (если есть)
5. Прочитать `foundation/skills/MANIFEST.md` — **лёгкий каталог скиллов** (Progressive Disclosure)
6. Если работа с конкретным проектом — прочитать его `PROJECT.md` / `README.md`
7. НЕ пересказывать содержимое пользователю, просто работать
8. **🔌 ПИНГ ВСЕХ API** — выполнить `bash ~/freelance-2026/tools/ping_apis.sh` и вывести таблицу статусов

### 🌐 ОБЯЗАТЕЛЬНЫЙ US ПРОКСИ ДЛЯ ВСЕХ ВНЕШНИХ API

**ЖЕЛЕЗНОЕ ПРАВИЛО:** Любой запрос к внешним API (Gemini, OpenRouter, Tavily, Perplexity, Unsplash, Pexels, Pixabay, FAL.ai, Google AI) **ОБЯЗАН** идти через US SOCKS5 прокси.

```
ПРОКСИ: из .env → HTTPS_PROXY / TELEGRAM_PROXY
ФОРМАТ: socks5://user:pass@host:port
ИСТОЧНИК: ai-eggs/.env (единый файл ключей)
```

**При пинге API:**
```bash
# ✅ ПРАВИЛЬНО — через прокси:
curl --proxy socks5://user:pass@host:port https://api.example.com

# ❌ НЕПРАВИЛЬНО — напрямую из РФ:
curl https://api.example.com   # 403 Forbidden / timeout
```

**В Python-коде:**
```python
# ✅ ПРАВИЛЬНО:
import os
from dotenv import load_dotenv
load_dotenv("ai-eggs/.env")
# httpx/requests подхватят HTTPS_PROXY автоматически

# ❌ НЕПРАВИЛЬНО:
httpx.get("https://api.google.com")  # без прокси → 403
```

> **НАРУШЕНИЕ:** Любой внешний API-запрос без прокси из РФ — это **ГРУБАЯ ОШИБКА**. Прокси ОБЯЗАТЕЛЕН.

### 🎯 Progressive Disclosure (загрузка скиллов)

**НЕ читай все SKILL.md при boot!** 28 скиллов = ~104K токенов — это убивает контекст.

```
┌──────────────────────────────────────────────────┐
│  BOOT: Читай MANIFEST.md (~1.4K токенов)         │
│  Содержит name + description + triggers           │
│                                                    │
│  MATCH: Когда задача пришла →                     │
│    1. Найди скилл по триггерам в MANIFEST.md      │
│    2. view_file → полный SKILL.md этого скилла    │
│    3. Следуй инструкциям                          │
│                                                    │
│  CLI: python3 ~/freelance-2026/tools/             │
│       skills_manifest.py --match "описание задачи"│
│                                                    │
│  RELEASE: После задачи контекст скилла не нужен   │
└──────────────────────────────────────────────────┘
```

**Регенерация манифеста** (после добавления/изменения скиллов):
```bash
python3 ~/freelance-2026/tools/skills_manifest.py
```

---

## 8. 🛡️ AGENT READINESS — ПОЛНАЯ КАРТА АГЕНТОВ

**При буте проверяй наличие `MANIFEST.md`** — если нет, регенерируй.
Полная проверка всех SKILL.md — только по запросу или при подозрении на проблемы.

### 7.1. Foundation агенты — 8 ролей

| # | Агент | Путь | Назначение |
|---|-------|------|------------|
| 1 | **Игорёк** (igorek-core) | `foundation/agents/igorek-core/` | Оркестратор |
| 2 | **Кулибин** (kulibin-engineer) | `foundation/agents/kulibin-engineer/` | Инженер-оптимизатор |
| 3 | **Артемий** (artemiy-frontend) | `foundation/agents/artemiy-frontend/` | Фронтенд |
| 4 | **Ботмэн** (botman-creator) | `foundation/agents/botman-creator/` | Боты |
| 5 | **Рембрандт** (rembrandt-designer) | `foundation/agents/rembrandt-designer/` | Дизайн |
| 6 | **Шекспир** (shakespeare-editor) | `foundation/agents/shakespeare-editor/` | Контент |
| 7 | **Шерл** (sherl-research) | `foundation/agents/sherl-research/` | Ресёрч |
| 8 | **Маркетолог** (marketer-strategist) | `foundation/agents/marketer-strategist/` | Маркетинг |

Каждый агент:
- `agent.yaml` — роль, инструменты, навыки
- `prompt.md` — системный промпт
- `skills.json` — подключённые foundation/project-скиллы

### 7.2. Foundation скиллы (основные)

| # | Скилл | Путь | Назначение |
|---|-------|------|------------|
| 1 | angelochka-sales | `foundation/skills/business/angelochka-sales/` | Протокол продаж |
| 2 | bitrix-integration | `foundation/skills/business/bitrix-integration/` | Битрикс24 |
| 3 | brand-voice | `foundation/skills/business/brand-voice/` | Голос бренда |
| 4 | deployment-procedures | `foundation/skills/business/deployment-procedures/` | Деплой |
| 5 | geo-fundamentals | `foundation/skills/business/geo-fundamentals/` | GEO/AEO |
| 6 | telegram-bot-patterns | `foundation/skills/business/telegram-bot-patterns/` | Telegram-боты |
| 7 | react-patterns | `foundation/skills/code/react-patterns/` | React |

### 7.3. Проектные скиллы

Каждый проект хранит свои скиллы в `projects/<project-name>/project-skills/<skill>/`.
Реестр: `projects/freelance-agent/.agent/skills-registry.json`

### 7.4. Формат вывода при буте

```
=== AGENT READINESS ===
✅ igorek-core        — ARMED (foundation/agents/igorek-core)
✅ kulibin-engineer    — ARMED (foundation/agents/kulibin-engineer)
✅ artemiy-frontend    — ARMED (foundation/agents/artemiy-frontend)
✅ botman-creator      — ARMED (foundation/agents/botman-creator)
✅ rembrandt-designer  — ARMED (foundation/agents/rembrandt-designer)
✅ shakespeare-editor  — ARMED (foundation/agents/shakespeare-editor)
✅ sherl-research      — ARMED (foundation/agents/sherl-research)
✅ marketer-strategist — ARMED (foundation/agents/marketer-strategist)
FOUNDATION SKILLS: ✅
PROJECT SKILLS: по projects/<name>/config/skills.yaml
SESSION: ✅ SAFE
```
