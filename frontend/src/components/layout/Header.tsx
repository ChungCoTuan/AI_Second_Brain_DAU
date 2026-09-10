import React from 'react';
import { Bell, User } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="header" style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '0 20px', height: '58px', background: 'var(--blue)', color: '#fff',
      boxShadow: '0 1px 0 rgba(0,0,0,.15)', zIndex: 10, position: 'sticky', top: 0
    }}>
      <div className="header-left" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="brand" style={{ fontWeight: 700, fontSize: '16px' }}>Hệ thống Rà soát & Cảnh báo</div>
      </div>
      <div className="header-right" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
          <Bell size={20} />
        </button>
        <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div className="avatar" style={{ 
            width: '32px', height: '32px', borderRadius: '50%', 
            backgroundColor: 'rgba(255,255,255,0.2)', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <User size={16} />
          </div>
          <span style={{ fontWeight: 600, fontSize: '13px' }}>
            Phòng Đào tạo
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
