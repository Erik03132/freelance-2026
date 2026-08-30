# OmniRoute Provider Configuration Details

## Configuration Keys

### Root Level Keys

| Ключ | Значение | Описание |
|------|----------|----------|
| `model.provider` | `omniroute` | Активный провайдер |
| `model.default` | `auto/best-coding` | Дефолтная модель |
| `model.base_url` | `http://127.0.0.1:20128/v1` | URL эндпоинта |
| `model.key_env` | `OMNI_API_KEY` | Переменная окружения с ключом |

### Provider-Specific Keys

```yaml
providers.omniroute.name: "OmniRoute (OpenCode Zen + OpenRouter + Orca)"
providers.omniroute.base_url: http://127.0.0.1:20128/v1
providers.omniroute.key_env: OMNI_API_KEY
providers.omniroute.discover_models: true
providers.omniroute.models.auto/free-coding.name: "🆓 Free Coding (combo: OC Zen + OR + Orca)"
providers.omniroute.models.auto/best-coding.name: 🏆 Best Coding
```

## Common CLI Commands

```bash
# Проверить текущий провайдер
hermes config get model.provider

# Проверить дефолтную модель
hermes config get model.default

# Установить провайдер
hermes config set model.provider omniroute

# Установить модель
hermes config set model.default "auto/best-coding"

# Установить base URL
hermes config set model.base_url "http://127.0.0.1:20128/v1"

# Установить переменную окружения для ключа
hermes config set model.key_env OMNI_API_KEY
```

## Verification Script

Создайте скрипт для проверки конфигурации:

```bash
#!/bin/bash
echo "=== OmniRoute Provider Verification ==="
echo "Provider: $(hermes config get model.provider)"
echo "Default model: $(hermes config get model.default)"
echo "Base URL: $(hermes config get model.base_url)"
echo "Key env: $(hermes config get model.key_env)"
echo ""
echo "Provider config:"
grep -A 10 "^providers:" ~/.hermes/config.yaml | grep -A 10 omniroute
```

## Migration History

### Откуда берёмся

1. Изначальная конфигурация имела несколько провайдеров (nous, openrouter, anthropic и др.)
2. Провайдер `nous` был основным, но не все модели работали
3. Решение: оставить только OmniRoute как единственный провайдер

### Изменённые файлы

- `~/.hermes/config.yaml` — удалены неиспользуемые провайдеры, оставлен только omniroute