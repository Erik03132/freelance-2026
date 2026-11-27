# ACTIVE_TASKS.md — активное (перекомпактировано 2026-10-10)

> SSoT активных задач. Августовские истории, идеи и отчёты — в архиве:
> `checkpoints/active_tasks_archive_202608.md` (см. указатели в секциях).
> Предыдущая версия: `ACTIVE_TASKS.md.bak-20261010`.

> ⛔ VPS и мост Mac→VPS не проверять с 25.11.2026 (решение Игоря: серверов
> больше нет); проверки убраны из `tools/ops/start_day.sh`.

## 💅 IZ — Изольда: частный мастер по косметике/депиляции, Москва (старт 26.11.2026)

- [x] IZ-1 — ✅ Fixed + Verified (26.11): 4 отчёта в `projects/izolda/research/` + сводка `00-executive-summary.md`.
- [x] IZ-2 — ✅ Fixed (26.11): `marketing/strategy.md` (позиционирование, ЦА, каналы, цены).
- [x] IZ-3 — ✅ Fixed (26.11): `marketing/roadmap.md` (фазы 0–4, бюджет, метрики).
- [x] IZ-4 — ✅ Fixed (26.11): `marketing/content-plan.md` (17 тем, 4 кластера, ритм).
- [x] IZ-6 — ✅ Fixed (26.11): `docs/adr/ADR-001-channel-stack.md` (стек каналов, статус «Предложено»).
- [x] IZ-5 — ✅ Fixed + Verified (26.11): объявление прочитано через одолженную вкладку;
  адрес (Локомотивный пр., м. Окружная), прайс 11 позиций, 3 отзыва, 10 фото →
  `research/05-avito-listing.md`, `assets/avito/`. Стратегия и дорожная карта обновлены.
- [x] IZ-7 — ✅ Решено 26.11: публично «Алина», Изольда — внутреннее название; формат Игоря
  «стратегия + настройка»; бюджет Авито до 2 000 ₽/мес; цель — новые клиенты; сертификат есть,
  медлицензии нет. Коммерческое предложение → `marketing/commercial-proposal.md`.
- [x] IZ-9 — ✅ Fixed + Verified (26.11): разведка механизмов оспаривания отзывов
  (`research/06-reputation-defense.md`) и постоянный протокол реагирования с SLA и шаблонами
  (`marketing/reputation-defense.md`). Встроено в `commercial-proposal.md` и метрики.
  Цель — готовность к будущим отзывам, не разбор одного. Принцип: не обвинять без доказательств.
- [x] IZ-10 — ✅ Fixed + Verified (26.11): итог по двум вопросам Игоря —
  платные «удаления отзывов» не используем; лишние профили/карточки не создаём
  (`research/07-removal-multiprofile.md`). Встроено в `commercial-proposal.md`, ADR-001,
  `reputation-defense.md`. Причина: прямые правила Авито и 2ГИС, заявление Яндекса.
- [x] IZ-11 — ✅ Fixed (26.11): `marketing/offer-ready.md` — чистая версия КП для отправки
  Алине: без внутренних путей, с разделами «что не делаем», метриками и протоколом реакций.
  Стоимость услуг не упоминается (бартер). Второй этап = мини-сайт, статьи, ВК, Дзен.
  Единственный платёж — Авито до 2 000 ₽/мес. Контакт @erik03132 указан.
  Добавлена `marketing/offer-telegram.md` — версия чистым текстом без Markdown/таблиц
  для копирования в сообщение Telegram. Готово к отправке.
- [x] IZ-12 — ✅ Fixed (26.11): `marketing/first-3-days.md` — план на первые 3 дня с ролями
  Игоря и Алины, критериями готовности и готовыми текстами сообщений.
- [x] IZ-13 — ✅ Fixed + Verified (27.11): создан агент Изольда по плану
  `docs/superpowers/plans/2026-11-27-izolda-agent.md`; eval 3/3 PASS, валидатор PASS,
  негативный черновик отклонён. RED до создания файлов не был — файлы ушли в параллельные
  субагенты раньше валидатора.
- [ ] IZ-8 — ждём от мастера: доступы (телефон/Telegram, Яндекс Бизнес, 2ГИС), номер дома,
  подтверждение «Мария Депиляция», согласие на фото и видео. Текущий спорный отзыв больше
  не разбираем: Авито отказало в возражении, повторных попыток не делаем — только протокол
  на будущие отзывы.

> ⏰ **ПОРЯДОК ДНЯ (25.10.2026):** лендинг на подходе → как готов первый
> превью — прогнать через паттерн 🧪 UXT (4 персоны-субагенты, first-users).
> Записано в UXT-2, НЕ забыть.

## 🧠 HMS — Agentic Context: Hermes / Honcho / Obsidian LLM Wiki (дроп 17.11.2026)

**Статус: разбор сделан, не начато.** Источник: `youtu.be/nlYuDKdDvMY` (Wanderloots, ~41.5K, 20 мин).

Проверка источников (17.11.2026, правило 13):
- **Hermes Agent** — Nous Research, `hermes-agent.nousresearch.com`, **MIT**, self-host/cloud, десктоп
  (macOS/Win/Linux), плагины (tools/hooks/themes), «скиллы из опыта». Реальный, но это **другой харнесс**:
  переезд с OpenCode не окупается — на OpenCode завязаны claude-mem, `eval_gate.sh`, holdout (RSI-002),
  скилл-каскад L0/L1/L2.
- **Honcho** — `plastic-labs/honcho` ★8139, **AGPL-3.0**, FastAPI, self-host или `api.honcho.dev`,
  официально поддерживает OpenCode/MCP. Примитивы Workspace/Peer/Session/Message + фоновое reasoning →
  представления о пользователе и dialectic-запросы.
- **LLM Wiki** — gist `karpathy/442a6bf555914893e9891c11519de94f` реален, адресован в т.ч. OpenCode.
- «Pareto frontier памяти», «экономия 60–90% токенов» — источник = eval-страница вендора, независимо
  не подтверждено. Не считать решением.

**Вердикт по слоям:** LLM Wiki → **принято**; `User.md` → **принято**; Honcho → **отклонено** (25.11.2026);
Hermes как харнесс → **граница** (не мигрируем).

- [x] **HMS-1 (принято, первый шаг):** ✅ **Fixed + Verified (17.11.2026), v0.** Собрано `vault/wiki/`: `INDEX.md`, `sources.md`, `contradictions.md` + **15 страниц** сущностей (677 строк на всё, не вода). Правка `vault/CLAUDE.md` — раздел «Порядок чтения для агента» (+6 строк). Доказательства: битых ссылок и несуществующих путей-источников — **0** (скрипт-чекер чист); числа сверены с первоисточниками (408 обращений / ~515 млн бот-событий, Мюллер 17.06.2025, адопшн 951→12 174 — всё есть в `digest.md`); повреждённый `sinergy-expert-council/digest.md` (потеряна кириллица) подтверждён и в вики не домыслен. Найдено 7 расхождений источников, главные: llms.txt `<0.0001%` vs `<0,001%` (второй в 12 раз грубее), `skill-library-v2` план от 23.08 против пустого `catalog.json` от 16.11 и E407 у `npx skills add`.
- [x] **HMS-4.** ✅ **Fixed + Verified (25.11.2026).** Чекер вынесен в `tools/wiki_check.py` (stdlib, `--root/--wiki/--json/--dry-run`, коды 0/1/2) + eval `tools/tests/eval_wiki_check.py` (9 кейсов: ссылки, frontmatter, backtick-пути, якоря/URL-код, CLI, отсутствующий путь) — RED→GREEN. Правило обновления вики добавлено в `vault/CLAUDE.md`. Прогон на реальной вики: 18 файлов, 15 ссылок, 75 источников, **0 проблем**. Дыра закрыта: причина — темы **не закидывались** (`vault/00-Inbox` пуст, ночной читатель ни при чём); созданы `06-Library/tools/{honcho,firecrawl,kb-prep}/digest.md` из уже проверенных фактов (ACTIVE_TASKS HMS/FCW, ADR-005, AGENTS.md п. 19), с пометкой о нерабочем VPS с 25.11.2026; `INDEX.md`/`sources.md` обновлены.

- [x] **HMS-2.** ✅ **Fixed + Verified (25.11.2026).** Создан `~/.config/opencode/User.md` — SSoT профиля (кто/стек/стиль/запреты/бюджеты, на 25.11.2026; без секретов и без устаревших данных Hermes про VPS). Подключён ПЕРВЫМ: шапка глобального `AGENTS.md`, п. 0, `AGENTS.md` воркспейса и «Порядок чтения» `vault/CLAUDE.md`. Убраны дубли: «всегда на русском» и «$15–20/мес, лимит $20» из `AGENTS.md`. Eval `tools/tests/eval_user_profile.py` — PASSED (секции, дата, порядок, отсутствие дублей и секретов). Профили `hermes-sync/**/USER.md` не трогались — другая система, там есть устаревшие данные про VPS.
- [x] **HMS-3 (отклонено 25.11.2026):** Honcho-триал не делаем. Проверено: в `opencode.jsonc` нет
  MCP-блока, пакет/процесс/порт/импорты отсутствуют — систему **не используем**; память и профиль
  покрыты claude-mem + `User.md` + вики. Уникальное (фоновое рассуждение о пользователе,
  dialectic-запросы) не стоит AGPL-3.0 + self-host при отсутствии VPS и данных клиентов.
  «60–90% экономии токенов» — маркетинг вендора, независимо не подтверждён. Условие пересмотра:
  агент начинает терять контекст о клиенте между сессиями — тогда локальный self-host, 20 задач,
  замер латентности/токенов/качества.
- Границы при пересмотре: AGPL-3.0 — не встраивать в клиентские продукты с сетевым доступом; managed Honcho — не для NDA.

## 🔥 FCW — Firecrawl MCP: включить (разбор поста 16.11.2026)

**Статус: Verified (17.11.2026) — MCP-канал работает, 407 устранён.**

Проверка источников (16.11.2026, правило 13):
- npm `firecrawl-mcp` **v3.40.0** (пакет называется `firecrawl-mcp`, НЕ `firecrawl-mcp-server` — на втором npm 404).
- GitHub `firecrawl/firecrawl-mcp-server` ★7836, MIT, push 16.11.2026 → живой, официальный.
- Self-host: `firecrawl/firecrawl` ★202k, AGPL-3.0.

Что уже есть у нас: в `~/.config/opencode/opencode.jsonc` блок `mcp.firecrawl` **уже прописан**, но `"enabled": false` и нет `FIRECRAWL_API_KEY`. Т.е. работа = 2 строки, а не установка.

Что даёт поверх имеющегося (`browse` — реальный браузер, `webfetch` — одна страница):
- `/crawl` — обход сайта целиком в markdown (питание kb-prep, ADR-005);
- `/extract` по JSON-схеме — структурированные данные, не текст;
- `/search` + scrape одним вызовом;
- `/parse` PDF/docx (закрывает дыру poppler в kb-prep);
- научные индексы PubMed/bioRxiv/medRxiv/arXiv (для deep-research).

- [x] **FCW-1.** ✅ Игорь дал ключ (16.11.2026). Ключ в `~/.config/opencode/.secrets/firecrawl.key` (600), в конфиге через `{file:...}` — в открытом виде не лежит. `enabled: true`, `command` → `/Users/igorvasin/.local/bin/npx`.
- [x] **FCW-2.** ✅ CLI-канал проверен: `~/.config/opencode/tools/firecrawl/fc.py` — scrape реальной страницы вернул 23 КБ markdown, списан **1 кредит** (1507→1506). Остаток 1506, план 1000/мес, период до 22.11.2026.
- [x] **FCW-4.** ✅ **Verified 17.11.2026.** Корень найден: MCP-процесс **наследовал протухшие прокси-переменные** от приложения (`ALL_PROXY`/`HTTPS_PROXY` → порт `64468`, которого уже нет) → прокси отвечал `407`, а не Firecrawl. Дословные доказательства, что дело не в ключе и не в пакете: `curl --noproxy '*' https://api.firecrawl.dev/v2/team/credit-usage` → **200**, `remainingCredits 1506`; `curl -x 127.0.0.1:64468 ...` → **000** (порт мёртв). Фикс: в блоке `mcp.firecrawl` (`~/.config/opencode/opencode.jsonc`) явно обнулены `HTTP(S)_PROXY`/`ALL_PROXY` (плюс lowercase) и `NO_PROXY=*`. Проверка после перезагрузки конфига: MCP-вызов `firecrawl_credit_usage` → **200/1506 кредитов**, и независимый пробник `python3 tools/firecrawl/probe_mcp.py --tool firecrawl_credit_usage --json` → `{"ok": true, "server": {"name": "firecrawl-fastmcp", "version": "3.40.0"}}`, exit 0. Пробник оставлен в репо как регресс-проверка канала (`--keep-proxy` воспроизводит 407).
- [ ] **FCW-3.** (опция) Self-host на VPS `217.149.23.113` через docker compose → `FIRECRAWL_API_URL` на свой инстанс. Блокер: docker нет ни на VPS, ни локально.
- [ ] **FCW-5.** (гигиена, не срочно) В `~/.zshrc` лежат `export ALL_PROXY=http://...:64468` и источник `~/.proxy_funcs.sh` — порт мёртв, любая программа, которая наследует env, получает 407/000. Действие Игоря: либо поднять прокси, либо вычистить эти export'ы; в `ADR-002` зафиксировать, что прокси включается точечно, а не глобально.

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
- [ ] **ATP-R2 (от Игоря, блокирует Фазу 0):** доступы — подтверждение домена в
  Вебмастере и GSC, API мониторинга uptime, вход в DNS. Счётчик Метрики ✅
  заведён 02.11 (114006019, 4 цели) — этот пункт закрыт. Без остальных Фаза 0
  (0.2–0.4) не сдвинется.
- [ ] **ATP-R3:** Фаза 0, задачи 0.2–0.4 — Вебмастер+GSC, uptime-алерт в
  Telegram, сквозной тест заявки. **0.1 (Метрика) ✅ Verified 02.11** — визит и
  цели `chat_open`/`phone_click`/`scroll_75` доходят до счётчика (см.
  `projects/ai-marketing/docs/adr/ADR-004-analytics-goals.md`). **0.2 домены ✅
  02.11**: Вебмастер `VERIFIED` (мета-тег в `Base.astro`), GSC `Ownership
  verified` (`public/google21afb67cb52a9da8.html` + rewrite в `_redirects`).
  Гейт 0: заявка в Telegram + визит в Метрике + сработавший алерт.
- [ ] **ATP-R10 (от Игоря, напомнить 03.11.2026): отправить `sitemap.xml` в
  поисковики.** 02.11 Google Search Console временно не принимал карту —
  отвечал «попробуйте позже» (лимит отправок на новый ресурс). Нажать, когда
  отпустит: **GSC** <https://search.google.com/search-console> → «Файлы
  Sitemap» → вписать `sitemap.xml` → «Отправить»; **Вебмастер**
  <https://webmaster.yandex.ru/sites/> → `ai-traffic-pro.ru` → «Индексирование»
  → «Файлы Sitemap» → `https://ai-traffic-pro.ru/sitemap.xml` → «Добавить».
  Файл уже отдаётся (HTTP 200, 3365 байт) и объявлен в `robots.txt`, поэтому
  поисковики его всё равно увидят — задача на ускорение, не блокирующая.
