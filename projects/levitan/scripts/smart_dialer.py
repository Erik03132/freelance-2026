#!/usr/bin/env python3
"""
Levitan Smart Dialer v2 — Автодозвон + автоCRM через запись Mango.
===================================================================

Ты звонишь → Mango записывает → система обрабатывает → CRM заполняется.

Запуск: python3 scripts/smart_dialer.py
Тест:   python3 scripts/smart_dialer.py --test
"""

import csv, hashlib, json, os, re, sys, time, uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

# === PATHS ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "campaigns" / "csv" / "all_contacts_2026.csv"
RESULTS_DIR = DATA_DIR / "call_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
RESULTS_CSV = RESULTS_DIR / f"results_{TODAY}.csv"
RESULTS_JSON = RESULTS_DIR / f"results_{TODAY}.json"

# === LOAD .env ===
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# === CONFIG ===
MANGO_API_KEY  = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

VPS_HOST = os.getenv("LEVITAN_VPS_HOST", "72.56.38.19")
VPS_USER = os.getenv("LEVITAN_VPS_USER", "root")

# === ФИЛЬТР КУЛЬТУР ===
TARGET_KEYWORDS = [
    "зерновые", "пшеница", "ячмень", "кукуруза",
    "подсолнечник", "рапс", "соя",
    "горох", "нут", "чечевица",
    "масличные", "бобовые", "озимая", "яровая",
    "зерно", "закупка зерновых",
]

EXCLUDE_ONLY = [
    "крс", "молочный", "мясной", "овцы", "свиньи",
    "птица", "рыба", "овощи", "картофель", "сахарная",
    "хранение", "сооружений", "техника", "ремонт",
    "торговля", "производство молочной",
]

# === LLM PROMPT ===
EXTRACTION_PROMPT = """Проанализируй транскрипт телефонного разговора между менеджером (Иван, компания «Глобал Филдс Экспорт») и клиентом (сельхозпроизводитель).

Извлеки информацию и верни ТОЛЬКО JSON (без markdown):

{{
  "status": "lead|callback|rejected|no_interest|wrong_number|other",
  "interest_level": "high|medium|low|none",
  "contact_name": "имя если назвал",
  "crops": ["список культур"],
  "volume": "объём если назвал",
  "region": "регион если упомянул",
  "basis": "CPT|FOB|DAP если обсуждали",
  "delivery_time": "сроки если назвал",
  "preferred_contact": "телефон/whatsapp/telegram/email",
  "callback_time": "когда перезвонить если просил",
  "objections": ["список возражений"],
  "key_info": "главная информация (1-2 предложения)",
  "next_action": "что делать дальше (1 предложение)"
}}

ТРАНСКРИПТ:
{transcript}"""


# ============================================================
# UTILS
# ============================================================

def norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d


def is_valid_phone(num: str) -> bool:
    n = norm_phone(num)
    return len(n) == 11 and n.startswith("7")


# ============================================================
# MANGO API
# ============================================================

def _mango_sign(payload: dict) -> str:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()


