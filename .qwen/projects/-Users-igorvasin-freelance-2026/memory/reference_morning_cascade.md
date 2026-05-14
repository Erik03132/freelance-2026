---
name: Morning Report Cascade — каскад + страховка
description: 02:00 аудит → 03:00 транскрибация → 08:00 отчёт (PM2 + cron-страховка)
type: reference
---

**Расписание (MSK):**

| Время | Задача | Скрипт | Страховка |
|-------|--------|--------|-----------|
| 02:00 | Ночной аудит кода | `night_audit_vps.sh` | 02:01 cron |
| 03:00 | Транскрибация звонков | `call_transcriber.py` | 03:01 cron |
| 08:00 | Объединённый отчёт | `unified_morning_report.py` | 08:01 cron |

**Страховка:** Cron проверяет наличие файлов-маркеров и запускает задачи если PM2 scheduler не сработал.

**Файл:** `ai-eggs/docs/MORNING_REPORT_CASCADE.md`
