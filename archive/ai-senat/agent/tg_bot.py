"""
Telegram-бот для Senator AI (Мустай).
Интерфейс сенатора к AI-помощнику.
Паттерн из ai-eggs/tg_bot.py.
"""
import os
import sys
import asyncio
import signal
import re
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv

# Пути
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(AGENT_DIR)
sys.path.insert(0, AGENT_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

TELEGRAM_TOKEN = os.getenv("SENATOR_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ SENATOR_BOT_TOKEN не найден в .env!")

ADMIN_ID = int(os.getenv("SENATOR_ADMIN_ID", "176203333"))
PROXY_URL = os.getenv("TELEGRAM_PROXY", "socks5://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469")

# Бот
if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TELEGRAM_TOKEN, session=session)
else:
    bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Хранение истории диалогов в памяти
user_histories = {}

# Логи
LOG_DIR = os.path.join(AGENT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOCK_FILE = os.path.join(LOG_DIR, "bot.lock")


def is_admin(user_id: int) -> bool:
    # Временно разрешаем доступ всем для тестирования
    return True


# ============================================================
# 📋 КОМАНДЫ БОТА
# ============================================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_histories[user_id] = []
    await message.answer(
        "🏛️ **Мустай** — AI-помощник сенатора от Башкортостана\n\n"
        "Доступные команды:\n"
        "📋 /initiative — Инициатива дня\n"
        "🔍 /search [тема] — Глубокий поиск\n"
        "🌍 /global [тема] — Мировой опыт\n"
        "📊 /compare [регион] — Сравнение регионов\n"
        "🎯 /focus [тема] — Установить фокус\n"
        "📜 /history — Архив инициатив\n"
        "📰 /digest — Дайджест за сегодня\n"
        "⚙️ /status — Статус системы\n"
        "🔄 /pipeline — Запустить полный цикл\n\n"
        "Или просто напишите вопрос — я отвечу!",
        parse_mode="Markdown",
    )


@dp.message(Command("initiative"))
async def cmd_initiative(message: types.Message):
    """Генерация инициативы дня."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    await message.answer("🏛️ Генерирую инициативу дня... Это займёт 1-2 минуты.")

    try:
        from senator_core import run_daily_pipeline
        result = await asyncio.to_thread(run_daily_pipeline)
        initiative = result.get("initiative", {})
        text = initiative.get("text", "⚠️ Не удалось сгенерировать инициативу")

        # Разбиваем на части если слишком длинный
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(text)

    except Exception as e:
        await message.answer(f"❌ Ошибка генерации: {e}")


@dp.message(Command("search"))
async def cmd_search(message: types.Message):
    """Глубокий поиск по теме."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    query = message.text.replace("/search", "").strip()
    if not query:
        await message.answer("Укажите тему: /search налоговые льготы IT")
        return

    await message.answer(f"🔍 Ищу информацию по теме: *{query}*...", parse_mode="Markdown")

    try:
        from senator_core import get_answer
        answer = await asyncio.to_thread(get_answer, f"найди {query}")
        if len(answer) > 4000:
            answer = answer[:3997] + "..."
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"❌ Ошибка поиска: {e}")


@dp.message(Command("global"))
async def cmd_global(message: types.Message):
    """Мировой опыт по теме."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    query = message.text.replace("/global", "").strip()
    if not query:
        await message.answer("Укажите тему: /global цифровизация здравоохранения")
        return

    await message.answer(f"🌍 Ищу мировой опыт по теме: *{query}*...", parse_mode="Markdown")

    try:
        from scanner.deep_search import deep_search
        from llm_cascade import call_llm_structured

        result = await asyncio.to_thread(deep_search, query, "global_experience")
        context = result.get("combined_context", "")

        if not context:
            await message.answer("⚠️ Поиск не дал результатов. Попробуйте другую формулировку.")
            return

        prompt = f"""На основе данных подготовь справку о мировом опыте для сенатора.
Укажи конкретные страны, результаты, и что можно адаптировать для России/Башкортостана.

ДАННЫЕ: {context[:4000]}

