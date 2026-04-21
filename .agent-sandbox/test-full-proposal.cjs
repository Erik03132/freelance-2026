/**
 * Полный тест Scout Agent: анализ + генерация предложения
 * Выводит то же, что покажет Dashboard UI
 */

const path = require('path');
const fs = require('fs');

// Загрузка конфигов
const profilePath = path.join(__dirname, 'freelance-agent', 'config', 'profile.json');
const skillsPath = path.join(__dirname, 'freelance-agent', 'config', 'agent-skills.json');
let profile = {}, servicesConfig = {};
try { profile = JSON.parse(fs.readFileSync(profilePath, 'utf-8')); } catch(e) {}
try { servicesConfig = JSON.parse(fs.readFileSync(skillsPath, 'utf-8')); } catch(e) {}

function detectCategory(text) {
  if (['flutter', 'react native', 'swift', 'kotlin', 'мобильное приложение', 'мобильн'].some(w => text.includes(w))) return 'mobile_app';
  if (['machine learning', 'ml', 'нейросет', 'tensorflow', 'pytorch'].some(w => text.includes(w))) return 'data_science';
  if (['лекц', 'урок', 'презентац', 'обучени', 'курс'].some(w => text.includes(w))) return 'lecture_education';
  if (['telegram', 'телеграм'].some(w => text.includes(w)) && text.includes('бот')) return 'telegram_bot';
  if (['парсинг', 'парсер', 'scraping', 'спарсить'].some(w => text.includes(w))) return 'parsing_scraping';
  if (['backend', 'бекенд', 'api', 'fastapi', 'django'].some(w => text.includes(w))) {
    if (['frontend', 'react', 'vue', 'лендинг'].some(w => text.includes(w))) return 'web_fullstack';
    return 'web_backend';
  }
  if (['react', 'vue', 'angular', 'frontend', 'лендинг', 'верстк'].some(w => text.includes(w))) return 'web_frontend';
  if (['разработ', 'программ', 'сайт'].some(w => text.includes(w))) return 'web_fullstack';
  return 'other';
}

