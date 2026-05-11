#!/usr/bin/env python3
"""Автопостинг ВКонтакте — cron-обёртка.
Запускает vk_smart_poster.py для всех групп.
Crontab: 0 9 * * * /path/to/venv/bin/python3 /path/to/vk_autoposter.py
"""
import subprocess, sys, os, datetime

VENV_PYTHON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "bin", "python3")
SMART_POSTER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vk_smart_poster.py")

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def main():
    log("=== VK AUTOPOST START ===")

    if not os.path.isfile(SMART_POSTER):
        log(f"SCRIPT NOT FOUND: {SMART_POSTER}")
        sys.exit(1)

    # Публикуем по 1 посту для каждой группы
    try:
        result = subprocess.run(
            [VENV_PYTHON, SMART_POSTER, "all", "--count", "1"],
            capture_output=True, text=True, timeout=120,
            cwd=os.path.dirname(SMART_POSTER),
        )
        log(result.stdout.strip() if result.stdout else "(no output)")
        if result.stderr:
            log(f"STDERR: {result.stderr.strip()}")
        log(f"EXIT CODE: {result.returncode}")
    except Exception as e:
        log(f"EXCEPTION: {e}")

    log("=== VK AUTOPOST END ===")

if __name__ == "__main__":
    main()
