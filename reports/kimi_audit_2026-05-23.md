# 🤖 Аудит ai-eggs — Kimi K2 (SWE-bench #1)
> Дата: 23.05.2026 | Модель: moonshotai/kimi-k2 | Токены: 55 631  
> Файлов: 10 ключевых | Строк: 4 653 | Охват: ядро системы Анжелы

---

## 🔴 КРИТИЧЕСКИЕ БАГИ (могут упасть в продакшне)

### 1. `angelochka_core.py` строка 201 — ADMIN_TELEGRAM_ID без валидации типа
❌ **Проблема**: если `ADMIN_TELEGRAM_ID` задан не как число — `detect_role` всегда возвращает `customer`, даже для владельца.
```python
# БЫЛО (сломано):
_CREATOR_TG_ID = os.getenv("ADMIN_TELEGRAM_ID")

# ФИКС:
_CREATOR_TG_ID = str(os.getenv("ADMIN_TELEGRAM_ID", "")).strip() or "176203333"
```

### 2. `angelochka_core.py` строка 334 — `_has_phone_in_history` без истории
❌ **Проблема**: при повторном запросе «а корм?» бот показывает прайс-лист без телефона — нарушает Phone-First логику продаж.  
**Фикс**: передавать `history=history_cache` из `chat_db.load_history`.

### 3. `bitrix_scanner.py` строка 519 — глобальная мутация при параллельных запусках
❌ **Проблема**: `_closedStages()` вызывается каждый `run_scan` → race condition между cron-запусками.  
```python
# ФИКС: на уровне модуля, один раз
CLOSED_STAGES = frozenset(["LOSE", "APOLOGY", ...])
```

### 4. `tg_bot.py` строка 72 — orphaned lock при SIGKILL
❌ **Проблема**: при убийстве процесса через `systemd kill` остаётся lock-файл → бот не стартует при рестарте.  
**Фикс**: использовать `fcntl.flock` или socket-singleton вместо файлового лока.

---

## 🟠 СЕРЬЁЗНЫЕ ПРОБЛЕМЫ

### Memory Leak — SmartFAQ `_counter` + `_cache`
Словари читаются/пишутся на каждый запрос без `lru_cache`. При нагрузке >5 RPS → бесконтрольный рост RAM.  
**Фикс**: `@functools.lru_cache(maxsize=512)` на `get_faq_response`.

### Race Condition — VectorMemory
`VectorMemory.stats()` и `add_knowledge()` вызываются из двух потоков (cron + HTTP) без файловой блокировки → возможен `sqlite.DatabaseError: database disk image is malformed`.  
**Фикс**: `threading.Lock()` на уровне класса.

### Cron-зависимость `get_latest_scan()`
Если `bitrix_scanner.py` не запускался >8 часов — `get_latest_scan()` возвращает нулевые данные → `build_report_text()` падает на пустом `for`.  
**Фикс**: fallback-обновление при устаревании >2 часов.

---

## 🟡 АРХИТЕКТУРНЫЕ ПРОБЛЕМЫ

| Проблема | Где | Решение |
|---------|-----|---------|
| `detect_role()` дублируется в 3 файлах | `tg_bot.py`, `bitrix_receiver.py`, тесты | Вынести в `utils/roles.py` |
| Разные форматы ID клиентов: `tg_`, `vk_` | `client_memory.py` | Унифицировать через `uuid3` |
| **Мегафайл** `angelochka_core.py` (~1700 строк) | `angelochka_core.py` | Разбить на `sales_logic.py`, `prompts.py`, `price_manager.py` |
| Прайс-лист захардкожен в коде | `angelochka_core.py` | Вынести в `config/prices.json` |
| Системный промпт — монолит | `angelochka_core.py` | `prompts/` папка + Jinja2 шаблоны |

---

## ✅ ЧТО СДЕЛАНО ХОРОШО

1. **Grace degradation**: все внешние сервисы (RAG, VectorDB, Neon) в `try/except` — бот не падает при сбоях
2. **SmartFAQ с fingerprint**: экономит LLM-вызовы, качественные ответы после 3-го повторения  
3. **Phone-First**: `feed_calc_result` запрещён без телефона → продажная воронка не пробивается
4. **Health-monitor v2.0**: каскад проверок + auto-heal + кулдаун-алёртов → быстрое восстановление

---

## 🎯 ТОП-5 ПРИОРИТЕТНЫХ ИСПРАВЛЕНИЙ

| # | Задача | Файл | Сложность |
|---|--------|------|----------|
| **1** | `get_latest_scan()` — always-fresh (fallback при устаревании >2ч) | `bitrix_scanner.py` | 1ч |
| **2** | Унифицировать маппинг ID клиентов (`uuid3` stable CID) | `client_memory.py` | 2ч |
| **3** | Вынести price-list в `config/prices.json` | `angelochka_core.py` | 1ч |
| **4** | Circuit-breaker для OpenRouter (5 ошибок → fallback Ollama) | `angelochka_core.py` | 3ч |
| **5** | Рефактор системного промпта → `prompts/` + Jinja2 | `angelochka_core.py` | 4ч |

---

## 📋 Следующие шаги

- [ ] **Сегодня**: фикс orphaned lock (tg_bot.py:72) — риск нестарта бота
- [ ] **Сегодня**: `CLOSED_STAGES = frozenset(...)` (bitrix_scanner.py:519) — 5 минут
- [ ] **Этот спринт**: get_latest_scan fallback → добавить в W-бэклог
- [ ] **Этот спринт**: вынести prices в JSON
- [ ] **Следующий спринт**: circuit-breaker, рефактор промптов
