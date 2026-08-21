import React, { useState } from 'react';
import { UploadCloud, AlertCircle, FileText, CheckCircle2, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

const mockQueue = [
  { id: '4', title: 'Quyết định 88/QĐ-ĐHKT Quy định thi chuẩn đầu ra Tin học', status: 'processing', step: 'Đang kiểm tra Faithfulness' },
  { id: '5', title: 'Thông tư 17/2021/TT-BGDĐT Chuẩn chương trình đào tạo', status: 'warning', step: 'Cần rà soát 2 câu không đạt', docId: '1' },
  { id: '6', title: 'Công văn 789/BGDĐT Hướng dẫn chuyển đổi số', status: 'completed', step: 'Hoàn tất' },
];

const ContentAdmin: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);

  return (
    <div className="content-admin">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 className="page-title" style={{ margin: 0 }}>Quản Trị Nội Dung</h2>
        <button className="btn btn-primary">
          <UploadCloud size={18} /> Nạp văn bản mới
        </button>
      </div>

      <div 
        className="dropzone" 
        style={{ borderColor: isDragging ? 'var(--dau-red)' : 'var(--dau-border)' }}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { e.preventDefault(); setIsDragging(false); alert('Giả lập tải file lên thành công'); }}
      >
        <UploadCloud size={48} color="var(--dau-gray)" style={{ marginBottom: '1rem' }} />
        <h3>Kéo thả file PDF hoặc ảnh scan vào đây</h3>
        <p style={{ color: 'var(--dau-gray)', marginTop: '0.5rem' }}>Hỗ trợ PDF, PNG, JPG (Tối đa 20MB)</p>
      </div>

      <div className="alert-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertCircle size={20} color="var(--color-accent)" />
          <span><strong>Có 1 văn bản cần rà soát!</strong> Hệ thống phát hiện 2 câu tóm tắt có điểm Faithfulness dưới ngưỡng quy định.</span>
        </div>
        <Link to="/compare/1" className="btn btn-outline" style={{ borderColor: 'var(--color-accent)', color: 'var(--color-accent)' }}>
          Rà soát ngay
        </Link>
      </div>

      <h3 style={{ marginBottom: '1rem' }}>Hàng Đợi Xử Lý</h3>
      <div className="queue-list">
        {mockQueue.map(item => (
          <div key={item.id} className="queue-item">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <FileText size={20} color="var(--dau-gray)" />
              <span style={{ fontWeight: 500 }}>{item.title}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--dau-gray)', fontSize: '0.875rem' }}>
              {item.status === 'processing' && <Clock size={16} color="var(--color-warning)" />}
              {item.status === 'warning' && <AlertCircle size={16} color="var(--color-accent)" />}
              {item.status === 'completed' && <CheckCircle2 size={16} color="var(--color-success)" />}
              <span>{item.step}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContentAdmin;
