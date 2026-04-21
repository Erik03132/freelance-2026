import { useState, useEffect, useCallback } from 'react';
import { Message, ChatState } from '../types/chat';

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

export const useChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: 'Привет! Я BureauBot. Помогу подобрать решение под ваш бизнес. С чего начнем?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState<ChatContext>({
    stage: 'greeting',
    leadData: {}
  });

  const toggleChat = () => setIsOpen(prev => !prev);

  const processLeadStage = useCallback(async (userInput: string) => {
    let nextStage: LeadStage = context.stage;
    let updatedData = { ...context.leadData };

    switch (context.stage) {
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
        nextStage = 'completed';
        break;
    }

    setContext({ stage: nextStage, leadData: updatedData });
    return nextStage;
  }, [context]);

  const sendMessage = useCallback(async () => {
    if (!input.trim()) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      // 1. Процессинг воронки (Lead Qualification)
      const nextStage = await processLeadStage(userMsg);

      // 2. Генерация ответа через AI
      const resp = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMsg,
          context: {
            stage: nextStage,
            leadData: context.leadData 
          }
        })
      });

      if (!resp.ok) throw new Error('Server error');
      const data = await resp.json();

      // 3. Формирование следующего вопроса на основе стадии
      let botReply = data.reply;
      
      if (nextStage === 'business_type') {
        botReply = `Принято. Расскажите кратко, какую задачу вы хотите решить с помощью ИИ?`;
      } else if (nextStage === 'task_description') {
        botReply = `Понятно. Какой примерный бюджет вы закладываете на внедрение?`;
      } else if (nextStage === 'budget') {
        botReply = `Последний шаг: оставьте ваш Telegram или Email, и наш архитектор свяжется с вами с готовым предложением.`;
      } else if (nextStage === 'completed') {
        botReply = `Спасибо! Данные переданы. Мы свяжемся с вами в течение 30 минут.`;
      }

      setMessages(prev => [...prev, { role: 'bot', text: botReply }]);
    } catch (e) {
      console.error('Chat error:', e);
      setMessages(prev => [...prev, { role: 'bot', text: 'Ошибка связи. Попробуйте еще раз.' }]);
    } finally {
      setLoading(false);
    }
  }, [input, context, processLeadStage]);

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
