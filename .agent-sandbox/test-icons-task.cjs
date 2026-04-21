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
      body: JSON.stringify({ 
        jobId: job.id,
        taskTitle: job.title,
        taskDescription: job.description,
        budget: job.budget_amount ? String(job.budget_amount) : ""
      })
    });

    const data = await res.json();
    
    if (!data.metadata) {
        console.log("SERVER RETURNED ERROR:", data);
        return;
    }

    const metadata = data.metadata;
    const executionPlan = metadata.executionPlan;
    
    console.log('--- ШАГ 1: АНАЛИЗ SHERLOCK ---');
    console.log(`Категория: ${metadata.analysis.category} => ОПРЕДЕЛИЛИ, КАКОЙ АГЕНТ НУЖЕН`);
    
    console.log('--- ШАГ 2: ПЛАН ДЛЯ ДАШБОРДА (EXECUTION PLAN) ---');
    console.log(`Всего минут: ${executionPlan.totalMinutes}`);
    console.log('Шаги:');
    executionPlan.roadmap.forEach((step, i) => {
      console.log(`  ${i+1}. [${step.agentName}] ${step.action} (~${step.minutes} мин)`);
    });
    console.log(`Обоснование: ${executionPlan.rationale}\n`);

    console.log('--- ШАГ 3: ИТОГОВЫЙ ОФФЕР (Сам текст заказчику) ---');
    console.log(data.response);

  } catch (error) {
    console.error('Ошибка:', error);
  }
}

testTask();
