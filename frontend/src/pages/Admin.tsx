import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { useData } from '../context/DataContext';

const Admin: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile: File) => {
    if (selectedFile.type !== 'application/pdf') {
      setStatus('error');
      setMessage('Vui lòng chọn file định dạng PDF.');
      return;
    }
    setFile(selectedFile);
    setStatus('idle');
    setMessage('');
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setStatus('uploading');
    setMessage('Đang tải lên và phân tích văn bản...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStatus('success');
        setMessage(data.message || 'Xử lý thành công!');
      } else {
        setStatus('error');
        setMessage(data.detail || 'Lỗi khi xử lý file.');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Không thể kết nối đến máy chủ.');
      console.error(error);
    }
  };

  return (
    <section id="admin-upload" style={{ background: 'var(--soft)', minHeight: '100vh', paddingBottom: '40px' }}>
      <div className="wrap" style={{ maxWidth: '800px', margin: '0 auto', paddingTop: '32px' }}>
        
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--ink)' }}>Tải tài liệu lên hệ thống</h2>
          <p className="sub" style={{ color: 'var(--muted)', marginTop: '4px' }}>
            Quá trình này bao gồm: Tải file PDF &rarr; Chạy OCR đọc chữ &rarr; Gọi AI bóc tách (Mock) &rarr; Đẩy vào hàng đợi duyệt.
          </p>
        </div>

        <div 
          style={{
            background: 'var(--card-bg)',
            border: `2px dashed ${dragActive ? 'var(--blue)' : 'var(--border)'}`,
            borderRadius: '16px',
            padding: '40px',
            textAlign: 'center',
            transition: 'all 0.2s',
            cursor: 'pointer',
            boxShadow: dragActive ? '0 0 0 4px var(--blue-50)' : 'none'
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            multiple={false}
            onChange={handleChange}
            style={{ display: 'none' }}
          />
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            <div style={{ 
              background: dragActive ? 'var(--blue-50)' : 'var(--app-bg)',
              padding: '20px',
              borderRadius: '50%',
              color: dragActive ? 'var(--blue)' : 'var(--muted)',
              transition: 'all 0.2s'
            }}>
              <UploadCloud size={48} />
            </div>
            
            <div>
              <p style={{ fontSize: '18px', fontWeight: 600, color: 'var(--ink)' }}>
                Kéo thả file PDF vào đây
              </p>
              <p style={{ fontSize: '14px', color: 'var(--muted)', marginTop: '8px' }}>
                hoặc click để chọn file từ máy tính của bạn (tối đa 50MB)
              </p>
            </div>
          </div>
        </div>

        {file && (
          <div style={{ 
            marginTop: '24px',
            background: 'var(--card-bg)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ background: 'var(--blue-50)', padding: '12px', borderRadius: '8px', color: 'var(--blue)' }}>
                <FileText size={24} />
              </div>
              <div>
                <p style={{ fontWeight: 600, color: 'var(--ink)', fontSize: '15px' }}>{file.name}</p>
                <p style={{ color: 'var(--muted)', fontSize: '13px', marginTop: '4px' }}>
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            
            <button 
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={status === 'uploading'}
              style={{
                background: 'var(--blue)',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '8px',
                fontWeight: 600,
                cursor: status === 'uploading' ? 'not-allowed' : 'pointer',
                opacity: status === 'uploading' ? 0.7 : 1
              }}
            >
              {status === 'uploading' ? 'Đang xử lý...' : 'Bắt đầu Xử lý'}
            </button>
          </div>
        )}

        {status !== 'idle' && (
          <div style={{ 
            marginTop: '16px',
            padding: '16px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: status === 'error' ? 'var(--red-50)' : status === 'success' ? 'var(--green-50)' : 'var(--blue-50)',
            color: status === 'error' ? 'var(--red)' : status === 'success' ? 'var(--green)' : 'var(--blue)',
            border: `1px solid ${status === 'error' ? 'var(--red-200)' : status === 'success' ? 'var(--green-200)' : 'var(--blue-200)'}`
          }}>
            {status === 'error' && <AlertCircle size={20} />}
            {status === 'success' && <CheckCircle2 size={20} />}
            {status === 'uploading' && <div className="spinner" style={{ width: '20px', height: '20px', borderTopColor: 'var(--blue)', borderRightColor: 'var(--blue)', borderRadius: '50%', border: '2px solid transparent' }}></div>}
            
            <span style={{ fontWeight: 500, fontSize: '14px' }}>{message}</span>
          </div>
        )}
      </div>
    </section>
  );
};

export default Admin;
