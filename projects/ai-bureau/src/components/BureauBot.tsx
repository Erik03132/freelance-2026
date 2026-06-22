import React, { useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';

const BureauBot = () => {
  const {
    isOpen,
    setIsOpen,
    messages,
    input,
    setInput,
    loading,
    sendMessage,
    stage
  } = useChat();

  const dialogRef = useRef<HTMLDialogElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    if (isOpen) {
      el.showModal();
    } else {
      el.close();
    }
  }, [isOpen]);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    const onClose = () => setIsOpen(false);
    el.addEventListener('close', onClose);
    return () => el.removeEventListener('close', onClose);
  }, [setIsOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  const stages = [
    { name: 'Бизнес', status: stage !== 'greeting' ? 'done' as const : 'pending' as const },
    { name: 'Задача', status: stage === 'task_description' ? 'active' as const : (stage !== 'greeting' && stage !== 'business_type' ? 'done' as const : 'pending' as const) },
    { name: 'Бюджет', status: stage === 'budget' ? 'active' as const : (stage !== 'greeting' && stage !== 'business_type' && stage !== 'task_description' ? 'done' as const : 'pending' as const) },
    { name: 'Контакт', status: stage === 'contact_collection' ? 'active' as const : (stage === 'completed' ? 'done' as const : 'pending' as const) },
  ];

  return (
    <>
      <button
        className="chat-trigger"
        onClick={() => setIsOpen(true)}
        aria-label="Открыть чат"
        style={{ display: isOpen ? 'none' : 'flex' }}
      >
        AI
      </button>

      <dialog ref={dialogRef} className="chat-dialog">
        <div className="chat-header">
          <div className="header-info">
            <span className="status-indicator"></span>
            <h4>BUREAU_AGENT.sys</h4>
          </div>
          <button className="close-btn" onClick={() => setIsOpen(false)} aria-label="Закрыть чат">✕</button>
        </div>

        <div className="bot-progress">
          {stages.map((s, i) => (
            <div key={i} className={`progress-step ${s.status}`}>
              <div className="step-dot"></div>
              <span className="step-label">{s.name}</span>
            </div>
          ))}
        </div>

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
            placeholder={stage === 'completed' ? 'Сессия завершена' : 'Спросите об услугах...'}
            disabled={stage === 'completed'}
            autoFocus
          />
          <button
            onClick={sendMessage}
            disabled={loading || stage === 'completed'}
            aria-label="Отправить"
          >
            {loading ? '...' : '→'}
          </button>
        </div>
      </dialog>
    </>
  );
};

export default BureauBot;
