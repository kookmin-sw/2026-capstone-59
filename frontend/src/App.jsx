import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import ProjectListPage from './pages/ProjectListPage'
import CreateProjectPage from './pages/CreateProjectPage'
import AuthCallbackPage from './pages/AuthCallbackPage'
import CanvasPage from './pages/CanvasPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/projects" element={<ProjectListPage />} />
        <Route path="/projects/create" element={<CreateProjectPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/canvas/:projectId" element={<CanvasPage />} />
      </Routes>
    </BrowserRouter>
  )
}