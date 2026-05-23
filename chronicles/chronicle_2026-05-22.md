# 📅 Хроника дня — 22 мая 2026

## 🎙️ Автодозвон: голос Kore (Gemini TTS) через Mango + baresip

### Что сделано

| Время | Событие |
|-------|---------|
| 11:30 | Начали подбор голоса — Supertonic F5 не понравился |
| 11:34 | Нашли техрадар — 3 голосовых сервиса (Gemini TTS, Zvonok, VoxCPM2) |
| 11:38 | Сгенерировали 3 голоса Gemini TTS через US-прокси: **Kore**, Puck, Charon |
| 11:43 | Прослушали все 3 — **Kore выбран** (женский, нейтральный) |
| 11:47 | Первая попытка звонка — DNS сломан (SOCKS-прокси подменил DNS на 169.254.113.53) |
| 12:03 | Починили DNS: `sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 1.1.1.1` |
| 12:04 | Звонок прошёл, но без голоса (401 на upload — файл нужно грузить вручную в ЛК) |
| 12:17 | Загрузили `confirm_call_kore.mp3` в ЛК Mango (Аудиофайлы) |
| 12:18 | Callback через ext 25 — звонок менеджеру (ошибка!) |
| 12:37 | Обнаружили: **baresip на VPS** (72.56.38.19) — SIP-бот, авто-ответ, `/tmp/mango_play.wav` |
| 12:37 | Загрузили Kore.wav на VPS, конвертировали в 8kHz PCM для baresip |
| 12:43 | Перезапустили baresip → `200 OK` регистрация в Mango |
| 12:56 | Разобрались: ext 22 = Игорь + SIP-бот, ext 25 = менеджер (НЕ ТРОГАТЬ!) |
| 12:59 | **Голос обрезан** — baresip играет сразу, клиент подключается через 7 сек |
| 12:59 | Добавили 7 сек тишины в начало WAV |
| **13:01** | **✅ РАБОТАЕТ! Полное сообщение Kore слышно!** |

### Архитектура (финальная)

```
Local Mac                          VPS (72.56.38.19)
┌─────────────────┐               ┌──────────────────────┐
│ auto_confirm_    │  callback     │ baresip (SIP-бот)    │
│ call.py          │──→ Mango ──→ │ ext 22 / user4       │
│ (ext 22)         │    Office     │ авто-ответ           │
└─────────────────┘               │ играет mango_play.wav│
                                  │ (7с тишина + Kore)   │
        Mango                     ├──────────────────────┤
        соединяет                 │ mango-webhook (PM2)  │
        ↓                        │ порт 8085            │
  +79859234644                    │ ловит DTMF           │
  (клиент слышит Kore)            └──────────────────────┘
```

### Ключевые файлы
- `agent/auto_confirm_call.py` — скрипт звонка (ext 22, без прокси)
- `agent/tts_cache/gemini_voices/Kore.wav` — оригинал голоса (24kHz)
- `agent/tts_cache/confirm_call_kore.mp3` — версия для ЛК Mango
- VPS `/tmp/mango_play.wav` — версия для baresip (8kHz + 7с тишины)
- VPS `/root/.baresip/accounts` — SIP-конфиг user4
- VPS `/opt/mango_webhook.py` — webhook сервер (PM2: mango-webhook)

### Грабли
1. **SOCKS-прокси ломает DNS** — `load_dotenv` ставит HTTPS_PROXY в os.environ → нужно `os.environ.pop()`
2. **Mango upload API = 401** — файлы грузить ТОЛЬКО через ЛК (веб-интерфейс)
3. **ext 25 = менеджер** — НИКОГДА не использовать для тестов!
4. **baresip начинает играть сразу** — нужно 7 сек тишины в начале WAV
5. **baresip регистрация протухает** — перезапускать если нет входящих

### TODO
- [x] ~~🔧 **DTMF** — настроить приём нажатий 1/0~~ ✅ РАБОТАЕТ!
- [ ] Интеграция DTMF → Bitrix24 (привязка deal_id к звонку)
- [ ] Голосовое распознавание (ДА/НЕТ через STT)
- [x] ~~Автоперезапуск baresip через PM2~~ ✅ baresip-watchdog v1.1 (PM2 id:13)

---

## 🔢 DTMF — перехват нажатий (18:16–19:01)

### Что сделали
1. Создали `dtmf_handler.py` — HTTP-сервер (порт 8086), принимает DTMF, обновляет Bitrix24
2. Создали `dtmf_monitor.py` — мониторит screen baresip каждые 0.5с, парсит `received event`
3. Починили baresip — добавили `g711.so` + `account.so` (были 0 audio codecs)
4. Задеплоили оба на VPS через PM2

### Полный тест: ✅ УСПЕХ
```
19:00 → Звонок на +79859234644
     → baresip авто-ответ → Kore голос → клиент нажал 1
     → baresip: "received event: '1' (end=1)"  
     → dtmf-monitor: "🔢 DTMF обнаружен: '1' от 79859234644"
     → dtmf-handler: "✅ ПОДТВЕРЖДЕНО: 79859234644 (action=confirmed)"
```

