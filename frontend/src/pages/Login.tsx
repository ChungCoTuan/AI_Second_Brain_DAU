import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../context/AuthContext';
import { GraduationCap, ShieldCheck, BookOpen } from 'lucide-react';

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (role: UserRole) => {
    login(role);
    navigate('/');
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <GraduationCap size={48} color="var(--dau-red)" style={{ marginBottom: '1rem' }} />
          <h2 style={{ color: 'var(--dau-red)', textTransform: 'uppercase' }}>DAU Second Brain</h2>
          <p style={{ color: 'var(--dau-gray)', marginTop: '0.5rem' }}>Đăng nhập để tiếp tục</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <button 
            className="btn btn-outline login-btn"
            onClick={() => handleLogin('admin')}
          >
            <ShieldCheck size={20} color="var(--color-success)" />
            Đăng nhập với quyền Cán Bộ Đào Tạo
          </button>
          
          <button 
            className="btn btn-outline login-btn"
            onClick={() => handleLogin('teacher')}
          >
            <BookOpen size={20} color="var(--dau-orange)" />
            Đăng nhập với quyền Giảng Viên
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
