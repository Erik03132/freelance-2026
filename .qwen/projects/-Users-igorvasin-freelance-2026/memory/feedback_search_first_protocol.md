---
name: SEARCH-FIRST PROTOCOL — железное правило
description: Обязательный каскад решений перед ЛЮБОЙ задачей: скиллы → GitHub → своя голова
type: feedback
---

**Правило:** Перед тем как писать код или решать техническую проблему — ОБЯЗАТЕЛЬНЫЙ каскад:

```
┌──────────────────────────────────────────────┐
│  1️⃣  СВОИ СКИЛЛЫ                             │
│     grep/find по skills/ и knowledge/        │
│     Если решение найдено → ИСПОЛЬЗОВАТЬ      │
│                                              │
│  2️⃣  GITHUB                                  │
│     Поиск рабочих библиотек и примеров       │
│     Если нашёл → адаптировать                │
│                                              │
│  3️⃣  СВОЯ ГОЛОВА                             │
│     Только если 1️⃣ и 2️⃣ не дали результата   │
│     Писать собственное решение               │
└──────────────────────────────────────────────┘
```

**Why:** 03.05.2026 добавлено в IRON_RULES.md §6. Нарушение = агент тратит 20+ минут на изобретение решения, которое УЖЕ есть в скиллах — это **ГРУБАЯ ОШИБКА**.

**How to apply:**
- **Шаг 1:** `grep -r "pattern_name" /Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/*/SKILL.md`
- **Шаг 2:** Поиск на GitHub (если есть доступ)
- **Шаг 3:** Только если 1 и 2 не дали → писать своё

**Где искать скиллы:**
| Тип | Путь |
|-----|------|
| Глобальные | `~/.gemini/antigravity/skills/*/SKILL.md` |
| Проектные | `/Users/igorvasin/freelance-2026/freelance-agent/.agent/skills/*/SKILL.md` |
| ai-eggs | `/Users/igorvasin/freelance-2026/ai-eggs/.agent/skills/*/SKILL.md` |
| Knowledge Items | `~/.gemini/antigravity/knowledge/*/` |

**Файл:** `.agent/rules/IRON_RULES.md` (раздел 6)
