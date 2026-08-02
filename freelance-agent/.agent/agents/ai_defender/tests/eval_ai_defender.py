"""Eval suite for ai_defender — deterministic security checks.

Запуск: python3 tests/eval_ai_defender.py
Прогонять перед любыми изменениями scan-логики / промптов / модели (правило №9).

Критерии:
- каждый класс уязвимости детектится (true positive)
- чистый код не даёт ложных срабатываний (false positive == 0)
"""

from __future__ import annotations

import os
import sys
import tempfile

AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if AGENTS not in sys.path:
    sys.path.insert(0, AGENTS)

from ai_defender.scan import scan_path, mask_secret  # noqa: E402

FIXTURES_TP = {
    "hardcoded_secret": 'api_key = "sk-or-1234567890abcdef"',  # gitleaks:allow
    "public_secret_var": 'export VITE_API_KEY="12345"',
    "sql_concat": 'query = "SELECT * FROM users WHERE name = " + req.body.name',
    "command_injection": 'os.system("ping " + request.args["host"])',
    "eval_usage": 'result = eval(user_input)',
    "pickle_loads": 'data = pickle.loads(request.body)',
    "dangerous_innerhtml": 'el.innerHTML = user_message',
    "secret_in_log": 'print("token=" + auth_token)',
    "weak_crypto": 'hash = hashlib.md5(password.encode()).hexdigest()',
    "shell_true": 'subprocess.run(cmd, shell=True)',
}

FIXTURES_CLEAN = [
    'API_KEY = os.environ.get("API_KEY", "")',
    'db.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
    'el.textContent = user_message',
    "logger.info('user created')",
    "hash = hashlib.sha256(password.encode()).hexdigest()",
    "subprocess.run([\"ls\", \"-l\"])",
    'resp = requests.get(url, timeout=10)',
    "console.error('RESEND_API_KEY не задан — email не отправлен')",
]


def _write(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tp_dir = os.path.join(tmp, "tp")
        clean_dir = os.path.join(tmp, "clean")
        os.makedirs(tp_dir)
        os.makedirs(clean_dir)
        for i, (pid, code) in enumerate(FIXTURES_TP.items()):
            _write(os.path.join(tp_dir, f"vuln_{i}_{pid}.py"), code)
        for i, code in enumerate(FIXTURES_CLEAN):
            _write(os.path.join(clean_dir, f"clean_{i}.py"), code)

        tp_res = scan_path(tp_dir)
        clean_res = scan_path(clean_dir)

        detected = {f["pattern"] for f in tp_res["findings"]}
        for pid in FIXTURES_TP:
            if pid not in detected:
                fails.append(f"TP MISS: паттерн '{pid}' не найден")

        if clean_res["findings"]:
            found = [f["pattern"] for f in clean_res["findings"]]
            fails.append(f"FP: чистый код дал находки: {found}")

        for f in tp_res["findings"]:
            if f["pattern"] == "hardcoded_secret" and len(f["snippet"]) >= 40:
                if "1234567890abcdef" in f["snippet"]:
                    fails.append("MASK: секрет не замаскирован")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"✅ EVAL PASSED — {len(FIXTURES_TP)} TP classes detected, 0 FP, masking OK")
