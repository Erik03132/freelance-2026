# 📌 ЧТО ТАКОЕ ISSUE? Подробное объяснение

## Самое простое определение

**Issue** = это проблема, задача или идея, которую нужно решить в проекте.

Примеры:
- ❌ **Баг:** "При нажатии на кнопку появляется ошибка"
- ✨ **Фича:** "Добавить тёмный режим"
- 📝 **Улучшение:** "Переписать документацию"
- ❓ **Вопрос:** "Как использовать эту функцию?"

---

## Где живут issues?

Issues живут на **GitHub** (или других платформах типа GitLab, Jira, Bitbucket).

Это как **доска объявлений**, где все пишут:
- Что сломалось
- Что нужно добавить
- Что нужно улучшить

---

## Реальный пример

### Ты разработчик. Утро, понедельник.

Ты открываешь GitHub репозиторий своего проекта:

```
https://github.com/facebook/react/issues
```

Там ты видишь список:

```
1. GH-5432 — Fix: TypeError when using hooks with class components
   └─ Открыта: 3 дня назад
   └─ Labels: bug, critical
   └─ 12 комментариев
   └─ 5 реакций 👍

2. GH-5431 — Feature: Add support for async components
   └─ Открыта: 1 день назад
   └─ Labels: feature, enhancement
   └─ 3 комментария
   └─ 20 реакций 👍

3. GH-5430 — Docs: Update README with new examples
   └─ Открыта: 2 дня назад
   └─ Labels: documentation
   └─ 1 комментарий
   └─ 0 реакций

4. GH-5429 — Fix: Typo in error message
   └─ Открыта: 5 дней назад
   └─ Labels: bug, minor
   └─ 2 комментария
   └─ 1 реакция 👍
```

Каждая строка = **один issue**.

---

## Структура issue

Когда ты кликаешь на issue, ты видишь:

```
═══════════════════════════════════════════════════════════════════
Fix: TypeError when using hooks with class components
═══════════════════════════════════════════════════════════════════

Issue #5432 | Opened by @user123 | 3 days ago | 12 comments

LABELS: bug, critical, priority-high

DESCRIPTION:
────────────────────────────────────────────────────────────────────
When I use hooks inside a class component, I get:

TypeError: Cannot read property 'useState' of undefined

Steps to reproduce:
1. Create a class component
2. Try to use useState hook
3. See the error

Expected: Should work without errors
Actual: TypeError

Code example:
```javascript
class MyComponent extends React.Component {
  render() {
    const [count, setCount] = useState(0);  // ← ERROR HERE
    return <div>{count}</div>;
  }
}
```

COMMENTS:
────────────────────────────────────────────────────────────────────
@developer1: This is a known limitation. Hooks only work in functional components.
@user123: Oh, I didn't know that. Can we add a better error message?
@maintainer: Good idea. Let me check if we can improve the error message.

═══════════════════════════════════════════════════════════════════
```

---

## Типы issues

### 1. 🐛 BUG (Баг)

**Что:** Что-то сломалось, не работает как надо.

**Примеры:**
```
- "При нажатии на кнопку 'Сохранить' ничего не происходит"
- "На мобильном телефоне текст выходит за границы экрана"
- "API возвращает ошибку 500"
- "При загрузке большого файла приложение зависает"
```

**Как выглядит:**
```
Title: Fix: "Save" button doesn't work on mobile
Labels: bug, mobile, critical
Description:
- When I click "Save" on mobile, nothing happens
- Expected: Data should be saved
- Actual: No response, button doesn't react
```

---

### 2. ✨ FEATURE (Фича)

**Что:** Новая функция, которую нужно добавить.

**Примеры:**
```
- "Добавить тёмный режим"
- "Реализовать экспорт в PDF"
- "Добавить фильтр по датам"
- "Интегрировать с Google Drive"
```

**Как выглядит:**
```
Title: Feature: Add dark mode
Labels: feature, enhancement, ui
Description:
- Users want a dark mode option
- Should save preference in localStorage
- Apply to all pages
```

---

### 3. 📝 DOCUMENTATION (Документация)

**Что:** Нужно написать, обновить или улучшить документацию.

**Примеры:**
```
- "Написать гайд по установке"
- "Обновить README"
- "Добавить примеры использования API"
- "Исправить опечатки в документации"
```

