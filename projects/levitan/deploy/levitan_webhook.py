"""Levitan Webhook Server — деплой на VPS, порт 8087."""

import hashlib
import json
import logging
import os
import re
import threading
import uuid
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

import requests

# === CONFIG ===
API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
TELEGRAM_BOT_TOKEN = os.getenv("LEVITAN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("LEVITAN_TELEGRAM_CHAT_ID", "")

# === LOGS ===
LOG_DIR = Path(os.getenv("LEVITAN_LOG_DIR", "/var/log/levitan"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

EVENTS_PATH = LOG_DIR / "events.jsonl"
CALLS_DIR = LOG_DIR / "calls"
CALLS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "webhook.log")],
)
log = logging.getLogger("levitan-wh")

# === STATE ===
pending_calls: dict[str, dict] = {}
active_calls: dict[str, dict] = {}


def _write_event(data: dict):
    try:
        with open(EVENTS_PATH, "a") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        log.error("write event: %s", e)


def _save_call_data(call_id: str, data: dict):
    try:
        path = CALLS_DIR / f"{call_id}.json"
        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error("save call: %s", e)


def _mango_sign(payload: dict) -> str:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()


def mango_api(endpoint: str, payload: dict) -> dict:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    try:
        r = requests.post(
            f"{MANGO_API_BASE}{endpoint}",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": _mango_sign(payload)},
            timeout=20,
        )
        return r.json()
    except Exception as e:
        log.error("Mango API %s: %s", endpoint, e)
        return {}


def _norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    return d


def _is_mobile(num: str) -> bool:
    n = _norm_phone(num)
    return len(n) == 11 and n.startswith("7")


def register_callback(phone: str, campaign: str = "levitan") -> str:
    """Initiate callback via Mango API."""
    command_id = f"levitan_{campaign}_{uuid.uuid4().hex[:8]}"

    payload = {
        "command_id": command_id,
        "from": {"type": "extension", "number": os.getenv("MANGO_FROM_EXTENSION", "22")},
        "to": {"type": "external", "number": _norm_phone(phone)},
    }

    result = mango_api("commands/callback", payload)

    pending_calls[command_id] = {
        "phone": _norm_phone(phone),
        "campaign": campaign,
        "command_id": command_id,
        "created": datetime.now().isoformat(),
        "result": result,
    }

    log.info("📞 Callback: %s → %s (cid=%s)", phone, result.get("result"), command_id)
    return command_id


def play_audio(call_id: str, audio_id: int, label: str = "msg") -> dict:
    """Play audio file in the call."""
    if not call_id:
        return {}

    payload = {
        "command_id": f"play_{label}_{uuid.uuid4().hex[:8]}",
        "call_id": call_id,
        "internal_id": audio_id,
    }

    result = mango_api("play/start", payload)
    log.info("🎵 play/%s id=%s → call=%s: %s", label, audio_id, call_id[:20], result.get("result"))
    return result


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
        log.error("Telegram notify: %s", e)


def _schedule_greeting_play(call_id: str, delay: float = 2.0):
    """Play greeting after a delay."""

    def _run():
        time.sleep(delay)
        play_audio(call_id, 1000550776, label="greeting")  # Kore greeting

    threading.Thread(target=_run, daemon=True).start()


