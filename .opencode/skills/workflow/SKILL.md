---
name: workflow
description: Development workflow — Plan First, TDD, 5-axis Code Review, AI Agent Security, OWASP, Conventional Commits, finish-day protocol, session lifecycle.
---

## Feature Implementation Workflow
```
Plan First → TDD → Code Review → Commit
```

## 0. Search-First (обязательный каскад)
```
1️⃣ СВОИ СКИЛЛЫ — загрузи релевантный skill через tool
2️⃣ GITHUB / NPM — поиск рабочих библиотек
3️⃣ СВОЯ ГОЛОВА — только если 1️⃣ и 2️⃣ не дали результата
```

## 1. Plan First
- Декомпозиция задач, критерии завершения ДО начала
- Каждый юнит: верифицируемый, с одним доминирующим риском

## 2. TDD
- RED → GREEN → IMPROVE, 80%+ coverage, AAA Pattern

## 3. Code Review (5 осей)
- **Correctness** — edge cases, error paths
- **Readability** — имена, управляющий поток
- **Architecture** — паттерны, границы, DRY, циклические зависимости
- **Security** — AI Agent Security (Prompt Injection, Guardrails, Output Validation) + OWASP Top 10 + Secrets Management
- **Performance** — N+1, неограниченные циклы, пагинация

## Управление сессиями
### Старт
1. Прочитай: AGENTS.md + CHRONICLE.md (конец) + chp.md
2. Проверь: git status, npm run build/dev
3. Загрузи нужный skill через tool

### Завершение (finish-day) — Global (OpenCode)
1. **Git:** git status → коммит → пуш
2. **CHRONICLE.md:** допиши сессию, обнови секции
3. **Финал:** npm run build — не сломана?

### Завершение (finish-day) — Antigravity (project-level)
```bash
cd /Users/igorvasin/freelance-2026/freelance-agent/.agent/agents
# Self-improvement hook
python3 -m learning capture_outcome --agent $(current_agent) --outcome accepted
python3 -m memory compact $(current_agent)
python3 -m soul fold $(current_agent) "$(lesson_from_session)"

# Diff check
git status

# Auto-document checkpoint
cat > .agent/knowledge/daily_checkpoint_$(date +%Y%m%d).md << 'EOF'
# Daily Checkpoint $(date +%Y-%m-%d)

## Completed
- 

## Open Issues
- 

## Dependencies Changed
- 

## Context for Next Session
- 
EOF

# Cleanup & commit
rm -rf ./scratch/* 2>/dev/null
git add -A
git commit -m "chore: daily checkpoint $(date +%Y-%m-%d)"
git push

echo "Day finished successfully! Session checkpoint created."
```
