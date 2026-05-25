# Деплой и инфраструктура AI Bureau

## Production Readiness Checklist

### Application
- Все тесты проходят
- Нет hardcoded секретов (только env vars)
- Error handling покрывает edge cases
- Health check endpoint возвращает осмысленный статус

### Infrastructure
- Сборка с зафиксированными (pinned) версиями пакетов
- Env переменные валидируются при старте
- Установлены ограничения ресурсов (CPU, memory)
- SSL/TLS включён

## Стратегии деплоя
| Стратегия | Когда | Плюсы | Минусы |
|-----------|-------|-------|--------|
| **Rolling** | Стандартные обновления | Zero downtime | Две версии одновременно |
| **Blue-Green** | Критичные сервисы | Instant rollback | 2x инфраструктура |
| **Canary** | Рисковые изменения | Ловит баги | Нужен traffic splitting |

## PM2 (Node.js проекты)
```bash
pm2 start server.js --name ai-bureau
pm2 save
pm2 startup
pm2 logs ai-bureau
pm2 deploy previous  # откат
```

## Docker
- Pinned версии в Dockerfile
- Multi-stage builds для уменьшения образа
- Health check в Dockerfile
- Не запускать от root

## Security Checklist
- API ключи только в environment variables
- Rate Limiting на API эндпоинтах
- Мониторинг падений процессов
- IP whitelist где возможно
- HTTPS через Let's Encrypt

## Rollback Strategy
```bash
# PM2
pm2 deploy previous

# Git
git revert HEAD && git push
```

## Scout — поиск новых инструментов (правило Кулибина)
Перед внедрением новой библиотеки:
1. Размер бандла не должен расти > 20%
2. Проверить количество зависимостей
3. Proof-of-concept в изолированном скрипте
4. Backward compatibility обязательна
