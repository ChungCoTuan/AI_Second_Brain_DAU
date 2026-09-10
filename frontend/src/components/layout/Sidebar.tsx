import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  AlertTriangle,
  FileX2,
  CalendarClock,
  PieChart,
  History,
  ClipboardList,
  Search,
  CheckSquare,
  Book,
  Network
} from 'lucide-react';

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar" style={{ width: '260px', background: '#fff', borderRight: '1px solid var(--line)', padding: '20px 0' }}>
      <div className="sidebar-header" style={{ padding: '0 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="logo" style={{ width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <img src="/dau-logo.png" alt="DAU" style={{ maxWidth: '100%', maxHeight: '100%' }} />
        </div>
        <span style={{ fontWeight: 800, color: 'var(--blue)', fontSize: '18px' }}>Second Brain</span>
      </div>
      
      <nav className="sidebar-nav" style={{ display: 'flex', flexDirection: 'column', gap: '4px', padding: '0 12px' }}>
        <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Cảnh báo & Rà soát
        </div>
        <NavLink to="/priority" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <AlertTriangle size={18} />
          <span>Ưu tiên xử lý</span>
        </NavLink>
        <NavLink to="/dead-docs" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <FileX2 size={18} />
          <span>Văn bản khai tử</span>
        </NavLink>
        <NavLink to="/deadlines" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <CalendarClock size={18} />
          <span>Hạn chót & mốc</span>
        </NavLink>
        <NavLink to="/analytics" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <PieChart size={18} />
          <span>Phân tích</span>
        </NavLink>
        <NavLink to="/events" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <History size={18} />
          <span>Sự kiện luật</span>
        </NavLink>
        <NavLink to="/review" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <ClipboardList size={18} />
          <span>Cần rà soát</span>
        </NavLink>
        
        <div style={{ padding: '16px 12px 8px', fontSize: '11px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Tra cứu & Dữ liệu
        </div>
        <NavLink to="/search" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <Search size={18} />
          <span>Tra cứu kho</span>
        </NavLink>
        <NavLink to="/obligations" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <CheckSquare size={18} />
          <span>Việc phải làm</span>
        </NavLink>
        <NavLink to="/thresholds" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <Book size={18} />
          <span>Sổ ngưỡng & định mức</span>
        </NavLink>
        <NavLink to="/graph" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle}>
          <Network size={18} />
          <span>Đồ thị ảnh hưởng</span>
        </NavLink>
      </nav>
      
      {/* Basic styles for Sidebar nav items using styled inline for simplicity, 
          since we cleared App.css and index.css has the global styles */}
      <style>{`
        .navtabs-a {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 14px;
          color: var(--muted);
          text-decoration: none;
          font-size: 14px;
          font-weight: 600;
          border-radius: 8px;
          transition: 0.15s;
        }
        .navtabs-a:hover {
          background: var(--soft);
          color: var(--ink);
        }
        .navtabs-a.active {
          background: var(--blue-50);
          color: var(--blue);
          border-right: 3px solid var(--blue);
        }
      `}</style>
    </aside>
  );
};

const navStyle = {};

export default Sidebar;
