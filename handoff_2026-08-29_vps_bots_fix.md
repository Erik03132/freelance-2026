# HANDOFF — 2026-08-29 (VPS Telegram-боты: маршрутизация + мост) [FINAL]

> SSoT для продолжения. Предыдущий `handoff_2026-08-29_vps_bots_setup.md` — база
> (6 ботов подняты, мост описан). Этот файл — ДОПОЛНЕНИЕ: что починили сегодня
> и что осталось. Читать ВМЕСТЕ с setup-handoff.

## ЧТО СДЕЛАНО (verified 29.08 вечер, end-to-end)

### 1. Мост Mac→VPS — СТАБИЛЕН ✅
- Причина падения утром: IPv4 Мака динамический, выпал из whitelist VPS (FWaaS).
- **РЕШЕНО:** в whitelist-igor (TimeWeb FWaaS) добавлен блок **`91.78.5.0/24`**
  на порты 22 и 2222 (плюс старые одиночные IP оставлены). Мост перестал падать
  при смене IP.
- `check_bridge.sh --with-echo` = ВСЁ ЗЕЛЁНОЕ (9119 + 8742 LISTEN, 8742/health=200,
  peer dm VPS ответил «мост работает»).
- Туннель: autossh LaunchAgent `com.igorvasin.vps-tunnel.plist`
  (`ssh root@217.149.23.113 -p 22`, форварды 9119→9119, 8742→8642).

### 2. Каша маршрутизации — УСТРАНЕНА ✅
- **БЫЛО:** в root `config.yaml` блок `profile_routes` жёстко вёл
  `chat_id 176203333 → profile: batrak`. Из-за этого ВСЕ боты, кому Игорь писал
  из своего чата, летели в Батрака (Шерлок отвечал «я Батрак», Маркетолог —
  «я Батрак»).
- **СДЕЛАНО:** блок `profile_routes:` полностью удалён из
  `/root/.hermes/config.yaml`. Gateway (multiplex) сам матчит бот→профиль по токену.
- **РЕЗУЛЬТАТ (подтверждено логом gateway.log):**
  - @sher03132_bot → **sherlock** ✅
  - @market03132_bot → **marketer** ✅ (лог: `agent:marketer:telegram:dm:176203333`)
  - @finans03132_bot → **financier** ✅
  - @femida03132_bot → **femida** ✅
  - @batrak03132_bot → **batrak** ✅
  - @hermes03132_bot → **personal** (НО см. «НЕ ДОДЕЛАНО») ⚠️

### 3. Кэш-мусор сеансов почищен ✅
- В `state.db` (VPS) удалена stale-сессия `agent:main:telegram:dm:176203333`
  (1 сессия + 108 сообщений + 6 usage, каскадом). Бэкап:
  `/root/.hermes/state.db.bak_1788001053`.
- Это убрало старые «фантомные» сеансы, из-за которых боты несли чушь
  про «забинден на femida».

## НЕ ДОДЕЛАНО (оставили как есть, по решению Игоря)

### personal НЕ именованный адаптер ⚠️
- @hermes03132_bot (главный) отвечает, НО в логе идёт как `agent:main`
  (default), а не `agent:personal`.
- **Попытка исправить (НЕ УДАЛАСЬ, откатана):** убрал токен из root
  `gateway.telegram.token`, чтобы gateway матчил @hermes03132 к профилю personal.
  Результат: personal вообще не поднялся как адаптер (getMe Unauthorized),
  бот перестал отвечать. **Откатил** root-токен из бэкапа
  `config.yaml.bak_1788001416` → бот снова отвечает как main.
- **ПРИЧИНА (не чинилось вслепую):** в `profiles/personal/config.yaml` стоит
  `gateway.telegram.enabled: false` и НЕТ верхнеуровневого блока `telegram:`
  (у sherlock тоже нет, но он работает — видимо, токен из `.env` подхватывается
  автоматом для multiplex). Gateway не стартует адаптер personal из профиля,
  т.к. telegram в нём выключен.
- **ФУНКЦИОНАЛЬНО ЭТО НЕ БАГ:** personal отвечает персоной из `personal/SOUL.md`
  (корректная: «Hermes — личный ИИ-помощник Игоря»). Разница только в имени
  адаптера в логе. Игорь решил оставить как есть.
