import React, { useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { Message } from '../types/chat';

const BureauBot = () => {
  const {
    isOpen,
    setIsOpen,
    messages,
    input,
    setInput,
    loading,
    sendMessage,
    toggleChat,
    context
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  // Визуальный индикатор прогресса воронки
  const renderProgress = () => {
    const stages: { name: string; status: 'done' | 'active' | 'pending' }[] = [
      { name: 'Бизнес', status: context.stage !== 'greeting' ? 'done' : 'pending' },
      { name: 'Задача', status: context.stage === 'task_description' ? 'active' : (context.stage !== 'greeting' && context.stage !== 'business_type' ? 'done' : 'pending') },
      { name: 'Бюджет', status: context.stage === 'budget' ? 'active' : (context.stage !== 'greeting' && context.stage !== 'business_type' && context.stage !== 'task_description' ? 'done' : 'pending') },
      { name: 'Контакт', status: context.stage === 'contact_collection' ? 'active' : (context.stage === 'completed' ? 'done' : 'pending') },
    ];

    return (
      <div className="bot-progress">
        {stages.map((s, i) => (
          <div key={i} className={`progress-step ${s.status}`}>
            <div className="step-dot"></div>
            <span className="step-label">{s.name}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`chat-wrapper ${isOpen ? 'open' : ''}`}>
      {!isOpen && (
        <div className="chat-trigger" onClick={toggleChat}>
          <div className="trigger-pulse"></div>
          <span>AI</span>
        </div>
      )}

      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="header-info">
              <span className="status-indicator"></span>
              <h4>BUREAU_AGENT.sys</h4>
            </div>
            <button className="close-btn" onClick={toggleChat}>✕</button>
          </div>

          {renderProgress()}

          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={`${m.role}-${i}`} className={`msg ${m.role}`}>
                <div className="msg-content">{m.text}</div>
              </div>
            ))}
            {loading && (
              <div className="msg bot typing">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-inputbar">
            <input 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              onKeyDown={handleKeyDown}
              placeholder={context.stage === 'completed' ? "Сессия завершена" : "Спросите об услугах..."}
              disabled={context.stage === 'completed'}
            />
            <button 
              onClick={sendMessage}
              disabled={loading || context.stage === 'completed'}
            >
              {loading ? '...' : '→'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default BureauBot;
