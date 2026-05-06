#!/usr/bin/env python3
"""
🐕 WATCHDOG — 3-уровневая защита vezemcip.ru
Уровень 1: /api/health каждые 5 мин (БЕЗ LLM — бесплатно)
Уровень 2: Авторестарт PM2/nginx при падении
Уровень 3: Алерт в Telegram (с прокси, т.к. TG заблокирован в РФ)
"""
import subprocess, json, os, sys, time
from datetime import datetime

BOT_TOKEN  = "8336409939:AAHr2wbuOfED5woCzCokKKM9JnkVRYepfms"
ADMIN_ID   = "176203333"
PROXY      = "socks5h://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469"
STATE_FILE = "/tmp/watchdog_state"
LOG_FILE   = "/var/log/watchdog.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def tg(msg):
    try:
        payload = json.dumps({
            "chat_id": ADMIN_ID,
            "text": msg,
            "parse_mode": "Markdown"
        })
        r = subprocess.run([
            "curl", "-s", "-x", PROXY,
            "-X", "POST",
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            "-H", "Content-Type: application/json",
            "-d", payload,
            "--max-time", "10"
        ], capture_output=True, timeout=15)
        is_ok = b'"ok":true' in r.stdout
        log(f"  TG: {'OK' if is_ok else 'ERROR: ' + r.stdout[:80].decode(errors='replace')}")
    except Exception as e:
        log(f"  TG error: {e}")

def now_str():
    return datetime.now().strftime("%H:%M %d.%m.%Y")

def check_health():
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/tmp/wd_resp", "-w", "%{http_code}",
             "https://vezemcip.ru/api/health", "--max-time", "10"],
            capture_output=True, timeout=15
        )
        code = r.stdout.decode().strip()
        body = open("/tmp/wd_resp").read() if os.path.exists("/tmp/wd_resp") else ""
        is_ok = (code == "200") and ('"status":"ok"' in body)
        return is_ok, code, body[:120]
    except Exception as e:
        return False, "ERR", str(e)

def port_up(port):
    r = subprocess.run(["ss", "-tlnp"], capture_output=True)
    return f":{port}" in r.stdout.decode()

def pm2_restart(name):
    subprocess.run(
        ["pm2", "restart", name],
        cwd="/root/antigravity/ai-eggs",
        capture_output=True
    )

# === Читаем последний статус ===
last_status = "ok"
if os.path.exists(STATE_FILE):
    last_status = open(STATE_FILE).read().strip()

# === УРОВЕНЬ 1: /api/health (без LLM, бесплатно) ===
ok, code, body = check_health()

if ok:
    log("OK (health) HTTP=200")
    if last_status == "fail":
        tg(f"✅ *RECOVERED: vezemcip.ru*\n\nЧат-бот снова работает 🎉\n⏰ {now_str()}")
    open(STATE_FILE, "w").write("ok")
    sys.exit(0)

# === УРОВЕНЬ 2: Диагностика и авторестарт ===
log(f"FAIL: HTTP={code} | body={body}")
actions = []

if not port_up(5000):
    pm2_restart("angela-server")
    actions.append("• angela-server: перезапущен")
    log("  pm2 restart angela-server")
    time.sleep(5)

if not port_up(4321):
    pm2_restart("vezem-web")
    actions.append("• vezem-web: перезапущен")
    log("  pm2 restart vezem-web")
    time.sleep(5)

nginx_active = subprocess.run(
    ["systemctl", "is-active", "nginx"], capture_output=True
).stdout.decode().strip() == "active"

if not nginx_active:
    subprocess.run(["systemctl", "restart", "nginx"])
    actions.append("• nginx: рестарт")
    log("  nginx restart")
else:
    subprocess.run(["nginx", "-s", "reload"])
    actions.append("• nginx: reload")
    log("  nginx reload")

# === УРОВЕНЬ 3: Алерт в Telegram ===
if last_status == "ok":
    actions_str = "\n".join(actions) if actions else "• сервисы работают, проверь nginx-конфиг"
    tg(
        f"🚨 *ALERT: vezemcip.ru*\n\n"
        f"❌ Чат-бот не отвечает!\n"
        f"HTTP: {code}\n\n"
        f"🔧 *Авторестарт выполнен:*\n{actions_str}\n\n"
        f"⏰ {now_str()}"
    )

open(STATE_FILE, "w").write("fail")

# Повторная проверка через 60 сек
log("  Ждём 60 сек для повторной проверки...")
time.sleep(60)

ok2, code2, _ = check_health()
if ok2:
    log("  Восстановлено после рестарта ✅")
    tg(f"✅ *RECOVERED: vezemcip.ru*\n\nАвторестарт помог ✅\n⏰ {now_str()}")
    open(STATE_FILE, "w").write("ok")
else:
    log(f"  Всё ещё не работает (HTTP={code2}) — нужна ручная проверка")
    tg(
        f"‼️ *НЕ ВОССТАНОВЛЕН: vezemcip.ru*\n\n"
        f"Авторестарт не помог!\n"
        f"HTTP: {code2}\n"
        f"Нужна ручная проверка 🛠️\n"
        f"⏰ {now_str()}"
    )
