"""
Mustay Bot — чистый Telegram-бот-маршрутизатор к Hermes-профилям (спецам).

Без сенаторской темы: никаких initiative/search/senator_core.
Только переключение профилей (спецов) через алиасы и свободный диалог
через активный Hermes-профиль.

Команды меню (Telegram Bot API не допускает пробел в команде):
  /start              — справка + клавиатура спецов
  /profile            — какой профиль сейчас активен
  /use_profile_batrak / sherlock / femida / defender / marketer / financier / health

Клавиатура (видна сразу, без кэша меню): кнопки «👤 Спец: <Имя>»,
нажатие = тот же эффект, что /use_profile_<id>.
"""

import asyncio
import os
import signal
import subprocess
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# ── Пути ────────────────────────────────────────────────
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(AGENT_DIR)
sys.path.insert(0, AGENT_DIR)

# ── Конфиг из .env ──────────────────────────────────────
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

TELEGRAM_TOKEN = os.getenv("MUSTAY_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ MUSTAY_BOT_TOKEN не найден в .env!")

ADMIN_ID = int(os.getenv("MUSTAY_ADMIN_ID", "176203333"))
PROXY_URL = os.getenv("TELEGRAM_PROXY")  # опц. socks5

# ── Бот ─────────────────────────────────────────────────
if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TELEGRAM_TOKEN, session=session)
else:
    bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ── SSoT: наши спецы (профили Hermes) ───────────────────
# command = use_profile_<id> (алиас в меню), title = подпись на кнопке.
PROFILES = {
    "batrak": ("use_profile_batrak", "🤖 Мустай (Батрак)"),
    "sherlock": ("use_profile_sherlock", "🔍 Шерлок"),
    "femida": ("use_profile_femida", "⚖️ Фемида"),
    "defender": ("use_profile_defender", "🛡️ Дефендер"),
    "marketer": ("use_profile_marketer", "📣 Маркетолог"),
    "financier": ("use_profile_financier", "💰 Финансист"),
    "health": ("use_profile_health", "⚕️ Айболит"),
}
ACTIVE_TITLE = {pid: title for pid, (_cmd, title) in PROFILES.items()}
ALIAS_TO_PID = {cmd: pid for pid, (cmd, _title) in PROFILES.items()}


