/**
 * Мини-тестовый сервер для проверки API generate-response
 * Не требует Next.js — запускается как чистый Node.js
 * 
 * Использование: node test-api-server.cjs
 * Тест: curl -X POST http://localhost:3333/api/generate-response -H "Content-Type: application/json" -d '{"taskTitle":"...", "taskDescription":"..."}'
 */

const http = require('http');
const path = require('path');
const fs = require('fs');

// ===================================================
// Загрузка профиля и сервисов (копия логики из route.ts)
// ===================================================

function loadProfile() {
  const profilePath = path.join(__dirname, 'freelance-agent', 'config', 'profile.json');
  try {
    if (fs.existsSync(profilePath)) return JSON.parse(fs.readFileSync(profilePath, 'utf-8'));
  } catch (e) {}
  return { user: { name: 'Разработчик' }, skills: { React: 0.9, TypeScript: 0.85 }, skillSynonyms: {} };
}

function loadServicesInfo() {
  const skillsPath = path.join(__dirname, 'freelance-agent', 'config', 'agent-skills.json');
  try {
    if (fs.existsSync(skillsPath)) return JSON.parse(fs.readFileSync(skillsPath, 'utf-8'));
  } catch (e) {}
  return { antigravity: { services: {} } };
}

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

function analyzeTask(job, profile, servicesConfig) {
  const text = `${job.title} ${job.description}`.toLowerCase();
  const warnings = [];
  const missingServices = [];
  const blockers = [];
  const category = detectCategory(text);

  // Skills
  const userSkills = Object.keys(profile.skills || {}).map(s => s.toLowerCase());
  const synonyms = profile.skillSynonyms || {};
  const allSkills = new Set(userSkills);
  for (const syns of Object.values(synonyms)) {
    if (Array.isArray(syns)) for (const s of syns) allSkills.add(s.toLowerCase());
  }
  let skillMatches = 0;
  for (const skill of allSkills) if (text.includes(skill)) skillMatches++;
  const skillCoverage = Math.min(1, skillMatches / Math.max(1, job.skills?.length || 1));

  // Effort
  const baseEffort = { 'web_fullstack': 40, 'web_frontend': 20, 'web_backend': 25, 'telegram_bot': 15, 'chrome_extension': 15, 'parsing_scraping': 12, 'mobile_app': 60, 'desktop_app': 50, 'devops': 15, 'data_science': 30, 'design_ui': 12, 'lecture_education': 8, 'text_content': 6, 'other': 15 };
  let effortHours = baseEffort[category] || 15;
  if (['авториз', 'jwt', 'oauth'].some(w => text.includes(w))) effortHours += 5;
  if (['админ панел', 'admin'].some(w => text.includes(w))) effortHours += 10;
  if (['интеграци', 'api', 'webhook'].some(w => text.includes(w))) effortHours += 5;
  if (['простой', 'простая', 'несложн', 'небольш'].some(w => text.includes(w))) effortHours *= 0.6;
  if (['сложн', 'комплексн', 'масштабн'].some(w => text.includes(w))) effortHours *= 1.5;
  effortHours = Math.round(effortHours);

  // Budget
  let budgetAmount = null, budgetCurrency = 'RUB';
  if (job.budget) {
    budgetAmount = job.budget.amount || job.budget.min || null;
    budgetCurrency = job.budget.currency || 'RUB';
  }
  let hourlyRate = null, rewardComment = 'Бюджет не указан', worthIt = true;
  if (budgetAmount) {
    let amountRub = budgetAmount;
    if (budgetCurrency === 'USD') amountRub *= 95;
    if (budgetCurrency === 'EUR') amountRub *= 103;
    hourlyRate = Math.round(amountRub / effortHours);
    if (hourlyRate >= 2000) rewardComment = `Отличная ставка: ~${hourlyRate} ₽/час`;
    else if (hourlyRate >= 1000) rewardComment = `Хорошая ставка: ~${hourlyRate} ₽/час`;
    else if (hourlyRate >= 500) rewardComment = `Приемлемая ставка: ~${hourlyRate} ₽/час`;
    else { rewardComment = `Низкая ставка: ~${hourlyRate} ₽/час`; worthIt = false; warnings.push(`💰 Низкая ставка: ~${hourlyRate} ₽/час`); }
  }

  // Blockers
  if (['казино', 'ставки', 'adult', '18+', 'обход блокировк', 'взлом', 'кардинг', 'накрутк'].some(w => text.includes(w)))
    blockers.push('Нелегальная/сомнительная деятельность');
  if (job.description.length < 50) warnings.push('⚠️ Описание слишком короткое');

  // Services
  const services = servicesConfig?.antigravity?.services || {};
  if (['web_frontend', 'web_fullstack', 'design_ui'].includes(category) && !services.stitch?.enabled)
    missingServices.push({ name: 'Stitch MCP', purpose: 'Генерация UI', howToConnect: 'Подключить StitchMCP', priority: 'recommended' });
  if (text.includes('firebase'))
    missingServices.push({ name: 'Firebase', purpose: 'Firestore', howToConnect: 'Firebase MCP', priority: 'recommended' });
  for (const ms of missingServices)
    warnings.push(`🔧 Рекомендуется: ${ms.name} (${ms.purpose})`);

  const feasible = blockers.length === 0 && worthIt;
  return { category, feasible, blockers, warnings, missingServices, effortHours,
    rewardAnalysis: { budgetAmount, budgetCurrency, hourlyRate, worthIt, comment: rewardComment },
    skillCoverage: Math.round(skillCoverage * 100),
    operatorNotes: `📋 Категория: ${category}\n⏱ Трудоёмкость: ~${effortHours}ч (~${(effortHours/8).toFixed(1)} дней)\n💰 ${rewardComment}\n🎯 Пок. навыков: ${Math.round(skillCoverage*100)}%`
  };
}

