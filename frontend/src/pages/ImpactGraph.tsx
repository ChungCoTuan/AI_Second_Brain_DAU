import React, { useState } from 'react';
import { DEMO_DATA } from '../data';
import { useDetail } from '../context/DetailContext';

const ImpactGraph: React.FC = () => {
  const { openDetail } = useDetail();
  const impact = DEMO_DATA.impact || [];
  const [selectedIndex, setSelectedIndex] = useState(0);

  if (impact.length === 0) return null;

  const x = impact[selectedIndex];
  const deps = x ? x.dependents : [];

  const W = 740;
  const rowH = 50;
  const pad = 44;
  const bx = 18;
  const bw = 214;
  const dx = 474;
  const dw = 250;
  const dh = 38;
  const H = Math.max(240, pad * 2 + deps.length * rowH);
  const by = H / 2;

  return (
    <section id="do-thi" style={{ background: 'var(--bg)' }}>
      <div className="wrap">
        <h2>Đồ thị mức độ ảnh hưởng</h2>
        <p className="sub">Trực quan hoá dây chuyền "văn bản kéo văn bản".</p>

        <div className="impact">
          <div style={{ marginBottom: '14px' }}>
            <span style={{ fontSize: '13px', color: 'var(--muted)', display: 'inline-block', width: '130px' }}>
              Chọn căn cứ thay đổi:
            </span>
            <select
              value={selectedIndex}
              onChange={(e) => setSelectedIndex(Number(e.target.value))}
              style={{
                fontSize: '14px',
                padding: '8px 10px',
                border: '1px solid var(--line)',
                borderRadius: '8px',
                width: '100%',
                maxWidth: '420px',
              }}
            >
              {impact.map((item: any, i: number) => (
                <option key={i} value={i}>
                  {item.canCu} ({item.dependents.length} văn bản phụ thuộc)
                </option>
              ))}
            </select>
          </div>

          <div id="impactOut">
            {x && (
              <>
                <div className="note">
                  Nếu <b>{x.canCu}</b> thay đổi ({x.lyDo} → <b>{x.thayBang}</b>), {deps.length} văn bản dưới đây cần rà
                  lại.
                </div>
                {deps.length === 0 ? (
                  <p className="sub">Không có văn bản phụ thuộc trong kho.</p>
                ) : (
                  <div style={{ overflowX: 'auto', marginTop: '14px' }}>
                    <svg
                      viewBox={`0 0 ${W} ${H}`}
                      width={W}
                      style={{ minWidth: `${W}px`, maxWidth: `${W}px`, fontFamily: 'inherit' }}
                    >
                      <defs>
                        <marker
                          id="ah"
                          markerWidth="9"
                          markerHeight="9"
                          refX="7"
                          refY="3"
                          orient="auto"
                        >
                          <path d="M0,0 L7,3 L0,6 Z" fill="#b91c1c" />
                        </marker>
                      </defs>

                      {deps.map((_d: any, i: number) => {
                        const dy = pad + i * rowH + dh / 2;
                        const x1 = bx + bw;
                        const y1 = by;
                        const x2 = dx;
                        const y2 = dy;
                        const mx = (x1 + x2) / 2;
                        return (
                          <path
                            key={`path-${i}`}
                            d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2 - 2},${y2}`}
                            fill="none"
                            stroke="#d99"
                            strokeWidth="1.6"
                            markerEnd="url(#ah)"
                          />
                        );
                      })}

                      <g>
                        <rect
                          x={bx}
                          y={by - 28}
                          width={bw}
                          height={56}
                          rx={10}
                          fill="#fef2f2"
                          stroke="#b91c1c"
                          strokeWidth="1.8"
                          strokeDasharray="5 3"
                        />
                        <text
                          x={bx + bw / 2}
                          y={by - 6}
                          textAnchor="middle"
                          fontSize="9.5"
                          fill="#b91c1c"
                          fontWeight="700"
                        >
                          CĂN CỨ HẾT HIỆU LỰC
                        </text>
                        <text
                          x={bx + bw / 2}
                          y={by + 12}
                          textAnchor="middle"
                          fontSize="13"
                          fill="#1e293b"
                          fontWeight="700"
                        >
                          {x.canCu}
                        </text>
                      </g>

                      <g>
                        <rect
                          x={bx}
                          y={by + 40}
                          width={bw}
                          height={30}
                          rx={8}
                          fill="#f0fdf4"
                          stroke="#15803d"
                          strokeWidth="1.4"
                        />
                        <text x={bx + bw / 2} y={by + 59} textAnchor="middle" fontSize="11.5" fill="#15803d">
                          thay bằng:{' '}
                          <tspan fontWeight="700">{x.thayBang}</tspan>
                        </text>
                      </g>
                      <line x1={bx + bw / 2} y1={by + 28} x2={bx + bw / 2} y2={by + 40} stroke="#15803d" strokeWidth="1.2" />

                      {deps.map((d: any, i: number) => {
                        const dy = pad + i * rowH + dh / 2;
                        return (
                          <g
                            key={`node-${i}`}
                            className="dnode"
                            style={{ cursor: 'pointer' }}
                            onClick={() => openDetail(d.docId)}
                          >
                            <rect
                              x={dx}
                              y={dy - dh / 2}
                              width={dw}
                              height={dh}
                              rx={8}
                              fill="#fff"
                              stroke="#990000"
                              strokeWidth="1.3"
                            />
                            <text x={dx + 12} y={dy + 2} fontSize="12.5" fill="#1e293b" fontWeight="600">
                              {d.soHieu}
                            </text>
                            {d.loai && (
                              <text x={dx + 12} y={dy + 15} fontSize="9.5" fill="#64748b">
                                {d.loai} · bấm xem chi tiết
                              </text>
                            )}
                          </g>
                        );
                      })}
                    </svg>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ImpactGraph;
