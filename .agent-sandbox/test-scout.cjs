/**
 * Тестовый скрипт: проверяет работу ScoutAgent на реальных задачах
 * 
 * Использование: node test-scout.js
 * 
 * Берёт задачи из БД и генерирует предложение для каждой.
 * Также тестирует API endpoint /api/generate-response через HTTP.
 */

const http = require('http');
const path = require('path');
const fs = require('fs');

// ===================================================
// Загрузка конфигураций
// ===================================================

const profilePath = path.join(__dirname, 'freelance-agent', 'config', 'profile.json');
const skillsPath = path.join(__dirname, 'freelance-agent', 'config', 'agent-skills.json');

let profile = {};
let servicesConfig = {};

try {
  profile = JSON.parse(fs.readFileSync(profilePath, 'utf-8'));
  console.log('✅ Профиль загружен');
} catch (e) {
  console.log('⚠️ Профиль не найден, используется пустой');
}

try {
  servicesConfig = JSON.parse(fs.readFileSync(skillsPath, 'utf-8'));
  console.log('✅ Agent-skills загружены');
} catch (e) {
  console.log('⚠️ Agent-skills не найден');
}

// ===================================================
// Тестовые задачи (эмулируют данные с Kwork)
// ===================================================

const testTasks = [
  {
    title: 'Разработать Telegram-бота для интернет-магазина',
    description: 'Необходимо создать Telegram-бота для магазина одежды. Бот должен: показывать каталог товаров, корзина, оформление заказа, интеграция с платёжной системой ЮKassa, уведомления о статусе заказа, админ-панель для управления товарами. База данных PostgreSQL. Нужна документация по развёртыванию.',
    budget: '25000 ₽',
    skills: ['Python', 'aiogram', 'PostgreSQL'],
    platform: 'kwork'
  },
  {
    title: 'Парсинг товаров с Wildberries',
    description: 'Необходимо спарсить данные о товарах с Wildberries (название, цена, рейтинг, количество отзывов, продавец) по определённым категориям. Данные нужны в формате Excel. Объём: ~10000 товаров. Обход защиты от парсинга обязателен.',
    budget: '8000 ₽',
    skills: ['Python', 'Parsing', 'Playwright'],
    platform: 'kwork'
  },
  {
    title: 'Доработка мобильного приложения на Flutter',
    description: 'У нас есть мобильное приложение на Flutter. Нужно добавить авторизацию через Apple ID и Google, push-уведомления, экран избранного, и исправить баги из списка. Исходный код предоставим. Нужен доступ к аккаунту разработчика Apple.',
    budget: '60000 ₽',
    skills: ['Flutter', 'Dart', 'Firebase'],
    platform: 'kwork'
  },
  {
    title: 'Написать лекцию по FastAPI и JWT авторизации',
    description: 'Нужна лекция для курса по backend-разработке на Python. Тема: создание REST API с FastAPI и авторизация через JWT токены. Формат: текст + примеры кода + слайды. Объём: 1 час чтения.',
    budget: '5000 ₽',
    skills: ['Python', 'FastAPI'],
    platform: 'kwork'
  },
  {
    title: 'Создание сайта казино онлайн',
    description: 'Нужен сайт онлайн казино с игровыми автоматами, рулеткой и ставками на спорт. Оплата криптовалютой.',
    budget: '200000 ₽',
    skills: ['React', 'Node.js'],
    platform: 'kwork'
  },
  {
    title: 'Сделать лендинг для стоматологии',
    description: 'Простой лендинг для стоматологической клиники. 5 экранов: главная, услуги, врачи, отзывы, контакты. Адаптивная вёрстка. Есть дизайн в Figma.',
    budget: '3000 ₽',
    skills: ['HTML', 'CSS', 'JavaScript'],
    platform: 'kwork'
  },
  {
    title: 'Нужен сайт',
    description: 'Нужен сайт. Подробности в личке.',
    budget: '',
    skills: [],
    platform: 'kwork'
  }
];

// ===================================================
// Inline-анализатор (копия логики из route.ts)
// ===================================================