- [ ] **ATP-R4:** Фаза 1 — 404-страница, favicon в `public/`, og:image +
  twitter:image (1200×630), title ≤60, `lastmod` по факту, 1 хоп редиректа,
  решение по security-заголовкам (Cloudflare или VPS — Pages не умеет `_headers`).
- [ ] **ATP-R5:** Фаза 2 — семантика по 7 услугам (сейчас 727–809 слов против
  1200), вилки цен, кейсы, блог 6–8 статей, FAQ 8→15+, закрыть разрыв
  «`CONTENT_SPEC.md` ↔ `src/data/site.ts`».
- [ ] **ATP-R6:** Фаза 3 — наполнить `llms.txt` фактами (сейчас 101 строка, без
  FAQ/цен/сроков), NAP-консистентность, ≥10 цитируемых фактов, мониторинг
  AI-ответов (10 контрольных запросов).
- [x] **ATP-R7 (Verified 02.11): сводки по аналитике в Telegram раз в 3 дня,
  без VPS и без веб-дашборда.** Репозиторий `Erik03132/ai-traffic-dashboard`
  (приватный): `collector.py` (только stdlib) + GitHub Actions cron
  `0 6 */3 * *`. Отправляет заходы, посетителей, 4 цели, конверсию, источники,
  позиции по фразам. Бот — HERMES-1 (токен профиля `chief`), чат 176203333.
  История: `data/daily/<день>.json` (один файл = один день, складывается в
  отчёт) + `data/runs/<дата>.json` (журнал). Отчёт за период:
  `python3 collector.py --days 30 --report` — считает скрипт, агент только
  пересказывает. Проверено: запуск в облаке success, сводка дошла в Telegram,
  дневной срез закоммичен. Детали — `ai-traffic-dashboard/README.md`.
  **Дополнено 02.11 (Verified):** блок «переходы из ИИ-ассистентов» — разбор
  рефереров Метрики (ChatGPT не ставит UTM, его переходы выглядят как прямые).
  Распознаются ChatGPT, Perplexity, Copilot, Gemini, Claude, Grok, DeepSeek,
  Mistral, Poe, You.com, Meta AI, Алиса, Яндекс Нейро. Блок появляется только
  при ненулевых переходах, по дням пишется в `data/daily` (поле `ai`).
  12 тестов (`tests/test_ai_referers.py`), в CI шаг с тестами до отправки.
- [ ] **ATP-R11 (решение Игоря): измерение ИИ-видимости — попали ли мы в
  ответы ИИ по контрольным фразам.** Готовые SaaS (Profound, Otterly, Peec,
  AthenaHQ, LLM Sleuth, Semrush/Ahrefs AI, в РФ «Шпиониро») стоят десятки–сотни
  долларов в месяц и почти не дают API — их цифры не попадут в наш JSON-архив,
  тренд не сложится. Свой вариант: 10 фраз через Perplexity API (Sonar Chat
  Completions закрыт 07.2026, теперь Agent API; `citations` → `annotations`;
  Search API ~$1/1000) ≈ $0.1–0.5/мес. **Включать не раньше, чем будет
  20–30 заходов в день** — на 2 визитах это измерение шума (проверено 02.11:
  за всю историю счётчика 3 визита, все прямые).

## 📌 ATP-G — GEO-факторы в ответах нейросетей (разбор статьи 03.11.2026)

> Источник: https://habr.com/ru/articles/1098416/ (Ja-gagarin, 23.10.2026,
> «GEO-факторы ранжирования в ответах нейросетей», 5.4K прочтений).
> Автор сам оговаривает: таблица приоритетов — его экспертная оценка, а не
> опубликованные данные алгоритмов.
>
> **Верификация 03.11.2026:**
> - `arXiv:2610.15033` (Chen, Koudas, 10.10.2026, Information Retrieval) —
>   **подтверждено**: 158 099 ответов, 468 037 цитат; внутренняя выдача самого
>   нейродвижка объясняет **32%** дисперсии цитируемости, свойства страницы —
>   **2.8%**. «Каждая страница, которую цитирует ChatGPT, — та, что нашёл его
>   собственный поиск». FAQ-блоки, schema, скорость и summary-боксы дают эффект
>   только **между сайтами**, внутри одного сайта прироста нет.
> - AirOps «The Fan-Out Effect» — **не проверено** (страница не ответила).
> - Цифры Ahrefs из статьи (37.9% в топ-10, корреляция упоминаний 0.66–0.71) —
>   **не проверено**.
>
> **Вердикт: проверено src → принято частично.** Что меняем в планах:
> доказуемый рычаг — совпадение заголовков и абзацев с формулировками вопросов,
> а не микроразметка и `llms.txt`.

- [x] **ATP-G1 (Verified 03.11): переписать `title`/H1/первые абзацы 7 услуг
  под формулировки вопросов из `docs/semantics/semantics.json`.** Критерий
  приёмки: заголовок и первый абзац услуги дословно-по-смыслу совпадают с ≥5
  фразами своего кластера (проверяемо скриптом, не на глаз). Это выполнение
  части ATP-R5, но с измеримым условием вместо «написать 1200 слов».
  **Инструмент замера:** `tools/geo_match.py` (читает собранный `dist/`, а не
  исходник; считает дословные и по-словесные совпадения с учётом окончаний,
  отдельно — по фразам с данными о спросе).
  **Итог по всем 7 страницам (было → стало, фразы с данными о спросе):**
  `seo` 0/17 → **9/17** (48/278) · `crm` 0/25 → **10/25** (13/88) ·
  `leadgen` 1/28 → **8/28** (21/269) · `ecommerce` 1/19 → **6/19** (11/131) ·
  `smm` 1/17 → **6/17** (11/127) · `advertising` 0/18 → **9/18** (24/198) ·
  `landing` 2/21 → **9/21** (24/227). Порог ≥5 выполнен на всех 7.
  Длины `title`: 51–60 символов. `npm run build` 21 страница, `npm test`
  зелёный (9 файлов). Изменены `src/data/services/*.ts`:
  seoTitle/h1/subtitle/seoDescription у seo, crm, leadgen, ecommerce, smm,
  advertising, landing.
  **`marketplace` из плана исключён:** страницы нет, `/services/marketplace/` —
  noindex-заглушка с редиректом на `/services/ecommerce/` (слияние 28.10.2026).
  Корни маркетплейсов остались в кластере ecommerce и покрываются его страницей.
- [x] **ATP-G7 (Verified 03.11): карта распределения фраз.**
  `tools/page_map.py` → `docs/semantics/page-map.json`. 114 корней разложены
  по 7 страницам, 155 информационных тем отданы блогу. Проверка коллизий есть
  в скрипте и **доказана** синтетическим повтором (детектор поймал). В реальных
  данных повторов корней между кластерами нет — значит коллизий не было изначально,
  а `OVERRIDES` в скрипте это осознанный перенос по интенту, не разрешение спора.
  Распределение спроса (hh.ru, вакансии): crm 128 099 · leadgen 88 505 ·
  ecommerce 74 010 · smm 22 522 · landing 16 757 · advertising 13 599 · seo 12 983.
  **Исправление 03.11:** страница `marketplace` в карте была ошибочно отдельной.
  Её нет с 28.10.2026 — адрес отдаёт noindex-редирект на `ecommerce`, поэтому в
  скрипте добавлен `MERGED_INTO`, а 18 маркетплейс-корней вернулись в `ecommerce`
  (30 корней). Оптимизировать редирект-заглушку бессмысленно.
- [ ] **ATP-G8 (рынок РФ, 26.11.2026): замер эффекта правок через 3–4 недели по
      русскоязычным запросам.** РФ — это **рынок и язык**, а не «только Яндекс»:
      аудитория ищет также в Google, Perplexity, Gemini и ChatGPT. Задача замеров —
      чтобы эти системы находили и цитировали **русскоязычные ресурсы**. Движки:
      Яндекс (Вебмастер, поиск, нейроответы), Google RU (GSC по RU-запросам),
      Perplexity / Gemini / ChatGPT с русскими формулировками. Метрики в Метрике —
      по RU-трафику; показы/клики по фразам из title/H1, средняя позиция, число
      страниц в индексе. Сравнивать с базовой линией 22.11 и с 03.11 на RU-выборке.
      Замер от 24.11 (`gpt-5-mini`) — архив одного канала; эгресс тогда был NL.
      Для Perplexity/Gemini/OpenAI доступ нужен через прокси по ADR-002: помечать
      «RU-запрос, эгресс зарубежный», не выдавать за «замер из РФ».
- [x] **ATP-G9 (РФ-базовая линия).** ✅ **Verified (26.11.2026):** снят первый РФ-срез
      из РФ-эгресса (95.154.153.47): Яндекс.Поиск `lr=213`, 5 формулировок ×1 прогон,
      плюс Вебмастер за 22.10–22.11. Брендовый запрос уже показывает `ai-traffic-pro.ru`
      (в архивном зарубежном замере было 0 цитирований); по остальным четырём нас нет,
      доминируют RU-площадки; lookalike-домены сохраняются. Вебмастер: 2 показа, 0 кликов;
      API-токен без scope `COMMON` дал 403, цифры сняты из живого интерфейса. Сырые данные —
      `docs/seo/raw/2026-11-26/yandex-rf-baseline.md`, хаб обновлён (замер №4). Ограничения:
      1 прогон вместо 3, текст «Быстрого ответа ИИ» не сохранён, регион в Вебмастере
      `ALL_LOCATIONS_ORGANIC`. ATP-G8 остаётся как повтор через 3–4 недели.
- [x] **ATP-G10.** ✅ **Verified (26.11.2026):** Игорь отключил US-прокси/VPN;
      `ipinfo.io` (прямой и с env) → **95.154.153.47, Воскресенск, Московская область,
      RU, AS43714**. Это новая базовая линия эгресса для всех РФ-замеров и мониторинга.
      Прежний NL-адрес (104.238.31.146) остался только в архивной строке замера
      24.11. Замеры через прокси для Perplexity/Gemini/OpenAI помечаем отдельно
      «RU-запрос / зарубежный эгресс».
- [ ] **ATP-G2 (пересмотр приоритета): `llms.txt` — гигиена, не рычаг.**
  Доказательств влияния нет ни в статье, ни в arXiv-работе. В ATP-R6 оставить
  как бытовую задачу, бюджет не выделять. Аналогично `FAQ 8→15+` и schema.org:
  перевести из «высокого GEO-приоритета» в «после контента».
- [ ] **ATP-G3 (уточнение ATP-R11): мерить две разные вещи, не одну.**
  (а) **цитируемость** — наш домен в источниках ответа (рычаг: попасть в поиск
  нейродвижка, то есть обычная SEO-выдача), (б) **знание бренда** — модель
  называет компанию без цитаты (рычаг: внешние упоминания). Набор вопросов —
  стабильный, 15 коммерческих формулировок, а не «10 ВЧ».
- [ ] **ATP-G4 (рынок РФ): внешние упоминания бренда** — модель вписывает в
  запрос бренды, которые уже знает. Нужны упоминания **русскоязычных ресурсов**,
  которые цитируют Яндекс, Google RU, Perplexity, Gemini и ChatGPT: российские
  каталоги, отраслевые площадки, отзывы, профили с NAP. Площадку оцениваем по тому,
  даёт ли она русскоязычный факт для цитаты, а не по «российская/зарубежная».
  Дешёвый и недооценённый рычаг.
- [ ] **ATP-G5 (ограничение метрики, не задача):** клики из AI Overviews и
  нейроответов Яндекса в Метрике приходят как **обычный поисковый трафик** —
  наш блок «ИИ-переходы» видит только чат-интерфейсы. Разделить нельзя, пока
  поисковики сами не разметят. Учитывать при чтении отчётов.
- [x] **ATP-G6 (проверено 03.11): доступ для AI-ботов открыт.** `robots.txt`
  на ai-traffic-pro.ru: `User-agent: * / Allow: /`, отдельных запретов для
  GPTBot, PerplexityBot, ClaudeBot, Google-Extended, YandexAdditional нет.
  Действий не требуется. Побочное наблюдение: `/privacy/` и `/consent/`
  закрыты от индексации — для сайта, собирающего персональные данные, это
  спорно (страница политики обычно должна индексироваться). Решить отдельно.
- [ ] **ATP-R8:** после закрытия Фазы 0 отозвать временные доступы: удалить
  OAuth-приложение `opencode-metrika` в Яндексе, отозвать Cloudflare-токен
  (`~/.config/opencode/secrets/cloudflare.token` больше не нужен).
- [ ] **ATP-R9 (ожидание, не дефект):** Вебмастер отдаёт `HOST_NOT_LOADED` на
  «Поисковые запросы» — Яндекс ещё не загрузил хост `https:ai-traffic-pro.ru:443`
  (добавлен 02.11). Через 1–2 суток проверить: `collector.py --days 7 --dry-run`,
  в блоке «Видимость» должны появиться фразы. Пустая таблица у нового сайта —
  норма 2–3 недели.

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

- [x] **LEAD-001** — ✅ **Fixed + Verified (17.11.2026).** Скилл `skills/lead-copilot/SKILL.md` (вход-карточка, 5 сигналов с весами 30/20/20/15/15, полосы P0≥75 / P1≥50 / P2<50, шаблоны ответа, границы), детерминированный скоринг `tools/lead_score.py` (stdlib, CLI по CP-1: `--input/--weights/--json/--out/--as-of/--dry-run/--help`, ошибки → stderr + код 2, леджер JSONL идемпотентен), eval `tools/tests/eval_lead_score.py` (TP-1…TP-14). Строка в `skills/skill-router.md` для обнаруживаемости. Доказательства: eval → **PASSED** exit 0; `ruff check` → All checks passed; P0-карточка → **100/100 P0**; P2-карточка → **15/100 P2** `missing: [budget]`; пустой вход и битый JSON → **exit 2**; два прогона `--out` → **1 строка** (идемпотентно). Пороги помечены в коде/JSON/SKILL.md как `placeholder: LEAD-002 PENDING`.
- [ ] **LEAD-002** — Апрув порогов lead-score thresholds от Игоря (P0/P1/P2 по баллам) — **сейчас placeholder 75/50**, меняются через `--weights` без правки кода. Блокирует содержательные решения по лидам.
- [ ] **LEAD-003** — Настройка мониторинга сигналов (TG-поиск руками + классификация агентом) — без юзерботов
- [ ] **LEAD-004** — Юридическая проверка ПД (152-ФЗ, 38-ФЗ ст.18) через Фемиду перед любыми email-действиями
- [x] **LEAD-005** — ✅ закрыт вместе с UXT-1/UXT-2 (25.11.2026): 4 персоны-субагента, отчёт до/после, 16 скриншотов — `qa/first-users/REPORT.md`.

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

## 🎨 HMK — Hallmark: anti-slop дизайн-скилл + sloplint (разбор 16.11.2026)

**Статус: ПОТЕНЦИАЛЬНАЯ ЗАДАЧА — оценка сделана, интеграция не начата (0 из 5).**
Проверено на нашем коде (Verified, 16.11.2026), но ни одна правка ещё не внесена.

> **Источник:** `github.com/Nutlope/hallmark` (от Together AI), прислал Игорь.
> **Верификация (правило 13, проверено src):** GitHub API — MIT, 55 902 ★, 3 008 форков,
> push 11.11.2026 (живой), не архивный. `install.mjs` официально поддерживает
> `--claude / --codex / --cursor / --opencode` — OpenCode в списке, Hermes НЕТ.
> Локальная копия `~/.config/opencode/skills/hallmark` = v2.0.0, `SKILL.md` побайтово
> совпадает с `main`, 102 файла тем (50 тем) — **актуально, обновлять нечего.**

