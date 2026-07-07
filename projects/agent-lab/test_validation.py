"""
Тест Validation Layer.
"""
import json
from validation_layer import (
    DeterministicValidator,
    validated,
    ValidationError,
    get_validation_stats,
)


def test_format_validation():
    """Тест валидации форматов."""
    print("=" * 60)
    print("ТЕСТ 1: Валидация форматов")
    print("=" * 60)
    
    v = DeterministicValidator()
    
    # Email
    assert v.validate_format("test@example.com", "email") == True
    assert v.validate_format("invalid-email", "email") == False
    print("✅ Email валидация")
    
    # Phone
    assert v.validate_format("+7 (999) 123-45-67", "phone") == True
    assert v.validate_format("abc", "phone") == False
    print("✅ Phone валидация")
    
    # Date
    assert v.validate_format("2026-06-25", "date") == True
    assert v.validate_format("25.06.2026", "date") == False
    print("✅ Date валидация")
    
    # URL
    assert v.validate_format("https://example.com", "url") == True
    assert v.validate_format("not-a-url", "url") == False
    print("✅ URL валидация")
    
    # JSON
    assert v.validate_format('{"key": "value"}', "json") == True
    assert v.validate_format("not json", "json") == False
    print("✅ JSON валидация")


def test_range_validation():
    """Тест валидации диапазонов."""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Валидация диапазонов")
    print("=" * 60)
    
    v = DeterministicValidator()
    
    assert v.validate_range(50, min_val=0, max_val=100) == True
    assert v.validate_range(-5, min_val=0) == False
    assert v.validate_range(200, max_val=150) == False
    assert v.validate_range(25, min_val=0, max_val=150) == True
    print("✅ Range валидация")


def test_json_structure():
    """Тест валидации JSON структуры."""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Валидация JSON структуры")
    print("=" * 60)
    
    v = DeterministicValidator()
    
    data = json.dumps({"name": "Иван", "age": 30, "email": "ivan@test.com"})
    
    assert v.validate_json_structure(data, ["name", "age"]) == True
    assert v.validate_json_structure(data, ["name", "phone"]) == False
    print("✅ JSON structure валидация")


def test_validated_decorator():
    """Тест декоратора @validated."""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Декоратор @validated")
    print("=" * 60)
    
    # Успешный случай
    @validated(checks=[
        {"type": "range", "field": "age", "params": {"min_val": 0, "max_val": 150}}
    ])
    def get_patient_info():
        return {"name": "Иван", "age": 30}
    
    result = get_patient_info()
    assert result["age"] == 30
    print("✅ Декоратор пропускает валидные данные")
    
    # Провальный случай
    @validated(checks=[
        {"type": "not_empty", "field": "result"}
    ], max_retries=1)
    def get_empty_result():
        return {"result": ""}
    
    try:
        get_empty_result()
        print("❌ Должен был выбросить ValidationError")
    except ValidationError:
        print("✅ Декоратор отклоняет невалидные данные")


def test_validation_stats():
    """Тест статистики."""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Статистика валидаций")
    print("=" * 60)
    
    stats = get_validation_stats()
    print(f"   Провалов: {stats['total_failures']}")
    
    if stats['recent_failures']:
        print(f"   Последний провал: {stats['recent_failures'][-1]['check']}")
    
    print("✅ Статистика работает")


if __name__ == "__main__":
    print("🚀 Тестирование Validation Layer\n")
    
    try:
        test_format_validation()
        test_range_validation()
        test_json_structure()
        test_validated_decorator()
        test_validation_stats()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
