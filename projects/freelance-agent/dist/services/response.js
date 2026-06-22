"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ResponseGenerator = void 0;
/**
 * Генератор персонализированных ответов
 */
class ResponseGenerator {
    /**
     * Определить тип задачи по описанию
     */
    detectTaskType(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        if (text.includes('лекц') || text.includes('урок') || text.includes('обучен') || text.includes('курс')) {
            return 'lecture';
        }
        if (text.includes('код') || text.includes('разработ') || text.includes('сайт') || text.includes('react') || text.includes('api')) {
            return 'code';
        }
        if (text.includes('текст') || text.includes('стать') || text.includes('пост') || text.includes('копирайт')) {
            return 'text';
        }
        if (text.includes('дизайн') || text.includes('логотип') || text.includes('макет') || text.includes('figma')) {
            return 'design';
        }
        if (text.includes('парс') || text.includes('данные') || text.includes('scrap') || text.includes('баз') || text.includes('excel')) {
            return 'data';
        }
        return 'code'; // По умолчанию
    }
    /**
     * Сгенерировать ответ для заказчика
     */
    generate(job, skills) {
        const type = this.detectTaskType(job);
        switch (type) {
            case 'lecture':
                return this.generateLectureResponse(job, skills);
            case 'code':
                return this.generateCodeResponse(job, skills);
            case 'text':
                return this.generateTextResponse(job, skills);
            case 'design':
                return this.generateDesignResponse(job, skills);
            case 'data':
                return this.generateDataResponse(job, skills);
            default:
                return this.generateCodeResponse(job, skills);
        }
    }
    /**
     * Генерация ответа для учебных задач (лекции, курсы)
     */
    generateLectureResponse(job, skills) {
        const title = job.title.toLowerCase();
        // Определение темы и стиля
        let topic = 'тема';
        let style = 'академический';
        let tone = 'нейтральный';
        if (title.includes('fastapi') || title.includes('python') || title.includes('api')) {
            topic = 'FastAPI и авторизация';
            style = 'технический, с примерами кода';
            tone = 'профессиональный, но доступный';
        }
        if (title.includes('react') || title.includes('frontend')) {
            topic = 'React и современные подходы';
            style = 'практический, с живыми примерами';
            tone = 'дружелюбный, наставнический';
        }
        // Генерация фрагмента лекции
        const sample = this.generateLectureSample(topic, style);
        // Пояснение
        const explanation = `Я выбрал ${style} стиль изложения, потому что это позволяет:\n` +
            `• Быстро погрузиться в тему без лишней «воды»\n` +
            `• Показать практические примеры, которые можно сразу применить\n` +
            `• Сохранить баланс между теорией и практикой\n\n` +
            `В полной версии лекции я также затрону:\n` +
            `• Распространённые ошибки и как их избежать\n` +
            `• Best practices из реальной разработки\n` +
            `• Ответы на частые вопросы студентов`;
        return {
            type: 'lecture',
            subject: job.title,
            letter: `Здравствуйте!

Заинтересовала ваша задача: "${job.title}"

📚 Я специализируюсь на создании образовательного контента для разработчиков.
Мой подход — давать максимум практики с первого урока.

Ниже — пример того, как будет выглядеть ваша лекция:`,
            sample,
            explanation,
            nextSteps: [
                'Согласовать структуру и стиль изложения',
                'Подготовить полную версию лекции (60-90 минут)',
                'Добавить практические задания для студентов',
                'Записать видео-версию (опционально)'
            ]
        };
    }
    /**
     * Генерация фрагмента лекции
     */
    generateLectureSample(topic, style) {
        if (topic.includes('FastAPI')) {
            return `---
📖 ФРАГМЕНТ ЛЕКЦИИ: FastAPI и авторизация
---

## Введение

FastAPI — это современный фреймворк для создания API на Python. 
Сегодня мы разберём один из ключевых аспектов — авторизацию через JWT токены.

## Почему именно JWT?

Традиционная сессионная авторизация имеет недостатки:
• Сервер должен хранить состояние каждой сессии
• Масштабирование требует синхронизации между серверами
• Мобильные приложения работают с сессиями неудобно

JWT (JSON Web Token) решает эти проблемы:
✓ Токен содержит всю необходимую информацию
✓ Серверу не нужно хранить состояние
✓ Легко масштабировать горизонтально

## Пример реализации

` ``;
            python;
            from;
            fastapi;
            import FastAPI, {} from Depends, HTTPException;
            from;
            fastapi.security;
            import OAuth2PasswordBearer from jose;
            import JWTError, {} from jwt;
            app = (0, module_1.default)();
            oauth2_scheme = (0, module_2.default)(tokenUrl = "token");
            SECRET_KEY = "your-secret-key";
            ALGORITHM = "HS256";
            def;
            create_access_token(data, dict);
            encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm = ALGORITHM);
            return encoded_jwt;
            def;
            login(username, str, password, str);
            #;
            Проверка;
            учётных;
            данных;
            if (not)
                validate_user(username, password);
            raise;
            HTTPException(status_code = 401);
            #;
            Создание;
            токена;
            access_token = create_access_token(data = { "sub": username, "role": "user" });
            return { "access_token": access_token } `` `

---
[Это демонстрационный фрагмент. Полная лекция включает 5 разделов с практическими заданиями]
`;
        }
        // Универсальный шаблон
        return `---
📖 ФРАГМЕНТ ЛЕКЦИИ: ${topic}
---

## Введение в тему

${topic} — это важная часть современной разработки.
Давайте разберём ключевые концепции на практических примерах.

## Основные концепции

1. **Базовые принципы**
   - Понимание фундаментальных идей
   - Почему это работает именно так
   - Распространённые заблуждения

2. **Практическое применение**
   - Реальные примеры из проектов
   - Типичные сценарии использования
   - Что может пойти не так

3. **Best Practices**
   - Рекомендации от опытных разработчиков
   - Как избежать распространённых ошибок
   - Оптимизация и производительность

## Пример кода

\`\`\`python
# Практический пример
def main():
    # Инициализация
    setup()
    
    # Основная логика
    result = process()
    
    # Возврат результата
    return result
\`\`\`

---
[Это демонстрационный фрагмент. Полная лекция включает больше примеров и упражнений]
`;
    }
    /**
     * Генерация ответа для задач по коду
     */
    generateCodeResponse(job, skills) {
        const desc = job.description.toLowerCase();
        let architecture = '';
        let techStack = '';
        if (desc.includes('react')) {
            architecture = `
• Компонентный подход с разделением на контейнеры и презентационные компоненты
• Управление состоянием через React Context или Zustand
• Кастомные хуки для переиспользуемой логики`;
            techStack = 'React 18, TypeScript, Vite';
        }
        else if (desc.includes('api') || desc.includes('backend')) {
            architecture = `
• RESTful архитектура с чётким разделением маршрутов
• Middleware для обработки ошибок и валидации
• Слоистая архитектура (routes → controllers → services)`;
            techStack = 'Node.js, Express, TypeScript';
        }
        else {
            architecture = `
• Модульная структура с чётким разделением ответственности
• Обработка ошибок на всех уровнях
• Логирование и мониторинг`;
            techStack = 'JavaScript/TypeScript, современные инструменты';
        }
        return {
            type: 'code',
            subject: job.title,
            letter: `Здравствуйте!

Заинтересовала ваша задача: "${job.title}"

💻 Я готов приступить к разработке.
Мой подход — создавать чистый, поддерживаемый код с первого дня.`,
            sample: `---
🏗 АРХИТЕКТУРНОЕ РЕШЕНИЕ
---

Предлагаемая структура проекта:

${architecture}

Стек технологий: ${techStack}

Пример реализации ключевого модуля:

\`\`\`typescript
// Пример кода будет предоставлен после уточнения деталей ТЗ
// Обычно это 50-100 строк чистого, типизированного кода
\`\`\`

---
[Полное решение с кодом будет после согласования архитектуры]
`,
            explanation: `Я выбрал такой подход, потому что он:\n` +
                `• Позволяет быстро начать разработку без лишних абстракций\n` +
                `• Легко масштабируется при росте проекта\n` +
                `• Понятен другим разработчикам\n\n` +
                `Использую AI-инструменты (Stitch, Gemini) для ускорения разработки на 30-40%.`,
            nextSteps: [
                'Согласовать архитектуру и стек технологий',
                'Уточнить детали ТЗ (если есть вопросы)',
                'Приступить к реализации',
                'Предоставить промежуточный результат через 24 часа'
            ]
        };
    }
    /**
     * Генерация ответа для текстовых задач
     */
    generateTextResponse(job, skills) {
        return {
            type: 'text',
            subject: job.title,
            letter: `Здравствуйте!

Заинтересовала ваша задача: "${job.title}"

✍️ Я создаю тексты, которые работают на ваш бизнес.
Адаптирую стиль под вашу аудиторию и цели.`,
            sample: `---
📝 ПРИМЕР ТЕКСТА
---

[Здесь будет пример текста в нужном стиле]

Для создания качественного контента мне нужно уточнить:
• Целевую аудиторию
• Ключевые сообщения
• Tone of voice бренда

---
[Полный текст будет после согласования стиля]
`,
            explanation: `Мой подход к написанию текстов:\n` +
                `• Изучаю вашу аудиторию и конкурентов\n` +
                `• Адаптирую стиль под платформу публикации\n` +
                `• Использую проверенные копирайтерские формулы\n\n` +
                `Готов предоставить 2-3 варианта на выбор.`,
            nextSteps: [
                'Получить бриф с деталями задачи',
                'Изучить примеры желаемого стиля',
                'Подготовить черновик',
                'Внести правки (2 итерации включены)'
            ]
        };
    }
    /**
     * Генерация ответа для дизайн-задач
     */
    generateDesignResponse(job, skills) {
        return {
            type: 'design',
            subject: job.title,
            letter: `Здравствуйте!

Заинтересовала ваша задача: "${job.title}"

🎨 Я создаю дизайн, который решает бизнес-задачи.
Сочетаю эстетику с юзабилити.`,
            sample: `---
🎨 КОНЦЕПЦИЯ ДИЗАЙНА
---

Референсы и аналоги:
• [Подберу 3-5 релевантных примера]
• [Проанализирую сильные стороны]
• [Предложу уникальные решения]

Цветовая палитра:
• Основной цвет: [будет согласован]
• Дополнительные: [2-3 акцентных цвета]
• Фон и текст: [контрастные комбинации]

---
[Полный мудборд будет после обсуждения предпочтений]
`,
            explanation: `Мой процесс работы:\n` +
                `• Анализирую нишу и конкурентов\n` +
                `• Подбираю референсы под ваши задачи\n` +
                `• Создаю 2-3 концепции на выбор\n\n` +
                `Работаю в Figma, предоставляю исходники.`,
            nextSteps: [
                'Обсудить предпочтения по стилю',
                'Получить примеры того, что нравится',
                'Подготовить 2-3 концепции',
                'Внести правки (3 итерации включены)'
            ]
        };
    }
    /**
     * Генерация ответа для задач по данным
     */
    generateDataResponse(job, skills) {
        return {
            type: 'data',
            subject: job.title,
            letter: `Здравствуйте!

Заинтересовала ваша задача: "${job.title}"

📊 Я специализируюсь на работе с данными.
Автоматизирую рутину, обеспечиваю качество данных.`,
            sample: `---
📊 ПОДХОД К ОБРАБОТКЕ ДАННЫХ
---

План работ:
1. Анализ источника данных
2. Разработка парсера/скрипта
3. Валидация и очистка данных
4. Экспорт в нужном формате

Пример структуры выходных данных:

\`\`\`json
{
  "items": [
    {
      "id": "unique_id",
      "name": "Название",
      "value": "Значение",
      "timestamp": "2026-03-24T12:00:00Z"
    }
  ],
  "total": 100,
  "processed_at": "2026-03-24T12:00:00Z"
}
\`\`\`

---
[Полное решение будет после анализа источника]
`,
            explanation: `Использую современные инструменты:\n` +
                `• Python (BeautifulSoup, Scrapy, Playwright)\n` +
                `• Обработка ошибок и повторные попытки\n` +
                `• Логирование и мониторинг прогресса\n\n` +
                `Готов обеспечить обход блокировок (если нужно).`,
            nextSteps: [
                'Получить доступ к источнику данных',
                'Согласовать формат вывода',
                'Разработать и протестировать скрипт',
                'Передать данные и документацию'
            ]
        };
    }
}
exports.ResponseGenerator = ResponseGenerator;
//# sourceMappingURL=response.js.map