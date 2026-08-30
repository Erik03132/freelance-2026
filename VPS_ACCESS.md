# VPS ACCESS + HERMES TELEGRAM — единственный источник истины

> Обновлено после подтверждённого end-to-end запуска 24.08.2026.
> Секреты сюда не записывать.

## 1. Главное разделение

### Telegram-бот работает автономно на VPS

`@hermes03132_bot` НЕ зависит от открытого Terminal на Маке и НЕ зависит от
локального SSH-туннеля. Telegram egress идёт с TimeWeb VPS через настроенный в
systemd внешний HTTP CONNECT proxy (порт 64468).

Подтверждено:

- `Connected to Telegram (polling mode)`;
- PID стабилен минимум 75 секунд;
- `NRestarts=0`;
- исходящая доставка успешна;
- входящее сообщение получено и бот ответил.

### SSH нужен только для администрирования VPS

Падение SSH/смена динамического IP Мака не должны ломать Telegram-бота.
Если бот отвечает, но SSH недоступен — не трогай gateway: это отдельная
проблема TimeWeb FWaaS/доступа администратора.

## 2. Активный Hermes на VPS

- CLI: `/srv/hermes/venv/bin/hermes`
- systemd: `hermes-gateway.service`
- **активный HERMES_HOME:** `/root/.hermes`
- **активный config:** `/root/.hermes/config.yaml`
- systemd override: `/etc/systemd/system/hermes-gateway.service.d/20-hermes03132.conf`
- `/srv/hermes/.hermes` — миграционная/архивная копия, НЕ активный gateway-home.

Никогда не править `/srv/hermes/.hermes/config.yaml`, ожидая изменения
systemd-gateway.

## 3. Каноническое управление gateway

```bash
systemctl status hermes-gateway.service --no-pager
systemctl restart hermes-gateway.service
journalctl -u hermes-gateway.service --since '-5 minutes' --no-pager
systemctl show hermes-gateway.service -p MainPID -p NRestarts
```

**Не запускать** второй gateway через `nohup`, прямой `python -m ... gateway run`
или отдельный aiogram-бот с тем же Telegram-токеном.

## 4. Рабочая модель

```yaml
model:
  provider: opencode-free
  default: laguna-s-2.1-free
```

Keyless, проверена реальным запросом. `hermes model cascade ...` не существует;
fallback управляется через `hermes fallback add|remove|list`.

## 5. Telegram security

- Один токен = один polling-процесс.
- Разрешён Telegram ID владельца через `TELEGRAM_ALLOWED_USERS`.
- `GATEWAY_ALLOW_ALL_USERS=false`.
- 401/token rejected = токен отозван, а не проблема прокси.
- Токены и proxy credentials хранить только в active secrets/systemd override,
  не печатать в чат/логи/документацию.

## 6. Профильное меню

Канонический плагин:

- исходник на Маке: `~/freelance-2026/hermes-profile-menu/`
- установка на VPS: `/root/.hermes/plugins/hermes-profile-menu/`

Команды: `/chief`, `/default`, `/batrak`, `/bridge`, `/defender`, `/english`,
`/femida`, `/financier`, `/aibolit`, `/marketer`, `/sherlock`, `/profiles`.

Плагин использует один multiplex gateway и маршрутизирует конкретный Telegram-чат
в профиль через `gateway.profile_routes`. Второй бот-процесс не нужен.

## 7. SSH/FWaaS (администрирование)

- TimeWeb SSH-порт, подтверждённый поддержкой: `2222`; порт `22` может быть refused.
- FWaaS может разрешать вход только с текущего динамического IP клиента.
- Если все входящие проверки timeout, но бот работает: VPS жив; сравни текущий IP
  Мака с активным FWaaS Allow rule.
- Предпочтительный аварийный доступ: веб-консоль TimeWeb.
- Не использовать иностранный proxy как generic SSH jump host к RU VPS.
- Локальный старый туннель `localhost:22001` был настроен на VPS:22 и устарел;
  не считать его каноническим доступом.
- WireGuard может быть будущим улучшением административного доступа, но он НЕ
  нужен для работы Telegram-бота.

## 8. Быстрая проверка здоровья

```bash
systemctl is-active hermes-gateway.service
systemctl show hermes-gateway.service -p MainPID -p NRestarts
journalctl -u hermes-gateway.service --since '-2 minutes' --no-pager | \
  grep -E 'Proxy detected|Connected to Telegram|Failed to connect|Conflict|auth failed|No inference provider'
```

Ожидается:

```text
active
NRestarts=0
Proxy detected; passing explicitly to HTTPXRequest
Connected to Telegram (polling mode)
```

Тест доставки:

```bash
HERMES_HOME=/root/.hermes /srv/hermes/venv/bin/hermes send \
  --to telegram:176203333 'Hermes VPS healthcheck' --json
```

## 9. Золотой навык

Перед любой работой с этим ботом/VPS загружать Hermes skill
`igor-hermes-telegram-vps`. Он важнее старых сессионных догадок.
