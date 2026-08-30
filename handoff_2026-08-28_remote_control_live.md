# HANDOFF — 2026-08-28 (Remote Control Mac → VPS, РЕАЛЬНО РАБОТАЕТ)

> ВАЖНО: старый `handoff_2026-08-28_remote_control_setup.md` содержит ГАЛЛЮЦИНАЦИИ
> (команды `hermes config set network.mode remote_client`, `network.server_url`,
> `network.listen`, `hermes gateway start --port 20128`). Этих ключей/флагов в Hermes
> НЕТ. Реальный remote-control в Hermes — это `hermes peer` + платформа `api_server`.
> Этот файл — единственный источник истины, проверенный живыми вызовами.

## Что ДОКАЗАНО работает (verified, 28.08, end-to-end)

- `hermes peer dm vps "Тест Mac→VPS: ответь одной фразой 'мост работает'"`
  → VPS-агент ответил: **"мост работает"** ✅
- Мост `localhost:9119` → VPS Hermes-serve: HTTP 404 (сервер живой) ✅
- Мост `localhost:8742` → VPS api_server: HTTP 200 на /health ✅
- На VPS: `ss -ltnp` показывает `127.0.0.1:8642` (api_server, pid 794881) и
  `127.0.0.1:9119` (hermes serve, pid 733) — оба LISTEN ✅
- `hermes peer list` на Mac: `vps  http://127.0.0.1:8742  [key set]` ✅
- Telegram-бот (`@hermes03132_bot`) жив, gateway `NRestarts=0` после перезапуска ✅

## Архитектура (реальная)

```
Mac (пульт)
  ├─ LaunchAgent com.user.vps-tunnel  (ssh -N -L, порт 22 → VPS)
  │     ├─ 127.0.0.1:9119 → VPS:127.0.0.1:9119  (hermes serve, веб-UI)
  │     └─ 127.0.0.1:8742 → VPS:127.0.0.1:8642  (api_server, peer-DM)
  └─ hermes peer vps → http://127.0.0.1:8742  (ключ HERMES_PEER_VPS_KEY)
            │
VPS 217.149.23.113 (TimeWeb, root@... -p 22)
  ├─ hermes-gateway.service (systemd): telegram + api_server(8642) + hermes serve(9119)
  └─ FWaaS whitelist-igor пускает SSH только с разрешённых IP
```

## Как ПОВТОРИТЬ настройку (если VPS пересобирать с нуля)

### На VPS (SSH root@217.149.23.113 -p 22, ключ ~/freelance-2026/.ssh_agent_key)
1. Поднять Hermes-serve (веб-UI, порт 9119):
   `HERMES_HOME=/root/.hermes /srv/hermes/venv/bin/hermes serve --port 9119 --host 127.0.0.1 --skip-build`
2. Включить api_server — дописать в `/root/.hermes/.env` (идемпотентно, бэкап сначала!):
   ```
   API_SERVER_ENABLED=true
   API_SERVER_HOST=127.0.0.1
   API_SERVER_PORT=8642
   API_SERVER_KEY=<secrets.token_hex(24) сгенерировать на Mac>
   ```
3. Перезапустить gateway: `systemctl restart hermes-gateway.service`
   (api_server поднимается автоматически рядом с telegram; проверить
   `ss -ltnp | grep 8642` и `systemctl show hermes-gateway.service -p NRestarts`)
4. НЕ запускать второй gateway вручную — один токен = один polling-процесс (VPS_ACCESS.md).

### На Mac (пульт)
1. Туннель `~/.vps-tunnel.sh` (через LaunchAgent `com.user.vps-tunnel`):
   - порт SSH = **22** (НЕ 2222! на VPS sshd слушает только 22);
   - форварды: `127.0.0.1:9119:127.0.0.1:9119` и `127.0.0.1:8742:127.0.0.1:8642`
     (локальный 8642 ЗАНЯТ mac-профилем `bridge` gateway — поэтому мост на 8742!);
   - `root@217.149.23.113 -p 22`, ключ `~/freelance-2026/.ssh_agent_key`.
2. `hermes peer add vps --url http://127.0.0.1:8742 --key <API_SERVER_KEY>`
   (ключ хранится как `HERMES_PEER_VPS_KEY` в `~/.hermes/.env`).

## Реальные команды управления (Mac → VPS)
- Отправить задачу VPS-агенту: `hermes peer dm vps "текст задачи"`
- В профиль femida: `hermes profile use femida` (сделано в этой сессии)
- **Веб-пульт VPS `http://127.0.0.1:9119` НЕ работает** — `hermes serve` на VPS поднят
  с `--skip-build`, web UI отключён (headless). При открытии в браузере отдаёт
  `{"error":"Headless backend (hermes serve): web UI disabled — use hermes dashboard…"}`.
  Реальный браузерный UI — `hermes dashboard` (локально на Mac). Чтобы включить
  веб-UI на VPS — поднять `hermes serve` БЕЗ `--skip-build` (смотри нюанс про serve ниже).
