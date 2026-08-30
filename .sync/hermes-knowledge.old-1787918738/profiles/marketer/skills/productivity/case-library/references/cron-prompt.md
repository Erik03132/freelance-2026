# Cron Prompt — `hermes-cases-weekly`

Используется в `cronjob action=create prompt=...`.
Без `deliver` (по умолчанию local) — результат сохраняется, не отправляется в чат.

---

```
Найди 3-5 свежих публичных кейсов использования Hermes Agent / AI-агентов / LLM-инструментов за прошедшую неделю.

Источники (по приоритету):
1. YouTube: фильтр «за неделю», запросы «Hermes Agent case», «Hermes Agent workflow»
2. Каналы: AI Stack Engineer (OpenCode, MCP, CodeGraph), Дмитрий Попов / COMANDOS AI
3. vc.ru/ai (русскоязычные практические разборы)
4. GitHub Trending в тематике ai-agents / hermes-agent / mcp
5. Telegram-каналы практиков (AntiGravity Brain, Hermes Agent Russian Community если есть)

Для каждого кейса:
- Прочитай источник (не только описание/сниппет)
- Дай вердикт по формату «что → зачем → применимо ли нам → брать/не брать»
- Если долгоживущий урок — создай one-pager в ~/freelance-2026/docs/cases/<slug>.md
  по шаблону из скилла `case-library`
- Обнови ~/freelance-2026/docs/cases/INDEX.md одной строкой
- Если из кейса вытекает пилот — добавь ES-N в ~/freelance-2026/ACTIVE_TASKS.md со ссылкой на файл кейса
- Если шум/продающее — добавь одну строку в секцию «❌ Пропущено» с короткой причиной

Громкие цифры (звёзды, метрики) верифицируй живым API:
  curl -sf https://api.github.com/repos/<owner>/<repo> | grep stargazers_count

Не реализуй пилоты из кейсов автоматически — только фиксируй как ES-N в ACTIVE_TASKS.
В конце ответа — сводка: сколько кейсов найдено, сколько в docs/cases/, сколько пропущено, ID добавленных ES-N.
```