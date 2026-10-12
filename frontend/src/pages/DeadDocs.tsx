import React, { useState, useMemo, useEffect } from 'react';
import { useData } from '../context/DataContext';
import { fmtDate, fold } from '../utils';
import { useDetail } from '../context/DetailContext';
import { Filter, RotateCcw, Search } from 'lucide-react';

const DeadDocs: React.FC = () => {
    const { openDetail } = useDetail();
    const [expandedDocs, setExpandedDocs] = useState<Record<string, boolean>>({});
    const { data, markAsRead, readDeadDocs } = useData();

    // 1. Phân loại danh sách gốc
    const rows = useMemo(() => {
        return [...(data.vbTuChet || [])].sort((a: any, b: any) => {
            const aUnread = !readDeadDocs.includes(a.soHieu);
            const bUnread = !readDeadDocs.includes(b.soHieu);
            if (aUnread && !bUnread) return -1;
            if (!aUnread && bUnread) return 1;
            return 0;
        });
    }, [data.vbTuChet, readDeadDocs]);

    const sap = useMemo(() => {
        return [...(data.vbSapChet || [])].sort((a: any, b: any) => {
            const aUnread = !readDeadDocs.includes(a.soHieu);
            const bUnread = !readDeadDocs.includes(b.soHieu);
            if (aUnread && !bUnread) return -1;
            if (!aUnread && bUnread) return 1;
            return 0;
        });
    }, [data.vbSapChet, readDeadDocs]);

    // 2. State bộ lọc
    const [searchTerm, setSearchTerm] = useState('');
    const [filterForm, setFilterForm] = useState('all'); // all, thay_the, bai_bo_mot_phan, bai_bo_toan_bo
    const [filterLoai, setFilterLoai] = useState('all');
    const [filterCoQuan, setFilterCoQuan] = useState('all');
    const [filterYear, setFilterYear] = useState('all');

    const [pageRows, setPageRows] = useState(1);
    const [pageSap, setPageSap] = useState(1);
    const limit = 15;

    // 3. Tùy chọn động từ dữ liệu
    const allDocsCombined = useMemo(() => [...rows, ...sap], [rows, sap]);

    const availableTypes = useMemo(() => {
        const types = new Set<string>();
        allDocsCombined.forEach((r: any) => {
            if (r.loai && r.loai.trim()) types.add(r.loai.trim());
        });
        return Array.from(types).sort();
    }, [allDocsCombined]);

    const availableAgencies = useMemo(() => {
        const agencies = new Set<string>();
        allDocsCombined.forEach((r: any) => {
            if (r.coQuan && r.coQuan.trim()) agencies.add(r.coQuan.trim());
        });
        return Array.from(agencies).sort();
    }, [allDocsCombined]);

    const availableYears = useMemo(() => {
        const years = new Set<string>();
        allDocsCombined.forEach((r: any) => {
            const y = r.nam || (r.tuNgay ? (r.tuNgay.match(/\b(20[0-2]\d)\b/) ? r.tuNgay.match(/\b(20[0-2]\d)\b/)[1] : '') : '');
            if (y && /^\d{4}$/.test(y)) years.add(y);
        });
        return Array.from(years).sort().reverse();
    }, [allDocsCombined]);

    // 4. Reset phân trang khi đổi bộ lọc
    useEffect(() => {
        setPageRows(1);
        setPageSap(1);
    }, [searchTerm, filterForm, filterLoai, filterCoQuan, filterYear]);

    const handleResetFilters = () => {
        setSearchTerm('');
        setFilterForm('all');
        setFilterLoai('all');
        setFilterCoQuan('all');
        setFilterYear('all');
    };

    const hasActiveFilters =
        searchTerm !== '' ||
        filterForm !== 'all' ||
        filterLoai !== 'all' ||
        filterCoQuan !== 'all' ||
        filterYear !== 'all';

    // 5. Predicate lọc dữ liệu
    const filterDocPredicate = (r: any) => {
        // Lọc hình thức
        if (filterForm !== 'all') {
            const isPartial = r.phamVi === 'một phần' || fold(r.lyDo || '').includes('mot phan');
            if (filterForm === 'thay_the') {
                const isThayThe = r.rawType === 'thay_the' || fold(r.lyDo || '').includes('thay the');
                if (!isThayThe) return false;
            } else if (filterForm === 'bai_bo_mot_phan') {
                if (!isPartial) return false;
            } else if (filterForm === 'bai_bo_toan_bo') {
                const isBaiBo = r.rawType === 'bai_bo' || fold(r.lyDo || '').includes('bai bo');
                if (!isBaiBo || isPartial) return false;
            }
        }

        // Lọc loại văn bản
        if (filterLoai !== 'all') {
            if ((r.loai || '').trim() !== filterLoai) return false;
        }

        // Lọc cơ quan
        if (filterCoQuan !== 'all') {
            if ((r.coQuan || '').trim() !== filterCoQuan) return false;
        }

        // Lọc năm
        if (filterYear !== 'all') {
            const y = r.nam || (r.tuNgay ? (r.tuNgay.match(/\b(20[0-2]\d)\b/) ? r.tuNgay.match(/\b(20[0-2]\d)\b/)[1] : '') : '');
            if (y !== filterYear) return false;
        }

        // Tìm kiếm tự do
        if (searchTerm.trim()) {
            const q = fold(searchTerm.trim());
            const matchText = fold([
                r.soHieu || '',
                r.loai || '',
                r.coQuan || '',
                r.lyDo || '',
                (r.thayBang || []).join(' '),
                r.nguyenVan || '',
                r.phamVi || ''
            ].join(' '));
            if (!matchText.includes(q)) return false;
        }

        return true;
    };

    const filteredRows = useMemo(() => rows.filter(filterDocPredicate), [rows, filterForm, filterLoai, filterCoQuan, filterYear, searchTerm]);
    const filteredSap = useMemo(() => sap.filter(filterDocPredicate), [sap, filterForm, filterLoai, filterCoQuan, filterYear, searchTerm]);

    const pagedRows = filteredRows.slice((pageRows - 1) * limit, pageRows * limit);
    const pagedSap = filteredSap.slice((pageSap - 1) * limit, pageSap * limit);
    const totalPagesRows = Math.ceil(filteredRows.length / limit) || 1;
    const totalPagesSap = Math.ceil(filteredSap.length / limit) || 1;

    // Early return khi kho văn bản hoàn toàn rỗng
    if (!rows.length && !sap.length) {
        return (
            <section id="khai-tu" style={{ background: 'var(--soft)' }}>
                <div className="wrap">
                    <h2>Chính văn bản đã bị khai tử</h2>
                    <p className="sub">Không phát hiện văn bản nào trong kho đã hết hiệu lực.</p>
                </div>
            </section>
        );
    }

    const renderDoc = (r: any, sapToi: boolean) => {
        const con = sapToi
            ? Math.round((Date.parse(r.tuNgay + 'T00:00:00Z') - Date.parse('2026-08-19T00:00:00Z')) / 86400000)
            : 0;

        const toggleExpand = (e: React.MouseEvent) => {
            e.stopPropagation();
            setExpandedDocs(prev => ({ ...prev, [r.docId]: !prev[r.docId] }));
        };

        const isUnread = !readDeadDocs.includes(r.docId);

        return (
            <div
                key={r.docId}
                className={`r ${isUnread ? 'unread-item' : ''}`}
                data-did={r.docId}
                onClick={() => {
                    markAsRead('dead', r.docId);
                    openDetail(r.docId);
                }}
            >
                <div>
                    <span className="rs">{r.soHieu}</span>
                    <div className="rm" style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap', marginTop: '2px' }}>
                        <span style={{ fontWeight: 600, color: 'var(--ink)' }}>{r.loai || 'Văn bản'}</span>
                        {r.coQuan && (
                            <>
                                <span>·</span>
                                <span style={{ color: 'var(--muted, #64748b)' }}>{r.coQuan}</span>
                            </>
                        )}
                        {r.nam && (
                            <>
                                <span>·</span>
                                <span style={{ color: 'var(--muted, #64748b)' }}>{r.nam}</span>
                            </>
                        )}
                    </div>
                </div>
                <div>
                    <div className="rt" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                        <div>
                            {r.lyDo} bởi <b style={{ color: 'var(--green)' }}>{(r.thayBang || []).join(', ')}</b>, từ {fmtDate(r.tuNgay)}
                            {sapToi && <span className="dleft gan" style={{ marginLeft: '8px' }}>còn {con} ngày, HIỆN VẪN CÒN HIỆU LỰC</span>}
                        </div>

                        <span
                            onClick={toggleExpand}
                            style={{ color: 'var(--primary)', cursor: 'pointer', fontSize: '13px', fontWeight: 600, marginTop: '6px' }}
                        >
                            {expandedDocs[r.docId] ? 'Ẩn nguyên văn' : 'Xem nguyên văn'}
                        </span>

                        {expandedDocs[r.docId] && (
                            <div style={{
                                marginTop: '12px', padding: '12px 16px', background: 'var(--soft)',
                                borderLeft: '3px solid var(--red)', borderRadius: '0 8px 8px 0', fontSize: '14px', width: '100%'
                            }}>
                                <div style={{ fontWeight: 600, fontSize: '11px', color: 'var(--red)', marginBottom: '4px' }}>NGUYÊN VĂN ĐIỀU KHOẢN</div>
                                <div style={{ color: 'var(--ink)' }}>{r.nguyenVan || `Văn bản này ${r.lyDo.toLowerCase()} ${(r.thayBang || []).join(', ')} theo quy định hiện hành.`}</div>
                            </div>
                        )}
                    </div>
                    {r.phamVi && r.phamVi !== 'toàn bộ' && (
                        <div className="rm" style={{ color: 'var(--amber)' }}>
                            phạm vi: {r.phamVi}
                        </div>
                    )}
                    {r.chuyenTiep && r.chuyenTiep.length > 0 && (
                        <div className="rm">
                            Có {r.chuyenTiep.length} điều khoản chuyển tiếp:{' '}
                            {r.chuyenTiep.map((c: any) => `${c.vb} ${c.dieu || ''}`).join('; ')}
                        </div>
                    )}
                </div>
                <div className="rr">
                    bấm xem
                    <br />
                    chi tiết
                </div>
            </div>
        );
    };

    return (
        <section id="khai-tu" style={{ background: 'var(--soft)' }}>
            <div className="wrap">
                <h2>Chính văn bản đã bị khai tử</h2>
                <p className="sub">
                    Nặng hơn một bậc so với mục trên. Ở trên là văn bản <b>viện dẫn</b> căn cứ đã chết. Ở đây là{' '}
                    <b>bản thân văn bản</b> đã hết hiệu lực, nên mọi điều khoản đang trích từ nó đều không còn giá trị. Phát hiện
                    được nhờ đối chiếu với đợt thông tư mới của Bộ.
                </p>

                <div id="tuChetBox">
                    <div className="alert">
                        <b>{rows.length} văn bản</b> trong kho đã hết hiệu lực
                        {sap.length > 0 ? `, thêm <b>${sap.length}</b> văn bản sẽ hết hiệu lực trong thời gian tới` : ''}. Trang
                        này trước đây chỉ báo được rằng chúng <b>viện dẫn</b> căn cứ đã chết. Nay đối chiếu với đợt văn bản mới cho
                        thấy chính chúng cũng đã bị thay. Điều khoản trích từ chúng <b>không còn là căn cứ để ban hành mới</b>,
                        nhưng phần lớn văn bản thay thế có <b>điều khoản chuyển tiếp</b> cho phép áp dụng tiếp với khoá tuyển sinh
                        hoặc hồ sơ đã có.
                    </div>

                    {/* Bộ lọc văn bản hết hiệu lực */}
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
                                <span>Bộ lọc tra cứu văn bản hết hiệu lực</span>
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
                                    id="deadTim"
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
                                    placeholder="Tìm số hiệu, thay thế, trích yếu..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>

                            {/* Lọc Hình thức hết hiệu lực */}
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
                                    value={filterForm}
                                    onChange={(e) => setFilterForm(e.target.value)}
                                >
                                    <option value="all">Tất cả hình thức</option>
                                    <option value="thay_the">Bị thay thế</option>
                                    <option value="bai_bo_mot_phan">Bãi bỏ một phần</option>
                                    <option value="bai_bo_toan_bo">Bãi bỏ toàn bộ</option>
                                </select>
                            </div>

                            {/* Lọc Loại văn bản */}
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

                            {/* Lọc Cơ quan ban hành */}
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
                                    value={filterCoQuan}
                                    onChange={(e) => setFilterCoQuan(e.target.value)}
                                >
                                    <option value="all">Tất cả cơ quan</option>
                                    {availableAgencies.map((cq) => (
                                        <option key={cq} value={cq}>
                                            {cq}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Lọc Năm */}
                            {availableYears.length > 0 && (
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
                                        value={filterYear}
                                        onChange={(e) => setFilterYear(e.target.value)}
                                    >
                                        <option value="all">Tất cả các năm</option>
                                        {availableYears.map((y) => (
                                            <option key={y} value={y}>
                                                Năm {y}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}
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
                                Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{filteredRows.length + filteredSap.length}</b> / {rows.length + sap.length} văn bản
                                {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
                            </div>
                            {hasActiveFilters && (
                                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                                    {searchTerm && (
                                        <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                                            "{searchTerm}"
                                        </span>
                                    )}
                                    {filterForm !== 'all' && (
                                        <span style={{ background: '#fef3c7', color: '#92400e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                                            {filterForm === 'thay_the' ? 'Bị thay thế' : filterForm === 'bai_bo_mot_phan' ? 'Bãi bỏ một phần' : 'Bãi bỏ toàn bộ'}
                                        </span>
                                    )}
                                    {filterLoai !== 'all' && (
                                        <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                                            {filterLoai}
                                        </span>
                                    )}
                                    {filterCoQuan !== 'all' && (
                                        <span style={{ background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                                            {filterCoQuan}
                                        </span>
                                    )}
                                    {filterYear !== 'all' && (
                                        <span style={{ background: '#ecfdf5', color: '#047857', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                                            Năm {filterYear}
                                        </span>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Danh sách văn bản đã hết hiệu lực */}
                    <div className="rlist">{pagedRows.map((r: any) => renderDoc(r, false))}</div>

                    {/* Empty state khi không khớp kết quả nào */}
                    {filteredRows.length === 0 && filteredSap.length === 0 && (
                        <div
                            style={{
                                textAlign: 'center',
                                padding: '40px 20px',
                                background: '#fff',
                                borderRadius: '12px',
                                border: '1px dashed var(--line, #cbd5e1)',
                                marginTop: '16px'
                            }}
                        >
                            <p style={{ color: 'var(--muted, #64748b)', fontSize: '15px', margin: '0 0 12px 0' }}>
                                Không tìm thấy văn bản hết hiệu lực nào khớp với điều kiện lọc hiện tại.
                            </p>
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

                    {filteredRows.length > 0 && (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                            <button onClick={() => setPageRows(p => Math.max(1, p - 1))} disabled={pageRows === 1} style={{ padding: '8px 16px', background: pageRows === 1 ? '#e0e0e0' : 'var(--blue)', color: pageRows === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageRows === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang trước</button>
                            <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {pageRows} / {totalPagesRows}</span>
                            <button onClick={() => setPageRows(p => p + 1)} disabled={pageRows >= totalPagesRows} style={{ padding: '8px 16px', background: pageRows >= totalPagesRows ? '#e0e0e0' : 'var(--blue)', color: pageRows >= totalPagesRows ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageRows >= totalPagesRows ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang sau</button>
                        </div>
                    )}

                    {filteredSap.length > 0 && (
                        <>
                            <div className="sec-t" style={{ marginTop: '20px', textTransform: 'uppercase' }}>
                                Sắp hết hiệu lực, hiện vẫn còn giá trị
                            </div>
                            <div className="rlist">{pagedSap.map((r: any) => renderDoc(r, true))}</div>
                            {filteredSap.length > 0 && (
                                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                                    <button onClick={() => setPageSap(p => Math.max(1, p - 1))} disabled={pageSap === 1} style={{ padding: '8px 16px', background: pageSap === 1 ? '#e0e0e0' : 'var(--blue)', color: pageSap === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageSap === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang trước</button>
                                    <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {pageSap} / {totalPagesSap}</span>
                                    <button onClick={() => setPageSap(p => p + 1)} disabled={pageSap >= totalPagesSap} style={{ padding: '8px 16px', background: pageSap >= totalPagesSap ? '#e0e0e0' : 'var(--blue)', color: pageSap >= totalPagesSap ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageSap >= totalPagesSap ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang sau</button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </section>
    );
};

export default DeadDocs;