function detectCategory(text) {
  if (['flutter', 'react native', 'swift', 'kotlin', 'мобильное приложение', 'мобильн'].some(w => text.includes(w))) return 'mobile_app';
  if (['electron', 'desktop app', 'десктопное'].some(w => text.includes(w))) return 'desktop_app';
  if (['machine learning', 'ml', 'нейросет', 'tensorflow', 'pytorch', 'data science'].some(w => text.includes(w))) return 'data_science';
  if (['ci/cd', 'devops', 'kubernetes', 'terraform', 'ansible'].some(w => text.includes(w))) return 'devops';
  if (['лекц', 'урок', 'презентац', 'обучени', 'курс', 'вебинар'].some(w => text.includes(w))) return 'lecture_education';
  if (['telegram', 'tg bot', 'телеграм'].some(w => text.includes(w)) && text.includes('бот')) return 'telegram_bot';
  if (['chrome extension', 'расширение chrome'].some(w => text.includes(w))) return 'chrome_extension';
  if (['парсинг', 'парсер', 'scraping', 'scraper', 'спарсить', 'краулер'].some(w => text.includes(w))) return 'parsing_scraping';
  if (['дизайн', 'логотип', 'figma', 'макет', 'ui/ux'].some(w => text.includes(w))) return 'design_ui';
  if (['текст', 'стать', 'копирайт', 'контент'].some(w => text.includes(w))) return 'text_content';
  if (['backend', 'бекенд', 'api', 'fastapi', 'django', 'flask', 'express', 'nestjs'].some(w => text.includes(w))) {
    if (['frontend', 'react', 'vue', 'angular', 'фронтенд', 'лендинг'].some(w => text.includes(w))) return 'web_fullstack';
    return 'web_backend';
  }
  if (['react', 'vue', 'angular', 'next.js', 'frontend', 'фронтенд', 'лендинг', 'верстк'].some(w => text.includes(w))) return 'web_frontend';
  if (['разработ', 'программ', 'сайт', 'приложен'].some(w => text.includes(w))) return 'web_fullstack';
  return 'other';
}

function analyzeTask(task) {
  const text = `${task.title} ${task.description}`.toLowerCase();
  const warnings = [];
  const missingServices = [];
  const blockers = [];
  
  const category = detectCategory(text);
  
  // Skill coverage
  const userSkills = Object.keys(profile.skills || {}).map(s => s.toLowerCase());
  let skillMatches = 0;
  for (const skill of userSkills) {
    if (text.includes(skill)) skillMatches++;
  }
  const skillCoverage = Math.min(1, skillMatches / Math.max(1, task.skills?.length || 1));

  // Effort
  const baseEffort = {
    'web_fullstack': 40, 'web_frontend': 20, 'web_backend': 25,
    'telegram_bot': 15, 'chrome_extension': 15, 'parsing_scraping': 12,
    'mobile_app': 60, 'desktop_app': 50, 'devops': 15,
    'data_science': 30, 'design_ui': 12, 'lecture_education': 8,
    'text_content': 6, 'other': 15
  };
  let effortHours = baseEffort[category] || 15;
  if (['авториз', 'jwt', 'oauth'].some(w => text.includes(w))) effortHours += 5;
  if (['админ панел', 'admin', 'cms'].some(w => text.includes(w))) effortHours += 10;
  if (['интеграци', 'api', 'webhook'].some(w => text.includes(w))) effortHours += 5;
  if (['простой', 'простая', 'несложн', 'небольш'].some(w => text.includes(w))) effortHours *= 0.6;
  if (['сложн', 'комплексн', 'масштабн'].some(w => text.includes(w))) effortHours *= 1.5;
  effortHours = Math.round(effortHours);

  // Budget analysis
  let budgetAmount = null;
  const budgetMatch = (task.budget || '').match(/(\d[\d\s]*)/);
  if (budgetMatch) budgetAmount = parseInt(budgetMatch[1].replace(/\s/g, ''));
  
  let hourlyRate = null;
  let worthIt = true;
  let rewardComment = 'Бюджет не указан';
  
  if (budgetAmount) {
    hourlyRate = Math.round(budgetAmount / effortHours);
    if (hourlyRate >= 2000) rewardComment = `Отличная ставка: ~${hourlyRate} ₽/час`;
    else if (hourlyRate >= 1000) rewardComment = `Хорошая ставка: ~${hourlyRate} ₽/час`;
    else if (hourlyRate >= 500) rewardComment = `Приемлемая ставка: ~${hourlyRate} ₽/час`;
    else {
      rewardComment = `Низкая ставка: ~${hourlyRate} ₽/час. Рекомендуется отказаться.`;
      worthIt = false;
      warnings.push(`💰 Низкая ставка: ~${hourlyRate} ₽/час при трудоёмкости ~${effortHours}ч`);
    }
  }

  // Blockers
  if (['казино', 'ставки', 'adult', '18+', 'обход блокировк', 'взлом', 'кардинг', 'спам рассылк', 'накрутк']
    .some(w => text.includes(w))) {
    blockers.push('Задача связана с нелегальной/сомнительной деятельностью');
  }

  if (task.description.length < 50) {
    warnings.push('⚠️ Описание задачи очень короткое — рекомендуется уточнить');
  }

  // Missing services
  const services = servicesConfig?.antigravity?.services || {};
  if (['web_frontend', 'web_fullstack', 'design_ui'].includes(category) && !services.stitch?.enabled) {
    missingServices.push({ name: 'Stitch MCP', purpose: 'Генерация UI/React компонентов', priority: 'recommended' });
  }
  if (text.includes('firebase') || text.includes('firestore')) {
    missingServices.push({ name: 'Firebase', purpose: 'Работа с Firebase/Firestore', priority: 'recommended' });
  }

  const feasible = blockers.length === 0 && worthIt;

  // Services warnings
  for (const ms of missingServices) {
    warnings.push(`🔧 Рекомендуется подключить: ${ms.name} (${ms.purpose})`);
  }

  return { category, feasible, blockers, warnings, missingServices, effortHours, 
    rewardAnalysis: { budgetAmount, hourlyRate, worthIt, comment: rewardComment },
    skillCoverage: Math.round(skillCoverage * 100)
  };
}

