import { useState, useCallback } from 'react';
import { Message } from '../types/chat';

type LeadStage = 'greeting' | 'business_type' | 'task_description' | 'budget' | 'contact_collection' | 'completed';

interface ChatContext {
  stage: LeadStage;
  leadData: {
    businessType?: string;
    task?: string;
    budget?: string;
    contact?: string;
  };
}

// В dev-режиме Astro проксирует /api/* на server.js (localhost:3001).
// В проде — указать VITE_API_URL на ваш RAG-сервер (или reverse-proxy).
const BASE_URL = import.meta.env.VITE_API_URL || '';
const API_URL = `${BASE_URL}/api/chat`;
const LEAD_URL = `${BASE_URL}/api/lead`;

// Подсказки, направляющие клиента к следующему шагу воронки.
// Раньше ответ ИИ полностью заменялся этой строкой — теперь склеиваем.
const STAGE_HINTS: Record<string, string> = {
  business_type: 'Расскажите кратко, какую задачу вы хотите решить с помощью ИИ?',
  task_description: 'Какой примерный бюджет вы закладываете на внедрение?',
  budget: 'Последний шаг: оставьте ваш Telegram или Email — архитектор свяжется с вами с готовым предложением.',
  contact_collection: '',
  completed: 'Спасибо! Данные переданы. Мы свяжемся с вами в течение 30 минут.',
};

export const useChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: 'Привет! Я BureauBot. Помогу подобрать решение под ваш бизнес. Чем занимается ваша компания?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState<ChatContext>({
    stage: 'greeting',
    leadData: {}
  });

  const toggleChat = () => setIsOpen(prev => !prev);

  // Продвигает клиента по воронке квалификации и фиксирует данные лида.
  const processLeadStage = useCallback((userInput: string, currentStage: LeadStage): {
    nextStage: LeadStage;
    leadData: ChatContext['leadData'];
  } => {
    let nextStage: LeadStage = currentStage;
    const updatedData = { ...context.leadData };

    switch (currentStage) {
      case 'greeting':
        nextStage = 'business_type';
        updatedData.businessType = userInput;
        break;
      case 'business_type':
        nextStage = 'task_description';
        updatedData.task = userInput;
        break;
      case 'task_description':
        nextStage = 'budget';
        updatedData.budget = userInput;
        break;
      case 'budget':
        nextStage = 'contact_collection';
        updatedData.contact = userInput;
        break;
      case 'contact_collection':
        // Контакт собирается на этой стадии — фиксируем его.
        updatedData.contact = userInput;
        nextStage = 'completed';
        break;
    }

    return { nextStage, leadData: updatedData };
  }, [context.leadData]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      // 1. Продвигаем воронку на основе ТЕКУЩЕЙ стадии.
      const { nextStage, leadData } = processLeadStage(userMsg, context.stage);
      setContext({ stage: nextStage, leadData });

      // 2. Шлём на сервер ВСЮ историю диалога + новый вопрос (память!)
      //    Раньше уходило только последнее сообщение — бот переспрашивал.
      const resp = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          context: {
            stage: nextStage,
            leadData,
          },
          messages: [...messages, { role: 'user', text: userMsg }].map(m => ({
            role: m.role,
            text: m.text,
          })),
        })
      });

      if (!resp.ok) throw new Error(`Server error ${resp.status}`);
      const data = await resp.json();

      // 3. Склеиваем реальный AI-ответ с подсказкой следующего шага.
      //    Раньше AI-ответ полностью выбрасывался — теперь он в основе.
      let botReply = data.reply?.trim() || '';
      const hint = STAGE_HINTS[nextStage];

      if (nextStage === 'completed') {
        botReply = STAGE_HINTS.completed;
        // Лид уже отправлен сервером по funnelContext.stage === 'completed',
        // но дублируем через /api/lead на случай, если воронка завершилась
        // без полного прохода (надёжность сохранения лида важнее экономии запроса).
        fetch(LEAD_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ leadData, messages: [...messages, { role: 'user', text: userMsg }] }),
        }).catch((e) => console.error('Lead submit error:', e));
      } else if (hint && !botReply.toLowerCase().includes(hint.toLowerCase().slice(0, 20))) {
        // Если AI не упомянул нужный следующий шаг — аккуратно добавляем его.
        botReply = `${botReply}\n\n${hint}`.trim();
      }

      setMessages(prev => [...prev, { role: 'bot', text: botReply }]);
    } catch (e) {
      console.error('Chat error:', e);
      setMessages(prev => [...prev, { role: 'bot', text: 'Ошибка связи. Попробуйте ещё раз.' }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, context, messages, processLeadStage]);

  return {
    isOpen,
    setIsOpen,
    messages,
    setMessages,
    input,
    setInput,
    loading,
    sendMessage,
    toggleChat,
    context
  };
};
