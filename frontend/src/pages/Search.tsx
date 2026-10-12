import React, { useState, useEffect } from 'react';
import { fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';
import axiosClient from '../api/axiosClient';
import { Filter, RotateCcw, Search as SearchIcon } from 'lucide-react';

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
      
      axiosClient.get(`/search?${params.toString()}`)
        .then(res => {
          setResults(res.data.results || []);
          setTotal(res.data.total || 0);
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

  const handleResetFilters = () => {
    setSearchTerm('');
    setNguon('all');
    setLoai('all');
  };

  const hasActiveFilters = searchTerm !== '' || nguon !== 'all' || loai !== 'all';

  const loais = ['Công văn', 'Quyết định', 'Quy chế', 'Thông tư', 'Nghị định', 'Luật'];

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

        {/* Card Bộ lọc */}
        <div
          style={{
            background: '#fff',
            border: '1px solid var(--line, #e2e8f0)',
            borderRadius: '12px',
            padding: '16px 20px',
            marginTop: '16px',
            marginBottom: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, color: 'var(--ink, #1e293b)', fontSize: '15px' }}>
              <Filter size={18} style={{ color: 'var(--red, #b91c1c)' }} />
              <span>Bộ lọc tra cứu kho văn bản</span>
            </div>
            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '13px',
                  color: 'var(--red, #b91c1c)',
                  background: '#fee2e2',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                <RotateCcw size={14} /> Đặt lại bộ lọc
              </button>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {/* Ô tìm kiếm */}
            <div style={{ position: 'relative' }}>
              <SearchIcon
                size={16}
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--muted, #64748b)'
                }}
              />
              <input
                id="traTim"
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 12px 0 36px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  boxSizing: 'border-box'
                }}
                type="search"
                autoComplete="off"
                placeholder="Gõ không dấu cũng được: tuyen sinh, 54/2026..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Nguồn văn bản */}
            <div>
              <select
                id="traNguon"
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 28px 0 12px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  background: '#fff',
                  color: 'var(--ink, #1e293b)',
                  boxSizing: 'border-box'
                }}
                value={nguon}
                onChange={(e) => setNguon(e.target.value)}
              >
                <option value="all">Mọi nguồn</option>
                <option value="bộ">Văn bản pháp quy của Bộ/Chính phủ</option>
                <option value="trường">Văn bản nội bộ của Trường</option>
              </select>
            </div>

            {/* Loại văn bản */}
            <div>
              <select
                id="traLoai"
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 28px 0 12px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  background: '#fff',
                  color: 'var(--ink, #1e293b)',
                  boxSizing: 'border-box'
                }}
                value={loai}
                onChange={(e) => setLoai(e.target.value)}
              >
                <option value="all">Mọi loại văn bản</option>
                {loais.map((l: any) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Thanh tổng kết đếm số lượng */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: '12px',
              paddingTop: '10px',
              borderTop: '1px solid var(--line, #f1f5f9)',
              fontSize: '13px',
              color: 'var(--muted, #64748b)'
            }}
          >
            <div>
              {loading ? (
                <span>Đang tìm kiếm dữ liệu...</span>
              ) : (
                <>Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{results.length}</b> / {total} bản ghi</>
              )}
              {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
            </div>
            {hasActiveFilters && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {searchTerm && (
                  <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                    "{searchTerm}"
                  </span>
                )}
                {nguon !== 'all' && (
                  <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    Nguồn: {nguon === 'bộ' ? 'Bộ / CP' : 'Trường'}
                  </span>
                )}
                {loai !== 'all' && (
                  <span style={{ background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {loai}
                  </span>
                )}
              </div>
            )}
          </div>
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
            <div style={{ padding: '40px 20px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', margin: '16px 0' }}>
              <p style={{ color: 'var(--muted)', fontSize: '15px', margin: '0 0 12px 0' }}>Không tìm thấy văn bản phù hợp trong kho.</p>
              {hasActiveFilters && (
                <button
                  onClick={handleResetFilters}
                  style={{
                    padding: '8px 16px',
                    background: 'var(--blue, #2563eb)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '13px'
                  }}
                >
                  Xóa bộ lọc để xem tất cả
                </button>
              )}
            </div>
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
