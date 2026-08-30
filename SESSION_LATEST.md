# SESSION_LATEST.md — итоги сессии 29.08.2026 (вечер, аудит дашбордов)

## Главный результат

Аудит дашбордов OmniRoute/Hermes. Найдена и устранена путаница с портами,
починен автостарт VPS (systemd), зафиксирован SSoT-док.

### 1. Родной OmniRoute = :20128/dashboard (не :8890)
- `:8890` — самописный `omni_dashboard.py` на VPS через туннель (НЕ OmniRoute).
- `:20128/dashboard` — настоящий UI OmniRoute (локально на Маке). Открыт, подтверждён.

### 2. Фикс автостарта VPS (systemd)
- `omniroute.service` был failed (EADDRINUSE с ручной копией) → active.
- `hermes-dashboard.service` был crash-loop 220+ → active (дитя systemd).
- Все 6 юнитов active+enabled: omniroute, omni-dashboard, hermes-dashboard,
  hermes-gateway, hermes-serve, pm2-root.

### 3. Hermes Desktop в Login Items
- Добавлен автозапуск GUI при входе в Mac.

### 4. Веб :9120 = админка, не чат
- `/chat` = активация сессии. Общение → Desktop или ТГ-боты.

### 5. SSoT-док
- `~/freelance-2026/INFRA_SSOT_OMNIROUTE_HERMES.md` — единый источник по портам/сервисам.

---

# SESSION_LATEST.md — итоги сессии 29.08.2026 (вечер)

## Главный результат

Продолжили по `handoff_2026-08-29_vps_bots_setup.md`. Починили мост Mac→VPS
(стабильно через блок IP) и устранили кашу маршрутизации ТГ-ботов.

### 1. Мост Mac→VPS — СТАБИЛЕН
- Утром мост был КРАСНЫЙ: IPv4 Мака (динамический) выпал из whitelist VPS.
- В whitelist-igor (TimeWeb FWaaS) добавлен блок **`91.78.5.0/24`** на порты 22/2222
  (плюс старые одиночные IP). Мост перестал падать при смене IP.
- `check_bridge.sh --with-echo` = ВСЁ ЗЕЛЁНОЕ.
- Туннель: autossh LaunchAgent `com.igorvasin.vps-tunnel.plist`
  (форварды 9119→VPS:9119, 8742→VPS:8642).

### 2. Каша маршрутизации — УСТРАНЕНА
- Убран жёсткий `profile_routes` (chat 176203333 → batrak) из root `config.yaml`.
  Из-за него все боты летели в Батрака.
- Почищен stale-сеанс `agent:main:telegram:dm:176203333` в `state.db`
  (убрал фантомные «femida» в ответах ботов).
- Итог (verified по `gateway.log`):
  - @sher03132 → sherlock ✅
  - @market03132 → marketer ✅
  - @finans03132 → financier ✅
  - @femida03132 → femida ✅
  - @batrak03132 → batrak ✅
  - @hermes03132 → personal (НО как `main`, см. ниже) ⚠️

### 3. personal НЕ сделан именованным (решено оставить)
- Попытка убрать root-токен, чтобы @hermes03132 шёл в `agent:personal` —
  НЕ удалась (personal не поднялся, бот перестал отвечать). Откатили.
- Причина: `profiles/personal/config.yaml` имеет `gateway.telegram.enabled: false`.
- Функционально НЕ баг: personal отвечает персоной из SOUL.md. Разница только
  в имени адаптера в логе. Игорь решил оставить как есть.

## Важные уроки зафиксировать
- Бот ВРЁТ про свой конфиг («забинден на femida») — это галлюцинация модели.
  Истина — `gateway.log` (строка `agent:<профиль>:telegram:...`).
- Логи gateway — в файле `/root/.hermes/logs/gateway.log`, НЕ в journald.
- ТГ с VPS ходит ТОЛЬКО через US-прокси (не `--noproxy`).
- OmniRoute на VPS мёртв, но боты не зависят (ходят на opencode.ai/zen/v1).

## Файлы
- `handoff_2026-08-29_vps_bots_fix.md` — SSoT по этой сессии (маршрутизация).
- `handoff_2026-08-29_vps_bots_setup.md` — база (6 ботов, мост).
- Бэкапы на VPS: `config.yaml.bak_1788001416`, `state.db.bak_1788001053`.

## ДОБИТО (сессия 29.08, продолжение) — VPS-доступ + nginx ⚠️

