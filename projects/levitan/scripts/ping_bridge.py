#!/usr/bin/env python3
"""Ping Bridge — автоответчик для проверки "живых" номеров.

Запускает baresip с answermode=auto и короткой тишиной.
Mango callback звонит на этот extension, baresip снимает трубку,
играет 1 секунду тишины и вешает трубку.
"""
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger("ping-bridge")

BASE_DIR = Path(__file__).resolve().parent.parent
BARESIP_DIR = BASE_DIR / "ping_bridge"
LOG_FILE = BARESIP_DIR / "baresip.log"

process: subprocess.Popen | None = None


def cleanup(signum=None, frame=None):
    if process:
        log.info("Останавливаю baresip...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


def main():
    log.info(f"Запуск baresip из {BARESIP_DIR}")
    global process
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        process = subprocess.Popen(
            ["baresip", "-f", str(BARESIP_DIR), "-T", "-c"],
            stdin=subprocess.PIPE,
            stdout=fh,
            stderr=subprocess.STDOUT,
            text=True,
        )
    log.info(f"baresip PID {process.pid}")
    try:
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
