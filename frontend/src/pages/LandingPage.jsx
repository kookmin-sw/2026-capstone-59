import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api/auth'
import styles from './LandingPage.module.css'

// ===== Design tokens =====
const tokens = {
  primary: '#7C5CFF',
  primaryHover: '#6A47FF',
  primarySoft: '#F4F1FF',
  primarySoftBorder: '#E2DBFF',
  bg: '#FAF8FF',
  bgGradient:
    'radial-gradient(60% 60% at 50% 0%, #EEEAFF 0%, #FAF8FF 60%, #FFFFFF 100%)',
  ink: '#11121A',
  body: '#3C3C48',
  sub: '#7A7A88',
  border: '#ECECF2',
  hairline: '#F0EEF7',
  green: '#22A06B',
  greenSoft: '#E8F6EE',
}

const fontStack =
  "'Pretendard', 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
const monoStack = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

// ===== Hooks =====
function useInView(options = {}) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true)
          io.disconnect()
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -8% 0px', ...options }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return [ref, inView]
}

// ===== Atoms =====
function Reveal({ children, delay = 0, y = 28, style = {} }) {
  const [ref, inView] = useInView()
  return (
    <div
      ref={ref}
      className={`${styles.reveal} ${inView ? styles.revealVisible : ''}`}
      style={{ transitionDelay: `${delay}s`, '--poco-reveal-y': `${y}px`, ...style }}
    >
      {children}
    </div>
  )
}

function Pill({ children }) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 7,
        padding: '5px 12px',
        background: tokens.primarySoft,
        color: tokens.primary,
        fontSize: 12,
        fontWeight: 600,
        borderRadius: 99,
        letterSpacing: '-0.01em',
        whiteSpace: 'nowrap',
        fontFamily: fontStack,
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: 99, background: tokens.primary }} />
      {children}
    </span>
  )
}

function PrimaryCTA({ children, size = 'md', onClick, glow = false }) {
  const sizes = {
    sm: { h: 40, px: 18, fs: 13.5 },
    md: { h: 48, px: 22, fs: 14.5 },
    lg: { h: 56, px: 28, fs: 16 },
  }
  const s = sizes[size]
  return (
    <button
      onClick={onClick}
      className={glow ? styles.ctaGlow : ''}
      style={{
        height: s.h,
        padding: `0 ${s.px}px`,
        background: tokens.primary,
        color: '#fff',
        border: 'none',
        borderRadius: 99,
        fontSize: s.fs,
        fontWeight: 600,
        letterSpacing: '-0.01em',
        cursor: 'pointer',
        fontFamily: fontStack,
        whiteSpace: 'nowrap',
        boxShadow:
          '0 1px 2px rgba(124,92,255,0.3), 0 8px 24px -8px rgba(124,92,255,0.45), inset 0 -1px 0 rgba(0,0,0,0.06)',
      }}
    >
      {children}
    </button>
  )
}

function GhostCTA({ children, size = 'md', onClick }) {
  const sizes = {
    sm: { h: 40, px: 16, fs: 13.5 },
    md: { h: 48, px: 20, fs: 14.5 },
    lg: { h: 56, px: 24, fs: 16 },
  }
  const s = sizes[size]
  return (
    <button
      onClick={onClick}
      style={{
        height: s.h,
        padding: `0 ${s.px}px`,
        background: 'transparent',
        color: tokens.ink,
        border: `1px solid ${tokens.border}`,
        borderRadius: 99,
        fontSize: s.fs,
        fontWeight: 500,
        cursor: 'pointer',
        fontFamily: fontStack,
        whiteSpace: 'nowrap',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
      }}
    >
      {children}
    </button>
  )
}

function Eyebrow({ children, align = 'left' }) {
  return (
    <div
      style={{
        fontSize: 12.5,
        color: tokens.primary,
        fontWeight: 600,
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        fontFamily: monoStack,
        textAlign: align,
      }}
    >
      {children}
    </div>
  )
}

