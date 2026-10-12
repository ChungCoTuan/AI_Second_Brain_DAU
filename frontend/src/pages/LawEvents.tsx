import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Filter, RotateCcw, Search } from 'lucide-react';
import { useData } from '../context/DataContext';
import { badge, fmtDate, fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';

const LawEvents: React.FC = () => {
    const { openDetail } = useDetail();
    const { data, markAsRead, readEvents } = useData();
    const navigate = useNavigate();

    // Unified filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [filterType, setFilterType] = useState<'all' | 'thay_the' | 'bai_bo'>('all');
    const [filterYear, setFilterYear] = useState<string>('all');
    const [filterImpact, setFilterImpact] = useState<'all' | 'has_affected' | 'no_affected'>('all');

    const [pageEvents, setPageEvents] = useState(1);
    const [pageSK, setPageSK] = useState(1);
    const limit = 15;

    const events = useMemo(() => {
        return [...(data.events || [])].sort((a: any, b: any) => {
            const aUnread = !readEvents.includes(`${a.canCu}->${a.thayBang}`);
            const bUnread = !readEvents.includes(`${b.canCu}->${b.thayBang}`);
            if (aUnread && !bUnread) return -1;
            if (!aUnread && bUnread) return 1;
            return (b.docs?.length || 0) - (a.docs?.length || 0);
        });
    }, [data.events, readEvents]);

    const SK = useMemo(() => data.suKienHieuLuc || [], [data.suKienHieuLuc]);

    // Trích xuất danh sách các năm có trong sự kiện
    const availableYears = useMemo(() => {
        const yearsSet = new Set<string>();
        events.forEach((e: any) => {
            if (e.nam) yearsSet.add(e.nam);
            else {
                const m = (e.thayBang || '').match(/\b(20[0-2]\d)\b/);
                if (m) yearsSet.add(m[1]);
            }
        });
        SK.forEach((s: any) => {
            if (s.nam) yearsSet.add(s.nam);
            else {
                const m = (s.tuNgay || '').match(/\b(20[0-2]\d)\b/);
                if (m) yearsSet.add(m[1]);
            }
        });
        return Array.from(yearsSet).sort().reverse();
    }, [events, SK]);

    const q = fold(searchQuery);

    // Lọc sự kiện cảnh báo (events)
    const filteredEvents = useMemo(() => {
        return events.filter((e: any) => {
            // Lọc theo Loại sự kiện
            if (filterType === 'thay_the' && !(e.rawType === 'thay_the' || (e.lyDo && fold(e.lyDo).includes('thay the')))) {
                return false;
            }
            if (filterType === 'bai_bo' && !(e.rawType === 'bai_bo' || (e.lyDo && fold(e.lyDo).includes('bai bo')))) {
                return false;
            }

            // Lọc theo Năm
            if (filterYear !== 'all') {
                const y = e.nam || ((e.thayBang || '').match(/\b(20[0-2]\d)\b/) ? (e.thayBang || '').match(/\b(20[0-2]\d)\b/)[1] : '');
                if (y !== filterYear) return false;
            }

            // Lọc theo Mức độ ảnh hưởng
            if (filterImpact === 'has_affected' && (!e.docs || e.docs.length === 0)) return false;
            if (filterImpact === 'no_affected' && e.docs && e.docs.length > 0) return false;

            // Tìm kiếm tự do
            if (q) {
                const matchText = fold([
                    e.canCu || '',
                    e.thayBang || '',
                    e.lyDo || '',
                    ...(e.docs || []).map((d: any) => d.soHieu || '')
                ].join(' '));
                if (!matchText.includes(q)) return false;
            }

            return true;
        });
    }, [events, filterType, filterYear, filterImpact, q]);

    // Lọc chi tiết các lần đổi hiệu lực (suKienHieuLuc)
    const filteredSK = useMemo(() => {
        return SK.filter((s: any) => {
            // Lọc theo Loại sự kiện
            if (filterType === 'thay_the' && !(s.rawType === 'thay_the' || (s.lyDo && fold(s.lyDo).includes('thay the')))) {
                return false;
            }
            if (filterType === 'bai_bo' && !(s.rawType === 'bai_bo' || (s.lyDo && fold(s.lyDo).includes('bai bo')))) {
                return false;
            }

            // Lọc theo Năm
            if (filterYear !== 'all') {
                const y = s.nam || ((s.tuNgay || '').match(/\b(20[0-2]\d)\b/) ? (s.tuNgay || '').match(/\b(20[0-2]\d)\b/)[1] : '');
                if (y !== filterYear) return false;
            }

            // Lọc theo Mức độ ảnh hưởng
            if (filterImpact !== 'all') {
                const matchingEvt = events.find((e: any) => fold(e.canCu) === fold(s.cu) || fold(e.thayBang) === fold(s.moi));
                const hasAffected = matchingEvt && matchingEvt.docs && matchingEvt.docs.length > 0;
                if (filterImpact === 'has_affected' && !hasAffected) return false;
                if (filterImpact === 'no_affected' && hasAffected) return false;
            }

            // Tìm kiếm tự do
            if (q) {
                const matchText = fold([
                    s.cu || '',
                    s.tenCu || '',
                    s.moi || '',
                    s.tenMoi || '',
                    s.lyDo || '',
                    s.nguon || ''
                ].join(' '));
                if (!matchText.includes(q)) return false;
            }

            return true;
        });
    }, [SK, events, filterType, filterYear, filterImpact, q]);

    // Reset pagination on filter change
    useEffect(() => {
        setPageEvents(1);
        setPageSK(1);
    }, [searchQuery, filterType, filterYear, filterImpact]);

    const pagedEvents = filteredEvents.slice((pageEvents - 1) * limit, pageEvents * limit);
    const totalPagesEvents = Math.ceil(filteredEvents.length / limit) || 1;

    const pagedSK = filteredSK.slice((pageSK - 1) * limit, pageSK * limit);
    const totalPagesSK = Math.ceil(filteredSK.length / limit) || 1;

    const handleResetFilters = () => {
        setSearchQuery('');
        setFilterType('all');
        setFilterYear('all');
        setFilterImpact('all');
    };

    const hasActiveFilters = searchQuery !== '' || filterType !== 'all' || filterYear !== 'all' || filterImpact !== 'all';

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
        <section id="su-kien">
            <div className="wrap">
                <h2>Cảnh báo theo sự kiện thay đổi luật</h2>
                <p className="sub">
                    Mỗi thẻ là một lần luật thay đổi, kéo theo nhiều văn bản nội bộ. Bấm để lọc danh sách bên dưới (Chuyển sang
                    trang Rà soát).
                </p>

                {/* Unified Filter Bar */}
                <div
                    style={{
                        background: '#fff',
                        border: '1px solid var(--line, #e2e8f0)',
                        borderRadius: '12px',
                        padding: '16px 20px',
                        marginBottom: '24px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                    }}
                >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, color: 'var(--ink, #1e293b)', fontSize: '15px' }}>
                            <Filter size={18} style={{ color: 'var(--red, #b91c1c)' }} />
                            <span>Bộ lọc tra cứu sự kiện pháp lý</span>
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
                        {/* Search Input */}
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
                                placeholder="Tìm số hiệu, lý do, trích yếu..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        {/* Filter Type */}
                        <div>
                            <select
                                className="inp"
                                style={{
                                    width: '100%',
                                    height: '42px',
                                    padding: '0 28px 0 12px',
                                    fontSize: '14px',
                                    borderRadius: '8px',
                                    border: '1px solid var(--line, #cbd5e1)',
                                    background: '#fff',
                                    cursor: 'pointer',
                                    fontWeight: 500,
                                    boxSizing: 'border-box'
                                }}
                                value={filterType}
                                onChange={(e) => setFilterType(e.target.value as any)}
                            >
                                <option value="all">Tất cả loại sự kiện</option>
                                <option value="thay_the">Bị thay thế</option>
                                <option value="bai_bo">Bị bãi bỏ</option>
                            </select>
                        </div>

                        {/* Filter Year */}
                        <div>
                            <select
                                className="inp"
                                style={{
                                    width: '100%',
                                    height: '42px',
                                    padding: '0 28px 0 12px',
                                    fontSize: '14px',
                                    borderRadius: '8px',
                                    border: '1px solid var(--line, #cbd5e1)',
                                    background: '#fff',
                                    cursor: 'pointer',
                                    fontWeight: 500,
                                    boxSizing: 'border-box'
                                }}
                                value={filterYear}
                                onChange={(e) => setFilterYear(e.target.value)}
                            >
                                <option value="all">Tất cả các năm</option>
                                {availableYears.map((y) => (
                                    <option key={y} value={y}>Năm {y}</option>
                                ))}
                            </select>
                        </div>

                        {/* Filter Impact */}
                        <div>
                            <select
                                className="inp"
                                style={{
                                    width: '100%',
                                    height: '42px',
                                    padding: '0 28px 0 12px',
                                    fontSize: '14px',
                                    borderRadius: '8px',
                                    border: '1px solid var(--line, #cbd5e1)',
                                    background: '#fff',
                                    cursor: 'pointer',
                                    fontWeight: 500,
                                    boxSizing: 'border-box'
                                }}
                                value={filterImpact}
                                onChange={(e) => setFilterImpact(e.target.value as any)}
                            >
                                <option value="all">Tất cả mức độ ảnh hưởng</option>
                                <option value="has_affected">Có văn bản nội bộ bị ảnh hưởng</option>
                                <option value="no_affected">Chưa có văn bản nội bộ ảnh hưởng</option>
                            </select>
                        </div>
                    </div>

                    {/* Filter Counters */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '14px', fontSize: '13px', color: 'var(--muted, #64748b)', flexWrap: 'wrap' }}>
                        <span>Đang hiển thị: <b>{filteredEvents.length}</b>/{events.length} thẻ sự kiện</span>
                        <span>•</span>
                        <span><b>{filteredSK.length}</b>/{SK.length} lần đổi hiệu lực chi tiết</span>
                    </div>
                </div>

                {/* Section 1: Event Cards */}
                <div className="events">
                    {filteredEvents.length > 0 ? (
                        pagedEvents.map((e: any) => {
                            const eid = `${e.canCu}->${e.thayBang}`;
                            const isUnread = !readEvents.includes(eid);
                            const globalIdx = events.findIndex((evt: any) => evt.canCu === e.canCu && evt.thayBang === e.thayBang);
                            const hasDocs = e.docs && e.docs.length > 0;
                            return (
                                <div
                                    key={eid}
                                    className={`ev ${isUnread ? 'unread-item' : ''}`}
                                    onClick={() => {
                                        markAsRead('event', eid);
                                        navigate(`/review?event=${globalIdx}`);
                                    }}
                                >
                                    <div className="n" style={{ color: hasDocs ? 'var(--red, #b91c1c)' : 'var(--muted, #64748b)' }}>
                                        {e.docs.length}{' '}
                                        <span style={{ fontSize: '13px', fontWeight: hasDocs ? 700 : 500 }}>
                                            {hasDocs ? 'văn bản bị ảnh hưởng' : 'văn bản ảnh hưởng'}
                                        </span>
                                    </div>
                                    <div className="chain">
                                        <span className="old" style={{ color: 'var(--red, #b91c1c)' }} title={e.canCu}>
                                            {hl(e.canCu, q)}
                                        </span>{' '}
                                        <span className="arrow">→</span>{' '}
                                        <span className="new" style={{ color: 'var(--green, #15803d)' }} title={e.thayBang}>
                                            {hl(e.thayBang, q)}
                                        </span>
                                    </div>
                                    <span className={`pill ${badge(e.lyDo)}`}>{e.lyDo}</span>
                                </div>
                            );
                        })
                    ) : (
                        <div className="empty" style={{ gridColumn: '1 / -1', padding: '32px 0', textAlign: 'center', color: 'var(--muted)' }}>
                            Không có sự kiện thay đổi luật nào khớp với bộ lọc.
                        </div>
                    )}
                </div>

                {filteredEvents.length > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                        <button
                            onClick={() => setPageEvents((p) => Math.max(1, p - 1))}
                            disabled={pageEvents === 1}
                            style={{
                                padding: '8px 16px',
                                background: pageEvents === 1 ? '#e0e0e0' : 'var(--blue)',
                                color: pageEvents === 1 ? '#888' : '#fff',
                                border: 'none',
                                borderRadius: '8px',
                                cursor: pageEvents === 1 ? 'not-allowed' : 'pointer',
                                fontWeight: 600
                            }}
                        >
                            Trang trước
                        </button>
                        <span style={{ fontWeight: 600, color: 'var(--text)' }}>
                            Trang {pageEvents} / {totalPagesEvents}
                        </span>
                        <button
                            onClick={() => setPageEvents((p) => p + 1)}
                            disabled={pageEvents >= totalPagesEvents}
                            style={{
                                padding: '8px 16px',
                                background: pageEvents >= totalPagesEvents ? '#e0e0e0' : 'var(--blue)',
                                color: pageEvents >= totalPagesEvents ? '#888' : '#fff',
                                border: 'none',
                                borderRadius: '8px',
                                cursor: pageEvents >= totalPagesEvents ? 'not-allowed' : 'pointer',
                                fontWeight: 600
                            }}
                        >
                            Trang sau
                        </button>
                    </div>
                )}

                {/* Section 2: Detailed Validity Changes */}
                <h2 id="doi-hieu-luc" style={{ marginTop: '36px', scrollMarginTop: '112px' }}>
                    Mọi lần đổi hiệu lực mà kho biết
                </h2>
                <p className="sub">
                    Bóc từ chính điều khoản thi hành của các văn bản Bộ, mỗi dòng kèm nguyên văn. Nhiều văn bản 2026 dùng chữ{' '}
                    <b>hết hiệu lực thi hành</b> chứ không dùng <b>thay thế</b> hay <b>bãi bỏ</b>, nên tra theo hai từ khoá quen
                    thuộc sẽ bỏ sót.
                </p>

                <div className="rlist">
                    {filteredSK.length > 0 ? (
                        <>
                            {pagedSK.map((s: any, idx: number) => (
                                <div
                                    key={idx}
                                    className="r r-sk"
                                    onClick={() => openDetail('bo:' + (s.docId || s.moi))}
                                >
                                    <div>
                                        <span className="rs" style={{ color: 'var(--red)' }}>
                                            {hl(s.cu || '(không nêu số hiệu)', q)}
                                        </span>
                                        <div className="rm">{hl(s.tenCu || '', q)}</div>
                                    </div>
                                    <div>
                                        <div className="rt">
                                            {s.lyDo} bởi <b style={{ color: 'var(--green)' }}>{hl(s.moi, q)}</b>
                                            {s.phamVi && s.phamVi !== 'toàn bộ' && (
                                                <span className="tag2 dai"> phạm vi: {s.phamVi}</span>
                                            )}
                                        </div>
                                        {bangChung(s.nguon)}
                                    </div>
                                    <div className="rr">{s.tuNgay ? fmtDate(s.tuNgay) : ''}</div>
                                </div>
                            ))}

                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                                <button
                                    onClick={() => setPageSK((p) => Math.max(1, p - 1))}
                                    disabled={pageSK === 1}
                                    style={{
                                        padding: '8px 16px',
                                        background: pageSK === 1 ? '#e0e0e0' : 'var(--blue)',
                                        color: pageSK === 1 ? '#888' : '#fff',
                                        border: 'none',
                                        borderRadius: '8px',
                                        cursor: pageSK === 1 ? 'not-allowed' : 'pointer',
                                        fontWeight: 600
                                    }}
                                >
                                    Trang trước
                                </button>
                                <span style={{ fontWeight: 600, color: 'var(--text)' }}>
                                    Trang {pageSK} / {totalPagesSK}
                                </span>
                                <button
                                    onClick={() => setPageSK((p) => p + 1)}
                                    disabled={pageSK >= totalPagesSK}
                                    style={{
                                        padding: '8px 16px',
                                        background: pageSK >= totalPagesSK ? '#e0e0e0' : 'var(--blue)',
                                        color: pageSK >= totalPagesSK ? '#888' : '#fff',
                                        border: 'none',
                                        borderRadius: '8px',
                                        cursor: pageSK >= totalPagesSK ? 'not-allowed' : 'pointer',
                                        fontWeight: 600
                                    }}
                                >
                                    Trang sau
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="empty">Không có lần đổi hiệu lực nào khớp với bộ lọc.</div>
                    )}
                </div>
            </div>
        </section>
    );
};

export default LawEvents;
