import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { DetailProvider } from '../../context/DetailContext';
import DocumentDetailDrawer from '../shared/DocumentDetailDrawer';

const Layout: React.FC = () => {
  return (
    <DetailProvider>
      <div className="app-container" style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg)' }}>
        <Sidebar />
        <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
          <Header />
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