> **Что уже есть в стеке (не дублировать!):** скилл `hallmark` v2.0.0 в L0 OpenCode
> (6.9 МБ, SKILL.md 18 КБ ≈ 4.5k токенов); кластер ADM (Рембрандт +
> `popular-web-designs` + `design-bridge` + `design-md`); `hermes-skills-sync/`
> (канонический репо скиллов + symlink в профили Hermes + `~/.hermes/skills/load_skill.py`
> по `skills_index.json` / `skills_tag_index.json`, 180 скиллов).
> Hallmark ≠ замена ADM: DESIGN.md описывает токены, Hallmark строит страницу и линтит.

> **Проверка на нашем коде (Verified):** `node scripts/sloplint.mjs ai-bureau-site/concept/index.html`
> → **floor FAIL 108, reflex 47, warns 8**. Полезное: `pure #fff` в `.btn-accent`,
> 2× `<svg>` без `aria-hidden/aria-label`, нет focus-стилей. Шум: гейт 20 требует
> «Hallmark stamp» в первой строке CSS (на легаси всегда FAIL), гейт 19 — запрет
> длинного тире (вкусовщина). **Не проверено:** render-режим (`--render` / `--url`,
> скриншоты, проверка «hero попадает в экран») — требует Chrome под CDP.

- [ ] **HMK-001** — Порт Hallmark в Hermes через `hermes-skills-sync/`: каталог в
  `skills/hallmark/` → frontmatter `metadata.hermes.tags: [design, ui, frontend,
  landing, anti-slop, sloplint]` + `related_skills: [design-md, popular-web-designs,
  claude-design]` → перегенерить `skills_index.json` + `skills_tag_index.json` →
  symlink в профиль. **On-demand по тегу `design`, НЕ в автозагрузку** (4.5k токенов
  не должны висеть в контексте постоянно). Оценка: 20-30 мин, риск низкий (sloplint на
  node, к рантайму Hermes не привязан).
- [x] **HMK-002** — Baseline-замер: прогнать sloplint (`--tier floor --json`) по 3 нашим
  фронтам. ✅ **16.11.2026, Verified** (`node scripts/sloplint.mjs <dir> --tier floor --json`).
  Вкусовые гейты (`54` eyebrow, `67` tracked-caps, `63` middle-dot, `19` тире, `20` stamp)
  исключены из подсчёта — на легаси-дизайне это шум:

  | Проект | floor FAIL | файлов | реальных | вкусовых | главные реальные гейты |
  |---|---|---|---|---|---|
  | `ai-bureau-site` | **256** | 62 | 149 | 107 | `48`×129 (hex/шрифты вместо токенов), `10a`×8 (`transition-all`), `39a`×4 (focus через border), `33`×3 (svg без aria), `34`×3 (нет `overflow-x: clip`), `7a`×2 (pure `#fff`) |
  | `dashboard` | **4** | 4 | 4 | 0 | `26a`×2 (нет `:focus-visible`), `30a`×1 (эмодзи в `<h1>`), `34`×1 |
  | `projects/affiliate-landing` | **40** | 1 | 28 | 12 | `48`×18 (литералы шрифтов/цветов), `30a`×4 (эмодзи-иконки), `7a`×3 (pure `#fff`), `26a`×1, `34`×1, `62`×1 (`.reveal` скрыт без JS) |

  Вывод: `dashboard` почти чист (4 находки — дешёвый фикс), `ai-bureau-site` — основной
  должник, и 129 из 149 реальных находок там — **дисциплина токенов** (`48`), а не вёрстка.
- [x] **HMK-003** — sloplint как механический гейт. ✅ **16.11.2026, Fixed+Verified**:
  шаг 4 добавлен в команду `/code-review` (`~/.config/opencode/AGENTS.md`): команда запуска,
  список **блокирующих** гейтов (`7a`, `10a`, `26a`, `39a`, `33`, `34`, `62`, `30a`, `48`)
  и явно **не блокирующих** вкусовых (`54`, `67`, `63`, `19`, `20`), плюс требование
  сравнивать с baseline HMK-002, а не с нулём. Сделано именно advisory-шагом, а не
  блокирующим pre-commit: на `ai-bureau-site` 149 реальных находок — блокировка парализовала
  бы коммиты. Проверено: шаг присутствует в файле, нумерация 1-6 целая.
- [ ] **HMK-004** — Правило для новых страниц: `DESIGN.md` (ADM-002) задаёт токены +
  Hallmark задаёт направление из 50 тем → 3 темы на выбор, а не «фиолетово-синий
  градиент». Зафиксировать в `skills/agents/rembrandt/SKILL.md` связку ADM ↔ HMK.
- [ ] **HMK-005** — Темы Hallmark = чужой бренд. Для клиентских проектов тема
  подменяется на brand tokens из DESIGN.md, иначе получим «красиво, но не их».
  Проверить на одном реальном клиентском лендинге.

**Ограничения (зафиксировать, чтобы не переоткрывать):** скилл применяется только к
НОВЫМ страницам (на существующий дизайн — лишь по явному `/hallmark redesign <path>`);
50 тем — материал, а не наш бренд; гейты 19/20 на легаси дают шум.

**Что нужно от Игоря:** одно решение — делать HMK-001 (порт в Hermes) или ограничиться
HMK-003 (только sloplint в CI OpenCode). Плюс назвать первый лендинг для HMK-002.

## 🐘 EGM — Elephant-Goldfish Model: решение «не делать» (разбор 16.11.2026) ⏸ ОТКЛОНЕНО

**Статус: ОТКЛОНЕНО Игорем 16.11.2026 — вариант C, ничего не делаем.**
Секция оставлена, чтобы не переоткрывать задачу заново. Реализация не начиналась,
ни один файл не изменён.

> **Источник:** `github.com/google/elephant-goldfish-model` (прислал Игорь).
> **Верификация (правило 13, проверено src):** Apache-2.0, 20 182 ★, 1 495 форков,
> создан 13.09.2026, push 15.11.2026, не архивный. 7 скиллов
> (`egm-brainstorm`, `egm-draft`, `egm-review`, `egm-review-loop`, `egm-resolve`,
> `egm-bootstrap`, `egm-drift-report`), 10 промптов-ревьюеров,
> `resources/document_standards`, официальный адаптер `adapters/opencode/install.py`
> (`HOST_VERSION = "1.18.29"`, помечен experimental / «OpenCode V1 bundle»).
> У нас `opencode --version` = 1.19.0 — совместимость адаптера НЕ проверялась.

**Почему отклонено (три факта, не мнение):**

1. **Уже портировано и не использовано.** `~/.config/opencode/skills/egm-review/`
   (commit `b7d9e27`, 09.11.2026) — `skills_audit.py --dry-run` даёт
   **0 вызовов**. Второй скилл с нулём вызовов не нужен.
2. **В порте отрезана половина ценности.** Строка 110 нашего `SKILL.md` прямо
   перечисляет выброшенное: `egm-draft` («дублирует `writing-plans`»),
   `egm-brainstorm` («дублирует `brainstorming`»), `egm-bootstrap`, `install.py`.
   Осталась «рыбка без слона» — ревью документа, который не писали как спеку.
   Отсюда и 0 вызовов.
3. **Дорого.** `full` = 8 субагентов, 150-220k токенов; `standard` = 5, 80-120k
   (цифры из нашего же порта). Самая дорогая операция в стеке при бюджете $15-20/мес.

**Триггер переоткрытия (только при выполнении любого):**

- появится устойчивый поток **≥2 спек в месяц** (тогда вариант B: официальный бандл
  в `~/freelance-2026/tools/egm-bundle/`, глобальный конфиг не трогаем, проверить на 1.19.0);
- понадобится вариант A (доукомплектовать наш порт `egm-draft` + `egm-review-loop`
  + `egm-resolve`, ~1 час);
- понадобится Hermes-порт — отдельная задача: вся модель держится на субагентах
  со свежим контекстом, есть ли у Hermes эквивалент `subagent` — **не проверено**.

**Не переоткрывать без триггера.** При обновлении когда-нибудь учесть: upstream
`#439 Fix bare-mention neutralization bypass via stray fence backtick` (15.11.2026)
вышел ПОСЛЕ нашего порта — при возврате к теме перепроверить нейтрализацию упоминаний.

## ☎️ VSIP — OpenAI Voice SIP: телефония напрямую в GPT-Live (разбор 16.11.2026) ⏸ ОТЛОЖЕНО

**Статус: ИЗУЧЕНО, ОТЛОЖЕНО (16.11.2026). Код не менялся, к Levitan не применяем.**
Причина — не «не понравилось», а три блокера, которые не решаются кодом (см. ниже).
Один бесплатный вывод забираем сразу: паттерн sideband (пункт VSIP-004).

> **Источник:** `developers.openai.com/api/docs/guides/voice-sip` (прислал Игорь).
> **Верификация (проверено по докам, 16.11.2026):** сигналинг SIP over **TLS**, аудио
> **SRTP** (обязательно); входящий звонок — вебхук `live.transport.incoming` + accept/reject;
> SIP URI `sip:$PROJECT_ID@sip.api.openai.com;transport=tls`; исходящий — создать сессию и
> набрать номер через провайдера; управление — **sideband** WebSocket (один обработчик на
> действие, иначе дубли вебхуков исполнят тул дважды). Модель `gpt-live-1`: full-duplex,
> reasoning и тулы **делегирует на бэкенд** (Responses API, биллинг отдельно).
> Цена: **$0.05/мин**, посекундно, без округления (страница `models/gpt-live-1`).

**Что это заменило бы у нас (Levitan/Анжелла):** 6 компонентов — пропатченный `livekit-sip`
(Go, `media_codecs.go`) + `livekit-server` (диспатч-правила, `trunk_ids`) + pipecat-агент +
Yandex SpeechKit TTS + Deepgram STT + Gemini 2.5 Flash, плюс `sip_register.py` с REGISTER
каждые 60с — схлопывается в **один SIP URI + sideband WS**. Исчезает именно наш самый
хрупкий слой: «Appeared→Disconnected мгновенно» из-за протухшей регистрации, обрезанное
приветствие (джиттер PCMA 8k vs 48k), G722 который не отключается через yaml.

**Блокеры (не решаются кодом):**

1. **Mango Office должен уметь направить транк на внешний SIP URI по TLS+SRTP.** Сейчас мы
   абонент `user4` (vpbx400161137), АТС шлёт INVITE нам. Поддержки пиринга на
   `sip.api.openai.com` в нашей базе знаний НЕТ. **НЕ ПРОВЕРЕНО — это вопрос жизни и смерти
   идеи.** Проверка: поддержка Mango или `docs.mango-office.ru`.
2. **OpenAI API недоступен в РФ.** Обходим HTTP-прокси, но SIP через HTTP-прокси не ходит —
   нужен прямой TLS-путь от инфраструктуры Mango до OpenAI (следствие блокера 1).
3. **152-ФЗ.** Голос клиентов-физлиц обрабатывается в США — нарушение локализации ПДн.
   Для клиентских проектов это блокер, не риск. Перед любым использованием — femida.

**Прочие ограничения:** цена ~4-5 ₽/мин только за голос (1500 мин/мес ≈ $75 против нынешних
$20-30); переписывание воронки под delegation-тулы (2-3 дня); трюк «лид-тишина 5с против
обрезанного приветствия» не переносится; совместимость кодека (наш PCMA/PCMU 8 кГц vs
SRTP/G.711) — не проверена.

- [ ] **VSIP-001** — Проверить блокер №1: поддерживает ли Mango Office SIP-транк с
  пирингом/регистрацией на внешний SIP URI по TLS. **Единственное, что решает судьбу идеи.**
  Один запрос в поддержку Mango или чтение `docs.mango-office.ru`.
- [ ] **VSIP-002** — Если Mango подтвердит: юр. заключение по 152-ФЗ (femida) ДО любого
  пилота. Без заключения — не начинать.
- [ ] **VSIP-003** — Если оба зелёные: пилот на 1 номере, 20 звонков, сравнение с текущим
  стеком по трём метрикам — латентность первого ответа, обрезанное приветствие, ₽/мин.
- [ ] **VSIP-004** — **Забрать бесплатно уже сейчас:** паттерн sideband + accept/reject-вебхук
  + правило «один обработчик на действие» применить в текущем livekit-стеке против двойных
  срабатываний тулов. Не зависит ни от одного блокера.
- [ ] **VSIP-005** — Держать как готовый вариант для **иностранного клиента** (Twilio/Vonage
  номер): там нет блокеров 1-3, и это экономит неделю работы против нашего livekit-стека.

**Триггеры переоткрытия:** (а) появился клиент с иностранным номером; (б) Mango подтвердил
SIP-транк на внешний URI + есть заключение по 152-ФЗ; (в) переделка Levitan с нуля.

## 🏠 HOME — The Home Repo Pattern: диагноз нашего «домашнего репо» (разбор 16.11.2026)

**Статус: ЗАПИСАНО, НЕ НАЧАТО (16.11.2026).** Игорь: «только записать», реализацию
не начинал, ни один файл не изменён.

> **Источник:** `aihero.dev/the-home-repo-pattern` (обновлено 12.11.2026).
> **Суть паттерна:** один git-репо держит скиллы + AGENTS.md + общие доки, агент
> запускается из него, а его AGENTS.md содержит указатели на остальные репо
> (remote + команда клона). При ~20 репо указатели группируются по областям.

**Вердикт: паттерн у нас уже реализован на ~80% — принимать как ДИАГНОЗ, не как новый
инструмент.** `~/freelance-2026` и есть home repo (`origin: Erik03132/freelance-2026`),
из него и работаем (cwd сессий). Внутри: `AGENTS.md`, `ACTIVE_TASKS.md`, `docs/adr/`,
`plans/`, `CONTEXT.md` + 4 вложенных репо.

**Что вскрыл диагноз (проверено локально 16.11.2026):**

| Что | Факт | Почему проблема |
|---|---|---|
| Скиллы вне git | `~/.config/opencode/skills` 7.4 МБ (22 папки + 18 симлинков), `skills-lib` 8.1 МБ, `~/.agents/skills` 844 КБ — **ни один не под git** | нет rollback, нет «кто сломал», нет синка на VPS/вторую машину |
| `hermes-skills-sync/skills` пуст | 0 элементов, при этом README называет его «канонический репозиторий — основной источник истины» | **наша дока врёт** (HT-3) |
| 18 симлинков между двумя не-репо | `~/.config/opencode/skills` → `~/.agents/skills` | при переносе машины развалится молча |
| Нет секции «Other Repos» | в `AGENTS.md` есть «Карта проектов» (путь + projectId), но без remote и команд клона | агент не знает, откуда взять отсутствующее репо |
| 6 живых репо вне home repo | `~/hermes-sync`, `~/memento-skills`, `~/new-site`, `~/nextjs-starter`, `~/orca-audit` (+ сам `freelance-2026`) | ровно тот случай, ради которого паттерн написан |

**Не проверено:** есть ли бэкап скиллов в Timeweb S3 (упомянут в S3-блоке `AGENTS.md`).
Если есть — «единственная копия» неверно, формулировку не использовать до проверки.

