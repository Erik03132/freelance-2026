# 📘 VK INTEGRATION SKILL
# Навык: Работа с VK API — публикация постов, загрузка фото, токены
# Создан: 03.05.2026 (из боевого опыта ai-eggs / IncuBird)
# Обновлён: 03.05.2026 — миграция на vk_api, VKPoster base class
# SSoT: этот файл — единственный источник правды по VK API

---

## 📦 СТЕК БИБЛИОТЕК

### [`python273/vk_api`](https://github.com/python273/vk_api) ⭐ 1.4k — ОСНОВНАЯ
```bash
pip install vk_api
```

**Решает проблему загрузки фото ОДНОЙ СТРОКОЙ** (вместо ручного multipart):
```python
import vk_api
from vk_api import VkUpload

vk_session = vk_api.VkApi(token="vk1.a.XXXXX")
vk = vk_session.get_api()
upload = VkUpload(vk_session)

# Загрузка фото — ОДНА строка вместо 50 строк urllib
photos = upload.photo_wall('photo.jpg', group_id=238230663)
attachment = f"photo{photos[0]['owner_id']}_{photos[0]['id']}"

# Публикация
vk.wall.post(owner_id=-238230663, from_group=1,
             message="Текст", attachments=attachment)
```

### Другие полезные GitHub-репозитории

