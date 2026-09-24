import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewResearchPage } from './pages/NewResearchPage';
import { ResearchHistoryPage } from './pages/ResearchHistoryPage';
import { ResearchDetailsPage } from './pages/ResearchDetailsPage';
import { AgentMonitorPage } from './pages/AgentMonitorPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { DocumentsPage } from './pages/DocumentsPage';
import { ReportsPage } from './pages/ReportsPage';
import { EvaluationsPage } from './pages/EvaluationsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ProfilePage } from './pages/ProfilePage';
import { ProtectedRoute } from './components/ui/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="research" element={<ResearchHistoryPage />} />
          <Route path="research/new" element={<NewResearchPage />} />
          <Route path="research/:id" element={<ResearchDetailsPage />} />
          <Route path="agent-monitor" element={<AgentMonitorPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="evaluations" element={<EvaluationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
