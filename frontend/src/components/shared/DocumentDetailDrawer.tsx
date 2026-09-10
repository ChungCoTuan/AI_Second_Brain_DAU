import React, { useEffect, useState } from 'react';
import { useDetail } from '../../context/DetailContext';
import { DEMO_DATA } from '../../data';
import { fmtDate, badge } from '../../utils';

const DocumentDetailDrawer: React.FC = () => {
  const { docId, closeDetail } = useDetail();
  const [data, setData] = useState<any>(null);

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

    let m = DEMO_DATA.docMeta?.[docId];
    
    // Văn bản của Bộ
    if (docId.startsWith('bo:')) {
      const so = docId.slice(3);
      const o = (DEMO_DATA.vbBo || []).find((x: any) => x.soHieu === so);
      if (o) {
        setData({ type: 'bo', data: o });
        return;
      }
    }

    if (!m) {
      setData({ type: 'not-found' });
      return;
    }

    const w = DEMO_DATA.warnings.find((x: any) => x.docId === docId);
    const items = w ? w.items : null;
    setData({ type: 'truong', data: m, items });
  }, [docId]);

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

    if (data.type === 'bo') {
      const o = data.data;
      const hl0 = o.hieuLucTu || {};
      const ad = o.apDungTu || {};
      const tt = o.thayThe || [];
      const bb = o.baiBo || [];
      const cc = o.canCu || [];
      const dk = o.dieuKhoan || [];
      const nv = o.nghiaVu || [];
      const cs = o.conSoChot || [];
      const qc = o.quyCheKemTheo;

      return (
        <>
          <div className="dr-h">
            <div>
              <div className="t">{o.soHieu}</div>
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
              {row('Ban hành', fmtDate(o.ngayBanHanh))}
              {row('Người ký', [o.chucVu, o.nguoiKy].filter(Boolean).join(' · '))}
              {row('Hiệu lực', fmtDate(hl0.ngay))}
              {ad.ngay && row('Áp dụng từ', fmtDate(ad.ngay))}
            </div>

            {o.trichYeu && (
              <>
                <div className="sec-t">Trích yếu</div>
                <div className="sum">{o.trichYeu}</div>
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
                <div className="sec-t">Nghĩa vụ ({nv.length})</div>
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

    if (data.type === 'truong') {
      const m = data.data;
      const items = data.items;
      const conf = m.conf != null ? Math.round(m.conf * 100) : null;

      return (
        <>
          <div className="dr-h">
            <div>
              <div className="t">{m.soHieu || 'Văn bản'}</div>
              <div className="s">{[m.loai, m.coQuan].filter(Boolean).join(' · ')}</div>
            </div>
            <div className="x" onClick={closeDetail}>&times;</div>
          </div>
          <div className="dr-b">
            <div className="kv">
              {row('Loại', m.loai)}
              {row('Cơ quan', m.coQuan)}
              {row('Người ký', m.nguoiKy)}
              {row('Ngày ký', fmtDate(m.ngayKy))}
              {row('Hiệu lực', `${fmtDate(m.hieuLucTu)} → ${m.hieuLucDen ? fmtDate(m.hieuLucDen) : 'nay'}`)}
              {row('Trạng thái', m.status)}
            </div>

            <div style={{ display: 'flex', gap: '18px', alignItems: 'center', marginBottom: '6px' }}>
              {conf != null && (
                <span className="conf">
                  Độ tin cậy trích xuất
                  <span className="bar2">
                    <i style={{ width: `${conf}%` }}></i>
                  </span>
                  <b>{conf}%</b>
                </span>
              )}
              <span className="conf">{m.ocr ? '📄 có dùng OCR' : '📄 lớp chữ số'}</span>
            </div>

            {m.tomTat && (
              <>
                <div className="sec-t">Tóm tắt (AI trích)</div>
                <div className="sum">{m.tomTat}</div>
              </>
            )}

            {items && (
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

            {m.chuDe && m.chuDe.length > 0 && (
              <>
                <div className="sec-t">Chủ đề</div>
                <div className="chips">
                  {m.chuDe.map((c: string, i: number) => (
                    <span className="chip2" key={i}>{c}</span>
                  ))}
                </div>
              </>
            )}

            {m.tags && m.tags.length > 0 && (
              <>
                <div className="sec-t">Từ khoá</div>
                <div className="chips">
                  {m.tags.map((t: string, i: number) => (
                    <span className="chip2" key={i}>{t}</span>
                  ))}
                </div>
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
    </>
  );
};

export default DocumentDetailDrawer;
