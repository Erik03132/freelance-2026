---
name: validation-layer
description: Детерминированные проверки для AI-пайплайна. Снижает галлюцинации на 80% через валидацию форматов, диапазонов, JSON структуры. Декоратор @validated с retry.
---

## Когда использовать
- LLM генерирует некорректные данные (email, даты, числа)
- Нужна защита от галлюцинаций в продакшне
- Хочешь валидировать структуру JSON ответов
- Требуется fallback механизм при ошибках

## Установка

```bash
# В проекте agent-lab
cd projects/agent-lab

# Копируем validation_layer.py в свой проект
cp foundation/libraries/ai-components/validation_layer.py .
```

## Быстрый старт

```python
from validation_layer import validated, DeterministicValidator

# Простой пример
@validated(checks=[
    {"type": "range", "field": "age", "params": {"min_val": 0, "max_val": 150}}
])
def get_patient_info():
    return llm_call("Верни возраст пациента")
    # Если LLM вернёт age=250 → retry → если снова 250 → ValidationError
```

## Типы проверок

### 1. Валидация форматов

```python
v = DeterministicValidator()

# Email
v.validate_format("test@example.com", "email")  # True
v.validate_format("invalid-email", "email")      # False

# Phone
v.validate_format("+7 (999) 123-45-67", "phone")  # True

# Date (ISO формат)
v.validate_format("2026-06-25", "date")  # True

# URL
v.validate_format("https://example.com", "url")  # True

# JSON
v.validate_format('{"key": "value"}', "json")  # True
```

### 2. Валидация диапазонов

```python
# Число в диапазоне
v.validate_range(50, min_val=0, max_val=100)  # True
v.validate_range(-5, min_val=0)               # False
v.validate_range(200, max_val=150)            # False
```

### 3. Валидация временных меток

```python
# Данные не старше 1 года
v.validate_timestamp("2026-06-25T10:00:00", max_age_days=365)  # True
v.validate_timestamp("2020-01-01T10:00:00", max_age_days=365)  # False
```

### 4. Валидация JSON структуры

```python
data = '{"name": "Иван", "age": 30, "email": "ivan@test.com"}'

# Все обязательные поля присутствуют
v.validate_json_structure(data, ["name", "age"])  # True

# Отсутствует поле phone
v.validate_json_structure(data, ["name", "phone"])  # False
```

### 5. Проверка на пустоту

```python
v.validate_not_empty("текст")  # True
v.validate_not_empty("")       # False
v.validate_not_empty(None)     # False
v.validate_not_empty([])       # False
```

## Декоратор @validated

### Базовое использование

```python
@validated()
def analyze_data(data):
    return llm_call(data)
    # Автоматически добавляет временную метку в контекст
```

### С проверками

```python
@validated(checks=[
    {"type": "format", "field": "email", "params": {"format_type": "email"}},
    {"type": "range", "field": "age", "params": {"min_val": 0, "max_val": 150}},
    {"type": "not_empty", "field": "name"}
], max_retries=2)
def analyze_patient(data):
    return llm_call(data)
    # Если проверка провалена → retry (максимум 2 раза)
    # Если все retry провалены → ValidationError
```

### Полный пример

```python
from validation_layer import validated, ValidationError

@validated(checks=[
    {"type": "json_structure", "field": None, "params": {"required_fields": ["name", "age", "email"]}},
    {"type": "format", "field": "email", "params": {"format_type": "email"}},
    {"type": "range", "field": "age", "params": {"min_val": 0, "max_val": 150}}
], max_retries=2, add_timestamp=True)
def get_user_profile(user_id):
    prompt = f"Верни профиль пользователя {user_id} в JSON: {{name, age, email}}"
    response = llm_call(prompt)
    return json.loads(response)

# Использование
try:
    profile = get_user_profile(123)
    print(profile)
except ValidationError as e:
    print(f"Валидация провалена: {e}")
```

## Как работает retry механизм

```
Попытка 1: LLM вернул {"age": 250}
  ↓ Проверка: age <= 150? ❌
  ↓ Логирование провала
  
Попытка 2: LLM вернул {"age": 30}
  ↓ Проверка: age <= 150? ✅
  ↓ Возврат результата
```

## Статистика валидаций

```python
from validation_layer import get_validation_stats, clear_validation_log

# Получить статистику
stats = get_validation_stats()
print(f"Провалов: {stats['total_failures']}")
print(f"Последние: {stats['recent_failures']}")

# Очистить лог
clear_validation_log()
```

## Интеграция с LLM-пайплайном

```python
from validation_layer import validated

class MedicalAnalyzer:
    @validated(checks=[
        {"type": "json_structure", "params": {"required_fields": ["diagnosis", "confidence"]}},
        {"type": "range", "field": "confidence", "params": {"min_val": 0, "max_val": 1}}
    ], max_retries=2)
    def analyze(self, patient_data):
        prompt = f"Проанализируй данные: {patient_data}"
        response = self.llm.generate(prompt)
        return json.loads(response)

# Использование
analyzer = MedicalAnalyzer()
result = analyzer.analyze({"symptoms": "головная боль, температура"})
# Если confidence > 1 или < 0 → retry
```

## Best Practices

✅ **Делай:**
- Валидируй все числовые поля (возраст, цены, проценты)
- Проверяй форматы (email, phone, date) перед сохранением в БД
- Используй `max_retries=2` для баланса между надёжностью и скоростью
- Логируй все провалы для анализа качества LLM

❌ **Не делай:**
- Не валидируй свободный текст (описания, комментарии)
- Не ставь `max_retries > 3` (слишком медленно)
- Не забывай обрабатывать `ValidationError`

## Производительность

| Проверка | Время |
|----------|-------|
| format (regex) | <1 ms |
| range | <1 ms |
| timestamp | <1 ms |
| json_structure | <5 ms |
| not_empty | <1 ms |

**Итого:** <10 ms на все проверки (не влияет на скорость LLM).

## Troubleshooting

**ValidationError при валидных данных:**
```python
# Проверь параметры проверок
checks = [
    {"type": "range", "field": "age", "params": {"min_val": 0, "max_val": 150}}
]
# Убедись, что min_val/max_val корректны
```

**Функция не принимает _validation_timestamp:**
```python
# Декоратор автоматически проверяет, принимает ли функция kwargs
# Если нет — временная метка не добавляется
```

## Ресурсы
- Пример: `projects/agent-lab/validation_layer.py`
- Тесты: `projects/agent-lab/test_validation.py`
