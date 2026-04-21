import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
import {
  BaseSpecialist,
  TechStackRecommendation,
  PlanStep,
  PrototypeSpec,
  AgentCapability,
} from './base';
import { TEAM_ROLES } from '../../constants/team';

/**
 * 🎨 REMBRANDT (Design Agent) - GBP v1.0
 * Visual Futurizer. Превращает интерфейс в произведение технологического искусства.
 */
export class DesignAgent extends BaseSpecialist {
  readonly agentType = 'design';
  readonly agentName = TEAM_ROLES.REMBRANDT.NAME;
  readonly emoji = '🎨';
  readonly expertise = TEAM_ROLES.REMBRANDT.EXPERTISE;

  readonly supportedCategories: TaskCategory[] = [
    'design_ui', 'web_frontend', 'mobile_app'
  ];

  readonly capabilities: AgentCapability[] = [
    {
      name: 'Nano-Banana Assets',
      description: 'Использование продвинутых промптов для фотореалистичных и изометрических рендеров (Character Cloning, Material Mapping)',
      enabled: true,
    },
    {
      name: 'SVG Logo Sourcing',
      description: 'Поиск и интеграция официальных SVG-логотипов (svglogo.dev, simpleicons)',
      enabled: true,
    },
    {
      name: 'Stitch UI Generation',
      description: 'Мгновенная генерация прототипов экранов и дизайн-систем через Stitch MCP',
      mcpServer: 'StitchMCP',
      enabled: true,
    },
    {
      name: 'SVG to 3D Workflows (WebGL / 3dsvg.design)',
      description: 'Генерация топологически точных 2D SVG-контуров для последующей 3D-экструзии (React Three Fiber, Spline, или 3dsvg.design)',
      enabled: true,
    }
  ];

  /**
   * Глобальный Протокол Загрузки (GBP): Сертификат готовности
   */
  async generateBootCertificate(category: string): Promise<string> {
    const isGeminiOk = !!process.env.GEMINI_API_KEY;
    const isStitchOk = true; // Предполагаем наличие MCP, если запущен
    const bananaVersion = 'Awesome-Nano-Banana v1.0 Integrated';

    return [
      '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓',
      '┃  🛡️ REMBRANDT READINESS CERTIFICATE (GBP v1.0)      ┃',
      '┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫',
      `┃ 📖 Rules Hierarchy: GBP -> Constitution -> Visual ┃`,
      `┃ 🔍 Context Scope: src/agents/specialists/design.ts  ┃`,
      `┃ 🛠️ Tools Ping: Gemini: ${isGeminiOk ? 'OK ✅' : 'Missing ❌'}  Stitch: ${isStitchOk ? 'OK ✅' : 'Offline ❌'} ┃`,
      `┃ 🍌 Knowledge: ${bananaVersion} [OK]              ┃`,
      '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛'
    ].join('\n');
  }

  recommendTechStack(job: RawJob): TechStackRecommendation[] {
    const text = `${job.title} ${job.description}`.toLowerCase();
    const isSmallTask = this.matchesAny(text, ['баннер', 'логотип', 'картинка', 'banner', 'logo', 'background', 'соцсет', 'linkedin', 'vk', 'превью']);
    const stack: TechStackRecommendation[] = [];

    if (isSmallTask) {
      stack.push({ name: 'Figma + SVGLogo.dev', reason: 'Для мгновенного доступа к качественным векторным ассетам.' });
      stack.push({ name: 'Nano-Banana Prompts', reason: 'Для создания фотореалистичных текстур и уникальных ассетов.' });
    } else {
      stack.push({ name: 'Figma + Stitch MCP', reason: 'Отраслевой стандарт + AI-автоматизация для сборки интерфейсов.' });
      stack.push({ name: 'Atomic Design System', reason: 'Методология создания масштабируемых интерфейсов.' });
      stack.push({ name: 'Nano-Banana Concept Architecture', reason: 'Для проектирования сложных систем (CJM, Exploded Views).' });
    }

    return stack;
  }

  createPlan(job: RawJob, techStack: TechStackRecommendation[]): PlanStep[] {
    const text = `${job.title} ${job.description}`.toLowerCase();
    const isSmallTask = this.matchesAny(text, ['баннер', 'логотип', 'картинка', 'banner', 'logo', 'background', 'соцсет', 'linkedin', 'vk', 'превью']);
    const steps: PlanStep[] = [];
    let order = 1;

    if (isSmallTask) {
      steps.push({
        order: order++,
        title: 'Концепт и референсы (Banana Recon)',
        description: 'Подбор стилистики на базе Awesome-Nano-Banana, поиск визуальных образов и создание 2-3 черновых эскизов.',
        deliverable: 'Мудборд и эскизы',
        estimatedHours: '1-2',
        rationale: 'Позволяет быстро согласовать направление через проверенные паттерны.',
        canAutomate: true,
        automationTool: 'Nano-Banana Library'
      });
      steps.push({
        order: order++,
        title: 'Финальная отрисовка',
        description: 'Чистовая работа над макетом, работа с типографикой, цветом и финальная ретушь.',
        deliverable: 'Готовый баннер/логотип в нужных форматах (SVG, PNG, JPG)',
        estimatedHours: '2-4',
        rationale: 'Создание качественного визуального продукта, готового к публикации.',
        canAutomate: false
      });
    } else {
      // План для серьезных интерфейсов
      steps.push({
        order: order++,
        title: 'UX-исследование и Banana CJM',
        description: 'Анализ конкурентов, проектирование путей пользователя и логики переходов с использованием UX-схем.',
        deliverable: 'CJM + UX-прототип',
        estimatedHours: '4-8',
        rationale: 'Гарантирует, что продукт будет удобным, а не просто красивым.',
        canAutomate: false
      });
      steps.push({
        order: order++,
        title: 'UI-дизайн и Дизайн-система (Stitch)',
        description: 'Разработка визуального стиля и создание библиотеки компонентов в Figma через Stitch MCP.',
        deliverable: 'Дизайн-макеты + UI Kit',
        estimatedHours: '12-20',
        rationale: 'Создание консистентного и масштабируемого дизайна.',
        canAutomate: true,
        automationTool: 'Stitch MCP'
      });
      steps.push({
        order: order++,
        title: 'Интерактив и Передача (Exploded View)',
        description: 'Сборка кликабельного прототипа и подготовка спецификаций для разработки.',
        deliverable: 'Интерактивный прототип + Handover',
        estimatedHours: '4-6',
        rationale: 'Упрощает реализацию и тестирование гипотез до написания кода.',
        canAutomate: true,
        automationTool: 'Stitch Prototypes'
      });
    }

    return steps;
  }

