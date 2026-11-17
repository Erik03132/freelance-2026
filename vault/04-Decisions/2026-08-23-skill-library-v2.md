# ADR: Универсальная библиотека скиллов (Skill Library v2)

**Дата:** 2026-08-23  
**Статус:** Принято  
**Контекст:** Проект `freelance-2026` / Мультиагентная система Hermes / 6 экспертов (Sherlock, Femida, Defender, Marketer, Financier, Health)

---

## 1. Проблема

Текущие скиллы Hermes — статичны, привязаны к профилю, не обновляются автоматически. Нужна динамическая библиотека, где:
- Агенты **не скачивают** всю библиотеку (50MB+), а обращаются к каталогу
- Каждая задача → агент **читает актуальные скиллы** из внешних источников
- Автосинхронизация раз в сутки через cron

---

## 2. Решение

**Skill Library v2** — федеративная модель:

```
dailyprompts.ru/feed.json  +  GitHub (coreyhaines31/marketingskills + др.)
        ↓
   Синхронизатор (cron 03:00 МСК)
        ↓
   ~/freelance-2026/vault/06-Library/skills-catalog/
        ↓
   Кэш в ~/.hermes/profiles/personal/cache/skills/
        ↓
   Агенты → skill_view(tag=#marketing) → читают только нужные
```

**Теги-агенты:**
| Agent | Tag | Primary Source |
|-------|-----|----------------|
| Marketer | `#marketing` | `coreyhaines31/marketingskills` (50+ skills) |
| Sherlock | `#research` | `simonw/llm` + `dailyprompts.ru/research` |
| Femida | `#legal` | `femida-skills` (создадим) |
| Defender | `#security` | `ai-defender-skills` (создадим) |
| Financier | `#finance` | `financier-skills` (создадим) |
| Health | `#health` | `health-skills` (создадим) |

---

## 3. Синхронизатор

**Расположение:** `freelance-2026/projects/skill-library-bridge/`
**Cron:** `0 3 * * *` (ежедневно 03:00 МСК)
**Действия:**
1. Fetch `catalog.json` из источников
2. Pull только `.md` скиллов, обновлённых за 24ч
3. Парсинг → `digest.md` + обновление `_catalog.md`
4. Кэш для офлайн-режима

---

## 4. Интеграция с агентами

Маркетолог:
```python
# В задаче "SEO-аудит Levitan"
skills = skill_library.query(tag="#marketing", topic="seo-audit")
# → получает: seo-audit, ai-seo, schema, programmatic-seo
for skill in skills:
    read_skill(skill)
apply_strategy()
```

---

## 5. Статус

- [x] ADR создан
- [ ] Синхронизатор
- [ ] Cron
- [ ] Интеграция с Маркетологом
- [ ] Расширение на 5 остальных агентов