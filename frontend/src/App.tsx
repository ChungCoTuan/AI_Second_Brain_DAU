import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import TopicDashboard from './pages/TopicDashboard';
import ReviewService from './pages/ReviewService';
import ReportTemplate from './pages/ReportTemplate';
import DocumentDetail from './pages/DocumentDetail';
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
            
            {/* Màn hình 2 & 5 (Chỉ Admin) */}
            <Route path="topics" element={
              <AdminRoute>
                <TopicDashboard />
              </AdminRoute>
            } />
            <Route path="review" element={
              <AdminRoute>
                <ReviewService />
              </AdminRoute>
            } />
            
            {/* Màn hình 4 & 6 (Gộp chung trong Chi tiết VB) */}
            <Route path="document/:id" element={<DocumentDetail />} />
            
            {/* Màn hình 3 */}
            <Route path="report/:id" element={<ReportTemplate />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
