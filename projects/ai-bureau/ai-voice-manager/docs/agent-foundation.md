# Agent Foundation — финишные настройки голосового агента (база AVM ← Levitan)

> **SSoT (код):** `projects/levitan/agent/levitan_agent.py` + `projects/levitan/agent/funnel.py`.
> Этот документ — справочный снимок финальных настроек агента, перенесённый из
> проекта Levitan как базовая основа для AVM. Код НЕ дублируем (правило `CLAUDE.md`:
> стек только в Levitan). При изменении настроек — править в Levitan, здесь держать
> синхронный снимок.
>
> **Снимок от 15.08 (состояние незакоммичено в Levitan, тест OK):** крупный рефактор —
> fast-path вынесен в `funnel.py`, добавлен preempt по interim ASR.

## 1. Архитектура (ключевые решения, перенесено из Levitan)

- **Fast-path вынесен в отдельный модуль `funnel.py`** (чистый stdlib, без livekit/LLM).
  Экспортирует: `_fast_path_reply_text(text, llm_obj)`, `_fast_path_reply(chat_ctx, llm_obj)`,
  `_price_for_qty`, `_qty_from_text`, `normalize`, `_phone_from_text`, `_fmt_phone_spoken`,
  плюс `save_lead_fn` (ленько биндится из `levitan_agent.py` во избежание circular import).
  **`funnel.py` — SSoT для AVM-2**: переиспользуемый детерминированный слой без LLM.
- **Конфигурация fast-path — `funnel_config.json`** (рядом с `funnel.py`): `price_tiers`
  (ступенчатая шкала) + `regex` (`neg_full`, `delivery_confirm`, `pos_full`, `quantity`).
  **Это интерфейс подстройки под клиента в AVM-2** — меняем цены/паттерны в JSON, код не трогаем.
- **Preempt-генерация по interim ASR** (новое, 15.08): в `_on_transcribed` при
  `not ev.is_final` и невзведённом `_preempt_lock` вызывается `_fast_path_reply_text(ev.transcript, …)`
  по ЧАСТИЧНОМУ распознаванию. При совпадении — `session.say(reply, allow_interruptions=True)`
  ДО финала транскрипта → ещё ниже `resp_lat`. Блокировка дубля: `_preempt_lock` /
  `llm._preempt_fired`; сброс при `_on_user_state == "speaking"` (новый ход клиента).
  В `DebugLLMStream._first_or_fallback` при `_preempt_fired` LLM-стрим шунтируется (ответ уже отдан).
- **Streaming TTS**: `StreamAdapter(tts=YandexTTS(streaming=False), sentence_tokenizer=tokenize.basic.SentenceTokenizer(retain_format=True))`.

## 2. Тюнинг-параметры (финальные, 15.08)

| Параметр | Значение | Примечание |
|---|---|---|
| `endpointing.min_delay` | 0.2 | без изменений |
| `endpointing.max_delay` | 0.4 | без изменений |
| LLM primary | `deepseek/deepseek-chat` (env `LLM_MODEL`, default) | было `opencode-go/minimax-m3`; фактическая модель — из env |
| LLM fallback | env `LLM_FALLBACK_MODEL` | |
| `LLM_BASE` / `OPENAI_BASE_URL` | OmniRoute (`http://127.0.0.1:20128/v1` на VPS) | |
| `max_completion_tokens` | 600 | без изменений |
| `temperature` | 0.3 | без изменений |
| TTS | Yandex `alena`, `streaming=False` + StreamAdapter | |
| STT | Deepgram `nova-3` (ru), **`interim_results=True`** | включён для preempt |
| `allow_interruptions` | False (агент), True (preempt `say`) | |
| `TTS_LEAD_SILENCE_SEC` | 2.5 | (.env на VPS) |
| Приветствие | 5с тишина перед `say(GREETING)` | Mango режет аудио до ответа |

## 3. Fast-path правила (детерминированные, ветки — SSoT `funnel.py`)

| Триггер (нормализованный текст) | Ответ агента | Побочный эффект |
|---|---|---|
| НЕТ (`^нет`/`отказ`, ≤2 слова) — ДО доставки | «Спасибо за внимание, всего хорошего!» | завершение |
| ДА (`^да`/`ну да`/`да ладно`/`конечно`/…) — ДО количества | «Отлично! Сколько голов вам нужно?» | `_asked_quantity=True` |
| КОЛИЧЕСТВО (число/словами) — после вопроса | «Для N голов цена P рублей за голову. Место доставки цыплят прежнее?» | P по шкале; фиксирует `_last_qty` |
| ДА после «Место доставки прежнее?» | «С вами свяжется менеджер для уточнения заказа, всего хорошего!» | `save_lead` (фон) |
| НЕТ на вопросе доставки | (отдаётся LLM) | клиент меняет адрес |
| Первый ход — приветствие (`алло`/`здравствуйте`, без ДА) | «Здравствуйте! Это Азовский инкубатор…? Вам интересно?» | детерминированно, без LLM |
| Первый ход — **вопрос** (`?` / сколько / какой / где / когда …) | (отдаётся LLM / заглушка) | вопрос не игнорируется приветствием |

