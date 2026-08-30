# SSoT: OmniRoute + Hermes Agent — дашборды, порты, сервисы

**Создан:** 2026-08-29 (зафиксировано после разбора путаницы с портами)
**Статус:** ЕДИНСТВЕННЫЙ ИСТОЧНИК ИСТИНЫ. Правишь тут → правишь везде.

---

## ⚠️ ГЛАВНОЕ (чтобы не путаться)

| Что открывать в браузере | Адрес | Это что |
|---|---|---|
| **РОДНОЙ OmniRoute дашборд** | **http://127.0.0.1:20128/dashboard** | Настоящий UI OmniRoute (Next.js из пакета). Локальный инстанс на Маке. |
| Hermes веб-интерфейс | http://127.0.0.1:9120 | Hermes Agent web UI (Hermes Desktop / VPS-туннель совпадают по порту). |
| ❌ НЕ родной (НЕ путать) | ~~http://127.0.0.1:8890~~ | Самописный `/root/omni_dashboard.py` на VPS, проброшенный через туннель. Это НЕ OmniRoute. |

**Запомни:** родной OmniRoute = порт **20128** → `/dashboard`. Порт **8890** — это кастомная самописка, не открывать как OmniRoute.

Родной `/dashboard` редиректит на `/login` — UI живой, просит вход (через `POST /api/auth/login`).

---

## 1. Дашборды (что видит пользователь на Маке)

| Сервис | Адрес | Поднят чем | Примечание |
|---|---|---|---|
| OmniRoute (родной) | `127.0.0.1:20128/dashboard` | launchd `com.user.omniroute` (Мак, локально) | PID ноды ~68256. БЕЗ туннеля. |
| Hermes web | `127.0.0.1:9120` | Hermes Desktop приложение (Мак) + туннель на VPS:9120 | |
| OmniRoute API (VPS через туннель) | `127.0.0.1:8743` | туннель `~/.vps-tunnel.sh` → VPS:20128 | VPS-инстанс OmniRoute (отдельный от локального!). |
| Самописный дашборд (VPS) | `127.0.0.1:8890` | туннель → VPS:8890 (`omni-dashboard.service`) | НЕ родной, служебный. |

> Почему VPS- OmniRoute на 8743, а не 20128? Потому что локальный Мак-инстанс уже занимает 20128. Туннель специально мапит VPS:20128 → Mac:8743 во избежание конфликта.

---

## 2. Сервисы на МАКЕ (launchd / LaunchAgents)

Файлы: `~/Library/LaunchAgents/*.plist`. Автостарт при логине пользователя.

| Label | Что | Порт | RunAtLoad/KeepAlive |
|---|---|---|---|
| `com.user.omniroute` | OmniRoute (нода) | 20128 (+20131/20132 WS) | RunAtLoad=true, KeepAlive=true |
| `com.user.omniroute-guard` | watchdog `omniroute_guard.sh` (каждые 300с) | — | StartInterval=300 |
| `ai.hermes.gateway-chief` | Hermes gateway (chief) | — | launchd |
| `ai.hermes.gateway-bridge` | Hermes gateway (bridge) | — | launchd |
| `ai.hermes.gateway-femida` | Hermes gateway (femida) | — | launchd |
| `ai.hermes.gateway-batrak` | Hermes gateway (batrak) | — | launchd |
| `ai.hermes.gateway-personal` | Hermes gateway (personal) | — | launchd |
| `com.user.vps-tunnel` | SSH-туннель `~/.vps-tunnel.sh` | 9120/8742/8743/8890 | launchd |
| `com.user.hermes-sync` | синк Mac↔VPS | — | launchd |

**Проверка:** `launchctl list | grep -iE "omniroute|hermes|vps-tunnel"`

---

## 3. Сервисы на VPS (217.149.23.113, systemd 249 + pm2)

### systemd (юниты в `/etc/systemd/system/`)
| Юнит | Что | Порт | Состояние (после 29.08) |
|---|---|---|---|
| `omniroute.service` | OmniRoute (нода) | 20128/20131/20132 | ✅ active (был failed — чинили) |
| `omni-dashboard.service` | самописный `/root/omni_dashboard.py` | 8890 | ✅ active |
| `hermes-dashboard.service` | Hermes web dashboard | 9120 | ✅ active (был crash-loop — чинили) |
| `hermes-gateway.service` | Hermes gateway (мессенджеры) | 8642 | ✅ active |
| `hermes-serve.service` | Hermes headless backend | 9119 | ✅ active |
| `pm2-root.service` | менеджер pm2 (15 ботов) | — | ✅ active, enabled |

### pm2 (под `pm2-root.service`)
Держит 15 процессов: `angela-bot`, `angela-server`, `angela-autopilot`, `angela-scheduler`, `ptenchikova-bot`, `a2a-dispatcher`, `mango-webhook`, `dtmf-handler`, `vezem-web`, `bitrix-bot`, `levitan-faq`, `levitan-webhook`, `baresip-sip`, `livekit-sip`, `levitan-sip-register`.
**Автостарт pm2:** `pm2-root.service` enabled + `dump.pm2` сохранён.

