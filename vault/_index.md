# Vault — база знаний

SSoT для документных знаний. События сессий — в claude-mem, здесь — постоянные знания.

**Для ИИ:** начинай отсюда. Этот файл — точка входа. Описывает структуру, правила и навигацию по vault.

---

## Владелец

Игорь Васин — фриланс AI-инженер, Россия. Основные направления:
- AI-агенты (Retell, Retell Conductor, голосовые боты)
- SEO/GEO (AI Overviews, Perplexity, ChatGPT)
- Автоматизация (Bitrix24, Mango Office, Telegram)
- Гранты (44-ФЗ, 223-ФЗ, Фонд ИСТИНА)

---

## Структура vault

```
vault/
├── _index.md              ← ТЫ ЗДЕСЬ. Точка входа для ИИ.
├── 00-Inbox/              ← Сырой вход. Файлы с VPS (rsync из /opt/vault_inbox).
│   └── (ночные скрипты переносят в 06-Library/books/)
├── 01-Projects/           ← Контекст по проектам (CONTEXT.md для каждого)
├── 02-Knowledge/          ← Доменные базы знаний
│   ├── ai-agents/         ← Архитектура AI-агентов, паттерны, интеграции
│   ├── bitrix/            ← Bitrix24: CRM, webhook, интеграции
│   ├── grants/            ← Гранты: Фонд ИСТИНА, 44-ФЗ, чеклисты
│   ├── laws/              ← Законодательство РФ
│   └── seo/               ← SEO/GEO/AEO: стратегии, инструменты
├── 03-Lessons/            ← Уроки и паттерны (извлечённые из опыта)
│   └── YYYY-MM-DD_<slug>.md
├── 04-Decisions/          ← ADR (Architecture Decision Records)
│   └── <project>-<number>-<slug>.md
├── 05-Audits/             ← Аудиты: код, инструменты, безопасность
│   └── <prefix>_<name>.md
├── 06-Library/            ← Личная библиотека
│   ├── _catalog.md        ← Каталог всех материалов
│   ├── books/             ← Книги и статьи (digest.md + source)
│   ├── fiction/           ← Художественная литература
│   └── media/             ← Видео/аудио (summary.md + ссылки)
├── 10-Daily/              ← Daily notes (пока пусто)
└── _templates/            ← Шаблоны файлов
```

---

## Как работать с этим vault

### Если ты — ИИ-ассистент (Claude, Gemini, Codex, etc.)

1. **Начни с этого файла** — ты уже здесь
2. **Определи контекст задачи** — какой раздел релевантен?
3. **Читай только .md** — PDF/ePub не читать (конвертацию делает ночной читатель)
4. **При архитектурных решениях** — проверяй `04-Decisions/` и `05-Audits/`
5. **При работе с книгами** — `06-Library/books/<slug>/digest.md`

### Правила для ИИ

- **SSoT:** постоянные знания — в vault, сессионные — в claude-mem
- **Форматы:** только markdown. Исходники (PDF, ePub) — в vault не добавлять
- **Нумерация:** файлы в `03-Lessons/`, `05-Audits/` начинаются с даты или префикса (PF-1, HT-1)
- **ADR:** формат `RW-4-agpl-repowise.md` — проект + номер + slug
- **Каталог:** `06-Library/_catalog.md` — автообновляется nightly

### Ночные скрипты

- **night_reader.sh** (02:30 daily): VPS inbox → digest → reports → Telegram
- **night_audit.sh** (03:30 daily): код-аудит → reports
- **obsidian_mirror.py:** claude-mem → vault sync (ежедневно)

---

## Навигация по темам

| Задача | Куда смотреть |
|---|---|
| "Что по грантам?" | `02-Knowledge/grants/`, `03-Lessons/*grant*` |
| "Как интегрировать Bitrix?" | `02-Knowledge/bitrix/` |
| "Какие аудиты были?" | `05-Audits/` |
| "Что за решения принимались?" | `04-Decisions/` |
| "Есть ли digest по книге X?" | `06-Library/_catalog.md` → `06-Library/books/` |
| "Какие уроки по AI-агентам?" | `03-Lessons/`, `02-Knowledge/ai-agents/` |
| "SEO-стратегия?" | `02-Knowledge/seo/` |

---

## Связь с другими системами

- **claude-mem** — сессионная память (observations, timeline). Vault и claude-mem дополняют друг друга.
- **AGENTS.md** — глобальные правила для OpenCode (каскад моделей, TDD, eval-driven)
- **skills/** — `~/.config/opencode/skills/` — навыки для специализированных задач
- **VPS** — `/opt/vault_inbox/` → `00-Inbox/` через rsync (порт 22001)

---

*Последнее обновление: 2026-08-10*
