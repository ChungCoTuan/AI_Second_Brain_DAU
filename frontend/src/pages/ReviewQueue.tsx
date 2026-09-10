import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { DEMO_DATA } from '../data';
import { badge, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';

const ReviewQueue: React.FC = () => {
  const { openDetail } = useDetail();
  const [searchParams, setSearchParams] = useSearchParams();
  const eventParam = searchParams.get('event');
  const activeEvent = eventParam !== null ? parseInt(eventParam, 10) : null;
  const [filterReason, setFilterReason] = useState('all');

  const evDocs = activeEvent !== null && !isNaN(activeEvent) && DEMO_DATA.events[activeEvent]
    ? new Set(DEMO_DATA.events[activeEvent].docs)
    : null;

  const reasons = [
    { id: 'all', label: 'Tất cả' },
    { id: 'thay', label: 'Bị thay thế' },
    { id: 'bãi', label: 'Bị bãi bỏ' },
  ];

  let filteredWarnings = DEMO_DATA.warnings.map((w: any) => {
    if (evDocs && !evDocs.has(w.soHieu)) return null;
    const items = w.items.filter((it: any) => {
      if (filterReason === 'thay') return it.lyDo.includes('thay');
      if (filterReason === 'bãi') return it.lyDo.includes('bãi');
      return true;
    });
    if (!items.length) return null;
    return { ...w, items };
  }).filter(Boolean);

  const activeEventName =
    activeEvent !== null && !isNaN(activeEvent) && DEMO_DATA.events[activeEvent]
      ? DEMO_DATA.events[activeEvent].canCu
      : '';

  return (
    <section id="ra-soat">
      <div className="wrap">
        <h2>Văn bản cần rà soát</h2>
        <p className="sub">Mỗi văn bản kèm danh sách căn cứ đã hết hiệu lực và văn bản thay thế.</p>

        <div className="filterbar">
          {reasons.map((r) => (
            <span
              key={r.id}
              className={`chip ${filterReason === r.id ? 'active' : ''}`}
              onClick={() => setFilterReason(r.id)}
            >
              {r.label}
            </span>
          ))}

          {activeEventName && (
            <span style={{ color: 'var(--muted)', fontSize: '13px' }}>
              · đang lọc theo sự kiện: <b>{activeEventName}</b>{' '}
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  searchParams.delete('event');
                  setSearchParams(searchParams);
                }}
              >
                bỏ lọc
              </a>
            </span>
          )}
        </div>

        <div className="cards">
          {filteredWarnings.length > 0 ? (
            filteredWarnings.map((w: any) => {
              const worst = w.items.some((it: any) => it.lyDo.includes('bãi')) ? 'repeal' : 'replace';
              return (
                <div
                  key={w.docId}
                  className="card"
                  onClick={() => openDetail(w.docId)}
                >
                  <div className="h">
                    <span className={`badge ${worst}`}>
                      {worst === 'repeal' ? 'bãi bỏ' : 'thay thế'}
                    </span>
                    <span className="doc">{w.soHieu}</span>
                    <span style={{ marginLeft: 'auto', color: 'var(--muted)', fontSize: '12px' }}>
                      xem chi tiết →
                    </span>
                  </div>
                  <div className="b">
                    {w.items.map((it: any, i: number) => {
                      const dc = it.thayBangDaChet;
                      return (
                        <div className="item" key={i}>
                          <div className="row">
                            <span style={{ color: 'var(--red)' }}>{it.canCu}</span>
                            <span className="arrow">→</span>
                            <span style={{ color: dc && dc.daQua ? 'var(--red)' : 'var(--green)' }}>
                              {it.thayBang}
                            </span>
                            <span className={`badge ${badge(it.lyDo)}`}>{it.lyDo}</span>
                            {it.coNguon ? (
                              <span
                                className="tag2"
                                style={{ background: '#f0fdf4', color: 'var(--green)', borderColor: '#bbf7d0' }}
                              >
                                có nguyên văn
                              </span>
                            ) : (
                              <span
                                className="tag2"
                                style={{ background: 'var(--amber-bg)', color: 'var(--amber)', borderColor: '#fde68a' }}
                              >
                                suy luận, chưa có nguyên văn
                              </span>
                            )}
                          </div>
                          {dc && (
                            <div className="cc-ev" style={{ color: 'var(--red)', fontSize: '12px', marginTop: '4px' }}>
                              {dc.daQua ? 'Cảnh báo: ' : 'Sắp tới: '}
                              {it.thayBang} {dc.daQua ? 'cũng đã hết hiệu lực từ ' : 'sẽ hết hiệu lực từ '}
                              {fmtDate(dc.tuNgay)}. Căn cứ dùng được là <b>{dc.thayTiepBang.join(', ')}</b>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })
          ) : (
            <p className="sub">Không có văn bản khớp bộ lọc.</p>
          )}
        </div>
      </div>
    </section>
  );
};

export default ReviewQueue;
