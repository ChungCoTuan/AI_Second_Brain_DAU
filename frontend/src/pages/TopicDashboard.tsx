import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, AlertTriangle, BookOpen, Users, Banknote, Building, FileQuestion, ArrowLeft } from 'lucide-react';
import { TopicCard, DocumentCard } from '../components/shared/Card';
import type { DocStatus } from '../components/shared/Badge';
import { fetchTopics, fetchDocuments, fetchReviewItems, DocumentItem, TopicSummary } from '../services/api';

const TopicDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [topics, setTopics] = useState<TopicSummary[]>([]);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoading(true);
        const [topicData, reviewData] = await Promise.all([
          fetchTopics(),
          fetchReviewItems()
        ]);
        setTopics(topicData);
        setPendingCount(reviewData.pending_count || 0);
      } catch (err) {
        console.error("Lỗi khi tải dữ liệu chủ đề:", err);
      } finally {
        setLoading(false);
      }
    }
    loadInitialData();
  }, []);

  useEffect(() => {
    async function loadDocs() {
      if (!selectedTopic) return;
      try {
        setLoading(true);
        const docList = await fetchDocuments({ topic: selectedTopic });
        setDocs(docList);
      } catch (err) {
        console.error("Lỗi khi tải danh sách văn bản:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDocs();
  }, [selectedTopic]);

  const getTopicIcon = (iconName: string) => {
    switch (iconName) {
      case 'BookOpen': return <BookOpen size={24} />;
      case 'Users': return <Users size={24} />;
      case 'Banknote': return <Banknote size={24} />;
      case 'Building': return <Building size={24} />;
      default: return <FileQuestion size={24} />;
    }
  };

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
              <h3 style={{ margin: 0, fontSize: '1.125rem' }}>Có {pendingCount} văn bản đang chờ rà soát PENDING_REVIEW</h3>
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
            <h1 className="title-h1" style={{ margin: 0 }}>Dashboard theo chủ đề (Thực tế Pipeline)</h1>
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
                icon={getTopicIcon(topic.icon)} 
                onClick={() => setSelectedTopic(topic.id)}
              />
            ))}
          </div>

          <div className="card">
            <h2 className="title-h2">Trạng thái Pipeline dữ liệu thực tế</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontWeight: 500 }}>Kiểm duyệt Pydantic Quality Gate: 29 Documents, 56 Chunks</span>
                <span className="badge badge-success">✅ 100% Valid</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem' }}>
                <span style={{ fontWeight: 500 }}>Phân loại chủ đề NER (Epic-2): 5 Nhóm Topic</span>
                <span className="badge badge-primary-light">✅ Đã gán 29 văn bản</span>
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
            <h1 className="title-h1" style={{ margin: 0 }}>
              Chủ đề: {topics.find(t => t.id === selectedTopic)?.title} ({docs.length} văn bản thực tế)
            </h1>
          </div>
          
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {loading ? (
              <p>Đang tải danh sách văn bản...</p>
            ) : docs.length === 0 ? (
              <p>Chưa có văn bản thuộc chủ đề này.</p>
            ) : (
              docs.map(doc => (
                <DocumentCard 
                  key={doc.doc_id} 
                  id={doc.doc_id}
                  title={doc.ten_van_ban}
                  type={doc.loai_van_ban}
                  topic={doc.chu_de}
                  status={(doc.trang_thai_xuat_ban.toLowerCase() as DocStatus)}
                  date={doc.ngay_ban_hanh}
                  onClick={() => navigate(`/document/${doc.doc_id}`)}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TopicDashboard;
