import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, FileText, CheckCircle } from 'lucide-react';
import { StatusBadge, NLILabelBadge, ManualOverrideBadge } from '../components/shared/Badge';
import { RelationList } from '../components/shared/List';
import { useAuth } from '../context/AuthContext';
import { fetchDocumentDetail, DocumentItem, ChunkItem, RelationItem } from '../services/api';
import type { DocStatus } from '../components/shared/Badge';

const DocumentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { role } = useAuth();

  const [doc, setDoc] = useState<DocumentItem | null>(null);
  const [chunks, setChunks] = useState<ChunkItem[]>([]);
  const [relations, setRelations] = useState<RelationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDetail() {
      if (!id) return;
      try {
        setLoading(true);
        const data = await fetchDocumentDetail(id);
        setDoc(data.document);
        setChunks(data.chunks);
        setRelations(data.relations);
      } catch (err) {
        console.error("Lỗi khi tải thông tin văn bản:", err);
        setError("Không tìm thấy văn bản!");
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [id]);

  if (loading) {
    return <div className="dashboard-container"><p>Đang tải chi tiết văn bản thực tế...</p></div>;
  }

  if (error || !doc) {
    return (
      <div className="dashboard-container">
        <h2>{error || "Không tìm thấy văn bản"}</h2>
        <button onClick={() => navigate('/')}>Về trang chủ</button>
      </div>
    );
  }

  const isPending = doc.trang_thai_xuat_ban === 'PENDING_REVIEW';

  const mappedRelations = relations.map(r => ({
    title: r.document_id_b === doc.doc_id ? r.document_id_a : r.document_id_b,
    meta: `Loại quan hệ: ${r.loai_quan_he} ${r.mo_ta ? '• ' + r.mo_ta : ''}`,
    type: (r.loai_quan_he === 'LIEN_QUAN_NGU_NGHIA' ? 'semantic' : 'direct') as 'direct' | 'semantic',
    similarity: r.diem_tuong_dong ? Math.round(r.diem_tuong_dong * 100) : undefined,
    level: 'direct_apply' as const
  }));

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button onClick={() => navigate(-1)} className="icon-btn hover-lift" style={{ padding: '0.5rem', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '50%' }}>
          <ArrowLeft size={20} />
        </button>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <h1 className="title-h1" style={{ margin: 0 }}>{doc.ten_van_ban}</h1>
            <StatusBadge status={(doc.trang_thai_xuat_ban.toLowerCase() as DocStatus)} />
          </div>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            Số hiệu: {doc.so_hieu} • Cơ quan ban hành: {doc.co_quan_ban_hanh} • Ngày ban hành: {doc.ngay_ban_hanh} • Chủ đề: {doc.chu_de}
          </p>
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
            <span style={{ fontWeight: 600 }}>Văn bản ở trạng thái PENDING_REVIEW (Cần rà soát kiểm duyệt)</span>
          </div>
          <button onClick={() => navigate('/review')} style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--color-danger)', color: 'white', borderRadius: 'var(--radius-md)', fontWeight: 600 }}>
            Xem trong Rà soát
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', flex: 1 }}>
        
        {/* Danh sách Chunks Điều/Khoản */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h2 className="title-h2" style={{ margin: 0 }}>Các đoạn Chunks bóc tách ({chunks.length} đoạn)</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {chunks.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>Chưa có chunk chi tiết bóc tách cho văn bản này.</p>
            ) : (
              chunks.map((chunk) => (
                <div key={chunk.chunk_id} style={{ 
                  padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-surface)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', marginBottom: '0.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--color-primary)' }}>{chunk.title}</h3>
                    <span className="badge badge-primary-light">Trang {chunk.so_trang}</span>
                  </div>
                  <p style={{ margin: '0.5rem 0', fontSize: '0.95rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                    {chunk.content}
                  </p>
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                    <span>Tokens: {chunk.token_count}</span>
                    <span>Chủ đề: {chunk.chu_de}</span>
                    <span>Mức độ: {chunk.muc_do_lien_quan_dau}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Quan hệ văn bản (DocumentRelation) */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h2 className="title-h2" style={{ margin: 0 }}>Mối quan hệ liên văn bản ({relations.length})</h2>
          
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary-hover)', borderRadius: 'var(--radius-md)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle size={18} />
            Mức độ liên quan DAU: {doc.muc_do_lien_quan_dau}
          </div>

          <div>
            <h3 className="title-h3" style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Quan hệ trực tiếp ({relations.length})</h3>
            <RelationList items={mappedRelations} />
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default DocumentDetail;
