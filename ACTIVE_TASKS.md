# ACTIVE_TASKS.md — активное (перекомпактировано 2026-10-10)

> SSoT активных задач. Августовские истории, идеи и отчёты — в архиве:
> `checkpoints/active_tasks_archive_202608.md` (см. указатели в секциях).
> Предыдущая версия: `ACTIVE_TASKS.md.bak-20261010`.

> ⏰ **ПОРЯДОК ДНЯ (25.10.2026):** лендинг на подходе → как готов первый
> превью — прогнать через паттерн 🧪 UXT (4 персоны-субагенты, first-users).
> Записано в UXT-2, НЕ забыть.

## 🌐 ATP — AI-Traffic PRO: прод на GitHub Pages + API на Cloudflare Worker (28.10.2026) ✅ Verified

> Репозиторий: `Erik03132/ai-traffic-pro-landing` (origin), рабочая копия
> `~/freelance-2026/projects/ai-marketing` (в монорепо не отслеживается).

- [x] **ATP-1 (Verified):** DNS переключён на GitHub Pages. A-записи
  `ai-traffic-pro.ru` и `www.ai-traffic-pro.ru` → `185.199.108.153`,
  `api.ai-traffic-pro.ru` → `217.149.23.113` (Wild Cygnus). Распространение
  подтверждено на 8.8.8.8 / 1.1.1.1 / 9.9.9.9.