ТЕМА: {query}"""

        answer = await asyncio.to_thread(
            call_llm_structured,
            "Ты — аналитик мирового опыта для сенатора от Башкортостана.",
            prompt,
            temperature=0.4,
        )
        if len(answer) > 4000:
            answer = answer[:3997] + "..."
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("compare"))
async def cmd_compare(message: types.Message):
    """Сравнение с другим регионом."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    query = message.text.replace("/compare", "").strip()
    if not query:
        await message.answer("Укажите регион/тему: /compare Татарстан IT-поддержка")
        return

    await message.answer(f"📊 Сравниваю: *{query}*...", parse_mode="Markdown")

    try:
        from senator_core import get_answer
        answer = await asyncio.to_thread(get_answer, f"сравни {query}")
        if len(answer) > 4000:
            answer = answer[:3997] + "..."
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("focus"))
async def cmd_focus(message: types.Message):
    """Установить фокусную тему."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    topic = message.text.replace("/focus", "").strip()
    if not topic:
        from senator_core import _get_focus_topic
        current = _get_focus_topic()
        if current:
            await message.answer(f"🎯 Текущий фокус: *{current}*\n\nДля изменения: /focus [новая тема]\nДля очистки: /focus clear", parse_mode="Markdown")
        else:
            await message.answer("🎯 Фокус не задан.\nУстановить: /focus [тема]")
        return

    if topic.lower() == "clear":
        from senator_core import clear_focus_topic
        clear_focus_topic()
        await message.answer("🎯 Фокус очищен. Инициативы будут по самым актуальным темам.")
    else:
        from senator_core import set_focus_topic
        set_focus_topic(topic)
        await message.answer(f"🎯 Фокус установлен: *{topic}*\n\nСледующая инициатива будет в этом направлении.", parse_mode="Markdown")


@dp.message(Command("history"))
async def cmd_history(message: types.Message):
    """Архив инициатив."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    import json
    history_path = os.path.join(BASE_DIR, "data", "initiatives_history.json")

    if not os.path.exists(history_path):
        await message.answer("📜 Архив пуст — инициатив ещё не было.")
        return

    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)

    if not history:
        await message.answer("📜 Архив пуст.")
        return

    lines = ["📜 **Архив инициатив** (последние 10):\n"]
    for h in history[-10:]:
        date = h.get("date", "?")[:10]
        title = h.get("title", "Без названия")
        lines.append(f"• [{date}] {title}")

    await message.answer("\n".join(lines), parse_mode="Markdown")