function parseBudget(str) {
  if (!str) return undefined;
  const m = str.match(/(\d[\d\s]*)\s*(₽|руб|RUB)/i);
  if (m) return { type: 'fixed', amount: parseInt(m[1].replace(/\s/g, '')), currency: 'RUB' };
  const m2 = str.match(/\$\s*(\d[\d,]*)/);
  if (m2) return { type: 'fixed', amount: parseInt(m2[1].replace(/,/g, '')), currency: 'USD' };
  const m3 = str.match(/(\d[\d\s]*)/);
  if (m3) return { type: 'fixed', amount: parseInt(m3[1].replace(/\s/g, '')), currency: 'RUB' };
  return undefined;
}

function extractTechStack(text, category) {
  const stack = [];
  const known = { 'react': 'React 18+', 'next.js': 'Next.js 14', 'vue': 'Vue 3', 'typescript': 'TypeScript', 'node.js': 'Node.js', 'python': 'Python 3.12+', 'fastapi': 'FastAPI', 'django': 'Django', 'postgresql': 'PostgreSQL', 'mongodb': 'MongoDB', 'docker': 'Docker', 'aiogram': 'aiogram 3.x', 'playwright': 'Playwright', 'tailwind': 'Tailwind CSS', 'firebase': 'Firebase' };
  for (const [kw, tech] of Object.entries(known)) if (text.includes(kw) && !stack.includes(tech)) stack.push(tech);
  if (stack.length === 0) {
    const d = { 'web_fullstack': ['TypeScript', 'React', 'Node.js', 'PostgreSQL'], 'web_frontend': ['TypeScript', 'React', 'Tailwind'], 'web_backend': ['Python', 'FastAPI', 'PostgreSQL'], 'telegram_bot': ['Python', 'aiogram 3.x', 'SQLite'], 'parsing_scraping': ['Python', 'Playwright'], 'other': ['TypeScript', 'Node.js'] };
    stack.push(...(d[category] || d['other']));
  }
  return stack;
}

