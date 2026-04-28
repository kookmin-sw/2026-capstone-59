import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function AuthCallbackPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const hash = window.location.hash.substring(1)
    const params = new URLSearchParams(hash)

    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')

    if (accessToken) {
      localStorage.setItem('access_token', accessToken)
      if (refreshToken) localStorage.setItem('refresh_token', refreshToken)
      navigate('/projects', { replace: true })
    } else {
      navigate('/login', { replace: true })
    }
  }, [])

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <p style={{ color: '#6B6D90', fontFamily: 'Pretendard, sans-serif' }}>로그인 처리 중...</p>
    </div>
  )
}