- Статус мостов: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/ ; curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8742/health`
- **Короткая обёртка (не длинные команды):** `~/freelance-2026/vps_do.sh`
  - `vps_do.sh sherlock "найди вакансии на hh.ru за 3 дня"` → задача профилю sherlock
  - `vps_do.sh "просто задача"` → на default-профиль
  - `vps_do.sh --list` / `--current` / `--dry-run` / `--help`
  - Флаги по AGENTS.md: --help, --dry-run, позиционные аргументы + --profile.
- **Проверка моста встроена в `/start-day`** (tools/ops/start_day.sh, секция G «Mac → VPS Bridge» —
  гоняет `check_bridge.sh --with-echo`). Запускай `/start-day` в начале сессии — мост проверится сам.

## Известные НЮАНСЫ (блокеры и ловушки)
1. **FWaaS `whitelist-igor` (TimeWeb):** SSH (22 и 2222) пускает ТОЛЬКО с
   `95.154.153.47`, `185.77.216.16` и (добавлено 28.08) `91.78.5.165`.
   Текущий Mac-IP узнать: `curl --noproxy '*' https://api.ipify.org`.
   Если SSH refused — значит IP Мака сменился, добавить его в whitelist-igor (порты 22+2222).
2. **Мобильный модем = динамический IP.** При переподключении телефона IP меняется →
   мост падает → надо добавить новый IP в FWaaS. На стационарном IP мост встаёт сам.
3. **VPS может быть выключен** (TimeWeb ЛК → Start). Тогда SSH refused, бот недоступен.
   LaunchAgent сам поднимет туннель при оживлении VPS.
4. **Локальный порт 8642 на Mac ЗАНЯТ** профилем `bridge` (`--profile bridge gateway run`).
   Поэтому мост на VPS-api_server = локальный `8742`, не трогать bridge.
7. **Порт 2222 на VPS НЕ слушает** (sshd только на 22). Туннель переведён на 22.
8. **`hermes serve` на VPS поднят с `--skip-build`** → web UI отключён (headless).
   `http://127.0.0.1:9119` в браузере отдаёт ошибку `web UI disabled`.
   Браузерный UI агента — `hermes dashboard` (локально на Mac).
   Чтобы включить веб-UI на VPS: переподнять serve БЕЗ `--skip-build`
   (`HERMES_HOME=/root/.hermes /srv/hermes/venv/bin/hermes serve --port 9119 --host 127.0.0.1`),
   но это соберёт фронтенд и съест память — не нужно, управляй через `vps_do.sh` + `peer dm`.
9. **`vps_do.sh` — короткая обёртка** вместо длинных команд (см. раздел «Реальные команды»).
   `vps_do.sh sherlock "задача"` переключает VPS-агента в профиль и ставит задачу.

## Текущее состояние (на момент handoff)
- Профиль Mac: `femida` (активен, `hermes profile use femida` сделано).
- Мосты: 9119 ✅, 8742 ✅. Peer `vps` зарегистрирован ✅.
- VPS: gateway active, api_server(8642)+hermes serve(9119)+telegram живы.
- Бэкап `.env` на VPS: `/root/.hermes/.env.bak_api_<unix>` (снят перед правкой).
- Бэкап туннеля: `~/.vps-tunnel.sh.bak_<unix>` (снят перед правкой 2222→22).

## Что делать в НОВОЙ сессии (если мост упал)
1. Проверить VPS в ЛК TimeWeb — включен? (Start если выключен).
2. `curl --noproxy '*' https://api.ipify.org` → сверить с whitelist-igor.
   Если IP нет в списке — добавить (порты 22+2222) в ЛК TimeWeb → Сеть.
3. Подождать ~30-60с; LaunchAgent сам поднимет туннель (проверить
   `lsof -iTCP:9119 -sTCP:LISTEN` и `:8742`).
4. Если туннель не встаёт — `launchctl unload/load ~/Library/LaunchAgents/com.user.vps-tunnel.plist`.
5. Тест: `hermes peer dm vps "эхо тест"`.

## Чего НЕ делать (по старому handoff — галлюцинации)
- НЕ писать `network.mode/remote_client/server_url/list/controller/auth_token` в config.yaml.
- НЕ делать `hermes gateway start --port 20128` (gateway = messaging, не chat-сервер).
- НЕ трогать второй gateway на VPS с тем же Telegram-токеном.

## Ссылки
- VPS_ACCESS.md — SSoT по VPS/Telegram (не править gateway вручную).
- SESSION_LATEST.md — контекст сессий 24-27.08.
- `~/.vps-tunnel.sh` — скрипт туннеля (автостарт через LaunchAgent).
- `~/.hermes/.env` (Mac) — `HERMES_PEER_VPS_KEY` (peer-ключ).
- `/root/.hermes/.env` (VPS) — `API_SERVER_KEY` + `API_SERVER_ENABLED`.
