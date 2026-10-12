import React from 'react';
import { useData } from '../context/DataContext';

const Analytics: React.FC = () => {
  const { data } = useData();
  const I = data.insights || {};

  const renderBars = (rows: any[], className = '') => {
    if (!rows || rows.length === 0) {
      return (
        <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--muted)', fontSize: '13px' }}>
          Chưa có dữ liệu thống kê
        </div>
      );
    }
    const max = Math.max(...rows.map((r) => r.n), 1);
    return (
      <div className={className}>
        {rows.map((r, idx) => (
          <div className="bar" key={idx}>
            <span className="lbl" title={r.label}>
              {r.label}
            </span>
            <span className="track">
              <span className="fill" style={{ width: `${(r.n / max) * 100}%` }}></span>
            </span>
            <span className="val">{r.n}</span>
          </div>
        ))}
      </div>
    );
  };

  const renderDonut = () => {
    const a = I.thayThe || 0;
    const b = I.baiBo || 0;
    const tot = a + b;
    if (tot === 0) {
      return (
        <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--muted)', fontSize: '13px' }}>
          Chưa có sự kiện thay thế hoặc bãi bỏ
        </div>
      );
    }
    const r = 42;
    const c = 2 * Math.PI * r;
    const segA = (a / tot) * c;
    const segB = (b / tot) * c;

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r={r}
            fill="none"
            stroke="var(--amber)"
            strokeWidth="16"
            strokeDasharray={`${segA} ${c - segA}`}
            transform="rotate(-90 60 60)"
          />
          <circle
            cx="60"
            cy="60"
            r={r}
            fill="none"
            stroke="var(--red)"
            strokeWidth="16"
            strokeDasharray={`${segB} ${c - segB}`}
            strokeDashoffset={-segA}
            transform="rotate(-90 60 60)"
          />
          <text x="60" y="58" textAnchor="middle" fontSize="22" fontWeight="800" fill="var(--ink)">
            {tot}
          </text>
          <text x="60" y="74" textAnchor="middle" fontSize="10" fill="var(--muted)">
            lượt
          </text>
        </svg>
        <div style={{ fontSize: '13px' }}>
          <div>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '10px',
                background: 'var(--amber)',
                borderRadius: '2px',
                marginRight: '6px',
              }}
            ></span>
            Bị thay thế · <b>{a}</b>
          </div>
          <div style={{ marginTop: '6px' }}>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '10px',
                background: 'var(--red)',
                borderRadius: '2px',
                marginRight: '6px',
              }}
            ></span>
            Bị bãi bỏ · <b>{b}</b>
          </div>
        </div>
      </div>
    );
  };

  const t = I.tinCay;
  const renderTrust = () => {
    if (!t || t.tong === 0) {
      return (
        <div style={{ padding: '20px 0', color: 'var(--muted)', fontSize: '13px' }}>
          Chưa có dữ liệu trích xuất độ tin cậy.
        </div>
      );
    }
    return (
      <>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '12px' }}>
          <svg width="86" height="86" viewBox="0 0 86 86">
            <circle cx="43" cy="43" r="34" fill="none" stroke="var(--soft)" strokeWidth="12" />
            <circle
              cx="43"
              cy="43"
              r="34"
              fill="none"
              stroke="var(--green)"
              strokeWidth="12"
              strokeDasharray={`${(t.tb / 100) * 2 * Math.PI * 34} ${2 * Math.PI * 34}`}
              strokeLinecap="round"
              transform="rotate(-90 43 43)"
            />
            <text x="43" y="48" textAnchor="middle" fontSize="20" fontWeight="800" fill="var(--ink)">
              {t.tb}%
            </text>
          </svg>
          <div style={{ fontSize: '13px', color: 'var(--muted)' }}>
            Độ tin cậy trung bình khi AI bóc tách {t.tong} văn bản trong kho.
          </div>
        </div>
        <div className="tline">
          <b>
            {t.ocr}/{t.tong}
          </b>{' '}
          văn bản đọc qua kênh xử lý quang học (OCR)
        </div>
        <div className="tline">
          <b>
            {t.duoi80}/{t.tong}
          </b>{' '}
          văn bản có độ tin cậy dưới 80%: <span style={{ color: 'var(--amber)' }}>nên có người kiểm lại</span>
        </div>
        <div className="tline" style={{ color: 'var(--muted)', fontSize: '12px', marginTop: '8px' }}>
          Hệ thống không tự quyết; con người duyệt cuối (HITL) + lưu vết kiểm toán.
        </div>
      </>
    );
  };

  return (
    <section id="phan-tich" style={{ background: 'var(--soft)' }}>
      <div className="wrap">
        <h2>Phân tích nhanh</h2>
        <p className="sub">Rút trích trực tiếp từ kết quả rà soát, không phải số minh hoạ.</p>

        <div className="metrics" id="metrics">
          <div className="metric">
            <b>{I.luotVien ?? 0}</b>
            <span>lượt viện dẫn căn cứ đã hết hiệu lực</span>
          </div>
          <div className="metric">
            <b>
              {I.thayThe ?? 0} / {I.baiBo ?? 0}
            </b>
            <span>bị thay thế / bị bãi bỏ</span>
          </div>
          <div className="metric">
            <b>{I.vbNhieuCanCu ?? 0}</b>
            <span>văn bản dính từ 2 căn cứ hỏng trở lên</span>
          </div>
          <div className="metric">
            <b>{I.luotLuatMoi ?? 0}</b>
            <span>lượt do luật mới 2025 tới 2026</span>
          </div>
        </div>

        <div className="panels">
          <div className="panel">
            <div className="panel-h">Căn cứ bị viện nhiều nhất</div>
            {renderBars((I.topCanCu || []).map((x: any) => ({ label: x.canCu, n: x.n })))}
          </div>
          <div className="panel">
            <div className="panel-h">Thay thế / bãi bỏ</div>
            {renderDonut()}
            <div className="panel-h" style={{ marginTop: '18px' }}>
              Văn bản thay thế theo năm
            </div>
            {renderBars(
              (I.theoNam || []).map((x: any) => ({ label: x.nam, n: x.n })),
              'barY'
            )}
          </div>
        </div>

        <div className="panels" style={{ marginTop: '16px' }}>
          <div className="panel">
            <div className="panel-h">Rủi ro tập trung ở đâu</div>
            {renderBars((I.tapTrung?.theoLoai || []).map((x: any) => ({ label: x.loai, n: x.n })))}
            <div className="panel-h" style={{ marginTop: '16px' }}>
              Chủ đề hay gặp
            </div>
            <div className="chips">
              {(I.tapTrung?.theoChuDe || []).map((c: any, idx: number) => (
                <span className="chip2" key={idx}>
                  {c.chuDe} · {c.n}
                </span>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-h">Độ tin cậy trích xuất (chất lượng đọc)</div>
            {renderTrust()}
          </div>
        </div>

        <div className="note" style={{ marginTop: '16px' }}>
          <b>Nhận định rà soát:</b>{' '}
          {I.summaryText ? (
            <span>{I.summaryText}</span>
          ) : (
            <span>
              {I.luotVien > 0 ? (
                <>
                  Có <b>{I.luotVien}</b> lượt viện căn cứ hết hiệu lực hoặc bị thay thế. Cần ưu tiên rà soát để giảm thiểu rủi ro pháp lý.
                </>
              ) : (
                'Hệ thống đối soát chưa ghi nhận văn bản nào viện dẫn căn cứ đã hết hiệu lực. Toàn bộ căn cứ pháp lý đang ở trạng thái an toàn.'
              )}
            </span>
          )}
        </div>
      </div>
    </section>
  );
};

export default Analytics;
