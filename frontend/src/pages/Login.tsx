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
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', width: '100vw', backgroundColor: 'var(--bg-main)' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px', padding: '3rem 2rem', textAlign: 'center' }}>
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'var(--color-primary-light)', borderRadius: '50%' }}>
              <GraduationCap size={48} color="var(--color-primary)" />
            </div>
          </div>
          <h2 className="title-h2" style={{ margin: 0, textTransform: 'uppercase', color: 'var(--text-primary)' }}>DAU Second Brain</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '1rem' }}>Đăng nhập để tiếp tục</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <button 
            className="hover-lift"
            onClick={() => handleLogin('admin')}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem',
              width: '100%', padding: '1rem',
              backgroundColor: 'var(--bg-surface)', border: '2px solid var(--color-primary)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-primary)', fontWeight: 600, fontSize: '1rem'
            }}
          >
            <ShieldCheck size={20} />
            Đăng nhập: Cán Bộ Đào Tạo
          </button>
          
          <button 
            className="hover-lift"
            onClick={() => handleLogin('teacher')}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem',
              width: '100%', padding: '1rem',
              backgroundColor: 'var(--bg-surface)', border: '2px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)', fontWeight: 600, fontSize: '1rem'
            }}
          >
            <BookOpen size={20} color="var(--text-secondary)" />
            Đăng nhập: Giảng Viên
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
