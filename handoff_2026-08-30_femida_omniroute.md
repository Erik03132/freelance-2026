# Handoff 2026-08-30 — Telegram-боты (Hermes profiles) + VPS-OmniRoute

**Дата:** 2026-08-30 (MSK)
**Проблема:** боты в ТГ писали «The model server is not responding», femida-бот присылал scam (номер +1 917 600-9129).
**Статус:** VPS-OmniRoute починен, femida-токен ревокнут и заменён, gateway перезапущен.

---

## Что было сделано

### 1. VPS-OmniRoute (корень проблемы с «model server not responding»)

**Причина:** В `/etc/systemd/system/omniroute.service` были прописаны
`HTTP_PROXY`/`HTTPS_PROXY=http://Q3NeJXTY:dsBaWh2L@172.120.21.141:64468`.
OmniRoute роутил ДАЖЕ localhost-self-check через этот прокси → `PROXY_UNREACHABLE`
→ `ECONNREFUSED` на 127.0.0.1:20128 → сервер висел на старте, HTTP не поднимался,
хотя порт «слушался» воркером. Боты на VPS смотрели на `127.0.0.1:20128` → падали.

**Фикс (на VPS через туннель 2222→VPS:22):**
- `override.conf` (`/etc/systemd/system/omniroute.service.d/override.conf`): `HTTP_PROXY=`,
  `HTTPS_PROXY=`, `NO_PROXY=127.0.0.1,localhost,::1,217.149.23.113`
- Провайдеры (Nous/OpenRouter) из РФ заблокированы (403 напрямую), работают ТОЛЬКО через
  прокси 172.120.21.141:64468. Поэтому прокси остаётся в окружении OmniRoute как
  `HTTPS_PROXY`, но `NO_PROXY` ловит localhost — self-check идёт напрямую, провайдеры через прокси.
- Результат: `curl 127.0.0.1:20128/v1/models` → **HTTP 200**, 614 моделей.
- Конфиги ботов на VPS (`/root/.hermes/config.yaml` + `/root/.hermes/profiles/*/config.yaml`)
  откачены с `20129` обратно на `127.0.0.1:20128` (локальный VPS-OmniRoute, НЕ Мак).

### 2. @femida03132_bot — scam / компрометация

**Где живёт:** на МАКЕ (не в pm2 на VPS!). launchd `ai.hermes.gateway-femida`,
процесс `python -m hermes_cli.main --profile femida gateway run`.

**Что случилось:** бот прислал «Hi / hop on this call / (917) 600-9129» — это НЕ ответ
юриста, это scam (вероятно утёк токен, кто-то параллельно держал бота).

**Фикс:**
- Пользователь РЕВОКНУЛ токен в @BotFather.
- Новый токен `8953909042:AAFKytky_zq1SFlUFyX7C3vEJ8iJ5Gvf0ng` прописан в:
  - `/Users/igorvasin/.hermes/profiles/femida/.env` (TELEGRAM_BOT_TOKEN)
  - `/Users/igorvasin/.hermes/.env` (TELEGRAM_BOT_TOKEN)
- Gateway перезапущен: `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-femida`
  (новый PID ~21183). В логе: «Connecting to Telegram (attempt 1/8)» — токен принят.

---

## Что проверить (новая сессия)

1. **femida в ТГ:** написать @femida03132_bot — должна ответить как юрист (проверка договоров/рисков),
   НЕ scam. Если молчит — смотреть `~/.hermes/profiles/femida/logs/gateway.error.log`.
2. **Остальные боты (angela/bitrix/ptenchikova)** на VPS — должны работать через VPS-OmniRoute (20128).
3. **VPS-OmniRoute стабильность:** после ребута VPS — проверить `systemctl is-active omniroute`
   и `curl 127.0.0.1:20128/v1/models`. Если упадёт — см. п.1 (прокси/NO_PROXY).

---

## Важные заметки

- **Туннель `vps-tunnel` (Мак→VPS)** правился: добавлены форварды
  `-L 2222:127.0.0.1:22` и `-L 2223:127.0.0.1:20128` в `~/.vps-tunnel.sh`.
  Нужны для доступа к VPS (домашний IP меняется, ufw вайтлист 95.154.153.47 + 185.77.216.28).
- **Mac-OmniRoute** тоже работает (порт 20128 на Маке, 614 моделей) — но боты НЕ должны на него
  ходить (это была временная костыль-заплутка через reverse-tunnel 20129, потом откачена).
- **Прямой Nous API** (inference-api.nousresearch.com) для бесплатных моделей требует плату (x402),
  поэтому бесплатные модели Nous доступны ТОЛЬКО через OmniRoute. Вариант «Nous без OmniRoute» — не бесплатный.

---

## Кому что принадлежит

| Сервис | Где | Порт |
|--------|-----|------|
| OmniRoute | VPS (systemd) | 20128 |
| OmniRoute | Мак (launchd com.user.omniroute) | 20128 |
| Hermes gateway | VPS (systemd) | 8642 |
| Hermes gateway femida | Мак (launchd ai.hermes.gateway-femida) | — |
| Боты angela/bitrix/ptenchikova | VPS (pm2) | — |
| femida-bot | Мак (launchd) | — |
