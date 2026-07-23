# !/usr/bin/env python3
"""Levitan FAQ-Agent — Анжелла, бройлеры (ai-eggs × Левитан).

Архитектура (как Айка, но с большим кэшем):
    Клиент (телефон) → Mango callback → baresip (8kHz PCM s16)
        → STT (faster-whisper) → ТЕКСТ
        → FAQ-КЭШ (fuzzy match ~110 триггеров) → ТАК: мгновенный TTS (без LLM!)
        → ИНАЧЕ: LLM (DeepSeek/Claude) → TTS
        → баресип проигрывает WAV клиенту

Ключевая идея: ~110 типовых вопросов по бройлерам предзагружены как
готовые реплики → ответ ЗАДЕРЖКА = только синтез TTS (~200-400мс),
без обращения к LLM (которое даёт +2-4с). Нетиповой вопрос → LLM.

Источник знаний: ai-eggs (Азовский инкубатор) → docs/ANGELLA_BROILERS_*.
"""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import threading
import uuid
import wave
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

import requests

# === CONFIG (из .env) ===
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")
MANGO_FROM_NUMBER = os.getenv("MANGO_FROM_NUMBER", "")

# Пути
BARESIP_AUFILE_PATH = Path(os.getenv("BARESIP_AUFILE_PATH", "/tmp/levitan_play.wav"))
BARESIP_RECORD_DIR = Path(os.getenv("BARESIP_RECORD_DIR", str(Path.home() / ".baresip" / "recordings")))
GREETING_WAV = Path(os.getenv("LEVITAN_GREETING_WAV", "/tmp/levitan_greeting_lead.wav"))
TTS_OUTPUT_DIR = Path("/tmp/levitan_tts")
TTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(os.getenv("LEVITAN_LOG_DIR", "/var/log/levitan"))
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_PATH = LOG_DIR / "events.jsonl"
DIALOGS_DIR = LOG_DIR / "dialogs"
DIALOGS_DIR.mkdir(parents=True, exist_ok=True)

# Параметры диалога
MAX_TURNS = int(os.getenv("LEVITAN_MAX_TURNS", "12"))
CALLBACK_DELAY = float(os.getenv("LEVITAN_CALLBACK_DELAY", "2.5"))
RECORDING_WAIT_TIMEOUT = int(os.getenv("LEVITAN_RECORDING_WAIT", "30"))
MIN_RECORDING_SIZE = 2000

# FAQ-кэш
FAQ_MATCH_THRESHOLD = float(os.getenv("LEVITAN_FAQ_THRESHOLD", "0.72"))  # порог fuzzy-совпадения
FAQ_CACHE_PATH = Path(__file__).resolve().parent.parent / "docs" / "ANGELLA_BROILERS_FAQ_CACHE.json"


# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "faq_agent.log")],
)
log = logging.getLogger("levitan-faq")


# === SYSTEM PROMPT (Анжелла, бройлеры, turn-based) ===
SYSTEM_PROMPT = """Ты — Анжелла, голосовой менеджер Азовского инкубатора (IncuBird). Ты отвечаешь клиентам по телефону про бройлеров.

КОМПАНИЯ: Азовский инкубатор, Крым, пгт Азовское, ул. Железнодорожная 42. Телефон +7 (918) 047-51-07.
Самовывоз — только Крым (Азовское, 14:00–17:00). В Москву самовывоза нет.
Доставка — по ПН и ЧТ по Крыму и Югу России (Краснодар, Ростов, Волгоград, Ставрополь), спецтранспорт с климат-контролем. Гарантия 100% выживаемости при доставке.
Оплата: наличные при получении, перевод на карту, по реквизитам. Предоплата 50%.

АССОРТИМЕНТ (июль–декабрь 2026 — ТОЛЬКО бройлеры):
— КОББ-500: до 2.5 кг за 40 дней, мощная грудка. Для бизнеса/откорма.
— РОСС-308: выносливее, крепче здоровьем. Для дома и новичков — рекомендуем его.
Минимальный заказ — от 50 голов одной породы.
ЦЕНЫ (tiered): до 100 голов — 90₽/шт, 101-300 — 85₽/шт, 301-999 — 80₽/шт, от 1000 — 75₽/шт.
График вывода: каждый ПН и ЧТ. Дата вывода ≠ дата доставки (вывод 24-го = доставка 25-го).
Вывод: Июль 2,9,16,23,30 · Авг 7,14,21,28 · Сен 3,10,17,24 · Окт 1,8,15,22,29 · Ноя 6,13,20,27 · Дек 4,18.

ВАКЦИНАЦИЯ И ЗДОРОВЬЕ: базовая вакцинация на инкубатории (Марек, Гамборо, Ньюкасл), ветсвидетельство в каждой партии. Аптечка (200₽) — рекомендуем.
КОРМ (cross-sell ТОЛЬКО после телефона): Purina Старт 990₽, Рост 950₽, Финиш 890₽ (25кг). Energy дешевле. ~185₽ на голову за 42 дня.

СТИЛЬ (голос, естественность — главное): говори живо, тепло, как заботливая хозяйка, но по-деловому. Коротко: 1–2 предложения, один вопрос за раз. Не дави. Цену называй СРАЗУ с порогом (от 50 голов). Не выдумывай породы/цены. Другую птицу (утки/индюки/гуси) летом не возим — вежливо направляй на бройлеров.

ВОРОНКА: 1) польза/ответ → 2) уточнить объём, город, дату → 3) ЗАПРОСИТЬ ТЕЛЕФОН («чтобы забронировать партию за вами») → 4) ТОЛЬКО ПОСЛЕ телефона предлагай корм/аптечку → 5) зафиксировать лид.
НЕ предлагай корм и допы ДО получения телефона.
Когда собрала породу, количество, город и телефон — заверши диалог подтверждением."""


