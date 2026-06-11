import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import ProjectListPage from './pages/ProjectListPage'
import TrashPage from './pages/TrashPage'
import CreateProjectPage from './pages/CreateProjectPage'
import AuthCallbackPage from './pages/AuthCallbackPage'
import CanvasPage from './pages/CanvasPage'
import SharedCanvasPage from './pages/SharedCanvasPage'
import PrivateRoute from './components/PrivateRoute'
import UseCasePage from './pages/UseCasePage'

export default function App() {
  // GitHub Pages 서브경로 배포 시 BASE_URL(예: /2026-capstone-59/landing/)을
  // 라우터 basename 으로 사용. 일반 배포(base '/')에서는 빈 문자열이 되어 동작 동일.
  const basename = import.meta.env.BASE_URL.replace(/\/$/, '')
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/usecase" element={<UseCasePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/projects" element={<PrivateRoute><ProjectListPage /></PrivateRoute>} />
        <Route path="/projects/create" element={<PrivateRoute><CreateProjectPage /></PrivateRoute>} />
        <Route path="/projects/trash" element={<PrivateRoute><TrashPage /></PrivateRoute>} />
        <Route path="/canvas/:projectId" element={<PrivateRoute><CanvasPage /></PrivateRoute>} />
        <Route path="/shared/:shareToken" element={<SharedCanvasPage />} />
      </Routes>
    </BrowserRouter>
  )
}