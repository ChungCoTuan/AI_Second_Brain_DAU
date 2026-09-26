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
  Network,
  Bot,
  Layers,
  Settings,
  Trash2
} from 'lucide-react';

import { useData } from '../../context/DataContext';

const Badge = ({ count }: { count: number }) => {
  if (!count) return null;
  return (
    <span style={{
      background: '#ef4444', 
      color: 'white', 
      fontSize: '11px', 
      fontWeight: 700, 
      padding: '2px 8px', 
      borderRadius: '12px'
    }}>
      {count}
    </span>
  );
};

const navStyle = {};

const Sidebar: React.FC = () => {
  const { data, readDeadDocs, readEvents, readObligations, readThresholds, readDeadlines, readWarnings, isProcessing } = useData();
  
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

  const blockIfProcessing = (e: React.MouseEvent) => {
    if (isProcessing) {
      e.preventDefault();
      e.stopPropagation();
      alert('AI đang bóc tách văn bản. Vui lòng đợi hoàn thành trước khi chuyển tab!');
    }
  };

  return (
    <aside className="sidebar" style={{ width: '260px', background: '#fff', borderRight: '1px solid var(--line)', padding: '20px 0', position: 'relative' }}>
      <div className="sidebar-header" style={{ padding: '0 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="logo" style={{ width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <img src="/dau-logo.png" alt="DAU" style={{ maxWidth: '100%', maxHeight: '100%' }} />
        </div>
        <span style={{ fontWeight: 800, color: 'var(--blue)', fontSize: '18px' }}>Second Brain</span>
      </div>
      
      {/* Overlay hiển thị khi đang xử lý - bọc TOÀN BỘ nav */}
      <div
        onClickCapture={blockIfProcessing}
        style={{ position: 'relative' }}
      >
        {isProcessing && (
          <div style={{
            position: 'absolute', inset: 0, zIndex: 100,
            background: 'rgba(239,246,255,0.75)', backdropFilter: 'blur(2px)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            gap: '8px', cursor: 'not-allowed', pointerEvents: 'all'
          }}>
            <div style={{
              width: 24, height: 24, border: '3px solid var(--blue)',
              borderTopColor: 'transparent', borderRadius: '50%',
              animation: 'spin 0.8s linear infinite'
            }} />
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--blue)', textAlign: 'center', lineHeight: 1.5 }}>
              AI đang bóc tách<br />Vui lòng đợi...
            </span>
          </div>
        )}

        <nav className="sidebar-nav" style={{ display: 'flex', flexDirection: 'column', gap: '4px', padding: '0 12px' }}>
          <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Cảnh báo & Rà soát
          </div>
          <NavLink to="/priority" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <AlertTriangle size={18} />
              <span>Ưu tiên xử lý</span>
            </div>
            <Badge count={unreadWarningsCount} />
          </NavLink>
          <NavLink to="/dead-docs" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <FileX2 size={18} />
              <span>Văn bản khai tử</span>
            </div>
            <Badge count={Math.max(0, unreadDeadDocsCount)} />
          </NavLink>
          <NavLink to="/deadlines" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <CalendarClock size={18} />
              <span>Hạn chót & mốc</span>
            </div>
            <Badge count={unreadDeadlinesCount} />
          </NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <PieChart size={18} />
            <span>Phân tích</span>
          </NavLink>
          <NavLink to="/events" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <History size={18} />
              <span>Sự kiện luật</span>
            </div>
            <Badge count={Math.max(0, unreadEventsCount)} />
          </NavLink>
          <NavLink to="/review" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <ClipboardList size={18} />
              <span>Cần rà soát</span>
            </div>
            <Badge count={data?.pendingCount || 0} />
          </NavLink>
          <NavLink to="/topics" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <Layers size={18} />
            <span>Chủ đề văn bản</span>
          </NavLink>
          
          <div style={{ padding: '16px 12px 8px', fontSize: '11px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Tra cứu & Dữ liệu
          </div>
          <NavLink to="/search" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <Search size={18} />
            <span>Tra cứu thủ công</span>
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <Bot size={18} />
            <span>Tra cứu AI (Chatbot)</span>
          </NavLink>
          <NavLink to="/obligations" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <CheckSquare size={18} />
              <span>Việc phải làm</span>
            </div>
            <Badge count={unreadObligationsCount} />
          </NavLink>
          <NavLink to="/thresholds" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}} onClick={blockIfProcessing}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <Book size={18} />
              <span>Sổ ngưỡng & định mức</span>
            </div>
            <Badge count={unreadThresholdsCount} />
          </NavLink>
          <NavLink to="/graph" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <Network size={18} />
            <span>Đồ thị ảnh hưởng</span>
          </NavLink>

          <div style={{ padding: '16px 12px 8px', fontSize: '11px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Hệ thống
          </div>
          <NavLink to="/admin" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={{...navStyle, justifyContent: 'space-between'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px', width: '100%'}}>
              <Settings size={18} />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flex: 1 }}>
                <span>Tải tài liệu (Admin)</span>
                {data.hasNewDocs && (
                  <div style={{
                    background: 'var(--red)', color: 'white', borderRadius: '50%',
                    width: '8px', height: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}></div>
                )}
              </div>
            </div>
            <Badge count={data?.adminCount || 0} />
          </NavLink>
          <NavLink to="/audit" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <History size={18} />
            <span>Nhật ký thao tác</span>
          </NavLink>
          <NavLink to="/rejected" className={({ isActive }) => `navtabs-a ${isActive ? 'active' : ''}`} style={navStyle} onClick={blockIfProcessing}>
            <Trash2 size={18} />
            <span>Văn bản loại bỏ</span>
          </NavLink>
        </nav>
      </div>

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

export default Sidebar;