- Детектор количества: `_qty_from_text` — цифры + суффикс `голов|цыпл`, иначе `_text_to_digits`
  (русские числительные: «двести пятьдесят шесть» → 256).
- Все паттерны и шкала цен — в `funnel_config.json` (см. §3.1).
- **Preempt:** то же самое срабатывает на interim (нефинальном) транскрипте — агент
  начинает говорить ещё до того, как ASR завершил фразу клиента.

### 3.1 `funnel_config.json` — интерфейс KB для AVM-2

```json
{
  "price_tiers": [
    {"min": 1000, "price": 75},
    {"min": 301, "price": 80},
    {"min": 101, "price": 85},
    {"min": 0,   "price": 90}
  ],
  "regex": {
    "neg_full": "(нет|не надо|не интересно|не хочу|отказ[а-я]*)",
    "delivery_confirm": "\\b(да|прежнее|подтверждаю|верно|точно|правильно|хорошо)\\b",
    "pos_full": "(да|да да|конечно|интересно|беру|хорошо|ну да|да интересно|да ладно|ну конечно)",
    "quantity": "(\\d+)\\s*(?:голов|цыпл)"
  }
}
```

**Для AVM-2** этот JSON генерируется из KB клиента (цены услуг, триггеры ДА/НЕТ под нишу).
Код агента не меняется — только конфиг. Ступенчатая шкала в примере — образец
(бройлеры); реальная берётся из KB клиента (демо-конвейер).

## 4. Шкала цен (детерминированная, `_price_for_qty`) — пример воронки Levitan

| Объём (голов) | Цена за голову |
|---|---|
| до 100 | 90₽ |
| 101–300 | 85₽ |
| 301–999 | 80₽ |
| от 1000 | 75₽ |

Общую сумму агент НЕ считает (её даёт менеджер). Для AVM эта шкала — образец;
реальная берётся из KB клиента (демо-конвейер).

## 5. SYSTEM_PROMPT (финальный, ~450 токенов, пример IncuBird)

Роль (AI-менеджер инкубатора), компания/ассортимент/доставка, шкала цен, типовые
вопросы (отвечать по фактам, без поиска), стиль (коротко, 1-2 предложения), воронка
(алло→ДА→количество→доставка→финал), финальная фраза ОДНИМ предложением.
Полный текст — в `projects/levitan/agent/levitan_agent.py` (SYSTEM_PROMPT).
**Для AVM-2 промпт параметризуется из KB клиента** (название, услуги, прайс, график).

## 6. Результаты измерений (голос, 15.08, проект Levitan)

- Продающий диалог по fast-path БЕЗ единого вызова LLM: `avg_resp_lat = 4.9s` (было 8.4s baseline).
- **Preempt по interim ASR** (15.08) дополнительно снижает `resp_lat` — агент начинает
  отвечать ещё до финала распознавания клиента.
- Дублей нет (шунт LLM-ноды при `_preempt_fired` + единый fast-path в `funnel`).
- Edge-case «Нет, другое» (смена города) → LLM, логика сохранена.

**Связь с гейтом AVM-0:** «немые звонки» (лид-тишина >5с) устранены — fast-path +
preempt дают мгновенный ответ; TTFT на LLM-ходах ~2s. Гейт практически закрыт со
стороны задержек; остаток — STT + сеть OmniRoute (AVM-0b — нагрузочная стабильность).

## 7. Состояние кода (эталон, проект levitan)

Незакоммичено на 15.08 (тест OK), снимок для AVM:
- `agent/funnel.py` (новый, untracked) — SSoT fast-path, чистый stdlib, конфиг из `funnel_config.json`.
- `agent/funnel_config.json` (новый, untracked) — price_tiers + regex.
- `agent/levitan_agent.py` (modified): импорт `funnel`, preempt по interim ASR, `interim_results=True`,
  `_preempt_lock`/`_preempt_fired`, бинд `funnel.save_lead_fn = save_lead`.

Предыдущие релевантные коммиты (baseline):
- `908196a1` prompt ~2k→~450 tok, max_completion 2500→600
- `c337042a` endpointing 1.2→0.4
- `3420d52b` количество→цена (детерминированная шкала)
- `2828bcae` fast-path ДА/НЕТ + доставка в слое LLM
