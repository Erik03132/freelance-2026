# Уроки: Универсальная библиотека скиллов (Skill Library v2)

**Дата:** 2026-08-23  
**Проект:** `freelance-2026` / Hermes Agent / 6 экспертов  
**Связанный ADR:** `vault/04-Decisions/2026-08-23-skill-library-v2.md`

---

## 1. Не качаем — читаем

Идея Игоря: агенты **не скачивают** библиотеки, а обращаются к каталогу по тегам.
- Экономия токенов и места
- Всегда свежие скиллы
- Авто-обновление через cron

---

## 2. product-marketing — фундамент

В `marketingskills` все скиллы считывают `product-marketing.md` первым.
→ У нас должен быть единый `.agents/product-marketing.md` на уровне проекта.

---

## 3. Кросс-ссылки между скиллами

`marketingskills` использует явные `Related Skills`:
- `copywriting ↔ cro ↔ ab-testing`
- `revops ↔ sales-enablement ↔ cold-email`
- `seo-audit ↔ schema ↔ ai-seo`
→ Наш синхронизатор должен сохранять этот граф.

---

## 4. Версионирование

Репо использует `VERSIONS.md` + релизы на GitHub.
→ Синхронизатор должен отслеживать `updated_at` каждого скилла.

---

## 5. Установка через `npx skills`

Официальный CLI: `npx skills add coreyhaines31/marketingskills`
→ Для Hermes делаем свой bridge, не зависим от CLI.