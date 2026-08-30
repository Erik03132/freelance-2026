---
name: financier-unit-economics
description: Unit-economics framework (LTV/CAC ≥3:1, payback <12мес, contribution margin) + pricing-strategy playbook + CFO-чеклисты. Адаптирован из Auto-Company `.claude/skills/financial-unit-economics/` + `.claude/agents/cfo-campbell.md`. Для профиля financier: ценообразование, финмодель, Kwork-бюджет, Snapog tier-экономика.
argument-hint: "[продукт/модель + задача: pricing/unit-economics/cost-control]"
disable-model-invocation: true
---

# Financier Unit Economics — мозг Финансиста + Маркетолога

Адаптирован из Auto-Company (MaxMiksa, 2563★).
Объединяет financial-unit-economics framework + CFO-чеклисты Patrick Campbell (ProfitWell).

## Зачем

Финансист + Маркетолог работают в паре:
- **Финансист** считает unit economics, CAC, LTV, payback, contribution margin
- **Маркетолог** использует эти данные для ценообразования, позиционирования, воронки

Этот скил = их общий язык и набор шаблонов.

## Триггер

- «Считай unit economics для [продукт]» / «CAC/LTV» / «payback period»
- «Как ценовать [продукт]?» / «pricing strategy» / «ценовой анализ»
- «Финмодель для [продукт]» / «MRR/ARPU/churn» / «воронка окупается?»
- «Kwork-бюджет на [задача]» / «прайс для [заказ]»
- «Snapog tier-экономика» / «$0/$19/$49 → MRR»
- Входной параметр `$ARGUMENTS` — описание задачи/продукта

## Формулы (Quick Reference)

```
CAC = (Sales + Marketing Costs) ÷ New Customers Acquired

LTV (subscription) = ARPU × Gross Margin % ÷ Monthly Churn Rate

LTV (transactional) = AOV × Purchase Frequency × Gross Margin % × Lifetime (years)

Contribution Margin % = (Revenue - Variable Costs) ÷ Revenue

LTV/CAC Ratio = Lifetime Value ÷ Customer Acquisition Cost

Payback Period (months) = CAC ÷ (Monthly Revenue × Gross Margin %)

Gross Margin % = (Revenue - COGS) ÷ Revenue

Customer Lifetime (months) = 1 ÷ Monthly Churn Rate

MRR = Sum of all monthly subscriptions
ARR = MRR × 12
ARPU = Total Revenue ÷ Total Users
NRR = (Starting ARR + Expansion - Contraction - Churn) ÷ Starting ARR
```

## Benchmarks

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| **LTV/CAC Ratio** | ≥5:1 | 3:1 - 5:1 | <3:1 |
| **Payback Period** | <6 months | 6-12 months | >18 months |
| **Gross Margin (SaaS)** | ≥80% | 60-80% | <60% |
| **Gross Margin (E-commerce)** | ≥50% | 40-50% | <40% |
| **Monthly Churn (B2C SaaS)** | <3% | 3-7% | >7% |
| **Monthly Churn (B2B SaaS)** | <1% | 1-3% | >3% |
| **CAC Payback (SaaS)** | <12 months | 12-18 months | >18 months |
| **NRR (SaaS)** | ≥120% | 100-120% | <100% |

## Decision Framework

| LTV/CAC | Payback | Recommendation |
|---------|---------|----------------|
| <1:1 | Any | **Stop**: Теряем деньги на каждом клиенте. Фиксить модель или pivot. |
| 1:1 - 2:1 | >12 months | **Caution**: Маржинальная экономика. Не масштабировать. Улучшать retention или снижать CAC. |
| 2:1 - 3:1 | 6-12 months | **Optimize**: Экономика приемлема. Фокус на улучшении перед масштабом. |
| 3:1 - 5:1 | <12 months | **Scale**: Хорошая экономика. Можно прибыльно инвестировать в рост. |
| >5:1 | <6 months | **Aggressive scale**: Отличная экономика. Привлекать капитал, увеличивать расходы. |

