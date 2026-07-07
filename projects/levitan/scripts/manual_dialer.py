#!/usr/bin/env python3
"""
Levitan Manual Dialer — Автодозвон + CRM для ручного обзвона.
==============================================================

Запуск: python3 scripts/manual_dialer.py

Функции:
- Загружает базу контактов (фильтр по зерновым/масличным/бобовым)
- Набирает номера через Mango callback (ты говоришь сам)
- Показывает шпаргалку-скрипт
- Фиксирует результат (лид/отказ/перезвон/не взял)
- Сохраняет всё в CSV и JSON

Горячие клавиши:
  Enter — набрать следующий номер
  s — пропустить (skip)
  q — выйти
"""

import csv
import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

# === PATHS ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "campaigns" / "csv" / "all_contacts_2026.csv"
RESULTS_DIR = DATA_DIR / "call_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_CSV = RESULTS_DIR / f"results_{datetime.now().strftime('%Y-%m-%d')}.csv"
RESULTS_JSON = RESULTS_DIR / f"results_{datetime.now().strftime('%Y-%m-%d')}.json"

# === MANGO CONFIG ===
API_KEY = os.getenv("MANGO_VPBX_API_KEY", "") or os.getenv("MANGO_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "") or os.getenv("MANGO_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")

# Загружаем .env если есть
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())
    # Перечитываем после загрузки .env
    API_KEY = os.getenv("MANGO_VPBX_API_KEY", "") or os.getenv("MANGO_API_KEY", "")
    API_SALT = os.getenv("MANGO_VPBX_API_SALT", "") or os.getenv("MANGO_SALT", "")
    MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")

# === ФИЛЬТР КУЛЬТУР ===
TARGET_KEYWORDS = [
    "зерновые", "пшеница", "ячмень", "кукуруза",
    "подсолнечник", "рапс", "соя",
    "горох", "нут", "чечевица",
    "масличные", "бобовые", "озимая", "яровая",
    "зерно", "закупка зерновых",
]

EXCLUDE_KEYWORDS = [
    "крс", "молочный", "мясной", "овцы", "свиньи",
    "птица", "рыба", "овощи", "картофель", "сахарная",
    "хранение", "сооружений", "техника", "ремонт",
    "торговля", "производство молочной", "элеватор",
]


def norm_phone(num: str) -> str:
    """Нормализация номера."""
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d


def is_valid_phone(num: str) -> bool:
    """Проверка валидности номера."""
    n = norm_phone(num)
    return len(n) == 11 and n.startswith("7")


