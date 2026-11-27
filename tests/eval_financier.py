"""FCA-1 — eval сценариев Финансиста из FCA AI Spotlight Observatory (27.11.2026).

Офлайн, детерминированный, только stdlib. Сценарии привязаны к публичным кейсам
FCA (FUCxxx); числа синтетические — это проверка логики, не рыночные данные.
Источник: https://ai-spotlight.fcainnovation.co.uk/ (FCA, 19.11.2026).

Запуск: python3 tests/eval_financier.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financier-unit-economics" / "SKILL.md"
SOUL = Path.home() / ".hermes" / "profiles" / "financier" / "SOUL.md"

# Guardrail №4 скилла: LTV без когорт не экстраполируется бесконечно.
HORIZON_CAP = 36

# Таксономия тем из FCA AI Spotlight participation pack.
FCA_THEMES = {
    "bias-fairness",
    "explainability-governance",
    "data-quality",
    "compliance-automation",
}


@dataclass(frozen=True)
class Case:
    fid: str
    theme: str
    arpu: float
    margin: float
    cac: float
    churn: float
    verdict: str


# 6 кейсов FCA + 2 отдельные проверки гардрейлов ниже = 8 сценариев.
CASES = (
    Case("FUC043", "explainability-governance", 1000, 0.60, 3000, 0.05, "Scale"),
    Case("FUC023", "data-quality", 500, 0.80, 500, 0.10, "Aggressive scale"),
    Case("FUC011", "bias-fairness", 1000, 0.50, 4000, 0.05, "Optimize"),
    Case("FUC059", "compliance-automation", 1000, 0.60, 8000, 0.05, "Caution"),
    Case("FUC019", "explainability-governance", 1000, 0.50, 10000, 0.10, "Stop"),
    Case("FUC044", "data-quality", 1000, 0.50, 3000, 0.0, "Scale"),
)


def lifetime_months(churn: float) -> float:
    """0% churn не даёт бесконечный lifetime — режем на консервативном горизонте."""
    if churn <= 0:
        return HORIZON_CAP
    return min(1.0 / churn, HORIZON_CAP)


def ltv(arpu: float, margin: float, churn: float) -> float:
    return arpu * margin * lifetime_months(churn)


def payback_months(cac: float, arpu: float, margin: float) -> float:
    return cac / (arpu * margin)


def margin_floor_ok(margin: float, kind: str = "saas") -> bool:
    """Гардрейл №8: пол маржи ≥60% для SaaS, ≥40% для e-commerce."""
    return margin >= (0.60 if kind == "saas" else 0.40)


def verdict(ratio: float, payback: float) -> str:
    """Decision framework скилла + гардрейл №5: длинный payback бьёт высокий ratio."""
    if ratio < 1:
        return "Stop"
    if payback > 18:
        return "Caution"
    if ratio < 2:
        return "Caution"
    if ratio < 3:
        return "Optimize"
    if ratio > 5 and payback < 6:
        return "Aggressive scale"
    if ratio >= 3:
        return "Scale"
    return "Optimize"


def _run() -> list[str]:
    fails: list[str] = []

    # Сценарии привязаны к реальным кейсам FCA и их темам.
    ids = [c.fid for c in CASES]
    if len(ids) != len(set(ids)):
        fails.append("дубли FUC-id в сценариях")
    for c in CASES:
        if c.theme not in FCA_THEMES:
            fails.append(f"{c.fid}: неизвестная тема {c.theme!r}")

    # Метрики и вердикт по формулам скилла.
    for c in CASES:
        value = ltv(c.arpu, c.margin, c.churn)
        ratio = value / c.cac
        payback = payback_months(c.cac, c.arpu, c.margin)
        got = verdict(ratio, payback)
        if got != c.verdict:
            fails.append(
                f"{c.fid}: verdict {got!r}, ожидался {c.verdict!r} "
                f"(ratio={ratio:.2f}, payback={payback:.2f})"
            )
        if not (0 < value < float("inf")):
            fails.append(f"{c.fid}: некорректный LTV {value}")

    # Гардрейл №5: высокий LTV/CAC при payback >18 мес — не масштабировать.
    if verdict(5.5, 20) != "Caution":
        fails.append("длинный payback не перебивает высокий LTV/CAC")

    # Гардрейл №1/№2: CAC и маржа считаются по полным затратам, а не «из головы».
    if payback_months(1200, 1000, 0.5) != 2.4:
        fails.append("неверный payback: 1200/(1000*0.5) должен быть 2.4")
    if ltv(1000, 0.5, 0.1) != 5000:
        fails.append("неверный LTV: 1000*0.5*10 должен быть 5000")

    # Гардрейл пола маржи: 45% — плохо для SaaS, но норма для e-commerce.
    if margin_floor_ok(0.45, "saas") or not margin_floor_ok(0.45, "ecommerce"):
        fails.append("пол маржи 60%/40% работает неверно")

    # Контракт промпта: если формулы/пороги в SKILL.md поправят — ловим регресс.
    if SKILL.exists():
        text = SKILL.read_text(encoding="utf-8")
        required = (
            "LTV/CAC Ratio = Lifetime Value ÷ Customer Acquisition Cost",
            "Payback Period (months) = CAC ÷ (Monthly Revenue × Gross Margin %)",
            "≥3:1",
            "Fully-loaded CAC",
            "Cohort-based LTV",
            "Правовая граница (FCA-2",
            "human-gate",
        )
        for fragment in required:
            if fragment not in text:
                fails.append(f"SKILL.md: пропал фрагмент {fragment!r}")
    else:
        fails.append(f"нет файла скилла: {SKILL}")

    # Граница FCA-2 должна дойти до живого промпта Hermes-профиля.
    if SOUL.exists():
        soul = SOUL.read_text(encoding="utf-8")
        for fragment in ("внутренние расчёты", "human-gate", "FCA AI Spotlight"):
            if fragment not in soul:
                fails.append(f"SOUL.md: пропал фрагмент {fragment!r}")
    else:
        fails.append(f"нет файла промпта: {SOUL}")

    return fails


def _main() -> int:
    fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({len(fails)}):")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(
        f"✅ EVAL PASSED — FCA-1/2 Финансист: {len(CASES)} сценариев FCA "
        "+ 2 гардрейла + контракт промпта и границы FCA-2"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
