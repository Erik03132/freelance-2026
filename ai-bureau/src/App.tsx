import React, { useEffect } from 'react';
import './index.css';
import BureauBot from './components/BureauBot';

const App = () => {
  useEffect(() => {
    const schema = {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "AI Bureau",
      "url": "https://ai-bureau.pro",
      "logo": "https://ai-bureau.pro/logo.png",
      "description": "Специализированное инженерное бюро по проектированию автономных интеллектуальных систем и RAG-инфраструктур.",
      "contactPoint": {
        "@type": "ContactPoint",
        "email": "architect@ai-bureau.pro",
        "contactType": "customer support"
      },
      "offers": {
        "@type": "AggregateOffer",
        "description": "AI Agents, RAG Systems, Private LLM Deployment"
      }
    };

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  return (
    <div className="app-container">
      <div className="bg-gradient"></div>
      <div className="grain"></div>
      
      <header className="header">
        <div className="logo-group">
          <svg className="neural-logo" width="40" height="40" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(0,240,255,0.2)" strokeWidth="1"/>
            <circle className="dot d1" cx="50" cy="20" r="3" fill="#00f0ff" />
            <circle className="dot d2" cx="80" cy="50" r="3" fill="#00f0ff" />
            <circle className="dot d3" cx="50" cy="80" r="3" fill="#00f0ff" />
            <circle className="dot d4" cx="20" cy="50" r="3" fill="#00f0ff" />
            <circle className="dot d5" cx="50" cy="50" r="5" fill="#00f0ff" />
            <line x1="50" y1="20" x2="50" y2="50" stroke="rgba(0,240,255,0.3)" />
            <line x1="80" y1="50" x2="50" y2="50" stroke="rgba(0,240,255,0.3)" />
            <line x1="50" y1="80" x2="50" y2="50" stroke="rgba(0,240,255,0.3)" />
            <line x1="20" y1="50" x2="50" y2="50" stroke="rgba(0,240,255,0.3)" />
          </svg>
          <div className="logo-text">AI BUREAU</div>
        </div>
        <nav className="nav">
          <a href="#solutions">Решения</a>
          <a href="#governance">Безопасность</a>
          <a href="#hub">Хаб</a>
          <a href="#inquiry" className="btn-contact">Запрос</a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <span className="hero-pre">Инновационное Инженерное Бюро</span>
            <h1>Архитектор <br /> Интеллектуальных Систем</h1>
            <p>
              Мы проектируем автономные нейронные инфраструктуры, 
              преобразуя бизнес-процессы в эффективные цифровые экосистемы.
            </p>
            <div className="cta-group">
              <a href="#inquiry" className="btn-primary">Заказать Аудит</a>
              <a href="#solutions" className="btn-secondary">Архитектура Решений</a>
            </div>
          </div>
        </section>

        <section id="solutions">
          <span className="section-tag">Ключевые Компетенции / 2026</span>
          <h2>Инженерные Решения</h2>
          <div className="architect-grid">
            <div className="architect-card">
              <h3>Автономные AI-Агенты</h3>
              <p>Разработка агентов-исполнителей, способных к самостоятельному логическому выводу и интеграции в CRM/ERP контуры без внешнего контроля.</p>
            </div>
            <div className="architect-card">
              <h3>Нейронные Базы Знаний</h3>
              <p>RAG-системы корпоративного уровня. Семантическая память вашего бизнеса, обеспечивающая мгновенный доступ к экспертизе.</p>
            </div>
            <div className="architect-card">
              <h3>eCommerce Интеллект</h3>
              <p>Автоматизация товарных матриц и SEO-доминирования на маркетплейсах через масштабируемую генерацию на базе LLM.</p>
            </div>
            <div className="architect-card">
              <h3>Private Model Ops</h3>
              <p>Развертывание локальных моделей (Gemma 2, Llama 3) внутри закрытого периметра компании для абсолютной безопасности данных.</p>
            </div>
          </div>
        </section>

        <section id="governance" style={{ background: '#050505', borderRadius: '40px' }}>
          <span className="section-tag">Governance & Security</span>
          <h2>Суверенитет Данных</h2>
          <div className="architect-grid">
            <div className="architect-card">
              <h3>Air-Gapped Deployment</h3>
              <p>Мы специализируемся на решениях, которые не требуют доступа к внешней сети. Ваша интеллектуальная собственность остается вашей.</p>
            </div>
            <div className="architect-card">
              <h3>Ollama & vLLM Infrastructure</h3>
              <p>Экспертиза в оптимизации локальных моделей для максимальной производительности на корпоративном оборудовании.</p>
            </div>
          </div>
        </section>

        <section id="hub">
          <span className="section-tag">Хаб Экспертизы</span>
          <h2>Нейронные Инсайты</h2>
          <p style={{ color: '#888', marginBottom: '4rem', maxWidth: '600px' }}>
            Наш контент-завод транслирует экспертизу через Яндекс.Дзен и VK, 
            формируя экосистему знаний в области прикладного интеллекта.
          </p>
          <div className="architect-grid">
            <div className="architect-card">
              <h4>Образовательный Контент</h4>
              <p>Технические гайды и архитектурные разборы внедрения AI-агентов.</p>
            </div>
            <div className="architect-card">
              <h4>Кейсы и Аналитика</h4>
              <p>Демонстрация измеримых бизнес-результатов перехода от ручного труда к AI-автономии.</p>
            </div>
          </div>
        </section>

        <section id="inquiry" className="hero" style={{ height: 'auto', padding: '10rem 0' }}>
          <div className="hero-content">
            <span className="hero-pre">Системное Партнерство</span>
            <h2>Начать Проектирование</h2>
            <p>Опишите текущие задачи вашей инфраструктуры, и мы предложим прагматичный план внедрения ИИ.</p>
            <a href="mailto:architect@ai-bureau.pro" className="btn-primary" style={{ marginTop: '2rem', display: 'inline-block' }}>
              Запросить Консультацию
            </a>
          </div>
        </section>
      </main>

      <footer style={{ padding: '4rem 10%', borderTop: '1px solid rgba(255,255,255,0.05)', textAlign: 'center', fontSize: '0.7rem', color: '#444' }}>
        AI BUREAU © 2026. АРХИТЕКТОРЫ АВТОНОМНЫХ СИСТЕМ.
      </footer>

      <BureauBot />
    </div>
  );
};

export default App;
