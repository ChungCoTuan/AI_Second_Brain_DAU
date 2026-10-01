import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Bell, User, CheckCircle2, AlertTriangle, CalendarClock, ClipboardList, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../../context/DataContext';
import { useAuth } from '../../context/AuthContext';

const Header: React.FC = () => {
  const { data, readWarnings, readDeadlines, markAsRead } = useData();
  const { role } = useAuth();
  const navigate = useNavigate();
  
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Xử lý đóng dropdown khi click ra ngoài
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Tổng hợp danh sách thông báo
  const notifications = useMemo(() => {
    const notifs = [];
    
    // 1. Văn bản mới cào (Chỉ Admin)
    if (role === 'admin' && data.hasNewDocs) {
      notifs.push({
        id: 'new_crawled_docs',
        type: 'admin',
        title: 'Phát hiện văn bản mới',
        desc: 'Có văn bản mới được ban hành trên Chinhphu.vn. Cần đồng bộ.',
        link: '/admin',
        isRead: false,
        icon: <FileText size={16} color="#3b82f6" />
      });
    }

    // 2. Chờ rà soát (Chỉ Admin)
    if (role === 'admin' && data.pendingCount > 0) {
      notifs.push({
        id: 'pending_review',
        type: 'review',
        title: 'Cần rà soát',
        desc: `Có ${data.pendingCount} hạng mục đang chờ bạn duyệt.`,
        link: '/review',
        isRead: false,
        icon: <ClipboardList size={16} color="#8b5cf6" />
      });
    }

    // 3. Cảnh báo rủi ro
    (data.warnings || []).forEach((w: any) => {
      notifs.push({
        id: w.soHieu,
        type: 'warning',
        title: `Cảnh báo: ${w.soHieu}`,
        desc: w.lyDo,
        link: '/priority',
        isRead: readWarnings.includes(w.soHieu),
        icon: <AlertTriangle size={16} color="#ef4444" />
      });
    });

    // 4. Hạn chót sắp tới
    (data.hanChot || []).forEach((h: any) => {
      notifs.push({
        id: h.vb,
        type: 'deadline',
        title: 'Hạn chót sắp tới',
        desc: `Văn bản ${h.vb}: ${h.noiDung}`,
        link: '/deadlines',
        isRead: readDeadlines.includes(h.vb),
        icon: <CalendarClock size={16} color="#f59e0b" />
      });
    });

    return notifs;
  }, [data, role, readWarnings, readDeadlines]);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const handleNotificationClick = (notif: any) => {
    if (!notif.isRead) {
      if (notif.type === 'warning') markAsRead('warning', notif.id);
      if (notif.type === 'deadline') markAsRead('deadline', notif.id);
      // 'admin' và 'review' không lưu theo ID riêng lẻ mà cập nhật state nội tại hoặc ko cần
    }
    setIsOpen(false);
    navigate(notif.link);
  };

  return (
    <header className="header" style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '0 20px', height: '58px', background: 'var(--blue)', color: '#fff',
      boxShadow: '0 1px 0 rgba(0,0,0,.15)', zIndex: 10, position: 'sticky', top: 0
    }}>
      <div className="header-left" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="brand" style={{ fontWeight: 700, fontSize: '16px' }}>Hệ thống Trợ lý Pháp lý</div>
      </div>
      <div className="header-right" style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
        
        {/* Khối Thông báo */}
        <div ref={dropdownRef} style={{ position: 'relative' }}>
          <button 
            onClick={() => setIsOpen(!isOpen)}
            style={{ 
              background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative',
              width: '32px', height: '32px', borderRadius: '50%',
              backgroundColor: isOpen ? 'rgba(255,255,255,0.1)' : 'transparent',
              transition: 'background 0.2s'
            }}
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute', top: '0px', right: '0px',
                background: '#ef4444', color: 'white', fontSize: '10px',
                fontWeight: 700, padding: '1px 5px', borderRadius: '10px',
                lineHeight: 1, border: '2px solid var(--blue)'
              }}>
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>

          {/* Dropdown UI */}
          {isOpen && (
            <div style={{
              position: 'absolute', top: '44px', right: '-10px', width: '340px',
              background: '#fff', borderRadius: '12px', boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
              border: '1px solid var(--line)', color: 'var(--ink)', zIndex: 100,
              overflow: 'hidden', display: 'flex', flexDirection: 'column', maxHeight: '420px'
            }}>
              <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--soft)' }}>
                <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 700 }}>Thông báo</h3>
                {unreadCount > 0 && <span style={{ fontSize: '12px', color: 'var(--blue)', fontWeight: 600 }}>{unreadCount} chưa đọc</span>}
              </div>
              
              <div style={{ overflowY: 'auto', flex: 1 }}>
                {notifications.length === 0 ? (
                  <div style={{ padding: '32px 20px', textAlign: 'center', color: 'var(--muted)' }}>
                    <CheckCircle2 size={32} style={{ margin: '0 auto 12px', color: 'var(--line)' }} />
                    <p style={{ margin: 0, fontSize: '13px' }}>Bạn không có thông báo nào.</p>
                  </div>
                ) : (
                  <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
                    {notifications.map((notif, idx) => (
                      <li key={idx} style={{ borderBottom: '1px solid var(--line)' }}>
                        <button 
                          onClick={() => handleNotificationClick(notif)}
                          style={{
                            width: '100%', textAlign: 'left', background: notif.isRead ? '#fff' : 'var(--blue-50)',
                            border: 'none', padding: '12px 16px', cursor: 'pointer',
                            display: 'flex', gap: '12px', alignItems: 'flex-start',
                            transition: 'background 0.15s'
                          }}
                          onMouseOver={(e) => e.currentTarget.style.background = notif.isRead ? 'var(--soft)' : '#f3e8e8'}
                          onMouseOut={(e) => e.currentTarget.style.background = notif.isRead ? '#fff' : 'var(--blue-50)'}
                        >
                          <div style={{ marginTop: '2px' }}>{notif.icon}</div>
                          <div style={{ flex: 1 }}>
                            <div style={{ fontSize: '13px', fontWeight: notif.isRead ? 600 : 700, color: 'var(--ink)', marginBottom: '4px' }}>
                              {notif.title}
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--muted)', lineHeight: 1.4 }}>
                              {notif.desc}
                            </div>
                          </div>
                          {!notif.isRead && (
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--blue)', marginTop: '6px', flexShrink: 0 }} />
                          )}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div className="avatar" style={{ 
            width: '32px', height: '32px', borderRadius: '50%', 
            backgroundColor: 'rgba(255,255,255,0.2)', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <User size={16} />
          </div>
          <span style={{ fontWeight: 600, fontSize: '13px' }}>
            {role === 'admin' ? 'Phòng Đào tạo' : 'Giảng viên'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
