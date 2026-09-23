
import React from 'react';
import './ServicePage.css';

const AiAgentsService = () => {
  return (
    <div className="service-page">
      <header className="service-header">
        <h1>AI-агенты для бизнес-процессов</h1>
        <p className="subtitle">Автономные цифровые сотрудники</p>
      </header>
      
      <section className="service-description">
        <p>Разработка и внедрение автономных AI-агентов, способных к самостоятельному выполнению задач, принятию решений и интеграции в существующие бизнес-процессы.</p>
      </section>
      
      <section className="service-section">
        <h2>❌ Ваши боли</h2>
        <ul className="pain-list">
          <li>Сотрудники тратят часы на рутинные задачи</li><li>CRM/ERP системы работают без автоматизации</li><li>Требуются персонализированные ассистенты для разных отделов</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>✅ Наше решение</h2>
        <ul className="solution-list">
          <li>Разработка агентов под конкретные задачи (продажи, поддержка, финансы)</li><li>Интеграция с CRM/ERP, Slack, Email и другими системами</li><li>Полная автономность - агент работает 24/7 без надзора</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>🔧 Ключевые возможности</h2>
        <div className="features-grid">
          <div className='feature-card'><h3>🧠 Логический вывод</h3><p>Агент принимает решения на основе контекста и правил</p></div><div className='feature-card'><h3>🔗 Интеграции</h3><p>Работает с вашими системами: 1С, Bitrix24, amoCRM, Notion</p></div><div className='feature-card'><h3>📊 Самообучение</h3><p>Улучшает работу на основе обратной связи и анализа</p></div><div className='feature-card'><h3>🔐 Безопасность</h3><p>Работает внутри вашей сети без утечки данных</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>📊 Примеры использования</h2>
        <div className="use-cases">
          <div className='use-case'><h3>Отдел продаж</h3><p>Квалификация лидов, ответы на запросы, ведение сделок</p></div><div className='use-case'><h3>Техподдержка</h3><p>Обработка тикетов, ответы на частые вопросы</p></div><div className='use-case'><h3>HR-процессы</h3><p>Онбординг новых сотрудников, ответы на вопросы</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>💻 Технологии</h2>
        <div className="tech-stack">
          <span className='tech-tag'>Python</span><span className='tech-tag'>LangChain</span><span className='tech-tag'>LLM</span><span className='tech-tag'>API</span><span className='tech-tag'>Docker</span>
        </div>
      </section>
      
      <div className="service-cta">
        <p>Хотите внедрить AI-агентов в ваши процессы?</p>
        <a href="#inquiry" className="btn-primary">Обсудить проект</a>
      </div>
    </div>
  );
}

export default AiAgentsService;
