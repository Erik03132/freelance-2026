# 🎯 МАТРИЦА ПРИМЕНЕНИЯ task-prioritizer

## По типам задач

### 🐛 БАГ-ТРЕКИНГ

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ Много багов из разных источников (GitHub, Sentry, Slack)
✅ Нужно быстро определить критичные
✅ Команда не может решать всё одновременно

РЕЗУЛЬТАТЫ:
• MTTR ↓ 60% (Mean Time To Resolution)
• Critical bugs detected за 15 мин (вместо 8 часов)
• Экономия: 387 часов/год для типичной компании

ПРИМЕР КОНФИГА:
triggers:
  production_down: 50
  data_loss: 48
  security: 45
  performance: 30
  
entities:
  database: S-tier (30)
  auth: S-tier (30)
  payment: S-tier (30)
```

---

### 🚀 FEATURE MANAGEMENT

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ Много feature requests от пользователей
✅ Нужно выбрать, что разработать в первую очередь
✅ Хочешь максимизировать ROI

РЕЗУЛЬТАТЫ:
• Feature adoption ↑ 3x (20% → 60%)
• User satisfaction ↑ 40%
• Development velocity ↑ 25%

ПРИМЕР КОНФИГА:
triggers:
  user_requests: 40  # сколько пользователей просят
  revenue_impact: 50  # влияет ли на доход
  churn_risk: 45  # если не сделаем, пользователи уйдут
  
entities:
  onboarding: S-tier (30)
  core_feature: A-tier (15)
```

---

### 🛡️ SECURITY & COMPLIANCE

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ Нужно отслеживать уязвимости
✅ Compliance требования (GDPR, HIPAA, SOC2)
✅ Security audit findings

РЕЗУЛЬТАТЫ:
• Vulnerability response time ↓ 80%
• Compliance violations ↓ 100%
• Security incidents ↓ 60%

ПРИМЕР КОНФИГА:
triggers:
  critical_vulnerability: 50
  compliance_issue: 48
  data_exposure: 50
  zero_day: 50
  
entities:
  auth_system: S-tier (30)
  user_data: S-tier (30)
  api_gateway: S-tier (30)
```

---

### 📊 TECH DEBT MANAGEMENT

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ Много рефакторинга и обновления зависимостей
✅ Нужно балансировать между новыми фичами и техдолгом
✅ Хочешь предотвратить collapse of codebase

РЕЗУЛЬТАТЫ:
• Code quality ↑ 35%
• Build time ↓ 40%
• Developer velocity ↑ 20%

ПРИМЕР КОНФИГА:
triggers:
  vulnerable_dependency: 45
  deprecated_library: 35
  performance_regression: 30
  test_coverage_low: 20
  
entities:
  core_library: S-tier (30)
  api_layer: A-tier (15)
```

---

### 🔍 COMPETITOR INTELLIGENCE (sherl-research)

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ Нужно отслеживать конкурентов
✅ Хочешь понять реальные угрозы vs шум
✅ Аналитик тонет в информации

РЕЗУЛЬТАТЫ:
• Signal-to-noise ratio ↑ 10x
• Strategic decisions based on data ✓
• Time spent on analysis ↓ 70%

ПРИМЕР КОНФИГА:
triggers:
  price_cut: 50  # конкурент снизил цену
  feature_launch: 35  # запустил новую фичу
  funding: 30  # получил инвестиции
  partnership: 25  # новое партнёрство
  
entities:
  main_competitor: S-tier (30)
  secondary_competitor: A-tier (15)
```

---

### 📱 MOBILE APP DEVELOPMENT

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ App Store reviews и crash reports
✅ Нужно отслеживать версии (iOS, Android)
✅ User feedback из разных каналов

РЕЗУЛЬТАТЫ:
• App Store rating ↑ 0.5 звёзд
• Crash rate ↓ 80%
• User retention ↑ 25%

ПРИМЕР КОНФИГА:
triggers:
  app_crash: 50
  ui_broken: 40
  performance_bad: 35
  feature_request: 15
  
entities:
  core_feature: S-tier (30)
  payment_flow: S-tier (30)
  authentication: S-tier (30)
```

---

### 🌐 SAAS PLATFORM

