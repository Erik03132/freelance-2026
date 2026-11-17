---
type: wiki
tags: [multi-agent, expert-council, sinergy, femida, defender, marketer, financier, sherlock, health]
status: done
updated: 2026-11-17
sources: [06-Library/es-n-multiagent-gateway/digest.md, 06-Library/sinergy-expert-council/digest.md]
---

# Совет 6 экспертов (Expert Council)

Источники: `06-Library/es-n-multiagent-gateway/digest.md` (2026-08-23) и `06-Library/sinergy-expert-council/digest.md` (2026-08-23, текст частично повреждён — см. ниже).

## Состав

| Эксперт | Профиль | Зона ответственности |
|---|---|---|
| Femida | `femida` | Право, договоры, NDA, риски 152-ФЗ / GDPR, тендеры 44/223-ФЗ |
| Defender | `defender` | Безопасность, .env, утечки, OWASP, зависимости, PII |
| Marketer | `marketer` | Позиционирование, офферы, SEO/GEO/AEO, воронки, копирайтинг |
| Financier | `financier` | Юнит-экономика, смета, ROI, риски неоплаты, ценообразование |
| Sherlock | `sherlock` | Рынок, конкуренты, валидация гипотез, поиск вакансий |
| Health | `health` | MedTech, эргономика, режим труда, стресс-тест ограничений |

Шесть ролей совпадают с картой агентов в `skill-library-v2` (там же теги скиллов).

## Формула вызова

Параллельный опрос через `delegate_task`: по одной задаче на эксперта, в `context` — SOUL профиля плюс данные, `role: leaf`. Эксперты не видят друг друга и не влияют на ответы.

## Формат вердикта

1. Тема/задача, уровень риска: Low / Medium / High / Strategic.
2. Шесть вердиктов: рынок, право и красные линии, уязвимости, оффер и аудитория, бюджет/сроки/ROI, факторы нагрузки.
3. Резюме координатора: решение ДЕЛАЕМ / КОРРЕКТИРУЕМ / ОТКЛОНЯЕМ, 1–2 главных стоп-фактора, первые 3 конкретных шага.

Сила схемы: разные эксперты дают несовместимые возражения (например, финансы «дорого» против маркетинга «надо»), и координатор обязан выбрать, а не усреднить.

## Пайплайн Sinergy

Из уцелевшего текста дайджеста: идея описывается в `brief.md` → `POST /api/sinergy/expert-council` → те же 6 экспертов через `delegate_task` с `SOUL.md` → результат пишется в `projects/sinergy/ideas/<id>/verdict.md` → UI `/sinergy/analysis/[id]`. Вердикт: GO / NO-GO / REWORK плюс первые 3 шага.

## Оговорка по источнику

`sinergy-expert-council/digest.md` повреждён: кириллица в большинстве строк потеряна, читаются только структура, латиница и цифры. Поэтому детали (формулировки полей brief.md, критерии GO/NO-GO) здесь не восстановлены. Полный текст — в `vault/04-Decisions/2026-08-23-sinergy-expert-council-pipeline.md` (в HMS-1 не читался, вне области 06-Library).

## Связанные документы (по ссылкам самих дайджестов)

`vault/04-Decisions/2026-08-23-es-n-telegram-gateway-council.md`, `vault/03-Lessons/2026-08-23-es-n-multiagent-gateway-lessons.md`, `vault/03-Lessons/2026-08-23-sinergy-council-lessons.md`.
