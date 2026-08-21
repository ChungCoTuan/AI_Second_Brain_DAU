import React, { useState } from 'react';
import { Send } from 'lucide-react';
import DocumentCard from '../components/shared/DocumentCard';
import CitationBadge from '../components/shared/CitationBadge';

const mockDocs = [
  { id: '1', title: 'Thông tư 08/2021/TT-BGDĐT Quy chế đào tạo trình độ đại học', type: 'Thông tư', date: '18/03/2021', status: 'success' as const, statusLabel: 'Còn hiệu lực', hasReport: true },
  { id: '2', title: 'Quyết định 123/QĐ-ĐHKT Quy định chuẩn đầu ra Tiếng Anh', type: 'Quyết định', date: '01/08/2022', status: 'success' as const, statusLabel: 'Còn hiệu lực', hasReport: false },
  { id: '3', title: 'Công văn 456/BGDĐT Về việc triển khai năm học 2023-2024', type: 'Công văn', date: '10/08/2023', status: 'warning' as const, statusLabel: 'Cần rà soát', hasReport: false },
];

const Dashboard: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'system', text: string, citation?: { id: string, text: string } }[]>([
    { role: 'system', text: 'Xin chào, tôi là trợ lý AI của DAU. Bạn muốn tìm kiếm hoặc hỏi đáp về quy chế đào tạo nào?' }
  ]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setIsLoading(true);
    setQuery('');

    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'system', 
        text: 'Theo Quy chế đào tạo trình độ đại học, sinh viên được xếp loại học lực dựa trên điểm trung bình tích lũy. Mức điểm từ 3.2 đến 3.59 hệ 4 được xếp loại Giỏi.', 
        citation: { id: '1', text: 'TT 08/2021, Điều 10, Khoản 3' }
      }]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="dashboard">
      <h2 className="page-title">Tra cứu & Hỏi đáp Quy chế</h2>
      
      <div className="dashboard-stats">
        <div className="card stat-card">
          <div className="stat-value">256</div>
          <div className="stat-label">Văn bản đã xử lý</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">92%</div>
          <div className="stat-label">Độ tin cậy (Faithfulness)</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">1,024</div>
          <div className="stat-label">Câu hỏi đã giải đáp</div>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.role === 'user' ? 'chat-user' : 'chat-system'}`}>
              <p>{msg.text}</p>
              {msg.citation && (
                <div style={{ marginTop: '0.5rem' }}>
                  <CitationBadge documentId={msg.citation.id} sourceText={msg.citation.text} />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble chat-system" style={{ color: 'var(--dau-gray)' }}>
              Đang tìm kiếm thông tin...
            </div>
          )}
        </div>
        <form className="chat-input-area" onSubmit={handleSearch}>
          <input 
            type="text" 
            className="chat-input"
            placeholder="Hỏi về quy chế, hoặc tìm kiếm số hiệu văn bản..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            <Send size={18} />
          </button>
        </form>
      </div>

      <h3 style={{ marginBottom: '1rem', color: 'var(--text-color)' }}>Văn bản nổi bật</h3>
      <div className="docs-grid">
        {mockDocs.map(doc => (
          <DocumentCard key={doc.id} {...doc} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
