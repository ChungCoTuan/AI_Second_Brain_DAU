import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Bell, User } from 'lucide-react';

const Header: React.FC = () => {
  const { role } = useAuth();

  return (
    <header className="header">
      <div className="header-left">
        {/* Có thể để breadcrumbs hoặc khoảng trống ở đây */}
      </div>
      <div className="header-right" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button className="icon-btn hover-lift" style={{ color: 'var(--text-secondary)' }}>
          <Bell size={20} />
        </button>
        <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div className="avatar" style={{ 
            width: '32px', height: '32px', borderRadius: '50%', 
            backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <User size={16} />
          </div>
          <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>
            {role === 'admin' ? 'Cán bộ Đào tạo' : 'Giảng viên'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
