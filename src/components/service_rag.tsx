
import React from 'react';
import './ServicePage.css';

const RagService = () => {
  return (
    <div className="service-page">
      <header className="service-header">
        <h1>Умный поиск по документам</h1>
        <p className="subtitle">RAG-системы корпоративного уровня</p>
      </header>
      
      <section className="service-description">
        <p>Системы, которые понимают ваш бизнес и отвечают на вопросы сотрудников на основе внутренних документов, регламентов и базы знаний.</p>
      </section>
      
      <section className="service-section">
        <h2>❌ Ваши боли</h2>
        <ul className="pain-list">
          <li>Сотрудники тратят время на поиск информации</li><li>Знания разбросаны по разным системам</li><li>Новички долго осваивают процессы компании</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>✅ Наше решение</h2>
        <ul className="solution-list">
          <li>Единый поисковый интерфейс по всем документам</li><li>Ответы на естественном языке (как диалог с экспертом)</li><li>Интеграция с вашими базами знаний</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>🔧 Ключевые возможности</h2>
        <div className="features-grid">
          <div className='feature-card'><h3>📄 Работает с любыми документами</h3><p>PDF, Word, Excel, Confluence, Notion, Google Docs</p></div><div className='feature-card'><h3>🔍 Семантический поиск</h3><p>Понимает смысл, а не просто ключевые слова</p></div><div className='feature-card'><h3>⚡ Мгновенные ответы</h3><p>Находит и обобщает информацию за секунды</p></div><div className='feature-card'><h3>👤 Контроль доступа</h3><p>Сотрудники видят только доступное им</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>📊 Примеры использования</h2>
        <div className="use-cases">
          <div className='use-case'><h3>Корпоративная база знаний</h3><p>Централизованные ответы на все вопросы</p></div><div className='use-case'><h3>Техническая поддержка</h3><p>Поиск решений в документации</p></div><div className='use-case'><h3>Онбординг</h3><p>Новые сотрудники быстро находят нужную информацию</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>💻 Технологии</h2>
        <div className="tech-stack">
          <span className='tech-tag'>RAG</span><span className='tech-tag'>Vector DB</span><span className='tech-tag'>LLM</span><span className='tech-tag'>Embeddings</span><span className='tech-tag'>React</span>
        </div>
      </section>
      
      <div className="service-cta">
        <p>Ваша компания теряет часы на поиск информации?</p>
        <a href="#inquiry" className="btn-primary">Обсудить проект</a>
      </div>
    </div>
  );
}

export default RagService;