**Ограничение паттерна для нас:** он про несколько репо одного владельца. У нас 10+ репо,
часть клиентские, часть заброшенные. Тащить все в указатели нельзя — `AGENTS.md` и так
460 строк always-on; указатели только для живых.

- [ ] **HOME-001** — **Git для скиллов (главное).** Предпочтительно: перенести скиллы в
  `freelance-2026/agent-config/skills` + симлинки (home repo остаётся один, как в статье).
  Альтернатива: `git init` в `~/.config/opencode` с `.gitignore` на `node_modules/`,
  `.secrets/`, `*.log`. Перед стартом — прогнать `skills_audit.py --dry-run` и не тащить
  в репо нулевые скиллы.
- [ ] **HOME-002** — **Починить или убрать ложь:** либо заполнить `hermes-skills-sync/skills`
  реальным содержимым, либо переписать README, чтобы не называл пустую папку источником
  истины. Плюс зафиксировать, где канон: `~/.config/opencode/skills` vs `~/.agents/skills`
  vs `skills-lib` — сейчас три места и 18 симлинков без объявленного владельца.
- [ ] **HOME-003** — **Секция «Other Repos» в `AGENTS.md`:** 6 живых репо — remote + одна
  команда клона. Заброшенные не включать. Не раздувать: указатели только для того, что
  реально открывается агентом.
- [ ] **HOME-004** — **Проверить бэкап** скиллов в Timeweb S3 до любых утверждений о
  «единственной копии»; результат зафиксировать здесь же.

**Триггеры переоткрытия:** переезд на новую машину; поломка скилла без возможности отката;
необходимость синка скиллов на VPS; рост числа репо, из-за которого агент перестаёт видеть
нужный проект.

## 🧩 UIS — Vercel UI SDK: поведенческий слой для агентов (разбор 16.11.2026)

**Статус: ЗАПИСАНО, НЕ НАЧАТО (16.11.2026).** Игорь: «записать». Библиотека не
устанавливалась, скиллы не забирались, ни один файл проекта не изменён.

> **Источник:** `github.com/vercel-labs/ui` (прислал Игорь). Apache-2.0, **5 252 ★**,
> 171 форк, создан **26.10.2026**, push 16.11.2026, не архивный. **beta, pre-1.0**
> (`size-budget.json`, changesets) → API будет меняться.
> **Что это:** библиотека ПОВЕДЕНИЙ, не компонентов — клавиатурная навигация, фокус,
> выделение, dismissal, попапы, drag&drop, typeahead + ARIA в `@ui-sdk/core`; адаптеры
> React / Vue / Svelte / Solid / Web Components. Позиционируется как «behaviors for agents»:
> внутрь встроены 4 скилла в `.agents/skills/` + `benchmarks/agent` (замер, как агент строит UI).

**Наш стек (проверено 16.11.2026):** `ai-bureau-site` — React + Tailwind + **Radix**
(`@radix-ui/react-dialog`, `@radix-ui/react-popover`); `projects/sinergy` — Next+React+Tailwind;
`projects/ai-scout` — React+Tailwind; `ai-bureau` — Astro+React; остальные — Astro/статика.

**Вердикт: библиотеку НЕ брать.** Это прямой конкурент Radix, которому три недели от роду
и ни одного продакшн-кейса; у Radix — годы багрепортов по скринридерам. Менять проверенный
a11y-слой на непроверенный в клиентских проектах — плохая сделка. Плюс большинство наших
фронтов — маркетинговые страницы на Astro, где поведенческий слой почти не нужен.

**Ценность — в скиллах и в диагнозе, не в зависимости.**

- [ ] **UIS-001** — Забрать `ui-sdk-unslop` как чеклист в `/code-review` (независимо от
  библиотеки). Бьёт по «сгенерированному виду **кода**»: комментарии, пересказывающие
  следующую строку; JSDoc-филлер на каждой декларации; защитные проверки невозможных
  кейсов; хелперы с одним вызовом; расплывчатые имена. Правило: поведение не меняется,
  тесты проходят до и после. Источник: `.agents/skills/ui-sdk-unslop/SKILL.md`.
- [ ] **UIS-002** — Перенести scaffold-паттерны из `ui-sdk-write-code` в наши промпты:
  (а) **«найди близнеца»** — перед первой строкой открыть существующий файл, который делает
  это хорошо, и копировать его форму/имена/порядок; (б) `experts/<framework>/knowledge.md`
  **привязан к установленной версии** и довереннее памяти модели (у нас болит: React 19 /
  Svelte 5 / Vue 3.5 идиомы); (в) список «что делает код сгенерированным»: одна форма
  (`<Name>` + `<Name><Part>`, никаких `as`), имена полными словами, булевы как вопросы.
- [ ] **UIS-003** — Зафиксировать в дизайн-стеке три зоны ответственности: **токены**
  (ADM: DESIGN.md) → **вид** (HMK: Hallmark) → **поведение** (Radix). Пробел был именно в
  третьей зоне — sloplint на `ai-bureau-site` нашёл `<svg>` без `aria-label` при готовом виде.
- [ ] **UIS-004** — Посмотреть `benchmarks/agent` (методика замера «агент строит UI») —
  может пригодиться для наших eval-наборов по фронтенду. Только изучение, без внедрения.

**Триггеры переоткрытия:** появится проект, где нужен один набор поведений на React +
Svelte + Web Components одновременно; Radix начнёт мешать; UI SDK выйдет из beta с
публичными продакшн-кейсами.

## 💤 CLD — ClamDown: MacBook работает с закрытой крышкой (разбор + тест 16.11.2026) 🔧 В ТЕСТЕ

**Статус: УСТАНОВЛЕНО (Verified 16.11.2026), функциональный тест ждёт закрытия крышки.**
Игорь: «записать и тестировать. Тест сегодня-завтра, когда закрою крышку, поставив задачу
агенту в OpenCode и Hermes».

> **Источник:** `github.com/delef/ClamDown` (прислал Игорь). Apache-2.0, **54 ★**, 2 форка,
> 0 подписчиков, **0 issues за всю историю**, ~317 скачиваний DMG, создан **10.11.2026**
> (6 дней), 70 коммитов за 3 дня, последний 13.11.2026, язык Swift, требует macOS 13+.
> **Почему мало откликов:** проект просто молодой, а не заброшенный — и качество инженерии
> выше среднего для 54 звёзд (см. проверки ниже).

**Что проверено лично (16.11.2026):**

| Проверка | Результат |
|---|---|
| Нотаризация DMG | `spctl` → `accepted`, `source=Notarized Developer ID` |
| Подпись приложения | `Identifier=app.clamdown`, `TeamIdentifier=RFYMF7Q4UK`, **hardened runtime** (`flags=0x10000 runtime`), Developer ID: Ivan Palamarchuk |
| Хелпер | `app.clamdown.helper` в `Contents/Library/LaunchDaemons`, **fail-closed**: читает свой bundle ID + Team ID из подписи, строит requirement, пиннящий оба; иначе `exit(1)` |
| Инъекция команд | исключена: `PmsetCommand` — закрытый enum, аргументы только `Bool` (`disablesleep 0\|1`, `-b lowpowermode 0\|1`, `sleepnow`) |
| Восстановление | SIGTERM/SIGINT → вернуть настройку; `recoverOnStart()` до любых exit-путей (покрывает SIGKILL); обрыв XPC → `core.disable()` |
| Вентиляторы | `FanCurve` = `min + fraction×(max−min)`, fraction ∈ [0,1] — выйти за паспортные обороты нельзя по построению |
| Тесты | по модулям (`SharedTests`, `AppKitTests`, `HelperKitTests`) + CI `swift build && swift test` + e2e `unauthorized-client.swift` (проверка отказа неавторизованному) |
| Зависимости | одна, закреплена точно: Sparkle `exact: 2.10.1`. Телеметрии в коде нет, сеть — только appcast с GitHub |
| Локальный статус | `/Applications/ClamDown.app`, процесс жив, `launchctl print system/app.clamdown.helper` → `active count = 2`, `SleepDisabled` был 0 — режим не взведён (на 23:30 взведён Игорем, `SleepDisabled = 1`) |

**Риски (не сняты):** управление вентиляторами через SMC на Apple Silicon ломается при
обновлениях macOS; bus factor = 1; ноль сторонних подтверждений «работает»; ноутбук в сумке
под нагрузкой = нагрев и деградация батареи (их cutoffs — единственная защита, нами не
проверена); наша macOS 26.5.2 автором не заявлена (он тестировал на 13+).

**Что это закрывает у нас:** `caffeinate` **не спасает от закрытой крышки**, а `pmset`
показывает, что сон сейчас подавлен случайными аудио-ассертами (`coreaudiod`, `bluetoothd`),
а не нашим решением. Уникальность ClamDown не в «не спать» (это одна команда
`sudo pmset disablesleep 1`), а в **кривой вентиляторов + отсечках по заряду и теплу +
автовосстановлении + блокировке экрана** — то есть в защите от того, чтобы сжечь ноутбук
в сумке, как только начинаешь пользоваться этой командой.

**Инструмент теста:** `~/.config/opencode/tools/ops/clamdown_probe.sh` (read-only снимок:
приложение, хелпер, `disablesleep`, батарея, thermal, крышка, ассерты, PID агентов, нагрузка).
Лог: `~/.config/opencode/logs/clamdown_test.log`.

- [x] **CLD-001** — Установка + проверка подписи. ✅ 16.11.2026: DMG нотаризован, приложение
  скопировано в `/Applications`, запущено, хелпер зарегистрирован (`active count = 2`).
  **Verified:** `spctl`, `codesign`, `launchctl print`.
- [ ] **CLD-002** — **Функциональный тест (сегодня-завтра):**
  1. В приложении взвести режим (menu bar → включить), проверить `pmset -g | grep SleepDisabled` → `SleepDisabled 1`.
  2. `bash ~/.config/opencode/tools/ops/clamdown_probe.sh before --note "OpenCode + Hermes"`
     — до закрытия, когда задачи уже запущены.
  3. Запустить длинную задачу в **OpenCode** и в **Hermes**, дождаться первых шагов.
  4. Закрыть крышку, оставить на **20-30 минут** (первые прогоны — не на часы).
  5. Открыть крышку → `... clamdown_probe.sh after --note "после крышки"`.
  **Критерии PASS:** (а) `SleepDisabled 1` во время и `0` после выключения режима (проверять через `pmset -g`, НЕ `pmset -g custom` — там этого поля нет);
  (б) оба агента живы, их логи/таймстемпы продвинулись за время с закрытой крышкой;
  (в) экран был заблокирован при закрытии; (г) батарея не ниже отсечки, thermal-лимит не
  прибит к 100% надолго; (д) после выключения режима вентиляторы не залипли на max/min.
- [ ] **CLD-003** — Проверка восстановления: `kill -9` приложения при взведённом режиме →
  перезапуск → `SleepDisabled` вернулся в 0 (иначе `recoverOnStart` не работает на 26.5.2).
- [ ] **CLD-004** — Решение по итогам теста: оставить как рабочий инструмент или снести.
  **Снести:** quit → System Settings → Login Items → убрать `app.clamdown.helper` →
  `rm -rf /Applications/ClamDown.app /var/db/clamdown` → `defaults delete app.clamdown`.

**Правила безопасности (до снятия рисков):** первые две недели не оставлять в сумке без
присмотра; всегда ставить таймер авто-отключения; фолбэк держать в голове —
`sudo pmset disablesleep 0` и `caffeinate -d`.

**Триггеры переоткрытия/пересмотра:** обновление macOS (проверить SMC и `disablesleep`);
появление issues с жалобами на вентиляторы; отказ автора от проекта.

## 🔁 RSI — самоулучшающийся цикл агентов: пять правил и наши пробелы (разбор 16.11.2026)

**Статус: ЗАПИСАНО, НЕ НАЧАТО (16.11.2026).** Игорь: «записать». Ни один файл правил
не менялся; приоритет — **RSI-002 (сейф)**.

> **Источник:** YouTube «Как я научил своих AI-агентов улучшать себя каждый день»
> (Мысли Рвачева, Lecture Club, 10.11.2026, **81 мин**, 16 871 просмотр).
> Слайды: `crm.rvachev.org/uploads/rsi-agents-slides.pdf` — 31 страница, **картинками,
> текстового слоя нет**.
> **Честно: транскрипт не читал.** Оценка по описанию, таймкодам и проверке названных
> артефактов, а не по аргументации автора.

**Содержание по таймкодам:** живой эксперимент (агент учится писать холодные письма, видя
только «ответили/нет») → из чего состоит агент → RSI и autoresearch → Darwin Gödel Machine
(«лучшее иногда вырастает из плохой ветки») → закон Гудхарта + случай Hugging Face →
свой эксперимент (Claude Code двое суток улучшал антиспам для 57 Telegram-чатов) →
**пять правил цикла** → Q&A.

**Пять правил (дословно):** одна метрика · сейф для проверки · маленькие шаги ·
журнал попыток · бюджет.

**Проверка названного (правило 13):**

| Утверждение | Проверка |
|---|---|
| autoresearch Карпаты, 700 экспериментов за 2 дня | ✅ `karpathy/autoresearch` — **★100 134**, push 26.03.2026, «AI agents running research on single-GPU nanochat training automatically» |
| Darwin Gödel Machine | ✅ `jennyzzt/dgm` — «Open-Ended Evolution of Self-Improving Agents», активен 16.11.2026 + 3 независимых реимплементации |
| Случай Hugging Face (обман проверки) | ⚠️ не проверял, принимаю как иллюстрацию Гудхарта |
| Антиспам 57 чатов, холодные письма | ⚠️ не проверял — личный опыт автора, публичных артефактов нет |

**Наш стек — что уже есть (проверено 16.11.2026):** правило «улучшаем только scaffold»
(ADR-001, `AGENTS.md` п.10); `self_improve_log.md` — 7 записей в формате «сигнал →
update target → изменение → результат»; **36 файлов `eval_*.py`** + `tools/eval_gate.sh`;
claude-mem для решений. Концепцию мы приняли раньше — видео её не открывает.

**Где разрыв — по пяти правилам:**

| Правило | У нас | Вердикт |
|---|---|---|
| Одна метрика | 36 eval-файлов, но это набор pass/fail, а не один счёт на прогон | ❌ нет |
| **Сейф для проверки (holdout)** | нет: **агент сам пишет eval и сам по нему проверяется** | ❌ **самый опасный пробел** |
| Маленькие шаги | правило scaffold-апдейтов | ✅ есть |
| Журнал попыток | нарративный лог есть, таблицы «изменение → метрика → keep/discard» нет | 🟡 половина |
| Бюджет | месячный лимит $15-20 есть, лимита на цикл нет | 🟡 половина |

- [ ] **RSI-001** — Одна метрика на агента: числовой счёт за прогон для 2-3 агентов
  (кандидаты: доля откликов Батрака, принятых без правок; pass-rate eval Кулибина).
  Без метрики остальные четыре правила не имеют смысла.
