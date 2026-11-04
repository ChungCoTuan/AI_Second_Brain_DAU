import React, { useState, useMemo, useEffect } from 'react';
import { useData } from '../context/DataContext';
import { useDetail } from '../context/DetailContext';
import { Filter, RotateCcw, Search } from 'lucide-react';
import { fold } from '../utils';
import { API_BASE_URL } from '../api/axiosClient';
import { PageHead, Badge, Pager, EmptyState, FilterPanel } from '../components/ui';

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
      await fetch(`${API_BASE_URL}/auditing/warnings/${encodeURIComponent(soHieu)}/resolve`, {
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
        <PageHead
          title="Ưu tiên xử lý trước"
          sub="Xếp theo mức độ: văn bản có căn cứ bị bãi bỏ và dính nhiều căn cứ hỏng lên đầu. Bấm để xem chi tiết."
        />

        {/* Card Bộ lọc */}
        <FilterPanel
          title="Bộ lọc danh sách ưu tiên xử lý"
          icon={<Filter size={18} style={{ color: 'var(--danger)' }} />}
          hasActive={hasActiveFilters}
          onReset={handleResetFilters}
        >
          <div className="panel-filters-grid">
            {/* Ô tìm kiếm */}
            <div className="field">
              <Search size={16} className="field-icon" />
              <input
                className="inp"
                type="search"
                placeholder="Tìm số hiệu, loại văn bản..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Mức độ ưu tiên */}
            <div>
              <select
                className="sel"
                style={{ width: '100%' }}
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
                className="sel"
                style={{ width: '100%' }}
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
                className="sel"
                style={{ width: '100%' }}
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
          <div className="panel-filters-summary">
            <div>
              Hiển thị: <b style={{ color: 'var(--ink)' }}>{filteredRows.length}</b> / {rows.length} văn bản
              {hasActiveFilters && <span style={{ color: 'var(--danger)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
            </div>
            {hasActiveFilters && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {searchTerm && (
                  <span className="filter-tag search">
                    "{searchTerm}"
                  </span>
                )}
                {filterLevel !== 'all' && (
                  <span className={`filter-tag ${filterLevel === 'high' ? 'danger' : 'warn'}`}>
                    {filterLevel === 'high' ? 'Ưu tiên cao' : 'Cần rà soát'}
                  </span>
                )}
                {filterLoai !== 'all' && (
                  <span className="filter-tag info">
                    {filterLoai}
                  </span>
                )}
                {filterBrokenCount !== 'all' && (
                  <span className="filter-tag neutral">
                    ≥ {filterBrokenCount} căn cứ hỏng
                  </span>
                )}
              </div>
            )}
          </div>
        </FilterPanel>

        <div id="priority">
          <div className="table-head">
            <span>#</span>
            <span>Văn bản</span>
            <span>Loại</span>
            <span>Căn cứ hỏng</span>
            <span>Mức độ</span>
          </div>

          {filteredRows.length === 0 ? (
            rows.length === 0 ? (
              <EmptyState tone="ok" title="Mọi thứ đang ổn định" desc="Hiện tại không có văn bản nào cần ưu tiên rà soát do xung đột căn cứ." />
            ) : (
              <EmptyState
                title="Không tìm thấy văn bản phù hợp"
                desc="Không có văn bản nào khớp với điều kiện lọc hiện tại."
                action={
                  <button className="btn btn-primary" onClick={handleResetFilters}>
                    <RotateCcw size={14} /> Xóa bộ lọc để xem tất cả
                  </button>
                }
              />
            )
          ) : (
            pagedRows.map((r: any, i: number) => {
              const isUnread = !readWarnings.includes(r.soHieu);
              const itemIdx = (page - 1) * limit + i + 1;
              return (
                <div
                  key={r.docId}
                  className={`row-item ${isUnread ? 'unread-item' : ''}`}
                  data-did={r.docId}
                  onClick={() => handleViewWarning(r.soHieu)}
                >
                  <span className="pk">{itemIdx}</span>
                  <span className="pd">{r.soHieu}</span>
                  <span className="pl">{r.loai || ''}</span>
                  <span className="pn">{r.n}</span>
                  <span>
                    {r.baiBo ? (
                      <Badge tone="danger">Ưu tiên cao</Badge>
                    ) : (
                      <Badge tone="warn">Cần rà</Badge>
                    )}
                  </span>
                </div>
              );
            })
          )}

          {filteredRows.length > 0 && (
            <Pager
              page={page}
              totalPages={totalPages}
              onPrev={() => setPage(p => Math.max(1, p - 1))}
              onNext={() => setPage(p => p + 1)}
            />
          )}
        </div>
      </div>
    </section>
  );
};

export default PriorityList;
