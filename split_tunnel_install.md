# Split-Tunnel VPS — автозапуск (launchd)

## Что это
Хост-маршрут `217.149.23.113 → <текущий default-шлюз>` (минуя VPN), чтобы
мост Mac→VPS не падал при включённом VPN. Поднимается сам при старте/смене сети.

## Установка (2 шага, требуют sudo-пароль — делаешь сам в терминале)

### 1. Разрешить скрипту route add без пароля (NOPASSWD, только этот файл)
```bash
sudo bash -c 'echo "%admin ALL=(root) NOPASSWD: /Users/igorvasin/freelance-2026/split_tunnel_vps.sh" > /etc/sudoers.d/split_tunnel'
sudo chmod 0440 /etc/sudoers.d/split_tunnel
sudo visudo -c   # должно вывести "/etc/sudoers.d/split_tunnel: OK"
```

### 2. Загрузить launchd-юнит
```bash
launchctl load ~/Library/LaunchAgents/com.user.split-tunnel-vps.plist
# проверить:
launchctl list | grep split-tunnel-vps
```

## Проверка
```bash
# при VPN включённом:
route get 217.149.23.113 | grep gateway   # -> 172.20.10.1 (или текущий шлюз), НЕ VPN
~/freelance-2026/check_bridge.sh --with-echo
```

## Откат / выгрузка
```bash
launchctl unload ~/Library/LaunchAgents/com.user.split-tunnel-vps.plist
sudo rm /etc/sudoers.d/split_tunnel
```

## Файлы
- `split_tunnel_vps.sh` — основной (динамический шлюз, idempotent, --undo)
- `split_tunnel_vps_launchd.sh` — враппер для launchd (только sudo-вызов)
- `~/Library/LaunchAgents/com.user.split-tunnel-vps.plist` — юнит
- `split_tunnel_install.md` — этот файл

## Примечание
WatchPaths перезапускает юнит при изменении конфигов сети (Wi-Fi переподключение).
StartInterval=300 — перепроверка раз в 5 мин на случай, если WatchPaths не сработал.