- [x] **RSI-002** — **Сейф (приоритет).** Разделить eval на `visible/` и `holdout/`;
  holdout агенту не показывать, прогонять только на приёмке. Причина: у нас агент пишет
  тест и сам его проходит — классическая петля Гудхарта. Ни в одном из 36 файлов
  разделения нет.
  **✅ 17.11.2026 — Fixed + Verified.**
  - `tools/rag_evalset.py`: `SPLITS = {"visible","holdout"}`, поле `EvalCase.split`
    (дефолт `visible`), разбор в `from_dict`, проверки в `validate_case` (значение вне
    списка; `holdout` без `reviewed_by`), `load_eval_set(path, split=None)` + хелперы
    `load_visible` / `load_holdout`.
  - `tools/holdout_gate.py` — новый гейт: ищет `*/tests/holdout/*.jsonl`, ловит утечку
    visible-кейсов в закрытый файл, проверяет `reviewed_by`, `--min`, `--dry-run`,
    `--help`. **Пустой сейф = exit 1 с громкой причиной**, не «зелёно».
  - `tools/eval_gate.sh --holdout` — режим прогона сейфа через общий гейт.
  - `tools/tests/holdout/` — `README.md` (правила, формат, как наполнять, ротация) +
    `_example.jsonl.template` (намеренно не `.jsonl`, чтобы не попал в гейт до
    заполнения `reviewed_by`).
  - `~/.config/opencode/AGENTS.md` — правило **20** (агент не читает holdout и не правит
    `expected_*`; прогон только на приёмке) + строка в таблице автодействий.
  - **Verified:** `python3 tools/tests/eval_rag_evalset.py` → PASSED (TP-1..TP-7,
    включая split-фильтр, невалидный split, holdout без `reviewed_by`, легальный holdout);
    регрессий нет — `eval_rag_evalrunner.py` и `eval_rag_retrieval.py` тоже PASSED;
    гейт проверен на 4 путях: валидный сейф → exit 0, без `reviewed_by` → exit 1,
    утечка visible в holdout-файл → exit 1, `--min 5` при 1 кейсе → exit 1;
    на реальном репозитории сейчас **exit 1 «сейф пуст»** — это честное состояние,
    кейсы пишет человек.
  - **Не сделано (сознательно):** holdout-кейсы не заведены ни для одного агента —
    это работа человека по реальным провалам приёмки (RSI-005, пилот на `agents/batrak`).
- [ ] **RSI-003** — Журнал попыток: таблица `дата | изменение | метрика до | метрика после |
  keep/discard` рядом с `self_improve_log.md`. Нарратив оставить, но решение «оставить/
  откатить» должно опираться на числа.
- [ ] **RSI-004** — Бюджет цикла: лимит токенов/времени на одну итерацию самоулучшения +
  авто-стоп. Месячный лимит $15-20 не защищает от одного дорогого прогона.
- [ ] **RSI-005** — Пилот на одном скилле: `agents/batrak` (там метрика «отклик принят без
  правок» уже почти есть). Прогнать 3-5 итераций по правилам RSI-001..004, зафиксировать
  keep/discard. Только после пилота решать, автоматизировать ли цикл.

**Границы (чтобы не переоценить):** 81 минута вебинара — это оглавление, а не методология;
RSI здесь узкий (метрика → изменение → проверка), а не «самоулучшение интеллекта»; любая
метрика-функция неполна — «ответили/не ответили» геймится короткими провокационными
письмами при нуле сделок, поэтому holdout + человеческий гейт обязательны; автор продаёт
клуб — тон оптимистичный.

**Триггеры переоткрытия:** появление второго агента с измеримой метрикой; провал приёмки,
вызванный «зелёными» тестами, написанными самим агентом; решение автоматизировать цикл
улучшения скиллов.

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
- [x] **UXT-1.** ✅ **Fixed + Verified (25.11.2026).** Создан скилл
      `~/.config/opencode/skills/first-users/SKILL.md` (4 промпта-персоны с quit-правилами,
      цикл «прогон → таблица → фикс → свежая партия», границы: только localhost, без
      реальных отправок, субагенты по очереди, slow 3G — «не проверено») и команда
      `~/.config/opencode/commands/first-users.md`; симлинк в `~/.agents/skills/` для ZCode.
      Вторая партия из 4 свежих субагентов выполнена вслепую: 2 настоящих дефекта
      (мёртвый `href="#"` у Telegram-фолбэка, противоречие FAQ про цены + опечатки)
      исправлены; регресс-тест в `tests/service-facts.test.js` нашёл то же противоречие
      на странице лендинга. Мобильные претензии про CTA/фокус/FAQ не подтвердились —
      артефакт клика по координатам при DPR2; реален только мелкий чекбокс (16→24px).
      Отчёт: `qa/first-users/REPORT.md`.
- [x] **UXT-2.** ✅ **Fixed + Verified (25.11.2026).** Первый прогон — на лендинге `ai-traffic-pro` (`projects/ai-marketing`), локальный `astro preview :4321`. Отчёт до/после + 10 скриншотов: `qa/first-users/REPORT.md`. Найдено и исправлено 2 дефекта: мусорные имя/контакт (`#$%^&*()`, `123`) проходили в Worker → вынесена `validateLead()` + 6 тестов; опечатка «заутанного» → «заумного». Повтор 4 сценариев после сборки: `fetchCalls: 0`, подсказки видны, мобильный 375px без горизонтального скролла, цены/политики — 200. `npm test` и `npm run build` зелёные. Вторая партия — 4 свежих субагента вслепую по команде `first-users` (UXT-1). Ограничение: slow 3G недоступен; мобильные претензии субагента про CTA/фокус/FAQ не подтвердились при проверке селектором/JS.
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
- [x] **ADS-1.** ✅ **Fixed + Verified (25.11.2026).** `landing-page-design` и
      `anti-ui-slop-reviewer` перенесены из `skills-lib/` в активные скиллы,
      симлинки в `~/.agents/skills/` для ZCode. В конец `landing-page-design`
      добавлен раздел «Design values — AI Bureau fork»: Playfair Display italic
      400 + Manrope + JetBrains Mono, точные hex токенов Editorial Warm, spacing,
      radii, тени, локальные исключения (Material Symbols, blur только у шапки).
      Источник репо верифицирован 25.10 (MIT, 5.0k★) — правило 13 соблюдено.
- [x] **ADS-2.** ✅ **Fixed + Verified (25.11.2026).** Ретро-интейк по A1/A2
      сделан по данным репо (лендинг уже собран). Finish-gate свежим субагентом
      `anti-ui-slop-reviewer`: вердикт **block** → после фиксов **conditional pass**.
      Исправлено: сломанный переключатель услуг (`innerHTML=''` → сохранение
      `unifiedMarkup`, проверка 3→3→3), псевдо-live метки, контраст stone-400
      в 11–12px, touch-таргеты 32→44px, тихие ошибки чата, обещание «CPA −40%»,
      дрейф шрифтов в комментариях, незатроттленный scroll. Отчёт и скриншоты:
      `qa/first-users/ADS2-FINISH-GATE.md`. `npm run build` и `npm test` зелёные.
      Реальные POST проверены отдельно (API-GATE-1). Не проверено: slow 3G,
      iOS Safari, reduced-motion; B11 «tagline reveal» осознанно не внедрён
      (нужно решение владельца).

## ✅ API-GATE — живые POST в Worker (25.11.2026)

- [x] **API-GATE-1.** ✅ **Verified (25.11.2026).** `GET /api/health/` → 200
      (`telegram/ai/publish: true`); `POST /api/lead/` с явно тестовой заявкой →
      200 `{"ok":true}`; `POST /api/chat/` → 200, `source: knowledge`,
      `askContact: true`. Независимо подтверждена запись вопроса в KV через
      `/api/chat/log` (Bearer): «ТЕСТ UXT» найден. Telegram-доставку заявки
      подтвердить не удалось (`getUpdates` заблокирован активным webhook, а
      `deliverLead()` возвращает true даже при отказе Telegram) — нужно визуально
      проверить чат. Живой ответ выявил устаревшую базу знаний («Вилки на сайте
      нет намеренно»): исправлено в `server/agent-core.js` + регресс-тест,
      `npm test` зелёный. Отчёт: `qa/first-users/API-GATE.md`.
- [x] **API-GATE-2.** ✅ **Fixed + Verified (25.11.2026).** После подтверждения
      Игорем доставки (Telegram 23:41/23:42) выполнен `--dry-run`, затем деплой
      `npx wrangler@4 deploy --config worker/wrangler.jsonc` — Version ID
      `9e85177f-a8ec-49a3-beb1-80773d93b809`. Повторный живой `/api/chat/`
      теперь отвечает «Нижние границы по работам есть на страницах услуг;
      точную смету считаем по запросу…» — старого «вилок нет» нет. Третий
      тестовый вопрос ушёл в Telegram (помечен «ПОВТОРНЫЙ ТЕСТ после деплоя»).

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

## 🔎 AB-AUDIT — AI Bureau: аудит сайта и контентная дорожная карта (24.11.2026)

**Источник истины:** прод https://ai-bureau.online/ отдаётся репозиторием `Erik03132/ai-bureau-web-finish` (`cname` подтверждён GitHub Pages API), коммит `0eb65c7`. `ai-traffic-pro-landing` — эталон, не источник сайта. `ai-bureau-site` и `ai-bureau` домен не обслуживают.

**Статус: Fixed (документы) + Verified (находки подтверждены).** Код сайта не менялся. Коммитов и публикаций нет. Все работы ниже требуют одобрения Игоря.

- [x] **AB-AUDIT-1 (Fixed + Verified):** аудит в `docs/audit/`: `README.md`, `FINDINGS.md` (12 находок с доказательствами), `BENCHMARK_GAP.md`, `PROPOSED_STRUCTURE.md`, скриншоты 1440/390 px, логи гейтов. Verified: curl-ответы, разбор JSON-LD, сравнение репо с продом. Полевых CWV нет — помечено как limitation.
- [x] **AB-AUDIT-2 (Fixed + Verified):** дорожная карта в `docs/roadmap/`: 10 статей на декабрь с датами Хабра и D+2 для TG/VK/Дзен, схема реестра, шаблон обложки, голос Шекспир v2 для B2B, eval-гейт. Ключи помечены гипотезой. VK и Дзен — ручная публикация.
- [x] **AB-AUDIT-3 (Verified):** контент-линтер прогнан по всем 11 авторским документам: 11/11 EXIT=0, лог `docs/audit/gates/content_lint_2026-11-24.log`.
- [x] **AB-P0-1 (фактически закрыто 27.11.2026):** форма на главной шлёт `POST /api/submit` на статический GitHub Pages. `curl -X POST` → **405**. Цель Метрики `form_submit` срабатывает до ответа сервера. Игорь одобрил Worker/эндпоинт, но к моменту проверки патч `docs/roadmap/stitch/prod-patch/` уже заменил форму на рабочую Telegram-кнопку и задеплоен в прод (AB-P0-1-DEPLOY, коммит `82e7ad8`). Повторная проверка 27.11: `t.me/erik03132` ×4, `api/submit`/`contactForm`/`form_submit` = 0. Worker избыточен; нужен только если Игорь явно захочет замены Telegram.
- [ ] **AB-P1-1 (1–2 ч):** карточки шести услуг на главной не являются ссылками — страницы-сироты. Доказательство: `index.html:1469–1569`, `grep 'services/'` → 0.
- [ ] **AB-P1-2 (2–4 ч):** `llms.txt` и `llms-full.txt` на домене отдают 404. У эталона 216 строк / 18 581 B, live 200.
- [ ] **AB-P1-3 (1 день на каркас):** нет `/blog/`, кейсов с цифрами и датами. 7 URL в sitemap. Раздел «кейсы» — три сценария без метрик.
- [ ] **AB-P1-4 (1 день):** шесть сервисных страниц повторяют дословно «Как это работает» и «Что получите».
- [ ] **AB-P1-5 (2–4 ч + юрист):** `privacy.html` без мета и каноникала, не в sitemap, есть «на behalf of», «по электронной почte», «ноказание», нет юрлица и упоминания Метрики; заявлено шифрование в БД при отсутствии бэкенда.
- [ ] **AB-P1-6 (0,5–1 день):** нет заголовков безопасности. GitHub Pages такие заголовки не позволяет — нужно решить вопрос CDN/proxy.
- [ ] **AB-P2 (по очереди):** мобильное переполнение (скрин 390 px), `@import` Google Fonts и 25 КБ inline CSS, нет skip-link и `:focus-visible`, слабый граф JSON-LD без `@id`, устаревший sitemap (`lastmod=2026-09-30`).
- [x] **AB-EVAL-1 (Verified 27.11.2026):** `eval_gate.sh --quick` зелёный — **19/19**, включая `eval_ai_scout.py` 9/9 (было 8/9). Старый лог 17/18 в `docs/audit/gates/` устарел. `--holdout` по-прежнему FAIL: сейф пуст по RSI-002, кейсы пишет только человек. Свой `tests/eval_ai_bureau_content.py` не создавался — отдельная задача после одобрения AB-01…AB-03.
- **Следующий шаг одно действие:** закрепить `Erik03132/ai-bureau-web-finish` как SSoT и убрать `ai-bureau.pro` из локальных копий; Worker не нужен, пока работает Telegram-кнопка.

## 🎨 AB-STITCH — главная AI Bureau в новом редакционном стиле (24.11.2026)

**Статус: Fixed + Verified.** Владелец выбрал концепт A «Редакционный лайм» из трёх предложенных. Новый Stitch-проект API создал, но генерация экранов уходила в timeout и канвас оставался пустым. Работа выполнена в старом проекте `13295436464234185747`: HTML главной заменён через `update_screen`, экран `d98c2bdbb3534ea68ebb0d4095e35558`.

- [x] **AB-STITCH-1 (Fixed + Verified):** HTML `docs/roadmap/stitch/variant-a-home.html` загружен в Stitch. Повторная загрузка из Stitch подтвердила новый заголовок, рубрику `[09 / СЛЕДУЮЩИЙ ШАГ]` и отсутствие старого текста. Локальный скрин `variant-a-home.png` 1440×2400. Прод и код не тронуты.
- [x] **AB-STITCH-2 (Fixed):** зафиксированы три концепта; A выбран владельцем. B «тёмный инженерный» и C «лендинг-каталог» остаются опцией.
- [x] **AB-STITCH-3 (Fixed + Verified):** по выбору владельца лаймовый акцент заменён на палитру A: графит `#23211F`, тёплый песок `#F3EFE7`, терракота `#B95433`. HTML в Stitch обновлён повторно; проверка загруженного файла показала терракоту и отсутствие лайма.
- [x] **AB-STITCH-4 (Fixed + Verified):** по правкам владельца убран бесполезный рисунок в hero, вместо него блок «Что будет после аудита»; кнопки вверху терракотовые; все карточки услуг и кейсов светлые; радиус 16 px. HTML в Stitch обновлён, проверка показала новый блок и отсутствие лайма.
- [x] **AB-STITCH-5 (Fixed):** сделан газетный макет `variant-newspaper.html` и скриншот. Чёрно-белый, три колонки, Georgia, точечный растр вместо фото. В Stitch не загружался.
- [x] **AB-STITCH-6 (Fixed):** владелец выбрал вариант A для главной. Газетный макет отложен для будущих лендингов и записан как SYS-002 в `docs/IMPROVEMENT_BACKLOG.md`. A остаётся загруженным в Stitch.
- [x] **AB-STITCH-7 (Fixed + Verified):** сделаны шесть экранов в стиле A: услуги, услуга RAG, кейсы, блог, контакты и мобильная главная. Все загружены в Stitch через замену HTML старых экранов. Verified: повторная выгрузка показала нужные заголовки, терракоту и отсутствие лайма. Контакты и реквизиты взяты из `projects/ai-marketing/src/data/site.ts` по указанию владельца, помечены как требующие подтверждения для ai-bureau.online.
- [ ] **AB-STITCH-8 (после приёмки макетов):** перенести одобренную вёрстку в прод только после явного разрешения и после AB-P0-1. Проверить мобильную версию остальных страниц.

