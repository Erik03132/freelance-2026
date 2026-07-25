# Архитектура ai-levitan

## Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram Bot                           │
│                   @levitan_dialer_bot                        │
│                  (dialer_bot.py, PM2)                        │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐    ┌──────────────────┐
│   Mango Office API   │    │   OpenRouter API  │
│   (commands/callback)│    │   (DeepSeek LLM)  │
└──────────┬───────────┘    └──────────────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────────┐
│  Zoiper  │  │   baresip     │
│  ext 22  │  │   ext 23      │
│(оператор)│  │(робот WIP)    │
└──────────┘  └──────────────┘
```

## Поток звонка (текущий)

```
1. Бот:           берёт контакт из CSV
2. Mango callback: ext 22 → клиент
3. Zoiper:        звонит оператору
4. Оператор:      поднимает трубку
5. Mango:         звонит клиенту
6. Клиент:        отвечает
7. Оператор:      говорит приветствие → диалог
8. После звонка:  запись → STT → LLM → CRM (CSV/JSON)
9. Telegram:      уведомление с карточкой
10. Команда:      «следующий» → переход к п.1
```

## Поток звонка (целевой, с роботом-приветствием)

```
1. Бот:           берёт контакт из CSV
2. Mango callback: ext 23 → клиент
3. baresip (23):  автоответ, проигрывание greeting.wav
4. Mango:         звонит клиенту
5. Клиент:        отвечает, слышит приветствие
6. baresip:       SIP-перевод вызова на ext 22
7. Zoiper (22):   звонит оператору
8. Оператор:      поднимает — сразу к живому клиенту
9. Диалог → STT → LLM → CRM
```

## Компоненты

### dialer_bot.py
- Telegram-бот на python-telegram-bot
- Управление циклом обзвона
- Mango callback API
- Поиск записи разговора через Mango API / VPS
- STT (faster-whisper) локально или на VPS
- LLM-извлечение через OpenRouter
- Сохранение в CSV/JSON

### greeting_bridge/ (baresip)
- Локальный SIP-клиент на baresip
- Регистрация: ext 23, TCP
- Аудио-источник: aufile (WAV приветствия)
- Аудио-кодек: PCMA (G.711 A-law)
- План: автоответ → приветствие → SIP-перевод на ext 22

### База контактов
- Исходный Excel: конвертирован в CSV
- 15 965 контактов → 11 240 целевых (фильтр по ключевым словам)
- Фильтр: зерновые/масличные/бобовые
- Исключения: КРС, молочные, мясные, овощи, техника

### CRM
- `data/call_results/results_YYYY-MM-DD.csv`
- `data/call_results/results_YYYY-MM-DD.json`
- Поля: phone, company, contact_name, product, volume, price, status, notes, transcript

## Технический стек

| Слой | Технология |
|------|-----------|
| Управление | Python 3, python-telegram-bot |
| Телефония | Mango Office API, SIP (TCP) |
| SIP-клиент | baresip v4.9.0 (brew) |
| STT | faster-whisper base, CPU int8 |
| LLM | DeepSeek Chat V3 (OpenRouter) |
| TTS | edge-tts (ru-RU-SvetlanaNeural) |
| VoIP-клиент | Zoiper 5 (macOS) |
