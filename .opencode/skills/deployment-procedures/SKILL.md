# Deployment Procedures & Server Management

## Стратегии деплоя
| Стратегия | Когда использовать | Плюсы | Минусы |
|-----------|-------------------|-------|--------|
| **Rolling** | Стандартные обновления | Zero downtime | Две версии одновременно |
| **Blue-Green** | Критичные сервисы | Instant rollback | 2x инфраструктура |
| **Canary** | Рисковые изменения | Ловит баги | Нужен traffic splitting |

## Production Readiness Checklist

### Application
- [ ] Все тесты проходят
- [ ] Нет hardcoded секретов
- [ ] Error handling покрывает edge cases
- [ ] Health check endpoint возвращает осмысленный статус

### Infrastructure (Node/PM2/Python)
- [ ] Сборка с зафиксированными (pinned) версиями пакетов.
- [ ] Env переменные валидируются при старте.
- [ ] Установлены ограничения ресурсов (CPU, memory).
- [ ] SSL/TLS включён.

## Rollback Strategy (PM2)
```bash
# PM2: откат к предыдущей версии
pm2 deploy previous

# Git:
git revert HEAD && git push
```

## Security Checklist
- Вынеси `API_KEY` в окружение, никогда не храни в репозитории.
- Настрой `Rate Limiting` на API.
- Настрой мониторинг падений и процессов (pm2 monit).
