---
name: omni-route-provider
description: "Configure OmniRoute provider for Hermes Agent model routing."
version: 1.1.0
author: Igor Vasin
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [hermes, provider, configuration, omniroute, omni-route]
    related_skills: [hermes-agent]
---

# OmniRoute Provider

## When to Use This Skill

Use this skill when:
- Нужно настроить единственный провайдер OmniRoute вместо нескольких
- Работают только определенные модели (например, Neus), но не другие
- Нужно объединить модели OpenCode Zen, OpenRouter и Orca в одну точку доступа
- Остальные провайдеры не работают из-за конфликтов или неправильной маршрутизации

## Что это?

OmniRoute — кастомный провайдер модели, объединяющий несколько LLM сервисов:
- OpenCode Zen
- OpenRouter
- Orca

**Base URL:** `http://127.0.0.1:20128/v1`
**Key Env:** `OMNI_API_KEY`

## Быстрая настройка

```bash
# Установить OmniRoute как единственный провайдер
hermes config set model.provider omniroute
hermes config set model.default "auto/best-coding"
```

## Доступные модели

| Модель | Описание |
|--------|----------|
| `auto/free-coding` | 🆓 Free Coding — комбинация OC Zen + OR + Orca (бесплатные варианты) |
| `auto/best-coding` | 🏆 Best Coding — топ общепромышленная модель для кодинга |

## Полная конфигурация

```yaml
model:
  provider: omniroute
  default: auto/best-coding
  base_url: http://127.0.0.1:20128/v1
  key_env: OMNI_API_KEY

providers:
  omniroute:
    name: OmniRoute (OpenCode Zen + OpenRouter + Orca)
    base_url: http://127.0.0.1:20128/v1
    key_env: OMNI_API_KEY
    discover_models: true
    models:
      auto/free-coding:
        name: '🆓 Free Coding (combo: OC Zen + OR + Orca)'
      auto/best-coding:
        name: 🏆 Best Coding (top general-purpose coding combo)
```

## Работа с несколькими провайдерами

### Проблема: "работает только Neus, остальные провайдеры не работают"

Причина может быть в конфликте провайдеров или неправильной маршрутизации запросов.

**Решение:** Оставить только OmniRoute как единственный провайдер:

1. Удалить конфликтующие провайдеры (openrouter, anthropic, dunno и др.)
2. Оставить только OmniRoute

```bash
# Удалить секцию excluded_providers (чтобы не блокировать провайдеры)
hermes config set model_catalog.excluded_providers '[]'

# Установить OmniRoute
hermes config set model.provider omniroute
hermes config set model.default "auto/best-coding"
```

## Проверка настройки

```bash
hermes config get model.provider
hermes config get model.default
```

Ожидаемый вывод:
```
omniroute
auto/best-coding
```

## Добавление внешнего провайдера (Nous, и др.) — РАБОЧИЙ путь

> ⚠️ **`omniroute nodes add` СЛОМАН в v3.8.48 (и, похоже, в 16.2.10).** Опция
> `--base-url` объявлена одновременно глобально (для самого роутера) и локально
> (для ноды), commander путается, и `nodes add` ВСЕГДА падает с
> `error: required option '--base-url <url>' not specified` — при любом синтаксисе
> (пробованы: `--base-url url`, `--base-url=url`, через глобальный `--base-url ДО
> подкоманды, через `OMNIROUTE_BASE_URL` env, через `OMNIROUTE_NODE_BASE_URL`).
> `nodes list` / `nodes update` / `nodes test` работают — только `add` заблокирован.

**Обход (проверено 2026-08-19): прямая запись в БД OmniRoute.**
`nodes add` — лишь обёртка над `INSERT INTO provider_nodes`. Схема таблицы:
```sql
CREATE TABLE provider_nodes (
  id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL,
  prefix TEXT, api_type TEXT, base_url TEXT, chat_path TEXT,
  models_path TEXT, custom_headers_json TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, icon_url TEXT
)
```
Рабочий INSERT (Пример: Nous Inference, OpenAI-совместимый):
```python
import sqlite3, json, os
db = os.path.expanduser("~/.omniroute/storage.sqlite")
now = "2026-08-19T00:00:00Z"   # datetime.utcnow().isoformat()+"Z"
con = sqlite3.connect(db); c = con.cursor()
c.execute("""INSERT OR REPLACE INTO provider_nodes
 (id,type,name,prefix,api_type,base_url,chat_path,models_path,custom_headers_json,created_at,updated_at,icon_url)
 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
 ("nous-inference","openai","Nous Research Inference","nous","openai-compatible",
  "https://inference-api.nousresearch.com/v1",
  "/v1/chat/completions","/v1/models",
  json.dumps({"Authorization":"Bearer <sk-nous-...>"}), now, now, None))
con.commit(); con.close()
```
После INSERT нода сразу видна: `omniroute nodes list` (нужен `OMNIROUTE_API_KEY`).
`nodes test` может вернуть `405` — это баг CLI-метода теста, не признак поломки ноды.

**Где OpenCode берёт OmniRoute (реальная связка):**
НЕ в `~/.config/opencode/config.toml` (там часто старый бэкап, вроде Kimi).
Рабочий биндинг — `~/.config/opencode/opencode.jsonc`:
```jsonc
"provider": { "omni-auto": {
  "name": "OmniRoute",
  "npm": "@ai-sdk/openai-compatible",
  "options": { "baseURL": "http://127.0.0.1:20128/v1", "apiKey": "${env:OMNI_API_KEY}" },
  "models": { "auto/free-coding": {"name":"🆓 Free Coding"}, ... }
}}
```
Чтобы новая модель появилась в OpenCode, ДОБАВЬ её имя в `provider.omni-auto.models`:
```jsonc
"nous/nousresearch/hermes-4-70b":  { "name": "🔥 Nous Hermes 4 70B" },
"nous/nousresearch/hermes-4-405b": { "name": "🔥 Nous Hermes 4 405B" }
```
Тогда вызывается как `omni-auto/nous/nousresearch/hermes-4-70b`.
Имя модели = `prefix` ноды + `/` + реальный model-id из `/v1/models` провайдера.

**Проверка, что нода живая (не забудь `--noproxy`!):**
`curl` на `127.0.0.1` без `NO_PROXY`/`--noproxy '*'` уходит в SOCKS5-прокси →
`http_code=000`. Правильно:
```bash
curl --noproxy '*' -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $OMNI_API_KEY" \
  http://127.0.0.1:20128/v1/models
```
Подробности и провайдер-специфика — `references/nous-inference.md`.