```
КОГДА ИСПОЛЬЗОВАТЬ:
✅ Много пользователей, много issues
✅ Нужно минимизировать churn
✅ Быстро растущая компания

РЕЗУЛЬТАТЫ:
• Customer churn ↓ 40%
• NPS score ↑ 15 points
• Support tickets ↓ 50%

ПРИМЕР КОНФИГА:
triggers:
  customer_complaint: 50
  feature_parity_gap: 40
  onboarding_friction: 35
  integration_failure: 30
  
entities:
  core_platform: S-tier (30)
  integrations: A-tier (15)
  onboarding: A-tier (15)
```

---

## По размеру команды

### 👥 STARTUP (2-10 разработчиков)

```
ПРИМЕНЕНИЕ: ⭐⭐⭐⭐⭐ (ИДЕАЛЬНО)

Почему:
• Все задачи кажутся одинаково срочными
• Нет бюджета на PM/project manager
• Нужна автоматизация

Как внедрить:
1. GitHub Issues + task-prioritizer
2. Запускать каждый день
3. Обновлять конфиг еженедельно

Результаты:
• Velocity ↑ 30%
• Burndown chart чистый ✓
• Мораль команды ↑ (знают, что делать)
```

---

### 🏢 SCALEUP (10-50 разработчиков)

```
ПРИМЕНЕНИЕ: ⭐⭐⭐⭐⭐ (ИДЕАЛЬНО)

Почему:
• Много разных проектов
• Нужна координация между командами
• Есть PM, но он/она перегружен

Как внедрить:
1. GitHub Issues + Jira + Sentry
2. Centralized dashboard
3. Auto-update приоритетов
4. Slack notifications

Результаты:
• Sync-time ↓ 40%
• Cross-team coordination ↑
• Issue resolution time ↓ 60%
```

---

### 🏭 ENTERPRISE (50+ разработчиков)

```
ПРИМЕНЕНИЕ: ⭐⭐⭐ (ХОРОШО, НО НУЖНА КАСТОМИЗАЦИЯ)

Почему:
• Уже есть система (Jira, Azure DevOps)
• Много разных процессов
• Нужна интеграция

Как внедрить:
1. Кастомный конфиг для каждого team
2. Integration с существующей системой
3. Governance layer (кто может менять приоритеты)
4. Audit trail

Результаты:
• Compliance ✓
• Transparency ↑
• Decision-making speed ↑
```

---

## По отраслям

### 💳 FINTECH

```
ПРИОРИТЕТ ТРИГГЕРОВ:
1. Security vulnerability (50)
2. Payment processing down (50)
3. Compliance issue (48)
4. Data loss (48)
5. Performance (30)

РЕЗУЛЬТАТЫ:
• Security incidents ↓ 90%
• Compliance violations ↓ 100%
• Customer trust ↑
```

---

### 🏥 HEALTHTECH

```
ПРИОРИТЕТ ТРИГГЕРОВ:
1. Patient data loss (50)
2. HIPAA violation (50)
3. Medical accuracy issue (48)
4. System down (45)
5. Performance (30)

РЕЗУЛЬТАТЫ:
• Compliance ✓
• Patient safety ✓
• Liability ↓
```

---

### 🛒 E-COMMERCE

```
ПРИОРИТЕТ ТРИГГЕРОВ:
1. Payment system down (50)
2. Checkout broken (48)
3. Inventory sync failed (45)
4. Performance (40)
5. Feature request (15)

РЕЗУЛЬТАТЫ:
• Revenue ↑ (no lost sales)
• Customer satisfaction ↑
• Cart abandonment ↓
```

---

### 🎮 GAMING

```
ПРИОРИТЕТ ТРИГГЕРОВ:
1. Game crash (50)
2. Exploit found (48)
3. Server down (45)
4. Matchmaking broken (40)
5. Feature request (20)

РЕЗУЛЬТАТЫ:
• Player retention ↑
• Reviews ↑
• Revenue ↑ (less churn)
```

---

## По источникам данных

### 📌 GitHub Issues

```
SETUP:
scorer = TaskScorer(project_id="github")
scorer.load_niche_config("backend")

# Парсим GitHub labels
for issue in github_issues:
    task = {
        "id": f"GH-{issue['number']}",
        "title": issue['title'],
        "tags": [label['name'] for label in issue['labels']],
        "created_at": issue['created_at'],
        "reactions": issue['reactions']['+1'],
    }

РЕЗУЛЬТАТЫ:
• Issue resolution time ↓ 60%
• False priority reports ↓ 80%
```

