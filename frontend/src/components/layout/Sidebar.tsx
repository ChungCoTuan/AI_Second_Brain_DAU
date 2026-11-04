import React, { useState } from 'react';
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
  Network,
  Bot,
  Layers,
  Settings,
  Trash2
} from 'lucide-react';

import { useData } from '../../context/DataContext';
import { useAuth } from '../../context/AuthContext';
import { LogOut } from 'lucide-react';
import ConfirmModal from '../shared/ConfirmModal';

const Badge = ({ count }: { count: number }) => {
  if (!count) return null;
  return (
    <span className="snav-badge">
      {count}
    </span>
  );
};

interface SidebarProps {
  mobile?: boolean;
  open?: boolean;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ mobile = false, open = false, onClose }) => {
  const { data, readDeadDocs, readEvents, readObligations, readThresholds, readDeadlines, readWarnings} = useData();
  const { role, logout, user } = useAuth();
  
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);
  
  const allWarnings = (data?.insights?.uuTien || []).map((w: any) => w.soHieu);
  const unreadWarningsCount = allWarnings.filter((id: string) => !readWarnings.includes(id)).length;
  const allDeadDocs = [...(data?.vbTuChet || []), ...(data?.vbSapChet || [])].map((d: any) => d.docId);
  const unreadDeadDocsCount = allDeadDocs.filter(id => !readDeadDocs.includes(id)).length;
  const unreadEventsCount = Math.max(0, (data?.events?.length || 0) - readEvents.length);
  
  const uniqueObligationDocs = Array.from(new Set((data?.nghiaVu || []).map((n: any) => n.vb)));
  const unreadObligationsCount = Math.max(0, uniqueObligationDocs.length - (readObligations?.length || 0));

  const uniqueThresholdDocs = Array.from(new Set((data?.conSoChot || []).map((n: any) => n.vb)));
  const unreadThresholdsCount = Math.max(0, uniqueThresholdDocs.length - (readThresholds?.length || 0));

  const uniqueDeadlineDocs = Array.from(new Set((data?.hanChot || []).map((n: any) => n.vb)));
  const unreadDeadlinesCount = Math.max(0, uniqueDeadlineDocs.length - (readDeadlines?.length || 0));



  return (
    <aside
      className={`sidebar ${mobile ? 'sidebar--mobile' : ''} ${open ? 'sidebar--open' : ''}`}
      onClick={mobile ? onClose : undefined}
    >
      <div className="sidebar-header">
        <div className="logo">
          <img src="/dau-logo.png" alt="DAU" style={{ maxWidth: '100%', maxHeight: '100%' }} />
        </div>
        <span className="sidebar-brand">Second Brain</span>
      </div>
      
      {/* Sidebar nav wrap */}
      <nav className="sidebar-nav">
          
          {role === 'admin' && (
            <>
              <div className="snav-section">
                Cảnh báo & Rà soát
              </div>
          <NavLink to="/priority" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <AlertTriangle size={18} />
              <span>Ưu tiên xử lý</span>
            </div>
            <Badge count={unreadWarningsCount} />
          </NavLink>
          <NavLink to="/dead-docs" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <FileX2 size={18} />
              <span>Văn bản khai tử</span>
            </div>
            <Badge count={Math.max(0, unreadDeadDocsCount)} />
          </NavLink>
          <NavLink to="/deadlines" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <CalendarClock size={18} />
              <span>Hạn chót & mốc</span>
            </div>
            <Badge count={unreadDeadlinesCount} />
          </NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <PieChart size={18} />
            <span>Phân tích</span>
          </NavLink>
          <NavLink to="/events" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <History size={18} />
              <span>Sự kiện luật</span>
            </div>
            <Badge count={Math.max(0, unreadEventsCount)} />
          </NavLink>
          <NavLink to="/review" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <ClipboardList size={18} />
              <span>Cần rà soát</span>
            </div>
            <Badge count={data?.pendingCount || 0} />
          </NavLink>
          <NavLink to="/topics" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <Layers size={18} />
            <span>Chủ đề văn bản</span>
          </NavLink>
          </>
          )}
          
          <div className="snav-section">
            Tra cứu & Dữ liệu
          </div>
          <NavLink to="/search" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <Search size={18} />
            <span>Tra cứu thủ công</span>
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <Bot size={18} />
            <span>Tra cứu AI (Chatbot)</span>
          </NavLink>
          <NavLink to="/obligations" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <CheckSquare size={18} />
              <span>Việc phải làm</span>
            </div>
            <Badge count={unreadObligationsCount} />
          </NavLink>
          <NavLink to="/thresholds" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <Book size={18} />
              <span>Sổ ngưỡng & định mức</span>
            </div>
            <Badge count={unreadThresholdsCount} />
          </NavLink>
          <NavLink to="/graph" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <Network size={18} />
            <span>Đồ thị ảnh hưởng</span>
          </NavLink>

          {role === 'admin' && (
          <>
          <div className="snav-section">
            Hệ thống
          </div>
          <NavLink to="/admin" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`} style={{ justifyContent: 'space-between' }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px', width: '100%'}}>
              <Settings size={18} />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flex: 1 }}>
                <span>Tải tài liệu (Admin)</span>
                {data.hasNewDocs && <span className="snav-dot" />}
              </div>
            </div>
            <Badge count={data?.adminCount || 0} />
          </NavLink>
          <NavLink to="/audit" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <History size={18} />
            <span>Nhật ký thao tác</span>
          </NavLink>
          <NavLink to="/rejected" className={({ isActive }) => `snav ${isActive ? 'active' : ''}`}>
            <Trash2 size={18} />
            <span>Văn bản loại bỏ</span>
          </NavLink>
          </>
          )}
      </nav>
      
      <div className="sidebar-user">
        <div className="sidebar-user-row">
          <div className="sidebar-avatar">
            {user?.email?.[0].toUpperCase()}
          </div>
          <div className="sidebar-user-meta">
            <div className="sidebar-user-email">{user?.email}</div>
            <div className="sidebar-user-role">{role === 'admin' ? 'Quản trị viên' : 'Giảng viên'}</div>
          </div>
        </div>
        <button 
          onClick={() => setIsLogoutModalOpen(true)}
          className="btn btn-ghost-danger"
          style={{ width: '100%', justifyContent: 'center' }}
        >
          <LogOut size={16} /> Đăng xuất
        </button>
      </div>

      <ConfirmModal
        isOpen={isLogoutModalOpen}
        title="Xác nhận đăng xuất"
        message="Bạn có chắc chắn muốn đăng xuất khỏi hệ thống không?"
        confirmText="Đăng xuất"
        isDestructive={true}
        onConfirm={() => {
          setIsLogoutModalOpen(false);
          logout();
        }}
        onCancel={() => setIsLogoutModalOpen(false)}
      />
    </aside>
  );
};

export default Sidebar;
