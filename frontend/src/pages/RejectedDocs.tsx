import React, { useState, useEffect } from 'react';
import { Trash2, RefreshCw, XCircle } from 'lucide-react';

interface RejectedDocument {
  id: number;
  soHieu: string;
  loai: string;
  ngayKy: string;
  chuDe: string[];
  status: string;
}

const RejectedDocs: React.FC = () => {
  const [documents, setDocuments] = useState<RejectedDocument[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchRejectedDocs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/rejected');
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error("Lỗi khi tải văn bản bị loại:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRejectedDocs();
  }, []);

  const handleReprocess = async (id: number) => {
    if (!window.confirm('Bạn có chắc muốn đưa văn bản này về lại tab Tải tài liệu để bóc tách lại không?')) return;
    
    setProcessingId(id);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/documents/${id}/reprocess`, {
        method: 'POST'
      });
      const result = await response.json();
      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.id !== id));
        setMessage({ text: result.message, type: 'success' });
      } else {
        setMessage({ text: result.detail || 'Lỗi khi bóc tách lại', type: 'error' });
      }
    } catch (error) {
      setMessage({ text: 'Không thể kết nối đến máy chủ', type: 'error' });
    } finally {
      setProcessingId(null);
    }
  };

  const handleHardDelete = async (id: number) => {
    if (!window.confirm('CẢNH BÁO: Hành động này sẽ xóa vĩnh viễn văn bản khỏi cơ sở dữ liệu và ổ cứng. Bạn có chắc chắn không?')) return;
    
    setProcessingId(id);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/documents/${id}/hard_delete`, {
        method: 'DELETE'
      });
      const result = await response.json();
      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.id !== id));
        setMessage({ text: result.message, type: 'success' });
      } else {
        setMessage({ text: result.detail || 'Lỗi khi xóa', type: 'error' });
      }
    } catch (error) {
      setMessage({ text: 'Không thể kết nối đến máy chủ', type: 'error' });
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <section style={{ padding: '20px' }}>
        <div className="wrap">
          <h2>Thùng rác / Văn bản bị loại</h2>
          <p className="sub">Đang tải...</p>
        </div>
      </section>
    );
  }

  return (
    <section style={{ background: 'var(--soft)', minHeight: '100vh', paddingBottom: '40px' }}>
      <div className="wrap" style={{ maxWidth: '1200px', margin: '0 auto', paddingTop: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--ink)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Trash2 size={24} color="var(--red)" />
            Văn bản bị loại bỏ
          </h2>
          <p className="sub" style={{ color: 'var(--muted)', marginTop: '4px' }}>
            Nơi quản lý các văn bản đã bị từ chối toàn bộ nội dung. Bạn có thể xóa vĩnh viễn hoặc đưa chúng trở lại hàng chờ để bóc tách lại.
          </p>
        </div>

        {message && (
          <div style={{
            padding: '12px 16px',
            marginBottom: '20px',
            borderRadius: '8px',
            background: message.type === 'success' ? 'var(--green-50)' : 'var(--red-50)',
            color: message.type === 'success' ? 'var(--green)' : 'var(--red)',
            fontWeight: 600
          }}>
            {message.text}
          </div>
        )}

        {documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0', background: 'var(--card-bg)', borderRadius: '12px' }}>
            <XCircle size={48} color="var(--muted)" style={{ opacity: 0.5, marginBottom: '16px' }} />
            <p style={{ color: 'var(--muted)', fontWeight: 600 }}>Thùng rác đang trống.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {documents.map((doc, idx) => (
              <div key={doc.id} style={{
                display: 'grid',
                gridTemplateColumns: '40px 2fr 1fr 1fr auto',
                gap: '16px',
                padding: '16px',
                background: 'var(--card-bg)',
                borderRadius: '8px',
                alignItems: 'center',
                border: '1px solid var(--border)',
              }}>
                <span style={{ fontWeight: 600, color: 'var(--muted)' }}>{idx + 1}</span>
                <span style={{ fontWeight: 700, color: 'var(--ink)' }}>{doc.soHieu}</span>
                <span style={{ color: 'var(--muted)' }}>{doc.loai}</span>
                <span style={{ color: 'var(--muted)' }}>{doc.ngayKy}</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={() => handleReprocess(doc.id)}
                    disabled={processingId === doc.id}
                    style={{
                      background: 'var(--blue-50)', color: 'var(--blue)', border: 'none',
                      padding: '8px 12px', borderRadius: '6px', fontWeight: 600,
                      display: 'flex', alignItems: 'center', gap: '6px', cursor: processingId === doc.id ? 'wait' : 'pointer'
                    }}
                  >
                    <RefreshCw size={16} /> Bóc tách lại
                  </button>
                  <button
                    onClick={() => handleHardDelete(doc.id)}
                    disabled={processingId === doc.id}
                    style={{
                      background: 'var(--red-50)', color: 'var(--red)', border: 'none',
                      padding: '8px 12px', borderRadius: '6px', fontWeight: 600,
                      display: 'flex', alignItems: 'center', gap: '6px', cursor: processingId === doc.id ? 'wait' : 'pointer'
                    }}
                  >
                    <Trash2 size={16} /> Xóa vĩnh viễn
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default RejectedDocs;
