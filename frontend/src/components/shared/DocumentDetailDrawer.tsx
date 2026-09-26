import React, { useEffect, useState } from 'react';
import { useDetail } from '../../context/DetailContext';
import { fmtDate, badge } from '../../utils';
import { Download, Eye, X } from 'lucide-react';

const DocumentDetailDrawer: React.FC = () => {
  const { docId, closeDetail } = useDetail();
  const [data, setData] = useState<any>(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeDetail();
    };
    if (docId) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [docId, closeDetail]);

  useEffect(() => {
    if (!docId) {
      setData(null);
      return;
    }

    // Fetch dữ liệu thật từ API
    fetch(`http://localhost:8000/api/v1/documents/detail/${encodeURIComponent(docId)}`)
      .then(res => {
        if (!res.ok) throw new Error('Not found');
        return res.json();
      })
      .then(d => {
        // API trả về d.type là 'bo' hoặc 'truong'
        setData({ type: d.type, data: d.data, items: d.items });
      })
      .catch(e => {
        console.error(e);
        setData({ type: 'not-found' });
      });
  }, [docId]);

  const handleDownloadReport = async (soHieu: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/reports/template/${encodeURIComponent(soHieu)}`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Khung_Bao_Cao_${soHieu.replace(/[\/\\]/g, '_')}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error(err);
      alert('Có lỗi khi tải khung báo cáo!');
    }
  };

  const row = (k: string, v: string | undefined | null) => {
    if (!v) return null;
    return (
      <>
        <span className="k">{k}</span>
        <span className="v">{v}</span>
      </>
    );
  };

  const bangChung = (nguon: string) => {
    if (!nguon) return null;
    return (
      <details style={{ marginTop: '4px', flexBasis: '100%' }}>
        <summary className="toggle" style={{ listStyle: 'none' }}>
          Xem nguyên văn
        </summary>
        <div className="ev-q" style={{ marginTop: '8px' }}>
          <span className="lbl">Nguyên văn điều khoản</span>
          {nguon}
        </div>
      </details>
    );
  };

  const nhanNgay = (ngay: string) => {
    if (!ngay) return '';
    if (ngay.startsWith('--')) {
      const p = ngay.split('-');
      return `hằng năm, ngày ${p[3]}/${p[2]}`;
    }
    return fmtDate(ngay);
  };

  const renderContent = () => {
    if (!data) return null;

    if (data.type === 'not-found') {
      return (
        <>
          <div className="dr-h">
            <div>
              <div className="t">Không có dữ liệu chi tiết</div>
              <div className="s"></div>
            </div>
            <div className="x" onClick={closeDetail}>&times;</div>
          </div>
          <div className="dr-b">
            <p className="sub">Văn bản này chưa có bản trích xuất trong demo.</p>
          </div>
        </>
      );
    }

    if (data.type === 'bo' || data.type === 'truong') {
      const o = data.data;
      const items = data.items;
      const hl0 = o.hieuLucTu || {};
      const ad = o.apDungTu || {};
      const tt = o.thayThe || [];
      const bb = o.baiBo || [];
      const cc = o.canCu || [];
      const dk = o.dieuKhoan || [];
      const nv = o.nghiaVu || [];
      const cs = o.conSoChot || [];
      const qc = o.quyCheKemTheo;
      const conf = o.conf != null ? Math.round(o.conf * 100) : null;

      return (
        <>
          <div className="dr-h">
            <div>
              <div className="t">{o.soHieu || 'Văn bản'}</div>
              <div className="s">{[o.loai, o.coQuan].filter(Boolean).join(' · ')}</div>
            </div>
            <div className="x" onClick={closeDetail}>&times;</div>
          </div>
          <div className="dr-b">
            {o.ngayNghiNgo && (
              <div className="alert" style={{ marginBottom: '14px' }}>
                Văn bản này đọc từ <b>bản scan qua OCR</b>. Các con số đã được đối chiếu bằng mắt trên ảnh trang gốc,
                nhưng vẫn nên kiểm lại Công báo trước khi dùng cho việc có hậu quả pháp lý.
              </div>
            )}
            <div className="kv">
              {row('Loại', o.loai)}
              {row('Cơ quan', o.coQuan)}
              {row('Người ký', [o.chucVu, o.nguoiKy].filter(Boolean).join(' · '))}
              {row('Ngày ký', fmtDate(o.ngayKy || o.ngayBanHanh))}
              {row('Hiệu lực', o.hieuLucDen ? `${fmtDate(hl0.ngay)} — ${fmtDate(o.hieuLucDen)}` : (hl0.ngay ? `${fmtDate(hl0.ngay)} — nay` : ''))}
              {o.status && row('Trạng thái', o.status)}
              {ad.ngay && row('Áp dụng từ', fmtDate(ad.ngay))}
            </div>

            <div style={{ display: 'flex', gap: '18px', alignItems: 'center', marginBottom: '16px' }}>
              {conf != null && (
                <span className="conf" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                  Độ tin cậy trích xuất
                  <span className="bar2">
                    <i style={{ width: `${conf}%` }}></i>
                  </span>
                  <b>{conf}%</b>
                  {o.ocr !== undefined && (
                    <span style={{ color: 'var(--muted)' }}>
                      {' · '}{o.ocr ? 'có dùng OCR' : 'lớp chữ số'}
                    </span>
                  )}
                </span>
              )}
            </div>

            {(o.tomTat || o.trichYeu) && (
              <>
                <div className="sec-t" style={{ textTransform: 'uppercase' }}>Tóm tắt (AI trích)</div>
                <div className="sum" style={{ background: 'var(--soft)', padding: '12px', borderRadius: '8px', border: '1px dashed var(--line)', marginBottom: '16px' }}>{o.tomTat || o.trichYeu}</div>
              </>
            )}

            {items && items.length > 0 && (
              <>
                <div className="sec-t" style={{ textTransform: 'uppercase', color: 'var(--red)' }}>Căn cứ đã hết hiệu lực</div>
                {items.map((item: any, i: number) => (
                  <div className="cc-item" key={`cc-dead-${i}`} style={{ padding: '8px 0', borderBottom: '1px dashed var(--line)', display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
                    <span style={{ color: 'var(--red)', fontWeight: 600 }}>{item.canCu}</span>
                    <span style={{ margin: '0 8px', color: 'var(--muted)' }}>→</span>
                    <span style={{ color: 'var(--green)', fontWeight: 600 }}>{item.thayBang}</span>
                    <span className="badge replace" style={{ marginLeft: '12px' }}>{item.lyDo}</span>
                  </div>
                ))}
              </>
            )}

            {o.chuDe && o.chuDe.length > 0 && o.chuDe[0] && (
              <>
                <div className="sec-t" style={{ textTransform: 'uppercase', marginTop: '16px' }}>Chủ đề</div>
                <div className="chips" style={{ marginBottom: '16px' }}>
                  {o.chuDe.map((c: string, i: number) => (
                    <span className="chip2" key={i} style={{ borderRadius: '20px', padding: '4px 12px', color: 'var(--red)', background: '#fff0f0', border: '1px solid #ffd0d0' }}>{c}</span>
                  ))}
                </div>
              </>
            )}

            {o.tags && o.tags.length > 0 && o.tags[0] && (
              <>
                <div className="sec-t" style={{ textTransform: 'uppercase', marginTop: '16px' }}>Từ khoá</div>
                <div className="chips" style={{ marginBottom: '16px' }}>
                  {o.tags.map((t: string, i: number) => (
                    <span className="chip2" key={i} style={{ borderRadius: '20px', padding: '4px 12px', background: '#fff0f0', color: 'var(--red)', border: '1px solid #ffd0d0' }}>{t.trim()}</span>
                  ))}
                </div>
              </>
            )}

            {hl0.nguon && (
              <>
                <div className="sec-t">Điều khoản hiệu lực</div>
                <div className="ev-q">
                  <span className="lbl">Nguyên văn</span>
                  {hl0.nguon}
                </div>
              </>
            )}

            {ad.nguon && (
              <>
                <div className="sec-t">Mốc áp dụng tách riêng</div>
                {ad.mo_ta && <div className="sum" style={{ marginBottom: '6px' }}>{ad.mo_ta}</div>}
                <div className="ev-q">
                  <span className="lbl">Nguyên văn</span>
                  {ad.nguon}
                </div>
              </>
            )}

            {(tt.length > 0 || bb.length > 0) && (
              <>
                <div className="sec-t">Làm văn bản khác hết hiệu lực ({tt.length + bb.length})</div>
                {tt.map((t: any, i: number) => (
                  <div className="cc-item" key={`tt-${i}`}>
                    <span style={{ color: 'var(--red)', fontWeight: 700 }}>
                      {t.soHieu || '(không nêu số hiệu)'}
                    </span>
                    <span className="badge replace">bị thay thế</span>
                    <div style={{ flexBasis: '100%' }}>{t.ten || ''}</div>
                    {bangChung(t.nguon)}
                  </div>
                ))}
                {bb.map((b: any, i: number) => (
                  <div className="cc-item" key={`bb-${i}`}>
                    <span style={{ color: 'var(--red)', fontWeight: 700 }}>
                      {b.soHieu || '(không nêu số hiệu)'}
                    </span>
                    <span className="badge repeal">bị bãi bỏ</span>
                    {b.phamVi && b.phamVi !== 'toàn bộ' && <span className="tag2">phạm vi: {b.phamVi}</span>}
                    <div style={{ flexBasis: '100%' }}>{b.ten || ''}</div>
                    {bangChung(b.nguon)}
                  </div>
                ))}
              </>
            )}

            {cc.length > 0 && (
              <>
                <div className="sec-t">Căn cứ ({cc.length})</div>
                <div className="chips">
                  {cc.map((c: any, i: number) => (
                    <span className="chip2" key={i}>{c.soHieu || c.ten || ''}</span>
                  ))}
                </div>
              </>
            )}

            {qc && (
              <>
                <div className="sec-t">Quy chế ban hành kèm</div>
                <div className="sum">
                  {qc.ten || ''}
                  {qc.soChuong ? ` · ${qc.soChuong} chương` : ''}
                  {qc.soDieu ? ` · ${qc.soDieu} điều` : ''}
                </div>
              </>
            )}

            {dk.length > 0 && (
              <>
                <div className="sec-t">Mục lục điều khoản ({dk.length})</div>
                {dk.map((d: any, i: number) => (
                  <div className="dk" key={i}>
                    <span className="n">{d.so || ''}</span>
                    <span>
                      {d.ten || ''}
                      {d.thuoc && <span className="tag2" style={{ marginLeft: '6px' }}>{d.thuoc}</span>}
                    </span>
                  </div>
                ))}
              </>
            )}

            {nv.length > 0 && (
              <>
                <div className="sec-t" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>Nghĩa vụ ({nv.length})</span>
                  <button 
                    onClick={() => setShowPreview(true)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '4px',
                      background: 'var(--red)', color: '#fff', border: 'none',
                      padding: '4px 10px', borderRadius: '4px', cursor: 'pointer',
                      fontSize: '12px', fontWeight: '500'
                    }}
                  >
                    <Eye size={14} /> Xem trước Khung Báo Cáo
                  </button>
                </div>
                {nv.map((n: any, i: number) => (
                  <div className="nvrow" key={i}>
                    <div className="h">
                      <span className="tag2">{n.dieu || ''}</span>
                      <span className="tag2">{n.loai || 'khác'}</span>
                      {n.hanChot && <span className="tag2 han">hạn {nhanNgay(n.hanChot)}</span>}
                    </div>
                    <div>{n.noiDung || ''}</div>
                    {bangChung(n.nguon)}
                  </div>
                ))}
              </>
            )}

            {cs.length > 0 && (
              <>
                <div className="sec-t">Con số chốt ({cs.length})</div>
                {cs.map((c: any, i: number) => (
                  <div className="nvrow" key={i}>
                    <div className="h">
                      <b style={{ color: 'var(--blue)' }}>{c.giaTri || ''}</b>
                      {c.dieu && <span className="tag2">{c.dieu}</span>}
                    </div>
                    <div>{c.yNghia || ''}</div>
                    {bangChung(c.nguon)}
                  </div>
                ))}
              </>
            )}

            {items && items.length > 0 && (
              <>
                <div className="sec-t">Căn cứ đã hết hiệu lực</div>
                {items.map((it: any, i: number) => (
                  <div className="cc-item" key={i}>
                    <span style={{ color: 'var(--red)', fontWeight: 600 }}>{it.canCu}</span>
                    <span className="arrow">→</span>
                    <span style={{ color: 'var(--green)', fontWeight: 600 }}>{it.thayBang}</span>
                    <span className={`badge ${badge(it.lyDo)}`}>{it.lyDo}</span>
                  </div>
                ))}
              </>
            )}

            {o.chuDe && o.chuDe.length > 0 && (
              <>
                <div className="sec-t">Chủ đề</div>
                <div className="chips">
                  {o.chuDe.map((c: string, i: number) => (
                    <span className="chip2" key={i}>{c}</span>
                  ))}
                </div>
              </>
            )}

            {o.tags && o.tags.length > 0 && (
              <>
                <div className="sec-t">Từ khoá</div>
                <div className="chips">
                  {o.tags.map((t: string, i: number) => (
                    <span className="chip2" key={i}>{t}</span>
                  ))}
                </div>
              </>
            )}

            {o.ghiChu && (
              <>
                <div className="sec-t">Ghi chú khi bóc tách</div>
                <div className="sum">{o.ghiChu}</div>
              </>
            )}
          </div>
        </>
      );
    }
  };

  return (
    <>
      <div className={`ov ${docId ? 'show' : ''}`} onClick={closeDetail}></div>
      <div className={`drawer ${docId ? 'show' : ''}`}>
        {renderContent()}
      </div>

      {showPreview && data && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', zIndex: 10000,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{
            background: '#fff', width: '600px', maxWidth: '90vw', maxHeight: '90vh',
            borderRadius: '8px', display: 'flex', flexDirection: 'column',
            boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
          }}>
            <div style={{ 
              padding: '16px 24px', borderBottom: '1px solid #eee', 
              display: 'flex', justifyContent: 'space-between', alignItems: 'center' 
            }}>
              <h3 style={{ margin: 0, fontSize: '18px', color: '#111' }}>Bản xem trước Khung Báo Cáo</h3>
              <button 
                onClick={() => setShowPreview(false)}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#666' }}
              >
                <X size={20} />
              </button>
            </div>
            
            <div style={{ padding: '24px', overflowY: 'auto', flex: 1, fontSize: '14px', lineHeight: '1.6' }}>
              <div style={{ textAlign: 'center', fontWeight: 'bold', marginBottom: '24px' }}>
                CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM<br/>
                Độc lập - Tự do - Hạnh phúc
              </div>
              <div style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '16px', marginBottom: '24px' }}>
                BÁO CÁO THỰC HIỆN<br/>
                ({data.data.soHieu})
              </div>
              
              <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>I. CĂN CỨ PHÁP LÝ</div>
              <div style={{ marginBottom: '16px', paddingLeft: '16px' }}>- Căn cứ theo văn bản: {data.data.soHieu}.</div>
              
              <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>II. KẾT QUẢ THỰC HIỆN NGHĨA VỤ</div>
              <div style={{ marginBottom: '16px', paddingLeft: '16px' }}>
                {data.data.nghiaVu?.map((nv: any, i: number) => (
                  <div key={i} style={{ marginBottom: '16px' }}>
                    <b>{i + 1}. {nv.noiDung}</b>
                    {nv.hanChot && nv.hanChot !== 'Không quy định cụ thể' && (
                      <i style={{ color: '#666' }}> (Hạn chót: {nv.hanChot})</i>
                    )}
                    <div style={{ color: '#888', marginTop: '4px' }}>
                      - Đơn vị phụ trách: (Tự điền)<br/>
                      - Số liệu / Kết quả đạt được: ......................................................<br/>
                      - Khó khăn vướng mắc: ..............................................................
                    </div>
                  </div>
                ))}
              </div>
              
              <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>III. ĐỀ XUẤT, KIẾN NGHỊ</div>
              <div style={{ marginBottom: '16px', paddingLeft: '16px', color: '#888' }}>
                1. ....................................................................................<br/>
                2. ....................................................................................
              </div>
            </div>
            
            <div style={{ 
              padding: '16px 24px', borderTop: '1px solid #eee', 
              display: 'flex', justifyContent: 'flex-end', gap: '12px', background: '#f9f9f9', borderRadius: '0 0 8px 8px' 
            }}>
              <button 
                onClick={() => setShowPreview(false)}
                style={{
                  padding: '8px 16px', border: '1px solid #ddd', background: '#fff', 
                  borderRadius: '4px', cursor: 'pointer', fontWeight: '500'
                }}
              >
                Hủy bỏ
              </button>
              <button 
                onClick={() => handleDownloadReport(data.data.soHieu)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  background: 'var(--red)', color: '#fff', border: 'none', 
                  padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: '500'
                }}
              >
                <Download size={16} /> Tải file Word (.docx)
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DocumentDetailDrawer;
