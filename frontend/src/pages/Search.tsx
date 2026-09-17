import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { DEMO_DATA } from '../data';
import { fold, hl } from '../utils';
import { useDetail } from '../context/DetailContext';
import { queryRAG, fetchDocuments, type RAGQueryResponse, type DocumentItem } from '../services/api';
import { Sparkles, ShieldCheck, AlertCircle, ExternalLink, Loader2 } from 'lucide-react';

const TOPIC_NAMES: Record<string, string> = {
  DAO_TAO: "Đào Tạo & Học Vụ",
  TUYEN_SINH: "Tuyển Sinh & Nhập Học",
  TAI_CHINH: "Tài Chính & Học Phí",
  NHAN_SU: "Nhân Sự & Giảng Viên",
  CO_SO_VAT_CHAT: "Cơ Sở Vật Chất",
  KHAC: "Văn Bản Hành Chính Khác"
};

const Search: React.FC = () => {
  const { openDetail } = useDetail();
  const [searchParams, setSearchParams] = useSearchParams();
  const chuDeParam = searchParams.get('chu_de') || 'all';

  const [searchTerm, setSearchTerm] = useState('');
  const [nguon, setNguon] = useState('all');
  const [loai, setLoai] = useState('all');
  const [selectedTopic, setSelectedTopic] = useState(chuDeParam);
  const [apiDocs, setApiDocs] = useState<DocumentItem[]>([]);

  // State cho RAG Query AI
  const [ragQuestion, setRagQuestion] = useState('');
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResult, setRagResult] = useState<RAGQueryResponse | null>(null);

  useEffect(() => {
    setSelectedTopic(chuDeParam);
  }, [chuDeParam]);

  useEffect(() => {
    let isMounted = true;
    const fetchApiDocs = async () => {
      try {
        const topicFilter = selectedTopic === 'all' ? undefined : selectedTopic;
        const res = await fetchDocuments({ chu_de: topicFilter, q: searchTerm, limit: 100 });
        if (isMounted) {
          setApiDocs(res.items || []);
        }
      } catch (err) {
        console.warn("Failed to fetch API docs:", err);
      }
    };
    fetchApiDocs();
    return () => { isMounted = false; };
  }, [selectedTopic, searchTerm]);

  const C = DEMO_DATA.corpus || [];
  const nBo = C.filter((r: any) => r.nguon === 'bộ').length;
  const nTr = C.length - nBo;

  const loais = Array.from(new Set(C.map((r: any) => r.loai).filter(Boolean))).sort();

  const q = fold(searchTerm);
  
  // Convert API docs to uniform display format
  const mappedApiDocs = apiDocs.map(d => ({
    id: d.doc_id,
    soHieu: d.so_hieu || d.doc_id,
    tomTat: d.ten_van_ban,
    coQuan: d.co_quan_ban_hanh || 'Hệ thống DAU',
    ngay: d.ngay_ban_hanh || '',
    loai: d.loai_van_ban || 'Quy định',
    nguon: d.muc_do_lien_quan_dau === 'DIRECT' ? 'trường' : 'bộ',
    chuDe: [TOPIC_NAMES[d.chu_de] || d.chu_de || 'Khác'],
    isApi: true
  }));

  const combinedCorpus = [
    ...mappedApiDocs,
    ...C.filter((r: any) => !mappedApiDocs.some(a => a.id === r.id))
  ];

  const kq = combinedCorpus.filter((r: any) => {
    if (nguon !== 'all' && r.nguon !== nguon) return false;
    if (loai !== 'all' && r.loai !== loai) return false;
    if (selectedTopic !== 'all') {
      const topicName = TOPIC_NAMES[selectedTopic];
      const matchTopicCode = r.chuDe?.includes(selectedTopic);
      const matchTopicName = topicName && r.chuDe?.some((c: string) => c.includes(topicName) || topicName.includes(c));
      if (!matchTopicCode && !matchTopicName) return false;
    }
    if (!q) return true;
    return fold([r.soHieu, r.tomTat, (r.chuDe || []).join(' '), (r.tags || []).join(' '), r.coQuan].join(' ')).includes(q);
  });

  const show = kq.slice(0, 120);

  const cat = (s: string, n: number) => {
    s = String(s == null ? '' : s);
    if (s.length <= n) return s;
    const c = s.slice(0, n);
    const k = c.lastIndexOf(' ');
    return (k > n * 0.6 ? c.slice(0, k) : c) + '…';
  };

  const handleAskRAG = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuestion.trim()) return;

    setRagLoading(true);
    setRagResult(null);

    const res = await queryRAG(ragQuestion.trim());
    setRagResult(res);
    setRagLoading(false);
  };

  return (
    <section id="tra-cuu" style={{ background: 'var(--soft)', paddingBottom: '40px' }}>
      <div className="wrap">
        <h2>Tra cứu kho văn bản & Trợ lý RAG AI</h2>
        <p className="sub">
          <b>{C.length}</b> bản ghi tra cứu: <b>{nTr}</b> văn bản của trường và <b>{nBo}</b> văn bản của Bộ. Tích hợp RAG AI kiểm định NLI trung thực.
        </p>

        {/* ── Box RAG AI Question & Answer ──────────────────────────────── */}
        <div style={{
          background: '#fff',
          borderRadius: '12px',
          border: '1px solid var(--line)',
          padding: '20px',
          marginBottom: '28px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.03)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <Sparkles size={20} color="var(--blue)" />
            <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--blue)', fontWeight: 700 }}>
              Hỏi Trợ Lý RAG AI (Citation-First & NLI Check)
            </h3>
          </div>

          <form onSubmit={handleAskRAG} style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              className="inp"
              style={{ flex: 1, padding: '12px 16px', fontSize: '14px', borderRadius: '8px' }}
              placeholder="Nhập câu hỏi tra cứu (Ví dụ: Quy định về thạc sĩ, điều kiện xét tuyển đại học...)"
              value={ragQuestion}
              onChange={(e) => setRagQuestion(e.target.value)}
            />
            <button
              type="submit"
              disabled={ragLoading || !ragQuestion.trim()}
              style={{
                background: 'var(--blue)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                padding: '0 20px',
                fontWeight: 600,
                cursor: ragLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                opacity: ragLoading ? 0.7 : 1
              }}
            >
              {ragLoading ? <Loader2 size={16} className="spin" /> : <Sparkles size={16} />}
              {ragLoading ? 'Đang truy vấn...' : 'Hỏi RAG AI'}
            </button>
          </form>

          {/* RAG Answer Display */}
          {ragResult && (
            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--ink)' }}>
                  Câu trả lời từ hệ thống:
                </span>
                {ragResult.nli_status === 'entailment' && (
                  <span style={{ background: '#ecfdf5', color: '#047857', padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ShieldCheck size={14} /> NLI Verified (Faithful)
                  </span>
                )}
                {ragResult.nli_status === 'OFFLINE' && (
                  <span style={{ background: '#fef3c7', color: '#b45309', padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <AlertCircle size={14} /> Backend Offline (FastAPI)
                  </span>
                )}
              </div>

              {ragResult.answer ? (
                <div style={{
                  background: '#f8fafc',
                  borderLeft: '4px solid var(--blue)',
                  padding: '16px 20px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  lineHeight: '1.7',
                  whiteSpace: 'pre-wrap',
                  color: '#0f172a',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                  fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                }}>
                  {ragResult.answer}
                </div>
              ) : (
                <div style={{ color: '#64748b', fontStyle: 'italic', fontSize: '14px' }}>
                  {ragResult.message}
                </div>
              )}

              {/* Citations */}
              {ragResult.citations && ragResult.citations.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Nguồn Trích Dẫn ({ragResult.citations.length} nguồn PUBLISHED — Đã kiểm định):
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {ragResult.citations.map((c) => (
                      <div
                        key={c.chunk_id || c.index}
                        style={{
                          background: '#ffffff',
                          border: '1px solid #cbd5e1',
                          borderRadius: '8px',
                          padding: '12px 16px',
                          fontSize: '13px',
                          cursor: c.doc_id ? 'pointer' : 'default',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                        }}
                        onClick={() => c.doc_id && openDetail(c.doc_id)}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span style={{ fontWeight: 700, color: 'var(--blue)', fontSize: '14px' }}>
                            [{c.index}] {c.ten_van_ban} — {c.dieu_khoan}
                          </span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span
                              style={{
                                background: '#dcfce7',
                                color: '#15803d',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontSize: '11px',
                                fontWeight: 700,
                              }}
                            >
                              🟢 PUBLISHED
                            </span>
                            {c.doc_id && (
                              <span
                                style={{
                                  background: '#eff6ff',
                                  color: '#1d4ed8',
                                  padding: '2px 8px',
                                  borderRadius: '6px',
                                  fontSize: '11px',
                                  fontWeight: 700,
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                }}
                              >
                                📄 Xem Chi Tiết <ExternalLink size={12} />
                              </span>
                            )}
                          </div>
                        </div>
                        <div style={{ color: '#475569', fontSize: '12px', lineHeight: '1.5' }}>
                          "{c.content_preview}..."
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Filters & Traditional Search ─────────────────────────────── */}
        <div className="srow">
          <input
            id="traTim"
            className="inp"
            type="search"
            autoComplete="off"
            placeholder="Lọc từ khóa kho văn bản: tuyen sinh, kiem dinh, thac si, van bang..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select 
            id="traChuDe" 
            className="sel" 
            value={selectedTopic} 
            onChange={(e) => {
              setSelectedTopic(e.target.value);
              if (e.target.value === 'all') {
                searchParams.delete('chu_de');
                setSearchParams(searchParams);
              } else {
                setSearchParams({ chu_de: e.target.value });
              }
            }}
          >
            <option value="all">Tất cả chủ đề (UC-09)</option>
            <option value="DAO_TAO">🎓 Đào Tạo & Học Vụ</option>
            <option value="TUYEN_SINH">🎯 Tuyển Sinh & Nhập Học</option>
            <option value="TAI_CHINH">💰 Tài Chính & Học Phí</option>
            <option value="NHAN_SU">👔 Nhân Sự & Giảng Viên</option>
            <option value="CO_SO_VAT_CHAT">🏢 Cơ Sở Vật Chất</option>
            <option value="KHAC">📂 Văn Bản Hành Chính Khác</option>
          </select>
          <select id="traNguon" className="sel" value={nguon} onChange={(e) => setNguon(e.target.value)}>
            <option value="all">Mọi nguồn</option>
            <option value="bộ">Văn bản pháp quy của Bộ/Chính phủ</option>
            <option value="trường">Văn bản nội bộ của Trường</option>
          </select>
          <select id="traLoai" className="sel" value={loai} onChange={(e) => setLoai(e.target.value)}>
            <option value="all">Mọi loại</option>
            {loais.map((l: any) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <span className="cnt" id="traCnt">
            <b>{kq.length}</b> / {C.length} bản ghi
          </span>
        </div>

        <div className="rlist" id="traList">
          {show.length > 0 ? (
            show.map((r: any) => (
              <div
                key={r.id}
                className="r"
                data-did={r.id}
                onClick={() => openDetail(r.id)}
              >
                <div>
                  <span className="rs">{hl(r.soHieu, q)}</span>
                  <div className="rm">
                    <span className={`src ${r.nguon === 'bộ' ? 'bo' : 'truong'}`}>
                      {r.nguon === 'bộ' ? 'BỘ' : 'TRƯỜNG'}
                    </span>{' '}
                    {r.loai || ''}
                  </div>
                </div>
                <div>
                  <div className="rt">{hl(cat(r.tomTat || '', 240), q)}</div>
                  {r.soDieu ? (
                    <div className="rm">
                      {r.soDieu} điều · {r.soNghiaVu || 0} nghĩa vụ
                    </div>
                  ) : null}
                  {r.chuDe && r.chuDe.length ? (
                    <div className="rm">{r.chuDe.join(' · ')}</div>
                  ) : null}
                </div>
                <div className="rr">
                  {r.ngay || ''}
                  {r.ocr ? (
                    <>
                      <br />
                      nguồn scan
                    </>
                  ) : null}
                </div>
              </div>
            ))
          ) : (
            <div className="empty">Không tìm thấy. Thử gõ số hiệu, ví dụ 54/2026, hoặc từ khoá không dấu.</div>
          )}
          {kq.length > show.length && (
            <div className="empty">Còn {kq.length - show.length} bản ghi nữa, gõ thêm để thu hẹp.</div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Search;
