#!/usr/bin/env python3
"""
Levitan Dialer Bot — Telegram-бот для автообзвона.
===================================================

Команды:
  /start          — приветствие
  начать обзвон   — запускает цикл обзвона
  конец обзвона   — останавливает
  статус          — текущая статистика
  пропустить      — пропустить текущий контакт

Цикл:
1. Бот берёт следующий номер из базы
2. Mango callback: звонит тебе (+79859234644) и клиенту одновременно
3. Разговор записывается
4. После disconnect: запись → STT → LLM → CRM
5. Бот присылает карточку CRM
6. Автоматически набирает следующий

Запуск: python3 scripts/dialer_bot.py
PM2 (VPS): pm2 start dialer_bot.py --name levitan-bot --interpreter python3

Зависимости: python-telegram-bot, requests
"""

import asyncio
import csv
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import httpx
    import requests
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from telegram.request import HTTPXRequest
except ImportError:
    print("pip install python-telegram-bot requests httpx[socks]")
    sys.exit(1)

# === PATHS ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "campaigns" / "csv" / "_for_evening_dial_2026-07-07.csv"
RESULTS_DIR = DATA_DIR / "call_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
RESULTS_CSV = RESULTS_DIR / f"results_{TODAY}.csv"
RESULTS_JSON = RESULTS_DIR / f"results_{TODAY}.json"
ALREADY_CALLED_CSV = RESULTS_DIR / "already_called.csv"
REMINDERS_PATH = RESULTS_DIR / "reminders.json"

# === CRM ENRICHER ===
from levitan.crm_enricher import CrmEnricher

_crm_enricher = CrmEnricher()


async def _enrich_contact(contact: dict) -> dict:
    """Обогатить контакт данными из CRM."""
    try:
        enriched = await _crm_enricher.enrich(contact["phone"])
        if enriched.name and not contact.get("contact_name"):
            contact["contact_name"] = enriched.name
        if enriched.company and not contact.get("name"):
            contact["name"] = enriched.company
        contact["position"] = enriched.position
        contact["crm_email"] = enriched.email
    except Exception as e:
        log.debug("CRM enrich error: %s", e)
    return contact


# === LOAD .env ===
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Загружаем ai-eggs .env (прокси)
EGGS_ENV = Path("/Users/igorvasin/freelance-2026/projects/ai-eggs/.env")
if EGGS_ENV.exists():
    with open(EGGS_ENV) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# === CONFIG ===
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY", "")
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")
MANGO_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")
MY_PHONE = os.getenv("MY_PHONE", "79859234644")  # Твой мобильный

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

VPS_HOST = os.getenv("LEVITAN_VPS_HOST", "185.39.206.145")
VPS_USER = os.getenv("LEVITAN_VPS_USER", "root")
VPS_AVAILABLE = False  # будет проверено при старте

# CRM API
CRM_API_BASE = os.getenv("CRM_API_BASE", "http://127.0.0.1:8088")
CRM_AVAILABLE = False  # проверяется при первом использовании

# Пауза между звонками (сек)
CALL_INTERVAL = int(os.getenv("CALL_INTERVAL", "5"))

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("levitan-bot")


def _mask_proxy_url(url: str) -> str:
    """Скрывает логин/пароль в URL прокси для безопасного вывода."""
    try:
        parsed = urlparse(url)
        if parsed.username or parsed.password:
            netloc = f"***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return parsed._replace(netloc=netloc).geturl()
    except Exception:
        pass
    return url


def _pick_working_proxy(test_url: str = "https://api.telegram.org") -> str:
    """
    Проверяет все доступные прокси-переменные и возвращает первый работающий.
    Пустая строка означает, что ни один прокси не ответил.
    """
    candidates = []
    for key in (
        "TELEGRAM_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "HTTP_PROXY",
        "https_proxy",
        "all_proxy",
        "http_proxy",
    ):
        value = os.getenv(key, "").strip()
        if value and value not in candidates:
            candidates.append(value)

    for proxy_url in candidates:
        try:
            with httpx.Client(proxy=proxy_url, timeout=5.0) as client:
                resp = client.head(test_url)
                if resp.status_code < 500:
                    log.info("Working proxy selected: %s", _mask_proxy_url(proxy_url))
                    return proxy_url
        except Exception as exc:
            log.debug("Proxy %s failed: %s", _mask_proxy_url(proxy_url), exc)
            continue

    log.warning("No working proxy found among %s", [_mask_proxy_url(u) for u in candidates])
    return ""


# === ФИЛЬТР ===
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
EXTRACTION_PROMPT = """Проанализируй транскрипт телефонного разговора менеджера с сельхозпроизводителем.
Компания «Глобал Филдс Экспорт» закупает зерновые, масличные, бобовые.

Верни ТОЛЬКО JSON:

{{
  "status": "lead|callback|rejected|no_interest|no_answer|other",
  "contact_name": "имя контакта",
  "phone": "телефон",
  "product": "наименование продукции (культуры)",
  "volume": "количество (тонн)",
  "ready_date": "когда будет готово к отгрузке",
  "price_info": "информация о цене",
  "notes": "примечания (возражения, особенности, договорённости)"
}}

Правила:
- status=lead если есть интерес к продаже
- status=callback если просит перезвонить
- status=rejected если категорически отказал
- Заполняй только то что реально прозвучало в разговоре

ДАННЫЕ ИЗ БАЗЫ КОНТАКТОВ:
{contact_context}

ТРАНСКРИПТ:
{transcript}"""


# ============================================================
# STATE
# ============================================================

class DialerState:
    """Состояние обзвона для одного оператора."""

    def __init__(self):
        self.active = False
        self.carousel = False
        self.contacts: list[dict] = []
        self.current_idx = 0
        self.current_contact: Optional[dict] = None
        self.call_start: float = 0
        self.stats = Counter()
        self.results: list[dict] = []
        self.waiting_for_hangup = False
        self.waiting_for_next = False
        self.next_event: Optional[asyncio.Event] = None
        self.csv_path: Optional[str] = None
        self.ext: Optional[str] = None
        self.chat_id: Optional[str] = None
        self.waiting_for_summary = False

    def reset(self):
        self.active = False
        self.carousel = False
        self.current_contact = None
        self.call_start = 0
        self.waiting_for_hangup = False
        self.waiting_for_next = False
        self.next_event = None


# Хранилище состояний: chat_id → DialerState
_operator_states: dict[int, DialerState] = {}


def get_state(chat_id: int) -> DialerState:
    if chat_id not in _operator_states:
        _operator_states[chat_id] = DialerState()
    return _operator_states[chat_id]

# Кнопки
MAIN_BUTTONS = [["▶ Начать обзвон", "⏹ Стоп"], ["⏭ Следующий", "⏩ Пропустить"], ["📊 Статус"]]
IDLE_BUTTONS = [["▶ Начать обзвон", "🎠 Карусель"], ["📊 Статус"]]
DIALING_BUTTONS = [["⏭ Следующий", "⏩ Пропустить"], ["⏹ Стоп", "📊 Статус"]]
WAIT_BUTTONS = [["⏭ Следующий"], ["⏹ Стоп", "📊 Статус"]]
CAROUSEL_BUTTONS = [["🎠 Карусель ✓", "⏭ Следующий"], ["⏩ Пропустить", "⏹ Стоп", "📊 Статус"]]


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


