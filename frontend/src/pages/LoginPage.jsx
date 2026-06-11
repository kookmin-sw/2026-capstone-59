import styles from './LoginPage.module.css'
import { SiGoogle, SiNaver } from 'react-icons/si'
import { resolveApiUrl } from '../api/_client'


export default function LoginPage() {
  function handleLogin(provider) {
    window.location.href = resolveApiUrl('GET', `/auth/${provider}/login`)
  }

  return (
    <div className={styles.page}>
      {/* 네비바 */}
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <object data={`${import.meta.env.BASE_URL}poco-logo-text.svg`} alt="poco" height={25}></object>
        </div>
      </nav>

      {/* 로그인 영역 */}
      <section className={styles.container}>
        <h1 className={styles.title}>로그인</h1>

        <div className={styles.btnGroup}>
          <button className={`${styles.socialBtn} ${styles.google}`} onClick={() => handleLogin('google')}>
            <object data={`${import.meta.env.BASE_URL}google-logo.svg`} width={27} height={27}></object> Google로 시작하기
          </button>
          <button className={`${styles.socialBtn} ${styles.naver}`} onClick={() => handleLogin('naver')}>
            <SiNaver size={25} /> Naver로 시작하기
          </button>
        </div>
      </section>
    </div>
  )
}