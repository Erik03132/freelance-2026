
import React from 'react';
import './ServicePage.css';

const PrivateLlmService = () => {
  return (
    <div className="service-page">
      <header className="service-header">
        <h1>Развертывание безопасных моделей</h1>
        <p className="subtitle">Private LLM внутри вашей сети</p>
      </header>
      
      <section className="service-description">
        <p>Локальное развёртывание LLM внутри корпоративной сети для максимальной безопасности данных.</p>
      </section>
      
      <section className="service-section">
        <h2>❌ Ваши боли</h2>
        <ul className="pain-list">
          <li>Невозможность отправлять данные в облако</li><li>Требования законодательства (152-ФЗ)</li><li>Страх утечки интеллектуальной собственности</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>✅ Наше решение</h2>
        <ul className="solution-list">
          <li>Полностью локальные решения без выхода в интернет</li><li>Оптимизированные модели под ваше оборудование</li><li>Полный контроль над данными</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>🔧 Ключевые возможности</h2>
        <div className="features-grid">
          <div className='feature-card'><h3>🔒 Air-gapped</h3><p>Работает без доступа к внешней сети</p></div><div className='feature-card'><h3>⚡ Высокая производительность</h3><p>Оптимизация под ваше GPU/CPU</p></div><div className='feature-card'><h3>📦 Гибкость</h3><p>Любые модели: Llama, Mistral, и другие</p></div><div className='feature-card'><h3>💰 Экономия</h3><p>Один раз - использование неограниченно</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>📊 Примеры использования</h2>
        <div className="use-cases">
          <div className='use-case'><h3>Государственные организации</h3><p>Соответствие требованиям регуляторов</p></div><div className='use-case'><h3>Финансы</h3><p>Работа с конфиденциальными данными</p></div><div className='use-case'><h3>Консалтинг</h3><p>Защита интеллектуальной собственности</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>💻 Технологии</h2>
        <div className="tech-stack">
          <span className='tech-tag'>Ollama</span><span className='tech-tag'>vLLM</span><span className='tech-tag'>Llama</span><span className='tech-tag'>Docker</span><span className='tech-tag'>NVIDIA</span>
        </div>
      </section>
      
      <div className="service-cta">
        <p>Требования безопасности ограничивают использование ИИ?</p>
        <a href="#inquiry" className="btn-primary">Обсудить проект</a>
      </div>
    </div>
  );
}

export default PrivateLlmService;
