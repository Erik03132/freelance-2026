#!/usr/bin/env python3
"""
Levitan Webhook Server — приём событий от Mango Office (включая конспекты).
Запуск: python3 scripts/webhook_server.py
"""

import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# === CONFIG ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

def load_env():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

load_env()

MANGO_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

RESULTS_DIR = PROJECT_ROOT / "data" / "call_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = PROJECT_ROOT / "data" / "webhook_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

CONTACTS = {}
contacts_path = PROJECT_ROOT / "data" / "campaigns" / "csv" / "all_contacts_2026.csv"
if contacts_path.exists():
    import csv
    with open(contacts_path) as f:
        for row in csv.DictReader(f):
            CONTACTS[row["Телефоны"].strip()] = row["Название"].strip()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "webhook.log"),
    ],
)
log = logging.getLogger("levitan-wh")

app = FastAPI(title="Levitan Webhook")

# === UTILITIES ===

def _norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    return d

def _get_contact_name(phone: str) -> str:
    return CONTACTS.get(phone, "")

def _write_event(data: dict):
    try:
        path = LOG_DIR / "events.jsonl"
        with open(path, "a") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        log.error("write event: %s", e)

def _save_summary(data: dict):
    """Save summary/transcript to call_results."""
    phone = _norm_phone(data.get("phone", ""))
    contact_name = _get_contact_name(phone) or phone
    timestamp = datetime.now().isoformat()
    
    transcript = data.get("transcript") or data.get("text") or data.get("summary") or ""
    recording_id = data.get("recording_id") or data.get("dialog_id") or ""
    
    result = {
        "timestamp": timestamp,
        "phone": phone,
        "company_name": contact_name,
        "transcript": transcript,
        "recording_id": recording_id,
        "source": "mango_webhook_summary",
    }
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = RESULTS_DIR / f"webhook_summary_{date_str}.jsonl"
    with open(path, "a") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    log.info("✅ Summary saved: %s (%s chars)", phone, len(transcript))
    _write_event({"type": "summary_received", "phone": phone, "recording_id": recording_id})

def _notify_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        log.error("Telegram notify: %s", e)

# === MANGO EVENT HANDLERS ===

def _extract_mango_data(raw_body: str) -> dict:
    """Parse Mango's form-encoded POST body."""
    try:
        from urllib.parse import parse_qs
        params = parse_qs(raw_body)
        json_str = params.get("json", [""])[0]
        if json_str:
            return json.loads(json_str)
    except Exception:
        pass
    
    try:
        return json.loads(raw_body)
    except Exception:
        return {"raw": raw_body[:500]}

def handle_call_state(data: dict):
    """Handle call state events."""
    call_state = data.get("call_state", "")
    call_id = data.get("call_id", "")
    entry_id = data.get("entry_id", "")
    
    from_info = data.get("from") or {}
    to_info = data.get("to") or {}
    from_num = str(from_info.get("number", ""))
    to_num = str(to_info.get("number", ""))
    
    log.info("Call event: %s | %s→%s", call_state, from_num, to_num)
    _write_event({"type": "call_state", "state": call_state, "call_id": call_id, "entry_id": entry_id})

def handle_recording(data: dict):
    """Handle recording ready event."""
    rec_id = data.get("recording_id") or data.get("record_id") or ""
    if rec_id:
        log.info("Recording ready: %s", rec_id)
        _write_event({"type": "recording_ready", "recording_id": rec_id})

def handle_summary(data: dict):
    """Handle speech analytics summary event."""
    log.info("Summary received: %s", json.dumps(data, ensure_ascii=False)[:300])
    
    # Extract transcript - Mango sends it in different formats
    transcript = ""
    phone = ""
    recording_id = ""
    
    # Format 1: direct fields
    if "text" in data:
        transcript = data["text"]
    elif "transcript" in data:
        transcript = data["transcript"]
    elif "summary" in data:
        summary = data["summary"]
        if isinstance(summary, str):
            transcript = summary
        elif isinstance(summary, dict):
            transcript = summary.get("text") or summary.get("transcript") or json.dumps(summary, ensure_ascii=False)
    
    # Find phone number from various fields
    phone = (
        data.get("phone") or data.get("client_number") or data.get("from", {}).get("number", "")
        or data.get("to", {}).get("number", "") or ""
    )
    
    recording_id = data.get("recording_id") or data.get("dialog_id") or data.get("call_id") or ""
    
    # Fallback: try to find phone from the entire data tree
    if not phone:
        for key in ["from", "to", "caller", "called_number", "number", "client_phone"]:
            val = data.get(key)
            if isinstance(val, dict):
                phone = str(val.get("number", ""))
            elif isinstance(val, str) and re.search(r"\d{10,}", val):
                phone = val
            if phone:
                break
    
    # Save and notify
    save_data = {
        "phone": phone,
        "transcript": transcript,
        "recording_id": recording_id,
        "raw": json.dumps(data, ensure_ascii=False),
    }
    _save_summary(save_data)
    
    if phone and transcript:
        contact = _get_contact_name(_norm_phone(phone)) or phone
        _notify_telegram(
            f"📝 <b>Новый конспект</b>\n"
            f"Клиент: {contact}\n"
            f"Телефон: +{phone}\n"
            f"Транскрипт: {transcript[:300]}..."
        )

# === ROUTES ===

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "running", "service": "levitan-webhook"}

@app.post("/mango-webhook")
async def mango_webhook(request: Request):
    """Main webhook endpoint for Mango events."""
    body = await request.body()
    raw = body.decode("utf-8", errors="replace")
    
    data = _extract_mango_data(raw)
    log.info("Mango webhook: %s", json.dumps(data, ensure_ascii=False)[:200])
    
    call_state = data.get("call_state", "")
    recording_id = data.get("recording_id") or data.get("record_id") or ""
    
    if recording_id and call_state in ("Disconnected", "Failed", ""):
        # This is a recording notification
        handle_recording(data)
    
    if call_state:
        handle_call_state(data)
    
    # Check for summary/transcript data
    has_transcript = any(k in data for k in ["text", "transcript", "summary", "dialog_text"])
    has_summary_event = "summary" in (data.get("type", "").lower()) or request.url.path.endswith("/summary")
    
    if has_transcript or has_summary_event:
        handle_summary(data)
    
    return JSONResponse({"status": "ok"})

@app.post("/mango-webhook/{event_type}")
async def mango_webhook_event(event_type: str, request: Request):
    """Handle specific event types (e.g., /mango-webhook/summary)."""
    body = await request.body()
    raw = body.decode("utf-8", errors="replace")
    data = _extract_mango_data(raw)
    
    log.info("Mango event [%s]: %s", event_type, json.dumps(data, ensure_ascii=False)[:200])
    
    if event_type == "summary":
        handle_summary(data)
    elif event_type == "recording":
        handle_recording(data)
    elif event_type == "call":
        handle_call_state(data)
    
    return JSONResponse({"status": "ok"})

@app.post("/")
async def catch_all(request: Request):
    """Catch-all for any POST."""
    body = await request.body()
    raw = body.decode("utf-8", errors="replace")
    log.info("Catch-all POST: %s", raw[:200])
    return JSONResponse({"status": "ok"})

# === MAIN ===

def main():
    port = int(os.getenv("LEVITAN_WEBHOOK_PORT", "8088"))
    log.info("Starting Levitan Webhook on port %d", port)
    log.info("Telegram notifications: %s", "ON" if TELEGRAM_BOT_TOKEN else "OFF")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )

if __name__ == "__main__":
    main()
