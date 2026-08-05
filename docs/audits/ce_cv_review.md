# CE-2/CE-3: Изучение ce-plan/ce-code-review/lfg + вывод

> Дата: 06.08.2026 · Источник: EveryInc/compound-engineering-plugin (21K⭐, 32 скилла)

## CE-2: Сравнение с нашими планами/ревью

| Аспект | Их (ce-plan / ce-code-review) | Наши (writing-plans / two-axis review) | Забрать |
|---|---|---|---|
| План | U-ID на каждый элемент, тест-сценарии прикреплены к плану, confidence-check | планы без U-ID, гейты не формализованы | **U-ID + test-scenarios в планы** (готовый readiness-гейт) |
| Ревью | report-only multi-agent review ПРОТИВ плана, apply — явный | two-axis (standards+spec) без привязки к плану | **проверка «каждый пункт плана покрыт кодом»** |
| Знания | ce-compound → docs/solutions/ с frontmatter + валидаторы frontmatter | self_improve_log (глобальный), lessons не в репо | уже частично (CE-1); frontmatter-валидация не нужна |

**Вывод CE-2:** берём U-ID в writing-plans (разметка пунктов плана U-1..U-N + чек «все U покрыты» в ревью). Это дешёвый readiness-гейт без установки 32 скиллов.

## CE-3: lfg как апгрейд /goal — НЕ БРАТЬ
lfg = автопилот до зелёного PR: план → работа → simplify → ревью → browser-тесты → коммит → push → PR → следить за CI до зелёного.
**Почему не берём:** (1) требует CI/PR-воркфлоу (у нас репозитории без PR-пайплайнов в основном), (2) browser-QA (ce-dogfood) — поверхность дорогая, (3) наш /goal + do + executing-plans покрывает цикл, (4) автопилот-коммиты без человека = риск (граница делегирования пользователя).
**Что берём:** идея «принять рекомендацию следующей области после завершения» — в /goal уже есть (следующая единица работы AP-1).

## CV-2/CV-3: caveman siblings

### CV-2: caveman-shrink (npm) — НЕ внедрять сейчас
Сжимает MCP tool-дескрипшены. У нас MCP-тулов немного (claude-mem, geekneural) и их описания уже краткие; внедрение middleware = сложность > выгода. **Отложено** (пересмотреть при росте числа MCP).

### CV-3: junior-to-senior / loop-factory — заменить Ralph? НЕТ
- junior-to-senior: adversarial review-цикл — у нас уже есть grill-me/двухосевое ревью; дубль.
- loop-factory: spec-driven loop — то же, что ce-loop/lfg; дубль с /goal.
**Вывод:** Ralph и /goal оставить как есть; adversarial review — усиливать через
двухосевое ревью (уже есть), не новым скиллом.

## Итоговые решения
1. **CE-2 ✅**: внести U-ID в writing-plans (практика, без плагина).
2. **CE-3 ✅**: lfg не берём, обоснование выше.
3. **CV-2 ✅**: caveman-shrink отложен.
4. **CV-3 ✅**: junior-to-senior/loop-factory не берём (дубли).
