import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchTopicsSummary, type TopicSummaryItem } from '../services/api';

interface TopicDashboardProps {
  onSelectTopic: (topicCode: string) => void;
  refreshKey?: number;
}

export const TopicDashboard: React.FC<TopicDashboardProps> = ({ onSelectTopic, refreshKey = 0 }) => {
  const navigate = useNavigate();
  const [topics, setTopics] = useState<TopicSummaryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchTopicsSummary().then((data) => {
      if (isMounted) {
        setTopics(data);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  const totalDocs = topics.reduce((acc, t) => acc + t.total_documents, 0);
  const totalPublished = topics.reduce((acc, t) => acc + t.published_documents, 0);
  const totalPending = topics.reduce((acc, t) => acc + t.pending_documents, 0);
  const overallRate = totalDocs > 0 ? Math.round((totalPublished / totalDocs) * 100) : 0;

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
        📊 Đang tải dữ liệu Dashboard Chủ Đề từ PostgreSQL Database...
      </div>
    );
  }

  return (
    <div style={{ padding: '24px 0' }}>
      {/* SUMMARY BANNER */}
      <div
        style={{
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          borderRadius: '16px',
          padding: '24px 28px',
          color: '#ffffff',
          marginBottom: '28px',
          boxShadow: '0 10px 25px -5px rgba(15, 23, 42, 0.3)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '24px' }}>📊</span>
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 800 }}>
              Dashboard Quản Lý & Duyệt Văn Bản Theo Chủ Đề (UC-08)
            </h2>
          </div>
          <p style={{ margin: '6px 0 0 0', fontSize: '13px', color: '#94a3b8' }}>
            Phân nhóm tự động thông tư, quyết định, quy chế theo 6 lĩnh vực quản lý tại Trường ĐH Kiến trúc Đà Nẵng
          </p>
        </div>

        {/* OVERALL PROGRESS BADGE */}
        <div style={{ background: 'rgba(255, 255, 255, 0.08)', padding: '12px 20px', borderRadius: '12px', minWidth: '220px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#cbd5e1', marginBottom: '6px' }}>
            <span>Tiến độ hoàn thiện:</span>
            <b>{overallRate}% Published</b>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.2)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${overallRate}%`, background: '#22c55e', height: '100%', transition: 'width 0.5s ease' }} />
          </div>
          <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '6px', textAlign: 'right' }}>
            {totalPublished} / {totalDocs} văn bản đã duyệt ({totalPending} cần rà soát)
          </div>
        </div>
      </div>

      {/* BANNER CẢNH BÁO "CẦN RÀ SOÁT" NẾU CÓ VĂN BẢN PENDING */}
      {totalPending > 0 && (
        <div style={{ 
          background: '#fffbeb', 
          border: '1px solid #fef3c7', 
          borderLeft: '4px solid #f59e0b',
          borderRadius: '8px', 
          padding: '16px 20px', 
          marginBottom: '28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
        }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '15px', color: '#b45309', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>⚠️</span> Có {totalPending} văn bản cần rà soát thủ công
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#92400e' }}>
              Một số câu văn bản được AI tóm tắt có nhãn "contradiction" hoặc điểm độ tin cậy thấp. Vui lòng rà soát trước khi xuất bản.
            </p>
          </div>
          <button
            onClick={() => navigate('/review')}
            style={{
              background: '#f59e0b',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontWeight: 600,
              fontSize: '13px',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            Đi đến Hàng Đợi Duyệt →
          </button>
        </div>
      )}

      {/* TOPIC CARDS GRID */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '20px',
        }}
      >
        {topics.map((topic) => (
          <div
            key={topic.code}
            onClick={() => onSelectTopic(topic.code)}
            style={{
              background: '#ffffff',
              borderRadius: '14px',
              border: '1px solid #e2e8f0',
              padding: '20px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            <div>
              {/* CARD HEADER */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '28px' }}>{topic.icon}</span>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                      {topic.name}
                    </h3>
                    <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>
                      Mã: {topic.code}
                    </span>
                  </div>
                </div>
                <span
                  style={{
                    background: '#f1f5f9',
                    color: '#334155',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: 700,
                  }}
                >
                  {topic.total_documents} văn bản
                </span>
              </div>

              {/* PROGRESS BAR */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#64748b', marginBottom: '4px' }}>
                  <span>Tỷ lệ hoàn thành</span>
                  <b>{topic.completion_rate}%</b>
                </div>
                <div style={{ background: '#e2e8f0', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${topic.completion_rate}%`,
                      background: topic.completion_rate === 100 ? '#16a34a' : '#2563eb',
                      height: '100%',
                    }}
                  />
                </div>
              </div>

              {/* STATS BADGES */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '18px' }}>
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '8px 10px' }}>
                  <div style={{ fontSize: '10px', color: '#166534', fontWeight: 700 }}>🟢 ĐÃ XUẤT BẢN</div>
                  <div style={{ fontSize: '16px', fontWeight: 800, color: '#15803d', marginTop: '2px' }}>
                    {topic.published_documents}
                  </div>
                </div>

                <div style={{ background: topic.pending_documents > 0 ? '#fffbeb' : '#f8fafc', border: `1px solid ${topic.pending_documents > 0 ? '#fef3c7' : '#e2e8f0'}`, borderRadius: '8px', padding: '8px 10px' }}>
                  <div style={{ fontSize: '10px', color: topic.pending_documents > 0 ? '#b45309' : '#64748b', fontWeight: 700 }}>
                    {topic.pending_documents > 0 ? '🟠 CẦN RÀ SOÁT' : '⚪ HOÀN TẤT'}
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 800, color: topic.pending_documents > 0 ? '#b45309' : '#64748b', marginTop: '2px' }}>
                    {topic.pending_documents}
                  </div>
                </div>
              </div>
            </div>

            {/* ACTION BUTTON */}
            <button
              onClick={() => onSelectTopic(topic.code)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                background: 'linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%)',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: '13px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                boxShadow: '0 4px 6px -1px rgba(30, 64, 175, 0.2)',
              }}
            >
              🔍 Lọc & Duyệt Văn Bản Theo Chủ Đề
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
