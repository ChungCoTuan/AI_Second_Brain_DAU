import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { badge, fmtDate, fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';

const LawEvents: React.FC = () => {
    const { openDetail } = useDetail();
    const { data, markAsRead, readEvents } = useData();
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [searchEvents, setSearchEvents] = useState('');
    const [pageEvents, setPageEvents] = useState(1);
    const [pageSK, setPageSK] = useState(1);
    const limit = 15;

    const events = [...(data.events || [])].sort((a: any, b: any) => {
        const aUnread = !readEvents.includes(`${a.canCu}->${a.thayBang}`);
        const bUnread = !readEvents.includes(`${b.canCu}->${b.thayBang}`);
        if (aUnread && !bUnread) return -1;
        if (!aUnread && bUnread) return 1;
        return 0;
    });
    const qE = fold(searchEvents);
    const filteredEvents = events.filter((e: any) => {
        if (!qE) return true;
        return fold([e.canCu, e.thayBang, e.lyDo].join(' ')).includes(qE);
    });
    const pagedEvents = filteredEvents.slice((pageEvents - 1) * limit, pageEvents * limit);
    const totalPagesEvents = Math.ceil(filteredEvents.length / limit) || 1;
    React.useEffect(() => setPageEvents(1), [searchEvents]);

    const SK = data.suKienHieuLuc || [];

    const q = fold(searchTerm);
    const filteredSK = SK.filter((s: any) => {
        if (!q) return true;
        return fold([s.cu, s.tenCu, s.moi, s.tenMoi, s.lyDo].join(' ')).includes(q);
    });
    const pagedSK = filteredSK.slice((pageSK - 1) * limit, pageSK * limit);
    const totalPagesSK = Math.ceil(filteredSK.length / limit) || 1;
    React.useEffect(() => setPageSK(1), [searchTerm]);

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

                <div className="srow" style={{ marginBottom: '16px' }}>
                    <input
                        id="evTim"
                        className="inp"
                        type="search"
                        placeholder="Lọc sự kiện: số hiệu, lý do..."
                        value={searchEvents}
                        onChange={(e) => setSearchEvents(e.target.value)}
                    />
                    <span className="cnt"><b>{filteredEvents.length}</b> / {events.length} sự kiện</span>
                </div>

                <div className="events">
                    {pagedEvents.map((e: any) => {
                        const eid = `${e.canCu}->${e.thayBang}`;
                        const isUnread = !readEvents.includes(eid);
                        const globalIdx = events.findIndex((evt: any) => evt.canCu === e.canCu && evt.thayBang === e.thayBang);
                        return (
                            <div
                                key={eid}
                                className={`ev ${isUnread ? 'unread-item' : ''}`}
                                onClick={() => {
                                    markAsRead('event', eid);
                                    navigate(`/review?event=${globalIdx}`);
                                }}
                            >
                                <div className="n">
                                    {e.docs.length} <span style={{ fontSize: '13px', color: 'var(--muted)', fontWeight: 600 }}>văn bản</span>
                                </div>
                                <div className="chain">
                                    <span className="old">{e.canCu}</span> <span className="arrow">→</span>{' '}
                                    <span className="new">{e.thayBang}</span>
                                </div>
                                <span className={`pill ${badge(e.lyDo)}`}>{e.lyDo}</span>
                            </div>
                        )
                    })}
                </div>

                {filteredEvents.length > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                        <button onClick={() => setPageEvents(p => Math.max(1, p - 1))} disabled={pageEvents === 1} style={{ padding: '8px 16px', background: pageEvents === 1 ? '#e0e0e0' : 'var(--blue)', color: pageEvents === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageEvents === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang trước</button>
                        <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {pageEvents} / {totalPagesEvents}</span>
                        <button onClick={() => setPageEvents(p => p + 1)} disabled={pageEvents >= totalPagesEvents} style={{ padding: '8px 16px', background: pageEvents >= totalPagesEvents ? '#e0e0e0' : 'var(--blue)', color: pageEvents >= totalPagesEvents ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageEvents >= totalPagesEvents ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang sau</button>
                    </div>
                )}

                <h2 id="doi-hieu-luc" style={{ marginTop: '34px', scrollMarginTop: '112px' }}>
                    Mọi lần đổi hiệu lực mà kho biết
                </h2>
                <p className="sub">
                    Bóc từ chính điều khoản thi hành của các văn bản Bộ, mỗi dòng kèm nguyên văn. Nhiều văn bản 2026 dùng chữ{' '}
                    <b>hết hiệu lực thi hành</b> chứ không dùng <b>thay thế</b> hay <b>bãi bỏ</b>, nên tra theo hai từ khoá quen
                    thuộc sẽ bỏ sót.
                </p>

                <div className="srow">
                    <input
                        id="skTim"
                        className="inp"
                        type="search"
                        placeholder="Lọc: 17/2021, tuyen sinh, kiem dinh, 1982"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <span className="cnt">
                        <b>{filteredSK.length}</b> / {SK.length} lần đổi hiệu lực
                    </span>
                </div>

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

                            {filteredSK.length > 0 && (
                                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
                                    <button onClick={() => setPageSK(p => Math.max(1, p - 1))} disabled={pageSK === 1} style={{ padding: '8px 16px', background: pageSK === 1 ? '#e0e0e0' : 'var(--blue)', color: pageSK === 1 ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageSK === 1 ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang trước</button>
                                    <span style={{ fontWeight: 600, color: 'var(--text)' }}>Trang {pageSK} / {totalPagesSK}</span>
                                    <button onClick={() => setPageSK(p => p + 1)} disabled={pageSK >= totalPagesSK} style={{ padding: '8px 16px', background: pageSK >= totalPagesSK ? '#e0e0e0' : 'var(--blue)', color: pageSK >= totalPagesSK ? '#888' : '#fff', border: 'none', borderRadius: '8px', cursor: pageSK >= totalPagesSK ? 'not-allowed' : 'pointer', fontWeight: 600 }}>Trang sau</button>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="empty">Không có lần đổi nào khớp.</div>
                    )}
                </div>
            </div>
        </section>
    );
};

export default LawEvents;
