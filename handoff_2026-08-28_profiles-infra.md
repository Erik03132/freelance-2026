# HANDOFF — 2026-08-28 (профили + инфра LLM)

## Контекст
Сессия началась с прогона `start_day.sh` и разбора здоровья инфры. Основной
фокус сместился на **приведение конфигов профилей Hermes к единому SSoT** и
**разъяснение Игорю архитектуры профилей** (он путался в 3 слоях «профиль»).

## Что сделано (verified)

### 1. SSoT профилей — ЕДИНЫЙ LLM-шаблон
Все 11 воркспейс-профилей (`~/.hermes/profiles/*`) приведены к:
```yaml
model:
  provider: omniroute
  default: auto/free-coding-full
  base_url: http://127.0.0.1:20128/v1
  key_env: OMNI_API_KEY
  aliases:
    best-coding: omniroute/auto/free-coding-full
    free-coding: omniroute/auto/free-coding-full
```
- Убраны дубликаты `auto/free-coding-full`, прокинуты aliases во все профили.
- `bridge` получил `providers.omniroute.models` (был только fallback_providers).
- `personal` — сохранён отдельный `key_env: HERMES_CUSTOM_OMNIROUTE_API_KEY`.
- Валидатор `tools/ops/validate_profiles.py`: **11/11 ✅, 0 нарушений**.

### 2. Доки (SSoT-карта)
- `docs/PROFILES.md` — 3 слоя профилей (платформенный / воркспейс / TG-роль) +
  канонический шаблон + таблица назначений.
- `tools/ops/validate_profiles.py` — валидатор (exit 1 при нарушениях).
- `start_day.sh` исправлен: чекает `auto/free-coding-full` (не мёртвый `auto/free-coding`)
  + добавлены проверки Ollama (11434) и Nous-provider (inference-api.nousresearch.com).

### 3. Провайдеры добавлены во ВСЕ профили
Поверх `omniroute` добавлены отдельные провайдеры:
- `nous` — все 14 моделей (hy3:free, laguna-*, Hermes-4-70B/405B и т.д.)
- `ollama` — `qwen2.5:1.5b`, `qwen2.5:0.5b`, `nomic-embed-text`

### 4. Профиль `chief` — расширен под проектную работу
Добавлен отдельный провайдер `openrouter` (только в chief):
- 35 free-моделей `openrouter/*:free` (fallback если Omni отвалится)
- платные: `orcarouter/google/gemini-3.6-flash`, `gemini-3.5-flash`,
  `gemini-3-pro-image-preview` + `opencode-zen/gemini-3.7-flash`
- `OPENROUTER_API_KEY` присутствует в `~/.hermes/.env` ✅
- chief теперь = 4 провайдера (omniroute + nous + ollama + openrouter)

### 5. Обучение Игоря (разобраны вопросы)
- Почему каша: «профиль» = 3 разных слоя. Решено через `docs/PROFILES.md`.
- Переключение: `hermes profile use <name>` (sticky), сессии изолированы по профилям.
- Контекстное окно `auto/free-coding-full` = **128K** (не 1M; 1M у платных `best-*`).
- Процедура завершения сессии: **НЕ `sync`** (sync=только скиллы), а
  `--resume`/`--continue` или **handoff-файл** для чистого старта с контекстом.

## Открытые пункты (не закрыты)

1. **`qwen2.5:7b` НЕ докачан** — `ollama pull` упал на 30% (connection reset by peer,
   1.4/4.7GB). Нужен повтор `ollama pull qwen2.5:7b` (с VPN/стабильным каналом).
   Сейчас локально только `qwen2.5:1.5b` и `qwen2.5:0.5b`.

2. **US-прокси для omniroute НЕ прокинут** (Игорь запретил трогать сеть).
   `auto/free-coding-full` реально отвечает ТОЛЬКО когда VPN включён вручную
   (formward 64468 закрыт, omniroute не видит системный VPN). Без VPN комбо виснет 31s.

3. **Платные Nous-модели в omniroute отсутствуют** — каталог отдаёт только `:free`.
   Если нужен платный Nous-путь, надо отдельно прописывать key+модели.

4. **`gemini-3.7-flash` через чистый OpenRouter НЕТ** в каталоге (есть
   `opencode-zen/gemini-3.7-flash` и `orcarouter/google/gemini-3.6-flash`).
   Прописал оба варианта в chief, но чистого `openrouter/google/gemini-3.7-flash` нет.

## Следующий шаг (для новой сессии)
Продолжить: `hermes chat --continue` (эта сессия) ИЛИ начать новую и сказать
«продолжи по handoff_2026-08-28_profiles-infra.md».
Приоритет: добить `ollama pull qwen2.5:7b` (п.1) и решить вопрос US-прокси (п.2).

## Бэкапы
- `~/freelance-2026/backups/profiles_llm_unify_20260828/` — до унификации
- `~/freelance-2026/backups/profiles_providers_20260828/` — до добавления провайдеров
