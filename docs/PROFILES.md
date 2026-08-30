# PROFILES.md — Единая карта профилей (SSoT)

> Каша с профилями возникала, потому что слово «профиль» означает 3 разные вещи,
> и воркспейс-профили правились ad-hoc без шаблона. Этот файл — источник истины.

## Три слоя «профиля» (НЕ путать)

| Слой | Где живёт | Что это | Примеры |
|------|-----------|---------|---------|
| **A. Платформенные** | внутри приложения Hermes | дефолтные профили самого агента | `default`, `hermes-agent`, `desktop`, `tg-bot` |
| **B. Воркспейс-профили** | `~/.hermes/profiles/<name>/` | твои бандлы: LLM-конфиг + навыки + память + SOUL | `chief`, `batrak`, `femida`, … (11 шт) |
| **C. TG-роли** | меню `@hermes03132_bot` (VPS) | роль поверх воркспейс-профиля | Шерлок, Батрак, Айболит, Фемида |

**Правило:** когда спрашиваешь «какой профиль», уточняй слой. Текущий чат-агент
(десктоп) сам по себе сидит в платформенном `default` (слой A), а воркспейс-профиль
(слой B) переключается командой `/profile <name>` или в UI.

## Канонический шаблон воркспейс-профиля (слой B)

ЕДИНЫЙ формат. Любое отклонение = ошибка (проверяет `tools/ops/validate_profiles.py`):

```yaml
model:
  provider: omniroute
  default: auto/free-coding-full
  base_url: http://127.0.0.1:20128/v1
  key_env: OMNI_API_KEY
  aliases:
    best-coding: omniroute/auto/free-coding-full
    free-coding: omniroute/auto/free-coding-full
providers:
  omniroute:
    name: OmniRoute (OpenCode Zen + OpenRouter + Orca)
    base_url: http://127.0.0.1:20128/v1
    key_env: OMNI_API_KEY
    discover_models: true
    models:
      auto/free-coding-full:
        name: 🏆 Best Coding (top general-purpose coding combo)
```

- `auto/free-coding-full` — ЕДИНСТВЕННОЕ актуальное free-комбо (требует US-прокси у omniroute).
- Дубликаты моделей (`auto/free-coding-full` встречается 2+ раза) — запрещены.
- `provider` всегда `omniroute` (локальный `:20128`). Прямые `opencode`/`opencode-free` — не использовать.
- `personal` сохраняет свой `key_env: HERMES_CUSTOM_OMNIROUTE_API_KEY` (отдельный ключ) — это допустимое исключение.

## Воркспейс-профили (слой B) — назначение

| Профиль | Роль / назначение | TG-роль (слой C) |
|---------|-------------------|------------------|
| `chief` | Chief oversight, координация задач | — |
| `batrak` | Отклики на кворки/вакансии (1500₽/ч) | Батрак |
| `sherlock` | Поиск вакансий (hh.ru) | Шерлок |
| `femida` | Юр-/эксперт-разбор | Фемида |
| `defender` | Безопасность/аудит | — |
| `health` | Здоровье (без диагнозов) | Айболит |
| `marketer` | Маркетинг/проДвижение | — |
| `financier` | Финансы/бюджет | — |
| `english-tutor` | Тьютор английского | — |
| `bridge` | Мост/каскады моделей (имеет fallback-провайдеры) | — |
| `personal` | Личный/экспериментальный (отдельный ключ) | — |

## Контроль
- `tools/ops/validate_profiles.py` — проверяет все профили слоя B на соответствие шаблону.
- Запускать после любой правки профиля. CI-гейт в будущем — по желанию.
