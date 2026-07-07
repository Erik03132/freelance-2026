#!/usr/bin/env python3
"""
Ping Checker — проверка "живых" номеров через короткий звонок.

Использует baresip (ext 23) как автоответчик + Mango callback.
Звонит каждому номеру, ждёт 8 секунд, сбрасывает, потом сверяется
со статистикой Mango: если был answer_time — номер "живой".

Запуск:
    source .venv/bin/activate
    python3 scripts/ping_checker.py data/campaigns/csv/test_ext100.csv

Результат:
    data/campaigns/csv/alive_YYYY-MM-DD.csv
    data/campaigns/csv/dead_YYYY-MM-DD.csv
"""
import argparse
import csv
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import requests
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ping-checker")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_DIR = DATA_DIR / "campaigns" / "csv"
CSV_DIR.mkdir(parents=True, exist_ok=True)

BARESIP_DIR = BASE_DIR / "ping_bridge"
PING_EXT = "23"
PING_SIP_DOMAIN = "vpbx400374818.mangosip.ru"

# Настройки пинга
PING_OPERATOR_WAIT = 10      # сколько ждём, пока baresip примет звонок (оператор)
PING_CLIENT_WAIT = 10        # сколько держим линию после ответа оператора
PING_POST_HANGUP_WAIT = 3    # пауза перед запросом статистики
PING_BETWEEN_CALLS = 2       # пауза между звонками


def load_env():
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def norm_phone(num: str) -> str:
    digits = re.sub(r"\D", "", num)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    if digits.startswith("9") and len(digits) == 10:
        digits = "7" + digits
    return digits


def is_valid_phone(num: str) -> bool:
    n = norm_phone(num)
    return len(n) == 11 and n.startswith("7")