- **ЕСЛИ В БУДУЩЕМ ЗАХОЧЕТСЯ именованный personal:** надо понять точную
  структуру конфига multiplex-профиля с telegram (почитать исходники Hermes,
  как матчится токен профиля → адаптер, и какой ключ включает telegram в профиле).
  НЕ угадывать — прошлый раз угадывание сломало бота.

## ИЗВЕСТНЫЕ НЮАНСЫ

- **Бот врёт про свой конфиг.** Модель при ответе может сказать
  «забинден на femida/default» — это ГАЛЛЮЦИНАЦИЯ модели, она не знает свой
  конфиг. Источник истины — `gateway.log` (строка `agent:<профиль>:telegram:...`)
  и `profile_routes` в config. Сейчас `profile_routes` НЕТ нигде.
- **ТГ-трафик VPS → только через US-прокси.** `proxy_url:
  http://Q3NeJXTY:dsBaWh2L@172.120.21.141:64468` в `gateway.telegram` и в
  OmniRoute systemd. При getMe-тестах НЕ ставить `--noproxy` (ипси ломает маршрут).
- **OmniRoute на VPS МЁРТВ (не мешает ботам).** Порт 20128 слушается, но
  `/v1/models` пусто → инференс не отдаёт. Причина: `credentialLoader` OmniRoute
  читает ТОЛЬКО поля `clientId/clientSecret/tokenUrl/authUrl/refreshUrl`, а файл
  `/root/.omniroute/provider-credentials.json` содержит `openrouter.apiKey`
  (игнорируется → «0 fields»). Боты НЕ зависят от OmniRoute — профили VPS
  стоят на `custom → https://opencode.ai/zen/v1` (живой free-эндпоинт, `hy3-free`
  отвечает). Отдельная задача: `OMNIROUTE_VPS_TASK.md` (переподнять/init).
- **Логи gateway пишутся в файл**, не в journald: `/root/.hermes/logs/gateway.log`
  (и `agent.log`, `errors.log`). `journalctl -u hermes-gateway` почти пустой.
  Смотреть ВСЕГДА файл `gateway.log` для маршрутизации.

## КАК ПРОДОЛЖИТЬ В НОВОЙ СЕССИИ

1. «продолжи по handoff_2026-08-29_vps_bots_fix.md» — прочитает это.
2. Перед правкой конфига VPS — БЭКАП:
   `cp /root/.hermes/config.yaml /root/.hermes/config.yaml.bak_$(date +%s)`
   `cp /root/.hermes/state.db /root/.hermes/state.db.bak_$(date +%s)`
3. Рестарт gateway (ВНЕ дерева, иначе убьёт сам себя):
   `setsid systemctl restart hermes-gateway` (через SSH туннель Mac→VPS).
4. Проверка маршрутизации: пишем боту в ТГ → смотрим в
   `/root/.hermes/logs/gateway.log` строку `agent:<профиль>:telegram:dm:...`.
5. Мост: `bash ~/freelance-2026/check_bridge.sh --with-echo`.

## ФАЙЛЫ
- `handoff_2026-08-29_vps_bots_setup.md` — база (6 ботов, мост, allowlist).
- `handoff_2026-08-29_vps_bots_fix.md` — ЭТОТ файл (маршрутизация, personal).
- `check_bridge.sh` — проверка моста.
- `vps_do.sh` — обёртка профиль+задача.
- `split_tunnel_vps.sh` + `split_tunnel_install.md` — VPN+мост.
- `config.yaml.bak_1788001416` — рабочий бэкап config (root-токен на месте).
- `state.db.bak_1788001053` — бэкап БД после чистки сеансов.
- НЕ пушить: `~/.hermes/.env`, `state.db`, `sessions/`, `vault/`.

## ДОБИТО (сессия 29.08 вечер, продолжение) — меню-свитчер ПОЧИНЕН ✅

> Root-cause найден в ИСХОДНИКАХ (без угадывания), см. ниже.

### Root-cause (почему `/batrak`/`/sherlock`/`/profiles` молчали)
- Плагин `hermes-profile-menu` читает chat_id/platform через
  `gateway.session_context.get_session_env("HERMES_SESSION_*")` — это
  **ContextVar**, который gateway проставляет вызовом `_set_session_env()`
  **только внутри** `_handle_message_with_agent` (run.py:18979).
- Но slash-команды плагинов диспетчатся **раньше** — в `_handle_message`
  (run.py:17722), где контекст ещё НЕ установлен. В `os.environ` этих
  переменных тоже нет (systemd задаёт только HERMES_HOME/TOKEN/PROXY).
