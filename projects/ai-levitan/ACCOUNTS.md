# Аккаунты и доступы

## Mango Office (IP-телефония)

| Параметр | Значение |
|----------|----------|
| API Key | см. `.env` (MANGO_VPBX_API_KEY) |
| API Salt | см. `.env` (MANGO_VPBX_API_SALT) |
| API URL | `https://app.mango-office.ru/vpbx/` |
| PBX Domain | `vpbx400374818.mangosip.ru` |
| PBX IP (SIP) | `81.88.86.35:5060` |
| Mango ЛК | https://lk.mango-office.ru |

### Сотрудники/Extensions

| Сотрудник | Ext | SIP | Пароль | Назначение |
|-----------|-----|-----|--------|------------|
| v1000 | 22 | `v1000@vpbx400374818.mangosip.ru` | см. `.env` (ZOIPER_PASSWORD) | Zoiper (оператор) |
| user1 | 23 | `user1@vpbx400374818.mangosip.ru` | см. `.env` (BARESIP_PASSWORD) | baresip (робот-приветствие) |

### Медиафайлы

| ID | Описание |
|----|----------|
| `1000556744` | Приветствие (загружено вручную через ЛК) |

## Telegram

| Параметр | Значение |
|----------|----------|
| Бот | `@levitan_dialer_bot` |
| Bot Token | см. `.env` (TELEGRAM_BOT_TOKEN) |
| Chat ID | `176203333` |
| Команды | `начать обзвон`, `конец обзвона`, `пропустить`, `следующий`, `статус` |

## OpenRouter (LLM)

| Параметр | Значение |
|----------|----------|
| API Key | см. `.env` (OPENROUTER_API_KEY) |
| Основная модель | `deepseek/deepseek-chat-v3-0324` |
| Fallback модель | `qwen/qwen-2.5-7b-instruct` |

## Zoiper 5 (macOS)

| Параметр | Значение |
|----------|----------|
| SIP User | `v1000` |
| Domain | `vpbx400374818.mangosip.ru` |
| Password | см. `.env` (ZOIPER_PASSWORD) |
| Transport | TCP |
| Port | 5060 |

## VPS

| Сервер | IP | Статус |
|--------|-----|--------|
| Levitan | `185.39.206.145` | ⛔ Выключен |
| AI Eggs | `72.56.38.19` | ⛔ Выключен |

## Mac (рабочая станция)

| Параметр | Значение |
|----------|----------|
| Модель | MacBook Air (Apple Silicon) |
| IP (локальный) | `192.168.0.108` |
| IP (публичный) | `95.154.153.47` |

## Примечания по безопасности

- При частых 403 ошибках Mango блокирует IP → сброс: отключить/включить Wi-Fi
- SIP URI в baresip должен быть `sip:user1@...` НЕ `sip:23@...`
- Baresip требует foreground-терминал для работы с аудио