def mango_callback(phone: str) -> dict:
    """Позвонить через Mango callback."""
    command_id = f"manual_{uuid.uuid4().hex[:8]}"
    payload = {
        "command_id": command_id,
        "from": {"extension": MANGO_FROM_EXTENSION},
        "to_number": norm_phone(phone),
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()

    try:
        r = requests.post(
            f"{MANGO_API_BASE}commands/callback",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def load_contacts() -> list[dict]:
    """Загрузить и отфильтровать контакты."""
    contacts = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = (row.get("Описание", "") or "").lower()
            phones = row.get("Телефоны", "") or ""

            # Фильтр: есть целевые культуры
            has_target = any(kw in desc for kw in TARGET_KEYWORDS)
            # Фильтр: нет исключений (или есть зерновые вместе с КРС)
            is_excluded = any(kw in desc for kw in EXCLUDE_KEYWORDS) and not has_target

            if not has_target or is_excluded:
                continue

            # Парсим телефоны
            phone_list = re.findall(r"[\d\-\(\)\+\s]{7,}", phones)
            for phone in phone_list:
                normalized = norm_phone(phone)
                if is_valid_phone(normalized):
                    contacts.append({
                        "name": row.get("Название", "").strip(),
                        "description": row.get("Описание", "").strip(),
                        "region": row.get("Регион", "").strip(),
                        "city": row.get("Город", "").strip(),
                        "contact_name": row.get("Имя", "").strip(),
                        "phone": normalized,
                        "phone_display": phone.strip(),
                    })
                    break  # Один номер на контакт

    return contacts


def load_already_called() -> set:
    """Загрузить уже обзвоненные номера."""
    called = set()
    for f in RESULTS_DIR.glob("results_*.csv"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if row.get("phone"):
                        called.add(row["phone"])
        except Exception:
            pass
    return called


def save_result(result: dict):
    """Сохранить результат звонка."""
    # CSV
    file_exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "phone", "name", "region", "description",
            "status", "interest", "crops", "volume", "notes",
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

    # JSON (append)
    results = []
    if RESULTS_JSON.exists():
        try:
            results = json.loads(RESULTS_JSON.read_text())
        except Exception:
            results = []
    results.append(result)
    RESULTS_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2))


def print_script():
    """Показать шпаргалку."""
    print("\n" + "=" * 60)
    print("  СКРИПТ РАЗГОВОРА — «Глобал Филдс Экспорт»")
    print("=" * 60)
    print("""
┌─────────────────────────────────────────────────────────┐
│ ПРИВЕТСТВИЕ:                                            │
│ «Здравствуйте! Меня зовут Иван, компания               │
│  Глобал Филдс Экспорт. Мы закупаем зерновые,           │
│  масличные и бобовые у сельхозпроизводителей.           │
│  Подскажите, выращиваете что-то из этого на продажу?»   │
├─────────────────────────────────────────────────────────┤
│ ВОПРОСЫ (по одному):                                    │
│  1. Какие культуры выращиваете?                         │
│  2. Какой примерный объём на продажу?                   │
│  3. Какой базис удобен? (CPT/FOB/DAP)                   │
│  4. Когда планируете поставку?                          │
│  5. Как удобнее связаться для расчёта?                  │
├─────────────────────────────────────────────────────────┤
│ БАЗИСЫ:                                                 │
│  CPT — мы забираем с хозяйства/терминала                │
│  FOB — вы привозите в порт                              │
│  DAP — доставка до границы/пункта                       │
├─────────────────────────────────────────────────────────┤
│ ВОЗРАЖЕНИЯ:                                             │
│  «Цена низкая» → Зависит от объёма, рассчитаем         │
│  «Есть покупатель» → Можем быть запасным вариантом      │
│  «Маленький объём» → Работаем с любым, зафиксируем      │
│  «Далеко от порта» → Забираем сами (CPT/DAP)            │
│  «Не продаём» → Ок, зафиксируем на будущее             │
│  «Позвоните позже» → Когда удобно?                      │
├─────────────────────────────────────────────────────────┤
│ ЗАКРЫТИЕ (если интерес):                                │
│ «Отлично, зафиксировал. Менеджер свяжется для           │
│  расчёта цены. Спасибо, до свидания!»                   │
├─────────────────────────────────────────────────────────┤
│ КОНТАКТЫ: +7(918)639-30-30 | info@globalfields.ru       │
└─────────────────────────────────────────────────────────┘
""")


def print_contact(idx: int, total: int, contact: dict):
    """Показать карточку контакта."""
    print(f"\n{'─' * 60}")
    print(f"  [{idx}/{total}] СЛЕДУЮЩИЙ КОНТАКТ")
    print(f"{'─' * 60}")
    print(f"  Название:  {contact['name']}")
    print(f"  Описание:  {contact['description']}")
    print(f"  Регион:    {contact['region']}, {contact['city']}")
    if contact['contact_name']:
        print(f"  Контакт:   {contact['contact_name']}")
    print(f"  Телефон:   {contact['phone_display']} → {contact['phone']}")
    print(f"{'─' * 60}")


def get_call_result(contact: dict) -> dict:
    """Получить результат звонка от пользователя."""
    print("\n  Результат звонка:")
    print("    1 — Лид (заинтересован)")
    print("    2 — Перезвон (просит позже)")
    print("    3 — Отказ (не интересно)")
    print("    4 — Не взял трубку")
    print("    5 — Неверный номер")
    print("    6 — Другое")

    while True:
        choice = input("\n  Статус [1-6]: ").strip()
        if choice in "123456":
            break
        print("  Введите число 1-6")

    status_map = {
        "1": "lead", "2": "callback", "3": "rejected",
        "4": "no_answer", "5": "wrong_number", "6": "other",
    }
    status = status_map[choice]

    # Доп. инфо для лидов
    interest = ""
    crops = ""
    volume = ""
    notes = ""

    if status == "lead":
        crops = input("  Культуры: ").strip()
        volume = input("  Объём: ").strip()
        interest = "high"
    elif status == "callback":
        notes = input("  Когда перезвонить: ").strip()
        interest = "medium"

    notes_extra = input("  Заметки (Enter — пропустить): ").strip()
    if notes_extra:
        notes = f"{notes}; {notes_extra}" if notes else notes_extra

    return {
        "timestamp": datetime.now().isoformat(),
        "phone": contact["phone"],
        "name": contact["name"],
        "region": contact["region"],
        "description": contact["description"],
        "status": status,
        "interest": interest,
        "crops": crops,
        "volume": volume,
        "notes": notes,
    }


def main():
    print("\n" + "=" * 60)
    print("  LEVITAN MANUAL DIALER")
    print("  Автодозвон через Mango + CRM")
    print("=" * 60)

    # Проверка ключей
    if not API_KEY or not API_SALT:
        print("\n  ⚠️  Не заданы MANGO_VPBX_API_KEY / MANGO_VPBX_API_SALT")
        print("  Загрузите .env: source .env или export MANGO_VPBX_API_KEY=...")
        print("  Продолжаю без автодозвона (только CRM-фиксация)")
        use_mango = False
    else:
        use_mango = True
        print(f"\n  ✓ Mango API подключён (ext: {MANGO_FROM_EXTENSION})")

    # Загрузка контактов
    print("\n  Загрузка базы...")
    contacts = load_contacts()
    already_called = load_already_called()

    # Убираем уже обзвоненные
    contacts = [c for c in contacts if c["phone"] not in already_called]

    print(f"  Всего контактов (зерновые/масличные/бобовые): {len(contacts)}")
    print(f"  Уже обзвонено: {len(already_called)}")
    print(f"  Осталось: {len(contacts)}")

    if not contacts:
        print("\n  Все контакты обзвонены!")
        return

    # Выбор региона
    from collections import Counter
    regions = Counter(c["region"] for c in contacts)
    print("\n  Регионы:")
    for i, (region, cnt) in enumerate(regions.most_common(), 1):
        print(f"    {i}. {region} ({cnt})")
    print(f"    0. Все регионы ({len(contacts)})")

    region_choice = input("\n  Выберите регион [0=все]: ").strip()
    if region_choice and region_choice != "0":
        try:
            idx_r = int(region_choice) - 1
            selected_region = regions.most_common()[idx_r][0]
            contacts = [c for c in contacts if c["region"] == selected_region]
            print(f"  Выбран: {selected_region} ({len(contacts)} контактов)")
        except (ValueError, IndexError):
            print("  Все регионы")

    # Показать скрипт
    print_script()

    # Основной цикл
    idx = 0
    stats = {"lead": 0, "callback": 0, "rejected": 0, "no_answer": 0, "wrong_number": 0, "other": 0}

    print("\n  Команды: Enter=звонить | s=пропустить | q=выйти | h=шпаргалка")

    while idx < len(contacts):
        contact = contacts[idx]
        print_contact(idx + 1, len(contacts), contact)

        cmd = input("\n  [Enter=звонить / s=skip / q=quit / h=help]: ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "s":
            idx += 1
            continue
        elif cmd == "h":
            print_script()
            continue
        elif cmd == "":
            # Звоним
            if use_mango:
                print(f"\n  📞 Набираю {contact['phone']}...")
                result = mango_callback(contact["phone"])
                if result.get("result") == 1000:
                    print("  ✓ Callback инициирован. Ожидайте звонка на ваш телефон...")
                else:
                    print(f"  ⚠️  Mango: {result}")
            else:
                print(f"\n  📞 Позвоните вручную: {contact['phone_display']}")

            # Ждём результат
            input("\n  [Нажмите Enter когда разговор завершится]")

            # Фиксируем результат
            call_result = get_call_result(contact)
            save_result(call_result)
            stats[call_result["status"]] += 1

            # Статистика
            total_calls = sum(stats.values())
            print(f"\n  📊 Статистика: {total_calls} звонков | "
                  f"Лиды: {stats['lead']} | "
                  f"Перезвон: {stats['callback']} | "
                  f"Отказ: {stats['rejected']} | "
                  f"Не взял: {stats['no_answer']}")

            if stats['lead'] > 0:
                conv = stats['lead'] / total_calls * 100
                print(f"  Конверсия в лиды: {conv:.1f}%")

            idx += 1
        else:
            print("  Неизвестная команда. Enter/s/q/h")

    # Итог
    total_calls = sum(stats.values())
    print(f"\n{'=' * 60}")
    print(f"  ИТОГ ДНЯ")
    print(f"{'=' * 60}")
    print(f"  Всего звонков: {total_calls}")
    print(f"  Лиды:         {stats['lead']}")
    print(f"  Перезвон:     {stats['callback']}")
    print(f"  Отказ:        {stats['rejected']}")
    print(f"  Не взял:      {stats['no_answer']}")
    print(f"  Неверный №:   {stats['wrong_number']}")
    if total_calls > 0:
        print(f"  Конверсия:    {stats['lead']/total_calls*100:.1f}%")
    print(f"\n  Результаты: {RESULTS_CSV}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
