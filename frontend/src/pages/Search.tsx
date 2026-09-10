import React, { useState } from 'react';
import { DEMO_DATA } from '../data';
import { fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';

const Search: React.FC = () => {
  const { openDetail } = useDetail();
  const [searchTerm, setSearchTerm] = useState('');
  const [nguon, setNguon] = useState('all');
  const [loai, setLoai] = useState('all');

  const C = DEMO_DATA.corpus || [];

  const nBo = C.filter((r: any) => r.nguon === 'bộ').length;
  const nTr = C.length - nBo;

  const loais = Array.from(new Set(C.map((r: any) => r.loai).filter(Boolean))).sort();

  const q = fold(searchTerm);
  const kq = C.filter((r: any) => {
    if (nguon !== 'all' && r.nguon !== nguon) return false;
    if (loai !== 'all' && r.loai !== loai) return false;
    if (!q) return true;
    return fold([r.soHieu, r.tomTat, (r.chuDe || []).join(' '), (r.tags || []).join(' '), r.coQuan].join(' ')).includes(q);
  });

  const show = kq.slice(0, 120);

  const cat = (s: string, n: number) => {
    s = String(s == null ? '' : s);
    if (s.length <= n) return s;
    const c = s.slice(0, n);
    const k = c.lastIndexOf(' ');
    return (k > n * 0.6 ? c.slice(0, k) : c) + '…';
  };

  return (
    <section id="tra-cuu" style={{ background: 'var(--soft)' }}>
      <div className="wrap">
        <h2>Tra cứu kho văn bản</h2>
        <p className="sub">
          <b>{C.length}</b> bản ghi tra được: <b>{nTr}</b> văn bản của trường và <b>{nBo}</b> văn bản của Bộ vừa bóc. Đây{' '}
          <b>không</b> phải toàn bộ kho: hệ thống khai {DEMO_DATA.tongCorpus || '?'} văn bản nhưng chỉ {nTr} cái có bản
          trích xuất. Phần chênh được nói rõ ở mục <a>Chỗ hệ thống chưa biết</a>.
        </p>
        <div className="srow">
          <input
            id="traTim"
            className="inp"
            type="search"
            autoComplete="off"
            placeholder="Gõ không dấu cũng được: tuyen sinh, kiem dinh, 54/2026, giao trinh, van bang"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select id="traNguon" className="sel" value={nguon} onChange={(e) => setNguon(e.target.value)}>
            <option value="all">Mọi nguồn</option>
            <option value="bộ">Văn bản pháp quy của Bộ/Chính phủ</option>
            <option value="trường">Văn bản nội bộ của Trường</option>
          </select>
          <select id="traLoai" className="sel" value={loai} onChange={(e) => setLoai(e.target.value)}>
            <option value="all">Mọi loại</option>
            {loais.map((l: any) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <span className="cnt" id="traCnt">
            <b>{kq.length}</b> / {C.length} bản ghi
          </span>
        </div>

        <div className="rlist" id="traList">
          {show.length > 0 ? (
            show.map((r: any) => (
              <div
                key={r.id}
                className="r"
                data-did={r.id}
                onClick={() => openDetail(r.id)}
              >
                <div>
                  <span className="rs">{hl(r.soHieu, q)}</span>
                  <div className="rm">
                    <span className={`src ${r.nguon === 'bộ' ? 'bo' : 'truong'}`}>
                      {r.nguon === 'bộ' ? 'BỘ' : 'TRƯỜNG'}
                    </span>{' '}
                    {r.loai || ''}
                  </div>
                </div>
                <div>
                  <div className="rt">{hl(cat(r.tomTat || '', 240), q)}</div>
                  {r.soDieu ? (
                    <div className="rm">
                      {r.soDieu} điều · {r.soNghiaVu || 0} nghĩa vụ
                    </div>
                  ) : null}
                  {r.chuDe && r.chuDe.length ? (
                    <div className="rm">{r.chuDe.join(' · ')}</div>
                  ) : null}
                </div>
                <div className="rr">
                  {r.ngay || ''}
                  {r.ocr ? (
                    <>
                      <br />
                      nguồn scan
                    </>
                  ) : null}
                </div>
              </div>
            ))
          ) : (
            <div className="empty">Không tìm thấy. Thử gõ số hiệu, ví dụ 54/2026, hoặc từ khoá không dấu.</div>
          )}
          {kq.length > show.length && (
            <div className="empty">Còn {kq.length - show.length} bản ghi nữa, gõ thêm để thu hẹp.</div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Search;
