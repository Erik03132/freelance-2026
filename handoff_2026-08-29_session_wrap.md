# HANDOFF — 2026-08-29 (вечер, закругление сессии)

> SSoT для продолжения. Предыдущий: `handoff_2026-08-29_vps_access_nginx_fix.md`

## ЧТО СДЕЛАНО (зелёное)

- [x] **VPS nginx восстановлен** (ТГ-бот, профиль femida, удалённо): `nginx -t` ok,
  reload done, 80/443 слушают, добавлен корректный `map $http_upgrade` для WS
  (OmniRoute /omni/). P0 из старого handoff ЗАКРЫТ.
- [x] **Десктоп Hermes gateway (профиль femida) пофикшен:** причина падения —
  в `~/.hermes/profiles/femida/config.yaml` был ollama-провайдер
  `qwen2.5:1.5b` (32K context), Hermes отверг как compression-модель (нужно ≥64K).
  Закомментирован → femida берёт `gemini-2.0-flash` из `auxiliary.compression`.
  Gateway установлен как launchd-сервис: `ai.hermes.gateway-femida.plist`
  (`hermes --profile femida gateway install`). Статус: ✓ running.
- [x] **Локальный веб-UI Hermes** поднят: http://127.0.0.1:9120 (порт 9120,
  чтобы не мешать туннелю 9119). Работает без VPS.
- [x] **SSoT шаблон задач** дописан в `ACTIVE_TASKS.md` (секция
  «СИНХРОНИЗАЦИЯ Mac ↔ VPS»): формат `T-NN` с полями Поручил/Задача/Результат.
  ТГ-боту дана инструкция вести задачи по шаблону (файл создал на VPS).
- [x] **Скрипты готовы к статическому IP:** `~/.vps-tunnel.sh` (читает
  `VPS_RU_PROXY` env) + `~/freelance-2026/socks_relay.py` (локальный SOCKS-релей
  без зависимостей, т.к. macOS nc не умеет SOCKS-auth). `~/freelance-2026/my_ip.sh`
  — показать текущий IP для дежурного цикла.

## ОТКРЫТЫЕ ЗАДАЧИ (следующая сессия)

- [ ] **Десктоп Hermes "Server not found"**: gateway femida установлен как сервис
  и running, но окно приложения не подхватило (нет кнопки Retry — приложение
  показало ошибку и не переподключилось). Шаг: полностью закрыть Hermes (Cmd+Q)
  и открыть заново — сервис уже стоит, должен увидеть. Если нет — см. лог
  `~/Library/Application Support/Hermes/logs/desktop.log`.
- [ ] **Статический IP VOSNET** — подключить в ПОНЕДЕЛЬНИК (ЛК/офис
  +7(496)441-11-62, ~150₽/мес). После получения IP: вписать в TimeWeb FWaaS +
  ufw (порт 22) на VPS (через ТГ-бота), прописать в `~/.vps-tunnel.sh`, поднять
  туннель навсегда. Поставить на VPS cron auto-whitelist (сам добавляет новые
  home-IP в ufw) как страховку.
- [ ] **RU-SOCKS5-прокси ОТМЕНЁН**: поддержка вернула деньги (работает только по
  белым спискам РФ-сервисов). Не использовать.
- [ ] **Дашборд OmniRoute** (`https://217.149.23.113/omni/`) недоступен сейчас —
  только из-за того, что VPS закрыт динамическим IP. Откроется, когда туннель
  оживёт. Логин в `/root/.omniroute/.env` (INITIAL_PASSWORD).

## ДЕЖУРНЫЙ ЦИКЛ (выходные, динамический IP)
Туннель падает при смене home-IP. Оживить БЕЗ туннеля (ТГ-бот жив):
1. `bash ~/freelance-2026/my_ip.sh` → узнать IP.
2. В ТГ главному боту: «открой <IP> в ufw на VPS (порт 22)».
3. LaunchAgent `com.user.vps-tunnel` сам ретраит туннель (~10с).

## ФАЙЛЫ
- `handoff_2026-08-29_vps_access_nginx_fix.md` — база (P0 закрыт).
- `ACTIVE_TASKS.md` — SSoT задач + шаблон T-NN + дежурный цикл.
- `~/.vps-tunnel.sh`, `~/freelance-2026/socks_relay.py`, `my_ip.sh` — туннель.
- `~/.hermes/profiles/femida/config.yaml` — ollama-провайдер закомментирован.
- `ai.hermes.gateway-femida.plist` — gateway femida как сервис.

## СТАТУС НА МОМЕНТ ЗАКРЫТИЯ
- VPS: nginx ок, но закрыт (home-IP сменился, туннель упал). Бот жив.
- Туннель Mac→VPS: упал (ждёт статику VOSNET в понедельник).
- Десктоп Hermes: gateway femida установлен+running, но окно не переподключилось
  (нужен перезапуск приложения).
- Локальный дашборд 9120: жив.

---

## ПРОДОЛЖЕНИЕ — 29.08 ВЕЧЕР (прямо сейчас, суббота 21:xx МСК)

> SSoT для следующей сессии. Предыдущий: выше (база 29.08).

### ЧТО СДЕЛАНО (зелёное)
- [x] **Доступ к VPS восстановлен.** Причина была НЕ в блоке VPS, а в
  мёртвом хостовом маршруте `217.149.23.113 → 172.20.10.1` (шлюз iPhone
  Hotspot, оставшийся от `split_tunnel_vps.sh`). Убран через
  `route delete 217.149.23.113` (Touch ID). VPS пингуется, SSH ок.
