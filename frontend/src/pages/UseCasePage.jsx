import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api/auth'
import PocoLogo from '../components/PocoLogo'
import navStyles from './LandingPage.module.css'
import styles from './UseCasePage.module.css'

const USE_CASES = [
  { title: '사례 1 — 사이드 프로젝트 기획', url: 'https://...' },
  { title: '사례 2 — 캡스톤 졸업작품', url: 'https://...' },
  { title: '사례 3 — 1인 창업 아이디어', url: 'https://...' },
  { title: '사례 4 — 팀 해커톤', url: 'https://...' },
]

export default function UseCasePage() {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [navScrolled, setNavScrolled] = useState(false)

  useEffect(() => {
    let cancelled = false
    getMe()
      .then(() => { if (!cancelled) setIsLoggedIn(true) })
      .catch(() => { if (!cancelled) setIsLoggedIn(false) })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    const onScroll = () => setNavScrolled(window.scrollY > 12)
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleStart = useCallback(() => {
    navigate(isLoggedIn ? '/projects' : '/login')
  }, [isLoggedIn, navigate])

  const handleLogout = useCallback(async () => {
    try { await logout() } catch { /* */ }
    setIsLoggedIn(false)
  }, [])

  // 랜딩 섹션으로 이동 (랜딩으로 가서 해당 섹션 스크롤)
  const goToSection = useCallback((id) => {
    navigate('/', { state: { scrollTo: id } })
  }, [navigate])

  return (
    <div className={navStyles.page}>
      {/* ===== NAV (LandingPage 복붙) ===== */}
      <nav className={`${navStyles.nav} ${navScrolled ? navStyles.navScrolled : ''}`}>
        <div className={navStyles.brand}>
          <PocoLogo height={25} />
        </div>
        <ul className={navStyles.navMenu}>
          <li><a href="/#scene-1" onClick={(e) => { e.preventDefault(); goToSection('scene-1') }}>서비스</a></li>
          <li><a href="/#scene-3" onClick={(e) => { e.preventDefault(); goToSection('scene-3') }}>기능</a></li>
          <li><a href="/#scene-4" onClick={(e) => { e.preventDefault(); goToSection('scene-4') }}>근거</a></li>
          <li><a href="/#scene-5" onClick={(e) => { e.preventDefault(); goToSection('scene-5') }}>사용자</a></li>
          <li><a href="/usecase" onClick={(e) => e.preventDefault()} aria-current="page">사용사례</a></li>
        </ul>
        <div className={navStyles.navRight}>
          {isLoggedIn ? (
            <button type="button" className={navStyles.navLogout} onClick={handleLogout}>로그아웃</button>
          ) : null}
          <button type="button" className={navStyles.navCta} onClick={handleStart}>시작하기</button>
        </div>
      </nav>

      {/* ===== USECASE 본문 ===== */}
      <main className={styles.main}>
        <h1 className={styles.title}>usecase</h1>
        <p className={styles.subtitle}>Poco로 진행된 실제 사용 사례를 살펴보세요.</p>
        <div className={styles.cards}>
          {USE_CASES.map((uc) => (
            <a
              key={uc.title}
              className={styles.card}
              href={uc.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className={styles.cardTitle}>{uc.title}</span>
              <span className={styles.cardArrow}>→</span>
            </a>
          ))}
        </div>
      </main>
    </div>
  )
}