function generateProposal(job, analysis, profile) {
  const { category, effortHours, rewardAnalysis } = analysis;
  const text = `${job.title} ${job.description}`.toLowerCase();
  const techStack = extractTechStack(text, category);
  const desc = job.description || '';
  const sentences = desc.split(/[.!?]/).filter(s => s.trim().length > 10).slice(0, 2);
  const understanding = sentences.length > 0 ? `Понял задачу: ${sentences.join('. ').trim()}.` : `Понял задачу: ${job.title}.`;
  const totalDays = (effortHours / 8).toFixed(1);

  const questions = [];
  if (!text.includes('срок') && !text.includes('дедлайн')) questions.push('Есть ли дедлайн?');
  if (['web_fullstack', 'web_frontend'].includes(category) && !text.includes('figma') && !text.includes('макет')) questions.push('Есть ли готовый дизайн?');
  if (category === 'telegram_bot') questions.push('Есть ли уже созданный бот через @BotFather?');
  if (category === 'parsing_scraping') questions.push('Какой объём данных?');
  questions.push('Остались ли требования, не отражённые в описании?');

  return `Здравствуйте!

Внимательно изучил ваше техническое задание.

${understanding}

━━━━━━━━━━━━━━━━━━━━

🛠 СТЕК: ${techStack.join(', ')}

📋 ПЛАН РЕАЛИЗАЦИИ:
1. Анализ ТЗ и проектирование (2-4ч)
2. Реализация основной функциональности (${Math.round(effortHours * 0.5)}ч)
3. Тестирование и отладка (${Math.round(effortHours * 0.15)}ч)
4. Документация и сдача (1-3ч)

⏱️ Общий срок: ~${totalDays} рабочих дней (~${effortHours}ч)
${rewardAnalysis.budgetAmount ? `💰 Бюджет: ${rewardAnalysis.budgetAmount} ${rewardAnalysis.budgetCurrency} — готов обсудить` : '💰 Бюджет: открыт к обсуждению'}

❓ ВОПРОСЫ:
${questions.slice(0, 4).map((q, i) => `${i+1}. ${q}`).join('\n')}

Готов приступить!
С уважением, ${profile?.user?.name || 'Ваш исполнитель'}`;
}

// ===================================================
// HTTP СЕРВЕР
// ===================================================

const profileData = loadProfile();
const servicesData = loadServicesInfo();

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/api/generate-response') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const { taskTitle, taskDescription, budget, skills } = JSON.parse(body);
        if (!taskTitle || !taskDescription) {
          res.writeHead(400, {'Content-Type': 'application/json'});
          res.end(JSON.stringify({ error: 'taskTitle и taskDescription обязательны' }));
          return;
        }

        const job = { title: taskTitle, description: taskDescription, budget: parseBudget(budget), skills: skills || [] };
        const analysis = analyzeTask(job, profileData, servicesData);
        
        let proposalText;
        if (analysis.feasible) {
          proposalText = generateProposal(job, analysis, profileData);
        } else {
          proposalText = `⛔ ЗАДАЧА НЕ РЕКОМЕНДОВАНА\n\nПричины:\n${analysis.blockers.map(b => `• ${b}`).join('\n')}`;
          if (!analysis.rewardAnalysis.worthIt) proposalText += `\n• ${analysis.rewardAnalysis.comment}`;
        }

        res.writeHead(200, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({
          success: true,
          response: proposalText,
          metadata: {
            source: 'scout-agent',
            generatedAt: new Date().toISOString(),
            analysis: {
              category: analysis.category,
              feasible: analysis.feasible,
              effortHours: analysis.effortHours,
              rewardAnalysis: analysis.rewardAnalysis,
              skillCoverage: analysis.skillCoverage,
              missingServices: analysis.missingServices,
              blockers: analysis.blockers,
            },
            warnings: analysis.warnings,
            operatorNotes: analysis.operatorNotes,
          }
        }, null, 2));
      } catch (e) {
        res.writeHead(500, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not found. Use POST /api/generate-response');
  }
});

const PORT = 3333;
server.listen(PORT, () => {
  console.log(`\n🤖 Scout Agent API запущен: http://localhost:${PORT}`);
  console.log(`\nТест:`)
  console.log(`curl -s -X POST http://localhost:${PORT}/api/generate-response \\`);
  console.log(`  -H "Content-Type: application/json" \\`);
  console.log(`  -d '{"taskTitle":"Telegram бот для магазина","taskDescription":"Нужен бот с каталогом товаров, корзиной, оплатой через ЮKassa. PostgreSQL.","budget":"25000 ₽"}' | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');const j=JSON.parse(d);console.log(j.response.substring(0,500));console.log('---');console.log(JSON.stringify(j.metadata.analysis,null,2))"`);
  console.log('');
});
