# project_context — справочник инфраструктуры и провайдеров

Здесь лежат данные для принятия решений по инфраструктуре Hermes Agent.

## Файлы

| Файл | Что |
|---|---|
| `vps_pricing.md` | Детальные цены TimeWeb (pay-per-use JSON-расшифровка, 2026-09-01) |
| `vps_provider_comparison.md` | **Сравнение TimeWeb vs Beget vs Selectel** (тарифы, фичи, рекомендации, чеклист миграции) |

## Быстрый поиск

- **Цены Beget** → `vps_provider_comparison.md` #Beget
- **Тарифы TimeWeb** → `vps_pricing.md`
- **Миграция — что проверить** → `vps_provider_comparison.md` #research-чеклист
- **SSoT инфраструктуры** → `INFRA_SSOT_OMNIROUTE_HERMES.md` (корень воркспейса)
- **Активные задачи** → `ACTIVE_TASKS.md`

## При миграции с TimeWeb на Beget

1. Читай `vps_provider_comparison.md` #research-чеклист — список того, что нужно проверить/перенести
2. Актуализируй `INFRA_SSOT_OMNIROUTE_HERMES.md` (новый IP, HERMES_HOME)
3. Обнови `ACTIVE_TASKS.md`: TW-001/TW-002 (Timeweb S3) → переход на Beget S3
4. Пересобери tunnel Mac↔Beget