function analyzeAndGenerate(taskTitle, taskDescription, budget) {
  const text = `${taskTitle} ${taskDescription}`.toLowerCase();
  const category = detectCategory(text);
  const warnings = [], missingServices = [], blockers = [];
  
  // Skills
  const userSkills = Object.keys(profile.skills || {}).map(s => s.toLowerCase());
  const synonyms = profile.skillSynonyms || {};
  const allSkills = new Set(userSkills);
  for (const syns of Object.values(synonyms)) {
    if (Array.isArray(syns)) for (const s of syns) allSkills.add(s.toLowerCase());
  }
  let skillMatches = 0;
  for (const skill of allSkills) if (text.includes(skill)) skillMatches++;
  
  // Effort
  const base = { 'web_fullstack': 40, 'web_frontend': 20, 'web_backend': 25, 'telegram_bot': 15, 'parsing_scraping': 12, 'mobile_app': 60, 'lecture_education': 8, 'other': 15 };
  let effortHours = base[category] || 15;
  if (['авториз', 'jwt', 'oauth'].some(w => text.includes(w))) effortHours += 5;
  if (['админ', 'admin'].some(w => text.includes(w))) effortHours += 10;
  if (['интеграци', 'api'].some(w => text.includes(w))) effortHours += 5;
  if (['простой', 'простая', 'несложн'].some(w => text.includes(w))) effortHours *= 0.6;
  effortHours = Math.round(effortHours);

  // Budget
  let budgetAmount = null;
  const bm = (budget || '').match(/(\d[\d\s]*)/);
  if (bm) budgetAmount = parseInt(bm[1].replace(/\s/g, ''));
  
  let hourlyRate = null, worthIt = true, rewardComment = 'Бюджет не указан';
  if (budgetAmount) {
    hourlyRate = Math.round(budgetAmount / effortHours);
    if (hourlyRate >= 2000) rewardComment = `Отличная ставка: ~${hourlyRate} ₽/час`;
    else if (hourlyRate >= 1000) rewardComment = `Хорошая ставка: ~${hourlyRate} ₽/час`;
    else if (hourlyRate >= 500) rewardComment = `Приемлемая ставка: ~${hourlyRate} ₽/час`;
    else { rewardComment = `Низкая ставка: ~${hourlyRate} ₽/час`; worthIt = false; }
  }

  // Blockers
  if (['казино', 'ставки', 'adult', 'взлом', 'кардинг', 'накрутк'].some(w => text.includes(w)))
    blockers.push('Нелегальная деятельность');
  if (taskDescription.length < 50) warnings.push('⚠️ Описание слишком короткое');

  // Services
  const services = servicesConfig?.antigravity?.services || {};
  if (['web_frontend', 'web_fullstack'].includes(category) && !services.stitch?.enabled)
    missingServices.push({ name: 'Stitch MCP', purpose: 'UI-генерация' });

  const feasible = blockers.length === 0 && worthIt;

  // === TechStack ===
  const stack = [];
  const known = { 'react': 'React 18+', 'next.js': 'Next.js 14', 'typescript': 'TypeScript', 'node.js': 'Node.js', 'python': 'Python 3.12+', 'fastapi': 'FastAPI', 'postgresql': 'PostgreSQL', 'mongodb': 'MongoDB', 'aiogram': 'aiogram 3.x', 'playwright': 'Playwright', 'firebase': 'Firebase' };
  for (const [kw, tech] of Object.entries(known)) if (text.includes(kw) && !stack.includes(tech)) stack.push(tech);
  if (stack.length === 0) {
    const d = { 'telegram_bot': ['Python 3.12+', 'aiogram 3.x'], 'parsing_scraping': ['Python', 'Playwright'], 'web_fullstack': ['TypeScript', 'React', 'Node.js'], 'other': ['TypeScript'] };
    stack.push(...(d[category] || d['other']));
  }

  // === Proposal ===
  let proposal;
  if (feasible) {
    const desc = taskDescription || '';
    const sentences = desc.split(/[.!?]/).filter(s => s.trim().length > 10).slice(0, 2);
    const understanding = sentences.length > 0 ? `Понял задачу: ${sentences.join('. ').trim()}.` : `Понял задачу: ${taskTitle}.`;
    const totalDays = (effortHours / 8).toFixed(1);
    const questions = [];
    if (!text.includes('срок')) questions.push('Есть ли дедлайн?');
    if (category === 'telegram_bot') questions.push('Есть ли бот через @BotFather?');
    if (category === 'parsing_scraping') questions.push('Какой объём данных?');
    questions.push('Остались ли требования, не отражённые в описании?');

    proposal = `Здравствуйте!

Внимательно изучил ваше техническое задание.

${understanding}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠 СТЕК: ${stack.join(', ')}

📋 ПЛАН РЕАЛИЗАЦИИ:
1. Анализ ТЗ и проектирование (2-4ч)
2. Реализация основной функциональности (~${Math.round(effortHours * 0.5)}ч)
3. Тестирование и отладка (~${Math.round(effortHours * 0.15)}ч)
4. Документация и сдача (1-3ч)

⏱️ Срок: ~${totalDays} рабочих дней (~${effortHours}ч)
${budgetAmount ? `💰 Бюджет: ${budgetAmount} ₽ — готов обсудить` : '💰 Бюджет: открыт к обсуждению'}

❓ ВОПРОСЫ:
${questions.slice(0, 4).map((q, i) => `${i+1}. ${q}`).join('\n')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Работаю итеративно: сделал → показал → фидбек → доработал
Готов приступить!
С уважением, ${profile?.user?.name || 'Разработчик'}`;
  } else {
    proposal = `⛔ ЗАДАЧА НЕ РЕКОМЕНДОВАНА\n\n${blockers.map(b => `• ${b}`).join('\n')}${!worthIt ? `\n• ${rewardComment}` : ''}`;
  }

  return { proposal, analysis: { category, feasible, effortHours, hourlyRate, worthIt, rewardComment, skillMatches, blockers, warnings, missingServices } };
}