## 5-шаговый пайплайн

### Шаг 1. Define the unit
Что анализируем? (Customer, product SKU, transaction, subscription).

### Шаг 2. Calculate CAC
Общепринятые затраты на привлечение (sales + marketing) ÷ новых клиентов.
Разбить по каналам (paid search, referral, content, organic).

### Шаг 3. Calculate LTV
Выручка за жизненный цикл минус переменные затраты.
Использовать cohort data для retention/churn.

### Шаг 4. Assess contribution margin
(Revenue - Variable Costs) ÷ Revenue.
Определить рычаги для улучшения margin.

### Шаг 5. Interpret and recommend
Оценить LTV/CAC, payback, cash efficiency.
Дать рекомендации: pricing, channels, growth.

## Pricing Strategy Playbook (из CFO Campbell)

### Принципы
1. **Ценообразование = стратегия**, не «затраты + прибыль»
2. **Value-Based Pricing**: цена = количественное выражение ценности
3. **Цена — главный рычаг роста**: ROI от оптимизации цены × 4 выше, чем от оптимизации привлечения
4. **Пересматривать цену каждые 3-6 месяцев**, не «установил и забыл»

### Чеклист ценового аудита
- [ ] Value metric выверен? (что получает клиент → линейно связано с ценой)
- [ ] Граница free/paid разумна?
- [ ] Что если +20% к цене? А -20%?
- [ ] Как конкуренты ценуют? Почему мы дороже/дешевле?
- [ ] Какие клиенты самые прибыльные? Можно ли найти больше таких?

### Методы ценообразования
| Метод | Когда | Как |
|---|---|---|
| **Van Westendorp** | B2C SaaS, массовый рынок | 4 вопроса: too cheap / bargain / expensive / too expensive |
| **Gabor-Granger** | Новый продукт, мало данных | Тестируем 5 ценовых точек, ищем оптимум |
| **A/B тест** | Есть трафик, можем рандомизировать | Две цены → конверсия × выручка |
| **Value Metric** | Usage-based pricing | Цена за единицу ценности (seats, API calls, storage) |

### Tier-структура (SaaS)
```
Free → Pro → Enterprise
```
- **Free**: time-to-value < 7 дней, конверсия ≥2%
- **Pro**: основной продукт, 80% пользователей
- **Enterprise**: кастомные SLA, ACV ≥$10k

## Шаблоны под наши продукты

### Snapog tier-экономика ($0/$19/$49)
```
Tier      | Price | Target        | Value Metric
----------|-------|---------------|---------------------------
Free      | $0    | Lead gen      | 10 OG-images/month
Pro       | $19   | Indie hackers | 500 OG-images/month
Enterprise| $49   | Agencies      | Unlimited + API access
```

**Расчёт экономики (пример):**
- CAC (Pro): $30 (content + paid)
- ARPU: $19/month
- Gross margin: 85% (Supabase + Vercel costs)
- Churn: 5% monthly → Lifetime = 20 months
- LTV: $19 × 20 × 85% = $323
- LTV/CAC: $323 / $30 = 10.8:1 ✅
- Payback: $30 / ($19 × 85%) = 1.9 months ✅

### Kwork-воронка (socialmos, этап 2)
```
Продукт               | Цена   | Сегмент
-----------------------|--------|------------------
Аудит сообщества       | 3,000₽ | Все
Настройка меню         | 5,000₽ | Блогер/бизнес
Настройка рассыльщика  | 7,000₽ | Бизнес
Настройка бота         | 10,000₽| Бизнес/компания
```

**Юнит-экономика Kwork-заказа:**
- Средний чек: 6,250₽
- Затраты времени: 3-5 часов
- Часовая ставка: 1,250-2,080₽/ч (выше якоря 1,500₽/ч ✅)
- Повторные продажи: 30% клиентов берут следующий продукт

## Guardrails (КРИТИЧНО)

