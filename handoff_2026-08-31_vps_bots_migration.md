# Handoff: Перенос Telegram-ботов на VPS и отвязка от Mac

## 🎯 Главный результат расследования (31.08.2026)
1. **Подтверждено:** Боты в Telegram физически работали **на Маке** (через процессы `ai.hermes.gateway-*` в `launchd`). При закрытии крышки Мака боты засыпали.
2. **Токены на VPS были устаревшими:** На VPS в `profiles/*/.env` лежали старые токены, которые Telegram отклонял (`The token was rejected`).
3. **Токены синхронизированы:** Скриптом перенесены актуальные токены со всех профилей Мака на VPS в `/root/.hermes/profiles/*/.env`.
4. **Результат проверки токенов на VPS:**
   - Токены **100% валидны**! Telegram выдал ошибку: `Conflict: terminated by other getUpdates request; make sure that only one bot instance is running`.
   - Это значит, что VPS успешно постучался в Telegram, но Telegram не пустил его, так как **в этот же момент опрос (getUpdates) держал Mac**.

---

## 🛠️ Что осталось сделать для полного переезда ботов на VPS (в новом окне)

### Шаг 1. Отключить запуск ботов на Маке
Чтобы Telegram не давал `Conflict 409`, нужно остановить и выгрузить гейтвеи из `launchd` на Маке:
```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-*.plist
```

### Шаг 2. Перезапустить gateway на VPS
После отключения на Маке VPS заберет себе сессии Telegram без конфликтов:
```bash
ssh -p 2222 root@127.0.0.1 "systemctl restart hermes-gateway"
```

### Шаг 3. Зафиксировать модель для генерации на VPS
В `profiles/*/config.yaml` на VPS для генерации ответов прописать рабочую модель (например, `deepseek-v4-flash-free` или `laguna-s-2.1-free` через `opencode-zen` с валидным ключом или через рабочий апстрим), чтобы боты не только принимали сообщения, но и генерировали ответы без падений.

---

## 📋 Статус активных задач (ACTIVE_TASKS.md)
- [x] **MCP-001** — Vercel MCP авторизован через OAuth PKCE (37 tools доступны).
- [x] **Peer VPS** — Peer зарегистрирован на Mac (`http://127.0.0.1:8742`).
- [x] **Токены ботов** — Синхронизированы с Мака на VPS.
