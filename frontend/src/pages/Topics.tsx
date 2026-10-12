import React, { useState, useEffect } from 'react';
import { useDetail } from '../context/DetailContext';
import { Layers, CheckCircle2, Clock, XCircle, Filter, RotateCcw, Search } from 'lucide-react';

interface Topic {
  id: string;
  name: string;
  count: number;
}

interface DocumentItem {
  soHieu: string;
  loai: string;
  ngayKy: string;
  status: string;
  chuDe: string[];
}

const Topics: React.FC = () => {
  const { openDetail } = useDetail();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [nguon, setNguon] = useState('all');
  const [loai, setLoai] = useState('all');
  const [statusFilter, setStatusFilter] = useState('active'); // active (không gồm rejected), all, published, in_review, rejected
  const [page, setPage] = useState(1);
  const limit = 15;

  // Reset page khi filter thay đổi - phải đặt trước mọi early return
  useEffect(() => { setPage(1); }, [searchQuery, loai, statusFilter, selectedTopic, nguon]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setNguon('all');
    setLoai('all');
    setStatusFilter('active');
  };

  const hasActiveFilters = searchQuery !== '' || nguon !== 'all' || loai !== 'all' || statusFilter !== 'active';

  // Lấy danh sách các chủ đề ban đầu
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/topics')
      .then(res => res.json())
      .then(data => {
        setTopics(data.topics || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Lỗi khi tải chủ đề:", err);
        setLoading(false);
      });
  }, []);

  // Khi click vào chủ đề, fetch danh sách văn bản thuộc chủ đề đó
  useEffect(() => {
    if (!selectedTopic) {
      setSearchQuery('');
      setNguon('all');
      setLoai('all');
      setStatusFilter('active');
      return;
    }

    setDocuments([]);
    fetch(`http://localhost:8000/api/v1/topics/${selectedTopic}/documents`)
      .then(res => res.json())
      .then(data => {
        setDocuments(data.documents || []);
      })
      .catch(err => {
        console.error("Lỗi khi tải văn bản của chủ đề:", err);
      });
  }, [selectedTopic]);

  if (loading) {
    return (
      <section id="topics" style={{ padding: '20px' }}>
        <div className="wrap">
          <h2>Chủ đề văn bản</h2>
          <p className="sub">Đang tải...</p>
        </div>
      </section>
    );
  }

  const activeTopicName = topics.find(t => t.id === selectedTopic)?.name;

  const filteredDocuments = documents.filter(doc => {
    if (nguon !== 'all' && (doc.soHieu || '').toLowerCase().includes('bộ') === (nguon === 'trường')) {
      // logic giả lập: nếu nguồn bộ mà văn bản là của trường thì return false. Thực tế nên trả về theo thuộc tính `nguon`
      // Do data documentItem không có `nguon`, tạm coi số hiệu có BGDĐT là bộ
      const isBo = doc.soHieu.includes('BGDĐT') || doc.soHieu.includes('CP') || doc.soHieu.includes('QH');
      if (nguon === 'bộ' && !isBo) return false;
      if (nguon === 'trường' && isBo) return false;
    }
    if (loai !== 'all' && doc.loai !== loai) return false;
    if (statusFilter === 'active' && doc.status === 'rejected') return false;
    if (statusFilter !== 'active' && statusFilter !== 'all' && doc.status !== statusFilter) return false;

    if (!searchQuery) return true;
    const lowerQ = searchQuery.toLowerCase();
    return doc.soHieu.toLowerCase().includes(lowerQ) ||
      doc.loai.toLowerCase().includes(lowerQ) ||
      (doc.chuDe || []).some(cd => cd.toLowerCase().includes(lowerQ));
  });

  const uniqueLoais = Array.from(new Set(documents.map(d => d.loai).filter(Boolean))).sort();

  const pagedDocuments = filteredDocuments.slice((page - 1) * limit, page * limit);
  const totalPages = Math.ceil(filteredDocuments.length / limit) || 1;

  return (
    <section id="topics" style={{ background: 'var(--soft)', minHeight: '100vh', paddingBottom: '40px' }}>
      <div className="wrap" style={{ maxWidth: '1200px', margin: '0 auto', paddingTop: '32px' }}>

        {/* Tiêu đề trang */}
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--ink)' }}>Dashboard theo chủ đề</h2>
          <p className="sub" style={{ color: 'var(--muted)', marginTop: '4px' }}>
            Duyệt kho văn bản trực quan theo từng lĩnh vực chuyên môn (thay thế cho danh sách phẳng).
          </p>
        </div>

        {/* Lưới các thẻ chủ đề */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '16px',
          marginBottom: '32px'
        }}>
          {topics.map(topic => (
            <div
              key={topic.id}
              onClick={() => setSelectedTopic(topic.id === selectedTopic ? null : topic.id)}
              style={{
                background: topic.id === selectedTopic ? 'var(--blue)' : 'var(--card-bg)',
                color: topic.id === selectedTopic ? 'white' : 'var(--ink)',
                border: topic.id === selectedTopic ? '2px solid var(--blue)' : '2px solid var(--border)',
                borderRadius: '12px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: topic.id === selectedTopic ? '0 10px 25px -5px rgba(37, 99, 235, 0.4)' : '0 2px 5px rgba(0,0,0,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  background: topic.id === selectedTopic ? 'rgba(255,255,255,0.2)' : 'var(--app-bg)',
                  padding: '10px',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center'
                }}>
                  <Layers size={20} color={topic.id === selectedTopic ? 'white' : 'var(--blue)'} />
                </div>
                <span style={{ fontSize: '16px', fontWeight: 600 }}>{topic.name}</span>
              </div>
              <div style={{
                background: topic.id === selectedTopic ? 'rgba(255,255,255,0.2)' : 'var(--blue-50)',
                color: topic.id === selectedTopic ? 'white' : 'var(--blue)',
                padding: '4px 10px',
                borderRadius: '20px',
                fontSize: '14px',
                fontWeight: 700
              }}>
                {topic.count}
              </div>
            </div>
          ))}
        </div>

        {/* Danh sách văn bản khi một thẻ được chọn */}
        {selectedTopic && (
          <div style={{
            background: 'var(--card-bg)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid var(--border)',
            boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)'
          }}>
            <h3 style={{ fontSize: '18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Văn bản thuộc chủ đề <span style={{ color: 'var(--blue)' }}>{activeTopicName}</span>
            </h3>

            {/* Card Bộ lọc chủ đề */}
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
                  <span>Bộ lọc văn bản theo chủ đề</span>
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
                    id="topicTim"
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
                    placeholder="Lọc số hiệu, loại, từ khóa..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                {/* Nguồn */}
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
                    value={nguon}
                    onChange={(e) => setNguon(e.target.value)}
                  >
                    <option value="all">Mọi nguồn</option>
                    <option value="bộ">Bộ, CP, Quốc hội</option>
                    <option value="trường">Nội bộ Trường</option>
                  </select>
                </div>

                {/* Loại */}
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
                    value={loai}
                    onChange={(e) => setLoai(e.target.value)}
                  >
                    <option value="all">Mọi loại văn bản</option>
                    {uniqueLoais.map((l, i) => (
                      <option key={i} value={l}>{l}</option>
                    ))}
                  </select>
                </div>

                {/* Trạng thái */}
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
                    <option value="active">Ẩn mục từ chối</option>
                    <option value="all">Tất cả trạng thái</option>
                    <option value="published">Đã duyệt (Xuất bản)</option>
                    <option value="in_review">Chờ duyệt</option>
                    <option value="rejected">Bị từ chối</option>
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
                  Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{filteredDocuments.length}</b> / {documents.length} văn bản
                  {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
                </div>
                {hasActiveFilters && (
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {searchQuery && (
                      <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                        "{searchQuery}"
                      </span>
                    )}
                    {nguon !== 'all' && (
                      <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                        {nguon === 'bộ' ? 'Bộ / CP' : 'Trường'}
                      </span>
                    )}
                    {loai !== 'all' && (
                      <span style={{ background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                        {loai}
                      </span>
                    )}
                    {statusFilter !== 'active' && (
                      <span style={{ background: '#ecfdf5', color: '#047857', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                        {statusFilter === 'all' ? 'Tất cả' : statusFilter === 'published' ? 'Đã duyệt' : statusFilter === 'in_review' ? 'Chờ duyệt' : 'Bị từ chối'}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {documents.length === 0 ? (
              <p style={{ color: 'var(--muted)', textAlign: 'center', padding: '40px 0' }}>Đang tải danh sách...</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '50px 2fr 1fr 1fr 1fr',
                  gap: '16px',
                  padding: '12px 16px',
                  borderBottom: '2px solid var(--border)',
                  fontSize: '13px',
                  fontWeight: 700,
                  color: 'var(--muted)',
                  textTransform: 'uppercase'
                }}>
                  <span>#</span>
                  <span>Văn bản</span>
                  <span>Loại</span>
                  <span>Ngày ký</span>
                  <span>Trạng thái</span>
                </div>

                {filteredDocuments.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px 20px', background: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', margin: '16px 0' }}>
                    <p style={{ color: 'var(--muted)', fontSize: '15px', margin: '0 0 12px 0' }}>Không tìm thấy văn bản phù hợp với bộ lọc.</p>
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
                ) : (
                  <>
                    {pagedDocuments.map((doc, idx) => (
                    <div
                      key={idx}
                      onClick={() => openDetail(doc.soHieu)}
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '50px 2fr 1fr 1fr 1fr',
                        gap: '16px',
                        padding: '16px',
                        background: 'var(--app-bg)',
                        borderRadius: '8px',
                        alignItems: 'center',
                        cursor: 'pointer',
                        border: '1px solid transparent',
                        transition: '0.2s'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--blue-200)')}
                      onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'transparent')}
                    >
                      <span style={{ fontWeight: 600, color: 'var(--muted)' }}>{idx + 1}</span>
                      <span style={{ fontWeight: 600, color: 'var(--ink)' }}>{doc.soHieu}</span>
                      <span style={{ color: 'var(--muted)' }}>{doc.loai}</span>
                      <span style={{ color: 'var(--muted)' }}>{doc.ngayKy}</span>
                      <span>
                        {doc.status === 'published' ? (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'var(--green-50)', color: 'var(--green)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                            <CheckCircle2 size={14} /> Xuất bản
                          </span>
                        ) : doc.status === 'rejected' ? (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'var(--red-50)', color: 'var(--red)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                            <XCircle size={14} /> Bị từ chối
                          </span>
                        ) : (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'var(--amber-50)', color: 'var(--amber)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                            <Clock size={14} /> Chờ duyệt
                          </span>
                        )}
                      </span>
                    </div>
                    ))}

                    {filteredDocuments.length > 0 && (
                      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{ padding: '8px 16px', background: page === 1 ? '#e0e0e0' : 'var(--blue)', color: page === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: page === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang trước</button>
                        <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {page} / {totalPages}</span>
                        <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages} style={{ padding: '8px 16px', background: page >= totalPages ? '#e0e0e0' : 'var(--blue)', color: page >= totalPages ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: page >= totalPages ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang sau</button>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

export default Topics;
