import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, X, Bot, User } from 'lucide-react';
import api from '../services/api';

function ChatBot({ ticker }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: "👋 Hi! I'm your TradeWise AI Assistant. Ask me anything about trading, predictions, or your portfolio!",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.chatbot({ message: input, ticker });
      
      const botMessage = {
        type: 'bot',
        text: response.data.response.message,
        quickReplies: response.data.response.quick_replies,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      setMessages(prev => [...prev, {
        type: 'bot',
        text: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReply = (reply) => {
    setInput(reply);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white p-4 rounded-full shadow-2xl z-50 transform hover:scale-110 transition-all"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl z-50 flex flex-col border border-white/20">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 rounded-t-2xl flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-full">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white">TradeWise AI</h3>
            <p className="text-xs text-white/80">Your Trading Assistant</p>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:bg-white/20 p-2 rounded-full transition-all"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index}>
            <div className={`flex items-start space-x-2 ${msg.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`p-2 rounded-full ${msg.type === 'bot' ? 'bg-indigo-600' : 'bg-purple-600'}`}>
                {msg.type === 'bot' ? <Bot className="w-4 h-4 text-white" /> : <User className="w-4 h-4 text-white" />}
              </div>
              <div className={`flex-1 ${msg.type === 'user' ? 'text-right' : ''}`}>
                <div className={`inline-block p-3 rounded-2xl ${
                  msg.type === 'bot' 
                    ? 'bg-white/20 text-white' 
                    : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
                }`}>
                  <p className="text-sm whitespace-pre-line">{msg.text}</p>
                </div>
                {msg.quickReplies && (
                  <div className="mt-2 space-y-1">
                    {msg.quickReplies.map((reply, i) => (
                      <button
                        key={i}
                        onClick={() => handleQuickReply(reply)}
                        className="block text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-1 rounded-full transition-all"
                      >
                        {reply}
                      </button>
                    ))}
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  {msg.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2">
            <div className="bg-indigo-600 p-2 rounded-full">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-white/20 p-3 rounded-2xl">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/20">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything..."
            className="flex-1 bg-white/10 border border-white/20 rounded-full px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white p-2 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatBot;