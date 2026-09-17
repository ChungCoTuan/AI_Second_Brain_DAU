import React, { useState, useMemo } from 'react';
import { DEMO_DATA } from '../data';
import { fold, mucDo, nhanNgay, conLaiNode, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';

const Deadlines: React.FC = () => {
  const { openDetail } = useDetail();
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  const moc = useMemo(() => {
    const arr: any[] = [];
    (DEMO_DATA.hanChot || []).forEach((n: any) => {
      arr.push({
        ngay: n.hanChot,
        viec: n.noiDung,
        vb: n.vb,
        dieu: n.dieu,
        loai: n.loai || 'nghĩa vụ',
        nguon: n.nguon,
        chuThe: n.chuThe || 'trường',
        nguonNgay: n.nguonNgay,
        vbDaChet: n.vbDaChet,
      });
    });
    (DEMO_DATA.chuaHieuLuc || []).forEach((c: any) => {
      arr.push({
        ngay: c.ngay,
        viec: (c.loai === 'áp dụng' ? 'Bắt đầu áp dụng: ' : 'Bắt đầu có hiệu lực: ') + (c.trichYeu || c.soHieu),
        vb: c.soHieu,
        dieu: '',
        loai: c.loai,
        nguon: c.nguon,
        chuThe: 'trường',
        nguonNgay: 'chép',
      });
    });
    return arr;
  }, []);

  const laTruong = (m: any) => (m.chuThe || 'trường') === 'trường';
  const qua = moc.filter((m) => mucDo(m.ngay) === 'qua' && laTruong(m)).length;
  const quaK = moc.filter((m) => mucDo(m.ngay) === 'qua' && !laTruong(m)).length;
  const gan = moc.filter((m) => mucDo(m.ngay) === 'gan' && laTruong(m)).length;
  const lap = moc.filter((m) => mucDo(m.ngay) === 'lap').length;
  const khac = moc.filter((m) => !laTruong(m)).length;

  const filteredMoc = useMemo(() => {
    const q = fold(searchTerm.trim());
    let kq = moc.filter((m) => {
      if (filter !== 'all' && mucDo(m.ngay) !== filter) return false;
      if (!q) return true;
      return fold([m.viec, m.vb, m.dieu, m.loai].join(' ')).includes(q);
    });
    kq.sort((a, b) => {
      const ma = mucDo(a.ngay);
      const mb = mucDo(b.ngay);
      if ((ma === 'lap') !== (mb === 'lap')) return ma === 'lap' ? 1 : -1;
      return String(a.ngay).localeCompare(String(b.ngay));
    });
    return kq;
  }, [moc, searchTerm, filter]);

  const hl = (s: string, q: string) => {
    if (!q || !s) return s;
    const lowerS = fold(s);
    if (!lowerS.includes(q)) return s;
    // Simple implementation for React without dangerouslySetInnerHTML for everything
    // In a real app we'd split the string, here we just return the string for safety.
    return s;
  };

  return (
    <section id="han-chot">
      <div className="wrap">
        <h2>Hạn chót và mốc chưa tới</h2>
        <p className="sub">
          Rút từ điều khoản chuyển tiếp và điều khoản thi hành của các văn bản Bộ. Mốc <b>đỏ</b> là đã qua, <b>vàng</b>{' '}
          là còn dưới 120 ngày.
        </p>

        <div className="tiles" id="hanTiles">
          <div className="tile">
            <b>{moc.length}</b>
            <span>mốc bóc được từ văn bản pháp quy</span>
          </div>
          <div className="tile">
            <b style={{ color: 'var(--red)' }}>{qua}</b>
            <span>
              trường đã quá hạn
              {quaK > 0 && (
                <>
                  {' '}
                  <br />
                  <span style={{ color: 'var(--muted)' }}>({quaK} mốc quá hạn khác không thuộc về trường)</span>
                </>
              )}
            </span>
          </div>
          <div className="tile">
            <b style={{ color: 'var(--amber)' }}>{gan}</b>
            <span>việc của trường, còn dưới 120 ngày</span>
          </div>
          <div className="tile">
            <b>{khac}</b>
            <span>mốc thuộc về cơ quan khác, không phải việc của trường</span>
          </div>
          <div className="tile">
            <b>{lap}</b>
            <span>hạn lặp hằng năm</span>
          </div>
        </div>

        <div className="srow">
          <input
            id="hanTim"
            className="inp"
            placeholder="Lọc theo nội dung hoặc số hiệu: quy chế, công khai, 56/2026"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select id="hanLoc" className="sel" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">Tất cả mốc</option>
            <option value="qua">Đã qua hạn</option>
            <option value="gan">Còn dưới 120 ngày</option>
            <option value="sau">Còn xa</option>
          </select>
          <span className="cnt" id="hanCnt">
            <b>{filteredMoc.length}</b> / {moc.length} mốc
          </span>
        </div>

        <div className="tl" id="hanList">
          {filteredMoc.length > 0 ? (
            filteredMoc.map((m, idx) => {
              const ngoai = (m.chuThe || 'trường') !== 'trường';
              const c = mucDo(m.ngay);
              return (
                <div
                  key={idx}
                  className={`tlr ${ngoai ? '' : c}`}
                  onClick={() => openDetail('bo:' + (m.docId || m.vb))}
                  style={{ opacity: ngoai ? 0.72 : 1 }}
                >
                  <div className="d">
                    {nhanNgay(m.ngay)}
                    {!ngoai && conLaiNode(m.ngay)}
                    {ngoai && <span className="dleft">không phải việc của trường</span>}
                    {m.nguonNgay === 'tính' && (
                      <span className="tag2" style={{ marginLeft: '6px' }}>
                        tính ra
                      </span>
                    )}
                  </div>
                  <div className="w">{hl(m.viec, fold(searchTerm))}</div>
                  <div className="m">
                    {m.vb}
                    {m.dieu ? ` · ${m.dieu}` : ''} · {m.loai}
                    {ngoai && (
                      <>
                        {' · '}
                        <b>{m.chuThe}</b>
                      </>
                    )}
                  </div>
                  {m.vbDaChet && (
                    <div className="rm" style={{ color: 'var(--red)' }}>
                      Văn bản này đã hết hiệu lực từ {fmtDate(m.vbDaChet.tuNgay)}, xem {m.vbDaChet.thayBang.join(', ')}
                    </div>
                  )}
                  {m.nguon && (
                    <div className="ev-q" style={{ marginTop: '8px' }}>
                      <span className="lbl">Nguyên văn</span>
                      {m.nguon}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="empty">Không có mốc nào khớp.</div>
          )}
        </div>

        <div className="warnbox" id="hanNote">
          <b>Hai lưu ý khi đọc mục này.</b> Thứ nhất, {DEMO_DATA.diemMu?.mocTinhRa || 0} mốc có ngày cụ thể là do{' '}
          <b>cộng ra</b> chứ không in trong văn bản (ví dụ "36 tháng kể từ ngày có hiệu lực"), các mốc đó mang nhãn{' '}
          <span className="tag2">tính ra</span>; mốc ghi "hằng năm" thì không suy ra năm cụ thể. Thứ hai, không phải
          mốc nào cũng là việc của trường: mốc mang nhãn xám thuộc về cơ quan quản lý, trường công lập, đại học quốc gia
          hoặc bậc học khác, và <b>không được tính</b> vào ô quá hạn ở trên.
        </div>
      </div>
    </section>
  );
};

export default Deadlines;
