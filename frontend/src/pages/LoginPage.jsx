import styles from './LoginPage.module.css'
import { SiGoogle, SiNaver } from 'react-icons/si'
import { RiKakaoTalkFill } from 'react-icons/ri'


export default function LoginPage() {
  function handleLogin(provider) {
    window.location.href = `/api/auth/${provider}/login`
  }

  return (
    <div className={styles.page}>
      {/* 네비바 */}
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <span>poco</span>
        </div>
      </nav>

      {/* 로그인 영역 */}
      <section className={styles.container}>
        <h1 className={styles.title}>로그인</h1>

        <div className={styles.btnGroup}>
          
          <button className={`${styles.socialBtn} ${styles.kakao}`} onClick={() => handleLogin('kakao')}>
            <RiKakaoTalkFill size={35} /> Kakao로 시작하기
          </button>
          <button className={`${styles.socialBtn} ${styles.google}`} onClick={() => handleLogin('google')}>
            <img src="/google-logo.svg" width={27} height={27} /> Google로 시작하기
          </button>
          <button className={`${styles.socialBtn} ${styles.naver}`} onClick={() => handleLogin('naver')}>
            <SiNaver size={25} /> Naver로 시작하기
          </button>
        </div>
      </section>
    </div>
  )
}