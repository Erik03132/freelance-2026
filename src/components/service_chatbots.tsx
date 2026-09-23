
import React from 'react';
import './ServicePage.css';

const ChatbotsService = () => {
  return (
    <div className="service-page">
      <header className="service-header">
        <h1>Чат-боты и поддержка клиентов</h1>
        <p className="subtitle">Ответы 24/7 без задержек</p>
      </header>
      
      <section className="service-description">
        <p>AI-помощники для отдела продаж и поддержки, которые отвечают мгновенно и квалифицируют лиды.</p>
      </section>
      
      <section className="service-section">
        <h2>❌ Ваши боли</h2>
        <ul className="pain-list">
          <li>Клиенты ждут ответов часами</li><li>Операторы перегружены типовыми вопросами</li><li>Многие заявки не доходят до менеджеров</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>✅ Наше решение</h2>
        <ul className="solution-list">
          <li>Чат-боты отвечают мгновенно на любые вопросы</li><li>Типовые задачи автоматизируются</li><li>Квалифицированные лиды передаются менеджерам</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>🔧 Ключевые возможности</h2>
        <div className="features-grid">
          <div className='feature-card'><h3>⚡ Мгновенные ответы</h3><p>Ответы за секунды, 24/7</p></div><div className='feature-card'><h3>🎯 Квалификация лидов</h3><p>Сбор информации о клиенте и потребностях</p></div><div className='feature-card'><h3>🔗 Интеграции</h3><p>Работа с WhatsApp, Telegram, сайт, CRM</p></div><div className='feature-card'><h3>📊 Аналитика</h3><p>Отслеживание конверсии и вопросов</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>📊 Примеры использования</h2>
        <div className="use-cases">
          <div className='use-case'><h3>Отдел продаж</h3><p>Первичная консультация, квалификация, назначение встреч</p></div><div className='use-case'><h3>Техподдержка</h3><p>Ответы на частые вопросы, статус заказа</p></div><div className='use-case'><h3>HR</h3><p>Ответы кандидатов на вопросы о вакансиях</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>💻 Технологии</h2>
        <div className="tech-stack">
          <span className='tech-tag'>LLM</span><span className='tech-tag'>NLP</span><span className='tech-tag'>WhatsApp API</span><span className='tech-tag'>Telegram API</span><span className='tech-tag'>CRM</span>
        </div>
      </section>
      
      <div className="service-cta">
        <p>Клиенты ждут слишком долго?</p>
        <a href="#inquiry" className="btn-primary">Обсудить проект</a>
      </div>
    </div>
  );
}

export default ChatbotsService;
