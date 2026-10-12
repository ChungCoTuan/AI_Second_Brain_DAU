import React, { useState, useEffect, useMemo } from 'react';
import { Check, X, AlertTriangle, Edit2, RefreshCw, Clock, Filter, RotateCcw, Search } from 'lucide-react';
import { useData } from '../context/DataContext';
import { fold } from '../utils';
import axiosClient from '../api/axiosClient';

interface ReviewItem {
  id: number;
  document_id: number;
  vb: string;
  dieu: string;
  nguon: string;
  status: string;
  chuThe?: string;
  noiDung?: string;
  hanChot?: string;
  loai?: string;
  giaTri?: string;
  yNghia?: string;
  tom_tat?: string;
  nli_label?: string;
  created_at?: string;
  _itemType: 'nghiaVu' | 'conSoChot';
}

const ReviewQueue: React.FC = () => {
  const { refreshData } = useData();
  const [pendingItems, setPendingItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'nghiaVu' | 'conSoChot'>('all');
  const [filterNli, setFilterNli] = useState<string>('all'); // all, entailment, contradiction, neutral
  const [page, setPage] = useState(1);
  const limit = 15;

  // Edit states
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editedText, setEditedText] = useState<string>('');
  const [revalidating, setRevalidating] = useState<boolean>(false);
  const [tempLabel, setTempLabel] = useState<string | null>(null);

  // Reset page khi filter thay đổi - phải đặt ở đây, trước mọi early return
  useEffect(() => { setPage(1); }, [searchQuery, filterType, filterNli]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setFilterType('all');
    setFilterNli('all');
  };

  const hasActiveFilters = searchQuery !== '' || filterType !== 'all' || filterNli !== 'all';

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const fetchPendingData = async () => {
    try {
      const response = await axiosClient.get('/review/pending');
      const data = response.data;

      const nghiaVu: ReviewItem[] = (data.nghiaVu || []).map((i: any) => ({ ...i, _itemType: 'nghiaVu' }));
      const conSoChot: ReviewItem[] = (data.conSoChot || []).map((i: any) => ({ ...i, _itemType: 'conSoChot' }));

      const combined = [...nghiaVu, ...conSoChot];
      combined.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());

      setPendingItems(combined);
    } catch (error) {
      console.error("Lỗi khi tải dữ liệu chờ duyệt:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingData();
  }, []);

  const handlePublish = async (itemType: string, id: number, textToPublish?: string) => {
    try {
      const body = textToPublish ? { edited_summary: textToPublish } : {};
      const response = await axiosClient.put(`/review/${itemType}/${id}/publish`, body);
      if (response.status === 200) {
        setPendingItems(prev => prev.filter(item => !(item._itemType === itemType && item.id === id)));
        refreshData();
        showToast("Đã duyệt & Publish thành công!");
        setEditingId(null);
        setTempLabel(null);
      }
    } catch (error) {
      console.error("Lỗi khi duyệt:", error);
    }
  };

  const handleReject = async (itemType: string, id: number) => {
    try {
      const response = await axiosClient.put(`/review/${itemType}/${id}/reject`);
      if (response.status === 200) {
        setPendingItems(prev => prev.filter(item => !(item._itemType === itemType && item.id === id)));
        refreshData();
      }
    } catch (error) {
      console.error("Lỗi khi từ chối:", error);
    }
  };

  const handleRevalidate = async (originalText: string) => {
    if (!editedText) return;
    setRevalidating(true);
    try {
      const res = await axiosClient.post('/review/revalidate', {
        original_text: originalText,
        edited_summary: editedText
      });
      setTempLabel(res.data.nli_label);
    } catch (e) {
      console.error(e);
    } finally {
      setRevalidating(false);
    }
  };

  const startEditing = (type: string, id: number, initialText: string, currentLabel?: string) => {
    setEditingId(`${type}-${id}`);
    setEditedText(initialText);
    setTempLabel(currentLabel || null);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Chưa rõ thời gian';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    }).format(date);
  };

  const displayedItems = useMemo(() => {
    return pendingItems.filter(item => {
      // 1. Loại bóc tách
      if (filterType !== 'all' && item._itemType !== filterType) return false;

      // 2. Nhãn suy luận NLI
      if (filterNli !== 'all' && item.nli_label !== filterNli) return false;

      // 3. Tìm kiếm từ khóa
      if (searchQuery.trim()) {
        const q = fold(searchQuery.trim());
        const matchText = fold([
          item.vb || '',
          item.dieu || '',
          item.noiDung || '',
          item.giaTri || '',
          item.yNghia || '',
          item.tom_tat || '',
          item.nguon || '',
          item.chuThe || '',
          item.loai || ''
        ].join(' '));
        if (!matchText.includes(q)) return false;
      }

      return true;
    });
  }, [pendingItems, filterType, filterNli, searchQuery]);

  const totalPages = Math.ceil(displayedItems.length / limit) || 1;
  const pagedItems = displayedItems.slice((page - 1) * limit, page * limit);

  if (loading) {
    return (
      <section id="ra-soat">
        <div className="wrap">
          <h2>Cổng Duyệt Văn Bản (Publish Gate)</h2>
          <p className="sub">Đang tải danh sách chờ duyệt từ mô hình AI...</p>
        </div>
      </section>
    );
  }


  const renderItemRightColumn = (item: ReviewItem) => {
    const isEditing = editingId === `${item._itemType}-${item.id}`;
    const displayLabel = isEditing && tempLabel ? tempLabel : item.nli_label;

    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between' }}>
          <span className="badge" style={{ background: 'var(--hover)', color: 'var(--text)' }}>Nguyên bản gốc</span>
          {isEditing && revalidating ? (
            <span className="badge" style={{ background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center' }}>
              <RefreshCw size={12} className="spin" style={{ marginRight: '6px' }} /> Đang suy luận NLI...
            </span>
          ) : (
            <>
              {displayLabel === 'entailment' && <span className="badge" style={{ background: 'var(--green)', color: 'white' }}>🟢 An toàn (Entailment)</span>}
              {displayLabel === 'contradiction' && <span className="badge" style={{ background: 'var(--red)', color: 'white' }}>🔴 Mâu thuẫn (Contradiction)</span>}
              {displayLabel === 'neutral' && <span className="badge" style={{ background: 'var(--amber)', color: 'white' }}>🟠 Chung chung (Neutral)</span>}
            </>
          )}
        </div>

        {item.tom_tat && !isEditing && (
          <div style={{ marginBottom: '12px', padding: '12px', backgroundColor: 'var(--surface-color, #f8f9fa)', borderLeft: '3px solid var(--primary)', borderRadius: '4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--primary)' }}>AI Tóm tắt:</div>
              <button className="btn" style={{ padding: '4px 10px', fontSize: '12px', background: 'transparent', color: 'var(--primary)', border: '1px solid var(--primary)', borderRadius: '6px', cursor: 'pointer' }} onClick={() => startEditing(item._itemType, item.id, item.tom_tat || '', item.nli_label)}>
                <Edit2 size={12} style={{ display: 'inline', marginRight: '4px' }} /> Sửa
              </button>
            </div>
            <div style={{ fontSize: '14px', lineHeight: 1.6 }}>{item.tom_tat}</div>
          </div>
        )}

        {isEditing && (
          <div style={{ marginBottom: '12px', padding: '12px', backgroundColor: '#fffbe6', borderLeft: '3px solid var(--amber)', borderRadius: '4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--amber)' }}>Chế độ Sửa (Human-in-the-loop):</div>
              <button className="btn" disabled={revalidating} style={{ padding: '4px 10px', fontSize: '12px', background: 'var(--amber)', color: 'white', borderRadius: '6px', cursor: 'pointer', border: 'none' }} onClick={() => handleRevalidate(item.nguon)}>
                <RefreshCw size={12} style={{ display: 'inline', marginRight: '4px' }} className={revalidating ? 'spin' : ''} /> Kiểm tra lại NLI
              </button>
            </div>
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              disabled={revalidating}
              style={{ width: '100%', minHeight: '80px', padding: '10px', fontSize: '14px', border: '1px solid var(--border)', borderRadius: '6px', marginTop: '4px', opacity: revalidating ? 0.7 : 1, cursor: revalidating ? 'not-allowed' : 'text' }}
            />
          </div>
        )}

        <div style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--muted)', fontStyle: 'italic', flex: 1, backgroundColor: 'var(--bg)', padding: '16px', borderRadius: '8px', border: '1px dashed var(--line)', maxHeight: '180px', overflowY: 'auto' }}>
          "{item.nguon}"
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '20px', justifyContent: 'flex-end' }}>
          <button
            className="btn"
            style={{ background: '#fff', border: '1px solid var(--line)', color: 'var(--red)', display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, transition: '0.2s' }}
            onClick={() => handleReject(item._itemType, item.id)}
            onMouseOver={(e) => (e.currentTarget.style.background = 'var(--red-bg)')}
            onMouseOut={(e) => (e.currentTarget.style.background = '#fff')}
          >
            <X size={16} /> Từ chối
          </button>

          {isEditing ? (
            <button
              className="btn"
              style={{ background: 'var(--amber)', color: 'white', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 'bold', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', border: 'none' }}
              onClick={() => handlePublish(item._itemType, item.id, editedText)}
            >
              <Check size={16} /> Sửa & Duyệt
            </button>
          ) : (
            <button
              className="btn"
              style={{ background: 'var(--green)', color: 'white', display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', border: 'none', fontWeight: 600 }}
              onClick={() => handlePublish(item._itemType, item.id)}
            >
              <Check size={16} /> Duyệt giữ nguyên
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <section id="ra-soat" style={{ paddingBottom: '60px' }}>
      {toastMessage && (
        <div style={{
          position: 'fixed', bottom: '30px', right: '30px',
          background: 'var(--green)', color: 'white',
          padding: '14px 28px', borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
          display: 'flex', alignItems: 'center', gap: '10px', zIndex: 9999,
          fontWeight: 600, fontSize: '15px'
        }}>
          <Check size={20} /> {toastMessage}
        </div>
      )}
      <div className="wrap">
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '28px', color: 'var(--blue)', marginBottom: '8px' }}>Cổng Duyệt Văn Bản</h2>
          <p className="sub" style={{ margin: 0, fontSize: '15px' }}>
            <AlertTriangle size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '6px', color: 'var(--amber)' }} />
            Rà soát kết quả bóc tách của AI để đảm bảo độ chính xác tuyệt đối.
          </p>
        </div>

        {/* Card Bộ lọc */}
        <div
          style={{
            background: '#fff',
            border: '1px solid var(--line, #e2e8f0)',
            borderRadius: '12px',
            padding: '16px 20px',
            marginBottom: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, color: 'var(--ink, #1e293b)', fontSize: '15px' }}>
              <Filter size={18} style={{ color: 'var(--red, #b91c1c)' }} />
              <span>Bộ lọc danh sách bóc tách chờ duyệt</span>
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

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
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
                placeholder="Tìm số hiệu, điều, nội dung, tóm tắt..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Phân loại bóc tách */}
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
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as any)}
              >
                <option value="all">Tất cả mục ({pendingItems.length})</option>
                <option value="nghiaVu">Nghĩa vụ ({pendingItems.filter(i => i._itemType === 'nghiaVu').length})</option>
                <option value="conSoChot">Con số chốt ({pendingItems.filter(i => i._itemType === 'conSoChot').length})</option>
              </select>
            </div>

            {/* Đánh giá suy luận NLI */}
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
                value={filterNli}
                onChange={(e) => setFilterNli(e.target.value)}
              >
                <option value="all">Tất cả nhãn NLI</option>
                <option value="entailment">🟢 An toàn (Entailment)</option>
                <option value="contradiction">🔴 Mâu thuẫn (Contradiction)</option>
                <option value="neutral">🟠 Chung chung (Neutral)</option>
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
              Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{displayedItems.length}</b> / {pendingItems.length} mục chờ duyệt
              {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
            </div>
            {hasActiveFilters && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {searchQuery && (
                  <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                    "{searchQuery}"
                  </span>
                )}
                {filterType !== 'all' && (
                  <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterType === 'nghiaVu' ? 'Nghĩa vụ' : 'Con số chốt'}
                  </span>
                )}
                {filterNli !== 'all' && (
                  <span style={{ background: filterNli === 'entailment' ? '#ecfdf5' : filterNli === 'contradiction' ? '#fee2e2' : '#fef3c7', color: filterNli === 'entailment' ? '#047857' : filterNli === 'contradiction' ? '#b91c1c' : '#92400e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterNli === 'entailment' ? 'An toàn' : filterNli === 'contradiction' ? 'Mâu thuẫn' : 'Chung chung'}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {pendingItems.length === 0 ? (
          <div style={{ padding: '60px 40px', textAlign: 'center', backgroundColor: '#fff', borderRadius: '16px', border: '1px dashed var(--line)', marginTop: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <h3 style={{ color: 'var(--green)', fontSize: '22px', marginBottom: '8px' }}>Tuyệt vời! 🎉</h3>
            <p className="sub" style={{ fontSize: '16px' }}>Không còn văn bản nào đang chờ duyệt trong hàng đợi.</p>
          </div>
        ) : displayedItems.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', margin: '16px 0' }}>
            <p style={{ color: 'var(--muted)', fontSize: '15px', margin: '0 0 12px 0' }}>Không tìm thấy mục nào khớp với điều kiện lọc.</p>
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
        ) : (
          <div className="cards" style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '20px' }}>
            {pagedItems.map((item) => (
              <div key={`${item._itemType}-${item.id}`} className="card" style={{
                display: 'flex', gap: '24px', alignItems: 'stretch', padding: '24px',
                borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.04)', border: '1px solid var(--line)',
                background: '#fff', transition: '0.3s'
              }}>
                <div style={{ flex: 1, paddingRight: '24px', borderRight: '1px solid var(--line)', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <span className="badge" style={{
                        background: item._itemType === 'nghiaVu' ? 'var(--blue-50)' : 'var(--amber-bg)',
                        color: item._itemType === 'nghiaVu' ? 'var(--blue)' : 'var(--amber)',
                        padding: '4px 10px', borderRadius: '8px', fontSize: '12px', fontWeight: 700, width: 'fit-content'
                      }}>
                        {item._itemType === 'nghiaVu' ? '📋 Bóc tách Nghĩa vụ' : '🎯 Bóc tách Con số chốt'}
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--muted)', fontSize: '12px', marginTop: '4px' }}>
                        <Clock size={14} />
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="doc" style={{ fontSize: '16px', fontWeight: 700, color: 'var(--ink)', marginBottom: '16px', lineHeight: 1.4 }}>
                    {item.vb} - {item.dieu}
                  </div>

                  <div style={{ fontSize: '15px', lineHeight: '1.7', background: 'var(--soft)', padding: '16px', borderRadius: '12px', flex: 1 }}>
                    {item._itemType === 'nghiaVu' ? (
                      <>
                        <div style={{ marginBottom: '12px' }}><b style={{ color: 'var(--muted)' }}>Chủ thể:</b> <span style={{ color: 'var(--blue)', fontWeight: 600 }}>{item.chuThe}</span></div>
                        <div style={{ marginBottom: '12px' }}><b style={{ color: 'var(--muted)' }}>Hành động:</b> <span>{item.noiDung}</span></div>
                        <div><b style={{ color: 'var(--muted)' }}>Hạn chót:</b> <span style={{ color: 'var(--red)', fontWeight: 500 }}>{item.hanChot || 'Không quy định'}</span></div>
                      </>
                    ) : (
                      <>
                        <div style={{ marginBottom: '12px' }}><b style={{ color: 'var(--muted)' }}>Giá trị:</b> <span style={{ color: 'var(--amber)', fontWeight: 'bold', fontSize: '18px' }}>{item.giaTri}</span></div>
                        <div><b style={{ color: 'var(--muted)' }}>Ý nghĩa:</b> <span>{item.yNghia}</span></div>
                      </>
                    )}
                  </div>
                </div>
                {renderItemRightColumn(item)}
              </div>
            ))}

            {displayedItems.length > 0 && (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  style={{ padding: '8px 16px', background: page === 1 ? '#e0e0e0' : 'var(--blue)', color: page === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: page === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}
                >
                  Trang trước
                </button>
                <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {page} / {totalPages}</span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= totalPages}
                  style={{ padding: '8px 16px', background: page >= totalPages ? '#e0e0e0' : 'var(--blue)', color: page >= totalPages ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: page >= totalPages ? 'not-allowed' : 'pointer', fontWeight: 600 }}
                >
                  Trang sau
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

export default ReviewQueue;
