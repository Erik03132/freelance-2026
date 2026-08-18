# Эксперименты: сокращение задержек голосового агента (2026-08-15)

**Якорь отката:** `git tag voice-stable-20260814` → `908196a1` (стабильный Levitan-агент).
Правило: каждый пункт — код → тест (голосовой звонок + bench) → при провале откат на якорь.

## Порядок и статус

| # | Пункт | Статус | Тест | Откат |
|---|-------|--------|------|-------|
| 0 | Якорь отката установлен (tag + voice-stability на VPS) | ✅ | — | — |
| AVM-0b | Каскад LLM без 402/обрыва под нагрузкой | ⏳ ждёт VPS | `scripts/bench_cascade.py` (n=12, conc=12) на VPS | tag |
| #2 | Воронка → data-файл (переиспользуемый funnel) | ✅ | unit-тесты 14/14 ✅, ruff ✅; голосовой тест ✅ (пользователь подтвердил диалог) | tag + rm funnel* |
| #3 | Preemptive generation (LLM на частичном распознавании) | ✅ | голосовой тест ✅ (PREEMPT на interim зафиксирован в логах) | tag |
| #4 | Realtime S2S (Gemini Live / OpenAI Realtime) | ⏳ | голосовой тест + метрика <500ms | tag |

## Что сделано локально (до возврата VPS)
- `agent/funnel.py` — SSoT детерминированной логики (normalize, _price_for_qty, _qty_from_text,
  _extract_quantity, _phone_from_text, _fmt_phone_spoken, _fast_path_reply) + `_load_config()`.
- `agent/funnel_config.json` — данные воронки (ценовые ступени, паттерны ДА/НЕТ/количество).
- `tests/test_funnel.py` — 10 unit-тестов fast-path без LLM (все проходят).
- `scripts/bench_cascade.py` — AVM-0b нагрузочный бенч (готов к запуску на VPS).
- `levitan_agent.py` переключён на импорт из `funnel` (поведение идентично, py_compile + ruff OK).

## #2 и #3 — РЕЗУЛЬТАТЫ (2026-08-15 ~11:42 UTC)

### #2 (воронка → data-файл) — ✅
- `agent/funnel.py` (SSoT: normalize, _price_for_qty, _qty_from_text, _extract_quantity,
  _phone_from_text, _fmt_phone_spoken, _fast_path_reply/_fast_path_reply_text) + `agent/funnel_config.json`.
- Голосовой тест (номер 79859234644): ДА → «Сколько голов?» → «567» → «Для 567 голов цена **80₽**
  за голову. Доставка прежняя?» (тир 301–999 → 80₽, верно) → ДА → лид сохранён + прощание.
  Весь путь по fast-path, **без LLM**. Пользователь подтвердил: «звонок пришёл-диалог есть-ок».
- unit-тесты 14/14 ✅, `ruff check` чисто.

### #3 (preemptive generation на interim ASR) — ✅
- Включён `deepgram.STT(interim_results=True)`; в `_on_transcribed` по `is_final=False` вызывается
  `_fast_path_reply_text(ev.transcript, llm)` и при совпадении агент **говорит сразу** (до финала),
  ставит `_preempt_fired` → LLM-нода в `DebugLLMStream._first_or_fallback` шунтируется (пустая
  генерация, без дубля). Сброс блока — на `user_state_changed=="speaking"`.
- Голосовой тест: зафиксированы маркеры `[FAST] PREEMPT` на interim:
  - interim «Да, интересно.» (final=False) → «Отлично! Сколько голов вам нужно?»
  - interim «Пятьдесят семь.» (final=False) → «Для 57 голов цена **90** рублей за голову…» (57≤100 → 90₽, верно).
- Эффект: ответ начинается по частичному распознаванию, исключается ожидание endpointing+финала
  (снижение `resp_lat` на величину задержки финализации). Точную метрику мешает нерегламентированная
  речь тестера («Алло» между репликами) — нужен чистый замер на скриптовом диалоге.
- unit-тесты `_fast_path_reply_text` (да / количество / подтверждение доставки / не-триггер) добавлены.

## Блокер
VPS `217.149.23.113` после ребута недоступен по всем портам (22/20128/7880/8081) с хоста агента.
Нужно подтверждение, что бокс реально поднялся и SSH доступен (IP/порт не изменились ли).

## AVM-0b — РЕЗУЛЬТАТ (2026-08-15, 10:4x UTC)
**FAIL (обнаружен продакшн-блокер).** VPS поднят (через web-консоль провайдера: `systemctl enable --now ssh`),
порты 22/20128/7880/8081 слушают. Но LLM-каскад мёртв:
- OmniRoute (20128, node) шлёт в OpenRouter с ключом `sk-or-v1-8508…` → **502 «Insufficient credits»**.
- `omni-auto-router` (20129) тоже роутит в OpenRouter с тем же/пустым ключом → таймаут.
- Прямая проверка OpenRouter (через US-прокси) двумя ключами: `sk-or-v1-8508…` (insufficient credits)
  и `OPENROUTER_API_KEY` из root `.env` (**403 Key limit exceeded**) — оба мертвы.
