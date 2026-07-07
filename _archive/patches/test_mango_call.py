#!/usr/bin/env python3
"""
Тест звонка через Mango Office API

Использование:
    python3 test_call.py <from_extension> <to_number> [line_number]
    
Пример:
    python3 test_call.py 100 79991234567 74951234567
"""

import sys
from mango_api import make_call, get_balance

def main():
    print("=== Тест звонка Mango Office ===\n")
    
    # Проверяем баланс
    print("1. Проверка баланса...")
    balance_result = get_balance()
    if balance_result.get('result') == 1000:
        print(f"   Баланс: {balance_result['balance']} {balance_result['currency']}")
    else:
        print(f"   Ошибка получения баланса: {balance_result}")
        return
    
    print()
    
    # Параметры звонка
    if len(sys.argv) >= 3:
        from_extension = sys.argv[1]
        to_number = sys.argv[2]
        line_number = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # Тестовые значения - замените на свои
        print("Введите параметры звонка:")
        from_extension = input("   Внутренний номер сотрудника (from): ").strip()
        to_number = input("   Номер телефона клиента (to): ").strip()
        line_number = input("   Входящая линия (line_number, необязательно): ").strip() or None
    
    print(f"\n2. Инициация звонка:")
    print(f"   От сотрудника: {from_extension}")
    print(f"   Клиент: {to_number}")
    if line_number:
        print(f"   Линия: {line_number}")
    
    try:
        result = make_call(
            from_extension=from_extension,
            to_number=to_number,
            line_number=line_number
        )
        
        print(f"\n3. Результат:")
        print(f"   {result}")
        
        if result.get('result') == 1000:
            print("\n✅ Звонок успешно инициирован!")
        else:
            print(f"\n❌ Ошибка: {result.get('result')}")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == '__main__':
    main()
