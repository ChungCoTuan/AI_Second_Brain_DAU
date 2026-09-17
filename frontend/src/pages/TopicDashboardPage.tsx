import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopicDashboard } from '../components/TopicDashboard';
import { uploadDocument } from '../services/api';

const TopicDashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState('AUTO');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSelectTopic = (topicCode: string) => {
    // Navigate to search/priority page with topic filter
    navigate(`/search?chu_de=${topicCode}`);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setIsUploading(true);
      setUploadSuccess(false);
      try {
        const file = files[0];
        const topicToSubmit = selectedTopic === 'AUTO' ? 'KHAC' : selectedTopic;
        const res = await uploadDocument(file, topicToSubmit);
        console.log("Upload response:", res);
        setUploadSuccess(true);
        setTimeout(() => setUploadSuccess(false), 3000);
        setRefreshKey(prev => prev + 1);
      } catch (error) {
        console.error(error);
        alert("Có lỗi xảy ra khi tải file lên.");
      } finally {
        setIsUploading(false);
        e.target.value = '';
      }
    }
  };

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 20px', paddingBottom: '40px' }}>
      
      {/* KHU VỰC NẠP VĂN BẢN (UPLOAD UI - UC-01) */}
      <div style={{ 
        marginTop: '24px', 
        padding: '24px', 
        background: '#ffffff', 
        borderRadius: '16px', 
        border: '1px dashed #cbd5e1',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px'
      }}>
        <div style={{ fontSize: '32px' }}>📂</div>
        <h3 style={{ margin: 0, fontSize: '18px', color: '#334155' }}>Nạp văn bản mới vào hệ thống</h3>
        <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>Hỗ trợ PDF, DOCX. Tối đa 50MB.</p>
        
        <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
          <select 
            value={selectedTopic} 
            onChange={e => setSelectedTopic(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              background: '#fff',
              color: '#334155',
              outline: 'none',
              fontWeight: 500
            }}
            disabled={isUploading}
          >
            <option value="AUTO">🤖 Tự động phân loại (AI)</option>
            <option value="DAO_TAO">Đào Tạo & Học Vụ</option>
            <option value="TUYEN_SINH">Tuyển Sinh & Nhập Học</option>
            <option value="TAI_CHINH">Tài Chính & Học Phí</option>
            <option value="NHAN_SU">Nhân Sự & Giảng Viên</option>
            <option value="CO_SO_VAT_CHAT">Cơ Sở Vật Chất</option>
            <option value="KHAC">Văn Bản Hành Chính Khác</option>
          </select>

          <label style={{
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            padding: '8px 16px',
            borderRadius: '8px',
            color: '#0f172a',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}>
            {isUploading ? '⏳ Đang xử lý...' : uploadSuccess ? '✅ Thành công' : 'Chọn file tải lên...'}
            <input 
              type="file" 
              accept=".pdf,.docx" 
              onChange={handleFileUpload} 
              style={{ display: 'none' }} 
              disabled={isUploading}
            />
          </label>
        </div>
      </div>

      <TopicDashboard onSelectTopic={handleSelectTopic} refreshKey={refreshKey} />
    </div>
  );
};

export default TopicDashboardPage;
