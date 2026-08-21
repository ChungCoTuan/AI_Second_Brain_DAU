import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ContentAdmin from './pages/ContentAdmin';
import ReportTemplate from './pages/ReportTemplate';
import CitationCompare from './pages/CitationCompare';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

// Component để bảo vệ route Admin
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { role } = useAuth();
  if (role !== 'admin') return <Navigate to="/" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="admin" element={
              <AdminRoute>
                <ContentAdmin />
              </AdminRoute>
            } />
            <Route path="report/:id" element={<ReportTemplate />} />
            <Route path="compare/:id" element={<CitationCompare />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
