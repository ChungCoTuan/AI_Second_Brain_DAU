import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Download, ArrowLeft } from 'lucide-react';
import CitationBadge from '../components/shared/CitationBadge';
import StatusBadge from '../components/shared/StatusBadge';

const ReportTemplate: React.FC = () => {
  const { id } = useParams();

  return (
    <div className="report-template">
      <Link to={`/compare/${id}`} className="btn" style={{ marginBottom: '1rem', color: 'var(--dau-gray)' }}>
        <ArrowLeft size={16} /> Quay lại văn bản
      </Link>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 className="page-title" style={{ margin: 0, marginBottom: '0.5rem' }}>Khung Báo Cáo Gợi Ý</h2>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <StatusBadge status="warning" label="Hạn nộp: 30/09/2024" />
            <StatusBadge status="warning" label="Đơn vị: Phòng Đào Tạo" />
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => alert('Đang tải file Word...')}>
          <Download size={18} /> Tải file Word (.docx)
        </button>
      </div>

      <div className="report-preview">
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h3>BÁO CÁO</h3>
          <h4>V/v: Tình hình đào tạo học kỳ I năm học 2023-2024</h4>
        </div>

        <div className="report-section">
          <h3>1. Căn cứ pháp lý</h3>
          <ul>
            <li style={{ marginBottom: '0.5rem' }}>
              Căn cứ <CitationBadge documentId="1" sourceText="Thông tư 08/2021/TT-BGDĐT" pageNumber={5} /> Quy chế đào tạo trình độ đại học.
            </li>
            <li>
              Căn cứ Kế hoạch năm học 2023-2024 của Trường Đại học Kiến trúc Đà Nẵng.
            </li>
          </ul>
        </div>

        <div className="report-section">
          <h3>2. Nội dung báo cáo</h3>
          <p style={{ color: 'var(--dau-gray)', fontStyle: 'italic' }}>* Các đề mục dưới đây được trích xuất từ yêu cầu báo cáo của văn bản</p>
          <ul>
            <li>Tình hình tổ chức giảng dạy</li>
            <li>Công tác khảo thí và đảm bảo chất lượng</li>
            <li>Khó khăn, vướng mắc</li>
          </ul>
        </div>

        <div className="report-section">
          <h3>3. Số liệu thống kê</h3>
          <div className="report-dashed-box">
            (Để trống - Người dùng tự điền số liệu thực tế)
          </div>
        </div>

        <div className="report-section">
          <h3>4. Kết luận và Kiến nghị</h3>
          <div className="report-dashed-box">
            (Để trống - Người dùng tự viết kết luận)
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportTemplate;