### Новые компоненты на VPS (PM2)
| Процесс | Порт | Назначение |
|----------|------|-----------|
| `dtmf-handler` | 8086 | HTTP-сервер, обрабатывает DTMF → Bitrix24 |
| `dtmf-monitor` | — | Парсит screen baresip → шлёт на handler |
| `mango-webhook` | 8085 | Webhook Mango (call/summary/recording) |

### Грабли
6. **baresip без g711.so = 0 audio codecs** — обязательно `module g711.so` + `account.so`
7. **Python requests таймаутит на Mango** — curl работает, requests нет → вызывать через VPS
8. **sndfile enc vs dec** — enc = наш голос, **dec = голос клиента** (нужен для STT!)
9. **screen обрезает строки** — `terminated (duration: 22 secs)` разбивается на 2 строки → нужен 2-фазный regex

---

## 🎤 STT — распознавание голоса ДА/НЕТ (19:02–19:16)

### Что сделали
1. Установили `faster-whisper` (tiny, 40MB) на VPS
2. Добавили `sndfile.so` в baresip — запись входящего аудио (dec.wav)
3. Обновили `dtmf_monitor.py` → DTMF+STT Monitor:
   - Если DTMF не нажат → ищет dec.wav → Whisper STT → classify ДА/НЕТ
4. Добавили **бипер** (800Hz, 0.5с) после голоса Kore — сигнал "говорите"
5. WAV: 7с тишина + 13.5с Kore + 0.5с БИП + 10с для ответа = **31.4с**

### Тест: ✅ УСПЕХ
```
📞 Звонок → Kore говорит → БИП → клиент говорит "Да"
     ↓
📁 /root/dump-*-dec.wav (голос клиента, 25.9с)
     ↓
🔇 VAD убрал 24.9с тишины → ~1с речи
     ↓
🎤 Whisper: "Капа, горы, да?" (2.3с обработка на 1 CPU)
     ↓
✅ Классификатор: найдено "да" → ПОДТВЕРЖДЕНО (digit=1, source=stt)
```

### Архитектура (финальная)
```
VPS (72.56.38.19)
┌──────────────────────────────────────────┐
│ baresip (SIP-бот, screen: sip_bot)       │
│  ├── авто-ответ → играет mango_play.wav  │
│  ├── sndfile → пишет dec.wav (клиент)    │
│  └── DTMF events в консоль              │
├──────────────────────────────────────────┤
│ dtmf-monitor (PM2)                       │
│  ├── парсит screen каждые 0.5с           │
│  ├── DTMF: received event → handler      │
│  └── STT: dec.wav → Whisper → handler    │
├──────────────────────────────────────────┤
│ dtmf-handler (PM2, порт 8086)            │
│  ├── DTMF/STT → Bitrix24 стадия сделки  │
│  └── Telegram уведомление               │
├──────────────────────────────────────────┤
│ mango-webhook (PM2, порт 8085)           │
│  └── call/summary/recording от Mango     │
└──────────────────────────────────────────┘
```

---

## 🧠 Умный каскад LLM v2 (17:47)

### Что сделали
Заменили плоский каскад (deepseek → claude → moonlight → free) на **маршрутизацию по сложности запроса**.

### Тиры

| Тир | Когда | Модели | Цена input/1M |
|-----|-------|--------|---------------|
| 🟢 LITE | FAQ, цены, «привет», «да/нет» | DeepSeek V4 Flash → Free → Qwen 3.6 Flash | $0.11 |
| 🟡 STD | Консультации, RAG, продажи | DeepSeek V4 Pro → Kimi K2.6 → Flash | $0.43 |
| 🔴 PRO | Жалобы, торг, юрлица, сложные | Kimi K2.6 → V4 Pro → Claude Sonnet 4.6 | $0.73 |

### Новые модели в каскаде
- **Kimi K2.6** (`moonshotai/kimi-k2.6`) — $0.73/$3.49, 262K контекст
- **DeepSeek V4 Pro** — $0.43/$0.87, 1048K контекст
- **DeepSeek V4 Flash** — $0.11/$0.22, 1048K (+ бесплатная)
- **Qwen 3.6 Flash** — $0.19/$1.12, 1000K контекст

### Экономия
- ~70% запросов = LITE (FAQ, цены) → $0.11 вместо $0.40
- ~20% = STD → $0.43
- ~10% = PRO → $0.73
- **Средняя: ~$0.17/1M** вместо $0.40 (экономия ~57%)

---

## 🛡️ Автоперезапуск baresip через PM2 (19:57–20:10)

