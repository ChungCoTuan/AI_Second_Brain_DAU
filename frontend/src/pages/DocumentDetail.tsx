import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, FileText, CheckCircle } from 'lucide-react';
import { StatusBadge, NLILabelBadge, ManualOverrideBadge } from '../components/shared/Badge';
import { RelationList } from '../components/shared/List';
import { useAuth } from '../context/AuthContext';

const DocumentDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { role } = useAuth();

  // Mock data
  const isPending = id === '2'; // Just for demo
  
  const summarySentences = [
    { text: 'Thời gian tối đa để hoàn thành khoá học đối với hệ đại học chính quy là thời gian thiết kế cộng thêm 4 học kỳ.', source: 'Điều 6', label: 'entailment' as const },
    { text: 'Sinh viên được phép nghỉ học tạm thời tối đa 2 học kỳ liên tiếp.', source: 'Điều 8', label: 'entailment' as const, manualOverride: true },
    { text: 'Sinh viên năm cuối không được phép đăng ký học vượt quá 20 tín chỉ.', source: 'Điều 12', label: 'contradiction' as const },
    { text: 'Học phí được tính dựa trên số lượng tín chỉ đăng ký.', source: 'Điều 15', label: 'neutral' as const },
  ];

  const relationItems = [
    { title: 'Quy chế 43/2007/QĐ-BGDĐT', meta: 'Văn bản căn cứ', type: 'direct' as const },
    { title: 'Quyết định 12/QĐ-ĐHKT', meta: 'Văn bản thay thế', type: 'direct' as const },
    { title: 'Hướng dẫn thực hiện quy chế đào tạo', meta: 'Văn bản liên quan', type: 'semantic' as const, level: 'direct_apply' as const, similarity: 92 },
    { title: 'Quy định chuẩn đầu ra Tiếng Anh', meta: 'Văn bản liên quan', type: 'semantic' as const, level: 'general_apply' as const, similarity: 78 },
  ];

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button onClick={() => navigate(-1)} className="icon-btn hover-lift" style={{ padding: '0.5rem', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '50%' }}>
          <ArrowLeft size={20} />
        </button>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <h1 className="title-h1" style={{ margin: 0 }}>Quy định quản lý điểm sinh viên hệ chính quy</h1>
            <StatusBadge status={isPending ? 'pending_review' : 'published'} />
          </div>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Số hiệu: 154/QĐ-ĐHKT • Ngày ban hành: 20/08/2026 • Chủ đề: Đào tạo</p>
        </div>
        <button onClick={() => navigate(`/report/${id}`)} className="hover-lift" style={{ 
          display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', padding: '0.75rem 1.25rem', borderRadius: 'var(--radius-md)', fontWeight: 600, border: '1px solid rgba(37, 99, 235, 0.2)'
        }}>
          <FileText size={18} /> Khung báo cáo
        </button>
      </div>

      {isPending && role === 'admin' && (
        <div className="card" style={{ backgroundColor: 'var(--color-danger-light)', borderColor: 'var(--color-danger)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--color-danger-text)' }}>
            <AlertTriangle size={20} />
            <span style={{ fontWeight: 600 }}>Văn bản chưa hoàn thiện — còn 2 câu chờ rà soát</span>
          </div>
          <button onClick={() => navigate('/review')} style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--color-danger)', color: 'white', borderRadius: 'var(--radius-md)', fontWeight: 600 }}>
            Xem trong Rà soát
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', flex: 1 }}>
        
        {/* Đối chiếu trích dẫn (Màn hình 4) */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h2 className="title-h2" style={{ margin: 0 }}>Đối chiếu trích dẫn (Tóm tắt AI)</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {summarySentences.map((sentence, idx) => (
              <div key={idx} style={{ 
                padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)',
                backgroundColor: sentence.label === 'contradiction' || sentence.label === 'neutral' ? 'var(--bg-main)' : 'var(--bg-surface)',
                opacity: (sentence.label === 'contradiction' && !isPending) ? 0.5 : 1
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
                  <p style={{ margin: 0, fontSize: '1rem', lineHeight: 1.5, 
                    textDecoration: (sentence.label === 'contradiction' && !isPending) ? 'line-through' : 'none' 
                  }}>
                    {sentence.text}
                  </p>
                  <NLILabelBadge label={sentence.label} />
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Nguồn: {sentence.source}</span>
                  {sentence.manualOverride && <ManualOverrideBadge />}
                  {isPending && (sentence.label === 'contradiction' || sentence.label === 'neutral') && role === 'admin' && (
                    <button onClick={() => navigate('/review')} style={{ marginLeft: 'auto', fontSize: '0.875rem', color: 'var(--color-primary)', fontWeight: 500 }}>
                      Xử lý ngay →
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cây văn bản (Màn hình 6) */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h2 className="title-h2" style={{ margin: 0 }}>Cây văn bản</h2>
          
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary-hover)', borderRadius: 'var(--radius-md)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle size={18} />
            Áp dụng trực tiếp — có quy chế nội bộ
          </div>

          <div>
            <h3 className="title-h3" style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Quan hệ trực tiếp</h3>
            <RelationList items={relationItems.filter(item => item.type === 'direct')} />
          </div>

          <div>
            <h3 className="title-h3" style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem', marginTop: '1rem' }}>Quan hệ ngữ nghĩa (AI Gợi ý)</h3>
            <RelationList items={relationItems.filter(item => item.type === 'semantic')} />
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default DocumentDetail;