def contact_from_row(row: dict, phone: str) -> dict:
    return {
        "name": row.get("Название", row.get("company_name", row.get("company", ""))).strip(),
        "description": row.get("Описание", row.get("description", "")).strip(),
        "region": row.get("Регион", row.get("region", "")).strip(),
        "city": row.get("Город", row.get("city", "")).strip(),
        "address": row.get("Адрес", row.get("address", "")).strip(),
        "contact_name": row.get("Имя", row.get("contact_name", "")).strip(),
        "phone": norm_phone(phone),
    }


def contact_context(contact: dict) -> str:
    if not contact:
        return "нет данных"
    fields = [
        ("Компания", contact.get("name", "")),
        ("Контакт", contact.get("contact_name", "")),
        ("Регион", contact.get("region", "")),
        ("Район/город", contact.get("city", "")),
        ("Адрес", contact.get("address", "")),
        ("Культуры из базы", contact.get("description", "")),
        ("Телефон", contact.get("phone", "")),
    ]
    return "\n".join(f"{k}: {v}" for k, v in fields if v) or "нет данных"


_CONTACT_LOOKUP_CACHE: Optional[dict[str, dict]] = None


def load_contact_lookup() -> dict[str, dict]:
    global _CONTACT_LOOKUP_CACHE
    if _CONTACT_LOOKUP_CACHE is not None:
        return _CONTACT_LOOKUP_CACHE

    lookup: dict[str, dict] = {}
    csv_dir = DATA_DIR / "campaigns" / "csv"
    for path in sorted(csv_dir.glob("*.csv")):
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    phones = row.get("Телефоны", row.get("phone", "")) or ""
                    for raw_phone in re.findall(r"[\d\-\(\)\+\s]{7,}", phones):
                        phone = norm_phone(raw_phone)
                        if is_valid_phone(phone) and phone not in lookup:
                            lookup[phone] = contact_from_row(row, phone)
        except Exception:
            continue
    _CONTACT_LOOKUP_CACHE = lookup
    return lookup


def find_contact_by_phone(phone: str) -> Optional[dict]:
    normalized = norm_phone(phone)
    if not is_valid_phone(normalized):
        return None
    return load_contact_lookup().get(normalized)


# === СТОП-ЛИСТ (ФЗ-152: право на отзыв согласия на обработку/обзвон) ===

STOPLIST_PATH = RESULTS_DIR / "stoplist.txt"


def _normalize_stop_phone(raw: str) -> str:
    return norm_phone(raw)


def load_stoplist() -> set:
    """Загрузить стоп-лист (номера, кому звонить запрещено).

    Поддерживаются:
    - RESULTS_DIR/stoplist.txt (по одному номеру на строку)
    - записи CRM со status='blocked'
    """
    blocked: set = set()

    if STOPLIST_PATH.exists():
        try:
            for line in STOPLIST_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                blocked.add(_normalize_stop_phone(line))
        except Exception:
            pass

    # CRM API
    try:
        for c in crm_get_contacts(status="blocked"):
            phone = c.get("phone", "")
            if phone:
                blocked.add(_normalize_stop_phone(phone))
    except Exception:
        pass

    return blocked


def add_to_stoplist(phone: str) -> bool:
    """Добавить номер в стоп-лист. Возвращает True если добавлен."""
    normalized = _normalize_stop_phone(phone)
    if not is_valid_phone(normalized):
        return False
    blocked = load_stoplist()
    if normalized in blocked:
        return False
    try:
        with open(STOPLIST_PATH, "a", encoding="utf-8") as f:
            f.write(normalized + "\n")
        blocked.add(normalized)
        return True
    except Exception:
        return False


def is_blocked(phone: str) -> bool:
    return _normalize_stop_phone(phone) in load_stoplist()


# ============================================================
# MANGO API
# ============================================================

def mango_callback(client_phone: str, from_ext: Optional[str] = None) -> dict:
    """
    Predictive callback: Mango звонит клиенту,
    если ответил — соединяет с MY_PHONE.
    """
    ext = from_ext or MANGO_FROM_EXTENSION
    command_id = f"bot_{uuid.uuid4().hex[:8]}"
    payload = {
        "command_id": command_id,
        "from": {"extension": ext},
        "to_number": norm_phone(client_phone),
        "timeout": 30,
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()

    try:
        r = requests.post(
            f"{MANGO_API_BASE}commands/callback",
            data={"vpbx_api_key": MANGO_API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        result = r.json()
        log.info(f"Callback → {client_phone}: {result}")
        return {"command_id": command_id, **result}
    except Exception as e:
        log.error(f"Callback error: {e}")
        return {"error": str(e)}


# ============================================================
# RECORDING & STT (КАСКАД: VPS → локально)
# ============================================================

def check_vps() -> bool:
    import subprocess
    try:
        r = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", f"{VPS_USER}@{VPS_HOST}", "echo ok"],
            capture_output=True, text=True, timeout=8,
        )
        return r.returncode == 0
    except Exception:
        return False


def find_recording_mango(phone: str, after_ts: float) -> Optional[str]:
    """Найти recording_id через расширенную статистику Mango API."""
    try:
        from mango_s2t import find_recording_via_stats
        found = find_recording_via_stats(phone, after_ts, timeout=30)
        if found:
            return found["recording_id"]
    except Exception as e:
        log.error("find_recording_mango: %s", e)
    return None


def wait_for_recording(phone: str, call_start: float, timeout: int = 90) -> Optional[str]:
    """Каскад: VPS events → Mango API скрипт."""
    # 1. VPS
    if VPS_AVAILABLE:
        log.info("VPS: ищем запись...")
        start = time.time()
        while time.time() - start < min(timeout, 30):
            time.sleep(4)
            try:
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=5", f"{VPS_USER}@{VPS_HOST}",
                     "grep 'recording_added' /var/log/voice-angela/events.jsonl 2>/dev/null | tail -5"],
                    capture_output=True, text=True, timeout=8,
                )
                for line in result.stdout.strip().split("\n"):
                    if not line: continue
                    try:
                        evt = json.loads(line)
                        et = evt.get("timestamp", "")
                        if et and datetime.fromisoformat(et).timestamp() > call_start:
                            return evt.get("recording_id", "")
                    except: pass
            except: pass

    # 2. Mango API
    log.info("Mango API: ищем запись...")
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(8)
        rec = find_recording_mango(phone, call_start)
        if rec: return rec
    return None


def process_recording(recording_id: str) -> Optional[str]:
    """Каскад: VPS STT → локальный STT."""
    # 1. VPS
    if VPS_AVAILABLE:
        try:
            script = f'''
import os, hashlib, json, requests, sys
from dotenv import load_dotenv
load_dotenv("/opt/.env")
API_KEY=os.getenv("MANGO_VPBX_API_KEY");API_SALT=os.getenv("MANGO_VPBX_API_SALT")
rec_id="{recording_id}"
payload={{"recording_id":rec_id,"action":"download"}}
j=json.dumps(payload);sign=hashlib.sha256((API_KEY+j+API_SALT).encode()).hexdigest()
r=requests.post("https://app.mango-office.ru/vpbx/queries/recording/post",
    data={{"vpbx_api_key":API_KEY,"json":j,"sign":sign}},timeout=60)
if r.status_code!=200:print("FAIL");sys.exit(1)
mp3=f"/tmp/lr_{id(recording_id)}.mp3"
with open(mp3,"wb") as f:f.write(r.content)
from faster_whisper import WhisperModel
m=WhisperModel("base",device="cpu",compute_type="int8")
segs,_=m.transcribe(mp3,language="ru",beam_size=5,vad_filter=True)
print(" ".join(s.text for s in segs).strip())
'''
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=8", f"{VPS_USER}@{VPS_HOST}", f"python3 -c '{script}'"],
                capture_output=True, text=True, timeout=180,
            )
            output = result.stdout.strip()
            if output and output != "FAIL": return output
        except: pass

    # 2. Локально
    payload = {"recording_id": recording_id, "action": "download"}
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()
    try:
        r = requests.post(
            f"{MANGO_API_BASE}queries/recording/post",
            data={"vpbx_api_key": MANGO_API_KEY, "json": j, "sign": sign},
            timeout=60,
        )
        if r.status_code != 200 or len(r.content) < 1000: return None
        mp3 = f"/tmp/levitan_local_{id(recording_id)}.mp3"
        with open(mp3, "wb") as f: f.write(r.content)
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(mp3, language="ru", beam_size=5, vad_filter=True)
        return " ".join(s.text for s in segments).strip()
    except Exception as e:
        log.error(f"Local STT: {e}")
        return None


