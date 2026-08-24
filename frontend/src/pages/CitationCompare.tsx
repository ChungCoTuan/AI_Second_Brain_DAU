import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, ExternalLink } from 'lucide-react';
import StatusBadge from '../components/shared/StatusBadge';
import FaithfulnessScore from '../components/shared/FaithfulnessScore';

const CitationCompare: React.FC = () => {
  const { id } = useParams();

  return (
    <div className="compare-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
        <div>
          <Link to="/" className="btn" style={{ marginBottom: '1rem', color: 'var(--dau-gray)', paddingLeft: 0 }}>
            <ArrowLeft size={16} /> Quay lại Trang chủ
          </Link>
          <h2 className="page-title" style={{ margin: 0, marginBottom: '0.5rem' }}>Đối Chiếu Trích Dẫn</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontWeight: 600 }}>Thông tư 08/2021/TT-BGDĐT</span>
            <StatusBadge status="success" label="Còn hiệu lực" />
          </div>
        </div>
        <Link to={`/report/${id}`} className="btn btn-outline" style={{ borderColor: 'var(--color-accent)', color: 'var(--color-accent)' }}>
          Mở Khung báo cáo
        </Link>
      </div>

      <div className="compare-list">
        {/* Hợp lệ */}
        <div className="compare-item">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ color: 'var(--dau-gray)', fontSize: '0.875rem', fontWeight: 600 }}>CÂU TÓM TẮT</div>
            <FaithfulnessScore score={95} />
          </div>
          <p style={{ fontWeight: 500, marginBottom: '1rem' }}>Sinh viên được bảo lưu kết quả học tập tối đa không quá thời gian quy định cho khóa học.</p>
          <div style={{ padding: '1rem', backgroundColor: 'var(--dau-light-gray)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--dau-gray)', fontWeight: 600 }}>NGUỒN GỐC (ĐIỀU 15, KHOẢN 1)</div>
              <button 
                className="btn btn-outline" 
                style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                onClick={() => alert('Mở trình xem PDF tự động cuộn đến Trang 12')}
              >
                <ExternalLink size={12} /> Xem nguyên văn trong file gốc (Trang 12)
              </button>
            </div>
            <p style={{ fontSize: '0.875rem' }}>"Sinh viên được xin nghỉ học tạm thời và bảo lưu kết quả học tập... Thời gian nghỉ học tạm thời không được vượt quá thời gian tối đa để hoàn thành chương trình..."</p>
          </div>
        </div>

        {/* Cảnh báo nhẹ */}
        <div className="compare-item">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ color: 'var(--dau-gray)', fontSize: '0.875rem', fontWeight: 600 }}>CÂU TÓM TẮT</div>
            <FaithfulnessScore score={75} />
          </div>
          <p style={{ fontWeight: 500, marginBottom: '1rem' }}>Điểm tổng kết môn học được làm tròn đến một chữ số thập phân.</p>
          <div style={{ padding: '1rem', backgroundColor: 'var(--dau-light-gray)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--dau-gray)', marginBottom: '0.5rem', fontWeight: 600 }}>NGUỒN GỐC (ĐIỀU 9, KHOẢN 2)</div>
            <p style={{ fontSize: '0.875rem' }}>"Điểm học phần được tính theo thang điểm 10, làm tròn đến một chữ số thập phân..." (Lưu ý: Thiếu chi tiết về trọng số)</p>
          </div>
        </div>

        {/* Bị loại bỏ */}
        <div className="compare-item rejected">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-danger)' }}>
              <AlertTriangle size={18} />
              <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>CÂU ĐÃ BỊ LOẠI BỎ DO ĐỘ TIN CẬY THẤP</span>
            </div>
            <FaithfulnessScore score={20} />
          </div>
          <p className="rejected-text" style={{ fontWeight: 500, marginBottom: '1rem' }}>Sinh viên không được thi lại nếu rớt môn chuyên ngành.</p>
          <div style={{ padding: '1rem', backgroundColor: 'white', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(203, 9, 20, 0.2)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--dau-gray)', marginBottom: '0.5rem', fontWeight: 600 }}>NGUỒN GỐC TÌM THẤY (ĐIỀU 10)</div>
            <p style={{ fontSize: '0.875rem' }}>"Sinh viên có điểm học phần không đạt được đăng ký học lại..." (AI sinh câu mâu thuẫn hoàn toàn với văn bản gốc).</p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default CitationCompare;
