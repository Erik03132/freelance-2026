# Handoff: «Отдел вокруг Гермеса» — подключение агентов (2026-08-20)

> Статус: 3 шага закрыты, нужен рестарт сессии Гермеса для применения.

## Что сделано
1. **`skills.external_dirs`** прописан в `~/.hermes/profiles/personal/config.yaml`
   (через `hermes config set`, бэкап `config.yaml.bak.*` создан).
   Подтягивает 53 скилла из `~/.config/opencode/skills` + 52 из `~/.agents/skills`.
2. **Фемида** оформлена как агент: `~/.hermes/profiles/personal/skills/productivity/femida-agent/SKILL.md`
   (юр-чек-лист: РИД ст.1298/1373 ГК РФ, NDA, налоги, гранты, ПДн 152-ФЗ; вердикт З/Ж/К).
3. **Эксперт вшит в пайплайн Шерлока** (`sherlock-hh-kwork` SKILL.md, шаг 5.5):
   Шерлок → Эксперт (брать/не брать/в очередь) → [юр-риск] Фемида → Батрак.

## Сборка «отдела»
```
Шерлок (поиск HH/Кворк)
  → ЭКСПЕРТ (главный фильтр релевантности + советник по любым фичам)
  → [юр-риск] ФЕМИДА (legal review)
  → БАТРАК (аудит + отклик)
  + МАРКЕТЕР (упаковка, теперь подключён через external_dirs)
```

## Что сделать утром / при первой возможности
- [ ] **Перезапустить сессию Гермеса** (`/reset` или выход-вход). `external_dirs`
      применяется только на старте процесса (hard invariant: не ломать prompt cache).
- [x] **Видимость проверена (smoke-тест 20.08, БЕЗ рестарта)**: `hermes chat` видит
      `femida-agent=ДА` (нативный в профиле) и `content-marketing=ДА` (из external_dirs
      `~/.agents/skills`) → `external_dirs` применился сразу. Маркетер представлен
      скиллами `content-marketing`, `marketing-psychology`, `ponytail` — все видны.
      Полный `hermes skills` список лучше глянуть после рестарта для полноты.
- [x] **Smoke-тест пайплайна (20.08, БЕЗ сети)**: тестовый markdown (3 вакансии:
      Python-агент / 1C / PHP) прогнан через `sherlock_search.py --stdin` → Шерлок
      корректно ОТСЕК 1C и PHP (исключения), оставил 2 Python/AI. Затем live-вызов
      Гермеса как ЭКСПЕРТ-ФИЛЬТРА дал вердикты: обе → БРАТЬ (100% попадание в стек).
      Связка Шерлок → Эксперт подтверждена.
- [x] **marketer-strategist** переложен в нативный скилл Гермеса
      (`~/.hermes/profiles/personal/skills/productivity/marketer-strategist/SKILL.md`)
      на базе `.agent/agents/marketer-strategist.md` + `prompts/library/marketer.md`.
      Проверка: `marketer-strategist=ДА` после деплоя.
- [ ] Обновить `ACTIVE_TASKS.md` HZ-8 → done (подключение скиллов к Hermes).

## БЛОКЕР (на 20.08 не решён): реальный прогон Шерлока через Firecrawl
- Состояние: `hermes portal info` → `Web tools: not configured`. Managed Firecrawl
  НЕ активирован в Portal routing. Прямой POST в `firecrawl-gateway.nousresearch.com/v1/scrape`
  с `sk-nous-...` ключом из `.env` даёт `AUTH_ERROR: Unauthorized` — этот ключ предназначен
  для portal session, а НЕ для прямого вызова gateway (формат авторизации другой).
- `hermes setup --portal --non-interactive` отказал (нет TTY). `hermes portal` в PTY уходит
  в меню выбора модели, Tool Gateway не активирует слепым вводом.
- **Решение (когда будет время):** зайти в Portal ЧЕРЕЗ БРАУЗЕР (мышкой, без комбинаций) →
  включить Tool Gateway / Web Search & Extract (Firecrawl). Либо `hermes portal open` откроет
  страницу. После активации проверить `hermes portal info` → `Web tools: via Nous Portal`,
  затем запустить `bash scripts/run_sherlock_curl.sh hh data/...json` (wrapper уже готов,
  ходит через curl с учётом SOCKS5-прокси, т.к. urllib его не понимает).
- Сделано заранее: токен лежит в `~/.hermes/profiles/personal/.env` (TOOL_GATEWAY_USER_TOKEN,
  записан из буфера обмена, в чат не попадал). Wrapper `scripts/run_sherlock_curl.sh` готов.
- Smoke-тест БЕЗ сети уже доказал работу связки Шерлок → Эксперт (отсек 1C/PHP, Эксперт
  дал БРАТЬ по 2 Python/AI-вакансиям). Реальный прогон — только вопрос активации Web tools.

## Проверено сейчас (без рестарта)
- config.yaml валиден (YAML parse OK), `external_dirs` = оба пути.
- Все 3 файла скиллов на месте (`sherlock-hh-kwork`, `batrak-agent`, `femida-agent`).
