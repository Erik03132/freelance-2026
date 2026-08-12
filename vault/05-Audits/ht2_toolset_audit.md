# HT-2: Тулсет-аудит — вес скиллов в системном промпте

> Дата: 06.08.2026 · Источник: Hamidun «33 агента» (тулсет = бюджет: 331 инструмент → 302KB
> JSON-схем → 75K токенов префикса; тримминг 15 266 → 1 424 токенов, ответ 17 → 7.7с).

## Метод
Подсчёт байтов всех SKILL.md в ~/.config/opencode/skills (36 скиллов) + оценка
входных токенов (1 токен ≈ 4 байта для русского текста).

## Результат
- **36 скиллов, суммарно 174 908 байт ≈ 43 700 токенов** — если бы все грузились всегда.
- На практике OpenCode грузит скиллы по триггеру описания → реальный префикс меньше,
  но описания всех 36 присутствуют в списке доступных скиллов всегда.

## Тяжёлые скиллы (топ-5 = 65% веса)
| Скилл | Байты | Токены | Комментарий |
|---|---|---|---|
| vk-integration | 20 377 | ~5 100 | Тяжёлый — только под задачи VK |
| beautify-github-readme | 16 383 | ~4 100 | Тяжёлый — только под README-задачи |
| agents/femida | 11 128 | ~2 800 | Проектный, нужен по триггеру |
| svo-veteran-support | 9 357 | ~2 300 | Проектный |
| agents/rembrandt | 9 166 | ~2 300 | Дизайн |

## Кандидаты на сокращение
1. **vk-integration (20KB)** — разбить: ядро в триггер-описание, процедуры вынести
   в отдельные файлы скилла (skills грузят вложенные файлы по необходимости).
2. **beautify-github-readme (16KB)** — описание триггерит только README-задачи;
   допустимо, но можно ужать описания.
3. **Дубли-пары**: deployment (1544) + deployment-procedures (1565) + workflow (2987) —
   три перекрывающихся скилла; bot-development (1663) + telegram-bot-patterns (2221) +
   agents/botman (2680) — три бот-скилла. Кандидаты на слияние/дедупликацию.

## Обновление 11.08.2026: реальные вызовы скиллов (из opencode.db)

> Источник: пост neurobussines/3011 «Skill-Guide» (05.08.2026) — паттерн «считать
> реальные вызовы, а не только вес». Извлечено из `~/.local/share/opencode/opencode.db`
> (`part.data`, `json_extract(data,'$.state.input.name')`, tool=skill).

**Всего 77 skill-вызовов за всё время.** Активно используется меньшинство:

| Скилл | Вызовы | Дней |
|---|---|---|
| bot-development | 12 | 10 |
| brainstorming | 7 | 6 |
| mango-autocall | 6 | 6 |
| levitan-voice-agent | 5 | 4 |
| workflow | 4 | 4 |
| web-search | 3 | 2 |
| governance, frontend-design, agents/femida, action-first | 3 | 2-3 |
| writing-plans, systematic-debugging, mem-search, do, customize-opencode, claude-handoff | 2 | 1-2 |
| остальные (seo-*, smart-rag, video-clipper, geo-strategy, sitemap-audit, ai-seo и др.) | 1 | 1 |

## Выводы из счётчика вызовов
1. **Паттерн Skill-Guide подтверждается**: половина скиллов вызвана 0-1 раз за
   всю историю — они платят токенами за описания, но не приносят пользы.
   Кандидаты на вынос в репозиторий `skills-lib/` (не автозагрузку): весь
   seo-* семейство кроме seo-audit, smart-rag, video-clipper, geo-strategy,
   sitemap-audit, content-* и др. с 1 вызовом.
2. **Каскад вызовов совпадает с реальной работой**: боты (12) + голосовые
   (mango+levitan = 11) + процесс (workflow/brainstorming) = ядро. Именно их
   описания должны быть максимально конкретными.
3. **Метрика**: замерять через
   `sqlite3 ~/.local/share/opencode/opencode.db "SELECT json_extract(data,'$.state.input.name'),count(*) FROM part WHERE json_extract(data,'$.tool')='skill' GROUP BY 1 ORDER BY 2 DESC;"` —
   добавить в finish-day как ponytail-gain для скиллов.

## Рекомендации (по HT-2)
1. Объединить/дедуплицировать дубли-пары (deployment×2, боты×3) — экономия ~8-10K токенов.
2. Проверить, что у тяжёлых скиллов описания максимально специфичны (триггерятся
   только по делу): у vk-integration и beautify описание уже сужает область.
3. **Вынести 0-1 вызовные скиллы из автозагрузки в `skills-lib/`** (см. выводы 1) —
   экономия на описаниях ~15-20K токенов префикса.
4. Замерять после: `find . -name SKILL.md | xargs wc -c | tail -1` до/после.

## Выполнено 11.08.2026: вынос в skills-lib

12 скиллов (0 вызовов) перенесены из `~/.config/opencode/skills/` в
`~/.config/opencode/skills-lib/` (115 376 байт): seo-geo, seo-local,
seo-technical, seo-sxo, seo-content, seo-schema, seo-sitemap, seo-page,
beautify-github-readme, svo-veteran-support, wizard, to-questionnaire.

- **Реальная постоянная экономия: ~268 токенов/запрос** (сумма описаний —
  именно они всегда в списке available skills). Плюс эти 115KB больше не
  загрузятся по ложному триггеру.
- **Уточнение метрики HT-2**: оценка «43.7K токенов» считала весь SKILL.md,
  но в системный промпт постоянно попадают только description. Вес файла
  платится лишь при активации по триггеру. Постоянная цена = описания.
- Скиллы не удалены навсегда: возврат одной командой `mv` (см.
  `skills-lib/README.md`). Решение об удалении — после повторного замера
  вызовов.
- **Не тронуты**: симлинки на `~/.agents/skills/` (external auto-load),
  упомянутые в AGENTS.md (geo-strategy, deployment, web-standards, bitrix,
  content-marketing, self-improvement), seo-audit (точка входа), все с
  вызовами >0.

---

## HT-2 остаток (12.08.2026) — дедупликация deployment/bot-семейств

Проверка пересечений в `~/.config/opencode/skills/`:

### Deployment-family
- `deployment` (May 26, 1544 байт) — базовый.
- `deployment-procedures` (Jul 26, 1565 байт) — **90% дубликат**. Та же таблица
  стратегий, тот же checklist, тот же rollback, тот же security. Отличие:
  формат `[ ]` в checklist + `pm2 monit`. → Полезное слито в `deployment`,
  `deployment-procedures` вынесен в `skills-lib/`.

### Workflow
- `workflow` (2987 байт) — НЕ дубликат `deployment` (TDD/5-axis review/sessions
  vs деплой). Оставлен.

### Bot-family
- `bot-development` (RAG/Smart Fallback, базовый) +
  `telegram-bot-patterns` (Telegram FSM/rate-limit, специфичный) +
  `agents/botman` (мета-агент, ссылается на оба) — **слои, не дубликаты**.
  Оставлены все 3. Пересечение только в архитектурной диаграмме (не критично).

### Итог HT-2 остатка
- Вынесен 1 скилл (`deployment-procedures`, ~1.5KB описания → минус из
  автозагрузки).
- `deployment` расширен (`pm2 monit`, `[ ]` чек-лист) — покрывает функционал
  вынесенного.
- Экономия: минус 1 триггер-кандидат в списке skills; bot-family НЕ тронут
  (дополняют друг друга, не избыточны).
- Обновлён `skills-lib/README.md` (секция «Дубликаты»).
