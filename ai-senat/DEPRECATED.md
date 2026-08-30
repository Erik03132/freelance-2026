# ⚠️ DEPRECATED — ai-senat (старый Мустай)

Сенаторская тема вынесена. Старый бот `ai-senat/agent/tg_bot.py` (инициативы,
senator_core, поиск регионов) — **больше не развивается**.

Замена: **`mustay-bot/`** — чистый маршрутизатор к Hermes-профилям (спецам)
через алиасы `/use_profile_<id>` и клавиатуру спецов. Код без senator_core.

## Миграция
- Новый бот: `freelance-2026/mustay-bot/agent/tg_bot.py`
- Токен: `MUSTAY_BOT_TOKEN` в корневом `.env` (от нового бота @BotFather)
- Запуск: `bash mustay-bot/run.sh` (через venv с aiogram)
- Старый `ai-senat` оставлен только для истории; не запускать параллельно
  с новым во избежание конфликта polling на одном токене.
