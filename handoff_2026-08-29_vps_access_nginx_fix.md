# HANDOFF — 2026-08-29 (VPS доступ + починка nginx.conf) [FINAL]

> SSoT для продолжения. Предыдущие: `handoff_2026-08-29_vps_bots_fix.md`
> (6 ботов, мост, меню-свитчер ПОЧИНЕН), `handoff_2026-08-29_vps_bots_setup.md` (база).

## ТЕКУЩИЙ СТАТУС (на момент закрытия сессии)

### 1. VPS доступ — ВОССТАНОВЛЕН через консоль TimeWeb ✅
- VPS: `217.149.23.113` (IP НЕ менялся; менялся только IP Мака).
- Причина блока SSH: внутренний ufw на VPS стоял `policy DROP` и пускал
  только старый диапазон `91.78.5.0/24` (тот, с которого агент заходил
  ранее). Домашний IP `95.154.153.47` не был в ufw.
- **ИСПРАВЛЕНО в консоли VPS (VNC TimeWeb):** добавлены правила
  `ufw allow from 95.154.153.47 to any port 22/2222 proto tcp`.
  Проверено: `ufw status` показывает оба правила ALLOW для 95.154.153.47.
- **TimeWeb FWaaS:** в панели правила на 22/2222 для 95.154.153.47 тоже
  добавлены (whitelist-igor). Сам VPS подтвердил успешные входы
  `Accepted publickey for root from 91.78.5.91` в логе sshd.
- sshd на VPS: `active (running)`, слушает 0.0.0.0:22 и :2222.
- ⚠️ **НО:** с Мака по состоянию на конец сессии SSH ещё НЕ прошёл
  (`nc 22` → BLOCKED). Вероятные причины (проверить при следующем сеансе):
  1. Домашний IP сменился снова (динамический) — перепроверить
     `dig +short myip.opendns.com @resolver1.opendns.com` на Маке.
  2. TimeWeb FWaaS не применил правило (нажать «Применить» в панели).
  3. Домашний роутер режет исходящий 22 (провайдер) — тогда ходить
     через 2222 или через 185.77.216.16:64468 (tunnel-igor).

### 2. nginx.conf НА ДИСКЕ ИСПОРЧЕН ⚠️ (КРИТИЧНО ПЕРЕД РЕБУТОМ)
- В этой сессии агент добавил невалидный `map` в `/etc/nginx/nginx.conf`
  (потерялись `$`-переменные при передаче через ssh-heredoc). Команда
  `cp` из бэкапа НЕ прошла из-за таймаута связи.
- **Старый nginx-процесс ещё ЖИВ** (reload не применился), поэтому
  сейчас 443/дашборд работают. НО при перезагрузке VPS nginx НЕ стартует
  (конфиг не проходит `nginx -t`) → 443 и всё веб ляжет.
- **БЭКАП ЕСТЬ:** `/etc/nginx/nginx.conf.bak_<ts>` (агент создал перед
  правкой). Точный путь узнать в консоли:
  `ls -t /etc/nginx/nginx.conf.bak_* | head -1`
- **ПРАВИЛО:** ВПЕРЁД ПЕРЕЗАГРУЖАТЬ VPS — сначала восстановить конфиг!

### 3. Как починить nginx (из консоли VPS ИЛИ по SSH, когда откроется)
```bash
BAK=$(ls -t /etc/nginx/nginx.conf.bak_* | head -1)
cp "$BAK" /etc/nginx/nginx.conf
nginx -t && systemctl reload nginx   # или: nginx -s reload
```
После этого nginx валиден и VPS можно перезагружать без риска.

### 4. Дашборд OmniRoute — доступен (когда nginx жив)
- OmniRoute на VPS: `active`, дашборд-WebSocket на `127.0.0.1:20131`.
- nginx уже настроен проксировать `/omni/` → `127.0.0.1:20131`
  (файл `/etc/nginx/sites-enabled/levitan-webhook`, блок добавлен агентом).
- Доступ в браузере: `https://217.149.23.113/omni/`
  (отвечает `426 Upgrade Required` — это WS-endpoint дашборда, норма;
  браузер с JS откроет UI). Логин — `INITIAL_PASSWORD` из
  `/root/.omniroute/.env` на VPS.
- ⚠️ Блок в nginx НУЖНО ДОПИСАТЬ: в location `/omni/` сейчас
  `proxy_set_header Connection "upgrade";` (всегда) — это ломает plain HTTP.
  Правильно: использовать `map $http_upgrade $connection_upgrade`
  и `proxy_set_header Connection $connection_upgrade;`. Добавить `map`
  в http-блок nginx.conf при восстановлении (см. пункт 5).

### 5. Правильный блок для nginx (когда будешь править)
В `/etc/nginx/nginx.conf` внутрь `http {`:
```
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }
```
В `/etc/nginx/sites-enabled/levitan-webhook` location `/omni/`:
```
    location /omni/ {
        proxy_pass http://127.0.0.1:20131/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
    location = /omni { return 301 /omni/; }
```
НЕ вписывать `$`-переменные через ssh-heredoc без экранирования `\$
` — они теряются!

## ОТКРЫТЫЕ ЗАДАЧИ (следующая сессия)
- [ ] **P0:** восстановить `/etc/nginx/nginx.conf` из бэкапа + добавить
  корректный `map` для WS (пункт 5). Сделать ДО любой перезагрузки VPS.
- [ ] проверить, прошёл ли SSH с Мака (dig IP, TimeWeb apply, проба 22/2222).
- [ ] если SSH не идёт с дома — использовать VNC-консоль TimeWeb как
  основной канал управления VPS (она работает без SSH/интернета Мака).
- [ ] доделать доступ к дашборду OmniRoute в браузере (проверить, что UI
  грузится, а не только 426).
- [ ] (опц.) перенастроить ботов VPS на primary `omniroute` вместо
  фоллбэка opencode-zen, когда дашборд жив и каскады настроены Игорем.

## ФАЙЛЫ
- `handoff_2026-08-29_vps_bots_fix.md` — база (6 ботов, мост, свитчер).
- `handoff_2026-08-29_vps_bots_setup.md` — первичная база (6 ботов, мост).
- `/etc/nginx/nginx.conf.bak_<ts>` — РАБОЧИЙ бэкап конфига nginx на VPS.
- `/root/.hermes/gateway_run_profile_menu_fix.patch` — патч меню-свитчера.
- `/root/.omniroute/.env` — пароль дашборда OmniRoute (INITIAL_PASSWORD).

## КАК ПРОДОЛЖИТЬ
1. «продолжи по handoff_2026-08-29_vps_access_nginx_fix.md»
2. Сначала восстановить nginx.conf из бэкапа (пункт 3) — КРИТИЧНО.
3. Проверить SSH / дашборд.
4. Мост Mac→VPS при необходимости: `bash ~/freelance-2026/check_bridge.sh --with-echo`.
