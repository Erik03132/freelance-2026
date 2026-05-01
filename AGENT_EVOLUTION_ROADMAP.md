# 🚀 Эволюция агентов Antigravity — Дорожная карта

> **Тема:** Совершенствование, автоматизация и упрощение взаимодействия с агентами экосистемы Antigravity  
> **Создан:** 2026-04-30  
> **Статус:** 🟡 Планирование  
> **Связанные файлы:** `ACTIVE_TASKS.md`, `AGENT_SKILL_ROADMAP.md`

---

## 🧠 Концепция

Агенты Antigravity становятся полноценной **автономной системой**:
- Единая шина сообщений → агенты общаются между собой без ручного запуска
- Стандартизированный API → новый агент подключается за часы, не дни
- Автоматизированная рутина → финиш дня, бэкапы, деплой — без участия шефа
- Мониторинг → система сама сообщает о проблемах в Telegram

---

## 📐 Архитектурная схема

```
[Шеф/Пользователь]
       │
       ▼
  [agctl CLI]  ←→  [Telegram Webhook]  ←→  [REST Webhooks]
       │
       ▼
  [agentClient.js]  ──  единая точка входа
       │
       ▼
  [event_log.jsonl]  ──  файл-очередь / брокер событий
       │
  ┌────┴────────────────────┐
  ▼                         ▼
[igorek-core]         [sherlock]
[rembrandt]           [kulibin]
[shakespeare]         [marketer]
       │
       ▼
  [skillLoader.js]  ──  регистрирует навыки из ./skills/
       │
       ▼
  [logAgent.js]  ──  JSON-логи в ./logs/
       │
       ▼
  [Prometheus]  ──  метрики → Grafana
  [Alertmanager]  ──  алерты → Telegram
```

---

## 📋 Этапы реализации

### ✅ Этап 0 — Уже сделано (текущий статус)
- [x] Агенты определены как markdown-файлы в `.agent/agents/`
- [x] Навыки хранятся в `.agent/skills/` и `./skills/`
- [x] GBP-протокол загрузки контекста
- [x] Perplexity API для Шерлока
- [x] GitHub MCP Server подключён
- [x] OrbStack / Docker настроен

---

### 🔧 Этап 1 — Унификация коммуникации (приоритет: ВЫСОКИЙ)

**Цель:** Одна функция для вызова любого агента. Не нужно знать, как именно работает агент.

**Задачи:**
- [ ] **1.1** `utils/agentClient.js`
  ```js
  export async function callAgent(agentId, action, payload) {
    const msg = { agentId, action, payload, ts: Date.now(), id: uuid() };
    await writeToQueue(msg);          // пишем в event_log.jsonl
    return await waitForResponse(msg.id); // ждём ответа
  }
  ```
- [ ] **1.2** `shared/event_log.jsonl` — файл-очередь
  - Каждая строка = одно событие в формате JSON
  - Агенты читают очередь и обрабатывают свои сообщения
- [ ] **1.3** `config/message_schema.yaml` — схема сообщений
  ```yaml
  fields:
    - id: string (uuid)
    - agentId: string  # кому адресовано
    - action: string   # что сделать
    - payload: object  # данные
    - ts: timestamp
    - status: pending | processing | done | error
    - response: object # ответ агента
  ```
- [ ] **1.4** `config/agents.yaml` — реестр агентов
  ```yaml
  agents:
    - id: igorek-core
      name: Игорёк (Оркестратор)
      path: .agent/agents/igorek-core.md
      permissions: [read, write, execute]
    - id: sherlock
      name: Шерлок (Аналитик)
      path: .agent/agents/sherlock.md
      permissions: [read, search]
    # ...и т.д.
  ```

**Оценка трудозатрат:** 2–3 дня  
**Окупаемость:** Снижает время на координацию агентов на ~50%

---

### ⚙️ Этап 2 — Автоматизация рутины (приоритет: ВЫСОКИЙ)

**Цель:** Рутинные операции выполняются автоматически без команды шефа.

**Задачи:**
- [ ] **2.1** Cron для `finish-day`:
  ```bash
  # Добавить в crontab -e
  0 23 * * * ~/freelance-2026/tools/finish_day.sh >> ~/freelance-2026/logs/cron.log 2>&1
  ```
- [ ] **2.2** Автобэкап на NAS (`launchd` для macOS):
  ```xml
  <!-- ~/Library/LaunchAgents/com.antigravity.nas-backup.plist -->
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>3</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  ```
- [ ] **2.3** GitHub Actions для линта агентов (при push):
  ```yaml
  name: Lint Agent Skills
  on: [push]
  jobs:
    lint:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - run: npx markdownlint-cli "**/*.md"
  ```
- [ ] **2.4** Перенос `deploy.sh` в задачи очереди через `callAgent`

**Оценка трудозатрат:** 1–2 дня

---

### 💻 Этап 3 — CLI-интерфейс агентов (приоритет: СРЕДНИЙ)

**Цель:** Быстро отправить команду агенту из терминала одной строкой.

