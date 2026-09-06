"""Утилиты для обработки данных."""

import re


def normalize_phone(phone: str) -> str:
    """
    Нормализация номера телефона к формату 7XXXXXXXXXX.

    Поддерживаемые форматы:
    - +7XXXXXXXXXX
    - 8XXXXXXXXXX
    - 7XXXXXXXXXX
    - +7 (XXX) XXX-XX-XX
    - 8-XXX-XXX-XX-XX
    - +7 XXX XXX XX XX

    Args:
        phone: Номер телефона в любом формате

    Returns:
        Номер в формате 7XXXXXXXXXX или пустая строка если не удалось распарсить
    """
    if not phone:
        return ""

    cleaned = re.sub(r"[^\d]", "", phone)

    if len(cleaned) == 11 and cleaned.startswith("8"):
        return "7" + cleaned[1:]
    elif len(cleaned) == 11 and cleaned.startswith("7"):
        return cleaned
    elif len(cleaned) == 10:
        return "7" + cleaned
    elif len(cleaned) == 12 and cleaned.startswith("7"):
        return cleaned
    else:
        return ""