- Результат: плагин видел пустой platform → возвращал
  «Эта команда переключает профиль только внутри Telegram-чата» и
  молча ничего не делал. **Подтверждено изолированным тестом:**
  до проставления contextvar `_session_origin()` = `('', '')`,
  после = `('telegram', '176203333')`.

### Фикс (точечный патч ядра, НЕ трогали логику плагина)
- В `gateway/run.py` вокруг вызова `plugin_handler(user_args)` (блок
  плагин-команд, ~17776) добавлен scoped `set_session_vars(...)` из
  `source` (он доступен в `_handle_message`), с гарантированным
  `clear_session_vars(...)` в `finally`. Теперь плагин при вызове
  команды видит реальный platform+chat_id и корректно пишет
  `profile_routes` в config.yaml.
- Патч-файл (git diff): `/root/.hermes/gateway_run_profile_menu_fix.patch`
  — для отката `cd /srv/hermes/.hermes/hermes-agent && git apply -R <patch`.
- Бэкап до правки: `/srv/hermes/.hermes/hermes-agent/gateway/run.py.bak_<ts>`.
- Плагин `hermes-profile-menu/__init__.py` возвращён к ЧИСТОМУ оригиналу
  (диаг-лог удалён).

### Verification (честный статус)
- ✅ Синтаксис run.py OK, gateway перезапущен (`setsid systemctl restart`),
  активен, ошибок загрузки нет, 60 команд в меню зарегистрированы.
- ✅ Изолированный тест: contextvar доходит до плагина (root-cause устранён).
- ⏳ **REAL end-to-end остаётся за Игорем:** бот НЕ получает собственные
  `sendMessage` как входящие (Telegram так не работает), поэтому авто-тест
  команды невозможен. Игорю нужно в ТГ у `@hermes03132_bot` нажать
  `/sherlock` → должен прийти ответ «✅ Переключено: 🔍 Шерлок» и в
  `gateway.log` появиться строка `agent:sherlock:telegram:dm:176203333`.
  (См. «ПЕРВЫЙ ШАГ ИГОРЯ» внизу.)

## ЧТО МОЖНО ДЕЛАТЬ ДАЛЬШЕ (по желанию Игоря)
- [ ] **Игорю:** real E2E проверка `/sherlock` `/profiles` `/batrak` у бота.
- [ ] Починить personal как именованный профиль (см. НЕ ДОДЕЛАНО).
- [ ] OmniRoute на VPS (отдельная задача, не блокирует ботов).
- [ ] Завести ботов для financier/health/defender/chief при необходимости
      (сейчас подняты только 6: personal/sherlock/marketer/financier/femida/batrak).
- [x] ~~Починить меню-свитчер `/batrak` `/chief` в ТГ~~ — СДЕЛАНО (фикс выше).

## ПЕРВЫЙ ШАГ ИГОРЯ (проверка починки)
> ВАЖНО: свитчер НУЖЕН только для агентов БЕЗ своего бота. У 6 основных
> (sherlock/marketer/financier/femida/batrak/personal) уже есть отдельные
> боты — им свитчер не нужен (пишешь боту → уже в агенте).
> Агенты БЕЗ бота (в allowlist, но без токена): `defender`, `health`
> (Айболит), `english-tutor`, `chief`, `bridge`. Для них `/<команда>` в
> `@hermes03132_bot` — единственный доступ. РЕШЕНО (29.08): свитчер
> ОСТАВЛЯЕМ, пока не поднимем им отдельные боты (нужны токены BotFather).

1. В Telegram у `@hermes03132_bot` отправь `/aibolit` (у Айболита НЕТ своего
   бота — это реально проверит переключение, в отличие от /sherlock).
2. Ожидается: бот отвечает «✅ Переключено: ☢️ Айболит / Профиль: `health`».
3. Следующее сообщение пойдёт Айболиту (в логе VPS:
   `agent:health:telegram:dm:176203333`).
4. Команда `/profiles` покажет меню всех специалистов с текущим выбором.
5. Если не сработало — откат патча:
   `ssh root@217.149.23.113` →
   `cd /srv/hermes/.hermes/hermes-agent && git apply -R /root/.hermes/gateway_run_profile_menu_fix.patch`
   → `setsid systemctl restart hermes-gateway`.