По `handoff_2026-08-29_vps_bots_fix.md` докатали меню-свитчер (сделан в
прошлой части сессии). Потом вскрылась новая проблема доступа к VPS.

- **Root-cause блока SSH:** внутренний ufw VPS стоял `policy DROP` и пускал
  только старый диапазон `91.78.5.0/24`. Домашний IP Игоря
  `95.154.153.47` (сменил мобильный→домашний роутер) не был в ufw.
- **Исправлено в VNC-консоли TimeWeb:** `ufw allow from 95.154.153.47 to
  any port 22/2222 proto tcp` (подтверждено `ufw status`). TimeWeb FWaaS —
  правила на 22/2222 для 95.154.153.47 тоже добавлены.
- **ПРОБЛЕМА:** с Мака по SSH на конец сессии ещё не прошло (`nc 22`
  BLOCKED). Причины проверить в след. сессии: (1) домашний IP снова
  сменился (динамический) → `dig +short myip.opendns.com`; (2) TimeWeb FWaaS
  не применил правило (нажать «Применить»); (3) роутер режет исходящий 22.
- **⚠️ КРИТИЧНО — nginx.conf на диске ИСПОРЧЕН:** агент вписал невалидный
  `map` в `/etc/nginx/nginx.conf` (потерялись `$` при передаче через ssh).
  Старый nginx-процесс ещё ЖИВ, но при перезагрузке VPS nginx НЕ стартует.
  **БЭКАП ЕСТЬ:** `/etc/nginx/nginx.conf.bak_<ts>`. ВОССТАНОВИТЬ ДО РЕБУТА:
  `cp $(ls -t /etc/nginx/nginx.conf.bak_*|head -1) /etc/nginx/nginx.conf &&
  nginx -t && nginx -s reload`.
- **Дашборд OmniRoute:** доступен в браузере `https://217.149.23.113/omni/`
  (nginx уже проксирует `/omni/`→`127.0.0.1:20131`). Нужно дописать
  корректный `map $http_upgrade` для WS при восстановлении конфига.
- **Канал управления:** VNC-консоль TimeWeb работает БЕЗ SSH/интернета
  Мака — использовать как основной, если SSH не идёт.

См. `handoff_2026-08-29_vps_access_nginx_fix.md` (детально + правильный
блок nginx для WS).

## ПЕРВЫЙ ШАГ ИГОРЯ (след. сессия)
1. НЕ перезагружать VPS, пока nginx.conf не восстановлен из бэкапа.
2. Открыть VNC-консоль TimeWeb ИЛИ (если SSH пошёл) зайти и выполнить
   восстановление nginx.conf из бэкапа + `nginx -t` + reload.
3. Проверить `dig +short myip.opendns.com` на Маке — тот ли IP в whitelist.
4. Проверить дашборд `https://217.149.23.113/omni/` в браузере.

## ДОБИТО (сессия 29.08 вечер, продолжение) — меню-свитчер ПОЧИНЕН ✅

По `handoff_2026-08-29_vps_bots_fix.md` взял незакрытую задачу «починить
меню-свитчер `/batrak`/`/chief` в ТГ».

- **Root-cause (без угадывания, по исходникам Hermes):** плагин
  `hermes-profile-menu` читает chat_id/platform через ContextVar
  `HERMES_SESSION_*`, который gateway проставляет ТОЛЬКО внутри
  `_handle_message_with_agent` (run.py:18979). А slash-команды плагинов
  диспетчатся раньше — в `_handle_message` (run.py:17722), где контекст ещё
  пуст → плагин видел `('','')` и молча возвращал «только внутри ТГ-чата».
- **Фикс:** вокруг вызова `plugin_handler()` в run.py добавлен scoped
  `set_session_vars(source...)` + `clear_session_vars()` в finally, чтобы
  плагин при команде видел реальный platform+chat_id. Плагин не трогал.
- **Бэкап/патч:** `gateway/run.py.bak_<ts>` + git diff
  `/root/.hermes/gateway_run_profile_menu_fix.patch` (откат:
  `git apply -R` на VPS).
- **Проверено:** синтаксис OK, gateway активен, 60 команд в меню, изолированный
  тест подтвердил — contextvar теперь доходит до плагина
  (`('','')` → `('telegram','176203333')`).
