import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import PriorityList from './pages/PriorityList';
import DeadDocs from './pages/DeadDocs';
import Deadlines from './pages/Deadlines';
import Analytics from './pages/Analytics';
import LawEvents from './pages/LawEvents';
import ReviewQueue from './pages/ReviewQueue';
import Search from './pages/Search';
import Obligations from './pages/Obligations';
import Thresholds from './pages/Thresholds';
import ImpactGraph from './pages/ImpactGraph';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/priority" replace />} />
          <Route path="priority" element={<PriorityList />} />
          <Route path="dead-docs" element={<DeadDocs />} />
          <Route path="deadlines" element={<Deadlines />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="events" element={<LawEvents />} />
          <Route path="review" element={<ReviewQueue />} />
          <Route path="search" element={<Search />} />
          <Route path="obligations" element={<Obligations />} />
          <Route path="thresholds" element={<Thresholds />} />
          <Route path="graph" element={<ImpactGraph />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
