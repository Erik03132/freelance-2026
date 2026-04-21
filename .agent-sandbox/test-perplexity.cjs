const { ScoutAgent } = require('./freelance-agent/dist/agents/scout');
const profile = require('./freelance-agent/config/profile.json');
const path = require('path');

async function run() {
  const job = {
    title: 'Написать парсер для объявлений на Wildberries',
    description: 'Нужно спарсить карточки товаров первой страницы по 10 популярным запросам на Python.',
    platform: 'kwork',
    url: 'https://kwork.ru/test'
  };

  const scout = new ScoutAgent(profile, path.join(__dirname, 'freelance-agent'));
  scout.services = {
    perplexity: { enabled: true, purpose: 'Search web facts', name: 'Perplexity', capabilities: [] }
  };

  console.log('Sherlock is thinking...');
  const result = await scout.analyzeAndProposeExpert(job);

  console.log('\n========= ПРЕДЛОЖЕНИЕ =========\n');
  console.log(result.proposal);
  
  console.log('\n========= ЗАМЕТКИ ДЛЯ ВАС =========\n');
  console.log(result.operatorNotes);
}

run().catch(console.error);
