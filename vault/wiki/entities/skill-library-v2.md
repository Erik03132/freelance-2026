---
type: wiki
tags: [skills, skill-library, hermes, tags, sync, architecture]
status: done
updated: 2026-11-17
sources: [06-Library/skill-library-v2/digest.md, 06-Library/skills-catalog/catalog.json]
---

# Skill Library v2: федеративная библиотека скиллов по тегам

Источник: `06-Library/skill-library-v2/digest.md` (2026-08-23). Это проектное описание, не отчёт о работающей системе — см. «Состояние».

## Идея

Статические скиллы, привязанные к профилю, заменяются федеративной библиотекой по тегам: внешние источники (GitHub + dailyprompts.ru) → sync worker (cron 03:00 MSK) → `vault/06-Library/skills-catalog/` → кеш `~/.hermes/profiles/personal/cache/skills/` → агент запрашивает по тегу и грузит только нужное.

## Карта агент → тег → источник

| Агент | Тег | Основной источник |
|---|---|---|
| Marketer | `#marketing` | `coreyhaines31/marketingskills` (50+ скиллов) |
| Sherlock | `#research` | `simonw/llm` + `dailyprompts.ru/research` |
| Femida | `#legal` | собственные `femida-skills` |
| Defender | `#security` | собственные `ai-defender-skills` |
| Financier | `#finance` | собственные `financier-skills` |
| Health | `#health` | собственные `health-skills` |

## Пять принципов

1. Не скачивать всё: агент берёт только скиллы под теги задачи.
2. Всегда свежее: ежедневная синхронизация по cron.
3. Офлайн-кеш: локальная копия на случай недоступности источника.
4. Сохранять кросс-ссылки: граф зависимостей скиллов не теряется.
5. `product-marketing.md` — общий контекстный фундамент (по паттерну marketingskills).

## Состав marketingskills

50+ скиллов в 8 категориях: SEO и контент (seo-audit, ai-seo, programmatic-seo, schema, content-strategy, link-building, aso, site-architecture), CRO, контент и копирайтинг, paid и measurement, growth и retention, стратегия и монетизация, sales/revops, PR. Установка заявлена как `npx skills add coreyhaines31/marketingskills`, но в проекте планировался собственный Hermes-мост.

## Состояние на 2026-11-16 (факт, не план)

- `06-Library/skills-catalog/catalog.json`: `{"updated": "2026-11-16T14:45:26Z", "skills": []}` — каталог пуст.
- Sync worker и мост `projects/skill-library-bridge/` в библиотеке не описаны как сделанные.
- `gh-weekly-2026-10-20` (2026-10-20) фиксирует, что `npx skills add` упал с E407, и скиллы ставились вручную из другого набора (`mattpocock/skills`), см. `oss-weekly-2026-10`.

## Вывод

Читать как архитектурный замысел: теги вместо профилей, кеш вместо полной загрузки. Реализации на 2026-11-17 нет; в работе — локальные папки скиллов. Расхождение плана и факта — `contradictions.md`, п.2.

## Связанное

`hermes-profiles` (SOUL и кеш профилей), `expert-council` (те же 6 ролей), `oss-weekly-2026-10` (что фактически установлено в октябре).