def mango_callback(phone: str) -> dict:
    """Инициировать callback через Mango."""
    command_id = f"smart_{uuid.uuid4().hex[:8]}"
    payload = {
        "command_id": command_id,
        "from": {"extension": MANGO_FROM_EXTENSION},
        "to_number": norm_phone(phone),
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


def mango_download_recording(recording_id: str) -> Optional[bytes]:
    """Скачать запись из Mango API."""
    payload = {"recording_id": recording_id, "action": "download"}
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()
    try:
        r = requests.post(
            f"{MANGO_API_BASE}queries/recording/post",
            data={"vpbx_api_key": MANGO_API_KEY, "json": j, "sign": sign},
            timeout=60,
        )
        if r.status_code == 200 and "audio" in r.headers.get("content-type", ""):
            return r.content
        return None
    except Exception as e:
        print(f"  Download error: {e}")
        return None


# ============================================================
# RECORDING PROCESSING
# ============================================================

def process_recording_on_vps(recording_id: str) -> Optional[str]:
    """Скачать и транскрибировать запись на VPS."""
    import subprocess

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

mp3_path = "/tmp/levitan_rec_{recording_id[-8:]}.mp3"
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
        if not output or output == "DOWNLOAD_FAILED":
            return None
        return output
    except Exception as e:
        print(f"  VPS processing error: {e}")
        return None


def wait_for_recording(phone: str, call_start: float, timeout: int = 90) -> Optional[str]:
    """Ждать запись разговора."""
    import subprocess

    print(f"  Ожидаю запись (до {timeout} сек)...", end="", flush=True)
    start = time.time()

    while time.time() - start < timeout:
        time.sleep(5)
        print(".", end="", flush=True)

        try:
            result = subprocess.run(
                ["ssh", f"{VPS_USER}@{VPS_HOST}",
                 "grep 'recording_added' /var/log/voice-angela/events.jsonl 2>/dev/null | tail -5"],
                capture_output=True, text=True, timeout=10,
            )

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    ts = event.get("timestamp", "")
                    if not ts:
                        continue
                    event_time = datetime.fromisoformat(ts).timestamp()
                    if event_time <= call_start:
                        continue
                    rec_id = event.get("recording_id", "")
                    if rec_id:
                        print(f"\n  Запись найдена: {rec_id[:20]}...")
                        return rec_id
                except (json.JSONDecodeError, ValueError):
                    continue
        except Exception:
            pass

    print("\n  Запись не найдена (timeout)")
    return None


def get_last_recording() -> Optional[str]:
    """Последняя запись (fallback)."""
    import subprocess
    try:
        result = subprocess.run(
            ["ssh", f"{VPS_USER}@{VPS_HOST}",
             "grep 'recording_added' /var/log/voice-angela/events.jsonl 2>/dev/null | tail -1"],
            capture_output=True, text=True, timeout=10,
        )
        line = result.stdout.strip()
        if line:
            event = json.loads(line)
            return event.get("recording_id", "")
    except Exception:
        pass
    return None


# ============================================================
# LLM
# ============================================================

def extract_call_data(transcript: str) -> dict:
    """Извлечь данные из транскрипта через LLM."""
    prompt = EXTRACTION_PROMPT.format(transcript=transcript)

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "HTTP-Referer": "https://levitan.app",
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.1,
            },
            timeout=30,
        )
        content = r.json()["choices"][0]["message"]["content"].strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError):
        return {"status": "other", "key_info": "Ошибка парсинга"}
    except Exception as e:
        return {"status": "other", "key_info": f"LLM ошибка: {e}"}


# ============================================================
# TELEGRAM
# ============================================================

def notify_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception:
        pass


# ============================================================
# CRM
# ============================================================

def save_result(contact: dict, extracted: dict, transcript: str, recording_id: str):
    """Сохранить результат в CRM."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "phone": contact["phone"],
        "name": contact.get("name", ""),
        "region": contact.get("region", ""),
        "description": contact.get("description", ""),
        "status": extracted.get("status", "other"),
        "interest_level": extracted.get("interest_level", ""),
        "contact_name": extracted.get("contact_name", ""),
        "crops": ", ".join(extracted.get("crops", [])) if isinstance(extracted.get("crops"), list) else str(extracted.get("crops", "")),
        "volume": extracted.get("volume", ""),
        "basis": extracted.get("basis", ""),
        "delivery_time": extracted.get("delivery_time", ""),
        "preferred_contact": extracted.get("preferred_contact", ""),
        "callback_time": extracted.get("callback_time", ""),
        "objections": ", ".join(extracted.get("objections", [])) if isinstance(extracted.get("objections"), list) else str(extracted.get("objections", "")),
        "key_info": extracted.get("key_info", ""),
        "next_action": extracted.get("next_action", ""),
        "recording_id": recording_id,
        "transcript_short": transcript[:200] if transcript else "",
    }

    file_exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

    full_result = {**result, "transcript_full": transcript}
    results = []
    if RESULTS_JSON.exists():
        try:
            results = json.loads(RESULTS_JSON.read_text())
        except Exception:
            results = []
    results.append(full_result)
    RESULTS_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    return result


# ============================================================
# CONTACTS
# ============================================================

def load_contacts() -> list[dict]:
    """Загрузить контакты."""
    contacts = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = (row.get("Описание", "") or "").lower()
            phones = row.get("Телефоны", "") or ""

            has_target = any(kw in desc for kw in TARGET_KEYWORDS)
            is_excluded = any(kw in desc for kw in EXCLUDE_ONLY) and not has_target

            if not has_target or is_excluded:
                continue

            phone_list = re.findall(r"[\d\-\(\)\+\s]{7,}", phones)
            for phone in phone_list:
                normalized = norm_phone(phone)
                if is_valid_phone(normalized):
                    contacts.append({
                        "name": row.get("Название", "").strip(),
                        "description": row.get("Описание", "").strip(),
                        "region": row.get("Регион", "").strip(),
                        "city": row.get("Город", "").strip(),
                        "contact_name": row.get("Имя", "").strip(),
                        "phone": normalized,
                        "phone_display": phone.strip(),
                    })
                    break

    return contacts


def load_already_called() -> set:
    """Загруженные номера."""
    called = set()
    for f in RESULTS_DIR.glob("results_*.csv"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if row.get("phone"):
                        called.add(row["phone"])
        except Exception:
            pass
    return called


# ============================================================
# UI
# ============================================================

def print_header():
    print("\n" + "=" * 60)
    print("  LEVITAN SMART DIALER")
    print("  Звони → Запись → STT → LLM → CRM")
    print("=" * 60)


def print_script():
    print("""
