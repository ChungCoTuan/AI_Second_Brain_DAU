import React, { useState } from 'react';
import { useData } from '../context/DataContext';
import { fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';

const DeadDocs: React.FC = () => {
  const { openDetail } = useDetail();
  const [expandedDocs, setExpandedDocs] = useState<Record<string, boolean>>({});
  const { data, markAsRead, readDeadDocs } = useData();
  const rows = [...(data.vbTuChet || [])].sort((a: any, b: any) => {
    const aUnread = !readDeadDocs.includes(a.soHieu);
    const bUnread = !readDeadDocs.includes(b.soHieu);
    if (aUnread && !bUnread) return -1;
    if (!aUnread && bUnread) return 1;
    return 0;
  });
  const sap = [...(data.vbSapChet || [])].sort((a: any, b: any) => {
    const aUnread = !readDeadDocs.includes(a.soHieu);
    const bUnread = !readDeadDocs.includes(b.soHieu);
    if (aUnread && !bUnread) return -1;
    if (!aUnread && bUnread) return 1;
    return 0;
  });

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
          <div className="rm">{r.loai || ''}</div>
        </div>
        <div>
          <div className="rt" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
            <div>
              {r.lyDo} bởi <b style={{ color: 'var(--green)' }}>{r.thayBang.join(', ')}</b>, từ {fmtDate(r.tuNgay)}
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
                <div style={{ color: 'var(--ink)' }}>{r.nguyenVan || `Văn bản này ${r.lyDo.toLowerCase()} ${r.thayBang.join(', ')} theo quy định hiện hành.`}</div>
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

          <div className="rlist">{rows.map((r: any) => renderDoc(r, false))}</div>

          {sap.length > 0 && (
            <>
              <div className="sec-t" style={{ marginTop: '20px', textTransform: 'uppercase' }}>
                Sắp hết hiệu lực, hiện vẫn còn giá trị
              </div>
              <div className="rlist">{sap.map((r: any) => renderDoc(r, true))}</div>
            </>
          )}
        </div>
      </div>
    </section>
  );
};

export default DeadDocs;
