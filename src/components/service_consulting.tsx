
import React from 'react';
import './ServicePage.css';

const ConsultingService = () => {
  return (
    <div className="service-page">
      <header className="service-header">
        <h1>AI-аудит и внедрение</h1>
        <p className="subtitle">От идеи до результата</p>
      </header>
      
      <section className="service-description">
        <p>Диагностика бизнес-процессов, подбор сценариев автоматизации и полный цикл внедрения ИИ.</p>
      </section>
      
      <section className="service-section">
        <h2>❌ Ваши боли</h2>
        <ul className="pain-list">
          <li>Непонятно, с чего начать внедрение ИИ</li><li>Опасения насчёт ROI</li><li>Не хватает экспертизы</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>✅ Наше решение</h2>
        <ul className="solution-list">
          <li>Аудит процессов и поиск точек применения ИИ</li><li>Расчёт ROI и плана внедрения</li><li>Полный цикл: от идеи до результата</li>
        </ul>
      </section>
      
      <section className="service-section">
        <h2>🔧 Ключевые возможности</h2>
        <div className="features-grid">
          <div className='feature-card'><h3>🔍 Диагностика</h3><p>Анализ процессов и выявление возможностей</p></div><div className='feature-card'><h3>📊 ROI-анализ</h3><p>Оценка затрат и выгод</p></div><div className='feature-card'><h3>📋 План внедрения</h3><p>Пошаговый план на 3-6 месяцев</p></div><div className='feature-card'><h3>🤝 Сопровождение</h3><p>Поддержка на всех этапах</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>📊 Примеры использования</h2>
        <div className="use-cases">
          <div className='use-case'><h3>Стартапы</h3><p>Быстрое внедрение MVP с ИИ</p></div><div className='use-case'><h3>Enterprise</h3><p>Постепенное внедрение по департаментам</p></div><div className='use-case'><h3>Консалтинг</h3><p>Подготовка к цифровизации</p></div>
        </div>
      </section>
      
      <section className="service-section">
        <h2>💻 Технологии</h2>
        <div className="tech-stack">
          <span className='tech-tag'>Consulting</span><span className='tech-tag'>Project Management</span><span className='tech-tag'>ROI Analysis</span>
        </div>
      </section>
      
      <div className="service-cta">
        <p>Не знаете с чего начать?</p>
        <a href="#inquiry" className="btn-primary">Обсудить проект</a>
      </div>
    </div>
  );
}

export default ConsultingService;
