"""
Планировщик Senator AI — ежедневный автоматический цикл.
Расписание:
  - 07:00 — Сканирование RSS + Deep Search + Генерация инициативы
  - 10:00 — Отправка инициативы сенатору в Telegram
"""
import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime

from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# Расписание (часы по серверному времени)
PIPELINE_HOUR = 7   # Запуск полного pipeline
DELIVERY_HOUR = 10   # Доставка в Telegram

VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable  # Фоллбэк на текущий Python


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(os.path.join(LOG_DIR, "scheduler.log"), "a") as f:
        f.write(line + "\n")


def run_pipeline():
    """Запуск полного pipeline через senator_core."""
    log("🏛️ Запуск ежедневного pipeline...")
    try:
        sys.path.insert(0, SCRIPT_DIR)
        from senator_core import run_daily_pipeline
        result = run_daily_pipeline()
        if result:
            initiative = result.get("initiative", {})
            log(f"  ✅ Инициатива: {initiative.get('title', '?')}")
            return result
        else:
            log("  ⚠️ Pipeline вернул пустой результат")
    except Exception as e:
        log(f"  ❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
    return None


def send_to_telegram(text):
    """Отправляет текст сенатору в Telegram."""
    import requests

    token = os.getenv("SENATOR_BOT_TOKEN")
    admin_id = os.getenv("SENATOR_ADMIN_ID", "176203333")

    if not token:
        log("  ⚠️ SENATOR_BOT_TOKEN не задан, пропускаю отправку")
        return False

    try:
        # Разбиваем длинные сообщения
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": admin_id, "text": part},
                timeout=15,
            )
            if resp.status_code != 200:
                log(f"  ⚠️ Telegram API error: {resp.text[:200]}")
                return False
        log(f"  ✅ Отправлено в Telegram ({len(parts)} сообщ.)")
        return True
    except Exception as e:
        log(f"  ❌ Telegram send error: {e}")
        return False


def deliver_initiative():
    """Загружает сегодняшнюю инициативу и отправляет в Telegram."""
    import json
    today = datetime.now().strftime("%Y-%m-%d")
    digest_path = os.path.join(BASE_DIR, "data", "daily_digests", f"digest_{today}.json")

    if not os.path.exists(digest_path):
        log(f"  ⚠️ Дайджест за {today} не найден (pipeline не запускался?)")
        return

    with open(digest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    initiative = data.get("initiative", {})
    text = initiative.get("text", "")

    if not text:
        log("  ⚠️ Инициатива пуста")
        return

    header = f"🏛️ Доброе утро!\n\nВот инициатива на сегодня ({today}):\n\n{'─'*30}\n\n"
    send_to_telegram(header + text)


def main():
    log("🕐 ПЛАНИРОВЩИК МУСТАЯ v1.0")
    log(f"   Pipeline: {PIPELINE_HOUR}:00")
    log(f"   Доставка: {DELIVERY_HOUR}:00")

    executed_today = set()

    while True:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        hour = now.hour
        minute = now.minute

        # === PIPELINE (07:00) ===
        task_pipeline = f"{today}-pipeline"
        if hour == PIPELINE_HOUR and minute < 5 and task_pipeline not in executed_today:
            log("⚙️ ЗАПУСК ЕЖЕДНЕВНОГО PIPELINE...")
            run_pipeline()
            executed_today.add(task_pipeline)

        # === ДОСТАВКА (10:00) ===
        task_delivery = f"{today}-delivery"
        if hour == DELIVERY_HOUR and minute < 5 and task_delivery not in executed_today:
            log("📱 ДОСТАВКА ИНИЦИАТИВЫ...")
            deliver_initiative()
            executed_today.add(task_delivery)

        # Очистка кэша в полночь
        if hour == 0 and minute < 5:
            executed_today.clear()
            log("♻️ Кэш задач очищен")

        time.sleep(60)


if __name__ == "__main__":
    main()