**Как выглядит:**
```
Title: Docs: Add examples for useContext hook
Labels: documentation
Description:
- Current docs don't have examples for useContext
- Should include basic and advanced examples
- Add to docs/hooks/useContext.md
```

---

### 4. 🔧 REFACTOR (Рефакторинг)

**Что:** Нужно переписать код, чтобы он был лучше (но функция остаётся той же).

**Примеры:**
```
- "Переписать компонент Header с использованием hooks"
- "Разбить большой файл на несколько модулей"
- "Улучшить производительность поиска"
- "Удалить неиспользуемый код"
```

**Как выглядит:**
```
Title: Refactor: Convert class components to hooks
Labels: refactor, tech-debt
Description:
- Old class components are hard to maintain
- Should convert to functional components with hooks
- Will improve performance and code readability
```

---

### 5. ❓ QUESTION (Вопрос)

**Что:** Кто-то что-то не понимает и спрашивает.

**Примеры:**
```
- "Как установить зависимости?"
- "Почему мой код не работает?"
- "Какая разница между useState и useReducer?"
- "Как настроить TypeScript?"
```

**Как выглядит:**
```
Title: Question: How to use authentication?
Labels: question, help
Description:
- I'm trying to implement login
- How do I store the token?
- Should I use localStorage or cookies?
```

---

## Жизненный цикл issue

### Этап 1: ОТКРЫТ (Open)

```
Кто-то создал issue, проблема зарегистрирована.

Статус: 🟢 OPEN
```

### Этап 2: В ПРОЦЕССЕ (In Progress)

```
Разработчик начал работать над issue.

Статус: 🟡 IN PROGRESS
```

### Этап 3: ГОТОВО (Closed)

```
Разработчик решил проблему и закрыл issue.

Статус: 🔴 CLOSED
```

---

## Реальный пример: GitHub React Issues

Откройте: https://github.com/facebook/react/issues

Вы увидите:

```
OPEN ISSUES (Открытые):
────────────────────────────────────────────────────────────────────
1. #12345 — Fix: Memory leak in useEffect
   └─ Opened 1 week ago
   └─ Labels: bug, critical
   └─ 5 comments

2. #12346 — Feature: Add useAsync hook
   └─ Opened 3 days ago
   └─ Labels: feature, enhancement
   └─ 12 comments

3. #12347 — Docs: Add examples for Suspense
   └─ Opened 5 days ago
   └─ Labels: documentation
   └─ 2 comments

CLOSED ISSUES (Закрытые):
────────────────────────────────────────────────────────────────────
✅ #12340 — Fix: TypeError when using hooks (Closed 2 days ago)
✅ #12341 — Feature: Add support for async (Closed 1 day ago)
✅ #12342 — Refactor: Improve performance (Closed 3 days ago)
```

---

## Как это связано с task-prioritizer?

task-prioritizer **берёт все эти issues** и **ранжирует их по приоритету**.

```
БЫЛО (без task-prioritizer):
────────────────────────────────────────────────────────────────────
GitHub Issues (в порядке создания):
1. #12345 — Fix: Memory leak
2. #12346 — Feature: Add useAsync
3. #12347 — Docs: Add examples
4. #12340 — Fix: TypeError
...

❓ Что делать в первую очередь? 🤷


СТАЛО (с task-prioritizer):
────────────────────────────────────────────────────────────────────
GitHub Issues (отранжированы по приоритету):

🔴 КРИТИЧНО (100/100)
1. #12340 — Fix: TypeError (Production bug!)

🔴 КРИТИЧНО (95/100)
2. #12345 — Fix: Memory leak (Security issue!)

🟠 ВЫСОКИЙ (60/100)
3. #12346 — Feature: Add useAsync (Popular request)

🟢 НИЗКИЙ (20/100)
4. #12347 — Docs: Add examples (Can wait)

✅ ВЫВОД: Делай #12340 и #12345, потом #12346!
```

---

## Пример: Как создаётся issue

### Шаг 1: Разработчик обнаруживает проблему

```
"Ой, при нажатии на кнопку 'Сохранить' ничего не происходит!"
```

### Шаг 2: Открывает GitHub

```
https://github.com/myproject/myrepo/issues
```

### Шаг 3: Кликает "New Issue"