- **НЕ проверено автоматически (честно):** реальный E2E невозможен ботом
  (он не получает собственные sendMessage как входящие). Игорю нужно у
  `@hermes03132_bot` нажать `/sherlock` → ждать «✅ Переключено: 🔍 Шерлок».
- Мост Mac→VPS зелёный (проверено `check_bridge.sh`).

См. раздел «ДОБИТО» и «ПЕРВЫЙ ШАГ ИГОРЯ» в
`handoff_2026-08-29_vps_bots_fix.md`.

## ДОБИТО (сессия 30.08 вечер) — настройка всех профилей на free-модель (Nous laguna)

**Задача Игоря:** все профили Hermes + 6 ТГ-ботов → бесплатная модель по
умолчанию (Nous free), платные — только в конце каскада. Исходный пост Игоря
содержал ГАЛЛЮЦИНИРОВАННЫЕ токены (MacBah, ROMBOX, Mantime, REO, «Verein, wer
Server-Omniroute hat») — агент их НЕ применил, работал по реальным конфигам.

### Корневая ошибка (потеряно ~2 часа)
- VPS-gateway читает конфиги из **`HERMES_HOME=/srv/hermes/.hermes`**, а НЕ из
  `/root/.hermes`. Почти всю сессию агент правил `/root/.hermes/*` — правки НЕ
  применялись к живому gateway (поэтому бот выдавал `hy3-free`/`custom`).
- Найдено по `cat /proc/<pid>/environ` → `HERMES_HOME=/srv/hermes/.hermes`.

### Что реально сделано (в `/srv/hermes/.hermes`)
- Все профили (batrak/bridge/english-tutor/hermes/personal/sherlock/defender/
  marketer/financier/health/femida) + root `config.yaml` →
  `model.provider: omniroute`, `model.default: nous/poolside/laguna-s-2.1:free`.
- Удалён мусор: `nous/Hermes-4-70B/405B` (несуществующие), запрещённый
  `openrouter/stealth/ox-alpha` (ES-28), платные `deepseek-v4-flash-free`,
  `openrouter/google/gemini-3.7-flash`, `auto/free-coding`, `auto/best-coding`,
  `hy3-free`. MOA-агрегаторы переведены на laguna.
- Ранее (в начале сессии) починен коннект VPS-gateway: возвращён валидный токен
  `882055` (`@hermes03132`, getMe=True), убран мёртвый `895390` (rejected by
  server) из femida `.env`, femida убран из VPS-multiplex (живёт на Маке).
- Gateway перезапущен (процесс 849452), в свежем логе 0 rejected / 0
  «not supported». Бэкапы: `*.bak_1788108744` в `/srv/hermes/.hermes`.

### Мак (дашборд :9120, /Users/igorvasin/.hermes)
- Тоже пришит `nous/poolside/laguna-s-2.1:free` во все 12 профилей + root
  (бэкапы `*.bak_1788108426`). Дашборд показывал stale `hy3-free` — обновляется
  после Restart Gateway / перезагрузки страницы.

### Проверено / не проверено (честно)
- ✅ VPS-OmniRoute жив (`2223→VPS:20128`, /v1/models=200), `laguna-s-2.1:free`
  отвечает адекватно («I'm poolside Malibu»).
- ✅ Токен `882055` валиден, gateway active, `@hermes03132` коннектится.
- ⚠️ Качество ответа free-модели: `laguna-s:free` на сложных/наводящих промптах
  галлюцинирует (ахинея про «RPM-пакеты Neous»). Это ограничение free-слоя, не
  баг конфига. Для серьёзных задач (Фемида-юр) нужна платная модель — вне
  политики free-only Игоря.
- ⚠️ VPS-OmniRoute иногда ловит transient 429 на free-моделях (лимиты).

### УРОК (зафиксирован в memory)
VPS-gateway конфиги = `/srv/hermes/.hermes`, НЕ `/root/.hermes`. Перед правкой
всегда править `/srv/hermes/.hermes/{config.yaml,profiles/*/config.yaml`.

### ПЕРВЫЙ ШАГ ИГОРЯ
1. Написать `@hermes03132_bot` — должен ответить на laguna (в заголовке сессии
   `Model: nous/poolside/laguna-s-2.1:free`).
2. Если дашборд Мака (:9120/Profiles) показывает старое — нажать Restart Gateway
   или перезагрузить страницу.
3. Если ахинея повторяется — сообщить; либо смотрим системный промпт, либо
   обсуждаем платную модель для тяжёлых профилей.
