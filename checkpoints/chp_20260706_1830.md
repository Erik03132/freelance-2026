# Changelog — ai-levitan

## 06.07.2026

### Mango Speech Analytics (M1-M16)
- Проанализирована PDF-встреча RECHEVAYA-ANALITIKA v1.26.18
- Определены 6 AI-компонентов: ИИ Помощники, ИИ Конспекты, ИИ Тегирование, ИИ Тематики, Чек-листы, Ловец инсайтов
- Создан документ рекомендаций: `docs/MANGO_SPEECH_ANALYTICS_RECOMMENDATIONS.md`
- Создан шаблон анализа звонков: `docs/CALL_ANALYSIS_TEMPLATE.md`
- **Решение:** data-first подход — сначала 100 звонков → анализ записей → настройка тематик

### Pрайс-лист для зерновой базы
- 11K контактов → 1100 лидов (10%) → 220-330 сделок × 100 тонн × 2-5К₽ маржа
- Рекомендация: фикс 200К₽ + 4% бонус за сделку (гибридная модель)
- Общая маржа клиентов: 44-165 млн₽

### Голосовой агент
- xAI Voice Agent Builder: $0.05/мин ($0.25/звонок), no-code, Grok Voice
- Pipecat (13.3k ⭐): Python, DeepSeek поддержка, sub-second латентность
- LiveKit Agents (11.3k ⭐): WebRTC, SIP интеграция
- Сохранено в `docs/OPEN_SOURCE_VOICE_AGENTS.md`
- **Рекомендация:** Pipecat как основной фреймворк для Фазы 5

### Baresip config
- Добавлены модули: `ctrl_tcp.so`, `stun.so`
- Тестирование: baresip запускается, greeting WAV загружается

### Напоминание
- 12.07.2026 — дедлайн демо Mango (7 дней)
- Создан скрипт `scripts/reminder_mango.sh`
- Календарное событие: `docs/reminder_mango_july12.ics`

### Задачи (ACTIVE_TASKS.md)
- M1-M16: План внедрения Mango Speech Analytics
- Phase 1: Запуск 100 звонков, анализ записей
- Фаза 5: Real-time AI Voice Agent (Вариант D: Pipecat)

---

## Текущие метрики
- Mango: ~$500/мес базовый, ~$1500/мес pro
- xAI: $0.25/звонок, $25 кредит
- Pipecat + DeepSeek: ~$0.01-0.02/звонок
- edge-tts: бесплатно

## Следующие шаги
1. VPS недоступен → ждать доступа
2. 100 звонков → анализ записей → настройка Mango
3. Pipecat: установить и протестировать basic_agent.py
