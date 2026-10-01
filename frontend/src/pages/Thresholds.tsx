import React, { useState } from 'react';
import { useData } from '../context/DataContext';
import { fold, hl, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';

const Thresholds: React.FC = () => {
    const { openDetail } = useDetail();
    const { data, loading, markAsRead, readThresholds } = useData();
    const CS = [...(data.conSoChot || [])].sort((a: any, b: any) => {
        const aUnread = !readThresholds.includes(a.vb);
        const bUnread = !readThresholds.includes(b.vb);
        if (aUnread && !bUnread) return -1;
        if (!aUnread && bUnread) return 1;
        return 0;
    });
    const [searchTerm, setSearchTerm] = useState('');
    const [vb, setVb] = useState('all');

    const vbs = Array.from(new Set(CS.map((c: any) => c.vb))).sort();

    const q = fold(searchTerm);
    const kq = CS.filter((c: any) => {
        if (vb !== 'all' && c.vb !== vb) return false;
        if (!q) return true;
        return fold([c.giaTri, c.yNghia, c.vb, c.dieu].join(' ')).includes(q);
    });

    const [page, setPage] = useState(1);
    const limit = 15;
    const show = kq.slice((page - 1) * limit, page * limit);
    const totalPages = Math.ceil(kq.length / limit) || 1;
    React.useEffect(() => { setPage(1); }, [searchTerm, vb]);

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

                <div className="srow">
                    <input
                        id="csTim"
                        className="inp"
                        type="search"
                        placeholder="Lọc: 100%, 2 ty, tuyen sinh, 15 ngay, dien tich"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <select id="csVb" className="sel" value={vb} onChange={(e) => setVb(e.target.value)}>
                        <option value="all">Mọi văn bản</option>
                        {vbs.map((v: any) => (
                            <option key={v} value={v}>
                                {v}
                            </option>
                        ))}
                    </select>
                    <span className="cnt" id="csCnt">
                        <b>{kq.length}</b> / {CS.length} con số
                    </span>
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
                        <div className="empty">Không có con số nào khớp.</div>
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
