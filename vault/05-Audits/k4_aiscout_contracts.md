# K4: Контракты AI-Scout (Collector/Analyst/Curator) — проверка 08.08.2026

## Текущее состояние

`backend/src/content-pipeline.ts` (442 строки) — монолитный пайплайн из 7 шагов:
`fetch → normalize → score → deduplicate → cluster → generate → export`.

Контракты на уровне **типов** есть:
- `NormalizedContent` (17) — выход шага fetch/normalize (вход для score)
- `ScoredContent extends NormalizedContent` (33) — выход score (вход для cluster)
- `ClusteredContent` (44) — выход cluster

Явных **функциональных контрактов** (PASS-критерии на шаг, STOP-коды) НЕТ —
шаги соединены последовательно без валидации.

## Проверка контрактов

| Агент | Роль в плане | Вход | Выход | Критерий | Статус |
|-------|-------------|------|-------|----------|--------|
| Collector | fetch+normalize | источники (habr/medium/twitter/tg) | `NormalizedContent[]` | есть тип | ✅ тип, ❌ PASS-критерий |
| Analyst | score+dedupe+cluster | `NormalizedContent[]` | `ScoredContent[]` → `ClusteredContent[]` | есть тип | ✅ тип, ❌ PASS-критерий |
| Curator | generate+export | `ClusteredContent[]` | digest/alert/trending | тип частичный | ⚠️ частично |

## Вывод

**Контракты на вход/выход = ЕСТЬ (типы). Контракты на критерии = НЕТ.**

Это важно для отказоустойчивости: шаг score при пустом входе вернёт `[]`, шаг generate
сгенерирует пустой дайджест — и никто не «покраснеет» (правило LV-4: проверка должна
уметь краснеть).

## Рекомендация

Добавить в content-pipeline.ts PASS-гейты (мини-валидаторы) между шагами:
1. После fetch: `if (normalized.length === 0) throw new Error('Collector: empty')` + лог.
2. После score: `scored = scored.filter(s => s.score > threshold)` — если 0, пометить «NO_TRENDING».
3. После generate: проверка непустого тела дайджеста перед export.

Это соответствует K1-оркестратору (orchestrator_table.py) — единый паттерн гейтов.

**Статус:** K4 проверен. Гейты — интеграция в content-pipeline.ts при следующем релизе ai-scout.