- [x] **ATP-2 (Verified):** HTTPS. Сертификат GitHub (Let's Encrypt, до 2027-01-04)
  покрывает apex + www. `http → 301 → https`. `www → 301 → apex`.
- [x] **ATP-3 (Verified):** API на поддомене. **Основной путь — Cloudflare
  Worker** (`https://ai-traffic-pro-api.erik03132.workers.dev`, см. ATP-13);
  **резерв — VPS** `https://api.ai-traffic-pro.ru/api/health/` →
  `{"ok":true,"telegram":true}`; CORS по белому списку `ALLOWED_ORIGINS`
  (чужой origin → без заголовков). Заявка с разрешённого origin → 200,
  в pm2-логе `✅ Заявка отправлена в Telegram`. DNS-запись `api` на Timeweb
  пока указывает на VPS (`217.149.23.113`) — переключится на Worker после
  переноса NS (ATP-14).
- [x] **ATP-4 (Verified):** LLM-канал виджета — `source: "llm"` (9.6 с), ответы
  не выдумывают цены/кейсы. При недоступности — `source: "fallback"`, не 500.
- [x] **ATP-5 (Verified):** 14 маршрутов на проде → 200; несуществующий путь → 404;
  цен («₽») на главной нет.
- [x] **ATP-6 (Fixed):** автообновление apex-сертификата на VPS отключено
  (`renewal/ai-traffic-pro.ru.conf.disabled`) — после ухода DNS на Pages
  HTTP-01-челлендж до VPS не доходит. Сертификат оставлен для отката.
- [x] **ATP-7 (Verified):** `certbot renew --dry-run` для `api.ai-traffic-pro.ru` →
  «all simulated renewals succeeded». Таймер `certbot.timer` + `/etc/cron.d/certbot` активны.
- [x] **ATP-10 (Fixed + Verified):** автообновление сертификатов на VPS починено.
  Системный `/usr/bin/certbot` (1.21.0) падал с `ImportError` (pip-пакеты в
  `/usr/local/lib/python3.10/dist-packages` перекрыли urllib3) — автообновление
  не работало ни для одного сертификата. `certbot.service` и `/etc/cron.d/certbot`
  переведены на рабочий `/opt/certbot-venv/bin/certbot` (5.8.0) + доустановлен
  `certbot-nginx`. Проверка: `systemctl start certbot.service` → `0/SUCCESS`.
- [x] **ATP-11 (Fixed):** отключён `renewal/vezemcip.ru.conf` — домен обслуживает
  сторонний партнёр (DNS → 88.212.208.67, регистрация истекла), его renewal ронял
  весь `certbot renew` на VPS.
- [x] **ATP-8 (Fixed + Verified):** рабочий email `erik03132@gmail.com` прописан в
  `SITE.legal.email` → выводится в футере (`mailto:`), в реквизитах оператора на
  `/privacy/` и `/consent/`, в JSON-LD (`org.email`) и в `public/llms.txt`.
  Прод проверен: `curl https://ai-traffic-pro.ru/{,privacy/,consent/,requisites/,llms.txt}`
  — адрес везде. **Остаток:** это личная почта, не доменная — при заведении
  `@ai-traffic-pro.ru` обновить `src/data/site.ts`.
- [x] **ATP-12 (Fixed + Verified):** сборка в GitHub Actions падала на Astro 7 —
  раннер отдавал Node 22.23.3 при требуемом `>=22.23.4`. В
  `.github/workflows/deploy.yml` `node-version` закреплён на `24`.
- [ ] **ATP-9 (от Игоря):** мобильные экраны в Stitch (адаптив сделан на глаз).
- [x] **ATP-13 (Fixed + Verified):** API переведён с VPS на Cloudflare Worker —
  сайт больше не зависит от VPS. `ai-traffic-pro-api.erik03132.workers.dev`
  (аккаунт `Erik03132@gmail.com's Account`, ID `610715a2ab95ac2c3540caf469796412`).
  Общая логика вынесена в `server/agent-core.js` (база знаний, валидация лида,
  формат сообщения Telegram) — один источник истины для Worker и VPS-сервера;
  покрыта 20 тестами. LLM переехал внутрь CF (Workers AI,
  `@cf/meta/llama-3.1-8b-instruct-fp8-fast`): внешние провайдеры из РФ отдают
  403 (CF блокирует российские IP), из CF-эджа — работают. Бэкап лидов —
  Workers KV (`LEADS`, `6aa58b76b01e4c2f9999578e4234c976`), пишется **до**
  отправки в Telegram. Rate limit — встроенные binding'и `CHAT_LIMITER`/
  `LEAD_LIMITER` (10 req/60s, раздельные баки). Секреты — `wrangler secret put`.
  Проверено: health 200, база знаний, Workers AI, заявка в Telegram (`✅` в логах
  `wrangler tail`), CORS по белому списку, OPTIONS 204, 404, доступ из РФ
  (180 мс с VPS-IP), сквозная проверка формы в браузере на проде.
  Переключение сайта: GitHub Actions variable `PUBLIC_API_BASE_URL`.
  Коммиты `fbdbe8e`, `52da759`, `1b51e42`.
- [x] **ATP-13a (Fixed + Verified):** баг `applyCors is not defined` — при выносе
  общей логики в `agent-core.js` мой скрипт вырезал `ALLOWED_ORIGINS` и
  `applyCors` из `server/server.js`. VPS-API падал с `ReferenceError` на любом
  запросе (health/chat/lead → 000). Восстановлено, VPS перезапущен,
  error-лог pm2 пуст после серии запросов. Закрыт интеграционным тестом
  `server/server.test.js` (7 тестов: сервер поднимается на свободном порту) —
  проверено мутацией: без `applyCors` тест падает. `npm test` → 36/36.
- [ ] **ATP-14 (от Игоря, косметика — не блокер работы):** перенос NS зоны
  `ai-traffic-pro.ru` с Timeweb на Cloudflare. Без этого кастомный домен
  `api.ai-traffic-pro.ru` привязать к Worker нельзя: CNAME-setup и
  subdomain-setup доступны только на Business/Enterprise, на Free — только
  primary setup (перенос NS всей зоны). Подтверждено документацией CF
  (dns/zone-setups).
  **Эмпирически проверено 28.10 (не документом, а экспериментом):** CNAME в
  Timeweb НЕ публикуется авторитетным NS. Тестовая запись
  `api-test → ai-traffic-pro-api.erik03132.workers.dev` появилась в панели,
  но авторитетный NS отдавал `NXDOMAIN`, SOA serial зоны не менялся, публичные
  резолверы — пусто. Тестовая запись удалена, все 6 рабочих записей на месте.
  Значит CNAME-путь закрыт технически, остаётся только перенос NS.
  **Схема Игоря при этом уже выполнена:** на Timeweb только домен + переадресация
  на GitHub Pages, API — на Worker. Перенос NS нужен лишь для кастомного домена
  API (красота + независимость от CF-блокировок), а не для работы сайта.
  **Действие Игоря:** войти в `dash.cloudflare.com` (сессии у агента нет —
  OAuth-токен ≠ сессия дашборда; `dash.cloudflare.com` с российского IP отдаёт
  403 «Just a moment…» — риск, что вход не пройдёт), добавить зону
  `ai-traffic-pro.ru` (primary setup, без jump-start) → Cloudflare выдаст
  NS-серверы → в Timeweb («Управление» → «NS-серверы» → «Настроить») заменить
  `ns1-4.timeweb.{ru,org}` на выданные CF. Готовая форма NS в Timeweb
  открыта и доступна. Записи DNS переносятся как есть: `A @ 185.199.108.153`,
  `A www 185.199.108.153`, `A api → Worker (custom domain)`, `MX 10 mx1.timeweb.ru`
  / `20 mx2.timeweb.ru`, `TXT @ v=spf1 include:_spf.timeweb.ru ~all`
  (DKIM-селекторов нет).
  **После переноса NS — обязательно:** (1) раскомментировать `routes` в
  `worker/wrangler.jsonc` (`pattern: api.ai-traffic-pro.ru`, `custom_domain: true`)
  и задеплоить (`npm run worker:deploy`); (2) проверить
  `https://api.ai-traffic-pro.ru/api/health/`; (3) **перевести резерв на
  отдельный хост** (например `api-vps.ai-traffic-pro.ru` + nginx-vhost +
  Let's Encrypt) — иначе резерв станет той же инфраструктурой Cloudflare и
  перестанет быть резервом.
- [x] **ATP-15 (Fixed + Verified):** резервный путь API в браузере. Сайт шёл
  только на один адрес: если Worker недоступен по сети (троттлинг трафика
  из РФ), форма отдавала «сетевую ошибку», а заявка терялась. Добавлен
  `src/lib/api-post.ts` (`postJson`) — Worker → при сетевой ошибке резерв на
  VPS; **повтор только при сетевой ошибке** (на 5xx повтор запрещён: сервер
  ответил — значит заявка могла уйти, повтор дал бы две заявки; на 400/404/429
  резерв не пробуем). Если не сработало ни то, ни другое — форма показывает
  ссылку в Telegram с готовым текстом заявки. 12 тестов на правила повтора.
  Адреса API — из переменных сборки: `PUBLIC_API_BASE_URL` (Worker),
  `PUBLIC_API_FALLBACK_URL` (VPS). Проверено сквозняком в браузере на проде:
  Worker недоступен → форма показала success, чат получил ответ по базе
  знаний, оба запроса ушли на резерв; лид дошёл на VPS
  (`server/leads/2026-10-28.jsonl`), тестовые записи удалены.
  Параллельно: **ADR-001** (`docs/adr/ADR-001-api-on-cloudflare-worker.md`) —
  решение о Worker + резерв, причины (VPS под давлением, 403 внешних LLM
  из РФ), отклонённые альтернативы, последствия; README и ROADMAP приведены
  в соответствие с продом (до этого они описывали «API на VPS» как основной
  путь — документация врала); **18 тестов Worker**
  (`worker/src/index.test.js`) — роутинг, CORS, чат по базе знаний, LLM,
  падение AI → fallback, валидация заявки, KV-бэкап до Telegram, honeypot,
  rate limit, раздельные баки; проверено мутациями (без CORS в `json()` падают
  2 теста, без KV-бэкапа — 1, без rate limit — 2). `npm test` → 66/66,
  `astro check` → 0 ошибок, `wrangler deploy --dry-run` → 29.89 KiB (тесты в
  бандл не попадают). Коммиты `13cd244`, `138211f`, `692ad6c`, `ffc9487`.
- [x] **ATP-16 (Fixed + Verified):** статика переведена на **Cloudflare Pages**.
  GitHub Pages не умеет `_headers` — security-заголовки и `Cache-Control:
  immutable` для `/_astro/` там недоступны (живёт `max-age=600`); это же
  ограничение закрывало Фазу 1 (задачи 1.5, 1.8). Сделано: Pages-проект
  `ai-traffic-pro` (production branch `main`, env_vars с адресами API),
  `public/_headers` (CSP, HSTS, X-Frame-Options, Permissions-Policy,
  Referrer-Policy, nosniff + `/_astro/*` → `max-age=31536000, immutable`),
  `public/_redirects` (`/services/marketplace/` → 301 на `/services/ecommerce/`
  вместо meta-refresh в 2 хопа), `src/pages/404.astro` (без него Pages отдаёт
  на любой мусорный URL главную с кодом 200 — soft-404, дубликат главной в
  индексе), `public/favicon.svg` (на проде был 404; перекрашен в фирменный
  `#004ac6`, оранжевый `#FF3C00` остался от старого Replit-билда).
  Проверено на staging `ai-traffic-pro.pages.dev`: заголовки присутствуют,
  `/_astro/*` → immutable, маркетплейс → 301, мусорный URL → 404,
  favicon → 200; заявка со staging-origin дошла до Telegram и легла в Workers
  KV; CORS Worker'а дополнен origin `https://ai-traffic-pro.pages.dev`
  (без этого форма на staging не отправлялась). Прод (GitHub Pages) уже
  отдаёт новую сборку: favicon 200, 404-страница с `noindex`. CI: новый
  `ci.yml` (`astro check` + тесты + проверка артефактов `_headers`/
  `_redirects`/`404.html`/`favicon.svg` в `dist/`) и `deploy-pages.yml`
  (деплой в Pages; без `CLOUDFLARE_API_TOKEN` шаг пропускается, job зелёный).
  `npm test` → 66/66, `astro check` → 0 ошибок. Коммиты `27ae831`, `d2c9446`.
- [ ] **ATP-17 (от Игоря, блокирует ATP-14/ATP-16):** довести переезд до
  боевого домена. (1) **Создать зону `ai-traffic-pro.ru` в Cloudflare** —
  OAuth-токен агента не имеет права `zone.create` (проверено: ошибка 9109
  «Requires permission com.cloudflare.api.account.zone.create»), в панели
  домена на CF зон нет. (2) Сменить NS в Timeweb на выданные CF. (3) Привязать
  кастомный домен к Pages-проекту (`ai-traffic-pro.ru` + `www`). (4) Завести
  `CLOUDFLARE_API_TOKEN` (шаблон «Edit Cloudflare Workers») и
  `CLOUDFLARE_ACCOUNT_ID` в секреты репозитория — без них CI-деплой в Pages
  пропускается (токен агента не умеет создавать API-токены: ошибка 9109).
  **Риск окна простоя:** между шагом 2 и 3 домен не отвечает — записи A
  указывают на GitHub Pages IP, а если NS переключить до привязки домена,
  Cloudflare не найдёт зону и отдаст 1016/«error 1016». Порядок обязателен:
  зона → NS → привязка домена к Pages → проверка A-записей и TLS.
  **Альтернатива без NS:** оставить домен на GitHub Pages, а Pages использовать
  как staging (`pages.dev`) — тогда задачи 1.5/1.8 на проде не закрываются.
- [x] **ATP-18 (Fixed + Verified):** бот выдумывал определение GEO. На вопрос
  «Что такое GEO?» виджет уходил в LLM и отвечал «GEO — это сокращение от
  Geographic или Geolocation» — путал GEO с геолокацией. Правильный ответ
  («Generative Engine Optimization» — попадание бренда в ответы AI-сервисов)
  был в FAQ сайта (`src/data/site.ts`), но **не в базе знаний бота**: запрос не
  находился по ключевым словам и уходил в модель, а модель выдумывала.
  Найдено при ручной проверке в браузере (28.10), не тестом — тестов на GEO
  не было. Исправлено: правило GEO/AEO и правило SEO в `KNOWLEDGE`
  (`server/agent-core.js`) + определение GEO в `FACTS` (системный промпт
  страхует модель, если вопрос не найдётся в базе). 3 регрессионных теста,
  проверено мутациями: без правила GEO падает 1 тест, без строки в FACTS — 1.
  Проверено на проде: `source: knowledge`, ответ верный; регрессия на остальных
  вопросах не найдена (цены, услуги, e-commerce, сроки, договор — все
  `knowledge`). Worker передеплоен, commit `3faec2b`.
- [ ] **ATP-19 (от Игоря, в работе):** редизайн главной под **Corporate
  Elegance Hub**. Референс: <https://motiondesignspain.github.io/Google-Stitch-Style-Hub/demos/corporate.html>.
  Ветка `redesign` (репозиторий `Erik03132/ai-traffic-pro-landing`), `main` не
  трогаем, production без согласования Игоря не публикуем.
  **Сделано (Fixed):** коммит `ad0e7f1` — палитра, тени, градиенты, `public/logo.svg`,
  логотип в Header/Footer/ChatWidget, favicon перекрашен. **Игорь отклонил:**
  «вообще не похоже» — темная сапфировая палитра (#1e3a5f) и объёмные вертикальные
  тени не совпадают с референсом (там яркий синий #0052cc + горизонтальные мягкие
  тени с синим подтоном rgba(9,30,66)).
  **Спецификация на следующую сессию:** `docs/design/SPEC-redesign-corporate.md`
  (точные токены + маппинг + список паттернов), локальная копия темы —
  `docs/design/theme-corporate.css` (коммиты `47973dd`, `8321177`).
  **Ограничения:** менять только оформление; контент (`src/data/site.ts`),
  порядок секций, логику форм (`ContactSection.astro`, `submit-lead.ts`), API,
  DNS/NS/Worker/секреты/env — не трогать. Логотип принят, не переделывать.
  **Next:** переделать `index.astro` + компоненты по спеке → собрать → показать
  Игорю локально (`npm run dev`) → preview Cloudflare Pages → ждать согласования.

### 🐔 AIEGGS — второй сервер: `72.56.38.19` заменён на `217.149.23.113` (28.10.2026) ✅ Verified

> Проект: `~/freelance-2026/projects/ai-eggs` (Анжелочка / ВеземCip / голосовой стек).

- [x] **AIEGGS-1 (Verified):** разобрано, где на самом деле живёт голосовой и
  CRM-стек. Документ `projects/ai-eggs/PROJECT.md` указывал
  `root@72.56.38.19` и путь `/root/antigravity/ai-eggs/agent/` — это **старый,
  заменённый сервер**. Факты (проверено на живом VPS 28.10.2026):
  - `72.56.38.19` — не Timeweb: whois отдаёт `NetRange 72.56.0.0-72.56.255.255`,
    `RIPE Network Coordination Centre`, `Country: NL`. В панели Timeweb такого
    сервера нет — только «Wild Cygnus» = `217.149.23.113`.
  - SSH на `72.56.38.19` недоступен: `Permission denied (publickey,password)`
    для всех ключей (`.ssh_agent_key`, `~/.ssh/id_ed25519`, ssh-agent). Хост
    жив (ping RTT 1.4 мс), с моего IP все порты видны открытыми — фильтр на
    стороне моего IP; с VPS порт 22 открыт.
  - `projects/ai-eggs/.env` уже указывает `VEZEM_SERVER_IP=217.149.23.113`
    (тот сервер, где есть доступ), `VEZEM_SERVER_USER=root`, пароль есть;
    в git-истории `.env` смены IP не нашлось.
  - **Проверка, что стек переехал целиком:** на `217.149.23.113` в pm2 — весь
    набор из `PROJECT.md`: `angela-scheduler`, `angela-autopilot`, `angela-bot`,
    `angela-test`, `vezem-web` (путь `/opt/levitan/projects/ai-eggs/vezem/dist/server/entry.mjs`),
    плюс `levitan-sip-register`, `dtmf-handler` (порт 8086), `mango-webhook`.
    Код агента — `/opt/freelance/projects/ai-eggs/agent`; рядом uvicorn на 8080,
    Ollama на 11434, pm2-`ai-traffic-pro-api` на 3001.
  - Вывод: `72.56.38.19` — устаревшая запись в документации, отдельного
    «второго сервера» в панели Timeweb не существует. Рабочий сервер один —
    `217.149.23.113`.
- [x] **AIEGGS-2 (Fixed):** документация приведена в соответствие.
  `projects/ai-eggs/PROJECT.md`: `root@72.56.38.19` → `root@217.149.23.113`,
  пути `/root/antigravity/ai-eggs/agent/` → `/opt/freelance/projects/ai-eggs/agent/`,
  vezem → `/opt/freelance/projects/ai-eggs/vezem/`, обновлены примеры
  rsync/ssh, добавлена таблица **systemd-юнитов** (их не было в документе —
  а именно ими управляется seller-бот на 8002 и голосовой стек на 8081) и
  предупреждение о конфликте `angelochka` (systemd) vs `server-seller` (pm2)
  за порт 8002. `projects/ai-eggs/agent/deploy_to_vps.sh`: дефолты путей
  `VPS_DIR` → `/opt/freelance/projects/ai-eggs`,
  `ECOSYSTEM_ROOT` → `/opt/freelance/projects` (были `/opt/levitan/...` —
  существовали только как symlink'и). Синтаксис скрипта проверен (`bash -n`).
- [x] **AIEGGS-3 (Fixed + Verified):** точечная замена старого IP/путей доведена
  до конца. Ключевое — правились **не только документы, но и сломанные рабочие
  файлы** (это и было реальным блокером):
  - **Были сломаны (Fixed):** `resurrect.sh` (указывал на несуществующий
    `/root/antigravity` — аварийное восстановление не могло ничего восстановить),
    `agent/ecosystem.config.cjs` и `.js` (интерпретатор
    `/root/antigravity/ai-eggs/venv/bin/python3` — каталога нет), `agent/run_agent.sh`
    (вообще не было в git — жил только на VPS), `agent/deploy_to_vps.sh`
    (копировал `ecosystem.config.js` → `.cjs`, затирая конфиг `angela-bot`),
    `vezem/deploy_cloud.sh` (делал `pm2 delete all` + `pm2 start ecosystem.config.cjs`
    при **несуществующем** корневом ecosystem-файле → убил бы все 16 процессов
    и не поднял ни одного), `tools/setup_dtmf_vps.sh` (загружал в `/opt/`,
    поднимал `baresip` — конфликт порта 5060 с `livekit-sip`).
  - **Были неверны в доке:** `PROJECT.md`, `AGENTS.md`, `chp.md`,
    `docs/RECOVERY_RUNBOOK.md` (переписан полностью под реальный сервер),
    `docs/MORNING_REPORT_CASCADE.md`, `SECURITY_FIX_REPORT.md`,
    `data/mango/README.md` + `AUTO_CALL_SETUP.md` (порт Mango-callback
    8080 → **8085**, Verified живым POST'ом 200),
    `vezem/PRODUCTION.md`, `vezem/deploy.sh`, `vezem/deploy_mustai.sh`,
    `vezem/tools/night_audit*.sh`, `vezem/tools/pm2_status.sh`,
    правила агентов `vezem/.agent/rules/{IRON_RULES,two-angelas-map}.md`,
    `vezem/freelance-agent/.agent/rules/AUTONOMOUS_SERVER_ACCESS.md`,
    `vezem/freelance-agent/.agent/skills/vk-integration/SKILL.md`.
  - **Проверки:** `bash -n` — OK для всех 9 скриптов; `node -e` валидирует
    оба ecosystem-конфига; остатки `72.56.38.19` / `/root/antigravity` — только
    в комментариях-объяснениях правки и в исторических отчётах
    (`vezem/checkpoints|chronicles|reports`, `_archive/`) — их прошлое не меняем.
  - **Синхронизация на VPS (Verified):** `resurrect.sh`,
    `agent/ecosystem.config.{cjs,js}`, `agent/run_agent.sh` залиты в
    `/opt/freelance/projects/ai-eggs/` (бэкап старых версий:
    `/root/bak/ai-eggs-20261028-2025/`), `chmod +x` проставлен, `pm2 save --force`
    выполнен (бэкап дампа: `/root/.pm2/dump.pm2.bak-20261028-2026`).
    Дамп валиден: 16 процессов, **битых путей нет**. pm2: 16 online, 0 errored.
  - **Побочно найдено и проверено:** сообщения `angela-scheduler` «Скрипт не
    найден: unified_morning_report.py / habr_intelligence.py» — это сбои
    **до** создания symlink (19:28), а логи за 08:00/09:00. Сейчас
    `os.path.exists` → True для обоих (Verified) — проблема устранена сама
    после починки symlink'ов, отдельного кода не требует.
  - **История отчётов/чекпоинтов намеренно не переписывается** — это запись
    о прошлом, а не инструкция.

### 🛠 VPSFIX — восстановление VPS `217.149.23.113` после удаления `/opt/levitan` (28.10.2026) ✅ Verified

> Причина поломки: каталог `/opt/levitan/projects/` удалён 22.10.2026
> (остался пустой `/opt/levitan/vendor`). pm2-dump от 30.09 указывал на эти
> пути и на venv `/opt/levitan/projects/ai-eggs/.server_venv`, поэтому
> процессы держали удалённые inode (`cwd → … (deleted)`, каталог пуст).

- [x] **VPSFIX-1 (Fixed + Verified):** `vezem-web` отдавал **500**
  (`ERR_MODULE_NOT_FOUND: …/vezem/dist/server/pages/index.astro.mjs`) — сайт
  VezemCip был мёртв. Восстановлен symlink'ами
  (`/opt/levitan/projects/{ai-eggs,angel-backend,levitan}` →
  `/opt/freelance/projects/*`) — **500 → 200 без перезапуска процесса**.
  Проверено: `curl :4321` → 200.
- [x] **VPSFIX-2 (Fixed + Verified):** venv'ы пересозданы с
  `--system-site-packages` (быстро, экономит место): `ai-eggs/.server_venv`,
  `levitan/.server_venv` (+ symlink `bin/python`), `/opt/levitan/.venv`,
  `angel-backend/.venv`. Доустановлено `markdown2==2.4.12`,
  `psycopg2-binary==2.9.9`, `flask==3.0.0`, `rank_bm25`, `uvicorn`
  (последний — был нужен для `bin/uvicorn` в юните `knowledge-api`).
  Все 8 ключевых модулей импортируются: `tg_bot`, `scheduler`, `autopilot`,
  `feed_interactor`, `dtmf_handler`, `mango_webhook`, `a2a_dispatcher`,
  `angelochka_core`.
- [x] **VPSFIX-3 (Fixed + Verified):** восстановлен `run_agent.sh`
  (`/opt/freelance/projects/ai-eggs/agent/run_agent.sh`, chmod +x) — обёртка
  запуска python через venv, на которую ссылались `angela-bot`, `bitrix-bot`
  и `server-seller`. Поведение восстановлено по cmdline живых процессов:
  `exec "$VENV_PYTHON" "$@"` + `PYTHONPATH=angel-backend:agent`. Проверено:
  `run_agent.sh -c` → `python из venv`; `tg_bot`, `bitrix_bot`, `agent/server.py`
  импортируются.
- [x] **VPSFIX-4 (Fixed + Verified):** `bitrix-bot` был errored (30 рестартов) →
  **online**, лог: «Непрочитанных нет — чисто!».
- [x] **VPSFIX-5 (Fixed + Verified):** восстановлены 3 файла `angel-backend`
  из GitHub (`Erik03132/angel-backend`): `server.py` (9773 б),
  `bitrix_crm.py` (13556 б), `delivery_reminder.py` (7377 б) — их не было
  ни на диске, ни в репозитории `ai-eggs` (у них отдельный репозиторий).
  `angel-backend/server.py` импортируется: OK.
- [x] **VPSFIX-6 (Fixed + Verified):** `pm2 save` выполнен — **до этого дамп
  был от 30.09 и не содержал `ai-traffic-pro-api`** (создан 28.10), то есть
  резервный API сайта не поднялся бы после ребута. Бэкап старого дампа:
  `/root/.pm2/dump.pm2.bak-20261028-pre-save`. Новый дамп: 16 процессов,
  **все 16 валидны** (exec/interpreter/cwd существуют — проверено скриптом).
- [x] **VPSFIX-7 (Fixed + Verified):** разрулен конфликт за порт 8002.
  Найдено, что **seller-ботом управляет systemd-юнит `angelochka.service`**
  (`ExecStart=…/.server_venv/bin/python3 -u server.py`, порт 8002), а pm2-
  процесс `server-seller` запускал тот же `agent/server.py` → оба на 8002 →
  pm2 уходил в цикл рестартов (накопилось 133 рестарта). Решение: pm2-
  `server-seller` удалён (дубликат), остался systemd-юнит. Проверено:
  `:8002/api/health` → `{"status":"ok","agent":"angelochka","version":"2.0"}`,
  `/api/chat` отвечает, через nginx с `Host: vezemcip.ru` — то же.
- [x] **VPSFIX-8 (Fixed + Verified):** `knowledge-api.service` (порт 8080,
  RAG-поиск по базе знаний) был enabled, но **битый**: `ExecStart` указывал на
  несуществующий `…/.server_venv/bin/uvicorn` → `status=203/EXEC` → сервис
  падал в рестарт-цикле. Починен: `uvicorn` доустановлен (`--force-reinstall
  --no-deps` — иначе pip пропускал скрипт, т.к. пакет был виден через
  `--system-site-packages`), юнит перезапущен. Проверено:
  `/health` → `{"status":"ok","service":"knowledge-api","model":"paraphrase-multilingual-MiniLM-L12-v2","model_loaded":true,…}`,
  `/docs` → 200, порт 8080 слушается.
- [x] **VPSFIX-9 (Fixed):** `angelochka-seller.service` (systemd, ссылался на
  утерянный `server_seller.py`) — `stop`+`disable`; `angelochka-bitrix.service`
  и `angelochka-expert.service` — `disable` (исходники утеряны, но процессы
  875/876 живы и продолжают работать на 8003/8004). Кто ими пользуется —
  никто: grep по коду и nginx пуст, наружу порты закрыты (`ufw` INPUT DROP,
  8002–8004 не открыты), внешних соединений нет.
- [x] **VPSFIX-10 (Fixed + Verified):** `levitan-agent.service` (голосовой агент
  LiveKit, порт 8081) — enabled, но битый: `WorkingDirectory=/opt/pipecat-agent`
  и `ExecStart=/opt/pipecat-venv/bin/python3` — **оба каталога удалены**.
  Исходник цел: `/opt/freelance/projects/levitan/agent/levitan_agent.py`.
  Собран venv `/opt/pipecat-venv` (393 МБ): `livekit-agents==1.8.9`,
  `livekit-plugins-deepgram==1.8.9`, `livekit-plugins-openai==1.8.9`,
  `aiohttp`, `httpx`, `python-dotenv`, `openai`. Импорты OK
  (`livekit.agents`, `livekit.plugins.deepgram`, `livekit.plugins.openai`),
  `levitan_agent` импортируется («[FUNNEL] FAQ cache loaded: 242 triggers»).
  Юнит переведён на `WorkingDirectory=/opt/freelance/projects/levitan/agent`
  (бэкап: `levitan-agent.service.bak-20261028`), перезапущен: **active**,
  `NRestarts=0`, worker зарегистрирован в LiveKit, порт 8081 слушается.
- [x] **VPSFIX-11 (потеря безвозвратно, зафиксировано):** три исходника
  **не восстановимы** — `server_seller.py`, `server_bitrix.py`,
  `server_expert.py`: отсутствуют на диске (в т.ч. в git-истории
  `angel-sales` по всем веткам, в `git fsck`), в репозиториях
  `angel-sales`/`angel-backend`/`antigravity-brain`/`freelance-2026`,
  в бэкапах и тарах; следы работы есть только в `syslog`/journal. Их
  функциональность **закрыта**: `agent/server.py` (systemd `angelochka`,
  порт 8002) отдаёт тот же формат `{"response":…,"session_id":…}` и больше
  маршрутов, чем seller-сирота; 8003/8004 никем не используются. Реальная
  потеря — только `profile: "seller"` в ответе `/api/health` и персональные
  промпты bitrix/expert-профилей. Восстановление возможно лишь переписать
  с нуля — целесообразности нет, пока их не зовёт код.
- [x] **VPSFIX-12 (Verified):** финальная проверка после восстановления.
  Все 10 сервисов на VPS отвечают **200**: `api-traffic`(3001), `vezem-web`
  (4321), `angel-backend`(5001), `angelochka`(8002), bitrix-профиль(8003),
  expert-профиль(8004), `knowledge-api`(8080), `mango-webhook`(8085),
  `dtmf-handler`(8086), `livekit-sip`(8081). pm2: **16 процессов online**,
  0 errored; дамп валиден (16/16, все exec/interpreter/cwd существуют).
  systemd: **0 битых enabled-юнитов** (было 2). Внешне: сайт 200,
  Worker-API 200 (`{"ok":true,"telegram":true,"ai":true}`), резерв-API 200
  (`{"ok":true,"telegram":true}`). nginx-конфиг валиден.
  Проверено, что `pm2 resurrect` **не** поднимет `baresip-sip` (в дампе
  `status=stopped`; в коде pm2 `God.prepare` при `STOPPED_STATUS` только
  регистрирует процесс, а `resurrect` пропускает уже присутствующие) —
  иначе он конфликтовал бы с `livekit-sip` за порт 5060 (оба на `sip_port:
  5060`).
- [ ] **VPSFIX-13 (гигиена, отложено):** `pip cache` на VPS занимает **3.5 ГБ**
  при 74% заполненности диска (`/dev/sda1 117G, свободно 31G`). Можно
  безопасно чистить (`pip cache purge`) — но лучше после того, как убедимся,
  что голосовой стек не требует офлайн-переустановки. Не срочно.

### 🗺️ ATP-ROADMAP — карта прод-качества: Фаза 0 (28.10.2026)

> Карта: `~/freelance-2026/projects/ai-marketing/docs/ROADMAP.md` (6 фаз, 12 недель).
> Горизонт 29.10.2026 → 17.01.2027. Базов��я линия зафиксирована в карте.

- [x] **ATP-R0 (Fixed + Verified):** rate limit считался **общим на всех** —
  IP брался из `req.socket.remoteAddress` (за nginx всегда `127.0.0.1`).
  Воспроизведено на проде: 10 запросов → 11-й с другого IP = 429, т.е. любой
  посетитель отрезал заявки всем. Плюс чат и форма делили один счётчик
  (10 сообщений в чате блокировали форму). Исправлено: `server/ratelimit.js`
  (IP из `X-Forwarded-For`, раздельные баки `lead`/`chat`), 8 тестов,
  `npm test`. Задеплоено на VPS, commit `974453f`. Проверено на проде.
- [x] **ATP-R1 (Verified):** карта пересобрана против кода и прода. Исправлены
  расхождения: 9 URL в sitemap (не 8), 7 услуг (не 6 — маркетплейс заменён на
  e-commerce), добавлены дырки «favicon 404», «8 из 11 `title` > 60»,
  «два источника правды», уточнены ограничения GitHub Pages (нет `_headers`)
  и внешних шрифтов (Material Symbols с `display=block`).
- [ ] **ATP-R2 (от Игоря, блокирует Фазу 0):** доступы — счётчик Яндекс.Метрики,
  подтверждение домена в Вебмастере и GSC, API мониторинга uptime, вход в DNS.
  Без них Фаза 0 (0.1–0.4) не сдвинется.
- [ ] **ATP-R3:** Фаза 0, задачи 0.1–0.4 — Метрика с целями, Вебмастер+GSC,
  uptime-алерт в Telegram, сквозной тест заявки. Гейт 0: заявка в Telegram +
  визит в Метрике + сработавший алерт.
- [ ] **ATP-R4:** Фаза 1 — 404-страница, favicon в `public/`, og:image +
  twitter:image (1200×630), title ≤60, `lastmod` по факту, 1 хоп редиректа,
  решение по security-заголовкам (Cloudflare или VPS — Pages не умеет `_headers`).
- [ ] **ATP-R5:** Фаза 2 — семантика по 7 услугам (сейчас 727–809 слов против
  1200), вилки цен, кейсы, блог 6–8 статей, FAQ 8→15+, закрыть разрыв
  «`CONTENT_SPEC.md` ↔ `src/data/site.ts`».
- [ ] **ATP-R6:** Фаза 3 — наполнить `llms.txt` фактами (сейчас 101 строка, без
  FAQ/цен/сроков), NAP-консистентность, ≥10 цитируемых фактов, мониторинг
  AI-ответов (10 контрольных запросов).

## 🗄️ ODB — opencode-db: CLI к SQLite-истории OpenCode (разбор дропа 25.10.2026)

> Источник: https://habr.com/ru/articles/1097396/ (VasilevNStas, 21.10.2026).
> Верифицировано web 26.10: GitHub VasilevNStas/opencode-db (3★, 0 forks, MIT,
> 37 коммитов, CI test/release, PyPI opencode-db), README + docs/README.ru.md.
> **Локально подтверждён главный факт статьи:** `~/.local/share/opencode/
> opencode.db` существует — **у нас 4.3 ГБ** (статья: «может разрастаться до
> многих гигабайт» — прям наш кейс).

**Что делает (Commands):** list/info/export (md+json, bundle, --sanitize —
затирание sk-/ghp_/JWT!)/search/tree/digest (compaction-summary)/costs (из
session.cost — реальные цены провайдера)/projects/stats/todos/health (freelist,
сколько VACUUM вернёт)/backup (SQLite API, manifest+sha256)/backups/delete
(--dry-run по умолчанию, дата-фильтры)/prune/vacuum (11 стадий защиты: бэкап,
lock-check, WAL-checkpoint).

**Границы:**
- Молодой проект: 3★ соло, но stdlib-only (0 deps), Python 3.12+ (у нас 3.14 ✓),
  CI, документация отличная; деструктивные команды (delete/vacuum) имеют
  многослойные гейты и бэкап по умолчанию — риск низкий, но работать пока только
  в read-only-режиме (list/stats/costs/export/health).
- Есть встроенное `opencode db` (консоль) и опенсорсный chncaesar/opencode-db-clean —
  альтернативы; меняет раскладку: opencode-db шире всех на export+costs+backup.
- export никогда не модифицирует БД; для шаринга — с --sanitize (секреты).
- NAS/офлайн-том может выглядеть «missing directory» — delete --missing-directories
  НЕ запускать без ручной сверки (гейт с фразой DELETE <N> SESSIONS).

**Задачи:**
- [ ] **ODB-1 (по «да»):** `uv tool install opencode-db` → read-only-прогон:
      `stats`, `costs --total`, `directories`, `health` (сколько места вернёт
      VACUUM) + `export --latest --sanitize` в vault как пилот. Отчёт Игорю.
      → **Done 25.10.2026, с находками:**
      • Установлен 0.14.0 (uv, 2 сек). Read-команды работают: stats (339 сессий,
        875.8M токенов, **$109.05 суммарно** с 04.02.2026), projects (freelance-2026
        $89.79 / global $19.13), **health — ГЛАВНАЯ НАХОДКА: файл 4.3 ГБ, живых
        данных 926 МБ, freelist 3.4 ГБ (79%) → ~3.4 ГБ можно вернуть VACUUM'ом**.
      • ⛔ **vacuum заблокирован утилитой**: наша БД — schema v2 preview
        (OpenCode 2.0.32), тул отказывает write-операции до реализации v2-writes
        → ODB-2 ставится **Blocked (v2)** — ждать апдейт тул-а или проверить
        chncaesar/opencode-db-clean на предмет v2.
      • ⛔ **export НЕ работает на v2**: пишет «Сообщений: 0» и 194B-файлы, хотя
        `info` видит 82 сообщения — вероятно, export читает v1-таблицы. Не баг
        нашей настройки — граница v2-support. Оценка: issue автору (если舍不得
        фидбек); пока экспорт диалогов не юзать, SESSION_LATEST остаётся ручным.
- [ ] **ODB-2 (по «да» на ODB-1, отдельным решением):** если health покажет
      большую freelist → BACKUP-первее всего → `vacuum` (только при закрытом
      OpenCode, agree по «да», бэкап обязателен).
      → **Разблокирован вариантом (б), проверено 25.10.2026:** `ocdbc` 0.1.1
      (chncaesar/opencode-db-clean, 30★ MIT, stdlib-only, SQLite-уровень —
      схеме v1/v2 всё равно). `ocdbc analyze` на нашей v2-базе: подтверждено
      3.4 ГБ freelist (79%), после VACUUM файл ~926 МБ. Побочный плюс: включит
      auto_vacuum=INCREMENTAL (не даст базе распухать снова).
      ⏰ **Ручной запуск (только Игорь):** закрыть ВСЕ OpenCode-сессии → в
      терминале: `export PATH="$HOME/.local/bin:$PATH" && ocdbc vacuum`
      (бэкап и integrity-checkы внутри автоматически; требуется ~9 ГБ свободно —
      на 25.10 свободно 13 ГБ, ТОСНО, после vacuum станет +3.4 ГБ). НЕ запускать,
      если что-то ещё пишет на диск крупное. После — проверить, что OpenCode
      стартует и сессии на месте. Отчёт Игоря → close-задача.
- [ ] **ODB-3 (низкий приоритет):** finish-day интеграция — `export --latest` в
      SESSION_LATEST/vault вместо/дополн к ручному логу.



## 🟢 РАЗБЛОКИРОВАНО (10.10.2026) — решения Игоря + проверка

- **T-08 (VPS-доступ) — РЕШЕНО.** Проверено 10.10: TCP/22 к 217.149.23.113 OPEN
  (ping закрыт провайдером — это нормально; ходим по SSH). Детали блокера —
  в архиве (`checkpoints/active_tasks_archive_202608.md`).
- **T-09 (TG-токены) — РЕШЕНО** (выданы Игорем, прописаны).
- **Что снова можно делать:** деплой AI-Scout (скрипт `scripts/deploy.sh` готов),
  ночной синк Mac↔VPS, TG-доставка ночного конвейера Кворков (Ф1–Ф4 ниже).
- **AI-BUS — ⏸ ПАУЗА** (см. блок выше).

## 🧹 DRIFT — аудит скиллов OpenCode vs Hermes (2026-10-10)

> Отчёт: `docs/skill-drift-audit-2026-10-10.md`. 110 скиллов Hermes vs ~148 OC;
> 12 смысловых дублей, 7 уникальных кандидатов. Правило: мастер — OC.

- [x] **DRIFT-001** — Импорт 7 скиллов в `~/.config/opencode/skills/` (+ симлинки в `~/.agents/skills/`): grounded-citations, ocr-and-documents, popular-web-designs, architecture-diagram, competitor-news-monitor, blogwatcher, text-unicode-hygiene
- [x] **DRIFT-002** — 12 смысловых дублей свёрнуты: 11 мастеров OC обогащены (`tools/ops/drift_merge_skills.py`), 19 Hermes-скиллов стали обёртками (бэкапы `.bak-20261010`)
- [x] **DRIFT-003** — `tools/ops/skills_drift_report.sh` + встроен в воскресный `expert-skills-updater.mjs` (через `.finally`, даже при падении). Проверить первый реальный запуск updater в вс 03:00 и дубль-статус в `logs/skills_drift_latest.md` (цель: «Нет ✅»)

## 🚌 AI-BUS — «Автобус + алгоритм выживания» (создан 2026-10-10) ⏸ ПАУЗА

> **СТАТУС (10.10.2026): ПАУЗА по решению Игоря.** Возобновляется по команде —
> нужны данные пилота (мессенджер водителей, список, интервью). До возобновления
> задачи приостановлены, ничего не делаем.
> Концепция для заказчика: `projects/ai-bus/docs/concept/` (PDF на Desktop).

- [ ] **AIB-001** — Интервью с предприятием: текущий поток инструктажа, допуск на линию
- [ ] **AIB-002** — Зафиксировать канал (VK Mini App vs Telegram) и получить список водителей
- [ ] **AIB-003** — Согласовать программу пилота и 4 темы выживания (БПЛА/АУН/ДТП/пассажиры)
- [ ] **AIB-010..012** — Каркас: backend журнала (timestamp+sha256+медиа), Mini App, экспорт журнала
- [ ] **AIB-020..022** — Контент: банк сценариев, формат брифа, сводка дня
- [ ] **AIB-030..032** — Дашборд диспетчера, кнопка «ЧП» (спец-рассылка ≤3 мин), анти-фрод
- [ ] **AIB-040..042** — Пилот: 20 водителей → 100 водителей → отчёт по метрикам
- [ ] **AIB-050..053** — Пост-пилот: ЭП (63-ФЗ), интеграции ЭПЛ/медосмотр, face-match, монетизация

## 🔴 P0-блок (finish-day 2026-10-25) — Лид-генерация копилот-схема

- [ ] **LEAD-001** — Запуск `lead-copilot` skill: скоринг по 5 сигналам + черновик ответа в тоне Игоря (propose→approve, паттерн batrak)
- [ ] **LEAD-002** — Апрув порогов lead-score thresholds от Игоря (P0/P1/P2 по баллам)
- [ ] **LEAD-003** — Настройка мониторинга сигналов (TG-поиск руками + классификация агентом) — без юзерботов
- [ ] **LEAD-004** — Юридическая проверка ПД (152-ФЗ, 38-ФЗ ст.18) через Фемиду перед любыми email-действиями
- [ ] **LEAD-005** — Прогон UXT-1 на лендинге (когда готов превью) — 4 персоны-субагента, отчёт до/после

## 🔴 P0-блок (finish-day 2026-09-01) — VPS: каскад моделей и TG-токены

- [x] **HFM-004** — Настроить каскад из 13 бесплатных моделей на OpenRouter для всех 13 профилей (deepseek-v4, nemotron-3.5, laguna-s-2.1, minimax-m2.7/m3, ling-3.0 и др.)
- [x] **HFM-005** — Обновить TG-токены 7 ботов (personal, sherlock, marketer, batrak, femida, financier, english-tutor) в `.env`
- [x] **HFM-006** — Удалить дубликаты `/srv/hermes/.hermes/profiles/` → 13 уникальных профилей в `/root/.hermes/profiles/`
- [x] **HFM-007** — Настроить systemd drop-in: `HERMES_HOME=/root/.hermes`, `TELEGRAM_PROXY`, `OPENROUTER_API_KEY`, `TELEGRAM_ALLOWED_USERS=176203333`
- [x] **HFM-008** — Проверить что все 6 ТГ-ботов отвечают (personal, sherlock, marketer, batrak, femida, financier)
- [ ] **HFM-009** — Настроить `/sethome` для каждого бота в Telegram

## 🔴 P0-блок (finish-day 2026-08-30 вечер) — Инфраструктура знаний, Timeweb S3 и MCP

- [x] **TW-001** — Timeweb Cloud: создать S3-бакет (напр. `igor-shared`) для обмена файлами и знаниями между Mac и VPS.
- [x] **TW-002** — Настроить `rclone` / sync-пайплайн на Mac и VPS для безопасного knowledge-экспорта из Obsidian в S3.
- [x] **TW-003** — Подключить Timeweb мониторинг и алерты на падение сервисов/ботов на VPS.
- [x] **MCP-001** — Проверить OAuth-авторизацию Vercel MCP в живой сессии при первом деплое. ✅ 31.08: `hermes mcp login vercel` (OAuth-браузер) → `✓ Authenticated — 37 tool(s)`, `hermes mcp test vercel` отдаёт инструменты.
- [ ] **MCP-002** — Протестировать инструменты GitHub MCP (26 tools via `mcp-github-stdio.sh`) и Obsidian Vault MCP на реальных задачах.

## 🔴 P0-блок (finish-day 2026-08-30) — Автономия и оркестрация агентов

- [x] **ORCH-001** — Внедрен Zero-Token Watchdog Kwork (`~/.hermes/scripts/watchdog_kwork.py`, крон ID: `4b6f9e4f5184`, `no_agent=True`, каждые 30м, $0 затрат токенов).
- [x] **ORCH-002** — Развернут автономный пайплайн Scout → Batrak через `continuity` and `context_from` (крон ID: `b4b4e33a4272` and `18939972f1ed`, дедупликация + инлайн-драфт отклика).
- [x] **ORCH-003** — Создан раннер долгих автономных миссий в `tmux` (`tools/ops/run_mission_tmux.sh`).

## 🔴 P0-блок (finish-day 2026-08-29 вечер) — инфраструктура OmniRoute/Hermes

> Итог аудита: инфра подтверждена рабочей. Блокеров нет.

- [x] **HTG-001** — Фикс автостарта VPS: `omniroute.service` (failed→active), `hermes-dashboard.service` (crash-loop→active). Все 6 systemd-юнитов active+enabled. Verified.
- [x] **HTG-002** — Найдена путаница портов: `:8890`=самописный (не OmniRoute), `:20128/dashboard`=родной OmniRoute. SSoT зафиксирован.
- [x] **HTG-003** — Hermes Desktop добавлен в Mac Login Items (автооткрытие GUI).
- [x] **HTG-004** — Веб `:9120` = админка (не чат); `/chat`=активация сессии. Общение → Desktop/ТГ.
- [x] **HTG-005** — SSoT-док создан: `~/freelance-2026/INFRA_SSOT_OMNIROUTE_HERMES.md`.
- [ ] **HFM-001** (P1) — Уточнить учётку входа в родной OmniRoute `/login` (что просит форма).
- [ ] **HFM-002** (P2) — Подключить провайдеров в OmniRoute (OpenRouter/Nous API-ключи) — опц.
- [ ] **HFM-003** (P2) — Улучшить кастомный дашборд `:8890` (модели/провайдеры) — опц.

> SSoT активных задач. Старое (июльские планы, HABR-дайджесты, ротация
> секретов, Angela ГОТОВО) вычищено — лежит в `ACTIVE_TASKS.md.bak-20260822`.

## 🔴 БЕЗОПАСНОСТЬ (постоянно)

- **Не коммитить секреты** (.env, ключи) — правило в AGENTS.md.
- **Write-protect скиллов** (ES-22): `tools/security/lock_skills.sh` —
  активные скиллы read-only (chmod 0444 + git-track). Правки только через `skill_manage`.
- **ai-defender**: летальное трио (ES-25) — агент с секретами ≠ парсящий веб/почту.
  Runtime guardrail (ES-26) + непрерывный red-teaming (ES-27) — в очереди.
- **stealth/ox-alpha** (ES-28): LOW-TRUST модель в OmniRoute. ТОЛЬКО публичный
  код/несекретные задачи. ЗАПРЕТ: клиентский код, Фемида, приватные данные.
- **Модельная политика (постоянно):** платные модели (GPT/Claude и др.) — только
  ручное включение по явному запросу Игоря. Автоматический primary/fallback —
  только verified free. Летальное трио (ES-25): агент с секретами ≠ парсящий
  веб/почту.

## 🌙 НОЧНОЙ КОНВЕЙЕР КВОРКОВ (Sherlock→Batrak→Chief, 25.08)

**Цель:** ночью агенты ищут подходящие кворки, пишут отклики в стандарте v3;
утром Игорь копирует готовое и отправляет вручную (анти-бан HH/Kwork).
SSoT: `docs/adr/007-nightly-kwork-pipeline.md`, план `.hermes/plans/nightly-kwork-pipeline.md`.

- [x] **Ф0 аудит:** старый `freelance-agent` НЕ содержит парсера Kwork (`src/index.ts`
  отсутствует, только MCP Avito/Bitrix + design-агент). Строим почти с нуля.
- [x] **Ф1 код:** `cron_jobs/kwork_finder.py` написан (Playwright headless, фильтр
  калибровки, дедуп через sqlite, запись в outbox + leads). `--dry-run` готов.
  Фильтр проверен на 5 тестах: транскрибация→A, бот+Bitrix→A, игра→X,
  Senior Backend→X, парсер 800₽→B. ✅
- [ ] **Ф1 тест:** прогнать `kwork_finder.py --dry-run` на реальном Kwork (ждём
  завершения `playwright install chromium` в фоне, pid 72152).
- [ ] **Ф2:** Batrak v3-промпт (HOOK→MATCH→PROOF) подключить в конвейер.
- [ ] **Ф3:** «рыбка» proof-budget (≤30 мин, локально, без секретов).
- [ ] **Ф4:** cron 0 3 * * * → outbox + leads; TG-дайджест — после починки gateway.
- [ ] **Заметка Firecrawl:** `sk-nous` (Nous Inference) НЕ авторизует api.firecrawl.dev
  (401). Firecrawl по подписке Nous требует отдельного эндпоинта/ключа — не найдено
  в доках; временно используем Playwright headless (локально, без ключей).

## 🔗 СИНХРОНИЗАЦИЯ Mac ↔ VPS (ТГ-бот) — SSoT общения (решено 29.08)

> ПРАВИЛО: два «главных» агента (десктоп на Маке + ТГ-бот, оба профиль femida)
не видят общих файлов напрямую. Чтобы не было раздвоения — ВСЁ пишется сюда,
в ACTIVE_TASKS.md, по единому шаблону. Кто бы ни исполнял (Мак или бот на VPS),
результат дописывается В ТУ ЖЕ строку.

### Формат задачи (обязателен для ТГ-бота и для Мака)
```
### T-NN · <название> · [⏳|🔧|✅|❌]
- Поручил: <ТГ|Мак> · <дата/время>
- Задача: <что сделать, кратко>
- Результат: <вывод команды / ссылка / краткий итог>   ← заполняет ИСПОЛНИТЕЛЬ
```
- Большая задача → отдельный `tasks/T-NN.md` с полным логом; здесь — ссылка + статус.
- Игорь спрашивает «что по T-NN?» → бот/Мак цитирует строку из этого файла.

### Каналы синхронизации (приоритет)
1. **ДОМА** → VPS через СТАТИЧЕСКИЙ IP VOSNET (подключить ЛК/офис +7(496)441-11-62).
   IP вписать в TimeWeb FWaaS + ufw (порт 22) → туннель `~/.vps-tunnel.sh` живёт.
   Тогда `ACTIVE_TASKS.md` синкается scp/rsync по SSH (GitHub с Мака недоступен).
2. **МОБАЙЛ** → через ТГ-бота (уже работает, входящий IP не нужен). Бот пишет в
   свой `ACTIVE_TASKS.md` на VPS; Игорь спрашивает бота «что по T-NN?» → цитирует.
3. **RU-SOCKS5-прокси ОТМЕНЁН** (поддержка: только белые списки РФ, возврат средств).

### Инструкция ТГ-боту (профиль femida на VPS)
При любом поручении от Игоря: создать строку `T-NN` по формату выше (статус ⏳),
после выполнения дописать `Результат:`, сохранить в `/root/freelance-2026/ACTIVE_TASKS.md`
(копия на VPS). Не держать контекст только в чате — всё в файл.

### ДЕЖУРНЫЙ ЦИКЛ (выходные, динамический IP VOSNET ещё не куплен)
Туннель падает при смене домашнего IP. Оживить БЕЗ туннеля (через ТГ-бота, он жив):
1. `bash ~/freelance-2026/my_ip.sh` → узнать текущий IP.
2. В ТГ главному боту: «открой <IP> в ufw на VPS (порт 22)».
3. LaunchAgent сам ретраит туннель (~10с), порты 9119/8742 оживают.
АВТО-вариант (после статического IP в понедельник): cron на VPS смотрит лог sshd
и сам добавляет новые IP в ufw → туннель оживает без участия Игоря.


## 🔴 ЖЁСТКИЙ УРОК 25.08 (Игорь закрыл сессию — НЕ повторять)

Агент облажался на подборе кворков. Зафиксировано как обязательное правило:

- [ ] **ФИЛЬТР ПО РЕАЛЬНЫМ КОМПЕТЕНЦИЯМ, не по regex-ключам.** Наш профиль СТРОГО:
  боты (aiogram)+Bitrix24/Mango CRM, RAG/эмбеддинги, парсеры, транскрибация
  (faster-whisper — реально есть), лендинги/сайты под ключ.
  **ЖЁСТКО ОТСЕКАТЬ:** видео-синтез/face-swap, игры (Roblox/Unity/движки),
  чистый SEO/GEO-маркетинг, Hardcore Senior/Enterprise. Агент зацепился на
  «ИИ/видео/игра» и предложил не наши задачи — БРАК.
- [ ] **ПЕРЕД ОТКЛИКОМ ОБЯЗАТЕЛЬНО ПРОЧИТАТЬ ТЗ заказчика** (описание + вложения,
  часто Word-док на странице кворка). Писать отклик ПО ЗАГОЛОВКУ = брак
  (было на кворке Bitrix24 — отклик вслепую, ТЗ не читал).
- [ ] **Игорь сам бракует лишнее** — спрашивать, что вычеркнуть, не угадывать.
- [ ] **ФОРМАТ ВЫВОДА:** Игорь НЕ может открывать/кликать файлы в Hermes.
  Печатать каждый кворк как «ссылка → готовый отклик» ПРЯМО В ЧАТ, не в outbox/.
- [ ] **VOICE:** писать как исполнитель «Готов разработать…», НИКОГДА не
  парафразить ТЗ «Нужно разработать…» (старый баг вставлял текст заказчика в наше письмо).
- [ ] **АНТИ-БАН Kwork:** Qrator банит IP после частых заходов (ERR_CONNECTION_REFUSED/
  Timeout). Один медленный прогон: задержки 30–60с, ротация UA, пауза 60мин между
  прогонами. Не долбить в цикле.
- [ ] Код `cron_jobs/kwork_finder.py` требует переписать фильтр (сейчас regex-ключи →
  не те предложения). См. ADR-007 + план `.hermes/plans/nightly-kwork-pipeline.md`.

## 🎨 ADM — Awesome Design MD для Рембрандт (разбор 11.10.2026)

> **Источник:** видео AI Stack Engineer «OpenCode + AwesomeDesign-md: Build 100X
> Stunning Designs for Free» (10.04.2026, 36K) + репо `VoltAgent/awesome-design-md`.
> **Верификация (проверено src, не на веру автора):** GitHub API — MIT, 120 211 ★,
> 13 404 форка, создан 31.03.2026, последний пуш 05.10.2026 (активно), 73 DESIGN.md,
> 9 категорий брендов. Концепция DESIGN.md — от Google Stitch (офиц. дока), не
> выдумка видео. Кросс-подтверждение: независимые обзоры (AICodeKing, Flux Academy).
> Формат файлов проверен вживую (linear.app): frontmatter + цвета с ролями/hover,
> тени, радиусы — машиночитаемые токены, не вайбы.
> **Вердикт: принято — ДОинтеграция (новый скилл НЕ нужен, см. DRIFT-001).**

> **Что уже есть в стеке (не дублировать!):** скилл `popular-web-designs` (54 бренда
> из этого же репо, MIT, триггеры «сделай как stripe/linear» — импортирован
> DRIFT-001 10.10.2026); скилл `design-bridge` (DESIGN.md → инструкции для
> реализации); Рембрандт уже умеет `designmd.supply` (анализ произвольного сайта).

- [x] **ADM-001** — Прописать в skill Рембрандта источники референсов единой строкой:
  «стиль как [бренд]» → `popular-web-designs` (54 локальных шаблонов) → при отсутствии
  бренда — `designmd.supply` или raw-DESIGN.md из awesome-design.md через `design-bridge`
  ✅ 11.10.2026: раздел «4. awesome-design-md» + workflow + «🆕 Новые возможности» в
  `skills/agents/rembrandt/SKILL.md`
- [x] **ADM-002** — Правило «DESIGN.md в корне проекта»: перед любой UI-генерацией
  (лендинг, дашборд, контент-фабрика) кладём DESIGN.md в корень проекта как дизайн-SSoT
  рядом с AGENTS.md (как уже сделано в `ai-bureau/DESIGN.md`). ✅ 11.10.2026: зафиксировано
  в workflow Рембрандта и в `skills/design-bridge/SKILL.md` (секция «DESIGN.md в корне
  проекта — правило ADM»)
- [x] **ADM-003** — Канал обновления снимка: 73 raw-DESIGN.md в апстриме vs 54 в
  локальном скилле. ✅ 11.10.2026: секция «Refresh channel» in
  `skills/popular-web-designs/SKILL.md` (clone --depth 1 → diff → добор missing)
- [x] **ADM-004** — Proof (SA-1, **Verified**): scratch-проект, обе версии лендинга
  TaskFlow (один копирайт, одна структура) → `/var/folders/…/T/opencode/adm-proof/`:
  `index_no.html` + `index_yes.html` + скриншоты `*.png` (Playwright/Chrome, 1440px).
  БЕЗ DESIGN.md: indigo→pink градиент, эмодзи-иконки, shadow-карточки (generic AI-slop).
  С DESIGN.md (Linear): #08090a canvas, 48px/510/-1.056px заголовок #f7f8f8, hairline-бордюры
  rgba(255,255,255,.08), ghost+indigo кнопки 6px, SVG-иконки, mono-eyebrow. Копирайт
  идентичен — различие ТОЛЬКО в дизайн-слое.
  Ограничение proof: n=1, оба варианта написал я (не blinded) — но фИДЕЛЬНОСТЬ токенов
  объективна (hex/tracking/radius сверены с DESIGN.md)

## 🧠 GX — GitNexus: «память кодebase» для OpenCode (разбор 11.10.2026)

> **Источник:** видео AI Stack Engineer «OpenCode + GitNexus: Give OpenCode Real
> Codebase Memory» + репо `abhigyanpatwari/GitNexus`.
> **Верификация (проверено src):** 47 829 ★, 5 196 форков, создан 02.08.2025, пуш
> 11.10.2026 (активно), OpenSSF Scorecard + CI, npm v1.6.12. Механика подтверждена
> по README: Tree-sitter → граф (структура/парсинг/resolution) → LadybugDB локально
> в `.gitnexus/` → MCP-тулы (impact/clusters on коде песочницы, call chains,
> execution flows) — precomputed, ответ за 1 вызов вместо grep-археологии.
> **🔴 ЛИЦЕНЗИЯ — PolyForm Noncommercial 1.0.0 (НЕ MIT!).** Бесплатно только
> некоммерческое использование. Коммерция (все клиентские проекты: Levitan,
> ai-eggs, Bitrix-задачи) — отдельная лицензия через akonlabs.com. Заголовок
> видео говорит «free» — это верно лишь для non-commercial.
> **Вердикт: пилот принят — ТОЛЬКО некоммерческая песочница. Коммерция — гипотеза
> до цены от akonlabs (GX-001).**
>
> **Зачем (наше «больное место»):** агент правит функцию, не зная что 47 других
> зависят от её возвращаемого типа → ломает. Это ровно домен ADR-003 (Graph Layer,
> impact slice вместо full-repo dump) — у нас запланирован, но не внедрён как
> рабочий слой. Граф персистентен (выживает между сессиями) = память структуры.
> Уже есть частичные покрытия (не дублировать): `graphify` (аналитика, не MCP),
> `smart-explore` (tree-sitter on-demand, без персистентности), `code-mapper`
> (карта под задачу, без графа зависимостей), claude-mem (память наблюдений,
> не код-структура). MCP в OpenCode: `claude-mem`, `notebooklm`, `geekneural`,
> `transcribe-mcp` — граф-кода среди них нет.
>
> - [ ] **GX-001** — Лицензия: написать в akonlabs.com (founders@akonlabs.com / Discord)
>   за стоимость commercial-лицензии. До ответа: GitNexus ТОЛЬКО на личных/некоммерческих
>   задачах. Решение о покупке — Игорь (RT-1: действие за Игорем — отправить письмо или санкционировать использование как есть)
> - [ ] **GX-002** — Песочница (НЕ freelance-2026!): scratch-репо → бэкап AGENTS.md →
>   `npm i -g gitnexus` (npm 11 имеет npx-баг, ставить глобально) → `gitnexus analyze`
>   → замерить: время индекса, размер `.gitnexus/`, **перезаписывает ли AGENTS.md/CLAUDE.md**
>   (угроза нашему SSoT — искать флаг отключения записи context-файлов)
> - [ ] **GX-003** — MCP-подключение в OpenCode (`~/.config/opencode/opencode.jsonc`:
>   `"gitnexus": {"type": "local", "command": ["gitnexus", "mcp"]}`) → проверить тулы
>   impact/clusters на коде песочницы. Учтить: OpenCode = MCP + Skills, hooks (как в
>   Claude Code) НЕ поддерживаются — контекст не подмешивается автоматически
> - [ ] **GX-004** — Proof на «больном месте» (SA-1: Verified ≠ Fixed): одна и та же
>   правка в песочнице без графа и с графом → зафиксировать пропущенную зависимость
>   → скриншот/лог в отчёт
> - [ ] **GX-005** — Защита SSoT: `.gitignore` += `.gitnexus/` + правило в AGENTS.md:
>   `gitnexus analyze` в реальных репах — только после бэкапа AGENTS.md и проверки
>   флагов (niche: команда сама «создаёт AGENTS.md/CLAUDE.md context files`)

## 🎥 ASV2 — Top 5 OpenCode Skills V2 (AI Stack Engineer, 20.10.2026)

> **Источник:** youtube.com/watch?v=rlw6ckOhYCk (22.09.2026, 9К просмотров). Разбор по
> expert-source-pipeline. **Вердикт: проверено src → всё уже покрыто или отклонено,
> НОВОГО НЕ ПРИНИМАЕМ.** Сиквел видео V1 (разобрано 22.09.2026, см. AGENTS.md).
>
> 1. **GitNexus** — уже разобран 11.10.2026 (секция GX: пилот только non-commercial).
> 2. **claude-mem** — уже работает (server-beta, MCP `claude-mem`).
> 3. **Graphify** — установлен в skills/.
> 4. **GSD Core** — отклонено: дубль writing-plans + expert-source-pipeline; независимый
>    ревью (dev.to/aws): «burned tokens fast, takes over your whole workflow».
> 5. **AionUi** (desktop GUI мульти-агентов) — отклонено: дублирует subagent +
>    claude-handoff + worktree-per-task (OR-2).
> 6. **UI UX Pro Max v2** — отклонено: высокий референс-тест (192 rules/79 стилей/192
>    палитры/74 шрифтовые пары), но у нас уже есть frontend-design, ui-designer,
>    popular-web-designs, anti-ui-slop-reviewer, web-design-guidelines + агент Рембрандт
>    с designmd.supply (ADM-секция). С(+151 скилл) — lazy-load не нужен.
> 7. **Impeccable** — гипотеза: ссылка в описании пустая, репо не верифицирован.
>    Берём только если Рембрандт покажет пробел в polish-контроле.

## 🐦 ORN — Ornith-1.0: self-scaffolding модели для agentic coding (разбор 20.10.2026)

> **Источник:** ornith.ai/ornith_1_0.html (25.06.2026, DeepReinforce/Ornith Team).
> **Верификация (проверено src):** GitHub `ornith-ai/Ornith-1` (2.1k★, MIT-лицензия —
> подтверждено независимыми разборами explainx.ai, emergent.sh, Medium), HF-коллекция
> (9B/31B/35B/397B + GGUF/FP8, 396 upvotes, 1.5M+ загрузок GGUF-9B). Метрики
> воспроизводимы: vLLM/SG-serving, OpenHands/Terminus harness, 5 прогонов.
> Ключевой факт: TB-2.1 77.5 (Metropolis-2) / 78.2 (Claude Code harness) — стабильность
> между двумя харнесами подтверждает, что это не overfit под один рантайм.
>
> **Вердикт: проверено src → модель НЕ берём, паттерн уже реализован, 2 гипотезы.**
>
> 1. **Не берём 397B:** наш Tier 0 DeepSeek-V4-Flash-0731 по той же таблице (репо
>    Ornith) даёт TB-2.1 82.7 / SWEB-V 81.6 — НЕ хуже, при живом OmniRoute-роутинге.
>    Плюс вышел Ornith-1.5 (TB 86.1) — значит 1.0 уже не флагман лайнапа.
> 2. **Паттерн self-scaffolding валидирует ADR-001 (scaffold self-improvement):**
>    Ornith-friendly трёхслойная защита от reward hacking = 1:1 наша структура:
>    неизменяемая внешняя граница (env/eval_gate без правок агентом) → детерминированный
>    монитор (validation-layer) → LLM-judge veto (кросс-чек). Подтверждение, что наш
>    scaffold-подход (ADR-001/002/003 + eval suites) идёт в ту же сторону, что и
>    фронтовиков; нового стека-действия из этого не следует.
> - [ ] **ORN-001 (гипотеза)** — Ornith-1.0-9B-GGUF как локальный тир (Tier L):
>       SWEB-V 69.4 на ноутбуке, без интернета/прокси — для offline-задач и
>       приватных данных (ADR-002_PL). Проверка: llama.cpp/Ollama на Игоревом Mac,
>       замер латентности/качества на 3-5 реальных задачах. Решение — Игорь.
> - [ ] **ORN-002 (гипотеза)** — преследуем выход Ornith-1.5-MLX: MLX-кванты для
>       Apple Silicon уже в HF-коллекции = локальный тир на Mac без llama.cpp.
>       Если подтвердится качество — можно заменить OLLAMA-секцию ORN-001 на MLX.

## 📄 MOCR — Mistral OCR 4 (дайджест, разбор 20.10.2026)

> **Источник:** дайджест Игоря + первоисточник mistral.ai/news/ocr-4 (23.06.2026),
> сверено с docs.mistral.ai/pricing и 3 независимыми разборами (AIwire/HPCwire,
> digitalapplied, therundown).
> **Верификация (проверено src):** цифры дайджеста верны — $4/1000 стр. (Batch $2,
> Document AI schema $5), 170 языков, bounding boxes + block classification +
> inline confidence. Поправки к дайджесту: (a) подсветка уверенности по блокам и
> указание источника в странице — это OCR 4.1 (16.07.2026, alias mistral-ocr-latest);
> (b) self-host = single container, но только для enterprise-контрактов;
> (c) бенчмарки вендорские: на публичном OlmOCRBench это ~3-е место, не 1-е;
> (d) OCR 4.1 извлекает структуру страниц, а «спросить по договору и получить ответ
> с подсветкой» — это LLM поверх его выхода, отдельно.
>
> **Вердикт: проверено src → принято как preload-тир для ADR-005, НЕ как замена стека.**
> **Решение Игоря (20.10.2026): используем как вариант — активируем при появлении
> первой задачи, где poppler ломает сканы/сложные таблицы. До тех пор — в ожидании.**
> Наше больное место: `kb-prep pdf` (poppler) ломает сканы/таблицы/формулы → корявые
> чанки → шум в Qdrant. OCR 4 закрывает ровно это: структурный extraction с
> confidence (низкая уверенность → чанк в ручную очередь проверок).
> Подсветка места источника совпадает со нашим стандартом Femida/grounded-citations
> (цитата + указатель на первоисточник) — мигрируется без переделки. Self-host
> правил бы ADR-002 (документы не уходят наружу), но он enterprise-only — для нас
> пока вариант только через API.
>
> ⚠️ Границы (проверить ДО покупки ключа): доступность Mistral API из РФ без
> прокси (ADR-002: если блок — прокси строго socks5h) и способ оплаты. Не проверено.
>
> - [ ] **MOCR-001** — Проверить доступность API из РФ (прямой curl на mistral.ai)
>       и способ оплаты (карта; если нет — вариант через посредника).
>       Действие за Игорем: либо дать ключ, либо санкционировать тест через прокси.
> - [ ] **MOCR-002** — Пилот: взять 5 худших PDF корпуса (сканы/сложные таблицы, где
>       poppler ломался) → OCR 4.1 → `kb-prep send` → сравнить чанки с poppler-базой.
>       Критерий приёма: меньше мусорных чанков и лучше точность на прогонке
>       `kb-prep eval` (обязателен по ADR-005 после изменения пайплайна — иначе
>       статус Verified не ставим, SA-1).
> - [ ] **MOCR-003** — Если пилот пройден: в `kb-prep pdf` добавить tier «сложный
>       PDF» (наличие скана/грязного layout) → OCR 4.1 Batch ($2/1000 стр.) →
>       eval-гейт в eval_gate. Внедрять только после «да» Игоря.

## 📦 GH — Подборка растущих OSS, неделя 13–20.10 (20.10.2026) ✅ Fixed

> **Верификация:** README всех 4 репо прочитаны 20.10.2026. Полный разбор и вердикты:
> `vault/06-Library/gh-weekly-2026-10-20/digest.md` (+must-read для уроков установки).
>
> - **mattpocock/skills** (298k★, MIT) — установлено 7 скиллов: grilling,
>   domain-modeling, grill-with-docs, retro, wizard, to-tickets, writing-for-agents.
>   Дубли не ставились (tdd/code-review/handoff/ grill-me = наш каскад).
> - **hyperframes** (68.2k★, Apache-2.0) — установлено core из 10 скиллов
>   (роутер + домены + media-use). Node 24 ✓, ffmpeg ✓. Рендер-движок для PMO.
> - **openrig** (8k★) — БИБЛИОТЕКА, не ставим: kernel full-access + хуки в конфиг
>   (ai-defender флаг), перекрыто subagent/handoff/worktree.
> - **claude-mem** — уже работает (server-beta с 25.07.2026); выбор подтверждён
>   ростом проекта.
>
> - [ ] **GH-001** — Первый HyperFrames-смоук на реальном мини-задаче (15с kinetic
>       title, 1920x1080): `npx hyperframes init → preview → render` с обходом E407
>       (вручную через clone; детали в vault digest). Критерий: MP4 рендерится
>       детерминированно → Verified. Запускать только при появлении видео-задачи.
> - [ ] **GH-002** — Adopt идей без кода: GLOSSARY-подход в CONTEXT.md при
>       следующем новом проекте (grill-with-docs процедуру совместить с нашей
>       CONTEXT.md практикой). Dashboard/canvas решение — по ходу.

## 🤖 MW — Meta Muse Wonder / Muse Wonder Full (дайджест, 20.10.2026)

> **Источник:** дайджест Игоря; сверено с официальным анонсом Meta Newsroom
> (about.fb.com/news/2026/10/introducing-muse-wonder-models/, 12.10.2026).
> **Верификация (проверено src):** факт-чек дайджеста ПРОЙДЕН — Frontier модели для
> агентных задач (преемник Muse Spark); **Active Memory** (перенос важного между
> разговорами) и **Active Focus** (доведение до цели, альтернативные подходы при
> ошибках, уточнения перед важными действиями) — подтверждены как именованные
> фичи; домены law/finance/health + frontier coding; доступ: Muse Wonder через
> Meta Model API и Muse Code, Full — подписчикам Muse Code; скоро в muse.ai.
>
> **Поправки к дайджесту:** (a) «высокие результаты» = вендорские заявления, в
> посте нет независимых цифр (research-блог отсылается, таблиц не проверено);
> (b) цены не раскрыты.
>
> **Вердикт: проверено src → НЕ БЕРЁМ, watchlist-граница.**
> 1. **Граница ADR-002/юр:** Meta признана экстремистской организацией на
>    территории РФ (2022): сервисы заблокированы, оплата/ToS недоступны из РФ.
>    Подключение Meta Model API = обходной путь, который мы не строим.
> 2. **Нет дыры в стеке:** ровно те же фичи (память между сессиями =
>    claude-mem + agent-memory-kit; мультитаскинг/восстановление = scaffold
>    ADR-001+evals) у нас УЖЕ есть и работают через OpenCode/OmniRoute/Fable.
> 3. **Позитив:** третий независимый сигнал направления (после Ornith-1.0 и
>    harness2): «память + самокорректирующийся scaffold» = верное стратегическое
>    направление investimento. Наш стек на социально-верной траектории.
> - [ ] **MW-001 (watchlist)** — Проверить при появлении: Muse Wonder в сторонних
>       агрегаторах (OpenRouter и др.), доступных из РФ без обходных схем. Только
>       тогда возвращаться к оценке Tier-3 замены. Не раньше.

## 🧠 H2 — google-research/harness2: рекурсивный harnessing-фреймворк (20.10.2026)

> **Источник:** github.com/google-research/harness2 (+ paper arXiv:2610.14224,
> сайт harness2.github.io).
> **Верификация (проверено src):** 14.2k★ / 1.3k форка, Apache-2.0, релиз свежий
> (3 коммита), официальная организация google-research (страница: не официальный
> продукт Google). Поддерживает **OpenCode** и Codex как executors; бенчмарки
> JobBench (профработа) / LAB (юрработа) / WorkBuddy-Bench (office/web/code).
>
> **Суть:** harness = всё вокруг модели при замороженных весах: system prompt,
> guardrails, memory, tool guidance, subagents, skills, scripts, plugins (8
> редактируемых компонент). Рекурсия в 2 уровня: per-task Propose–Probe–Compose
> (контрастные прогоны-кандидаты, композит без ground-truth) + persistent
> «improvement harness» (принятые lessons для следующих задач). Протестировано
> на GLM-5 и Gemini 3.5 Flash: до +11.5 pts (WorkBuddy), +4.5 (JobBench),
> +11.8 pp (LAB partial pass).
>
> **Вердикт: проверено src → принят как методологический референс для Target B.**
> Это индустриальная версия нашего scaffold-self-improvement (ADR-001,
> self_improve_log.md): 8 компонент Harness² ≈ наш scaffold (skills/AGENTS/
> memory/hooks), а «improvement harness» = наш Self-Improvement цикл с
> Propose→Approve. Декларативный шаблон не меняем и не внедряем сразу — берём
> ПАТТЕРН (прогон демо без ключей термосится демо-задача). Стоимость реального
> прогона: model-backed = платный API (Vertex/Gemini).
>
> - [ ] **H2-001 ( Shops: бесплатно)** — Прогнать локальное демо без модели
>       (`uv pip install -e '.[render]' && harness2-demo --output runs/demo --k 2`)
>       — посмотреть форму артефактов: adopted harness, reflection notes. Статус:
>       гипотеза до прогона. Решение — по правилу активности (появится задача на
>       прокачку scaffold).
> - [ ] **H2-001b (H2-002)** — Читаем BENCHMARKS/SETUP только ПЕРЕД пилотом на
>       нашем стеке (executor opencode); не читать всё сразу (lazy-load). Учёт
>       к costs: реальный прогон = API; перед пилотом зафиксировать бюджет.

## 🧪 EE — tester-army/e2e: agent-driven e2e фреймворк (20.10.2026)

> **Источник:** github.com/tester-army/e2e.
> **Верификация (проверено src):** 11.5k★ / 592 форка, Apache-2.0, GitHub Trending,
> 883 коммита, npm `e2e` + пакеты движков (`@e2e-dev/web` на Playwright,
> `@e2e-dev/mobile`), docs-сайт, examples для Vite/Next/Astro/Flutter/MAUI и др.,
> статусы в репо (roadmap к 1.0, API может меняться). Анонимная телеметрия,
> opt-out (`E2E_TELEMETRY_DISABLED=1` или `npx e2e telemetry disable`).
>
> **Суть:** e2e-тест = цель на естественном языке → агент ведёт приложение
> (Playwright под капотом) → детерминированные locator/assertions в том же тесте.
> **Ключевой паттерн:** шаги агента записываются → следующий прогон выполняется
> REPLAY'ем БЕЗ вызовов модели, пока приложение не изменилось. Экономика внимания:
> LLM платится один раз, CI гоняется бесплатно. BYO-ключ/локальная модель.
>
> **Вердикт: проверено src → принято к отложенному пилоту.** Закрывает наш пробел
> «UI-правка сломала флоу, а мы узнали от клиента»: агент находит и фиксирует
> путь, потом CI его реплеит. Дублирует частично: e2e-runner (Playwright-агент),
> browser.* MCP, ui-ux-tester — но они не дают persistent replay-режима.
> Pre-1.0 → на боевую верификацию только после stabilization.
>
> - [ ] **EE-001** — Отложенный пилот (при появлении фронтенд-задачи в WEB
>       lime-polish-magic или dashboard): `npx e2e init`, телеметрию выключить,
>       1 агент-тест флоу (форма/заказ) + детерминированные assertions; критерий —
>       тест реплеится локально без LLM и ловит изменённый UI. Статус: гипотеза
>       до прогона. Решение запустить — по ходу задачи (правило Igor 20.10: tools
>       activate when matching task appears).

## 📦 ACO — ArtCraft Office-клоны: WordCraft / GridCraft / DeckCraft (дайджест, 20.10.2026)

> **Источник:** дайджест Игоря; сверено с первыми разборами (Thurrott, Office Watch,
> XenoSpectrum, gadgethacks) 10-14.10.2026.
> **Верификация (проверено src):** проект РЕАЛЕН — ArtCraft (Brandon Thomas, автор
> Adobe-клонов PhotoCraft/FilmCraft): чисто-«clean-room» Rust-реализации W/E/P,
> MIT/Apache-2.0, исходники открыты, v0.5.0 (10-11.10.2026), установщики
> Win/macOS/Linux, браузерные WASM-версии; у каждого свой MCP-сервер (WordCraft —
> 389 команд, AI может водить документ: открыть/выделить/форматнуть/сохранить).
> **Поправки к дайджесту:** (a) «полностью повторяют функциональность» — НЕВЕРНО:
> pre-alpha/alpha, сам автор говорит «не готов заменить Microsoft 365»;
> WordCraft ~62% parity, DeckCraft ~79% фич PPT; (b) DOCX round-trip теряет
> встроенный контент (задокументировано); (c) Thurrott: ссылки с сайта временно
> сняты, дистрибутивы только через GitHub-репозитории.
>
> **Вердикт: проверено src → WATCHLIST, не внедряем.** Уникальная ценность — не
> редакторы (LibreOffice уже есть), а MCP-серверы: агент управляет НАСТОЯЩЕЙ
> оболочкой с ribbon/tracked-changes. Но pre-alpha + задокументированная порча
> DOCX = риск потери документов клиентов (Femida, оферты). Ретест после
> первого alpha-релиза.
>
> - [ ] **ACO-001 (watchlist)** — Отметить месяц пересмотра: **ноябрь 2026** —
>       проверить GitHub ArtCraft на alpha-версии и отчёт README о testable
>       corpus-fidelity (потеря контента DOCX). При положительном результате:
>       пилот MCP-сервера WordCraft в OpenCode (opencode.jsonc) на
>       некритичной документации (черновики ai-eggs). Решение — Игорь.

## 🎬 PMO — Prompt Motion: библиотека моушен-референсов (20.10.2026)

> **Источник:** prompt-motion.com (проверено src: живая, 140k+ визитов/нед., куратор
> @p4nthera_). Галерея роликов, сделанных Claude Opus 5.5 (CSS/HTML/SVG/Three.js/
> Remotion/manim), у каждой карточки открыты промпт и/или skill. Категории: Product
> UI (102), Charts (33), Diagrams (31), Kinetic type (98), Shapes (44), Particles (43),
> Characters (27), 3D, Photos, Music, Code.
> **Вердикт: принято как референсная библиотека для моушен-задач.** Валидирует стек
> Rembrandt (motion design, emilkowalski skills) — это те же техники, только с
> готовыми эталонами вместо выдумывания с нуля.
>
> **СОГЛАСОВАННЫЙ WORKFLOW (Igor, 20.10.2026):**
> 1. Появляется задача на видео/моушен → агент открывает prompt-motion.com и
>    кидает Игорю 2-3 ссылки ПОД задачу (по категории, не весь сайт).
> 2. Игорь выбирает референс (действие Игоря, ~10 сек).
> 3. Агент снимает промпт с карточки → адаптирует под задачу (продукт, бренд,
>    размер кабинета/сторис) → Rembrandt генерит ролик.
> 4. Проверка: подсвеченный результат доступен Игорьву в панель, правки через
>    план-canvas/чат. Спиннер-критерия нет: авторский приём Игорем.
>
> - [ ] **PMO-001** — Первое реальное применение: ближайшая пост-визуализация из
>       октябрьского контент-плана (ai-eggs), где уместен моушен вместо статики —
>       кандидат есть, решаем по ходу задачи. Статус: гипотеза → проверится первым
>       же применением.

## 🌐 WEB — AI Bureau: унификация стиля сайта (11.10.2026) ✅ Verified

> **Задача:** сайт Erik03132/lime-polish-magic (Vite/Lovable, индекс + 6 страниц услуг)
> привести к единому стилю lime-polish (как развёрнутый index.html). Рембрандт.
> **Статус: Verified** — билд успешен, 7 скриншотов (1440px) + мобильный (390px).

- [x] **WEB-001** — DESIGN.md в корне репо (lime-polish SSoT: палитра ink #0f172a / paper #f7f8f6 / signal #c8ef67, пастели blue/peach/lavender, тёмные секции #142943/#040912, пилюли 100px, карточки 14px, Inter 700/-0.088em)
- [x] **WEB-002** — `src/styles.css` переписан под lime-polish ПО КЛАССАМ service-page (разметка не тронута): хедер/hero/strip/metrics/scenarios/steps/faq/contact/related/footer; сохранены tailwind-импорты + @theme oklch-токены + медиа-запросы
- [x] **WEB-003** — Проверка: `bun install && bun run build` ✅; скриншоты всех 7 маршрутов + мобильный (390px) в `<repo>/shots/`; отклонения: hero одноколоночный (разметка сохранена), пастели сценариев 0/2/1 (signal-soft/blue), metrics on #142943
- [x] **WEB-004** — Клон перенесён в `~/freelance-2026/ai-bureau-site` (постоянно),
  коммит `decf611` запушен в main (синк с Lovable). Сайт живой на
  `http://localhost:8080/` (launchd, HMR). Скриншоты: `shots/home-new.png`,
  `shots/rag-new.png` + старые `shots/*.png`

## 🧠 Эксперт-сессия (19.10.2026) — новые кейсы из case library

> Источник: `docs/cases/INDEX.md` сводка за 13–19 октября 2026.
> Вердикт: 3 кейса (2 Reddit r/hermesagent + 1 YouTube) = 2 новых паттерна + расширение ES-NEW-03.

### 📌 ES-NEW-03 · Qwen 3.5-35B local inference на Mac M3/M4 (расширение)

> Есть: always-on-personal-assistant (u/recmend, 12.10) + jonathan-rivera (12.10) — оба запускают Qwen 3.5-35B через LM Studio на Windows/Mac. Mac M3 доступен.

- Что: Валидация, что Qwen 3.5-35B (4-bit GGUF / MLX) можно запустить локально на Mac M3/M4 (16–32GB) для наших профилей (особенно `marketer` — анализ рекламных каналов, конкуренции, RAG по кейсам).
- Решение: `llama-cpp` skill + `nous-inference-api` fallback pattern. Протестировать MLX-квант Qwen 3.5-35B на Mac M3 (8-core) с ограничением context ≤8K. Если LM Studio работает на Windows — значит llama.cpp/MLX точно влезет на Mac.
- Что делать: `llama-cpp` → pull `Qwen/Qwen3-35B-Instruct-GGUF` (IQ4_NL, ~22GB) → benchmark на M3. Сравнить токен/cost vs `ling-3.0` через VPS. Если local ≥30% дешевле — добавить в OmniRoute cascade как LOW-TRUST tier.
- Проект: omniroute, marketer, llama-cpp

### 📌 ES-NEW-04 · Telegram Topics = Discord multi-channel UX

> Есть: rasmus-hermes-windows-discord (05.10, Rasmus Wulff Jensen, YouTube) — 3 месяца 24/7 на Windows, Discord multi-channel (meal prep, morning status, notifications, YouTube, email, calendar) с контекстными инструкциями на канал.

- Что: Discord каналы дают многоканальность с перс-инструкциями на домен. У нас: TG-бот @hermes03132_bot (мультиплекс профиль→чат), forum groups в TG = аналог Discord channels через topics.
- Решение: адаптировать `sherlock`/`marketer`/`femida` профили на forum-group с топиками: каждая тема = канал с фиксированным системным промптом (как Discord). Использовать `apple-reminders` для cross-channel reminders.
- Что делать: создать forum group в TG (бот должен быть админом), настроить topic-based routing в gateway, протестировать на nightly кворках (Ф1–Ф4).
- Проект: telegram-gateway, sherlock, marketer

### 📌 ES-NEW-05 · Hermes-optimizer skill (агент улучшает агента)

> Есть: jonathan-rivera (12.10) — «dedicated Claude Code skill for optimizing Hermes», каждая ошибка/фикс логируется в shared doc.

- Что: Паттерн «agent-optimizes-agent» — Claude Code (или Batrak) пишет/фиксит скиллы Hermes, логируя в shared doc; результат auto-деплоится через `sync_hermes_knowledge.sh`.
- Решение: создать `hermes-optimizer` skill — input = error transcript + fix proposal, output = патч SKILL.md + commit. Интегрировать в weekly `expert-skills-updater.mjs` (DRIFT-003).
- Что делать: шаблон skill + пример workflow (error→fix→patch→deploy). Оценить: можно ли auto-apply после review, или нужен manual approve.
- Проект: skills, batrak

---

## 🧠 Эксперт-сессия (26.10.2026) — новые кейсы из case library

> Источник: `docs/cases/INDEX.md` сводка за 26 октября 2026.
> Вердикт: 3 новых кейса (2 YouTube + 1 Telegram) = 3 паттерна для наших профилей.

### 📌 ES-NEW-06 · Профильная изоляция: persona + memory + skills per profile

> Есть: skorohod-6-agent-team (25.10, YouTube) — 6 профилей на одном VPS, каждый с отдельной моделью, памятью, persona (sole-file), набором skills. Автор: разработчик-практик, но не Nous core.

- Что: разделить текущие 6 профиля (personal/sherlock/marketer/femida/financier/health/batrak) на изолированные профили с собственными persona-файлами, памятью и skill-наборами — паттерн из видео, где каждый агент = отдельный сотрудник с чёткой ролью.
- Решение: создать `sole`-файлы (persona/identity/instructions) для каждого профиля в `~/.hermes/profiles/<name>/`; выделить отдельный workspace + memory-db per profile; skills — только релевантные к роли (не «все скиллы в каждом профиле», как сейчас).
- Что делать: (1) inventory текущих skills per profile (какие скиллы использует каждый профиль сейчас); (2) создать persona-файл для marketer (контент/SEO/реклама) и femida (право/контракты/риски); (3) протестировать worker-изоляцию: собрать marketer в отдельный профиль с persona + 5 ключевыми skills через неделю.
- Проект: profiles, marketer, femida

### 📌 ES-NEW-07 · Навыки контент-профиля: 3 роли + 16 навыков для статей/SEO

> Есть: comandos-ai-komanda-13-cases (19.10, Telegram COMANDOS) — 13 видеокейсов, включая "Контент: 3 роли + 16 навыков для статей и постов" и "SEO: данные Яндекса → задания по сайту". Автор: бизнес-интегратор (47 внедрений), но утверждения о росте/внедрениях не верифицированы.

- Что: шаблон навыков для контент-профиля (marketer): 3 роли (writer/researcher/editor) × 16 навыков (источники, ключи, структура, SEO-оптимизация, публикация, мониторинг). Применимо к нашей задаче: marketer → автоматический контент из кворк-отчётов + SEO-адаптация под Telegram/личный сайт.
- Решение: собрать skill-кит `content-pro` (3 роли + 16 skills) в `~/.hermes/skills/`; интегрировать с botwatcher (сбор Telegram-обратки) + blogwatcher (конкуренты) + grounded-citations (факт-чекинг перед публикацией).
- Что делать: (1) выписать 16 skills из кейса видео (на основе описания); (2) сверить с установленными в marketer (уже есть 8 из 16); (3) написать недостающие 8 навыков; (4) протестировать на контент-цикле: кворк-отчёт → черновик статьи → SEO-правка → публикация.
- Проект: marketer, content-pro

### 📌 ES-NEW-08 · Формализация persona-файлов per profile (голосовой режим)

> Есть: ai-doctor-hermes-complete-guide (21.10, YouTube) — каждый профиль/bot в Hermes имеет свою persona (файл `sole`), модель, память, навыки; можно создавать профили через prompt. Hands-free voice mode есть в WebUI, требует активацию в settings. Автор: образовательный канал, технические детали совпадают с официальными docs.

- Что: у нас пока профили живут в `.env` + config.yaml без явного `sole`/persona-файла. Видео показывает: persona = чёткое определение роли (Cloud = дизайнер landing, Astra = back-office dev). Нужно формализовать persona для каждого нашего профиля, чтобы sub-agents и кросс-инвокации работали предсказуемо. Voice mode — кандидат для health-профиля.
- Решение: создать `sole`-файл (`persona.md`) для каждого профиля в `~/.hermes/profiles/<name>/persona.md` с: ролью, целями, persona-голосом, ограничениями, preferred tools; добавить в каждый profile `.env` ключ `PERSONA_FILE=persona.md`; оценить voice-mode для health (whisper-local / edge-tts уже в workspace? если нет — добавить).
- Что делать: (1) написать persona-файлы для marketer + femida (первые 2 в приоритете); (2) протестировать: создать задачу, где marketer и femida работают параллельно (кросс-инвокация через chat) — проверить, что context не смешивается; (3) voice-mode: собрать Faster Whisper + edge-tts в отдельный profile (health) на Mac; проверить hands-free (8-сек пауза).
- Проект: profiles, health, voice

---

## 🔍 SHS — Sherlock skill-scouting (дайджест агента, 21.10.2026) — выбрано

> Отчёт скаута: `vault/06-Library/sherlock-skill-scouting-2026-10-21.md`
> (remote: /opt/freelance). Правило п.13: верификация перед принятием.

**Проверено (src) 21.10 — все репы GitHub API подтверждены:**
- NousResearch/hermes-agent: 255 836★, MIT, push 21.10 — 30 инфра-коммитов, 212 SKILL.md без изменений (0 новых) ❌ пропустить
- ZeroPointRepo/awesome-hermes-skills: 632★, 0 коммитов с 20.10 ❌
- moonlight-lupin/agent-skills: 109★, push 18.10 — «WARM» ✅ источник P1
- ChuckSRQ (80★, stale 02.05), frankxax (6★, repo отдалён) — COLD ❌
- seaworld008/Commonly-used-high-value-skills: 594 SKILL.md (оценка скаута 297 — недосчитал половину), fact-checker/deep-research/web-scraper на месте
- breakstageaxe61/genspark-claw: 565★, super-research на месте (5 SKILL.md)

**Принято:**
- ✅ **Fixed:** deep-research v1.9.2 (moonlight-lupin, 15 файлов) + fact-checker v1.0.0 (moonlight-lupin, 6 файлов) установлены в `~/.config/opencode/skills/`, системой распознаны. Шерлоку: deep-research — приоритет 1; fact-checker — приоритет 1.
- [ ] **SHS-1** — super-research (genspark-claw, 565★, mixture-of-agents, параллельные поисковые волны + cross-verify): сравнить с установленным deep-research на живом кейсе, затем взять/отклонить (не копировать вслепую — подход другой)
- [ ] **SHS-2** — fact-checker v1.1.1 (seaworld008, документ-orientation + правки с цитатами): смотреть как дополнение, если fact-checker v1.0.0 покажет слабость на документах
- [ ] **SHS-3** — web-scraper v1.0.1 (seaworld008, OSINT/pagination/dedup): кворк-сценарии шерлока; не срочно
- НЕ принято: arxiv (уже локальный порт), x-twitter-scraper (платный Xquik API), researcher (UX-домен), spark-report/spark-slides/call-prep/claw-browser-anchor (Genspark-специфика)

**Процесс-баги (нужен ревизит у chief):**
- [ ] **SHS-4** — t_2f7a4d91 / t_8b1e3f5c / t_4c6d2a7e помечены «done», но порты скиллов НЕ выполнялись (выявлено в отчётах 20.10 и 21.10): ревизия статусов тасок в канбане — done ставится только после верифицированного порта, не после маршрутизации
- [ ] **SHS-5** — t_4f618fa1 (оценка новых скиллов, sherlock) — BLOCKED: uv.lock отсутствует, воркер падал 2×: собрать env-фикс для воркеров sherlock (восстановить uv.lock или предпросчёт зависимостей в контейнер/лейаут), приоритет — до дальнейших прогонов

## 🐨 CUA — trycua/cua, samples/cua-bots-macos (разбор 21.10.2026) — принято как кандидат

> Источник: https://github.com/trycua/cua/tree/main/samples/cua-bots-macos
> (перенесён в examples/). Проверено src 21.10: 30 562★, 2 216 forks, MIT (корень),
> push 21.10. НО: пример и jarвис-ядро Spaces — **FSL-1.1-MIT** (source-available,
> не OSI-MIT; ограничение на конкурентные продукты 2 года — для внутреннего
> использования некритично, см. LICENSING.md).

**Что это:** SwiftUI-приложение «персистентные боты»: каждый бот = свой Space
(лёгкая VM на Docker/Colima или облако), память (Cua Volume: MEMORY.md,
outputs/, inbox/), рутинные задачи (RoutineStore), карточки-апрувы `[[ask: ...]]`,
лайв-стрим экрана бота с PiP и take-over, харнессы claude-code / codex /
hermes / openclaw. Модель настраивается через `CUA_BOTS_MODEL_URL` /
`CUA_BOTS_MODEL` — есть вшитый контракт на внешний endpoint.

**Вердикт: берём как референс-паттерн, не как замену OpenCode-агентов** — усиливает
то, чего у нас нет: изоляция каждого агента в своей VM + явный UI-контракт
апрувов (протокол маркеров `[[ask]]/[[notify]]/[[schedule]]/[[done]]` — модель
простая, переносимая в наших handoff-агентов). Одна причина против борьбы за
«прямо внедрить»: сборка Swift + Docker VM на каждую задачу — тяжело для Mac,
а ядро прорывное (persistent agents, Keyvault) пока не задействуется sample'ом
(см. Gaps в README).

- Вердикт-статус: проверено src → принято (эксперимент, не продакшн)
- ⏸ **ТРЕБОВАНИЕ ОТ ИГОРЯ (21.10.2026): НЕ запускать до апгрейда железа.** Сейчас 8 ГБ RAM / 256 ГБ диск — мало. После апгрейда (16+ ГБ RAM / 512 ГБ+) — напоминалка сработает, тестить CUA-1.
- 🛒 **ЖЕЛЕЗО — решение по покупке (обсуждено 26.10.2026):** дилемма
  «M5 24 ГБ/512 ГБ или 16 ГБ/1 ТБ» → рекомендация: **RAM приоритетнее диска**
  (память не апгрейдится, диск добирается внешним SSD ~$100 + NAS DS720 уже
  есть). Формат: если агенты 24/7 — **M5 mini 24 ГБ как сервер** + текущий
  M1-ноут как клиент (Screen Sharing/Tailscale); если один девайс — ноут с
  вентилятором (Pro), но 24/7 на ноуте = батарея/термика (AlDente 80%,
  `pmset autorestart 1`, caffeinate). Решение за Игорем; порог «16 ГБ» в
  задачах ниже считать МИНИМУМОМ, оптимум — 24 ГБ.
  → **Уточнение 26.10: у Игоря есть большой монитор под mini** → единственный
  минус mini (нет экрана) снят, схема «mini-сервер + ноут-клиент» становится
  основной рекомендацией. При покупке не забыть: автологин (FileVault мешает
  после power-loss reboot), Screen Sharing + Tailscale, внешний SSD под модели.
- [ ] **⏰ ПОСЛЕ 15.11.2026 (напоминалка) — СТАРТ CUA-1:** по обновлении машины до 16 ГБ RAM / 512 ГБ диск — вернуть к задаче: смоук-тест CUA Bots (клон + сборка cua-spaces-ffi + swift build + создание бота, ~1 час). Согласовать с Игорем, делать ли. Простой тест-кейс: бот делает в своей VM мини-дайджест новости → outputs/ → карточка [[done]]; проверка памяти: закрыть/открыть — бот помнит контекст (см. план в CUA-1 ниже)
- [ ] **CUA-1** — смоук: клон, quick start (`cargo build -p cua-spaces-ffi`,
  stage-library, swift build), запустить `CuaBots`, проверить создание бота:
  держится ~1 час, отчёт о том, что заработало
- [ ] **CUA-2** — по «да» на CUA-1: подключить бота к OmniRoute через
  `CUA_BOTS_MODEL_URL` (ADR-002-совместимо: хостингимым шлюзом), бот на
  claude-code харнессе
- [ ] **CUA-3** — независимо от CUA-1: протокол маркеров `[[ask]]/[[notify]]/
  [[done]]` → предложить как контракт ответов для наших агентов (handoff,
  chief) — маленькая, переносимая часть
- Граница (ai-defender, ADR-004/AI-безопасность): в sample «правила —
  инструкции, не enforcement» — харнесс сам апрувит свои permissions внутри
  Space (README, Gaps). До включения host-sharing (взять доступ к Mac) НЕ
  разрешать боту; host-доступ пер-аккаунт, не пер-бот — ризки. Не запускать
  ботов с доступом к секретам ключей рабочей машины.

**Апдейт дропа 25.10.2026 — Spaces SDK анонс (верифицировано web 26.10):**
- Публичный релиз SDK: SDK-и Python/TS/Swift/Rust + `cua` CLI + MCP-сервер
  (тот же Spaces-контекст, что и app). Source: cua.ai/docs/spaces, docs/cua-sdk/
  guides/run-a-coding-agent, spaces.cua.ai, techcityauthority 20.10.2026.
- `sandbox.agents()` — харнессы Claude Code / Codex / Gemini CLI / **OpenCode** /
  Goose через Agent Client Protocol, события нормализуются, run живёт в
  `~/.cua/agents/<run>` — реттач после смерти процесса (CP: длинные задачи).
- Компьютеры: свой ноут/Mac mini/сервер, свой облако-аккаунт AWS/GCP/Azure/Modal;
  дроп добавил песочницы E2B/Daytona (в доке упоминается «sandbox service»,
  явного списка E2B/Daytona в результатах поиска не увидели — проверить при
  внедрении). ~10 строк старт (пример `examples/agents-in-sandboxes/tour.py`).- Hosted relay бесплатный в раннем доступе; teleport/multiplayer free (early access).
- Лицензии не изменились: driver MIT; Spaces app FSL-1.1-MIT (см. блок выше).
- Статус: «проверено (src)» → вердикт из 21.10 сохраняется (кандидат/эксперимент,
  НЕ продакшн; ⏰ ждём апгрейд железа 15.11.2026). Новых задач из дропа не
  выделяем — расширяют CUA-1: при смоук-тесте проверить `cua agent run` (CLI-путь,
  без Swift-сборки) как более лёгкую точку входа, чем CuaBots-app.
- Связка с нами: OpenCode — официальный харнесс → наш handoff-агент теоретически
  может мигрировать в Space (изоляция + реттач) — вариант при перепроектировании
  handoff-инфраструктуры.

## ⚖️ PLL — Perplexity for Legal → прокачка Фемиды (разбор дропа 25.10.2026)

> Источник: perplexity.ai/enterprise/use-cases/legal (страница 403 — верифицировано
> через независимые разборы: gc.ai/blog/perplexity-for-lawyers [SEC-сторона,
> продаёт конкурента], marktechpost 26.06.2026, spellbook). Проверено src.

**Что у Perplexity Legal:** Computer for Counsel (24.06.2026) — агентский слой:
исследование («orient me» по незнакомой области права с цитатами), мониторинг
регуляторики по расписанию, contract triage, маршрутизация 20+ моделей на
подзадачи, премиум-источники (Midpage — case law + citator), 400+ тулов через
MCP, $40/seat Enterprise. 

**Где Perplexity слабее нашей Фемиды УЖЕ СЕЙЧАС (важнее!):**
- формат «вывод + дословная цитата + ссылка на первоисточник» — Exact Quote у
  них это платная фича, у Фемиды это обязательный формат отчёта
- обязательный кросс-чек на второй модели + финальный гейт человека — у
  Perplexity нет (они сами пишут «проверяй каждую ссылку»)
- регион: Perplexity = публичный веб, слабо покрывает РФ-НПА и российские
  суды; Фемида — специализация РФ (pravo.gov.ru), это наша ниша
- приватность: по US v. Heppner (февраль 2026) чаты с юр. AI не приватны и
  без Kovel-структуры — поэтому наше «закрытая связка на своём стеке» правильно

**Чего у Фемиды нет и стоит докрутить (не копировать Perplexity, а заимствовать паттерн):**
- [ ] **PLL-1 — Playbook'и по классам договоров.** Чеклисты «фицида смотрит NDA/DPA/MSA/оферта/44-ФЗ/223-ФЗ»: типовые риски по классу, обязательные проверки, аргументы фейл. Включить в skill agents/femida как references/ (по «да») — **Fixed+Verified 25.10.2026**: 8 файлов в `~/.config/opencode/skills/agents/femida/references/playbooks/` (nda, dpa-152fz, it-license, oferta-b2c, 44fz, 223fz, prentenziya-isk-shtraf + README); SKILL.md: шаг пайплайна 2.5 «PLAYBOOK». Eval: 9+6 passed
- [ ] **PLL-2 — Цитатор актуальности: «действует ли норма в этой редакции?»** Проверка статьи по pravo.gov.ru: текущая редакция, последние изменения, не отменена ли. Прототип для Фемиды (по «да») — **Fixed+Verified 25.10.2026**: `tools/legal/pravo_check.py` переписан (HTTP-only publication.pravo.gov.ru — HTTPS срезается ТСПУ; `--link` → дата публикации; `--new N` через RSS /api/rss; поиск → SEARCH_UNAVAILABLE с инструкцией, т.к. search.pravo.gov.ru NXDOMAIN). Live: link 0001202610240002 → «24.10.2026»
- [ ] **PLL-3 — Поиск судебной практики по статье/спору** (kad.arbitr.ru, sudact.ru): в отчёт Фемиды добавить блок «практика применения» со ссылками на дела (по «да») — **Fixed+Verified 25.10.2026**: `tools/legal/sudact_search.py` — poll-протокол doc_ajax (X-Requested-With, «status:new» → poll ~0.9s), секции arbitral/regular/magistrate/law, --case-doc, case_no-regex, JSON + browser_url. Live: «о персональных данных согласие ст. 11» → >100k документов, case_no 4/5. Ограничения в docstring: lawchunkinfo не работает в открытой форме; троттлинг → «Документы не найдены» на всё, пауза 15-20с, 1 вызов на тему. SKILL.md: раздел «Утилиты-цитаторы» вшит
- [ ] **PLL-4 — Мониторинг регуляторики по расписанию.** Заодно артефакт «обози и сравни»: ночной дайджест «что изменилось в теме X за 30 дней, датированный источник на каждый пункт» — вшить в ночной конвейер (шерлок/фемида) (по «да») — **Fixed+Verified 25.10.2026**: `tools/legal/legal_monitor.py` (--days/--new/--topics/--markdown/--out/--dry-run), источник RSS /api/rss (жив). Live: дайджест по «Правительства» → 10 актов; dry-run файл не пишет. Cron НЕ вшит самовольно — предложение Игорю (propose→approve): `30 7 * * * /usr/bin/python3 ~/freelance-2026/tools/legal/legal_monitor.py --days 1 --markdown --out ~/freelance-2026/reports/legal_digest.md`
- [ ] **PLL-5 — Память позиции команды.** kb-prep corpus `kb_legal` (ADR-005): позиции по прошлым договорам, стандартные оговорки — чтобы Фемида сверяла новый договор с «как мы раньше отвечали». Связано с AN-2 (anydoc) — **Blocked (VPS)**: подготовлено без VPS — `tools/legal/kb_legal_recipe.md` (состав корпуса, пошаговый план, DoD) + `tools/legal/kb_legal_sources.json` (152/44/223/ZoZPP/98-ФЗ, ГК1/ГК4, ПП-1236, карточки статей, правила ingest). Внедрить после оживления VPS по recipe

НЕ принято: покупка Perplexity Enterprise ($40/seat) — RF-юрисдикция не покрывается,«конфиденциально» (потребительские тиры тренируются на промптах, Heppner-риск); чистые паттерны заимствуем, платим $0.

## 🎙️ ELV — ElevenLabs Eleven Realtime (разбор дропа 25.10.2026)

> Источник: дроп ТГ 25.10.2026. Верифицировано (26.10 via web): elevenlabs.io/blog/realtime
> (05.10→20.10.2026), docs.io changelog 19.10.2026, the-decoder.com 20.10.2026,
> benchmarks.coval.ai/providers/elevenlabs (независимый замер). Статус: «проверено (src)».

**Claims подтверждены независимо:**
- Speech-to-Speech: STT+VAD/turn-taking+LLM+TTS = одна система. Realtime API OpenAI-совместим (меняешь endpoint+model — клиент тот же).
- v1 Max: 98.8% Big Bench Audio, TTFA 570ms; v1 Mini: 75.9%, 620ms — ЦИФРЫ РАЗЛИЧАЮТСЯ, Mini НЕ «столько же точна» (дроп умолчал).
- Независимый eval Artificial Analysis: Big Bench Audio + Full-Duplex-Bench (95.8%) + Speech Agent Arena (task success 87.1%) — не только self-report.
- Русский: 90+ языков обе версии. 17k+ голосов. Pricing: за минуту + токены (Max > Mini, цифры не публиковались в независимых источниках).
- Тонкости из docs, которых нет в дропе: Max требует token limit ≥1024; Mini недоступна в Zero Retention Mode/HIPAA; Realtime-модели не годятся для text-only.

**Маппинг на наш стек (Levitan/AVM):**
- Заменил бы цепочку livekit-sip: STT→OmniRoute LLM→TTS одним WebSocket-агентом; turn-taking «угу» — прямо наш кейс (Levitan: лид-тишина 5с против обрезанного приветствия).
- Границы: (1) LLM внутри закрыт — теряем OmniRoute-роутинг/контроль и наш русский промпт-стек; (2) оплата ElevenLabs из РФ (карты) — нерешаемая без посредника-плательщика; (3) 152-ФЗ: передача аудио звонков в US-облако = ПД третьих лиц без согласия — нужно юр-заключение Фемиды, скорее «не для Mango-обзвона»; (4) цепочка STT+LLM+TTS у нас уже и так даёт приличный TTFA —выигрыш может быть marginal — надо мерить, не брать на веру.

**Задачи (не срочное):**
- [ ] **ELV-1:** Тест «11RT v1 Mini vs наш стек» на 10 русских реплик: TTFA, понимание «угу», перебивания, цена звонка/мин. Только ПОСЛЕ решения оплаты и 152-ФЗ-вопроса. (предложено → проверено src → к решению Игоря)
- [ ] **ELV-2:** ElevenAgents как Retell-альтернатива для MVP-прототипов (retell-conductor скилл — паттерн тот же). Низкий приоритет — Retell работает, менять не обязательно.
- [ ] **ELV-3:** Написать в `docs/lesson/`: паттерн «end-to-end STS модель = новая единица роутинга голосовых агентов» — учесть в ADR-006 (если будет) при выборе стека для AVM.

НЕ принято: миграция Levitan на Eleven Realtime без сравнительного бенчмарка и решения 152-ФЗ/оплаты.

## 🧪 UXT — First Users: 4 персоны-субагента перед запуском продукта (дроп 25.10.2026)

> Источник: дроп ТГ (промпт-рецепт, автор не назван). Верифицировано web 26.10:
> паттерн не выдуман — существует в OSS: persona-test скилл (iamneilroberts/
> claude-skills, персона-субагенты с quit-conditions и rubric-judging), Playwright
> Test Agents (planner/generator/healer), у нас в экосистеме: скилл ui-ux-tester
> (уже покрывает «документированные user flows»), accessibility-tester, e2e-runner.

**Суть паттерна:** перед запуском — 4 субагента играют новых пользователей и проходят
путь «landing → первый успешный результат»: нетерпеливый (кликует первую кнопку,
бросает при первой ошибке), скептик (читает цены/условия/политику, стоп на любом
непонятном), мобильный (375px + slow 3G — скрытая кнопка/горизонтальный скролл
= баг), крошитель (мусор в формы, back mid-flow, double-click → повторный submit).
Все затруднения → скриншот в qa/first-users/ → общая таблица, сортировка «сколько
персон застряло» → фикс (кроме pricing/terms — их только человек) → вторая партия
из 4 СВЕЖИХ субагентов, не видевших таблицу → сравнение до/после.

**Маппинг на наш стек (важнее, чем обычно):**
- Браузерный слой УЖЕ ЕСТЬ: native browser-tools OpenCode (45 тулов: табы, скриншоты,
  preview) + скилл `ui-ux-tester` — паттерн встаёт как новый режим поверх, БЕЗ
  Playwright MCP-установки (дроповский «если нет MCP — установи» у нас неактуален).
- Рецепту требуются правки: (1) throttle 3G в native browser недоступен —
  честно писать «не можем» (дроп это прямо разрешает); (2) субагенты ходят ПО
  ОЧЕРЕДИ, не параллельно — иначе табы и скриншоты конфликтуют; (3) роли идут
  поверх наших скилл-агентов (e2e-runner / ui-ux-tester), а не «голых» тулов.
- Границы: только local/preview, тестовая почта, тестовые платежи; НЕ гонять
  8 субагентов-прогонов на проде. Запускать только перед релизом (cost-aware,
  8 прогонов × 2 итерации = заметный расход токенов).

**Задачи:**
- [ ] **UXT-1:** Сделать команду `first-users` (skill/command-файл): 4 персоны как
      промпт-шаблоны + прогон поверх native browser-tools + вывод таблицы, ранжированной
      по «сколько персон застряло на месте» — по «да». Скелет почти есть в ui-ux-tester,
      добавить персоны-quit-правила как в persona-test.
- [ ] **UXT-2 (после UXT-1):** базовый прогон на кандидате (dashboard или
      sinergy-лендинг), отчёт до/после со скриншот-пруфами.
      ⏰ **НЕ ЗАБЫТЬ (Игорь, 25.10.2026): лендинг на подходе — записан КАК
      ВАРИАНТ ДЛЯ ТЕСТА #1.** Как только лендинг готов/превью поднят — первым
      же прогоном гонять через `first-users` (UXT-1). Договорились заранее.
- Альтернативный стек: `npx playwright init-agents` (официальные Playwright Test
  Agents) — если native browser-tools не хватит по сценарным возможностям.

## 📇 FCP — Firecrawl Alexandria People Data: 270M контактов в чате агентов (дроп 25.10.2026)

> Источник: дроп ТГ. Верифицировано web 26.10: firecrawl.dev/blog/
> alexandria-people-enrichment (01.10), blog/claude-for-people-search (18.10),
> changelog/people-data-relaunch (20.10), X/@firecrawl. Статус: «проверено (src)».

**Claims подтверждены:** 270M+ people/company records; плагин в ChatGPT/Claude
(и Codex); провайдеры: Apollo (поиск по должности/компании — БЕСПЛАТНО по их
jack: «Apollo people search is free»), FullEnrich (по навыкам/истории, вериф.
email — жжёт кредиты, требует админа-акцепт термов), Data Legion (дозаполнение
существующих контактов). Free: 1000 кредитов/мес. Дроп точен, умолчал:
FullEnrich нужен team-вход; тарифы сверх free не озвучены (кредит/почту —
проверить при внедрении).

**Маппинг на наш стек:**
- Через ChatGPT/Claude плагин — чужой стек; для OpenCode — Alexandria доступен
  через **Firecrawl MCP / CLI** (`npx firecrawl-cli init`) → вписывается наш путь.
- Ути-кейсы наших проектов: AI-Scout (поиск экспертов/заказчиков),
  Batrak (контакты ответственных для откликов — осторожно), Sherlock
  (компетит-аудит), lead-gen под Kwork-продажи.
- **Жёсткая юр-граница (ai-defender + Фемида, ДО любой работы с ПД):**
  собирать ФИО+рабочие email россиян/ЕС = обработка ПД (152-ФЗ; GDPR для ЕС).
  Холодные рекламные письма по e-mail физлицам в РФ = нарушение ст. 18
  38-ФЗ «О рекламе» (предварительное согласие обязательно; штрафы РКН/ФАС
  по 13.11 КоАП). B2B-рассылки на корпоративные ящики — серая зона по
  юрисдикциям. ВАЖНО: использование через плагин ChatGPT/Claude = ПД уходят
  в чужой чат-стек — наш принцип «закрытой связки» (US v. Heppner) здесь
  применяется ещё строже, чем в юр-задачах.

**Задачи:**
- [ ] **FCP-1 (по «да»):** прототип через Firecrawl MCP/CLI в OpenCode: тест
      «найди 10 человек по роли в РФ-компаниях» → проверить (а) покрытие
      RU-рынка (Apollo/FullEnrich — западные данные; RU-покрытие может быть
      слабым), (б) свежесть записей, (в) расход кредитов на email. Стоп-гейт:
      юзать только на НЕ-персональных данных (компании/должности глобал),
      никакие выгрузки email РФ-лиц — до юр-вывода.
- [ ] **FCP-2:** юр-чайник Фемиде: «моё использование Alexandria = ПД?» разбор
      (152-ФЗ транграничность, 38-ФЗ ст.18) — ЗАПУСТИТЬ ДО любой email-желики.
- НЕ принято: подключение плагина в личный ChatGPT/Claude-аккаунт с загрузкой
  ПД; сбор email-баз для холодных писем без согласия.

- НЕ принято: подключение плагина в личный ChatGPT/Claude-аккаунт с загрузкой
  ПД; сбор email-баз для холодных писем без согласия.

## 🎣 LEAD — Лид-усиление в сообществах (план на 26.10, задача Игоря)

> Задача: вступать в диалоги сообществ под личным аккаунтом → выводить
> потенциальных клиентов в личку → сотрудничество. Вопрос: автоматизировать
> (Hermes/инструменты)? Главная забота Игоря: адекватное поведение агента.

**Вердикт (экспертное мнение 25.10):** полностью автоматическую версию делать
НЕЛЬЗЯ (ToS сообществ, бан личного аккаунта, «AI-письмо» клиенты чуют, реп-риск);
делаем **копилот-схему** — агент нагружает 70% труда вокруг диалога, отправка —
только Игорем. Отправку сообщений из-под личного аккаунта не автоматизируем
(решение оформлено, пересматривается только с новым вводом).

- [ ] **LEAD-1 (если «да» сегодня/утром):** скилл `lead-copilot`: (а) скоринг
      лида по 5 сигналам (боль, бюджет, срочность, роль, тайминг); (б) черновик
      ответа в тоне Игоря (примеры его прошлых сообщений в контекст); (в) фут
      ап-напоминания (следующий шаг по каждому лиду); (г) лог лида: кто, откуда,
      стадия → claude-mem + файл. Полу-авто (propose→approve, паттерн batrak).
- [ ] **LEAD-2:** мониторинг сигналов: TG-поиск по ключевикам руками + агент
      классифицирует скопированные диалоги; НЕ юзерботы, НЕ автомассликинг.
- Границы (ai-defender): собранные лиды = ПД; хранить локально, не пихать в
  облачные чаты; массовые рассылки = рассогласовать (см. FCP, 38-ФЗ ст.18).
- **Тех-вопрос «антидетект-браузеры с API/сценариями» — разобран 25.10:** НЕ
  решают нашу задачу. (1) TG — не веб: заход через MTProto-клиент, фингерпринт
  браузера (canvas/WebGL/UA) не учитывается; TG смотрит на api_id/session-мету
  (кстати, РОТАЦИЯ фингерпринта сама по себе флаг — нужен стабильный preset).
  (2) Баны 2026 = поведенческий скоринг: равномерные интервалы, отсутствие
  пауз/idle, одинаковые тексты, CQS-скор, жалобы людей — AD-браузер на это
  не влияет вообще. (3) Мультя-аккаунтность AD (Dolphin Anty API+Playwright,
  AdsPower Local API+RPA) ортогональна нам — у нас ОДИН личный аккаунт.
  (4) Даже лидген-гайды 2026 (dev.to, 15.10) сходятся с нашей копилот-схемой:
  «full-auto first contact reads as spam», автоматизировать рутину, человек —
  в первом касании. Вердикт: AD-браузер для TG-задачи = деньги за ложную
  надежду; пересматривать только если когда-нить будем работать на веб-
  платформах (LinkedIn-web/FB) — и то отдельным решением.
- **⚡ УТОЧНЕНИЕ Игоря (25.10 вечер): сообщества скорее всего в VK, браузерный
  формат; нюансы завтра (26.10).** Пер-оценка: AD-браузеры становятся
  РЕЛЕВАНТНЫМИ по классу (VK = веб → фингерпринт/IP/сессии имеют силу). Но
  для ОДНОГО личного аккаунта рекомендация не меняется: работать с реального
  устройства/обвязки — резкая смена фингерпринта зрелого VK-аккаунта сама по
  себе аномалия (история аккаунта привязана к старой девайс-обвязке).
  AD-браузер — на потом, рассмотреть при вторых аккаунтах/масштабе. VK-спе-
  цифика: анти-спам по жалобам между личками мягче на поведение, а не на
  фингерпринт (лимит на символы «не-другу», засылка = быстрые ограничения);
  у VK есть официальный сообществ-слой (Bot API/виджеты), но это для
  OUR-community, не для личного аутрича. Мониторинг/чтение — native
  browser-tools OpenCode (только чтение/копирование, никакой автотипизации);
  отправка — Игорем вручную. Ждём деталей завтра.

## 🧬 RPL — replica-skill: 11 скиллов «клонируй любое приложение» (дроп 25.10.2026)

> Источник: дроп ТГ → https://github.com/Jakeschincariol/replica-skill.
> Верифицировано web 25.10: репо живое, **MIT**, **5.4k★ / 954 forks**
> (рост 1.7k→4.3k за 12 дней по git-now, 03.10.2026 v1.0, соло-автор Jake
> Schincariol — opusjake.ai, 1.1k followers, опыт скилл-пакетов: linkedin-
> agent-skill, arena-skill и др.). Skills Directory Security: **A (100/100)**.
> Тулы — stdlib-only Python (6 шт: imgdiff, parity, reviews, contrast, sweep,
> listing), есть тесты. Дроп точен, умолчал: это Claude-скиллы — но формат
> SKILL.md с нами совместим.

**Суть:** 11 команд в пайплайн: recon (реверс-инжиниринг с публичных страниц +
свой аккаунт) → architect (стек/схема) → design (дизайн-система токенами) →
build (поэкранно по features.csv) → backend → test (Playwright-спеки, S1/S2
баги) → diff (parity-скор против оригинала, imgdiff на скриншотах) →
**entrepreneur** (читает реальные отзывы App Store/G2/Capterra/Reddit → что
ненавидят юзеры → фичи-фиксы + позиционирование) → brand (имя, TM/domain
чеки, sweep по коду до чистоты) → launch (лендинг + листинг стор) → deploy.

**Маппинг на наш стек:**
- Формат совместим: папки replica-* → `~/.config/opencode/skills/` (наши
  скиллы такой же структуры) — 5 мин установки, ноль зависимостей.
- Утилиты ценны СВЕРХ клонирования: imgdiff/parity — пригодятся в наш
  🧪 UXT (скрин-диффы), sweep/contrast — ai-defender рядом.
- **replica-entrepreneur — отдельная жемчужина:** майнинг жалоб юзеров
  оригинала → готовый УТП-угол. Полезно для НАШИХ продуктов (лендинг на
  подходе!) без всякого клонирования.

**Юр-границы (заделка в правила при установке, по духу ридми + наша Фемидов-
ская оптика):** clean-room (функциональность не копирайтна — ок), но дизайн
близко к оригиналу + та же ниша = риск недобросовестной конкуренции/трейс-
дресс (РФ: ст. 14.6 135-ФЗ «О защите конкуренции»); ToS оригинала «нельзя
строить конкурента» — скилл сам честно стопит; НЕ клонировать: каталоги-
контент, сети (marketplace), закрытые API. Для РФ-рынка: клон глобального
сааса под RU-аудиторию — законнее и осмысленнее, чем клон RU-соседа 1:1.

**Задачи:**
- [ ] **RPL-1 (по «да»):** установить 11 папок в `~/.config/opencode/skills/`,
      проверить подхват OpenCode, прогнать README-пример imgdiff на тестовых
      PNG. (~20 мин)
- [ ] **RPL-2 (после RPL-1, по «да» отдельно):** мини-пилот: один простой
      сервис → recon → entrepreneur (репорд по болям) — даже без build/diff
      это продукт-исследование. Выбор сервиса согласовать.
- [ ] **RPL-3 (быстрая победа, можно отдельно):** прогнать replica-entrepreneur
      логику на 2-3 конкурентах нашего лендинга → боли аудитории → текст УТП.
      Дешёвый способ разговорить «лендинг на подходе».
- cost-aware: полный клон больших приложений = недели сборки — пилотить
  только на малых VPN/B2B-тулах (вариант «booking-линк» из README-примера).

## 🎨 ADS — ai-design-skills (Elaya): landing-page-design + design-to-motion (дроп 25.10.2026)

> Источник: дроп ТГ → https://github.com/elayadesign/ai-design-skills.
> Верифицировано web 25.10: MIT, **5.0k★ / 354 forks** (+1.4k звёзд за 15
> дней, Trendshift), создан 29.07.2026, 4 коммита, соло-автор — дизайнер
> Elaya (@elayadesigns, elaya.design), стала виральной в X (169k/142k
> просмотров): «дизайнер, 2 месяца, стена лендингов через Higgsfield +
> Claude + Cursor + свой скилл». Порфолио-подтверждение налицо, репо
> молодое и без issue-истории — читать аккуратно.

**Что внутри (2 скилла + сиблинг-репо):**
- `landing-page-design` — лендинг с нуля: intake-вопросы → структура →
  конверсионный копирайт → полная визуальная система (тайп, спейсинг,
  радиусы, motion) в одном файле; дизайн-валю внизу файла — форкнешь, правишь токены, остальное тянется.
- `design-to-motion` — статик-дизайн → «пиксельно точный» анимационный
  шоукейс (empty→loaded, всё на цикле, MP4 для X + GIFы) — правила
  адаптированы изMIT-emilkowalski/designer-skills/animation-principles.
- Сиблинг: `redesign-skill` (отдельный репо) — аудит существующего сайта:
  generic-паттерны, отсутствующие стейты, sloppy-код → фикс на месте.

**Маппинг на наш стек (важно — у нас ПЕРЕКРЫТИЯ):**
- У нас уже есть: `frontend-design` (анти-generiс гайд), `anti-ui-slop-
  reviewer`, `ui-designer`, apple-design, web-design-guidelines. Elaya-скиллы
  НЕ дублируют их 1:1: landing-page-design — это СТРУКТУРНЫЙ пайплайн
  (intake→structure→copy→tokens) поверх которых наши гайды смотрят за
  slop-ом. Комплементарно, встаёт к Рембрандту.
- Скиллов у нас 230+ — правило lazy-load: ставим МАКСИМУМ 2 папки, не
  коллекционируем ради коллекции. design-to-motion частично дублирует
  наш HyperFrames-стек (у нас шире) — приоритет низкий.
- Самое своевременное: **лендинг на подходе** (см. UXT-2) — перед сборкой
  прогнать через intake-чёклист Elaya, наши токены вписать в design-values.

**Границы:** дизайн-валю скиллов = вкусы Elaya (не наш брэнд) — править
перед использованием; скиллы про КАК, не про ЧТО — контент и УТП наши.

**Задачи:**
- [ ] **ADS-1 (по «да»):** установить `landing-page-design` (и опц.
      `redesign-skill`) в `~/.config/opencode/skills/`, вписать наши
      дизайн-валю (шрифты/цвета/spacing) в design-values секцию.
- [ ] **ADS-2 (к лендингу UXT-2):** перед сборкой лендинга — intake-вопросы
      скилла → структура → конверсионный copy → визуальная система; далее
      гонки через наш anti-ui-slop-reviewer. После сборки — UXT-прогон.

## ⚙️ VLM — vLLM: движок инференса LLM (дроп 25.10.2026) — ⏸ не применимо сейчас

> Источник: дроп ТГ → https://github.com/vllm-project/vllm. Верифицировано
> API 26.10: **MIT/Apache (Linux Foundation-проект), 95 572★ / 23 978 forks**,
> создан 09.02.2023, пуши ежедневно. Клеймы дропа точны: PagedAttention,
> 200+ моделей, OpenAI-совместимый API.

**Маппинг на наше железо (честно):** MacBook **M1 / 8 ГБ RAM / 7 GPU-ядер**.
- vLLM изначально CUDA/ROCm; в 2026 появился **vLLM-Metal** (community-плагин,
  MLX-бэкенд, macOS Sonoma+) — формально Apple Silicon поддерживается.
- НО на 8 ГБ unified memory смысла ноль: сервить можно только ≤1-3B, а у нас
  уже есть Ollama (qwen2.5:0.5b/1.5b + nomic-embed) — тот же класс задач проще.
- Реальная выгода vLLM (сотни параллельных запросов, PagedAttention) включается
  на **GPU-сервере (NVIDIA)** — у нас такого нет: VPS RU-хост, GPU-аренда = $$
  и отдельная юр-тема.

**Вердикт: «проверено (src)» → НЕ принято (не применимо сейчас).** На полку:
пригодится, если (а) появится GPU-сервер / облако под боты-RAG при росте
нагрузки, (б) будем сравнивать cost API-провайдеров vs своё хостинг-решение.
Замены на сегодня: Ollama (локально), OmniRoute + провайдеры (облако).

## 🧩 OPN — дроп «anomalyco/opencode» = наш собственный инструмент (дроп 25.10.2026)

> Дроп ТГ: «+5 921★ за неделю, 221 634 всего, open-source агент, build/plan,
> desktop». Верифицировано API 26.10: **anomalyco/opencode, MIT, 221 714★,
> 29 647 forks**, создан 30.04.2025, пуши ежедневно, homepage opencode.ai.
> Клеймы точны. Вывод: это инструмент, в котором мы работаем — новизны нет,
> но проверка версий дала полезный инсайт ↓

**Инсайт по версиям (проверено по GitHub releases 26.10):**
- Desktop `OpenCode.app` = **2.1.4** — свежее, чем brew cask (там 2.1.0);
  десктоп распространяется вне GitHub releases, автоапдейт встроен → **ок,
  обновлять не нужно**
- CLI `~/.opencode/bin/opencode` = **1.19.0**, последний релиз **v1.19.4**
  (22.10) → отставание ПАТЧЕВОЕ (4 патча), не мажорное. Ветки разные:
  1.19.x = CLI, 2.x = desktop — это разные продуктовые линии
- БД `opencode.db` = schema **v2 preview** (desktop 2.1.4). `opencode-db 0.14`
  читает v1-таблицы → export=0 это **schema-level** (тул vs v2 база), а НЕ
  рассинхрон CLI. Прежняя гипотеза в этой заметке опровергнута (HT-3).

- [ ] **OPN-1 (по «да», 5 мин):** обновить CLI 1.19.0 → 1.19.4 (гигиена,
  не фикс export). Делать НЕ в середине рабочей сессии (ND-1).
- ODB-2 (vacuum) — не зависит от OPN-1. Export в finish-day (ODB-3) —
  blocked до v2-поддержки в opencode-db (issue автору либо ждать).

## 🖥️ MIG — «mini как сервер»: план миграции (обсуждено 26.10.2026)

> Решение по железу: M5 mini 24 ГБ/512 ГБ как сервер 24/7 + текущий M1-ноут
> как тонкий клиент (монитор большой уже есть). Задача НЕ про «синхронизацию
> проекта между машинами», а про «проект живёт на одной машине» — так исчезают
> конфликты, расхождение .env, разные истории сессий и двойные базы.

**Архитектура:**
```
Ноут M1 ──Tailscale/SSH──▶ mini (единственный «мозг»)
                            • файлы проекта (SSoT)
                            • opencode.db (история сессий, 1 шт.)
                            • claude-mem, .env, launchd-джобы
                            • Ollama + внешний SSD под модели
                            • бэкапы на NAS DS720
GitHub = страховка/бэкап (finish-day уже пушит), НЕ транспорт синхронизации
```

- [ ] **MIG-1 (после покупки mini):** базовая связка — Tailscale на обе машины,
      `ssh mini`, `tmux new -A -s work`, `opencode` внутри; Remote Login (SSH) +
      Screen Sharing включены.
- [ ] **MIG-2:** 24/7-режим: `pmset -a sleep 0 disksleep 0 autorestart 1 womp 1`,
      автологин (FileVault off ИЛИ `fdesetup authrestart` после ребута — иначе
      GUI-агенты/CUA после света не поднимутся), дисплей гаснет — агентам не мешает.
- [ ] **MIG-3:** перенос окружения: `~/.config/opencode/` (скиллы, AGENTS.md,
      opencode.jsonc), `~/freelance-2026`, Ollama-модели → внешний SSD
      (`OLLAMA_MODELS`), ключи `.env` переносятся РУКАМИ (в git их нет).
- [ ] **MIG-4:** launchd-джобы (night_reader, JobHunter, geo_monitor) + бэкапы на
      NAS DS720; Time Machine на NAS уже настроен.
- [ ] **MIG-5 (опционально):** claude-mem туннель с ноута
      `ssh -L 37878:localhost:37878 mini` — если понадобится память при локальной
      работе на ноуте.
- [ ] **MIG-6 (ОТЛОЖЕНО по решению Игоря 26.10):** чистка репо — вложенный
      `projects/ai-eggs/vezem` (530 МБ, gitlink) вынести в отдельный репозиторий
      или submodule; `.git` 863 МБ → будущий клон на mini будет лёгким.
      Вернуться перед клонированием на mini.

**Правила при работе с двух машин (вариант B, если понадобится):**
`git pull --rebase` в начале, commit+push в конце, ветка на задачу (worktree-per-task),
один файл не править на двух машинах одновременно, `.env` — только на mini.

## 🖨️ IM2 — iMac Mid 2011 (i3-2100, 24 ГБ) как worker-нода (решено 26.10.2026)

> Аппарат: **iMac12,1** — 21.5", Core i3-2100 (2C/4T, Sandy Bridge, **без AVX2**),
> 24 ГБ DDR3, Radeon HD 6750M, **USB 2.0**, Gigabit Ethernet, потолок macOS =
> High Sierra 10.13.6. Playbook: `tools/ops/imac_worker_setup.md`,
> скрипт: `tools/ops/imac_worker_bootstrap.sh`.

**Вердикты (проверено 26.10):**
- ❌ **Target Display Mode — не работает.** Дока Apple (support/105126, upd 15.05.2026):
  подключаемый Mac должен быть «2019 или раньше, macOS ≤ 10.15.8». M1 Air = 2020,
  Apple Silicon TDM не поддерживает. TargetBridge требует iMac 2017+. Тема закрыта.
- ❌ **LLM-сервер** — Sandy Bridge без AVX2, ~1100 однопоточных баллов vs ~3700 у M1
  → 2-4 ток/с на моделях ≤1B. 24 ГБ RAM не помогают: узкое место — CPU.
- ❌ **CUA-хост** — нужен Apple Silicon + Virtualization.framework. Архитектурно нет.
- ❌ **Основная dev-машина** — потолок High Sierra; Homebrew снял поддержку в 2023,
  современный Node/Python-стек не ставится.
- ✅ **Offline/batch-воркер** — эмбеддинги (nomic-embed), `kb-prep pdf`, ночной
  парсинг, проверка бэкапов, `git fetch` тяжёлых репо. CPU-bound рутина уходит с mini.
- ✅ **Дежурный экран** (дашборд/логи в полноэкранном браузере) — бесплатно по RAM.
- 🟡 **x86_64 Docker-раннер** — если появятся x86-only образы.

**Цена владения:** ~85 Вт idle → ~60 кВт·ч/мес (~400-500 ₽); железо 2011 г.;
**автостарта после потери питания нет** (у Mac нет BIOS-настройки) → в критический
путь не ставить; секреты/.env там НЕ держать.

- [ ] **IM2-1 (Игорь, 10 мин):** включить iMac, подключить **кабелем Ethernet**
  (Wi-Fi BCM4331 на Ubuntu — лишняя боль), зафиксировать IP в роутере
  (DHCP reservation). Проверить модель: «Об этом Mac» → `iMac12,1`.
- [ ] **IM2-2 (Игорь, 30-40 мин):** загрузочная флешка Ubuntu 24.04 LTS Desktop
  (`Etcher`), старт с Option при включении, установка «стереть диск целиком».
  Сразу: `sudo apt install openssh-server tmux` + включить Remote Login.
- [ ] **IM2-3 (после IM2-2):** прогнать `imac_worker_bootstrap.sh --dry-run`, затем
  `--apply` (пакеты, отключение сна, проверка). ⚠️ tailscale — ОПЦИЯ: дома обе
  машины в одной LAN, для удалённого доступа решим отдельно (Tailscale/WireGuard/
  Cloudflare Tunnel) с учётом ADR-002.
- [ ] **IM2-4 (первый полезный прогон):** перенести на него `kb-prep pdf` +
  пакетную эмбеддинговую сборку (nomic-embed через Ollama на CPU); прогнать на
  реальной пачке PDF из vault → сверить результат с тем, что делает mini.
- [ ] **IM2-5 (апгрейд, опц., ~$40 + 40 мин):** заменить HDD на **SSD 500 ГБ SATA**
  (в 21.5" 2011 стекло на магнитах — разбирается присосками, гайд iFixit).
  Даёт 10x на загрузке и убирает seek-залипания при batch-нагрузке. Внешние
  диски на этом узле смысла не имеют (USB 2.0 = 40 МБ/с).

## 🧰 LGT — Личные тулы (по решению Игоря)

- [ ] **LGT-1 (21.10.2026, pending)** — **Tangerine for Mac** (LEAP STUDIO, Mac App Store, v2.0.1, one-time покупка после 20 бесплатных файлов; Apple Silicon M1+, macOS 13+): https://tangerineformac.com/. Проверено src 21.10: локальная обработка (ADR-002 дружелюбно), 275 конвертаций (PDF→DOCX/MD/EPUB, HEIC, видео/аудио, RAR-вход, QR), UX «тянешь файл + Shift = колесо форматов». НЕ для агентов (GUI-only, наши скиллы ocr-and-documents/ffmpeg/sips закрывают CLI-часть). Действие: Игорь тестирует 20 бесплатных файлов на реальных кейсах (HEIC, PDF→DOCX для Фемиды, ужатие видео) → по итогам: покупать/нет. Покупка разовая, без подписки.
- Окно для будущих тулов этого класса: только локальные, без подписок, macOS.

## 🟢 ОКТЯБРЬ 2026 (Игорь – аналитик)

- [ ] 13.10.2026 (Сб) – Создать структуру папок для постов: ai-eggs/content/posts/2026-10/{vk,ok,makc,tg,dzen} и подготовить шаблоны с указанием размеров изображений и лимитов текста для каждой платформы.
- [ ] 14.10.2026 (Вс) – Подготовить пост для ВК: тема «ошибки зимнего содержания» (с UTM‑меткой utm_source=vk&utm_medium=post&utm_campaign=okt2026_zima), изображение 1200x628 px (Rembrandt стиль).
- [ ] 14.10.2026 (Вс) – Запустить первый автообзвон (Levitan) 16:00‑19:00, зафиксировать результаты в Bitrix24 (сегмент клиентов 2022‑2026).
- [ ] 15.10.2026 (Пн) – Подготовить пост для Одноклассников: тема «кормление в первый неделе» (с UTM), изображение 1080x1080 px.
- [ ] 16.10.2026 (Вт) – Подготовить пост для МАКС: тема «профилактика заболеваний» (с UTM), изображение 800x800 px.
- [ ] 17.10.2026 (Ср) – Подготовить пост для Telegram: тема «первые 72 часа жизни цыплёнка» (с UTM), изображение через Rembrandt (1200x628).
- [ ] 18.10.2026 (Чт) – Подготовить пост для Яндекс.Дзен: статья «подготовка курятника к зиме» (2000‑3000 знаков, UTM).
- [ ] 19.10.2026 (Пт) – Подготовить пост для ВК: тема «расчёт необходимого количества цыплёнка» (с UTM), изображение 1200x628.
- [ ] 20.10.2026 (Сб) – Подготовить пост для Одноклассников: тема «подготовка птичника к весне» (с UTM), изображение 1080x1080.
- [ ] 21.10.2026 (Вс) – Подготовить пост для МАКС: тема «признаки здорового суточного цыплёнка» (с UTM), изображение 800x800.
- [ ] 21.10.2026 (Вс) – Запустить второй автообзвон 16:00‑19:00, фиксация результатов в Bitrix24.
- [ ] 22.10.2026 (Пн) – Подготовить пост для Telegram: тема «опрос: Как прошёл ваш сезон‑2026?» (с UTM), изображение через Rembrandt.
- [ ] 23.10.2026 (Вт) – Подготовить пост для ВК: тема «итоги месяца: что работает в нашей стратегии?» (с UTM), изображение 1200x628.
- [ ] 24.10.2026 (Ср) – Подготовить пост для Одноклассников: тема «рекомендации по кормлению в холодное время» (с UTM), изображение 1080x1080.
- [ ] 25.10.2026 (Чт) – Подготовить пост для МАКС: тема «запоминание: советы по уходу за птицей зимой» (с UTM), изображение 800x800.
- [ ] 26.10.2026 (Пт) – Подготовить пост для Telegram: тема «профилактика заболеваний у птицы» (с UTM), изображение через Rembrandt.
- [ ] 27.10.2026 (Сб) – Подготовить пост для ВК: тема «оборудование, экономящее корм» (с UTM), изображение 1200x628.
- [ ] 28.10.2026 (Вс) – Подготовить пост для Одноклассников: тема «ошибки зимнего содержания – повтор» (с UTM), изображение 1080x1080.
- [ ] 28.10.2026 (Вс) – Запустить второй автообзвон 16:00‑19:00 (уже указан выше, но оставляем как подтверждение) – фиксация результатов в Bitrix24.
- [ ] 29.10.2026 (Пн) – Подготовить пост для МАКС: тема «преимущества локального производства цыплёнка» (с UTM), изображение 800x800.
- [ ] 30.10.2026 (Вт) – Подготовить пост для ВК: тема «как выбрать качественный комбикорм» (с UTM), изображение 1200x628.
- [ ] 31.10.2026 (Ср) – Подготовить пост для Одноклассников: тема «подготовка к весеннему сезону: проверка оборудования» (с UTM), изображение 1080x1080.
- [ ] 31.10.2026 (Ср) – Подготовить итоговый отчёт за октябрь: сравнение CPL по каналам (соцсети, сайт, телефония) с потолком рентабельности, рекомендации на ноябрь.
