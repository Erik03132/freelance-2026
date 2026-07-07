# 🔐 Список ключей для ротации

> **ВСЕ перечисленные ключи были в git-истории и скомпрометированы.**
> **Нужно создать НОВЫЕ ключи, а старые удалить.**

---

## 1. OpenRouter API Keys

| Где используется | Старый ключ | Действие |
|------------------|-------------|----------|
| ai-levitan | `sk-or-v1-1dd83e5b...` | Удалить → создать новый |
| ai-eggs | `sk-or-v1-1dd83e5b...` | Тот же ключ |
| ai-bureau | `sk-or-v1-1dd83e5b...` | Тот же ключ |
| ai-grant-consalt | `sk-or-v1-6100c265...` | Удалить → создать новый |
| ai-senat (archive) | `sk-or-v1-7979a446...` | Удалить → создать новый |
| angel-backend | `sk-or-v1-7979a446...` | Тот же ключ |

**Как заменить:**
1. https://openrouter.ai/settings/keys
2. Удалить ВСЕ старые ключи
3. Создать 1-2 новых ключа
4. Обновить `.env` файлы

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
