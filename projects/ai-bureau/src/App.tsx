import React, { useEffect } from 'react';
import './index.css';
import BureauBot from './components/BureauBot';
import InteractiveNeuralGraph from './components/InteractiveNeuralGraph';

const App = () => {
  useEffect(() => {
    const schema = {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "AI Bureau",
      "url": "https://ai-bureau.pro",
      "logo": "https://ai-bureau.pro/logo.png",
      "description": "Специализированное инженерное бюро по проектированию автономных интеллектуальных систем и RAG-инфраструктур.",
      "contactPoint": { "@type": "ContactPoint", "email": "architect@ai-bureau.pro", "contactType": "customer support" },
      "offers": { "@type": "AggregateOffer", "description": "AI Agents, RAG Systems, Private LLM Deployment" }
    };
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
    return () => { document.head.removeChild(script); };
  }, []);

  return (
    <div className="app-container">
      <div className="progress-bar"></div>
      <div className="noise-overlay"></div>

      <nav className="nav-bar">
        <div className="nav-brand">
          <svg className="nav-logo" width="28" height="28" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.3"/>
            <circle cx="50" cy="20" r="2" fill="currentColor" opacity="0.6"><animate attributeName="opacity" values="0.2;1;0.2" dur="3s" repeatCount="indefinite"/></circle>
            <circle cx="80" cy="50" r="2" fill="currentColor" opacity="0.6"><animate attributeName="opacity" values="0.2;1;0.2" dur="3s" begin="0.6s" repeatCount="indefinite"/></circle>
            <circle cx="50" cy="80" r="2" fill="currentColor" opacity="0.6"><animate attributeName="opacity" values="0.2;1;0.2" dur="3s" begin="1.2s" repeatCount="indefinite"/></circle>
            <circle cx="20" cy="50" r="2" fill="currentColor" opacity="0.6"><animate attributeName="opacity" values="0.2;1;0.2" dur="3s" begin="1.8s" repeatCount="indefinite"/></circle>
            <line x1="50" y1="20" x2="80" y2="50" stroke="currentColor" strokeWidth="0.3" opacity="0.15"/>
            <line x1="80" y1="50" x2="50" y2="80" stroke="currentColor" strokeWidth="0.3" opacity="0.15"/>
            <line x1="50" y1="80" x2="20" y2="50" stroke="currentColor" strokeWidth="0.3" opacity="0.15"/>
            <line x1="20" y1="50" x2="50" y2="20" stroke="currentColor" strokeWidth="0.3" opacity="0.15"/>
          </svg>
          <span>AI BUREAU</span>
        </div>
        <div className="nav-links">
          <a href="#services">Услуги</a>
          <a href="#governance">Безопасность</a>
          <a href="#hub">Хаб</a>
          <a href="#inquiry" className="nav-cta">Консультация</a>
        </div>
      </nav>

      <section className="hero-split">
        <div className="hero-text">
          <span className="hero-label">Инженерное бюро</span>
          <h1>Архитектор<br/>интеллектуальных<br/>систем</h1>
          <p>Проектируем автономные нейронные инфраструктуры, преобразуя бизнес-процессы в эффективные цифровые экосистемы.</p>
          <div className="hero-actions">
            <a href="#inquiry" className="btn-primary">Заказать аудит</a>
            <a href="#services" className="btn-outline">Возможности</a>
          </div>
        </div>
        <div className="hero-visual">
          <InteractiveNeuralGraph />
        </div>
      </section>

      <section id="services" className="section-services">
        <div className="section-header">
          <span className="section-number">01</span>
          <h2>Компетенции</h2>
        </div>
        <div className="services-list">
          <article className="service-item">
            <span className="service-num">01</span>
            <div className="service-body">
              <h3>Автономные AI-агенты</h3>
              <p>Разработка агентов-исполнителей, способных к самостоятельному логическому выводу и интеграции в CRM/ERP контуры без внешнего контроля.</p>
            </div>
          </article>
          <article className="service-item">
            <span className="service-num">02</span>
            <div className="service-body">
              <h3>Нейронные базы знаний</h3>
              <p>RAG-системы корпоративного уровня. Семантическая память вашего бизнеса, обеспечивающая мгновенный доступ к экспертизе.</p>
            </div>
          </article>
          <article className="service-item">
            <span className="service-num">03</span>
            <div className="service-body">
              <h3>eCommerce интеллект</h3>
              <p>Автоматизация товарных матриц и SEO-доминирования на маркетплейсах через масштабируемую генерацию на базе LLM.</p>
            </div>
          </article>
          <article className="service-item">
            <span className="service-num">04</span>
            <div className="service-body">
              <h3>Private model ops</h3>
              <p>Развертывание локальных моделей внутри закрытого периметра компании для абсолютной безопасности данных.</p>
            </div>
          </article>
        </div>
      </section>

      <section id="governance" className="section-governance">
        <div className="governance-inner">
          <div className="section-header">
            <span className="section-number">02</span>
            <h2>Суверенитет данных</h2>
          </div>
          <div className="governance-grid">
            <div className="gov-card">
              <span className="gov-icon">⊘</span>
              <h3>Air-gapped deployment</h3>
              <p>Решения, не требующие доступа к внешней сети. Ваша интеллектуальная собственность остаётся вашей.</p>
            </div>
            <div className="gov-card">
              <span className="gov-icon">⎔</span>
              <h3>Ollama &amp; vLLM</h3>
              <p>Экспертиза в оптимизации локальных моделей для максимальной производительности на корпоративном оборудовании.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="hub" className="section-hub">
        <div className="section-header">
          <span className="section-number">03</span>
          <h2>Хаб экспертизы</h2>
        </div>
        <p className="hub-desc">Наш контент-завод транслирует экспертизу через Яндекс.Дзен и VK, формируя экосистему знаний в области прикладного интеллекта.</p>
        <div className="hub-scroll">
          <div className="hub-card">
            <span className="hub-tag">Образование</span>
            <h4>Технические гайды</h4>
            <p>Архитектурные разборы внедрения AI-агентов для инженеров.</p>
          </div>
          <div className="hub-card">
            <span className="hub-tag">Аналитика</span>
            <h4>Кейсы и результаты</h4>
            <p>Измеримые бизнес-результаты перехода от ручного труда к AI-автономии.</p>
          </div>
          <div className="hub-card">
            <span className="hub-tag">Исследования</span>
            <h4>Обзоры рынка</h4>
            <p>Еженедельный дайджест новинок в мире open-source LLM и агентов.</p>
          </div>
          <div className="hub-card">
            <span className="hub-tag">Инструменты</span>
            <h4>Open Source</h4>
            <p>Наши наработки и компоненты для сообщества AI-разработчиков.</p>
          </div>
        </div>
      </section>

      <section id="inquiry" className="section-inquiry">
        <div className="inquiry-content">
          <span className="section-number" style={{color: 'oklch(0.6 0.15 85)', opacity: 0.5}}>04</span>
          <h2>Начать проектирование</h2>
          <p>Опишите текущие задачи вашей инфраструктуры, и мы предложим прагматичный план внедрения ИИ.</p>
          <a href="mailto:architect@ai-bureau.pro" className="btn-primary">Запросить консультацию →</a>
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-inner">
          <span className="footer-brand">AI BUREAU</span>
          <span className="footer-tag">Архитекторы автономных систем</span>
          <span className="footer-year">2026</span>
        </div>
      </footer>

      <BureauBot />
    </div>
  );
};

export default App;
