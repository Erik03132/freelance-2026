"""AI-Defender — report generation: SECURITY.md + audit-report.json."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


def _sev_order(s):
    return {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(s, 9)


def build_report(project: str, target: str, static: dict, ext: list[dict]) -> dict:
    """Собирает единый отчёт из статики + внешних сканеров."""
    all_findings: list[dict] = list(static.get("findings", []))
    ext_findings = []
    for tool in ext:
        for f in tool.get("findings", []):
            f["tool"] = tool.get("tool")
            ext_findings.append(f)
        if tool.get("error"):
            label = f"tool error: {tool['error']}"
            if tool.get("detail"):
                label += f" — {tool['detail']}"
            ext_findings.append(
                {"tool": tool.get("tool"), "severity": "LOW", "label": label, "file": ""}
            )
    all_findings.extend(ext_findings)
    all_findings.sort(key=lambda f: (_sev_order(f.get("severity")), f.get("file", ""), f.get("line", 0)))

    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in all_findings:
        s = f.get("severity")
        if s in by_severity:
            by_severity[s] += 1

    report = {
        "project": project,
        "target": target,
        "date": datetime.now(timezone.utc).isoformat(),
        "files_scanned": static.get("files_scanned", 0),
        "by_severity": by_severity,
        "findings": all_findings,
        "meta": {"static_by_pattern": static.get("by_pattern", {})},
    }
    return report


def severity_emoji(s: str) -> str:
    return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(s, "⚪")


def render_markdown(report: dict) -> str:
    """Рендерит SECURITY.md из отчёта."""
    b = report["by_severity"]
    lines = [
        f"# 🔐 Security Audit — {report['project']}",
        "",
        f"- **Дата:** {report['date']}",
        f"- **Цель:** `{report['target']}`",
        f"- **Файлов просканировано:** {report['files_scanned']}",
        "",
        "## Сводка по severity",
        "",
        "| Severity | Кол-во |",
        "|----------|--------|",
        f"| 🔴 CRITICAL | {b['CRITICAL']} |",
        f"| 🟠 HIGH | {b['HIGH']} |",
        f"| 🟡 MEDIUM | {b['MEDIUM']} |",
        f"| 🔵 LOW | {b['LOW']} |",
        "",
        "## Находки",
        "",
    ]
    if not report["findings"]:
        lines.append("_Находок нет._")
    for i, f in enumerate(report["findings"], start=1):
        loc = f.get("file", "")
        if f.get("line"):
            loc = f"{loc}:{f['line']}"
        tool = f" `[{f.get('tool')}]`" if f.get("tool") else ""
        lines.append(
            f"{i}. {severity_emoji(f.get('severity',''))} **{f.get('severity','?')}** "
            f"`{f.get('pattern') or f.get('advisory') or f.get('package','')}`{tool}"
        )
        lines.append(f"   - **Где:** {loc}")
        lines.append(f"   - **Что:** {f.get('label', '')}")
        if f.get("fix"):
            lines.append(f"   - **Фикс:** {f.get('fix')}")
        lines.append("")
    return "\n".join(lines)


def save_report(report: dict, out_dir: str) -> tuple[str, str]:
    """Сохраняет SECURITY.md и audit-report.json. Возвращает (md_path, json_path)."""
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "SECURITY.md")
    json_path = os.path.join(out_dir, "audit-report.json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(report))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return md_path, json_path
