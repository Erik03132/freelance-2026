# OmniRoute — рецепты диагностики (Hermes ↔ OmniRoute)

## 1. Живой ли процесс / порты
- `ps aux | grep omniroute` → процесс `node …/omniroute`, v3.8.48 (LaunchAgent `com.user.omniroute`).
- Слушает: `20128` (API+Dashboard), `20131`, `20132` (внутренние).
- Проверка: `curl --noproxy '*' -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:20128/v1/models` → `200`.
- Список моделей: `…/v1/models` → ~1083 шт. (включая `auto/free-coding`, `auto/coding:free`, `auto/best-free`).

## 2. Тестируем комбо чат-запросом (как Hermes)
Реплицируем окружение gateway Hermes (оно ИМЕЕТ NO_PROXY, поэтому localhost идёт напрямую):
```bash
curl --noproxy '*' -m 60 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer x" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"hi"}],"max_tokens":30,"stream":true}'
```
- Дошёл до `[DONE]` → комбо живо.
- `http_code=000` + `SOCKS5 error (2)` → забыл `--noproxy '*'` (curl ушёл в прокси). Не путать с поломкой OmniRoute.

## 3. Читаем ошибки комбо (почему рвётся стрим)
Логи запросов: `~/.omniroute/call_logs/YYYY-MM-DD/*.json` (один файл на запрос).
Полезное: `request.model`, `error`, `responseBody`.
```bash
D=$(date +%F); for f in ~/.omniroute/call_logs/$D/*.json; do
  python3 -c "import json,sys;d=json.load(open('$f'));print(d.get('error'))" 2>/dev/null
done | sort | uniq -c
```
Типичные `[401]/[400]/[404]/[429]` → см. таблицу в SKILL.md (раздел «Диагностика»).
Мёртвые звенья, найденные 2026-08-19: `pollinations/*` (401 нет ключа),
`oc/qwen3.6-plus-free` (401), `ddgw/gpt-4o-mini` (400), `orcarouter/*` (404 no creds), `Console` (429).

## 4. Circuit-breaker / resilience
```bash
omniroute resilience status          # closed/open/half-open по провайдерам
```
Стратегии комбо переключаются в Dashboard → Combos (`round-robin` ↔ `failover`).
Для free-каскада лучше `failover` + агрессивный cooldown, чтобы мёртвые звенья быстро выпадали.

## 5. ПРОВЕРКА КОМПРЕССИИ (гипотеза «экономия токенов»)
OmniRoute сжимает прозрачно ВЕСЬ трафик до отправки upstream (input + output).
Эхо в ответе: заголовок `X-OmniRoute-Compression: <mode>; source=<source>`
(`off; source=request-header`, `stacked; source=default`, …).

**Выключить сжатие на один запрос** (для A/B):
```bash
curl … -H "x-omniroute-compression: off" …
```

**Телеметрия реальной экономии** (SQLite OmniRoute):
```bash
sqlite3 -readonly ~/.omniroute/storage.sqlite \
  "SELECT model, tokens_before, tokens_after, round(ratio,3), source \
   FROM compression_run_telemetry ORDER BY id DESC LIMIT 10;"
```
Поле `ratio` — реальный коэффициент сжатия (1.0 = НЕ сжалось).

### A/B тест на сохранение смысла (проверено 2026-08-19)
Метод: один и тот же «хрупкий» промпт (точные числа, даты, SQL FK, URL, код) гоняем
со сжатием (default) и с `x-omniroute-compression: off`; проверяем, дошли ли литералы
дословно до модели и корректен ли ответ.
- **Результат:** при включённом `stacked` все хрупкие литералы (`12847`, `983245.57`,
  `2023-04-12T08:33:21Z`, `ON DELETE CASCADE`, URL, `NUMERIC(10,2)`, `JSONB`, `timestamptz`)
  сохранились дословно → смысл НЕ испортился. Риск порчи минимален (код/URL/числа защищены).
- **НО важнее:** в текущей конфигурации сжатие ФАКТИЧЕСКИ НЕ РАБОТАЕТ — telemetry показывает
  `ratio=1.0` на ВСЕХ прогонах, даже на промпте в 18338 токенов. То есть экономии токенов
  сейчас НЕТ; компрессию надо реально включить/настроить в Dashboard (adaptive dial /
  active profile / понизить порог auto-trigger), иначе весь выигрыш от завода внешнего
  провайдера (напр. Nous) через OmniRoute — нулевой (плюс добавленная latency локального хопа).
- На коротких промптах (<~200 токенов) сжатие точно не срабатывает (ниже порога auto-trigger).

## 6. Завести внешний провайдер (напр. Nous) внутрь OmniRoute
Nous — OpenAI-совместимый (`https://inference-api.nousresearch.com/v1`).
Dashboard → Providers → Add → Custom/OpenAI-compatible: Base URL + API key.
Ключ тянется из той же `OMNI_API_KEY` env (если она же = Nous-ключ).
Убедиться, что compression ON для этого провайдера, иначе экономии не будет.
Переключить Hermes на него: `model.provider: omniroute`, `base_url: http://127.0.0.1:20128/v1`,
`default: <combo-или-nous/model>`. Делать на СВЕЖЕЙ сессии (mid-conversation switch ломает сессию).
