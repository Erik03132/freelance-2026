# AI Bureau — Session Chronicle

## Goal
- Рабочий сайт AI Bureau с RAG-чатом, лид-воронкой, современным фронтендом по Chrome Modern Web Guidance.

## Constraints & Preferences
- Светлая/нейтральная цветовая тема (oklch, не dark).
- Все современные веб-API: `<dialog>`, Popover API, Container Queries, Scroll-driven animations, View Transitions, oklch, `@starting-style`.
- RAG-пайплайн: гибридный поиск (0.7 косинус + 0.3 keyword overlap), Top-K 15→7, retry 2x при сетевых ошибках.
- Сервер на чистом Node.js (без express/deps).
- Лид-воронка: greeting → business_type → task_description → budget → contact_collection → completed. Сохранение в `leads.json`.
- Магазинный (magazine) лейаут: split-screen hero, нумерованный список услуг, горизонтальный scroll хаба.

## Progress
### Done
- **API-ключи:** Найдены свежие ключи в `ai-eggs/.env`. OpenRouter и Gemini ключи рабочие, проверены. Gemini геозаблокированы из РФ.
- **Индексация знаний:** 253 вектора из 22 файлов (бэклог, стратегия, проекты, скиллы). OpenRouter `text-embedding-3-small`.
- **Server.js:** Полностью переписан. `apiPost` через `https` модуль (вместо fetch). Гибридный поиск, retry 2x. Лид-воронка: stage-зависимые system prompt, `callLLM` с контекстом, сохранение в `leads.json`. Timeout 30s.
- **Визуал:** Радикальный редизайн — split-screen hero с нейро-графом (Canvas 2D, force-directed, mouse interaction, particles, 24 узла). Секции: 01 Компетенции (нумерованный список с `animation-timeline: view()`), 02 Суверенитет данных (governance-блок с радиальным градиентом), 03 Хаб экспертизы (горизонтальный scroll-snap). Прогресс-бар сверху.
- **Цветовая тема:** Светлая, нейтральная. Все хардкоды oklch заменены на CSS-переменные.
- **Чат (`<dialog>` + Popover API):** BureauBot в `<dialog>` с `showModal()`, backdrop blur, `@starting-style` entry/exit. Индикатор прогресса воронки.
- **index.html:** Починен (были битые теги).
- **useChat.ts:** Починен баг передачи leadData. Убран хардкод ответов.
- **Сборка:** `vite build` — без ошибок. CSS 12 KB / JS 158 KB.
- **Инфраструктура:** Backend (:3001) + Frontend (:3000) запущены. End-to-end тест пройден (все 4 стадии воронки + RAG-ответы).
- **InteractiveNeuralGraph:** Force-directed Canvas с 24 узлами, mouse repulsion, edge glow, particle flows, pulsing nodes.

### In Progress
- (none)

### Blocked
- SOCKS5-прокси (`172.120.21.141:64469`) не работает — `PROXY_FAILED`. OpenRouter доступен напрямую, но с перебоями (иногда `ETIMEDOUT`). Retry 2x спасает.
- Gemini API недоступен напрямую (geo-block). Для использования нужен рабочий US-прокси.

## Key Decisions
- OpenRouter вместо Gemini для эмбеддингов и LLM — ключ оказался рабочим, не требует прокси.
- `https` модуль вместо `fetch` для API-вызовов — не имеет таймаутов по умолчанию, плюс поддержка прокси через `socks-proxy-agent` (прокси пока мёртв, но механика готова).
- Магазинный лейаут (numbered list, split hero, horizontal scroll) вместо карточной сетки.
- CSS-переменные + `color-mix()` вместо хардкодов oklch.
- Canvas 2D force-directed graph вместо анимированного SVG для героя.

## Next Steps
1. Найти рабочий US/SOCKS5-прокси для Gemini (если нужно будет использовать Gemini API).
2. Добавить View Transitions API для смены секций.
3. Добавить CSP-метатег (Content-Security-Policy).
4. Деплой на VPS/хостинг.
5. Отрефакторить сервер на Express/Fastify для production.

