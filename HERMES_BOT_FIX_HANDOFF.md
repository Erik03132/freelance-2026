# @hermes03132_bot на TimeWeb VPS — рабочая схема

**Статус:** ИСПРАВЛЕНО и проверено 24.08.2026.

## Подтверждённый результат

- `hermes-gateway.service` активен.
- PID был стабилен минимум 75 секунд.
- `NRestarts=0` за контрольное окно.
- Hermes: `Connected to Telegram (polling mode)`.
- Тестовая отправка успешна (`success: true`).
- Бесплатная LLM проверена реальным запросом и ответила.

## Настоящий корень проблемы

На VPS существовали **два разных Hermes home**:

- `/root/.hermes` — активный, его читает systemd (`HERMES_HOME=/root/.hermes`).
- `/srv/hermes/.hermes` — неактивный для gateway-сервиса.

Большая часть прежних исправлений модели и Telegram-конфига применялась к
`/srv/hermes/.hermes/config.yaml`, поэтому работающий systemd-gateway продолжал
читать старый `/root/.hermes/config.yaml` и сообщал `No inference provider configured`.

Дополнительно gateway многократно запускали вручную через `nohup` параллельно с
systemd. Это создавало `Gateway already running`, PID/credential locks и ложное
впечатление crash-loop. Старые строки `status=1` преимущественно совпадали с
ручными `systemctl restart` и относились к остановленному старому PID.

## Рабочая архитектура

### Активный Hermes

- CLI: `/srv/hermes/venv/bin/hermes`
- systemd unit: `/etc/systemd/system/hermes-gateway.service`
- Активный home/config: `/root/.hermes` и `/root/.hermes/config.yaml`
- Постоянные overrides: `/etc/systemd/system/hermes-gateway.service.d/20-hermes03132.conf`

### Telegram из РФ

- TimeWeb VPS использует внешний **HTTP CONNECT proxy** на порту `64468`.
- Схема `http://…:64468` подтверждена реальным запросом (HTTP 200).
- Hermes передаёт прокси непосредственно в `python-telegram-bot` `HTTPXRequest`.
- `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS=1` оставлен: при прокси fallback-IP не нужен.
- Разрешён только Telegram user ID владельца через `TELEGRAM_ALLOWED_USERS`.
- `GATEWAY_ALLOW_ALL_USERS=false` — бот не открыт посторонним.

**Не путать:** порт `64469` также является рабочим SOCKS5H, но переходить на него
не требуется. Предыдущая гипотеза «64468 — ошибочный SOCKS-порт» была ложной.

### Бесплатная LLM

Активная конфигурация:

```yaml
model:
  provider: opencode-free
  default: laguna-s-2.1-free
```

`opencode-free` — штатный keyless-провайдер Hermes, API-ключ не требуется.
Проверен реальным ответом `OK_LLM`.

## Каноническое управление

```bash
systemctl status hermes-gateway.service --no-pager
systemctl restart hermes-gateway.service
journalctl -u hermes-gateway.service --since '-5 minutes' --no-pager
```

**Не запускать gateway через `nohup`/ручной `python -m ... gateway run`**, пока
systemd-сервис активен. Иначе появляются конкурирующие poller'ы и locks.

## Быстрая проверка здоровья

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

Тест исходящей доставки:

```bash
HERMES_HOME=/root/.hermes /srv/hermes/venv/bin/hermes send \
  --to telegram:176203333 'Hermes VPS healthcheck' --json
```

## История исправления

1. Отозванный Telegram-токен заменён во всех активных местах.
2. Подтверждён рабочий HTTP CONNECT proxy `64468`.
3. Удалены конфликтующие ручные gateway-процессы и locks.
4. Настроен **активный** `/root/.hermes`, а не `/srv/hermes/.hermes`.
5. Включён keyless `opencode-free / laguna-s-2.1-free`.
6. Создан постоянный systemd drop-in.
7. Проведена 75-секундная проверка: PID стабилен, рестартов 0.
8. Подтверждены polling и исходящая Telegram-доставка.

## Секреты

Токены и прокси-пароли намеренно не записаны в этот файл. Они хранятся только
в активной конфигурации/секретах VPS и локальных `.env`.
