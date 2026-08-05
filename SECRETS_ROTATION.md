# 🔐 Список ключей для ротации

> **ВСЕ перечисленные ключи были в git-истории и скомпрометированы.**
> **Нужно создать НОВЫЕ ключи, а старые удалить.**

---

## 1. OpenRouter API Keys ✅ ОБНОВЛЕНО

| Где используется | Старый ключ | Действие |
|------------------|-------------|----------|
| ai-levitan | `sk-or-v1-1dd83e5b...` | ✅ Заменён |
| ai-eggs | `sk-or-v1-1dd83e5b...` | ✅ Заменён |
| ai-bureau | `sk-or-v1-1dd83e5b...` | ✅ Заменён |
| ai-grant-consalt | `sk-or-v1-6100c265...` | ✅ Заменён |
| ai-senat (archive) | `sk-or-v1-7979a446...` | ✅ Заменён |
| angel-backend | `sk-or-v1-7979a446...` | ✅ Заменён |
| agent-lab | `sk-or-v1-1dd83e5b...` | ✅ Заменён |
| ai-scout | `sk-or-v1-1dd83e5b...` | ✅ Заменён |
| dashboard | `sk-or-v1-6100c265...` | ✅ Заменён |

---

## 2. Telegram Bot Tokens

| Где используется | Старый токен | Действие |
|------------------|--------------|----------|
| ai-levitan | `8776258870:AAEvEAQNRL4N...` | @BotFather → /revoke |
| ai-eggs | `8703086989:AAHf8Nw8fd2X...` | @BotFather → /revoke |

**Как заменить:**
1. @BotFather → /mybots
2. Выбрать бота → API Token → Revoke
3. Скопировать новый токен
4. Обновить `.env` файлы

---

## 3. Google Gemini API Keys

| Где используется | Старый ключ | Действие |
|------------------|-------------|----------|
| ai-grant-consalt | `AIzaSyB1G9IxIDv8...` | Удалить → создать новый |
| ai-senat | `AIzaSyB7g7QQLPO4...` | Удалить → создать новый |
| ai-eggs | `AIzaSyC9l5XLl4QG...` | Удалить → создать новый |
| ai-eggs | `AIzaSyDHrlv13hQM...` | Удалить → создать новый |
| ai-bureau | `AIzaSyDNy9_KkLbi...` | Удалить → создать новый |
| dashboard | `AIzaSyB1G9IxIDv8...` | Тот же ключ |
| dashboard | `AIzaSyCH2ZkWKuI1...` | Удалить → создать новый |

**Как заменить:**
1. https://console.cloud.google.com/apis/credentials
2. Удалить старые ключи
3. Создать новые
4. Обновить `.env` файлы

---

## 4. Perplexity API Keys

| Где используется | Старый ключ | Действие |
|------------------|-------------|----------|
| ai-grant-consalt | `pplx-0ya0VPkHwn...` | Удалить → создать новый |
| ai-senat | `pplx-0ya0VPkHwn...` | Тот же ключ |
| ai-eggs | `pplx-0ya0VPkHwn...` | Тот же ключ |
| ai-bureau | `pplx-0ya0VPkHwn...` | Тот же ключ |
| dashboard | `pplx-0ya0VPkHwn...` | Тот же ключ |

**Как заменить:**
1. https://www.perplexity.ai/settings/api
2. Удалить старый ключ
3. Создать новый
4. Обновить `.env` файлы

---

## 5. GitHub Token

| Где используется | Старый токен | Действие |
|------------------|--------------|----------|
| dashboard | `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` | Удалить → создать новый |

**Как заменить:**
1. https://github.com/settings/tokens
2. Удалить старый токен
3. Создать новый (repo, workflow)
4. Обновить `.env` файлы

---

## 6. Neon Database

| Где используется | Строка подключения | Действие |
|------------------|-------------------|----------|
| ai-grant-consalt | `npg_YUbMN2FpBKf9@...` | Сменить пароль в Neon |
| ai-senat | `npg_buzQZOKe3cf7@...` | Сменить пароль в Neon |
| ai-eggs | `npg_buzQZOKe3cf7@...` | Тот же ключ |
| angel-backend | `npg_buzQZOKe3cf7@...` | Тот же ключ |

**Как заменить:**
1. https://console.neon.tech
2. Выбрать проект → Settings → Users
3. Сменить пароль для `neondb_owner`
4. Обновить `NEON_DATABASE_URL` в `.env`

---

## 7. Mango API Keys ✅ ОБНОВЛЕНО

| Где используется | Старый ключ | Действие |
|------------------|-------------|----------|
| ai-levitan | `k0ockrwsafuf7tfpuk7fkqtps4nl77o8` | ✅ Заменён на `n13i3gcy6ddqbswzjqfb3qggat4o67mt` |
| levitan | `k0ockrwsafuf7tfpuk7fkqtps4nl77o8` | ✅ Заменён на `n13i3gcy6ddqbswzjqfb3qggat4o67mt` |

---

## 8. SIP пароли (Mango)

| Сотрудник | Старый пароль | Действие |
|-----------|---------------|----------|
| v1000 (ext 22) | `p?BJq78tmDk2` | ЛК Mango → Сотрудники → сменить |
| user1 (ext 23) | `25!vsnzQ6m6H` | ЛК Mango → Сотрудники → сменить |

