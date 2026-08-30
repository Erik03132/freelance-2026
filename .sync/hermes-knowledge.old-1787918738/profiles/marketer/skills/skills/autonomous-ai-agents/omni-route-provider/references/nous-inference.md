# Nous Research Inference — подключение через OmniRoute (проверено 2026-08-19)

## Что это
Nous Research Inference API — OpenAI-совместимый бэкенд. Доступен по подписке/кредитам
на `portal.nousresearch.com`. Это «Ромес Агент» / Hermes Agent от Nous (сервис, в котором
сидит пользователь). Можно юзать и напрямую из скриптов/агентов, и завести как ноду в
локальный OmniRoute, чтобы модели появились в OpenCode.

## Эндпоинт и авторизация
- **Base URL:** `https://inference-api.nousresearch.com/v1`
- **Auth:** `Authorization: Bearer <sk-nous-...>` (один ключ на весь аккаунт, работает для
  всех моделей — НЕ «один ключ на одну модель», как кажется из сниппета портала).
- **OpenAI SDK:** `OpenAI(base_url="https://inference-api.nousresearch.com/v1", api_key=...)`

## Реальные ID моделей (из `/v1/models`, не из док-заглушки!)
| Модель | ID для запроса | Контекст | Цена $/1M (in/out) |
|--------|----------------|----------|---------------------|
| Hermes 4 70B | `nousresearch/hermes-4-70b` | 128k | 0.05 / 0.20 |
| Hermes 4 405B | `nousresearch/hermes-4-405b` | 128k | 0.09 / 0.37 |

Доки на сайте пишут `Hermes-4-70B` — НЕВЕРНО, в API реальный ID со строчной `nousresearch/...`.
Всего через API доступно ~370 моделей (вкл. бесплатные: `meituan/longcat-2.0:free` и др.).

## Параметры запроса (OpenAI-совместимые)
- `max_tokens`: 1–32000
- `temperature`: 0–2
- `stream`: true/false
- `messages`: roles `system`/`user`/`assistant`

## Reasoning (Hermes 4 hybrid)
Включить глубокое мышление — системный промпт:
`You are a deep thinking AI, you may use extremely long chains of thought... enclose
thoughts inside <think> </think> tags...`
Для Hermes 4 reasoning-вывод приходит в поле `reasoning_content` (если не префиксовать
тег), либо между `<think>` в content (если префиксовать).

## Быстрый smoke-тест (прямой, минуя OmniRoute)
```bash
curl -s --max-time 25 https://inference-api.nousresearch.com/v1/chat/completions \
  -H "Authorization: Bearer <sk-nous-...>" -H "Content-Type: application/json" \
  -d '{"model":"nousresearch/hermes-4-70b","messages":[{"role":"user","content":"ping"}],"max_tokens":16}'
```
Возвращает `choices[0].message.content` = `pong` → ключ и эндпоинт живы.

## Завести в OmniRoute (обход сломанного `nodes add`)
См. SKILL.md раздел «Добавление внешнего провайдера». Коротко:
1. Прямой `INSERT` в `~/.omniroute/storage.sqlite`, таблица `provider_nodes`:
   - `type=openai`, `api_type=openai-compatible`, `prefix=nous`
   - `base_url=https://inference-api.nousresearch.com/v1`
   - `chat_path=/v1/chat/completions`, `models_path=/v1/models`
   - `custom_headers_json={"Authorization":"Bearer <sk-nous-...>"}`
2. Зарегистрировать модели в `~/.config/opencode/opencode.jsonc`
   (`provider.omni-auto.models`): `"nous/nousresearch/hermes-4-70b": {...}` и `...405b`.
   Вызываются как `omni-auto/nous/nousresearch/hermes-4-70b`.

## Лимиты (платный аккаунт по умолчанию)
180 RPM, 720 000 TPM.

## Безопасность ключей
- `sk-nous-...` — секрет. Не коммитить, не светить в чат (если засветил — отозвать и
  сгенерить новый в portal.nousresearch.com).
- OmniRoute-ключ (`OMNIROUTE_API_KEY`, формат `sk-e354...`) — тоже секрет, он даёт доступ
  к локальному management-API роутера.