function FloatingDots() {
  const dots = [
    { x: 8, y: 18, s: 8, o: 0.5, d: 0 },
    { x: 92, y: 12, s: 14, o: 0.35, d: 1.5 },
    { x: 18, y: 78, s: 10, o: 0.4, d: 2.8 },
    { x: 88, y: 68, s: 18, o: 0.25, d: 0.8 },
    { x: 4, y: 50, s: 6, o: 0.5, d: 3.5 },
    { x: 75, y: 88, s: 12, o: 0.3, d: 2.1 },
  ]
  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      {dots.map((d, i) => (
        <span
          key={i}
          style={{
            position: 'absolute',
            left: `${d.x}%`,
            top: `${d.y}%`,
            width: d.s,
            height: d.s,
            borderRadius: 99,
            background: '#C7BBFF',
            opacity: d.o,
            animation: `pocoFloat ${5 + (i % 3)}s ease-in-out ${d.d}s infinite`,
          }}
        />
      ))}
    </div>
  )
}

function InlineTree({ width = 240, height = 90 }) {
  const nodes = [
    { x: 30, y: 100 }, { x: 110, y: 60 }, { x: 110, y: 140 },
    { x: 200, y: 30, required: true }, { x: 200, y: 90 }, { x: 200, y: 170 },
    { x: 290, y: 60 }, { x: 290, y: 130 },
  ]
  const edges = [[0,1],[0,2],[1,3],[1,4],[2,5],[4,6],[5,7]]
  const accentNode = 2
  return (
    <svg width={width} height={height} viewBox="0 0 320 200" fill="none">
      {edges.map(([a, b], i) => (
        <path
          key={i}
          d={`M${nodes[a].x} ${nodes[a].y} C${(nodes[a].x + nodes[b].x) / 2} ${nodes[a].y}, ${(nodes[a].x + nodes[b].x) / 2} ${nodes[b].y}, ${nodes[b].x} ${nodes[b].y}`}
          stroke="#D7CCFF"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      ))}
      {nodes.map((n, i) =>
        n.required ? (
          <g key={i} transform={`translate(${n.x} ${n.y}) rotate(45)`}>
            <rect x={-10} y={-10} width={20} height={20} rx={3} fill="#7C5CFF" stroke="#fff" strokeWidth="3" />
          </g>
        ) : (
          <g key={i}>
            {i === accentNode && (
              <circle
                cx={n.x} cy={n.y} r={13} fill="#7C5CFF"
                style={{ transformOrigin: `${n.x}px ${n.y}px`, animation: 'pocoPulse 2.4s ease-out infinite' }}
              />
            )}
            <circle
              cx={n.x} cy={n.y}
              r={i === accentNode ? 13 : 10}
              fill={i === accentNode ? '#7C5CFF' : '#fff'}
              stroke={i === accentNode ? '#fff' : '#C7BBFF'}
              strokeWidth={i === accentNode ? 3 : 2}
            />
          </g>
        )
      )}
    </svg>
  )
}

