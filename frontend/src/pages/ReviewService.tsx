import React, { useState, useEffect } from 'react';
import { PriorityIndicator, NLILabelBadge } from '../components/shared/Badge';
import { History, Check, X, Edit3 } from 'lucide-react';
import { fetchReviewItems, updateDocumentStatus, DocumentItem } from '../services/api';

interface FaithfulnessSample {
  sample_id: string;
  doc_id: string;
  chunk_id: string;
  premise: string;
  hypothesis: string;
  label: 'entailment' | 'neutral' | 'contradiction';
  notes?: string;
}

const ReviewService: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'review' | 'audit'>('review');
  const [editMode, setEditMode] = useState(false);
  const [pendingDocs, setPendingDocs] = useState<DocumentItem[]>([]);
  const [samples, setSamples] = useState<FaithfulnessSample[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [editedText, setEditedText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await fetchReviewItems();
        setPendingDocs(data.pending_documents || []);
        setSamples(data.faithfulness_samples || []);
        if (data.faithfulness_samples && data.faithfulness_samples.length > 0) {
          setEditedText(data.faithfulness_samples[0].hypothesis);
        }
      } catch (err) {
        console.error("Lỗi khi tải dữ liệu rà soát:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const currentSample = samples[selectedIndex];

  const handleSelectSample = (idx: number) => {
    setSelectedIndex(idx);
    setEditMode(false);
    if (samples[idx]) {
      setEditedText(samples[idx].hypothesis);
    }
  };

  const handleApproveDocument = async (docId: string) => {
    try {
      await updateDocumentStatus(docId, 'PUBLISHED');
      setPendingDocs(prev => prev.filter(d => d.doc_id !== docId));
      alert(`Đã duyệt chuyển văn bản [${docId}] sang trạng thái PUBLISHED!`);
    } catch (err) {
      console.error(err);
      alert('Không thể cập nhật trạng thái văn bản.');
    }
  };

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', height: '100%', overflow: 'hidden' }}>
      <h1 className="title-h1" style={{ margin: 0 }}>Rà soát & Duyệt nội dung (Publish Gate FR-08)</h1>
      
      <div style={{ display: 'flex', gap: '2rem', flex: 1, overflow: 'hidden' }}>
        
        {/* Hàng đợi bên trái */}
        <div className="card" style={{ width: '380px', display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
          <h2 className="title-h2">Văn bản chờ duyệt ({pendingDocs.length})</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {loading ? (
              <p>Đang tải danh sách rà soát...</p>
            ) : pendingDocs.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>Không có văn bản bị kẹt PENDING_REVIEW.</p>
            ) : (
              pendingDocs.map((item, idx) => (
                <div key={item.doc_id} className="hover-lift" style={{ 
                  padding: '1rem', 
                  border: '1px solid var(--border-color)', 
                  borderRadius: 'var(--radius-md)', 
                  backgroundColor: 'var(--bg-surface)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem'
                }}>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{item.ten_van_ban}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="badge badge-warning">PENDING_REVIEW</span>
                    <button 
                      onClick={() => handleApproveDocument(item.doc_id)}
                      style={{ padding: '0.25rem 0.75rem', backgroundColor: 'var(--color-primary)', color: 'white', borderRadius: 'var(--radius-md)', fontSize: '0.8rem', fontWeight: 600 }}
                    >
                      Duyệt Publish
                    </button>
                  </div>
                </div>
              ))
            )}

            <h3 className="title-h3" style={{ marginTop: '1rem' }}>Mẫu Faithfulness NLI ({samples.length})</h3>
            {samples.slice(0, 10).map((sample, idx) => (
              <div 
                key={sample.sample_id} 
                className={`hover-lift ${idx === selectedIndex ? 'active' : ''}`}
                onClick={() => handleSelectSample(idx)}
                style={{ 
                  padding: '0.75rem 1rem', 
                  border: '1px solid var(--border-color)', 
                  borderRadius: 'var(--radius-md)', 
                  backgroundColor: idx === selectedIndex ? 'var(--color-primary-light)' : 'var(--bg-surface)',
                  cursor: 'pointer'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{sample.sample_id}</span>
                  <NLILabelBadge label={sample.label} />
                </div>
                <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {sample.hypothesis}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Khung xử lý bên phải */}
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', gap: '2rem' }}>
            <button 
              onClick={() => setActiveTab('review')}
              style={{ fontWeight: 600, fontSize: '1.125rem', color: activeTab === 'review' ? 'var(--color-primary)' : 'var(--text-secondary)', borderBottom: activeTab === 'review' ? '2px solid var(--color-primary)' : 'none', paddingBottom: '0.5rem' }}
            >
              Xử lý mẫu ({selectedIndex + 1}/{samples.length})
            </button>
            <button 
              onClick={() => setActiveTab('audit')}
              style={{ fontWeight: 600, fontSize: '1.125rem', color: activeTab === 'audit' ? 'var(--color-primary)' : 'var(--text-secondary)', borderBottom: activeTab === 'audit' ? '2px solid var(--color-primary)' : 'none', paddingBottom: '0.5rem' }}
            >
              <History size={18} style={{ display: 'inline', marginRight: '0.5rem' }}/> 
              Audit Trail
            </button>
          </div>

          {activeTab === 'review' && currentSample ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', flex: 1, overflowY: 'auto' }}>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Nguyên bản */}
                <div>
                  <h3 className="title-h3">Đoạn văn bản gốc (Premise)</h3>
                  <div style={{ padding: '1.25rem', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', fontSize: '1rem', lineHeight: 1.6 }}>
                    {currentSample.premise}
                  </div>
                </div>

                {/* Hypotheses */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h3 className="title-h3" style={{ margin: 0 }}>Giả thuyết tóm tắt (Hypothesis)</h3>
                    <NLILabelBadge label={currentSample.label} />
                  </div>
                  
                  {editMode ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <textarea 
                        value={editedText}
                        onChange={(e) => setEditedText(e.target.value)}
                        style={{ width: '100%', padding: '1rem', borderRadius: 'var(--radius-md)', border: '2px solid var(--color-primary)', outline: 'none', resize: 'vertical', minHeight: '120px', fontSize: '1rem', lineHeight: 1.6, fontFamily: 'inherit' }}
                      />
                      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                        <button onClick={() => setEditMode(false)} style={{ padding: '0.5rem 1rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Hủy</button>
                        <button onClick={() => setEditMode(false)} style={{ padding: '0.5rem 1.5rem', backgroundColor: 'var(--color-primary)', color: 'white', borderRadius: 'var(--radius-md)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Check size={18} /> Lưu chỉnh sửa
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ 
                      padding: '1.25rem', 
                      backgroundColor: currentSample.label === 'contradiction' ? 'var(--color-danger-light)' : 'var(--bg-surface)', 
                      border: currentSample.label === 'contradiction' ? '1px solid var(--color-danger)' : '1px solid var(--border-color)', 
                      borderRadius: 'var(--radius-md)', 
                      fontSize: '1rem', 
                      lineHeight: 1.6, 
                      color: currentSample.label === 'contradiction' ? 'var(--color-danger-text)' : 'var(--text-primary)' 
                    }}>
                      {editedText}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              {!editMode && (
                <div style={{ marginTop: 'auto', display: 'flex', gap: '1rem', padding: '1.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', justifyContent: 'center' }}>
                  <button className="hover-lift" onClick={() => setEditMode(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', backgroundColor: 'var(--color-primary)', color: 'white', borderRadius: 'var(--radius-md)', fontWeight: 600 }}>
                    <Edit3 size={20} /> Sửa câu này
                  </button>
                  <button className="hover-lift" onClick={() => handleSelectSample((selectedIndex + 1) % samples.length)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)', fontWeight: 600 }}>
                    <Check size={20} color="var(--color-success)" /> Chuyển mẫu tiếp theo
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ flex: 1, padding: '1rem' }}>
              <p>Hệ thống hỗ trợ lưu log kiểm duyệt Faithfulness Audit Trail cho các mẫu NLI 3 nhãn.</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default ReviewService;
