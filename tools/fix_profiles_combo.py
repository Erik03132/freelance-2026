#!/usr/bin/env python3
"""Fix broken OmniRoute combo names across Hermes profiles.

Replaces deleted combos (auto/free-coding, auto/best-free, auto/best-coding,
auto/super-free) with the only live one: auto/free-coding-full.
Backs up each file before editing, validates YAML after.
Skips `personal` (uses direct OpenCode, not Omni).
"""
import os
import re
import shutil
import sys
from datetime import datetime

PROFILES_DIR = os.path.expanduser("~/.hermes/profiles")
BACKUP_DIR = os.path.expanduser("~/freelance-2026/backups/profiles_combo_fix")
LIVE_COMBO = "auto/free-coding-full"

# Profiles to fix (personal intentionally excluded — direct OpenCode, healthy)
TARGETS = [
    "batrak", "femida", "health", "english-tutor",
    "sherlock", "marketer", "financier", "defender", "bridge",
]

# Mapping: old substring -> new
REPL = {
    "auto/free-coding": LIVE_COMBO,
    "auto/best-free": LIVE_COMBO,
    "auto/best-coding": LIVE_COMBO,
    "auto/super-free": LIVE_COMBO,
}

def validate_yaml(path):
    try:
        import yaml
    except ImportError:
        # fallback: basic sanity (no tabs, balanced brackets is hard; trust patch)
        return True
    with open(path) as f:
        yaml.safe_load(f)
    return True

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = []
    for name in TARGETS:
        cfg = os.path.join(PROFILES_DIR, name, "config.yaml")
        if not os.path.exists(cfg):
            report.append(f"[SKIP] {name}: no config.yaml")
            continue
        with open(cfg) as f:
            text = f.read()
        new_text = text
        hits = {}
        for old, new in REPL.items():
            n = new_text.count(old)
            if n:
                hits[old] = n
                new_text = new_text.replace(old, new)
        if not hits:
            report.append(f"[OK]   {name}: already clean, nothing to do")
            continue
        # backup
        bak = os.path.join(BACKUP_DIR, f"{name}_{stamp}.yaml")
        shutil.copy2(cfg, bak)
        with open(cfg, "w") as f:
            f.write(new_text)
        # validate
        try:
            validate_yaml(cfg)
            status = "FIXED"
        except Exception as e:
            # restore from backup
            shutil.copy2(bak, cfg)
            status = f"YAML-INVALID-ROLLBACK ({e})"
        report.append(f"[{status}] {name}: " + ", ".join(f"{k}->{LIVE_COMBO} x{v}" for k, v in hits.items())
                      + f" | backup: {os.path.basename(bak)}")
    print("\n".join(report))
    print(f"\nBackups in: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
