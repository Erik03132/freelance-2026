# FCA AI Spotlight Observatory — 10 карточек для агента «Финансист» (27.11.2026)

**Источник:** [FCA AI Spotlight Observatory](https://ai-spotlight.fcainnovation.co.uk/) — официальная платформа FCA (пресс-релиз [19.11.2026](https://fca.org.uk/news/press-releases/fca-launches-world-first-platform-giving-firms-new-insight-ai-innovation)), созданная с CFTE и NayaOne: >200 организаций, 150 областей деятельности, таксономия «use case ≠ implementation». Публичные карточки доступны без регистрации; детальные данные (целевые клиенты, демо) — только после регистрации, без клиентских персданных не запрашивались.

**Метод (детерминированный, без LLM):** `curl --noproxy "*" -fsSL --max-time 20 <url>` (ADR-002: внешний ресурс, локальный прокси мёртв) + regex-извлечение `h1`, первого `p`, ссылок `/vendor_listing/`; описания приведены дословно на английском, маппинг на Финансиста — статический, заданный в запросе выгрузки. Никаких LLM-суммаризаций и выдуманных метрик.

| ID | Кейс FCA (дословно) | Описание (дословно) | Innovators | Маппинг на Финансиста |
|---|---|---|---|---|
| [FUC043](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc043-analyse-financial-results-and-earnings/fuc043-analyse-financial-results-and-earnings) | Analyse financial results and earnings | Summarise financial results and accelerate financial analysis, modelling or interpretation for finance professionals. | PwC UK | Финрезультаты: сценарий в tests/eval_financier.py |
| [FUC023](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc023-forecast-cash-flows-and-support-treasury-decisions/fuc023-forecast-cash-flows-and-support-treasury-decisions) | Forecast cash flows and support treasury decisions | Forecast cash flows, liquidity or treasury needs and support cash-management decisions. | — | Кэш-флоу и treasury: сценарий в eval_financier.py |
| [FUC011](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc011-assess-affordability-and-income-and-expenditure/fuc011-assess-affordability-and-income-and-expenditure) | Assess affordability and income and expenditure | Capture, verify and assess income, expenditure and other affordability information, including indicators of vulnerability or support needs. | — | Доступность и расходы: сценарий + тема bias/fairness |
| [FUC059](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc059-validate-stress-test-and-monitor-ai-models/fuc059-validate-stress-test-and-monitor-ai-models) | Validate, stress-test and monitor AI models | Test and monitor AI models for uncertainty, drift, bias, safety, robustness, adversarial vulnerabilities and compliance before and after deployment. | Advai, RevAIsor | Стресс-тест моделей: сценарий + гардрейд payback >18 мес |
| [FUC019](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc019-generate-investment-research-and-ideas/fuc019-generate-investment-research-and-ideas) | Generate investment research and ideas | Retrieve and analyse market, company and portfolio information to support research, alerts, theme discovery and investment idea generation. | — | Исследования: сценарий Stop + граница «не инвестконсультация» |
| [FUC044](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc044-retrieve-internal-knowledge-and-answer-questions/fuc044-retrieve-internal-knowledge-and-answer-questions) | Retrieve internal knowledge and answer questions | Retrieve and synthesise trusted internal information so employees, advisers or agents can answer questions and complete work faster. | — | Внутренние знания: сценарий zero-churn → горизонт 36 мес |
| [FUC016](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc016-support-investment-strategy-and-decisions/fuc016-support-investment-strategy-and-decisions) | Support investment strategy and decisions | Use models and analytics to support security selection, strategy design or investment decision-making. | — | Инвестстратегия: только внутренние сценарии, human-gate |
| [FUC008](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc008-provide-personal-financial-guidance-and-money-management/fuc008-provide-personal-financial-guidance-and-money-management) | Provide personal financial guidance and money management | Analyse personal finances and circumstances to provide budgeting, savings, pension or behavioural guidance and help customers take action. | Complex Customer Service Agent, Engage Smarter, INATIGO, Planda, Sopra Steria | Фин-гайденс: граница FCA-2, обезличенные данные |
| [FUC041](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc041-detect-market-abuse-and-conduct-risk/fuc041-detect-market-abuse-and-conduct-risk) | Detect market abuse and conduct risk | Monitor trading or investment activity to detect market abuse, conduct or consumer-duty issues and prioritise alerts for review. | VIGIL from Pytilia | Мониторинг market abuse: без рекомендаций клиенту |
| [FUC037](https://ai-spotlight.fcainnovation.co.uk/use_case/fuc037-review-regulated-content-and-documents-for-compliance/fuc037-review-regulated-content-and-documents-for-compliance) | Review regulated content and documents for compliance | Review customer communications, marketing, trade documents or other regulated content against policies and regulatory requirements, flagging issues and retaining evidence. | Adclear, Amplified Global, Finspector | Compliance-ревью контента: human-gate, только внутренний usage |

## Что берём

- Таксономию FCA и формулировки кейсов — как источник сценариев для `tests/eval_financier.py` (FCA-1: 6 сценариев + 2 гардрейла, eval gate 20/20).
- Темы FCA (`bias-fairness`, `explainability-governance`, `data-quality`, `compliance-automation`) — как регистрационные атрибуты сценариев и границ
- Границу FCA-2: unit-economics — внутренние расчёты, не инвестиционная консультация; human-gate на деньги/цену/договор; только обезличенные данные.

## Что НЕ берём

- Сама платформа не является фичей агента: это каталог кейсов UK-регулятора, а не API, модель или пайплайн.
- Метрики ROI и имена клиентов в карточках не заявлены — выдумывать их запрещено.
- UK-регулирование не переносится напрямую на наши Kwork/IZ-задачи; для РФ-контекста нужна отдельная проверка.

## Ограничения выгрузки

- Снято 10 публичных карточек из ~65 доступных в обзоре; выборка сделана под unit-economics, кэш-флоу, доступность, стресс-тест, исследовательские и комплаенс-кейсы.
- Описания — короткие английские строки с сайта, без перевода и без LLM-обработки; при изменении сайта карточки надо снять заново.