**Проверка:** `systemctl is-active omniroute hermes-dashboard hermes-gateway hermes-serve pm2-root; pm2 list`

---

## 4. Туннель `~/.vps-tunnel.sh` (Мак → VPS)

Прямой SSH (без RU-SOCKS5; прокси отменён 29.08). Форварды:
```
-L 127.0.0.1:9120:127.0.0.1:9120   # Hermes web (VPS)
-L 127.0.0.1:8742:127.0.0.1:8642   # Hermes gateway API (VPS)
-L 127.0.0.1:8743:127.0.0.1:20128  # OmniRoute API (VPS)
-L 127.0.0.1:8890:127.0.0.1:8890   # самописный дашборд (VPS)
```
Ключ: `~/freelance-2026/.ssh_agent_key`. Ретрай в цикле при обрыве сети.
**Если домашний IP сменился** → VPS не пускает (whitelist в ufw:22/2222). Решение: ТГ-боту «открой <IP> в ufw на VPS (порт 22)».

---

## 5. Что чинили 29.08 (история — не повторять ошибку)

До правки «всё работало через systemd» было ЛОЖЬЮ. Два сервиса лежали:
- `omniroute.service` — **failed**: systemd пытался поднять шлюз на :20128, но порт занят ручным процессом из ssh-сессии → `EADDRINUSE`.
- `hermes-dashboard.service` — **crash-loop** (счётчик 220+): лез в :9120 к осиротевшему `hermes dashboard`.

**Починка:** убрали осиротевшие ручные копии (из ssh-сессий, `session-*.scope`), отдали порты штатным systemd-юнитам. После `systemctl restart` все 6 юнитов active+enabled. Осиротевших копий нет. Hermes-дашборд теперь дитя `system.slice/hermes-dashboard.service` (переживёт ребут).

---

## 6. ЧЕГО НЕ ТРОГАТЬ

- ❌ Не запускать `hermes dashboard` / `omniroute` вручную в ssh на VPS — создаст конфликт портов с systemd.
- ❌ Не путать 8890 (самописный) с 20128 (родной OmniRoute).
- ❌ Не менять сетевой конфиг (.zshrc/прокси) без явного согласия.
- ✅ US-прокси 172.120.21.141 (VPS→зарубеж, Nous/Telegram) — не трогать.
- ✅ RU-SOCKS5 отменён (возврат средств), ходим напрямую.

---

## 7. Веб-панель Hermes (127.0.0.1:9120) — ЭТО АДМИНКА, НЕ ЧАТ

**Важно:** страница `9120/chat` — это НЕ переписка. Это **экран активации сессии** (`chat-activation` = 43 байта, пустышка). Поле ввода там ждёт ID сессии/профиля, поэтому русский текст «тупит». Сам чат (`ChatPage`) живёт через WebSocket (JSON-RPC) и для обычного общения не нужен.

**Где РЕАЛЬНО общаться с агентом:**
- ✅ **Hermes Desktop** (это окно) — основной и рабочий вариант.
- ✅ **Telegram-боты** (6 штук на VPS) — для мобайла/вне дома.

**Веб-панель `9120` = управление, а не диалог.** Не пытайся писать туда сообщения.

### Разделы веб-панели (20 штук, из кода дашборда)
`AnalyticsPage, ChannelsPage, ChatPage, ConfigPage, CronPage, DocsPage, EnvPage, FilesPage, LogsPage, McpPage, ModelsPage, PairingPage, PluginsPage, ProfileBuilderPage, ProfilesPage, SessionsPage, SkillsPage, SystemPage, WebhooksPage`

### Маршрут освоения (по приоритету, не лезь во всё сразу)
1. **ProfilesPage** — профили агента (chief/bridge/femida/batrak/personal). Смотри, не трогай.
2. **ModelsPage / EnvPage** — модели и переменные окружения. Только просмотр, править по инструкции.
3. **SessionsPage / LogsPage** — активные сессии и логи. Сюда заглядывать, если что-то не работает.
4. **SkillsPage / PluginsPage / McpPage** — навыки, плагины, MCP-серверы. Расширение функционала.
5. **ChannelsPage / WebhooksPage / PairingPage** — интеграции (Telegram и т.п.). Уже настроено, не трогать.
6. **ConfigPage / SystemPage / AnalyticsPage / CronPage / FilesPage / DocsPage** — системные настройки, метрики, задачи по расписанию, файлы, дока.

**Совет:** 90% пользователей веб-панель вообще не нужна — достаточно Desktop + ТГ. Веб открывай только когда надо: посмотреть логи, сменить модель, подключить плагин. Всё остальное — через чат.
