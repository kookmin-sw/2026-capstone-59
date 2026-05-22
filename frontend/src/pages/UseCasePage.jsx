import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api/auth'
import { HiMenu, HiX} from 'react-icons/hi'
import PocoLogo from '../components/PocoLogo'
import navStyles from './LandingPage.module.css'
import styles from './UseCasePage.module.css'

const USE_CASES = [
  { title: '사례 1 — Poco - ', url: 'http://pj-kmucd1-09-poco-frontend.s3-website-us-east-1.amazonaws.com/shared/eJaFCWx-QrXiF-3BdjZLOirAMb7kSIVPyzX4nqZu8Uo' },
  { title: '사례 2 — 반려동물 케어 플랫폼', url: 'http://pj-kmucd1-09-poco-frontend.s3-website-us-east-1.amazonaws.com/shared/A-jXWf49y-hHqt9CKeChk4v2eRBmJSv5jum0oY0fxa0' },
  { title: '사례 3 — 실시간 강의실 질문 시스템', url: 'http://pj-kmucd1-09-poco-frontend.s3-website-us-east-1.amazonaws.com/shared/LZG7zgH8f3rKh9elfWu4O9MeQAW_7jZ8Wv8gxAOHSuY' },
  { title: '사례 4 — C++ 프로그래밍 스네이크 게임', url: 'http://pj-kmucd1-09-poco-frontend.s3-website-us-east-1.amazonaws.com/shared/qCZDdOwRUeHTrJ89_m4PgEBMfUW9aXGndC5ZocUzkOc' },
  { title: '사례 5 — 유치원 활동기록지 관리 프로그램', url: 'http://pj-kmucd1-09-poco-frontend.s3-website-us-east-1.amazonaws.com/shared/Ezy8uMxZoI5oflP1FbJMqSe5nt1nvtojC2gPOUkEelU' },
]

export default function UseCasePage() {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [navScrolled, setNavScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

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

  useEffect(() => {
    document.documentElement.style.scrollbarGutter = 'stable'
    return () => { document.documentElement.style.scrollbarGutter = '' }
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

        {/* 햄버거 (좁을 때만 CSS로 표시) */}
        <button className={styles.hamburger} onClick={() => setMenuOpen(true)} aria-label="메뉴 열기">
          <HiMenu size={26} />
        </button>
      </nav>

      {/* 우측 드로어 */}
      <div
        className={`${styles.drawerOverlay} ${menuOpen ? styles.drawerOpen : ''}`}
        onClick={() => setMenuOpen(false)}
      />
      <aside className={`${styles.drawer} ${menuOpen ? styles.drawerOpen : ''}`}>
        <button className={styles.drawerClose} onClick={() => setMenuOpen(false)} aria-label="메뉴 닫기">
          <HiX size={24} />
        </button>
        <ul className={styles.drawerMenu}>
          <li><a href="#scene-1" onClick={(e) => { e.preventDefault(); goToSection('scene-1'); setMenuOpen(false) }}>서비스</a></li>
          <li><a href="#scene-3" onClick={(e) => { e.preventDefault(); goToSection('scene-3'); setMenuOpen(false) }}>기능</a></li>
          <li><a href="#scene-4" onClick={(e) => { e.preventDefault(); goToSection('scene-4'); setMenuOpen(false) }}>근거</a></li>
          <li><a href="#scene-5" onClick={(e) => { e.preventDefault(); goToSection('scene-5'); setMenuOpen(false) }}>사용자</a></li>
          <li><a href="/usecase" onClick={(e) => { e.preventDefault(); navigate('/usecase'); setMenuOpen(false) }}>사용사례</a></li>
        </ul>
        <div className={styles.drawerActions}>
          {isLoggedIn ? <button className={styles.navLogout} onClick={() => { handleLogout(); setMenuOpen(false) }}>로그아웃</button> : null}
          <button className={styles.navCta} onClick={() => { handleStart(); setMenuOpen(false) }}>시작하기</button>
        </div>
      </aside>

      {/* ===== USECASE 본문 ===== */}
      <main className={styles.main}>
        <h1 className={styles.title}>usecase</h1>
        <p className={styles.subtitle}>Poco로 진행된 사용 사례를 살펴보세요.</p>
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