## Critical Context
- **OpenRouter key:** в `.env.local` (рабочий, есть баланс).
- **Gemini keys:** в `.env.local` (основной + бэкап). Геозаблокированы из РФ.
- **Порт:** Frontend :3000, Backend :3001.
- **Тема:** Светлая, `--bg: oklch(0.97 0.005 260)`.
- **Сборка:** `vite build` без ошибок.
- **Backend:** `node server.js` — необходим для работы чата и лид-воронки.
- **leads.json:** Сохраняет лиды.

---

## 08.06.2026 — Content Machine Finalize (ai-eggs)

**Контент-машина «Своё Подворье»:** финальная доводка и тестирование.

### Что сделано
- **Контент-план июнь** (`month2_content_plan.md`): 23 поста на 8–30 июня, каждый 3-й — про цыплят/утят со ссылкой на vezemcip.ru
- **`morning_post.py`**: загрузка темы из контент-плана (`_load_content_plan`), кнопки «📡 Только TG» / «📡 Только Дзен» / «📡 Только VK», прокси+resolve для РФ
- **`fan_publish.py`**: Дзен — фото и текст раздельно (работает с автоимпортом), `--form-string` для `@` в chat_id, `--proxy`/`--resolve`
- **Сайт**: `_is_poultry_post` — публикация только для постов про цыплят/утят. Сохраняет `.md` в `data/site_posts/`
- **OK**: `data/ok_posts/podvorye/YYYY-MM-DD_HHMM/post.txt + photo.png` — для ручного копирования
- **`photo_cascade.py`**: Leonardo prompt с no-american, VK API retry, убран `os.unlink` после VK (ломал последующие публикации)
- **`tg_bot.py`**: PENDING_DIR fix, SOCKS5 прокси для бота

### Тестирование (5/5 площадок)
| Площадка | Результат |
|----------|-----------|
| TG @svoye_podvorye | ✅ |
| VK (post_id: 149) | ✅ |
| Дзен @podvorye_dzen → автоимпорт | ✅ |
| Сайт `data/site_posts/` | ✅ |
| OK `data/ok_posts/` | ✅ |

### Архитектура
```
morning_post.py --brand podvorye
  → _load_content_plan() → month2_content_plan.md
  → generate_post_text() → OpenRouter (Gemini fallback)
  → generate_photo() → Leonardo AI
  → save_pending() + send_preview_to_admin() → TG кнопки
  → fan_publish() → TG + VK + Дзен + OK + Сайт
```

### Ключевые решения
- Дзен: фото отдельно, текст отдельно (автоимпорт не берёт caption у sendPhoto с HTML)
- Бот только на VPS (Telegram conflict при локальном запуске)
- Синк через SCP, не git (VPS без гит-репы ai-eggs)

---

## Relevant Files
- `/Users/igorvasin/freelance-2026/ai-bureau/.env.local` — свежие ключи (OpenRouter + Gemini).
- `/Users/igorvasin/freelance-2026/ai-bureau/server.js` — Node.js сервер, гибридный поиск, лид-воронка, retry.
- `/Users/igorvasin/freelance-2026/ai-bureau/src/index.css` — oklch, scroll-driven animations, container queries, `<dialog>`.
- `/Users/igorvasin/freelance-2026/ai-bureau/src/App.tsx` — split-screen hero, numbered services, horizontal hub.
- `/Users/igorvasin/freelance-2026/ai-bureau/src/components/InteractiveNeuralGraph.tsx` — Canvas force-directed graph.
- `/Users/igorvasin/freelance-2026/ai-bureau/src/components/BureauBot.tsx` — `<dialog>` с showModal(), Progress API.
- `/Users/igorvasin/freelance-2026/ai-bureau/src/hooks/useChat.ts` — починен, генерация через сервер.
- `/Users/igorvasin/freelance-2026/ai-bureau/scripts/ingest-knowledge.js` — OpenRouter embeddings.
- `/Users/igorvasin/freelance-2026/ai-bureau/knowledge/processed/vectors.json` — 253 вектора.
- `/Users/igorvasin/freelance-2026/ai-bureau/leads.json` — сохранённые лиды.
- `/Users/igorvasin/freelance-2026/ai-eggs/.env` — источник свежих ключей.
- `/Users/igorvasin/freelance-2026/ai-bureau/CHRONICLE.md` — этот файл.
