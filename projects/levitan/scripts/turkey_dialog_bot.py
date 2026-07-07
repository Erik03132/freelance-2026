#!/usr/bin/env python3
"""
Levitan Turkey Dialog Bot v2 — предиктивная схема + Битрикс24.
================================================================

Схема (предиктивная — ты на линии сразу):
1. TG: "обзвон индюшат" → бот начинает
2. Mango звонит клиенту И тебе ОДНОВРЕМЕННО
3. Клиент слышит приветствие (TTS) → ты слышишь всё
4. Клиент отвечает → ты ведёшь диалог
5. Disconnect → запись → STT → LLM → CRM + Битрикс
6. Карточка в TG → следующий контакт

Команды:
  обзвон индюшат  — запуск
  стоп            — стоп
  статус          — статистика
  пропустить      — пропустить

Запуск: python3 scripts/turkey_dialog_bot.py
"""

import asyncio, csv, hashlib, json, logging, os, re, subprocess, sys, time, uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("pip install python-telegram-bot requests")
    sys.exit(1)

# === PATHS ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONTACTS_FILE = DATA_DIR / "turkey_not_called.json"
RESULTS_DIR = DATA_DIR / "call_results" / "turkey"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")
RESULTS_CSV = RESULTS_DIR / f"turkey_{TODAY}.csv"
RESULTS_JSON = RESULTS_DIR / f"turkey_{TODAY}.json"

# === LOAD .env ===
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Также загружаем .env из ai-eggs (для Битрикс)
AI_EGGS_ENV = Path("/Users/igorvasin/freelance-2026/projects/ai-eggs/.env")
if AI_EGGS_ENV.exists():
    with open(AI_EGGS_ENV) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Убираем прокси — Битрикс и Mango это РФ-сервисы
for v in ['HTTPS_PROXY','HTTP_PROXY','ALL_PROXY','https_proxy','http_proxy','all_proxy']:
    os.environ.pop(v, None)

# === CONFIG ===
MANGO_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")
MY_PHONE = os.getenv("MY_PHONE", "79859234644")

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Bitrix24
BITRIX_URL = os.getenv("PRODUCTION_BITRIX_WEBHOOK_URL", "").rstrip("/")

VPS_HOST = os.getenv("LEVITAN_VPS_HOST", "72.56.38.19")
VPS_USER = os.getenv("LEVITAN_VPS_USER", "root")

DELIVERY_DATE = "24 июля"
CALL_INTERVAL = int(os.getenv("CALL_INTERVAL", "5"))
RECORDING_WAIT = int(os.getenv("RECORDING_WAIT", "120"))

# === LOGGING ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("turkey-bot")

# === LLM PROMPT ===
EXTRACTION_PROMPT = """Проанализируй транскрипт разговора с клиентом про индюшат (поставка {date}).
Азовский инкубатор предлагает индюшат.

Верни ТОЛЬКО JSON:
{{
  "status": "lead|callback|rejected|no_answer|other",
  "contact_name": "имя клиента",
  "quantity": "количество индюшат",
  "delivery_info": "дата/условия доставки",
  "price_info": "информация о цене",
  "questions": "вопросы клиента",
  "notes": "примечания, договорённости",
  "wants_order": true|false
}}

ТРАНСКРИПТ:
{transcript}"""


# ============================================================
# STATE
# ============================================================
class TurkeyState:
    def __init__(self):
        self.active = False
        self.contacts: list[dict] = []
        self.current_idx = 0
        self.stats = Counter()
        self.called_phones: set = set()

state = TurkeyState()


# ============================================================
# UTILS
# ============================================================
def norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"): d = "7" + d[1:]
    elif len(d) == 10: d = "7" + d
    return d


# ============================================================
# MANGO API
# ============================================================
def _mango_sign(payload: dict) -> str:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()


