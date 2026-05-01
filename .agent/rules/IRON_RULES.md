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
├── chp.md                                 ← Чекпоинт текущего состояния
├── ACTIVE_TASKS.md                        ← Дорожная карта задач
├── reports/                               ← Дневные отчёты сессий
├── tools/                                 ← Общие скрипты
├── ai-eggs/                               ← Проект AI-EGGS (Заботкина + Птенчикова)
├── freelance-agent/                       ← Навыки агента, SKILL.md
└── [другие проекты]/                      ← Каждый проект — отдельная папка
```

**Правило:** проектные знания (каскад моделей, PM2 конфиг, расписание) лежат
в `.md` файлах **внутри папки проекта**, а НЕ здесь.

---

## 4. 🔒 ПРОТОКОЛЫ

### Finish Day (команда: "финиш", "конец дня"):
1. Перезаписать `chp.md`
2. Создать `checkpoints/chp_YYYYMMDD_HHMM.md`
3. Создать `reports/report-day_YYYY-MM-DD_HHMM.md`
4. Запустить `bash ~/freelance-2026/tools/finish_day.sh`

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

## 6. 🧠 BOOT SEQUENCE

При старте сессии по команде `boot` / `старт` / `инициализация`:
1. Прочитать **этот файл** (IRON_RULES.md)
2. Прочитать `chp.md` — текущий чекпоинт
3. Прочитать `ACTIVE_TASKS.md` — активные задачи
4. Если работа с конкретным проектом — прочитать его `PROJECT.md` / `README.md`
5. **Agent Readiness Check** — проверить заряженность ВСЕХ агентов по таблице ниже
6. НЕ пересказывать содержимое пользователю, просто работать

---

## 7. 🛡️ AGENT READINESS — ПОЛНАЯ КАРТА АГЕНТОВ

**ОБЯЗАТЕЛЬНО при каждом буте.** Проверить `view_file` на каждый путь из колонки «Global SKILL.md».
Если файл не найден → агент `❌ MISSING` → сессия **НЕ Safe**.
Проектные скиллы: warning, не блокер.

### 7.1. Фундаментальные (Global) скиллы — 8 агентов

| # | Агент | Global SKILL.md (абсолютный путь) | ECC-скиллы (встроены в SKILL.md) |
|---|-------|----------------------------------|----------------------------------|
| 1 | **Игорёк** (igorek-core) | `/Users/igorvasin/.gemini/antigravity/skills/igorek-core/SKILL.md` | agentic-engineering, search-first, ADR, parallel execution, model routing, hooks |
| 2 | **Кулибин** (kulibin-engineer) | `/Users/igorvasin/.gemini/antigravity/skills/kulibin-engineer/SKILL.md` | deployment-patterns, security-review, cost-aware-llm, search-first, coding-style, patterns, git-workflow, testing |
| 3 | **Артемий** (artemiy-frontend) | `/Users/igorvasin/.gemini/antigravity/skills/artemiy-frontend/SKILL.md` | frontend-patterns, AI website cloning |
| 4 | **Ботмэн** (botman-creator) | `/Users/igorvasin/.gemini/antigravity/skills/botman-creator/SKILL.md` | security, cost-aware-ai, deployment-checklist |
| 5 | **Рембрандт** (rembrandt-designer) | `/Users/igorvasin/.gemini/antigravity/skills/rembrandt-designer/SKILL.md` | design-system, SVG→3D WebGL |
| 6 | **Шекспир** (shakespeare-editor) | `/Users/igorvasin/.gemini/antigravity/skills/shakespeare-editor/SKILL.md` | content-engine, brand-voice, article-writing, human-first writing |
| 7 | **Шерл** (sherl-research) | `/Users/igorvasin/.gemini/antigravity/skills/sherl-research/SKILL.md` | market-research, search-first, deep-research |
| 8 | **Маркетолог** (marketer-strategist) | `/Users/igorvasin/.gemini/antigravity/skills/marketer-strategist/SKILL.md` | technical-seo, dashboard-builder, CMO-framework, AI-ORM |

### 7.2. Проектные скиллы (абсолютные пути)

| # | Скилл | Абсолютный путь | Назначение |
|---|-------|-----------------|------------|
| 1 | bitrix-integration | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/bitrix-integration/SKILL.md` | CRM Битрикс24 |
| 2 | brand-voice | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/brand-voice/SKILL.md` | Голос бренда |
| 3 | deployment-procedures | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/deployment-procedures/SKILL.md` | Процедуры деплоя |
| 4 | geo-fundamentals | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/geo-fundamentals/SKILL.md` | GEO-оптимизация |
| 5 | react-patterns | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/react-patterns/SKILL.md` | React-паттерны |
| 6 | telegram-bot-patterns | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/telegram-bot-patterns/SKILL.md` | Telegram-боты |
| 7 | svo-veteran-support | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/svo-veteran-support/SKILL.md` | Гранты для ветеранов |

### 7.3. Реестр скиллов

Полный реестр с версиями и маршрутизацией:
`/Users/igorvasin/.gemini/antigravity/skills/skills-registry.json`

### 7.4. Формат вывода при буте

```
=== AGENT READINESS ===
✅ igorek-core        — ARMED (global + 6 ECC)
✅ kulibin-engineer    — ARMED (global + 8 ECC + 1 project)
✅ artemiy-frontend    — ARMED (global + 2 ECC + 2 project)
✅ botman-creator      — ARMED (global + 3 ECC + 1 project)
✅ rembrandt-designer  — ARMED (global + 2 ECC)
✅ shakespeare-editor  — ARMED (global + 4 ECC + 1 project)
✅ sherl-research      — ARMED (global + 3 ECC)
✅ marketer-strategist — ARMED (global + 4 ECC + 1 project)
PROJECT SKILLS: 7/7 ✅
SESSION: ✅ SAFE
```
