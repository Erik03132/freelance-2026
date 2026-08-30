# Telegram Bots — Working Configuration (SSoT)

> **Статус: ВСЕ 6 БОТОВ ЖИВЫ И ОТВЕЧАЮТ** (зафиксировано 2026-08-30).
> Токены хранятся ТОЛЬКО в `~/.hermes/profiles/<profile>/.env` (или `~/.hermes/config.yaml` для personal).
> Никакие секреты не коммитятся — здесь только маски.

## Бот → Профиль → Токен (маска)

| Бот | Профиль | Токен (маска) | Гейтвей | Pairing |
|-----|---------|---------------|---------|---------|
| @hermes03132_bot | `personal` | `8820559136…qjIw` | ✅ | ✅ |
| @femida03132_bot | `femida` | `8953909042…fucY` | ✅ | ✅ |
| @market03132_bot | `marketer` | `8865204388…L3Uk` | ✅ | ✅ |
| @sher03132_bot | `sherlock` | `8564093096…9Q3c` | ✅ | ✅ |
| @finans03132_bot | `financier` | `8922868309…yoNA` | ✅ | ✅ |
| @batrak03132_bot | `batrak` | `8638160916…yG9s` | ✅ | ✅ |

- Каждый бот = отдельный профиль Hermes с собственным `TELEGRAM_BOT_TOKEN`. Один токен НЕ шарится между ботами.
- `personal` — токен в корневом `~/.hermes/config.yaml` (`gateway.telegram.token`), остальные — в `profiles/<p>/.env`.

## Архитектура

- Каждый бот = отдельный **Hermes Gateway** процесс: `hermes --profile <p> gateway run --external-supervisor`.
- Все 6 гейтвеев живут на **Маке** (launchd), не на VPS. VPS используется только для OmniRoute (`127.0.0.1:20128`) и как мозг 24/7.
- Модель по умолчанию для агент-профилей: **free** (`omniroute/auto/free-coding-full` → `nous/poolside/laguna-s-2.1:free` и др.).

## Критически важные настройки (НЕ ТРОГАТЬ)

### 1. financier — провайдер `omniroute` обязан быть определён
После чистки config финансист падал с `Unknown provider 'omniroute'`. В `profiles/financier/config.yaml`
должен быть блок:
```yaml
model:
  provider: omniroute
  default: auto/free-coding-full
  base_url: http://127.0.0.1:20128/v1
  key_env: OMNI_API_KEY
providers:
  omniroute:
    name: OmniRoute (OpenCode Zen + OpenRouter + Orca)
    base_url: http://127.0.0.1:20128/v1
    key_env: OMNI_API_KEY
    discover_models: true
  nous:
    name: NEOUS / Nous Research (direct)
    base_url: https://inference-api.nousresearch.com/v1
    key_env: OMNI_API_KEY
```
И в `gateway.telegram` прописан токен (иначе `No messaging platforms enabled`):
```yaml
gateway:
  telegram:
    enabled: true
    token: <FINANCIER_TOKEN>
```

### 2. НЕТ платных фоллбэков
Раньше `fallback_providers` у financier содержал `opencode-zen/claude-fable-5*` и `openrouter` → жёг
платный кап ($22). Сейчас `fallback_providers` = ТОЛЬКО free-модели (omniroute + nous free).
**Не добавлять платные провайдеры в каскад агент-профилей.**

### 3. `agent.max_turns` снижен до 40
Был 500 → бот застревал в долгих лупах («iteration 1/500»). Для Telegram-ботов достаточно 40.

## Автозагрузка (launchd)

Все 6 гейтвеев встают сами после ребута Мака через `~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist`
(`RunAtLoad=true`, `KeepAlive=true`).

| Профиль | plist |
|---------|-------|
| personal | `ai.hermes.gateway-personal.plist` ✅ |
| femida | `ai.hermes.gateway-femida.plist` ✅ |
| marketer | `ai.hermes.gateway-marketer.plist` ✅ |
| sherlock | `ai.hermes.gateway-sherlock.plist` ✅ |
| financier | `ai.hermes.gateway-financier.plist` ✅ |
| batrak | `ai.hermes.gateway-batrak.plist` ✅ |

Скрипт (пере)создания плist для недостающих профилей: `tools/ops/make_gateway_plists.sh`.

## Команды обслуживания

```bash
# Статус всех гейтвеев
for p in personal femida marketer sherlock financier batrak; do
  hermes --profile $p gateway status
done

# Рестарт одного
hermes --profile financier gateway stop
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-financier

# Проверка живости токена (через прокси с кредой)
# см. HERMES_BOT_FIX_HANDOFF.md для деталей прокси
```

## Pairing

Новый бот (свежий токен) при первом сообщении от Игоря выдаёт pairing-code.
Одобрение (на хосте, где крутится гейтвей — Мак):
```bash
hermes --profile <profile> pairing approve telegram <CODE>
```
Chat ID Игоря: `176203333`.

## Связанные handoff-файлы

- `HERMES_BOT_FIX_HANDOFF.md` — что чинили и почему.
- `handoff_2026-08-29_vps_bots_setup.md` / `..._fix.md` — история setup.
- `tools/ops/start_day.sh` — утренняя проверка (в т.ч. batrak gateway + токен).
