---
name: CEO Report использует bitrix_scanner
description: Железное правило — CEO Report получает данные ТОЛЬКО из bitrix_scanner.py, никогда напрямую из API
type: feedback
---

**Правило:** `ceo_report.py` получает данные ИСКЛЮЧИТЕЛЬНО через `bitrix_scanner.py`. Никогда не дёргать Bitrix API напрямую!

**Why:** 14.05.2026 обнаружено, что прямые API вызовы (`crm.deal.list`, `voximplant.statistic.get`) не возвращают:
- UF_CRM поля (оплаты 1С, номера заказов, адреса доставки)
- Товарные строки (породы, количество, цены)
- Забытые сделки (требуется DATE_MODIFY + фильтрация стадий)
- Лиды с источниками (SOURCE_ID)
- Воронку по стадиям (STAGE_ID, STAGE_NAME)

**How to apply:**
```python
# 🔴 ЖЕЛЕЗНОЕ ПРАВИЛО в ceo_report.py:
from bitrix_scanner import run_scan  # или subprocess.run

scan = run_bitrix_scanner()  # Запускаем сканер
deals = scan["deals"]["items"]  # Полные данные с UF_CRM
leads = scan["leads"]["items"]  # С источниками
payments = scan["payments"]  # Оплаты 1С
forgotten = get_forgotten_deals(scan["deals"]["items"])  # Активные стадии + DATE_MODIFY > 3 дней
```

**Файл:** `ai-eggs/agent/ceo_report.py` — использует `run_bitrix_scanner()` через subprocess.
