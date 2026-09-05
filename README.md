# Игорь В. — AI-инженер | LLM / RAG / Автоматизация

**Специализация:** прикладная AI-автоматизация для МСБ — от обследования процесса до внедрения в прод. Python, FastAPI, Telegram-боты, Bitrix24, RAG, n8n.

**Образование:** РЭУ им. Плеханова (1989). Английский — B1 (читаю документацию с AI). Формат — удаленка, гибрид Москва.

**Контакты:** HH, Telegram — по запросу.

---

## Кейсы

### 1. «Архивариус» — RAG-бот по 40 Гб документов (продакшн)
**Задача:** сократить поиск по регламентам и ускорить подготовку ответов.
**Решение:** Python 3.12 + FastAPI, Qdrant/pgvector, гибридный поиск + переранжирование, structured output, интеграции Bitrix24 REST, eval на 150 эталонах.
**Результат:** 25 мин → 40 сек (-97%), 12 ч ручной аналитики → 1.5 ч, точность 89–91% по eval, uptime 99.5%. Собрано за 3 дня в связке Claude Code + Cursor.
**Стек:** Python, FastAPI, PostgreSQL, Qdrant, LangChain, Docker.

### 2. Telegram-бот + CRM (Bitrix24) + телефония Mango
**Задача:** автоматизировать прием заявок и контроль исполнителей.
**Решение:** Telegram Bot API, вебхуки Bitrix24, Mango VPBX, очереди, FSM, логирование.
**Результат:** 12–18 ч ручной обработки → 1.5–2 ч, прозрачность статусов, возвраты снижены.
**Стек:** Python, Aiogram, Bitrix24 REST, PostgreSQL, Redis, Docker.

### 3. STT/TTS — транскрибация и озвучка
**Задача:** ускорить обработку созвонов и создание контента.
**Решение:** Whisper (STT), diarization, streaming STT/TTS, постобработка LLM.
**Результат:** 4 мин аудио → 1.5 мин обработки, точность транскрибации 90%+.
**Стек:** Python, Whisper, LLM API, Docker.

---

## Стек
`Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Redis, Docker, Git, REST API, LLM API (OpenAI/Claude/YandexGPT), LangChain/LangGraph, LlamaIndex, Qdrant/pgvector/Milvus, n8n/Make, Bitrix24 API, MCP, Langfuse, CI/CD`

---

## Как работаю
1. Обследование процесса → 2. Архитектура + ТЗ → 3. MVP → 4. Внедрение + метрики → 5. Сопровождение.
Быстро осваиваю стек заказчика. Работаю без доступа к production, ставлю задачи однозначно (проблема → изменение → критерий приемки → негативный сценарий).

---

## Setup после клонирования

```bash
# 1. Окружение
cp .env.example .env
# 2. Pre-commit
pip install pre-commit gitleaks
pre-commit install
```
Хуки: `.pre-commit-config.yaml` → `githooks/*.sh`. Секреты: см. `SECRETS_ROTATION.md`.

