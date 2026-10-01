import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { DataProvider } from './context/DataContext';
import PriorityList from './pages/PriorityList';
import DeadDocs from './pages/DeadDocs';
import Deadlines from './pages/Deadlines';
import Analytics from './pages/Analytics';
import LawEvents from './pages/LawEvents';
import ReviewQueue from './pages/ReviewQueue';
import Search from './pages/Search';
import Chat from './pages/Chat';
import Obligations from './pages/Obligations';
import Thresholds from './pages/Thresholds';
import ImpactGraph from './pages/ImpactGraph';
import Topics from './pages/Topics';
import Admin from './pages/Admin';
import AuditLogs from './pages/AuditLogs';
import RejectedDocs from './pages/RejectedDocs';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children, requireAdmin = false }: { children: React.ReactNode, requireAdmin?: boolean }) => {
  const { token, role, isLoading } = useAuth();
  
  if (isLoading) return <div>Đang tải...</div>;
  if (!token) return <Navigate to="/login" replace />;
  if (requireAdmin && role !== 'admin') return <Navigate to="/search" replace />;
  
  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route path="/" element={<ProtectedRoute><DataProvider><Layout /></DataProvider></ProtectedRoute>}>
              <Route index element={<Navigate to="/priority" replace />} />
              
              {/* Admin only routes */}
              <Route path="priority" element={<ProtectedRoute requireAdmin><PriorityList /></ProtectedRoute>} />
              <Route path="dead-docs" element={<ProtectedRoute requireAdmin><DeadDocs /></ProtectedRoute>} />
              <Route path="deadlines" element={<ProtectedRoute requireAdmin><Deadlines /></ProtectedRoute>} />
              <Route path="events" element={<ProtectedRoute requireAdmin><LawEvents /></ProtectedRoute>} />
              <Route path="review" element={<ProtectedRoute requireAdmin><ReviewQueue /></ProtectedRoute>} />
              <Route path="topics" element={<ProtectedRoute requireAdmin><Topics /></ProtectedRoute>} />
              <Route path="admin" element={<ProtectedRoute requireAdmin><Admin /></ProtectedRoute>} />
              <Route path="audit" element={<ProtectedRoute requireAdmin><AuditLogs /></ProtectedRoute>} />
              <Route path="rejected" element={<ProtectedRoute requireAdmin><RejectedDocs /></ProtectedRoute>} />
              
              {/* Both roles routes */}
              <Route path="analytics" element={<Analytics />} />
              <Route path="search" element={<Search />} />
              <Route path="chat" element={<Chat />} />
              <Route path="obligations" element={<Obligations />} />
              <Route path="thresholds" element={<Thresholds />} />
              <Route path="graph" element={<ImpactGraph />} />
            </Route>
          </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
