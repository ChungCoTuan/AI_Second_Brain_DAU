import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Bell, User, CheckCircle2, AlertTriangle, CalendarClock, ClipboardList, FileText, Menu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../../context/DataContext';
import { useAuth } from '../../context/AuthContext';

interface HeaderProps {
  onMenu?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenu }) => {
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
    <header className="hdr">
      <div className="hdr-left">
        {onMenu && (
          <button
            className="hdr-menu-btn"
            onClick={onMenu}
            aria-label="Mở menu"
          >
            <Menu size={22} />
          </button>
        )}
        <div className="hdr-brand">Hệ thống Trợ lý Pháp lý</div>
      </div>
      <div className="hdr-right">

        {/* Khối Thông báo */}
        <div ref={dropdownRef} className="hdr-bell-wrap">
          <button
            className={`hdr-bell ${isOpen ? 'open' : ''}`}
            onClick={() => setIsOpen(!isOpen)}
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="hdr-bell-count">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>

          {/* Dropdown UI */}
          {isOpen && (
            <div className="hdr-dropdown">
              <div className="hdr-dropdown-head">
                <h3 className="hdr-dropdown-title">Thông báo</h3>
                {unreadCount > 0 && <span className="hdr-dropdown-unread">{unreadCount} chưa đọc</span>}
              </div>

              <div className="hdr-dropdown-body">
                {notifications.length === 0 ? (
                  <div className="hdr-empty">
                    <CheckCircle2 size={32} style={{ margin: '0 auto 12px', color: 'var(--line)' }} />
                    <p>Bạn không có thông báo nào.</p>
                  </div>
                ) : (
                  <ul className="hdr-notif-list">
                    {notifications.map((notif, idx) => (
                      <li key={idx} className="hdr-notif">
                        <button
                          className={`hdr-notif-btn ${notif.isRead ? '' : 'unread'}`}
                          onClick={() => handleNotificationClick(notif)}
                        >
                          <div className="hdr-notif-icon">{notif.icon}</div>
                          <div className="hdr-notif-body">
                            <div className={`hdr-notif-title ${notif.isRead ? 'read' : ''}`}>
                              {notif.title}
                            </div>
                            <div className="hdr-notif-desc">
                              {notif.desc}
                            </div>
                          </div>
                          {!notif.isRead && <div className="hdr-notif-dot" />}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="hdr-user">
          <div className="hdr-avatar">
            <User size={16} />
          </div>
          <span className="hdr-user-label">
            {role === 'admin' ? 'Phòng Đào tạo' : 'Giảng viên'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
