import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function AuthCallbackPage() {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/projects', { replace: true })
  }, [])

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <p style={{ color: '#6B6D90', fontFamily: 'Pretendard, sans-serif' }}>로그인 처리 중...</p>
    </div>
  )
}