**Как заменить:**
1. https://lk.mango-office.ru → Сотрудники
2. Открыть сотрудника → Сменить пароль
3. Обновить `.env` файлы и Zoiper/baresip

---

## Приоритет ротации

| Приоритет | Сервис | Почему |
|-----------|--------|--------|
| 🔴 КРИТИЧНО | OpenRouter | Платный API, могут потратить деньги |
| 🔴 КРИТИЧНО | Telegram Bot | Могут отправлять спам |
| 🔴 КРИТИЧНО | GitHub Token | Доступ к репозиториям |
| 🟡 ВАЖНО | Google Gemini | Платный API |
| 🟡 ВАЖНО | Perplexity | Платный API |
| 🟡 ВАЖНО | Mango API | Доступ к телефонии |
| 🟢 СРЕДНЕ | Neon DB | Доступ к базе данных |
| 🟢 СРЕДНЕ | SIP пароли | Доступ к телефонии |

---

## Файлы .env для обновления

После ротации ключей обновить:

```
projects/ai-levitan/.env
projects/ai-eggs/.env
projects/ai-bureau/.env.local
projects/levitan/.env
projects/angel-backend/.env
projects/angel-backend/.env.sandbox
dashboard/.env.local
ai-grant-consalt/.env
ai-grant-consalt/bot/.env
```

---

## Дата создания списка: 07.07.2026
## Статус: ТРЕБУЕТСЯ РОТАЦИЯ ВСЕХ КЛЮЧЕЙ

---

## ➕ Дополнение от аудита 2026-08-02 (ai-defender + gitleaks)

> Живые секреты закоммичены в GitHub. Считаются скомпрометированными → ротация обязательна.

| Ключ | Где | Опасность | Действие |
|------|-----|-----------|----------|
| 🔴 Funpay API-ключ (`Funpay_MYbt...`) | `opencode.json` (в дереве + история) | Доступ к платным LLM, сжигание денег | ✅ ЗАКРЫТ (02.08): провайдер wellflow/funpay больше НЕ существует в opencode — ключ мёртв, ротация не нужна. Провайдер удалён из `opencode.json`. Ключ остался только в git-истории (см. SEC-11). |
| 🔴 OmniRoute JWT_SECRET | `tools/omni-auto-router/omniroute-recover.sh` | Подделка JWT шлюза :20128 | ✅ РОТИРОВАН (02.08): `openssl rand -hex 32`, обновлён скрипт + VPS `.env`, pm2 restarted, `/v1/models` = 200. Бэкап VPS `.env.bak-2026-08-03` |
| 🔴 OmniRoute API_KEY_SECRET | там же | Доступ к API шлюза | ✅ РОТИРОВАН (02.08): новый `openssl rand -hex 32` в скрипте + VPS |
| 🔴 OmniRoute INITIAL_PASSWORD | там же (`Levitan2026!`) | Пароль доступа к шлюзу | ✅ РОТИРОВАН (02.08): новый пароль — в gitignored `tools/omni-auto-router/.env` (INITIAL_PASSWORD), dashboard-логин с новым паролем |
| 🟠 GCP API-ключи | `.cursor/rules/...`, `CHRONICLE.md` (история) | Платный GCP | Ротация в GCP Console |
| 🟠 Mango ключ+salt | `mango_api.py` (история) | Телефония | Ротация в кабинете Mango |
| 🔴 Watchdog TG-токен (`8336409939:AAHr2wbu...`) | `tools/scripts/watchdog.py` (в дереве + история) | Спам в TG от имени бота | ✅ ЗАКРЫТ (02.08): токен МЁРТВ (getMe → 401, это старый токен Анжелочки; активный `AAH8fos...`). Ротация не нужна. Код параметризован (SEC-4), следы убраны из `watchdog.py`, `send_report_today.py`, `angel-backend/.env.sandbox`. В истории остался → SEC-11 |

**Проверить:** публичность репозитория `github.com/Erik03132/freelance-2026` → ✅ **СДЕЛАНО (02.08): репо был PUBLIC → теперь PRIVATE** (`gh repo edit --visibility private`). Экспозиция секретов была публичной до этой даты. Secret scanning недоступен для аккаунта (422).

## ➕ SEC-5 (02.08): levitan SQLi ×4 + path traversal — ИСПРАВЛЕНЫ
`crm/app.py` — whitelist `_SAFE_CONDITIONS` (статич. шаблоны WHERE), whitelist `CONTACT_COLUMNS` (UPDATE SET), `/api/import` защищён от path traversal (`Path(filename).name`). ruff/py_compile чисты.

## ➕ SEC-6 (02.08): levitan chmod + MD5 — ИСПРАВЛЕНЫ
FIFO `0o777`→`0o600` (fifo_bridge.py), MD5→SHA256 (tts_engine.py кэш-ключ, upload_greeting.py command_id). `smart_dialer_zadarma_old.py` не трогал — MD5 требует протокол Zadarma.

## ➕ SEC-8/9 (02.08): gitleaks + переносимые хуки — ГОТОВО
`.gitleaks.toml` закоммичен, `no-secrets` через pre-commit. Хук-скрипты перенесены из `.git/hooks/` в версионируемые `githooks/`, `.pre-commit-config.yaml` обновлён, корневой `README.md` с шагом `pre-commit install`.