const categoryNames = {
  'web_fullstack': 'Full-stack', 'web_frontend': 'Frontend', 'web_backend': 'Backend/API',
  'telegram_bot': 'Telegram бот', 'parsing_scraping': 'Парсинг', 'mobile_app': 'Мобильное прил.',
  'lecture_education': 'Образование', 'other': 'Другое'
};

// ===================================================
// ТЕСТ 1: Telegram бот (хорошая задача)
// ===================================================
console.log('\n' + '═'.repeat(80));
console.log('  🤖 ТЕСТ 1: Хорошая задача — Telegram бот для магазина');
console.log('═'.repeat(80));

const test1 = analyzeAndGenerate(
  'Разработать Telegram-бота для интернет-магазина',
  'Необходимо создать Telegram-бота для магазина одежды. Бот должен: показывать каталог товаров, корзина, оформление заказа, интеграция с платёжной системой ЮKassa, уведомления о статусе заказа, админ-панель для управления товарами. База данных PostgreSQL. Нужна документация по развёртыванию.',
  '25000 ₽'
);
console.log(`\n📊 АНАЛИЗ:`);
console.log(`   Категория: ${categoryNames[test1.analysis.category] || test1.analysis.category}`);
console.log(`   Выполнимость: ${test1.analysis.feasible ? '✅ ДА' : '⛔ НЕТ'}`);
console.log(`   Трудоёмкость: ~${test1.analysis.effortHours}ч`);
console.log(`   Ставка: ~${test1.analysis.hourlyRate} ₽/час → ${test1.analysis.rewardComment}`);
console.log(`\n📝 ПРЕДЛОЖЕНИЕ:\n`);
console.log(test1.proposal);

// ===================================================
// ТЕСТ 2: Казино (должен отказать)
// ===================================================
console.log('\n' + '═'.repeat(80));
console.log('  🤖 ТЕСТ 2: Плохая задача — Сайт казино (200k)');
console.log('═'.repeat(80));

const test2 = analyzeAndGenerate(
  'Создание сайта казино онлайн',
  'Нужен сайт онлайн казино с игровыми автоматами, рулеткой и ставками на спорт.',
  '200000 ₽'
);
console.log(`\n📊 АНАЛИЗ:`);
console.log(`   Категория: ${categoryNames[test2.analysis.category] || test2.analysis.category}`);
console.log(`   Выполнимость: ${test2.analysis.feasible ? '✅ ДА' : '⛔ НЕТ'}`);
console.log(`   Блокеры: ${test2.analysis.blockers.join(', ')}`);
console.log(`\n📝 ОТВЕТ:\n`);
console.log(test2.proposal);

// ===================================================
// ТЕСТ 3: Размытое ТЗ
// ===================================================
console.log('\n' + '═'.repeat(80));
console.log('  🤖 ТЕСТ 3: Размытое ТЗ — "Нужен сайт"');
console.log('═'.repeat(80));

const test3 = analyzeAndGenerate('Нужен сайт', 'Нужен сайт. Подробности в личке.', '');
console.log(`\n📊 АНАЛИЗ:`);
console.log(`   Категория: ${categoryNames[test3.analysis.category] || test3.analysis.category}`);
console.log(`   Предупреждения: ${test3.analysis.warnings.join('; ')}`);
console.log(`\n📝 ПРЕДЛОЖЕНИЕ:\n`);
console.log(test3.proposal);

console.log('\n' + '═'.repeat(80));
console.log('  ✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ');
console.log('═'.repeat(80) + '\n');
