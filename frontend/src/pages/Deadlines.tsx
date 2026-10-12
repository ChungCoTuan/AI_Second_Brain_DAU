import React, { useState, useMemo } from 'react';
import { useData } from '../context/DataContext';
import { fold, mucDo, nhanNgay, conLaiNode, fmtDate } from '../utils';
import { useDetail } from '../context/DetailContext';
import { Filter, RotateCcw, Search } from 'lucide-react';

const Deadlines: React.FC = () => {
  const { openDetail } = useDetail();
  const { data, markAsRead, readDeadlines } = useData();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterChuThe, setFilterChuThe] = useState('all');
  const [filterLoai, setFilterLoai] = useState('all');
  const [expandedDocs, setExpandedDocs] = useState<Record<string, boolean>>({});

  const moc = useMemo(() => {
    const arr: any[] = [];
    (data.hanChot || []).forEach((n: any) => {
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
    (data.chuaHieuLuc || []).forEach((c: any) => {
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
  }, [data.hanChot, data.chuaHieuLuc]);

  const laTruong = (m: any) => (m.chuThe || 'trường') === 'trường';
  const qua = moc.filter((m) => mucDo(m.ngay) === 'qua' && laTruong(m)).length;
  const quaK = moc.filter((m) => mucDo(m.ngay) === 'qua' && !laTruong(m)).length;
  const gan = moc.filter((m) => mucDo(m.ngay) === 'gan' && laTruong(m)).length;
  const lap = moc.filter((m) => mucDo(m.ngay) === 'lap').length;
  const khac = moc.filter((m) => !laTruong(m)).length;

  const availableTypes = useMemo(() => {
    const types = new Set<string>();
    moc.forEach((m) => {
      if (m.loai && m.loai.trim()) types.add(m.loai.trim());
    });
    return Array.from(types).sort();
  }, [moc]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setFilterStatus('all');
    setFilterChuThe('all');
    setFilterLoai('all');
  };

  const hasActiveFilters =
    searchTerm !== '' ||
    filterStatus !== 'all' ||
    filterChuThe !== 'all' ||
    filterLoai !== 'all';

  const filteredMoc = useMemo(() => {
    const q = fold(searchTerm.trim());
    let kq = moc.filter((m) => {
      // 1. Trạng thái hạn
      if (filterStatus !== 'all' && mucDo(m.ngay) !== filterStatus) return false;

      // 2. Chủ thể
      if (filterChuThe === 'truong' && !laTruong(m)) return false;
      if (filterChuThe === 'khac' && laTruong(m)) return false;

      // 3. Loại mốc
      if (filterLoai !== 'all' && (m.loai || '').trim() !== filterLoai) return false;

      // 4. Tìm kiếm từ khóa
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
  }, [moc, searchTerm, filterStatus, filterChuThe, filterLoai]);

  const hl = (s: string, q: string) => {
    if (!q || !s) return s;
    const lowerS = fold(s);
    if (!lowerS.includes(q)) return s;
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

        {/* Card Bộ lọc */}
        <div
          style={{
            background: '#fff',
            border: '1px solid var(--line, #e2e8f0)',
            borderRadius: '12px',
            padding: '16px 20px',
            marginTop: '20px',
            marginBottom: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, color: 'var(--ink, #1e293b)', fontSize: '15px' }}>
              <Filter size={18} style={{ color: 'var(--red, #b91c1c)' }} />
              <span>Bộ lọc tra cứu hạn chót & mốc thời gian</span>
            </div>
            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '13px',
                  color: 'var(--red, #b91c1c)',
                  background: '#fee2e2',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                <RotateCcw size={14} /> Đặt lại bộ lọc
              </button>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {/* Ô tìm kiếm */}
            <div style={{ position: 'relative' }}>
              <Search
                size={16}
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--muted, #64748b)'
                }}
              />
              <input
                id="hanTim"
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 12px 0 36px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  boxSizing: 'border-box'
                }}
                type="search"
                placeholder="Lọc: quy chế, công khai, 56/2026..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Trạng thái hạn */}
            <div>
              <select
                id="hanLoc"
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 28px 0 12px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  background: '#fff',
                  color: 'var(--ink, #1e293b)',
                  boxSizing: 'border-box'
                }}
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="all">Tất cả mốc</option>
                <option value="qua">Đã qua hạn</option>
                <option value="gan">Còn dưới 120 ngày</option>
                <option value="sau">Còn xa</option>
                <option value="lap">Hạn lặp hằng năm</option>
              </select>
            </div>

            {/* Chủ thể */}
            <div>
              <select
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 28px 0 12px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  background: '#fff',
                  color: 'var(--ink, #1e293b)',
                  boxSizing: 'border-box'
                }}
                value={filterChuThe}
                onChange={(e) => setFilterChuThe(e.target.value)}
              >
                <option value="all">Tất cả chủ thể</option>
                <option value="truong">Việc của trường</option>
                <option value="khac">Việc của cơ quan khác</option>
              </select>
            </div>

            {/* Loại mốc */}
            <div>
              <select
                className="inp"
                style={{
                  width: '100%',
                  padding: '0 28px 0 12px',
                  height: '42px',
                  fontSize: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--line, #cbd5e1)',
                  background: '#fff',
                  color: 'var(--ink, #1e293b)',
                  boxSizing: 'border-box'
                }}
                value={filterLoai}
                onChange={(e) => setFilterLoai(e.target.value)}
              >
                <option value="all">Tất cả loại việc</option>
                {availableTypes.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Thanh tổng kết đếm số lượng */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: '12px',
              paddingTop: '10px',
              borderTop: '1px solid var(--line, #f1f5f9)',
              fontSize: '13px',
              color: 'var(--muted, #64748b)'
            }}
          >
            <div>
              Hiển thị: <b style={{ color: 'var(--ink, #0f172a)' }}>{filteredMoc.length}</b> / {moc.length} mốc
              {hasActiveFilters && <span style={{ color: 'var(--red, #b91c1c)', marginLeft: '6px', fontWeight: 600 }}>(đang lọc)</span>}
            </div>
            {hasActiveFilters && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {searchTerm && (
                  <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                    "{searchTerm}"
                  </span>
                )}
                {filterStatus !== 'all' && (
                  <span style={{ background: '#fef3c7', color: '#92400e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterStatus === 'qua' ? 'Đã qua hạn' : filterStatus === 'gan' ? 'Dưới 120 ngày' : filterStatus === 'sau' ? 'Còn xa' : 'Hạn lặp'}
                  </span>
                )}
                {filterChuThe !== 'all' && (
                  <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterChuThe === 'truong' ? 'Việc của trường' : 'Cơ quan khác'}
                  </span>
                )}
                {filterLoai !== 'all' && (
                  <span style={{ background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {filterLoai}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {filteredMoc.length === 0 && (
          <div style={{ padding: '40px 20px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px dashed var(--line)', marginBottom: '20px' }}>
            <p style={{ color: 'var(--muted)', fontSize: '15px', margin: '0 0 12px 0' }}>Không tìm thấy mốc thời gian nào khớp với điều kiện lọc.</p>
            <button
              onClick={handleResetFilters}
              style={{
                padding: '8px 16px',
                background: 'var(--blue, #2563eb)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '13px'
              }}
            >
              Xóa bộ lọc để xem tất cả
            </button>
          </div>
        )}

        <div className="tl" id="hanList">
          {filteredMoc.length > 0 ? (
              filteredMoc.map((m, idx) => {
                const ngoai = (m.chuThe || 'trường') !== 'trường';
                const c = mucDo(m.ngay);
                const isUnread = !readDeadlines.includes(m.vb);
                return (
                  <div
                    key={idx}
                    className={`tlr ${ngoai ? '' : c} ${isUnread ? 'unread-item' : ''}`}
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
                    <div className="m" onClick={() => {
                      openDetail('bo:' + (m.docId || m.vb));
                      markAsRead('deadline', m.vb);
                    }} style={{ cursor: 'pointer' }}>
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
                    <>
                      <span 
                        onClick={(e) => {
                          e.stopPropagation();
                          setExpandedDocs(prev => ({ ...prev, [idx]: !prev[idx] }));
                        }} 
                        style={{ color: 'var(--primary)', cursor: 'pointer', fontSize: '13px', fontWeight: 600, display: 'inline-block', marginTop: '6px' }}
                      >
                        {expandedDocs[idx] ? 'Ẩn nguyên văn' : 'Xem nguyên văn'}
                      </span>
                      
                      {expandedDocs[idx] && (
                        <div className="ev-q" style={{ marginTop: '8px' }}>
                          <span className="lbl" style={{ textTransform: 'uppercase', color: 'var(--red)' }}>Nguyên văn điều khoản</span>
                          {m.nguon}
                        </div>
                      )}
                    </>
                  )}
                </div>
              );
            })
          ) : (
            <div className="empty">Không có mốc nào khớp.</div>
          )}
        </div>

        <div className="warnbox" id="hanNote">
          <b>Hai lưu ý khi đọc mục này.</b> Thứ nhất, {data.diemMu?.mocTinhRa || 0} mốc có ngày cụ thể là do{' '}
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
