#!/usr/bin/env python3
"""validate_profiles.py — SSoT-валидатор воркспейс-профилей Hermes.

Проверяет, что каждый профиль в ~/.hermes/profiles/<name>/config.yaml
соответствует каноническому шаблону (см. docs/PROFILES.md):
  - model.provider == omniroute
  - model.default == auto/free-coding-full
  - model.base_url == http://127.0.0.1:20128/v1
  - aliases.best-coding / free-coding == omniroute/auto/free-coding-full
  - ровно одна запись auto/free-coding-full в models
  - есть SOUL.md (чтобы агент знал, кто он)

Exit code 0 = все профили валидны, 1 = есть нарушения.
"""
import sys
from pathlib import Path

PROFILES = Path.home() / ".hermes" / "profiles"
EXPECT_BASE = "http://127.0.0.1:20128/v1"
EXPECT_DEFAULT = "auto/free-coding-full"
EXPECT_ALIAS = "omniroute/auto/free-coding-full"


def check_profile(p: Path):
    cfg = p / "config.yaml"
    errors = []
    if not cfg.exists():
        return ["config.yaml отсутствует"]
    text = cfg.read_text(errors="replace")
    lines = text.splitlines()

    def val(key):
        for i, l in enumerate(lines):
            if l.strip().startswith(f"{key}:"):
                # либо "key: value" на той же строке, либо следующая непустая
                rest = l.split(":", 1)[1].strip()
                if rest:
                    return rest
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() and not lines[j].startswith(" " * 4):
                        return lines[j].split(":", 1)[1].strip()
        return None

    prov = val("provider")
    if prov != "omniroute":
        errors.append(f"model.provider != omniroute (={prov})")

    default = val("default")
    if default != EXPECT_DEFAULT:
        errors.append(f"model.default != {EXPECT_DEFAULT} (={default})")

    base = val("base_url")
    if base != EXPECT_BASE:
        errors.append(f"model.base_url != {EXPECT_BASE} (={base})")

    # aliases
    alias_best = None
    alias_free = None
    in_aliases = False
    for l in lines:
        s = l.strip()
        if s == "aliases:":
            in_aliases = True
            continue
        if in_aliases:
            if s.startswith("best-coding:"):
                alias_best = s.split(":", 1)[1].strip()
            elif s.startswith("free-coding:"):
                alias_free = s.split(":", 1)[1].strip()
            elif s and not s.startswith(" ") and ":" in s and not s.startswith("best-coding") and not s.startswith("free-coding"):
                # вышли из блока aliases
                if not (s.startswith("provider") or s.startswith("key_env") or s.startswith("base_url")):
                    in_aliases = False
    if alias_best != EXPECT_ALIAS:
        errors.append(f"aliases.best-coding != {EXPECT_ALIAS} (={alias_best})")
    if alias_free != EXPECT_ALIAS:
        errors.append(f"aliases.free-coding != {EXPECT_ALIAS} (={alias_free})")

    # дубликаты auto/free-coding-full в models
    fcf_count = sum(1 for l in lines if l.strip() == "auto/free-coding-full:")
    if fcf_count != 1:
        errors.append(f"записей 'auto/free-coding-full:' = {fcf_count} (должно быть 1)")

    # SOUL.md
    if not (p / "SOUL.md").exists():
        errors.append("SOUL.md отсутствует (агент не знает, кто он)")

    return errors


def main():
    if not PROFILES.exists():
        print(f"Нет каталога профилей: {PROFILES}")
        sys.exit(1)
    profiles = sorted([d for d in PROFILES.iterdir() if d.is_dir()])
    total = 0
    bad = 0
    print(f"{'ПРОФИЛЬ':14} {'СТАТУС':8} ДЕТАЛИ")
    print("-" * 70)
    for p in profiles:
        errs = check_profile(p)
        total += 1
        if errs:
            bad += 1
            print(f"{p.name:14} ❌      " + "; ".join(errs))
        else:
            print(f"{p.name:14} ✅")
    print("-" * 70)
    print(f"Всего: {total}, валидно: {total - bad}, нарушений: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