### Что сделали
1. Создали `/opt/baresip_watchdog.sh` v1.1 — bash-скрипт сторож
2. Запускает baresip в `screen -S sip_bot` (совместимость с `dtmf_monitor`)
3. Каждые 10с проверяет: процесс жив? screen жив?
4. При падении — перезапуск с экспоненциальным бэкоффом (5→10→20→40→80→120с)
5. Лимит: 10 рестартов, сброс после 5 мин стабильной работы
6. Добавили `baresip-watchdog` в PM2 (id:13) + `pm2 save`
7. Обновили `ecosystem.config.cjs` локально

### Краш-тест: ✅ ПРОЙДЕН
```
kill baresip → watchdog: ❌ не найден → 5с задержка → перезапуск → SIP 200 OK (9с)
```

### Ключевые файлы
- VPS `/opt/baresip_watchdog.sh` — скрипт сторож
- Локально `ecosystem.config.cjs` — добавлена секция `baresip-watchdog`

### Стоимость: $0 (bash-скрипт, 3.4MB RAM)

---

## 🎨 Артемий v2.0 — Modern Web Guidance (20:11–20:18)

### Что сделали
Фундаментально прокачали SKILL.md Артемия (artemiy-frontend) по Chrome Modern Web Guidance:

### Новые модули знаний

| Область | Что добавлено |
|---------|--------------|
| **CSS Layout** | Container Queries, Subgrid, oklch() colors, text-wrap: balance/pretty, text-box-trim |
| **UI Components** | `<dialog>`, Popover API, CSS Anchor Positioning, `:user-invalid`, field-sizing |
| **Animations** | View Transitions API, `@starting-style`, Scroll-driven Animations (CSS-only) |
| **Performance** | Speculation Rules (prerender/prefetch), `scheduler.yield()`, `content-visibility`, `fetchpriority` |
| **Security** | CSP headers, WebAuthn/Passkeys |
| **Anti-patterns** | Таблица "Legacy → Modern" (12 паттернов замены) |
| **CLI** | `npx modern-web-guidance@latest search/retrieve/install` |

- https://developer.chrome.com/docs/modern-web-guidance
- https://github.com/GoogleChrome/modern-web-guidance-src

---

## 💰 Аудит ночных процессов — оптимизация расходов (20:21–20:28)

### Анализ
Проверили все ночные процессы на VPS и Mac — какие платные, какие полезные.

**541 транскрипт за 14 дней → 0 извлечённых фактов** — call_learner оказался полностью бесполезен. Звонки однотипные (цена/наличие/дата доставки), Анжела и так знает ассортимент.

### Отключены
| Процесс | Где | Причина |
|---------|-----|---------|
| `call_learner` (00:30) | VPS crontab → закомментирован | 0 фактов за 14 дней, пустая трата API-квоты |
| `morning_dream` (07:00) | Mac launchd → unloaded | Повторяющийся анализ хроник, низкая ценность |

### Оставлены (полезные)
- `call_transcriber` (03:00) — нужен для оценки качества звонков
- `call_quality_report` (~03:30) — реальный скоринг менеджеров
- `night_audit` (02:00) — код-ревью
- `habr_digest` (09:05) — бесплатный (без LLM)
- `baresip-watchdog` — бесплатный (bash)

### Восстановление (при необходимости)
```bash
# call_learner — раскомментировать в crontab на VPS
# morning_dream:
launchctl load ~/Library/LaunchAgents/com.antigravity.morningdream.plist
```


---

## 🎓 Сессия прокачки навыков (02:47–03:35)

### Скиллы обновлены

| Скилл | Версия | Что добавлено |
|-------|--------|---------------|
| `code-review-and-quality` | v2.0 | Thermo-nuclear rules из Cursor Team Kit: Code Judo, правило 1000 строк, анти-спагетти |
| `rag-master` | v3.0 | Честный знак + LightRAG + OTUS. Naive→Advanced→ReAct→GraphRAG, RAGAS, диагностика 3 сбоев retrieval |
| `artemiy-frontend` | v2.0 | Modern Web Guidance: oklch, container queries, view transitions, Speculation Rules |

### RAG Анжелы — аудит

- Реальный стек: **Advanced RAG** (ChromaDB + BM25 + гибридный RRF) ✅
- Добавлены: `rerank_with_llm()` и `search_with_rerank()` в `rag_lite.py`
- Тест качества: **100% (5/5)** на базовых вопросах
- База: **6195 чанков** из **18 PDF** по птицеводству

### Анализ 541 транскрипта

| Тип вопросов | Кол-во | Для чего |
|-------------|--------|---------|
| RAG-worthy (птицеводство) | 46 | Тест RAG Recall@5 |
| Цены/наличие | 138 | Тест Анжелы-продавца |
| Логистика | 54 | Тест обработки запросов |
| Жалобы | 21 | Тест тональности |
| Нечёткие | 1849 | Пропустить |

**Вывод**: 541 транскрипт = тест продавца, не RAG.
**GraphRAG**: не нужен для Анжелы — Advanced RAG достаточен.
**Eval план**: `/root/antigravity/ai-eggs/data/rag_knowledge/eval_plan.md`
