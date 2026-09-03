import React, { useState } from 'react';
import { PriorityIndicator, NLILabelBadge } from '../components/shared/Badge';
import { History, Check, X, Edit3 } from 'lucide-react';

const ReviewService: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'review' | 'audit'>('review');
  const [editMode, setEditMode] = useState(false);
  const [editedText, setEditedText] = useState('Sinh viên năm cuối không được phép đăng ký học vượt quá 20 tín chỉ.');

  const queue = [
    { id: '1', title: 'Quy định quản lý điểm sinh viên', count: 2, priority: 'high' as const },
    { id: '2', title: 'Quyết định ban hành khung học phí', count: 1, priority: 'medium' as const },
  ];

  const auditTrail = [
    { time: '10:30 20/08/2026', user: 'Cán bộ Nguyễn Văn A', action: 'Sửa & duyệt câu #2', status: 'entailment' },
    { time: '09:15 19/08/2026', user: 'Cán bộ Trần Thị B', action: 'Duyệt giữ nguyên câu #1', status: 'contradiction' },
  ];

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', height: '100%', overflow: 'hidden' }}>
      <h1 className="title-h1" style={{ margin: 0 }}>Rà soát & Duyệt nội dung (Publish Gate)</h1>
      
      <div style={{ display: 'flex', gap: '2rem', flex: 1, overflow: 'hidden' }}>
        
        {/* Hàng đợi bên trái */}
        <div className="card" style={{ width: '350px', display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
          <h2 className="title-h2">Hàng đợi rà soát</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {queue.map((item, idx) => (
              <div key={idx} className={`hover-lift ${idx === 0 ? 'active' : ''}`} style={{ 
                padding: '1rem', 
                border: '1px solid var(--border-color)', 
                borderRadius: 'var(--radius-md)', 
                backgroundColor: idx === 0 ? 'var(--color-primary-light)' : 'var(--bg-surface)',
                borderColor: idx === 0 ? 'var(--color-primary)' : 'var(--border-color)',
                cursor: 'pointer'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 600, color: idx === 0 ? 'var(--color-primary-hover)' : 'var(--text-primary)', lineHeight: 1.4 }}>{item.title}</span>
                  <span className="badge badge-danger">{item.count} câu</span>
                </div>
                <PriorityIndicator level={item.priority} />
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
              Xử lý câu (1/2)
            </button>
            <button 
              onClick={() => setActiveTab('audit')}
              style={{ fontWeight: 600, fontSize: '1.125rem', color: activeTab === 'audit' ? 'var(--color-primary)' : 'var(--text-secondary)', borderBottom: activeTab === 'audit' ? '2px solid var(--color-primary)' : 'none', paddingBottom: '0.5rem' }}
            >
              <History size={18} style={{ display: 'inline', marginRight: '0.5rem' }}/> 
              Audit Trail
            </button>
            
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ width: '150px', height: '8px', backgroundColor: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: '50%', height: '100%', backgroundColor: 'var(--color-primary)' }}></div>
              </div>
              <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Tiến độ: 1/2</span>
            </div>
          </div>

          {activeTab === 'review' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', flex: 1, overflowY: 'auto' }}>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Nguyên bản */}
                <div>
                  <h3 className="title-h3">Đoạn văn gốc (Điều 12)</h3>
                  <div style={{ padding: '1.25rem', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', fontSize: '1rem', lineHeight: 1.6 }}>
                    Sinh viên năm cuối được phép đăng ký học vượt quá 20 tín chỉ trong một học kỳ để đảm bảo tiến độ tốt nghiệp, tuy nhiên phải được sự đồng ý của cố vấn học tập và Trưởng khoa.
                  </div>
                </div>

                {/* AI Sinh ra */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h3 className="title-h3" style={{ margin: 0 }}>Câu tóm tắt (AI sinh)</h3>
                    <NLILabelBadge label="contradiction" />
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
                        <button style={{ padding: '0.5rem 1.5rem', backgroundColor: 'var(--color-primary)', color: 'white', borderRadius: 'var(--radius-md)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Check size={18} /> Lưu & Revalidate
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-danger-light)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', fontSize: '1rem', lineHeight: 1.6, color: 'var(--color-danger-text)' }}>
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
                  <button className="hover-lift" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)', fontWeight: 600 }}>
                    <Check size={20} color="var(--color-success)" /> Duyệt giữ nguyên
                  </button>
                  <button className="hover-lift" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--color-danger)', color: 'var(--color-danger)', borderRadius: 'var(--radius-md)', fontWeight: 600 }}>
                    <X size={20} /> Loại bỏ câu
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ flex: 1, overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-main)', borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
                    <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Thời gian</th>
                    <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Người thực hiện</th>
                    <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Hành động</th>
                    <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Trạng thái NLI</th>
                  </tr>
                </thead>
                <tbody>
                  {auditTrail.map((log, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '1rem', fontSize: '0.875rem' }}>{log.time}</td>
                      <td style={{ padding: '1rem', fontWeight: 500 }}>{log.user}</td>
                      <td style={{ padding: '1rem' }}>{log.action}</td>
                      <td style={{ padding: '1rem' }}><NLILabelBadge label={log.status as any} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default ReviewService;
