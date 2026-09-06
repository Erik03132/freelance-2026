# SESSION_LATEST.md — итоги сессии 01.09.2026 (Каскад моделей, TG-токены)

## Главный результат

Настроен каскад из 13 бесплатных моделей на OpenRouter для всех 13 профилей ботов на VPS. Обновлены Telegram-токены для 7 ботов. Gateway запущен, боты подключаются.

### 1. Провайдеры модели
- **OpenRouter** выбран как основной провайдер (13 бесплатных моделей работают через прокси)
- **OpenCode Zen** — бесплатные модели заблокированы для РФ (RegionError 403)
- **Nous** — работает только через inference-api (не portal), 6 моделей

### 2. Каскад моделей (13 штук, все 200 OK)
```
deepseek-v4 → nemotron-3.5:free → laguna-s-2.1:free → laguna-xs-2.1:free →
minimax-m2.7:free → minimax-m3:free → cohere/north-mini-code:free →
ling-3.0:free → lfm-2.5-2.6b:free → nemotron-3-nano-omni:free →
nemotron-3-super:free → nemotron-3.5-safety:free → dots-3-note:free
```

### 3. Telegram-боты
- Обновлены токены: personal, sherlock, marketer, batrak, femida, financier, english-tutor
- Настроен `TELEGRAM_ALLOWED_USERS=176203333`
- Gateway подключает 6 профилей к Telegram через прокси

### 4. Инфраструктура
- Удалены дубликаты: `/srv/hermes/.hermes/profiles/` (23 → 13 профилей)
- Обновлён systemd drop-in: `HERMES_HOME=/root/.hermes`, `TELEGRAM_PROXY`, `OPENROUTER_API_KEY`

### 5. Осталось
- Дождаться полного подключения ботов к Telegram (~5-10 мин)
- Проверить что все отвечают
- Настроить `/sethome` для каждого бота

---

# SESSION_LATEST.md — итоги сессии 30.08.2026 (Безопасность, Checkpoints, MCP и Timeweb S3)

(см. chp.md — история хранится там)