┌─────────────────────────────────────────────────────────┐
│ ПРИВЕТСТВИЕ:                                            │
│ «Здравствуйте! Иван, Глобал Филдс Экспорт.             │
│  Закупаем зерновые, масличные, бобовые.                 │
│  Выращиваете что-то на продажу?»                        │
├─────────────────────────────────────────────────────────┤
│ ВОПРОСЫ: культуры → объём → базис → сроки → контакт     │
│ БАЗИСЫ: CPT(забираем) | FOB(порт) | DAP(граница)        │
│ КОНТАКТЫ: +7(918)639-30-30 | info@globalfields.ru       │
└─────────────────────────────────────────────────────────┘""")


def print_contact(idx: int, total: int, contact: dict):
    print(f"\n{'─' * 60}")
    print(f"  [{idx}/{total}]  {contact['name'][:40]}")
    print(f"  Описание:  {contact['description'][:50]}")
    print(f"  Регион:    {contact['region']}, {contact['city']}")
    if contact['contact_name']:
        print(f"  Контакт:   {contact['contact_name']}")
    print(f"  Телефон:   {contact['phone_display']}  →  +{contact['phone']}")
    print(f"{'─' * 60}")


def print_result(result: dict):
    status_emoji = {
        "lead": "🟢", "callback": "🟡", "rejected": "🔴",
        "no_interest": "⚪", "wrong_number": "❌", "other": "⚫",
    }
    emoji = status_emoji.get(result["status"], "⚫")

    print(f"\n  {emoji} Статус: {result['status'].upper()}")
    if result.get("crops"):
        print(f"  🌾 Культуры: {result['crops']}")
    if result.get("volume"):
        print(f"  📦 Объём: {result['volume']}")
    if result.get("key_info"):
        print(f"  💡 Инфо: {result['key_info']}")
    if result.get("next_action"):
        print(f"  ➡️  Действие: {result['next_action']}")


# ============================================================
# MAIN
# ============================================================

def main():
    print_header()

    if not MANGO_API_KEY or not MANGO_API_SALT:
        print("\n  ⚠️  Mango ключи не найдены!")
        print("  Добавь в .env: MANGO_VPBX_API_KEY и MANGO_VPBX_API_SALT")
        return

    if not OPENROUTER_KEY:
        print("\n  ⚠️  OPENROUTER_API_KEY не задан!")
        return

    print(f"  ✓ Mango API (ext: {MANGO_FROM_EXTENSION})")
    print(f"  ✓ OpenRouter LLM")
    print(f"  ✓ VPS: {VPS_HOST}")
    if TELEGRAM_BOT_TOKEN:
        print(f"  ✓ Telegram уведомления")

    print("\n  Загрузка базы...")
    contacts = load_contacts()
    already_called = load_already_called()
    contacts = [c for c in contacts if c["phone"] not in already_called]

    print(f"  База: {len(contacts)} контактов (обзвонено ранее: {len(already_called)})")

    if not contacts:
        print("\n  Все контакты обзвонены!")
        return

    # Выбор региона
    regions = Counter(c["region"] for c in contacts)
    print("\n  Регионы:")
    for i, (region, cnt) in enumerate(regions.most_common(), 1):
        print(f"    {i}. {region} ({cnt})")
    print(f"    0. Все ({len(contacts)})")

    region_choice = input("\n  Регион [0=все]: ").strip()
    if region_choice and region_choice != "0":
        try:
            idx_r = int(region_choice) - 1
            selected_region = regions.most_common()[idx_r][0]
            contacts = [c for c in contacts if c["region"] == selected_region]
            print(f"  → {selected_region} ({len(contacts)})")
        except (ValueError, IndexError):
            pass

    print_script()
    print("\n  Команды: Enter=звонить | s=skip | q=quit | h=скрипт")

    stats = Counter()
    idx = 0

    while idx < len(contacts):
        contact = contacts[idx]
        print_contact(idx + 1, len(contacts), contact)

        cmd = input("\n  [Enter/s/q/h]: ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "s":
            idx += 1
            continue
        elif cmd == "h":
            print_script()
            continue

        # === ЗВОНИМ ===
        print(f"\n  📞 Набираю +{contact['phone']}...")
        call_start = time.time()
        result = mango_callback(contact["phone"])

        if result.get("result") in (1000, "1000"):
            print("  ✓ Callback инициирован. Говори с клиентом!")
        else:
            print(f"  ⚠️  Ошибка: {result}")
            choice = input("  Продолжить? [y/n]: ").strip().lower()
            if choice != "y":
                idx += 1
                continue

        print("\n  🎙  Разговор идёт... Нажми Enter когда закончишь.")
        input("  [Enter — разговор завершён]")
        call_duration = time.time() - call_start

        print(f"\n  Длительность: {call_duration:.0f} сек")

        if call_duration < 5:
            print("  → Слишком короткий звонок")
            stats["no_answer"] += 1
            idx += 1
            continue

        # === ЗАПИСЬ ===
        print("\n  🔍 Ищу запись разговора...")
        recording_id = wait_for_recording(contact["phone"], call_start, timeout=60)

        if not recording_id:
            print("  Пробую последнюю запись...")
            recording_id = get_last_recording()

        if not recording_id:
            print("  ❌ Запись не найдена")
            stats["other"] += 1
            idx += 1
            continue

        # === STT ===
        print(f"  📝 Транскрибирую на VPS...")
        transcript = process_recording_on_vps(recording_id)

        if not transcript:
            print("  ❌ Транскрибация не удалась")
            stats["other"] += 1
            idx += 1
            continue

        print(f"\n  📄 Транскрипт ({len(transcript)} символов):")
        print(f"  «{transcript[:200]}{'...' if len(transcript) > 200 else ''}»")

        # === LLM ===
        print("\n  🤖 Извлекаю данные через LLM...")
        extracted = extract_call_data(transcript)

        saved = save_result(contact, extracted, transcript, recording_id)
        stats[extracted.get("status", "other")] += 1

        print_result(saved)

        if TELEGRAM_BOT_TOKEN:
            status_emoji = {"lead": "🟢", "callback": "🟡", "rejected": "🔴"}.get(
                extracted.get("status", ""), "⚫"
            )
            notify_telegram(
                f"{status_emoji} <b>{contact['name'][:30]}</b>\n"
                f"📞 {contact['phone']}\n"
                f"Статус: {extracted.get('status', '?')}\n"
                f"{'🌾 ' + saved.get('crops', '') if saved.get('crops') else ''}\n"
                f"{'📦 ' + saved.get('volume', '') if saved.get('volume') else ''}"
            )

        total = sum(stats.values())
        print(f"\n  📊 [{total} звонков] "
              f"Лиды:{stats['lead']} "
              f"Перезвон:{stats['callback']} "
              f"Отказ:{stats['rejected']+stats['no_interest']} "
              f"Не взял:{stats['no_answer']}")
        if stats["lead"]:
            print(f"  Конверсия: {stats['lead']/total*100:.1f}%")

        idx += 1

    # === ИТОГ ===
    total = sum(stats.values())
    print(f"\n{'=' * 60}")
    print(f"  ИТОГ: {total} звонков")
    print(f"{'=' * 60}")
    for status, count in stats.most_common():
        print(f"  {status:15s}: {count}")
    if total and stats["lead"]:
        print(f"  {'Конверсия':15s}: {stats['lead']/total*100:.1f}%")
    print(f"\n  Результаты: {RESULTS_CSV}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    if "--test" in sys.argv:
        print("  Тест: обработка последней записи с VPS...")
        rec_id = get_last_recording()
        if rec_id:
            print(f"  Recording: {rec_id}")
            transcript = process_recording_on_vps(rec_id)
            if transcript:
                print(f"  Транскрипт: {transcript[:300]}")
                extracted = extract_call_data(transcript)
                print(f"  Извлечено:")
                print(json.dumps(extracted, ensure_ascii=False, indent=4))
            else:
                print("  Транскрибация не удалась")
        else:
            print("  Записи не найдены")
    else:
        main()
