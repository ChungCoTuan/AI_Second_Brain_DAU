import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Navigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, token, isLoading } = useAuth();
  const navigate = useNavigate();

  if (isLoading) {
    return <div className="flex h-screen w-screen items-center justify-center">Đang tải...</div>;
  }

  // If already logged in, redirect
  if (token) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axiosClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token } = response.data;
      
      // Fetch user info to get role
      const userRes = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      login(access_token, userRes.data);
      
      if (userRes.data.role === 'lecturer') {
        navigate('/search');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sai email hoặc mật khẩu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Cột trái: Hình ảnh giới thiệu DAU */}
      <div className="auth-hero">
        {/* Abstract pattern */}
        <div className="auth-hero-pattern">
          <svg width="400" height="400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>

        <div className="auth-hero-inner">
          <div className="auth-brand-badge">
            <span className="auth-brand-text">AI SECOND BRAIN</span>
          </div>
          <h1>Hệ thống Trợ lý pháp lý thông minh</h1>
          <p>
            Đại học Kiến trúc Đà Nẵng (DAU). Quản lý, bóc tách và tra cứu văn bản quy phạm pháp luật tự động bằng trí tuệ nhân tạo.
          </p>
          <div className="auth-hero-note">HÀNH CHÍNH · PHÁP LÝ</div>
        </div>
      </div>

      {/* Cột phải: Form đăng nhập */}
      <div className="auth-form-panel">
        <div className="auth-card">
          <div className="auth-card-head">
            <h2>Đăng nhập</h2>
            <p>Vui lòng đăng nhập để tiếp tục</p>
          </div>

          {error && (
            <div className="auth-error">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="auth-field">
              <label className="auth-label">Email đăng nhập</label>
              <input
                type="email"
                required
                className="auth-input"
                placeholder="Ví dụ: admin@dau.edu.vn"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="auth-field">
              <label className="auth-label">Mật khẩu</label>
              <input
                type="password"
                required
                className="auth-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="auth-submit"
            >
              {loading ? 'Đang xác thực...' : 'Đăng nhập ngay'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
