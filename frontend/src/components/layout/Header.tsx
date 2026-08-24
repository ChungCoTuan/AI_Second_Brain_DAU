import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { GraduationCap, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Header: React.FC = () => {
  const { role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  return (
    <header className="header">
      <NavLink to="/" className="header-left">
        <GraduationCap size={32} />
        <h1 className="header-title">Trường Đại học Kiến trúc Đà Nẵng</h1>
      </NavLink>
      <nav className="nav-links">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Tra Cứu
        </NavLink>
        {role === 'admin' && (
          <NavLink to="/admin" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Quản Trị (Cán bộ)
          </NavLink>
        )}
        <button onClick={handleLogout} className="nav-link" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <LogOut size={16} /> Đăng xuất
        </button>
      </nav>
    </header>
  );
};

export default Header;
