#!/usr/bin/env python3
"""
Тестовый callback в Mango Office.

Запуск:
    python3 scripts/test_callback.py +79161234567
    python3 scripts/test_callback.py 79161234567

Скрипт отправляет callback с from.extension=22 на указанный номер
и показывает ответ API.
"""

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

MANGO_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"


def norm_phone(num: str) -> str:
    d = "".join(c for c in num if c.isdigit())
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d


def send_callback(to_number: str, from_extension: str = MANGO_FROM_EXTENSION) -> dict:
    command_id = f"test_{uuid.uuid4().hex[:8]}"
    payload = {
        "command_id": command_id,
        "from": {"extension": from_extension},
        "to_number": norm_phone(to_number),
        "timeout": 30,
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()

    print(f"→ Отправляю callback: ext={from_extension} → {to_number}")
    print(f"  JSON: {j}")
    r = requests.post(
        f"{MANGO_API_BASE}commands/callback",
        data={"vpbx_api_key": MANGO_API_KEY, "json": j, "sign": sign},
        timeout=20,
    )
    print(f"  HTTP {r.status_code}")
    try:
        result = r.json()
    except Exception:
        result = {"raw": r.text}
    print(f"  Ответ: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


if __name__ == "__main__":
    if not MANGO_API_KEY or not MANGO_API_SALT:
        print("❌ MANGO_VPBX_API_KEY или MANGO_VPBX_API_SALT не заданы в .env")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Использование: python3 scripts/test_callback.py <номер>")
        sys.exit(1)

    phone = sys.argv[1]
    send_callback(phone)
