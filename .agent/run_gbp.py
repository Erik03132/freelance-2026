#!/usr/bin/env python3
"""
Global Boot Protocol (GBP) runner
Выполняет все обязательные проверки при старте сессии:
1. Поиск и чтение GLOBAL_BOOT_PROTOCOL.md (если есть)
2. Проверка переменных окружения (GEMINI_API_KEY, PERPLEXITY_API_KEY, …)
3. Пинг MCP‑серверов (StitchMCP)
4. Загрузка и валидация правил (.agent/rules/*)
5. Синхронизация скиллов (проверка, что у каждого агента есть SKILL.md)
6. Подтверждение Scope‑Lock
7. Чтение чек‑поинтов (chp.md, последние отчёты, ACTIVE_TASKS.md)
8. Вывод таблицы готовности агентов
9. (Опционально) проверка эволюции скиллов в .ecc‑library
"""

import os
import subprocess
import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).parents[2]      # ~/freelance-2026
AGENT_ROOT = ROOT / ".agent"
RULES_DIR = AGENT_ROOT / "rules"
SKILLS_ROOT = pathlib.Path(os.getenv("HOME")) / ".gemini" / "antigravity" / "skills"

def read_file(p: pathlib.Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"❌ Ошибка чтения {p.name}: {e}"

def check_env_keys() -> list:
    keys = ["GEMINI_API_KEY", "PERPLEXITY_API_KEY"]
    missing = [k for k in keys if not os.getenv(k)]
    return missing

def ping_mcp() -> bool:
    # простая проверка доступности сервера через curl (если curl установлен)
    try:
        subprocess.run(
            ["curl", "-sSf", "https://stitchmcp.googleapis.com"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False

def load_rules() -> list:
    missing = []
    for fn in ["IRON_RULES.md", "STRICT_SCOPE_LOCK.md"]:
        if not (RULES_DIR / fn).exists():
            missing.append(fn)
    return missing

def skill_readiness() -> dict:
    agents = [
        "igorek-core", "kulibin-engineer", "artemiy-frontend",
        "botman-creator", "rembrandt-designer", "shakespeare-editor",
        "sherl-research", "marketer-strategist"
    ]
    results = {}
    for a in agents:
        skill_path = SKILLS_ROOT / a / "SKILL.md"
        results[a] = skill_path.is_file()
    return results

def read_checkpoints() -> dict:
    chp = ROOT / "chp.md"
    active = ROOT / "ACTIVE_TASKS.md"
    reports_dir = ROOT / "reports"
    latest_report = False
    if reports_dir.is_dir():
        reports = sorted(reports_dir.glob("report-day_*.md"))
        latest_report = bool(reports)
    return {
        "chp.md": chp.is_file(),
        "ACTIVE_TASKS.md": active.is_file(),
        "latest_report": latest_report
    }

def main():
    print("=== GBP RUNNER –", datetime.now().isoformat(), "===\n")
    # 1. Protocol file
    gp_path = RULES_DIR / "GLOBAL_BOOT_PROTOCOL.md"
    print("1️⃣ Протокол", "(найден)" if gp_path.is_file() else "❌ НЕ найден")
    if gp_path.is_file():
        print(read_file(gp_path)[:200] + "...\n")

    # 2. Переменные окружения
    missing_keys = check_env_keys()
    print("2️⃣ Переменные окружения:", "✅ всё в порядке" if not missing_keys else f"❌ Отсутствуют: {', '.join(missing_keys)}")

    # 3. MCP‑сервер
    mcp_ok = ping_mcp()
    print("3️⃣ Доступ к MCP‑серверу:", "✅ доступен" if mcp_ok else "❌ недоступен")

    # 4. Правила
    missing_rules = load_rules()
    print("4️⃣ Правила:", "✅ все есть" if not missing_rules else f"❌ Missing: {', '.join(missing_rules)}")

    # 5. Скиллы
    readiness = skill_readiness()
    print("5️⃣ Проверка скиллов:")
    for ag, ok in readiness.items():
        print(f"   {ag:20} {'✅' if ok else '❌ MISSING'}")

    # 6. Scope‑Lock
    scope_lock = (RULES_DIR / "STRICT_SCOPE_LOCK.md").exists()
    print("6️⃣ Scope‑Lock:", "✅ найден" if scope_lock else "❌ отсутствует")

    # 7. Чек‑поинты
    cp = read_checkpoints()
    print("7️⃣ Чек‑поинты:")
    for k, v in cp.items():
        print(f"   {k:15} {'✅' if v else '❌'}")

    # 8. Итоги
    all_ok = all([
        gp_path.is_file(),
        not missing_keys,
        mcp_ok,
        not missing_rules,
        all(readiness.values()),
        scope_lock,
        all(cp.values())
    ])
    print("\n=== ИТОГИ GBP ===")
    print("✅ Сессия считается **Safe**" if all_ok else "⚠️ Сессия **не Safe** – требуется исправление")

if __name__ == "__main__":
    main()
