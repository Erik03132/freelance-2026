# Фаза 0 — Стабилизация инфраструктуры (подробный план)

> Предусловие для Фаз 2-5. Без стабильного фундамента автоматизация рухнет.

---

## Текущий статус (07.07.2026)

| Компонент | Статус | Проблема |
|-----------|--------|----------|
| VPS `root@72.56.38.19` | ❌ timeout/refused | Недоступен, причина неизвестна |
| VPS `root@185.39.206.145` | ❌ timeout/refused | Недоступен (старый хост) |
| Диск VPS | ⚠️ было 91% | Логи/записи забивают место |
| NAT (baresip) | ❌ ORIGINATOR_CANCEL | SDP с приватным IP 192.168.0.112 |
| Секреты | ✅ ротированы | Mango/OpenRouter/Telegram в `.env` |
| Бэкап CRM | ❌ не настроен | `data/call_results/` только локально |

---

## Шаг 1: Доступ к VPS

**Действия со стороны пользователя (я не могу удалённо):**
1. Проверить, поднят ли VPS у хостера (панель / письмо).
2. Если выключен — включить.
3. Если доступ по SSH-ключу — убедиться, что ключ добавлен в `ssh-agent`.
4. Проверить, не сменился ли IP (хостер мог переназначить).

**После доступа — проверяю:**
```bash
ssh root@<IP> 'uptime; df -h /; free -h; systemctl status mango-events 2>/dev/null'
```

---

## Шаг 2: Очистка диска

```bash
# Логи старше 7 дней
find /var/log -name "*.log" -mtime +7 -delete
# Старые записи разговоров (старше 30 дней)
find /opt/recordings -mtime +30 -delete 2>/dev/null
# journalctl
journalctl --vacuum-time=7d
# Docker (если есть)
docker system prune -f
```

Цель: <70% заполнения диска.

---

## Шаг 3: Автоперезапуск сервисов

Создаю systemd-юнит для voice-angela ( если есть скрипт приёма событий Mango):

`/etc/systemd/system/voice-angela.service`:
```ini
[Unit]
Description=Voice Angela event listener
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/voice-angela/events.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```
```bash
systemctl enable --now voice-angela
systemctl status voice-angela
```

**Telegram-алерт при падении** (через cron или watchdog):
```bash
# /opt/watchdog.sh
if ! systemctl is-active --quiet voice-angela; then
  curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<ID>&text=⚠️ VPS service down"
fi
```

---

## Шаг 4: Решение NAT для baresip

**Вариант A (рекомендован): baresip на VPS с публичным IP**

1. На VPS ставим baresip:
   ```bash
   apt install baresip
   ```
2. `config` (sip_listen 0.0.0.0:5081, sip_trans_def tcp, ctrl_tcp 4444)
3. `accounts` — SIP `user1@vpbx400374818.mangosip.ru` (user1, НЕ 23)
4. Запуск: `baresip -f /opt/baresip -d &`
5. Mango callback `from.extension=23` → baresip отвечает → перевод на ext 22

**Почему это работает:** VPS имеет публичный IP, Mango может отправить
RTP напрямую. Нет NAT между Mango и baresip.

**Вариант B (если не хотим поднимать baresip на VPS): ngrok для SIP**
```bash
ngrok tcp 5081
# в Mango SIP URI использовать ngrok-host:port
```
Минус: ngrok-хост меняется при рестарте (нужен платный фикс. домен).

**Вариант C (отклонён):** проброс портов на роутере — пользователь
отказался ("на соплях").

---

## Шаг 5: Секреты и бэкап

**Секреты** (уже сделано, проверка):
- [x] Mango API key/salt в `.env`
- [x] OpenRouter key в `.env`
- [x] Telegram token в `.env`
- [x] Нет хардкода в `.py`/`.md`/`.sh`
- [ ] Оценить ротацию Gemini/Perplexity/GitHub/Neon/SIP (по решению)

**Бэкап CRM:**
```bash
# cron: ежедневно
0 3 * * * rsync -a /root/antigravity/data/call_results/ /backup/call_results/
# или git (если не секреты)
cd /path && git add data/call_results && git commit -m "backup $(date +%F)"
```

---

## Критерии готовности Фазы 0

- [ ] VPS доступен по SSH, авто-восстановление при сбое
- [ ] Диск <70%
- [ ] baresip на VPS принимает звонок Mango без ORIGINATOR_CANCEL
- [ ] Секреты только в `.env`
- [ ] Ежедневный бэкап `call_results/`
