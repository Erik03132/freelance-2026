## discord-failclosed-permission — Hermes Agent Discord развёртывание с fail-closed политикой (2026)

**Автор/источник:** Hermes Agent Team (официальный блог) — https://hermes-agent.ai/blog/hermes-agent-discord-setup, опубликовано 11 октября 2026  
**Суть (2-3 строки):** Официальный гайд настройки Hermes Agent на Discord с акцентом на 2026 fail-closed политику доступа (bot token ≠ sufficient), thread-based сессии, role/user/channel allowlists, gateway self-test. Руководит через Developer Portal → `hermes gateway setup` → fail-closed конфиг → рукопожатие DM + server channel.  
**Стек:** Hermes Agent gateway (Telegram/Discord/Slack/Mattermost/Email unified), Discord intents (Server Members Intent + Message Content Intent), `hermes gateway setup` CLI wizard, systemd для headless, FlyHermes option для managed.  
**Что применимо у нас:** **ДА** — мы уже настраивали Discord-бота (см. память, bridge/chief/english-tutor через @hermes0313_bot). Fail-closed политика актуальна: раньше полагались на token-only, теперь нужен explicit allowlist. Thread sessions могут улучшить чат-логику для Shield'а и других профилей.  
**Действие:** [ ] Обновить Discord-gateway конфиг в профилях до fail-closed политики: добавить `DISCORD_ALLOWED_USERS`/`DISCORD_ALLOWED_ROLES`/`DISCORD_ALLOWED_CHANNELS` в `.env` → ACTIVE_TASKS как **ES-NEW-02**

---

### Детали разбора (анти-авторитет: проверено в первоисточнике)

1. **Fail-closed = Security по умолчанию:** Раньше Discord бот мог появиться online и принимать сообщения всех. Теперь `DISCORD_BOT_TOKEN` alone is not enough — нужен explicit allowlist (user/role/channel). Если allowlist пустой → все denied. Это breaking change, но обоснованное (security > convenience).
2. **Интенты обязательны:** `Server Members Intent` и `Message Content Intent` — требуется включить в Developer Portal, иначе бот будет online, но молчалив.
3. **Thread sessions (новинка 2026):** Hermes теперь поддерживает Discord threads for conversation history — каждый thread = stateful session. Это улучшает UX по сравнению с flat-chan общением.
4. **FlyHermes option:** Hermes Cloud managed gateway (аналогично Fly.io) — alternative to self-hosted gateway. Полезно если не хочется держать gateway на VPS.
5. **Тестируем по шагам:** `hermes chat -q "reply with discord-provider-ok"` после настройки — проверка, что gateway слышит.

---

### Верификация утверждений автора (ADR-003 + анти-авторитет)

| Утверждение | Проверка | Результат |
|-------------|----------|-----------|
| Fail-closed политика в 2026 Hermes Discord | Официальный блог hermes-agent.ai, опубликовано 11.10.2026 | **Подтверждено** |
| Интенты обязательны | Описаны оба интента с пояснением почему нужны | **Подтверждено** |
| Thread sessions | Упомянуто как "thread sessions" в разделе access policy | **Подтверждено** |
| `hermes gateway setup` wizard | CLI команда описана с пошаговыми инструкциями | **Подтверждено** (соответствует hermes-agent патчу v0.21.7) |
| DISCORD_ALLOWED_USERS / DISCORD_ALLOWED_ROLES / DISCORD_ALLOWED_CHANNELS env vars | Приведены в конфиг-секции с примерами | **Подтверждено** |
| FlyHermes = managed option | Упомянут как альтернатива self-hosted gateway | **Подтверждено**