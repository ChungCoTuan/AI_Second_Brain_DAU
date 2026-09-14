import React, { useState, useEffect } from 'react';
import { Check, X, AlertTriangle } from 'lucide-react';
import { useData } from '../context/DataContext';

interface ReviewItem {
  id: number;
  document_id: number;
  vb: string;
  dieu: string;
  nguon: string;
  status: string;
  // Nghĩa vụ fields
  chuThe?: string;
  noiDung?: string;
  hanChot?: string;
  loai?: string;
  // Con số chốt fields
  giaTri?: string;
  yNghia?: string;
  // NLI & Tóm tắt
  tom_tat?: string;
  nli_label?: string;
}

const ReviewQueue: React.FC = () => {
  const { refreshData } = useData();
  const [nghiaVuList, setNghiaVuList] = useState<ReviewItem[]>([]);
  const [conSoChotList, setConSoChotList] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPendingData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/review/pending');
      const data = await response.json();
      setNghiaVuList(data.nghiaVu || []);
      setConSoChotList(data.conSoChot || []);
    } catch (error) {
      console.error("Lỗi khi tải dữ liệu chờ duyệt:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingData();
  }, []);

  const handlePublish = async (itemType: string, id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/review/${itemType}/${id}/publish`, {
        method: 'PUT',
      });
      if (response.ok) {
        if (itemType === 'nghiaVu') {
          setNghiaVuList(prev => prev.filter(item => item.id !== id));
        } else {
          setConSoChotList(prev => prev.filter(item => item.id !== id));
        }
        // Cập nhật lại dữ liệu gốc của App để tab "Việc phải làm" hiển thị data vừa duyệt
        refreshData();
      }
    } catch (error) {
      console.error("Lỗi khi duyệt:", error);
    }
  };

  const handleReject = async (itemType: string, id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/review/${itemType}/${id}/reject`, {
        method: 'PUT',
      });
      if (response.ok) {
        if (itemType === 'nghiaVu') {
          setNghiaVuList(prev => prev.filter(item => item.id !== id));
        } else {
          setConSoChotList(prev => prev.filter(item => item.id !== id));
        }
      }
    } catch (error) {
      console.error("Lỗi khi từ chối:", error);
    }
  };

  if (loading) {
    return (
      <section id="ra-soat">
        <div className="wrap">
          <h2>Cổng Duyệt Văn Bản (Publish Gate)</h2>
          <p className="sub">Đang tải danh sách chờ duyệt từ mô hình AI...</p>
        </div>
      </section>
    );
  }

  const hasItems = nghiaVuList.length > 0 || conSoChotList.length > 0;

  return (
    <section id="ra-soat">
      <div className="wrap">
        <h2>Cổng Duyệt Văn Bản (Publish Gate)</h2>
        <p className="sub">
          <AlertTriangle size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '4px', color: 'var(--amber)' }}/>
          Rà soát kết quả bóc tách của mô hình AI trước khi Publish để ngăn chặn Ảo giác (Hallucination).
        </p>

        {!hasItems && (
          <div style={{ padding: '40px', textAlign: 'center', backgroundColor: 'var(--card-bg)', borderRadius: '12px', border: '1px dashed var(--border)', marginTop: '20px' }}>
            <h3 style={{ color: 'var(--green)' }}>Tuyệt vời!</h3>
            <p className="sub">Không còn văn bản nào đang chờ duyệt trong hàng đợi.</p>
          </div>
        )}

        {nghiaVuList.length > 0 && (
          <div style={{ marginTop: '30px' }}>
            <h3>Nghĩa vụ chờ duyệt ({nghiaVuList.length})</h3>
            <div className="cards" style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
              {nghiaVuList.map(nv => (
                <div key={`nv-${nv.id}`} className="card" style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
                  {/* Cột trái: AI Bóc tách */}
                  <div style={{ flex: 1, paddingRight: '20px', borderRight: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                      <span className="badge new">Kết quả bóc tách</span>
                      <span className="doc">{nv.vb} - {nv.dieu}</span>
                    </div>
                    <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                      <div style={{ marginBottom: '8px' }}><b>Chủ thể:</b> <span style={{ color: 'var(--primary)' }}>{nv.chuThe}</span></div>
                      <div style={{ marginBottom: '8px' }}><b>Hành động:</b> {nv.noiDung}</div>
                      <div style={{ marginBottom: '8px' }}><b>Hạn chót:</b> <span style={{ color: 'var(--red)' }}>{nv.hanChot || 'Không quy định'}</span></div>
                    </div>
                  </div>
                  
                  {/* Cột phải: Văn bản gốc & Tóm tắt AI */}
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between' }}>
                      <span className="badge" style={{ background: 'var(--hover)', color: 'var(--text)' }}>Nguyên bản gốc</span>
                      {nv.nli_label === 'entailment' && <span className="badge" style={{ background: 'var(--green)', color: 'white' }}>🟢 An toàn (Entailment)</span>}
                      {nv.nli_label === 'contradiction' && <span className="badge" style={{ background: 'var(--red)', color: 'white' }}>🔴 Mâu thuẫn (Contradiction)</span>}
                      {nv.nli_label === 'neutral' && <span className="badge" style={{ background: 'var(--amber)', color: 'white' }}>🟠 Chung chung (Neutral)</span>}
                    </div>
                    
                    {nv.tom_tat && (
                      <div style={{ marginBottom: '12px', padding: '10px', backgroundColor: 'var(--surface-color, #f8f9fa)', borderLeft: '3px solid var(--primary)' }}>
                        <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--primary)', marginBottom: '4px' }}>AI Tóm tắt:</div>
                        <div style={{ fontSize: '13px' }}>{nv.tom_tat}</div>
                      </div>
                    )}
                    
                    <div style={{ fontSize: '13px', lineHeight: '1.6', color: 'var(--muted)', fontStyle: 'italic', flex: 1, backgroundColor: 'var(--app-bg)', padding: '12px', borderRadius: '8px', maxHeight: '150px', overflowY: 'auto' }}>
                      "{nv.nguon}"
                    </div>
                    
                    {/* Hành động */}
                    <div style={{ display: 'flex', gap: '10px', marginTop: '16px', justifyContent: 'flex-end' }}>
                      <button 
                        className="btn" 
                        style={{ background: 'var(--red)', color: 'white', display: 'flex', alignItems: 'center', gap: '6px' }}
                        onClick={() => handleReject('nghiaVu', nv.id)}
                      >
                        <X size={16} /> Từ chối
                      </button>
                      <button 
                        className="btn" 
                        style={{ background: 'var(--green)', color: 'white', display: 'flex', alignItems: 'center', gap: '6px' }}
                        onClick={() => handlePublish('nghiaVu', nv.id)}
                      >
                        <Check size={16} /> Duyệt & Publish
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {conSoChotList.length > 0 && (
          <div style={{ marginTop: '40px' }}>
            <h3>Con số chốt chờ duyệt ({conSoChotList.length})</h3>
            <div className="cards" style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
              {conSoChotList.map(cs => (
                <div key={`cs-${cs.id}`} className="card" style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
                  {/* Cột trái: AI Bóc tách */}
                  <div style={{ flex: 1, paddingRight: '20px', borderRight: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                      <span className="badge warning">Kết quả bóc tách</span>
                      <span className="doc">{cs.vb} - {cs.dieu}</span>
                    </div>
                    <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                      <div style={{ marginBottom: '8px' }}><b>Giá trị:</b> <span style={{ color: 'var(--amber)', fontWeight: 'bold', fontSize: '16px' }}>{cs.giaTri}</span></div>
                      <div style={{ marginBottom: '8px' }}><b>Ý nghĩa:</b> {cs.yNghia}</div>
                    </div>
                  </div>
                  
                  {/* Cột phải: Văn bản gốc & Tóm tắt AI */}
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between' }}>
                      <span className="badge" style={{ background: 'var(--hover)', color: 'var(--text)' }}>Nguyên bản gốc</span>
                      {cs.nli_label === 'entailment' && <span className="badge" style={{ background: 'var(--green)', color: 'white' }}>🟢 An toàn (Entailment)</span>}
                      {cs.nli_label === 'contradiction' && <span className="badge" style={{ background: 'var(--red)', color: 'white' }}>🔴 Mâu thuẫn (Contradiction)</span>}
                      {cs.nli_label === 'neutral' && <span className="badge" style={{ background: 'var(--amber)', color: 'white' }}>🟠 Chung chung (Neutral)</span>}
                    </div>
                    
                    {cs.tom_tat && (
                      <div style={{ marginBottom: '12px', padding: '10px', backgroundColor: 'var(--surface-color, #f8f9fa)', borderLeft: '3px solid var(--primary)' }}>
                        <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--primary)', marginBottom: '4px' }}>AI Tóm tắt:</div>
                        <div style={{ fontSize: '13px' }}>{cs.tom_tat}</div>
                      </div>
                    )}
                    
                    <div style={{ fontSize: '13px', lineHeight: '1.6', color: 'var(--muted)', fontStyle: 'italic', flex: 1, backgroundColor: 'var(--app-bg)', padding: '12px', borderRadius: '8px', maxHeight: '150px', overflowY: 'auto' }}>
                      "{cs.nguon}"
                    </div>
                    
                    {/* Hành động */}
                    <div style={{ display: 'flex', gap: '10px', marginTop: '16px', justifyContent: 'flex-end' }}>
                      <button 
                        className="btn" 
                        style={{ background: 'var(--red)', color: 'white', display: 'flex', alignItems: 'center', gap: '6px' }}
                        onClick={() => handleReject('conSoChot', cs.id)}
                      >
                        <X size={16} /> Từ chối
                      </button>
                      <button 
                        className="btn" 
                        style={{ background: 'var(--green)', color: 'white', display: 'flex', alignItems: 'center', gap: '6px' }}
                        onClick={() => handlePublish('conSoChot', cs.id)}
                      >
                        <Check size={16} /> Duyệt & Publish
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default ReviewQueue;
