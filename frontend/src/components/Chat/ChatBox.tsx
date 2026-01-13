import React, { useState } from 'react';
import { Message } from './Message';
import { apiClient, endpoints } from '../../api/client';
import { Send } from 'lucide-react';

export const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<{ role: 'user' | 'ai', text: string }[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 1. Add User Message
    const newMessages = [...messages, { role: 'user', text: input }];
    setMessages(newMessages as any);
    setInput('');
    setLoading(true);

    try {
      // 2. Call Python API
      const response = await apiClient.post(endpoints.chat, { query: input });
      
      // 3. Add AI Response
      setMessages([...newMessages, { role: 'ai', text: response.data.answer }] as any);
    } catch (error) {
      setMessages([...newMessages, { role: 'ai', text: "Error connecting to server." }] as any);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-gray-50 border rounded-xl shadow-sm overflow-hidden">
      {/* Message History */}
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, idx) => (
          <Message key={idx} role={msg.role} text={msg.text} />
        ))}
        {loading && <div className="text-gray-400 text-sm animate-pulse">AI is thinking...</div>}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t flex gap-2">
        <input
          className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about tennis stats..."
        />
        <button onClick={handleSend} className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700">
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

