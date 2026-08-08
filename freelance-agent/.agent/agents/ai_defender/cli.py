"""🛡️ AI-Defender — Security Agent CLI.

Запуск: python3 -m ai_defender [opts]
Аудит секретов, уязвимостей, зависимостей, MCP. Отчёт: SECURITY.md + JSON.

Использование:
    python3 -m ai_defender --audit ./src
    python3 -m ai_defender --deps ./src
    python3 -m ai_defender --llm ./src [--frame owasp|mcp]
    python3 -m ai_defender --full ./src [--out ./security]
"""

import argparse
import os
import sys

_AGENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

from .deps_scan import scan_all  # noqa: E402
from .llm_audit import count_files, deep_audit  # noqa: E402
from .report import build_report, save_report  # noqa: E402
from .scan import scan_path  # noqa: E402


def _out_dir(args_out: str | None, target: str) -> str:
    if args_out:
        return args_out
    if os.path.isdir(target):
        return os.path.join(target, "security")
    return os.path.join(os.path.dirname(target) or ".", "security")


def main():
    parser = argparse.ArgumentParser(
        description="🛡️ AI-Defender — Security Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python3 -m ai_defender --audit ./src\n"
        "  python3 -m ai_defender --full ./src --out ./security\n"
        "  python3 -m ai_defender --llm ./mcp_server --frame mcp\n",
    )
    parser.add_argument("--audit", "-a", type=str, default=None, help="Static scan of file/dir")
    parser.add_argument("--deps", "-d", type=str, default=None, help="Dependency/tooling scan")
    parser.add_argument("--llm", "-l", type=str, default=None, help="LLM deep audit")
    parser.add_argument("--frame", type=str, default="owasp", choices=["owasp", "mcp"], help="LLM audit frame")
    parser.add_argument("--full", type=str, default=None, help="Static + deps + LLM in one pass")
    parser.add_argument("--out", "-o", type=str, default=None, help="Output dir for report")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()

    target = args.full or args.audit or args.deps or args.llm
    if not target:
        parser.print_help()
        sys.exit(1)

    project = os.path.basename(os.path.abspath(target)) or "project"
    if args.audit or args.full:
        static = scan_path(target)
    elif args.llm:
        static = {"files_scanned": count_files(target), "findings": [], "by_pattern": {}}
    else:
        static = {"files_scanned": 0, "findings": []}
    ext = scan_all(target) if (args.deps or args.full) else []
    report = build_report(project, target, static, ext)

    if args.full or args.llm:
        frame = "mcp" if args.frame == "mcp" else "owasp"
        llm_md = deep_audit(target, frame=frame)
        if llm_md:
            out = _out_dir(args.out, target)
            os.makedirs(out, exist_ok=True)
            with open(os.path.join(out, "llm-deep-audit.md"), "w", encoding="utf-8") as f:
                f.write(llm_md)
            print(f"🧠 LLM deep audit saved ({frame} frame).")

    md_path, json_path = save_report(report, _out_dir(args.out, target))
    print(f"📄 Отчёт: {md_path}")
    print(f"📦 JSON:  {json_path}")
    if args.json:
        import json as _json

        print(_json.dumps({"by_severity": report["by_severity"], "findings": len(report["findings"])}))
        return

    b = report["by_severity"]
    print(
        f"🔴 CRITICAL={b['CRITICAL']} 🟠 HIGH={b['HIGH']} "
        f"🟡 MEDIUM={b['MEDIUM']} 🔵 LOW={b['LOW']}"
    )
    for f in report["findings"][:20]:
        loc = f"{f.get('file','')}:{f.get('line','')}" if f.get("line") else f.get("file", "")
        print(f"  {f.get('severity','?')}  {f.get('pattern') or f.get('package','')}  {loc}  — {f.get('label','')[:80]}")
    if len(report["findings"]) > 20:
        print(f"  ... и ещё {len(report['findings'])-20} находок")


if __name__ == "__main__":
    main()
