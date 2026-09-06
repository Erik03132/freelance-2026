#!/usr/bin/env python3
"""Upload levitan_greeting_lead.wav to Mango Office and get audio_id."""

import hashlib
import json
import os
import sys
from pathlib import Path

import requests

# Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
for _env in (BASE_DIR / ".env", BASE_DIR / "deploy" / ".env"):
    if _env.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(_env, override=True)
            break
        except ImportError:
            pass

# Remove proxy for Russian APIs
for _proxy in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(_proxy, None)

VPBX_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
VPBX_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"

if not VPBX_API_KEY or not VPBX_API_SALT:
    print("❌ MANGO_VPBX_API_KEY or MANGO_VPBX_API_SALT not set in .env")
    sys.exit(1)

WAV_FILE = BASE_DIR / "data" / "voice_cache" / "levitan_greeting_lead.wav"


def _mango_sign(payload: dict) -> str:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((VPBX_API_KEY + j + VPBX_API_SALT).encode()).hexdigest()


def upload_audio():
    if not WAV_FILE.exists():
        print(f"❌ File not found: {WAV_FILE}")
        sys.exit(1)

    import hashlib

    filename = WAV_FILE.name
    command_id = f"levitan_upload_{hashlib.sha256(filename.encode()).hexdigest()[:8]}"

    print(f"📤 Uploading {filename} ({WAV_FILE.stat().st_size // 1024} KB)...")

    with open(WAV_FILE, "rb") as f:
        file_data = f.read()

    # Prepare the JSON payload
    json_payload = {
        "command_id": command_id,
        "filename": filename,
    }

    # The Mango API expects the file in multipart/form-data
    # and the JSON/sign in form fields
    j = json.dumps(json_payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((VPBX_API_KEY + j + VPBX_API_SALT).encode()).hexdigest()

    try:
        response = requests.post(
            f"{MANGO_API_BASE}files/upload",
            files={"file": (filename, file_data, "audio/wav")},
            data={
                "vpbx_api_key": VPBX_API_KEY,
                "json": j,
                "sign": sign,
            },
            timeout=60,
        )

        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, ensure_ascii=False)}")

        if result.get("result") == 1000:
            file_id = result.get("file_id")
            print("\n✅ Upload successful!")
            print(f"   file_id: {file_id}")
            print(f"   filename: {result.get('filename')}")
            return file_id
        else:
            print(f"\n❌ Upload failed: {result}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    audio_id = upload_audio()
    if audio_id:
        print("\n📝 Update levitan_webhook.py:")
        print(f"   Replace 1000550776 with {audio_id}")
