#!/usr/bin/env python3
"""
Mango Office Virtual PBX API Client
https://app.mango-office.ru/vpbx/

Документация: MangoOffice_VPBX_API_v1.9.pdf
"""

import hashlib
import json
import uuid
import requests

# Конфигурация
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
VPBX_API_KEY = "a0e6fwgqmjrm6g4qp1zt6ps1sx62ey6f"  # Уникальный код ВАТС
VPBX_API_SALT = "pabuxia9ssloyg5d8ux49fws2sl7hhdw"  # Ключ для создания подписи


def generate_signature(json_data: dict, api_key: str = VPBX_API_KEY, salt: str = VPBX_API_SALT) -> str:
    """
    Генерация подписи для запроса.
    
    Формула: sign = sha256(vpbx_api_key + json + vpbx_api_salt)
    
    JSON формируется без пробелов и переносов строк.
    """
    json_string = json.dumps(json_data, separators=(',', ':'), ensure_ascii=False)
    sign_string = api_key + json_string + salt
    signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()
    return signature


def make_request(endpoint: str, json_data: dict) -> dict:
    """
    Выполнение API запроса к Mango Office.
    
    POST запрос с JSON телом и подписью.
    """
    url = f"{MANGO_API_BASE}{endpoint}"
    
    # Формируем тело запроса
    payload = {
        'vpbx_api_key': VPBX_API_KEY,
        'json': json.dumps(json_data, separators=(',', ':'), ensure_ascii=False),
        'sign': generate_signature(json_data)
    }
    
    print(f"POST {url}")
    print(f"Payload: {payload}")
    
    # Выполняем POST запрос
    response = requests.post(url, data=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    response.raise_for_status()
    
    result = response.json()

    # result: 1000 = успех, 3xxx/4xxx/5xxx = ошибка
    if result.get('result') not in (0, 1000, None):
        print(f"API Error: {result}")

    return result


def get_users() -> dict:
    """
    Получить список сотрудников (внутренних номеров).
    
    Метод: /users/request
    """
    json_data = {
        "show_users": 1
    }
    return make_request('users/request', json_data)


def make_call(from_extension: str, to_number: str, line_number: str = None, customer_number: str = None) -> dict:
    """
    Инициировать исходящий вызов (callback).
    
    from_extension: внутренний номер сотрудника, от имени которого звоним
    to_number: номер, куда звоним (клиент)
    line_number: входящая линия ВАТС для вызова (опционально)
    customer_number: номер клиента для отображения (опционально)
    """
    command_id = f"cmd_{uuid.uuid4().hex[:8]}"
    
    json_data = {
        "command_id": command_id,
        "from": {
            "extension": from_extension
        },
        "to_number": to_number
    }
    
    if line_number:
        json_data["line_number"] = line_number
    
    if customer_number:
        json_data["customer_number"] = customer_number
    
    return make_request('commands/callback', json_data)


def get_balance() -> dict:
    """
    Получить баланс лицевого счета ВАТС.
    
    Метод: /account/balance
    """
    json_data = {}
    return make_request('account/balance', json_data)


if __name__ == '__main__':
    # Тест: получаем баланс
    print("=== Mango Office API Test ===\n")
    
    print("1. Получаем баланс...")
    try:
        balance = get_balance()
        print(f"Результат: {balance}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n2. Получаем список внутренних номеров...")
    try:
        users = get_users()
        print(f"Результат: {users}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n=== Готово ===")
