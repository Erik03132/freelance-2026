"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ArchitectureAgent = void 0;
const base_1 = require("./base");
class ArchitectureAgent extends base_1.BaseSpecialist {
    agentType = 'architecture';
    agentName = 'Кулибин (Инженер-Конструктор)';
    emoji = '📐';
    expertise = 'Инженер-конструктор с опытом в промышленном дизайне и мебельном производстве. Проектирование чертежей по ГОСТ/ISO, расчет нагрузок и спецификаций материалов.';
    supportedCategories = [
        'engineering_drafting'
    ];
    capabilities = [
        {
            name: 'Blueprints Analysis',
            description: 'Анализ существующих схем и набросков',
            enabled: true,
        },
        {
            name: 'CAD Specification Generation',
            description: 'Генерация технических спецификаций и деталировок в формате таблиц',
            enabled: true,
        }
    ];
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        if (this.matchesAny(text, ['3d', 'визуализ', 'рендер'])) {
            stack.push({ name: 'SketchUp / 3ds Max', reason: 'Для фотореалистичной визуализации и объемного моделирования.' });
        }
        if (this.matchesAny(text, ['чертеж', 'схема', 'план'])) {
            stack.push({ name: 'AutoCAD / КОМПАС-3D', reason: 'Отраслевой стандарт для подготовки точных рабочих чертежей по стандартам.' });
        }
        if (this.matchesAny(text, ['мебель', 'шкаф', 'кухня'])) {
            stack.push({ name: 'Базис-Мебельщик', reason: 'Специализированное ПО для мебельного производства с авто-раскроем.' });
        }
        return stack.length > 0 ? stack : [{ name: 'AutoCAD', reason: 'Универсальный стандарт для инженерной графики.' }];
    }
    createPlan(job, techStack) {
        const steps = [];
        let order = 1;
        steps.push({
            order: order++,
            title: 'Изучение ТЗ и эскизов',
            description: 'Анализ габаритов, материалов и требований к функциональности изделия.',
            deliverable: 'Техническое задание на проектирование',
            estimatedHours: '2-3 часа',
            rationale: 'Необходимо исключить ошибки в размерах на самом раннем этапе.',
            canAutomate: false,
        });
        steps.push({
            order: order++,
            title: 'Построение 3D-модели',
            description: 'Создание объемной модели для проверки стыковки узлов и внешнего вида.',
            deliverable: '3D-модель (просмотровая)',
            estimatedHours: '4-8 часов',
            rationale: 'Позволяет заказчику увидеть изделие "в объеме" до фиксации чертежей.',
            canAutomate: false,
        });
        steps.push({
            order: order++,
            title: 'Подготовка рабочих чертежей',
            description: 'Отрисовка всех проекций, разрезов и узлов крепления с указанием точных размеров.',
            deliverable: 'Комплект чертежей (PDF/DWG)',
            estimatedHours: '6-12 часов',
            rationale: 'Основной документ для производства/изготовления.',
            canAutomate: false,
        });
        steps.push({
            order: order++,
            title: 'Спецификация и деталировка',
            description: 'Составление списка всех деталей, фурнитуры и расчет расхода материалов (раскрой).',
            deliverable: 'Таблица материалов и карта раскроя',
            estimatedHours: '2-4 часа',
            rationale: 'Нужно для закупки материалов и оценки себестоимости.',
            canAutomate: true,
            automationTool: 'CAD Specification SDK',
        });
        return steps;
    }
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        questions.push('Укажите основные габаритные размеры (Ширина x Высота x Глубина).');
        questions.push('Из каких материалов планируется изготовление (ЛДСП, МДФ, массив, металл)?');
        questions.push('Нужна ли детальная карта раскроя для производства или только общий чертеж?');
        if (this.matchesAny(text, ['мебель'])) {
            questions.push('Какую фурнитуру предпочтительно использовать (Hettich, Blum или эконом-сегмент)?');
        }
        return questions.slice(0, 4);
    }
    specifyPrototype(job) {
        return {
            type: 'engineering_spec',
            files: new Map(),
            description: 'Пример деталировки одного типового узла и предварительная спецификация материалов.',
            completionPercent: 30,
            whatIsImplemented: ['Анализ габаритов', 'Список материалов'],
            whatIsLeft: ['Полная деталировка всех узлов', 'Сборочный чертеж'],
        };
    }
    explainWhyMe(job) {
        return `🛠 Почему я подхожу:
• Имею опыт подготовки чертежей специально под мебельное производство.
• Учитываю припуски на кромку и технические зазоры для фурнитуры.
• Мои чертежи понятны любому мастеру в цеху, что исключает брак при сборке.`;
    }
}
exports.ArchitectureAgent = ArchitectureAgent;
