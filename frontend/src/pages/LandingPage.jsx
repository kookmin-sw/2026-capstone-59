import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api/auth'
import styles from './LandingPage.module.css'

export default function LandingPage() {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    getMe()
      .then(() => setIsLoggedIn(true))
      .catch(() => setIsLoggedIn(false))
  }, [])

  async function handleLogout() {
    try {
      await logout()
    } catch {
      // 로그아웃 실패해도 일단 클라이언트에서는 로그인 상태 해제
    }
    setIsLoggedIn(false)
  }

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <img src="/poco-logo-text.svg" alt="poco" height={25}/>
        </div>
        {isLoggedIn ? (
          <button className={styles.loginBtn} onClick={handleLogout}>
            로그아웃
          </button>
        ) : (
          <button className={styles.loginBtn} onClick={() => navigate('/login')}>
            로그인
          </button>
        )}
      </nav>

      <section className={styles.hero}>
        <p className={styles.subtitle}>Your AI Development Partner</p>
        <img src="/poco-logo-text.svg" alt="poco" className={styles.pocoText} />
        <button className={styles.startBtn} onClick={() => navigate(isLoggedIn ? '/projects' : '/login')}>
          Get started!
        </button>
      </section>
    </div>
  )
}