def mango_callback(client_phone: str, from_ext: str = PING_EXT) -> dict:
    key = os.environ.get("MANGO_VPBX_API_KEY", "")
    salt = os.environ.get("MANGO_VPBX_API_SALT", "")
    payload = {
        "command_id": f"ping_{int(time.time() * 1000)}",
        "from": {"extension": from_ext},
        "to_number": norm_phone(client_phone),
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((key + j + salt).encode()).hexdigest()
    try:
        r = requests.post(
            "https://app.mango-office.ru/vpbx/commands/callback",
            data={"vpbx_api_key": key, "json": j, "sign": sign},
            timeout=30,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


STATUS_ORDER = {"alive": 3, "no_answer": 2, "unreachable": 1, "unknown": 0}


def get_call_status(phone: str, after_ts: float) -> str:
    """
    Проверить результат звонка в статистике Mango.
    Возвращает: alive | no_answer | unreachable | unknown.

    Расшифровка call_type (на основе наблюдений):
      1110 + answer_time != 0  → снял трубку (alive)
      1120                     → дозвонился, гудок, не ответил (no_answer)
      1131                     → недоступен / вне сети / отключен (unreachable)
    """
    key = os.environ.get("MANGO_VPBX_API_KEY", "")
    salt = os.environ.get("MANGO_VPBX_API_SALT", "")
    target = norm_phone(phone)
    result = "unknown"

    payload = {"date_from": int(after_ts - 60), "date_to": int(time.time())}
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((key + j + salt).encode()).hexdigest()
    try:
        r = requests.post(
            "https://app.mango-office.ru/vpbx/stats/request",
            data={"vpbx_api_key": key, "json": j, "sign": sign},
            timeout=30,
        )
        resp = r.json()
        stats_key = resp.get("key")
        if not stats_key:
            return result

        payload2 = {"key": stats_key}
        j2 = json.dumps(payload2, separators=(",", ":"), ensure_ascii=False)
        sign2 = hashlib.sha256((key + j2 + salt).encode()).hexdigest()

        for _ in range(8):
            r2 = requests.post(
                "https://app.mango-office.ru/vpbx/stats/result",
                data={"vpbx_api_key": key, "json": j2, "sign": sign2},
                timeout=30,
            )
            text = r2.text.strip()
            if text:
                reader = csv.reader(text.splitlines(), delimiter=";")
                for row in reader:
                    if len(row) < 9:
                        continue
                    to_number = row[7].strip()
                    from_ext = row[4].strip()
                    answer_time = row[3].strip()
                    call_type = row[8].strip()
                    try:
                        start_ts = int(row[1])
                    except ValueError:
                        continue
                    if norm_phone(to_number) != target or from_ext != PING_EXT or start_ts < int(after_ts):
                        continue

                    if call_type == "1110" and answer_time and answer_time != "0":
                        new_status = "alive"
                    elif call_type == "1131":
                        new_status = "unreachable"
                    elif call_type in ("1120", "1110"):
                        new_status = "no_answer"
                    else:
                        new_status = "unknown"

                    if STATUS_ORDER[new_status] > STATUS_ORDER[result]:
                        result = new_status
            time.sleep(2)
    except Exception as e:
        log.error(f"Ошибка проверки статистики: {e}")
    return result


class PingBridge:
    """Управляет baresip для пинга."""

    def __init__(self):
        self.proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._lines: list[str] = []
        self.established = False
        self.ended = False
        self._running = False

    def start(self) -> bool:
        log_file = BARESIP_DIR / "baresip.log"
        log_file.write_text("")
        self.proc = subprocess.Popen(
            ["baresip", "-f", str(BARESIP_DIR), "-T", "-c"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._running = True
        self._reader_thread = threading.Thread(target=self._reader, daemon=True)
        self._reader_thread.start()

        for _ in range(60):
            if self._has_line(lambda l: "200 OK" in l and f"user1@{PING_SIP_DOMAIN}" in l):
                log.info("baresip зарегистрирован")
                return True
            time.sleep(0.5)
        log.error("baresip не зарегистрировался")
        return False

    def _reader(self):
        log_file = BARESIP_DIR / "baresip.log"
        with open(log_file, "a", encoding="utf-8") as fh:
            for line in self.proc.stdout:
                fh.write(line)
                fh.flush()
                with self._lock:
                    self._lines.append(line)
                    if "Call established" in line:
                        self.established = True
                    if "Call with" in line and "terminated" in line:
                        self.ended = True
                    if "terminated by signal" in line:
                        self.ended = True
        self._running = False

    def _has_line(self, pred) -> bool:
        with self._lock:
            return any(pred(l) for l in self._lines)

    def reset_flags(self):
        with self._lock:
            self.established = False
            self.ended = False
            self._lines.clear()

    def send_cmd(self, cmd: str):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.write(cmd + "\n")
                self.proc.stdin.flush()
            except Exception as e:
                log.debug(f"Не удалось отправить команду baresip: {e}")

    def ping(self, phone: str) -> dict:
        self.reset_flags()
        result = {"phone": phone, "status": "unknown", "error": None}

        cb_resp = mango_callback(phone)
        if cb_resp.get("result") != 1000:
            result["error"] = f"callback result={cb_resp.get('result')}"
            return result

        call_start = time.time()

        # Ждём, пока baresip примет звонок (оператор)
        deadline = call_start + PING_OPERATOR_WAIT
        while time.time() < deadline:
            if self.established:
                break
            time.sleep(0.2)
        if not self.established:
            result["error"] = "baresip не ответил на операторский звонок"
            self.send_cmd("/hangup")
            return result

        # Держим линию, чтобы у клиента было время снять трубку
        time.sleep(PING_CLIENT_WAIT)
        self.send_cmd("/hangup")

        # Ждём завершения звонка
        deadline = time.time() + 5
        while time.time() < deadline:
            if self.ended:
                break
            time.sleep(0.2)

        # Проверяем статистику Mango
        time.sleep(PING_POST_HANGUP_WAIT)
        result["status"] = get_call_status(phone, call_start)
        result["alive"] = result["status"] == "alive"
        return result

    def stop(self):
        if self.proc:
            self.send_cmd("/quit")
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.proc.kill()


def load_contacts(csv_path: Path) -> list[dict]:
    contacts = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phones_raw = row.get("Телефоны", "") or ""
            for phone in re.findall(r"[\d\-\(\)\+\s]{7,}", phones_raw):
                normalized = norm_phone(phone)
                if is_valid_phone(normalized):
                    contacts.append({
                        "name": (row.get("Название", "") or "").strip(),
                        "description": (row.get("Описание", "") or "").strip(),
                        "region": (row.get("Регион", "") or "").strip(),
                        "city": (row.get("Город", "") or "").strip(),
                        "contact_name": (row.get("Имя", "") or "").strip(),
                        "phone": normalized,
                    })
                    break
    return contacts


def save_results(results: dict[str, list[dict]], prefix: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    prefix = f"{prefix}_" if prefix else ""
    paths = {}
    fieldnames = ["Название", "Описание", "Регион", "Город", "Имя", "Телефоны"]
    for status, rows in results.items():
        if not rows:
            continue
        path = CSV_DIR / f"{prefix}{status}_{today}.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in rows:
                writer.writerow({
                    "Название": c["name"],
                    "Описание": c["description"],
                    "Регион": c["region"],
                    "Город": c["city"],
                    "Имя": c["contact_name"],
                    "Телефоны": c["phone"],
                })
        paths[status] = path
    return paths


def main():
    load_env()

    import argparse
    parser = argparse.ArgumentParser(description="Пинг-чекер номеров")
    parser.add_argument("csv", nargs="?", help="Путь к CSV с контактами")
    parser.add_argument("limit", nargs="?", type=int, default=0, help="Лимит контактов")
    parser.add_argument("--quick", action="store_true", help="Быстрый пинг: 2 сек, только проверка доступности")
    args = parser.parse_args()

    if not args.csv:
        parser.print_help()
        sys.exit(1)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        log.error(f"Файл не найден: {csv_path}")
        sys.exit(1)

    limit = args.limit
    quick = args.quick

    if quick:
        global PING_CLIENT_WAIT
        PING_CLIENT_WAIT = 3
        log.info("Режим: быстрый пинг (~5 сек, только проверка доступности номера)")

    contacts = load_contacts(csv_path)
    if limit:
        contacts = contacts[:limit]
    log.info(f"Загружено контактов: {len(contacts)}")

    bridge = PingBridge()
    if not bridge.start():
        log.error("Не удалось запустить baresip")
        sys.exit(1)

    if quick:
        buckets: dict[str, list[dict]] = {
            "ok": [],
            "unreachable": [],
        }
    else:
        buckets: dict[str, list[dict]] = {
            "alive": [],
            "no_answer": [],
            "unreachable": [],
            "unknown": [],
        }
    stopped = False

    def signal_handler(signum, frame):
        nonlocal stopped
        stopped = True

    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        for idx, contact in enumerate(contacts, 1):
            if stopped:
                log.info("Остановлено пользователем")
                break
            phone = contact["phone"]
            log.info(f"[{idx}/{len(contacts)}] Пинг +{phone}")
            try:
                res = bridge.ping(phone)
            except Exception as e:
                log.error(f"Ошибка пинга {phone}: {e}")
                res = {"phone": phone, "status": "unknown", "error": str(e)}

            status = res.get("status", "unknown")
            if res.get("error"):
                log.warning(f"  ⚠️ {res['error']}")

    if quick:
        bucket_status = "ok" if status == "alive" else "unreachable"
        labels = {
            "alive": "🟢 Доступен",
            "no_answer": "🔴 Недоступен (нет ответа за 3с)",
            "unreachable": "🔴 Недоступен",
            "unknown": "🔴 Недоступен (нет ответа за 3с)",
        }
                log.info(f"  {labels.get(status, '❓')}")
            else:
                bucket_status = status
                labels = {
                    "alive": "🟢 Живой",
                    "no_answer": "🟡 Гудок, не ответил",
                    "unreachable": "🔴 Недоступен",
                    "unknown": "⚪ Неизвестно",
                }
                log.info(f"  {labels.get(status, '❓')} ({status})")
            buckets[bucket_status].append(contact)

            if idx < len(contacts) and not stopped:
                time.sleep(PING_BETWEEN_CALLS)
    finally:
        bridge.stop()

    paths = save_results(buckets, prefix="ping")
    log.info("=" * 50)
    for status, path in paths.items():
        log.info(f"{status}: {len(buckets[status])} -> {path}")
    if quick:
        total_ok = len(buckets["ok"])
        log.info(f"Итого пригодных для обзвона: {total_ok}")
    else:
        total_ok = len(buckets["alive"]) + len(buckets["no_answer"])
        log.info(f"Итого пригодных для обзвона (alive + no_answer): {total_ok}")


if __name__ == "__main__":
    main()
