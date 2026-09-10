import React from 'react';
import { DEMO_DATA } from '../data';

const Analytics: React.FC = () => {
  const I = DEMO_DATA.insights;

  const renderBars = (rows: any[], className = '') => {
    const max = Math.max(...rows.map((r) => r.n));
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
    const a = I.thayThe;
    const b = I.baiBo;
    const tot = a + b;
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
    if (!t) return null;
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
            Độ tin cậy trung bình khi AI bóc tách {t.tong} văn bản cảnh báo.
          </div>
        </div>
        <div className="tline">
          <b>
            {t.ocr}/{t.tong}
          </b>{' '}
          văn bản đọc bằng OCR (ảnh scan)
        </div>
        <div className="tline">
          <b>
            {t.duoi80}/{t.tong}
          </b>{' '}
          văn bản có độ tin cậy dưới 80%: <span style={{ color: 'var(--amber)' }}>nên có người kiểm lại</span>
        </div>
        <div className="tline" style={{ color: 'var(--muted)', fontSize: '12px', marginTop: '8px' }}>
          Hệ thống không tự quyết; con người duyệt cuối (HITL) + lưu vết.
        </div>
      </>
    );
  };

  return (
    <section id="phan-tich" style={{ background: 'var(--soft)' }}>
      <div className="wrap">
        <h2>Phân tích nhanh</h2>
        <p className="sub">Rút trực tiếp từ kết quả rà soát, không phải số minh hoạ.</p>

        <div className="metrics" id="metrics">
          <div className="metric">
            <b>{I.luotVien}</b>
            <span>lượt viện dẫn căn cứ đã hết hiệu lực</span>
          </div>
          <div className="metric">
            <b>
              {I.thayThe} / {I.baiBo}
            </b>
            <span>bị thay thế / bị bãi bỏ</span>
          </div>
          <div className="metric">
            <b>{I.vbNhieuCanCu}</b>
            <span>văn bản dính từ 2 căn cứ hỏng trở lên</span>
          </div>
          <div className="metric">
            <b>{I.luotLuatMoi}</b>
            <span>lượt do luật mới 2025 tới 2026</span>
          </div>
        </div>

        <div className="panels">
          <div className="panel">
            <div className="panel-h">Căn cứ bị viện nhiều nhất</div>
            {renderBars(I.topCanCu.map((x: any) => ({ label: x.canCu, n: x.n })))}
          </div>
          <div className="panel">
            <div className="panel-h">Thay thế / bãi bỏ</div>
            {renderDonut()}
            <div className="panel-h" style={{ marginTop: '18px' }}>
              Văn bản thay thế theo năm
            </div>
            {renderBars(
              I.theoNam.map((x: any) => ({ label: x.nam, n: x.n })),
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
          <b>Vì sao bây giờ:</b> {I.luotLuatMoi}/{I.luotVien} lượt viện căn cứ hết hiệu lực là do đợt sửa luật lớn{' '}
          <b>2025 tới 2026</b>. Riêng <b>Luật Giáo dục đại học 125/2025</b> đã có nguyên văn điều khoản thi hành trong
          kho và tự khai làm 5 luật cũ hết hiệu lực. Càng để lâu, số văn bản đứng trên căn cứ đã chết càng dồn.
        </div>
      </div>
    </section>
  );
};

export default Analytics;
