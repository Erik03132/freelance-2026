import React, { useState, useRef, useEffect } from 'react'
import { Button, Card, Input, Avatar, AvatarFallback } from '@blinkdotnew/ui'
import { MessageSquare, X, Send, Bot, Minimize2, Maximize2 } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { knowledgeBase } from '../data/knowledge'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Привет! Я Ульяна. Готова ответить на любой вопрос по грантам, налогам или банкротству со ссылками на законы. Что вас интересует?',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isTyping, isOpen])

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isTyping) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    // Отправка запроса на наш новый бэкенд (Live Verification RAG)
    fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input })
    })
    .then(res => res.json())
    .then(data => {
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMsg])
      setIsTyping(false)
    })
    .catch(err => {
      console.error("Ошибка AI-Ульяны:", err)
      setIsTyping(false)
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: "Извините, произошла техническая заминка. Пожалуйста, попробуйте еще раз через минуту.",
        timestamp: new Date()
      }])
    })
  }

  const getMockResponse = (query: string) => {
    const q = query.toLowerCase().trim()
    
    let bestDoc = null
    let maxScore = 0

    knowledgeBase.forEach(doc => {
      let score = 0
      const content = doc.content.toLowerCase()
      const title = doc.title.toLowerCase()
      
      title.split(' ').forEach(word => {
        if (word.length > 3 && q.includes(word.substring(0, 4))) score += 5
      })

      const words = q.split(' ')
      words.forEach(word => {
        if (word.length > 3 && content.includes(word.substring(0, 4))) {
          score += 1
        }
      })

      if (score > maxScore) {
        maxScore = score
        bestDoc = doc
      }
    })

    if (maxScore > 2 && bestDoc) {
      return (bestDoc as any).content
    }

    return "Интересная задача. Чтобы я нашла точный ответ со ссылкой на НПА, уточните: вы физлицо или ООО? И какова примерная сумма гранта/вычета?"
  }

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 h-16 w-16 rounded-full bg-cyan-400 text-slate-900 shadow-[0_0_30px_rgba(6,182,212,0.4)] flex items-center justify-center hover:scale-110 transition-all z-[100] group"
      >
        <MessageSquare size={28} />
        <span className="absolute -top-1 -right-1 flex h-4 w-4">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[8px] font-bold text-white flex items-center justify-center">1</span>
        </span>
        <div className="absolute right-20 bg-slate-900 border border-white/10 px-4 py-2 rounded-xl whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none text-xs font-medium text-white shadow-2xl">
           Ульяна на связи
        </div>
      </button>
    )
  }

  return (
    <div className={`fixed right-8 bottom-8 z-[100] transition-all duration-300 transform ${isMinimized ? 'h-14 w-64' : 'h-[500px] w-96'} flex flex-col`}>
      <Card className="flex-grow glass-panel rounded-3xl border border-white/10 shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 bg-slate-900/80 border-b border-white/5 flex items-center justify-between">
           <div className="flex items-center gap-3">
              <div className="relative">
                <Avatar className="h-8 w-8 border border-cyan-500/30">
                   <div className="bg-cyan-500/10 h-full w-full flex items-center justify-center text-cyan-400">
                      <Bot size={16} />
                   </div>
                </Avatar>
                <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 bg-green-500 border-2 border-slate-900 rounded-full"></div>
              </div>
              <div>
                 <h4 className="text-[11px] font-bold text-white uppercase tracking-wider mb-0.5">Ульяна Эксперт</h4>
                 <p className="text-[8px] text-cyan-400 uppercase font-bold tracking-widest leading-none">RAG-Base Active</p>
              </div>
           </div>
           <div className="flex items-center gap-1">
              <button 
                onClick={() => setIsMinimized(!isMinimized)} 
                className="p-1.5 hover:bg-white/5 rounded-lg text-slate-500 hover:text-white transition-colors"
              >
                {isMinimized ? <Maximize2 size={14} /> : <Minimize2 size={14} />}
              </button>
              <button 
                onClick={() => setIsOpen(false)} 
                className="p-1.5 hover:bg-white/5 rounded-lg text-slate-500 hover:text-white transition-colors"
              >
                <X size={14} />
              </button>
           </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-slate-800 bg-[#030712]/50">
               {messages.map((msg) => (
                 <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                   <div className={`max-w-[85%] rounded-2xl p-3 text-[13px] leading-relaxed ${
                     msg.role === 'assistant' 
                       ? 'bg-slate-800/80 border border-white/5 text-slate-200' 
                       : 'bg-cyan-500/20 border border-cyan-500/30 text-white'
                   }`}>
                      {msg.content}
                   </div>
                 </div>
               ))}
               {isTyping && (
                 <div className="flex justify-start">
                    <div className="bg-slate-800/80 border border-white/5 rounded-2xl px-4 py-2">
                       <div className="flex gap-1">
                          <div className="w-1 h-1 bg-cyan-400/50 rounded-full animate-bounce"></div>
                          <div className="w-1 h-1 bg-cyan-400/50 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                          <div className="w-1 h-1 bg-cyan-400/50 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                       </div>
                    </div>
                 </div>
               )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/5 bg-slate-900/50">
               <form onSubmit={handleSend} className="relative flex items-center">
                  <Input 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ваш вопрос..." 
                    className="w-full bg-slate-800/40 border-slate-700/50 rounded-xl pr-10 py-5 text-xs font-light text-white focus:border-cyan-500/50"
                  />
                  <button 
                    type="submit" 
                    className="absolute right-2 text-cyan-400 hover:text-cyan-300 disabled:opacity-30"
                    disabled={!input.trim() || isTyping}
                  >
                    <Send size={16} />
                  </button>
               </form>
               <div className="mt-3 flex justify-between items-center px-1">
                  <span className="text-[8px] font-bold text-slate-600 uppercase tracking-widest">Verified Expert Unit</span>
                  <Link to="/ai-consult" className="text-[8px] font-bold text-cyan-500/60 hover:text-cyan-400 uppercase tracking-widest underline underline-offset-2">Развернуть на весь экран</Link>
               </div>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
