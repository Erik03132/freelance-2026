import React, { useEffect, useState } from 'react';
import './index.css';
import Nav from './components/Nav';
import BureauBot from './components/BureauBot';
import InteractiveNeuralGraph from './components/InteractiveNeuralGraph';
import AiAgentsService from './components/service_ai-agents';
import RagService from './components/service_rag';
import DocumentAutomationService from './components/service_document-automation';
import ChatbotsService from './components/service_chatbots';
import PrivateLlmService from './components/service_private-llm';
import ConsultingService from './components/service_consulting';

const serviceMap = {
  'ai-agents': AiAgentsService,
  'rag': RagService,
  'document-automation': DocumentAutomationService,
  'chatbots': ChatbotsService,
  'private-llm': PrivateLlmService,
  'consulting': ConsultingService,
};

const App = () => {
  const [activeSection, setActiveSection] = useState('home');

  useEffect(() => {
    const schema = {
      "@context":"https://schema.org","@type":"Organization","name":"AI Bureau",
      "url":"https://ai-bureau.pro","logo":"https://ai-bureau.pro/logo.png",
      "description":"Специализированное инженерное бюро по проектированию автономных интеллектуальных систем и RAG-инфраструктур.",
      "contactPoint":{"@type":"ContactPoint","email":"architect@ai-bureau.pro","contactType":"customer support"},
      "offers":{"@type":"AggregateOffer","description":"AI Agents, RAG Systems, Private LLM Deployment"}
    };
    const s = document.createElement('script'); s.type = 'application/ld+json'; s.text = JSON.stringify(schema); document.head.appendChild(s);
    return () => document.head.removeChild(s);
  }, []);

  useEffect(() => {
    const h = () => { setActiveSection(window.location.hash.replace('#','') || 'home'); };
    window.addEventListener('hashchange', h); h();
    return () => window.removeEventListener('hashchange', h);
  const Active = serviceMap[activeSection as keyof typeof serviceMap];
  const ActiveService = Active ? Active : null;
  const Active = serviceMap[activeSection];

  return (
    <div className="app-container">
      <div className="progress-bar" /><div className="noise-overlay" />
      <Nav active={activeSection} />
      {activeSection !== 'home' && Active ? <Active /> : (
        <main>
          <section className="hero-split">
            <div className="hero-text">
              <span className="hero-label">Инженерное бюро</span>
              <h1>Архитектор<br/>интеллектуальных<br/>систем</h1>
              <p>Проектируем автономные нейронные инфраструктуры, преобразуя бизнес-процессы в эффективные цифровые экосистемы.</p>
              <div className="hero-actions">
                <a href="#inquiry" className="btn-primary">Заказать аудит</a>
                <a href="#services" className="btn-outline">Все услуги</a>
              </div>
            </div>
            <div className="hero-visual"><InteractiveNeuralGraph /></div>
          </section>

          <section id="services" className="section-services">
            <div className="section-header"><span className="section-number">01</span><h2>Наши услуги</h2></div>
            <div className="services-list">
              {[
                {id:'ai-agents',t:'AI-агенты',d:'Автономные цифровые сотрудники'},
                {id:'rag',t:'Умный поиск',d:'RAG-системы корпоративного уровня'},
                {id:'document-automation',t:'Документооборот',d:'Автоматизация обработки документов'},
                {id:'chatbots',t:'Чат-боты',d:'Поддержка клиентов 24/7'},
                {id:'private-llm',t:'Безопасные модели',d:'Приватное развёртывание LLM'},
                {id:'consulting',t:'AI-аудит',d:'Полный цикл внедрения ИИ'},
              ].map(s=> (
                <a key={s.id} href={`#${s.id}`} className="service-item">
                  <span className="service-num">{s.id}</span>
                  <div className="service-body"><h3>{s.t}</h3><p>{s.d}</p></div>
                </a>
              ))}
            </div>
          </section>

          <section id="governance" className="section-governance">
            <div className="section-header"><span className="section-number">02</span><h2>Суверенитет данных</h2></div>
            <div className="governance-grid">
              <div className="gov-card"><span className="gov-icon">⊘</span><h3>Air-gapped deployment</h3><p>Решения без внешней сети, полная конфиденциальность.</p></div>
              <div className="gov-card"><span className="gov-icon">⎔</span><h3>Ollama &amp; vLLM</h3><p>Оптимизация локальных моделей под ваш сервер.</p></div>
            </div>
          </section>

          <section id="hub" className="section-hub">
            <div className="section-header"><span className="section-number">03</span><h2>Хаб экспертизы</h2></div>
            <p className="hub-desc">Наш контент-завод транслирует экспертизу через Яндекс.Дзен и VK.</p>
            <div className="hub-scroll">
              {[{t:'Образование',h:'Технические гайды',d:'Разборы внедрения для инженеров'},{t:'Аналитика',h:'Кейсы и результаты',d:'Измеримые бизнес-результаты'},
                {t:'Исследования',h:'Обзоры рынка',d:'Дайджест open-source LLM'},
                {t:'Инструменты',h:'Open Source',d:'Компоненты для сообщества'}].map((c,i)=>(
                <div key={i} className="hub-card"><span className="hub-tag">{c.t}</span><h4>{c.h}</h4><p>{c.d}</p></div>
              ))}
            </div>
          </section>

          <section id="inquiry" className="section-inquiry">
            <div className="inquiry-content"><span className="section-number" style={{color:'oklch(0.6 0.15 85)',opacity:0.5}}>04</span><h2>Начать проектирование</h2><p>Опишите задачи — предложим план внедрения ИИ.</p><a href="mailto:architect@ai-bureau.pro" className="btn-primary">Запросить консультацию →</a></div>
          </section>

          <footer className="site-footer"><div className="footer-inner"><span className="footer-brand">AI BUREAU</span><span className="footer-tag">Архитекторы автономных систем</span><span className="footer-year">2026</span></div></footer>
        </main>
      )}
      <BureauBot />
    </div>
  );
};
export default App;
