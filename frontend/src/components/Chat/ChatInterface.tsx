import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { apiClient, endpoints } from '../../api/client';
import { Send, User, Bot, Loader2, Info } from 'lucide-react';
import clsx from 'clsx';

interface Message {
  role: 'user' | 'ai';
  text: string;
  summary?: string;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await apiClient.post(endpoints.chat, { query: userMsg });
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: res.data.answer,
        summary: res.data.summary 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: "Sorry, I encountered an error connecting to the server." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-[600px]">
      <div className="p-4 border-b bg-gray-50 rounded-t-xl">
        <h2 className="font-semibold text-gray-700 flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-600" /> AI Assistant
        </h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            Ask me anything about tennis stats! <br/>
            <span className="text-sm">"Who has the most aces in 2023?"</span>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={clsx("flex gap-3", msg.role === 'user' ? "flex-row-reverse" : "")}>
            <div className={clsx(
              "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
              msg.role === 'user' ? "bg-blue-100 text-blue-600" : "bg-green-100 text-green-600"
            )}>
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className={clsx(
              "p-3 rounded-lg max-w-[80%] text-sm leading-relaxed",
              msg.role === 'user' ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
            )}>
              {msg.role === 'ai' && msg.summary && (
                <div className="mb-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800 flex items-start gap-2">
                  <Info size={14} className="mt-0.5 flex-shrink-0" />
                  <span>{msg.summary}</span>
                </div>
              )}
              {msg.role === 'ai' ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="ml-2">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      code: ({ children }) => (
                        <code className="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                      pre: ({ children }) => (
                        <pre className="bg-gray-200 p-2 rounded text-xs overflow-x-auto mb-2">
                          {children}
                        </pre>
                      ),
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                </div>
              ) : (
                <span>{msg.text}</span>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin text-green-600" />
            </div>
            <div className="bg-gray-100 p-3 rounded-lg text-sm text-gray-500">Thinking...</div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="p-4 border-t">
        <div className="relative">
          <input
            type="text"
            className="w-full p-3 pr-12 bg-gray-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button 
            onClick={handleSend}
            disabled={loading}
            className="absolute right-2 top-2 p-1.5 text-blue-600 hover:bg-blue-50 rounded-md disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