def extract_crm_data(transcript: str, contact: Optional[dict] = None) -> dict:
    """LLM извлечение CRM-данных."""
    prompt = EXTRACTION_PROMPT.format(transcript=transcript, contact_context=contact_context(contact or {}))
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
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
    except Exception as e:
        log.error(f"LLM error: {e}")
        return {"status": "other", "notes": f"LLM ошибка: {e}"}


# ============================================================
# CRM
# ============================================================

def save_to_crm(contact: dict, extracted: dict, transcript: str, recording_id: str) -> dict:
    """Сохранить в CRM."""
    product = extracted.get("product", "") or contact.get("description", "")
    contact_name = extracted.get("contact_name", "") or contact.get("contact_name", "")
    result = {
        "timestamp": datetime.now().isoformat(),
        "phone": contact["phone"],
        "company_name": contact.get("name", ""),
        "region": contact.get("region", ""),
        "city": contact.get("city", ""),
        "address": contact.get("address", ""),
        "contact_name": contact_name,
        "product": product,
        "base_product": contact.get("description", ""),
        "volume": extracted.get("volume", ""),
        "ready_date": extracted.get("ready_date", ""),
        "price_info": extracted.get("price_info", ""),
        "status": extracted.get("status", "other"),
        "notes": extracted.get("notes", ""),
        "recording_id": recording_id,
    }

    # CSV
    file_exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

    # JSON
    results = []
    if RESULTS_JSON.exists():
        try:
            results = json.loads(RESULTS_JSON.read_text())
        except Exception:
            results = []
    results.append({**result, "transcript": transcript})
    RESULTS_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    # CRM API (дублирование)
    try:
        crm_save_contact(result, transcript)
    except Exception:
        pass

    return result


# === CRM API ===

def _crm_api(method: str, path: str, data: dict = None) -> Optional[dict]:
    """Вызов CRM API. Возвращает dict или None при ошибке."""
    global CRM_AVAILABLE
    try:
        url = f"{CRM_API_BASE}{path}"
        if method == "GET":
            r = requests.get(url, timeout=5)
        elif method == "POST":
            r = requests.post(url, json=data, timeout=5)
        elif method == "PATCH":
            r = requests.patch(url, json=data, timeout=5)
        elif method == "DELETE":
            r = requests.delete(url, timeout=5)
        else:
            return None
        if r.status_code < 400:
            CRM_AVAILABLE = True
            return r.json()
        log.warning("CRM API %s %s → %s", method, path, r.status_code)
        CRM_AVAILABLE = False
        return None
    except Exception as e:
        log.debug("CRM API error: %s", e)
        CRM_AVAILABLE = False
        return None


def crm_save_contact(result: dict, transcript: str) -> Optional[dict]:
    """Сохранить контакт в CRM через API."""
    payload = {**result, "transcript": transcript}
    return _crm_api("POST", "/api/contacts", payload)


def crm_find_by_phone(phone: str) -> Optional[dict]:
    """Найти контакт в CRM по телефону."""
    data = _crm_api("GET", f"/api/contacts?search={phone}")
    if isinstance(data, list):
        for c in data:
            if norm_phone(c.get("phone", "")) == norm_phone(phone):
                return c
    return None


def crm_update_contact(contact_id: int, updates: dict) -> Optional[dict]:
    """Обновить контакт в CRM."""
    return _crm_api("PUT", f"/api/contacts/{contact_id}", updates)


def crm_get_contacts(search: str = "", status: str = "") -> list[dict]:
    """Получить контакты из CRM API."""
    params = []
    if search:
        params.append(f"search={search}")
    if status:
        params.append(f"status={status}")
    qs = "?" + "&".join(params) if params else ""
    data = _crm_api("GET", f"/api/contacts{qs}")
    return data if isinstance(data, list) else []


def crm_get_stats() -> dict:
    """Получить статистику из CRM API."""
    data = _crm_api("GET", "/api/stats")
    return data if isinstance(data, dict) else {}


def crm_save_reminder(phone: str, due_date: str, note: str) -> Optional[dict]:
    return _crm_api("POST", "/api/reminders", {
        "phone": phone, "due_date": due_date, "note": note,
    })


def crm_get_reminders() -> list[dict]:
    data = _crm_api("GET", "/api/reminders")
    return data if isinstance(data, list) else []


def crm_toggle_reminder(rid: int) -> Optional[dict]:
    return _crm_api("PATCH", f"/api/reminders/{rid}/done")


def crm_delete_reminder(rid: int) -> Optional[dict]:
    return _crm_api("DELETE", f"/api/reminders/{rid}")


# ============================================================
# CONTACTS
# ============================================================

def load_contacts(weekend_only: bool = False, csv_path: Optional[str] = None) -> list[dict]:
    """Загрузить контакты."""
    path = csv_path or CSV_PATH
    contacts = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Название", "").strip()
            desc = (row.get("Описание", "") or "").lower()
            phones = row.get("Телефоны", "") or ""

            has_target = any(kw in desc for kw in TARGET_KEYWORDS)
            is_excluded = any(kw in desc for kw in EXCLUDE_ONLY) and not has_target

            # Для TXT/простых CSV без описания — пропускаем фильтр
            skip_filter = not desc and not name
            if not skip_filter and (not has_target or is_excluded):
                continue

            # В выходные — только КФХ и ИП (не ООО/АО/ЗАО)
            if weekend_only:
                name_lower = name.lower()
                if any(t in name_lower for t in ("ооо", "ао ", "зао", "спк", "общество")):
                    continue

            phone_list = re.findall(r"[\d\-\(\)\+\s]{7,}", phones)
            for phone in phone_list:
                normalized = norm_phone(phone)
                if is_valid_phone(normalized):
                    contacts.append(contact_from_row(row, normalized))
                    break
    return contacts


