const job = {
  id: 1001,
  title: 'Создать три иконки',
  description: 'создать три иконки по аналогии светофора - запрещено, Разрешено, и Внимание по теме - интерфейс приложения КУЛИНАРИЯ!',
  budget_amount: null
};

async function testTask() {
  console.log('--- ОТПРАВЛЯЕМ ЗАДАЧУ ---');
  console.log(`Название: ${job.title}`);
  console.log(`Описание: ${job.description}\n`);

  try {
    const res = await fetch('http://localhost:3000/api/generate-response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job })
    });

    const data = await res.json();
    
    console.log('--- ШАГ 1: АНАЛИЗ SHERLOCK ---');
    console.log(`Категория: ${data.analysis.category} => ОПРЕДЕЛИЛИ, КАКОЙ АГЕНТ НУЖЕН`);
    console.log(`Скилл/понятность: ${(data.analysis.scores.skillMatch * 100).toFixed()}% / ${(data.analysis.scores.clarity * 100).toFixed()}%\n`);
    
    console.log('--- ШАГ 2: ПЛАН ДЛЯ ДАШБОРДА (EXECUTION PLAN) ---');
    console.log(`Всего минут: ${data.executionPlan.totalMinutes}`);
    console.log('Шаги:');
    data.executionPlan.steps.forEach((step: any, i: number) => {
      console.log(`  ${i+1}. [${step.agentEmoji} ${step.agentName}] ${step.action} (~${step.minutes} мин)`);
    });
    console.log(`Обоснование: ${data.executionPlan.pricingRationale}\n`);

    console.log('--- ШАГ 3: ИТОГОВЫЙ ОФФЕР (Сам текст заказчику) ---');
    console.log(data.offerText);

  } catch (error) {
    console.error('Ошибка:', error);
  }
}

testTask();