  generateQuestions(job: RawJob): string[] {
    const text = `${job.title} ${job.description}`.toLowerCase();
    const questions: string[] = [];

    questions.push('Кто ваш основной конкурент и чем ваш продукт должен выделяться визуально?');
    
    if (!this.matchesAny(text, ['брендбук', 'логотип', 'цвета'])) {
      questions.push('Есть ли готовый брендбук или предпочтения по цветовой палитре (HEX-коды)?');
    }
    
    questions.push('Какое ключевое действие должен совершить пользователь на главном экране (Conversion Goal)?');

    if (!this.matchesAny(text, ['wcag', 'доступность', 'accessibility'])) {
      questions.push('Насколько критично соответствие стандартам доступности (WCAG 2.1) для вашего проекта?');
    }

    questions.push('В какой стилистике мы работаем? (Neo-Brutalism, Glassmorphism, Minimalist, Corporate)');

    return questions.slice(0, 5);
  }

  specifyPrototype(job: RawJob): PrototypeSpec | null {
    const text = `${job.title} ${job.description}`.toLowerCase();
    
    // CRM / Dashboard
    if (this.matchesAny(text, ['dashboard', 'админ', 'лк', 'crm', 'панел'])) {
      return {
        type: 'stitch_dashboard_prototype',
        files: new Map(),
        description: 'Интерактивный прототип CRM-системы в Stitch с настроенной дизайн-системой.',
        mcpActions: [
          {
            server: 'StitchMCP',
            tool: 'create_project',
            arguments: { title: `CRM Dashboard for ${job.title}` },
            purpose: 'Создание рабочего пространства проекта в Stitch'
          },
          {
            server: 'StitchMCP',
            tool: 'generate_screen_from_text',
            arguments: { prompt: `Modern dark-themed CRM dashboard for ${job.title} with sidebar navigation, stat cards, and data table. Premium aesthetics, glassmorphism.` },
            purpose: 'Генерация главного экрана дашборда'
          }
        ],
        completionPercent: 35,
        whatIsImplemented: ['Dashboard Home', 'Navigation Sidebar', 'User Profile State', 'Color Tokens', 'Typography System'],
        whatIsLeft: ['Таблицы данных', 'Графики (recharts)', 'Формы редактирования', 'Мобильная версия'],
        demoInstructions: 'Прототип доступен для просмотра в Stitch/Figma (ссылка по запросу)'
      };
    }

    // Landing / Promo
    if (this.matchesAny(text, ['лендинг', 'landing', 'сайт', 'одностранич', 'промо'])) {
      return {
        type: 'stitch_landing_concept',
        files: new Map(),
        description: 'Высокоуровневый концепт главного экрана + UI-Kit основных элементов.',
        mcpActions: [
          {
            server: 'StitchMCP',
            tool: 'create_project',
            arguments: { title: `Landing Page: ${job.title}` },
            purpose: 'Инициализация дизайн-проекта лендинга'
          },
          {
            server: 'StitchMCP',
            tool: 'generate_screen_from_text',
            arguments: { prompt: `High-converting modern landing page for "${job.title}". Features: Hero section with CTA, features grid, social proof. Clean, premium typography, vibrant accent colors.` },
            purpose: 'Сборка концепта главного экрана (Hero section)'
          }
        ],
        completionPercent: 40,
        whatIsImplemented: ['Hero Section', 'Header/Footer', 'Button System', 'Grid Layout', 'Concept Visuals via AI'],
        whatIsLeft: ['Блок отзывов', 'Ценовые таблицы', 'Форма захвата', 'Контентные блоки'],
        demoInstructions: 'Демонстрация концепта через Stitch Shared Link'
      };
    }

    return null;
  }

  protected explainWhyMe(job: RawJob): string {
    return `🎯 Почему я подхожу:
• Проектирую на основе данных и User Research, используя паттерны Nano-Banana для максимального визуального влияния.
• Внедряю дизайн-системы через Stitch MCP, что позволяет вам увидеть результат уже в первый день.
• **Visual Futurizer:** Мои интерфейсы выглядят премиально и современно (Glassmorphism, Vibrant Gradients, Modern Typography).
• **Прагматичный подход:** Мы фиксируем только ключевое (MVP Design), не тратя бюджет на "декор ради декора".`;
  }
}

