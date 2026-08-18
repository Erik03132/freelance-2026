# vault/CLAUDE.md — правила работы агентов с Obsidian vault

Возможности vault для агентов (см. AGENTS.md 0.1):
- Агенты читают ТОЛЬКО md: `vault/06-Library/**/digest.md|source.md` и
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Личное/КНИГИ/**/digest.md`.
- Ночной читатель (`tools/ops/night_reader.sh`) разгребает `vault/00-Inbox/`:
  сырьё → 06-Library. СЫРЬЁ не попадает в ACTIVE_TASKS напрямую.

## Frontmatter (минимум 4 поля в создаваемых заметках)

Все новые/редактируемые заметки в vault несут YAML frontmatter:

```yaml
---
type: <тип>           # book-digest | article-digest | lesson | decision | audit | note
tags: [<теги>]        # темы, для фильтрации без чтения всех файлов
status: <статус>      # inbox | read | processing | done
updated: YYYY-MM-DD   # дата последнего изменения
---
```

- `book_digest.py` уже пишет `type: book-digest`, `tags: []`, `updated`, `status: read`.
- Агент САМ предлагает/дополняет поля (type/tags/status/updated) для заметок, которые создаёт
  или меняет — фильтрация по frontmatter быстрее чтения всех файлов.

## Иерархия

- `00-Inbox/` — вход (свалка), ночной читатель раскладывает.
- `06-Library/` — переработанные материалы (digest.md + source.md).
- `03-Lessons/` — уроки из практики.
- `04-Decisions/`, `05-Audits/` — решения и аудиты.
- 5 полей frontmatter достаточно; НЕ плодить десятки полей (YAGNI).

## Правило-исключение

- Заметки в `00-Inbox/` до обработки могут НЕ иметь frontmatter — их нормализует ночной читатель.