# === FAQ CACHE ===
_faq_cache: dict = {}
def load_faq_cache() -> dict:
    global _faq_cache
    try:
        data = json.loads(FAQ_CACHE_PATH.read_text(encoding="utf-8"))
        # отфильтровываем _meta
        _faq_cache = {k: v for k, v in data.items() if not k.startswith("_")}
        log.info(f"FAQ-кэш загружен: {len(_faq_cache)} триггеров")
    except Exception as e:
        log.error(f"FAQ load error: {e}")
        _faq_cache = {}
    return _faq_cache

def _normalize(text: str) -> str:
    """Нормализация текста для fuzzy match."""
    text = text.lower()
    text = re.sub(r"[ёйЁЙ]", lambda m: {"ё": "е", "й": "и"}.get(m.group(), m.group()), text)
    text = re.sub(r"[^а-яа-я0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def faq_lookup(transcript: str) -> Optional[str]:
    """Поиск по FAQ-кэшу. Возвращает готовую реплику или None.

    Использует fuzzy match (SequenceMatcher) по нормализованному тексту.
    Порог FAH_MATCH_THRESHOLD (0.72) — выше = точнее совпадение.
    Возвращает реплику ТОЛЬКО при уверенном совпадении → мгновенный ответ.
    """
    if not _faq_cache:
        return None
    norm = _normalize(transcript)
    if len(norm) < 3:
        return None

    best_score = 0.0
    best_reply = None
    for trigger, reply in _faq_cache.items():
        score = SequenceMatcher(None, norm, trigger).ratio()
        # бонус если ключевые слова совпадают
        if score > best_score:
            best_score = score
            best_reply = reply

    if best_score >= FAQ_MATCH_THRESHOLD:
        log.info(f"FAQ HIT ({best_score:.2f}): «{norm[:50]}» → мгновенный ответ")
        return best_reply
    # частичное совпадение ключевых слов
    for trigger, reply in _faq_cache.items():
        if len(trigger) >= 5 and trigger in norm:
            log.info(f"FAQ HIT (substring): «{trigger}» → мгновенный ответ")
            return reply
    return None


# === MANGO API ===
def _mango_sign(payload: dict) -> str:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()

def mango_callback(phone: str, command_id: str = "") -> dict:
    if not command_id:
        command_id = f"levitan_{uuid.uuid4().hex[:8]}"
    # Mango при callback звонит на SIP URI = from.number (username), НЕ extension!
    # sip:22@... → 403, sip:user1@... → 200 OK (см. STATUS.md)
    from_field = {"extension": MANGO_FROM_EXTENSION}
    if MANGO_FROM_NUMBER:
        from_field["number"] = MANGO_FROM_NUMBER
    payload = {
        "command_id": command_id,
        "from": from_field,
        "to_number": _norm_phone(phone),
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()
    try:
        r = requests.post(
            f"{MANGO_API_BASE}commands/callback",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        result = r.json()
        log.info(f"Callback → {phone}: {result}")
        return result
    except Exception as e:
        log.error(f"Callback failed: {e}")
        return {"error": str(e)}

def mango_download_recording(recording_id: str, output_path: str) -> bool:
    payload = {"recording_id": recording_id}
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()
    try:
        r = requests.post(
            f"{MANGO_API_BASE}queries/recording/post",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
            timeout=60, stream=True,
        )
        if r.status_code == 200 and len(r.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(r.content)
            log.info(f"Recording downloaded: {output_path} ({len(r.content)} bytes)")
            return True
        else:
            log.warning(f"Recording download failed: status={r.status_code}")
            return False
    except Exception as e:
        log.error(f"Recording download error: {e}")
        return False

def _norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    return d


# === BARESIP AUDIO ===
def set_baresip_audio(wav_path: Path):
    try:
        shutil.copy2(str(wav_path), str(BARESIP_AUFILE_PATH))
        log.info(f"Baresip audio set: {wav_path.name} → {BARESIP_AUFILE_PATH}")
        return True
    except Exception as e:
        log.error(f"Failed to set baresip audio: {e}")
        return False

def get_latest_recording(after_timestamp: float = 0) -> Optional[Path]:
    recordings = []
    for pattern in ["dump-*-dec.wav", "*.wav"]:
        for f in BARESIP_RECORD_DIR.glob(pattern):
            if f.stat().st_mtime > after_timestamp and f.stat().st_size > MIN_RECORDING_SIZE:
                recordings.append(f)
    if not recordings:
        return None
    recordings.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return recordings[0]

def wait_for_recording(after_timestamp: float, timeout: int = RECORDING_WAIT_TIMEOUT) -> Optional[Path]:
    start = time.time()
    while time.time() - start < timeout:
        rec = get_latest_recording(after_timestamp)
        if rec:
            time.sleep(1.0)
            return rec
        time.sleep(0.5)
    return None


# === STT (faster-whisper) ===
_whisper_model = None
def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        log.info("Whisper model loaded")
    return _whisper_model

def transcribe(wav_path: str) -> str:
    try:
        model = get_whisper()
        segments, info = model.transcribe(
            wav_path, language="ru", beam_size=5,
            vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
        )
        text = " ".join(s.text for s in segments).strip()
        log.info(f"STT [{Path(wav_path).name}]: «{text[:100]}»")
        return text
    except Exception as e:
        log.error(f"STT error: {e}")
        return ""


# === LLM (OpenRouter, fallback при нетиповом вопросе) ===
def llm_response(transcript: list[dict]) -> str:
    """Генерация ответа через LLM (OpenRouter primary, Yandex fallback).
    Если оба LLM недоступны — возвращает безопасный шаблонный ответ."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(transcript[-10:])
    last_user = transcript[-1]["content"] if transcript and transcript[-1]["role"] == "user" else ""

    # 1. OpenRouter
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "HTTP-Referer": "https://levitan.app"},
            json={"model": "deepseek/deepseek-chat-v3-0324", "messages": messages, "max_tokens": 150, "temperature": 0.7},
            timeout=25,
        )
        if r.status_code == 200:
            resp = r.json()["choices"][0]["message"]["content"].strip()
            log.info(f"LLM (OpenRouter): «{resp[:100]}»")
            return resp
    except Exception as e:
        log.warning(f"OpenRouter LLM error: {e}")

    # 2. Yandex Foundation Models (fallback)
    if YC_API_KEY_TTS and YC_FOLDER_ID_TTS:
        try:
            r = requests.post(
                "https://llm.api.cloud.yandex.net/llm/v1/chat/completions",
                headers={"Authorization": f"Api-Key {YC_API_KEY_TTS}"},
                json={"modelUri": f"gpt://{YC_FOLDER_ID_TTS}/yandexgpt-lite",
                      "messages": [{"role": m["role"], "text": m["content"]} for m in messages]},
                timeout=25,
            )
            if r.status_code == 200:
                resp = r.json()["result"]["alternatives"][0]["message"]["text"].strip()
                log.info(f"LLM (Yandex): «{resp[:100]}»")
                return resp
        except Exception as e:
            log.warning(f"Yandex LLM error: {e}")

    # 3. Локальный fallback (без LLM)
    log.warning("LLM unavailable — local template fallback")
    return _local_fallback(last_user)

def _local_fallback(text: str) -> str:
    """Безопасный шаблонный ответ без LLM (для автономного режима)."""
    t = text.lower()
    if extract_phone(text):
        return "Отлично, записала ваш номер! Менеджер перезвонит и подтвердит заказ. До скорой связи!"
    if any(w in t for w in ["москв", "питер", "спб", "санкт"]):
        return "В Москву и Питер пока не доставляем — только Крым и Юг России. Если есть знакомые на юге — подскажите им!"
    if "почему" in t and ("дорог" in t or "цена" in t):
        return "Цена от 75 рублей с гарантией выживаемости и вакцинацией — это выгодно. Дешевле — риск потерять половину. А при объёме от тысячи цена падает до 75!"
    if any(w in t for w in ["когда", "сколько врем", "срок"]):
        return "Вывод каждый понедельник и четверг. Доставка на следующий день спецтранспортом."
    if any(w in t for w in ["оплат", "перевод", "карт"]):
        return "Оплата наличными при получении, перевод на карту или по реквизитам. Предоплата 50%."
    if any(w in t for w in ["гарант", "дохл", "доx", "умер"]):
        return "Гарантия сто процентов! Если что-то в дороге — заменим бесплатно. Вакцинация входит."
    return "Хороший вопрос! Я записала его — наш менеджер перезвонит и ответит подробнее. Оставьте, пожалуйста, ваш номер?"


# === TTS (Яндекс SpeechKit primary, edge-tts fallback) ===
YC_API_KEY_TTS = os.getenv("YC_API_KEY", os.getenv("YC_API_KEY_TTS", ""))
YC_FOLDER_ID_TTS = os.getenv("YC_FOLDER_ID", os.getenv("YC_FOLDER_ID_TTS", ""))
TTS_VOICE = os.getenv("TTS_VOICE", "alena")  # Яндекс голос (Алёна)

def _tts_yandex(text: str) -> Optional[bytes]:
    """Синтез через Яндекс SpeechKit → PCM 8000Hz mono s16le."""
    if not YC_API_KEY_TTS or not YC_FOLDER_ID_TTS:
        return None
    try:
        r = requests.post(
            "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize",
            headers={"Authorization": f"Api-Key {YC_API_KEY_TTS}"},
            data={
                "text": text, "folderId": YC_FOLDER_ID_TTS, "lang": "ru-RU",
                "voice": TTS_VOICE, "format": "lpcm", "sampleRateHertz": 8000,
            },
            timeout=30,
        )
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        log.warning(f"Yandex TTS status {r.status_code}: {r.text[:120]}")
        return None
    except Exception as e:
        log.error(f"Yandex TTS error: {e}")
        return None

def _tts_edge(text: str, voice: str = "ru-RU-DariyaNeural") -> Optional[Path]:
    """Fallback: edge-tts → MP3 → WAV 8kHz."""
    ts = int(time.time() * 1000)
    mp3_path = TTS_OUTPUT_DIR / f"tts_edge_{ts}.mp3"
    wav_path = TTS_OUTPUT_DIR / f"tts_edge_{ts}.wav"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media", str(mp3_path)],
            capture_output=True, timeout=30,
        )
        if result.returncode != 0 or not mp3_path.exists():
            return None
        result = subprocess.run(
            ["ffmpeg", "-i", str(mp3_path), "-ar", "8000", "-ac", "1", "-sample_fmt", "s16", str(wav_path), "-y"],
            capture_output=True, timeout=15,
        )
        mp3_path.unlink(missing_ok=True)
        if result.returncode != 0 or not wav_path.exists():
            return None
        return wav_path
    except Exception:
        return None

def synthesize_wav(text: str) -> Optional[Path]:
    """Синтезировать текст в WAV 8000Hz mono.
    Сначала Яндекс SpeechKit (чистый русский голос), fallback — edge-tts.
    """
    ts = int(time.time() * 1000)
    wav_path = TTS_OUTPUT_DIR / f"tts_{ts}.wav"
    pcm = _tts_yandex(text)
    if pcm:
        # PCM 8000Hz s16le → WAV
        try:
            with wave.open(str(wav_path), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(8000)
                w.writeframes(pcm)
        except Exception as e:
            log.error(f"PCM→WAV error: {e}")
            return None
    else:
        # Fallback edge-tts
        edge_wav = _tts_edge(text)
        if not edge_wav:
            log.error("Both Yandex and edge-tts failed")
            return None
        shutil.copy2(str(edge_wav), str(wav_path))
        edge_wav.unlink(missing_ok=True)
    # Добавляем тишину в начало (lead-in)
    wav_with_lead = TTS_OUTPUT_DIR / f"tts_{ts}_lead.wav"
    _add_lead_silence(wav_path, wav_with_lead, seconds=0.8)
    if wav_with_lead.exists():
        wav_path.unlink(missing_ok=True)
        return wav_with_lead
    return wav_path

def _add_lead_silence(input_wav: Path, output_wav: Path, seconds: float = 0.8):
    try:
        with wave.open(str(input_wav), "rb") as w:
            params = w.getparams()
            frames = w.readframes(w.getnframes())
        silence_frames = int(params.framerate * seconds) * params.sampwidth * params.nchannels
        silence = b"\x00" * silence_frames
        with wave.open(str(output_wav), "wb") as w:
            w.setparams(params)
            w.writeframes(silence + frames)
    except Exception as e:
        log.error(f"Lead silence error: {e}")
        shutil.copy2(str(input_wav), str(output_wav))


# === TELEGRAM ===
def notify_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        log.error(f"Telegram: {e}")


# === PHONE EXTRACTION ===
def extract_phone(text: str) -> Optional[str]:
    """Извлечь номер телефона из текста клиента.
    Ловит: +7XXX, 8XXX, 7XXX, или просто 10 цифр (РФ)."""
    # Вариант 1: с кодом (7/8) + 10 цифр
    m = re.search(r"(?:\+?7|8)[\s\-]?\(?(\d{3})\)?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})", text)
    if m:
        return "+7" + "".join(m.groups())
    # Вариант 2: просто 10 цифр подряд (без кода)
    m2 = re.search(r"\b(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})\b", text)
    if m2:
        return "+7" + "".join(m2.groups())
    return None


# === DIALOG HELPERS ===
REJECTION_PHRASES = [
    "не интересно", "не интересует", "не надо", "отказ",
    "до свидания", "не продаем", "не продаём", "не выращиваем",
    "не звоните", "отстаньте", "нет спасибо", "нет, спасибо",
    "не нужно", "занят", "перезвоните",
]
def is_rejection(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in REJECTION_PHRASES)

INTEREST_PHRASES = [
    "да", "ага", "угу", "интересно", "расскажите", "расскажи",
    "давай", "давайте", "хорошо", "конечно", "слушаю",
    "да интересно", "очень интересно", "подробнее", "продолжайте",
    "я слушаю", "давайте послушаем",
]
def is_interest(text: str) -> bool:
    t = text.lower().strip()
    if t in ("да", "ага", "угу", "ну", "ок", "ok"):
        return True
    return any(p in t for p in INTEREST_PHRASES)

UNCLEAR_RETRY = "Извините, я не расслышала. Вам интересно наше предложение по бройлерам?"
UNCLEAR_CLOSE = "Хорошо, я поняла. Наш менеджер перезвонит в удобное время, чтобы уточнить все детали. Спасибо за звонок, до свидания!"

VOLUME_RE = re.compile(r"(\d+)\s*(голов|штук|шт|гол|тысяч|тыс)")
def extract_volume(text: str) -> Optional[int]:
    m = VOLUME_RE.search(text.lower())
    if m:
        return int(m.group(1))
    nums = re.findall(r"\b(\d{2,4})\b", text)
    if nums:
        return int(nums[0])
    return None

def extract_breed(text: str) -> Optional[str]:
    t = text.lower()
    if re.search(r"кобб|cobb|500", t):
        return "Кобб-500"
    if re.search(r"росс|ross|308", t):
        return "Росс-308"
    if any(w in t for w in ["оба", "любая", "всё равно", "без разницы", "на ваш вкус"]):
        return "Любая"
    return None

QUALIFY_PROMPTS = {
    "start": "Отлично! Сколько голов бройлеров вам нужно?",
    "volume": "Сколько именно голов бройлеров вам нужно?",
    "breed": "Какую породу предпочитаете — Кобб-500 или Росс-308?",
    "breed_retry": "Не расслышала породу. Кобб-500 растёт быстрее, Росс-308 выносливее. Какая больше подходит?",
    "city": "В какой город вам доставить?",
    "city_retry": "Подскажите город доставки — Крым, Краснодар, Ростов, Волгоград, Ставрополь?",
    "phone": "Оставьте, пожалуйста, ваш номер телефона — менеджер перезвонит подтвердить заказ.",
    "phone_retry": "Не расслышала номер. Скажите, пожалуйста, ваш телефон — мы перезвоним для подтверждения.",
}

def is_complete(text: str, turn: int = 0, got_phone: bool = False) -> bool:
    if turn < 4 or not got_phone:
        return False
    if turn >= 8:
        return True
    return False


# === DIALOG SESSION ===
class FAQDialog:
    def __init__(self, phone: str, campaign: str = "levitan"):
        self.phone = _norm_phone(phone)
        self.campaign = campaign
        self.session_id = f"dialog_{uuid.uuid4().hex[:8]}"
        self.transcript: list[dict] = []
        self.turn = 0
        self.active = True
        self.started_at = datetime.now()
        self.last_call_time: float = 0
        self.got_phone = False
        self.qualify_state: Optional[str] = None
        self.qualify_retries = 0
        self.qualify_volume: Optional[int] = None
        self.qualify_breed: Optional[str] = None
        self.qualify_city: Optional[str] = None
        self.interested: Optional[bool] = None

    def run(self):
        log.info(f"{'='*60}")
        log.info(f"DIALOG START: {self.phone} | session={self.session_id}")
        log.info(f"{'='*60}")
        notify_telegram(f"🐣 <b>Диалог начат</b>\nТелефон: {self.phone}\nСессия: {self.session_id}")
        try:
            self._turn_greeting()
            while self.active and self.turn < MAX_TURNS:
                self._turn_response()
        except Exception as e:
            log.error(f"Dialog error: {e}", exc_info=True)
        finally:
            self._finish()

    def _turn_greeting(self):
        log.info(f"[Turn 0] Greeting → {self.phone}")
        if not GREETING_WAV.exists():
            log.error(f"Greeting WAV not found: {GREETING_WAV}")
            self.active = False
            return
        set_baresip_audio(GREETING_WAV)
        time.sleep(0.5)
        self.last_call_time = time.time()
        result = mango_callback(self.phone, f"levitan_greet_{self.session_id}")
        if "error" in result:
            self.active = False
            return
        self.transcript.append({"role": "assistant", "content": "..."})
        recording = wait_for_recording(self.last_call_time, timeout=RECORDING_WAIT_TIMEOUT)
        if not recording:
            self.active = False
            return
        client_text = transcribe(str(recording))
        if not client_text or len(client_text.strip()) < 3:
            self.active = False
            return
        self.transcript.append({"role": "user", "content": client_text})
        log.info(f"[Turn 0] Client: «{client_text[:100]}»")

        if self._is_rejection(client_text):
            self._respond_and_close("Извините за беспокойство. Всего доброго, хорошего дня!")
            return

        if is_interest(client_text):
            self.interested = True
            self.qualify_state = "start"
            log.info(f"[Turn 0] Client interested → qualify start")
            self.turn = 1
            return

        # Client might have jumped straight to volume ("мне нужно 200 голов")
        volume = extract_volume(client_text)
        if volume:
            self.interested = True
            self.qualify_volume = volume
            self.qualify_state = "breed"
            self.turn = 1
            return

        # FAQ cache hit (client asked a question instead of yes/no)
        faq_reply = faq_lookup(client_text)
        if faq_reply:
            self.interested = True
            self.qualify_state = "start"
            self.turn = 1
            return

        # Unclear → retry once, then close
        if self._retry_unclear(client_text, UNCLEAR_RETRY):
            # Listen again
            recording = wait_for_recording(self.last_call_time, timeout=RECORDING_WAIT_TIMEOUT)
            if recording:
                client_text = transcribe(str(recording))
                if client_text and len(client_text.strip()) >= 3:
                    self.transcript.append({"role": "user", "content": client_text})
                    if self._is_rejection(client_text):
                        self._respond_and_close("Извините за беспокойство. Всего доброго!")
                        return
                    if is_interest(client_text):
                        self.interested = True
                        self.qualify_state = "start"
                        self.turn = 1
                        return
                    volume = extract_volume(client_text)
                    if volume:
                        self.interested = True
                        self.qualify_volume = volume
                        self.qualify_state = "breed"
                        self.turn = 1
                        return
        self._respond_and_close(UNCLEAR_CLOSE)

    def _retry_unclear(self, client_text: str, retry_text: str) -> bool:
        wav_path = synthesize_wav(retry_text)
        if not wav_path:
            return False
        set_baresip_audio(wav_path)
        time.sleep(CALLBACK_DELAY)
        self.last_call_time = time.time()
        result = mango_callback(self.phone, f"levitan_retry_{self.session_id}")
        if "error" in result:
            return False
        return True

    def _turn_response(self):
        log.info(f"[Turn {self.turn}] Generating response...")
        client_last = self.transcript[-1]["content"] if self.transcript and self.transcript[-1]["role"] == "user" else ""
        phone_found = self._extract_phone(client_last)
        if phone_found:
            self.got_phone = True
        if self._is_rejection(client_last):
            self._respond_and_close("Извините за беспокойство. Всего доброго, хорошего дня!")
            return

        # 1. QUALIFY FLOW (если клиент сказал "Да" на приветствие)
        if self.qualify_state and self.qualify_state != "done":
            response = self._handle_qualify(client_last)
            if response is None:
                return
            self.transcript.append({"role": "assistant", "content": response})
            log.info(f"[Turn {self.turn}] Qualify: «{response[:100]}»")
            wav_path = synthesize_wav(response)
            if not wav_path:
                self.active = False
                return
            set_baresip_audio(wav_path)
            time.sleep(CALLBACK_DELAY)
            self.last_call_time = time.time()
            cmd_id = f"levitan_q{self.turn}_{self.session_id}"
            result = mango_callback(self.phone, cmd_id)
            if "error" in result:
                self.active = False
                return
            recording = wait_for_recording(self.last_call_time, timeout=RECORDING_WAIT_TIMEOUT)
            if not recording:
                self.active = False
                return
            client_text = transcribe(str(recording))
            if not client_text or len(client_text.strip()) < 3:
                if self.qualify_retries >= 2:
                    self._respond_and_close(UNCLEAR_CLOSE)
                    return
                    self.active = False
                return
            self.transcript.append({"role": "user", "content": client_text})
            log.info(f"[Turn {self.turn}] Client: «{client_text[:100]}»")
            if self._is_rejection(client_text):
                self._respond_and_close("Извините за беспокойство. Всего доброго!")
                return
            self.turn += 1
            return

        # 2. FAQ-КЭШ (мгновенный ответ)
        faq_reply = faq_lookup(client_last)
        if faq_reply:
            response = faq_reply
            log.info(f"[Turn {self.turn}] FAQ cache hit → instant TTS")
        else:
            # 3. LLM
            response = llm_response(self.transcript)
            if not response:
                self.active = False
                return
        self.transcript.append({"role": "assistant", "content": response})
        log.info(f"[Turn {self.turn}] Agent: «{response[:100]}»")
        wav_path = synthesize_wav(response)
        if not wav_path:
            self.active = False
            return
        set_baresip_audio(wav_path)
        time.sleep(CALLBACK_DELAY)
        self.last_call_time = time.time()
        cmd_id = f"levitan_t{self.turn}_{self.session_id}"
        result = mango_callback(self.phone, cmd_id)
        if "error" in result:
            self.active = False
            return
        recording = wait_for_recording(self.last_call_time, timeout=RECORDING_WAIT_TIMEOUT)
        if not recording:
            self.active = False
            return
        client_text = transcribe(str(recording))
        if not client_text or len(client_text.strip()) < 3:
            if self.turn > 2:
                self.active = False
            return
        self.transcript.append({"role": "user", "content": client_text})
        log.info(f"[Turn {self.turn}] Client: «{client_text[:100]}»")
        phone_found = self._extract_phone(client_text)
        if phone_found:
            self.got_phone = True
        if self._is_rejection(client_text):
            self._respond_and_close("Извините за беспокойство. Всего доброго!")
            return
        if self._is_complete(client_text):
            self._respond_and_close("Отлично, я всё зафиксировала. Наш менеджер свяжется с вами для подтверждения. Спасибо за время, до свидания!")
            return
        self.turn += 1

    def _handle_qualify(self, client_text: str) -> Optional[str]:
        if self.qualify_state == "start":
            self.qualify_state = "volume"
            return QUALIFY_PROMPTS["start"]

        if self.qualify_state == "volume":
            volume = extract_volume(client_text)
            if volume:
                self.qualify_volume = volume
                self.qualify_state = "breed"
                self.qualify_retries = 0
                return QUALIFY_PROMPTS["breed"]
            self.qualify_retries += 1
            if self.qualify_retries >= 2:
                self._respond_and_close(UNCLEAR_CLOSE)
                return None
            return QUALIFY_PROMPTS["volume"]

        if self.qualify_state == "breed":
            breed = extract_breed(client_text)
            if breed:
                self.qualify_breed = breed
                self.qualify_state = "city"
                self.qualify_retries = 0
                return QUALIFY_PROMPTS["city"]
            self.qualify_retries += 1
            if self.qualify_retries >= 2:
                self._respond_and_close(UNCLEAR_CLOSE)
                return None
            return QUALIFY_PROMPTS["breed_retry"]

        if self.qualify_state == "city":
            city = self._extract_city(client_text)
            if city:
                self.qualify_city = city
                self.qualify_state = "phone"
                self.qualify_retries = 0
                return QUALIFY_PROMPTS["phone"]
            self.qualify_retries += 1
            if self.qualify_retries >= 2:
                self._respond_and_close(UNCLEAR_CLOSE)
                return None
            return QUALIFY_PROMPTS["city_retry"]

        if self.qualify_state == "phone":
            phone = extract_phone(client_text)
            if phone:
                self.got_phone = True
                self.qualify_state = "done"
                vol_str = f" {self.qualify_volume} голов" if self.qualify_volume else ""
                breed_str = f" {self.qualify_breed}" if self.qualify_breed else ""
                city_str = f" в {self.qualify_city}" if self.qualify_city else ""
                log.info(f"Qualify complete: {vol_str}{breed_str}{city_str} phone={phone}")
                return (
                    f"Спасибо! Я передала заказ{vol_str}{breed_str}{city_str}. "
                    f"Наш менеджер перезвонит вам для подтверждения. До свидания!"
                )
            self.qualify_retries += 1
            if self.qualify_retries >= 2:
                self._respond_and_close(UNCLEAR_CLOSE)
                return None
            return QUALIFY_PROMPTS["phone_retry"]

        return None

    def _extract_city(self, text: str) -> Optional[str]:
        t = text.lower().strip()
        cities = {
            "краснодар": "Краснодар", "ростов": "Ростов-на-Дону",
            "ростов-на-дону": "Ростов-на-Дону", "волгоград": "Волгоград",
            "ставрополь": "Ставрополь", "симферополь": "Симферополь",
            "севастополь": "Севастополь", "ялта": "Ялта",
            "феодосия": "Феодосия", "керачь": "Керчь",
            "евпатория": "Евпатория", "джанкой": "Джанкой",
            "азовское": "Азовское",
        }
        for key, val in cities.items():
            if key in t:
                return val
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        return extract_phone(text)

    def _respond_and_close(self, text: str):
        self.transcript.append({"role": "assistant", "content": text})
        wav_path = synthesize_wav(text)
        if wav_path:
            set_baresip_audio(wav_path)
            time.sleep(CALLBACK_DELAY)
            mango_callback(self.phone, f"levitan_close_{self.session_id}")
            time.sleep(10)
        self.active = False

    def _is_rejection(self, text: str) -> bool:
        return is_rejection(text)

    def _is_complete(self, text: str) -> bool:
        return is_complete(text, self.turn, self.got_phone)

    def _finish(self):
        duration = (datetime.now() - self.started_at).total_seconds()
        dialog_data = {
            "session_id": self.session_id, "phone": self.phone, "campaign": self.campaign,
            "turns": self.turn, "duration_sec": round(duration),
            "got_phone": self.got_phone,
            "started_at": self.started_at.isoformat(), "ended_at": datetime.now().isoformat(),
            "transcript": self.transcript,
        }
        path = DIALOGS_DIR / f"{self.session_id}.json"
        with open(path, "w") as f:
            json.dump(dialog_data, f, ensure_ascii=False, indent=2)
        log.info(f"{'='*60}")
        log.info(f"DIALOG END: {self.phone} | turns={self.turn} | {duration:.0f}s | phone={self.got_phone}")
        log.info(f"Saved: {path}")
        log.info(f"{'='*60}")
        transcript_text = "\n".join([
            f"{'🤖' if e['role'] == 'assistant' else '👤'} {e['content'][:80]}" for e in self.transcript
        ])
        notify_telegram(
            f"🐣 <b>Диалог завершён</b>\nТелефон: {self.phone}\nХодов: {self.turn}\n"
            f"Длительность: {duration:.0f} сек\nТелефон собран: {'да' if self.got_phone else 'нет'}\n\n"
            f"<b>Транскрипт:</b>\n{transcript_text[:1500]}"
        )
        if GREETING_WAV.exists():
            set_baresip_audio(GREETING_WAV)


# === EVENT WATCHER ===
def watch_for_calls():
    seen = set()
    active_phones = set()
    log.info("="*60)
    log.info("LEVITAN FAQ-AGENT STARTED (Анжелла, бройлеры)")
    log.info(f"  Greeting: {GREETING_WAV}")
    log.info(f"  FAQ-кэш: {FAQ_CACHE_PATH}")
    log.info(f"  Max turns: {MAX_TURNS}")
    log.info("="*60)
    load_faq_cache()
    if GREETING_WAV.exists():
        set_baresip_audio(GREETING_WAV)
    while True:
        try:
            if EVENTS_PATH.exists():
                with open(EVENTS_PATH) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line in seen:
                            continue
                        seen.add(line)
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if event.get("type") == "callback_connected":
                            phone = event.get("phone", "")
                            call_id = event.get("call_id", "")
                            if not phone or len(phone) < 11:
                                continue
                            if phone in active_phones:
                                continue
                            cmd_id = event.get("command_id", "")
                            if "levitan_t" in cmd_id or "levitan_close" in cmd_id:
                                continue
                            log.info(f"New call detected: {phone}")
                            active_phones.add(phone)
                            def run_dialog(ph):
                                try:
                                    dialog = FAQDialog(ph)
                                    dialog.run()
                                finally:
                                    active_phones.discard(ph)
                            t = threading.Thread(target=run_dialog, args=(phone,), daemon=True)
                            t.start()
            time.sleep(1)
        except Exception as e:
            log.error(f"Watch error: {e}")
            time.sleep(5)


def manual_call(phone: str):
    load_faq_cache()
    dialog = FAQDialog(phone)
    dialog.run()


if __name__ == "__main__":
    load_faq_cache()
    if len(sys.argv) > 1:
        manual_call(sys.argv[1])
    else:
        watch_for_calls()