- **Рабочий бэкенд найден:** Gemini `gemini-2.5-flash` через US-прокси
  (`HTTP_PROXY=Q3NeJXTY:…@172.120.21.141:64468`) отвечает корректно («4» на 2+2),
  принимает `reasoning_effort:"none"`. GEMINI_API_KEY из root `.env` валиден.

**Вывод:** чтобы продолжить тесты (#2/#3/#4 затрагивают LLM-повороты), нужно временно направить
агента напрямую на Gemini (LLM_BASE=`https://generativelanguage.googleapis.com/v1beta/openai`,
LLM_MODEL=`gemini-2.5-flash`, KEY=`GEMINI_API_KEY`, PROXY=US) в обход мёртвого OmniRoute.
Откат — вернуть env в systemd-сервисе на OmniRoute после пополнения OpenRouter.
Fast-path воронки (ДА/НЕТ/количество/доставка) работает БЕЗ LLM — его можно тестить и сейчас.

### Уточнение после переключения агента на Gemini (11:24 UTC)
- Агент перезапущен на Gemini (service-файл забэкаплен: `levitan-agent.service.bak_gemini_20260815`).
- AVM-0b повторён: **гейт 402/обрыв/connection = 0 → PASS**. Но успешность низкая:
  - `gemini-2.5-flash` → **429 «exceeded your current quota»** (free-квота быстро кончается).
  - `gemini-2.0-flash` → 404 (модель недоступна), `gemini-1.5-flash` → 404, `gemini-flash-latest` → EMPTY.
  - Т.е. Gemini пригоден для ОДИНОЧНЫХ вызовов (проверено: «4» на 2+2), но не под нагрузкой/нестабилен по квоте.
- Корень проблемы: бесплатный каскад OmniRoute строится на `opencode-provider` (для `opencode-go/minimax-m3`)
  и OpenRouter. OpenRouter мёртв (кредиты), а `opencode-provider` НЕ отрабатывает (нужен endpoint/ключ —
  см. `/usr/lib/node_modules/omniroute/@omniroute/opencode-provider`, требует `apiKey`+`endpoint`),
  поэтому OmniRoute валится в мёртвый OpenRouter → 502. На VPS крутится ollama (127.0.0.1:11434) и
  дублирующийся omniroute (pid 1015 от systemd падает EADDRINUSE, порт держит orphan pid 1107 v16.2.12).
- **Статус LLM на данный момент:** ни OpenRouter, ни Gemini(kвота), ни opencode-provider не дают
  стабильного бэкенда. Нужно действие пользователя: либо поднять/починить `opencode-provider`
  (дать endpoint/ключ Open Code), либо пополнить квоту OpenRouter/Gemini.

## AVM-2b — #2 revert + детерминированное приветствие VERIFIED (2026-08-15 ~13:05 UTC)
**PASS (голосом подтверждено пользователем: «приветствие ок, диалог ок»).**
- Откат #3 (preempt/interim/filler) → #2: `funnel.py` вернул оригинальный `_fast_path_reply(chat_ctx, llm)`,
  убраны `_fast_path_reply_text`/filler/`_preempt_lock`/`_preempt_fired`; `levitan_agent.py` — убраны
  `interim_results`, preempt-блок, восстановлено вооружение `_asked_delivery` в `_on_item`.
- **Правка:** открывающее приветствие сделано детерминированным fast-path (первый ход, `not _asked`
  → каноническое «Здравствуйте! Это Азовский инкубатор, вас интересуют суточные цыплята породы Росс-308?
  Вам интересно?» без LLM). Root cause «обрезано приветствие + задержки»: приветствие генерил LLM (Gemini)
  ~21с и длинный текст обрывался barge-in. Теперь играет полностью и быстро.
- Метрики звонка: `resp_lat=[2.9, 6.9, 4.7]` (TTS/пайплайн, не LLM). Fast-path turn-ы мгновенны (`[FAST] LLM bypass`).
- Деплой: репозиторий **приватный** → raw 404 без токена; заливали через временный **public gist** +
  `curl` в web-консоль ВМ (SSH с хоста агента заблокирован внешним фаерволом провайдера:
  `connection refused` на :22/:20128; внутри ВМ sshd слушает, ufw разрешает).
- Committed `ad1ae6eb` (branch `levitan-revert-2`). 11 unit-тестов `test_funnel.py` PASS.
- **Открытый вопрос надёжности:** периодический даун ВМ — диск почищен (89%→74% journal-vacuum),
  но root cause (OOM / ребуты гипервизора) НЕ подтверждён (нет `last reboot`/`dmesg oom`);
  хост снаружи недоступен (только web-консоль). Задача каскада серверов отложена до доступа/данных.
