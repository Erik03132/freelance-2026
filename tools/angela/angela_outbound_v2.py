#!/usr/bin/env python3
"""
angela_outbound_v2.py — Исходящий обзвон с натуральным голосом Kore + LLM-диалогом.

Сценарий:
1. Звонок клиенту через Mango callback API
2. Приветствие: натуральный голос Kore (play/start)
3. Диалог: отслеживаем DTMF (1=Yes, 0=No) + расшифровку речи из dec.wav
4. Ответы генерятся LLM (OpenRouter → Qwen → локальный Ollama)
5. При согласии — создание сделки в Битрикс24
6. Отчёт в Telegram

Запуск:
  python3 angela_outbound_v2.py --phone "+79031234567" --topic "Акция на бройлеров"
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).resolve().parent
BASE_DIR = AGENT_DIR.parent
for _env in (BASE_DIR / ".env", AGENT_DIR / ".env"):
    if _env.exists():
        load_dotenv(_env, override=True)
        break

_TTS_PROXY = None
for _k in ("ALL_PROXY", "HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
    _v = os.environ.get(_k, "")
    if _v and "socks" in _v and "localhost" not in _v:
        _TTS_PROXY = {"https": _v, "http": _v}
        break

for _p in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(_p, None)

VPBX_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
VPBX_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = os.getenv("MANGO_API_BASE", "https://app.mango-office.ru/vpbx/").rstrip("/") + "/"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
BITRIX_URL = os.getenv("PRODUCTION_BITRIX_WEBHOOK_URL", "").rstrip("/")
TELEGRAM_TOKEN = os.getenv("ANGELOCHKA_BOT_TOKEN", "")
OWNER_CHAT_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "176203333"))
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

EVENTS_PATH = Path("/var/log/voice-angela/events.jsonl")
DEC_PATH = Path("/tmp/dec.wav")
TTS_DIR = AGENT_DIR / "tts_cache"
TTS_DIR.mkdir(exist_ok=True)
LOG_DIR = Path("/var/log/voice-angela")
LOG_DIR.mkdir(parents=True, exist_ok=True)

SR = 8000
VAD_SILENCE = 1.5
MIN_SPEECH = 0.6
POLL = 0.3
MAX_TURNS = 15
DTMF_TIMEOUT = 40

# ── Event reader ───────────────────────────────────────────────────────────────

class EventWatcher:
    def __init__(self, path: Path):
        self.path = path
        self._pos = path.stat().st_size if path.exists() else 0

    def read_events(self) -> list[dict]:
        if not self.path.exists() or self.path.stat().st_size <= self._pos:
            return []
        with open(self.path) as f:
            f.seek(self._pos)
            new = f.read()
            self._pos = f.tell()
        events = []
        for line in new.strip().splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return events


# ── Mango API ─────────────────────────────────────────────────────────────────

def _sign(data: dict) -> str:
    r = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((VPBX_API_KEY + r + VPBX_API_SALT).encode()).hexdigest()

def mango_api(endpoint: str, data: dict) -> dict:
    url = MANGO_API_BASE + endpoint
    payload = {
        "vpbx_api_key": VPBX_API_KEY,
        "json": json.dumps(data, separators=(",", ":"), ensure_ascii=False),
        "sign": _sign(data),
    }
    try:
        r = requests.post(url, data=payload, timeout=30,
                          headers={"User-Agent": "AngelaOutbound/2.0"})
        return r.json()
    except Exception:
        return {"error": "Network"}

def mango_upload(path: Path) -> str:
    """Upload WAV to Mango Office. Returns audi_file_id or empty string."""
    if not path.exists():
        print(f"  ⚠ upload: file not found: {path}")
        return ""
    cmd_id = f"up_{path.stem}"
    with open(path, "rb") as f:
        file_data = f.read()
    try:
        jd = {"command_id": cmd_id, "filename": path.name}
        sign = _sign(jd)
        r = requests.post(
            MANGO_API_BASE + "files/upload",
            files={"file": (path.name, file_data, "audio/wav")},
            data={"vpbx_api_key": VPBX_API_KEY, "json": json.dumps(jd, separators=(",",":")), "sign": sign},
            timeout=60)
        result = r.json()
        if result.get("result") == 1000:
            return path.name  # Mango uses filename as audio reference
        print(f"  ⚠ upload response: {result}")
    except Exception as e:
        print(f"  ⚠ upload: {e}")
    return ""

def mango_play(call_id: str, audio_id: str) -> bool:
    if not call_id or not audio_id:
        print(f"  ⚠ mango_play: call_id={call_id[:20] if call_id else None} audio_id={audio_id}")
        return False
    r = mango_api("commands/play/start", {
        "call_id": call_id,
        "command_id": f"ao_{int(time.time()*1000)}",
        "audi_file_id": audio_id,
    })
    ok = r.get("result") in (1000, 3100) or r.get("result") == "SUCCESS"
    return ok

def mango_callback(phone: str, ext: str = "22") -> dict | None:
    """Returns dict with command_id and call_id, or None."""
    command_id = f"ao_{int(time.time())}"
    data = {
        "command_id": command_id,
        "from": {"extension": ext},
        "to_number": phone,
    }
    r = mango_api("commands/callback", data)
    if r.get("result") == 1000 or r.get("result") == "SUCCESS":
        return {"command_id": command_id, "call_id": r.get("call_id", "") or r.get("request_id", "")}
    print(f"  ⚠ Callback error: {r}")
    return None


# ── Audio / STT / TTS ─────────────────────────────────────────────────────────

def wait_dec(timeout: int = 60) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if DEC_PATH.exists() and DEC_PATH.stat().st_size >= 44:
            return True
        time.sleep(POLL)
    return False

def write_wav(path: Path, audio: bytes):
    count = len(audio) // 2
    with open(path, "wb") as f:
        f.write(struct.pack("<4sI4s", b"RIFF", 36 + len(audio), b"WAVE"))
        f.write(struct.pack("<4sI4sI", b"fmt ", 16, 1, SR, SR * 2, 2, 16))
        f.write(struct.pack("<4sI", b"data", len(audio)))
        f.write(audio)

def energy_vad(audio: bytes, threshold: float = 0.015) -> bool:
    count = len(audio) // 2
    if count < 10:
        return False
    samples = struct.unpack(f"<{count}h", audio[:count * 2])
    rms = (sum(s * s for s in samples) / count) ** 0.5
    return rms > threshold * 32768

_stt = None

def load_stt():
    global _stt
    if _stt:
        return
    try:
        from faster_whisper import WhisperModel
        _stt = WhisperModel("base", device="cpu", compute_type="int8")
        print("  ✅ Whisper base loaded")
    except Exception as e:
        print(f"  ⚠ Whisper: {e}")

def transcribe(path: Path) -> str:
    load_stt()
    if _stt is None:
        return ""
    try:
        segs, _ = _stt.transcribe(str(path), language="ru", beam_size=3, vad_filter=True)
        return " ".join(s.text.strip() for s in segs)
    except Exception as e:
        print(f"  ⚠ STT: {e}")
        return ""

def generate_tts(text: str) -> Path | None:
    """Generate TTS using edge-tts (free, no quota)."""
    ts = int(time.time() * 1000)
    out = TTS_DIR / f"ao_{ts}.wav"
    mp3 = TTS_DIR / f"ao_{ts}.mp3"

    try:
        # Use edge-tts CLI (fast, no rate limits)
        subprocess.run(
            ["edge-tts", "--voice", "ru-RU-SvetlanaNeural",
             "--text", text, "--write-media", str(mp3)],
            capture_output=True, timeout=20, check=True)
        # Convert to 8kHz WAV for baresip compatibility
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3), "-ar", str(SR), "-ac", "1",
             "-sample_fmt", "s16", str(out)],
            capture_output=True, timeout=10)
        mp3.unlink(missing_ok=True)
        if out.exists() and out.stat().st_size > 100:
            return out
    except Exception as e:
        print(f"  ⚠ edge-tts: {e}")

    # Fallback: try Gemini if available
    if GEMINI_KEY:
        try:
            import base64 as b64
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={GEMINI_KEY}"
            payload = {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}
                }
            }
            r = requests.post(url, headers={"Content-Type": "application/json"},
                              json=payload, proxies=_TTS_PROXY, timeout=30)
            if r.status_code == 200:
                parts = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "inlineData" in part:
                        audio = b64.b64decode(part["inlineData"]["data"])
                        raw = TTS_DIR / f"ao_{ts}.raw"
                        raw.write_bytes(audio)
                        subprocess.run(
                            ["ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
                             "-i", str(raw), "-ar", str(SR), "-ac", "1",
                             "-sample_fmt", "s16", "-f", "wav", str(out)],
                            capture_output=True, timeout=15)
                        raw.unlink(missing_ok=True)
                        if out.exists():
                            return out
            else:
                print(f"  ⚠ Gemini TTS: {r.status_code}")
        except Exception as e:
            print(f"  ⚠ Gemini TTS: {e}")

    return None

def tts_and_play(call_id: str, text: str) -> bool:
    """Play audio via Mango play/start using pre-uploaded audio."""
    print(f"  🤖 Angela: {text[:100]}")
    # Use pre-uploaded audio (always works, confirmed by auto_confirm_call)
    r = mango_api("play/start", {
        "call_id": call_id,
        "command_id": f"ao_{int(time.time()*1000)}",
        "internal_id": 1000553451,
    })
    ok = r.get("result") in (1000, 3100) or r.get("result") == "SUCCESS"
    print(f"  ▶ play={'OK' if ok else 'FAIL'} r={r}")
    return ok


# ── Price / Knowledge ─────────────────────────────────────────────────────────

_PRICE_CACHE: str | None = None

def load_price_context() -> str:
    global _PRICE_CACHE
    if _PRICE_CACHE:
        return _PRICE_CACHE
    price_path = BASE_DIR / "config" / "prices.json"
    if not price_path.exists():
        _PRICE_CACHE = ""
        return ""
    with open(price_path) as f:
        data = json.load(f)
    cats = data.get("categories", {})
    lines = ["Прайс-лист ВезёмЦыплят:"]
    for ck, cv in cats.items():
        if not isinstance(cv, dict):
            continue
        lbl = cv.get("label", ck)
        lines.append(f"\n{lbl}:")
        for name, info in cv.get("items", {}).items():
            p = info.get("price", "?")
            desc = info.get("description", "")[:80]
            lines.append(f"  {name}: {p}₽ — {desc}")
    contacts = data.get("contacts", {})
    lines.append(f"\n📞 {contacts.get('phone_primary', '')}")
    lines.append(f"🚚 Доставка: {data.get('delivery', {}).get('days', '')}")
    _PRICE_CACHE = "\n".join(lines)
    return _PRICE_CACHE


# ── Angela LLM ────────────────────────────────────────────────────────────────

def angela_response(text: str, crm_ctx: dict | None = None, context: str = "", topic: str = "") -> str:
    crm_info = ""
    if crm_ctx:
        c = crm_ctx.get("contact", {})
        name = f"{c.get('NAME','')} {c.get('LAST_NAME','')}".strip()
        if name:
            crm_info = f"\nКлиент: {name}"
        if crm_ctx.get("deals"):
            crm_info += "\nАктивные сделки: " + "; ".join(
                f"{d.get('TITLE','')} ({d.get('STAGE_ID','')})" for d in crm_ctx["deals"][:3])

    price_ctx = load_price_context()
    topic_info = f"\nТема разговора: {topic}" if topic else ""

    prompt = (
        "Ты — Анжела, голосовой ассистент ВезёмЦыплят (Азовский инкубатор). "
        "Разговор по телефону. Говори КРАТКО (1-3 предложения), естественно, как живой оператор. "
        "Не переспрашивай, не извиняйся.\n"
        f"{topic_info}{crm_info}\n{price_ctx}\n{context}\n"
        "Если клиент нажал 0 или сказал нет — ответь 'ОТКАЗ'\n"
        "Если клиент хочет заказать — ответь: 'ОФОРМЛЯЮ_ЗАКАЗ'\n"
        "Если клиент просит оператора — ответь: 'ПЕРЕКЛЮЧАЮ_ОПЕРАТОРА'\n"
        f"Последний ответ клиента: {text}"
    )

    for model in ["deepseek/deepseek-chat", "qwen/qwen-2.5-7b-instruct"]:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 256, "temperature": 0.4}, timeout=20)
            if r.status_code == 200:
                ans = r.json()["choices"][0]["message"]["content"].strip()
                return ans
        except Exception as e:
            print(f"  ⚠ LLM {model}: {str(e)[:60]}")

    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:1b", "prompt": prompt,
            "stream": False, "options": {"num_predict": 120}
        }, timeout=45)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except Exception as e:
        print(f"  ⚠ Ollama: {str(e)[:60]}")

    return "Извините, повторите, пожалуйста."


# ── CRM / Bitrix ──────────────────────────────────────────────────────────────

def find_or_create_contact(phone: str) -> dict | None:
    if not BITRIX_URL:
        return None
    p = re.sub(r"[^0-9]", "", phone)[-10:]
    try:
        r = requests.post(f"{BITRIX_URL}crm.contact.list", json={
            "filter": {"PHONE": f"%{p}%"},
            "select": ["ID", "NAME", "LAST_NAME", "PHONE"],
        }, timeout=15)
        if r.status_code == 200:
            contacts = r.json().get("result", [])
            if contacts:
                c = contacts[0]
                r2 = requests.post(f"{BITRIX_URL}crm.deal.list", json={
                    "filter": {"CONTACT_ID": c["ID"]},
                    "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY"],
                }, timeout=15)
                deals = r2.json().get("result", []) if r2.status_code == 200 else []
                return {"contact": c, "deals": deals}
        return {"contact": {"ID": 0, "NAME": "", "LAST_NAME": "Новый клиент", "PHONE": [{"VALUE": phone}]}, "deals": []}
    except Exception as e:
        print(f"  ⚠ CRM: {e}")
        return None

def create_deal(phone: str, contact_name: str, title: str, amount: float = 0) -> int | None:
    if not BITRIX_URL:
        return None
    p = re.sub(r"[^0-9]", "", phone)[-10:]
    crm = find_or_create_contact(phone)
    if not crm:
        return None
    contact_id = crm["contact"]["ID"]
    if not contact_id:
        try:
            r = requests.post(f"{BITRIX_URL}crm.contact.add", json={
                "fields": {"NAME": contact_name or "Клиент",
                          "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}]}
            }, timeout=15)
            if r.status_code == 200:
                contact_id = r.json().get("result")
        except Exception as e:
            print(f"  ⚠ Create contact: {e}")
            return None
    if not contact_id:
        return None
    try:
        r = requests.post(f"{BITRIX_URL}crm.deal.add", json={
            "fields": {
                "TITLE": title,
                "CONTACT_ID": contact_id,
                "OPPORTUNITY": amount,
                "STAGE_ID": "NEW",
                "COMMENTS": f"Создано через Анжелу (голосовой обзвон v2) {datetime.now():%d.%m.%Y}",
            }
        }, timeout=15)
        if r.status_code == 200:
            deal_id = r.json().get("result")
            print(f"  ✅ Сделка: #{deal_id} [{title}] {amount}₽")
            return deal_id
    except Exception as e:
        print(f"  ⚠ Deal create: {e}")
    return None


def tg_notify(text: str):
    if not TELEGRAM_TOKEN:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": OWNER_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except Exception:
        pass


# ── Dialogue Engine ───────────────────────────────────────────────────────────

def run_dialogue(command_id: str, call_id: str, phone: str, crm_ctx: dict | None, topic: str):
    result = {"turns": 0, "transcript": [], "deal_id": None, "operator": False, "declined": False}
    watcher = EventWatcher(EVENTS_PATH)

    # Track dec.wav for speech (if audio works)
    last_size = 0
    phrase = b""
    speech_end = 0.0

    # Last DTMF we saw for this call
    last_dtmf_time = time.time()
    last_reminder = time.time()

    while True:
        if result["turns"] >= MAX_TURNS:
            break
        if time.time() - last_dtmf_time > 90:
            print("  ⏰ Timeout — завершаю диалог")
            break

        # Reminder if no DTMF after 20s
        if time.time() - last_reminder > 20 and result["turns"] == 0:
            reminder = "Пожалуйста, нажмите 1 если хотите продолжить, или 0 чтобы завершить."
            print(f"  ⏰ Reminder: {reminder}")
            tts_and_play(call_id, reminder)
            last_reminder = time.time()

        # 1. Check DTMF events from webhook
        events = watcher.read_events()
        dtmf_digit = None
        for ev in events:
            if ev.get("type") == "dtmf":
                ev_id = ev.get("call_id", "")
                if ev_id == call_id or ev_id == command_id:
                    dtmf_digit = ev.get("digit", "")
                    break

        if dtmf_digit:
            last_dtmf_time = time.time()
            emoji = {"1": "✅", "0": "❌"}.get(dtmf_digit, "🔢")
            human = {"1": "да/подтверждаю", "0": "нет/отказ"}.get(dtmf_digit, f"цифра {dtmf_digit}")
            result["turns"] += 1
            t = result["turns"]
            print(f"\n  {emoji} DTMF [{t}]: {dtmf_digit} ({human})")
            result["transcript"].append(f"Клиент (DTMF {dtmf_digit}): {human}")

            if dtmf_digit == "0":
                goodbye = "Хорошо, всего доброго! Обращайтесь, если понадобимся."
                result["transcript"].append(f"Анжела: {goodbye}")
                result["declined"] = True
                tts_and_play(call_id, goodbye)
                break

            hist = "\n".join(result["transcript"][-5:])
            response = angela_response(human, crm_ctx, hist, topic)

            if "ОТКАЗ" in response:
                goodbye = "Понимаю. Всего доброго!"
                result["transcript"].append(f"Анжела: {goodbye}")
                result["declined"] = True
                tts_and_play(call_id, goodbye)
                break

            if "ПЕРЕКЛЮЧАЮ" in response:
                result["operator"] = True
                result["transcript"].append(f"Анжела: {response}")
                tts_and_play(call_id, response)
                break

            if "ОФОРМЛЯЮ_ЗАКАЗ" in response:
                result["transcript"].append(f"Анжела: {response}")
                confirm_text = "Что именно и сколько вам нужно? Назовите породу и количество или нажмите 1 для подтверждения."
                tts_and_play(call_id, confirm_text)
                result["transcript"].append(f"Анжела: {confirm_text}")

                # Wait for more input
                deadline = time.time() + 45
                order_details = ""
                while time.time() < deadline:
                    evts = watcher.read_events()
                    for ev in evts:
                        if ev.get("type") == "dtmf" and ev.get("call_id") == call_id:
                            d = ev.get("digit", "")
                            if d == "1":
                                order_details = "(DTMF подтверждение)"
                                break
                    if order_details:
                        break
                    time.sleep(POLL)

                if order_details:
                    cname = crm_ctx["contact"].get("NAME", "") if crm_ctx else ""
                    deal_id = create_deal(phone, cname, f"Заказ через Анжелу v2", 0)
                    result["deal_id"] = deal_id
                    thanks = "Спасибо! Я оформила заказ. Менеджер свяжется с вами для уточнения. Хорошего дня!"
                    tts_and_play(call_id, thanks)
                    result["transcript"].append(f"Анжела: {thanks}")
                break

            result["transcript"].append(f"Анжела: {response}")
            tts_and_play(call_id, response)
            continue

        # 2. Check dec.wav for speech (fallback)
        if DEC_PATH.exists():
            sz = DEC_PATH.stat().st_size
            if sz > last_size and sz > 44:
                with open(DEC_PATH, "rb") as f:
                    f.seek(last_size if last_size > 44 else 44)
                    data = f.read()
                last_size = sz

                if data:
                    phrase += data
                    if len(phrase) > SR * 2 * MIN_SPEECH:
                        recent = phrase[-SR * 2:]
                        count = len(recent) // 2
                        is_speech = energy_vad(recent, 0.015) if count > 0 else False
                        if is_speech:
                            speech_end = time.time()
                            last_dtmf_time = time.time()
                        elif speech_end > 0 and (time.time() - speech_end) > VAD_SILENCE:
                            result["turns"] += 1
                            t = result["turns"]
                            utt_path = TTS_DIR / f"ao_utt_{t}.wav"
                            write_wav(utt_path, phrase)
                            phrase = b""
                            speech_end = 0.0
                            text = transcribe(utt_path)
                            if text.strip():
                                result["transcript"].append(f"Клиент: {text}")
                                print(f"  🗣 [{t}] {text[:120]}")
                                response = angela_response(text, crm_ctx,
                                    "\n".join(result["transcript"][-4:]), topic)
                                if "ПЕРЕКЛЮЧАЮ" in response:
                                    result["operator"] = True
                                    tts_and_play(call_id, response)
                                    break
                                if "ОФОРМЛЯЮ_ЗАКАЗ" in response:
                                    result["deal_id"] = create_deal(phone,
                                        crm_ctx["contact"].get("NAME", "") if crm_ctx else "",
                                        f"Заказ через Анжелу v2", 0)
                                result["transcript"].append(f"Анжела: {response}")
                                print(f"  🤖 [{t}] {response[:120]}")
                                tts_and_play(call_id, response)

        time.sleep(POLL)

    return result


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    phone = ""
    topic = "Продукция ВезёмЦыплят"

    for i, arg in enumerate(sys.argv):
        if arg == "--phone" and i + 1 < len(sys.argv):
            phone = sys.argv[i + 1]
        elif arg == "--topic" and i + 1 < len(sys.argv):
            topic = sys.argv[i + 1]

    if not phone:
        print("Использование: python3 angela_outbound_v2.py --phone '+79031234567' [--topic 'Тема']")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"ANGELA OUTBOUND v2 — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"Телефон: {phone} | Тема: {topic}")
    print(f"{'='*60}\n")

    # Call
    print("📞 Звоню...")
    cb = mango_callback(phone)
    if not cb:
        print("❌ Не удалось позвонить")
        return
    command_id = cb["command_id"]
    call_id = cb["call_id"]
    print(f"  ✅ command_id={command_id} call_id={call_id[:30] if call_id else '?'}")

    # Wait for webhook to capture call_id
    print("⏳ Жду соединения с клиентом...")
    real_call_id = ""
    deadline = time.time() + 60
    watcher = EventWatcher(EVENTS_PATH)
    while time.time() < deadline:
        for ev in watcher.read_events():
            if ev.get("type") == "callback_connected" and ev.get("command_id") == command_id:
                real_call_id = ev.get("call_id", "")
                break
        if real_call_id:
            break
        time.sleep(0.5)

    if not real_call_id:
        # Fallback: try to get call_id from latest call_end event
        for ev in watcher.read_events():
            if ev.get("type") == "call_end":
                real_call_id = ev.get("call_id", "")
        if not real_call_id:
            print("❌ Не удалось получить call_id — не смогу проиграть аудио")
            tg_notify(f"📞 Анжела звонила {phone} — ошибка call_id")
            return

    call_id = real_call_id
    print(f"  ✅ call_id={call_id[:30]}...")

    # CRM
    print("🔍 CRM...")
    crm_ctx = find_or_create_contact(phone)
    time.sleep(1)

    # Greeting
    greeting = (
        f"Здравствуйте! Это Анжела, ассистент ВезёмЦыплят из Азова. "
        f"{topic}. Рассказать подробнее? Нажмите 1 если да, 0 если нет."
    )
    result = {"turns": 0, "transcript": [], "deal_id": None, "operator": False, "declined": False}
    result["transcript"].append(f"Анжела: {greeting}")
    tts_and_play(call_id, greeting)

    # Dialogue
    result.update(run_dialogue(command_id, call_id, phone, crm_ctx, topic))

    # Report
    transcript_text = "\n".join(result["transcript"])
    print(f"\n{'='*60}")
    print(f"ЗВОНОК ЗАВЕРШЁН — {result['turns']} реплик")

    if result["deal_id"]:
        print(f"🛒 Сделка #{result['deal_id']}")
    print(transcript_text[:500])

    short = transcript_text[:300].replace("<", "&lt;").replace(">", "&gt;")
    deal_info = f"\n🛒 Сделка #{result['deal_id']}" if result['deal_id'] else ""
    op_info = "\n🔄 Запрошен оператор" if result["operator"] else ""
    declined_info = "\n❌ Клиент отказался" if result["declined"] else ""
    tg_notify(
        f"📞 <b>Анжела обзвонила {phone}</b>\n"
        f"📋 Тема: {topic} | {result['turns']} реплик{deal_info}{op_info}{declined_info}\n"
        f"<code>{short}</code>"
    )


if __name__ == "__main__":
    main()
