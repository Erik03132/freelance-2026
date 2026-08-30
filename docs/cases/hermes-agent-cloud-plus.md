# Hermes Agent: Cloud Hosting + Plus-подписка (разбор Шерлока, 22.08.2026)

> Источники: официальный Nous Portal (скриншот пользователя), docs.hermes-agent.nousresearch.com,
> r/hermesagent (Reddit), Facebook-группы Hermes, openclawlaunch.com, virtua.cloud, tencentcloud techpedia,
> hostinger, myclaw.ai, hermes-agent.ai (FlyHermes). Верифицировано через web_search 22.08.2026.

## 1. Главный ответ: 24×7 на сервере — ДА, входит в Plus
Официально (Nous Portal): **«Agent Cloud hosting: Deploy in one click and Portal hosts your
agent in the cloud, running around the clock. Server costs bill straight to your credit balance.»**

То есть **Nous сами хостят агента в облаке** — не нужен твой VPS (217.149.23.113).
Работает 24/7, оплата — с кредитного баланса подписки. Это и есть то, что ты искал.

## 2. Тарифы Nous Portal (официально, из скриншота)
| Тариф | Цена/мес | Кредиты | Бонус | Rollover | Модели | Tools | Лимиты |
|-------|----------|---------|-------|----------|--------|-------|--------|
| Free | $0 | $0 | — | — | только free | стандартные | низкие |
| **Plus** | **$20** | **$22** | +10% | $10 cap | 200+ | hosted | высокие |
| Super | $100 | $110 | +10% | $50 cap | 200+ | hosted | высокие |
| Ultra | $200 | $220 | +10% | $100 cap | 200+ | hosted | высокие |

Rollover = неспользованные кредиты переносятся (лимит зависит от тарифа).

## 3. Что ДАЁТ Plus (помимо 24×7)
- **300+ моделей** (из скриншота): Claude (до Opus 4.8), Gemini (до 3.7 Flash),
  GPT Latest, DeepSeek V4, Nemotron 3, Kimi K2/K3, Mistral, Llama 4, Qwen и т.д.
  Цены видны (напр. Gemini 3.7 Flash $0.30/$1.50 per 1M, Claude Opus $4/$20).
- **Hosted Tools** (биллятся с того же баланса):
  - Browser Use (браузер-автоматизация)
  - FAL (генерация изображений)
  - Firecrawl (web-scraping)
  - OpenAI Studio (голос/voice)
  - Kreа (image_gen)
- **One Account, Everywhere**: один логин → модели + Tool Gateway + cloud hosting.
- **High rate limits** (vs стандартные на Free).

## 4. Hermes Cloud — размеры и цены (из openclawlaunch.com, НЕ официально, но детально)
| Size | RAM | vCPU | Concurrent sessions | Running | Stopped |
|------|-----|------|-------------------|---------|---------|
| Small | 1GB | 2 | 5 | $0.29/день (~$8.70/мес) | $0.03/день |
| Medium | 2GB | 4 | 10 | $0.56/день (~$16.80/мес) | $0.03/день |
| Large | 4GB | 8 | 20 | $1.09/день (~$32.70/мес) | $0.03/день |

- «Scales to zero when idle» — платишь только когда работает.
- Stopped = storage-only ($0.03/день ≈ $0.90/мес) — данные живы.
- **Минимум для деплоя**: $10 кредитов (по Cloud page) или $2 (по getting-started) — бюджет на $10.
- В **preview** (бета) на момент исследования.
- Каналы: Telegram / Discord / Slack / email / CLI против одной shared memory.
- Изолированный hardened container на агента.

## 5. Отзывы фанатов (r/hermesagent, Facebook, X)
- «Hermes Agent Cloud first impressions» (FB): setup < 5 мин, «pretty neat».
- Reddit r/hermesagent: «Nous Portal has been pretty good», хвалят auto-routing.
- «three months with Hermes Agent: what i wish i had known» — USER/MEMORY короткие,
  editable, «rewired my workflow».
- Non-technical users (FB): «0 coding experience, still get Hermes to do all».
- X (@coreyganim): «personal agent with messaging, scheduling, tool access. But it
  doesn't have a learning loop. Doesn't write its own skills» — честный минус.
- Reddit «Battle of the $20 providers»: «Nous Portal - You pay $20, you get $22 credits.
  Not a lot of savings. However they do have some free models from time to time.»

## 6. Cloud vs Self-Host (VPS) — вердикт сообщества
**Аргументы ЗА Cloud (Hermes Cloud / FlyHermes):**
- Uptime 99.95%+ vs 40–60% на локальной машине (спит → агент мёртв).
- Self-learning эффективнее (30-дневный cloud-агент > 90-дневный local).
- Нет обслуживания (Docker, ключи, gateway polling, systemd/launchd).
- Мобильный/messaging доступ быстрее.

**Аргументы ЗА Self-Host (VPS, твой 217.149.23.113):**
- Данные на твоём диске (privacy/control).
- Provider freedom (OpenRouter, Anthropic, Ollama, Portal — любой).
- Полный сервер, не только агент (cron, БД, reverse proxy рядом).
- Нет vendor lock-in.
- VPS-минимум: 1 vCPU + 2GB RAM + 10GB (браузер/несколько каналов → 2vCPU + 4-8GB).
- Цена VPS: ~$6–85+/мес (зависит от размера).

**Гибрид (рекомендуют многие):** self-host для глубокой техработы, Cloud для
повседневного доступа и 24×7 операций.

## 7. Альтернативы хостинга (упомянуты фанатами)
- **FlyHermes** (hermes-agent.ai) — managed, deploy 60 сек, cancel anytime.
- **OpenClaw Launch** — Hermes Cloud alt, 30 сек, нет credit minimum, WhatsApp/WeChat.
- **OMC Cloud, xCloud, Contabo, Hostinger, Bluehost, Network Solutions** — VPS с
  предустановленным Hermes.
- **Virtua.cloud** — гайд self-host на VPS (детальный).

## 8. Русскоязычные источники
- habr.com: статьи про Hermes Agent (мы разбирали ранее, ES-сессия).
- Нет выделенного RU-комьюнити (основной — англоязычный r/hermesagent + FB-группы).
- Дискорд: официальный Nous (упомянут в docs, но прямых отзывов не вытянул — нужен
  инвайт, который я не имею).

## 9. Вердикт эксперта (для тебя, Игорь)
1. **24×7 в облаке — реально**, входит в Plus ($20/мес, $22 кредитов).
   Cloud-инстанс Small ~$8.70/мес + inference сверху. Итог: ~$30–40/мес за полный 24×7.
2. **Твой VPS (217.149.23.113)** — уже есть, но требует обслуживания (мы сегодня
   чинили SSH/VPN). Если хочешь zero-maintenance → Cloud.
3. **Plus vs Free**: Plus нужен для 200+ моделей + hosted tools + высоких лимитов.
   Free — только free-модели.
4. **Рекомендация**: если важен 24×7 без головной боли → **Plus + Hermes Cloud Small**.
   Если важен control/privacy → **self-host на твоём VPS** (мы уже настроили Angela там).
5. **Гибрид**: Angela_bot + Hermes-news уже на VPS (self-host). Можно добавить
   Cloud-инстанс для Mustay (личный агент) → 24×7 без забот.

## 10. Что НЕ проверено (честно)
- Точный состав Plus vs Super vs Ultra (кроме цен/кредитов — из скриншота).
- Реальные отзывы из Discord (нужен инвайт).
- Текущий статус Hermes Cloud (preview → GA? на 22.08.2026 был preview).
- RU-комьюнити (узкое, в основном англоязычное).
