import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, FolderTree, ClipboardCheck, GraduationCap, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar: React.FC = () => {
  const { role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <GraduationCap size={28} />
        <span>Second Brain</span>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
          <LayoutDashboard size={20} />
          <span>Tra cứu & Hỏi đáp</span>
        </NavLink>
        
        {role === 'admin' && (
          <>
            <NavLink to="/topics" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <FolderTree size={20} />
              <span>Chủ đề & Nạp liệu</span>
            </NavLink>
            <NavLink to="/review" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <ClipboardCheck size={20} />
              <span>Rà soát & Duyệt</span>
            </NavLink>
          </>
        )}
      </nav>

      <div className="sidebar-footer">
        <button onClick={handleLogout} className="nav-item" style={{ width: '100%' }}>
          <LogOut size={20} />
          <span>Đăng xuất</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
