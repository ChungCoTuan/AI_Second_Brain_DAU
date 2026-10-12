import React, { useState, useMemo, useEffect } from 'react';
import { useData } from '../context/DataContext';
import { fold, hl, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';
import { Filter, RotateCcw, Search } from 'lucide-react';

const Thresholds: React.FC = () => {
    const { openDetail } = useDetail();
    const { data, loading, markAsRead, readThresholds } = useData();

    const CS = useMemo(() => {
        return [...(data.conSoChot || [])].sort((a: any, b: any) => {
            const aUnread = !readThresholds.includes(a.vb);
            const bUnread = !readThresholds.includes(b.vb);
            if (aUnread && !bUnread) return -1;
            if (!aUnread && bUnread) return 1;
            return 0;
        });
    }, [data.conSoChot, readThresholds]);

    // State bộ lọc
    const [searchTerm, setSearchTerm] = useState('');
    const [vb, setVb] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all'); // all, valid, dead
    const [sourceMatchFilter, setSourceMatchFilter] = useState('all'); // all, verified, unverified

    const [page, setPage] = useState(1);
    const limit = 15;

    const vbs = useMemo(() => Array.from(new Set(CS.map((c: any) => c.vb))).sort(), [CS]);

    useEffect(() => {
        setPage(1);
    }, [searchTerm, vb, statusFilter, sourceMatchFilter]);

    const handleResetFilters = () => {
        setSearchTerm('');
        setVb('all');
        setStatusFilter('all');
        setSourceMatchFilter('all');
    };

    const hasActiveFilters =
        searchTerm !== '' ||
        vb !== 'all' ||
        statusFilter !== 'all' ||
        sourceMatchFilter !== 'all';

    const q = fold(searchTerm.trim());
    const kq = useMemo(() => {
        return CS.filter((c: any) => {
            if (vb !== 'all' && c.vb !== vb) return false;

            // Trạng thái hiệu lực văn bản
            if (statusFilter === 'valid' && c.vbDaChet) return false;
            if (statusFilter === 'dead' && !c.vbDaChet) return false;

            // Trạng thái kiểm chứng nguồn số
            if (sourceMatchFilter === 'verified' && c.nguonDoSo === false) return false;
            if (sourceMatchFilter === 'unverified' && c.nguonDoSo !== false) return false;

            if (!q) return true;
            return fold([c.giaTri, c.yNghia, c.vb, c.dieu].join(' ')).includes(q);
        });
    }, [CS, vb, statusFilter, sourceMatchFilter, q]);

    const show = kq.slice((page - 1) * limit, page * limit);
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
        <section id="nguong" style={{ background: 'var(--soft)' }}>
            <div className="wrap">
                <h2>Sổ tra ngưỡng & Định mức {loading && <span style={{ fontSize: '14px', color: '#888' }}>(Đang tải...)</span>}</h2>
                <p className="sub">Tra cứu nhanh các con số, tỷ lệ, thời hạn, định mức bắt buộc.</p>

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
                            <span>Bộ lọc tra cứu ngưỡng & định mức bắt buộc</span>
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
                                id="csTim"
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
                                placeholder="Lọc: 100%, 2 tỷ, tuyển sinh, 15 ngày..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        {/* Văn bản */}
                        <div>
                            <select
                                id="csVb"
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

                        {/* Trạng thái hiệu lực VB */}
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

                        {/* Kiểm chứng nguồn số */}
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
                                value={sourceMatchFilter}
                                onChange={(e) => setSourceMatchFilter(e.target.value)}
                            >
                                <option value="all">Tất cả nguồn bóc tách</option>
                                <option value="verified">Khớp trong nguyên văn câu</option>
                                <option value="unverified">Nghi vấn (chưa khớp nguyên văn)</option>
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
                            Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{kq.length}</b> / {CS.length} con số
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
                                {statusFilter !== 'all' && (
                                    <span style={{ background: statusFilter === 'dead' ? '#fee2e2' : '#ecfdf5', color: statusFilter === 'dead' ? '#b91c1c' : '#047857', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                                        {statusFilter === 'dead' ? 'VB đã hết hiệu lực' : 'VB còn hiệu lực'}
                                    </span>
                                )}
                                {sourceMatchFilter !== 'all' && (
                                    <span style={{ background: '#fef3c7', color: '#92400e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                                        {sourceMatchFilter === 'verified' ? 'Khớp nguyên văn' : 'Nghi vấn số'}
                                    </span>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                <div className="rlist" id="csList">
                    {show.length > 0 ? (
                        show.map((c: any, idx: number) => {
                            const isUnread = !readThresholds.includes(c.vb);
                            return (
                                <div
                                    key={idx}
                                    className={`r r-cs ${isUnread ? 'unread-item' : ''}`}
                                    onClick={() => {
                                        openDetail('bo:' + (c.docId || c.vb));
                                        markAsRead('threshold', c.vb);
                                    }}
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
                            )
                        })
                    ) : (
                        <div style={{ padding: '40px 20px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', margin: '16px 0' }}>
                            <p style={{ color: 'var(--muted)', fontSize: '15px', margin: '0 0 12px 0' }}>Không có con số nào khớp với điều kiện lọc.</p>
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

export default Thresholds;
