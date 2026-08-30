# watermarks-remover — гигиена AI-провенанса в файлах и тексте

**Что:** MIT-проект guillaumemeyer (15.1k★ / 1.7k fork, 128 коммитов, активный — последний коммит час назад). Снимает multi-vendor AI-провенанс с текста (Unicode + статистический rewrite) и файлов (C2PA/EXIF/XMP/container metadata) на PNG/JPEG/WebP/SVG/PDF/DOCX/HTML/MD. Архитектурно — **skill/service split**: скилл в `~/.claude/skills/` это тонкий HTTP-клиент, вся движуха в `service/scripts/` за stdlib ThreadingHTTPServer (`127.0.0.1:8765`, dynamic OpenAPI 3.0.3).
Источник: <https://github.com/guillaumemeyer/watermarks-remover> (v0.5.0 от 14.08.2026, потом ещё 4 PR). Файлы, которые реально читал: `skills/remove-ai-marks/SKILL.md` (14 KB), `skills/clean-user-facing-text/SKILL.md` (4 KB), `service/scripts/server.py` (stdlib HTTP + dynamic OpenAPI), `README.md` (73 KB, 1324 строки), `.env.example`, `SECURITY.md`.

**Суть (метод за 1 минуту):**

Три слоя, всегда независимые:

1. **Layer A — Unicode-нормализация (NFKC, гомоглифы, ZWSP, soft hyphens).** Без LLM, дёшево, идемпотентно. Снимает невидимые символы, которые ИИ-агенты и LLM иногда вставляют (zero-width space U+200B, soft hyphen U+00AD и т.п.). `text_unicode.py` 25 KB, чистый stdlib.
2. **Layer B — статистический rewrite через внешнюю LLM** (конфигурируется `WATERMARKS_REWRITE_BACKEND=ollama|openai-compatible`, по умолнию reasoning_effort=none). Конфиг под наш стек: `--rewrite-base-url http://127.0.0.1:11434` (Ollama) ИЛИ `--rewrite-base-url https://api.deepseek.com` (OpenAI-compatible). Итеративно: `--candidates N` × `--max-loops M`, выходит на первом кандидате, прошедшем evaluation. **Это наш OmniRoute-паттерн: можно подключить любую openai-compatible endpoint.**
3. **Layer C — container metadata strip** для PNG/JPEG/SVG/PDF/DOCX/ODT/HTML/MD: `c2patool`, `exiftool`, `qpdf`. Без LLM.

**Детектор = отдельный шаг, никогда не блокирует clean (fail-soft):** `/detect` принимает текст/image, возвращает массив detections. Детекторы: `markllm` (KGW/SynthID), `claude-text` (заглушка, ждёт API Anthropic), stylometry, SynthID pixel (heavy profile).

**Compose-профили:**
- `core` (всегда) — HTTP-сервис + exiftool + qpdf + c2patool, **публикуется в GHCR**.
- `harness` (опционально) — `wr-markllm` + `wr-markdiffusion`, **публикуются**.
- `heavy` (только локальный билд) — `wr-ctrlregen` (нет LICENSE у upstream), `wr-synthid-score` (non-commercial research license), **никогда не публикуются**.

**Вес (диск):**
- **Только скилл (HTTP-клиент):** ~30 KB текста, **0 MB** — никаких зависимостей.
- **Core сервис (Docker):** ~150 MB (python:3.12-slim + exiftool + qpdf + c2patool).
- **+ harness:** +5-10 GB (MarkLLM/MarkDiffusion тянут torch + opt-1.3b/Stable-Diffusion-2-1-base).
- **+ heavy:** ещё +10-20 GB.

**У нас на Mac 228 GB свободно — core сервис влезает без вопросов, harness/heavy — НЕТ, ставим только на VPS Timeweb 72.56.38.19.**

**Когда юзать у нас (чёткая граница — Layer A безопасен, Layer B/C — этически опасны):**

| Слой | Безопасно? | У нас применимо для |
|------|-----------|---------------------|
| **Layer A (Unicode)** | ДА — это гигиена, не anti-detect | Angela/Levitan/Botman: чистить скрытые символы из шаблонов писем и входящего текста; AI-Eggs/AI-Scout: нормализация перед эмбеддингом (эмбеддинг-модели ломаются на ZWSP); Botman: входящий от клиента в CRM/Mango — чистить перед записью в БД; agent-lab: чистить собственный output перед коммитом в git. |
| **Layer B (rewrite LLM)** | ЭТИЧЕСКИ СЕРО — это и есть «anti-detect» | НЕ использовать для коммерческих публикаций. Только для собственных исследований (A/B-тест собственных текстов). |
| **Layer C (container)** | ДА для своих, ЭТИЧЕСКИ СЕРО для чужих | Свой арт-контент (AI-Eggs логотипы, иллюстрации) — нормально. Чужой — нет. |

