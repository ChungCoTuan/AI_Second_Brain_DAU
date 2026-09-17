import React, { useEffect, useState } from 'react';
import { fetchReportOutline, type ReportOutlineResponse, getReportDocxDownloadUrl } from '../services/api';

interface ReportSuggestionModalProps {
  docId: string;
  onClose: () => void;
}

export const ReportSuggestionModal: React.FC<ReportSuggestionModalProps> = ({ docId, onClose }) => {
  const [outline, setOutline] = useState<ReportOutlineResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    fetchReportOutline(docId).then((data) => {
      if (isMounted) {
        setOutline(data);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [docId]);

  const handleDownloadDocx = () => {
    const downloadUrl = getReportDocxDownloadUrl(docId);
    window.location.href = downloadUrl;
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(15, 23, 42, 0.65)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
        backdropFilter: 'blur(4px)',
      }}
    >
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          width: '750px',
          maxWidth: '92%',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          overflow: 'hidden',
        }}
      >
        {/* MODAL HEADER */}
        <div
          style={{
            padding: '20px 24px',
            background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
            color: '#ffffff',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>
              📄 Khung Báo Cáo Gợi Ý (UC-05)
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '12px', opacity: 0.85 }}>
              Tự động chọn template theo loại văn bản & chủ đề • Không bịa số liệu thực tế
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              color: '#ffffff',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 700,
            }}
          >
            ✕
          </button>
        </div>

        {/* MODAL BODY - ADMINISTRATIVE PAPER PREVIEW */}
        <div style={{ padding: '24px', overflowY: 'auto', flex: 1, background: '#f1f5f9' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: 'var(--muted)', fontSize: '14px' }}>Đang tạo khung báo cáo từ PostgreSQL DB...</p>
            </div>
          ) : outline ? (
            <div
              style={{
                background: '#ffffff',
                padding: '32px 36px',
                borderRadius: '8px',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.08)',
                border: '1px solid #cbd5e1',
                fontFamily: '"Times New Roman", Times, serif',
                color: '#0f172a',
                lineHeight: 1.5,
              }}
            >
              {/* 1. ADMINISTRATIVE HEADER TABLE */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '20px',
                  marginBottom: '24px',
                  borderBottom: '1px solid #e2e8f0',
                  paddingBottom: '16px',
                }}
              >
                {/* LEFT: ORGAN & DEPT */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', textTransform: 'uppercase' }}>
                    {outline.co_quan_ban_hanh_tren || 'TRƯỜNG ĐẠI HỌC KIẾN TRÚC ĐÀ NẴNG'}
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '2px', color: '#334155' }}>
                    {outline.don_vi_bao_cao || 'ĐƠN VỊ / KHOA / PHÒNG: [........................................]'}
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '4px', fontStyle: 'italic', color: '#64748b' }}>
                    {outline.so_ky_hieu || 'Số: ...../BC-DAU'}
                  </div>
                </div>

                {/* RIGHT: NATIONAL MOTTO & DATE */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', textTransform: 'uppercase' }}>
                    {outline.quoc_hieu || 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM'}
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '13px', marginTop: '2px' }}>
                    {outline.tieu_ngu || 'Độc lập - Tự do - Hạnh phúc'}
                  </div>
                  <div style={{ fontSize: '12px', fontWeight: 700, marginTop: '2px', color: '#64748b' }}>
                    -----------------------
                  </div>
                  <div style={{ fontSize: '12px', fontStyle: 'italic', marginTop: '4px', color: '#475569' }}>
                    {outline.dia_danh_ngay_thang || 'Đà Nẵng, ngày ... tháng ... năm 20...'}
                  </div>
                </div>
              </div>

              {/* 2. DOCUMENT TITLE & SUBJECT */}
              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <h2
                  style={{
                    margin: 0,
                    fontSize: '20px',
                    fontWeight: 700,
                    color: '#1e3a8a',
                    letterSpacing: '0.5px',
                    textTransform: 'uppercase',
                  }}
                >
                  {outline.ten_don_bao_cao || 'BÁO CÁO THỰC HIỆN'}
                </h2>
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: 700,
                    fontStyle: 'italic',
                    color: '#334155',
                    marginTop: '6px',
                  }}
                >
                  {outline.trich_yeu || `V/v Triển khai & Thực hiện ${outline.ten_van_ban}`}
                </div>
                <div
                  style={{
                    fontSize: '13px',
                    fontStyle: 'italic',
                    color: '#64748b',
                    marginTop: '8px',
                  }}
                >
                  {outline.kinh_gui || 'Kính gửi: Ban Giám hiệu Trường Đại học Kiến trúc Đà Nẵng / Trưởng đơn vị'}
                </div>
              </div>

              {/* TEMPLATE BADGE */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
                <span
                  style={{
                    background: '#dbeafe',
                    color: '#1e40af',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '11px',
                    fontWeight: 700,
                    fontFamily: 'sans-serif',
                  }}
                >
                  📌 {outline.template_used}
                </span>
              </div>

              {/* 3. OUTLINE SECTIONS PREVIEW */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {outline.sections.map((sec, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: sec.is_blank ? '#fffbeb' : '#fafafa',
                      border: sec.is_blank ? '2px dashed #f59e0b' : '1px solid #e2e8f0',
                      borderRadius: '8px',
                      padding: '16px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span
                        style={{
                          fontWeight: 700,
                          fontSize: '14px',
                          color: sec.is_blank ? '#b45309' : '#0f172a',
                        }}
                      >
                        {sec.heading}
                      </span>
                      {sec.is_blank && (
                        <span
                          style={{
                            background: '#fef3c7',
                            color: '#b45309',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '10px',
                            fontWeight: 700,
                            fontFamily: 'sans-serif',
                          }}
                        >
                          ⚠️ ĐỂ TRỐNG (KHÔNG BỊA SỐ LIỆU)
                        </span>
                      )}
                    </div>
                    {sec.type === 'legal_base' ? (
                      <div
                        style={{
                          background: '#ffffff',
                          borderLeft: '4px solid #3b82f6',
                          padding: '10px 14px',
                          fontSize: '13px',
                          color: '#334155',
                          lineHeight: 1.6,
                          whiteSpace: 'pre-wrap',
                          borderRadius: '4px',
                          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                        }}
                      >
                        {sec.content}
                      </div>
                    ) : (
                      <div
                        style={{
                          fontSize: '13px',
                          color: sec.is_blank ? '#b45309' : '#334155',
                          lineHeight: 1.6,
                          whiteSpace: 'pre-wrap',
                          fontStyle: sec.is_blank ? 'italic' : 'normal',
                        }}
                      >
                        {sec.content}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* 4. FOOTER SIGNATURE BLOCK */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '20px',
                  marginTop: '32px',
                  paddingTop: '20px',
                  borderTop: '1px solid #cbd5e1',
                }}
              >
                {/* LEFT: NƠI NHẬN */}
                <div>
                  <div style={{ fontWeight: 700, fontSize: '12px', fontStyle: 'italic', marginBottom: '4px' }}>
                    Nơi nhận:
                  </div>
                  {(outline.noi_nhan || ['- Như trên;', '- Lưu: VT, Đơn vị.']).map((item, i) => (
                    <div key={i} style={{ fontSize: '11px', fontStyle: 'italic', color: '#475569' }}>
                      {item}
                    </div>
                  ))}
                </div>

                {/* RIGHT: CHỮ KÝ */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', textTransform: 'uppercase' }}>
                    {outline.nguoi_ky_chuc_danh || 'NGƯỜI LÀM BÁO CÁO / THỦ TRƯỞNG ĐƠN VỊ'}
                  </div>
                  <div style={{ fontSize: '12px', fontStyle: 'italic', color: '#64748b', marginTop: '2px' }}>
                    {outline.nguoi_ky_chu_ky || '(Ký và ghi rõ họ tên)'}
                  </div>
                  <div style={{ height: '60px' }}></div>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                    ........................................................
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--red)', fontSize: '14px' }}>Không thể nạp được khung báo cáo.</p>
          )}
        </div>

        {/* MODAL FOOTER */}
        <div
          style={{
            padding: '16px 24px',
            background: '#f8fafc',
            borderTop: '1px solid #e2e8f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span style={{ fontSize: '12px', color: '#64748b' }}>
            Xuất file định dạng <b>Microsoft Word (.docx)</b> chuẩn để gõ hoàn thiện.
          </span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={onClose}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                background: '#ffffff',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
              }}
            >
              Đóng
            </button>
            <button
              onClick={handleDownloadDocx}
              disabled={!outline}
              style={{
                padding: '8px 20px',
                borderRadius: '6px',
                border: 'none',
                background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 700,
                boxShadow: '0 4px 6px -1px rgba(22, 163, 74, 0.3)',
              }}
            >
              📥 Tải File Word (.docx)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
