#!/usr/bin/env python3
"""Тестовый звонок на один номер через Mango callback."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dialer_bot import mango_callback, wait_for_recording

phone = "+79687896924"

print(f"📞 Звоню на {phone}...")
result = mango_callback(phone)
print(f"Callback result: {result}")

if result.get("result") in (1000, "1000"):
    import time
    call_start = time.time()
    print("✅ Звонок инициирован. Ожидаю запись...")
    recording_id = wait_for_recording(phone, call_start, timeout=90)
    if recording_id:
        print(f"🎙 Запись найдена: {recording_id}")
    else:
        print("⚫ Нет записи (не взял трубку или короткий разговор)")
else:
    print(f"⚠️ Ошибка callback: {result}")