- [x] **Туннель Мак→ВПС переписан на ПРЯМОЙ SSH** (без отменённого
  RU-SOCKS5). `~/.vps-tunnel.sh` теперь форвардит:
  `9120→9120` (Hermes dash), `8742→8642` (gateway), `8743→20128` (Omni API),
  `8890→8890` (Omni dash). LaunchAgent `com.user.vps-tunnel` держит живым.
  Текущий home-IP `95.154.153.47` уже в ufw VPS (22 + 2222 + добавил 80/443).
- [x] **Hermes Agent веб-дашборд ПОДНЯТ на VPS** (`127.0.0.1:9120`, HTTP 200).
  Закреплён systemd `hermes-dashboard.service` (переживёт ребут). Доступен
  локально на Маке: **http://127.0.0.1:9120**
- [x] **OmniRoute дашборд СДЕЛАН СВОЙ** (родной Next.js в v16.2.12 битый —
  пишет "Ready" но не биндит HTTP-порт, self-fetch падает ECONNREFUSED).
  Написан лёгкий backend `/root/omni_dashboard.py` (port 8890, читает/пишет
  `/root/.omniroute/.env` + показывает статус) + HTML `/var/www/html/
  omni_dashboard.html`. Закреплён systemd `omni-dashboard.service`.
  Доступен локально: **http://127.0.0.1:8890/** (HTML) и
  `http://127.0.0.1:8890/api/status` (JSON).
- [x] **nginx на VPS**: добавлен `dashboards.conf` (443 SSL + basic auth,
  пароль = `INITIAL_PASSWORD` из `/root/.omniroute/.env`). Локации:
  `/hermes/` → 9120, `/omni/` → HTML + `/omni/api/` → 8890.
  На VPS локально проверено: обе отдают 401 без auth, 200 с auth.
- [x] **Whitelist VPS пополнен**: `95.154.153.47` добавлен в ufw на 80/443
  (кроме уже бывших 22/2222).

### ОТКРЫТЫЕ ЗАДАЧИ (следующая сессия)
- [ ] **Веб снаружи (217.149.23.113/hermes/ и /omni/) НЕДОСТУПЕН** — TimeWeb
  FWaaS блокирует 80/443 для динамического home-IP (только 22 доступен,
  проверено nc: 443/80 timeout, 22 ok). Откроется после статического IP
  VOSNET (понедельник, ЛК/офис +7(496)441-11-62). Пока дашборды доступны
  ТОЛЬКО через туннель локально (9120 / 8890).
- [ ] **OmniRoute родной дашборд не работает** (битый Next.js билд v16.2.12).
  Решено: свой дашборд поверх `.env`. Если нужен именно родной — надо
  переустановить/пересобрать OmniRoute (риск сломать рабочий gateway).
- [ ] **Провайдеры OmniRoute не подключены** — в `.env` нет ключей
  (OpenRouter/Nous/др.), поэтому `auto/*` пулы пустые. Через дашборд
  (8890) можно добавить `OMNIROUTE_API_KEY` / `OPENROUTER_API_KEY` и т.п.
  Сейчас агенты ходят через `fallback_providers: opencode-zen` (тест
  вернул `hy3-free`).
- [ ] **Статический IP VOSNET** — понедельник. После: вписать в TimeWeb
  FWaaS + ufw (22), `~/.vps-tunnel.sh` (уже готов), cron auto-whitelist.
- [ ] **Дежурный цикл при смене IP**: `my_ip.sh` → ТГ-боту «открой <IP>
  в ufw» → LaunchAgent ретраит туннель. Сейчас маршрут починен, но при
  смене home-IP (хотспот/другой WiFi) маршрут `217.149.23.113→172.20.10.1`
  МОЖЕТ ВОССТАНОВИТЬСЯ (если `split_tunnel_vps.sh` ещё где-то дёргается).
  Проверить: `grep -rIl 172.20.10.1 ~/Library/LaunchAgents` — если найдётся,
  выключить, чтобы не плодить мёртвые маршруты.

### АДРЕСА (для Игоря)
- **Hermes веб-интерфейс**: http://127.0.0.1:9120 (через туннель, локально)
- **OmniRoute дашборд**: http://127.0.0.1:8890/ (через туннель, локально)
- **Снаружи (после VOSNET)**: https://217.149.23.113/hermes/ и /omni/
  (basic auth, пароль = OmniRoute INITIAL_PASSWORD)
- **VPS SSH**: root@217.149.23.113:22 (ключ ~/freelance-2026/.ssh_agent_key)

### ФАЙЛЫ (новые/изменённые)
- `~/.vps-tunnel.sh` — прямой SSH, 4 форварда.
- `/root/hermes-dashboard.service` (VPS) — systemd Hermes dash.
- `/root/omni_dashboard.py` + `/var/www/html/omni_dashboard.html` (VPS).
- `/etc/systemd/system/omni-dashboard.service` (VPS).
- `/etc/nginx/conf.d/dashboards.conf` + `dashboards.htpasswd` (VPS).
- `~/.hermes/profiles/femida/config.yaml` — ollama закомментирован (из базы).

### СТАТУС НА МОМЕНТ ПЕРЕЗАПИСИ
- VPS: доступен по SSH, nginx ок, Hermes gateway active (агенты отвечают),
  Hermes dash (9120) + Omni dash (8890) running как systemd.
- Туннель Мак→VPS: ЖИВ (прямой SSH, LaunchAgent).
- Десктоп Hermes: ты со мной общаешься → gateway femida running (окно
  переподключилось само, пункт «Server not found» из базы ЗАКРЫТ).
- OmniRoute родной: висит (битый Next.js), агенты идут через opencode-zen.
