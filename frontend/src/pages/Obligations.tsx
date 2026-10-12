import React, { useState, useMemo, useEffect } from 'react';
import { useData } from '../context/DataContext';
import { fold, hl, nhanNgay, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';
import { Filter, RotateCcw, Search } from 'lucide-react';

const Obligations: React.FC = () => {
  const { openDetail } = useDetail();
  const { data, loading, markAsRead, readObligations } = useData();

  const NV = useMemo(() => {
    return [...(data.nghiaVu || [])].sort((a: any, b: any) => {
      const aUnread = !readObligations.includes(a.vb);
      const bUnread = !readObligations.includes(b.vb);
      if (aUnread && !bUnread) return -1;
      if (!aUnread && bUnread) return 1;
      return 0;
    });
  }, [data.nghiaVu, readObligations]);

  // State bộ lọc
  const [searchTerm, setSearchTerm] = useState('');
  const [vb, setVb] = useState('all');
  const [loai, setLoai] = useState('all');
  const [ct, setCt] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all'); // all, valid, dead

  const [page, setPage] = useState(1);
  const limit = 15;

  const vbs = useMemo(() => Array.from(new Set(NV.map((n: any) => n.vb))).sort(), [NV]);
  const los = useMemo(() => Array.from(new Set(NV.map((n: any) => n.loai).filter(Boolean))).sort(), [NV]);

  useEffect(() => {
    setPage(1);
  }, [searchTerm, vb, loai, ct, statusFilter]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setVb('all');
    setLoai('all');
    setCt('all');
    setStatusFilter('all');
  };

  const hasActiveFilters =
    searchTerm !== '' ||
    vb !== 'all' ||
    loai !== 'all' ||
    ct !== 'all' ||
    statusFilter !== 'all';

  const q = fold(searchTerm.trim());
  const kq = useMemo(() => {
    return NV.filter((n: any) => {
      const la = (n.chuThe || 'trường') === 'trường';
      if (ct === 'trường' && !la) return false;
      if (ct === 'khac' && la) return false;
      if (vb !== 'all' && n.vb !== vb) return false;
      if (loai !== 'all' && n.loai !== loai) return false;

      // Trạng thái hiệu lực
      if (statusFilter === 'valid' && n.vbDaChet) return false;
      if (statusFilter === 'dead' && !n.vbDaChet) return false;

      if (!q) return true;
      return fold([n.noiDung, n.vb, n.dieu, n.loai].join(' ')).includes(q);
    });
  }, [NV, ct, vb, loai, statusFilter, q]);

  const pagedList = kq.slice((page - 1) * limit, page * limit);
  const totalPages = Math.ceil(kq.length / limit) || 1;

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
        <h2>Việc phải làm {loading && <span style={{ fontSize: '14px', color: '#888' }}>(Đang tải dữ liệu từ AI...)</span>}</h2>
        <p className="sub">Tập hợp mọi điều khoản mang tính bắt buộc (nghĩa vụ, trách nhiệm).</p>

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
              <span>Bộ lọc tra cứu nghĩa vụ & trách nhiệm</span>
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
              <Search
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
                id="nvTim"
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
                placeholder="Lọc: báo cáo, công khai, hiệu trưởng..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Văn bản */}
            <div>
              <select
                id="nvVb"
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
                value={vb}
                onChange={(e) => setVb(e.target.value)}
              >
                <option value="all">Mọi văn bản ({vbs.length})</option>
                {vbs.map((v: any) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </div>

            {/* Loại việc */}
            <div>
              <select
                id="nvLoai"
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
                <option value="all">Mọi loại việc ({los.length})</option>
                {los.map((l: any) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </div>

            {/* Chủ thể */}
            <div>
              <select
                id="nvChuThe"
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
                value={ct}
                onChange={(e) => setCt(e.target.value)}
              >
                <option value="all">Tất cả chủ thể</option>
                <option value="trường">Việc của trường</option>
                <option value="khac">Việc của cơ quan khác</option>
              </select>
            </div>

            {/* Trạng thái hiệu lực */}
            <div>
              <select
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
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">Tất cả trạng thái VB</option>
                <option value="valid">Văn bản còn hiệu lực</option>
                <option value="dead">Văn bản đã hết hiệu lực</option>
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
              Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{kq.length}</b> / {NV.length} nghĩa vụ
              {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
            </div>
            {hasActiveFilters && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {searchTerm && (
                  <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                    "{searchTerm}"
                  </span>
                )}
                {vb !== 'all' && (
                  <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    VB: {vb}
                  </span>
                )}
                {loai !== 'all' && (
                  <span style={{ background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {loai}
                  </span>
                )}
                {ct !== 'all' && (
                  <span style={{ background: '#fef3c7', color: '#92400e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {ct === 'trường' ? 'Việc của trường' : 'Cơ quan khác'}
                  </span>
                )}
                {statusFilter !== 'all' && (
                  <span style={{ background: statusFilter === 'dead' ? '#fee2e2' : '#ecfdf5', color: statusFilter === 'dead' ? '#b91c1c' : '#047857', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {statusFilter === 'dead' ? 'VB đã hết hiệu lực' : 'VB còn hiệu lực'}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="rlist" id="nvList">
          {pagedList.length > 0 ? (
            pagedList.map((n: any, idx: number) => {
              const isUnread = !readObligations.includes(n.vb);
              return (
              <div
                key={idx}
                className={`r r-nv ${isUnread ? 'unread-item' : ''}`}
                onClick={() => {
                  openDetail('bo:' + (n.docId || n.vb));
                  markAsRead('obligation', n.vb);
                }}
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
            )})
          ) : (
            <div style={{ padding: '40px 20px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', margin: '16px 0' }}>
              <p style={{ color: 'var(--muted)', fontSize: '15px', margin: '0 0 12px 0' }}>Không có nghĩa vụ nào khớp với điều kiện lọc.</p>
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
            </div>
          )}

          {kq.length > 0 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{ padding: '8px 16px', background: page === 1 ? '#e0e0e0' : 'var(--blue)', color: page === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: page === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang trước</button>
              <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {page} / {totalPages}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages} style={{ padding: '8px 16px', background: page >= totalPages ? '#e0e0e0' : 'var(--blue)', color: page >= totalPages ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: page >= totalPages ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang sau</button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Obligations;
