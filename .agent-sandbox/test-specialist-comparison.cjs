/**
 * Тест: сравнение ScoutAgent (legacy) vs Specialist Agent (new)
 * 
 * Запуск: node test-specialist-comparison.js
 * (после компиляции: npx tsc && node test-specialist-comparison.js)
 * 
 * Пока без компиляции — показываем логику в чистом JS
 */

// === Симуляция задачи с биржи ===

const testJobs = [
  {
    id: 'test-1',
    title: 'Разработать REST API для интернет-магазина',
    description: 'Нужно разработать REST API на FastAPI с JWT авторизацией, CRUD для товаров, корзина, заказы. PostgreSQL, Docker. Swagger документация. Должна быть пагинация и фильтрация.',
    platform: 'kwork',
    url: 'https://kwork.ru/test-1',
    budget: { amount: 15000, currency: 'RUB' },
    skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
    postedAt: new Date().toISOString(),
  },
  {
    id: 'test-2',
    title: 'Telegram бот для записи на услуги',
    description: 'Нужен Telegram бот для салона красоты. Запись на услуги, выбор мастера, выбор времени. Напоминания за час до записи. Админка для мастеров. Оплата через ЮKassa.',
    platform: 'kwork',
    url: 'https://kwork.ru/test-2',
    budget: { amount: 12000, currency: 'RUB' },
    skills: ['Python', 'Telegram Bot', 'aiogram'],
    postedAt: new Date().toISOString(),
  },
  {
    id: 'test-3',
    title: 'Лендинг для стоматологической клиники',
    description: 'Нужен лендинг для стоматологии. Услуги, врачи, отзывы, форма записи. Современный дизайн, адаптивная вёрстка. SEO оптимизация. Next.js или React.',
    platform: 'kwork',
    url: 'https://kwork.ru/test-3',
    budget: { amount: 8000, currency: 'RUB' },
    skills: ['React', 'Next.js', 'CSS'],
    postedAt: new Date().toISOString(),
  },
  {
    id: 'test-4',
    title: 'Парсинг данных с сайта объявлений + дашборд',
    description: 'Нужно спарсить данные о ценах на квартиры с Avito (Москва) за последние 3 месяца. Данные загрузить в базу и сделать дашборд с графиками цен по районам.',
    platform: 'kwork',
    url: 'https://kwork.ru/test-4',
    budget: { amount: 10000, currency: 'RUB' },
    skills: ['Python', 'Playwright', 'React'],
    postedAt: new Date().toISOString(),
  },
];

// === Симуляция WebDev Agent ===

function simulateWebDevRecommendations(job) {
  const text = `${job.title} ${job.description}`.toLowerCase();
  const stack = [];

  // Автоматический выбор с обоснованием
  if (text.includes('fastapi')) {
    stack.push({ name: 'FastAPI', reason: 'Async из коробки = высокая производительность. Автоматическая OpenAPI документация. Pydantic v2 для валидации' });
  } else if (text.includes('next') || text.includes('seo') || text.includes('лендинг')) {
    stack.push({ name: 'Next.js 14 (App Router)', reason: 'SSR/SSG из коробки — критично для SEO. Server Components сокращают bundle size на 30-40%' });
  }

  if (text.includes('postgresql') || text.includes('postgres')) {
    stack.push({ name: 'PostgreSQL', reason: 'Надёжная, ACID-совместимая БД. JSON-поддержка, full-text search из коробки' });
  }

  if (text.includes('jwt') || text.includes('авторизац')) {
    stack.push({ name: 'JWT (python-jose) + passlib', reason: 'Stateless авторизация — масштабируется без сервера сессий' });
  }

  if (text.includes('docker')) {
    stack.push({ name: 'Docker + Docker Compose', reason: 'Единое dev/prod окружение. Деплой в 1 команду' });
  }

  return stack;
}

function simulateRoutingDecision(job) {
  const text = `${job.title} ${job.description}`.toLowerCase();
  
  if (text.includes('telegram') && text.includes('бот')) {
    return { agent: '🤖 Bot Agent', support: [], mode: 'single' };
  }
  if (text.includes('парсинг') || text.includes('спарсить')) {
    const support = text.includes('дашборд') || text.includes('график') ? ['💻 WebDev'] : [];
    return { agent: '📊 Data Agent', support, mode: support.length ? 'sequential' : 'single' };
  }
  if (text.includes('лендинг') || text.includes('сайт')) {
    const support = text.includes('дизайн') || text.includes('современн') ? ['🎨 Design'] : [];
    return { agent: '💻 WebDev Agent', support, mode: support.length ? 'sequential' : 'single' };
  }
  return { agent: '💻 WebDev Agent', support: [], mode: 'single' };
}