function StageStrip() {
  const stages = [
    { n: '01', ko: '아이디어 구체화', en: 'Ideation' },
    { n: '02', ko: '프로젝트 계획', en: 'Planning' },
    { n: '03', ko: '요구사항 정의', en: 'Requirement' },
    { n: '04', ko: '설계', en: 'Design' },
    { n: '05', ko: '개발', en: 'Development' },
    { n: '06', ko: '테스트 및 검증', en: 'Test' },
  ]
  const [ref, inView] = useInView({ threshold: 0.25 })
  return (
    <div ref={ref} style={{ position: 'relative', padding: '0 20px' }}>
      <svg
        style={{ position: 'absolute', left: 50, right: 50, top: 30, width: 'calc(100% - 100px)', height: 2, pointerEvents: 'none' }}
        viewBox="0 0 1000 2" preserveAspectRatio="none"
      >
        <line
          x1="0" y1="1" x2="1000" y2="1"
          stroke={tokens.primarySoftBorder} strokeWidth="2" strokeDasharray="6 6"
          style={{ strokeDasharray: '1000 1000', strokeDashoffset: inView ? 0 : 1000, transition: 'stroke-dashoffset 1.8s ease-out 0.3s' }}
        />
      </svg>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 16, position: 'relative' }}>
        {stages.map((s, i) => (
          <div
            key={s.n}
            style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center',
              opacity: inView ? 1 : 0,
              transform: inView ? 'translateY(0)' : 'translateY(16px)',
              transition: `opacity 0.6s ease ${0.5 + i * 0.12}s, transform 0.6s ease ${0.5 + i * 0.12}s`,
            }}
          >
            <div
              className={styles.stageNumber}
              style={{
                width: 60, height: 60, borderRadius: 99,
                background: '#fff',
                border: `2px solid ${tokens.primarySoftBorder}`,
                color: tokens.primary,
                display: 'grid', placeItems: 'center',
                fontFamily: monoStack, fontSize: 14, fontWeight: 700,
                boxShadow: '0 2px 4px rgba(20,18,40,0.04)',
              }}
            >
              {s.n}
            </div>
            <div style={{ fontSize: 14, fontWeight: 600, marginTop: 14, color: tokens.ink, letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>{s.ko}</div>
            <div style={{ fontSize: 11, color: tokens.sub, marginTop: 4, fontFamily: monoStack, letterSpacing: '0.04em' }}>{s.en}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ===== Feature data =====
const FEATURES = [
  { n: '01', title: 'AI 기반 Step Flow 생성', en: 'Step Flow',
    body: '프로젝트 맥락에 맞춰 AI가 다음 한 걸음의 선택지 3개를 제시합니다. 검증된 6단계 프로세스 위에서 캔버스가 자랍니다.',
    quote: '막연함을 "다음 한 걸음"으로', icon: 'compass' },
  { n: '02', title: 'Step별 클릭 어시스턴트', en: 'Side Panel Guide',
    body: '노드를 클릭하면 멘토링·용어사전·노션 템플릿이 펼쳐집니다. 딱딱한 방법론 문서 대신 맥락에 맞는 가이드.',
    quote: '곁에 있는 시니어 멘토', icon: 'book' },
  { n: '03', title: 'Footprint — 의사결정 궤적', en: 'Decision Tree',
    body: '분기점으로 자유롭게 돌아가 AI 추천을 다시 받을 수 있습니다. 끝날 때쯤엔 "무엇을 왜 만들었는지" 스스로 설명할 수 있습니다.',
    quote: '되돌아갈 수 있는 선택', icon: 'tree', highlight: true },
]
const PREVIEW_NOTES = [
  ['다음 한 걸음, 선택지 3개', '사용자는 가장 공감되는 것을 클릭만'],
  ['사이드패널 멘토링·용어', '맥락에 맞는 가이드가 자동으로'],
  ['분기·롤백 가능', '이전 결정으로 돌아가 다시 추천'],
]

function FeatureIcon({ kind }) {
  if (kind === 'tree') return <InlineTree width={240} height={90} />
  if (kind === 'compass') return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
      <circle cx="32" cy="32" r="22" stroke="#7C5CFF" strokeWidth="2" />
      <circle cx="32" cy="32" r="4" fill="#7C5CFF" />
      <path d="M32 14 L32 22 M32 42 L32 50 M14 32 L22 32 M42 32 L50 32" stroke="#C7BBFF" strokeWidth="2" strokeLinecap="round" />
      <path d="M28 28 L36 36 M36 28 L28 36" stroke="#7C5CFF" strokeWidth="1.5" strokeLinecap="round" opacity="0.4" />
    </svg>
  )
  if (kind === 'book') return (
    <svg width="80" height="64" viewBox="0 0 80 64" fill="none">
      <rect x="10" y="14" width="28" height="36" rx="3" fill="#fff" stroke="#7C5CFF" strokeWidth="2" />
      <rect x="42" y="14" width="28" height="36" rx="3" fill="#F4F1FF" stroke="#7C5CFF" strokeWidth="2" />
      <path d="M16 22 L32 22 M16 28 L32 28 M16 34 L26 34" stroke="#C7BBFF" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M48 22 L64 22 M48 28 L64 28 M48 34 L58 34" stroke="#7C5CFF" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
  return null
}

// ===== Main page =====
export default function LandingPage() {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    getMe().then(() => setIsLoggedIn(true)).catch(() => setIsLoggedIn(false))
  }, [])

  const handleStart = useCallback(() => {
    navigate(isLoggedIn ? '/projects' : '/login')
  }, [isLoggedIn, navigate])

  const handleLogout = useCallback(async () => {
    try { await logout() } catch { /* ignore */ }
    setIsLoggedIn(false)
  }, [])

  const handleGitHub = useCallback(() => {
    window.open('https://github.com/kookmin-sw/2026-capstone-59', '_blank', 'noopener')
  }, [])

  // Smooth section-by-section scrolling
  useEffect(() => {
    const sections = [...document.querySelectorAll(`.${styles.snapSection}`)]
    if (!sections.length) return

    let currentIdx = 0
    let isAnimating = false
    let lastWheelAt = 0
    const DURATION = 800

    const easeInOutCubic = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

    function animateTo(targetY) {
      const startY = window.scrollY
      const distance = targetY - startY
      if (Math.abs(distance) < 1) { isAnimating = false; return }
      isAnimating = true
      const startTime = performance.now()
      function step(now) {
        const t = Math.min((now - startTime) / DURATION, 1)
        window.scrollTo(0, startY + distance * easeInOutCubic(t))
        if (t < 1) requestAnimationFrame(step)
        else isAnimating = false
      }
      requestAnimationFrame(step)
    }

    function goTo(idx) {
      idx = Math.max(0, Math.min(sections.length - 1, idx))
      if (isAnimating || idx === currentIdx) return
      currentIdx = idx
      const rect = sections[idx].getBoundingClientRect()
      animateTo(window.scrollY + rect.top)
    }

    function syncIdx() {
      let best = 0, bestDist = Infinity
      sections.forEach((s, i) => {
        const r = s.getBoundingClientRect()
        const dist = Math.abs(r.top)
        if (dist < bestDist) { bestDist = dist; best = i }
      })
      currentIdx = best
    }
    syncIdx()

    function onWheel(e) {
      if (isAnimating) { e.preventDefault(); return }
      if (Math.abs(e.deltaY) < 4) return
      const now = performance.now()
      if (now - lastWheelAt < 80) { e.preventDefault(); return }
      lastWheelAt = now
      e.preventDefault()
      goTo(currentIdx + (e.deltaY > 0 ? 1 : -1))
    }
    function onKey(e) {
      const navKeys = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', ' ', 'Home', 'End']
      if (!navKeys.includes(e.key)) return
      const tag = document.activeElement?.tagName ?? ''
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return
      e.preventDefault()
      if (isAnimating) return
      if (e.key === 'Home') goTo(0)
      else if (e.key === 'End') goTo(sections.length - 1)
      else if (e.key === 'ArrowUp' || e.key === 'PageUp') goTo(currentIdx - 1)
      else goTo(currentIdx + 1)
    }
    let touchStartY = 0, touchDelta = 0
    function onTouchStart(e) { touchStartY = e.touches[0].clientY; touchDelta = 0 }
    function onTouchMove(e) {
      if (isAnimating) { e.preventDefault(); return }
      touchDelta = touchStartY - e.touches[0].clientY
    }
    function onTouchEnd() {
      if (isAnimating) return
      if (Math.abs(touchDelta) > 40) goTo(currentIdx + (touchDelta > 0 ? 1 : -1))
    }
    function onAnchorClick(e) {
      const a = e.target.closest('a[href^="#"]')
      if (!a) return
      const id = a.getAttribute('href').slice(1)
      if (!id) return
      const target = sections.find((s) => s.id === id)
      if (target) { e.preventDefault(); goTo(sections.indexOf(target)) }
    }

    window.addEventListener('wheel', onWheel, { passive: false })
    window.addEventListener('keydown', onKey)
    window.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchmove', onTouchMove, { passive: false })
    window.addEventListener('touchend', onTouchEnd)
    document.addEventListener('click', onAnchorClick)
    return () => {
      window.removeEventListener('wheel', onWheel)
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('touchstart', onTouchStart)
      window.removeEventListener('touchmove', onTouchMove)
      window.removeEventListener('touchend', onTouchEnd)
      document.removeEventListener('click', onAnchorClick)
    }
  }, [])

  return (
    <div style={{ width: '100%', background: tokens.bg, fontFamily: fontStack, color: tokens.ink }}>
      {/* Sticky Nav */}
      <div className={styles.navSticky}>
        <header
          style={{
            width: '100%', padding: '20px 56px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            background: 'transparent', boxSizing: 'border-box',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img src="/poco-logo-text.svg" alt="poco" height={28} />
          </div>
          <nav style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
            <a href="#features" style={navLinkStyle}>기능</a>
            <a href="#preview" style={navLinkStyle}>제품 미리보기</a>
            <a href="https://github.com/kookmin-sw/2026-capstone-59" target="_blank" rel="noopener noreferrer" style={navLinkStyle}>GitHub</a>
            {isLoggedIn ? (
              <GhostCTA size="sm" onClick={handleLogout}>로그아웃</GhostCTA>
            ) : null}
            <PrimaryCTA size="sm" onClick={handleStart}>Get started!</PrimaryCTA>
          </nav>
        </header>
      </div>

      {/* ===== HERO ===== */}
      <section className={styles.snapSection} style={{ textAlign: 'center', background: tokens.bgGradient, overflow: 'hidden' }}>
        <FloatingDots />
        <div style={{ position: 'relative', maxWidth: 880, margin: '0 auto' }}>
          <div className={styles.fadeUp} style={{ animationDelay: '0.05s' }}>
            <Eyebrow align="center">Your AI Development Partner</Eyebrow>
          </div>

          <div className={styles.fadeScale} style={{ display: 'flex', justifyContent: 'center', margin: '24px 0 8px', animationDelay: '0.18s' }}>
            <img src="/poco-logo-text.svg" alt="poco" style={{ height: 220, width: 'auto' }} />
          </div>

          <h1 className={styles.fadeUp} style={{
            fontSize: 52, lineHeight: 1.18, letterSpacing: '-0.035em', fontWeight: 700,
            margin: '16px 0 18px', color: tokens.ink, animationDelay: '0.35s',
          }}>
            조금씩, 한 걸음씩 —<br />
            아이디어를 설계까지 쌓아가는 <span style={{ color: tokens.primary }}>사고의 캔버스</span>
          </h1>

          <p className={styles.fadeUp} style={{
            fontSize: 18, lineHeight: 1.6, color: tokens.sub, maxWidth: 620,
            margin: '0 auto 36px', letterSpacing: '-0.01em', animationDelay: '0.5s',
          }}>
            AI가 다 만들어주는 시대, <b style={{ color: tokens.ink, fontWeight: 600 }}>무엇을·왜 만들지</b> 정의하고 계신가요?<br />
            Poco가 다음 한 걸음의 선택지를 제시하고, 의사결정의 궤적을 트리로 시각화해드립니다.
          </p>

          <div className={styles.fadeUp} style={{ display: 'flex', gap: 12, justifyContent: 'center', alignItems: 'center', animationDelay: '0.65s' }}>
            <PrimaryCTA size="lg" onClick={handleStart} glow>Get started!</PrimaryCTA>
            <GhostCTA size="lg" onClick={handleGitHub}>
              View on GitHub <span style={{ color: tokens.sub }}>↗</span>
            </GhostCTA>
          </div>

          <div className={styles.fadeIn} style={{
            marginTop: 56, display: 'inline-flex', gap: 14, alignItems: 'center',
            color: tokens.sub, fontSize: 13, fontFamily: monoStack, whiteSpace: 'nowrap',
            animationDelay: '0.85s',
          }}>
            <span style={{ display: 'inline-block', width: 28, height: 1, background: tokens.border }} />
            DOJ SDLC · SWEBOK V4.0a 기반
            <span style={{ display: 'inline-block', width: 28, height: 1, background: tokens.border }} />
          </div>
        </div>

        <div className={styles.fadeIn} style={{
          marginTop: 80, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
          color: tokens.sub, fontSize: 11, fontFamily: monoStack, letterSpacing: '0.16em',
          textTransform: 'uppercase', animationDelay: '1.1s',
        }}>
          scroll
          <span style={{
            width: 1, height: 32,
            background: `linear-gradient(to bottom, ${tokens.primarySoftBorder}, transparent)`,
            animation: 'pocoFloat 2.4s ease-in-out infinite',
          }} />
        </div>
      </section>

      {/* ===== PROBLEM ===== */}
      <section className={styles.snapSection} style={{ background: '#fff', padding: '80px 56px' }}>
        <div style={{ maxWidth: 980, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <Eyebrow>The Problem</Eyebrow>
            <h2 style={{ fontSize: 42, lineHeight: 1.25, letterSpacing: '-0.03em', fontWeight: 700, margin: '16px 0 0', maxWidth: 720 }}>
              AI는 <span style={{ color: tokens.primary }}>How</span>를 만들어준다.<br />
              그렇다면 <span style={{ color: tokens.primary }}>What·Why</span>는?
            </h2>
          </Reveal>

          <div style={{ marginTop: 64, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
            <Reveal delay={0.05}>
              <div style={{
                padding: 32, background: '#FAFAFD',
                border: `1px solid ${tokens.border}`, borderRadius: 18, height: '100%',
              }}>
                <div style={{ fontSize: 13, color: tokens.sub, fontFamily: monoStack, letterSpacing: '0.06em' }}>AI가 잘하는 것</div>
                <div style={{ fontSize: 22, fontWeight: 700, marginTop: 10, letterSpacing: '-0.02em' }}>How — 어떻게 만들지</div>
                <div style={{ fontSize: 15, color: tokens.body, marginTop: 14, lineHeight: 1.65 }}>
                  코드도, 디자인도, 문서도 엄청난 속도로 만들어 줍니다. 손은 더 이상 병목이 아닙니다.
                </div>
              </div>
            </Reveal>
            <Reveal delay={0.2}>
              <div style={{
                padding: 32, background: tokens.primarySoft,
                border: `1px solid ${tokens.primarySoftBorder}`, borderRadius: 18, height: '100%',
              }}>
                <div style={{ fontSize: 13, color: tokens.primary, fontFamily: monoStack, letterSpacing: '0.06em' }}>여전히 우리의 몫</div>
                <div style={{ fontSize: 22, fontWeight: 700, marginTop: 10, letterSpacing: '-0.02em', color: tokens.ink }}>
                  What · Why — 무엇을 왜 만들지
                </div>
                <div style={{ fontSize: 15, color: tokens.body, marginTop: 14, lineHeight: 1.65 }}>
                  "왜 이 결정을 했는가"는 AI가 대신해줄 수 없습니다. Poco는 이 영역을 구조적으로 수행할 수 있게 돕습니다.
                </div>
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.15}>
            <blockquote style={{
              marginTop: 56, marginInline: 0, padding: '28px 32px',
              borderLeft: `3px solid ${tokens.primary}`, background: '#FBFAFF',
              borderRadius: '0 14px 14px 0', fontSize: 18, lineHeight: 1.65,
              color: tokens.body, letterSpacing: '-0.01em', fontStyle: 'italic',
            }}>
              "AI한테 뭐라도 시켜보려는데… 정작 내가 뭘 만들고 싶은 건지부터 모르겠다.<br />
              용어도 어렵고, 빠뜨린 단계는 없는지 불안하고, 사람들에게 '왜 이 결정을 했는지' 설명할 자신도 없다."
            </blockquote>
          </Reveal>
        </div>
      </section>

      {/* ===== 6 STAGE ===== */}
      <section className={styles.snapSection} style={{ background: tokens.bg, padding: '80px 56px' }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 72 }}>
              <Eyebrow align="center">6 Stage Process</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 10px' }}>
                검증된 방법론을 자연스럽게
              </h2>
              <p style={{ fontSize: 15, color: tokens.sub, margin: 0, lineHeight: 1.65 }}>
                DOJ SDLC 10단계를 초심자·소규모 팀에 맞게 재구성한 6단계 프로세스.<br />
                각 단계마다 핵심 관문에서 멘토링과 템플릿이 제공됩니다.
              </p>
            </div>
          </Reveal>
          <StageStrip />
        </div>
      </section>

      {/* ===== FEATURES ===== */}
      <section id="features" className={styles.snapSection} style={{ background: '#fff', padding: '80px 56px' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 72 }}>
              <Eyebrow align="center">3 Core Features</Eyebrow>
              <h2 style={{ fontSize: 42, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 0' }}>
                다음 한 걸음, Poco가 함께
              </h2>
            </div>
          </Reveal>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {FEATURES.map((f, i) => (
              <Reveal key={f.n} delay={i * 0.12} y={36}>
                <div className={styles.card} style={{
                  padding: 28, background: '#fff',
                  border: `1px solid ${f.highlight ? tokens.primarySoftBorder : tokens.border}`,
                  borderRadius: 20,
                  boxShadow: f.highlight
                    ? '0 1px 2px rgba(124,92,255,0.08), 0 20px 40px -20px rgba(124,92,255,0.25)'
                    : '0 1px 2px rgba(20,18,40,0.03)',
                  display: 'flex', flexDirection: 'column', height: '100%',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22 }}>
                    <span style={{
                      fontFamily: monoStack, fontSize: 13, color: tokens.primary,
                      background: tokens.primarySoft, padding: '4px 10px', borderRadius: 7, fontWeight: 600,
                    }}>{f.n}</span>
                    <span style={{ fontSize: 11, color: tokens.sub, fontFamily: monoStack, letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>{f.en}</span>
                  </div>

                  <div style={{
                    height: 96, marginBottom: 22, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: '#FAFAFD', borderRadius: 14, border: `1px dashed ${tokens.border}`,
                  }}>
                    <FeatureIcon kind={f.icon} />
                  </div>

                  <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 10 }}>{f.title}</div>
                  <div style={{ fontSize: 14, color: tokens.body, lineHeight: 1.65, flex: 1 }}>{f.body}</div>
                  <div style={{
                    marginTop: 20, paddingTop: 16, borderTop: `1px solid ${tokens.hairline}`,
                    fontSize: 13, color: tokens.primary, fontFamily: monoStack, letterSpacing: '-0.005em',
                  }}>— {f.quote}</div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ===== PRODUCT PREVIEW ===== */}
      <section id="preview" className={styles.snapSection} style={{ background: tokens.bg, padding: '80px 56px' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 40, gap: 32, flexWrap: 'wrap' }}>
              <div>
                <Pill>Live Canvas</Pill>
                <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '14px 0 0', maxWidth: 540 }}>
                  캔버스 안에서 사고는 <span style={{ color: tokens.primary }}>트리</span>로 자란다
                </h2>
              </div>
              <p style={{ fontSize: 15, color: tokens.body, lineHeight: 1.7, maxWidth: 360, margin: 0 }}>
                선택의 궤적이 캔버스 위에 그대로 남습니다. 분기점으로 돌아가 다른 길을 다시 탐색해도, 모든 흔적이 자산으로 보존됩니다.
              </p>
            </div>
          </Reveal>

          <Reveal delay={0.1} y={40}>
            <div style={{
              position: 'relative', borderRadius: 24,
              background: 'linear-gradient(180deg, #F4F1FF 0%, #FAF8FF 100%)',
              border: `1px solid ${tokens.primarySoftBorder}`, padding: 14,
              boxShadow: '0 30px 60px -30px rgba(124,92,255,0.3)',
            }}>
              <div style={{
                borderRadius: 16, overflow: 'hidden', background: '#fff',
                height: 'min(540px, 52vh)',
              }}>
                <img
                  src="/canvas-preview.png"
                  alt="Poco 캔버스 미리보기"
                  style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                />
              </div>
            </div>
          </Reveal>

          <div style={{ marginTop: 28, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            {PREVIEW_NOTES.map(([t, s], i) => (
              <Reveal key={t} delay={0.05 + i * 0.1}>
                <div style={{ padding: '12px 18px', borderLeft: `2px solid ${tokens.primarySoftBorder}` }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: tokens.ink }}>{t}</div>
                  <div style={{ fontSize: 13, color: tokens.sub, marginTop: 4 }}>{s}</div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CTA + FOOTER ===== */}
      <section className={`${styles.snapSection} ${styles.hasFooter}`} style={{ background: '#fff' }}>
        <div className={styles.snapCta}>
          <div style={{ maxWidth: 720, margin: '0 auto', textAlign: 'center' }}>
            <Reveal>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: 0 }}>
                무엇을 만들지부터,<br />
                Poco와 함께 정의해보세요.
              </h2>
            </Reveal>
            <Reveal delay={0.15}>
              <div style={{ marginTop: 36, display: 'flex', gap: 12, justifyContent: 'center' }}>
                <PrimaryCTA size="lg" onClick={handleStart} glow>Get started!</PrimaryCTA>
              </div>
            </Reveal>
          </div>
        </div>

        <footer style={{
          width: '100%', padding: '48px 56px 40px',
          borderTop: `1px solid ${tokens.hairline}`, background: '#fff',
          boxSizing: 'border-box', fontFamily: fontStack,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 40 }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <img src="/poco-logo-text.svg" alt="poco" height={28} />
              <div style={{ fontSize: 13, color: tokens.sub, marginTop: 12, lineHeight: 1.6 }}>
                조금씩, 한 걸음씩 — 아이디어를 설계까지 쌓아가는 사고의 캔버스.<br />
                국민대학교 캡스톤 디자인 2026 · Team 59
              </div>
            </div>
            <div style={{ display: 'flex', gap: 56, flexShrink: 0 }}>
              <div>
                <div style={{ fontSize: 11.5, color: tokens.sub, fontWeight: 600, marginBottom: 12, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Project</div>
                {[
                  { l: 'GitHub Repo', h: 'https://github.com/kookmin-sw/2026-capstone-59' },
                  { l: 'Docs', h: 'https://kookmin-sw.github.io/2026-capstone-59/' },
                ].map((it) => (
                  <a key={it.l} href={it.h} target="_blank" rel="noopener noreferrer" style={{ display: 'block', fontSize: 13.5, color: tokens.ink, marginBottom: 8, textDecoration: 'none' }}>
                    {it.l} ↗
                  </a>
                ))}
              </div>
              <div>
                <div style={{ fontSize: 11.5, color: tokens.sub, fontWeight: 600, marginBottom: 12, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Team</div>
                {['정연승', '장우리', '김한림', '박수연'].map((n) => (
                  <div key={n} style={{ fontSize: 13.5, color: tokens.ink, marginBottom: 8 }}>{n}</div>
                ))}
              </div>
            </div>
          </div>
          <div style={{ marginTop: 36, paddingTop: 20, borderTop: `1px solid ${tokens.hairline}`, fontSize: 12, color: tokens.sub, display: 'flex', justifyContent: 'space-between' }}>
            <span>© 2026 Poco · Kookmin University Capstone</span>
            <span style={{ fontFamily: monoStack }}>v0.1</span>
          </div>
        </footer>
      </section>
    </div>
  )
}

const navLinkStyle = {
  fontSize: 14,
  color: tokens.body,
  textDecoration: 'none',
  fontFamily: fontStack,
  fontWeight: 500,
  whiteSpace: 'nowrap',
}
