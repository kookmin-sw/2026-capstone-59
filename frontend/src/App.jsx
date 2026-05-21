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
  return (
    <BrowserRouter>
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