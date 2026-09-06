import os
import json
import hashlib
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("MANGO_VPBX_API_KEY", "")
SALT = os.getenv("MANGO_VPBX_API_SALT", "")
EXT = os.getenv("MANGO_FROM_EXTENSION", "22")
BASE = "https://app.mango-office.ru/vpbx/"
PHONE = os.getenv("TEST_PHONE", "79859234644")

payload = {
    "command_id": f"test_levitan_{uuid.uuid4().hex[:8]}",
    "from": {"extension": EXT},
    "to_number": PHONE,
}
j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
sign = hashlib.sha256((KEY + j + SALT).encode()).hexdigest()
r = requests.post(
    f"{BASE}commands/callback",
    data={"vpbx_api_key": KEY, "json": j, "sign": sign},
    timeout=20,
)
print("command_id:", payload["command_id"])
print("status:", r.status_code)
print("body:", r.text)