| Репо | ⭐ | Что делает | Нам полезно |
|------|-----|-----------|-------------|
| [vkbottle/vkbottle](https://github.com/vkbottle/vkbottle) | 491 | Async VK framework (боты) | Альтернатива для ботов |
| [alcortazzo/vktgbot](https://github.com/alcortazzo/vktgbot) | 123 | Репост VK → Telegram | Кросспостинг |
| [Bizordec/vk-to-tgm](https://github.com/Bizordec/vk-to-tgm) | 49 | VK wall → TG channel (Celery) | Автоматический кросспост |
| [sergo-code/VKGroupParser](https://github.com/sergo-code/VKGroupParser) | 53 | Парсер постов + MongoDB + TG бот | Анализ конкурентов |
| [voronind/vk](https://github.com/voronind/vk) | 396 | Простой VK API wrapper | Лёгкая альтернатива |
| [prostomarkeloff/vkwave](https://github.com/prostomarkeloff/vkwave) | 230 | Async high-performance VK | Для масштабирования |

---

## 🏗️ АРХИТЕКТУРА КОДА (после рефакторинга 03.05.2026)

```
ai-eggs/agent/
├── vk_poster_base.py       ← 🆕 БАЗОВЫЙ МОДУЛЬ (VKPoster class)
│   ├── VKPoster             — класс: post, upload_photo, create_poll, delete_post
│   ├── fetch_photo_cascade  — Unsplash → Pexels → Pixabay
│   ├── parse_posts_from_file— парсинг markdown постов
│   ├── load_env()           — единая загрузка .env
│   └── load/save_posted_log — лог публикаций
├── vk_podvorye_poster.py   ← Постер «Своё Подворье» (канал Б)
├── vk_vezemcyp_poster.py   ← Постер «ВезёмЦыплят» (канал А)
├── photo_cascade.py         ← Каскадный поиск (legacy, совместимость)
└── photo_cache_builder.py   ← ЛОКАЛЬНЫЙ билдер кеша фото
```

### VKPoster — ключевые методы
```python
from vk_poster_base import VKPoster, load_env

env = load_env()
poster = VKPoster(token=env["VK_PODVORYE_TOKEN"],
                  group_id=env["VK_PODVORYE_GROUP_ID"], env=env)

# Проверка токена
info = poster.check_token()  # → {"ok": True, "name": "...", "members": 42}

# Загрузка фото из файла
attachment = poster.upload_photo("/path/to/photo.jpg")

# Загрузка фото из интернета (каскад Unsplash → Pexels → Pixabay)
attachment = poster.upload_photo_from_url("цыплята бройлер")

# Публикация поста
post_id = poster.post(message="Текст", attachments=attachment)

# Отложенный пост
from datetime import datetime, timedelta
poster.post(message="Текст", publish_date=datetime.now() + timedelta(hours=2))

# Создание опроса
poll = poster.create_poll("Вопрос?", ["Вариант 1", "Вариант 2"])
poster.post(message="Голосуем!", attachments=poll)

# Удаление поста
poster.delete_post(post_id=12345)

# Количество постов на стене
count = poster.get_wall_count()
```

---

## 🔑 ТИПЫ ТОКЕНОВ — КРИТИЧЕСКИ ВАЖНО

| Тип | Как получить | Что умеет | Чего НЕ умеет |
|-----|-------------|-----------|---------------|
| **Community Token** | Настройки группы → Работа с API | wall.post, messages, docs | ❌ photos.getWallUploadServer |
| **User Token** | OAuth через браузер (см. ниже) | ВСЁ включая загрузку фото | истекает через 24ч |

### ⚠️ ЖЕЛЕЗНОЕ ПРАВИЛО
```
photos.getWallUploadServer — ТОЛЬКО USER TOKEN.
Community Token: "Group authorization failed: method is unavailable with group auth"

vk_api + VkUpload — автоматически использует правильные методы,
но ТОКЕН всё равно должен быть User Token для загрузки фото!
```

---

## 🔐 Получение User Token (OAuth Implicit Flow)

### Шаг 1: VK приложение (уже создано)
- **Antigravity Podvorje** → ID: **54572099**
- Тип: Standalone
- Управление: https://vk.com/apps?act=manage

### Шаг 2: Получить токен
Открыть в браузере **С ТОГО ЖЕ КОМПЬЮТЕРА**, с которого будут идти API-запросы:
```
https://oauth.vk.com/authorize?client_id=54572099&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=photos,wall,groups&response_type=token&v=5.199&revoke=1
```
- `revoke=1` — ОБЯЗАТЕЛЬНО! Отзывает старый токен и выдаёт новый с привязкой к текущему IP.
- Авторизоваться аккаунтом **Игоря Васина** (id172382079) — он админ обеих групп.
- Скопировать `access_token=...` из адресной строки.

### Шаг 3: Записать в .env
```bash
VK_USER_TOKEN=vk1.a.XXXXX...
```

### ⚠️ КРИТИЧНО: IP-привязка!
- Токен привязывается к IP при **получении** через браузер.
- Если API-запросы идут с ДРУГОГО IP (VPS, VPN, другой Mac) → `access_token was given to another ip address`.
- **Решение:** получать токен с того же IP, откуда будут запросы.
- Для VPS: использовать **Photo Cache Architecture** (загрузка фото локально → кеш → деплой).

### ⚠️ Срок жизни: 24 часа!
После истечения нужно повторить Шаг 2 и обновить `.env`.


---

## 📸 ФОТО В VK — АРХИТЕКТУРА КАСКАДА

### Проблема: VPS IP заблокирован стоковыми сервисами
Датацентровые IP (72.56.38.19 и подобные) **блокируются** Pexels, Pixabay, Unsplash.
Признак: локально API работает (200), с VPS — 403 или SSL timeout.

### Решение: Photo Cache Architecture
```
Локальный Mac (сеть работает)        VPS (сеть заблокирована)
Unsplash API                          photo_cache.json
     ↓ скачать                              ↓ читать attachment ID
vk_poster_base.py                    vk_podvorye_poster.py
  (VKPoster.upload_photo_from_url)     (poster.post с attachment из кеша)
     ↓ загрузить в VK
photo_cache.json ──── scp ───────────→ /root/antigravity/ai-eggs/data/
```

### Workflow загрузки фото (полный цикл)
```bash
# 1. Локально: загрузить фото в VK и закешировать IDs
cd ~/freelance-2026/ai-eggs
python3 agent/photo_cache_builder.py build

# 2. Задеплоить кеш на VPS
scp -i ~/.ssh_agent_key data/photo_cache.json \
    root@72.56.38.19:/root/antigravity/ai-eggs/data/

# 3. На VPS постер сам подхватит из кеша
```

---

## 🌐 ИСТОЧНИКИ СТОКОВЫХ ФОТО

| Приоритет | Сервис | Ключ в .env | Лимит | Статус |
|-----------|--------|-------------|-------|--------|
| 1 | **Unsplash** | `UNSPLASH_ACCESS_KEY` | 50 req/час | ✅ Работает локально |
| 2 | **Pexels** | `PEXELS_API_KEY` | 200 req/мес | ⚠️ Ключ 403 (pending?) |
| 3 | **Pixabay** | `PIXABAY_API_KEY` | 100 req/мин | ✅ Работает локально |

### Диагностика источников
```bash
python3 agent/photo_cascade.py test --keywords="цыплята бройлер"
```

---

## 📮 ПУБЛИКАЦИЯ ПОСТОВ

### Через VKPoster (РЕКОМЕНДУЕМЫЙ СПОСОБ)
```python
from vk_poster_base import VKPoster, load_env

env = load_env()
poster = VKPoster(token=env["VK_PODVORYE_TOKEN"],
                  group_id=env["VK_PODVORYE_GROUP_ID"])

# Простой пост
poster.post(message="Привет мир!")

# Пост с фото из файла
att = poster.upload_photo("photo.jpg")
poster.post(message="Пост с фото", attachments=att)

# Пост с фото из интернета (каскад)
att = poster.upload_photo_from_url("цыплята несушки")
poster.post(message="Текст", attachments=att)
```

### CLI-команды постеров
```bash
# Подворье
python3 agent/vk_podvorye_poster.py check_token
python3 agent/vk_podvorye_poster.py status
python3 agent/vk_podvorye_poster.py post 1
python3 agent/vk_podvorye_poster.py post_all
python3 agent/vk_podvorye_poster.py schedule

# ВезёмЦыплят
python3 agent/vk_vezemcyp_poster.py check_token
python3 agent/vk_vezemcyp_poster.py status
python3 agent/vk_vezemcyp_poster.py test_post
python3 agent/vk_vezemcyp_poster.py test_post_photo /path/to/photo.jpg
python3 agent/vk_vezemcyp_poster.py post 1
python3 agent/vk_vezemcyp_poster.py schedule
```

### ⚠️ Удаление постов
Community Token **НЕ МОЖЕТ** удалять посты через `wall.delete`.
Удалять только вручную через интерфейс ВК или через User Token.

---

## 🔧 ДИАГНОСТИКА СЕТИ (Mac + AmneziaVPN)

### Симптом: SSL timeout / curl 000 / ping заблокирован
Причина: AmneziaVPN оставляет мёртвые маршруты через `utun6`.

### Диагностика
```bash
netstat -rn | grep '^default'
# Если первая строка: default → utun6 → ПРОБЛЕМА
# Должно быть: default → 192.168.0.1 (роутер) → en0
```

### Лечение
```bash
# 1. Убить default route через utun6
sudo route delete default -interface utun6

# 2. Если не помогло — выкл/вкл Wi-Fi

# 3. Ядерный вариант — перезагрузить Mac
# После ребута: НЕ открывать AntiGravity Tools!
```

---

## 📁 СТРУКТУРА ФАЙЛОВ (ai-eggs проект)

```
ai-eggs/
├── .env                          ← Все токены и ключи
│   ├── VK_PODVORYE_TOKEN         ← Community Token (Подворье)
│   ├── VK_VEZEMCYP_TOKEN         ← Community Token (ВезёмЦыплят)
│   ├── VK_PODVORYE_GROUP_ID      ← ID группы Подворье
│   ├── VK_GROUP_ID               ← ID группы ВезёмЦыплят
│   ├── VK_USER_TOKEN             ← User Token (фото, 24ч)
│   ├── UNSPLASH_ACCESS_KEY
│   ├── PEXELS_API_KEY
│   └── PIXABAY_API_KEY
├── agent/
│   ├── vk_poster_base.py        ← 🆕 БАЗОВЫЙ модуль (VKPoster)
│   ├── vk_podvorye_poster.py    ← Постер Подворья (на vk_api)
│   ├── vk_vezemcyp_poster.py    ← Постер ВезёмЦыплят (на vk_api)
│   ├── photo_cascade.py         ← Каскадный загрузчик (legacy)
│   └── photo_cache_builder.py   ← ЛОКАЛЬНЫЙ билдер кеша
├── data/
│   └── photo_cache.json          ← VK attachment IDs (→ VPS)
└── vk_content/
    ├── podvorye/
    │   ├── week1_posts.md        ← Контент Подворья
    │   └── posted_log.json       ← Лог публикаций
    └── vezemcyp/
        ├── starter_posts.md      ← Контент ВезёмЦыплят
        ├── assets/               ← Локальные фото для постов
        └── posted_log.json       ← Лог публикаций
```

---

## 🚀 БЫСТРЫЙ СТАРТ (новая сессия)

```bash
# 1. Проверить сеть
curl -s -o /dev/null -w "%{http_code}" https://google.com
# 200 — OK, 000 — нет сети (см. диагностику VPN выше)

# 2. Установить vk_api (если ещё нет)
pip install vk_api

# 3. Проверить токены
grep -E "VK_|UNSPLASH|PEXELS|PIXABAY" ai-eggs/.env

# 4. Проверить токен группы
cd ai-eggs && python3 agent/vk_podvorye_poster.py check_token

# 5. Загрузить фото в кеш (если кеш пустой)
python3 agent/photo_cache_builder.py build

# 6. Задеплоить кеш на VPS
scp -i ~/freelance-2026/.ssh_agent_key \
    data/photo_cache.json \
    root@72.56.38.19:/root/antigravity/ai-eggs/data/

# 7. Проверить статус постов
python3 agent/vk_podvorye_poster.py status
```

---

## ❓ ЧАСТО ВСТРЕЧАЕМЫЕ ОШИБКИ

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Group authorization failed` | Community token вместо user token | Получить User Token (см. выше) |
| `HTTP 401` при curl тесте API | `$ENV_VAR` не загружена в shell | Читать из файла или `source .env` |
| `HTTP 403` с VPS | IP датацентра заблокирован | Использовать photo_cache_builder локально |
| `SSL handshake timed out` | Мёртвые VPN маршруты (utun6) | `sudo route delete default -interface utun6` |
| `curl 000` | Нет сети | Проверить `netstat -rn \| grep default` |
| `ImportError: vk_api` | Библиотека не установлена | `pip install vk_api` |
| `VK_GROUP_ID` не та группа | Старый group_id | Проверить club_ID в URL группы ВК |
| `Too many requests per second` | Больше 3 req/сек к VK API | Добавить `time.sleep(0.4)` между вызовами |
| `invalid scope` | Приложение не поддерживает scope | Использовать Kate Mobile (ID 2685278) |
| `access_token was given to another ip` | Токен привязан к другому IP | Получить новый токен с нужного IP |
| `application is blocked` | VK заблокировал приложение | Не использовать VK Admin (6121396) |
| `market_item_validation-need-main_photo_id` | Товар без фото нельзя создать | Всегда загружать фото перед market.add |

---

## 🛍 VK MARKET API (товары в сообществе)

### Обновлено: 05.05.2026 — из боевого опыта

### ⚠️ КРИТИЧНО: market.* ТРЕБУЕТ User Token!
```
market.add, market.get, market.edit, market.delete,
market.getProductPhotoUploadServer, market.saveProductPhoto
→ ВСЕ эти методы ТРЕБУЮТ User Token (НЕ Community Token!)
→ Community Token даёт: "Group authorization failed"
```

### Получение User Token с market scope

**App ID для OAuth:** `2685278` (Kate Mobile) — единственный проверенный рабочий вариант!

❌ **НЕ работают:**
- App 54572099 (Antigravity) — `invalid_scope` с любым scope
- App 6121396 (VK Admin) — `application is blocked`
- App 2274003 (VK Android) — `incorrect app. Unavailable for apps with direct auth`
- Новый VK ID (id.vk.com) — нет Standalone-приложений, только Web/Mobile

✅ **Рабочая ссылка:**
```
https://oauth.vk.com/authorize?client_id=2685278&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=368644&response_type=token&v=5.199
```
- scope=368644 = market(32768) + photos(4) + groups(262144) + wall(8192) + offline(65536)
- `expires_in=0` → бессрочный (offline scope)
- ⚠️ Привязан к IP с которого открыта ссылка!

### IP-привязка и VPS

Токен привязан к IP компьютера. На VPS (другой IP) → ошибка.

**Решение:** Запускать `vk_market_sync.py` ЛОКАЛЬНО с Mac, не на VPS.
```bash
# Локально на Mac (IP совпадает с токеном):
cd ~/freelance-2026/ai-eggs
python3 agent/vk_market_sync.py --limit 25

# Brain данные скачать с VPS:
scp root@72.56.38.19:/root/antigravity/ai-eggs/data/angelochka_unified_brain.json data/
```

### Загрузка фото товара (новый VK API)

```python
# Шаг 1: Получить upload URL
result = vk_api_call('market.getProductPhotoUploadServer', {
    'group_id': GROUP_ID,
}, use_user_token=True)
upload_url = result['upload_url']

# Шаг 2: POST файл (multipart/form-data)
upload_data = _multipart_upload(upload_url, 'photo.png')

# Шаг 3: Сохранить фото в системный альбом
save_result = vk_api_call('market.saveProductPhoto', {
    'upload_response': json.dumps(upload_data),
}, use_user_token=True)
photo_id = save_result['photo_id']

# Шаг 4: Создать товар
vk_api_call('market.add', {
    'owner_id': f'-{GROUP_ID}',
    'name': 'Цыплята РОСС суточные',
    'description': 'Описание...',
    'category_id': 1,
    'price': '85',
    'main_photo_id': photo_id,  # ← ОБЯЗАТЕЛЬНО!
    'url': 'https://vezemcip.ru',
}, use_user_token=True)
```

### Требования к фото товара
- Форматы: JPG, PNG, GIF
- Минимум: 400×400 px
- Максимум: сумма сторон ≤ 14000 px
- Размер файла: ≤ 50 МБ
- **main_photo_id ОБЯЗАТЕЛЕН** — товар без фото создать нельзя!

### Архитектура файлов Market

```
ai-eggs/agent/
├── vk_market_sync.py     ← Синхронизация brain → VK Market
│   ├── parse_products_from_brain()  — парсинг unified_brain.json
│   ├── upload_market_photo()        — загрузка фото (3-шаговый API)
│   ├── create_vk_product()          — создание карточки товара
│   └── sync_products()              — основной sync с дедупликацией
├── vk_token_manager.py   ← Получение/проверка User Token
│   ├── --auth             — генерация OAuth URL
│   ├── --save-token TOKEN — сохранение в .env
│   ├── --exchange CODE    — обмен code→token (Code Flow)
│   └── --check            — проверка текущего токена
└── sync_products.py      ← Bitrix24 → unified_brain.json (уже был)
```

### CLI синхронизации товаров
```bash
# Dry-run (показать что будет создано)
python3 agent/vk_market_sync.py --dry-run

# Создать первые 5 товаров
python3 agent/vk_market_sync.py --limit 5

# Создать все товары с фото
python3 agent/vk_market_sync.py

# Проверить токен
python3 agent/vk_token_manager.py --check
```
