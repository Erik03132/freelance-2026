# 📐 DOCUMENT GOVERNANCE — Управление документами Antigravity
# Формализовано: 01.05.2026 (из аудита 30.04.2026)
# ОБЯЗАТЕЛЬНО для всех агентов при создании/редактировании файлов

---

## Правило 1: Single Source of Truth (SSoT)

```
Каждой теме — ОДИН файл.
Нет файла по теме — создать.
Есть файл по теме — ДОПОЛНИТЬ, не создавать новый.
```

**Перед созданием нового MD-файла, ответь на вопросы:**

1. Существует ли уже файл с похожей темой? → `grep` по названию
2. Это временная заметка? → пиши в `chp.md`, не в файл
3. Это статус проекта? → обновляй `PROJECT.md`
4. Это задача? → пиши в `ACTIVE_TASKS.md`
5. Это план/дорожная карта? → обновляй `ROADMAP.md`
6. Только если НИ ОДИН файл не подходит → создавай новый

---

## Правило 2: Иерархия документов по типу

```
📁 project/
├── PROJECT.md          ← Всё о проекте (1 файл!)
│   ├── Overview
│   ├── Current Status  ← сюда STATUS.md
│   ├── Agent Config
│   └── Architecture
├── ROADMAP.md          ← Единая дорожная карта (1 файл!)
│   ├── Done
│   ├── In Progress
│   └── Backlog
├── data/               ← Только данные агента (не трогать)
└── logs/               ← Логи (не трогать)
```

---

## Правило 3: Запрещённые типы файлов

| Запрещённый тип | Куда вместо |
|----------------|------------|
| `DAILY_PLAN_*.md` | → Задача в `chp.md` |
| `SESSION_HANDOVER*.md` | → Секция в `chp.md` |
| `STATUS_*.md` | → Секция в `PROJECT.md` |
| `TODO.md` | → Задача в `ACTIVE_TASKS.md` |
| `*_V2.md`, `*_NEW.md` | → Обновить оригинал! |
| Файлы в `tmp/` | → Удалить после сессии |

---

## Правило 4: TTL (Time To Live)

| Тип документа | TTL | Действие |
|--------------|-----|----------|
| `DAILY_PLAN` | 1 день | Автоудаление |
| `SESSION_HANDOVER` | 3 дня | Архив |
| `STATUS.md` | 7 дней | Влить в PROJECT.md |
| `ROADMAP.md` | 30 дней | Ревью |
| Данные агента (`data/`) | ∞ | Не удалять |

---

## Правило 5: Merge-группы (текущие задолженности)

Эти файлы должны быть объединены при следующей возможности:

### Группа: Роадмапы ai-eggs → `UNIFIED_ROADMAP.md`
- `BITRIX_ROADMAP.md` → секция "Bitrix"
- `PHASE_1_DETAILED_ROADMAP.md` → секция "Phase History"
- `IMPROVEMENTS.md` → секция "Backlog"
- `INCUBIRD_AUDIT_CHECKLIST.md` → секция "Audit"

### Группа: VK → `VK_EXPANSION_STRATEGY.md`
- `VK_INCUBATOR_KNOWLEDGE.md` → секция "Знания Инкубатора"
- `VK_MARKET_RESEARCH.md` → секция "Исследование"
- `VK_READY_TEXTS.md` → секция "Готовые тексты"
- `VK_ACTION_PLAN.md` → секция "Пошаговый план"

### Группа: Аудиты → `TECHNICAL_AUDIT_REPORT.md`
- `FINAL_BUSINESS_AUDIT_REPORT.md`
- `MASTER_CHECKLIST.md`
- `DEBUG_PROTOCOLS.md`