@dp.message(Command("digest"))
async def cmd_digest(message: types.Message):
    """Дайджест за сегодня."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    digest_path = os.path.join(BASE_DIR, "data", "daily_digests", f"digest_{today}.json")

    if not os.path.exists(digest_path):
        await message.answer("📰 Дайджест за сегодня ещё не сформирован.\nЗапустите /pipeline для генерации.")
        return

    import json
    with open(digest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    classification = data.get("classification", "Нет данных")
    if len(classification) > 3500:
        classification = classification[:3500] + "..."

    await message.answer(
        f"📰 **Дайджест за {today}**\n\n"
        f"📊 Новостей обработано: {data.get('news_count', '?')}\n"
        f"🎯 Фокус: {data.get('focus_topic', 'нет')}\n\n"
        f"**Классификация:**\n{classification}",
        parse_mode="Markdown",
    )


@dp.message(Command("pipeline"))
async def cmd_pipeline(message: types.Message):
    """Ручной запуск полного цикла."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    await message.answer("⚙️ Запускаю полный pipeline...\n📡 RSS → 🔍 Анализ → 🏛️ Инициатива\nЭто займёт 2-3 минуты.")

    try:
        from senator_core import run_daily_pipeline
        result = await asyncio.to_thread(run_daily_pipeline)
        initiative = result.get("initiative", {})
        text = initiative.get("text", "⚠️ Ошибка генерации")

        await message.answer("✅ Pipeline завершён!\n\n" + "─" * 30)

        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        await message.answer(f"❌ Ошибка pipeline: {e}")


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    """Статус системы."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    gemini = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
    openrouter = "✅" if os.getenv("OPENROUTER_API_KEY") else "❌"
    perplexity = "✅" if os.getenv("PERPLEXITY_API_KEY") else "❌"
    tavily = "✅" if os.getenv("TAVILY_API_KEY") else "❌"
    neon = "✅" if os.getenv("NEON_DATABASE_URL") else "❌"

    from senator_core import _get_focus_topic
    focus = _get_focus_topic() or "не задан"

    # Считаем инициативы
    import json
    h_path = os.path.join(BASE_DIR, "data", "initiatives_history.json")
    ini_count = 0
    if os.path.exists(h_path):
        with open(h_path, "r") as f:
            ini_count = len(json.load(f))

    await message.answer(
        f"⚙️ **МУСТАЙ v1.0** — Статус\n"
        f"{'─'*30}\n\n"
        f"🔌 **Подключения:**\n"
        f"  Gemini AI:    {gemini}\n"
        f"  OpenRouter:   {openrouter}\n"
        f"  Perplexity:   {perplexity}\n"
        f"  Tavily:       {tavily}\n"
        f"  Neon DB:      {neon}\n\n"
        f"🎯 Фокус: {focus}\n"
        f"📜 Инициатив сгенерировано: {ini_count}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}",
        parse_mode="Markdown",
    )


# ============================================================
# 💬 Свободный диалог
# ============================================================

@dp.message()
async def chat_handler(message: types.Message):
    """Обработка произвольных сообщений."""
    user_id = message.from_user.id
    text = message.text

    if not text or not is_admin(user_id):
        return

    print(f"\n{'='*40}")
    print(f"SENATOR: {message.from_user.full_name} (ID: {user_id})")
    print(f"MSG:     {text}")
    print(f"{'='*40}\n")

    if user_id not in user_histories:
        user_histories[user_id] = []
    history = user_histories[user_id]

    try:
        from senator_core import get_answer
        response = await asyncio.to_thread(get_answer, text, history)

        if len(response) > 4000:
            response = response[:3997] + "..."

        history.append({"role": "user", "parts": [text]})
        history.append({"role": "model", "parts": [response]})
        user_histories[user_id] = history[-20:]  # Длиннее история — лучше контекст

        await message.answer(response)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(f"⚠️ Ошибка обработки: {e}")


# ============================================================
# 🚀 Запуск
# ============================================================

def _acquire_lock():
    """Захват lock-файла."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(f"❌ Другой экземпляр уже работает (PID {old_pid})")
            return False
        except (ProcessLookupError, ValueError):
            os.remove(LOCK_FILE)
        except PermissionError:
            return False

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def _release_lock():
    """Освобождение lock-файла."""
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, "r") as f:
                if int(f.read().strip()) == os.getpid():
                    os.remove(LOCK_FILE)
    except Exception:
        pass


async def main():
    if not _acquire_lock():
        return

    print(f"\n🏛️ Мустай v1.0 — AI-помощник сенатора")
    print(f"   PID:         {os.getpid()}")
    print(f"   Gemini:      {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")
    print(f"   OpenRouter:  {'✅' if os.getenv('OPENROUTER_API_KEY') else '❌'}")
    print(f"   Perplexity:  {'✅' if os.getenv('PERPLEXITY_API_KEY') else '❌'}")
    print(f"   Admin ID:    {ADMIN_ID}")

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))

    # Регистрация меню
    commands = [
        BotCommand(command="initiative", description="🏛️ Инициатива дня"),
        BotCommand(command="search",     description="🔍 Глубокий поиск"),
        BotCommand(command="global",     description="🌍 Мировой опыт"),
        BotCommand(command="compare",    description="📊 Сравнение регионов"),
        BotCommand(command="focus",      description="🎯 Фокусная тема"),
        BotCommand(command="digest",     description="📰 Дайджест дня"),
        BotCommand(command="history",    description="📜 Архив инициатив"),
        BotCommand(command="pipeline",   description="⚙️ Запуск цикла"),
        BotCommand(command="status",     description="📊 Статус системы"),
    ]

    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
        print(f"   ✅ Меню зарегистрировано")
    except Exception as e:
        print(f"   ⚠️ Меню: {e}")

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print(f"   🚀 Polling (попытка {attempt}/{max_retries})...\n")
            await dp.start_polling(bot, polling_timeout=30)
            break
        except Exception as e:
            if "conflict" in str(e).lower() or "409" in str(e):
                wait = min(2 ** attempt, 30)
                print(f"⚠️ Conflict (попытка {attempt}). Жду {wait}с...")
                await asyncio.sleep(wait)
            else:
                print(f"❌ Ошибка: {e}")
                break
    else:
        print(f"❌ Не удалось запустить после {max_retries} попыток")

    _release_lock()


async def _shutdown():
    print("\n🛑 Остановка Мустая...")
    _release_lock()
    await dp.stop_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        _release_lock()