def mango_callback_predictive(client_phone: str) -> dict:
    """
    Предиктивный callback: Mango звонит клиенту И тебе одновременно.
    from = extension (SIP-бот с aufile = приветствие)
    to   = клиент
    Дополнительно: второй callback на твой мобильный.
    """
    # Звонок клиенту (через SIP-бот, который проиграет приветствие)
    command_id = f"turkey_{uuid.uuid4().hex[:8]}"
    payload = {
        "command_id": command_id,
        "from": {"extension": MANGO_FROM_EXTENSION},
        "to_number": norm_phone(client_phone),
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()
    try:
        r = requests.post(
            f"{MANGO_API_BASE}commands/callback",
            data={"vpbx_api_key": MANGO_API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        return {"command_id": command_id, **r.json()}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# BITRIX24
# ============================================================
def bx_post(method: str, params: dict = None) -> dict:
    if not BITRIX_URL:
        return {}
    try:
        r = requests.post(f"{BITRIX_URL}/{method}", json=params or {}, timeout=20)
        return r.json()
    except Exception as e:
        log.error(f"Bitrix {method}: {e}")
        return {}


def bx_create_lead(contact: dict, extracted: dict, transcript: str) -> Optional[str]:
    """Создать Лид в Битрикс24."""
    if not BITRIX_URL:
        return None

    status = extracted.get("status", "other")
    if status in ("no_answer", "other"):
        return None

    name = extracted.get("contact_name", "") or contact.get("name", "")
    phone = contact.get("phone", "")
    quantity = extracted.get("quantity", "")
    notes = extracted.get("notes", "")
    questions = extracted.get("questions", "")
    price = extracted.get("price_info", "")

    lead_data = {
        "fields": {
            "TITLE": f"🦃 Индюшата {DELIVERY_DATE} — {name or phone}",
            "NAME": name,
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}],
            "COMMENTS": (
                f"📞 Автообзвон {datetime.now().strftime('%d.%m %H:%M')}\n"
                f"Статус: {status}\n"
                f"Количество: {quantity or '—'}\n"
                f"Цена: {price or '—'}\n"
                f"Вопросы: {questions or '—'}\n"
                f"Заметки: {notes or '—'}\n"
                f"Deal ID: {contact.get('deal_id', '—')}"
            ),
            "SOURCE_ID": "CALL",
        }
    }

    # Стадия: если lead → PREPARATION, если rejected → LOSE
    if status == "lead":
        lead_data["fields"]["STAGE_ID"] = "PREPARATION"
    elif status == "rejected":
        lead_data["fields"]["STAGE_ID"] = "LOSE"
    elif status == "callback":
        lead_data["fields"]["STAGE_ID"] = "NEW"

    result = bx_post("crm.lead.add", lead_data)
    lead_id = result.get("result", "")
    if lead_id:
        log.info(f"Bitrix lead created: {lead_id}")
        return str(lead_id)
    return None


def bx_update_deal_stage(deal_id: str, stage: str) -> bool:
    """Обновить стадию существующей сделки."""
    if not BITRIX_URL or not deal_id:
        return False
    result = bx_post("crm.deal.update", {"id": deal_id, "fields": {"STAGE_ID": stage}})
    return result.get("result", False) is not False


# ============================================================
# RECORDING & STT
# ============================================================
def wait_for_recording(call_start: float, timeout: int = RECORDING_WAIT) -> Optional[str]:
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(5)
        try:
            result = subprocess.run(
                ["ssh", f"{VPS_USER}@{VPS_HOST}",
                 "grep 'recording_added' /var/log/voice-angela/events.jsonl 2>/dev/null | tail -5"],
                capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.strip().split("\n"):
                if not line: continue
                try:
                    event = json.loads(line)
                    ts = event.get("timestamp", "")
                    if not ts: continue
                    event_time = datetime.fromisoformat(ts).timestamp()
                    if event_time > call_start:
                        return event.get("recording_id", "")
                except (json.JSONDecodeError, ValueError): continue
        except Exception: pass
    return None


def process_recording(recording_id: str) -> Optional[str]:
    script = f'''
import os, hashlib, json, requests, sys
from dotenv import load_dotenv
load_dotenv("/opt/.env")
API_KEY = os.getenv("MANGO_VPBX_API_KEY")
API_SALT = os.getenv("MANGO_VPBX_API_SALT")
rec_id = "{recording_id}"
payload = {{"recording_id": rec_id, "action": "download"}}
j = json.dumps(payload, separators=(",",":"))
sign = hashlib.sha256((API_KEY+j+API_SALT).encode()).hexdigest()
r = requests.post("https://app.mango-office.ru/vpbx/queries/recording/post",
    data={{"vpbx_api_key":API_KEY,"json":j,"sign":sign}}, timeout=60)
if r.status_code != 200 or "audio" not in r.headers.get("content-type",""):
    print("DOWNLOAD_FAILED"); sys.exit(1)
mp3_path = "/tmp/turkey_rec_{recording_id[-8:]}.mp3"
with open(mp3_path, "wb") as f: f.write(r.content)
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, _ = model.transcribe(mp3_path, language="ru", beam_size=5, vad_filter=True)
print(" ".join(s.text for s in segments).strip())
'''
    try:
        result = subprocess.run(
            ["ssh", f"{VPS_USER}@{VPS_HOST}", f"python3 -c '{script}'"],
            capture_output=True, text=True, timeout=180,
        )
        output = result.stdout.strip()
        if not output or output == "DOWNLOAD_FAILED": return None
        return output
    except Exception as e:
        log.error(f"VPS error: {e}")
        return None


# ============================================================
# LLM
# ============================================================
def extract_crm_data(transcript: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(date=DELIVERY_DATE, transcript=transcript)
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500, "temperature": 0.1,
            }, timeout=30,
        )
        content = r.json()["choices"][0]["message"]["content"].strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"): content = content[4:]
        return json.loads(content)
    except Exception as e:
        log.error(f"LLM: {e}")
        return {"status": "other", "notes": f"LLM ошибка: {e}"}


# ============================================================
# CRM
# ============================================================
def save_to_crm(contact: dict, extracted: dict, transcript: str, recording_id: str, bitrix_id: str = "") -> dict:
    result = {
        "timestamp": datetime.now().isoformat(),
        "deal_id": contact.get("deal_id", ""),
        "phone": contact.get("phone", ""),
        "name": contact.get("name", ""),
        "products": contact.get("products", ""),
        "contact_name": extracted.get("contact_name", ""),
        "quantity": extracted.get("quantity", ""),
        "delivery_info": extracted.get("delivery_info", ""),
        "price_info": extracted.get("price_info", ""),
        "questions": extracted.get("questions", ""),
        "status": extracted.get("status", "other"),
        "notes": extracted.get("notes", ""),
        "recording_id": recording_id,
        "bitrix_lead_id": bitrix_id,
    }

    file_exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        if not file_exists: writer.writeheader()
        writer.writerow(result)

    results = []
    if RESULTS_JSON.exists():
        try: results = json.loads(RESULTS_JSON.read_text())
        except: results = []
    results.append({**result, "transcript": transcript})
    RESULTS_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    return result


# ============================================================
# LOAD CONTACTS
# ============================================================
def load_contacts() -> list[dict]:
    if not CONTACTS_FILE.exists():
        log.error(f"Contacts file not found: {CONTACTS_FILE}")
        return []
    with open(CONTACTS_FILE) as f:
        return json.load(f)


def load_already_called() -> set:
    called = set()
    for f in RESULTS_DIR.glob("turkey_*.csv"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if row.get("phone"): called.add(row["phone"])
        except: pass
    return called


# ============================================================
# TELEGRAM BOT
# ============================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦃 <b>Turkey Dialog Bot v2</b>\n\n"
        f"Поставка: <b>{DELIVERY_DATE}</b>\n"
        "Схема: предиктивная (ты на линии сразу)\n\n"
        "Команды:\n"
        "• <b>обзвон индюшат</b> — запуск\n"
        "• <b>стоп</b> — остановить\n"
        "• <b>статус</b> — статистика\n"
        "• <b>пропустить</b> — пропустить\n\n"
        f"Битрикс: {'✅ подключён' if BITRIX_URL else '❌ нет'}\n"
        f"Оператор: +{MY_PHONE}",
        parse_mode="HTML",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "обзвон" in text and "индюш" in text:
        await start_dialing(update, context)
    elif "стоп" in text or "остановить" in text:
        await stop_dialing(update, context)
    elif "пропустить" in text or "skip" in text:
        state.current_idx += 1
        await update.message.reply_text("⏭ Пропущен")
    elif "статус" in text:
        await show_status(update, context)
    else:
        await update.message.reply_text("Команды: обзвон индюшат / стоп / статус / пропустить")


async def start_dialing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if state.active:
        await update.message.reply_text("⚠️ Обзвон уже идёт!")
        return

    contacts = load_contacts()
    if not contacts:
        await update.message.reply_text("⚠️ База контактов пуста!")
        return

    already = load_already_called()
    contacts = [c for c in contacts if c["phone"] not in already]

    if not contacts:
        await update.message.reply_text("✅ Все контакты обзвонены!")
        return

    state.contacts = contacts
    state.current_idx = 0
    state.stats = Counter()
    state.called_phones = already
    state.active = True

    await update.message.reply_text(
        f"🦃 <b>Обзвон запущен!</b>\n"
        f"Поставка: {DELIVERY_DATE}\n"
        f"Контактов: {len(contacts)}\n"
        f"Уже обзвонено: {len(already)}\n"
        f"Оператор: +{MY_PHONE}\n"
        f"Битрикс: {'✅' if BITRIX_URL else '❌'}\n\n"
        f"Набираю первый номер...",
        parse_mode="HTML",
    )
    asyncio.create_task(dialing_loop(context))


async def stop_dialing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state.active:
        await update.message.reply_text("Обзвон не запущен.")
        return
    state.active = False
    total = sum(state.stats.values())
    await update.message.reply_text(
        f"🏁 <b>Обзвон завершён</b>\n\n"
        f"Всего: {total}\n"
        f"🟢 Лиды: {state.stats['lead']}\n"
        f"🟡 Перезвон: {state.stats['callback']}\n"
        f"🔴 Отказ: {state.stats['rejected']}\n"
        f"⚫ Не взял: {state.stats['no_answer']}\n"
        f"📋 В Битрикс: {state.stats['bitrix']}",
        parse_mode="HTML",
    )


async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = sum(state.stats.values())
    remaining = len(state.contacts) - state.current_idx if state.contacts else 0
    text = (
        f"📊 <b>Статус</b>\n\n"
        f"Активен: {'✅' if state.active else '❌'}\n"
        f"Звонков: {total}\n"
        f"Осталось: {remaining}\n\n"
        f"🟢 Лиды: {state.stats['lead']}\n"
        f"🟡 Перезвон: {state.stats['callback']}\n"
        f"🔴 Отказ: {state.stats['rejected']}\n"
        f"⚫ Не взял: {state.stats['no_answer']}\n"
        f"📋 Битрикс: {state.stats['bitrix']}"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")


# ============================================================
# MAIN DIALING LOOP (предиктивная схема)
# ============================================================
async def dialing_loop(context: ContextTypes.DEFAULT_TYPE):
    chat_id = TELEGRAM_CHAT_ID

    while state.active and state.current_idx < len(state.contacts):
        contact = state.contacts[state.current_idx]
        phone = contact["phone"]

        # Уведомление
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📞 <b>Звоню #{state.current_idx + 1}</b>\n"
                f"👤 {contact.get('name', '—')[:40]}\n"
                f"🦃 {contact.get('products', '')[:40]}\n"
                f"📱 +{phone}\n"
                f"📋 Deal: {contact.get('deal_id', '—')}"
            ),
            parse_mode="HTML",
        )

        # === ЗВОНОК ===
        call_start = time.time()
        result = mango_callback_predictive(phone)

        if "error" in result:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Ошибка: {result}")
            state.current_idx += 1
            continue

        # Ждём завершения (запись появится после disconnect)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🎙 Разговор идёт... Ожидаю завершения."
        )

        recording_id = await asyncio.to_thread(wait_for_recording, call_start, RECORDING_WAIT)

        if not state.active:
            break

        if not recording_id:
            await context.bot.send_message(chat_id=chat_id, text="⚫ Не взял трубку / нет записи")
            state.stats["no_answer"] += 1
            state.current_idx += 1
            await asyncio.sleep(CALL_INTERVAL)
            continue

        # === STT ===
        await context.bot.send_message(chat_id=chat_id, text="🔄 Транскрибирую...")
        transcript = await asyncio.to_thread(process_recording, recording_id)

        if not transcript:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ STT не удался")
            state.stats["other"] += 1
            state.current_idx += 1
            await asyncio.sleep(CALL_INTERVAL)
            continue

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"💬 <b>Транскрипт:</b>\n<em>«{transcript[:300]}»</em>",
            parse_mode="HTML",
        )

        # === LLM ===
        await context.bot.send_message(chat_id=chat_id, text="🤖 Извлекаю данные...")
        extracted = await asyncio.to_thread(extract_crm_data, transcript)

        # === BITRIX ===
        bitrix_id = ""
        if BITRIX_URL:
            bitrix_id = await asyncio.to_thread(bx_create_lead, contact, extracted, transcript)
            if bitrix_id:
                state.stats["bitrix"] += 1

        # === CRM ===
        saved = save_to_crm(contact, extracted, transcript, recording_id, bitrix_id)
        status = extracted.get("status", "other")
        state.stats[status] += 1

        # === КАРТОЧКА ===
        emoji = {"lead": "🟢", "callback": "🟡", "rejected": "🔴", "no_answer": "⚫", "other": "⚫"}.get(status, "⚫")
        card = (
            f"{emoji} <b>Результат #{sum(state.stats.values())}</b>\n\n"
            f"👤 {saved.get('contact_name') or saved.get('name') or '—'}\n"
            f"📱 +{saved['phone']}\n"
            f"🦃 {saved.get('quantity') or '—'}\n"
            f"📦 {saved.get('products', '')[:40]}\n"
            f"📅 {saved.get('delivery_info') or DELIVERY_DATE}\n"
            f"💰 {saved.get('price_info') or '—'}\n"
            f"❓ {saved.get('questions') or '—'}\n"
            f"📝 {saved.get('notes') or '—'}\n"
            f"{'📋 <a href=\"https://incubird.bitrix24.ru/crm/lead/show/' + bitrix_id + '/\">Битрикс лид #' + bitrix_id + '</a>' if bitrix_id else ''}"
        )
        await context.bot.send_message(chat_id=chat_id, text=card, parse_mode="HTML")

        # Статистика
        total = sum(state.stats.values())
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📊 [{total} звонков] 🟢{state.stats['lead']} 🟡{state.stats['callback']} 🔴{state.stats['rejected']} ⚫{state.stats['no_answer']} 📋{state.stats['bitrix']}"
        )

        state.current_idx += 1
        if state.active:
            await asyncio.sleep(CALL_INTERVAL)

    # Конец
    if state.active:
        state.active = False
        total = sum(state.stats.values())
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ <b>Все контакты обзвонены!</b>\nВсего: {total}",
            parse_mode="HTML",
        )


# ============================================================
# MAIN
# ============================================================
def main():
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  TELEGRAM_BOT_TOKEN не задан!")
        sys.exit(1)
    if not MANGO_API_KEY:
        print("⚠️  MANGO_VPBX_API_KEY не задан!")
        sys.exit(1)

    print("🦃 Turkey Dialog Bot v2 starting...")
    print(f"   Поставка: {DELIVERY_DATE}")
    print(f"   Mango ext: {MANGO_FROM_EXTENSION}")
    print(f"   Оператор: +{MY_PHONE}")
    print(f"   Битрикс: {'✅' if BITRIX_URL else '❌'}")
    print(f"   VPS: {VPS_HOST}")
    print(f"   Контактов: {len(load_contacts())}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("   Bot ready. Polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
