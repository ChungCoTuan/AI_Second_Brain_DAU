import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Loader } from 'lucide-react';
import { useDetail } from '../context/DetailContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = localStorage.getItem('chat_history');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Lỗi đọc lịch sử chat:", e);
      }
    }
    return [
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Xin chào! Tôi là Trợ lý AI của DAU Second Brain. Bạn có thể hỏi tôi bất kỳ thông tin nào về các Thông tư, Quy chế đã được duyệt (Published). Ví dụ: "Chuẩn chương trình đào tạo quy định thế nào?"'
      }
    ];
  });

  useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(messages));
  }, [messages]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { openDetail } = useDetail();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content })
      });
      
      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Lỗi khi chat:", error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Xin lỗi, đã có lỗi kết nối đến máy chủ. Vui lòng thử lại sau."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="tra-cuu-ai" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 40px)', padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2>Tra cứu AI (RAG Chatbot)</h2>
        <p className="sub">Hỏi đáp dựa trên CSDL Vector. Mọi câu trả lời đều có trích dẫn từ văn bản gốc để chống Ảo giác (Hallucination).</p>
      </div>

      <div style={{ flex: 1, backgroundColor: 'var(--card-bg)', borderRadius: '12px', border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* Chat History */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {messages.map((msg) => (
            <div key={msg.id} style={{ display: 'flex', gap: '16px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
              <div style={{ 
                width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                backgroundColor: msg.role === 'user' ? 'var(--blue)' : 'var(--amber-bg)',
                color: msg.role === 'user' ? 'white' : 'var(--amber)'
              }}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              
              <div style={{ maxWidth: '75%', display: 'flex', flexDirection: 'column', gap: '8px', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{ 
                  padding: '12px 16px', borderRadius: '16px',
                  backgroundColor: msg.role === 'user' ? 'var(--blue)' : '#f8fafc',
                  color: msg.role === 'user' ? 'white' : 'var(--text)',
                  border: msg.role === 'user' ? 'none' : '1px solid var(--border)',
                  lineHeight: '1.6', fontSize: '15px'
                }}>
                  {msg.content}
                </div>
                
                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '4px' }}>
                    <span style={{ fontSize: '13px', color: 'var(--muted)', alignSelf: 'center' }}>Nguồn:</span>
                    {msg.citations.map((cit, idx) => (
                      <span 
                        key={idx} 
                        className="badge" 
                        style={{ background: 'var(--green-bg)', color: 'var(--green)', borderColor: '#bbf7d0', cursor: 'pointer' }}
                        onClick={() => openDetail(cit.vb)}
                        title={cit.nguon}
                      >
                        <FileText size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }}/>
                        {cit.vb} ({cit.dieu})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: 'var(--amber-bg)', color: 'var(--amber)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={20} />
              </div>
              <div style={{ padding: '12px 16px', borderRadius: '16px', backgroundColor: '#f8fafc', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Loader size={16} className="spin" style={{ color: 'var(--amber)' }} />
                <span style={{ color: 'var(--muted)', fontSize: '14px' }}>Đang tìm kiếm thông tin...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '16px', borderTop: '1px solid var(--border)', backgroundColor: '#f8fafc' }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <input 
              type="text" 
              className="inp" 
              placeholder="Bạn muốn hỏi gì về văn bản quy phạm pháp luật?" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              style={{ flex: 1, padding: '12px 16px', borderRadius: '24px', fontSize: '15px' }}
              disabled={isLoading}
            />
            <button 
              className="btn" 
              style={{ width: '48px', height: '48px', borderRadius: '50%', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: input.trim() ? 'var(--blue)' : 'var(--muted)', color: 'white' }}
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
      
      {/* CSS cho hiệu ứng xoay (Loader) */}
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </section>
  );
};

export default Chat;
