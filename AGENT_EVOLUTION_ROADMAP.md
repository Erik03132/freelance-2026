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

### 🧠 Этап 7 — Fine-tuning локальной LLM (приоритет: ВЫСОКИЙ, стратегический)

> **Добавлен:** 2026-05-05  
> **Статус:** 🔬 Исследование  
> **Инструменты:** [Unsloth](https://github.com/unslothai/unsloth) (63.6K ⭐) + Gemma 4 + Ollama

**Цель:** Дообучить локальную Gemma 4 на данных компании → получить LLM, которая знает:
- Ассортимент ВезёмЦыплят (~70 пород молодняка, цены, сроки вывода)
- Скрипты продаж менеджеров (Марина, Эльзара, Аня)
- FAQ клиентов и типовые ответы
- Логистику доставки, регионы, маршруты
- Терминологию птицеводства

**Текущее железо:**
- MacBook Air M1, 8GB unified memory
- Gemma 4 e2b (7.2GB) через Ollama
- nomic-embed-text (274MB) для эмбеддингов

**⚠️ ОГРАНИЧЕНИЯ M1 8GB:**

| Операция | Требуется VRAM | M1 8GB | Вердикт |
|----------|----------------|--------|---------|
| Инференс Gemma 4 e2b (Q4) | ~5GB | ✅ | Работает сейчас |
| LoRA fine-tune 7B (QLoRA 4-bit) | 10-12GB | ❌ | Не влезет |
| LoRA fine-tune 2-3B | 6-8GB | 🟡 | На пределе, со swap |
| Full fine-tune 7B | 28-32GB | ❌ | Невозможно |

**РЕШЕНИЯ (от простого к сложному):**

**7.1 — Google Colab + Unsloth (БЕСПЛАТНО, можно СЕЙЧАС)** ✅
```
Colab Free = T4 16GB → достаточно для QLoRA Gemma 4
Unsloth снижает VRAM на 70% → 7B модель в 5-6GB
```
- [ ] Подготовить датасет из CRM (сделки, звонки, FAQ)
- [ ] Запустить [Gemma 4 notebook](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Gemma4_(E2B)-Vision.ipynb)
- [ ] Экспорт в GGUF → загрузить в Ollama на Mac

**7.2 — Unsloth Studio на Mac (Chat + Data Recipes)** ✅
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
unsloth studio -p 8888
```
- macOS поддерживает Chat и Data Recipes (создание датасетов из PDF/CSV)
- ⏳ MLX training для Mac — **coming very soon** (заявлено Unsloth)
- [ ] Установить Unsloth Studio
- [ ] Создать Data Recipe из `expert_knowledge.md` + CRM сканов + FAQ

**7.3 — Fine-tune на VPS Timeweb (если нужна GPU)** 🟡
- Текущий VPS: CPU only (нет GPU) → не подходит для обучения
- Опция: арендовать GPU-инстанс на Timeweb/Vast.ai на 2-4 часа (~$1-3)
- [ ] Оценить стоимость GPU-аренды для одного fine-tune цикла

**7.4 — Промежуточная альтернатива: Ollama Modelfile (БЕЗ fine-tune)** ✅
```
FROM gemma4:e2b
SYSTEM """
Ты — Анжела Заботкина, AI-ассистент компании Азовский Инкубатор (ВезёмЦыплят).
Знаешь ~70 пород молодняка, 3 менеджеров, логистику по ЮФО...
[вставить expert_knowledge.md]
"""
PARAMETER temperature 0.3
```
- Не fine-tune, но **system prompt + RAG** дают 80% эффекта
- Можно сделать СЕГОДНЯ, бесплатно, на текущем железе
- [ ] Создать `ollama/Modelfile.zabotkina` с системным промптом + знаниями

**Данные для обучения (что уже есть):**
| Источник | Файл | Записей |
|----------|------|---------|
| Expert Knowledge | `data/expert_knowledge.md` | ~50 фактов |
| CRM сканы | `data/bitrix_scans/scan_*.json` | ~30 дней |
| Chat Learnings | `data/chat_learnings.json` | Диалоги из чатов |
| FAQ сайта | `vezemcip.ru` | ~40 вопросов |
| Каталог товаров | `products.json` | ~70 пород молодняка (156 позиций в CRM вкл. корма/прочее) |
| Промпты скиллов | `.agent/skills/*/SKILL.md` | 10 скиллов |

**Оценка трудозатрат:**
- 7.1 (Colab): 1 день подготовки данных + 2-4 часа обучения
- 7.2 (Studio): 30 мин установка + эксперименты
- 7.4 (Modelfile): 2 часа → работает сразу

---

### 📚 Этап 8 — Prompt Library (prompts.chat MCP) (приоритет: НИЗКИЙ)

> **Добавлен:** 2026-05-05  
> **Ресурс:** [prompts.chat](https://github.com/f/prompts.chat) (162K ⭐, CC0 лицензия)

**Цель:** Подключить крупнейшую библиотеку промптов как справочник для агентов.

**Задачи:**
- [ ] **8.1** Подключить MCP-сервер prompts.chat:
  ```json
  {
    "mcpServers": {
      "prompts.chat": {
        "url": "https://prompts.chat/api/mcp"
      }
    }
  }
  ```
- [ ] **8.2** Адаптировать 5-7 промптов под нашу нишу (птицеводство, CRM, VK)
- [ ] **8.3** Интегрировать паттерн `Prompt Generator` для авто-генерации SKILL.md

**Оценка:** 7/10 — полезный справочник, но наши скиллы уже сложнее.  
**Трудозатраты:** 2-3 часа

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
| **2–3** | **Этап 7.4** | **Ollama Modelfile с системным промптом (быстрый win)** |
| **3–4** | **Этап 7.1** | **QLoRA fine-tune Gemma 4 через Colab + Unsloth** |
| **4+** | **Этап 7.2** | **Unsloth Studio MLX (когда выйдет поддержка Mac)** |
| **5+** | **Этап 8** | **prompts.chat MCP + адаптация промптов** |
| **6+** | **Этап 9** | **Self-Evolution агентов (GEPA + DSPy)** |

---

### 🧬 Этап 9 — Self-Evolution агентов (приоритет: СТРАТЕГИЧЕСКИЙ, R&D)

> **Добавлен:** 2026-05-05  
> **Статус:** 🔬 Исследование  
> **Источник:** [NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) (2.8K ⭐, MIT)  
> **Научная база:** GEPA (Genetic-Pareto Prompt Evolution) — ICLR 2026 Oral  

**Суть:** Агенты **сами улучшают свои скиллы, промпты и код** через эволюционный поиск. Без GPU, без fine-tuning — только API-вызовы ($2-10 за цикл оптимизации).

**Принцип работы:**
```
Текущий SKILL.md → Генерация тестов → GEPA Optimizer ← Execution Traces
                                         ↓
                                    Мутация промптов → Оценка → Отбор лучших
                                         ↓
                                    Лучший вариант → PR (человек проверяет)
```

**Что оптимизирует (5 фаз):**

| Фаза | Цель | Движок | Применимость для нас |
|------|------|--------|---------------------|
| Фаза 1 | SKILL.md файлы | DSPy + GEPA | 🔥🔥🔥 10 скиллов агентов |
| Фаза 2 | Описания инструментов | DSPy + GEPA | 🔥🔥 MCP-инструменты |
| Фаза 3 | Системные промпты | DSPy + GEPA | 🔥🔥🔥 Промпты Анжелочки |
| Фаза 4 | Код инструментов | Darwinian Evolver | 🔥 bitrix_intelligence.py и др. |
| Фаза 5 | Автоматический цикл | Pipeline | 🔥🔥 Еженедельная самооптимизация |

**Прямое применение к Antigravity:**
1. **10 SKILL.md файлов** (shakespeare, rembrandt, marketer...) → GEPA эволюционирует каждый, оценивает через LLM-as-judge
2. **Системный промпт Анжелочки** → мутация + A/B тест → лучшие ответы клиентам
3. **Код bitrix_intelligence.py / chat_listener.py** → эволюция через pytest + бенчмарки
4. **FAQ-база** → оптимизация формулировок для повышения точности ответов

**Зависимости:**
- Python 3.10+, DSPy (`pip install dspy`), GEPA (`pip install gepa`)
- API ключ LLM (Gemini / OpenRouter — уже есть)
- Тестовый датасет (мин. 3 примера на скилл — GEPA работает даже с 3)

**Риски и ограничения:**
- AGPL v3 на Darwinian Evolver (Фаза 4) → использовать только как CLI
- Молодой проект (7 коммитов, 2.8K ⭐) → может быстро меняться
- Эволюция промптов может «уплыть» от цели → нужен semantic preservation gate

**Стоимость:** ~$2-10 за цикл оптимизации одного скилла (API-вызовы)

**Оценка трудозатрат:**

| Подэтап | Что делаем | Часов |
|---------|-----------|-------|
| 9.1 | Установка DSPy + GEPA, обёртка 1 скилла | 4 |
| 9.2 | Генерация eval-датасета (synthetic) для shakespeare | 2 |
| 9.3 | Первый прогон GEPA на shakespeare SKILL.md | 2 |
| 9.4 | Оценка: baseline vs evolved, человек проверяет | 1 |
| 9.5 | Масштабирование на все 10 скиллов | 8 |
| **Итого** | | **~17 часов** |

---

## 💡 Принципы эволюции

1. **Минимальные зависимости** — начинаем с файлов (`.jsonl`), не с RabbitMQ
2. **Безопасность** — все внешние вызовы через центральный брокер с логированием
3. **Обратная совместимость** — новые интеграции не ломают существующие скрипты
4. **Постепенность** — каждый этап даёт ценность сам по себе, не требует следующего
5. **Документируем всё** — каждый новый навык/агент имеет `SKILL.md` и `metadata.json`
6. **Локальный AI-first** — дообученная Gemma 4 = свой LLM без зависимости от облаков и API-лимитов
7. **Self-Evolution** — агенты сами оптимизируют свои скиллы через эволюционный поиск (GEPA)

---

> **Следующий шаг (обновлён 05.05.2026):**
> 1. ⚡ **Быстрый win:** Создать `Modelfile.zabotkina` с знаниями компании → Ollama → тест
> 2. 📊 Подготовить датасет из CRM + FAQ для fine-tune
> 3. 🧪 Запустить QLoRA через Unsloth на Colab (бесплатно)
> 4. 📥 Экспорт GGUF → загрузить в Ollama → заменить базовую Gemma 4
> 5. 🧬 **R&D:** Попробовать GEPA на одном скилле (shakespeare) — $2-5 за тест
