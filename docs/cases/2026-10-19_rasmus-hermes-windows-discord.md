# rasmus-hermes-windows-discord — личный рабочий процесс Hermes на Windows + Discord

**Автор/источник:** AI in C# (Rasmus Wulff Jensen, YouTube, 05.10.2026, [pAnOpLiRpn8](https://www.youtube.com/watch?v=pAnOpLiRpn8))

**Суть (2-3 строки):** Разработчик запускает Hermes Agent 24/7 на локальном Windows-ПК 3 месяца. Основной интерфейс — Discord (несколько каналов/треды: meal prep, morning status, notifications, YouTube, email triage, invoices, calendar). Ключевой инсайт: Discord вместо Telegram даёт многоканальность и контекстные инструкции на канал — это «меняет всё». Агент работает через schedules/hooks/dashboard, не требует API-ключа для старта (v0.22), интегрирует RSS, X, Gmail, Calendar, Todoist, файловую систему, терминал.

**Стек:**
- OS: Windows (локально, не VPS/Mac Mini)
- Коммуникация: Discord (multi-channel, threads per domain)
- Модели: не указано явно (вероятно OpenRouter/Cloud, так как локального железа для больших моделей нет)
- Интеграции: RSS, X/Twitter, Gmail, Google Calendar, Todoist, файловые операции, терминал (git, builds, scripts), cron jobs, background processes
- Память: персистентная между сессиями (преференции, workflows, доменные знания)
- Навыки: финансовый трекинг (акции, опционы), domain intelligence/reconnaissance
- Сохранение контекста: личный Obsidian vault как SSoT

**Что применимо у нас:** [ЧАСТИЧНО] — Discord как основной интерфейс уже оценён у нас (ES-NEW-02: fail-closed Discord gateway), но у нас профиль femida на VPS + TG-бот @hermes03132_bot. Многоканальность Discord (threads per domain) — сильный паттерн, который можно перенести в TG через топики (forum groups). Локальный Windows-хост — не наш сценарий (у нас Mac + VPS), но демонстрирует, что Hermes стабилен на Windows. «9 из 10 бросают после хайпа» — подтверждает нашу боль: нужен ночной конвейер + утренний дайджест, чтобы агент не забывался.

**Действие:**
- [x] Создать запись в `docs/cases/`
- [ ] Изучить перенос многоканального UX в Telegram Topics (forum groups) для профилей sherlock/marketer/femida → ACTIVE_TASKS как **ES-NEW-04**
- [ ] Проверить: можно ли в текущем Hermes gateway настроить Discord + TG параллельно с разными профилями на канал

**Подводные камни (из источника):**
- Требует доверия: полный доступ к файлам/папкам на хосте
- Нужен фиксированный IP + Caddy/reverse proxy для экспоза дашборда вовне (автор делает это)
- Telegram «однообразен» — один чат, теряется контекст; Discord каналы = разделение доменов
- Агент «забывается» без регулярного использования — нужен внешний триггер (крон/дейли)

**Когда НЕ применять:** Если нет возможности/желания держать машину 24/7 онлайн; если приватность локальных файлов критична и нет изоляции; если нужен только coding-агент без бытовых интеграций.