**Конкретные правки в нашей системе (по экспертизе):**

1. **Принять архитектурный паттерн «skill = тонкий HTTP-клиент».** У нас CP-1 (cli-for-agent) говорит «как писать CLI», watermarks-remover показывает **куда** его положить: skill не должен тащить Python/venv/torch на хост агента. Скилл = `curl` + base64 + JSON. У нас сейчас в `agent-lab/integrations/` паттерна нет — **создать прецедент**: для каждой новой интеграции (Mango, WB, Bitrix24) делаем skill/service split, а не монолит. Это снижает диск (агент-хост лёгкий) и ускоряет установку (1 curl, не pip install + 5 GB).

2. **Скопировать `skills/clean-user-facing-text/` в `~/.hermes/skills/text-unicode-hygiene/`** (Layer A only, 4 KB). Это:
   - 1 файл `SKILL.md` + 0 scripts (тонкий клиент через curl к сервису)
   - Команды: `curl -sf http://127.0.0.1:8765/health`, `curl -X POST $WM/clean -d '{"file": base64, "name": "input.md"}'`
   - Безопасный дефолт: только Layer A (не anti-detect).
   - Подходит для **Шерлока** (нормализация текста из web-источников), **Angela outbound** (шаблоны писем), **Ботмана** (входящий текст в CRM).

3. **В `agent-lab/references/text-unicode-hygiene.md`** — короткий reference для агентов (не скилл, просто памятка):
   - Какие символы ZWSP/soft-hyphen/homoglyph ломают markdown/CSV/БД
   - Команда curl для очистки
   - Предупреждение: НЕ использовать Layer B для чужих коммерческих текстов (юридический риск)
   - В нашем AGENTS.md уже есть правило «ИНН/КПП — string, не int»; добавить рядом «Unicode — нормализовать NFKC перед записью в БД/JSON/CSV»

4. **Деплой core-сервиса на VPS Timeweb** (если будет спрос). `docker compose up -d` в `~/freelance-2026/infra/watermarks-service/` → доступ с Mac по `WATERMARKS_SERVICE_URL=http://72.56.38.19:8765`. **Не ставить на Mac** — диск. **Не ставить harness/heavy** — 15+ GB и нужны GPU. Если понадобится verification (markllm), вынести в отдельный compose-профиль на VPS с GPU (на Timeweb нет GPU → брать RunPod/A100, но это уже отдельный проект).

5. **В `agent-lab/foundation/AI_CONTENT_POLICY.md`** — короткий документ (1 страница):
   - Layer A (Unicode) — ОК для всего своего
   - Layer C (container) — ОК для своего арта/документов, НЕ ОК для чужого коммерческого
   - Layer B (LLM-rewrite) — только для собственных исследований, **НИКОГДА** для коммерческих публикаций (ЕС AI Act Art. 50, обсуждаемый РФ-закон)
   - Ссылка на `skills/remove-ai-marks/references/ethics.md` upstream как пример формулировки

6. **Pre-commit hook** (для нашего `freelance-2026`/`agent-lab`): `watermarks-remover-check` блокирует коммит, если в staged-файлах есть невидимые Unicode. Это **наша текущая проблема** — мы коммитим JSON с ZWSP от LLM, потом CI падает на парсинге. Конкретная команда: `docker run --rm -v "$PWD:/data" ghcr.io/guillaumemeyer/watermarks-remover:latest /app/scripts/check_staged.py <files>`. Добавить как опциональный pre-commit в `~/freelance-2026/.pre-commit-config.yaml` (если ещё нет).

**Риски/ограничения (экспертиза, авг-2026):**

