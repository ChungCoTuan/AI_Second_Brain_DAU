import React from 'react';
import { DEMO_DATA } from '../data';
import { useDetail } from '../context/DetailContext';

const PriorityList: React.FC = () => {
  const { openDetail } = useDetail();
  const rows = DEMO_DATA.insights.uuTien || [];

  return (
    <section id="uu-tien">
      <div className="wrap">
        <h2>Ưu tiên xử lý trước</h2>
        <p className="sub">
          Xếp theo mức độ: văn bản có căn cứ <b>bị bãi bỏ</b> và dính <b>nhiều căn cứ hỏng</b> lên đầu. Bấm để xem chi tiết.
        </p>
        <div id="priority">
          <div className="prow phead">
            <span>#</span>
            <span>Văn bản</span>
            <span>Loại</span>
            <span>Căn cứ hỏng</span>
            <span>Mức độ</span>
          </div>
          {rows.map((r: any, i: number) => {
            const lvl = r.baiBo ? (
              <span className="lv lv-hi">Ưu tiên cao</span>
            ) : (
              <span className="lv lv-md">Cần rà</span>
            );
            return (
              <div
                key={r.docId}
                className="prow"
                data-did={r.docId}
                onClick={() => openDetail(r.docId)}
              >
                <span className="pk">{i + 1}</span>
                <span className="pd">{r.soHieu}</span>
                <span className="pl">{r.loai || ''}</span>
                <span className="pn">{r.n}</span>
                <span>{lvl}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default PriorityList;