# ── Хелперы Hermes CLI ──────────────────────────────────
def _run_hermes(args: list[str]) -> tuple[str, int]:
    """Синхронный вызов Hermes CLI (без сети к модели — только управление профилем)."""
    try:
        result = subprocess.run(
            ["hermes", *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (result.stdout or result.stderr or "").strip()
        return out, result.returncode
    except Exception as e:  # noqa: BLE001
        return f"⚠️ Ошибка вызова hermes: {e}", 1


def _ask_hermes(query: str, profile: str) -> tuple[str, int]:
    """Одноразовый запрос к Hermes через профиль (-p profile -z query)."""
    try:
        result = subprocess.run(
            ["hermes", "-p", profile, "-z", query, "--no-restore-cwd"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        out = (result.stdout or result.stderr or "").strip()
        return out, result.returncode
    except Exception as e:  # noqa: BLE001
        return f"⚠️ Ошибка вызова hermes: {e}", 1


_ACTIVE_PROFILE_CACHE: str | None = None


def _active_hermes_profile() -> str:
    """id активного профиля Hermes (помечен ◆). Кэшируется на запуск."""
    global _ACTIVE_PROFILE_CACHE
    if _ACTIVE_PROFILE_CACHE is not None:
        return _ACTIVE_PROFILE_CACHE
    out, _ = _run_hermes(["profile", "list"])
    active = "default"
    for line in out.splitlines():
        if "◆" in line:
            parts = line.replace("◆", "").split()
            if parts:
                active = parts[0]
            break
    _ACTIVE_PROFILE_CACHE = active
    return active


def _spec_keyboard() -> ReplyKeyboardMarkup:
    """Постоянная клавиатура: по кнопке на каждого спеца + статус."""
    rows = []
    pids = list(PROFILES.keys())
    for i in range(0, len(pids), 2):
        row = [KeyboardButton(text=f"👤 {ACTIVE_TITLE[pid]}") for pid in pids[i : i + 2]]
        rows.append(row)
    rows.append([KeyboardButton(text="🧭 Какой спец активен?")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def _pid_from_text(text: str) -> str | None:
    """Понять, какой профиль выбран: по алиасу команды или по тексту кнопки."""
    cleaned = text.strip().lstrip("/")
    token = cleaned.split()[0] if cleaned else ""
    if token in ALIAS_TO_PID:
        return ALIAS_TO_PID[token]
    # текст кнопки "👤 🤖 Мустай (Батрак)" → ищем по title
    for pid, (_cmd, title) in PROFILES.items():
        if title in text:
            return pid
    return None


# ── Команды ─────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not _is_admin(message):
        return
    active = _active_hermes_profile()
    await message.answer(
        "🤖 <b>Mustay Bot</b> — маршрутизатор к спецам Hermes.\n\n"
        "Нажми кнопку спецa или напиши <code>/use_profile_&lt;id&gt;</code>, "
        "чтобы переключить активного спеца. Потом просто пиши сообщения — "
        "они пойдут через выбранного спеца.\n\n"
        f"Сейчас активен: <b>{ACTIVE_TITLE.get(active, active)}</b>",
        parse_mode="HTML",
        reply_markup=_spec_keyboard(),
    )


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    if not _is_admin(message):
        return
    active = _active_hermes_profile()
    out, _ = _run_hermes(["profile", "list"])
    await message.answer(
        f"🧭 Активен: <b>{ACTIVE_TITLE.get(active, active)}</b>\n<pre>{out}</pre>",
        parse_mode="HTML",
        reply_markup=_spec_keyboard(),
    )


@dp.message(Command(*list(ALIAS_TO_PID.keys())))
async def cmd_use_profile(message: types.Message):
    if not _is_admin(message):
        return
    pid = _pid_from_text(message.text)
    if not pid:
        await message.answer("⚠️ Неизвестный алиас профиля.")
        return
    out, rc = _run_hermes(["profile", "use", pid])
    if rc == 0:
        await message.answer(
            f"✅ Переключено на <b>{ACTIVE_TITLE[pid]}</b>.\n"
            "Пиши дальше — сообщения пойдут через этого спеца.",
            parse_mode="HTML",
            reply_markup=_spec_keyboard(),
        )
    else:
        await message.answer(f"⚠️ Не удалось переключить:\n<code>{out}</code>", parse_mode="HTML")


@dp.message()
async def chat_handler(message: types.Message):
    """Свободный диалог: кнопка спецa ИЛИ произвольный текст → через Hermes."""
    if not _is_admin(message):
        return
    text = message.text or ""

    # Нажали кнопку выбора спеца?
    pid = _pid_from_text(text)
    if pid and (text.startswith("👤") or text.lstrip("/").split()[0] in ALIAS_TO_PID):
        out, rc = _run_hermes(["profile", "use", pid])
        if rc == 0:
            await message.answer(
                f"✅ Переключено на <b>{ACTIVE_TITLE[pid]}</b>.",
                parse_mode="HTML",
                reply_markup=_spec_keyboard(),
            )
        else:
            await message.answer(
                f"⚠️ Не удалось переключить:\n<code>{out}</code>", parse_mode="HTML"
            )
        return

    if text.startswith("🧭"):
        await cmd_profile(message)
        return

    # Обычное сообщение — через активного спеца
    active = _active_hermes_profile()
    await message.answer(
        f"⏳ Думаю через «{ACTIVE_TITLE.get(active, active)}»…", reply_markup=_spec_keyboard()
    )
    try:
        response, rc = _ask_hermes(text, active)
        if rc != 0:
            response = f"⚠️ Hermes вернул ошибку:\n{response}"
        for chunk in [response[i : i + 4000] for i in range(0, len(response), 4000)]:
            await message.answer(chunk)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка обработки: {e}")


# ── Админ-гейт ──────────────────────────────────────────
def _is_admin(message: types.Message) -> bool:
    # TODO: снять для продакшена, сейчас доступ всем для теста
    return True


# ── Меню команд ─────────────────────────────────────────
def _build_menu() -> list[BotCommand]:
    cmds = [
        BotCommand(command="start", description="👋 Старт / справка"),
        BotCommand(command="profile", description="🧭 Текущий активный спец"),
    ]
    for pid, (cmd, title) in PROFILES.items():
        cmds.append(BotCommand(command=cmd, description=f"▶ {title}"))
    return cmds


# ── Запуск ──────────────────────────────────────────────
def _acquire_lock() -> bool:
    lock = os.path.join(AGENT_DIR, "bot.lock")
    if os.path.exists(lock):
        try:
            old = int(open(lock).read().strip())
            os.kill(old, 0)
            print(f"❌ Уже запущен (PID {old})")
            return False
        except (ProcessLookupError, ValueError):
            os.remove(version_fix := lock) if False else os.remove(lock)
        except PermissionError:
            return False
    open(lock, "w").write(str(os.getpid()))
    return True


def _release_lock():
    lock = os.path.join(AGENT_DIR, "bot.lock")
    try:
        if os.path.exists(lock):
            os.remove(lock)
    except Exception:
        pass


async def main():
    if not _acquire_lock():
        return
    print("\n🤖 Mustay Bot — маршрутизатор к Hermes-спецам")
    print(f"   Admin ID: {ADMIN_ID}")

    try:
        await bot.set_my_commands(_build_menu(), scope=BotCommandScopeChat(chat_id=ADMIN_ID))
        print("   ✅ Меню зарегистрировано")
    except Exception as e:
        print(f"   ⚠️ Меню: {e}")

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print(f"   🚀 Polling (попытка {attempt}/{max_retries})...\n")
            await dp.start_polling(bot, polling_timeout=30)
            break
        except Exception as e:
            if "conflict" in str(e).lower() or "409" in str(e):
                wait = min(2**attempt, 30)
                print(f"⚠️ Conflict (попытка {attempt}). Жду {wait}с...")
                await asyncio.sleep(wait)
            else:
                print(f"❌ Ошибка: {e}")
                break
    else:
        print(f"❌ Не удалось запустить после {max_retries} попыток")
    _release_lock()


async def _shutdown():
    print("\n🛑 Остановка Mustay Bot...")
    _release_lock()
    await dp.stop_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        _release_lock()
