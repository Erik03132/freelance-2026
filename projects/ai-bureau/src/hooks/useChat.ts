import { useState, useCallback } from 'react';
import { Message } from '../types/chat';

export type LeadStage = 'greeting' | 'business_type' | 'task_description' | 'budget' | 'contact_collection' | 'completed';

export interface LeadData {
  businessType?: string;
  task?: string;
  budget?: string;
  contact?: string;
}

export const useChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: 'Привет! Я BureauBot. Помогу подобрать решение под ваш бизнес. Расскажите о вашей сфере деятельности.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState<LeadStage>('greeting');
  const [leadData, setLeadData] = useState<LeadData>({});

  const toggleChat = () => setIsOpen(prev => !prev);

  const sendMessage = useCallback(async () => {
    if (!input.trim()) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    // advance lead stage & capture answer
    let nextStage: LeadStage = stage;
    let updatedData = { ...leadData };

    switch (stage) {
      case 'greeting':
        nextStage = 'business_type';
        updatedData.businessType = userMsg;
        break;
      case 'business_type':
        nextStage = 'task_description';
        updatedData.task = userMsg;
        break;
      case 'task_description':
        nextStage = 'budget';
        updatedData.budget = userMsg;
        break;
      case 'budget':
        nextStage = 'contact_collection';
        updatedData.contact = userMsg;
        break;
      case 'contact_collection':
        nextStage = 'completed';
        break;
    }

    setStage(nextStage);
    setLeadData(updatedData);

    try {
      const resp = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          context: { stage: nextStage, leadData: updatedData }
        })
      });

      if (!resp.ok) throw new Error('Server error');
      const data = await resp.json();

      setMessages(prev => [...prev, { role: 'bot', text: data.reply }]);
    } catch (e) {
      console.error('Chat error:', e);
      setMessages(prev => [...prev, { role: 'bot', text: 'Ошибка связи. Попробуйте еще раз.' }]);
    } finally {
      setLoading(false);
    }
  }, [input, stage, leadData]);

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
    stage,
    leadData
  };
};
