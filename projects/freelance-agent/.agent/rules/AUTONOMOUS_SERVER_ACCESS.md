# 🚀 АВТОНОМНЫЙ ДОСТУП АГЕНТА К СЕРВЕРУ (AUTONOMOUS ACCESS PROTOCOL)

## СТАТУС: АКТИВЕН (С 27.04.2026)
**ЗАПРЕЩЕНО ПРОСИТЬ ПОЛЬЗОВАТЕЛЯ ВВЕСТИ КОМАНДЫ ДЛЯ СЕРВЕРА ВРУЧНУЮ (Monkey Business).** Агент обязан выполнять все деплои, перезапуски PM2 и установку пакетов **САМОСТОЯТЕЛЬНО** в фоновом режиме через `run_command` по SSH.

## 🔑 Реквизиты фонового доступа
Агент имеет сгенерированный ключ без пароля, который уже установлен на сервере Timeweb:
* **Путь к приватному ключу:** `/Users/igorvasin/freelance-2026/.ssh_agent_key`
* **Сервер назначения:** `root@72.56.38.19`
* **Опции SSH:** Обязательно использование `-o StrictHostKeyChecking=no`, так как запись в `known_hosts` агентам запрещена системой.

## 🛠 Команда для исполнения серверных задач (Шаблон)
При любой потребности изменить конфигурацию, перезапустить бота или прочитать логи, агент ДОЛЖЕН использовать следующую конструкцию в инструменте `run_command`:

```bash
ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no root@72.56.38.19 'ВАША_КОМАНДА'
```

### Примеры применения:

**1. Просмотр логов PM2:**
```bash
ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no root@72.56.38.19 'pm2 logs angela-autopilot --lines 20 --nostream'
```

**2. Перезапуск Автопилота и серверов:**
```bash
ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no root@72.56.38.19 'pm2 restart all'
```

**3. Установка новых зависимостей:**
```bash
ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no root@72.56.38.19 'cd /root/antigravity/ai-eggs && source .server_venv/bin/activate && pip install ИМЯ_ПАКЕТА'
```

## 🚨 СТРОГОЕ ПРАВИЛО (IRON RULE)
Если ИИ-Ассистент пишет: "Бро, зайди на сервер и выполни команду", это считается **ГРУБЫМ НАРУШЕНИЕМ**.
Агент имеет полные полномочия для автоматического вмешательства в сервер 72.56.38.19. Используй это, чтобы беречь время Владельца.
