import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, CheckCircle, MessageSquare, ArrowRight } from 'lucide-react';
import { ChatBubble } from '../components/shared/Chat';
import { DocumentCard } from '../components/shared/Card';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { 
      isUser: true, 
      message: 'Quy định về thời gian đào tạo tối đa của hệ tín chỉ?' 
    },
    { 
      isUser: false, 
      message: 'Theo Quy chế đào tạo đại học hệ chính quy theo hệ thống tín chỉ, thời gian tối đa để sinh viên hoàn thành khoá học được quy định như sau:\n\n- Thời gian tối đa = Thời gian thiết kế của khoá học + 2 năm (4 học kỳ chính) đối với các khoá học từ 4 đến 5 năm.\n- Thời gian tối đa = Thời gian thiết kế của khoá học + 1 năm (2 học kỳ chính) đối với các khoá học từ 2 đến 3 năm.', 
      citations: [{ id: '1', source: 'Quy chế 43/2007/QĐ-BGDĐT, Điều 6' }, { id: '2', source: 'Quy chế 01/2021/QĐ-ĐHKT, Điều 4' }] 
    }
  ]);

  const recentDocs = [
    { id: '1', title: 'Quy chế đào tạo đại học hệ chính quy theo hệ thống tín chỉ', type: 'Quy chế', topic: 'Đào tạo', status: 'published' as const, date: '15/08/2026' },
    { id: '2', title: 'Quy định mức thu học phí năm học 2026-2027', type: 'Quy định', topic: 'Tài chính - Học phí', status: 'published' as const, date: '10/08/2026' },
    { id: '3', title: 'Thông báo xét cấp học bổng khuyến khích học tập', type: 'Thông báo', topic: 'Tuyển sinh', status: 'published' as const, date: '05/08/2026' },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setChatHistory([...chatHistory, { isUser: true, message: query }]);
    setQuery('');
    
    // Giả lập trả lời
    setTimeout(() => {
      setChatHistory(prev => [...prev, {
        isUser: false,
        message: 'Tôi đang tìm kiếm thông tin liên quan...',
      }]);
      
      setTimeout(() => {
        setChatHistory(prev => [
          ...prev.slice(0, -1),
          {
            isUser: false,
            message: 'Không tìm thấy thông tin liên quan đến câu hỏi của bạn. Vui lòng thử lại với từ khóa khác.',
          }
        ]);
      }, 1500);
    }, 500);
  };

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <h1 className="title-h1">Dashboard Tra Cứu & Hỏi Đáp</h1>
      
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
        <div className="card hover-lift" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', borderRadius: 'var(--radius-full)' }}>
            <FileText size={24} />
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>1,248</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Văn bản đã xử lý</div>
          </div>
        </div>
        <div className="card hover-lift" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-success-light)', color: 'var(--color-success-text)', borderRadius: 'var(--radius-full)' }}>
            <CheckCircle size={24} />
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>96.5%</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Độ tin cậy (Faithfulness)</div>
          </div>
        </div>
        <div className="card hover-lift" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-warning-light)', color: 'var(--color-warning-text)', borderRadius: 'var(--radius-full)' }}>
            <MessageSquare size={24} />
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>342</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Câu hỏi đã trả lời (Tháng)</div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Chat / Search */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '600px', padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)' }}>
            <h2 className="title-h2" style={{ margin: 0 }}>Trợ lý AI Second Brain</h2>
          </div>
          
          <div style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
            {chatHistory.map((chat, idx) => (
              <ChatBubble 
                key={idx} 
                isUser={chat.isUser} 
                message={chat.message} 
                citations={chat.citations} 
                onCitationClick={(id) => navigate(`/document/${id}`)}
              />
            ))}
          </div>
          
          <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', position: 'relative' }}>
              <div style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
                <Search size={20} />
              </div>
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Hỏi bất cứ thông tin quy chế, quy định nào..." 
                style={{ 
                  flex: 1, 
                  padding: '1rem 1rem 1rem 3rem', 
                  borderRadius: 'var(--radius-full)', 
                  border: '1px solid var(--border-color)',
                  outline: 'none',
                  fontSize: '1rem',
                  boxShadow: 'var(--shadow-sm)'
                }} 
              />
              <button type="submit" style={{ 
                backgroundColor: 'var(--color-primary)', 
                color: 'white', 
                width: '56px', 
                height: '56px', 
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                boxShadow: 'var(--shadow-md)',
                transition: 'all var(--transition-fast)'
              }}>
                <ArrowRight size={24} />
              </button>
            </form>
          </div>
        </div>

        {/* Recent Docs */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '600px', overflowY: 'auto' }}>
          <h2 className="title-h2" style={{ margin: 0 }}>Văn bản gần đây</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {recentDocs.map(doc => (
              <DocumentCard 
                key={doc.id} 
                {...doc} 
                onClick={() => navigate(`/document/${doc.id}`)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