```
┌─────────────────────────────────────────────┐
│ New Issue                                   │
├─────────────────────────────────────────────┤
│ Title:                                      │
│ [Save button doesn't work on mobile]        │
│                                             │
│ Description:                                │
│ When I click "Save" on mobile, nothing      │
│ happens. Expected: Data should be saved.    │
│ Actual: No response.                        │
│                                             │
│ Labels:                                     │
│ [bug] [mobile] [critical]                   │
│                                             │
│ [Create Issue]                              │
└─────────────────────────────────────────────┘
```

### Шаг 4: Issue создан!

```
Issue #5432 — Fix: Save button doesn't work on mobile
Opened by @developer1 | 1 minute ago | 0 comments

Labels: bug, mobile, critical

Description:
When I click "Save" on mobile, nothing happens.
Expected: Data should be saved.
Actual: No response.
```

### Шаг 5: Другой разработчик видит issue

```
"О, это критичный баг! Нужно срочно исправить!"
```

### Шаг 6: Разработчик начинает работать

```
- Открывает код
- Находит проблему
- Исправляет баг
- Делает commit
- Создаёт Pull Request
```

### Шаг 7: Pull Request принят

```
Issue #5432 закрыт ✅
```

---

## Реальные примеры issues из популярных проектов

### React (facebook/react)

```
#12345 — Fix: Memory leak in useEffect
#12346 — Feature: Add useAsync hook
#12347 — Docs: Update hooks documentation
#12348 — Refactor: Improve performance
```

### Node.js (nodejs/node)

```
#42000 — Fix: Buffer overflow in crypto module
#42001 — Feature: Add native support for WebAssembly
#42002 — Docs: Add examples for streams
```

### Vue.js (vuejs/vue)

```
#10000 — Fix: v-model not working with custom components
#10001 — Feature: Add Composition API
#10002 — Docs: Add migration guide from Vue 2
```

---

## Как это выглядит в реальности?

### Вариант 1: Ты разработчик

**Утро:**
```
Открываю GitHub
Смотрю на issues
Вижу: "Fix: Database connection timeout" (КРИТИЧНО)
Начинаю работать
```

### Вариант 2: Ты менеджер

**На встречу с командой:**
```
"Вот приоритет на сегодня:
1. Fix: Database connection (критично, ДЕЛАЙ СЕЙЧАС)
2. Fix: API error (высокий, делай сегодня)
3. Feature: Add dark mode (низкий, в backlog)"
```

### Вариант 3: Ты аналитик

**Ежедневный отчёт:**
```
"За день:
- 2 критичных issue
- 1 высокоприоритетный
- 5 низкоприоритетных

Рекомендация: Сосредоточиться на критичных"
```

---

## Итог

**Issue** = это просто **задача/проблема в GitHub**.

Примеры:
- ❌ Баг: "Кнопка не работает"
- ✨ Фича: "Добавить тёмный режим"
- 📝 Документация: "Написать гайд"
- 🔧 Рефакторинг: "Переписать код"
- ❓ Вопрос: "Как это работает?"

**task-prioritizer** берёт все эти issues и **показывает, какие в первую очередь решать**.

Вместо: "Ладно, какой issue взять? Может #12345? Может #12346?"  
Теперь: "Вот TOP-3 issues, начинай с первого"

---

## Где ты видишь issues?

### GitHub (самый популярный)

```
https://github.com/facebook/react/issues
```

Откройте эту ссылку и вы увидите реальные issues из React!

### GitLab

```
https://gitlab.com/gitlab-org/gitlab/-/issues
```

### Jira (для компаний)

```
https://your-company.atlassian.net/browse/PROJ-123
```

### Bitbucket

```
https://bitbucket.org/your-team/your-repo/issues
```

---

## Быстрая аналогия

**Issue = письмо на доске объявлений**

```
📌 ДОСКА ОБЪЯВЛЕНИЙ (GitHub)
├─ 📌 "Кнопка сломана!" (BUG)
├─ 📌 "Добавьте тёмный режим!" (FEATURE)
├─ 📌 "Напишите документацию" (DOCUMENTATION)
├─ 📌 "Как это работает?" (QUESTION)
└─ 📌 "Переписать код" (REFACTOR)

task-prioritizer смотрит на все письма и говорит:
"Первое письмо (баг) = КРИТИЧНО
 Второе письмо (фича) = НИЗКИЙ ПРИОРИТЕТ"
```

---

**Теперь ты знаешь, что такое issue! 🎉**
