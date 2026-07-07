# Levitan — Session Log

## 2026-07-07

### Done
- **Mango S2T integration**: Создан `scripts/mango_s2t.py` — модуль для получения расшифровок через API Речевой аналитики Mango (расширенная статистика → recording_id → recording_transcripts)
- **CRM save fix**: Бот теперь сохраняет ВСЕ звонки в CRM (включая no_answer — статус `no_contact`), а не только отвеченные
- **Recording link**: В заметки CRM добавляется ссылка на запись Mango
- **Backfill command**: Добавлена команда `/backfill` — подтягивает конспекты из Mango для существующих контактов
- **CRM API**: Добавлены `crm_find_by_phone()` и `crm_update_contact()` для обновления контактов
- **Evening dial DB**: Сформирован `_for_evening_dial_2026-07-07.csv` — 73 контакта (35 свежих ping + 38 повтор no_answer)
- **Extended stats API**: Настроен поиск recording_id через расширенную статистику ВАТС (search_string filter)
- **Bot keyboard**: Все `ReplyKeyboardMarkup` теперь с `is_persistent=True`

### Issues / Blockers
- `recording_transcripts` API — жёсткий rate limit (429), не удалось получить текст расшифровки
- `s2t/queries/` (Speech Analytics) — возвращает 3128 (возможно не подключена услуга)
- VPS недоступны — CRM и бот работают только локально
- Whisper STT не используется (качество плохое из-за музыки ожидания)
- Бот не находит recording_id после звонка → думает "не ответил" → шлёт неверный отчёт

### Next Steps
1. Убрать автоотчёт результатов из Telegram (пользователь не нуждается)
2. Дозвонить оставшиеся контакты (73 в базе, ~60 после фильтрации)
3. Настроить вебхук Mango для автоматического получения конспектов
4. Разобраться с rate limit recording_transcripts