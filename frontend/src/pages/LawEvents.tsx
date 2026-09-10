import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DEMO_DATA } from '../data';
import { badge, fmtDate, fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';

const LawEvents: React.FC = () => {
  const { openDetail } = useDetail();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const events = DEMO_DATA.events || [];
  const SK = DEMO_DATA.suKienHieuLuc || [];

  const q = fold(searchTerm);
  const filteredSK = SK.filter((s: any) => {
    if (!q) return true;
    return fold([s.cu, s.tenCu, s.moi, s.tenMoi, s.lyDo].join(' ')).includes(q);
  });

  const bangChung = (nguon: string, nhan?: string) => {
    if (!nguon) return null;
    return (
      <details style={{ marginTop: '4px' }}>
        <summary className="toggle" style={{ listStyle: 'none' }}>
          Xem nguyên văn
        </summary>
        <div className="ev-q" style={{ marginTop: '8px' }}>
          <span className="lbl">{nhan || 'Nguyên văn điều khoản'}</span>
          {nguon}
        </div>
      </details>
    );
  };

  return (
    <section id="su-kien">
      <div className="wrap">
        <h2>Cảnh báo theo sự kiện thay đổi luật</h2>
        <p className="sub">
          Mỗi thẻ là một lần luật thay đổi, kéo theo nhiều văn bản nội bộ. Bấm để lọc danh sách bên dưới (Chuyển sang
          trang Rà soát).
        </p>

        <div className="events">
          {events.map((e: any, i: number) => (
            <div
              key={i}
              className="ev"
              onClick={() => {
                navigate(`/review?event=${i}`);
              }}
            >
              <div className="n">
                {e.docs.length} <span style={{ fontSize: '13px', color: 'var(--muted)', fontWeight: 600 }}>văn bản</span>
              </div>
              <div className="chain">
                <span className="old">{e.canCu}</span> <span className="arrow">→</span>{' '}
                <span className="new">{e.thayBang}</span>
              </div>
              <span className={`pill ${badge(e.lyDo)}`}>{e.lyDo}</span>
            </div>
          ))}
        </div>

        <h2 id="doi-hieu-luc" style={{ marginTop: '34px', scrollMarginTop: '112px' }}>
          Mọi lần đổi hiệu lực mà kho biết
        </h2>
        <p className="sub">
          Bóc từ chính điều khoản thi hành của các văn bản Bộ, mỗi dòng kèm nguyên văn. Nhiều văn bản 2026 dùng chữ{' '}
          <b>hết hiệu lực thi hành</b> chứ không dùng <b>thay thế</b> hay <b>bãi bỏ</b>, nên tra theo hai từ khoá quen
          thuộc sẽ bỏ sót.
        </p>

        <div className="srow">
          <input
            id="skTim"
            className="inp"
            type="search"
            placeholder="Lọc: 17/2021, tuyen sinh, kiem dinh, 1982"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <span className="cnt">
            <b>{filteredSK.length}</b> / {SK.length} lần đổi hiệu lực
          </span>
        </div>

        <div className="rlist">
          {filteredSK.length > 0 ? (
            filteredSK.map((s: any, idx: number) => (
              <div
                key={idx}
                className="r r-sk"
                onClick={() => openDetail('bo:' + (s.docId || s.moi))}
              >
                <div>
                  <span className="rs" style={{ color: 'var(--red)' }}>
                    {hl(s.cu || '(không nêu số hiệu)', q)}
                  </span>
                  <div className="rm">{hl(s.tenCu || '', q)}</div>
                </div>
                <div>
                  <div className="rt">
                    {s.lyDo} bởi <b style={{ color: 'var(--green)' }}>{hl(s.moi, q)}</b>
                    {s.phamVi && s.phamVi !== 'toàn bộ' && (
                      <span className="tag2 dai"> phạm vi: {s.phamVi}</span>
                    )}
                  </div>
                  {bangChung(s.nguon)}
                </div>
                <div className="rr">{s.tuNgay ? fmtDate(s.tuNgay) : ''}</div>
              </div>
            ))
          ) : (
            <div className="empty">Không có lần đổi nào khớp.</div>
          )}
        </div>
      </div>
    </section>
  );
};

export default LawEvents;
