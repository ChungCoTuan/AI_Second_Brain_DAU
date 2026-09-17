import React, { useState } from 'react';
import { DEMO_DATA } from '../data';
import { fold, hl, nhanNgay, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';

const Obligations: React.FC = () => {
  const { openDetail } = useDetail();
  const NV = DEMO_DATA.nghiaVu || [];
  const [searchTerm, setSearchTerm] = useState('');
  const [vb, setVb] = useState('all');
  const [loai, setLoai] = useState('all');
  const [ct, setCt] = useState('trường');

  const vbs = Array.from(new Set(NV.map((n: any) => n.vb))).sort();
  const los = Array.from(new Set(NV.map((n: any) => n.loai).filter(Boolean))).sort();

  const nTruong = NV.filter((n: any) => (n.chuThe || 'trường') === 'trường').length;

  const q = fold(searchTerm);
  const kq = NV.filter((n: any) => {
    const la = (n.chuThe || 'trường') === 'trường';
    if (ct === 'trường' && !la) return false;
    if (ct === 'khac' && la) return false;
    if (vb !== 'all' && n.vb !== vb) return false;
    if (loai !== 'all' && n.loai !== loai) return false;
    if (!q) return true;
    return fold([n.noiDung, n.vb, n.dieu, n.loai].join(' ')).includes(q);
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
    <section id="viec">
      <div className="wrap">
        <h2>Việc phải làm</h2>
        <p className="sub">Tập hợp mọi điều khoản mang tính bắt buộc (nghĩa vụ, trách nhiệm).</p>
        <div className="srow">
          <input
            id="nvTim"
            className="inp"
            type="search"
            placeholder="Lọc: bao cao, cong khai, hieu truong"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select id="nvVb" className="sel" value={vb} onChange={(e) => setVb(e.target.value)}>
            <option value="all">Mọi văn bản</option>
            {vbs.map((v: any) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
          <select id="nvLoai" className="sel" value={loai} onChange={(e) => setLoai(e.target.value)}>
            <option value="all">Mọi loại việc</option>
            {los.map((l: any) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <select id="nvChuThe" className="sel" value={ct} onChange={(e) => setCt(e.target.value)}>
            <option value="trường">Việc của trường</option>
            <option value="khac">Việc của cơ quan khác</option>
            <option value="all">Tất cả chủ thể</option>
          </select>
          <span className="cnt" id="nvCnt">
            <b>{kq.length}</b> / {NV.length} nghĩa vụ
            {ct === 'trường' && (
              <span style={{ color: 'var(--muted)' }}> ({NV.length - nTruong} mục của cơ quan khác đang bị ẩn)</span>
            )}
          </span>
        </div>

        <div className="rlist" id="nvList">
          {show.length > 0 ? (
            show.map((n: any, idx: number) => (
              <div
                key={idx}
                className="r r-nv"
                onClick={() => openDetail('bo:' + (n.docId || n.vb))}
              >
                <div>
                  <span className="rs">{n.vb}</span>
                  <div className="rm">{n.dieu || ''}</div>
                </div>
                <div>
                  <div className="h" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '4px' }}>
                    <span className="tag2">{n.loai || 'khác'}</span>
                    {n.chuThe && n.chuThe !== 'trường' && (
                      <span className="tag2" style={{ background: 'var(--soft)', fontWeight: 700 }}>
                        {n.chuThe}
                      </span>
                    )}
                    {n.hanChot && <span className="tag2 han">hạn {nhanNgay(n.hanChot)}</span>}
                    {n.vbDaChet && (
                      <span
                        className="tag2"
                        style={{
                          background: 'var(--red-bg)',
                          color: 'var(--red)',
                          borderColor: '#fecaca',
                          fontWeight: 700,
                        }}
                      >
                        văn bản đã hết hiệu lực
                      </span>
                    )}
                  </div>
                  <div className="rt">{hl(n.noiDung, q)}</div>
                  {n.vbDaChet && (
                    <div className="rm" style={{ color: 'var(--red)' }}>
                      {n.vb} đã bị thay thế từ {fmtDate(n.vbDaChet.tuNgay)}. Nghĩa vụ này không còn là căn cứ để ban
                      hành mới, xem {n.vbDaChet.thayBang.join(', ')}
                    </div>
                  )}
                  {bangChung(n.nguon)}
                </div>
              </div>
            ))
          ) : (
            <div className="empty">Không có nghĩa vụ nào khớp.</div>
          )}
          {kq.length > show.length && (
            <div className="empty">Còn {kq.length - show.length} mục nữa, gõ thêm để thu hẹp.</div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Obligations;