## 📄 AB-LANDINGS — мультилендинги услуг AI Bureau (25.11.2026)

**Статус: Fixed (структура) + Verified (линтер).** Визуал согласован. Реализация перенесена в новую сессию с чистым контекстом. Handoff: `docs/handoff_2026-11-25_service-landings.json`.

- [x] **AB-LANDINGS-1 (Fixed + Verified):** структура шести страниц услуг зафиксирована в `docs/roadmap/stitch/SERVICE_LANDING_STRUCTURE.md`. Каркас по аналогу `projects/ai-marketing/docs/design/SPEC-multi-landing.md`. Для каждой услуги расписаны H1, бейдж, метрика, проблемы, шаги, сервисные блоки и темы FAQ. Добавлены структуры страницы блога, статьи, автора, политики конфиденциальности и публичной оферты по аналогу ai-marketing. `content_lint` EXIT=0.
- [x] **AB-LANDINGS-2 (Fixed):** структура шести лендингов утверждена Игорем 25.11.2026 без правок.
- [x] **AB-LANDINGS-3 (Fixed + Verified):** первый лендинг RAG собран в стиле A. Файлы `docs/roadmap/stitch/landing-rag.html` и `landing-rag.png` (1440×2400). После замечания владельца лендинг расширен с 21 КБ до 56 КБ: добавлены блоки 03.8–03.12, 3 таблицы, полные ответы на 15 вопросов. HTML загружен в экран Stitch `1da96734a54946d9834783d5ae1b2ac1`; повторная выгрузка подтвердила H1, терракоту, 15 FAQ и отсутствие лайма. `content_lint` по видимому тексту rc=0. Ждёт визуального апрува.
- [x] **AB-LANDINGS-3b (Fixed + Verified):** сделан скан трёх конкурентов через Firecrawl. Отчёт `docs/audit/competitor-scan-ai-bureau-2026-11-25.md`. Найдены четыре дополнения: полоса метрик, цена ошибки в проблемах, стек и подготовка заказчика, смета по строкам. Чужие цифры и тексты не копируются. `content_lint` rc=0.
- [x] **AB-LANDINGS-3c (Fixed + Verified):** в RAG-лендинг внесены все четыре дополнения из скан-отчёта. HTML вырос до 64 КБ. Добавлены [03.13 / СТЕК], [03.14 / ЧТО ПОДГОТОВИТЬ], [03.15 / СТОИМОСТЬ], полоса метрик и цена ошибки в проблемах. Stitch принял HTML; повторная выгрузка подтвердила блоки, терракоту и отсутствие лайма. `content_lint` rc=0. Блок отзывов отложен. Дополнительно загружен новый скриншот в `screenshot` экрана Stitch: канвас показывал старый превью, потому что менялся только HTML.
- [x] **AB-LANDINGS-3d (Fixed + Verified):** владелец поставил звёздочки и лайки в Stitch. Главная и RAG апрувлены в стиле «светлая инженерная сетка». Сняты финальные HTML и картинки в `docs/roadmap/stitch/final/` (`home.html`, `home.jpg`, `rag.html`, `rag.png`, `CAPTURE.md`). Черновики перенесены в `archive/`. Цены и метрики в новой главной помечены как гипотеза и не переносятся без подтверждения.
- [x] **AB-LANDINGS-3e (Fixed + Verified):** лендинг AI-агентов собран. Файлы `docs/roadmap/stitch/final/agents.html` (61 КБ) и `agents.png` (1440×2400). HTML и скриншот загружены в экран Stitch `74e29b…`. Verified: H1, терракота, зелёные акценты, 15 FAQ, 3 таблицы, разделы 03.5–03.15, отсутствие лайма. `content_lint` rc=0. Неподтверждённые цены и метрики не переносились. По правке владельца розовая подложка блока «Как работает агент в продажах» заменена на белую: блок и заголовок восстановлены. Затем все розовые и светло-зелёные подложки убраны из активных макетов: главная, RAG и AI-агенты. Правило зафиксировано: подложка только белая или тёмно-зелёная. HTML и скриншоты всех трёх экранов повторно загружены в Stitch. Тонкие линии на тёмно-зелёном фоне заменены с красных на белые. По-final решению владельца зелёные большие блоки заменены на графитово-синий формат `#1f2937`, `#0f172a`, `#334155`, `#475569`; номера и подписи на тёмном — белые или `#cbd5e1`. Verified: в выгруженных HTML нет `F3E1D7`, `E9E6DD`, `d3e5d0` и лайма. `content_lint` rc=0. Папка `archive/` удалена по просьбе владельца. В канвасе Stitch скрыты все лишние экраны; видимы только три с метками 01 ГЛАВНАЯ, 02 RAG, 03 AI-АГЕНТЫ. Ждёт апрува.
- [x] **AB-LANDINGS-3f (Fixed):** владелец апрувнул три страницы. По правке удалена декоративная полоса под H2 «Как работает агент в продажах»; HTML и скриншот загружены в Stitch. Verified: полоса отсутствует в выгруженном HTML.
- [x] **AB-LANDINGS-3g-RAG (Fixed + Verified):** RAG-страница обновлена по новым правилам. `final/rag.html` 76 828 байт, иконок 37, три графитовые секции (02, 03.8, 03.10), светлые FAQ и заявка. Stitch принял HTML и скриншот; `content_lint` rc=0. Ждёт апрува.
- [x] **AB-LANDINGS-3h-1 (Fixed + Verified):** готовы лендинги «Документооборот» и «Чат-боты». HTML ~62 КБ каждый, по 15 FAQ, 3 таблицы, 3 графитовые секции, монохромные иконки. Загружены в Stitch; проверка выгрузки прошла, `content_lint` 0 предупреждений. Неподтверждённые цифры не использовались.
- [x] **AB-LANDINGS-3h-2 (Fixed + Verified):** собраны приватные LLM, AI-аудит, блог, автор, политика и оферта. Все одиннадцать экранов проекта Stitch видны и промаркированы от 01 до 11. После сообщения владельца видимость восстановлена повторно и экраны разложены сеткой: три колонки, четыре ряда, метки 01–11. Verified: HTML и PNG выгружены из Stitch, `content_lint` по видимому тексту rc=0 для всех новых страниц; у LLM и аудита исправлены повторы после основного прогона. Исправлена ссылка с главной на `privacy.html`.
- [x] **AB-LANDINGS-4a (Fixed + Verified):** по первому шагу постраничного разбора обновлена главная. Боковые отступы 48 px, внутренние отступы карточек 32 px, секции 104 px, добавлены графитовые блоки «С чего начать» и «Разборы по делу» с адаптированными таблицами и карточками. Verified: Stitch принял HTML и скриншот, выгрузка показывает три тёмных блока и новые отступы. Подвал приведён к тому же графитовому цвету `var(--dark)`; снят полностраничный миниатюрный скрин `home-full-thumb.png`. Убрана последняя короткая линия перед шагом 01. В блоке заявки рубрика `[09 / СЛЕДУЮЩИЙ ШАГ]` и ободок кнопки «Написать в Telegram» переведены в бежевый `var(--line)`. Владелец принял главную как финальную. Все правила главной объявлены обязательными для остальных страниц: единый графит, бежевая линия-разделитель, без коротких линий под H2, отступы 48/104/32 px.
- [x] **AB-LANDINGS-4b-RAG (Fixed + Verified):** RAG приведён к правилам главной. Один графит `#1f2937` для тёмных секций, заявки и подвала; бежевые разделители и рамки; без коротких линий под H2; отступы 48/104/32 px. Сохранены 37 иконок, 15 FAQ, 5 таблиц и AEO. Stitch принял HTML и PNG, `content_lint` rc=0. Снят полный миниатюрный скрин `rag-full-thumb.png`. По замечанию владельца блок 03.5 «Источники» переведён в графитовую подложку; в hero под кнопкой добавлены три подсказки с иконками. Verified: Stitch принял изменения, content_lint rc=0. Правило hero-подсказок распространено на остальные страницы. По замечанию об отступах RAG переведена на боковые поля 64 px, секции 120 px и карточки 36 px; это правило отправлено на остальные страницы. В RAG переформулирован H1: «Поиск по документам на базе RAG: ответы со ссылкой на источник». Блок 03.13 «Из чего собран поиск» переведён на графитовую подложку. Verified: Stitch принял HTML и PNG, новый full-thumb снят. Два агента применили hero-подсказки и новые отступы к девяти страницам. Verified: HTML и PNG загружены в Stitch, content_lint rc=0. По замечанию о пустом месте у полосы цифр в RAG верхний отступ уменьшен до 24 px, нижний до 56 px; повторный full-thumb снят. Все H2 в одиннадцати страницах сокращены до одной строки, включая «Как работает RAG» и «Что в поставке»; HTML и PNG всех экранов загружены повторно. Тёмная полоса цифр и её сдвиг к hero были отклонены владельцем и откачены на RAG и трёх услугах. Владелец подтвердил состояние «принято». В шагах процессов на шести страницах номер и срок вынесены в одну строку: номер слева, срок у правого края. Verified: Stitch принял HTML и PNG, полный thumb RAG переснят. Verified: Stitch принял откат, полный thumb RAG переснят заново.
- [x] **AB-LANDINGS-4c-03 (Fixed + Verified):** к странице «AI-агенты» применены все универсальные правила RAG и главной: единый графит, бежевые разделители, hero-подсказки, отступы 64/120/36 px, H2 в одну строку, номер и срок в одну строку со сроком у правого края, тёмный подвал с бежевой линией и бежевый ободок CTA. Короткие акцентные линии удалены и здесь, и ещё на двух услугах. Verified: Stitch принял HTML и PNG трёх страниц, полный thumb агентов снят. По правке владельца красные линии и подписи в тёмном блоке этапов заменены на бежевые `var(--line)`. Блок «Что в поставке» получил терракотовые иконки по образцу RAG; блоки «Из чего собран агент» и «Способы и границы» переведены на графитовую подложку. По последней правке в hero добавлены два поясняющих предложения, полоса цифр придвинута к блоку. Verified: Stitch принял HTML и PNG, полный thumb переснят. Ждёт апрува.
- [x] **AB-LANDINGS-4d-04 (Fixed + Verified):** страница «Документооборот» приведена к общим правилам: единые тёмные секции, тёмные CTA/подвал с бежевой линией, бежевый ободок кнопки, hero-подсказки, отступы 64/120/36 px, H2 и шаги в одну строку, полоса цифр придвинута. По правке владельца блок «Что в поставке» получил терракотовые иконки. Блок «От потока до прогона» расширен с двух до четырёх колонок: добавлены пилот на одном типе документов и расширение на поток. Verified: Stitch принял HTML и PNG, полный thumb переснят, четыре шага на месте. Ждёт апрува.
- [x] **AB-LANDINGS-4e-04 (Fixed + Verified):** «Способы и границы» и «Состав стоимости» переведены на графитовый фон с бежевыми таблицами. Владелец подтвердил: страница принята. Verified: Stitch принял HTML и PNG, полный скрин 1440×15961 сохранён.
- [x] **AB-LANDINGS-4f-05 (Fixed + Verified):** chatbots приведён к общим правилам: H2 в одну строку, два новых предложения в hero, отступы 128/120/36 px, полоса цифр придвинута, единый графит, тёмные CTA и подвал с бежевой линией, 10 терракотовых иконок в «Что в поставке», тёмные «Способы и границы» и «Состав стоимости». Verified: Stitch принял HTML и PNG, 15 FAQ и AEO сохранены, `content_lint` rc=0, полный скрин 1440×13840 и миниатюра есть. Ждёт апрува.
- [x] **AB-LANDINGS-4f-05 (Verified):** владелец подтвердил приёмку chatbots.
- [x] **AB-LANDINGS-4g-06 (Fixed + Verified):** приватные LLM приведены к общим правилам: H2 в одну строку, hero-подсказки и два новых предложения, отступы 128/120/36 px, полоса цифр придвинута, единый графит, бежевые разделители, 12 терракотовых иконок в поставке, тёмные «Способы и границы» и «Состав стоимости», шаги со сроком справа. Verified: Stitch принял HTML и PNG, 15 FAQ и AEO сохранены, content_lint rc=0, полный скрин 1440×15038 есть. Ждёт апрува.
- [x] **AB-LANDINGS-4g-06 (Verified):** владелец подтвердил приёмку приватных LLM.
- [x] **AB-LANDINGS-4h-07 (Fixed + Verified):** AI-аудит приведён к общим правилам: H2 в одну строку, hero-подсказки, отступы 128/120/36 px, полоса цифр придвинута, единый графит, бежевые разделители, 10 терракотовых иконок в поставке, тёмные «Четыре способа» и «Состав стоимости», шаги со сроком справа. Verified: Stitch принял HTML и PNG, 15 FAQ и AEO сохранены, content_lint rc=0, полный скрин 1440×15394 есть. Ждёт апрува.
- [x] **AB-LANDINGS-4h-07 (по правке):** «Четыре области» расширено до шести мини-блоков, «Честные ограничения» — до шести; «Четыре способа» переведено в светлый бежевый фон, «Состав работы» — в графит. Verified: Stitch принял HTML и PNG, полный thumb переснят. По правке владельца «Границы работы» расширены с четырёх до шести мини-блоков; «Шесть областей» фактически содержали четыре блока; добавлены «Метрики» и «Команда» — теперь шесть мини-блоков. Verified: Stitch принял HTML и PNG, полный thumb переснят. Ждёт апрува.
- [x] **AB-LANDINGS-4h-07 (Verified):** владелец подтвердил приёмку AI-аудита. Межстрочный интервал между «Что вы получите» и «Бесплатно» уменьшен до 8 px; Stitch обновлён.
- [x] **AB-LANDINGS-4i (Fixed + Verified):** служебные страницы — блог, автор, политика, оферта — доведены до финального стандарта: H2 в одну строку, hero-подсказки, отступы 128/120/36 px, светлые бежевые секции, тёмные CTA/подвал с бежевой линией. Verified: Stitch принял HTML и PNG, content_lint rc=0, полные скрины и миниатюры сохранены. Добавлена двенадцатая страница — согласие на обработку персональных данных. По последней правке автор получил расширенную биографию, «Три правила» и юридические страницы переведены в одну колонку, отступы CTA исправлены. Verified: Stitch принял HTML и PNG, content_lint rc=0 на всех четырёх. Все 12 страниц макетов готовы.
- [x] **AB-LANDINGS-5-FEMIDA (Fixed + Verified):** внутренний разбор Фемиды записан в `docs/audit/legal/femida-review-ai-bureau.md`. Покрытие 47/52 фактов (90%). Топ-3 риска: нет фиксации согласия на странице; оферта без цены и дат; срок удаления «в срок, установленный законодательством» вместо 30 дней. Ограничения: кросс-чек не делался, редакции помечены как независимо не проверенные. Отчёт справочный, финальное слово за юристом.
- [x] **AB-LANDINGS-5-QA (Fixed + Verified):** финальный QA в `docs/audit/final-qa-ai-bureau.md`. Проверено 268 href, исправлено 28 битых ссылок, осталось 0. content_lint rc=0 на 12/12. Verified: Stitch принял 6 исправленных HTML и PNG, сервер убит.
- [x] **AB-LANDINGS-6 (Fixed + Verified):** по решению владельца главная и RAG приведены к общему стандарту: акцент `#9e2a2b`, текст `#1f2937`, отступы 128/120/36. Verified: Stitch принял HTML и PNG, выгрузка байт-в-байт совпала с локальными файлами, content_lint rc=0, полные thumb сохранены.
- [x] **AB-LANDINGS-7 (Fixed + Verified):** владелец принял сайт целиком. Повторный финальный QA: 268 href, 0 битых; стили едины для 12 страниц; content_lint rc=0 на 12/12; HTML в Stitch совпадает с локальным 12/12. Отчёт `docs/audit/final-qa-ai-bureau.md`.
- [x] **AB-P0-1-PATCH (Fixed):** по решению владельца подготовлена замена формы на рабочую Telegram-кнопку. Файл `docs/roadmap/stitch/prod-patch/index.html`, диф `index.patch`, описание `README.md`. Verified: `api/submit`, `contactForm` и `form_submit` отсутствуют. Коммит и деплой не выполнялись.
- [x] **AB-P0-1-DEPLOY (Verified):** по разрешению владельца патч применён к прод-репо `Erik03132/ai-bureau-web-finish`, коммит `82e7ad8`, запушен в main. Verified на https://ai-bureau.online/: HTTP 200, `last-modified` 26.11.2026 16:57 GMT, `api/submit`/`contactForm`/`form_submit` = 0, рабочая Telegram-ссылка на месте. Dirty-файлов в клоне нет.
- [x] **AB-TW-1 (Fixed, Verified частично):** создано приложение Timeweb App Platform ID `296823` (`ai-bureau`, HTML/CSS/JS, Москва, репозиторий `Erik03132/ai-bureau-web-finish` подключён по URL, автодеплой недоступен). Verified: сборка `82e7ad8` успешна, по IP приложения `/`, `/privacy.html`, `/services/`, `/robots.txt`, `/sitemap.xml`, `/og-image.png` — 200, заголовок наш. OAuth GitHub не понадобился: репозиторий публичный.
- [x] **AB-TW-2 (Fixed + Verified):** DNS `ai-bureau.online` переведён с GitHub Pages на Timeweb App `296823`. Первая попытка 26.11 упиралась в лимит Let's Encrypt (серия неудачных проверок, пока apex ещё смотрел на GitHub). Одноразовая задача `aut_2197b1f67001KfXuORTQsRl1O6` (27.11 00:04 MSK, скрипт `docs/roadmap/timeweb/apex-switch.sh`) привязала apex к приложению и дождалась сертификата: `Exit code: 0`, «сертификат выпущен, https://ai-bureau.online/ отдаёт 200». Verified 27.11.2026: `CN=ai-bureau.online`, Let's Encrypt, до 24.02.2027; apex и `www` → `178.209.127.53`; `/`, `/privacy.html`, `/services/`, `/robots.txt`, `/sitemap.xml` — 200; canonical и og:url на apex; деплой `82e7ad8` success.
- [x] **AB-TW-3 (Fixed + Verified):** снят дубль с GitHub Pages: из прод-репозитория удалён `CNAME` (коммит `18ddf0a`), Pages выключен (`GET /repos/.../pages` → 404), `erik03132.github.io/ai-bureau-web-finish/` отдаёт 404. Деплой на Timeweb автоматизирован: `docs/roadmap/timeweb/deploy.sh` (флаги `--repo/--app/--commit/--wait/--dry-run/--help`, токен из `projects/ai-marketing/.env`, проверяет сборку и HTTP 200). Verified 27.11.2026 12:05: `success`, `https://ai-bureau.online/` → 200.
- [ ] **AB-TW-4 (частично Fixed, нужен Timeweb):** добавлена страница `404.html` (коммит `694ec3f`, деплой success, `https://ai-bureau.online/404.html` → 200 с нашим заголовком). Но статический пресет App Platform (`framework: static-nobuild`, Caddy) отдаёт `index.html` со статусом 200 на любой несуществующий путь — проверил `/foo.txt`, `/missing.css`, `/deep/nested/page`, `/CNAME`: везде 200 и заголовок главной. Своими файлами это не переопределяется, тумблера в API нет (`index_dir`, `build_cmd`, `run_cmd` — единственные поля). Пока риск снят canonical на главной. Решение владельца 27.11.2026: тикет отправлен — №13191315 «Настройка обработки ошибок 404 для приложения», сервис `ai-bureau`, статус «На рассмотрении». `404.html` уже в репозитории и заработает без правок. Резервный вариант (если поддержка откажет): перевести приложение на свой Node-сервер статики (`run_cmd: node server.js`).
- [x] **AB-LANDINGS-8 (Fixed + Verified):** новые 12 страниц из `docs/roadmap/stitch/final/` собраны и задеплоены на прод. Структура: `/` (home), `/services/ai-agents/`, `/services/rag/`, `/services/document-automation/`, `/services/chatbots/`, `/services/private-models/`, `/services/ai-audit/`, `/blog/`, `/author/`, `/privacy.html`, `/offer.html`, `/consent.html`. Добавлены canonical, OG, favicon, theme-color; ссылки на «Подробнее» ведут на свои услуги. Sitemap 12 URL. Link-check: 14 страниц, 307 ссылок, 0 проблем. Деплой `379d557` success, `https://ai-bureau.online/` → 200. Скриншоты live: новый дизайн (бежевый фон, красный акцент), старый лайм (`c8ef67`) отсутствует.
- [x] **AB-LANDINGS-9 (Fixed + Verified):** перекрёстные ссылки и навигация работают. Главная → 6 услуг + блог + автор. С каждой страницы услуги → 5 других услуг + блог. Блог/автор/юрстраницы → Услуги `/#services`, Блог, Автор, Конфиденциальность, Оферта, Согласие. Подвал и CTA выровнены: CTA обёрнут в `.wrap`, строки подвала в `.wrap`, ссылки в подвале — `flex-start` с отступами. Убраны служебные пометки в футере услуг; дисклеймер «не является публичной офертой» сохранён. Проверено: 13 страниц live, 232 ссылки, 0 проблем. Деплой `b8f64ae` success.
- [x] **AB-LANDINGS-10 (Fixed + Verified 27.11.2026):** единый подвал по образцу ai-traffic-pro на всех 13 страницах. Правка в `docs/roadmap/stitch/build_prod.py`: структура с брендом, услугами, правовыми ссылками, контактами, реквизитами и автором. Link-check: 15 страниц, 334 ссылки, 0 проблем. Деплой `3328bcf` success, `https://ai-bureau.online/` → 200.
- [x] **AB-LANDINGS-11 (Fixed + Verified 27.11.2026):** sticky-шапка на всех страницах при скролле. Добавлен общий `<style id="site-shared">` через сборщик. Проверено в Chrome: шапка видна на главной и на лендинге услуги при скролле. Деплой `3328bcf` success, `https://ai-bureau.online/` → 200.
- [ ] **AB-LANDINGS-12 (резерв):** юридические страницы на аппруве у человека-юриста; реквизиты и имя автора не подтверждены владельцем. Ждём ответа Timeweb по тикету №13191315 для 404.
- [x] **AB-LANDINGS-4 (Resolved):** форма на проде исправлена в AB-P0-1 (Telegram-ссылка). Блокер снят.

