# Handoff 2026-08-30 — настройка всех профилей Hermes на free-модель (Nous laguna)

**Статус:** основная задача ВЫПОЛНЕНА (все профили VPS+Мак на `nous/poolside/laguna-s-2.1:free`),
но в конце сессии вылезла новая проблема (решена) — см. «ПОСЛЕДНЯЯ ПРОБЛЕМА».

## ГЛАВНЫЙ УРОК (читать первым!)

**VPS-gateway читает конфиги из `HERMES_HOME=/srv/hermes/.hermes`,
а НЕ из `/root/.hermes`!**

- `/root/.hermes` на VPS — это КОПИЯ/неиспользуемый путь. Правки туда НЕ применяются к живому gateway.
- Всегда править: `/srv/hermes/.hermes/config.yaml` и `/srv/hermes/.hermes/profiles/*/config.yaml`.
- Проверить текущий HOME: `cat /proc/$(pgrep -f "gateway run")/environ | tr '\0' '\n' | grep HERMES_HOME`

## Что сделано (fact-checked, не галлюцинация)

### 1. Поиск/исправление путей
- Найдено, что gateway живёт в `/srv/hermes/.hermes` (env `HERMES_HOME`).
- Починен коннект VPS-gateway: возвращён валидный токен `882055` (`@hermes03132`, проверено `getMe=True`),
  убран мёртвый `895390` (rejected by server) из femida `.env`, femida убран из VPS-multiplex (живёт на Маке launchd).

### 2. Пришивка laguna (во все профили + root)
- `model.provider: omniroute`, `model.default: nous/poolside/laguna-s-2.1:free`
  во всех 11 профилей VPS (`/srv/hermes/.hermes`) + root.
- То же на Маке (`/Users/igorvasin/.hermes`) — все 12 профилей + root.
- MOA-агрегаторы переведены на laguna.

### 3. Чистка мусора
Удалено из `providers.*.models`, `model.default`, `fallback_providers`, `moa.*`:
- `nous/Hermes-4-70B`, `nous/Hermes-4-405B` (несуществующие модели)
- `openrouter/stealth/ox-alpha` (запрещённый ES-28 stealth-провайдер)
- платные `deepseek-v4-flash-free`, `openrouter/google/gemini-3.7-flash`
- `auto/free-coding`, `auto/best-coding`, `auto/free-coding-full`, `hy3-free`, `nemotron*`

### 4. ПОСЛЕДНЯЯ ПРОБЛЕМА (решена в конце сессии)
Бот выдавал `Model 'auto/free-coding' is not a valid combo` (HTTP 400) даже после правки
`model.default`. Причина: `auto/free-coding` висел во ВЛОЖЕННЫХ секциях (moa reference_models,
custom provider models, profile-specific model-блоки), которые первый скрипт не трогал, плюс
в `provider_models_cache.json` (кэш моделей).

Исправлено:
- Рекурсивная чистка всех `*.yaml` в `/srv/hermes/.hermes` (замена строковых значений `auto/free-coding`
  → `laguna`, удаление bad-ключей в словарях).
- Докрутка `omniroute/auto/free-coding` в batrak/english-tutor (ключ `free-coding`).
- Сброс `provider_models_cache.json` (truncate → gateway перестроил).
- Рестарт gateway. Итог: 0 ошибок `auto/free-coding` в свежем логе, все профили = laguna.

## Проверено (real)
- ✅ `curl http://127.0.0.1:2223/v1/models` (VPS-OmniRoute через туннель 2223) = 200.
- ✅ `nous/poolside/laguna-s-2.1:free` через VPS-OmniRoute отвечает («I'm poolside Malibu»),
  хотя иногда transient 429 (лимиты free-слоя).
- ✅ Токен `882055` валиден, gateway active, `@hermes03132` коннектится.
- ✅ Все профили VPS = `omniroute/nous/poolside/laguna-s-2.1:free` (проверено по факту).

## НЕ проверено / открытые вопросы
- ⚠️ Качество ответа free-модели: `laguna-s:free` галлюцинирует на сложных/наводящих промптах
  (ахинея про «RPM-пакеты Neous»). Это ограничение free-слоя, не баг конфига.
  Для серьёзных задач (Фемида-юр) нужна платная модель — вне политики free-only Игоря.
- ⚠️ Реальный E2E-ответ бота в ТГ не проверялся агентом (бот не получает свои сообщения как входящие).
  Игорь должен написать `@hermes03132_bot` и убедиться, что заголовок сессии = laguna, ответ без мусора.
- ⚠️ Дашборд Мака (:9120/Profiles) мог показывать stale `hy3-free` — обновляется после Restart Gateway.

## Туннель / доступ (актуально)
- SSH: `ssh -p 2222 root@127.0.0.1` (туннель 2222→VPS:22, добавлен Игорем в handoff).
- VPS-OmniRoute: `http://127.0.0.1:2223/v1/...` (туннель 2223→VPS:20128).
- VPS IP: 217.149.23.113 (TimeWeb). US-прокси для исх. VPS→зарубеж: 172.120.21.141:64468.

## Бэкапы (откат при необходимости)
- VPS `/srv/hermes/.hermes/*.yaml.bak_1788108744` (после пришивки laguna)
- VPS `/srv/hermes/.hermes/*.yaml.bak_1788108...` (после финальной чистки auto/free-coding) — см. `ls /srv/hermes/.hermes/config.yaml.bak_*`
- VPS root config откат токена: `/root/.hermes/config.yaml.broken_*` и `*.bak_1788105301`
- Мак: `/Users/igorvasin/.hermes/**/*.yaml.bak_1788108426`

## ПЕРВЫЙ ШАГ (новая сессия)
1. `ssh -p 2222 root@127.0.0.1` → проверить `systemctl is-active hermes-gateway` (должен быть active).
2. Написать `@hermes03132_bot` в ТГ → должен ответить на laguna, заголовок `Model: nous/poolside/laguna-s-2.1:free`.
3. Если ахинея/ошибки — см. «Открытые вопросы»; смотреть `journalctl -u hermes-gateway -n 50`.
4. Дашборд Мака (:9120) — если stale, нажать Restart Gateway.

## Файлы состояния обновлены
- `SESSION_LATEST.md` — блок «ДОБИТО (сессия 30.08 вечер)».
- `ACTIVE_TASKS.md` — блок «🔴 P0 30.08 (вечер) — все профили на free-модель (Nous laguna)».
