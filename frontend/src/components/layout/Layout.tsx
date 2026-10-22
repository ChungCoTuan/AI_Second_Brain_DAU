import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { DetailProvider } from '../../context/DetailContext';
import DocumentDetailDrawer from '../shared/DocumentDetailDrawer';

const MOBILE_QUERY = '(max-width: 768px)';

const Layout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(
    typeof window !== 'undefined' ? window.matchMedia(MOBILE_QUERY).matches : false
  );
  const location = useLocation();

  useEffect(() => {
    const mq = window.matchMedia(MOBILE_QUERY);
    const update = () => setIsMobile(mq.matches);
    update();
    mq.addEventListener('change', update);
    return () => mq.removeEventListener('change', update);
  }, []);

  // Khi chuyển trang hoặc phóng to màn hình, đóng drawer menu.
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!isMobile) setMobileOpen(false);
  }, [isMobile]);

  return (
    <DetailProvider>
      <div className="app-container" style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg)' }}>
        <Sidebar mobile={isMobile} open={mobileOpen} onClose={() => setMobileOpen(false)} />

        {isMobile && mobileOpen && (
          <div
            className="sidebar-backdrop"
            onClick={() => setMobileOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(15,23,42,.45)',
              zIndex: 49,
            }}
          />
        )}

        <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', minWidth: 0 }}>
          <Header onMenu={() => setMobileOpen(true)} />
          <main className="page-content" style={{ flex: 1, overflowY: 'auto' }}>
            <Outlet />
          </main>
        </div>
        <DocumentDetailDrawer />
      </div>
    </DetailProvider>
  );
};

export default Layout;