## 🎓 LL — SEO-гейткипинг и отравление LLM-консенсуса (ролик 26.11.2026)

> Источник: `youtu.be/rmQpx5jPDpU` — The Edward Show E1239 «SEO Experts Are Hiding
> Their Best Tactics From AI» (24.11.2026, 1:45:46), Edward Sturm + David Quaid.
> Верифицировано: oEmbed (автор/название) + независимые анонсы эпизода
> (getpodcast, Podfollow). Проверка factual-ядра (правило 13):
> **E-E-A-T не является прямым ранжирующим фактором** — подтверждено документацией Google
> (SEO Starter Guide, обновл. 2025-12-10; creating-helpful-content).
> **«Crawled — currently not indexed = проблема качества»** — частично:
> 03.11.2026 Google переписал справку («common message… doesn't necessarily
> indicate an issue»), но на Search Off the Record (07.2026) Mueller говорил
> «sometimes». Пять форм гейткипинга и «LLM сдаётся на 5-м возражении» — мнение
> спикеров, не бенчмарк; решением не считать.

**Вердикт: принять частично.** Берём не «publish everything», а два рабочих
слоя: (1) фильтр SEO-мифов с первоисточниками в наших агентах, (2) first-hand
замеры как GEO-преимущество. Граница: клиентские кейсы/данные без согласования не
публикуем — это не гейткипинг, а NDA.

- [x] **LL-1.** ✅ **Fixed + Verified (26.11.2026).** Фильтр SEO-мифов:
      `tools/seo_myths.py` (5 устойчивых мифов с исправлением и датированным
      первоисточником, CLI `--text/--file/--json`, коды 0/1/2) +
      `tools/tests/eval_seo_myths.py` (RED→GREEN: ловит все 5, не ловит
      корректные формулировки, детерминированные номера строк, CLI) — PASSED.
      Вшит в `tools/eval_gate.sh`; подключён к `freelance-agent/.agent/agents/
      marketer-strategist.md` как обязательный фильтр перед SEO-выводом. Добавлен
      раздел 8 в `vault/wiki/contradictions.md`. polish: eval_gate --quick
      выявил неродной провал `eval_ai_scout.py` (8/9, TS6133 — неиспользуемые
      импорты/функции в App.tsx, FavoritesTab, InsightsTab); убраны, `tsc --noEmit`
      rc=0. Итог: **eval gate 19/19 PASSED**, чекер вики 0 проблем.
- [x] **LL-2.** ✅ **Fixed + Verified (26.11.2026).** Создан
      `projects/ai-marketing/docs/GEO-FIRST-HAND.md` — хаб трёх собственных замеров
      с датой, методом и путями к сырым данным: 5×3 прогонов (Citation Rate 0/15,
      Brand Mention 2/15; `docs/seo/ai-visibility-2026-11-22.md` + raw/), аудит
      14 проверок (4 провала, llms.txt 7 КБ/11 ссылок; `geo-lint*.json`), разбор
      кликов 0,9% против 58%. Все три уже опубликованы в блоге и подключены к
      `blog/index.ts`. Регресс-тест `tests/geofirsthand.test.js` (5 кейсов: метод,
      существование сырых файлов, согласованность чисел, подключение статей,
      граница клиентских данных) — PASSED; `npm test` 34/34, `npm run build`
      35 страниц. ATP-G8 (повтор через 3–4 недели, рынок РФ: Яндекс + Google RU + Perplexity/Gemini/ChatGPT с русскими запросами) — следующий апдейт хаба.
- [x] **LL-3.** ✅ **Fixed + Verified (26.11.2026).** Политика публичности зафиксирована
      в SSoT: `~/.config/opencode/skills/brand-voice/SKILL.md` (таблица «публично /
      только по согласованию», граница ради NDA и точности, а не гейткипинга;
      напоминание, что E-E-A-T не фактор ранжирования + фильтр LL-1),
      `projects/ai-marketing/CONTEXT.md` и `~/.config/opencode/AGENTS.md` (п. 0.4).
      Регресс-тест границы — в `tests/geofirsthand.test.js`.

## 🧠 HND — Hindsight: долговременная память для кодящих агентов (ролик 26.11.2026)

> Источник: `youtu.be/wguigtLChtQ` — AI Stack Engineer, «Hindsight Agent Memory:
> Long Term Memory for Claude Code, OpenCode and Codex». Верифицировано 26.11:
> oEmbed (автор/название) + GitHub API `vectorize-io/hindsight` — **★63 385, MIT,
> push 25.11, не архивирован** + официальная документация интеграций.
> Бенчмарк вендора (AMB sdebench, 61 задача ×3): точность не растёт (60–61/61
> без памяти и с ней), меняется цена — Claude Code 0.85→0.36 правок/задачу и
> $0.445→$0.338; **opencode 1.20→0.80 и $0.634→$0.553**. Независимо не подтверждено,
> решением не считать — мерить на наших задачах.

**Вердикт: гипотеза-триал, не внедрять сразу.** Уникальное — автоматический ingest
git-истории и курируемые «pages» (архитектура, конвенции, текущие инициативы) на
старте сессии. Пересечение с claude-mem + `User.md` + викой + ACTIVE_TASKS почти
полное. Риски: cloud по умолчанию (данные клиентов вне РФ/NDA), daemon требует
LLM-ключ для экстракции, `opencode` и `opencode2` делят один конфиг и могут сломать
друг друга.

- [ ] **HND-1 (на досуге, по «да»):** поднять Hindsight в режиме `daemon`
      (self-host, без клиентских данных) на 10–20 наших задачах; замерить
      corrections/task и стоимость против текущего стека. Нет выигрыша → отклонить.
- [ ] **HND-2 (граница):** cloud НЕ использовать; bypass-прокси по ADR-002;
      симлинки `~/.agents/skills/` не трогать без проверки совместимости v1/v2.
- [ ] **HND-3 (точка решения):** по результатам HND-1 — принять/отклонить;
      при принятии записать ADR (scaffold, не замена claude-mem) и eval.

## 🩺 SITE-WD — сторож сайта: детерминированный слой + вечерний агент (26.11.2026)

- [x] **SITE-WD-1.** ✅ **Fixed + Verified (26.11.2026).** Создан
      `tools/ops/site_watchdog.sh` (CP-1: `--base/--api/--dry-run/--json/--quiet/
      --no-alert/--help`, коды 0/1/2, идемпотентный, reader-only): 9 публичных
      URL + `/api/health/` + POST `/api/lead/` с honeypot (реальных заявок не шлёт).
      Алерт в Telegram только при смене состояния, как в `gateway_watchdog.sh`.
      Dry-run на проде — 11/11 = 200, `ok`; negative-path на мёртвом хосте —
      `fail` с перечнем, `json` валидный, `--bogus` → rc=2. Повешен на launchd
      `com.user.site-watchdog` каждые 15 мин (`plutil -lint OK`, `launchctl list`
      → pid 1399, state `ok`). Источник токенов — корневой `.env` (как у gateway).
- [x] **SITE-WD-2.** ✅ **Fixed + Verified (26.11.2026).** Детерминированный ежедневный
      отчёт без LLM: `tools/ops/site_daily_digest.sh` (собирает JSON site_watchdog +
      вывод gateway_watchdog в `reports/site_digest_<дата>.md`, `--dry-run`, atomic
      write) и `tools/ops/site_daily_report.py` (читает только JSON, сравнивает с
      вчерашним состоянием, ≤5 строк, `--send/--dry-run/--force`). Launchd
      `com.user.site-daily-report` 08:15 после `nightsummary` (08:00): `plutil -lint
      OK`, два kickstart → отчёт в логе, **stderr пуст**, Telegram-отправка
      выполнена. Агент не генерирует findings — только интерпретирует exit-коды;
      тренд GEO (ATP-G8) оставлен как ссылка в дижесте, а не как выдуманный вывод.
      Побочно: eval_gate выявил нестабильность `eval_agent_lab.py` — тест памяти
      писал в фиксированный `/tmp/test_eval_memory.json` и падал 13/14 после наших
      прогонов; переведён на `tempfile.TemporaryDirectory`. Итог: eval gate 19/19.