class LevitanHandler(BaseHTTPRequestHandler):
    def _ok(self, body=None):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body or {"status": "ok"}).encode())

    def do_GET(self):
        path = self.path.strip("/").rstrip("/")

        if path == "health":
            self._ok({
                "status": "running",
                "service": "levitan-webhook",
                "pending": len(pending_calls),
                "active": len(active_calls),
            })
            return
        elif path == "status":
            self._ok({
                "service": "levitan-webhook",
                "pending_calls": len(pending_calls),
                "active_calls": {k: v for k, v in list(active_calls.items())[-20:]},
            })
            return
        self._ok({"service": "levitan-webhook"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        path = self.path.strip("/").rstrip("/")

        # JSON registration endpoint
        if path == "register" and "application/json" in self.headers.get("Content-Type", ""):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {}

            phone = data.get("phone", "")
            campaign = data.get("campaign", "levitan")

            cmd_id = register_callback(phone, campaign)
            self._ok({"command_id": cmd_id, "phone": phone})
            return

        # Mango webhook events
        try:
            params = parse_qs(raw)
            json_str = params.get("json", ["{}"])[0]
            data = json.loads(json_str)
        except json.JSONDecodeError:
            data = {"raw": raw[:200]}

        self._ok()

        self._process_mango_event(data, path)

    def _process_mango_event(self, data: dict, path: str):
        """Process Mango event."""
        call_state = data.get("call_state", "?")
        call_id = data.get("call_id", "")
        command_id = data.get("command_id", "")
        entry_id = data.get("entry_id", "")
        from_info = data.get("from") or {}
        to_info = data.get("to") or {}
        from_num = str(from_info.get("number", ""))
        to_num = str(to_info.get("number", ""))
        callback_initiator = data.get("callback_initiator", "")

        # Find pending call
        ctx = None
        for key in [command_id, entry_id, call_id]:
            if key and key in pending_calls:
                ctx = pending_calls[key]
                break

        client_phone = (
            _norm_phone(from_num)
            if callback_initiator != "API"
            else _norm_phone(to_num)
        )

        log.info(
            "📥 %s | %s | %s→%s | cmd=%s call=%s",
            call_state, path, from_num, to_num,
            (command_id or entry_id or "-")[:20],
            (call_id or "-")[:20],
        )

        # Track call
        if call_id:
            if call_id not in active_calls:
                active_calls[call_id] = {
                    "call_id": call_id,
                    "command_id": command_id,
                    "client_phone": client_phone,
                    "events": [],
                    "started": datetime.now().isoformat(),
                }
            active_calls[call_id]["events"].append({
                "state": call_state,
                "time": datetime.now().isoformat(),
            })

        # Handle callback connected → client answered
        if call_state == "Connected" and callback_initiator == "API":
            log.info("✅ CALLBACK ANSWERED: %s", client_phone)

            event = {
                "type": "callback_connected",
                "call_id": call_id,
                "command_id": command_id,
                "phone": client_phone,
                "timestamp": datetime.now().isoformat(),
            }
            _write_event(event)

            if call_id:
                active_calls[call_id]["phone"] = client_phone
                active_calls[call_id]["connected_at"] = datetime.now().isoformat()

                # Schedule greeting play
                _schedule_greeting_play(call_id)

                # Telegram notification
                notify_telegram(
                    f"📞 <b>Новый звонок</b>\n"
                    f"Телефон: {client_phone}\n"
                    f"Статус: Connected"
                )

                ctx_data = ctx or {}
                ctx_data["call_id"] = call_id
                ctx_data["client_phone"] = client_phone

        # Handle call end
        if call_state in ("Disconnected", "Failed"):
            log.info("🔚 CALL ENDED: %s → %s", client_phone, call_state)

            event = {
                "type": "call_end",
                "call_id": call_id,
                "phone": client_phone,
                "state": call_state,
                "timestamp": datetime.now().isoformat(),
            }
            _write_event(event)

            if call_id and call_id in active_calls:
                active_calls[call_id]["ended_at"] = datetime.now().isoformat()
                active_calls[call_id]["end_state"] = call_state
                _save_call_data(call_id, active_calls[call_id])

                duration = ""
                if "connected_at" in active_calls[call_id]:
                    started = datetime.fromisoformat(active_calls[call_id]["connected_at"])
                    ended = datetime.now()
                    duration = f"\nДлительность: {(ended - started).total_seconds():.0f} сек"

                notify_telegram(
                    f"🔚 <b>Звонок завершен</b>\n"
                    f"Телефон: {client_phone}{duration}\n"
                    f"Статус: {call_state}"
                )

            # Cleanup after a while
            if call_id:
                for cmd_key in list(pending_calls.keys()):
                    if pending_calls[cmd_key].get("call_id") == call_id:
                        del pending_calls[cmd_key]

        # Handle recording
        if path == "events/events/record/added":
            rec_id = data.get("recording_id", "") or data.get("record_id", "")
            if rec_id:
                event = {
                    "type": "recording_added",
                    "recording_id": str(rec_id),
                    "call_id": call_id,
                    "timestamp": datetime.now().isoformat(),
                }
                _write_event(event)
                log.info("🎙️ Recording: %s", rec_id)

    def log_message(self, fmt, *args):
        pass


def main():
    port = int(os.getenv("LEVITAN_WEBHOOK_PORT", "8087"))
    server = HTTPServer(("0.0.0.0", port), LevitanHandler)
    log.info("🚀 Levitan Webhook started on port %s", port)
    server.serve_forever()


if __name__ == "__main__":
    main()