def load_already_called() -> set:
    called = set()

    # Локальные файлы результатов
    for f in RESULTS_DIR.glob("results_*.csv"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if row.get("phone"):
                        called.add(row["phone"])
        except Exception:
            pass
    if ALREADY_CALLED_CSV.exists():
        try:
            with open(ALREADY_CALLED_CSV, "r", encoding="utf-8") as fh:
                for line in fh:
                    phone = line.strip()
                    if phone:
                        called.add(phone)
        except Exception:
            pass

    # CRM API — номера из CRM (уже обзвоненные ранее)
    try:
        r = requests.get("http://127.0.0.1:8088/api/contacts", timeout=3)
        if r.ok:
            for c in r.json():
                phone = c.get("phone", "")
                if phone:
                    called.add(phone)
    except Exception:
        pass

    return called


def save_already_called(phone: str):
    with open(ALREADY_CALLED_CSV, "a", encoding="utf-8") as f:
        f.write(phone + "\n")


# ============================================================
# TELEGRAM BOT HANDLERS
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = get_state(update.effective_chat.id)
    keyboard = ReplyKeyboardMarkup(IDLE_BUTTONS, resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(
        "🎙 <b>Levitan Dialer Bot</b>\n\n"
        "Нажми <b>▶ Начать обзвон</b> для запуска.\n"
        "Можно отправить CSV/XLS/TXT файл с контактами — загрузится своя база.\n"
        f"Текущий extension: <b>{os.getenv('MANGO_FROM_EXTENSION', '22')}</b>",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def cmd_ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить внутренний номер оператора."""
    st = get_state(update.effective_chat.id)
    if context.args:
        ext_num = context.args[0]
        st.ext = ext_num
        MANGO_FROM_EXTENSION = ext_num
        await update.message.reply_text(f"✅ Внутренний номер: <b>{ext_num}</b>", parse_mode="HTML")
    else:
        current = st.ext or os.getenv("MANGO_FROM_EXTENSION", "22")
        await update.message.reply_text(f"Текущий номер: <b>{current}</b>\nИспользуй: /ext 100", parse_mode="HTML")


async def cmd_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вставить конспект из Mango и извлечь данные."""
    st = get_state(update.effective_chat.id)
    if context.args:
        transcript = " ".join(context.args)
        await _process_summary(update, context, transcript)
    else:
        st.waiting_for_summary = True
        await update.message.reply_text(
            "📝 Вставь конспект разговора из Mango (скопируй из карточки звонка).\n"
            "Отправь текстом в ответ."
        )


async def _process_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, transcript: str):
    """Извлечь данные из конспекта через LLM."""
    if len(transcript) < 20:
        await update.message.reply_text("⚠️ Слишком короткий текст. Вставь полный конспект.")
        return

    msg = await update.message.reply_text("🔄 Анализирую конспект...")

    prompt = f"""Ты ассистент отдела продаж зерновой компании Global Fields Export (ООО «Глобал Фиилдс Экспорт»).

Из транскрипции разговора менеджера с потенциальным клиентом (фермером, КФХ) извлеки структурированные данные.
Компания покупает зерновые (пшеница, ячмень, кукуруза, подсолнечник) на экспорт.

Верни ТОЛЬКО JSON без пояснений:
{{
  "contact_name": "имя фермера",
  "company": "название хозяйства",
  "phone": "номер телефона из транскрипции",
  "product": "какая культура",
  "volume": "объём в тоннах",
  "price_info": "что по цене (если обсуждали)",
  "ready_date": "когда готов продать",
  "status": "lead | not_interested | callback | no_contact | other",
  "notes": "краткое саммари 2-3 предложения"
}}

Транскрипция:
{transcript}"""

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={
                "model": OPENROUTER_MODEL,
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
        data = json.loads(content)
    except Exception as e:
        await msg.edit_text(f"⚠️ Ошибка обработки: {e}")
        log.error(f"Summary error: {e}")
        return

    # Try to find phone in the transcript
    phone = data.get("phone", "")
    if not phone:
        import re
        m = re.search(r"(\+?7[- \d]?\d{3}[- \d]?\d{3}[- \d]?\d{2}[- \d]?\d{2})", transcript)
        if m:
            phone = m.group(1)

    db_contact = find_contact_by_phone(phone) if phone else None

    # CRM enrichment
    if phone:
        try:
            enriched = await _crm_enricher.enrich(phone)
            if not db_contact:
                db_contact = {}
            if enriched.name and not db_contact.get("contact_name"):
                db_contact["contact_name"] = enriched.name
            if enriched.company and not db_contact.get("name"):
                db_contact["name"] = enriched.company
            if enriched.position:
                db_contact["position"] = enriched.position
        except Exception:
            pass

    result = {
        **data,
        "timestamp": datetime.now().isoformat(),
        "phone": norm_phone(phone) if phone else "",
        "company_name": data.get("company", "") or (db_contact or {}).get("name", ""),
        "region": (db_contact or {}).get("region", ""),
        "city": (db_contact or {}).get("city", ""),
        "address": (db_contact or {}).get("address", ""),
        "contact_name": data.get("contact_name", "") or (db_contact or {}).get("contact_name", ""),
        "base_product": (db_contact or {}).get("description", ""),
        "transcript": transcript[:300],
        "source": "manual_summary",
    }

    # Save to results (JSONL)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = Path(os.environ.get("LEVITAN_RESULTS_DIR", str(DATA_DIR / "call_results")))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"results_{date_str}_manual.jsonl"
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    # Save to CRM API
    try:
        crm_payload = {
            "phone": result.get("phone", ""),
            "company_name": result.get("company_name", ""),
            "region": result.get("region", ""),
            "city": result.get("city", ""),
            "address": result.get("address", ""),
            "contact_name": result.get("contact_name", ""),
            "product": data.get("product", "") or result.get("base_product", ""),
            "base_product": result.get("base_product", ""),
            "volume": data.get("volume", ""),
            "ready_date": data.get("ready_date", ""),
            "price_info": data.get("price_info", ""),
            "status": data.get("status", "other"),
            "notes": data.get("notes", ""),
            "transcript": transcript[:1000],
            "timestamp": result["timestamp"],
        }
        _crm_api("POST", "/api/contacts", crm_payload)
    except Exception as e:
        log.error("CRM API save from summary: %s", e)

    # Format response
    status_emoji = {"lead": "🔥", "callback": "📞", "not_interested": "❌", "no_contact": "⚪", "other": "❓"}
    emoji = status_emoji.get(data.get("status", ""), "❓")

    text = (
        f"{emoji} <b>Результат анализа</b>\n"
        f"Клиент: {result.get('contact_name', '?')}\n"
        f"Хозяйство: {result.get('company_name', '?')}\n"
        f"Телефон: {phone}\n"
        f"Регион: {result.get('region', '—')} {result.get('city', '')}\n"
        f"Адрес: {result.get('address', '—') or '—'}\n"
        f"Продукт: {data.get('product', '') or result.get('base_product', '?')}\n"
        f"Объём: {data.get('volume', '?')}\n"
        f"Цена: {data.get('price_info', '?')}\n"
        f"Готовность: {data.get('ready_date', '?')}\n"
        f"Статус: {data.get('status', '?')}\n\n"
        f"📝 {data.get('notes', '')}"
    )
    await msg.edit_text(text, parse_mode="HTML")
    log.info("Summary processed: %s → %s", phone, data.get("status"))


# ============================================================
# CRM & REMINDERS
# ============================================================

def _load_results() -> list[dict]:
    results = []
    for f in sorted(RESULTS_DIR.glob("results_*.json")):
        try:
            with open(f) as fh:
                results.extend(json.load(fh))
        except: pass
    for f in sorted(RESULTS_DIR.glob("results_*.jsonl")):
        try:
            with open(f) as fh:
                for line in fh:
                    if line.strip():
                        results.append(json.loads(line))
        except: pass
    return results


def _load_reminders() -> list[dict]:
    if REMINDERS_PATH.exists():
        try:
            with open(REMINDERS_PATH) as f:
                return json.load(f)
        except: pass
    return []


def _save_reminders(reminders: list[dict]):
    with open(REMINDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)


async def cmd_crm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр CRM: /crm — сводка, /crm <текст> — поиск."""
    try:
        query = " ".join(context.args) if context.args else ""
        if query:
            api_results = crm_get_contacts(search=query)
            if not api_results:
                await update.message.reply_text(f"Ничего не найдено по: {query}")
                return
            lines = [f"<b>{c.get('company_name', '?')}</b> +{c.get('phone', '?')}"
                     f"\n  Статус: {c.get('status', '?')} | Товар: {c.get('product', '?')} | Объём: {c.get('volume', '?')}"
                     f"\n  {c.get('notes', '')}"
                     for c in api_results[:5]]
            await update.message.reply_text("\n".join(lines), parse_mode="HTML")
            return

        stats = crm_get_stats()
        leads = crm_get_contacts(status="lead")
        callbacks = crm_get_contacts(status="callback")
        all_contacts = crm_get_contacts()

        if not all_contacts and not stats.get("total"):
            # fallback на локальные файлы
            results = _load_results()
            if not results:
                await update.message.reply_text("📭 CRM пуста. Нет обработанных звонков.")
                return
            return await _cmd_crm_local(update, results)

        total = stats.get("total", len(all_contacts))
        lines = [f"📊 <b>CRM — сводка</b>\n"]
        lines.append(f"🔥 Лиды: {stats.get('leads', len(leads))}")
        lines.append(f"📞 Всего контактов: {total}")
        lines.append(f"📅 Звонков сегодня: {stats.get('today_calls', 0)}")

        if leads:
            lines.append("\n<b>Горячие лиды:</b>")
            for l in leads[:5]:
                lines.append(f"  🔥 {l.get('company_name','?')} +{l.get('phone','?')} — {l.get('product','?')} {l.get('volume','?')}")
        if callbacks:
            lines.append("\n<nontext>Ожидают перезвона:</b>")
            for c in callbacks[:5]:
                lines.append(f"  📞 {c.get('company_name','?')} +{c.get('phone','?')}")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        log.error("CRM API error, falling back to local: %s", e)
        results = _load_results()
        if not results:
            await update.message.reply_text("📭 CRM пуста. Нет обработанных звонков.")
        else:
            await _cmd_crm_local(update, results)


async def _cmd_crm_local(update: Update, results: list):
    """Fallback: показать сводку CRM из локальных JSON."""
    statuses = {}
    for r in results:
        s = r.get("status", "other")
        statuses[s] = statuses.get(s, 0) + 1
    lines = ["📊 <b>CRM — сводка (локально)</b>\n"]
    emoji_map = {"lead": "🔥", "callback": "📞", "not_interested": "❌", "no_contact": "⚪", "other": "❓"}
    for s in ["lead", "callback", "not_interested", "no_contact", "other"]:
        cnt = statuses.get(s, 0)
        if cnt:
            lines.append(f"{emoji_map.get(s, '❓')} {s}: {cnt}")
    lines.append(f"\nВсего записей: {len(results)}")
    leads = [r for r in results if r.get("status") == "lead"]
    if leads:
        lines.append("\n<b>Горячие лиды:</b>")
        for l in leads:
            lines.append(f"  🔥 {l.get('company_name','?')} +{l.get('phone','?')} — {l.get('product','?')} {l.get('volume','?')}")
    callbacks = [r for r in results if r.get("status") == "callback"]
    if callbacks:
        lines.append("\n<b>Ожидают перезвона:</b>")
        for c in callbacks:
            lines.append(f"  📞 {c.get('company_name','?')} +{c.get('phone','?')}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить напоминание: /remind <телефон> <ГГГГ-ММ-ДД> <заметка>"""
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "Использование:\n"
            "/remind <телефон> <ГГГГ-ММ-ДД> <заметка>\n"
            "Пример: /remind 79184296652 2026-07-20 Перезвонить Белому, 50т пшеницы\n\n"
            "Без даты: /remind list — все напоминания\n"
            "/remind del <id> — удалить"
        )
        return

    if args[0] == "list":
        reminders = crm_get_reminders()
        if not reminders:
            reminders = _load_reminders()
        if not reminders:
            await update.message.reply_text("Нет напоминаний.")
            return
        lines = ["📌 <b>Напоминания:</b>"]
        for r in reminders:
            done = "✅" if r.get("done") else "⏳"
            lines.append(f"{done} [{r.get('id','?')}] {r.get('phone','?')} до {r.get('due_date','?')} — {r.get('note','')}")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
        return

    if args[0] == "del" and len(args) > 1:
        try:
            rid = int(args[1])
            rem = crm_delete_reminder(rid)
            if rem and rem.get("ok"):
                await update.message.reply_text(f"✅ Напоминание {rid} удалено")
            else:
                # fallback: локальный файл
                reminders = _load_reminders()
                if 0 <= rid < len(reminders):
                    removed = reminders.pop(rid)
                    _save_reminders(reminders)
                    await update.message.reply_text(f"✅ Удалено: {removed.get('note','')}")
                else:
                    await update.message.reply_text("Неверный ID.")
        except ValueError:
            await update.message.reply_text("Укажи ID: /remind del <id>")
        return

    phone = args[0]
    due_date = args[1] if len(args) > 1 else ""
    note = " ".join(args[2:]) if len(args) > 2 else ""

    # CRM API + локальный fallback
    rem_data = {
        "phone": norm_phone(phone) if phone else phone,
        "due_date": due_date,
        "note": note or f"Перезвонить {phone}",
    }
    api_res = crm_save_reminder(rem_data["phone"], due_date, rem_data["note"])
    if not api_res:
        reminders = _load_reminders()
        reminders.append({**rem_data, "created": datetime.now().isoformat(), "done": False})
        _save_reminders(reminders)

    msg = f"✅ Напоминание создано"
    if due_date:
        msg += f" на {due_date}"
    if note:
        msg += f": {note}"
    await update.message.reply_text(msg)


async def _check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Периодическая проверка напоминаний (запускается из main)."""
    reminders = crm_get_reminders()
    if not reminders:
        reminders = _load_reminders()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    changed = False

    for r in reminders:
        if r.get("done"):
            continue
        due = r.get("due_date", "")
        if due and due <= today:
            rid = r.get("id")
            if rid is not None:
                crm_toggle_reminder(rid)
            changed = True
            text = (
                f"⏰ <b>Напоминание!</b>\n"
                f"Телефон: +{r.get('phone', '?')}\n"
                f"{r.get('note', 'Перезвонить клиенту')}"
            )
            try:
                await context.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=text,
                    parse_mode="HTML",
                )
            except Exception as e:
                log.error("Reminder notify: %s", e)

    if changed:
        _save_reminders(reminders)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Загрузка CSV/XLS/TXT через Telegram."""
    st = get_state(update.effective_chat.id)
    doc = update.message.document
    if not doc or not doc.file_name:
        return

    fname = doc.file_name.lower()
    if not (fname.endswith(".csv") or fname.endswith(".xls") or fname.endswith(".xlsx") or fname.endswith(".txt")):
        await update.message.reply_text("⚠️ Отправь CSV, XLS(X) или TXT файл с контактами")
        return

    file = await doc.get_file()
    csv_dir = DATA_DIR / "operator_csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    raw_path = csv_dir / f"{update.effective_user.id}_{doc.file_name}"
    await file.download_to_drive(raw_path)

    # Конвертация XLS/XLSX → CSV
    if fname.endswith(".xls") or fname.endswith(".xlsx"):
        try:
            import pandas as pd
            df = pd.read_excel(raw_path)
            converted = raw_path.with_suffix(".csv")
            df.to_csv(converted, index=False, encoding="utf-8")
            raw_path = converted
        except ImportError:
            await update.message.reply_text("⚠️ Нужен pandas: pip install pandas openpyxl")
            return
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка конвертации XLS: {e}")
            return

    # Парсинг TXT (один номер на строку) → CSV
    if fname.endswith(".txt"):
        try:
            phones = []
            with open(raw_path, "r", encoding="utf-8") as f:
                for line in f:
                    p = norm_phone(line.strip())
                    if is_valid_phone(p):
                        phones.append(p)
            converted = raw_path.with_suffix(".csv")
            with open(converted, "w", encoding="utf-8", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["Название", "Описание", "Регион", "Город", "Имя", "Телефоны"])
                for p in phones:
                    writer.writerow(["", "", "", "", "", p])
            raw_path = converted
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка парсинга TXT: {e}")
            return

    st.csv_path = str(raw_path)

    count = 0
    try:
        with open(raw_path, "r", encoding="utf-8") as fh:
            count = sum(1 for _ in fh) - 1
    except Exception:
        pass

    keyboard = ReplyKeyboardMarkup(IDLE_BUTTONS, resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(
        f"✅ Загружено: <b>{doc.file_name}</b>\n"
        f"Контактов: ~{count}\n\n"
        f"Нажми <b>▶ Начать обзвон</b>",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def cmd_stoplist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stoplist — просмотр и добавление номеров в стоп-лист (ФЗ-152)."""
    args = context.args
    if args:
        phone = " ".join(args)
        if add_to_stoplist(phone):
            await update.message.reply_text(f"🛑 {norm_phone(phone)} добавлен в стоп-лист")
        else:
            await update.message.reply_text(
                f"⚠️ Не удалось добавить {phone} (неверный формат или уже в стоп-листе)"
            )
        return

    blocked = load_stoplist()
    if not blocked:
        await update.message.reply_text("🛑 Стоп-лист пуст")
        return
    lines = [f"🛑 <b>Стоп-лист ({len(blocked)})</b>:"]
    for p in sorted(blocked):
        lines.append(f"  • +{p}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = get_state(update.effective_chat.id)
    text = (update.message.text or "").strip()

    # Если ждём конспект — обрабатываем как summary
    if st.waiting_for_summary:
        st.waiting_for_summary = False
        await _process_summary(update, context, text)
        return

    if text == "▶ Начать обзвон" or ("начать" in text.lower() and "обзвон" in text.lower()):
        await start_dialing(update, context, st, carousel=False)
    elif text == "🎠 Карусель" or "карусель" in text.lower():
        if st.active:
            st.carousel = True
            st.waiting_for_next = False
            if st.next_event:
                st.next_event.set()
            kb = ReplyKeyboardMarkup(CAROUSEL_BUTTONS, resize_keyboard=True, is_persistent=True)
            await update.message.reply_text("🎠 Режим карусели включён", reply_markup=kb)
        else:
            await start_dialing(update, context, st, carousel=True)
    elif text == "⏹ Стоп" or "конец" in text.lower() or "стоп" in text.lower() or "остановить" in text.lower():
        await stop_dialing(update, context, st)
    elif text == "⏩ Пропустить" or "пропустить" in text.lower() or "скип" in text.lower() or "skip" in text.lower():
        await skip_contact(update, context, st)
    elif text == "⏭ Следующий" or "следующий" in text.lower() or "дальше" in text.lower() or "next" in text.lower():
        await next_contact(update, context, st)
    elif text == "📊 Статус" or "статус" in text.lower() or "стат" in text.lower():
        await show_status(update, context, st)
    else:
        kb = ReplyKeyboardMarkup(
            CAROUSEL_BUTTONS if st.carousel and st.active else
            WAIT_BUTTONS if st.waiting_for_next else
            DIALING_BUTTONS if st.active else
            IDLE_BUTTONS,
            resize_keyboard=True, is_persistent=True,
        )
        await update.message.reply_text(
            "Используй кнопки или команды: начать обзвон / карусель / стоп / пропустить / следующий / статус",
            reply_markup=kb,
        )


async def start_dialing(update: Update, context: ContextTypes.DEFAULT_TYPE, st: DialerState, carousel: bool = False):
    """Начать цикл обзвона."""
    if st.active:
        await update.message.reply_text("⚠️ Обзвон уже идёт!")
        return

    csv_path = st.csv_path or os.environ.get("LEVITAN_DEFAULT_CSV") or CSV_PATH
    is_weekend = datetime.now().weekday() >= 5
    contacts = load_contacts(weekend_only=is_weekend, csv_path=csv_path)
    already_called = load_already_called()
    contacts = [c for c in contacts if c["phone"] not in already_called]

    # Стоп-лист (ФЗ-152: право на отзыв согласия)
    blocked = load_stoplist()
    if blocked:
        before = len(contacts)
        contacts = [c for c in contacts if c["phone"] not in blocked]
        if before != len(contacts):
            log.info("Стоп-лист: исключено %d номеров", before - len(contacts))

    if not contacts:
        await update.message.reply_text("✅ Все контакты обзвонены!")
        return

    st.contacts = contacts
    st.current_idx = 0
    st.active = True
    st.carousel = carousel
    st.stats = Counter()
    st.results = []

    week_label = "🌾 Только КФХ/ИП" if is_weekend else "🏢 Все (включая ООО)"
    src_label = f"📁 {Path(csv_path).name}" if st.csv_path else "📁 общая база"

    mode_label = "🎠 Карусель" if carousel else "🔄 Ручной"
    keyboard = ReplyKeyboardMarkup(CAROUSEL_BUTTONS if carousel else DIALING_BUTTONS, resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(
        f"🚀 <b>Обзвон запущен!</b>\n"
        f"Режим: {mode_label}\n"
        f"Контактов: {len(contacts)}\n"
        f"{src_label}\n"
        f"{week_label}\n\n"
        f"Сейчас набираю первый номер...",
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    st.chat_id = str(update.effective_chat.id)
    asyncio.create_task(dialing_loop(context, st))


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stop — остановить обзвон."""
    st = get_state(update.effective_chat.id)
    await stop_dialing(update, context, st)

async def stop_dialing(update: Update, context: ContextTypes.DEFAULT_TYPE, st: DialerState):
    """Остановить обзвон."""
    if not st.active:
        await update.message.reply_text("Обзвон не запущен.")
        return

    st.active = False
    st.carousel = False
    if st.next_event:
        st.next_event.set()
    total = sum(st.stats.values())
    conv_line = f"\n📈 Конверсия: {st.stats['lead']/total*100:.1f}%" if total else ""

    keyboard = ReplyKeyboardMarkup(IDLE_BUTTONS, resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(
        f"🏁 <b>Обзвон завершён!</b>\n\n"
        f"📊 Итого: {total} звонков\n"
        f"🟢 Лиды: {st.stats['lead']}\n"
        f"🟡 Перезвон: {st.stats['callback']}\n"
        f"🔴 Отказ: {st.stats['rejected'] + st.stats['no_interest']}\n"
        f"⚫ Не взял: {st.stats['no_answer']}"
        f"{conv_line}",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def cmd_backfill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /backfill — подтянуть конспекты из Mango для существующих контактов."""
    msg = await update.message.reply_text("🔄 Загружаю конспекты из Mango S2T...")
    try:
        from mango_s2t import fetch_summary_by_phone
    except ImportError:
        await msg.edit_text("❌ mango_s2t.py не найден")
        return

    contacts = crm_get_contacts()
    if not contacts:
        await msg.edit_text("Нет контактов в CRM")
        return

    done = 0
    skipped = 0
    errors = 0
    for c in contacts:
        phone = c.get("phone", "")
        existing_transcript = c.get("transcript", "")
        if existing_transcript and len(existing_transcript) > 20:
            skipped += 1
            continue
        try:
            ts = c.get("timestamp", "")
            after_ts = 0
            if ts:
                try:
                    after_ts = datetime.fromisoformat(ts).timestamp()
                except Exception:
                    after_ts = 0
            if not after_ts:
                continue

            summary = fetch_summary_by_phone(phone, after_ts, timeout=45)
            if summary:
                crm_update_contact(c["id"], {"transcript": summary})
                done += 1
                if done % 3 == 0:
                    await msg.edit_text(f"🔄 Обработано: {done}/{len(contacts)}, пропущено: {skipped}")
        except Exception as e:
            log.error("Backfill %s: %s", phone, e)
            errors += 1

    await msg.edit_text(
        f"✅ Готово!\n"
        f"📥 Загружено конспектов: {done}\n"
        f"⏭ Пропущено (уже есть): {skipped}\n"
        f"❌ Ошибок: {errors}"
    )


async def skip_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, st: DialerState):
    """Пропустить текущий контакт."""
    if not st.active:
        await update.message.reply_text("Обзвон не запущен.")
        return

    st.current_idx += 1
    st.waiting_for_hangup = False
    if st.next_event:
        st.next_event.set()
    await update.message.reply_text("⏭ Пропущен. Набираю следующий...")


async def next_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, st: DialerState):
    """Команда «следующий» — продолжить обзвон."""
    if not st.active:
        await update.message.reply_text("Обзвон не запущен.")
        return
    if not st.waiting_for_next:
        await update.message.reply_text("Обзвон не приостановлен.")
        return
    st.waiting_for_next = False
    if st.next_event:
        st.next_event.set()


async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE, st: DialerState):
    """Показать статистику."""
    total = sum(st.stats.values())
    remaining = len(st.contacts) - st.current_idx if st.contacts else 0

    text = (
        f"📊 <b>Статус</b>\n\n"
        f"Активен: {'✅' if st.active else '❌'}\n"
        f"Звонков: {total}\n"
        f"Осталось: {remaining}\n"
        f"🟢 Лиды: {st.stats['lead']}\n"
        f"🟡 Перезвон: {st.stats['callback']}\n"
        f"🔴 Отказ: {st.stats['rejected'] + st.stats['no_interest']}\n"
    )
    if total and st.stats["lead"]:
        text += f"📈 Конверсия: {st.stats['lead']/total*100:.1f}%\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")



# ============================================================
# BACKGROUND CALL PROCESSING
# ============================================================

async def process_call_background(
    bot, chat_id: str, contact: dict, call_start: float, st: DialerState
):
    """Обработка звонка в фоне: запись → Mango S2T конспект → LLM → CRM → Telegram."""
    recording_id = await asyncio.to_thread(
        wait_for_disconnect_and_recording, contact["phone"], call_start
    )

    # 1. Пробуем Mango Speech2Text (расшифровка из Речевой аналитики)
    mango_transcript = None
    try:
        from mango_s2t import fetch_summary
        mango_transcript = await asyncio.to_thread(
            fetch_summary, contact["phone"], call_start, 60
        )
    except Exception:
        pass

    if mango_transcript:
        transcript = mango_transcript
        st.stats["s2t_mango"] = st.stats.get("s2t_mango", 0) + 1
        log.info("Mango S2T transcript for %s: %d chars", contact["phone"], len(transcript))
    elif recording_id:
        # 2. Fallback: Whisper STT через MP3
        try:
            transcript = await asyncio.to_thread(process_recording, recording_id)
        except Exception:
            transcript = None
    else:
        transcript = None

    if transcript:
        extracted = await asyncio.to_thread(extract_crm_data, transcript, contact)
    else:
        extracted = {
            "status": "no_contact",
            "contact_name": contact.get("contact_name", ""),
            "product": contact.get("description", ""),
            "volume": "",
            "ready_date": "",
            "price_info": "",
            "notes": "Не ответил" if not recording_id else "STT не удался",
        }

    # Добавляем ссылку на запись в заметки
    if recording_id:
        recording_link = f"https://app.mango-office.ru/vpbx/queries/recording/post?action=download&recording_id={recording_id}"
        crm_notes = extracted.get("notes", "")
        if crm_notes:
            crm_notes += f"\n🎙 Запись: {recording_link}"
        else:
            crm_notes = f"🎙 Запись: {recording_link}"
        extracted["notes"] = crm_notes

    saved = save_to_crm(contact, extracted, transcript or "", recording_id or "")
    st.stats[extracted.get("status", "no_contact")] += 1
    st.results.append(saved)

    # Авто-стоп-лист: если клиент попросил не звонить (ФЗ-152)
    STOP_WORDS = [
        "не звоните", "вычеркните", "больше не беспокойте", "не беспокойте",
        "не надо звонить", "перестаньте звонить", "уберите из базы",
        "не звони", "вычеркни", "не буду с вами",
    ]
    haystack = f"{transcript or ''}\n{extracted.get('notes', '')}\n{extracted.get('contact_name', '')}".lower()
    if any(w in haystack for w in STOP_WORDS):
        if add_to_stoplist(contact["phone"]):
            log.info("Стоп-лист: добавлен %s (клиент попросил не звонить)", contact["phone"])
            saved["status"] = "blocked"
            saved["notes"] = (saved.get("notes", "") + "\n🛑 Клиент попросил не звонить — в стоп-листе").strip()

    status_emoji = {
        "lead": "🟢", "callback": "🟡", "rejected": "🔴",
        "no_interest": "⚪", "no_contact": "⚫", "no_answer": "⚫", "other": "⚫",
        "blocked": "🛑",
    }
    emoji = status_emoji.get(saved["status"], "⚫")

    crm_card = (
        f"{emoji} <b>Результат</b>\n\n"
        f"🏢 {saved['company_name']}\n"
        f"📍 {saved.get('region', '')} {saved.get('city', '')}\n"
        f"🏠 {saved.get('address', '') or '—'}\n"
        f"📱 +{saved['phone']}\n"
        f"👤 {saved['contact_name'] or '—'}\n"
        f"🌾 {saved['product'] or '—'}\n"
        f"📦 {saved['volume'] or '—'}\n"
        f"📅 {saved['ready_date'] or '—'}\n"
        f"💰 {saved['price_info'] or '—'}\n"
        f"📝 {saved['notes'] or '—'}\n"
        f"\n📊 Лиды: {st.stats['lead']}"
    )
    try:
        await bot.send_message(chat_id=chat_id, text=crm_card, parse_mode="HTML")
    except Exception as e:
        log.error(f"Send result error: {e}")


# ============================================================
# MAIN DIALING LOOP
# ============================================================

async def dialing_loop(context: ContextTypes.DEFAULT_TYPE, st: DialerState):
    """Основной цикл обзвона."""
    chat_id = st.chat_id
    pending_tasks: list[asyncio.Task] = []

    while st.active and st.current_idx < len(st.contacts):
        contact = st.contacts[st.current_idx]
        st.current_contact = contact

        # CRM enrichment
        contact = await _enrich_contact(contact)

        # Уведомляем о следующем звонке
        kb = ReplyKeyboardMarkup(CAROUSEL_BUTTONS if st.carousel else DIALING_BUTTONS, resize_keyboard=True, is_persistent=True)
        address_line = f"🏠 {contact.get('address', '')[:60]}\n" if contact.get("address") else ""
        contact_line = f"👤 {contact['contact_name']}" if contact.get("contact_name") else ""
        enrich_line = f"💼 {contact['position']}" if contact.get("position") else ""
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📞 <b>Звоню #{st.current_idx + 1}</b>\n"
                f"🏢 {contact['name'][:40]}\n"
                f"📍 {contact['region']}, {contact['city']}\n"
                f"{address_line}"
                f"🌾 {contact['description'][:40]}\n"
                f"📱 +{contact['phone']}\n"
                f"{contact_line}"
                f"{enrich_line}"
            ),
            parse_mode="HTML",
            reply_markup=kb,
        )

        # Callback
        st.call_start = time.time()
        result = mango_callback(contact["phone"], st.ext)

        if result.get("result") in (1000, "1000"):
            save_already_called(contact["phone"])

        if result.get("result") not in (1000, "1000") and "error" not in result:
            pass
        elif "error" in result:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ Ошибка вызова: {result.get('error', result)}",
            )
            st.current_idx += 1
            continue

        # Стартуем обработку в фоне (ждёт запись, STT, LLM, CRM)
        task = asyncio.create_task(
            process_call_background(
                context.bot, chat_id, contact, st.call_start, st
            )
        )
        pending_tasks.append(task)
        pending_tasks = [t for t in pending_tasks if not t.done()]

        # Сразу переходим к следующему контакту
        st.current_idx += 1

        # Сразу переходим к следующему контакту
        st.current_idx += 1

        # Ждём команду «следующий» (в карусели — авто 5 сек)
        if st.active and st.current_idx < len(st.contacts):
            st.next_event = asyncio.Event()
            st.waiting_for_next = True
            if st.carousel:
                keyboard = ReplyKeyboardMarkup(CAROUSEL_BUTTONS, resize_keyboard=True, is_persistent=True)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="⏸ Карусель: следующий через 5 сек",
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
                try:
                    await asyncio.wait_for(st.next_event.wait(), timeout=5)
                except asyncio.TimeoutError:
                    pass
            else:
                keyboard = ReplyKeyboardMarkup(WAIT_BUTTONS, resize_keyboard=True, is_persistent=True)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="⏸ Нажми <b>⏭ Следующий</b> для продолжения",
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
                await st.next_event.wait()
            st.waiting_for_next = False
            st.next_event = None

    # Обзвон завершён
    if st.active:
        st.active = False
        total = sum(st.stats.values())
        keyboard = ReplyKeyboardMarkup(IDLE_BUTTONS, resize_keyboard=True, is_persistent=True)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ <b>Все контакты обзвонены!</b>\nВсего: {total} звонков",
            parse_mode="HTML",
            reply_markup=keyboard,
        )


def wait_for_disconnect_and_recording(phone: str, call_start: float, timeout: int = 120) -> Optional[str]:
    """
    Ждать завершения звонка и появления записи.
    Timeout = 120 сек (макс длина звонка).
    """
    # Ждём минимум 10 сек (время на дозвон + короткий разговор)
    time.sleep(10)

    # Потом ищем запись
    return wait_for_recording(phone, call_start, timeout=timeout - 10)


# ============================================================
# MAIN
# ============================================================

def main():
    global MANGO_FROM_EXTENSION, TELEGRAM_CHAT_ID, MY_PHONE

    import argparse
    parser = argparse.ArgumentParser(description="Levitan Dialer Bot")
    parser.add_argument("--ext", type=str, default=MANGO_FROM_EXTENSION,
                        help="Mango extension (default: %(default)s)")
    parser.add_argument("--chat-id", type=str, default=TELEGRAM_CHAT_ID,
                        help="Telegram chat ID for notifications")
    parser.add_argument("--phone", type=str, default=MY_PHONE,
                        help="Operator phone number (default: %(default)s)")
    parser.add_argument("--csv", type=str, default=None,
                        help="Path to custom CSV contact file")
    parser.add_argument("--start", action="store_true",
                        help="Auto-start campaign on launch")
    args = parser.parse_args()

    MANGO_FROM_EXTENSION = args.ext
    TELEGRAM_CHAT_ID = args.chat_id
    MY_PHONE = args.phone

    if args.csv:
        os.environ["LEVITAN_DEFAULT_CSV"] = args.csv
        log.info(f"Default CSV: {args.csv}")

    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  TELEGRAM_BOT_TOKEN не задан в .env!")
        sys.exit(1)

    if not MANGO_API_KEY:
        print("⚠️  MANGO_VPBX_API_KEY не задан в .env!")
        sys.exit(1)

    print("🤖 Levitan Dialer Bot starting...")
    print(f"   Mango ext: {MANGO_FROM_EXTENSION}")
    print(f"   Operator phone: +{MY_PHONE}")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"   VPS: {VPS_HOST}")

    # Выбираем работающий прокси автоматически. Если ни один не работает —
    # бот попытается подключиться напрямую (в РФ обычно не работает).
    saved_proxy = _pick_working_proxy()
    for k in ("ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "TELEGRAM_PROXY", "all_proxy", "http_proxy", "https_proxy"):
        os.environ.pop(k, None)
    proxy_msg = _mask_proxy_url(saved_proxy) if saved_proxy else "none"
    print(f"   Proxy: {proxy_msg}")

    builder = Application.builder().token(TELEGRAM_BOT_TOKEN)
    if saved_proxy:
        req = HTTPXRequest(proxy=saved_proxy, connect_timeout=30, read_timeout=30)
        builder = builder.request(req).get_updates_request(req)
    app = builder.build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ext", cmd_ext))
    app.add_handler(CommandHandler("summary", cmd_summary))
    app.add_handler(CommandHandler("crm", cmd_crm))
    app.add_handler(CommandHandler("remind", cmd_remind))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("stoplist", cmd_stoplist))
    app.add_handler(CommandHandler("backfill", cmd_backfill))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("   Bot ready. Polling...")

    if args.start:
        chat_id = int(os.environ.get("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID or "176203333"))
        default_csv = os.environ.get("LEVITAN_DEFAULT_CSV") or str(CSV_PATH)
        print(f"   --start mode: chat={chat_id}, csv={default_csv}")

        async def auto_start(app):
            import asyncio
            await asyncio.sleep(2)
            st = get_state(chat_id)
            st.chat_id = str(chat_id)
            if Path(default_csv).exists():
                st.csv_path = default_csv
            from telegram import ReplyKeyboardMarkup
            kb = ReplyKeyboardMarkup(IDLE_BUTTONS, resize_keyboard=True, is_persistent=True)
            await app.bot.send_message(
                chat_id=chat_id,
                text="🎙 <b>Levitan Dialer Bot готов</b>\n▶ Начать обзвон — ручной режим\n🎠 Карусель — автодозвон",
                parse_mode="HTML",
                reply_markup=kb,
            )

        app.post_init = auto_start

    # Периодическая проверка напоминаний (каждый час)
    app.job_queue.run_repeating(_check_reminders, interval=3600, first=30)

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
        poll_interval=1.0,
        timeout=30,
    )


if __name__ == "__main__":
    main()