**Задачи:**
- [ ] **3.1** `tools/agctl.sh` — CLI-утилита
  ```bash
  #!/bin/bash
  # Использование: agctl <agent> "<message>"
  AGENT=$1
  MESSAGE=$2
  node utils/agentClient.js --agent "$AGENT" --msg "$MESSAGE"
  ```
- [ ] **3.2** Псевдонимы в `.zshrc`:
  ```bash
  alias igorek='agctl igorek-core'
  alias sherlok='agctl sherlock'
  alias rembrandt='agctl rembrandt'
  ```
- [ ] **3.3** Подключить `agctl` к `agentClient.js`

**Оценка трудозатрат:** 1 день  
**Пример использования:**
```bash
$ igorek "Составь план на сегодня"
$ sherlok "Найди задачи по AI-ботам на Kwork"
```

---

### 📊 Этап 4 — Мониторинг и алертинг (приоритет: СРЕДНИЙ)

**Цель:** Система сама сообщает о проблемах и статусе агентов.

**Задачи:**
- [ ] **4.1** `utils/logAgent.js` — JSON-логи
  ```js
  export function log(agentId, action, status, data) {
    const entry = { ts: new Date().toISOString(), agentId, action, status, data };
    fs.appendFileSync(`./logs/agent_${agentId}.log`, JSON.stringify(entry) + '\n');
  }
  ```
- [ ] **4.2** Prometheus-метрики (simple push gateway):
  - Количество запросов к агентам
  - Среднее время ответа
  - Количество ошибок
- [ ] **4.3** Telegram-алерты при сбоях:
  ```js
  // При ошибке агента → отправить в Telegram
  await sendTelegramAlert(`⚠️ Агент ${agentId} упал: ${error.message}`);
  ```

**Оценка трудозатрат:** 2–3 дня

---

### 🧩 Этап 5 — Модульная архитектура навыков (приоритет: СРЕДНИЙ)

**Цель:** Новый навык подключается за часы, не дни.

**Задачи:**
- [ ] **5.1** `utils/skillLoader.js` — авторегистрация навыков:
  ```js
  // Сканирует ./skills/, читает SKILL.md, регистрирует навык
  const skills = await loadSkills('./skills/');
  ```
- [ ] **5.2** `metadata.json` для каждого навыка:
  ```json
  {
    "id": "brand-voice",
    "name": "Голос бренда",
    "version": "1.0.0",
    "agent": "shakespeare",
    "permissions": ["read"]
  }
  ```
- [ ] **5.3** RPC-интерфейс навыка:
  ```js
  // Вызов навыка через agentClient
  await callAgent('shakespeare', 'brand-voice', { topic: 'Пост для VK' });
  ```

**Оценка трудозатрат:** 2–3 дня

---

### 🌐 Этап 6 — Внешние интеграции (приоритет: НИЗКИЙ, но ценный)

**Цель:** Управлять агентами из Telegram, Slack, Calendar.

**Задачи:**
- [ ] **6.1** **Telegram → агенты:**
  ```
  Шеф в TG: "Шерлок, найди задачи по SEO на Kwork"
  → Webhook → callAgent('sherlock', 'search', { query: 'SEO Kwork' })
  → Ответ → отправить обратно в TG
  ```
- [ ] **6.2** **Google Calendar → задачи:**
  - Каждое событие в Calendar = задача для агента
  - Агент планировщик читает Calendar API и ставит задачи в очередь
- [ ] **6.3** **REST-webhooks:**
  ```
  POST /api/agent/sherlock/search
  { "query": "AI-боты Kwork", "filters": { "budget_min": 10000 } }
  ```

**Оценка трудозатрат:** 1–2 недели (зависит от интеграций)

---

## 📅 Рекомендуемый порядок внедрения

| Неделя | Этап | Что делаем |
|--------|------|-----------|
| 1 | Этап 1 | `agentClient.js` + `event_log.jsonl` + схема сообщений |
| 1–2 | Этап 2 | Cron + NAS-бэкап + GitHub Actions |
| 2 | Этап 3 | `agctl` CLI + псевдонимы в `.zshrc` |
| 3 | Этап 4 | Логи + Telegram-алерты (Prometheus — опционально) |
| 3–4 | Этап 5 | `skillLoader.js` + `metadata.json` для навыков |
| 5+ | Этап 6 | Telegram-бот + Calendar + REST API |

---

## 💡 Принципы эволюции

1. **Минимальные зависимости** — начинаем с файлов (`.jsonl`), не с RabbitMQ
2. **Безопасность** — все внешние вызовы через центральный брокер с логированием
3. **Обратная совместимость** — новые интеграции не ломают существующие скрипты
4. **Постепенность** — каждый этап даёт ценность сам по себе, не требует следующего
5. **Документируем всё** — каждый новый навык/агент имеет `SKILL.md` и `metadata.json`

---

> **Следующий шаг:** Начать с Этапа 1 — создать `utils/agentClient.js` и `shared/event_log.jsonl`. Написать шефу: *"Погнали прокачивать агентов — Этап 1?"*