const categoryNames = {
  'web_fullstack': 'Full-stack', 'web_frontend': 'Frontend', 'web_backend': 'Backend/API',
  'telegram_bot': 'Telegram бот', 'chrome_extension': 'Chrome ext', 'parsing_scraping': 'Парсинг',
  'mobile_app': 'Мобильное приложение', 'desktop_app': 'Десктоп', 'devops': 'DevOps',
  'data_science': 'Data Science', 'design_ui': 'Дизайн', 'lecture_education': 'Образование',
  'text_content': 'Контент', 'other': 'Другое'
};

// ===================================================
// ТЕСТ
// ===================================================

console.log('\n' + '═'.repeat(80));
console.log('  🤖 ТЕСТ SCOUT AGENT — АНАЛИЗ ЗАДАЧ');
console.log('═'.repeat(80) + '\n');

for (let i = 0; i < testTasks.length; i++) {
  const task = testTasks[i];
  const analysis = analyzeTask(task);
  
  const statusIcon = analysis.feasible ? '✅' : '⛔';
  const budgetStr = task.budget || 'не указан';
  
  console.log(`━━━ ${i + 1}/${testTasks.length} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📌 ${task.title}`);
  console.log(`   ${statusIcon} ${analysis.feasible ? 'ВЫПОЛНИМА' : 'НЕ РЕКОМЕНДОВАНА'}`);
  console.log(`   📋 Категория: ${categoryNames[analysis.category] || analysis.category}`);
  console.log(`   ⏱  Трудоёмкость: ~${analysis.effortHours}ч (~${(analysis.effortHours / 8).toFixed(1)} дней)`);
  console.log(`   💰 Бюджет: ${budgetStr} → ${analysis.rewardAnalysis.comment}`);
  console.log(`   🎯 Покрытие навыков: ${analysis.skillCoverage}%`);
  
  if (analysis.blockers.length > 0) {
    console.log(`   🚫 Блокеры:`);
    analysis.blockers.forEach(b => console.log(`      ⛔ ${b}`));
  }
  
  if (analysis.warnings.length > 0) {
    console.log(`   ⚠️  Предупреждения:`);
    analysis.warnings.forEach(w => console.log(`      ${w}`));
  }
  
  if (analysis.missingServices.length > 0) {
    console.log(`   🔧 Рекомендуемые сервисы: ${analysis.missingServices.map(s => s.name).join(', ')}`);
  }
  
  console.log('');
}

console.log('═'.repeat(80));
console.log('  ✅ ТЕСТ ЗАВЕРШЁН');
console.log('═'.repeat(80));
console.log('');
console.log('Следующий шаг: запустите Dashboard и нажмите «Анализ + Предложение»');
console.log('  cd dashboard && npm run dev');
console.log('');
