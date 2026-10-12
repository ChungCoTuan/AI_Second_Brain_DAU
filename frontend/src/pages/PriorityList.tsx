import React, { useState, useMemo, useEffect } from 'react';
import { useData } from '../context/DataContext';
import { useDetail } from '../context/DetailContext';
import { Filter, RotateCcw, Search } from 'lucide-react';
import { fold } from '../utils';

const PriorityList: React.FC = () => {
  const { openDetail } = useDetail();
  const { data, refreshData, markAsRead, readWarnings } = useData();

  const rows = useMemo(() => {
    return [...(data.insights?.uuTien || [])].sort((a: any, b: any) => {
      const aUnread = !readWarnings.includes(a.soHieu);
      const bUnread = !readWarnings.includes(b.soHieu);
      if (aUnread && !bUnread) return -1;
      if (!aUnread && bUnread) return 1;
      return 0;
    });
  }, [data.insights?.uuTien, readWarnings]);

  // State bộ lọc
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState<'all' | 'high' | 'medium'>('all');
  const [filterLoai, setFilterLoai] = useState('all');
  const [filterBrokenCount, setFilterBrokenCount] = useState('all');

  const [page, setPage] = useState(1);
  const limit = 15;

  // Trích xuất danh sách loại văn bản động
  const availableTypes = useMemo(() => {
    const types = new Set<string>();
    rows.forEach((r: any) => {
      if (r.loai && r.loai.trim()) types.add(r.loai.trim());
    });
    return Array.from(types).sort();
  }, [rows]);

  // Reset phân trang khi đổi bộ lọc
  useEffect(() => {
    setPage(1);
  }, [searchTerm, filterLevel, filterLoai, filterBrokenCount]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setFilterLevel('all');
    setFilterLoai('all');
    setFilterBrokenCount('all');
  };

  const hasActiveFilters =
    searchTerm !== '' ||
    filterLevel !== 'all' ||
    filterLoai !== 'all' ||
    filterBrokenCount !== 'all';

  // Lọc dữ liệu
  const filteredRows = useMemo(() => {
    return rows.filter((r: any) => {
      // 1. Mức độ ưu tiên
      if (filterLevel === 'high' && !r.baiBo) return false;
      if (filterLevel === 'medium' && r.baiBo) return false;

      // 2. Loại văn bản
      if (filterLoai !== 'all' && (r.loai || '').trim() !== filterLoai) return false;

      // 3. Số căn cứ hỏng
      if (filterBrokenCount !== 'all') {
        const minCount = parseInt(filterBrokenCount, 10);
        if (isNaN(minCount) || (r.n || 0) < minCount) return false;
      }

      // 4. Tìm kiếm từ khóa
      if (searchTerm.trim()) {
        const q = fold(searchTerm.trim());
        const matchText = fold([r.soHieu || '', r.loai || ''].join(' '));
        if (!matchText.includes(q)) return false;
      }

      return true;
    });
  }, [rows, filterLevel, filterLoai, filterBrokenCount, searchTerm]);

  const pagedRows = filteredRows.slice((page - 1) * limit, page * limit);
  const totalPages = Math.ceil(filteredRows.length / limit) || 1;

  const handleViewWarning = async (soHieu: string) => {
    markAsRead('warning', soHieu);
    openDetail(soHieu);
    try {
      await fetch(`http://localhost:8000/api/v1/auditing/warnings/${encodeURIComponent(soHieu)}/resolve`, {
        method: 'POST'
      });
      refreshData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <section id="uu-tien">
      <div className="wrap">
        <h2>Ưu tiên xử lý trước</h2>
        <p className="sub">
          Xếp theo mức độ: văn bản có căn cứ <b>bị bãi bỏ</b> và dính <b>nhiều căn cứ hỏng</b> lên đầu. Bấm để xem chi tiết.
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
              <span>Bộ lọc danh sách ưu tiên xử lý</span>
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
                placeholder="Tìm số hiệu, loại văn bản..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Mức độ ưu tiên */}
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
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value as any)}
              >
                <option value="all">Tất cả mức độ</option>
                <option value="high">Ưu tiên cao (Căn cứ bị bãi bỏ)</option>
                <option value="medium">Cần rà soát (Căn cứ thay thế)</option>
              </select>
            </div>

            {/* Loại văn bản */}
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
                value={filterLoai}
                onChange={(e) => setFilterLoai(e.target.value)}
              >
                <option value="all">Tất cả loại văn bản</option>
                {availableTypes.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            {/* Số căn cứ hỏng */}
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
                value={filterBrokenCount}
                onChange={(e) => setFilterBrokenCount(e.target.value)}
              >
                <option value="all">Tất cả số căn cứ hỏng</option>
                <option value="1">Từ 1 căn cứ hỏng trở lên</option>
                <option value="2">Từ 2 căn cứ hỏng trở lên</option>
                <option value="3">Từ 3 căn cứ hỏng trở lên</option>
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
              Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{filteredRows.length}</b> / {rows.length} văn bản
              {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
            </div>
            {hasActiveFilters && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {searchTerm && (
                  <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                    "{searchTerm}"
                  </span>
                )}
                {filterLevel !== 'all' && (
                  <span style={{ background: filterLevel === 'high' ? '#fee2e2' : '#fef3c7', color: filterLevel === 'high' ? '#b91c1c' : '#92400e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterLevel === 'high' ? 'Ưu tiên cao' : 'Cần rà soát'}
                  </span>
                )}
                {filterLoai !== 'all' && (
                  <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterLoai}
                  </span>
                )}
                {filterBrokenCount !== 'all' && (
                  <span style={{ background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    ≥ {filterBrokenCount} căn cứ hỏng
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        <div id="priority">
          <div className="prow phead" style={{ display: 'grid', gridTemplateColumns: '40px 3fr 2fr 1fr 1fr', textTransform: 'uppercase', fontSize: '11px', color: 'var(--muted)', fontWeight: 700, paddingBottom: '12px', borderBottom: '1px solid var(--line)', marginBottom: '8px' }}>
            <span>#</span>
            <span>Văn bản</span>
            <span>Loại</span>
            <span>Căn cứ hỏng</span>
            <span>Mức độ</span>
          </div>

          {filteredRows.length === 0 ? (
            <div style={{ padding: '60px 40px', textAlign: 'center', backgroundColor: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', marginTop: '20px' }}>
              {rows.length === 0 ? (
                <>
                  <h3 style={{ color: 'var(--green)', fontSize: '20px', marginBottom: '8px' }}>Mọi thứ đang ổn định</h3>
                  <p className="sub">Hiện tại không có văn bản nào cần ưu tiên rà soát do xung đột căn cứ.</p>
                </>
              ) : (
                <>
                  <h3 style={{ color: 'var(--muted)', fontSize: '18px', marginBottom: '8px' }}>Không tìm thấy văn bản phù hợp</h3>
                  <p className="sub" style={{ marginBottom: '16px' }}>Không có văn bản nào khớp với điều kiện lọc hiện tại.</p>
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
                </>
              )}
            </div>
          ) : (
            pagedRows.map((r: any, i: number) => {
              const lvl = r.baiBo ? (
                <span className="lv lv-hi" style={{ padding: '4px 10px', border: '1px solid #ffd0d0', color: 'var(--red)', background: '#fff0f0', borderRadius: '20px', fontSize: '11px', fontWeight: 600 }}>Ưu tiên cao</span>
              ) : (
                <span className="lv lv-md" style={{ padding: '4px 10px', border: '1px solid #ffe4b5', color: 'var(--amber)', background: '#fffdf5', borderRadius: '20px', fontSize: '11px', fontWeight: 600 }}>Cần rà</span>
              );
              const isUnread = !readWarnings.includes(r.soHieu);
              const itemIdx = (page - 1) * limit + i + 1;
              return (
                <div
                  key={r.docId}
                  className={`prow ${isUnread ? 'unread-item' : ''}`}
                  style={{ display: 'grid', gridTemplateColumns: '40px 3fr 2fr 1fr 1fr', alignItems: 'center', padding: '12px 8px', borderBottom: '1px solid var(--soft)', cursor: 'pointer', transition: 'background 0.2s' }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--soft)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  data-did={r.docId}
                  onClick={() => handleViewWarning(r.soHieu)}
                >
                  <span className="pk" style={{ color: 'var(--red)', fontWeight: 700 }}>{itemIdx}</span>
                  <span className="pd" style={{ fontWeight: 600, color: 'var(--ink)' }}>{r.soHieu}</span>
                  <span className="pl" style={{ color: 'var(--muted)' }}>{r.loai || ''}</span>
                  <span className="pn" style={{ color: 'var(--red)', fontWeight: 700 }}>{r.n}</span>
                  <span>{lvl}</span>
                </div>
              );
            })
          )}

          {filteredRows.length > 0 && (
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

export default PriorityList;
