import React, { useState, useEffect } from 'react';
import { fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';

const Search: React.FC = () => {
  const { openDetail } = useDetail();
  const [searchTerm, setSearchTerm] = useState('');
  const [nguon, setNguon] = useState('all');
  const [loai, setLoai] = useState('all');
  
  const [results, setResults] = useState<any[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [page, setPage] = useState<number>(1);
  const limit = 10;

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      setLoading(true);
      const params = new URLSearchParams({
        q: searchTerm,
        nguon: nguon,
        loai: loai,
        page: page.toString(),
        limit: limit.toString()
      });
      
      fetch(`http://localhost:8000/api/v1/search?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
          setResults(data.results || []);
          setTotal(data.total || 0);
          setLoading(false);
        })
        .catch(err => {
          console.error("Lỗi khi tìm kiếm:", err);
          setLoading(false);
        });
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, nguon, loai, page]);

  // Reset page to 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [searchTerm, nguon, loai]);

  const nBo = results.filter((r: any) => r.nguon === 'bộ').length;
  const nTr = results.length - nBo;

  // Giả lập danh sách loại văn bản để hiển thị trong select box
  const loais = ['Công văn', 'Quyết định', 'Quy chế', 'Thông tư'];

  const q = fold(searchTerm);
  const show = results;

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
          <b>{results.length}</b> bản ghi phù hợp trên tổng số <b>{total}</b> văn bản trong kho (được trả về qua API động).
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
            {loading ? <b>Đang tìm...</b> : <><b>{results.length}</b> / {total} bản ghi</>}
          </span>
        </div>

        <div className="rlist" id="traList">
          {show.map((r: any) => (
              <div
                key={r.id || r.soHieu}
                className="r"
                data-did={r.id || r.soHieu}
                onClick={() => openDetail(r.soHieu)}
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
            ))}
          {results.length === 0 && !loading && (
            <div className="empty">Không tìm thấy. Thử gõ số hiệu, ví dụ 54/2026, hoặc từ khoá không dấu.</div>
          )}
        </div>
        
        {total > 0 && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              style={{
                padding: '8px 16px', background: page === 1 ? '#e0e0e0' : 'var(--blue)', color: page === 1 ? '#888' : '#fff',
                border: 'none', borderRadius: '8px', cursor: page === 1 ? 'not-allowed' : 'pointer', fontWeight: 600
              }}
            >
              Trang trước
            </button>
            <span style={{ fontWeight: 600, color: 'var(--text)' }}>
              Trang {page} / {Math.ceil(total / limit) || 1}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(total / limit)}
              style={{
                padding: '8px 16px', background: page >= Math.ceil(total / limit) ? '#e0e0e0' : 'var(--blue)', color: page >= Math.ceil(total / limit) ? '#888' : '#fff',
                border: 'none', borderRadius: '8px', cursor: page >= Math.ceil(total / limit) ? 'not-allowed' : 'pointer', fontWeight: 600
              }}
            >
              Trang sau
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

export default Search;