// === ВЫВОД СРАВНЕНИЯ ===

console.log('═══════════════════════════════════════════════════════');
console.log('  СРАВНЕНИЕ: ScoutAgent (legacy) vs Specialist (new)');
console.log('═══════════════════════════════════════════════════════\n');

for (const job of testJobs) {
  console.log(`\n${'━'.repeat(55)}`);
  console.log(`📌 ${job.title}`);
  console.log(`💰 ${job.budget.amount} ${job.budget.currency}`);
  console.log(`${'━'.repeat(55)}`);

  // --- Маршрутизация ---
  const routing = simulateRoutingDecision(job);
  console.log(`\n🔀 МАРШРУТИЗАЦИЯ:`);
  console.log(`   Основной: ${routing.agent}`);
  if (routing.support.length > 0) {
    console.log(`   Поддержка: ${routing.support.join(', ')} (${routing.mode})`);
  }

  // --- Стек (сравнение) ---
  console.log(`\n📊 СТЕК (legacy vs expert):`);
  
  // Legacy — хардкод стек
  const legacyStack = job.skills.join(', ');
  console.log(`   Legacy:  ${legacyStack}`);
  
  // Expert — стек с обоснованиями
  const expertStack = simulateWebDevRecommendations(job);
  if (expertStack.length > 0) {
    console.log(`   Expert:`);
    for (const t of expertStack) {
      console.log(`     • ${t.name}`);
      console.log(`       → ${t.reason}`);
    }
  }

  // --- План (preview) ---
  console.log(`\n📋 ПЛАН:`);
  console.log(`   Legacy: 4-5 шаблонных этапов без объяснений`);
  console.log(`   Expert: каждый этап с "rationale" + canAutomate + automationTool`);

  // --- Прототип ---
  const text = `${job.title} ${job.description}`.toLowerCase();
  if (text.includes('api') || text.includes('backend')) {
    console.log(`\n🎁 ПРОТОТИП: api (30%)`);
    console.log(`   ✅ 5 CRUD endpoints + Swagger + Docker`);
    console.log(`   📝 Осталось: авторизация, бизнес-логика, тесты`);
  } else if (text.includes('telegram') && text.includes('бот')) {
    console.log(`\n🎁 ПРОТОТИП: shop-bot (30%)`);
    console.log(`   ✅ /start + каталог (3 товара) + корзина + inline-кнопки`);
    console.log(`   📝 Осталось: оплата, админка, рассылки`);
  } else if (text.includes('лендинг')) {
    console.log(`\n🎁 ПРОТОТИП: landing (35%)`);
    console.log(`   ✅ Hero + блок преимуществ + CTA + responsive`);
    console.log(`   📝 Осталось: формы, аналитика, SEO мета-теги`);
  } else if (text.includes('парсинг') || text.includes('спарсить')) {
    console.log(`\n🎁 ПРОТОТИП: parser (30%)`);
    console.log(`   ✅ Скрипт, парсящий 10-20 записей + CSV-файл`);
    console.log(`   📝 Осталось: полный сбор, дашборд, графики`);
  }
}

console.log(`\n\n${'═'.repeat(55)}`);
console.log('  ИТОГО: Структура файлов агентов');
console.log(`${'═'.repeat(55)}\n`);

const fs = require('fs');
const path = require('path');

const agentFiles = [
  'freelance-agent/src/agents/specialists/base.ts',
  'freelance-agent/src/agents/specialists/router.ts',
  'freelance-agent/src/agents/specialists/webdev.ts',
  'freelance-agent/src/agents/specialists/bot.ts',
  'freelance-agent/src/agents/specialists/index.ts',
  'freelance-agent/src/agents/scout.ts',
];

let totalLines = 0;
for (const f of agentFiles) {
  try {
    const content = fs.readFileSync(f, 'utf-8');
    const lines = content.split('\n').length;
    totalLines += lines;
    const status = f.includes('scout') ? '(обновлён ✏️)' : '(новый ✅)';
    console.log(`  ${status} ${f}: ${lines} строк`);
  } catch(e) {
    console.log(`  ❌ ${f}: не найден`);
  }
}

console.log(`\n  Всего: ${totalLines} строк агентного кода`);
console.log(`\n  analyzeAndPropose()      → legacy (шаблоны)`);
console.log(`  analyzeAndProposeExpert() → Router → Specialist → Expert Proposal`);
