# SESSION_LATEST.md — отчёт 29.10.2026 (AI-Traffic PRO: редизайн под Corporate Elegance Hub)

## Что делали

Редизайн главной страницы `ai-traffic-pro.ru` под референс **Corporate Elegance Hub**
(<https://motiondesignspain.github.io/Google-Stitch-Style-Hub/demos/corporate.html>)
в отдельной ветке `redesign` репозитория `Erik03132/ai-traffic-pro-landing`.

## Результат

- **Fixed (код изменён, не принят):** коммит `ad0e7f1` — заменены токены палитры на
  «сапфировые» (#1e3a5f/#2d5a87), добавлены свои `--shadow-soft/card/elevated` с вертикальным
  смещением, градиентный hero, тени на карточках/кнопках/хедере, новый `public/logo.svg`
  (щит + график роста), логотип в Header/Footer/ChatWidget, favicon перекрашен в `#1e3a5f`.
- **Rejected (Игорь):** «ну ваабще не похоже» — сравнивал с референсом. Причина: акцент в
  референсе `#0052cc` (яркий синий), а не тёмно-сапфировый; тени горизонтальные мягкие
  с синим подтоном `rgba(9,30,66)`, а не объёмные вертикальные; radius кнопок 4px, не 8px;
  заголовки секций с `border-bottom: 2px`; бейджи с заливкой `#deebff`.
- **Verified (проверено):** `main` в обоих репозиториях не изменён (`git diff origin/main main`
  пусто; в монорепо `main..redesign` пусто); ветка `redesign` запушена в origin;
  dev-сервер отдаёт новые токены (`curl localhost:4322` → `1e3a5f`, `shadow-card`×9,
  `shadow-soft`×22, `shadow-elevated`×2); `logo.svg` → 200.

## Что зафиксировано для следующей сессии

- `docs/design/SPEC-redesign-corporate.md` — точные токены референса, маппинг
  «текущий токен → токен референса», ключевые паттерны (карточки, кнопки, бейджи, поля,
  sticky-nav), список того, что менять нельзя.
- `docs/design/theme-corporate.css` (497 строк) и `docs/design/README-corporate.md` —
  локальные копии темы Stitch (коммиты `47973dd`, `8321177`).

## Не тронуто (по требованию Игоря)

DNS, NS, Worker, секреты, переменные окружения, контент `src/data/site.ts`, порядок секций,
логика форм (`ContactSection.astro`, `submit-lead.ts`), API-адреса. Production не публиковался —
merge в `main` только после согласования.

## Next

1. Переделать `src/pages/index.astro` + компоненты по спеке (палитра, тени, radius, секции).
2. `npm run dev` → показать Игорю локально → получить «да/нет».
3. Preview Cloudflare Pages для `redesign` (проверить, что preview-деплои включены).
4. Согласование → merge в `main` → production.

## Блокировано на Игоря

- DNS/NS на Cloudflare (ATP-17): зона создана, NS выданы, записи внесены, переключение NS
  у регистратора — за Игорем; проверка — после делегирования.
- `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` в секреты репозитория (CI-деплой в Pages
  без них пропускается).
- Включение preview-деплоя для ветки `redesign` в Cloudflare Pages.

---

# SESSION_LATEST.md — отчёт 28.10.2026 (часть 2: Worker + резерв + восстановление VPS)

> Продолжение отчёта от 28.10.2026 («AI-Traffic PRO: выход в прод»). Тот отчёт
> описывал схему «статика → GitHub Pages, API → VPS». Эта часть — доведение
> схемы до схемы пользователя (никакой зависимости от VPS) плюс восстановление
> VPS-инфраструктуры, которую нашли сломанной.

## Главный результат (Verified)

- **Сайт больше не зависит от VPS.** API переведён на Cloudflare Worker
  (`https://ai-traffic-pro-api.erik03132.workers.dev`); VPS оставлен как
  **резерв**, а не как основной путь. Схема пользователя выполнена: на Timeweb
  остался только домен, статика — на GitHub Pages.
- **Заявка не теряется, если Worker недоступен** (троттлинг трафика из РФ):
  браузер идёт на Worker → при сетевой ошибке на резерв (VPS) → если и это
  не вышло, пользователь получает ссылку в Telegram с готовым текстом заявки.
  Проверено сквозняком в браузере на проде: Worker недоступен → форма показала
  success, чат ответил по базе знаний, оба запроса ушли на резерв; лид дошёл
  на VPS (`server/leads/2026-10-28.jsonl`).
- **VPS восстановлен** после удаления каталога `/opt/levitan/projects/`
  (22.10.2026): сайт VezemCip отдавал 500, 13 из 18 процессов ссылались на
  удалённые пути и не пережили бы ребута, `knowledge-api` и голосовой юнит
  были битыми.

## Схема (итоговая)

| Слой | Где | Адрес |
|------|-----|-------|
| Статика | GitHub Pages | `ai-traffic-pro.ru`, `www.` → `185.199.108.153` |
| API (основной) | Cloudflare Worker | `ai-traffic-pro-api.erik03132.workers.dev` |
| API (резерв) | VPS `217.149.23.113` | `api.ai-traffic-pro.ru` → nginx → pm2, порт 3001 |
| LLM | Workers AI внутри CF | `@cf/meta/llama-3.1-8b-instruct-fp8-fast` |
| Бэкап лидов | Workers KV (`LEADS`) | пишется **до** отправки в Telegram |

- Адреса API задаются переменными сборки: `PUBLIC_API_BASE_URL` (Worker),
  `PUBLIC_API_FALLBACK_URL` (VPS-резерв).
- Повтор запроса — **только при сетевой ошибке**. На 5xx повтор запрещён
  (сервер ответил → значит заявка могла уйти, повтор дал бы две заявки);
  на 400/404/429 резерв не пробуем.
- CORS — белый список origin (`ALLOWED_ORIGINS`), не `*`. Rate limit —
  встроенные binding'и CF (10 req/60s, раздельные баки `lead`/`chat`).
- Почему LLM переехал внутрь CF: внешние провайдеры (OpenRouter, Gemini) из
  российских IP отдают 403 — Cloudflare блокирует российские IP; из CF-эджа
  работают. Модели `deepseek-v4-*`/`kimi-k2.6` требуют Workers Paid ($5/мес).

## Код и документация (закоммичено и запушено)

- `src/lib/api-post.ts` (`postJson`) + 12 тестов на правила повтора.
- `worker/src/index.js` — 18 тестов (`worker/src/index.test.js`), проверено
  мутациями: без CORS в `json()` падают 2 теста, без KV-бэкапа — 1, без rate
  limit — 2.
- `server/agent-core.js` — общая логика Worker и VPS-сервера (один источник
  истины, 20 тестов): база знаний, валидация лида, формат сообщения Telegram.
- **ADR-001** `docs/adr/ADR-001-api-on-cloudflare-worker.md` — решение о Worker
  + резерв, причины, отклонённые альтернативы, последствия.
- README и ROADMAP приведены в соответствие с продом (до этого они описывали
  «API на VPS» как основной путь — документация врала).
- `npm test` → 66/66, `astro check` → 0 ошибок, `wrangler deploy --dry-run` →
  29.89 KiB (тесты в бандл не попадают).
- Коммиты запушены в `Erik03132/ai-traffic-pro-landing` (origin/main):
  `fbdbe8e`, `52da759`, `1b51e42`, `138211f`, `13cd244`, `692ad6c`, `ffc9487`,
  `3faec2b`.

## Восстановление VPS (Verified)

Причина поломки: каталог `/opt/levitan/projects/` удалён 22.10.2026; pm2-dump
от 30.09 указывал на эти пути и на удалённый venv, поэтому процессы держали
удалённые inode (`cwd → … (deleted)`), а каталог для них был пуст.

- **Symlink'и** `/opt/levitan/projects/{ai-eggs,angel-backend,levitan}` →
  `/opt/freelance/projects/*`: `vezem-web` **500 → 200 без перезапуска**.
- **venv'ы пересозданы** с `--system-site-packages`: `ai-eggs/.server_venv`,
  `levitan/.server_venv`, `/opt/levitan/.venv`, `angel-backend/.venv`.
  Доустановлено: `markdown2`, `psycopg2-binary`, `flask`, `rank_bm25`,
  `uvicorn`. Все 8 ключевых модулей импортируются.
- **`run_agent.sh` восстановлен** — обёртка запуска python через venv, на
  которую ссылались `angela-bot`, `bitrix-bot`, `server-seller` (файла не было
  нигде). Поведение восстановлено по cmdline живых процессов.
- **`bitrix-bot`**: errored (30 рестартов) → **online**.
- **3 файла `angel-backend` восстановлены из GitHub** (`Erik03132/angel-backend`):
  `server.py`, `bitrix_crm.py`, `delivery_reminder.py`.
- **`pm2 save` выполнен** — до этого дамп был от 30.09 и **не содержал
  `ai-traffic-pro-api`** (создан 28.10), то есть резервный API не поднялся бы
  после ребута. Новый дамп: 16 процессов, все валидны. Бэкап старого:
  `/root/.pm2/dump.pm2.bak-20261028-pre-save`.
- **Конфликт за порт 8002 разрулен**: seller-ботом управляет **systemd-юнит
  `angelochka.service`**, а pm2-`server-seller` запускал тот же `agent/server.py`
  → pm2 уходил в цикл рестартов (133 рестарта). pm2-дубликат удалён.
- **`knowledge-api.service` (8080) починен**: `ExecStart` указывал на
  несуществующий `bin/uvicorn` → `status=203/EXEC`. Починено, `/health` → ok,
  модель загружена, `/docs` → 200.
- **`levitan-agent.service` (8081, голосовой агент LiveKit) починен**:
  `WorkingDirectory=/opt/pipecat-agent` и `ExecStart=/opt/pipecat-venv/...`
  — оба каталога были удалены. Собран venv `/opt/pipecat-venv` (393 МБ):
  `livekit-agents==1.8.9` + плагины `deepgram`/`openai`. Юнит переведён на
  `/opt/freelance/projects/levitan/agent`, **active**, `NRestarts=0`, worker
  зарегистрирован в LiveKit.
- **Финальная проверка (Verified):** все 10 сервисов на VPS отвечают 200;
  pm2 — 16 online, 0 errored, дамп валиден 16/16; systemd — **0 битых
  enabled-юнитов** (было 2); внешне — сайт 200, Worker-API 200, резерв-API 200.

## Второй сервер: `72.56.38.19` — не Timeweb (Verified)

- whois: `NetRange 72.56.0.0-72.56.255.255`, `RIPE`, `Country: NL`.
  В панели Timeweb такого сервера нет — только «Wild Cygnus» = `217.149.23.113`.
- SSH: `Permission denied (publickey,password)` для всех ключей.
- Весь голосовой/CRM-стек живёт на `217.149.23.113` (проверено по pm2 и
  портам). Вывод: `72.56.38.19` — устаревшая запись в документации.
- `projects/ai-eggs/PROJECT.md` и `agent/deploy_to_vps.sh` приведены в
  соответствие (AIEGGS-2).

## AIEGGS-3: сломаны были не только документы, но и рабочие файлы (Fixed + Verified)

Заявленная задача звучала как «38 файлов в документации упоминают старый
сервер». На деле нашлось существенное: часть из них — **исполняемые файлы**,
и они были сломаны.

- **Были сломаны (Fixed):**
  - `resurrect.sh` — указывал на несуществующий `/root/antigravity`. Скрипт
    аварийного восстановления не мог восстановить ничего.
  - `agent/ecosystem.config.cjs` и `.js` — интерпретатор
    `/root/antigravity/ai-eggs/venv/bin/python3` (каталога нет). Следующий
    деплой уронил бы `angela-bot`.
  - `agent/run_agent.sh` — **вообще не было в git**, файл жил только на VPS.
    Из-за этого `angela-bot` и `bitrix-bot` падали после каждого деплоя.
  - `agent/deploy_to_vps.sh` — копировал `ecosystem.config.js` (это
    `angela-vk-bot`) в `ecosystem.config.cjs` (рабочий конфиг `angela-bot`),
    затирая его. Теперь `.js` сохраняется отдельно как
    `ecosystem.config.vk.cjs`, `.cjs` не перезаписывается.
  - `vezem/deploy_cloud.sh` — делал `pm2 delete all` + `pm2 start
    ecosystem.config.cjs`, а корневого `/opt/freelance/ecosystem.config.cjs`
    **не существует**. Скрипт убил бы все 16 процессов и не поднял ни одного.
    Заменено на точечный рестарт + старт реальных ecosystem-файлов.
  - `tools/setup_dtmf_vps.sh` — загружал в несуществующий `/opt/`, поднимал
    `baresip`, конфликтующий с `livekit-sip` за порт 5060.
- **Были неверны в доке:** `PROJECT.md`, `AGENTS.md`, `chp.md`,
  `docs/RECOVERY_RUNBOOK.md` (переписан полностью под реальный сервер),
  `docs/MORNING_REPORT_CASCADE.md`, `SECURITY_FIX_REPORT.md`,
  `data/mango/README.md` + `AUTO_CALL_SETUP.md` (порт Mango-callback
  8080 → **8085**, Verified живым POST'ом 200), `vezem/PRODUCTION.md`,
  `vezem/deploy.sh`, `vezem/deploy_mustai.sh`,
  `vezem/tools/night_audit*.sh`, `vezem/tools/pm2_status.sh`, правила агентов
  `vezem/.agent/rules/*` и `vezem/freelance-agent/.agent/rules/*`.
- **Проверки:** `bash -n` — OK для всех 9 скриптов; `node -e` валидирует оба
  ecosystem-конфига; остатки старого IP/путей — только в комментариях-
  объяснениях и в исторических отчётах (прошлое не переписываем).
- **Синхронизация на VPS (Verified):** 4 файла залиты в
  `/opt/freelance/projects/ai-eggs/` (бэкап: `/root/bak/ai-eggs-20261028-2025/`),
  `chmod +x` проставлен, `pm2 save --force` выполнен (бэкап дампа:
  `/root/.pm2/dump.pm2.bak-20261028-2026`). Дамп валиден: 16 процессов,
  битых путей нет. pm2: 16 online, 0 errored.

## ✅ VK-секрет — ложная тревога, закрыто (28.10.2026)

Изначально я поднял это как блокер. Разбор показал, что блокера нет:

- `VK_CLIENT_ID=2274003` — это **официальное приложение VK для Android**, а не
  приложение владельца. Его `client_secret` публично известен и годами лежит
  в открытых репозиториях (`vkpymusic`, `vk_voices_api`). **Ротировать нечего**
  — доступа к настройкам чужого приложения нет.
- Утечки «своего» ключа не было → `git filter-repo`/BFG **не нужны**.
- Скрипт `agent/_vk_get_token.py` **никем не вызывался** — удалён как мёртвый
  код (вместе с паттерном «логин+пароль в открытом виде»). Значение вычищено
  из `SECURITY_FIX_REPORT.md`, файл помечен закрытым.
- Реальный постинг идёт через токены из `.env` (`VK_SERVICE_TOKEN`,
  `VK_VEZEMCYP_TOKEN`, `VK_USER_TOKEN`) — в git они не попадают.

Остаток (не срочно): в репо есть ещё 3 файла с тем же паттерном логин/пароль,
все мёртвые (0 внешних ссылок): `ingestor/vk_ingestor.py`, `agent/_vk_auth.py`,
`agent/test_vk_auth.py`.

## Что НЕ завершено (Не фейк)

- **ATP-17 (от Игоря):** перенос NS зоны на Cloudflare → привязка домена к
  Pages. OAuth-токен агента не имеет права `zone.create` (ошибка 9109), в
  панели CF зон нет; `dash.cloudflare.com` с российского IP отдаёт 403
  «Just a moment…». Нужен вход Игоря в дашборд.
- **ATP-14:** кастомный домен `api.ai-traffic-pro.ru` для Worker — та же
  блокировка (нужен перенос NS). Сайт при этом работает: домен не нужен для
  работы, только для красоты и независимости от CF-блокировок. После переноса
  NS — обязательно **перевести резерв на отдельный хост** (например
  `api-vps.ai-traffic-pro.ru`), иначе резерв станет той же инфраструктурой CF.
- **VPSFIX-10 (доделан, Verified):** `levitan-agent.service` (голосовой агент
  LiveKit, 8081) — venv `/opt/pipecat-venv` собран (393 МБ, livekit-agents
  1.8.9 + плагины deepgram/openai), юнит переведён на
  `WorkingDirectory=/opt/freelance/projects/levitan/agent` (бэкап
  `levitan-agent.service.bak-20261028`), `NRestarts=0`, порт 8081 → 200.
- **VPSFIX-11:** три исходника (`server_seller.py`, `server_bitrix.py`,
  `server_expert.py`) утеряны безвозвратно — нет на диске, в git-истории, в
  репозиториях, в бэкапах; следы только в syslog. Функциональность закрыта
  `agent/server.py`; 8003/8004 никем не используются (grep пуст, `ufw` закрыт).
- **ATP-8 (остаток):** email `erik03132@gmail.com` — личная почта, не
  доменная. При заведении `@ai-traffic-pro.ru` обновить `src/data/site.ts`.
- **ATP-9:** мобильные экраны в Stitch — адаптив сделан на глаз.
- Сертификат `vezemcip.ru` на VPS обновлять нельзя (домен у стороннего
  партнёра, регистрация истекла) — renewal-конфиг отключён. Сам домен
  `vezemcip.ru` указывает на **другой IP** (`88.212.208.67`), который
  не отвечает; nginx-vhost на VPS работает, но публично недоступен.

## Status

Прод сайта работает и не зависит от VPS. VPS восстановлен и переживает ребут
(pm2-дамп валиден, systemd-юниты починены). Блокер для полного «красивого»
завершения — один: **доступ Игоря в `dash.cloudflare.com`** (ATP-17/ATP-14).
