import { useNavigate } from 'react-router-dom'
import styles from './LandingPage.module.css'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>
      {/* 네비바 */}
      <nav className={styles.nav}>
        <div className={styles.logo}>
          {/* 로고 SVG 추후 추가 */}
          <span>poco</span>
        </div>
        <button className={styles.loginBtn} onClick={() => navigate('/login')}>
          Login
        </button>
      </nav>

      {/* 메인 영역 */}
      <section className={styles.hero}>
        <p className={styles.subtitle}>Your AI Development Partner</p>
        <img src="/poco-logo-text.svg" alt="poco" className={styles.pocoText} />
        <button className={styles.startBtn} onClick={() => navigate('/login')}>
          Get started!
        </button>
      </section>

    </div>
  )
}