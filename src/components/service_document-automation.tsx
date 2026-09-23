
import React from 'react';
import './ServicePage.css';

const DocumentAutomationService = () => {
  return (
    <div className="service-page">
      <header className="service-header">
        <h1>Автоматизация документооборота</h1>
        <p className="subtitle">От обработки до согласования</p>
      </header>
      
      <section className="service-description">
        <p>Автоматическая обработка, маршрутизация и согласование документов с минимальным участием человека.</p>
      </section>
      
      <section className="service-section">
        <h2>❌ Ваши боли</h2>
        <ul className="pain-list">
          <li>Документы теряются или долго обрабатываются</li><li>Согласование занимает дни</li><li>Человеческие ошибки при вводе данных</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>✅ Наше решение</h2>
        <ul className="solution-list">
          <li>AI распознаёт и структурирует данные из документов</li><li>Автоматическая маршрутизация по утверждённым流程</li><li>Контроль и уведомления на каждом этапе</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>🔧 Ключевые возможности</h2>
        <div className="features-grid">
          <div className='feature-card'><h3>📥 Распознавание</h3><p>Извлекает данные из сканов: счета, накладные, договоры</p></div><div className='feature-card'><h3>🔄 Маршрутизация</h3><p>Автоматически направляет документы нужным людям</p></div><div className='feature-card'><h3>✍️ Согласование</h3><p>Отслеживает статус и напоминает о сроках</p></div><div className='feature-card'><h3>📊 Отчётность</h3><p>Аналитика времени обработки документов</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>📊 Примеры использования</h2>
        <div className="use-cases">
          <div className='use-case'><h3>Бухгалтерия</h3><p>Обработка счетов, актов, накладных</p></div><div className='use-case'><h3>Юридический отдел</h3><p>Согласование и контроль договоров</p></div><div className='use-case'><h3>Логистика</h3><p>Обработка накладных и сопроводительных документов</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>💻 Технологии</h2>
        <div className="tech-stack">
          <span className='tech-tag'>OCR</span><span className='tech-tag'>LLM</span><span className='tech-tag'>Workflow</span><span className='tech-tag'>API</span><span className='tech-tag'>1C</span>
        </div>
      </section>
      
      <div className="service-cta">
        <p>Документы тормозят ваши бизнес-процессы?</p>
        <a href="#inquiry" className="btn-primary">Обсудить проект</a>
      </div>
    </div>
  );
}

export default DocumentAutomationService;
