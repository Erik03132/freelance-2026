---
name: CEO Report данные из Битрикс24
description: Расширенный отчёт руководителю использует 62 права админского вебхука
type: reference
---

**Вебхук:** `https://incubird.bitrix24.ru/rest/42020/o74etj0a5dc7q79f/`
**Права:** 62 (админский, полный доступ к CRM, телефонии, задачам, сотрудникам)

**Критические данные (ежедневно):**
1. Пропущенные звонки — `voximplant.statistic.get` (filter[DIRECTION]=1, CALL_DURATION=0)
2. Сделки по менеджерам — `crm.deal.list` (группировка по ASSIGNED_BY_ID, STAGE_ID)
3. Конверсия лид→сделка — `crm.lead.list` + `crm.deal.list`

**Важные данные (еженедельно):**
4. Счета и оплаты — `crm.invoice.list` (дебиторская задолженность)
5. Эффективность менеджеров — `user.get` + `crm.deal` + `voximplant`
6. Тимменеджер — `timeman.report.list` (опоздания, ранние уходы)

**Дополнительно (по запросу):**
7. Товары/остатки — `catalog.product`
8. Встречи — `calendar.event.get`
9. Задачи — `tasks.task.list`
10. Живая лента — `log.get`

**Файл:** `angel-backend/ceo_report_data_sources.md` — полный список API endpoints
