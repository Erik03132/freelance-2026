
import React, { useState } from 'react';
import './Nav.css';

const ServiceNav = () => {
  const [active, setActive] = useState('home');

  const services = [
    { id: 'ai-agents', name: 'AI-агенты' },
    { id: 'rag', name: 'Умный поиск' },
    { id: 'document-automation', name: 'Документооборот' },
    { id: 'chatbots', name: 'Чат-боты' },
    { id: 'private-llm', name: 'Безопасные модели' },
    { id: 'consulting', name: 'AI-аудит' }
  ];

  return (
    <nav className="service-nav">
      <div className="nav-container">
        <a href="#home" className={active === 'home' ? 'nav-item active' : 'nav-item'}>
          Главная
        </a>
        {services.map(s => (
          <a
            key={s.id}
            href={`#${s.id}`}
            className={active === s.id ? 'nav-item active' : 'nav-item'}
            onClick={() => setActive(s.id)}
          >
            {s.name}
          </a>
        ))}
      </div>
    </nav>
  );
};

export default ServiceNav;