1. **Главный:** вензоры ЗАКРЫВАЮТ детекторы. Google retired SynthID text watermarking в августе 2026 (коммит `1cc2783` явно это фиксирует в README, .env.example удалил WATERMARKS_GEMINI_*, `GeminiSynthIDTextDetector` удалён из `text_detectors.py`). Anthropic ещё не выпустил watermark detection API (есть placeholder `claude-text`). Тренд явно против ремуверов — инструмент через год может стать бесполезным для text Layer B.
2. **Юридический риск для РФ/EU.** ЕС AI Act Art. 50 уже требует маркировку AI-generated. В РФ обсуждается аналог. Skill сам это признаёт в `references/ethics.md`: «for your own content — not academic fraud or false "human-written" claims». У нас в `agent-lab/foundation/` нет документа про AI Content Policy — **дыра**.
3. **Heavy profile — лицензионный тупик.** CtrlRegen (`noai-watermark`) **не имеет LICENSE**, поэтому upstream watermarks-remover не публикует этот образ в GHCR. SynthID-score sidecar — non-commercial research license. Если мы хотим полный цикл removal — нужен локальный билд по `Dockerfile.ctrlregen`/`Dockerfile.synthid`, и юридически это **только для своих исследований**, не для продакшена.
4. **MarkLLM-detector — same-config-only.** В README и SKILL.md прямо сказано: «verification harness, not an oracle». Нельзя использовать результат «cleared: true» как доказательство, что вензорный детектор тоже не найдёт. Это принципиальное ограничение — агенты могут ошибочно обещать клиенту «полностью скрыли». Skill явно предупреждает, мы должны транслировать.
5. **Зависимость от LLM для Layer B.** Каждый rewrite = 1 LLM-вызов, по умолчанию 1 кандидат, max-loops=1 → дёшево. С `--candidates 3 --max-loops 5` = до 15 вызовов на текст. У нас OmniRoute, можно настроить endpoint. Но для массового применения (тысячи текстов) — **нерентабельно**, лучше Layer A only.
6. **Скилл не публичный в каталоге Hermes/OpenCode.** Upstream устанавливается через `install_skill.py` или `install-skill.sh` (2 скрипта в репо) → копирует в `~/.claude/skills/`. У нас путь `~/.hermes/skills/` — нужно скопировать руками. Без автоматического подхвата системой придётся явно загружать через `skill_view(name='text-unicode-hygiene')` или добавить в `AGENTS.md` явное упоминание.
7. **Verify ≠ certify.** `audit_dir.py` + SARIF export дают покрытие, но не гарантию. Skill честно это пишет, мы не должны продавать клиенту «100% очистка».

**Статус:** **кандидат, внедрить Layer A как text-unicode-hygiene для Angela/Botman/AI-Scout, НЕ ставить Layer B/C в прод.** Причина: text Layer A — чистая гигиена (не anti-detect, не юридически серая). Layer B/C — оставить как reference, не как production-инструмент.

**Сравнение с razbor-servisa (только что разобрали):**
| Аспект | razbor-servisa | watermarks-remover |
|---|---|---|
| Звёзды / зрелость | 7★, 2 коммита, нишевой | 15.1k★, 128 коммитов, multi-vendor, v0.5.0 |
| Назначение | реверс чужого API в CLI | снятие AI-провенанса |
| Архитектура skill | skill = код (Python) | skill = тонкий HTTP-клиент (curl) |
| Требования к агенту | нет (копи-паста в чат) | запущенный Docker (core) |
| Уровень этики | высокий (явные правила) | очень высокий (ethics.md + scope limits) |
| Где у нас полезно | Шерлок/Botman (интеграции) | Angela/Botman/AI-Scout (гигиена Layer A) |

**Главный архитектурный урок для нас:** watermarks-remover — эталон того, **как должен выглядеть наш skill/service split по CP-1**. Буквально копируем паттерн для будущих интеграций (Mango, WB, Bitrix24): skill = `SKILL.md` + curl, сервис = Docker, общаются через OpenAPI 3.0.3.

**Следующие шаги (предлагаю, не делаю без команды):**
1. Скопировать `skills/clean-user-facing-text/` (4 KB, Layer A only) в `~/.hermes/skills/text-unicode-hygiene/`. Альтернативный путь — оформить как Hermes skill в `~/.hermes/skills/` напрямую.
2. Создать `agent-lab/references/text-unicode-hygiene.md` (памятка для агентов, что Layer A = ОК, Layer B/C = этически серо).
3. Создать `agent-lab/foundation/AI_CONTENT_POLICY.md` (1 страница: что Layer A/C ок, Layer B — нет).
4. (Опционально) Поднять `ghcr.io/guillaumemeyer/watermarks-remover:latest` на VPS Timeweb через `docker compose up -d`, если появится реальная задача «прогнать 1000 черновиков через гигиену».
5. НЕ делать pre-commit hook, пока не будет зафиксирован хотя бы один реальный случай «сломали коммит ZWSP-ом». Иначе — шум без пользы.

**Что я НЕ буду делать без явного «да»:**
- Не ставить Docker watermarks-remover на Mac (диск 228 GB).
- Не подключать Layer B (LLM-rewrite) к OmniRoute — нужен отдельный этический разбор.
- Не публиковать ничего про watermarks-remover в наш публичный GitHub — репо PRIVATE, и `docs/integrations/watermarks-remover.md` (если создам) должен лежать там же.