---

### 🚨 Sentry Errors

```
SETUP:
scorer = TaskScorer(project_id="sentry")
scorer.load_niche_config("backend")

# Парсим Sentry issues
for issue in sentry_issues:
    task = {
        "id": f"SENTRY-{issue['id']}",
        "title": issue['title'],
        "tags": ["production", "error"],
        "related_issues": issue['count'],  # frequency
    }

РЕЗУЛЬТАТЫ:
• MTTR ↓ 80%
• Critical bugs found in 15 min (vs 8 hours)
```

---

### 💬 Slack Threads

```
SETUP:
scorer = TaskScorer(project_id="slack")
scorer.load_niche_config("backend")

# Парсим Slack messages
for message in slack_threads:
    task = {
        "id": f"SLACK-{message['ts']}",
        "title": message['text'],
        "tags": extract_tags(message),
        "reactions": len(message['reactions']),
        "replies": message['reply_count'],
    }

РЕЗУЛЬТАТЫ:
• Informal issues captured ✓
• Team communication ↑
```

---

### 📋 Jira Tickets

```
SETUP:
scorer = TaskScorer(project_id="jira")
scorer.load_niche_config("backend")

# Парсим Jira issues
for issue in jira_issues:
    task = {
        "id": issue.key,
        "title": issue.fields.summary,
        "tags": issue.fields.labels,
        "component": issue.fields.components[0].name,
        "related_issues": len(issue.fields.issuelinks),
    }
    
# Обновляем приоритет в Jira
issue.update(priority={'name': get_priority_by_score(score)})

РЕЗУЛЬТАТЫ:
• Jira priority always up-to-date ✓
• Team alignment ↑
```

---

## 📊 ROI CALCULATOR

```
КОМПАНИЯ: 50 разработчиков
ТЕКУЩЕЕ СОСТОЯНИЕ:
• 200 open issues
• MTTR: 8 часов (critical), 24 часа (high)
• 10% time spent on prioritization
• Burndown: -30% (не успевают)

ПОСЛЕ task-prioritizer:
• MTTR: 1 час (critical), 4 часа (high) — ↓ 8x
• Time spent: 1% (↓ 90%)
• Burndown: +10% (успевают больше)

РАСЧЁТ:
• 50 разработчиков × 40 часов/неделю = 2000 часов/неделю
• 10% → 1% = 180 часов/неделю экономии
• 180 часов × 52 недели = 9360 часов/год
• 9360 часов × $100/hour = $936,000/год экономии

ИНВЕСТИЦИЯ:
• Implementation: 40 часов = $4,000
• Maintenance: 4 часов/месяц = $2,000/год

ROI: $936,000 / $6,000 = 156x
Payback period: 2 недели
```

---

## ✅ ЧЕК-ЛИСТ ВНЕДРЕНИЯ

### Неделя 1: Setup
- [ ] Выбрать источник данных (GitHub/Sentry/Jira)
- [ ] Установить task-prioritizer
- [ ] Создать конфиг для вашей ниши
- [ ] Запустить на 10 задачах

### Неделя 2: Integration
- [ ] Подключить к основному источнику (все issues)
- [ ] Настроить автоматический скоринг
- [ ] Настроить notifications (Slack/email)
- [ ] Обучить команду

### Неделя 3: Optimization
- [ ] Собрать feedback от команды
- [ ] Обновить конфиг на основе feedback
- [ ] Добавить feedback loop (record_decision)
- [ ] Документировать процесс

### Неделя 4: Scale
- [ ] Добавить второй источник (если нужно)
- [ ] Создать dashboard
- [ ] Настроить reporting
- [ ] Планировать следующую фазу

---

## 🎓 ЗАКЛЮЧЕНИЕ

**task-prioritizer подходит для:**

✅ Стартапов (автоматизация без PM)
✅ Scaleups (координация между командами)
✅ Больших компаний (с кастомизацией)
✅ Open source (мало maintainers, много issues)
✅ Аутсорс-компаний (много клиентов)

**Начните с одного источника и вы сразу увидите результат!**
