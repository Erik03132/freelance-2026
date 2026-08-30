"""Eval for ND-1 — Needle 2 structured extraction (cactus-compute/needle) — stdlib + pydantic.

Запуск: python3 tools/tests/eval_needle_extraction.py
Гейт-срез ND-1: invoice, contact, order, RU/EN. Критерий: >=80% полей точны.
Модель локальная, веса ~14MB (кешируются после первого прогона).
"""

from __future__ import annotations

import sys

from pydantic import BaseModel


class Invoice(BaseModel):
    vendor: str
    total: float
    due_date: str


class Contact(BaseModel):
    name: str
    email: str
    phone: str


class OrderStatus(BaseModel):
    order_id: int
    status: str


CASES: list[tuple[type[BaseModel], str, dict]] = [
    (
        Invoice,
        "Invoice from Acme Corp, $1,200.00, due 2026-09-01",
        {"vendor": "Acme Corp", "total": 1200.0, "due_date": "2026-09-01"},
    ),
    (
        Invoice,
        "Счёт от ООО «Ромашка» на 45 500 руб., оплатить до 15.10.2026",
        {"vendor": "Ромашка", "total": 45500.0, "due_date": "15.10.2026"},
    ),
    (
        Contact,
        "Reach John Doe at john.doe@example.com or +7 912 345-67-89",
        {"name": "John Doe", "email": "john.doe@example.com", "phone": "+7 912 345-67-89"},
    ),
    (
        Contact,
        "Менеджер Иванова Мария, почта m.ivanova@mail.ru, тел 8-921-100-20-30",
        {"name": "Иванова Мария", "email": "m.ivanova@mail.ru", "phone": "8-921-100-20-30"},
    ),
    (
        OrderStatus,
        "Mark order 305 as fulfilled",
        {"order_id": 305, "status": "fulfilled"},
    ),
    (
        OrderStatus,
        "Заказ 12 перевести в статус pending",
        {"order_id": 12, "status": "pending"},
    ),
]


def _normalize(v: str) -> str:
    v = v.strip().lower().replace(",", ".").replace("ё", "е")
    while "  " in v:
        v = v.replace("  ", " ")
    return v


PASS_THRESHOLD = 80.0


def _run() -> tuple[int, list[str]]:
    import needle  # локально: веса тянутся при первом вызове

    fails: list[str] = []
    passed_fields = 0
    total_fields = 0
    for schema, text, expected in CASES:
        total_fields += len(expected)
        try:
            data = needle.extract(text, schema).model_dump()
        except Exception as exc:
            fails.append(f"ND-{schema.__name__} '{text[:28]}…': exception {exc}")
            continue
        for field, want in expected.items():
            got_v = data.get(field)
            if isinstance(want, float):
                ok = isinstance(got_v, (int, float)) and abs(float(got_v) - want) <= 0.01
            else:
                ok = _normalize(str(got_v)) == _normalize(str(want))
            passed_fields += int(ok)
            if not ok:
                fails.append(
                    f"ND-{schema.__name__}.{field} '…{text[-22:]}': ждали {want!r}, получили {got_v!r}"
                )

    accuracy = passed_fields / total_fields * 100 if total_fields else 0.0
    print(f"ND-1 extraction: {passed_fields}/{total_fields} полей точны ({accuracy:.0f}%)")
    if accuracy < PASS_THRESHOLD and not fails:
        fails.append(f"ND-1: точность {accuracy:.0f}% < порога {PASS_THRESHOLD:.0f}%")
    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — ND-1 Needle 2 structured extraction OK (invoice/contact/order, RU/EN)")