- [x] **SITE-WD-3 (только РФ, 26.11.2026).** ✅ **Fixed + Verified.** Все проверки
      сайта переведены на РФ-направление: `site_watchdog.sh` теперь явно вызывает
      `curl --noproxy '*'` для страниц и API (ADR-002: российские сервисы напрямую),
      dry-run после правки — 11/11 = 200. Ежедневный отчёт остался, но GEO-тренд
      в нём теперь ссылка на РФ-протокол ATP-G8, а не на архивный замер. Разовая
      проверка `ipinfo.io` после отключения VPN (ATP-G10): **95.154.153.47,
      Воскресенск, МО, RU** — это рабочий РФ-эгресс; мониторинг сайта и новые
      GEO-замеры идут из РФ. Старый NL-адрес остался только в архиве замера 24.11.
      Сломанный launchd `ru.freelance.geo-monitor` (ссылается на несуществующий
      `tools/geo_monitor.py`) выгружен: `launchctl list` показывает только
      `com.user.site-watchdog`. plist удалён не был.

## 🏦 FCA — AI Spotlight Observatory: разбор для агента «Финансист» (27.11.2026)

**Источник:** `ai-spotlight.fcainnovation.co.uk`. **Проверено (src)**: пресс-релиз
FCA от 19.11.2026 (`fca.org.uk/news/press-releases/fca-launches-world-first-platform…`) —
платформа FCA + CFTE + NayaOne, >200 организаций, 150 областей, ~65 публичных
кейсов с таксономией «use case ≠ implementation». Детали (целевые клиенты, демо)
доступны только после регистрации.

**Вердикт: принято частично — как источник eval-сценариев и границ, НЕ как фича.**
Каталог регулятора не добавляет агенту новой функции, но даёт готовую таксономию
и темы (bias/fairness, explainability/governance, data quality, compliance),
которые усиливают промпт и eval Финансиста. Прямого отношения к нашим Kwork/IZ
финансам нет — как готовое решение не берём.

- [x] **FCA-1 (eval).** ✅ **Fixed + Verified (27.11.2026).** Создан
      `tests/eval_financier.py`: 6 сценариев по кейсам FCA (FUC043/023/011/059/
      019/044) + 2 гардрейла (длинный payback бьёт высокий ratio, пол маржи
      60/40, zero-churn → горизонт 36 мес) + контракт формул в `SKILL.md`.
      Добавлен в `KNOWN_EVALS` (`tools/eval_gate.sh`). Прогон: соло — PASSED,
      `bash tools/eval_gate.sh --quick` — **20/20 PASSED**. Holdout (RSI-002)
      не трогался — только на приёмке человеком.
- [x] **FCA-2 (граница).** ✅ **Fixed + Verified (27.11.2026).** Добавлена секция
      «Правовая граница (FCA-2)» в OC-мастер
      `skills/financier-unit-economics/SKILL.md` (внутренние расчёты ≠ инвестиционная
      консультация; human-gate; обезличенные входные данные) и отдельная строка
      в живом промпте `~/.hermes/profiles/financier/SOUL.md` (вне git-репозитория).
      Проверка фрагментов добавлена в `tests/eval_financier.py`: PASSED,
      `eval_gate.sh --quick` — 20/20. **Gateway перезапущен 27.11 в 12:16**
      (`launchctl kickstart -k gui/501/ai.hermes.gateway-financier`): PID 14513,
      `launchctl print` → state=running, SOUL.md от 12:14 вошёл в новый процесс.
      **Отказ по имени (HT-3):** Telegram не подключается через локальный прокси
      `127.0.0.1:64468` (attempt 6/8, ConnectError); тот же отказ у `sherlock`
      в 12:12 — системная проблема сети/прокси, не правка промпта.
      **Диагноз 27.11:** `lsof` — слушателя нет на 64468/64469; launchd
      `com.antigravity.usproxy-tunnel.plist.disabled` (форвард на старый VPS
      172.120.21.141, серверов нет с 25.11); в `~/.hermes/profiles/financier/.env`
      строки 494–499 хардкодят мёртвый локальный прокси, `NO_PROXY` — только
      localhost. Прямой доступ к Telegram работает (`curl --noproxy '*'` → 302).
      Тот же прокси прописан в 18 профилях — чинить надо централизованно,
      по ADR-002 (прокси только для заблокированных ресурсов).
      **Исправлено 27.11 (Fixed + Verified):** в 18 `.env` добавлены
      `api.telegram.org,telegram.org` в `NO_PROXY`/`no_proxy` (внутрь кавычек,
      mode `-rw-------` сохранён), 9 активных gateway перезапущены. Прокси-ошибка
      ушла: adaptive дошёл до сервера Telegram.

## 🤖 TG-TOKEN — токены ботов отклонены Telegram (27.11.2026)

- [x] **TG-1a (финансист).** ✅ **Fixed + Verified (27.11 12:33).** Игорь дал
      новый `TELEGRAM_BOT_TOKEN`; заменён в `.env` профиля (права `-rw-------`
      сохранены), gateway перезапущен: `✓ telegram connected`, polling healthy,
      `Channel directory built: 1 target(s)`, 60 команд зарегистрировано, PID 22716.
      Токен в чате не воспроизводился.
- [x] **TG-1b — закрыто по решению Игоря (27.11):** остальные 6 профилей
      (batrak, builder, english-tutor, femida, marketer, sherlock) пока не нужны,
      токены не обновляем, gateway не трогаем. При возобновлении — начать с
      новых токенов через @BotFather.
- [ ] **TG-2 (не трогать до TG-1):** `ai.hermes.gateway-default` вышел с кодом 1
      и пишет STANDALONE / `hermes gateway migrate --multiplex` — отдельная
      проблема оркестрации, не следствие правки NO_PROXY.
- [x] **FCA-3 (источник).** ✅ **Fixed + Verified (27.11.2026).** Снято 10 карточек
      (FUC043/023/011/059/019/044/016/008/041/037) в
      `docs/cases/2026-11-27_fca-ai-spotlight.md`: `curl --noproxy '*'` + regex
      `h1`/`p`/`vendor_listing`, без LLM и без выдуманных метрик. Отказ по имени:
     register на платформе НЕ делался (детальные данные — только после регистрации,
      клиентские персданные не нужны). Индекс обновлён; smoke — 10 строк таблицы,
      1 запись в `docs/cases/INDEX.md`, eval_financier PASSED.
- [x] **FCA-4 — переписано под реальность (27.11.2026, Fixed).** Прежняя
      формулировка «внешние ресурсы только через прокси» была неверной и
      противоречила ADR-002: мёртвый туннель `127.0.0.1:64468` маскировал
      доступность и вызвал ConnectError у 9 gateway. Рабочая политика:
      внешние ресурсы (FCA, Brave и др.) — **напрямую, если доступны**; прокси
      только при реальной блокировке и только при живом слушателе
      (`lsof -nP -iTCP:<port> -sTCP:LISTEN`). Для Telegram домены добавлены
      в `NO_PROXY` 18 профилей. ADR-002 не менялся — он уже требовал прокси
      только для заблокированных ресурсов; ошибка была в этой задаче.

## 🚫 CGL — colab-g4-glm53: оценка для стека (дроп 27.11.2026)

**Источник и проверка (src):** `github.com/alesha-pro/tools/tree/main/colab-g4-glm53` —
GitHub API: **★819, MIT, push 26.11.2026, не архивирован**; README.ru.md прочитан
полностью. Независимая сверка — [Sulat 27.11.2026](https://news.sulat.com/2026/11/27/colab-glm-uncensored):
замеры 102.3 tok/s — **авторские**, а не независимый бенчмарк.

**Вердикт: НЕ ПРИМЕНЯЕМ — граница HTC (abliterated/uncensored модель).**
Дополнительные причины: DFlash2-драфтер, от которого зависит 102 tok/s, имеет
лицензию **CC BY-NC-ND 4.0 (только некоммерческое использование)**; без него 71.5 tok/s.
Маркетинговое «refusal-free» опровергается модель-кардой: отказы снижены с 0.891
до 0.094 и измерены на FP8, а не на кванте 2.51 bpw. Цена ~$1/ч ≈ $2.72 за 1M
output-token — дороже хостинга в 1.7–4.9 раза. G4 подтверждён только для Ultra,
Colab ToS запрещает расшаривать туннель и требует `colab stop`.

- [ ] **CGL-1 (если тема вернётся):** рассмотреть ту же схему (Colab G4 + Project
      Maya + SSH-туннель) с **обычной, не abliterated моделью** и без драфтера
      CC BY-NC-ND — как отдельную гипотезу с eval по latency/цене, не как эту фичу.
- [ ] **CGL-2 (граница):** не клонировать репо и не запускать `start.sh` без
      явного решения владельца; никаких ключей/токенов Colab в общие конфиги.

## 🎬 VEX — video-explainer: анимированные постеры/рекламные блоки (дроп 27.11.2026)

**Источник и проверка (src):** `github.com/petergyang/video-explainer` — GitHub API:
**★556, MIT, создан 15.11.2026, push 25.11, не архивирован**; README/SKILL.md/eval.md
прочитаны. Независимо подтверждено [ReelStack 25.11](https://thereelstack.com/lab/video-explainer-peter-yang-open-source-agent-skill-motion-illustrated-3d-explainers-hyperframes)
и [hotskills.dev](https://hotskills.dev/skill/petergyang-video-explainer/) (Grade A PARTIAL):
у проекта **observed network/broad shell**, 6 файлов не просканированы → перед установкой
обязателен `ai-defender` аудит исходников, ставить global не сразу.

**Вердикт: принято в пилот с ограничениями.** Это не генератор картинок, а агентный
пайплайн: `script.md` → локальный рендер через HyperFrames (Apache 2.0) → MP4 1080p
16:9/9:16/1:1, 30 fps; 3 движка (Motion 2D, Illustrated, 3D Three.js + bloom),
кадры детерминированы, есть 10 QA-проверок + second-agent frame review + браузерный
review с комментариями к кадрам. Для «movie-design» — режим 3D, но он ~7× токенов
Motion; для рекламных блоков — Motion + 9:16 + `Voice: none` + synth-музыка.
Постеры ≈ стоп-кадры из рендера (`work/preview/frame-*.png`) или отдельный seek-кадр.

- [x] **VEX-1 (безопасность).** ✅ **Fixed + Verified (27.11.2026).** Клон
      `--depth 1` в изолированный temp, прогон `ai-defender.sh audit`:
      **CRITICAL=0 / HIGH=0 / MEDIUM=3 / LOW=0**; отчёты в клоне
      `security/SECURITY.md` и `security/audit-report.json`. Ручная сверка:
      3× `innerHTML` в `review_page.py` — 2 безопасные (числа/пустая строка),
      1 с `short(scene)` из своего `script.md`; комментарии идут через
      `textContent`. Review-сервер слушает **только 127.0.0.1**. Секретов
      в исходниках нет; `GEMINI_API_KEY` читается из env/`.env` — мы его не используем.
      Доп. MEDIUM (ручной разбор): `media.py` тянет произвольный URL без
      allowlist и без лимита размера ответа; `setup.sh` при первом запуске
      ставит `npx hyperframes@0.9.79` + Chrome (~390 MB), `--voice` ставит
      kokoro/parakeet. Митигация: только доверенные хосты/медиа, без `--voice`
      и без Gemini-ключа, установка в отдельный worktree, не global.
- [x] **VEX-2 (пилот).** ✅ **Fixed + Verified (27.11.2026).** Скилл поставлен
      в isolated worktree `~/.local/share/opencode/worktree/619c7d/vex-video-pilot`
      (`setup.sh` без `--voice`, HyperFrames Chrome готов); проект
      `projects/vex-pilot-ai-bureau` — вертикальный 9:16 ролик 24 с без голоса
      (Motion, `Voice: none`, `Music: synth:minimal`, 5 сцен). Итог:
      `renders/vex-pilot-ai-bureau-v4.mp4`, 1080×1920 / 30 fps, `qa.py` **10/10**
      (loudness -14.4 LUFS, motion 87%, hyperframes errors=0). 2 layout-warning
      про safe area TikTok/Reels — визуально кадры в границах, но это долг VEX-3.
      Это смоук пайплайна, **не финальный креатив**: hero пока статичный,
      настоящий «movie-design» — отдельная итерация в 3D-режиме. Fresh-eyes
      subagent-ревью контакт-листа не запускал — смоук принимается как Verified
      по `qa.py` + ручному просмотру.
- [x] **VEX-3/VEX-4 — отложено по решению Игоря (27.11.2026):** оценка
      «троечка с минусом, потенциал есть». Вся фича перенесена в
      `docs/IMPROVEMENT_BACKLOG.md` как **SYS-003** с вердиктом, списком
      «что взять при возврате» и условием пересмотра. В ACTIVE_TASKS больше
      не держим: возврат только при конкретной задаче анимированной рекламы.
      Границы на будущее (без Gemini-ключа, обезличенные данные, ADR-002)
      перенесены в SYS-003.

## 🗂 OBS — Obsidian Connectors: разбор заявления (дроп 27.11.2026)

**Проверка (src):** официальная [Obsidian Help / Connectors](https://obsidian.md/help/connectors)
+ независимый разбор [Sulat 26.11](https://news.sulat.com/2026/11/26/obsidian-connectors-agents/).
Заявление в целом верное, с тремя уточнениями: (1) это **не сервер и не MCP**, а
7 open-source навыков (`obsidian-markdown`, `obsidian-bases`, `json-canvas`,
`obsidian-cli`, `obsidian-headless`, `defuddle`, `knap`) — know-how, а не доступ;
(2) CLI требует запущенного десктопа Obsidian и включённого CLI, Headless —
Node 22 + подписки Sync/Publish; (3) «обмен контекстом» = общие файлы, которые
агент должен прочитать, а не автоматическая передача памяти. Список агентов
шире заявленного: Claude, ChatGPT/Dots/Codex, Antigravity, Cursor, GitHub
Copilot, Grok Bot, Hermes, Kiro, Muse, **OpenCode**. Канбан — через Bases/Canvas,
не отдельный навык. Приватность: Obsidian не имеет доступа к заметкам, но
прочитанное агентом уходит в модель — 중요 для NDA/клиентских данных.

**Вердикт: принято частично — базовый паттерн у нас уже работает, берём только
форматные навыки после аудита.** У нас уже есть `vault/` (md-заметки, digest/source,
`vault/CLAUDE.md`) и агенты, которые читают/пишут файлы напрямую; claude-mem
остаётся отдельным слоем памяти и коннекторами не заменяется.

- [ ] **OBS-1 (до установки):** ai-defender аудит `obsidianmd/obsidian-skills`
      (внешние инструкции = surface prompt injection); поставить только
      форматные навыки `obsidian-markdown`/`obsidian-bases`/`json-canvas`,
      не `obsidian-cli` (широкий доступ к running app).
- [ ] **OBS-2 (пилот):** прогнать 1–2 наши vault-заметки через навыки, сверить
      корректность wikilinks/Bases/Canvas и соблюдение `vault/CLAUDE.md`
      (frontmatter `type/tags/status/updated`); без клиентских/NDA-заметок.
- [ ] **OBS-3 (граница):** не смешивать vault и SSoT (`ACTIVE_TASKS.md`,
      `chp.md`); любые записи агентов в vault — по правилу propose→approve;
      память `claude-mem` не дублировать в Obsidian без явного решения.
