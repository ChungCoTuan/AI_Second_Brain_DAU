import React, { useState } from 'react';
import { DEMO_DATA } from '../data';
import { fold, hl, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';

const Thresholds: React.FC = () => {
  const { openDetail } = useDetail();
  const CS = DEMO_DATA.conSoChot || [];
  const [searchTerm, setSearchTerm] = useState('');
  const [vb, setVb] = useState('all');

  const vbs = Array.from(new Set(CS.map((c: any) => c.vb))).sort();

  const q = fold(searchTerm);
  const kq = CS.filter((c: any) => {
    if (vb !== 'all' && c.vb !== vb) return false;
    if (!q) return true;
    return fold([c.giaTri, c.yNghia, c.vb, c.dieu].join(' ')).includes(q);
  });

  const show = kq.slice(0, 150);

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
    <section id="nguong" style={{ background: 'var(--soft)' }}>
      <div className="wrap">
        <h2>Sổ tra ngưỡng và định mức</h2>
        <p className="sub">
          Bóc tách mọi con số từ các nghị định, thông tư. Có ích khi cần viết tờ trình mà không nhớ chính xác con số nằm
          ở đâu.
        </p>

        <div className="srow">
          <input
            id="csTim"
            className="inp"
            type="search"
            placeholder="Lọc: 100%, 2 ty, tuyen sinh, 15 ngay, dien tich"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select id="csVb" className="sel" value={vb} onChange={(e) => setVb(e.target.value)}>
            <option value="all">Mọi văn bản</option>
            {vbs.map((v: any) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
          <span className="cnt" id="csCnt">
            <b>{kq.length}</b> / {CS.length} con số
          </span>
        </div>

        <div className="rlist" id="csList">
          {show.length > 0 ? (
            show.map((c: any, idx: number) => (
              <div
                key={idx}
                className="r r-cs"
                onClick={() => openDetail('bo:' + (c.docId || c.vb))}
              >
                <div>
                  <span className="rs">{hl(c.giaTri, q)}</span>
                  {c.nguonDoSo === false && (
                    <div className="rm" style={{ color: 'var(--amber)' }}>
                      con số này không có trong câu nguyên văn kèm theo
                    </div>
                  )}
                </div>
                <div>
                  <div className="rt">{hl(c.yNghia, q)}</div>
                  {c.vbDaChet && (
                    <div className="rm" style={{ color: 'var(--red)' }}>
                      Văn bản đã hết hiệu lực từ {fmtDate(c.vbDaChet.tuNgay)}, xem {c.vbDaChet.thayBang.join(', ')}
                    </div>
                  )}
                  {bangChung(c.nguon)}
                </div>
                <div className="rr">
                  {c.vb}
                  <br />
                  {c.dieu || ''}
                </div>
              </div>
            ))
          ) : (
            <div className="empty">Không có con số nào khớp.</div>
          )}
          {kq.length > show.length && (
            <div className="empty">Còn {kq.length - show.length} con số nữa, gõ thêm để thu hẹp.</div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Thresholds;
