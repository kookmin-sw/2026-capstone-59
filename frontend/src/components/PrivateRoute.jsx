import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { getMe } from '../api/auth'

const DEV_BYPASS = import.meta.env.DEV  // 로컬 개발 환경에서만 true

export default function PrivateRoute({ children }) {
  const [status, setStatus] = useState(DEV_BYPASS ? 'ok' : 'loading')

  useEffect(() => {
    if (DEV_BYPASS) return
    getMe()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('unauth'))
  }, [])

  if (status === 'loading') return null
  if (status === 'unauth') return <Navigate to="/login" replace />
  return children
}