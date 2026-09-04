import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, ArrowLeft, Calendar, Building2, FileSignature } from 'lucide-react';
import { CitationBadge } from '../components/shared/Badge';

const ReportTemplate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* Header section */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button 
          onClick={() => navigate(-1)} 
          className="icon-btn hover-lift" 
          style={{ padding: '0.5rem', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '50%' }}
        >
          <ArrowLeft size={20} />
        </button>
        <div style={{ flex: 1 }}>
          <h1 className="title-h1" style={{ margin: 0, marginBottom: '0.5rem' }}>Báo cáo định kỳ công tác đào tạo tín chỉ</h1>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', color: 'var(--text-secondary)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Calendar size={16} /> Hạn nộp: 30/08/2026
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Building2 size={16} /> Đơn vị: Khoa CNTT
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-primary)', fontWeight: 500 }}>
              <FileSignature size={16} /> Mẫu: Báo cáo định kỳ
            </span>
          </div>
        </div>
        <button className="hover-lift" style={{ 
          display: 'flex', alignItems: 'center', gap: '0.5rem', 
          backgroundColor: 'var(--color-primary)', color: 'white', 
          padding: '0.75rem 1.5rem', borderRadius: 'var(--radius-md)', fontWeight: 600
        }}>
          <Download size={20} />
          Tải file Word (.docx)
        </button>
      </div>

      {/* Preview section */}
      <div className="card" style={{ padding: '3rem', backgroundColor: 'white', color: 'black' }}>
        <h2 style={{ textAlign: 'center', textTransform: 'uppercase', marginBottom: '2rem', fontSize: '1.25rem' }}>
          BÁO CÁO KẾT QUẢ ĐÀO TẠO
        </h2>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '0.75rem' }}>I. Căn cứ pháp lý</h3>
          <ul style={{ paddingLeft: '1.5rem', lineHeight: '1.8' }}>
            <li>
              Căn cứ theo <CitationBadge id="1" source="Quy chế 43/2007/QĐ-BGDĐT" /> ban hành quy chế đào tạo tín chỉ;
            </li>
            <li>
              Thực hiện theo <CitationBadge id="2" source="Công văn 123/ĐHKT-ĐT" /> về việc rà soát học vụ;
            </li>
          </ul>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '0.75rem' }}>II. Kết quả thực hiện theo từng chỉ tiêu</h3>
          <div style={{ 
            padding: '2rem', border: '2px dashed #9ca3af', borderRadius: '8px', 
            backgroundColor: '#f9fafb', color: '#6b7280', fontStyle: 'italic',
            textAlign: 'center'
          }}>
            (Để trống) Cán bộ điền số liệu kết quả triển khai học vụ tại đây...
          </div>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '0.75rem' }}>III. Khó khăn vướng mắc</h3>
          <div style={{ 
            padding: '2rem', border: '2px dashed #9ca3af', borderRadius: '8px', 
            backgroundColor: '#f9fafb', color: '#6b7280', fontStyle: 'italic',
            textAlign: 'center'
          }}>
            (Để trống) Nêu các vướng mắc trong quá trình áp dụng quy chế...
          </div>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '0.75rem' }}>IV. Kiến nghị</h3>
          <div style={{ 
            padding: '2rem', border: '2px dashed #9ca3af', borderRadius: '8px', 
            backgroundColor: '#f9fafb', color: '#6b7280', fontStyle: 'italic',
            textAlign: 'center'
          }}>
            (Để trống) Đề xuất hướng giải quyết...
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '3rem' }}>
          <div></div>
          <div style={{ textAlign: 'center' }}>
            <p style={{ margin: 0, fontStyle: 'italic' }}>Đà Nẵng, ngày ... tháng ... năm ...</p>
            <p style={{ margin: 0, fontWeight: 'bold', marginTop: '0.5rem' }}>NGƯỜI LẬP BÁO CÁO</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportTemplate;
