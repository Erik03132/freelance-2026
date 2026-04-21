# Implementation Plan: Angelochka VK Sales Bot

## 🛠️ Technology Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (Async)
- **Database**: Neon DB (PostgreSQL) with `pgvector` for product search.
- **LLM**: Gemini 1.5 Pro (via Google Generative AI SDK) for reasoning and personality.
- **VK Integration**: `vkwave` or `vk_api` (Long Poll approach).

## 🏗️ Architecture
1. **Message Listener**: Постоянное соединение с ВК через Long Poll. Ловит каждое входящее сообщение.
2. **Context Manager**: Подгружает историю последних 5-10 сообщений клиента из базы, чтобы Анжелочка «помнила», о чем говорили.
3. **RAG-Retrieval**: По запросу клиента (например, «нужна Линда») ищет в базе Neon актуальную цену и наличие.
4. **Logic Engine**: Gemini анализирует сообщение + контекст + данные из БД и генерирует ответ согласно `spec.md`.
5. **Action Dispatcher**: Если клиент оставил телефон — пишет лид в отдельную таблицу `leads` и присылает уведомление в админку.

## 🗄️ Database Schema (Neon)
- `products`: id, name, category, price, stock_status, description_vector.
- `leads`: id, client_id (vk_id), platform (vk/tg), name, phone, city, order_details, status.
- `conversations`: id, client_id, message, sender (bot/user), timestamp.

## 🚀 Today's Implementation Tasks (MVP)
1. [ ] Настройка `vk_manager.py` для приема сообщений (заглушка до получения токена).
2. [ ] Обновление системного промпта Анжелочки в `sales_engine.py` (внедрение Zero-Click логики).
3. [ ] Создание тестового скрипта `test_sales_flow.py` для симуляции диалога без ВК.

---
*Created by Antigravity under the mandate of Spec-Driven Development.*
