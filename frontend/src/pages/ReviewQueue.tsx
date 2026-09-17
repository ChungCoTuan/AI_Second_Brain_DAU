import React, { useEffect, useState } from 'react';
import {
  fetchReviewQueue,
  submitReviewAction,
  fetchAuditLogs,
  type ReviewItemData,
  type AuditLogData,
} from '../services/api';
import { useDetail } from '../context/DetailContext';

const ReviewQueue: React.FC = () => {
  const { openDetail } = useDetail();
  const [activeTab, setActiveTab] = useState<'queue' | 'audit'>('queue');

  // Queue state
  const [items, setItems] = useState<ReviewItemData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Edit modal state
  const [editingItem, setEditingItem] = useState<ReviewItemData | null>(null);
  const [editText, setEditText] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Audit logs state
  const [auditLogs, setAuditLogs] = useState<AuditLogData[]>([]);
  const [loadingLogs, setLoadingLogs] = useState<boolean>(false);

  const loadQueueData = async () => {
    setLoading(true);
    const res = await fetchReviewQueue({
      status: 'pending',
      priority: filterPriority === 'all' ? undefined : filterPriority,
    });
    setItems(res.items || []);
    setLoading(false);
  };

  const loadAuditData = async () => {
    setLoadingLogs(true);
    const logs = await fetchAuditLogs(50);
    setAuditLogs(logs);
    setLoadingLogs(false);
  };

  useEffect(() => {
    if (activeTab === 'queue') {
      loadQueueData();
    } else {
      loadAuditData();
    }
  }, [activeTab, filterPriority]);

  const handleApprove = async (item: ReviewItemData) => {
    setStatusMsg(null);
    const res = await submitReviewAction(item.review_item_id, 'approve');
    if (res.success) {
      setStatusMsg({ type: 'success', text: `Đã duyệt giữ nguyên câu cho văn bản [${item.document_id}]` });
      loadQueueData();
    } else {
      setStatusMsg({ type: 'error', text: res.message || 'Lỗi duyệt item' });
    }
  };

  const handleReject = async (item: ReviewItemData) => {
    setStatusMsg(null);
    const res = await submitReviewAction(item.review_item_id, 'reject');
    if (res.success) {
      setStatusMsg({ type: 'success', text: `Đã loại bỏ câu bị gắn cờ` });
      loadQueueData();
    } else {
      setStatusMsg({ type: 'error', text: res.message || 'Lỗi loại bỏ item' });
    }
  };

  const openEditModal = (item: ReviewItemData) => {
    setEditingItem(item);
    setEditText(item.cau_ai_sinh);
  };

  const handleConfirmEdit = async () => {
    if (!editingItem || !editText.trim()) return;
    setIsSubmitting(true);
    setStatusMsg(null);

    const res = await submitReviewAction(editingItem.review_item_id, 'edit', editText);
    setIsSubmitting(false);

    if (res.success) {
      setStatusMsg({
        type: 'success',
        text: `Đã sửa & re-validate NLI! Nhãn NLI mới: ${res.data?.new_nli_label || 'entailment'}. Trạng thái VB: ${res.data?.document_publish_status || 'published'}`,
      });
      setEditingItem(null);
      loadQueueData();
    } else {
      setStatusMsg({ type: 'error', text: res.message || 'Lỗi chỉnh sửa' });
    }
  };

  return (
    <section id="ra-soat">
      <div className="wrap">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h2>Quy trình Rà soát & Phê duyệt (Human-in-the-Loop — UC-04)</h2>
            <p className="sub">
              Duyệt các câu bị NLI chấm mâu thuẫn (`contradiction`) hoặc không đủ căn cứ (`neutral`). Văn bản chỉ được xuất bản sau khi rà soát xong.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className={`chip ${activeTab === 'queue' ? 'active' : ''}`}
              onClick={() => setActiveTab('queue')}
              style={{ cursor: 'pointer', padding: '8px 16px', fontWeight: 600 }}
            >
              📋 Hàng đợi Rà soát ({items.length})
            </button>
            <button
              className={`chip ${activeTab === 'audit' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit')}
              style={{ cursor: 'pointer', padding: '8px 16px', fontWeight: 600 }}
            >
              📜 Lịch sử Audit Trail
            </button>
          </div>
        </div>

        {statusMsg && (
          <div
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '16px',
              background: statusMsg.type === 'success' ? '#f0fdf4' : '#fef2f2',
              border: `1px solid ${statusMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
              color: statusMsg.type === 'success' ? '#166534' : '#991b1b',
              fontWeight: 500,
            }}
          >
            {statusMsg.text}
          </div>
        )}

        {/* TAB 1: REVIEW QUEUE */}
        {activeTab === 'queue' && (
          <>
            <div className="filterbar" style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--muted)', marginRight: '8px' }}>
                Lọc mức độ ưu tiên:
              </span>
              {[
                { id: 'all', label: 'Tất cả' },
                { id: 'high', label: '🔴 Cao (Contradiction)' },
                { id: 'medium', label: '🟡 Vừa (Neutral)' },
              ].map((p) => (
                <span
                  key={p.id}
                  className={`chip ${filterPriority === p.id ? 'active' : ''}`}
                  onClick={() => setFilterPriority(p.id)}
                  style={{ cursor: 'pointer' }}
                >
                  {p.label}
                </span>
              ))}
            </div>

            {loading ? (
              <p className="sub">Đang tải hàng đợi rà soát từ PostgreSQL DB...</p>
            ) : items.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {items.map((item) => (
                  <div
                    key={item.review_item_id}
                    className="card"
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '16px',
                      padding: '16px',
                      borderLeft: `4px solid ${item.do_uu_tien === 'high' ? '#ef4444' : '#f59e0b'}`,
                      background: '#ffffff',
                    }}
                  >
                    {/* LEFT COLUMN: AI Flagged Sentence & Actions */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span
                          className={`badge ${item.nhan_nli === 'contradiction' ? 'repeal' : 'replace'}`}
                          style={{
                            fontWeight: 700,
                            padding: '4px 8px',
                            borderRadius: '4px',
                            textTransform: 'uppercase',
                          }}
                        >
                          {item.nhan_nli === 'contradiction' ? '🔴 Contradiction' : '🟡 Neutral'}
                        </span>
                        <span style={{ fontSize: '12px', color: 'var(--muted)' }}>
                          Item ID: #{item.review_item_id}
                        </span>
                      </div>

                      <div>
                        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--muted)', marginBottom: '4px' }}>
                          CÂU TÓM TẮT AI SINH BỊ GẮN CỜ:
                        </div>
                        <div
                          style={{
                            background: '#fef2f2',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #fecaca',
                            fontSize: '14px',
                            color: '#991b1b',
                            lineHeight: 1.5,
                          }}
                        >
                          "{item.cau_ai_sinh}"
                        </div>
                      </div>

                      <div style={{ marginTop: 'auto', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        <button
                          onClick={() => handleApprove(item)}
                          style={{
                            background: '#16a34a',
                            color: '#fff',
                            border: 'none',
                            padding: '8px 12px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            fontSize: '13px',
                          }}
                        >
                          ✓ Duyệt giữ nguyên
                        </button>
                        <button
                          onClick={() => openEditModal(item)}
                          style={{
                            background: '#2563eb',
                            color: '#fff',
                            border: 'none',
                            padding: '8px 12px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            fontSize: '13px',
                          }}
                        >
                          ✏️ Sửa & Re-validate NLI
                        </button>
                        <button
                          onClick={() => handleReject(item)}
                          style={{
                            background: '#dc2626',
                            color: '#fff',
                            border: 'none',
                            padding: '8px 12px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            fontSize: '13px',
                          }}
                        >
                          ✕ Loại bỏ
                        </button>
                      </div>
                    </div>

                    {/* RIGHT COLUMN: Original Source Paragraph */}
                    <div
                      style={{
                        background: '#f8fafc',
                        padding: '12px 16px',
                        borderRadius: '6px',
                        border: '1px solid #e2e8f0',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span
                          style={{ fontWeight: 700, fontSize: '13px', color: '#1e293b', cursor: 'pointer' }}
                          onClick={() => openDetail(item.document_id)}
                        >
                          📄 {item.ten_van_ban} ({item.so_hieu})
                        </span>
                      </div>

                      {item.source_chunk ? (
                        <>
                          <div style={{ fontSize: '12px', fontWeight: 600, color: '#2563eb' }}>
                            📌 {item.source_chunk.dieu_khoan} (Trang {item.source_chunk.so_trang})
                          </div>
                          <div
                            style={{
                              fontSize: '13px',
                              color: '#334155',
                              lineHeight: 1.6,
                              maxHeight: '160px',
                              overflowY: 'auto',
                              whiteSpace: 'pre-wrap',
                            }}
                          >
                            {item.source_chunk.noi_dung_goc}
                          </div>
                        </>
                      ) : (
                        <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Không có đoạn văn nguồn chi tiết.</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div
                style={{
                  textAlign: 'center',
                  padding: '40px',
                  background: '#f0fdf4',
                  borderRadius: '12px',
                  border: '1px dashed #bbf7d0',
                }}
              >
                <h3 style={{ color: '#166534', marginBottom: '8px' }}>🎉 Hàng đợi trống!</h3>
                <p className="sub" style={{ color: '#15803d' }}>
                  Tất cả các câu tóm tắt bị gắn cờ NLI đã được rà soát xong. Các văn bản đã đủ điều kiện xuất bản (PUBLISHED).
                </p>
              </div>
            )}
          </>
        )}

        {/* TAB 2: AUDIT TRAIL LOGS */}
        {activeTab === 'audit' && (
          <div>
            <h3>Nhật ký Duyệt Audit Trail (Ghi vết lịch sử Cán bộ)</h3>
            <p className="sub" style={{ marginBottom: '16px' }}>
              Lưu toàn bộ lịch sử thao tác: nội dung AI sinh ban đầu, câu sau khi cán bộ sửa, người duyệt và thời gian.
            </p>

            {loadingLogs ? (
              <p className="sub">Đang tải nhật ký audit logs từ PostgreSQL DB...</p>
            ) : auditLogs.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', background: '#fff' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', textAlign: 'left', borderBottom: '2px solid #cbd5e1' }}>
                      <th style={{ padding: '10px' }}>Log ID</th>
                      <th style={{ padding: '10px' }}>Văn bản</th>
                      <th style={{ padding: '10px' }}>Câu AI sinh ban đầu</th>
                      <th style={{ padding: '10px' }}>Nội dung sau sửa</th>
                      <th style={{ padding: '10px' }}>Hành động</th>
                      <th style={{ padding: '10px' }}>Cán bộ</th>
                      <th style={{ padding: '10px' }}>Thời gian</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => (
                      <tr key={log.log_id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '10px', fontWeight: 600 }}>#{log.log_id}</td>
                        <td style={{ padding: '10px', maxWidth: '200px' }}>
                          <b>{log.ten_van_ban}</b>
                        </td>
                        <td style={{ padding: '10px', color: '#991b1b', maxWidth: '250px' }}>
                          {log.cau_ai_sinh}
                        </td>
                        <td style={{ padding: '10px', color: '#166534', maxWidth: '250px' }}>
                          {log.cau_sau_sua || '—'}
                        </td>
                        <td style={{ padding: '10px' }}>
                          <span
                            style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '11px',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              background:
                                log.hanh_dong === 'approve'
                                  ? '#dcfce7'
                                  : log.hanh_dong === 'edit'
                                  ? '#dbeafe'
                                  : '#fee2e2',
                              color:
                                log.hanh_dong === 'approve'
                                  ? '#15803d'
                                  : log.hanh_dong === 'edit'
                                  ? '#1d4ed8'
                                  : '#b91c1c',
                            }}
                          >
                            {log.hanh_dong}
                          </span>
                        </td>
                        <td style={{ padding: '10px' }}>{log.reviewer_id}</td>
                        <td style={{ padding: '10px', color: 'var(--muted)' }}>
                          {log.created_at ? new Date(log.created_at).toLocaleString('vi-VN') : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="sub">Chưa có nhật ký rà soát nào trong hệ thống.</p>
            )}
          </div>
        )}

        {/* EDIT MODAL WITH NLI RE-VALIDATION */}
        {editingItem && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
            }}
          >
            <div
              style={{
                background: '#fff',
                padding: '24px',
                borderRadius: '12px',
                width: '600px',
                maxWidth: '90%',
                boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)',
              }}
            >
              <h3 style={{ marginBottom: '8px' }}>Chỉnh sửa & Re-validate NLI Check (UC-04)</h3>
              <p className="sub" style={{ marginBottom: '16px' }}>
                Khi bạn bấm Xác nhận, hệ thống sẽ tự động chạy lại kiểm tra NLI cho câu đã sửa trước khi lưu vào CSDL.
              </p>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--muted)' }}>CÂU AI SINH BAN ĐẦU:</label>
                <div style={{ padding: '8px', background: '#f8fafc', borderRadius: '6px', fontSize: '13px' }}>
                  {editingItem.cau_ai_sinh}
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600, color: '#1e293b' }}>
                  NỘI DUNG MỚI CHÍNH XÁC (CÁN BỘ SỬA):
                </label>
                <textarea
                  rows={4}
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    fontSize: '14px',
                    marginTop: '4px',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  onClick={() => setEditingItem(null)}
                  disabled={isSubmitting}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    background: '#fff',
                    cursor: 'pointer',
                  }}
                >
                  Hủy
                </button>
                <button
                  onClick={handleConfirmEdit}
                  disabled={isSubmitting || !editText.trim()}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#2563eb',
                    color: '#fff',
                    cursor: 'pointer',
                    fontWeight: 600,
                  }}
                >
                  {isSubmitting ? 'Đang re-validate NLI...' : 'Xác nhận Sửa & Re-validate NLI'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default ReviewQueue;
