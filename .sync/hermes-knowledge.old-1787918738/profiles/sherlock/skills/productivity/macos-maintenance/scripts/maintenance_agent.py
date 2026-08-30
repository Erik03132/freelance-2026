#!/usr/bin/env python3
"""
Maintenance Agent — агент обслуживания macOS.
Следит за чисткой мусора и держит систему в рабочем состоянии.

Режимы:
  --dry-run   (по умолчанию) — только отчёт, ничего не удаляет
  --clean     — реально чистит мусор (по возрасту, безопасно)

Безопасность:
  - трогаем только Корзину, кэши и temp по возрасту (старше AGE_DAYS)
  - никогда не удаляем системные файлы, библиотеки приложений, данные пользователя
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta

# ---- Конфигурация ----
HOME = os.path.expanduser("~")
AGE_DAYS = 7  # удаляем файлы старше N дней
REPORT_DIR = os.path.join(HOME, "maintenance-agent", "reports")

# Пути для очистки (только безопасные)
TRASH = os.path.join(HOME, ".Trash")
CACHE_TARGETS = [
    os.path.join(HOME, "Library", "Caches"),
    os.path.join(HOME, "Library", "Logs"),
]

# Никогда не трогаем (защита)
PROTECTED = [
    os.path.join(HOME, "Library", "Caches", "com.apple"),
]


def now():
    return datetime.now()


def is_protected(path):
    for p in PROTECTED:
        if path.startswith(p):
            return True
    return False


def human_size(num):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def get_old_files(root, age_days, action="report"):
    """Собирает файлы/папки старше age_days. Возвращает (items, total_size)."""
    cutoff = now() - timedelta(days=age_days)
    items = []
    total = 0
    if not os.path.exists(root):
        return items, total
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if not is_protected(os.path.join(dirpath, d))]
        for name in filenames + dirnames:
            fp = os.path.join(dirpath, name)
            try:
                st = os.lstat(fp)
            except OSError:
                continue
            mtime = datetime.fromtimestamp(st.st_mtime)
            if mtime < cutoff:
                size = st.st_size if os.path.isfile(fp) else 0
                total += size
                items.append((fp, size, mtime))
                if action == "clean" and not is_protected(fp):
                    try:
                        if os.path.isfile(fp) or os.path.islink(fp):
                            os.remove(fp)
                        else:
                            shutil.rmtree(fp, ignore_errors=True)
                    except OSError as e:
                        items[-1] = (fp, size, mtime, f"ERR: {e}")
    return items, total


def system_stats():
    stats = {}
    total, used, free = shutil.disk_usage("/")
    stats["disk_total"] = human_size(total)
    stats["disk_used"] = human_size(used)
    stats["disk_free"] = human_size(free)
    stats["disk_used_pct"] = round(used / total * 100, 1)
    try:
        out = subprocess.check_output(["vm_stat"], text=True)
        pages = {}
        for line in out.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                pages[k.strip()] = int("".join(filter(str.isdigit, v)) or 0)
        page = 4096
        free_mb = pages.get("Pages free", 0) * page / 1e6
        active_mb = pages.get("Pages active", 0) * page / 1e6
        stats["mem_free_mb"] = round(free_mb)
        stats["mem_active_mb"] = round(active_mb)
    except Exception as e:
        stats["mem_error"] = str(e)
    try:
        boot = subprocess.check_output(["sysctl", "-n", "kern.boottime"], text=True)
        import re
        m = re.search(r"\d+", boot)
        if m:
            bt = int(m.group())
            up = int(time.time()) - bt
            stats["uptime"] = str(timedelta(seconds=up)).split(".")[0]
    except Exception as e:
        stats["uptime_error"] = str(e)
    return stats


def scan_trash(age_days, action):
    return get_old_files(TRASH, age_days, action)


def scan_caches(age_days, action):
    items = []
    total = 0
    for t in CACHE_TARGETS:
        i, s = get_old_files(t, age_days, action)
        items.extend(i)
        total += s
    return items, total


def run(mode):
    dry = mode == "dry-run"
    action = "report" if dry else "clean"
    lines = []
    lines.append(f"=== Maintenance Agent report — {now().isoformat()} ===")
    lines.append(f"Mode: {'DRY-RUN (no changes)' if dry else 'CLEAN (removing old junk)'}")
    lines.append(f"Age threshold: {AGE_DAYS} days\n")

    lines.append("--- System stats ---")
    st = system_stats()
    for k, v in st.items():
        lines.append(f"  {k}: {v}")
    lines.append("")

    lines.append("--- Trash (.Trash) ---")
    ti, ts = scan_trash(AGE_DAYS, action)
    lines.append(f"  Old items: {len(ti)} | reclaimable: {human_size(ts)}")
    for fp, sz, mt, *rest in ti[:20]:
        err = rest[0] if rest else ""
        lines.append(f"    {mt.date()} {human_size(sz):>10} {fp}{(' '+err) if err else ''}")
    if len(ti) > 20:
        lines.append(f"    ... and {len(ti)-20} more")
    lines.append("")

    lines.append("--- Caches (Library/Caches, Library/Logs) ---")
    ci, cs = scan_caches(AGE_DAYS, action)
    lines.append(f"  Old items: {len(ci)} | reclaimable: {human_size(cs)}")
    for fp, sz, mt, *rest in ci[:20]:
        err = rest[0] if rest else ""
        lines.append(f"    {mt.date()} {human_size(sz):>10} {fp}{(' '+err) if err else ''}")
    if len(ci) > 20:
        lines.append(f"    ... and {len(ci)-20} more")
    lines.append("")

    total_reclaim = ts + cs
    lines.append(f"=== TOTAL reclaimable: {human_size(total_reclaim)} ===")
    if dry:
        lines.append("DRY-RUN complete. Re-run with --clean to actually remove (safe, age-gated).")

    report_text = "\n".join(lines)
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_path = os.path.join(REPORT_DIR, f"report_{now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_path, "w") as f:
        f.write(report_text)
    print(report_text)
    print(f"\nReport saved: {report_path}")
    return report_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintenance Agent for macOS")
    parser.add_argument("--clean", action="store_true", help="Actually remove old junk (age-gated)")
    args = parser.parse_args()
    mode = "clean" if args.clean else "dry-run"
    run(mode)
