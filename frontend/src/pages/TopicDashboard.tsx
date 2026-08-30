import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, AlertTriangle, BookOpen, Users, Banknote, Building, FileQuestion, ArrowLeft } from 'lucide-react';
import { TopicCard, DocumentCard } from '../components/shared/Card';
import type { DocStatus } from '../components/shared/Badge';

const TopicDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);

  const pendingCount = 12;

  const topics = [
    { id: 'dao-tao', title: 'Đào tạo', count: 450, icon: <BookOpen size={24} /> },
    { id: 'tuyen-sinh', title: 'Tuyển sinh', count: 120, icon: <Users size={24} /> },
    { id: 'tai-chinh', title: 'Tài chính - Học phí', count: 85, icon: <Banknote size={24} /> },
    { id: 'nhan-su', title: 'Nhân sự', count: 210, icon: <Users size={24} /> },
    { id: 'co-so-vat-chat', title: 'Cơ sở vật chất', count: 54, icon: <Building size={24} /> },
    { id: 'chua-phan-loai', title: 'Chưa phân loại', count: 18, icon: <FileQuestion size={24} /> },
  ];

  const mockDocs = [
    { id: '1', title: 'Quy chế đào tạo đại học hệ chính quy theo hệ thống tín chỉ', type: 'Quy chế', topic: 'Đào tạo', status: 'published' as DocStatus, date: '15/08/2026' },
    { id: '2', title: 'Quy định quản lý điểm sinh viên hệ chính quy', type: 'Quy định', topic: 'Đào tạo', status: 'pending_review' as DocStatus, date: '20/08/2026' },
    { id: '3', title: 'Hướng dẫn thực hiện khóa luận tốt nghiệp', type: 'Hướng dẫn', topic: 'Đào tạo', status: 'published' as DocStatus, date: '22/08/2026' },
  ];

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      {/* Banner "Cần rà soát" */}
      {pendingCount > 0 && (
        <div 
          className="card hover-lift" 
          onClick={() => navigate('/review')}
          style={{ 
            backgroundColor: 'var(--color-danger-light)', 
            borderColor: 'var(--color-danger)',
            color: 'var(--color-danger-text)',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            cursor: 'pointer'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <AlertTriangle size={24} />
            <div>
              <h3 style={{ margin: 0, fontSize: '1.125rem' }}>Có {pendingCount} văn bản đang chờ rà soát</h3>
              <p style={{ margin: 0, fontSize: '0.875rem', opacity: 0.8 }}>Bấm vào đây để đi tới màn hình Rà soát & Duyệt</p>
            </div>
          </div>
          <button style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: 'var(--color-danger)', 
            color: 'white', 
            borderRadius: 'var(--radius-md)',
            fontWeight: 600
          }}>
            Xử lý ngay
          </button>
        </div>
      )}

      {!selectedTopic ? (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 className="title-h1" style={{ margin: 0 }}>Dashboard theo chủ đề</h1>
            <button className="hover-lift" style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              backgroundColor: 'var(--color-primary)', 
              color: 'white', 
              padding: '0.75rem 1.5rem', 
              borderRadius: 'var(--radius-md)',
              fontWeight: 600
            }}>
              <UploadCloud size={20} />
              Nạp văn bản mới
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
            {topics.map(topic => (
              <TopicCard 
                key={topic.id} 
                title={topic.title} 
                count={topic.count} 
                icon={topic.icon} 
                onClick={() => setSelectedTopic(topic.id)}
              />
            ))}
          </div>

          <div className="card">
            <h2 className="title-h2">Hàng đợi xử lý</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontWeight: 500 }}>Quyết định ban hành khung học phí 2026.pdf</span>
                <span className="badge badge-warning">Đang trích xuất OCR...</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem' }}>
                <span style={{ fontWeight: 500 }}>Kế hoạch tuyển sinh bổ sung đợt 2.docx</span>
                <span className="badge badge-primary-light">Đang phân loại chủ đề...</span>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button 
              onClick={() => setSelectedTopic(null)} 
              className="icon-btn hover-lift" 
              style={{ 
                padding: '0.5rem', 
                backgroundColor: 'var(--bg-surface)', 
                border: '1px solid var(--border-color)', 
                borderRadius: '50%' 
              }}
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="title-h1" style={{ margin: 0 }}>Chủ đề: {topics.find(t => t.id === selectedTopic)?.title}</h1>
          </div>
          
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {mockDocs.map(doc => (
              <DocumentCard 
                key={doc.id} 
                {...doc} 
                onClick={() => navigate(`/document/${doc.id}`)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TopicDashboard;