1. **Fully-loaded CAC**: ВСЕ затраты на привлечение (зарплаты, инструменты, накладные). Недооценка CAC = ложная картина.
2. **True variable costs**: Только то, что масштабируется с каждой единицей (COGS, hosting per user, transaction fees). НЕ включаем фиксированные (rent, core engineering).
3. **Cohort-based LTV**: Не усреднять по всем клиентам. Ранние когорты ≠ поздние. Использовать observed retention, не предположения.
4. **Time horizon matters**: LTV = прогноз. Консервативные предположения. Для новых продуктов — ненадёжно.
5. **Payback vs LTV/CAC**: Оба важны. Высокий LTV/CAC, но долгий payback (>18 мес) напрягает кэш.
6. **Channel-level analysis**: Blended metrics прячут правду. CAC и LTV варьируются по каналам.
7. **Retention is king**: Малые изменения churn → экспоненциальное влияние на LTV. Снизить churn с 5% до 4% → LTV +25%.
8. **Gross margin floor**: ≥60% для SaaS, ≥40% для e-commerce. Низкий margin = даже высокий LTV/CAC даёт слабый cash flow.

## Частые ошибки (Anti-patterns)

- ❌ **Ignoring churn**: Предполагаем, что клиенты остаются навсегда. Реальность: churn компаундится.
- ❌ **Vanity LTV**: Нереалистичный retention (5 лет при 1 месяце данных).
- ❌ **Blended CAC**: Смешиваем прибыльные и убыточные каналы.
- ❌ **Not updating**: Экономика меняется с продуктом, рынком, конкуренцией. Пересчитывать ежеквартально.
- ❌ **Missing costs**: Забываем support costs, payment processing, fraud, refunds.
- ❌ **Premature scaling**: Рост до того, как экономика заработала (LTV/CAC <2:1).

## Формат вывода (обязательный)

```
## Финансовый вердикт
[ПРИБЫЛЬНО / УБЫТОЧНО / МАРЖИНАЛЬНО] + одно предложение.

## Ключевые метрики
| Метрика | Значение | Бенчмарк | Статус |
|---------|----------|----------|--------|
| LTV/CAC | X:1 | ≥3:1 | ✅/⚠️/❌ |
| Payback | X мес | <12 мес | ✅/⚠️/❌ |
| Gross Margin | X% | ≥60%/40% | ✅/⚠️/❌ |
| Churn | X%/мес | <3%/7% | ✅/⚠️/❌ |

## Расчёты
[Формулы + подстановка + результат]

## Сравнение с конкурентами (если применимо)
| Метрика | Мы | Comp A | Comp B |
|---------|-----|--------|--------|
| Price | $X | $X | $X |
| LTV/CAC | X:1 | X:1 | X:1 |

## Риски
- ...

## Рекомендации
1. ...
2. ...

## Документы
- projects/sinergy/docs/cfo/<slug>.md (или docs/cfo/<slug>.md)
```

## Привязка к задачам

- **T-03** (регистратор): Финансист берёт этот скилл для ценовых/финмодельных задач
- **ES-N** (экспертные боты): паттерн ложится на многоагентную дискуссию
- **AI-Scout expert analysis**: unit-economics как fallback для `expert_analysis`
- **Kwork-воронка (socialmos)**: pricing + unit-economics для этапа 2
- **Snapog**: tier-экономика $0/$19/$49 → MRR/ARPU/churn

## Примечания

- Названия агентов — наши профили (`sherlock/femida/defender/marketer/financier/health`), **не** `.claude/agents/*` из Auto-Company
- Выход: `projects/sinergy/docs/cfo/` или `docs/cfo/`, не `docs/cfo/` из Auto-Company
- Структура `SKILL.md` — по канону Hermes (`---` frontmatter + `name`/`description` + `argument-hint` + `disable-model-invocation`)
- Китайский текст из cfo-campbell убран; нотация адаптирована под ru
- Примеры с Cloudflare/AWS заменены на наш стек (Supabase, Vercel, TimeWeb)
