import React, { useEffect, useState } from 'react';
import {
  fetchDocumentTree,
  updateDocumentScope,
  type DocumentTreeResponse,
  type DocumentTreeNode,
} from '../services/api';
import { useDetail } from '../context/DetailContext';

interface DocumentTreeTabProps {
  docId: string;
}

const SCOPE_MAP: Record<string, { label: string; bg: string; color: string }> = {
  DIRECT_DAU: {
    label: 'Áp dụng trực tiếp — Có văn bản nội bộ DAU',
    bg: '#dcfce7',
    color: '#15803d',
  },
  GENERAL: {
    label: 'Áp dụng chung — Chưa có văn bản nội bộ',
    bg: '#e0f2fe',
    color: '#0369a1',
  },
  REFERENCE: {
    label: 'Chỉ mang tính tham khảo',
    bg: '#f3f4f6',
    color: '#4b5563',
  },
};

const REL_TYPE_MAP: Record<string, { label: string; bg: string; color: string }> = {
  can_cu: { label: 'Căn cứ', bg: '#eff6ff', color: '#1d4ed8' },
  thay_the: { label: 'Thay thế', bg: '#fef2f2', color: '#b91c1c' },
  sua_doi: { label: 'Sửa đổi', bg: '#fffbeb', color: '#b45309' },
  bai_bo: { label: 'Bãi bỏ', bg: '#fdf2f8', color: '#be185d' },
  cung_chu_de: { label: 'Cùng chủ đề', bg: '#f0fdf4', color: '#15803d' },
};

export const DocumentTreeTab: React.FC<DocumentTreeTabProps> = ({ docId }) => {
  const [treeData, setTreeData] = useState<DocumentTreeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentScope, setCurrentScope] = useState<string>('GENERAL');
  const [savingScope, setSavingScope] = useState<boolean>(false);
  const [msg, setMsg] = useState<string>('');

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchDocumentTree(docId).then((data) => {
      if (isMounted && data) {
        setTreeData(data);
        setCurrentScope(data.pham_vi_ap_dung || 'GENERAL');
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [docId]);

  const handleScopeChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newScope = e.target.value;
    setCurrentScope(newScope);
    setSavingScope(true);
    setMsg('');

    const res = await updateDocumentScope(docId, newScope);
    setSavingScope(false);
    if (res.success) {
      setMsg('✅ Đã lưu phạm vi áp dụng tại DAU!');
      setTimeout(() => setMsg(''), 3000);
    } else {
      setMsg(`❌ Lỗi: ${res.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
        ⏳ Đang nạp Cây văn bản & Mối quan hệ pháp lý...
      </div>
    );
  }

  if (!treeData) {
    return (
      <div style={{ padding: '20px', color: '#ef4444' }}>
        Không thể nạp dữ liệu Cây văn bản cho ID={docId}.
      </div>
    );
  }

  const activeScopeBadge = SCOPE_MAP[currentScope] || SCOPE_MAP.GENERAL;
  const { openDetail } = useDetail();

  const renderNodeList = (nodes: DocumentTreeNode[], title: string, icon: string) => {
    if (nodes.length === 0) {
      return (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontWeight: 700, fontSize: '13px', color: '#334155', marginBottom: '6px' }}>
            {icon} {title} (0)
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8', fontStyle: 'italic' }}>
            Không tìm thấy văn bản liên kết.
          </div>
        </div>
      );
    }

    return (
      <div style={{ marginBottom: '18px' }}>
        <div style={{ fontWeight: 700, fontSize: '13px', color: '#1e293b', marginBottom: '8px' }}>
          {icon} {title} ({nodes.length})
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {nodes.map((node, idx) => {
            const relBadge = REL_TYPE_MAP[node.loai_quan_he] || REL_TYPE_MAP.can_cu;
            return (
              <div
                key={idx}
                onClick={() => openDetail(node.doc_id)}
                style={{
                  background: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                }}
                onMouseOver={(e) => (e.currentTarget.style.background = '#f8fafc')}
                onMouseOut={(e) => (e.currentTarget.style.background = '#ffffff')}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '13px', color: '#0f172a' }}>
                    {node.so_hieu ? `${node.so_hieu}: ` : ''}
                    {node.ten_van_ban}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                    Phạm vi: <b>{node.pham_vi_ap_dung}</b>
                    {node.diem_tuong_dong && (
                      <span> • Độ tương đồng: <b>{Math.round(node.diem_tuong_dong * 100)}%</b></span>
                    )}
                  </div>
                </div>
                <span
                  style={{
                    background: relBadge.bg,
                    color: relBadge.color,
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    whiteSpace: 'nowrap',
                    marginLeft: '8px',
                  }}
                >
                  {relBadge.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '16px', background: '#f8fafc', borderRadius: '12px', marginTop: '12px' }}>
      {/* SCOPE SELECTOR HEADER */}
      <div
        style={{
          background: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '10px',
          padding: '14px 16px',
          marginBottom: '20px',
        }}
      >
        <div style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a', marginBottom: '8px' }}>
          🏛️ Mức Độ Áp Dụng Tại Trường ĐH Kiến Trúc Đà Nẵng (DAU)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <select
            value={currentScope}
            onChange={handleScopeChange}
            disabled={savingScope}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #94a3b8',
              fontSize: '13px',
              fontWeight: 600,
              background: '#ffffff',
              color: '#0f172a',
            }}
          >
            <option value="DIRECT_DAU">🟢 Áp dụng trực tiếp — Có quy chế / văn bản nội bộ DAU</option>
            <option value="GENERAL">🔵 Áp dụng chung — Chưa có văn bản nội bộ riêng</option>
            <option value="REFERENCE">⚪ Chỉ mang tính tham khảo</option>
          </select>
          <span
            style={{
              background: activeScopeBadge.bg,
              color: activeScopeBadge.color,
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 700,
            }}
          >
            {savingScope ? '⏳ Đang lưu...' : 'Nhãn hiện tại'}
          </span>
        </div>
        {msg && (
          <div style={{ marginTop: '8px', fontSize: '12px', fontWeight: 600, color: msg.startsWith('✅') ? '#15803d' : '#b91c1c' }}>
            {msg}
          </div>
        )}
      </div>

      {/* DOCUMENT RELATION TREE NODES */}
      {renderNodeList(treeData.legal_parents, 'Căn cứ Pháp lý Ban hành (Parent Docs)', '📜')}
      {renderNodeList(treeData.legal_children, 'Văn bản Liên quan / Thay thế / Sửa đổi (Child Docs)', '🔄')}
      {renderNodeList(treeData.semantic_related, 'Văn bản Cùng Chủ đề & Ngữ nghĩa (FAISS Vector Store)', '🔗')}
    </div>
  );
};
