import React, { useState, useEffect, useRef } from 'react'
import { Container, Button, Card, Input, Avatar, AvatarFallback, Skeleton } from '@blinkdotnew/ui'
import { Link } from '@tanstack/react-router'
import { Send, User as UserIcon, Bot, ArrowLeft, RefreshCw, ShieldCheck } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function AIConsultPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Здравствуйте! Я Ульяна, ваш эксперт по грантам и финансовой защите. Чем я могу помочь вашему проекту сегодня?',
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
  }, [messages, isTyping])

  const handleSend = async (e: React.FormEvent) => {
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

    // Send request to the smart backend
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

  return (
    <div className="pb-24 pt-40 min-h-screen bg-[#030712]">
      <Container>
        <div className="max-w-4xl mx-auto flex flex-col h-[70vh]">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
               <Link to="/" className="h-10 w-10 glass-panel rounded-full flex items-center justify-center text-slate-400 hover:text-white transition-colors">
                  <ArrowLeft size={18} />
               </Link>
               <div>
                  <h1 className="text-2xl font-medium text-white tracking-tight leading-none mb-1">Ульяна Эксперт</h1>
                  <span className="text-[10px] text-cyan-400 uppercase font-bold tracking-widest flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                    RAG-Engine Active
                  </span>
               </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border border-white/5 bg-white/5 text-slate-500 text-[10px] uppercase font-bold tracking-widest">
                <ShieldCheck size={14} className="text-cyan-500" />
                Secure Analysis Stream
            </div>
          </div>

          {/* Chat Box */}
          <Card className="flex-grow glass-panel rounded-3xl border border-white/5 overflow-hidden flex flex-col relative">
             <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/[0.02] to-transparent pointer-events-none"></div>
             
             <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800">
                {messages.map((msg) => (
                  <div key={msg.id} className={`flex items-start gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <Avatar className={`h-10 w-10 border shadow-lg ${msg.role === 'assistant' ? 'border-cyan-500/30' : 'border-slate-700'}`}>
                      {msg.role === 'assistant' ? (
                        <div className="bg-cyan-500/10 h-full w-full flex items-center justify-center">
                            <Bot size={20} className="text-cyan-400" />
                        </div>
                      ) : (
                        <AvatarFallback className="bg-slate-800 text-[10px]">USER</AvatarFallback>
                      )}
                    </Avatar>
                    <div className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed ${
                      msg.role === 'assistant' 
                        ? 'bg-slate-900/50 border border-white/5 text-slate-200' 
                        : 'bg-cyan-500/10 border border-cyan-500/20 text-white italic'
                    }`}>
                        {msg.content}
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex items-start gap-4">
                     <Avatar className="h-10 w-10 border border-cyan-500/30">
                        <div className="bg-cyan-500/10 h-full w-full flex items-center justify-center">
                            <Bot size={20} className="text-cyan-400" />
                        </div>
                     </Avatar>
                     <div className="bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-3 ml-1">
                        <div className="flex gap-1">
                           <div className="w-1.5 h-1.5 bg-cyan-400/50 rounded-full animate-bounce"></div>
                           <div className="w-1.5 h-1.5 bg-cyan-400/50 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                           <div className="w-1.5 h-1.5 bg-cyan-400/50 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                        </div>
                     </div>
                  </div>
                )}
             </div>

             {/* Input Area */}
             <div className="p-6 border-t border-white/5 pt-4 bg-slate-900/20">
                <form onSubmit={handleSend} className="relative flex items-center">
                    <Input 
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Спросите Ульяну о грантах или налогах..." 
                      className="w-full bg-slate-800/40 border-slate-700/50 rounded-2xl pr-16 h-14 text-sm font-light text-white focus:border-cyan-500/50"
                    />
                    <button 
                      type="submit" 
                      disabled={isTyping || !input.trim()}
                      className="absolute right-2 h-10 w-10 bg-cyan-400 hover:bg-cyan-500 text-slate-900 rounded-xl flex items-center justify-center transition-all disabled:opacity-50 disabled:grayscale"
                    >
                      <Send size={18} />
                    </button>
                </form>
                <div className="mt-4 flex items-center justify-center gap-4 text-[9px] font-bold uppercase tracking-[0.2em] text-slate-600">
                    <span className="flex items-center gap-1"><RefreshCw size={10} /> Context Real-time sync</span>
                    <span className="flex items-center gap-1"><ShieldCheck size={10} /> NDA Encrypted</span>
                </div>
             </div>
          </Card>
        </div>
      </Container>
    </div>
  )
}
