"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DevOpsAgent = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class DevOpsAgent extends base_1.BaseSpecialist {
    agentType = 'devops';
    agentName = team_1.TEAM_ROLES.KULIBIN.NAME;
    emoji = '🔧';
    expertise = team_1.TEAM_ROLES.KULIBIN.EXPERTISE;
    supportedCategories = [
        'devops', 'web_backend', 'web_fullstack'
    ];
    capabilities = [
        {
            name: 'Infrastructure Blueprinting',
            description: 'Использование эталонных Docker и Terraform шаблонов для production-ready инфраструктуры',
            enabled: true,
        },
        {
            name: 'CI/CD Pipeline Sourcing',
            description: 'Подбор проверенных GitHub Actions / GitLab CI сценариев',
            enabled: true,
        }
    ];
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        // Контейнеризация
        stack.push({ name: 'Docker / Docker Compose', reason: 'Обеспечивает воспроизводимость окружений; устраняет проблему "у меня на компе это работает".' });
        // CI/CD
        if (this.matchesAny(text, ['gitlab'])) {
            stack.push({ name: 'GitLab CI', reason: 'Указан в ТЗ. Мощный встроенный инструментарий CI/CD конвейеров.' });
        }
        else {
            stack.push({ name: 'GitHub Actions', reason: 'Простота настройки, отличная интеграция с GitHub репозиториями, большая база готовых actions.' });
        }
        // Инфраструктура
        if (this.matchesAny(text, ['aws', 'amazon'])) {
            stack.push({ name: 'AWS Cloud (EC2, S3, RDS)', reason: 'Высокая надежность (SLA) и масштабируемость.' });
            stack.push({ name: 'Terraform', reason: 'Инфраструктура как код (IaC) - повторяемость, ревью и история инфраструктуры.' });
        }
        else if (this.matchesAny(text, ['k8s', 'kubernetes', 'масштаб'])) {
            stack.push({ name: 'Kubernetes', reason: 'Оркестрация большого числа сервисов (microservices), auto-scaling, self-healing.' });
        }
        else {
            stack.push({ name: 'Ubuntu Linux VPS (Nginx)', reason: 'Недорогое, надёжное решение для одного-нескольких монолитов (балансировщик + reverse proxy).' });
        }
        return stack;
    }
    createPlan(job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const steps = [];
        let order = 1;
        steps.push({
            order: order++,
            title: 'Аудит и планирование инфраструктуры',
            description: 'Анализ текущей архитектуры, выбор облачного провайдера, расчет конфигураций виртуальных серверов/баз данных.',
            deliverable: 'Схема инфраструктуры, список доступов',
            estimatedHours: '2-4 часа',
            rationale: 'Необходим для правильного расчета бюджета на серверы и избежания over-engineering.',
            canAutomate: true,
        });
        steps.push({
            order: order++,
            title: 'Infrastructure Blueprinting',
            description: 'Подбор эталонных Docker-композиций и CI-скриптов для выбранного стека.',
            deliverable: 'Архитектурный план развёртывания',
            estimatedHours: '2-3 часа',
            rationale: 'Стандартные шаблоны гарантируют отсутствие ошибок конфигурации в продакшене.',
            canAutomate: true,
        });
        steps.push({
            order: order++,
            title: 'Настройка серверов и баз данных',
            description: 'Развертывание Linux, защита (firewall), установка Nginx, получение SSL, запуск СУБД.',
            deliverable: 'Настроенный боевой сервер (Production)',
            estimatedHours: '5-10 часов',
            rationale: 'Обеспечение безопасности и базовой доступности сервиса извне (HTTPS).',
            canAutomate: false,
        });
        steps.push({
            order: order++,
            title: 'Настройка CI/CD',
            description: 'Автоматизация тестирования (CI) и деплоя (CD) на сервера при пуше в основную ветку репозитория.',
            deliverable: 'Авто-обновляющийся деплой Pipeline',
            estimatedHours: '4-8 часов',
            rationale: 'Отказ от "ручного" деплоя исключает человеческий фактор и ускоряет time-to-market.',
            canAutomate: true,
        });
        return steps;
    }
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        questions.push('На каких мощностях планируется развертывание (Ваши VPS сервера на DigitalOcean/Hetzner, AWS, Google Cloud)?');
        questions.push('Нужна ли настройка системы мониторинга и аллертов (Grafana / Prometheus)?');
        if (!this.matchesAny(text, ['github', 'gitlab'])) {
            questions.push('Где на текущий момент хостится исходный код (GitHub / GitLab / Bitbucket)?');
        }
        questions.push('Имеются ли приобретенные домены для проекта и доступы к их DNS записям?');
        return questions.slice(0, 5);
    }
    specifyPrototype(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        if (this.matchesAny(text, ['docker', 'докер', 'деплой'])) {
            return {
                type: 'docker_compose',
                files: new Map(),
                description: 'Предварительный docker-compose.yml для тестового запуска проекта локально.',
                completionPercent: 50,
                whatIsImplemented: ['Описание сервисов', 'Базовая сеть', 'Environment variables map'],
                whatIsLeft: ['Финальная донастройка', 'Стейндж сервера', 'CI pipe'],
                demoInstructions: 'Приложу готовый YML файл.'
            };
        }
        return null;
    }
    explainWhyMe(job) {
        return `🎯 Почему я подхожу:
• Практикую парадигму Infrastructure as Code — инфраструктуру легко восстановить и пересоздать.
• Придерживаюсь стандартов безопасности (SecOps), правильная изоляция сетей и портов.
• Автоматизирую рутинный деплой, чтобы разработчики занимались фичами, а не перезапуском серверов.`;
    }
}
exports.DevOpsAgent = DevOpsAgent;
